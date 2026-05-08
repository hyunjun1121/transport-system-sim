# Transport System Simulation

Disrupted regional personnel-transport micro-simulation comparing **bus-only**
and **rail-bus multimodal** movement for approximately 1,000 people.

The implemented baseline was originally developed for a reserve-force transport
case. The active research direction is now broader: evolve the model into an
open-data, region-reusable, real-world or quasi-real transport-resilience study
for emergency personnel movement, disrupted regional mobility, and
public-sector contingency transport planning.

The implemented scenarios are:

- `bus_only`: passengers assemble at `A` and travel by road to `D`.
- `multimodal`: passengers shuttle from `A` to `S`, ride rail from `S` to `R`,
  then complete the last mile by road to `D`.

The current generated results are conditional findings under a representative
abstract network. They should not be interpreted as calibrated operational
forecasts.

## Current Audit Snapshot

As of 2026-05-08, the final-study audit reports
`final_study_ready=false`. Three of 15 final gates are ready:
`real_input_smoke`, `structured_disruptions`, and `policy_alternatives`.
The remaining 12 gates are blocked.

Formal acceptance is also not ready: 0 of 12 required formal acceptance targets
are ready, and the corresponding formal acceptance artifacts are intentionally
absent until source-backed human review supplies them. The current
`validation_strategy_readiness`, `graph_scale_strategy_readiness`,
`sensitivity_strategy_readiness`, and `experiment_strategy_readiness` packets
are implemented blocker/readiness aids, not acceptance records. No generated
output in this repository is a calibrated real-world result or an operational
route plan.

## Windows Setup

Use Windows PowerShell from the repository root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt
```

If `py -3.11` is unavailable, install Python 3.11+ for Windows and enable the
Python Launcher during installation.

## Git Handoff

The handoff target is a fresh clone on another computer after the main agent
commits and pushes the intended repository state to `main`.

```powershell
git -c core.longpaths=true clone https://github.com/hyunjun1121/transport-system-sim.git C:\tss
cd C:\tss
py -3.11 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt
```

On Windows, prefer a short checkout path such as `C:\tss` and keep
`core.longpaths=true`; the retained `cloned_repo/` reference snapshots include
deep paths that can exceed default Windows checkout limits in a long temp path.
If `py -3.11` is unavailable but Python 3.11+ is installed, use the available
`python -m venv .venv` command.

Before handoff, verify that every required source, Markdown, data, manifest,
and generated-result artifact is committed or deliberately excluded. A clean
clone will not include local `.venv` contents, Word lock files such as
`~$report.docx`, or uncommitted working-tree artifacts.

## Run

```powershell
.\.venv\Scripts\python main.py --test       # Single paired scenario debug run
.\.venv\Scripts\python main.py --quick      # Reduced smoke run, writes results/
.\.venv\Scripts\python main.py --phase 1    # Phase 1 only
.\.venv\Scripts\python main.py --phase 2    # Phase 2 only
.\.venv\Scripts\python main.py              # Full experiment
```

`--quick` reduces replications and grid sizes, but it still writes CSV and PNG
artifacts under `results/`.

## Tests

Each test file is directly executable; the project does not require pytest.

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
```

To run the direct-execution tests as a batch in PowerShell:

```powershell
Get-ChildItem tests\test_*.py | ForEach-Object { .\.venv\Scripts\python $_.FullName }
```

## Current Architecture

