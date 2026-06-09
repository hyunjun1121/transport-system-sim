# Phase 4 Rail Source-Decision Guard Sprint Ledger

Timestamp: 2026-06-03 04:29:26 KST

## Objective

Strengthen Phase 4 rail/transit source-decision guardrails without creating
rail evidence, publication readiness, final-study readiness, or formal
acceptance.

## Baseline Status

Current git status was recorded before new guard edits. The worktree is dirty
from prior Phase 3 and Phase 4 recovery/implementation work. This sprint must
not clean, revert, delete, or move broad directories.

Current readiness evidence:

- `scripts/audit_publication_readiness.py` reported `publication_ready=false`,
  1 ready gate, and 7 blocked gates.
- `scripts/write_goal_completion_audit.py` wrote current goal audit with
  `final_study_ready=False` and 12 blocked gates.
- `scripts/audit_formal_acceptance_artifacts.py` reported 0 formal targets
  present, 12 missing, and 0 template/placeholder artifacts in formal paths.
- `scripts/validate_formal_acceptance_package.py` reported formal acceptance
  0/12 ready and `final_study_ready=false`.

## Agent Wave

Read-only GPT-5.5 xhigh agents launched in parallel:

- GTFS/timetable evidence explorer.
- Capacity/availability bounded-treatment explorer.
- Adversarial false-readiness and acceptance-hygiene reviewer.

All agent tasks are read-only. No agent may edit, move, delete, generate
artifacts, or create acceptance records.

## Main Thread Write Scope

Allowed write scope for this sprint:

- `src/realworld/rail_source_decision_packet.py`
- `tests/test_realworld_rail_source_decision_packet.py`
- `docs/rail_source_decision_packet.md`
- `docs/rail_source_decision_action_ledger_template.md`
- `data/rail/rail_source_decision_packet.csv`
- `data/rail/rail_source_decision_manifest.json`
- `data/rail/rail_source_decision_action_ledger_template.csv`
- `data/rail/rail_source_decision_action_ledger_template_manifest.json`
- this ledger file
- `plan.md` and `status.md` only if the guard outcome changes documented
  workflow/status language.

Forbidden write scope:

- formal acceptance targets;
- broad cleanup, deletion, or directory moves;
- full experiment outputs;
- unrelated contest or web-demo folders;
- road evidence code except through a separately authorized sprint.

## Candidate Guard Target

Local inspection found that source-backed acquisition rows already require local
source/cache/raw artifacts and matching 64-hex SHA256 values. A remaining
review-hygiene risk is that non-formal source decisions can use arbitrary
`decision_date` text. This sprint may add a small validation guard requiring
ISO `YYYY-MM-DD` decision dates for non-pending action decisions.

## Required Tests

Narrow tests:

```powershell
.\.venv\Scripts\python tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
```

Generated-output commands if writer behavior changes:

```powershell
.\.venv\Scripts\python scripts\write_rail_source_decision_action_ledger_template.py
.\.venv\Scripts\python scripts\write_rail_source_decision_packet.py
```

Readiness/audit commands:

```powershell
.\.venv\Scripts\python scripts\audit_publication_readiness.py
.\.venv\Scripts\python scripts\write_goal_completion_audit.py
.\.venv\Scripts\python scripts\audit_formal_acceptance_artifacts.py
.\.venv\Scripts\python scripts\validate_formal_acceptance_package.py
```

## Gate Rule

Proceed only if the guard keeps source decisions non-formal, keeps readiness
blocked where evidence is absent, and does not create formal acceptance
artifacts.

## Agent Findings Integrated

- GTFS/timetable evidence explorer confirmed that current rail service evidence
  is still proxy/scaffold evidence. Reviewed GTFS, timetable, shortest-path
  cache payloads, and GTFS Validator evidence remain absent.
- Capacity/availability bounded-treatment explorer confirmed that stress
  profiles and bounded fallback rows are review support only. A zero mismatch
  bounded-treatment audit must not be treated as rail capacity or availability
  evidence.
- Adversarial false-readiness reviewer identified a final-study gate risk:
  completed non-formal rail source-decision rows could be overread unless the
  rail source-decision manifest's own `publication_ready` and
  `can_mark_complete` flags remain part of the gate check. The same risk applies
  to rail/transit stress-profile support flags.

## Edits Made

- Added ISO `YYYY-MM-DD` date validation for non-pending rail source-decision
  action ledger rows. Invalid dates now classify the row as
  `invalid_action_decision_date` and count as missing decision evidence.
- Strengthened the final-study rail gate so rail source decisions are not ready
  unless the manifest is recorded, complete, free of blocking/human-review rows,
  `publication_ready=true`, and `can_mark_complete=true`.
- Strengthened the final-study rail gate so rail/transit stress profiles must
  explicitly support the rail evidence gate. Mere coverage documentation is not
  enough.
- Regenerated rail source-decision and rail/transit stress-profile review
  artifacts. No formal acceptance artifacts were created.

## Verification Results

Passed targeted tests:

```powershell
.\.venv\Scripts\python tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
.\.venv\Scripts\python tests\test_realworld_rail_transit_stress_profile_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_bounded_treatment_audit.py
.\.venv\Scripts\python tests\test_realworld_rail_source_decision_action_ledger_template.py
```

Passed generation and readiness/audit commands:

```powershell
.\.venv\Scripts\python scripts\write_rail_source_decision_action_ledger_template.py
.\.venv\Scripts\python scripts\write_rail_source_decision_packet.py
.\.venv\Scripts\python scripts\write_rail_transit_stress_profile_packet.py
.\.venv\Scripts\python scripts\audit_rail_bounded_treatments.py
.\.venv\Scripts\python scripts\audit_publication_readiness.py
.\.venv\Scripts\python scripts\write_goal_completion_audit.py
.\.venv\Scripts\python scripts\audit_formal_acceptance_artifacts.py
.\.venv\Scripts\python scripts\validate_formal_acceptance_package.py
```

Observed post-check status:

- `publication_ready=false`.
- `final_study_ready=false`.
- Final-study readiness remains 3/15 ready and 12 blocked.
- Formal acceptance remains 0/12 ready.
- Formal target paths remain absent, with 0 template/placeholder artifacts in
  formal paths.

## Remaining Blockers

- Acquire reviewed GTFS/timetable/shortest-path rail timing evidence, or record
  an explicit exclusion/sensitivity-only decision with appropriate claim
  limits.
- Resolve rail capacity and availability as source-backed evidence,
  sensitivity-only/scenario-only bounded assumptions, or exclusions.
- Close upstream parameter, road, provenance, validation, sensitivity,
  experiment, manuscript, reproducibility, and final-audit gates before any
  final-study acceptance claim.
