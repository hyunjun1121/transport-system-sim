# Artifact Invalidation Reviewer Evidence Apply Path - 2026-06-09

## Objective

Continue the narrowed implementation-first sprint after claim-language guard
cleanup. The target was to make artifact-invalidation closeout capable of
consuming real row-level reviewer evidence without treating stale worksheet
values, support-only audits, or obsolete human-review markers as gate-clearing
evidence.

## Inspected State

Files inspected during this slice:

- `plan.md`
- `docs/recovery/agent_ledgers/claim_language_phase_gate_guard_20260608.md`
- `docs/recovery/agent_ledgers/artifact_invalidation_reviewer_evidence_hardening_20260608.md`
- `data/validation/artifact_invalidation_closeout_readiness_audit_manifest.json`
- `data/validation/artifact_invalidation_action_batch_inspection_manifest.json`
- `src/realworld/artifact_invalidation_matrix.py`
- `scripts/write_artifact_invalidation_matrix.py`
- `tests/test_realworld_artifact_invalidation_matrix.py`

Observed current artifact-invalidation state:

- `row_count=51`
- `can_clear_invalidation_gate=false`
- `can_clear_invalidation_gate_count=0`
- `closeout_ready_row_count=0`
- `pending_or_blocked_row_count=51`
- `missing_evidence_row_count=51`
- all action batches remain blocked by
  `reviewer_identity:obsolete_human_reviewer_marker` and
  `can_clear_invalidation_gate`

## Sub-Agent Availability

Two GPT-5.5 xhigh reviewer waves were attempted for artifact-invalidation
reviewer evidence, but both returned usage-limit errors. No reviewer evidence
record was created or applied from those attempts.

This sprint therefore implemented only the local evidence-application path.
It did not synthesize approval records and did not mark any of the 51 rows as
clearable.

## Changes

- `plan.md`
  - Updated Immediate Next Actions after the claim-language and phase-gate
    scoped sprint.
  - Reframed phase-gate ledger consistency as a control-plane check rather
    than a trigger for broad validation after every small patch.
  - Set the next dependency-safe slice to artifact-invalidation reviewer
    evidence consumption.
- `src/realworld/artifact_invalidation_matrix.py`
  - Added `write_artifact_invalidation_closeout_rows(...)` so a concrete
    closeout worksheet can be rewritten without creating reviewer evidence or
    promotion flags.
  - Added `apply_artifact_invalidation_reviewer_evidence(...)` to scan an
    evidence directory for JSON reviewer records and apply only valid,
    hash-linked, row-matching closeout evidence.
  - Required reviewer evidence records to use
    `record_type=artifact_invalidation_closeout_reviewer_evidence`,
    `scope=artifact_invalidation_closeout_only`, and
    `decision=signed_off_for_invalidation_closeout_only`.
  - Required referenced support `evidence_paths` inside the reviewer record to
    exist on disk.
  - Preserved fail-closed behavior for publication readiness, final-study
    readiness, and formal acceptance evidence.
- `scripts/write_artifact_invalidation_matrix.py`
  - Added `--apply-reviewer-evidence-dir`.
  - Added `--apply-reviewer-evidence-closeout-input`.
  - Rewrites the selected closeout CSV, manifest, and doc only after applying
    valid reviewer evidence.
- `tests/test_realworld_artifact_invalidation_matrix.py`
  - Added regression coverage for valid hash-linked reviewer evidence.
  - Added rejection coverage for reviewer evidence that references a missing
    support path.
  - Added CLI coverage for applying reviewer evidence to a filled closeout CSV.

## Verification

Focused verification run for this slice:

| command | result | claim impact |
| --- | --- | --- |
| `.\.venv\Scripts\python -m py_compile src\realworld\artifact_invalidation_matrix.py scripts\write_artifact_invalidation_matrix.py tests\test_realworld_artifact_invalidation_matrix.py` | exit 0 | Syntax check for touched Python files. |
| `.\.venv\Scripts\python tests\test_realworld_artifact_invalidation_matrix.py` | exit 0 | Focused artifact-invalidation regression suite passed after fixture correction. |
| `.\.venv\Scripts\python scripts\write_artifact_invalidation_matrix.py --write-action-batch-inspection --write-closeout-readiness-audit` | exit 0 | Regenerated support audits; all 51 rows remain blocked. |
| `.\.venv\Scripts\python scripts\audit_claim_language.py --fail-on-blockers` | exit 0 | Claim-language guard still reports zero blocking findings. |
| `git diff --check -- <touched artifact-invalidation paths>` | exit 0 | Whitespace check for touched artifact-invalidation source, tests, and generated audit files. |
| `.\.venv\Scripts\python scripts\audit_plan_artifacts.py` | exit 1 | Expected broad closeout failure; artifact invalidation and other study gates remain blocked. |
| `.\.venv\Scripts\python tests\test_realworld_phase_gate_ledger.py` | exit 0 | Phase-gate ledger test still passes after plan checkpoint update. |

## Gate Impact

- Promoted phases: none.
- Cleared artifact-invalidation rows: none.
- New reviewer evidence records written: none.
- Publication readiness: unchanged, still not supported by this sprint.
- Final-study readiness: unchanged, still not supported by this sprint.
- Formal acceptance evidence: unchanged, still not supported by this sprint.

## Remaining Blockers

The implementation path for reviewer evidence now exists, but the gate remains
blocked until actual row-level reviewer JSON records exist and pass the new
hash/path checks.

Immediate blocker:

- 51 artifact-invalidation closeout rows still have no current structured
  reviewer evidence.

Dependency-safe next work:

1. Generate or obtain real row-level reviewer evidence for the first
   `quarantine_non_evidence` batch only, or keep it blocked if reviewers reject
   the rows.
2. Apply the evidence with
   `scripts\write_artifact_invalidation_matrix.py --apply-reviewer-evidence-dir ... --apply-reviewer-evidence-closeout-input ...`.
3. Regenerate action-batch inspection and closeout-readiness audit.
4. Only then evaluate whether the next action batch can proceed.

## Claim Boundary

This sprint added a safe evidence-consumption path. It does not approve any
artifact, does not close Phase 9, does not establish final-study readiness, and
does not replace missing reviewer evidence.