```text
main.py                    # CLI entry: --quick, --test, --phase 1|2
config.yaml                # Network, stochastic model, dispatch, DoE, KPI config
requirements.txt           # Python dependencies for Windows venv setup
generate_report.py         # Builds report.docx from report_draft.md
report_draft.md            # Korean report source
report.docx                # Generated Word report
src/
  sim_types.py             # Passenger, VehicleTrip, EdgeDisruption records
  network.py               # NetworkX DiGraph builder from config
  models.py                # BPR, arrival delay, legacy failure/travel helpers
  policies.py              # StrictPolicy and GracePolicy(W, theta)
  dispatch.py              # Queue-based dispatch manifest planning
  fleet.py                 # Fleet availability and turnaround assignment
  traffic.py               # Rolling-window dynamic road volume and BPR traversal
  disruptions.py           # Blocked/degraded edge disruption sampling
  rail.py                  # Fixed-headway rail service helpers
  transfers.py             # Fixed plus per-passenger transfer delay helpers
  metrics.py               # Makespan, completion, censoring, resource KPIs
  scenario.py              # Scenario orchestrator: run_scenario(...) -> dict
  realworld/
    acceptance_records.py  # Common sub-agent review record schema validation
    acceptance_orchestration.py # Deterministic review-agent gate orchestration
    acceptance_decision_templates.py # Non-approval formal acceptance templates
    acceptance_blocker_queue.py # Formal blocker queue for reviewer actions
    acceptance_task_assignments.py # Map formal blockers to review-agent tasks
    formal_acceptance_evidence_matrix.py # Per-artifact reviewer intake matrix
    formal_acceptance_guard.py # Detect placeholder/template misuse in formal paths
    formal_evidence_path_audit.py # Check formal evidence/source paths exist
    formal_acceptance_package.py # Aggregate formal acceptance intake audit
    manuscript_acceptance.py # Explicit manuscript/report acceptance validation
    types.py               # Region, boundary, zone, and rail input records
    regions.py             # Region registry loading and validation helpers
    osm_network.py         # Optional OSMnx bbox extraction and GraphML cache
    attributes.py          # OSM-style road attributes -> simulator edge fields
    zones.py               # Nearest-node snapping and connector edges
    adapter.py             # OSM-like graph -> simulator-compatible DiGraph
    validation.py          # Scenario-readiness checks for adapted graphs
    parameters.py          # Parameter-source table validation
    graph_scale_acceptance.py # Explicit graph-scale acceptance validation
    validation_acceptance.py # Explicit validation-package acceptance validation
    final_audit_acceptance.py # Explicit independent final-audit acceptance validation
    parameter_acceptance.py # Optional weak-parameter acceptance validation
    parameter_audit.py     # Parameter evidence readiness audit
    parameter_review_packet.py # Weak-parameter review worksheet generation
    parameter_evidence_request_packet.py # Cross-cutting parameter source-request worksheet
    pilot_acceptance.py    # Explicit pilot acceptance record validation
    pilot_privacy_review_packet.py # Pilot privacy/sensitivity review worksheet
    provenance_acceptance.py # Explicit data-provenance acceptance validation
    source_provenance.py   # Source provenance review packet validation
    source_license_review_packet.py # Source/license review worksheet generation
    source_url_review_packet.py # Source URL review worksheet generation
    claim_alignment_review_packet.py # Manuscript/report claim review worksheet
    road_evidence.py       # Cached road-input evidence audit
    road_evidence_diagnostics.py # Road-class evidence gap diagnostics
    road_capacity_evidence.py # Cached OSM lanes capacity candidate evidence
    road_speed_evidence.py # Cached OSM maxspeed candidate evidence
    road_evidence_review_packet.py # Consolidated road-input review worksheet
    road_evidence_request_packet.py # Road evidence source-request worksheet
    road_overrides.py      # Optional road-class evidence override loader
    road_override_template.py # Draft road-class override review templates
    road_override_audit.py # Optional road-class override readiness audit
    plausibility.py        # Offline pilot route plausibility checks
    validation_review_packet.py # Validation-strategy review worksheet generator
    route_road_evidence_exposure.py # Route-level road evidence exposure review aid
    accessibility.py       # Route accessibility-loss diagnostics
    graph_scale_diagnostics.py # Full-vs-reduced route parity and alternate-route diagnostics
    graph_scale_review.py  # Graph-scale method option review worksheet
    disruption_scenarios.py # Structured disruption scenario definitions
    policy_alternatives.py # Policy alternative config variants
    pilot_experiments.py   # Cached pilot scaffold experiment runner
    experiment_acceptance.py # Explicit pilot experiment-output acceptance validation
    experiment_package_review_packet.py # Full experiment output review worksheet
    reproducibility_acceptance.py # Explicit clean-checkout acceptance validation
    reproducibility_review_packet.py # Clean-checkout review worksheet generator
    reproducibility_smoke.py # Current-worktree smoke evidence runner
    tracked_artifact_audit.py # Changed-artifact clean-checkout packaging audit
    sensitivity.py         # Deterministic and SALib Morris sensitivity scaffold
    sensitivity_acceptance.py # Explicit sensitivity acceptance validation
    sensitivity_diagnostics.py # Morris output review diagnostics
    sensitivity_review_packet.py # Morris diagnostics review worksheet generator
    pilot_figures.py       # Scaffold-only figures and claim-boundary tables
    publication_readiness.py # Aggregated final-claim readiness audit
    final_study_readiness.py # Plan-level final-study gate audit
    rail_evidence.py       # Offline rail evidence cache validation
    rail_station_binding.py # Rail-point station binding evidence audit
    rail_station_cache.py  # Cached station extract -> binding derivation
    rail_timetable.py      # Cached timetable -> rail evidence derivation
    rail_timetable_api.py  # Optional data.go.kr train-schedule cache fetcher
    rail_gtfs.py           # Cached static GTFS -> rail timing evidence
    rail_shortest_path.py  # Cached shortest-path -> rail travel-time evidence
    rail_shortest_path_api.py # Optional data.go.kr shortest-path cache fetcher
    rail_evidence_review_packet.py # Consolidated rail evidence review worksheet
    rail_timing_request_packet.py # Rail timing source-request worksheet
  experiment/
    doe.py                 # Phase 1 and Phase 2 grids
    runner.py              # CRN paired experiment execution
    analysis.py            # CI, break-even, Phase 1 summaries
  visualize/
    plots.py               # Heatmaps, success-rate plots, Pareto, break-even
tests/                     # Direct-execution regression and unit tests
results/                   # Generated CSV and PNG experiment outputs
paper/                     # English paper/manuscript scaffold
data/
  regions/pilot_region.yaml
  cache/pilot_region_road.graphml
scripts/
  build_pilot_cache.py     # Preserve current cache or explicitly refresh it
  run_pilot_smoke.py       # Run bus-only and multimodal on pilot cache
  run_full_graph_smoke.py  # Tiny smoke on the full bus-practical graph
  write_full_graph_runtime_readiness_packet.py # Full-graph runtime review aid
  audit_rail_evidence.py   # Check rail evidence cache status
  write_rail_evidence_review_packet.py # Write rail evidence review packet
  write_rail_timing_source_request_packet.py # Write rail timing source requests
  audit_rail_station_bindings.py # Check rail-point station binding status
  audit_parameter_evidence.py # Check core parameter evidence readiness
  write_parameter_review_packet.py # Write weak-parameter review packet
  write_parameter_evidence_source_request_packet.py # Write parameter source-request packet
  audit_road_evidence.py   # Check OSM road input evidence readiness
  audit_road_evidence_diagnostics.py # Rank road-class evidence gaps
  write_road_capacity_evidence.py # Write cached OSM lane-count capacity candidates
  write_road_speed_evidence.py # Write cached OSM maxspeed candidate evidence
  write_road_evidence_review_packet.py # Write road-input evidence review packet
  write_road_evidence_source_request_packet.py # Write road evidence source-request packet
  audit_road_overrides.py  # Check optional road-class override evidence status
  write_road_class_override_template.py # Draft road override review template
  audit_source_provenance.py # Check source provenance review packet
  write_source_url_review_packet.py # Write URL-level source review worksheet
  audit_publication_readiness.py # Aggregate final-study claim blockers
  audit_final_study_readiness.py # Check all plan.md final-study gates
  audit_sensitivity_diagnostics.py # Review Morris output diagnostics
  write_sensitivity_review_packet.py # Write Morris diagnostics review packet
  write_osrm_snapshot_manifest.py # Write optional OSRM checksum/query manifest
  write_validation_review_packet.py # Write validation-strategy review packet
  write_reproducibility_review_packet.py # Write clean-checkout review packet
  run_reproducibility_smoke.py # Run bounded current-worktree reproducibility smoke
  audit_tracked_artifacts.py # List changed artifacts missing from clean checkout
  write_acceptance_decision_templates.py # Write non-approval formal acceptance templates
  write_acceptance_blocker_queue.py # Write gate-by-gate formal blocker queue
  write_acceptance_task_assignments.py # Assign blocker rows to review-agent roles
  write_formal_acceptance_evidence_matrix.py # Write per-artifact evidence matrix
  audit_formal_acceptance_artifacts.py # Guard formal paths against templates/placeholders
  audit_formal_evidence_paths.py # Check formal evidence/source path hygiene
  validate_formal_acceptance_package.py # Validate reviewer-supplied formal acceptance package
  write_route_road_evidence_exposure.py # Write route-level road evidence exposure aid
  derive_rail_station_bindings.py # Optional cached station binding derivation
  derive_rail_service_evidence.py # Optional cached timetable derivation
  derive_rail_headway_evidence.py # Optional cached headway-only derivation
  fetch_rail_timetable_cache.py # Optional key-required timetable cache fetch
  derive_rail_gtfs_evidence.py # Optional cached static-GTFS derivation
  derive_rail_shortest_path_evidence.py # Optional cached shortest-path derivation
  fetch_rail_shortest_path_cache.py # Optional key-required shortest-path cache fetch
  run_accessibility_loss_analysis.py # Route critical-edge/accessibility loss
  run_graph_scale_diagnostics.py # Full-vs-reduced route parity and alternate-route diagnostics
  write_graph_scale_review_packet.py # Write graph-scale method review packet
  write_graph_scale_result_comparison.py # Compare current vs candidate graph-scale results
  run_acceptance_audit.py  # Refresh review packets and sub-agent gate records
  audit_plan_artifacts.py  # Check scaffold artifacts and claim boundary
  write_goal_completion_audit.py # Write active-goal non-acceptance audit
cloned_repo/               # Public repo source snapshots for reference
```

## Research And Planning Documents

The current research context is distributed across these Markdown files:

| File | Purpose |
| --- | --- |
| `status.md` | Current project context, generated outputs, limitations, research direction, and clone state |
| `plan.md` | Remaining work plan for implementation and validation |
| `IMPLEMENTATION_PLAN.md` | Implemented system notes and module contracts |
| `realistic_simulation_requirements.md` | Korean realism requirements for real-world or quasi-real simulation |
| `public_github_repo_research.md` | Public repository research for realistic regional simulation |
| `disrupted_mobilization_resilience_repo_research.md` | Public repository research for disrupted regional resilience framing |
| `real_world_simulation_implementation_blueprint.md` | Extracted implementation ideas from public repos and phased real-world upgrade plan |
| `cloned_repo_manifest.md` | Manifest of local shallow clones in ignored `cloned_repo/` |
| `docs/realworld_pipeline.md` | Implemented real-world/quasi-real MVP workflow and validation notes |
| `docs/pilot_region_data_card.md` | Current non-sensitive pilot scaffold, privacy handling, and claim limits |
| `docs/analysis_corridor_method_note.md` | Current reduced-corridor method boundary and final-study decision options |
| `docs/graph_scale_diagnostics.md` | Full-vs-reduced route parity and alternate-route diagnostic scope and review notes |
| `docs/graph_scale_review_packet.md` | Four-option graph-scale method review packet scope and regeneration notes |
| `docs/validation_review_packet.md` | Validation-strategy review worksheet scope and non-acceptance notes |
| `docs/route_road_evidence_exposure.md` | Route-level road-evidence exposure scope and regeneration notes |
| `docs/sensitivity_diagnostics.md` | Morris sensitivity diagnostic scope and review notes |
| `docs/sensitivity_review_packet.md` | Sensitivity review worksheet scope and non-acceptance notes |
| `docs/road_evidence_diagnostics.md` | Road-class evidence diagnostic scope and review notes |
| `docs/road_evidence_review_packet.md` | Consolidated road-input evidence review packet scope and regeneration notes |
| `docs/road_evidence_source_request_packet.md` | Road evidence source-request packet scope and regeneration notes |
| `docs/rail_evidence_review_packet.md` | Consolidated rail evidence review packet scope and regeneration notes |
| `docs/rail_timing_source_request_packet.md` | Rail timing source-request packet scope and regeneration notes |
| `docs/accessibility_loss_analysis.md` | Route-level critical-edge/accessibility-loss diagnostic scope |
| `docs/source_provenance_manifest.md` | Source provenance manifest scope and audit notes |
| `docs/source_license_review_packet.md` | Source/license review worksheet; not provenance acceptance |
| `docs/source_url_review_packet.md` | URL-level source review worksheet; not provenance acceptance |
| `docs/experiment_package_review_packet.md` | Full experiment output worksheet; not experiment acceptance |
| `docs/experiment_strategy_readiness_packet.md` | Experiment blocker/readiness worksheet; not experiment acceptance |
| `docs/pilot_privacy_review_packet.md` | Pilot privacy/sensitivity review worksheet; not pilot acceptance |
| `docs/claim_alignment_review_packet.md` | Paper/report/figure claim worksheet; not manuscript acceptance |
| `docs/parameter_evidence_review_packet.md` | Parameter evidence review packet scope and regeneration notes |
| `docs/parameter_evidence_source_request_packet.md` | Parameter evidence source-request packet scope and regeneration notes |
| `docs/reproducibility_package.md` | Reproduction commands, artifact manifests, and claim boundaries |
| `docs/reproducibility_smoke.md` | Current-worktree reproducibility smoke summary; not clean-checkout acceptance |
| `docs/tracked_artifact_audit.md` | Changed-artifact packaging audit for clean-checkout reproducibility |
| `docs/acceptance_decision_templates.md` | Non-approval formal acceptance template guide for human reviewers |
| `docs/formal_acceptance_blocker_queue.md` | Gate-by-gate formal acceptance blocker queue generated for reviewers |
| `docs/acceptance_task_assignments.md` | Sub-agent role assignments for each unresolved formal acceptance blocker |
| `docs/formal_acceptance_evidence_matrix.md` | Per-formal-artifact intake matrix; not acceptance evidence |
| `docs/human_acceptance_runbook.md` | Reviewer workflow for closing formal acceptance gates without fabricating evidence |
| `docs/formal_acceptance_artifact_guard.md` | Guard notes for detecting placeholder/template misuse in formal acceptance paths |
| `docs/formal_evidence_path_audit.md` | Evidence-path hygiene report for reviewer-supplied formal artifacts |
| `docs/formal_acceptance_package_audit.md` | One-shot intake report for formal acceptance artifacts after human review |
| `docs/plan_completion_audit.md` | Current plan-gate audit, scaffold status, and remaining blockers |
| `docs/current_goal_completion_audit.md` | Active-goal prompt-to-artifact completion gap audit; not final acceptance |
| `docs/agents/acceptance_review_agents.md` | Sub-agent review role definitions and non-fabrication rules |
| `docs/review_packets/acceptance_review_index.md` | Aggregated gate review packet index generated by `scripts/run_acceptance_audit.py` |
| `docs/third_party_adaptations.md` | Third-party reference and adaptation provenance records |
| `paper/paper_draft.md` | English manuscript scaffold for a journal-style paper |

`cloned_repo/` contains public repository source snapshots with nested `.git`
metadata removed. These snapshots are references for studying implementation
patterns, not production modules imported by the simulator.

## Real-World / Quasi-Real Pipeline MVP

`src/realworld/` now provides an opt-in vertical slice for converting an
OSM-style regional road graph into the existing simulator graph contract. It
does not replace the abstract `config.yaml` network used by the current
generated results.

Implemented pieces:

- `RegionSpec`, `BoundarySpec`, `ZoneSpec`, `RailPointSpec`, and `RailSpec`
  validate a bbox region, assembly/destination zones, and fixed-headway rail
  assumptions.
- OSM-style edge attributes such as `highway`, `maxspeed`, `length`, `osmid`,
  `p_fail`, and `base_p_fail` are normalized into `t0`, `capacity`,
  `base_p_fail`, `p_fail`, `mode`, and metadata.
- The real-world adapter filters pedestrian, cycling, platform, construction,
  track, living-street, and service-only OSM geometries out of bus-practical
  simulator routes before zone snapping.
- OSMnx access is optional and lazy. Offline GraphML load/save and synthetic
  NetworkX fixtures do not require live OSM or Overpass calls.
- Zone and rail points are snapped to nearest road nodes using OSMnx-style
  `x` longitude and `y` latitude attributes, then connected with bidirectional
  connector edges.
- `build_simulator_graph(...)` emits a `networkx.DiGraph` compatible with the
  existing `run_scenario(...)` API and route checks for `A -> D`, `A -> S`, and
  `R -> D`.
- Current pilot graph scale is 13,268 raw OSM-cache nodes / 28,947 raw edges,
  4,608 bus-practical simulator nodes / 9,148 simulator edges after filtering,
  and 118 analysis-corridor nodes / 174 edges in the current sample/staged/full
  pilot outputs.
- `validate_graph_readiness(...)` and `assert_graph_ready(...)` check required
  nodes, edge fields, numeric validity, and road-mode connectivity before a
  scenario run.
- `songpa_public_demo` provides a first offline pilot scaffold through
  `data/regions/pilot_region.yaml`, `data/cache/pilot_region_road.graphml`,
  `data/cache/pilot_region_road_manifest.json`,
  `scripts/build_pilot_cache.py`, and `scripts/run_pilot_smoke.py`.
- `data/parameters/` records parameter, rail, and fleet source classes and is
  validated by `src.realworld.parameters`.
- `src.realworld.parameter_acceptance` validates optional
  `data/parameters/parameter_acceptance.csv` records for weak assumptions that
  reviewers explicitly accept within the final claim boundary. The file is
  intentionally absent in the current scaffold.
- `src.realworld.graph_scale_acceptance` validates optional
  `data/manifests/graph_scale_acceptance.json` records for the final
  source-vs-analysis graph decision. The file is intentionally absent in the
  current scaffold.
- `src.realworld.validation_acceptance` validates optional
  `data/manifests/validation_acceptance.json` records for the final
  publication-level validation strategy. The file is intentionally absent in
  the current scaffold.
- `src.realworld.parameter_audit` and `scripts/audit_parameter_evidence.py`
  classify core inputs as source-backed, benchmark-supported,
  assumption-only, or sensitivity-only. The current audit has no missing core
  parameters, but it still blocks final calibrated-study claims.
