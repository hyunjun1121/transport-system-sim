# Formal Gate Pre-Review

Draft pre-review recommendations only. These records classify remaining formal acceptance gates for human reviewers; they do not create formal approval, certify evidence, validate licenses, calibrate results, or mark the final study complete.

## Summary

- Draft records: 12
- Recommendation counts: `{'blocked_requires_human_decision': 4, 'blocked_missing_evidence': 8}`
- Human decisions required: 12
- Formal permission made: `false`
- Final-study ready: `false`
- Can mark complete: `false`
- Draft directory: `data/manifests/draft_acceptance`

## Gate Recommendations

| Gate | Current Status | Recommendation | Formal Target | Missing Evidence | Human Action |
| --- | --- | --- | --- | --- | --- |
| pilot_region_accepted | `blocked` | `blocked_requires_human_decision` | `data/manifests/pilot_acceptance.json` | Blocked non-approval item: create an explicit pilot decision record after privacy and case-scope review<br>Blocked non-approval item: resolve pilot-region decision blockers before pilot decision record<br>+5 more | Blocked non-approval item: Inspect the listed review packets and evidence paths.<br>Blocked non-approval item: Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| graph_scale_strategy | `blocked` | `blocked_requires_human_decision` | `data/manifests/graph_scale_acceptance.json` | Blocked non-approval item: create an explicit graph-scale decision record after source-vs-analysis graph review<br>Blocked non-approval item: resolve graph-scale strategy-readiness blockers before graph-scale decision record<br>+12 more | Blocked non-approval item: Inspect the listed review packets and evidence paths.<br>Blocked non-approval item: Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| data_provenance | `blocked` | `blocked_requires_human_decision` | `data/manifests/provenance_acceptance.json` | Blocked non-approval item: create an explicit provenance decision record after source, license, snapshot, privacy, and reproducibility review<br>Blocked non-approval item: replace scaffold-only reproducibility manifest with reviewer-retained source/license/snapshot provenance<br>+20 more | Blocked non-approval item: Inspect the listed review packets and evidence paths.<br>Blocked non-approval item: Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| parameter_acceptance | `blocked` | `blocked_missing_evidence` | `data/parameters/parameter_acceptance.csv` | Blocked non-approval item: create reviewed parameter decision records only for weak assumptions retained in release-scope claims<br>Blocked non-approval item: parameter_acceptance.csv is missing<br>+53 more | Blocked non-approval item: Inspect the listed review packets and evidence paths.<br>Blocked non-approval item: Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| road_class_overrides | `blocked` | `blocked_missing_evidence` | `data/parameters/road_class_overrides.csv` | Blocked non-approval item: replace weak field-level road override sources before treating speed, capacity, or base-disruption values as source-backed<br>Blocked non-approval item: verify graph-adapter runs apply the reviewed override table before using road-calibration claims<br>+23 more | Blocked non-approval item: Inspect the listed review packets and evidence paths.<br>Blocked non-approval item: Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| validation_package | `blocked` | `blocked_requires_human_decision` | `data/manifests/validation_acceptance.json` | Blocked non-approval item: create an explicit validation decision record after benchmark-strategy review<br>Blocked non-approval item: resolve benchmark strategy-readiness blockers before benchmark decision record<br>+10 more | Blocked non-approval item: Inspect the listed review packets and evidence paths.<br>Blocked non-approval item: Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| sensitivity_analysis | `blocked` | `blocked_missing_evidence` | `data/manifests/sensitivity_acceptance.json` | Blocked non-approval item: create an explicit sensitivity decision record after SALib output and Sobol-decision review<br>Blocked non-approval item: resolve sensitivity strategy-readiness blockers before sensitivity decision record<br>+7 more | Blocked non-approval item: Inspect the listed review packets and evidence paths.<br>Blocked non-approval item: Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| full_experiment_output | `blocked` | `blocked_missing_evidence` | `data/manifests/experiment_acceptance.json` | Blocked non-approval item: create an explicit experiment decision record after input checks, graph-scope, and scenario-policy-seed review<br>Blocked non-approval item: resolve experiment strategy-readiness blockers before experiment decision record<br>+14 more | Blocked non-approval item: Inspect the listed review packets and evidence paths.<br>Blocked non-approval item: Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| manuscript_report_alignment | `blocked` | `blocked_missing_evidence` | `data/manifests/manuscript_acceptance.json` | Blocked non-approval item: create an explicit manuscript/report decision record after evidence gates, figures, paper, report, and claim boundaries are reviewed<br>Blocked non-approval item: close evidence gates before release-scope paper/report claims<br>+17 more | Blocked non-approval item: Inspect the listed review packets and evidence paths.<br>Blocked non-approval item: Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| reproducibility | `blocked` | `blocked_missing_evidence` | `data/manifests/reproducibility_acceptance.json` | Blocked non-approval item: create an explicit reproducibility decision record after clean-checkout reproduction review, artifact regeneration, manifest review, and import-boundary checks<br>Blocked non-approval item: replace scaffold-only manifest with clean-checkout final reproduction package<br>+5 more | Blocked non-approval item: Inspect the listed review packets and evidence paths.<br>Blocked non-approval item: Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| final_audit_document | `blocked` | `blocked_missing_evidence` | `docs/final_study_audit.md` | Blocked non-approval item: create docs/final_study_audit.md after all other gates close<br>Blocked non-approval item: create an explicit closeout-audit decision record only after prompt-to-artifact review confirms every closeout gate is closed<br>+8 more | Blocked non-approval item: Inspect the listed review packets and evidence paths.<br>Blocked non-approval item: Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+5 more |
| final_audit | `blocked` | `blocked_missing_evidence` | `data/manifests/final_audit_acceptance.json` | Blocked non-approval item: create an explicit closeout-audit decision record only after prompt-to-artifact review confirms every closeout gate is closed<br>Blocked non-approval item: create docs/final_study_audit.md after all other gates close<br>+8 more | Blocked non-approval item: Inspect the listed review packets and evidence paths.<br>Blocked non-approval item: Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+5 more |

## Gate Details

### pilot_region_accepted

- Label: Pilot Region Decision
- Related plan gates: `pilot_region_accepted`
- Recommendation: `blocked_requires_human_decision`
- Reason: Repository review packets exist, but a source-backed human decision is still required before any formal artifact can be created.
- Formal target after human decision: `data/manifests/pilot_acceptance.json`
- Formal permission: `false`
- Human decision required: `true`

Review packets:
- docs/review_packets/pilot_region_accepted.md
- data/manifests/pilot_privacy_review_packet.csv
- data/manifests/pilot_region_decision_packet.csv

Source paths:
- data/regions/pilot_region.yaml
- docs/pilot_region_data_card.md
- data/manifests/pilot_privacy_review_packet.csv
- data/manifests/pilot_privacy_review_manifest.json
- data/manifests/pilot_region_decision_packet.csv
- data/manifests/pilot_region_decision_manifest.json
- data/manifests/pilot_acceptance.json

Evidence inspected:
- `data/regions/pilot_region.yaml`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/pilot_region_data_card.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/pilot_privacy_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/pilot_privacy_review_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/pilot_region_decision_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/pilot_region_decision_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/pilot_acceptance.json`: absent; formal artifact absent; expected until a source-backed reviewer decision exists
- `docs/review_packets/pilot_region_accepted.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/current_goal_completion_audit.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/current_goal_completion_audit.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/pilot_privacy_review_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/pilot_region_decision_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_pilot_region_decision_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review

Missing evidence:
- Blocked non-approval item: create an explicit pilot decision record after privacy and case-scope review
- Blocked non-approval item: resolve pilot-region decision blockers before pilot decision record
- Blocked non-approval item: pilot-region decision: data/manifests/graph_scale_acceptance.json is absent
- Blocked non-approval item: pilot-region decision: data/manifests/provenance_acceptance.json is absent
- Blocked non-approval item: pilot-region decision: data/manifests/pilot_acceptance.json is absent
- Blocked non-approval item: review pilot-region decision human-decision items before pilot decision record
- Blocked non-approval item: data/manifests/pilot_acceptance.json is absent

Residual risks:
- Blocked non-approval risk note: Record an explicit pilot acceptance decision with reviewer, scope, privacy review, evidence paths, and not-deployment-scope claim boundary.
- Blocked non-approval risk note: create an explicit pilot decision record after privacy and case-scope review
- Blocked non-approval risk note: create an explicit pilot decision record after privacy and case-scope review
- Blocked non-approval risk note: Draft recommendation could be overread as permission if copied into a target path.
- Blocked non-approval risk note: Study gate status remains false until reviewers record source-backed decisions.

Human reviewer action required:
- Blocked non-approval action: Inspect the listed review packets and evidence paths.
- Blocked non-approval action: Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Blocked non-approval action: Decide whether to clear, reject, or keep blocked based on the existing review packet evidence.
- Blocked non-approval action: Resolve each missing-evidence item listed in this record.
- Blocked non-approval action: After a real decision, create or update data/manifests/pilot_acceptance.json.
- Blocked non-approval action: Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/manifests/pilot_acceptance.json

