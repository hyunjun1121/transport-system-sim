# Phase 11 Benchmark Strategy Decision Claim-Boundary Sprint

## Objective

Reduce release-blocking lexical claim-language findings in the generated
benchmark strategy decision packet without changing benchmark-review semantics
or closing any validation, publication, or final-study gate.

## Scope

Edited source:

- `src/realworld/validation_benchmark_decision_packet.py`

Edited test:

- `tests/test_realworld_validation_benchmark_decision_packet.py`

Regenerated artifacts:

- `data/validation/validation_benchmark_decision_packet.csv`
- `data/validation/validation_benchmark_decision_manifest.json`
- `docs/validation_benchmark_decision_packet.md`
- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `docs/claim_language_guard.md`
- `data/validation/dirty_worktree_classification.csv`
- `data/validation/dirty_worktree_classification_manifest.json`
- `docs/dirty_worktree_classification.md`

Temporary focused-guard artifacts were created and then removed:

- `data/validation/tmp_claim_language_guard_validation_benchmark_decision.csv`
- `data/validation/tmp_claim_language_guard_validation_benchmark_decision_manifest.json`
- `docs/tmp_claim_language_guard_validation_benchmark_decision.md`

## Changes

- Reworded the generated Markdown title from validation phrasing to benchmark
  strategy decision phrasing.
- Reworded the fallback benchmark reviewer action so it points to a formal
  benchmark-review record rather than using acceptance wording.
- Reworded the formal benchmark boundary row so it describes release-scope
  benchmark review rather than final/acceptance wording.
- Reworded manifest review items from final validation claims to release-scope
  benchmark claims.
- Preserved the same six decision rows, the same fail-closed validation-gate
  closure candidate count of zero, and `publication_ready=false`.

## Command Evidence

| Command | Result | Claim impact |
| --- | --- | --- |
| `.\.venv\Scripts\python -m py_compile .\src\realworld\validation_benchmark_decision_packet.py .\scripts\write_validation_benchmark_decision_packet.py .\tests\test_realworld_validation_benchmark_decision_packet.py` | Exit 0 | Syntax check only. |
| `git diff --check -- src/realworld/validation_benchmark_decision_packet.py tests/test_realworld_validation_benchmark_decision_packet.py scripts/write_validation_benchmark_decision_packet.py` | Exit 0 with CRLF warnings only | Whitespace check only. |
| `.\.venv\Scripts\python .\scripts\write_validation_benchmark_decision_packet.py` | Exit 0; regenerated CSV, manifest, and Markdown | Keeps the benchmark packet as review support with no gate closure. |
| `.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\docs\validation_benchmark_decision_packet.md --scan-path .\data\validation\validation_benchmark_decision_manifest.json --output .\data\validation\tmp_claim_language_guard_validation_benchmark_decision.csv --manifest .\data\validation\tmp_claim_language_guard_validation_benchmark_decision_manifest.json --doc .\docs\tmp_claim_language_guard_validation_benchmark_decision.md` | Exit 0; focused blocker count 0 | Confirms the benchmark decision packet no longer has release-blocking unbounded wording. |
| `.\.venv\Scripts\python .\tests\test_realworld_validation_benchmark_decision_packet.py` | Exit 0; test passed | Confirms generated benchmark decision artifacts match current rows. |
| `.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py` | Exit 0; test passed | Confirms claim-language guard behavior after regeneration. |
| `.\.venv\Scripts\python .\scripts\audit_claim_language.py` | Exit 0; release-blocking count changed from 72 to 69 | Reduces lexical blockers only. Release remains blocked. |
| `Remove-Item -LiteralPath .\data\validation\tmp_claim_language_guard_validation_benchmark_decision.csv, .\data\validation\tmp_claim_language_guard_validation_benchmark_decision_manifest.json, .\docs\tmp_claim_language_guard_validation_benchmark_decision.md` | Exit 0 | Removes temporary focused-guard outputs from the scan set. |
| `.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py` | Exit 0; plan audit test passed | Confirms plan-audit scaffold boundary is preserved. |
| `.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py` | Exit 0; classified 551 dirty paths and 0 unclassified paths before this ledger was added | Worktree remains dirty and cleanup is not authorized. |

## Current Guard State

- `data/validation/claim_language_guard_manifest.json` records
  `blocking_finding_count=69`.
- `release_blocked=true`.
- `claim_language_guard_ready=false`.
- `publication_ready=false`.
- `final_study_ready=false`.
- `can_mark_complete=false`.

## Remaining Blockers

- 69 release-blocking claim-language findings remain.
- Phase-gate ledgers are present but not closed.
- Artifact invalidation rows still require source and manifest evidence before
  closeout.
- Formal acceptance records remain absent.
- Dirty worktree classification still reports hundreds of dirty paths.

## Boundary

This sprint only reduces overclaim-sensitive wording in one generated review
packet family. It does not create validation evidence, choose a benchmark
strategy, close publication readiness, approve final-study use, or authorize
operational routing.
