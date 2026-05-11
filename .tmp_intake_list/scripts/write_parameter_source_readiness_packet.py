"""Write the current parameter source-readiness packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.parameter_evidence_request_packet import (  # noqa: E402
    DEFAULT_PARAMETER_EVIDENCE_SOURCE_REQUEST_PACKET_PATH,
)
from src.realworld.parameter_source_readiness_packet import (  # noqa: E402
    DEFAULT_PARAMETER_SOURCE_READINESS_DOC_PATH,
    DEFAULT_PARAMETER_SOURCE_READINESS_MANIFEST_PATH,
    DEFAULT_PARAMETER_SOURCE_READINESS_PACKET_PATH,
    build_parameter_source_readiness_rows,
    write_parameter_source_readiness_packet,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_parameter_source_readiness_rows(
        request_packet_path=args.request_packet,
    )
    manifest = write_parameter_source_readiness_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        request_packet_path=args.request_packet,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write parameter source-readiness rows from the current parameter "
            "evidence source-request packet. The output is a reviewer packet "
            "and does not accept weak parameters."
        )
    )
    parser.add_argument(
        "--request-packet",
        type=Path,
        default=DEFAULT_PARAMETER_EVIDENCE_SOURCE_REQUEST_PACKET_PATH,
        help="Parameter evidence source-request CSV path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_PARAMETER_SOURCE_READINESS_PACKET_PATH,
        help="Parameter source-readiness CSV path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_PARAMETER_SOURCE_READINESS_MANIFEST_PATH,
        help="Parameter source-readiness manifest JSON path.",
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_PARAMETER_SOURCE_READINESS_DOC_PATH,
        help="Parameter source-readiness Markdown path.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
