"""Write the validation benchmark decision packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.validation_acceptance import (  # noqa: E402
    DEFAULT_VALIDATION_ACCEPTANCE_PATH,
)
from src.realworld.road_evidence_priority_packet import (  # noqa: E402
    DEFAULT_ROAD_EVIDENCE_PRIORITY_MANIFEST_PATH,
    DEFAULT_ROAD_EVIDENCE_PRIORITY_PACKET_PATH,
)
from src.realworld.route_road_evidence_exposure import (  # noqa: E402
    DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_MANIFEST_PATH,
    DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_PATH,
)
from src.realworld.validation_benchmark_decision_packet import (  # noqa: E402
    DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH,
    DEFAULT_VALIDATION_BENCHMARK_DECISION_DOC_PATH,
    DEFAULT_VALIDATION_BENCHMARK_DECISION_MANIFEST_PATH,
    DEFAULT_VALIDATION_BENCHMARK_DECISION_PACKET_PATH,
    DEFAULT_VALIDATION_REVIEW_MANIFEST_PATH,
    build_validation_benchmark_decision_rows,
    write_validation_benchmark_decision_packet,
)
from src.realworld.validation_benchmark_readiness_packet import (  # noqa: E402
    DEFAULT_VALIDATION_BENCHMARK_READINESS_MANIFEST_PATH,
)
from src.realworld.validation_strategy_readiness_packet import (  # noqa: E402
    DEFAULT_VALIDATION_STRATEGY_READINESS_MANIFEST_PATH,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_validation_benchmark_decision_rows(
        validation_review_manifest_path=args.validation_review_manifest,
        benchmark_readiness_manifest_path=args.benchmark_readiness_manifest,
        strategy_readiness_manifest_path=args.strategy_readiness_manifest,
        osrm_benchmark_manifest_path=args.osrm_benchmark_manifest,
        validation_acceptance_path=args.validation_acceptance,
        route_exposure_path=args.route_exposure,
        route_exposure_manifest_path=args.route_exposure_manifest,
        road_evidence_priority_path=args.road_evidence_priority,
        road_evidence_priority_manifest_path=args.road_evidence_priority_manifest,
    )
    manifest = write_validation_benchmark_decision_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        validation_review_manifest_path=args.validation_review_manifest,
        benchmark_readiness_manifest_path=args.benchmark_readiness_manifest,
        strategy_readiness_manifest_path=args.strategy_readiness_manifest,
        osrm_benchmark_manifest_path=args.osrm_benchmark_manifest,
        route_exposure_path=args.route_exposure,
        route_exposure_manifest_path=args.route_exposure_manifest,
        road_evidence_priority_path=args.road_evidence_priority,
        road_evidence_priority_manifest_path=args.road_evidence_priority_manifest,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a validation benchmark decision packet. The output is "
            "review support only, not validation acceptance."
        )
    )
    parser.add_argument(
        "--validation-review-manifest",
        type=Path,
        default=DEFAULT_VALIDATION_REVIEW_MANIFEST_PATH,
    )
    parser.add_argument(
        "--benchmark-readiness-manifest",
        type=Path,
        default=DEFAULT_VALIDATION_BENCHMARK_READINESS_MANIFEST_PATH,
    )
    parser.add_argument(
        "--strategy-readiness-manifest",
        type=Path,
        default=DEFAULT_VALIDATION_STRATEGY_READINESS_MANIFEST_PATH,
    )
    parser.add_argument(
        "--osrm-benchmark-manifest",
        type=Path,
        default=DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH,
    )
    parser.add_argument(
        "--validation-acceptance",
        type=Path,
        default=DEFAULT_VALIDATION_ACCEPTANCE_PATH,
    )
    parser.add_argument(
        "--route-exposure",
        type=Path,
        default=DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_PATH,
    )
    parser.add_argument(
        "--route-exposure-manifest",
        type=Path,
        default=DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_MANIFEST_PATH,
    )
    parser.add_argument(
        "--road-evidence-priority",
        type=Path,
        default=DEFAULT_ROAD_EVIDENCE_PRIORITY_PACKET_PATH,
    )
    parser.add_argument(
        "--road-evidence-priority-manifest",
        type=Path,
        default=DEFAULT_ROAD_EVIDENCE_PRIORITY_MANIFEST_PATH,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_VALIDATION_BENCHMARK_DECISION_PACKET_PATH,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_VALIDATION_BENCHMARK_DECISION_MANIFEST_PATH,
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_VALIDATION_BENCHMARK_DECISION_DOC_PATH,
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
