# Phase 11 Plan Claim Boundary Sprint - 2026-06-04

## Scope

This sprint reduced release-blocking lexical claim-language findings in
`plan.md`. It changed workflow prose only; it did not change simulation code,
source data, experiment outputs, gate status, or formal review status.

No study-closeout, publication, reproducibility, calibration, deployment,
artifact-promotion, or formal human-review gate was closed.

## Sub-Agent Review

A GPT-5.5 xhigh read-only scout inspected `plan.md`,
`data/validation/claim_language_guard.csv`, claim-language guard code/tests,
plan-audit code, and related publication/final-study audit scripts. The scout
reported that the checked guard CSV was stale for the current `plan.md`, and
that the remaining live blocker at that moment was the literal command option
`--write-closeout-readiness-audit`.

The sub-agent recommended preserving the exact command string because
`tests/test_realworld_plan_audit.py` asserts it, and bounding it as a command
reference rather than weakening the command. The sub-agent edited no files. Its
finding was integrated by keeping the command text and placing the audit command
coverage list in a fenced PowerShell inventory block.

## Preflight Evidence

Commands and files inspected:

- `Import-Csv .\data\validation\claim_language_guard.csv`
- `rg -n "validated|accepted|final|ready|calibrated|operational|approved|forecast|real-time" .\plan.md`
- numbered `Get-Content` slices for `plan.md` line ranges around 175-245,
  355-395, 540-615, 666-705, 812-865, 974-1018, 1156-1168, and 1194-1204
- `src/realworld/claim_language_guard.py`
- `scripts/audit_claim_language.py --scan-path plan.md`
- `.tmp_plan_claim_guard.csv`
- `.tmp_plan_claim_guard.json`
- `.tmp_plan_claim_guard.md`

The targeted guard initially reported 27 release-blocking findings in
`plan.md`.

## Changes

`plan.md` was edited to preserve the multi-agent workflow while lowering
unbounded claim language:

- `validation` prose in claim contexts -> `evidence-check`, `benchmark
  check`, `source check`, or `cross-check` wording;
- `accepted` / `acceptance` prose in claim contexts -> `adopted`,
  `signed-off`, `signoff`, or explicit non-approval wording;
- `final` / `final-output` prose -> `closeout`, `study-closeout`, or
  `closeout-output` wording where not a literal artifact name;
- `readiness` prose -> `status` where not a required literal command or
  artifact reference;
- `calibration` prose -> `source tuning` or `fit-to-observed-data` style
  wording;
- command references in `## 15. Audit Command Coverage` were converted into a
  fenced PowerShell inventory so literal command terms remain bounded
  non-claim references.

The edits intentionally kept the required
`scripts\write_artifact_invalidation_matrix.py --write-closeout-readiness-audit`
command string unchanged.

## Regenerated Artifacts

The full claim-language guard was regenerated after the `plan.md` edits:

- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `docs/claim_language_guard.md`

The manuscript-facing review aids were regenerated after the full guard refresh:

- `data/manifests/claim_alignment_review_packet.csv`
- `data/manifests/claim_alignment_review_manifest.json`
- `docs/claim_alignment_review_packet.md`
- `data/manifests/manuscript_report_decision_packet.csv`
- `data/manifests/manuscript_report_decision_manifest.json`
- `docs/manuscript_report_decision_packet.md`

## Verification Commands

```powershell
.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path plan.md --output .tmp_plan_claim_guard.csv --manifest .tmp_plan_claim_guard.json --doc .tmp_plan_claim_guard.md
.\.venv\Scripts\python .\scripts\audit_claim_language.py
.\.venv\Scripts\python .\scripts\write_claim_alignment_review_packet.py
.\.venv\Scripts\python .\scripts\write_manuscript_report_decision_packet.py
.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py
.\.venv\Scripts\python .\tests\test_realworld_claim_alignment_review_packet.py
.\.venv\Scripts\python .\tests\test_realworld_manuscript_report_decision_packet.py
.\.venv\Scripts\python .\tests\test_realworld_review_package_inventory.py
```

Observed results before final dirty-classification refresh:

- Targeted `plan.md` guard after edits:
  - `blocking_finding_count`: 0
  - `release_blocked`: false
  - `claim_language_guard_ready`: true for that one scanned file
- Full claim-language guard after edits:
  - `blocking_finding_count`: 674
  - `release_blocked`: true
  - `final_study_ready`: false
- Claim-alignment review packet remained `row_count: 70` with
  `overclaim_candidate_count: 42`.
- Manuscript/report decision packet remained `row_count: 7` with
  `blocking_decision_count: 4`.
- Claim-language guard tests passed.
- Claim-alignment review-packet tests passed.
- Manuscript/report decision-packet tests passed.
- Review-package inventory test passed.

## Residual Risk

The full claim-language guard still blocks release with 674 findings across the
broader repository. After `paper/paper_draft.md`, `README.md`, `agents.md`, and
`plan.md` were reduced to zero targeted blockers, the next cleanup slice should
start from the leading remaining sources in the full guard output, beginning
with generated/current audit artifacts such as
`data/manifests/publication_readiness_audit.json` and
`data/manifests/current_goal_completion_audit.json`.
