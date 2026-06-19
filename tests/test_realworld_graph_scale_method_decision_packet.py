"""Tests for graph-scale method decision packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.graph_scale_method_decision_packet import (  # noqa: E402
    DEFAULT_GRAPH_SCALE_METHOD_DECISION_MANIFEST_PATH,
    DEFAULT_GRAPH_SCALE_METHOD_DECISION_PACKET_PATH,
    GRAPH_SCALE_METHOD_DECISION_COLUMNS,
    GRAPH_SCALE_METHOD_DECISION_SCOPE,
    build_graph_scale_method_decision_rows,
    write_graph_scale_method_decision_packet,
)


def test_graph_scale_method_decision_rows_surface_current_blockers() -> None:
    """Current method-decision rows should expose graph-scale blockers."""

    rows = build_graph_scale_method_decision_rows()
    by_id = {row["decision_id"]: row for row in rows}

    assert len(rows) == 7
    assert by_id["current_reduced_corridor_method_option"]["decision_status"] == (
        "needs_human_review_reduced_corridor_warning_policy"
    )
    assert "alternate_route_warn=6" in by_id[
        "current_reduced_corridor_method_option"
    ]["current_evidence"]
    assert by_id["multi_corridor_candidate_method_option"]["decision_status"] == (
        "needs_human_review_multi_corridor_sample_scope"
    )
    assert by_id["multi_corridor_full_candidate_method_option"][
        "decision_status"
    ] == "needs_human_review_multi_corridor_result_delta_policy"
    assert "candidate_worsens=27" in by_id[
        "multi_corridor_full_candidate_method_option"
    ]["current_evidence"]
    assert by_id["full_bus_practical_graph_method_option"]["decision_status"] == (
        "blocked_missing_full_graph_full_profile_outputs"
    )
    assert by_id["downstream_regeneration_scope"]["decision_status"] == (
        "blocked_missing_downstream_regeneration_decision"
    )
    assert by_id["formal_graph_scale_acceptance_boundary"]["decision_status"] == (
        "needs_human_review_existing_graph_scale_acceptance"
    )
    assert {row["claim_boundary"] for row in rows} == {
        GRAPH_SCALE_METHOD_DECISION_SCOPE
    }
    assert all(row["can_support_graph_scale_gate"] == "false" for row in rows)

    print("PASS: graph-scale method-decision rows surface current blockers")


def test_graph_scale_method_decision_writer_outputs_artifacts() -> None:
    """Writer should emit CSV, manifest, and Markdown artifacts."""

    rows = build_graph_scale_method_decision_rows()
    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "graph_scale_method_decision.csv"
        manifest_path = root / "graph_scale_method_decision_manifest.json"
        doc_path = root / "graph_scale_method_decision.md"
        manifest = write_graph_scale_method_decision_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == GRAPH_SCALE_METHOD_DECISION_COLUMNS
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        doc_text = doc_path.read_text(encoding="utf-8")

    assert len(written_rows) == len(rows)
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["selected_graph_method_recorded"] is False
    assert manifest["downstream_regeneration_decision_recorded"] is False
    assert written_manifest["graph_scale_gate_closure_candidate_count"] == 0
    assert "Graph-Scale Method Decision Packet" in doc_text
    assert "It does not select a graph method" in doc_text

    print("PASS: graph-scale method-decision writer emits artifacts")


def test_shipped_graph_scale_method_decision_packet_matches_current_outputs() -> None:
    """Committed graph-scale method packet should match current artifacts."""

    rows = build_graph_scale_method_decision_rows()

    assert DEFAULT_GRAPH_SCALE_METHOD_DECISION_PACKET_PATH.exists()
    assert DEFAULT_GRAPH_SCALE_METHOD_DECISION_MANIFEST_PATH.exists()
    with DEFAULT_GRAPH_SCALE_METHOD_DECISION_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    manifest = json.loads(
        DEFAULT_GRAPH_SCALE_METHOD_DECISION_MANIFEST_PATH.read_text(
            encoding="utf-8"
        )
    )

    assert len(written_rows) == len(rows)
    assert [row["decision_id"] for row in written_rows] == [
        row["decision_id"] for row in rows
    ]
    assert manifest["row_count"] == 7
    assert manifest["blocking_decision_count"] == 0
    assert manifest["human_review_decision_count"] == 0
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False

    print("PASS: shipped graph-scale method-decision packet matches outputs")


if __name__ == "__main__":
    test_graph_scale_method_decision_rows_surface_current_blockers()
    test_graph_scale_method_decision_writer_outputs_artifacts()
    test_shipped_graph_scale_method_decision_packet_matches_current_outputs()
    print("\n=== REALWORLD GRAPH-SCALE METHOD DECISION TESTS PASSED ===")
