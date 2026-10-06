"""Execute one planned paper-revision condition without mutating source inputs."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Mapping, Sequence

import networkx as nx

from src.policies import GracePolicy, StrictPolicy
from src.scenario import run_scenario
from src.realworld.revision_campaign import RunSpec
from src.realworld.revision_planner import PlannedCondition
from src.realworld.revision_runner import (
    apply_forced_failure_config,
    apply_revision_config,
    selected_edges_checksum,
)


Edge = tuple[str, str]


@dataclass(frozen=True, slots=True)
class PreparedDisruption:
    """Sparse deterministic road disruption attached to one condition."""

    edges: tuple[Edge, ...]
    mode: str
    capacity_factor: float
    travel_time_multiplier: float

    def __post_init__(self) -> None:
        if self.mode not in {"none", "blocked", "capacity_reduction"}:
            raise ValueError("unsupported disruption mode")
        normalized = tuple(sorted({(str(u), str(v)) for u, v in self.edges}))
        if self.mode == "none" and normalized:
            raise ValueError("none disruption must not select edges")
        if self.mode != "none" and not normalized:
            raise ValueError("road disruption must select at least one edge")
        capacity = float(self.capacity_factor)
        multiplier = float(self.travel_time_multiplier)
        if not math.isfinite(capacity) or not 0.0 <= capacity <= 1.0:
            raise ValueError("capacity_factor must be finite in [0, 1]")
        if not math.isfinite(multiplier) or multiplier <= 0.0:
            raise ValueError("travel_time_multiplier must be finite and positive")
        object.__setattr__(self, "edges", normalized)
        object.__setattr__(self, "capacity_factor", capacity)
        object.__setattr__(self, "travel_time_multiplier", multiplier)

    @classmethod
    def none(cls) -> "PreparedDisruption":
        return cls((), "none", 1.0, 1.0)


def execute_condition(
    graph: nx.DiGraph,
    base_config: Mapping[str, Any],
    condition: PlannedCondition,
    *,
    disruption: PreparedDisruption,
) -> dict[str, Any]:
    """Run one condition and return JSON-safe metrics plus full provenance."""

    if not isinstance(condition, PlannedCondition):
        raise TypeError("condition must be a PlannedCondition")
    if not isinstance(disruption, PreparedDisruption):
        raise TypeError("disruption must be a PreparedDisruption")

    parameters = _thaw(condition.parameters)
    demand = _rounded_positive_int(
        _factor_value(parameters, "demand", base_config["personnel"]["total"]),
        "demand",
    )
    road_fleet_total_raw = _factor_value(parameters, "road_fleet_total", None)
    road_fleet_total = (
        None
        if road_fleet_total_raw is None
        else _rounded_positive_int(road_fleet_total_raw, "road_fleet_total")
    )
    return_strategy = str(parameters.get("return_strategy", "reverse_network"))
    effective_rail_status, effective_rail_multiplier = effective_rail_condition(
        condition
    )

    config_policy, executed_mode = _execution_branch(
        condition.policy_id,
        effective_rail_status,
    )
    config = apply_revision_config(
        base_config,
        policy_id=config_policy,
        resource_frame=condition.resource_frame,
        demand=demand,
        road_fleet_total=road_fleet_total,
        return_strategy=return_strategy,
        rail_status=effective_rail_status,
        rail_multiplier=effective_rail_multiplier,
    )
    _apply_factor_config(config, parameters)

    effective_disruption = _with_parameter_multiplier(disruption, parameters)
    config = apply_forced_failure_config(
        config,
        edges=effective_disruption.edges,
        mode=effective_disruption.mode,
        capacity_factor=effective_disruption.capacity_factor,
        travel_time_multiplier=effective_disruption.travel_time_multiplier,
    )
    resource_allocation = _configured_resource_allocation(config, executed_mode)

    departure_policy_id = str(parameters.get("departure_policy_id", "strict"))
    departure_policy = _departure_policy(departure_policy_id, parameters)
    sigma = float(
        _factor_value(
            parameters,
            "arrival_sigma",
            config.get("lateness", {}).get("sigma_levels", [0.75])[0],
        )
    )
    metrics = run_scenario(
        G=graph,
        config=config,
        scenario_type=executed_mode,
        policy=departure_policy,
        params={"s": 1.0, "p_fail_scale": 0.0, "sigma": sigma},
        seed=condition.arrival_seed,
    )

    checksum = selected_edges_checksum(effective_disruption.edges)
    run_spec = RunSpec(
        campaign_id=condition.campaign_id,
        configuration_id=condition.configuration_id,
        policy_id=condition.policy_id,
        departure_policy_id=departure_policy_id,
        resource_frame=condition.resource_frame,
        graph_scope=condition.graph_scope,
        corridor_path_count=condition.corridor_path_count,
        arrival_seed=condition.arrival_seed,
        threat_seed=condition.threat_seed,
        threat_draw=condition.threat_draw,
        selected_edges_checksum=checksum,
        rail_status=effective_rail_status,
        return_strategy=return_strategy,
    )
    row: dict[str, Any] = dict(parameters)
    row.update(run_spec.to_mapping())
    row.update(
        {
            "run_key": run_spec.run_key,
            "scenario_id": condition.scenario_id,
            "executed_mode": executed_mode,
            "rail_multiplier": effective_rail_multiplier,
            "selected_edge_count": len(effective_disruption.edges),
            "disruption_mode": effective_disruption.mode,
            "disruption_capacity_factor": effective_disruption.capacity_factor,
            "road_travel_time_multiplier": (
                effective_disruption.travel_time_multiplier
            ),
            "analysis_graph_nodes": graph.number_of_nodes(),
            "analysis_graph_edges": graph.number_of_edges(),
            **resource_allocation,
        }
    )
    row.update(_json_safe(metrics))
    return row


def effective_rail_condition(
    condition: PlannedCondition,
) -> tuple[str, float | None]:
    """Resolve planned and Morris-factor rail inputs to executed service state."""

    if not isinstance(condition, PlannedCondition):
        raise TypeError("condition must be a PlannedCondition")
    if condition.rail_status == "unavailable":
        return "unavailable", None
    multiplier = float(
        _factor_value(
            condition.parameters,
            "rail_travel_multiplier",
            condition.rail_multiplier,
        )
    )
    if not math.isfinite(multiplier) or multiplier < 1.0:
        raise ValueError("rail_travel_multiplier must be finite and at least 1.0")
    status = "degraded" if multiplier > 1.0 else condition.rail_status
    return status, multiplier


def _execution_branch(policy_id: str, rail_status: str) -> tuple[str, str]:
    if policy_id == "bus_only":
        return "bus_only", "bus_only"
    if policy_id == "static_multimodal":
        return "static_multimodal", "multimodal"
    if policy_id == "precheck_switch":
        if rail_status == "unavailable":
            return "bus_only", "bus_only"
        return "static_multimodal", "multimodal"
    if policy_id == "split_600_400":
        return policy_id, "adaptive_split"
    if policy_id.startswith("station_fallback_"):
        return policy_id, "adaptive_fallback"
    raise ValueError(f"unsupported revision policy: {policy_id!r}")


def _apply_factor_config(config: dict[str, Any], parameters: Mapping[str, Any]) -> None:
    factors = parameters.get("factor_values", {})
    if not isinstance(factors, Mapping):
        factors = {}
    transfer = factors.get("transfer_time_min")
    if transfer is not None:
        config.setdefault("multimodal", {})["transfer_time_min"] = float(transfer)
    if "arrival_sigma" in factors:
        config.setdefault("lateness", {})["sigma_levels"] = [
            float(factors["arrival_sigma"])
        ]


def _factor_value(
    parameters: Mapping[str, Any],
    name: str,
    default: Any,
) -> Any:
    factors = parameters.get("factor_values", {})
    if isinstance(factors, Mapping) and name in factors:
        return factors[name]
    return parameters.get(name, default)


def _with_parameter_multiplier(
    disruption: PreparedDisruption,
    parameters: Mapping[str, Any],
) -> PreparedDisruption:
    multiplier = _factor_value(
        parameters,
        "road_longhaul_multiplier",
        parameters.get("road_multiplier", disruption.travel_time_multiplier),
    )
    if disruption.mode == "none":
        return disruption
    return PreparedDisruption(
        disruption.edges,
        disruption.mode,
        disruption.capacity_factor,
        float(multiplier),
    )


def _departure_policy(policy_id: str, parameters: Mapping[str, Any]):
    if policy_id == "strict":
        return StrictPolicy()
    if policy_id == "grace":
        return GracePolicy(
            W=float(parameters.get("grace_wait_min", 0.0)),
            theta=float(parameters.get("grace_threshold", 1.0)),
        )
    raise ValueError(f"unsupported departure_policy_id: {policy_id!r}")


def _configured_resource_allocation(
    config: Mapping[str, Any],
    executed_mode: str,
) -> dict[str, int]:
    """Report role counts actually configured for executed policy branch."""

    road_branch = executed_mode in {"bus_only", "adaptive_split"}
    multimodal_branch = executed_mode in {
        "multimodal",
        "adaptive_split",
        "adaptive_fallback",
    }
    fallback_branch = executed_mode == "adaptive_fallback"
    bus = config.get("bus", {})
    multimodal = config.get("multimodal", {})
    adaptation = config.get("adaptation", {})

    direct = _nonnegative_configured_int(
        bus.get("fleet_size", 0) if road_branch else 0,
        "bus.fleet_size",
    )
    feeder = _nonnegative_configured_int(
        multimodal.get("shuttle_fleet_size", 0) if multimodal_branch else 0,
        "multimodal.shuttle_fleet_size",
    )
    last_mile = _nonnegative_configured_int(
        multimodal.get("lastmile_fleet_size", 0) if multimodal_branch else 0,
        "multimodal.lastmile_fleet_size",
    )
    fallback = _nonnegative_configured_int(
        adaptation.get("fallback_fleet_size", 0) if fallback_branch else 0,
        "adaptation.fallback_fleet_size",
    )

    train_capacity = 0
    if multimodal_branch:
        rail_links = config.get("network", {}).get("rail_link") or []
        if not rail_links or len(rail_links[0]) < 5:
            raise ValueError("multimodal branch requires rail_link capacity")
        train_capacity = _nonnegative_configured_int(
            rail_links[0][4],
            "network.rail_link[0].capacity",
        )

    return {
        "direct_bus_count": direct,
        "feeder_shuttle_count": feeder,
        "last_mile_bus_count": last_mile,
        "fallback_bus_count": fallback,
        "total_road_vehicle_count": direct + feeder + last_mile + fallback,
        "train_capacity": train_capacity,
    }


def _nonnegative_configured_int(value: Any, name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a non-negative integer")
    numeric = float(value)
    if not math.isfinite(numeric) or numeric < 0.0 or not numeric.is_integer():
        raise ValueError(f"{name} must be a non-negative integer")
    return int(numeric)


def _rounded_positive_int(value: Any, name: str) -> int:
    numeric = float(value)
    if not math.isfinite(numeric) or numeric <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return max(1, int(round(numeric)))


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


__all__ = [
    "PreparedDisruption",
    "effective_rail_condition",
    "execute_condition",
]
