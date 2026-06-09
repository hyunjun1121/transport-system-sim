"""Run the frozen Phase 8 executable micro-probe."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.phase8_micro_probe import (  # noqa: E402
    DEFAULT_MICRO_PROBE_MANIFEST_PATH,
    DEFAULT_MICRO_PROBE_OUTPUT_DIR,
    DEFAULT_MICRO_PROBE_RERUN_OUTPUT_DIR,
    run_phase8_micro_probe,
)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    result = run_phase8_micro_probe(
        output_dir=args.output_dir,
        rerun_output_dir=args.rerun_output_dir,
        manifest_path=args.manifest,
        runtime_preflight_manifest_path=args.runtime_preflight_manifest,
    )
    manifest = result["manifest"]
    print(
        "Phase 8 micro-probe outputs written: "
        f"{manifest['actual_row_count']} rows, "
        f"{manifest['actual_summary_row_count']} summary rows"
    )
    print(f"manifest: {result['manifest_path']}")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    if args.fail_on_blockers and manifest["execution_blockers"]:
        return 1
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_MICRO_PROBE_OUTPUT_DIR,
        help="Primary micro-probe output directory.",
    )
    parser.add_argument(
        "--rerun-output-dir",
        type=Path,
        default=DEFAULT_MICRO_PROBE_RERUN_OUTPUT_DIR,
        help="Deterministic rerun output directory.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MICRO_PROBE_MANIFEST_PATH,
        help="Micro-probe wrapper manifest path.",
    )
    parser.add_argument(
        "--runtime-preflight-manifest",
        type=Path,
        required=True,
        help="Ready runtime preflight manifest generated with execution_scope=micro_probe.",
    )
    parser.add_argument(
        "--fail-on-blockers",
        action="store_true",
        help="Return exit code 1 when execution checks fail.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
