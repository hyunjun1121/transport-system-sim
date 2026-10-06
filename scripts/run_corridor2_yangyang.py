"""Phase 4: second corridor (Songpa-Yangyang) transferability case.

Same anchors A/S/R, new destination D (Yangyang county-office centroid).
Protocol subset: graph-scope audit (7 scenarios, configured bundle) ->
resource-frame baseline sign -> allocation surface -> break-even sweep at
the corridor-2 best split. Edge selection reuses the campaign-identical
selectors frozen on the corridor-2 top-3 graph.
"""
import csv
import json
import os
import statistics
import sys
import time

import networkx as nx

sys.path.insert(0, "C:\\project\\transport-system-sim")

from src.policies import StrictPolicy
from src.realworld.disruption_scenarios import (
    load_disruption_scenarios,
    select_candidate_edges,
    select_corridor_time_band_edges,
)
from src.realworld.osm_network import _graphml_safe_copy
from src.realworld.pilot_experiments import (
    apply_pilot_demand_fleet_profiles,
    load_pilot_inputs,
    make_pilot_base_config,
    pilot_experiment_multi_corridor_subgraphs,
)
from src.realworld.revision_runner import (
    apply_forced_failure_config,
    apply_revision_config,
    selected_edges_checksum,
)
from src.scenario import run_scenario

ROOT = "C:\\project\\transport-system-sim"
OUT = f"{ROOT}\\results\\corridor2_yangyang_v1"
os.makedirs(OUT + "\\_graphs", exist_ok=True)

SEEDS30 = list(range(3101, 3131))
SEEDS5 = list(range(3101, 3106))
AUDIT_SCENARIOS = [
    "no_disruption",
    "yangyang_long_haul_damage_severe",
    "yangyang_critical_link_blockage",
    "yangyang_random_blockage",
    "yangyang_access_road_damage_severe",
    "yangyang_last_mile_damage_severe",
    "yangyang_random_capacity_reduction",
]
SCEN_PARAMS = {  # mode, capacity_factor, road_multiplier
    "no_disruption": None,
    "yangyang_long_haul_damage_severe": ("capacity_reduction", 1.0, 3.0),
    "yangyang_critical_link_blockage": ("blocked", 0.0, 1.0),
    "yangyang_random_blockage": ("blocked", 0.0, 1.0),
    "yangyang_access_road_damage_severe": ("capacity_reduction", 1.0, 3.0),
    "yangyang_last_mile_damage_severe": ("capacity_reduction", 1.0, 3.0),
    "yangyang_random_capacity_reduction": ("capacity_reduction", 0.30, 1.0),
}
BE_GRID = [1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.5, 3.0]

t_start = time.perf_counter()
inputs = load_pilot_inputs(
    region_path="data/regions/yangyang_mobilization.yaml",
    cache_path="data/cache/goseong_nodelink_road.graphml",
    road_class_overrides_path="data/parameters/road_class_overrides.csv",
    reduce_graph=False,
)
full_yy = inputs.graph
print(f"yangyang full graph: {full_yy.number_of_nodes()} nodes", flush=True)
scopes = pilot_experiment_multi_corridor_subgraphs(full_yy, path_counts=(3, 5, 10))
graphs = {"top3": scopes[3], "top5": scopes[5], "top10": scopes[10], "full": full_yy}
for name, graph in graphs.items():
    if name != "full":
        nx.write_graphml(
            _graphml_safe_copy(graph), f"{OUT}\\_graphs\\{name}.graphml")
    print(f"scope {name}: {graph.number_of_nodes()} nodes, "
          f"{graph.number_of_edges()} edges", flush=True)

scenarios = {s.scenario_id: s for s in load_disruption_scenarios(
    "data/scenarios/goseong_disruption_scenarios.csv",
    region_id="yangyang_mobilization")}
top3 = graphs["top3"]
frozen, missing_report = {}, {}
for sid in AUDIT_SCENARIOS:
    if sid == "no_disruption":
        frozen[sid] = ()
        continue
    sc = scenarios[sid]
    if sc.selection_method == "corridor_time_band":
        edges = select_corridor_time_band_edges(
            top3, source="A", target="D", path_count=3,
            lower_fraction=0.2, upper_fraction=0.8)
        frozen[sid] = tuple((str(u), str(v)) for u, v in edges)
    else:
        frozen[sid] = tuple(
            (str(item.edge[0]), str(item.edge[1]))
            for item in select_candidate_edges(top3, sc))
    print(f"frozen {sid}: {len(frozen[sid])} edges", flush=True)

base, _ = apply_pilot_demand_fleet_profiles(
    make_pilot_base_config(inputs.region), demand_profile_id="pilot_default_demand"
)
policy = StrictPolicy()
params = {"s": 1.0, "p_fail_scale": 0.0, "sigma": 0.75}
FIELDS = ["part", "scenario_id", "graph_scope", "resource_frame", "n_feeder",
          "road_multiplier", "policy_id", "arrival_seed", "makespan",
          "completion_rate", "empty_return_trips", "empty_return_minutes",
          "road_vehicle_cycles", "elapsed_s"]


