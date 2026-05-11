# KCI Implementation Plan — From Resolved Decisions to Submitted Manuscript

**Document role:** HOW. Step-by-step implementation plan that executes the research described in `kci/research_plan.md` using the file decisions in `kci/repo_assets_audit.md`, the locked decisions in `kci/agents.md` §7, and the format spec in `kci/submission_format.md`.
**Last updated:** 2026-05-11 (v0.2 — added parallelization, sub-agent allocation, and critical-path analysis).
**Status:** Ready to execute. In-phase decision points are flagged with `🟡 IN-PHASE DECISION`.

---

## 1. Read-first

| If you're asking… | Read |
|---|---|
| Why this study? | `research_plan.md` §1–§3 |
| What's in/out of scope? | `research_plan.md` §4 |
| What is the research design? | `research_plan.md` §6–§7 |
| What's the framing rule (military, virtual corridor, IE)? | `agents.md` §2, §6 |
| What's already locked? | `agents.md` §7 |
| Which upstream files do we reuse? | `repo_assets_audit.md` |
| What format does KCI demand? | `submission_format.md` |
| **What do I run, in what order, and with what concurrency?** | **This document.** |

---

## 2. Execution model — parallelization, sub-agents, critical path

> This section is the optimizer's overlay on the phase plan below. Read it before starting work; it changes which tasks can be batched, which need a sub-agent, and which must wait.

### 2.1 Critical path (longest dependency chain)

```
[Bootstrap imports]
   → [OSM extract] → [graph build] → [config wired]
   → [smoke A passes]
   → [LONGEST Phase-4 run (probably Phase 1 paired CRN, ~2–6h)]
   → [analysis + figure assembly]
   → [clone_form manuscript build]
   → [USER-SIDE 보안성 검토 발급]   ← real bottleneck for submission
   → [JAMS upload]
```

**The single longest segment is Phase 4** — the longest of {Phase 1 paired CRN, Phase 2 policy sweep, Morris sensitivity, origin-robustness sub-run}. This is the wall-clock bottleneck **regardless of parallelization elsewhere**, so the highest-leverage optimization is "launch all four Phase-4 runs concurrently in the background." Everything else (file ops, manuscript drafting) is small relative to this.

The most likely real-world bottleneck is **outside this plan**: the user-side **보안성 검토 발급** at KMA can take days to weeks. Start that process at Phase 1 — do not wait until Phase 7.

### 2.2 Parallelization rules per phase

| Phase | Parallel-within opportunities | Speedup vs serial | How to parallelize |
|---|---|---|---|
| 0 Bootstrap | File copies + adapts (T0.3 / T0.4 / T0.8 / T0.9 / T0.10 / T0.12) | ~3–5× | Multiple `Edit` and `Bash cp` calls in one message |
| 1 Network | After graph build: reachability probe + accessibility-loss + manifest write | ~3× on the post-build phase | Parallel `Bash` calls in one message |
| 2 Code adapt | Almost everything (T2.1–T2.5, T2.7, T2.8) | ~5× | Parallel `Edit` calls in one message |
| 3 Smoke | T3.1 + T3.2 + T3.3 in parallel; then 4 origin smokes (B/C/D) in parallel | ~3× | Parallel `Bash` calls (some `run_in_background=true`) |
| **4 Full runs** | **All 4 experiment families run concurrently** | **~2× (5–12 h → 3–6 h)** | **`Bash run_in_background=true` × 4 in one message; harness notifies on completion** |
| 5 Analysis + figures | 5 figures + 5 tables generated in parallel | ~3–5× | One Opus sub-agent per figure (5 parallel) + one for tables |
| **6 Manuscript** | **6 manuscript sections drafted by 6 parallel sub-agents** | **~3–5× on drafting** | **One Opus sub-agent per section (서론 / 선행연구 / 연구방법 / 결과 / 논의 / Abstract+References)** |
| 7 Submission | None (sequential JAMS form) | 1× | — |

### 2.3 Sub-agent allocation policy

> **Sub-agents have overhead** (cold context, cost). Use them only when the work pays for that overhead.

**USE sub-agents (general-purpose Opus) when:**
- The task requires deep, focused context that would bloat the parent window (e.g., authoring a full manuscript section).
- Multiple genuinely independent creative / analytical streams can run in parallel (e.g., 6 manuscript sections, 5 figures).
- The output quality benefits from specialized prompting and isolated reasoning.

**DO NOT use sub-agents for:**
- Simple file copies or single-file edits — use parallel `Bash` / `Edit` tool calls in a single message.
- Linear shell commands — use `Bash` directly.
- Reading or grepping a few files — use `Read` / `Grep` directly.

**Sub-agent allocation table:**

| Phase | Sub-agents? | If yes, how many | What each does |
|---|---|---|---|
| 0–4 | No | — | Parallel tool calls + `run_in_background` are sufficient |
| 5 | **Yes** | **6** | (a) figure 2 corridor map, (b) figure 3 break-even heatmap, (c) figure 4 miss-rate, (d) figure 5 origin robustness, (e) all 5 tables, (f) figure-table cross-reference audit |
| 6 | **Yes** | **6** | One per manuscript section: (a) §1 서론, (b) §2 선행연구, (c) §3 연구방법, (d) §4 결과 및 분석, (e) §5 결론, (f) English abstract + references in APA |
| 7 | No | — | User-side checklist |

### 2.4 Background execution (Phase 4)