- `src.realworld.parameter_review_packet` and
  `scripts/write_parameter_review_packet.py` turn that audit into a 29-row
  reviewer worksheet. The generated packet marks 25 core parameters as weak
  for final-study claims and does not accept or calibrate any value.
- `src.realworld.parameter_evidence_request_packet` and
  `scripts/write_parameter_evidence_source_request_packet.py` produce a 6-row
  source-request worksheet for cross-cutting demand, fleet, dispatch,
  transfer, disruption, and traffic/BPR evidence. It is a request aid only and
  does not accept weak parameters.
- `src.realworld.pilot_acceptance` validates an explicit
  `data/manifests/pilot_acceptance.json` review record for future final-study
  acceptance. The record is intentionally absent in the current scaffold.
- `src.realworld.provenance_acceptance` validates optional
  `data/manifests/provenance_acceptance.json` records for source snapshot,
  license/attribution, privacy abstraction, cache manifest, reproducibility
  manifest, and not-operational claim-boundary review. The file is
  intentionally absent in the current scaffold.
- `src.realworld.manuscript_acceptance` validates optional
  `data/manifests/manuscript_acceptance.json` records for English manuscript,
  Korean report, regenerated docx, figure/table manifest, evidence-gate,
  result-claim, and not-operational claim-boundary review. The file is
  intentionally absent in the current scaffold.
- `src.realworld.reproducibility_acceptance` validates optional
  `data/manifests/reproducibility_acceptance.json` records for clean-checkout
  validation, validation-ladder, artifact-regeneration, manifest-path,
  cloned-repo import-boundary, command-count, and not-operational claim review.
  The file is intentionally absent in the current scaffold.
- `src.realworld.final_audit_acceptance` validates optional
  `data/manifests/final_audit_acceptance.json` records for independent
  prompt-to-artifact completion review, gate evidence review, no-proxy
  completion review, gate-list/count matching, and not-operational claim
  boundaries. The file is intentionally absent in the current scaffold.
- `src.realworld.acceptance_records` and
  `src.realworld.acceptance_orchestration` define deterministic review-agent
  records for blocked gates. `scripts/run_acceptance_audit.py` refreshes review
  packets, writes 12 records under `data/manifests/agent_reviews/`, and keeps
  all non-ready gates as `blocked` or `needs_human_review`; it does not create
  formal acceptance artifacts.
- `src.realworld.acceptance_blocker_queue` and
  `scripts/write_acceptance_blocker_queue.py` write one CSV row per unresolved
  formal acceptance blocker for reviewer assignment. The generated queue is not
  acceptance evidence.
- `src.realworld.acceptance_task_assignments` and
  `scripts/write_acceptance_task_assignments.py` assign every unresolved formal
  blocker row to a deterministic review-agent role. The generated task table is
  an auditable work-allocation aid only; it cannot approve gates.
- `src.realworld.formal_acceptance_evidence_matrix` and
  `scripts/write_formal_acceptance_evidence_matrix.py` join each required
  formal target to its review agent, template or worksheet, review packets,
  current blockers, source paths, and validation command. The generated matrix
  is reviewer intake only and cannot approve gates.
- `src.realworld.formal_evidence_path_audit` and
  `scripts/audit_formal_evidence_paths.py` check reviewer-supplied formal
  artifacts for missing local evidence paths, unresolved placeholders, empty
  evidence records, and external-reference review needs. This is path hygiene
  only; it does not certify evidence quality or approve gates.
- `src.realworld.road_evidence` and `scripts/audit_road_evidence.py` audit
  the cached road graph. The current cache has parseable lengths but still
  relies on maxspeed fallbacks, capacity proxies, and disruption-probability
  proxies for final-study purposes.
- `src.realworld.road_evidence_diagnostics` and
  `scripts/audit_road_evidence_diagnostics.py` rank routeable highway classes
  by speed, capacity, and base-disruption evidence gaps so reviewed overrides
  can target the roads that matter most.
- `src.realworld.road_speed_evidence` and
  `scripts/write_road_speed_evidence.py` summarize sparse cached OSM
  `maxspeed` tags by routeable road class. The current candidate table has 10
  rows and 5 classes with observed tags; it is a speed-review aid only.
- `src.realworld.road_capacity_evidence` and
  `scripts/write_road_capacity_evidence.py` summarize cached OSM `lanes` tags
  by routeable road class. The current candidate table has 10 rows and 0
  classes with observed lane tags; it documents the capacity evidence gap.
- `src.realworld.road_evidence_review_packet` and
  `scripts/write_road_evidence_review_packet.py` consolidate road-class
  diagnostics, sparse `maxspeed` evidence, lane-count evidence, and draft
  overrides into a 10-row review worksheet. All current rows remain weak for
  final-study road claims.
- `src.realworld.road_evidence_request_packet` and
  `scripts/write_road_evidence_source_request_packet.py` produce a 5-row
  source-request worksheet for collecting source-backed road speed, capacity,
  benchmark, disruption, and override-application evidence. It is a request
  aid only and does not create `road_class_overrides.csv`.
- `src.realworld.road_overrides` can load reviewed road-class speed, capacity,
  and base-disruption override tables for future calibrated or source-backed
  road evidence. The default pilot path does not apply an override table yet.
- `src.realworld.road_override_template` and
  `scripts/write_road_class_override_template.py` can create a draft
  non-acceptance override template from the current road-class diagnostics so
  reviewers can replace mapper defaults with real evidence where it matters
  most.
- `data/parameters/road_class_overrides_draft.csv` is the current generated
  review worksheet: 10 routeable road-class rows, all still labeled
  `expert assumption`, so it is not publication evidence.
- `src.realworld.road_override_audit` and `scripts/audit_road_overrides.py`
  report that no reviewed default road-class override table is currently
  present and no accepted pilot manifest applies one, so built-in road proxies
  remain a final-claim blocker.
- `data/parameters/rail_service_evidence.csv` records the current rail timing
  values as an offline assumption proxy and keeps rail capacity explicitly
  sensitivity-only. `src.realworld.rail_evidence` and
  `scripts/audit_rail_evidence.py` keep this separate from future cached
  timetable or GTFS-derived timing evidence.
- `src.realworld.rail_evidence_review_packet` and
  `scripts/write_rail_evidence_review_packet.py` consolidate station-binding
  readiness, rail timing gaps, capacity treatment, service-window assumptions,
  availability assumptions, and derivation paths into a 10-row review
  worksheet. The current packet keeps service publication readiness false.
- `src.realworld.rail_timing_request_packet` and
  `scripts/write_rail_timing_source_request_packet.py` write a 5-row request
  worksheet that names the API key, GTFS file, capacity, and availability
  inputs needed before cached rail timing evidence can be derived.
- `data/rail/pilot_station_binding_cache.csv` stores the cached Seoul Open
  Data Plaza station-name search extract used for official line-specific
  station identifiers.
- `data/parameters/rail_station_bindings.csv` records current `S` and `R`
  rail points as official station-code bindings. `src.realworld.rail_station_binding`
  and `scripts/audit_rail_station_bindings.py` keep this station binding
  separate from rail headway, travel-time, capacity, and service-availability
  evidence.
- `src.realworld.rail_station_cache` and
  `scripts/derive_rail_station_bindings.py` can derive official station
  bindings from a reviewed cached station extract without live API calls.
- `src.realworld.rail_timetable` and
  `scripts/derive_rail_service_evidence.py` can derive rail headway and travel
  time from a reviewed cached timetable extract without live API calls and
  record field-level evidence plus source artifact SHA256. No such extract is
  committed for the current pilot yet.
