"""BPR volume-delay no-op sweep (wartime mobilization frame).

Under the wartime assumption civilian background volume V~0, the BPR
volume-delay term ``t0 * (1 + alpha * (V/C)^beta)`` is a near-no-op, so travel
time reduces to ``t0 = distance / free-flow speed``. This script MEASURES that
claim by sweeping ``background_volume`` x ``alpha`` x ``scale`` on a fixed
baseline scenario and reporting the BPR contribution to makespan.

Method (non-circular): for each (volume, scale) the free-flow reference is the
run at ``alpha=0`` (BPR term is then exactly 0 regardless of volume), and
``bpr_delay_pct`` for every alpha>0 row is measured relative to that reference.
So the reported delay is the congestion contribution attributable to BPR, not
an absolute assumption.

Decision-support / quasi-real sensitivity only -- not a calibrated validation
and not an operational forecast. ``final_study_ready`` stays false.

Usage::

    .\\.venv\\Scripts\\python scripts\\run_bpr_noop_sweep.py
    # -> results/bpr_noop_sweep.csv  (+ stdout summary)
"""

from __future__ import annotations

import copy
import csv
import math
import os
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.scenario import run_scenario  # noqa: E402
from src.policies import StrictPolicy  # noqa: E402

DEFAULT_VOLUMES = (0.0, 100.0, 500.0, 2000.0, 5000.0)
DEFAULT_ALPHAS = (0.15, 0.36, 0.74)
DEFAULT_SCALES = (1.0, 2.0)
# alpha=0 => BPR multiplier is exactly 1.0 for any volume => pure free-flow t0.
ALPHA_FREEFLOW = 0.0

SWEEP_COLUMNS = (
    "scenario_type",
    "seed",
    "background_volume",
    "alpha",
    "scale",
    "makespan",
    "completion_rate",
    "bpr_delay_pct",
)

RunFn = Callable[..., dict[str, Any]]


def compute_bpr_delay_pct(freeflow_makespan: float, makespan: float) -> float:
    """BPR-attributable makespan delay (%) vs the alpha=0 free-flow reference."""
    if freeflow_makespan <= 0:
        return 0.0
    return (makespan - freeflow_makespan) / freeflow_makespan * 100.0


def _run_one(
    run_fn: RunFn,
    graph: Any,
    base_config: dict,
    scenario_type: str,
    seed: int,
    sigma: float,
    volume: float,
    alpha: float,
    scale: float,
) -> dict[str, Any]:
    cfg = copy.deepcopy(base_config)
    cfg.setdefault("traffic", {})["background_volume"] = volume
    cfg.setdefault("bpr", {})["alpha"] = alpha
    return run_fn(
        G=graph,
        config=cfg,
        scenario_type=scenario_type,
        policy=StrictPolicy(),
        params={"s": scale, "p_fail_scale": 0.0, "sigma": sigma},
        seed=seed,
    )


def run_bpr_noop_sweep(
    graph: Any,
    base_config: dict,
    *,
    volumes: tuple[float, ...] = DEFAULT_VOLUMES,
    alphas: tuple[float, ...] = DEFAULT_ALPHAS,
    scales: tuple[float, ...] = DEFAULT_SCALES,
    scenario_type: str = "bus_only",
    seed: int = 1101,
    sigma: float = 0.75,
    run_fn: RunFn | None = None,
) -> list[dict[str, Any]]:
    """Sweep background_volume x alpha x scale and return BPR-delay rows.

    ``run_fn`` defaults to :func:`src.scenario.run_scenario`; tests inject a
    deterministic fake so the sweep arithmetic is verified offline/fast.
    """
    run_fn = run_fn or run_scenario
    rows: list[dict[str, Any]] = []
    for scale in scales:
        for volume in volumes:
            ref = _run_one(
                run_fn, graph, base_config, scenario_type, seed, sigma,
                volume, ALPHA_FREEFLOW, scale,
            )
            ref_makespan = ref["makespan"]
            for alpha in alphas:
                res = ref if alpha == ALPHA_FREEFLOW else _run_one(
                    run_fn, graph, base_config, scenario_type, seed, sigma,
                    volume, alpha, scale,
                )
                rows.append(
                    {
                        "scenario_type": scenario_type,
                        "seed": seed,
                        "background_volume": volume,
                        "alpha": alpha,
                        "scale": scale,
                        "makespan": res["makespan"],
                        "completion_rate": res["completion_rate"],
                        "bpr_delay_pct": compute_bpr_delay_pct(
                            ref_makespan, res["makespan"]
                        ),
                    }
                )
    return rows


def _finite_max_delay(rows: list[dict[str, Any]], max_volume: float) -> float:
    """Max finite BPR delay over rows with background_volume <= max_volume.

    Saturation rows (makespan=inf, completion collapses) are excluded -- they
    mark a capacity-collapse regime beyond 'wartime residual traffic', not a
    BPR-delay measurement.
    """
    vals = [
        r["bpr_delay_pct"]
        for r in rows
        if r["background_volume"] <= max_volume
        and math.isfinite(r["bpr_delay_pct"])
    ]
    return max(vals) if vals else 0.0


def _delay_at(rows: list[dict[str, Any]], volume: float) -> float:
    """Max finite BPR delay across alpha/scale at a fixed volume."""
    vals = [
        r["bpr_delay_pct"]
        for r in rows
        if r["background_volume"] == volume and math.isfinite(r["bpr_delay_pct"])
    ]
    return max(vals) if vals else float("inf")


def main() -> None:
    from src.realworld.pilot_experiments import (  # noqa: E402
        apply_pilot_demand_fleet_profiles,
        load_pilot_inputs,
        make_pilot_base_config,
    )

    os.chdir(ROOT)
    region = "data/regions/goseong_mobilization.yaml"
    cache = "data/cache/goseong_nodelink_road.graphml"
    overrides = "data/parameters/road_class_overrides.csv"
    inputs = load_pilot_inputs(
        region_path=region, cache_path=cache, road_class_overrides_path=overrides
    )
    base = apply_pilot_demand_fleet_profiles(make_pilot_base_config(inputs.region))[0]

    rows = run_bpr_noop_sweep(inputs.graph, base, scenario_type="bus_only", seed=1101)
    out = ROOT / "results" / "bpr_noop_sweep.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=SWEEP_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {len(rows)} rows -> {out}")
    print(
        "BPR makespan delay at canonical background_volume=100 (config default): "
        f"{_delay_at(rows, 100.0):.4f}%"
    )
    print(
        "max finite BPR delay for background_volume<=500 (realistic wartime residual): "
        f"{_finite_max_delay(rows, 500.0):.4f}%"
    )
    print("Decision-support / quasi-real sensitivity only; not a calibrated validation.")


if __name__ == "__main__":
    main()
