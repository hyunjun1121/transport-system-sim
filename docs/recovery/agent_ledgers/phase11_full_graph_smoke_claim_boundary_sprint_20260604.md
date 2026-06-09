# Phase 11 Full-Graph Smoke Claim-Boundary Sprint

## Objective

Reduce release-blocking lexical claim-language findings in the generated
full-graph smoke manifest and Markdown without changing smoke-run semantics or
closing any graph-scale, validation, experiment, publication, or final-study
gate.

## Scope

Edited source:

- `scripts/run_full_graph_smoke.py`

Regenerated artifacts:

- `data/validation/full_graph_smoke_manifest.json`
- `docs/full_graph_smoke.md`
- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `docs/claim_language_guard.md`
- `data/validation/dirty_worktree_classification.csv`
- `data/validation/dirty_worktree_classification_manifest.json`
- `docs/dirty_worktree_classification.md`

Temporary focused-guard artifacts were created and then removed:

- `data/validation/tmp_claim_language_guard_full_graph_smoke.csv`
- `data/validation/tmp_claim_language_guard_full_graph_smoke_manifest.json`
- `docs/tmp_claim_language_guard_full_graph_smoke.md`

## Changes

- Reworded graph-scale acceptance/final-claim wording to reviewed
  graph-scale method decision and release-scope claim wording.
- Reworded accepted graph-method wording to reviewer-selected graph-method
  wording.
- Preserved the two-row full-graph smoke scope, `smoke_passed=true`,
  `full_graph_experiment_output_created=false`, `publication_ready=false`, and
  `can_mark_complete=false`.

## Command Evidence

| Command | Result | Claim impact |
| --- | --- | --- |
| `.\.venv\Scripts\python -m py_compile .\scripts\run_full_graph_smoke.py .\tests\test_realworld_full_graph_smoke.py` | Exit 0 | Syntax check only. |
| `git diff --check -- scripts/run_full_graph_smoke.py tests/test_realworld_full_graph_smoke.py` | Exit 0 with CRLF warning only | Whitespace check only. |
| `.\.venv\Scripts\python .\scripts\run_full_graph_smoke.py` | Exit 0; regenerated full-graph smoke manifest and Markdown | Confirms two-row smoke execution only, not full-profile outputs. |
| `.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\docs\full_graph_smoke.md --scan-path .\data\validation\full_graph_smoke_manifest.json --output .\data\validation\tmp_claim_language_guard_full_graph_smoke.csv --manifest .\data\validation\tmp_claim_language_guard_full_graph_smoke_manifest.json --doc .\docs\tmp_claim_language_guard_full_graph_smoke.md` | Exit 0; focused blocker count 0 | Confirms full-graph smoke artifacts no longer have release-blocking unbounded wording. |
| `.\.venv\Scripts\python .\tests\test_realworld_full_graph_smoke.py` | Exit 0; test passed | Confirms full bus-practical graph smoke and CLI plumbing. |
| `.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py` | Exit 0; test passed | Confirms claim-language guard behavior after regeneration. |
| `Remove-Item -LiteralPath .\data\validation\tmp_claim_language_guard_full_graph_smoke.csv, .\data\validation\tmp_claim_language_guard_full_graph_smoke_manifest.json, .\docs\tmp_claim_language_guard_full_graph_smoke.md` | Exit 0 | Removes temporary focused-guard outputs from the scan set. |
| `.\.venv\Scripts\python .\scripts\audit_claim_language.py` | Exit 0; release-blocking count changed from 60 to 57 | Reduces lexical blockers only. Release remains blocked. |
| `.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py` | Exit 0; plan audit test passed | Confirms plan-audit scaffold boundary is preserved. |
| `.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py` | Exit 0; classified 565 dirty paths and 0 unclassified paths before this ledger was added | Worktree remains dirty and cleanup is not authorized. |

## Current Guard State

- `data/validation/claim_language_guard_manifest.json` records
  `blocking_finding_count=57`.
- `release_blocked=true`.
- `claim_language_guard_ready=false`.
- `publication_ready=false`.
- `final_study_ready=false`.
- `can_mark_complete=false`.

## Remaining Blockers

- 57 release-blocking claim-language findings remain.
- Full-graph smoke is two-row runtime/smoke evidence only, not full-profile
  experiment output.
- Phase-gate ledgers are present but not closed.
- Formal graph-scale and final-study records remain absent.
- Dirty worktree classification still reports hundreds of dirty paths.

## Boundary

This sprint only reduces overclaim-sensitive wording in one smoke-output
family. It does not select a graph-scale method, create full-profile
full-graph experiment outputs, close publication readiness, approve final-study
use, or authorize operational routing.
