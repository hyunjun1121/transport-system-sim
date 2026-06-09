# Phase 11 Experiment Statistical Plan Claim-Boundary Sprint - 2026-06-04

## Scope

- Source: `src/realworld/experiment_statistical_plan.py`
- Generated targets:
  - `data/manifests/experiment_statistical_analysis_plan.json`
  - `docs/experiment_statistical_analysis_plan.md`
- Purpose: remove release-blocking unbounded accepted/final wording from the statistical-analysis plan while preserving it as a pre-review planning artifact.
- Non-goal: no experiment decision record was created, no multiplicity procedure was selected, and no final-study gate was closed.

## Edits

- Reworded the claim boundary from experiment acceptance/validation/final-study language to experiment decision artifact, CRN verification, multiple-comparison selection, and study-closeout language.
- Reworded the secondary-comparison boundary so reviewers select comparison families rather than accept them.
- Reworded review items from formal experiment acceptance and accepted primary metrics to formal experiment decision and reviewer-selected primary metrics.
- Reworded row-count review actions from before acceptance to before review closure.
- Reworded primary contrast review action to reviewer-selected primary contrast language.
- Reworded replication adequacy review action from final claims to release-scope claims.
- Reworded multiplicity action from accepting a procedure to selecting a procedure.
- Reworded the formal experiment record action to formal experiment decision record language.

## Verification

- `.\.venv\Scripts\python .\tests\test_realworld_experiment_statistical_plan.py`
  - Result: exit code 0.
  - Output ended with `PASS: experiment statistical analysis plan`.
- `.\.venv\Scripts\python .\scripts\write_experiment_statistical_plan.py`
  - Result: exit code 0.
  - Output summary included `blocking_check_count: 1`, `needs_human_review_count: 4`, `acceptance_ready: false`, and `statistical_plan_ready_for_review: false`.
- `.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\docs\experiment_statistical_analysis_plan.md --scan-path .\data\manifests\experiment_statistical_analysis_plan.json --output .\.tmp_experiment_stat_plan_guard.csv --manifest .\.tmp_experiment_stat_plan_guard.json --doc .\.tmp_experiment_stat_plan_guard.md`
  - Result: exit code 0.
  - Focused blocker count: 0.
  - Focused bounded finding count: 23.
  - Focused `claim_language_guard_ready`: true.
- `Remove-Item -LiteralPath .\.tmp_experiment_stat_plan_guard.csv, .\.tmp_experiment_stat_plan_guard.json, .\.tmp_experiment_stat_plan_guard.md -ErrorAction SilentlyContinue`
  - Result: exit code 0.
- `.\.venv\Scripts\python .\scripts\audit_claim_language.py`
  - Result: exit code 0.
  - Full blocker count after this sprint: 221.
  - Full guard remains fail-closed: `claim_language_guard_ready=false`, `release_blocked=true`, `final_study_ready=false`.
- `.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py`
  - Result: exit code 0.
  - Classified path count: 441.
  - Unclassified path count: 0.
- `.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD CLAIM LANGUAGE GUARD TESTS PASSED ===`.
- `.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD PLAN AUDIT TESTS PASSED ===`.
- CSV check:
  - `docs/experiment_statistical_analysis_plan.md` release blockers: 0.
  - `data/manifests/experiment_statistical_analysis_plan.json` release blockers: 0.
  - Top remaining blocker sources after this sprint:
    - `docs/parameter_source_decision_packet.md`: 7.
    - `docs/experiment_strategy_readiness_packet.md`: 6.
    - `docs/rail_source_decision_packet.md`: 6.
    - `docs/route_road_evidence_exposure.md`: 6.
    - `docs/parameter_source_readiness_packet.md`: 6.
    - `docs/manuscript_report_decision_packet.md`: 6.
    - `docs/graph_scale_review_packet.md`: 6.
    - `docs/crn_pairing_audit.md`: 5.
- `git diff --check -- .\src\realworld\experiment_statistical_plan.py .\docs\experiment_statistical_analysis_plan.md .\data\manifests\experiment_statistical_analysis_plan.json .\data\validation\claim_language_guard.csv .\data\validation\claim_language_guard_manifest.json .\docs\claim_language_guard.md .\data\validation\dirty_worktree_classification.csv .\data\validation\dirty_worktree_classification_manifest.json .\docs\dirty_worktree_classification.md`
  - Result: exit code 0.
  - Output included only an LF-to-CRLF warning for `src/realworld/experiment_statistical_plan.py`.
