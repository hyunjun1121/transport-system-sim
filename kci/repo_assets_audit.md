# KCI Repo Assets Audit — What to Bring into `./kci/`

**Workspace folder:** `./kci/`
**Companion document:** `kci/research_plan.md` (research scope, framing, methodology)
**Document role:** File-by-file decision sheet for everything in the upstream repo, used as input to a later `kci/plan.md` implementation plan.
**Status:** Draft v0.1 (2026-05-11). Synthesized from three parallel Opus sub-agent audits run on 2026-05-11.

---

## 0. How to read this document

Each entry has one of four decisions:

- **COPY** — bring into `./kci/` as-is. Essential for the KCI study.
- **ADAPT** — bring into `./kci/` with named modifications.
- **EXCLUDE** — leave in the upstream repo. Not needed for KCI scope (typically because it belongs to the deferred 12-blocker formal-acceptance / real-world calibration track that the KCI study explicitly does not pursue).
- **REFERENCE-ONLY** — leave in the upstream repo, but cite from `kci/` documents. Useful provenance or background.

The KCI scope (per `kci/research_plan.md`) is a *virtual* major-arterial Songpa corridor, IE-methodology positioning, and a deliberate deferral of all real-world calibration / formal-acceptance gates. Most of the upstream calibration scaffolding is therefore EXCLUDE for this submission, not because it is low quality, but because it is for a different paper.

---

## 1. Core simulation code (`src/`, top-level entry points)

### Simulator core (`src/*.py`)

| Path | Decision | Rationale |
|---|---|---|
| `src/__init__.py` | COPY | Package marker. |
| `src/network.py` | COPY | Pure abstract DiGraph builder + variant resolver — the H/A/S/R/D contract used by every scenario. No external deps. |
| `src/scenario.py` | COPY | Core simulator: bus-only and multimodal runners, dynamic BPR routing, fleet / rail / transfer wiring. Sibling-only imports. |
| `src/dispatch.py` | COPY | Queue-based passenger dispatch helper used by both scenarios. |
| `src/disruptions.py` | COPY | Structured edge-disruption sampling (blocked + capacity_reduction); central to the KCI failure-rate sweep. |
| `src/fleet.py` | COPY | Finite-fleet availability — required for both bus and last-mile resource accounting. |
| `src/metrics.py` | COPY | Censoring-aware KPIs (penalized_makespan, censored_count, resource efficiency) — methodological pillar. |
| `src/models.py` | COPY | BPR + lognormal arrival delays + legacy link-failure sampler. |
| `src/policies.py` | COPY | STRICT / GRACE policies — required for Phase 2. |
| `src/rail.py` | COPY | Fixed-headway rail dispatch helpers used by multimodal scenario. |
| `src/sim_types.py` | COPY | Shared records (`Passenger`, `VehicleTrip`, `EdgeDisruption`, validators) imported across the package. |
| `src/traffic.py` | COPY | `DynamicRoadTraffic` — rolling-window volume, BPR-at-departure-time. Core simulator. |
| `src/transfers.py` | COPY | Transfer-delay computation for the multimodal hub. |

### Experiment runner (`src/experiment/`)

| Path | Decision | Rationale |
|---|---|---|
| `src/experiment/__init__.py` | COPY | Package marker. |
| `src/experiment/runner.py` | COPY | Paired-CRN runner (Phase 1 + Phase 2) — methodological pillar. |
| `src/experiment/doe.py` | COPY | DoE grid generation for both phases. |
| `src/experiment/analysis.py` | COPY | Confidence intervals, break-even interpolation, Phase 1 summarization — drives the KCI tables. |

### Visualization (`src/visualize/`)

| Path | Decision | Rationale |
|---|---|---|
| `src/visualize/__init__.py` | COPY | Package marker. |
| `src/visualize/plots.py` | ADAPT | Plotting works as-is (delta heatmap, success-rate, Pareto, breakeven). Add Korean axis labels / titles for KCI figures and keep English fallbacks. |

### Real-world adapter subset (`src/realworld/`)

The `src/realworld/` package is large (~110 files). The KCI study uses only the OSM-extraction surface and intentionally drops the calibration / acceptance / evidence machinery that drives the deferred 12 blocked gates. **Critical: the current `src/realworld/__init__.py` eagerly re-exports almost the entire package; copying it as-is would force every excluded module to import. A slim init is required.**

