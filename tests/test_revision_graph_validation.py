"""Tests for structural graph-scope route evidence."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.realworld.revision_graph_validation import (
    CANONICAL_PUBLIC_ROAD_LEGS,
    compute_corridor_target_scope_metrics,
    compute_graph_scope_route_metrics,
    write_corridor_target_scope_evidence,
    write_graph_scope_route_evidence,
)


def _edge(
    graph: nx.DiGraph,
    source: str,
    target: str,
    *,
    time: float,
    length: float | None,
) -> None:
    attrs = {"mode": "road", "t0": time}
    if length is not None:
        attrs["length_m"] = length
    graph.add_edge(source, target, **attrs)


def _full_graph() -> nx.DiGraph:
    graph = nx.DiGraph()
    # A->D has a two-edge shortest path and a slower alternative.
    _edge(graph, "A", "x", time=1.0, length=1_000.0)
    _edge(graph, "x", "D", time=1.0, length=1_000.0)
    _edge(graph, "A", "y", time=2.0, length=2_000.0)
    _edge(graph, "y", "D", time=2.0, length=2_000.0)
    _edge(graph, "A", "S", time=3.0, length=3_000.0)
    _edge(graph, "R", "D", time=4.0, length=4_000.0)
    _edge(graph, "S", "R", time=5.0, length=5_000.0)
    # Rail edges must never be included in road metrics.
    graph.add_edge("S", "R", mode="rail", t0=0.1, length_m=50.0)
    return graph


def _reduced_graph() -> nx.DiGraph:
    graph = nx.DiGraph()
    _edge(graph, "A", "y", time=2.0, length=2_000.0)
    _edge(graph, "y", "D", time=2.0, length=2_000.0)
    _edge(graph, "A", "S", time=3.0, length=3_000.0)
    _edge(graph, "R", "D", time=4.0, length=None)
    # S->R intentionally absent to exercise honest unreachable reporting.
    graph.graph["corridor_path_count"] = 3
    graph.graph["corridor_method_version"] = "hybrid_exact3_penalty_v1"
    graph.graph["corridor_candidate_method"] = "exact_shortest_simple_paths"
    graph.graph["corridor_leg_candidates_json"] = json.dumps(
        {
            "A_to_D": {
                "candidate_count": 2,
                "exact_shortest_count": 2,
                "expansion_count": 0,
                "method": "exact_shortest_simple_paths",
            },
            "A_to_S": {
                "candidate_count": 1,
                "exact_shortest_count": 1,
                "expansion_count": 0,
                "method": "exact_shortest_simple_paths",
            },
            "R_to_D": {
                "candidate_count": 1,
                "exact_shortest_count": 1,
                "expansion_count": 0,
                "method": "exact_shortest_simple_paths",
            },
        },
        sort_keys=True,
    )
    return graph


def test_metrics_cover_every_scope_and_public_canonical_leg() -> None:
    rows = compute_graph_scope_route_metrics(
        {"top3": _reduced_graph(), "full": _full_graph()},
        diversity_limits={"top3": 3, "full": 3},
    )

    assert len(rows) == 2 * len(CANONICAL_PUBLIC_ROAD_LEGS)
    keyed = {(row.graph_scope, row.leg_id): row for row in rows}

    full = keyed[("full", "A_to_D")]
    assert full.connected is True
    assert full.shortest_travel_time_min == 2.0
    assert full.shortest_distance_m == 2_000.0
    assert full.path_edge_count == 2
    assert full.path_diversity_count == 0
    assert full.path_diversity_status == "not_enumerated_cost_guard"
    assert full.path_diversity_method == "not_enumerated_cost_guard"
    assert full.full_path_edge_overlap_ratio == 1.0
    assert full.travel_time_detour_ratio_vs_full == 1.0
    assert len(full.path_signature_sha256) == 64

    reduced = keyed[("top3", "A_to_D")]
    assert reduced.connected is True
    assert reduced.shortest_travel_time_min == 4.0
    assert reduced.shortest_distance_m == 4_000.0
    assert reduced.full_path_edge_overlap_ratio == 0.0
    assert reduced.full_path_edge_jaccard == 0.0
    assert reduced.travel_time_detour_ratio_vs_full == 2.0
    assert reduced.distance_detour_ratio_vs_full == 2.0
    assert reduced.path_diversity_count == 2
    assert reduced.path_diversity_status == "exhausted_before_limit"
    assert reduced.path_diversity_method == "exact_shortest_simple_paths"

    missing_length = keyed[("top3", "R_to_D")]
    assert missing_length.connected is True
    assert missing_length.shortest_distance_m is None
    assert missing_length.distance_status == "missing_or_invalid_length_m"
    assert missing_length.distance_detour_ratio_vs_full is None

    unreachable = keyed[("top3", "S_to_R")]
    assert unreachable.connected is False
    assert unreachable.path_edge_count == 0
    assert unreachable.shortest_travel_time_min is None
    assert unreachable.path_diversity_count == 0
    assert unreachable.path_diversity_status == "not_enumerated_cost_guard"
    assert unreachable.path_diversity_method == "not_enumerated_cost_guard"


def test_shortest_simple_paths_is_never_called_during_validation() -> None:
    original = nx.shortest_simple_paths

    def forbidden(*args: object, **kwargs: object) -> object:
        raise AssertionError("shortest_simple_paths must not run during graph validation")

    nx.shortest_simple_paths = forbidden
    try:
        rows = compute_graph_scope_route_metrics(
            {"top3": _reduced_graph(), "full": _full_graph()},
            diversity_limits={"top3": 3, "full": 3},
        )
    finally:
        nx.shortest_simple_paths = original

    assert len(rows) == 2 * len(CANONICAL_PUBLIC_ROAD_LEGS)


def test_missing_candidate_metadata_is_explicit_and_never_recomputed() -> None:
    reduced = _reduced_graph()
    del reduced.graph["corridor_leg_candidates_json"]
    rows = compute_graph_scope_route_metrics(
        {"top3": reduced, "full": _full_graph()},
        diversity_limits={"top3": 3, "full": 3},
    )
    keyed = {(row.graph_scope, row.leg_id): row for row in rows}
    row = keyed[("top3", "A_to_D")]
    assert row.path_diversity_count == 0
    assert row.path_diversity_status == "candidate_metadata_missing"
    assert row.path_diversity_method == "candidate_metadata_missing"


def test_evidence_writer_is_isolated_hashed_and_coordinate_free() -> None:
    rows = compute_graph_scope_route_metrics(
        {"full": _full_graph()}, diversity_limits={"full": 2}
    )
    input_artifacts = {
        "cache": {"path": "data/cache/public.graphml", "sha256": "a" * 64, "size_bytes": 99}
    }
    with TemporaryDirectory() as temp_dir:
        output_root = Path(temp_dir) / "paper-revision"
        result = write_graph_scope_route_evidence(
            output_root,
            rows,
            input_artifacts=input_artifacts,
        )
        csv_path = Path(result["metrics_path"])
        manifest_path = Path(result["manifest_path"])
        assert csv_path.name == "graph_scope_route_metrics.csv"
        assert manifest_path.name == "graph_scope_route_metrics_manifest.json"

        with csv_path.open(encoding="utf-8-sig", newline="") as handle:
            written = list(csv.DictReader(handle))
        assert len(written) == len(CANONICAL_PUBLIC_ROAD_LEGS)
        assert all("lat" not in key.lower() and "lon" not in key.lower() for key in written[0])

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert manifest["final_study_ready"] is False
        assert manifest["contains_coordinates"] is False
        assert manifest["public_canonical_node_ids_only"] is True
        assert manifest["stage_independent"] is True
        assert manifest["schema_version"] == 2
        assert manifest["path_diversity_count_source"] == (
            "reduced-scope corridor_leg_candidates_json metadata"
        )
        assert manifest["path_diversity_cost_guard"]["sentinel_count"] == 0
        assert manifest["path_diversity_cost_guard"]["status"] == (
            "not_enumerated_cost_guard"
        )
        assert manifest["input_artifacts"] == input_artifacts
        assert len(manifest["output_artifact"]["sha256"]) == 64
        assert manifest["output_artifact"]["size_bytes"] == csv_path.stat().st_size


def test_corridor_target_response_uses_one_fixed_edge_set_across_scopes() -> None:
    full = _full_graph()
    top10 = nx.DiGraph()
    _edge(top10, "A", "x", time=1.0, length=1_000.0)
    _edge(top10, "x", "D", time=1.0, length=1_000.0)
    target = (("A", "x"), ("x", "D"))
    rows = compute_corridor_target_scope_metrics(
        {"top10": top10, "full": full},
        selected_edges=target,
        road_multipliers=(1.0, 2.0, 3.0),
    )
    keyed = {(row.graph_scope, row.road_multiplier): row for row in rows}
    assert keyed[("top10", 1.0)].shortest_travel_time_min == 2.0
    assert keyed[("full", 1.0)].shortest_travel_time_min == 2.0
    assert keyed[("top10", 3.0)].shortest_travel_time_min == 6.0
    assert keyed[("full", 3.0)].shortest_travel_time_min == 4.0
    assert keyed[("top10", 3.0)].travel_time_ratio_vs_full == 1.5
    assert keyed[("full", 3.0)].path_target_edge_count == 0
    assert len({row.selected_target_checksum for row in rows}) == 1

    with TemporaryDirectory() as temp_dir:
        written = write_corridor_target_scope_evidence(
            Path(temp_dir) / "paper-revision",
            rows,
            input_artifacts={"cache": {"sha256": "a" * 64}},
        )
        manifest = json.loads(
            Path(written["manifest_path"]).read_text(encoding="utf-8")
        )
        assert manifest["contains_coordinates"] is False
        assert manifest["fixed_target_across_scopes"] is True
        assert manifest["row_count"] == 6
        assert len(manifest["output_artifact"]["sha256"]) == 64


TESTS = [
    test_metrics_cover_every_scope_and_public_canonical_leg,
    test_shortest_simple_paths_is_never_called_during_validation,
    test_missing_candidate_metadata_is_explicit_and_never_recomputed,
    test_evidence_writer_is_isolated_hashed_and_coordinate_free,
    test_corridor_target_response_uses_one_fixed_edge_set_across_scopes,
]


if __name__ == "__main__":
    for test in TESTS:
        test()
    print("test_revision_graph_validation: all checks passed")
