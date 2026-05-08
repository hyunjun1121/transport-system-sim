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
