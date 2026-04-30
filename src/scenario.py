"""SimPy scenario execution.

Two scenarios:
  bus_only:    A → (bus) → road network → D
  multimodal:  A → (shuttle) → S → (rail) → R → (last-mile) → D

Pattern: run_scenario(params, scenario, seed) → metrics dict
(inspired by inventory-simulation's run() → dict pattern)

Design:
  - Personnel arrive at A with LogNormal delays (lateness)
  - They are grouped into vehicle-sized batches
  - Departure policy decides when each batch departs
  - Vehicles traverse the network with BPR travel times
  - Rail uses SimPy Resource for capacity management
"""

import simpy
import numpy as np
import networkx as nx

from src.network import build_network
from src.models import (
    bpr_travel_time,
    sample_link_failures,
    sample_arrival_delays,
    find_shortest_path_time,
)
from src.policies import DeparturePolicy
from src.metrics import MetricsCollector


def run_scenario(
    G: nx.DiGraph,
    config: dict,
    scenario_type: str,
    policy: DeparturePolicy,
    params: dict,
    seed: int,
) -> dict:
    """Run a single scenario and return KPI dict.

    Args:
        G: transport network graph
        config: YAML configuration
        scenario_type: 'bus_only' or 'multimodal'
        policy: departure policy instance
        params: {s, p_fail_scale, sigma}
        seed: random seed for CRN pairing

    Returns:
        Dictionary of KPI metrics
    """
    rng = np.random.default_rng(seed)

    n_personnel = config["personnel"]["total"]
    group_size = config["personnel"]["group_size"]
    assembly_time = config["personnel"]["assembly_time"]

    # Sample stochastic elements (same seed = same samples for paired comparison)
    delays = sample_arrival_delays(
        n_personnel, mu=config["lateness"]["mu"], sigma=params["sigma"], rng=rng,
    )
    failed_edges = sample_link_failures(G, params["p_fail_scale"], rng)

    # Compute BPR travel times for each edge
    travel_times = _compute_all_travel_times(G, config, params["s"], failed_edges)

    # Get route travel times
    bus_route_time, bus_route = find_shortest_path_time(G, travel_times, "A", "D")
    shuttle_time = travel_times.get(("A", "S"), float("inf"))
    rail_time = travel_times.get(("S", "R"), float("inf"))
    lastmile_time = travel_times.get(("R", "D"), float("inf"))

    # Personnel absolute arrival times at A
    arrival_times = assembly_time + delays  # absolute time each person reaches A
    arrival_times.sort()  # sort for grouping

    # Setup SimPy
    env = simpy.Environment()
    metrics = MetricsCollector(
        total_personnel=n_personnel,
        time_limit=config["experiment"]["time_limit"],
    )

    if scenario_type == "bus_only":
        env.process(
            _bus_coordinator(env, arrival_times, group_size, policy,
                             bus_route_time, metrics)
        )
    else:
        rail_headway = config["network"]["rail_link"][0][3]
        rail_cap = config["network"]["rail_link"][0][4]
        env.process(
            _multimodal_coordinator(env, arrival_times, group_size, policy,
                                    shuttle_time, rail_time, lastmile_time,
                                    rail_headway, rail_cap, metrics)
        )

    env.run(until=config["experiment"]["time_limit"])
    metrics.leftover_count = n_personnel - metrics.success_count
    return metrics.as_dict()


def _compute_all_travel_times(
    G, config, scale, failed_edges,
) -> dict[tuple[str, str], float]:
    """Compute BPR travel times for every edge."""
    failed_set = set(failed_edges)
    alpha = config["bpr"]["alpha"]
    beta = config["bpr"]["beta"]
    times = {}
    for u, v, data in G.edges(data=True):
        if (u, v) in failed_set:
            times[(u, v)] = float("inf")
        else:
            times[(u, v)] = bpr_travel_time(
                t0=data["t0"], volume=100.0, capacity=data["capacity"],
                alpha=alpha, beta=beta, scale=scale,
            )
    return times


# ---------------------------------------------------------------------------
# Scenario 1: Bus-only
# ---------------------------------------------------------------------------

