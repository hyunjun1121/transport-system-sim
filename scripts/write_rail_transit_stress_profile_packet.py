"""Write the rail/transit stress-profile review packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.rail_transit_stress_profile_packet import (  # noqa: E402
    DEFAULT_DISRUPTION_SCENARIOS_PATH,
    DEFAULT_POLICY_ALTERNATIVES_PATH,
    DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH,
    DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_DOC_PATH,
    DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_MANIFEST_PATH,
    DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_PACKET_PATH,
    DEFAULT_SENSITIVITY_DESIGN_PATH,
    build_rail_transit_stress_profile_rows,
    write_rail_transit_stress_profile_packet,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_rail_transit_stress_profile_rows(
        region_id=args.region_id,
        policy_alternatives_path=args.policy_alternatives,
        disruption_scenarios_path=args.disruption_scenarios,
        sensitivity_design_path=args.sensitivity_design,
    )
    manifest = write_rail_transit_stress_profile_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        rail_source_decision_manifest_path=args.rail_source_decision_manifest,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a rail/transit stress-profile packet. The output is review "
            "support only, not rail evidence, not rail availability evidence, "
            "and not formal acceptance."
        )
    )
    parser.add_argument("--region-id", default="songpa_public_demo")
    parser.add_argument(
        "--policy-alternatives",
        type=Path,
        default=DEFAULT_POLICY_ALTERNATIVES_PATH,
    )
    parser.add_argument(
        "--disruption-scenarios",
        type=Path,
        default=DEFAULT_DISRUPTION_SCENARIOS_PATH,
    )
    parser.add_argument(
        "--sensitivity-design",
        type=Path,
        default=DEFAULT_SENSITIVITY_DESIGN_PATH,
    )
    parser.add_argument(
        "--rail-source-decision-manifest",
        type=Path,
        default=DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_PACKET_PATH,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_MANIFEST_PATH,
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_DOC_PATH,
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
