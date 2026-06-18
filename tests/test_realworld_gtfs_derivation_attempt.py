"""Tests for the cached-GTFS derivation attempt manifest."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.record_gtfs_derivation_attempt import build_attempt_manifest  # noqa: E402


MANIFEST_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "rail"
    / "gtfs_derivation_attempt_manifest.json"
)
KTDB_EXTRACT_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "rail"
    / "ktdb_gtfs_source_extract.csv"
)


def test_shipped_manifest_records_feed_absent() -> None:
    """The shipped manifest documents an honest 'feed absent' result."""

    assert MANIFEST_PATH.is_file(), f"missing manifest at {MANIFEST_PATH}"
    with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)

    assert manifest["schema_version"] == 1
    assert manifest["input_is_gtfs_feed"] is False
    assert manifest["input_path"] == "data/rail/ktdb_gtfs_source_extract.csv"
    assert manifest["input_sha256"]
    assert manifest["gtfs_feed_files_present"] == []
    assert "metadata only" in manifest["conclusion"]
    assert "not a GTFS feed" in manifest["conclusion"]
    assert manifest["failure_reason"]
    assert manifest["can_close_rail_evidence_gate"] is False
    assert manifest["publication_ready"] is False
    assert "not rail timing evidence" in manifest["claim_boundary"]

    print("PASS: shipped GTFS attempt manifest records feed absent")


def test_attempt_manifest_matches_cached_extract() -> None:
    """The manifest SHA256 matches the current cached KTDB extract."""

    assert KTDB_EXTRACT_PATH.is_file()
    manifest = build_attempt_manifest(KTDB_EXTRACT_PATH)
    assert manifest["input_is_gtfs_feed"] is False
    assert manifest["gtfs_feed_files_present"] == []
    assert manifest["failure_reason"]

    from src.realworld.source_artifacts import file_sha256

    assert manifest["input_sha256"] == file_sha256(KTDB_EXTRACT_PATH)

    print("PASS: GTFS attempt manifest matches cached extract")


def test_attempt_manifest_on_real_feed_succeeds(tmp_path: Path) -> None:
    """A directory with all required GTFS files is classified as a feed."""

    import zipfile

    gtfs_zip = tmp_path / "feed.zip"
    with zipfile.ZipFile(gtfs_zip, "w") as archive:
        archive.writestr("stops.txt", "stop_id,stop_name\nS,Access\n")
        archive.writestr("trips.txt", "trip_id,route_id,service_id\nt1,r1,s1\n")
        archive.writestr(
            "stop_times.txt",
            "trip_id,arrival_time,departure_time,stop_id,stop_sequence\n"
            "t1,08:00:00,08:00:00,S,1\n",
        )

    manifest = build_attempt_manifest(gtfs_zip)
    assert manifest["input_is_gtfs_feed"] is True
    assert manifest["failure_reason"] == ""
    assert sorted(manifest["gtfs_feed_files_present"]) == [
        "stop_times.txt",
        "stops.txt",
        "trips.txt",
    ]

    print("PASS: GTFS attempt manifest classifies real feed correctly")


if __name__ == "__main__":
    from tempfile import TemporaryDirectory

    test_shipped_manifest_records_feed_absent()
    test_attempt_manifest_matches_cached_extract()
    with TemporaryDirectory() as tmp:
        test_attempt_manifest_on_real_feed_succeeds(Path(tmp))
    print("\n=== REALWORLD GTFS DERIVATION ATTEMPT TESTS PASSED ===")
