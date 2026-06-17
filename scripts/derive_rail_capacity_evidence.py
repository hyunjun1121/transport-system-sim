"""Derive rail capacity evidence from a cached Metro9 operator-page extract."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.metro9_capacity_source import (  # noqa: E402
    DEFAULT_METRO9_CAPACITY_EXTRACT_PATH,
    load_metro9_capacity_extract,
)
from src.realworld.rail_evidence import (  # noqa: E402
    RailServiceEvidence,
    load_rail_service_evidence,
)
from src.realworld.rail_timetable import (  # noqa: E402
    file_sha256,
    write_rail_service_evidence,
)


def main(argv: list[str] | None = None) -> int:
    """Derive one capacity evidence row from a cached Metro9 extract."""

    args = _parse_args(argv)
    rows = load_metro9_capacity_extract(args.input)
    extract_row = rows[0]
    capacity_str = extract_row.get("total_capacity_6_cars", "")
    if not capacity_str:
        raise ValueError("Metro9 extract has no total_capacity_6_cars value")
    capacity = float(capacity_str)
    if capacity <= 0.0:
        raise ValueError(f"invalid capacity {capacity_str!r}")

    input_path = Path(args.input)
    source_sha256 = file_sha256(input_path)
    source_artifact_path = _display_path(input_path)

    seats = extract_row.get("seats_6_cars", "")
    standing = extract_row.get("standing_6_cars", "")
    configuration = extract_row.get("configuration", "")
    review_status = extract_row.get("review_status", "")
    source_url = extract_row.get("source_url", "")

    record = RailServiceEvidence(
        evidence_id=args.evidence_id,
        region_id=args.region_id,
        access_point=args.access_point,
        egress_point=args.egress_point,
        access_station_name=args.access_station_name,
        egress_station_name=args.egress_station_name,
        source_status="documented_public_source_available",
        source_name=f"Metro9 operator rolling-stock page ({configuration})",
        source_url_or_citation=(
            f"{source_url}; {source_artifact_path}"
        ),
        extraction_date=args.extraction_date,
        headway_min=args.headway_proxy,
        travel_time_min=args.travel_time_proxy,
        capacity_pax_per_train=capacity,
        service_window=args.service_window,
        claim_scope=(
            "not calibrated; cached Metro9 operator-page capacity value "
            f"({review_status}); capacity remains sensitivity-only; "
            "not operational forecast"
        ),
        notes=(
            f"Capacity {int(capacity)} pax for 6-car train set "
            f"(seats={seats}, standing={standing}) extracted from "
            f"cached operator page. Headway and travel_time are carried "
            f"proxies, not derived fields."
            f" source_artifact_path={source_artifact_path};"
            f" source_artifact_sha256={source_sha256}."
        ),
        derived_fields="",
        source_artifact_path=source_artifact_path,
        source_artifact_sha256=source_sha256,
    )
    write_rail_service_evidence([record], args.output)
    load_rail_service_evidence(args.output)
    print(f"wrote {args.output}")
    print("source_status: documented_public_source_available")
    print(f"capacity_pax_per_train: {int(capacity)}")
    print(f"source_artifact_sha256: {source_sha256}")
    print(
        "claim_scope: not calibrated; capacity remains sensitivity-only; "
        "pending formal source review"
    )
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Derive one rail-capacity evidence row from a cached Metro9 "
            "operator-page extract CSV. This command does not call live APIs."
        )
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_METRO9_CAPACITY_EXTRACT_PATH),
        help="Metro9 capacity extract CSV path",
    )
    parser.add_argument("--output", required=True, help="Output rail evidence CSV path")
    parser.add_argument("--evidence-id", required=True)
    parser.add_argument("--region-id", default="songpa_public_demo")
    parser.add_argument("--access-point", default="S")
    parser.add_argument("--egress-point", default="R")
    parser.add_argument("--access-station-name", default="Olympic Park Station area")
    parser.add_argument("--egress-station-name", default="Jamsil Station area")
    parser.add_argument("--extraction-date", required=True)
    parser.add_argument("--headway-proxy", type=float, default=10.0)
    parser.add_argument("--travel-time-proxy", type=float, default=20.0)
    parser.add_argument("--service-window", default="scheduled public service")
    return parser.parse_args(argv)


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
