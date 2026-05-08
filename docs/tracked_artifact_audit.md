# Tracked Artifact Audit

This audit checks whether current changed artifacts would be present in a clean checkout of the current Git HEAD. It does not commit files, approve reproducibility, validate evidence quality, or close final-study gates.

## Summary

- Clean-checkout reproducibility ready: `false`
- Can mark complete: `false`
- Changed reproducibility artifacts: 70
- Blocking changed artifacts: 70
- Untracked artifacts: 6
- Modified or staged artifacts: 64

## Changed Artifacts

| Status | Category | Path | Required Action |
| --- | --- | --- | --- |
| M | agent_definition | `agents/acceptance_review_agents.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/acceptance_decision_template_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/acceptance_orchestration_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/acceptance_task_assignments_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_review_path_audit.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/cached_osm_input__road_rail_parameter_evidence_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/data_provenance__osm_source_license_provenance_review_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/final_audit__final_independent_audit_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/full_experiment_output__full_experiment_package_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/graph_scale_strategy__graph_scale_method_review_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/manuscript_report_alignment__paper_report_claim_alignment_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/parameter_evidence__road_rail_parameter_evidence_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/pilot_region_accepted__pilot_region_privacy_review_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/rail_evidence__road_rail_parameter_evidence_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/reproducibility__clean_checkout_reproducibility_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/sensitivity_analysis__sensitivity_analysis_review_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/validation_package__validation_benchmark_strategy_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/current_goal_completion_audit.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/data_provenance_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/final_audit_document_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/final_audit_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/formal_acceptance_pre_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/full_experiment_output_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/graph_scale_strategy_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/manuscript_report_alignment_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/parameter_acceptance_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/pilot_region_accepted_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/reproducibility_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/road_class_overrides_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/sensitivity_analysis_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/validation_package_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/formal_acceptance_blocker_queue_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/formal_acceptance_evidence_matrix.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/formal_acceptance_evidence_matrix_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/publication_readiness_audit.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/reproducibility_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/reproducibility_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/agent_review_path_audit.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/current_goal_completion_audit.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/formal_acceptance_evidence_matrix.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/formal_acceptance_pre_review.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/acceptance_review_index.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/cached_osm_input.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/data_provenance.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/final_audit.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/full_experiment_output.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/graph_scale_strategy.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/manuscript_report_alignment.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/parameter_evidence.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/pilot_region_accepted.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/rail_evidence.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/reproducibility.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/sensitivity_analysis.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/validation_package.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | root_document_or_config | `plan.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | script | `scripts/audit_plan_artifacts.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | script | `scripts/run_acceptance_audit.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/acceptance_orchestration.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/final_study_readiness.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/reproducibility_smoke.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | root_document_or_config | `status.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_acceptance_orchestration.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_final_study_readiness.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_plan_audit.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| ?? | data_or_manifest | `data/road/road_source_decision_manifest.json` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | data_or_manifest | `data/road/road_source_decision_packet.csv` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | documentation | `docs/road_source_decision_packet.md` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | script | `scripts/write_road_source_decision_packet.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | realworld_code | `src/realworld/road_source_decision_packet.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_road_source_decision_packet.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |

## Use

Run this before clean-checkout reproducibility acceptance. Any row means the current working tree contains changes that a clean checkout of the current Git HEAD would not reproduce unless they are committed, packaged, or explicitly excluded from the accepted reproduction scope. The audit excludes its own generated CSV, manifest, and Markdown outputs from candidate rows so reruns do not create self-blockers.
