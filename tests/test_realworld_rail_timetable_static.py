"""Tests for static rail timetable CSV normalization."""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.rail_evidence import load_rail_service_evidence  # noqa: E402
from src.realworld.rail_station_binding import (  # noqa: E402
    REQUIRED_COLUMNS as STATION_BINDING_COLUMNS,
)
from src.realworld.rail_timetable import (  # noqa: E402
    REQUIRED_TIMETABLE_COLUMNS,
    file_sha256,
    load_cached_timetable_events,
)
from src.realworld.rail_timetable_static import (  # noqa: E402
    StaticTimetableColumnMap,
    StaticTimetableSelection,
    normalize_static_timetable_csv,
)


ROOT = Path(__file__).resolve().parents[1]


def test_static_timetable_normalizer_maps_explicit_columns_to_cache_schema() -> None:
    """A reviewed static source CSV should normalize only through explicit mappings."""

    with TemporaryDirectory(dir=ROOT) as tmp:
        root = Path(tmp)
        source = root / "reviewed_source.csv"
        output = root / "normalized_cache.csv"
        manifest = root / "normalization_manifest.json"
        _write_static_source(source)

        summary = normalize_static_timetable_csv(
            source,
            output,
            columns=_column_map(),
            selection=_selection(),
            manifest_path=manifest,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)

        assert tuple(reader.fieldnames or ()) == REQUIRED_TIMETABLE_COLUMNS
        assert len(rows) == 6
        assert summary["normalized_event_count"] == 6
        assert summary["access_event_count"] == 3
        assert summary["egress_event_count"] == 3
        assert summary["input_sha256"] == file_sha256(source)
        assert summary["output_sha256"] == file_sha256(output)
        assert load_cached_timetable_events(output)

        manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
        assert manifest_data["input_sha256"] == file_sha256(source)
        assert manifest_data["claim_scope"].startswith("static timetable normalization")
        assert manifest_data["publication_ready"] is False
        assert manifest_data["final_study_ready"] is False
        assert manifest_data["formal_acceptance_evidence"] is False
        assert manifest_data["can_mark_complete"] is False
        assert manifest_data["can_support_rail_evidence_gate"] is False

    print("PASS: static timetable normalizer maps explicit columns to cache schema")


def test_static_timetable_normalizer_cli_output_feeds_timetable_derivation() -> None:
    """The CLI output should feed the existing cached-timetable derivation CLI."""

    with TemporaryDirectory(dir=ROOT) as tmp:
        root = Path(tmp)
        source = root / "reviewed_source.csv"
        normalized = root / "normalized_cache.csv"
        manifest = root / "normalization_manifest.json"
        bindings = root / "bindings.csv"
        evidence = root / "rail_service_evidence.csv"
        _write_static_source(source)
        _write_bindings(bindings)

        _run(
            "scripts/normalize_rail_timetable_cache.py",
            "--input",
            _rel(source),
            "--output",
            _rel(normalized),
            "--manifest-output",
            _rel(manifest),
            *_mapping_args(),
            "--access-station-code",
            "P550",
            "--egress-station-code",
            "216",
            "--filter",
            "운행일=평일",
        )
        _run(
            "scripts/derive_rail_service_evidence.py",
            "--input",
            _rel(normalized),
            "--output",
            _rel(evidence),
            "--evidence-id",
            "static_cli_timetable",
            "--source-name",
            "reviewed static timetable fixture",
            "--source-url-or-citation",
            "fixture",
            "--extraction-date",
            "2026-06-03",
            "--capacity-pax-per-train",
            "500",
            "--service-window",
            "weekday fixture window",
            "--direction",
            "하행",
            "--service-day",
            "평일",
            "--station-bindings",
            _rel(bindings),
        )

        records = load_rail_service_evidence(evidence)
        assert records[0].headway_min == 10.0
        assert records[0].travel_time_min == 12.0
        assert records[0].source_artifact_sha256 == file_sha256(normalized)

    print("PASS: static timetable normalizer CLI output feeds derivation")


def test_static_timetable_normalizer_requires_explicit_column_mapping() -> None:
    """The CLI should not infer source headers when mappings are omitted."""

    with TemporaryDirectory(dir=ROOT) as tmp:
        root = Path(tmp)
        source = root / "reviewed_source.csv"
        output = root / "normalized_cache.csv"
        _write_static_source(source)

        result = _run_raw(
            "scripts/normalize_rail_timetable_cache.py",
            "--input",
            _rel(source),
            "--output",
            _rel(output),
            expect_success=False,
        )

        assert result.returncode != 0
        assert not output.exists()
        assert "--trip-id-column" in result.stderr

    print("PASS: static timetable normalizer requires explicit mapping")