def _bus_coordinator(env, arrival_times, group_size, policy, route_time, metrics):
    """Coordinate bus dispatches for bus-only scenario.

    Groups personnel by arrival time, applies departure policy,
    dispatches buses through the road network.
    """
    if route_time == float("inf"):
        return  # route completely blocked

    n = len(arrival_times)
    groups = []
    # Create groups of group_size from sorted arrivals
    for i in range(0, n, group_size):
        groups.append(arrival_times[i : i + group_size])

    bus_interval = 5.0  # min between consecutive bus availabilities
    next_bus_available = 0.0

    for idx, group in enumerate(groups):
        scheduled_depart = arrival_times[0] + (idx * bus_interval)  # rough schedule

        # Wait until the last person in this group has arrived at A
        last_arrival = max(group)
        if last_arrival > env.now:
            yield env.timeout(last_arrival - env.now)

        # Apply departure policy: wait more if policy says so
        wait_start = env.now
        group_expected = len(group)
        while True:
            arrived = sum(1 for t in group if t <= env.now)
            elapsed = env.now - scheduled_depart
            if policy.should_depart(elapsed, arrived, group_expected, group_size):
                break
            # Wait a bit and re-check
            yield env.timeout(1.0)

        # Wait for bus availability
        if env.now < next_bus_available:
            yield env.timeout(next_bus_available - env.now)

        # Dispatch bus
        depart_time = env.now
        metrics.bus_trips += 1

        # Bus travel
        yield env.timeout(route_time)
        metrics.bus_minutes += route_time

        # All aboard personnel arrive at D
        for person_time in group:
            if person_time <= depart_time:  # only those who arrived before departure
                metrics.record_arrival(0, env.now)

        next_bus_available = env.now + bus_interval


# ---------------------------------------------------------------------------
# Scenario 2: Multimodal
# ---------------------------------------------------------------------------

def _multimodal_coordinator(
    env, arrival_times, group_size, policy,
    shuttle_time, rail_time, lastmile_time,
    rail_headway, rail_capacity, metrics,
):
    """Coordinate multimodal transport.

    Flow: A →(shuttle)→ S →(rail)→ R →(last-mile bus)→ D

    Shuttle buses take groups from A to S.
    Trains run on fixed headway from S with capacity limits.
    Last-mile buses take people from R to D.
    """
    if shuttle_time == float("inf") or rail_time == float("inf") or lastmile_time == float("inf"):
        return  # some segment blocked

    n = len(arrival_times)

    # Shared waiting areas
    station_S_queue = []     # people waiting at S for train
    arrived_at_D = simpy.Store(env)  # signal arrivals at D

    # --- Rail dispatch process ---
    def rail_process():
        """Trains depart from S on fixed headway."""
        train_count = 0
        while True:
            yield env.timeout(rail_headway)

            if not station_S_queue:
                continue

            # Board as many as capacity allows
            n_board = min(len(station_S_queue), rail_capacity)
            if n_board == 0:
                continue

            boarded = station_S_queue[:n_board]
            del station_S_queue[:n_board]
            train_count += 1
            metrics.train_trips += 1

            # Train travel S → R
            yield env.timeout(rail_time)
            metrics.train_minutes += rail_time * 1  # 1 train

            # Each person takes last-mile bus R → D
            for _ in boarded:
                metrics.lastmile_minutes += lastmile_time

            # Last-mile travel (grouped)
            yield env.timeout(lastmile_time)

            # Record arrivals at D
            for _ in boarded:
                metrics.record_arrival(0, env.now)

    # --- Shuttle dispatch process ---
    def shuttle_process():
        """Shuttle buses from A to S."""
        groups = []
        for i in range(0, n, group_size):
            groups.append(arrival_times[i : i + group_size])

        next_bus = 0.0

        for group in groups:
            # Wait until last person in group arrives at A
            last_arrival = max(group)
            if last_arrival > env.now:
                yield env.timeout(last_arrival - env.now)

            # Wait for bus
            if env.now < next_bus:
                yield env.timeout(next_bus - env.now)

            metrics.bus_trips += 1

            # Shuttle travel A → S
            yield env.timeout(shuttle_time)
            metrics.bus_minutes += shuttle_time

            # People arrive at station S
            for _ in group:
                station_S_queue.append(env.now)

            next_bus = env.now + 5.0  # bus turnaround

    # Start processes
    env.process(rail_process())
    yield from shuttle_process()  # run shuttle as main process

    # Wait for remaining people in rail system
    while station_S_queue:
        yield env.timeout(rail_headway)
