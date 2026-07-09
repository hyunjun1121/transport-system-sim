"""Tests for source context-cache decision packet."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.source_context_cache_decision_packet import (  # noqa: E402
    DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_MANIFEST_PATH,
    DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_PACKET_PATH,
    SOURCE_CONTEXT_CACHE_DECISION_COLUMNS,
    SOURCE_CONTEXT_CACHE_DECISION_SCOPE,
    build_source_context_cache_decision_rows,
    write_source_context_cache_decision_packet,
)


def test_context_cache_decision_rows_classify_current_context_sources() -> None:
    """Current context-only sources should become pending decision rows."""

    rows = build_source_context_cache_decision_rows()
    by_id = {row["source_id"]: row for row in rows}

    assert len(rows) == 3
    assert set(by_id) == {
        "ktdb_public_transport_gtfs_context",
        "seoul_shortest_path_api_context",
        "seoul_timetable_api_context",
    }
    assert {row["decision_status"] for row in rows} == {
        "blocked_missing_context_source_cache_retention_or_exclusion_decision"
    }
    assert {row["provisional_decision"] for row in rows} == {
        "pending_reviewer_decision"
    }
    assert "cache_reviewed_extract" in by_id[
        "seoul_timetable_api_context"
    ]["candidate_decision_options"]
    assert "exclude_from_release_scope_claims" in by_id[
        "ktdb_public_transport_gtfs_context"
    ]["candidate_decision_options"]
    assert "retain_as_sensitivity_or_context_only" in by_id[
        "seoul_shortest_path_api_context"
    ]["candidate_decision_options"]
    assert "sha256_or_digest_if_cached" in by_id[
        "seoul_shortest_path_api_context"
    ]["required_evidence_fields"]
    assert "data/rail/ktdb_gtfs_source_extract.csv" in by_id[
        "ktdb_public_transport_gtfs_context"
    ]["evidence_input_paths"]
    assert "scripts/cache_ktdb_gtfs_source.py" in by_id[
        "ktdb_public_transport_gtfs_context"
    ]["evidence_input_paths"]
    assert "docs/schemas/rail_shortest_path_cache_schema.md" in by_id[
        "seoul_shortest_path_api_context"
    ]["evidence_input_paths"]
    assert "docs/schemas/rail_timetable_cache_schema.md" in by_id[
        "seoul_timetable_api_context"
    ]["evidence_input_paths"]
    assert {row["can_support_final_provenance_gate"] for row in rows} == {"false"}
    assert {row["claim_boundary"] for row in rows} == {
        SOURCE_CONTEXT_CACHE_DECISION_SCOPE
    }

    print("PASS: source context-cache decision rows classify current sources")


def test_context_cache_decision_writer_outputs_artifacts() -> None:
    """Writer should emit stable CSV, manifest, and Markdown artifacts."""

    rows = build_source_context_cache_decision_rows()
    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "source_context_cache_decision.csv"
        manifest_path = root / "manifest.json"
        doc_path = root / "source_context_cache_decision.md"
        manifest = write_source_context_cache_decision_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == (
                SOURCE_CONTEXT_CACHE_DECISION_COLUMNS
            )
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        doc_text = doc_path.read_text(encoding="utf-8")

    assert len(written_rows) == len(rows)
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert written_manifest["row_count"] == 3
    assert written_manifest["blocking_decision_count"] == 3
    assert written_manifest["human_review_decision_count"] == 0
    assert written_manifest["provenance_gate_closure_candidate_count"] == 0
    assert "Source Context Cache Decision Packet" in doc_text

    print("PASS: source context-cache decision writer emits artifacts")


def test_shipped_context_cache_decision_packet_matches_current_outputs() -> None:
    """Committed decision packet should match current request rows."""

    rows = build_source_context_cache_decision_rows()

    assert DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_PACKET_PATH.exists()
    assert DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_MANIFEST_PATH.exists()
    with DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    manifest = json.loads(
        DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_MANIFEST_PATH.read_text(
            encoding="utf-8"
        )
    )

    assert written_rows == rows
    assert manifest["row_count"] == len(rows)
    assert manifest["blocking_decision_count"] == 3
    assert manifest["cache_retention_or_exclusion_decision_recorded"] is False
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False

    print("PASS: shipped source context-cache decision packet matches outputs")


if __name__ == "__main__":
    test_context_cache_decision_rows_classify_current_context_sources()
    test_context_cache_decision_writer_outputs_artifacts()
    test_shipped_context_cache_decision_packet_matches_current_outputs()
    print("\n=== REALWORLD SOURCE CONTEXT CACHE DECISION TESTS PASSED ===")
