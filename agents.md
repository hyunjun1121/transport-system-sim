# AGENTS.md — Transport System Simulation

> **Wartime reserve-force (전시 동원예비군) mobilization transport micro-simulation.**
> Active case study: **Songpa → Gangwon Goseong (22nd Infantry Division area)**, ~1,000 mobilized
> reservists. Compares a **bus-only** alternative against a **rail-bus multimodal** alternative under
> identical wartime disruption conditions.
>
> **Public-data-based conditional scenario simulation for decision support.** It is not a field-use
> movement plan. `final_study_ready=false` by design.

**This file is the single source of truth for the project.** It covers purpose, the canonical
experiment, data provenance, methodology, headline results, repository layout, architecture, how to
reproduce, verification, constraints, and deliverables. The companion `CLAUDE.md` is a lighter
"how to work in the repo" guide; where the two disagree, **this file wins** (current as of
2026-07-21).

The current paper evidence is the **2026-07-21 top-10/full-scope paper-revision experiment** on the
Korean 표준노드링크 network. It adds physical reverse-network empty returns, explicit rail states,
two resource frames, post-blockage rerouting, paired/bootstrap inference, graph-scope checks,
random-threat outer replication, adaptive policies, Morris elementary effects, break-even fine
granularity, scale sensitivity, and path-interdiction threat analysis. The 2026-07-17
14,490-row pilot remains a legacy regression artifact; its numeric paper claims are superseded.

The authoritative paper analysis is
`results/paper_revision_top10_corridor_v4_20260721/analysis/full/analysis_manifest.json`, backed by
eleven campaign result sets. The manifest reports
`analysis_complete_full=true`, zero completeness blockers, and `final_study_ready=false`.

**Headline:** resource definition changes the baseline. In the configured bundle (bus 23 road
vehicles; multimodal 46 road vehicles plus rail), means are 374.1 vs 363.8 min and the paired
difference is unresolved. With equal total road fleets of 23, means are 374.1 vs 475.8 min and
bus-only is faster. In that equal-road-fleet frame with normally available rail, the estimated
long-haul road-damage break-even multiplier is 1.742, joint-bootstrap 95% interval 1.550–2.003.
See §5.

**Extended campaigns (2026-07-22):** break-even fine (17 multipliers at 0.1 granularity),
scale sensitivity (demand 2,000–12,000), and path-interdiction threat (k=3/k=5 shortest-path
interdiction). Eleven campaigns total, 24,630 full rows executed.
bus-only is faster. In that equal-road-fleet frame with normally available rail, the estimated
long-haul road-damage break-even multiplier is 1.742, joint-bootstrap 95% interval 1.550–2.003.
See §5.

---

## 1. What is being compared

Two transport alternatives move **~1,000 reservists** from assembly zone **A** (Songpa, Olympic Park)
to destination zone **D** (Goseong, 22nd Infantry Division area) over a **24-hour (1440 min) window**:

- **bus_only** — direct road transport A → D over the road network.
- **baseline_multimodal** — shuttle A → S (Cheongnyangni Station) → rail S → R (Gangneung Station,
  KTX-Eum chartered nonstop) → last-mile bus R → D.

Both alternatives run under the same disruption scenario and common-random-number seed block
(3101–3130). Comparisons use two explicit resource frames: `configured_bundle` (23 direct buses vs
23 feeder + 23 last-mile road vehicles plus rail) and `matched_road_fleet` (23 road vehicles on each
side; multimodal splits them 12 + 11 and still includes rail). The outcome rule maximizes completion
rate first, then minimizes finite makespan when completion rates match.

Canonical nodes (all coordinates are **public administrative centroids / public rail stations** —
never real unit facility coordinates):

| Node | Role | Location | Coord (lat, lon) |
|------|------|----------|------------------|
| A | assembly zone | Songpa, Olympic Park | 37.5202, 127.1210 |
| S | rail access | Cheongnyangni Station (Seoul) | 37.5806, 127.0484 |
| R | rail egress | Gangneung Station (Gangwon) | 37.7645, 128.8996 |
| D | destination | Goseong Tochon-myeon Hakya-ri | 38.3000, 128.5500 |

---

## 2. Data sources (every input, with provenance)

All inputs are **offline, public-data-derived**. No live OSM/Overpass/data.go.kr calls in the run path;
the network cache was built once and reused. Nothing here is calibrated to observed wartime data
(such data does not exist publicly); every input carries an explicit `source_class` and claim boundary.

