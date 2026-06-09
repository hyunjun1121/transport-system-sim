# Phase 11 Reader-Facing Claim-Boundary Sprint

Date: 2026-06-04

## Objective

Continue the `plan.md` workflow by reducing reader-facing and generated
claim-language blockers without changing the project claim boundary. This sprint
does not close publication, reproducibility, formal human-review, study
closeout, or operational-use gates.

## Scope

Main edited paths:

- `README.md`
- `status.md`
- `agents.md`
- `plan.md`
- `src/realworld/tracked_artifact_audit.py`
- `tests/test_realworld_tracked_artifact_audit.py`

Regenerated evidence:

- `docs/tracked_artifact_audit.md`
- `data/validation/tracked_artifact_audit.csv`
- `data/validation/tracked_artifact_audit_manifest.json`
- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `docs/claim_language_guard.md`
- `data/validation/dirty_worktree_classification.csv`
- `data/validation/dirty_worktree_classification_manifest.json`
- `docs/dirty_worktree_classification.md`

## Sub-Agent Inputs

Read-only GPT-5.5 xhigh scout `019e8e98-bb3c-7200-8634-f9931b843cfc`
inspected `README.md`, `status.md`, and the claim-language guard CSV. It
recommended same-clause non-approval wording for the audit snapshot and
consultation follow-up sections.

Read-only GPT-5.5 xhigh scout `019e8e98-fdb7-7523-bc0b-bdcc04e4b912`
inspected `agents.md`, `plan.md`, and the claim-language guard CSV. It
recommended replacing acceptance/final language in the active instructions with
human-review, closeout, and sign-off wording while preserving fail-closed
semantics.

## Implementation

- Reworded `README.md` top-level audit and consultation text so package and
  formal-review statements are explicitly non-approval.
- Reworded `status.md` current audit snapshot so ready/gate counts remain
  status values, not approval claims.
- Reworded the `agents.md` audit snapshot and review-packet paragraph to use
  scaffold-level checks, human-review closure, and study sign-off wording.
- Added an explicit literal-listing boundary before the `agents.md` repository
  structure map.
- Reworded selected `plan.md` sections from acceptance/final/validated language
  toward human-review gates, closeout audit, release-candidate artifacts, and
  benchmark checks.
- Changed `tracked_artifact_audit` generated required actions from accepted
  reproduction scope to reviewer-bounded reproduction scope.
- Added a regression assertion that generated tracked-artifact audit Markdown no
  longer emits `accepted reproduction scope`.

## Command Evidence

Before this sprint:

- overall claim-language blockers: `1810`
- `status.md`: `148`
- `README.md`: `141`
- `agents.md`: `131`
- `plan.md`: `51`
- `docs/tracked_artifact_audit.md`: `130`

Commands run:

| Command | Exit | Result |
| --- | ---: | --- |
| `.\.venv\Scripts\python .\tests\test_realworld_tracked_artifact_audit.py` | 0 | Tracked artifact audit tests passed. |
| `.\.venv\Scripts\python .\scripts\audit_tracked_artifacts.py` | 0 | Tracked artifact audit artifacts regenerated. |
| `.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py` | 0 | Eleven claim guard tests passed. |
| `.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path README.md --scan-path status.md --scan-path agents.md --scan-path plan.md --output .tmp_claim_language_rootdocs.csv --manifest .tmp_claim_language_rootdocs.json --doc .tmp_claim_language_rootdocs.md` | 0 | Temporary root-doc scan reported 422 blockers; temporary files were removed after inspection. |
| `.\.venv\Scripts\python .\scripts\audit_claim_language.py` | 0 | Full claim-language guard artifacts regenerated. |
| `.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py` | 0 | Plan artifact audit unit test passed. |
| `git diff --check -- README.md status.md agents.md plan.md src\realworld\tracked_artifact_audit.py tests\test_realworld_tracked_artifact_audit.py` | 0 | No whitespace errors; PowerShell reported only CRLF warnings. |
| `.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py` | 0 | Dirty paths classified with zero unclassified paths. |
| `.\.venv\Scripts\python .\scripts\audit_plan_artifacts.py` | 1 | Expected fail-closed result because source, parameter, road, rail, artifact-invalidation, reproducibility, and formal human-review gates remain blocked. |

After this sprint:

- overall claim-language blockers: `1634`
- `status.md`: `139`
- `README.md`: `133`
- `agents.md`: `121`
- `plan.md`: `29`
- `docs/tracked_artifact_audit.md`: `0`

## Gate Impact

- Overall claim-language blockers decreased by `176`.
- The tracked-artifact audit no longer emits release-blocking claim-language
  rows.
- Root planning documents still contain reader-facing blocker rows and require
  future claim-boundary cleanup.
- No final-study, publication, formal human-review, reproducibility, calibrated
  forecast, or operational-use gate was closed.

## Next Dependency-Safe Slice

The next highest-value slice is to address `README.md`, `status.md`, and
`agents.md` repository-map/comment blockers. Prefer either precise wording
changes in literal inventory comments or a narrow guard enhancement that covers
repository-tree listings without hiding real prose overclaims.
