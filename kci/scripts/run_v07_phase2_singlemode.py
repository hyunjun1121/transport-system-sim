"""v0.7 Phase 2: single-mode (bus_only) parametric sweep.

Sweeps bus.fleet_size × bus.dispatch_interval_min × p_fail_scale at fixed
s=1.2, R=20, origin A. Paired CRN against multimodal at baseline multimodal
parameters (so the comparison is single-mode-tuning vs untuned multimodal).

Writes one CSV: results/phase2_singlemode.csv.
"""
from __future__ import annotations

import sys
import time
from copy import deepcopy
from itertools import product
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from main import load_config
from src.experiment.runner import _ContextCache, _paired_result_row
from src.kci_runtime import (
    build_corridor_graph,
    load_region_with_origin,
    merge_config_paths,
)
from src.policies import StrictPolicy
from src.scenario import run_scenario


FLEET_LEVELS = [15, 23, 35, 50, 80]
DISPATCH_LEVELS = [3.0, 5.0, 10.0]
P_LEVELS = [0.5, 1.0, 2.0]
R = 20
SIGMA = None  # uses lateness.sigma_levels[0]
S = 1.2


def main() -> int:
    cfg = merge_config_paths(load_config(ROOT / "config.yaml"))
    region_path = ROOT / cfg["region_path"]
    candidates_path = ROOT / cfg["origin_candidates_path"]
    cache_path = ROOT / cfg["cache_path"]
    out_dir = ROOT / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "phase2_singlemode.csv"

    region = load_region_with_origin(region_path, candidates_path, "A")
    graph = build_corridor_graph(region, cache_path)

    seed_base = cfg["experiment"]["seed_base"]
    sigma = cfg["lateness"]["sigma_levels"][0]
    policy = StrictPolicy()

    rows: list[dict] = []
    grid = list(product(FLEET_LEVELS, DISPATCH_LEVELS, P_LEVELS))
    total = len(grid) * R
    print(f"Phase 2 grid: {len(grid)} cells, R={R}, total={total}", flush=True)

    count = 0
    t_start = time.time()
    for fleet, dispatch, p_fail in grid:
        run_cfg = deepcopy(cfg)
        run_cfg["bus"]["fleet_size"] = int(fleet)
        run_cfg["bus"]["dispatch_interval_min"] = float(dispatch)
        for r in range(R):
            seed = seed_base + r
            params = {"s": S, "p_fail_scale": float(p_fail), "sigma": sigma}
            bus = run_scenario(graph, run_cfg, "bus_only", policy, params, seed)
            multi = run_scenario(graph, run_cfg, "multimodal", policy, params, seed)
            base = {
                "bus_fleet_size": int(fleet),
                "bus_dispatch_interval_min": float(dispatch),
                "p_fail_scale": float(p_fail),
                "rep": r,
                "seed": seed,
                "s": S,
            }
            rows.append(_paired_result_row(base, bus, multi))
            count += 1
            if count % 50 == 0:
                elapsed = time.time() - t_start
                print(
                    f"  Phase 2: {count}/{total} elapsed={elapsed:.1f}s",
                    flush=True,
                )

    df = pd.DataFrame(rows)
    df.to_csv(out_path, index=False, encoding="utf-8")
    print(
        f"V07_PHASE2_DONE rows={len(df)} elapsed={time.time() - t_start:.1f}s",
        flush=True,
    )
    print(f"Results saved to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
