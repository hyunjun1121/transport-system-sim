"""Deterministic scenario regression tests.

These tests document Wave 1 target behavior for the scenario orchestrator.
They intentionally exercise the public run_scenario API and avoid pytest so the
file can be run directly with:

    .\.venv\Scripts\python tests\test_scenario.py

The assertions cover dispatch, fleet, rail, transfer, and censoring semantics
through deterministic stochastic fixtures.
"""

from contextlib import contextmanager
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import scenario as scenario_module
from src.network import build_network
from src.policies import GracePolicy, StrictPolicy
from src.sim_types import EdgeDisruption


PARAMS = {"s": 1.0, "p_fail_scale": 0.0, "sigma": 0.0}
HIGH_CAPACITY = 1_000_000_000


@contextmanager
def fixed_stochastic_inputs(delays):
    """Patch stochastic scenario inputs to fixed deterministic values."""
    original_delays = scenario_module.sample_arrival_delays
    original_disruptions = scenario_module.sample_edge_disruptions
    original_failures = scenario_module.sample_link_failures

    def sample_fixed_delays(n_personnel, mu, sigma, rng):
        assert n_personnel == len(delays), (
            f"fixture has {len(delays)} delays for {n_personnel} personnel"
        )
        return np.array(delays, dtype=float)

    def sample_no_disruptions(G, p_fail_scale, rng, **kwargs):
        return {(u, v): EdgeDisruption() for u, v in G.edges()}

    scenario_module.sample_arrival_delays = sample_fixed_delays
    scenario_module.sample_edge_disruptions = sample_no_disruptions
    scenario_module.sample_link_failures = lambda G, p_fail_scale, rng, **kwargs: []
    try:
        yield
    finally:
        scenario_module.sample_arrival_delays = original_delays
        scenario_module.sample_edge_disruptions = original_disruptions
        scenario_module.sample_link_failures = original_failures


def make_config(
    total,
    group_size,
    *,
    bus_route_time=5.0,
    shuttle_time=1.0,
    rail_time=1000.0,
    rail_headway=10.0,
    rail_capacity=100,
    lastmile_time=1.0,
    dispatch_interval=10.0,
    fleet_size=1,
    turnaround=0.0,
    time_limit=500.0,
    assembly_time=0.0,
    bus_first_departure=None,
    shuttle_first_departure=None,
    rail_first_departure=None,
    lastmile_fleet_size=None,
    lastmile_turnaround=None,
    lastmile_vehicle_capacity=None,
    lastmile_first_departure=None,
):
    """Build a small deterministic config for scenario behavior tests."""
    bus_conf = {
        "dispatch_interval_min": dispatch_interval,
        "fleet_size": fleet_size,
        "turnaround_min": turnaround,
    }
    if bus_first_departure is not None:
        bus_conf["first_departure_min"] = bus_first_departure

    multimodal_conf = {
        "shuttle_dispatch_interval_min": dispatch_interval,
        "shuttle_fleet_size": fleet_size,
        "transfer_time_min": 0.0,
        "transfer_per_passenger_min": 0.0,
        "lastmile_dispatch_interval_min": dispatch_interval,
    }
    if shuttle_first_departure is not None:
        multimodal_conf["shuttle_first_departure_min"] = shuttle_first_departure
    if rail_first_departure is not None:
        multimodal_conf["rail_first_departure_min"] = rail_first_departure
    if lastmile_fleet_size is not None:
        multimodal_conf["lastmile_fleet_size"] = lastmile_fleet_size
    if lastmile_turnaround is not None:
        multimodal_conf["lastmile_turnaround_min"] = lastmile_turnaround
    if lastmile_vehicle_capacity is not None:
        multimodal_conf["lastmile_vehicle_capacity"] = lastmile_vehicle_capacity
    if lastmile_first_departure is not None:
        multimodal_conf["lastmile_first_departure_min"] = lastmile_first_departure

    return {
        "network": {
            "nodes": ["H", "A", "S", "R", "D"],
            "road_links": [
                ["A", "D", bus_route_time, HIGH_CAPACITY, 0.0],
                ["A", "S", shuttle_time, HIGH_CAPACITY, 0.0],
                ["R", "D", lastmile_time, HIGH_CAPACITY, 0.0],
            ],
            "rail_link": [["S", "R", rail_time, rail_headway, rail_capacity]],
        },
        "personnel": {
            "total": total,
            "group_size": group_size,
            "assembly_time": assembly_time,
        },
        "bus": bus_conf,
        "multimodal": multimodal_conf,
        "traffic": {
            "volume_window_min": 60.0,
            "background_volume": 0.0,
        },
        "failure": {
            "mode": "blocked",
            "capacity_reduction_factor": 1.0,
        },
        "metrics": {
            "late_penalty_min": time_limit,
        },
        "bpr": {
            "alpha": 0.0,
            "beta": 4.0,
        },
        "lateness": {
            "distribution": "fixed-test-fixture",
            "mu": 0.0,
            "sigma_levels": [0.0],
        },
        "experiment": {
            "R": 1,
            "seed_base": 1,
            "time_limit": time_limit,
        },
    }


