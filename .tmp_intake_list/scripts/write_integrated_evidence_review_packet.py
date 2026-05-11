"""Write the integrated E2/E3/E5 evidence review packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.integrated_evidence_review_packet import (  # noqa: E402
    DEFAULT_EXPERIMENT_DESIGN_DECISION_MANIFEST_PATH,
    DEFAULT_INTEGRATED_EVIDENCE_REVIEW_DOC_PATH,
    DEFAULT_INTEGRATED_EVIDENCE_REVIEW_MANIFEST_PATH,
    DEFAULT_INTEGRATED_EVIDENCE_REVIEW_PACKET_PATH,
    DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH,
    DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_MANIFEST_PATH,
    DEFAULT_SOURCE_PROVENANCE_DECISION_MANIFEST_PATH,
    DEFAULT_VALIDATION_BENCHMARK_DECISION_MANIFEST_PATH,
    DEFAULT_VALIDATION_STRATEGY_READINESS_MANIFEST_PATH,
    build_integrated_evidence_review_rows,
    write_integrated_evidence_review_packet,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_integrated_evidence_review_rows(
        rail_source_decision_manifest_path=args.rail_source_decision_manifest,
        validation_benchmark_decision_manifest_path=(
            args.validation_benchmark_decision_manifest
        ),
        validation_strategy_readiness_manifest_path=(
            args.validation_strategy_readiness_manifest
        ),
        experiment_design_decision_manifest_path=(
            args.experiment_design_decision_manifest
        ),
        source_context_cache_decision_manifest_path=(
            args.source_context_cache_decision_manifest
        ),
        source_provenance_decision_manifest_path=(
            args.source_provenance_decision_manifest
        ),
    )
    manifest = write_integrated_evidence_review_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        rail_source_decision_manifest_path=args.rail_source_decision_manifest,
        validation_benchmark_decision_manifest_path=(
            args.validation_benchmark_decision_manifest
        ),
        validation_strategy_readiness_manifest_path=(
            args.validation_strategy_readiness_manifest
        ),
        experiment_design_decision_manifest_path=(
            args.experiment_design_decision_manifest
        ),
        source_context_cache_decision_manifest_path=(
            args.source_context_cache_decision_manifest
        ),
        source_provenance_decision_manifest_path=(
            args.source_provenance_decision_manifest
        ),
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a non-approval integrated E2/E3/E5 evidence review packet."
        )
    )
    parser.add_argument(
        "--rail-source-decision-manifest",
        type=Path,
        default=DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH,
    )
    parser.add_argument(
        "--validation-benchmark-decision-manifest",
        type=Path,
        default=DEFAULT_VALIDATION_BENCHMARK_DECISION_MANIFEST_PATH,
    )
    parser.add_argument(
        "--validation-strategy-readiness-manifest",
        type=Path,
        default=DEFAULT_VALIDATION_STRATEGY_READINESS_MANIFEST_PATH,
    )
    parser.add_argument(
        "--experiment-design-decision-manifest",
        type=Path,
        default=DEFAULT_EXPERIMENT_DESIGN_DECISION_MANIFEST_PATH,
    )
    parser.add_argument(
        "--source-context-cache-decision-manifest",
        type=Path,
        default=DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_MANIFEST_PATH,
    )
    parser.add_argument(
        "--source-provenance-decision-manifest",
        type=Path,
        default=DEFAULT_SOURCE_PROVENANCE_DECISION_MANIFEST_PATH,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_INTEGRATED_EVIDENCE_REVIEW_PACKET_PATH,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_INTEGRATED_EVIDENCE_REVIEW_MANIFEST_PATH,
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_INTEGRATED_EVIDENCE_REVIEW_DOC_PATH,
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
