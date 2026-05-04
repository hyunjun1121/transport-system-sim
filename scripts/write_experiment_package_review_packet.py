"""Write the current full experiment-package review packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.experiment_package_review_packet import (  # noqa: E402
    DEFAULT_EXPERIMENT_ACCEPTANCE_PATH,
    DEFAULT_EXPERIMENT_PACKAGE_REVIEW_DOC_PATH,
    DEFAULT_EXPERIMENT_PACKAGE_REVIEW_MANIFEST_PATH,
    DEFAULT_EXPERIMENT_PACKAGE_REVIEW_PACKET_PATH,
    DEFAULT_PILOT_FULL_MANIFEST_PATH,
    build_experiment_package_review_rows,
    write_experiment_package_review_packet,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_experiment_package_review_rows(
        manifest_path=args.pilot_manifest,
        experiment_acceptance_path=args.experiment_acceptance,
    )
    manifest = write_experiment_package_review_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        pilot_manifest_path=args.pilot_manifest,
        experiment_acceptance_path=args.experiment_acceptance,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write full experiment-package review rows. The output is a "
            "reviewer packet and does not create experiment acceptance."
        )
    )
    parser.add_argument(
        "--pilot-manifest",
        type=Path,
        default=DEFAULT_PILOT_FULL_MANIFEST_PATH,
        help="Full pilot manifest JSON path.",
    )
    parser.add_argument(
        "--experiment-acceptance",
        type=Path,
        default=DEFAULT_EXPERIMENT_ACCEPTANCE_PATH,
        help="Formal experiment acceptance JSON path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_EXPERIMENT_PACKAGE_REVIEW_PACKET_PATH,
        help="Experiment package review CSV path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_EXPERIMENT_PACKAGE_REVIEW_MANIFEST_PATH,
        help="Experiment package review manifest JSON path.",
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_EXPERIMENT_PACKAGE_REVIEW_DOC_PATH,
        help="Experiment package review Markdown path.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
