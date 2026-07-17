# Tracked Artifact Audit

This audit checks whether current changed artifacts would be present in a clean checkout of the current Git HEAD. It does not commit files, approve reproducibility, validate evidence quality, or close final-study gates.

## Summary

- Clean-checkout reproducibility ready: `false`
- Can mark complete: `false`
- Changed reproducibility artifacts: 122
- Blocking changed artifacts: 122
- Untracked artifacts: 47
- Modified or staged artifacts: 75

## Changed Artifacts

| Status | Category | Path | Required Action |
| --- | --- | --- | --- |
| M | root_document_or_config | `README.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | root_document_or_config | `agents.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/acceptance_decision_template_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/acceptance_orchestration_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_review_path_audit.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/cached_osm_input__road_rail_parameter_evidence_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/graph_scale_strategy__graph_scale_method_review_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/agent_reviews/manuscript_report_alignment__paper_report_claim_alignment_agent.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/claim_alignment_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/claim_alignment_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/current_goal_completion_audit.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/graph_scale_strategy_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/manuscript_report_alignment_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/draft_acceptance/road_class_overrides_pre_review.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/manuscript_report_decision_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/manuscript_report_decision_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/publication_readiness_audit.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_context_cache_request_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_provenance_priority_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_url_remediation_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_url_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/road/road_source_readiness_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/clean_checkout_reproducibility_smoke_log.jsonl` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/clean_checkout_reproducibility_smoke_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/graph_scale_method_decision_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/graph_scale_strategy_readiness_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/reproducibility_decision_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/reproducibility_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/reproducibility_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/reproducibility_smoke_log.jsonl` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/validation/reproducibility_smoke_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/agent_review_path_audit.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/claim_alignment_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/clean_checkout_reproducibility_smoke.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/current_goal_completion_audit.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/formal_acceptance_pre_review.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/human_acceptance_runbook.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/manuscript_report_decision_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/plan_completion_audit.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/reproducibility_decision_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/acceptance_review_index.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/cached_osm_input.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/graph_scale_strategy.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/manuscript_report_alignment.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/review_packets/reproducibility.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/source_provenance_priority_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/source_url_remediation_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/source_url_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | paper | `paper/paper_draft.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | root_document_or_config | `plan.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | root_document_or_config | `report.docx` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/tables/pilot_full_statistics_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/tables/pilot_multi_corridor_full_statistics_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | generated_result | `results/realworld_pilot/tables/pilot_multi_corridor_statistics_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | script | `scripts/audit_plan_artifacts.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/__init__.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/agent_review_path_audit.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/goal_completion_audit.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/graph_scale_strategy_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/pilot_statistics.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/reproducibility_smoke.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/road_source_decision_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/road_source_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/tracked_artifact_audit.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | root_document_or_config | `status.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_agent_review_path_audit.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_final_study_readiness.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_goal_completion_audit.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_graph_scale_strategy_readiness_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_pilot_statistics.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_plan_audit.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_reproducibility_smoke.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_road_source_decision_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_source_provenance_priority_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_tracked_artifact_audit.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| ?? | data_or_manifest | `data/manifests/crn_pairing_audit.csv` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | data_or_manifest | `data/manifests/crn_pairing_audit_manifest.json` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | data_or_manifest | `data/manifests/deterministic_rerun_audit.csv` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | data_or_manifest | `data/manifests/deterministic_rerun_audit_manifest.json` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | data_or_manifest | `data/manifests/draft_acceptance/formal_target_placeholders_20260510/` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | data_or_manifest | `data/manifests/experiment_statistical_analysis_plan.json` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | data_or_manifest | `data/manifests/replication_adequacy_audit.csv` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | data_or_manifest | `data/manifests/replication_adequacy_audit_manifest.json` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | data_or_manifest | `data/manifests/seed_stream_manifest.json` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | data_or_manifest | `data/parameters/draft_acceptance/` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | documentation | `docs/crn_pairing_audit.md` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | documentation | `docs/deterministic_rerun_audit.md` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | documentation | `docs/draft_acceptance/` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | documentation | `docs/experiment_statistical_analysis_plan.md` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | documentation | `docs/expert_consultation_followup_plan.md` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | documentation | `docs/expert_consultation_request.md` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | documentation | `docs/expert_consultation_request_reply.md` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | documentation | `docs/formal_target_placeholder_relocation.md` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | documentation | `docs/replication_adequacy_audit.md` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | documentation | `docs/seed_stream_manifest.md` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | script | `scripts/audit_crn_pairing.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | script | `scripts/audit_deterministic_rerun.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | script | `scripts/audit_replication_adequacy.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | script | `scripts/audit_review_package_paths.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | script | `scripts/build_review_package.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | script | `scripts/write_experiment_statistical_plan.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | script | `scripts/write_expert_review_handoff.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | script | `scripts/write_review_package_inventory.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | script | `scripts/write_seed_stream_manifest.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | realworld_code | `src/realworld/crn_pairing_audit.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | realworld_code | `src/realworld/deterministic_rerun_audit.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | realworld_code | `src/realworld/experiment_statistical_plan.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | realworld_code | `src/realworld/replication_adequacy_audit.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | realworld_code | `src/realworld/review_package_builder.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | realworld_code | `src/realworld/review_package_handoff.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | realworld_code | `src/realworld/review_package_inventory.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | realworld_code | `src/realworld/review_package_path_audit.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | realworld_code | `src/realworld/seed_stream_manifest.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_crn_pairing_audit.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_deterministic_rerun_audit.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_experiment_statistical_plan.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_replication_adequacy_audit.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_review_package_builder.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_review_package_handoff.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_review_package_inventory.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_review_package_path_audit.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_seed_stream_manifest.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |

## Use

Run this before clean-checkout reproducibility acceptance. Any row means the current working tree contains changes that a clean checkout of the current Git HEAD would not reproduce unless they are committed, packaged, or explicitly excluded from the accepted reproduction scope. The audit excludes its own generated CSV, manifest, and Markdown outputs from candidate rows so reruns do not create self-blockers. It also excludes review-package build, inventory, and path-audit sidecars because those are generated after ZIP assembly for external handoff and are not accepted reproduction-scope inputs.
