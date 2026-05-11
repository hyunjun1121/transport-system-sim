"""Tests for deriving rail evidence from cached static GTFS feeds."""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.rail_evidence import (  # noqa: E402
    load_rail_service_evidence,
    summarize_rail_service_evidence,
)
from src.realworld.rail_gtfs import (  # noqa: E402
    GtfsEvidenceDerivationConfig,
    derive_rail_service_evidence_from_gtfs,
    file_sha256,
    load_cached_gtfs_feed,
)
from src.realworld.rail_timetable import write_rail_service_evidence  # noqa: E402


def assert_raises_value_error(func, expected_message: str) -> None:
    """Assert that a zero-argument function raises ValueError with context."""

    try:
        func()
    except ValueError as exc:
        message = str(exc)
        assert expected_message in message, message
        return
    raise AssertionError("expected ValueError")


def test_cached_gtfs_zip_derives_publication_ready_timing_evidence() -> None:
    """A cached GTFS zip can produce a validated rail-service evidence row."""

    with TemporaryDirectory() as tmp:
        gtfs_zip = Path(tmp) / "feed.zip"
        output_path = Path(tmp) / "rail_service_evidence.csv"
        _write_gtfs_zip(gtfs_zip)

        feed = load_cached_gtfs_feed(gtfs_zip)
        record = derive_rail_service_evidence_from_gtfs(
            feed,
            _config(gtfs_zip),
        )
        write_rail_service_evidence([record], output_path)
        loaded = load_rail_service_evidence(output_path)
        summary = summarize_rail_service_evidence(loaded)

        assert record.source_status == "cached_gtfs_derived"
        assert record.access_station_name == "Olympic Park"
        assert record.egress_station_name == "Jamsil"
        assert record.headway_min == 10.0
        assert record.travel_time_min == 12.0
        assert record.derived_field_set == frozenset({"headway", "travel_time"})
        assert record.source_artifact_sha256 == file_sha256(gtfs_zip)
        assert summary["publication_ready"] is True
        assert summary["source_artifact_ready"] is True

    print("PASS: cached GTFS zip derives publication-ready timing evidence")


def test_gtfs_route_filter_blocks_wrong_route() -> None:
    """A route filter with no matching trips should fail clearly."""

    with TemporaryDirectory() as tmp:
        gtfs_zip = Path(tmp) / "feed.zip"
        _write_gtfs_zip(gtfs_zip)
        feed = load_cached_gtfs_feed(gtfs_zip)
        config = _config(gtfs_zip, route_id="wrong_route")

        assert_raises_value_error(
            lambda: derive_rail_service_evidence_from_gtfs(feed, config),
            "no GTFS trips match",
        )

    print("PASS: GTFS route filter blocks wrong route")


def test_gtfs_stop_sequence_must_reach_egress_after_access() -> None:
    """Trips where the egress stop comes before access should not certify travel."""

    with TemporaryDirectory() as tmp:
        gtfs_zip = Path(tmp) / "feed.zip"
        _write_gtfs_zip(gtfs_zip, reversed_sequence=True)
        feed = load_cached_gtfs_feed(gtfs_zip)

        assert_raises_value_error(
            lambda: derive_rail_service_evidence_from_gtfs(feed, _config(gtfs_zip)),
            "access and egress stops in sequence",
        )

    print("PASS: GTFS stop sequence must reach egress after access")


def test_gtfs_zip_requires_required_files() -> None:
    """Missing GTFS core files should fail before derivation."""

    with TemporaryDirectory() as tmp:
        gtfs_zip = Path(tmp) / "feed.zip"
        with zipfile.ZipFile(gtfs_zip, "w") as archive:
            archive.writestr("stops.txt", "stop_id,stop_name\nS,Access\n")

        assert_raises_value_error(
            lambda: load_cached_gtfs_feed(gtfs_zip),
            "missing required GTFS files",
        )

    print("PASS: GTFS zip requires required files")


def _config(
    gtfs_zip: Path,
    *,
    route_id: str = "line9",
) -> GtfsEvidenceDerivationConfig:
    return GtfsEvidenceDerivationConfig(
        evidence_id="fixture_gtfs",
        region_id="songpa_public_demo",
        access_point="S",
        egress_point="R",
        access_stop_id="S",
        egress_stop_id="R",
        source_name="fixture cached GTFS",
        source_url_or_citation="fixture",
        extraction_date="2026-05-04",
        capacity_pax_per_train=500,
        service_window="weekday 08:00-08:30",
        route_id=route_id,
        service_ids=("weekday",),
        direction_id="0",
        source_artifact_path=str(gtfs_zip),
        source_artifact_sha256=file_sha256(gtfs_zip),
    )


def _write_gtfs_zip(path: Path, *, reversed_sequence: bool = False) -> None:
    rows_by_file = {
        "stops.txt": [
            {"stop_id": "S", "stop_name": "Olympic Park"},
            {"stop_id": "R", "stop_name": "Jamsil"},
        ],
        "trips.txt": [
            {
                "route_id": "line9",
                "service_id": "weekday",
                "trip_id": f"trip_{index}",
                "direction_id": "0",
            }
            for index in range(3)
        ],
        "stop_times.txt": _stop_time_rows(reversed_sequence=reversed_sequence),
    }
    with zipfile.ZipFile(path, "w") as archive:
        for filename, rows in rows_by_file.items():
            archive.writestr(filename, _csv_text(rows))


def _stop_time_rows(*, reversed_sequence: bool) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for index, minute in enumerate((0, 10, 20)):
        trip_id = f"trip_{index}"
        access_sequence = 2 if reversed_sequence else 1
        egress_sequence = 1 if reversed_sequence else 2
        rows.extend(
            [
                {
                    "trip_id": trip_id,
                    "arrival_time": f"08:{minute:02d}:00",
                    "departure_time": f"08:{minute:02d}:00",
                    "stop_id": "S",
                    "stop_sequence": str(access_sequence),
                },
                {
                    "trip_id": trip_id,
                    "arrival_time": f"08:{minute + 12:02d}:00",
                    "departure_time": f"08:{minute + 12:02d}:00",
                    "stop_id": "R",
                    "stop_sequence": str(egress_sequence),
                },
            ]
        )
    return rows


def _csv_text(rows: list[dict[str, str]]) -> str:
    if not rows:
        return ""
    from io import StringIO

    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


if __name__ == "__main__":
    test_cached_gtfs_zip_derives_publication_ready_timing_evidence()
    test_gtfs_route_filter_blocks_wrong_route()
    test_gtfs_stop_sequence_must_reach_egress_after_access()
    test_gtfs_zip_requires_required_files()
    print("\n=== REALWORLD RAIL GTFS TESTS PASSED ===")
