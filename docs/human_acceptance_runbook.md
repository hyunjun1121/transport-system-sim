# Human Acceptance Runbook

This runbook explains how a reviewer should close final-study gates without
fabricating approval, source evidence, calibration, validation, or operational
routing claims. The repository can generate review packets, templates, guards,
and package audits, but only source-backed reviewer decisions can create formal
acceptance artifacts.

## Current Boundary

- Current final-study status: `final_study_ready=false`.
- Current plan gates: 3 / 15 ready (`real_input_smoke`,
  `structured_disruptions`, and `policy_alternatives`) and 12 / 15 blocked.
- Current formal acceptance status: 0 / 12 formal gates ready; all required
  formal acceptance artifacts are absent.
- `docs/current_goal_completion_audit.md` and
  `data/manifests/current_goal_completion_audit.json` are the current-state
  gap audit outputs.
- `docs/final_study_audit.md` must not be created until every pre-final gate is
  accepted with evidence.
- `data/manifests/agent_reviews/*.json` are sub-agent review records, not
  formal acceptance records.
- `data/manifests/formal_acceptance_evidence_matrix.csv` is a reviewer intake
  index, not a formal acceptance record.
- `docs/formal_acceptance_pre_review.md` and
  `data/manifests/draft_acceptance/*_pre_review.json` are AI-generated
  pre-review recommendations. They classify gates for human review but are not
  formal approval records.
- `data/manifests/acceptance_templates/*.json` and
  `data/parameters/parameter_acceptance_template.csv` are non-approval
  worksheets. They intentionally keep `accepted: false`.
- A copied template, unresolved `REVIEW_REQUIRED` value, draft road override,
  or current-state audit text cannot close a gate.
- `docs/archive/2026-05-11/expert_review_cycle_archive_20260511.md` adds an explicit package
  completeness requirement before renewed expert acceptance review. The expert
  reply reported that the submitted ZIP lacked the implementation, scripts,
  tests, data, results, and full documentation needed for technical review, so
  the next reviewer package must be inventory-checked before any acceptance
  decision is requested.

## Consultation-Driven Preflight

Before asking an external reviewer to assess the model, experiment results, or
policy-comparison claims again, perform this preflight:

1. Build a complete review package containing the implementation tree,
   configuration, scripts, tests, data/cache manifests, results, docs, paper
   draft, report sources, planning files, and acceptance materials.
2. Produce a package inventory with path, byte size, checksum, source category,
   and artifact role.
3. Run formal artifact and evidence-path hygiene checks.
4. Confirm that acceptance-looking files in formal target paths are either real
   reviewed decisions or absent.
5. Confirm that draft/template files remain clearly named and outside formal
   target paths.
6. Confirm that every missing local evidence path is intentionally externalized
   with URL or citation, retrieval date, checksum or archive note, license
   disposition, and reviewer decision.
7. Include `docs/archive/2026-05-11/expert_review_cycle_archive_20260511.md` in the package so the
   reviewer can see how the previous reply was converted into work items.

The preflight is packaging and review hygiene only. It does not accept any
transport, validation, source, sensitivity, reproducibility, or manuscript
claim.

## Reviewer Workflow

1. Refresh review artifacts:

```powershell
.\.venv\Scripts\python scripts\run_acceptance_audit.py
.\.venv\Scripts\python scripts\run_acceptance_audit.py --live-source-url-checks --source-url-timeout-sec 12
.\.venv\Scripts\python scripts\audit_source_provenance.py
.\.venv\Scripts\python scripts\write_source_license_review_packet.py
.\.venv\Scripts\python scripts\write_source_url_review_packet.py --preserve-existing-live
.\.venv\Scripts\python scripts\write_source_url_remediation_packet.py
.\.venv\Scripts\python scripts\write_source_provenance_priority_packet.py
.\.venv\Scripts\python scripts\write_source_context_cache_request_packet.py
.\.venv\Scripts\python scripts\write_source_context_cache_decision_packet.py
.\.venv\Scripts\python scripts\write_source_provenance_decision_packet.py
.\.venv\Scripts\python scripts\write_pilot_privacy_review_packet.py
.\.venv\Scripts\python scripts\write_pilot_region_decision_packet.py
.\.venv\Scripts\python scripts\write_rail_evidence_review_packet.py
.\.venv\Scripts\python scripts\write_rail_timing_source_request_packet.py
.\.venv\Scripts\python scripts\write_rail_fetch_readiness_packet.py
.\.venv\Scripts\python scripts\write_rail_evidence_priority_packet.py
.\.venv\Scripts\python scripts\write_rail_source_decision_packet.py
.\.venv\Scripts\python scripts\write_road_evidence_review_packet.py
.\.venv\Scripts\python scripts\write_road_evidence_source_request_packet.py
.\.venv\Scripts\python scripts\write_road_source_readiness_packet.py
.\.venv\Scripts\python scripts\write_road_evidence_priority_packet.py
.\.venv\Scripts\python scripts\write_road_source_decision_packet.py
.\.venv\Scripts\python scripts\write_parameter_review_packet.py
.\.venv\Scripts\python scripts\write_transfer_evidence_review_packet.py
.\.venv\Scripts\python scripts\write_parameter_evidence_source_request_packet.py
.\.venv\Scripts\python scripts\write_parameter_source_readiness_packet.py
.\.venv\Scripts\python scripts\write_parameter_evidence_priority_packet.py
.\.venv\Scripts\python scripts\write_parameter_source_decision_packet.py
.\.venv\Scripts\python scripts\write_full_graph_runtime_readiness_packet.py
.\.venv\Scripts\python scripts\write_graph_scale_review_packet.py
.\.venv\Scripts\python scripts\write_graph_scale_strategy_readiness_packet.py
.\.venv\Scripts\python scripts\write_graph_scale_method_decision_packet.py
.\.venv\Scripts\python scripts\write_osm_graph_snapshot_review_packet.py
.\.venv\Scripts\python scripts\write_validation_review_packet.py
.\.venv\Scripts\python scripts\write_validation_strategy_readiness_packet.py
.\.venv\Scripts\python scripts\write_validation_benchmark_readiness_packet.py
.\.venv\Scripts\python scripts\write_validation_benchmark_decision_packet.py
.\.venv\Scripts\python scripts\write_integrated_evidence_review_packet.py
.\.venv\Scripts\python scripts\write_sensitivity_review_packet.py
.\.venv\Scripts\python scripts\write_sensitivity_index_review_packet.py
.\.venv\Scripts\python scripts\write_sensitivity_strategy_readiness_packet.py
.\.venv\Scripts\python scripts\write_sensitivity_method_decision_packet.py
.\.venv\Scripts\python scripts\write_experiment_package_review_packet.py
.\.venv\Scripts\python scripts\write_seed_stream_manifest.py
.\.venv\Scripts\python scripts\audit_crn_pairing.py
.\.venv\Scripts\python scripts\audit_replication_adequacy.py
.\.venv\Scripts\python scripts\write_experiment_strategy_readiness_packet.py
.\.venv\Scripts\python scripts\write_experiment_design_decision_packet.py
.\.venv\Scripts\python scripts\write_experiment_statistical_plan.py
.\.venv\Scripts\python scripts\audit_deterministic_rerun.py
.\.venv\Scripts\python scripts\write_figure_table_review_packet.py
.\.venv\Scripts\python scripts\write_claim_alignment_review_packet.py
.\.venv\Scripts\python scripts\write_manuscript_report_decision_packet.py
.\.venv\Scripts\python scripts\write_reproducibility_review_packet.py
.\.venv\Scripts\python scripts\write_reproducibility_decision_packet.py
.\.venv\Scripts\python scripts\write_final_audit_decision_packet.py
.\.venv\Scripts\python scripts\run_reproducibility_smoke.py
.\.venv\Scripts\python scripts\audit_tracked_artifacts.py
.\.venv\Scripts\python scripts\write_review_package_inventory.py
.\.venv\Scripts\python scripts\build_review_package.py --fail-on-missing
.\.venv\Scripts\python scripts\write_acceptance_decision_templates.py
.\.venv\Scripts\python scripts\write_formal_acceptance_blocker_queue.py
.\.venv\Scripts\python scripts\write_acceptance_task_assignments.py
.\.venv\Scripts\python scripts\write_formal_acceptance_evidence_matrix.py
.\.venv\Scripts\python scripts\write_formal_acceptance_pre_review.py
.\.venv\Scripts\python scripts\audit_agent_review_paths.py
```

Use `scripts\write_formal_acceptance_blocker_queue.py` in refresh checklists.
`scripts\write_acceptance_blocker_queue.py` is the compatibility implementation
behind that explicit formal-acceptance command name.

