"""Tests for deriving rail evidence from cached timetable extracts."""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.rail_evidence import (  # noqa: E402
    load_rail_service_evidence,
    summarize_rail_service_evidence,
)
from src.realworld.rail_timetable import (  # noqa: E402
    REQUIRED_TIMETABLE_COLUMNS,
    RailEvidenceDerivationConfig,
    RailHeadwayEvidenceConfig,
    derive_rail_headway_evidence_from_timetable,
    derive_rail_service_evidence_from_timetable,
    file_sha256,
    load_cached_timetable_events,
    parse_service_time_min,
    validate_timetable_station_bindings,
    write_rail_service_evidence,
)
from src.realworld.rail_station_binding import RailStationBinding  # noqa: E402


def assert_raises_value_error(func, expected_message: str) -> None:
    """Assert that a zero-argument function raises ValueError with context."""

    try:
        func()
    except ValueError as exc:
        message = str(exc)
        assert expected_message in message, message
        return
    raise AssertionError("expected ValueError")


def test_cached_timetable_fixture_derives_publication_ready_evidence() -> None:
    """A cached station-event extract can produce a validated derived row."""

    with TemporaryDirectory() as tmp:
        timetable_path = Path(tmp) / "timetable.csv"
        output_path = Path(tmp) / "rail_service_evidence.csv"
        _write_timetable_fixture(timetable_path)

        events = load_cached_timetable_events(timetable_path)
        record = derive_rail_service_evidence_from_timetable(
            events,
            RailEvidenceDerivationConfig(
                evidence_id="fixture_derived",
                region_id="songpa_public_demo",
                access_point="S",
                egress_point="R",
                source_name="fixture cached timetable",
                source_url_or_citation="fixture",
                extraction_date="2026-05-04",
                capacity_pax_per_train=500,
                service_window="weekday 08:00-08:30",
                direction="eastbound",
                service_day="weekday",
                source_artifact_path=str(timetable_path),
                source_artifact_sha256=file_sha256(timetable_path),
            ),
        )
        write_rail_service_evidence([record], output_path)
        loaded = load_rail_service_evidence(output_path)
        summary = summarize_rail_service_evidence(loaded)

        assert record.source_status == "cached_timetable_derived"
        assert record.headway_min == 10.0
        assert record.travel_time_min == 12.0
        assert record.derived_field_set == frozenset({"headway", "travel_time"})
        assert record.source_artifact_path == str(timetable_path)
        assert record.source_artifact_sha256 == file_sha256(timetable_path)
        assert "source_artifact_sha256=" in record.notes
        assert loaded[0].source_artifact_sha256 == file_sha256(timetable_path)
        assert summary["publication_ready"] is True
        assert summary["derived_record_count"] == 1

    print("PASS: cached timetable fixture derives publication-ready evidence")


def test_service_time_parser_accepts_gtfs_style_hours() -> None:
    """GTFS-style times after midnight should parse without wrapping."""

    assert parse_service_time_min("08:30") == 510.0
    assert parse_service_time_min("08:30:30") == 510.5
    assert parse_service_time_min("25:00:00") == 1500.0

    print("PASS: service time parser accepts GTFS-style hours")


def test_headway_only_derivation_does_not_claim_travel_time() -> None:
    """Access-station timetable rows can derive headway without travel-time evidence."""

    with TemporaryDirectory() as tmp:
        timetable_path = Path(tmp) / "headway.csv"
        _write_timetable_fixture(timetable_path, include_egress=False, access_code="P550")
        output_path = Path(tmp) / "rail_service_evidence.csv"
        events = load_cached_timetable_events(timetable_path)
        record = derive_rail_headway_evidence_from_timetable(
            events,
            RailHeadwayEvidenceConfig(
                evidence_id="fixture_headway",
                region_id="songpa_public_demo",
                access_point="S",
                egress_point="R",
                egress_station_name="Jamsil Station",
                source_name="fixture cached timetable",
                source_url_or_citation="fixture",
                extraction_date="2026-05-04",
                travel_time_min_proxy=12.0,
                capacity_pax_per_train=500,
                service_window="weekday 08:00-08:30",
                direction="eastbound",
                service_day="weekday",
                source_artifact_path=str(timetable_path),
                source_artifact_sha256=file_sha256(timetable_path),
            ),
            station_bindings=_binding_fixture(),
        )
        write_rail_service_evidence([record], output_path)
        loaded = load_rail_service_evidence(output_path)
        summary = summarize_rail_service_evidence(loaded)

        assert record.headway_min == 10.0
        assert record.travel_time_min == 12.0
        assert record.derived_field_set == frozenset({"headway"})
        assert summary["derived_field_ready"]["headway"] is True
        assert summary["derived_field_ready"]["travel_time"] is False
        assert summary["publication_ready"] is False

    print("PASS: headway-only derivation does not claim travel time")


def test_timetable_station_codes_must_match_official_bindings() -> None:
    """Station-event extracts should match official S/R station bindings."""

    with TemporaryDirectory() as tmp:
        timetable_path = Path(tmp) / "timetable.csv"
        _write_timetable_fixture(
            timetable_path,
            access_code="P550",
            egress_code="216",
        )
        events = load_cached_timetable_events(timetable_path)
        config = _derivation_config(timetable_path)

        validate_timetable_station_bindings(
            events,
            config,
            station_bindings=_binding_fixture(),
        )

    print("PASS: timetable station codes match official bindings")


