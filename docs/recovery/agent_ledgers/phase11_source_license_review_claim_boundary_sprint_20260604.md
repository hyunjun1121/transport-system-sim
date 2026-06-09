# Phase 11 Source/License Review Claim-Boundary Sprint

## Objective

Reduce release-blocking lexical claim-language findings in the generated
source/license review packet without changing source-provenance semantics or
closing any provenance, publication, or final-study gate.

## Scope

Edited source:

- `src/realworld/source_license_review_packet.py`

Regenerated artifacts:

- `data/manifests/source_license_review_packet.csv`
- `data/manifests/source_license_review_manifest.json`
- `docs/source_license_review_packet.md`
- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `docs/claim_language_guard.md`
- `data/validation/dirty_worktree_classification.csv`
- `data/validation/dirty_worktree_classification_manifest.json`
- `docs/dirty_worktree_classification.md`

Temporary focused-guard artifacts were created and then removed:

- `data/validation/tmp_claim_language_guard_source_license_review.csv`
- `data/validation/tmp_claim_language_guard_source_license_review_manifest.json`
- `docs/tmp_claim_language_guard_source_license_review.md`

## Changes

- Reworded the generated Markdown support column from final-gate wording to
  provenance-gate wording.
- Reworded context-source exclusion wording from final claims to release-scope
  claims.
- Reworded pilot package wording from acceptance to retention.
- Reworded a manifest review item from provenance acceptance to provenance
  review-record wording.
- Preserved `provenance_gate_closure_candidate_count=0`,
  `publication_ready=false`, and `can_mark_complete=false`.

## Command Evidence

| Command | Result | Claim impact |
| --- | --- | --- |
| `.\.venv\Scripts\python -m py_compile .\src\realworld\source_license_review_packet.py .\scripts\write_source_license_review_packet.py .\tests\test_realworld_source_license_review_packet.py` | Exit 0 | Syntax check only. |
| `git diff --check -- src/realworld/source_license_review_packet.py scripts/write_source_license_review_packet.py tests/test_realworld_source_license_review_packet.py` | Exit 0 with CRLF warning only | Whitespace check only. |
| `.\.venv\Scripts\python .\scripts\write_source_license_review_packet.py` | Exit 0; regenerated CSV, manifest, and Markdown | Keeps the source/license packet as review support with no gate closure. |
| `.\.venv\Scripts\python .\tests\test_realworld_source_license_review_packet.py` | Exit 0; test passed | Confirms regenerated source/license artifacts match deterministic provenance inputs. |
| `.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\docs\source_license_review_packet.md --scan-path .\data\manifests\source_license_review_manifest.json --output .\data\validation\tmp_claim_language_guard_source_license_review.csv --manifest .\data\validation\tmp_claim_language_guard_source_license_review_manifest.json --doc .\docs\tmp_claim_language_guard_source_license_review.md` | Exit 0; focused blocker count 0 after self-refine | Confirms the source/license packet no longer has release-blocking unbounded wording. |
| `.\.venv\Scripts\python .\scripts\audit_claim_language.py` | Exit 0; release-blocking count changed from 69 to 64 | Reduces lexical blockers only. Release remains blocked. |
| `.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py` | Exit 0; test passed | Confirms claim-language guard behavior after regeneration. |
| `Remove-Item -LiteralPath .\data\validation\tmp_claim_language_guard_source_license_review.csv, .\data\validation\tmp_claim_language_guard_source_license_review_manifest.json, .\docs\tmp_claim_language_guard_source_license_review.md` | Exit 0 | Removes temporary focused-guard outputs from the scan set. |
| `.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py` | Exit 0; plan audit test passed | Confirms plan-audit scaffold boundary is preserved. |
| `.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py` | Exit 0; classified 555 dirty paths and 0 unclassified paths before this ledger was added | Worktree remains dirty and cleanup is not authorized. |

## Self-Refine Note

The first focused guard found one remaining blocker in
`data/manifests/source_license_review_manifest.json` from the phrase
`provenance acceptance`. The source was patched to `provenance review record`,
then the packet was regenerated and the focused guard returned zero blockers.

## Current Guard State

- `data/validation/claim_language_guard_manifest.json` records
  `blocking_finding_count=64`.
- `release_blocked=true`.
- `claim_language_guard_ready=false`.
- `publication_ready=false`.
- `final_study_ready=false`.
- `can_mark_complete=false`.

## Remaining Blockers

- 64 release-blocking claim-language findings remain.
- Phase-gate ledgers are present but not closed.
- Source/license rows remain review aids and do not certify license
  compatibility.
- Formal provenance and acceptance records remain absent.
- Dirty worktree classification still reports hundreds of dirty paths.

## Boundary

This sprint only reduces overclaim-sensitive wording in one generated review
packet family. It does not certify sources, approve licenses, close provenance
readiness, approve final-study use, or authorize operational routing.