### graph_scale_strategy

- Label: Graph-Scale Decision
- Related plan gates: `graph_scale_strategy`
- Recommendation: `blocked_requires_human_decision`
- Reason: Repository review packets exist, but a source-backed human decision is still required before any formal artifact can be created.
- Formal target after human decision: `data/manifests/graph_scale_acceptance.json`
- Formal permission: `false`
- Human decision required: `true`

Review packets:
- docs/review_packets/graph_scale_strategy.md
- data/validation/graph_scale_review_packet.csv
- data/validation/full_graph_runtime_readiness_packet.csv
- data/validation/graph_scale_manifest_audit.csv
- data/validation/graph_scale_strategy_readiness_packet.csv
- data/validation/graph_scale_method_decision_packet.csv

Source paths:
- results/realworld_pilot/pilot_full_manifest.json
- data/validation/graph_scale_route_comparison.csv
- data/validation/graph_scale_alternate_routes.csv
- data/validation/graph_scale_multi_corridor_routes.csv
- data/validation/full_graph_runtime_readiness_packet.csv
- data/validation/graph_scale_manifest_audit.csv
- data/validation/graph_scale_strategy_readiness_packet.csv
- data/validation/graph_scale_method_decision_packet.csv
- data/validation/graph_scale_result_comparison.csv
- data/manifests/graph_scale_acceptance.json

