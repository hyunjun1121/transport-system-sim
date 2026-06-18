"""Run cached pilot experiment design profiles and write separated outputs."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.pilot_experiments import (
    DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_QUEUE,
    DEFAULT_CACHE_PATH,
    DEFAULT_DESIGN_PATH,
    DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_MANIFEST_PATH,
    DEFAULT_ARTIFACT_INVALIDATION_MANIFEST_PATH,
    DEFAULT_FULL_PROFILE_ID,
    DEFAULT_FULL_GRAPH_PROFILE_ID,
    DEFAULT_MULTI_CORRIDOR_FULL_PROFILE_ID,
    DEFAULT_MULTI_CORRIDOR_PROFILE_ID,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_REGION_PATH,
    DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH,
    DEFAULT_SAMPLE_PROFILE_ID,
    DEFAULT_STAGED_PROFILE_ID,
    run_pilot_experiments,
)
from src.realworld.disruption_scenarios import DEFAULT_SCENARIO_PATH
from src.realworld.policy_alternatives import DEFAULT_POLICY_ALTERNATIVES_PATH


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for named pilot experiment design profiles."""

    args = _parse_args(argv)
    run_profile = _resolve_profile_arg(args)
    seeds = _parse_optional_csv_ints(args.seeds, "--seeds")
    policy_ids = _parse_optional_csv_text(args.policy_ids)
    scenario_ids = _parse_optional_csv_text(args.scenario_ids)
    result = run_pilot_experiments(
        region_path=args.region_path,
        cache_path=args.cache_path,
        scenarios_path=args.scenarios_path,
        policies_path=args.policies_path,
        design_path=args.design_path,
        rail_source_decision_manifest_path=args.rail_source_decision_manifest_path,
        artifact_invalidation_manifest_path=args.artifact_invalidation_manifest_path,
        artifact_invalidation_closeout_manifest_path=(
            args.artifact_invalidation_closeout_manifest_path
        ),
        closeout_action_queue_path=args.closeout_action_queue_path,
        output_dir=args.output_dir,
        road_class_overrides_path=args.road_class_overrides_path,
        seeds=seeds,
        sample=run_profile == DEFAULT_SAMPLE_PROFILE_ID,
        run_profile=run_profile,
        policy_ids=policy_ids,
        scenario_ids=scenario_ids,
        engineering_only=args.engineering_only,
        closeout_regeneration_scope=args.closeout_regeneration_scope,
    )

    manifest = result["manifest"]
    print(
        "Pilot experiment outputs written: "
        f"{manifest['row_count']} rows, {manifest['summary_row_count']} summary rows"
    )
    print(f"profile: {manifest['run_profile']} ({manifest['run_stage']})")
    print(f"results: {result['results_path']}")
    print(f"summary: {result['summary_path']}")
    print(f"manifest: {result['manifest_path']}")
    if "legacy_manifest_path" in result:
        print(f"legacy sample manifest: {result['legacy_manifest_path']}")
    print(manifest["result_scope"])
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run reproducible pilot experiment profiles from cached GraphML, "
            "disruption scenarios, policy alternatives, and design metadata."
        )
    )
    profile_group = parser.add_mutually_exclusive_group()
    profile_group.add_argument(
        "--sample",
        action="store_true",
        help="Run the default small sample subset. This is also the default.",
    )
    profile_group.add_argument(
        "--staged",
        action="store_true",
        help="Run the staged pilot design profile.",
    )
    profile_group.add_argument(
        "--full",
        action="store_true",
        help="Run the full pilot design profile.",
    )
    profile_group.add_argument(
        "--multi-corridor",
        action="store_true",
        help="Run the multi-corridor candidate profile for graph-scale review.",
    )
    profile_group.add_argument(
        "--multi-corridor-full",
        action="store_true",
        help=(
            "Run the full-scale multi-corridor candidate profile for "
            "graph-scale review."
        ),
    )
    profile_group.add_argument(
        "--full-graph",
        action="store_true",
        help=(
            "Run the full bus-practical graph (4,608 nodes) feasibility "
            "probe for graph-scale review."
        ),
    )
    profile_group.add_argument(
        "--all",
        action="store_true",
        help="Alias for --full; retained for compatibility with earlier runner usage.",
    )
    profile_group.add_argument(
        "--profile",
        help="Named profile from the pilot experiment design manifest.",
    )
    parser.add_argument(
        "--region-path",
        type=Path,
        default=DEFAULT_REGION_PATH,
        help="Pilot region YAML path.",
    )
    parser.add_argument(
        "--cache-path",
        type=Path,
        default=DEFAULT_CACHE_PATH,
        help="Cached pilot road GraphML path.",
    )
    parser.add_argument(
        "--scenarios-path",
        type=Path,
        default=DEFAULT_SCENARIO_PATH,
        help="Structured disruption scenario CSV path.",
    )
    parser.add_argument(
        "--policies-path",
        type=Path,
        default=DEFAULT_POLICY_ALTERNATIVES_PATH,
        help="Policy-alternative CSV path.",
    )
    parser.add_argument(
        "--design-path",
        type=Path,
        default=DEFAULT_DESIGN_PATH,
        help="Pilot experiment design JSON path.",
    )
    parser.add_argument(
        "--rail-source-decision-manifest-path",
        type=Path,
        default=DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH,
        help="Rail source-decision manifest used by Phase 8 preflight.",
    )
    parser.add_argument(
        "--artifact-invalidation-manifest-path",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_MANIFEST_PATH,
        help="Artifact invalidation manifest used by Phase 9 promotion preflight.",
    )
    parser.add_argument(
        "--artifact-invalidation-closeout-manifest-path",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_MANIFEST_PATH,
        help="Artifact invalidation closeout manifest used by Phase 9 promotion preflight.",
    )
    parser.add_argument(
        "--closeout-action-queue-path",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_QUEUE,
        help="Artifact invalidation closeout action queue used by scoped regeneration preflight.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for pilot result CSVs and manifest.",
    )
    parser.add_argument(
        "--road-class-overrides-path",
        type=Path,
        default=None,
        help=(
            "Optional reviewed road-class override CSV. When provided, fallback "
            "speed, capacity, and base-disruption values are applied during "
            "cached graph adaptation."
        ),
    )
    parser.add_argument(
        "--seeds",
        default=None,
        help="Optional comma-separated integer seeds overriding the design profile.",
    )
    parser.add_argument(
        "--policy-ids",
        default=None,
        help="Optional comma-separated policy IDs overriding the design profile.",
    )
    parser.add_argument(
        "--scenario-ids",
        default=None,
        help="Optional comma-separated scenario IDs overriding the design profile.",
    )
    parser.add_argument(
        "--engineering-only",
        action="store_true",
        help=(
            "Allow non-sample profiles with pending rail source decisions only as "
            "explicit non-publication, non-acceptance, non-operational method checks."
        ),
    )
    parser.add_argument(
        "--closeout-regeneration-scope",
        choices=("compact_outputs",),
        default=None,
        help=(
            "Allow a non-sample compact-output regeneration run only after prior "
            "invalidation closeout batches are closed. This is not publication, "
            "final-study, formal-acceptance, or operational evidence."
        ),
    )
    return parser.parse_args(argv)


