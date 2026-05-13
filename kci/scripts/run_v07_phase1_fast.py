"""Phase 1 (a or b) — parallel + checkpoint variant.

Default (Phase 1a): origin A, R=30, s=[1.2], p_fail × 8 levels from config.
Override --origin / --p-levels / --R / --output to run Phase 1b cells.

- Parallel cells across processes (default: cpu_count)
- Per-cell append to CSV (kill-tolerant)
- Resume: re-running with the same --output skips cells already saved
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from main import load_config
from src.experiment.parallel_runner import run_phase1_parallel
from src.kci_runtime import merge_config_paths


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        default=ROOT / "results" / "phase1a_origin_A.csv")
    parser.add_argument("--origin", default="A")
    parser.add_argument("--R", type=int, default=None)
    parser.add_argument("--p-levels", type=str, default=None,
                        help="Comma-separated p_fail_scale levels (default: config).")
    parser.add_argument("--s-levels", type=str, default=None,
                        help="Comma-separated s levels (default: config).")
    parser.add_argument("--workers", type=int, default=None)
    args = parser.parse_args()

    cfg = merge_config_paths(load_config(ROOT / "config.yaml"))
    region_path = str((ROOT / cfg["region_path"]).resolve())
    cache_path = str((ROOT / cfg["cache_path"]).resolve())

    p_levels = [float(x) for x in args.p_levels.split(",")] if args.p_levels else None
    s_levels = [float(x) for x in args.s_levels.split(",")] if args.s_levels else None

    df = run_phase1_parallel(
        cfg,
        region_path=region_path,
        cache_path=cache_path,
        origin=args.origin,
        output_path=args.output,
        s_levels=s_levels,
        p_levels=p_levels,
        R=args.R,
        n_workers=args.workers,
    )
    print(f"V07_PHASE1_DONE rows={len(df)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