| Path | Decision | Rationale |
|---|---|---|
| `src/realworld/__init__.py` | ADAPT | Replace with a slim init that re-exports only `osm_network`, `adapter`, `attributes`, `zones`, `regions`, `types`, `disruption_scenarios`, `validation`, and (optionally) `accessibility`, `sensitivity`. |
| `src/realworld/osm_network.py` | COPY | OSMnx bbox extraction + GraphML save / load + normalize. Required for the major-arterial extraction. No internal package deps. |
| `src/realworld/adapter.py` | ADAPT | OSM → simulator-graph adapter (collapses parallel edges, snaps zones, builds H/A/S/R/D). **Filter `routeable_highway_classes` down to `{motorway, motorway_link, trunk, trunk_link, primary, primary_link}` (and possibly `secondary` — open question 1 in `research_plan.md`)** to enforce major-arterial-only. |
| `src/realworld/attributes.py` | ADAPT | `HIGHWAY_DEFAULTS` provides speed / capacity / p_fail proxies. Keep entries for major-arterial classes only; document that values are uncalibrated planning proxies (consistent with KCI deferral of calibration). |
| `src/realworld/zones.py` | COPY | Nearest-node snapping + connector-edge construction. No extra deps. |
| `src/realworld/regions.py` | COPY | Region-spec loader / registry. Tiny, no deps. |
| `src/realworld/types.py` | COPY | `RegionSpec`, `ZoneSpec`, `RailPointSpec` dataclasses + validators. Tiny. |
| `src/realworld/validation.py` | COPY | `assert_graph_ready` readiness checks. Pure stdlib. Guards adapter output before simulation. |
| `src/realworld/disruption_scenarios.py` | ADAPT | Loads structured disruption-scenario CSV → simulator `EdgeDisruption` map. Trim the accompanying CSV to KCI-relevant arterial-blockage cases; remap any references to the old destination ID `D` to the new reserve-assembly ID. |
| `src/realworld/accessibility.py` | ADAPT | Route-fragility / critical-edge diagnostics on the adapted graph. Useful for the KCI sensitivity narrative; keep `claim_scope` tagging that already labels it as scaffold. |
| `src/realworld/sensitivity.py` | ADAPT | SALib-compatible problem framing + OAT screening fallback. Morris is a stated KCI methodological pillar — copy this and **rewrite to call `src.scenario.run_scenario` directly** rather than going through `pilot_experiments` / `policy_alternatives`, otherwise it drags in the entire excluded pilot stack. |
| `src/realworld/plausibility.py` | REFERENCE-ONLY | Sanity checks against external benchmarks; adjacent to deferred validation work. Keep upstream link from `kci/` docs. |
| `src/realworld/README.md` | REFERENCE-ONLY | Documents the original pilot scaffold status; link from a `kci/` README. |
| `src/realworld/pilot_experiments.py`, `policy_alternatives.py`, `road_overrides.py`, `parameters.py`, `parameter_audit.py`, all `parameter_*.py` | EXCLUDE | Calibration / parameter-evidence loaders and audit packets. Deferred. |
| `src/realworld/acceptance_*.py` (~10 files) | EXCLUDE | Formal-acceptance scaffold (records, orchestration, blocker queue, templates, guards, package, pre-review). Deferred. |
| `src/realworld/validation_*.py`, `formal_*`, `final_*`, `manuscript_*`, `publication_*`, `provenance_*`, `reproducibility_*`, `goal_completion_audit.py`, `tracked_artifact_audit.py`, `agent_review_path_audit.py`, `clean_checkout_smoke.py`, `manifest_timestamp.py`, `figure_table_review_packet.py`, `integrated_evidence_review_packet.py`, `claim_alignment_review_packet.py`, `experiment_acceptance.py`, `experiment_design_decision_packet.py`, `experiment_package_review_packet.py`, `experiment_strategy_readiness_packet.py`, `full_graph_runtime_readiness_packet.py` | EXCLUDE | Decision / review / acceptance packets and freshness / audit machinery for the deferred formal-acceptance gates. Not simulator code. |
| `src/realworld/graph_scale_*.py` (8 files) | EXCLUDE | Reduced-vs-full corridor decision worksheets. KCI uses one explicit virtual major-arterial network. |
| `src/realworld/source_*.py`, `osrm_snapshot_manifest.py`, `osm_graph_snapshot_review_packet.py` | EXCLUDE | Source-provenance and license / URL review packets. Calibration scaffolding. |
| `src/realworld/road_*.py` (evidence / diagnostics / override / audit packets) | EXCLUDE | Road-evidence acceptance scaffolding. Deferred. |
| `src/realworld/rail_*.py` (evidence, GTFS, timetable, station, shortest-path, fetch-readiness packets, ~12 files) | EXCLUDE | Rail GTFS / KTDB / Metro9 calibration sources and review packets. KCI uses the abstract fixed-headway proxy only. |
| `src/realworld/ktdb_gtfs_source.py`, `metro9_capacity_source.py` | EXCLUDE | External Korean rail data ingestion for calibration. Deferred. |
| `src/realworld/transfer_evidence_review_packet.py` | EXCLUDE | Transfer-time evidence packet. Deferred. |
| `src/realworld/pilot_*.py` (statistics, figures, acceptance, region_decision_packet, privacy_review_packet) | EXCLUDE | Pilot-runner companion files. Pilot runner itself is excluded. |
| `src/realworld/sensitivity_*.py` (acceptance, diagnostics, index_review_packet, method_decision_packet, review_packet, strategy_readiness_packet) | EXCLUDE | Acceptance / review packets around `sensitivity.py`. The core is adapted; the surrounding gate packets are deferred. |
| `src/realworld/route_road_evidence_exposure.py` | EXCLUDE | Route-level calibration evidence reporting. Deferred. |

### Top-level entry points

| Path | Decision | Rationale |
|---|---|---|
| `main.py` | ADAPT | Keep CLI entry but rewire imports to `kci.src.*` (or run with `kci/` on `sys.path`). Strip references to deferred experiment context if any are present; keep Phase 1 / Phase 2 / `--quick` paths. |
| `config.yaml` | ADAPT | Replace the abstract H/A/S/R/D + D1/D2 baseline with the Songpa major-arterial virtual network (either inlined `road_links` or loaded from the adapted region YAML). Tune `personnel.total = 1000`, fleet sizes, and `failure.*` for the reserve-mobilization framing. CRN, BPR, Phase 1 / Phase 2 grids stay. |
| `requirements.txt` | ADAPT | Keep `simpy`, `networkx`, `numpy`, `pandas`, `PyYAML`, `matplotlib`, `seaborn`, `SALib`. Drop `python-docx` if `generate_report.py` is excluded. Add `osmnx` (currently optional / lazy in `osm_network.py`) since major-arterial extraction is in scope. |
| `generate_report.py` | EXCLUDE | Builds the Korean `report.docx` from `report_draft.md` for the prior decision-support deliverable. KCI manuscript will be authored separately. |
| `generate_report_figures.py` | ADAPT | Korean-labeled summary figures (figure1 / 2 / 3) are exactly the executive-style plots a KCI paper benefits from; rewrite captions for IE / reserve-mobilization framing and rebind to KCI results CSVs. Drop figure 0 pipeline overview unless reused. |

