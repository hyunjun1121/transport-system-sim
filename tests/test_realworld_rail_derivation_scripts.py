"""CLI smoke tests for cached rail evidence derivation scripts."""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.rail_evidence import load_rail_service_evidence  # noqa: E402
from src.realworld.rail_gtfs import file_sha256 as gtfs_sha256  # noqa: E402
from src.realworld.rail_shortest_path import (  # noqa: E402
    REQUIRED_SHORTEST_PATH_COLUMNS,
)
from src.realworld.rail_station_binding import (  # noqa: E402
    REQUIRED_COLUMNS as STATION_BINDING_COLUMNS,
)
from src.realworld.rail_timetable import (  # noqa: E402
    REQUIRED_TIMETABLE_COLUMNS,
    file_sha256,
)


ROOT = Path(__file__).resolve().parents[1]


def test_timetable_derivation_cli_uses_retained_source_metadata() -> None:
    """The full timetable CLI should work with relative retained-source paths."""

    with TemporaryDirectory(dir=ROOT) as tmp:
        root = Path(tmp)
        timetable = root / "timetable.csv"
        bindings = root / "bindings.csv"
        output = root / "rail_service_evidence.csv"
        _write_timetable(timetable, include_egress=True)
        _write_bindings(bindings)

        _run(
            "scripts/derive_rail_service_evidence.py",
            "--input",
            _rel(timetable),
            "--output",
            _rel(output),
            "--evidence-id",
            "cli_timetable",
            "--source-name",
            "fixture timetable",
            "--source-url-or-citation",
            "fixture",
            "--extraction-date",
            "2026-05-04",
            "--capacity-pax-per-train",
            "500",
            "--service-window",
            "weekday 08:00-08:30",
            "--direction",
            "eastbound",
            "--service-day",
            "weekday",
            "--station-bindings",
            _rel(bindings),
        )

        records = load_rail_service_evidence(output)
        assert records[0].source_status == "cached_timetable_derived"
        assert records[0].source_artifact_sha256 == file_sha256(timetable)

    print("PASS: timetable derivation CLI uses retained source metadata")


def test_headway_derivation_cli_uses_retained_source_metadata() -> None:
    """The headway-only CLI should keep travel-time claims bounded."""

    with TemporaryDirectory(dir=ROOT) as tmp:
        root = Path(tmp)
        timetable = root / "headway.csv"
        bindings = root / "bindings.csv"
        output = root / "rail_headway_evidence.csv"
        _write_timetable(timetable, include_egress=False)
        _write_bindings(bindings)

        _run(
            "scripts/derive_rail_headway_evidence.py",
            "--input",
            _rel(timetable),
            "--output",
            _rel(output),
            "--evidence-id",
            "cli_headway",
            "--egress-station-name",
            "Jamsil",
            "--source-name",
            "fixture timetable",
            "--source-url-or-citation",
            "fixture",
            "--extraction-date",
            "2026-05-04",
            "--travel-time-min-proxy",
            "12",
            "--capacity-pax-per-train",
            "500",
            "--service-window",
            "weekday 08:00-08:30",
            "--direction",
            "eastbound",
            "--service-day",
            "weekday",
            "--station-bindings",
            _rel(bindings),
        )

        records = load_rail_service_evidence(output)
        assert records[0].derived_field_set == frozenset({"headway"})
        assert records[0].source_artifact_sha256 == file_sha256(timetable)

    print("PASS: headway derivation CLI uses retained source metadata")


def test_shortest_path_derivation_cli_uses_retained_source_metadata() -> None:
    """The shortest-path CLI should derive travel-time-only evidence."""

    with TemporaryDirectory(dir=ROOT) as tmp:
        root = Path(tmp)
        shortest_path = root / "shortest_path.csv"
        bindings = root / "bindings.csv"
        output = root / "rail_shortest_path_evidence.csv"
        _write_shortest_path(shortest_path)
        _write_bindings(bindings)

        _run(
            "scripts/derive_rail_shortest_path_evidence.py",
            "--input",
            _rel(shortest_path),
            "--output",
            _rel(output),
            "--evidence-id",
            "cli_shortest_path",
            "--source-name",
            "fixture shortest path",
            "--source-url-or-citation",
            "fixture",
            "--extraction-date",
            "2026-05-04",
            "--headway-min-proxy",
            "10",
            "--capacity-pax-per-train",
            "500",
            "--service-window",
            "weekday",
            "--route-type",
            "minimum_time",
            "--station-bindings",
            _rel(bindings),
        )

        records = load_rail_service_evidence(output)
        assert records[0].derived_field_set == frozenset({"travel_time"})
        assert records[0].source_artifact_sha256 == file_sha256(shortest_path)

    print("PASS: shortest-path derivation CLI uses retained source metadata")


