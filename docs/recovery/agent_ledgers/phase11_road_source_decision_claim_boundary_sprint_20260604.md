# Phase 11 Road Source Decision Claim-Boundary Sprint - 2026-06-04

## Scope

- Generated packet library: `src/realworld/road_source_decision_packet.py`
- Writer command: `scripts/write_road_source_decision_packet.py`
- Test: `tests/test_realworld_road_source_decision_packet.py`
- Generated artifacts:
  - `data/road/road_source_decision_packet.csv`
  - `data/road/road_source_decision_manifest.json`
- Manual document: `docs/road_source_decision_packet.md`
- Purpose: remove release-blocking unbounded final, validated, calibrated, and accepted wording while preserving the packet as road source decision review support only.
- Non-goal: no road source decision was accepted, no road evidence was created, no reviewed road-class override table was created, no cached OSM input gate was closed, no publication gate was closed, and no final-study gate was closed.

## Edits

- Reworded scope text from accepted road calibration to road-input tuning evidence.
- Reworded review items from road calibration, validation, and final-study audit wording to bounded road-input, benchmark, publication, and study-scope audit wording.
- Reworded boundary text from calibrate/accept wording to tune/record wording.
- Reworded decision options from `accept_*`, `*_calibrated_*`, and `*_final_claims` strings to `record_*`, `*_bounded_*`, and `*_release_scope_claims` strings.
- Kept internal file names, CSV column names, and status identifiers stable for compatibility with existing review/audit code.
- Kept `publication_ready=false`, `can_mark_complete=false`, `cached_osm_input_gate_closure_candidate_count=0`, `road_evidence_gate_closure_candidate_count=0`, `road_application_gate_closure_candidate_count=0`, and `acceptance_gate_closure_candidate_count=0` intact.

## Verification

- `.\.venv\Scripts\python .\scripts\write_road_source_decision_packet.py`
  - Result: exit code 0.
  - Manifest output reported row count 5, `publication_ready=false`, `can_mark_complete=false`, all four gate closure candidate counts as 0, `blocking_decision_count=2`, and `human_review_decision_count=3`.
- `.\.venv\Scripts\python .\tests\test_realworld_road_source_decision_packet.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD ROAD SOURCE DECISION TESTS PASSED ===`.
- `.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\docs\road_source_decision_packet.md --scan-path .\data\road\road_source_decision_manifest.json --output .\data\validation\tmp_claim_language_guard_road_source_decision.csv --manifest .\data\validation\tmp_claim_language_guard_road_source_decision_manifest.json --doc .\docs\tmp_claim_language_guard_road_source_decision.md`
  - First result after the option/action edit: exit code 0 with focused blocker count 1 at `data/road/road_source_decision_manifest.json:56` for `validated`.
  - Self-refine patch reworded `validation` to `benchmark` in the review item.
  - Final focused result: exit code 0, focused blocker count 0, focused bounded finding count 6, and focused `claim_language_guard_ready=true`.
- `Remove-Item -LiteralPath .\data\validation\tmp_claim_language_guard_road_source_decision.csv, .\data\validation\tmp_claim_language_guard_road_source_decision_manifest.json, .\docs\tmp_claim_language_guard_road_source_decision.md -ErrorAction Stop`
  - Result: exit code 0.
- `.\.venv\Scripts\python .\scripts\audit_claim_language.py`
  - Result: exit code 0.
  - Full blocker count after this sprint: 144.
  - Full guard remains fail-closed: `claim_language_guard_ready=false`, `release_blocked=true`, `final_study_ready=false`.
- `.\.venv\Scripts\python -m py_compile .\src\realworld\road_source_decision_packet.py .\scripts\write_road_source_decision_packet.py`
  - Result: exit code 0.
- `.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD CLAIM LANGUAGE GUARD TESTS PASSED ===`.
- `.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py`
  - Result before adding this ledger: exit code 0.
  - Classified path count before adding this ledger: 494.
  - Result after adding this ledger: exit code 0.
  - Classified path count after adding this ledger: 495.
  - Unclassified path count: 0.
  - `destructive_cleanup_allowed=false`.
- `.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD PLAN AUDIT TESTS PASSED ===`.
- `Test-Path` check for the three focused-guard temporary files:
  - Result: exit code 0.
  - All three paths returned `Exists=False`.
- `git diff --check -- .\src\realworld\road_source_decision_packet.py .\scripts\write_road_source_decision_packet.py .\data\road\road_source_decision_packet.csv .\data\road\road_source_decision_manifest.json .\docs\road_source_decision_packet.md .\data\validation\claim_language_guard.csv .\data\validation\claim_language_guard_manifest.json .\docs\claim_language_guard.md .\data\validation\dirty_worktree_classification.csv .\data\validation\dirty_worktree_classification_manifest.json .\docs\dirty_worktree_classification.md`
  - Result: exit code 0.
  - Output included only LF-to-CRLF warnings for `scripts/write_road_source_decision_packet.py` and `src/realworld/road_source_decision_packet.py`.

## Claim Boundary

This sprint only reduces lexical release-blocking wording in the road source decision packet. It does not create a formal source decision, does not create source-backed road evidence, does not create or apply a reviewed override table, does not close cached-road, road evidence, road application, validation, publication, or formal acceptance gates, and does not change the project-wide `final_study_ready=false` state.

## Remaining Work

- Full claim-language guard remains blocked with 144 release-blocking unbounded findings.
- Current top blocker groups after this sprint include `data/manifests/experiment_package_review_manifest.json`, `data/manifests/figure_table_review_manifest.json`, `docs/accessibility_loss_analysis.md`, `docs/source_provenance_manifest.md`, `docs/crn_pairing_audit.md`, and `docs/pilot_region_data_card.md`.
- The dirty worktree remains large; cleanup is not allowed without owner and package decisions.
