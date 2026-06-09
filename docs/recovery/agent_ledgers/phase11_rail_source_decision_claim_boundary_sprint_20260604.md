# Phase 11 Rail Source Decision Claim-Boundary Sprint - 2026-06-04

## Scope

- Source: `src/realworld/rail_source_decision_packet.py`
- Scripts:
  - `scripts/write_rail_source_decision_packet.py`
  - `scripts/write_rail_source_decision_action_ledger_template.py`
- Generated targets:
  - `data/rail/rail_source_decision_packet.csv`
  - `data/rail/rail_source_decision_manifest.json`
  - `docs/rail_source_decision_packet.md`
  - `data/rail/rail_source_decision_action_ledger_template.csv`
  - `data/rail/rail_source_decision_action_ledger_template_manifest.json`
  - `docs/rail_source_decision_action_ledger_template.md`
- Purpose: remove release-blocking unbounded wording from rail source-decision rows and the action-ledger template while preserving all rail source rows as reviewer-owned non-formal decisions.
- Non-goal: no rail timing evidence was created, no GTFS validation was approved, no rail service evidence gate was closed, and no study-closeout gate was closed.

## Edits

- Reworded rail source-decision scope from publication-readiness/final-study readiness language to publication-gate and study-closeout boundary language.
- Reworded action-ledger template scope, review items, and remaining blockers to avoid unbounded final-study wording.
- Reworded Markdown verdict labels for publication and study-closeout support while preserving the false manifest fields.
- Reworded rail source packet boundary from final-study/formal-acceptance gate wording to study-closeout/formal-decision gate wording.
- Reworded required reviewer action from final-study interpretation to study-closeout interpretation.
- Renamed exclusion option identifiers:
  - `exclude_timing_dependent_final_claims` -> `exclude_timing_dependent_release_scope_claims`
  - `exclude_capacity_dependent_final_claims` -> `exclude_capacity_dependent_release_scope_claims`
  - `exclude_availability_dependent_final_claims` -> `exclude_availability_dependent_release_scope_claims`
  - `exclude_from_final_claims` -> `exclude_from_release_scope_claims`
- Updated rail source-decision tests and action-ledger fixture choices to match the renamed release-scope option identifiers.

## Verification

- `.\.venv\Scripts\python .\scripts\write_rail_source_decision_packet.py`
  - Result: exit code 0.
  - Output summary included `row_count: 6`, `blocking_decision_count: 3`, `human_review_decision_count: 3`, `publication_ready: false`, and `final_study_ready: false`.
- `.\.venv\Scripts\python .\scripts\write_rail_source_decision_action_ledger_template.py`
  - Result: exit code 0.
  - Output summary included `row_count: 6`, `template_only: true`, `publication_ready: false`, and candidate options using `release_scope_claims`.
- `.\.venv\Scripts\python .\tests\test_realworld_rail_source_decision_packet.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD RAIL SOURCE DECISION TESTS PASSED ===`.
- `.\.venv\Scripts\python .\tests\test_realworld_rail_source_decision_action_ledger_template.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD RAIL SOURCE DECISION ACTION LEDGER TEMPLATE TESTS PASSED ===`.
- `.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\docs\rail_source_decision_packet.md --scan-path .\data\rail\rail_source_decision_manifest.json --scan-path .\docs\rail_source_decision_action_ledger_template.md --scan-path .\data\rail\rail_source_decision_action_ledger_template_manifest.json --output .\data\validation\tmp_claim_language_guard_rail_source.csv --manifest .\data\validation\tmp_claim_language_guard_rail_source_manifest.json --doc .\docs\tmp_claim_language_guard_rail_source.md`
  - Result: exit code 0.
  - Focused blocker count: 0.
  - Focused bounded finding count: 26.
  - Focused `claim_language_guard_ready`: true.
- `Remove-Item -LiteralPath .\data\validation\tmp_claim_language_guard_rail_source.csv, .\data\validation\tmp_claim_language_guard_rail_source_manifest.json, .\docs\tmp_claim_language_guard_rail_source.md -ErrorAction Stop`
  - Result: exit code 0.
- `.\.venv\Scripts\python .\scripts\audit_claim_language.py`
  - Result: exit code 0.
  - Full blocker count after this sprint: 206.
  - Full guard remains fail-closed: `claim_language_guard_ready=false`, `release_blocked=true`, `final_study_ready=false`.
- `.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py`
  - Result: exit code 0.
  - Classified path count: 444.
  - Unclassified path count: 0.
- `.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD CLAIM LANGUAGE GUARD TESTS PASSED ===`.
- `.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD PLAN AUDIT TESTS PASSED ===`.
- CSV check:
  - `docs/rail_source_decision_packet.md` release blockers: 0.
  - `docs/rail_source_decision_action_ledger_template.md` release blockers: 0.
  - Top remaining blocker sources after this sprint:
    - `docs/experiment_strategy_readiness_packet.md`: 6.
    - `docs/route_road_evidence_exposure.md`: 6.
    - `docs/parameter_source_readiness_packet.md`: 6.
    - `docs/manuscript_report_decision_packet.md`: 6.
    - `docs/graph_scale_review_packet.md`: 6.
    - `docs/graph_scale_strategy_readiness_packet.md`: 5.
    - `docs/accessibility_loss_analysis.md`: 5.
    - `docs/road_source_readiness_packet.md`: 5.
- `git diff --check -- .\src\realworld\rail_source_decision_packet.py .\scripts\write_rail_source_decision_packet.py .\tests\test_realworld_rail_source_decision_packet.py .\tests\test_realworld_rail_source_decision_action_ledger_template.py .\data\rail\rail_source_decision_packet.csv .\data\rail\rail_source_decision_manifest.json .\docs\rail_source_decision_packet.md .\data\rail\rail_source_decision_action_ledger_template.csv .\data\rail\rail_source_decision_action_ledger_template_manifest.json .\docs\rail_source_decision_action_ledger_template.md .\data\validation\claim_language_guard.csv .\data\validation\claim_language_guard_manifest.json .\docs\claim_language_guard.md .\data\validation\dirty_worktree_classification.csv .\data\validation\dirty_worktree_classification_manifest.json .\docs\dirty_worktree_classification.md`
  - Result: exit code 0.
  - Output included only LF-to-CRLF warnings for `scripts/write_rail_source_decision_packet.py`, `src/realworld/rail_source_decision_packet.py`, and `tests/test_realworld_rail_source_decision_packet.py`.
