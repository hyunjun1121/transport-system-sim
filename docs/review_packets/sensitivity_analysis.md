# Sensitivity Analysis Review Packet

Sub-agent records are review aids. They do not replace formal acceptance artifacts, source-backed reviewer decisions, calibrated validation, or operational routing approval.

- Gate ID: `sensitivity_analysis`
- Agent: `Sensitivity Analysis Review Agent`
- Status: `blocked`
- Can mark complete: `false`
- Generated at: `2026-05-04T11:33:48+00:00`

## Decision

Sensitivity Analysis Review Agent cannot accept gate sensitivity_analysis; the current final-study readiness audit reports blockers.

## Reviewed Inputs

- data/validation/sensitivity_review_packet.csv
- data/validation/sensitivity_review_manifest.json
- scripts/run_sensitivity.py
- data/manifests/sensitivity_acceptance.json
- results/realworld_pilot/morris_results.csv
- results/realworld_pilot/morris_summary.csv
- results/realworld_pilot/morris_manifest.json
- scripts/audit_sensitivity_diagnostics.py
- scripts/write_sensitivity_review_packet.py

## Evidence And Source Paths

- data/manifests/sensitivity_acceptance.json
- results/realworld_pilot/morris_results.csv
- results/realworld_pilot/morris_summary.csv
- results/realworld_pilot/morris_manifest.json
- data/validation/sensitivity_review_packet.csv
- data/validation/sensitivity_review_manifest.json
- scripts/run_sensitivity.py
- scripts/audit_sensitivity_diagnostics.py
- scripts/write_sensitivity_review_packet.py
- docs/review_packets/sensitivity_analysis.md

## Risks

- Sensitivity outputs are scaffold-level while upstream evidence gates remain blocked.
- Wrong parameter ranges can reverse strategy-regime conclusions.
- create an explicit sensitivity acceptance record after SALib output and Sobol-decision review
- accept sensitivity outputs on final graph/evidence scope; current Morris outputs are scaffold-level

## Required Actions

- Review parameter ranges and decide whether Morris is enough or Sobol is required.
- Create sensitivity_acceptance.json after final input and graph scope are accepted.
- create an explicit sensitivity acceptance record after SALib output and Sobol-decision review
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
    "accept sensitivity outputs on final graph/evidence scope; current Morris outputs are scaffold-level"
  ],
  "details": {
    "acceptance_path": "data/manifests/sensitivity_acceptance.json",
    "acceptance_record_present": false,
    "accepted_method": "",
    "method": "salib_morris",
    "result_scope": "Pilot scaffold SALib Morris sensitivity output; not calibrated real-world sensitivity evidence or an operational forecast.",
    "review_packet_acceptance_gate_closure_candidate_count": 0,
    "review_packet_publication_ready": false,
    "review_packet_row_count": 6,
    "review_packet_rows_with_index_issues": 168,
    "review_packet_zero_mu_star_count": 4272,
    "row_count": 4320,
    "scope_blocked": true,
    "sobol_requirement_decision": "",
    "summary_row_count": 7056
  },
  "evidence": [
    "data/manifests/sensitivity_acceptance.json",
    "results/realworld_pilot/morris_results.csv",
    "results/realworld_pilot/morris_summary.csv",
    "results/realworld_pilot/morris_manifest.json",
    "data/validation/sensitivity_review_packet.csv",
    "data/validation/sensitivity_review_manifest.json",
    "scripts/run_sensitivity.py",
    "scripts/audit_sensitivity_diagnostics.py",
    "scripts/write_sensitivity_review_packet.py"
  ],
  "gate_id": "sensitivity_analysis",
  "label": "Sensitivity Analysis",
  "ready": false
}
```
