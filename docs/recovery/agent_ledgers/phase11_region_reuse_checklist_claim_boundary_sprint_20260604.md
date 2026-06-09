# Phase 11 Region Reuse Checklist Claim-Boundary Sprint - 2026-06-04

## Scope

- Target: `docs/region_reuse_checklist.md`
- Purpose: remove release-blocking unbounded reuse/validation/acceptance wording while preserving the document as implementation guidance for adding a new region.
- Non-goal: no second case study was created, no region evidence was reviewed, and no final-study gate was closed.

## Edits

- Reworded the opening boundary so the checklist does not imply a second case study, field-fit evidence, or deployment routing authority.
- Replaced `revalidated` with `rechecked` for adapter/scenario contract changes.
- Reworded companion artifact requirements from validation outputs to benchmark/precheck outputs.
- Reworded formal acceptance artifact language to formal decision artifact and evidence-specific decision record language.
- Reworded the fixture coverage boundary so the synthetic fixture remains schema/adapter reuse support only.
- Retitled `Validation Commands` to `Check Commands`.
- Reworded CLI descriptions from `accept explicit` region arguments to `take explicit` region arguments.
- Reworded source-readiness manifest prose to source-request manifest prose.
- Reworded publication-bound/full-validation-ladder prose to external-release-bound/full-review-ladder prose.

## Verification

- `.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\docs\region_reuse_checklist.md --output .\.tmp_region_reuse_guard.csv --manifest .\.tmp_region_reuse_guard.json --doc .\.tmp_region_reuse_guard.md`
  - Result: exit code 0.
  - Focused blocker count: 0.
  - Focused bounded finding count: 2.
  - Focused `claim_language_guard_ready`: true.
- `Remove-Item -LiteralPath .\.tmp_region_reuse_guard.csv, .\.tmp_region_reuse_guard.json, .\.tmp_region_reuse_guard.md -ErrorAction SilentlyContinue`
  - Result: exit code 0.
- `.\.venv\Scripts\python .\scripts\audit_claim_language.py`
  - Result: exit code 0.
  - Full blocker count after this sprint: 241.
  - Full guard remains fail-closed: `claim_language_guard_ready=false`, `release_blocked=true`, `final_study_ready=false`.
- `.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py`
  - Result: exit code 0.
  - Classified path count: 435.
  - Unclassified path count: 0.
- `.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD CLAIM LANGUAGE GUARD TESTS PASSED ===`.
- `.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD PLAN AUDIT TESTS PASSED ===`.
- CSV check:
  - `docs/region_reuse_checklist.md` release blockers: 0.
  - Top remaining blocker sources after this sprint:
    - `docs/formal_acceptance_artifact_guard.md`: 8.
    - `data/manifests/experiment_statistical_analysis_plan.json`: 7.
    - `docs/parameter_source_decision_packet.md`: 7.
    - `docs/rail_source_decision_packet.md`: 6.
    - `docs/experiment_strategy_readiness_packet.md`: 6.
    - `docs/route_road_evidence_exposure.md`: 6.
    - `docs/parameter_source_readiness_packet.md`: 6.
    - `docs/manuscript_report_decision_packet.md`: 6.
- `git diff --check -- .\docs\region_reuse_checklist.md .\data\validation\claim_language_guard.csv .\data\validation\claim_language_guard_manifest.json .\docs\claim_language_guard.md .\data\validation\dirty_worktree_classification.csv .\data\validation\dirty_worktree_classification_manifest.json .\docs\dirty_worktree_classification.md`
  - Result: exit code 0.
  - Output included only an LF-to-CRLF warning for `docs/region_reuse_checklist.md`.
