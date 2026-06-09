"""Write and print the source-context raw-file hash audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.source_context_hash_audit import (  # noqa: E402
    DEFAULT_SOURCE_CONTEXT_HASH_AUDIT_DOC_PATH,
    DEFAULT_SOURCE_CONTEXT_HASH_AUDIT_MANIFEST_PATH,
    write_source_context_hash_audit,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    manifest = write_source_context_hash_audit(
        manifest_path=args.manifest,
        doc_path=args.doc,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    if args.fail_on_hash_blockers and manifest["raw_file_integrity_blocker_count"]:
        return 1
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit cached source-context raw-file SHA256 integrity. "
            "This is review support only, not provenance acceptance."
        )
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_SOURCE_CONTEXT_HASH_AUDIT_MANIFEST_PATH,
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_SOURCE_CONTEXT_HASH_AUDIT_DOC_PATH,
    )
    parser.add_argument(
        "--fail-on-hash-blockers",
        action="store_true",
        help="Return exit code 1 if any cached source-context raw hash mismatches.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