The source-provenance audit, live source-URL option, source-license review
packet, source URL review packet, remediation packet, provenance-priority
packet, and source-provenance decision packet are reviewer aids only. They
record citation reachability, source-specific actions, source-level priorities,
and pending source decisions; they do not certify licenses, attribution, source
suitability, or provenance acceptance.

The source context-cache request and decision packets identify context-source
target payload blockers such as the KTDB GTFS zip or directory, Seoul
shortest-path API cache/raw JSON, and Seoul timetable API cache/raw JSON. They
are cache, sensitivity/context-only retention, or exclusion review aids only.
Cached KTDB metadata is review support, not a GTFS payload cache or provenance
acceptance.

Optional live source-cache refresh commands are separate from the default
packet refresh and should only be run when a reviewer intentionally updates
source snapshots:

```powershell
.\.venv\Scripts\python scripts\cache_ktdb_gtfs_source.py
.\.venv\Scripts\python scripts\cache_metro9_capacity_source.py
```

The KTDB command writes public source metadata only, not a reviewed GTFS feed.
The Metro 9 command writes a rolling-stock source-review extract only, not
accepted rail capacity. After either command, rerun the rail and
source-provenance review packets before considering any formal source decision.

The rail fetch-readiness and source-decision packets do not fetch or approve
live data. They record whether rail timing source requests are blocked by
missing API keys, missing reviewed GTFS files, or human-review-only capacity
and availability decisions.

The road source-readiness and source-decision packets do not fetch external
road data or create overrides. They record whether road source requests are
blocked by missing capacity/override evidence or require human review for
sparse speed candidates, benchmark strategy, and scenario-only disruption
treatment.

The parameter source-readiness and source-decision packets do not accept weak
assumptions. They record whether demand, fleet, dispatch, transfer,
disruption, and traffic/BPR source requests are blocked or require human
review before final parameter claims.

The graph-scale strategy-readiness packet does not choose the final
source-vs-analysis graph. It records whether the current reduced corridor,
multi-corridor candidates, full graph, result deltas, and missing
`graph_scale_acceptance.json` are blockers or human-review items. Current
cross-references are `docs/graph_scale_strategy_readiness_packet.md`,
`data/validation/graph_scale_strategy_readiness_packet.csv`, and
`data/validation/graph_scale_strategy_readiness_manifest.json`.

The validation strategy-readiness packet does not choose the final benchmark
strategy. It records whether internal checks, fallback benchmarks, optional
OSRM snapshots, accessibility diagnostics, route-road exposure, validation
summary scope, and the missing validation acceptance record are blockers or
human-review items. Current cross-references are
`docs/validation_strategy_readiness_packet.md`,
`data/validation/validation_strategy_readiness_packet.csv`, and
`data/validation/validation_strategy_readiness_manifest.json`.

The validation benchmark-readiness and benchmark-decision packets isolate
whether fallback, OSRM, or other route benchmarks are sufficient for the
validation claim boundary. They do not convert plausibility checks into ground
truth or create `validation_acceptance.json`.

The integrated evidence review packet consolidates the rail-source,
validation-benchmark, validation-strategy, experiment-design, context-cache,
and source-provenance decision manifests into a cross-gate worksheet. It is a
review aid only; it does not accept rail timing, validation benchmarks,
experiment outputs, or integrated final claims.

The sensitivity review, index-review, strategy-readiness, and method-decision
packets do not accept Morris output, waive Sobol analysis, or approve final
sensitivity claims. They record whether missing/non-finite Morris indices,
zero `mu_star` interpretation, reduced graph scope, scaffold result scope, the
Morris-vs-Sobol decision, and the missing sensitivity acceptance record are
blockers or human-review items. Current cross-references are
`docs/sensitivity_strategy_readiness_packet.md`,
`data/validation/sensitivity_strategy_readiness_packet.csv`, and
`data/validation/sensitivity_strategy_readiness_manifest.json`.

The experiment package, strategy-readiness, and design-decision packets do not
accept full pilot outputs or approve calibrated experiment claims. They record
whether scaffold result scope, graph-scale dependency, upstream input-evidence
dependency, row-count and checksum review, scenario-policy-seed design, CRN
pairing, and the missing experiment acceptance record are blockers or
human-review items. Current cross-references are
`docs/seed_stream_manifest.md`,
`docs/crn_pairing_audit.md`,
`docs/replication_adequacy_audit.md`,
`docs/experiment_strategy_readiness_packet.md`,
`data/manifests/experiment_strategy_readiness_packet.csv`, and
`data/manifests/experiment_strategy_readiness_manifest.json`.