### Critical dependencies (carry-over from sub-agent A)

- `adapter.py` requires `attributes.py`, `regions.py`, `types.py`, `zones.py` co-located (relative imports). `zones.py` requires `regions.py` and `types.py`; `regions.py` requires `types.py`.
- `disruption_scenarios.py` imports `src.sim_types.EdgeDisruption` — the copy under `kci/src/` must keep the `src.sim_types` import path intact. **Recommended: keep the `src.` package name inside `kci/` (i.e. `kci/src/realworld/...`) and run with `kci/` on `sys.path`** to avoid touching every import.
- `sensitivity.py` (if kept) currently imports `pilot_experiments`, `policy_alternatives`, `disruption_scenarios` — must be rewritten to call `src.scenario.run_scenario` directly with KCI configs, otherwise it drags in the entire excluded pilot stack.
- The slim `src/realworld/__init__.py` rewrite is **REQUIRED** — the current init eagerly imports ~100 modules; any `from kci.src.realworld import …` would force every excluded module to load and fail.
- `osm_network.extract_bbox_graph` lazy-imports `osmnx`. If you actually run the Songpa extraction, `osmnx` must be in requirements; cached GraphML reads work without it.
- Both `main.py` and the experiment runner depend on `src.network.build_network`. To use the OSM-extracted Songpa network, either (a) pre-compute it to a config-compatible `road_links` list and put it in `config.yaml`, or (b) wire `main.py` to call `realworld.adapter.build_simulator_graph` and bypass `network.build_network` for the KCI variant. **Decision required (see open question A).**

---

## 2. Data, results, scripts, tests, schemas

### `data/cache/`

| Path | Decision | Rationale |
|---|---|---|
| `data/cache/pilot_region_road.graphml` | COPY | Foundational OSM Songpa road graph; input to the major-arterial filter. |
| `data/cache/pilot_region_road_manifest.json` | COPY | Provenance / checksum for the graphml; needed to document filtering input. |

### `data/regions/`

| Path | Decision | Rationale |
|---|---|---|
| `data/regions/pilot_region.yaml` | ADAPT | Replace `destination_zones[D]` with a reserve-assembly point; rename region (e.g. `songpa_arterial_kci`); drop `public_demo` framing; keep bbox + rail access / egress + cache_path. |

### `data/scenarios/`

| Path | Decision | Rationale |
|---|---|---|
| `data/scenarios/disruption_scenarios.csv` | ADAPT | Keep random / critical-link / access-road / last-mile families; remap `D` rows to the new reserve-assembly point; drop scenarios outside the arterial corridor scope. |
| `data/scenarios/policy_alternatives.csv` | COPY | Defines bus-only vs multimodal comparators and stress policies. Central to the IE comparison. |
| `data/scenarios/sensitivity_design.csv` | COPY | Morris design parameter table. Methodological asset. |

### `data/parameters/` — calibration evidence (mostly EXCLUDE)

| Path | Decision | Rationale |
|---|---|---|
| `data/parameters/fleet_assumptions.csv` | ADAPT | Strip `source_url_or_citation` empirical claims; keep parameter values + uncertainty ranges; relabel `source_class` as `expert_assumption_virtual_study`. |
| `data/parameters/rail_assumptions.csv` | ADAPT | Same treatment — retain headway / travel-time / capacity assumptions but drop external URLs and rephrase as virtual-study assumptions. |
| `data/parameters/parameter_sources.csv` | EXCLUDE | Real-world calibration source-tracking table. |
| `data/parameters/parameter_acceptance_template.csv` | EXCLUDE | Formal-acceptance gate scaffold. Deferred. |
| `data/parameters/parameter_evidence_*` (priority / review / source_request) | EXCLUDE | Calibration-evidence packets. Deferred. |
| `data/parameters/parameter_source_decision_*`, `parameter_source_readiness_*` | EXCLUDE | Formal source-decision artifacts. |
| `data/parameters/rail_evidence_*`, `rail_service_evidence.csv`, `rail_station_bindings.csv` | EXCLUDE | Real Seoul rail evidence packets. |
| `data/parameters/road_capacity_evidence_*`, `road_speed_evidence_*`, `road_class_overrides_draft.csv`, `road_evidence_review_*` | EXCLUDE | Road real-data calibration packets. Deferred. |
| `data/parameters/transfer_evidence_review_*` | EXCLUDE | Transfer-time evidence packet. Deferred. |

### `data/rail/`, `data/road/`

| Path | Decision | Rationale |
|---|---|---|
| `data/rail/*` (KTDB / Metro9 / station-binding / timing-source packets) | EXCLUDE | Pure real-world rail-data sourcing artifacts. Not used by the virtual fixed-headway model. |
| `data/road/*` (evidence / source / readiness manifests + packets) | EXCLUDE | Road-data sourcing scaffolds. Deferred. |

### `data/manifests/`

