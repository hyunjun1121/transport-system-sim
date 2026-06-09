"""Write Phase 8 pre-compact policy and benchmark guardrail tables."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.phase8_precompact_tables import (  # noqa: E402
    DEFAULT_BENCHMARK_THRESHOLD_DOC_PATH,
    DEFAULT_BENCHMARK_THRESHOLD_MANIFEST_PATH,
    DEFAULT_BENCHMARK_THRESHOLD_TABLE_PATH,
    DEFAULT_FALLBACK_BENCHMARK_PATH,
    DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH,
    DEFAULT_OSRM_BENCHMARK_PATH,
    DEFAULT_PILOT_DESIGN_PATH,
    DEFAULT_POLICY_ALTERNATIVES_PATH,
    DEFAULT_POLICY_FEASIBILITY_DOC_PATH,
    DEFAULT_POLICY_FEASIBILITY_MANIFEST_PATH,
    DEFAULT_POLICY_FEASIBILITY_TABLE_PATH,
    DEFAULT_REGION_PATH,
    write_phase8_precompact_tables,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    manifest = write_phase8_precompact_tables(
        policy_output_path=args.policy_output,
        policy_manifest_path=args.policy_manifest,
        policy_doc_path=args.policy_doc,
        benchmark_output_path=args.benchmark_output,
        benchmark_manifest_path=args.benchmark_manifest,
        benchmark_doc_path=args.benchmark_doc,
        policy_path=args.policy_alternatives,
        design_path=args.pilot_design,
        region_path=args.region_path,
        fallback_benchmark_path=args.fallback_benchmark,
        osrm_benchmark_path=args.osrm_benchmark,
        osrm_manifest_path=args.osrm_manifest,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write Phase 8 pre-compact feasibility/fairness and benchmark "
            "threshold review tables. Outputs are review support only."
        )
    )
    parser.add_argument(
        "--policy-alternatives",
        type=Path,
        default=DEFAULT_POLICY_ALTERNATIVES_PATH,
    )
    parser.add_argument(
        "--pilot-design",
        type=Path,
        default=DEFAULT_PILOT_DESIGN_PATH,
    )
    parser.add_argument(
        "--region-path",
        type=Path,
        default=DEFAULT_REGION_PATH,
    )
    parser.add_argument(
        "--fallback-benchmark",
        type=Path,
        default=DEFAULT_FALLBACK_BENCHMARK_PATH,
    )
    parser.add_argument(
        "--osrm-benchmark",
        type=Path,
        default=DEFAULT_OSRM_BENCHMARK_PATH,
    )
    parser.add_argument(
        "--osrm-manifest",
        type=Path,
        default=DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH,
    )
    parser.add_argument(
        "--policy-output",
        type=Path,
        default=DEFAULT_POLICY_FEASIBILITY_TABLE_PATH,
    )
    parser.add_argument(
        "--policy-manifest",
        type=Path,
        default=DEFAULT_POLICY_FEASIBILITY_MANIFEST_PATH,
    )
    parser.add_argument(
        "--policy-doc",
        type=Path,
        default=DEFAULT_POLICY_FEASIBILITY_DOC_PATH,
    )
    parser.add_argument(
        "--benchmark-output",
        type=Path,
        default=DEFAULT_BENCHMARK_THRESHOLD_TABLE_PATH,
    )
    parser.add_argument(
        "--benchmark-manifest",
        type=Path,
        default=DEFAULT_BENCHMARK_THRESHOLD_MANIFEST_PATH,
    )
    parser.add_argument(
        "--benchmark-doc",
        type=Path,
        default=DEFAULT_BENCHMARK_THRESHOLD_DOC_PATH,
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
