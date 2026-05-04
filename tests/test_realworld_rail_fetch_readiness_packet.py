"""Tests for rail fetch-readiness packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.rail_fetch_readiness_packet import (  # noqa: E402
    DEFAULT_RAIL_FETCH_READINESS_MANIFEST_PATH,
    DEFAULT_RAIL_FETCH_READINESS_PACKET_PATH,
    RAIL_FETCH_READINESS_COLUMNS,
    RAIL_FETCH_READINESS_SCOPE,
    build_rail_fetch_readiness_rows,
    write_rail_fetch_readiness_packet,
)


def test_rail_fetch_readiness_rows_classify_blockers() -> None:
    """Rail source requests should become concrete preflight statuses."""

    rows = build_rail_fetch_readiness_rows(
        request_rows=[
            _request("api", "public_api_key_required", "data/rail/missing.csv"),
            _request("gtfs", "reviewed_static_gtfs_file_required", "data/rail/missing_gtfs.zip"),
            _request(
                "capacity",
                "operator_or_literature_or_sensitivity_decision",
                "data/parameters/rail_assumptions.csv",
            ),
        ],
        env={},
    )
    by_id = {row["request_id"]: row for row in rows}

    assert by_id["api"]["readiness_status"] == "blocked_missing_data_go_kr_key"
    assert by_id["gtfs"]["readiness_status"] == "blocked_missing_reviewed_gtfs_file"
    assert by_id["capacity"]["readiness_status"] == (
        "needs_human_review_capacity_treatment"
    )
    assert {row["claim_boundary"] for row in rows} == {RAIL_FETCH_READINESS_SCOPE}
    assert all(row["can_support_rail_evidence_gate"] == "false" for row in rows)

    print("PASS: rail fetch-readiness rows classify blockers")


def test_rail_fetch_readiness_rows_notice_api_key() -> None:
    """API rows should move to reviewed-fetch readiness when a key is supplied."""

    rows = build_rail_fetch_readiness_rows(
        request_rows=[
            _request("api", "public_api_key_required", "data/rail/missing.csv"),
        ],
        env={"DATA_GO_KR_KEY": "fixture-key"},
    )

    assert rows[0]["readiness_status"] == "ready_for_reviewed_live_api_fetch"
    assert rows[0]["data_go_kr_key_present"] == "true"

    print("PASS: rail fetch-readiness rows notice API key")


def test_write_rail_fetch_readiness_packet_outputs_artifacts() -> None:
    """Writer should emit CSV, manifest, and Markdown artifacts."""

    rows = build_rail_fetch_readiness_rows(
        request_rows=[
            _request("api", "public_api_key_required", "data/rail/missing.csv"),
            _request(
                "availability",
                "scenario_or_public_disruption_source_required",
                "data/scenarios/disruption_scenarios.csv",
            ),
        ],
        env={},
    )

    with TemporaryDirectory() as directory:
        output = Path(directory) / "rail_fetch_readiness.csv"
        manifest = Path(directory) / "rail_fetch_readiness_manifest.json"
        doc = Path(directory) / "rail_fetch_readiness.md"
        value = write_rail_fetch_readiness_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
            doc_path=doc,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == RAIL_FETCH_READINESS_COLUMNS
        with manifest.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)
        text = doc.read_text(encoding="utf-8")

        assert len(written_rows) == len(rows)
        assert value["publication_ready"] is False
        assert value["can_mark_complete"] is False
        assert written_manifest["rail_evidence_gate_closure_candidate_count"] == 0
        assert "Rail Fetch Readiness Packet" in text

    print("PASS: rail fetch-readiness writer emits artifacts")


def test_shipped_rail_fetch_readiness_packet_matches_current_requests() -> None:
    """Current shipped readiness packet should stay non-accepting."""

    rows = build_rail_fetch_readiness_rows()

    assert DEFAULT_RAIL_FETCH_READINESS_PACKET_PATH.exists()
    assert DEFAULT_RAIL_FETCH_READINESS_MANIFEST_PATH.exists()
    with DEFAULT_RAIL_FETCH_READINESS_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    with DEFAULT_RAIL_FETCH_READINESS_MANIFEST_PATH.open(
        "r",
        encoding="utf-8",
    ) as handle:
        manifest = json.load(handle)

    assert len(written_rows) == len(rows)
    assert [row["request_id"] for row in written_rows] == [
        row["request_id"] for row in rows
    ]
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["result_scope"] == RAIL_FETCH_READINESS_SCOPE
    assert manifest["rail_evidence_gate_closure_candidate_count"] == 0

    print("PASS: shipped rail fetch-readiness packet matches current requests")


def _request(request_id: str, source_type: str, cache_path: str) -> dict[str, str]:
    return {
        "request_id": request_id,
        "region_id": "songpa_public_demo",
        "evidence_fields": "headway",
        "source_type": source_type,
        "source_name": request_id,
        "source_cache_path": cache_path,
        "raw_payload_path": "data/rail/missing_raw.json",
        "fetch_command": "fixture fetch",
        "derive_command": "fixture derive",
        "notes": "fixture",
    }


if __name__ == "__main__":
    test_rail_fetch_readiness_rows_classify_blockers()
    test_rail_fetch_readiness_rows_notice_api_key()
    test_write_rail_fetch_readiness_packet_outputs_artifacts()
    test_shipped_rail_fetch_readiness_packet_matches_current_requests()
    print("\n=== REALWORLD RAIL FETCH READINESS PACKET TESTS PASSED ===")
