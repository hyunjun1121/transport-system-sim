# AGENTS.md - Transport System Simulation

## Project Overview

Disrupted regional personnel-transport resilience simulation. The implemented
baseline compares **bus-only** vs **rail-bus multimodal** transport for moving
approximately 1,000 people from an assembly context toward a destination zone.

The current research direction is broader than the original wartime/reserve
framing:

> build an open-data, region-reusable, real-world or quasi-real simulation
> pipeline for emergency personnel movement, disrupted regional mobility, and
> public-sector contingency transport planning.

Do not present the current model as an operational route plan or real-world
forecast. It is a decision-support and resilience-evaluation framework.

**Environment**: Windows PowerShell. Use the Python Launcher (`py`) to create a
local virtual environment, then run project commands through
`.\.venv\Scripts\python`.

## Current Audit Snapshot

As of 2026-05-06, `final_study_ready=false`. The current final-study audit has
15 gates: 3 ready (`real_input_smoke`, `structured_disruptions`,
`policy_alternatives`) and 12 blocked. Formal acceptance is 0/12 ready, and
the required formal acceptance artifacts are intentionally absent until
source-backed human review supplies them.

The latest `validation_strategy_readiness`, `graph_scale_strategy_readiness`,
and `sensitivity_strategy_readiness` packets are implemented, but they are
blocker/readiness review aids only. Do not treat them as acceptance records,
calibration evidence, operational route plans, or final-study approval.

## Repository Structure

