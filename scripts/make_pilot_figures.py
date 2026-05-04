"""Generate scaffold-only pilot figures and tables from current summary CSVs."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.pilot_figures import (
    DEFAULT_OUTPUT_DIR,
    DEFAULT_PILOT_MANIFEST_PATH,
    DEFAULT_PILOT_SUMMARY_PATH,
    DEFAULT_SENSITIVITY_MANIFEST_PATH,
    DEFAULT_SENSITIVITY_SUMMARY_PATH,
    build_pilot_figure_tables,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for Workstream 11 scaffold-only figures and tables."""

    args = _parse_args(argv)
    result = build_pilot_figure_tables(
        pilot_summary_path=args.pilot_summary_path,
        sensitivity_summary_path=args.sensitivity_summary_path,
        pilot_manifest_path=args.pilot_manifest_path,
        sensitivity_manifest_path=args.sensitivity_manifest_path,
        output_dir=args.output_dir,
        figures_dir=args.figures_dir,
        tables_dir=args.tables_dir,
        sensitivity_metric=args.sensitivity_metric,
    )

    manifest = result["manifest"]
    print("Pilot scaffold figure/table outputs written")
    print(f"figures_dir: {result['figures_dir']}")
    print(f"tables_dir: {result['tables_dir']}")
    for name, path in sorted(result["figures"].items()):
        print(f"figure {name}: {path}")
    for name, path in sorted(result["tables"].items()):
        print(f"table {name}: {path}")
    print(manifest["result_scope"])
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate scaffold-only pilot figure and table scaffolds from the "
            "current realworld_pilot summary CSVs."
        )
    )
    parser.add_argument(
        "--pilot-summary-path",
        type=Path,
        default=DEFAULT_PILOT_SUMMARY_PATH,
        help="Pilot summary CSV path. Default uses the full pilot profile.",
    )
    parser.add_argument(
        "--sensitivity-summary-path",
        type=Path,
        default=DEFAULT_SENSITIVITY_SUMMARY_PATH,
        help="Sensitivity summary CSV path. Default uses SALib Morris output.",
    )
    parser.add_argument(
        "--pilot-manifest-path",
        type=Path,
        default=DEFAULT_PILOT_MANIFEST_PATH,
        help="Pilot result manifest JSON path. Default uses the full pilot profile.",
    )
    parser.add_argument(
        "--sensitivity-manifest-path",
        type=Path,
        default=DEFAULT_SENSITIVITY_MANIFEST_PATH,
        help="Sensitivity manifest JSON path. Default uses SALib Morris output.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Base output directory for generated figures/ and tables/.",
    )
    parser.add_argument(
        "--figures-dir",
        type=Path,
        default=None,
        help="Optional explicit figure output directory.",
    )
    parser.add_argument(
        "--tables-dir",
        type=Path,
        default=None,
        help="Optional explicit table output directory.",
    )
    parser.add_argument(
        "--sensitivity-metric",
        default="penalized_makespan",
        help="Sensitivity metric used for the ranking figure.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