| Path | Decision | Rationale |
|---|---|---|
| `data/manifests/pilot_experiment_design.json` | COPY | Cached pilot-experiment design profile consumed by the runner. |
| `data/manifests/reproducibility_manifest.json` | COPY | Reproducibility hash chain — IE methodology contribution. |
| `data/manifests/source_provenance_manifest.json` | REFERENCE-ONLY | Useful provenance index but oriented at real-data sourcing. |
| `data/manifests/acceptance_templates/*` (9), `agent_reviews/*` (12), `draft_acceptance/*` (13) | EXCLUDE | Formal-acceptance / sub-agent acceptance / pre-review templates. Deferred. |
| `data/manifests/{claim_alignment, experiment_design_decision, experiment_package_review, experiment_strategy_readiness, figure_table_review, final_audit_decision, manuscript_report_decision, pilot_privacy_review, pilot_region_decision, ...}_manifest+packet` | EXCLUDE | All formal-acceptance / review packets and audit JSONs. Deferred. |
| `data/manifests/source_context_cache_*`, `source_license_review_*`, `source_provenance_decision/priority_*`, `source_url_*` | EXCLUDE | Source-licensing / URL audit packets. Deferred. |
| `data/manifests/formal_acceptance_*`, `formal_evidence_path_audit.json`, `publication_readiness_audit.json`, `current_goal_completion_audit.json`, `agent_review_path_audit.json`, `acceptance_*` | EXCLUDE | Formal-acceptance machinery (12 blocked gates). Deferred. |

### `data/validation/`

| Path | Decision | Rationale |
|---|---|---|
| `data/validation/accessibility_loss.csv` (+ `_summary.md`) | COPY | Diagnostic produced by `run_accessibility_loss_analysis.py`; useful as IE-methodology illustration. |
| `data/validation/reproducibility_smoke_log.jsonl`, `reproducibility_smoke_manifest.json`, `clean_checkout_reproducibility_smoke_*` | COPY | Reproducibility evidence for the IE method paper. |
| `data/validation/external_route_benchmarks*.csv`, `osrm_route_*`, `route_plausibility.csv`, `canonical_route_road_evidence_exposure*` | EXCLUDE | OSRM / external benchmark calibration. Deferred. |
| `data/validation/full_graph_*`, `graph_scale_*` (12 files) | EXCLUDE | Full-graph runtime / scale review packets. KCI uses the arterial subset. |
| `data/validation/sensitivity_*` (review / decision / strategy packets) | EXCLUDE | Acceptance scaffolds (the actual sensitivity *results* live under `results/`). |
| `data/validation/validation_*`, `integrated_evidence_review_*`, `tracked_artifact_audit*`, `osm_graph_snapshot_review_*`, `reproducibility_review/decision_*` | EXCLUDE | Acceptance-gate review packets. Deferred. |

### `results/`

The KCI study will **regenerate** all results on the new arterial corridor. Existing CSVs and figures are kept as REFERENCE-ONLY only.

| Path | Decision | Rationale |
|---|---|---|
| `results/phase1_results.csv`, `phase1_summary.csv`, `phase1_ci.csv`, `phase2_results.csv`, `phase2_ci.csv` | REFERENCE-ONLY | Abstract-network legacy outputs. |
| `results/breakeven_line.png`, `delta_heatmap.png`, `policy_pareto.png`, `success_rate_comparison.png` | REFERENCE-ONLY | Legacy figures from the abstract network. |
| `results/report_figures/figure{0..3}_*.png` | REFERENCE-ONLY | Pre-existing report figures. |
| `results/realworld_pilot/pilot_full_*`, `pilot_sample_*`, `pilot_staged_*`, `pilot_multi_corridor_*`, `morris_*`, `sensitivity_*` | REFERENCE-ONLY | Songpa pilot outputs; useful provenance / sanity comparison. |
| `results/realworld_pilot/figures/*.png` (6 figures), `tables/*` | REFERENCE-ONLY | Guides the KCI figure / table plan. |
| `results/realworld_pilot/pilot_result_manifest.json` | REFERENCE-ONLY | Index of pilot outputs. |

### `scripts/`

| Path | Decision | Rationale |
|---|---|---|
| `scripts/build_pilot_cache.py` | ADAPT | Add an arterial-filter mode (e.g. `--filter major_arterials`) that emits the corridor GraphML from the existing GraphML. |
| `scripts/run_pilot_experiments.py` | COPY | Core runner. |
| `scripts/run_pilot_smoke.py` | COPY | Fast offline smoke for CI on the new corridor. |
| `scripts/run_sensitivity.py` | COPY | Morris sensitivity runner — methodological centerpiece. |
| `scripts/make_pilot_figures.py` | ADAPT | Reuse plotting; relabel for KCI manuscript figure naming. |
| `scripts/make_pilot_statistics.py` | COPY | CI / paired-delta table generator. |
| `scripts/run_accessibility_loss_analysis.py` | COPY | Useful corridor-level diagnostic for the new arterial network. |
| `scripts/run_reproducibility_smoke.py`, `run_clean_checkout_smoke.py` | COPY | Reproducibility scaffolds for the IE method paper. |
| `scripts/run_plausibility_validation.py` | REFERENCE-ONLY | Real-world validation; not needed. |
| `scripts/run_osrm_route_benchmark.py` | EXCLUDE | External OSRM benchmark. Deferred. |
| `scripts/run_full_graph_smoke.py`, `run_graph_scale_diagnostics.py` | EXCLUDE | Full-graph runtime / scale evidence. Out of scope. |
| `scripts/audit_*.py` (17 files) | EXCLUDE | Formal-acceptance / evidence audits. Deferred. |
| `scripts/run_acceptance_audit.py`, `validate_formal_acceptance_package.py`, `write_acceptance_*`, `write_formal_acceptance_*` | EXCLUDE | Formal-acceptance machinery. Deferred. |
| `scripts/write_*_review_packet.py`, `write_*_decision_packet.py`, `write_*_readiness_packet.py`, `write_*_request_packet.py` (~50 files) | EXCLUDE | Acceptance / review packet writers. Deferred. |
| `scripts/cache_ktdb_gtfs_source.py`, `cache_metro9_capacity_source.py`, `derive_rail_*`, `fetch_rail_*` | EXCLUDE | Real Seoul rail data fetch / derivation. Deferred. |
| `scripts/write_road_capacity_evidence.py`, `write_road_speed_evidence.py`, `write_road_class_override_template.py`, `write_route_road_evidence_exposure.py`, `write_osrm_snapshot_manifest.py` | EXCLUDE | Real road-evidence writers. Deferred. |
| `scripts/write_goal_completion_audit.py` | EXCLUDE | Acceptance-gate audit. |