Phase 4 has the largest single time block. **Launch all four experiment families in one message using `Bash run_in_background=true` so the harness notifies on completion** instead of blocking. The four families are independent (different output CSVs, no shared mutable state), so concurrent execution is safe as long as Python processes don't exceed available cores.

If runtime budget is tight, **priority order** (drop from the bottom if necessary):

1. T4.1 Phase 1 paired CRN — produces the manuscript's main result. **Never drop.**
2. T4.4 Origin-robustness B/C/D — needed for the origin-robustness figure 5; second priority.
3. T4.3 Morris sensitivity — methodological pillar; can be reduced to 100 trajectories instead of 200.
4. T4.2 Phase 2 (policy sweep) — supports a smaller story; can be reduced or deferred.

### 2.5 Synchronization points (mandatory waits)

Even with maximum parallelism, the following are hard sync points:

| After | Before | Why |
|---|---|---|
| Phase 1 graph build (T1.4) | Phase 2 config wiring (T2.6) | `config.yaml` needs the final origin/destination node IDs |
| Phase 3 smoke pass | Phase 4 launch | Don't burn 5–12h on a broken pipeline |
| All Phase 4 runs complete | Phase 5 analysis | Paired-delta tables need both modes' rows |
| Phase 5 figures + tables ready | Phase 6 manuscript build | Manuscript references figures by file path |
| Phase 6 manuscript draft | Phase 7 anonymization | Must strip author info from the final `.hwp` |

### 2.6 What runs in parallel with the user-side critical path

The 보안성 검토 process is owned by the user, runs out-of-band, and likely takes the longest real-world time. **All of Phase 0 through Phase 6 can run in parallel with that process.** The plan triggers the security-review request at Phase 1 (§4.0), not Phase 7.

---

## 3. Phase overview

| Phase | Goal | Output | Wall-clock (parallel) | Blocks next? |
|---|---|---|---|---|
| 0 | Bootstrap `kci/` directory and slim package skeleton | Working `kci/` tree, simulator imports succeed | ~30 min | YES |
| 1 | Build the Songpa↔양주 major-arterial corridor network + **trigger 보안성 검토 request** | corridor GraphML + region YAML | ~1 h (+ user-side started) | YES |
| 2 | Adapt simulator code, config, scenarios | `kci/main.py`, `config.yaml`, scenario CSVs ready | ~30 min | YES |
| 3 | Smoke runs | One paired smoke (~minutes), end-to-end validates | ~15 min | YES |
| **4** | **Full experiment runs (4 concurrent)** | Phase 1 + Phase 2 + Morris + origin-robustness CSVs | **~3–6 h** | YES |
| 5 | Analysis, CIs, figures (6 parallel sub-agents) | 5 figures + 5 tables in `manuscript/` | ~30 min wall-clock | YES |
| 6 | Manuscript draft via clone_form (6 parallel sub-agents) | `manuscript.hwp` in KCI 편집양식 | ~1–2 h drafting + manual figure paste | YES |
| 7 | Submission package + JAMS upload | Submitted (depends on 보안성 검토 ready) | User-side; days–weeks | END |

> **Total plan-side wall-clock estimate: ~7–11 hours, dominated by Phase 4. Total submit-ready estimate: dominated by user-side 보안성 검토 turnaround.**

---

## 4. Phase 0 — Bootstrap

### 4.1 Prerequisites

- `kci/agents.md`, `research_plan.md`, `repo_assets_audit.md`, `submission_format.md` present (already done).
- Python 3.11+, `git`, network access for `osmnx`.

### 4.2 Tasks (with parallelization)

```
T0.1 [seq, must run first]   mkdir kci/ subdirectories per repo_assets_audit.md §4
T0.2 [seq, after T0.1]        touch __init__.py files in src/, src/experiment/,
                              src/visualize/, src/realworld/, tests/

[‖ PARALLEL BATCH after T0.2 — issue all of these in a single message
 with multiple Bash/Edit tool calls:]

T0.3  COPY simulator-core (network.py, scenario.py, dispatch.py, disruptions.py,
      fleet.py, metrics.py, models.py, policies.py, rail.py, sim_types.py,
      traffic.py, transfers.py, experiment/*, visualize/*) from upstream src/
      into kci/src/
T0.4  COPY realworld subset (osm_network.py, zones.py, regions.py, types.py,
      validation.py) from upstream src/realworld/ into kci/src/realworld/
T0.6  ADAPT realworld/adapter.py — change ROUTEABLE_HIGHWAY_CLASSES to:
        {"motorway", "motorway_link", "trunk", "trunk_link",
         "primary", "primary_link", "secondary", "secondary_link"}
T0.8  COPY simulator-core tests + realworld adapter/scenario/sensitivity/
      e2e/reproducibility tests per audit §2 into kci/tests/
T0.9  COPY 국방.md and 전시_예비군_수송체계_시뮬레이션_개념도.png into
      kci/manuscript/figures/
T0.10 ADAPT requirements.txt — add osmnx, drop python-docx
T0.12 Write kci/README.md (light, points to research_plan.md / agents.md /
      submission_format.md / plan.md)

[seq, depends on T0.4 (adapter et al. exist before init imports them):]

T0.5  ADAPT realworld/__init__.py — slim init that re-exports ONLY:
        from .types import RegionSpec, ZoneSpec, RailPointSpec
        from .regions import load_region
        from .zones import nearest_node, add_connectors
        from .osm_network import extract_bbox_graph, save_graphml, load_graphml, normalize
        from .attributes import HIGHWAY_DEFAULTS
        from .adapter import build_simulator_graph
        from .validation import assert_graph_ready
        from .accessibility import accessibility_loss
        from .disruption_scenarios import load_scenarios
        from .sensitivity import morris_problem, run_morris

T0.7  ADAPT realworld/sensitivity.py — strip imports of pilot_experiments /
      policy_alternatives; rewrite run_morris() to call src.scenario.run_scenario()
      directly with KCI configs

[seq, depends on T0.3 + T0.4:]

T0.11 Write kci/main.py with PROJECT_ROOT pointing at kci/, sys.path.insert,
      preserve --phase 1 / --phase 2 / --quick CLI shape

T0.13 [VALIDATION GATE — sequential, after T0.5/T0.7/T0.11]
```

