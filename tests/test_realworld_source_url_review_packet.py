"""Tests for source URL review packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.source_url_review_packet import (  # noqa: E402
    DEFAULT_SOURCE_URL_REVIEW_MANIFEST_PATH,
    DEFAULT_SOURCE_URL_REVIEW_PACKET_PATH,
    SOURCE_URL_REVIEW_COLUMNS,
    SOURCE_URL_REVIEW_SCOPE,
    UrlCheckResult,
    build_source_url_review_rows,
    extract_urls,
    write_source_url_review_packet,
)


def test_extract_urls_handles_semicolon_separated_citations() -> None:
    """URL extraction should preserve order and remove duplicates."""

    urls = extract_urls(
        "https://example.com/a; https://example.org/b, https://example.com/a"
    )

    assert urls == ("https://example.com/a", "https://example.org/b")

    print("PASS: source URL extraction handles citation separators")


def test_source_url_review_rows_are_non_acceptance_rows() -> None:
    """Rows should turn source citations into concrete URL-review actions."""

    rows = build_source_url_review_rows()
    by_source = {}
    for row in rows:
        by_source.setdefault(row["source_id"], []).append(row)

    assert len(rows) >= 10
    assert len(by_source["osm_overpass_road_snapshot"]) == 2
    assert by_source["osm_overpass_road_snapshot"][0]["url"].startswith("https://")
    assert {row["check_mode"] for row in rows} == {"not_checked"}
    assert {row["url_status"] for row in rows} == {"no_url_detected", "not_checked"}
    assert {row["claim_boundary"] for row in rows} == {SOURCE_URL_REVIEW_SCOPE}
    assert all(row["can_support_final_provenance_gate"] == "false" for row in rows)

    print("PASS: source URL review rows are non-acceptance rows")


def test_source_url_review_rows_support_injected_live_checker() -> None:
    """Live checking behavior should be testable without network access."""

    def checker(url: str, timeout_sec: float) -> UrlCheckResult:
        assert timeout_sec == 1.5
        return UrlCheckResult(
            url_status="reachable",
            http_status="200",
            final_url=url,
            content_type="text/html",
            checked_at="2026-05-04T00:00:00+00:00",
            notes="fixture checker",
        )

    rows = build_source_url_review_rows(
        live_check=True,
        timeout_sec=1.5,
        checker=checker,
    )

    checked_rows = [row for row in rows if row["url"]]

    assert checked_rows
    assert {row["check_mode"] for row in checked_rows} == {"live_http"}
    assert {row["url_status"] for row in checked_rows} == {"reachable"}
    assert {row["http_status"] for row in checked_rows} == {"200"}
    assert {row["check_mode"] for row in rows if not row["url"]} == {"not_checked"}

    print("PASS: source URL review rows support injected live checker")


def test_write_source_url_review_packet_outputs_artifacts() -> None:
    """Writer should emit stable CSV, manifest, and Markdown artifacts."""

    rows = build_source_url_review_rows()

    with TemporaryDirectory() as directory:
        output = Path(directory) / "source_url_review.csv"
        manifest = Path(directory) / "source_url_review_manifest.json"
        doc = Path(directory) / "source_url_review.md"
        value = write_source_url_review_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
            doc_path=doc,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == SOURCE_URL_REVIEW_COLUMNS
        with manifest.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)
        text = doc.read_text(encoding="utf-8")

        assert len(written_rows) == len(rows)
        assert value["publication_ready"] is False
        assert value["can_mark_complete"] is False
        assert written_manifest["row_count"] == len(rows)
        assert written_manifest["provenance_gate_closure_candidate_count"] == 0
        assert "Source URL Review Packet" in text

    print("PASS: source URL review writer emits artifacts")


def test_shipped_source_url_review_packet_matches_current_manifest() -> None:
    """Current shipped packet should match deterministic provenance inputs."""

    rows = build_source_url_review_rows()

    assert DEFAULT_SOURCE_URL_REVIEW_PACKET_PATH.exists()
    assert DEFAULT_SOURCE_URL_REVIEW_MANIFEST_PATH.exists()
    with DEFAULT_SOURCE_URL_REVIEW_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    with DEFAULT_SOURCE_URL_REVIEW_MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)

    assert len(written_rows) == len(rows)
    assert [row["url"] for row in written_rows] == [row["url"] for row in rows]
    assert manifest["publication_ready"] is False
    assert manifest["result_scope"] == SOURCE_URL_REVIEW_SCOPE

    print("PASS: shipped source URL review packet matches current manifest")


if __name__ == "__main__":
    test_extract_urls_handles_semicolon_separated_citations()
    test_source_url_review_rows_are_non_acceptance_rows()
    test_source_url_review_rows_support_injected_live_checker()
    test_write_source_url_review_packet_outputs_artifacts()
    test_shipped_source_url_review_packet_matches_current_manifest()
    print("\n=== REALWORLD SOURCE URL REVIEW PACKET TESTS PASSED ===")
