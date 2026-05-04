# Final Real-World Transport-Resilience Study Plan

## Purpose

Move the project from an implemented abstract-network simulator plus a working
real-world input MVP into a defensible real-world or quasi-real regional
transport-resilience study.

The target is not an operational routing product. The final artifact should be
a reproducible decision-support research package that can say:

```text
Under documented public-data inputs, explicit assumptions, validation checks,
and uncertainty analysis, this framework identifies when bus-only, rail-bus
multimodal, and redundancy policies are robust, competitive, or fragile under
regional network disruption.
```

Avoid claiming:

```text
The model predicts actual emergency operations or proves one mode is always
superior in the real world.
```

## Review Verdict

The plan covers the final research target as a master execution guide: real or
quasi-real regional inputs, region reuse, non-sensitive zone abstraction,
OSM/GraphML road ingestion, rail evidence, parameter provenance, structured
disruptions, policy alternatives, validation, sensitivity analysis, publication
figures/tables, manuscript/report alignment, and reproducibility.

The plan also explicitly includes GPT-5.5 xhigh subagents. The subagent plan is
kept as an execution strategy, not a substitute for integration: each worker
gets a bounded write set, the main integrator owns validation and claim
guardrails, and final publication claims are allowed only after the validation
gates pass.

A repo-native acceptance-orchestration layer now turns blocked gates into
deterministic review-agent records. It defines specialized review roles,
generates machine-readable records under `data/manifests/agent_reviews/`, and
writes human review packets under `docs/review_packets/`. This makes the
approval process executable and auditable, but it is not a substitute for
source-backed reviewer decisions or formal acceptance artifacts.

A non-approval acceptance-decision template layer now writes reviewer
worksheets for the missing formal acceptance artifacts. It generates 9 JSON
templates under `data/manifests/acceptance_templates/`, a 25-row
`data/parameters/parameter_acceptance_template.csv`, an aggregate
`data/manifests/acceptance_decision_template_manifest.json`, and
`docs/acceptance_decision_templates.md`. These templates intentionally keep
`accepted: false`; they are copy/edit aids for reviewers and do not close any
gate.

A human acceptance runbook now ties the review packets, templates, formal
targets, and validation commands together in `docs/human_acceptance_runbook.md`.
It gives reviewers the exact gate-by-gate workflow for moving from scaffold
evidence to formal acceptance without treating placeholders, tests, OSM
presence, or generated outputs as approval.

A formal acceptance blocker queue now converts the formal package blockers into
one CSV row per unresolved reviewer action. It writes
`data/manifests/formal_acceptance_blocker_queue.csv`,
`data/manifests/formal_acceptance_blocker_queue_manifest.json`, and
`docs/formal_acceptance_blocker_queue.md`. This makes the remaining work easier
to assign and audit, but it is still not approval evidence.

An acceptance task-assignment layer now maps each formal blocker queue row to a
deterministic review-agent role. It writes
`data/manifests/acceptance_task_assignments.csv`,
`data/manifests/acceptance_task_assignments_manifest.json`, and
`docs/acceptance_task_assignments.md`. The current assignment table has 15
tasks across 10 review-agent roles and remains work allocation only, not
approval evidence.

A formal acceptance evidence matrix now gives reviewers one row per required
formal target. It writes
`data/manifests/formal_acceptance_evidence_matrix.csv`,
`data/manifests/formal_acceptance_evidence_matrix_manifest.json`, and
`docs/formal_acceptance_evidence_matrix.md`, joining each target with the
assigned agent, template or worksheet, review packets, current blockers,
source paths, and validation command. It is reviewer intake only, not approval
evidence.

A formal acceptance artifact guard now checks the required acceptance paths for
copied templates, `REVIEW_REQUIRED` placeholders, and draft-only weak rows. The
current guard reports all 12 required formal acceptance artifacts as missing
and reports zero template/placeholder copies in formal paths. This guard
prevents a placeholder file from laundering a gate, but it also cannot approve
the study.

A formal evidence-path audit now checks reviewer-supplied formal artifacts for
missing local evidence paths, unresolved placeholders, empty evidence records,
and external references that still need source/license review. It writes
`data/manifests/formal_evidence_path_audit.json` and
`docs/formal_evidence_path_audit.md`, and is also embedded in the formal
acceptance package intake audit. This is path hygiene only; it does not certify
evidence quality or close any gate.

A formal acceptance package intake audit now aggregates all reviewer-supplied
formal acceptance artifacts into one command. It validates individual
acceptance records, road-class override readiness, the placeholder guard,
formal evidence-path hygiene, and the final-study readiness audit, then writes
`data/manifests/formal_acceptance_package_audit.json` and
`docs/formal_acceptance_package_audit.md`. This audit is for intake validation
only; it does not create approval records or fabricate evidence.

The plan is not itself proof that the project has reached the final research
state. It is complete only as a roadmap. The project becomes final only after
the acceptance gates, validation ladder, full pilot outputs, sensitivity
outputs, manuscript/report alignment, and final audit all pass.

This revision tightens five points that were previously under-specified:

- the current cached road graph is now an Overpass/OSM-derived snapshot, not
  only a hand-built fixture, and the adapter now filters pedestrian, cycling,
  platform, construction, track, living-street, and service-only geometries out
  of bus-practical simulator routes; it is still not a reviewed or calibrated
  publication-grade network;
- pilot sample experiments run on a reduced analysis corridor extracted from
  the cached graph so the current simulator remains performant while full
  network-scale methods are deferred;
- deterministic sensitivity screening exists, but publication-ready formal
  SALib Morris/Sobol analysis remains a final-study requirement until current
  outputs, manifests, tests, and result interpretation are finalized;
- official line-specific station-code bindings are now cached for `S` and `R`,
  but station binding remains separate from rail headway, travel-time,
  route-choice, and service-availability evidence; rail capacity is explicitly
  retained as sensitivity-only until stronger evidence is accepted;
- future GPT-5.5 xhigh workers should focus on the remaining publication
  gates rather than redoing already implemented scaffolds.

## Current State

The first real-world MVP is already implemented under `src/realworld/`.

Implemented and verified:

- Region, boundary, zone, rail-point, and rail-service specs.
- Optional OSMnx bbox extraction behind a lazy import boundary.
- Offline GraphML load/save helpers.
- OSM-style road attribute mapping to simulator fields.
- Zone and rail-point snapping to nearest OSM-like road nodes.
- Connector edge creation.
- OSM-like graph to simulator-compatible `networkx.DiGraph` adapter.
- Graph readiness validation.
- Synthetic end-to-end smoke test reaching `run_scenario(...)` for both
  `bus_only` and `multimodal`.
- Documentation describing quasi-real limitations and third-party adaptation
  provenance.

First pilot-smoke artifacts also exist:

- `data/regions/pilot_region.yaml` defines the `songpa_public_demo` public
  demo region.
- `docs/pilot_region_data_card.md` documents public/synthetic coordinate
  handling, claim limits, and reuse notes.
- `src/realworld/pilot_acceptance.py` and
  `docs/pilot_acceptance_schema.md` define the explicit human-review record
  required before the pilot-region gate can close. The actual
  `data/manifests/pilot_acceptance.json` file is intentionally absent in the
  current scaffold.
- `src/realworld/pilot_privacy_review_packet.py` and
  `scripts/write_pilot_privacy_review_packet.py` now split the pilot-region
  privacy review into row-level checks for the bbox, public assembly point,
  synthetic destination point, public rail points, coordinate policy, and data
  card claim boundary. The generated
  `data/manifests/pilot_privacy_review_packet.csv`,
  `data/manifests/pilot_privacy_review_manifest.json`, and
  `docs/pilot_privacy_review_packet.md` are reviewer aids only and do not
  close the pilot-region gate.
- `src/realworld/graph_scale_acceptance.py` and
  `docs/graph_scale_acceptance_schema.md` define the explicit review record
  required before the graph-scale strategy gate can close. The actual
  `data/manifests/graph_scale_acceptance.json` file is intentionally absent in
  the current scaffold.
- `src/realworld/validation_acceptance.py` and
  `docs/validation_acceptance_schema.md` define the explicit review record
  required before the validation-package gate can close. The actual
  `data/manifests/validation_acceptance.json` file is intentionally absent in
  the current scaffold.
- `src/realworld/sensitivity_acceptance.py` and
  `docs/sensitivity_acceptance_schema.md` define the explicit review record
  required before the sensitivity-analysis gate can close. The actual
  `data/manifests/sensitivity_acceptance.json` file is intentionally absent in
  the current scaffold.
- `src/realworld/experiment_acceptance.py` and
  `docs/experiment_acceptance_schema.md` define the explicit review record
  required before the full-experiment-output gate can close. The actual
  `data/manifests/experiment_acceptance.json` file is intentionally absent in
  the current scaffold.
- `src/realworld/experiment_package_review_packet.py` and
  `scripts/write_experiment_package_review_packet.py` now convert the full
  pilot manifest, result CSV, summary CSV, design counts, CRN declaration,
  graph scope, input dependencies, checksums, and formal acceptance absence
  into review rows. The generated
  `data/manifests/experiment_package_review_packet.csv`,
  `data/manifests/experiment_package_review_manifest.json`, and
  `docs/experiment_package_review_packet.md` are reviewer aids only and do not
  accept the experiment package.
- `src/realworld/provenance_acceptance.py` and
  `docs/provenance_acceptance_schema.md` define the explicit review record
  required before the data-provenance gate can close. The actual
  `data/manifests/provenance_acceptance.json` file is intentionally absent in
  the current scaffold.
- `src/realworld/manuscript_acceptance.py` and
  `docs/manuscript_acceptance_schema.md` define the explicit review record
  required before the manuscript/report-alignment gate can close. The actual
  `data/manifests/manuscript_acceptance.json` file is intentionally absent in
  the current scaffold.
- `src/realworld/claim_alignment_review_packet.py` and
  `scripts/write_claim_alignment_review_packet.py` now convert the paper
  draft, Korean report source, and figure/table manifest into guarded-claim
  and overclaim-candidate review rows. The generated
  `data/manifests/claim_alignment_review_packet.csv`,
  `data/manifests/claim_alignment_review_manifest.json`, and
  `docs/claim_alignment_review_packet.md` are reviewer aids only and do not
  accept manuscript/report claims.
- `src/realworld/reproducibility_acceptance.py` and
  `docs/reproducibility_acceptance_schema.md` define the explicit review record
  required before the reproducibility gate can close. The actual
  `data/manifests/reproducibility_acceptance.json` file is intentionally
  absent in the current scaffold.
- `src/realworld/final_audit_acceptance.py` and
  `docs/final_audit_acceptance_schema.md` define the explicit review record
  required before the final-audit gate can close. The actual
  `data/manifests/final_audit_acceptance.json` file is intentionally absent in
  the current scaffold.
- `data/cache/pilot_region_road.graphml` and
  `data/cache/pilot_region_road_manifest.json` provide an offline GraphML
  cache. The current manifest records `live_overpass_osm_snapshot`
  provenance, 13,268 raw source nodes, and 28,947 raw source edges. The current
  adapter filters that raw cache to a bus-practical simulator graph with 4,608
  nodes and 9,148 edges before snapping zone connectors. This is a stronger
  real-world input than the original compact fixture, but it still needs human
  source review, parameter evidence, rail evidence, benchmark checks, and
  uncertainty analysis before publication-grade claims.
- `src/realworld/road_evidence_diagnostics.py` and
  `scripts/audit_road_evidence_diagnostics.py` now summarize cached OSM road
  evidence by routeable highway class. Current diagnostics are structurally
  ready but not acceptance evidence: they prioritize residential, tertiary,
  secondary, primary, and trunk-class routeable roads for speed, capacity, and
  base-disruption evidence review.
- `src/realworld/road_speed_evidence.py` and
  `scripts/write_road_speed_evidence.py` now summarize sparse cached OSM
  `maxspeed` tags by routeable road class. The generated
  `data/parameters/road_speed_evidence_candidates.csv` has 10 routeable
  road-class rows and 5 rows with observed tags. It is a speed-review aid only,
  not reviewed speed calibration or accepted override evidence.
