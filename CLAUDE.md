# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A **wartime reserve-force (전시 동원예비군) mobilization transport micro-simulation**. The
core of the project: build a **traffic network** from official Korean road data, construct
**wartime / contingency disruption scenarios**, and **simulate** how ~1,000 mobilized
reservists move from an assembly zone to a destination zone, comparing a **bus-only**
alternative against a **rail-bus multimodal** alternative under the same disruption
conditions. The active case study is the **Songpa → Gangwon Goseong (22nd Infantry
Division area)** mobilization corridor. The current research target is a **KIIE
(한국경영공학회)** academic paper; AI/ML is out of scope for this path.

This is a **decision-support / quasi-real sensitivity framework**, explicitly NOT an
operational route plan, a calibrated forecast, or "final-study-ready" (`final_study_ready=false`
by design). Keep that framing in every claim and output (see Constraints).

For the full experiment writeup (data provenance, methodology, headline results) see
**`agents.md`** — it is current and authoritative. This file covers how to work in the repo.

## Repository state (post-cleanup, 2026-07-18)

The repo was aggressively decluttered to the current experiment context. Surviving scope:
- `src/realworld/`: **21 .py** — 20 KEEP modules + a slim `__init__.py` (see Architecture).
- `tests/`: **36** directly-executable tests (all PASS; incl. oracle byte-identity).
- `scripts/`: **16** (the run-path + a few data writers).
- `data/`: **52** files (current experiment inputs + truth table only).
- `docs/`: **3** (project_overview, experiment_design_v2, claim_language_guard).

`_archive/` (moved, preserved, not active): `web_demo`, `국방AI_활용_아이디어_경연대회`,
`kci_redesign`, `previous-kci`, `cloned_repo`, `.tmp_intake_list`, `.tmp_phase4_source_probe`,
submission zips, and the OSM-era `realworld_pilot_osm` results. The acceptance/review-packet
machinery, the abstract-network `main.py`/`config.yaml`/`src/experiment`/`src/visualize`,
the AI/ML layer, and the songpa/OSM previous-experiment code were **deleted** (git history:
`44a007c9` snapshot → `cb08c522` r1 → `6600dd3c` r2 → `686c65b6` r3).

**If an older note/memory references `*_acceptance.py`, ~90 `scripts/`, `main.py`, `ml_analysis`,
or `kci_redesign/` as present — it is stale.** Trust `agents.md`, `git log`, and `ls`.

## Run commands

All run from repo root on Windows PowerShell. Python 3.11 via the local venv:
`.\.venv\Scripts\python ...` (setup: `py -3.11 -m venv .venv` then
`.\.venv\Scripts\python -m pip install -r requirements.txt`).

```powershell
# Goseong full-scale wartime experiment (the case study; ~2-3 h wall on the 752-node graph)
.\.venv\Scripts\python scripts\run_pilot_experiments.py --engineering-only --full `
  --region-path            data/regions/goseong_mobilization.yaml `
  --cache-path             data/cache/goseong_nodelink_road.graphml `
  --road-class-overrides-path data/parameters/road_class_overrides.csv `
  --design-path            data/manifests/goseong_experiment_design.json `
  --scenarios-path         data/scenarios/goseong_disruption_scenarios.csv `
  --output-dir             results/realworld_pilot_nodelink
# profile flags: --sample | --staged | --multi-corridor | --multi-corridor-full | --full | --full-graph
# --road-class-overrides-path is REQUIRED for Goseong (else raw HIGHWAY_DEFAULTS fallback).
# --engineering-only bypasses the pending-source gate for non-sample profiles (labels only).

# Refresh outputs after a re-run, in order:
.\.venv\Scripts\python scripts\regenerate_truth_table.py --source results/realworld_pilot_nodelink/pilot_full_summary.csv
.\.venv\Scripts\python scripts\generate_phase23_oracle.py        # byte-identity oracle guard
.\.venv\Scripts\python scripts\run_bpr_noop_sweep.py             # A2 BPR no-op proof
.\.venv\Scripts\python scripts\audit_claim_language.py --fail-on-blockers   # claim guard
.\.venv\Scripts\python generate_report.py                        # report_draft.md -> report.docx

# Network cache rebuild (only if data-collections/ SHP is present; cache is already committed):
.\.venv\Scripts\python scripts\build_goseong_nodelink_cache.py
.\.venv\Scripts\python scripts\build_vds_override.py
.\.venv\Scripts\python scripts\apply_road_overrides_to_cache.py
```

### Tests — direct execution, NO pytest

Each `tests/test_*.py` is **directly executable** (`if __name__ == "__main__"`); the project
deliberately does not depend on pytest.

```powershell
.\.venv\Scripts\python tests\test_scenario.py                    # single test
.\.venv\Scripts\python tests\test_realworld_pilot_experiments.py  # realworld runner test
Get-ChildItem tests\test_*.py | ForEach-Object { .\.venv\Scripts\python $_.FullName }   # all 36
```

