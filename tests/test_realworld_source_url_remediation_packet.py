"""Tests for source-URL remediation packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.source_url_remediation_packet import (  # noqa: E402
    DEFAULT_SOURCE_URL_REMEDIATION_MANIFEST_PATH,
    DEFAULT_SOURCE_URL_REMEDIATION_PACKET_PATH,
    SOURCE_URL_REMEDIATION_COLUMNS,
    SOURCE_URL_REMEDIATION_SCOPE,
    build_source_url_remediation_rows,
    write_source_url_remediation_packet,
)


def test_source_url_remediation_rows_classify_review_actions() -> None:
    """URL statuses should become concrete non-acceptance remediation rows."""

    rows = build_source_url_remediation_rows(
        url_rows=[
            _url_row("osm", "public_map", "reachable"),
            _url_row("api", "public_api", "http_error"),
            _url_row(
                "api_with_alt",
                "public_api",
                "reachable",
                url="https://example.com/reachable",
            ),
            _url_row(
                "api_with_alt",
                "public_api",
                "network_error",
                url="https://example.com/stale",
            ),
            _url_row("repo", "repository_input", "no_url_detected", url=""),
            _url_row("api_unchecked", "public_api", "not_checked"),
        ]
    )
    by_id = {row["source_id"]: row for row in rows}

    assert by_id["osm"]["remediation_status"] == "reachable_needs_license_review"
    assert by_id["api"]["remediation_status"] == "blocked_unreachable_or_http_error"
    assert by_id["api_with_alt"]["remediation_status"] in {
        "reachable_needs_license_review",
        "alternate_reachable_url_needs_review",
    }
    assert any(
        row["source_id"] == "api_with_alt"
        and row["remediation_status"] == "alternate_reachable_url_needs_review"
        and row["alternate_url_candidates"] == "https://example.com/reachable"
        for row in rows
    )
    assert all(
        row["alternate_url_candidates"] == ""
        for row in rows
        if row["source_id"] != "api_with_alt"
        or row["remediation_status"] != "alternate_reachable_url_needs_review"
    )
    assert by_id["repo"]["remediation_status"] == "local_citation_needs_review"
    assert by_id["api_unchecked"]["remediation_status"] == "live_check_required"
    assert {row["claim_boundary"] for row in rows} == {SOURCE_URL_REMEDIATION_SCOPE}
    assert all(row["can_support_final_provenance_gate"] == "false" for row in rows)

    print("PASS: source-URL remediation rows classify review actions")


def test_write_source_url_remediation_packet_outputs_artifacts() -> None:
    """Writer should emit stable CSV, manifest, and Markdown artifacts."""

    rows = build_source_url_remediation_rows(
        url_rows=[
            _url_row("osm", "public_map", "reachable"),
            _url_row("api", "public_api", "network_error"),
        ]
    )

    with TemporaryDirectory() as directory:
        output = Path(directory) / "source_url_remediation.csv"
        manifest = Path(directory) / "source_url_remediation_manifest.json"
        doc = Path(directory) / "source_url_remediation.md"
        value = write_source_url_remediation_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
            doc_path=doc,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == SOURCE_URL_REMEDIATION_COLUMNS
        with manifest.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)
        text = doc.read_text(encoding="utf-8")

        assert len(written_rows) == len(rows)
        assert value["publication_ready"] is False
        assert value["can_mark_complete"] is False
        assert value["blocking_issue_count"] == 1
        assert value["alternate_candidate_row_count"] == 0
        assert any("blocked URL rows" in item for item in value["remaining_blockers"])
        assert any("sensitivity/context-only" in item for item in value["review_items"])
        assert written_manifest["provenance_gate_closure_candidate_count"] == 0
        assert "Source URL Remediation Packet" in text

    print("PASS: source-URL remediation writer emits artifacts")


def test_shipped_source_url_remediation_packet_matches_current_review_packet() -> None:
    """Current shipped remediation packet should stay non-accepting."""

    rows = build_source_url_remediation_rows()

    assert DEFAULT_SOURCE_URL_REMEDIATION_PACKET_PATH.exists()
    assert DEFAULT_SOURCE_URL_REMEDIATION_MANIFEST_PATH.exists()
    with DEFAULT_SOURCE_URL_REMEDIATION_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    with DEFAULT_SOURCE_URL_REMEDIATION_MANIFEST_PATH.open(
        "r",
        encoding="utf-8",
    ) as handle:
        manifest = json.load(handle)

    assert len(written_rows) == len(rows)
    assert [row["source_id"] for row in written_rows] == [
        row["source_id"] for row in rows
    ]
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["result_scope"] == SOURCE_URL_REMEDIATION_SCOPE
    assert manifest["provenance_gate_closure_candidate_count"] == 0
    assert manifest["alternate_candidate_row_count"] >= 0
    assert any("sensitivity/context-only" in item for item in manifest["review_items"])
    if manifest["blocking_issue_count"] == 0 and manifest["live_check_required_count"] == 0:
        assert not any(
            "unreachable" in item or "network-error" in item or "not-checked" in item
            for item in manifest["remaining_blockers"]
        )

    print("PASS: shipped source-URL remediation packet matches current review packet")


def _url_row(
    source_id: str,
    source_type: str,
    url_status: str,
    *,
    url: str = "https://example.com/source",
) -> dict[str, str]:
    return {
        "source_id": source_id,
        "source_name": source_id,
        "source_type": source_type,
        "url": url,
        "url_status": url_status,
        "http_status": "200" if url_status == "reachable" else "",
        "notes": "fixture",
    }


if __name__ == "__main__":
    test_source_url_remediation_rows_classify_review_actions()
    test_write_source_url_remediation_packet_outputs_artifacts()
    test_shipped_source_url_remediation_packet_matches_current_review_packet()
    print("\n=== REALWORLD SOURCE URL REMEDIATION PACKET TESTS PASSED ===")
