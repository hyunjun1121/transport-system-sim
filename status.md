# Project Status

## Current Date And Workspace

- Date: 2026-05-08
- Workspace: `C:\project\transport-system-sim`
- Platform in use: Windows PowerShell
- Git branch: `main`
- Remote: `https://github.com/hyunjun1121/transport-system-sim.git`

## Latest Audit Snapshot

- `final_study_ready=false`.
- Final-study gate count: 15.
- Ready gates: 3/15:
  - `real_input_smoke`
  - `structured_disruptions`
  - `policy_alternatives`
- Blocked gates: 12/15:
  - `pilot_region_accepted`
  - `cached_osm_input`
  - `graph_scale_strategy`
  - `data_provenance`
  - `parameter_evidence`
  - `rail_evidence`
  - `validation_package`
  - `sensitivity_analysis`
  - `full_experiment_output`
  - `manuscript_report_alignment`
  - `reproducibility`
  - `final_audit`
- Formal acceptance readiness: 0/12. The required formal acceptance artifacts
  are intentionally absent until reviewers supply real, source-backed
  decisions.
- Latest blocker/readiness packets are implemented for
  `validation_strategy_readiness`, `graph_scale_strategy_readiness`,
  `sensitivity_strategy_readiness`, and `experiment_strategy_readiness`, with
  a focused `validation_benchmark_decision` worksheet for route-benchmark
  scope choices and a focused `experiment_design_decision` worksheet for
  run-profile/design choices, plus a focused `figure_table_review` worksheet
  for scaffold figure/table review. They make the remaining review work
  explicit but do not close acceptance gates.
- There is still no calibrated real-world result and no operational route plan.

## Project Goal

This project is a disrupted regional personnel-transport micro-simulation. The
implemented baseline compares:

- Bus-only transport
- Rail-bus multimodal transport

The baseline scenario moves about 1,000 people from an assembly context toward
a destination zone. The original use case was reserve-force transport, but the
current research direction is broader and more publishable:

> open-data, region-reusable, real-world or quasi-real simulation of emergency
> personnel movement, disrupted regional mobility, and public-sector
> contingency transport planning.

The goal is to make the simulator as close as practical to a real-world
disrupted regional transport scenario while keeping claims conservative.

## Current Implementation State

The codebase currently includes:

- Queue-based passenger dispatch
- STRICT and GRACE departure policies
- Finite fleet availability and turnaround
- Bus-only road transport
- Multimodal shuttle, rail, and last-mile transport
- Fixed-headway rail service
- Transfer delay modeling
- Rolling-window dynamic BPR road traffic
- Road disruption modes:
  - Full blockage
  - Capacity reduction
- Completion, censoring, penalized makespan, and resource-efficiency metrics
- Common-random-number paired experiments
- Phase 1 and Phase 2 experiment runners
- CSV output and PNG plot generation
- Korean narrative report generation to Word
- Real-world/quasi-real input MVP under `src/realworld/`:
  - validated region, boundary, zone, and rail specs
  - OSM-style road attribute mapping to simulator edge fields
  - bus-practical OSM edge filtering before zone snapping
  - optional OSMnx bbox extraction behind a lazy import boundary
  - offline GraphML cache load/save helpers
  - nearest-node zone snapping and bidirectional connector edges
  - adapter from normalized OSM-like graphs to simulator-compatible DiGraphs
  - graph-readiness validation and synthetic end-to-end smoke tests
