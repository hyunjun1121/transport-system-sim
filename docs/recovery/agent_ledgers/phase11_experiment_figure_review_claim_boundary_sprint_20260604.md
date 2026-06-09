# Phase 11 Experiment/Figure Review Claim-Boundary Sprint - 2026-06-04

## Scope

- Objective: reduce release-blocking claim-language findings in generated experiment-package and figure/table review artifacts without changing their non-approval semantics.
- Ownership:
  - `src/realworld/experiment_package_review_packet.py`
  - `src/realworld/figure_table_review_packet.py`
  - `tests/test_realworld_figure_table_review_packet.py`
  - generated experiment-package and figure/table review CSV/JSON/Markdown outputs
  - claim-language guard outputs
- Out of scope:
  - formal acceptance record creation
  - evidence-gate closure
  - publication-readiness or final-study signoff

## Inspected Evidence

- `plan.md`, Immediate Next Actions: current sprint candidate is claim-language guard refresh and narrow wording fixes, while avoiding manual generated-inventory edits merely to reduce blocker counts.
- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `src/realworld/experiment_package_review_packet.py`
- `src/realworld/figure_table_review_packet.py`
- `scripts/write_experiment_package_review_packet.py`
- `scripts/write_figure_table_review_packet.py`
- `tests/test_realworld_experiment_package_review_packet.py`
- `tests/test_realworld_figure_table_review_packet.py`

## Edits

- Reworded experiment-package review strings from approval-like terms to bounded decision-review terms:
  - `accepted graph/input scope` -> `reviewer-selected graph/input scope`
  - `accepted run profile` -> `review-selected run profile`
  - `final acceptance record` -> `experiment decision record`
  - `input validation` -> `input checks`
  - `accepted before using full outputs` -> `before using full outputs`
- Reworded figure/table review strings from approval-like terms to bounded decision-review terms:
  - `validated and accepted` -> `benchmark-reviewed and decision-reviewed`
  - `final manuscript claims` -> `release-scope manuscript claims`
  - `manuscript acceptance` in claim-bearing review text -> `manuscript decision`
  - `validation dependencies` -> `benchmark dependencies`
- Updated the figure/table test assertion to match the revised non-approval boundary phrase.

## Regenerated Artifacts

- `data/manifests/experiment_package_review_packet.csv`
- `data/manifests/experiment_package_review_manifest.json`
- `docs/experiment_package_review_packet.md`
- `data/manifests/figure_table_review_packet.csv`
- `data/manifests/figure_table_review_manifest.json`
- `docs/figure_table_review_packet.md`
- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `docs/claim_language_guard.md`

## Verification Commands

```powershell
.\.venv\Scripts\python -m py_compile .\src\realworld\experiment_package_review_packet.py .\src\realworld\figure_table_review_packet.py .\scripts\write_experiment_package_review_packet.py .\scripts\write_figure_table_review_packet.py
.\.venv\Scripts\python .\scripts\write_experiment_package_review_packet.py
.\.venv\Scripts\python .\scripts\write_figure_table_review_packet.py
.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\docs\experiment_package_review_packet.md --scan-path .\data\manifests\experiment_package_review_manifest.json --scan-path .\docs\figure_table_review_packet.md --scan-path .\data\manifests\figure_table_review_manifest.json --output .\data\validation\tmp_claim_language_guard_experiment_figure.csv --manifest .\data\validation\tmp_claim_language_guard_experiment_figure_manifest.json --doc .\docs\tmp_claim_language_guard_experiment_figure.md
.\.venv\Scripts\python .\tests\test_realworld_experiment_package_review_packet.py
.\.venv\Scripts\python .\tests\test_realworld_figure_table_review_packet.py
Remove-Item -LiteralPath .\data\validation\tmp_claim_language_guard_experiment_figure.csv, .\data\validation\tmp_claim_language_guard_experiment_figure_manifest.json, .\docs\tmp_claim_language_guard_experiment_figure.md -ErrorAction Stop
.\.venv\Scripts\python .\scripts\audit_claim_language.py
.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py
.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py
.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py
git diff --check -- .\src\realworld\experiment_package_review_packet.py .\src\realworld\figure_table_review_packet.py .\tests\test_realworld_figure_table_review_packet.py .\data\manifests\experiment_package_review_packet.csv .\data\manifests\experiment_package_review_manifest.json .\docs\experiment_package_review_packet.md .\data\manifests\figure_table_review_packet.csv .\data\manifests\figure_table_review_manifest.json .\docs\figure_table_review_packet.md .\data\validation\claim_language_guard.csv .\data\validation\claim_language_guard_manifest.json .\docs\claim_language_guard.md .\data\validation\dirty_worktree_classification.csv .\data\validation\dirty_worktree_classification_manifest.json .\docs\dirty_worktree_classification.md
```

## Results

- Focused claim-language guard for the four generated experiment/figure review outputs:
  - `blocking_finding_count=0`
  - `claim_language_guard_ready=true`
  - `release_blocked=false`
- Full claim-language guard:
  - before sprint: `blocking_finding_count=133`
  - after sprint: `blocking_finding_count=119`
  - `claim_language_guard_ready=false`
  - `release_blocked=true`
- Tests:
  - experiment-package review packet test passed
  - figure/table review packet test passed
  - claim-language guard test passed
  - plan artifact audit test passed
- Dirty worktree classification before this ledger was added:
  - `classified_path_count=510`
  - `unclassified_path_count=0`
- Dirty worktree classification after this ledger was added:
  - `classified_path_count=511`
  - `unclassified_path_count=0`
- Temporary focused-guard files were removed:
  - `data/validation/tmp_claim_language_guard_experiment_figure.csv`
  - `data/validation/tmp_claim_language_guard_experiment_figure_manifest.json`
  - `docs/tmp_claim_language_guard_experiment_figure.md`
- `git diff --check` reported no whitespace errors for the sprint scope. It reported LF-to-CRLF warnings for the changed Python/test files.

## Residual Risks

- This sprint does not close publication, manuscript, experiment, or formal acceptance gates.
- Full claim-language guard still has 119 release-blocking findings.
- The regenerated packets remain review-support artifacts only.
- The broader dirty worktree remains large and classified for safety, not clean.
