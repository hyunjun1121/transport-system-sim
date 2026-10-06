"""Scenario execution for bus-only and rail-bus multimodal transport.

The scenario runner keeps the public ``run_scenario`` API stable while using
queue-based departure policy, fleet availability, fixed-headway rail dispatch,
structured disruptions, and dynamic road BPR traversal.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass

import networkx as nx
import numpy as np

from src.dispatch import plan_dispatches
from src.disruptions import sample_edge_disruptions
from src.fleet import FleetAvailability
from src.metrics import MetricsCollector
from src.models import (
    bpr_travel_time,
    sample_arrival_delays,
    sample_link_failures,  # kept as module attribute for existing tests/patches
)
from src.policies import DeparturePolicy, StrictPolicy
from src.rail import next_departure_time, resolve_rail_service
from src.sim_types import (
    EdgeDisruption,
    Passenger,
    StationBatch,
    VehicleTrip,
    require_int_at_least,
    require_non_negative,
)
from src.traffic import DynamicRoadTraffic
from src.transfers import compute_transfer_delay

# Non-rail fixed-headway service modes the composable pipeline accepts. This
# mirrors src.realworld.types.ALLOWED_SERVICE_MODES minus 'rail'; kept local so
# the core simulator does not depend on the realworld package. Rail is the
# default multimodal service_mode and resolves from network.rail_link, so it is
# intentionally excluded here — an unsupported service_mode must fail loudly
# rather than silently run as a misleading service_breakdown entry.
_NON_RAIL_SERVICE_MODES = frozenset({"sea", "air"})


RouteTraveler = Callable[[float], tuple[float, tuple[str, ...]]]
Edge = tuple[str, str]

DEFAULT_DISPATCH_INTERVAL_MIN = 5.0
DEFAULT_TURNAROUND_MIN = 5.0
_RETURN_STRATEGIES = frozenset({"legacy_none", "reverse_network"})
_ADAPTIVE_SPLIT_POLICY_IDS = frozenset({"split_600_400", "split_60_40"})
_STATION_FALLBACK_HOLDS_MIN = {
    "station_fallback_30": 30.0,
    "station_fallback_60": 60.0,
    "station_fallback_90": 90.0,
}
_STOCHASTIC_ROLES = (
    "direct_bus",
    "feeder_shuttle",
    "last_mile",
    "fallback_bus",
)
_ROLE_STREAM_IDS = {
    role: index for index, role in enumerate(_STOCHASTIC_ROLES)
}


def _named_role_rngs(
    seed: int,
    *,
    family_offset: int,
    active: bool,
) -> dict[str, np.random.Generator | None]:
    """Build deterministic, independent role streams for one replication.

    SeedSequence composition keeps each role aligned across static and adaptive
    policies under common-random-number pairing without arithmetic seed-range
    collisions. A role's stream never depends on how many values another role
    consumes.
    """

    if not active:
        return {role: None for role in _STOCHASTIC_ROLES}
    return {
        role: np.random.default_rng(
            np.random.SeedSequence([int(seed), int(family_offset), role_id])
        )
        for role, role_id in _ROLE_STREAM_IDS.items()
    }


def run_scenario(
    G: nx.DiGraph,
    config: dict,
    scenario_type: str,
    policy: DeparturePolicy,
    params: dict,
    seed: int,
) -> dict:
    """Run a single scenario and return KPI metrics."""
    n_personnel = config["personnel"]["total"]
    assembly_time = config["personnel"]["assembly_time"]
    time_limit = config["experiment"]["time_limit"]
    return_strategy = _resolve_return_strategy(config)
    adaptive_policy_id = _resolve_adaptive_policy_id(config, scenario_type)

    rng_arrival = np.random.default_rng(seed)
    rng_failure = np.random.default_rng(seed + 10_000)
    stochastic_conf = config.get("stochastic", {})
    road_noise_sigma = float(stochastic_conf.get("road_noise_sigma", 0.0))
    turnaround_noise_lambda = float(stochastic_conf.get("turnaround_noise_lambda", 0.0))
    road_rngs = _named_role_rngs(
        seed,
        family_offset=20_000,
        active=road_noise_sigma > 0.0,
    )
    turnaround_rngs = _named_role_rngs(
        seed,
        family_offset=30_000,
        active=turnaround_noise_lambda > 0.0,
    )

    delays = sample_arrival_delays(
        n_personnel,
        mu=config["lateness"]["mu"],
        sigma=params["sigma"],
        rng=rng_arrival,
    )
    # Optional underestimation-correction multiplier (진학은 et al. 2022 report
    # ~40% underestimation -> 1.67x). Defaults to 1.0 (raw anchor); applied as
    # a documented opt-in stress knob, not by default (source composition
    # unverified). CRN-preserving: same seed -> same raw sample -> scaled.
    correction_factor = float(config.get("lateness", {}).get("correction_factor", 1.0))
    delays = delays * correction_factor
    passengers = _make_passengers(assembly_time + delays)

    disruptions = _sample_disruptions(G, config, params, rng_failure)

    metrics = MetricsCollector(
        total_personnel=n_personnel,
        time_limit=time_limit,
        late_penalty_min=config.get("metrics", {}).get("late_penalty_min"),
        success_deadline_min=config.get("experiment", {}).get("success_deadline_min"),
    )
    traffic = DynamicRoadTraffic.from_config(
        G,
        config,
        params=params,
        disruptions=disruptions,
        road_noise_sigma=road_noise_sigma,
        rng_road=None,
    )

    if scenario_type == "bus_only":
        _run_bus_only(
            G, config, passengers, policy, traffic, metrics,
            turnaround_noise_lambda=turnaround_noise_lambda,
            rng_road=road_rngs["direct_bus"],
            rng_turnaround=turnaround_rngs["direct_bus"],
            return_strategy=return_strategy,
        )
    elif scenario_type == "multimodal":
        _run_multimodal(
            G, config, passengers, policy, traffic, metrics,
            turnaround_noise_lambda=turnaround_noise_lambda,
            rng_road_shuttle=road_rngs["feeder_shuttle"],
            rng_road_lastmile=road_rngs["last_mile"],
            rng_turnaround_shuttle=turnaround_rngs["feeder_shuttle"],
            rng_turnaround_lastmile=turnaround_rngs["last_mile"],
            return_strategy=return_strategy,
        )
    elif scenario_type == "adaptive_split":
        _run_adaptive_split(
            G,
            config,
            passengers,
            policy,
            traffic,
            metrics,
            policy_id=adaptive_policy_id,
            turnaround_noise_lambda=turnaround_noise_lambda,
            road_rngs=road_rngs,
            turnaround_rngs=turnaround_rngs,
            return_strategy=return_strategy,
        )
    elif scenario_type == "adaptive_fallback":
        _run_adaptive_fallback(
            G,
            config,
            passengers,
            policy,
            traffic,
            metrics,
            policy_id=adaptive_policy_id,
            turnaround_noise_lambda=turnaround_noise_lambda,
            road_rngs=road_rngs,
            turnaround_rngs=turnaround_rngs,
            return_strategy=return_strategy,
        )
    else:
        raise ValueError(f"unknown scenario_type: {scenario_type}")

    metrics.leftover_count = n_personnel - metrics.success_count
    include_extended = bool(config.get("metrics", {}).get("include_extended", False))
    return metrics.as_dict(include_extended=include_extended)


def _run_bus_only(
    G: nx.DiGraph,
    config: dict,
    passengers: tuple[Passenger, ...],
    policy: DeparturePolicy,
    traffic: DynamicRoadTraffic,
    metrics: MetricsCollector,
    *,
    turnaround_noise_lambda: float = 0.0,
    rng_road: np.random.Generator | None = None,
    rng_turnaround: np.random.Generator | None = None,
    return_strategy: str = "legacy_none",
) -> None:
    """Run queue-based bus-only transport from A to D."""
    bus_conf = config.get("bus", {})
    group_size = config["personnel"]["group_size"]
    assembly_time = config["personnel"]["assembly_time"]
    rerouting_conf = config.get("failure", {}).get("rerouting", {})
    traffic.set_road_noise_rng(rng_road)
    traveler = _make_route_traveler(
        G, traffic, "A", "D",
        allowed_modes={"road"},
        rerouting_config=rerouting_conf,
        metrics=metrics,
    )
    return_traveler = None
    if return_strategy == "reverse_network":
        return_traveler = _make_route_traveler(
            G, traffic, "D", "A",
            allowed_modes={"road"},
            rerouting_config=rerouting_conf,
        )

    planned = _plan_origin_dispatches(
        passengers=passengers,
        policy=policy,
        vehicle_capacity=group_size,
        dispatch_interval=bus_conf.get(
            "dispatch_interval_min",
            DEFAULT_DISPATCH_INTERVAL_MIN,
        ),
        first_depart_time=_optional_config_time(
            bus_conf,
            "first_departure_min",
            assembly_time,
        ),
        mode="bus",
        route=("A", "D"),
    )

    _execute_vehicle_trips(
        planned,
        traveler=traveler,
        fleet_size=bus_conf.get("fleet_size", 1),
        vehicle_capacity=group_size,
        turnaround_time=bus_conf.get("turnaround_min", DEFAULT_TURNAROUND_MIN),
        metrics=metrics,
        record_arrivals_at_destination=True,
        resource_mode="bus",
        passenger_ready_times={
            passenger.id: passenger.arrival_time for passenger in passengers
        },
        wait_stage="assembly",
        turnaround_noise_lambda=turnaround_noise_lambda,
        rng_turnaround=rng_turnaround,
        return_traveler=return_traveler,
    )


def _run_service_alternative(
    G: nx.DiGraph,
    config: dict,
    passengers: tuple[Passenger, ...],
    policy: DeparturePolicy,
    traffic: DynamicRoadTraffic,
    metrics: MetricsCollector,
    *,
    spec: ServiceSpec,
    turnaround_noise_lambda: float = 0.0,
    rng_road_shuttle: np.random.Generator | None = None,
    rng_road_lastmile: np.random.Generator | None = None,
    rng_turnaround_shuttle: np.random.Generator | None = None,
    rng_turnaround_lastmile: np.random.Generator | None = None,
    return_strategy: str = "legacy_none",
) -> None:
    """Run the composable service alternative.

    Pipeline: ``A -> shuttle(road) -> spec.access_id -> transfer ->
    fixed-headway service leg -> spec.egress_id -> last-mile(road) -> D``. Mode
    is carried by ``spec`` (rail / sea / air). Node IDs are spec-driven; A and
    D stay canonical (assembly is always origin, destination always sink).
    """
    if not passengers:
        return

    multimodal_conf = config.get("multimodal", {})
    group_size = config["personnel"]["group_size"]
    assembly_time = config["personnel"]["assembly_time"]
    rerouting_conf = config.get("failure", {}).get("rerouting", {})

    traffic.set_road_noise_rng(rng_road_shuttle)
    shuttle_traveler = _make_route_traveler(
        G, traffic, "A", spec.access_id,
        allowed_modes={"road"},
        rerouting_config=rerouting_conf,
        metrics=metrics,
    )
    shuttle_return_traveler = None
    if return_strategy == "reverse_network":
        shuttle_return_traveler = _make_route_traveler(
            G, traffic, spec.access_id, "A",
            allowed_modes={"road"},
            rerouting_config=rerouting_conf,
        )
    shuttle_plan = _plan_origin_dispatches(
        passengers=passengers,
        policy=policy,
        vehicle_capacity=group_size,
        dispatch_interval=multimodal_conf.get(
            "shuttle_dispatch_interval_min",
            DEFAULT_DISPATCH_INTERVAL_MIN,
        ),
        first_depart_time=_optional_config_time(
            multimodal_conf,
            "shuttle_first_departure_min",
            assembly_time,
        ),
        mode="shuttle",
        route=("A", spec.access_id),
    )
    station_batches = _execute_vehicle_trips(
        shuttle_plan,
        traveler=shuttle_traveler,
        fleet_size=multimodal_conf.get("shuttle_fleet_size", 1),
        vehicle_capacity=group_size,
        turnaround_time=multimodal_conf.get(
            "shuttle_turnaround_min",
            DEFAULT_TURNAROUND_MIN,
        ),
        metrics=metrics,
        record_arrivals_at_destination=False,
        resource_mode="bus",
        passenger_ready_times={
            passenger.id: passenger.arrival_time for passenger in passengers
        },
        wait_stage="assembly",
        turnaround_noise_lambda=turnaround_noise_lambda,
        rng_turnaround=rng_turnaround_shuttle,
        return_traveler=shuttle_return_traveler,
    )

    transfer_batches = _apply_transfer_batches(
        station_batches,
        base_min=multimodal_conf.get("transfer_time_min", 0.0),
        per_passenger_min=multimodal_conf.get("transfer_per_passenger_min", 0.0),
        metrics=metrics,
    )
    service_arrivals = _run_fixed_headway_service(
        config, transfer_batches, metrics, spec=spec
    )

    traffic.set_road_noise_rng(rng_road_lastmile)
    lastmile_traveler = _make_route_traveler(
        G, traffic, spec.egress_id, "D",
        allowed_modes={"road"},
        rerouting_config=rerouting_conf,
        metrics=metrics,
    )
    lastmile_return_traveler = None
    if return_strategy == "reverse_network":
        lastmile_return_traveler = _make_route_traveler(
            G, traffic, "D", spec.egress_id,
            allowed_modes={"road"},
            rerouting_config=rerouting_conf,
        )
    _execute_lastmile_batches(
        service_arrivals,
        traveler=lastmile_traveler,
        dispatch_interval=multimodal_conf.get("lastmile_dispatch_interval_min", 0.0),
        vehicle_capacity=multimodal_conf.get("lastmile_vehicle_capacity", group_size),
        fleet_size=multimodal_conf.get(
            "lastmile_fleet_size",
            multimodal_conf.get("shuttle_fleet_size", 1),
        ),
        turnaround_time=multimodal_conf.get(
            "lastmile_turnaround_min",
            DEFAULT_TURNAROUND_MIN,
        ),
        first_depart_time=_optional_config_time(
            multimodal_conf,
            "lastmile_first_departure_min",
            0.0,
        ),
        metrics=metrics,
        egress_id=spec.egress_id,
        turnaround_noise_lambda=turnaround_noise_lambda,
        rng_turnaround=rng_turnaround_lastmile,
        return_traveler=lastmile_return_traveler,
    )


def _resolve_service_spec(config: dict) -> ServiceSpec:
    """Resolve the service spec for the multimodal alternative.

    Default ``service_mode='rail'`` builds the spec from the legacy
    ``rail_link[0]`` (byte-identical to the pre-widening runner). A non-rail
    ``service_mode`` (sea / air) builds the spec from
    ``config['multimodal']['service']`` — the bridge to Phase 3 sea/air
    execution; rail configs never carry that key, so they are unchanged.
    """

    multimodal_conf = config.get("multimodal", {})
    mode = multimodal_conf.get("service_mode", "rail")
    if mode == "rail":
        return _service_spec_from_legacy_rail(config)
    if mode not in _NON_RAIL_SERVICE_MODES:
        raise ValueError(
            f"multimodal.service_mode={mode!r} is not a supported service mode; "
            f"non-rail modes must be one of {sorted(_NON_RAIL_SERVICE_MODES)} "
            "(rail is the default and resolves from network.rail_link)"
        )
    service = multimodal_conf.get("service")
    if not isinstance(service, dict):
        raise ValueError(
            f"multimodal.service_mode={mode!r} requires a multimodal.service "
            "mapping (access_id, egress_id, travel_time_min, headway_min, "
            "capacity)"
        )
    return ServiceSpec(
        mode=str(mode),
        access_id=str(service["access_id"]),
        egress_id=str(service["egress_id"]),
        travel_time_min=float(service["travel_time_min"]),
        headway_min=float(service["headway_min"]),
        capacity=int(service["capacity"]),
        first_departure_min=service.get("first_departure_min"),
    )


def _run_multimodal(
    G: nx.DiGraph,
    config: dict,
    passengers: tuple[Passenger, ...],
    policy: DeparturePolicy,
    traffic: DynamicRoadTraffic,
    metrics: MetricsCollector,
    *,
    turnaround_noise_lambda: float = 0.0,
    rng_road_shuttle: np.random.Generator | None = None,
    rng_road_lastmile: np.random.Generator | None = None,
    rng_turnaround_shuttle: np.random.Generator | None = None,
    rng_turnaround_lastmile: np.random.Generator | None = None,
    return_strategy: str = "legacy_none",
) -> None:
    """Run the multimodal alternative (service spec resolved from config)."""

    _run_service_alternative(
        G,
        config,
        passengers,
        policy,
        traffic,
        metrics,
        spec=_resolve_service_spec(config),
        turnaround_noise_lambda=turnaround_noise_lambda,
        rng_road_shuttle=rng_road_shuttle,
        rng_road_lastmile=rng_road_lastmile,
        rng_turnaround_shuttle=rng_turnaround_shuttle,
        rng_turnaround_lastmile=rng_turnaround_lastmile,
        return_strategy=return_strategy,
    )


def _run_adaptive_split(
    G: nx.DiGraph,
    config: dict,
    passengers: tuple[Passenger, ...],
    policy: DeparturePolicy,
    traffic: DynamicRoadTraffic,
    metrics: MetricsCollector,
    *,
    policy_id: str | None,
    turnaround_noise_lambda: float = 0.0,
    road_rngs: dict[str, np.random.Generator | None] | None = None,
    turnaround_rngs: dict[str, np.random.Generator | None] | None = None,
    return_strategy: str = "legacy_none",
) -> None:
    """Run a deterministic 60% service / 40% direct-bus allocation.

    Allocation uses stable passenger IDs, not sampled arrival order. Each arm
    keeps its configured role-specific fleet. No passenger may appear in both
    arms. An unavailable service therefore leaves only the service arm
    incomplete while the direct-bus arm can still arrive.
    """

    if policy_id not in _ADAPTIVE_SPLIT_POLICY_IDS:
        raise ValueError(
            "adaptation.policy_id for adaptive_split must be one of "
            f"{sorted(_ADAPTIVE_SPLIT_POLICY_IDS)}, got {policy_id!r}"
        )
    road_rngs = road_rngs or {role: None for role in _STOCHASTIC_ROLES}
    turnaround_rngs = turnaround_rngs or {
        role: None for role in _STOCHASTIC_ROLES
    }

    service_count = (3 * len(passengers)) // 5
    passengers_by_id = sorted(passengers, key=lambda passenger: passenger.id)
    service_ids = {
        passenger.id for passenger in passengers_by_id[:service_count]
    }
    service_passengers = tuple(
        passenger for passenger in passengers if passenger.id in service_ids
    )
    bus_passengers = tuple(
        passenger for passenger in passengers if passenger.id not in service_ids
    )

    # A2 treats road-volume feedback as a near-no-op.  Keep simultaneously
    # launched split arms on input-identical, independent traffic histories so
    # sequential function calls cannot leak future entries into earlier events.
    bus_traffic = traffic.clone_empty()
    service_traffic = traffic.clone_empty()

    _run_bus_only(
        G,
        config,
        bus_passengers,
        policy,
        bus_traffic,
        metrics,
        turnaround_noise_lambda=turnaround_noise_lambda,
        rng_road=road_rngs["direct_bus"],
        rng_turnaround=turnaround_rngs["direct_bus"],
        return_strategy=return_strategy,
    )
    _run_multimodal(
        G,
        config,
        service_passengers,
        policy,
        service_traffic,
        metrics,
        turnaround_noise_lambda=turnaround_noise_lambda,
        rng_road_shuttle=road_rngs["feeder_shuttle"],
        rng_road_lastmile=road_rngs["last_mile"],
        rng_turnaround_shuttle=turnaround_rngs["feeder_shuttle"],
        rng_turnaround_lastmile=turnaround_rngs["last_mile"],
        return_strategy=return_strategy,
    )


def _run_adaptive_fallback(
    G: nx.DiGraph,
    config: dict,
    passengers: tuple[Passenger, ...],
    policy: DeparturePolicy,
    traffic: DynamicRoadTraffic,
    metrics: MetricsCollector,
    *,
    policy_id: str | None,
    turnaround_noise_lambda: float = 0.0,
    road_rngs: dict[str, np.random.Generator | None] | None = None,
    turnaround_rngs: dict[str, np.random.Generator | None] | None = None,
    return_strategy: str = "legacy_none",
) -> None:
    """Use static multimodal service or a timed station-to-D road fallback.

    Available and degraded service states delegate to the unchanged multimodal
    pipeline. When rail is unavailable, passengers still take the configured
    feeder and transfer stages, wait at the access station for the policy
    threshold, then use a finite fallback fleet from the station to D.
    """

    if policy_id not in _STATION_FALLBACK_HOLDS_MIN:
        raise ValueError(
            "adaptation.policy_id for adaptive_fallback must be one of "
            f"{sorted(_STATION_FALLBACK_HOLDS_MIN)}, got {policy_id!r}"
        )
    road_rngs = road_rngs or {role: None for role in _STOCHASTIC_ROLES}
    turnaround_rngs = turnaround_rngs or {
        role: None for role in _STOCHASTIC_ROLES
    }

    spec = _resolve_service_spec(config)
    if spec.available:
        _run_multimodal(
            G,
            config,
            passengers,
            policy,
            traffic,
            metrics,
            turnaround_noise_lambda=turnaround_noise_lambda,
            rng_road_shuttle=road_rngs["feeder_shuttle"],
            rng_road_lastmile=road_rngs["last_mile"],
            rng_turnaround_shuttle=turnaround_rngs["feeder_shuttle"],
            rng_turnaround_lastmile=turnaround_rngs["last_mile"],
            return_strategy=return_strategy,
        )
        return
    if not passengers:
        return

    multimodal_conf = config.get("multimodal", {})
    adaptation_conf = config.get("adaptation", {})
    group_size = config["personnel"]["group_size"]
    assembly_time = config["personnel"]["assembly_time"]
    rerouting_conf = config.get("failure", {}).get("rerouting", {})

    traffic.set_road_noise_rng(road_rngs["feeder_shuttle"])
    shuttle_traveler = _make_route_traveler(
        G,
        traffic,
        "A",
        spec.access_id,
        allowed_modes={"road"},
        rerouting_config=rerouting_conf,
        metrics=metrics,
    )
    shuttle_return_traveler = None
    if return_strategy == "reverse_network":
        shuttle_return_traveler = _make_route_traveler(
            G,
            traffic,
            spec.access_id,
            "A",
            allowed_modes={"road"},
            rerouting_config=rerouting_conf,
        )
    shuttle_plan = _plan_origin_dispatches(
        passengers=passengers,
        policy=policy,
        vehicle_capacity=group_size,
        dispatch_interval=multimodal_conf.get(
            "shuttle_dispatch_interval_min",
            DEFAULT_DISPATCH_INTERVAL_MIN,
        ),
        first_depart_time=_optional_config_time(
            multimodal_conf,
            "shuttle_first_departure_min",
            assembly_time,
        ),
        mode="shuttle",
        route=("A", spec.access_id),
    )
    station_batches = _execute_vehicle_trips(
        shuttle_plan,
        traveler=shuttle_traveler,
        fleet_size=multimodal_conf.get("shuttle_fleet_size", 1),
        vehicle_capacity=group_size,
        turnaround_time=multimodal_conf.get(
            "shuttle_turnaround_min",
            DEFAULT_TURNAROUND_MIN,
        ),
        metrics=metrics,
        record_arrivals_at_destination=False,
        resource_mode="bus",
        passenger_ready_times={
            passenger.id: passenger.arrival_time for passenger in passengers
        },
        wait_stage="assembly",
        turnaround_noise_lambda=turnaround_noise_lambda,
        rng_turnaround=turnaround_rngs["feeder_shuttle"],
        return_traveler=shuttle_return_traveler,
    )
    transfer_batches = _apply_transfer_batches(
        station_batches,
        base_min=multimodal_conf.get("transfer_time_min", 0.0),
        per_passenger_min=multimodal_conf.get("transfer_per_passenger_min", 0.0),
        metrics=metrics,
    )
    hold_min = _STATION_FALLBACK_HOLDS_MIN[policy_id]
    for batch in transfer_batches:
        metrics.record_passenger_wait(
            "transfer",
            hold_min,
            len(batch.passenger_ids),
            count_passengers=False,
        )
    fallback_batches = [
        StationBatch(
            ready_time=batch.ready_time + hold_min,
            passenger_ids=batch.passenger_ids,
        )
        for batch in transfer_batches
    ]

    traffic.set_road_noise_rng(road_rngs["fallback_bus"])
    fallback_traveler = _make_route_traveler(
        G,
        traffic,
        spec.access_id,
        "D",
        allowed_modes={"road"},
        rerouting_config=rerouting_conf,
        metrics=metrics,
    )
    fallback_return_traveler = None
    if return_strategy == "reverse_network":
        fallback_return_traveler = _make_route_traveler(
            G,
            traffic,
            "D",
            spec.access_id,
            allowed_modes={"road"},
            rerouting_config=rerouting_conf,
        )

    _execute_lastmile_batches(
        fallback_batches,
        traveler=fallback_traveler,
        dispatch_interval=adaptation_conf.get(
            "fallback_dispatch_interval_min",
            multimodal_conf.get("lastmile_dispatch_interval_min", 0.0),
        ),
        vehicle_capacity=adaptation_conf.get(
            "fallback_vehicle_capacity",
            multimodal_conf.get("lastmile_vehicle_capacity", group_size),
        ),
        fleet_size=require_int_at_least(
            adaptation_conf.get("fallback_fleet_size"),
            "adaptation.fallback_fleet_size",
            1,
        ),
        turnaround_time=adaptation_conf.get(
            "fallback_turnaround_min",
            multimodal_conf.get(
                "lastmile_turnaround_min",
                DEFAULT_TURNAROUND_MIN,
            ),
        ),
        first_depart_time=_optional_config_time(
            adaptation_conf,
            "fallback_first_departure_min",
            _optional_config_time(
                multimodal_conf,
                "lastmile_first_departure_min",
                0.0,
            ),
        ),
        metrics=metrics,
        egress_id=spec.access_id,
        turnaround_noise_lambda=turnaround_noise_lambda,
        rng_turnaround=turnaround_rngs["fallback_bus"],
        return_traveler=fallback_return_traveler,
    )


def _sample_disruptions(
    G: nx.DiGraph,
    config: dict,
    params: dict,
    rng: np.random.Generator,
) -> dict[Edge, EdgeDisruption]:
    """Sample structured disruptions from scenario failure configuration."""
    failure_conf = config.get("failure", {})
    if "forced_edges" in failure_conf:
        return _forced_edge_disruptions(G, failure_conf)
    return sample_edge_disruptions(
        G,
        params["p_fail_scale"],
        rng,
        mode=failure_conf.get("mode", "blocked"),
        capacity_reduction_factor=failure_conf.get("capacity_reduction_factor", 0.5),
        road_travel_time_multiplier=failure_conf.get(
            "road_travel_time_multiplier", 1.0
        ),
    )


def _forced_edge_disruptions(
    G: nx.DiGraph,
    failure_conf: dict,
) -> dict[Edge, EdgeDisruption]:
    """Build a sparse deterministic disruption map for explicit road edges."""

    mode = str(failure_conf.get("mode", "blocked"))
    if mode not in {"none", "blocked", "capacity_reduction"}:
        raise ValueError(f"unsupported forced-edge failure mode: {mode!r}")
    raw_edges = failure_conf.get("forced_edges")
    if not isinstance(raw_edges, Sequence) or isinstance(raw_edges, (str, bytes)):
        raise ValueError("failure.forced_edges must be a sequence of edge pairs")
    if mode == "none":
        return {}

    if mode == "capacity_reduction":
        state = EdgeDisruption(
            status="degraded",
            capacity_factor=float(
                failure_conf.get("capacity_reduction_factor", 0.5)
            ),
            travel_time_multiplier=float(
                failure_conf.get("road_travel_time_multiplier", 1.0)
            ),
        )
    else:
        state = EdgeDisruption(status="blocked", capacity_factor=0.0)

    disruptions: dict[Edge, EdgeDisruption] = {}
    for index, raw_edge in enumerate(raw_edges):
        if (
            not isinstance(raw_edge, Sequence)
            or isinstance(raw_edge, (str, bytes))
            or len(raw_edge) != 2
        ):
            raise ValueError(
                f"failure.forced_edges[{index}] must contain exactly two nodes"
            )
        edge = (raw_edge[0], raw_edge[1])
        if not G.has_edge(*edge):
            raise ValueError(f"forced disruption edge missing from graph: {edge!r}")
        if G.edges[edge].get("mode", "road") != "road":
            raise ValueError(f"forced disruption edge must be road mode: {edge!r}")
        disruptions[edge] = state
    if not disruptions:
        raise ValueError("forced-edge disruption requires at least one edge")
    return disruptions


def _optional_config_time(conf: dict, key: str, default: float) -> float:
    """Read an optional non-negative schedule time from a config namespace."""
    value = conf.get(key, default)
    if value is None:
        value = default
    return require_non_negative(value, key)


def _resolve_return_strategy(config: dict) -> str:
    """Resolve and validate vehicle return behavior without changing legacy runs."""
    strategy = config.get("fleet", {}).get("return_strategy", "legacy_none")
    if not isinstance(strategy, str) or strategy not in _RETURN_STRATEGIES:
        raise ValueError(
            "fleet.return_strategy must be one of "
            f"{sorted(_RETURN_STRATEGIES)}, got {strategy!r}"
        )
    return str(strategy)


def _resolve_adaptive_policy_id(config: dict, scenario_type: str) -> str | None:
    """Validate the policy identifier required by adaptive scenario types."""
    if scenario_type not in {"adaptive_split", "adaptive_fallback"}:
        return None

    adaptation_conf = config.get("adaptation")
    if not isinstance(adaptation_conf, dict):
        raise ValueError(
            f"adaptation.policy_id is required for {scenario_type}"
        )
    policy_id = adaptation_conf.get("policy_id")
    if not isinstance(policy_id, str) or not policy_id:
        raise ValueError(
            f"adaptation.policy_id is required for {scenario_type}"
        )

    if scenario_type == "adaptive_split" and policy_id not in _ADAPTIVE_SPLIT_POLICY_IDS:
        raise ValueError(
            "adaptation.policy_id for adaptive_split must be one of "
            f"{sorted(_ADAPTIVE_SPLIT_POLICY_IDS)}, got {policy_id!r}"
        )
    if scenario_type == "adaptive_fallback" and policy_id not in _STATION_FALLBACK_HOLDS_MIN:
        raise ValueError(
            "adaptation.policy_id for adaptive_fallback must be one of "
            f"{sorted(_STATION_FALLBACK_HOLDS_MIN)}, got {policy_id!r}"
        )
    return policy_id


def _plan_origin_dispatches(
    *,
    passengers: tuple[Passenger, ...],
    policy: DeparturePolicy,
    vehicle_capacity: int,
    dispatch_interval: float,
    first_depart_time: float,
    mode: str,
    route: Sequence[str],
) -> list[VehicleTrip]:
    """Plan manifests from the origin queue using the shared dispatch helper."""
    return plan_dispatches(
        passengers=passengers,
        policy=policy,
        vehicle_capacity=vehicle_capacity,
        dispatch_interval=dispatch_interval,
        travel_time=0.0,
        first_depart_time=first_depart_time,
        expected_passengers_per_dispatch=vehicle_capacity,
        mode=mode,
        route=route,
    )


def _execute_vehicle_trips(
    planned_trips: list[VehicleTrip],
    *,
    traveler: RouteTraveler,
    fleet_size: int,
    vehicle_capacity: int,
    turnaround_time: float,
    metrics: MetricsCollector,
    record_arrivals_at_destination: bool,
    resource_mode: str,
    passenger_ready_times: dict[int, float] | None = None,
    wait_stage: str | None = None,
    wait_count_passengers: bool = True,
    turnaround_noise_lambda: float = 0.0,
    rng_turnaround: np.random.Generator | None = None,
    return_traveler: RouteTraveler | None = None,
) -> list[StationBatch]:
    """Apply fleet availability, traverse routes, and optionally record arrivals."""
    ready_batches: list[StationBatch] = []
    fleet = FleetAvailability(
        fleet_size=fleet_size,
        turnaround_time=turnaround_time,
        turnaround_noise_lambda=turnaround_noise_lambda,
        rng_turnaround=rng_turnaround,
    )

    for planned in planned_trips:
        depart_time = _next_vehicle_departure(fleet, planned.depart_time)
        if depart_time > metrics.time_limit:
            break

        travel_time, route = traveler(depart_time)
        if not math.isfinite(travel_time):
            continue

        return_time = 0.0
        if return_traveler is not None:
            return_time, _ = return_traveler(depart_time + travel_time)

        assignment = fleet.reserve(
            planned.depart_time,
            travel_time,
            return_time=return_time,
        )

        _record_vehicle_usage(
            metrics,
            resource_mode,
            travel_time,
            passenger_count=len(planned.passenger_ids),
            vehicle_capacity=vehicle_capacity,
        )
        if return_traveler is None or math.isfinite(return_time):
            metrics.record_road_vehicle_cycle()
        if return_traveler is not None and math.isfinite(return_time):
            metrics.record_empty_return(return_time)
        if passenger_ready_times is not None and wait_stage is not None:
            _record_manifest_wait(
                metrics,
                wait_stage,
                planned.passenger_ids,
                assignment.depart_time,
                passenger_ready_times,
                count_passengers=wait_count_passengers,
            )

        actual_trip = VehicleTrip(
            mode=planned.mode,
            depart_time=assignment.depart_time,
            arrival_time=assignment.arrival_time,
            passenger_ids=planned.passenger_ids,
            route=route,
        )

        if record_arrivals_at_destination:
            _record_trip_arrivals(metrics, actual_trip)
        else:
            ready_batches.append(_trip_to_station_batch(actual_trip))

    return ready_batches


def _execute_lastmile_batches(
    batches: list[StationBatch],
    *,
    traveler: RouteTraveler,
    dispatch_interval: float,
    vehicle_capacity: int,
    fleet_size: int,
    turnaround_time: float,
    first_depart_time: float,
    metrics: MetricsCollector,
    egress_id: str = "R",
    turnaround_noise_lambda: float = 0.0,
    rng_turnaround: np.random.Generator | None = None,
    return_traveler: RouteTraveler | None = None,
) -> None:
    """Move service-arrived passengers through a finite last-mile fleet."""
    planned = _plan_lastmile_dispatches(
        batches,
        vehicle_capacity=vehicle_capacity,
        dispatch_interval=dispatch_interval,
        first_depart_time=first_depart_time,
        egress_id=egress_id,
    )
    _execute_vehicle_trips(
        planned,
        traveler=traveler,
        fleet_size=fleet_size,
        vehicle_capacity=vehicle_capacity,
        turnaround_time=turnaround_time,
        metrics=metrics,
        record_arrivals_at_destination=True,
        resource_mode="lastmile",
        passenger_ready_times={
            passenger_id: batch.ready_time
            for batch in batches
            for passenger_id in batch.passenger_ids
        },
        wait_stage="transfer",
        wait_count_passengers=False,
        turnaround_noise_lambda=turnaround_noise_lambda,
        rng_turnaround=rng_turnaround,
        return_traveler=return_traveler,
    )


def _plan_lastmile_dispatches(
    batches: list[StationBatch],
    *,
    vehicle_capacity: int,
    dispatch_interval: float,
    first_depart_time: float,
    egress_id: str = "R",
) -> list[VehicleTrip]:
    """Plan last-mile manifests from the service-egress passenger queue."""
    passengers = _station_batches_to_passengers(batches)
    if not passengers:
        return []

    vehicle_capacity = require_int_at_least(
        vehicle_capacity,
        "lastmile_vehicle_capacity",
        1,
    )
    dispatch_interval = require_non_negative(
        dispatch_interval,
        "lastmile_dispatch_interval_min",
    )
    first_depart_time = require_non_negative(
        first_depart_time,
        "lastmile_first_departure_min",
    )

    if dispatch_interval > 0.0:
        return plan_dispatches(
            passengers=passengers,
            policy=StrictPolicy(),
            vehicle_capacity=vehicle_capacity,
            dispatch_interval=dispatch_interval,
            travel_time=0.0,
            first_depart_time=first_depart_time,
            expected_passengers_per_dispatch=vehicle_capacity,
            mode="lastmile",
            route=(egress_id, "D"),
        )

    return _plan_on_demand_lastmile_dispatches(
        passengers,
        vehicle_capacity=vehicle_capacity,
        first_depart_time=first_depart_time,
        egress_id=egress_id,
    )


def _station_batches_to_passengers(
    batches: Sequence[StationBatch],
) -> tuple[Passenger, ...]:
    """Flatten station-ready batches into queue records."""
    passengers = [
        Passenger(id=passenger_id, arrival_time=batch.ready_time)
        for batch in batches
        for passenger_id in batch.passenger_ids
    ]
    return tuple(sorted(passengers, key=lambda passenger: (passenger.arrival_time, passenger.id)))


def _plan_on_demand_lastmile_dispatches(
    passengers: Sequence[Passenger],
    *,
    vehicle_capacity: int,
    first_depart_time: float,
    egress_id: str = "R",
) -> list[VehicleTrip]:
    """Plan immediate last-mile departures when no interval is configured."""
    queue = list(passengers)
    trips: list[VehicleTrip] = []

    while queue:
        depart_time = max(queue[0].arrival_time, first_depart_time)
        arrived_count = 0
        for passenger in queue:
            if passenger.arrival_time > depart_time:
                break
            arrived_count += 1

        boarded = queue[: min(vehicle_capacity, arrived_count)]
        queue = queue[len(boarded):]
        trips.append(
            VehicleTrip(
                mode="lastmile",
                depart_time=depart_time,
                arrival_time=depart_time,
                passenger_ids=tuple(passenger.id for passenger in boarded),
                route=(egress_id, "D"),
            )
        )

    return trips


def _next_vehicle_departure(fleet: FleetAvailability, requested_depart_time: float) -> float:
    """Return when the next vehicle can actually depart."""
    return max(float(requested_depart_time), min(fleet.next_available_times))


def _record_vehicle_usage(
    metrics: MetricsCollector,
    resource_mode: str,
    travel_time: float,
    *,
    passenger_count: int,
    vehicle_capacity: int,
) -> None:
    """Accumulate vehicle usage counters for a completed trip."""
    metrics.record_road_vehicle_load(passenger_count, vehicle_capacity)
    metrics.passenger_travel_minutes += travel_time * passenger_count
    if resource_mode == "bus":
        metrics.bus_trips += 1
        metrics.bus_minutes += travel_time
        return
    if resource_mode == "lastmile":
        metrics.lastmile_minutes += travel_time
        metrics.lastmile_vehicle_minutes += travel_time
        return
    raise ValueError(f"unsupported vehicle resource mode: {resource_mode}")


def _record_manifest_wait(
    metrics: MetricsCollector,
    stage: str,
    passenger_ids: Sequence[int],
    depart_time: float,
    ready_times: dict[int, float],
    *,
    count_passengers: bool = True,
) -> None:
    """Record passenger waits through the actual, fleet-adjusted departure."""
    for passenger_id in passenger_ids:
        wait_time = max(0.0, depart_time - ready_times[passenger_id])
        metrics.record_passenger_wait(
            stage,
            wait_time,
            count_passengers=count_passengers,
        )


def _record_trip_arrivals(metrics: MetricsCollector, trip: VehicleTrip) -> None:
    """Record all passengers on a destination-bound trip if it completes in time."""
    if trip.arrival_time <= metrics.time_limit:
        _record_arrivals(metrics, trip.passenger_ids, trip.arrival_time)


def _record_arrivals(
    metrics: MetricsCollector,
    passenger_ids: Sequence[int],
    arrival_time: float,
) -> None:
    for passenger_id in passenger_ids:
        metrics.record_arrival(passenger_id, arrival_time)


def _trip_to_station_batch(trip: VehicleTrip) -> StationBatch:
    """Convert an upstream vehicle arrival into a station-ready batch."""
    return StationBatch(
        ready_time=trip.arrival_time,
        passenger_ids=trip.passenger_ids,
    )


def _apply_transfer_batches(
    batches: list[StationBatch],
    *,
    base_min: float,
    per_passenger_min: float,
    metrics: MetricsCollector | None = None,
) -> list[StationBatch]:
    """Apply fixed plus crowd-dependent transfer delay to station batches."""
    ready: list[StationBatch] = []
    for batch in batches:
        delay = compute_transfer_delay(
            len(batch.passenger_ids),
            base_min=base_min,
            per_passenger_min=per_passenger_min,
        )
        if metrics is not None:
            metrics.record_passenger_wait(
                "transfer",
                delay,
                passenger_count=len(batch.passenger_ids),
            )
        ready.append(
            StationBatch(
                ready_time=batch.ready_time + delay,
                passenger_ids=batch.passenger_ids,
            )
        )
    return sorted(ready, key=lambda batch: batch.ready_time)


@dataclass(frozen=True)
class ServiceSpec:
    """A composable fixed-headway service leg (rail / sea / air).

    Carries the node IDs and timing the pipeline needs to compose
    ``assembly -> shuttle -> service.access -> service-leg -> service.egress ->
    last-mile -> destination`` for any mode. ``first_departure_min`` is the
    legacy ``rail_first_departure_min`` knob, generalized.
    """

    mode: str
    access_id: str
    egress_id: str
    travel_time_min: float
    headway_min: float
    capacity: int
    first_departure_min: float | None = None
    available: bool = True


def _service_spec_from_legacy_rail(config: dict) -> ServiceSpec:
    """Build a rail ``ServiceSpec`` from ``rail_link[0]`` + multimodal config.

    Keeps the legacy rail path feeding the exact same values into the
    generalized runner (KPI byte-identity).
    """

    rail_link = config.get("network", {}).get("rail_link") or []
    if not rail_link:
        raise ValueError(
            "default multimodal service_mode='rail' requires a non-empty "
            "network.rail_link; this region has none — set "
            "multimodal.service_mode to a configured non-rail service"
        )
    rail = rail_link[0]
    multimodal_conf = config.get("multimodal", {})
    resolved = resolve_rail_service(
        float(rail[2]),
        state=multimodal_conf.get("rail_status", "available"),
        degradation_multiplier=multimodal_conf.get(
            "rail_degradation_multiplier",
            1.0,
        ),
    )
    return ServiceSpec(
        mode="rail",
        access_id=str(rail[0]),
        egress_id=str(rail[1]),
        travel_time_min=(
            resolved.base_travel_time_min
            if resolved.effective_travel_time_min is None
            else resolved.effective_travel_time_min
        ),
        headway_min=float(rail[3]),
        capacity=int(rail[4]),
        first_departure_min=multimodal_conf.get("rail_first_departure_min"),
        available=resolved.is_available,
    )


def _record_service_trip(
    metrics: MetricsCollector,
    mode: str,
    travel_time: float,
    *,
    passenger_count: int,
) -> None:
    """Accumulate a fixed-headway service trip.

    Rail writes the legacy ``train_trips`` / ``train_minutes`` counters
    (byte-identical to the legacy runner); non-rail modes write the additive
    ``service_trips`` / ``service_minutes`` dicts. All modes advance
    ``passenger_travel_minutes``.
    """

    metrics.passenger_travel_minutes += travel_time * passenger_count
    if mode == "rail":
        metrics.train_trips += 1
        metrics.train_minutes += travel_time
        return
    metrics.service_trips[mode] = metrics.service_trips.get(mode, 0) + 1
    metrics.service_minutes[mode] = metrics.service_minutes.get(mode, 0.0) + travel_time


def _run_fixed_headway_service(
    config: dict,
    station_batches: list[StationBatch],
    metrics: MetricsCollector,
    *,
    spec: ServiceSpec,
) -> list[StationBatch]:
    """Move station-ready batches through a fixed-headway service leg.

    Mode-generic (rail / sea / air). The dispatch loop — first-departure
    seeding, ``queue[:capacity]`` boarding, ``depart_time += headway`` advance
    — is byte-identical to the legacy rail runner so the rail path produces
    identical KPIs.
    """

    if not station_batches or not spec.available:
        return []

    service_time = spec.travel_time_min
    headway = spec.headway_min
    capacity = spec.capacity
    if headway <= 0 or capacity <= 0:
        return []

    ready_passengers = [
        Passenger(id=passenger_id, arrival_time=batch.ready_time)
        for batch in station_batches
        for passenger_id in batch.passenger_ids
    ]
    ready_passengers.sort(key=lambda passenger: (passenger.arrival_time, passenger.id))

    queue: list[Passenger] = []
    next_idx = 0
    delivered = 0
    n = len(ready_passengers)
    depart_time = next_departure_time(
        ready_passengers[0].arrival_time,
        headway,
        first_departure_min=spec.first_departure_min,
    )
    arrivals: list[StationBatch] = []

    while delivered < n:
        while next_idx < n and ready_passengers[next_idx].arrival_time <= depart_time:
            queue.append(ready_passengers[next_idx])
            next_idx += 1

        if not queue:
            if next_idx >= n:
                break
            depart_time = next_departure_time(
                ready_passengers[next_idx].arrival_time,
                headway,
                first_departure_min=spec.first_departure_min,
            )
            continue

        if depart_time > metrics.time_limit:
            break

        boarded = queue[:capacity]
        queue = queue[capacity:]
        delivered += len(boarded)
        if spec.mode == "rail":
            metrics.record_rail_load(len(boarded), capacity)
        if spec.mode == "rail":
            for passenger in boarded:
                metrics.record_passenger_wait(
                    "rail",
                    max(0.0, depart_time - passenger.arrival_time),
                )
        _record_service_trip(metrics, spec.mode, service_time, passenger_count=len(boarded))

        arrivals.append(
            StationBatch(
                ready_time=depart_time + service_time,
                passenger_ids=tuple(passenger.id for passenger in boarded),
            )
        )
        depart_time += headway

    return arrivals


def _run_rail_service(
    config: dict,
    station_batches: list[StationBatch],
    metrics: MetricsCollector,
) -> list[StationBatch]:
    """Backward-compatible rail-service runner (rail ``ServiceSpec`` shim)."""

    return _run_fixed_headway_service(
        config,
        station_batches,
        metrics,
        spec=_service_spec_from_legacy_rail(config),
    )


def _make_route_traveler(
    G: nx.DiGraph,
    traffic: DynamicRoadTraffic,
    source: str,
    target: str,
    *,
    allowed_modes: set[str],
    rerouting_config: dict | None = None,
    metrics: MetricsCollector | None = None,
) -> RouteTraveler:
    """Create a route traveler that chooses a dynamic shortest path at departure."""
    rerouting_enabled = (rerouting_config or {}).get("enabled", False)
    overhead_min = (rerouting_config or {}).get("overhead_min", 3.0)
    cache_departure_path = bool(
        (rerouting_config or {}).get("cache_departure_path", False)
    )
    cached_path: list[str] | None = None
    cache_initialized = False

    def travel(depart_time: float) -> tuple[float, tuple[str, ...]]:
        nonlocal cached_path, cache_initialized
        if cache_departure_path and cache_initialized:
            path = list(cached_path or ())
        else:
            path = _shortest_path_at_time(
                G,
                traffic,
                source,
                target,
                depart_time,
                allowed_modes=allowed_modes,
            )
            if cache_departure_path:
                cached_path = list(path)
                cache_initialized = True
        if not path:
            return float("inf"), ()

        if not rerouting_enabled:
            travel_time, _ = traffic.traverse_route(path, depart_time)
            return travel_time, tuple(path)

        travel_time, actual_path = _traverse_with_rerouting(
            G,
            traffic,
            path,
            depart_time,
            target,
            allowed_modes=allowed_modes,
            overhead_min=overhead_min,
            metrics=metrics,
        )
        return travel_time, actual_path

    return travel


def _shortest_path_at_time(
    G: nx.DiGraph,
    traffic: DynamicRoadTraffic,
    source: str,
    target: str,
    depart_time: float,
    *,
    allowed_modes: set[str],
) -> list[str]:
    """Find a shortest path using current dynamic traffic state."""
    edge_weights: dict[Edge, float] = {}

    def weight(u: str, v: str, data: dict) -> float:
        edge = (u, v)
        if edge not in edge_weights:
            if data.get("mode", "road") not in allowed_modes:
                edge_weights[edge] = float("inf")
            else:
                edge_weights[edge] = _edge_weight_at_time(
                    traffic,
                    edge,
                    data,
                    depart_time,
                )
        return edge_weights[edge]

    try:
        path = nx.shortest_path(
            G,
            source,
            target,
            weight=weight,
        )
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return []

    path_weight = sum(
        weight(u, v, G.edges[u, v])
        for u, v in zip(path, path[1:])
    )
    if not math.isfinite(path_weight):
        return []
    return path


def _edge_weights_at_time(
    G: nx.DiGraph,
    traffic: DynamicRoadTraffic,
    depart_time: float,
    *,
    allowed_modes: set[str],
) -> dict[Edge, float]:
    """Return immutable route weights for one departure-time routing decision."""
    weights: dict[Edge, float] = {}
    for u, v, data in G.edges(data=True):
        edge = (u, v)
        if data.get("mode", "road") not in allowed_modes:
            weights[edge] = float("inf")
        else:
            weights[edge] = _edge_weight_at_time(traffic, edge, data, depart_time)
    return weights


def _path_weight(path: Sequence[str], edge_weights: dict[Edge, float]) -> float:
    """Sum precomputed edge weights for a path."""
    return sum(edge_weights[(u, v)] for u, v in zip(path, path[1:]))


def _edge_weight_at_time(
    traffic: DynamicRoadTraffic,
    edge: Edge,
    data: dict,
    depart_time: float,
) -> float:
    disruption = traffic.disruptions.get(edge, EdgeDisruption())
    if disruption.is_blocked:
        return float("inf")

    mode = data.get("mode", "road")
    if mode != "road":
        return float(data["t0"])

    capacity = float(data.get("capacity", 0.0)) * disruption.capacity_factor
    if capacity <= 0:
        return float("inf")

    current_volume = traffic.current_volume(edge, depart_time)
    current_vehicle_volume = 60.0 / traffic.volume_window_min
    return bpr_travel_time(
        t0=float(data["t0"]) * disruption.travel_time_multiplier,
        volume=current_volume + current_vehicle_volume,
        capacity=capacity,
        alpha=traffic.alpha,
        beta=traffic.beta,
        scale=traffic.scale,
    )


def _reroute_around_blocked_edge(
    G: nx.DiGraph,
    blocked_edge: Edge,
    target: str,
    traffic: DynamicRoadTraffic,
    *,
    allowed_modes: set[str],
) -> list[str] | None:
    u, _ = blocked_edge

    def _weight(nu: str, nv: str, data: dict) -> float:
        if data.get("mode", "road") not in allowed_modes:
            return float("inf")
        disruption = traffic.disruptions.get((nu, nv), EdgeDisruption())
        if disruption.is_blocked:
            return float("inf")
        return float(data.get("t0", 1.0))

    try:
        path = nx.shortest_path(G, u, target, weight=_weight)
        total = sum(
            _weight(path[i], path[i + 1], G.edges[path[i], path[i + 1]])
            for i in range(len(path) - 1)
        )
        if not math.isfinite(total):
            return None
        return path
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None


def _traverse_with_rerouting(
    G: nx.DiGraph,
    traffic: DynamicRoadTraffic,
    initial_path: list[str],
    depart_time: float,
    target: str,
    *,
    allowed_modes: set[str],
    overhead_min: float,
    metrics: MetricsCollector | None,
) -> tuple[float, tuple[str, ...]]:
    current_time = depart_time
    actual_nodes = [initial_path[0]]
    edges = list(zip(initial_path, initial_path[1:]))
    idx = 0
    reroute_count = 0
    max_reroutes = len(G.nodes) + 1

    while idx < len(edges):
        u, v = edges[idx]
        edge_data = G.edges[(u, v)]
        mode = edge_data.get("mode", "road")
        disruption = traffic.disruptions.get((u, v), EdgeDisruption())

        if mode == "road" and disruption.is_blocked:
            if reroute_count >= max_reroutes:
                return float("inf"), tuple(actual_nodes)
            alt = _reroute_around_blocked_edge(
                G, (u, v), target, traffic,
                allowed_modes=allowed_modes,
            )
            if alt and len(alt) > 1:
                reroute_count += 1
                if metrics is not None:
                    metrics.rerouting_events += 1
                current_time += overhead_min
                edges = list(zip(alt, alt[1:]))
                idx = 0
                continue
            return float("inf"), tuple(actual_nodes)

        traversal = traffic.enter_edge((u, v), current_time)

        if not math.isfinite(traversal.travel_time):
            if mode == "road" and reroute_count < max_reroutes:
                alt = _reroute_around_blocked_edge(
                    G, (u, v), target, traffic,
                    allowed_modes=allowed_modes,
                )
                if alt and len(alt) > 1:
                    reroute_count += 1
                    if metrics is not None:
                        metrics.rerouting_events += 1
                    current_time += overhead_min
                    edges = list(zip(alt, alt[1:]))
                    idx = 0
                    continue
            return float("inf"), tuple(actual_nodes)

        actual_nodes.append(v)
        current_time = traversal.exit_time
        idx += 1

    return current_time - depart_time, tuple(actual_nodes)


def _make_passengers(arrival_times: np.ndarray) -> tuple[Passenger, ...]:
    """Create sorted passenger records from absolute arrival times."""
    passengers = [
        Passenger(id=index, arrival_time=float(arrival_time))
        for index, arrival_time in enumerate(arrival_times)
    ]
    return tuple(sorted(passengers, key=lambda passenger: (passenger.arrival_time, passenger.id)))


def _compute_all_travel_times(
    G, config, scale, failed_edges,
) -> dict[tuple[str, str], float]:
    """Compute static BPR travel times for compatibility with older callers."""
    failed_set = set(failed_edges)
    alpha = config["bpr"]["alpha"]
    beta = config["bpr"]["beta"]
    volume = config.get("traffic", {}).get("background_volume", 100.0)
    times = {}
    for u, v, data in G.edges(data=True):
        if (u, v) in failed_set:
            times[(u, v)] = float("inf")
        else:
            times[(u, v)] = bpr_travel_time(
                t0=data["t0"],
                volume=volume,
                capacity=data["capacity"],
                alpha=alpha,
                beta=beta,
                scale=scale,
            )
    return times
