# Phase 11 Deterministic Rerun Claim-Boundary Sprint - 2026-06-04

## Objective

Remove the release-blocking lexical claim-language finding at
`docs/deterministic_rerun_audit.md:7` while preserving the bounded deterministic
rerun audit result and its non-acceptance claim boundary.

## Scope Boundary

This sprint changed the generated Markdown label for one verdict field and
regenerated the deterministic rerun audit artifacts with the owner script. It
did not close experiment acceptance, reproducibility, publication, or
final-study gates.

## Main-Thread Inspection

- Inspected the blocker row in `data/validation/claim_language_guard.csv`.
- Inspected `docs/deterministic_rerun_audit.md`.
- Inspected `src/realworld/deterministic_rerun_audit.py`.
- Inspected `scripts/audit_deterministic_rerun.py`.
- Inspected `tests/test_realworld_deterministic_rerun_audit.py`.
- Inspected `data/manifests/deterministic_rerun_audit_manifest.json`.

## Edit

- Replaced the generated Markdown label
  `Deterministic rerun structurally ready` with
  `Deterministic rerun structural checks passed`.

The manifest key `deterministic_rerun_structurally_ready` remains unchanged.
The change only lowers the prose label that appears in the Markdown report.

## Regenerated Outputs

The owner script refreshed:

- `data/manifests/deterministic_rerun_audit.csv`
- `data/manifests/deterministic_rerun_audit_manifest.json`
- `docs/deterministic_rerun_audit.md`

The rerun output hashes changed relative to the prior tracked artifacts because
the audit was regenerated against the current dirty input state. The two local
executions within the regenerated audit still matched each other:

- row hash: `88b8533c94c090b02c4a7bcf9c6a4c167d39ac200cdb513eb4d5c2e29505949d`
- summary hash: `eb7768d4247ae01084f104b6c4a0476d485b29fd871f09af942b3ea4fc6c1275`

The audit still reports one blocker:
`blocked_missing_experiment_acceptance_record`.

## Commands

| Command | Result | Claim Impact |
| --- | --- | --- |
| `Import-Csv data\validation\claim_language_guard.csv ... docs/deterministic_rerun_audit.md ... Format-List` | Exit 0; identified `docs/deterministic_rerun_audit.md:7 ready` as the release-blocking row | Established the exact target and evidence context before editing. |
| `Get-Content docs\deterministic_rerun_audit.md -Raw` | Exit 0; showed the old verdict label and non-acceptance boundary | Confirmed the blocker was in generated Markdown. |
| `Get-Content src\realworld\deterministic_rerun_audit.py -Raw` | Exit 0; identified `build_deterministic_rerun_markdown` as the owner function | Confirmed the source-owned generation path. |
| `.\.venv\Scripts\python scripts\audit_deterministic_rerun.py` | Exit 0; regenerated CSV, manifest, and Markdown; two reruns matched row and summary hashes | Refreshes bounded repeatability support only; does not close experiment acceptance. |
| `.\.venv\Scripts\python tests\test_realworld_deterministic_rerun_audit.py` | Exit 0; deterministic rerun audit tests passed | Confirms row building and output writer behavior remain covered. |
| `.\.venv\Scripts\python scripts\audit_claim_language.py --scan-path docs\deterministic_rerun_audit.md --output data\validation\tmp_claim_language_guard_deterministic_rerun.csv --doc docs\tmp_claim_language_guard_deterministic_rerun.md --manifest data\validation\tmp_claim_language_guard_deterministic_rerun_manifest.json --fail-on-blockers` | Exit 0; focused scan reported `blocking_finding_count=0` | Confirms the document no longer has a release-blocking lexical finding. |
| Temp focused-guard cleanup for `data\validation\tmp_claim_language_guard_deterministic_rerun.csv`, `docs\tmp_claim_language_guard_deterministic_rerun.md`, and `data\validation\tmp_claim_language_guard_deterministic_rerun_manifest.json` | Exit 0; all temp files absent after cleanup | Prevents temporary guard outputs from entering review packages. |
| `.\.venv\Scripts\python scripts\audit_claim_language.py` | Exit 0; full scan reported `blocking_finding_count=32` | Reduced total release-blocking lexical findings from 33 to 32. Release remains blocked. |
| `.\.venv\Scripts\python tests\test_realworld_claim_language_guard.py` | Exit 0; claim-language guard tests passed | Confirms guard behavior after the full refresh. |
| `Import-Csv data\validation\claim_language_guard.csv ... docs/deterministic_rerun_audit.md ... Measure-Object` | Exit 0; count `0` | Confirms this document has no remaining release-blocking lexical row. |
| `.\.venv\Scripts\python scripts\write_dirty_worktree_classification.py` | Exit 0; dirty paths fully classified | Refreshes sprint-safety metadata after regenerated artifacts. |
| `.\.venv\Scripts\python tests\test_realworld_plan_audit.py` | Exit 0; plan audit test passed | Confirms the plan artifact audit remains aligned with dirty classification. |
| `git diff --check -- src\realworld\deterministic_rerun_audit.py docs\deterministic_rerun_audit.md data\manifests\deterministic_rerun_audit.csv data\manifests\deterministic_rerun_audit_manifest.json data\validation\claim_language_guard.csv data\validation\claim_language_guard_manifest.json docs\claim_language_guard.md data\validation\dirty_worktree_classification.csv data\validation\dirty_worktree_classification_manifest.json docs\dirty_worktree_classification.md` | Exit 0; PowerShell printed a CRLF normalization warning for `src/realworld/deterministic_rerun_audit.py` | No whitespace errors were reported. |

## Result

- `docs/deterministic_rerun_audit.md` release-blocking lexical rows: `1 -> 0`.
- Overall claim-language guard release-blocking rows: `33 -> 32`.
- `release_blocked=true`, `final_study_ready=false`, and
  `can_mark_complete=false` remain unchanged.

## Remaining Work

Continue Phase 11 claim-language cleanup from the next row in
`data/validation/claim_language_guard_manifest.json`, currently
`docs/final_audit_decision_packet.md:1 final`. The deterministic rerun audit
still depends on later experiment acceptance and does not support final-study
completion by itself.
