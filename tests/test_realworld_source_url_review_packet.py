"""Tests for source URL review packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError, URLError

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import src.realworld.source_url_review_packet as source_url_module  # noqa: E402
from src.realworld.source_url_review_packet import (  # noqa: E402
    DEFAULT_SOURCE_URL_REVIEW_MANIFEST_PATH,
    DEFAULT_SOURCE_URL_REVIEW_PACKET_PATH,
    SOURCE_URL_REVIEW_COLUMNS,
    SOURCE_URL_REVIEW_SCOPE,
    UrlCheckResult,
    build_source_url_review_manifest,
    build_source_url_review_rows,
    check_url_reachability,
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


def test_extract_urls_preserves_url_internal_semicolon_and_commas() -> None:
    """URL extraction should keep OSRM-style coordinate separators intact."""

    url = "https://router.project-osrm.org/route/v1/driving/127.1,37.5;127.2,37.6?overview=false"
    urls = extract_urls(f"{url}; https://example.com/terms")

    assert urls == (url, "https://example.com/terms")

    print("PASS: source URL extraction preserves internal URL separators")


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


def test_check_url_reachability_falls_back_from_head_http_error() -> None:
    """HEAD-only HTTP errors should try GET before marking a URL unreachable."""

    class FakeResponse:
        status = 200
        headers = {"content-type": "text/html"}

        def __init__(self, url: str) -> None:
            self._url = url

        def __enter__(self) -> "FakeResponse":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def geturl(self) -> str:
            return self._url

    def fake_urlopen(request: object, timeout: float) -> FakeResponse:
        assert timeout == 2.0
        method = request.get_method()  # type: ignore[attr-defined]
        url = request.full_url  # type: ignore[attr-defined]
        if method == "HEAD":
            raise HTTPError(url, 400, "Bad Request", {}, None)
        assert method == "GET"
        return FakeResponse(url)

    original_urlopen = source_url_module.urlopen
    source_url_module.urlopen = fake_urlopen  # type: ignore[assignment]
    try:
        result = check_url_reachability("https://example.com/source", timeout_sec=2.0)
    finally:
        source_url_module.urlopen = original_urlopen  # type: ignore[assignment]

    assert result.url_status == "reachable"
    assert result.http_status == "200"
    assert "HEAD returned HTTP 400" in result.notes

    print("PASS: source URL reachability falls back from HEAD HTTP errors")


def test_check_url_reachability_falls_back_from_head_network_error() -> None:
    """Sites that reject HEAD at the socket layer should still try GET."""

    class FakeResponse:
        status = 200
        headers = {"content-type": "text/html"}

        def __init__(self, url: str) -> None:
            self._url = url

        def __enter__(self) -> "FakeResponse":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def geturl(self) -> str:
            return self._url

    def fake_urlopen(request: object, timeout: float) -> FakeResponse:
        assert timeout == 2.0
        method = request.get_method()  # type: ignore[attr-defined]
        url = request.full_url  # type: ignore[attr-defined]
        if method == "HEAD":
            raise URLError("fixture connection reset")
        assert method == "GET"
        return FakeResponse(url)

    original_urlopen = source_url_module.urlopen
    source_url_module.urlopen = fake_urlopen  # type: ignore[assignment]
    try:
        result = check_url_reachability("https://example.com/source", timeout_sec=2.0)
    finally:
        source_url_module.urlopen = original_urlopen  # type: ignore[assignment]

    assert result.url_status == "reachable"
    assert result.http_status == "200"
    assert "HEAD network error" in result.notes

    print("PASS: source URL reachability falls back from HEAD network errors")


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


def test_source_url_review_manifest_surfaces_failed_live_rows() -> None:
    """A live-check failure should remain visible in review blockers."""

    rows = [
        {
            "source_id": "fixture_source",
            "check_mode": "live_http",
            "url_status": "network_error",
            "requires_reviewer_confirmation": "true",
        }
    ]

    manifest = build_source_url_review_manifest(
        rows=rows,
        output_path="source_url_review.csv",
        manifest_path="source_url_review_manifest.json",
        doc_path="source_url_review.md",
        provenance_manifest_path="source_provenance_manifest.json",
    )

    assert manifest["unreachable_or_error_count"] == 1
    assert any(
        "network-error URL rows" in blocker
        for blocker in manifest["remaining_blockers"]
    )
    assert any("failed URL rows" in item for item in manifest["review_items"])

    print("PASS: source URL review manifest surfaces failed live rows")


def test_shipped_source_url_review_packet_matches_current_manifest() -> None:
    """Current shipped packet should preserve provenance inputs and non-acceptance."""

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
    assert {row["claim_boundary"] for row in written_rows} == {SOURCE_URL_REVIEW_SCOPE}
    assert all(
        row["can_support_final_provenance_gate"] == "false" for row in written_rows
    )
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["result_scope"] == SOURCE_URL_REVIEW_SCOPE
    assert manifest["provenance_gate_closure_candidate_count"] == 0
    assert manifest["row_count"] == len(rows)
    assert manifest["requires_reviewer_confirmation_count"] == len(rows)
    for row in written_rows:
        if row["url"]:
            assert row["check_mode"] in {"not_checked", "live_http"}
            assert row["url_status"] != "no_url_detected"
        else:
            assert row["check_mode"] == "not_checked"
            assert row["url_status"] == "no_url_detected"

    print("PASS: shipped source URL review packet matches current manifest")


if __name__ == "__main__":
    test_extract_urls_handles_semicolon_separated_citations()
    test_extract_urls_preserves_url_internal_semicolon_and_commas()
    test_source_url_review_rows_are_non_acceptance_rows()
    test_source_url_review_rows_support_injected_live_checker()
    test_check_url_reachability_falls_back_from_head_http_error()
    test_check_url_reachability_falls_back_from_head_network_error()
    test_write_source_url_review_packet_outputs_artifacts()
    test_source_url_review_manifest_surfaces_failed_live_rows()
    test_shipped_source_url_review_packet_matches_current_manifest()
    print("\n=== REALWORLD SOURCE URL REVIEW PACKET TESTS PASSED ===")