Note: `test_composable_service_pipeline.py` (oracle byte-identity, 8 runs on the 972k-edge
graph) takes ~11 min cold — run it standalone with a long timeout, not in a tight batch.

After changing engine/fleet/KPI/network/disruption semantics: `compileall` → run all
`tests\test_*.py` → `generate_phase23_oracle.py` (oracle must stay bit-identical) →
re-run the pilot → `regenerate_truth_table.py` → treat prior `results/` as stale.

## Architecture — the simulator

**Dataflow:**
`data/regions/goseong_mobilization.yaml` + `data/cache/goseong_nodelink_road.graphml` +
`road_class_overrides.csv` → `src/realworld/adapter.build_simulator_graph()` (NetworkX
`DiGraph`) → `src/scenario.run_scenario(G, config, scenario_type, policy, params, seed)` →
KPI `dict`. Two scenario types share one runner:
- `bus_only`: assembly `A` → road network → destination `D`.
- `multimodal`: `A` → shuttle → rail access `S` → rail → rail egress `R` → last-mile road → `D`.

**Core engine** (`src/`, each a single concern):
- `network.py` — builds the DiGraph (now driven by the realworld adapter, not config.yaml).
- `models.py` — BPR link travel time, arrival-delay sampling, failure helpers.
- `policies.py` — `StrictPolicy` (depart on time, arrived pax only) vs `GracePolicy(W, theta)`.
- `dispatch.py` — queue-based departure-manifest planning per policy.
- `fleet.py` — `FleetAvailability` (finite fleet, turnaround reuse, optional noise).
- `traffic.py` — `DynamicRoadTraffic`: rolling-window volume → hourly BPR, per-edge entry,
  optional rerouting around blocked edges.
- `disruptions.py` — `sample_edge_disruptions`: per-edge blocked / capacity-reduction /
  travel-time-multiplier state.
- `rail.py` / `transfers.py` — fixed-headway rail departure; transfer delay = base + per-passenger.
- `metrics.py` — makespan, `completion_rate`, `censored_count`, `penalized_makespan`,
  unit-consistent resource KPIs.
- `scenario.py` — orchestrator; the stable public API everything calls.
- `sim_types.py` — shared immutable records (`ServiceSpec`, `EdgeDisruption`, …).

**Real-world pipeline** (`src/realworld/`, 20 KEEP modules) — converts the official Korean
표준노드링크 road graph into the simulator contract and runs the wartime experiment:
- `nodelink_network.py` — Korean 표준노드링크 SHP → GraphML (the canonical Goseong source).
- `osm_network.py` — GraphML cache load/save (offline; OSM is an archived alternative source).
- `vds_calibration.py` — VDS expressway observations → road-class override fragment.
- `attributes.py` / `adapter.py` — normalize edge attrs (`highway`, `maxspeed`, `lanes`,
  `p_fail`) into simulator fields (`t0`, `capacity`, `base_p_fail`, `mode`); filter
  pedestrian/cycle/service geometries; snap zones + rail points; `build_simulator_graph()`.
- `road_overrides.py` — applies the evidenced per-class speed/capacity/p_fail override table.
- `regions.py` / `types.py` — region registry (`RegionSpec`, assembly/destination zones,
  rail access `S` / egress `R`, public-coordinate policy).
- `validation.py` — `assert_graph_ready()` / `validate_graph_readiness()` pre-run checks.
- `disruption_scenarios.py` — loads the **wartime scenario table** (see Domain model).
- `policy_alternatives.py` — policy-variant table (congestion/transfer/fleet stress, etc.).
- `parameters.py` — shipped parameter tables (speed/capacity/pfail source classes).
- `pilot_experiments.py` — the **runner**: joins cache + scenarios + policies + design
  profiles → `run_scenario` over CRN seed blocks → separated CSV/manifest outputs. Named
  profiles (`sample`/`staged`/`full`/`multi-corridor`/`multi-corridor-full`/`full-graph`)
  fix the policy×scenario×seed matrix; Goseong full = **23 policies × 21 executed scenarios
  × 30 seeds = 14,490 rows** (4 bbox spatial scenarios skip as inapplicable).
- `artifact_invalidation_matrix.py` (+ `manifest_timestamp.py`, `source_artifacts.py`) —
  runtime provenance the runner writes into its manifest (KEEP: `pilot_experiments` imports it).
- `claim_language_guard.py` — lexical claim-boundary guard backing `audit_claim_language.py`.
- `phase_gate_ledger.py`, `plausibility.py` — retained ledger + route-plausibility helpers.

`src/realworld/__init__.py` is **slim**: it imports only the 20 KEEP modules and re-exports
just the package-level names KEEP code uses (`build_simulator_graph`, `load_graphml`,
`load_region_spec`, `PortPointSpec`/`RegionSpec`/…, `pilot_experiments`/`osm_network`
submodule access). Do **not** re-add eager imports of removed modules.

## Domain model — the wartime scenario

