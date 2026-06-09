# Phase 11 Manuscript/Report Decision Claim-Boundary Sprint - 2026-06-04

## Scope

- Generated packet library: `src/realworld/manuscript_report_decision_packet.py`
- Writer command: `scripts/write_manuscript_report_decision_packet.py`
- Test: `tests/test_realworld_manuscript_report_decision_packet.py`
- Generated artifacts:
  - `data/manifests/manuscript_report_decision_packet.csv`
  - `data/manifests/manuscript_report_decision_manifest.json`
  - `docs/manuscript_report_decision_packet.md`
- Purpose: remove release-blocking unbounded accepted/validated/calibrated/operational/final wording from the manuscript/report decision packet while preserving it as a non-approval worksheet.
- Non-goal: no manuscript acceptance record was created, no paper/report/docx claim was approved, no upstream evidence gate was closed, and no final-study gate was closed.

## Edits

- Reworded paper-claim review action from accepted validation/calibration/operational/finality language to unsupported evidence-verification, benchmark-treatment, route-command, and release-complete wording.
- Reworded Korean report, figure/table, claim-alignment, upstream-gate, and docx rows from accepted/final language to reviewed decision-record and release-scope language.
- Reworded manifest review items from final manuscript claims and accepted report source to release-scope manuscript claims and reviewed report source.
- Reworded Markdown boundary guidance to keep claims in scaffold scope until a formal manuscript decision record is reviewed.
- Kept explicit non-approval boundaries and `final_study_ready=false` guard output intact.

## Verification

- `.\.venv\Scripts\python .\scripts\write_manuscript_report_decision_packet.py`
  - Result: exit code 0.
  - Manifest output reported row count 7, blocking decision count 4, human-review decision count 3, `publication_ready=false`, and `can_mark_complete=false`.
- `.\.venv\Scripts\python .\tests\test_realworld_manuscript_report_decision_packet.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD MANUSCRIPT REPORT DECISION TESTS PASSED ===`.
- `.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\docs\manuscript_report_decision_packet.md --scan-path .\data\manifests\manuscript_report_decision_manifest.json --output .\data\validation\tmp_claim_language_guard_manuscript_report_decision.csv --manifest .\data\validation\tmp_claim_language_guard_manuscript_report_decision_manifest.json --doc .\docs\tmp_claim_language_guard_manuscript_report_decision.md`
  - Result: exit code 0.
  - Focused blocker count: 0.
  - Focused bounded finding count: 24.
  - Focused `claim_language_guard_ready`: true.
- `Remove-Item -LiteralPath .\data\validation\tmp_claim_language_guard_manuscript_report_decision.csv, .\data\validation\tmp_claim_language_guard_manuscript_report_decision_manifest.json, .\docs\tmp_claim_language_guard_manuscript_report_decision.md -ErrorAction Stop`
  - Result: exit code 0.
- `.\.venv\Scripts\python .\scripts\audit_claim_language.py`
  - Result: exit code 0.
  - Full blocker count after this sprint: 174.
  - Full guard remains fail-closed: `claim_language_guard_ready=false`, `release_blocked=true`, `final_study_ready=false`.
- `.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py`
  - Result: exit code 0.
  - Classified path count: 464.
  - Unclassified path count: 0.
- `.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD CLAIM LANGUAGE GUARD TESTS PASSED ===`.
- `.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py`
  - Result: exit code 0.
  - Output ended with `=== REALWORLD PLAN AUDIT TESTS PASSED ===`.
- `git diff --check -- .\src\realworld\manuscript_report_decision_packet.py .\scripts\write_manuscript_report_decision_packet.py .\tests\test_realworld_manuscript_report_decision_packet.py .\docs\manuscript_report_decision_packet.md .\data\manifests\manuscript_report_decision_packet.csv .\data\manifests\manuscript_report_decision_manifest.json .\data\validation\claim_language_guard.csv .\data\validation\claim_language_guard_manifest.json .\docs\claim_language_guard.md .\data\validation\dirty_worktree_classification.csv .\data\validation\dirty_worktree_classification_manifest.json .\docs\dirty_worktree_classification.md`
  - Result: exit code 0.
  - Output included only an LF-to-CRLF warning for `src/realworld/manuscript_report_decision_packet.py`.
