"""Run pilot scaffold sensitivity screening and write separated outputs."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.disruption_scenarios import DEFAULT_SCENARIO_PATH
from src.realworld.pilot_experiments import (
    DEFAULT_CACHE_PATH,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_REGION_PATH,
)
from src.realworld.policy_alternatives import DEFAULT_POLICY_ALTERNATIVES_PATH
from src.realworld.sensitivity import (
    DEFAULT_DESIGN_PATH,
    DEFAULT_SAMPLE_POLICY_IDS,
    DEFAULT_SAMPLE_SCENARIO_IDS,
    DEFAULT_SENSITIVITY_SEED,
    METHOD_DETERMINISTIC,
    METHOD_MORRIS,
    run_morris_sensitivity,
    run_sensitivity_screening,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for pilot sensitivity screening."""

    args = _parse_args(argv)
    if args.sample and args.all:
        raise SystemExit("--sample and --all cannot be used together")

    sample = args.sample or not args.all
    method = str(args.method).lower()
    common_kwargs = {
        "region_path": args.region_path,
        "cache_path": args.cache_path,
        "scenarios_path": args.scenarios_path,
        "policies_path": args.policies_path,
        "design_path": args.design_path,
        "output_dir": args.output_dir,
        "seed": args.seed,
        "sample": sample,
        "policy_ids": _parse_optional_list(args.policies),
        "scenario_ids": _parse_optional_list(args.scenarios),
        "parameter_ids": _parse_optional_list(args.parameters),
    }
    if method in {"auto", METHOD_DETERMINISTIC}:
        result = run_sensitivity_screening(**common_kwargs)
    elif method in {"morris", METHOD_MORRIS}:
        result = run_morris_sensitivity(
            **common_kwargs,
            num_trajectories=args.trajectories,
            num_levels=args.levels,
        )
    else:
        raise SystemExit(
            f"{args.method!r} is not implemented; use 'auto', "
            f"{METHOD_DETERMINISTIC!r}, 'morris', or {METHOD_MORRIS!r}"
        )

    manifest = result["manifest"]
    print(
        "Pilot scaffold sensitivity outputs written: "
        f"{manifest['row_count']} rows, {manifest['summary_row_count']} summary rows"
    )
    print(f"method: {manifest['method']}")
    print(f"results: {result['results_path']}")
    print(f"summary: {result['summary_path']}")
    print(f"manifest: {result['manifest_path']}")
    print(manifest["result_scope"])
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run deterministic one-at-a-time sensitivity screening for the "
            "cached pilot scaffold. The default path does not require SALib."
        )
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Run the default small policy and scenario subset. This is the default.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all policy and disruption table rows.",
    )
    parser.add_argument(
        "--method",
        default="auto",
        help=(
            "Sensitivity method. Use 'auto' or deterministic_oat_screening for "
            "offline one-at-a-time screening; use 'morris' or salib_morris for "
            "SALib Morris screening."
        ),
    )
    parser.add_argument(
        "--trajectories",
        type=int,
        default=4,
        help="Number of Morris trajectories when --method morris is selected.",
    )
    parser.add_argument(
        "--levels",
        type=int,
        default=4,
        help="Number of Morris levels when --method morris is selected.",
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
        help="Sensitivity design CSV path.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for sensitivity result CSVs and manifest.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SENSITIVITY_SEED,
        help="Fixed seed used as the common random-number input.",
    )
    parser.add_argument(
        "--policies",
        default="",
        help=(
            "Optional comma-separated policy IDs. Default sample policies are "
            f"{','.join(DEFAULT_SAMPLE_POLICY_IDS)}."
        ),
    )
    parser.add_argument(
        "--scenarios",
        default="",
        help=(
            "Optional comma-separated disruption scenario IDs. Default sample "
            f"scenarios are {','.join(DEFAULT_SAMPLE_SCENARIO_IDS)}."
        ),
    )
    parser.add_argument(
        "--parameters",
        default="",
        help="Optional comma-separated sensitivity parameter IDs.",
    )
    return parser.parse_args(argv)


def _parse_optional_list(raw: str) -> tuple[str, ...] | None:
    values = tuple(part.strip() for part in raw.split(",") if part.strip())
    return values or None


if __name__ == "__main__":
    raise SystemExit(main())
