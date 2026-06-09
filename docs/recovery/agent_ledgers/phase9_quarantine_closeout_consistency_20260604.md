# Phase 9 Quarantine Closeout Consistency Ledger - 2026-06-04

## Scope

This ledger records a narrow Phase 9 artifact-invalidation consistency fix for
the immediate `quarantine_non_evidence` closeout template family. It is not a
Phase 9 closeout record, not reviewer signoff, not publication readiness, not
final-study approval, and not formal acceptance.

## Trigger

The quarantine closeout CSV could be rewritten while the manifest and Markdown
were preserved by content-aware writers. That created timestamp drift between:

- `data/validation/artifact_invalidation_quarantine_closeout_template.csv`
- `data/validation/artifact_invalidation_quarantine_closeout_manifest.json`
- `docs/artifact_invalidation_quarantine_closeout_template.md`

## Edits

- Added content-aware CSV writing for
  `write_artifact_invalidation_quarantine_closeout_template`.
- Added `csv_sha256` to the quarantine closeout manifest and Markdown summary.
- Computed `csv_sha256` from the actual written CSV bytes.
- Added a regression test proving repeated writes skip unchanged CSV rewrites.

## Evidence Commands

```powershell
.\.venv\Scripts\python -m py_compile src\realworld\artifact_invalidation_matrix.py scripts\write_artifact_invalidation_matrix.py tests\test_realworld_artifact_invalidation_matrix.py
.\.venv\Scripts\python tests\test_realworld_artifact_invalidation_matrix.py
.\.venv\Scripts\python scripts\write_artifact_invalidation_matrix.py --write-quarantine-closeout-template --write-quarantine-scope-audit --write-quarantine-non-evidence-index --write-quarantine-non-evidence-transfer-packet
.\.venv\Scripts\python scripts\audit_claim_language.py --fail-on-blockers
.\.venv\Scripts\python tests\test_realworld_claim_language_guard.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
git diff --check -- src\realworld\artifact_invalidation_matrix.py tests\test_realworld_artifact_invalidation_matrix.py data\validation\artifact_invalidation_quarantine_closeout_manifest.json docs\artifact_invalidation_quarantine_closeout_template.md
```

## Results

- Artifact invalidation tests passed.
- Claim-language guard passed with `blocking_finding_count=0`.
- Plan audit test passed.
- `git diff --check` returned no whitespace findings for the touched files.
- The manifest `csv_sha256` matched the actual CSV file SHA256:
  `5970895b8c8d1f00c51d5577f4e5dc38fec0de1ebfcea7c1707e03840b9ce75e`.
- A repeated generator run left the quarantine closeout CSV, manifest, and
  Markdown hash and mtime unchanged.

## Remaining Blockers

- The quarantine closeout template still has 6 rows, all pending and unsigned.
- The full artifact invalidation matrix still has 51 unresolved blocking rows.
- `phase9_promotion_ready=false`, `publication_ready=false`,
  `final_study_ready=false`, and `formal_acceptance_evidence=false` remain
  unchanged.

