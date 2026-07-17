# AGENTS.md — Transport System Simulation

> **Wartime reserve-force (전시 동원예비군) mobilization transport micro-simulation.**
> Active case study: **Songpa → Gangwon Goseong (22nd Infantry Division area)**, ~1,000 mobilized
> reservists. Compares a **bus-only** alternative against a **rail-bus multimodal** alternative under
> identical wartime disruption conditions.
>
> **Decision-support / quasi-real sensitivity analysis only** — explicitly NOT an operational route
> plan, a calibrated forecast, or a field-validated result. `final_study_ready=false` by design.

This document describes **only the current canonical experiment**: the 1000-pax wartime re-run on the
Korean **표준노드링크** (national node-link) road network, completed 2026-07-17. Prior experiment
iterations (abstract-network Phase 1/2, 24-pax fixture runs, OSM-source runs, acceptance-scaffolding
gates) have been removed from this file; consult git history for them. Everything below is the setup,
data provenance, methodology, and headline results of *this* experiment.

The authoritative output artifact is
`results/realworld_pilot_nodelink/pilot_full_summary.csv` (483 summary rows) backed by
`pilot_full_results.csv` (14,490 raw rows) and `pilot_full_manifest.json` (full provenance + hashes).

---

## 1. What is being compared

Two transport alternatives move **~1,000 reservists** from assembly zone **A** (Songpa, Olympic Park)
to destination zone **D** (Goseong, 22nd Infantry Division area) over a **24-hour (1440 min) window**:

- **bus_only** — direct road transport A → D over the road network.
- **baseline_multimodal** — shuttle A → S (Cheongnyangni Station) → rail S → R (Gangneung Station,
  KTX-Eum chartered nonstop) → last-mile bus R → D.

Both alternatives run under the **same disruption scenario** and the **same common-random-number seed
block (seeds 3101–3130)**, so the makespan/completion delta is attributable to transport *structure*,
not noise. The unit of comparison is **makespan (min)** at 1000-pax/24h, because completion rate
saturates at 1.000 nearly everywhere in this regime (see §5).

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
  — the official Korean national road network. This is the **canonical Goseong source** since commit
  `cbb49089` (Phase 2 promotion); the earlier OSM-derived cache (`goseong_corridor_road.graphml`) is a
  documented archived alternative, rebuilt via `scripts/build_goseong_cache.py`.
- **Cache build:** `scripts/build_goseong_nodelink_cache.py` →
  `data/cache/goseong_nodelink_road.graphml` (GraphML).
- **Cache stats (recorded in manifest):** source graph **360,556 nodes / 971,680 edges** (≈972k edges);
  after bus-practical filtering + multi-corridor reduction (top-3 shortest-time corridors per canonical
  leg) → **analysis graph 752 nodes / 1,512 edges**.
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
    base disruption rates.
  - **VDS expressway observations** feed a sensitivity fragment via
    `scripts/build_vds_override.py` (public-data-derived, not calibrated).
- **Speed/capacity evidence aids:** `data/parameters/road_speed_evidence_candidates.csv` (OSM maxspeed),
  `road_capacity_evidence_candidates.csv` (OSM lanes).

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
  - `critical_link` — top-3 road edges by weighted edge betweenness.
  - `access_road` — shortest-path degradation on A→S / A→D; **segment-targeted damage ladder A→S**
    (mild/severe/extreme + ±50% rug).
  - `last_mile` — shortest-path degradation R→D; **segment-targeted damage ladder R→D** (+ ±50% rug).
  - `long_haul` — **segment-targeted damage ladder S→R** (mild/moderate/severe) — the trunk bus-only
    shares; multimodal bypasses by rail.
  - `rail_station_access` — road edges incident to S/R connectors.
  - `spatial_hazard_overlay` — bbox exposure overlays (Tancheon/feeder/last-mile/assembly/transfer).
  - `rail_service` — `goseong_rail_unavailable` (rail_travel_time_multiplier=100), the binary
    assumption-failure stress for A1.

### 2.7 Experiment design
- **File:** `data/manifests/goseong_experiment_design.json`, profile **`full_pilot`**.
- **Matrix:** **23 policies × 25 scenarios × 30 seeds = 17,250 nominal rows.**
- **Executed:** 4 spatial-overlay scenarios select no candidate edges on the 752-node analysis graph
  and are skipped as inapplicable (recorded in `skipped_scenarios`:
  `goseong_spatial_tancheon_corridor`, `goseong_spatial_feeder_east`, `goseong_spatial_lastmile_west`,
  `goseong_transfer_point_blockage`) → **21 executed scenarios × 23 policies × 30 seeds = 14,490 rows**.
- **Policies (23):** the 2 baselines (`bus_only`, `baseline_multimodal`) plus 21 alternatives —
  last-mile redundancy, staggered/adaptive dispatch, increased feeder capacity, rail delay/partial
  unavailability, fleet shortage (stress/severe), congestion ladders (moderate/heavy/severe/peak ×
  bus/multimodal), transfer-stress ladders (mild→extreme), last-mile-capacity ladders.

