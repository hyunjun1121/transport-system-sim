"""Write the current validation-package review packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.validation_review_packet import (  # noqa: E402
    DEFAULT_VALIDATION_REVIEW_MANIFEST_PATH,
    DEFAULT_VALIDATION_REVIEW_PACKET_PATH,
    build_validation_review_rows,
    write_validation_review_packet,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_validation_review_rows(
        route_plausibility_path=args.route_plausibility,
        fallback_benchmark_path=args.fallback_benchmarks,
        osrm_benchmark_path=args.osrm_benchmarks,
        osrm_benchmark_manifest_path=args.osrm_benchmark_manifest,
        accessibility_loss_path=args.accessibility_loss,
        route_road_evidence_exposure_path=args.route_road_evidence_exposure,
        validation_summary_path=args.validation_summary,
        validation_acceptance_path=args.validation_acceptance,
    )
    manifest = write_validation_review_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        route_plausibility_path=args.route_plausibility,
        fallback_benchmark_path=args.fallback_benchmarks,
        osrm_benchmark_path=args.osrm_benchmarks,
        osrm_benchmark_manifest_path=args.osrm_benchmark_manifest,
        accessibility_loss_path=args.accessibility_loss,
        route_road_evidence_exposure_path=args.route_road_evidence_exposure,
        validation_summary_path=args.validation_summary,
        validation_acceptance_path=args.validation_acceptance,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a conservative validation-package review packet. The output "
            "is a review aid only, not validation acceptance."
        )
    )
    parser.add_argument(
        "--route-plausibility",
        type=Path,
        default=ROOT / "data" / "validation" / "route_plausibility.csv",
    )
    parser.add_argument(
        "--fallback-benchmarks",
        type=Path,
        default=ROOT / "data" / "validation" / "external_route_benchmarks.csv",
    )
    parser.add_argument(
        "--osrm-benchmarks",
        type=Path,
        default=ROOT
        / "data"
        / "validation"
        / "external_route_benchmarks_osrm.csv",
    )
    parser.add_argument(
        "--osrm-benchmark-manifest",
        type=Path,
        default=ROOT
        / "data"
        / "validation"
        / "osrm_route_benchmark_manifest.json",
    )
    parser.add_argument(
        "--accessibility-loss",
        type=Path,
        default=ROOT / "data" / "validation" / "accessibility_loss.csv",
    )
    parser.add_argument(
        "--route-road-evidence-exposure",
        type=Path,
        default=ROOT
        / "data"
        / "validation"
        / "canonical_route_road_evidence_exposure.csv",
    )
    parser.add_argument(
        "--validation-summary",
        type=Path,
        default=ROOT / "data" / "validation" / "validation_summary.md",
    )
    parser.add_argument(
        "--validation-acceptance",
        type=Path,
        default=ROOT / "data" / "manifests" / "validation_acceptance.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_VALIDATION_REVIEW_PACKET_PATH,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_VALIDATION_REVIEW_MANIFEST_PATH,
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
