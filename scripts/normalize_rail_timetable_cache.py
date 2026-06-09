"""Normalize a reviewed static rail timetable CSV into local cache schema."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.rail_timetable_static import (  # noqa: E402
    StaticTimetableColumnMap,
    StaticTimetableSelection,
    normalize_static_timetable_csv,
)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        summary = normalize_static_timetable_csv(
            args.input,
            args.output,
            columns=StaticTimetableColumnMap(
                trip_id=args.trip_id_column,
                station_name=args.station_name_column,
                station_code=args.station_code_column,
                arrival_time=args.arrival_time_column,
                departure_time=args.departure_time_column,
                direction=args.direction_column,
                service_day=args.service_day_column,
            ),
            selection=StaticTimetableSelection(
                access_station_name=args.access_station_name,
                access_station_code=args.access_station_code,
                egress_station_name=args.egress_station_name,
                egress_station_code=args.egress_station_code,
                filters=_parse_filters(args.filter),
            ),
            encoding=args.encoding,
            manifest_path=args.manifest_output or None,
        )
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"wrote {summary['output_path']}")
    print(f"normalized_event_count: {summary['normalized_event_count']}")
    print(f"access_event_count: {summary['access_event_count']}")
    print(f"egress_event_count: {summary['egress_event_count']}")
    print(f"input_sha256: {summary['input_sha256']}")
    print(f"output_sha256: {summary['output_sha256']}")
    print(
        "claim_scope: static timetable normalization cache only; "
        "not rail evidence, not publication readiness, not final-study "
        "readiness, and not formal acceptance"
    )
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert a reviewed static rail timetable CSV into the repository "
            "rail_timetable_cache schema. All source columns must be named "
            "explicitly; this command does not infer official CSV headers."
        )
    )
    parser.add_argument("--input", required=True, help="Reviewed static source CSV")
    parser.add_argument("--output", required=True, help="Normalized timetable cache CSV")
    parser.add_argument(
        "--manifest-output",
        default="",
        help="Optional JSON summary with source/output hashes and mapping",
    )
    parser.add_argument("--encoding", default="utf-8-sig")
    parser.add_argument("--trip-id-column", required=True)
    parser.add_argument("--station-name-column", required=True)
    parser.add_argument("--station-code-column", required=True)
    parser.add_argument("--arrival-time-column", required=True)
    parser.add_argument("--departure-time-column", required=True)
    parser.add_argument("--direction-column", required=True)
    parser.add_argument("--service-day-column", required=True)
    parser.add_argument("--access-station-name", default="")
    parser.add_argument("--access-station-code", default="")
    parser.add_argument("--egress-station-name", default="")
    parser.add_argument("--egress-station-code", default="")
    parser.add_argument(
        "--filter",
        action="append",
        default=[],
        metavar="COLUMN=VALUE",
        help="Optional exact source-row filter; repeatable",
    )
    return parser.parse_args(argv)


def _parse_filters(values: list[str]) -> dict[str, str]:
    filters: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"--filter must be COLUMN=VALUE, got {value!r}")
        column, expected = value.split("=", 1)
        column = column.strip()
        if not column:
            raise ValueError(f"--filter must include a source column, got {value!r}")
        filters[column] = expected.strip()
    return filters


if __name__ == "__main__":
    raise SystemExit(main())
