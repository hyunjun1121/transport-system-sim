"""Extract claim-disciplined findings from the Goseong 12,420-row pilot results.

Outputs a JSON summary consumed by report prose authoring. Descriptive only.
"""
from __future__ import annotations

import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "realworld_pilot" / "pilot_full_results.csv"
OUT = ROOT / "results" / "realworld_pilot" / "analysis_goseong_full_20260705" / "goseong_findings.json"


def f(x):
    try:
        v = float(x)
        return v if v == v else None  # nan check
    except (TypeError, ValueError):
        return None


def main() -> int:
    rows = []
    with open(RESULTS, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            rows.append(r)

    # group by (scenario_id, policy_id, mode)
    groups: dict[tuple, list] = defaultdict(list)
    for r in rows:
        key = (r["scenario_id"], r["policy_id"], r["mode"])
        groups[key].append(r)

    def agg(rs, col):
        vals = [f(r[col]) for r in rs if f(r[col]) is not None]
        if not vals:
            return None
        return statistics.mean(vals)

    def summarize(key):
        rs = groups[key]
        return {
            "n": len(rs),
            "makespan_mean": agg(rs, "makespan"),
            "penalized_makespan_mean": agg(rs, "penalized_makespan"),
            "completion_rate_mean": agg(rs, "completion_rate"),
            "censored_count_mean": agg(rs, "censored_count"),
        }

    # scenario inventory
    scenarios = sorted({r["scenario_id"] for r in rows})
    policies = sorted({r["policy_id"] for r in rows})
    modes = sorted({r["mode"] for r in rows})
    families = sorted({r["scenario_family"] for r in rows})

    # baseline bus vs multimodal, per scenario
    baseline_pairs = {}
    for sc in scenarios:
        b_key = (sc, "bus_only", "bus_only")
        m_key = (sc, "baseline_multimodal", "multimodal")
        if b_key in groups and m_key in groups:
            b = summarize(b_key)
            m = summarize(m_key)
            baseline_pairs[sc] = {"bus_only": b, "multimodal": m}

    # no_disruption baseline
    no_disrupt = baseline_pairs.get("no_disruption", {})

    # scenario families present
    family_scenarios = defaultdict(list)
    for r in rows:
        if r["scenario_id"] not in family_scenarios[r["scenario_family"]]:
            family_scenarios[r["scenario_family"]].append(r["scenario_id"])

    out = {
        "row_count": len(rows),
        "scenario_count": len(scenarios),
        "policy_count": len(policies),
        "seed_count_per_cell": 30,
        "modes": modes,
        "scenario_families": {
            fam: sorted(family_scenarios[fam]) for fam in families
        },
        "no_disruption_baseline": no_disrupt,
        "baseline_bus_vs_multimodal_by_scenario": baseline_pairs,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)

    # print a compact human-readable digest
    print(f"rows={len(rows)} scenarios={len(scenarios)} policies={len(policies)}")
    print(f"modes={modes}")
    print(f"families={list(family_scenarios)}")
    print("\n=== no_disruption baseline ===")
    print(json.dumps(no_disrupt, indent=2, ensure_ascii=False))
    print("\n=== bus vs multimodal (baseline policies), makespan mean by scenario ===")
    print(f"{'scenario':45s} {'bus_ms':>8s} {'multi_ms':>9s} {'bus_CR':>7s} {'multi_CR':>8s}")
    for sc in sorted(baseline_pairs):
        b = baseline_pairs[sc]["bus_only"]
        m = baseline_pairs[sc]["multimodal"]
        bm = b["makespan_mean"]; mm = m["makespan_mean"]
        bc = b["completion_rate_mean"]; mc = m["completion_rate_mean"]
        bm_s = f"{bm:.1f}" if bm is not None else "inf"
        mm_s = f"{mm:.1f}" if mm is not None else "inf"
        bc_s = f"{bc:.3f}" if bc is not None else "-"
        mc_s = f"{mc:.3f}" if mc is not None else "-"
        print(f"{sc:45s} {bm_s:>8s} {mm_s:>9s} {bc_s:>7s} {mc_s:>8s}")
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