- Real-world evidence and scenario scaffolding:
  - `data/parameters/parameter_sources.csv`
  - optional weak-parameter acceptance validation in
    `src/realworld/parameter_acceptance.py` and
    `docs/parameter_acceptance_schema.md`; the actual
    `data/parameters/parameter_acceptance.csv` file is intentionally absent
    until reviewers explicitly accept retained weak assumptions within final
    claim boundaries
  - `data/parameters/rail_assumptions.csv`
  - `data/parameters/fleet_assumptions.csv`
  - `data/parameters/rail_service_evidence.csv`
  - `data/rail/pilot_station_binding_cache.csv`
  - `data/parameters/rail_station_bindings.csv`
  - `data/parameters/rail_evidence_review_packet.csv`
  - `data/parameters/rail_evidence_review_manifest.json`
  - `data/rail/rail_timing_source_request_packet.csv`
  - `data/rail/rail_timing_source_request_manifest.json`
  - `data/validation/route_plausibility.csv`
  - `data/validation/external_route_benchmarks.csv`
  - `data/validation/external_route_benchmarks_osrm.csv`
  - `data/validation/osrm_route_benchmark_summary.md`
  - `data/validation/osrm_route_benchmark_manifest.json`
  - `data/validation/validation_summary.md`
  - `data/validation/canonical_route_road_evidence_exposure.csv`
  - `data/validation/canonical_route_road_evidence_exposure_manifest.json`
  - `data/validation/validation_review_packet.csv`
  - `data/validation/validation_review_manifest.json`
  - `data/validation/validation_strategy_readiness_packet.csv`
  - `data/validation/validation_strategy_readiness_manifest.json`
  - `data/validation/sensitivity_strategy_readiness_packet.csv`
  - `data/validation/sensitivity_strategy_readiness_manifest.json`
  - `data/scenarios/disruption_scenarios.csv`
  - `data/scenarios/policy_alternatives.csv`
  - explicit graph-scale acceptance validation in
    `src/realworld/graph_scale_acceptance.py` and
    `docs/graph_scale_acceptance_schema.md`; the actual
    `data/manifests/graph_scale_acceptance.json` record is intentionally
    absent until a real source-vs-analysis graph decision is reviewed
  - explicit validation-package acceptance validation in
    `src/realworld/validation_acceptance.py` and
    `docs/validation_acceptance_schema.md`; the actual
    `data/manifests/validation_acceptance.json` record is intentionally
    absent until a real benchmark-strategy review occurs
  - explicit sensitivity-analysis acceptance validation in
    `src/realworld/sensitivity_acceptance.py` and
    `docs/sensitivity_acceptance_schema.md`; the actual
    `data/manifests/sensitivity_acceptance.json` record is intentionally
    absent until a real Morris/Sobol review occurs
  - explicit experiment-output acceptance validation in
    `src/realworld/experiment_acceptance.py` and
    `docs/experiment_acceptance_schema.md`; the actual
    `data/manifests/experiment_acceptance.json` record is intentionally
    absent until graph scope, input validation, scenario-policy-seed design,
    CRN pairing, counts, and not-operational claim limits are reviewed
  - experiment-package review worksheet in
    `data/manifests/experiment_package_review_packet.csv`,
    `data/manifests/experiment_package_review_manifest.json`, and
    `docs/experiment_package_review_packet.md`, generated by
    `scripts/write_experiment_package_review_packet.py`; this turns full
    result row counts, summary counts, design counts, graph/input dependencies,
    CRN declaration, checksums, and acceptance absence into review rows without
    accepting the experiment package
  - experiment strategy-readiness worksheet in
    `data/manifests/experiment_strategy_readiness_packet.csv`,
    `data/manifests/experiment_strategy_readiness_manifest.json`, and
    `docs/experiment_strategy_readiness_packet.md`, generated by
    `scripts/write_experiment_strategy_readiness_packet.py`; this classifies
    4 blocking requests and 5 human-review requests before any experiment
    acceptance record can be created
  - experiment design-decision worksheet in
    `data/manifests/experiment_design_decision_packet.csv`,
    `data/manifests/experiment_design_decision_manifest.json`, and
    `docs/experiment_design_decision_packet.md`, generated by
    `scripts/write_experiment_design_decision_packet.py`; this compares
    current sample/staged/full profiles and the multi-corridor full candidate
    without selecting a final accepted run profile
  - explicit data-provenance acceptance validation in
    `src/realworld/provenance_acceptance.py` and
    `docs/provenance_acceptance_schema.md`; the actual
    `data/manifests/provenance_acceptance.json` record is intentionally
    absent until source snapshots, license/attribution, privacy abstraction,
    cache manifests, reproduction paths, and not-operational claim limits are
    reviewed
  - explicit manuscript/report acceptance validation in
    `src/realworld/manuscript_acceptance.py` and
    `docs/manuscript_acceptance_schema.md`; the actual
    `data/manifests/manuscript_acceptance.json` record is intentionally absent
    until paper/report text, regenerated docx, figures/tables, evidence gates,
    result claims, and not-operational claim limits are reviewed
  - manuscript/report claim-alignment worksheet in
    `data/manifests/claim_alignment_review_packet.csv`,
    `data/manifests/claim_alignment_review_manifest.json`, and
    `docs/claim_alignment_review_packet.md`, generated by
    `scripts/write_claim_alignment_review_packet.py`; this identifies guarded
    claim-boundary language and overclaim candidates without accepting the
    manuscript/report gate
  - figure/table review worksheet in
    `data/manifests/figure_table_review_packet.csv`,
    `data/manifests/figure_table_review_manifest.json`, and
    `docs/figure_table_review_packet.md`, generated by
    `scripts/write_figure_table_review_packet.py`; this audits scaffold
    figure/table inventory, row counts, captions, graph-scope dependencies,
    Morris index handling, proxy interpretation, upstream evidence blockers,
    and missing manuscript acceptance without approving figure/table claims
  - explicit clean-checkout reproducibility acceptance validation in
    `src/realworld/reproducibility_acceptance.py` and
    `docs/reproducibility_acceptance_schema.md`; the actual
    `data/manifests/reproducibility_acceptance.json` record is intentionally
    absent until validation ladder, artifact regeneration, manifest paths,
    runtime import boundaries, command counts, and not-operational claim limits
    are reviewed
  - reproducibility review packet generation in
    `src/realworld/reproducibility_review_packet.py` and
    `scripts/write_reproducibility_review_packet.py`; the generated packet
    records scaffold scope, Git worktree state, untracked artifact risk,
    validation command ladder, runtime `cloned_repo` import boundary, and
    clean-checkout execution scope without accepting reproducibility
  - bounded current-worktree reproducibility smoke in
    `src/realworld/reproducibility_smoke.py` and
    `scripts/run_reproducibility_smoke.py`; the current manifest records 24
    passing commands and `smoke_passed: true`, while keeping
    `clean_checkout_test_performed: false` and `can_mark_complete: false`
  - agent-review path hygiene auditing in
    `src/realworld/agent_review_path_audit.py` and
    `scripts/audit_agent_review_paths.py`; it confirms sub-agent review
    records cite existing local paths or explicit missing formal targets
    without approving any gate
  - tracked-artifact packaging auditing in
    `src/realworld/tracked_artifact_audit.py` and
    `scripts/audit_tracked_artifacts.py`; it lists changed artifacts that a
    clean checkout of the current Git HEAD would miss unless they are
    committed, packaged, or explicitly excluded from the accepted reproduction
    scope, while excluding its own generated CSV, manifest, and Markdown
    outputs so repeated audit runs do not create self-blockers
  - formal evidence-path hygiene auditing in
    `src/realworld/formal_evidence_path_audit.py` and
    `scripts/audit_formal_evidence_paths.py`; the current manifest records no
    formal reviewer artifacts in the acceptance paths, checks 11 structured
    formal paths, and keeps `can_mark_complete: false`
  - explicit independent final-audit acceptance validation in
    `src/realworld/final_audit_acceptance.py` and
    `docs/final_audit_acceptance_schema.md`; the actual
    `data/manifests/final_audit_acceptance.json` record is intentionally
    absent until a prompt-to-artifact audit verifies every pre-final gate,
    rejects proxy-only completion evidence, and confirms no blocked gates
    remain
  - explicit pilot acceptance validation in
    `src/realworld/pilot_acceptance.py` and
    `docs/pilot_acceptance_schema.md`; the actual
    `data/manifests/pilot_acceptance.json` acceptance record is intentionally
    absent until a real privacy, graph-scale, evidence, and claim-boundary
    review occurs
  - validators/helpers in `src/realworld/parameters.py`,
    `src/realworld/plausibility.py`,
    `src/realworld/disruption_scenarios.py`, and
    `src/realworld/policy_alternatives.py`
  - rail evidence cache validation in `src/realworld/rail_evidence.py` and
    `scripts/audit_rail_evidence.py`
  - rail evidence review packet generation in
    `src/realworld/rail_evidence_review_packet.py` and
    `scripts/write_rail_evidence_review_packet.py`; the generated 10-row
    packet records station binding as ready, keeps rail service timing weak
    until cached timetable, GTFS, or shortest-path evidence is reviewed, and
    does not close the rail evidence gate
  - rail timing source-request packet generation in
    `src/realworld/rail_timing_request_packet.py` and
    `scripts/write_rail_timing_source_request_packet.py`; the generated 5-row
    packet names the API-key, GTFS, capacity, and availability inputs needed
    before cached rail timing evidence can be derived, carries the binding
    `region_id`, accepts a cache prefix, and preserves a custom station-binding
    path in generated derivation commands
  - rail fetch-readiness packet generation in
    `src/realworld/rail_fetch_readiness_packet.py` and
    `scripts/write_rail_fetch_readiness_packet.py`; the manifest records the
    `region_ids` from the rail timing request rows and remains a
    non-acceptance preflight packet
  - rail-point station binding validation in
    `src/realworld/rail_station_binding.py` and
    `scripts/audit_rail_station_bindings.py`
  - cached station binding derivation in
    `src/realworld/rail_station_cache.py` and
    `scripts/derive_rail_station_bindings.py`
  - official line-specific station-code bindings for the current pilot rail
    points, derived from the cached Seoul Open Data Plaza station-name search
    extract. This closes station binding only; rail headway, travel time,
    path choice, and availability remain assumption-backed blockers, while rail
    capacity is explicitly retained as a sensitivity-only value.
  - cached rail timetable derivation in `src/realworld/rail_timetable.py` and
    `scripts/derive_rail_service_evidence.py`, with field-level derived timing
    evidence and source artifact SHA256 support for future reviewed extracts
  - cached rail headway-only derivation in
    `scripts/derive_rail_headway_evidence.py`, allowing timetable-derived
    headway to be combined with a separate shortest-path or GTFS travel-time
    evidence row without overclaiming travel time
  - cached static-GTFS derivation in `src/realworld/rail_gtfs.py` and
    `scripts/derive_rail_gtfs_evidence.py`, allowing a reviewed GTFS zip or
    directory to support scheduled headway and access-to-egress travel-time
    evidence while preserving source artifact SHA256; no reviewed GTFS feed is
    committed for the current pilot
  - optional key-required data.go.kr train-schedule cache fetch in
    `src/realworld/rail_timetable_api.py` and
    `scripts/fetch_rail_timetable_cache.py`; this creates a local timetable
    cache only when an API key, reviewed station/line filters, extraction date,
    and raw response retention plan are available
  - cached rail shortest-path derivation in
    `src/realworld/rail_shortest_path.py` and
    `scripts/derive_rail_shortest_path_evidence.py`, with station-code
    cross-checks against official rail-point bindings and source artifact
    SHA256 support for future reviewed station-to-station extracts
  - optional key-required data.go.kr rail shortest-path cache fetch in
    `src/realworld/rail_shortest_path_api.py` and
    `scripts/fetch_rail_shortest_path_cache.py`; this creates a local cache
    only when an API key, reviewed station names/codes, extraction date, and
    raw response retention plan are available
  - parameter evidence readiness audit in
    `src/realworld/parameter_audit.py` and
    `scripts/audit_parameter_evidence.py`
  - parameter evidence review packet in
    `src/realworld/parameter_review_packet.py` and
    `scripts/write_parameter_review_packet.py`; the generated 29-row packet
    marks 25 core parameters as weak for final-study claims and is review
    support only
  - parameter evidence source-request packet in
    `src/realworld/parameter_evidence_request_packet.py` and
    `scripts/write_parameter_evidence_source_request_packet.py`; the generated
    6-row packet covers 22 cross-cutting demand, fleet, dispatch, transfer,
    disruption, and traffic/BPR parameters and is request support only
  - parameter source-readiness packet generation in
    `src/realworld/parameter_source_readiness_packet.py` and
    `scripts/write_parameter_source_readiness_packet.py`; the manifest records
    the `region_ids` from the request rows and remains non-acceptance review
    metadata
  - cached road-input evidence audit in
    `src/realworld/road_evidence.py` and `scripts/audit_road_evidence.py`
  - road-class evidence diagnostics in
    `src/realworld/road_evidence_diagnostics.py` and
    `scripts/audit_road_evidence_diagnostics.py`; these rank routeable
    highway classes by speed, capacity, and base-disruption evidence gaps
    without accepting calibration
  - cached OSM maxspeed candidate evidence in
    `src/realworld/road_speed_evidence.py` and
    `scripts/write_road_speed_evidence.py`; the generated table has 10
    routeable road-class rows and 5 rows with observed maxspeed tags, and is
    review support only
  - cached OSM lane-count capacity candidate evidence in
    `src/realworld/road_capacity_evidence.py` and
    `scripts/write_road_capacity_evidence.py`; the generated table has 10
    routeable road-class rows and 0 rows with observed lane tags, making the
    capacity evidence gap explicit
  - road-input evidence review packet in
    `src/realworld/road_evidence_review_packet.py` and
    `scripts/write_road_evidence_review_packet.py`; the generated 10-row
    packet consolidates speed, capacity, base-disruption, and draft-override
    evidence status, and all rows remain weak for final-study road claims
  - road evidence source-request packet in
    `src/realworld/road_evidence_request_packet.py` and
    `scripts/write_road_evidence_source_request_packet.py`; the generated
    5-row packet names the source-backed speed, capacity, benchmark,
    disruption, and override-application inputs needed before reviewed road
    overrides can be built, and the override-application row uses the full
    pilot profile when pointing at `pilot_full_manifest.json`
  - road source-readiness packet generation in
    `src/realworld/road_source_readiness_packet.py` and
    `scripts/write_road_source_readiness_packet.py`; the manifest records the
    `region_ids` from the request rows and remains non-acceptance review
    metadata
  - draft road-class override review templates in
    `src/realworld/road_override_template.py` and
    `scripts/write_road_class_override_template.py`; generated rows mirror
    current mapper defaults and remain weak until reviewers replace values and
    sources with real evidence
  - `data/parameters/road_class_overrides_draft.csv`, currently generated with
    10 routeable road-class rows and all rows labeled `expert assumption`; it
    is a review worksheet, not accepted road evidence
  - optional road-class override loading in `src/realworld/road_overrides.py`
  - optional road-class override evidence audit in
    `src/realworld/road_override_audit.py` and
    `scripts/audit_road_overrides.py`
  - pilot experiment manifests record road-class override path and SHA256 when
    a reviewed override table is explicitly supplied; the road override audit
    separately checks accepted-manifest application before final road claims
  - pilot scaffold sample experiment runner in
    `src/realworld/pilot_experiments.py` and
    `scripts/run_pilot_experiments.py`
  - deterministic sensitivity screening and SALib Morris scaffold screening in
    `src/realworld/sensitivity.py` and `scripts/run_sensitivity.py`
  - Morris sensitivity diagnostics in
    `src/realworld/sensitivity_diagnostics.py` and
    `scripts/audit_sensitivity_diagnostics.py`, which expose count consistency,
    explicitly unavailable index rows, unexplained blank/non-finite index
    values, zero-effect rows, reduced graph scope, and scaffold claim
    boundaries without accepting final-study sensitivity claims
  - sensitivity review packet generation in
    `src/realworld/sensitivity_review_packet.py` and
    `scripts/write_sensitivity_review_packet.py`; the generated 6-row packet
    summarizes Morris structural readiness, 168 explicitly unavailable index
    rows, 0 unexplained missing/non-finite index rows, 4,272 zero `mu_star`
    rows, reduced-graph scope, scaffold result scope, and the Morris-vs-Sobol
    decision while keeping `publication_ready: false`
  - sensitivity strategy-readiness packet generation in
    `src/realworld/sensitivity_strategy_readiness_packet.py` and
    `scripts/write_sensitivity_strategy_readiness_packet.py`; the generated
    7-row packet classifies 4 blocking requests and 3 human-review requests
    before any sensitivity acceptance record can be created
  - sensitivity method-decision packet generation in
    `src/realworld/sensitivity_method_decision_packet.py` and
    `scripts/write_sensitivity_method_decision_packet.py`; the generated
    7-row packet lists Morris screening, Sobol extension, deferral,
    index-handling, graph-scope, result-scope, and formal-acceptance decision
    rows without running Sobol, waiving Sobol, or accepting Morris output
  - graph-scale strategy-readiness packet generation in
    `src/realworld/graph_scale_strategy_readiness_packet.py` and
    `scripts/write_graph_scale_strategy_readiness_packet.py`; the generated
    5-row packet classifies reduced-corridor, multi-corridor, full-graph, and
    missing-acceptance blockers without choosing a graph-scale method
  - validation review packet generation in
    `src/realworld/validation_review_packet.py` and
    `scripts/write_validation_review_packet.py`; the generated 7-row packet
    summarizes internal plausibility status, fallback benchmark warnings,
    optional OSRM snapshot and manifest status, accessibility-loss coverage,
    route-level road-evidence exposure, validation summary scope, and the
    benchmark-strategy decision while keeping
    `publication_ready: false` and `acceptance_ready: false`
  - validation strategy-readiness packet generation in
    `src/realworld/validation_strategy_readiness_packet.py` and
    `scripts/write_validation_strategy_readiness_packet.py`; the generated
    7-row packet classifies validation blockers and human-review items without
    choosing or approving a benchmark strategy
  - OSRM snapshot manifest generation in
    `src/realworld/osrm_snapshot_manifest.py` and
    `scripts/write_osrm_snapshot_manifest.py`; the current manifest records 3
    pass rows, 3 cached external-router rows, 0 unpinned rows, 3 retained raw
    response files, query URLs, CSV/summary checksums, and a non-acceptance
    claim boundary
  - route-level road-evidence exposure generation in
    `src/realworld/route_road_evidence_exposure.py` and
    `scripts/write_route_road_evidence_exposure.py`; current output has 76 rows
    across 18 route candidates and links weak road speed, capacity, disruption,
    and connector assumptions to canonical route candidates without accepting
    road calibration or validation claims
  - scaffold-only figure/table generation in `src/realworld/pilot_figures.py`
    and `scripts/make_pilot_figures.py`
  - route-level critical-edge/accessibility-loss diagnostics in
    `src/realworld/accessibility.py` and
    `scripts/run_accessibility_loss_analysis.py`; current scaffold output has
    127 directed edge-removal rows across `A -> D`, `A -> S`, and `R -> D`,
    including 22 disconnected edge-removal cases
  - full-vs-reduced graph-scale route parity diagnostics in
    `src/realworld/graph_scale_diagnostics.py` and
    `scripts/run_graph_scale_diagnostics.py`; current scaffold output has
    3 rows for `A -> D`, `A -> S`, and `R -> D`, all passing baseline
    shortest-time path preservation while remaining non-acceptance evidence
  - graph-scale alternate-route sensitivity diagnostics from the same script;
    current scaffold output has 9 rows, with 3 rank-1 pass rows and 6
    alternate-route warning rows that keep corridor-abstraction uncertainty
    visible
  - graph-scale multi-corridor candidate diagnostics; current scaffold output
    has 9 rows, all pass, on a 164-node / 246-edge candidate graph that
    preserves the top 3 full-graph route candidates per canonical road leg
  - graph-scale method review packet generation in
    `src/realworld/graph_scale_review.py` and
    `scripts/write_graph_scale_review_packet.py`; current output has 4
    option rows comparing the reduced corridor, the 164-node / 246-edge small
    multi-corridor candidate, the 164-node / 246-edge full-profile
    multi-corridor candidate, and the full bus-practical graph as a review
    worksheet only
  - graph-scale result comparison generation in
    `src/realworld/graph_scale_result_comparison.py` and
    `scripts/write_graph_scale_result_comparison.py`; current output has 819
    current-vs-full-profile-candidate metric delta rows and remains
    non-acceptance review evidence
  - scaffold-aligned paper/report text in `paper/paper_draft.md` and
    `report_draft.md`, with `report.docx` regenerated from source; these
    documents now state the OSM-derived graph scales, reduced analysis
    corridor, full pilot row counts, Morris row counts, and non-calibrated
    claim boundary without closing the manuscript/report acceptance gate
  - scaffold artifact audit in `scripts/audit_plan_artifacts.py`
  - final-study publication-readiness aggregation in
    `src/realworld/publication_readiness.py` and
    `scripts/audit_publication_readiness.py`
  - plan-level final-study readiness auditing in
    `src/realworld/final_study_readiness.py` and
    `scripts/audit_final_study_readiness.py`, mapping every `plan.md` final
    gate to concrete artifacts while keeping scaffold presence separate from
    final-study completion
  - `scripts/audit_plan_artifacts.py` includes the parameter evidence audit
    summary while preserving the non-calibrated claim boundary
  - active-goal prompt-to-artifact completion gap audit in
    `docs/current_goal_completion_audit.md` and structured non-acceptance
    manifest `data/manifests/current_goal_completion_audit.json`
  - deterministic acceptance-orchestration review layer in
    `src/realworld/acceptance_records.py`,
    `src/realworld/acceptance_orchestration.py`, and
    `scripts/run_acceptance_audit.py`; current generated outputs are
    `agents/acceptance_review_agents.json`,
    `schemas/acceptance_record.schema.json`,
    `data/manifests/acceptance_orchestration_manifest.json`, 12
    `data/manifests/agent_reviews/*.json` records, and 13
    `docs/review_packets/*.md` files. These artifacts make blocked gates
    auditable but do not approve the final study.
  - non-approval formal acceptance decision templates in
    `src/realworld/acceptance_decision_templates.py` and
    `scripts/write_acceptance_decision_templates.py`; current generated
    outputs are 9 JSON templates under
    `data/manifests/acceptance_templates/`,
    `data/parameters/parameter_acceptance_template.csv` with 25 weak-parameter
    rows, `data/manifests/acceptance_decision_template_manifest.json`, and
    `docs/acceptance_decision_templates.md`. These templates keep
    `accepted: false` and are reviewer worksheets, not formal acceptance.
  - human acceptance runbook in `docs/human_acceptance_runbook.md`; it gives
    reviewers the gate-by-gate workflow for moving from review packets and
    non-approval templates to formal artifacts without treating placeholders,
    tests, OSM presence, or scaffold outputs as approval.
  - formal acceptance blocker queue in
    `src/realworld/acceptance_blocker_queue.py` and
    `scripts/write_acceptance_blocker_queue.py`; it writes
    `data/manifests/formal_acceptance_blocker_queue.csv`,
    `data/manifests/formal_acceptance_blocker_queue_manifest.json`, and
    `docs/formal_acceptance_blocker_queue.md` with one row per unresolved
    reviewer action. It is a work queue only and cannot approve a gate.
  - acceptance task assignments in
    `src/realworld/acceptance_task_assignments.py` and
    `scripts/write_acceptance_task_assignments.py`; they map the 15 current
    formal blocker rows to 10 deterministic review-agent roles and write
    `data/manifests/acceptance_task_assignments.csv`,
    `data/manifests/acceptance_task_assignments_manifest.json`, and
    `docs/acceptance_task_assignments.md`. These assignments are auditable
    work allocation only and cannot approve evidence.
  - formal acceptance evidence matrix in
    `src/realworld/formal_acceptance_evidence_matrix.py` and
    `scripts/write_formal_acceptance_evidence_matrix.py`; it writes
    `data/manifests/formal_acceptance_evidence_matrix.csv`,
    `data/manifests/formal_acceptance_evidence_matrix_manifest.json`, and
    `docs/formal_acceptance_evidence_matrix.md` with one row per required
    formal target. It joins reviewer agent, template/worksheet, review
    packets, blockers, source paths, and validation commands. The assigned
    review-agent source paths now include current readiness packets for
    graph-scale, parameter/road/rail evidence, validation, sensitivity,
    experiment, and reproducibility review, but the matrix remains reviewer
    intake only.
  - formal acceptance artifact guard in
    `src/realworld/formal_acceptance_guard.py` and
    `scripts/audit_formal_acceptance_artifacts.py`; it reports 12 required
    formal acceptance paths as currently missing, confirms no template or
    placeholder has been copied into a formal path, and cannot mark the final
    study complete.
  - formal acceptance package intake audit in
    `src/realworld/formal_acceptance_package.py` and
    `scripts/validate_formal_acceptance_package.py`; it aggregates the
    individual acceptance validators, road-override readiness, formal guard,
    and final-study readiness into
    `data/manifests/formal_acceptance_package_audit.json` and
    `docs/formal_acceptance_package_audit.md` without creating approvals.
  - first/median/80th/95th arrival-time KPIs in generated pilot outputs
  - scaffold-only bottleneck attribution proxy and policy-regime map outputs
  - scaffold-only reproducibility package in
    `docs/reproducibility_package.md` and
    `data/manifests/reproducibility_manifest.json`
  - source provenance review packet in
    `data/manifests/source_provenance_manifest.json`, with validation in
    `src/realworld/source_provenance.py` and
    `scripts/audit_source_provenance.py`; this records source URLs,
    license/terms notes, snapshot/access dates, local artifacts, review
    statuses, and claim boundaries without accepting final-study provenance
  - source/license review worksheet in
    `data/manifests/source_license_review_packet.csv`,
    `data/manifests/source_license_review_manifest.json`, and
    `docs/source_license_review_packet.md`, generated by
    `scripts/write_source_license_review_packet.py`; this breaks provenance
    review into source-specific license, attribution, snapshot, privacy, and
    reproducibility actions without certifying license compatibility
  - source URL review worksheet in
    `data/manifests/source_url_review_packet.csv`,
    `data/manifests/source_url_review_manifest.json`, and
    `docs/source_url_review_packet.md`, generated by
    `scripts/write_source_url_review_packet.py`; this breaks source citations
    into URL-level reviewer checks, keeps optional live reachability separate
    from license/source acceptance, and supports `--preserve-existing-live`
    for offline refreshes that should not downgrade prior live URL checks
  - source URL remediation worksheet in
    `data/manifests/source_url_remediation_packet.csv`,
    `data/manifests/source_url_remediation_manifest.json`, and
    `docs/source_url_remediation_packet.md`, generated by
    `scripts/write_source_url_remediation_packet.py`; this converts URL status
    rows into unresolved reviewer actions, including same-source reachable URL
    candidates for failed citations, without accepting source provenance
  - source provenance priority worksheet in
    `data/manifests/source_provenance_priority_packet.csv`,
    `data/manifests/source_provenance_priority_manifest.json`, and
    `docs/source_provenance_priority_packet.md`, generated by
    `scripts/write_source_provenance_priority_packet.py`; this carries
    source-level provenance priorities and same-source alternate URL candidates
    without accepting source provenance
  - source context-cache request worksheet in
    `data/manifests/source_context_cache_request_packet.csv`,
    `data/manifests/source_context_cache_request_manifest.json`, and
    `docs/source_context_cache_request_packet.md`, generated by
    `scripts/write_source_context_cache_request_packet.py`; this turns
    context-only public sources into reviewed cache-or-exclude actions without
    fetching public data or accepting source provenance
  - source context-cache decision worksheet in
    `data/manifests/source_context_cache_decision_packet.csv`,
    `data/manifests/source_context_cache_decision_manifest.json`, and
    `docs/source_context_cache_decision_packet.md`, generated by
    `scripts/write_source_context_cache_decision_packet.py`; this records one
    pending cache/exclude/sensitivity-only decision row per context-only public
    source without caching public data, certifying licenses, or creating
    provenance acceptance
  - pilot privacy review worksheet in
    `data/manifests/pilot_privacy_review_packet.csv`,
    `data/manifests/pilot_privacy_review_manifest.json`, and
    `docs/pilot_privacy_review_packet.md`, generated by
    `scripts/write_pilot_privacy_review_packet.py`; this breaks the pilot
    boundary, public/synthetic points, coordinate policy, and data-card claim
    boundary into reviewer actions without accepting the pilot case
  - manuscript/report claim-alignment worksheet in
    `data/manifests/claim_alignment_review_packet.csv`,
    `data/manifests/claim_alignment_review_manifest.json`, and
    `docs/claim_alignment_review_packet.md`, generated by
    `scripts/write_claim_alignment_review_packet.py`; this turns paper/report
    claim wording and figure/table boundary language into review rows without
    creating manuscript acceptance
  - plan-gate audit in `docs/plan_completion_audit.md`
  - reduced-corridor method boundary in
    `docs/analysis_corridor_method_note.md`
  - separated sample/staged/full outputs under `results/realworld_pilot/`
