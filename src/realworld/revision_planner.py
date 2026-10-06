"""Deterministic matrix planner for paper-revision simulation campaigns.

Planning is pure: no graph is loaded and no result file is touched.  Each
condition keeps exogenous configuration identity separate from policy and
arrival replication so paired alternatives share both configuration and seed.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from itertools import product
import math
from types import MappingProxyType
from typing import Any, Literal

from SALib.sample import morris as morris_sampler

from src.realworld.revision_design import (
    EXPECTED_CAMPAIGNS,
    EXPECTED_MORRIS_FACTORS,
    RevisionExperimentDesign,
)
from src.realworld.revision_runner import build_configuration_id


Stage = Literal["smoke", "full"]
_BASELINE_POLICIES = ("bus_only", "static_multimodal")


@dataclass(frozen=True, slots=True)
class PlannedCondition:
    """One immutable policy replication in a revision campaign matrix."""

    campaign_id: str
    configuration_id: str
    policy_id: str
    resource_frame: str
    graph_scope: str
    corridor_path_count: int | None
    arrival_seed: int
    threat_seed: int | None
    threat_draw: int | None
    rail_status: str
    rail_multiplier: float | None
    scenario_id: str
    parameters: Mapping[str, Any]

    def __post_init__(self) -> None:
        for field_name in (
            "campaign_id",
            "configuration_id",
            "policy_id",
            "resource_frame",
            "graph_scope",
            "rail_status",
            "scenario_id",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        if len(self.configuration_id) != 16 or any(
            character not in "0123456789abcdef"
            for character in self.configuration_id
        ):
            raise ValueError("configuration_id must be a 16-character hex digest")
        _optional_positive_int(self.corridor_path_count, "corridor_path_count")
        _positive_int(self.arrival_seed, "arrival_seed")
        _optional_positive_int(self.threat_seed, "threat_seed")
        _optional_positive_int(self.threat_draw, "threat_draw")
        if self.rail_status not in {"available", "degraded", "unavailable"}:
            raise ValueError("unsupported rail_status")
        if self.rail_status == "unavailable":
            if self.rail_multiplier is not None:
                raise ValueError("unavailable rail must have no multiplier")
        else:
            if self.rail_multiplier is None:
                raise ValueError("available or degraded rail requires multiplier")
            multiplier = float(self.rail_multiplier)
            if not math.isfinite(multiplier) or multiplier < 1.0:
                raise ValueError("rail_multiplier must be finite and at least one")
        if not isinstance(self.parameters, Mapping):
            raise TypeError("parameters must be a mapping")
        object.__setattr__(self, "parameters", _deep_freeze(self.parameters))

    @property
    def parameter_mapping(self) -> Mapping[str, Any]:
        """Explicit alias used by tabular campaign executors."""

        return self.parameters


def plan_campaign_conditions(
    design: RevisionExperimentDesign,
    campaign_id: str,
    stage: Stage = "smoke",
) -> tuple[PlannedCondition, ...]:
    """Expand one validated campaign into stable, paired run conditions."""

    if not isinstance(design, RevisionExperimentDesign):
        raise TypeError("design must be a RevisionExperimentDesign")
    if stage not in {"smoke", "full"}:
        raise ValueError("stage must be smoke or full")
    if campaign_id not in EXPECTED_CAMPAIGNS:
        raise KeyError(f"unknown revision campaign {campaign_id!r}")

    planners = {
        "paired_reanalysis": _plan_paired_reanalysis,
        "graph_scope": _plan_graph_scope,
        "break_even": _plan_break_even,
        "break_even_fine": _plan_break_even_fine,
        "demand_fleet": _plan_demand_fleet,
        "road_rail_map": _plan_road_rail_map,
        "random_threat_outer": _plan_random_threat_outer,
        "adaptive_policies": _plan_adaptive_policies,
        "morris": _plan_morris,
        "scale_sensitivity": _plan_scale_sensitivity,
        "path_interdiction_threat": _plan_path_interdiction_threat,
    }
    conditions = tuple(planners[campaign_id](design, stage))
    expected = _expected_count(design, campaign_id, stage)
    if len(conditions) != expected:
        raise RuntimeError(
            f"{campaign_id} {stage} plan count {len(conditions)} != {expected}"
        )
    _assert_unique_conditions(conditions)
    return conditions


def _plan_paired_reanalysis(
    design: RevisionExperimentDesign, stage: Stage
) -> Sequence[PlannedCondition]:
    campaign = design.campaign("paired_reanalysis")
    scenarios = tuple(campaign["scenario_ids"])
    if stage == "smoke":
        scenarios = scenarios[:3]
    seeds = _arrival_seeds(design, stage)
    conditions: list[PlannedCondition] = []
    for frame, scenario_id, policy, seed in product(
        campaign["resource_frames"], scenarios, campaign["policies"], seeds
    ):
        rail_status, rail_multiplier = _scenario_rail_condition(str(scenario_id))
        parameters = _parameters(
            design,
            "paired_reanalysis",
            resource_frame=str(frame),
            scenario_id=str(scenario_id),
            rail_status=rail_status,
            rail_multiplier=rail_multiplier,
        )
        conditions.append(
            _condition(
                design,
                "paired_reanalysis",
                policy_id=str(policy),
                arrival_seed=seed,
                scenario_id=str(scenario_id),
                resource_frame=str(frame),
                rail_status=rail_status,
                rail_multiplier=rail_multiplier,
                parameters=parameters,
            )
        )
    return conditions


def _plan_graph_scope(
    design: RevisionExperimentDesign, stage: Stage
) -> Sequence[PlannedCondition]:
    campaign = design.campaign("graph_scope")
    paired_policies = tuple(design.campaign("paired_reanalysis")["policies"])
    conditions: list[PlannedCondition] = []
    for scope in campaign["graph_scopes"]:
        scope_id = str(scope["id"])
        corridor_count = scope["corridor_path_count"]
        if stage == "smoke":
            seed_count = int(campaign["smoke_arrival_seed_count"])
        elif scope_id == "full":
            seed_count = int(campaign["full_graph_arrival_seed_count"])
        else:
            seed_count = int(campaign["full_arrival_seed_count"])
        for scenario_id, policy, seed in product(
            campaign["scenario_ids"],
            paired_policies,
            design.arrival_seeds[:seed_count],
        ):
            parameters = _parameters(
                design,
                "graph_scope",
                scenario_id=str(scenario_id),
                graph_scope=scope_id,
                corridor_path_count=corridor_count,
                freeze_selected_edges_from=str(
                    campaign["freeze_selected_edges_from"]
                ),
            )
            conditions.append(
                _condition(
                    design,
                    "graph_scope",
                    policy_id=str(policy),
                    arrival_seed=seed,
                    scenario_id=str(scenario_id),
                    graph_scope=scope_id,
                    corridor_path_count=corridor_count,
                    parameters=parameters,
                )
            )
    return conditions


def _plan_break_even(
    design: RevisionExperimentDesign, stage: Stage
) -> Sequence[PlannedCondition]:
    campaign = design.campaign("break_even")
    multipliers = tuple(campaign["road_multipliers"])
    if stage == "smoke":
        multipliers = multipliers[:3]
    conditions: list[PlannedCondition] = []
    for multiplier, frame, policy, seed in product(
        multipliers,
        campaign["resource_frames"],
        campaign["policies"],
        _arrival_seeds(design, stage),
    ):
        parameters = _parameters(
            design,
            "break_even",
            resource_frame=str(frame),
            scenario_id="long_haul_break_even",
            target_segment=str(campaign["target_segment"]),
            road_multiplier=float(multiplier),
        )
        conditions.append(
            _condition(
                design,
                "break_even",
                policy_id=str(policy),
                arrival_seed=seed,
                scenario_id="long_haul_break_even",
                resource_frame=str(frame),
                parameters=parameters,
            )
        )
    return conditions


def _plan_demand_fleet(
    design: RevisionExperimentDesign, stage: Stage
) -> Sequence[PlannedCondition]:
    campaign = design.campaign("demand_fleet")
    demand = tuple(campaign["demand"])
    fleet = tuple(campaign["road_fleet_total"])
    if stage == "smoke":
        demand = demand[:2]
        fleet = fleet[:2]
    conditions: list[PlannedCondition] = []
    for demand_value, fleet_value, frame, policy, seed in product(
        demand,
        fleet,
        campaign["resource_frames"],
        campaign["policies"],
        _arrival_seeds(design, stage),
    ):
        parameters = _parameters(
            design,
            "demand_fleet",
            resource_frame=str(frame),
            scenario_id="no_disruption",
            demand=int(demand_value),
            road_fleet_total=int(fleet_value),
        )
        conditions.append(
            _condition(
                design,
                "demand_fleet",
                policy_id=str(policy),
                arrival_seed=seed,
                scenario_id="no_disruption",
                resource_frame=str(frame),
                parameters=parameters,
            )
        )
    return conditions


def _plan_road_rail_map(
    design: RevisionExperimentDesign, stage: Stage
) -> Sequence[PlannedCondition]:
    campaign = design.campaign("road_rail_map")
    target_segment = str(design.campaign("break_even")["target_segment"])
    road_multipliers = tuple(campaign["road_multipliers"])
    rail_conditions = tuple(campaign["rail_conditions"])
    if stage == "smoke":
        road_multipliers = road_multipliers[:2]
        rail_conditions = rail_conditions[:2]
    conditions: list[PlannedCondition] = []
    for road_multiplier, rail, frame, policy, seed in product(
        road_multipliers,
        rail_conditions,
        campaign["resource_frames"],
        campaign["policies"],
        _arrival_seeds(design, stage),
    ):
        status = str(rail["status"])
        multiplier = _optional_float(rail["multiplier"])
        parameters = _parameters(
            design,
            "road_rail_map",
            resource_frame=str(frame),
            scenario_id="road_rail_decision_map",
            target_segment=target_segment,
            road_multiplier=float(road_multiplier),
            rail_status=status,
            rail_multiplier=multiplier,
        )
        conditions.append(
            _condition(
                design,
                "road_rail_map",
                policy_id=str(policy),
                arrival_seed=seed,
                scenario_id="road_rail_decision_map",
                resource_frame=str(frame),
                rail_status=status,
                rail_multiplier=multiplier,
                parameters=parameters,
            )
        )
    return conditions


def _plan_random_threat_outer(
    design: RevisionExperimentDesign, stage: Stage
) -> Sequence[PlannedCondition]:
    campaign = design.campaign("random_threat_outer")
    draw_count = int(campaign["threat_draw_count"])
    arrival_count = int(campaign["arrival_seed_count"])
    if stage == "smoke":
        draw_count = min(2, draw_count)
        arrival_count = min(2, arrival_count)
    draws = tuple(
        (index + 1, design.threat_seeds[index]) for index in range(draw_count)
    )
    conditions: list[PlannedCondition] = []
    for (draw, threat_seed), policy, arrival_seed in product(
        draws,
        campaign["policies"],
        design.arrival_seeds[:arrival_count],
    ):
        parameters = _parameters(
            design,
            "random_threat_outer",
            scenario_id="random_blockage_outer",
            threat_draw=draw,
            threat_seed=threat_seed,
            blocked_edge_count=int(campaign["blocked_edge_count"]),
        )
        conditions.append(
            _condition(
                design,
                "random_threat_outer",
                policy_id=str(policy),
                arrival_seed=arrival_seed,
                scenario_id="random_blockage_outer",
                threat_seed=threat_seed,
                threat_draw=draw,
                parameters=parameters,
            )
        )
    return conditions


def _plan_adaptive_policies(
    design: RevisionExperimentDesign, stage: Stage
) -> Sequence[PlannedCondition]:
    campaign = design.campaign("adaptive_policies")
    conditions: list[PlannedCondition] = []
    for frame, rail, policy, seed in product(
        campaign["resource_frames"],
        campaign["rail_conditions"],
        campaign["policy_ids"],
        _arrival_seeds(design, stage),
    ):
        status = str(rail["status"])
        multiplier = _optional_float(rail["multiplier"])
        parameters = _parameters(
            design,
            "adaptive_policies",
            resource_frame=str(frame),
            scenario_id="rail_service_response",
            rail_status=status,
            rail_multiplier=multiplier,
        )
        conditions.append(
            _condition(
                design,
                "adaptive_policies",
                policy_id=str(policy),
                arrival_seed=seed,
                scenario_id="rail_service_response",
                resource_frame=str(frame),
                rail_status=status,
                rail_multiplier=multiplier,
                parameters=parameters,
            )
        )
    return conditions


def _plan_morris(
    design: RevisionExperimentDesign, stage: Stage
) -> Sequence[PlannedCondition]:
    campaign = design.campaign("morris")
    target_segment = str(design.campaign("break_even")["target_segment"])
    trajectories = int(campaign["trajectories"])
    arrival_count = int(campaign["arrival_seed_count"])
    if stage == "smoke":
        trajectories = min(2, trajectories)
        arrival_count = min(2, arrival_count)
    factor_points = _morris_factor_points(design, campaign, trajectories)
    conditions: list[PlannedCondition] = []
    for point_index, factor_values in enumerate(factor_points):
        trajectory = point_index // (len(EXPECTED_MORRIS_FACTORS) + 1)
        parameters = _parameters(
            design,
            "morris",
            scenario_id="morris_screening",
            target_segment=target_segment,
            morris_seed=design.morris_seed,
            morris_point=point_index,
            morris_trajectory=trajectory,
            factor_values=factor_values,
        )
        for policy, arrival_seed in product(
            campaign["policies"], design.arrival_seeds[:arrival_count]
        ):
            conditions.append(
                _condition(
                    design,
                    "morris",
                    policy_id=str(policy),
                    arrival_seed=arrival_seed,
                    scenario_id="morris_screening",
                    parameters=parameters,
                )
            )
    return conditions


def _morris_factor_points(
    design: RevisionExperimentDesign,
    campaign: Mapping[str, Any],
    trajectories: int,
) -> tuple[dict[str, float], ...]:
    factors = campaign["factors"]
    names = list(EXPECTED_MORRIS_FACTORS)
    problem = {
        "num_vars": len(names),
        "names": names,
        "bounds": [list(factors[name]) for name in names],
    }
    samples = morris_sampler.sample(
        problem,
        trajectories,
        num_levels=int(campaign["levels"]),
        seed=design.morris_seed,
    )
    return tuple(
        {
            name: float(row[index])
            for index, name in enumerate(names)
        }
        for row in samples
    )


def _condition(
    design: RevisionExperimentDesign,
    campaign_id: str,
    *,
    policy_id: str,
    arrival_seed: int,
    scenario_id: str,
    parameters: Mapping[str, Any],
    resource_frame: str | None = None,
    graph_scope: str | None = None,
    corridor_path_count: int | None | object = ...,
    threat_seed: int | None = None,
    threat_draw: int | None = None,
    rail_status: str | None = None,
    rail_multiplier: float | None | object = ...,
) -> PlannedCondition:
    resolved_scope = graph_scope or str(design.defaults["graph_scope"])
    if corridor_path_count is ...:
        resolved_corridor_count = design.defaults["corridor_path_count"]
    else:
        resolved_corridor_count = corridor_path_count
    resolved_status = rail_status or str(design.defaults["rail_status"])
    if rail_multiplier is ...:
        resolved_rail_multiplier = None if resolved_status == "unavailable" else 1.0
    else:
        resolved_rail_multiplier = rail_multiplier
    return PlannedCondition(
        campaign_id=campaign_id,
        configuration_id=build_configuration_id(parameters),
        policy_id=policy_id,
        resource_frame=resource_frame or str(design.defaults["resource_frame"]),
        graph_scope=resolved_scope,
        corridor_path_count=resolved_corridor_count,
        arrival_seed=arrival_seed,
        threat_seed=threat_seed,
        threat_draw=threat_draw,
        rail_status=resolved_status,
        rail_multiplier=resolved_rail_multiplier,
        scenario_id=scenario_id,
        parameters=parameters,
    )


def _parameters(
    design: RevisionExperimentDesign,
    campaign_id: str,
    **overrides: Any,
) -> dict[str, Any]:
    parameters: dict[str, Any] = {
        "design_id": design.design_id,
        "campaign_id": campaign_id,
        "departure_policy_id": str(design.defaults["departure_policy_id"]),
        "resource_frame": str(design.defaults["resource_frame"]),
        "graph_scope": str(design.defaults["graph_scope"]),
        "corridor_path_count": design.defaults["corridor_path_count"],
        "return_strategy": str(design.defaults["return_strategy"]),
        "rail_status": str(design.defaults["rail_status"]),
        "rail_multiplier": 1.0,
    }
    parameters.update(overrides)
    return parameters


def _arrival_seeds(
    design: RevisionExperimentDesign, stage: Stage
) -> tuple[int, ...]:
    return design.arrival_seeds[:2] if stage == "smoke" else design.arrival_seeds


def _scenario_rail_condition(scenario_id: str) -> tuple[str, float | None]:
    if scenario_id == "goseong_rail_unavailable":
        return "unavailable", None
    return "available", 1.0


def _plan_break_even_fine(
    design: RevisionExperimentDesign, stage: Stage
) -> Sequence[PlannedCondition]:
    campaign = design.campaign("break_even_fine")
    seeds = design.arrival_seeds[:2] if stage == "smoke" else design.arrival_seeds
    multipliers = campaign["road_multipliers"] if stage == "full" else [1.0, 1.742]
    conditions = []
    for multiplier in multipliers:
        for frame in campaign["resource_frames"]:
            for policy in campaign["policies"]:
                for seed in seeds:
                    params = _parameters(
                        design,
                        "break_even_fine",
                        scenario_id="long_haul_break_even_fine",
                        target_segment=str(campaign["target_segment"]),
                        road_multiplier=float(multiplier),
                        demand=int(campaign.get("demand_pax", 6000)),
                        resource_frame=str(frame),
                    )
                    conditions.append(
                        _condition(
                            design,
                            "break_even_fine",
                            policy_id=str(policy),
                            arrival_seed=seed,
                            scenario_id="long_haul_break_even_fine",
                            resource_frame=str(frame),
                            parameters=params,
                        )
                    )
    return conditions


def _plan_scale_sensitivity(
    design: RevisionExperimentDesign, stage: Stage
) -> Sequence[PlannedCondition]:
    campaign = design.campaign("scale_sensitivity")
    seeds = design.arrival_seeds[:2] if stage == "smoke" else design.arrival_seeds
    demands = campaign["demand_levels"] if stage == "full" else [2000, 6000]
    multipliers = campaign["road_multipliers"] if stage == "full" else [1.0, 2.0]
    conditions = []
    for demand_value in demands:
        for multiplier in multipliers:
            for seed in seeds:
                params1 = _parameters(
                    design,
                    "scale_sensitivity",
                    scenario_id="no_disruption",
                    demand=int(demand_value),
                    road_multiplier=float(multiplier),
                    resource_frame=str(campaign["resource_frames"][0]),
                )
                conditions.append(
                    _condition(
                        design,
                        "scale_sensitivity",
                        policy_id="bus_only",
                        arrival_seed=seed,
                        scenario_id="no_disruption",
                        resource_frame=str(campaign["resource_frames"][0]),
                        parameters=params1,
                    )
                )
                params2 = _parameters(
                    design,
                    "scale_sensitivity",
                    scenario_id="no_disruption",
                    demand=int(demand_value),
                    road_multiplier=float(multiplier),
                    resource_frame=str(campaign["resource_frames"][0]),
                )
                conditions.append(
                    _condition(
                        design,
                        "scale_sensitivity",
                        policy_id="static_multimodal",
                        arrival_seed=seed,
                        scenario_id="no_disruption",
                        resource_frame=str(campaign["resource_frames"][0]),
                        parameters=params2,
                    )
                )
    return conditions


def _plan_path_interdiction_threat(
    design: RevisionExperimentDesign, stage: Stage
) -> Sequence[PlannedCondition]:
    campaign = design.campaign("path_interdiction_threat")
    seeds = design.arrival_seeds[:2] if stage == "smoke" else design.arrival_seeds
    ks = campaign["interdiction_k"] if stage == "full" else [3]
    conditions = []
    multipliers = campaign["road_multipliers"] if stage == "full" else [1.0, 2.0]
    for k in ks:
        for multiplier in multipliers:
            for frame in campaign["resource_frames"]:
                for policy in campaign["policies"]:
                    for seed in seeds:
                        params = _parameters(
                            design,
                            "path_interdiction_threat",
                            scenario_id="goseong_path_interdiction",
                            interdiction_k=k,
                            road_multiplier=float(multiplier),
                            resource_frame=str(frame),
                        )
                        conditions.append(
                            _condition(
                                design,
                                "path_interdiction_threat",
                                policy_id=str(policy),
                                arrival_seed=seed,
                                scenario_id="goseong_path_interdiction",
                                resource_frame=str(frame),
                                parameters=params,
                            )
                        )
    return conditions


def _expected_count(
    design: RevisionExperimentDesign,
    campaign_id: str,
    stage: Stage,
) -> int:
    campaign = design.campaign(campaign_id)
    default_seed_count = 2 if stage == "smoke" else len(design.arrival_seeds)
    if campaign_id == "paired_reanalysis":
        scenarios = 3 if stage == "smoke" else len(campaign["scenario_ids"])
        return (
            len(campaign["policies"])
            * len(campaign["resource_frames"])
            * scenarios
            * default_seed_count
        )
    if campaign_id == "graph_scope":
        if stage == "smoke":
            seed_total = (
                len(campaign["graph_scopes"])
                * int(campaign["smoke_arrival_seed_count"])
            )
        else:
            seed_total = (
                (len(campaign["graph_scopes"]) - 1)
                * int(campaign["full_arrival_seed_count"])
                + int(campaign["full_graph_arrival_seed_count"])
            )
        return (
            len(campaign["scenario_ids"])
            * len(design.campaign("paired_reanalysis")["policies"])
            * seed_total
        )
    if campaign_id == "break_even":
        multipliers = 3 if stage == "smoke" else len(campaign["road_multipliers"])
        return (
            multipliers
            * len(campaign["resource_frames"])
            * len(campaign["policies"])
            * default_seed_count
        )
    if campaign_id == "demand_fleet":
        demand = 2 if stage == "smoke" else len(campaign["demand"])
        fleet = 2 if stage == "smoke" else len(campaign["road_fleet_total"])
        return (
            demand
            * fleet
            * len(campaign["resource_frames"])
            * len(campaign["policies"])
            * default_seed_count
        )
    if campaign_id == "road_rail_map":
        roads = 2 if stage == "smoke" else len(campaign["road_multipliers"])
        rails = 2 if stage == "smoke" else len(campaign["rail_conditions"])
        return (
            roads
            * rails
            * len(campaign["resource_frames"])
            * len(campaign["policies"])
            * default_seed_count
        )
    if campaign_id == "random_threat_outer":
        draws = min(2, int(campaign["threat_draw_count"])) if stage == "smoke" else int(campaign["threat_draw_count"])
        seeds = min(2, int(campaign["arrival_seed_count"])) if stage == "smoke" else int(campaign["arrival_seed_count"])
        return draws * seeds * len(campaign["policies"])
    if campaign_id == "adaptive_policies":
        return (
            len(campaign["policy_ids"])
            * len(campaign["resource_frames"])
            * len(campaign["rail_conditions"])
            * default_seed_count
        )
    if campaign_id == "break_even_fine":
        multipliers = 2 if stage == "smoke" else len(campaign["road_multipliers"])
        return (
            multipliers
            * len(campaign["resource_frames"])
            * len(campaign["policies"])
            * default_seed_count
        )
    if campaign_id == "scale_sensitivity":
        levels = 2 if stage == "smoke" else len(campaign["demand_levels"])
        multipliers = 2 if stage == "smoke" else len(campaign["road_multipliers"])
        return (
            levels
            * multipliers
            * default_seed_count
            * 2
        )
    if campaign_id == "path_interdiction_threat":
        ks = 1 if stage == "smoke" else len(campaign["interdiction_k"])
        multipliers = 2 if stage == "smoke" else len(campaign["road_multipliers"])
        return (
            ks
            * multipliers
            * len(campaign["resource_frames"])
            * len(campaign["policies"])
            * default_seed_count
        )
    trajectories = min(2, int(campaign["trajectories"])) if stage == "smoke" else int(campaign["trajectories"])
    seeds = min(2, int(campaign["arrival_seed_count"])) if stage == "smoke" else int(campaign["arrival_seed_count"])
    return (
        trajectories
        * (len(campaign["factors"]) + 1)
        * len(campaign["policies"])
        * seeds
    )


def _assert_unique_conditions(conditions: Sequence[PlannedCondition]) -> None:
    identities = {
        (
            item.configuration_id,
            item.policy_id,
            item.arrival_seed,
            item.threat_seed,
            item.threat_draw,
        )
        for item in conditions
    }
    if len(identities) != len(conditions):
        raise RuntimeError("campaign planner produced duplicate conditions")


def _positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _optional_positive_int(value: Any, name: str) -> int | None:
    if value is None:
        return None
    return _positive_int(value, name)


def _optional_float(value: Any) -> float | None:
    return None if value is None else float(value)


def _deep_freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {str(key): _deep_freeze(item) for key, item in value.items()}
        )
    if isinstance(value, list | tuple):
        return tuple(_deep_freeze(item) for item in value)
    return value


__all__ = ["PlannedCondition", "Stage", "plan_campaign_conditions"]
