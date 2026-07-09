# Full Experiment Output Review Packet

Sub-agent records are review aids. They do not replace formal acceptance artifacts, source-backed reviewer decisions, calibrated validation, or operational routing approval.

- Gate ID: `full_experiment_output`
- Agent: `Full Experiment Package Agent`
- Status: `blocked`
- Can mark complete: `false`
- Generated at: `2026-07-05T07:30:47+00:00`

## Decision

Full Experiment Package Agent cannot accept gate full_experiment_output; the current final-study readiness audit reports blockers.

## Reviewed Inputs

- scripts/run_pilot_experiments.py
- data/scenarios/disruption_scenarios.csv
- data/scenarios/policy_alternatives.csv
- data/manifests/experiment_package_review_manifest.json
- data/manifests/experiment_strategy_readiness_manifest.json
- data/manifests/experiment_design_decision_manifest.json
- docs/experiment_design_decision_packet.md
- data/manifests/experiment_acceptance.json
- results/realworld_pilot/pilot_full_results.csv
- results/realworld_pilot/pilot_full_summary.csv
- results/realworld_pilot/pilot_full_manifest.json
- data/manifests/experiment_package_review_packet.csv
- docs/experiment_package_review_packet.md
- data/manifests/experiment_strategy_readiness_packet.csv
- docs/experiment_strategy_readiness_packet.md
- data/manifests/experiment_design_decision_packet.csv
- scripts/write_experiment_design_decision_packet.py

## Evidence And Source Paths

- data/manifests/experiment_acceptance.json
- results/realworld_pilot/pilot_full_results.csv
- results/realworld_pilot/pilot_full_summary.csv
- results/realworld_pilot/pilot_full_manifest.json
- data/manifests/experiment_package_review_packet.csv
- data/manifests/experiment_package_review_manifest.json
- docs/experiment_package_review_packet.md
- data/manifests/experiment_strategy_readiness_packet.csv
- data/manifests/experiment_strategy_readiness_manifest.json
- docs/experiment_strategy_readiness_packet.md
- data/manifests/experiment_design_decision_packet.csv
- data/manifests/experiment_design_decision_manifest.json
- docs/experiment_design_decision_packet.md
- scripts/write_experiment_design_decision_packet.py
- docs/review_packets/full_experiment_output.md

## Risks

- Current outputs are useful scaffold runs, not final calibrated study results.
- Upstream input changes invalidate current experiment summaries.
- resolve experiment strategy-readiness blockers before experiment acceptance
- experiment strategy readiness: current full-pilot result scope is scaffold or not calibrated
- experiment strategy readiness: full-pilot outputs depend on a graph method that has no graph-scale decision
- experiment strategy readiness: upstream input, road override, parameter, benchmark, or provenance gates are unresolved
- review experiment strategy-readiness human-decision items before experiment acceptance
- resolve experiment design-decision blockers before experiment acceptance
- experiment design decision: experiment outputs depend on a graph method that is not selected by review
- experiment design decision: upstream input, road override, parameter, validation, or provenance gates are not closed
- experiment design decision: current full-pilot result scope is scaffold or not calibrated
- review experiment design-decision human-decision items before experiment acceptance
- accept or regenerate full pilot outputs after input validation and graph-scale decision
- experiment acceptance counts must match the pilot full manifest: row_count: acceptance=15870, manifest=12420; summary_row_count: acceptance=529, manifest=414; scenario_count: acceptance=23, manifest=18
- review experiment-package rows before formal experiment acceptance

## Required Actions

- Regenerate or accept full outputs after input, graph-scale, and validation gates close.
- Create experiment_acceptance.json with matching run profile and row counts.
- resolve experiment strategy-readiness blockers before experiment acceptance
- experiment strategy readiness: current full-pilot result scope is scaffold or not calibrated
- experiment strategy readiness: full-pilot outputs depend on a graph method that has no graph-scale decision
- experiment strategy readiness: upstream input, road override, parameter, benchmark, or provenance gates are unresolved
- review experiment strategy-readiness human-decision items before experiment acceptance
- resolve experiment design-decision blockers before experiment acceptance
- experiment design decision: experiment outputs depend on a graph method that is not selected by review
- experiment design decision: upstream input, road override, parameter, validation, or provenance gates are not closed
- experiment design decision: current full-pilot result scope is scaffold or not calibrated
- review experiment design-decision human-decision items before experiment acceptance
- accept or regenerate full pilot outputs after input validation and graph-scale decision
- experiment acceptance counts must match the pilot full manifest: row_count: acceptance=15870, manifest=12420; summary_row_count: acceptance=529, manifest=414; scenario_count: acceptance=23, manifest=18
- review experiment-package rows before formal experiment acceptance

## Formal Acceptance Boundary

To close this final-study gate, create or update the formal acceptance artifact listed in the agent definition. Do not edit this review packet as a substitute for formal acceptance.

Formal acceptance artifacts:

- data/manifests/experiment_acceptance.json

## Current Final-Study Gate Details