- First offline pilot scaffold and smoke path:
  - `data/regions/pilot_region.yaml`
  - `data/cache/pilot_region_road.graphml`
  - `data/cache/pilot_region_road_manifest.json`
  - `docs/pilot_region_data_card.md`
  - `scripts/build_pilot_cache.py`
  - `scripts/run_pilot_smoke.py`
  - `scripts/run_full_graph_smoke.py`
  - `tests/test_realworld_pilot_smoke.py`
  - `tests/test_realworld_full_graph_smoke.py`

`scripts/build_pilot_cache.py` now preserves an existing cache by default.
Use `--source fixture` or `--source overpass` only when intentionally replacing
the cache.

## Current Full Experiment Outputs

The current full output set already exists under `results/`.

Verified row counts:

- Phase 1: 8,400 paired comparison rows
- Phase 2: 840 paired comparison rows

Current generated result artifacts include:

- `results/phase1_results.csv`
- `results/phase1_summary.csv`
- `results/phase1_ci.csv`
- `results/phase2_results.csv`
- `results/phase2_ci.csv`
- `results/delta_heatmap.png`
- `results/success_rate_comparison.png`
- `results/breakeven_line.png`
- `results/policy_pareto.png`

Important interpretation:

The experiments have been run, but the real-world MVP documentation wave did
not rerun the full simulations. The current CSV/PNG outputs remain abstract
representative-network results. A pilot smoke scaffold, evidence tables, small
separated scaffold sample, staged, and full outputs, deterministic sensitivity
screening outputs, SALib Morris scaffold outputs, and generated scaffold-only
figures/tables now exist. The current cache is OSM-derived, but the outputs are
not reviewed, calibrated real-world experiment results.

