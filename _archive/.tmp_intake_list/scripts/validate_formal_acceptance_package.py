"""Validate all formal acceptance artifacts as one package."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.formal_acceptance_package import (  # noqa: E402
    DEFAULT_FORMAL_ACCEPTANCE_PACKAGE_DOC_PATH,
    DEFAULT_FORMAL_ACCEPTANCE_PACKAGE_MANIFEST_PATH,
    write_formal_acceptance_package_audit,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate formal acceptance artifacts without creating approvals."
        )
    )
    parser.add_argument(
        "--manifest",
        default=str(DEFAULT_FORMAL_ACCEPTANCE_PACKAGE_MANIFEST_PATH),
        help="Output JSON package audit path.",
    )
    parser.add_argument(
        "--doc",
        default=str(DEFAULT_FORMAL_ACCEPTANCE_PACKAGE_DOC_PATH),
        help="Output Markdown package audit path.",
    )
    parser.add_argument(
        "--fail-on-blockers",
        action="store_true",
        help="Return non-zero unless the formal package can mark complete.",
    )
    args = parser.parse_args()

    summary = write_formal_acceptance_package_audit(
        manifest_path=args.manifest,
        doc_path=args.doc,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if args.fail_on_blockers and not summary["can_mark_complete"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
