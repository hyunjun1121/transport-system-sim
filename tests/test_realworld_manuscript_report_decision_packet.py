"""Tests for manuscript/report decision packet."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.manuscript_report_decision_packet import (  # noqa: E402
    DEFAULT_MANUSCRIPT_REPORT_DECISION_MANIFEST_PATH,
    DEFAULT_MANUSCRIPT_REPORT_DECISION_PACKET_PATH,
    MANUSCRIPT_REPORT_DECISION_COLUMNS,
    MANUSCRIPT_REPORT_DECISION_SCOPE,
    build_manuscript_report_decision_rows,
    write_manuscript_report_decision_packet,
)


def test_manuscript_report_decision_rows_classify_current_state() -> None:
    """Current manuscript/report artifacts should stay blocked for acceptance."""

    rows = build_manuscript_report_decision_rows()
    by_id = {row["decision_id"]: row for row in rows}

    assert len(rows) == 7
    assert by_id["paper_claim_review_decision"]["decision_status"] == (
        "needs_human_review_paper_claims"
    )
    assert by_id["korean_report_review_decision"]["decision_status"] == (
        "needs_human_review_korean_report_scope"
    )
    assert by_id["figure_table_use_decision"]["decision_status"] == (
        "needs_human_review_figure_table_use"
    )
    assert by_id["result_claim_alignment_decision"]["decision_status"] == (
        "needs_human_review_claim_alignment"
    )
    assert by_id["upstream_evidence_gate_dependency"]["decision_status"] == (
        "needs_human_review_upstream_gate_scope"
    )
    assert by_id["docx_regeneration_decision"]["decision_status"] == (
        "needs_human_review_docx_regeneration"
    )
    assert by_id["formal_manuscript_acceptance_boundary"]["decision_status"] == (
        "needs_human_review_formal_manuscript_acceptance"
    )
    claim_alignment_manifest = json.loads(
        (ROOT / "data" / "manifests" / "claim_alignment_review_manifest.json")
        .read_text(encoding="utf-8")
    )
    expected_overclaim_count = claim_alignment_manifest["overclaim_candidate_count"]
    assert f"overclaim_candidate_count={expected_overclaim_count}" in by_id[
        "result_claim_alignment_decision"
    ]["current_evidence"]
    assert {row["claim_boundary"] for row in rows} == {
        MANUSCRIPT_REPORT_DECISION_SCOPE
    }
    assert all(row["can_support_manuscript_acceptance"] == "false" for row in rows)

    print("PASS: manuscript/report decision rows classify current state")


def test_manuscript_report_decision_writer_outputs_artifacts() -> None:
    """Writer should emit stable CSV, manifest, and Markdown artifacts."""

    rows = build_manuscript_report_decision_rows()
    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "manuscript_report_decision.csv"
        manifest_path = root / "manifest.json"
        doc_path = root / "packet.md"
        manifest = write_manuscript_report_decision_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == MANUSCRIPT_REPORT_DECISION_COLUMNS
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        doc_text = doc_path.read_text(encoding="utf-8")

    assert len(written_rows) == len(rows)
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert written_manifest["row_count"] == 7
    assert written_manifest["blocking_decision_count"] == 0
    assert written_manifest["human_review_decision_count"] == 7
    assert written_manifest["manuscript_gate_closure_candidate_count"] == 0
    assert "Manuscript/Report Decision Packet" in doc_text

    print("PASS: manuscript/report decision writer emits artifacts")


def test_shipped_manuscript_report_decision_packet_matches_current_outputs() -> None:
    """Committed decision packet should match current manuscript artifacts."""

    rows = build_manuscript_report_decision_rows()

    assert DEFAULT_MANUSCRIPT_REPORT_DECISION_PACKET_PATH.exists()
    assert DEFAULT_MANUSCRIPT_REPORT_DECISION_MANIFEST_PATH.exists()
    with DEFAULT_MANUSCRIPT_REPORT_DECISION_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    manifest = json.loads(
        DEFAULT_MANUSCRIPT_REPORT_DECISION_MANIFEST_PATH.read_text(
            encoding="utf-8"
        )
    )

    assert len(written_rows) == manifest["row_count"]
    for shipped_row in written_rows:
        assert shipped_row["decision_id"] in {r["decision_id"] for r in rows}
    assert manifest["row_count"] == len(written_rows)
    assert manifest["blocking_decision_count"] == 0
    assert manifest["human_review_decision_count"] == 0
    assert manifest["paper_review_decision_recorded"] is False
    assert manifest["korean_report_review_decision_recorded"] is False
    assert manifest["docx_regeneration_decision_recorded"] is False
    assert manifest["figure_table_decision_recorded"] is False
    assert manifest["result_claims_aligned"] is False
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False

    print("PASS: shipped manuscript/report decision packet matches outputs")


if __name__ == "__main__":
    test_manuscript_report_decision_rows_classify_current_state()
    test_manuscript_report_decision_writer_outputs_artifacts()
    test_shipped_manuscript_report_decision_packet_matches_current_outputs()
    print("\n=== REALWORLD MANUSCRIPT REPORT DECISION TESTS PASSED ===")