The Goseong region spec (`data/regions/goseong_mobilization.yaml`) and the disruption
scenario table (`data/scenarios/goseong_disruption_scenarios.csv`) ARE the
"전시상황과 유사한 시나리오". Canonical nodes: `A` Songpa assembly (Olympic Park, ~1000
reservists) → `S` Cheongnyangni Station → rail (KTX-Eum chartered nonstop, 114 min, 600
pax/train, 30 min dispatch interval) → `R` Gangneung Station → `D` Goseong Tochon-myeon
Hakya-ri. Coordinates are **public administrative centroids / public rail stations only** —
never real unit facility coordinates.

**Wartime assumptions A1–A4** organize the experiment (stated scope conditions, not measured):
- **A1 rail reliability** — rail is chartered/non-stop/reliable and disruption-immune; rail
  gradual-degradation scenarios are removed; `goseong_rail_unavailable` (rail×100) is the
  binary assumption-failure stress.
- **A2 civilian traffic ≈ 0** — directional asymmetry (mobilization corridor runs opposite
  civilian evacuation) → V≈0 → **BPR is a no-op** (delay <2% of free-flow; proven by
  `run_bpr_noop_sweep.py`). Makespan is driven by distance + free-flow + disruption, not
  congestion. BPR α/β calibration is therefore a peacetime concern, downscoped here.
- **A3 military-fixed fleet** — 3 roles × 23 vehicles (45 pax each), not a market response.
- **A4 doctrinal disruption ladder** — mild/severe/extreme multipliers with ±50% stability rugs.

Disruption families in the CSV (deterministic, `force_deterministic=True`): random hash-ranked
blockage/capacity-reduction, critical-link blockage (edge betweenness), access-road
(`A→S`/`A→D`), last-mile (`R→D`), rail-station-access, spatial bbox overlays,
`rail_unavailable`, and **segment-targeted road-damage ladders** (`A→S` access,
`R→D` last-mile, `S→R` long-haul) via a direct-slowdown lever
(`road_travel_time_multiplier` on free-flow `t0`, `capacity_factor=1.0`). Each row carries
`capacity_factor`, `p_fail_scale`, `max_edges`, rail multipliers, `evidence_class`, and
claim-boundary metadata.

**Headline regime (1000-pax/24h):** completion rate saturates at 1.000 nearly everywhere →
**makespan is the discriminator**. Bus-only is the faster baseline (~283 vs ~364 min);
multimodal's advantage is conditional (rail-substitution when road damage hits a trunk the
bus must use but rail bypasses; collapses if A1 is removed). See `agents.md` §5 for the table.

## Constraints and conventions

- **Claim discipline (non-negotiable).** `final_study_ready=false`; describe outputs as
  "decision-support", "quasi-real", or "sensitivity" — never "operational", "forecast",
  "calibrated", "validated", "final-ready", or "optimal route". Korean "검증" is a reserved
  tripwire. Enforced by `scripts/audit_claim_language.py`. Smoke runs and generated artifacts
  are not acceptance evidence.
- **Security.** NEVER use real unit coordinates, OOB lines, or movement schedules — public
  administrative centroids / public transport networks / official doctrine only. The V-World
  API key is a **credential** — never commit/hardcode; store in `.env` (gitignored).
- **Offline by default.** No live OSM/Overpass/data.go.kr calls in tests or the default path.
  The network cache is built once and committed; live extraction is opt-in only.
- **Deterministic within-scenario.** `force_deterministic=True`; the only variance is across
  the 30 CRN seeds (Cornish-Fisher t-CI, df=29). `road_noise_sigma`/`turnaround_noise_lambda`
  are exploratory Morris parameters, default 0.
- **CRN pairing.** `bus_only` and `baseline_multimodal` (and paired policies) run under the
  same seed (block 3101–3130); separate arrival + failure RNG streams per seed.
- **Windows + long paths.** Short checkout paths and `core.longpaths=true`; `.editorconfig`
  and PowerShell-first.
- **Ignore these trees** unless explicitly asked: `_archive/` (archived deliverables +
  `cloned_repo` reference snapshots — large, not active), `data-collections/` (3 GB gitignored
  표준노드링크 SHP; regenerable, the `.graphml` cache is already committed), `.venv/`.

## Deliverable context

Current research target: **KIIE (한국경영공학회)** paper. Active deliverables that wrap the
simulator: `report_draft.md` → `report.docx` (Korean report, via `generate_report.py`) and
`paper/paper_draft.md` (English manuscript). AI/ML is dropped from this path.

Earlier targets are **archived** in `_archive/`: the 2026 국방AI 경연대회 submission
(`국방AI_활용_아이디어_경연대회/`, `web_demo/`), and the KCI/한국군사학논집 redesign
(`kci_redesign/`, `previous-kci/`). They are preserved but not part of the current build.

## Conventions

- Code comments/docstrings in English; report files (`report_draft.md`, `report.docx`) in Korean.
- Keep text files UTF-8; no emojis unless requested.
- Keep changes minimal; do not refactor beyond what was asked.
- After realworld-module changes, re-confirm the oracle stays bit-identical
  (`generate_phase23_oracle.py` + `test_composable_service_pipeline.py`).