Evidence inspected:
- `results/realworld_pilot/pilot_full_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/graph_scale_route_comparison.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/graph_scale_alternate_routes.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/graph_scale_multi_corridor_routes.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/full_graph_runtime_readiness_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/graph_scale_manifest_audit.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/graph_scale_strategy_readiness_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/graph_scale_method_decision_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/graph_scale_result_comparison.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/graph_scale_acceptance.json`: absent; formal artifact absent; expected until a source-backed reviewer decision exists
- `docs/review_packets/graph_scale_strategy.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/graph_scale_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/analysis_corridor_method_note.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/graph_scale_diagnostics.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/graph_scale_manifest_audit.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/full_graph_runtime_readiness_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/graph_scale_manifest_audit_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/graph_scale_strategy_readiness_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/graph_scale_method_decision_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/graph_scale_method_decision_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/graph_scale_result_comparison_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/graph_scale_route_comparison_summary.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/graph_scale_alternate_routes_summary.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/graph_scale_multi_corridor_routes_summary.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/graph_scale_review_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/graph_scale_strategy_readiness_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/full_graph_runtime_readiness_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/audit_graph_scale_manifests.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_graph_scale_review_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_graph_scale_strategy_readiness_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_graph_scale_method_decision_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_graph_scale_result_comparison.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/run_graph_scale_diagnostics.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `results/realworld_pilot/pilot_multi_corridor_results.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `results/realworld_pilot/pilot_multi_corridor_summary.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `results/realworld_pilot/pilot_multi_corridor_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `results/realworld_pilot/pilot_multi_corridor_full_results.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `results/realworld_pilot/pilot_multi_corridor_full_summary.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `results/realworld_pilot/pilot_multi_corridor_full_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review

Missing evidence:
- Blocked non-approval item: create an explicit graph-scale decision record after source-vs-analysis graph review
- Blocked non-approval item: resolve graph-scale strategy-readiness blockers before graph-scale decision record
- Blocked non-approval item: graph-scale strategy readiness: full bus-practical graph has smoke evidence only
- Blocked non-approval item: graph-scale strategy readiness: data/manifests/graph_scale_acceptance.json is absent
- Blocked non-approval item: graph-scale strategy readiness: current reduced-corridor output has alternate-route warnings
- Blocked non-approval item: graph-scale strategy readiness: full bus-practical graph has smoke/runtime evidence only, not full scenario-policy-seed output
- Blocked non-approval item: graph-scale strategy readiness: selected graph choice still requires downstream regeneration decisions for sensitivity, figures, tables, and manuscript interpretation
- Blocked non-approval item: review graph-scale strategy-readiness human-decision items before graph-scale decision record
- Blocked non-approval item: resolve graph-scale method-decision blockers before graph-scale decision record
- Blocked non-approval item: graph-scale method decision: full bus-practical graph has smoke/runtime evidence only, not full scenario-policy-seed output
- Blocked non-approval item: graph-scale method decision: selected graph choice still requires downstream regeneration decisions for sensitivity, figures, tables, and manuscript interpretation
- Blocked non-approval item: graph-scale method decision: data/manifests/graph_scale_acceptance.json is absent
- Blocked non-approval item: review graph-scale method-decision human-decision items before graph-scale decision record
- Blocked non-approval item: data/manifests/graph_scale_acceptance.json is absent

Residual risks:
- Blocked non-approval risk note: Choose and document reduced-corridor, multi-corridor, or full-graph strategy.
- Blocked non-approval risk note: Create graph_scale_acceptance.json with matching graph counts and evidence paths.
- Blocked non-approval risk note: create an explicit graph-scale decision record after source-vs-analysis graph review
- Blocked non-approval risk note: create an explicit graph-scale decision record after source-vs-analysis graph review
- Blocked non-approval risk note: Draft recommendation could be overread as permission if copied into a target path.
- Blocked non-approval risk note: Study gate status remains false until reviewers record source-backed decisions.

Human reviewer action required:
- Blocked non-approval action: Inspect the listed review packets and evidence paths.
- Blocked non-approval action: Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Blocked non-approval action: Decide whether to clear, reject, or keep blocked based on the existing review packet evidence.
- Blocked non-approval action: Resolve each missing-evidence item listed in this record.
- Blocked non-approval action: After a real decision, create or update data/manifests/graph_scale_acceptance.json.
- Blocked non-approval action: Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/manifests/graph_scale_acceptance.json

### data_provenance

- Label: Source/License/Provenance Decision
- Related plan gates: `data_provenance`
- Recommendation: `blocked_requires_human_decision`
- Reason: Repository review packets exist, but a source-backed human decision is still required before any formal artifact can be created.
- Formal target after human decision: `data/manifests/provenance_acceptance.json`
- Formal permission: `false`
- Human decision required: `true`

Review packets:
- docs/review_packets/data_provenance.md
- data/manifests/source_license_review_packet.csv
- data/manifests/source_url_review_packet.csv
- data/manifests/source_url_remediation_packet.csv
- data/manifests/source_provenance_priority_packet.csv
- data/manifests/source_context_cache_request_packet.csv
- data/manifests/source_context_cache_decision_packet.csv
- data/manifests/source_provenance_decision_packet.csv

Source paths:
- data/manifests/source_provenance_manifest.json
- data/manifests/source_license_review_packet.csv
- data/manifests/source_url_review_packet.csv
- data/manifests/source_url_remediation_packet.csv
- data/manifests/source_provenance_priority_packet.csv
- data/manifests/source_context_cache_request_packet.csv
- data/manifests/source_context_cache_decision_packet.csv
- data/manifests/source_provenance_decision_packet.csv
- data/manifests/reproducibility_manifest.json
- data/cache/pilot_region_road_manifest.json
- cloned_repo_manifest.md
- data/manifests/provenance_acceptance.json

Evidence inspected:
- `data/manifests/source_provenance_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/source_license_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/source_url_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/source_url_remediation_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/source_provenance_priority_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/source_context_cache_request_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/source_context_cache_decision_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/source_provenance_decision_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/reproducibility_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/cache/pilot_region_road_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `cloned_repo_manifest.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/provenance_acceptance.json`: absent; formal artifact absent; expected until a source-backed reviewer decision exists
- `docs/review_packets/data_provenance.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/source_license_review_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/source_url_review_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/source_url_remediation_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/source_provenance_priority_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/source_context_cache_request_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/source_context_cache_decision_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/source_provenance_decision_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/source_provenance_decision_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/current_goal_completion_audit.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/reproducibility_package.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/source_license_review_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/source_url_review_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/source_url_remediation_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/source_provenance_priority_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/source_context_cache_request_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/source_context_cache_decision_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/pilot_region_data_card.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/audit_source_provenance.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_source_license_review_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_source_url_review_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_source_url_remediation_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_source_provenance_priority_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_source_context_cache_request_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_source_context_cache_decision_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_source_provenance_decision_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review

Missing evidence:
- Blocked non-approval item: create an explicit provenance decision record after source, license, snapshot, privacy, and reproducibility review
- Blocked non-approval item: replace scaffold-only reproducibility manifest with reviewer-retained source/license/snapshot provenance
- Blocked non-approval item: source provenance priority: formal provenance decision record is absent
- Blocked non-approval item: source provenance priority: context-source target artifacts still need reviewed payloads, sensitivity/context-only retention decisions, or exclusion decisions
- Blocked non-approval item: source provenance priority: cached public snapshots still require license, attribution, snapshot, and reproducibility review
- Blocked non-approval item: source provenance priority: repository inputs still require human scope/privacy/reproducibility review
- Blocked non-approval item: source provenance priority: URL remediation rows still require reviewer confirmation
- Blocked non-approval item: source context cache request: context-source target cache artifacts still lack reviewed source payloads, sensitivity/context-only retention decisions, or explicit exclusion decisions
- Blocked non-approval item: source context cache request: license, attribution, snapshot, and reproducibility review are still required for retained public sources
- Blocked non-approval item: source context cache request: formal provenance decision record is absent
- Blocked non-approval item: source context cache decision: formal provenance decision record is absent
- Blocked non-approval item: source context cache decision: target cache/retention/exclusion decisions are pending for context-source rows
- Blocked non-approval item: source context cache decision: retained context sources still require license, attribution, snapshot, and reproducibility review
- Blocked non-approval item: source context cache decision: ktdb_public_transport_gtfs_context: no reviewed cache artifact, sensitivity/context-only retention decision, or explicit exclusion decision is present
- Blocked non-approval item: source context cache decision: seoul_shortest_path_api_context: no reviewed cache artifact, sensitivity/context-only retention decision, or explicit exclusion decision is present
- Blocked non-approval item: source context cache decision: seoul_timetable_api_context: no reviewed cache artifact, sensitivity/context-only retention decision, or explicit exclusion decision is present
- Blocked non-approval item: resolve source-provenance decision blockers before provenance decision record
- Blocked non-approval item: source provenance decision: context-source target cache artifacts still lack reviewed source payloads, sensitivity/context-only retention decisions, or explicit exclusion decisions
- Blocked non-approval item: source provenance decision: reproducibility manifest remains scaffold-only
- Blocked non-approval item: source provenance decision: data/manifests/provenance_acceptance.json is absent
- Blocked non-approval item: review source-provenance decision human-decision items before provenance decision record
- Blocked non-approval item: data/manifests/provenance_acceptance.json is absent

Residual risks:
- Blocked non-approval risk note: Review source URLs, licenses, attribution, local snapshots, privacy abstraction, and reproducibility scope.
- Blocked non-approval risk note: Create data/manifests/provenance_acceptance.json only after source-backed review.
- Blocked non-approval risk note: create an explicit provenance decision record after source, license, snapshot, privacy, and reproducibility review
- Blocked non-approval risk note: create an explicit provenance decision record after source, license, snapshot, privacy, and reproducibility review
- Blocked non-approval risk note: Draft recommendation could be overread as permission if copied into a target path.
- Blocked non-approval risk note: Study gate status remains false until reviewers record source-backed decisions.

Human reviewer action required:
- Blocked non-approval action: Inspect the listed review packets and evidence paths.
- Blocked non-approval action: Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Blocked non-approval action: Decide whether to clear, reject, or keep blocked based on the existing review packet evidence.
- Blocked non-approval action: Resolve each missing-evidence item listed in this record.
- Blocked non-approval action: After a real decision, create or update data/manifests/provenance_acceptance.json.
- Blocked non-approval action: Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/manifests/provenance_acceptance.json

### parameter_acceptance

- Label: Weak-Parameter Decision
- Related plan gates: `parameter_evidence`, `rail_evidence`
- Recommendation: `blocked_missing_evidence`
- Reason: The gate still lacks source-backed, reviewer-decided, or upstream-complete evidence required by the current study audit.
- Formal target after human decision: `data/parameters/parameter_acceptance.csv`
- Formal permission: `false`
- Human decision required: `true`

Review packets:
- docs/review_packets/parameter_evidence.md
- data/parameters/parameter_evidence_review_packet.csv
- data/parameters/parameter_source_readiness_packet.csv
- data/parameters/parameter_evidence_priority_packet.csv
- data/parameters/parameter_source_decision_packet.csv
- data/parameters/transfer_evidence_review_packet.csv
- data/parameters/road_evidence_review_packet.csv
- data/road/road_source_readiness_packet.csv
- data/road/road_source_decision_packet.csv
- data/road/road_evidence_priority_packet.csv
- data/parameters/rail_evidence_review_packet.csv
- data/rail/rail_fetch_readiness_packet.csv
- data/rail/rail_evidence_priority_packet.csv
- data/rail/rail_source_decision_packet.csv
- docs/review_packets/cached_osm_input.md
- docs/review_packets/rail_evidence.md

Source paths:
- data/parameters/parameter_sources.csv
- data/parameters/road_class_overrides_draft.csv
- data/parameters/rail_service_evidence.csv
- data/parameters/rail_station_bindings.csv
- data/parameters/parameter_source_readiness_packet.csv
- data/parameters/parameter_evidence_priority_packet.csv
- data/parameters/parameter_source_decision_packet.csv
- data/parameters/transfer_evidence_review_packet.csv
- data/road/road_source_readiness_packet.csv
- data/road/road_source_decision_packet.csv
- data/road/road_evidence_priority_packet.csv
- data/rail/rail_fetch_readiness_packet.csv
- data/rail/rail_evidence_priority_packet.csv
- data/rail/rail_source_decision_packet.csv
- data/parameters/parameter_acceptance.csv

Evidence inspected:
- `data/parameters/parameter_sources.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/road_class_overrides_draft.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/rail_service_evidence.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/rail_station_bindings.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/parameter_source_readiness_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/parameter_evidence_priority_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/parameter_source_decision_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/transfer_evidence_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/road/road_source_readiness_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/road/road_source_decision_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/road/road_evidence_priority_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/rail/rail_fetch_readiness_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/rail/rail_evidence_priority_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/rail/rail_source_decision_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/parameter_acceptance.csv`: absent; formal artifact absent; expected until a source-backed reviewer decision exists
- `docs/review_packets/parameter_evidence.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/parameter_evidence_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/road_evidence_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/rail_evidence_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/review_packets/cached_osm_input.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/review_packets/rail_evidence.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/parameter_evidence_source_request_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/parameter_source_readiness_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/parameter_evidence_priority_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/parameter_source_decision_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/transfer_evidence_review_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/road/road_evidence_source_request_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/road/road_source_readiness_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/road/road_source_decision_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/road/road_evidence_priority_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/rail/rail_timing_source_request_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/rail/rail_fetch_readiness_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/rail/rail_evidence_priority_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/rail/rail_source_decision_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/parameter_evidence_review_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/transfer_evidence_review_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/parameter_evidence_source_request_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/parameter_source_readiness_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/parameter_evidence_priority_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/parameter_source_decision_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/audit_parameter_evidence.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_transfer_evidence_review_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_parameter_review_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_parameter_evidence_source_request_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_parameter_source_readiness_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_parameter_evidence_priority_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_parameter_source_decision_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/rail_evidence_review_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/rail/rail_timing_source_request_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/rail_fetch_readiness_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/rail_evidence_priority_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/rail_source_decision_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/audit_rail_evidence.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_rail_evidence_review_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_rail_timing_source_request_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_rail_fetch_readiness_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_rail_evidence_priority_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_rail_source_decision_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/fetch_rail_timetable_cache.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/derive_rail_headway_evidence.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/derive_rail_service_evidence.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/derive_rail_gtfs_evidence.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/schemas/rail_gtfs_cache_schema.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/fetch_rail_shortest_path_cache.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/derive_rail_shortest_path_evidence.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/rail/rail_transit_stress_profile_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/rail/rail_transit_stress_profile_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/rail_transit_stress_profile_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_rail_transit_stress_profile_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/rail/rail_bounded_treatment_audit.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/rail_bounded_treatment_audit.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/audit_rail_bounded_treatments.py`: present; local supporting artifact present; evidence quality still requires human/source review

Missing evidence:
- Blocked non-approval item: create reviewed parameter decision records only for weak assumptions retained in release-scope claims
- Blocked non-approval item: parameter_acceptance.csv is missing
- Blocked non-approval item: justify demand scale, arrival process, time horizon, and censoring penalties with planning assumptions or sensitivity-bound evidence
- Blocked non-approval item: replace scenario-only disruption probabilities and degradation rules with public hazard, incident, literature, or expert-reviewed evidence
- Blocked non-approval item: replace generic fleet and vehicle-capacity assumptions with agency, planning, literature, or reviewer-retained scenario evidence
- Blocked non-approval item: derive rail headway and travel time from cached GTFS, timetable, operator, or agency records, and keep rail capacity source-backed or explicitly sensitivity-only
- Blocked non-approval item: strengthen road speed, capacity, and background traffic values with public speed limits, traffic counts, or benchmark-calibrated routing
- Blocked non-approval item: support transfer delays with station-layout evidence, observed ranges, or literature rather than generic fixed delays
- Blocked non-approval item: parameter source readiness: all rows require human review or external source decisions before release-scope claims
- Blocked non-approval item: parameter source readiness: this packet is source-review evidence only and cannot create reviewed parameter values
- Blocked non-approval item: parameter source readiness: parameter_acceptance.csv remains separate and absent unless reviewers explicitly retain weak assumptions
- Blocked non-approval item: parameter evidence priority: transfer-delay evidence still requires human review and source-backed or reviewer-retention treatment
- Blocked non-approval item: parameter evidence priority: rail timing/source-decision evidence is incomplete
- Blocked non-approval item: parameter evidence priority: high-priority disruption and traffic/BPR rows still require human/source-backed decisions
- Blocked non-approval item: parameter evidence priority: medium-priority demand, fleet, dispatch, and transfer rows remain scenario assumptions
- Blocked non-approval item: parameter evidence priority: parameter_acceptance.csv remains absent unless reviewers accept retained weak assumptions
- Blocked non-approval item: parameter source decision: formal parameter acceptance table is absent
- Blocked non-approval item: parameter source decision: parameter source decisions are pending for weak parameter groups
- Blocked non-approval item: parameter source decision: retained weak assumptions require source-backed updates, sensitivity-only limits, or explicit weak-parameter acceptance
- Blocked non-approval item: rail service evidence: cache timetable, shortest-path, or GTFS-derived records
- Blocked non-approval item: rail service evidence: derive headway and travel time from the cached records
- Blocked non-approval item: rail fetch readiness: source-backed rail timing evidence remains incomplete until every required timing source is reviewed and retained
- Blocked non-approval item: rail fetch readiness: API-key rows require DATA_GO_KR_KEY or reviewed cached API payloads
- Blocked non-approval item: rail fetch readiness: reviewed-GTFS row requires a reviewed GTFS input and validator report
- Blocked non-approval item: rail fetch readiness: reviewed-static-timetable cache is retained for headway review only; it does not close rail travel-time evidence
- Blocked non-approval item: rail fetch readiness: capacity and availability rows still require reviewer-scoped bounded treatment or source-backed evidence
- Blocked non-approval item: rail fetch readiness: this packet is readiness evidence only and cannot create rail_service_evidence.csv
- Blocked non-approval item: rail evidence priority: source-backed rail timing evidence remains incomplete until API/GTFS/travel-time source paths are reviewed and retained
- Blocked non-approval item: rail evidence priority: DATA_GO_KR_KEY, reviewed GTFS input, or reviewed shortest-path cache is absent
- Blocked non-approval item: rail evidence priority: capacity and availability treatment still require human/source-backed decisions
- Blocked non-approval item: rail source decision: rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests
- Blocked non-approval item: rail source decision: rail timing cache or reviewed GTFS source files remain required for source-backed timing claims
- Blocked non-approval item: rail source decision: retained rail capacity and availability assumptions require source-backed updates, sensitivity-only limits, scenario-only limits, or reviewer-scoped bounded treatment
- Blocked non-approval item: rail source decision: non-formal source decisions do not close rail evidence, publication, study-closeout, or formal decision gates
- Blocked non-approval item: rail source decision: rail_shortest_path_travel_time_request: DATA_GO_KR_KEY is absent and no cached payload is present
- Blocked non-approval item: rail source decision: rail_static_gtfs_timing_request: reviewed GTFS file or GTFS Validator report is absent
- Blocked non-approval item: rail source decision: rail_timetable_headway_request: DATA_GO_KR_KEY is absent and no cached payload is present
- Blocked non-approval item: record reviewed rail source decisions for every row with zero blocking and human-review rows
- Blocked non-approval item: non-formal rail source-decision action ledger cannot close rail evidence gate
- Blocked non-approval item: rail source-decision action ledger is not formal decision evidence
- Blocked non-approval item: rail transit stress profile cannot support rail evidence gate
- Blocked non-approval item: rail transit stress profile is not publication-ready evidence
- Blocked non-approval item: rail transit stress profile cannot mark complete
- Blocked non-approval item: rail transit stress profile: rail transit stress profiles are scenario/sensitivity review support only
- Blocked non-approval item: rail transit stress profile: capacity and availability profiles require reviewer decisions before release-scope rail claims
- Blocked non-approval item: rail transit stress profile: rail source decision: rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests
- Blocked non-approval item: rail transit stress profile: rail source decision: rail timing cache or reviewed GTFS source files remain required for source-backed timing claims
- Blocked non-approval item: rail transit stress profile: rail source decision: retained rail capacity and availability assumptions require source-backed updates, sensitivity-only limits, scenario-only limits, or reviewer-scoped bounded treatment
- Blocked non-approval item: rail transit stress profile: rail source decision: non-formal source decisions do not close rail evidence, publication, study-closeout, or formal decision gates
- Blocked non-approval item: rail transit stress profile: rail source decision: rail_shortest_path_travel_time_request: DATA_GO_KR_KEY is absent and no cached payload is present
- Blocked non-approval item: rail transit stress profile: rail source decision: rail_static_gtfs_timing_request: reviewed GTFS file or GTFS Validator report is absent
- Blocked non-approval item: rail transit stress profile: rail source decision: rail_timetable_headway_request: DATA_GO_KR_KEY is absent and no cached payload is present
- Blocked non-approval item: 4 rail bounded-treatment warnings remain
- Blocked non-approval item: 2 rail bounded-treatment source decisions remain pending
- Blocked non-approval item: data/parameters/parameter_acceptance.csv is absent

Residual risks:
- Blocked non-approval risk note: Replace weak road, rail, and parameter assumptions with source-backed evidence or explicit reviewer-retained overrides.
- Blocked non-approval risk note: Create road_class_overrides.csv and parameter_acceptance.csv only after review.
- Blocked non-approval risk note: create reviewed parameter decision records only for weak assumptions retained in release-scope claims
- Blocked non-approval risk note: parameter_acceptance.csv is missing
- Blocked non-approval risk note: create reviewed parameter decision rows only for weak assumptions retained in release-scope claims
- Blocked non-approval risk note: Draft recommendation could be overread as permission if copied into a target path.
- Blocked non-approval risk note: Study gate status remains false until reviewers record source-backed decisions.

Human reviewer action required:
- Blocked non-approval action: Inspect the listed review packets and evidence paths.
- Blocked non-approval action: Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Blocked non-approval action: Supply or regenerate the missing evidence items before deciding.
- Blocked non-approval action: Resolve each missing-evidence item listed in this record.
- Blocked non-approval action: After a real decision, create or update data/parameters/parameter_acceptance.csv.
- Blocked non-approval action: Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/parameters/parameter_acceptance.csv

### road_class_overrides

- Label: Road-Class Override Decision
- Related plan gates: `cached_osm_input`
- Recommendation: `blocked_missing_evidence`
- Reason: The gate still lacks source-backed, reviewer-decided, or upstream-complete evidence required by the current study audit.
- Formal target after human decision: `data/parameters/road_class_overrides.csv`
- Formal permission: `false`
- Human decision required: `true`

Review packets:
- docs/review_packets/cached_osm_input.md
- data/parameters/parameter_evidence_review_packet.csv
- data/parameters/parameter_source_readiness_packet.csv
- data/parameters/parameter_evidence_priority_packet.csv
- data/parameters/parameter_source_decision_packet.csv
- data/parameters/transfer_evidence_review_packet.csv
- data/parameters/road_evidence_review_packet.csv
- data/road/road_source_readiness_packet.csv
- data/road/road_source_decision_packet.csv
- data/road/road_evidence_priority_packet.csv
- data/parameters/rail_evidence_review_packet.csv
- data/rail/rail_fetch_readiness_packet.csv
- data/rail/rail_evidence_priority_packet.csv
- data/rail/rail_source_decision_packet.csv
- docs/review_packets/parameter_evidence.md
- docs/review_packets/rail_evidence.md

Source paths:
- data/parameters/parameter_sources.csv
- data/parameters/road_class_overrides_draft.csv
- data/parameters/rail_service_evidence.csv
- data/parameters/rail_station_bindings.csv
- data/parameters/parameter_source_readiness_packet.csv
- data/parameters/parameter_evidence_priority_packet.csv
- data/parameters/parameter_source_decision_packet.csv
- data/parameters/transfer_evidence_review_packet.csv
- data/road/road_source_readiness_packet.csv
- data/road/road_source_decision_packet.csv
- data/road/road_evidence_priority_packet.csv
- data/rail/rail_fetch_readiness_packet.csv
- data/rail/rail_evidence_priority_packet.csv
- data/rail/rail_source_decision_packet.csv
- data/parameters/road_class_overrides.csv

Evidence inspected:
- `data/parameters/parameter_sources.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/road_class_overrides_draft.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/rail_service_evidence.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/rail_station_bindings.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/parameter_source_readiness_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/parameter_evidence_priority_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/parameter_source_decision_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/transfer_evidence_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/road/road_source_readiness_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/road/road_source_decision_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/road/road_evidence_priority_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/rail/rail_fetch_readiness_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/rail/rail_evidence_priority_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/rail/rail_source_decision_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/road_class_overrides.csv`: present; formal artifact present; still requires validator review
- `docs/review_packets/cached_osm_input.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/parameter_evidence_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/road_evidence_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/rail_evidence_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/review_packets/parameter_evidence.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/review_packets/rail_evidence.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/parameter_evidence_source_request_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/parameter_source_readiness_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/parameter_evidence_priority_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/parameter_source_decision_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/transfer_evidence_review_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/road/road_evidence_source_request_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/road/road_source_readiness_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/road/road_source_decision_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/road/road_evidence_priority_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/rail/rail_timing_source_request_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/rail/rail_fetch_readiness_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/rail/rail_evidence_priority_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/rail/rail_source_decision_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/cache/pilot_region_road.graphml`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/cache/pilot_region_road_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/audit_road_evidence.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/audit_road_evidence_diagnostics.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/road_speed_evidence_candidates.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/road_capacity_evidence_candidates.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/road_evidence_review_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/road/road_evidence_source_request_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/road_source_readiness_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/road_source_decision_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/road_evidence_priority_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_road_speed_evidence.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_road_capacity_evidence.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_road_evidence_review_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_road_evidence_source_request_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_road_source_readiness_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_road_source_decision_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_road_evidence_priority_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/road_attribute_evidence_table.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/parameters/road_attribute_evidence_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_road_attribute_evidence.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/road_attribute_evidence.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_road_class_override_template.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/audit_road_overrides.py`: present; local supporting artifact present; evidence quality still requires human/source review