### 4.3 Validation gate (T0.13)

```bash
cd kci
python -c "import sys; sys.path.insert(0, '.'); from src import scenario, network, metrics; from src.realworld import adapter, osm_network; print('imports ok')"
pytest tests/test_models.py tests/test_dispatch.py tests/test_metrics.py -q
```

Expected: imports succeed, three smoke tests pass.

### 4.4 Sub-agents in this phase

**None.** All work is mechanical file-ops and small ADAPTs; parallel `Bash` + `Edit` calls in one message are faster and cheaper than spawning sub-agents.

### 4.5 Rollback

If imports fail (most likely T0.5 missing a needed re-export), add the missing symbol. **Do not** copy upstream `__init__.py` — it eagerly loads the entire deferred-acceptance scaffold.

---

## 5. Phase 1 — Network construction

### 5.1 Prerequisites

- Phase 0 complete.
- OSMnx network access available.

### 5.2 Tasks (with parallelization)

```
T1.0 [‖ KICK OFF in parallel with T1.1 — USER-SIDE, no Claude action]
     User initiates 보안성 검토 request at KMA institutional process.
     This runs out-of-band for days/weeks. Do not block plan execution on it.

T1.1 [seq]   Write data/regions/songpa_yangju_corridor.yaml (full structure
             below in §5.2.1)

T1.2 [seq, network-bound]  Run OSMnx bbox extraction (single-threaded,
             rate-limited; cannot parallelize within this task):
   python -c "
   import sys; sys.path.insert(0, '.')
   from src.realworld.osm_network import extract_bbox_graph, save_graphml
   g = extract_bbox_graph(north=37.78, south=37.46, east=127.20, west=126.85)
   save_graphml(g, 'data/cache/songpa_yangju_corridor.graphml')
   print('nodes', g.number_of_nodes(), 'edges', g.number_of_edges())
   "

T1.3 [seq, depends on T1.2]  🟡 IN-PHASE DECISION: final bbox.
     If extraction <5,000 nodes: widen +0.05° in the limiting axis.
     If >30,000 nodes: trim away dead corners.
     Target: 5,000–20,000 pre-filter (post-arterial-filter ~500–2,000).

T1.4 [seq, depends on T1.3]  Build simulator-compatible graph:
   python -c "
   import sys; sys.path.insert(0, '.')
   from src.realworld import adapter, regions, validation
   region = regions.load_region('data/regions/songpa_yangju_corridor.yaml')
   g = adapter.build_simulator_graph(region,
       cache_path='data/cache/songpa_yangju_corridor.graphml')
   validation.assert_graph_ready(g, region)
   print('built sim graph:', g.number_of_nodes(), 'nodes')
   "

[‖ PARALLEL BATCH after T1.4 — issue these three in one message:]

T1.5  Reachability probe — confirm A→T, B→T, C→T, D→T and A→S→R→T return
      finite shortest-path distances. If any pair unreachable, add explicit
      connector edges via zones.add_connectors() or widen bbox.
T1.6  Accessibility-loss diagnostic:
        python scripts/run_accessibility_loss_analysis.py \
          --region data/regions/songpa_yangju_corridor.yaml \
          --cache  data/cache/songpa_yangju_corridor.graphml \
          --output data/validation/accessibility_loss.csv
      Inspect: confirm 올림픽대로 / 강변북로 / 외곽순환 each show single-edge-
      removal impact (expected single-points-of-failure on the corridor).
T1.7  Write data/cache/songpa_yangju_corridor_manifest.json with extraction
      parameters, OSM snapshot hash, node/edge counts pre and post filter,
      timestamp.

T1.8 [VALIDATION GATE — depends on T1.5 + T1.6 + T1.7]
```

#### 5.2.1 Region YAML structure

