"""Tests for pilot-region decision packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.pilot_region_decision_packet import (  # noqa: E402
    DEFAULT_PILOT_REGION_DECISION_MANIFEST_PATH,
    DEFAULT_PILOT_REGION_DECISION_PACKET_PATH,
    PILOT_REGION_DECISION_COLUMNS,
    PILOT_REGION_DECISION_SCOPE,
    build_pilot_region_decision_rows,
    write_pilot_region_decision_packet,
)


def test_pilot_region_decision_rows_surface_current_blockers() -> None:
    """Current pilot-region decision rows should expose acceptance blockers."""

    rows = build_pilot_region_decision_rows()
    by_id = {row["decision_id"]: row for row in rows}

    assert len(rows) == 6
    assert by_id["pilot_case_scope_decision"]["decision_status"] == (
        "needs_human_review_pilot_case_scope"
    )
    assert "region_id=songpa_public_demo" in by_id["pilot_case_scope_decision"][
        "current_evidence"
    ]
    assert by_id["privacy_review_completion_decision"]["decision_status"] == (
        "needs_human_review_privacy_completion"
    )
    assert "review_required_count=7" in by_id["privacy_review_completion_decision"][
        "current_evidence"
    ]
    assert by_id["graph_scale_dependency_decision"]["decision_status"] == (
        "needs_human_review_existing_graph_scale_acceptance"
    )
    assert by_id["cache_and_provenance_scope_decision"]["decision_status"] == (
        "needs_human_review_existing_provenance_acceptance"
    )
    assert by_id["formal_pilot_acceptance_boundary"]["decision_status"] == (
        "needs_human_review_existing_pilot_acceptance"
    )
    assert {row["claim_boundary"] for row in rows} == {
        PILOT_REGION_DECISION_SCOPE
    }
    assert all(row["can_support_pilot_acceptance"] == "false" for row in rows)

    print("PASS: pilot-region decision rows surface current blockers")


def test_pilot_region_decision_writer_outputs_artifacts() -> None:
    """Writer should emit CSV, manifest, and Markdown artifacts."""

    rows = build_pilot_region_decision_rows()
    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "pilot_region_decision.csv"
        manifest_path = root / "pilot_region_decision_manifest.json"
        doc_path = root / "pilot_region_decision.md"
        manifest = write_pilot_region_decision_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == PILOT_REGION_DECISION_COLUMNS
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        doc_text = doc_path.read_text(encoding="utf-8")

    assert len(written_rows) == len(rows)
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["pilot_region_decision_recorded"] is False
    assert manifest["privacy_completion_decision_recorded"] is False
    assert written_manifest["pilot_acceptance_closure_candidate_count"] == 0
    assert "Pilot Region Decision Packet" in doc_text
    assert "It does not approve privacy" in doc_text

    print("PASS: pilot-region decision writer emits artifacts")


def test_shipped_pilot_region_decision_packet_matches_current_outputs() -> None:
    """Committed pilot-region decision packet should match current artifacts."""

    rows = build_pilot_region_decision_rows()

    assert DEFAULT_PILOT_REGION_DECISION_PACKET_PATH.exists()
    assert DEFAULT_PILOT_REGION_DECISION_MANIFEST_PATH.exists()
    with DEFAULT_PILOT_REGION_DECISION_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    manifest = json.loads(
        DEFAULT_PILOT_REGION_DECISION_MANIFEST_PATH.read_text(encoding="utf-8")
    )

    assert len(written_rows) == len(rows)
    assert [row["decision_id"] for row in written_rows] == [
        row["decision_id"] for row in rows
    ]
    assert manifest["row_count"] == 6
    assert manifest["blocking_decision_count"] == 0
    # All 6 pilot-region rows need human review; none are blocking. This is the
    # honest non-acceptance classification (no formal pilot acceptance recorded).
    assert manifest["human_review_decision_count"] == 6
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False

    print("PASS: shipped pilot-region decision packet matches outputs")


if __name__ == "__main__":
    test_pilot_region_decision_rows_surface_current_blockers()
    test_pilot_region_decision_writer_outputs_artifacts()
    test_shipped_pilot_region_decision_packet_matches_current_outputs()
    print("\n=== REALWORLD PILOT REGION DECISION TESTS PASSED ===")
