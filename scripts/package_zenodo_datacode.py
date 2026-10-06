"""Package the data/code-only Zenodo archival bundle (v3+).

Allowlist-based so deposits are reproducible: engine + run/analysis scripts +
tests + input tables + result/analysis CSVs and manifests.  Excludes the
manuscript/figures/docs/report tracks, network-cache GraphML files,
checkpoints, logs, and caches.
"""

import hashlib
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_NAME = "transport-system-sim_zenodo_v3_data_code.zip"

RESULT_FILES = [
    # Original paper-revision analysis products.
    "results/paper_revision_top10_corridor_v4_20260721/analysis/full/paired_summary.csv",
    "results/paper_revision_top10_corridor_v4_20260721/analysis/full/break_even.csv",
    "results/paper_revision_top10_corridor_v4_20260721/analysis/full/demand_fleet.csv",
    "results/paper_revision_top10_corridor_v4_20260721/analysis/full/road_rail_map.csv",
    "results/paper_revision_top10_corridor_v4_20260721/analysis/full/adaptive_policies.csv",
    "results/paper_revision_top10_corridor_v4_20260721/analysis/full/morris_effects.csv",
    "results/paper_revision_top10_corridor_v4_20260721/analysis/full/replicate_convergence.csv",
    "results/paper_revision_top10_corridor_v4_20260721/analysis/full/graph_scope_stability.csv",
    "results/paper_revision_top10_corridor_v4_20260721/analysis/full/graph_scope_route_metrics.csv",
    "results/paper_revision_top10_corridor_v4_20260721/analysis/full/corridor_target_scope_metrics.csv",
    "results/paper_revision_top10_corridor_v4_20260721/analysis/full/random_threat_hierarchical.csv",
    "results/paper_revision_top10_corridor_v4_20260721/analysis/full/random_threat_crossed.csv",
    "results/paper_revision_top10_corridor_v4_20260721/analysis/full/analysis_manifest.json",
    # Allocation surface.
    "results/allocation_sweep_v1/sweep_results.csv",
    "results/allocation_sweep_v1/allocation_surface.csv",
    "results/allocation_sweep_v1/manifest.json",
    # Full-graph validation.
    "results/fullgraph_breakeven_v1/fullgraph_results.csv",
    "results/fullgraph_breakeven_v1/fullgraph_summary.csv",
    "results/fullgraph_breakeven_v1/manifest.json",
    # Sensitivity.
    "results/sensitivity_v1/sensitivity_results.csv",
    "results/sensitivity_v1/sensitivity_crossings.csv",
    "results/sensitivity_v1/manifest.json",
    # Second corridor.
    "results/corridor2_yangyang_v1/corridor2_results.csv",
    "results/corridor2_yangyang_v1/manifest.json",
    # Summary tables.
    "results/fig7_data.csv",
    "results/compute_frontier.csv",
]

TOP_FILES = ["requirements.txt", "README.md"]


def collect():
    paths = list(TOP_FILES)
    for tree in ("src", "scripts", "tests"):
        for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, tree)):
            dirnames[:] = [d for d in dirnames if d != "__pycache__"]
            for name in sorted(filenames):
                if name.endswith(".py"):
                    paths.append(os.path.relpath(os.path.join(dirpath, name), ROOT))
    for tree in ("data/regions", "data/scenarios", "data/parameters",
                 "data/manifests", "data/validation"):
        full = os.path.join(ROOT, tree)
        if not os.path.isdir(full):
            continue
        for dirpath, _, filenames in os.walk(full):
            for name in sorted(filenames):
                if name.endswith((".csv", ".yaml", ".yml", ".json", ".md")):
                    paths.append(os.path.relpath(os.path.join(dirpath, name), ROOT))
    paths.extend(RESULT_FILES)
    return sorted(set(paths))


def main():
    out_path = os.path.join(ROOT, OUT_NAME)
    entries = []
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for rel in collect():
            full = os.path.join(ROOT, rel)
            if not os.path.isfile(full):
                print(f"SKIP missing: {rel}")
                continue
            zf.write(full, rel)
            entries.append(rel)
    digest = hashlib.sha256()
    with open(out_path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    size = os.path.getsize(out_path)
    manifest = {
        "bundle": OUT_NAME,
        "sha256": digest.hexdigest(),
        "size_bytes": size,
        "file_count": len(entries),
        "files": entries,
    }
    with open(os.path.join(ROOT, "zenodo_v3_contents.json"), "w", encoding="utf-8") as fh:
        import json
        json.dump(manifest, fh, indent=1)
    print(f"files={len(entries)} size={size} sha256={digest.hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