```yaml
region_id: songpa_yangju_kci
name: Songpa-gu to 72사단 부곡리 KCI Corridor
boundary:
  type: bbox
  north: 37.78    # tighten after T1.3 sanity check
  south: 37.46
  east:  127.20
  west:  126.85
assembly_zones:
  - id: A   # 송파구청 일자리센터 앞
    name: Songpa-gu Office Job Center
    lat: 37.5147
    lon: 127.1057
    metadata: {coordinate_class: public, role: assembly_primary,
               source: "Hankyung 2024-02-29 + 송파구 조례 2023-09-14"}
  - id: B   # 삼전동 구민회관 앞
    name: Samjeon-dong Community Hall
    lat: 37.5036
    lon: 127.0857
    metadata: {coordinate_class: public, role: assembly_alt,
               source: "Hankyung 2024-02-29"}
  - id: C   # 장지역 4번 출구 앞
    name: Jangji Station Exit 4
    lat: 37.4784
    lon: 127.1262
    metadata: {coordinate_class: public, role: assembly_alt,
               source: "Hankyung 2024-02-29"}
  - id: D   # 잠실종합운동장
    name: Jamsil Sports Complex (assembly variant — unverified source)
    lat: 37.5159
    lon: 127.0727
    metadata: {coordinate_class: public, role: assembly_unverified,
               source: "user-supplied, no public 동원수송 source confirmed"}
destination_zones:
  - id: T   # 72사단 부곡리 동원훈련장
    name: 72사단 부곡리 동원훈련장
    lat: 37.7400   # to be refined to 부곡리 산 6-17 centroid in extraction
    lon: 126.9500
    metadata: {coordinate_class: public, role: mobilization_destination,
               source: "병무청 찾아가는길 (mma.go.kr/contents.do?mc=mma0002106)",
               address: "경기 양주 장흥 부곡리 산 6-17"}
rail:
  access:  {id: S, name: rail-access-stub, lat: ?, lon: ?}    # finalize after T1.4
  egress:  {id: R, name: rail-egress-stub, lat: ?, lon: ?}
  travel_time_min: 60     # placeholder; documented assumption
  headway_min:    30
  capacity_pax_per_train: 500
  metadata:
    source_class: documented_assumption
    operational_claim: abstract_long_distance_proxy_no_real_timetable
metadata:
  kci_status: corridor_for_kci_submission
  data_sensitivity: public_open_data_only
```

### 5.3 Validation gate

- Graph nodes (post-filter) within 500–2,000 range.
- All four origins + destination + rail access/egress reachable.
- accessibility-loss CSV shows ≥3 critical edges identifiable on the connecting expressways.

### 5.4 Sub-agents in this phase

**None.** OSM extraction is rate-limited (single-threaded by Overpass policy). Post-build tasks T1.5–T1.7 are quick parallel `Bash` calls; sub-agents would add overhead without speedup.

### 5.5 Rollback

If OSMnx is rate-limited or unavailable, retry with smaller bbox quadrants and stitch. Do not commit a partial cache; the manifest hash will be wrong.

---

## 6. Phase 2 — Code adaptation

### 6.1 Prerequisites

- Phase 1 complete; corridor cache + region YAML usable.

### 6.2 Tasks (with parallelization)

```
[‖ PARALLEL BATCH — issue all of these in one message:]

T2.1  ADAPT data/scenarios/disruption_scenarios.csv
       - Remap every `D` → `T`
       - Add new rows: kci_olimpic_blockage / kci_gangbyeon_blockage /
         kci_outer_loop_blockage
       - Drop scenarios outside the corridor

T2.2  COPY data/scenarios/policy_alternatives.csv as-is
T2.3  COPY data/scenarios/sensitivity_design.csv as-is

T2.4  ADAPT data/parameters/fleet_assumptions.csv
       - Strip source_url_or_citation values; set source_class =
         expert_assumption_virtual_study
       - Verify 23/23/23/45 fleet values

T2.5  ADAPT data/parameters/rail_assumptions.csv
       - Strip Seoul Open Data plaza URLs; mark as
         abstract_long_distance_proxy_no_real_timetable

T2.7  ADAPT main.py path resolution
       PROJECT_ROOT = pathlib.Path(__file__).parent
       sys.path.insert(0, str(PROJECT_ROOT))

T2.8  ADAPT generate_report_figures.py
       - Korean axis labels; English legends
       - Drop figure 0 pipeline overview
       - Bind to kci/results/

[seq, after T2.1–T2.5 + T2.7:]

T2.6  ADAPT config.yaml
       personnel.total: 1000
       origin: A
       destination: T
       network.region_yaml: data/regions/songpa_yangju_corridor.yaml
       network.cache_path: data/cache/songpa_yangju_corridor.graphml
       bus.fleet_size: 23
       multimodal.shuttle_fleet_size: 23
       multimodal.lastmile_fleet_size: 23
       multimodal.lastmile_vehicle_capacity: 45
       rail.headway_min: 30
       rail.capacity_pax_per_train: 500
       rail.travel_time_min: 60
       failure.* : preserve upstream defaults
       phase1: preserve upstream grid (origin treatment per §6.3 below)
       phase2: preserve upstream grid

T2.9 [VALIDATION GATE]
   python main.py --quick --config config.yaml --origin A
   Expected: single Phase-1 cell completes <2 min; results/quick_check.csv written.
```

### 6.3 🟡 IN-PHASE DECISION: origin treatment in Phase 1

| Option | Cell count | Pros | Cons |
|---|---|---|---|
| (a) Full 5-factor sweep | 4× upstream (≈ 33,600 paired) | Clean robustness story | Runtime ↑ |
| **(b) Focused robustness** | upstream + 4-origin × small-cell | Faster; per-origin still reported | Two-stage analysis |

**Default if undecided at smoke time: (b)**, with Phase 4 §7 origin-robustness sub-run after Phase 1 main completes.

### 6.4 Sub-agents in this phase

**None.** Trivial CSV / YAML edits.

### 6.5 Rollback

If config schema mismatch breaks runs, diff against upstream `config.yaml`. Do NOT re-introduce excluded calibration columns.

---

## 7. Phase 3 — Smoke validation

### 7.1 Tasks (with parallelization)

