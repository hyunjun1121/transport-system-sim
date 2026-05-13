"""v0.7 Phase 1b: origin robustness sweep at R=20 for origins B/C/D.

Each origin gets the focused p_fail grid [0.0, 0.5, 1.0, 1.5] at s=1.2.
Writes one CSV per origin: results/phase1b_origin_{X}.csv.
"""
from __future__ import annotations

import sys
import time
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from main import load_config
from src.kci_runtime import (
    build_corridor_graph,
    load_region_with_origin,
    merge_config_paths,
)
from src.experiment.runner import run_phase1, save_results


ORIGINS = ("B", "C", "D")
P_LEVELS = [0.0, 0.5, 1.0, 1.5]
S_LEVELS = [1.2]
R = 20


def main() -> int:
    base_cfg = merge_config_paths(load_config(ROOT / "config.yaml"))
    region_path = ROOT / base_cfg["region_path"]
    candidates_path = ROOT / base_cfg["origin_candidates_path"]
    cache_path = ROOT / base_cfg["cache_path"]
    out_dir = ROOT / "results"
    out_dir.mkdir(parents=True, exist_ok=True)

    for origin in ORIGINS:
        cfg = deepcopy(base_cfg)
        cfg["congestion_scale"]["levels"] = list(S_LEVELS)
        cfg["failure_rate"]["levels"] = list(P_LEVELS)
        cfg["experiment"] = dict(cfg.get("experiment", {}))
        cfg["experiment"]["R"] = R

        print(f"=== Phase 1b origin {origin} ===", flush=True)
        t0 = time.time()
        region = load_region_with_origin(region_path, candidates_path, origin)
        graph = build_corridor_graph(region, cache_path)
        df = run_phase1(cfg, graph)
        df["origin"] = origin
        save_results(df, out_dir / f"phase1b_origin_{origin}.csv")
        print(
            f"Origin {origin}: {len(df)} rows, "
            f"elapsed {time.time() - t0:.1f}s",
            flush=True,
        )

    print("V07_PHASE1B_DONE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
