"""Write and optionally fail on lexical claim-language guard findings."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.claim_language_guard import (  # noqa: E402
    DEFAULT_CLAIM_LANGUAGE_GUARD_DOC_PATH,
    DEFAULT_CLAIM_LANGUAGE_GUARD_MANIFEST_PATH,
    DEFAULT_CLAIM_LANGUAGE_GUARD_PATH,
    build_claim_language_guard_rows,
    write_claim_language_guard,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    scan_paths = args.scan_path if args.scan_path else None
    rows = build_claim_language_guard_rows(
        scan_paths=scan_paths,
        context_window=args.context_window,
    )
    manifest = write_claim_language_guard(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        scan_paths=scan_paths,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    if args.fail_on_blockers and bool(manifest.get("release_blocked", True)):
        return 1
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write lexical claim-language guard artifacts. This is a fail-closed "
            "release guard and does not create formal acceptance."
        )
    )
    parser.add_argument(
        "--scan-path",
        action="append",
        type=Path,
        default=[],
        help="Explicit file to scan. May be repeated. Defaults to project release text and manifests.",
    )
    parser.add_argument(
        "--context-window",
        type=int,
        default=2,
        help="Neighboring line window used to identify explicit non-approval context.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_CLAIM_LANGUAGE_GUARD_PATH)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_CLAIM_LANGUAGE_GUARD_MANIFEST_PATH,
    )
    parser.add_argument("--doc", type=Path, default=DEFAULT_CLAIM_LANGUAGE_GUARD_DOC_PATH)
    parser.add_argument(
        "--fail-on-blockers",
        action="store_true",
        help="Return exit code 1 when unbounded claim-language findings remain.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