```
[‖ PARALLEL BATCH 1 — issue together (B/C/D smokes use run_in_background=true
 since each takes a few minutes):]

T3.1  python scripts/run_pilot_smoke.py --config config.yaml --origin A --seeds 5
T3.2  python scripts/run_reproducibility_smoke.py
T3.3  python scripts/run_clean_checkout_smoke.py
T3.4a [run_in_background] python scripts/run_pilot_smoke.py --origin B --seeds 5
T3.4b [run_in_background] python scripts/run_pilot_smoke.py --origin C --seeds 5
T3.4c [run_in_background] python scripts/run_pilot_smoke.py --origin D --seeds 5

(harness notifies as each background job finishes; review when all done)

T3.5 [seq, after all smokes return]
   🟡 IN-PHASE DECISION: rail leg framing
     (i) Keep abstract long-distance rail [DEFAULT]
     (ii) Demote rail to alternative scenario (if structurally never competitive)
     (iii) Drop rail entirely (last resort — weakens contribution)
```

### 7.2 Validation gate

All four origins return finite penalized_makespan; censoring_rate not 100%; reproducibility manifest matches upstream pattern.

### 7.3 Sub-agents in this phase

**None.** Each smoke is a single shell command; parallelism via `run_in_background=true`.

---

## 8. Phase 4 — Full experiment runs (★ HIGHEST-LEVERAGE PARALLELIZATION)

### 8.1 The big batch

**Issue all four runs in a single message using `Bash run_in_background=true`. The harness will notify on each completion.** This is the single most important parallelization in the entire plan.

```
[‖ ALL FOUR PARALLEL — single message, all run_in_background=true:]

T4.1  python main.py --phase 1 --config config.yaml --origin A
       Output: results/phase1_results.csv, phase1_summary.csv, phase1_ci.csv
       Estimate: 2–6 h

T4.2  python main.py --phase 2 --config config.yaml --origin A
       Output: results/phase2_results.csv, phase2_ci.csv
       Estimate: 0.5–1 h

T4.3  python scripts/run_sensitivity.py --config config.yaml \
        --output results/morris_sensitivity.csv \
        --output-summary results/morris_summary.csv
       Estimate: 1–3 h

T4.4  Origin-robustness sub-run (Option (b)):
       for O in B C D; do
         python main.py --phase 1 --config config.yaml --origin $O \
           --grid focused --seeds 10 \
           --output results/phase1_origin_$O.csv
       done
       Estimate: 1–2 h total (run inside one background job)
```

### 8.2 Concurrency safety

The four runs are independent: different output CSVs, different random-seed namespaces, no shared mutable state. The only shared resource is CPU. **If the host has ≥8 cores, expect ~2× speedup over serial.** With fewer cores, expect Python GIL contention to flatten the speedup; measure on the actual host with a single cell first.

### 8.3 Runtime budget — serial vs parallel

| Run | Serial (single-machine) | Parallel (run_in_background × 4) |
|---|---|---|
| T4.1 Phase 1 | 2–6 h | 2–6 h (the bottleneck) |
| T4.2 Phase 2 | 0.5–1 h | (overlaps with T4.1) |
| T4.3 Morris | 1–3 h | (overlaps with T4.1) |
| T4.4 Origin robustness | 1–2 h | (overlaps with T4.1) |
| **Total wall-clock** | **5–12 h** | **3–6 h** |

### 8.4 If runtime overruns

Drop in priority order (per §2.4): T4.2 first, then reduce T4.3 to 100 trajectories, then T4.4.

### 8.5 Validation gate

- T4.1 paired-run rows match the cell count expected from the design.
- All cells have non-null censoring_rate.
- T4.3 Morris `mu_star` finite for the parameters that should be active.
- T4.4 sub-run completes for B, C, D.

### 8.6 Sub-agents in this phase

**None.** Run-monitoring is handled by `run_in_background` notifications; sub-agents would just add a layer of indirection.

---

## 9. Phase 5 — Analysis, CIs, figures (★ PARALLEL SUB-AGENTS)

### 9.1 Strategy

**Spawn 6 Opus sub-agents in a single message, one per artifact.** Each sub-agent reads the Phase-4 output CSVs, generates its assigned figure or table set, writes to `manuscript/figures/` or `manuscript/tables/`, and reports a one-paragraph summary of what it produced.

### 9.2 Sub-agent allocation

