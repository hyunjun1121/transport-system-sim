# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A **wartime reserve-force (전시 동원예비군) mobilization transport micro-simulation**. The
core value of the project — the thing the rest exists to support — is this: build a
**traffic network**, construct **realistic wartime / contingency scenarios**, and
**simulate** how ~1,000 mobilized reservists move from an assembly zone to a destination
zone, comparing a **bus-only** alternative against a **rail-bus multimodal** alternative
under the same disruption conditions. The active case study is the
**Songpa → Gangwon Goseong (22nd Infantry Division area)** mobilization corridor.

This is a **decision-support / quasi-real research framework**, explicitly NOT an
operational route plan, a calibrated forecast, or "final-study-ready". Keep that framing
in every claim and output (see Constraints).

The repository has two very different layers. Learn to tell them apart before editing:

1. **The simulator** (`src/` core + `src/realworld/` real-world pipeline + `src/experiment/`
   + `src/visualize/` + ML analysis). This is the product.
2. **Acceptance / review-integrity machinery** (`src/realworld/*_acceptance.py`,
   `*_review_packet.py`, `*_decision_packet.py`, and ~90 of the 141 `scripts/`). This is
   research-integrity scaffolding (formal gate closure, evidence provenance, claim-boundary
   guards). It does **not** drive the simulation. Do not confuse closing a "gate" with
   running an experiment.

## Run commands

All run from repo root on Windows PowerShell. Python 3.11. Use the local venv:
`.\.venv\Scripts\python ...` (setup: `py -3.11 -m venv .venv` then
`.\.venv\Scripts\python -m pip install -r requirements.txt`).

```powershell
# Core abstract-network simulator (legacy config.yaml network, H/A/S/R/D nodes)
.\.venv\Scripts\python main.py --test       # single paired bus vs multimodal debug
.\.venv\Scripts\python main.py --quick      # reduced grid, R=3, still writes results/
.\.venv\Scripts\python main.py --phase 1    # Phase 1 only (congestion × failure grid)
.\.venv\Scripts\python main.py --phase 2    # Phase 2 only (lateness × policy trade-off)
.\.venv\Scripts\python main.py              # full configured experiment

# Goseong full-scale wartime experiment (the competition case study)
.\.venv\Scripts\python scripts\run_pilot_experiments.py --sample `
  --region-path  data/regions/goseong_mobilization.yaml `
  --cache-path   data/cache/goseong_corridor_road.graphml `
  --design-path  data/manifests/goseong_experiment_design.json `
  --scenarios-path data/scenarios/goseong_disruption_scenarios.csv `
  --output-dir   results/goseong_pilot
# profile flags: --sample | --staged | --multi-corridor | --multi-corridor-full | --full | --full-graph

# ML/AI analysis layer (XGBoost risk classification, KMeans, SHAP, NL summary)
.\.venv\Scripts\python -m pip install -r requirements-ml.txt   # optional, separate from core
.\.venv\Scripts\python scripts\run_ml_analysis.py --input results/goseong_pilot/pilot_sample_results.csv

# Korean report (report_draft.md -> report.docx)
.\.venv\Scripts\python generate_report.py