def run_fixed(config, scenario_type, policy, delays):
    """Run a scenario with fixed arrivals and no link failures."""
    G = build_network(config)
    with fixed_stochastic_inputs(delays):
        return scenario_module.run_scenario(
            G=G,
            config=config,
            scenario_type=scenario_type,
            policy=policy,
            params=PARAMS,
            seed=123,
        )


def assert_close(actual, expected, tolerance=0.05, label="value"):
    assert abs(actual - expected) <= tolerance, (
        f"{label}: expected {expected}, got {actual}"
    )


def test_origin_schedule_defaults_to_assembly_time():
    """Origin dispatch should use the assembly-time timetable, not first arrival."""
    config = make_config(
        total=1,
        group_size=1,
        bus_route_time=1.0,
        dispatch_interval=10.0,
        fleet_size=1,
        assembly_time=0.0,
    )

    result = run_fixed(config, "bus_only", StrictPolicy(), [6.0])

    assert result["success_count"] == 1
    assert result["bus_trips"] == 1
    assert_close(result["makespan"], 11.0, label="assembly-time schedule makespan")
    print("PASS: origin schedule defaults to assembly time")


def test_origin_schedule_accepts_explicit_first_departure():
    """Origin dispatch should accept an explicit first departure override."""
    config = make_config(
        total=1,
        group_size=1,
        bus_route_time=1.0,
        dispatch_interval=10.0,
        fleet_size=1,
        assembly_time=0.0,
        bus_first_departure=6.0,
    )

    result = run_fixed(config, "bus_only", StrictPolicy(), [6.0])

    assert result["success_count"] == 1
    assert result["bus_trips"] == 1
    assert_close(result["makespan"], 7.0, label="explicit first departure makespan")
    print("PASS: explicit first departure overrides assembly-time default")


def test_strict_departures_do_not_wait_for_late_arrivals():
    """STRICT should send an on-time partial bus and leave latecomers queued."""
    config = make_config(
        total=4,
        group_size=4,
        bus_route_time=5.0,
        dispatch_interval=10.0,
        fleet_size=2,
    )

    result = run_fixed(config, "bus_only", StrictPolicy(), [0.0, 0.0, 6.0, 6.0])

    assert result["success_count"] == 4, (
        f"expected all passengers delivered, got {result['success_count']}"
    )
    assert result["bus_trips"] == 2, (
        "STRICT should depart at t=0 with the two present passengers and "
        "carry the late arrivals on the next dispatch; "
        f"got {result['bus_trips']} bus trips"
    )
    assert_close(result["makespan"], 15.0, label="STRICT makespan")
    print("PASS: STRICT leaves late arrivals for a follow-up dispatch")


def test_fleet_delay_does_not_retroactively_board_late_arrivals():
    """Passengers who miss policy time should not board a later-delayed vehicle."""
    config = make_config(
        total=3,
        group_size=2,
        bus_route_time=100.0,
        dispatch_interval=10.0,
        fleet_size=1,
        turnaround=0.0,
        time_limit=500.0,
    )

    result = run_fixed(config, "bus_only", StrictPolicy(), [0.0, 5.0, 60.0])

    assert result["success_count"] == 3
    assert result["bus_trips"] == 3, (
        "the passenger arriving at t=60 missed the t=10 policy decision even "
        "though that vehicle physically departed later"
    )
    assert_close(result["makespan"], 300.0, label="fleet-delayed makespan")
    print("PASS: fleet delays do not retroactively change manifests")


