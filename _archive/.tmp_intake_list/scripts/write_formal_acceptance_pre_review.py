"""Write draft-only formal acceptance pre-review recommendations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.formal_acceptance_pre_review import (  # noqa: E402
    DEFAULT_PRE_REVIEW_DOC_PATH,
    DEFAULT_PRE_REVIEW_DIR,
    DEFAULT_PRE_REVIEW_MANIFEST_PATH,
    write_formal_acceptance_pre_review,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_PRE_REVIEW_DIR),
        help="Draft recommendation JSON output directory.",
    )
    parser.add_argument(
        "--manifest",
        default=str(DEFAULT_PRE_REVIEW_MANIFEST_PATH),
        help="Draft pre-review manifest path.",
    )
    parser.add_argument(
        "--doc",
        default=str(DEFAULT_PRE_REVIEW_DOC_PATH),
        help="Markdown pre-review report path.",
    )
    args = parser.parse_args()

    summary = write_formal_acceptance_pre_review(
        output_dir=args.output_dir,
        manifest_path=args.manifest,
        doc_path=args.doc,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
