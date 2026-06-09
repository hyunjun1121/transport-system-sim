# Phase 11 Road/Sensitivity Review Claim-Boundary Sprint - 2026-06-04

## Scope

- Objective: reduce release-blocking claim-language findings in road-evidence and sensitivity review packets without changing gate status or evidence meaning.
- Ownership:
  - `src/realworld/road_evidence_review_packet.py`
  - `src/realworld/sensitivity_review_packet.py`
  - `src/realworld/sensitivity_strategy_readiness_packet.py`
  - `docs/road_evidence_review_packet.md`
  - `docs/sensitivity_review_packet.md`
  - `docs/sensitivity_strategy_readiness_packet.md`
  - generated road and sensitivity packet CSV/JSON artifacts
  - claim-language guard outputs
  - dirty-worktree classification outputs
- Out of scope:
  - road-class override signoff
  - sensitivity acceptance or Morris/Sobol method decision
  - graph-scale acceptance
  - publication-readiness or study-closeout signoff

## Inspected Evidence

- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `src/realworld/road_evidence_review_packet.py`
- `src/realworld/sensitivity_review_packet.py`
- `src/realworld/sensitivity_strategy_readiness_packet.py`
- `docs/road_evidence_review_packet.md`
- `docs/sensitivity_review_packet.md`
- `docs/sensitivity_strategy_readiness_packet.md`
- `tests/test_realworld_road_evidence_review_packet.py`
- `tests/test_realworld_sensitivity_review_packet.py`
- `tests/test_realworld_sensitivity_strategy_readiness_packet.py`

## Edits

- Reworded road-evidence packet wording:
  - `accepted road calibration` -> `road calibration signoff`
  - `accepted road-class overrides` -> `road-class override signoff`
  - `move accepted values` -> `move reviewer-selected values`
  - `final-study acceptance gates` -> `study-closeout decision records`
  - `accepted scenario assumptions` -> `reviewer-scoped scenario assumptions`
- Reworded sensitivity review wording:
  - `ready_for_review` -> `available_for_review`
  - `structural readiness` -> `structural review state`
  - `final-study sensitivity run` -> `study-closeout sensitivity run`
  - `final claims` -> `release-scope claims`
  - `final claim boundary` -> `release-scope claim boundary`
- Reworded sensitivity strategy packet Markdown:
  - title `Sensitivity Strategy Readiness Packet` -> `Sensitivity Strategy Review Packet`
  - heading `Readiness Rows` -> `Review Rows`
  - `accepted claim boundary` -> `reviewer-selected claim boundary`
  - `accepted graph method` -> `reviewer-selected graph method`
  - `final evidence scope` -> `release evidence scope`
- Updated tests for the changed non-approval wording.
- Regenerated road and sensitivity review CSV/JSON/Markdown outputs from project-owned scripts.

## Verification Commands

```powershell
.\.venv\Scripts\python -m py_compile .\src\realworld\road_evidence_review_packet.py .\src\realworld\sensitivity_review_packet.py .\src\realworld\sensitivity_strategy_readiness_packet.py .\scripts\write_road_evidence_review_packet.py .\scripts\write_sensitivity_review_packet.py .\scripts\write_sensitivity_strategy_readiness_packet.py
.\.venv\Scripts\python .\scripts\write_road_evidence_review_packet.py
.\.venv\Scripts\python .\scripts\write_sensitivity_review_packet.py
.\.venv\Scripts\python .\scripts\write_sensitivity_strategy_readiness_packet.py
.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\docs\road_evidence_review_packet.md --scan-path .\docs\sensitivity_review_packet.md --scan-path .\docs\sensitivity_strategy_readiness_packet.md --output .\data\validation\tmp_claim_language_guard_road_sensitivity.csv --manifest .\data\validation\tmp_claim_language_guard_road_sensitivity_manifest.json --doc .\docs\tmp_claim_language_guard_road_sensitivity.md
Remove-Item -LiteralPath .\data\validation\tmp_claim_language_guard_road_sensitivity.csv, .\data\validation\tmp_claim_language_guard_road_sensitivity_manifest.json, .\docs\tmp_claim_language_guard_road_sensitivity.md
.\.venv\Scripts\python .\tests\test_realworld_road_evidence_review_packet.py
.\.venv\Scripts\python .\tests\test_realworld_sensitivity_review_packet.py
.\.venv\Scripts\python .\tests\test_realworld_sensitivity_strategy_readiness_packet.py
.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py
.\.venv\Scripts\python .\scripts\audit_claim_language.py
.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py
.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py
git diff --check -- .\src\realworld\road_evidence_review_packet.py .\src\realworld\sensitivity_review_packet.py .\src\realworld\sensitivity_strategy_readiness_packet.py .\docs\road_evidence_review_packet.md .\docs\sensitivity_review_packet.md .\docs\sensitivity_strategy_readiness_packet.md .\tests\test_realworld_road_evidence_review_packet.py .\tests\test_realworld_sensitivity_review_packet.py .\tests\test_realworld_sensitivity_strategy_readiness_packet.py .\data\parameters\road_evidence_review_packet.csv .\data\parameters\road_evidence_review_manifest.json .\data\validation\sensitivity_review_packet.csv .\data\validation\sensitivity_review_manifest.json .\data\validation\sensitivity_strategy_readiness_packet.csv .\data\validation\sensitivity_strategy_readiness_manifest.json .\data\validation\claim_language_guard.csv .\data\validation\claim_language_guard_manifest.json .\docs\claim_language_guard.md .\data\validation\dirty_worktree_classification.csv .\data\validation\dirty_worktree_classification_manifest.json .\docs\dirty_worktree_classification.md
```

## Results

- Focused claim-language guard for the three docs:
  - `blocking_finding_count=0`
  - `claim_language_guard_ready=true`
  - `release_blocked=false`
- Full claim-language guard:
  - before this sprint: `blocking_finding_count=109`
  - after this sprint: `blocking_finding_count=97`
  - `claim_language_guard_ready=false`
  - `release_blocked=true`
- Tests:
  - road-evidence review packet tests passed
  - sensitivity review packet tests passed
  - sensitivity strategy review packet tests passed
  - claim-language guard tests passed
  - plan artifact audit test passed after dirty-worktree classification refresh
- Dirty worktree classification before this ledger was added:
  - `classified_path_count=529`
  - `unclassified_path_count=0`
- Dirty worktree classification after this ledger was added:
  - `classified_path_count=530`
  - `unclassified_path_count=0`
- Temporary focused-guard files were removed:
  - `data/validation/tmp_claim_language_guard_road_sensitivity.csv`
  - `data/validation/tmp_claim_language_guard_road_sensitivity_manifest.json`
  - `docs/tmp_claim_language_guard_road_sensitivity.md`
- `git diff --check` reported no whitespace errors for the sprint scope. It reported LF-to-CRLF warnings for edited Python, Markdown, and test files.

## Residual Risks

- The edits are claim-boundary wording only; no evidence gate was closed.
- Full claim-language guard still has 97 release-blocking findings.
- Road-class override evidence, rail/source evidence, sensitivity acceptance, and formal closeout records remain blocked.
