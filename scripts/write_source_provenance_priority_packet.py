"""Write the source provenance priority packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.source_license_review_packet import (  # noqa: E402
    DEFAULT_SOURCE_LICENSE_REVIEW_PACKET_PATH,
)
from src.realworld.source_provenance_priority_packet import (  # noqa: E402
    DEFAULT_SOURCE_PROVENANCE_PRIORITY_DOC_PATH,
    DEFAULT_SOURCE_PROVENANCE_PRIORITY_MANIFEST_PATH,
    DEFAULT_SOURCE_PROVENANCE_PRIORITY_PACKET_PATH,
    build_source_provenance_priority_rows,
    write_source_provenance_priority_packet,
)
from src.realworld.source_url_remediation_packet import (  # noqa: E402
    DEFAULT_SOURCE_URL_REMEDIATION_PACKET_PATH,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_source_provenance_priority_rows(
        source_license_review_path=args.source_license_review,
        source_url_remediation_path=args.source_url_remediation,
    )
    manifest = write_source_provenance_priority_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        source_license_review_path=args.source_license_review,
        source_url_remediation_path=args.source_url_remediation,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a source provenance priority packet. The output is review "
            "support only, not source acceptance or license certification."
        )
    )
    parser.add_argument(
        "--source-license-review",
        type=Path,
        default=DEFAULT_SOURCE_LICENSE_REVIEW_PACKET_PATH,
    )
    parser.add_argument(
        "--source-url-remediation",
        type=Path,
        default=DEFAULT_SOURCE_URL_REMEDIATION_PACKET_PATH,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_SOURCE_PROVENANCE_PRIORITY_PACKET_PATH,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_SOURCE_PROVENANCE_PRIORITY_MANIFEST_PATH,
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_SOURCE_PROVENANCE_PRIORITY_DOC_PATH,
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
