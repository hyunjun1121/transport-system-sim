"""Write the current experiment strategy review packet."""

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
from src.realworld.experiment_package_review_packet import (  # noqa: E402
    DEFAULT_EXPERIMENT_PACKAGE_REVIEW_PACKET_PATH,
)
from src.realworld.experiment_strategy_readiness_packet import (  # noqa: E402
    DEFAULT_EXPERIMENT_STRATEGY_READINESS_DOC_PATH,
    DEFAULT_EXPERIMENT_STRATEGY_READINESS_MANIFEST_PATH,
    DEFAULT_EXPERIMENT_STRATEGY_READINESS_PACKET_PATH,
    build_experiment_strategy_readiness_rows,
    write_experiment_strategy_readiness_packet,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_experiment_strategy_readiness_rows(
        review_packet_path=args.review_packet,
        acceptance_path=args.acceptance,
    )
    manifest = write_experiment_strategy_readiness_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        review_packet_path=args.review_packet,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write experiment strategy review rows from the current "
            "experiment-package review packet. The output is a reviewer "
            "packet and does not accept the experiment package."
        )
    )
    parser.add_argument(
        "--review-packet",
        type=Path,
        default=DEFAULT_EXPERIMENT_PACKAGE_REVIEW_PACKET_PATH,
        help="Experiment package review packet CSV path.",
    )
    parser.add_argument(
        "--acceptance",
        type=Path,
        default=DEFAULT_EXPERIMENT_ACCEPTANCE_PATH,
        help="Formal experiment acceptance JSON path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_EXPERIMENT_STRATEGY_READINESS_PACKET_PATH,
        help="Experiment strategy review CSV path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_EXPERIMENT_STRATEGY_READINESS_MANIFEST_PATH,
        help="Experiment strategy review manifest JSON path.",
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_EXPERIMENT_STRATEGY_READINESS_DOC_PATH,
        help="Experiment strategy review Markdown path.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
