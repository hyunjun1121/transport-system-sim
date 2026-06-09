# Phase 11 Full-Graph Runtime Review Claim-Boundary Sprint - 2026-06-04

## Scope

- Generated packet library: `src/realworld/full_graph_runtime_readiness_packet.py`
- Writer command: `scripts/write_full_graph_runtime_readiness_packet.py`
- Test: `tests/test_realworld_full_graph_runtime_readiness_packet.py`
- Generated artifacts:
  - `data/validation/full_graph_runtime_readiness_packet.csv`
  - `data/validation/full_graph_runtime_readiness_manifest.json`
- Manual document: `docs/full_graph_runtime_readiness_packet.md`
- Purpose: remove release-blocking unbounded full-graph runtime readiness, accepted, and final wording while preserving the packet as runtime review support only.
- Non-goal: no full-graph full-profile output was generated, no graph-scale method was accepted, no formal decision record was created, no calibrated validation was created, and no final-study gate was closed.

## Edits

- Reworded reader-facing text from full-graph runtime readiness packet to full-graph runtime review packet.
- Reworded generated review item text from final claims to release-scope claims.
- Reworded reviewer actions from accepted graph method to selected graph method recorded in a formal decision record.
- Kept internal file names, CSV column names, and status identifiers stable for compatibility with existing review/audit code.
- Kept `publication_ready=false`, `can_mark_complete=false`, and `full_graph_gate_closure_candidate_count=0` intact.

## Verification

- `.\.venv\Scripts\python .\scripts\write_full_graph_runtime_readiness_packet.py`
  - Result: exit code 0.
  - Manifest output reported row count 4, `publication_ready=false`, `can_mark_complete=false`, `full_graph_gate_closure_candidate_count=0`, `blocking_request_count=2`, and `human_review_request_count=2`.
- `.\.venv\Scripts\python .\tests\test_realworld_full_graph_runtime_readiness_packet.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD FULL-GRAPH RUNTIME READINESS TESTS PASSED ===`.
- `.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\docs\full_graph_runtime_readiness_packet.md --scan-path .\data\validation\full_graph_runtime_readiness_manifest.json --output .\data\validation\tmp_claim_language_guard_full_graph_runtime.csv --manifest .\data\validation\tmp_claim_language_guard_full_graph_runtime_manifest.json --doc .\docs\tmp_claim_language_guard_full_graph_runtime.md`
  - Result: exit code 0.
  - Focused blocker count: 0.
  - Focused bounded finding count: 19.
  - Focused `claim_language_guard_ready`: true.
- `Remove-Item -LiteralPath .\data\validation\tmp_claim_language_guard_full_graph_runtime.csv, .\data\validation\tmp_claim_language_guard_full_graph_runtime_manifest.json, .\docs\tmp_claim_language_guard_full_graph_runtime.md -ErrorAction Stop`
  - Result: exit code 0.
- `.\.venv\Scripts\python .\scripts\audit_claim_language.py`
  - Result: exit code 0.
  - Full blocker count after this sprint: 164.
  - Full guard remains fail-closed: `claim_language_guard_ready=false`, `release_blocked=true`, `final_study_ready=false`.
- `.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py`
  - Result: exit code 0.
  - Classified path count before adding this ledger: 478.
  - Classified path count after adding this ledger: 479.
  - Unclassified path count: 0.
  - `destructive_cleanup_allowed=false`.
- `.\.venv\Scripts\python -m py_compile .\src\realworld\full_graph_runtime_readiness_packet.py .\scripts\write_full_graph_runtime_readiness_packet.py`
  - Result: exit code 0.
- `.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD CLAIM LANGUAGE GUARD TESTS PASSED ===`.
- `.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD PLAN AUDIT TESTS PASSED ===`.
- `Test-Path` check for the three focused-guard temporary files:
  - Result: exit code 0.
  - All three paths returned `Exists=False`.
- `git diff --check -- .\src\realworld\full_graph_runtime_readiness_packet.py .\scripts\write_full_graph_runtime_readiness_packet.py .\tests\test_realworld_full_graph_runtime_readiness_packet.py .\docs\full_graph_runtime_readiness_packet.md .\data\validation\full_graph_runtime_readiness_packet.csv .\data\validation\full_graph_runtime_readiness_manifest.json .\data\validation\claim_language_guard.csv .\data\validation\claim_language_guard_manifest.json .\docs\claim_language_guard.md .\data\validation\dirty_worktree_classification.csv .\data\validation\dirty_worktree_classification_manifest.json .\docs\dirty_worktree_classification.md`
  - Result: exit code 0.
  - Output included only LF-to-CRLF warnings for `scripts/write_full_graph_runtime_readiness_packet.py`, `src/realworld/full_graph_runtime_readiness_packet.py`, and `tests/test_realworld_full_graph_runtime_readiness_packet.py`.

## Claim Boundary

This sprint only reduces lexical release-blocking wording in the full-graph runtime review packet. It does not create full-graph full-profile outputs, does not select or approve a graph-scale method, does not create formal human-review evidence, does not validate the traffic model, does not approve publication, and does not change the project-wide `final_study_ready=false` state.

## Remaining Work

- Full claim-language guard remains blocked with 164 release-blocking unbounded findings.
- The updated guard shows remaining graph-adjacent blockers in `docs/full_graph_smoke.md` and `docs/graph_scale_method_decision_packet.md`.
- The dirty worktree remains large; cleanup is not allowed without owner and package decisions.
