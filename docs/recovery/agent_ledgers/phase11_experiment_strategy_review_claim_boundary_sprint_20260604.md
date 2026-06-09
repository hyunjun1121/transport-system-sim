# Phase 11 Experiment Strategy Review Claim-Boundary Sprint - 2026-06-04

## Scope

- Source: `src/realworld/experiment_strategy_readiness_packet.py`
- Script: `scripts/write_experiment_strategy_readiness_packet.py`
- Test: `tests/test_realworld_experiment_strategy_readiness_packet.py`
- Generated targets:
  - `data/manifests/experiment_strategy_readiness_packet.csv`
  - `data/manifests/experiment_strategy_readiness_manifest.json`
  - `docs/experiment_strategy_readiness_packet.md`
- Purpose: remove release-blocking unbounded readiness, final, accepted, and validation wording from the experiment strategy packet while preserving its fail-closed experiment-gate boundary.
- Non-goal: no experiment acceptance record was created, no full-pilot output was promoted, and no experiment gate was closed.

## Edits

- Reworded displayed title from `Experiment Strategy Readiness Packet` to `Experiment Strategy Review Packet`.
- Reworded packet scope from strategy-readiness/publication-readiness language to strategy-review/publication-gate boundary language.
- Reworded the Markdown section heading from `Readiness Rows` to `Strategy Review Rows`.
- Reworded review items from accepting full outputs and final decisions to promoting outputs only after a formal experiment decision record.
- Reworded reviewer actions from accepted/final result scope language to selected run profile and release-scope result set language.
- Reworded graph/input dependency actions from accepted upstream gates to unresolved upstream gates and selected graph method.
- Reworded formal experiment acceptance prose in generated evidence detail to formal experiment decision record prose.
- Updated the CLI help text and tests to match the new display title and strategy-review wording.

## Verification

- `.\.venv\Scripts\python .\scripts\write_experiment_strategy_readiness_packet.py`
  - Result: exit code 0.
  - Output summary included `row_count: 9`, `blocking_request_count: 4`, `human_review_request_count: 5`, `publication_ready: false`, and `can_mark_complete: false`.
- `.\.venv\Scripts\python .\tests\test_realworld_experiment_strategy_readiness_packet.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD EXPERIMENT STRATEGY REVIEW TESTS PASSED ===`.
- `.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\docs\experiment_strategy_readiness_packet.md --scan-path .\data\manifests\experiment_strategy_readiness_manifest.json --output .\data\validation\tmp_claim_language_guard_experiment_strategy.csv --manifest .\data\validation\tmp_claim_language_guard_experiment_strategy_manifest.json --doc .\docs\tmp_claim_language_guard_experiment_strategy.md`
  - Result: exit code 0.
  - Focused blocker count: 0.
  - Focused bounded finding count: 2.
  - Focused `claim_language_guard_ready`: true.
- `Remove-Item -LiteralPath .\data\validation\tmp_claim_language_guard_experiment_strategy.csv, .\data\validation\tmp_claim_language_guard_experiment_strategy_manifest.json, .\docs\tmp_claim_language_guard_experiment_strategy.md -ErrorAction Stop`
  - Result: exit code 0.
- `.\.venv\Scripts\python .\scripts\audit_claim_language.py`
  - Result: exit code 0.
  - Full blocker count after this sprint: 198.
  - Full guard remains fail-closed: `claim_language_guard_ready=false`, `release_blocked=true`, `final_study_ready=false`.
- `.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py`
  - Result: exit code 0.
  - Classified path count: 451.
  - Unclassified path count: 0.
- `.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD CLAIM LANGUAGE GUARD TESTS PASSED ===`.
- `.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD PLAN AUDIT TESTS PASSED ===`.
- CSV check:
  - `docs/experiment_strategy_readiness_packet.md` release blockers: 0.
  - `data/manifests/experiment_strategy_readiness_manifest.json` release blockers: 0.
  - Top remaining blocker sources after this sprint:
    - `docs/route_road_evidence_exposure.md`: 6.
    - `docs/graph_scale_review_packet.md`: 6.
    - `docs/parameter_source_readiness_packet.md`: 6.
    - `docs/manuscript_report_decision_packet.md`: 6.
    - `docs/source_provenance_manifest.md`: 5.
    - `docs/full_graph_runtime_readiness_packet.md`: 5.
    - `docs/crn_pairing_audit.md`: 5.
    - `docs/graph_scale_strategy_readiness_packet.md`: 5.
- `git diff --check -- .\src\realworld\experiment_strategy_readiness_packet.py .\scripts\write_experiment_strategy_readiness_packet.py .\tests\test_realworld_experiment_strategy_readiness_packet.py .\data\manifests\experiment_strategy_readiness_packet.csv .\data\manifests\experiment_strategy_readiness_manifest.json .\docs\experiment_strategy_readiness_packet.md .\data\validation\claim_language_guard.csv .\data\validation\claim_language_guard_manifest.json .\docs\claim_language_guard.md .\data\validation\dirty_worktree_classification.csv .\data\validation\dirty_worktree_classification_manifest.json .\docs\dirty_worktree_classification.md`
  - Result: exit code 0.
  - Output included only LF-to-CRLF warnings for `scripts/write_experiment_strategy_readiness_packet.py`, `src/realworld/experiment_strategy_readiness_packet.py`, and `tests/test_realworld_experiment_strategy_readiness_packet.py`.
