"""Tests for figure/table review packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.figure_table_review_packet import (  # noqa: E402
    DEFAULT_FIGURE_TABLE_REVIEW_MANIFEST_PATH,
    DEFAULT_FIGURE_TABLE_REVIEW_PACKET_PATH,
    FIGURE_TABLE_REVIEW_COLUMNS,
    FIGURE_TABLE_REVIEW_SCOPE,
    build_figure_table_review_rows,
    write_figure_table_review_packet,
)


def test_figure_table_review_rows_classify_current_state() -> None:
    """Current figure/table outputs should remain review-only scaffold rows."""

    rows = build_figure_table_review_rows()
    by_id = {row["review_id"]: row for row in rows}

    assert len(rows) == 8
    assert by_id["artifact_inventory"]["review_status"] == (
        "needs_human_review_artifact_inventory"
    )
    assert by_id["table_lineage_and_row_counts"]["review_status"] == (
        "needs_human_review_table_lineage"
    )
    assert by_id["caption_and_claim_boundary"]["review_status"] == (
        "needs_human_review_caption_boundary"
    )
    assert by_id["graph_scope_dependency"]["review_status"] == (
        "blocked_reduced_graph_scope_dependency"
    )
    assert by_id["sensitivity_index_handling"]["review_status"] == (
        "needs_human_review_morris_index_handling"
    )
    assert by_id["bottleneck_and_regime_interpretation"]["review_status"] == (
        "needs_human_review_proxy_interpretation"
    )
    assert by_id["upstream_evidence_dependency"]["review_status"] == (
        "blocked_upstream_evidence_dependency"
    )
    assert by_id["formal_manuscript_acceptance_boundary"]["review_status"] == (
        "needs_human_review_formal_manuscript_acceptance"
    )
    assert {row["claim_boundary"] for row in rows} == {FIGURE_TABLE_REVIEW_SCOPE}
    assert all(row["can_support_manuscript_gate"] == "false" for row in rows)

    print("PASS: figure/table review rows classify current state")


def test_figure_table_review_writer_outputs_artifacts() -> None:
    """The writer should emit CSV, manifest, and Markdown review artifacts."""

    rows = build_figure_table_review_rows()
    with TemporaryDirectory() as directory:
        manifest = write_figure_table_review_packet(
            rows=rows,
            output_path=f"{directory}/figure_table_review_packet.csv",
            manifest_path=f"{directory}/figure_table_review_manifest.json",
            doc_path=f"{directory}/figure_table_review_packet.md",
        )

        assert manifest["row_count"] == 8
        assert manifest["blocking_review_count"] == 2
        assert manifest["human_review_count"] == 6
        assert manifest["manuscript_gate_closure_candidate_count"] == 0
        assert manifest["publication_ready"] is False
        assert manifest["can_mark_complete"] is False

        with open(manifest["outputs"]["csv"], "r", encoding="utf-8", newline="") as handle:
            output_rows = list(csv.DictReader(handle))
        assert output_rows
        assert list(output_rows[0]) == list(FIGURE_TABLE_REVIEW_COLUMNS)
        assert all(row["can_support_manuscript_gate"] == "false" for row in output_rows)

        with open(manifest["outputs"]["manifest"], "r", encoding="utf-8") as handle:
            manifest_file = json.load(handle)
        assert manifest_file["row_count"] == manifest["row_count"]

        with open(manifest["outputs"]["doc"], "r", encoding="utf-8") as handle:
            doc = handle.read()
        assert "Figure/Table Review Packet" in doc
        assert "not manuscript decision" in doc

    print("PASS: figure/table review writer emits artifacts")


def test_shipped_figure_table_review_packet_matches_current_outputs() -> None:
    """Shipped packet should match the current generated artifact state."""

    rows = build_figure_table_review_rows()
    expected_statuses = {
        row["review_id"]: row["review_status"]
        for row in rows
    }

    with DEFAULT_FIGURE_TABLE_REVIEW_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        shipped_rows = list(csv.DictReader(handle))

    with DEFAULT_FIGURE_TABLE_REVIEW_MANIFEST_PATH.open(
        "r",
        encoding="utf-8",
    ) as handle:
        manifest = json.load(handle)

    assert len(shipped_rows) == len(rows)
    assert manifest["row_count"] == len(shipped_rows)
    assert manifest["blocking_review_count"] == 0
    assert manifest["human_review_count"] == 0
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    for row in shipped_rows:
        assert row["review_id"] in expected_statuses

    print("PASS: shipped figure/table review packet matches outputs")


if __name__ == "__main__":
    test_figure_table_review_rows_classify_current_state()
    test_figure_table_review_writer_outputs_artifacts()
    test_shipped_figure_table_review_packet_matches_current_outputs()
    print("\n=== REALWORLD FIGURE/TABLE REVIEW TESTS PASSED ===")