```
[‖ ALL SIX PARALLEL — single message with 6 Agent tool calls,
 subagent_type="general-purpose", model="opus"]

SA-5.1  "Generate figure 2: corridor map"
        Inputs:  data/regions/songpa_yangju_corridor.yaml,
                 data/cache/songpa_yangju_corridor.graphml
        Output:  manuscript/figures/figure2_corridor_map.png (Korean labels,
                 English legend; mark origins A/B/C/D and destination T;
                 highlight 올림픽대로 / 강변북로 / 외곽순환)

SA-5.2  "Generate figure 3: break-even heatmap"
        Inputs:  results/phase1_results.csv, phase1_summary.csv
        Output:  manuscript/figures/figure3_breakeven.png
                 (delta_makespan(disruption_intensity, capacity_reduction)
                 heatmap, paired CRN; mark the zero-line)

SA-5.3  "Generate figure 4: miss-rate vs disruption intensity"
        Inputs:  results/phase1_results.csv
        Output:  manuscript/figures/figure4_miss_rate.png
                 (censoring_rate vs disruption intensity for both modes,
                 error bars from paired_ci)

SA-5.4  "Generate figure 5: origin robustness"
        Inputs:  results/phase1_origin_{B,C,D}.csv + results/phase1_results.csv (origin A)
        Output:  manuscript/figures/figure5_origin_robustness.png
                 (penalized_makespan boxplot per origin per mode)

SA-5.5  "Generate all 5 tables"
        Inputs:  all Phase-4 CSVs
        Outputs: manuscript/tables/{table1_design_summary.csv,
                 table2_phase1_paired_delta.csv,
                 table3_phase2_policy.csv,
                 table4_morris_top10.csv,
                 table5_origin_robustness.csv}
                 (English headers, KCI submission_format §7 conventions)

SA-5.6  "Figure-table cross-reference audit"
        Inputs:  all of manuscript/figures/, manuscript/tables/
        Output:  manuscript/cross_ref_audit.md — a one-page check that:
                 every figure has a caption, every table has a caption,
                 numeric values in tables match the figures, no figure
                 exceeds half-page A4, total figure+table count ≤ 10.
        (Runs after SA-5.1..SA-5.5 — but it can also run in parallel and re-
        check at the end; running in parallel is fine since it just verifies.)

T5.7 [seq, after all six return]
   Sanity check the audit; regenerate any artifact flagged FAIL.

T5.8 [VALIDATION GATE]
   - Every figure renders, ≤ A4-half page
   - All table headers in English
   - Number of figures ≤ 5, tables ≤ 5
```

### 9.3 Why sub-agents here

Each figure/table is a self-contained creative + technical task: read CSV, design plot, encode KCI conventions, save PNG/CSV. Doing all 6 serially in the parent context would burn context window and serialize ~30 min of plotting. Six parallel Opus calls deliver in ~5–10 min wall-clock with isolated context per artifact.

### 9.4 Synchronization

After all 6 return, T5.7 reads the audit (SA-5.6) and triggers any regenerations. Then T5.8 closes the gate.

---

## 10. Phase 6 — Manuscript draft (★ PARALLEL SECTION DRAFTING)

### 10.1 Strategy

**Spawn 6 Opus sub-agents in a single message, one per manuscript section.** Each sub-agent gets:
- The full manuscript outline (`submission_format.md` §4)
- The relevant Phase-5 artifacts (figures, tables, captions)
- The relevant `research_plan.md` sections
- A length budget (so the total stays ≤ 30 pages)

Each writes its section in Korean as a standalone Markdown file, then the parent assembles them into one `manuscript_ko.md`.

After Markdown is assembled, run the `hwpx` skill `clone_form` workflow (sequential — single template, single output `.hwp`).

### 10.2 Sub-agent allocation

```
[‖ ALL SIX PARALLEL — single message with 6 Agent tool calls,
 subagent_type="general-purpose", model="opus"]

SA-6.1  "Draft §1 서론 (Introduction)"
        Inputs:  research_plan.md §1-3, 국방.md (military framing),
                 figure 1 caption (concept image)
        Output:  manuscript/sections/01_introduction_ko.md
        Length budget: 3–4 pages. Must invoke 투고규정 §2-나-5 framing.

SA-6.2  "Draft §2 선행연구 고찰 (Literature review)"
        Inputs:  research_plan.md §3, public_github_repo_research.md,
                 disrupted_mobilization_resilience_repo_research.md
        Output:  manuscript/sections/02_literature_ko.md
        Length budget: 3–4 pages. APA in-text citations
        (per submission_format.md §6); 10–20 references.

SA-6.3  "Draft §3 연구방법 (Methods)"
        Inputs:  research_plan.md §6-7, repo_assets_audit.md,
                 docs/analysis_corridor_method_note.md (upstream),
                 figure 2 corridor map, table 1 design summary
        Output:  manuscript/sections/03_methods_ko.md
        Length budget: 6–8 pages. Cover (a) simulator architecture,
        (b) Songpa↔양주 corridor extraction, (c) paired CRN + censoring-aware
        metrics, (d) Phase 1 + Phase 2 + Morris design.

SA-6.4  "Draft §4 결과 및 분석 (Results & Analysis)"
        Inputs:  ALL Phase-5 figures and tables, results CSVs
        Output:  manuscript/sections/04_results_ko.md
        Length budget: 6–8 pages. Reference figures 3–5 and tables 2–5
        explicitly. Report the break-even line, miss-rate curves, Morris
        top parameters, origin-robustness conclusions.

SA-6.5  "Draft §5 결론 (Conclusion + Limitations + Future work)"
        Inputs:  research_plan.md §8 (contributions), §10 (limitations),
                 §4 (out-of-scope as future work roadmap)
        Output:  manuscript/sections/05_conclusion_ko.md
        Length budget: 2–3 pages. Must include the catchment hedge from
        agents.md §7 #3b verbatim and the "virtual corridor abstraction"
        framing from agents.md §6 #1 + #2.

SA-6.6  "Draft English ABSTRACT + APA References list"
        Inputs:  ALL above outputs (read after they exist) + 5-10 chosen citations
        Outputs: manuscript/sections/00_abstract_en.md (≤ 200 words,
                 includes necessity/results/significance per
                 submission_format.md §1) AND manuscript/references_apa.md
                 (APA Style entries per submission_format.md §6 templates,
                 internet-searchable, English titles where possible).
        NOTE: SA-6.6 should be launched AFTER SA-6.1..SA-6.5 because it
        needs to summarize their content. So run as a second parallel batch
        of size 1.
```

### 10.3 Sequential post-processing