- `src/realworld/road_capacity_evidence.py` and
  `scripts/write_road_capacity_evidence.py` now summarize cached OSM `lanes`
  tags by routeable road class. The generated
  `data/parameters/road_capacity_evidence_candidates.csv` has 10 routeable
  road-class rows and 0 rows with parseable lane tags, making the remaining
  capacity evidence gap explicit.
- `src/realworld/road_evidence_review_packet.py` and
  `scripts/write_road_evidence_review_packet.py` now consolidate road-class
  diagnostics, sparse speed evidence, lane-count evidence, and draft override
  rows into a 10-row review worksheet. All current rows remain weak for
  final-study road claims, so this is review support only.
- `src/realworld/road_evidence_request_packet.py` and
  `scripts/write_road_evidence_source_request_packet.py` now write a 5-row
  source-request worksheet naming the speed, capacity, benchmark, disruption,
  and override-application inputs required before reviewed road-class
  overrides can be built and applied.
- `src/realworld/road_source_readiness_packet.py` and
  `scripts/write_road_source_readiness_packet.py` now classify those 5 road
  source requests into concrete readiness states. The current packet has 2
  blocking rows, for missing capacity evidence and missing reviewed
  `road_class_overrides.csv`, and 3 human-review rows for sparse speed
  candidates, benchmark strategy, and scenario-only disruption treatment.
  It remains readiness evidence only and cannot approve road inputs.
- `src/realworld/road_override_template.py` and
  `scripts/write_road_class_override_template.py` can create a draft
  non-acceptance road-class override template from those diagnostics. The draft
  uses current mapper defaults and `expert assumption` source class by design,
  so reviewers must replace values and sources before final road-evidence
  claims.
- `data/parameters/road_class_overrides_draft.csv` has now been generated as
  that reviewer worksheet. It contains 10 routeable road-class rows and all
  rows are still `expert assumption`, so it does not close road evidence or
  publication-readiness gates.
- `scripts/build_pilot_cache.py` preserves the existing cache by default, can
  rebuild the offline fixture with `--source fixture`, and can optionally
  perform manual Overpass extraction with `--source overpass`. Do not make live
  Overpass extraction part of default tests; default tests should load the
  committed or otherwise managed cached GraphML.
- `scripts/run_pilot_smoke.py` runs both `bus_only` and `multimodal` on the
  cached pilot graph.
- `scripts/run_full_graph_smoke.py` runs a tiny bus-only and baseline
  multimodal smoke on the full 4,608-node / 9,148-edge bus-practical graph
  without corridor reduction. This is full-graph feasibility evidence only.
- `src/realworld/graph_scale_diagnostics.py` and
  `scripts/run_graph_scale_diagnostics.py` compare the current canonical road
  legs `A -> D`, `A -> S`, and `R -> D` on the full bus-practical graph and
  reduced analysis corridor. Current diagnostic output has 3 pass rows for
  baseline shortest-time path preservation.
- The same graph-scale diagnostic run also compares the top 3 full-graph
  shortest-time route candidates for each canonical leg against the reduced
  corridor. Current alternate-route output has 9 rows: 3 rank-1 pass rows and
  6 alternate-route warning rows. This makes corridor-abstraction uncertainty
  visible, but it is not graph-scale acceptance and does not review traffic
  assignment, spillback, hazard exposure, or operational detours.
- A candidate multi-corridor graph preserving those top 3 route candidates has
  also been generated for graph-scale review. It has 164 nodes and 246 edges,
  and the current diagnostic has 9 pass rows. This is an upgrade path only;
  experiments and figures must be regenerated and accepted before result
  claims can use it.
- `src/realworld/graph_scale_review.py` and
  `scripts/write_graph_scale_review_packet.py` now consolidate the reduced
  corridor, 164-node / 246-edge small multi-corridor candidate, 164-node /
  246-edge full-profile multi-corridor candidate, and full bus-practical graph
  into a 4-row graph-scale method review packet. This is a worksheet for
  deciding the final graph-scale method, not acceptance evidence.
- `src/realworld/graph_scale_strategy_readiness_packet.py` and
  `scripts/write_graph_scale_strategy_readiness_packet.py` convert that
  4-option worksheet and the current-vs-candidate result-delta manifest into
  a 5-row pre-review readiness packet under
  `data/validation/graph_scale_strategy_readiness_packet.csv`. It separates
  current reduced-corridor alternate-route warnings, incomplete small
  multi-corridor output, full-profile candidate result deltas, missing
  full-graph experiment output, and the missing graph-scale acceptance record
  without choosing or approving a graph-scale method.
- `src/realworld/graph_scale_result_comparison.py` and
  `scripts/write_graph_scale_result_comparison.py` now compare the current
  full-pilot summary with the full-profile multi-corridor candidate summary.
  The generated 819-row delta table is graph-scale review evidence only, not
  graph-scale acceptance.
- `src/realworld/route_road_evidence_exposure.py` and
  `scripts/write_route_road_evidence_exposure.py` now link weak road speed,
  capacity, disruption, and connector assumptions to the canonical route
  candidates used in graph-scale review. The generated 76-row table is
  route-level road-evidence review support only, not calibration or validation
  acceptance.
- `tests/test_realworld_pilot_smoke.py` verifies the offline pilot path.
- `data/parameters/` contains first parameter-source, rail-assumption, and
  fleet-assumption tables with validators in `src/realworld/parameters.py`.
- `src/realworld/parameter_review_packet.py` and
  `scripts/write_parameter_review_packet.py` now convert the core-parameter
  audit into `data/parameters/parameter_evidence_review_packet.csv` and
  `data/parameters/parameter_evidence_review_manifest.json`. The generated
  packet has 29 core-parameter rows, marks 25 rows as weak for final-study
  claims, and remains review support only.
- `src/realworld/parameter_evidence_request_packet.py` and
  `scripts/write_parameter_evidence_source_request_packet.py` now write a
  6-row source-request worksheet for cross-cutting demand, fleet, dispatch,
  transfer, disruption, and traffic/BPR evidence collection. The generated
  packet covers 22 parameters, keeps `publication_ready: false`, and does not
  close the parameter-evidence or weak-parameter acceptance gates.
- `src/realworld/parameter_source_readiness_packet.py` and
  `scripts/write_parameter_source_readiness_packet.py` now classify those 6
  parameter source requests into concrete readiness states. The current packet
  covers 20 weak parameters, separates human-review rows from blocker rows,
  keeps `publication_ready: false`, and cannot approve weak assumptions or
  final parameter claims.
- `src/realworld/parameter_acceptance.py` and
  `docs/parameter_acceptance_schema.md` define the optional reviewer record
  needed when weak expert/sensitivity-only parameters are retained inside the
  final claim boundary. The actual `data/parameters/parameter_acceptance.csv`
  file is intentionally absent in the current scaffold.
- `data/parameters/rail_service_evidence.csv` and
  `src/realworld/rail_evidence.py` record the current rail timing values as
  an offline assumption proxy, keep rail capacity explicitly sensitivity-only,
  and distinguish them from future cached timetable/GTFS-derived timing
  evidence.
- `src/realworld/rail_evidence_review_packet.py` and
  `scripts/write_rail_evidence_review_packet.py` now consolidate station
  binding, rail timing, capacity, service-window, availability, and derivation
  path status into a 10-row review worksheet. Station binding is ready, but
  rail service timing remains weak until cached timetable, GTFS, shortest-path,
  or equivalent evidence is reviewed.
- `src/realworld/rail_timing_request_packet.py` and
  `scripts/write_rail_timing_source_request_packet.py` now write a 5-row
  source-request worksheet naming the API-key, GTFS, capacity, and availability
  inputs required before cached rail timing evidence can be derived.
- `src/realworld/rail_fetch_readiness_packet.py` and
  `scripts/write_rail_fetch_readiness_packet.py` now classify those 5 rail
  timing requests into concrete readiness states. The current packet has 3
  blocking rows, for missing `DATA_GO_KR_KEY` or reviewed GTFS input, and 2
  human-review rows for rail capacity and availability treatment. It remains
  readiness evidence only and cannot approve rail service evidence.
- `data/rail/pilot_station_binding_cache.csv`,
  `data/parameters/rail_station_bindings.csv`, and
  `src/realworld/rail_station_binding.py` now bind `S` and `R` to official
  line-specific station identifiers from a cached Seoul Open Data Plaza
  station-name search extract. `scripts/audit_rail_station_bindings.py`
  reports `binding_ready: true`, but this is station binding only and not rail
  service evidence.
- `src/realworld/rail_station_cache.py`,
  `scripts/derive_rail_station_bindings.py`, and
  `docs/rail_station_cache_schema.md` provide the offline derivation path for
  regenerating binding-ready rows from a reviewed official station extract.
- `src/realworld/rail_timetable.py`,
  `scripts/derive_rail_service_evidence.py`, and
  `docs/rail_timetable_cache_schema.md` provide the offline derivation path for
  reviewed station-event timetable extracts. Derived rows can support headway
  and matched trip travel time when station codes match official bindings and
  source artifact SHA256 values are preserved.
- `scripts/derive_rail_headway_evidence.py` can derive headway-only evidence
  from reviewed access-station timetable rows. This supports a more realistic
  mixed-evidence path where timetable records support headway and separate
  shortest-path, GTFS, or timetable records support station-to-station travel
  time.
- `src/realworld/rail_gtfs.py`,
  `scripts/derive_rail_gtfs_evidence.py`, and
  `docs/rail_gtfs_cache_schema.md` provide the offline derivation path for a
  reviewed static GTFS zip or directory. Derived rows can support scheduled
  headway and access-to-egress travel time while preserving source artifact
  SHA256. No reviewed GTFS feed is committed for the current pilot, so this is
  a readiness path rather than final evidence.
- `src/realworld/rail_timetable_api.py` and
  `scripts/fetch_rail_timetable_cache.py` provide an optional key-required
  data.go.kr train-schedule fetch path for creating the local timetable cache.
  This helper is excluded from default offline validation and does not upgrade
  rail evidence unless the cache and raw response are reviewed.
- `src/realworld/rail_shortest_path.py`,
  `scripts/derive_rail_shortest_path_evidence.py`, and
  `docs/rail_shortest_path_cache_schema.md` provide the offline derivation path
  for reviewed station-to-station shortest-path extracts. Derived rows support
  travel-time evidence only; headway and capacity still require separate
  evidence or sensitivity-only treatment.
- `src/realworld/rail_shortest_path_api.py` and
  `scripts/fetch_rail_shortest_path_cache.py` provide an optional key-required
  data.go.kr fetch path for creating the local shortest-path cache from a
  reviewed live request. This helper is excluded from default offline
  validation and does not upgrade rail evidence unless the cache and raw
  response are reviewed.
- `data/validation/` contains first offline route plausibility sanity outputs
  with helpers in `src/realworld/plausibility.py`.
- `src/realworld/accessibility.py` and
  `scripts/run_accessibility_loss_analysis.py` now provide a route-level
  critical-edge/accessibility-loss diagnostic for `A -> D`, `A -> S`, and
  `R -> D`. The current scaffold output has 127 edge-removal rows and 22
  disconnected edge-removal cases. This is a route-fragility diagnostic, not
  calibrated outage probability or operational accessibility evidence.
- `data/validation/external_route_benchmarks_osrm.csv` contains an optional
  OSRM public route API snapshot. After bus-practical route filtering, the
  current optional OSRM comparison has 3 pass rows and no warn/fail rows. The
  offline deterministic fallback benchmark still has one warning on `A -> S`,
  so route realism remains plausibility evidence rather than calibration.
- `src/realworld/osrm_snapshot_manifest.py` and
  `scripts/write_osrm_snapshot_manifest.py` now write
  `data/validation/osrm_route_benchmark_manifest.json`, recording OSRM CSV and
  summary checksums, query URLs, source/status counts, 3 live/unpinned rows,
  and a non-acceptance claim boundary.
