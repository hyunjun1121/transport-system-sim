# Phase 4 Stress-Profile Integrity Guard Ledger

Timestamp: 2026-06-03 KST

## Objective

Strengthen rail/transit stress-profile and bounded-treatment guardrails so
scenario/sensitivity coverage cannot be overread as runnable, source-backed, or
publication-ready evidence.

## Agent Findings Integrated

Two GPT-5.5 xhigh read-only reviewers inspected the Phase 4 rail stress-profile,
bounded-treatment, publication-readiness, and final-study readiness logic.

Integrated findings:

- Matched bounded-treatment stress rows must not pass if their
  `implementation_status` is `missing_runtime_hook`.
- Matched bounded-treatment stress rows must resolve their `linked_artifact` and
  `linked_artifact_key` values against the referenced scenario/policy/sensitivity
  CSVs.
- Semicolon-delimited linked keys must be split and checked token by token.
- The full stress-profile manifest must expose broken runtime hooks and
  unresolved linked artifacts across all stress rows, not only capacity and
  availability rows.
- Publication readiness must include a rail/transit stress-profile gate.
- Final-study rail readiness must not ignore stress-profile `remaining_blockers`
  or integrity counts, even if optimistic manifest booleans are present.

## Edits Made

- `src/realworld/rail_bounded_treatment_audit.py`
  - Added matched-row runtime-hook and linked-artifact integrity checks.
  - Added expected implementation-status checks for capacity and availability
    stress classes.
- `tests/test_realworld_rail_bounded_treatment_audit.py`
  - Added negative tests for missing runtime hooks and unresolved linked keys.
  - Added semicolon-key resolver coverage.
- `src/realworld/rail_transit_stress_profile_packet.py`
  - Added full stress-profile linked-artifact integrity checks.
  - Added `unresolved_linked_artifact_count` to the manifest.
- `tests/test_realworld_rail_transit_stress_profile_packet.py`
  - Added manifest-level broken runtime/link tests.
- `src/realworld/publication_readiness.py`
  - Added rail/transit stress-profile summary and readiness gate.
- `tests/test_realworld_publication_readiness.py`
  - Updated gate counts and added broken stress-profile manifest tests.
- `src/realworld/final_study_readiness.py`
  - Added stress-profile `remaining_blockers`, missing runtime-hook count, and
    unresolved linked-artifact count to the rail gate blocker logic.
- `tests/test_realworld_final_study_readiness.py`
  - Added an optimistic-manifest false-readiness regression test.

## Verification

Passed:

```powershell
.\.venv\Scripts\python -m py_compile src\realworld\final_study_readiness.py src\realworld\publication_readiness.py src\realworld\rail_transit_stress_profile_packet.py src\realworld\rail_bounded_treatment_audit.py
.\.venv\Scripts\python tests\test_realworld_rail_transit_stress_profile_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_bounded_treatment_audit.py
.\.venv\Scripts\python tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
```

Regenerated and passed:

```powershell
.\.venv\Scripts\python scripts\write_rail_transit_stress_profile_packet.py
.\.venv\Scripts\python scripts\audit_rail_bounded_treatments.py
.\.venv\Scripts\python scripts\audit_publication_readiness.py
.\.venv\Scripts\python scripts\write_goal_completion_audit.py
.\.venv\Scripts\python scripts\audit_formal_acceptance_artifacts.py
.\.venv\Scripts\python scripts\validate_formal_acceptance_package.py
```

Observed status after regeneration:

- `data/rail/rail_transit_stress_profile_manifest.json` reports
  `missing_runtime_hook_count=0` and `unresolved_linked_artifact_count=0`.
- `data/rail/rail_bounded_treatment_audit.json` reports `mismatch_count=0`,
  `publication_ready=false`, `can_mark_complete=false`, and
  `can_support_rail_evidence_gate=false`.
- `data/manifests/publication_readiness_audit.json` now has 9 evidence gates:
  1 ready and 8 blocked.
- `data/manifests/current_goal_completion_audit.json` still reports
  `final_study_ready=false`.
- Formal acceptance remains 0/12 ready with no placeholder/template artifacts in
  formal paths.

## Remaining Blockers

- Stress-profile integrity is now checked, but it remains review support only.
- Reviewed GTFS/timetable/shortest-path timing evidence is still absent.
- Rail capacity and availability source decisions are still pending human
  review.
- Road, parameter, provenance, validation, sensitivity, experiment,
  reproducibility, manuscript, and final-audit gates remain blocked.