Missing evidence:
- Blocked non-approval item: replace weak field-level road override sources before treating speed, capacity, or base-disruption values as source-backed
- Blocked non-approval item: verify graph-adapter runs apply the reviewed override table before using road-calibration claims
- Blocked non-approval item: accepted pilot manifest does not record road_class_overrides_applied: true
- Blocked non-approval item: accepted pilot manifest does not record road_class_overrides_path
- Blocked non-approval item: accepted pilot manifest does not record road_class_overrides_sha256
- Blocked non-approval item: accepted pilot manifest graph_source does not record road_class_overrides
- Blocked non-approval item: road input evidence: review OSM maxspeed coverage and replace fallback free-flow speeds where release-scope claims require calibration
- Blocked non-approval item: road input evidence: replace road-class capacity proxies with traffic counts, agency capacity references, or benchmark-field-fit values
- Blocked non-approval item: road input evidence: replace road-class base disruption probabilities with hazard, incident, or reviewer-retained scenario evidence
- Blocked non-approval item: road input evidence: treat this as road-input evidence only; route plausibility and traffic validation remain separate gates
- Blocked non-approval item: road override evidence: replace weak field-level road override sources before treating speed, capacity, or base-disruption values as source-backed
- Blocked non-approval item: road override evidence: verify graph-adapter runs apply the reviewed override table before using road-calibration claims
- Blocked non-approval item: road override application: accepted pilot manifest does not record road_class_overrides_applied: true
- Blocked non-approval item: road override application: accepted pilot manifest does not record road_class_overrides_path
- Blocked non-approval item: road override application: accepted pilot manifest does not record road_class_overrides_sha256
- Blocked non-approval item: road override application: accepted pilot manifest graph_source does not record road_class_overrides
- Blocked non-approval item: road source readiness: cached lane-count evidence has no parseable observed lane rows
- Blocked non-approval item: road source readiness: data/parameters/road_class_overrides.csv is absent
- Blocked non-approval item: road source readiness: capacity and disruption evidence still require external source or formal assumption decisions
- Blocked non-approval item: road source readiness: this packet is source-review triage only and cannot create road-class overrides
- Blocked non-approval item: road source decision: reviewed road_class_overrides.csv is absent
- Blocked non-approval item: road source decision: road source decisions are pending for speed, capacity, disruption, benchmark, and override-application requests
- Blocked non-approval item: road source decision: retained road assumptions require source-backed updates, sensitivity-only limits, benchmark-only limits, or explicit reviewer decisions
- Blocked non-approval item: road source decision: reviewed_road_class_override_application_request: data/parameters/road_class_overrides.csv is absent
- Blocked non-approval item: road source decision: road_capacity_lane_count_source_request: cached lane-count evidence has no parseable observed lane rows

