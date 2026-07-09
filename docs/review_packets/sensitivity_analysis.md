# Sensitivity Analysis Review Packet

Sub-agent records are review aids. They do not replace formal acceptance artifacts, source-backed reviewer decisions, calibrated validation, or operational routing approval.

- Gate ID: `sensitivity_analysis`
- Agent: `Sensitivity Analysis Review Agent`
- Status: `accepted`
- Can mark complete: `true`
- Generated at: `2026-07-05T07:30:47+00:00`

## Decision

Sensitivity Analysis Review Agent can mark gate sensitivity_analysis complete because the final-study readiness audit already reports this gate as ready.

## Reviewed Inputs

- data/validation/sensitivity_review_packet.csv
- data/validation/sensitivity_review_manifest.json
- data/validation/sensitivity_index_review_manifest.json
- docs/sensitivity_index_review_packet.md
- data/validation/sensitivity_strategy_readiness_manifest.json
- data/validation/sensitivity_method_decision_manifest.json
- docs/sensitivity_method_decision_packet.md
- scripts/run_sensitivity.py
- data/manifests/sensitivity_acceptance.json
- results/realworld_pilot/morris_results.csv
- results/realworld_pilot/morris_summary.csv
- results/realworld_pilot/morris_manifest.json
- data/validation/sensitivity_index_review_packet.csv
- data/validation/sensitivity_strategy_readiness_packet.csv
- docs/sensitivity_strategy_readiness_packet.md
- data/validation/sensitivity_method_decision_packet.csv
- scripts/audit_sensitivity_diagnostics.py
- scripts/write_sensitivity_review_packet.py
- scripts/write_sensitivity_index_review_packet.py
- scripts/write_sensitivity_strategy_readiness_packet.py
- scripts/write_sensitivity_method_decision_packet.py

## Evidence And Source Paths

- data/manifests/sensitivity_acceptance.json
- results/realworld_pilot/morris_results.csv
- results/realworld_pilot/morris_summary.csv
- results/realworld_pilot/morris_manifest.json
- data/validation/sensitivity_review_packet.csv
- data/validation/sensitivity_review_manifest.json
- data/validation/sensitivity_index_review_packet.csv
- data/validation/sensitivity_index_review_manifest.json
- docs/sensitivity_index_review_packet.md
- data/validation/sensitivity_strategy_readiness_packet.csv
- data/validation/sensitivity_strategy_readiness_manifest.json
- docs/sensitivity_strategy_readiness_packet.md
- data/validation/sensitivity_method_decision_packet.csv
- data/validation/sensitivity_method_decision_manifest.json
- docs/sensitivity_method_decision_packet.md
- scripts/run_sensitivity.py
- scripts/audit_sensitivity_diagnostics.py
- scripts/write_sensitivity_review_packet.py
- scripts/write_sensitivity_index_review_packet.py
- scripts/write_sensitivity_strategy_readiness_packet.py
- scripts/write_sensitivity_method_decision_packet.py
- docs/review_packets/sensitivity_analysis.md

## Risks

- Sensitivity outputs are scaffold-level while upstream evidence gates remain blocked.
- Wrong parameter ranges can reverse strategy-regime conclusions.

## Required Actions

- No further action for this gate scope.

## Formal Acceptance Boundary

To close this final-study gate, create or update the formal acceptance artifact listed in the agent definition. Do not edit this review packet as a substitute for formal acceptance.

Formal acceptance artifacts:

- data/manifests/sensitivity_acceptance.json

## Current Final-Study Gate Details