def test_grace_waits_for_threshold_and_differs_from_strict():
    """GRACE should wait for the threshold when it is reached before max wait."""
    config = make_config(
        total=4,
        group_size=4,
        bus_route_time=5.0,
        dispatch_interval=10.0,
        fleet_size=2,
    )
    delays = [0.0, 0.0, 6.0, 6.0]

    strict = run_fixed(config, "bus_only", StrictPolicy(), delays)
    grace = run_fixed(config, "bus_only", GracePolicy(W=10.0, theta=1.0), delays)

    assert grace["success_count"] == 4, (
        f"expected all passengers delivered, got {grace['success_count']}"
    )
    assert grace["bus_trips"] == 1, (
        "GRACE should wait until all four passengers have arrived at t=6; "
        f"got {grace['bus_trips']} bus trips"
    )
    assert_close(grace["makespan"], 11.0, label="GRACE makespan")
    assert grace["bus_trips"] < strict["bus_trips"], (
        "STRICT and GRACE should produce different dispatch counts; "
        f"strict={strict['bus_trips']} grace={grace['bus_trips']}"
    )
    assert grace["makespan"] < strict["makespan"], (
        "Waiting for the threshold should beat the next scheduled STRICT bus here; "
        f"strict={strict['makespan']} grace={grace['makespan']}"
    )
    print("PASS: GRACE threshold behavior differs from STRICT")


def test_grace_max_wait_leaves_late_arrivals_for_next_dispatch():
    """GRACE should depart at max wait when the threshold is not reached."""
    config = make_config(
        total=4,
        group_size=4,
        bus_route_time=5.0,
        dispatch_interval=10.0,
        fleet_size=2,
    )

    result = run_fixed(
        config,
        "bus_only",
        GracePolicy(W=10.0, theta=1.0),
        [0.0, 0.0, 20.0, 20.0],
    )

    assert result["success_count"] == 4, (
        f"expected all passengers delivered, got {result['success_count']}"
    )
    assert result["bus_trips"] == 2, (
        "GRACE should depart at t=10 with early arrivals, then use a later "
        "dispatch for passengers who arrive after the max wait; "
        f"got {result['bus_trips']} bus trips"
    )
    assert_close(result["makespan"], 25.0, label="GRACE max-wait makespan")
    print("PASS: GRACE max wait leaves later arrivals queued")


def test_bus_fleet_allows_overlapping_trips():
    """A fleet larger than one should not serialize all bus trips."""
    config = make_config(
        total=4,
        group_size=2,
        bus_route_time=100.0,
        dispatch_interval=10.0,
        fleet_size=2,
        turnaround=100.0,
    )

    result = run_fixed(config, "bus_only", StrictPolicy(), [0.0, 0.0, 0.0, 0.0])

    assert result["success_count"] == 4, (
        f"expected all passengers delivered, got {result['success_count']}"
    )
    assert result["bus_trips"] == 2, (
        f"expected two bus trips, got {result['bus_trips']}"
    )
    assert_close(result["makespan"], 110.0, label="overlapping fleet makespan")
    print("PASS: bus fleet overlaps trips when multiple buses are available")


def test_rail_departures_keep_fixed_headway_while_trains_are_in_transit():
    """Rail headway should be independent of earlier trains still traveling."""
    config = make_config(
        total=6,
        group_size=6,
        shuttle_time=0.0,
        rail_time=100.0,
        rail_headway=10.0,
        rail_capacity=2,
        lastmile_time=0.0,
        time_limit=500.0,
    )

    result = run_fixed(config, "multimodal", StrictPolicy(), [0.0] * 6)

    assert result["success_count"] == 6, (
        f"expected all rail passengers delivered, got {result['success_count']}"
    )
    assert result["train_trips"] == 3, (
        f"expected three train trips, got {result['train_trips']}"
    )
    assert result["makespan"] <= 130.05, (
        "three capacity-two trains should depart near t=10, t=20, and t=30 "
        "even though the first train arrives near t=110; "
        f"got makespan {result['makespan']}"
    )
    print("PASS: rail dispatch keeps fixed headway during in-transit trains")


def test_explicit_rail_first_departure_is_honored():
    """Rail should honor the optional first-departure timetable override."""
    config = make_config(
        total=2,
        group_size=2,
        shuttle_time=0.0,
        rail_time=10.0,
        rail_headway=10.0,
        rail_capacity=2,
        rail_first_departure=50.0,
        lastmile_time=0.0,
        time_limit=200.0,
    )

    result = run_fixed(config, "multimodal", StrictPolicy(), [0.0, 0.0])

    assert result["success_count"] == 2
    assert result["train_trips"] == 1
    assert_close(result["makespan"], 60.0, label="explicit rail first departure")
    print("PASS: explicit rail first departure is honored")