- `data/scenarios/` contains deterministic structured disruption and policy
  alternative tables with helpers in `src/realworld/disruption_scenarios.py`
  and `src/realworld/policy_alternatives.py`.
- `scripts/run_pilot_experiments.py --sample` writes separated pilot scaffold
  sample outputs under `results/realworld_pilot/`. The sample runner now uses
  a route-corridor analysis subgraph for fast execution on the larger cached
  OSM snapshot; current sample/full outputs use 118 analysis nodes and 174
  analysis edges derived from the 4,608-node / 9,148-edge bus-practical
  simulator graph.
- `scripts/run_pilot_experiments.py --staged` and `--full` write separated
  staged/full outputs. Current full output has 1,890 rows and 63 summary rows
  over 7 policies, 9 scenarios, and 30 seeds, while still using the reduced
  route-corridor analysis graph with source-vs-analysis graph scale recorded.
- `scripts/run_pilot_experiments.py --multi-corridor` writes a separated
  candidate profile on the 164-node / 246-edge multi-corridor analysis graph.
  Current output has 32 rows and 16 summary rows; it is graph-scale review
  evidence only and does not replace the accepted staged/full run design.
- `scripts/run_pilot_experiments.py --multi-corridor-full` writes a separated
  full-profile candidate on the same 164-node / 246-edge multi-corridor
  analysis graph. Current output has 1,890 rows and 63 summary rows over the
  same 7 policies, 9 scenarios, and 30 seeds as the current full pilot; it is
  graph-scale review evidence only and does not accept the candidate graph.
- `src/realworld/experiment_acceptance.py` keeps those staged/full outputs
  blocked from final-study claims until graph scope, input validation,
  scenario-policy-seed design, common-random-number pairing, output counts, and
  the not-operational claim boundary are reviewed together.
- `src/realworld/experiment_package_review_packet.py` makes that blocker
  auditable by checking current full output counts, checksums, design counts,
  graph/input dependencies, and formal acceptance absence without approving the
  run package.
- `scripts/run_sensitivity.py --sample` writes deterministic one-at-a-time
  sensitivity screening outputs and a SALib-compatible manifest.
- `scripts/run_sensitivity.py --method morris --all` writes current SALib
  Morris scaffold outputs over the 8-policy, 9-scenario sensitivity design,
  with 4,320 rows and 7,056 summary rows. These are formal scaffold indices,
  not calibrated real-world sensitivity evidence.
- `scripts/audit_sensitivity_diagnostics.py` reviews Morris summary/manifest
  consistency, blank or non-finite index values, zero `mu_star` rows, reduced
  graph scope, and scaffold claim boundaries without accepting the outputs for
  final-study claims.
- `src/realworld/sensitivity_review_packet.py` and
  `scripts/write_sensitivity_review_packet.py` convert those Morris
  diagnostics into a 6-row reviewer worksheet under
  `data/validation/sensitivity_review_packet.csv`. The packet summarizes
  structural readiness, missing/non-finite indices, zero `mu_star` rows,
  reduced graph scope, result scope, and the Morris-vs-Sobol decision. It keeps
  `publication_ready: false`, does not create
  `data/manifests/sensitivity_acceptance.json`, and does not close the
  sensitivity gate.
- `src/realworld/validation_review_packet.py` and
  `scripts/write_validation_review_packet.py` convert the current validation
  artifacts into a 7-row reviewer worksheet under
  `data/validation/validation_review_packet.csv`. The packet summarizes
  internal route plausibility, fallback benchmark warnings, optional OSRM
  snapshot/manifest status, accessibility-loss coverage, route-level
  road-evidence exposure, validation-summary scope, and the benchmark-strategy
  decision. It keeps `publication_ready: false`, does
  not create `data/manifests/validation_acceptance.json`, and does not close
  the validation gate.
- `src/realworld/validation_strategy_readiness_packet.py` and
  `scripts/write_validation_strategy_readiness_packet.py` convert the 7-row
  validation worksheet into concrete pre-review readiness statuses under
  `data/validation/validation_strategy_readiness_packet.csv`. It separates
  internal warnings, fallback benchmark warnings, unpinned OSRM snapshot risk,
  accessibility diagnostics, weak route-road evidence exposure,
  validation-summary scope, and the missing validation acceptance record
  without choosing or approving a benchmark strategy.
- `scripts/make_pilot_statistics.py` writes full-pilot uncertainty summaries
  from seed replications: 819 metric confidence-interval rows and 702 paired
  policy-delta confidence-interval rows. These support experiment review but do
  not close calibration or final-study acceptance gates.
- The same statistics CLI also runs on the multi-corridor candidate output,
  producing 208 metric confidence-interval rows and 156 paired policy-delta
  rows for graph-scale review of the 164-node / 246-edge candidate graph.
- The same statistics CLI also runs on the full-profile multi-corridor
  candidate output, producing 819 metric confidence-interval rows and 702
  paired policy-delta rows for graph-scale review of the same candidate graph.
- `scripts/make_pilot_figures.py` writes scaffold-only figures, result tables,
  bottleneck attribution proxy, policy regime-map tables/figures, and
  claim-boundary artifacts from the current full pilot and Morris CSVs.
- `scripts/audit_plan_artifacts.py` checks expected scaffold artifact row
  counts, JSON manifests, docs, and the current non-calibrated claim boundary.
- `scripts/write_goal_completion_audit.py` writes a non-acceptance
  prompt-to-artifact checklist for the active `plan.md` objective.
- `scripts/audit_publication_readiness.py` aggregates parameter, road, rail
  service, and station-binding evidence gates. It reports
  `publication_ready: false` for the current scaffold and can be run with
  `--fail-on-blockers` when a strict final audit is desired.
- `scripts/audit_final_study_readiness.py` maps every Final Definition of Done
  gate in this plan to concrete artifacts. It reports
  `final_study_ready: false` until pilot acceptance, graph-scale, evidence,
  validation, experiment, sensitivity, manuscript/report, reproducibility, and
  final-audit gates are all closed.
- `scripts/audit_road_overrides.py` reports that no reviewed default
  road-class override table is currently present and no accepted pilot
  manifest applies one, so built-in road speed, capacity, and base-disruption
  proxies remain final-claim blockers.
- `docs/road_class_override_schema.md` defines the reviewed override table
  shape and explicitly warns that example values are not evidence.
- `docs/reproducibility_package.md` and
  `data/manifests/reproducibility_manifest.json` record the current
  scaffold-only reproduction package.
- `src/realworld/reproducibility_review_packet.py` and
  `scripts/write_reproducibility_review_packet.py` turn clean-checkout
  reproducibility into a 7-row review packet covering scaffold manifest scope,
  formal acceptance-record absence, Git worktree state, untracked artifact
  risk, validation command ladder, runtime `cloned_repo` import boundary, and
  clean-checkout execution scope. It is review support only and does not
  create `data/manifests/reproducibility_acceptance.json`.
- `src/realworld/reproducibility_smoke.py` and
  `scripts/run_reproducibility_smoke.py` run a bounded current-worktree smoke
  ladder. The current manifest records 22 passing commands and
  `smoke_passed: true`, but it explicitly keeps
  `clean_checkout_test_performed: false`, `can_mark_complete: false`, and
  final-study readiness blocked.
- `src/realworld/agent_review_path_audit.py` and
  `scripts/audit_agent_review_paths.py` check that sub-agent review records
  cite existing local evidence/review inputs or explicit missing formal
  acceptance targets. The current audit has no missing non-formal paths and
  still keeps `can_mark_complete: false`.
- `src/realworld/tracked_artifact_audit.py` and
  `scripts/audit_tracked_artifacts.py` list changed reproducibility artifacts
  that a clean checkout of the current Git HEAD would not reproduce unless
  they are committed, packaged, or explicitly excluded from the accepted
  reproduction scope. The current audit is packaging hygiene only and keeps
  `clean_checkout_reproducibility_ready: false`.
- `src/realworld/provenance_acceptance.py` keeps the data-provenance gate
  blocked until source snapshots, license/attribution, privacy abstraction,
  cache manifests, reproduction paths, and the not-operational claim boundary
  are reviewed together.
- `data/manifests/source_provenance_manifest.json` and
  `scripts/audit_source_provenance.py` now provide a non-acceptance source
  provenance review packet for source URLs, license/terms notes,
  snapshot/access dates, local artifacts, review statuses, and claim
  boundaries. This supports provenance review but does not replace
  `data/manifests/provenance_acceptance.json`.
- `src/realworld/source_license_review_packet.py` and
  `scripts/write_source_license_review_packet.py` now turn the source
  provenance manifest into one row per source for license, attribution,
  snapshot, privacy, and reproducibility review. The generated
  `data/manifests/source_license_review_packet.csv`,
  `data/manifests/source_license_review_manifest.json`, and
  `docs/source_license_review_packet.md` are reviewer aids only; they do not
  certify license compatibility or close the data-provenance gate.
- `src/realworld/source_url_review_packet.py` and
  `scripts/write_source_url_review_packet.py` now turn the source provenance
  manifest into URL-level review rows. The generated
  `data/manifests/source_url_review_packet.csv`,
  `data/manifests/source_url_review_manifest.json`, and
  `docs/source_url_review_packet.md` identify every HTTP(S) source reference
  that a reviewer must inspect. The default command is offline parse-only;
  optional `--live` reachability checks remain volatile review aids and do not
  certify licenses, source suitability, or provenance acceptance.
- `src/realworld/manuscript_acceptance.py` keeps the manuscript/report gate
  blocked until paper/report text, regenerated docx, figures/tables, evidence
  gates, result claims, and the not-operational claim boundary are reviewed
  together.
- `src/realworld/claim_alignment_review_packet.py` keeps that manuscript
  blocker actionable by listing claim-bearing lines and figure/table boundary
  rows that require revision or formal review before acceptance.
- `src/realworld/reproducibility_acceptance.py` keeps the reproducibility gate
  blocked until clean-checkout validation, validation ladder, artifact
  regeneration, manifest paths, runtime import boundaries, validation command
  counts, and the not-operational claim boundary are reviewed together.
- `src/realworld/final_audit_acceptance.py` keeps the final-audit gate blocked
  until an independent prompt-to-artifact audit verifies every pre-final gate,
  rejects proxy-only completion evidence, matches current gate lists/counts,
  and accepts the not-operational claim boundary.
- `docs/plan_completion_audit.md` records the current plan-gate audit. It
  confirms that the executable quasi-real scaffold is in place while calibrated
  final-study claims remain blocked by pilot acceptance, stronger evidence, and
  final manuscript/report review.
- `docs/current_goal_completion_audit.md` restates the active goal as concrete
  gates, lists named acceptance artifacts, rejects proxy-only completion
  signals, and remains separate from the future `docs/final_study_audit.md`.
- `docs/analysis_corridor_method_note.md` records that the current 118-node /
  174-edge analysis corridor is a scaffold/performance abstraction. The final
  study must choose accepted corridor abstraction, full-graph runtime, or a
  multi-corridor ensemble before making final graph-scale claims.
- `docs/graph_scale_diagnostics.md` records the current route-parity,
  alternate-route, and multi-corridor candidate diagnostics and keeps them
  separate from
  `data/manifests/graph_scale_acceptance.json`, which remains absent until
  reviewed.
- `docs/graph_scale_review_packet.md` records the 4-option method review
  worksheet. Use it to support the final source-vs-analysis graph decision,
  but do not treat it as graph-scale acceptance.
- `docs/graph_scale_result_comparison.md` records the current-vs-candidate
  result-delta table. Use it to review graph-choice impact, but do not treat
  it as graph-scale acceptance.

Known validation that should remain green:

```powershell
.\.venv\Scripts\python -m compileall main.py src tests scripts generate_report.py
Get-ChildItem tests\test_*.py | ForEach-Object { .\.venv\Scripts\python $_.FullName }
.\.venv\Scripts\python scripts\run_pilot_smoke.py
.\.venv\Scripts\python scripts\run_full_graph_smoke.py
.\.venv\Scripts\python scripts\run_graph_scale_diagnostics.py
.\.venv\Scripts\python scripts\write_graph_scale_review_packet.py
.\.venv\Scripts\python scripts\write_graph_scale_strategy_readiness_packet.py
.\.venv\Scripts\python tests\test_realworld_graph_scale_diagnostics.py
.\.venv\Scripts\python tests\test_realworld_graph_scale_review.py
.\.venv\Scripts\python tests\test_realworld_graph_scale_strategy_readiness_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_gtfs.py
.\.venv\Scripts\python tests\test_realworld_rail_shortest_path_api.py
.\.venv\Scripts\python tests\test_realworld_rail_timetable_api.py
.\.venv\Scripts\python scripts\audit_rail_evidence.py
.\.venv\Scripts\python scripts\write_rail_evidence_review_packet.py
.\.venv\Scripts\python scripts\write_rail_timing_source_request_packet.py
.\.venv\Scripts\python scripts\write_rail_fetch_readiness_packet.py
.\.venv\Scripts\python scripts\audit_rail_station_bindings.py
.\.venv\Scripts\python scripts\audit_parameter_evidence.py
.\.venv\Scripts\python scripts\write_parameter_review_packet.py
.\.venv\Scripts\python scripts\write_parameter_evidence_source_request_packet.py
.\.venv\Scripts\python scripts\write_parameter_source_readiness_packet.py
.\.venv\Scripts\python scripts\audit_road_evidence.py
.\.venv\Scripts\python scripts\audit_road_evidence_diagnostics.py
.\.venv\Scripts\python scripts\write_road_capacity_evidence.py
.\.venv\Scripts\python scripts\write_road_speed_evidence.py
.\.venv\Scripts\python scripts\write_road_evidence_review_packet.py
.\.venv\Scripts\python scripts\write_road_evidence_source_request_packet.py
.\.venv\Scripts\python scripts\write_road_source_readiness_packet.py
.\.venv\Scripts\python scripts\write_road_class_override_template.py --output data\parameters\road_class_overrides_draft.csv --overwrite
.\.venv\Scripts\python tests\test_realworld_road_override_template.py
.\.venv\Scripts\python scripts\audit_source_provenance.py
.\.venv\Scripts\python tests\test_realworld_source_url_review_packet.py
.\.venv\Scripts\python scripts\write_source_url_review_packet.py
.\.venv\Scripts\python tests\test_realworld_formal_acceptance_evidence_matrix.py
.\.venv\Scripts\python scripts\write_formal_acceptance_evidence_matrix.py
.\.venv\Scripts\python scripts\audit_publication_readiness.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
.\.venv\Scripts\python scripts\run_pilot_experiments.py --sample
.\.venv\Scripts\python scripts\run_pilot_experiments.py --multi-corridor
.\.venv\Scripts\python scripts\run_pilot_experiments.py --multi-corridor-full
rg -n "(^|\s)(from|import)\s+cloned_repo" src tests scripts
git diff --check
```

The current generated CSV/PNG/report results are still representative-network
results. The cached pilot GraphML is now OSM-derived, and the smoke/sample
pipeline proves executable quasi-real input compatibility, but the pilot sample
outputs, sensitivity screening outputs, and figures/tables are still scaffold
evidence. They are not calibrated real-world results and should not be used as
final publication findings.

## Gap Review And Completion Roadmap

The plan contains the full final-goal scope, but the project is still between
the executable scaffold and final quasi-real study stages. Use the phase gates
below to prevent accidental overclaiming.

| Phase | Goal | Exit Evidence | Main Owner | Subagent Support |
| --- | --- | --- | --- | --- |
| P0 baseline integrity | Keep the existing abstract simulator and real-world MVP stable | compile, unit tests, pilot smoke, no runtime imports from `cloned_repo/` | main integrator | only narrow bug-fix workers |
| P1 accepted pilot input | Freeze the non-sensitive pilot region, cached OSM snapshot, graph scale strategy, and data card | reviewed cache manifest, region spec, source/analysis graph counts, privacy notes | main integrator | E1 OSM provenance and scale |
| P2 evidence tables | Make road, rail, fleet, transfer, disruption, and demand assumptions traceable | parameter-source tables, parameter evidence audit, rail evidence, assumption classes, uncertainty ranges | main integrator | E2 rail evidence and parameter workers |
| P3 validation package | Separate internal invariants, map plausibility, fallback benchmarks, and external-router benchmarks | validation CSVs, benchmark summary, failure/warning interpretation | main integrator | E3 external benchmark |
| P4 full pilot experiments | Replace sample outputs with accepted scenario-policy-seed outputs | full or staged run manifest, paired comparisons, uncertainty summaries | main integrator | E5 full pilot experiment design |
| P5 sensitivity and regimes | Identify which uncertain parameters drive strategy choice | SALib Morris/Sobol outputs, regime tables, sensitivity figures | main integrator | E4 formal sensitivity |
| P6 manuscript/report package | Align English paper, Korean report, figures, tables, and limitations with current evidence | generated paper/report artifacts, claim-boundary table, figure captions | main integrator | E6 and E7 workers |
| P7 final audit | Confirm that no final gate is skipped | GPT-5.5 xhigh audit note and green validation ladder | main integrator | E8 final audit |

Final-study readiness requires all phases P0 through P7. If a phase remains
incomplete, paper/report language must stay at scaffold, quasi-real pilot, or
assumption-supported decision-support level as appropriate.

## Final Definition Of Done

The final version is complete only when all gates below are satisfied.

| Gate | Required Evidence |
| --- | --- |
| Pilot region accepted | A non-sensitive pilot region is selected, documented, and reproducible from a region spec. |
| Cached OSM input | Road graph is extracted or loaded from a committed/managed cache path with metadata, road-input evidence audit, road-class diagnostics, a consolidated road-input review packet, and no live OSM dependency in tests. |
| Real input smoke | The cached pilot graph converts through `src.realworld` and runs both `bus_only` and `multimodal` scenarios. |
| Graph-scale strategy | The study states whether it uses the full cached graph, a justified analysis corridor, a 164-node / 246-edge multi-corridor candidate graph, or a multi-corridor ensemble; route-parity, alternate-route, multi-corridor diagnostics, the full-profile multi-corridor candidate output, the current-vs-candidate result-delta comparison, and the 4-option graph-scale review packet are reviewed; result manifests record both source and analysis graph scale; and `data/manifests/graph_scale_acceptance.json` records the reviewed graph-scale decision within a not-operational claim boundary. |
| Data provenance | Every data file, snapshot date, source, license/attribution note, and assumption category is recorded, and `data/manifests/provenance_acceptance.json` records reviewed source snapshot, license/attribution, privacy abstraction, cache manifest, reproduction path, and not-operational claim-boundary acceptance. |
| Parameter evidence | Every important parameter has a source class, the parameter evidence audit reports no missing core parameters, and any weak expert/sensitivity-only values are either replaced through evidence tables or explicitly accepted within the final claim boundary. |
| Rail evidence | Rail access and egress are bound to official station identifiers; review packets keep rail timing gaps visible; travel time, headway, and capacity are GTFS-derived, cached timetable-derived, shortest-path-derived, or explicitly documented assumptions; any derived row must preserve source artifact path and digest. |
| Validation package | Internal, external plausibility, and benchmark validation checks are implemented and summarized, and `data/manifests/validation_acceptance.json` records the reviewed benchmark strategy, not-ground-truth limitation, and not-operational claim boundary. |
| Structured disruptions | Random, critical-link, access/last-mile, and spatial/hazard-overlay disruption families are implemented or explicitly scenario-defined. |
| Policy alternatives | At least bus-only, baseline multimodal, multimodal with last-mile redundancy, and staggered/adaptive dispatch are compared. |
| Sensitivity analysis | SALib Morris or Sobol analysis identifies parameters that determine winning regimes, and `data/manifests/sensitivity_acceptance.json` records the reviewed method, graph scope, parameter ranges, NaN/masked-value handling, Sobol decision, and not-operational claim boundary. |
| Full experiment output | Pilot-region experiment outputs, result metadata, confidence intervals or equivalent uncertainty summaries, and figures/tables are regenerated, and `data/manifests/experiment_acceptance.json` records reviewed graph scope, input validation, scenario-policy-seed design, CRN pairing, output counts, and the not-operational claim boundary. |
| Manuscript/report alignment | `paper/`, Korean report source, README/agents/status/docs all reflect the real-world or quasi-real pilot results without overclaiming, and `data/manifests/manuscript_acceptance.json` records reviewed paper/report, regenerated docx, figure/table, evidence-gate, result-claim, and not-operational claim-boundary acceptance. |
| Reproducibility | A clean checkout can rebuild the pilot inputs from cache, run smoke tests, run experiments, regenerate tables/figures, run publication-readiness audit gates, and `data/manifests/reproducibility_acceptance.json` records reviewed clean-checkout validation, artifact-regeneration, manifest-path, import-boundary, command-count, and not-operational claim-boundary acceptance. |

## Coverage Checklist Against The Final Goal

This section maps the full project goal to the workstreams that must satisfy it.
If a row is incomplete, the project is not final.

| Final Goal Element | Covered By | Completion Evidence |
| --- | --- | --- |
| Real-world or quasi-real road network | Workstreams 1, 2, 3 | accepted pilot region spec, cached GraphML, offline graph load smoke |
| Reusable across regions, not only one case | Workstreams 1, 3, 13 | region-parameterized inputs, no hard-coded pilot-only logic, manifest format |
| Non-sensitive location handling | Workstreams 1, 13 | data card marks public, synthetic, aggregated, or assumption-based coordinates |
| Current simulator preserved | Workstreams 3, 10 | existing abstract tests pass and `run_scenario(...)` call surface remains stable |
| Realistic road attributes | Workstreams 4, 6 | parameter-source table, validation summary, benchmark/plausibility checks |
| Large cached graph remains executable | Workstreams 2, 3, 10 | source graph loads offline, analysis graph or full-network runner completes sample/full experiments |
| Rail-bus realism | Workstreams 5, 8 | GTFS/timetable evidence or documented rail-assumption table |
| Structured disruption realism | Workstream 7 | disruption scenario table with random, critical-link, access/last-mile, and spatial families |
| Decision-relevant strategy comparison | Workstreams 8, 10 | bus-only, baseline multimodal, redundancy, and staggered/adaptive policies |
| Critical-link, accessibility-loss, and route evidence exposure diagnostics | Workstreams 6, 7, 11 | `data/validation/accessibility_loss.csv`, `data/validation/accessibility_loss_summary.md`, `data/validation/canonical_route_road_evidence_exposure.csv`, and claim-boundary docs |
| Uncertainty and sensitivity | Workstream 9 | SALib Morris or Sobol outputs with parameter ranking |
| SCI/SCIE-style evidence structure | Workstreams 4, 6, 9, 10, 11, 12 | source tables, validation tables, sensitivity results, current figures/tables |
| Korean report and English paper alignment | Workstream 12 | `paper/`, `report_draft.md`, generated figures, and `report.docx` reflect current outputs |
| Reproducibility package | Workstream 13 | input, scenario, seed, result, and data snapshot manifests |
| GPT-5.5 xhigh parallel execution | Subagent Execution Plan | wave-specific worker cards, ownership, validation, and integration gates |
| Final audit discipline | Subagent Execution Plan, Final Validation Ladder | independent audit confirms no gate is silently skipped, and `data/manifests/final_audit_acceptance.json` records reviewed prompt-to-artifact completion, gate evidence, no-proxy completion, gate-list/count, and not-operational claim-boundary acceptance |

## Final Architecture

Target data flow:

```text
pilot region decision
-> RegionSpec YAML/JSON
-> OSMnx live extraction or cached GraphML
-> normalized OSM-like graph
-> road attribute mapping and calibration overlays
-> zone and rail-point connectors
-> simulator-compatible DiGraph
-> rail/timetable input table
-> OD demand and fleet parameter table
-> disruption scenario table
-> bus-only and policy alternatives
-> paired simulation runs
-> validation, sensitivity, figures, paper/report
```

