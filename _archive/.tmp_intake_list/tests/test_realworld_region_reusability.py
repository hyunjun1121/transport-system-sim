"""Region reusability checks using a second synthetic fixture file."""

from __future__ import annotations

import os
from pathlib import Path
import sys

import networkx as nx
import yaml

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.adapter import build_simulator_graph, realworld_network_config  # noqa: E402
from src.realworld.regions import load_region_spec  # noqa: E402
from src.realworld.validation import assert_graph_ready  # noqa: E402


FIXTURE_PATH = (
    Path(__file__).resolve().parent / "fixtures" / "synthetic_region_fixture.yaml"
)


def test_second_synthetic_region_fixture_loads_and_adapts() -> None:
    """A non-pilot region fixture should pass schema and adapter checks."""

    with FIXTURE_PATH.open("r", encoding="utf-8") as handle:
        raw_region = yaml.safe_load(handle)

    region = load_region_spec(raw_region)
    graph = build_simulator_graph(_synthetic_osm_like_graph(), region)
    assert_graph_ready(graph, required_nodes=region.simulator_node_ids)
    network_config = realworld_network_config(region)

    assert region.region_id == "synthetic_region_fixture"
    assert region.metadata["coordinate_policy"] == "synthetic_fixture_only"
    assert graph.graph["region_id"] == "synthetic_region_fixture"
    assert graph.graph["source_node_count"] == 4
    assert graph.graph["routeable_source_edge_count"] == 4
    assert nx.has_path(graph, "A", "D")
    assert nx.has_path(graph, "A", "S")
    assert nx.has_path(graph, "R", "D")
    assert network_config["nodes"] == ["A", "D", "S", "R"]
    assert network_config["rail_link"] == [("S", "R", 18.0, 9.0, 240)]

    print("PASS: second synthetic region fixture loads and adapts")


def _synthetic_osm_like_graph() -> nx.MultiDiGraph:
    """Return a routeable non-pilot OSM-like graph for the fixture region."""

    graph = nx.MultiDiGraph()
    graph.add_node(101, x=127.005, y=37.005)
    graph.add_node(102, x=127.015, y=37.010)
    graph.add_node(103, x=127.025, y=37.020)
    graph.add_node(104, x=127.035, y=37.030)
    graph.add_edge(
        101,
        102,
        key=0,
        osmid="synthetic-101-102",
        highway="primary",
        maxspeed=45,
        length=1_200,
    )
    graph.add_edge(
        102,
        103,
        key=0,
        osmid="synthetic-102-103",
        highway="secondary",
        maxspeed=40,
        length=1_500,
    )
    graph.add_edge(
        103,
        104,
        key=0,
        osmid="synthetic-103-104",
        highway="tertiary",
        maxspeed=35,
        length=1_000,
    )
    graph.add_edge(
        104,
        103,
        key=0,
        osmid="synthetic-104-103",
        highway="tertiary",
        maxspeed=35,
        length=1_000,
    )
    return graph


if __name__ == "__main__":
    test_second_synthetic_region_fixture_loads_and_adapts()
    print("\n=== REALWORLD REGION REUSABILITY TESTS PASSED ===")
