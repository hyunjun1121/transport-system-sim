"""Derive rail-service evidence from a cached static GTFS zip or directory."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.rail_evidence import load_rail_service_evidence  # noqa: E402
from src.realworld.rail_gtfs import (  # noqa: E402
    GtfsEvidenceDerivationConfig,
    derive_rail_service_evidence_from_gtfs,
    file_sha256,
    load_cached_gtfs_feed,
)
from src.realworld.rail_timetable import write_rail_service_evidence  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    """Run the cached-GTFS derivation command."""

    args = _parse_args(argv)
    feed = load_cached_gtfs_feed(args.input)
    input_path = Path(args.input)
    record = derive_rail_service_evidence_from_gtfs(
        feed,
        GtfsEvidenceDerivationConfig(
            evidence_id=args.evidence_id,
            region_id=args.region_id,
            access_point=args.access_point,
            egress_point=args.egress_point,
            access_stop_id=args.access_stop_id,
            egress_stop_id=args.egress_stop_id,
            source_name=args.source_name,
            source_url_or_citation=args.source_url_or_citation,
            extraction_date=args.extraction_date,
            capacity_pax_per_train=args.capacity_pax_per_train,
            service_window=args.service_window,
            route_id=args.route_id,
            service_ids=tuple(args.service_id or ()),
            direction_id=args.direction_id,
            source_artifact_path=_display_path(input_path),
            source_artifact_sha256=file_sha256(input_path)
            if input_path.is_file()
            else args.source_artifact_sha256,
        ),
    )
    write_rail_service_evidence([record], args.output)
    load_rail_service_evidence(args.output)
    print(f"wrote {args.output}")
    print("source_status: cached_gtfs_derived")
    print(
        "claim_scope: cached GTFS-derived rail timing evidence; "
        "capacity remains sensitivity-only unless separately sourced; "
        "not operational forecast"
    )
    if input_path.is_file():
        print(f"source_artifact_sha256: {file_sha256(input_path)}")
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Derive one rail-service evidence row from a cached static GTFS "
            "zip or directory. This command does not call live APIs."
        )
    )
    parser.add_argument("--input", required=True, help="Cached GTFS zip or directory")
    parser.add_argument("--output", required=True, help="Output rail evidence CSV path")
    parser.add_argument("--evidence-id", required=True)
    parser.add_argument("--region-id", default="songpa_public_demo")
    parser.add_argument("--access-point", default="S")
    parser.add_argument("--egress-point", default="R")
    parser.add_argument("--access-stop-id", required=True)
    parser.add_argument("--egress-stop-id", required=True)
    parser.add_argument("--source-name", required=True)
    parser.add_argument("--source-url-or-citation", required=True)
    parser.add_argument("--extraction-date", required=True)
    parser.add_argument("--capacity-pax-per-train", type=float, required=True)
    parser.add_argument("--service-window", required=True)
    parser.add_argument("--route-id", default="")
    parser.add_argument("--service-id", action="append", default=[])
    parser.add_argument("--direction-id", default="")
    parser.add_argument(
        "--source-artifact-sha256",
        default="",
        help=(
            "Required only when --input is a directory. Zip inputs are hashed "
            "directly and should be preferred for final reproducibility."
        ),
    )
    args = parser.parse_args(argv)
    input_path = Path(args.input)
    if input_path.is_dir() and not args.source_artifact_sha256:
        parser.error(
            "--source-artifact-sha256 is required when --input is a directory; "
            "prefer a reviewed GTFS zip for final evidence"
        )
    return args


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
