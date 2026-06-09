# Phase 4 Source-Decision Recommendation Guard - 2026-06-03

## Objective

Continue Phase 4 rail/transit work under `plan.md` without creating false rail
evidence. The task was to make reviewer decision paths clearer while preserving
fail-closed publication, final-study, and formal-acceptance gates.

## Baseline Evidence

- Inspected `plan.md` Phase 4 and Immediate Next Actions.
- Inspected current publication readiness:
  `data/manifests/publication_readiness_audit.json` reported
  `publication_ready=false`, `blocked_gate_count=9`, `ready_gate_count=1`, and
  `rail_source_decision_ready=false`.
- Inspected current rail decision artifacts:
  `data/rail/rail_source_decision_packet.csv`,
  `data/rail/rail_source_decision_manifest.json`,
  `data/rail/rail_source_decision_action_ledger_template.csv`,
  `data/rail/rail_source_decision_recommendation_packet.csv`,
  `data/rail/rail_bounded_treatment_audit.json`, and
  `data/rail/rail_evidence_priority_manifest.json`.
- Verified before edits that the generated action-ledger template CSV contained
  only `pending_reviewer_decision` rows with blank reviewer/action fields.

## Sub-Agent Findings

Three GPT-5.5 xhigh read-only agents were used and closed after synthesis.

- GTFS/timetable explorer found no retained source-backed rail timing evidence
  in the current local artifacts. GTFS, static timetable CSV, timetable API, and
  shortest-path API paths are possible in code but blocked by missing reviewed
  source files, cache/raw payloads, validator report, or `DATA_GO_KR_KEY`.
- Capacity/availability explorer found the capacity and availability rows still
  pending. It recommended documentation-only examples for reviewer-owned copied
  ledgers, not prefilled generated CSV rows.
- Adversarial reviewer confirmed current gates fail closed, but found stale
  final-study test assertions and recommended explicit guards against optimistic
  non-formal source-decision manifests and stale source-decision input
  manifests.

## Implementation

- Added `reviewer_action_prompt` to
  `src/realworld/rail_source_decision_recommendation_packet.py` so each
  recommendation row tells a reviewer what evidence or bounded scope decision
  is still required.
- Updated `docs/rail_source_decision_recommendation_packet.md` and
  `data/rail/rail_source_decision_recommendation_packet.csv` through the
  existing writer. All six rows now have non-empty reviewer action prompts.
- Added a `Non-Formal Example Rows` section to the generated action-ledger
  template Markdown. The examples show how a copied, reviewer-owned ledger could
  classify capacity as sensitivity-only and availability as scenario-only. The
  generated CSV itself remains blank and pending.
- Added publication and final-study guards rejecting rail source-decision
  manifests whose `action_ledger_completion_scope` is
  `non_formal_source_review_only` or whose action ledger is not formal
  acceptance evidence.
- Added a publication-readiness stale-input guard. If a rail source-decision
  manifest otherwise appears ready, the guard checks the linked
  fetch-readiness and evidence-priority manifests for unresolved blocking or
  human-review counts before allowing `rail_source_decision_ready=true`.
- Updated final-study readiness details and tests for the current rail packet
  counts: fetch external-input present count `2`, specified/text-present counts
  `6`, rail priority row count `7`, blocking priority count `4`, and
  human-review priority count `2`.

## Verification

Commands run and passed:

```powershell
.\.venv\Scripts\python -m py_compile .\src\realworld\rail_source_decision_packet.py .\src\realworld\rail_source_decision_recommendation_packet.py .\src\realworld\publication_readiness.py .\src\realworld\final_study_readiness.py .\tests\test_realworld_rail_source_decision_action_ledger_template.py .\tests\test_realworld_rail_source_decision_recommendation_packet.py .\tests\test_realworld_publication_readiness.py .\tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python .\scripts\write_rail_source_decision_action_ledger_template.py
.\.venv\Scripts\python .\scripts\write_rail_source_decision_recommendation_packet.py
.\.venv\Scripts\python .\tests\test_realworld_rail_source_decision_action_ledger_template.py
.\.venv\Scripts\python .\tests\test_realworld_rail_source_decision_recommendation_packet.py
.\.venv\Scripts\python .\tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python .\tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python .\scripts\audit_publication_readiness.py
.\.venv\Scripts\python .\scripts\audit_final_study_readiness.py
.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py
.\.venv\Scripts\python .\scripts\audit_plan_artifacts.py
```

Additional inspected outputs:

- `data/rail/rail_source_decision_recommendation_packet.csv` has 6 rows and
  `prompt_empty_count=0`.
- `data/rail/rail_source_decision_action_ledger_template.csv` still has only
  `pending_reviewer_decision` rows and no filled reviewer fields.
- `data/manifests/publication_readiness_audit.json` remains
  `publication_ready=false`, `blocked_gate_count=9`, `ready_gate_count=1`.
- Plan artifact audit reports `all_required_artifacts_present=true` and
  verdict `executable_quasi_real_scaffold_not_final_calibrated_study`.
- `git diff --check` on the touched files reported only CRLF normalization
  warnings.

## Gate Status

This work does not create rail timing evidence, rail capacity evidence, rail
availability evidence, publication readiness, final-study readiness, or formal
acceptance. It only strengthens reviewer guidance and fail-closed guards.

Remaining Phase 4 blockers:

- retain reviewed GTFS plus same-feed Validator report, or reviewed static
  timetable CSV plus mapping/normalization manifest;
- retain timetable/shortest-path cache and raw payloads, or provide an
  accepted exclusion/bounded treatment;
- record reviewer-owned source decisions for all rail rows;
- keep capacity and availability source-backed, bounded, or excluded before
  compact/full experiments rely on rail claims.