```text
main.py                    # CLI entry: --quick, --test, --phase 1|2
config.yaml                # Network, BPR, stochastic, dispatch, DoE config
requirements.txt           # Python dependencies for Windows/venv setup
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
    graph_scale_diagnostics.py # Full-vs-reduced route parity and alternate-route diagnostics
    graph_scale_review.py   # Graph-scale method option review worksheet
    graph_scale_strategy_readiness_packet.py # Graph-scale blocker/readiness worksheet
    disruption_scenarios.py # Structured disruption scenario definitions
    policy_alternatives.py  # Policy alternative config variants
    pilot_experiments.py    # Cached pilot scaffold experiment runner
    experiment_acceptance.py # Explicit pilot experiment-output acceptance validation
    experiment_package_review_packet.py # Full experiment output review worksheet
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
  test_realworld_acceptance_records.py
  test_realworld_acceptance_orchestration.py
  test_realworld_acceptance_blocker_queue.py
  test_realworld_acceptance_task_assignments.py
  test_realworld_formal_acceptance_evidence_matrix.py
  test_realworld_formal_evidence_path_audit.py
  test_realworld_plan_audit.py
data/
  regions/pilot_region.yaml
  cache/pilot_region_road.graphml
  parameters/
    road_class_overrides_draft.csv  # 10-row expert-assumption review worksheet
    parameter_evidence_review_packet.csv # 29-row weak-parameter review worksheet
    parameter_evidence_review_manifest.json
    parameter_evidence_source_request_packet.csv # 6-row parameter source-request aid
    parameter_evidence_source_request_manifest.json
    road_capacity_evidence_candidates.csv # 10-row capacity evidence gap aid
    road_speed_evidence_candidates.csv # 10-row OSM maxspeed review aid
    road_evidence_review_packet.csv # 10-row consolidated road review aid
    road_evidence_review_manifest.json
  road/
    road_evidence_source_request_packet.csv # 5-row road source-request aid
    road_evidence_source_request_manifest.json
    rail_evidence_review_packet.csv # 10-row consolidated rail review aid
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
    reproducibility_review_packet.csv # 7-row clean-checkout review aid
    reproducibility_review_manifest.json
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
  build_pilot_cache.py       # Preserves cache by default; explicit fixture/Overpass refresh
  run_pilot_smoke.py
  run_full_graph_smoke.py
  audit_rail_evidence.py
  write_rail_evidence_review_packet.py
  write_rail_timing_source_request_packet.py
  audit_rail_station_bindings.py
  audit_parameter_evidence.py
  write_parameter_review_packet.py
  write_parameter_evidence_source_request_packet.py
  audit_road_evidence.py
  audit_road_evidence_diagnostics.py
  write_road_capacity_evidence.py
  write_road_speed_evidence.py
  write_road_evidence_review_packet.py
  write_road_evidence_source_request_packet.py
  audit_road_overrides.py
  write_road_class_override_template.py
  write_pilot_privacy_review_packet.py
  audit_source_provenance.py
  audit_publication_readiness.py
  audit_final_study_readiness.py
  derive_rail_station_bindings.py
  run_plausibility_validation.py
  run_osrm_route_benchmark.py
  write_osrm_snapshot_manifest.py
  derive_rail_service_evidence.py
  derive_rail_headway_evidence.py
  fetch_rail_timetable_cache.py
  derive_rail_gtfs_evidence.py
  derive_rail_shortest_path_evidence.py
  fetch_rail_shortest_path_cache.py
  run_graph_scale_diagnostics.py
  write_graph_scale_review_packet.py
  write_graph_scale_strategy_readiness_packet.py
  write_graph_scale_result_comparison.py
  run_acceptance_audit.py
  write_experiment_package_review_packet.py
  write_acceptance_decision_templates.py
  write_acceptance_blocker_queue.py
  write_acceptance_task_assignments.py
  write_formal_acceptance_evidence_matrix.py
  write_source_license_review_packet.py
  write_source_url_review_packet.py
  write_claim_alignment_review_packet.py
  audit_formal_acceptance_artifacts.py
  audit_formal_evidence_paths.py
  validate_formal_acceptance_package.py
  run_pilot_experiments.py
  run_sensitivity.py
  audit_sensitivity_diagnostics.py
  write_sensitivity_review_packet.py
  write_sensitivity_strategy_readiness_packet.py
  write_validation_review_packet.py
  write_validation_strategy_readiness_packet.py
  write_reproducibility_review_packet.py
  run_reproducibility_smoke.py
  write_route_road_evidence_exposure.py
  make_pilot_figures.py
  audit_plan_artifacts.py
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
.\.venv\Scripts\python tests\test_realworld_pilot_figures.py
.\.venv\Scripts\python tests\test_realworld_formal_acceptance_evidence_matrix.py
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

`config.yaml` keeps legacy experiment keys and includes operational namespaces
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

Config validation guidance:

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
  `scripts/write_acceptance_blocker_queue.py` write
  `data/manifests/formal_acceptance_blocker_queue.csv`,
  `data/manifests/formal_acceptance_blocker_queue_manifest.json`, and
  `docs/formal_acceptance_blocker_queue.md`. These rows are reviewer work
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
  `scripts/audit_formal_acceptance_artifacts.py` guard the formal acceptance
  paths against copied templates, unresolved `REVIEW_REQUIRED` placeholders,
  and draft-only weak road override rows. The current guard reports all 12
  required formal acceptance artifacts as missing and cannot mark the final
  study complete.
- `src/realworld/formal_acceptance_package.py` and
  `scripts/validate_formal_acceptance_package.py` aggregate reviewer-supplied
  formal acceptance artifacts into one intake audit. The generated
  `data/manifests/formal_acceptance_package_audit.json` and
  `docs/formal_acceptance_package_audit.md` are validation outputs only; they
  do not create approvals or bypass the final-study readiness audit.
- `src/realworld/formal_evidence_path_audit.py` and
  `scripts/audit_formal_evidence_paths.py` inspect reviewer-supplied formal
  artifacts for missing local evidence paths, unresolved placeholders, empty
  evidence records, and external references that still need source/license
  review. The generated `data/manifests/formal_evidence_path_audit.json` and
  `docs/formal_evidence_path_audit.md` are path-hygiene checks only, not
  evidence sufficiency or acceptance.
- Region records validate bbox boundaries, assembly/destination zones, rail
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
- `src/realworld/graph_scale_acceptance.py` validates the optional
  `data/manifests/graph_scale_acceptance.json` review record required before a
  reduced corridor, full-graph runtime, or multi-corridor ensemble can close
  the final graph-scale strategy gate. This file is absent in the current
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
- `src/realworld/validation_acceptance.py` validates the optional
  `data/manifests/validation_acceptance.json` review record required before
  route plausibility and external benchmark evidence can close the final
  validation-package gate. This file is absent in the current scaffold.
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
  final-study readiness. The current audit has no missing core parameters but
  still reports weak expert/sensitivity-only evidence for final claims.
- `src/realworld/parameter_review_packet.py` and
  `scripts/write_parameter_review_packet.py` turn the audit into a generated
  29-row review worksheet. The current packet marks 25 core parameters as weak
  for final-study claims and remains review support only.
- `src/realworld/parameter_evidence_request_packet.py` and
  `scripts/write_parameter_evidence_source_request_packet.py` produce a 6-row
  source-request worksheet for cross-cutting demand, fleet, dispatch,
  transfer, disruption, and traffic/BPR evidence. It is request support only
  and does not accept weak parameters.
- `src/realworld/parameter_acceptance.py` validates optional
  `data/parameters/parameter_acceptance.csv` review records for weak
  assumptions that are explicitly retained inside final claim boundaries. This
  file is absent in the current scaffold.
- `src/realworld/pilot_acceptance.py` validates the optional
  `data/manifests/pilot_acceptance.json` review record. The file is absent in
  the current scaffold so the final-study gate remains blocked until a real
  acceptance decision is recorded.
- `src/realworld/provenance_acceptance.py` validates the optional
  `data/manifests/provenance_acceptance.json` review record required before
  source snapshot, license/attribution, privacy abstraction, cache manifest,
  reproducibility manifest, and not-operational claim-boundary review can close
  the final data-provenance gate. This file is absent in the current scaffold.
- `src/realworld/manuscript_acceptance.py` validates the optional
  `data/manifests/manuscript_acceptance.json` review record required before
  English manuscript, Korean report, regenerated docx, figure/table manifest,
  evidence-gate, result-claim, and not-operational claim-boundary review can
  close the final manuscript/report gate. This file is absent in the current
  scaffold.
- `src/realworld/claim_alignment_review_packet.py` and
  `scripts/write_claim_alignment_review_packet.py` generate a claim-level
  review worksheet for `paper/paper_draft.md`, `report_draft.md`, and the
  figure/table manifest. It is review support only and does not create
  `manuscript_acceptance.json`.
- `src/realworld/reproducibility_acceptance.py` validates the optional
  `data/manifests/reproducibility_acceptance.json` review record required
  before clean-checkout validation, validation ladder, artifact regeneration,
  manifest paths, cloned-repo import-boundary, command count, and
  not-operational claim-boundary review can close the final reproducibility
  gate. This file is absent in the current scaffold.
- `src/realworld/reproducibility_smoke.py` and
  `scripts/run_reproducibility_smoke.py` run a bounded current-worktree smoke
  ladder. Current output has 20 passing commands in
  `data/validation/reproducibility_smoke_manifest.json` and a JSONL command
  log, but `clean_checkout_test_performed` and `can_mark_complete` remain
  false.
- `src/realworld/final_audit_acceptance.py` validates the optional
  `data/manifests/final_audit_acceptance.json` review record required before
  independent prompt-to-artifact completion review, gate evidence review,
  no-proxy completion review, gate-list/count matching, and not-operational
  claim-boundary review can close the final audit gate. This file is absent in
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
- `src/realworld/road_evidence_review_packet.py` and
  `scripts/write_road_evidence_review_packet.py` consolidate the road-class
  diagnostics, sparse speed evidence, lane-count evidence, and draft override
  rows into a 10-row review worksheet. All current rows remain weak for
  final-study road claims and are review support only.
- `src/realworld/road_evidence_request_packet.py` and
  `scripts/write_road_evidence_source_request_packet.py` write a 5-row
  source-request worksheet for the missing speed, capacity, benchmark,
  disruption, and override-application source inputs. It is request support
  only and does not create reviewed road overrides.
- `src/realworld/road_overrides.py` validates optional road-class override
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
  graph-scale strategy-readiness packet and manifest under `data/validation/`;
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
  readiness, timing gaps, capacity treatment, service-window assumptions,
  availability assumptions, and derivation paths into a 10-row review
  worksheet. It is review support only and keeps service publication readiness
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
  not part of default offline validation.
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
- `src/realworld/experiment_acceptance.py` validates the optional
  `data/manifests/experiment_acceptance.json` review record required before
  staged/full pilot outputs can close the final full-experiment-output gate.
  This file is absent in the current scaffold.
- `src/realworld/experiment_package_review_packet.py` and
  `scripts/write_experiment_package_review_packet.py` generate a full
  experiment output worksheet covering manifest/result/summary row counts,
  scenario-policy-seed design counts, graph scope, input dependencies, CRN
  declaration, checksums, and formal acceptance absence without accepting the
  experiment package.
- `scripts/run_sensitivity.py --sample` runs deterministic one-at-a-time
  scaffold screening and writes SALib-compatible manifest metadata.
- `scripts/run_sensitivity.py --method morris --all` runs SALib Morris
  screening for the current full policy/scenario scaffold and writes
  `morris_*` outputs.
- `scripts/audit_sensitivity_diagnostics.py` reports Morris count consistency,
  blank/non-finite index values, zero `mu_star` rows, reduced graph scope, and
  scaffold claim boundaries without accepting final-study sensitivity claims.
- `src/realworld/sensitivity_review_packet.py` and
  `scripts/write_sensitivity_review_packet.py` convert those diagnostics into
  a 6-row review worksheet that keeps index handling, zero-effect
  interpretation, reduced graph scope, and the Morris-vs-Sobol decision
  visible without closing the sensitivity gate.
- `src/realworld/sensitivity_strategy_readiness_packet.py` and
  `scripts/write_sensitivity_strategy_readiness_packet.py` convert that
  6-row worksheet into 7 pre-review readiness rows. The packet keeps
  missing/non-finite indices, zero `mu_star` interpretation, reduced graph
  scope, scaffold result scope, Morris-vs-Sobol decision, and missing
  sensitivity acceptance visible without accepting final sensitivity evidence.
- `src/realworld/validation_review_packet.py` and
  `scripts/write_validation_review_packet.py` convert route plausibility,
  fallback/OSRM benchmark, OSRM snapshot manifest, accessibility-loss,
  route-level road-evidence exposure, and validation-summary scope artifacts
  into a 7-row review
  worksheet without closing the validation gate.
- `src/realworld/validation_strategy_readiness_packet.py` and
  `scripts/write_validation_strategy_readiness_packet.py` convert that 7-row
  validation worksheet into pre-review readiness statuses. The packet keeps
  internal warnings, fallback benchmark warnings, unpinned OSRM snapshot risk,
  accessibility diagnostics, weak route-road evidence exposure, summary scope,
  and missing validation acceptance visible without approving a benchmark
  strategy.
- `src/realworld/route_road_evidence_exposure.py` and
  `scripts/write_route_road_evidence_exposure.py` generate a 76-row
  route-level worksheet that links weak road speed, capacity, disruption, and
  connector assumptions to canonical route candidates. This is review support
  only, not calibration or validation acceptance.
- `scripts/make_pilot_statistics.py` writes full-pilot metric confidence
  intervals and paired policy-delta confidence intervals from seed replications;
  these are uncertainty summaries for scaffold outputs, not calibration proof.
- `src/realworld/sensitivity_acceptance.py` validates the optional
  `data/manifests/sensitivity_acceptance.json` review record required before
  current Morris or future Sobol outputs can close the final sensitivity gate.
  This file is absent in the current scaffold.
- `scripts/make_pilot_figures.py` generates scaffold-only figures, tables, and
  a claim-boundary table from current full pilot and Morris outputs, including
  bottleneck attribution proxy and policy regime-map artifacts.
- `scripts/audit_plan_artifacts.py` checks current scaffold artifact row
  counts, JSON manifests, docs, parameter evidence readiness, and the
  conservative claim boundary.
- `scripts/audit_source_provenance.py` checks the non-acceptance source
  provenance review packet for source URLs, license/terms notes, local
  artifacts, review statuses, and claim boundaries.
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
- `scripts/audit_publication_readiness.py` aggregates parameter, road, rail
  service, and station-binding gates while preserving `publication_ready:
  false` until evidence blockers are closed.
- `scripts/audit_final_study_readiness.py` checks all `plan.md` final-study
  gates and keeps scaffold artifact presence separate from final readiness for
  pilot acceptance, graph scale, evidence, validation, experiment, sensitivity,
  manuscript/report, reproducibility, and final audit requirements.
- `docs/graph_scale_acceptance_schema.md` defines the graph-scale acceptance
  record shape; do not create the actual acceptance JSON unless a real review
  has accepted the source-vs-analysis graph decision and claim boundary.
- `docs/graph_scale_diagnostics.md` documents the route-parity and
  alternate-route diagnostics plus their claim boundaries; keep it distinct
  from graph-scale acceptance.
- `docs/graph_scale_review_packet.md` documents the 4-option graph-scale
  method review packet; keep it distinct from graph-scale acceptance.
- `docs/graph_scale_result_comparison.md` documents the current-vs-candidate
  graph-scale result-delta table; keep it distinct from graph-scale
  acceptance.
- `docs/validation_acceptance_schema.md` defines the validation acceptance
  record shape; do not create the actual acceptance JSON unless a real review
  has accepted the benchmark strategy and its not-ground-truth limitation.
- `docs/experiment_acceptance_schema.md` defines the experiment-output
  acceptance record shape; do not create the actual acceptance JSON unless a
  real review has accepted graph scope, input validation,
  scenario-policy-seed design, CRN pairing, counts, and not-operational claim
  limits.
- `docs/provenance_acceptance_schema.md` defines the data-provenance
  acceptance record shape; do not create the actual acceptance JSON unless a
  real review has accepted source snapshots, license/attribution, privacy
  abstraction, cache manifests, reproducibility paths, and not-operational
  claim limits.
- `docs/manuscript_acceptance_schema.md` defines the manuscript/report
  acceptance record shape; do not create the actual acceptance JSON unless a
  real review has accepted paper/report text, regenerated docx, figures/tables,
  evidence gates, result claims, and not-operational claim limits.
- `docs/reproducibility_acceptance_schema.md` defines the clean-checkout
  reproducibility acceptance record shape; do not create the actual acceptance
  JSON unless a real clean-checkout reproduction review has accepted validation
  commands, regenerated artifacts, manifest paths, import boundaries, and
  not-operational claim limits.
- `docs/final_audit_acceptance_schema.md` defines the independent final-audit
  acceptance record shape; do not create the actual acceptance JSON unless a
  real final audit has reviewed every prompt-to-artifact requirement and all
  pre-final gates are closed.
- `docs/reproducibility_package.md` and
  `data/manifests/reproducibility_manifest.json` record reproduction commands,
  artifact paths, and claim limits for the current scaffold-only package.
- `docs/reproducibility_smoke.md` summarizes the bounded current-worktree
  smoke run. It is execution evidence only and must not be treated as
  clean-checkout reproducibility acceptance.
- `docs/plan_completion_audit.md` records the current gate-by-gate audit and
  remaining final-study blockers.

Treat outputs from this path as quasi-real decision-support experiments until
pilot data, travel-time assumptions, capacity proxies, rail inputs, and
disruption assumptions are validated. The current pilot scaffold, evidence
tables, sample/staged/full outputs, sensitivity screening, and generated figure/table
artifacts prove offline execution and study scaffolding only; do not claim
calibrated real-world or operational accuracy.

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
implementation goal is to review the current OSM-derived cache as an accepted
pilot snapshot or replace it with a better snapshot, review staged/full pilot
outputs, and document each input as
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
4. **Public transit and rail validation** using GTFS where available, or a
   documented rail-assumption table when GTFS is incomplete.
5. **Plausibility benchmarking** with routing or multimodal tools such as
   OSRM, Valhalla, routingpy, r5py/R5, or UXsim as appropriate. The current
   optional OSRM snapshot has 3 pass rows after bus-practical road filtering,
   and its manifest records 3 live/unpinned rows plus query URLs and checksums;
   it remains live-service plausibility evidence rather than calibration.
6. **Policy alternatives** beyond baseline bus-only and baseline multimodal:
   redundant last-mile fleet, increased feeder capacity, staggered dispatch,
   adaptive rerouting, fleet shortage, and rail delay/unavailability.
7. **Full pilot experiment package review** for the staged/full
   scenario/seed/policy outputs after input validation.
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
- Operational parameters are uncalibrated scenario assumptions.
- The real-world MVP can adapt OSM-like road graphs and now has an offline
  pilot smoke scaffold, but it has not yet been calibrated with accepted
  pilot-region traffic, capacity, rail, or disruption evidence.
- The cached OSM maxspeed candidate table is a road-speed review aid only; it
  is not a reviewed override table or calibrated traffic-speed input.
- The cached OSM lane-count capacity table is a capacity evidence-gap review
  aid only; it is not calibrated capacity input.
- Parameter, plausibility, disruption, and policy tables are implemented
  scaffolds, and sample/staged/full, deterministic screening, SALib Morris
  scaffold outputs, and generated figures/tables exist; they have not yet
  produced calibrated sensitivity evidence or reviewed publication-grade
  acceptance.
- The public repository clone cache exists for reference only; production code
  must not import runtime modules from `cloned_repo/`.
- The paper draft and real-world implementation blueprint define the next
  research direction but do not by themselves create calibrated real-world
  results.
- The default Phase 1 sweep covers `baseline` and `matched_redundancy`; the
  additional declared sensitivity variants require an explicit result
  regeneration before they are used in conclusions.
- Report narrative and generated outputs should be reviewed together after a
  new full experiment is accepted.

## Git

- Remote: `https://github.com/hyunjun1121/transport-system-sim.git`
- Branch: `main`
- Configure local commit identity if commits are needed:
  `git config user.name "hyunjun1121"` and
  `git config user.email "hyunjun1121@users.noreply.github.com"`

## Conventions

- All code comments and docstrings in English.
- Report files (`report_draft.md`, `report.docx`) in Korean.
- Keep text files encoded as UTF-8.
- Do not add emojis unless explicitly requested.
- Keep changes minimal; do not refactor beyond what was asked.
- Do not revert edits made by other workers.
