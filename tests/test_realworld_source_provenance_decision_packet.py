"""Tests for source-provenance decision packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.source_provenance_decision_packet import (  # noqa: E402
    DEFAULT_SOURCE_PROVENANCE_DECISION_MANIFEST_PATH,
    DEFAULT_SOURCE_PROVENANCE_DECISION_PACKET_PATH,
    SOURCE_PROVENANCE_DECISION_COLUMNS,
    SOURCE_PROVENANCE_DECISION_SCOPE,
    build_source_provenance_decision_rows,
    write_source_provenance_decision_packet,
)


def test_source_provenance_decision_rows_surface_current_blockers() -> None:
    """Current source-provenance decision rows should expose gate blockers."""

    rows = build_source_provenance_decision_rows()
    by_id = {row["decision_id"]: row for row in rows}

    assert len(rows) == 7
    assert by_id["source_inventory_review_decision"]["decision_status"] == (
        "needs_human_review_source_inventory"
    )
    assert "source_record_count=11" in by_id["source_inventory_review_decision"][
        "current_evidence"
    ]
    assert by_id["license_attribution_decision"]["decision_status"] == (
        "needs_human_review_license_attribution"
    )
    assert "review_required_count=11" in by_id["license_attribution_decision"][
        "current_evidence"
    ]
    assert by_id["context_source_cache_or_exclusion_decision"][
        "decision_status"
    ] == "blocked_missing_context_cache_or_exclusion_decisions"
    assert by_id["url_remediation_decision"]["decision_status"] == (
        "needs_human_review_url_remediation"
    )
    assert by_id["cached_snapshot_repository_scope_decision"][
        "decision_status"
    ] == "needs_human_review_cached_snapshot_and_repository_scope"
    assert by_id["reproducibility_source_scope_decision"]["decision_status"] == (
        "blocked_scaffold_reproducibility_manifest_scope"
    )
    assert by_id["formal_provenance_acceptance_boundary"]["decision_status"] == (
        "blocked_missing_provenance_acceptance_record"
    )
    assert {row["claim_boundary"] for row in rows} == {
        SOURCE_PROVENANCE_DECISION_SCOPE
    }
    assert all(row["can_support_provenance_acceptance"] == "false" for row in rows)

    print("PASS: source-provenance decision rows surface current blockers")


def test_source_provenance_decision_writer_outputs_artifacts() -> None:
    """Writer should emit CSV, manifest, and Markdown artifacts."""

    rows = build_source_provenance_decision_rows()
    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "source_provenance_decision.csv"
        manifest_path = root / "source_provenance_decision_manifest.json"
        doc_path = root / "source_provenance_decision.md"
        manifest = write_source_provenance_decision_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == (
                SOURCE_PROVENANCE_DECISION_COLUMNS
            )
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        doc_text = doc_path.read_text(encoding="utf-8")

    assert len(written_rows) == len(rows)
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["provenance_decision_recorded"] is False
    assert manifest["provenance_gate_closure_candidate_count"] == 0
    assert written_manifest["blocking_decision_count"] == 3
    assert written_manifest["human_review_decision_count"] == 4
    assert "Source Provenance Decision Packet" in doc_text
    assert "It does not certify licenses" in doc_text

    print("PASS: source-provenance decision writer emits artifacts")


def test_shipped_source_provenance_decision_packet_matches_current_outputs() -> None:
    """Committed source-provenance decision packet should match current outputs."""

    rows = build_source_provenance_decision_rows()

    assert DEFAULT_SOURCE_PROVENANCE_DECISION_PACKET_PATH.exists()
    assert DEFAULT_SOURCE_PROVENANCE_DECISION_MANIFEST_PATH.exists()
    with DEFAULT_SOURCE_PROVENANCE_DECISION_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    manifest = json.loads(
        DEFAULT_SOURCE_PROVENANCE_DECISION_MANIFEST_PATH.read_text(
            encoding="utf-8"
        )
    )

    assert len(written_rows) == len(rows)
    assert [row["decision_id"] for row in written_rows] == [
        row["decision_id"] for row in rows
    ]
    assert manifest["row_count"] == 7
    assert manifest["blocking_decision_count"] == 3
    assert manifest["human_review_decision_count"] == 4
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False

    print("PASS: shipped source-provenance decision packet matches outputs")


if __name__ == "__main__":
    test_source_provenance_decision_rows_surface_current_blockers()
    test_source_provenance_decision_writer_outputs_artifacts()
    test_shipped_source_provenance_decision_packet_matches_current_outputs()
    print("\n=== REALWORLD SOURCE PROVENANCE DECISION TESTS PASSED ===")
