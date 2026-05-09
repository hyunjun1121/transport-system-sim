# Formal Acceptance Pre-Review

Draft pre-review recommendations only. These records classify remaining formal acceptance gates for human reviewers; they do not create formal approval, certify evidence, validate licenses, calibrate results, or mark the final study complete.

## Summary

- Draft records: 12
- Recommendation counts: `{'blocked_requires_human_decision': 4, 'blocked_missing_evidence': 8}`
- Human decisions required: 12
- Formal approval made: `false`
- Final-study ready: `false`
- Can mark complete: `false`
- Draft directory: `data/manifests/draft_acceptance`

## Gate Recommendations

| Gate | Current Status | Recommendation | Formal Target | Missing Evidence | Human Action |
| --- | --- | --- | --- | --- | --- |
| pilot_region_accepted | `blocked` | `blocked_requires_human_decision` | `data/manifests/pilot_acceptance.json` | create an explicit pilot acceptance record after privacy and case-scope review<br>resolve pilot-region decision blockers before pilot acceptance<br>+5 more | Inspect the listed review packets and evidence paths.<br>Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| graph_scale_strategy | `blocked` | `blocked_requires_human_decision` | `data/manifests/graph_scale_acceptance.json` | create an explicit graph-scale acceptance record after source-vs-analysis graph review<br>resolve graph-scale strategy-readiness blockers before graph-scale acceptance<br>+11 more | Inspect the listed review packets and evidence paths.<br>Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| data_provenance | `blocked` | `blocked_requires_human_decision` | `data/manifests/provenance_acceptance.json` | create an explicit provenance acceptance record after source, license, snapshot, privacy, and reproducibility review<br>replace scaffold-only reproducibility manifest with accepted source/license/snapshot provenance<br>+20 more | Inspect the listed review packets and evidence paths.<br>Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| parameter_acceptance | `blocked` | `blocked_missing_evidence` | `data/parameters/parameter_acceptance.csv` | create reviewed parameter acceptance records only for weak assumptions retained in final claims<br>parameter_acceptance.csv is missing<br>+33 more | Inspect the listed review packets and evidence paths.<br>Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| road_class_overrides | `blocked` | `blocked_missing_evidence` | `data/parameters/road_class_overrides.csv` | replace the draft road-class override worksheet with a reviewed road_class_overrides.csv table containing source-backed speed, capacity, and base-disruption evidence<br>apply the reviewed overrides when adapting the pilot graph if final claims require calibrated road inputs<br>+17 more | Inspect the listed review packets and evidence paths.<br>Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| validation_package | `blocked` | `blocked_requires_human_decision` | `data/manifests/validation_acceptance.json` | create an explicit validation acceptance record after benchmark-strategy review<br>resolve validation strategy-readiness blockers before validation acceptance<br>+10 more | Inspect the listed review packets and evidence paths.<br>Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| sensitivity_analysis | `blocked` | `blocked_missing_evidence` | `data/manifests/sensitivity_acceptance.json` | create an explicit sensitivity acceptance record after SALib output and Sobol-decision review<br>resolve sensitivity strategy-readiness blockers before sensitivity acceptance<br>+7 more | Inspect the listed review packets and evidence paths.<br>Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| full_experiment_output | `blocked` | `blocked_missing_evidence` | `data/manifests/experiment_acceptance.json` | create an explicit experiment acceptance record after input validation, graph-scope, and scenario-policy-seed review<br>resolve experiment strategy-readiness blockers before experiment acceptance<br>+14 more | Inspect the listed review packets and evidence paths.<br>Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| manuscript_report_alignment | `blocked` | `blocked_missing_evidence` | `data/manifests/manuscript_acceptance.json` | create an explicit manuscript/report acceptance record after evidence gates, figures, paper, report, and claim boundaries are reviewed<br>close evidence gates before final paper/report claims<br>+17 more | Inspect the listed review packets and evidence paths.<br>Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| reproducibility | `blocked` | `blocked_missing_evidence` | `data/manifests/reproducibility_acceptance.json` | create an explicit reproducibility acceptance record after clean-checkout validation, artifact regeneration, manifest review, and import-boundary checks<br>replace scaffold-only manifest with clean-checkout final reproduction package<br>+5 more | Inspect the listed review packets and evidence paths.<br>Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+4 more |
| final_audit_document | `blocked` | `blocked_missing_evidence` | `docs/final_study_audit.md` | create docs/final_study_audit.md after all other gates close<br>create an explicit final-audit acceptance record only after prompt-to-artifact review confirms every final gate is closed<br>+8 more | Inspect the listed review packets and evidence paths.<br>Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+5 more |
| final_audit | `blocked` | `blocked_missing_evidence` | `data/manifests/final_audit_acceptance.json` | create an explicit final-audit acceptance record only after prompt-to-artifact review confirms every final gate is closed<br>create docs/final_study_audit.md after all other gates close<br>+8 more | Inspect the listed review packets and evidence paths.<br>Record an explicit source-backed reviewer decision; do not use this draft record as approval.<br>+5 more |

## Gate Details

### pilot_region_accepted

- Label: Pilot Region Acceptance
- Related plan gates: `pilot_region_accepted`
- Recommendation: `blocked_requires_human_decision`
- Reason: Repository review packets exist, but a source-backed human decision is still required before any formal artifact can be created.
- Formal target after human decision: `data/manifests/pilot_acceptance.json`
- Formal approval: `false`
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
- `data/manifests/pilot_acceptance.json`: absent; formal artifact absent; expected until source-backed human approval exists
- `docs/review_packets/pilot_region_accepted.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/current_goal_completion_audit.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/current_goal_completion_audit.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/pilot_privacy_review_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/pilot_region_decision_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/write_pilot_region_decision_packet.py`: present; local supporting artifact present; evidence quality still requires human/source review

Missing evidence:
- create an explicit pilot acceptance record after privacy and case-scope review
- resolve pilot-region decision blockers before pilot acceptance
- pilot-region decision: data/manifests/graph_scale_acceptance.json is absent
- pilot-region decision: data/manifests/provenance_acceptance.json is absent
- pilot-region decision: data/manifests/pilot_acceptance.json is absent
- review pilot-region decision human-decision items before pilot acceptance
- data/manifests/pilot_acceptance.json is absent

