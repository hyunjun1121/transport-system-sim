# Phase 11 Status Claim Boundary Sprint - 2026-06-04

## Scope

This sprint continued the fail-closed claim-language cleanup required by
`plan.md`. It focused on `status.md`, plus a narrow guard correction for wrapped
non-approval clauses.

No final-study, publication, formal-signoff, reproducibility, artifact
promotion, or calibration gate was closed.

## Agent Wave

Two GPT-5.5 xhigh read-only scouts were used in parallel:

- `019e8eb2-df6b-7502-9f6f-a15573f1ba04`: inspected `status.md` blockers from
  `data/validation/claim_language_guard.csv`.
- `019e8eb3-2edf-7652-9162-3bd0e1b400f7`: inspected
  `docs/reproducibility_package.md` and `paper/paper_draft.md` blockers as the
  next-slice candidates.

Both agents were read-only. Both were closed after their findings were
integrated.

## Changes

Code/test guard changes:

- `src/realworld/claim_language_guard.py`
  - Preserves newline structure in context windows.
  - Treats a reserved term as explicitly bounded when the term is in a line
    that is syntactically continued from an immediately preceding non-approval
    clause, for example a wrapped `does not prove ...` sentence.
  - Keeps this rule narrow: separate sentences and literal field/status lines
    do not bound later overclaims.
  - Restricts formal-evidence classification to same-line context so a nearby
    `formal` phrase cannot clear a later overclaim.
- `tests/test_realworld_claim_language_guard.py`
  - Adds a regression test for wrapped non-approval clauses.
  - Preserves tests that literal paths, fenced inventory lines, and false fields
    do not clear neighboring prose overclaims.

Documentation changes:

- `status.md`
  - Replaced release-sensitive terms with lower-claim wording:
    `acceptance validation` -> `review-record checker`,
    `readiness` -> `preflight`,
    `final-study` -> `study-closeout`,
    `calibrated` -> `fit-to-observed-data` or `source-tuned`,
    `operational` -> `field-use`,
    `forecast` -> `prediction`,
    `approval` -> `signoff`.
  - Preserved the same fail-closed meaning: blocked gates remain blocked, formal
    records remain absent, and outputs remain decision-support only.

Regenerated artifacts:

- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `docs/claim_language_guard.md`
- `data/validation/dirty_worktree_classification.csv`
- `data/validation/dirty_worktree_classification_manifest.json`
- `docs/dirty_worktree_classification.md`

## Verification Commands

```powershell
.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py
.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path status.md --output .tmp_status_claim_guard.csv --manifest .tmp_status_claim_guard.json --doc .tmp_status_claim_guard.md
.\.venv\Scripts\python .\scripts\audit_claim_language.py
.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py
git diff --check -- .\status.md .\src\realworld\claim_language_guard.py .\tests\test_realworld_claim_language_guard.py .\data\validation\claim_language_guard.csv .\data\validation\claim_language_guard_manifest.json .\docs\claim_language_guard.md .\data\validation\dirty_worktree_classification.csv .\data\validation\dirty_worktree_classification_manifest.json .\docs\dirty_worktree_classification.md
.\.venv\Scripts\python .\scripts\audit_plan_artifacts.py
.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py
```

Observed results:

- Claim-language guard regression tests passed.
- `status.md` targeted claim-language audit reached
  `blocking_finding_count=0`.
- Full claim-language audit ran successfully and remained fail-closed with
  `blocking_finding_count=961`.
- Plan audit regression test passed.
- `git diff --check` found no whitespace errors; it reported LF/CRLF warnings
  for `status.md`.
- `audit_plan_artifacts.py` exited with code 1 as expected for the current
  fail-closed project state.
- Dirty worktree classification regenerated successfully.

Temporary targeted-audit files were removed:

- `.tmp_status_claim_guard.csv`
- `.tmp_status_claim_guard.json`
- `.tmp_status_claim_guard.md`

## Count Summary

Full claim-language guard:

- Before this sprint: `blocking_finding_count=1535`
- After wrapped-clause guard fix: `blocking_finding_count=1052`
- After `status.md` cleanup: `blocking_finding_count=961`

Focused `status.md` state:

- Scout-observed blocker count before this cleanup: 139
- After wrapped-clause guard fix: 91
- After wording cleanup: 0

Top remaining blocker sources after this sprint:

- `paper/paper_draft.md`: 76
- `agents.md`: 58
- `docs/reproducibility_package.md`: 56
- `README.md`: 49
- `docs/claim_alignment_review_packet.md`: 45
- `docs/plan_completion_audit.md`: 43
- `data/manifests/formal_acceptance_package_audit.json`: 38
- `docs/artifact_invalidation_quarantine_scope_audit.md`: 36
- `docs/dirty_worktree_classification.md`: 30
- `docs/realworld_pipeline.md`: 27
- `plan.md`: 26

## Boundary

This sprint did not:

- approve the model;
- prove real-world calibration;
- create formal signoff records;
- promote generated outputs;
- close reproducibility;
- close publication or study-closeout gates.

Next recommended slice: use the second scout's finding and clean
`docs/reproducibility_package.md`, especially its scope, claim-boundary,
manifest-table, and remaining-upgrade sections.