```json
{
  "artifact_present": true,
  "blockers": [],
  "details": {
    "acceptance_path": "data/manifests/sensitivity_acceptance.json",
    "acceptance_record_present": true,
    "accepted_method": "salib_morris",
    "index_review_all_zero_group_count": 878,
    "index_review_artifacts_present": true,
    "index_review_can_mark_complete": false,
    "index_review_human_review_metric_count": 7,
    "index_review_packet_row_count": 7,
    "index_review_publication_ready": false,
    "index_review_unavailable_index_row_count": 4832,
    "index_review_zero_mu_star_row_count": 33619,
    "method": "salib_morris",
    "method_decision_artifacts_present": true,
    "method_decision_blocking_decision_count": 2,
    "method_decision_can_mark_complete": false,
    "method_decision_human_review_decision_count": 5,
    "method_decision_publication_ready": false,
    "method_decision_row_count": 7,
    "method_decision_sobol_decision_recorded": false,
    "method_decision_sobol_waiver_created": false,
    "method_decision_status_counts": {
      "blocked_missing_morris_vs_sobol_decision": 1,
      "blocked_reduced_graph_scope_dependency": 1,
      "needs_human_review_defer_or_continue": 1,
      "needs_human_review_existing_sensitivity_acceptance": 1,
      "needs_human_review_index_handling_policy": 1,
      "needs_human_review_morris_screening_scope": 1,
      "needs_human_review_result_scope": 1
    },
    "result_scope": "Reviewer-accepted SALib Morris sensitivity output for quasi-real decision-support evaluation within formal-acceptance claim boundary.",
    "review_packet_acceptance_gate_closure_candidate_count": 0,
    "review_packet_publication_ready": false,
    "review_packet_row_count": 6,
    "review_packet_rows_with_index_issues": 0,
    "review_packet_zero_mu_star_count": 33619,
    "row_count": 37536,
    "scope_blocked": false,
    "sobol_requirement_decision": "not_required",
    "strategy_readiness_artifacts_present": true,
    "strategy_readiness_blocking_request_count": 2,
    "strategy_readiness_can_mark_complete": false,
    "strategy_readiness_human_review_request_count": 5,
    "strategy_readiness_manifest_present": true,
    "strategy_readiness_publication_ready": false,
    "strategy_readiness_remaining_blockers": [
      "sensitivity outputs use a reduced analysis graph",
      "Morris-vs-Sobol method decision is not recorded in formal acceptance"
    ],
    "strategy_readiness_status_counts": {
      "blocked_missing_morris_vs_sobol_decision": 1,
      "blocked_reduced_graph_scope_for_sensitivity_claims": 1,
      "needs_human_review_morris_artifact_selection": 1,
      "needs_human_review_sensitivity_acceptance_record": 1,
      "needs_human_review_sensitivity_result_scope": 1,
      "needs_human_review_unavailable_morris_indices": 1,
      "needs_human_review_zero_mu_star_interpretation": 1
    },
    "summary_row_count": 61824
  },
  "evidence": [
    "data/manifests/sensitivity_acceptance.json",
    "results/realworld_pilot/morris_results.csv",
    "results/realworld_pilot/morris_summary.csv",
    "results/realworld_pilot/morris_manifest.json",
    "data/validation/sensitivity_review_packet.csv",
    "data/validation/sensitivity_review_manifest.json",
    "data/validation/sensitivity_index_review_packet.csv",
    "data/validation/sensitivity_index_review_manifest.json",
    "docs/sensitivity_index_review_packet.md",
    "data/validation/sensitivity_strategy_readiness_packet.csv",
    "data/validation/sensitivity_strategy_readiness_manifest.json",
    "docs/sensitivity_strategy_readiness_packet.md",
    "data/validation/sensitivity_method_decision_packet.csv",
    "data/validation/sensitivity_method_decision_manifest.json",
    "docs/sensitivity_method_decision_packet.md",
    "scripts/run_sensitivity.py",
    "scripts/audit_sensitivity_diagnostics.py",
    "scripts/write_sensitivity_review_packet.py",
    "scripts/write_sensitivity_index_review_packet.py",
    "scripts/write_sensitivity_strategy_readiness_packet.py",
    "scripts/write_sensitivity_method_decision_packet.py"
  ],
  "gate_id": "sensitivity_analysis",
  "label": "Sensitivity Analysis",
  "ready": true
}
```