Residual risks:
- Blocked non-approval risk note: Replace weak road, rail, and parameter assumptions with source-backed evidence or explicit reviewer-retained overrides.
- Blocked non-approval risk note: Create road_class_overrides.csv and parameter_acceptance.csv only after review.
- Blocked non-approval risk note: replace weak field-level road override sources before treating speed, capacity, or base-disruption values as source-backed
- Blocked non-approval risk note: verify graph-adapter runs apply the reviewed override table before using road-calibration claims
- Blocked non-approval risk note: accepted pilot manifest does not record road_class_overrides_applied: true
- Blocked non-approval risk note: accepted pilot manifest does not record road_class_overrides_path
- Blocked non-approval risk note: accepted pilot manifest does not record road_class_overrides_sha256
- Blocked non-approval risk note: accepted pilot manifest graph_source does not record road_class_overrides
- Blocked non-approval risk note: Draft recommendation could be overread as permission if copied into a target path.
- Blocked non-approval risk note: Study gate status remains false until reviewers record source-backed decisions.

Human reviewer action required:
- Blocked non-approval action: Inspect the listed review packets and evidence paths.
- Blocked non-approval action: Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Blocked non-approval action: Supply or regenerate the missing evidence items before deciding.
- Blocked non-approval action: Resolve each missing-evidence item listed in this record.
- Blocked non-approval action: After a real decision, create or update data/parameters/road_class_overrides.csv.
- Blocked non-approval action: Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/parameters/road_class_overrides.csv
- results/realworld_pilot/pilot_full_manifest.json
- results/realworld_pilot/pilot_full_results.csv
- data/manifests/experiment_acceptance.json

### validation_package

- Label: Benchmark Decision
- Related plan gates: `validation_package`
- Recommendation: `blocked_requires_human_decision`
- Reason: Repository review packets exist, but a source-backed human decision is still required before any formal artifact can be created.
- Formal target after human decision: `data/manifests/validation_acceptance.json`
- Formal permission: `false`
- Human decision required: `true`

Review packets:
- docs/review_packets/validation_package.md
- data/validation/validation_review_packet.csv
- data/validation/validation_strategy_readiness_packet.csv
- data/validation/validation_benchmark_readiness_packet.csv
- data/validation/validation_benchmark_decision_packet.csv

Source paths:
- data/validation/validation_review_packet.csv
- data/validation/validation_strategy_readiness_packet.csv
- data/validation/validation_benchmark_readiness_packet.csv
- data/validation/validation_benchmark_decision_packet.csv
- data/validation/osrm_route_benchmark_manifest.json
- data/validation/accessibility_loss.csv
- data/validation/canonical_route_road_evidence_exposure.csv
- data/manifests/validation_acceptance.json

