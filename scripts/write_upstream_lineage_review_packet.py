"""Write the Phase 9 upstream lineage review packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.upstream_lineage_review_packet import (  # noqa: E402
    DEFAULT_ACTION_QUEUE_PATH,
    DEFAULT_DOC_PATH,
    DEFAULT_MANIFEST_PATH,
    DEFAULT_OUTPUT_PATH,
    write_upstream_lineage_review_packet,
)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    manifest = write_upstream_lineage_review_packet(
        action_queue_path=args.action_queue,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a reviewer packet for Phase 9 upstream evidence and benchmark "
            "lineage. The output is review support only, not closeout or signoff."
        )
    )
    parser.add_argument("--action-queue", type=Path, default=DEFAULT_ACTION_QUEUE_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    parser.add_argument("--doc", type=Path, default=DEFAULT_DOC_PATH)
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