Residual risks:
- Record an explicit pilot acceptance decision with reviewer, scope, privacy review, evidence paths, and not-operational claim boundary.
- create an explicit pilot acceptance record after privacy and case-scope review
- resolve pilot-region decision blockers before pilot acceptance
- pilot-region decision: data/manifests/graph_scale_acceptance.json is absent
- pilot-region decision: data/manifests/provenance_acceptance.json is absent
- pilot-region decision: data/manifests/pilot_acceptance.json is absent
- review pilot-region decision human-decision items before pilot acceptance
- data/manifests/pilot_acceptance.json is absent
- Draft recommendation could be overread as formal approval if copied into a final acceptance path.
- Final-study readiness remains false until formal validators accept source-backed records.

Human reviewer action required:
- Inspect the listed review packets and evidence paths.
- Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Approve, reject, or keep blocked based on the existing review packet evidence.
- Resolve each missing-evidence item listed in this record.
- After a real decision, create or update data/manifests/pilot_acceptance.json.
- Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/manifests/pilot_acceptance.json

### graph_scale_strategy

- Label: Graph-Scale Acceptance
- Related plan gates: `graph_scale_strategy`
- Recommendation: `blocked_requires_human_decision`
- Reason: Repository review packets exist, but a source-backed human decision is still required before any formal artifact can be created.
- Formal target after human decision: `data/manifests/graph_scale_acceptance.json`
- Formal approval: `false`
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
- `data/manifests/graph_scale_acceptance.json`: absent; formal artifact absent; expected until source-backed human approval exists
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
- create an explicit graph-scale acceptance record after source-vs-analysis graph review
- resolve graph-scale strategy-readiness blockers before graph-scale acceptance
- graph-scale strategy readiness: graph_scale_acceptance.json is absent
- graph-scale strategy readiness: current reduced-corridor output has alternate-route warnings
- graph-scale strategy readiness: full bus-practical graph has smoke/runtime evidence only, not full scenario-policy-seed output
- graph-scale strategy readiness: accepted graph choice still requires downstream regeneration decisions for sensitivity, figures, tables, and manuscript interpretation
- review graph-scale strategy-readiness human-decision items before graph-scale acceptance
- resolve graph-scale method-decision blockers before graph-scale acceptance
- graph-scale method decision: full bus-practical graph has smoke/runtime evidence only, not full scenario-policy-seed output
- graph-scale method decision: accepted graph choice still requires downstream regeneration decisions for sensitivity, figures, tables, and manuscript interpretation
- graph-scale method decision: data/manifests/graph_scale_acceptance.json is absent
- review graph-scale method-decision human-decision items before graph-scale acceptance
- data/manifests/graph_scale_acceptance.json is absent

Residual risks:
- Choose and document reduced-corridor, multi-corridor, or full-graph strategy.
- Create graph_scale_acceptance.json with matching graph counts and evidence paths.
- create an explicit graph-scale acceptance record after source-vs-analysis graph review
- resolve graph-scale strategy-readiness blockers before graph-scale acceptance
- graph-scale strategy readiness: graph_scale_acceptance.json is absent
- graph-scale strategy readiness: current reduced-corridor output has alternate-route warnings
- graph-scale strategy readiness: full bus-practical graph has smoke/runtime evidence only, not full scenario-policy-seed output
- graph-scale strategy readiness: accepted graph choice still requires downstream regeneration decisions for sensitivity, figures, tables, and manuscript interpretation
- review graph-scale strategy-readiness human-decision items before graph-scale acceptance
- resolve graph-scale method-decision blockers before graph-scale acceptance
- graph-scale method decision: full bus-practical graph has smoke/runtime evidence only, not full scenario-policy-seed output
- graph-scale method decision: accepted graph choice still requires downstream regeneration decisions for sensitivity, figures, tables, and manuscript interpretation
- graph-scale method decision: data/manifests/graph_scale_acceptance.json is absent
- review graph-scale method-decision human-decision items before graph-scale acceptance
- data/manifests/graph_scale_acceptance.json is absent
- Draft recommendation could be overread as formal approval if copied into a final acceptance path.
- Final-study readiness remains false until formal validators accept source-backed records.

Human reviewer action required:
- Inspect the listed review packets and evidence paths.
- Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Approve, reject, or keep blocked based on the existing review packet evidence.
- Resolve each missing-evidence item listed in this record.
- After a real decision, create or update data/manifests/graph_scale_acceptance.json.
- Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/manifests/graph_scale_acceptance.json

### data_provenance

- Label: Source/License/Provenance Acceptance
- Related plan gates: `data_provenance`
- Recommendation: `blocked_requires_human_decision`
- Reason: Repository review packets exist, but a source-backed human decision is still required before any formal artifact can be created.
- Formal target after human decision: `data/manifests/provenance_acceptance.json`
- Formal approval: `false`
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
- `data/manifests/provenance_acceptance.json`: absent; formal artifact absent; expected until source-backed human approval exists
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
- create an explicit provenance acceptance record after source, license, snapshot, privacy, and reproducibility review
- replace scaffold-only reproducibility manifest with accepted source/license/snapshot provenance
- source provenance priority: formal provenance acceptance record is absent
- source provenance priority: context-source target artifacts still need reviewed payloads, sensitivity/context-only retention decisions, or exclusion decisions
- source provenance priority: cached public snapshots still require license, attribution, snapshot, and reproducibility review
- source provenance priority: repository inputs still require human scope/privacy/reproducibility review
- source provenance priority: URL remediation rows still require reviewer confirmation
- source context cache request: context-source target cache artifacts still lack reviewed source payloads, sensitivity/context-only retention decisions, or explicit exclusion decisions
- source context cache request: license, attribution, snapshot, and reproducibility review are still required for retained public sources
- source context cache request: formal provenance acceptance record is absent
- source context cache decision: formal provenance acceptance record is absent
- source context cache decision: target cache/retention/exclusion decisions are pending for context-source rows
- source context cache decision: retained context sources still require license, attribution, snapshot, and reproducibility review
- source context cache decision: ktdb_public_transport_gtfs_context: no reviewed cache artifact, sensitivity/context-only retention decision, or explicit exclusion decision is present
- source context cache decision: seoul_shortest_path_api_context: no reviewed cache artifact, sensitivity/context-only retention decision, or explicit exclusion decision is present
- source context cache decision: seoul_timetable_api_context: no reviewed cache artifact, sensitivity/context-only retention decision, or explicit exclusion decision is present
- resolve source-provenance decision blockers before provenance acceptance
- source provenance decision: context-source target cache artifacts still lack reviewed source payloads, sensitivity/context-only retention decisions, or explicit exclusion decisions
- source provenance decision: reproducibility manifest remains scaffold-only
- source provenance decision: data/manifests/provenance_acceptance.json is absent
- review source-provenance decision human-decision items before provenance acceptance
- data/manifests/provenance_acceptance.json is absent

