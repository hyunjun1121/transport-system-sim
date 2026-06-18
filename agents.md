# AGENTS.md - Transport System Simulation

## Current Continuation Context - 2026-06-18

Phase U (Automated Gate Closure & Evidence Strengthening) is **complete**.
All 13 task units (U1-U13) executed successfully. Evidence was strengthened
from cached public-data sources, a full-graph feasibility probe was run,
and all review packets were regenerated. 12 gates remain blocked pending
human-signoff acceptance artifacts.

### Phase U Summary

- **U1**: Disruption scenario manifest regenerated with SHA256 and row count.
- **U2**: Clean-checkout reproducibility smoke regenerated (20 commands pass,
  `clean_checkout_test_performed=false` stays — worktree smoke only).
- **U3**: Rail headway derived from KTDB GTFS timetable cache: **3.583 min**
  (median of 240 adjacent gaps, station 4136, 241 access departures).
- **U4**: Rail capacity derived from Metro9 operator page: **922 pax**
  (306 seats + 616 standing, 6 cars).
- **U5**: GTFS derivation attempt documented as failed
  (`input_is_gtfs_feed=false`).
- **U6**: Road override draft refined: 5/10 classes `public-data-derived`
  (observed OSM maxspeed).
- **U7**: Parameter evidence refreshed: 6 source-backed (was 4),
  23 weak (was 25). Rail headway/capacity no longer weak for final claims.
- **U8**: Full-graph probe: **15,870 rows** on 4,608-node bus-practical
  graph (0.278 s/row). Statistics + figures generated.
- **U9**: 15 cross-cutting review packets regenerated.
- **U10**: Full-graph statistics (6877 CI rows) + figures. Truth table
  unchanged (config values unchanged).
- **U11**: Full verification: 164/164 tests pass, claim guard clean.
- **U12**: 3 sub-agent reviewers confirmed evidence integrity (6/6 PASS),
  packet consistency (resolved), claim boundary (removed unreviewed
  `road_class_overrides.csv`).
- **U13**: This update + commit/push.

### Current State of the Worktree

- Simulation code: Deterministic disruptions + road noise (sigma) +
  turnaround noise (lambda) as sole within-scenario variance (from Phase T).
- Results: `pilot_full_results.csv` (15,870 rows, reduced corridor) +
  `pilot_full_graph_results.csv` (15,870 rows, full 4,608-node graph).
- Parameter evidence: `parameter_sources.csv` has 6 source-backed params
  (bpr_alpha, bpr_beta, rail_access_point, rail_egress_point, rail_headway,
  rail_capacity). Rail headway = 3.583 min, rail_capacity = 922 pax.
  Simulation config unchanged (10 min headway, 500 pax capacity) until
  config update and re-experimentation.
- Rail evidence: `rail_service_evidence.csv` has 3 rows (proxy,
  headway_derived, capacity_derived) with source SHA256.
- Road evidence: `road_class_overrides_draft.csv` has 5/10 classes
  `public-data-derived`. Reviewed `road_class_overrides.csv` intentionally
  absent (removed during U12 to restore claim boundary).
- Claim guard: `blocking_finding_count=0`, `release_blocked=false`.
- Tests: 164/164 pass.

### Gate Status

- Unblocked: 3/15 (`real_input_smoke`, `structured_disruptions`,
  `policy_alternatives`)
- Blocked: 12/15 (all require human-signoff `*_acceptance.json` artifacts)
- Formal acceptance artifacts: 0/12 present (all intentionally absent)
- `final_study_ready=false`, `publication_ready=false`

### Active Claim Boundary

Do not claim any of the following unless current audits independently prove
them:

- within-scenario route-command capability (not claimed);
- real-world forecasting accuracy (not claimed);
- calibrated field validation (not claimed);
- publication readiness (not claimed);
- final-study readiness (not claimed);
- formal acceptance (not claimed);
- "genuine estimates of stochastic uncertainty" from uncalibrated parameters
  (explicitly NOT claimed — within-scenario noise parameters are exploratory
  sensitivity assumptions, not calibrated values; see §10.7 for sensitivity
  to these parameter choices).

Allowed framing: decision-support simulation, quasi-real input pipeline,
scenario comparison (deterministic disruption + within-scenario noise),
resilience/sensitivity analysis, and ML-assisted classification only when
runtime evidence supports that specific claim.

### Phase T Key Design Decisions

1. **Mechanism A reverted**: Pilot experiments return to
   `force_deterministic=True`. Disruption scenarios are controlled experiments.
2. **Mechanisms B & C retained**: Road noise and turnaround noise remain as
   the sole within-scenario variance sources, but framed as exploratory
   sensitivity parameters, not calibrated defaults.
3. **Morris extended**: `road_noise_sigma` and `turnaround_noise_lambda` added
   to the Morris parameter space so sensitivity analysis reveals whether
   conclusions depend on noise parameter choices.
4. **Paper honesty**: §9.9 must not claim "genuine estimates of stochastic
   uncertainty" unless the Morris sweep proves conclusions are robust across
   parameter choices.

### Immediate Continuation Priority

The next agent should execute Phase T1 through T7 as defined in `plan.md`:

1. T1: Revert Mechanism A, add sigma/lambda to Morris parameters.
2. T2: Verify variance from B+C only, run parameter sweep diagnostics.
3. T3: Full re-experimentation + extended Morris.
4. T4: Truth table rebuild + data audit.
5. T5: Paper/report correction (honest stochasticity framing).
6. T6: Verification + independent sub-agent review.
7. T7: Closeout (update AGENTS.md, status.md).

Keep `final_study_ready=false`, `publication_ready=false`, and
`formal_acceptance_evidence=false` unless current repository audits prove
otherwise.

## Project Overview

Disrupted regional personnel-transport resilience simulation. The implemented
baseline compares **bus-only** vs **rail-bus multimodal** transport for moving
approximately 1,000 people from an assembly context toward a destination zone.

The current research direction is broader than the original wartime/reserve
framing:

> build an open-data, region-reusable, real-world or quasi-real simulation
> pipeline for emergency personnel movement, disrupted regional mobility, and
> public-sector contingency transport planning.

Do not present the current model as an operational route plan or real-world forecast; it is a decision-support and resilience-evaluation framework.

**Environment**: Windows PowerShell. Use the Python Launcher (`py`) to create a
local virtual environment, then run project commands through
`.\.venv\Scripts\python`.

## Current Audit Snapshot

As of 2026-05-10, the study-closeout audit reports the machine flag
`final_study_ready=false`. The audit has 15 gates: 3 currently unblocked for
scaffold-level checks (`real_input_smoke`, `structured_disruptions`,
`policy_alternatives`) and 12 blocked. Source-backed human-review closure is
0/12, and reviewer target files must be absent or backed by source-backed human
review before any gate can close. In the current local worktree, placeholder
copies were moved out of reviewer target paths into draft storage; the formal
guard reports 0 target files present and 12 missing, with no template copies in
formal paths.
The expert consultation reply on the previous package bundle remains the primary
guide for the pre-review process: the package must first pass package
inventory, path-integrity, and reviewer-file hygiene checks before any gate is
reinterpreted as complete.

Artifact identifiers only: `validation_strategy_readiness`,
`graph_scale_strategy_readiness`, `sensitivity_strategy_readiness`,
`experiment_strategy_readiness`, `validation_benchmark_decision`,
`experiment_design_decision`, and `figure_table_review` exist as blocker or
decision-review aids only. They are not reviewer decision records and cannot
support fit-to-observed-data evidence, route-command guidance, or study
sign-off.

## Repository Structure

The repository map below lists literal paths and identifiers only. Names in this
listing are not gate-status claims, evidence-quality claims, route-use
authority, or study sign-off.