- `scripts/derive_rail_headway_evidence.py` can derive headway-only evidence
  from reviewed access-station timetable rows. It deliberately leaves travel
  time as a proxy so a separate shortest-path, GTFS, or timetable record is
  still required for the travel-time evidence gate.
- `src.realworld.rail_gtfs` and `scripts/derive_rail_gtfs_evidence.py` can
  derive scheduled headway and access-to-egress travel time from a reviewed
  static GTFS zip or directory while preserving source artifact SHA256. No
  reviewed GTFS feed is committed for the current pilot, and GTFS timing does
  not establish emergency rail availability or train capacity.
- `src.realworld.rail_timetable_api` and
  `scripts/fetch_rail_timetable_cache.py` can create the timetable cache from
  a reviewed data.go.kr train-schedule request when `DATA_GO_KR_KEY` or
  `--service-key` is available. This live fetch path is optional and is not
  part of default offline validation.
- `src.realworld.rail_shortest_path` and
  `scripts/derive_rail_shortest_path_evidence.py` can derive station-to-station
  rail travel-time evidence from a reviewed cached shortest-path extract,
  verify station codes against official rail-point bindings, and preserve the
  source artifact SHA256. This path supplies travel time only; headway and
  capacity still require separate evidence or sensitivity-only treatment.
- `src.realworld.rail_shortest_path_api` and
  `scripts/fetch_rail_shortest_path_cache.py` can create the shortest-path
  cache from a reviewed data.go.kr request when `DATA_GO_KR_KEY` or
  `--service-key` is available. This live fetch path is optional and is not
  part of default offline validation.
- `data/validation/` stores route plausibility sanity checks for the pilot
  scaffold and is backed by `src.realworld.plausibility`.
- `scripts/run_osrm_route_benchmark.py` can generate an optional OSRM route
  benchmark snapshot. It is not part of offline default tests and is not ground
  truth.
- `scripts/write_osrm_snapshot_manifest.py` records the cached OSRM CSV and
  summary checksums, query URLs, live/unpinned status, and non-acceptance claim
  boundary.
- `scripts/run_full_graph_smoke.py` runs a tiny two-policy smoke on the full
  4,608-node / 9,148-edge bus-practical graph without corridor reduction. This
  writes `data/validation/full_graph_smoke_manifest.json` and is feasibility
  evidence only, not final full-graph experiment evidence.
- `src.realworld.full_graph_runtime_readiness_packet` and
  `scripts/write_full_graph_runtime_readiness_packet.py` write a 4-row
  full-graph runtime/readiness worksheet. It records the full-graph smoke,
  missing full-profile full-graph outputs, runtime-scope review, and
  downstream regeneration decisions without closing graph-scale acceptance.
- `src.realworld.graph_scale_diagnostics` and
  `scripts/run_graph_scale_diagnostics.py` compare the three canonical
  baseline road legs on the full bus-practical graph and the reduced analysis
  corridor. Current rows all pass for shortest-time path preservation, but this
  is scaffold route-parity evidence only and not graph-scale acceptance.
- The same graph-scale diagnostic run also writes
  `data/validation/graph_scale_alternate_routes.csv`. Current output has 9
  rows: 3 rank-1 pass rows and 6 alternate-route warning rows, so omitted
  alternate corridors remain graph-scale uncertainty.
- A multi-corridor candidate graph preserving the top 3 full-graph route
  candidates for each canonical leg is also diagnosed. It has 164 nodes and
  246 edges, with 9 pass rows in
  `data/validation/graph_scale_multi_corridor_routes.csv`; it remains an
  upgrade path rather than accepted final-study evidence.
- `src.realworld.graph_scale_review` and
  `scripts/write_graph_scale_review_packet.py` summarize the current
  reduced-corridor, small multi-corridor candidate, full-profile
  multi-corridor candidate, and full-graph options into a 4-row review packet.
  This is a method-selection worksheet only and does not close
  `data/manifests/graph_scale_acceptance.json`.
- `src.realworld.graph_scale_result_comparison` and
  `scripts/write_graph_scale_result_comparison.py` compare the current full
  pilot summary against the full-profile multi-corridor candidate summary as
  819 metric-level delta rows. This is review evidence only and does not close
  graph-scale acceptance.
- `data/scenarios/` now contains structured disruption scenarios and policy
  alternatives backed by deterministic loader/validator modules.
- `scripts/run_pilot_experiments.py --sample` writes separated pilot scaffold
  sample outputs under `results/realworld_pilot/`.
- `scripts/run_pilot_experiments.py --multi-corridor` writes a separated
  32-row / 16-summary-row candidate output on the 164-node / 246-edge
  multi-corridor graph for graph-scale review. It does not replace the current
  sample, staged, or full outputs.
- `scripts/run_pilot_experiments.py --multi-corridor-full` writes a separated
  1,890-row / 63-summary-row full-profile candidate output on the same
  164-node / 246-edge graph. It is stronger graph-scale review evidence, not
  graph-scale acceptance.
- `src.realworld.experiment_acceptance` validates optional
  `data/manifests/experiment_acceptance.json` records for reviewed pilot
  experiment outputs, graph scope, input validation, scenario-policy-seed
  design, common-random-number pairing, and not-operational claim boundaries.
  The file is intentionally absent in the current scaffold.
- `src.realworld.experiment_strategy_readiness_packet` and
  `scripts/write_experiment_strategy_readiness_packet.py` turn the 9-row full
  experiment-package worksheet into blocker/readiness rows. It separates
  scaffold result scope, graph-scale dependency, upstream input-evidence
  dependency, row-count/checksum/design/CRN review, and missing
  `experiment_acceptance.json` without accepting full outputs.
- `scripts/run_sensitivity.py --sample` writes scaffold sensitivity screening
  outputs and a SALib-compatible problem manifest under `results/realworld_pilot/`.
- `scripts/run_sensitivity.py --method morris --all` writes SALib Morris
  sensitivity outputs for the current full policy/scenario scaffold.
- `scripts/audit_sensitivity_diagnostics.py` reports Morris row-count
  consistency, blank/non-finite index values, zero `mu_star` rows, reduced
  graph scope, and scaffold claim boundaries without accepting final-study
  sensitivity claims.
- `src.realworld.sensitivity_review_packet` and
  `scripts/write_sensitivity_review_packet.py` turn those diagnostics into a
  6-row reviewer worksheet under `data/validation/`. It is review support only,
  not sensitivity acceptance or a Sobol waiver.
- `src.realworld.sensitivity_strategy_readiness_packet` and
  `scripts/write_sensitivity_strategy_readiness_packet.py` turn the 6-row
  sensitivity review worksheet into a 7-row blocker/readiness packet. It
  separates missing/non-finite Morris indices, zero `mu_star` interpretation,
  reduced graph scope, scaffold result scope, missing Morris-vs-Sobol decision,
  and missing `sensitivity_acceptance.json` without accepting sensitivity
  evidence.
- `src.realworld.validation_review_packet` and
  `scripts/write_validation_review_packet.py` turn route plausibility,
  fallback/OSRM benchmark, OSRM snapshot-manifest, accessibility-loss,
  route-level road-evidence exposure, and validation-summary scope artifacts
  into a 7-row reviewer worksheet. It is review support only, not
  validation acceptance or benchmark-strategy approval.
- `src.realworld.route_road_evidence_exposure` and
  `scripts/write_route_road_evidence_exposure.py` link weak road speed,
  capacity, disruption, and connector assumptions to canonical route
  candidates. The current 76-row worksheet is prioritization support only.