Residual risks:
- Review source URLs, licenses, attribution, local snapshots, privacy abstraction, and reproducibility scope.
- Create data/manifests/provenance_acceptance.json only after source-backed review.
- create an explicit provenance acceptance record after source, license, snapshot, privacy, and reproducibility review
- replace scaffold-only reproducibility manifest with accepted source/license/snapshot provenance
- source provenance priority: formal provenance acceptance record is absent
- source provenance priority: context-source target artifacts still need reviewed payloads, sensitivity/context-only retention decisions, or exclusion decisions
- source provenance priority: cached public snapshots still require license, attribution, snapshot, and reproducibility review
- source provenance priority: repository inputs still require human scope/privacy/reproducibility review
- source provenance priority: URL remediation rows still require reviewer confirmation
- source context cache request: context-source target cache artifacts still lack reviewed source payloads, sensitivity/context-only retention decisions, or explicit exclusion decisions
- source context cache request: license, attribution, snapshot, and reproducibility review are still required for retained public sources
- source context cache request: formal provenance acceptance record is absent
- source context cache decision: formal provenance acceptance record is absent
- source context cache decision: target cache/retention/exclusion decisions are pending for context-source rows
- source context cache decision: retained context sources still require license, attribution, snapshot, and reproducibility review
- source context cache decision: ktdb_public_transport_gtfs_context: no reviewed cache artifact, sensitivity/context-only retention decision, or explicit exclusion decision is present
- source context cache decision: seoul_shortest_path_api_context: no reviewed cache artifact, sensitivity/context-only retention decision, or explicit exclusion decision is present
- source context cache decision: seoul_timetable_api_context: no reviewed cache artifact, sensitivity/context-only retention decision, or explicit exclusion decision is present
- resolve source-provenance decision blockers before provenance acceptance
- source provenance decision: context-source target cache artifacts still lack reviewed source payloads, sensitivity/context-only retention decisions, or explicit exclusion decisions
- source provenance decision: reproducibility manifest remains scaffold-only
- source provenance decision: data/manifests/provenance_acceptance.json is absent
- review source-provenance decision human-decision items before provenance acceptance
- data/manifests/provenance_acceptance.json is absent
- Draft recommendation could be overread as formal approval if copied into a final acceptance path.
- Final-study readiness remains false until formal validators accept source-backed records.

Human reviewer action required:
- Inspect the listed review packets and evidence paths.
- Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Approve, reject, or keep blocked based on the existing review packet evidence.
- Resolve each missing-evidence item listed in this record.
- After a real decision, create or update data/manifests/provenance_acceptance.json.
- Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/manifests/provenance_acceptance.json

### parameter_acceptance

- Label: Weak-Parameter Acceptance
- Related plan gates: `parameter_evidence`, `rail_evidence`
- Recommendation: `blocked_missing_evidence`
- Reason: The gate still lacks source-backed, accepted, or upstream-complete evidence required by the current final-study audit.
- Formal target after human decision: `data/parameters/parameter_acceptance.csv`
- Formal approval: `false`
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
- `data/parameters/parameter_acceptance.csv`: absent; formal artifact absent; expected until source-backed human approval exists
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
- `docs/rail_gtfs_cache_schema.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/fetch_rail_shortest_path_cache.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/derive_rail_shortest_path_evidence.py`: present; local supporting artifact present; evidence quality still requires human/source review

Missing evidence:
- create reviewed parameter acceptance records only for weak assumptions retained in final claims
- parameter_acceptance.csv is missing
- justify demand scale, arrival process, time horizon, and censoring penalties with planning assumptions or sensitivity-bound evidence
- replace scenario-only disruption probabilities and degradation rules with public hazard, incident, literature, or expert-reviewed evidence
- replace generic fleet and vehicle-capacity assumptions with agency, planning, literature, or accepted scenario evidence
- derive rail headway and travel time from cached GTFS, timetable, operator, or agency records, and keep rail capacity source-backed or explicitly sensitivity-only
- strengthen road speed, capacity, and background traffic values with public speed limits, traffic counts, or benchmark-calibrated routing
- support transfer delays with station-layout evidence, observed ranges, or literature rather than generic fixed delays
- parameter source readiness: all rows require human review or external source decisions before final claims
- parameter source readiness: this packet is readiness evidence only and cannot create accepted parameter values
- parameter source readiness: parameter_acceptance.csv remains separate and absent unless reviewers accept weak assumptions
- parameter evidence priority: transfer-delay evidence still requires human review and source-backed or accepted-assumption treatment
- parameter evidence priority: rail timing/source-decision evidence is incomplete
- parameter evidence priority: high-priority disruption and traffic/BPR rows still require human/source-backed decisions
- parameter evidence priority: medium-priority demand, fleet, dispatch, and transfer rows remain scenario assumptions
- parameter evidence priority: parameter_acceptance.csv remains absent unless reviewers accept retained weak assumptions
- parameter source decision: formal parameter acceptance table is absent
- parameter source decision: parameter source decisions are pending for weak parameter groups
- parameter source decision: retained weak assumptions require source-backed updates, sensitivity-only limits, or explicit weak-parameter acceptance
- parameter source decision: rail_service_parameter_source_request: rail timing cache, reviewed GTFS, or source-decision evidence remains incomplete
- rail service evidence: cache timetable, shortest-path, or GTFS-derived records
- rail service evidence: derive headway and travel time from the cached records
- rail fetch readiness: rail timing cache files are absent unless source_cache_present is true
- rail fetch readiness: API-key and reviewed-GTFS rows require external reviewer-provided inputs
- rail fetch readiness: this packet is readiness evidence only and cannot create rail_service_evidence.csv
- rail evidence priority: rail timing cache files are absent
- rail evidence priority: DATA_GO_KR_KEY or reviewed GTFS input is absent
- rail evidence priority: capacity and availability treatment still require human/source-backed decisions
- rail source decision: rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests
- rail source decision: rail timing cache or reviewed GTFS source files are absent for timing requests
- rail source decision: retained rail capacity and availability assumptions require source-backed updates, sensitivity-only limits, scenario-only limits, or explicit acceptance
- rail source decision: rail_shortest_path_travel_time_request: DATA_GO_KR_KEY is absent and no cached payload is present
- rail source decision: rail_static_gtfs_timing_request: reviewed GTFS file is absent
- rail source decision: rail_timetable_headway_request: DATA_GO_KR_KEY is absent and no cached payload is present
- data/parameters/parameter_acceptance.csv is absent

