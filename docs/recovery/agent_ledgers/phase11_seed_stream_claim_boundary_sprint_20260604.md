# Phase 11 Seed-Stream Claim-Boundary Sprint - 2026-06-04

## Scope

- Objective: reduce release-blocking claim-language findings in the seed-stream manifest without changing CRN, seed, or experiment-review semantics.
- Ownership:
  - `src/realworld/seed_stream_manifest.py`
  - `data/manifests/seed_stream_manifest.json`
  - `docs/seed_stream_manifest.md`
  - claim-language guard outputs
  - dirty-worktree classification outputs
- Out of scope:
  - CRN pairing approval
  - replication adequacy approval
  - experiment acceptance
  - publication-readiness or study-closeout signoff

## Inspected Evidence

- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `src/realworld/seed_stream_manifest.py`
- `scripts/write_seed_stream_manifest.py`
- `tests/test_realworld_seed_stream_manifest.py`
- `docs/seed_stream_manifest.md`
- `data/manifests/seed_stream_manifest.json`

## Edits

- Reworded seed-stream review actions:
  - `Review demand sampling implementation before accepting CRN design.` -> `Review demand sampling implementation before CRN design signoff.`
  - `Review disruption sampling implementation before accepting CRN design.` -> `Review disruption sampling implementation before CRN design signoff.`
- Reworded experiment-use wording:
  - `before experiment acceptance` -> `before experiment decision review`
  - `before any formal experiment acceptance` -> `before any formal experiment decision review`
- Preserved the manifest's non-approval claim boundary and `acceptance_ready=false`.
- Regenerated seed-stream JSON and Markdown outputs from `scripts/write_seed_stream_manifest.py`.

## Verification Commands

```powershell
.\.venv\Scripts\python -m py_compile .\src\realworld\seed_stream_manifest.py .\scripts\write_seed_stream_manifest.py
.\.venv\Scripts\python .\scripts\write_seed_stream_manifest.py
.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\docs\seed_stream_manifest.md --scan-path .\data\manifests\seed_stream_manifest.json --output .\data\validation\tmp_claim_language_guard_seed_stream.csv --manifest .\data\validation\tmp_claim_language_guard_seed_stream_manifest.json --doc .\docs\tmp_claim_language_guard_seed_stream.md
.\.venv\Scripts\python .\tests\test_realworld_seed_stream_manifest.py
Remove-Item -LiteralPath .\data\validation\tmp_claim_language_guard_seed_stream.csv, .\data\validation\tmp_claim_language_guard_seed_stream_manifest.json, .\docs\tmp_claim_language_guard_seed_stream.md
.\.venv\Scripts\python .\scripts\audit_claim_language.py
.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py
.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py
.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py
git diff --check -- .\src\realworld\seed_stream_manifest.py .\data\manifests\seed_stream_manifest.json .\docs\seed_stream_manifest.md .\data\validation\claim_language_guard.csv .\data\validation\claim_language_guard_manifest.json .\docs\claim_language_guard.md
```

## Results

- Focused claim-language guard for seed-stream artifacts:
  - `blocking_finding_count=0`
  - `claim_language_guard_ready=true`
  - `release_blocked=false`
- Full claim-language guard:
  - before this sprint: `blocking_finding_count=97`
  - after this sprint: `blocking_finding_count=91`
  - `claim_language_guard_ready=false`
  - `release_blocked=true`
- Tests:
  - seed-stream manifest tests passed
  - claim-language guard tests passed
  - plan artifact audit test passed after dirty-worktree classification refresh
- Dirty worktree classification before this ledger was added:
  - `classified_path_count=533`
  - `unclassified_path_count=0`
- Dirty worktree classification after this ledger was added:
  - `classified_path_count=534`
  - `unclassified_path_count=0`
- Temporary focused-guard files were removed:
  - `data/validation/tmp_claim_language_guard_seed_stream.csv`
  - `data/validation/tmp_claim_language_guard_seed_stream_manifest.json`
  - `docs/tmp_claim_language_guard_seed_stream.md`
- `git diff --check` reported no whitespace errors for the sprint scope. It reported an LF-to-CRLF warning for `src/realworld/seed_stream_manifest.py`.

## Residual Risks

- The edits are claim-boundary wording only; no evidence gate was closed.
- Full claim-language guard still has 91 release-blocking findings.
- CRN pairing, replication adequacy, experiment acceptance, and formal closeout records remain blocked.
