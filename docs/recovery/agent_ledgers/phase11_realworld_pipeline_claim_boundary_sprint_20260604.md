# Phase 11 Realworld Pipeline Claim Boundary Sprint - 2026-06-04

## Scope

This sprint reduced release-blocking lexical claim-language findings in
`docs/realworld_pipeline.md`. It changed document wording only. It did not
change simulation code, experiment outputs, cached source inputs, acceptance
state, publication state, or any formal review gate.

No study-closeout, calibration, deployment, formal acceptance, or package
approval was claimed or created.

## Preflight Evidence

- Full claim-language guard before this sprint:
  - `blocking_finding_count: 494`
  - `release_blocked: true`
  - `claim_language_guard_ready: false`
- `docs/realworld_pipeline.md` had 27 release-blocking findings and was the
  leading blocker source after the prior dirty-worktree Markdown sprint.
- `rg` found references to `docs/realworld_pipeline.md` in the plan audit and
  documentation, but no generator script that rewrites the document. The file
  was treated as hand-maintained Markdown.

## Sub-Agent Use

No new sub-agent output was adopted in this sprint. The changes were based on
main-thread inspection of the current guard CSV, the Markdown file, `rg`
references, and focused claim-language scans.

## Changes

The wording was narrowed to avoid implying approval-like status while keeping
the same technical meaning:

- `readiness validation` became `input-readiness checks`, then `input checks`.
- `Validated records` became `Record classes`.
- `simulator-ready` became `simulator-compatible`.
- `route-readiness checks` became `route-check screens`.
- `table validation` became `table schema checks`.
- `Offline Validation` became `Offline Test Commands`.
- `validates it` became `checks it`.
- `reviewed and validated` became `reviewed and checked`.
- `accepted proxies` became `reviewed proxies`.
- `road-calibration claims` became `road-evidence claims`.
- Strategy/readiness packet prose was renamed to blocker/review worksheets while
  preserving literal file-path references.
- The avoid-list examples were changed so the guard does not treat the list as
  an unbounded claim.
- `If readiness fails` became `If the graph check fails`.

## Verification Commands

```powershell
.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\docs\realworld_pipeline.md --output .\.tmp_realworld_pipeline_claim_guard.csv --manifest .\.tmp_realworld_pipeline_claim_guard.json --doc .\.tmp_realworld_pipeline_claim_guard.md
Remove-Item -LiteralPath .\.tmp_realworld_pipeline_claim_guard.csv, .\.tmp_realworld_pipeline_claim_guard.json, .\.tmp_realworld_pipeline_claim_guard.md -ErrorAction SilentlyContinue
.\.venv\Scripts\python .\scripts\audit_claim_language.py
.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py
.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py
.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py
git diff --check -- .\docs\realworld_pipeline.md .\data\validation\claim_language_guard.csv .\data\validation\claim_language_guard_manifest.json .\docs\claim_language_guard.md
```

Observed results:

- Focused `docs/realworld_pipeline.md` scan after edits:
  - `blocking_finding_count: 0`
  - `release_blocked: false`
  - `claim_language_guard_ready: true` for that focused scan
- Full claim-language guard after edits:
  - `blocking_finding_count: 467`
  - `release_blocked: true`
  - `final_study_ready: false`
- `docs/realworld_pipeline.md` now has 0 release-blocking findings.
- `tests/test_realworld_claim_language_guard.py` passed.
- `tests/test_realworld_plan_audit.py` passed.
- Dirty-worktree classification refresh after the edit reported 386 classified
  paths and `new_generated_output_allowed: false`.
- `git diff --check` exited 0 with LF-to-CRLF warnings only.

## Remaining Work

The full lexical guard remains fail-closed. The leading remaining blocker
sources after this sprint are:

- `docs/plan_completion_audit.md`: 26
- `data/manifests/acceptance_orchestration_manifest.json`: 21
- `docs/claim_alignment_review_packet.md`: 21
- `data/manifests/reproducibility_manifest.json`: 16
- `docs/source_url_remediation_packet.md`: 14
- `docs/graph_scale_diagnostics.md`: 14
- `data/manifests/formal_acceptance_package_audit.json`: 14
- `docs/formal_acceptance_pre_review.md`: 14

The next slice should start with `docs/plan_completion_audit.md` only after
inspecting whether it is generated and which writer owns the repeated terms.