Residual risks:
- Replace weak road, rail, and parameter assumptions with source-backed evidence or explicit accepted overrides.
- Create road_class_overrides.csv and parameter_acceptance.csv only after review.
- create reviewed parameter acceptance records only for weak assumptions retained in final claims
- parameter_acceptance.csv is missing
- justify demand scale, arrival process, time horizon, and censoring penalties with planning assumptions or sensitivity-bound evidence
- replace scenario-only disruption probabilities and degradation rules with public hazard, incident, literature, or expert-reviewed evidence
- replace generic fleet and vehicle-capacity assumptions with agency, planning, literature, or accepted scenario evidence
- derive rail headway and travel time from cached GTFS, timetable, operator, or agency records, and keep rail capacity source-backed or explicitly sensitivity-only
- strengthen road speed, capacity, and background traffic values with public speed limits, traffic counts, or benchmark-calibrated routing
- support transfer delays with station-layout evidence, observed ranges, or literature rather than generic fixed delays
- parameter source readiness: all rows require human review or external source decisions before final claims
- parameter source readiness: this packet is readiness evidence only and cannot create accepted parameter values
- parameter source readiness: parameter_acceptance.csv remains separate and absent unless reviewers accept weak assumptions
- parameter evidence priority: transfer-delay evidence still requires human review and source-backed or accepted-assumption treatment
- parameter evidence priority: rail timing/source-decision evidence is incomplete
- parameter evidence priority: high-priority disruption and traffic/BPR rows still require human/source-backed decisions
- parameter evidence priority: medium-priority demand, fleet, dispatch, and transfer rows remain scenario assumptions
- parameter evidence priority: parameter_acceptance.csv remains absent unless reviewers accept retained weak assumptions
- parameter source decision: formal parameter acceptance table is absent
- parameter source decision: parameter source decisions are pending for weak parameter groups
- parameter source decision: retained weak assumptions require source-backed updates, sensitivity-only limits, or explicit weak-parameter acceptance
- parameter source decision: rail_service_parameter_source_request: rail timing cache, reviewed GTFS, or source-decision evidence remains incomplete
- rail service evidence: cache timetable, shortest-path, or GTFS-derived records
- rail service evidence: derive headway and travel time from the cached records
- rail fetch readiness: rail timing cache files are absent unless source_cache_present is true
- rail fetch readiness: API-key and reviewed-GTFS rows require external reviewer-provided inputs
- rail fetch readiness: this packet is readiness evidence only and cannot create rail_service_evidence.csv
- rail evidence priority: rail timing cache files are absent
- rail evidence priority: DATA_GO_KR_KEY or reviewed GTFS input is absent
- rail evidence priority: capacity and availability treatment still require human/source-backed decisions
- rail source decision: rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests
- rail source decision: rail timing cache or reviewed GTFS source files are absent for timing requests
- rail source decision: retained rail capacity and availability assumptions require source-backed updates, sensitivity-only limits, scenario-only limits, or explicit acceptance
- rail source decision: rail_shortest_path_travel_time_request: DATA_GO_KR_KEY is absent and no cached payload is present
- rail source decision: rail_static_gtfs_timing_request: reviewed GTFS file is absent
- rail source decision: rail_timetable_headway_request: DATA_GO_KR_KEY is absent and no cached payload is present
- data/parameters/parameter_acceptance.csv is absent
- Draft recommendation could be overread as formal approval if copied into a final acceptance path.
- Final-study readiness remains false until formal validators accept source-backed records.

Human reviewer action required:
- Inspect the listed review packets and evidence paths.
- Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Supply or regenerate the missing evidence items before deciding.
- Resolve each missing-evidence item listed in this record.
- After a real decision, create or update data/parameters/parameter_acceptance.csv.
- Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/parameters/parameter_acceptance.csv

### road_class_overrides

- Label: Road-Class Override Acceptance
- Related plan gates: `cached_osm_input`
- Recommendation: `blocked_missing_evidence`
- Reason: The gate still lacks source-backed, accepted, or upstream-complete evidence required by the current final-study audit.
- Formal target after human decision: `data/parameters/road_class_overrides.csv`
- Formal approval: `false`
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
- `data/parameters/road_class_overrides.csv`: absent; formal artifact absent; expected until source-backed human approval exists
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
- `scripts/write_road_class_override_template.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/audit_road_overrides.py`: present; local supporting artifact present; evidence quality still requires human/source review

Missing evidence:
- replace the draft road-class override worksheet with a reviewed road_class_overrides.csv table containing source-backed speed, capacity, and base-disruption evidence
- apply the reviewed overrides when adapting the pilot graph if final claims require calibrated road inputs
- reviewed road-class override table is absent
- road input evidence: review OSM maxspeed coverage and replace fallback free-flow speeds where final claims require calibration
- road input evidence: replace road-class capacity proxies with traffic counts, agency capacity references, or benchmark-calibrated values
- road input evidence: replace road-class base disruption probabilities with hazard, incident, or accepted scenario evidence
- road input evidence: treat this as road-input evidence only; route plausibility and traffic validation remain separate gates
- road override evidence: replace the draft road-class override worksheet with a reviewed road_class_overrides.csv table containing source-backed speed, capacity, and base-disruption evidence
- road override evidence: apply the reviewed overrides when adapting the pilot graph if final claims require calibrated road inputs
- road override application: reviewed road-class override table is absent
- road source readiness: reviewed road_class_overrides.csv is absent unless target_output_present is true
- road source readiness: capacity and disruption evidence still require external source or formal assumption decisions
- road source readiness: this packet is readiness evidence only and cannot create road-class overrides
- road source decision: reviewed road_class_overrides.csv is absent
- road source decision: road source decisions are pending for speed, capacity, disruption, benchmark, and override-application requests
- road source decision: retained road assumptions require source-backed updates, sensitivity-only limits, benchmark-only limits, or explicit acceptance
- road source decision: reviewed_road_class_override_application_request: data/parameters/road_class_overrides.csv is absent
- road source decision: road_capacity_lane_count_source_request: cached lane-count evidence has no parseable observed lane rows
- data/parameters/road_class_overrides.csv is absent

