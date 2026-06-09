# Phase 4 Agent Ledger: Rail Bounded Treatment Audit

## Phase

Phase 4 rail/transit evidence continuation.

## Objective

Assess and, if supported by current files, implement one bounded improvement
that cross-checks rail capacity and rail availability source-decision rows
against rail/transit stress-profile coverage. The improvement must remain a
review aid only. It must not create rail evidence, capacity acceptance,
availability acceptance, operational rail-service claims, publication readiness,
final-study readiness, or formal acceptance artifacts.

## Baseline Status

Baseline command recorded before this phase:

```powershell
git status --short --branch
```

The worktree is dirty. This ledger treats the existing dirty state as
pre-existing phase/recovery work and forbids broad cleanup, directory moves,
recursive deletion, or reverting user/other-worker edits.

Relevant current-state observations already inspected for this ledger:

- `plan.md` Immediate Next Actions require continuing Phase 4 by acquiring or
  excluding real rail/transit evidence, with explicit capacity and availability
  source decisions.
- `data/rail/rail_source_decision_manifest.json` currently reports
  `row_count=5`, `publication_ready=false`, `can_mark_complete=false`,
  `rail_source_decision_recorded=false`, `completed_source_decision_count=0`,
  and remaining blockers for timetable, shortest-path, GTFS, capacity, and
  availability.
- `data/rail/rail_transit_stress_profile_manifest.json` currently reports
  `row_count=6`, `required_stress_classes_present=true`,
  `publication_ready=false`, `can_support_rail_evidence_gate=false`, and
  blockers that capacity and availability profiles still require reviewer
  decisions before final claims.

## Dirty-Worktree Inventory

Classification rule:

- `owned-by-current-phase`: paths this phase may touch after main-thread
  synthesis grants a write lock.
- `owned-by-other-worker`: dirty paths not assigned to this phase.
- `generated-output`: generated packets, manifests, docs, caches, or audit
  outputs from prior phases.
- `unknown`: dirty paths whose owner is not established; builders must not
  touch them without a new main-thread decision.

Current phase may inspect all dirty paths but may edit only explicitly locked
paths after the explorer wave.

Known current-phase candidate paths, not yet locked:

- `src/realworld/rail_bounded_treatment_audit.py`
- `scripts/audit_rail_bounded_treatments.py`
- `tests/test_realworld_rail_bounded_treatment_audit.py`
- `data/rail/rail_bounded_treatment_audit.json`
- `docs/rail_bounded_treatment_audit.md`
- this ledger

Pre-existing generated-output or prior phase paths observed in `git status`:

- `data/manifests/current_goal_completion_audit.json`
- `data/manifests/pilot_experiment_design.json`
- `data/manifests/publication_readiness_audit.json`
- `data/manifests/source_context_hash_audit.json`
- `data/parameters/road_attribute_evidence_manifest.json`
- `data/parameters/road_attribute_evidence_table.csv`
- `data/rail/ktdb_gtfs_source_extract.csv`
- `data/rail/metro9_capacity_source_extract.csv`
- `data/rail/rail_evidence_priority_packet.csv`
- `data/rail/rail_fetch_readiness_packet.csv`
- `data/rail/rail_source_decision_manifest.json`
- `data/rail/rail_source_decision_packet.csv`
- `data/rail/rail_timing_source_request_packet.csv`
- `data/rail/rail_transit_stress_profile_manifest.json`
- `data/rail/rail_transit_stress_profile_packet.csv`
- `docs/current_goal_completion_audit.md`
- `docs/publication_readiness_audit.md`
- `docs/rail_evidence_priority_packet.md`
- `docs/rail_fetch_readiness_packet.md`
- `docs/rail_source_decision_packet.md`
- `docs/rail_transit_stress_profile_packet.md`
- `docs/road_attribute_evidence.md`
- `docs/source_context_hash_audit.md`
- `docs/recovery/phase*_20260602.md`
- `docs/recovery/phase4_rail_source_decision_refinement_20260603.md`

Pre-existing source/test/doc paths not assigned to this phase unless a later
write lock explicitly adds them:

