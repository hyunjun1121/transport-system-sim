# Full Experiment Output Review Packet

Sub-agent records are review aids. They do not replace formal acceptance artifacts, source-backed reviewer decisions, calibrated validation, or operational routing approval.

- Gate ID: `full_experiment_output`
- Agent: `Full Experiment Package Agent`
- Status: `blocked`
- Can mark complete: `false`
- Generated at: `2026-05-04T13:32:58+00:00`

## Decision

Full Experiment Package Agent cannot accept gate full_experiment_output; the current final-study readiness audit reports blockers.

## Reviewed Inputs

- scripts/run_pilot_experiments.py
- data/scenarios/disruption_scenarios.csv
- data/scenarios/policy_alternatives.csv
- data/manifests/experiment_acceptance.json
- results/realworld_pilot/pilot_full_results.csv
- results/realworld_pilot/pilot_full_summary.csv
- results/realworld_pilot/pilot_full_manifest.json
- data/manifests/experiment_package_review_packet.csv
- data/manifests/experiment_package_review_manifest.json
- docs/experiment_package_review_packet.md

## Evidence And Source Paths

- data/manifests/experiment_acceptance.json
- results/realworld_pilot/pilot_full_results.csv
- results/realworld_pilot/pilot_full_summary.csv
- results/realworld_pilot/pilot_full_manifest.json
- data/manifests/experiment_package_review_packet.csv
- data/manifests/experiment_package_review_manifest.json
- docs/experiment_package_review_packet.md
- docs/review_packets/full_experiment_output.md

## Risks

- Current outputs are useful scaffold runs, not final calibrated study results.
- Upstream input changes invalidate current experiment summaries.
- create an explicit experiment acceptance record after input validation, graph-scope, and scenario-policy-seed review
- accept or regenerate full pilot outputs after input validation and graph-scale decision
- review experiment-package rows before formal experiment acceptance

## Required Actions

- Regenerate or accept full outputs after input, graph-scale, and validation gates close.
- Create experiment_acceptance.json with matching run profile and row counts.
- create an explicit experiment acceptance record after input validation, graph-scope, and scenario-policy-seed review
- accept or regenerate full pilot outputs after input validation and graph-scale decision
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
    "create an explicit experiment acceptance record after input validation, graph-scope, and scenario-policy-seed review",
    "accept or regenerate full pilot outputs after input validation and graph-scale decision",
    "review experiment-package rows before formal experiment acceptance"
  ],
  "details": {
    "acceptance_path": "data/manifests/experiment_acceptance.json",
    "acceptance_record_present": false,
    "accepted_run_profile": "",
    "design_status": "accepted_full_profile_pending_input_validation_and_compute_budget",
    "experiment_package_review_count_mismatch_count": 0,
    "experiment_package_review_manifest_present": true,
    "experiment_package_review_publication_ready": false,
    "experiment_package_review_row_count": 9,
    "result_scope": "Pilot full scenario-policy-seed output for quasi-real decision-support evaluation; not calibrated real-world results or an operational forecast.",
    "row_count": 1890,
    "scope_blocked": true,
    "summary_row_count": 63
  },
  "evidence": [
    "data/manifests/experiment_acceptance.json",
    "results/realworld_pilot/pilot_full_results.csv",
    "results/realworld_pilot/pilot_full_summary.csv",
    "results/realworld_pilot/pilot_full_manifest.json",
    "data/manifests/experiment_package_review_packet.csv",
    "data/manifests/experiment_package_review_manifest.json",
    "docs/experiment_package_review_packet.md"
  ],
  "gate_id": "full_experiment_output",
  "label": "Full Experiment Output",
  "ready": false
}
```