def test_lastmile_fleet_capacity_and_turnaround_create_bottleneck():
    """Finite last-mile capacity and turnaround should delay downstream delivery."""
    config = make_config(
        total=4,
        group_size=2,
        shuttle_time=0.0,
        rail_time=0.0,
        rail_headway=10.0,
        rail_capacity=4,
        lastmile_time=100.0,
        dispatch_interval=10.0,
        fleet_size=2,
        lastmile_fleet_size=1,
        lastmile_turnaround=100.0,
        time_limit=500.0,
    )

    result = run_fixed(config, "multimodal", StrictPolicy(), [0.0] * 4)

    assert result["success_count"] == 4
    assert result["train_trips"] == 1
    assert_close(result["makespan"], 310.0, label="last-mile bottleneck makespan")
    assert_close(result["lastmile_minutes"], 200.0, label="last-mile vehicle minutes")
    print("PASS: finite last-mile fleet creates a measurable bottleneck")


def test_censoring_penalty_prevents_failed_scenario_from_looking_better():
    """Censored scenarios need explicit completion and penalized KPIs."""
    censored_config = make_config(
        total=4,
        group_size=2,
        bus_route_time=100.0,
        dispatch_interval=10.0,
        fleet_size=1,
        turnaround=100.0,
        time_limit=150.0,
    )
    complete_config = make_config(
        total=4,
        group_size=2,
        bus_route_time=100.0,
        dispatch_interval=10.0,
        fleet_size=1,
        turnaround=100.0,
        time_limit=500.0,
    )

    delays = [0.0, 0.0, 0.0, 0.0]
    censored = run_fixed(censored_config, "bus_only", StrictPolicy(), delays)
    complete = run_fixed(complete_config, "bus_only", StrictPolicy(), delays)

    assert censored["success_count"] == 2, (
        f"expected two delivered passengers before the limit, got {censored['success_count']}"
    )
    assert censored["leftover_count"] == 2, (
        f"expected two censored passengers, got {censored['leftover_count']}"
    )
    for key in ("censored_count", "completion_rate", "penalized_makespan"):
        assert key in censored, f"missing explicit censoring KPI: {key}"
    assert censored["censored_count"] == 2
    assert_close(censored["completion_rate"], 0.5, label="completion rate")
    assert censored["penalized_makespan"] > complete["makespan"], (
        "a partially delivered run must not rank better than the complete run"
    )
    assert censored["penalized_makespan"] > censored["makespan"], (
        "penalized makespan should expose the cost of undelivered personnel"
    )
    print("PASS: censoring exposes incomplete delivery in penalized KPIs")


TESTS = [
    test_origin_schedule_defaults_to_assembly_time,
    test_origin_schedule_accepts_explicit_first_departure,
    test_strict_departures_do_not_wait_for_late_arrivals,
    test_fleet_delay_does_not_retroactively_board_late_arrivals,
    test_grace_waits_for_threshold_and_differs_from_strict,
    test_grace_max_wait_leaves_late_arrivals_for_next_dispatch,
    test_bus_fleet_allows_overlapping_trips,
    test_rail_departures_keep_fixed_headway_while_trains_are_in_transit,
    test_explicit_rail_first_departure_is_honored,
    test_lastmile_fleet_capacity_and_turnaround_create_bottleneck,
    test_censoring_penalty_prevents_failed_scenario_from_looking_better,
]


if __name__ == "__main__":
    failures = []
    for test in TESTS:
        try:
            test()
        except AssertionError as exc:
            failures.append((test.__name__, str(exc)))
            print(f"FAIL: {test.__name__}: {exc}")
        except Exception as exc:
            failures.append((test.__name__, f"{type(exc).__name__}: {exc}"))
            print(f"ERROR: {test.__name__}: {type(exc).__name__}: {exc}")

    if failures:
        print("\n=== SCENARIO TEST FAILURES ===")
        for name, message in failures:
            print(f"- {name}: {message}")
        raise SystemExit(1)

    print("\n=== ALL SCENARIO TESTS PASSED ===")
