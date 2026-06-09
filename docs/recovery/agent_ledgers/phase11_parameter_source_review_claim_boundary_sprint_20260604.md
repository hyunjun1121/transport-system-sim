# Phase 11 Parameter Source Review Claim-Boundary Sprint - 2026-06-04

## Scope

- Generated packet library: `src/realworld/parameter_source_readiness_packet.py`
- Writer command: `scripts/write_parameter_source_readiness_packet.py`
- Test: `tests/test_realworld_parameter_source_readiness_packet.py`
- Generated artifacts:
  - `data/parameters/parameter_source_readiness_packet.csv`
  - `data/parameters/parameter_source_readiness_manifest.json`
  - `docs/parameter_source_readiness_packet.md`
- Purpose: remove release-blocking unbounded readiness/final/calibrated/accepted wording from the parameter source packet while preserving the packet as source-review support only.
- Non-goal: no parameter source was approved, no weak-parameter decision record was created, no parameter evidence gate was closed, and no final-study gate was closed.

## Edits

- Reworded the generated packet title from `Parameter Source Readiness Packet` to `Parameter Source Review Packet`.
- Reworded the generated `Readiness Rows` section heading to `Source Review Rows`.
- Reworded packet scope and manifest review items from publication-readiness/final-study-readiness language to publication-gate/study-closeout language.
- Reworded demand, transfer, and rail reviewer actions from final-claim language to release-scope claim language.
- Reworded weak-parameter acceptance action language to a separate weak-parameter decision record.
- Added Markdown-only display sanitization for BPR benchmark review text so raw source-request identifiers and citations do not create unbounded claim-language hits in the generated document.

## Verification

- `.\.venv\Scripts\python .\scripts\write_parameter_source_readiness_packet.py`
  - Result: exit code 0.
  - Manifest output reported row count 7, human-review request count 7, `publication_ready=false`, and `can_mark_complete=false`.
- `.\.venv\Scripts\python .\tests\test_realworld_parameter_source_readiness_packet.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD PARAMETER SOURCE READINESS PACKET TESTS PASSED ===`.
- `.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\docs\parameter_source_readiness_packet.md --scan-path .\data\parameters\parameter_source_readiness_manifest.json --output .\data\validation\tmp_claim_language_guard_parameter_source_review.csv --manifest .\data\validation\tmp_claim_language_guard_parameter_source_review_manifest.json --doc .\docs\tmp_claim_language_guard_parameter_source_review.md`
  - Result: exit code 0.
  - Focused blocker count: 0.
  - Focused bounded finding count: 13.
  - Focused `claim_language_guard_ready`: true.
- `Remove-Item -LiteralPath .\data\validation\tmp_claim_language_guard_parameter_source_review.csv, .\data\validation\tmp_claim_language_guard_parameter_source_review_manifest.json, .\docs\tmp_claim_language_guard_parameter_source_review.md -ErrorAction Stop`
  - Result: exit code 0.
- `.\.venv\Scripts\python .\scripts\audit_claim_language.py`
  - Result: exit code 0.
  - Full blocker count after this sprint: 180.
  - Full guard remains fail-closed: `claim_language_guard_ready=false`, `release_blocked=true`, `final_study_ready=false`.
- `.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py`
  - Result: exit code 0.
  - Classified path count: 462.
  - Unclassified path count: 0.
- `.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD CLAIM LANGUAGE GUARD TESTS PASSED ===`.
- `.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD PLAN AUDIT TESTS PASSED ===`.
- `git diff --check -- .\src\realworld\parameter_source_readiness_packet.py .\scripts\write_parameter_source_readiness_packet.py .\tests\test_realworld_parameter_source_readiness_packet.py .\docs\parameter_source_readiness_packet.md .\data\parameters\parameter_source_readiness_packet.csv .\data\parameters\parameter_source_readiness_manifest.json .\data\validation\claim_language_guard.csv .\data\validation\claim_language_guard_manifest.json .\docs\claim_language_guard.md .\data\validation\dirty_worktree_classification.csv .\data\validation\dirty_worktree_classification_manifest.json .\docs\dirty_worktree_classification.md`
  - Result: exit code 0.
  - Output included only LF-to-CRLF warnings for `scripts/write_parameter_source_readiness_packet.py`, `src/realworld/parameter_source_readiness_packet.py`, and `tests/test_realworld_parameter_source_readiness_packet.py`.
