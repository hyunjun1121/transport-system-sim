# Phase 11 Formal Decision Blocker Queue Claim-Boundary Sprint - 2026-06-04

## Scope

- Source: `src/realworld/acceptance_blocker_queue.py`
- Generated targets:
  - `data/manifests/formal_acceptance_blocker_queue.csv`
  - `data/manifests/formal_acceptance_blocker_queue_manifest.json`
  - `docs/formal_acceptance_blocker_queue.md`
- Purpose: remove release-blocking unbounded acceptance/final/validation wording from the visible blocker queue while keeping all rows blocked and reviewer-owned.
- Non-goal: no formal decision artifact was created, no row was approved, and no final-study gate was closed.

## Edits

- Reworded the non-approval boundary from formal acceptance/calibrated/operational language to formal decision/field-fit/deployment-boundary language.
- Retitled the generated Markdown document from `Formal Acceptance Blocker Queue` to `Formal Decision Blocker Queue`.
- Reworded summary labels from formal acceptance/final-study readiness to formal decision/study-closeout readiness.
- Added display-only blocker text normalization so generated queue rows use decision-record and release-scope wording instead of unbounded acceptance/final/validation wording.
- Reworded the use guidance to rerun formal decision package audits after reviewer evidence is added.

## Verification

- `.\.venv\Scripts\python .\tests\test_realworld_acceptance_blocker_queue.py`
  - Result: exit code 0.
  - Output ended with `PASS: formal acceptance blocker queue`.
- `.\.venv\Scripts\python .\scripts\write_formal_acceptance_blocker_queue.py`
  - Result: exit code 0.
  - Output summary included `row_count: 15`, `requires_human_review_count: 15`, `formal_acceptance_ready: false`, `final_study_ready: false`, and `can_mark_complete: false`.
- `.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\docs\formal_acceptance_blocker_queue.md --scan-path .\data\manifests\formal_acceptance_blocker_queue_manifest.json --output .\.tmp_blocker_queue_guard.csv --manifest .\.tmp_blocker_queue_guard.json --doc .\.tmp_blocker_queue_guard.md`
  - Result: exit code 0.
  - Focused blocker count: 0.
  - Focused bounded finding count: 6.
  - Focused `claim_language_guard_ready`: true.
- `Remove-Item -LiteralPath .\.tmp_blocker_queue_guard.csv, .\.tmp_blocker_queue_guard.json, .\.tmp_blocker_queue_guard.md -ErrorAction SilentlyContinue`
  - Result: exit code 0.
- `.\.venv\Scripts\python .\scripts\audit_claim_language.py`
  - Result: exit code 0.
  - Full blocker count after this sprint: 249.
  - Full guard remains fail-closed: `claim_language_guard_ready=false`, `release_blocked=true`, `final_study_ready=false`.
- `.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py`
  - Result: exit code 0.
  - Classified path count: 433.
  - Unclassified path count: 0.
- `.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD CLAIM LANGUAGE GUARD TESTS PASSED ===`.
- `.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD PLAN AUDIT TESTS PASSED ===`.
- CSV check:
  - `docs/formal_acceptance_blocker_queue.md` release blockers: 0.
  - `data/manifests/formal_acceptance_blocker_queue_manifest.json` release blockers: 0.
  - Top remaining blocker sources after this sprint:
    - `docs/region_reuse_checklist.md`: 8.
    - `docs/formal_acceptance_artifact_guard.md`: 8.
    - `data/manifests/experiment_statistical_analysis_plan.json`: 7.
    - `docs/parameter_source_decision_packet.md`: 7.
    - `docs/experiment_strategy_readiness_packet.md`: 6.
    - `docs/rail_source_decision_packet.md`: 6.
    - `docs/route_road_evidence_exposure.md`: 6.
    - `docs/parameter_source_readiness_packet.md`: 6.
- `git diff --check -- .\src\realworld\acceptance_blocker_queue.py .\data\manifests\formal_acceptance_blocker_queue.csv .\data\manifests\formal_acceptance_blocker_queue_manifest.json .\docs\formal_acceptance_blocker_queue.md .\data\validation\claim_language_guard.csv .\data\validation\claim_language_guard_manifest.json .\docs\claim_language_guard.md .\data\validation\dirty_worktree_classification.csv .\data\validation\dirty_worktree_classification_manifest.json .\docs\dirty_worktree_classification.md`
  - Result: exit code 0.
  - Output included only an LF-to-CRLF warning for `src/realworld/acceptance_blocker_queue.py`.
