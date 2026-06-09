"""Tests for deriving rail evidence from cached shortest-path extracts."""

from __future__ import annotations

import csv
from dataclasses import replace
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.rail_evidence import (  # noqa: E402
    load_rail_service_evidence,
    summarize_rail_service_evidence,
)
from src.realworld.rail_shortest_path import (  # noqa: E402
    REQUIRED_SHORTEST_PATH_COLUMNS,
    RailShortestPathEvidenceConfig,
    derive_rail_service_evidence_from_shortest_path,
    file_sha256,
    load_cached_shortest_path_records,
    write_rail_shortest_path_evidence,
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


def test_shortest_path_fixture_derives_travel_time_evidence() -> None:
    """A cached shortest-path extract can produce a travel-time evidence row."""

    with TemporaryDirectory() as tmp:
        shortest_path = Path(tmp) / "shortest_path.csv"
        output_path = Path(tmp) / "rail_service_evidence.csv"
        _write_shortest_path_fixture(shortest_path)

        records = load_cached_shortest_path_records(shortest_path)
        evidence = derive_rail_service_evidence_from_shortest_path(
            records,
            _config(shortest_path),
            station_bindings=_binding_fixture(),
        )
        write_rail_shortest_path_evidence([evidence], output_path)
        loaded = load_rail_service_evidence(output_path)
        summary = summarize_rail_service_evidence(loaded)

        assert evidence.source_status == "cached_shortest_path_derived"
        assert evidence.travel_time_min == 13.0
        assert evidence.derived_field_set == frozenset({"travel_time"})
        assert summary["derived_field_ready"]["travel_time"] is True
        assert summary["derived_field_ready"]["headway"] is False
        assert summary["publication_ready"] is False

    print("PASS: shortest-path fixture derives travel-time evidence")


def test_shortest_path_station_code_mismatch_blocks_derivation() -> None:
    """A shortest-path extract for the wrong station should fail."""

    with TemporaryDirectory() as tmp:
        shortest_path = Path(tmp) / "shortest_path.csv"
        _write_shortest_path_fixture(shortest_path, access_code="WRONG")
        records = load_cached_shortest_path_records(shortest_path)

        assert_raises_value_error(
            lambda: derive_rail_service_evidence_from_shortest_path(
                records,
                _config(shortest_path),
                station_bindings=_binding_fixture(),
            ),
            "do not match official bindings",
        )

    print("PASS: shortest-path station-code mismatch blocks derivation")


def test_shortest_path_source_artifact_sha_mismatch_blocks_derivation() -> None:
    """Shortest-path evidence should be bound to the retained source file hash."""

    with TemporaryDirectory() as tmp:
        shortest_path = Path(tmp) / "shortest_path.csv"
        _write_shortest_path_fixture(shortest_path)
        records = load_cached_shortest_path_records(shortest_path)
        config = replace(
            _config(shortest_path),
            source_artifact_sha256="0" * 64,
        )

        assert_raises_value_error(
            lambda: derive_rail_service_evidence_from_shortest_path(records, config),
            "source artifact SHA256 does not match",
        )

    print("PASS: shortest-path source artifact SHA mismatch blocks derivation")


def test_shortest_path_loaded_source_must_match_metadata_path() -> None:
    """Loaded shortest-path records cannot be certified with another file hash."""

    with TemporaryDirectory() as tmp:
        loaded_path = Path(tmp) / "loaded.csv"
        metadata_path = Path(tmp) / "metadata.csv"
        _write_shortest_path_fixture(loaded_path)
        _write_shortest_path_fixture(metadata_path, access_code="P550", egress_code="216")
        records = load_cached_shortest_path_records(loaded_path)
        config = replace(
            _config(metadata_path),
            source_artifact_path=str(metadata_path),
            source_artifact_sha256=file_sha256(metadata_path),
        )

        assert_raises_value_error(
            lambda: derive_rail_service_evidence_from_shortest_path(records, config),
            "loaded source artifact path",
        )

    print("PASS: shortest-path loaded source must match metadata path")


def _write_shortest_path_fixture(
    path: Path,
    *,
    access_code: str = "P550",
    egress_code: str = "216",
) -> None:
    rows = [
        {
            "route_id": "minimum_time_1",
            "access_station_name": "Olympic Park Station",
            "access_station_code": access_code,
            "egress_station_name": "Jamsil Station",
            "egress_station_code": egress_code,
            "travel_time_min": "13",
            "distance_km": "4.2",
            "transfer_count": "1",
            "route_type": "minimum_time",
        },
        {
            "route_id": "minimum_time_2",
            "access_station_name": "Olympic Park Station",
            "access_station_code": access_code,
            "egress_station_name": "Jamsil Station",
            "egress_station_code": egress_code,
            "travel_time_min": "15",
            "distance_km": "3.9",
            "transfer_count": "0",
            "route_type": "minimum_time",
        },
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_SHORTEST_PATH_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def _config(path: Path) -> RailShortestPathEvidenceConfig:
    return RailShortestPathEvidenceConfig(
        evidence_id="fixture_shortest_path",
        region_id="songpa_public_demo",
        access_point="S",
        egress_point="R",
        source_name="fixture shortest path",
        source_url_or_citation="fixture",
        extraction_date="2026-05-04",
        headway_min_proxy=10,
        capacity_pax_per_train=500,
        service_window="weekday",
        route_type="minimum_time",
        source_artifact_path=str(path),
        source_artifact_sha256=file_sha256(path),
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
    test_shortest_path_fixture_derives_travel_time_evidence()
    test_shortest_path_station_code_mismatch_blocks_derivation()
    test_shortest_path_source_artifact_sha_mismatch_blocks_derivation()
    test_shortest_path_loaded_source_must_match_metadata_path()
    print("\n=== REALWORLD RAIL SHORTEST PATH TESTS PASSED ===")