---

## 3. Wartime assumptions A1–A4 (the core reframe)

The experiment is organized around four explicit wartime assumptions. They are **stated scope
conditions**, not measured properties — and they drive the design (what is modeled vs. abstracted away).

- **A1 — Rail reliability.** Under wartime mobilization, rail is chartered, non-stop, and treated as
  reliable and disruption-immune. Rail gradual-degradation scenarios are **removed**;
  `goseong_rail_unavailable` (×100 travel time) is retained as the binary *assumption-failure* stress.
- **A2 — Civilian traffic ≈ 0.** Directional asymmetry: the mobilization corridor (capital → front)
  runs opposite to civilian evacuation flow, so civilian volume V≈0 on the modeled corridor. At V≈0 the
  BPR congestion term is <2% of free-flow → **BPR is effectively a no-op** (proven via
  `scripts/run_bpr_noop_sweep.py`). Makespan is driven by distance + free-flow speed + disruption, not
  congestion. This is why the congestion ladder and most policy alternatives saturate at CR 1.000.
- **A3 — Military-fixed fleet.** Fleet is fixed at 3 roles × 23 vehicles, military-controlled — not a
  market or civilian-cooptation response.
- **A4 — Doctrinal disruption ladder.** Disruption severity is a planning sensitivity ladder
  (mild/severe/extreme multipliers), stability-checked with ±50% rugs (`_plus50` rows). It represents
  doctrinal hazard gradation, not a forecast of specific real-world damage.

---

## 4. Methodology

### 4.1 CRN paired design
`bus_only` and `baseline_multimodal` (and every paired policy) run under the **same seed** from the
3101–3130 block. The scenario runner derives **separate arrival and failure RNG streams** from each
seed, so paired replications differ only in transport structure. Deltas (Δmakespan) are therefore
attributable to the bus-vs-rail architecture, not stochastic noise.

### 4.2 Deterministic within-scenario; t-CI across seeds
Within a scenario, disruptions are **deterministic** (`force_deterministic=True`); the only variance is
**across the 30 seeds**. Uncertainty is reported as **t-based confidence intervals** (Cornish-Fisher,
df=29 → t≈2.0452) on the per-seed metric distribution. No within-scenario noise parameters are active
by default (`road_noise_sigma` / `turnaround_noise_lambda` are exploratory Morris parameters, default 0).

### 4.3 BPR no-op under A2
At V≈0 the BPR term `1 + α(V/C)^β` collapses toward 1 (delay <2%). So in this wartime regime the
simulator's per-edge travel time is essentially **free-flow t₀ (+ disruption multiplier where applied)**.
This is why (a) completion rate saturates at 1.000 across most of the matrix, and (b) the discriminator
between alternatives is makespan, not completion. Congestion/flow calibration is explicitly a *peacetime*
concern and is downscoped here.

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

### 4.5 Oracle byte-identity guard
`generate_phase23_oracle.py` pins `base_config_sha256` (`454269d0…`) and `runs_sha256` (`16b42655…`).
`test_byte_identity_against_oracle` re-runs 8 frozen specs bit-for-bit (6 baseline bus/multimodal ×
seeds 1101–1103 + 2 road-damage with multiplier=2.0). The oracle guards the **config-level failure
multiplier** on the real-p_fail graph and is **independent of CSV targeting** — so retargeting the
segment damage (§4.4) did **not** require an oracle refreeze. Oracle test stays GREEN.

---

## 5. Headline results (1000-pax, makespan min)

Completion rate (CR) saturates at 1.000 across nearly the entire matrix at 1000-pax/24h, so **makespan
is the discriminator**. Two findings reframe the paper's emphasis:

1. **Baseline flip** — bus-only is **~81 min faster** than multimodal at baseline (283 vs 364 min). The
   24h window + 23-vehicle fleet lets direct road delivery beat rail's fixed overhead (114 min leg +
   dispatch interval + transfer). Multimodal's advantage is **conditional**, not baseline.
2. **Completion saturation** — CR ≈ 1.000 everywhere except full-blockage/collapse cases, confirming A2
   (V≈0 → no congestion-driven completion collapse).

Verified bites (`bus_only` vs `baseline_multimodal`, mean over 30 seeds):

| Scenario | bus CR / MS | multi CR / MS | Reading |
|----------|-------------|---------------|---------|
| no_disruption (baseline) | 1.000 / 283.1 | 1.000 / 363.8 | **bus ~81 min faster** |
| access A→S damage mild/severe/extreme | 1.000 / 285·291·311 | 1.000 / 371·394·464 | multimodal feeder leg cost (bus near-invariant) |
| last-mile R→D damage mild/severe/extreme | 1.000 / 294·329·458 | 1.000 / 395·502·**976** | shared terminal bottleneck; multi extreme 976 |
| long-haul S→R damage mild/severe | 1.000 / 317·**671** | 1.000 / 363.8·363.8 | **rail-substitution**: multi flat, bus→671 |
| critical_link blockage | **0.000** / ∞ | 1.000 / 363.8 | multimodal survives, bus collapses |
| rail_unavailable (×100) | 1.000 / 283.1 | **0.000** / ∞ | multimodal collapses without rail (A1 failure) |
| random_blockage (8 edges) | 0.000 / ∞ | 0.000 / ∞ | both collapse |

