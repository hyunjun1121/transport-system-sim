"""Write the current full-graph runtime review packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.full_graph_runtime_readiness_packet import (  # noqa: E402
    DEFAULT_FULL_GRAPH_FULL_PROFILE_MANIFEST_PATH,
    DEFAULT_FULL_GRAPH_RUNTIME_READINESS_DOC_PATH,
    DEFAULT_FULL_GRAPH_RUNTIME_READINESS_MANIFEST_PATH,
    DEFAULT_FULL_GRAPH_RUNTIME_READINESS_PACKET_PATH,
    DEFAULT_FULL_GRAPH_SMOKE_MANIFEST_PATH,
    DEFAULT_PILOT_FULL_MANIFEST_PATH,
    build_full_graph_runtime_readiness_rows,
    write_full_graph_runtime_readiness_packet,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_full_graph_runtime_readiness_rows(
        smoke_manifest_path=args.smoke_manifest,
        pilot_full_manifest_path=args.pilot_full_manifest,
        full_graph_full_profile_manifest_path=args.full_graph_full_profile_manifest,
    )
    manifest = write_full_graph_runtime_readiness_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        smoke_manifest_path=args.smoke_manifest,
        pilot_full_manifest_path=args.pilot_full_manifest,
        full_graph_full_profile_manifest_path=args.full_graph_full_profile_manifest,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write full-graph runtime review rows from current smoke and "
            "pilot full manifests. The output is a reviewer packet and does "
            "not create full-graph experiment outputs."
        )
    )
    parser.add_argument(
        "--smoke-manifest",
        type=Path,
        default=DEFAULT_FULL_GRAPH_SMOKE_MANIFEST_PATH,
        help="Full-graph smoke manifest JSON path.",
    )
    parser.add_argument(
        "--pilot-full-manifest",
        type=Path,
        default=DEFAULT_PILOT_FULL_MANIFEST_PATH,
        help="Current pilot full manifest JSON path.",
    )
    parser.add_argument(
        "--full-graph-full-profile-manifest",
        type=Path,
        default=DEFAULT_FULL_GRAPH_FULL_PROFILE_MANIFEST_PATH,
        help="Optional full-graph full-profile manifest path if generated.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_FULL_GRAPH_RUNTIME_READINESS_PACKET_PATH,
        help="Full-graph runtime review CSV path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_FULL_GRAPH_RUNTIME_READINESS_MANIFEST_PATH,
        help="Full-graph runtime review manifest JSON path.",
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_FULL_GRAPH_RUNTIME_READINESS_DOC_PATH,
        help="Full-graph runtime review Markdown path.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
