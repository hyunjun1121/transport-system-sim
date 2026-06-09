# Phase 11 Parameter Source Decision Claim-Boundary Sprint - 2026-06-04

## Scope

- Source: `src/realworld/parameter_source_decision_packet.py`
- Generated targets:
  - `data/parameters/parameter_source_decision_packet.csv`
  - `data/parameters/parameter_source_decision_manifest.json`
  - `docs/parameter_source_decision_packet.md`
- Purpose: remove release-blocking unbounded final-claim wording from parameter source-decision rows while preserving all rows as reviewer-owned source decisions.
- Non-goal: no parameter acceptance table was created, no weak assumption was approved, and no final-study gate was closed.

## Edits

- Reworded the packet scope from accepted parameter calibration and publication-readiness approval language to approved-parameter-fitting and publication-gate boundary language.
- Reworded review items so retained weak assumptions require explicit reviewer decisions rather than accepted weak assumptions.
- Reworded audit follow-up from publication-readiness/final-study audits to publication/study-closeout audits.
- Reworded the Markdown boundary from final parameter claims and weak-parameter acceptance to release-scope parameter claims and formal weak-parameter decisions.
- Reworded required reviewer action from final-study interpretation to release-scope interpretation.
- Renamed candidate option `exclude_from_final_claims` to `exclude_from_release_scope_claims`.

## Verification

- `.\.venv\Scripts\python .\scripts\write_parameter_source_decision_packet.py`
  - Result: exit code 0.
  - Output summary included `row_count: 7`, `human_review_decision_count: 7`, `blocking_decision_count: 0`, `publication_ready: false`, and `can_mark_complete: false`.
- `.\.venv\Scripts\python .\tests\test_realworld_parameter_source_decision_packet.py`
  - First parallel attempt failed because the shipped-output comparison ran before the writer finished regenerating CSV output.
  - Sequential rerun result: exit code 0.
  - Output ended with `=== REALWORLD PARAMETER SOURCE DECISION TESTS PASSED ===`.
- `.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\docs\parameter_source_decision_packet.md --scan-path .\data\parameters\parameter_source_decision_manifest.json --output .\.tmp_parameter_source_decision_guard.csv --manifest .\.tmp_parameter_source_decision_guard.json --doc .\.tmp_parameter_source_decision_guard.md`
  - Result: exit code 0.
  - Focused blocker count: 0.
  - Focused bounded finding count: 10.
  - Focused `claim_language_guard_ready`: true.
- `Remove-Item -LiteralPath .\.tmp_parameter_source_decision_guard.csv, .\.tmp_parameter_source_decision_guard.json, .\.tmp_parameter_source_decision_guard.md -ErrorAction SilentlyContinue`
  - Result: exit code 0.
- `.\.venv\Scripts\python .\scripts\audit_claim_language.py`
  - Result: exit code 0.
  - Full blocker count after this sprint: 214.
  - Full guard remains fail-closed: `claim_language_guard_ready=false`, `release_blocked=true`, `final_study_ready=false`.
- `.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py`
  - Result: exit code 0.
  - Classified path count: 443.
  - Unclassified path count: 0.
- `.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD CLAIM LANGUAGE GUARD TESTS PASSED ===`.
- `.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD PLAN AUDIT TESTS PASSED ===`.
- CSV check:
  - `docs/parameter_source_decision_packet.md` release blockers: 0.
  - `data/parameters/parameter_source_decision_manifest.json` release blockers: 0.
  - Top remaining blocker sources after this sprint:
    - `docs/rail_source_decision_packet.md`: 6.
    - `docs/experiment_strategy_readiness_packet.md`: 6.
    - `docs/route_road_evidence_exposure.md`: 6.
    - `docs/parameter_source_readiness_packet.md`: 6.
    - `docs/manuscript_report_decision_packet.md`: 6.
    - `docs/graph_scale_review_packet.md`: 6.
    - `docs/source_provenance_manifest.md`: 5.
    - `docs/accessibility_loss_analysis.md`: 5.
- `git diff --check -- .\src\realworld\parameter_source_decision_packet.py .\data\parameters\parameter_source_decision_packet.csv .\data\parameters\parameter_source_decision_manifest.json .\docs\parameter_source_decision_packet.md .\data\validation\claim_language_guard.csv .\data\validation\claim_language_guard_manifest.json .\docs\claim_language_guard.md .\data\validation\dirty_worktree_classification.csv .\data\validation\dirty_worktree_classification_manifest.json .\docs\dirty_worktree_classification.md`
  - Result: exit code 0.
  - Output included only an LF-to-CRLF warning for `src/realworld/parameter_source_decision_packet.py`.
