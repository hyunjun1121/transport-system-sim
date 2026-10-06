"""Deterministic DES verification suite with hand-computed event times.

Each case runs ``run_scenario`` on a tiny synthetic graph with fixed arrivals
and asserts analytically derived makespan/completion/KPI values.  This is
implementation verification (the event engine reproduces known answers), not
campaign output: it guards dispatch, turnaround, reverse empty return,
stranding, strict late-arrival boarding, rail-state transition, and the BPR
no-op used by the paper's wartime assumption A2.

Run directly with::

    .\\.venv\\Scripts\\python tests\\test_verification_suite.py
"""

import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import scenario as scenario_module
from src.network import build_network
from src.policies import StrictPolicy
from tests.test_scenario import (
    HIGH_CAPACITY,
    PARAMS,
    fixed_stochastic_inputs,
    make_config,
)


def run_case(config, scenario_type, delays, extra_edges=()):
    """Run one deterministic case with extended KPIs enabled."""
    config = copy.deepcopy(config)
    config.setdefault("metrics", {})["include_extended"] = True
    graph = build_network(config)
    for source, target, free_flow in extra_edges:
        graph.add_edge(
            source,
            target,
            t0=free_flow,
            capacity=HIGH_CAPACITY,
            p_fail=0.0,
            mode="road",
        )
    with fixed_stochastic_inputs(delays):
        return scenario_module.run_scenario(
            G=graph,
            config=config,
            scenario_type=scenario_type,
            policy=StrictPolicy(),
            params=PARAMS,
            seed=123,
        )


def assert_close(actual, expected, tolerance=1e-9, label="value"):
    assert abs(actual - expected) <= tolerance, (
        f"{label}: expected {expected}, got {actual}"
    )


def test_single_vehicle_single_batch_matches_t0():
    """V1: 45 pax, one 10-min edge, depart t=0 -> makespan exactly 10."""
    out = run_case(
        make_config(
            45, 45,
            bus_route_time=10.0,
            dispatch_interval=10.0,
            fleet_size=1,
            turnaround=0.0,
            return_strategy="reverse_network",
        ),
        "bus_only",
        [0.0] * 45,
    )
    assert_close(out["makespan"], 10.0, label="V1 makespan")
    assert_close(out["completion_rate"], 1.0, label="V1 completion")
    assert out["bus_trips"] == 1
    assert out["empty_return_trips"] == 0
    assert_close(out["empty_return_minutes"], 0.0, label="V1 empty minutes")
    print("PASS: V1 single trip reproduces edge free-flow time")


def test_turnaround_and_empty_return_gate_reuse():
    """V2: 90 pax, 1 vehicle, 10-min legs, turnaround 5.

    Trip 1 departs 0, arrives 10; empty return 10->20 plus turnaround 5 makes
    the vehicle available at 25; it departs immediately with the waiting
    manifest and arrives at 35.  Two loaded trips and two 10-min empties.
    """
    out = run_case(
        make_config(
            90, 45,
            bus_route_time=10.0,
            dispatch_interval=10.0,
            fleet_size=1,
            turnaround=5.0,
            return_strategy="reverse_network",
        ),
        "bus_only",
        [0.0] * 90,
        extra_edges=[("D", "A", 10.0)],
    )
    assert_close(out["makespan"], 35.0, label="V2 makespan")
    assert_close(out["completion_rate"], 1.0, label="V2 completion")
    assert out["bus_trips"] == 2
    assert out["empty_return_trips"] == 2
    assert_close(out["empty_return_minutes"], 20.0, label="V2 empty minutes")
    assert out["road_vehicle_cycles"] == 2
    print("PASS: V2 reuse gated by empty return plus turnaround")


def test_disconnected_reverse_path_strands_vehicle():
    """V3: same as V2 but the D->A reverse edge is absent.

    The vehicle cannot return and is never teleported: the second batch is
    never delivered (completion 0.5), no empty trip is logged, and only the
    first 10-min trip exists.
    """
    out = run_case(
        make_config(
            90, 45,
            bus_route_time=10.0,
            dispatch_interval=10.0,
            fleet_size=1,
            turnaround=5.0,
            return_strategy="reverse_network",
        ),
        "bus_only",
        [0.0] * 90,
    )
    assert_close(out["makespan"], 10.0, label="V3 makespan")
    assert_close(out["completion_rate"], 0.5, label="V3 completion")
    assert out["bus_trips"] == 1
    assert out["empty_return_trips"] == 0
    assert_close(out["empty_return_minutes"], 0.0, label="V3 empty minutes")
    print("PASS: V3 disconnected reverse strands the vehicle without teleport")