The figure-table, claim-alignment, and manuscript/report decision packets do
not approve paper or report claims. They keep artifact inventory, captions,
graph scope, proxy interpretation, and evidence-gate dependencies visible
before any `manuscript_acceptance.json` record is drafted.

2. Inspect the aggregate blockers:

```powershell
Get-Content docs\current_goal_completion_audit.md
Get-Content docs\review_packets\acceptance_review_index.md
Get-Content docs\formal_acceptance_package_audit.md
Get-Content docs\formal_acceptance_blocker_queue.md
Get-Content docs\formal_acceptance_evidence_matrix.md
Get-Content docs\formal_acceptance_pre_review.md
```

3. For each gate, inspect the gate-specific review packet and supporting
   source paths listed in that packet.

4. If the evidence is still missing, leave the formal artifact absent and keep
   the gate `blocked` or `needs_human_review`.

5. If a reviewer has source-backed evidence and a bounded decision, copy the
   relevant non-approval template into the formal target path, replace every
   placeholder, set the accepted field according to the real decision, and keep
   the claim boundary non-operational.

6. After adding any formal artifact, run:

```powershell
.\.venv\Scripts\python scripts\audit_formal_acceptance_artifacts.py
.\.venv\Scripts\python scripts\audit_formal_evidence_paths.py
.\.venv\Scripts\python scripts\audit_tracked_artifacts.py
.\.venv\Scripts\python scripts\validate_formal_acceptance_package.py
.\.venv\Scripts\python scripts\write_formal_acceptance_evidence_matrix.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
.\.venv\Scripts\python scripts\audit_plan_artifacts.py
```

7. If all pre-final gates are accepted, create `docs/final_study_audit.md` as
   an independent prompt-to-artifact review. Then create
   `data/manifests/final_audit_acceptance.json` only if the final audit confirms
   the gate list, evidence, and non-operational claim boundary.

## Gate Worklist

