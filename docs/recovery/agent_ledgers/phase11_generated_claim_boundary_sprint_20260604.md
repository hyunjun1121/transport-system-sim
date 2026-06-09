# Phase 11 Generated Claim-Boundary Sprint

Date: 2026-06-04

## Objective

Reduce false release-blocking claim-language hits in generated acceptance and
pre-review artifacts without weakening the guard for actual overclaims. This
sprint also confirms that `plan.md` now contains the requested multi-agent,
test-heavy, hardware-aware implementation workflow. It does not close
publication, formal acceptance, final-study, or operational-readiness gates.

## Scope

Main changed implementation paths:

- `plan.md`
- `src/realworld/formal_acceptance_pre_review.py`
- `src/realworld/acceptance_orchestration.py`
- `src/realworld/claim_language_guard.py`
- `tests/test_realworld_formal_acceptance_pre_review.py`
- `tests/test_realworld_acceptance_orchestration.py`
- `tests/test_realworld_claim_language_guard.py`

Regenerated or refreshed evidence paths:

- `docs/formal_acceptance_pre_review.md`
- `data/manifests/acceptance_orchestration_manifest.json`
- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `data/validation/dirty_worktree_classification.csv`
- `data/validation/dirty_worktree_classification_manifest.json`
- `docs/dirty_worktree_classification.md`

## Sub-Agent Inputs

Read-only GPT-5.5 xhigh scout `019e8e81-fabf-7782-91d4-aec91eac1c19`
recommended generator-level wording fixes instead of broad guard weakening.
The scout identified repeated false blockers around agent names, final-audit
labels, acceptance-path wording, and copied blocker text.

Read-only GPT-5.5 xhigh scout `019e8e81-b9db-7d00-b529-96994c828aae`
identified the generator owners:

- `docs/formal_acceptance_pre_review.md` comes from
  `src/realworld/formal_acceptance_pre_review.py`.
- `data/manifests/acceptance_orchestration_manifest.json` comes from
  `src/realworld/acceptance_orchestration.py`.

The scout also recommended same-line non-approval prefixes for copied blocker
text and narrower wording such as reviewer decision, permission, target path,
and release claim.

## Main-Thread Decisions

- Accepted generator-level wording changes.
- Accepted a narrow claim guard bug fix for file-extension dots in clauses.
- Accepted same-line boundary prefixes for copied blocker and review notes.
- Rejected broad guard relaxation.
- Kept all formal acceptance and final-study gates fail-closed.

## Implementation

- Reframed formal pre-review output as pre-review and permission language
  rather than approval language.
- Added `Blocked non-approval ...` prefixes to generated missing-evidence,
  risk, and action bullets.
- Removed duplicated missing-evidence rows from formal pre-review residual
  risks.
- Reworded acceptance-orchestration role names and copied source notes to avoid
  accidental claim language.
- Guarded orchestration `remaining_blockers` and `review_items` with
  same-line non-approval prefixes.
- Fixed the claim-language guard clause splitter so a dot in
  `parameter_acceptance.csv` no longer splits the clause before the nearby
  non-approval marker.
- Added guard markers for `blocker`, `blockers`, and `lacks`.
- Added regression tests for file-extension clause splitting and generated
  non-approval boundaries.
- Expanded `plan.md` into the canonical implementation workflow with
  GPT-5.5 xhigh scout/reviewer/builder waves, sequential builder ordering,
  explicit self-refine loops, dirty-tree gates, test ladders, and RTX 3090
  runtime policy.

## Command Evidence

Before this sprint, the claim-language guard reported:

- total blocking findings: `2650`
- `data/manifests/acceptance_orchestration_manifest.json` blockers: `411`
- `docs/formal_acceptance_pre_review.md` blockers: `360`

Commands run after the patch:

| Command | Exit | Result |
| --- | ---: | --- |
| `.\.venv\Scripts\python -m py_compile ...` | 0 | Modified sources and tests compiled. |
| `.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py` | 0 | Eleven guard tests passed. |
| `.\.venv\Scripts\python .\tests\test_realworld_formal_acceptance_pre_review.py` | 0 | Formal pre-review test passed. |
| `.\.venv\Scripts\python .\tests\test_realworld_acceptance_orchestration.py` | 0 | Acceptance orchestration test passed. |
| `.\.venv\Scripts\python .\scripts\write_formal_acceptance_pre_review.py` | 0 | Formal pre-review artifacts regenerated. |
| Python call to `write_acceptance_orchestration_outputs()` | 0 | Acceptance orchestration manifest regenerated with 12 records and 373 remaining blockers. |
| `.\.venv\Scripts\python .\scripts\audit_claim_language.py` | 0 | Claim-language guard artifacts regenerated. |
| `.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py` | 0 | Dirty paths classified with zero unclassified paths. |
| `.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py` | 0 | Plan audit unit test passed after dirty classification refresh. |
| `git diff --check -- ...` | 0 | No whitespace errors; PowerShell reported only CRLF warnings. |
| `.\.venv\Scripts\python .\scripts\audit_plan_artifacts.py` | 1 | Expected fail-closed result because real evidence and acceptance gates remain blocked. |

After regeneration, the claim-language guard reported:

- total blocking findings: `1810`
- bounded findings: `5613`
- explicit non-approval findings: `4955`
- formal evidence-backed findings: `87`
- bounded non-claim references: `571`
- `claim_language_guard_ready=false`

Target-source effect:

- `data/manifests/acceptance_orchestration_manifest.json`: `411` blockers to
  `26` blockers.
- `docs/formal_acceptance_pre_review.md`: `360` blockers to `15` blockers.

## Gate Impact

- Claim-language blocker count decreased by `840` in the current scan.
- The most problematic generated sources now mostly contain bounded
  non-approval wording rather than unbounded claim language.
- `audit_plan_artifacts.py` still exits `1` by design because road, rail,
  parameter, provenance, invalidation, reproducibility, and formal acceptance
  gates remain blocked.
- No final-study, publication, formal-acceptance, calibrated-forecast, or
  operational-readiness claim was created.

## Remaining Work

Next dependency-safe slices should prioritize true reader-facing blockers in:

1. `status.md`
2. `README.md`
3. `agents.md`
4. `docs/tracked_artifact_audit.md`
5. `docs/reproducibility_package.md`

Do not reduce blocker counts by hiding real claims. Use either source-backed
evidence, same-clause non-approval boundaries, or clearer release-blocked
wording.