- `src.realworld.sensitivity_acceptance` validates optional
  `data/manifests/sensitivity_acceptance.json` records for the final
  sensitivity method, graph scope, parameter-range review, NaN/masked-value
  review, and Sobol decision. The file is intentionally absent in the current
  scaffold.
- `scripts/make_pilot_figures.py` generates scaffold-only PNG figures, result
  tables, bottleneck attribution proxy, policy regime map, and a
  claim-boundary table from the current full pilot and Morris CSVs.
- `scripts/audit_plan_artifacts.py` checks expected scaffold CSV row counts,
  JSON manifests, documentation artifacts, parameter evidence readiness, and
  the conservative claim boundary.
- `scripts/audit_source_provenance.py` validates the source provenance review
  packet without accepting final-study provenance.
- `scripts/write_pilot_privacy_review_packet.py` converts the pilot region
  YAML and data card into privacy/sensitivity review rows without accepting
  the pilot case.
- `scripts/write_source_license_review_packet.py` converts the source
  provenance manifest into source-by-source license, attribution, snapshot,
  privacy, and reproducibility review rows without accepting provenance.
- `scripts/write_source_url_review_packet.py` converts source provenance
  citations into URL-level reviewer rows. It is offline parse-only by default;
  optional `--live` reachability checks remain volatile and do not accept
  provenance.
- `scripts/write_experiment_package_review_packet.py` checks the full pilot
  manifest, result CSV, summary CSV, design counts, CRN declaration, graph
  scope, input dependencies, and checksums without accepting the experiment.
- `scripts/write_claim_alignment_review_packet.py` scans the paper draft,
  report source, and figure/table manifest for claim language that needs
  revision or formal acceptance before manuscript approval.
- `scripts/audit_publication_readiness.py` aggregates parameter, road, rail
  service, and station-binding evidence gates. It reports current blockers
  without failing by default, and can fail intentionally with `--fail-on-blockers`.
- `scripts/audit_final_study_readiness.py` maps the `plan.md` final definition
  of done to concrete artifacts and separates scaffold artifact presence from
  final-study readiness across pilot acceptance, graph scale, evidence,
  validation, experiments, sensitivity, manuscript/report, reproducibility, and
  final audit gates.
- `docs/analysis_corridor_method_note.md` records that the current 118-node /
  174-edge analysis corridor is a scaffold and performance abstraction, not
  accepted final-study evidence.
- `docs/graph_scale_acceptance_schema.md` defines the explicit review record
  required before a corridor abstraction, full-graph runtime, or
  multi-corridor ensemble can close the graph-scale strategy gate.
- `docs/validation_acceptance_schema.md` defines the explicit review record
  required before route plausibility and external benchmark evidence can close
  the validation-package gate.
- `docs/experiment_acceptance_schema.md` defines the explicit review record
  required before generated pilot rows can close the full-experiment-output
  gate.
- `docs/provenance_acceptance_schema.md` defines the explicit review record
  required before source/license/snapshot provenance can close the
  data-provenance gate.
- `docs/manuscript_acceptance_schema.md` defines the explicit review record
  required before paper/report wording can close the manuscript/report gate.
- `docs/reproducibility_acceptance_schema.md` defines the explicit review
  record required before clean-checkout reproduction can close the
  reproducibility gate.
- `docs/final_audit_acceptance_schema.md` defines the explicit review record
  required before the independent final-audit gate can close.
- `docs/reproducibility_package.md` and
  `data/manifests/reproducibility_manifest.json` record the current
  scaffold-only reproduction package.
- `docs/reproducibility_review_packet.md`,
  `data/validation/reproducibility_review_packet.csv`, and
  `data/validation/reproducibility_review_manifest.json` make clean-checkout
  reproducibility blockers executable without creating acceptance.
- `docs/reproducibility_smoke.md`,
  `data/validation/reproducibility_smoke_manifest.json`, and
  `data/validation/reproducibility_smoke_log.jsonl` record a bounded
  current-worktree smoke run. This helps reviewers inspect executable checks
  but does not replace clean-checkout reproduction or create acceptance.
- `docs/plan_completion_audit.md` records the current plan-gate audit and
  distinguishes complete scaffold evidence from remaining final-study blockers.
- `scripts/write_goal_completion_audit.py` writes
  `docs/current_goal_completion_audit.md`, a non-acceptance prompt-to-artifact
  checklist for the active `plan.md` objective.

Default validation is offline:

```powershell
.\.venv\Scripts\python tests\test_realworld_types.py
.\.venv\Scripts\python tests\test_realworld_attributes.py
.\.venv\Scripts\python tests\test_realworld_osm_network.py
.\.venv\Scripts\python tests\test_realworld_adapter.py
.\.venv\Scripts\python tests\test_realworld_validation.py
.\.venv\Scripts\python tests\test_realworld_end_to_end.py
.\.venv\Scripts\python tests\test_realworld_pilot_smoke.py
.\.venv\Scripts\python tests\test_realworld_parameters.py
.\.venv\Scripts\python tests\test_realworld_graph_scale_acceptance.py
.\.venv\Scripts\python tests\test_realworld_graph_scale_diagnostics.py
.\.venv\Scripts\python tests\test_realworld_full_graph_runtime_readiness_packet.py
.\.venv\Scripts\python tests\test_realworld_graph_scale_review.py
.\.venv\Scripts\python tests\test_realworld_graph_scale_result_comparison.py
.\.venv\Scripts\python tests\test_realworld_validation_acceptance.py
.\.venv\Scripts\python tests\test_realworld_parameter_acceptance.py
.\.venv\Scripts\python tests\test_realworld_parameter_audit.py
.\.venv\Scripts\python tests\test_realworld_parameter_review_packet.py
.\.venv\Scripts\python tests\test_realworld_pilot_acceptance.py
.\.venv\Scripts\python tests\test_realworld_pilot_privacy_review_packet.py
.\.venv\Scripts\python tests\test_realworld_provenance_acceptance.py
.\.venv\Scripts\python tests\test_realworld_source_license_review_packet.py
.\.venv\Scripts\python tests\test_realworld_source_url_review_packet.py
.\.venv\Scripts\python tests\test_realworld_manuscript_acceptance.py
.\.venv\Scripts\python tests\test_realworld_claim_alignment_review_packet.py
.\.venv\Scripts\python tests\test_realworld_reproducibility_acceptance.py
.\.venv\Scripts\python tests\test_realworld_reproducibility_review_packet.py
.\.venv\Scripts\python tests\test_realworld_reproducibility_smoke.py
.\.venv\Scripts\python tests\test_realworld_final_audit_acceptance.py
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
.\.venv\Scripts\python tests\test_realworld_accessibility.py
.\.venv\Scripts\python tests\test_realworld_disruption_scenarios.py
.\.venv\Scripts\python tests\test_realworld_policy_alternatives.py
.\.venv\Scripts\python tests\test_realworld_pilot_experiments.py
.\.venv\Scripts\python tests\test_realworld_experiment_acceptance.py
.\.venv\Scripts\python tests\test_realworld_experiment_package_review_packet.py
.\.venv\Scripts\python tests\test_realworld_experiment_strategy_readiness_packet.py
.\.venv\Scripts\python tests\test_realworld_sensitivity.py
.\.venv\Scripts\python tests\test_realworld_sensitivity_acceptance.py
.\.venv\Scripts\python tests\test_realworld_sensitivity_review_packet.py
.\.venv\Scripts\python tests\test_realworld_sensitivity_strategy_readiness_packet.py
.\.venv\Scripts\python tests\test_realworld_osrm_snapshot_manifest.py
.\.venv\Scripts\python tests\test_realworld_validation_review_packet.py
.\.venv\Scripts\python tests\test_realworld_route_road_evidence_exposure.py
.\.venv\Scripts\python tests\test_realworld_acceptance_records.py
.\.venv\Scripts\python tests\test_realworld_acceptance_orchestration.py
.\.venv\Scripts\python tests\test_realworld_acceptance_blocker_queue.py
.\.venv\Scripts\python tests\test_realworld_acceptance_task_assignments.py
.\.venv\Scripts\python tests\test_realworld_formal_acceptance_evidence_matrix.py
.\.venv\Scripts\python tests\test_realworld_formal_evidence_path_audit.py
```

