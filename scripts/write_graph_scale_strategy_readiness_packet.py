"""Write the current graph-scale strategy review packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.graph_scale_review import (  # noqa: E402
    DEFAULT_GRAPH_SCALE_REVIEW_PACKET_PATH,
)
from src.realworld.graph_scale_strategy_readiness_packet import (  # noqa: E402
    DEFAULT_FULL_GRAPH_RUNTIME_READINESS_MANIFEST_PATH,
    DEFAULT_GRAPH_SCALE_ACCEPTANCE_PATH,
    DEFAULT_GRAPH_SCALE_RESULT_COMPARISON_MANIFEST_PATH,
    DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_DOC_PATH,
    DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_MANIFEST_PATH,
    DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_PACKET_PATH,
    build_graph_scale_strategy_readiness_rows,
    write_graph_scale_strategy_readiness_packet,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_graph_scale_strategy_readiness_rows(
        review_packet_path=args.review_packet,
        result_comparison_manifest_path=args.result_comparison_manifest,
        acceptance_path=args.acceptance,
    )
    manifest = write_graph_scale_strategy_readiness_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        review_packet_path=args.review_packet,
        result_comparison_manifest_path=args.result_comparison_manifest,
        full_graph_runtime_readiness_manifest_path=args.full_graph_runtime_readiness_manifest,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write graph-scale strategy review rows from the current "
            "graph-scale review packet. The output is a reviewer packet and "
            "does not accept a graph-scale method."
        )
    )
    parser.add_argument(
        "--review-packet",
        type=Path,
        default=DEFAULT_GRAPH_SCALE_REVIEW_PACKET_PATH,
        help="Graph-scale review packet CSV path.",
    )
    parser.add_argument(
        "--result-comparison-manifest",
        type=Path,
        default=DEFAULT_GRAPH_SCALE_RESULT_COMPARISON_MANIFEST_PATH,
        help="Graph-scale result-comparison manifest JSON path.",
    )
    parser.add_argument(
        "--acceptance",
        type=Path,
        default=DEFAULT_GRAPH_SCALE_ACCEPTANCE_PATH,
        help="Formal graph-scale acceptance JSON path.",
    )
    parser.add_argument(
        "--full-graph-runtime-readiness-manifest",
        type=Path,
        default=DEFAULT_FULL_GRAPH_RUNTIME_READINESS_MANIFEST_PATH,
        help="Full-graph runtime review manifest JSON path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_PACKET_PATH,
        help="Graph-scale strategy review CSV path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_MANIFEST_PATH,
        help="Graph-scale strategy review manifest JSON path.",
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_DOC_PATH,
        help="Graph-scale strategy review Markdown path.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
