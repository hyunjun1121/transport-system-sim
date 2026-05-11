"""Audit graph-scale fields across generated result manifests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.graph_scale_manifest_audit import (  # noqa: E402
    DEFAULT_AUDITED_GRAPH_SCALE_MANIFEST_PATHS,
    DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_DOC_PATH,
    DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_MANIFEST_PATH,
    DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_PATH,
    build_graph_scale_manifest_audit_rows,
    write_graph_scale_manifest_audit,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    manifest_paths = args.manifest_path or DEFAULT_AUDITED_GRAPH_SCALE_MANIFEST_PATHS
    rows = build_graph_scale_manifest_audit_rows(manifest_paths=manifest_paths)
    manifest = write_graph_scale_manifest_audit(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        audited_manifest_paths=manifest_paths,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a conservative graph-scale manifest audit. The output is a "
            "review aid only, not graph-scale acceptance."
        )
    )
    parser.add_argument(
        "--manifest-path",
        type=Path,
        action="append",
        help=(
            "Manifest path to audit. May be repeated. Defaults to current "
            "pilot, sensitivity, Morris, statistics, and figure/table manifests."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_PATH,
        help="Output CSV path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_MANIFEST_PATH,
        help="Output manifest JSON path.",
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_DOC_PATH,
        help="Output Markdown path.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