Pilot scaffold commands below are offline except for the explicitly optional
OSRM benchmark command:

```powershell
.\.venv\Scripts\python scripts\build_pilot_cache.py
.\.venv\Scripts\python scripts\run_pilot_smoke.py
.\.venv\Scripts\python scripts\run_full_graph_smoke.py
.\.venv\Scripts\python scripts\run_graph_scale_diagnostics.py
.\.venv\Scripts\python scripts\write_full_graph_runtime_readiness_packet.py
.\.venv\Scripts\python scripts\write_graph_scale_review_packet.py
.\.venv\Scripts\python scripts\write_graph_scale_result_comparison.py
.\.venv\Scripts\python scripts\run_acceptance_audit.py
.\.venv\Scripts\python scripts\audit_rail_evidence.py
.\.venv\Scripts\python scripts\write_rail_evidence_review_packet.py
.\.venv\Scripts\python scripts\write_rail_timing_source_request_packet.py
.\.venv\Scripts\python scripts\audit_rail_station_bindings.py
.\.venv\Scripts\python scripts\audit_parameter_evidence.py
.\.venv\Scripts\python scripts\write_parameter_review_packet.py
.\.venv\Scripts\python scripts\write_parameter_evidence_source_request_packet.py
.\.venv\Scripts\python scripts\audit_road_evidence.py
.\.venv\Scripts\python scripts\audit_road_evidence_diagnostics.py
.\.venv\Scripts\python scripts\write_road_capacity_evidence.py
.\.venv\Scripts\python scripts\write_road_speed_evidence.py
.\.venv\Scripts\python scripts\write_road_evidence_review_packet.py
.\.venv\Scripts\python scripts\write_road_evidence_source_request_packet.py
.\.venv\Scripts\python scripts\write_road_class_override_template.py --output data\parameters\road_class_overrides_draft.csv --overwrite
.\.venv\Scripts\python scripts\audit_road_overrides.py
.\.venv\Scripts\python scripts\audit_publication_readiness.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
.\.venv\Scripts\python scripts\run_plausibility_validation.py
.\.venv\Scripts\python scripts\run_accessibility_loss_analysis.py
.\.venv\Scripts\python scripts\write_osrm_snapshot_manifest.py
.\.venv\Scripts\python scripts\write_route_road_evidence_exposure.py
.\.venv\Scripts\python scripts\write_validation_review_packet.py
.\.venv\Scripts\python scripts\write_reproducibility_review_packet.py
.\.venv\Scripts\python scripts\write_experiment_strategy_readiness_packet.py
.\.venv\Scripts\python scripts\run_reproducibility_smoke.py
.\.venv\Scripts\python scripts\audit_tracked_artifacts.py
.\.venv\Scripts\python scripts\audit_formal_evidence_paths.py
.\.venv\Scripts\python scripts\run_pilot_experiments.py --sample
.\.venv\Scripts\python scripts\run_pilot_experiments.py --staged
.\.venv\Scripts\python scripts\run_pilot_experiments.py --multi-corridor
.\.venv\Scripts\python scripts\run_pilot_experiments.py --multi-corridor-full
.\.venv\Scripts\python scripts\run_pilot_experiments.py --full
.\.venv\Scripts\python scripts\run_sensitivity.py --sample
.\.venv\Scripts\python scripts\run_sensitivity.py --method morris --all
.\.venv\Scripts\python scripts\audit_sensitivity_diagnostics.py
.\.venv\Scripts\python scripts\write_sensitivity_review_packet.py
.\.venv\Scripts\python scripts\write_sensitivity_strategy_readiness_packet.py
.\.venv\Scripts\python scripts\make_pilot_statistics.py
.\.venv\Scripts\python scripts\make_pilot_statistics.py --input results\realworld_pilot\pilot_multi_corridor_results.csv --source-manifest results\realworld_pilot\pilot_multi_corridor_manifest.json --output-prefix pilot_multi_corridor
.\.venv\Scripts\python scripts\make_pilot_statistics.py --input results\realworld_pilot\pilot_multi_corridor_full_results.csv --source-manifest results\realworld_pilot\pilot_multi_corridor_full_manifest.json --output-prefix pilot_multi_corridor_full
.\.venv\Scripts\python scripts\make_pilot_figures.py
.\.venv\Scripts\python scripts\audit_plan_artifacts.py
.\.venv\Scripts\python scripts\write_goal_completion_audit.py
```

Optional live external-router snapshot:

```powershell
.\.venv\Scripts\python scripts\run_osrm_route_benchmark.py
```

Offline OSRM snapshot manifest:

```powershell
.\.venv\Scripts\python scripts\write_osrm_snapshot_manifest.py
```

Explicit cache refresh commands:

```powershell
.\.venv\Scripts\python scripts\build_pilot_cache.py --source fixture
.\.venv\Scripts\python scripts\build_pilot_cache.py --source overpass
```

Optional live OSM extraction is available only when `osmnx` is installed and
called explicitly through `src.realworld.osm_network.extract_bbox_graph(...)`
or `load_or_extract_bbox_graph(...)`. Unit tests must remain offline and should
use cached GraphML or synthetic fixtures.

Outputs from this path should be described as quasi-real decision-support
experiments. The current pilot cache is an Overpass/OSM-derived GraphML
snapshot for repeatable offline smoke and sample runs; publication claims still
require human source review, parameter-source tables, rail evidence,
disruption assumptions, and validation benchmarks.
The current parameter, validation, disruption, and policy files are evidence
scaffolds for the pilot path. The sample/staged/full pilot outputs are
separated from old abstract-network results and are not calibrated real-world
results.

## Config Semantics

`config.yaml` keeps the legacy experiment keys and adds operational namespaces
used by the current scenario runner.

- `network.road_links`: `[from, to, t0_min, capacity_veh_per_hr, base_p_fail]`.
- `network.rail_link`: `[from, to, t0_min, headway_min, capacity_pax_per_train]`.
- `personnel.total`: total passengers in each scenario.
- `personnel.group_size`: vehicle capacity and scheduled batch target.
- `personnel.assembly_time`: absolute assembly time in minutes from midnight.
- `bus.first_departure_min`, `bus.dispatch_interval_min`, `bus.fleet_size`,
  `bus.turnaround_min`: bus-only schedule anchor, dispatch cadence, fleet size,
  and fleet reuse.
- `multimodal.shuttle_first_departure_min`,
  `multimodal.shuttle_dispatch_interval_min`, `multimodal.shuttle_fleet_size`:
  shuttle schedule anchor, dispatch cadence, and fleet size.
- `multimodal.transfer_time_min` and `transfer_per_passenger_min`: transfer
  delay as `base + per_passenger * passenger_count`.
- `multimodal.rail_first_departure_min`: optional first train departure time;
  `null` keeps the default fixed-headway convention.
