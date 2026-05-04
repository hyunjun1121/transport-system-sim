"""Generate pilot experiment confidence-interval and paired-delta tables."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.pilot_statistics import (  # noqa: E402
    DEFAULT_PILOT_FULL_MANIFEST_PATH,
    DEFAULT_PILOT_FULL_RESULTS_PATH,
    DEFAULT_PILOT_TABLE_DIR,
    load_pilot_result_rows,
    write_pilot_statistics_outputs,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = load_pilot_result_rows(args.input)
    result = write_pilot_statistics_outputs(
        rows=rows,
        output_dir=args.output_dir,
        output_prefix=args.output_prefix,
        source_results_path=args.input,
        source_manifest_path=args.source_manifest,
    )
    manifest = result["manifest"]
    print(
        "Pilot statistics written: "
        f"{manifest['metric_ci_row_count']} metric CI rows, "
        f"{manifest['paired_delta_ci_row_count']} paired-delta CI rows"
    )
    print(f"metric_ci: {result['metric_path']}")
    print(f"paired_delta_ci: {result['paired_delta_path']}")
    print(f"manifest: {result['manifest_path']}")
    print(manifest["result_scope"])
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create seed-replication confidence intervals and paired policy "
            "delta tables from a pilot result CSV."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_PILOT_FULL_RESULTS_PATH,
        help="Pilot result CSV path.",
    )
    parser.add_argument(
        "--source-manifest",
        type=Path,
        default=DEFAULT_PILOT_FULL_MANIFEST_PATH,
        help="Pilot result manifest path used for provenance metadata.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_PILOT_TABLE_DIR,
        help="Directory for generated statistics tables.",
    )
    parser.add_argument(
        "--output-prefix",
        default="pilot_full",
        help="Lowercase prefix for generated output files.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