| Gate | Review Packet | Formal Target | Reviewer Decision Needed |
| --- | --- | --- | --- |
| `pilot_region_accepted` | `docs/review_packets/pilot_region_accepted.md`; `docs/pilot_privacy_review_packet.md`; `docs/pilot_region_decision_packet.md` | `data/manifests/pilot_acceptance.json` | Privacy, sensitivity, region scope, upstream graph/provenance dependencies, and not-operational boundary acceptance |
| `data_provenance` | `docs/review_packets/data_provenance.md`; `docs/source_license_review_packet.md`; `docs/source_url_review_packet.md`; `docs/source_url_remediation_packet.md`; `docs/source_provenance_priority_packet.md`; `docs/source_context_cache_request_packet.md`; `docs/source_context_cache_decision_packet.md`; `docs/source_provenance_decision_packet.md` | `data/manifests/provenance_acceptance.json` | Source URLs, OSM/license/attribution, snapshot, reproducibility, privacy abstraction, and target payload cache/retention/exclusion decisions |
| `graph_scale_strategy` | `docs/review_packets/graph_scale_strategy.md`; `docs/graph_scale_review_packet.md`; `docs/full_graph_runtime_readiness_packet.md`; `docs/graph_scale_strategy_readiness_packet.md`; `docs/graph_scale_method_decision_packet.md` | `data/manifests/graph_scale_acceptance.json` | Reduced-corridor, multi-corridor, or full-graph method choice with matching graph counts and downstream regeneration decision |
| `cached_osm_input` | `docs/review_packets/cached_osm_input.md`; `docs/road_evidence_review_packet.md`; `docs/road_evidence_priority_packet.md`; `docs/road_source_readiness_packet.md`; `docs/road_source_decision_packet.md` | `data/parameters/road_class_overrides.csv` | Reviewed road speed, capacity, base-disruption evidence, benchmark limits, or bounded override decision |
| `parameter_evidence` | `docs/review_packets/parameter_evidence.md`; `docs/parameter_evidence_review_packet.md`; `docs/parameter_evidence_priority_packet.md`; `docs/parameter_source_readiness_packet.md`; `docs/parameter_source_decision_packet.md` | `data/parameters/parameter_acceptance.csv` | Acceptance or replacement of weak demand, fleet, transfer, disruption, traffic, censoring, and rail-dependent parameters |
| `rail_evidence` | `docs/review_packets/rail_evidence.md`; `docs/rail_evidence_review_packet.md`; `docs/rail_evidence_priority_packet.md`; `docs/rail_fetch_readiness_packet.md`; `docs/rail_source_decision_packet.md` | `data/parameters/parameter_acceptance.csv` | Rail headway, travel time, station, GTFS/API cache, capacity, availability, or sensitivity-only boundary |
| `validation_package` | `docs/review_packets/validation_package.md`; `docs/validation_review_packet.md`; `docs/validation_strategy_readiness_packet.md`; `docs/validation_benchmark_readiness_packet.md`; `docs/validation_benchmark_decision_packet.md`; `docs/integrated_evidence_review_packet.md` | `data/manifests/validation_acceptance.json` | Benchmark strategy, thresholds, sample scope, failure cases, weak road-evidence dependency, cross-gate evidence dependencies, and benchmark-not-ground-truth acknowledgement |
| `sensitivity_analysis` | `docs/review_packets/sensitivity_analysis.md`; `docs/sensitivity_review_packet.md`; `docs/sensitivity_index_review_packet.md`; `docs/sensitivity_strategy_readiness_packet.md`; `docs/sensitivity_method_decision_packet.md` | `data/manifests/sensitivity_acceptance.json` | Parameter ranges, Morris diagnostics, missing/non-finite indices, Sobol decision, graph scope, and interpretation caveats |
| `full_experiment_output` | `docs/review_packets/full_experiment_output.md`; `docs/experiment_package_review_packet.md`; `docs/seed_stream_manifest.md`; `docs/crn_pairing_audit.md`; `docs/replication_adequacy_audit.md`; `docs/experiment_strategy_readiness_packet.md`; `docs/experiment_design_decision_packet.md` | `data/manifests/experiment_acceptance.json` | Scenario-policy-seed package, seed streams, structural CRN pairing, paired-delta statistics, replication adequacy, multiple-comparison handling, row counts, manifests, checksums where available, graph/input dependencies, and rerun requirement after upstream changes |
| `manuscript_report_alignment` | `docs/review_packets/manuscript_report_alignment.md`; `docs/figure_table_review_packet.md`; `docs/claim_alignment_review_packet.md`; `docs/manuscript_report_decision_packet.md` | `data/manifests/manuscript_acceptance.json` | Claim-by-claim alignment of paper/report/figures against accepted evidence, graph scope, proxy interpretation, and upstream gate dependencies |
| `reproducibility` | `docs/review_packets/reproducibility.md`; `docs/reproducibility_review_packet.md`; `docs/reproducibility_decision_packet.md` | `data/manifests/reproducibility_acceptance.json` | Clean-checkout reproduction, artifact regeneration, package state, import-boundary review, and command log; current-worktree smoke is supporting evidence only |
| `final_audit` | `docs/review_packets/final_audit.md`; `docs/final_audit_decision_packet.md` | `docs/final_study_audit.md` and `data/manifests/final_audit_acceptance.json` | Independent final review after every pre-final gate closes and all formal artifacts exist |

## Acceptance Package Checks

The formal package should stay blocked until all required evidence is present.
These commands are expected to fail with blockers until the human/source-backed
records exist:

```powershell
.\.venv\Scripts\python scripts\validate_formal_acceptance_package.py --fail-on-blockers
.\.venv\Scripts\python scripts\audit_publication_readiness.py --fail-on-blockers
.\.venv\Scripts\python scripts\audit_final_study_readiness.py --fail-on-blockers
```

## Reviewer Safety Rules

- Do not approve a gate from passing tests alone.
- Do not approve a gate from evidence-path hygiene alone; existing paths only
  prove that files are present, not that the evidence is sufficient.
- Do not approve road or rail inputs from OSM/GraphML presence alone.
- Do not approve validation from OSRM or fallback-router checks without a
  benchmark-strategy decision.
- Do not approve sensitivity results while upstream graph/input evidence gates
  are still blocked.
- Do not approve reproducibility from current-worktree smoke alone; it is not a
  fresh-clone or clean-checkout reproduction.
- Do not approve paper/report claims before evidence gates and claim boundaries
  are aligned.
- Do not mark `final_study_ready: true` until the final-study readiness audit and
  formal acceptance package audit both agree.
