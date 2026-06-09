# Phase 4 Rail/Transit Stress Profile Results - 2026-06-02

## Scope

This phase adds a rail/transit stress-profile review packet for the current
real-world or quasi-real-world simulation plan. The packet documents whether
the current scenario and sensitivity artifacts represent the minimum rail
stress classes needed for Phase 4 review:

- normal service assumption;
- increased headway;
- partial capacity reduction;
- rail access or egress degradation;
- station processing or transfer-delay proxy;
- partial unavailability or delay.

The work is review support only. It does not create rail-service calibration,
emergency rail availability evidence, operational service planning, publication
readiness, or formal acceptance.

## Files Added Or Updated

Added:

- `src/realworld/rail_transit_stress_profile_packet.py`
- `scripts/write_rail_transit_stress_profile_packet.py`
- `tests/test_realworld_rail_transit_stress_profile_packet.py`
- `data/rail/rail_transit_stress_profile_packet.csv`
- `data/rail/rail_transit_stress_profile_manifest.json`
- `docs/rail_transit_stress_profile_packet.md`

Updated:

- `src/realworld/final_study_readiness.py`
- `tests/test_realworld_final_study_readiness.py`
- `src/realworld/rail_transit_stress_profile_packet.py`
- `plan.md`
- `agents.md`
- `status.md`
- `docs/current_goal_completion_audit.md`
- `data/manifests/current_goal_completion_audit.json`
- `docs/formal_acceptance_package_audit.md`
- `data/manifests/formal_acceptance_package_audit.json`

## Implementation Notes

- The stress-profile packet has six rows and all required stress classes are
  present.
- Every row keeps:
  - `publication_ready=false`;
  - `can_support_rail_evidence_gate=false`;
  - `can_support_acceptance_gate=false`.
- The normal-service row is explicitly classified as
  `documented_assumption_proxy` and `represented_by_assumption_proxy`.
- Station-access stress is represented as road or connector degradation around
  rail access/egress points, not a rail-service outage.
- Final-study rail readiness now requires:
  - rail service publication readiness;
  - station binding readiness;
  - reviewed rail source decisions with zero blocking and human-review rows;
  - documented rail/transit stress-profile coverage.

## Sub-Agent Review

Two GPT-5.5 xhigh read-only reviewers were used.

Implementation reviewer `019e88c3-d65f-7311-b8c9-4080be4ccf7e` inspected the
stress-profile module, writer, tests, generated packet, final-study readiness
logic, publication readiness logic, and plan-audit scope. It reported no
blocker or high findings. Medium/low recommendations were to add a focused
regression test for rail-gate misuse and clarify whether the stress-profile
artifact should be required by the rail gate.

Adversarial reviewer `019e88c4-4d43-7202-8116-36c91d4684e4` inspected the plan,
status, stress-profile packet, publication readiness audit, current-goal audit,
formal acceptance package audit, and readiness logic. It found no overclaim in
the stress-profile packet itself, but required regeneration of current-goal and
formal/readiness audit outputs after the new rail artifacts. It also flagged
an earlier implementation-status label as wording that could be misread as
source-backed evidence.

Both findings were addressed:

- final-study rail readiness now checks stress-profile documentation;
- a regression test covers that guard;
- the potentially ambiguous implementation-status label was replaced with
  `represented_by_assumption_proxy`;
- publication readiness, final-study readiness, current-goal completion, and
  formal package audit outputs were regenerated.

## Generated Evidence Summary

The regenerated rail/transit stress-profile manifest reports:

- `row_count`: 6
- `required_stress_classes_present`: `true`
- `missing_runtime_hook_count`: 0
- `publication_ready`: `false`
- `can_mark_complete`: `false`
- `can_support_rail_evidence_gate`: `false`
- `can_support_acceptance_gate`: `false`
- `rail_source_decision_blocker_count`: 6

The regenerated current-goal completion audit reports:

- `final_study_ready`: `false`
- `blocked_gate_count`: 12
- rail evidence gate: blocked
- stress-profile artifacts listed under rail evidence

The regenerated formal acceptance package audit reports:

- `formal_acceptance_ready`: `false`
- `ready_gate_count`: 0
- `blocked_gate_count`: 12
- `can_mark_complete`: `false`

## Commands Run

Passed:

```powershell
.\.venv\Scripts\python scripts\write_rail_transit_stress_profile_packet.py
.\.venv\Scripts\python -m py_compile src\realworld\rail_transit_stress_profile_packet.py src\realworld\final_study_readiness.py tests\test_realworld_rail_transit_stress_profile_packet.py tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python scripts\audit_publication_readiness.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
.\.venv\Scripts\python scripts\write_goal_completion_audit.py
.\.venv\Scripts\python scripts\audit_formal_acceptance_artifacts.py
.\.venv\Scripts\python scripts\validate_formal_acceptance_package.py
.\.venv\Scripts\python tests\test_realworld_rail_transit_stress_profile_packet.py
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
```

## Remaining Risks

- No reviewed GTFS feed is currently retained for the pilot rail leg.
- No GTFS Validator report is currently retained for a reviewed pilot GTFS
  feed.
- No reviewed timetable or shortest-path cache payload is currently accepted.
- Rail capacity and rail availability remain human/source-decision items.
- Formal acceptance artifacts remain absent by design until reviewer-backed
  evidence exists.
- This phase improves stress coverage documentation and guardrails only; it
  does not close rail, parameter, validation, publication, final-study, or
  formal acceptance gates.
