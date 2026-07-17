"""Write the experiment design decision packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.experiment_acceptance import (  # noqa: E402
    DEFAULT_EXPERIMENT_ACCEPTANCE_PATH,
)
from src.realworld.experiment_design_decision_packet import (  # noqa: E402
    DEFAULT_EXPERIMENT_DESIGN_DECISION_DOC_PATH,
    DEFAULT_EXPERIMENT_DESIGN_DECISION_MANIFEST_PATH,
    DEFAULT_EXPERIMENT_DESIGN_DECISION_PACKET_PATH,
    DEFAULT_GRAPH_SCALE_ACCEPTANCE_PATH,
    DEFAULT_PILOT_EXPERIMENT_DESIGN_PATH,
    DEFAULT_PILOT_MULTI_CORRIDOR_FULL_MANIFEST_PATH,
    DEFAULT_PILOT_MULTI_CORRIDOR_MANIFEST_PATH,
    DEFAULT_PILOT_SAMPLE_MANIFEST_PATH,
    DEFAULT_PILOT_STAGED_MANIFEST_PATH,
    build_experiment_design_decision_rows,
    write_experiment_design_decision_packet,
)
from src.realworld.experiment_package_review_packet import (  # noqa: E402
    DEFAULT_EXPERIMENT_PACKAGE_REVIEW_MANIFEST_PATH,
    DEFAULT_PILOT_FULL_MANIFEST_PATH,
)
from src.realworld.experiment_strategy_readiness_packet import (  # noqa: E402
    DEFAULT_EXPERIMENT_STRATEGY_READINESS_MANIFEST_PATH,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_experiment_design_decision_rows(
        sample_manifest_path=args.sample_manifest,
        staged_manifest_path=args.staged_manifest,
        full_manifest_path=args.full_manifest,
        multi_corridor_manifest_path=args.multi_corridor_manifest,
        multi_corridor_full_manifest_path=args.multi_corridor_full_manifest,
        design_path=args.design,
        package_manifest_path=args.package_manifest,
        strategy_manifest_path=args.strategy_manifest,
        graph_scale_acceptance_path=args.graph_scale_acceptance,
        experiment_acceptance_path=args.experiment_acceptance,
    )
    manifest = write_experiment_design_decision_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        sample_manifest_path=args.sample_manifest,
        staged_manifest_path=args.staged_manifest,
        full_manifest_path=args.full_manifest,
        multi_corridor_manifest_path=args.multi_corridor_manifest,
        multi_corridor_full_manifest_path=args.multi_corridor_full_manifest,
        design_path=args.design,
        package_manifest_path=args.package_manifest,
        strategy_manifest_path=args.strategy_manifest,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a non-approval worksheet for experiment run-profile and "
            "scenario-policy-seed design decisions."
        )
    )
    parser.add_argument(
        "--sample-manifest",
        type=Path,
        default=DEFAULT_PILOT_SAMPLE_MANIFEST_PATH,
    )
    parser.add_argument(
        "--staged-manifest",
        type=Path,
        default=DEFAULT_PILOT_STAGED_MANIFEST_PATH,
    )
    parser.add_argument(
        "--full-manifest",
        type=Path,
        default=DEFAULT_PILOT_FULL_MANIFEST_PATH,
    )
    parser.add_argument(
        "--multi-corridor-manifest",
        type=Path,
        default=DEFAULT_PILOT_MULTI_CORRIDOR_MANIFEST_PATH,
    )
    parser.add_argument(
        "--multi-corridor-full-manifest",
        type=Path,
        default=DEFAULT_PILOT_MULTI_CORRIDOR_FULL_MANIFEST_PATH,
    )
    parser.add_argument(
        "--design",
        type=Path,
        default=DEFAULT_PILOT_EXPERIMENT_DESIGN_PATH,
    )
    parser.add_argument(
        "--package-manifest",
        type=Path,
        default=DEFAULT_EXPERIMENT_PACKAGE_REVIEW_MANIFEST_PATH,
    )
    parser.add_argument(
        "--strategy-manifest",
        type=Path,
        default=DEFAULT_EXPERIMENT_STRATEGY_READINESS_MANIFEST_PATH,
    )
    parser.add_argument(
        "--graph-scale-acceptance",
        type=Path,
        default=DEFAULT_GRAPH_SCALE_ACCEPTANCE_PATH,
    )
    parser.add_argument(
        "--experiment-acceptance",
        type=Path,
        default=DEFAULT_EXPERIMENT_ACCEPTANCE_PATH,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_EXPERIMENT_DESIGN_DECISION_PACKET_PATH,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_EXPERIMENT_DESIGN_DECISION_MANIFEST_PATH,
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_EXPERIMENT_DESIGN_DECISION_DOC_PATH,
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
