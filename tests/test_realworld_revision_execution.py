"""Direct integration tests for one revision campaign condition."""

from __future__ import annotations

from pathlib import Path
import sys

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.revision_execution import (
    PreparedDisruption,
    execute_condition,
)
from src.realworld.revision_planner import PlannedCondition


def _graph() -> nx.DiGraph:
    graph = nx.DiGraph()
    for u, v, t0 in (
        ("A", "D", 10.0),
        ("D", "A", 10.0),
        ("A", "S", 2.0),
        ("S", "A", 2.0),
        ("R", "D", 2.0),
        ("D", "R", 2.0),
    ):
        graph.add_edge(
            u,
            v,
            mode="road",
            t0=t0,
            capacity=1_000_000.0,
            p_fail=0.0,
            realworld_edge_id=f"{u}-{v}",
        )
    return graph


def _config() -> dict:
    return {
        "network": {
            "nodes": ["A", "S", "R", "D"],
            "road_links": [],
            "rail_link": [["S", "R", 5.0, 5.0, 100]],
        },
        "personnel": {"total": 4, "group_size": 2, "assembly_time": 0.0},
        "bus": {
            "first_departure_min": 0.0,
            "dispatch_interval_min": 1.0,
            "fleet_size": 2,
            "turnaround_min": 0.0,
        },
        "multimodal": {
            "shuttle_first_departure_min": 0.0,
            "shuttle_dispatch_interval_min": 1.0,
            "shuttle_fleet_size": 2,
            "shuttle_turnaround_min": 0.0,
            "transfer_time_min": 0.0,
            "transfer_per_passenger_min": 0.0,
            "rail_first_departure_min": 0.0,
            "lastmile_first_departure_min": 0.0,
            "lastmile_dispatch_interval_min": 1.0,
            "lastmile_fleet_size": 2,
            "lastmile_turnaround_min": 0.0,
            "lastmile_vehicle_capacity": 2,
        },
        "traffic": {"volume_window_min": 60.0, "background_volume": 0.0},
        "failure": {"mode": "none", "capacity_reduction_factor": 1.0},
        "metrics": {"late_penalty_min": 60.0},
        "bpr": {"alpha": 0.0, "beta": 4.0},
        "lateness": {
            "distribution": "fixture",
            "mu": 0.0,
            "sigma_levels": [0.0],
        },
        "experiment": {"R": 1, "seed_base": 1, "time_limit": 60.0},
        "stochastic": {"road_noise_sigma": 0.0, "turnaround_noise_lambda": 0.0},
    }


def _condition(policy_id: str, rail_status: str = "available") -> PlannedCondition:
    multiplier = None if rail_status == "unavailable" else 1.0
    return PlannedCondition(
        campaign_id="paired_reanalysis",
        configuration_id="0123456789abcdef",
        policy_id=policy_id,
        resource_frame="matched_road_fleet",
        graph_scope="top3",
        corridor_path_count=3,
        arrival_seed=3101,
        threat_seed=None,
        threat_draw=None,
        rail_status=rail_status,
        rail_multiplier=multiplier,
        scenario_id="no_disruption",
        parameters={
            "departure_policy_id": "strict",
            "return_strategy": "reverse_network",
            "demand": 4,
            "road_fleet_total": 4,
        },
    )


def test_execute_condition_emits_complete_provenance_and_extended_metrics():
    row = execute_condition(
        _graph(),
        _config(),
        _condition("bus_only"),
        disruption=PreparedDisruption.none(),
    )

    assert row["campaign_id"] == "paired_reanalysis"
    assert row["configuration_id"] == "0123456789abcdef"
    assert row["policy_id"] == "bus_only"
    assert row["arrival_seed"] == 3101
    assert row["return_strategy"] == "reverse_network"
    assert row["completion_rate"] == 1.0
    assert row["empty_return_trips"] == 2
    assert row["selected_edge_count"] == 0
    assert len(row["selected_edges_checksum"]) == 64
    assert row["direct_bus_count"] == 4
    assert row["feeder_shuttle_count"] == 0
    assert row["last_mile_bus_count"] == 0
    assert row["fallback_bus_count"] == 0
    assert row["total_road_vehicle_count"] == 4
    assert row["train_capacity"] == 0
    assert row["road_vehicle_cycles"] == 2
    assert row["road_deployed_seat_capacity"] == 4
    assert row["road_boarded_passengers"] == 4
    assert row["road_mean_vehicle_load_factor"] == 1.0
    assert row["rail_deployed_seat_capacity"] == 0
    assert row["rail_boarded_passengers"] == 0
    assert row["rail_mean_load_factor"] == 0.0
    print("PASS: one condition emits provenance and extended metrics")


