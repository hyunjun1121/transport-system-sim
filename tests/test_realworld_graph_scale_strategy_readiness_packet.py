"""Tests for graph-scale strategy-readiness packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.graph_scale_review import build_graph_scale_review_rows  # noqa: E402
from src.realworld.graph_scale_strategy_readiness_packet import (  # noqa: E402
    DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_MANIFEST_PATH,
    DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_PACKET_PATH,
    GRAPH_SCALE_STRATEGY_READINESS_COLUMNS,
    GRAPH_SCALE_STRATEGY_READINESS_SCOPE,
    build_graph_scale_strategy_readiness_rows,
    write_graph_scale_strategy_readiness_packet,
)


def test_graph_scale_strategy_readiness_rows_classify_current_options() -> None:
    """Graph-scale options should become concrete pre-review statuses."""

    rows = build_graph_scale_strategy_readiness_rows()
    by_option = {row["option_id"]: row for row in rows}

    assert len(rows) == 5
    assert by_option["current_reduced_corridor"]["readiness_status"] == (
        "needs_human_review_reduced_corridor_alternate_route_warnings"
    )
    assert by_option["multi_corridor_candidate"]["readiness_status"] == (
        "blocked_incomplete_multi_corridor_run_profile"
    )
    assert by_option["multi_corridor_full_candidate"]["readiness_status"] == (
        "needs_human_review_multi_corridor_result_deltas"
    )
    assert by_option["full_bus_practical_graph"]["readiness_status"] == (
        "blocked_missing_full_graph_experiment_outputs"
    )
    assert by_option["graph_scale_acceptance_record"]["readiness_status"] == (
        "blocked_missing_graph_scale_acceptance_record"
    )
    assert {row["claim_boundary"] for row in rows} == {
        GRAPH_SCALE_STRATEGY_READINESS_SCOPE
    }
    assert all(row["can_support_graph_scale_gate"] == "false" for row in rows)

    print("PASS: graph-scale strategy-readiness rows classify current options")


def test_graph_scale_strategy_readiness_rows_handle_small_fixture() -> None:
    """Fixture rows should classify unknown or complete options conservatively."""

    review_rows = [
        _row(
            "current_reduced_corridor",
            "true",
            "0",
            "1890",
        ),
        _row(
            "full_bus_practical_graph",
            "false",
            "0",
            "1890",
        ),
        _row(
            "unexpected_option",
            "true",
            "0",
            "0",
        ),
    ]
    rows = build_graph_scale_strategy_readiness_rows(
        review_rows=review_rows,
        acceptance_path=Path("missing_graph_scale_acceptance.json"),
    )
    by_option = {row["option_id"]: row for row in rows}

    assert by_option["current_reduced_corridor"]["readiness_status"] == (
        "needs_human_review_reduced_corridor_scope"
    )
    assert by_option["full_bus_practical_graph"]["readiness_status"] == (
        "needs_human_review_full_graph_outputs"
    )
    assert by_option["unexpected_option"]["readiness_status"] == (
        "blocked_unclassified_graph_scale_option"
    )

    print("PASS: graph-scale strategy-readiness rows handle fixture cases")


def test_write_graph_scale_strategy_readiness_packet_outputs_artifacts() -> None:
    """Writer should emit CSV, manifest, and Markdown artifacts."""

    rows = build_graph_scale_strategy_readiness_rows(
        review_rows=build_graph_scale_review_rows(),
    )

    with TemporaryDirectory() as directory:
        output = Path(directory) / "graph_scale_strategy_readiness.csv"
        manifest = Path(directory) / "graph_scale_strategy_readiness_manifest.json"
        doc = Path(directory) / "graph_scale_strategy_readiness.md"
        value = write_graph_scale_strategy_readiness_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
            doc_path=doc,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == (
                GRAPH_SCALE_STRATEGY_READINESS_COLUMNS
            )
        with manifest.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)
        text = doc.read_text(encoding="utf-8")

        assert len(written_rows) == len(rows)
        assert value["publication_ready"] is False
        assert value["can_mark_complete"] is False
        assert written_manifest["graph_scale_gate_closure_candidate_count"] == 0
        assert "Graph-Scale Strategy Readiness Packet" in text

    print("PASS: graph-scale strategy-readiness writer emits artifacts")


def test_shipped_graph_scale_strategy_readiness_packet_matches_current_review() -> None:
    """Current shipped readiness packet should stay non-accepting."""

    rows = build_graph_scale_strategy_readiness_rows()

    assert DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_PACKET_PATH.exists()
    assert DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_MANIFEST_PATH.exists()
    with DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    with DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_MANIFEST_PATH.open(
        "r",
        encoding="utf-8",
    ) as handle:
        manifest = json.load(handle)

    assert len(written_rows) == len(rows)
    assert [row["option_id"] for row in written_rows] == [
        row["option_id"] for row in rows
    ]
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["result_scope"] == GRAPH_SCALE_STRATEGY_READINESS_SCOPE
    assert manifest["graph_scale_gate_closure_candidate_count"] == 0

    print("PASS: shipped graph-scale strategy-readiness packet matches current review")


def _row(
    option_id: str,
    alternate_paths_preserved: str,
    alternate_route_warn: str,
    experiment_row_count: str,
) -> dict[str, str]:
    return {
        "option_id": option_id,
        "option_label": option_id,
        "region_id": "fixture",
        "source_graph_nodes": "10",
        "source_graph_edges": "20",
        "analysis_graph_nodes": "10",
        "analysis_graph_edges": "20",
        "analysis_graph_reduced": "false",
        "experiment_run_profile": "fixture",
        "experiment_row_count": experiment_row_count,
        "experiment_summary_row_count": "1",
        "alternate_route_warn": alternate_route_warn,
        "alternate_paths_preserved": alternate_paths_preserved,
        "available_evidence": "fixture evidence",
        "publication_use_status": "fixture",
    }


if __name__ == "__main__":
    test_graph_scale_strategy_readiness_rows_classify_current_options()
    test_graph_scale_strategy_readiness_rows_handle_small_fixture()
    test_write_graph_scale_strategy_readiness_packet_outputs_artifacts()
    test_shipped_graph_scale_strategy_readiness_packet_matches_current_review()
    print("\n=== REALWORLD GRAPH-SCALE STRATEGY READINESS TESTS PASSED ===")