- `agents.md`
- `plan.md`
- `status.md`
- `data/regions/pilot_region.yaml`
- `scripts/derive_rail_gtfs_evidence.py`
- `scripts/audit_source_context_hashes.py`
- `scripts/write_rail_transit_stress_profile_packet.py`
- `scripts/write_road_attribute_evidence.py`
- `scripts/write_road_snapshot.py`
- `src/realworld/*` except the candidate audit module named above
- `tests/test_realworld_*` except the candidate audit test named above

## Read Set

Read-only sub-agents may inspect:

- `plan.md`
- `agents.md`
- `src/realworld/rail_source_decision_packet.py`
- `src/realworld/rail_transit_stress_profile_packet.py`
- `src/realworld/publication_readiness.py`
- `src/realworld/final_study_readiness.py`
- `tests/test_realworld_rail_source_decision_packet.py`
- `tests/test_realworld_rail_transit_stress_profile_packet.py`
- `tests/test_realworld_publication_readiness.py`
- `tests/test_realworld_final_study_readiness.py`
- `data/rail/rail_source_decision_packet.csv`
- `data/rail/rail_source_decision_manifest.json`
- `data/rail/rail_transit_stress_profile_packet.csv`
- `data/rail/rail_transit_stress_profile_manifest.json`
- `docs/rail_source_decision_packet.md`
- `docs/rail_transit_stress_profile_packet.md`
- relevant `rg` searches for capacity, availability, scenario-only,
  sensitivity-only, and stress-profile terms.

## Expected Write Set

No write lock is granted to sub-agents in Wave 1.

Tentative main-thread implementation write set after synthesis:

- `src/realworld/rail_bounded_treatment_audit.py`
- `scripts/audit_rail_bounded_treatments.py`
- `tests/test_realworld_rail_bounded_treatment_audit.py`
- `data/rail/rail_bounded_treatment_audit.json`
- `docs/rail_bounded_treatment_audit.md`
- optional: append a short note to
  `docs/recovery/phase4_rail_source_decision_refinement_20260603.md`
- optional: update `plan.md` Immediate Next Actions only if the audit is
  implemented and verified.

## Forbidden Paths

- No formal acceptance targets.
- No broad directory cleanup.
- No recursive deletion.
- No move/rename of project folders.
- No edit to `data/parameters/rail_service_evidence.csv` unless a separate
  reviewed evidence-acquisition phase authorizes it.
- No change that turns `publication_ready`, `can_mark_complete`,
  `can_support_rail_evidence_gate`, or `can_support_acceptance_gate` true.

## Agents

Wave 1 read-only agents, all GPT-5.5 xhigh:

- Agent A: rail capacity bounded-treatment explorer.
  - Scope: capacity rows, source-decision packet, Metro9 capacity context, and
    stress-profile capacity coverage.
  - Write lock: none.
  - Start condition: this ledger exists.
- Agent B: rail availability bounded-treatment explorer.
  - Scope: availability rows, disruption/stress scenario coverage, and
    no-operational-availability claim boundary.
  - Write lock: none.
  - Start condition: this ledger exists.
- Agent C: adversarial audit reviewer.
  - Scope: false realism, false acceptance, hidden operational rail claims, and
    whether a bounded-treatment audit would add defensible value.
  - Write lock: none.
  - Start condition: this ledger exists.

## Dependencies

Wave 1 agents are parallel read-only. Main thread must synthesize the findings
before any implementation. If agents disagree, the stricter evidence boundary
controls.

## Join Condition

Proceed to implementation only if the main thread can identify a bounded audit
that:

1. is traceable to inspected source-decision and stress-profile artifacts;
2. adds a missing consistency check;
3. keeps all acceptance/final readiness flags false;
4. has narrow tests;
5. does not require external credentials or live data.

## Narrow Tests

Potential tests if implemented:

```powershell
.\.venv\Scripts\python -m py_compile src\realworld\rail_bounded_treatment_audit.py scripts\audit_rail_bounded_treatments.py tests\test_realworld_rail_bounded_treatment_audit.py
.\.venv\Scripts\python scripts\audit_rail_bounded_treatments.py
.\.venv\Scripts\python tests\test_realworld_rail_bounded_treatment_audit.py
.\.venv\Scripts\python tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_transit_stress_profile_packet.py
```

