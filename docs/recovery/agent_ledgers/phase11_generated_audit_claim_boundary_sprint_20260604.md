# Phase 11 Generated Audit Claim Boundary Sprint - 2026-06-04

## Scope

This sprint reduced release-blocking lexical claim-language findings caused by
generated audit artifacts and their writers. It changed claim-boundary wording
and guard classification only; it did not change simulation code, experiment
outputs, gate truth, formal review status, or formal acceptance status.

No study-closeout, publication, reproducibility, calibration, deployment,
artifact-promotion, or formal human-review gate was closed.

## Sub-Agent Review

Two GPT-5.5 xhigh read-only scouts were used.

| Agent | Scope | Key Finding |
| --- | --- | --- |
| `019e8f08-3176-7222-9fc0-58fbb025c08b` | `src/realworld/publication_readiness.py`, publication audit outputs, tests, claim guard | Publication audit blockers came from generated Markdown labels and raw `remaining_blockers` inventory text, not from a gate becoming true. |
| `019e8f08-7243-7f02-9c15-dcf344f6eee5` | `src/realworld/goal_completion_audit.py`, current goal audit outputs, tests, claim guard | Goal-completion blockers came from copied blocker inventory rows, true-but-scaffold status labels, headings, and source claim-boundary prose. |

Both agents were read-only. Both were closed after their findings were
integrated.

## Changes

Claim-language guard behavior was refined in
`src/realworld/claim_language_guard.py`:

- JSON arrays named `remaining_blockers`, `missing_or_weak_requirements`, and
  `proxy_signals_rejected` are treated as explicit non-approval inventory.
- Markdown sections titled `Remaining Blockers`, `Missing Or Weak Requirement`,
  or `Proxy Signals Rejected` are treated as explicit non-approval inventory.
- New regression tests prove that these inventories are bounded while a
  separate unbounded claim outside the inventory still blocks release.

Generated audit writers were adjusted without changing gate booleans:

- `src/realworld/publication_readiness.py` now uses lower-claim Markdown labels
  such as `Publication Gate Blocker Audit`, `claim-scope audit`, `Unblocked
  gates`, and `Evidence status`.
- `src/realworld/goal_completion_audit.py` now uses lower-claim status labels
  such as `scaffold_unblocked`, prefixes copied gate blockers with `blocked
  requirement:`, and marks acceptance-related headings as `Non-Approval ...`.
- `src/realworld/formal_evidence_path_audit.py` lowered the claim-boundary
  wording from `formal acceptance artifacts` and `validate licenses` to formal
  target/path-hygiene wording.
- `src/realworld/formal_acceptance_package.py` lowered the package boundary
  wording from `validates` to `checks`.

## Regenerated Artifacts

The affected generated artifacts were regenerated:

- `data/manifests/publication_readiness_audit.json`
- `docs/publication_readiness_audit.md`
- `data/manifests/current_goal_completion_audit.json`
- `docs/current_goal_completion_audit.md`
- `data/manifests/formal_evidence_path_audit.json`
- `docs/formal_evidence_path_audit.md`
- `data/manifests/formal_acceptance_package_audit.json`
- `docs/formal_acceptance_package_audit.md`
- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `docs/claim_language_guard.md`
- `data/manifests/claim_alignment_review_packet.csv`
- `data/manifests/claim_alignment_review_manifest.json`
- `docs/claim_alignment_review_packet.md`
- `data/manifests/manuscript_report_decision_packet.csv`
- `data/manifests/manuscript_report_decision_manifest.json`
- `docs/manuscript_report_decision_packet.md`
- `data/validation/dirty_worktree_classification.csv`
- `data/validation/dirty_worktree_classification_manifest.json`
- `docs/dirty_worktree_classification.md`

## Verification Commands

```powershell
.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path data\manifests\publication_readiness_audit.json --scan-path docs\publication_readiness_audit.md --output .tmp_publication_claim_guard.csv --manifest .tmp_publication_claim_guard.json --doc .tmp_publication_claim_guard.md
.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path data\manifests\current_goal_completion_audit.json --scan-path docs\current_goal_completion_audit.md --output .tmp_goal_claim_guard.csv --manifest .tmp_goal_claim_guard.json --doc .tmp_goal_claim_guard.md
.\.venv\Scripts\python .\scripts\audit_claim_language.py
.\.venv\Scripts\python .\scripts\write_claim_alignment_review_packet.py
.\.venv\Scripts\python .\scripts\write_manuscript_report_decision_packet.py
.\.venv\Scripts\python .\scripts\audit_publication_readiness.py
.\.venv\Scripts\python .\scripts\write_goal_completion_audit.py
.\.venv\Scripts\python .\scripts\audit_formal_evidence_paths.py
.\.venv\Scripts\python .\scripts\validate_formal_acceptance_package.py
.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py
.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py
.\.venv\Scripts\python .\tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python .\tests\test_realworld_goal_completion_audit.py
.\.venv\Scripts\python .\tests\test_realworld_formal_evidence_path_audit.py
.\.venv\Scripts\python .\tests\test_realworld_formal_acceptance_package.py
.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py
git diff --check
```

Observed results:

- Focused publication audit guard after edits:
  - `blocking_finding_count`: 0
  - `release_blocked`: false
  - `claim_language_guard_ready`: true for that focused scan
- Focused current-goal audit guard after edits:
  - `blocking_finding_count`: 0
  - `release_blocked`: false
  - `claim_language_guard_ready`: true for that focused scan
- Full claim-language guard after edits:
  - `blocking_finding_count`: 561
  - `release_blocked`: true
  - `final_study_ready`: false
- Claim-language guard tests passed.
- Publication-readiness tests passed.
- Goal-completion audit tests passed.
- Formal evidence-path audit tests passed.
- Formal acceptance package test passed.
- Plan-audit test passed after dirty-worktree classification refresh.
- `git diff --check` exited 0 with LF-to-CRLF warnings only.

## Residual Risk

The full claim-language guard still blocks release with 561 findings across the
broader repository. The next high-impact cleanup slice should start with the
leading remaining generated-document sources, currently including
`docs/artifact_invalidation_quarantine_scope_audit.md`,
`docs/dirty_worktree_classification.md`, `docs/realworld_pipeline.md`, and
`docs/plan_completion_audit.md`.
