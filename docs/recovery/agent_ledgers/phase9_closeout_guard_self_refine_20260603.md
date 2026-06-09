# Phase 9 Closeout Guard Self-Refine Ledger - 2026-06-03

## Scope

Implemented a fail-closed guard for artifact invalidation closeout rows so
engineering-only compact outputs cannot clear Phase 9 invalidation. Added a
non-acceptance closeout readiness audit that reports evidence gaps without
closing any gate.

## Files Changed

- `src/realworld/artifact_invalidation_matrix.py`
- `scripts/write_artifact_invalidation_matrix.py`
- `tests/test_realworld_artifact_invalidation_matrix.py`
- `data/validation/artifact_invalidation_closeout_readiness_audit.csv`
- `data/validation/artifact_invalidation_closeout_readiness_audit_manifest.json`
- `docs/artifact_invalidation_closeout_readiness_audit.md`

## Sub-Agent Review

- Agent `019e8d81-c48e-7060-b5aa-f43b329e7a0b`, GPT-5.5 xhigh, read-only
  frozen-diff reviewer.
- Initial findings:
  - mixed eligible and blocked compact source manifests could close if the
    eligible manifest was encountered first;
  - CLI readiness audit did not read a filled closeout CSV;
  - compact engineering-only test depended on an untracked generated manifest.
- Self-refine fixes:
  - compact closeout now fails if any referenced compact source manifest is
    blocked;
  - CLI now reads `--closeout-readiness-closeout-input`, or existing
    `--closeout-output`, before writing readiness audit;
  - tests now create compact manifest fixtures in temporary directories.
- Recheck result: no blocker, high, or medium findings.

## Commands Run

```powershell
.\.venv\Scripts\python -m py_compile .\src\realworld\artifact_invalidation_matrix.py .\scripts\write_artifact_invalidation_matrix.py .\tests\test_realworld_artifact_invalidation_matrix.py
git diff --check -- .\src\realworld\artifact_invalidation_matrix.py .\scripts\write_artifact_invalidation_matrix.py .\tests\test_realworld_artifact_invalidation_matrix.py
.\.venv\Scripts\python .\tests\test_realworld_artifact_invalidation_matrix.py
.\.venv\Scripts\python .\scripts\write_artifact_invalidation_matrix.py --write-closeout-template --write-closeout-action-queue --write-closeout-readiness-audit
.\.venv\Scripts\python -c "from src.realworld.artifact_invalidation_matrix import artifact_invalidation_blocks_phase9; blocks, blockers, summary = artifact_invalidation_blocks_phase9(); print('blocks=', blocks); print('blocker_count=', len(blockers)); print('matrix_blocking=', summary.get('blocking_row_count')); print('closeout_pending=', summary.get('closeout_snapshot', {}).get('pending_or_invalid_row_count'))"
```

## Current Gate State

- `artifact_invalidation_blocks_phase9()` still reports `blocks=True`.
- Matrix blocking rows: 51.
- Closeout pending rows: 51.
- Readiness audit rows: 51.
- Closeout-ready rows: 0.
- Phase 9 promotion ready: `false`.
- The readiness audit has `must_not_be_used_as_closeout_manifest=true`.

This work improves the guardrail and review-support layer only. It does not
complete artifact invalidation closeout, publication readiness, final-study
readiness, or formal acceptance.

## Follow-On Closeout CSV Verification Patch

After the first guard patch, the Phase 9 preflight still trusted closeout
manifest summary counts. The follow-on patch makes
`summarize_artifact_invalidation_closeout_manifest()` read the manifest's
`outputs.csv`, validate the closeout CSV schema, recompute closeout row counts,
and compare `row_count`, `closed_row_count`, and
`pending_or_invalid_row_count` against the manifest.

Additional tests now verify that a spoofed closeout manifest claiming
`pending_or_invalid_row_count=0` remains blocked when its CSV rows are still
pending.

Additional commands run:

```powershell
.\.venv\Scripts\python -m py_compile .\src\realworld\artifact_invalidation_matrix.py .\scripts\write_artifact_invalidation_matrix.py .\tests\test_realworld_artifact_invalidation_matrix.py
git diff --check -- .\src\realworld\artifact_invalidation_matrix.py .\tests\test_realworld_artifact_invalidation_matrix.py
.\.venv\Scripts\python .\tests\test_realworld_artifact_invalidation_matrix.py
.\.venv\Scripts\python .\scripts\write_artifact_invalidation_matrix.py --write-closeout-template --write-closeout-action-queue --write-closeout-readiness-audit
```

Observed current closeout snapshot after regeneration:

- `blocks=True`.
- `closeout_csv_verification_status=verified`.
- `closeout_csv_summary_matches_manifest=True`.
- `closeout_pending=51`.