def test_strict_dispatch_boards_late_arrivals_on_later_manifest():
    """V4: second batch arrives at t=10 and waits for the reused vehicle.

    Trip 1 departs 0 with batch 1 and returns empty by 20 (turnaround 0);
    batch 2 (arrived at 10) boards the 20 departure and arrives at 30.
    The late batch never delays the first manifest.
    """
    out = run_case(
        make_config(
            90, 45,
            bus_route_time=10.0,
            dispatch_interval=10.0,
            fleet_size=1,
            turnaround=0.0,
            return_strategy="reverse_network",
        ),
        "bus_only",
        [0.0] * 45 + [10.0] * 45,
        extra_edges=[("D", "A", 10.0)],
    )
    assert_close(out["makespan"], 30.0, label="V4 makespan")
    assert_close(out["completion_rate"], 1.0, label="V4 completion")
    assert out["bus_trips"] == 2
    print("PASS: V4 strict dispatch boards late arrivals without delaying manifests")


def test_rail_state_transition_available_vs_unavailable():
    """V5: identical multimodal itinerary under available vs unavailable rail.

    Available: shuttle 0->1, rail departs 10 and arrives 30 (20-min leg),
    last mile 30->31, so makespan 31 with one train trip.  Unavailable: the
    S->R leg is removed, the shuttle still runs once, no train departs, and
    completion is 0.
    """
    available = make_config(
        45, 45,
        shuttle_time=1.0,
        rail_time=20.0,
        rail_headway=10.0,
        rail_capacity=100,
        lastmile_time=1.0,
        dispatch_interval=10.0,
        fleet_size=1,
        turnaround=0.0,
    )
    out = run_case(available, "multimodal", [0.0] * 45)
    assert_close(out["makespan"], 31.0, label="V5 available makespan")
    assert_close(out["completion_rate"], 1.0, label="V5 available completion")
    assert out["bus_trips"] == 1
    assert out["train_trips"] == 1

    unavailable = copy.deepcopy(available)
    unavailable["multimodal"]["rail_status"] = "unavailable"
    out = run_case(unavailable, "multimodal", [0.0] * 45)
    assert_close(out["completion_rate"], 0.0, label="V5 unavailable completion")
    assert out["train_trips"] == 0
    assert out["bus_trips"] == 1
    print("PASS: V5 rail unavailability removes the leg instead of slowing it")


def test_bpr_term_is_identity_at_zero_volume():
    """V6: BPR with alpha=0.36/beta=4.0 at zero background volume.

    V/C = 0 gives t = t0 exactly, so the run reproduces the V1 makespan of
    10 min.  This is the mechanism behind wartime assumption A2: at the
    100 veh/h planning input relative to class capacities, the BPR term is
    near 1 by construction and disruption effects enter elsewhere.
    """
    config = make_config(
        45, 45,
        bus_route_time=10.0,
        dispatch_interval=10.0,
        fleet_size=1,
        turnaround=0.0,
        return_strategy="reverse_network",
    )
    config["bpr"] = {"alpha": 0.36, "beta": 4.0}
    config["traffic"] = {"volume_window_min": 60.0, "background_volume": 0.0}
    out = run_case(config, "bus_only", [0.0] * 45)
    assert_close(out["makespan"], 10.0, label="V6 makespan")
    assert_close(out["completion_rate"], 1.0, label="V6 completion")
    print("PASS: V6 BPR term is identity at zero volume")


TESTS = [
    test_single_vehicle_single_batch_matches_t0,
    test_turnaround_and_empty_return_gate_reuse,
    test_disconnected_reverse_path_strands_vehicle,
    test_strict_dispatch_boards_late_arrivals_on_later_manifest,
    test_rail_state_transition_available_vs_unavailable,
    test_bpr_term_is_identity_at_zero_volume,
]


if __name__ == "__main__":
    for test in TESTS:
        test()
    print("\n=== ALL VERIFICATION SUITE TESTS PASSED ===")
