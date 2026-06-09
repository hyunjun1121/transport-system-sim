"""Tests for Metro 9 rolling-stock source extraction."""

from __future__ import annotations

import csv
import hashlib
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.metro9_capacity_source import (  # noqa: E402
    DEFAULT_METRO9_CAPACITY_URL,
    METRO9_CAPACITY_COLUMNS,
    METRO9_CAPACITY_SOURCE_SCOPE,
    audit_metro9_capacity_raw_hash,
    build_metro9_capacity_extract,
    load_metro9_capacity_extract,
    write_metro9_capacity_cache,
)


FIXTURE_HTML = """
<html>
  <head><title>Overview and Characteristics</title></head>
  <body>
    <h1>Overview and Characteristics</h1>
    <p>Configuration 6 Cars / 1 Train Set(Normal Train/Express Train)</p>
    <p>Max Running Speed 80km/h</p>
    <p>Number of Cars 318 Cars(53 Train Sets of 6 Cars)</p>
    <p>Manufacturer Hyundai Rotem</p>
    <h2>Specifications</h2>
    <p>Width : 3,120mm Length : 19,500mm Height : 4,010mm</p>
    <p>Track Gage : 1.435mm Seats : 306(6 cars) Standing : 616(6 cars)</p>
    <p>Total Capacity : 922(6 cars)</p>
    <h2>System Performance</h2>
    <p>Max. Speed : 100km/h Max. Running Speed : 80km/h</p>
  </body>
</html>
"""


def test_metro9_capacity_extract_parses_official_page_fields() -> None:
    """Fixture page fields should become a conservative source-review row."""

    row = build_metro9_capacity_extract(
        FIXTURE_HTML,
        source_url=DEFAULT_METRO9_CAPACITY_URL,
        fetched_at_utc="2026-05-08T00:00:00+00:00",
    )

    assert row["source_id"] == "metro9_capacity_context"
    assert row["configuration"] == "6 Cars / 1 Train Set(Normal Train/Express Train)"
    assert row["max_running_speed_kmh_overview"] == "80"
    assert row["number_of_cars"] == "318"
    assert row["train_sets"] == "53"
    assert row["manufacturer"] == "Hyundai Rotem"
    assert row["width_mm"] == "3120"
    assert row["length_mm"] == "19500"
    assert row["height_mm"] == "4010"
    assert row["track_gauge_mm"] == "1435"
    assert row["seats_6_cars"] == "306"
    assert row["standing_6_cars"] == "616"
    assert row["total_capacity_6_cars"] == "922"
    assert row["max_speed_kmh_system_performance"] == "100"
    assert row["review_status"] == "cached_operator_page_pending_review"
    assert row["claim_boundary"] == METRO9_CAPACITY_SOURCE_SCOPE

    print("PASS: Metro 9 capacity source fields are parsed")


def test_metro9_capacity_cache_writes_raw_and_extract() -> None:
    """Writer should preserve raw HTML and validate the extract CSV."""

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        raw_path = root / "raw.html"
        extract_path = root / "extract.csv"
        row = write_metro9_capacity_cache(
            html_text=FIXTURE_HTML,
            raw_output_path=raw_path,
            extract_output_path=extract_path,
            fetched_at_utc="2026-05-08T00:00:00+00:00",
        )
        loaded = load_metro9_capacity_extract(extract_path)

        assert raw_path.read_text(encoding="utf-8") == FIXTURE_HTML
        assert row["raw_file_sha256"] == hashlib.sha256(
            raw_path.read_bytes()
        ).hexdigest()
        assert len(loaded) == 1
        assert loaded[0]["total_capacity_6_cars"] == row["total_capacity_6_cars"]
        with extract_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            assert tuple(reader.fieldnames or ()) == METRO9_CAPACITY_COLUMNS
        audit = audit_metro9_capacity_raw_hash(
            extract_path=extract_path,
            raw_path=raw_path,
        )

    assert audit["raw_file_integrity_ready"] is True
    assert audit["publication_ready"] is False
    assert audit["can_mark_complete"] is False

    print("PASS: Metro 9 capacity cache writes raw page and extract")


def test_metro9_capacity_raw_hash_audit_detects_mismatch() -> None:
    """Raw-file hash audit should fail if the cached HTML changes."""

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        raw_path = root / "raw.html"
        extract_path = root / "extract.csv"
        write_metro9_capacity_cache(
            html_text=FIXTURE_HTML,
            raw_output_path=raw_path,
            extract_output_path=extract_path,
            fetched_at_utc="2026-05-08T00:00:00+00:00",
        )
        raw_path.write_text("changed after extract write", encoding="utf-8")
        audit = audit_metro9_capacity_raw_hash(
            extract_path=extract_path,
            raw_path=raw_path,
        )

    assert audit["raw_file_integrity_ready"] is False
    assert audit["raw_file_sha256_matches"] is False
    assert audit["remaining_blockers"]

    print("PASS: Metro 9 capacity raw hash audit detects mismatch")


if __name__ == "__main__":
    test_metro9_capacity_extract_parses_official_page_fields()
    test_metro9_capacity_cache_writes_raw_and_extract()
    test_metro9_capacity_raw_hash_audit_detects_mismatch()
    print("\n=== REALWORLD METRO9 CAPACITY SOURCE TESTS PASSED ===")