```
T6.7 [seq, after SA-6.1..SA-6.5 return]
   Assemble manuscript_ko.md by concatenating section files in order:
     00_abstract_en.md (after SA-6.6 returns)
     01_introduction_ko.md
     02_literature_ko.md
     03_methods_ko.md
     04_results_ko.md
     05_conclusion_ko.md
     references_apa.md

T6.8 [seq] Build the replacements map (manuscript/replacements.json):
   Map each placeholder string in 한국군사학논집 논문편집양식.hwp to the
   actual manuscript content. Handle title, author block (placeholder until
   resolved), abstract, keywords, footnote, body section markers, references.

T6.9 [seq] Run clone_form.py (Workflow F):
   python "C:/Users/User/.claude/skills/hwpx/scripts/clone_form.py" \
     "학회_관련_정보/한국군사학논집_논문편집양식.hwpx" \
     "manuscript/manuscript.hwpx" \
     --map manuscript/replacements.json \
     --validate

T6.10 [seq] Post-process namespaces (REQUIRED):
   python "C:/Users/User/.claude/skills/hwpx/scripts/fix_namespaces.py" \
     manuscript/manuscript.hwpx
   python "C:/Users/User/.claude/skills/hwpx/scripts/validate.py" \
     manuscript/manuscript.hwpx

T6.11 [seq, MANUAL] In 한컴오피스 한글:
   - Open manuscript/manuscript.hwpx
   - Replace any remaining placeholder body content with manuscript prose
     (clone_form covers structured replacements; manual paste covers prose-
     heavy sections that don't match a fixed template line)
   - Insert PNGs from manuscript/figures/ at the marked locations
   - Rebuild tables using the template's existing borderFill IDs
   - Save As → .hwp (KCI accepts .hwp only per submission_format.md §1)

T6.12 [VALIDATION GATE]
   - Body font Pretendard 10pt 160% JUSTIFY (random spot-check)
   - Korean section headings at OUTLINE level 0/1/2
   - Tables/figures/abstract/references in English (APA)
   - English abstract ≤ 200 words
   - Total pages ≤ 30 in 한글 print preview
```

### 10.4 🟡 IN-PHASE DECISION: figures inserted programmatically vs manually

`clone_form.py` text replacement is deterministic and safe; figure XML is fragile (per hwpx skill SKILL.md). **Default: manual insertion in 한글 (T6.11).** Reserve programmatic insertion for camera-ready if requested.

### 10.5 Why sub-agents here

Manuscript sections require deep reasoning about content + style + length budget per section. Each section pulls from different upstream documents. Six parallel Opus agents save ~3–5× wall-clock vs the parent serial-drafting (~5–8 hours single-thread → ~1–2 hours parallel). This is the second-highest-leverage parallelization in the plan after Phase 4.

---

## 11. Phase 7 — Submission package + JAMS upload

> Almost entirely user-side. Plan-side work is a checklist + final anonymization.

### 11.1 Pre-submission checklist (per submission_format.md §1, §9)

```
[ ]  manuscript.hwp in 편집양식 (Pretendard 10pt, A4, ≤ 30 pages)
[ ]  All figures / tables / abstract / references in English (APA)
[ ]  English abstract ≤ 200 words; necessity/results/significance present
[ ]  Author info STRIPPED from filename and document body (anonymous review)
[ ]  KCI similarity report < 10% (run KCI 문헌유사도 검사)
[ ]  보안성 검토완료 문서 (KMA — should already be in hand from Phase 1 §5.2 T1.0)
[ ]  저작권 양도 및 활용 동의서 자필 서명 후 jpg 스캔
       파일명: 저작권 양도 및 활용 동의서(<저자명>).jpg
[ ]  Funding statement decided (real grant or "no external funding")
[ ]  Cover-letter positioning paragraph invokes 투고규정 §2-나-5
       "첨단 과학기술의 군사적 응용"
```

### 11.2 JAMS upload sequence

```
1. Login to https://kjmac.jams.or.kr
2. 학술지 → 논문제출 → 한국군사학논집 클릭
3. 연구 윤리 서약 (모든 저자 서명)
4. 논문관련 정보 입력
   - 원문파일: manuscript.hwp (anonymized filename)
5. 첨부파일 업로드
   a) 이미지파일: 저작권 양도 및 활용 동의서(<저자명>).jpg
   b) 첨부파일: 보안성 검토완료 문서
   c) KCI 문헌유사도 결과 (PDF)
6. "다음 단계로" 클릭
7. 저자 등록 (공동저자 포함, 체크리스트, CCL 동의)
8. "제출" 클릭
9. 접수 확인 메일 수신 → received 날짜 기록
```

### 11.3 Post-submission

- Track received → accepted → published timeline. Next publication windows: Feb 28, Jun 30, Oct 31.
- Reject ("게재불가") → 6-month re-submission lock starts immediately.
- Revise ("수정후 재심") → editor-issued deadline; rerun affected analyses; resubmit.

### 11.4 Sub-agents in this phase

**None.** Sequential JAMS form.

---

## 12. Open items that block submission (NOT block running experiments)

These can be parked until Phase 6/7 but **must close before Phase 7 final submit**:

