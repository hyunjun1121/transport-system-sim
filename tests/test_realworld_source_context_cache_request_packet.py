"""Tests for source context-cache request packet."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.source_context_cache_request_packet import (  # noqa: E402
    DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_MANIFEST_PATH,
    DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_PACKET_PATH,
    SOURCE_CONTEXT_CACHE_REQUEST_COLUMNS,
    SOURCE_CONTEXT_CACHE_REQUEST_SCOPE,
    build_source_context_cache_request_rows,
    write_source_context_cache_request_packet,
)


def test_context_cache_request_rows_classify_current_context_sources() -> None:
    """Current context-only sources should become cache/exclusion requests."""

    rows = build_source_context_cache_request_rows()
    by_id = {row["source_id"]: row for row in rows}

    assert len(rows) == 3
    assert set(by_id) == {
        "ktdb_public_transport_gtfs_context",
        "seoul_shortest_path_api_context",
        "seoul_timetable_api_context",
    }
    assert by_id["seoul_shortest_path_api_context"]["cache_request_status"] == (
        "blocked_missing_context_source_cache"
    )
    assert "data/rail/pilot_rail_shortest_path_cache.csv" in by_id[
        "seoul_shortest_path_api_context"
    ]["target_cache_artifacts"]
    assert "scripts/fetch_rail_timetable_cache.py" in by_id[
        "seoul_timetable_api_context"
    ]["available_fetch_or_derivation_helpers"]
    assert "scripts/derive_rail_gtfs_evidence.py" in by_id[
        "ktdb_public_transport_gtfs_context"
    ]["available_fetch_or_derivation_helpers"]
    assert "scripts/cache_ktdb_gtfs_source.py" in by_id[
        "ktdb_public_transport_gtfs_context"
    ]["available_fetch_or_derivation_helpers"]
    assert "scripts/cache_ktdb_gtfs_source.py" in by_id[
        "ktdb_public_transport_gtfs_context"
    ]["context_local_artifacts"]
    assert "sensitivity/context-only" in by_id[
        "seoul_shortest_path_api_context"
    ]["required_reviewer_decision"]
    assert "sensitivity/context-only" in by_id[
        "seoul_timetable_api_context"
    ]["required_cache_action"]
    assert "data/rail/ktdb_gtfs_source_extract.csv" in by_id[
        "ktdb_public_transport_gtfs_context"
    ]["context_local_artifacts"]
    assert by_id["ktdb_public_transport_gtfs_context"][
        "target_cache_artifacts_present"
    ] == "false"
    assert {row["target_cache_artifacts_present"] for row in rows} == {"false"}
    assert {row["can_support_final_provenance_gate"] for row in rows} == {"false"}
    assert {row["claim_boundary"] for row in rows} == {
        SOURCE_CONTEXT_CACHE_REQUEST_SCOPE
    }

    print("PASS: source context-cache request rows classify current sources")


def test_context_cache_request_rows_keep_cached_metadata_with_missing_target() -> None:
    """Cached source metadata should not hide a missing target data artifact."""

    rows = build_source_context_cache_request_rows(
        source_priority_rows=[
            {
                "source_id": "ktdb_public_transport_gtfs_context",
                "source_name": "KTDB public transport GTFS dataset candidate",
                "source_type": "public_data",
                "review_status": "cached_snapshot_pending_review",
                "priority_status": "needs_human_review_cached_snapshot_source",
                "review_priority": "high",
                "required_reviewer_decision": (
                    "review source terms, attribution, snapshot date, and retained local artifacts"
                ),
                "url_required_reviewer_actions": "verify retained-snapshot policy",
                "source_url_or_citation": "https://www.ktdb.go.kr/",
                "target_acceptance_artifact": "data/manifests/provenance_acceptance.json",
                "publication_use_status": (
                    "cached source pending license, attribution, and snapshot review"
                ),
                "notes": "metadata snapshot is not a GTFS payload",
            }
        ]
    )

    assert len(rows) == 1
    row = rows[0]
    assert row["source_id"] == "ktdb_public_transport_gtfs_context"
    assert row["cache_request_status"] == "blocked_missing_context_source_cache"
    assert row["target_cache_artifacts_present"] == "false"
    assert "data/rail/pilot_gtfs.zip" in row["target_cache_artifacts"]
    assert "scripts/cache_ktdb_gtfs_source.py" in row[
        "available_fetch_or_derivation_helpers"
    ]
    assert row["required_reviewer_decision"].startswith(
        "cache the target source artifact"
    )
    assert row["publication_use_status"].startswith("target cache missing")

    print("PASS: source context-cache request keeps cached metadata target blockers")


def test_context_cache_request_writer_outputs_artifacts() -> None:
    """Writer should emit stable CSV, manifest, and Markdown artifacts."""

    rows = build_source_context_cache_request_rows()
    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "source_context_cache_requests.csv"
        manifest_path = root / "manifest.json"
        doc_path = root / "source_context_cache_requests.md"
        manifest = write_source_context_cache_request_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == (
                SOURCE_CONTEXT_CACHE_REQUEST_COLUMNS
            )
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        doc_text = doc_path.read_text(encoding="utf-8")

    assert len(written_rows) == len(rows)
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert written_manifest["row_count"] == 3
    assert written_manifest["blocking_request_count"] == 3
    assert written_manifest["missing_target_cache_artifact_count"] == 3
    assert "Source Context Cache Request Packet" in doc_text

    print("PASS: source context-cache request writer emits artifacts")


def test_shipped_context_cache_request_packet_matches_current_outputs() -> None:
    """Committed context-cache request packet should match current priority rows."""

    rows = build_source_context_cache_request_rows()

    assert DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_PACKET_PATH.exists()
    assert DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_MANIFEST_PATH.exists()
    with DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    manifest = json.loads(
        DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_MANIFEST_PATH.read_text(
            encoding="utf-8"
        )
    )

    assert written_rows == rows
    assert manifest["row_count"] == len(rows)
    assert manifest["blocking_request_count"] == 3
    assert manifest["context_source_count"] == 3
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False

    print("PASS: shipped source context-cache request packet matches outputs")


if __name__ == "__main__":
    test_context_cache_request_rows_classify_current_context_sources()
    test_context_cache_request_rows_keep_cached_metadata_with_missing_target()
    test_context_cache_request_writer_outputs_artifacts()
    test_shipped_context_cache_request_packet_matches_current_outputs()
    print("\n=== REALWORLD SOURCE CONTEXT CACHE REQUEST TESTS PASSED ===")