def run_one(writer, graph, scenario_id, frame, policy_id, seed, mult=1.0,
            n_f=None, part="audit", edges_override=None):
    config = apply_revision_config(
        base, policy_id="bus_only" if policy_id == "bus_only" else "static_multimodal",
        resource_frame=frame, demand=1000)
    if policy_id == "static_multimodal" and frame == "matched_road_fleet" and n_f:
        config["multimodal"]["shuttle_fleet_size"] = n_f
        config["multimodal"]["lastmile_fleet_size"] = 23 - n_f
    edges = frozen.get(scenario_id, ()) if edges_override is None else edges_override
    present = [e for e in edges if graph.has_edge(*e)]
    if edges_override is not None:
        config = apply_forced_failure_config(
            config, edges=present, mode="capacity_reduction",
            capacity_factor=1.0, travel_time_multiplier=mult)
    elif scenario_id != "no_disruption":
        mode, cfac, _ = SCEN_PARAMS[scenario_id]
        config = apply_forced_failure_config(
            config, edges=present, mode=mode, capacity_factor=cfac,
            travel_time_multiplier=mult)
    stype = "bus_only" if policy_id == "bus_only" else "multimodal"
    t0 = time.perf_counter()
    out = run_scenario(G=graph, config=config, scenario_type=stype,
                       policy=policy, params=params, seed=seed)
    writer.writerow({"part": part, "scenario_id": scenario_id,
                     "graph_scope": "", "resource_frame": frame,
                     "n_feeder": n_f or "", "road_multiplier": mult,
                     "policy_id": policy_id, "arrival_seed": seed,
                     "makespan": out.get("makespan"),
                     "completion_rate": out.get("completion_rate"),
                     "empty_return_trips": out.get("empty_return_trips"),
                     "empty_return_minutes": out.get("empty_return_minutes"),
                     "road_vehicle_cycles": out.get("road_vehicle_cycles"),
                     "elapsed_s": round(time.perf_counter() - t0, 1)})
    return len(edges) - len(present)


with open(f"{OUT}\\corridor2_results.csv", "w", newline="", encoding="utf-8") as fh:
    writer = csv.DictWriter(fh, fieldnames=FIELDS)
    writer.writeheader()
    # Part A: graph-scope audit, configured bundle.
    audit_missing = {}
    for sid in AUDIT_SCENARIOS:
        for scope_name, graph in graphs.items():
            seeds = SEEDS5 if scope_name == "full" else SEEDS30
            for pol in ("bus_only", "static_multimodal"):
                for seed in seeds:
                    miss = run_one(writer, graph, sid, "configured_bundle", pol, seed)
                fh.flush()
            if sid != "no_disruption":
                audit_missing[f"{sid}@{scope_name}"] = miss
        print(f"audit {sid} done", flush=True)
    # Part B: resource-frame baseline on corridor-2 top-10.
    for frame in ("configured_bundle", "matched_road_fleet"):
        for pol in ("bus_only", "static_multimodal"):
            for seed in SEEDS30:
                run_one(writer, graphs["top10"], "no_disruption", frame, pol, seed,
                        part="baseline")
            fh.flush()
        print(f"baseline {frame} done", flush=True)
    # Part C: allocation surface (matched, multimodal, no disruption).
    for n_f in range(1, 23):
        for seed in SEEDS30:
            run_one(writer, graphs["top10"], "no_disruption", "matched_road_fleet",
                    "static_multimodal", seed, n_f=n_f, part="allocation")
        fh.flush()
    print("allocation surface done", flush=True)

# Best split = min mean makespan among fully-complete splits.
import csv as _csv
alloc = {}
with open(f"{OUT}\\corridor2_results.csv", encoding="utf-8") as fh:
    for r in _csv.DictReader(fh):
        if r["part"] == "allocation" and r["makespan"]:
            alloc.setdefault(int(r["n_feeder"]), []).append(float(r["makespan"]))
best = min(
    ((n, statistics.mean(v)) for n, v in alloc.items()),
    key=lambda kv: kv[1],
)
print(f"corridor-2 best split: n_f={best[0]} mean={best[1]:.1f}", flush=True)

band = select_corridor_time_band_edges(
    graphs["top10"], source="A", target="D", path_count=10,
    lower_fraction=0.2, upper_fraction=0.8)
band_checksum = selected_edges_checksum(band)
print(f"corridor-2 band: {len(band)} edges {band_checksum[:16]}...", flush=True)
with open(f"{OUT}\\corridor2_results.csv", "a", newline="", encoding="utf-8") as fh:
    writer = _csv.DictWriter(fh, fieldnames=FIELDS)
    for mult in BE_GRID:
        for pol in ("bus_only", "static_multimodal"):
            for seed in SEEDS30:
                run_one(writer, graphs["top10"], "no_disruption",
                        "matched_road_fleet", pol, seed, mult=mult,
                        n_f=best[0] if pol == "static_multimodal" else None,
                        part="breakeven",
                        edges_override=[(str(u), str(v)) for u, v in band])
            fh.flush()
        print(f"breakeven x{mult} done", flush=True)

manifest = {
    "experiment": "corridor2_yangyang_v1",
    "region": "yangyang_mobilization (D=Yangyang county-office centroid)",
    "scopes": {k: {"nodes": g.number_of_nodes(), "edges": g.number_of_edges()}
               for k, g in graphs.items()},
    "frozen_from": "corridor-2 top3",
    "frozen_missing_on_execution_scope": audit_missing,
    "best_split": {"n_feeder": best[0], "mean_makespan": round(best[1], 1)},
    "band": {"count": len(band), "sha256": band_checksum},
    "wall_s": round(time.perf_counter() - t_start, 1),
}
json.dump(manifest, open(f"{OUT}\\manifest.json", "w"), indent=1)
print("DONE", manifest["wall_s"], "s", flush=True)