Residual risks:
- Replace weak road, rail, and parameter assumptions with source-backed evidence or explicit accepted overrides.
- Create road_class_overrides.csv and parameter_acceptance.csv only after review.
- replace the draft road-class override worksheet with a reviewed road_class_overrides.csv table containing source-backed speed, capacity, and base-disruption evidence
- apply the reviewed overrides when adapting the pilot graph if final claims require calibrated road inputs
- reviewed road-class override table is absent
- road input evidence: review OSM maxspeed coverage and replace fallback free-flow speeds where final claims require calibration
- road input evidence: replace road-class capacity proxies with traffic counts, agency capacity references, or benchmark-calibrated values
- road input evidence: replace road-class base disruption probabilities with hazard, incident, or accepted scenario evidence
- road input evidence: treat this as road-input evidence only; route plausibility and traffic validation remain separate gates
- road override evidence: replace the draft road-class override worksheet with a reviewed road_class_overrides.csv table containing source-backed speed, capacity, and base-disruption evidence
- road override evidence: apply the reviewed overrides when adapting the pilot graph if final claims require calibrated road inputs
- road override application: reviewed road-class override table is absent
- road source readiness: reviewed road_class_overrides.csv is absent unless target_output_present is true
- road source readiness: capacity and disruption evidence still require external source or formal assumption decisions
- road source readiness: this packet is readiness evidence only and cannot create road-class overrides
- road source decision: reviewed road_class_overrides.csv is absent
- road source decision: road source decisions are pending for speed, capacity, disruption, benchmark, and override-application requests
- road source decision: retained road assumptions require source-backed updates, sensitivity-only limits, benchmark-only limits, or explicit acceptance
- road source decision: reviewed_road_class_override_application_request: data/parameters/road_class_overrides.csv is absent
- road source decision: road_capacity_lane_count_source_request: cached lane-count evidence has no parseable observed lane rows
- data/parameters/road_class_overrides.csv is absent
- Draft recommendation could be overread as formal approval if copied into a final acceptance path.
- Final-study readiness remains false until formal validators accept source-backed records.

Human reviewer action required:
- Inspect the listed review packets and evidence paths.
- Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Supply or regenerate the missing evidence items before deciding.
- Resolve each missing-evidence item listed in this record.
- After a real decision, create or update data/parameters/road_class_overrides.csv.
- Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/parameters/road_class_overrides.csv
- results/realworld_pilot/pilot_full_manifest.json
- results/realworld_pilot/pilot_full_results.csv
- data/manifests/experiment_acceptance.json

### validation_package

- Label: Validation Acceptance
- Related plan gates: `validation_package`
- Recommendation: `blocked_requires_human_decision`
- Reason: Repository review packets exist, but a source-backed human decision is still required before any formal artifact can be created.
- Formal target after human decision: `data/manifests/validation_acceptance.json`
- Formal approval: `false`
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
- `data/manifests/validation_acceptance.json`: absent; formal artifact absent; expected until source-backed human approval exists
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
- create an explicit validation acceptance record after benchmark-strategy review
- resolve validation strategy-readiness blockers before validation acceptance
- validation strategy readiness: validation_acceptance.json is absent
- validation strategy readiness: route-level road evidence exposure remains weak until road evidence gates close
- review validation strategy-readiness human-decision items before validation acceptance
- resolve validation benchmark-decision blockers before validation acceptance
- validation benchmark decision: validation summary still declares scaffold or sanity scope
- validation benchmark decision: route-level road evidence exposure remains weak until road evidence gates close
- validation benchmark decision: data/manifests/validation_acceptance.json is absent
- review validation benchmark-decision human-decision items before validation acceptance
- revise validation summary from scaffold/sanity evidence to accepted publication-level validation scope after review
- data/manifests/validation_acceptance.json is absent

Residual risks:
- Review validation thresholds, benchmark scope, snapshot pinning, and failure cases.
- Create validation_acceptance.json after benchmark-strategy review.
- create an explicit validation acceptance record after benchmark-strategy review
- resolve validation strategy-readiness blockers before validation acceptance
- validation strategy readiness: validation_acceptance.json is absent
- validation strategy readiness: route-level road evidence exposure remains weak until road evidence gates close
- review validation strategy-readiness human-decision items before validation acceptance
- resolve validation benchmark-decision blockers before validation acceptance
- validation benchmark decision: validation summary still declares scaffold or sanity scope
- validation benchmark decision: route-level road evidence exposure remains weak until road evidence gates close
- validation benchmark decision: data/manifests/validation_acceptance.json is absent
- review validation benchmark-decision human-decision items before validation acceptance
- revise validation summary from scaffold/sanity evidence to accepted publication-level validation scope after review
- data/manifests/validation_acceptance.json is absent
- Draft recommendation could be overread as formal approval if copied into a final acceptance path.
- Final-study readiness remains false until formal validators accept source-backed records.

Human reviewer action required:
- Inspect the listed review packets and evidence paths.
- Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Approve, reject, or keep blocked based on the existing review packet evidence.
- Resolve each missing-evidence item listed in this record.
- After a real decision, create or update data/manifests/validation_acceptance.json.
- Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/manifests/validation_acceptance.json

### sensitivity_analysis

- Label: Sensitivity Acceptance
- Related plan gates: `sensitivity_analysis`
- Recommendation: `blocked_missing_evidence`
- Reason: The gate still lacks source-backed, accepted, or upstream-complete evidence required by the current final-study audit.
- Formal target after human decision: `data/manifests/sensitivity_acceptance.json`
- Formal approval: `false`
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
- `data/manifests/sensitivity_acceptance.json`: absent; formal artifact absent; expected until source-backed human approval exists
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
- create an explicit sensitivity acceptance record after SALib output and Sobol-decision review
- resolve sensitivity strategy-readiness blockers before sensitivity acceptance
- sensitivity strategy readiness: sensitivity outputs use a reduced analysis graph
- sensitivity strategy readiness: current sensitivity result scope is scaffold or not calibrated
- sensitivity strategy readiness: Morris-vs-Sobol method decision is not recorded in formal acceptance
- sensitivity strategy readiness: data/manifests/sensitivity_acceptance.json is absent
- review sensitivity strategy-readiness human-decision items before sensitivity acceptance
- accept sensitivity outputs on final graph/evidence scope; current Morris outputs are scaffold-level
- data/manifests/sensitivity_acceptance.json is absent

