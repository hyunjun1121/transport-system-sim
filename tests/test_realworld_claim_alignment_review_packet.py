"""Tests for manuscript/report claim-alignment review packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.claim_alignment_review_packet import (  # noqa: E402
    CLAIM_ALIGNMENT_REVIEW_COLUMNS,
    CLAIM_ALIGNMENT_REVIEW_SCOPE,
    DEFAULT_CLAIM_ALIGNMENT_REVIEW_MANIFEST_PATH,
    DEFAULT_CLAIM_ALIGNMENT_REVIEW_PACKET_PATH,
    build_claim_alignment_review_rows,
    write_claim_alignment_review_packet,
)


def test_claim_alignment_rows_find_guardrails_and_claim_candidates() -> None:
    """Rows should detect both guardrail language and review-required claims."""

    rows = build_claim_alignment_review_rows()
    statuses = {row["review_status"] for row in rows}
    sources = {row["source_path"] for row in rows}
    categories = {row["claim_category"] for row in rows}

    assert rows
    assert "paper/paper_draft.md" in sources
    assert "results/realworld_pilot/tables/figure_table_manifest.json" in sources
    assert "guardrail_language" in statuses
    assert "requires_revision_or_acceptance" in statuses
    assert "calibration_claim" in categories
    assert "manuscript_report_alignment" in {
        row["gate_dependency"] for row in rows
    }
    assert all(row["can_support_manuscript_acceptance"] == "false" for row in rows)

    print("PASS: claim alignment rows find guardrails and claim candidates")


def test_write_claim_alignment_review_packet_outputs_artifacts() -> None:
    """Writer should emit stable CSV, manifest, and Markdown review artifacts."""

    rows = build_claim_alignment_review_rows()

    with TemporaryDirectory() as directory:
        output = Path(directory) / "claim_alignment.csv"
        manifest = Path(directory) / "claim_alignment_manifest.json"
        doc = Path(directory) / "claim_alignment.md"
        value = write_claim_alignment_review_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
            doc_path=doc,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == CLAIM_ALIGNMENT_REVIEW_COLUMNS
        with manifest.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)
        text = doc.read_text(encoding="utf-8")

        assert len(written_rows) == len(rows)
        assert value["publication_ready"] is False
        assert value["can_mark_complete"] is False
        assert value["overclaim_candidate_count"] > 0
        assert written_manifest["row_count"] == len(rows)
        assert "Claim Alignment Review Packet" in text

    print("PASS: claim alignment review writer emits artifacts")


def test_shipped_claim_alignment_review_packet_matches_current_inputs() -> None:
    """Current shipped packet should match deterministic manuscript inputs."""

    rows = build_claim_alignment_review_rows()

    assert DEFAULT_CLAIM_ALIGNMENT_REVIEW_PACKET_PATH.exists()
    assert DEFAULT_CLAIM_ALIGNMENT_REVIEW_MANIFEST_PATH.exists()
    with DEFAULT_CLAIM_ALIGNMENT_REVIEW_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    with DEFAULT_CLAIM_ALIGNMENT_REVIEW_MANIFEST_PATH.open(
        "r",
        encoding="utf-8",
    ) as handle:
        manifest = json.load(handle)

    assert len(written_rows) == len(rows)
    assert [row["claim_id"] for row in written_rows] == [
        row["claim_id"] for row in rows
    ]
    assert manifest["publication_ready"] is False
    assert manifest["result_scope"] == CLAIM_ALIGNMENT_REVIEW_SCOPE

    print("PASS: shipped claim alignment review packet matches current inputs")


if __name__ == "__main__":
    test_claim_alignment_rows_find_guardrails_and_claim_candidates()
    test_write_claim_alignment_review_packet_outputs_artifacts()
    test_shipped_claim_alignment_review_packet_matches_current_inputs()
    print("\n=== REALWORLD CLAIM ALIGNMENT REVIEW PACKET TESTS PASSED ===")
