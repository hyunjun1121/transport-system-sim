"""Scenario execution for bus-only and rail-bus multimodal transport.

The scenario runner keeps the public ``run_scenario`` API stable while using
queue-based departure policy, fleet availability, fixed-headway rail dispatch,
structured disruptions, and dynamic road BPR traversal.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence

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
from src.rail import next_departure_time
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


RouteTraveler = Callable[[float], tuple[float, tuple[str, ...]]]
Edge = tuple[str, str]

DEFAULT_DISPATCH_INTERVAL_MIN = 5.0
DEFAULT_TURNAROUND_MIN = 5.0


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

    rng_arrival = np.random.default_rng(seed)
    rng_failure = np.random.default_rng(seed + 10_000)

    delays = sample_arrival_delays(
        n_personnel,
        mu=config["lateness"]["mu"],
        sigma=params["sigma"],
        rng=rng_arrival,
    )
    passengers = _make_passengers(assembly_time + delays)

    disruptions = _sample_disruptions(G, config, params, rng_failure)

    metrics = MetricsCollector(
        total_personnel=n_personnel,
        time_limit=time_limit,
        late_penalty_min=config.get("metrics", {}).get("late_penalty_min"),
    )
    traffic = DynamicRoadTraffic.from_config(
        G,
        config,
        params=params,
        disruptions=disruptions,
    )

    if scenario_type == "bus_only":
        _run_bus_only(G, config, passengers, policy, traffic, metrics)
    elif scenario_type == "multimodal":
        _run_multimodal(G, config, passengers, policy, traffic, metrics)
    else:
        raise ValueError(f"unknown scenario_type: {scenario_type}")

    metrics.leftover_count = n_personnel - metrics.success_count
    return metrics.as_dict()


def _run_bus_only(
    G: nx.DiGraph,
    config: dict,
    passengers: tuple[Passenger, ...],
    policy: DeparturePolicy,
    traffic: DynamicRoadTraffic,
    metrics: MetricsCollector,
) -> None:
    """Run queue-based bus-only transport from A to D."""
    bus_conf = config.get("bus", {})
    group_size = config["personnel"]["group_size"]
    assembly_time = config["personnel"]["assembly_time"]
    traveler = _make_route_traveler(G, traffic, "A", "D", allowed_modes={"road"})

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
        turnaround_time=bus_conf.get("turnaround_min", DEFAULT_TURNAROUND_MIN),
        metrics=metrics,
        record_arrivals_at_destination=True,
        resource_mode="bus",
    )


def _run_multimodal(
    G: nx.DiGraph,
    config: dict,
    passengers: tuple[Passenger, ...],
    policy: DeparturePolicy,
    traffic: DynamicRoadTraffic,
    metrics: MetricsCollector,
) -> None:
    """Run shuttle -> rail -> last-mile multimodal transport."""
    if not passengers:
        return

    multimodal_conf = config.get("multimodal", {})
    group_size = config["personnel"]["group_size"]
    assembly_time = config["personnel"]["assembly_time"]

    shuttle_traveler = _make_route_traveler(G, traffic, "A", "S", allowed_modes={"road"})
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
        route=("A", "S"),
    )
    station_batches = _execute_vehicle_trips(
        shuttle_plan,
        traveler=shuttle_traveler,
        fleet_size=multimodal_conf.get("shuttle_fleet_size", 1),
        turnaround_time=multimodal_conf.get(
            "shuttle_turnaround_min",
            DEFAULT_TURNAROUND_MIN,
        ),
        metrics=metrics,
        record_arrivals_at_destination=False,
        resource_mode="bus",
    )

    transfer_batches = _apply_transfer_batches(
        station_batches,
        base_min=multimodal_conf.get("transfer_time_min", 0.0),
        per_passenger_min=multimodal_conf.get("transfer_per_passenger_min", 0.0),
    )
    rail_arrivals = _run_rail_service(config, transfer_batches, metrics)

    lastmile_traveler = _make_route_traveler(G, traffic, "R", "D", allowed_modes={"road"})
    _execute_lastmile_batches(
        rail_arrivals,
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
    )


def _sample_disruptions(
    G: nx.DiGraph,
    config: dict,
    params: dict,
    rng: np.random.Generator,
) -> dict[Edge, EdgeDisruption]:
    """Sample structured disruptions from scenario failure configuration."""
    failure_conf = config.get("failure", {})
    return sample_edge_disruptions(
        G,
        params["p_fail_scale"],
        rng,
        mode=failure_conf.get("mode", "blocked"),
        capacity_reduction_factor=failure_conf.get("capacity_reduction_factor", 0.5),
    )


def _optional_config_time(conf: dict, key: str, default: float) -> float:
    """Read an optional non-negative schedule time from a config namespace."""
    value = conf.get(key, default)
    if value is None:
        value = default
    return require_non_negative(value, key)


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
    turnaround_time: float,
    metrics: MetricsCollector,
    record_arrivals_at_destination: bool,
    resource_mode: str,
) -> list[StationBatch]:
    """Apply fleet availability, traverse routes, and optionally record arrivals."""
    ready_batches: list[StationBatch] = []
    fleet = FleetAvailability(
        fleet_size=fleet_size,
        turnaround_time=turnaround_time,
    )

    for planned in planned_trips:
        depart_time = _next_vehicle_departure(fleet, planned.depart_time)
        if depart_time > metrics.time_limit:
            break

        travel_time, route = traveler(depart_time)
        if not math.isfinite(travel_time):
            continue

        assignment = fleet.reserve(planned.depart_time, travel_time)

        _record_vehicle_usage(
            metrics,
            resource_mode,
            travel_time,
            passenger_count=len(planned.passenger_ids),
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
) -> None:
    """Move rail-arrived passengers through a finite last-mile fleet."""
    planned = _plan_lastmile_dispatches(
        batches,
        vehicle_capacity=vehicle_capacity,
        dispatch_interval=dispatch_interval,
        first_depart_time=first_depart_time,
    )
    _execute_vehicle_trips(
        planned,
        traveler=traveler,
        fleet_size=fleet_size,
        turnaround_time=turnaround_time,
        metrics=metrics,
        record_arrivals_at_destination=True,
        resource_mode="lastmile",
    )


def _plan_lastmile_dispatches(
    batches: list[StationBatch],
    *,
    vehicle_capacity: int,
    dispatch_interval: float,
    first_depart_time: float,
) -> list[VehicleTrip]:
    """Plan last-mile manifests from the R-station passenger queue."""
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
            route=("R", "D"),
        )

    return _plan_on_demand_lastmile_dispatches(
        passengers,
        vehicle_capacity=vehicle_capacity,
        first_depart_time=first_depart_time,
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
                route=("R", "D"),
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
) -> None:
    """Accumulate vehicle usage counters for a completed trip."""
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
) -> list[StationBatch]:
    """Apply fixed plus crowd-dependent transfer delay to station batches."""
    ready: list[StationBatch] = []
    for batch in batches:
        delay = compute_transfer_delay(
            len(batch.passenger_ids),
            base_min=base_min,
            per_passenger_min=per_passenger_min,
        )
        ready.append(
            StationBatch(
                ready_time=batch.ready_time + delay,
                passenger_ids=batch.passenger_ids,
            )
        )
    return sorted(ready, key=lambda batch: batch.ready_time)


def _run_rail_service(
    config: dict,
    station_batches: list[StationBatch],
    metrics: MetricsCollector,
) -> list[StationBatch]:
    """Move station-ready batches through fixed-headway rail service."""
    if not station_batches:
        return []

    rail = config["network"]["rail_link"][0]
    rail_time = float(rail[2])
    headway = float(rail[3])
    capacity = int(rail[4])
    rail_first_departure = config.get("multimodal", {}).get(
        "rail_first_departure_min",
    )
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
    delivered_to_r = 0
    n = len(ready_passengers)
    depart_time = next_departure_time(
        ready_passengers[0].arrival_time,
        headway,
        first_departure_min=rail_first_departure,
    )
    rail_arrivals: list[StationBatch] = []

    while delivered_to_r < n:
        while next_idx < n and ready_passengers[next_idx].arrival_time <= depart_time:
            queue.append(ready_passengers[next_idx])
            next_idx += 1

        if not queue:
            if next_idx >= n:
                break
            depart_time = next_departure_time(
                ready_passengers[next_idx].arrival_time,
                headway,
                first_departure_min=rail_first_departure,
            )
            continue

        if depart_time > metrics.time_limit:
            break

        boarded = queue[:capacity]
        queue = queue[capacity:]
        delivered_to_r += len(boarded)
        metrics.train_trips += 1
        metrics.train_minutes += rail_time
        metrics.passenger_travel_minutes += rail_time * len(boarded)

        rail_arrivals.append(
            StationBatch(
                ready_time=depart_time + rail_time,
                passenger_ids=tuple(passenger.id for passenger in boarded),
            )
        )
        depart_time += headway

    return rail_arrivals


def _make_route_traveler(
    G: nx.DiGraph,
    traffic: DynamicRoadTraffic,
    source: str,
    target: str,
    *,
    allowed_modes: set[str],
) -> RouteTraveler:
    """Create a route traveler that chooses a dynamic shortest path at departure."""

    def travel(depart_time: float) -> tuple[float, tuple[str, ...]]:
        path = _shortest_path_at_time(
            G,
            traffic,
            source,
            target,
            depart_time,
            allowed_modes=allowed_modes,
        )
        if not path:
            return float("inf"), ()
        travel_time, _ = traffic.traverse_route(path, depart_time)
        return travel_time, tuple(path)

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
    edge_weights = _edge_weights_at_time(
        G,
        traffic,
        depart_time,
        allowed_modes=allowed_modes,
    )

    try:
        path = nx.shortest_path(
            G,
            source,
            target,
            weight=lambda u, v, _: edge_weights[(u, v)],
        )
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return []

    if not math.isfinite(_path_weight(path, edge_weights)):
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
        t0=float(data["t0"]),
        volume=current_volume + current_vehicle_volume,
        capacity=capacity,
        alpha=traffic.alpha,
        beta=traffic.beta,
        scale=traffic.scale,
    )


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