### `tests/` (simulator-core KEEP, acceptance EXCLUDE)

| Path | Decision | Rationale |
|---|---|---|
| `tests/test_models.py`, `test_dispatch.py`, `test_fleet.py`, `test_rail.py`, `test_disruptions.py`, `test_metrics.py`, `test_analysis.py`, `test_traffic.py`, `test_transfers.py`, `test_scenario.py`, `test_config.py` | COPY | Simulator-core unit tests — defend the IE methodology. |
| `tests/fixtures/synthetic_region_fixture.yaml` | COPY | Schema-only fixture used by core / adapter tests. |
| `tests/test_realworld_adapter.py`, `test_realworld_attributes.py`, `test_realworld_types.py`, `test_realworld_osm_network.py`, `test_realworld_region_reusability.py`, `test_realworld_disruption_scenarios.py`, `test_realworld_policy_alternatives.py`, `test_realworld_sensitivity.py`, `test_realworld_accessibility.py`, `test_realworld_end_to_end.py`, `test_realworld_reproducibility_smoke.py`, `test_realworld_clean_checkout_smoke.py`, `test_realworld_manifest_timestamp.py` | COPY | Region / adapter / scenario / sensitivity / accessibility / e2e / reproducibility tests — protect the YAML loader, scenario plumbing, and reproducibility scaffold the new corridor uses. |
| `tests/test_realworld_pilot_experiments.py`, `test_realworld_pilot_smoke.py`, `test_realworld_pilot_figures.py`, `test_realworld_pilot_statistics.py` | ADAPT | Keep the experiment / smoke / figure / statistics test patterns; rebind region IDs and result paths to the kci-arterial fixture. |
| `tests/test_realworld_acceptance_*` (5 files) | EXCLUDE | Acceptance orchestration / records / templates / blocker queue / task assignments. Deferred. |
| `tests/test_realworld_*_acceptance.py` (formal_acceptance_guard / package / pre_review / evidence_matrix; agent_review_path_audit; experiment_acceptance; final_audit_acceptance; graph_scale_acceptance; manuscript_acceptance; parameter_acceptance; pilot_acceptance; provenance_acceptance; publication_readiness; reproducibility_acceptance; sensitivity_acceptance; validation_acceptance; road_override_audit; plan_audit; parameter_audit; tracked_artifact_audit; goal_completion_audit) | EXCLUDE | All acceptance / audit gate tests. Deferred. |
| `tests/test_realworld_*_review_packet.py`, `*_decision_packet.py`, `*_readiness_packet.py`, `*_request_packet.py`, `*_priority_packet.py` (~40 files) | EXCLUDE | Tests for the deferred review / decision packet writers. |
| `tests/test_realworld_rail_*` (gtfs / shortest_path / station_binding / station_cache / timetable / fetch_readiness / evidence / source_decision / timing_request) | EXCLUDE | Real Seoul rail data tests. Deferred. |
| `tests/test_realworld_ktdb_gtfs_source.py`, `test_realworld_metro9_capacity_source.py` | EXCLUDE | Real rail-source caching tests. Deferred. |
| `tests/test_realworld_road_*` (capacity_evidence / evidence / evidence_diagnostics / override_template / overrides / speed_evidence / source_decision / source_readiness) | EXCLUDE | Real road-data evidence tests. Deferred. |
| `tests/test_realworld_route_road_evidence_exposure.py`, `test_realworld_osrm_snapshot_manifest.py`, `test_realworld_validation.py`, `test_realworld_plausibility.py` | EXCLUDE | Real-world validation tests. Deferred. |
| `tests/test_realworld_full_graph_smoke.py`, `test_realworld_graph_scale_*` (7 files) | EXCLUDE | Full-graph / scale tests. Out of scope. |
| `tests/test_realworld_source_*`, `test_realworld_pilot_privacy_review_packet.py`, `test_realworld_pilot_region_decision_packet.py`, `test_realworld_parameters.py`, `test_realworld_parameter_*` | EXCLUDE | Source / parameter calibration packet tests. Deferred. |
| `tests/test_realworld_final_study_readiness.py`, `test_realworld_manuscript_*`, `test_realworld_claim_alignment_review_packet.py`, `test_realworld_figure_table_review_packet.py`, `test_realworld_integrated_evidence_review_packet.py` | EXCLUDE | Manuscript / study-readiness gates. Deferred. |
| `tests/test_realworld_transfer_evidence_review_packet.py` | EXCLUDE | Transfer-evidence packet. Deferred. |

### `schemas/`

| Path | Decision | Rationale |
|---|---|---|
| `schemas/acceptance_record.schema.json` | EXCLUDE | Schema for formal sub-agent acceptance records — explicitly deferred. KCI study has no acceptance gates. |