### 2.1 Region & canonical nodes
- **File:** `data/regions/goseong_mobilization.yaml` (region spec, bbox 37.45–38.35°N, 126.95–128.95°E).
- **Source class:** `public` — administrative centroids + public rail-station coordinates.
- **Corridor:** Songpa →(bus ~30 min)→ Cheongnyangni →(KTX-Eum 114 min)→ Gangneung →(bus ~40 min)→
  Goseong. ~185 km, ~3 h door-to-door under normal conditions.

### 2.2 Road network — Korean 표준노드링크 (canonical default)
- **Primary source:** 국토교통부 **표준노드링크** (Standard Node-Link, 국가교통정보센터/NTIS) shapefile
  — the official Korean national road network. This has been the **sole canonical Goseong source**
  since commit `cbb49089` (Phase 2 promotion). The earlier OSM-derived run is **archived** under
  `_archive/realworld_pilot_osm/`; the OSM-era cache is no longer in the active path.
- **Cache build:** `scripts/build_goseong_nodelink_cache.py` →
  `data/cache/goseong_nodelink_road.graphml` (GraphML).
- **Cache stats (from `data/cache/goseong_nodelink_road_manifest.json`):** source graph **360,562
  nodes / 972,134 edges** (MultiDiGraph). The paper-revision full reference after simulator filtering is
  **360,556 / 971,680**. Corridor scopes are top-3 **752 / 1,512**, top-5 **2,733 / 5,532**, and
  top-10 **9,089 / 18,602**; top-10 is the current paper analysis graph. Top-3 is the union of three
  exact shortest simple paths for each of A→D, A→S, and R→D. Top-5/top-10 add deterministic
  penalty-diversified paths; they are nested sensitivity envelopes, not exact global k-shortest sets.
  `graphml_sha256 = ef96e6a4a4f624094a782f9417ee87ac78a0dfe4583324eb451bcdc2671aa14`.