## Broad Tests

Run only if readiness logic or generated readiness artifacts are touched:

```powershell
.\.venv\Scripts\python tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
```

## Self-Refine Actions

- Patch blocker/high findings from reviewer wave before broader tests.
- Rerun impacted tests.
- Record finding closure if a reviewer flags overclaim or acceptance hygiene.

## Gate Decision

Wave 1 read-only agent review complete.

Accepted findings:

- The audit should proceed only as a cross-artifact consistency check.
- The audit must map `rail_capacity_treatment_request` to
  `partial_capacity_reduction`.
- The audit must map `rail_availability_scenario_request` to rail
  delay/unavailability, increased-headway, and station-access stress rows
  through the stress-profile packet's linked artifacts, not by assuming
  `data/scenarios/disruption_scenarios.csv` contains all availability stress.
- The audit must keep `publication_ready=false`, `can_mark_complete=false`,
  `can_support_rail_evidence_gate=false`, and
  `can_support_acceptance_gate=false`.
- The audit must not be imported by `publication_readiness.py` or
  `final_study_readiness.py`.

Rejected or unsupported findings:

- None of the agent outputs proves rail capacity evidence, rail availability
  evidence, emergency rail service availability, operational planning, formal
  acceptance, publication readiness, or final-study readiness.

Implementation scope:

- Add a new bounded consistency audit module, script, tests, JSON output, and
  Markdown documentation.

Granted write lock:

- `src/realworld/rail_bounded_treatment_audit.py`
- `scripts/audit_rail_bounded_treatments.py`
- `tests/test_realworld_rail_bounded_treatment_audit.py`
- `data/rail/rail_bounded_treatment_audit.json`
- `docs/rail_bounded_treatment_audit.md`
- this ledger

Forbidden paths remain unchanged, especially formal acceptance targets and
`data/parameters/rail_service_evidence.csv`.

Gate decision: proceed to bounded implementation.

## Implementation Result

Implemented paths:

- `src/realworld/rail_bounded_treatment_audit.py`
- `scripts/audit_rail_bounded_treatments.py`
- `tests/test_realworld_rail_bounded_treatment_audit.py`
- `data/rail/rail_bounded_treatment_audit.json`
- `docs/rail_bounded_treatment_audit.md`

Supporting export/documentation updates:

- `src/realworld/__init__.py`
- `src/realworld/README.md`
- `agents.md`
- `status.md`
- `plan.md`

Current audit output:

- `audit_verdict=bounded_review_support_only`
- `mismatch_count=0`
- `warning_count=4`
- `unchecked_pending_decision_count=2`
- `publication_ready=false`
- `can_mark_complete=false`
- `can_support_rail_evidence_gate=false`
- `can_support_acceptance_gate=false`

This is not evidence acceptance. It only shows that current pending capacity
and availability source-decision rows are internally mapped to existing
stress-profile rows without promoting scenario-only or sensitivity-only
treatments into accepted rail evidence.

## Verification

Commands executed and passed:

```powershell
.\.venv\Scripts\python -m py_compile src\realworld\__init__.py src\realworld\rail_bounded_treatment_audit.py src\realworld\rail_transit_stress_profile_packet.py scripts\audit_rail_bounded_treatments.py tests\test_realworld_rail_bounded_treatment_audit.py
.\.venv\Scripts\python scripts\audit_rail_bounded_treatments.py
.\.venv\Scripts\python tests\test_realworld_rail_bounded_treatment_audit.py
.\.venv\Scripts\python tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_transit_stress_profile_packet.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
```

Public API import check executed and passed:

```powershell
from src.realworld import build_rail_bounded_treatment_audit, build_rail_transit_stress_profile_rows
```

## Remaining Blockers

- Capacity and availability still require reviewer source decisions before
  final claims.
- Stress-profile coverage remains scenario/sensitivity review support only.
- No formal rail evidence, publication readiness, final-study readiness, or
  acceptance gate is closed by this phase.