The `schemas/` directory is omitted from `kci/` entirely; the simulator core uses Python-side validation in `src/`.

---

## 3. Documentation, paper, agents, root markdown, images

### Paper draft

| Path | Decision | Rationale |
|---|---|---|
| `paper/paper_draft.md` | ADAPT | English manuscript scaffold. Drop the open-data civilian / public-sector framing and the 15-gate / 12-blocker readiness narrative; rewrite around (a) reserve-force mobilization and (b) major-arterial-only Songpa virtual corridor. Methods section (paired CRN, censoring-aware metrics, Morris, two-phase DoE) carries over largely intact. The Korean-language version becomes the primary submission per `kci/research_plan.md` §1, §11. |

### `docs/`

| Path | Decision | Rationale |
|---|---|---|
| `docs/analysis_corridor_method_note.md` | ADAPT | Already documents a 118-node / 174-edge reduced corridor extracted from cached OSM. Strip "scaffold / not certified" hedges; reposition as the "virtual major-arterial-only network" Methods sub-section. |
| `docs/sensitivity_diagnostics.md` | ADAPT | Direct source for the Methods / Results paragraph on Morris sensitivity. |
| `docs/sensitivity_method_decision_packet.md`, `docs/sensitivity_review_packet.md` | REFERENCE-ONLY | Useful for justifying choice of Morris + parameter grid; cite, don't duplicate. |
| `docs/experiment_design_decision_packet.md`, `docs/experiment_strategy_readiness_packet.md` | ADAPT | Two-phase paired-CRN DoE rationale. Distill into Methods. |
| `docs/figure_table_review_packet.md` | REFERENCE-ONLY | Useful checklist when assembling KCI figures / tables. |
| `docs/reproducibility_package.md`, `docs/reproducibility_smoke.md`, `docs/clean_checkout_reproducibility_smoke.md` | ADAPT (consolidate) | One short reproducibility appendix for KCI; drop the 0/12 formal-acceptance language. |
| `docs/schemas/manuscript_acceptance_schema.md`, `docs/manuscript_report_decision_packet.md`, `docs/claim_alignment_review_packet.md` | REFERENCE-ONLY | Useful claim-boundary discipline; do not copy verbatim. |
| `docs/realworld_pipeline.md` | EXCLUDE | Real-world calibration track — explicitly deferred. |
| `docs/pilot_region_*`, `pilot_privacy_*`, `region_reuse_checklist.md` | EXCLUDE | Pilot / privacy machinery for the deferred calibration. |
| `docs/parameter_evidence_*`, `parameter_source_*`, `parameter_acceptance_schema.md` | EXCLUDE | Parameter-evidence acceptance is part of the 12 deferred gates. |
| `docs/road_evidence_*`, `road_source_*`, `road_class_override_schema.md`, `route_road_evidence_exposure.md`, `road_evidence_diagnostics.md` | EXCLUDE | Same. |
| `docs/rail_evidence*`, `rail_*_cache_schema.md`, `rail_fetch_readiness_packet.md`, `rail_source_decision_packet.md`, `rail_timing_source_request_packet.md` | EXCLUDE | Same. |
| `docs/rail_evidence.md` | REFERENCE-ONLY | Single most useful deferred-track doc — cite in Limitations / Future work. |
| `docs/osm_graph_snapshot_review_packet.md`, `osrm_route_benchmark_manifest.md`, `full_graph_*`, `graph_scale_*` | EXCLUDE | OSM provenance + full-graph scale-up = deferred. KCI uses the virtual major-arterial corridor only. |
| `docs/source_*`, `third_party_adaptations.md`, `source_license_review_packet.md` | EXCLUDE | License / provenance for deferred real-world inputs. |
| `docs/validation_*`, `accessibility_loss_analysis.md` | EXCLUDE | Real-world validation benchmarks belong to the deferred track. |
| `docs/formal_acceptance_*`, `final_audit_*`, `acceptance_*`, `agent_review_path_audit.md`, `formal_evidence_path_audit.md`, `integrated_evidence_review_packet.md`, `publication_readiness_audit.md`, `human_acceptance_runbook.md`, `tracked_artifact_audit.md`, `plan_completion_audit.md`, `current_goal_completion_audit.md` | EXCLUDE | Entire 12-gate formal-acceptance machinery. Out of scope. |
| `docs/agents/acceptance_review_agents.md` | EXCLUDE | Same. |
| `docs/review_packets/*` (all 12) | EXCLUDE | Per-gate review aids for the deferred track. |

### Agents

| Path | Decision | Rationale |
|---|---|---|
| `agents.md` | ADAPT | Replace the broad public-sector mission statement with the KCI military framing; trim the 12-gate readiness boilerplate; keep repo-structure and Windows / venv setup. A new shorter `kci/agents.md` focused on the manuscript workstream is the right output. |
| `agents/acceptance_review_agents.json` | EXCLUDE | Drives the 12-gate acceptance-review pipeline that KCI is bypassing. |

### Root markdown

