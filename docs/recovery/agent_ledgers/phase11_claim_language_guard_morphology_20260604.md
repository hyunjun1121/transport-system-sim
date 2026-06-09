# Phase 11 Claim-Language Guard Morphology Sprint

Date: 2026-06-04

## Objective

Refresh the claim-language guard against the current root docs and implement
only the narrow negative-morphology fix identified during the read-only scout
wave. This sprint does not close publication, formal acceptance, final-study,
or claim-language gates.

## Scope

Changed paths:

- `src/realworld/claim_language_guard.py`
- `tests/test_realworld_claim_language_guard.py`
- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `docs/claim_language_guard.md`
- `data/validation/dirty_worktree_classification.csv`
- `data/validation/dirty_worktree_classification_manifest.json`
- `docs/dirty_worktree_classification.md`

Sub-agent inputs used:

- Read-only scout `019e8e51-1b71-71f1-a22b-000195c13221`: identified that
  reserved regexes matched verb forms such as accept, approve, validate, and
  calibrate, while boundary aliases did not cover the same morphology.
- Read-only scout `019e8e51-8488-7220-8169-076dd13ac104`: identified that many
  current blockers are audit/status language rather than real-world overclaims
  and recommended avoiding manual edits to generated inventories.

Main-thread decision:

- Accepted the narrow morphology fix.
- Rejected broad `only` handling and manual generated-inventory edits.
- Kept the guard fail-closed.

## Implementation

- Expanded reserved term patterns for `validates`, `calibrates`, and
  `approves`.
- Expanded term aliases for accept/approve/validate/calibrate verb forms.
- Added same-clause boundary markers for `without` and `never`.
- Reused `_term_aliases()` for false-field boundary matching.
- Fixed generated Markdown wording so it names the actual statuses
  `explicit_non_approval` and `formal_evidence_backed` instead of the stale
  `bounded_guardrail` label.
- Added a regression test proving verb-form boundary handling while preserving
  the existing clause-splitting safety check.

## Command Evidence

Before the patch, a fresh temporary guard run reported:

- `row_count=6504`
- `blocking_finding_count=3470`
- `explicit_non_approval_count=2816`
- `formal_evidence_backed_count=218`
- `release_blocked=true`

Commands run after the patch:

| Command | Exit | Result |
| --- | ---: | --- |
| `.\.venv\Scripts\python -m py_compile .\src\realworld\claim_language_guard.py .\scripts\audit_claim_language.py .\tests\test_realworld_claim_language_guard.py` | 0 | Syntax check passed. |
| `.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py` | 0 | Five claim-language guard tests passed. |
| `.\.venv\Scripts\python .\scripts\audit_claim_language.py` | 0 | Guard artifacts regenerated. |
| `git diff --check -- src\realworld\claim_language_guard.py tests\test_realworld_claim_language_guard.py scripts\audit_claim_language.py` | 0 | No whitespace errors reported. |
| `.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py` | 0 | Plan audit unit test passed. |
| `.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py` | 0 | Dirty paths classified; no unclassified paths. |
| `.\.venv\Scripts\python .\scripts\audit_plan_artifacts.py` | 1 | Expected fail-closed result because claim-language guard remains blocked. |

After regeneration, the claim-language guard reported:

- `row_count=6537`
- `blocking_finding_count=3171`
- `explicit_non_approval_count=3148`
- `formal_evidence_backed_count=218`
- `release_blocked=true`
- `claim_language_guard_ready=false`

The plan artifact audit summary reported:

- `all_required_artifacts_present=true`
- `claim_language_guard_ready=false`
- `claim_blocking=3171`
- `claim_release_blocked=true`
- `dirty_coverage=true`
- `dirty_unclassified=0`
- `gpu_can_support=true`
- exit code `1`

## Gate Impact

- Claim-language blocker count decreased by 299 in the current scan.
- The guard remains release-blocked.
- No publication, final-study, formal-acceptance, or operational-readiness gate
  was closed.
- The remaining blockers are still mostly generated audit/status wording,
  manifest inventories, and reader-facing reserved terms that need either
  tighter boundary wording or evidence-backed downgrade decisions.

## Next Dependency-Safe Slice

Run a focused read-only scout/synthesis cycle for the remaining top
claim-language blocker sources. Prioritize root reader-facing docs before
generated manifests:

1. `README.md`
2. `agents.md`
3. `status.md`
4. `plan.md`

Do not hand-edit generated audit inventories just to reduce lexical blocker
counts.