Current pilot graph scale after adapter filtering:

- Raw cached OSM snapshot: 13,268 nodes and 28,947 edges
- Bus-practical simulator graph: 4,608 nodes and 9,148 edges
- Reduced experiment corridor used by sample/staged/full outputs: 118 nodes
  and 174 edges
- The current reduced corridor is not accepted final-study evidence; the
  future acceptance record is defined by
  `docs/graph_scale_acceptance_schema.md`.
- Full-graph smoke: bus-only and baseline multimodal run on the 4,608-node /
  9,148-edge bus-practical graph without corridor reduction; the current
  `data/validation/full_graph_smoke_manifest.json` records 2 smoke rows and
  remains feasibility evidence only
- Full-graph runtime-readiness packet: 4 rows under
  `data/validation/full_graph_runtime_readiness_packet.csv`; it records the
  smoke scope, missing full-profile full-graph outputs, runtime-scope review,
  and downstream regeneration decisions without closing graph-scale acceptance
- Graph-scale route parity diagnostic: 3 full-vs-reduced comparison rows, all
  pass for baseline shortest-time path preservation on `A -> D`, `A -> S`, and
  `R -> D`; this does not review alternate corridors or close graph-scale
  acceptance
- Graph-scale alternate-route diagnostic: 9 full-graph candidate-route rows,
  with 3 rank-1 paths preserved and 6 alternate route candidates warning as
  omitted from the reduced corridor; this supports graph-scale review but does
  not close graph-scale acceptance
- Graph-scale multi-corridor candidate diagnostic: 9 full-graph
  candidate-route rows, all pass on a 164-node / 246-edge candidate graph;
  this is an upgrade path and still requires graph-scale acceptance before
  final claims
- Graph-scale method review packet: 4 option rows comparing the current
  reduced corridor, small multi-corridor candidate, full-profile
  multi-corridor candidate, and full bus-practical graph;
  this is a decision worksheet and does not close graph-scale acceptance
- Graph-scale result comparison: 819 metric-level rows comparing the current
  full pilot summary against the full-profile multi-corridor candidate
  summary; current status counts are 741 same-or-close rows, 24 candidate
  improvement rows, 24 candidate worsening rows, and 30 non-finite difference
  rows. This is review evidence only and does not close graph-scale acceptance
- Multi-corridor candidate experiment profile: 32 raw rows and 16 summary rows
  now run on the 164-node / 246-edge candidate graph under
  `pilot_multi_corridor_*`; this is separated graph-scale review evidence, not
  calibrated real-world output
- Full-profile multi-corridor candidate experiment profile: 1,890 raw rows
  and 63 summary rows now run on the same 164-node / 246-edge candidate graph
  under `pilot_multi_corridor_full_*`; this is stronger graph-scale review
  evidence, not graph-scale acceptance or calibrated real-world output
- Optional live OSRM snapshot: 3 pass rows after bus-practical road filtering;
  `data/validation/osrm_route_benchmark_manifest.json` records 3 cached
  external-router rows, 0 unpinned rows, 3 retained raw response files, query
  URLs, and checksums for review

## Report State

The report has been simplified into a readable Korean narrative. It intentionally avoids code, command, file-path, and configuration-key details in the report body.

The Word report currently includes:

- A first-page pipeline overview figure generated externally by the user
- Existing result-based figures:
  - Time and resource efficiency comparison
  - Undelivered personnel under disruption severity
  - Executive decision lens summary

The current Word report is:

- `report.docx`

The Korean source is:

- `report_draft.md`

Report generation script:

- `generate_report.py`

Report-specific generated figures:

- `results/report_figures/figure0_pipeline_overview.png`
- `results/report_figures/figure1_time_efficiency_summary.png`
- `results/report_figures/figure2_undelivered_risk.png`
- `results/report_figures/figure3_decision_lens.png`

## Recent Commits

Recent completed commits and pushes:

- `1ba6519 Simplify report narrative`
- `c2d0a38 Add report figures`
- `7aed7a6 Add pipeline overview figure to report`
- `d742cb1 Document realistic simulation roadmap`

The pipeline overview figure was inserted into `report.docx` and pushed in commit `7aed7a6`.
The realistic simulation roadmap, public GitHub repository research, and this status document were added in commit `d742cb1`.

## Current Git Working Tree Notes

After commit `d742cb1`, a documentation and research-context update was made.
Later worker waves added the `src/realworld/` MVP and tests. The broader update
includes:

- `cloned_repo/` source snapshots of public reference repositories with nested
  `.git` metadata removed
- `disrupted_mobilization_resilience_repo_research.md`
- `paper/paper_draft.md`
- `real_world_simulation_implementation_blueprint.md`
- `cloned_repo_manifest.md`
- updates to `agents.md`, `README.md`, `plan.md`, `IMPLEMENTATION_PLAN.md`,
  `repo_survey_results.md`, and this status file
- `docs/realworld_pipeline.md` and `docs/third_party_adaptations.md`
- `data/regions/pilot_region.yaml`, `data/cache/pilot_region_road.graphml`,
  `data/cache/pilot_region_road_manifest.json`,
  `docs/pilot_region_data_card.md`, `scripts/build_pilot_cache.py`,
  `scripts/run_pilot_smoke.py`, `scripts/run_full_graph_smoke.py`,
  `tests/test_realworld_pilot_smoke.py`, and
  `tests/test_realworld_full_graph_smoke.py`
- `data/parameters/`, `data/validation/`, `data/scenarios/`, and the
  corresponding real-world validator modules/tests
- `scripts/run_osrm_route_benchmark.py` and optional OSRM benchmark outputs
  under `data/validation/`
- `src/realworld/pilot_experiments.py`,
  `scripts/run_pilot_experiments.py`, and
  `results/realworld_pilot/` sample/staged/full outputs
- `src/realworld/experiment_strategy_readiness_packet.py`,
  `scripts/write_experiment_strategy_readiness_packet.py`,
  `tests/test_realworld_experiment_strategy_readiness_packet.py`,
  `data/manifests/experiment_strategy_readiness_packet.csv`,
  `data/manifests/experiment_strategy_readiness_manifest.json`, and
  `docs/experiment_strategy_readiness_packet.md`
- `src/realworld/experiment_design_decision_packet.py`,
  `scripts/write_experiment_design_decision_packet.py`,
  `tests/test_realworld_experiment_design_decision_packet.py`,
  `data/manifests/experiment_design_decision_packet.csv`,
  `data/manifests/experiment_design_decision_manifest.json`, and
  `docs/experiment_design_decision_packet.md`
- `src/realworld/figure_table_review_packet.py`,
  `scripts/write_figure_table_review_packet.py`,
  `tests/test_realworld_figure_table_review_packet.py`,
  `data/manifests/figure_table_review_packet.csv`,
  `data/manifests/figure_table_review_manifest.json`, and
  `docs/figure_table_review_packet.md`
- `src/realworld/validation_benchmark_decision_packet.py`,
  `scripts/write_validation_benchmark_decision_packet.py`,
  `tests/test_realworld_validation_benchmark_decision_packet.py`,
  `data/validation/validation_benchmark_decision_packet.csv`,
  `data/validation/validation_benchmark_decision_manifest.json`, and
  `docs/validation_benchmark_decision_packet.md`
- `src/realworld/sensitivity.py`, `scripts/run_sensitivity.py`,
  `data/scenarios/sensitivity_design.csv`, and
  `results/realworld_pilot/` deterministic and Morris sensitivity outputs
- `src/realworld/pilot_figures.py`, `scripts/make_pilot_figures.py`, and
  `results/realworld_pilot/figures/` plus `results/realworld_pilot/tables/`
- `scripts/audit_plan_artifacts.py` and `tests/test_realworld_plan_audit.py`
- `scripts/write_goal_completion_audit.py` and
  `tests/test_realworld_goal_completion_audit.py`
- `docs/analysis_corridor_method_note.md`
- `docs/reproducibility_package.md` and
  `data/manifests/reproducibility_manifest.json`
- `docs/plan_completion_audit.md`
- `docs/current_goal_completion_audit.md`
- `data/manifests/current_goal_completion_audit.json`

If this file is being read after additional edits, run `git status --short`
before committing.

A Word temporary file was observed earlier:

- `~$report.docx`

This is a Word lock/temp file and should not be committed.