| Path | Decision | Rationale |
|---|---|---|
| `국방.md` | COPY | Korean defense-AI competition proposal template — closest existing piece of military framing. Direct seed material for the KCI Introduction and Significance sections. |
| `report_draft.md` | ADAPT | Korean narrative report. **Heaviest reuse target** for the KCI manuscript body. Must (a) replace 지역 인력 이동 / 재난·공공안전 framing with reserve-force mobilization, (b) replace "추상 네트워크" Methods paragraph with "송파구 주요 간선도로 가상 네트워크", (c) drop the 12-blocker / `final_study_ready=false` paragraphs. |
| `README.md` | ADAPT (light) | Trim to a `kci/` README pointing at the manuscript, methods, and reproducibility scripts. |
| `IMPLEMENTATION_PLAN.md` | REFERENCE-ONLY | Implementation record of the simulator; useful as Methods cross-check. |
| `plan.md` | EXCLUDE | Plan for the deferred real-world study. The KCI folder will get its own `plan.md`. |
| `status.md` | EXCLUDE | Tracks the 12-gate readiness for the deferred track. |
| `realistic_simulation_requirements.md` | REFERENCE-ONLY | Korean realism-requirement notes — informs Limitations / Future work. |
| `real_world_simulation_implementation_blueprint.md` | EXCLUDE | Deferred-track blueprint. |
| `repo_survey_results.md` | EXCLUDE | Historical reference; superseded. |
| `public_github_repo_research.md` | REFERENCE-ONLY | Source pool for related-work citations (OSMnx, SALib, etc.). |
| `disrupted_mobilization_resilience_repo_research.md` | REFERENCE-ONLY | Feeds Literature Review on resilience metrics and emergency-evacuation engines. |
| `cloned_repo_manifest.md` | EXCLUDE | Manifest for ignored local clones. |
| `gpt_image_2_pipeline_prompt.md` | ADAPT | Reusable as the prompt for a KCI-specific concept figure if a second image is wanted. Strip readiness-boundary boilerplate. |

### Images

| Path | Decision | Rationale |
|---|---|---|
| `전시_예비군_수송체계_시뮬레이션_개념도.png` | COPY | Wartime reserve-force transport conceptual diagram. Directly aligned with the KCI military framing — strong candidate for **Figure 1** of the manuscript. |

### Other

| Path | Decision | Rationale |
|---|---|---|
| `microsim_experiment_proposal_v3.docx` | REFERENCE-ONLY | Original proposal (binary). Useful provenance; no need to copy into `kci/`. |
| `report.docx` | EXCLUDE | Auto-generated from `report_draft.md`. The `kci/` folder will regenerate its own .docx from the adapted Korean source. |

---

## 4. Suggested directory layout under `./kci/`

```
kci/
  research_plan.md                    # this file's companion (research scope)
  repo_assets_audit.md                # this document
  plan.md                             # to be authored next (implementation plan)
  README.md                           # ADAPT from upstream README
  agents.md                           # ADAPT — KCI manuscript workstream version
  학회_관련_정보/                       # already present — KCI submission rules
  manuscript/
    manuscript_ko.md                  # ADAPT from report_draft.md (primary)
    manuscript_en_supplementary.md    # ADAPT from paper/paper_draft.md (optional)
    figures/
      figure1_concept.png             # COPY 전시_예비군_수송체계_시뮬레이션_개념도.png
      figure2..N_*.png                # NEW — regenerated from kci runs
    references.bib                    # NEW
  src/                                # see §1
    __init__.py
    network.py … transfers.py
    experiment/
    visualize/
    realworld/                        # slim subset only
  data/
    cache/
      pilot_region_road.graphml
      pilot_region_road_manifest.json
      arterial_corridor.graphml       # NEW (filter output)
      arterial_corridor_manifest.json # NEW
    regions/
      kci_arterial_region.yaml        # ADAPT from pilot_region.yaml
    scenarios/
      disruption_scenarios.csv        # ADAPT
      policy_alternatives.csv
      sensitivity_design.csv
    parameters/
      fleet_assumptions.csv           # ADAPT
      rail_assumptions.csv            # ADAPT
    manifests/
      pilot_experiment_design.json
      reproducibility_manifest.json
    validation/
      accessibility_loss.csv          # COPY (regenerated for arterial)
      reproducibility_smoke_*         # COPY
  results/                            # populated by KCI runs (initially empty)
  scripts/
    build_arterial_cache.py           # ADAPT from build_pilot_cache.py
    run_pilot_experiments.py
    run_pilot_smoke.py
    run_sensitivity.py
    make_pilot_figures.py             # ADAPT (relabel)
    make_pilot_statistics.py
    run_accessibility_loss_analysis.py
    run_reproducibility_smoke.py
    run_clean_checkout_smoke.py
  tests/
    fixtures/synthetic_region_fixture.yaml
    test_*.py                         # simulator-core + adapter / scenario / sensitivity / e2e / reproducibility
  docs/
    analysis_corridor_method_note.md  # ADAPT
    sensitivity_diagnostics.md        # ADAPT
    experiment_design.md              # consolidated from upstream packets
    reproducibility.md                # consolidated
    legacy_pilot_results_pointer.md   # links to upstream results/realworld_pilot/
  config.yaml                         # ADAPT
  main.py                             # ADAPT
  requirements.txt                    # ADAPT
```

---

## 5. Manuscript-asset → KCI section mapping

