# Phase 11 Pilot/Source Docs Claim-Boundary Sprint - 2026-06-04

## Scope

- Objective: reduce release-blocking claim-language findings in two review-support documents without changing gate status or evidence meaning.
- Ownership:
  - `docs/pilot_region_data_card.md`
  - `docs/source_provenance_manifest.md`
  - claim-language guard outputs
  - dirty-worktree classification outputs
- Out of scope:
  - source-provenance acceptance
  - pilot-region acceptance
  - publication-readiness or final-study signoff

## Inspected Evidence

- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `docs/pilot_region_data_card.md`
- `docs/source_provenance_manifest.md`
- `scripts/audit_source_provenance.py`
- `src/realworld/source_provenance.py`
- `tests/test_realworld_source_provenance.py`
- `tests/test_realworld_pilot_acceptance.py`
- `tests/test_realworld_provenance_acceptance.py`

## Edits

- Reworded `docs/pilot_region_data_card.md`:
  - `operational routing instructions` -> `routing instructions for field use`
  - `simulator-ready graph` -> `simulator-compatible graph`
  - `calibrated OSM/Songpa transport model` -> `fit-to-observed-data OSM/Songpa transport model`
  - `operational route plan` -> `field-use route plan`
  - `validation commands` -> `review commands`
- Reworded `docs/source_provenance_manifest.md`:
  - `validation review packet` -> `benchmark review packet`
  - `validation-summary scope evidence` -> `benchmark-summary scope evidence`
  - `before final claims` -> `before release-scope claims`
  - `Final Gate Relationship` -> `Release Gate Relationship`
  - `final data-provenance gate` -> `release-scope data-provenance gate`

## Verification Commands

```powershell
.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\docs\pilot_region_data_card.md --scan-path .\docs\source_provenance_manifest.md --output .\data\validation\tmp_claim_language_guard_pilot_source_docs.csv --manifest .\data\validation\tmp_claim_language_guard_pilot_source_docs_manifest.json --doc .\docs\tmp_claim_language_guard_pilot_source_docs.md
.\.venv\Scripts\python .\tests\test_realworld_source_provenance.py
.\.venv\Scripts\python .\tests\test_realworld_pilot_acceptance.py
.\.venv\Scripts\python .\tests\test_realworld_provenance_acceptance.py
Remove-Item -LiteralPath .\data\validation\tmp_claim_language_guard_pilot_source_docs.csv, .\data\validation\tmp_claim_language_guard_pilot_source_docs_manifest.json, .\docs\tmp_claim_language_guard_pilot_source_docs.md -ErrorAction Stop
.\.venv\Scripts\python .\scripts\audit_claim_language.py
.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py
.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py
.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py
git diff --check -- .\docs\pilot_region_data_card.md .\docs\source_provenance_manifest.md .\data\validation\claim_language_guard.csv .\data\validation\claim_language_guard_manifest.json .\docs\claim_language_guard.md .\data\validation\dirty_worktree_classification.csv .\data\validation\dirty_worktree_classification_manifest.json .\docs\dirty_worktree_classification.md
```

## Results

- Focused claim-language guard for the two docs:
  - `blocking_finding_count=0`
  - `claim_language_guard_ready=true`
  - `release_blocked=false`
- Full claim-language guard:
  - before this sprint: `blocking_finding_count=119`
  - after this sprint: `blocking_finding_count=109`
  - `claim_language_guard_ready=false`
  - `release_blocked=true`
- Tests:
  - source-provenance tests passed
  - pilot-acceptance tests passed
  - provenance-acceptance tests passed
  - claim-language guard tests passed
  - plan artifact audit test passed
- Dirty worktree classification before this ledger was added:
  - `classified_path_count=513`
  - `unclassified_path_count=0`
- Dirty worktree classification after this ledger was added:
  - `classified_path_count=514`
  - `unclassified_path_count=0`
- Temporary focused-guard files were removed:
  - `data/validation/tmp_claim_language_guard_pilot_source_docs.csv`
  - `data/validation/tmp_claim_language_guard_pilot_source_docs_manifest.json`
  - `docs/tmp_claim_language_guard_pilot_source_docs.md`
- `git diff --check` reported no whitespace errors for the sprint scope. It reported LF-to-CRLF warnings for the two edited Markdown files.

## Residual Risks

- The edits are claim-boundary wording only; no evidence gate was closed.
- Full claim-language guard still has 109 release-blocking findings.
- The pilot data card and source-provenance manifest remain review-support artifacts only.
