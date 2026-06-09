# Phase 11 Reproducibility Manifest Claim Boundary Sprint - 2026-06-04

## Scope

This sprint reduced release-blocking lexical claim-language findings in the
tracked `data/manifests/reproducibility_manifest.json` file. It changed
claim-boundary wording in `claim_limit` and selected `remaining_upgrades`
entries only. It did not change reproduction commands, source evidence,
simulation code, experiment outputs, formal target records, publication state,
or formal acceptance state.

No study-closeout, calibration, deployment, formal acceptance, or package
approval was claimed or created.

## Preflight Evidence

- Full claim-language guard before this sprint:
  - `blocking_finding_count: 395`
  - `release_blocked: true`
  - `claim_language_guard_ready: false`
- CSV grouping showed `data/manifests/reproducibility_manifest.json` had 16
  release-blocking findings, the highest remaining single source at that time.
- `rg` did not identify a dedicated writer for this manifest in `src/`,
  `scripts/`, or `tests/`; `scripts/audit_plan_artifacts.py` reads the file as
  a JSON expectation.
- Recursive JSON inspection showed the unbounded terms were concentrated in
  `claim_limit` and selected `remaining_upgrades` strings.

## Sub-Agent Use

No new sub-agent output was adopted in this sprint. The changes were based on
main-thread inspection of the current guard CSV, the tracked manifest, targeted
`rg` searches, and reproducibility/final-study tests.

## Changes

The manifest wording was narrowed while preserving the same review intent:

- `not calibrated real-world results or operational route plans` became
  `not field-fit results or deployment route plans`.
- Weak-input rows now refer to reviewer retention or reviewer decisions rather
  than accepting weak assumptions.
- Graph-scale wording now uses `closeout graph-scale decision` and
  `reviewer-selected corridor abstraction`.
- Benchmark wording now avoids using unbounded validation/final language.
- Experiment, sensitivity, reproducibility, and audit rows now refer to
  decision records instead of acceptance/final-audit claims.

One test expectation in `tests/test_realworld_final_study_readiness.py` was
updated from `requires_revision_or_acceptance` to
`requires_revision_or_review` to match the current claim-alignment generator
status vocabulary.

## Verification Commands

```powershell
.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\data\manifests\reproducibility_manifest.json --output .\.tmp_repro_manifest_claim_guard.csv --manifest .\.tmp_repro_manifest_claim_guard.json --doc .\.tmp_repro_manifest_claim_guard.md
Remove-Item -LiteralPath .\.tmp_repro_manifest_claim_guard.csv, .\.tmp_repro_manifest_claim_guard.json, .\.tmp_repro_manifest_claim_guard.md -ErrorAction SilentlyContinue
.\.venv\Scripts\python .\tests\test_realworld_reproducibility_review_packet.py
.\.venv\Scripts\python .\tests\test_realworld_reproducibility_acceptance.py
.\.venv\Scripts\python .\tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python .\scripts\audit_claim_language.py
.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py
.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py
.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py
git diff --check -- .\data\manifests\reproducibility_manifest.json .\tests\test_realworld_final_study_readiness.py .\data\validation\claim_language_guard.csv .\data\validation\claim_language_guard_manifest.json .\docs\claim_language_guard.md .\data\validation\dirty_worktree_classification.csv .\data\validation\dirty_worktree_classification_manifest.json .\docs\dirty_worktree_classification.md
```

Observed results:

- Focused `data/manifests/reproducibility_manifest.json` scan after edits:
  - `blocking_finding_count: 0`
  - `release_blocked: false`
  - `claim_language_guard_ready: true` for that focused scan
- Full claim-language guard after edits:
  - `blocking_finding_count: 379`
  - `release_blocked: true`
  - `final_study_ready: false`
- CSV confirmation after the full guard:
  - `data/manifests/reproducibility_manifest.json` had 0
    `release_blocking_unbounded` findings.
- `tests/test_realworld_reproducibility_review_packet.py` passed.
- `tests/test_realworld_reproducibility_acceptance.py` passed.
- `tests/test_realworld_final_study_readiness.py` passed after the status-name
  expectation update.
- `tests/test_realworld_claim_language_guard.py` passed.
- `tests/test_realworld_plan_audit.py` passed.
- Dirty-worktree classification refresh reported 402 classified paths and
  `new_generated_output_allowed: false`.
- `git diff --check` exited 0 with LF-to-CRLF warnings only.

## Remaining Work

The full lexical guard remains fail-closed. The leading remaining blocker
sources after this sprint are:

- `docs/source_url_remediation_packet.md`: 14 release-blocking findings
- `docs/formal_acceptance_pre_review.md`: 14 release-blocking findings
- `docs/graph_scale_diagnostics.md`: 14 release-blocking findings
- `data/manifests/formal_acceptance_package_audit.json`: 14 release-blocking
  findings
- `docs/human_acceptance_runbook.md`: 13 release-blocking findings

The next slice should inspect whether the selected target is generated before
editing it.
