"""Run bounded Phase 10 post-simulation ML analysis."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.ml_analysis import (  # noqa: E402
    DEFAULT_ANALYSIS_DIR,
    DEFAULT_SOURCE_MANIFEST,
    DEFAULT_SOURCE_RESULTS,
    load_simulation_rows,
    write_ml_analysis_outputs,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    actual_argv = list(sys.argv[1:] if argv is None else argv)
    args = _parse_args(actual_argv)
    rows = load_simulation_rows(args.input)
    command = [str(Path(__file__).relative_to(ROOT)), *actual_argv]
    result = write_ml_analysis_outputs(
        rows=rows,
        output_dir=args.output_dir,
        source_results_path=args.input,
        source_manifest_path=args.source_manifest,
        output_prefix=args.output_prefix,
        allow_xgboost=not args.no_xgboost,
        device=args.device,
        command=command,
    )
    manifest = result["manifest"]
    print(
        "Phase 10 ML outputs written: "
        f"{manifest['label_row_count']} labels, "
        f"{manifest['prediction_row_count']} predictions, "
        f"{manifest['feature_importance_row_count']} feature rows"
    )
    print(f"model_status: {manifest['model_status']}")
    print(f"labels: {result['labels_path']}")
    print(f"predictions: {result['predictions_path']}")
    print(f"feature_importance: {result['importance_path']}")
    print(f"manifest: {result['manifest_path']}")
    print(manifest["result_scope"])
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_SOURCE_RESULTS,
        help="Simulation result CSV used for label derivation and ML features.",
    )
    parser.add_argument(
        "--source-manifest",
        type=Path,
        default=DEFAULT_SOURCE_MANIFEST,
        help="Simulation result manifest used for provenance.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_ANALYSIS_DIR,
        help="Directory for ML analysis outputs.",
    )
    parser.add_argument(
        "--output-prefix",
        default="pilot_staged_scoped",
        help="Prefix for generated ML output filenames.",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        help="XGBoost device. Use cpu unless a separate GPU runtime claim is needed.",
    )
    parser.add_argument(
        "--no-xgboost",
        action="store_true",
        help="Disable XGBoost and write deterministic majority-baseline outputs.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
