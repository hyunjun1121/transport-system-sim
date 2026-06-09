# Phase 11 Formal Review Evidence Matrix Claim-Boundary Sprint - 2026-06-04

## Scope

- Objective: remove release-blocking claim-language findings from the formal
  evidence-matrix artifacts without creating, approving, or closing any formal
  decision record.
- Ownership:
  - `src/realworld/formal_acceptance_evidence_matrix.py`
  - `tests/test_realworld_formal_acceptance_evidence_matrix.py`
  - `data/manifests/formal_acceptance_evidence_matrix.csv`
  - `data/manifests/formal_acceptance_evidence_matrix_manifest.json`
  - `docs/formal_acceptance_evidence_matrix.md`
  - claim-language guard outputs
  - dirty-worktree classification outputs
- Out of scope:
  - formal acceptance artifact creation
  - source-backed reviewer signoff
  - final-study, publication, or Phase 12 closure

## Inspected Evidence

- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `src/realworld/formal_acceptance_evidence_matrix.py`
- `scripts/write_formal_acceptance_evidence_matrix.py`
- `tests/test_realworld_formal_acceptance_evidence_matrix.py`
- `docs/formal_acceptance_evidence_matrix.md`
- `data/manifests/formal_acceptance_evidence_matrix_manifest.json`

## Edits

- Changed the user-facing title from `Formal Acceptance Evidence Matrix` to
  `Formal Review Evidence Matrix`.
- Changed the claim boundary from `Formal acceptance evidence matrix only` to
  `Formal review evidence matrix only`.
- Changed `validation commands` / `Validation` user-facing language to
  `check commands` / `Check Commands`.
- Updated the focused unit test expectation to the new user-facing title.
- Regenerated CSV, JSON manifest, and Markdown outputs through
  `scripts/write_formal_acceptance_evidence_matrix.py`.

## Verification Commands

```powershell
.\.venv\Scripts\python -m py_compile .\src\realworld\formal_acceptance_evidence_matrix.py .\scripts\write_formal_acceptance_evidence_matrix.py .\tests\test_realworld_formal_acceptance_evidence_matrix.py
.\.venv\Scripts\python .\scripts\write_formal_acceptance_evidence_matrix.py
.\.venv\Scripts\python .\tests\test_realworld_formal_acceptance_evidence_matrix.py
.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\docs\formal_acceptance_evidence_matrix.md --scan-path .\data\manifests\formal_acceptance_evidence_matrix_manifest.json --output .\data\validation\tmp_claim_language_guard_formal_matrix.csv --manifest .\data\validation\tmp_claim_language_guard_formal_matrix_manifest.json --doc .\docs\tmp_claim_language_guard_formal_matrix.md
Remove-Item -LiteralPath .\data\validation\tmp_claim_language_guard_formal_matrix.csv, .\data\validation\tmp_claim_language_guard_formal_matrix_manifest.json, .\docs\tmp_claim_language_guard_formal_matrix.md
.\.venv\Scripts\python .\scripts\audit_claim_language.py
.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py
.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py
.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py
```

## Results

- Python compile checks passed.
- Formal evidence-matrix writer completed and regenerated the matrix artifacts.
- Formal evidence-matrix tests passed.
- Focused claim-language guard for the matrix artifacts:
  - final focused blocker count: `0`
  - `claim_language_guard_ready=true`
  - `release_blocked=false`
- Full claim-language guard:
  - before this sprint: `blocking_finding_count=87`
  - after this sprint: `blocking_finding_count=84`
  - `claim_language_guard_ready=false`
  - `release_blocked=true`
- Claim-language guard tests passed.
- Dirty worktree classification before this ledger was added:
  - `classified_path_count=537`
  - `unclassified_path_count=0`
- Plan artifact audit test passed.
- Temporary focused-guard files were removed.

## Residual Risks

- The edits are claim-boundary wording only.
- No formal target path was created, approved, or closed.
- Full claim-language guard still has 84 release-blocking findings.
- Formal acceptance remains blocked until source-backed human review artifacts
  exist and project-owned audits verify them.
