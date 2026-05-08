"""Tests for reproducibility decision packet."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.reproducibility_decision_packet import (  # noqa: E402
    DEFAULT_REPRODUCIBILITY_DECISION_MANIFEST_PATH,
    DEFAULT_REPRODUCIBILITY_DECISION_PACKET_PATH,
    REPRODUCIBILITY_DECISION_COLUMNS,
    REPRODUCIBILITY_DECISION_SCOPE,
    build_reproducibility_decision_rows,
    write_reproducibility_decision_packet,
)


def test_reproducibility_decision_rows_classify_current_state() -> None:
    """Current reproducibility evidence should remain non-acceptance evidence."""

    rows = build_reproducibility_decision_rows()
    by_id = {row["decision_id"]: row for row in rows}

    assert len(rows) == 7
    assert by_id["reproducibility_manifest_scope_decision"]["decision_status"] == (
        "blocked_scaffold_reproducibility_manifest_scope"
    )
    assert by_id["validation_command_ladder_decision"]["decision_status"] == (
        "needs_human_review_command_ladder_scope"
    )
    assert by_id["clean_checkout_evidence_scope_decision"]["decision_status"] == (
        "blocked_bounded_or_stale_clean_checkout_evidence"
    )
    assert by_id["worktree_package_state_decision"]["decision_status"] == (
        "needs_human_review_committed_package_state"
    )
    assert by_id["runtime_import_boundary_decision"]["decision_status"] == (
        "needs_human_review_runtime_import_boundary"
    )
    assert by_id["artifact_regeneration_decision"]["decision_status"] == (
        "blocked_artifact_regeneration_not_tested"
    )
    assert by_id["formal_reproducibility_acceptance_boundary"]["decision_status"] == (
        "blocked_missing_reproducibility_acceptance_record"
    )
    assert "matches_review_head=false" in by_id[
        "clean_checkout_evidence_scope_decision"
    ]["current_evidence"]
    assert {row["claim_boundary"] for row in rows} == {
        REPRODUCIBILITY_DECISION_SCOPE
    }
    assert all(row["can_support_reproducibility_acceptance"] == "false" for row in rows)

    print("PASS: reproducibility decision rows classify current state")


def test_reproducibility_decision_writer_outputs_artifacts() -> None:
    """Writer should emit stable CSV, manifest, and Markdown artifacts."""

    rows = build_reproducibility_decision_rows()
    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "reproducibility_decision.csv"
        manifest_path = root / "manifest.json"
        doc_path = root / "packet.md"
        manifest = write_reproducibility_decision_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == REPRODUCIBILITY_DECISION_COLUMNS
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        doc_text = doc_path.read_text(encoding="utf-8")

    assert len(written_rows) == len(rows)
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert written_manifest["row_count"] == 7
    assert written_manifest["reproducibility_gate_closure_candidate_count"] == 0
    assert "Reproducibility Decision Packet" in doc_text

    print("PASS: reproducibility decision writer emits artifacts")


def test_shipped_reproducibility_decision_packet_matches_current_outputs() -> None:
    """Committed decision packet should match current reproducibility artifacts."""

    rows = build_reproducibility_decision_rows()

    assert DEFAULT_REPRODUCIBILITY_DECISION_PACKET_PATH.exists()
    assert DEFAULT_REPRODUCIBILITY_DECISION_MANIFEST_PATH.exists()
    with DEFAULT_REPRODUCIBILITY_DECISION_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    manifest = json.loads(
        DEFAULT_REPRODUCIBILITY_DECISION_MANIFEST_PATH.read_text(
            encoding="utf-8"
        )
    )

    assert written_rows == rows
    assert manifest["row_count"] == len(rows)
    assert manifest["blocking_decision_count"] == 4
    assert manifest["human_review_decision_count"] == 3
    assert manifest["reproducibility_manifest_decision_recorded"] is False
    assert manifest["reproducibility_decision_recorded"] is False
    assert manifest["command_ladder_decision_recorded"] is False
    assert manifest["clean_checkout_scope_decision_recorded"] is False
    assert manifest["artifact_regeneration_decision_recorded"] is False
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False

    print("PASS: shipped reproducibility decision packet matches outputs")


if __name__ == "__main__":
    test_reproducibility_decision_rows_classify_current_state()
    test_reproducibility_decision_writer_outputs_artifacts()
    test_shipped_reproducibility_decision_packet_matches_current_outputs()
    print("\n=== REALWORLD REPRODUCIBILITY DECISION TESTS PASSED ===")
