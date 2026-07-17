"""Synthetic end-to-end smoke tests for the real-world graph path."""

from contextlib import contextmanager
import os
import sys

import networkx as nx
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import scenario as scenario_module
from src.policies import StrictPolicy
from src.realworld.adapter import build_simulator_graph, realworld_network_config
from src.realworld.validation import assert_graph_ready
from src.sim_types import EdgeDisruption


PARAMS = {"s": 1.0, "p_fail_scale": 0.0, "sigma": 0.0}


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


def minimal_region_dict() -> dict:
    """Return a canonical region spec for the synthetic smoke test."""

    return {
        "region_id": "smoke_fixture",
        "name": "Smoke Fixture",
        "boundary": {
            "type": "bbox",
            "north": 37.53,
            "south": 37.49,
            "east": 127.14,
            "west": 127.08,
        },
        "assembly_zones": [{"id": "A", "lat": 37.5001, "lon": 127.1001}],
        "destination_zones": [{"id": "D", "lat": 37.5201, "lon": 127.1301}],
        "rail": {
            "access": {"id": "S", "lat": 37.5051, "lon": 127.1101},
            "egress": {"id": "R", "lat": 37.5151, "lon": 127.1201},
            "travel_time_min": 20,
            "headway_min": 10,
            "capacity_pax_per_train": 10,
        },
    }


def synthetic_osm_like_graph() -> nx.MultiDiGraph:
    """Build an offline OSM-like graph routeable through all required legs."""

    graph = nx.MultiDiGraph()
    graph.add_node(1, x=127.1000, y=37.5000)
    graph.add_node(2, x=127.1100, y=37.5050)
    graph.add_node(3, x=127.1200, y=37.5150)
    graph.add_node(4, x=127.1300, y=37.5200)

    graph.add_edge(
        1,
        2,
        key=0,
        osmid="12",
        highway="primary",
        maxspeed=60,
        length=1_000,
        base_p_fail=0.0,
    )
    graph.add_edge(
        2,
        3,
        key=0,
        osmid="23",
        highway="secondary",
        maxspeed=50,
        length=1_000,
        base_p_fail=0.0,
    )
    graph.add_edge(
        3,
        4,
        key=0,
        osmid="34",
        highway="secondary",
        maxspeed=50,
        length=1_000,
        base_p_fail=0.0,
    )
    graph.add_edge(
        4,
        3,
        key=0,
        osmid="43",
        highway="secondary",
        maxspeed=50,
        length=1_000,
        base_p_fail=0.0,
    )
    return graph


def make_smoke_config(region: dict) -> dict:
    """Return a minimal config compatible with run_scenario and the adapter graph."""

    network = realworld_network_config(region)
    return {
        "network": {
            "nodes": network["nodes"],
            "rail_link": network["rail_link"],
            "road_links": [],
        },
        "personnel": {
            "total": 4,
            "group_size": 4,
            "assembly_time": 0.0,
        },
        "bus": {
            "first_departure_min": 0.0,
            "dispatch_interval_min": 5.0,
            "fleet_size": 2,
            "turnaround_min": 0.0,
        },
        "multimodal": {
            "shuttle_first_departure_min": 0.0,
            "shuttle_dispatch_interval_min": 5.0,
            "shuttle_fleet_size": 2,
            "shuttle_turnaround_min": 0.0,
            "transfer_time_min": 0.0,
            "transfer_per_passenger_min": 0.0,
            "rail_first_departure_min": 0.0,
            "lastmile_first_departure_min": 0.0,
            "lastmile_dispatch_interval_min": 0.0,
            "lastmile_fleet_size": 2,
            "lastmile_turnaround_min": 0.0,
            "lastmile_vehicle_capacity": 4,
        },
        "traffic": {
            "volume_window_min": 60.0,
            "background_volume": 0.0,
        },
        "failure": {
            "mode": "blocked",
            "capacity_reduction_factor": 1.0,
        },
        "metrics": {
            "late_penalty_min": 300.0,
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
            "time_limit": 300.0,
        },
    }


def run_fixed(graph: nx.DiGraph, config: dict, scenario_type: str) -> dict:
    """Run one deterministic scenario through the public scenario API."""

    with fixed_stochastic_inputs([0.0, 0.0, 0.0, 0.0]):
        return scenario_module.run_scenario(
            G=graph,
            config=config,
            scenario_type=scenario_type,
            policy=StrictPolicy(),
            params=PARAMS,
            seed=123,
        )


def test_synthetic_realworld_graph_runs_bus_only_and_multimodal() -> None:
    """A synthetic OSM-like graph should reach run_scenario with both modes."""

    region = minimal_region_dict()
    graph = build_simulator_graph(synthetic_osm_like_graph(), region)
    assert_graph_ready(graph)
    config = make_smoke_config(region)

    bus_only = run_fixed(graph, config, "bus_only")
    multimodal = run_fixed(graph, config, "multimodal")

    assert bus_only["success_count"] == 4
    assert bus_only["completion_rate"] == 1.0
    assert bus_only["bus_trips"] >= 1
    assert multimodal["success_count"] == 4
    assert multimodal["completion_rate"] == 1.0
    assert multimodal["train_trips"] == 1
    assert multimodal["lastmile_minutes"] > 0.0

    print("PASS: synthetic real-world graph runs bus-only and multimodal scenarios")


if __name__ == "__main__":
    test_synthetic_realworld_graph_runs_bus_only_and_multimodal()
    print("\n=== REALWORLD END-TO-END SMOKE TESTS PASSED ===")
