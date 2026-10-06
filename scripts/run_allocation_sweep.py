"""Phase 3-1: equal-road-fleet feeder/last-mile allocation surface (n_f=1..22).

Faithful to the paper-revision run path: same base-config builders, same
top-10 execution graph, same CRN seeds; only shuttle/last-mile fleet sizes
are overridden post-apply_revision_config. Invariance subset re-applies the
campaign-identical long-haul slowdown edge set (checksum-verified).
"""
import csv
import json
import sys
import time

import networkx as nx

sys.path.insert(0, "C:\\project\\transport-system-sim")

from src.policies import StrictPolicy
from src.realworld.disruption_scenarios import select_corridor_time_band_edges
from src.realworld.pilot_experiments import (
    apply_pilot_demand_fleet_profiles,
    load_pilot_inputs,
    make_pilot_base_config,
)
from src.realworld.revision_runner import (
    apply_forced_failure_config,
    apply_revision_config,
    selected_edges_checksum,
)
from src.scenario import run_scenario

ROOT = "C:\\project\\transport-system-sim"
OUT = f"{ROOT}\\results\\allocation_sweep_v1"
EXPECTED_EDGE_CHECKSUM = "de3c7dae1e74c705a5cfb1a3e2de5d353776c3db4872151f860ec39e09741518"

import os

os.makedirs(OUT, exist_ok=True)

inputs = load_pilot_inputs(
    region_path="data/regions/goseong_mobilization.yaml",
    cache_path="data/cache/goseong_nodelink_road.graphml",
    road_class_overrides_path="data/parameters/road_class_overrides.csv",
    reduce_graph=False,
)
top10 = nx.read_graphml(
    "results/paper_revision_top10_corridor_v4_20260721/_graph_scope_cache/top10.graphml"
)
band = select_corridor_time_band_edges(
    top10, source="A", target="D", path_count=10,
    lower_fraction=0.2, upper_fraction=0.8,
)
assert selected_edges_checksum(band) == EXPECTED_EDGE_CHECKSUM, "edge set mismatch"
print(f"edge set verified: {len(band)} edges", flush=True)

base, _ = apply_pilot_demand_fleet_profiles(
    make_pilot_base_config(inputs.region), demand_profile_id="pilot_default_demand"
)
policy = StrictPolicy()
params = {"s": 1.0, "p_fail_scale": 0.0, "sigma": 0.75}
seeds = list(range(3101, 3131))

FIELDS = ["n_feeder", "n_lastmile", "road_multiplier", "arrival_seed", "makespan",
          "completion_rate", "empty_return_trips", "empty_return_minutes",
          "road_vehicle_cycles", "bus_minutes", "train_trips", "elapsed_s"]

t_start = time.perf_counter()
with open(f"{OUT}\\sweep_results.csv", "w", newline="", encoding="utf-8") as fh:
    writer = csv.DictWriter(fh, fieldnames=FIELDS)
    writer.writeheader()
    # Main surface: all 23 splits at no-disruption baseline.
    jobs = [(n_f, 1.0) for n_f in range(1, 23)]
    # Invariance subset: extreme/mid splits under 1.0x and 3.0x slowdown.
    jobs += [(n_f, m) for n_f in (1, 6, 12, 17, 22) for m in (1.0, 3.0)
             if not (m == 1.0)]
    # Note: (n_f,1.0) already covered by the main surface; skip dupes.
    seen = set()
    for n_f, mult in jobs:
        if (n_f, mult) in seen:
            continue
        seen.add((n_f, mult))
        for seed in seeds:
            config = apply_revision_config(
                base, policy_id="static_multimodal",
                resource_frame="matched_road_fleet", demand=1000,
            )
            config["multimodal"]["shuttle_fleet_size"] = n_f
            config["multimodal"]["lastmile_fleet_size"] = 23 - n_f
            config = apply_forced_failure_config(
                config, edges=list(band), mode="capacity_reduction",
                capacity_factor=1.0, travel_time_multiplier=mult,
            )
            t0 = time.perf_counter()
            out = run_scenario(G=top10, config=config, scenario_type="multimodal",
                               policy=policy, params=params, seed=seed)
            writer.writerow({
                "n_feeder": n_f, "n_lastmile": 23 - n_f,
                "road_multiplier": mult, "arrival_seed": seed,
                "makespan": out.get("makespan"),
                "completion_rate": out.get("completion_rate"),
                "empty_return_trips": out.get("empty_return_trips"),
                "empty_return_minutes": out.get("empty_return_minutes"),
                "road_vehicle_cycles": out.get("road_vehicle_cycles"),
                "bus_minutes": out.get("bus_minutes"),
                "train_trips": out.get("train_trips"),
                "elapsed_s": round(time.perf_counter() - t0, 3),
            })
        print(f"split {n_f}/(23-{n_f}) @x{mult} done", flush=True)

manifest = {
    "experiment": "allocation_sweep_v1",
    "graph": "top10 (9089 nodes, 18602 edges), checksum-verified execution graph",
    "edge_set": {"count": len(band), "sha256": EXPECTED_EDGE_CHECKSUM},
    "seeds": seeds,
    "policy": "static_multimodal, strict, reverse_network, rail available",
    "demand": 1000,
    "wall_s": round(time.perf_counter() - t_start, 1),
}
with open(f"{OUT}\\manifest.json", "w", encoding="utf-8") as fh:
    json.dump(manifest, fh, indent=1)
print("DONE", manifest["wall_s"], "s", flush=True)
