"""Write the parameter source decision packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.parameter_evidence_priority_packet import (  # noqa: E402
    DEFAULT_PARAMETER_EVIDENCE_PRIORITY_MANIFEST_PATH,
    DEFAULT_PARAMETER_EVIDENCE_PRIORITY_PACKET_PATH,
)
from src.realworld.parameter_review_packet import (  # noqa: E402
    DEFAULT_PARAMETER_REVIEW_PACKET_PATH,
)
from src.realworld.parameter_source_decision_packet import (  # noqa: E402
    DEFAULT_PARAMETER_SOURCE_DECISION_DOC_PATH,
    DEFAULT_PARAMETER_SOURCE_DECISION_MANIFEST_PATH,
    DEFAULT_PARAMETER_SOURCE_DECISION_PACKET_PATH,
    build_parameter_source_decision_rows,
    write_parameter_source_decision_packet,
)
from src.realworld.parameter_source_readiness_packet import (  # noqa: E402
    DEFAULT_PARAMETER_SOURCE_READINESS_MANIFEST_PATH,
    DEFAULT_PARAMETER_SOURCE_READINESS_PACKET_PATH,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_parameter_source_decision_rows(
        readiness_packet_path=args.readiness_packet,
        readiness_manifest_path=args.readiness_manifest,
        priority_packet_path=args.priority_packet,
        priority_manifest_path=args.priority_manifest,
        parameter_review_packet_path=args.parameter_review_packet,
    )
    manifest = write_parameter_source_decision_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        readiness_packet_path=args.readiness_packet,
        readiness_manifest_path=args.readiness_manifest,
        priority_packet_path=args.priority_packet,
        priority_manifest_path=args.priority_manifest,
        parameter_review_packet_path=args.parameter_review_packet,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a parameter source-decision packet. The output is review "
            "support only, not parameter evidence or weak-parameter acceptance."
        )
    )
    parser.add_argument(
        "--readiness-packet",
        type=Path,
        default=DEFAULT_PARAMETER_SOURCE_READINESS_PACKET_PATH,
    )
    parser.add_argument(
        "--readiness-manifest",
        type=Path,
        default=DEFAULT_PARAMETER_SOURCE_READINESS_MANIFEST_PATH,
    )
    parser.add_argument(
        "--priority-packet",
        type=Path,
        default=DEFAULT_PARAMETER_EVIDENCE_PRIORITY_PACKET_PATH,
    )
    parser.add_argument(
        "--priority-manifest",
        type=Path,
        default=DEFAULT_PARAMETER_EVIDENCE_PRIORITY_MANIFEST_PATH,
    )
    parser.add_argument(
        "--parameter-review-packet",
        type=Path,
        default=DEFAULT_PARAMETER_REVIEW_PACKET_PATH,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_PARAMETER_SOURCE_DECISION_PACKET_PATH,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_PARAMETER_SOURCE_DECISION_MANIFEST_PATH,
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_PARAMETER_SOURCE_DECISION_DOC_PATH,
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