## Git Handoff To Another Computer

The intended handoff path is a committed and pushed `main` branch, then a fresh
clone on the other computer:

```powershell
git -c core.longpaths=true clone https://github.com/hyunjun1121/transport-system-sim.git C:\tss
cd C:\tss
py -3.11 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt
```

Use a short checkout path such as `C:\tss` on Windows. The retained
`cloned_repo/` reference snapshots include deep paths that can exceed default
Windows checkout limits when cloned into a long temp directory. If the Python
Launcher does not provide `py -3.11` but Python 3.11+ is installed, use the
available `python -m venv .venv` command.

Before the main agent commits and pushes, run `git status --short` and confirm
that required root Markdown, code, tests, data/manifests, docs, and generated
results are either committed or deliberately excluded. A fresh clone will not
carry uncommitted files, `.venv`, local editor state, or Word lock files.

## Important Conceptual Status

The current simulation is not yet ready to be claimed as an SCI-grade real-world calibrated experiment.

Best current description:

> A meaningful baseline micro-simulation with realistic transport elements, now
> with an OSM-style graph adapter MVP and an offline public-coordinate pilot
> smoke scaffold plus evidence/scenario scaffolding and separated scaffold sample
> staged/full outputs, deterministic screening, SALib Morris scaffold outputs,
> and scaffold-only figures/tables, but still
> without calibrated real-world results.

It includes realistic features such as fleet limits, dispatch, rail headways,
disruption, traffic congestion, transfer time, and censored arrivals. The new
real-world MVP can adapt open-map-style road graphs into the simulator, but it
is not yet calibrated with accepted OSM-derived pilot coordinates, actual
traffic volumes, actual rail operation constraints, or validated mobilization
assumptions.

## Current Scientific Position

The current result should be interpreted as:

> Under the current representative network and operating assumptions, bus-only transport tends to be faster, while multimodal transport can show resource-efficiency advantages but is sensitive to road access and last-mile bottlenecks.

It should not be interpreted as:

> Bus-only transport is always faster in the real Seoul-to-forward-area setting.

## Main Limitations

Current limitations:

- Current generated results use an abstract and small network.
- The real-world MVP is an adapter, validation path, and offline pilot smoke
  scaffold with evidence/scenario scaffolding and small sample/screening
  outputs plus scaffold-only figures/tables, not a completed OSM/Seoul
  calibrated case.
- Road link times and capacities are representative assumptions.
- Failure probabilities and capacity reductions are sensitivity assumptions.
- Rail is simplified and mostly treated as operationally available.
- Actual station access, platform operations, and large-scale transfer handling are not fully calibrated.
- Vehicle availability and driver constraints are not validated against real mobilization conditions.
- Current results are conditional comparative outputs, not operational forecasts.

## Realism Upgrade Direction

The first implementation step of the realism roadmap now exists in
`src/realworld/`. It covers region specs, OSM-style edge normalization,
GraphML caching, zone connectors, simulator graph adaptation, and readiness
validation. A first offline `songpa_public_demo` pilot scaffold now exercises
that path. Parameter-source tables, route plausibility checks, deterministic
structured disruption scenarios, policy alternatives, sample/staged/full pilot
profiles and outputs, deterministic screening, and SALib Morris scaffold
screening now exist.
The next step is to review the current Overpass/OSM-derived pilot snapshot,
review staged/full pilot outputs, and decide whether the reduced-corridor graph
is defensible for the paper claim. The current repository documents that
reduced corridor as a scaffold/performance abstraction, not final-study
evidence.

A planning document was added:

- `realistic_simulation_requirements.md`

It summarizes what is needed to move toward a realistic simulation:

- Real or quasi-real road/rail network
- Reusable regional pipeline for locations beyond Songpa-gu
- Public map and open-source data pipeline
- Calibrated vehicle, road, rail, transfer, and disruption assumptions
- Sensitive-location abstraction
- Zone-level OD modeling
- Sensitivity analysis
- Reproducibility package
- SCI-level minimum criteria

Key idea:

> Public map data helps create a reusable and more realistic starting point, but public maps alone do not make the simulation real. Realism comes from adding calibrated assumptions, constraints, validation, and uncertainty analysis on top of public networks.

## Public GitHub Repository Research

A new research synthesis document was added:

- `public_github_repo_research.md`

This was produced after running multiple GPT-5.5 xhigh subagents in parallel, each responsible for one feature area.

Feature areas researched:

1. Road network extraction and reusable regional pipeline
2. Traffic assignment, calibration, and routing
3. Rail, GTFS, and multimodal routing
4. Fleet dispatch, queueing, and discrete-event modeling
5. Scenario management, sensitivity, and reproducibility
6. Geospatial anonymization, regional inputs, and OD generation

## Disrupted Resilience Repository Research

A second repository research document was added:

- `disrupted_mobilization_resilience_repo_research.md`

This document focuses specifically on the reframed research direction:

> disrupted regional mobilization transport resilience framework

It was produced with six GPT-5.5 high subagents in parallel. The subagents
searched public GitHub repositories for:

1. Transport network resilience metrics and critical-link analysis
2. Disruption scenario generation and hazard-overlay modeling
3. Emergency evacuation, mass movement, and multimodal simulation engines
4. Constrained fleet logistics and contingency routing
5. Public-data validation and calibration
6. Resilience visualization, reproducibility, and decision-support reporting

Main conclusion:

> Keep the current Python micro-simulation as the core evaluator, and add
> external repositories as data, validation, benchmark, optimization, and
> reporting layers around it.

Recommended immediate additions for this new framing:

- `NetworkX` and `OSMnx` for real road networks and critical-link metrics
- `snail` for hazard or disruption raster overlay onto transport edges
- `gtfs-validator` and `gtfs_kit` for public transit feed validation
- `Frictionless` for result and benchmark data package validation

Recommended evaluation targets:

- `r5py` for multimodal accessibility benchmarking
- `routingpy` with OSRM or Valhalla for road travel-time plausibility checks
- `OR-Tools` or `PyVRP` for optimizer-generated fleet and contingency policies
- `UXsim` for a Python-native road-congestion benchmark
- `Streamlit`, `Papermill`, and `Quarto` for decision-support and reproducible
  paper packaging

Recommended benchmark/reference-only tools:

- SUMO
- MATSim
- OpenTripPlanner
- R5
- Valhalla
- AequilibraE
- Path4GMNS
- open-gira
- transcrit
- pyincore
- CLIMADA

## Recommended Open-Source Stack

Recommended first-stage stack:

- OSMnx
- GeoPandas
- Shapely
- H3 / h3-py
- Pyrosm
- partridge or gtfs_kit
- SALib

Recommended later-stage candidates:

- Path4GMNS
- AequilibraE
- routingpy + Valhalla
- r5py
- scikit-mobility
- Ciw

Useful as design references:

- OpenMines
- FleetPy
- peartree
- street-network-models

Defer as first-pass core dependencies:

- SUMO
- MATSim
- OpenTripPlanner
- MOTIS
- DTALite
- OSM2GMNS
- eFLIPS tools

## Implemented Real-World MVP Validation

Known real-world MVP checks that passed in the current validation pass:

- `.\.venv\Scripts\python tests\test_realworld_types.py`
- `.\.venv\Scripts\python tests\test_realworld_attributes.py`
- `.\.venv\Scripts\python tests\test_realworld_osm_network.py`
- `.\.venv\Scripts\python tests\test_realworld_adapter.py`
- `.\.venv\Scripts\python tests\test_realworld_validation.py`
- `.\.venv\Scripts\python tests\test_realworld_end_to_end.py`
- `.\.venv\Scripts\python tests\test_realworld_pilot_smoke.py`
- `.\.venv\Scripts\python tests\test_realworld_full_graph_smoke.py`
- `.\.venv\Scripts\python tests\test_realworld_rail_evidence.py`
- `.\.venv\Scripts\python tests\test_realworld_rail_evidence_review_packet.py`
- `.\.venv\Scripts\python tests\test_realworld_rail_timing_request_packet.py`
- `.\.venv\Scripts\python tests\test_realworld_parameters.py`
- `.\.venv\Scripts\python tests\test_realworld_graph_scale_acceptance.py`
- `.\.venv\Scripts\python tests\test_realworld_graph_scale_diagnostics.py`
- `.\.venv\Scripts\python tests\test_realworld_graph_scale_review.py`
- `.\.venv\Scripts\python tests\test_realworld_validation_acceptance.py`
- `.\.venv\Scripts\python tests\test_realworld_parameter_acceptance.py`
- `.\.venv\Scripts\python tests\test_realworld_parameter_audit.py`
- `.\.venv\Scripts\python tests\test_realworld_parameter_review_packet.py`
- `.\.venv\Scripts\python tests\test_realworld_pilot_acceptance.py`
- `.\.venv\Scripts\python tests\test_realworld_provenance_acceptance.py`
- `.\.venv\Scripts\python tests\test_realworld_manuscript_acceptance.py`
- `.\.venv\Scripts\python tests\test_realworld_claim_alignment_review_packet.py`
- `.\.venv\Scripts\python tests\test_realworld_reproducibility_acceptance.py`
- `.\.venv\Scripts\python tests\test_realworld_reproducibility_review_packet.py`
- `.\.venv\Scripts\python tests\test_realworld_reproducibility_smoke.py`
- `.\.venv\Scripts\python tests\test_realworld_final_audit_acceptance.py`
- `.\.venv\Scripts\python tests\test_realworld_road_evidence.py`
- `.\.venv\Scripts\python tests\test_realworld_road_evidence_diagnostics.py`
- `.\.venv\Scripts\python tests\test_realworld_road_capacity_evidence.py`
- `.\.venv\Scripts\python tests\test_realworld_road_speed_evidence.py`
- `.\.venv\Scripts\python tests\test_realworld_road_evidence_review_packet.py`
- `.\.venv\Scripts\python tests\test_realworld_road_evidence_request_packet.py`
- `.\.venv\Scripts\python tests\test_realworld_road_overrides.py`
- `.\.venv\Scripts\python tests\test_realworld_road_override_template.py`
- `.\.venv\Scripts\python tests\test_realworld_road_override_audit.py`
- `.\.venv\Scripts\python tests\test_realworld_rail_station_binding.py`
- `.\.venv\Scripts\python tests\test_realworld_rail_station_cache.py`
- `.\.venv\Scripts\python tests\test_realworld_rail_timetable.py`
- `.\.venv\Scripts\python tests\test_realworld_rail_timetable_api.py`
- `.\.venv\Scripts\python tests\test_realworld_rail_shortest_path.py`
- `.\.venv\Scripts\python tests\test_realworld_rail_shortest_path_api.py`
- `.\.venv\Scripts\python tests\test_realworld_publication_readiness.py`
- `.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py`
- `.\.venv\Scripts\python tests\test_realworld_plausibility.py`
- `.\.venv\Scripts\python tests\test_realworld_accessibility.py`
- `.\.venv\Scripts\python tests\test_realworld_disruption_scenarios.py`
- `.\.venv\Scripts\python tests\test_realworld_policy_alternatives.py`
- `.\.venv\Scripts\python tests\test_realworld_pilot_experiments.py`
- `.\.venv\Scripts\python tests\test_realworld_experiment_acceptance.py`
- `.\.venv\Scripts\python tests\test_realworld_experiment_package_review_packet.py`
- `.\.venv\Scripts\python tests\test_realworld_experiment_strategy_readiness_packet.py`
- `.\.venv\Scripts\python tests\test_realworld_experiment_design_decision_packet.py`
- `.\.venv\Scripts\python tests\test_realworld_figure_table_review_packet.py`
- `.\.venv\Scripts\python tests\test_realworld_sensitivity.py`
- `.\.venv\Scripts\python tests\test_realworld_sensitivity_acceptance.py`
- `.\.venv\Scripts\python tests\test_realworld_sensitivity_review_packet.py`
- `.\.venv\Scripts\python tests\test_realworld_sensitivity_strategy_readiness_packet.py`
- `.\.venv\Scripts\python tests\test_realworld_osrm_snapshot_manifest.py`
- `.\.venv\Scripts\python tests\test_realworld_validation_review_packet.py`
- `.\.venv\Scripts\python tests\test_realworld_validation_strategy_readiness_packet.py`
- `.\.venv\Scripts\python tests\test_realworld_route_road_evidence_exposure.py`
- `.\.venv\Scripts\python scripts\run_pilot_smoke.py`
- `.\.venv\Scripts\python scripts\run_full_graph_smoke.py`
- `.\.venv\Scripts\python scripts\run_graph_scale_diagnostics.py`
- `.\.venv\Scripts\python scripts\write_graph_scale_review_packet.py`
- `.\.venv\Scripts\python scripts\write_graph_scale_strategy_readiness_packet.py`
- `.\.venv\Scripts\python scripts\write_graph_scale_result_comparison.py`
- `.\.venv\Scripts\python scripts\audit_rail_evidence.py`
- `.\.venv\Scripts\python scripts\write_rail_evidence_review_packet.py`
- `.\.venv\Scripts\python scripts\write_rail_timing_source_request_packet.py`
- `.\.venv\Scripts\python scripts\audit_rail_station_bindings.py`
- `.\.venv\Scripts\python scripts\audit_parameter_evidence.py`
- `.\.venv\Scripts\python scripts\write_parameter_review_packet.py`
- `.\.venv\Scripts\python scripts\write_parameter_evidence_source_request_packet.py`
- `.\.venv\Scripts\python scripts\audit_road_evidence.py`
- `.\.venv\Scripts\python scripts\audit_road_evidence_diagnostics.py`
- `.\.venv\Scripts\python scripts\write_road_capacity_evidence.py`
- `.\.venv\Scripts\python scripts\write_road_speed_evidence.py`
- `.\.venv\Scripts\python scripts\write_road_evidence_review_packet.py`
- `.\.venv\Scripts\python scripts\write_road_evidence_source_request_packet.py`
- `.\.venv\Scripts\python scripts\audit_source_provenance.py`
- `.\.venv\Scripts\python scripts\audit_road_overrides.py`
- `.\.venv\Scripts\python scripts\audit_publication_readiness.py`
- `.\.venv\Scripts\python scripts\audit_final_study_readiness.py`
- `.\.venv\Scripts\python scripts\run_plausibility_validation.py`
- `.\.venv\Scripts\python scripts\run_accessibility_loss_analysis.py`
- `.\.venv\Scripts\python scripts\write_osrm_snapshot_manifest.py`
- `.\.venv\Scripts\python scripts\write_route_road_evidence_exposure.py`
- `.\.venv\Scripts\python scripts\run_pilot_experiments.py --sample`
- `.\.venv\Scripts\python scripts\run_pilot_experiments.py --staged`
- `.\.venv\Scripts\python scripts\run_pilot_experiments.py --multi-corridor`
- `.\.venv\Scripts\python scripts\run_pilot_experiments.py --multi-corridor-full`
- `.\.venv\Scripts\python scripts\run_pilot_experiments.py --full`
- `.\.venv\Scripts\python scripts\run_sensitivity.py --sample`
- `.\.venv\Scripts\python scripts\run_sensitivity.py --method morris --all`
- `.\.venv\Scripts\python scripts\audit_sensitivity_diagnostics.py`
- `.\.venv\Scripts\python scripts\write_sensitivity_review_packet.py`
- `.\.venv\Scripts\python scripts\write_sensitivity_strategy_readiness_packet.py`
- `.\.venv\Scripts\python scripts\write_validation_review_packet.py`
- `.\.venv\Scripts\python scripts\write_validation_strategy_readiness_packet.py`
- `.\.venv\Scripts\python scripts\write_experiment_strategy_readiness_packet.py`
- `.\.venv\Scripts\python scripts\write_experiment_design_decision_packet.py`
- `.\.venv\Scripts\python scripts\write_figure_table_review_packet.py`
- `.\.venv\Scripts\python scripts\write_reproducibility_review_packet.py`
- `.\.venv\Scripts\python scripts\run_reproducibility_smoke.py`
- `.\.venv\Scripts\python scripts\run_acceptance_audit.py`
- `.\.venv\Scripts\python scripts\make_pilot_statistics.py`
- `.\.venv\Scripts\python scripts\make_pilot_statistics.py --input results\realworld_pilot\pilot_multi_corridor_results.csv --source-manifest results\realworld_pilot\pilot_multi_corridor_manifest.json --output-prefix pilot_multi_corridor`
- `.\.venv\Scripts\python scripts\make_pilot_statistics.py --input results\realworld_pilot\pilot_multi_corridor_full_results.csv --source-manifest results\realworld_pilot\pilot_multi_corridor_full_manifest.json --output-prefix pilot_multi_corridor_full`
- `.\.venv\Scripts\python scripts\make_pilot_figures.py`
- `.\.venv\Scripts\python scripts\audit_plan_artifacts.py`
- `.\.venv\Scripts\python tests\test_scenario.py`

These tests and default scripts are offline. Live OSM extraction and
`.\.venv\Scripts\python scripts\run_osrm_route_benchmark.py` are optional manual
functionality and must not be required by default tests.

## Recommended Technical Roadmap

Stage 1: Build a reusable regional network prototype. The offline adapter MVP
and first pilot smoke scaffold are implemented; the remaining work is
pilot-region OSM snapshot review and stronger validation.

- Use OSMnx, GeoPandas, Shapely, and NetworkX.
- Define a region registry.
- Review or replace the current cache with one accepted pilot region road
  network snapshot.
- Store GraphML/GPKG outputs and snapshot metadata.
- Validate graph connectivity and required edge attributes.

Stage 2: Add regional reproducibility and sensitive-location abstraction.

- Use Pyrosm and pinned South Korea OSM PBF snapshots.
- Use H3 or zone aggregation.
- Store zone IDs and OD counts rather than exact sensitive coordinates.

Stage 3: Add real rail/GTFS inputs.

- Use partridge or gtfs_kit.
- Extract stations, stop times, trips, frequencies, and headways.
- Optionally prototype peartree for GTFS-to-NetworkX conversion.
- Use r5py only as an external benchmark path.

Stage 4: Add assignment and calibration.

- Add a NetworkX-to-GMNS adapter.
- Use Path4GMNS for assignment/ODME experiments.
- Keep AequilibraE as a mature alternative for larger traffic assignment needs.

Stage 5: Extend formal sensitivity analysis.

- Use the implemented SALib Morris path on the current full policy/scenario
  scaffold and review the resulting parameter rankings conservatively.
- Analyze completion time, completion rate, censored personnel, and resource efficiency.

Stage 6: Improve fleet and queue semantics.

- Use Ciw, OpenMines, and FleetPy as references.
- Add passenger state logs, per-vehicle task logs, queue wait accounting, boarding/alighting service times, and driver/fleet shortage scenarios.

## SCI-Level Research Development Requirements

To develop this into an SCI-grade paper, the project needs:

- A sharply defined research question
- Real or quasi-real regional road and rail network
- Defensible input-parameter table
- Public-data, literature, or expert-judgment basis for key assumptions
- Multiple network and disruption scenarios
- Formal sensitivity analysis
- Confidence intervals or comparable uncertainty summaries
- Tail-risk and censored-arrival interpretation
- Reproducibility package
- Clear separation between operational claims and conditional simulation findings

Potential research question framing:

- Under what network disruption and resource constraints does rail-bus multimodal transport outperform bus-only transport?
- Which bottlenecks most reduce multimodal transport resilience?
- How do last-mile redundancy, transfer delay, and fleet shortage affect completion probability?
- Can a region-reusable open-map pipeline support robust reserve-force transport planning under uncertainty?

## High-IF SCI Framing Assessment

The idea can become a research paper, but the current version should not be framed as ready for a high-impact SCI journal. The current strongest assessment is:

> The project has a promising research seed and a non-trivial simulator, but the claim structure is still weaker than the evidence standard expected by high-impact transportation, logistics, reliability, or system-safety journals.

The main weakness is not the number of simulation runs. The main weakness is real-world alignment:

- The current network is representative and abstract.
- Major parameters are not yet supported by a source table.
- Rail availability, station access, transfer capacity, and last-mile reliability are not calibrated.
- Validation is not yet strong enough for operational or policy claims.
- The contribution is currently mixed between simulator, case result, and methodology.

The best high-impact framing is not:

> A wartime reserve-force transport simulator proves which mode is better.

The better framing is:

> An open-data, region-reusable decision framework that combines geospatial networks and discrete-event micro-simulation to identify when rail-bus multimodal mobilization transport becomes resilient or fragile under network degradation and constrained fleet operations.

This framing reduces military specificity, improves generalizability, and aligns the work with resilience, disrupted logistics, emergency mobilization, and multimodal network reliability.

## Strongest Paper Claim Direction

The most promising research question is:

> Under which disruption and resource constraints does rail-bus multimodal transport outperform bus-only mobilization transport?

A strong paper should produce conditional decision rules, such as:

- Multimodal transport becomes competitive only when rail access and last-mile redundancy remain available.
- Bus-only transport can dominate travel time under direct-road access but becomes vulnerable under fleet shortage or major corridor disruption.
- Transfer delay and last-mile bottlenecks can erase the theoretical capacity benefit of rail.
- Completion probability, censored personnel, and tail-risk are more decision-relevant than raw mean makespan.

The final claim should be about regimes, thresholds, and bottlenecks, not absolute superiority.