```text
main.py                    # CLI entry: --quick, --test, --phase 1|2
config.yaml                # Network, BPR, stochastic, dispatch, DoE config
requirements.txt           # Python dependencies for Windows/venv setup
requirements-ml.txt        # Optional Phase 10 post-simulation ML/GPU deps
generate_report.py         # Generates report.docx from report_draft.md
report_draft.md            # Korean narrative report source
report.docx                # Generated Word document
microsim_experiment_proposal_v3.docx  # Original proposal
status.md                  # Current project context and limitations
plan.md                    # Remaining work guide
IMPLEMENTATION_PLAN.md     # Implemented system notes
realistic_simulation_requirements.md  # Korean realism requirements
public_github_repo_research.md        # Public repo research synthesis
disrupted_mobilization_resilience_repo_research.md
                           # Disrupted-resilience repo research synthesis
real_world_simulation_implementation_blueprint.md
                           # Implementation blueprint from public repo research
cloned_repo_manifest.md    # Manifest for ignored local reference clones
paper/
  paper_draft.md           # English paper/manuscript scaffold
src/
  sim_types.py             # Shared immutable simulation records
  network.py               # Build NetworkX DiGraph from config
  models.py                # BPR, Bernoulli failures, LogNormal delays
  policies.py              # StrictPolicy, GracePolicy(W, theta)
  dispatch.py              # Passenger queues and dispatch manifests
  fleet.py                 # Fleet availability and turnaround
  traffic.py               # Dynamic road volume and BPR edge traversal
  disruptions.py           # Structured blocked/degraded edge states
  rail.py                  # Fixed-headway rail service helpers
  transfers.py             # Fixed and per-passenger transfer delays
  metrics.py               # MetricsCollector KPIs
  scenario.py              # Scenario orchestrator: run_scenario() -> dict
  realworld/
    acceptance_records.py  # Common review-agent record schema validation
    acceptance_orchestration.py # Deterministic sub-agent gate review runner
    acceptance_decision_templates.py # Non-approval formal acceptance templates
    acceptance_blocker_queue.py # Formal blocker queue for reviewer actions
    acceptance_task_assignments.py # Map formal blockers to review-agent tasks
    formal_acceptance_evidence_matrix.py # Per-artifact reviewer intake matrix
    formal_acceptance_guard.py # Detect placeholder/template misuse
    formal_evidence_path_audit.py # Check formal evidence/source paths
    formal_acceptance_package.py # Aggregate formal acceptance intake audit
    review_package_path_audit.py # ZIP-internal review-package path audit
    review_package_handoff.py # ZIP-external expert-review handoff sidecar
    manuscript_acceptance.py # Explicit manuscript/report acceptance validation
    types.py                # RegionSpec, BoundarySpec, ZoneSpec, RailSpec
    regions.py              # Region registry loading and validation
    osm_network.py          # Optional OSMnx bbox extraction and GraphML cache
    attributes.py           # OSM-style edge mapping to simulator fields
    zones.py                # Nearest-node snapping and connector edges
    adapter.py              # OSM-like graph to simulator-compatible DiGraph
    validation.py           # Graph-readiness checks before scenario runs
    parameters.py           # Parameter-source table validation
    graph_scale_acceptance.py # Explicit graph-scale acceptance validation
    validation_acceptance.py # Explicit validation-package acceptance validation
    final_audit_acceptance.py # Explicit independent final-audit acceptance validation
    parameter_acceptance.py # Optional weak-parameter acceptance validation
    parameter_audit.py      # Parameter evidence readiness audit
    parameter_review_packet.py # Weak-parameter review worksheet generation
    parameter_evidence_request_packet.py # Cross-cutting parameter source-request worksheet
    pilot_acceptance.py     # Explicit pilot acceptance record validation
    pilot_privacy_review_packet.py # Pilot privacy/sensitivity review worksheet
    provenance_acceptance.py # Explicit data-provenance acceptance validation
    source_provenance.py    # Source provenance review packet validation
    source_license_review_packet.py # Source/license review worksheet generation
    source_url_review_packet.py # Source URL review worksheet generation
    claim_alignment_review_packet.py # Manuscript/report claim review worksheet
    claim_language_guard.py # Fail-closed lexical claim-language release guard
    road_evidence.py        # Cached road-input evidence audit
    road_evidence_diagnostics.py # Road-class evidence gap diagnostics
    road_capacity_evidence.py # Cached OSM lanes capacity candidate evidence
    road_speed_evidence.py  # Cached OSM maxspeed candidate evidence
    road_evidence_review_packet.py # Consolidated road-input review worksheet
    road_evidence_request_packet.py # Road evidence source-request worksheet
    road_overrides.py       # Optional road-class evidence override loader
    road_override_template.py # Draft road-class override review templates
    road_override_audit.py  # Optional road-class override readiness audit
    plausibility.py         # Offline pilot route plausibility checks
    validation_review_packet.py # Validation-strategy review worksheet generator
    validation_strategy_readiness_packet.py # Validation blocker/readiness worksheet
    route_road_evidence_exposure.py # Route-level road evidence exposure review aid
    upstream_lineage_review_packet.py # Phase 9 upstream artifact lineage review aid
    graph_scale_diagnostics.py # Full-vs-reduced route parity and alternate-route diagnostics
    graph_scale_review.py   # Graph-scale method option review worksheet
    graph_scale_strategy_readiness_packet.py # Graph-scale blocker/readiness worksheet
    disruption_scenarios.py # Structured disruption definitions and manifest support
    policy_alternatives.py  # Policy alternative config variants
    pilot_experiments.py    # Cached pilot scaffold experiment runner
    experiment_acceptance.py # Explicit pilot experiment-output acceptance validation
    experiment_package_review_packet.py # Full experiment output review worksheet
    experiment_strategy_readiness_packet.py # Experiment blocker/readiness worksheet
    reproducibility_acceptance.py # Explicit clean-checkout acceptance validation
    reproducibility_review_packet.py # Clean-checkout review worksheet generator
    reproducibility_smoke.py # Current-worktree smoke evidence runner
    sensitivity.py          # Deterministic and SALib Morris sensitivity scaffold
    sensitivity_acceptance.py # Explicit sensitivity acceptance validation
    sensitivity_diagnostics.py # Morris output review diagnostics
    sensitivity_review_packet.py # Morris diagnostics review worksheet generator
    sensitivity_strategy_readiness_packet.py # Sensitivity blocker/readiness worksheet
    pilot_figures.py        # Scaffold-only figures and claim-boundary tables
    publication_readiness.py # Aggregated final-claim readiness audit
    final_study_readiness.py # Plan-level final-study gate audit
    rail_evidence.py        # Offline rail evidence cache validation
    rail_station_binding.py # Rail-point station binding evidence audit
    rail_station_cache.py   # Cached station extract -> binding derivation
    rail_timetable.py       # Cached timetable -> rail evidence derivation
    rail_timetable_api.py   # Optional data.go.kr train-schedule cache fetcher
    rail_gtfs.py            # Cached static GTFS -> rail timing evidence
    rail_shortest_path.py   # Cached shortest-path -> rail travel-time evidence
    rail_shortest_path_api.py # Optional data.go.kr shortest-path cache fetcher
    rail_evidence_review_packet.py # Consolidated rail evidence review worksheet
    rail_timing_request_packet.py # Rail timing source-request worksheet
  experiment/
    doe.py                 # phase1_grid, phase2_grid
    runner.py              # CRN paired execution: run_phase1(), run_phase2()
    analysis.py            # compute_ci(), find_breakeven(), summarize_phase1()
  visualize/
    plots.py               # Heatmaps, Pareto curves, break-even line
tests/
  test_models.py           # Model, network, policy, metrics smoke tests
  test_config.py           # Config namespace/schema smoke tests
  test_dispatch.py         # Queue dispatch behavior tests
  test_fleet.py            # Fleet availability tests
  test_traffic.py          # Dynamic traffic and BPR traversal tests
  test_disruptions.py      # Failure/disruption tests
  test_rail.py             # Fixed-headway rail tests
  test_transfers.py        # Transfer-delay tests
  test_metrics.py          # Censoring KPI tests
  test_analysis.py         # CI and summary tests
  test_scenario.py         # End-to-end scenario regression tests
  test_realworld_types.py
  test_realworld_attributes.py
  test_realworld_osm_network.py
  test_realworld_adapter.py
  test_realworld_validation.py
  test_realworld_end_to_end.py
  test_realworld_pilot_smoke.py
  test_realworld_full_graph_smoke.py
  test_realworld_rail_evidence.py
  test_realworld_parameters.py
  test_realworld_graph_scale_acceptance.py
  test_realworld_graph_scale_diagnostics.py
  test_realworld_graph_scale_review.py
  test_realworld_graph_scale_strategy_readiness_packet.py
  test_realworld_graph_scale_result_comparison.py
  test_realworld_validation_acceptance.py
  test_realworld_final_audit_acceptance.py
  test_realworld_parameter_acceptance.py
  test_realworld_parameter_audit.py
  test_realworld_parameter_review_packet.py
  test_realworld_pilot_acceptance.py
  test_realworld_provenance_acceptance.py
  test_realworld_source_license_review_packet.py
  test_realworld_source_url_review_packet.py
  test_realworld_manuscript_acceptance.py
  test_realworld_road_evidence.py
  test_realworld_road_evidence_diagnostics.py
  test_realworld_road_capacity_evidence.py
  test_realworld_road_speed_evidence.py
  test_realworld_road_overrides.py
  test_realworld_road_override_template.py
  test_realworld_rail_station_binding.py
  test_realworld_rail_timetable.py
  test_realworld_rail_timetable_api.py
  test_realworld_rail_shortest_path.py
  test_realworld_rail_shortest_path_api.py
  test_realworld_plausibility.py
  test_realworld_disruption_scenarios.py
  test_realworld_policy_alternatives.py
  test_realworld_pilot_experiments.py
  test_realworld_experiment_acceptance.py
  test_realworld_experiment_strategy_readiness_packet.py
  test_realworld_reproducibility_acceptance.py
  test_realworld_reproducibility_review_packet.py
  test_realworld_reproducibility_smoke.py
  test_realworld_sensitivity.py
  test_realworld_sensitivity_acceptance.py
  test_realworld_sensitivity_diagnostics.py
  test_realworld_sensitivity_review_packet.py
  test_realworld_sensitivity_strategy_readiness_packet.py
  test_realworld_osrm_snapshot_manifest.py
  test_realworld_validation_review_packet.py
  test_realworld_validation_strategy_readiness_packet.py
  test_realworld_route_road_evidence_exposure.py
  test_realworld_upstream_lineage_review_packet.py
  test_realworld_acceptance_records.py
  test_realworld_acceptance_orchestration.py
  test_realworld_acceptance_blocker_queue.py
  test_realworld_acceptance_task_assignments.py
  test_realworld_formal_acceptance_evidence_matrix.py
  test_realworld_formal_evidence_path_audit.py
  test_realworld_seed_stream_manifest.py
  test_realworld_crn_pairing_audit.py
  test_realworld_replication_adequacy_audit.py
  test_realworld_review_package_inventory.py
  test_realworld_review_package_builder.py
  test_realworld_review_package_handoff.py
  test_realworld_plan_audit.py
data/
  regions/pilot_region.yaml
  cache/pilot_region_road.graphml
  parameters/
    road_class_overrides_draft.csv  # 10-row expert-assumption review worksheet
    parameter_evidence_review_packet.csv # 29-row weak-parameter review worksheet
    parameter_evidence_review_manifest.json
    parameter_evidence_source_request_packet.csv # 7-row parameter source-request aid
    parameter_evidence_source_request_manifest.json
    road_capacity_evidence_candidates.csv # 10-row capacity evidence gap aid
    road_speed_evidence_candidates.csv # 10-row OSM maxspeed review aid
    road_evidence_review_packet.csv # 10-row consolidated road review aid
    road_evidence_review_manifest.json
  road/
    road_evidence_source_request_packet.csv # 5-row road source-request aid
    road_evidence_source_request_manifest.json
    rail_evidence_review_packet.csv # 12-row consolidated rail review aid
    rail_evidence_review_manifest.json
    rail_timing_source_request_packet.csv # 5-row rail source request aid
    rail_timing_source_request_manifest.json
  validation/
    validation_review_packet.csv # 7-row validation-strategy review aid
    validation_review_manifest.json
    validation_strategy_readiness_packet.csv # 7-row validation blocker/readiness aid
    validation_strategy_readiness_manifest.json
    graph_scale_strategy_readiness_packet.csv # 5-row graph-scale blocker/readiness aid
    graph_scale_strategy_readiness_manifest.json
    reproducibility_review_packet.csv # 8-row clean-checkout review aid
    reproducibility_review_manifest.json
    experiment_strategy_readiness_packet.csv # 9-row experiment blocker/readiness aid
    experiment_strategy_readiness_manifest.json
    reproducibility_smoke_manifest.json # current-worktree smoke summary
    reproducibility_smoke_log.jsonl # current-worktree smoke command log
    canonical_route_road_evidence_exposure.csv # 76-row route-level road-evidence exposure aid
    canonical_route_road_evidence_exposure_manifest.json
    sensitivity_review_packet.csv # 6-row Morris diagnostics review aid
    sensitivity_review_manifest.json
    sensitivity_strategy_readiness_packet.csv # 7-row sensitivity blocker/readiness aid
    sensitivity_strategy_readiness_manifest.json
  scenarios/
  manifests/reproducibility_manifest.json
  manifests/formal_evidence_path_audit.json # formal evidence-path hygiene summary
scripts/
  audit_agent_review_paths.py
  audit_analysis_outputs.py
  audit_claim_language.py
  audit_compact_scoped_outputs.py
  audit_review_package_paths.py
  audit_final_study_readiness.py
  audit_formal_acceptance_artifacts.py
  audit_formal_evidence_paths.py
  audit_graph_scale_manifests.py
  audit_parameter_evidence.py
  audit_plan_artifacts.py
  audit_publication_readiness.py
  audit_rail_bounded_treatments.py
  audit_rail_evidence.py
  audit_rail_station_bindings.py
  audit_road_evidence.py
  audit_road_evidence_diagnostics.py
  audit_road_overrides.py
  audit_sensitivity_diagnostics.py
  audit_source_context_hashes.py
  audit_source_provenance.py
  audit_tracked_artifacts.py
  build_pilot_cache.py       # Preserves cache by default; explicit fixture/Overpass refresh
  cache_ktdb_gtfs_source.py  # Optional source-cache helper; not default acceptance evidence
  cache_metro9_capacity_source.py # Optional source-cache helper; not default acceptance evidence
  check_gpu_ml_runtime.py    # Optional GPU ML runtime preflight; not simulation acceleration evidence
  write_runtime_preflight_manifest.py # Phase-scoped runtime/dependency preflight manifest
  derive_rail_gtfs_evidence.py
  derive_rail_capacity_evidence.py  # Cached Metro9 extract -> capacity evidence row
  derive_rail_headway_evidence.py
  derive_rail_service_evidence.py
  derive_rail_shortest_path_evidence.py
  derive_rail_station_bindings.py
  fetch_rail_shortest_path_cache.py
  fetch_rail_timetable_cache.py
  normalize_rail_timetable_cache.py
  record_gtfs_derivation_attempt.py # Document cached-GTFS feed-absent attempt
  make_pilot_figures.py
  make_pilot_statistics.py
  run_acceptance_audit.py
  run_accessibility_loss_analysis.py
  audit_deterministic_rerun.py
  write_dirty_worktree_classification.py
  write_phase_gate_ledgers.py
  run_clean_checkout_smoke.py
  run_full_graph_smoke.py
  run_graph_scale_diagnostics.py
  run_ml_analysis.py
  run_osrm_route_benchmark.py
  run_phase8_micro_probe.py
  run_pilot_experiments.py
  run_pilot_smoke.py
  run_plausibility_validation.py
  run_reproducibility_smoke.py
  run_sensitivity.py
  run_variance_diagnostic.py
  regenerate_truth_table.py
  validate_formal_acceptance_package.py
  build_review_package.py
  write_expert_review_handoff.py
  write_seed_stream_manifest.py
  audit_crn_pairing.py
  audit_replication_adequacy.py
  write_acceptance_blocker_queue.py
  write_acceptance_decision_templates.py
  write_acceptance_task_assignments.py
  write_claim_alignment_review_packet.py
  write_demand_fleet_behavior_profiles.py
  write_disruption_scenario_manifest.py
  write_experiment_design_decision_packet.py
  write_experiment_package_review_packet.py
  write_experiment_statistical_plan.py
  write_experiment_strategy_readiness_packet.py
  write_figure_table_review_packet.py
  write_final_audit_decision_packet.py
  write_formal_acceptance_blocker_queue.py
  write_formal_acceptance_evidence_matrix.py
  write_formal_acceptance_pre_review.py
  write_full_graph_runtime_readiness_packet.py
  write_goal_completion_audit.py
  write_graph_scale_method_decision_packet.py
  write_graph_scale_result_comparison.py
  write_graph_scale_review_packet.py
  write_graph_scale_strategy_readiness_packet.py
  write_artifact_invalidation_matrix.py
  write_integrated_evidence_review_packet.py
  write_manuscript_report_decision_packet.py
  write_osm_graph_snapshot_review_packet.py
  write_phase8_precompact_tables.py
  write_road_snapshot.py
  write_osrm_snapshot_manifest.py
  write_parameter_evidence_priority_packet.py
  write_parameter_evidence_source_request_packet.py
  write_parameter_review_packet.py
  write_parameter_source_decision_packet.py
  write_parameter_source_readiness_packet.py
  write_pilot_privacy_review_packet.py
  write_pilot_region_decision_packet.py
  write_rail_evidence_priority_packet.py
  write_rail_evidence_review_packet.py
  write_rail_fetch_readiness_packet.py
  write_rail_service_static_candidate.py
  write_rail_source_decision_action_ledger_template.py
  write_rail_source_decision_packet.py
  write_rail_source_decision_recommendation_packet.py
  write_rail_static_timetable_segment_pair_diagnostic.py
  write_rail_timing_source_request_packet.py
  write_rail_transit_stress_profile_packet.py
  write_reproducibility_decision_packet.py
  write_reproducibility_review_packet.py
  write_review_package_inventory.py
  write_road_attribute_evidence.py
  write_road_capacity_evidence.py
  write_road_class_override_source_candidate.py
  write_road_class_override_template.py
  write_road_evidence_priority_packet.py
  write_road_evidence_review_packet.py
  write_road_evidence_source_request_packet.py
  write_road_source_decision_packet.py
  write_road_source_readiness_packet.py
  write_road_speed_evidence.py
  write_route_road_evidence_exposure.py
  write_sensitivity_index_review_packet.py
  write_sensitivity_method_decision_packet.py
  write_sensitivity_review_packet.py
  write_sensitivity_strategy_readiness_packet.py
  write_source_context_cache_decision_packet.py
  write_source_context_cache_request_packet.py
  write_source_license_review_packet.py
  write_source_provenance_decision_packet.py
  write_source_provenance_priority_packet.py
  write_source_url_remediation_packet.py
  write_source_url_review_packet.py
  write_transfer_evidence_review_packet.py
  write_upstream_lineage_review_packet.py
  write_validation_benchmark_decision_packet.py
  write_validation_benchmark_readiness_packet.py
  write_validation_review_packet.py
  write_validation_strategy_readiness_packet.py
results/                   # Generated CSV outputs and PNG plots
  realworld_pilot/          # Separated pilot scaffold sample/staged/full outputs
cloned_repo/               # Public repo source snapshots for reference
docs/                      # Real-world pipeline, reproducibility, and audit records
```

