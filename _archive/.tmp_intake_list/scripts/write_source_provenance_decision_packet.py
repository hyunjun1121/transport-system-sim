"""Write the source-provenance decision packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.provenance_acceptance import (  # noqa: E402
    DEFAULT_PROVENANCE_ACCEPTANCE_PATH,
)
from src.realworld.reproducibility_review_packet import (  # noqa: E402
    DEFAULT_REPRODUCIBILITY_MANIFEST_PATH,
)
from src.realworld.source_context_cache_decision_packet import (  # noqa: E402
    DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_MANIFEST_PATH,
)
from src.realworld.source_context_cache_request_packet import (  # noqa: E402
    DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_MANIFEST_PATH,
)
from src.realworld.source_license_review_packet import (  # noqa: E402
    DEFAULT_SOURCE_LICENSE_REVIEW_MANIFEST_PATH,
)
from src.realworld.source_provenance import DEFAULT_SOURCE_PROVENANCE_PATH  # noqa: E402
from src.realworld.source_provenance_decision_packet import (  # noqa: E402
    DEFAULT_SOURCE_PROVENANCE_DECISION_DOC_PATH,
    DEFAULT_SOURCE_PROVENANCE_DECISION_MANIFEST_PATH,
    DEFAULT_SOURCE_PROVENANCE_DECISION_PACKET_PATH,
    build_source_provenance_decision_rows,
    write_source_provenance_decision_packet,
)
from src.realworld.source_provenance_priority_packet import (  # noqa: E402
    DEFAULT_SOURCE_PROVENANCE_PRIORITY_MANIFEST_PATH,
)
from src.realworld.source_url_remediation_packet import (  # noqa: E402
    DEFAULT_SOURCE_URL_REMEDIATION_MANIFEST_PATH,
)
from src.realworld.source_url_review_packet import (  # noqa: E402
    DEFAULT_SOURCE_URL_REVIEW_MANIFEST_PATH,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_source_provenance_decision_rows(
        source_provenance_manifest_path=args.source_provenance_manifest,
        source_license_manifest_path=args.source_license_manifest,
        source_url_manifest_path=args.source_url_manifest,
        source_url_remediation_manifest_path=args.source_url_remediation_manifest,
        source_priority_manifest_path=args.source_priority_manifest,
        source_context_request_manifest_path=args.source_context_request_manifest,
        source_context_decision_manifest_path=args.source_context_decision_manifest,
        reproducibility_manifest_path=args.reproducibility_manifest,
        provenance_acceptance_path=args.provenance_acceptance,
    )
    manifest = write_source_provenance_decision_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        source_provenance_manifest_path=args.source_provenance_manifest,
        source_license_manifest_path=args.source_license_manifest,
        source_url_manifest_path=args.source_url_manifest,
        source_url_remediation_manifest_path=args.source_url_remediation_manifest,
        source_priority_manifest_path=args.source_priority_manifest,
        source_context_request_manifest_path=args.source_context_request_manifest,
        source_context_decision_manifest_path=args.source_context_decision_manifest,
        reproducibility_manifest_path=args.reproducibility_manifest,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a source-provenance decision packet. The output is review "
            "support only, not provenance acceptance."
        )
    )
    parser.add_argument(
        "--source-provenance-manifest",
        type=Path,
        default=DEFAULT_SOURCE_PROVENANCE_PATH,
    )
    parser.add_argument(
        "--source-license-manifest",
        type=Path,
        default=DEFAULT_SOURCE_LICENSE_REVIEW_MANIFEST_PATH,
    )
    parser.add_argument(
        "--source-url-manifest",
        type=Path,
        default=DEFAULT_SOURCE_URL_REVIEW_MANIFEST_PATH,
    )
    parser.add_argument(
        "--source-url-remediation-manifest",
        type=Path,
        default=DEFAULT_SOURCE_URL_REMEDIATION_MANIFEST_PATH,
    )
    parser.add_argument(
        "--source-priority-manifest",
        type=Path,
        default=DEFAULT_SOURCE_PROVENANCE_PRIORITY_MANIFEST_PATH,
    )
    parser.add_argument(
        "--source-context-request-manifest",
        type=Path,
        default=DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_MANIFEST_PATH,
    )
    parser.add_argument(
        "--source-context-decision-manifest",
        type=Path,
        default=DEFAULT_SOURCE_CONTEXT_CACHE_DECISION_MANIFEST_PATH,
    )
    parser.add_argument(
        "--reproducibility-manifest",
        type=Path,
        default=DEFAULT_REPRODUCIBILITY_MANIFEST_PATH,
    )
    parser.add_argument(
        "--provenance-acceptance",
        type=Path,
        default=DEFAULT_PROVENANCE_ACCEPTANCE_PATH,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_SOURCE_PROVENANCE_DECISION_PACKET_PATH,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_SOURCE_PROVENANCE_DECISION_MANIFEST_PATH,
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_SOURCE_PROVENANCE_DECISION_DOC_PATH,
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