Recommended project artifacts:

```text
data/
  regions/
    pilot_region.yaml
  cache/
    pilot_region_road.graphml
  parameters/
    parameter_sources.csv
    parameter_evidence_review_packet.csv
    parameter_evidence_review_manifest.json
    rail_assumptions.csv
    fleet_assumptions.csv
  scenarios/
    disruption_scenarios.csv
    policy_alternatives.csv
  validation/
    route_plausibility.csv
    validation_summary.md
results/
  realworld_pilot/
    raw_runs.csv
    paired_comparisons.csv
    sensitivity_results.csv
    figures/
docs/
  realworld_pipeline.md
  third_party_adaptations.md
  pilot_region_data_card.md
paper/
  paper_draft.md
```

Do not use exact sensitive destinations. Use public civic points, synthetic
centroids, administrative zones, or H3/admin-grid cells.

## Region Reusability Requirements

The pilot region is the first demonstration, not a one-off special case.

Rules:

- Every input artifact must carry `region_id`.
- Region-specific data must live under a region-keyed file or folder.
- Shared code must not hard-code pilot coordinates, station IDs, or policy
  values outside test fixtures.
- Scripts should accept a region spec path and cache path rather than assuming
  one fixed region.
- Future regions should be addable by creating a new region spec, cache, data
  card, parameter table entries, and scenario table rows.

Acceptance checks:

- A second synthetic region fixture can pass schema and adapter tests without
  changing production code.
- Documentation explains which files must be duplicated or edited for another
  region.
- Paper claims say "region-reusable framework" only if this parameterization is
  actually exercised or demonstrated.

## Data Governance And Security

The final package must remain publishable and non-operational.

Rules:

- Do not expose sensitive military, emergency-response, or protected facility
  destinations.
- Use public civic locations, synthetic centroids, H3/admin-grid cells, or
  aggregated zones when a location could be sensitive.
- Mark every coordinate as `public`, `synthetic`, `aggregated`, or
  `assumption`.
- Keep source URLs and licenses for public data.
- Do not include personal data, vehicle plate data, private trip records, or
  non-public operational records.
- If a source is sensitive or cannot be cited, use it only for internal
  plausibility discussion and do not make it a publication dependency.

Acceptance checks:

- `docs/pilot_region_data_card.md` includes a privacy/security section.
- The paper limitation section states that outputs support planning and
  comparative evaluation, not operational routing.
- No generated figure reveals a sensitive exact destination.

## Workstream 1: Pilot Region And Data Card

Outcome:

Choose one non-sensitive pilot region and create a data card that explains why
it is suitable for a realistic but publishable case study.

Implementation tasks:

- Select a public, non-sensitive administrative area or metropolitan subregion.
- Define a bbox or boundary polygon.
- Define primary assembly zone `A`, destination zone `D`, rail access `S`, and
  rail egress `R`.
- If exact locations are inappropriate, use synthetic centroids or
  administrative/H3 zone centroids.
- Create `data/regions/pilot_region.yaml`.
- Create `docs/pilot_region_data_card.md`.

Acceptance checks:

- `load_region_spec(...)` accepts the region file.
- All points fall inside the boundary.
- The file says which coordinates are public, synthetic, aggregated, or
  assumption-based.
- No sensitive military or emergency-operation routing target is exposed.

## Workstream 2: Cached OSM / GraphML Input

Outcome:

Create a reproducible cached road graph for the pilot region.

Current status:

- The current checked-in `data/cache/pilot_region_road.graphml` is generated
  from a live Overpass/OSM snapshot for `songpa_public_demo`.
- The manifest records the source as `live_overpass_osm_snapshot`, node/edge
  counts, attribution, and claim limits.
- The road-class diagnostic audit ranks routeable classes by review priority
  and keeps weak maxspeed, capacity, and base-disruption evidence visible.
- This satisfies the minimum executable OSM-derived cache milestone, but it is
  still a research input requiring source review, route plausibility checks,
  parameter evidence, and benchmark validation.
- Running `scripts/build_pilot_cache.py` with no flags preserves an existing
  cache. Use explicit cache-refresh instructions when the goal is to replace
  the OSM-derived snapshot.

Implementation tasks:

- Use `src.realworld.osm_network.load_or_extract_bbox_graph(...)` or an
  equivalent manual extraction step to produce a GraphML cache.
- Store the cache under `data/cache/`.
- Add metadata for extraction date, OSM data source, bbox/boundary, OSMnx
  version if available, and attribution requirements.
- Add a test or smoke command that loads the cached graph without live OSM.
- Keep live OSM calls out of default tests.

Acceptance checks:

- Cached GraphML loads offline.
- Graph has finite node `x`/`y` coordinates for snap targets.
- Graph has nonzero road nodes and edges.
- Manifest distinguishes fixture, Overpass snapshot, or other source modes.
- `normalize_osm_graph(...)` preserves required metadata.
- Unit tests still pass without OSMnx installed.

## Workstream 3: Pilot Graph Conversion And Smoke Run

Outcome:

The cached pilot road graph becomes a simulator-ready graph and reaches
`run_scenario(...)`.

Implementation tasks:

- Load `data/regions/pilot_region.yaml`.
- Load cached `data/cache/pilot_region_road.graphml`.
- Build a simulator graph with `build_simulator_graph(...)`.
- Run `assert_graph_ready(...)`.
- Merge `realworld_network_config(region)` into a minimal scenario config.
- Run deterministic smoke tests for `bus_only` and `multimodal`.
- Add a pilot smoke test that can run offline.

Acceptance checks:

- `A -> D`, `A -> S`, and `R -> D` are routeable by road-mode edges.
- Every emitted edge has `t0`, `capacity`, `p_fail`, `base_p_fail`, and `mode`.
- Connector distances are recorded and inspected for plausibility.
- Both scenario types complete on a small deterministic demand fixture.
- Existing abstract-network tests remain unchanged and green.

## Workstream 4: Parameter-Source Tables

Outcome:

Every important model parameter is explicitly sourced, classified, and
defensible.

Current status:

- First CSV tables and validation helpers exist.
- The parameter review packet exists as a 29-row prioritization worksheet with
  25 weak rows for final-study claims; it is not accepted calibration.
- The tables are currently assumption/sensitivity evidence for the pilot
  scaffold. They still need stronger public-data, GTFS/timetable, literature,
  or benchmark-calibrated entries before publication-grade claims.

Create or update:

- `data/parameters/parameter_sources.csv`
- `data/parameters/parameter_evidence_review_packet.csv`
- `data/parameters/parameter_evidence_review_manifest.json`
- `data/parameters/parameter_evidence_source_request_packet.csv`
- `data/parameters/parameter_evidence_source_request_manifest.json`
- `data/parameters/rail_assumptions.csv`
- `data/parameters/rail_station_bindings.csv`
- `data/parameters/rail_evidence_review_packet.csv`
- `data/parameters/rail_evidence_review_manifest.json`
- `data/rail/rail_timing_source_request_packet.csv`
- `data/rail/rail_timing_source_request_manifest.json`
- `data/parameters/fleet_assumptions.csv`

Required fields:

```text
parameter
value
unit
source_class
source_name
source_url_or_citation
applies_to
uncertainty_range
notes
```

Minimum required parameters:

- road free-flow speed
- road capacity proxy
- background traffic multiplier
- BPR alpha and beta
- disruption probability or exposure threshold
- capacity-reduction factor
- blockage rule
- bus capacity
- direct bus fleet size
- feeder fleet size
- last-mile fleet size
- turnaround time
- dispatch interval
- rail headway
- rail travel time
- rail capacity
- transfer fixed delay
- transfer per-passenger delay
- passenger arrival distribution
- simulation time horizon
- late-arrival penalty
- censored-passenger penalty

Acceptance checks:

- No parameter used in real-world experiments is missing from the source table.
- Values are classified as public-data-derived, literature-derived,
  agency/timetable-derived, benchmark-calibrated, expert assumption, or
  sensitivity-only.
- Assumption-only values are included in sensitivity ranges.

## Workstream 5: Rail And Transit Evidence

Outcome:

Rail is not an arbitrary fixed-headway placeholder. It is either GTFS-derived
or documented as an assumption with source context.

Implementation tasks:

- Search for a public GTFS or timetable source for the pilot region.
- If GTFS is available, run the cached static-GTFS derivation path to parse
  candidate access/egress stops, scheduled travel time, headway, and service
  windows from a reviewed feed snapshot.
- If GTFS is unavailable or incomplete, create a documented rail-assumption
  table using public timetable or agency references where possible.
- Keep rail operational claims conservative.

Acceptance checks:

- Rail access and egress points are traceable to public stops/stations or
  explicitly synthetic points.
- Official station identifiers are committed for station binding, while the
  manuscript/report still limits rail service claims until timetable,
  shortest-path, capacity, and availability evidence are added.
- Headway and travel time are source-backed or clearly marked as assumptions.
- Rail capacity is source-backed, literature-derived, or sensitivity-only.
- The paper/report does not claim emergency rail availability is guaranteed.

## Workstream 6: External Plausibility Validation

Outcome:

Show that the adapted network and assumptions are plausible enough for
comparative decision-support analysis.

Current status:

- First offline route plausibility checks and summary exist for the pilot
  scaffold.
- A deterministic external-or-fallback benchmark interface exists and writes
  `data/validation/external_route_benchmarks.csv`. The current fallback uses
  endpoint straight-line distance, documented detour factors, and coarse urban
  speed assumptions. It is executable offline and explicitly labeled as
  `external_or_fallback_benchmark_not_ground_truth`.
- An optional OSRM route benchmark script exists and writes
  `data/validation/external_route_benchmarks_osrm.csv` plus
  `data/validation/osrm_route_benchmark_summary.md`. After bus-practical road
  filtering, the current optional OSRM snapshot has 3 pass rows and no
  warn/fail rows. Keep it optional because it depends on a live public service
  and remains plausibility evidence, not ground truth.
- The OSRM snapshot manifest now records the cached OSRM CSV checksum, summary
  checksum, query URLs, source/status counts, and 3 live/unpinned rows. It is a
  provenance aid only and does not make OSRM accepted validation evidence.
- The deterministic fallback benchmark still warns on `A -> S`, which should
  be interpreted as a conservative claim-boundary signal about connector and
  access-corridor assumptions.
- Reviewed external-router comparisons with OSRM, Valhalla, routingpy, R5,
  OpenTripPlanner, UXsim, or equivalent are still preferred before making
  publication-grade route-realism claims.
- Route-level accessibility-loss diagnostics now remove each directed edge on
  the baseline shortest-time paths for `A -> D`, `A -> S`, and `R -> D`.
  Current output rows are stored in `data/validation/accessibility_loss.csv`,
  with a summary in `data/validation/accessibility_loss_summary.md`. This
  advances critical-link/accessibility-loss scaffolding, but it remains a
  route-fragility diagnostic until graph-scale, road-input, and validation
  gates are accepted.
- Route-level road-evidence exposure now maps current road-class evidence
  weakness to canonical route candidates. Current output rows are stored in
  `data/validation/canonical_route_road_evidence_exposure.csv`, with a summary
  and manifest beside it. This helps prioritize road evidence collection but
  does not accept speed, capacity, disruption, connector, validation, or
  graph-scale claims.
- `scripts/write_validation_review_packet.py` consolidates internal
  plausibility, fallback benchmark, optional OSRM and its snapshot manifest,
  accessibility-loss, route-level road-evidence exposure, validation-summary scope, and
  benchmark-strategy decision evidence into
  `data/validation/validation_review_packet.csv` plus
  `data/validation/validation_review_manifest.json`. This is the validation
  gate worksheet only; it is not validation acceptance and does not treat any
  benchmark as ground truth.
