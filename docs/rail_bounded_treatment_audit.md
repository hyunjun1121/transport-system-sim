# Rail Bounded Treatment Audit

Rail bounded-treatment consistency audit only; cross-artifact mismatch check between rail source-decision rows and stress-profile rows, not rail capacity evidence, not rail availability evidence, not rail-service calibration, not operational service planning, and not formal acceptance. It can identify internal consistency gaps but cannot turn scenario-only or sensitivity-only rows into accepted evidence.

## Verdict

- Audit verdict: `bounded_review_support_only`
- Internal mapping mismatches: 0
- Mismatch count is an internal consistency check only, not validation evidence.
- Warnings: 4
- Pending source decisions: 2
- Publication ready: `false`
- Can mark complete: `false`
- Can support rail evidence gate: `false`
- Can support acceptance gate: `false`

## Row Checks

| Request | Status | Decision | Matched Stress Classes | Blockers | Warnings |
| --- | --- | --- | --- | --- | --- |
| rail_capacity_treatment_request | coverage_documented_not_evidence | pending_reviewer_decision | partial_capacity_reduction | - | source decision is still pending reviewer decision; source decision still needs human review |
| rail_availability_scenario_request | coverage_documented_not_evidence | pending_reviewer_decision | increased_headway; partial_unavailability_or_delay; rail_access_egress_degradation | - | source decision is still pending reviewer decision; source decision still needs human review |

## Boundary

- This audit checks whether bounded capacity and availability treatments are internally mapped to stress-profile rows.
- It does not validate rail timing, rail capacity, emergency rail availability, dispatch, or service operations.
- It must not be used as publication readiness, final-study readiness, rail evidence, or formal acceptance.
