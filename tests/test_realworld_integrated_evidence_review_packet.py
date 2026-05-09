"""Tests for integrated E2/E3/E5 evidence review packet."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.integrated_evidence_review_packet import (  # noqa: E402
    DEFAULT_INTEGRATED_EVIDENCE_REVIEW_MANIFEST_PATH,
    DEFAULT_INTEGRATED_EVIDENCE_REVIEW_PACKET_PATH,
    INTEGRATED_EVIDENCE_REVIEW_COLUMNS,
    INTEGRATED_EVIDENCE_REVIEW_SCOPE,
    build_integrated_evidence_review_rows,
    write_integrated_evidence_review_packet,
)


def test_integrated_evidence_review_rows_classify_current_state() -> None:
    """Current E2/E3/validation/E5 manifests should remain blocked."""

    rows = build_integrated_evidence_review_rows()
    by_id = {row["review_id"]: row for row in rows}

    assert len(rows) == 5
    assert by_id["e2_rail_timing_capacity_dependency"]["integration_status"] == (
        "blocked_rail_source_decisions_pending"
    )
    assert by_id["e3_external_benchmark_dependency"]["integration_status"] == (
        "blocked_validation_benchmark_decisions_pending"
    )
    assert by_id["validation_strategy_dependency"]["integration_status"] == (
        "blocked_validation_strategy_dependencies"
    )
    assert by_id["e5_experiment_profile_dependency"]["integration_status"] == (
        "blocked_experiment_design_dependencies"
    )
    assert by_id["integrated_claim_boundary"]["integration_status"] == (
        "blocked_integrated_claim_boundary"
    )
    assert {row["claim_boundary"] for row in rows} == {
        INTEGRATED_EVIDENCE_REVIEW_SCOPE
    }
    assert all(row["can_support_final_claims"] == "false" for row in rows)

    print("PASS: integrated evidence review rows classify current state")


def test_integrated_evidence_review_writer_outputs_artifacts() -> None:
    """Writer should emit stable CSV, manifest, and Markdown artifacts."""

    rows = build_integrated_evidence_review_rows()
    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "integrated_evidence_review.csv"
        manifest_path = root / "manifest.json"
        doc_path = root / "packet.md"
        manifest = write_integrated_evidence_review_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == INTEGRATED_EVIDENCE_REVIEW_COLUMNS
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        doc_text = doc_path.read_text(encoding="utf-8")

    assert len(written_rows) == len(rows)
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert written_manifest["row_count"] == 5
    assert written_manifest["integrated_gate_closure_candidate_count"] == 0
    assert "Integrated Evidence Review Packet" in doc_text

    print("PASS: integrated evidence review writer emits artifacts")


def test_shipped_integrated_evidence_review_packet_matches_current_outputs() -> None:
    """Committed integrated packet should match current source manifests."""

    rows = build_integrated_evidence_review_rows()

    assert DEFAULT_INTEGRATED_EVIDENCE_REVIEW_PACKET_PATH.exists()
    assert DEFAULT_INTEGRATED_EVIDENCE_REVIEW_MANIFEST_PATH.exists()
    with DEFAULT_INTEGRATED_EVIDENCE_REVIEW_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    manifest = json.loads(
        DEFAULT_INTEGRATED_EVIDENCE_REVIEW_MANIFEST_PATH.read_text(
            encoding="utf-8"
        )
    )

    assert written_rows == rows
    assert manifest["row_count"] == len(rows)
    assert manifest["blocking_review_count"] == 5
    assert manifest["human_review_row_count"] == 0
    assert manifest["underlying_human_review_count"] == 14
    assert manifest["human_review_count"] == 14
    assert manifest["integrated_gate_closure_candidate_count"] == 0
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False

    print("PASS: shipped integrated evidence review packet matches outputs")


if __name__ == "__main__":
    test_integrated_evidence_review_rows_classify_current_state()
    test_integrated_evidence_review_writer_outputs_artifacts()
    test_shipped_integrated_evidence_review_packet_matches_current_outputs()
    print("\n=== REALWORLD INTEGRATED EVIDENCE REVIEW TESTS PASSED ===")
