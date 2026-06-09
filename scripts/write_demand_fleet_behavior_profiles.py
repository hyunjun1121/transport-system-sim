"""Write Phase 5 demand, fleet, and behavior profile review artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.demand_fleet_behavior_profiles import (  # noqa: E402
    DEFAULT_BEHAVIOR_PROFILE_PATH,
    DEFAULT_CONFIG_PATH,
    DEFAULT_DEMAND_PROFILE_PATH,
    DEFAULT_FLEET_PROFILE_PATH,
    DEFAULT_PILOT_DESIGN_PATH,
    DEFAULT_PROFILE_DOC_PATH,
    DEFAULT_PROFILE_MANIFEST_PATH,
    DEFAULT_REGION_PATH,
    DEFAULT_SENSITIVITY_DESIGN_PATH,
    build_phase5_profile_rows,
    write_phase5_profile_packet,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_phase5_profile_rows(
        config_path=args.config,
        region_path=args.region,
        pilot_design_path=args.pilot_design,
        sensitivity_design_path=args.sensitivity_design,
    )
    manifest = write_phase5_profile_packet(
        rows=rows,
        demand_path=args.demand_output,
        fleet_path=args.fleet_output,
        behavior_path=args.behavior_output,
        manifest_path=args.manifest,
        doc_path=args.doc,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write Phase 5 demand/fleet/behavior profile artifacts. Outputs "
            "are bounded scenario-review inputs only, not calibrated demand, "
            "not agency fleet evidence, and not formal acceptance."
        )
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--region", type=Path, default=DEFAULT_REGION_PATH)
    parser.add_argument(
        "--pilot-design",
        type=Path,
        default=DEFAULT_PILOT_DESIGN_PATH,
    )
    parser.add_argument(
        "--sensitivity-design",
        type=Path,
        default=DEFAULT_SENSITIVITY_DESIGN_PATH,
    )
    parser.add_argument(
        "--demand-output",
        type=Path,
        default=DEFAULT_DEMAND_PROFILE_PATH,
    )
    parser.add_argument(
        "--fleet-output",
        type=Path,
        default=DEFAULT_FLEET_PROFILE_PATH,
    )
    parser.add_argument(
        "--behavior-output",
        type=Path,
        default=DEFAULT_BEHAVIOR_PROFILE_PATH,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_PROFILE_MANIFEST_PATH,
    )
    parser.add_argument("--doc", type=Path, default=DEFAULT_PROFILE_DOC_PATH)
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
