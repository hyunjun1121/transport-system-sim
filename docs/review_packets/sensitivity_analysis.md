# Sensitivity Analysis Review Packet

Sub-agent records are review aids. They do not replace formal acceptance artifacts, source-backed reviewer decisions, calibrated validation, or operational routing approval.

- Gate ID: `sensitivity_analysis`
- Agent: `Sensitivity Analysis Review Agent`
- Status: `blocked`
- Can mark complete: `false`
- Generated at: `2026-05-08T21:48:03+00:00`

## Decision

Sensitivity Analysis Review Agent cannot accept gate sensitivity_analysis; the current final-study readiness audit reports blockers.

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
- create an explicit sensitivity acceptance record after SALib output and Sobol-decision review
- resolve sensitivity strategy-readiness blockers before sensitivity acceptance
- sensitivity strategy readiness: sensitivity outputs use a reduced analysis graph
- sensitivity strategy readiness: current sensitivity result scope is scaffold or not calibrated
- sensitivity strategy readiness: Morris-vs-Sobol method decision is not recorded in formal acceptance
- sensitivity strategy readiness: data/manifests/sensitivity_acceptance.json is absent
- review sensitivity strategy-readiness human-decision items before sensitivity acceptance
- accept sensitivity outputs on final graph/evidence scope; current Morris outputs are scaffold-level

## Required Actions

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

## Formal Acceptance Boundary

To close this final-study gate, create or update the formal acceptance artifact listed in the agent definition. Do not edit this review packet as a substitute for formal acceptance.

Formal acceptance artifacts:

- data/manifests/sensitivity_acceptance.json

## Current Final-Study Gate Details

```json
{
  "artifact_present": true,
  "blockers": [
    "create an explicit sensitivity acceptance record after SALib output and Sobol-decision review",
    "resolve sensitivity strategy-readiness blockers before sensitivity acceptance",
    "sensitivity strategy readiness: sensitivity outputs use a reduced analysis graph",
    "sensitivity strategy readiness: current sensitivity result scope is scaffold or not calibrated",
    "sensitivity strategy readiness: Morris-vs-Sobol method decision is not recorded in formal acceptance",
    "sensitivity strategy readiness: data/manifests/sensitivity_acceptance.json is absent",
    "review sensitivity strategy-readiness human-decision items before sensitivity acceptance",
    "accept sensitivity outputs on final graph/evidence scope; current Morris outputs are scaffold-level"
  ],
  "details": {
    "acceptance_path": "data/manifests/sensitivity_acceptance.json",
    "acceptance_record_present": false,
    "accepted_method": "",
    "index_review_all_zero_group_count": 150,
    "index_review_artifacts_present": true,
    "index_review_can_mark_complete": false,
    "index_review_human_review_metric_count": 7,
    "index_review_packet_row_count": 7,
    "index_review_publication_ready": false,
    "index_review_unavailable_index_row_count": 168,
    "index_review_zero_mu_star_row_count": 4272,
    "method": "salib_morris",
    "method_decision_artifacts_present": true,
    "method_decision_blocking_decision_count": 4,
    "method_decision_can_mark_complete": false,
    "method_decision_human_review_decision_count": 3,
    "method_decision_publication_ready": false,
    "method_decision_row_count": 7,
    "method_decision_sobol_decision_recorded": false,
    "method_decision_sobol_waiver_created": false,
    "method_decision_status_counts": {
      "blocked_missing_morris_vs_sobol_decision": 1,
      "blocked_missing_sensitivity_acceptance_record": 1,
      "blocked_reduced_graph_scope_dependency": 1,
      "blocked_scaffold_result_scope": 1,
      "needs_human_review_defer_or_continue": 1,
      "needs_human_review_index_handling_policy": 1,
      "needs_human_review_morris_screening_scope": 1
    },
    "result_scope": "Pilot scaffold SALib Morris sensitivity output; not calibrated real-world sensitivity evidence or an operational forecast.",
    "review_packet_acceptance_gate_closure_candidate_count": 0,
    "review_packet_publication_ready": false,
    "review_packet_row_count": 6,
    "review_packet_rows_with_index_issues": 0,
    "review_packet_zero_mu_star_count": 4272,
    "row_count": 4320,
    "scope_blocked": true,
    "sobol_requirement_decision": "",
    "strategy_readiness_artifacts_present": true,
    "strategy_readiness_blocking_request_count": 4,
    "strategy_readiness_can_mark_complete": false,
    "strategy_readiness_human_review_request_count": 3,
    "strategy_readiness_manifest_present": true,
    "strategy_readiness_publication_ready": false,
    "strategy_readiness_remaining_blockers": [
      "sensitivity outputs use a reduced analysis graph",
      "current sensitivity result scope is scaffold or not calibrated",
      "Morris-vs-Sobol method decision is not recorded in formal acceptance",
      "data/manifests/sensitivity_acceptance.json is absent"
    ],
    "strategy_readiness_status_counts": {
      "blocked_missing_morris_vs_sobol_decision": 1,
      "blocked_missing_sensitivity_acceptance_record": 1,
      "blocked_reduced_graph_scope_for_sensitivity_claims": 1,
      "blocked_scaffold_or_not_calibrated_result_scope": 1,
      "needs_human_review_morris_artifact_selection": 1,
      "needs_human_review_unavailable_morris_indices": 1,
      "needs_human_review_zero_mu_star_interpretation": 1
    },
    "summary_row_count": 7056
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
  "ready": false
}
```
