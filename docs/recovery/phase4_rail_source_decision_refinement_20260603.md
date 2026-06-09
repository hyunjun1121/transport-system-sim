# Phase 4 Rail Source Decision Refinement Ledger - 2026-06-03

## Objective

Refine the existing rail source-decision worksheet so each row records the
minimum evidence acquisition path and the allowable sensitivity-only or
claim-exclusion fallback. This is review support only.

## Baseline Status

- Worktree status recorded before edits with `git status --short --branch`.
- Existing rail fetch-readiness rows: 5.
- Existing rail source-decision rows: 5.
- Current rail source-decision manifest reports `publication_ready=false`,
  `can_mark_complete=false`, `rail_source_decision_recorded=false`,
  `rail_service_evidence_gate_closure_candidate_count=0`, and
  `acceptance_gate_closure_candidate_count=0`.

## Read Set

- `plan.md`
- `src/realworld/rail_source_decision_packet.py`
- `src/realworld/rail_fetch_readiness_packet.py`
- `tests/test_realworld_rail_source_decision_packet.py`
- `tests/test_realworld_rail_fetch_readiness_packet.py`
- `data/rail/rail_source_decision_manifest.json`
- `docs/rail_source_decision_packet.md`

## Write Set

- `src/realworld/rail_source_decision_packet.py`
- `tests/test_realworld_rail_source_decision_packet.py`
- regenerated `data/rail/rail_source_decision_packet.csv`
- regenerated `data/rail/rail_source_decision_manifest.json`
- regenerated `docs/rail_source_decision_packet.md`
- this recovery ledger

## Sub-Agent Wave

- GPT-5.5 xhigh rail/transit evidence explorer: read-only.
- GPT-5.5 xhigh acceptance-hygiene adversarial reviewer: read-only.

## Safety Boundary

- Do not create `data/parameters/rail_service_evidence.csv` from this work.
- Do not create any formal acceptance artifact.
- Do not mark rail evidence, publication, final-study, or formal acceptance
  ready.
- Do not move, delete, or clean any directory.

## Verification Plan

Run narrow tests first:

```powershell
.\.venv\Scripts\python tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_fetch_readiness_packet.py
```

Then regenerate the source-decision packet and rerun readiness/audit checks
affected by rail decision metadata:

```powershell
.\.venv\Scripts\python scripts\write_rail_source_decision_packet.py
.\.venv\Scripts\python scripts\audit_publication_readiness.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
.\.venv\Scripts\python tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
```

## Gate Decision

Completed for this refinement step. Expected result remains blocked/non-final.

## Implementation Result

- Extended the existing rail source-decision packet with non-formal
  action-ledger fields:
  - `decision_scope`
  - `decision_choice`
  - `current_artifact_status`
  - `minimum_evidence_to_acquire`
  - `allowed_bounded_fallback`
  - `decision_completion_output`
  - `reviewer`
  - `decision_date`
  - `decision_basis`
  - `artifact_sha256s`
  - `excluded_or_retained_claim_scope`
  - `not_operational_claim_boundary`
  - `acceptance_or_exclusion_rationale`
- Added manifest counts for pending, completed, invalid, incomplete,
  acquisition, exclusion, sensitivity-only, and scenario-only decisions.
- Kept `publication_ready=false`, `can_mark_complete=false`,
  `rail_source_decision_recorded=false`,
  `rail_service_evidence_gate_closure_candidate_count=0`, and
  `acceptance_gate_closure_candidate_count=0`.
- Hardened publication readiness so aggregate `recorded=true` cannot close rail
  source decisions unless every source-decision row is completed.
- Hardened final-study rail readiness so stale fetch-readiness or priority
  blockers cannot be hidden by otherwise-ready rail source-decision aggregates.

## Commands Run