Residual risks:
- Review parameter ranges and decide whether Morris is enough or Sobol is required.
- Create sensitivity_acceptance.json after final input and graph scope are accepted.
- create an explicit sensitivity acceptance record after SALib output and Sobol-decision review
- resolve sensitivity strategy-readiness blockers before sensitivity acceptance
- sensitivity strategy readiness: sensitivity outputs use a reduced analysis graph
- sensitivity strategy readiness: current sensitivity result scope is scaffold or not calibrated
- sensitivity strategy readiness: Morris-vs-Sobol method decision is not recorded in formal acceptance
- sensitivity strategy readiness: data/manifests/sensitivity_acceptance.json is absent
- review sensitivity strategy-readiness human-decision items before sensitivity acceptance
- accept sensitivity outputs on final graph/evidence scope; current Morris outputs are scaffold-level
- data/manifests/sensitivity_acceptance.json is absent
- Draft recommendation could be overread as formal approval if copied into a final acceptance path.
- Final-study readiness remains false until formal validators accept source-backed records.

Human reviewer action required:
- Inspect the listed review packets and evidence paths.
- Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Supply or regenerate the missing evidence items before deciding.
- Resolve each missing-evidence item listed in this record.
- After a real decision, create or update data/manifests/sensitivity_acceptance.json.
- Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/manifests/sensitivity_acceptance.json

### full_experiment_output

- Label: Experiment Acceptance
- Related plan gates: `full_experiment_output`
- Recommendation: `blocked_missing_evidence`
- Reason: The gate still lacks source-backed, accepted, or upstream-complete evidence required by the current final-study audit.
- Formal target after human decision: `data/manifests/experiment_acceptance.json`
- Formal approval: `false`
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
- `data/manifests/experiment_acceptance.json`: absent; formal artifact absent; expected until source-backed human approval exists
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
- create an explicit experiment acceptance record after input validation, graph-scope, and scenario-policy-seed review
- resolve experiment strategy-readiness blockers before experiment acceptance
- experiment strategy readiness: current full-pilot result scope is scaffold or not calibrated
- experiment strategy readiness: full-pilot outputs depend on a graph method that is not accepted
- experiment strategy readiness: upstream input, road override, parameter, validation, or provenance gates are not accepted
- experiment strategy readiness: data/manifests/experiment_acceptance.json is absent
- review experiment strategy-readiness human-decision items before experiment acceptance
- resolve experiment design-decision blockers before experiment acceptance
- experiment design decision: experiment outputs depend on a graph method that is not accepted
- experiment design decision: upstream input, road override, parameter, validation, or provenance gates are not accepted
- experiment design decision: current full-pilot result scope is scaffold or not calibrated
- experiment design decision: data/manifests/experiment_acceptance.json is absent
- review experiment design-decision human-decision items before experiment acceptance
- accept or regenerate full pilot outputs after input validation and graph-scale decision
- review experiment-package rows before formal experiment acceptance
- data/manifests/experiment_acceptance.json is absent

Residual risks:
- Regenerate or accept full outputs after input, graph-scale, and validation gates close.
- Create experiment_acceptance.json with matching run profile and row counts.
- create an explicit experiment acceptance record after input validation, graph-scope, and scenario-policy-seed review
- resolve experiment strategy-readiness blockers before experiment acceptance
- experiment strategy readiness: current full-pilot result scope is scaffold or not calibrated
- experiment strategy readiness: full-pilot outputs depend on a graph method that is not accepted
- experiment strategy readiness: upstream input, road override, parameter, validation, or provenance gates are not accepted
- experiment strategy readiness: data/manifests/experiment_acceptance.json is absent
- review experiment strategy-readiness human-decision items before experiment acceptance
- resolve experiment design-decision blockers before experiment acceptance
- experiment design decision: experiment outputs depend on a graph method that is not accepted
- experiment design decision: upstream input, road override, parameter, validation, or provenance gates are not accepted
- experiment design decision: current full-pilot result scope is scaffold or not calibrated
- experiment design decision: data/manifests/experiment_acceptance.json is absent
- review experiment design-decision human-decision items before experiment acceptance
- accept or regenerate full pilot outputs after input validation and graph-scale decision
- review experiment-package rows before formal experiment acceptance
- data/manifests/experiment_acceptance.json is absent
- Draft recommendation could be overread as formal approval if copied into a final acceptance path.
- Final-study readiness remains false until formal validators accept source-backed records.

Human reviewer action required:
- Inspect the listed review packets and evidence paths.
- Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Supply or regenerate the missing evidence items before deciding.
- Resolve each missing-evidence item listed in this record.
- After a real decision, create or update data/manifests/experiment_acceptance.json.
- Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/manifests/experiment_acceptance.json

### manuscript_report_alignment

- Label: Manuscript/Report Acceptance
- Related plan gates: `manuscript_report_alignment`
- Recommendation: `blocked_missing_evidence`
- Reason: The gate still lacks source-backed, accepted, or upstream-complete evidence required by the current final-study audit.
- Formal target after human decision: `data/manifests/manuscript_acceptance.json`
- Formal approval: `false`
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
- `data/manifests/manuscript_acceptance.json`: absent; formal artifact absent; expected until source-backed human approval exists
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
- create an explicit manuscript/report acceptance record after evidence gates, figures, paper, report, and claim boundaries are reviewed
- close evidence gates before final paper/report claims
- revise figure/table claim boundary from scaffold to accepted study scope
- resolve figure/table review blockers before manuscript acceptance
- figure/table review: figure/table outputs depend on reduced analysis graph scope
- figure/table review: figure/table source outputs remain scaffold or not calibrated
- figure/table review: data/manifests/manuscript_acceptance.json is absent
- review figure/table human-review rows before manuscript acceptance
- review or revise claim-alignment overclaim candidates before manuscript acceptance
- claim alignment: formal manuscript/report acceptance record is absent
- claim alignment: claim-alignment rows are review aids and do not approve manuscript claims
- claim alignment: evidence gates remain blocked, so result claims cannot be accepted as final-study claims
- resolve manuscript/report decision blockers before manuscript acceptance
- manuscript/report decision: figure/table outputs depend on reduced analysis graph scope; figure/table source outputs remain scaffold or not calibrated; data/manifests/manuscript_acceptance.json is absent
- manuscript/report decision: claim-alignment packet has 108 rows requiring revision or acceptance
- manuscript/report decision: upstream evidence gates blocked: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output
- manuscript/report decision: data/manifests/manuscript_acceptance.json is absent
- review manuscript/report human-decision rows before manuscript acceptance
- data/manifests/manuscript_acceptance.json is absent

