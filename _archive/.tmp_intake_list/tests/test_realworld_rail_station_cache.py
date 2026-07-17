"""Tests for deriving station bindings from cached official station extracts."""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.rail_station_binding import (  # noqa: E402
    load_rail_station_bindings,
    summarize_rail_station_bindings,
)
from src.realworld.rail_station_cache import (  # noqa: E402
    REQUIRED_STATION_CACHE_COLUMNS,
    StationBindingDerivationConfig,
    derive_rail_station_bindings_from_cache,
    file_sha256,
    load_cached_station_binding_candidates,
    write_derived_rail_station_bindings,
)


def assert_raises_value_error(func, expected_message: str) -> None:
    """Assert that a zero-argument function raises ValueError with context."""

    try:
        func()
    except ValueError as exc:
        message = str(exc)
        assert expected_message in message, message
        return
    raise AssertionError("expected ValueError")


def test_cached_station_fixture_derives_binding_ready_rows() -> None:
    """A reviewed station extract can produce official binding rows."""

    with TemporaryDirectory() as tmp:
        input_path = Path(tmp) / "station_cache.csv"
        output_path = Path(tmp) / "rail_station_bindings.csv"
        _write_station_cache(input_path)

        candidates = load_cached_station_binding_candidates(input_path)
        records = derive_rail_station_bindings_from_cache(
            candidates,
            StationBindingDerivationConfig(
                binding_id_prefix="fixture_binding",
                region_id="songpa_public_demo",
                source_name="fixture official station cache",
                source_url_or_citation="fixture official source",
                source_accessed_date="2026-05-04",
                source_artifact_path="fixture/station_cache.csv",
                source_artifact_sha256=file_sha256(input_path),
            ),
        )
        write_derived_rail_station_bindings(records, output_path)
        loaded = load_rail_station_bindings(output_path)
        summary = summarize_rail_station_bindings(loaded)

        assert summary["binding_ready"] is True
        assert summary["official_required_points"] == ["R", "S"]
        assert all(record.source_status == "official_station_code_bound" for record in loaded)
        assert all("source_artifact_sha256=" in record.notes for record in loaded)

    print("PASS: cached station fixture derives binding-ready rows")


def test_station_cache_allows_interchange_station_rows_per_point() -> None:
    """A simulator rail point can map to multiple line-specific station IDs."""

    with TemporaryDirectory() as tmp:
        input_path = Path(tmp) / "interchange_station_cache.csv"
        output_path = Path(tmp) / "rail_station_bindings.csv"
        _write_rows(
            input_path,
            [
                {
                    "point_id": "S",
                    "station_name": "Olympic Park",
                    "station_id": "2556",
                    "station_code": "P550",
                    "line": "05호선",
                },
                {
                    "point_id": "S",
                    "station_name": "Olympic Park",
                    "station_id": "4136",
                    "station_code": "936",
                    "line": "09호선",
                },
                {
                    "point_id": "R",
                    "station_name": "Jamsil",
                    "station_id": "0216",
                    "station_code": "216",
                    "line": "02호선",
                },
                {
                    "point_id": "R",
                    "station_name": "Jamsil",
                    "station_id": "2815",
                    "station_code": "814",
                    "line": "08호선",
                },
            ],
        )

        candidates = load_cached_station_binding_candidates(input_path)
        records = derive_rail_station_bindings_from_cache(
            candidates,
            StationBindingDerivationConfig(
                binding_id_prefix="fixture_binding",
                region_id="songpa_public_demo",
                source_name="fixture official station cache",
                source_url_or_citation="fixture official source",
                source_accessed_date="2026-05-04",
            ),
        )
        write_derived_rail_station_bindings(records, output_path)
        loaded = load_rail_station_bindings(output_path)
        summary = summarize_rail_station_bindings(loaded)

        assert len(loaded) == 4
        assert summary["binding_ready"] is True
        assert len({record.binding_id for record in loaded}) == 4

    print("PASS: station cache allows interchange station rows")


def test_station_cache_rejects_missing_identifier() -> None:
    """Official candidate rows need a station_id or station_code."""

    with TemporaryDirectory() as tmp:
        input_path = Path(tmp) / "bad_station_cache.csv"
        _write_station_cache(input_path, station_id="pending", station_code="pending")

        assert_raises_value_error(
            lambda: load_cached_station_binding_candidates(input_path),
            "requires station_id or station_code",
        )

    print("PASS: station cache rejects missing identifier")


def test_station_cache_rejects_duplicate_station_candidate_rows() -> None:
    """A cache extract must not duplicate the same point and station identity."""

    with TemporaryDirectory() as tmp:
        input_path = Path(tmp) / "duplicate_station_cache.csv"
        rows = [
            {
                "point_id": "S",
                "station_name": "Access Station",
                "station_id": "station_1",
                "station_code": "code_1",
                "line": "fixture line",
            },
            {
                "point_id": "S",
                "station_name": "Access Station Duplicate",
                "station_id": "station_1",
                "station_code": "code_1",
                "line": "fixture line",
            },
        ]
        _write_rows(input_path, rows)

        assert_raises_value_error(
            lambda: load_cached_station_binding_candidates(input_path),
            "duplicate station candidate",
        )

    print("PASS: station cache rejects duplicate station candidates")


def _write_station_cache(
    path: Path,
    *,
    station_id: str = "official_station_id",
    station_code: str = "official_station_code",
) -> None:
    rows = []
    for point_id, station_name, line in (
        ("S", "Access Station", "fixture line 9"),
        ("R", "Egress Station", "fixture line 2"),
    ):
        rows.append(
            {
                "point_id": point_id,
                "station_name": station_name,
                "station_id": _point_value(station_id, point_id),
                "station_code": _point_value(station_code, point_id),
                "line": line,
            }
        )
    _write_rows(path, rows)


def _point_value(value: str, point_id: str) -> str:
    if value.lower() in {"pending", "unknown", "tbd", "none", "na", "n/a"}:
        return value
    return f"{value}_{point_id}"


def _write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_STATION_CACHE_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    test_cached_station_fixture_derives_binding_ready_rows()
    test_station_cache_allows_interchange_station_rows_per_point()
    test_station_cache_rejects_missing_identifier()
    test_station_cache_rejects_duplicate_station_candidate_rows()
    print("\n=== REALWORLD RAIL STATION CACHE TESTS PASSED ===")
