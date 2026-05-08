# Real-World Pipeline Implementation Root

All new production code for the real-world or quasi-real regional transport
pipeline should live under this package.

Rules:

- Do not import runtime code from `cloned_repo/`.
- Do not edit files inside `cloned_repo/`.
- If a public repository contains useful logic, copy or reimplement only the
  minimum needed part here after checking license compatibility.
- Keep any adapted helper small, local, tested, and documented with provenance.
- Preserve the existing abstract-network simulator behavior unless an explicit
  integration change is accepted.

The first implementation target is an OSM-derived road graph adapter that emits
a simulator-compatible NetworkX graph for `run_scenario(...)`.

## Current Scaffold Status

- Final-study ready: `false`.
- Final-study gate status: `3/15` ready (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`) and `12/15` blocked.
- Formal acceptance ready: `0/12`; no formal approval artifacts are present.
- `data/validation/validation_strategy_readiness_packet.csv` and
  `data/validation/graph_scale_strategy_readiness_packet.csv`, and
  `data/validation/sensitivity_strategy_readiness_packet.csv`, and
  `data/manifests/experiment_strategy_readiness_packet.csv` are implemented
  preflight review aids only.
- Current abstract-network and pilot outputs are not calibrated real-world
  results, formal approvals, or operational route plans.

Implemented extension modules now also cover:

- `acceptance_decision_templates.py`: non-approval templates for formal
  acceptance decisions. It writes JSON/CSV worksheets with `accepted: false`
  and explicit template-only claim boundaries so reviewers can prepare real
  acceptance records without accidentally closing gates.
- `acceptance_blocker_queue.py`: formal acceptance blocker queue writer. It
  turns package blockers into one CSV row per reviewer action without creating
  approval records.
- `acceptance_task_assignments.py`: sub-agent task assignment writer. It maps
  each unresolved formal blocker row to the deterministic review-agent role
  responsible for resolving it, while keeping every task non-approval.
- `formal_acceptance_guard.py`: guard audit for formal acceptance paths. It
  detects copied templates, `REVIEW_REQUIRED` placeholders, and draft-only weak
  override rows so placeholder files cannot be mistaken for real acceptance.
- `formal_evidence_path_audit.py`: path-hygiene audit for reviewer-supplied
  formal artifacts. It checks evidence/source/reviewed-input paths for missing
  local files, unresolved placeholders, empty evidence records, and external
  references that still need source/license review; it does not approve gates.
- `formal_acceptance_package.py`: one-shot intake audit for reviewer-supplied
  formal acceptance artifacts. It aggregates the individual acceptance
  validators, road-override readiness, the formal guard, evidence-path hygiene,
  and final-study readiness without creating approvals.
- `parameters.py`: parameter-source table loading and coverage validation.
- `graph_scale_acceptance.py`: explicit source-vs-analysis graph decision
  acceptance records for final-study readiness.
- `graph_scale_diagnostics.py`: full-vs-reduced route parity and
  alternate-route diagnostics for the current canonical road legs; this
  supports corridor review but is not graph-scale acceptance. The current run
  also emits a multi-corridor candidate diagnostic.
- `graph_scale_review.py`: generated 4-option worksheet comparing the reduced
  corridor, small multi-corridor candidate, full-profile multi-corridor
  candidate, and full bus-practical graph. It is review support only and not
  graph-scale acceptance.
- `graph_scale_strategy_readiness_packet.py`: preflight worksheet generated
  from the graph-scale review rows and result-comparison manifest. It separates
  reduced-corridor alternate-route warnings, incomplete multi-corridor output,
  full-profile candidate result deltas, missing full-graph outputs, and missing
  graph-scale acceptance without choosing a graph-scale method.
- `graph_scale_result_comparison.py`: generated current-vs-full-profile
  multi-corridor candidate result-delta worksheet. It is review support only
  and not graph-scale acceptance.
- `validation_acceptance.py`: explicit validation-package and benchmark
  strategy acceptance records for final-study readiness.
- `validation_review_packet.py`: generated 7-row worksheet that turns internal
  route plausibility, fallback/OSRM benchmark, accessibility-loss,
  optional OSRM snapshot-manifest status, route-level road-evidence exposure,
  validation-summary scope, and benchmark-strategy blockers into review
  support without accepting validation evidence.
- `osrm_snapshot_manifest.py`: optional OSRM benchmark manifest generation for
  CSV/Summary checksums, query URLs, cached/unpinned status, raw response
  files, and claim limits.
- `route_road_evidence_exposure.py`: route-level review aid that links weak
  road speed, capacity, disruption, and connector assumptions to canonical
  route candidates without accepting road calibration.
- `parameter_acceptance.py`: optional weak-parameter acceptance records for
  reviewed assumptions retained inside final claim boundaries.
- `parameter_review_packet.py`: generated 29-row weak-parameter review
  worksheet and manifest. The packet marks 25 core parameters as weak for
  final-study claims and remains review support only.
- `pilot_acceptance.py`: explicit human-review acceptance record validation for
  the future final pilot case.
- `pilot_privacy_review_packet.py`: pilot-region privacy and sensitivity
  worksheet generated from the region YAML and data card. It checks boundary,
  public/synthetic points, coordinate policy, and claim-boundary review needs
  without approving the pilot case.
- `provenance_acceptance.py`: explicit source snapshot, license/attribution,
  privacy abstraction, cache manifest, reproducibility manifest, and
  not-operational claim-boundary acceptance records.
- `source_license_review_packet.py`: source-by-source license, attribution,
  snapshot, privacy, and reproducibility review worksheet generated from the
  source provenance manifest. It makes provenance blockers concrete but does
  not certify licenses or create `provenance_acceptance.json`.
- `source_url_remediation_packet.py`: URL-status remediation queue generated
  from the source URL review packet. It separates reachable URLs, unreachable
  public URLs, live-check gaps, and local-only citations without approving
  provenance.
- `rail_fetch_readiness_packet.py`: preflight worksheet generated from rail
  timing source requests. It separates missing API keys, missing reviewed GTFS
  files, and human-review-only capacity/availability decisions without fetching
  live data or approving rail evidence.
- `road_source_readiness_packet.py`: preflight worksheet generated from road
  evidence source requests. It separates sparse speed candidates, missing
  capacity sources, benchmark/disruption human-review decisions, and missing
  reviewed override application without approving road evidence.
- `parameter_source_readiness_packet.py`: preflight worksheet generated from
  cross-cutting parameter source requests. It separates demand, fleet,
  dispatch, transfer, disruption, and traffic/BPR review states without
  accepting weak assumptions or changing parameter tables.
- `validation_strategy_readiness_packet.py`: preflight worksheet generated
  from validation review rows. It separates internal warning rows, fallback
  benchmark warnings, unpinned OSRM snapshots, accessibility diagnostics,
  weak route-road exposure, summary scope, and missing validation acceptance
  without accepting a benchmark strategy.
- `manuscript_acceptance.py`: explicit English manuscript, Korean report,
  regenerated docx, figure/table manifest, evidence-gate, result-claim, and
  not-operational claim-boundary acceptance records.
- `claim_alignment_review_packet.py`: paper/report/figure-table claim
  worksheet that separates guardrail language from overclaim candidates
  without approving manuscript claims.
- `reproducibility_acceptance.py`: explicit clean-checkout validation,
  validation-ladder, artifact-regeneration, manifest-path, cloned-repo
  import-boundary, command-count, and not-operational claim-boundary acceptance
  records.
- `reproducibility_review_packet.py`: generated 8-row worksheet that records
  scaffold manifest scope, formal acceptance absence, Git worktree state,
  untracked artifact risk, validation command ladder, runtime `cloned_repo`
  import boundary, bounded clean-checkout smoke, and clean-checkout execution
  scope without accepting reproducibility evidence.
- `reproducibility_smoke.py`: bounded current-worktree smoke runner for the
  acceptance/reproducibility command ladder. It writes a manifest, JSONL log,
  and markdown summary while keeping clean-checkout acceptance blocked.
- `tracked_artifact_audit.py`: clean-checkout packaging audit. It lists
  changed repo artifacts that a checkout of current Git HEAD would miss unless
  they are committed, packaged, or explicitly excluded from the accepted
  reproduction scope.
- `final_audit_acceptance.py`: explicit independent prompt-to-artifact
  completion, gate evidence, no-proxy completion, gate-list/count, and
  not-operational claim-boundary acceptance records.
- `plausibility.py`: offline route, connector, speed, and capacity sanity
  checks for pilot scaffolds.
- `accessibility.py`: route-level directed edge-removal accessibility-loss and
  critical-edge diagnostics for scaffold fragility review.
- `disruption_scenarios.py`: deterministic structured disruption scenario
  definitions and edge mapping helpers.
- `policy_alternatives.py`: conservative policy-alternative tables and
  non-mutating config-variant helpers.
- `pilot_experiments.py`: cached pilot scaffold experiment runner that writes
  separated sample, staged, full, small multi-corridor candidate, and
  full-profile multi-corridor candidate outputs under
  `results/realworld_pilot/`.
- `experiment_acceptance.py`: explicit pilot experiment-output acceptance
  records for reviewed graph scope, input validation, scenario-policy-seed
  design, common-random-number pairing, row counts, and not-operational claim
  limits.
- `experiment_package_review_packet.py`: full pilot experiment worksheet that
  checks row counts, design counts, graph/input dependencies, CRN declaration,
  checksums, and acceptance absence without approving full outputs.
- `experiment_strategy_readiness_packet.py`: generated 9-row worksheet that
  classifies full-experiment blockers and human-review items before any formal
  experiment acceptance record is created. It does not accept full outputs or
  calibrated result claims.
- `sensitivity.py`: deterministic one-at-a-time sensitivity screening with
  SALib-compatible problem metadata for later Morris/Sobol expansion.
- `sensitivity_acceptance.py`: explicit sensitivity method, parameter range,
  NaN/masked-value, graph-scope, and Sobol-decision acceptance records.
- `sensitivity_review_packet.py`: generated 6-row worksheet that turns Morris
  diagnostics into review items for index handling, zero-effect interpretation,
  reduced graph scope, and Morris-vs-Sobol decision support without accepting
  sensitivity evidence.
- `sensitivity_strategy_readiness_packet.py`: generated 7-row worksheet that
  classifies sensitivity blockers and human-review items before any formal
  sensitivity acceptance record is created. It does not accept Morris/Sobol
  scope or final sensitivity evidence.
- `pilot_figures.py`: scaffold-only figures, tables, and claim-boundary
  artifacts generated from current pilot sample CSVs.
- `pilot_statistics.py`: seed-replication metric confidence intervals and
  paired policy-delta confidence intervals for pilot scaffold outputs.
- `road_capacity_evidence.py`: cached OSM `lanes` capacity-candidate evidence
  by routeable road class. The current generated table has 10 rows and 0 rows
  with observed lane tags; it remains evidence-gap review support only.
- `road_override_audit.py`: optional road-class override evidence readiness
  audit that keeps missing override tables visible as final-claim blockers.
  The current `data/parameters/road_class_overrides_draft.csv` worksheet has
  10 expert-assumption rows and remains review support only.
- `road_speed_evidence.py`: cached OSM `maxspeed` candidate evidence by
  routeable road class. The current generated table has 10 rows and 5 rows
  with observed tags; it remains review support only.
- `road_evidence_review_packet.py`: consolidated road-input review worksheet
  that joins road-class diagnostics, sparse OSM speed tags, lane-count
  evidence gaps, and draft override rows. The current generated table has 10
  routeable road-class rows, all weak for final-study road claims.
- `road_evidence_request_packet.py`: road evidence source-request worksheet
  that names the speed, capacity, benchmark, disruption, and override
  application inputs needed before a reviewed road-class override package can
  be built. It is request support only, not road evidence.
- `rail_station_binding.py`: rail-point to station-identifier evidence
  validation that keeps official station binding separate from rail service
  evidence.
- `rail_station_cache.py`: reviewed station-source extracts to official
  rail-point binding rows, without live API calls in default tests.
- `rail_timetable.py`: cached timetable extracts to rail-service timing
  evidence with source artifact SHA256, without live API calls in default
  tests.
- `rail_gtfs.py`: reviewed static GTFS zip or directory extracts to scheduled
  headway and access-to-egress travel-time evidence with source artifact
  SHA256, without live API calls in default tests.
- `rail_shortest_path.py`: cached station-to-station shortest-path extracts to
  rail travel-time evidence with official station-code checks and source
  artifact SHA256, without live API calls in default tests.
- `rail_evidence_review_packet.py`: consolidated rail review worksheet for
  station-binding status, current rail-service evidence, rail assumptions, and
  available cached-derivation paths. The current generated table has 10 rows
  and keeps service timing weak until reviewed cached evidence derives headway
  and travel time.
- `rail_timing_request_packet.py`: rail timing source-request worksheet for
  the exact API-key, GTFS, capacity, and availability inputs needed before
  source caches can become derived rail-service evidence. The current table has
  5 rows and is not timing evidence.
- `publication_readiness.py`: aggregated parameter, road, rail-service, and
  station-binding readiness gates for final-study claim control.

These modules support quasi-real study scaffolding. They do not by themselves
create calibrated real-world results or operational routing guidance.