def test_gtfs_derivation_cli_requires_same_feed_validator_report() -> None:
    """The GTFS CLI should require a retained same-feed Validator report."""

    with TemporaryDirectory(dir=ROOT) as tmp:
        root = Path(tmp)
        gtfs_zip = root / "feed.zip"
        validator_report = root / "gtfs_validator_report.json"
        output = root / "rail_gtfs_evidence.csv"
        _write_gtfs_zip(gtfs_zip)
        _write_json(
            validator_report,
            {
                "validator": "fixture",
                "source_artifact_sha256": gtfs_sha256(gtfs_zip),
                "errors": 0,
            },
        )

        _run(
            "scripts/derive_rail_gtfs_evidence.py",
            "--input",
            _rel(gtfs_zip),
            "--output",
            _rel(output),
            "--evidence-id",
            "cli_gtfs",
            "--access-stop-id",
            "S",
            "--egress-stop-id",
            "R",
            "--source-name",
            "fixture GTFS",
            "--source-url-or-citation",
            "fixture",
            "--extraction-date",
            "2026-05-04",
            "--capacity-pax-per-train",
            "500",
            "--service-window",
            "weekday 08:00-08:30",
            "--route-id",
            "line9",
            "--service-id",
            "weekday",
            "--direction-id",
            "0",
            "--gtfs-validator-report",
            _rel(validator_report),
        )

        records = load_rail_service_evidence(output)
        assert records[0].source_status == "cached_gtfs_derived"
        assert records[0].gtfs_validator_report_sha256 == gtfs_sha256(validator_report)

    print("PASS: GTFS derivation CLI requires same-feed Validator report")


def _run(script: str, *args: str) -> None:
    command = [sys.executable, str(ROOT / script), *args]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        raise AssertionError(
            f"command failed: {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


def _rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


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
        "source_accessed_date": "2026-05-04",
        "source_status": "official_station_code_bound",
        "claim_scope": (
            "official station-code binding from cached station source; "
            "not operational rail service evidence"
        ),
        "notes": "fixture",
    }


def _write_timetable(path: Path, *, include_egress: bool) -> None:
    rows: list[dict[str, str]] = []
    for index, minute in enumerate((0, 10, 20), start=1):
        trip_id = f"trip_{index}"
        rows.append(
            {
                "trip_id": trip_id,
                "station_role": "access",
                "station_name": "Olympic Park",
                "station_code": "P550",
                "event_time": f"08:{minute:02d}:00",
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
                    "station_name": "Jamsil",
                    "station_code": "216",
                    "event_time": f"08:{minute + 12:02d}:00",
                    "event_type": "arrival",
                    "direction": "eastbound",
                    "service_day": "weekday",
                }
            )
    _write_csv(path, REQUIRED_TIMETABLE_COLUMNS, rows)


def _write_shortest_path(path: Path) -> None:
    _write_csv(
        path,
        REQUIRED_SHORTEST_PATH_COLUMNS,
        [
            {
                "route_id": "minimum_time_1",
                "access_station_name": "Olympic Park",
                "access_station_code": "P550",
                "egress_station_name": "Jamsil",
                "egress_station_code": "216",
                "travel_time_min": "13",
                "distance_km": "4.2",
                "transfer_count": "1",
                "route_type": "minimum_time",
            }
        ],
    )


def _write_gtfs_zip(path: Path) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "stops.txt",
            "stop_id,stop_name\nS,Olympic Park\nR,Jamsil\n",
        )
        archive.writestr(
            "trips.txt",
            "\n".join(
                ["route_id,service_id,trip_id,direction_id"]
                + [f"line9,weekday,trip_{index},0" for index in range(3)]
            )
            + "\n",
        )
        rows = ["trip_id,arrival_time,departure_time,stop_id,stop_sequence"]
        for index, minute in enumerate((0, 10, 20)):
            rows.append(f"trip_{index},08:{minute:02d}:00,08:{minute:02d}:00,S,1")
            rows.append(
                f"trip_{index},08:{minute + 12:02d}:00,08:{minute + 12:02d}:00,R,2"
            )
        archive.writestr("stop_times.txt", "\n".join(rows) + "\n")


def _write_json(path: Path, value: dict[str, object]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=True, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_csv(path: Path, fieldnames: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    test_timetable_derivation_cli_uses_retained_source_metadata()
    test_headway_derivation_cli_uses_retained_source_metadata()
    test_shortest_path_derivation_cli_uses_retained_source_metadata()
    test_gtfs_derivation_cli_requires_same_feed_validator_report()
    print("\n=== REALWORLD RAIL DERIVATION SCRIPT TESTS PASSED ===")
