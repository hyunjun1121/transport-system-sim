# Phase 11 Artifact Quarantine Scope Claim-Boundary Sprint - 2026-06-04

## Objective

Reduce release-blocking claim-language findings in
`docs/artifact_invalidation_quarantine_scope_audit.md` by changing the
project-owned generator, not by hand-editing generated Markdown.

## Claim Boundary

This sprint updates a generated audit support document so copied excerpts from
other documents do not create unbounded claim wording in the Markdown view. It
does not close artifact invalidation rows, permit Phase 9 promotion, approve
publication wording, or provide formal acceptance evidence.

## Sub-Agent Wave

| Agent ID | Model | Role | Scope | Result |
| --- | --- | --- | --- | --- |
| `019e8f2e-eaf6-73a2-a5a5-d153bbbc6255` | GPT-5.5 xhigh | read-only source scout | `src/realworld/artifact_invalidation_matrix.py`, writer script, tests, claim findings | confirmed smallest source change is Markdown-only detail sanitization for `reference_hit` rows |
| `019e8f2f-30bc-7890-8f8e-00af9547caca` | GPT-5.5 xhigh | read-only artifact scout | generated Markdown, CSV, manifest, claim guard rows | classified all 36 release blockers as row-derived excerpt text, not fixed template text |

Both agents were read-only and were closed after synthesis.

## Main-Thread Synthesis

Accepted:

- Keep CSV `matched_detail` as full evidence.
- Sanitize only the Markdown detail cell for `reference_hit` rows by omitting
  the copied `excerpt=` text.
- Preserve all non-approval flags:
  `phase9_promotion_ready=false`, `publication_ready=false`,
  `final_study_ready=false`, `formal_acceptance_evidence=false`,
  `can_clear_invalidation_gate=false`, and
  `must_not_be_used_as_closeout_manifest=true`.

Rejected:

- Broadly editing upstream documents in this slice. That would touch several
  independent generated or narrative artifacts and expand the write scope.

## Files Edited

- `src/realworld/artifact_invalidation_matrix.py`
- `tests/test_realworld_artifact_invalidation_matrix.py`
- `docs/recovery/agent_ledgers/phase11_artifact_quarantine_scope_claim_boundary_sprint_20260604.md`

## Generated Artifacts Refreshed

- `data/validation/artifact_invalidation_matrix.csv`
- `data/validation/artifact_invalidation_matrix_manifest.json`
- `docs/artifact_invalidation_matrix.md`
- `data/validation/artifact_invalidation_quarantine_scope_audit.csv`
- `data/validation/artifact_invalidation_quarantine_scope_audit_manifest.json`
- `docs/artifact_invalidation_quarantine_scope_audit.md`
- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `docs/claim_language_guard.md`

## Command Checkpoints

| Checkpoint ID | Command | Result | Claim impact |
| --- | --- | --- | --- |
| QSA-CMD-1 | `.\.venv\Scripts\python .\scripts\write_artifact_invalidation_matrix.py --write-quarantine-scope-audit` | exit 0 | regenerated matrix and quarantine scope audit; still non-approval and Phase 9 blocked |
| QSA-CMD-2 | `.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\docs\artifact_invalidation_quarantine_scope_audit.md --output .\.tmp_quarantine_scope_claim_guard.csv --manifest .\.tmp_quarantine_scope_claim_guard.json --doc .\.tmp_quarantine_scope_claim_guard.md` | exit 0 | single-document blocking findings reduced to 0 |
| QSA-CMD-3 | `.\.venv\Scripts\python .\tests\test_realworld_artifact_invalidation_matrix.py` | exit 0 | artifact invalidation matrix tests passed |
| QSA-CMD-4 | `.\.venv\Scripts\python -m py_compile .\src\realworld\artifact_invalidation_matrix.py .\scripts\write_artifact_invalidation_matrix.py` | exit 0 | changed Python files compile |
| QSA-CMD-5 | `.\.venv\Scripts\python .\scripts\audit_claim_language.py` | exit 0 | full guard blocking findings reduced from 561 to 525; release still blocked |

## Remaining Blockers

- Full claim-language guard remains blocked with 525 release-blocking findings.
- Artifact invalidation still blocks Phase 9. The refreshed quarantine scope
  audit is support evidence only and must not be used as the main closeout
  manifest.
- Dirty-worktree classification must be refreshed after this ledger is added.

