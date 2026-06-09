# Phase 9 Quarantine Closeout Prefill Ledger - 2026-06-04

## Scope

This ledger records a narrow Phase 9 support update for the immediate
`quarantine_non_evidence` artifact-invalidation batch. It creates a
closeout-schema prefill worksheet from the quarantine transfer packet so a
reviewer can copy confirmed candidate path and hash evidence into the separate
main closeout record.

This is prefill support only. It is not closeout evidence, not reviewer
signoff, not artifact regeneration evidence, not citation-removal approval, not
publication readiness, not final-study approval, not formal acceptance, and not
authorization for Phase 9 promotion.

## Objective

Reduce reviewer copy/paste risk for the six-row quarantine batch while keeping
all closeout rows pending until reviewer confirmation, audit/test evidence, and
non-acceptance signoff exist.

## Edits

- Added CLI support for `--write-quarantine-closeout-prefill` in
  `scripts/write_artifact_invalidation_matrix.py`.
- Added default output path arguments for the prefill CSV, manifest, and
  Markdown document.
- Added tests proving that the prefill:
  - maps the quarantine transfer packet into the closeout schema;
  - records source transfer-packet manifest path, SHA256, row count, candidate
    artifact count, and source integrity flag;
  - keeps `closeout_status=pending`;
  - keeps rerun, audit, and targeted-test results as `not_run`;
  - keeps reviewer signoff as `unsigned`;
  - keeps `can_clear_invalidation_gate=false`;
  - keeps publication, final-study, and formal-acceptance flags false;
  - cannot be used as the main closeout manifest.
- Generated the prefill artifacts:
  - `data/validation/artifact_invalidation_quarantine_closeout_prefill.csv`
  - `data/validation/artifact_invalidation_quarantine_closeout_prefill_manifest.json`
  - `docs/artifact_invalidation_quarantine_closeout_prefill.md`

## Evidence Commands

```powershell
.\.venv\Scripts\python -m py_compile src\realworld\artifact_invalidation_matrix.py scripts\write_artifact_invalidation_matrix.py tests\test_realworld_artifact_invalidation_matrix.py
.\.venv\Scripts\python tests\test_realworld_artifact_invalidation_matrix.py
.\.venv\Scripts\python scripts\write_artifact_invalidation_matrix.py --write-quarantine-closeout-prefill
.\.venv\Scripts\python scripts\audit_claim_language.py --fail-on-blockers
.\.venv\Scripts\python tests\test_realworld_claim_language_guard.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
.\.venv\Scripts\python scripts\write_dirty_worktree_classification.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
git diff --check -- src\realworld\artifact_invalidation_matrix.py scripts\write_artifact_invalidation_matrix.py tests\test_realworld_artifact_invalidation_matrix.py data\validation\artifact_invalidation_quarantine_closeout_prefill.csv data\validation\artifact_invalidation_quarantine_closeout_prefill_manifest.json docs\artifact_invalidation_quarantine_closeout_prefill.md data\validation\dirty_worktree_classification.csv data\validation\dirty_worktree_classification_manifest.json docs\dirty_worktree_classification.md
```

## Results

- `py_compile` passed for the changed Python files.
- Artifact invalidation tests passed, including the new prefill tests and CLI
  test.
- The prefill writer generated:
  - rows: 6
  - prefilled rows: 6
  - candidate artifacts copied into prefill: 73
  - pending or invalid rows: 6
  - CSV SHA256:
    `d6e215f9a7d737ca1a1ca109a645923acb4751c0bf772a27bc5d90daa6b0d807`
  - source transfer-packet manifest:
    `data/validation/artifact_invalidation_quarantine_non_evidence_transfer_packet_manifest.json`
  - source transfer-packet manifest SHA256:
    `2def07690588e7c5b7a3c7efd13c8cb1e5bddadeaf570c700432269cdc1d7ccd`
  - source transfer-packet rows: 6
  - source transfer-packet candidate artifacts: 73
- Claim-language guard passed with `blocking_finding_count=0`.
- Claim-language guard tests passed.
- During lineage hardening, the first regenerated Markdown used the phrase
  `Source transfer packet integrity ready`, which the claim-language guard
  correctly blocked as an unbounded reserved term. The label was changed to
  `Source transfer packet integrity flag`, the prefill document was
  regenerated, and the claim-language guard then passed with
  `blocking_finding_count=0`.
- The first `tests\test_realworld_plan_audit.py` run failed because the dirty
  worktree classification manifest still reflected the pre-prefill dirty path
  count.
- After rerunning `scripts\write_dirty_worktree_classification.py`, dirty
  classification reported:
  - dirty path count: 673
  - classified path count: 673
  - unclassified path count: 0
  - `new_generated_output_allowed=false`
  - `final_study_ready=false`
- The rerun of `tests\test_realworld_plan_audit.py` passed.
- `git diff --check` returned no whitespace findings for the touched paths.

## Remaining Blockers

- This prefill covers only the six-row `quarantine_non_evidence` batch, not all
  51 invalidation rows.
- All six prefilled rows remain pending and unsigned.
- The main closeout record still requires reviewer-confirmed disposition,
  exclusion or citation-removal evidence, targeted test evidence, and
  non-acceptance signoff before invalidation can be cleared.
- The Phase 9 matrix still has 51 unresolved stale rows.
- `phase9_promotion_ready=false`, `publication_ready=false`,
  `final_study_ready=false`, and `formal_acceptance_evidence=false` remain
  unchanged.
