"""Audit whether current evidence supports final-study publication claims."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.publication_readiness import audit_publication_readiness  # noqa: E402
from src.realworld.publication_readiness import (  # noqa: E402
    DEFAULT_PUBLICATION_READINESS_DOC_PATH,
    DEFAULT_PUBLICATION_READINESS_MANIFEST_PATH,
    write_publication_readiness_audit,
)


def main() -> int:
    """Print a JSON readiness audit and optionally fail on blockers."""

    args = _parse_args()
    manifest = write_publication_readiness_audit(
        manifest_path=args.manifest,
        doc_path=args.doc,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    if args.fail_on_blockers and not manifest["publication_ready"]:
        return 1
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fail-on-blockers",
        action="store_true",
        help="Return exit code 1 when final-study publication gates are blocked.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_PUBLICATION_READINESS_MANIFEST_PATH,
        help="JSON manifest output path.",
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_PUBLICATION_READINESS_DOC_PATH,
        help="Markdown output path.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
