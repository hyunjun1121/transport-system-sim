# Phase 11 Experiment Design Decision Claim-Boundary Sprint

## Objective

Reduce release-blocking lexical claim-language findings in the experiment design
decision packet without changing experiment gate status or creating acceptance
evidence.

## Scope

Edited source:

- `src/realworld/experiment_design_decision_packet.py`

Regenerated artifacts:

- `data/manifests/experiment_design_decision_packet.csv`
- `data/manifests/experiment_design_decision_manifest.json`
- `docs/experiment_design_decision_packet.md`
- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `docs/claim_language_guard.md`
- `data/validation/dirty_worktree_classification.csv`
- `data/validation/dirty_worktree_classification_manifest.json`
- `docs/dirty_worktree_classification.md`

## Changes

- Replaced human-facing accepted-output wording with reviewed-output or selected
  method wording.
- Replaced graph/input acceptance timing language with graph/input review
  language.
- Replaced final experiment decision wording with experiment-gate decision
  wording.
- Preserved the formal acceptance artifact path
  `data/manifests/experiment_acceptance.json` as the only place where future
  experiment gate decisions can be recorded.
- Preserved `publication_ready=false`, `can_mark_complete=false`, and
  `experiment_gate_closure_candidate_count=0`.

## Command Evidence

| Command | Result | Claim impact |
| --- | --- | --- |
| `.\.venv\Scripts\python -m py_compile .\src\realworld\experiment_design_decision_packet.py .\scripts\write_experiment_design_decision_packet.py .\tests\test_realworld_experiment_design_decision_packet.py` | Exit 0 | Syntax check only. |
| `git diff --check -- src/realworld/experiment_design_decision_packet.py scripts/write_experiment_design_decision_packet.py tests/test_realworld_experiment_design_decision_packet.py data/manifests/experiment_design_decision_packet.csv data/manifests/experiment_design_decision_manifest.json docs/experiment_design_decision_packet.md` | Exit 0 with LF-to-CRLF warning for the edited source file | Whitespace check only. |
| `.\.venv\Scripts\python .\scripts\write_experiment_design_decision_packet.py` | Exit 0; regenerated packet CSV, manifest, and Markdown | Keeps the packet as non-acceptance review support. |
| `.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\data\manifests\experiment_design_decision_manifest.json --scan-path .\docs\experiment_design_decision_packet.md --output .\data\validation\tmp_claim_language_guard_experiment_design.csv --manifest .\data\validation\tmp_claim_language_guard_experiment_design_manifest.json --doc .\docs\tmp_claim_language_guard_experiment_design.md` | Exit 0; focused blocker count 0 | Confirms the generated manifest and Markdown have no release-blocking unbounded wording. |
| `.\.venv\Scripts\python .\tests\test_realworld_experiment_design_decision_packet.py` | Exit 0; all experiment design decision tests passed | Confirms row classification and shipped artifacts still match the generator. |
| `.\.venv\Scripts\python .\scripts\audit_claim_language.py` | Exit 0; release-blocking count changed from 78 to 75 | Reduces lexical blockers only. Release remains blocked. |
| `.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py` | Exit 0; all claim-language guard tests passed | Confirms guard behavior after regeneration. |
| `.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py` | Exit 0; plan audit test passed | Confirms plan-audit scaffold boundary is preserved. |
| `.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py` | Exit 0; classified 545 dirty paths and 0 unclassified paths before this ledger was added | Worktree remains dirty and cleanup is not authorized. |

## Current Guard State

- `data/validation/claim_language_guard_manifest.json` records
  `blocking_finding_count=75`.
- `release_blocked=true`.
- `claim_language_guard_ready=false`.
- `publication_ready=false`.
- `final_study_ready=false`.
- `can_mark_complete=false`.

## Remaining Blockers

- 75 release-blocking claim-language findings remain.
- Artifact invalidation matrix still has unresolved blocking rows.
- Phase 9 promotion remains blocked.
- Formal acceptance records remain absent.
- Dirty worktree classification still reports hundreds of dirty paths.

## Boundary

This sprint only lowers overclaim-sensitive wording in the experiment design
decision packet. It does not select a run profile, close graph-scope review,
accept experiment outputs, approve publication, or close study gates.
