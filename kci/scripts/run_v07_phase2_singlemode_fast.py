"""Phase 2 single-mode parametric — parallel + checkpoint variant.

Same grid as `run_v07_phase2_singlemode.py`:
  fleet ∈ {15,23,35,50,80}, dispatch ∈ {3,5,10}, p ∈ {0.5,1,2}, R=20.

Differences:
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
from src.experiment.parallel_runner import run_phase2_singlemode_parallel
from src.kci_runtime import merge_config_paths


FLEET = [15, 23, 35, 50, 80]
DISPATCH = [3.0, 5.0, 10.0]
P_FAIL = [0.5, 1.0, 2.0]
R = 20


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        default=ROOT / "results" / "phase2_singlemode.csv")
    parser.add_argument("--origin", default="A")
    parser.add_argument("--workers", type=int, default=None,
                        help="Pool size; default = cpu_count clamped to cell count.")
    args = parser.parse_args()

    cfg = merge_config_paths(load_config(ROOT / "config.yaml"))
    region_path = str((ROOT / cfg["region_path"]).resolve())
    cache_path = str((ROOT / cfg["cache_path"]).resolve())

    df = run_phase2_singlemode_parallel(
        cfg,
        region_path=region_path,
        cache_path=cache_path,
        origin=args.origin,
        output_path=args.output,
        fleet_levels=FLEET,
        dispatch_levels=DISPATCH,
        p_levels=P_FAIL,
        R=R,
        n_workers=args.workers,
    )
    print(f"V07_PHASE2_DONE rows={len(df)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