| KCI section | Source assets |
|---|---|
| Abstract / 초록 | `report_draft.md` 요약 (rewritten with reserve-force framing); methods bullets adapted from `paper/paper_draft.md` |
| Introduction / 서론 · 연구 배경 | `국방.md` (military significance); `report_draft.md` 연구 배경; intro paragraphs of `paper/paper_draft.md`. **Figure 1** = `전시_예비군_수송체계_시뮬레이션_개념도.png` |
| Literature Review / 선행연구 | `public_github_repo_research.md`, `disrupted_mobilization_resilience_repo_research.md` (REFERENCE-ONLY — extract citations only) |
| Methods / 연구 방법 — simulator | `IMPLEMENTATION_PLAN.md` + `agents.md` repo-structure block |
| Methods — virtual corridor | `docs/analysis_corridor_method_note.md` (ADAPT — drop scaffold-only hedge) |
| Methods — DoE | `docs/experiment_design_decision_packet.md` + `paper/paper_draft.md` Methods |
| Methods — censoring-aware metrics | `paper/paper_draft.md` + `report_draft.md` 모형에 반영한 현실적 요소 |
| Methods — Morris sensitivity | `docs/sensitivity_diagnostics.md` + `docs/sensitivity_method_decision_packet.md` (REFERENCE-ONLY) |
| Results | `report_draft.md` 주요 결과 + `paper/paper_draft.md` results scaffold (regenerate tables / figures from new arterial-corridor runs) |
| Discussion / 논의 | Synthesize from both drafts; emphasize military mobilization implications using `국방.md` framing |
| Limitations / 한계 | `kci/research_plan.md` §10; cite `realistic_simulation_requirements.md` and `docs/rail_evidence.md` |
| Future work | `kci/research_plan.md` §4 deferred-list reframed as roadmap; point at (don't include) `docs/realworld_pipeline.md`, upstream `plan.md`, `real_world_simulation_implementation_blueprint.md` |
| Reproducibility appendix | Condensed from `docs/reproducibility_package.md` + `docs/reproducibility_smoke.md` |

---

## 6. Open questions — status (updated 2026-05-11 after origin/destination decision)

The original 16 open questions raised by the three sub-agents were **closed by user decision** on 2026-05-11 and are recorded as **`kci/agents.md` §7** (Resolved decisions). Material changes from this audit's v0.1 framing:

- **A.2 (destination):** Originally proposed as a synthetic centroid within Songpa-gu. **Now: 72사단 부곡리 동원훈련장** (경기 양주 장흥 부곡리 산 6-17, publicly published by 병무청). The Songpa→72사단 catchment is hedged as illustrative in the manuscript Limitations.
- **A.3 (Songpa region extent):** Originally "keep the existing Songpa-only pilot bbox." **Now expanded** to a corridor bbox covering all Songpa origins, the 부곡리 destination, and the connecting expressways (올림픽대로 / 강변북로 / 외곽순환). Provisional bbox: lat 37.46–37.78, lon 126.85–127.20 (final bbox tightened in `plan.md`). New cache file: `data/cache/songpa_yangju_corridor.graphml`.
- **A.6 (D-dependent scenarios):** All scenario rows referencing `D` are remapped to the 부곡리 destination ID. New scenario rows for arterial blockages on 올림픽대로 / 강변북로 / 외곽순환 are added.
- **NEW (origin):** Four origin scenarios — (A) 송파구청 일자리센터 앞 (37.5147, 127.1057), (B) 삼전동 구민회관 앞 (37.5036, 127.0857), (C) 장지역 4번 출구 앞 (37.4784, 127.1262) from Hankyung 2024-02-29 + 송파구 ordinance 2023-09-14, and (D) 잠실종합운동장 (37.5159, 127.0727) flagged as 출처 미확인 가정 변형 per user instruction. Treated as a robustness sweep; Phase 1 treatment (full factor vs focused robustness) settled in `plan.md`.
- **A.5 / B.7 / B.8 / B.9 / B.10 / C.11 / C.12 / C.13 / D.14 / D.15 / D.16:** All resolved per user decisions on 2026-05-11. See `agents.md` §7 for the per-row outcome.

### Items still open (carry to `kci/plan.md`)

1. **Final OSM bbox** for the songpa↔양주 corridor — provisional (lat 37.46–37.78, lon 126.85–127.20) to be tightened after a quick OSMnx extraction sanity check.
2. **Rail leg treatment** on the songpa↔의정부/양주 axis — keep abstract long-distance rail with hedging, demote rail to alternative scenario, or drop rail entirely.
3. **Origin Phase 1 treatment** — full 4-level factor (~4× cell count) vs focused robustness check at fewer seeds.
4. **Runtime budget** for the new (larger) corridor — Phase 1 / Phase 2 / Morris cell counts may need adjustment.
5. **Authorship and affiliation** (decision #12 — pending user confirmation).
6. **KCI manuscript template binding** at draft freeze using `kci/학회_관련_정보/`.

### Note on file name conventions in §4

The "Suggested directory layout under `./kci/`" in §4 still lists `arterial_corridor.graphml` and `kci_arterial_region.yaml` from the v0.1 framing. These are now superseded by `songpa_yangju_corridor.graphml` and `songpa_yangju_corridor.yaml`. The §4 layout will be regenerated in `kci/plan.md` with the corrected paths.

---

## 7. Audit provenance

This document is the synthesis of three parallel Opus sub-agent audits run on 2026-05-11:

- **Sub-agent A** — core simulation code (`src/`, `main.py`, `generate_report.py`, `generate_report_figures.py`, `config.yaml`, `requirements.txt`).
- **Sub-agent B** — data, results, scripts, tests, schemas (`data/`, `results/`, `scripts/`, `tests/`, `schemas/`).
- **Sub-agent C** — documentation, paper, agents, root markdown, images (`paper/`, `docs/`, `agents/`, `agents.md`, root `*.md`, conceptual image, `report.docx`, `microsim_experiment_proposal_v3.docx`).

Each sub-agent was given the same KCI study brief (military journal, IE framing, virtual major-arterial Songpa corridor, deferred real-world calibration). Decisions were assigned independently and reconciled here. Where the three reports overlap, the more conservative decision was kept (e.g., simulator-core unit tests are COPY in B's report and were carried through unchanged).
