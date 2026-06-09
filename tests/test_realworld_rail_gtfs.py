"""Tests for deriving rail evidence from cached static GTFS feeds."""

from __future__ import annotations

import csv
from dataclasses import replace
import json
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
    summarize_gtfs_validator_report,
    validate_gtfs_validator_report,
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
        validator_report = Path(tmp) / "gtfs_validator_report.json"
        output_path = Path(tmp) / "rail_service_evidence.csv"
        _write_gtfs_zip(gtfs_zip)
        _write_validator_report(
            validator_report,
            {
                "validator": "fixture",
                "source_artifact_sha256": file_sha256(gtfs_zip),
                "errors": 0,
            },
        )

        feed = load_cached_gtfs_feed(gtfs_zip)
        record = derive_rail_service_evidence_from_gtfs(
            feed,
            _config(gtfs_zip, validator_report),
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
        assert record.gtfs_validator_report_sha256 == file_sha256(validator_report)
        assert summary["publication_ready"] is True
        assert summary["source_artifact_ready"] is True
        assert summary["gtfs_validation_ready"] is True

    print("PASS: cached GTFS zip derives publication-ready timing evidence")


def test_gtfs_route_filter_blocks_wrong_route() -> None:
    """A route filter with no matching trips should fail clearly."""

    with TemporaryDirectory() as tmp:
        gtfs_zip = Path(tmp) / "feed.zip"
        _write_gtfs_zip(gtfs_zip)
        feed = load_cached_gtfs_feed(gtfs_zip)
        validator_report = Path(tmp) / "gtfs_validator_report.json"
        _write_validator_report(
            validator_report,
            {
                "validator": "fixture",
                "source_artifact_sha256": file_sha256(gtfs_zip),
                "errors": 0,
            },
        )
        config = _config(gtfs_zip, validator_report, route_id="wrong_route")

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
        validator_report = Path(tmp) / "gtfs_validator_report.json"
        _write_validator_report(
            validator_report,
            {
                "validator": "fixture",
                "source_artifact_sha256": file_sha256(gtfs_zip),
                "errors": 0,
            },
        )

        assert_raises_value_error(
            lambda: derive_rail_service_evidence_from_gtfs(
                feed, _config(gtfs_zip, validator_report)
            ),
            "access and egress stops in sequence",
        )

    print("PASS: GTFS stop sequence must reach egress after access")


def test_gtfs_derivation_requires_validator_report_metadata() -> None:
    """GTFS timing evidence should not be derived without validator metadata."""

    with TemporaryDirectory() as tmp:
        gtfs_zip = Path(tmp) / "feed.zip"
        _write_gtfs_zip(gtfs_zip)
        feed = load_cached_gtfs_feed(gtfs_zip)
        config = _config(gtfs_zip, validator_report=None)

        assert_raises_value_error(
            lambda: derive_rail_service_evidence_from_gtfs(feed, config),
            "gtfs_validator_report_path",
        )

    print("PASS: GTFS derivation requires validator report metadata")


def test_gtfs_validator_summary_counts_report_is_accepted() -> None:
    """Nested validator summary counts should certify zero-error reports."""

    with TemporaryDirectory() as tmp:
        gtfs_zip = Path(tmp) / "feed.zip"
        validator_report = Path(tmp) / "gtfs_validator_report.json"
        _write_gtfs_zip(gtfs_zip)
        _write_validator_report(
            validator_report,
            {
                "source_artifact_sha256": file_sha256(gtfs_zip),
                "validatorVersion": "fixture-validator",
                "summary": {
                    "counts": {
                        "errors": 0,
                        "warnings": 2,
                        "info": 3,
                        "total": 5,
                    }
                },
            },
        )

        summary = summarize_gtfs_validator_report(validator_report)
        record = derive_rail_service_evidence_from_gtfs(
            load_cached_gtfs_feed(gtfs_zip),
            _config(gtfs_zip, validator_report),
        )

        assert summary["error_count"] == 0
        assert summary["warning_count"] == 2
        assert summary["info_count"] == 3
        assert summary["total_notice_count"] == 5
        assert summary["validation_report_ready"] is True
        assert "gtfs_validator_warning_count=2" in record.notes

    print("PASS: GTFS validator summary-counts report is accepted")


def test_gtfs_validator_error_count_blocks_derivation() -> None:
    """GTFS evidence derivation should reject validator reports with errors."""

    with TemporaryDirectory() as tmp:
        gtfs_zip = Path(tmp) / "feed.zip"
        validator_report = Path(tmp) / "gtfs_validator_report.json"
        _write_gtfs_zip(gtfs_zip)
        _write_validator_report(
            validator_report,
            {
                "source_artifact_sha256": file_sha256(gtfs_zip),
                "summary": {
                    "counts": {
                        "errors": 1,
                        "warnings": 0,
                        "infos": 0,
                        "total": 1,
                    }
                }
            },
        )

        assert_raises_value_error(
            lambda: derive_rail_service_evidence_from_gtfs(
                load_cached_gtfs_feed(gtfs_zip),
                _config(gtfs_zip, validator_report),
            ),
            "GTFS Validator report has 1 error",
        )

    print("PASS: GTFS validator error count blocks derivation")


def test_gtfs_validator_sha_mismatch_blocks_derivation() -> None:
    """Validator report metadata should be tied to the retained report hash."""

    with TemporaryDirectory() as tmp:
        gtfs_zip = Path(tmp) / "feed.zip"
        validator_report = Path(tmp) / "gtfs_validator_report.json"
        _write_gtfs_zip(gtfs_zip)
        _write_validator_report(
            validator_report,
            {
                "validator": "fixture",
                "source_artifact_sha256": file_sha256(gtfs_zip),
                "errors": 0,
            },
        )
        config = replace(
            _config(gtfs_zip, validator_report),
            gtfs_validator_report_sha256="0" * 64,
        )

        assert_raises_value_error(
            lambda: derive_rail_service_evidence_from_gtfs(
                load_cached_gtfs_feed(gtfs_zip),
                config,
            ),
            "GTFS Validator report SHA256",
        )

    print("PASS: GTFS validator SHA mismatch blocks derivation")


def test_gtfs_validator_feed_sha_mismatch_blocks_derivation() -> None:
    """A zero-error report for a different GTFS feed should not certify evidence."""

    with TemporaryDirectory() as tmp:
        gtfs_zip = Path(tmp) / "feed.zip"
        validator_report = Path(tmp) / "gtfs_validator_report.json"
        _write_gtfs_zip(gtfs_zip)
        _write_validator_report(
            validator_report,
            {
                "validator": "fixture",
                "source_artifact_sha256": "1" * 64,
                "errors": 0,
            },
        )

        assert_raises_value_error(
            lambda: derive_rail_service_evidence_from_gtfs(
                load_cached_gtfs_feed(gtfs_zip),
                _config(gtfs_zip, validator_report),
            ),
            "feed SHA256 does not match",
        )

    print("PASS: GTFS validator feed SHA mismatch blocks derivation")


def test_gtfs_source_artifact_sha_mismatch_blocks_derivation() -> None:
    """The source artifact hash must match the retained GTFS file."""

    with TemporaryDirectory() as tmp:
        gtfs_zip = Path(tmp) / "feed.zip"
        validator_report = Path(tmp) / "gtfs_validator_report.json"
        _write_gtfs_zip(gtfs_zip)
        _write_validator_report(
            validator_report,
            {
                "validator": "fixture",
                "source_artifact_sha256": file_sha256(gtfs_zip),
                "errors": 0,
            },
        )
        config = replace(
            _config(gtfs_zip, validator_report),
            source_artifact_sha256="2" * 64,
        )

        assert_raises_value_error(
            lambda: derive_rail_service_evidence_from_gtfs(
                load_cached_gtfs_feed(gtfs_zip),
                config,
            ),
            "source artifact SHA256 does not match",
        )

    print("PASS: GTFS source artifact SHA mismatch blocks derivation")


def test_gtfs_loaded_feed_must_match_metadata_path() -> None:
    """Loaded GTFS feed cannot be certified with another feed's metadata."""

    with TemporaryDirectory() as tmp:
        loaded_gtfs = Path(tmp) / "loaded.zip"
        metadata_gtfs = Path(tmp) / "metadata.zip"
        validator_report = Path(tmp) / "gtfs_validator_report.json"
        _write_gtfs_zip(loaded_gtfs)
        _write_gtfs_zip(metadata_gtfs)
        _write_validator_report(
            validator_report,
            {
                "validator": "fixture",
                "source_artifact_sha256": file_sha256(metadata_gtfs),
                "errors": 0,
            },
        )

        assert_raises_value_error(
            lambda: derive_rail_service_evidence_from_gtfs(
                load_cached_gtfs_feed(loaded_gtfs),
                _config(metadata_gtfs, validator_report),
            ),
            "loaded source artifact path",
        )

    print("PASS: GTFS loaded feed must match metadata path")


def test_gtfs_validator_notices_report_counts_severity_string() -> None:
    """Notice-list reports should count severityString when severity is absent."""

    with TemporaryDirectory() as tmp:
        validator_report = Path(tmp) / "gtfs_validator_report.json"
        _write_validator_report(
            validator_report,
            {
                "notices": [
                    {"severityString": "WARNING", "totalNotices": 2},
                    {"severityString": "INFO", "totalNotices": 3},
                ]
            },
        )

        summary = validate_gtfs_validator_report(
            validator_report,
            expected_sha256=file_sha256(validator_report),
        )

        assert summary["error_count"] == 0
        assert summary["warning_count"] == 2
        assert summary["info_count"] == 3
        assert summary["total_notice_count"] == 5

    print("PASS: GTFS validator notices report counts severityString")


def test_gtfs_validator_missing_error_count_is_rejected() -> None:
    """Count-based reports must explicitly include an errors count."""

    with TemporaryDirectory() as tmp:
        validator_report = Path(tmp) / "gtfs_validator_report.json"
        _write_validator_report(
            validator_report,
            {
                "source_artifact_sha256": "a" * 64,
                "warnings": 1,
                "total": 1,
            },
        )

        assert_raises_value_error(
            lambda: validate_gtfs_validator_report(
                validator_report,
                expected_sha256=file_sha256(validator_report),
                expected_feed_sha256="a" * 64,
            ),
            "counts must include errors",
        )

    print("PASS: GTFS validator missing error count is rejected")


def test_gtfs_validator_malformed_notice_is_rejected() -> None:
    """Notice-list reports must not silently skip malformed notices."""

    with TemporaryDirectory() as tmp:
        validator_report = Path(tmp) / "gtfs_validator_report.json"
        _write_validator_report(
            validator_report,
            {
                "source_artifact_sha256": "a" * 64,
                "notices": [
                    {"severityString": "UNKNOWN", "totalNotices": 1},
                ],
            },
        )

        assert_raises_value_error(
            lambda: validate_gtfs_validator_report(
                validator_report,
                expected_sha256=file_sha256(validator_report),
                expected_feed_sha256="a" * 64,
            ),
            "notice severity",
        )

    print("PASS: GTFS validator malformed notice is rejected")


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
    validator_report: Path | None,
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
        gtfs_validator_report_path=str(validator_report or ""),
        gtfs_validator_report_sha256=(
            file_sha256(validator_report) if validator_report is not None else ""
        ),
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


def _write_validator_report(path: Path, value: dict[str, object]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=True, sort_keys=True) + "\n",
        encoding="utf-8",
    )


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
    test_gtfs_derivation_requires_validator_report_metadata()
    test_gtfs_validator_summary_counts_report_is_accepted()
    test_gtfs_validator_error_count_blocks_derivation()
    test_gtfs_validator_sha_mismatch_blocks_derivation()
    test_gtfs_validator_feed_sha_mismatch_blocks_derivation()
    test_gtfs_source_artifact_sha_mismatch_blocks_derivation()
    test_gtfs_loaded_feed_must_match_metadata_path()
    test_gtfs_validator_notices_report_counts_severity_string()
    test_gtfs_validator_missing_error_count_is_rejected()
    test_gtfs_validator_malformed_notice_is_rejected()
    test_gtfs_zip_requires_required_files()
    print("\n=== REALWORLD RAIL GTFS TESTS PASSED ===")
