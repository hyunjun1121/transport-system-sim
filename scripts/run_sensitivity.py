"""Phase 3-3: local break-even sensitivity (one-at-a-time perturbations).

Bus-side perturbations rerun the coarse multiplier grid (top-10, matched
frame); multimodal-side perturbations run at baseline only (structural
multiplier-invariance proven in Phase 3-1/3-2). Rail service perturbed via
network.rail_link entries; sigma via run params.
"""
import csv
import json
import os
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
OUT = f"{ROOT}\\results\\sensitivity_v1"
os.makedirs(OUT, exist_ok=True)
EXPECTED_EDGE_CHECKSUM = "de3c7dae1e74c705a5cfb1a3e2de5d353776c3db4872151f860ec39e09741518"

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
assert selected_edges_checksum(band) == EXPECTED_EDGE_CHECKSUM
base, _ = apply_pilot_demand_fleet_profiles(
    make_pilot_base_config(inputs.region), demand_profile_id="pilot_default_demand"
)
print("base rail_link:", base["network"]["rail_link"], flush=True)
policy = StrictPolicy()
SEEDS = list(range(3101, 3131))
GRID = [1.0, 1.2, 1.4, 1.6, 1.8, 2.0]

FIELDS = ["perturbation", "side", "param", "value", "road_multiplier",
          "arrival_seed", "makespan", "completion_rate", "elapsed_s"]


def run_cell(writer, tag, side, param, value, pol, mult, demand=1000,
             sigma=0.75, mutate=None):
    config = apply_revision_config(
        base, policy_id="bus_only" if pol == "bus_only" else "static_multimodal",
        resource_frame="matched_road_fleet", demand=demand,
    )
    if pol == "static_multimodal":
        config["multimodal"]["shuttle_fleet_size"] = 6
        config["multimodal"]["lastmile_fleet_size"] = 17
    if mutate:
        mutate(config)
    config = apply_forced_failure_config(
        config, edges=list(band), mode="capacity_reduction",
        capacity_factor=1.0, travel_time_multiplier=mult,
    )
    stype = "bus_only" if pol == "bus_only" else "multimodal"
    params = {"s": 1.0, "p_fail_scale": 0.0, "sigma": sigma}
    for seed in SEEDS:
        t0 = time.perf_counter()
        out = run_scenario(G=top10, config=config, scenario_type=stype,
                           policy=policy, params=params, seed=seed)
        writer.writerow({"perturbation": tag, "side": side, "param": param,
                         "value": value, "road_multiplier": mult,
                         "arrival_seed": seed, "makespan": out.get("makespan"),
                         "completion_rate": out.get("completion_rate"),
                         "elapsed_s": round(time.perf_counter() - t0, 3)})


def set_rail_link(config, travel=None, headway=None, capacity=None):
    link = list(config["network"]["rail_link"][0])
    if travel is not None:
        link[2] = travel
    if headway is not None:
        link[3] = headway
    if capacity is not None:
        link[4] = capacity
    config["network"]["rail_link"][0] = link


def set_turnaround(config, value):
    config["bus"]["turnaround_min"] = value
    config["multimodal"]["shuttle_turnaround_min"] = value
    config["multimodal"]["lastmile_turnaround_min"] = value


t_start = time.perf_counter()
with open(f"{OUT}\\sensitivity_results.csv", "w", newline="", encoding="utf-8") as fh:
    writer = csv.DictWriter(fh, fieldnames=FIELDS)
    writer.writeheader()
    # Bus-side: full coarse grid per perturbation.
    for tag, kw in [
        ("B1_demand1500", {"demand": 1500}),
        ("B2_sigma1.0", {"sigma": 1.0}),
        ("B3_turnaround12", {"mutate": lambda c: set_turnaround(c, 12.0)}),
    ]:
        for mult in GRID:
            run_cell(writer, tag, "bus", tag.split("_", 1)[1], tag.split("_", 1)[1],
                     "bus_only", mult, demand=kw.get("demand", 1000),
                     sigma=kw.get("sigma", 0.75), mutate=kw.get("mutate"))
        print(f"done {tag}", flush=True)
    # Multimodal-side: baseline multiplier only.
    multi_jobs = [
        ("M1_rail102.6", lambda c: set_rail_link(c, travel=102.6)),
        ("M2_rail125.4", lambda c: set_rail_link(c, travel=125.4)),
        ("M3_headway20", lambda c: set_rail_link(c, headway=20.0)),
        ("M4_headway45", lambda c: set_rail_link(c, headway=45.0)),
        ("M5_cap450", lambda c: set_rail_link(c, capacity=450)),
        ("M6_cap800", lambda c: set_rail_link(c, capacity=800)),
        ("M7_transfer1.0", lambda c: c["multimodal"].__setitem__("transfer_time_min", 1.0)),
        ("M8_transfer15.0", lambda c: c["multimodal"].__setitem__("transfer_time_min", 15.0)),
        ("M9_turnaround12", lambda c: set_turnaround(c, 12.0)),
        ("M10_demand1500", None),
    ]
    for tag, mutate in multi_jobs:
        kw = {"demand": 1500} if tag == "M10_demand1500" else {}
        run_cell(writer, tag, "multimodal", tag.split("_", 1)[1], tag.split("_", 1)[1],
                 "static_multimodal", 1.0, mutate=mutate, **kw)
        print(f"done {tag}", flush=True)

manifest = {"experiment": "sensitivity_v1", "graph": "top10",
            "wall_s": round(time.perf_counter() - t_start, 1)}
json.dump(manifest, open(f"{OUT}\\manifest.json", "w"), indent=1)
print("DONE", manifest["wall_s"], "s", flush=True)