## Three-Month Research Upgrade Plan

Month 1: Realistic network prototype.

- Build an OSMnx-based road network prototype for one non-sensitive pilot region.
- Represent sensitive destinations as zones or synthetic nodes.
- Review a GTFS feed for the pilot where available and run the cached
  static-GTFS derivation path; use partridge or gtfs_kit later only if broader
  feed filtering is needed.
- Define the region input schema and network persistence format.

Month 2: Calibration and parameter evidence.

- Run the existing simulator on the new quasi-real network.
- Create a parameter-source table.
- Classify each value as public-data, literature, expert-assumption, or sensitivity-only.
- Add sanity checks for road travel time, rail headway, bus turnaround, transfer time, and queue behavior.

Month 3: Scientific analysis package.

- Extend SALib-based sensitivity analysis to accepted staged/full pilot outputs.
- Expand policy scenarios: last-mile redundancy, rail delay, feeder capacity expansion, fleet shortage, adaptive routing, and staggered dispatch.
- Report completion probability, censored personnel, 95th-percentile arrival, bottleneck attribution, and resource efficiency.
- Prepare a reproducibility package with input snapshots, seeds, scenario tables, and result-generation steps.

## Immediate Next Steps

Suggested next work:

1. Review the current `songpa_public_demo` Overpass/OSM-derived GraphML
   snapshot, or replace it with a better accepted non-sensitive snapshot.
2. Update the pilot cache manifest with source, date, bbox, tooling, and
   attribution metadata.
3. Compare route plausibility rows with an external benchmark such as OSRM,
   Valhalla, routingpy, R5, OpenTripPlanner, or UXsim where feasible. A first
  optional OSRM snapshot exists and currently has 3 pass rows after
  bus-practical road filtering, but it remains plausibility evidence rather
  than calibration.
4. Review the graph-scale route parity, alternate-route, and multi-corridor
   candidate diagnostics. Decide whether the current 6 alternate-route warning
   rows are acceptable under a documented corridor-selection rule, whether to
   regenerate on the 164-node / 246-edge candidate graph, or whether full-graph
   runtime or a multi-corridor ensemble is needed before acceptance. Use
   `data/validation/graph_scale_review_packet.csv`,
   `data/validation/full_graph_runtime_readiness_packet.csv`, and
   `data/validation/graph_scale_strategy_readiness_packet.csv` as the
   consolidated worksheets for this decision.
5. Define how exact sensitive points will be replaced by administrative zones,
   H3/admin-grid cells, or synthetic centroids.
6. Use the cached static-GTFS derivation path where a reviewed feed is
   available, or strengthen the documented rail-assumption table where GTFS is
   incomplete.
7. Broaden the current sample pilot runner into the accepted scenario, policy,
   and seed design.
8. Review the current SALib Morris scaffold outputs against the staged/full
   profile, and add Sobol only if compute budget and interpretation justify it.
9. Regenerate pilot-region figures, result tables, and manuscript/report
   updates only after accepted validation and full experiment outputs exist.

## Files Added In Recent Roadmap Work

