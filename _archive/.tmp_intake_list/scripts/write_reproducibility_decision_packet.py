"""Write the reproducibility decision packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.clean_checkout_smoke import (  # noqa: E402
    DEFAULT_CLEAN_CHECKOUT_SMOKE_MANIFEST_PATH,
)
from src.realworld.reproducibility_acceptance import (  # noqa: E402
    DEFAULT_REPRODUCIBILITY_ACCEPTANCE_PATH,
)
from src.realworld.reproducibility_decision_packet import (  # noqa: E402
    DEFAULT_REPRODUCIBILITY_DECISION_DOC_PATH,
    DEFAULT_REPRODUCIBILITY_DECISION_MANIFEST_PATH,
    DEFAULT_REPRODUCIBILITY_DECISION_PACKET_PATH,
    build_reproducibility_decision_rows,
    write_reproducibility_decision_packet,
)
from src.realworld.reproducibility_review_packet import (  # noqa: E402
    DEFAULT_REPRODUCIBILITY_MANIFEST_PATH,
    DEFAULT_REPRODUCIBILITY_REVIEW_MANIFEST_PATH,
)
from src.realworld.reproducibility_smoke import (  # noqa: E402
    DEFAULT_REPRODUCIBILITY_SMOKE_MANIFEST_PATH,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_reproducibility_decision_rows(
        reproducibility_manifest_path=args.reproducibility_manifest,
        reproducibility_review_manifest_path=args.reproducibility_review_manifest,
        reproducibility_smoke_manifest_path=args.reproducibility_smoke_manifest,
        clean_checkout_smoke_manifest_path=args.clean_checkout_smoke_manifest,
        reproducibility_acceptance_path=args.reproducibility_acceptance,
    )
    manifest = write_reproducibility_decision_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        reproducibility_manifest_path=args.reproducibility_manifest,
        reproducibility_review_manifest_path=args.reproducibility_review_manifest,
        reproducibility_smoke_manifest_path=args.reproducibility_smoke_manifest,
        clean_checkout_smoke_manifest_path=args.clean_checkout_smoke_manifest,
        reproducibility_acceptance_path=args.reproducibility_acceptance,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a non-approval worksheet for reproducibility manifest, "
            "clean-checkout, command-ladder, artifact-regeneration, and "
            "formal acceptance-boundary decisions."
        )
    )
    parser.add_argument(
        "--reproducibility-manifest",
        type=Path,
        default=DEFAULT_REPRODUCIBILITY_MANIFEST_PATH,
    )
    parser.add_argument(
        "--reproducibility-review-manifest",
        type=Path,
        default=DEFAULT_REPRODUCIBILITY_REVIEW_MANIFEST_PATH,
    )
    parser.add_argument(
        "--reproducibility-smoke-manifest",
        type=Path,
        default=DEFAULT_REPRODUCIBILITY_SMOKE_MANIFEST_PATH,
    )
    parser.add_argument(
        "--clean-checkout-smoke-manifest",
        type=Path,
        default=DEFAULT_CLEAN_CHECKOUT_SMOKE_MANIFEST_PATH,
    )
    parser.add_argument(
        "--reproducibility-acceptance",
        type=Path,
        default=DEFAULT_REPRODUCIBILITY_ACCEPTANCE_PATH,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_REPRODUCIBILITY_DECISION_PACKET_PATH,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_REPRODUCIBILITY_DECISION_MANIFEST_PATH,
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_REPRODUCIBILITY_DECISION_DOC_PATH,
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