```json
{
  "artifact_present": true,
  "blockers": [
    "resolve experiment strategy-readiness blockers before experiment acceptance",
    "experiment strategy readiness: current full-pilot result scope is scaffold or not calibrated",
    "experiment strategy readiness: full-pilot outputs depend on a graph method that has no graph-scale decision",
    "experiment strategy readiness: upstream input, road override, parameter, benchmark, or provenance gates are unresolved",
    "review experiment strategy-readiness human-decision items before experiment acceptance",
    "resolve experiment design-decision blockers before experiment acceptance",
    "experiment design decision: experiment outputs depend on a graph method that is not selected by review",
    "experiment design decision: upstream input, road override, parameter, validation, or provenance gates are not closed",
    "experiment design decision: current full-pilot result scope is scaffold or not calibrated",
    "review experiment design-decision human-decision items before experiment acceptance",
    "accept or regenerate full pilot outputs after input validation and graph-scale decision",
    "experiment acceptance counts must match the pilot full manifest: row_count: acceptance=15870, manifest=12420; summary_row_count: acceptance=529, manifest=414; scenario_count: acceptance=23, manifest=18",
    "review experiment-package rows before formal experiment acceptance"
  ],
  "details": {
    "acceptance_path": "data/manifests/experiment_acceptance.json",
    "acceptance_record_present": true,
    "accepted_run_profile": "full_pilot",
    "design_decision_artifacts_present": true,
    "design_decision_blocking_decision_count": 3,
    "design_decision_can_mark_complete": false,
    "design_decision_human_review_decision_count": 5,
    "design_decision_manifest_present": true,
    "design_decision_publication_ready": false,
    "design_decision_remaining_blockers": [
      "experiment outputs depend on a graph method that is not selected by review",
      "upstream input, road override, parameter, validation, or provenance gates are not closed",
      "current full-pilot result scope is scaffold or not calibrated"
    ],
    "design_decision_scenario_policy_seed_decision_recorded": false,
    "design_decision_selected_run_profile_recorded": false,
    "design_decision_status_counts": {
      "blocked_graph_scale_dependency": 1,
      "blocked_input_evidence_dependency": 1,
      "blocked_scaffold_or_not_calibrated_experiment_scope": 1,
      "needs_human_review_current_full_profile_scope": 1,
      "needs_human_review_existing_experiment_acceptance": 1,
      "needs_human_review_multi_corridor_profile_scope": 1,
      "needs_human_review_regenerate_or_retain_outputs": 1,
      "needs_human_review_scenario_policy_seed_design": 1
    },
    "design_status": "review_scoped_full_profile_pending_input_validation_and_compute_budget",
    "experiment_package_review_count_mismatch_count": 0,
    "experiment_package_review_manifest_present": true,
    "experiment_package_review_publication_ready": false,
    "experiment_package_review_row_count": 9,
    "result_scope": "Engineering-only pilot output for quasi-real decision-support method review (non-publication, non-acceptance, non-operational); not publication evidence, not final-study evidence, not formal acceptance evidence, not calibrated real-world results, and not an operational route plan or forecast. Base profile scope: Pilot full scenario-policy-seed output for quasi-real decision-support evaluation; not calibrated real-world results or an operational forecast.",
    "row_count": 12420,
    "scope_blocked": true,
    "strategy_readiness_artifacts_present": true,
    "strategy_readiness_blocking_request_count": 3,
    "strategy_readiness_can_mark_complete": false,
    "strategy_readiness_human_review_request_count": 6,
    "strategy_readiness_manifest_present": true,
    "strategy_readiness_publication_ready": false,
    "strategy_readiness_remaining_blockers": [
      "current full-pilot result scope is scaffold or not calibrated",
      "full-pilot outputs depend on a graph method that has no graph-scale decision",
      "upstream input, road override, parameter, benchmark, or provenance gates are unresolved"
    ],
    "strategy_readiness_status_counts": {
      "blocked_graph_scale_dependency": 1,
      "blocked_input_evidence_dependency": 1,
      "blocked_scaffold_or_not_calibrated_experiment_scope": 1,
      "needs_human_review_common_random_numbers": 1,
      "needs_human_review_experiment_acceptance_record": 1,
      "needs_human_review_experiment_checksums": 1,
      "needs_human_review_experiment_row_counts": 2,
      "needs_human_review_scenario_policy_seed_design": 1
    },
    "summary_row_count": 414
  },
  "evidence": [
    "data/manifests/experiment_acceptance.json",
    "results/realworld_pilot/pilot_full_results.csv",
    "results/realworld_pilot/pilot_full_summary.csv",
    "results/realworld_pilot/pilot_full_manifest.json",
    "data/manifests/experiment_package_review_packet.csv",
    "data/manifests/experiment_package_review_manifest.json",
    "docs/experiment_package_review_packet.md",
    "data/manifests/experiment_strategy_readiness_packet.csv",
    "data/manifests/experiment_strategy_readiness_manifest.json",
    "docs/experiment_strategy_readiness_packet.md",
    "data/manifests/experiment_design_decision_packet.csv",
    "data/manifests/experiment_design_decision_manifest.json",
    "docs/experiment_design_decision_packet.md",
    "scripts/write_experiment_design_decision_packet.py"
  ],
  "gate_id": "full_experiment_output",
  "label": "Full Experiment Output",
  "ready": false
}
```