- `scripts/write_validation_strategy_readiness_packet.py` turns that
  validation worksheet into `data/validation/validation_strategy_readiness_packet.csv`,
  `data/validation/validation_strategy_readiness_manifest.json`, and
  `docs/validation_strategy_readiness_packet.md`. This is a pre-review blocker
  classifier only; it does not create `data/manifests/validation_acceptance.json`
  and cannot close the validation gate.

Validation layers:

1. Internal invariants
   - identical seeds reproduce identical outputs
   - more fleet capacity should not worsen completion unless congestion
     feedback explains it
   - increasing disruption severity generally worsens outcomes
   - increasing transfer delay should not improve multimodal speed
   - no-disruption cases should outperform disrupted cases

2. Public-map plausibility
   - OSM road distances and free-flow times are in plausible ranges
   - station access and last-mile connector distances are not unrealistic
   - speed and capacity defaults are reasonable by road class

3. Benchmark plausibility
   - Use one of OSRM, Valhalla, routingpy, r5py/R5, OpenTripPlanner, or UXsim
     as a plausibility benchmark where feasible.
   - If external tools are unavailable, use the deterministic offline fallback
     only as a benchmark interface and sanity check.
   - The benchmark is not ground truth; document it as a plausibility check.

Create:

- `data/validation/route_plausibility.csv`
- `data/validation/external_route_benchmarks.csv`
- `data/validation/accessibility_loss.csv`
- `data/validation/accessibility_loss_summary.md`
- `data/validation/canonical_route_road_evidence_exposure.csv`
- `data/validation/canonical_route_road_evidence_exposure_summary.md`
- `data/validation/canonical_route_road_evidence_exposure_manifest.json`
- `data/validation/validation_review_packet.csv`
- `data/validation/validation_review_manifest.json`
- `data/validation/validation_strategy_readiness_packet.csv`
- `data/validation/validation_strategy_readiness_manifest.json`
- `data/validation/validation_summary.md`
- tests for validation logic where deterministic.

Acceptance checks:

- Validation failures are actionable.
- Benchmark deviations are summarized, not hidden.
- Any route or connector that looks implausible is fixed or explicitly
  excluded from strong claims.

## Workstream 7: Structured Disruption Scenarios

Outcome:

Replace random-only disruption thinking with spatially meaningful degradation
families.

Current status:

- First deterministic scenario table and edge-mapping helpers exist for random,
  critical-link, access-road, last-mile, rail-station-access, and
  spatial/hazard-overlay families.
- These are scenario-based disruption definitions, not calibrated hazard or
  observed-disaster evidence.

Implement at least:

- random capacity reduction and full blockage baseline
- critical-link disruption using betweenness, edge importance, or high-flow
  proxy
- access-road disruption for `A -> S` and `A -> D`
- last-mile disruption for `R -> D`
- rail-station access disruption
- spatial/hazard overlay scenario using buffers, corridor exposure polygons,
  flood/low-lying proxy, severe-weather corridor, or documented scenario
  polygons

Create:

- `data/scenarios/disruption_scenarios.csv`
- a disruption builder module or extension under `src/realworld/`
- tests for deterministic scenario-to-edge mapping

Acceptance checks:

- Each disrupted edge has a disruption reason category.
- Scenario definitions are reproducible.
- Spatial overlay scenarios are clearly labeled as scenario-based unless they
  use observed disaster data.
- The simulator can compare random, critical-link, access/last-mile, and
  spatial disruption families.

## Workstream 8: Policy Alternatives

Outcome:

The final study compares useful decisions, not only bus-only versus baseline
multimodal.

Current status:

- First policy-alternative table and non-mutating config-variant helpers exist.
- Full paired pilot experiment integration now exists for the current
  single-corridor full profile and the multi-corridor full-profile candidate.
  Both use 7 implemented policy variants, 9 disruption/no-disruption
  scenarios, and 30 seeds for 1,890 rows. These outputs remain scaffold or
  graph-scale review evidence until input validation, graph-scale, and
  experiment acceptance gates close.

Minimum policies:

- direct bus-only
- baseline rail-bus multimodal
- multimodal with redundant last-mile fleet
- staggered or adaptive dispatch

Preferred additions:

- multimodal with increased feeder capacity
- bus-only with alternate corridors
- fleet-shortage scenario
- rail-delay or partial rail-unavailability scenario
- adaptive rerouting under blocked edges

Create:

- `data/scenarios/policy_alternatives.csv`
- config variant builders or experiment runner extensions
- tests that policies modify only intended knobs

Acceptance checks:

- Each policy has a clear decision interpretation.
- Policy changes are documented in plain language.
- Paired experiments use common random numbers where comparisons require them.
- Results report winning regimes, not a universal winner.

## Workstream 9: Sensitivity Analysis

Outcome:

Identify which uncertain assumptions determine whether bus-only,
multimodal, or redundancy policies perform best.

Current status:

- Deterministic one-at-a-time pilot scaffold screening exists with a
  SALib-compatible problem manifest.
- SALib Morris screening now exists for the current full policy/scenario
  scaffold, including p80/p95 arrival-time tail metrics, with
  `morris_results.csv`, `morris_summary.csv`, `morris_manifest.json`, CLI
  support through `scripts/run_sensitivity.py --method morris --all`, and
  narrow tests.
- A 6-row sensitivity review packet now summarizes Morris structural
  readiness, missing/non-finite index rows, zero `mu_star` rows, reduced graph
  scope, scaffold result scope, and the Morris-vs-Sobol decision without
  accepting final-study sensitivity claims.
- Publication-grade sensitivity claims still require applying the formal
  design to the accepted staged/full pilot profile, or documenting why the
  current reduced-corridor scaffold is the intended analysis scope. Sobol
  remains an optional extension, not a completed artifact.

Minimum:

- SALib Morris screening if compute budget is limited.

Preferred:

- Sobol first-order and total-order indices for key outputs.

Parameters to vary:

- passenger volume
- passenger arrival variability
- direct bus fleet size
- feeder fleet size
- last-mile fleet size
- dispatch interval
- road background traffic multiplier
- capacity-reduction factor
- disruption severity
- rail headway
- rail capacity
- transfer fixed delay
- transfer per-passenger delay
- turnaround time
- last-mile access disruption probability

Outputs:

- completion rate
- censored passenger count
- penalized makespan
- 80th and 95th percentile arrival times
- road vehicle-minutes
- passenger-minutes
- passengers moved per service-minute
- multimodal-versus-bus-only performance difference

Acceptance checks:

- Sensitivity results are reproducible from a fixed seed plan.
- The paper reports influential parameters and regime boundaries, not only
  average travel-time rankings.

## Workstream 10: Full Pilot Experiments

Outcome:

Run the final pilot-region experiment package and generate decision-relevant
outputs.

Current status:

- A small pilot scaffold sample runner exists and writes separated outputs
  under `results/realworld_pilot/`.
- The runner can execute against the current cached Overpass/OSM snapshot by
  reducing the large graph to required analysis corridors for `A -> D`,
  `A -> S`, and `R -> D`.
- This corridor reduction is acceptable for smoke/sample evidence, but the
  final study must either justify the reduced analysis graph as a deliberate
  zone-corridor abstraction or implement a faster full-network routing path
  before making broad regional resilience claims.
- The sample runner is not the full accepted pilot design. It still needs
  broader scenario/policy/seed coverage, sensitivity integration, and final
  validation before paper/report result claims are updated.

Experiment design:

- no-disruption baseline
- random disruption severity levels
- critical-link disruption severity levels
- access-road and last-mile disruption cases
- spatial/hazard overlay cases
- policy alternatives
- sensitivity design
- multiple seeds or replications for uncertainty summaries

Required metrics:

Speed lens:

- first-arrival time
- median arrival time
- 80th percentile arrival time
- 95th percentile arrival time
- penalized makespan

Reliability lens:

- completion rate
- censored passenger count
- probability of meeting time window
- OD disconnection rate
- performance loss relative to no-disruption baseline

Resource lens:

- road vehicle-minutes
- train-minutes
- passenger-minutes
- passengers moved per service-minute
- fleet utilization
- marginal benefit of additional vehicles

Bottleneck lens:

- origin access bottleneck
- feeder road bottleneck
- rail access bottleneck
- rail trunk bottleneck
- transfer bottleneck
- last-mile bottleneck
- destination access bottleneck

Acceptance checks:

- Result schemas are documented.
- Runs are reproducible from seed and input manifests.
- Result manifests record both source graph scale and analysis graph scale when
  a reduced graph is used.
- Failed or censored scenarios are not dropped silently.
- Full run outputs are separated from old abstract-network outputs.

## Workstream 11: Figures, Tables, And Results Narrative

Outcome:

Produce publication/report-ready evidence without overstating operational
accuracy.

Current status:

- Scaffold-only figures, result tables, Morris sensitivity tables, and
  claim-boundary table exist for the current full pilot outputs.
- Publication/report figures must be regenerated after accepted pilot inputs,
  validation, full experiments, and final sensitivity outputs exist.

Required figures:

- framework pipeline
- pilot regional network map
- generalized OD zones and rail access/egress points
- bus-only versus rail-bus schematic
- disruption overlay example
- completion rate by disruption severity
- censored passengers by disruption severity
- bottleneck attribution chart
- sensitivity ranking chart
- policy regime map

Required tables:

- data source table
- parameter-source table
- scenario design table
- policy alternatives table
- validation checks table
- main result table
- sensitivity result table
- claim-boundary and limitation table

Acceptance checks:

- Figures have captions that distinguish data-derived values from assumptions.
- Tables are generated from current outputs, not manually copied stale values.
- Report language remains readable for non-technical stakeholders.

## Workstream 12: Manuscript And Report Finalization

Outcome:

Align the English paper draft and Korean report with the final pilot-region
evidence.

Paper framing:

```text
Open-data, region-reusable simulation of disrupted regional personnel transport
under road-rail network degradation and constrained fleet operations.
```

Core thesis:

```text
Rail-bus multimodal transport is a conditional resilience strategy whose
performance depends on the joint reliability of access roads, rail service,
transfer handling, last-mile capacity, and finite fleet availability under
regional network disruption.
```

Manuscript structure:

1. Introduction and research questions
2. Open-data regional pipeline
3. Simulation model
4. Pilot-region data and parameter evidence
5. Disruption and policy scenario design
6. Validation and plausibility checks
7. Results
8. Sensitivity and regime interpretation
9. Discussion, limitations, and claim boundaries
10. Reproducibility package

Acceptance checks:

- Abstract is written as a completed real-world or quasi-real study only after
  pilot experiments are complete.
- No result is described as calibrated unless the relevant validation evidence
  exists.
- Limitations explicitly cover OSM quality, capacity proxies, rail assumptions,
  sensitive-location abstraction, mesoscopic approximation, and scenario-based
  disruptions.
- Korean report remains readable and excludes unnecessary code/command detail
  unless an appendix needs it.

## Workstream 13: Reproducibility And Packaging

Outcome:

A clean checkout can reproduce the accepted pilot study without live services
except for explicitly documented optional extraction steps.

Current status:

- A scaffold-only reproducibility package exists for the current pilot path.
- The final accepted pilot package still requires a reviewed OSM-derived input,
  stronger validation evidence, full pilot experiments, and formal sensitivity
  outputs.

Create:

- input manifest
- data snapshot manifest
- parameter manifest
- scenario manifest
- seed manifest
- result manifest
- third-party adaptation and license notes
- README instructions for reproducing smoke, validation, experiment, figures,
  and report

Acceptance checks:

- Cached inputs are used by default.
- Live OSM extraction is optional and documented separately.
- All generated outputs have source inputs and commands documented.
- `cloned_repo/` remains reference-only and is never imported at runtime.

## Subagent Execution Plan For The Final Version

Use subagents only for bounded, disjoint work. Keep the main agent responsible
for integration, validation, and claim guardrails.

For acceptance work, use the implemented repo-native sub-agent review layer
first:

```powershell
.\.venv\Scripts\python scripts\run_acceptance_audit.py
```

