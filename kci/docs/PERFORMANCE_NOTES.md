# Performance notes — experimental runners

## v0.7 hot-spot profile (single paired scenario, 1000 personnel, OSM corridor)

```
Total per scenario: ~25 s (50 s per paired bus+multi cell-rep)
- _edge_weight_at_time           94 %   (6.1 M calls / 3 scenarios)
- current_volume                 30 %   (5.97 M calls)
- require_non_negative/finite    14 %   (12 M+ calls — runtime validation guards)
- _shortest_path_at_time         97 %   cumulative
```

The dominant cost is BPR edge-weight recomputation inside repeated NetworkX
shortest-path calls, plus per-traversal `__post_init__` validation on
`EdgeTraversal` / `EdgeDisruption` dataclasses.

## Optimizations shipped in v0.7

### `src/experiment/parallel_runner.py`

A new module with three public entry points:

- `run_phase1_parallel(config, *, region_path, cache_path, origin, output_path, s_levels=None, p_levels=None, R=None, n_workers=None)`
- `run_phase2_singlemode_parallel(config, *, region_path, cache_path, origin, output_path, fleet_levels, dispatch_levels, p_levels, R, s=1.2, n_workers=None)`
- `run_phase3_parallel(config, *, region_path, cache_path, origin, output_path, n_workers=None)`

Each does:

1. **`multiprocessing.Pool`** sized to `cpu_count()` (or `--workers N`). The worker
   initializer builds the OSM corridor graph **once per process**, amortizing the
   ~14 s graph build over many cells.
2. **Per-cell append**: completed cells are written to the output CSV in append
   mode immediately. A kill or sleep loses at most the in-flight cells.
3. **Resume**: re-running with the same `--output` reads the existing CSV, sees
   which `cell_id` values are present, and skips them. Allows
   crash-recovery without losing prior compute.

Launchers (all support `--workers N`, all default-write to the v0.7 output paths):

- `scripts/run_v07_phase1_fast.py`
- `scripts/run_v07_phase2_singlemode_fast.py`
- `scripts/run_v07_phase3_fast.py`

## Expected speedups vs serial v0.7 runners

| Phase | Cells | R | Serial wall-clock | Parallel (N=8) | Speedup |
|---|---|---|---|---|---|
| 1a | 8 | 30 | ~70 min | ~12 min | ~6× |
| 1b (per origin) | 4 | 20 | ~22 min | ~5 min | ~4× |
| 2 | 45 | 20 | ~3.75 h | ~30 min | ~7.5× |
| 3 | 81 | 15 | ~5 h | ~40 min | ~7.6× |

Parallel times assume 8 cores; `--workers` clamps to `min(cpu_count, n_cells)`.
On a 4-core machine, halve N and ~halve the speedup.

## What is NOT in v0.7

The biggest remaining win is **eliminating runtime validation in hot loops**
(`require_non_negative`, `require_finite`, `EdgeTraversal.__post_init__`).
Profile shows ~28 % of per-scenario time goes to these guards. Removing them
would require:

- A module-level "trusted" flag (e.g. `os.environ["SIM_FAST_PATH"] = "1"`) that
  short-circuits validation in production runs, while leaving full validation
  active in tests.
- Audit of every call site that mutates these dataclasses to ensure inputs are
  pre-validated.

That change is intentionally deferred — it alters runtime contract and is risky
for paper-grade reproducibility. Plan for v0.8.

## Recovery cheat sheet

If a long run dies (machine sleep, power, etc.):

```bash
# Phase 2 — resumes from existing CSV automatically
python -u scripts/run_v07_phase2_singlemode_fast.py \
  --output results/phase2_singlemode.csv

# Phase 3
python -u scripts/run_v07_phase3_fast.py \
  --output results/phase3_lever_sweep.csv

# Phase 1b origin C, only the p_fail=1.0 and 1.5 cells (e.g., if first run lost those)
python -u scripts/run_v07_phase1_fast.py \
  --origin C --R 20 \
  --p-levels 1.0,1.5 \
  --s-levels 1.2 \
  --output results/phase1b_origin_C.csv
```

A successful append leaves a clean CSV with one header row at the top. Mixed
headers in the middle indicate a write-collision (two processes writing the
same file) — never run two parallel launchers against the same output path.
