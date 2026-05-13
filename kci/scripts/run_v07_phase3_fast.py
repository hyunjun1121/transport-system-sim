"""Phase 3 counterfactual lever sweep — parallel + checkpoint variant.

Same grid as `main.py --phase 3` (3×3×3×3 cells × R_phase3=15).
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
from src.experiment.parallel_runner import run_phase3_parallel
from src.kci_runtime import merge_config_paths


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        default=ROOT / "results" / "phase3_lever_sweep.csv")
    parser.add_argument("--origin", default="A")
    parser.add_argument("--workers", type=int, default=None,
                        help="Pool size; default = cpu_count clamped to cell count.")
    args = parser.parse_args()

    cfg = merge_config_paths(load_config(ROOT / "config.yaml"))
    region_path = str((ROOT / cfg["region_path"]).resolve())
    cache_path = str((ROOT / cfg["cache_path"]).resolve())

    df = run_phase3_parallel(
        cfg,
        region_path=region_path,
        cache_path=cache_path,
        origin=args.origin,
        output_path=args.output,
        n_workers=args.workers,
    )
    print(f"V07_PHASE3_DONE rows={len(df)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
