"""Direct tests for paper-revision campaign runner helpers."""

from __future__ import annotations

import copy
from pathlib import Path
import sys
import tempfile

import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.revision_runner import (
    apply_forced_failure_config,
    apply_revision_config,
    build_configuration_id,
    selected_edges_checksum,
    select_seeded_random_edges,
    write_campaign_csv,
)


def _base_config() -> dict:
    return {
        "personnel": {"total": 1000, "group_size": 45, "assembly_time": 0.0},
        "bus": {"fleet_size": 23},
        "multimodal": {
            "shuttle_fleet_size": 23,
            "lastmile_fleet_size": 23,
        },
        "metrics": {"late_penalty_min": 300.0},
        "fleet": {"return_strategy": "legacy_none"},
    }


def _graph() -> nx.DiGraph:
    graph = nx.DiGraph()
    for index in range(12):
        graph.add_edge(
            f"n{index}",
            f"n{index + 1}",
            mode="road",
            realworld_edge_id=f"edge-{index:02d}",
            t0=1.0,
            capacity=100.0,
            p_fail=0.0,
        )
    graph.add_edge("rail-a", "rail-b", mode="rail", realworld_edge_id="rail")
    graph.add_edge(
        "A",
        "n0",
        mode="road",
        source="connector",
        highway="connector",
        realworld_edge_id="connector-A",
    )
    return graph


def test_configuration_identity_and_edge_checksum_are_canonical():
    first = build_configuration_id({"b": 2, "a": [1, 3]})
    second = build_configuration_id({"a": [1, 3], "b": 2})
    changed = build_configuration_id({"a": [1, 4], "b": 2})
    assert first == second
    assert first != changed

    edges_a = (("z", "a"), ("a", "b"))
    edges_b = tuple(reversed(edges_a))
    assert selected_edges_checksum(edges_a) == selected_edges_checksum(edges_b)
    assert len(selected_edges_checksum(edges_a)) == 64
    print("PASS: canonical configuration and edge identities")


def test_revision_config_preserves_input_and_applies_resource_frames():
    base = _base_config()
    original = copy.deepcopy(base)

    configured = apply_revision_config(
        base,
        policy_id="static_multimodal",
        resource_frame="configured_bundle",
        demand=1500,
        return_strategy="reverse_network",
        rail_status="degraded",
        rail_multiplier=1.5,
    )
    matched = apply_revision_config(
        base,
        policy_id="static_multimodal",
        resource_frame="matched_road_fleet",
        demand=1000,
        road_fleet_total=15,
    )

    assert base == original
    assert configured["personnel"]["total"] == 1500
    assert configured["multimodal"]["shuttle_fleet_size"] == 23
    assert configured["multimodal"]["lastmile_fleet_size"] == 23
    assert configured["fleet"]["return_strategy"] == "reverse_network"
    assert configured["metrics"]["include_extended"] is True
    assert configured["multimodal"]["rail_status"] == "degraded"
    assert configured["multimodal"]["rail_degradation_multiplier"] == 1.5
    assert configured["failure"]["rerouting"]["cache_departure_path"] is True
    assert matched["multimodal"]["shuttle_fleet_size"] == 8
    assert matched["multimodal"]["lastmile_fleet_size"] == 7

    fallback = apply_revision_config(
        base,
        policy_id="station_fallback_30",
        resource_frame="matched_road_fleet",
        demand=1000,
    )
    assert fallback["multimodal"]["shuttle_fleet_size"] == 8
    assert fallback["multimodal"]["lastmile_fleet_size"] == 8
    assert fallback["adaptation"]["fallback_fleet_size"] == 7
    print("PASS: revision config resource frames")


def test_seeded_random_edges_are_reproducible_and_road_only():
    graph = _graph()
    first = select_seeded_random_edges(graph, count=4, seed=5101)
    repeat = select_seeded_random_edges(graph, count=4, seed=5101)
    other = select_seeded_random_edges(graph, count=4, seed=5102)

    assert first == repeat
    assert first != other
    assert len(first) == 4
    assert all(graph.edges[edge]["mode"] == "road" for edge in first)
    print("PASS: seeded random road edges")


def test_seeded_random_edges_exclude_synthetic_connectors():
    graph = _graph()
    graph.add_edge(
        "synthetic-zero",
        "synthetic-zero-target",
        mode="road",
        length_m=0.0,
        realworld_edge_id="synthetic-zero-length",
    )
    selected = select_seeded_random_edges(graph, count=12, seed=5101)

    assert len(selected) == 12
    assert ("A", "n0") not in selected
    assert ("synthetic-zero", "synthetic-zero-target") not in selected
    assert all(
        graph.edges[edge].get("source") != "connector"
        and graph.edges[edge].get("highway") != "connector"
        for edge in selected
    )
    try:
        select_seeded_random_edges(graph, count=13, seed=5101)
    except ValueError as exc:
        assert "available road edges=12" in str(exc)
    else:
        raise AssertionError("synthetic connector counted as random damage candidate")
    print("PASS: random threat excludes synthetic connectors")


def test_forced_failure_config_is_sparse_and_nonmutating():
    base = _base_config()
    edges = (("n1", "n2"), ("n3", "n4"))
    configured = apply_forced_failure_config(
        base,
        edges=edges,
        mode="capacity_reduction",
        capacity_factor=1.0,
        travel_time_multiplier=1.5,
    )

    assert "failure" not in base
    assert configured["failure"]["forced_edges"] == [
        ["n1", "n2"],
        ["n3", "n4"],
    ]
    assert configured["failure"]["mode"] == "capacity_reduction"
    assert configured["failure"]["capacity_reduction_factor"] == 1.0
    assert configured["failure"]["road_travel_time_multiplier"] == 1.5
    print("PASS: sparse forced failure config")


def test_campaign_csv_has_stable_union_schema_and_rejects_canonical_tree():
    rows = [
        {"run_key": "a", "policy_id": "bus_only", "makespan": 10.0},
        {"run_key": "b", "policy_id": "static_multimodal", "completion_rate": 1.0},
    ]
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "rows.csv"
        written = write_campaign_csv(path, rows)
        text = written.read_text(encoding="utf-8-sig")
        header = text.splitlines()[0]
        assert header == "run_key,policy_id,makespan,completion_rate"
        assert len(text.splitlines()) == 3

    canonical = ROOT / "results" / "realworld_pilot_nodelink" / "forbidden.csv"
    try:
        write_campaign_csv(canonical, rows)
    except ValueError:
        pass
    else:
        raise AssertionError("canonical output tree must remain read-only")
    print("PASS: stable isolated campaign CSV")


TESTS = [
    test_configuration_identity_and_edge_checksum_are_canonical,
    test_revision_config_preserves_input_and_applies_resource_frames,
    test_seeded_random_edges_are_reproducible_and_road_only,
    test_seeded_random_edges_exclude_synthetic_connectors,
    test_forced_failure_config_is_sparse_and_nonmutating,
    test_campaign_csv_has_stable_union_schema_and_rejects_canonical_tree,
]


if __name__ == "__main__":
    for test in TESTS:
        test()
    print("\n=== REVISION RUNNER TESTS PASSED ===")
