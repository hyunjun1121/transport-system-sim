# Phase 11 Agents Claim Boundary Sprint - 2026-06-04

## Scope

This sprint reduced release-blocking lexical claim-language findings in
`agents.md`. It changed agent instruction prose only; it did not change
simulation code, source data, experiment outputs, gate status, or formal
review status.

No study-closeout, publication, reproducibility, calibration, deployment,
artifact-promotion, or formal human-review gate was closed.

## Sub-Agent Review

A GPT-5.5 xhigh read-only scout inspected `agents.md`,
`data/validation/claim_language_guard.csv`, claim-language guard code/tests,
review-package inventory code, and relevant tests. The scout reported:

- `agents.md` appeared direct-maintained in the repository, with no generated
  header or local writer found;
- `agents.md` initially had 58 release-blocking unbounded claim-language
  findings;
- blocker clusters were concentrated in config schema notes, formal
  guard/package bullets, optional acceptance-record bullets, road/graph/rail
  packet wording, experiment/sensitivity/evidence-check packet wording,
  audit/schema-doc wording, current research upgrade direction, and remaining
  limitations;
- safe replacements should preserve literal paths and use low-claim prose such
  as `schema-checks`, `study-closeout gate status`, `source-backed`,
  `source-tuned`, and `pre-review blocker rows`.

The sub-agent edited no files. Its findings matched the local targeted guard
and were integrated into this sprint.

## Preflight Evidence

Commands and files inspected:

- `Import-Csv .\data\validation\claim_language_guard.csv`
- `rg -n "validated|accepted|final|ready|calibrated|operational|approved|forecast|real-time" .\agents.md`
- numbered `Get-Content` slices for `agents.md` line ranges around 550-715,
  730-850, 870-1030, and 1040-1250
- `scripts\audit_claim_language.py --scan-path agents.md`
- `.tmp_agents_claim_guard.csv`
- `.tmp_agents_claim_guard.json`
- `.tmp_agents_claim_guard.md`

The targeted guard initially reported 58 release-blocking findings in
`agents.md`.

## Changes

`agents.md` was edited to preserve agent workflow meaning while lowering
unbounded claim language:

- `operational namespaces` -> `scenario-runner namespaces`
- `Config validation guidance` -> `Config check guidance`
- `validates` prose -> `checks`, `schema-checks`, or `source-checks`
- `final-study` / `final` prose -> `study-closeout`, `closeout`, or
  `study-level`
- `accepted` / `acceptance` prose in claim contexts -> `signed off`,
  `signoff`, `source-backed`, or explicit schema/path wording
- `readiness` prose -> `status`, `pre-review status`, or
  `strategy-blocker-review` wording where not a literal artifact name
- `calibrated` prose -> `source-tuned` or `fit-to-observed-data` style wording
- `operational accuracy` -> `field-use accuracy`

The edits intentionally kept literal file/module names where those names are
repository APIs or artifact paths.

## Regenerated Artifacts

The full claim-language guard was regenerated after the `agents.md` edits:

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
.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path agents.md --output .tmp_agents_claim_guard.csv --manifest .tmp_agents_claim_guard.json --doc .tmp_agents_claim_guard.md
.\.venv\Scripts\python .\scripts\audit_claim_language.py
.\.venv\Scripts\python .\scripts\write_claim_alignment_review_packet.py
.\.venv\Scripts\python .\scripts\write_manuscript_report_decision_packet.py
```

Observed results before final dirty-classification refresh:

- Targeted `agents.md` guard after edits:
  - `blocking_finding_count`: 0
  - `release_blocked`: false
  - `claim_language_guard_ready`: true for that one scanned file
- Full claim-language guard after edits:
  - `blocking_finding_count`: 701
  - `release_blocked`: true
  - `final_study_ready`: false
- Claim-alignment review packet remained `row_count: 70` with
  `overclaim_candidate_count: 42`.
- Manuscript/report decision packet remained `row_count: 7` with
  `blocking_decision_count: 4`.

## Residual Risk

The full claim-language guard still blocks release with 701 findings across the
broader repository. After `README.md` and `agents.md` were reduced to zero
targeted blockers, the next leading source in the full guard output is
`plan.md`.
