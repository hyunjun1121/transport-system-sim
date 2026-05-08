"""Write the source context-cache decision packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.source_context_cache_decision_packet import (  # noqa: E402
    DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_DOC_PATH,
    DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_MANIFEST_PATH,
    DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_PACKET_PATH,
    build_source_context_cache_decision_rows,
    write_source_context_cache_decision_packet,
)
from src.realworld.source_context_cache_request_packet import (  # noqa: E402
    DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_MANIFEST_PATH,
    DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_PACKET_PATH,
)
from src.realworld.source_provenance import DEFAULT_SOURCE_PROVENANCE_PATH  # noqa: E402
from src.realworld.source_provenance_priority_packet import (  # noqa: E402
    DEFAULT_SOURCE_PROVENANCE_PRIORITY_PACKET_PATH,
)
from src.realworld.source_url_remediation_packet import (  # noqa: E402
    DEFAULT_SOURCE_URL_REMEDIATION_PACKET_PATH,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_source_context_cache_decision_rows(
        request_packet_path=args.request_packet,
        request_manifest_path=args.request_manifest,
        source_priority_packet_path=args.source_priority_packet,
        source_url_remediation_packet_path=args.source_url_remediation_packet,
        provenance_manifest_path=args.provenance_manifest,
    )
    manifest = write_source_context_cache_decision_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        request_packet_path=args.request_packet,
        request_manifest_path=args.request_manifest,
        source_priority_packet_path=args.source_priority_packet,
        source_url_remediation_packet_path=args.source_url_remediation_packet,
        provenance_manifest_path=args.provenance_manifest,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a source context-cache decision packet. The output is "
            "review support only, not provenance acceptance."
        )
    )
    parser.add_argument(
        "--request-packet",
        type=Path,
        default=DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_PACKET_PATH,
    )
    parser.add_argument(
        "--request-manifest",
        type=Path,
        default=DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_MANIFEST_PATH,
    )
    parser.add_argument(
        "--source-priority-packet",
        type=Path,
        default=DEFAULT_SOURCE_PROVENANCE_PRIORITY_PACKET_PATH,
    )
    parser.add_argument(
        "--source-url-remediation-packet",
        type=Path,
        default=DEFAULT_SOURCE_URL_REMEDIATION_PACKET_PATH,
    )
    parser.add_argument(
        "--provenance-manifest",
        type=Path,
        default=DEFAULT_SOURCE_PROVENANCE_PATH,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_PACKET_PATH,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_MANIFEST_PATH,
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_DOC_PATH,
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
