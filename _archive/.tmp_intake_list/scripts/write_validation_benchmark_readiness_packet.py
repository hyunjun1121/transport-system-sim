"""Write the validation benchmark readiness packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.validation_benchmark_readiness_packet import (  # noqa: E402
    DEFAULT_FALLBACK_BENCHMARK_PATH,
    DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH,
    DEFAULT_OSRM_BENCHMARK_PATH,
    DEFAULT_VALIDATION_ACCEPTANCE_PATH,
    DEFAULT_VALIDATION_BENCHMARK_READINESS_DOC_PATH,
    DEFAULT_VALIDATION_BENCHMARK_READINESS_MANIFEST_PATH,
    DEFAULT_VALIDATION_BENCHMARK_READINESS_PACKET_PATH,
    build_validation_benchmark_readiness_rows,
    write_validation_benchmark_readiness_packet,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_validation_benchmark_readiness_rows(
        fallback_benchmark_path=args.fallback_benchmarks,
        osrm_benchmark_path=args.osrm_benchmarks,
        osrm_benchmark_manifest_path=args.osrm_benchmark_manifest,
        validation_acceptance_path=args.validation_acceptance,
    )
    manifest = write_validation_benchmark_readiness_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        fallback_benchmark_path=args.fallback_benchmarks,
        osrm_benchmark_path=args.osrm_benchmarks,
        osrm_benchmark_manifest_path=args.osrm_benchmark_manifest,
        validation_acceptance_path=args.validation_acceptance,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a conservative validation benchmark readiness packet. The "
            "output is a review aid only, not validation acceptance."
        )
    )
    parser.add_argument(
        "--fallback-benchmarks",
        type=Path,
        default=DEFAULT_FALLBACK_BENCHMARK_PATH,
    )
    parser.add_argument(
        "--osrm-benchmarks",
        type=Path,
        default=DEFAULT_OSRM_BENCHMARK_PATH,
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
        default=DEFAULT_VALIDATION_BENCHMARK_READINESS_PACKET_PATH,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_VALIDATION_BENCHMARK_READINESS_MANIFEST_PATH,
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_VALIDATION_BENCHMARK_READINESS_DOC_PATH,
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