- **The cache is gitignored (475 MB > GitHub's 100 MB limit; ignored since `9d82be38`).** It is
  regenerable from the committed build script + the SHP under gitignored `data-collections/` (3 GB),
  and its integrity is anchored by the committed sha256 manifest above. This is by design, not a
  cleanup artifact — a fresh checkout rebuilds the cache, it does not fetch it.
- **Per-class road attributes:** `data/parameters/road_class_overrides.csv` (REQUIRED input — without it
  the runner falls back to raw defaults). 17 road classes, each with `speed_kph`, `capacity_veh_per_hr`,
  `base_p_fail`, and a per-field source class:
  - **Speed** — `public-data-derived`: OSM observed median `maxspeed` tags for the 6 routeable classes
    with adequate coverage (motorway 100, trunk 80, primary 60, secondary 60, motorway_link 50,
    trunk_link 40); `literature-derived` / statutory for sparse classes (Korea Road Traffic Act
    Enforcement Rules Art. 11).
  - **Capacity** — `public-data-derived`: observed median `lanes` × **KOTI HCM Korea 2013** per-lane
    proxy (e.g. motorway 1800/ln, trunk 1000/ln, primary 900/ln).
  - **base_p_fail** — `literature-derived`: **Fwa (2006), Highway Maintenance Management** per-class
    base disruption rates. Current paper-revision campaigns set `p_fail_scale=0.0`; these values remain
    graph attributes but do not drive paper results. Scenario-selected edges receive forced deterministic
    disruptions instead.
  - **VDS expressway observations** feed a sensitivity fragment (`data/parameters/vds_motorway_overrides.csv`,
    built via `scripts/build_vds_override.py`; public-data-derived, not calibrated).
  - **Evidence aids (also under `data/parameters/`):** `road_speed_evidence_candidates.csv` (OSM
    maxspeed), `road_capacity_evidence_candidates.csv` (OSM lanes), `parameter_sources.csv`,
    `rail_assumptions.csv`, `fleet_assumptions.csv`.

### 2.3 Rail service
- **Model:** wartime **chartered nonstop express** — KTX-Eum, Cheongnyangni → Gangneung, **114 min**,
  **600 pax/train**, **30 min dispatch interval** (a charter *dispatch* planning assumption, not a
  public-timetable headway). Defined in the region spec (`rail.travel_time_min/headway_min/capacity`).
- **Sources:** KORAIL public timetable / rolling-stock; namu.wiki 강릉선.
- **Reframe note:** an earlier 3.583-min-headway / 922-pax derivation (KTDB GTFS / Metro9) was
  **discarded** as wrong-service (peacetime scheduled passenger rail ≠ wartime chartered mobilization).
  The wartime-chartered framing is a planning assumption, not operational availability.

### 2.4 Demand
- **File:** `data/scenarios/demand_profiles.csv`, profile `pilot_default_demand`.
- **Values:** **1,000 pax**, origin A (Songpa), assembly at t=0, arrivals via
  `lognormal_sample_fixture` (μ=2.45, σ=0.75), boarding batch 45 pax, no no-show/late penalties.
- **Source class:** `sensitivity-only` — fixture scale anchored to **진학은 et al. (2022), KCI**
  arrival-delay distribution. Not a calibrated OD demand estimate.

### 2.5 Fleet
- **File:** `data/scenarios/fleet_profiles.csv`, profile `pilot_default_fleet`.
- **Values:** 3 roles — **direct_bus / feeder_shuttle / last_mile** — each **23 vehicles, 45 pax/vehicle,
  5 min dispatch interval, first departure t=0, 8 min turnaround**.
- **Source class:** `sensitivity-only` — finite military-fixed fleet profile, not an operating roster.

### 2.6 Disruption scenarios
- **File:** `data/scenarios/goseong_disruption_scenarios.csv` — **25 deterministic scenario rows**
  (`force_deterministic=True`), each carrying `family`, `selection_method`, `target_segment`,
  `capacity_factor`, `p_fail_scale`, `max_edges`, rail multipliers, `evidence_class`, and claim-boundary
  notes. Families:
  - `random` — hash-ranked capacity-reduction / blockage baselines.
  - `critical_link` — top road edges by weighted edge betweenness.
  - `access_road` — shortest-path degradation on A→S / A→D; **segment-targeted damage ladder A→S**
    (mild/severe/extreme + `severe_plus50` stability rug).
  - `last_mile` — shortest-path degradation R→D; **segment-targeted damage ladder R→D** (+ `severe_plus50` rug).
  - `long_haul` — **segment-targeted damage ladder S→R** (mild/moderate/severe) — the trunk the bus-only
    alternative shares; the multimodal alternative bypasses it by rail.
  - `rail_station_access` — road edges incident to S/R connectors.
  - `spatial_hazard_overlay` — bbox exposure overlays (Tancheon/feeder/last-mile/assembly/transfer).
  - `rail_service` — `goseong_rail_unavailable` (rail_travel_time_multiplier=100), the binary
    assumption-failure stress for A1.

### 2.7 Legacy pilot design (regression reference only)
- **File:** `data/manifests/goseong_experiment_design.json`, profile **`full_pilot`**.
- **Matrix:** **23 policies × 25 scenarios × 30 seeds = 17,250 nominal rows.**
- **Executed:** 4 spatial-overlay scenarios select no candidate edges on the 752-node analysis graph
  and are skipped as inapplicable (recorded in the pilot manifest's `skipped_scenarios`:
  `goseong_spatial_tancheon_corridor`, `goseong_spatial_feeder_east`, `goseong_spatial_lastmile_west`,
  `goseong_transfer_point_blockage`) → **21 executed scenarios × 23 policies × 30 seeds = 14,490 rows**.
- **Policies (23):** the 2 baselines (`bus_only`, `baseline_multimodal`) plus 21 alternatives —
  last-mile redundancy, staggered/adaptive dispatch, increased feeder capacity, rail delay/partial
  unavailability, fleet shortage (stress/severe), congestion ladders (moderate/heavy/severe/peak ×
  bus/multimodal), transfer-stress ladders (mild→extreme), last-mile-capacity ladders.

These 14,490 rows predate physical reverse-network empty returns and the paper-revision resource-frame
analysis. Keep them for regression history; do not use their numeric conclusions in the manuscript.

### 2.8 Current paper-revision design

- **File:** `data/manifests/paper_revision_experiment_design.json`.
- **Output root:** `results/paper_revision_top10_corridor_v4_20260721/`.
- **Eleven campaigns / 24,630 rows:** paired reanalysis 2,520; graph scope 1,330; break-even 1,920;
  break-even fine 2,040; demand–fleet 1,920; scale sensitivity 240; road–rail map 3,600;
  path-interdiction threat 2,400; random-threat outer loop 6,000; adaptive policies 1,260;
  Morris 1,400.
- **Road–rail map:** 6 road multipliers × 5 rail conditions (available 1.0, degraded 1.25/1.5/2.0,
  unavailable) × 2 resource frames × 2 policies × 30 arrival seeds.
- **Adaptive policies:** 3 rail conditions (available 1.0, degraded 1.5, unavailable) × 2 frames ×
  7 policies × 30 seeds. All current paper campaigns use `strict` departure policy.
- **Core mechanics:** reverse-network empty return before reuse, explicit rail states, blocked-edge
  rerouting, configured and matched-road-fleet frames.
- **Inference:** paired t and 10,000-replicate percentile bootstrap intervals, joint-seed crossing
  bootstrap, two-level threat/arrival bootstrap, and Morris elementary effects.

---

## 3. Wartime assumptions A1–A4 (the core reframe)

The experiment is organized around four explicit wartime assumptions. They are **stated scope
conditions**, not measured properties — and they drive the design (what is modeled vs. abstracted away).

- **A1 — Baseline rail state.** Chartered non-stop rail is the normally available baseline condition.
  The road–rail map tests 1.25×/1.5×/2.0× degradation and explicit unavailability; the adaptive campaign
  uses 1.5× as its representative degraded state. Unavailability is a service state, not an arbitrary
  large travel time.
- **A2 — Low civilian background traffic.** The implemented planning input is **100 veh/h**, not literal
  zero. It is low relative to link capacity, so the BPR term is small by construction. Treat that as an
  assumption consequence, not an independent finding.
- **A3 — Fixed road fleets.** Compare both the configured bundle (23 direct vs 23 feeder + 23 last-mile)
  and an equal-total-road-fleet frame (23 vs 12 + 11). The second still includes rail and is not equal cost.
- **A4 — Scenario-defined threat.** Severity and location are stress inputs, not asserted real damage.
  The paper uses a road multiplier grid, 100 random threat-set outer replications, and Morris trajectories.

---

## 4. Methodology

### 4.1 CRN paired design
`bus_only` and static multimodal policies run under the same 3101–3130 arrival seeds. Per-seed
Δ = bus makespan − multimodal makespan is analyzed only when completion rates match and both times
are finite. Completion mismatches remain explicit.

### 4.2 Deterministic within-scenario; t-CI across seeds
Fixed-scenario campaigns hold the threat set constant and vary 30 arrival seeds. They report paired
t and 10,000-replicate percentile-bootstrap intervals. The random-threat campaign nests 30 arrival
seeds within each of 100 threat sets and uses a two-level bootstrap. Replicate-count tables at
5/10/20/30 prevent a blanket adequacy claim for 30 runs.

### 4.3 BPR no-op under A2
At the 100 veh/h planning input relative to link capacity, the BPR term `1 + α(V/C)^β` approaches 1. The engine retains BPR, while paper comparisons obtain
disruption effects from direct slowdown, blocking with rerouting, rail state, demand, and fleet. Low BPR
impact is a scoped model consequence.

### 4.4 Segment-targeted road-damage decomposition
Road damage is applied via a **direct-slowdown lever**: selected edges get
`travel_time_multiplier = road_travel_time_multiplier` with `capacity_factor=1.0`, isolating road damage
from the wartime-inert BPR/capacity path. Targeting is by **functional segment shortest-path**, not
global betweenness, so each damage ladder bites the leg it is meant to test:

| Segment | bus_only | multimodal | Interpretation |
|---------|----------|------------|----------------|
| **A→S** access (feeder shuttle leg) | collateral only (bus goes A→D direct) | **bites** (its feeder leg) | multimodal-exclusive cost |
| **R→D** last-mile (terminal road to D) | **bites** | **bites** | shared terminal bottleneck |
| **S→R** long-haul trunk | **bites** (bus shares trunk) | rail-immune (by A1) | rail-substitution benefit |

This decomposition replaces an earlier global-betweenness targeting that was inert on multimodal (an
artifact, not a measured robustness property).

### 4.5 Vehicle return, rerouting, and rail-state policies

Road vehicles unload, traverse the current reverse road network empty, and then incur turnaround time
before reuse. Blocked edges are removed and the remaining route is searched again; a road leg is
incomplete only when no path remains. Rail has available, degraded, and unavailable states. Adaptive
policies include precheck switching, 600/400 splitting, and station fallback after 30/60/90 minutes.
In the matched-road-fleet policy comparison all policies use 23 road vehicles: bus 23 direct;
static/precheck 12 feeder + 11 last-mile; split 6 direct + 9 feeder + 8 last-mile; fallback 8 feeder +
8 last-mile + 7 reserve. Rail is additional.

### 4.6 Oracle byte-identity guard
`generate_phase23_oracle.py` pins `base_config_sha256` (`454269d0…`) and `runs_sha256` (`16b42655…`).
`test_byte_identity_against_oracle` re-runs 8 frozen specs bit-for-bit (6 baseline bus/multimodal ×
seeds 1101–1103 + 2 road-damage with multiplier=2.0). The oracle guards the **config-level failure
multiplier** on the real-p_fail graph and is **independent of CSV targeting** — so retargeting the
segment damage (§4.4) did **not** require an oracle refreeze. Oracle test stays GREEN.

---

## 5. Current paper results (1000-pax baseline unless noted)

The comparison uses Δ = bus-only makespan − static-multimodal makespan. Negative values favor bus-only;
positive values favor static multimodal transport. Completion rate is compared first.

| Resource frame | bus mean | multimodal mean | mean Δ | paired t 95% CI | Reading |
|---|---:|---:|---:|---:|---|
| configured bundle | 374.1 | 363.8 | +10.3 | [−12.6, 33.2] | point estimate favors multimodal; unresolved |
| equal total road fleet | 374.1 | 475.8 | −101.7 | [−125.0, −78.4] | bus-only faster; rail/cost still unmatched |

In the equal-road-fleet frame with normally available rail, long-haul road slowdown changes mean Δ
from −19.5 min at 1.6× to +7.9 min at 1.8×. The interpolated crossing is **1.742×**, with joint-seed
bootstrap 95% interval **[1.550, 2.003]**. The configured-bundle curve has no crossing in 1.0–3.0×.

Graph scope matters. In the configured-bundle graph campaign (7 scenarios × 5 common seeds), top-3
connectivity/ranking agreement with full scope is 0.786/0.686; top-5 and top-10 are 1.000/1.000.
Top-3 S→R normal time is 1.218× full and top-10 is 1.015×. This does not directly audit the matched-
road-fleet conclusion. Top-10 is the paper graph, but its full-scope travel-time ratio reaches 1.157 at
the extreme 3.0× target slowdown.

Blocked roads reroute. The current critical-link and fixed random-blockage cases complete for both
alternatives; old top-3 disconnection claims are superseded. Under the equal-road-fleet frame and unavailable rail, static multimodal
completion is 0, while precheck switching ties bus-only at completion 1.0 and 374.1 min. Across
100 random threat sets × 30 arrival seeds, both alternatives complete all configured-bundle draws;
mean Δ is +11.674 min with two-level bootstrap interval [9.221, 14.257]. These simulation frequencies
are not real-event probabilities.

---

## 6. Repository state (post-cleanup, 2026-07-18)

The repo was aggressively decluttered to the current experiment context. Surviving active scope:

| Tree | Count | Contents |
|------|-------|----------|
| `src/realworld/` | **21 .py** | 20 KEEP modules + slim `__init__.py` (see §7) |
| `src/` (core engine) | 12 .py | `network`, `models`, `policies`, `dispatch`, `fleet`, `traffic`, `disruptions`, `rail`, `transfers`, `metrics`, `scenario`, `sim_types` |
| `tests/` | **36** | directly-executable, all PASS (incl. oracle byte-identity) |
| `scripts/` | **11** | the run-path + provenance CLIs (see §8) |
| `data/` | **53** | current experiment inputs + truth table only |
| `docs/` | **3** | `project_overview.md`, `experiment_design_v2.md`, `claim_language_guard.md` |

**Archived (moved, preserved, not active) — `_archive/`:** `web_demo/`, `국방AI_활용_아이디어_경연대회/`
(2026 defense-AI submission), `kci_redesign/` + `previous-kci/` (KCI/한국군사학논집 redesign),
`cloned_repo/` (reference snapshot), `realworld_pilot_osm/` (OSM-era results),
`review_submission_bundle/`, and the `.tmp_*` intake trees.

**Stale-reference hazard.** If an older external note/memory references `*_acceptance.py`, ~90+ `scripts/`,
`main.py`, `ml_analysis`, `kci_redesign/` as *present in the active path* — it is stale. Trust this file,
`CLAUDE.md`, `git log`, and `ls`.

**Ignored by default** (large or regenerable, do not commit): `_archive/`, `data-collections/`
(3 GB 표준노드링크 SHP; regenerable, the `.graphml` cache is rebuilt from it), `.venv/`,
`data/cache/goseong_nodelink_road.graphml` (475 MB; see §2.2).

---

## 7. Architecture

### 7.1 Dataflow
`data/regions/goseong_mobilization.yaml` + `data/cache/goseong_nodelink_road.graphml` +
`data/parameters/road_class_overrides.csv` → `src/realworld/adapter.build_simulator_graph()`
(NetworkX `DiGraph`) → `src/scenario.run_scenario(G, config, scenario_type, policy, params, seed)` →
KPI `dict`. `pilot_experiments` joins cache + scenarios + policies + design profiles → `run_scenario`
over CRN seed blocks → separated CSV/manifest outputs.

Two scenario types share one runner:
- `bus_only`: assembly `A` → road network → destination `D`.
- `multimodal`: `A` → shuttle → rail access `S` → rail → rail egress `R` → last-mile road → `D`.

### 7.2 Core engine (`src/`, each a single concern)
- `network.py` — builds the DiGraph (driven by the realworld adapter, not a config file).
- `models.py` — BPR link travel time, arrival-delay sampling, failure helpers.
- `policies.py` — `StrictPolicy` (depart on time, arrived pax only) vs `GracePolicy(W, theta)`.
- `dispatch.py` — queue-based departure-manifest planning per policy.
- `fleet.py` — `FleetAvailability` (finite fleet, turnaround reuse, optional noise).
- `traffic.py` — `DynamicRoadTraffic`: rolling-window volume → hourly BPR, per-edge entry, optional
  rerouting around blocked edges.
- `disruptions.py` — `sample_edge_disruptions`: per-edge blocked / capacity-reduction /
  travel-time-multiplier state.
- `rail.py` / `transfers.py` — fixed-headway rail departure; transfer delay = base + per-passenger.
- `metrics.py` — makespan, `completion_rate`, `censored_count`, `penalized_makespan`,
  unit-consistent resource KPIs.
- `scenario.py` — orchestrator; the stable public API everything calls.
- `sim_types.py` — shared immutable records (`ServiceSpec`, `EdgeDisruption`, …).

### 7.3 Real-world pipeline (`src/realworld/`, 20 KEEP modules)
Converts the official Korean 표준노드링크 road graph into the simulator contract and runs the wartime
experiment:
- `nodelink_network.py` — Korean 표준노드링크 SHP → GraphML (canonical Goseong source).
- `osm_network.py` — GraphML cache load/save (offline; OSM is an archived alternative source).
- `vds_calibration.py` — VDS expressway observations → road-class override fragment.
- `attributes.py` / `adapter.py` — normalize edge attrs into simulator fields (`t0`, `capacity`,
  `base_p_fail`, `mode`); filter pedestrian/cycle/service geometries; snap zones + rail points;
  `build_simulator_graph()`.
- `road_overrides.py` — applies the evidenced per-class speed/capacity/p_fail override table.
- `regions.py` / `types.py` — region registry (`RegionSpec`, assembly/destination zones, rail access
  `S` / egress `R`, public-coordinate policy).
- `validation.py` — `assert_graph_ready()` / `validate_graph_readiness()` pre-run checks.
- `disruption_scenarios.py` — loads the wartime scenario table (§2.6).
- `policy_alternatives.py` — policy-variant table (congestion/transfer/fleet stress, etc.).
- `parameters.py` — shipped parameter tables (speed/capacity/pfail source classes).
- `pilot_experiments.py` — **the runner**: joins cache + scenarios + policies + design profiles →
  `run_scenario` over CRN seed blocks → separated CSV/manifest outputs. Named profiles
  (`sample`/`staged`/`full`/`multi-corridor`/`multi-corridor-full`/`full-graph`) fix the
  policy×scenario×seed matrix.
- `plausibility.py` — route-plausibility checks (backing `route_plausibility.csv`).
- `artifact_invalidation_matrix.py` / `phase_gate_ledger.py` / `claim_language_guard.py` /
  `manifest_timestamp.py` / `source_artifacts.py` — runtime provenance, claim-boundary guard, and
  integrity helpers the runner writes into its manifest.

`src/realworld/__init__.py` is **slim**: it imports only the 20 KEEP modules and re-exports just the
package-level names KEEP code uses. Do **not** re-add eager imports of removed modules.

---

## 8. Reproduce

All run from repo root on Windows PowerShell with the local venv (`.\.venv\Scripts\python`; setup:
`py -3.11 -m venv .venv` then `.\.venv\Scripts\python -m pip install -r requirements.txt`). The full
re-run is ~2–3 h wall-clock on the 752-node analysis graph.

### 8.1 Run-path scripts
- **Current paper experiment:** `run_paper_revision_experiments.py`.
- **Current paper analysis:** `analyze_paper_revision_results.py`.
- **Legacy pilot experiment:** `run_pilot_experiments.py`.
- **Outputs/proofs:** `regenerate_truth_table.py` (truth table), `generate_phase23_oracle.py`
  (byte-identity oracle), `run_bpr_noop_sweep.py` (A2 BPR no-op proof), `audit_claim_language.py`
  (claim guard).
- **Cache build (only if SHP present; cache otherwise rebuilt/regenerable):**
  `build_goseong_nodelink_cache.py`, `build_vds_override.py`, `apply_road_overrides_to_cache.py`.
- **Provenance CLIs:** `run_plausibility_validation.py` (regenerates `route_plausibility.csv` /
  `external_route_benchmarks.csv` / `validation_summary.md`), `run_variance_diagnostic.py`
  (Phase T2 wartime-variance-source diagnostic), `write_artifact_invalidation_matrix.py`
  (artifact-invalidation matrix; CLI-tested).

### 8.2 Current paper-revision experiment and analysis

```powershell
.\.venv\Scripts\python scripts\run_paper_revision_experiments.py `
  --campaign all --stage full `
  --design data\manifests\paper_revision_experiment_design.json `
  --region data\regions\goseong_mobilization.yaml `
  --cache data\cache\goseong_nodelink_road.graphml `
  --overrides data\parameters\road_class_overrides.csv `
  --scenarios data\scenarios\goseong_disruption_scenarios.csv `
  --output-root results\paper_revision_top10_corridor_v4_20260721

.\.venv\Scripts\python scripts\analyze_paper_revision_results.py `
  --stage full `
  --design-path data\manifests\paper_revision_experiment_design.json `
  --output-root results\paper_revision_top10_corridor_v4_20260721
```

Campaign checkpoints make the full run resumable. Do not use `--no-resume` unless a clean isolated
output root is intended.

### 8.3 Legacy pilot full experiment
```powershell
.\.venv\Scripts\python scripts\run_pilot_experiments.py --engineering-only --full `
  --region-path            data/regions/goseong_mobilization.yaml `
  --cache-path             data/cache/goseong_nodelink_road.graphml `
  --road-class-overrides-path data/parameters/road_class_overrides.csv `
  --design-path            data/manifests/goseong_experiment_design.json `
  --scenarios-path         data/scenarios/goseong_disruption_scenarios.csv `
  --output-dir             results/realworld_pilot_nodelink
```
`--full` selects the `full_pilot` profile (writes `pilot_full_results.csv` /
`pilot_full_summary.csv` / `pilot_full_manifest.json`). `--road-class-overrides-path` is **required**
for Goseong. `--engineering-only` bypasses the pending-source gate for non-sample profiles (labels
rows/manifest; no numeric effect). Other profile flags: `--sample` / `--staged` / `--multi-corridor` /
`--multi-corridor-full` / `--full-graph`.

### 8.4 After a legacy pilot re-run, refresh in order
```powershell
.\.venv\Scripts\python scripts\regenerate_truth_table.py --source results/realworld_pilot_nodelink/pilot_full_summary.csv
.\.venv\Scripts\python scripts\generate_phase23_oracle.py        # byte-identity oracle guard
.\.venv\Scripts\python scripts/run_bpr_noop_sweep.py             # A2 BPR no-op proof
.\.venv\Scripts\python scripts/audit_claim_language.py --fail-on-blockers   # claim guard
.\.venv\Scripts\python generate_report.py                        # report_draft.md -> report.docx
```
`regenerate_truth_table.py` re-freezes `data/validation/summary_truth_table.csv` +
`summary_truth_manifest.json` (current truth SHA `68804701…`, 483 rows, `cross_product_matches=true`,
`source_sha256` of `pilot_full_summary.csv`).

### 8.5 If the network cache is missing (fresh checkout)
The 475 MB `data/cache/goseong_nodelink_road.graphml` is gitignored. Rebuild from the SHP under
`data-collections/` (gitignored, ~3 GB): `build_goseong_nodelink_cache.py` → `build_vds_override.py`
→ `apply_road_overrides_to_cache.py`. Verify the rebuilt cache against the committed manifest's
`graphml_sha256` (`ef96e6a4…`).

---

## 9. Tests & verification

Tests are **directly executable** (each `tests/test_*.py` has `if __name__ == "__main__"`); the project
deliberately does **not** depend on pytest.

```powershell
.\.venv\Scripts\python tests\test_realworld_disruption_scenarios.py   # scenario parsing + segment rows
.\.venv\Scripts\python tests\test_realworld_pilot_experiments.py      # runner logic
.\.venv\Scripts\python tests\test_composable_service_pipeline.py      # oracle byte-identity (~11 min, 972k-edge graph)
.\.venv\Scripts\python tests\test_revision_analysis.py
.\.venv\Scripts\python tests\test_analyze_paper_revision_results.py
.\.venv\Scripts\python tests\test_update_revision_manuscript.py
Get-ChildItem tests\test_*.py | ForEach-Object { .\.venv\Scripts\python $_.FullName }
```

Current full-loop evidence (2026-07-21): 52 of 53 directly executable test files pass, including the
oracle. One legacy artifact-invalidation test expects nonempty `_archive` candidates that are absent
because those paths are already deleted in the working tree; do not recreate or alter those user-owned
deletions merely to satisfy that unrelated assertion.
Note: `test_composable_service_pipeline.py` is the slow one (~11 min cold on the 972k-edge graph) — run
it standalone with a long timeout, not in a tight batch.

After changing engine/fleet/KPI/network/disruption semantics: `compileall` → run all `tests\test_*.py`
→ confirm the legacy oracle remains bit-identical → run the current paper campaigns → run the paper
analyzer → rebuild figures and manuscript. Treat earlier paper result roots as stale.

---

## 10. Constraints (non-negotiable)

- **Claim discipline.** `final_study_ready=false`; formal acceptance is 0/12 by design until a human
  reviewer signs off. Describe outputs as "public-data-based conditional scenario simulation",
  "decision-support", or "sensitivity" — never
  "operational", "forecast", "calibrated", "validated", "final-ready", or "optimal route". Korean
  "검증" is a reserved tripwire. Enforced by `scripts/audit_claim_language.py`.
- **Security.** NEVER use real unit coordinates, OOB lines, or movement schedules — public
  administrative centroids / public transport networks / official doctrine only. The V-World API key is
  a **credential** — must not be committed or hardcoded; store in `.env` (gitignored).
- **Offline by default.** No live OSM/Overpass/data.go.kr calls in tests or the default run path. The
  network cache was built once; live extraction is opt-in only.
- **Deterministic within-scenario.** `force_deterministic=True`; variance is across seeds only.
  CRN pairing: `bus_only` and `baseline_multimodal` (and paired policies) run under the same seed
  (block 3101–3130); separate arrival + failure RNG streams per seed.
- **Windows + long paths.** Short checkout paths and `core.longpaths=true`; PowerShell-first.

---

## 11. Deliverable context

Current research target: **KIIE (한국경영공학회)** paper. AI/ML is **out of scope** for this path.

Active deliverables that wrap the simulator:
- `paper/KIIE_투고논문.docx` (Korean manuscript with figures 1–6).
- `paper/paper_draft.md` (evidence-synchronized English source summary).
- `paper/_build/revision_content_plan_v4.json` (hash-pinned DOCX content plan).
- `paper/figures/captions.md` (current captions).
- `report_draft.md` → `report.docx` (Korean supporting report, via `generate_report.py`).
- `docs/project_overview.md` (Korean project overview), `docs/experiment_design_v2.md`,
  `docs/claim_language_guard.md`.

Earlier targets are **archived** in `_archive/` (preserved, not part of the current build): the 2026
국방AI 경연대회 submission (`국방AI_활용_아이디어_경연대회/`, `web_demo/`), and the KCI/한국군사학논집 redesign
(`kci_redesign/`, `previous-kci/`).

---

## 12. Environment, conventions & git

- **Platform:** Windows 11, PowerShell-first. Python 3.11 via local venv.
- **Remote:** `https://github.com/hyunjun1121/transport-system-sim.git`
- **Current branch:** `wartime-bpr-targeting-fix` (default/main = `main`).
- **Conventions:** code comments/docstrings in English; report files (`report_draft.md`, `report.docx`)
  in Korean; UTF-8 everywhere; no emojis unless requested; keep changes minimal; do not refactor beyond
  what was asked. After realworld-module changes, re-confirm the oracle stays bit-identical
  (`generate_phase23_oracle.py` + `test_composable_service_pipeline.py`).
- **Commit/push/tag only on explicit request.** If on the default branch, branch first. Commit identity:
  `git config user.name "hyunjun1121"` / `git config user.email "hyunjun1121@users.noreply.github.com".