def test_execute_condition_records_multimodal_and_fallback_allocations():
    static_row = execute_condition(
        _graph(),
        _config(),
        _condition("static_multimodal"),
        disruption=PreparedDisruption.none(),
    )
    fallback_row = execute_condition(
        _graph(),
        _config(),
        _condition("station_fallback_30"),
        disruption=PreparedDisruption.none(),
    )

    assert static_row["direct_bus_count"] == 0
    assert static_row["feeder_shuttle_count"] == 2
    assert static_row["last_mile_bus_count"] == 2
    assert static_row["fallback_bus_count"] == 0
    assert static_row["total_road_vehicle_count"] == 4
    assert static_row["train_capacity"] == 100
    assert static_row["road_deployed_seat_capacity"] == 8
    assert static_row["road_boarded_passengers"] == 8
    assert static_row["rail_deployed_seat_capacity"] == 100
    assert static_row["rail_boarded_passengers"] == 4
    assert static_row["rail_mean_load_factor"] == 0.04

    assert fallback_row["direct_bus_count"] == 0
    assert fallback_row["feeder_shuttle_count"] == 2
    assert fallback_row["last_mile_bus_count"] == 1
    assert fallback_row["fallback_bus_count"] == 1
    assert fallback_row["total_road_vehicle_count"] == 4
    assert fallback_row["train_capacity"] == 100
    print("PASS: execution records actual road and rail allocation")


def test_precheck_switch_uses_road_branch_when_rail_is_unavailable():
    row = execute_condition(
        _graph(),
        _config(),
        _condition("precheck_switch", rail_status="unavailable"),
        disruption=PreparedDisruption.none(),
    )

    assert row["executed_mode"] == "bus_only"
    assert row["completion_rate"] == 1.0
    assert row["train_trips"] == 0
    print("PASS: precheck switch uses road branch")


def test_forced_blockage_is_applied_without_graph_mutation():
    graph = _graph()
    row = execute_condition(
        graph,
        _config(),
        _condition("bus_only"),
        disruption=PreparedDisruption(
            edges=(("A", "D"),),
            mode="blocked",
            capacity_factor=0.0,
            travel_time_multiplier=1.0,
        ),
    )

    assert graph.edges["A", "D"]["p_fail"] == 0.0
    assert row["completion_rate"] == 0.0
    assert row["selected_edge_count"] == 1
    assert row["makespan"] is None
    print("PASS: sparse blockage leaves graph unchanged")


def test_morris_rail_factor_changes_effective_state_and_travel_time():
    baseline = execute_condition(
        _graph(),
        _config(),
        _condition("static_multimodal"),
        disruption=PreparedDisruption.none(),
    )
    condition = PlannedCondition(
        campaign_id="morris",
        configuration_id="fedcba9876543210",
        policy_id="static_multimodal",
        resource_frame="matched_road_fleet",
        graph_scope="top3",
        corridor_path_count=3,
        arrival_seed=3101,
        threat_seed=None,
        threat_draw=None,
        rail_status="available",
        rail_multiplier=1.0,
        scenario_id="morris_screening",
        parameters={
            "departure_policy_id": "strict",
            "return_strategy": "reverse_network",
            "factor_values": {
                "road_longhaul_multiplier": 1.0,
                "rail_travel_multiplier": 2.0,
                "demand": 4.0,
                "road_fleet_total": 4.0,
                "transfer_time_min": 0.0,
                "arrival_sigma": 0.0,
            },
        },
    )
    degraded = execute_condition(
        _graph(),
        _config(),
        condition,
        disruption=PreparedDisruption.none(),
    )

    assert degraded["rail_status"] == "degraded"
    assert degraded["rail_multiplier"] == 2.0
    assert degraded["makespan"] == baseline["makespan"] + 5.0
    print("PASS: Morris rail factor changes effective service")


if __name__ == "__main__":
    test_execute_condition_emits_complete_provenance_and_extended_metrics()
    test_execute_condition_records_multimodal_and_fallback_allocations()
    test_precheck_switch_uses_road_branch_when_rail_is_unavailable()
    test_forced_blockage_is_applied_without_graph_mutation()
    test_morris_rail_factor_changes_effective_state_and_travel_time()
    print("\n=== REVISION EXECUTION TESTS PASSED ===")