- `multimodal.lastmile_first_departure_min`,
  `multimodal.lastmile_dispatch_interval_min`,
  `multimodal.lastmile_fleet_size`, `multimodal.lastmile_turnaround_min`, and
  `multimodal.lastmile_vehicle_capacity`: schedule anchor, cadence, finite
  fleet size, reuse time, and vehicle capacity for the road last-mile leg after
  rail arrival.
- `traffic.volume_window_min`: rolling window used to convert simulated vehicle
  entries into hourly BPR volume.
- `traffic.background_volume`: baseline vehicles/hour added to dynamic volume.
- `failure.mode`: `blocked` or `capacity_reduction`.
- `failure.capacity_reduction_factor`: effective capacity multiplier for
  degraded road links, with `0 < factor <= 1`.
- `metrics.late_penalty_min`: per-censored-passenger penalty used by
  `penalized_makespan`.

The configuration includes explicit first-departure fields, finite last-mile
fleet controls, network variant selection, and expanded failure-sensitivity
controls.

`failure_rate.levels` are `p_fail_scale` multipliers, not absolute failure
probabilities. For each road link, sampled probability is:

```text
min(edge_base_p_fail * p_fail_scale, 1.0)
```

Rail links are immune to sampled failures by default.

## Implemented Behavior

- STRICT and GRACE operate on passenger queues. STRICT departs at the scheduled
  time with arrived passengers only; GRACE waits until max wait, threshold, or
  vehicle capacity.
- The GRACE denominator is the scheduled batch target, capped by remaining
  queued demand. The default target is `personnel.group_size`.
- Bus-only, multimodal shuttle, and multimodal last-mile road dispatch use
  configurable finite fleet controls where applicable.
- Rail uses fixed headway; later train departures are not serialized behind
  earlier train travel.
- Bus, shuttle, rail, and last-mile services use explicit first-departure
  semantics where configured. Rail uses
  `multimodal.rail_first_departure_min`.
- Road travel chooses a shortest path at vehicle departure and evaluates BPR at
  each edge entry using current rolling-window traffic volume.
- Failures are structured per-edge states and support both full blockage and
  capacity reduction.
- Multimodal transfers include fixed and crowd-dependent delay.
- Metrics expose censoring through `censored_count`, `completion_rate`, and
  `penalized_makespan` in addition to legacy makespan and success-rate fields.
- Phase 1 and Phase 2 use common random numbers by running paired bus-only and
  multimodal scenarios with the same seed.

## Implemented Model Alignment

- Last-mile movement uses a finite fleet, turnaround, and vehicle capacity model.
- Dispatch schedules use explicit first-departure semantics for bus, shuttle,
  and last-mile services where applicable.
- Resource accounting is split into unit-consistent KPIs such as road
  vehicle-minutes, train-minutes, passenger-minutes, and passengers per service
  minute. The legacy `resource_efficiency` column is documented as an alias.
- Named network variants allow route redundancy to be compared fairly.
- Failure sensitivity spans disruption mode, capacity-reduction factor,
  `p_fail_scale`, and network variant.
- The default Phase 1 sweep uses `baseline` and `matched_redundancy`.
  `multimodal_redundant_lastmile` and `bus_single_corridor` are declared
  selectable sensitivity variants, not part of the current default full result
  set.

## Outputs And Report

Experiment runs write CSV files and plots under `results/`. The current full
result set has 8,400 Phase 1 rows and 840 Phase 2 rows. The Word report is
generated from the Korean Markdown source:

```powershell
.\.venv\Scripts\python generate_report.py
```

After model code changes pass, refresh outputs in this order:

```powershell
.\.venv\Scripts\python -m compileall main.py src tests generate_report.py
Get-ChildItem tests\test_*.py | ForEach-Object { .\.venv\Scripts\python $_.FullName }
.\.venv\Scripts\python main.py --test
.\.venv\Scripts\python main.py --quick
.\.venv\Scripts\python main.py --phase 1
.\.venv\Scripts\python main.py --phase 2
.\.venv\Scripts\python generate_report.py
```

Edit `report_draft.md` for Korean narrative changes, then regenerate
`report.docx`. Do not edit `report.docx` manually unless deliberately accepting
Word-only formatting changes. If model semantics change again, rerun Phase 1/2
before reusing CSV/PNG conclusions.

## Remaining Limitations

- The transport network is abstract and intentionally small; it is not an OSM
  or calibrated Seoul network in the current generated result set.
- Dynamic road traffic uses a rolling-window approximation, not full traffic
  assignment, spillback, signal timing, or lane-level simulation.
- Rail is failure-immune by default and uses a single fixed-headway service.
- Operational parameters are uncalibrated scenario assumptions, not field
  estimates.
- The real-world MVP now has an offline public-coordinate pilot scaffold,
  but it has not yet produced a reviewed OSM-derived or calibrated pilot study.
- Parameter-source, plausibility, disruption, and policy tables now exist, and
  sample, staged, full, deterministic screening, and SALib Morris scaffold
  outputs have been generated; calibrated sensitivity evidence and reviewed
  publication-grade acceptance have not been achieved.
- Scaffold-only figures and tables exist under `results/realworld_pilot/`; they
  should not be used as publication-grade evidence until the accepted pilot
  inputs and final experiments exist.
- OSM-derived roads and zone connectors are still assumption-based simulator
  inputs until travel times, capacities, disruption probabilities, and rail
  service assumptions are validated.
- Existing generated outputs should be reviewed as stale whenever schedule,
  fleet, KPI, network, or failure experiment semantics change.

## Real-World Upgrade Direction

The implemented MVP establishes the adapter layer, first offline pilot smoke
path, parameter-source tables, plausibility checks, disruption scenarios, policy
alternatives, sample/staged/full pilot experiment profiles, deterministic
screening, and SALib Morris scaffold screening. The next major target is to
review the current OSM-derived cache as an accepted pilot snapshot or replace it
with a better snapshot, review the staged/full outputs, and document the data
provenance:

- OSMnx/Pyrosm road-network extraction and cached GraphML review
- GeoPandas/Shapely region clipping and zone handling
- H3 or administrative-grid sensitive-location abstraction
- GTFS or documented rail timetable assumptions
- spatial hazard/exposure overlays and critical-link disruptions
- routing-engine plausibility checks with tools such as OSRM, Valhalla, r5py,
  routingpy, or UXsim; the current optional OSRM snapshot has 3 pass rows after
  bus-practical road filtering, and its manifest records 3 live/unpinned rows
  plus query URLs and checksums; this remains plausibility evidence, not
  calibration
- graph-scale route parity checks now show that the reduced corridor preserves
  the current full-graph baseline shortest-time paths for `A -> D`, `A -> S`,
  and `R -> D`; alternate corridor sensitivity or full-graph/multi-corridor
  evidence is still needed before graph-scale acceptance; the current
  alternate-route diagnostic makes this visible with 6 warning rows, and the
  current multi-corridor candidate shows one 164-node / 246-edge way to
  preserve the top route candidates; the graph-scale review packet now
  compares those three method options in one non-acceptance worksheet
- pilot experiment runner and result schemas separated from abstract outputs
- deterministic sensitivity screening and SALib Morris scaffold screening now
  exist; a 6-row sensitivity review packet now makes Morris index handling,
  zero-effect interpretation, reduced-graph scope, and the Morris-vs-Sobol
  decision explicit; optional Sobol remains a later upgrade
- figure/table generation now exists for current scaffold outputs; publication
  figure updates must wait for accepted pilot outputs

The intended paper thesis is:

> Rail-bus multimodal transport is a conditional resilience strategy whose
> performance depends on the joint reliability of access roads, rail service,
> transfer handling, last-mile capacity, and finite fleet availability under
> regional network disruption.