def test_timetable_station_code_mismatch_blocks_derivation() -> None:
    """A cached timetable extract for the wrong station should fail."""

    with TemporaryDirectory() as tmp:
        timetable_path = Path(tmp) / "timetable.csv"
        _write_timetable_fixture(
            timetable_path,
            access_code="WRONG",
            egress_code="216",
        )
        events = load_cached_timetable_events(timetable_path)

        assert_raises_value_error(
            lambda: derive_rail_service_evidence_from_timetable(
                events,
                _derivation_config(timetable_path),
                station_bindings=_binding_fixture(),
            ),
            "do not match official bindings",
        )

    print("PASS: timetable station-code mismatch blocks derivation")


def test_missing_matched_egress_arrival_blocks_derivation() -> None:
    """Headway alone is insufficient without matched travel-time evidence."""

    with TemporaryDirectory() as tmp:
        timetable_path = Path(tmp) / "timetable.csv"
        _write_timetable_fixture(timetable_path, include_egress=False)
        events = load_cached_timetable_events(timetable_path)
        source_digest = file_sha256(timetable_path)

        assert_raises_value_error(
            lambda: derive_rail_service_evidence_from_timetable(
                events,
                RailEvidenceDerivationConfig(
                    evidence_id="bad",
                    region_id="songpa_public_demo",
                    access_point="S",
                    egress_point="R",
                    source_name="fixture",
                    source_url_or_citation="fixture",
                    extraction_date="2026-05-04",
                    capacity_pax_per_train=500,
                    service_window="weekday",
                    direction="eastbound",
                    service_day="weekday",
                    source_artifact_path="fixture/timetable.csv",
                    source_artifact_sha256=source_digest,
                ),
            ),
            "matched access-departure to egress-arrival",
        )

    print("PASS: missing matched egress arrival blocks derivation")


def _write_timetable_fixture(
    path: Path,
    *,
    include_egress: bool = True,
    access_code: str = "fixture_access",
    egress_code: str = "fixture_egress",
) -> None:
    rows = []
    for index, departure_minute in enumerate((0, 10, 20), start=1):
        trip_id = f"trip_{index}"
        rows.append(
            {
                "trip_id": trip_id,
                "station_role": "access",
                "station_name": "Olympic Park Station",
                "station_code": access_code,
                "event_time": f"08:{departure_minute:02d}:00",
                "event_type": "departure",
                "direction": "eastbound",
                "service_day": "weekday",
            }
        )
        if include_egress:
            rows.append(
                {
                    "trip_id": trip_id,
                    "station_role": "egress",
                    "station_name": "Jamsil Station",
                    "station_code": egress_code,
                    "event_time": f"08:{departure_minute + 12:02d}:00",
                    "event_type": "arrival",
                    "direction": "eastbound",
                    "service_day": "weekday",
                }
            )

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_TIMETABLE_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def _derivation_config(timetable_path: Path) -> RailEvidenceDerivationConfig:
    return RailEvidenceDerivationConfig(
        evidence_id="fixture_derived",
        region_id="songpa_public_demo",
        access_point="S",
        egress_point="R",
        source_name="fixture cached timetable",
        source_url_or_citation="fixture",
        extraction_date="2026-05-04",
        capacity_pax_per_train=500,
        service_window="weekday",
        direction="eastbound",
        service_day="weekday",
        source_artifact_path=str(timetable_path),
        source_artifact_sha256=file_sha256(timetable_path),
    )


def _binding_fixture() -> tuple[RailStationBinding, ...]:
    return (
        RailStationBinding(
            binding_id="s",
            region_id="songpa_public_demo",
            point_id="S",
            station_name="Olympic Park",
            station_id="2556",
            station_code="P550",
            source_name="fixture",
            source_url_or_citation="fixture",
            source_accessed_date="2026-05-04",
            source_status="official_station_code_bound",
            claim_scope=(
                "official station-code binding from cached station source; "
                "not operational rail service evidence"
            ),
            notes="fixture",
        ),
        RailStationBinding(
            binding_id="r",
            region_id="songpa_public_demo",
            point_id="R",
            station_name="Jamsil",
            station_id="0216",
            station_code="216",
            source_name="fixture",
            source_url_or_citation="fixture",
            source_accessed_date="2026-05-04",
            source_status="official_station_code_bound",
            claim_scope=(
                "official station-code binding from cached station source; "
                "not operational rail service evidence"
            ),
            notes="fixture",
        ),
    )


if __name__ == "__main__":
    test_cached_timetable_fixture_derives_publication_ready_evidence()
    test_service_time_parser_accepts_gtfs_style_hours()
    test_headway_only_derivation_does_not_claim_travel_time()
    test_timetable_station_codes_must_match_official_bindings()
    test_timetable_station_code_mismatch_blocks_derivation()
    test_missing_matched_egress_arrival_blocks_derivation()
    print("\n=== REALWORLD RAIL TIMETABLE TESTS PASSED ===")
