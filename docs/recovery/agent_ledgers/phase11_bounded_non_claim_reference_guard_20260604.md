# Phase 11 Bounded Non-Claim Reference Guard Sprint

Date: 2026-06-04

## Objective

Reduce lexical false positives from literal file paths, module names, command
inventories, and guard vocabulary lists without weakening the claim-language
guard. This sprint does not close publication, formal acceptance, final-study,
or claim-language gates.

## Scope

Changed implementation and test paths:

- `src/realworld/claim_language_guard.py`
- `tests/test_realworld_claim_language_guard.py`

Regenerated guard and worktree outputs:

- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `docs/claim_language_guard.md`
- `data/validation/dirty_worktree_classification.csv`
- `data/validation/dirty_worktree_classification_manifest.json`
- `docs/dirty_worktree_classification.md`

## Sub-Agent Evidence

Two GPT-5.5 xhigh read-only scouts were used:

- `019e8e70-a2b9-7972-9e01-164ac9290c88`: inspected root inventories and the
  guard implementation. Recommendation: add a narrow span-aware rule that
  bounds only the reserved term inside structural references such as fenced
  repo trees, paths, filenames, module names, and table path cells. Do not
  exempt the whole line.
- `019e8e70-f3f7-7131-9944-608e1d06da3b`: inspected status/plan examples and
  guard behavior. Recommendation: bound literal paths, guard vocabulary, and
  false status fields only when the specific span is non-claim-bearing; keep
  same-line prose overclaims blocked.

Main-thread decision:

- Accepted the narrow span-aware literal-reference strategy.
- Rejected broad line-level clearance and backtick laundering.
- Ordered explicit non-approval before formal-evidence context so negative
  status fields remain fail-closed and cannot be reinterpreted as approval.

## Implementation

- Added `bounded_non_claim_reference` as a non-release-supporting status.
- Added span tracking for reserved-term matches on each scanned line.
- Added fenced-code, backtick, path, filename, module-name, table-cell, and
  guard-vocabulary reference detection.
- Kept classification at term-span granularity so a literal path can be
  bounded while a neighboring same-line phrase such as `operational` or
  `approved` remains `release_blocking_unbounded`.
- Limited false-field handling to the same physical line so
  `final_study_ready=false` does not clear a later
  `final_study_ready=true` line.
- Added regression tests for literal references, mixed identifier/prose
  overclaims, false status fields, neighboring context, and non-approval
  precedence.

## Command Evidence

Before this bounded-reference slice, after the root-doc prose sprint, the guard
reported:

- `row_count=6520`
- `blocking_finding_count=3147`
- `explicit_non_approval_count=3155`
- `formal_evidence_backed_count=218`
- `release_blocked=true`

Commands run:

| Command | Exit | Result |
| --- | ---: | --- |
| `.\.venv\Scripts\python -m py_compile .\src\realworld\claim_language_guard.py .\tests\test_realworld_claim_language_guard.py` | 0 | Syntax check passed. |
| `.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py` | 0 | Ten claim-language guard tests passed. |
| `.\.venv\Scripts\python .\scripts\audit_claim_language.py` | 0 | Guard artifacts regenerated. |
| `.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py` | 0 | Plan audit unit test passed. |
| `.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py` | 0 | Dirty paths classified; `unclassified_path_count=0`. |
| `.\.venv\Scripts\python .\scripts\audit_plan_artifacts.py` | 1 | Expected fail-closed result because claim-language and formal evidence gates remain blocked. |

After regeneration, the guard reported:

- `row_count=6738`
- `blocking_finding_count=2650`
- `explicit_non_approval_count=3378`
- `formal_evidence_backed_count=99`
- `bounded_non_claim_reference_count=611`
- `release_blocked=true`
- `claim_language_guard_ready=false`

Dirty-worktree classification reported:

- `dirty_path_count=338`
- `classified_path_count=338`
- `unclassified_path_count=0`

The plan artifact audit reported:

- `all_required_artifacts_present=true`
- `claim_language_guard_ready=false`
- `claim_blocking=2650`
- `claim_release_blocked=true`
- exit code `1`

## Gate Impact

- Claim-language blocker count decreased by 497 in this slice.
- Combined with the morphology and root-doc prose sprints, the blocker count is
  820 lower than the fresh pre-sprint baseline of 3,470.
- The guard remains release-blocked.
- No publication, final-study, formal-acceptance, operational-readiness, or
  calibrated-claim gate was closed.

## Remaining Blockers

The remaining claim-language blockers are still dominated by:

- real prose and report/manuscript wording requiring downgrade or evidence
  boundary review;
- generated formal acceptance and review-package inventories that intentionally
  contain reserved terms;
- remaining audit/status manifests whose language needs either generator-level
  adjustment or formal evidence-backed review;
- broader parameter, rail, road, benchmark, and formal acceptance blockers
  reported by `audit_plan_artifacts.py`.

Next dependency-safe slice: prioritize generator-level claim-boundary wording
for the highest-volume generated sources, starting with
`docs/formal_acceptance_pre_review.md` and
`data/manifests/acceptance_orchestration_manifest.json`. Do not hand-edit
generated outputs without updating their owning generator and tests.