- `realistic_simulation_requirements.md`
- `public_github_repo_research.md`
- `disrupted_mobilization_resilience_repo_research.md`
- `paper/paper_draft.md`
- `real_world_simulation_implementation_blueprint.md`
- `cloned_repo_manifest.md`
- `status.md`
- `docs/realworld_pipeline.md`
- `docs/third_party_adaptations.md`
- `data/regions/pilot_region.yaml`
- `data/cache/pilot_region_road.graphml`
- `data/cache/pilot_region_road_manifest.json`
- `docs/pilot_region_data_card.md`
- `docs/analysis_corridor_method_note.md`
- `scripts/build_pilot_cache.py`
- `scripts/run_pilot_smoke.py`
- `tests/test_realworld_pilot_smoke.py`
- `data/parameters/parameter_sources.csv`
- `data/parameters/parameter_evidence_review_packet.csv`
- `data/parameters/parameter_evidence_review_manifest.json`
- `data/parameters/parameter_evidence_source_request_packet.csv`
- `data/parameters/parameter_evidence_source_request_manifest.json`
- `data/parameters/rail_assumptions.csv`
- `data/parameters/fleet_assumptions.csv`
- `data/parameters/road_class_overrides_draft.csv`
- `data/parameters/road_capacity_evidence_candidates.csv`
- `data/parameters/road_capacity_evidence_manifest.json`
- `data/parameters/road_speed_evidence_candidates.csv`
- `data/parameters/road_speed_evidence_manifest.json`
- `data/parameters/road_evidence_review_packet.csv`
- `data/parameters/road_evidence_review_manifest.json`
- `data/road/road_evidence_source_request_packet.csv`
- `data/road/road_evidence_source_request_manifest.json`
- `data/parameters/rail_service_evidence.csv`
- `data/rail/pilot_station_binding_cache.csv`
- `data/parameters/rail_station_bindings.csv`
- `data/parameters/rail_evidence_review_packet.csv`
- `data/parameters/rail_evidence_review_manifest.json`
- `data/rail/rail_timing_source_request_packet.csv`
- `data/rail/rail_timing_source_request_manifest.json`
- `data/validation/route_plausibility.csv`
- `data/validation/external_route_benchmarks.csv`
- `data/validation/external_route_benchmarks_osrm.csv`
- `data/validation/osrm_route_benchmark_summary.md`
- `data/validation/graph_scale_route_comparison.csv`
- `data/validation/graph_scale_route_comparison_summary.md`
- `data/validation/graph_scale_alternate_routes.csv`
- `data/validation/graph_scale_alternate_routes_summary.md`
- `data/validation/graph_scale_multi_corridor_routes.csv`
- `data/validation/graph_scale_multi_corridor_routes_summary.md`
- `data/validation/graph_scale_review_packet.csv`
- `data/validation/graph_scale_review_manifest.json`
- `data/validation/graph_scale_result_comparison.csv`
- `data/validation/graph_scale_result_comparison_manifest.json`
- `data/validation/validation_summary.md`
- `data/manifests/experiment_design_decision_packet.csv`
- `data/manifests/experiment_design_decision_manifest.json`
- `docs/experiment_design_decision_packet.md`
- `data/validation/validation_benchmark_decision_packet.csv`
- `data/validation/validation_benchmark_decision_manifest.json`
- `docs/validation_benchmark_decision_packet.md`
- `data/scenarios/disruption_scenarios.csv`
- `data/scenarios/policy_alternatives.csv`
- `src/realworld/parameters.py`
- `src/realworld/graph_scale_acceptance.py`
- `src/realworld/validation_acceptance.py`
- `src/realworld/parameter_acceptance.py`
- `src/realworld/parameter_audit.py`
- `src/realworld/parameter_review_packet.py`
- `src/realworld/pilot_acceptance.py`
- `src/realworld/road_evidence.py`
- `src/realworld/road_evidence_diagnostics.py`
- `src/realworld/road_capacity_evidence.py`
- `src/realworld/road_speed_evidence.py`
- `src/realworld/road_evidence_review_packet.py`
- `src/realworld/road_evidence_request_packet.py`
- `src/realworld/road_overrides.py`
- `src/realworld/road_override_template.py`
- `src/realworld/road_override_audit.py`
- `src/realworld/rail_timetable.py`
- `src/realworld/rail_timetable_api.py`
- `src/realworld/rail_gtfs.py`
- `src/realworld/rail_shortest_path.py`
- `src/realworld/rail_shortest_path_api.py`
- `src/realworld/rail_station_binding.py`
- `src/realworld/rail_station_cache.py`
- `src/realworld/rail_evidence_review_packet.py`
- `src/realworld/rail_timing_request_packet.py`
- `src/realworld/publication_readiness.py`
- `src/realworld/final_study_readiness.py`
- `src/realworld/plausibility.py`
- `src/realworld/disruption_scenarios.py`
- `src/realworld/policy_alternatives.py`
- `src/realworld/rail_evidence.py`
- `tests/test_realworld_parameters.py`
- `tests/test_realworld_graph_scale_acceptance.py`
- `tests/test_realworld_graph_scale_diagnostics.py`
- `tests/test_realworld_graph_scale_review.py`
- `tests/test_realworld_validation_acceptance.py`
- `tests/test_realworld_parameter_acceptance.py`
- `tests/test_realworld_parameter_audit.py`
- `tests/test_realworld_parameter_review_packet.py`
- `tests/test_realworld_pilot_acceptance.py`
- `tests/test_realworld_road_evidence.py`
- `tests/test_realworld_road_evidence_diagnostics.py`
- `tests/test_realworld_road_capacity_evidence.py`
- `tests/test_realworld_road_speed_evidence.py`
- `tests/test_realworld_road_evidence_review_packet.py`
- `tests/test_realworld_road_evidence_request_packet.py`
- `tests/test_realworld_road_overrides.py`
- `tests/test_realworld_road_override_template.py`
- `tests/test_realworld_road_override_audit.py`
- `tests/test_realworld_rail_timetable.py`
- `tests/test_realworld_rail_timetable_api.py`
- `tests/test_realworld_rail_gtfs.py`
- `tests/test_realworld_rail_shortest_path.py`
- `tests/test_realworld_rail_shortest_path_api.py`
- `tests/test_realworld_rail_station_binding.py`
- `tests/test_realworld_rail_station_cache.py`
- `tests/test_realworld_rail_evidence_review_packet.py`
- `tests/test_realworld_rail_timing_request_packet.py`
- `tests/test_realworld_publication_readiness.py`
- `tests/test_realworld_final_study_readiness.py`
- `tests/test_realworld_rail_evidence.py`
- `tests/test_realworld_plausibility.py`
- `tests/test_realworld_disruption_scenarios.py`
- `tests/test_realworld_policy_alternatives.py`
- `scripts/write_road_class_override_template.py`
- `scripts/write_parameter_review_packet.py`
- `scripts/write_parameter_evidence_source_request_packet.py`
- `scripts/write_road_capacity_evidence.py`
- `scripts/write_road_speed_evidence.py`
- `scripts/derive_rail_headway_evidence.py`
- `scripts/fetch_rail_timetable_cache.py`
- `scripts/derive_rail_gtfs_evidence.py`
- `scripts/derive_rail_shortest_path_evidence.py`
- `scripts/fetch_rail_shortest_path_cache.py`
- `docs/rail_shortest_path_cache_schema.md`
- `docs/rail_gtfs_cache_schema.md`
- `src/realworld/pilot_experiments.py`
- `src/realworld/experiment_acceptance.py`
- `src/realworld/experiment_design_decision_packet.py`
- `src/realworld/provenance_acceptance.py`
- `src/realworld/source_provenance.py`
- `src/realworld/manuscript_acceptance.py`
- `src/realworld/figure_table_review_packet.py`
- `src/realworld/reproducibility_acceptance.py`
- `src/realworld/reproducibility_review_packet.py`
- `src/realworld/reproducibility_smoke.py`
- `src/realworld/formal_evidence_path_audit.py`
- `src/realworld/final_audit_acceptance.py`
- `src/realworld/graph_scale_diagnostics.py`
- `src/realworld/graph_scale_review.py`
- `src/realworld/graph_scale_result_comparison.py`
- `scripts/run_pilot_experiments.py`
- `scripts/write_experiment_design_decision_packet.py`
- `scripts/write_figure_table_review_packet.py`
- `scripts/run_graph_scale_diagnostics.py`
- `scripts/write_graph_scale_review_packet.py`
- `scripts/write_graph_scale_result_comparison.py`
- `tests/test_realworld_pilot_experiments.py`
- `tests/test_realworld_experiment_acceptance.py`
- `tests/test_realworld_experiment_design_decision_packet.py`
- `tests/test_realworld_figure_table_review_packet.py`
- `tests/test_realworld_provenance_acceptance.py`
- `tests/test_realworld_source_provenance.py`
- `tests/test_realworld_manuscript_acceptance.py`
- `tests/test_realworld_reproducibility_acceptance.py`
- `tests/test_realworld_reproducibility_review_packet.py`
- `tests/test_realworld_reproducibility_smoke.py`
- `tests/test_realworld_formal_evidence_path_audit.py`
- `tests/test_realworld_final_audit_acceptance.py`
- `data/manifests/figure_table_review_packet.csv`
- `data/manifests/figure_table_review_manifest.json`
- `docs/figure_table_review_packet.md`
- `results/realworld_pilot/pilot_sample_results.csv`
- `results/realworld_pilot/pilot_sample_summary.csv`
- `results/realworld_pilot/pilot_result_manifest.json`
- `results/realworld_pilot/pilot_multi_corridor_results.csv`
- `results/realworld_pilot/pilot_multi_corridor_summary.csv`
- `results/realworld_pilot/pilot_multi_corridor_manifest.json`
- `results/realworld_pilot/pilot_multi_corridor_full_results.csv`
- `results/realworld_pilot/pilot_multi_corridor_full_summary.csv`
- `results/realworld_pilot/pilot_multi_corridor_full_manifest.json`
- `results/realworld_pilot/tables/pilot_full_metric_ci.csv`
- `results/realworld_pilot/tables/pilot_full_paired_delta_ci.csv`
- `results/realworld_pilot/tables/pilot_full_statistics_manifest.json`
- `results/realworld_pilot/tables/pilot_multi_corridor_metric_ci.csv`
- `results/realworld_pilot/tables/pilot_multi_corridor_paired_delta_ci.csv`
- `results/realworld_pilot/tables/pilot_multi_corridor_statistics_manifest.json`
- `results/realworld_pilot/tables/pilot_multi_corridor_full_metric_ci.csv`
- `results/realworld_pilot/tables/pilot_multi_corridor_full_paired_delta_ci.csv`
- `results/realworld_pilot/tables/pilot_multi_corridor_full_statistics_manifest.json`
- `data/scenarios/sensitivity_design.csv`
- `src/realworld/sensitivity.py`
- `src/realworld/sensitivity_acceptance.py`
- `src/realworld/sensitivity_diagnostics.py`
- `src/realworld/sensitivity_review_packet.py`
- `src/realworld/graph_scale_strategy_readiness_packet.py`
- `src/realworld/validation_review_packet.py`
- `src/realworld/validation_strategy_readiness_packet.py`
- `src/realworld/route_road_evidence_exposure.py`
- `scripts/run_sensitivity.py`
- `scripts/audit_sensitivity_diagnostics.py`
- `scripts/write_sensitivity_review_packet.py`
- `scripts/write_graph_scale_strategy_readiness_packet.py`
- `src/realworld/osrm_snapshot_manifest.py`
- `scripts/write_osrm_snapshot_manifest.py`
- `scripts/write_validation_review_packet.py`
- `scripts/write_validation_strategy_readiness_packet.py`
- `scripts/write_reproducibility_review_packet.py`
- `scripts/run_reproducibility_smoke.py`
- `scripts/audit_formal_evidence_paths.py`
- `scripts/write_route_road_evidence_exposure.py`
- `tests/test_realworld_sensitivity.py`
- `tests/test_realworld_sensitivity_acceptance.py`
- `tests/test_realworld_sensitivity_diagnostics.py`
- `tests/test_realworld_sensitivity_review_packet.py`
- `tests/test_realworld_graph_scale_strategy_readiness_packet.py`
- `tests/test_realworld_osrm_snapshot_manifest.py`
- `tests/test_realworld_validation_review_packet.py`
- `tests/test_realworld_validation_strategy_readiness_packet.py`
- `tests/test_realworld_route_road_evidence_exposure.py`
- `results/realworld_pilot/sensitivity_results.csv`
- `results/realworld_pilot/sensitivity_summary.csv`
- `results/realworld_pilot/sensitivity_manifest.json`
- `results/realworld_pilot/morris_results.csv`
- `results/realworld_pilot/morris_summary.csv`
- `results/realworld_pilot/morris_manifest.json`
- `data/validation/sensitivity_review_packet.csv`
- `data/validation/sensitivity_review_manifest.json`
- `data/validation/graph_scale_strategy_readiness_packet.csv`
- `data/validation/graph_scale_strategy_readiness_manifest.json`
- `data/validation/validation_review_packet.csv`
- `data/validation/validation_strategy_readiness_packet.csv`
- `data/validation/validation_strategy_readiness_manifest.json`
- `data/validation/reproducibility_review_packet.csv`
- `data/validation/reproducibility_smoke_manifest.json`
- `data/validation/reproducibility_smoke_log.jsonl`
- `data/manifests/formal_evidence_path_audit.json`
- `data/validation/validation_review_manifest.json`
- `docs/reproducibility_smoke.md`
- `docs/formal_evidence_path_audit.md`
- `data/validation/canonical_route_road_evidence_exposure.csv`
- `data/validation/canonical_route_road_evidence_exposure_manifest.json`
- `src/realworld/pilot_figures.py`
- `scripts/make_pilot_figures.py`
- `tests/test_realworld_pilot_figures.py`
- `scripts/audit_plan_artifacts.py`
- `scripts/write_goal_completion_audit.py`
- `scripts/audit_final_study_readiness.py`
- `scripts/audit_parameter_evidence.py`
- `scripts/write_parameter_review_packet.py`
- `scripts/audit_road_evidence.py`
- `scripts/audit_road_evidence_diagnostics.py`
- `scripts/write_road_capacity_evidence.py`
- `scripts/write_road_speed_evidence.py`
- `scripts/write_road_evidence_review_packet.py`
- `scripts/write_road_evidence_source_request_packet.py`
- `scripts/write_rail_evidence_review_packet.py`
- `scripts/write_rail_timing_source_request_packet.py`
- `tests/test_realworld_plan_audit.py`
- `results/realworld_pilot/figures/`
- `results/realworld_pilot/tables/`
- `docs/reproducibility_package.md`
- `docs/plan_completion_audit.md`
- `docs/current_goal_completion_audit.md`
- `data/manifests/current_goal_completion_audit.json`
- `docs/analysis_corridor_method_note.md`
- `docs/graph_scale_diagnostics.md`
- `docs/graph_scale_review_packet.md`
- `docs/pilot_acceptance_schema.md`
- `docs/graph_scale_acceptance_schema.md`
- `docs/validation_acceptance_schema.md`
- `docs/sensitivity_acceptance_schema.md`
- `docs/experiment_acceptance_schema.md`
- `docs/provenance_acceptance_schema.md`
- `docs/source_provenance_manifest.md`
- `docs/road_evidence_diagnostics.md`
- `docs/road_evidence_review_packet.md`
- `docs/road_evidence_source_request_packet.md`
- `docs/parameter_evidence_source_request_packet.md`
- `docs/rail_evidence_review_packet.md`
- `docs/rail_timing_source_request_packet.md`
- `docs/manuscript_acceptance_schema.md`
- `docs/reproducibility_acceptance_schema.md`
- `docs/final_audit_acceptance_schema.md`
- `docs/sensitivity_diagnostics.md`
- `docs/parameter_acceptance_schema.md`
- `data/manifests/reproducibility_manifest.json`

## Paper Draft State

A paper draft scaffold was added under:

- `paper/paper_draft.md`

The draft is written in English and frames the project as:

> A region-reusable decision framework for disrupted mobilization transport
> resilience under network degradation and constrained fleet operations.

The draft includes:

- working title options
- abstract draft
- research questions
- contribution claims
- related-work plan
- framework architecture
- data and regional reuse design
- simulation model description
- disruption and resilience metrics
- experimental design
- validation and sensitivity plan
- preliminary baseline interpretation guardrails
- figure and table plan
- manuscript claim guardrails
- immediate author TODOs

## Public Repository Clone State

A public repository source snapshot directory was added:

- `cloned_repo/`

Nested `.git` metadata was removed from each cloned repository before adding it
to this project. Treat these files as reference snapshots for implementation
study, not as production simulator modules.

The following repositories were shallow-cloned successfully and then stripped of
their nested `.git` directories:

- `networkx`
- `osmnx`
- `geopandas`
- `shapely`
- `pyrosm`
- `h3-py`
- `snail`
- `open-gira`
- `gtfs_kit`
- `gtfs-validator`
- `SALib`
- `frictionless-py`
- `GOSTnets`
- `pysal-access`
- `r5py`
- `routingpy`
- `or-tools`
- `PyVRP`
- `UXsim`
- `transcrit`
- `Path4GMNS`
- `aequilibrae`
- `osrm-backend`
- `valhalla`

The source snapshot manifest is tracked separately in:

- `cloned_repo_manifest.md`

Heavy full-platform tools such as SUMO, MATSim, and OpenTripPlanner were not
included in this pass because the immediate implementation target is the
open-data real-world pipeline around the current simulator rather than a full
platform migration.

## Caution For Future Work

Do not overstate current experimental results as real-world operational predictions.

Use this language:

> The current results are conditional findings under a representative network and assumptions.

Avoid this language:

> The current model proves that one transport mode is operationally superior in the real world.

Before any publication-style claim, improve network realism, calibrate parameters, and run sensitivity analysis.

Also avoid claiming that the new `src/realworld/` path has produced calibrated
results. It currently proves an executable quasi-real input pathway, a first
offline pilot scaffold, evidence/scenario scaffolding, offline scenario
compatibility, separated scaffold sample/staged/full outputs, and deterministic sensitivity
screening outputs, SALib Morris scaffold outputs, and scaffold-only figures/tables.
