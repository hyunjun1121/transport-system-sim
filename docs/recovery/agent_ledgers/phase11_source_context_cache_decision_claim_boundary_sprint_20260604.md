# Phase 11 Source Context-Cache Decision Claim-Boundary Sprint

## Objective

Reduce release-blocking lexical claim-language findings in the generated
source context-cache decision packet without changing source-cache semantics or
closing any provenance, publication, or final-study gate.

## Scope

Edited source:

- `src/realworld/source_context_cache_decision_packet.py`

Edited test:

- `tests/test_realworld_source_context_cache_decision_packet.py`

Regenerated artifacts:

- `data/manifests/source_context_cache_decision_packet.csv`
- `data/manifests/source_context_cache_decision_manifest.json`
- `docs/source_context_cache_decision_packet.md`
- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `docs/claim_language_guard.md`
- `data/validation/dirty_worktree_classification.csv`
- `data/validation/dirty_worktree_classification_manifest.json`
- `docs/dirty_worktree_classification.md`

Temporary focused-guard artifacts were created and then removed:

- `data/validation/tmp_claim_language_guard_source_context_cache_decision.csv`
- `data/validation/tmp_claim_language_guard_source_context_cache_decision_manifest.json`
- `docs/tmp_claim_language_guard_source_context_cache_decision.md`

## Changes

- Reworded the generated decision option from `exclude_from_final_claims` to
  `exclude_from_release_scope_claims`.
- Reworded the required reviewer action from final-claim exclusion to
  release-scope-claim exclusion.
- Reworded the boundary note from final claims to release-scope claims.
- Reworded the manifest review item from final provenance to release-scope
  provenance.
- Preserved three blocked context-source decision rows,
  `provenance_gate_closure_candidate_count=0`, `publication_ready=false`, and
  `can_mark_complete=false`.

## Command Evidence

| Command | Result | Claim impact |
| --- | --- | --- |
| `.\.venv\Scripts\python -m py_compile .\src\realworld\source_context_cache_decision_packet.py .\scripts\write_source_context_cache_decision_packet.py .\tests\test_realworld_source_context_cache_decision_packet.py` | Exit 0 | Syntax check only. |
| `git diff --check -- src/realworld/source_context_cache_decision_packet.py tests/test_realworld_source_context_cache_decision_packet.py scripts/write_source_context_cache_decision_packet.py` | Exit 0 with CRLF warnings only | Whitespace check only. |
| `.\.venv\Scripts\python .\scripts\write_source_context_cache_decision_packet.py` | Exit 0; regenerated CSV, manifest, and Markdown | Keeps the context-cache packet as review support with no gate closure. |
| `.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\docs\source_context_cache_decision_packet.md --scan-path .\data\manifests\source_context_cache_decision_manifest.json --output .\data\validation\tmp_claim_language_guard_source_context_cache_decision.csv --manifest .\data\validation\tmp_claim_language_guard_source_context_cache_decision_manifest.json --doc .\docs\tmp_claim_language_guard_source_context_cache_decision.md` | Exit 0; focused blocker count 0 | Confirms the context-cache decision packet no longer has release-blocking unbounded wording. |
| `.\.venv\Scripts\python .\tests\test_realworld_source_context_cache_decision_packet.py` | Exit 0; test passed | Confirms regenerated context-cache artifacts match current request rows. |
| `.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py` | Exit 0; test passed | Confirms claim-language guard behavior after regeneration. |
| `Remove-Item -LiteralPath .\data\validation\tmp_claim_language_guard_source_context_cache_decision.csv, .\data\validation\tmp_claim_language_guard_source_context_cache_decision_manifest.json, .\docs\tmp_claim_language_guard_source_context_cache_decision.md` | Exit 0 | Removes temporary focused-guard outputs from the scan set. |
| `.\.venv\Scripts\python .\scripts\audit_claim_language.py` | Exit 0; release-blocking count changed from 64 to 60 | Reduces lexical blockers only. Release remains blocked. |
| `.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py` | Exit 0; plan audit test passed | Confirms plan-audit scaffold boundary is preserved. |
| `.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py` | Exit 0; classified 561 dirty paths and 0 unclassified paths before this ledger was added | Worktree remains dirty and cleanup is not authorized. |

## Current Guard State

- `data/validation/claim_language_guard_manifest.json` records
  `blocking_finding_count=60`.
- `release_blocked=true`.
- `claim_language_guard_ready=false`.
- `publication_ready=false`.
- `final_study_ready=false`.
- `can_mark_complete=false`.

## Remaining Blockers

- 60 release-blocking claim-language findings remain.
- Phase-gate ledgers are present but not closed.
- Context-cache rows remain blocked until reviewed cache, retention, or
  exclusion decisions exist.
- Formal provenance and acceptance records remain absent.
- Dirty worktree classification still reports hundreds of dirty paths.

## Boundary

This sprint only reduces overclaim-sensitive wording in one generated review
packet family. It does not cache source extracts, certify licenses, close
provenance readiness, approve final-study use, or authorize operational
routing.