Evidence inspected:
- `data/validation/validation_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/validation_strategy_readiness_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/validation_benchmark_readiness_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/validation_benchmark_decision_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/osrm_route_benchmark_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/accessibility_loss.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/canonical_route_road_evidence_exposure.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/validation_acceptance.json`: absent; formal artifact absent; expected until a source-backed reviewer decision exists
- `docs/review_packets/validation_package.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/validation_review_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/validation_strategy_readiness_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/validation_benchmark_readiness_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/validation_benchmark_decision_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/osrm_route_benchmark_manifest.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/validation_review_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/validation_strategy_readiness_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/validation_benchmark_readiness_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/validation_benchmark_decision_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/validation_summary.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/external_route_benchmarks.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/external_route_benchmarks_osrm.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/accessibility_loss_summary.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/canonical_route_road_evidence_exposure_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/run_plausibility_validation.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/run_accessibility_loss_analysis.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_route_road_evidence_exposure.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/run_osrm_route_benchmark.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_osrm_snapshot_manifest.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_validation_benchmark_readiness_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_validation_benchmark_decision_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_validation_review_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_validation_strategy_readiness_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review

Missing evidence:
- Blocked non-approval item: create an explicit validation decision record after benchmark-strategy review
- Blocked non-approval item: resolve benchmark strategy-readiness blockers before benchmark decision record
- Blocked non-approval item: benchmark strategy readiness: validation_acceptance.json is absent
- Blocked non-approval item: benchmark strategy readiness: route-level road evidence exposure remains weak until road evidence gates close
- Blocked non-approval item: review benchmark strategy-readiness human-decision items before benchmark decision record
- Blocked non-approval item: resolve benchmark-decision blockers before benchmark decision record
- Blocked non-approval item: benchmark decision: validation summary still declares scaffold or sanity scope
- Blocked non-approval item: benchmark decision: route-level road evidence exposure remains weak until road evidence gates close
- Blocked non-approval item: benchmark decision: data/manifests/validation_acceptance.json is absent
- Blocked non-approval item: review benchmark-decision human-decision items before benchmark decision record
- Blocked non-approval item: revise validation summary from scaffold/sanity evidence to accepted publication-level validation scope after review
- Blocked non-approval item: data/manifests/validation_acceptance.json is absent

Residual risks:
- Blocked non-approval risk note: Review validation thresholds, benchmark scope, snapshot pinning, and failure cases.
- Blocked non-approval risk note: Create validation_acceptance.json after benchmark-strategy review.
- Blocked non-approval risk note: create an explicit validation decision record after benchmark-strategy review
- Blocked non-approval risk note: create an explicit benchmark decision record after benchmark-strategy review
- Blocked non-approval risk note: Draft recommendation could be overread as permission if copied into a target path.
- Blocked non-approval risk note: Study gate status remains false until reviewers record source-backed decisions.

Human reviewer action required:
- Blocked non-approval action: Inspect the listed review packets and evidence paths.
- Blocked non-approval action: Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Blocked non-approval action: Decide whether to clear, reject, or keep blocked based on the existing review packet evidence.
- Blocked non-approval action: Resolve each missing-evidence item listed in this record.
- Blocked non-approval action: After a real decision, create or update data/manifests/validation_acceptance.json.
- Blocked non-approval action: Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/manifests/validation_acceptance.json

### sensitivity_analysis

- Label: Sensitivity Analysis Decision
- Related plan gates: `sensitivity_analysis`
- Recommendation: `blocked_missing_evidence`
- Reason: The gate still lacks source-backed, reviewer-decided, or upstream-complete evidence required by the current study audit.
- Formal target after human decision: `data/manifests/sensitivity_acceptance.json`
- Formal permission: `false`
- Human decision required: `true`

Review packets:
- docs/review_packets/sensitivity_analysis.md
- data/validation/sensitivity_review_packet.csv
- data/validation/sensitivity_index_review_packet.csv
- data/validation/sensitivity_strategy_readiness_packet.csv
- data/validation/sensitivity_method_decision_packet.csv

Source paths:
- results/realworld_pilot/morris_manifest.json
- results/realworld_pilot/morris_results.csv
- results/realworld_pilot/morris_summary.csv
- data/validation/sensitivity_strategy_readiness_packet.csv
- data/validation/sensitivity_index_review_packet.csv
- data/validation/sensitivity_method_decision_packet.csv
- data/manifests/sensitivity_acceptance.json

Evidence inspected:
- `results/realworld_pilot/morris_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `results/realworld_pilot/morris_results.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `results/realworld_pilot/morris_summary.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/sensitivity_strategy_readiness_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/sensitivity_index_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/sensitivity_method_decision_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/sensitivity_acceptance.json`: absent; formal artifact absent; expected until a source-backed reviewer decision exists
- `docs/review_packets/sensitivity_analysis.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/sensitivity_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/sensitivity_review_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/sensitivity_index_review_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/sensitivity_index_review_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/sensitivity_strategy_readiness_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/sensitivity_method_decision_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/sensitivity_method_decision_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/run_sensitivity.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/sensitivity_strategy_readiness_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/audit_sensitivity_diagnostics.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_sensitivity_review_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_sensitivity_index_review_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_sensitivity_strategy_readiness_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_sensitivity_method_decision_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review

Missing evidence:
- Blocked non-approval item: create an explicit sensitivity decision record after SALib output and Sobol-decision review
- Blocked non-approval item: resolve sensitivity strategy-readiness blockers before sensitivity decision record
- Blocked non-approval item: sensitivity strategy readiness: sensitivity outputs use a reduced analysis graph
- Blocked non-approval item: sensitivity strategy readiness: current sensitivity result scope is scaffold or not calibrated
- Blocked non-approval item: sensitivity strategy readiness: Morris-vs-Sobol method decision is not recorded in formal acceptance
- Blocked non-approval item: sensitivity strategy readiness: data/manifests/sensitivity_acceptance.json is absent
- Blocked non-approval item: review sensitivity strategy-readiness human-decision items before sensitivity decision record
- Blocked non-approval item: accept sensitivity outputs on final graph/evidence scope; current Morris outputs are scaffold-level
- Blocked non-approval item: data/manifests/sensitivity_acceptance.json is absent

Residual risks:
- Blocked non-approval risk note: Review parameter ranges and decide whether Morris is enough or Sobol is required.
- Blocked non-approval risk note: Create sensitivity_acceptance.json after final input and graph scope are accepted.
- Blocked non-approval risk note: create an explicit sensitivity decision record after SALib output and Sobol-decision review
- Blocked non-approval risk note: create an explicit sensitivity decision record after SALib output and Sobol-decision review
- Blocked non-approval risk note: Draft recommendation could be overread as permission if copied into a target path.
- Blocked non-approval risk note: Study gate status remains false until reviewers record source-backed decisions.

Human reviewer action required:
- Blocked non-approval action: Inspect the listed review packets and evidence paths.
- Blocked non-approval action: Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Blocked non-approval action: Supply or regenerate the missing evidence items before deciding.
- Blocked non-approval action: Resolve each missing-evidence item listed in this record.
- Blocked non-approval action: After a real decision, create or update data/manifests/sensitivity_acceptance.json.
- Blocked non-approval action: Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/manifests/sensitivity_acceptance.json

### full_experiment_output

- Label: Experiment Output Decision
- Related plan gates: `full_experiment_output`
- Recommendation: `blocked_missing_evidence`
- Reason: The gate still lacks source-backed, reviewer-decided, or upstream-complete evidence required by the current study audit.
- Formal target after human decision: `data/manifests/experiment_acceptance.json`
- Formal permission: `false`
- Human decision required: `true`

Review packets:
- docs/review_packets/full_experiment_output.md
- data/manifests/experiment_package_review_packet.csv
- data/manifests/experiment_strategy_readiness_packet.csv
- data/manifests/experiment_design_decision_packet.csv

Source paths:
- results/realworld_pilot/pilot_full_manifest.json
- results/realworld_pilot/pilot_full_results.csv
- results/realworld_pilot/pilot_full_summary.csv
- data/manifests/experiment_package_review_packet.csv
- data/manifests/experiment_strategy_readiness_packet.csv
- data/manifests/experiment_design_decision_packet.csv
- data/manifests/experiment_acceptance.json

Evidence inspected:
- `results/realworld_pilot/pilot_full_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `results/realworld_pilot/pilot_full_results.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `results/realworld_pilot/pilot_full_summary.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/experiment_package_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/experiment_strategy_readiness_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/experiment_design_decision_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/experiment_acceptance.json`: absent; formal artifact absent; expected until a source-backed reviewer decision exists
- `docs/review_packets/full_experiment_output.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/run_pilot_experiments.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/scenarios/disruption_scenarios.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/scenarios/policy_alternatives.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/experiment_package_review_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/experiment_strategy_readiness_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/experiment_design_decision_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/experiment_design_decision_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/experiment_package_review_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/experiment_strategy_readiness_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_experiment_design_decision_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review

Missing evidence:
- Blocked non-approval item: create an explicit experiment decision record after input checks, graph-scope, and scenario-policy-seed review
- Blocked non-approval item: resolve experiment strategy-readiness blockers before experiment decision record
- Blocked non-approval item: experiment strategy readiness: current full-pilot result scope is scaffold or not calibrated
- Blocked non-approval item: experiment strategy readiness: full-pilot outputs depend on a graph method that has no graph-scale decision
- Blocked non-approval item: experiment strategy readiness: upstream input, road override, parameter, benchmark, or provenance gates are unresolved
- Blocked non-approval item: experiment strategy readiness: data/manifests/experiment_acceptance.json is absent
- Blocked non-approval item: review experiment strategy-readiness human-decision items before experiment decision record
- Blocked non-approval item: resolve experiment design-decision blockers before experiment decision record
- Blocked non-approval item: experiment design decision: experiment outputs depend on a graph method that is not selected by review
- Blocked non-approval item: experiment design decision: upstream input, road override, parameter, validation, or provenance gates are not closed
- Blocked non-approval item: experiment design decision: current full-pilot result scope is scaffold or not calibrated
- Blocked non-approval item: experiment design decision: data/manifests/experiment_acceptance.json is absent
- Blocked non-approval item: review experiment design-decision human-decision items before experiment decision record
- Blocked non-approval item: accept or regenerate full pilot outputs after input checks and graph-scale decision
- Blocked non-approval item: review experiment-package rows before formal experiment acceptance
- Blocked non-approval item: data/manifests/experiment_acceptance.json is absent

Residual risks:
- Blocked non-approval risk note: Regenerate or accept full outputs after input, graph-scale, and validation gates close.
- Blocked non-approval risk note: Create experiment_acceptance.json with matching run profile and row counts.
- Blocked non-approval risk note: create an explicit experiment decision record after input checks, graph-scope, and scenario-policy-seed review
- Blocked non-approval risk note: create an explicit experiment decision record after input-evidence review, graph-scope, and scenario-policy-seed review
- Blocked non-approval risk note: Draft recommendation could be overread as permission if copied into a target path.
- Blocked non-approval risk note: Study gate status remains false until reviewers record source-backed decisions.

Human reviewer action required:
- Blocked non-approval action: Inspect the listed review packets and evidence paths.
- Blocked non-approval action: Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Blocked non-approval action: Supply or regenerate the missing evidence items before deciding.
- Blocked non-approval action: Resolve each missing-evidence item listed in this record.
- Blocked non-approval action: After a real decision, create or update data/manifests/experiment_acceptance.json.
- Blocked non-approval action: Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/manifests/experiment_acceptance.json

### manuscript_report_alignment

- Label: Manuscript/Report Alignment Decision
- Related plan gates: `manuscript_report_alignment`
- Recommendation: `blocked_missing_evidence`
- Reason: The gate still lacks source-backed, reviewer-decided, or upstream-complete evidence required by the current study audit.
- Formal target after human decision: `data/manifests/manuscript_acceptance.json`
- Formal permission: `false`
- Human decision required: `true`

Review packets:
- docs/review_packets/manuscript_report_alignment.md
- data/manifests/claim_alignment_review_packet.csv
- data/manifests/figure_table_review_packet.csv
- data/manifests/manuscript_report_decision_packet.csv

Source paths:
- paper/paper_draft.md
- report_draft.md
- report.docx
- results/realworld_pilot/tables/figure_table_manifest.json
- data/manifests/claim_alignment_review_packet.csv
- data/manifests/figure_table_review_packet.csv
- data/manifests/manuscript_report_decision_packet.csv
- data/manifests/manuscript_acceptance.json

Evidence inspected:
- `paper/paper_draft.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `report_draft.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `report.docx`: present; local supporting artifact present; evidence quality still requires human/source review
- `results/realworld_pilot/tables/figure_table_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/claim_alignment_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/figure_table_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/manuscript_report_decision_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/manuscript_acceptance.json`: absent; formal artifact absent; expected until a source-backed reviewer decision exists
- `docs/review_packets/manuscript_report_alignment.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/audit_publication_readiness.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/current_goal_completion_audit.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/current_goal_completion_audit.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/claim_alignment_review_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/figure_table_review_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/manuscript_report_decision_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/figure_table_review_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/manuscript_report_decision_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/claim_alignment_review_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review