# Web demo (Palantir-style decision-support UI; React + Vite + Leaflet + Blueprint)
cd web_demo; npm install; npm run dev      # build: npm run build, lint: npm run lint
```

### Tests — direct execution, NO pytest required

Each `tests/test_*.py` is **directly executable** (`if __name__ == "__main__"`). Run one
or batch them; the project deliberately does not depend on pytest.

```powershell
.\.venv\Scripts\python tests\test_scenario.py                    # single test
Get-ChildItem tests\test_*.py | ForEach-Object { .\.venv\Scripts\python $_.FullName }   # all 164
Get-ChildItem tests\test_realworld_*.py | Sort-Object Name | ForEach-Object { .\.venv\Scripts\python $_.FullName }
```

After changing model semantics, refresh outputs in order:
`compileall` → run all `tests\test_*.py` → `main.py --test/--quick/--phase 1/--phase 2` →
`generate_report.py`. If schedule/fleet/KPI/network/failure semantics change, treat
existing `results/` CSV/PNG as stale.

## Architecture — the simulator

**Dataflow (core):**
`config.yaml` → `src/network.build_network()` (NetworkX `DiGraph`) →
`src/scenario.run_scenario(G, config, scenario_type, policy, params, seed)` → KPI `dict`.
Two scenario types share one runner:
- `bus_only`: assembly `A` → road network → destination `D`.
- `multimodal`: `A` → shuttle → rail access `S` → rail → rail egress `R` → last-mile road → `D`.

**Core modules** (`src/`, each a single concern):
- `network.py` — builds the DiGraph from `config.yaml` (nodes, road/rail links, variants).
- `models.py` — BPR link travel time, arrival-delay sampling, legacy failure helpers.
- `policies.py` — `StrictPolicy` (depart on time, arrived pax only) vs
  `GracePolicy(W, theta)` (wait up to max-wait / arrival threshold / capacity).
- `dispatch.py` — queue-based departure-m manifest planning per policy.
- `fleet.py` — `FleetAvailability` (finite fleet, turnaround reuse, optional noise).
- `traffic.py` — `DynamicRoadTraffic`: rolling-window volume → hourly BPR, per-edge entry,
  optional rerouting around blocked edges.
- `disruptions.py` — `sample_edge_disruptions`: per-edge blocked or capacity-reduction state.
- `rail.py` / `transfers.py` — fixed-headway rail departure; transfer delay = base + per-passenger.
- `metrics.py` — makespan, `completion_rate`, `censored_count`, `penalized_makespan`,
  unit-consistent resource KPIs (vehicle-min, train-min, pax-min, pax/service-min).
- `scenario.py` — orchestrator; the stable public API everything calls.

**Experiment layer** (`src/experiment/`):
- `doe.py` — Phase 1 grid (`congestion_scale.levels` × `failure_rate.levels`) and Phase 2
  grid (`lateness.sigma_levels` × policies).
- `runner.py` — **CRN (common random numbers) paired runner**: bus-only and multimodal run
  under the **same seed** so deltas are attributable to transport structure, not noise.
- `analysis.py` — confidence intervals, break-even search, Phase 1 summaries.
- `visualize/plots.py` — delta heatmap, success-rate, Pareto, break-even line.

**Real-world pipeline** (`src/realworld/`) converts an OSM-derived road graph into the
simulator contract and runs quasi-real experiments:
- `osm_network.py` — optional/lazy OSMnx bbox extraction + GraphML cache load/save. Offline
  by default; tests use cached `.graphml` or synthetic fixtures.
- `attributes.py` / `adapter.py` — normalize OSM edge attrs (`highway`, `maxspeed`, `lanes`,
  `p_fail`) into simulator fields (`t0`, `capacity`, `base_p_fail`, `mode`); filter out
  pedestrian/cycle/service geometries for "bus-practical" routes; snap zones + rail points
  to nearest nodes with connector edges; `build_simulator_graph()` → DiGraph for `run_scenario`.
- `regions.py` / `types.py` — region registry (`RegionSpec`, assembly/destination zones,
  rail access `S` / egress `R`).
- `validation.py` — `assert_graph_ready()` / `validate_graph_readiness()` pre-run checks.
- `disruption_scenarios.py` — loads the **wartime scenario table** (see Domain model).
- `policy_alternatives.py` — policy-variant table (fleet reinforcement, congestion stress,
  transfer stress, rail delay/unavailability, adaptive dispatch).
- `pilot_experiments.py` — the **real-world runner**: joins cache + scenarios + policies +
  design profiles → calls `run_scenario` over CRN seed blocks → writes separated CSV/manifest
  outputs. Named design profiles (`sample` / `staged` / `full` / `multi-corridor` /
  `full-graph`) fix the policy×scenario×seed matrix; the Goseong full profile is
  **23 policies × 23 scenarios × 30 seeds = 15,870 rows**.
- `ml_analysis.py` — the **AI layer**: XGBoost multi-class risk classification
  (label rule 정상/주의/위험/실패위험; how many classes populate depends on the input
  completion distribution), gain feature_importance, **optional** SHAP TreeExplainer
  (requires `shap`; falls back to gain importance if absent), KMeans situation-type
  clustering, and a templated claim-disciplined Korean judgment summary. Driven by
  `scripts/run_ml_analysis.py`.

## Domain model — the wartime scenario

The Goseong region spec (`data/regions/goseong_mobilization.yaml`) and the disruption
scenario table (`data/scenarios/goseong_disruption_scenarios.csv`) ARE the
"전시상황과 유사한 시나리오" the project is built around. Canonical nodes:
`A` Songpa assembly (Olympic Park, ~1000 reservists) → `S` Cheongnyangni Station (rail
access) → rail (KTX-Eum, 114 min, 600 pax/train, 30 min headway) → `R` Gangneung Station
(rail egress) → `D` Goseong Tochon-myeon Hakya-ri destination. Coordinates are public
administrative centroids only — never real facility coordinates.

Disruption scenario families in the CSV (deterministic, `force_deterministic=True`): random
hash-ranked blockage/capacity-reduction, critical-link blockage (edge betweenness),
access-road degradation (`A→S`, `A→D`), last-mile degradation (`R→D`), rail-station-access
road degradation, spatial hazard bbox overlays (Tancheon/feeder/last-mile corridors), rail
service stress (delay / capacity / combined / unavailable severity ladders), and multi-hazard
combos. Each row carries `capacity_factor`, `p_fail_scale`, `max_edges`, rail multipliers,
`evidence_class`, and claim-boundary metadata.

Config semantics worth remembering: `failure_rate.levels` are `p_fail_scale` **multipliers**
(`min(edge_base_p_fail * level, 1.0)`), not absolute probabilities; rail links are
failure-immune by default; `policies.GRACE.W/theta` is the wait/threshold grid; BPR
`alpha=0.36` is a Korean-calibration-direction value (not the US FHWA 0.15 default).

## Constraints and conventions

- **Claim discipline (non-negotiable).** `final_study_ready=false` and formal acceptance is
  `0/12` by design until a human reviewer signs off. Describe outputs as "decision-support",
  "quasi-real", "scaffold", or "sensitivity" — never "operational", "forecast", "calibrated",
  "validated", "final-ready", or "optimal route". A claim-language guard
  (`scripts/audit_claim_language.py`, `final_study_readiness`) enforces this. Templates,
  copied drafts, generated review packets, and smoke runs are **not** acceptance evidence.
- **Offline by default.** Do not make live OSM/Overpass or data.go.kr calls in tests or the
  default path. Live extraction is opt-in via explicit `osmnx` calls or `--source overpass`
  / key-gated rail fetchers. Tests must use cached GraphML or `tests/fixtures/`.
- **Deterministic within-scenario.** Pilot experiments use `force_deterministic=True`; the
  only within-scenario variance sources are optional `road_noise_sigma` /
  `turnaround_noise_lambda` (exploratory Morris parameters, default 0).
- **Windows + long paths.** Short checkout paths (e.g. `C:\tss`) and `core.longpaths=true`
  because `cloned_repo/` snapshots have deep paths. `.editorconfig` and PowerShell-first.
- **Ignore these trees** unless explicitly asked: `cloned_repo/` (public source snapshots of
  osmnx, networkx, UXsim, OR-Tools, SALib, r5py, etc. — references, NOT imported by the sim),
  `.tmp_intake_list/` and `.tmp_phase4_source_probe/` (intake/probe workspaces),
  `.venv/`. They bloat file searches.
- `cloned_repo_manifest.md`, `status.md`, `plan.md`, `high_level_plan.md`,
  `IMPLEMENTATION_PLAN.md`, `agents.md`/`AGENTS.md`, and the 80+ `docs/*.md` are research
  state/audit records — read for context, but they describe scaffold/claim-boundary state,
  not necessarily current code behavior.

## Competition / deliverable context

This work backs the **2026 국방AI 활용 아이디어 경연대회** submission
("AI 기반 전시 동원예비군 수송대안 분석·판단지원 체계", 김현준). Deliverables that wrap the
simulator: the Korean planning doc
(`국방AI_활용_아이디어_경연대회/...공모기획서.md`), `report_draft.md`→`report.docx`
(Korean report), `paper/` (English manuscript scaffold), `kci_redesign/` (한국군사학논집 figure/table
redesign synthesis; the retired `previous-kci/` build scripts are a local archive), and `web_demo/` (Vercel-deployed Palantir-style UI at
mobilization-transport-ai.vercel.app). Phase-1 input re-tuning (road speed/capacity, rail
timing/headway/capacity, assembly delay, fleet) has a stated target of 2026-06-30. Long-term
roadmap (`high_level_plan.md`): FTA/FM/FA fault-tree disruption modeling, multi-corridor
ensembles, field-validation benchmarks, GPU Monte Carlo, RL dispatch policy.
