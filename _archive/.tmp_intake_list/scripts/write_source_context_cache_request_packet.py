"""Write the source context-cache request packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.source_context_cache_request_packet import (  # noqa: E402
    DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_DOC_PATH,
    DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_MANIFEST_PATH,
    DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_PACKET_PATH,
    build_source_context_cache_request_rows,
    write_source_context_cache_request_packet,
)
from src.realworld.source_provenance import (  # noqa: E402
    DEFAULT_SOURCE_PROVENANCE_PATH,
)
from src.realworld.source_provenance_priority_packet import (  # noqa: E402
    DEFAULT_SOURCE_PROVENANCE_PRIORITY_PACKET_PATH,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_source_context_cache_request_rows(
        source_priority_path=args.source_priority,
        provenance_manifest_path=args.provenance_manifest,
    )
    manifest = write_source_context_cache_request_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        source_priority_path=args.source_priority,
        provenance_manifest_path=args.provenance_manifest,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a source context-cache request packet. The output is review "
            "support only, not source acceptance or cached evidence."
        )
    )
    parser.add_argument(
        "--source-priority",
        type=Path,
        default=DEFAULT_SOURCE_PROVENANCE_PRIORITY_PACKET_PATH,
    )
    parser.add_argument(
        "--provenance-manifest",
        type=Path,
        default=DEFAULT_SOURCE_PROVENANCE_PATH,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_PACKET_PATH,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_MANIFEST_PATH,
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_DOC_PATH,
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
