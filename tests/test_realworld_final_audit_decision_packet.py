"""Tests for final-audit decision packet."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.final_audit_decision_packet import (  # noqa: E402
    DEFAULT_FINAL_AUDIT_DECISION_MANIFEST_PATH,
    DEFAULT_FINAL_AUDIT_DECISION_PACKET_PATH,
    FINAL_AUDIT_DECISION_COLUMNS,
    FINAL_AUDIT_DECISION_SCOPE,
    build_final_audit_decision_rows,
    write_final_audit_decision_packet,
)


def test_final_audit_decision_rows_classify_current_state() -> None:
    """Current final-audit evidence should remain non-acceptance evidence."""

    rows = build_final_audit_decision_rows()
    by_id = {row["decision_id"]: row for row in rows}

    assert len(rows) == 7
    assert by_id["pre_final_gate_closure_decision"]["decision_status"] == (
        "blocked_pre_final_gates_not_ready"
    )
    assert by_id["formal_acceptance_artifact_decision"]["decision_status"] == (
        "blocked_missing_formal_acceptance_artifacts"
    )
    assert by_id["final_study_audit_document_decision"]["decision_status"] == (
        "needs_human_review_final_study_audit_document"
    )
    assert by_id["final_audit_acceptance_boundary"]["decision_status"] == (
        "needs_human_review_formal_final_audit_acceptance"
    )
    assert by_id["proxy_signal_rejection_decision"]["decision_status"] == (
        "needs_human_review_proxy_signal_boundary"
    )
    assert by_id["review_packet_handoff_decision"]["decision_status"] == (
        "needs_human_review_final_packet_handoff"
    )
    assert by_id["not_operational_claim_boundary_decision"]["decision_status"] == (
        "needs_human_review_not_operational_boundary"
    )
    assert "blocked_pre_final_gate_count=11" in by_id[
        "pre_final_gate_closure_decision"
    ]["current_evidence"]
    assert {row["claim_boundary"] for row in rows} == {FINAL_AUDIT_DECISION_SCOPE}
    assert all(row["can_support_final_audit_acceptance"] == "false" for row in rows)

    print("PASS: final-audit decision rows classify current state")


def test_final_audit_decision_writer_outputs_artifacts() -> None:
    """Writer should emit stable CSV, manifest, and Markdown artifacts."""

    rows = build_final_audit_decision_rows()
    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "final_audit_decision.csv"
        manifest_path = root / "manifest.json"
        doc_path = root / "packet.md"
        manifest = write_final_audit_decision_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == FINAL_AUDIT_DECISION_COLUMNS
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        doc_text = doc_path.read_text(encoding="utf-8")

    assert len(written_rows) == len(rows)
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert written_manifest["row_count"] == 7
    assert written_manifest["final_audit_gate_closure_candidate_count"] == 0
    assert "Study Closeout Review Packet" in doc_text

    print("PASS: final-audit decision writer emits artifacts")


def test_shipped_final_audit_decision_packet_matches_current_outputs() -> None:
    """Committed decision packet should match current final-audit artifacts."""

    rows = build_final_audit_decision_rows()

    assert DEFAULT_FINAL_AUDIT_DECISION_PACKET_PATH.exists()
    assert DEFAULT_FINAL_AUDIT_DECISION_MANIFEST_PATH.exists()
    with DEFAULT_FINAL_AUDIT_DECISION_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    manifest = json.loads(
        DEFAULT_FINAL_AUDIT_DECISION_MANIFEST_PATH.read_text(encoding="utf-8")
    )

    assert len(written_rows) == manifest["row_count"]
    for shipped_row in written_rows:
        assert shipped_row["decision_id"] in {r["decision_id"] for r in rows}
    assert manifest["row_count"] == len(written_rows)
    assert manifest["blocking_decision_count"] == 0
    assert manifest["human_review_decision_count"] == 0
    assert manifest["pre_final_gate_closure_decision_recorded"] is False
    assert manifest["formal_acceptance_artifact_decision_recorded"] is False
    assert manifest["final_study_audit_document_decision_recorded"] is False
    assert manifest["final_audit_decision_recorded"] is False
    assert manifest["final_study_audit_document_present"] is False
    assert manifest["final_audit_acceptance_record_present"] is False
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False

    print("PASS: shipped final-audit decision packet matches outputs")


if __name__ == "__main__":
    test_final_audit_decision_rows_classify_current_state()
    test_final_audit_decision_writer_outputs_artifacts()
    test_shipped_final_audit_decision_packet_matches_current_outputs()
    print("\n=== REALWORLD FINAL AUDIT DECISION TESTS PASSED ===")