**Honest thesis:** bus-only wins the baseline; multimodal is a **conditional hedge** — it shines when
road-specific damage hits a trunk the bus must use but rail bypasses (long-haul S→R, critical-link),
and collapses if the rail-reliability assumption (A1) is removed. The congestion story (A2) is
confirmed but flat (CR saturation). Full per-policy/per-scenario bites live in the summary CSV and in
memory `project-v3-wartime-assumption-design.md`.

---

## 6. Reproduce

Run from repo root on Windows PowerShell with the local venv (`.\.venv\Scripts\python`). The full
re-run is ~2–3 h wall-clock on the 752-node analysis graph.

```powershell
.\.venv\Scripts\python scripts\run_pilot_experiments.py --engineering-only --full `
  --region-path data/regions/goseong_mobilization.yaml `
  --cache-path  data/cache/goseong_nodelink_road.graphml `
  --road-class-overrides-path data/parameters/road_class_overrides.csv `
  --design-path  data/manifests/goseong_experiment_design.json `
  --scenarios-path data/scenarios/goseong_disruption_scenarios.csv `
  --output-dir   results/realworld_pilot_nodelink
```

`--full` selects the `full_pilot` profile (writes `pilot_full_results.csv` / `pilot_full_summary.csv` /
`pilot_full_manifest.json`). `--road-class-overrides-path` is **required** for the Goseong case study.
`--engineering-only` bypasses the pending-source gate for non-sample profiles (labels rows/manifest; no
numeric effect). Other profile flags: `--sample` / `--staged` / `--multi-corridor` /
`--multi-corridor-full` / `--full-graph`.

After a re-run, refresh the truth table:

```powershell
.\.venv\Scripts\python scripts\regenerate_truth_table.py `
  --source results/realworld_pilot_nodelink/pilot_full_summary.csv
```

→ re-freezes `data/validation/summary_truth_table.csv` + `summary_truth_manifest.json`
(current truth SHA `68804701`, 483 rows, `cross_product_matches=true`).

---

## 7. Tests & verification

Tests are **directly executable** (each `tests/test_*.py` has `if __name__ == "__main__"`); the project
deliberately does **not** depend on pytest.

```powershell
.\.venv\Scripts\python tests\test_realworld_disruption_scenarios.py   # 11 checks
.\.venv\Scripts\python tests\test_realworld_pilot_experiments.py      # 19 checks
.\.venv\Scripts\python tests\test_realworld_composable_service.py     # 8 checks (incl. oracle byte-identity)
Get-ChildItem tests\test_*.py | ForEach-Object { .\.venv\Scripts\python $_.FullName }   # all tests
```

Current state (2026-07-17): the three realworld test files above all PASS, including
`test_byte_identity_against_oracle` (8 runs × 27 keys bit-for-bit; cfg `454269d0` / runs `16b42655`).

---

## 8. Constraints (non-negotiable)

- **Claim discipline.** `final_study_ready=false`; formal acceptance is 0/12 by design until a human
  reviewer signs off. Describe outputs as "decision-support", "quasi-real", "sensitivity" — never
  "operational", "forecast", "calibrated", "validated", "final-ready", or "optimal route". Korean
  "검증" is a reserved tripwire. Enforced by `scripts/audit_claim_language.py`.
- **Security.** NEVER use real unit coordinates, OOB lines, or movement schedules — public
  administrative centroids / public transport networks / official doctrine only. The V-World API key is
  a **credential** — must not be committed or hardcoded; store in `.env` (gitignored).
- **Offline by default.** No live OSM/Overpass/data.go.kr calls in tests or the default run path. The
  network cache was built once; live extraction is opt-in only.
- **Deterministic within-scenario.** `force_deterministic=True`; variance is across seeds only.

---

## 9. Environment & conventions

- **Platform:** Windows 11, PowerShell-first. Python 3.11 via local venv:
  `py -3.11 -m venv .venv` then `.\.venv\Scripts\python -m pip install -r requirements.txt`.
  Enable `core.longpaths=true`; keep checkout paths short.
- **Ignore** (reference/scaffold trees, not imported by the sim): `cloned_repo/`,
  `.tmp_intake_list/`, `.tmp_phase4_source_probe/`, `.venv/`.
- **Conventions:** code comments/docstrings in English; report files (`report_draft.md`,
  `report.docx`) in Korean; UTF-8 everywhere; no emojis unless requested; keep changes minimal.

---

## 10. Git

- **Remote:** `https://github.com/hyunjun1121/transport-system-sim.git`
- **Current branch:** `wartime-bpr-targeting-fix` (main = `main`).
- Commit/push/tag **only on explicit request**. If on the default branch, branch first.
- Commit identity: `git config user.name "hyunjun1121"` /
  `git config user.email "hyunjun1121@users.noreply.github.com"` (set locally if commits are needed).
