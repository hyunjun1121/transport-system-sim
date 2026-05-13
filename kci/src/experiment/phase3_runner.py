"""Phase 3 counterfactual lever-sweep runner.

Sweeps rail_headway_min x lastmile_fleet_size x rail_capacity_pax_per_train
x p_fail_scale on the active network/failure context, using paired CRN
between bus_only and multimodal scenarios.
"""

from copy import deepcopy

import networkx as nx
import pandas as pd

from src.experiment.doe import Phase3Point, phase3_grid
from src.experiment.runner import _ContextCache, _paired_result_row
from src.policies import StrictPolicy
from src.scenario import run_scenario

try:  # pragma: no cover - prefer canonical helper from A3 when available
    from src.kci_runtime import apply_phase3_lever_override  # type: ignore
except ImportError:  # pragma: no cover - local fallback until A3 ships
    apply_phase3_lever_override = None  # type: ignore[assignment]


def _fallback_apply_phase3_lever_override(
    run_config: dict, point: Phase3Point
) -> dict:
    """Mutate run_config in place to reflect Phase 3 lever values.

    Updates both the ``multimodal`` block (read by scenario simulation) and
    the first ``network.rail_link`` row (read by network/scenario.py) so the
    lever values are consumed regardless of which code path looks them up.
    """
    multimodal = run_config.setdefault("multimodal", {})
    multimodal["rail_headway_min"] = point.rail_headway_min
    multimodal["lastmile_fleet_size"] = int(point.lastmile_fleet_size)
    multimodal["rail_capacity_pax_per_train"] = int(point.rail_capacity_pax_per_train)

    network = run_config.setdefault("network", {})
    rail_links = network.get("rail_link")
    if isinstance(rail_links, list) and rail_links:
        mutable_links = [list(link) for link in rail_links]
        first = mutable_links[0]
        # rail_link tuple convention: [..., ..., ..., headway_min, capacity, ...]
        if len(first) > 3:
            first[3] = point.rail_headway_min
        if len(first) > 4:
            first[4] = int(point.rail_capacity_pax_per_train)
        mutable_links[0] = first
        network["rail_link"] = mutable_links

    return run_config


def _override(run_config: dict, point: Phase3Point) -> dict:
    if apply_phase3_lever_override is not None:
        return apply_phase3_lever_override(run_config, point)
    return _fallback_apply_phase3_lever_override(run_config, point)


def run_phase3(
    config: dict, G: nx.DiGraph = None, verbose: bool = True
) -> pd.DataFrame:
    """Run Phase 3: counterfactual lever sweep.

    For each lever cell, run R paired replications using the same seed for
    bus_only and multimodal scenarios. Uses STRICT policy and Phase-1 base
    sigma (``lateness.sigma_levels[0]``).
    """
    grid = phase3_grid(config)
    experiment = config["experiment"]
    R = int(experiment.get("R_phase3", experiment["R"]))
    seed_base = experiment["seed_base"]
    policy = StrictPolicy()
    sigma = config["lateness"]["sigma_levels"][0]
    context_cache = _ContextCache(config, G)

    results = []
    total = len(grid) * R
    count = 0

    for point in grid:
        base_config, run_graph = context_cache.get(
            point.network_variant,
            point.failure_mode,
            point.capacity_reduction_factor,
        )
        # Deepcopy per cell so paired CRN within a cell sees a consistent
        # config but lever overrides don't leak across cells. Reassign the
        # _override() return value: the canonical kci_runtime helper does its
        # own deepcopy and returns a fresh dict, so in-place mutation alone
        # would not propagate the lever values.
        run_config = _override(deepcopy(base_config), point)

        for r in range(R):
            seed = seed_base + r
            params = {
                "s": 1.0,
                "p_fail_scale": point.p_fail_scale,
                "sigma": sigma,
            }

            bus = run_scenario(
                run_graph, run_config, "bus_only", policy, params, seed
            )
            multi = run_scenario(
                run_graph, run_config, "multimodal", policy, params, seed
            )

            results.append(_paired_result_row({
                "rail_headway_min": point.rail_headway_min,
                "lastmile_fleet_size": point.lastmile_fleet_size,
                "rail_capacity_pax_per_train": point.rail_capacity_pax_per_train,
                "p_fail_scale": point.p_fail_scale,
                "network_variant": point.network_variant,
                "failure_mode": point.failure_mode,
                "capacity_reduction_factor": point.capacity_reduction_factor,
                "rep": r,
                "seed": seed,
            }, bus, multi))
            count += 1
            if verbose and count % 50 == 0:
                print(f"  Phase 3: {count}/{total}")

    return pd.DataFrame(results)
