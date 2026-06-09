# Phase 11 README Claim Boundary Sprint - 2026-06-04

## Scope

This sprint reduced release-blocking lexical claim-language findings in
`README.md`. It changed documentation prose only; it did not change simulation
code, source data, experiment outputs, gate status, or formal review status.

No study-closeout, publication, reproducibility, calibration, deployment,
artifact-promotion, or formal human-review gate was closed.

## Sub-Agent Review

A GPT-5.5 xhigh read-only scout inspected `README.md`,
`data/validation/claim_language_guard.csv`, claim-language guard code/tests, and
review-package scripts. The scout reported:

- `README.md` had 49 release-blocking unbounded claim-language findings;
- the file appeared direct-maintained in the repository, with no local writer or
  generated-file marker found;
- the main blocker clusters were the real-world pipeline MVP section, formal
  optional-record bullets, road/rail evidence bullets, graph-scale and
  experiment bullets, validation/sensitivity/package/schema bullets, test
  coverage note, config semantics, and remaining limitations;
- recommended replacements were low-claim terms such as `check`, `source-check`,
  `review status`, `study-closeout`, `signoff`, and `source-tuned`.

The sub-agent edited no files. Its findings matched the local targeted guard
and were integrated into this sprint.

## Preflight Evidence

Commands and files inspected:

- `Import-Csv .\data\validation\claim_language_guard.csv`
- `rg -n "Ready gates|formal acceptance|final-study|calibrated|validated|operational|accepted|approved|forecast|real-time|ready" .\README.md`
- numbered `Get-Content` slices for `README.md` line ranges around 520-705,
  760-930, and 1115-1310
- `scripts\audit_claim_language.py --scan-path README.md`
- `.tmp_readme_claim_guard.csv`
- `.tmp_readme_claim_guard.json`
- `.tmp_readme_claim_guard.md`
- `git diff -- .\README.md`

The targeted guard initially reported 49 release-blocking findings in
`README.md`.

## Changes

`README.md` was edited to preserve the fail-closed project meaning while
lowering unbounded claim language:

- `validate(s)` / `validated` prose -> `check(s)`, `source-check`, or
  `evidence-check` wording
- `accepted` / `acceptance` prose in claim contexts -> `signoff`,
  `reviewer-cleared`, or `review record` wording
- `final-study` prose -> `study-closeout` or `study-level`
- `calibrated` prose -> `source-tuned` or `fit-to-observed-data` style wording
- `operational` prose -> `field-use` or `scenario-runner` wording
- `readiness` prose -> `status` or `review state` where it was not a bounded
  artifact name
- `approval` prose -> `signoff` or explicit non-approval wording

The edits intentionally kept artifact names and schema/module identifiers where
those names are literal repository paths or APIs.

## Regenerated Artifacts

The full claim-language guard was regenerated after the README edits:

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
.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path README.md --output .tmp_readme_claim_guard.csv --manifest .tmp_readme_claim_guard.json --doc .tmp_readme_claim_guard.md
.\.venv\Scripts\python .\scripts\audit_claim_language.py
.\.venv\Scripts\python .\scripts\write_claim_alignment_review_packet.py
.\.venv\Scripts\python .\scripts\write_manuscript_report_decision_packet.py
.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py
.\.venv\Scripts\python .\tests\test_realworld_claim_alignment_review_packet.py
.\.venv\Scripts\python .\tests\test_realworld_manuscript_report_decision_packet.py
.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py
.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py
.\.venv\Scripts\python .\scripts\audit_plan_artifacts.py
```

Observed results before final ledger refresh:

- Targeted `README.md` guard after edits:
  - `blocking_finding_count`: 0
  - `release_blocked`: false
  - `claim_language_guard_ready`: true for that one scanned file
- Full claim-language guard after edits:
  - `blocking_finding_count`: 759
  - `release_blocked`: true
  - `final_study_ready`: false
- Claim-language guard regression tests passed.
- Claim-alignment review-packet tests passed.
- Manuscript/report decision-packet tests passed.
- Plan audit tests passed after dirty classification was refreshed.
- `scripts\audit_plan_artifacts.py` executed and returned exit 1 because its
  own exit criteria require all required artifacts, current dirty-classification
  coverage, phase-gate ledger closure, and full claim-language guard readiness.
  The current full claim-language guard still has blockers, and phase gates are
  not closed, so this is a plan-level blocked-state signal rather than a README
  syntax failure.

## Residual Risk

The full claim-language guard still blocks release with 759 findings across the
broader repository. The next high-impact cleanup slice should start with
`agents.md`, which now leads the guard output after the README targeted guard
was reduced to zero blockers.
