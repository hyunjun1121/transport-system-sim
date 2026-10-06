"""Phase 3-2: full-graph local break-even validation.

Mirrors the top-10 break-even design on the full reference graph:
multipliers x policies x 30 CRN seeds, matched road fleet (feeder splits
n_f=6 best and n_f=12 legacy), available rail, reverse empty return, plus
configured-bundle sanity cells at 1.0x/3.0x. The long-haul slowdown band is
re-derived on the full graph with the campaign-identical selector; its
checksum is recorded (the manuscript states top-10/full band checksums
match).
"""
import csv
import json
import os
import sys
import time

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
OUT = f"{ROOT}\\results\\fullgraph_breakeven_v1"
os.makedirs(OUT, exist_ok=True)

GRID = [1.50, 1.60, 1.70, 1.74, 1.75, 1.80, 2.00]
SANITY = [1.0, 3.0]
SEEDS = list(range(3101, 3131))
_SPLITS = (6, 12)

if os.environ.get("SMOKE"):
    GRID, SANITY, SEEDS, _SPLITS = [1.74], [], [3101, 3102], (6,)

t_start = time.perf_counter()
inputs = load_pilot_inputs(
    region_path="data/regions/goseong_mobilization.yaml",
    cache_path="data/cache/goseong_nodelink_road.graphml",
    road_class_overrides_path="data/parameters/road_class_overrides.csv",
    reduce_graph=False,
)
full = inputs.graph
print(f"full graph ready: {full.number_of_nodes()} nodes, "
      f"{full.number_of_edges()} edges "
      f"({time.perf_counter()-t_start:.0f}s)", flush=True)

band = select_corridor_time_band_edges(
    full, source="A", target="D", path_count=10,
    lower_fraction=0.2, upper_fraction=0.8,
)
band_checksum = selected_edges_checksum(band)
print(f"full-graph band: {len(band)} edges checksum={band_checksum[:16]}...",
      flush=True)

base, _ = apply_pilot_demand_fleet_profiles(
    make_pilot_base_config(inputs.region), demand_profile_id="pilot_default_demand"
)
policy = StrictPolicy()
params = {"s": 1.0, "p_fail_scale": 0.0, "sigma": 0.75}

FIELDS = ["resource_frame", "n_feeder", "n_lastmile", "road_multiplier",
          "policy_id", "arrival_seed", "makespan", "completion_rate",
          "empty_return_trips", "empty_return_minutes", "road_vehicle_cycles",
          "elapsed_s"]

jobs = []
for mult in GRID:
    for n_f in _SPLITS:
        for pol in ("bus_only", "static_multimodal"):
            jobs.append(("matched_road_fleet", n_f, mult, pol))
for mult in SANITY:
    for pol in ("bus_only", "static_multimodal"):
        jobs.append(("configured_bundle", 12, mult, pol))

CHUNK = os.environ.get("CHUNK", "ALL")
OUT_CSV = f"{OUT}\\fullgraph_results_{CHUNK}.csv"
if CHUNK == "A":
    jobs = [j for j in jobs if j[0] == "matched_road_fleet" and j[1] == 6]
elif CHUNK == "B":
    jobs = [j for j in jobs if j[0] == "matched_road_fleet" and j[1] == 12]
elif CHUNK == "C":
    jobs = [j for j in jobs if j[0] == "configured_bundle"]
print(f"chunk {CHUNK}: {len(jobs)} jobs", flush=True)

# Resume: skip (frame, n_f, mult, policy) cells already complete with 30 rows.
done_cells = set()
if os.path.exists(OUT_CSV):
    import csv as _csv
    with open(OUT_CSV, encoding="utf-8") as _fh:
        for _r in _csv.DictReader(_fh):
            done_cells[(_r["resource_frame"], _r["n_feeder"],
                        _r["road_multiplier"], _r["policy_id"])] = \
                done_cells.get((_r["resource_frame"], _r["n_feeder"],
                                _r["road_multiplier"], _r["policy_id"]), 0) + 1
    jobs = [j for j in jobs
            if done_cells.get((j[0], str(j[1]), str(j[2]), j[3]), 0) < 30]
    print(f"chunk {CHUNK}: {len(jobs)} jobs remain after resume", flush=True)

write_header = not os.path.exists(OUT_CSV)
with open(OUT_CSV, "a", newline="", encoding="utf-8") as fh:
    writer = csv.DictWriter(fh, fieldnames=FIELDS)
    if write_header:
        writer.writeheader()
    for frame, n_f, mult, pol in jobs:
        for seed in SEEDS:
            config = apply_revision_config(
                base, policy_id="bus_only" if pol == "bus_only" else "static_multimodal",
                resource_frame=frame, demand=1000,
            )
            if pol == "static_multimodal" and frame == "matched_road_fleet":
                config["multimodal"]["shuttle_fleet_size"] = n_f
                config["multimodal"]["lastmile_fleet_size"] = 23 - n_f
            config = apply_forced_failure_config(
                config, edges=list(band), mode="capacity_reduction",
                capacity_factor=1.0, travel_time_multiplier=mult,
            )
            stype = "bus_only" if pol == "bus_only" else "multimodal"
            t0 = time.perf_counter()
            out = run_scenario(G=full, config=config, scenario_type=stype,
                               policy=policy, params=params, seed=seed)
            writer.writerow({
                "resource_frame": frame, "n_feeder": n_f if pol != "bus_only" else "",
                "n_lastmile": (23 - n_f) if pol != "bus_only" else "",
                "road_multiplier": mult, "policy_id": pol, "arrival_seed": seed,
                "makespan": out.get("makespan"),
                "completion_rate": out.get("completion_rate"),
                "empty_return_trips": out.get("empty_return_trips"),
                "empty_return_minutes": out.get("empty_return_minutes"),
                "road_vehicle_cycles": out.get("road_vehicle_cycles"),
                "elapsed_s": round(time.perf_counter() - t0, 1),
            })
        fh.flush()
        print(f"done {frame} n_f={n_f} x{mult} {pol} "
              f"({time.perf_counter()-t_start:.0f}s elapsed)", flush=True)

manifest = {
    "experiment": "fullgraph_breakeven_v1",
    "graph": f"full ({full.number_of_nodes()} nodes, {full.number_of_edges()} edges)",
    "band": {"count": len(band), "sha256": band_checksum},
    "grid": GRID, "sanity": SANITY, "splits": [6, 12], "seeds": SEEDS,
    "wall_s": round(time.perf_counter() - t_start, 1),
}
with open(f"{OUT}\\manifest_{CHUNK}.json", "w", encoding="utf-8") as fh:
    json.dump(manifest, fh, indent=1)
print("DONE", manifest["wall_s"], "s", flush=True)