def test_static_timetable_normalizer_rejects_missing_source_column() -> None:
    """Bad mappings should fail instead of writing accepted normalized cache rows."""

    with TemporaryDirectory(dir=ROOT) as tmp:
        root = Path(tmp)
        source = root / "reviewed_source.csv"
        output = root / "normalized_cache.csv"
        _write_static_source(source)

        result = _run_raw(
            "scripts/normalize_rail_timetable_cache.py",
            "--input",
            _rel(source),
            "--output",
            _rel(output),
            *_mapping_args(trip_id_column="없는열"),
            "--access-station-code",
            "P550",
            expect_success=False,
        )

        assert result.returncode != 0
        assert not output.exists()
        assert "missing source columns" in result.stderr

    print("PASS: static timetable normalizer rejects missing source column")


def _write_static_source(path: Path) -> None:
    rows: list[dict[str, str]] = []
    for index, minute in enumerate((0, 10, 20), start=1):
        trip_id = f"T{index:03d}"
        rows.append(
            {
                "열차번호": trip_id,
                "역명": "Olympic Park",
                "역코드": "P550",
                "도착시각": f"08:{minute - 1:02d}:30" if minute else "08:00:00",
                "출발시각": f"08:{minute:02d}:00",
                "방향": "하행",
                "운행일": "평일",
            }
        )
        rows.append(
            {
                "열차번호": trip_id,
                "역명": "Jamsil",
                "역코드": "216",
                "도착시각": f"08:{minute + 12:02d}:00",
                "출발시각": f"08:{minute + 13:02d}:00",
                "방향": "하행",
                "운행일": "평일",
            }
        )
    _write_csv(
        path,
        ("열차번호", "역명", "역코드", "도착시각", "출발시각", "방향", "운행일"),
        rows,
    )


def _write_bindings(path: Path) -> None:
    rows = [
        _binding("fixture_s", "S", "Olympic Park", "2556", "P550"),
        _binding("fixture_r", "R", "Jamsil", "0216", "216"),
    ]
    _write_csv(path, STATION_BINDING_COLUMNS, rows)


def _binding(
    binding_id: str,
    point_id: str,
    station_name: str,
    station_id: str,
    station_code: str,
) -> dict[str, str]:
    return {
        "binding_id": binding_id,
        "region_id": "songpa_public_demo",
        "point_id": point_id,
        "station_name": station_name,
        "station_id": station_id,
        "station_code": station_code,
        "source_name": "fixture",
        "source_url_or_citation": "fixture",
        "source_accessed_date": "2026-06-03",
        "source_status": "official_station_code_bound",
        "claim_scope": (
            "official station-code binding from cached station source; "
            "not operational rail service evidence"
        ),
        "notes": "fixture",
    }


def _column_map() -> StaticTimetableColumnMap:
    return StaticTimetableColumnMap(
        trip_id="열차번호",
        station_name="역명",
        station_code="역코드",
        arrival_time="도착시각",
        departure_time="출발시각",
        direction="방향",
        service_day="운행일",
    )


def _selection() -> StaticTimetableSelection:
    return StaticTimetableSelection(
        access_station_code="P550",
        egress_station_code="216",
        filters={"운행일": "평일"},
    )


def _mapping_args(*, trip_id_column: str = "열차번호") -> tuple[str, ...]:
    return (
        "--trip-id-column",
        trip_id_column,
        "--station-name-column",
        "역명",
        "--station-code-column",
        "역코드",
        "--arrival-time-column",
        "도착시각",
        "--departure-time-column",
        "출발시각",
        "--direction-column",
        "방향",
        "--service-day-column",
        "운행일",
    )


def _run(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return _run_raw(script, *args, expect_success=True)


def _run_raw(
    script: str,
    *args: str,
    expect_success: bool,
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(ROOT / script), *args]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if expect_success and result.returncode != 0:
        raise AssertionError(
            f"command failed: {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def _rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def _write_csv(path: Path, fieldnames: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    test_static_timetable_normalizer_maps_explicit_columns_to_cache_schema()
    test_static_timetable_normalizer_cli_output_feeds_timetable_derivation()
    test_static_timetable_normalizer_requires_explicit_column_mapping()
    test_static_timetable_normalizer_rejects_missing_source_column()
    print("\n=== REALWORLD STATIC RAIL TIMETABLE TESTS PASSED ===")
