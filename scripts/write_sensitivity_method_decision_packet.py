"""Write the Morris-vs-Sobol sensitivity method decision packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.sensitivity import DEFAULT_MORRIS_MANIFEST_PATH  # noqa: E402
from src.realworld.sensitivity_acceptance import (  # noqa: E402
    DEFAULT_SENSITIVITY_ACCEPTANCE_PATH,
)
from src.realworld.sensitivity_index_review_packet import (  # noqa: E402
    DEFAULT_SENSITIVITY_INDEX_REVIEW_MANIFEST_PATH,
)
from src.realworld.sensitivity_method_decision_packet import (  # noqa: E402
    DEFAULT_SENSITIVITY_METHOD_DECISION_DOC_PATH,
    DEFAULT_SENSITIVITY_METHOD_DECISION_MANIFEST_PATH,
    DEFAULT_SENSITIVITY_METHOD_DECISION_PACKET_PATH,
    build_sensitivity_method_decision_rows,
    write_sensitivity_method_decision_packet,
)
from src.realworld.sensitivity_strategy_readiness_packet import (  # noqa: E402
    DEFAULT_SENSITIVITY_STRATEGY_READINESS_MANIFEST_PATH,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_sensitivity_method_decision_rows(
        morris_manifest_path=args.morris_manifest,
        index_manifest_path=args.index_manifest,
        strategy_manifest_path=args.strategy_manifest,
        acceptance_path=args.acceptance,
    )
    manifest = write_sensitivity_method_decision_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        morris_manifest_path=args.morris_manifest,
        index_manifest_path=args.index_manifest,
        strategy_manifest_path=args.strategy_manifest,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a non-approval worksheet for deciding whether current "
            "Morris screening is sufficient or Sobol analysis is required."
        )
    )
    parser.add_argument(
        "--morris-manifest",
        type=Path,
        default=DEFAULT_MORRIS_MANIFEST_PATH,
        help="Morris sensitivity manifest path.",
    )
    parser.add_argument(
        "--index-manifest",
        type=Path,
        default=DEFAULT_SENSITIVITY_INDEX_REVIEW_MANIFEST_PATH,
        help="Metric-level Morris index review manifest path.",
    )
    parser.add_argument(
        "--strategy-manifest",
        type=Path,
        default=DEFAULT_SENSITIVITY_STRATEGY_READINESS_MANIFEST_PATH,
        help="Sensitivity strategy-readiness manifest path.",
    )
    parser.add_argument(
        "--acceptance",
        type=Path,
        default=DEFAULT_SENSITIVITY_ACCEPTANCE_PATH,
        help="Formal sensitivity acceptance JSON path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_SENSITIVITY_METHOD_DECISION_PACKET_PATH,
        help="Sensitivity method-decision CSV path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_SENSITIVITY_METHOD_DECISION_MANIFEST_PATH,
        help="Sensitivity method-decision manifest path.",
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_SENSITIVITY_METHOD_DECISION_DOC_PATH,
        help="Sensitivity method-decision Markdown path.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
