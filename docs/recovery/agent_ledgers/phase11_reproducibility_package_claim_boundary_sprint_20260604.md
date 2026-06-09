# Phase 11 Reproducibility Package Claim Boundary Sprint - 2026-06-04

## Scope

This sprint reduced release-blocking lexical claim-language findings in
`docs/reproducibility_package.md`. It changed prose only; it did not change
simulation code, source data, experiment outputs, or gate status.

No study-closeout, publication, reproducibility, calibration, field-use,
artifact-promotion, or formal human-review gate was closed.

## Preflight Evidence

Commands and files inspected:

- `scripts\audit_claim_language.py --scan-path docs/reproducibility_package.md`
- `.tmp_repro_claim_guard.csv`
- `.tmp_repro_claim_guard.json`
- `.tmp_repro_claim_guard.md`
- `docs/reproducibility_package.md`
- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `docs/claim_language_guard.md`

The targeted guard initially reported 56 release-blocking findings in
`docs/reproducibility_package.md`.

## Changes

`docs/reproducibility_package.md` was edited to preserve the same fail-closed
meaning while lowering claim language:

- `ready gates` -> `preflight-pass gates`
- `acceptance` / `accepted` prose -> `signoff`, `reviewer-selected`, or
  `decision records`
- `final-study` prose -> `study-closeout` or `study-level`
- `calibrated` prose -> `fit-to-observed-data`, `source-tuned`, or
  `benchmark fit`
- `operational` prose -> `deployment` or bounded public demo context
- `validation ladder` -> `reproduction check ladder`
- `publication-readiness` / `final-study readiness` status prose -> blocked
  publication/study audit wording

The `Not allowed` section was rewritten as explicit low-claim instructions
rather than repeating the overclaim phrases verbatim.

## Verification Commands

```powershell
.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path docs/reproducibility_package.md --output .tmp_repro_claim_guard.csv --manifest .tmp_repro_claim_guard.json --doc .tmp_repro_claim_guard.md
.\.venv\Scripts\python .\scripts\audit_claim_language.py
.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py
.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py
git diff --check -- .\docs\reproducibility_package.md .\data\validation\claim_language_guard.csv .\data\validation\claim_language_guard_manifest.json .\docs\claim_language_guard.md .\plan.md .\docs\recovery\agent_ledgers\phase_plan_multi_agent_runtime_hardening_20260604.md
Remove-Item -LiteralPath .\.tmp_repro_claim_guard.csv, .\.tmp_repro_claim_guard.json, .\.tmp_repro_claim_guard.md -ErrorAction SilentlyContinue
.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py
```

Observed results:

- Targeted `docs/reproducibility_package.md` guard after edits:
  - `blocking_finding_count`: 0
  - `release_blocked`: false
  - `claim_language_guard_ready`: true for that one scanned file
- Full claim-language guard after edits:
  - `blocking_finding_count`: 906
  - `release_blocked`: true
  - `final_study_ready`: false
- Claim-language guard regression tests passed.
- Plan audit tests passed after dirty classification was refreshed.
- `git diff --check` exited 0 for the touched files; Git emitted LF-to-CRLF
  working-copy warnings for Markdown files only.
- Temporary `.tmp_repro_claim_guard.*` files were removed.

## Residual Risk

The full claim-language guard still blocks release with 906 findings across the
broader repository. The next high-impact claim cleanup slice should be selected
from the current `data/validation/claim_language_guard.csv`, with generated
source handling checked before direct edits.
