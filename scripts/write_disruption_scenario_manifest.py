"""Write Phase 6 disruption scenario manifest and review document."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.disruption_scenarios import (  # noqa: E402
    DEFAULT_SCENARIO_DOC_PATH,
    DEFAULT_SCENARIO_MANIFEST_PATH,
    DEFAULT_SCENARIO_PATH,
    build_scenario_edge_map,
    load_disruption_scenarios,
    write_disruption_scenario_manifest,
)
from src.realworld.pilot_experiments import load_pilot_inputs  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    scenarios = load_disruption_scenarios(args.scenarios, region_id=args.region_id)
    selected_edges = None
    if args.include_pilot_edge_map:
        inputs = load_pilot_inputs()
        selected_edges = build_scenario_edge_map(
            inputs.graph,
            scenarios,
            region_id=inputs.region_id,
        )

    manifest = write_disruption_scenario_manifest(
        scenarios,
        scenario_path=args.scenarios,
        manifest_path=args.manifest,
        doc_path=args.doc,
        selected_edges=selected_edges,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write Phase 6 disruption scenario manifest artifacts. Outputs are "
            "scenario-library review support only, not observed disaster data, "
            "not calibrated disruption evidence, and not formal acceptance."
        )
    )
    parser.add_argument("--scenarios", type=Path, default=DEFAULT_SCENARIO_PATH)
    parser.add_argument("--region-id", default="songpa_public_demo")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_SCENARIO_MANIFEST_PATH,
    )
    parser.add_argument("--doc", type=Path, default=DEFAULT_SCENARIO_DOC_PATH)
    parser.add_argument(
        "--include-pilot-edge-map",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Include selected-edge checksums from the current pilot graph.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
