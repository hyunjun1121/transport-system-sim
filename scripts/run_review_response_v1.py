"""Review-response analyses for the IEEE Access manuscript revision.

Subcommands (each resumable via run-key skip logic):
  holdout       Independent seed block 3301-3330: 22-split multimodal sweep
                + bus break-even grid; holdout best split, paired delta CI,
                and holdout crossing with joint-seed bootstrap.
  nested        Nested selection bootstrap on the original 22-split sweep:
                re-select the argmin split inside every seed resample.
  band          Formal 5%-mean-regret band definition from the original sweep;
                band membership, per-split crossings, endpoint bootstrap CIs.
  fullendpoints Full-graph multimodal runs at the band endpoint splits plus
                endpoint crossings with joint-seed bootstrap and replicate counts.
  joint         Joint factorial sensitivity (rail x headway x transfer x
                turnaround) around the 6/17 crossing.
  ablation      Adaptive-policy allocation ablation: static vs precheck under
                available/unavailable rail across five allocations.
  repcounts     Recompute headline crossing bootstraps recording
                successful-replicate counts and excluded seeds.

Outputs live in results/review_response_v1/.
"""
import argparse
import csv
import json
import math
import os
import random
import statistics
import sys
import time

import networkx as nx

ROOT = "C:\\project\\transport-system-sim"
sys.path.insert(0, ROOT)

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
from src.realworld.revision_statistics import (
    estimate_piecewise_linear_zero_crossing,
    joint_seed_zero_crossing_bootstrap,
    percentile_bootstrap_ci,
    t_paired_confidence_interval,
)
from src.scenario import run_scenario

OUT = f"{ROOT}\\results\\review_response_v1"
SWEEP = f"{ROOT}\\results\\allocation_sweep_v1\\sweep_results.csv"
BE = f"{ROOT}\\results\\paper_revision_top10_corridor_v4_20260721\\break_even\\full_results.csv"
BE_FINE = f"{ROOT}\\results\\paper_revision_top10_corridor_v4_20260721\\break_even_fine\\full_results.csv"
FG = f"{ROOT}\\results\\fullgraph_breakeven_v1\\fullgraph_results.csv"
EXPECTED_EDGE_CHECKSUM = "de3c7dae1e74c705a5cfb1a3e2de5d353776c3db4872151f860ec39e09741518"
HOLDOUT_SEEDS = list(range(3301, 3331))
HOLDOUT_GRID = [1.0, 1.1, 1.15, 1.2, 1.25, 1.3, 1.4, 1.5, 1.6,
                1.7, 1.75, 1.8, 2.0, 2.5, 3.0]
BE_GRID = [1.0, 1.1, 1.2, 1.25, 1.3, 1.35, 1.4, 1.425, 1.45, 1.475,
           1.5, 1.6, 1.8, 2.0, 2.5, 3.0]
BOOT_SEED = 20260721


def load_top10():
    return nx.read_graphml(
        "results/paper_revision_top10_corridor_v4_20260721/_graph_scope_cache/top10.graphml"
    )


def load_band(graph):
    band = select_corridor_time_band_edges(
        graph, source="A", target="D", path_count=10,
        lower_fraction=0.2, upper_fraction=0.8,
    )
    assert selected_edges_checksum(band) == EXPECTED_EDGE_CHECKSUM
    return band


def load_base():
    inputs = load_pilot_inputs(
        region_path="data/regions/goseong_mobilization.yaml",
        cache_path="data/cache/goseong_nodelink_road.graphml",
        road_class_overrides_path="data/parameters/road_class_overrides.csv",
        reduce_graph=False,
    )
    base, _ = apply_pilot_demand_fleet_profiles(
        make_pilot_base_config(inputs.region),
        demand_profile_id="pilot_default_demand",
    )
    return inputs, base


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


