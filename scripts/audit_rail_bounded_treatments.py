"""Write rail bounded-treatment consistency audit artifacts."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, os.fspath(PROJECT_ROOT))

from src.realworld.rail_bounded_treatment_audit import (  # noqa: E402
    DEFAULT_RAIL_BOUNDED_TREATMENT_AUDIT_DOC_PATH,
    DEFAULT_RAIL_BOUNDED_TREATMENT_AUDIT_PATH,
    DEFAULT_RAIL_SOURCE_DECISION_PACKET_PATH,
    DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_PACKET_PATH,
    build_rail_bounded_treatment_audit,
    write_rail_bounded_treatment_audit,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit bounded rail capacity/availability treatment consistency."
    )
    parser.add_argument(
        "--rail-source-decision-packet",
        default=DEFAULT_RAIL_SOURCE_DECISION_PACKET_PATH,
        help="Rail source-decision CSV path.",
    )
    parser.add_argument(
        "--rail-transit-stress-profile-packet",
        default=DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_PACKET_PATH,
        help="Rail/transit stress-profile CSV path.",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_RAIL_BOUNDED_TREATMENT_AUDIT_PATH,
        help="Output audit JSON path.",
    )
    parser.add_argument(
        "--doc-output",
        default=DEFAULT_RAIL_BOUNDED_TREATMENT_AUDIT_DOC_PATH,
        help="Output Markdown path.",
    )
    parser.add_argument(
        "--fail-on-mismatch",
        action="store_true",
        help="Exit non-zero when mismatch_count is non-zero.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    audit = build_rail_bounded_treatment_audit(
        source_decision_path=args.rail_source_decision_packet,
        stress_profile_path=args.rail_transit_stress_profile_packet,
    )
    write_rail_bounded_treatment_audit(
        audit=audit,
        output_path=args.output,
        doc_path=args.doc_output,
    )
    print(json.dumps(audit, indent=2, sort_keys=True))
    if args.fail_on_mismatch and int(audit.get("mismatch_count", 0)) > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
