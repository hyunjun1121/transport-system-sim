# Phase 11 Plan Methodology Claim-Boundary Sprint - 2026-06-04

## Objective

Remove the release-blocking lexical claim-language finding at `plan.md:401`
while preserving the intended reviewer role in the canonical implementation
plan.

## Scope Boundary

This sprint changed one reviewer-role phrase in `plan.md`. It did not change
simulation semantics, evidence gates, review requirements, generated experiment
outputs, formal acceptance records, publication readiness, or final-study
readiness.

## Main-Thread Inspection

- Inspected `plan.md` lines 388-410.
- Inspected the `plan.md` release-blocking row in
  `data/validation/claim_language_guard.csv`.
- Inspected all `calibrated` occurrences in `plan.md`.
- Inspected the plan diff before and after the edit.

## Edit

- Replaced `transportation-methodology reviewer for realism, calibration
  boundaries, and research-method adequacy` with
  `transportation-methodology reviewer for realism, empirical-fit boundaries,
  and research-method adequacy`.

The new phrase keeps the reviewer responsibility for realism and empirical-fit
limits while avoiding unbounded claim language in the plan.

## Commands

| Command | Result | Claim Impact |
| --- | --- | --- |
| `Import-Csv data\validation\claim_language_guard.csv ... plan.md ... Format-List` | Exit 0; identified `plan.md:401 calibrated` as the only release-blocking `plan.md` row | Established the exact blocker and target line before editing. |
| `rg -n "calibrated" plan.md` | Exit 0; listed other bounded/non-claim occurrences | Confirmed the edit should target the reviewer-role phrase rather than broad plan language. |
| `.\.venv\Scripts\python scripts\audit_claim_language.py --scan-path plan.md --output data\validation\tmp_claim_language_guard_plan.csv --doc docs\tmp_claim_language_guard_plan.md --manifest data\validation\tmp_claim_language_guard_plan_manifest.json --fail-on-blockers` | Exit 0; focused `plan.md` scan reported `blocking_finding_count=0` | Confirms `plan.md` no longer has release-blocking lexical findings. |
| `rg -n "calibration boundaries" plan.md` | Exit 1; old phrase absent | Confirms the blocker phrase was removed. |
| Temp focused-guard cleanup for `data\validation\tmp_claim_language_guard_plan.csv`, `docs\tmp_claim_language_guard_plan.md`, and `data\validation\tmp_claim_language_guard_plan_manifest.json` | Exit 0; all temp files absent after cleanup | Prevents temporary audit output from becoming package noise. |
| `.\.venv\Scripts\python scripts\audit_claim_language.py` | Exit 0; full scan reported `blocking_finding_count=34` | Reduced total release-blocking lexical findings from 35 to 34. Release remains blocked. |
| `.\.venv\Scripts\python tests\test_realworld_plan_audit.py` | Exit 0; plan audit test passed | Confirms the canonical plan still satisfies the plan-audit scaffold boundary. |
| `.\.venv\Scripts\python tests\test_realworld_claim_language_guard.py` | Exit 0; claim-language guard tests passed | Confirms guard behavior after the full refresh. |
| `git diff --check -- plan.md data\validation\claim_language_guard.csv data\validation\claim_language_guard_manifest.json docs\claim_language_guard.md` | Exit 0; PowerShell printed a CRLF normalization warning for `plan.md` | No whitespace errors were reported. |
| `Import-Csv data\validation\claim_language_guard.csv ... plan.md ... Measure-Object` | Exit 0; count `0` | Confirms `plan.md` has no remaining release-blocking lexical row. |

## Result

- `plan.md` release-blocking lexical rows: `1 -> 0`.
- Overall claim-language guard release-blocking rows: `35 -> 34`.
- `release_blocked=true`, `final_study_ready=false`, and
  `can_mark_complete=false` remain unchanged.

## Remaining Work

Continue Phase 11 claim-language cleanup from the next row in
`data/validation/claim_language_guard_manifest.json`. The remaining blockers
are still wording or formal-evidence boundary issues; resolving lexical blockers
does not close evidence, publication, reproducibility, or final-study gates.