This command refreshes review packets and writes conservative gate records. A
record with `blocked` or `needs_human_review` cannot close a final-study gate.

Default subagent setting:

```text
model: gpt-5.5
reasoning_effort: xhigh
```

Use GPT-5.5 xhigh for all work that involves architecture, real-world data
interpretation, calibration assumptions, validation design, experiment design,
sensitivity analysis, or manuscript claim boundaries. Use a lower effort only
for narrow mechanical cleanup after the main integrator confirms no design risk.

Shared subagent contract:

```text
Role:
You are a GPT-5.5 xhigh worker in a shared Windows PowerShell repository.
You are not alone in the codebase. Do not revert or overwrite edits made by
others.

Goal:
Deliver the assigned final-study slice so the project moves toward a
reproducible real-world or quasi-real regional transport-resilience paper and
report.

Ownership:
Edit only the assigned write set. If another file is necessary, report the
exact required change to the main integrator before editing it.

Evidence:
Every factual data, parameter, source, or result claim must be traceable to an
input file, source table, validation output, experiment output, or documented
assumption.

Constraints:
- Do not import runtime code from `cloned_repo/`.
- Do not edit files inside `cloned_repo/`.
- Do not make live web/OSM calls in default tests.
- Preserve `run_scenario(...)` unless the main integrator explicitly accepts an
  API change.
- Do not claim calibrated real-world accuracy unless validation evidence exists.
- Keep code comments and docstrings in English.

Validation:
Run the narrowest useful tests for the owned slice, then report commands and
results. If a command cannot run, state the blocker and fallback check.

Final report:
- Changed files
- Tests or checks run
- Data/source assumptions
- Third-party adaptations and license notes
- Integration notes
- Residual risks
- Blockers
```

GPT-5.5 worker prompt optimizations:

- Give each worker one outcome-first goal and a narrow write set.
- Keep prompts concise; do not copy the full plan unless the worker needs it.
- Include a retrieval budget: read `plan.md`, the owned files, and only the
  nearest relevant modules/tests before editing.
- Require a validation loop: implement, run the narrow owned check, fix once if
  the failure is clearly in the owned slice, then report unresolved blockers.
- Require claim discipline: source-backed facts, documented assumptions, and
  generated results must remain separate.
- Stop each worker when its owned artifact is correct and validated; do not let
  workers start adjacent workstreams without a new assignment.

Main integrator responsibilities:

- Launch only independent workers in parallel.
- Keep write sets disjoint.
- Review worker outputs before starting dependent waves.
- Run integration tests after each wave.
- Resolve interface conflicts centrally.
- Maintain the claim guardrails in documentation, paper, and report.

### Current Next GPT-5.5 Xhigh Wave

The original Wave A/B/C scaffolds have mostly been implemented. From the
current project state, the next useful GPT-5.5 xhigh workers should target the
remaining publication gates below.

Current integration status:

| Worker | Status | Integration Note |
| --- | --- | --- |
| E1 OSM provenance and scale | Mostly scaffolded by main integration | Keep source-vs-analysis graph counts visible in every manifest and decide whether corridor reduction is final-method or smoke shortcut. |
| E2 rail evidence | Partially integrated | Official station bindings, offline timetable/GTFS/shortest-path derivation paths, and optional key-required data.go.kr fetchers are now implemented and audited; rail timing assumptions still need accepted timetable, GTFS, or shortest-path source rows, while capacity is explicitly sensitivity-only until stronger capacity evidence is accepted. |
| E3 external benchmark | Worker output received; main review required | Offline fallback benchmark is useful, but final publication claims still need either external-router evidence or explicit fallback-only limitations. |
| E4 formal sensitivity | Full policy/scenario scaffold implemented; interpretation pending | SALib Morris CLI, tests, manifest, and full policy/scenario outputs exist; final claims still require conservative review or Sobol extension if justified. |
| E5 full pilot experiment design | Outputs generated; acceptance review required | Sample/staged/full profiles and outputs exist; `src/realworld/experiment_acceptance.py` now defines the missing review gate, and staged/full outputs are still not calibrated real-world evidence. |
| E6 figures and bottleneck attribution | Implemented as scaffold; acceptance review required | Current outputs include bottleneck attribution proxy and policy regime-map tables/figures; they are not causal bottleneck evidence. |
| E7 manuscript/report alignment | Scaffold aligned; acceptance review required | Paper/report text now reflects the current OSM-derived scaffold, reduced analysis corridor, Morris output scale, and non-calibrated claim boundary; final acceptance still requires evidence gates and reviewed result claims. |
| E8 final audit | Pending | Run last with write access limited to an audit note unless fixes are explicitly approved. |

Run these workers in parallel only when their write sets remain disjoint:

| Worker | Model/Effort | Write Set | Outcome | Integration Check |
| --- | --- | --- | --- | --- |
| E1 OSM provenance and scale | GPT-5.5 xhigh | `data/cache/`, `scripts/build_pilot_cache.py`, cache docs | source-reviewed cache metadata, fixture-vs-OSM refresh rules, source/analysis graph counts | offline cache load, pilot smoke, sample run |
| E2 rail evidence | GPT-5.5 xhigh | `data/parameters/rail_assumptions.csv`, `data/parameters/rail_station_bindings.csv`, optional station/timetable/shortest-path parsers/docs | cached timing evidence for headway and travel time after official station binding, plus source-backed or explicitly sensitivity-only capacity handling | rail validation plus paper limitation update |
| E3 external benchmark | GPT-5.5 xhigh | `data/validation/`, `src/realworld/plausibility.py`, benchmark docs/tests | OSRM/Valhalla/routingpy/R5/UXsim-style plausibility comparison or documented fallback | validation summary regenerated |
| E4 formal sensitivity | GPT-5.5 xhigh | `data/scenarios/sensitivity_design.csv`, `src/realworld/sensitivity.py`, sensitivity script/tests | SALib Morris or Sobol outputs, or a documented compute/dependency fallback | fixed-seed reproducibility and sensitivity manifest |
| E5 full pilot experiment design | GPT-5.5 xhigh | pilot experiment script/schema/results docs | accepted scenario-policy-seed matrix beyond sample outputs | full or staged pilot run manifest |
| E6 figures and bottleneck attribution | GPT-5.5 xhigh | `src/realworld/pilot_figures.py`, result tables/figures | current-output figures plus bottleneck/regime tables | figures generated from current CSVs |
| E7 manuscript/report alignment | GPT-5.5 xhigh | `paper/`, `report_draft.md`, `docs/`, `status.md` | readable paper/report that matches final outputs without overclaiming | report generation and claim-boundary check |
| E8 final audit | GPT-5.5 xhigh | audit note or checklist only unless fixes are approved | prompt-to-artifact completion audit against this plan | all final gates marked done or explicitly blocked |

Do not send a worker to make broad cross-cutting edits across `src/`, `docs/`,
`paper/`, and `results/` at once. That creates integration risk. The main
integrator should merge worker outputs, run the validation ladder, and decide
whether claims can move from scaffold-level to quasi-real study-level.

### Wave A: Pilot Input And Evidence

Run in parallel:

- Pilot region/data-card worker: owns `data/regions/` and
  `docs/pilot_region_data_card.md`.
- OSM cache worker: owns `data/cache/` extraction/cache scripts or docs and
  offline load smoke.
- Parameter-source worker: owns `data/parameters/` tables.
- Rail evidence worker: owns rail/GTFS or rail-assumption table plus station
  binding table.

Integration gate:

- Cached graph loads offline.
- Region spec validates.
- Parameter tables include all fields needed by the pilot smoke.

### Wave B: Validation And Scenarios

Run after Wave A:

- Plausibility validation worker.
- Structured disruption worker.
- Policy alternatives worker.
- Result schema worker.

Integration gate:

- Pilot graph smoke passes.
- Validation summary exists.
- Disruption and policy scenarios are deterministic and documented.

### Wave C: Experiments And Sensitivity

Run after Wave B:

- Experiment runner worker.
- SALib sensitivity worker.
- Bottleneck attribution worker.
- Figures/tables worker.

Integration gate:

- Pilot outputs regenerate from cached inputs.
- Sensitivity results are reproducible.
- Figures/tables are generated from current outputs.

### Wave D: Manuscript, Report, And Reproducibility

Run after Wave C:

- Paper worker.
- Korean report worker.
- Reproducibility/package worker.
- Final audit worker.

Integration gate:

- Manuscript and report match current outputs.
- Claim-boundary table is explicit.
- Final validation ladder passes.

### Final Worker Card Matrix

| Worker | Model/Effort | Write Set | Core Output | Required Check |
| --- | --- | --- | --- | --- |
| A1 pilot region | GPT-5.5 xhigh | `data/regions/`, `docs/pilot_region_data_card.md` | non-sensitive region spec and data card | `load_region_spec(...)` smoke |
| A2 OSM cache | GPT-5.5 xhigh | `data/cache/`, optional `scripts/build_pilot_cache.py` | cached GraphML and extraction metadata | offline GraphML load smoke |
| A3 parameters | GPT-5.5 xhigh | `data/parameters/` | parameter-source, rail, fleet tables | parameter coverage check |
| A4 rail evidence | GPT-5.5 xhigh | rail input table/docs | official station binding plus GTFS/timetable/shortest-path-derived or documented assumptions | rail table, station-binding, and service-evidence validation |
| B1 plausibility | GPT-5.5 xhigh | `data/validation/`, validation modules/tests | route and assumption plausibility checks | validation summary generated |
| B2 disruptions | GPT-5.5 xhigh | `data/scenarios/`, disruption modules/tests | structured disruption families | deterministic scenario mapping tests |
| B3 policies | GPT-5.5 xhigh | policy scenario table/runner extensions/tests | decision policy alternatives | policy knob tests |
| C1 experiments | GPT-5.5 xhigh | experiment scripts/results schema | pilot paired runs | smoke and sample run outputs |
| C2 sensitivity | GPT-5.5 xhigh | sensitivity scripts/results | Morris or Sobol ranking | fixed-seed reproducibility check |
| C3 figures/tables | GPT-5.5 xhigh | figure/table scripts/results | publication-ready evidence outputs | generated from current outputs |
| D1 paper | GPT-5.5 xhigh | `paper/` | manuscript aligned to results | claim-boundary check |
| D2 Korean report | GPT-5.5 xhigh | `report_draft.md`, report figures | readable stakeholder report | `generate_report.py` |
| D3 reproducibility | GPT-5.5 xhigh | manifests/docs/scripts | clean-checkout reproduction path | final validation ladder |
| D4 final audit | GPT-5.5 xhigh | audit notes only unless fixes approved | prompt-to-artifact completion audit | checklist has no open items |

Ready-to-paste worker prompt template:

```text
Use GPT-5.5 xhigh. You are Worker [ID] for the final real-world
transport-resilience study. You are working in C:\project\transport-system-sim
on Windows PowerShell.

Outcome:
[one-sentence outcome]

Write set:
- [paths]

Inputs to read:
- plan.md
- relevant existing modules/tests/docs
- at most two relevant cloned_repo references if needed

Constraints:
- Do not edit outside the write set unless the main integrator approves.
- Do not import runtime code from cloned_repo.
- Do not edit cloned_repo.
- Do not use live OSM/web calls in default tests.
- Do not overclaim calibrated real-world accuracy.
- Preserve run_scenario(...) unless explicitly approved.

Validation:
[exact command or check]

Final report:
Changed files, tests/checks run, data/source assumptions, third-party
adaptations, integration notes, residual risks, blockers.
```

Parallelism rules:

- Wave A workers can run in parallel because data card, cache, parameters, and
  rail evidence are mostly independent.
- Wave B starts only after cached graph and region spec pass the pilot smoke.
- Wave C starts only after scenario and validation tables are deterministic.
- Wave D starts only after outputs and figures are generated from current
  results.
- Do not run multiple workers on the same file family unless the main
  integrator splits a non-overlapping write set.

Subagent quality gates:

