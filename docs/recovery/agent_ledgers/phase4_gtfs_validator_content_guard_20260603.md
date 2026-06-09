# Phase 4 GTFS Validator Content Guard Ledger

Date: 2026-06-03

Objective: strengthen cached static-GTFS evidence derivation so a retained
GTFS Validator report cannot certify rail timing evidence unless the report is
hash-bound to the same GTFS source artifact and explicitly reports zero errors.

## Baseline

- Current scope: Phase 4 rail/transit evidence guard work.
- Formal acceptance status: unchanged; no formal acceptance artifact was
  created.
- Claim boundary: review support only, not rail service calibration, emergency
  availability evidence, operational routing, publication acceptance, or final
  study approval.

## Files Inspected

- `src/realworld/rail_gtfs.py`
- `tests/test_realworld_rail_gtfs.py`
- `scripts/derive_rail_gtfs_evidence.py`
- `docs/schemas/rail_gtfs_cache_schema.md`
- `docs/reproducibility_package.md`
- `README.md`
- `status.md`
- `data/manifests/reproducibility_manifest.json`
- `plan.md`

## Files Edited

- `src/realworld/rail_gtfs.py`
- `tests/test_realworld_rail_gtfs.py`
- `docs/schemas/rail_gtfs_cache_schema.md`
- `docs/reproducibility_package.md`
- `README.md`
- `status.md`
- `data/manifests/reproducibility_manifest.json`
- `plan.md`

## Sub-Agent Review

Reviewer: GPT-5.5 xhigh read-only reviewer.

Findings accepted:

- The GTFS Validator report was not bound to the GTFS feed it was supposed to
  validate.
- Missing validator count fields were treated as zero.
- Malformed `notices` report rows could be undercounted.
- New tests had to be included in the direct `tests/test_realworld_rail_gtfs.py`
  command path.

Self-refine actions:

- Added source GTFS artifact SHA verification for retained file inputs.
- Required Validator report feed SHA metadata to match the source artifact SHA.
- Required count-based reports to explicitly include an `errors` field.
- Rejected malformed notice-list rows with non-object notices or unknown
  severities.
- Added direct-run tests for summary counts, error rejection, report SHA
  mismatch, feed SHA mismatch, source artifact SHA mismatch, notice severity,
  missing error counts, and malformed notices.

## Verification

Commands run:

```powershell
.\.venv\Scripts\python -m py_compile .\src\realworld\rail_gtfs.py .\scripts\derive_rail_gtfs_evidence.py .\tests\test_realworld_rail_gtfs.py
.\.venv\Scripts\python .\tests\test_realworld_rail_gtfs.py
.\.venv\Scripts\python .\tests\test_realworld_rail_evidence.py
.\.venv\Scripts\python .\tests\test_realworld_rail_fetch_readiness_packet.py
.\.venv\Scripts\python .\scripts\derive_rail_gtfs_evidence.py --help
.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py
.\.venv\Scripts\python .\tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python -c "import json, pathlib; json.load(pathlib.Path('data/manifests/reproducibility_manifest.json').open(encoding='utf-8')); print('PASS: reproducibility manifest JSON parses')"
.\.venv\Scripts\python .\tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python .\tests\test_realworld_reproducibility_review_packet.py
```

Observed result: all commands above passed after one PowerShell heredoc command
format error was corrected with `python -c`.

## Gate Decision

Proceed within Phase 4 guard work. This closes only the GTFS Validator content
guard implementation gap. It does not close the rail evidence gate because the
reviewed GTFS feed and retained Validator report are still absent for the
current pilot.
