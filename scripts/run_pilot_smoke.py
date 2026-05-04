"""Run an offline pilot-region smoke scenario from cached inputs."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import sys
from typing import Any

import networkx as nx
import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import scenario as scenario_module
from src.policies import StrictPolicy
from src.realworld import (
    assert_graph_ready,
    build_simulator_graph,
    load_graphml,
    realworld_network_config,
)
from src.sim_types import EdgeDisruption


DEFAULT_REGION_PATH = ROOT / "data" / "regions" / "pilot_region.yaml"
DEFAULT_CACHE_PATH = ROOT / "data" / "cache" / "pilot_region_road.graphml"
PARAMS = {"s": 1.0, "p_fail_scale": 0.0, "sigma": 0.0}


def main() -> None:
    result = run_pilot_smoke(DEFAULT_REGION_PATH, DEFAULT_CACHE_PATH)
    print(result)


def run_pilot_smoke(region_path: str | Path, cache_path: str | Path) -> dict[str, Any]:
    """Load cached pilot inputs and run deterministic bus/multimodal smoke."""

    region = _load_yaml(Path(region_path))
    road_graph = load_graphml(cache_path, normalize=True)
    simulator_graph = build_simulator_graph(road_graph, region)
    assert_graph_ready(simulator_graph)
    config = make_smoke_config(region)

    with fixed_stochastic_inputs([0.0, 0.0, 0.0, 0.0]):
        bus = scenario_module.run_scenario(
            G=simulator_graph,
            config=config,
            scenario_type="bus_only",
            policy=StrictPolicy(),
            params=PARAMS,
            seed=123,
        )
        multimodal = scenario_module.run_scenario(
            G=simulator_graph,
            config=config,
            scenario_type="multimodal",
            policy=StrictPolicy(),
            params=PARAMS,
            seed=123,
        )
    return {
        "region_id": region["region_id"],
        "graph_nodes": simulator_graph.number_of_nodes(),
        "graph_edges": simulator_graph.number_of_edges(),
        "bus_success_count": bus["success_count"],
        "multimodal_success_count": multimodal["success_count"],
        "bus_completion_rate": bus["completion_rate"],
        "multimodal_completion_rate": multimodal["completion_rate"],
        "multimodal_train_trips": multimodal["train_trips"],
    }


def make_smoke_config(region: dict[str, Any]) -> dict[str, Any]:
    """Return a minimal scenario config for pilot smoke validation."""

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

    def sample_no_disruptions(G: nx.DiGraph, p_fail_scale, rng, **kwargs):
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


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


if __name__ == "__main__":
    main()
