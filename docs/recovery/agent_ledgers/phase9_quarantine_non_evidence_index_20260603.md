# Phase 9 Quarantine Non-Evidence Index Ledger - 2026-06-03

## Objective

Advance the Phase 9 artifact-invalidation workflow without falsely clearing
Phase 9. The immediate action queue batch is `quarantine_non_evidence`, which
requires stale full-output and review-package artifacts to be excluded or marked
non-evidence before regeneration and promotion work continues.

This sprint added a deduplicated reviewer-triage index. It does not move,
delete, regenerate, approve, or close artifacts.

## Sub-Agent Review Wave

- Aquinas (`019e8b7e-5edc-71e2-841f-7c3e13ca7e05`): read-only methodology
  reviewer. Recommended adding the index only if it remains aggregate-only,
  excludes closeout/signoff fields, keeps all readiness flags false, and records
  `must_not_be_used_as_closeout_manifest=true`.
- Helmholtz (`019e8b7e-b16b-7d03-a2be-799343d62a8a`): read-only
  implementation/test reviewer. Recommended deriving the index from existing
  quarantine scope rows, filtering only `stale_artifact_candidate` and
  `zip_candidate`, deduplicating by `matched_path`, preserving source
  `invalidation_row_id`s, adding CLI flags, and excluding the new index files
  from future scope-audit self-reference scans.

## Files Added Or Updated

- `src/realworld/artifact_invalidation_matrix.py`
- `scripts/write_artifact_invalidation_matrix.py`
- `tests/test_realworld_artifact_invalidation_matrix.py`
- `data/validation/artifact_invalidation_quarantine_non_evidence_index.csv`
- `data/validation/artifact_invalidation_quarantine_non_evidence_index_manifest.json`
- `docs/artifact_invalidation_quarantine_non_evidence_index.md`
- `plan.md`
- `status.md`
- `agents.md`

## Generated Evidence

`data/validation/artifact_invalidation_quarantine_non_evidence_index_manifest.json`
currently records:

- `row_count=25`
- `source_candidate_finding_count=73`
- `deduped_duplicate_count=48`
- `covered_quarantine_row_count=6`
- `expected_quarantine_row_count=6`
- `indexed_full_output_count=12`
- `indexed_review_package_count=13`
- `indexed_zip_candidate_count=4`
- `phase9_promotion_ready=false`
- `can_clear_invalidation_gate=false`
- `publication_ready=false`
- `final_study_ready=false`
- `formal_acceptance_evidence=false`
- `must_not_be_used_as_closeout_manifest=true`

Interpretation: the index makes stale full-output and review-package candidates
easier to review, but it remains non-acceptance triage only. Confirmed entries
must still be copied into the main artifact invalidation closeout record with
audit/test evidence and non-acceptance reviewer signoff.

## Commands Run

```powershell
.\.venv\Scripts\python -m py_compile src\realworld\artifact_invalidation_matrix.py scripts\write_artifact_invalidation_matrix.py tests\test_realworld_artifact_invalidation_matrix.py
.\.venv\Scripts\python tests\test_realworld_artifact_invalidation_matrix.py
.\.venv\Scripts\python scripts\write_artifact_invalidation_matrix.py --write-closeout-template --write-closeout-action-queue --write-quarantine-closeout-template --write-quarantine-scope-audit --write-quarantine-non-evidence-index
```

Observed result: compile and invalidation tests passed; writer completed and
generated the index while keeping Phase 9 blocked.

## Remaining Blockers

- Main closeout still has 51 pending rows and 0 closed rows.
- Quarantine closeout still has 6 pending rows and 0 closed rows.
- The new index cannot be used as the closeout manifest.
- Full-run promotion remains blocked until stale rows are regenerated,
  explicitly excluded, or marked non-evidence in the main closeout record with
  reviewer signoff for invalidation closeout only.