def _resolve_profile_arg(args: argparse.Namespace) -> str:
    if args.profile:
        return str(args.profile).strip()
    if args.staged:
        return DEFAULT_STAGED_PROFILE_ID
    if args.multi_corridor:
        return DEFAULT_MULTI_CORRIDOR_PROFILE_ID
    if args.multi_corridor_full:
        return DEFAULT_MULTI_CORRIDOR_FULL_PROFILE_ID
    if args.full_graph:
        return DEFAULT_FULL_GRAPH_PROFILE_ID
    if args.full or args.all:
        return DEFAULT_FULL_PROFILE_ID
    return DEFAULT_SAMPLE_PROFILE_ID


def _parse_optional_csv_ints(raw: str | None, label: str) -> tuple[int, ...] | None:
    if raw is None:
        return None
    values = tuple(int(part.strip()) for part in raw.split(",") if part.strip())
    if not values:
        raise ValueError(f"{label} must contain at least one integer value")
    return values


def _parse_optional_csv_text(raw: str | None) -> tuple[str, ...] | None:
    if raw is None:
        return None
    values = tuple(part.strip() for part in raw.split(",") if part.strip())
    if not values:
        raise ValueError("CSV override must contain at least one value")
    return values


if __name__ == "__main__":
    raise SystemExit(main())
