# Phase 11 Formal Review Template Title Claim-Boundary Sprint - 2026-06-04

## Objective

Remove the release-blocking lexical claim-language finding at
`docs/acceptance_decision_templates.md:1` while preserving the document's
purpose as a non-approval template guide for human reviewers.

## Scope Boundary

This sprint changed only the generated Markdown title and its source generator.
It did not alter formal target paths, template JSON fields, parameter template
rows, acceptance semantics, final-study readiness, or publication readiness.

## Main-Thread Inspection

- Inspected the blocker row in `data/validation/claim_language_guard.csv`.
- Inspected `docs/acceptance_decision_templates.md`.
- Inspected `src/realworld/acceptance_decision_templates.py`.
- Inspected `scripts/write_acceptance_decision_templates.py`.
- Inspected `tests/test_realworld_acceptance_decision_templates.py`.
- Inspected `data/manifests/acceptance_decision_template_manifest.json`.

## Edit

- Replaced the generated Markdown heading
  `# Acceptance Decision Templates` with `# Formal Review Templates`.

The new title keeps the document's reviewer-template meaning while avoiding an
unbounded first-line reserved-term match.

## Commands

| Command | Result | Claim Impact |
| --- | --- | --- |
| `Import-Csv data\validation\claim_language_guard.csv ... docs/acceptance_decision_templates.md ... Format-List` | Exit 0; identified `docs/acceptance_decision_templates.md:1` as the release-blocking row | Established the exact target and evidence context before editing. |
| `Get-Content docs\acceptance_decision_templates.md -Raw` | Exit 0; showed the old generated title and non-approval body | Confirmed the blocker was in generated Markdown. |
| `rg -n "acceptance_decision_templates|Acceptance Decision|accepted|acceptance" src scripts tests docs\acceptance_decision_templates.md data\manifests\acceptance_decision_template_manifest.json` | Exit 0; located generator, script, tests, and current outputs | Identified the source-owned generation path. |
| `.\.venv\Scripts\python scripts\write_acceptance_decision_templates.py` | Exit 0; regenerated the template guide and printed the unchanged manifest | Confirms the document was regenerated through the owner script. |
| `.\.venv\Scripts\python tests\test_realworld_acceptance_decision_templates.py` | Exit 0; template tests passed | Confirms non-approval template behavior remains intact. |
| `.\.venv\Scripts\python scripts\audit_claim_language.py --scan-path docs\acceptance_decision_templates.md --output data\validation\tmp_claim_language_guard_acceptance_templates.csv --doc docs\tmp_claim_language_guard_acceptance_templates.md --manifest data\validation\tmp_claim_language_guard_acceptance_templates_manifest.json --fail-on-blockers` | Exit 0; focused scan reported `blocking_finding_count=0` | Confirms the document no longer has a release-blocking lexical finding. |
| Temp focused-guard cleanup for `data\validation\tmp_claim_language_guard_acceptance_templates.csv`, `docs\tmp_claim_language_guard_acceptance_templates.md`, and `data\validation\tmp_claim_language_guard_acceptance_templates_manifest.json` | Exit 0; all temp files absent after cleanup | Prevents temporary guard outputs from entering review packages. |
| `.\.venv\Scripts\python scripts\audit_claim_language.py` | Exit 0; full scan reported `blocking_finding_count=33` | Reduced total release-blocking lexical findings from 34 to 33. Release remains blocked. |
| `.\.venv\Scripts\python tests\test_realworld_claim_language_guard.py` | Exit 0; claim-language guard tests passed | Confirms guard behavior after the full refresh. |
| `Import-Csv data\validation\claim_language_guard.csv ... docs/acceptance_decision_templates.md ... Measure-Object` | Exit 0; count `0` after the full refresh | Confirms this document has no remaining release-blocking lexical row. |
| `.\.venv\Scripts\python scripts\write_dirty_worktree_classification.py` | Exit 0; dirty paths fully classified | Refreshes sprint-safety metadata after code/doc/output changes. |
| `.\.venv\Scripts\python tests\test_realworld_plan_audit.py` | Exit 0; plan audit test passed | Confirms the plan artifact audit remains aligned with the dirty classification. |
| `git diff --check -- src\realworld\acceptance_decision_templates.py docs\acceptance_decision_templates.md data\validation\claim_language_guard.csv data\validation\claim_language_guard_manifest.json docs\claim_language_guard.md data\validation\dirty_worktree_classification.csv data\validation\dirty_worktree_classification_manifest.json docs\dirty_worktree_classification.md` | Exit 0; PowerShell printed a CRLF normalization warning for `src/realworld/acceptance_decision_templates.py` | No whitespace errors were reported. |

## Result

- `docs/acceptance_decision_templates.md` release-blocking lexical rows:
  `1 -> 0`.
- Overall claim-language guard release-blocking rows: `34 -> 33`.
- `release_blocked=true`, `final_study_ready=false`, and
  `can_mark_complete=false` remain unchanged.

## Remaining Work

Continue Phase 11 claim-language cleanup from the next row in
`data/validation/claim_language_guard_manifest.json`, currently
`docs/deterministic_rerun_audit.md:7 ready`. This cleanup does not close
formal acceptance, reproducibility, publication, or final-study gates.