| Item | Owner | Source | Latest start |
|---|---|---|---|
| Authorship and affiliation | User | `agents.md` §7 #12 | Phase 6 §10.3 T6.8 |
| Funding statement | User | `submission_format.md` §10 | Phase 6 §10.3 T6.8 |
| 보안성 검토완료 문서 발급 | User (KMA process) | `submission_format.md` §1 #4 | **Phase 1 §5.2 T1.0 — start NOW** |
| Final Korean and English titles | User + author | `submission_format.md` §10 | Phase 6 §10.2 SA-6.6 |
| 5 + 5 keyword sets | User + author | `submission_format.md` §10 | Phase 6 §10.2 SA-6.6 |
| English abstract (≤ 200 words) | SA-6.6 at draft freeze | `submission_format.md` §10 | Phase 6 §10.2 SA-6.6 |
| KCI 문헌유사도 < 10% | Author at submission | `submission_format.md` §1 | Phase 7 §11.1 |

Phases 0–5 can complete without any of these. Phase 6 can be drafted with placeholders. Phase 7 cannot proceed until **all** are closed.

---

## 13. Decision points summary (where this plan branches)

| § | Decision | Default | Trigger to revisit |
|---|---|---|---|
| 5.2 T1.3 | Final OSM bbox | lat 37.46–37.78, lon 126.85–127.20 | Node count outside 5,000–20,000 pre-filter |
| 6.3 | Phase 1 origin treatment | (b) Focused robustness | If runtime budget allows full 5-factor sweep, switch to (a) |
| 7.1 T3.5 | Rail leg framing | (i) Abstract long-distance rail | If multimodal is structurally never competitive |
| 10.4 | Figure insertion method | Manual via 한글 | Camera-ready may use programmatic |
| 8.4 | Phase 4 priority drop order | T4.2 → T4.3 (reduce trajectories) → T4.4 | If wall-clock budget tight |

---

## 14. Roll-back and recovery notes

- **Phase 0 imports break:** restore `kci/src/realworld/__init__.py` from upstream and re-prune. Do not delete `kci/src/`.
- **Phase 1 OSM extraction fails / rate-limited:** retry with smaller bbox quadrants and stitch. Do not commit a partial cache.
- **Phase 2 schema mismatch:** diff `config.yaml` against upstream — usually a renamed `policy.* → dispatch.policy.*`. Do not bring the upstream parameter-evidence review columns back.
- **Phase 4 background run fails:** the harness will notify. Do not retry blindly; inspect the output CSV partial state, identify the failed cell, restart from there. Do not drop CRN pairing under time pressure.
- **Phase 4 runtime overrun:** apply §8.4 priority drop. Tighten Phase 1 disruption-intensity grid first; preserve seeds.
- **Phase 5 sub-agent fails:** re-run that one sub-agent with stricter prompt; the other 5 outputs are already in hand.
- **Phase 5 figures cluttered:** consolidate to ≤ 5; KCI 30-page limit is tight.
- **Phase 6 sub-agent produces over-budget section:** re-issue with a tighter length cap. Do not paste a >budget section into the manuscript.
- **Phase 6 clone_form coverage low (< 60 %):** the template's text differs more than expected; re-analyze with `clone_form.py --analyze` and rebuild the map JSON. Do not edit `<hp:t>` nodes by hand.
- **Phase 7 보안성 검토 delayed:** all of Phases 0–6 can wait completed; this is the most likely real bottleneck. The mitigation (start at Phase 1 §5.2 T1.0) is already in the plan.

---

## 15. What this plan does NOT do

- Re-litigate the 16 resolved decisions in `agents.md` §7. If a decision needs to change, edit `agents.md` first, then update this plan.
- Pursue the 12 deferred formal-acceptance gates. Those belong to the follow-up calibration paper.
- Author manuscript prose with the parent agent (sub-agents do this — see Phase 6 §10.2).
- Bind to a specific submission target issue. Rolling submission; issue assignment happens at acceptance.

---

## 16. Quick-start summary (TL;DR for execution)

1. **Now:** Tell user to begin 보안성 검토 발급 at KMA (Phase 1 §5.2 T1.0). This is the real-world bottleneck.
2. **Phase 0** (~30 min): Run a single message with 6 parallel `Bash`/`Edit` calls (T0.3, T0.4, T0.6, T0.8, T0.9, T0.10, T0.12), then sequential T0.5 / T0.7 / T0.11, then validation T0.13.
3. **Phase 1** (~1 h): Sequential T1.1 → T1.2 → T1.3 → T1.4, then one message with 3 parallel `Bash` calls (T1.5, T1.6, T1.7), then validation T1.8.
4. **Phase 2** (~30 min): One message with 7 parallel `Edit` calls (T2.1–T2.5, T2.7, T2.8), then sequential T2.6, then validation T2.9.
5. **Phase 3** (~15 min): One message with 6 parallel `Bash` calls (3 foreground + 3 background), then T3.5 decision.
6. **Phase 4** (~3–6 h wall-clock): One message with 4 parallel `Bash run_in_background=true` calls (T4.1, T4.2, T4.3, T4.4). Wait for harness notifications.
7. **Phase 5** (~30 min wall-clock): One message with 6 parallel `Agent` calls (SA-5.1..SA-5.6, all `subagent_type="general-purpose"`, `model="opus"`).
8. **Phase 6** (~1–2 h wall-clock): One message with 5 parallel `Agent` calls (SA-6.1..SA-6.5), then 1 `Agent` call (SA-6.6) after they return, then sequential T6.7..T6.12.
9. **Phase 7**: User-side checklist + JAMS upload. Cannot start until 보안성 검토 in hand and Phase 6 manuscript ready.

> **Total Claude-side wall-clock**: ~7–11 h dominated by Phase 4. **Total submit-ready**: dominated by user-side 보안성 검토 turnaround.