Residual risks:
- Revise or hold claims until all supporting evidence gates are accepted.
- Create manuscript_acceptance.json after claim-by-claim review.
- create an explicit manuscript/report acceptance record after evidence gates, figures, paper, report, and claim boundaries are reviewed
- close evidence gates before final paper/report claims
- revise figure/table claim boundary from scaffold to accepted study scope
- resolve figure/table review blockers before manuscript acceptance
- figure/table review: figure/table outputs depend on reduced analysis graph scope
- figure/table review: figure/table source outputs remain scaffold or not calibrated
- figure/table review: data/manifests/manuscript_acceptance.json is absent
- review figure/table human-review rows before manuscript acceptance
- review or revise claim-alignment overclaim candidates before manuscript acceptance
- claim alignment: formal manuscript/report acceptance record is absent
- claim alignment: claim-alignment rows are review aids and do not approve manuscript claims
- claim alignment: evidence gates remain blocked, so result claims cannot be accepted as final-study claims
- resolve manuscript/report decision blockers before manuscript acceptance
- manuscript/report decision: figure/table outputs depend on reduced analysis graph scope; figure/table source outputs remain scaffold or not calibrated; data/manifests/manuscript_acceptance.json is absent
- manuscript/report decision: claim-alignment packet has 108 rows requiring revision or acceptance
- manuscript/report decision: upstream evidence gates blocked: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output
- manuscript/report decision: data/manifests/manuscript_acceptance.json is absent
- review manuscript/report human-decision rows before manuscript acceptance
- data/manifests/manuscript_acceptance.json is absent
- Draft recommendation could be overread as formal approval if copied into a final acceptance path.
- Final-study readiness remains false until formal validators accept source-backed records.

Human reviewer action required:
- Inspect the listed review packets and evidence paths.
- Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Supply or regenerate the missing evidence items before deciding.
- Resolve each missing-evidence item listed in this record.
- After a real decision, create or update data/manifests/manuscript_acceptance.json.
- Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/manifests/manuscript_acceptance.json

### reproducibility