`refs/` may be used for local reference clones if needed; keep it out of active
implementation and generated-output changes.

`cloned_repo/` contains source snapshots of public repositories with nested
`.git` metadata removed. Do not directly wire these snapshots into production
simulation imports. Extract design patterns and implement project-owned code in
`src/` instead.

## Windows Setup

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt
```

Optional Phase 10 ML/GPU runtime checks:

```powershell
.\.venv\Scripts\python -m pip install -r requirements-ml.txt
.\.venv\Scripts\python scripts\check_gpu_ml_runtime.py --package xgboost --requested-device cuda --requirements requirements-ml.txt --require-gpu
```

This optional check can support only a bounded post-simulation ML runtime claim.
It is not simulation acceleration evidence.

If `py -3.11` is unavailable, install Python 3.11+ for Windows and enable the
Python Launcher.

## How to Run

```powershell
.\.venv\Scripts\python main.py --test       # Single paired scenario debug
.\.venv\Scripts\python main.py --quick      # Smoke run, writes results/
.\.venv\Scripts\python main.py --phase 1    # Phase 1 only
.\.venv\Scripts\python main.py --phase 2    # Phase 2 only
.\.venv\Scripts\python main.py              # Full experiment
.\.venv\Scripts\python generate_report.py   # Regenerate report.docx
```

Direct test commands:

```powershell
.\.venv\Scripts\python tests\test_models.py
.\.venv\Scripts\python tests\test_config.py
.\.venv\Scripts\python tests\test_dispatch.py
.\.venv\Scripts\python tests\test_fleet.py
.\.venv\Scripts\python tests\test_traffic.py
.\.venv\Scripts\python tests\test_disruptions.py
.\.venv\Scripts\python tests\test_rail.py
.\.venv\Scripts\python tests\test_transfers.py
.\.venv\Scripts\python tests\test_metrics.py
.\.venv\Scripts\python tests\test_analysis.py
.\.venv\Scripts\python tests\test_scenario.py
.\.venv\Scripts\python tests\test_realworld_types.py
.\.venv\Scripts\python tests\test_realworld_attributes.py
.\.venv\Scripts\python tests\test_realworld_osm_network.py
.\.venv\Scripts\python tests\test_realworld_adapter.py
.\.venv\Scripts\python tests\test_realworld_validation.py
.\.venv\Scripts\python tests\test_realworld_end_to_end.py
.\.venv\Scripts\python tests\test_realworld_pilot_smoke.py
.\.venv\Scripts\python tests\test_realworld_full_graph_smoke.py
.\.venv\Scripts\python tests\test_realworld_rail_evidence.py
.\.venv\Scripts\python tests\test_realworld_parameters.py
.\.venv\Scripts\python tests\test_realworld_parameter_audit.py
.\.venv\Scripts\python tests\test_realworld_parameter_review_packet.py
.\.venv\Scripts\python tests\test_realworld_pilot_acceptance.py
.\.venv\Scripts\python tests\test_realworld_provenance_acceptance.py
.\.venv\Scripts\python tests\test_realworld_source_license_review_packet.py
.\.venv\Scripts\python tests\test_realworld_source_url_review_packet.py
.\.venv\Scripts\python tests\test_realworld_road_evidence.py
.\.venv\Scripts\python tests\test_realworld_road_evidence_diagnostics.py
.\.venv\Scripts\python tests\test_realworld_road_capacity_evidence.py
.\.venv\Scripts\python tests\test_realworld_road_speed_evidence.py
.\.venv\Scripts\python tests\test_realworld_road_evidence_review_packet.py
.\.venv\Scripts\python tests\test_realworld_road_evidence_request_packet.py
.\.venv\Scripts\python tests\test_realworld_road_overrides.py
.\.venv\Scripts\python tests\test_realworld_road_override_template.py
.\.venv\Scripts\python tests\test_realworld_road_override_audit.py
.\.venv\Scripts\python tests\test_realworld_rail_evidence_review_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_timing_request_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_station_binding.py
.\.venv\Scripts\python tests\test_realworld_rail_station_cache.py
.\.venv\Scripts\python tests\test_realworld_rail_timetable.py
.\.venv\Scripts\python tests\test_realworld_rail_timetable_api.py
.\.venv\Scripts\python tests\test_realworld_rail_gtfs.py
.\.venv\Scripts\python tests\test_realworld_rail_shortest_path.py
.\.venv\Scripts\python tests\test_realworld_rail_shortest_path_api.py
.\.venv\Scripts\python tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python tests\test_realworld_plausibility.py
.\.venv\Scripts\python tests\test_realworld_disruption_scenarios.py
.\.venv\Scripts\python tests\test_realworld_policy_alternatives.py
.\.venv\Scripts\python tests\test_realworld_pilot_experiments.py
.\.venv\Scripts\python tests\test_realworld_sensitivity.py
.\.venv\Scripts\python tests\test_realworld_sensitivity_review_packet.py
.\.venv\Scripts\python tests\test_realworld_osrm_snapshot_manifest.py
.\.venv\Scripts\python tests\test_realworld_validation_review_packet.py
.\.venv\Scripts\python tests\test_realworld_validation_strategy_readiness_packet.py
.\.venv\Scripts\python tests\test_realworld_route_road_evidence_exposure.py
.\.venv\Scripts\python tests\test_realworld_upstream_lineage_review_packet.py
.\.venv\Scripts\python tests\test_realworld_pilot_figures.py
.\.venv\Scripts\python tests\test_realworld_formal_acceptance_evidence_matrix.py
.\.venv\Scripts\python tests\test_realworld_seed_stream_manifest.py
.\.venv\Scripts\python tests\test_realworld_crn_pairing_audit.py
.\.venv\Scripts\python tests\test_realworld_replication_adequacy_audit.py
.\.venv\Scripts\python tests\test_realworld_review_package_inventory.py
.\.venv\Scripts\python tests\test_realworld_review_package_builder.py
.\.venv\Scripts\python tests\test_realworld_review_package_handoff.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
```

Batch form:

```powershell
Get-ChildItem tests\test_*.py | ForEach-Object { .\.venv\Scripts\python $_.FullName }
```

## Key Models

- **BPR**: `t = t0 * (1 + alpha * (s * v / C)^beta)`; defaults are
  `alpha=0.15`, `beta=4.0`.
- **Dynamic road volume**: `traffic.background_volume` plus rolling-window
  simulated vehicle entries converted to vehicles/hour.
- **Link failure**: road-link probability is
  `min(edge_base_p_fail * p_fail_scale, 1.0)`.
- **Failure modes**: `blocked` gives infinite traversal time; `capacity_reduction`
  multiplies effective road capacity by `failure.capacity_reduction_factor`.
- **Rail failure**: rail is immune by default.
- **Lateness**: `Y ~ LogNormal(mu=2.0, sigma^2)`; sigma controls long-tail
  arrival delay.
- **STRICT policy**: depart immediately at scheduled time with arrived
  passengers only.
- **GRACE policy**: wait until max `W` minutes, `theta` fraction arrived, or
  vehicle capacity reached.
- **CRN pairing**: paired bus-only and multimodal replications use the same
  seed. The scenario runner uses separate arrival and failure RNG streams
  derived from that seed.

## Config Schema Notes

`config.yaml` keeps legacy experiment keys and includes scenario-runner namespaces
used by the current scenario runner:

- `bus.first_departure_min`, `bus.dispatch_interval_min`,
  `bus.fleet_size`, `bus.turnaround_min`
- `multimodal.shuttle_first_departure_min`,
  `multimodal.shuttle_dispatch_interval_min`,
  `multimodal.shuttle_fleet_size`, `multimodal.transfer_time_min`,
  `multimodal.transfer_per_passenger_min`,
  `multimodal.rail_first_departure_min`,
  `multimodal.lastmile_first_departure_min`,
  `multimodal.lastmile_dispatch_interval_min`,
  `multimodal.lastmile_fleet_size`,
  `multimodal.lastmile_turnaround_min`,
  `multimodal.lastmile_vehicle_capacity`
- `traffic.volume_window_min`, `traffic.background_volume`
- `failure.mode`, `failure.capacity_reduction_factor`
- `metrics.late_penalty_min`
- `experiment.R`, `experiment.seed_base`, `experiment.time_limit`

`failure_rate.levels` are `p_fail_scale` multipliers, not actual probabilities.
Keep `failure_rate.parameter` and `failure_rate.semantics` aligned with that
behavior unless the model code is deliberately changed.

Config check guidance:

- Run `.\.venv\Scripts\python tests\test_config.py` after schema edits.
- Keep minute fields non-negative and fleet sizes at least 1.
- Keep `traffic.volume_window_min > 0`.
- Use `failure.mode: blocked` or `failure.mode: capacity_reduction`.
- Keep `0 < failure.capacity_reduction_factor <= 1`.

Config includes finite last-mile fleet controls, explicit first-departure
schedule controls, network variant selection, and expanded failure-sensitivity
dimensions. Keep documentation aligned with the implemented code and tests.

## Implemented Design Fixes

- STRICT and GRACE now operate on passenger queues rather than waiting for the
  last passenger in a pre-batched group.
- Bus-only and multimodal shuttle dispatch use configurable fleet size, dispatch
  interval, and turnaround.
- Multimodal last-mile dispatch uses a finite fleet, vehicle capacity, dispatch
  interval, turnaround, and optional first-departure anchor.
- Rail departures follow fixed headway and are not serialized by earlier train
  travel. `multimodal.rail_first_departure_min` can pin the first scheduled
  train departure when needed.
- Road travel uses dynamic per-link traffic volume with BPR travel time at edge
  entry.
- Failure sampling supports `blocked` and `capacity_reduction` modes.
- Multimodal transfers include configurable fixed and per-passenger delay.
- Metrics include explicit censoring KPIs: `censored_count`, `completion_rate`,
  and `penalized_makespan`.

## Implemented Real-World MVP

`src/realworld/` now contains an opt-in real-world or quasi-real input pipeline.
It does not change the default abstract-network experiments unless a caller
explicitly builds and passes an adapted graph.

Implemented behavior:

- `src/realworld/acceptance_records.py` and
  `src/realworld/acceptance_orchestration.py` provide a repo-native
  sub-agent review system for blocked final-study gates. Running
  `scripts/run_acceptance_audit.py` refreshes review packets, writes
  `agents/acceptance_review_agents.json`,
  `schemas/acceptance_record.schema.json`,
  `data/manifests/acceptance_orchestration_manifest.json`, 12 review-agent
  records under `data/manifests/agent_reviews/`, and human packets under
  `docs/review_packets/`. These are review aids only and do not create formal
  acceptance.
- `src/realworld/acceptance_decision_templates.py` and
  `scripts/write_acceptance_decision_templates.py` generate non-approval
  templates for missing formal acceptance decisions: 9 JSON templates under
  `data/manifests/acceptance_templates/`, a 25-row
  `data/parameters/parameter_acceptance_template.csv`, an aggregate
  `data/manifests/acceptance_decision_template_manifest.json`, and
  `docs/acceptance_decision_templates.md`. These keep `accepted: false` and
  must not be treated as accepted reviewer decisions.
- `docs/human_acceptance_runbook.md` gives human reviewers the gate-by-gate
  workflow for moving from review packets and non-approval templates to formal
  acceptance artifacts. It is instructional only and cannot approve a gate.
- `src/realworld/acceptance_blocker_queue.py` and
  `scripts/write_formal_acceptance_blocker_queue.py` write
  `data/manifests/formal_acceptance_blocker_queue.csv`,
  `data/manifests/formal_acceptance_blocker_queue_manifest.json`, and
  `docs/formal_acceptance_blocker_queue.md`.
  `scripts/write_acceptance_blocker_queue.py` remains the compatibility
  implementation behind that explicit command. These rows are reviewer work
  items only; they do not create approvals.
- `src/realworld/acceptance_task_assignments.py` and
  `scripts/write_acceptance_task_assignments.py` map formal blocker rows to
  deterministic review-agent roles and write
  `data/manifests/acceptance_task_assignments.csv`,
  `data/manifests/acceptance_task_assignments_manifest.json`, and
  `docs/acceptance_task_assignments.md`. These assignments are work allocation
  only; they cannot approve evidence or close gates.
- `src/realworld/formal_acceptance_evidence_matrix.py` and
  `scripts/write_formal_acceptance_evidence_matrix.py` join each formal target
  with its assigned agent, template or worksheet, review packets, current
  blockers, source paths, and validation command. The matrix is reviewer
  intake only and cannot approve evidence.
- `src/realworld/formal_acceptance_guard.py` and
  `scripts/audit_formal_acceptance_artifacts.py` guard the formal target
  paths against copied templates, unresolved `REVIEW_REQUIRED` placeholders,
  and draft-only weak road override rows. The current local guard reports 0
  formal target files present, 12 missing, and 0 template/placeholder copies in
  formal paths; it cannot mark study closeout complete.
- `src/realworld/formal_acceptance_package.py` and
  `scripts/validate_formal_acceptance_package.py` aggregate reviewer-supplied
  formal target artifacts into one intake audit. The generated
  `data/manifests/formal_acceptance_package_audit.json` and
  `docs/formal_acceptance_package_audit.md` are intake-check outputs only; they
  do not create approvals or bypass the study-closeout preflight audit.
- `src/realworld/formal_evidence_path_audit.py` and
  `scripts/audit_formal_evidence_paths.py` inspect reviewer-supplied formal
  artifacts for missing local evidence paths, unresolved placeholders, empty
  evidence records, and external references that still need source/license
  review. The generated `data/manifests/formal_evidence_path_audit.json` and
  `docs/formal_evidence_path_audit.md` are path-hygiene checks only, not
  evidence sufficiency or acceptance.
- Region records check bbox boundaries, assembly/destination zones, rail
  access and egress points, fixed rail travel time, headway, and train
  capacity.
- OSM-style edge attributes are mapped deterministically to simulator fields:
  `t0`, `capacity`, `base_p_fail`, `p_fail`, `mode`, and metadata.
- The real-world adapter filters pedestrian, cycling, platform, construction,
  track, living-street, and service-only OSM geometries out of bus-practical
  simulator routes before zone snapping.
- `osm_network.py` supports offline GraphML load/save with NetworkX and lazy
  optional OSMnx bbox extraction for manual live OSM use.
- Zone and rail points snap to nearest road nodes using OSMnx-style `x`/`y`
  lon/lat coordinates, then receive bidirectional connector edges.
- `build_simulator_graph(...)` emits a routeable `networkx.DiGraph` for the
  current `run_scenario(...)` call surface.
- Current pilot graph scale is: 13,268 raw OSM-cache nodes / 28,947 raw edges,
  4,608 bus-practical simulator nodes / 9,148 simulator edges after filtering,
  and 118 analysis-corridor nodes / 174 edges in the current sample/staged/full
  pilot experiment outputs.
- `src/realworld/graph_scale_acceptance.py` checks the optional
  `data/manifests/graph_scale_acceptance.json` review record required before a
  reduced corridor, full-graph runtime, or multi-corridor ensemble can close
  the study-closeout graph-scale strategy gate. This file is absent in the current
  scaffold.
- `src/realworld/graph_scale_diagnostics.py` and
  `scripts/run_graph_scale_diagnostics.py` compare the canonical baseline road
  legs `A -> D`, `A -> S`, and `R -> D` on the full bus-practical graph and
  reduced analysis corridor. Current rows all pass for shortest-time path
  preservation, but this is route-parity scaffold evidence only and not
  graph-scale acceptance.
- The same graph-scale diagnostic run also writes alternate-route sensitivity
  rows. Current output has 9 rows: 3 rank-1 pass rows and 6 alternate-route
  warning rows. Treat those warning rows as corridor-abstraction uncertainty,
  not operational detour evidence.
- A multi-corridor candidate graph preserving the top 3 full-graph route
  candidates per canonical leg is also diagnosed. Current output has 9 pass
  rows on a 164-node / 246-edge candidate graph. Treat it as an upgrade path,
  not graph-scale acceptance.
- `src/realworld/graph_scale_review.py` and
  `scripts/write_graph_scale_review_packet.py` summarize the current reduced
  corridor, 164-node / 246-edge small multi-corridor candidate, 164-node /
  246-edge full-profile multi-corridor candidate, and full-graph options into
  a 4-row review worksheet. Treat it as graph-scale method review support
  only, not acceptance.
- `src/realworld/graph_scale_strategy_readiness_packet.py` and
  `scripts/write_graph_scale_strategy_readiness_packet.py` classify the
  current graph-scale method options into blocker and human-review states
  without choosing or accepting the source-vs-analysis graph.
- `src/realworld/graph_scale_result_comparison.py` and
  `scripts/write_graph_scale_result_comparison.py` compare the current full
  pilot summary with the full-profile multi-corridor candidate summary. Treat
  the 819-row delta table as graph-scale review support only, not acceptance.
- `src/realworld/validation_acceptance.py` checks the optional
  `data/manifests/validation_acceptance.json` review record required before
  route plausibility and external benchmark evidence can close the study-closeout
  evidence-check package gate. This file is absent in the current scaffold.
- `validate_graph_readiness(...)` and `assert_graph_ready(...)` check required
  nodes, edge fields, numeric values, and road-mode routes.
- A first offline pilot scaffold exists for `songpa_public_demo`:
  `data/regions/pilot_region.yaml`,
  `data/cache/pilot_region_road.graphml`,
  `data/cache/pilot_region_road_manifest.json`,
  `docs/pilot_region_data_card.md`, `scripts/build_pilot_cache.py`,
  `scripts/run_pilot_smoke.py`, and `tests/test_realworld_pilot_smoke.py`.
- Parameter-source tables, route plausibility checks, structured disruption
  scenarios, and policy-alternative definitions now exist under
  `data/parameters/`, `data/validation/`, and `data/scenarios/`, with
  validators in `src/realworld/`.
- `src/realworld/parameter_audit.py` and
  `scripts/audit_parameter_evidence.py` keep valid source tables separate from
  study-closeout preflight status. The current audit has no missing core parameters but
  still reports weak expert/sensitivity-only evidence for closeout claims.
- `src/realworld/parameter_review_packet.py` and
  `scripts/write_parameter_review_packet.py` turn the audit into a generated
  29-row review worksheet. The current packet marks 25 core parameters as weak
  for study-level claims and remains review support only.
- `src/realworld/parameter_evidence_request_packet.py` and
  `scripts/write_parameter_evidence_source_request_packet.py` produce a 7-row
  source-request worksheet for cross-cutting demand, fleet, dispatch,
  transfer, rail, disruption, and traffic/BPR evidence. It is request support
  only and does not accept weak parameters.
- `src/realworld/parameter_acceptance.py` checks optional
  `data/parameters/parameter_acceptance.csv` review records for weak
  assumptions that are explicitly retained inside closeout claim boundaries. This
  file is absent in the current scaffold.
- `src/realworld/pilot_acceptance.py` checks the optional
  `data/manifests/pilot_acceptance.json` review record. The file is absent in
  the current scaffold so the study-closeout gate remains blocked until a real
  signoff decision is recorded.
- `src/realworld/provenance_acceptance.py` checks the optional
  `data/manifests/provenance_acceptance.json` review record required before
  source snapshot, license/attribution, privacy abstraction, cache manifest,
  reproducibility manifest, and not-operational claim-boundary review can close
  the study-closeout data-provenance gate. This file is absent in the current scaffold.
- `src/realworld/manuscript_acceptance.py` checks the optional
  `data/manifests/manuscript_acceptance.json` review record required before
  English manuscript, Korean report, regenerated docx, figure/table manifest,
  evidence-gate, result-claim, and not-operational claim-boundary review can
  close the study-closeout manuscript/report gate. This file is absent in the current
  scaffold.
- `src/realworld/claim_alignment_review_packet.py` and
  `scripts/write_claim_alignment_review_packet.py` generate a claim-level
  review worksheet for `paper/paper_draft.md`, `report_draft.md`, and the
  figure/table manifest. It is review support only and does not create
  `manuscript_acceptance.json`.
- `src/realworld/reproducibility_acceptance.py` checks the optional
  `data/manifests/reproducibility_acceptance.json` review record required
  before clean-checkout reproduction checks, evidence-check ladder, artifact regeneration,
  manifest paths, cloned-repo import-boundary, command count, and
  not-operational claim-boundary review can close the study-closeout reproducibility
  gate. This file is absent in the current scaffold.
- `src/realworld/reproducibility_smoke.py` and
  `scripts/run_reproducibility_smoke.py` run a bounded current-worktree smoke
  ladder. Current output has 20 passing commands in
  `data/validation/reproducibility_smoke_manifest.json` and a JSONL command
  log, but `clean_checkout_test_performed` and `can_mark_complete` remain
  false.
- `src/realworld/final_audit_acceptance.py` checks the optional
  `data/manifests/final_audit_acceptance.json` review record required before
  independent prompt-to-artifact completion review, gate evidence review,
  no-proxy completion review, gate-list/count matching, and not-operational
  claim-boundary review can close the closeout audit gate. This file is absent in
  the current scaffold.
- `src/realworld/road_evidence.py` and `scripts/audit_road_evidence.py` audit
  the cached OSM/GraphML road input. Current lengths are parseable, but speed,
  capacity, and base-disruption values still rely heavily on proxies.
- `src/realworld/road_evidence_diagnostics.py` and
  `scripts/audit_road_evidence_diagnostics.py` rank routeable highway classes
  by speed, capacity, and base-disruption evidence gaps so reviewed road-class
  overrides target the highest-impact roads first.
- `src/realworld/road_speed_evidence.py` and
  `scripts/write_road_speed_evidence.py` summarize sparse cached OSM
  `maxspeed` tags by routeable road class. The current table has 10 candidate
  rows and 5 rows with observed tags; it is review support only.
- `src/realworld/road_capacity_evidence.py` and
  `scripts/write_road_capacity_evidence.py` summarize cached OSM `lanes` tags
  by routeable road class. The current table has 10 candidate rows and 0 rows
  with observed lane tags; it documents the remaining capacity evidence gap.
- `src/realworld/road_attribute_evidence.py` and
  `scripts/write_road_attribute_evidence.py` write an edge-level
  road-attribute evidence table and manifest. The table separates OSM-derived
  values, mapper fallbacks, lane-derived capacity candidates, optional routing
  benchmark fields, and sensitivity-only disruption probabilities. It is
  review support only and does not create source-tuned road overrides or formal
  signoff.
- `src/realworld/road_evidence_review_packet.py` and
  `scripts/write_road_evidence_review_packet.py` consolidate the road-class
  diagnostics, sparse speed evidence, lane-count evidence, and draft override
  rows into a 10-row review worksheet. All current rows remain weak for
  study-level road claims and are review support only.
- `src/realworld/road_evidence_request_packet.py` and
  `scripts/write_road_evidence_source_request_packet.py` write a 5-row
  source-request worksheet for the missing speed, capacity, benchmark,
  disruption, and override-application source inputs. It is request support
  only and does not create reviewed road overrides.
- `src/realworld/road_overrides.py` checks optional road-class override
  tables so future source-backed speed, capacity, and disruption inputs can
  replace mapper fallbacks without changing simulation internals.
- `src/realworld/road_override_template.py` and
  `scripts/write_road_class_override_template.py` can create a draft
  non-acceptance override template from diagnostics. The current
  `data/parameters/road_class_overrides_draft.csv` has 10
  expert-assumption rows; it is a reviewer work aid and not calibrated road
  evidence.
- `src/realworld/road_override_audit.py` and `scripts/audit_road_overrides.py`
  report that no reviewed default override table is currently present and no
  accepted pilot manifest applies one.
- `scripts/run_osrm_route_benchmark.py` provides an optional OSRM benchmark
  snapshot path. It is not part of default offline tests and must be treated as
  plausibility evidence, not ground truth.
- `scripts/write_osrm_snapshot_manifest.py` records the cached OSRM CSV and
  summary checksums, row-level query URLs, live/unpinned status, and
  non-acceptance claim boundary.
- `src/realworld/road_snapshot.py` and `scripts/write_road_snapshot.py` write
  a road-network snapshot summary for the cached graph so later audits can
  compare node/edge counts, routeable edge counts, highway classes, and graph
  metadata without treating the cache as calibrated road evidence.
- `scripts/run_full_graph_smoke.py` runs a tiny bus-only and baseline
  multimodal smoke on the full bus-practical graph without corridor reduction;
  this is feasibility evidence only.
- `scripts/run_graph_scale_diagnostics.py` writes the full-vs-reduced
  route-parity, alternate-route, and multi-corridor candidate CSVs and
  summaries under `data/validation/`; this supports review of the corridor
  abstraction but does not close the graph-scale gate.
- `scripts/write_graph_scale_review_packet.py` writes a 4-option graph-scale
  method worksheet and manifest under `data/validation/`; this helps choose
  between reduced-corridor, small multi-corridor, full-profile
  multi-corridor, and full-graph methods but does not close the graph-scale
  gate.
- `scripts/write_graph_scale_strategy_readiness_packet.py` writes a 5-row
  graph-scale strategy-blocker-review packet and manifest under `data/validation/`;
  this makes graph-method blockers concrete but does not close the graph-scale
  gate.
- `scripts/write_graph_scale_result_comparison.py` writes the 819-row
  current-vs-full-profile-candidate graph-scale result-delta table and
  manifest under `data/validation/`; this helps review graph choice impact but
  does not close the graph-scale gate.
- `data/parameters/rail_service_evidence.csv` and
  `scripts/audit_rail_evidence.py` record that current rail timing values are
  still an assumption proxy, while rail capacity is explicitly sensitivity-only.
  This is not cached timetable or GTFS-derived timing evidence.
- `src/realworld/rail_evidence_review_packet.py` and
  `scripts/write_rail_evidence_review_packet.py` consolidate station-binding
  review status, timing gaps, capacity treatment, service-window assumptions,
  availability assumptions, and derivation paths into a 10-row review
  worksheet. It is review support only and keeps service publication status
  false.
- `src/realworld/rail_timing_request_packet.py` and
  `scripts/write_rail_timing_source_request_packet.py` write a 5-row request
  worksheet naming required API-key, GTFS, capacity, and rail-availability
  inputs before cached rail timing evidence can be derived. It is not evidence.
- `data/rail/pilot_station_binding_cache.csv`,
  `data/parameters/rail_station_bindings.csv`, and
  `scripts/audit_rail_station_bindings.py` record official line-specific
  station-code bindings for `S` and `R`. This is station binding only, not
  rail service, headway, travel-time, capacity, or route-availability evidence.
- `src/realworld/rail_station_cache.py` and
  `scripts/derive_rail_station_bindings.py` provide the offline parser needed
  to regenerate those rows from a reviewed official station extract.
- `src/realworld/rail_timetable.py` and
  `scripts/derive_rail_service_evidence.py` provide the offline parser needed
  once a reviewed station-event timetable extract is available. Derived rows
  record field-level timing evidence and source artifact SHA256. They do not
  make the current shipped rail row derived.
- `scripts/derive_rail_headway_evidence.py` can derive headway-only evidence
  from reviewed access-station timetable rows without claiming travel-time
  evidence. `src/realworld/rail_timetable_api.py` and
  `scripts/fetch_rail_timetable_cache.py` provide an optional key-required
  data.go.kr train-schedule fetch path for creating the local cache. This is
  not part of default offline checks.
- `src/realworld/rail_timetable_static.py` and
  `scripts/normalize_rail_timetable_cache.py` can normalize a reviewed static
  timetable CSV into the local timetable cache schema only when exact source
  column mappings are provided. This is a cache-preparation adapter only; it
  does not create rail evidence, publication readiness, final-study readiness,
  or formal acceptance.
- `src/realworld/rail_gtfs.py` and `scripts/derive_rail_gtfs_evidence.py`
  can derive scheduled headway and access-to-egress travel-time evidence from
  a reviewed static GTFS zip or directory, preserving source artifact SHA256.
  No reviewed GTFS feed is committed for the current pilot, so this path does
  not close the rail evidence gate yet.
- `src/realworld/rail_shortest_path.py` and
  `scripts/derive_rail_shortest_path_evidence.py` provide the offline parser
  needed once a reviewed station-to-station shortest-path extract is available.
  Derived rows record travel-time evidence only, verify station codes against
  official rail-point bindings, and preserve source artifact SHA256.
- `src/realworld/rail_shortest_path_api.py` and
  `scripts/fetch_rail_shortest_path_cache.py` provide the optional
  key-required data.go.kr fetch path for creating that local cache from a
  reviewed live request. This is not part of default offline validation and
  does not close rail-service evidence until the cache and raw response are
  reviewed.
- `scripts/run_pilot_experiments.py --sample` connects the pilot graph,
  disruption scenarios, and policy alternatives into separated scaffold sample
  outputs under `results/realworld_pilot/`.
- `scripts/run_pilot_experiments.py --multi-corridor` runs the separated
  multi-corridor candidate profile on the 164-node / 246-edge candidate graph
  and writes `pilot_multi_corridor_*` outputs for graph-scale review only.
- `scripts/run_pilot_experiments.py --multi-corridor-full` runs the same
  candidate graph on the full 7-policy, 9-scenario, 30-seed matrix and writes
  `pilot_multi_corridor_full_*` outputs for stronger graph-scale review only.
- `src/realworld/experiment_acceptance.py` checks the optional
  `data/manifests/experiment_acceptance.json` review record required before
  staged/full pilot outputs can close the study-closeout full-experiment-output gate.
  This file is absent in the current scaffold.
- `src/realworld/experiment_package_review_packet.py` and
  `scripts/write_experiment_package_review_packet.py` generate a full
  experiment output worksheet covering manifest/result/summary row counts,
  scenario-policy-seed design counts, graph scope, input dependencies, CRN
  declaration, checksums, and formal acceptance absence without accepting the
  experiment package.
- `src/realworld/experiment_strategy_readiness_packet.py` and
  `scripts/write_experiment_strategy_readiness_packet.py` convert that
  worksheet into 9 pre-review status rows. The packet keeps scaffold result
  scope, graph-scale dependency, upstream input-evidence dependency,
  row-count/checksum/design/CRN review, and missing experiment acceptance
  visible without accepting full outputs.
- `scripts/run_sensitivity.py --sample` runs deterministic one-at-a-time
  scaffold screening and writes SALib-compatible manifest metadata.
- `scripts/run_sensitivity.py --method morris --all` runs SALib Morris
  screening for the current full policy/scenario scaffold and writes
  `morris_*` outputs.
- `scripts/audit_sensitivity_diagnostics.py` reports Morris count consistency,
  blank/non-finite index values, zero `mu_star` rows, reduced graph scope, and
  scaffold claim boundaries without accepting study-closeout sensitivity claims.
- `src/realworld/sensitivity_review_packet.py` and
  `scripts/write_sensitivity_review_packet.py` convert those diagnostics into
  a 6-row review worksheet that keeps index handling, zero-effect
  interpretation, reduced graph scope, and the Morris-vs-Sobol decision
  visible without closing the sensitivity gate.
- `src/realworld/sensitivity_strategy_readiness_packet.py` and
  `scripts/write_sensitivity_strategy_readiness_packet.py` convert that
  6-row worksheet into 7 pre-review status rows. The packet keeps
  missing/non-finite indices, zero `mu_star` interpretation, reduced graph
  scope, scaffold result scope, Morris-vs-Sobol decision, and missing
  sensitivity acceptance visible without accepting closeout sensitivity evidence.
- `src/realworld/validation_review_packet.py` and
  `scripts/write_validation_review_packet.py` convert route plausibility,
  fallback/OSRM benchmark, OSRM snapshot manifest, accessibility-loss,
  route-level road-evidence exposure, and evidence-summary scope artifacts
  into a 7-row review
  worksheet without closing the evidence-check gate.
- `src/realworld/validation_strategy_readiness_packet.py` and
  `scripts/write_validation_strategy_readiness_packet.py` convert that 7-row
  evidence-check worksheet into pre-review statuses. The packet keeps
  internal warnings, fallback benchmark warnings, unpinned OSRM snapshot risk,
  accessibility diagnostics, weak route-road evidence exposure, summary scope,
  and missing validation acceptance visible without approving a benchmark
  strategy.
- `src/realworld/route_road_evidence_exposure.py` and
  `scripts/write_route_road_evidence_exposure.py` generate a 76-row
  route-level worksheet that links weak road speed, capacity, disruption, and
  connector assumptions to canonical route candidates. This is review support
  only, not source-tuning or evidence-check signoff.
- `scripts/make_pilot_statistics.py` writes full-pilot metric confidence
  intervals and paired policy-delta confidence intervals from seed replications;
  these are uncertainty summaries for scaffold outputs, not calibration proof.
- `src/realworld/sensitivity_acceptance.py` checks the optional
  `data/manifests/sensitivity_acceptance.json` review record required before
  current Morris or future Sobol outputs can close the closeout sensitivity gate.
  This file is absent in the current scaffold.
- `scripts/make_pilot_figures.py` generates scaffold-only figures, tables, and
  a claim-boundary table from current full pilot and Morris outputs, including
  bottleneck attribution proxy and policy regime-map artifacts.
- `src/realworld/artifact_invalidation_matrix.py` and
  `scripts/write_artifact_invalidation_matrix.py` write the Phase 9 stale
  artifact disposition matrix for compact/full outputs, statistics, ML outputs,
  figures, reports, and review packages. The matrix is preflight review support
  only; unresolved rows block non-sample promotion but do not regenerate
  artifacts, assess evidence quality, or create publication/study-closeout/formal
  signoff. With `--write-closeout-template`, the same script also writes a
  pending reviewer closeout worksheet that records disposition, affected
  artifacts or exclusion scope, rerun/audit/test evidence, reviewer signoff,
  and claim-boundary effects. The closeout worksheet is still non-acceptance
  review support and defaults every row to pending. With
  `--write-closeout-action-queue`, the script also writes dependency-ordered
  closeout work guidance; that queue does not close rows, approve evidence, or
  authorize Phase 9. With `--write-quarantine-closeout-template`, the script
  writes a separate six-row reviewer input template for the immediate
  `quarantine_non_evidence` batch. That quarantine template is not the main
  closeout manifest and cannot clear Phase 9 by itself. With
  `--write-quarantine-scope-audit`, the script writes finding-row support for
  stale artifact candidates, ZIP candidates, and claim-text reference hits for
  that same batch. The scope audit records
  `must_not_be_used_as_closeout_manifest=true` and must not be used as closeout
  evidence. With `--write-quarantine-non-evidence-index`, the script writes a
  deduplicated stale full-output/review-package candidate index for reviewer
  triage only. That index also records
  `must_not_be_used_as_closeout_manifest=true`; it does not close rows,
  approve citation removal, or authorize Phase 9.
- `src/realworld/gpu_ml_runtime.py` and
  `scripts/check_gpu_ml_runtime.py` write a Phase 10 optional GPU ML runtime
  preflight manifest, JSONL log, and Markdown note. The guard records
  `nvidia-smi`, Python, `pip check`, selected package versions, a
  package-specific CUDA check where supported, and CPU fallback status. It is
  runtime evidence for bounded post-simulation ML claims only; it does not
  prove the SimPy/NetworkX simulator is GPU-accelerated, does not assess ML
  model quality, and does not create publication/study-closeout/formal signoff.
- `scripts/audit_plan_artifacts.py` checks current scaffold artifact row
  counts, JSON manifests, docs, parameter evidence status, and the
  conservative claim boundary.
- `scripts/audit_source_provenance.py` checks the non-acceptance source
  provenance review packet for source URLs, license/terms notes, local
  artifacts, review statuses, and claim boundaries.
- `scripts/audit_source_context_hashes.py` writes a source-context raw-file
  hash audit for cached KTDB GTFS and Metro9 review extracts. It checks hash
  integrity only and does not assess GTFS, sign off rail capacity, certify
  licenses, or close provenance gates.
- `scripts/write_pilot_privacy_review_packet.py` writes a pilot-region
  privacy and sensitivity worksheet from the region YAML and data card. It is
  review support only and does not create pilot acceptance.
- `scripts/write_source_license_review_packet.py` writes a source-by-source
  license, attribution, snapshot, privacy, and reproducibility review
  worksheet from the source provenance manifest. It is review support only and
  does not certify license compatibility or create provenance acceptance.
- `scripts/write_source_url_review_packet.py` writes URL-level source review
  rows from the source provenance manifest. The default output is offline
  parse-only; optional live reachability checks are volatile review aids and do
  not certify licenses or create provenance acceptance.
- `scripts/write_claim_alignment_review_packet.py` writes manuscript/report
  claim-alignment rows for guarded language and overclaim candidates. It is
  review support only and does not create manuscript acceptance.
- `scripts/audit_claim_language.py` writes a fail-closed lexical
  claim-language guard for reports, docs, and manifests. It blocks release
  when reserved claim terms are not formally supported or explicitly bounded.
- `scripts/audit_publication_readiness.py` aggregates parameter, road, rail
  service, and station-binding gates while preserving a false publication-status
  field until evidence blockers are closed.
- `scripts/audit_final_study_readiness.py` checks all `plan.md` study-closeout
  gates and keeps scaffold artifact presence separate from study-closeout
  preflight status for pilot signoff, graph scale, evidence, evidence checks,
  experiment, sensitivity, manuscript/report, reproducibility, and closeout
  audit requirements.
- `docs/schemas/graph_scale_acceptance_schema.md` defines the graph-scale acceptance
  record shape; do not create the actual acceptance JSON unless a real review
  has signed off the source-vs-analysis graph decision and claim boundary.
- `docs/graph_scale_diagnostics.md` documents the route-parity and
  alternate-route diagnostics plus their claim boundaries; keep it distinct
  from graph-scale signoff.
- `docs/graph_scale_review_packet.md` documents the 4-option graph-scale
  method review packet; keep it distinct from graph-scale signoff.
- `docs/graph_scale_result_comparison.md` documents the current-vs-candidate
  graph-scale result-delta table; keep it distinct from graph-scale
  signoff.
- `docs/schemas/validation_acceptance_schema.md` defines the evidence-check
  signoff record shape; do not create the actual acceptance JSON unless a real review
  has signed off the benchmark strategy and its not-ground-truth limitation.
- `docs/schemas/experiment_acceptance_schema.md` defines the experiment-output
  acceptance record shape; do not create the actual acceptance JSON unless a
  real review has signed off graph scope, input evidence checks,
  scenario-policy-seed design, CRN pairing, counts, and not-operational claim
  limits.
- `docs/schemas/provenance_acceptance_schema.md` defines the data-provenance
  acceptance record shape; do not create the actual acceptance JSON unless a
  real review has signed off source snapshots, license/attribution, privacy
  abstraction, cache manifests, reproducibility paths, and not-operational
  claim limits.
- `docs/schemas/manuscript_acceptance_schema.md` defines the manuscript/report
  acceptance record shape; do not create the actual acceptance JSON unless a
  real review has signed off paper/report text, regenerated docx, figures/tables,
  evidence gates, result claims, and not-operational claim limits.
- `docs/schemas/reproducibility_acceptance_schema.md` defines the clean-checkout
  reproducibility acceptance record shape; do not create the actual acceptance
  JSON unless a real clean-checkout reproduction review has signed off reproduction
  commands, regenerated artifacts, manifest paths, import boundaries, and
  not-operational claim limits.
- `docs/schemas/final_audit_acceptance_schema.md` defines the independent closeout-audit
  signoff record shape; do not create the actual acceptance JSON unless a
  real closeout audit has reviewed every prompt-to-artifact requirement and all
  pre-closeout gates are closed.
- `docs/reproducibility_package.md` and
  `data/manifests/reproducibility_manifest.json` record reproduction commands,
  artifact paths, and claim limits for the current scaffold-only package.
- `docs/reproducibility_smoke.md` summarizes the bounded current-worktree
  smoke run. It is execution evidence only and must not be treated as
  clean-checkout reproducibility acceptance.
- `docs/plan_completion_audit.md` records a static gate-by-gate audit snapshot
  and remaining study-closeout blockers.

Treat outputs from this path as quasi-real decision-support experiments until
pilot data, travel-time assumptions, capacity proxies, rail inputs, and
disruption assumptions are source-checked. The current pilot scaffold, evidence
tables, sample/staged/full outputs, sensitivity screening, and generated figure/table
artifacts prove offline execution and study scaffolding only; do not claim
source-tuned real-world or field-use accuracy.

## Implemented Model Alignment

The implemented model includes finite last-mile fleet modeling, explicit
schedule semantics, unit-consistent resource KPIs, named network variants, and
expanded failure sensitivity. If these semantics change again, rerun Phase 1/2
before updating result conclusions.

Current full generated outputs contain 8,400 Phase 1 rows and 840 Phase 2 rows.
The default Phase 1 sweep includes only `baseline` and `matched_redundancy`;
`multimodal_redundant_lastmile` and `bus_single_corridor` are declared
selectable sensitivity variants outside the current default full result set.

## Current Research Upgrade Direction

The first real-world MVP, offline public-coordinate pilot smoke path,
parameter-source tables, plausibility checks, disruption scenarios, policy
alternatives, sample/staged/full pilot experiment profiles and outputs,
deterministic sensitivity screening, SALib Morris scaffold screening, and scaffold-only
figures/tables, plus sparse OSM maxspeed, lane-count candidate evidence, and a
consolidated road-input review packet for road-class review, now exist. The next major
implementation goal is to review the current OSM-derived cache as a
reviewer-cleared pilot snapshot or replace it with a better snapshot, review
staged/full pilot outputs, and document each input as
public-data-derived, literature-supported, expert-assumption, benchmarked, or
sensitivity-only.

Priority implementation layers:

1. **Pilot-region input package** by reviewing the current cached OSM/GraphML
   snapshot with region specs and reviewed zone
   connectors.
2. **Open-data regional network enrichment** using Pyrosm, GeoPandas/Shapely,
   and zone abstraction such as H3/admin-grid cells.
3. **Spatially structured disruptions** using critical-link scenarios and
   hazard/exposure overlays inspired by `snail` and `open-gira`.
4. **Public transit and rail source checks** using GTFS where available, or a
   documented rail-assumption table when GTFS is incomplete.
5. **Plausibility benchmarking** with routing or multimodal tools such as
   OSRM, Valhalla, routingpy, r5py/R5, or UXsim as appropriate. The current
   optional OSRM snapshot has 3 pass rows after bus-practical road filtering,
   and its manifest records 3 live/unpinned rows plus query URLs and checksums;
   it remains live-service plausibility evidence rather than source tuning.
6. **Policy alternatives** beyond baseline bus-only and baseline multimodal:
   redundant last-mile fleet, increased feeder capacity, staggered dispatch,
   adaptive rerouting, fleet shortage, and rail delay/unavailability.
7. **Full pilot experiment package review** for the staged/full
   scenario/seed/policy outputs after input evidence checks.
8. **Formal sensitivity review** for the current SALib Morris scaffold outputs,
   with Sobol only if compute and interpretation justify it.

The main thesis for the paper direction is:

> Rail-bus multimodal transport is a conditional resilience strategy whose
> performance depends on access roads, rail service, transfer handling,
> last-mile capacity, and finite fleet availability under disruption.

## Report Workflow

`report_draft.md` is the Korean source document. Regenerate the Word document
with:

```powershell
.\.venv\Scripts\python generate_report.py
```

After model code changes pass and refreshed outputs are requested, use this
Windows PowerShell workflow:

```powershell
.\.venv\Scripts\python -m compileall main.py src tests generate_report.py
Get-ChildItem tests\test_*.py | ForEach-Object { .\.venv\Scripts\python $_.FullName }
.\.venv\Scripts\python main.py --test
.\.venv\Scripts\python main.py --quick
.\.venv\Scripts\python main.py --phase 1
.\.venv\Scripts\python main.py --phase 2
.\.venv\Scripts\python generate_report.py
```

Do not edit `report.docx` or `results/` as part of routine code/documentation
changes unless refreshed outputs are explicitly requested. If model semantics
change, rerun full experiments before carrying result conclusions forward.

## Remaining Limitations

- The currently implemented experiment network is abstract and intentionally
  small in the current generated result set.
- Dynamic traffic uses rolling-window BPR, not full traffic assignment or
  microscopic road simulation.
- Rail is a single fixed-headway service and is failure-immune by default.
- Field-use parameters are source-untuned scenario assumptions.
- The real-world MVP can adapt OSM-like road graphs and now has an offline
  pilot smoke scaffold, but it has not yet been source-tuned with signed-off
  pilot-region traffic, capacity, rail, or disruption evidence.
- The cached OSM maxspeed candidate table is a road-speed review aid only; it
  is not a reviewed override table or source-tuned traffic-speed input.
- The cached OSM lane-count capacity table is a capacity evidence-gap review
  aid only; it is not source-tuned capacity input.
- Parameter, plausibility, disruption, and policy tables are implemented
  scaffolds, and sample/staged/full, deterministic screening, SALib Morris
  scaffold outputs, and generated figures/tables exist; they have not yet
  produced source-tuned sensitivity evidence or reviewed publication-grade
  signoff.
- The public repository clone cache exists for reference only; production code
  must not import runtime modules from `cloned_repo/`.
- The paper draft and real-world implementation blueprint define the next
  research direction but do not by themselves create source-tuned real-world
  results.
- The default Phase 1 sweep covers `baseline` and `matched_redundancy`; the
  additional declared sensitivity variants require an explicit result
  regeneration before they are used in conclusions.
- Report narrative and generated outputs should be reviewed together after a
  new full experiment is signed off.

## Git

- Remote: `https://github.com/hyunjun1121/transport-system-sim.git`
- Branch: `main`
- Configure local commit identity if commits are needed:
  `git config user.name "hyunjun1121"` and
  `git config user.email "hyunjun1121@users.noreply.github.com"`
- Handoff target: main agent commits and pushes the intended state to `main`,
  then the next computer uses `git clone` plus the Windows setup commands
  above. Do not assume uncommitted local artifacts, `.venv`, or Word lock files
  will be present after clone.

## Conventions

- All code comments and docstrings in English.
- Report files (`report_draft.md`, `report.docx`) in Korean.
- Keep text files encoded as UTF-8.
- Do not add emojis unless explicitly requested.
- Keep changes minimal; do not refactor beyond what was asked.
- Do not revert edits made by other workers.