Missing evidence:
- Blocked non-approval item: create an explicit manuscript/report decision record after evidence gates, figures, paper, report, and claim boundaries are reviewed
- Blocked non-approval item: close evidence gates before release-scope paper/report claims
- Blocked non-approval item: revise figure/table claim boundary from scaffold to accepted study scope
- Blocked non-approval item: resolve figure/table review blockers before manuscript acceptance
- Blocked non-approval item: figure/table review: figure/table outputs depend on reduced analysis graph scope
- Blocked non-approval item: figure/table review: figure/table source outputs remain scaffold or not calibrated
- Blocked non-approval item: figure/table review: data/manifests/manuscript_acceptance.json is absent
- Blocked non-approval item: review figure/table human-review rows before manuscript acceptance
- Blocked non-approval item: review or revise claim-alignment overclaim candidates before manuscript acceptance
- Blocked non-approval item: claim alignment: formal manuscript/report review record is absent
- Blocked non-approval item: claim alignment: claim-alignment rows are review aids and do not approve manuscript claims
- Blocked non-approval item: claim alignment: evidence gates remain blocked, so result claims cannot be treated as target-study claims
- Blocked non-approval item: resolve manuscript/report decision blockers before manuscript acceptance
- Blocked non-approval item: manuscript/report decision: figure/table outputs depend on reduced analysis graph scope; figure/table source outputs remain scaffold or not calibrated; data/manifests/manuscript_acceptance.json is absent
- Blocked non-approval item: manuscript/report decision: claim-alignment packet has 52 rows requiring revision or explicit retention
- Blocked non-approval item: manuscript/report decision: upstream evidence gates blocked: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output
- Blocked non-approval item: manuscript/report decision: data/manifests/manuscript_acceptance.json is absent
- Blocked non-approval item: review manuscript/report human-decision rows before manuscript acceptance
- Blocked non-approval item: data/manifests/manuscript_acceptance.json is absent

Residual risks:
- Blocked non-approval risk note: Revise or hold claims until all supporting evidence gates are accepted.
- Blocked non-approval risk note: Create manuscript_acceptance.json after claim-by-claim review.
- Blocked non-approval risk note: create an explicit manuscript/report decision record after evidence gates, figures, paper, report, and claim boundaries are reviewed
- Blocked non-approval risk note: create an explicit manuscript/report decision record after evidence gates, figures, paper, report, and claim boundaries are reviewed
- Blocked non-approval risk note: Draft recommendation could be overread as permission if copied into a target path.
- Blocked non-approval risk note: Study gate status remains false until reviewers record source-backed decisions.

Human reviewer action required:
- Blocked non-approval action: Inspect the listed review packets and evidence paths.
- Blocked non-approval action: Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Blocked non-approval action: Supply or regenerate the missing evidence items before deciding.
- Blocked non-approval action: Resolve each missing-evidence item listed in this record.
- Blocked non-approval action: After a real decision, create or update data/manifests/manuscript_acceptance.json.
- Blocked non-approval action: Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/manifests/manuscript_acceptance.json

### reproducibility

- Label: Reproducibility Decision
- Related plan gates: `reproducibility`
- Recommendation: `blocked_missing_evidence`
- Reason: The gate still lacks source-backed, reviewer-decided, or upstream-complete evidence required by the current study audit.
- Formal target after human decision: `data/manifests/reproducibility_acceptance.json`
- Formal permission: `false`
- Human decision required: `true`

Review packets:
- docs/review_packets/reproducibility.md
- data/validation/reproducibility_review_packet.csv
- data/validation/reproducibility_decision_packet.csv
- data/validation/tracked_artifact_audit.csv

Source paths:
- data/manifests/reproducibility_manifest.json
- data/validation/reproducibility_review_manifest.json
- data/validation/reproducibility_decision_packet.csv
- data/validation/reproducibility_decision_manifest.json
- docs/reproducibility_decision_packet.md
- data/validation/reproducibility_smoke_manifest.json
- data/validation/clean_checkout_reproducibility_smoke_manifest.json
- data/validation/tracked_artifact_audit_manifest.json
- data/manifests/current_goal_completion_audit.json
- docs/reproducibility_package.md
- requirements.txt
- data/manifests/reproducibility_acceptance.json

Evidence inspected:
- `data/manifests/reproducibility_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/reproducibility_review_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/reproducibility_decision_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/reproducibility_decision_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/reproducibility_decision_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/reproducibility_smoke_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/clean_checkout_reproducibility_smoke_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/tracked_artifact_audit_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/current_goal_completion_audit.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/reproducibility_package.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `requirements.txt`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/reproducibility_acceptance.json`: absent; formal artifact absent; expected until a source-backed reviewer decision exists
- `docs/review_packets/reproducibility.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/reproducibility_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/tracked_artifact_audit.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/audit_plan_artifacts.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/reproducibility_smoke.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/clean_checkout_reproducibility_smoke.md`: present; local supporting artifact present; evidence quality still requires human/source review

Missing evidence:
- Blocked non-approval item: create an explicit reproducibility decision record after clean-checkout reproduction review, artifact regeneration, manifest review, and import-boundary checks
- Blocked non-approval item: replace scaffold-only manifest with clean-checkout final reproduction package
- Blocked non-approval item: resolve reproducibility decision blockers before reproducibility acceptance
- Blocked non-approval item: reproducibility decision: reproducibility manifest remains scaffold-only
- Blocked non-approval item: reproducibility decision: data/manifests/reproducibility_acceptance.json is absent
- Blocked non-approval item: review reproducibility human-decision rows before reproducibility acceptance
- Blocked non-approval item: data/manifests/reproducibility_acceptance.json is absent

Residual risks:
- Blocked non-approval risk note: Run or document clean-checkout reproduction review with command log and artifact regeneration evidence.
- Blocked non-approval risk note: Create reproducibility_acceptance.json only after accepted reproduction scope is complete.
- Blocked non-approval risk note: create an explicit reproducibility decision record after clean-checkout reproduction review, artifact regeneration, manifest review, and import-boundary checks
- Blocked non-approval risk note: create an explicit reproducibility decision record after clean-checkout reproduction review, artifact regeneration, manifest review, and import-boundary checks
- Blocked non-approval risk note: Draft recommendation could be overread as permission if copied into a target path.
- Blocked non-approval risk note: Study gate status remains false until reviewers record source-backed decisions.

Human reviewer action required:
- Blocked non-approval action: Inspect the listed review packets and evidence paths.
- Blocked non-approval action: Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Blocked non-approval action: Supply or regenerate the missing evidence items before deciding.
- Blocked non-approval action: Resolve each missing-evidence item listed in this record.
- Blocked non-approval action: After a real decision, create or update data/manifests/reproducibility_acceptance.json.
- Blocked non-approval action: Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/manifests/reproducibility_acceptance.json