- Label: Reproducibility Acceptance
- Related plan gates: `reproducibility`
- Recommendation: `blocked_missing_evidence`
- Reason: The gate still lacks source-backed, accepted, or upstream-complete evidence required by the current final-study audit.
- Formal target after human decision: `data/manifests/reproducibility_acceptance.json`
- Formal approval: `false`
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
- `data/manifests/reproducibility_acceptance.json`: absent; formal artifact absent; expected until source-backed human approval exists
- `docs/review_packets/reproducibility.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/reproducibility_review_packet.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/validation/tracked_artifact_audit.csv`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/audit_plan_artifacts.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/reproducibility_smoke.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/clean_checkout_reproducibility_smoke.md`: present; local supporting artifact present; evidence quality still requires human/source review

Missing evidence:
- create an explicit reproducibility acceptance record after clean-checkout validation, artifact regeneration, manifest review, and import-boundary checks
- replace scaffold-only manifest with clean-checkout final reproduction package
- resolve reproducibility decision blockers before reproducibility acceptance
- reproducibility decision: reproducibility manifest remains scaffold-only
- reproducibility decision: data/manifests/reproducibility_acceptance.json is absent
- review reproducibility human-decision rows before reproducibility acceptance
- data/manifests/reproducibility_acceptance.json is absent

Residual risks:
- Run or document clean-checkout validation with command log and artifact regeneration evidence.
- Create reproducibility_acceptance.json only after accepted reproduction scope is complete.
- create an explicit reproducibility acceptance record after clean-checkout validation, artifact regeneration, manifest review, and import-boundary checks
- replace scaffold-only manifest with clean-checkout final reproduction package
- resolve reproducibility decision blockers before reproducibility acceptance
- reproducibility decision: reproducibility manifest remains scaffold-only
- reproducibility decision: data/manifests/reproducibility_acceptance.json is absent
- review reproducibility human-decision rows before reproducibility acceptance
- data/manifests/reproducibility_acceptance.json is absent
- Draft recommendation could be overread as formal approval if copied into a final acceptance path.
- Final-study readiness remains false until formal validators accept source-backed records.

Human reviewer action required:
- Inspect the listed review packets and evidence paths.
- Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Supply or regenerate the missing evidence items before deciding.
- Resolve each missing-evidence item listed in this record.
- After a real decision, create or update data/manifests/reproducibility_acceptance.json.
- Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/manifests/reproducibility_acceptance.json

### final_audit_document

- Label: Final Study Audit Document
- Related plan gates: `final_audit`
- Recommendation: `blocked_missing_evidence`
- Reason: The gate still lacks source-backed, accepted, or upstream-complete evidence required by the current final-study audit.
- Formal target after human decision: `docs/final_study_audit.md`
- Formal approval: `false`
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
- `docs/final_study_audit.md`: absent; formal artifact absent; expected until source-backed human approval exists
- `docs/review_packets/final_audit.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/formal_acceptance_evidence_matrix_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/final_audit_decision_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/audit_final_study_readiness.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/final_audit_acceptance.json`: absent; local supporting artifact absent

Missing evidence:
- create docs/final_study_audit.md after all other gates close
- create an explicit final-audit acceptance record only after prompt-to-artifact review confirms every final gate is closed
- resolve final-audit decision blockers before final-audit acceptance
- final-audit decision: pre-final gates remain blocked: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output, manuscript_report_alignment, reproducibility
- final-audit decision: required formal acceptance artifacts are absent: data/manifests/pilot_acceptance.json, data/manifests/graph_scale_acceptance.json, data/manifests/provenance_acceptance.json, data/parameters/parameter_acceptance.csv, data/parameters/road_class_overrides.csv, data/manifests/validation_acceptance.json, data/manifests/sensitivity_acceptance.json, data/manifests/experiment_acceptance.json, data/manifests/manuscript_acceptance.json, data/manifests/reproducibility_acceptance.json, docs/final_study_audit.md, data/manifests/final_audit_acceptance.json
- final-audit decision: docs/final_study_audit.md is absent
- final-audit decision: data/manifests/final_audit_acceptance.json is absent
- review final-audit human-decision rows before final-audit acceptance
- all pre-final gates must be ready before final audit acceptance: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output, manuscript_report_alignment, reproducibility
- docs/final_study_audit.md is absent

Residual risks:
- After all pre-final gates are ready, write the independent prompt-to-artifact final audit.
- Create final_audit_acceptance.json only when gate lists and readiness counts match current evidence.
- create docs/final_study_audit.md after all other gates close
- create an explicit final-audit acceptance record only after prompt-to-artifact review confirms every final gate is closed
- resolve final-audit decision blockers before final-audit acceptance
- final-audit decision: pre-final gates remain blocked: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output, manuscript_report_alignment, reproducibility
- final-audit decision: required formal acceptance artifacts are absent: data/manifests/pilot_acceptance.json, data/manifests/graph_scale_acceptance.json, data/manifests/provenance_acceptance.json, data/parameters/parameter_acceptance.csv, data/parameters/road_class_overrides.csv, data/manifests/validation_acceptance.json, data/manifests/sensitivity_acceptance.json, data/manifests/experiment_acceptance.json, data/manifests/manuscript_acceptance.json, data/manifests/reproducibility_acceptance.json, docs/final_study_audit.md, data/manifests/final_audit_acceptance.json
- final-audit decision: docs/final_study_audit.md is absent
- final-audit decision: data/manifests/final_audit_acceptance.json is absent
- review final-audit human-decision rows before final-audit acceptance
- all pre-final gates must be ready before final audit acceptance: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output, manuscript_report_alignment, reproducibility
- docs/final_study_audit.md is absent
- Draft recommendation could be overread as formal approval if copied into a final acceptance path.
- Final-study readiness remains false until formal validators accept source-backed records.

Human reviewer action required:
- Inspect the listed review packets and evidence paths.
- Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Supply or regenerate the missing evidence items before deciding.
- Wait until every pre-final formal gate is accepted before creating final-audit artifacts.
- Resolve each missing-evidence item listed in this record.
- After a real decision, create or update docs/final_study_audit.md.
- Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- docs/final_study_audit.md
- data/manifests/final_audit_acceptance.json

### final_audit

- Label: Final Audit Acceptance
- Related plan gates: `final_audit`
- Recommendation: `blocked_missing_evidence`
- Reason: The gate still lacks source-backed, accepted, or upstream-complete evidence required by the current final-study audit.
- Formal target after human decision: `data/manifests/final_audit_acceptance.json`
- Formal approval: `false`
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
- `data/manifests/final_audit_acceptance.json`: absent; formal artifact absent; expected until source-backed human approval exists
- `docs/review_packets/final_audit.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `data/manifests/formal_acceptance_evidence_matrix_manifest.json`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/final_audit_decision_packet.md`: present; local supporting artifact present; evidence quality still requires human/source review
- `scripts/audit_final_study_readiness.py`: present; local supporting artifact present; evidence quality still requires human/source review
- `docs/final_study_audit.md`: absent; local supporting artifact absent

Missing evidence:
- create an explicit final-audit acceptance record only after prompt-to-artifact review confirms every final gate is closed
- create docs/final_study_audit.md after all other gates close
- resolve final-audit decision blockers before final-audit acceptance
- final-audit decision: pre-final gates remain blocked: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output, manuscript_report_alignment, reproducibility
- final-audit decision: required formal acceptance artifacts are absent: data/manifests/pilot_acceptance.json, data/manifests/graph_scale_acceptance.json, data/manifests/provenance_acceptance.json, data/parameters/parameter_acceptance.csv, data/parameters/road_class_overrides.csv, data/manifests/validation_acceptance.json, data/manifests/sensitivity_acceptance.json, data/manifests/experiment_acceptance.json, data/manifests/manuscript_acceptance.json, data/manifests/reproducibility_acceptance.json, docs/final_study_audit.md, data/manifests/final_audit_acceptance.json
- final-audit decision: docs/final_study_audit.md is absent
- final-audit decision: data/manifests/final_audit_acceptance.json is absent
- review final-audit human-decision rows before final-audit acceptance
- all pre-final gates must be ready before final audit acceptance: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output, manuscript_report_alignment, reproducibility
- data/manifests/final_audit_acceptance.json is absent

Residual risks:
- After all pre-final gates are ready, write the independent prompt-to-artifact final audit.
- Create final_audit_acceptance.json only when gate lists and readiness counts match current evidence.
- create an explicit final-audit acceptance record only after prompt-to-artifact review confirms every final gate is closed
- create docs/final_study_audit.md after all other gates close
- resolve final-audit decision blockers before final-audit acceptance
- final-audit decision: pre-final gates remain blocked: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output, manuscript_report_alignment, reproducibility
- final-audit decision: required formal acceptance artifacts are absent: data/manifests/pilot_acceptance.json, data/manifests/graph_scale_acceptance.json, data/manifests/provenance_acceptance.json, data/parameters/parameter_acceptance.csv, data/parameters/road_class_overrides.csv, data/manifests/validation_acceptance.json, data/manifests/sensitivity_acceptance.json, data/manifests/experiment_acceptance.json, data/manifests/manuscript_acceptance.json, data/manifests/reproducibility_acceptance.json, docs/final_study_audit.md, data/manifests/final_audit_acceptance.json
- final-audit decision: docs/final_study_audit.md is absent
- final-audit decision: data/manifests/final_audit_acceptance.json is absent
- review final-audit human-decision rows before final-audit acceptance
- all pre-final gates must be ready before final audit acceptance: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output, manuscript_report_alignment, reproducibility
- data/manifests/final_audit_acceptance.json is absent
- Draft recommendation could be overread as formal approval if copied into a final acceptance path.
- Final-study readiness remains false until formal validators accept source-backed records.

Human reviewer action required:
- Inspect the listed review packets and evidence paths.
- Record an explicit source-backed reviewer decision; do not use this draft record as approval.
- Supply or regenerate the missing evidence items before deciding.
- Wait until every pre-final formal gate is accepted before creating final-audit artifacts.
- Resolve each missing-evidence item listed in this record.
- After a real decision, create or update data/manifests/final_audit_acceptance.json.
- Rerun scripts/validate_formal_acceptance_package.py.

Files to create or update after human decision:
- data/manifests/final_audit_acceptance.json
- docs/final_study_audit.md

## Use

Use these draft records to decide whether a human reviewer should approve, reject, or keep each gate blocked. Do not move any draft JSON into a formal acceptance path unless a reviewer replaces the draft fields with source-backed acceptance evidence and then reruns the formal package validators.