```powershell
.\.venv\Scripts\python -m py_compile src\realworld\rail_source_decision_packet.py src\realworld\publication_readiness.py src\realworld\final_study_readiness.py tests\test_realworld_rail_source_decision_packet.py tests\test_realworld_publication_readiness.py tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python scripts\write_rail_source_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python tests\test_realworld_rail_fetch_readiness_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_evidence_priority_packet.py
.\.venv\Scripts\python tests\test_realworld_ktdb_gtfs_source.py
.\.venv\Scripts\python tests\test_realworld_metro9_capacity_source.py
.\.venv\Scripts\python scripts\audit_rail_evidence.py
.\.venv\Scripts\python scripts\audit_publication_readiness.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
.\.venv\Scripts\python scripts\write_goal_completion_audit.py
.\.venv\Scripts\python tests\test_realworld_goal_completion_audit.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
.\.venv\Scripts\python scripts\validate_formal_acceptance_package.py
.\.venv\Scripts\python tests\test_realworld_formal_acceptance_package.py
```

## Verification Summary

- Rail source-decision tests passed.
- Rail fetch-readiness and evidence-priority tests passed.
- KTDB GTFS and Metro9 capacity source tests passed.
- Publication readiness tests passed.
- Final-study readiness tests passed.
- Goal completion and plan artifact audits passed.
- Formal acceptance package validation still reports 0/12 formal gates ready,
  as expected.

## Source-Context Hash Refinement Addendum

After the source-decision refinement, the KTDB GTFS and Metro9 source-context
extracts were tightened so the review CSVs retain both parsed source metadata
and an auditable raw-file byte hash.

Additional implementation:

- Added `notice_raw_file_sha256` and `list_raw_file_sha256` to
  `data/rail/ktdb_gtfs_source_extract.csv`.
- Added `raw_file_sha256` to
  `data/rail/metro9_capacity_source_extract.csv`.
- Added `audit_ktdb_gtfs_raw_hashes()` and
  `audit_metro9_capacity_raw_hash()` for local raw-file integrity checks.
- Added `src/realworld/source_context_hash_audit.py`,
  `scripts/audit_source_context_hashes.py`, and
  `tests/test_realworld_source_context_hash_audit.py`.
- Wrote `data/manifests/source_context_hash_audit.json` and
  `docs/source_context_hash_audit.md` with per-file recorded/computed SHA256
  checks for the KTDB notice page, KTDB dataset-list page, and Metro9 page.
- Preserved cached raw HTML snapshots; only the review extracts gained
  explicit raw-file hash columns.
- Kept `publication_ready=false` and `can_mark_complete=false` in the audit
  helpers and the aggregate source-context hash audit because source-context
  hash integrity is not a reviewed GTFS feed, rail timing evidence, capacity
  acceptance, provenance acceptance, or rail-service calibration.

Additional commands run:

```powershell
.\.venv\Scripts\python -m py_compile src\realworld\ktdb_gtfs_source.py src\realworld\metro9_capacity_source.py tests\test_realworld_ktdb_gtfs_source.py tests\test_realworld_metro9_capacity_source.py
.\.venv\Scripts\python tests\test_realworld_ktdb_gtfs_source.py
.\.venv\Scripts\python tests\test_realworld_metro9_capacity_source.py
.\.venv\Scripts\python scripts\audit_source_context_hashes.py
.\.venv\Scripts\python tests\test_realworld_source_context_hash_audit.py
.\.venv\Scripts\python tests\test_realworld_rail_timing_request_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_fetch_readiness_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_source_context_cache_request_packet.py
.\.venv\Scripts\python tests\test_realworld_source_context_cache_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
```

## Remaining Blockers

- `DATA_GO_KR_KEY` and reviewed API payloads are still absent for timetable and
  shortest-path timing rows.
- Reviewed static GTFS feed and GTFS Validator report are still absent.
- Capacity and availability rows still require human/source-backed decisions or
  explicit sensitivity-only/scenario-only/exclusion treatment.
- No formal rail, parameter, provenance, publication, final-study, or formal
  acceptance gate was closed by this refinement.
