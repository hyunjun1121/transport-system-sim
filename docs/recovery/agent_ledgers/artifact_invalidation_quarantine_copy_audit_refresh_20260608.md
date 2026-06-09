# Artifact Invalidation Quarantine Copy-Audit Refresh - 2026-06-08

## Scope

Refreshed the Phase 9 `quarantine_non_evidence` support artifacts after
reviewers found that the copy-audit and draft-overlay manifests referenced an
older main closeout CSV hash.

This work is support-only. It does not create formal acceptance evidence, does
not close artifact invalidation rows, and does not authorize Phase 9 promotion.

## Sub-Agent Review Evidence

- `019ea60e-07d5-70c1-9efa-0fdd0b82378d`
  - Role: adversarial claim-boundary reviewer.
  - Finding: copy-audit and draft-overlay inputs were stale relative to the
    current authoritative closeout CSV. Recommended regenerating those support
    artifacts after any authoritative-row change, while keeping readiness flags
    false.
- `019ea60d-fffa-7fc1-a379-14ab781fe0be`
  - Role: artifact-invalidation evidence reviewer.
  - Finding: the six `quarantine_non_evidence` rows remain blocked. Existing
    evidence supports candidate path/hash scope only, not row closure or
    gate-clear status.

## Files Regenerated

- `data/validation/artifact_invalidation_quarantine_main_closeout_copy_audit.csv`
- `data/validation/artifact_invalidation_quarantine_main_closeout_copy_audit_manifest.json`
- `docs/artifact_invalidation_quarantine_main_closeout_copy_audit.md`
- `data/validation/artifact_invalidation_quarantine_main_closeout_draft_overlay.csv`
- `data/validation/artifact_invalidation_quarantine_main_closeout_draft_overlay_manifest.json`
- `docs/artifact_invalidation_quarantine_main_closeout_draft_overlay.md`
- `data/validation/artifact_invalidation_matrix.csv`
- `data/validation/artifact_invalidation_matrix_manifest.json`
- `docs/artifact_invalidation_matrix.md`

The authoritative closeout CSV was not edited in this slice.

## Commands Run

```powershell
.\.venv\Scripts\python scripts\write_artifact_invalidation_matrix.py --write-quarantine-main-closeout-copy-audit --write-quarantine-main-closeout-draft-overlay
.\.venv\Scripts\python tests\test_realworld_artifact_invalidation_matrix.py
.\.venv\Scripts\python scripts\audit_claim_language.py
.\.venv\Scripts\python scripts\audit_plan_artifacts.py
```

## Results

- `tests\test_realworld_artifact_invalidation_matrix.py` passed.
- `scripts\audit_claim_language.py` regenerated the required global guard
  outputs. It remains release-blocked with `blocking_finding_count=46`.
- `scripts\audit_plan_artifacts.py` reports:
  - `all_required_artifacts_present=true`
  - `verdict=executable_quasi_real_scaffold_not_final_calibrated_study`
  - `phase9_promotion_ready=false`
  - `closeout_pending_or_invalid_row_count=51`
  - CSV/DOC/JSON required artifact check failures: `0`

Regenerated copy-audit manifest now records the current main closeout CSV hash:

- `source_main_closeout_sha256=21a94b5a8922e887de20cfb1d84449e1ac0ad7d0ff1c10e29e5253d7a62c4200`

## Gate Impact

- Promoted phases: none.
- Closed rows: none.
- Closed gates: none.
- `phase9_promotion_ready=false`
- `publication_ready=false`
- `final_study_ready=false`
- `formal_acceptance_evidence=false`

## Remaining Blocker

All 51 artifact-invalidation rows still fail because reviewer evidence is not
current closeout evidence. The six quarantine rows remain blocked by
`obsolete_human_reviewer_marker` and `can_clear_invalidation_gate=false`.