def resume_keys(path, key_fields):
    done = set()
    if not os.path.exists(path):
        return done
    with open(path, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            done.add(tuple(row.get(k, "") for k in key_fields))
    return done


def open_writer(path, fields):
    exists = os.path.exists(path)
    fh = open(path, "a", newline="", encoding="utf-8")
    writer = csv.DictWriter(fh, fieldnames=fields)
    if not exists:
        writer.writeheader()
    return fh, writer


def run_one(graph, band, base, *, policy_id, n_f, mult, seed,
            rail_status="available", mutate=None, demand=1000, sigma=0.75):
    config = apply_revision_config(
        base, policy_id=policy_id,
        resource_frame="matched_road_fleet", demand=demand,
        rail_status=rail_status,
    )
    if policy_id != "bus_only":
        config["multimodal"]["shuttle_fleet_size"] = n_f
        config["multimodal"]["lastmile_fleet_size"] = 23 - n_f
    if mutate:
        mutate(config)
    config = apply_forced_failure_config(
        config, edges=list(band), mode="capacity_reduction",
        capacity_factor=1.0, travel_time_multiplier=mult,
    )
    stype = "bus_only" if policy_id == "bus_only" else "multimodal"
    params = {"s": 1.0, "p_fail_scale": 0.0, "sigma": sigma}
    return run_scenario(G=graph, config=config, scenario_type=stype,
                        policy=StrictPolicy(), params=params, seed=seed)


def read_sweep_means(path=SWEEP):
    """Original 22-split sweep: {(n_f, seed): makespan} at multiplier 1.0."""
    values = {}
    with open(path, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if float(row["road_multiplier"]) != 1.0:
                continue
            values[(int(row["n_feeder"]), int(row["arrival_seed"]))] = (
                float(row["makespan"])
            )
    return values


def read_bus_curves(paths=(BE, BE_FINE)):
    """Top-10 bus curves: {seed: {mult: makespan}}, matched frame."""
    curves = {}
    for path in paths:
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                if row["policy_id"] != "bus_only":
                    continue
                if row["resource_frame"] != "matched_road_fleet":
                    continue
                if float(row["completion_rate"] or 0) < 1.0:
                    continue
                seed = int(row["arrival_seed"])
                mult = float(row["road_multiplier"])
                curves.setdefault(seed, {})[mult] = float(row["makespan"])
    return curves


def read_full_bus_curves(path=FG):
    curves = {}
    with open(path, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            if row["policy_id"] != "bus_only":
                continue
            if row["resource_frame"] != "matched_road_fleet":
                continue
            if float(row["completion_rate"] or 0) < 1.0:
                continue
            seed = int(row["arrival_seed"])
            mult = float(row["road_multiplier"])
            curves.setdefault(seed, {})[mult] = float(row["makespan"])
    return curves


def crossing_from_curves(bus_curves, multi_by_seed):
    """Point crossing of mean(bus) - flat mean(multi); returns estimate or None."""
    grid = sorted({m for curve in bus_curves.values() for m in curve})
    bus_mean = {}
    for m in grid:
        vals = [curve[m] for curve in bus_curves.values() if m in curve]
        if vals:
            bus_mean[m] = statistics.fmean(vals)
    multi_mean = statistics.fmean(list(multi_by_seed.values()))
    points = [(m, bus_mean[m] - multi_mean) for m in sorted(bus_mean)]
    est = estimate_piecewise_linear_zero_crossing(points)
    return est.crossing if est.crossing is not None else None


def joint_crossing(bus_curves, multi_by_seed):
    """Joint-seed bootstrap crossing for bus-curve minus flat-multimodal."""
    seeds = sorted(set(bus_curves) & set(multi_by_seed))
    grid = sorted({m for curve in bus_curves.values() for m in curve})
    outcomes = {}
    for seed in seeds:
        if all(m in bus_curves[seed] for m in grid):
            outcomes[seed] = {
                m: bus_curves[seed][m] - multi_by_seed[seed] for m in grid
            }
    interval = joint_seed_zero_crossing_bootstrap(
        outcomes, confidence=0.95, replicates=10_000, seed=BOOT_SEED,
    )
    return {
        "estimate": interval.estimate,
        "lower": interval.lower,
        "upper": interval.upper,
        "complete_seed_count": interval.complete_seed_count,
        "excluded_seeds": list(interval.excluded_seeds),
        "successful_replicates": interval.successful_replicates,
        "replicates": interval.replicates,
    }


def cmd_holdout(args):
    os.makedirs(OUT, exist_ok=True)
    t0 = time.perf_counter()
    top10 = load_top10()
    band = load_band(top10)
    _, base = load_base()
    print(f"graph ready ({time.perf_counter()-t0:.0f}s)", flush=True)

    fields = ["policy_id", "n_feeder", "road_multiplier", "arrival_seed",
              "makespan", "completion_rate", "elapsed_s"]
    path = f"{OUT}\\holdout_results.csv"
    done = resume_keys(path, ["policy_id", "n_feeder", "road_multiplier",
                              "arrival_seed"])
    fh, writer = open_writer(path, fields)

    jobs = [("static_multimodal", n_f, 1.0) for n_f in range(1, 23)]
    jobs += [("bus_only", 0, m) for m in HOLDOUT_GRID]
    for policy_id, n_f, mult in jobs:
        for seed in HOLDOUT_SEEDS:
            key = (policy_id, str(n_f), str(mult), str(seed))
            if key in done:
                continue
            t1 = time.perf_counter()
            out = run_one(top10, band, base, policy_id=policy_id, n_f=n_f,
                          mult=mult, seed=seed)
            writer.writerow({
                "policy_id": policy_id, "n_feeder": n_f,
                "road_multiplier": mult, "arrival_seed": seed,
                "makespan": out.get("makespan"),
                "completion_rate": out.get("completion_rate"),
                "elapsed_s": round(time.perf_counter() - t1, 3),
            })
            fh.flush()
        print(f"holdout {policy_id} n_f={n_f} x{mult} done", flush=True)
    fh.close()

    rows = list(csv.DictReader(open(path, encoding="utf-8-sig", newline="")))
    multi = {(int(r["n_feeder"]), int(r["arrival_seed"])): float(r["makespan"])
             for r in rows
             if r["policy_id"] == "static_multimodal"
             and r["makespan"] not in ("", None)}
    bus = {int(r["arrival_seed"]): float(r["makespan"]) for r in rows
           if r["policy_id"] == "bus_only"
           and r["makespan"] not in ("", None)
           and float(r["road_multiplier"]) == 1.0}
    means = {n_f: statistics.fmean(
        multi[(n_f, s)] for s in HOLDOUT_SEEDS
        if (n_f, s) in multi) for n_f in range(1, 23)}
    best = min(means, key=lambda n_f: (means[n_f], n_f))
    paired_seeds = [s for s in HOLDOUT_SEEDS
                    if s in bus and (best, s) in multi]
    diffs = [bus[s] - multi[(best, s)] for s in paired_seeds]
    t_ci = t_paired_confidence_interval(diffs)
    b_ci = percentile_bootstrap_ci(diffs)
    bus_curves = {}
    for r in rows:
        if (r["policy_id"] == "bus_only"
                and r["makespan"] not in ("", None)):
            bus_curves.setdefault(int(r["arrival_seed"]), {})[
                float(r["road_multiplier"])] = float(r["makespan"])
    multi_best = {s: multi[(best, s)] for s in HOLDOUT_SEEDS
                  if (best, s) in multi}
    holdout_cross = joint_crossing(bus_curves, multi_best)
    summary = {
        "seeds": HOLDOUT_SEEDS,
        "split_means_holdout": {str(k): round(v, 2) for k, v in means.items()},
        "best_split_holdout": best,
        "best_mean_holdout": round(means[best], 2),
        "original_best_split": 6,
        "delta_at_best": {
            "mean": round(t_ci.estimate, 2),
            "t_lower": round(t_ci.lower, 2),
            "t_upper": round(t_ci.upper, 2),
            "boot_lower": round(b_ci.lower, 2),
            "boot_upper": round(b_ci.upper, 2),
        },
        "holdout_crossing": holdout_cross,
        "wall_s": round(time.perf_counter() - t0, 1),
    }
    json.dump(summary, open(f"{OUT}\\holdout_summary.json", "w"), indent=1)
    print(json.dumps(summary, indent=1)[:1200], flush=True)


def cmd_nested(args):
    sweep = read_sweep_means()
    seeds = sorted({seed for (_, seed) in sweep})
    bus_curves = read_bus_curves()
    means = {n_f: statistics.fmean(
        sweep[(n_f, s)] for s in seeds) for n_f in range(1, 23)}
    original_best = min(means, key=lambda n_f: (means[n_f], n_f))
    bus_flat = {s: bus_curves[s][1.0] for s in seeds if 1.0 in bus_curves.get(s, {})}

    rng = random.Random(BOOT_SEED)
    replicates = 10_000
    selected = {}
    sel_means = []
    sel_deltas = []
    crossings = []
    valid_crossings = 0
    for _ in range(replicates):
        sample = [rng.choice(seeds) for _ in seeds]
        sample_means = {
            n_f: statistics.fmean(sweep[(n_f, s)] for s in sample)
            for n_f in range(1, 23)
        }
        star = min(sample_means, key=lambda n_f: (sample_means[n_f], n_f))
        selected[star] = selected.get(star, 0) + 1
        sel_means.append(sample_means[star])
        sel_deltas.append(statistics.fmean(bus_flat[s] for s in sample)
                          - sample_means[star])
        grid = sorted({m for curve in bus_curves.values() for m in curve})
        bus_mean = {}
        for m in grid:
            vals = [bus_curves[s][m] for s in sample if m in bus_curves[s]]
            if vals:
                bus_mean[m] = statistics.fmean(vals)
        multi_star = statistics.fmean(sweep[(star, s)] for s in sample)
        points = [(m, bus_mean[m] - multi_star) for m in sorted(bus_mean)]
        est = estimate_piecewise_linear_zero_crossing(points)
        if est.crossing is not None:
            crossings.append(est.crossing)
            valid_crossings += 1

    def pct(values, p):
        if not values:
            return None
        values = sorted(values)
        idx = p * (len(values) - 1)
        lo = math.floor(idx)
        hi = math.ceil(idx)
        if lo == hi:
            return values[lo]
        return values[lo] + (values[hi] - values[lo]) * (idx - lo)

    freq = sorted(((n_f, count) for n_f, count in selected.items()),
                  key=lambda item: (-item[1], item[0]))
    result = {
        "replicates": replicates,
        "seed": BOOT_SEED,
        "original_best_split": original_best,
        "original_best_mean": round(means[original_best], 2),
        "selection_frequency_top": [
            {"n_feeder": n_f, "count": count,
             "share": round(count / replicates, 4)}
            for n_f, count in freq[:8]
        ],
        "original_best_reselected_share": round(
            selected.get(original_best, 0) / replicates, 4),
        "selected_mean_distribution": {
            "p2_5": round(pct(sel_means, 0.025), 2),
            "p50": round(pct(sel_means, 0.5), 2),
            "p97_5": round(pct(sel_means, 0.975), 2),
        },
        "selection_adjusted_delta": {
            "p2_5": round(pct(sel_deltas, 0.025), 2),
            "p50": round(pct(sel_deltas, 0.5), 2),
            "p97_5": round(pct(sel_deltas, 0.975), 2),
        },
        "selection_adjusted_crossing": {
            "valid_replicates": valid_crossings,
            "valid_share": round(valid_crossings / replicates, 4),
            "p2_5": round(pct(crossings, 0.025), 3) if crossings else None,
            "p50": round(pct(crossings, 0.5), 3) if crossings else None,
            "p97_5": round(pct(crossings, 0.975), 3) if crossings else None,
        },
    }
    json.dump(result, open(f"{OUT}\\nested_selection.json", "w"), indent=1)
    print(json.dumps(result, indent=1), flush=True)


def cmd_band(args):
    os.makedirs(OUT, exist_ok=True)
    sweep = read_sweep_means()
    seeds = sorted({seed for (_, seed) in sweep})
    means = {n_f: statistics.fmean(
        sweep[(n_f, s)] for s in seeds) for n_f in range(1, 23)}
    min_mean = min(means.values())
    threshold = 1.05 * min_mean
    band = sorted(n_f for n_f, mean in means.items() if mean <= threshold)
    bus_curves = read_bus_curves()

    crossings = {}
    for n_f in band:
        multi = {s: sweep[(n_f, s)] for s in seeds}
        crossings[n_f] = crossing_from_curves(bus_curves, multi)
    endpoints = (band[0], band[-1])
    endpoint_cis = {}
    for n_f in endpoints:
        multi = {s: sweep[(n_f, s)] for s in seeds}
        endpoint_cis[n_f] = joint_crossing(bus_curves, multi)

    result = {
        "criterion": "mean makespan <= 1.05 x minimum split mean",
        "threshold_min": round(threshold, 2),
        "min_mean": round(min_mean, 2),
        "argmin_split": min(means, key=lambda n_f: (means[n_f], n_f)),
        "band_splits": band,
        "band_means": {str(n_f): round(means[n_f], 2) for n_f in band},
        "band_point_crossings": {str(k): v for k, v in crossings.items()},
        "band_crossing_range": [
            min(v for v in crossings.values() if v is not None),
            max(v for v in crossings.values() if v is not None),
        ],
        "endpoint_joint_intervals": {
            str(n_f): ci for n_f, ci in endpoint_cis.items()
        },
    }
    json.dump(result, open(f"{OUT}\\band_definition.json", "w"), indent=1)
    print(json.dumps(result, indent=1), flush=True)


def cmd_fullendpoints(args):
    os.makedirs(OUT, exist_ok=True)
    band_def = json.load(open(f"{OUT}\\band_definition.json"))
    endpoints = band_def["band_splits"][0], band_def["band_splits"][-1]
    t0 = time.perf_counter()
    inputs = load_pilot_inputs(
        region_path="data/regions/goseong_mobilization.yaml",
        cache_path="data/cache/goseong_nodelink_road.graphml",
        road_class_overrides_path="data/parameters/road_class_overrides.csv",
        reduce_graph=False,
    )
    full = inputs.graph
    print(f"full graph ready ({time.perf_counter()-t0:.0f}s): "
          f"{full.number_of_nodes()} nodes", flush=True)
    band = load_band(full)
    _, base = load_base()

    fields = ["n_feeder", "road_multiplier", "arrival_seed", "makespan",
              "completion_rate", "elapsed_s"]
    path = f"{OUT}\\fullendpoints_results.csv"
    done = resume_keys(path, ["n_feeder", "road_multiplier", "arrival_seed"])
    fh, writer = open_writer(path, fields)
    seeds = list(range(3101, 3131))
    for n_f in endpoints:
        for seed in seeds:
            key = (str(n_f), "1.0", str(seed))
            if key in done:
                continue
            t1 = time.perf_counter()
            out = run_one(full, band, base, policy_id="static_multimodal",
                          n_f=n_f, mult=1.0, seed=seed)
            writer.writerow({
                "n_feeder": n_f, "road_multiplier": 1.0,
                "arrival_seed": seed, "makespan": out.get("makespan"),
                "completion_rate": out.get("completion_rate"),
                "elapsed_s": round(time.perf_counter() - t1, 3),
            })
            fh.flush()
        print(f"full endpoint {n_f} done", flush=True)
    fh.close()

    rows = list(csv.DictReader(open(path, encoding="utf-8-sig", newline="")))
    multi_full = {n_f: {int(r["arrival_seed"]): float(r["makespan"])
                        for r in rows if int(r["n_feeder"]) == n_f}
                  for n_f in endpoints}
    bus_full = read_full_bus_curves()
    per_split = {}
    for n_f in endpoints:
        ci = joint_crossing(bus_full, multi_full[n_f])
        per_split[n_f] = ci
    summary = {
        "endpoints": list(endpoints),
        "endpoint_intervals_full_graph": {str(k): v for k, v in per_split.items()},
        "wall_s": round(time.perf_counter() - t0, 1),
    }
    json.dump(summary, open(f"{OUT}\\fullendpoints_summary.json", "w"), indent=1)
    print(json.dumps(summary, indent=1), flush=True)


def cmd_joint(args):
    os.makedirs(OUT, exist_ok=True)
    t0 = time.perf_counter()
    top10 = load_top10()
    band = load_band(top10)
    _, base = load_base()
    print(f"graph ready ({time.perf_counter()-t0:.0f}s)", flush=True)

    factors = {
        "rail": [102.6, 125.4],
        "headway": [20.0, 45.0],
        "transfer": [1.0, 15.0],
        "turnaround": [8.0, 12.0],
    }
    combos = [
        (r, h, tr, ta)
        for r in factors["rail"] for h in factors["headway"]
        for tr in factors["transfer"] for ta in factors["turnaround"]
    ]
    fields = ["family", "combo_id", "policy_id", "turnaround",
              "road_multiplier", "arrival_seed", "makespan",
              "completion_rate", "elapsed_s"]
    path = f"{OUT}\\joint_results.csv"
    done = resume_keys(path, ["combo_id", "policy_id", "road_multiplier",
                              "arrival_seed"])
    fh, writer = open_writer(path, fields)
    seeds = list(range(3101, 3131))

    def mutate_for(rail, headway, transfer, turnaround):
        def mutate(config):
            set_rail_link(config, travel=rail, headway=headway)
            config["multimodal"]["transfer_time_min"] = transfer
            set_turnaround(config, turnaround)
        return mutate

    for (rail, headway, transfer, turnaround) in combos:
        combo_id = f"r{rail}_h{headway}_t{transfer}_ta{turnaround}"
        mutate = mutate_for(rail, headway, transfer, turnaround)
        for seed in seeds:
            key = (combo_id, "static_multimodal", "1.0", str(seed))
            if key not in done:
                t1 = time.perf_counter()
                out = run_one(top10, band, base, policy_id="static_multimodal",
                              n_f=6, mult=1.0, seed=seed, mutate=mutate)
                writer.writerow({
                    "family": "joint", "combo_id": combo_id,
                    "policy_id": "static_multimodal",
                    "turnaround": turnaround, "road_multiplier": 1.0,
                    "arrival_seed": seed, "makespan": out.get("makespan"),
                    "completion_rate": out.get("completion_rate"),
                    "elapsed_s": round(time.perf_counter() - t1, 3),
                })
                fh.flush()
        print(f"combo {combo_id} done", flush=True)

    bus12_id = "bus_turnaround12"
    for mult in BE_GRID:
        for seed in seeds:
            key = (bus12_id, "bus_only", str(mult), str(seed))
            if key in done:
                continue
            t1 = time.perf_counter()
            out = run_one(top10, band, base, policy_id="bus_only", n_f=0,
                          mult=mult, seed=seed,
                          mutate=lambda c: set_turnaround(c, 12.0))
            writer.writerow({
                "family": "joint", "combo_id": bus12_id,
                "policy_id": "bus_only", "turnaround": 12.0,
                "road_multiplier": mult, "arrival_seed": seed,
                "makespan": out.get("makespan"),
                "completion_rate": out.get("completion_rate"),
                "elapsed_s": round(time.perf_counter() - t1, 3),
            })
            fh.flush()
        print(f"bus ta12 x{mult} done", flush=True)
    fh.close()

    rows = list(csv.DictReader(open(path, encoding="utf-8-sig", newline="")))
    bus8 = read_bus_curves()
    bus12 = {}
    for r in rows:
        if r["combo_id"] == bus12_id and float(r["completion_rate"] or 0) >= 1.0:
            bus12.setdefault(int(r["arrival_seed"]), {})[
                float(r["road_multiplier"])] = float(r["makespan"])

    combo_rows = {}
    for r in rows:
        if r["policy_id"] == "static_multimodal":
            combo_rows.setdefault(r["combo_id"], []).append(r)
    results = []
    for combo_id, cr in combo_rows.items():
        multi_by_seed = {int(r["arrival_seed"]): float(r["makespan"])
                         for r in cr if float(r["completion_rate"] or 0) >= 1.0}
        turnaround = float(cr[0]["turnaround"])
        curve = bus12 if turnaround == 12.0 else bus8
        cross = crossing_from_curves(curve, multi_by_seed)
        results.append({
            "combo_id": combo_id,
            "multi_mean": round(statistics.fmean(multi_by_seed.values()), 2),
            "turnaround": turnaround,
            "crossing": cross,
        })
    results.sort(key=lambda item: (item["crossing"] is None,
                                   item["crossing"] if item["crossing"]
                                   else 0))
    valid = [r["crossing"] for r in results if r["crossing"] is not None]
    summary = {
        "combos": len(results),
        "crossing_min": round(min(valid), 3),
        "crossing_max": round(max(valid), 3),
        "oat_range_reference": [1.077, 1.259],
        "per_combo": results,
        "wall_s": round(time.perf_counter() - t0, 1),
    }
    json.dump(summary, open(f"{OUT}\\joint_summary.json", "w"), indent=1)
    print(json.dumps(summary, indent=1)[:1500], flush=True)


def cmd_ablation(args):
    os.makedirs(OUT, exist_ok=True)
    t0 = time.perf_counter()
    top10 = load_top10()
    band = load_band(top10)
    _, base = load_base()
    print(f"graph ready ({time.perf_counter()-t0:.0f}s)", flush=True)

    allocations = [(12, 11), (10, 13), (8, 15), (6, 17), (5, 18)]
    rail_states = ["available", "unavailable"]
    policies = ["static_multimodal", "precheck_switch"]
    fields = ["policy_id", "n_feeder", "n_lastmile", "rail_status",
              "arrival_seed", "makespan", "completion_rate", "elapsed_s"]
    path = f"{OUT}\\ablation_results.csv"
    done = resume_keys(path, ["policy_id", "n_feeder", "rail_status",
                              "arrival_seed"])
    fh, writer = open_writer(path, fields)
    seeds = list(range(3101, 3131))
    for policy_id in policies:
        for rail_status in rail_states:
            for (n_f, n_l) in allocations:
                for seed in seeds:
                    key = (policy_id, str(n_f), rail_status, str(seed))
                    if key in done:
                        continue
                    # Official precheck semantics (revision_execution
                    # ._execution_branch): rail unavailable -> execute the
                    # bus_only scenario on the base config (23 direct buses);
                    # rail available -> static multimodal with the split.
                    exec_policy = policy_id
                    exec_n_f = n_f
                    if (policy_id == "precheck_switch"
                            and rail_status == "unavailable"):
                        exec_policy = "bus_only"
                        exec_n_f = 0
                    t1 = time.perf_counter()
                    out = run_one(top10, band, base, policy_id=exec_policy,
                                  n_f=exec_n_f, mult=1.0, seed=seed,
                                  rail_status=rail_status)
                    writer.writerow({
                        "policy_id": policy_id, "n_feeder": n_f,
                        "n_lastmile": n_l, "rail_status": rail_status,
                        "arrival_seed": seed,
                        "makespan": out.get("makespan"),
                        "completion_rate": out.get("completion_rate"),
                        "elapsed_s": round(time.perf_counter() - t1, 3),
                    })
                    fh.flush()
                print(f"ablation {policy_id} {rail_status} {n_f}/{n_l} done",
                      flush=True)
    fh.close()

    rows = list(csv.DictReader(open(path, encoding="utf-8-sig", newline="")))
    cells = {}
    for r in rows:
        key = (r["policy_id"], int(r["n_feeder"]), r["rail_status"])
        cells.setdefault(key, []).append(r)
    table = []
    for (policy_id, n_f, rail_status), group in sorted(cells.items()):
        comps = [float(r["completion_rate"]) for r in group]
        makes = [float(r["makespan"]) for r in group
                 if r["makespan"] not in ("", None)
                 and float(r["completion_rate"] or 0) >= 1.0]
        table.append({
            "policy_id": policy_id, "n_feeder": n_f, "n_lastmile": 23 - n_f,
            "rail_status": rail_status,
            "completion_rate": round(statistics.fmean(comps), 4),
            "mean_makespan": round(statistics.fmean(makes), 2) if makes else None,
        })
    summary = {"cells": table,
               "wall_s": round(time.perf_counter() - t0, 1)}
    json.dump(summary, open(f"{OUT}\\ablation_summary.json", "w"), indent=1)
    print(json.dumps(summary, indent=1), flush=True)


def cmd_repcounts(args):
    sweep = read_sweep_means()
    seeds = sorted({seed for (_, seed) in sweep})
    bus_top10 = read_bus_curves()
    bus_full = read_full_bus_curves()
    results = {}

    rows_1211 = []
    for path in (BE, BE_FINE):
        with open(path, encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                if (row["policy_id"] == "static_multimodal"
                        and row["resource_frame"] == "matched_road_fleet"
                        and int(row["feeder_shuttle_count"]) == 12):
                    rows_1211.append(row)
    outcomes = {}
    for row in rows_1211:
        seed = int(row["arrival_seed"])
        outcomes.setdefault(seed, {})[float(row["road_multiplier"])] = float(
            row["makespan"])
    bus_by_seed = {}
    for seed in outcomes:
        if seed in bus_top10:
            bus_by_seed[seed] = bus_top10[seed]
    merged = {}
    for seed, multi_curve in outcomes.items():
        if seed not in bus_by_seed:
            continue
        for m, multi_val in multi_curve.items():
            if m in bus_by_seed[seed]:
                merged.setdefault(seed, {})[m] = (
                    bus_by_seed[seed][m] - multi_val)
    interval = joint_seed_zero_crossing_bootstrap(
        merged, confidence=0.95, replicates=10_000, seed=BOOT_SEED)
    results["top10_12_11_campaign"] = {
        "estimate": interval.estimate, "lower": interval.lower,
        "upper": interval.upper,
        "complete_seed_count": interval.complete_seed_count,
        "excluded_seeds": list(interval.excluded_seeds),
        "successful_replicates": interval.successful_replicates,
        "replicates": interval.replicates,
    }

    for n_f in (6,):
        multi = {s: sweep[(n_f, s)] for s in seeds}
        results[f"top10_{n_f}_17_flat"] = joint_crossing(bus_top10, multi)

    fg_rows = list(csv.DictReader(open(FG, encoding="utf-8-sig", newline="")))
    for n_f in (6, 12):
        per_seed = {}
        for r in fg_rows:
            if (r["policy_id"] == "static_multimodal"
                    and r["resource_frame"] == "matched_road_fleet"
                    and int(r["n_feeder"]) == n_f):
                per_seed.setdefault(int(r["arrival_seed"]), {})[
                    float(r["road_multiplier"])] = float(r["makespan"])
        multi_full = {
            seed: curve[min(curve)] for seed, curve in per_seed.items()
        }
        results[f"full_{n_f}_flat"] = joint_crossing(bus_full, multi_full)

    ep_path = f"{OUT}\\fullendpoints_results.csv"
    if os.path.exists(ep_path):
        band_def = json.load(open(f"{OUT}\\band_definition.json"))
        endpoints = band_def["band_splits"]
        ep_rows = list(csv.DictReader(open(ep_path, encoding="utf-8-sig",
                                           newline="")))
        for n_f in endpoints:
            multi_full = {int(r["arrival_seed"]): float(r["makespan"])
                          for r in ep_rows if int(r["n_feeder"]) == n_f}
            results[f"full_endpoint_{n_f}_flat"] = joint_crossing(
                bus_full, multi_full)

    json.dump(results, open(f"{OUT}\\replicate_counts.json", "w"), indent=1)
    print(json.dumps(results, indent=1), flush=True)


COMMANDS = {
    "holdout": cmd_holdout,
    "nested": cmd_nested,
    "band": cmd_band,
    "fullendpoints": cmd_fullendpoints,
    "joint": cmd_joint,
    "ablation": cmd_ablation,
    "repcounts": cmd_repcounts,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=sorted(COMMANDS))
    args = parser.parse_args()
    COMMANDS[args.command](args)


if __name__ == "__main__":
    main()
