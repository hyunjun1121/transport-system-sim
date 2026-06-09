# Phase 11 Road Source Review Claim-Boundary Sprint - 2026-06-04

## Scope

- Generated packet library: `src/realworld/road_source_readiness_packet.py`
- Writer command: `scripts/write_road_source_readiness_packet.py`
- Test: `tests/test_realworld_road_source_readiness_packet.py`
- Generated artifacts:
  - `data/road/road_source_readiness_packet.csv`
  - `data/road/road_source_readiness_manifest.json`
- Manual document: `docs/road_source_readiness_packet.md`
- Purpose: remove release-blocking unbounded road source readiness, accepted, calibrated, and final wording while preserving the packet as road source review support only.
- Non-goal: no road source was acquired, no reviewed road-class override table was created, no road evidence or road application gate was closed, no formal decision record was created, and no final-study gate was closed.

## Edits

- Reworded reader-facing title from road source readiness to road source review.
- Reworded generated scope text from source-readiness to source review.
- Reworded the generated rows section from readiness rows to review rows.
- Reworded review items and required reviewer actions from accepted/calibrated/final wording to recorded, reviewed, bounded, or release-scope wording.
- Reworded the disruption-scenario action from accepting scenario-only treatment to recording scenario-only treatment.
- Kept internal file names, CSV column names, and status identifiers stable for compatibility with existing review/audit code.
- Kept `publication_ready=false`, `can_mark_complete=false`, `road_evidence_gate_closure_candidate_count=0`, and `road_application_gate_closure_candidate_count=0` intact.

## Verification

- `.\.venv\Scripts\python .\scripts\write_road_source_readiness_packet.py`
  - Result: exit code 0.
  - Manifest output reported row count 5, `publication_ready=false`, `can_mark_complete=false`, `road_evidence_gate_closure_candidate_count=0`, `road_application_gate_closure_candidate_count=0`, and `blocking_request_count=2`.
- `.\.venv\Scripts\python .\tests\test_realworld_road_source_readiness_packet.py`
  - First parallel run during regeneration: exit code 1 because the test read the shipped manifest before the writer dependency had completed. This run was not used as pass evidence.
  - Sequential rerun after regeneration: exit code 0.
  - Output ended with `=== REALWORLD ROAD SOURCE READINESS PACKET TESTS PASSED ===`.
- `.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\docs\road_source_readiness_packet.md --scan-path .\data\road\road_source_readiness_manifest.json --output .\data\validation\tmp_claim_language_guard_road_source_readiness.csv --manifest .\data\validation\tmp_claim_language_guard_road_source_readiness_manifest.json --doc .\docs\tmp_claim_language_guard_road_source_readiness.md`
  - First result after the title/scope edit: exit code 0 with focused blocker count 1 at `data/road/road_source_readiness_manifest.json:42` for `final`.
  - Self-refine patch reworded `before final claims` to `before release-scope claims`.
  - Final focused result: exit code 0, focused blocker count 0, focused bounded finding count 12, and focused `claim_language_guard_ready=true`.
- `Remove-Item -LiteralPath .\data\validation\tmp_claim_language_guard_road_source_readiness.csv, .\data\validation\tmp_claim_language_guard_road_source_readiness_manifest.json, .\docs\tmp_claim_language_guard_road_source_readiness.md -ErrorAction Stop`
  - Result: exit code 0.
- `.\.venv\Scripts\python .\scripts\audit_claim_language.py`
  - Result: exit code 0.
  - Full blocker count after this sprint: 149.
  - Full guard remains fail-closed: `claim_language_guard_ready=false`, `release_blocked=true`, `final_study_ready=false`.
- `.\.venv\Scripts\python -m py_compile .\src\realworld\road_source_readiness_packet.py .\scripts\write_road_source_readiness_packet.py`
  - Result: exit code 0.
- `.\.venv\Scripts\python .\tests\test_realworld_road_source_readiness_packet.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD ROAD SOURCE READINESS PACKET TESTS PASSED ===`.
- `.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD CLAIM LANGUAGE GUARD TESTS PASSED ===`.
- `.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py`
  - First result after guard regeneration: exit code 1 because `dirty_worktree_classification` was stale after new edits.
  - After rerunning dirty worktree classification: exit code 0.
  - Output ended with `=== REALWORLD PLAN AUDIT TESTS PASSED ===`.
- `.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py`
  - Result before adding this ledger: exit code 0.
  - Classified path count before adding this ledger: 488.
  - Result after adding this ledger: exit code 0.
  - Classified path count after adding this ledger: 489.
  - Unclassified path count: 0.
  - `destructive_cleanup_allowed=false`.
- `Test-Path` check for the three focused-guard temporary files:
  - Result: exit code 0.
  - All three paths returned `Exists=False`.
- `git diff --check -- .\src\realworld\road_source_readiness_packet.py .\scripts\write_road_source_readiness_packet.py .\tests\test_realworld_road_source_readiness_packet.py .\data\road\road_source_readiness_packet.csv .\data\road\road_source_readiness_manifest.json .\docs\road_source_readiness_packet.md .\data\validation\claim_language_guard.csv .\data\validation\claim_language_guard_manifest.json .\docs\claim_language_guard.md .\data\validation\dirty_worktree_classification.csv .\data\validation\dirty_worktree_classification_manifest.json .\docs\dirty_worktree_classification.md`
  - Result: exit code 0.
  - Output included only LF-to-CRLF warnings for `scripts/write_road_source_readiness_packet.py`, `src/realworld/road_source_readiness_packet.py`, and `tests/test_realworld_road_source_readiness_packet.py`.

## Claim Boundary

This sprint only reduces lexical release-blocking wording in the road source review packet. It does not acquire road evidence, does not create a reviewed override table, does not apply road-class overrides, does not close road evidence, cached-road, parameter, validation, publication, or formal acceptance gates, and does not change the project-wide `final_study_ready=false` state.

## Remaining Work

- Full claim-language guard remains blocked with 149 release-blocking unbounded findings.
- Current top blocker groups after this sprint include `data/manifests/experiment_package_review_manifest.json`, `data/manifests/figure_table_review_manifest.json`, `docs/accessibility_loss_analysis.md`, `docs/road_source_decision_packet.md`, `docs/source_provenance_manifest.md`, `docs/crn_pairing_audit.md`, and `docs/pilot_region_data_card.md`.
- The dirty worktree remains large; cleanup is not allowed without owner and package decisions.