### final_audit_document

- Label: Study-Closeout Audit Document
- Related plan gates: `final_audit`
- Recommendation: `blocked_missing_evidence`
- Reason: The gate still lacks source-backed, reviewer-decided, or upstream-complete evidence required by the current study audit.
- Formal target after human decision: `docs/final_study_audit.md`
- Formal permission: `false`
- Human decision required: `true`

Review packets:
- docs/review_packets/final_audit.md
- data/manifests/final_audit_decision_packet.csv

Source paths:
- docs/current_goal_completion_audit.md
- data/manifests/current_goal_completion_audit.json
- data/manifests/acceptance_orchestration_manifest.json
- data/manifests/formal_acceptance_evidence_matrix.csv
- data/manifests/formal_acceptance_package_audit.json
- data/manifests/final_audit_decision_packet.csv
- data/manifests/final_audit_decision_manifest.json
- docs/final_study_audit.md

Evidence inspected:
- `docs/current_goal_completion_audit.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/current_goal_completion_audit.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/acceptance_orchestration_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/formal_acceptance_evidence_matrix.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/formal_acceptance_package_audit.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/final_audit_decision_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/final_audit_decision_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/final_study_audit.md`: absent; formal artifact absent; expected until a source-backed reviewer decision exists
- `docs/review_packets/final_audit.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/formal_acceptance_evidence_matrix_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/final_audit_decision_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/audit_final_study_readiness.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/final_audit_acceptance.json`: absent; local supporting artifact absent

Missing evidence:
- Blocked non-approval item: create docs/final_study_audit.md after all other gates close
- Blocked non-approval item: create an explicit closeout-audit decision record only after prompt-to-artifact review confirms every closeout gate is closed
- Blocked non-approval item: resolve closeout-audit decision blockers before closeout-audit acceptance
- Blocked non-approval item: closeout-audit decision: pre-closeout gates remain blocked: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, structured_disruptions, sensitivity_analysis, full_experiment_output, manuscript_report_alignment, reproducibility
- Blocked non-approval item: closeout-audit decision: required formal decision artifacts are absent: data/manifests/pilot_acceptance.json, data/manifests/graph_scale_acceptance.json, data/manifests/provenance_acceptance.json, data/parameters/parameter_acceptance.csv, data/manifests/validation_acceptance.json, data/manifests/sensitivity_acceptance.json, data/manifests/experiment_acceptance.json, data/manifests/manuscript_acceptance.json, data/manifests/reproducibility_acceptance.json, docs/final_study_audit.md, data/manifests/final_audit_acceptance.json
- Blocked non-approval item: closeout-audit decision: docs/final_study_audit.md is absent
- Blocked non-approval item: closeout-audit decision: data/manifests/final_audit_acceptance.json is absent
- Blocked non-approval item: review closeout-audit human-decision rows before closeout-audit acceptance
- Blocked non-approval item: all pre-closeout gates must be ready before closeout audit acceptance: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, structured_disruptions, sensitivity_analysis, full_experiment_output, manuscript_report_alignment, reproducibility
- Blocked non-approval item: docs/final_study_audit.md is absent

Residual risks:
- Blocked non-approval risk note: After all pre-closeout gates are ready, write the independent prompt-to-artifact closeout audit.
- Blocked non-approval risk note: Create final_audit_acceptance.json only when gate lists and readiness counts match current evidence.
- Blocked non-approval risk note: create docs/final_study_audit.md after all other gates close
- Blocked non-approval risk note: Draft recommendation could be overread as permission if copied into a target path.
- Blocked non-approval risk note: Study gate status remains false until reviewers record source-backed decisions.

Human reviewer action required:
- Blocked non-approval action: Inspect the listed review packets and evidence paths.
- Blocked non-approval action: Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Blocked non-approval action: Supply or regenerate the missing evidence items before deciding.
- Blocked non-approval action: Wait until prerequisite formal gates have source-backed reviewer decisions before creating independent-audit artifacts.
- Blocked non-approval action: Resolve each missing-evidence item listed in this record.
- Blocked non-approval action: After a real decision, create or update docs/final_study_audit.md.
- Blocked non-approval action: Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- docs/final_study_audit.md
- data/manifests/final_audit_acceptance.json

### final_audit

- Label: Closeout Audit Decision
- Related plan gates: `final_audit`
- Recommendation: `blocked_missing_evidence`
- Reason: The gate still lacks source-backed, reviewer-decided, or upstream-complete evidence required by the current study audit.
- Formal target after human decision: `data/manifests/final_audit_acceptance.json`
- Formal permission: `false`
- Human decision required: `true`

Review packets:
- docs/review_packets/final_audit.md
- data/manifests/final_audit_decision_packet.csv

Source paths:
- docs/current_goal_completion_audit.md
- data/manifests/current_goal_completion_audit.json
- data/manifests/acceptance_orchestration_manifest.json
- data/manifests/formal_acceptance_evidence_matrix.csv
- data/manifests/formal_acceptance_package_audit.json
- data/manifests/final_audit_decision_packet.csv
- data/manifests/final_audit_decision_manifest.json
- data/manifests/final_audit_acceptance.json

Evidence inspected:
- `docs/current_goal_completion_audit.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/current_goal_completion_audit.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/acceptance_orchestration_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/formal_acceptance_evidence_matrix.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/formal_acceptance_package_audit.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/final_audit_decision_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/final_audit_decision_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/final_audit_acceptance.json`: absent; formal artifact absent; expected until a source-backed reviewer decision exists
- `docs/review_packets/final_audit.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/formal_acceptance_evidence_matrix_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/final_audit_decision_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/audit_final_study_readiness.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/final_study_audit.md`: absent; local supporting artifact absent

Missing evidence:
- Blocked non-approval item: create an explicit closeout-audit decision record only after prompt-to-artifact review confirms every closeout gate is closed
- Blocked non-approval item: create docs/final_study_audit.md after all other gates close
- Blocked non-approval item: resolve closeout-audit decision blockers before closeout-audit acceptance
- Blocked non-approval item: closeout-audit decision: pre-closeout gates remain blocked: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, structured_disruptions, sensitivity_analysis, full_experiment_output, manuscript_report_alignment, reproducibility
- Blocked non-approval item: closeout-audit decision: required formal decision artifacts are absent: data/manifests/pilot_acceptance.json, data/manifests/graph_scale_acceptance.json, data/manifests/provenance_acceptance.json, data/parameters/parameter_acceptance.csv, data/manifests/validation_acceptance.json, data/manifests/sensitivity_acceptance.json, data/manifests/experiment_acceptance.json, data/manifests/manuscript_acceptance.json, data/manifests/reproducibility_acceptance.json, docs/final_study_audit.md, data/manifests/final_audit_acceptance.json
- Blocked non-approval item: closeout-audit decision: docs/final_study_audit.md is absent
- Blocked non-approval item: closeout-audit decision: data/manifests/final_audit_acceptance.json is absent
- Blocked non-approval item: review closeout-audit human-decision rows before closeout-audit acceptance
- Blocked non-approval item: all pre-closeout gates must be ready before closeout audit acceptance: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, structured_disruptions, sensitivity_analysis, full_experiment_output, manuscript_report_alignment, reproducibility
- Blocked non-approval item: data/manifests/final_audit_acceptance.json is absent

Residual risks:
- Blocked non-approval risk note: After all pre-closeout gates are ready, write the independent prompt-to-artifact closeout audit.
- Blocked non-approval risk note: Create final_audit_acceptance.json only when gate lists and readiness counts match current evidence.
- Blocked non-approval risk note: create an explicit closeout-audit decision record only after prompt-to-artifact review confirms every closeout gate is closed
- Blocked non-approval risk note: create an explicit closeout audit decision record only after prompt-to-artifact review confirms every prerequisite gate is closed
- Blocked non-approval risk note: Draft recommendation could be overread as permission if copied into a target path.
- Blocked non-approval risk note: Study gate status remains false until reviewers record source-backed decisions.

Human reviewer action required:
- Blocked non-approval action: Inspect the listed review packets and evidence paths.
- Blocked non-approval action: Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Blocked non-approval action: Supply or regenerate the missing evidence items before deciding.
- Blocked non-approval action: Wait until prerequisite formal gates have source-backed reviewer decisions before creating independent-audit artifacts.
- Blocked non-approval action: Resolve each missing-evidence item listed in this record.
- Blocked non-approval action: After a real decision, create or update data/manifests/final_audit_acceptance.json.
- Blocked non-approval action: Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/manifests/final_audit_acceptance.json
- docs/final_study_audit.md

## Use

Use these draft records to decide whether a human reviewer should clear, reject, or keep each gate blocked. Do not move any draft JSON into a formal decision path unless a reviewer replaces the draft fields with source-backed decision evidence and then reruns the formal package validators.