- Use at most four GPT-5.5 xhigh workers in a wave unless the write sets are
  clearly independent and validation cost remains manageable.
- Do not let a worker commit, push, or rewrite project-wide documentation as a
  side effect of a narrow implementation task.
- Require every worker to distinguish implemented evidence, documented
  assumptions, generated results, and publication claims.
- Require workers to report exact commands run. The main integrator reruns
  integration checks after merging worker outputs.
- Treat worker output as proposed work until reviewed. A completed worker does
  not automatically close a final gate.
- If worker outputs conflict, preserve the more conservative claim boundary and
  resolve code interfaces centrally.

## Final Validation Ladder

Run before calling the project final:

```powershell
.\.venv\Scripts\python -m compileall main.py src tests scripts generate_report.py
Get-ChildItem tests\test_*.py | ForEach-Object { .\.venv\Scripts\python $_.FullName }
.\.venv\Scripts\python tests\test_realworld_end_to_end.py
rg -n "(^|\s)(from|import)\s+cloned_repo" src tests scripts
git diff --check
```

Project-specific final commands:

```powershell
.\.venv\Scripts\python scripts\run_pilot_smoke.py
.\.venv\Scripts\python scripts\run_full_graph_smoke.py
.\.venv\Scripts\python scripts\run_graph_scale_diagnostics.py
.\.venv\Scripts\python scripts\write_graph_scale_review_packet.py
.\.venv\Scripts\python scripts\write_graph_scale_strategy_readiness_packet.py
.\.venv\Scripts\python scripts\write_graph_scale_result_comparison.py
.\.venv\Scripts\python scripts\audit_rail_evidence.py
.\.venv\Scripts\python scripts\write_rail_evidence_review_packet.py
.\.venv\Scripts\python scripts\write_rail_timing_source_request_packet.py
.\.venv\Scripts\python scripts\write_rail_fetch_readiness_packet.py
.\.venv\Scripts\python scripts\audit_rail_station_bindings.py
.\.venv\Scripts\python scripts\audit_parameter_evidence.py
.\.venv\Scripts\python scripts\write_parameter_review_packet.py
.\.venv\Scripts\python scripts\write_parameter_evidence_source_request_packet.py
.\.venv\Scripts\python scripts\write_parameter_source_readiness_packet.py
.\.venv\Scripts\python scripts\audit_road_evidence.py
.\.venv\Scripts\python scripts\audit_road_evidence_diagnostics.py
.\.venv\Scripts\python scripts\write_road_capacity_evidence.py
.\.venv\Scripts\python scripts\write_road_speed_evidence.py
.\.venv\Scripts\python scripts\write_road_evidence_review_packet.py
.\.venv\Scripts\python scripts\write_road_evidence_source_request_packet.py
.\.venv\Scripts\python scripts\write_road_source_readiness_packet.py
.\.venv\Scripts\python scripts\write_road_class_override_template.py --output data\parameters\road_class_overrides_draft.csv --overwrite
.\.venv\Scripts\python scripts\audit_source_provenance.py
.\.venv\Scripts\python scripts\write_source_url_review_packet.py
.\.venv\Scripts\python scripts\audit_publication_readiness.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
.\.venv\Scripts\python scripts\run_plausibility_validation.py
.\.venv\Scripts\python scripts\run_accessibility_loss_analysis.py
.\.venv\Scripts\python scripts\write_osrm_snapshot_manifest.py
.\.venv\Scripts\python scripts\write_route_road_evidence_exposure.py
.\.venv\Scripts\python scripts\write_validation_review_packet.py
.\.venv\Scripts\python scripts\write_validation_strategy_readiness_packet.py
.\.venv\Scripts\python scripts\run_reproducibility_smoke.py
.\.venv\Scripts\python scripts\run_pilot_experiments.py --sample
.\.venv\Scripts\python scripts\run_pilot_experiments.py --staged
.\.venv\Scripts\python scripts\run_pilot_experiments.py --multi-corridor
.\.venv\Scripts\python scripts\run_pilot_experiments.py --multi-corridor-full
.\.venv\Scripts\python scripts\run_pilot_experiments.py --full
.\.venv\Scripts\python scripts\run_sensitivity.py --sample
.\.venv\Scripts\python scripts\run_sensitivity.py --method morris --all
.\.venv\Scripts\python scripts\audit_sensitivity_diagnostics.py
.\.venv\Scripts\python scripts\write_sensitivity_review_packet.py
.\.venv\Scripts\python scripts\make_pilot_statistics.py
.\.venv\Scripts\python scripts\make_pilot_statistics.py --input results\realworld_pilot\pilot_multi_corridor_results.csv --source-manifest results\realworld_pilot\pilot_multi_corridor_manifest.json --output-prefix pilot_multi_corridor
.\.venv\Scripts\python scripts\make_pilot_statistics.py --input results\realworld_pilot\pilot_multi_corridor_full_results.csv --source-manifest results\realworld_pilot\pilot_multi_corridor_full_manifest.json --output-prefix pilot_multi_corridor_full
.\.venv\Scripts\python scripts\make_pilot_figures.py
.\.venv\Scripts\python scripts\run_acceptance_audit.py
.\.venv\Scripts\python scripts\write_formal_acceptance_evidence_matrix.py
.\.venv\Scripts\python scripts\run_reproducibility_smoke.py
.\.venv\Scripts\python scripts\audit_tracked_artifacts.py
.\.venv\Scripts\python scripts\audit_formal_evidence_paths.py
.\.venv\Scripts\python scripts\validate_formal_acceptance_package.py
.\.venv\Scripts\python scripts\audit_plan_artifacts.py
.\.venv\Scripts\python scripts\write_goal_completion_audit.py
.\.venv\Scripts\python scripts\audit_publication_readiness.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
.\.venv\Scripts\python generate_report.py
```

Do not include live OSM extraction in the default validation ladder. Cache
refresh commands are separate:

```powershell
.\.venv\Scripts\python scripts\build_pilot_cache.py --source fixture
.\.venv\Scripts\python scripts\build_pilot_cache.py --source overpass
```

Optional live external-router benchmark commands are also separate from the
default validation ladder:

```powershell
.\.venv\Scripts\python scripts\run_osrm_route_benchmark.py
```

Use `--source fixture` only for deterministic fixture fallback work. Use
`--source overpass` only when intentionally replacing the cached OSM snapshot,
then rerun smoke, sample experiments, validation, figures, and documentation
checks before carrying the new snapshot forward.

If any command depends on optional external software, provide a cached or
documented fallback and do not make it part of default unit tests.

## Claim Guardrails

Allowed final claims after all gates pass:

- The framework converts open-map-derived regional road data into
  simulator-ready inputs.
- The pilot study compares bus-only and rail-bus strategies under documented
  disruption and fleet constraints.
- Completion probability, censored passengers, and penalized makespan give more
  decision-relevant resilience evidence than mean travel time alone.
- Sensitivity analysis identifies which uncertain assumptions most influence
  the preferred strategy.

Still avoid:

- The model predicts actual emergency operations.
- OSM data alone validate the real world.
- Bus-only or rail-bus is universally superior.
- The framework is ready for operational deployment.
- Scenario-based disruptions are observed disaster outcomes.

## Immediate Next Execution

Workstreams 1 to 3 now have a cached pilot OSM/GraphML path, offline smoke
path, bus-practical OSM edge filtering, and sample/staged/full experiment
paths. Treat this as an executable quasi-real scaffold, not the final
calibrated pilot case. Workstreams 4, 5, 6, 7, and 8 have first
evidence/scenario scaffolds, including rail-evidence, fallback benchmark, and
optional OSRM benchmark outputs plus a non-acceptance OSRM manifest that still
require publication-level review.
Workstream 10 now has generated sample/staged/full outputs on a reduced
analysis corridor, but the corridor abstraction still needs acceptance before
it becomes the final study method.

Concrete next tasks:

1. Use `docs/review_packets/acceptance_review_index.md` and the 12
   `data/manifests/agent_reviews/*.json` records as the first checklist for
   remaining human/source-backed decisions. Do not create formal acceptance
   files until their packet risks and required actions are resolved.
   Use `docs/acceptance_decision_templates.md` and
   `data/manifests/acceptance_templates/` only as non-approval starting points
   after those reviews; copy a template to a formal acceptance path only when
   the reviewer has replaced placeholders with real evidence and decisions.
   Run `scripts/audit_formal_acceptance_artifacts.py` after any formal
   acceptance file is added to ensure no template or placeholder was copied
   into a final-study acceptance path. Run
   `scripts/audit_formal_evidence_paths.py` as the next check to confirm that
   local evidence paths exist and placeholders are not left in evidence fields;
   still treat that as a necessary hygiene check, not approval.
2. Review the integrated GPT-5.5 xhigh E2 rail-evidence, E3 external-benchmark,
   validation review packet, and E5 pilot-experiment outputs. Keep fallback
   and OSRM benchmarks labeled as plausibility checks, not ground truth.
3. Review the current SALib Morris scaffold outputs against the full
   policy/scenario design using `data/validation/sensitivity_review_packet.csv`.
   Resolve how to handle missing/non-finite index rows, zero `mu_star` rows,
   reduced-graph scope, and the Morris-vs-Sobol decision before creating any
   sensitivity acceptance record. Add Sobol only if compute budget and result
   interpretation justify it.
4. Review the current Overpass/OSM-derived GraphML snapshot, confirm its
   attribution and cache metadata, use the road-class diagnostics to prioritize
   routeable speed/capacity/disruption evidence, and decide whether the reduced
   analysis corridor is an acceptable study abstraction or only a smoke-test
   shortcut.
5. Review the full-vs-reduced route parity, alternate-route, and
   multi-corridor candidate diagnostics. Decide whether the 6 current
   alternate-route warning rows are acceptable under a documented
   corridor-selection rule, whether to regenerate experiments on the
   164-node / 246-edge candidate graph, or whether to replace the current
   graph method with full-graph runtime evidence or a multi-corridor ensemble
   before graph-scale acceptance. Use the graph-scale review packet and
   graph-scale strategy-readiness packet as the consolidated method-selection
   and blocker-classification worksheets.
6. Review the source-graph and analysis-graph scale fields now recorded in
   every pilot, sensitivity, Morris, and figure/table manifest, and keep this
   distinction visible in all manuscript/report result text.
7. Strengthen parameter, road, and rail evidence with GTFS/timetable,
   shortest-path, literature, public speed/capacity references, hazard or
   scenario evidence, or benchmark-calibrated values where available. Use the
   parameter, rail, and road source-request packets before collecting new
   source inputs; official station binding is already cached and rail capacity
   is explicitly sensitivity-only, but cross-cutting parameter evidence, rail
   timing, and road override evidence remain weak.
8. Review `data/validation/osrm_route_benchmark_manifest.json` and decide
   whether the current optional OSRM snapshot is sufficient as a plausibility
   benchmark or whether cached Valhalla, routingpy, R5/OpenTripPlanner, UXsim,
   or equivalent evidence is needed within the publication schedule. Use
   `data/validation/validation_review_packet.csv` and
   `data/validation/validation_strategy_readiness_packet.csv` as the
   benchmark-strategy and blocker-classification worksheets before creating
   any validation acceptance record.
9. Review the current sample/staged/full pilot runner outputs as the candidate
   accepted scenario, policy, and seed design.
10. Regenerate pilot-region figures, paper tables, Korean report updates, and
   final reproducibility manifests after validation passes; keep the current
   regenerated report in scaffold scope until manuscript acceptance is reviewed.
   Use `data/validation/reproducibility_review_packet.csv` to inspect
   clean-checkout blockers before creating any reproducibility acceptance
   record.
11. Run a final GPT-5.5 xhigh audit worker to compare implemented artifacts
   against this plan before calling the project final, then run
   `scripts/audit_publication_readiness.py --fail-on-blockers` and
   `scripts/audit_final_study_readiness.py --fail-on-blockers`.

Do not update paper/report result claims until the accepted pilot cache,
parameter-source tables, validation package, and full pilot experiments pass.
