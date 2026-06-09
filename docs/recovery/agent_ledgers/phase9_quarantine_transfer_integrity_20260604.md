# Phase 9 Quarantine Transfer Integrity Ledger - 2026-06-04

## Scope

This ledger records a narrow Phase 9 support update for the immediate
`quarantine_non_evidence` transfer packet. It is reviewer triage only. It is
not closeout evidence, not reviewer signoff, not artifact regeneration
evidence, not publication readiness, not final-study approval, and not formal
acceptance.

## Objective

Make stale full-output and review-package candidate artifacts easier to verify
before any reviewer copies confirmed entries into the main artifact invalidation
closeout record.

## Edits

- Enriched each `candidate_artifacts_json` object in the quarantine transfer
  packet with:
  - `current_integrity_status`
  - `current_sha256`
  - `hash_matches_current_file`
- Added aggregate transfer-packet manifest and Markdown counts for:
  - candidate artifact hash matches
  - missing candidate artifacts
  - hash-mismatched candidate artifacts
- Tightened transfer-packet validation so candidate artifact integrity fields
  must be present and well-formed.
- Added a regression test that mutates a candidate artifact after the index is
  built and verifies the transfer packet reports `hash_mismatch`.

## Evidence Commands

```powershell
.\.venv\Scripts\python -m py_compile src\realworld\artifact_invalidation_matrix.py tests\test_realworld_artifact_invalidation_matrix.py
.\.venv\Scripts\python tests\test_realworld_artifact_invalidation_matrix.py
.\.venv\Scripts\python scripts\write_artifact_invalidation_matrix.py --write-quarantine-closeout-template --write-quarantine-scope-audit --write-quarantine-non-evidence-index --write-quarantine-non-evidence-transfer-packet
.\.venv\Scripts\python scripts\audit_claim_language.py --fail-on-blockers
.\.venv\Scripts\python tests\test_realworld_claim_language_guard.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
git diff --check -- src\realworld\artifact_invalidation_matrix.py tests\test_realworld_artifact_invalidation_matrix.py data\validation\artifact_invalidation_quarantine_non_evidence_transfer_packet.csv data\validation\artifact_invalidation_quarantine_non_evidence_transfer_packet_manifest.json docs\artifact_invalidation_quarantine_non_evidence_transfer_packet.md
```

## Results

- Artifact invalidation tests passed.
- Claim-language guard passed with `blocking_finding_count=0`.
- Plan audit test passed.
- `git diff --check` returned no whitespace findings for the touched files.
- The regenerated transfer packet reported:
  - candidate artifacts: 73
  - candidate artifact hash matches: 73
  - candidate artifact missing: 0
  - candidate artifact hash mismatches: 0
  - source integrity ready: true

## Remaining Blockers

- This transfer packet remains `draft_pending_reviewer_confirmation`.
- The six quarantine rows still require reviewer confirmation, copied main
  closeout entries, citation-removal or exclusion audit evidence, and
  non-acceptance signoff.
- The full artifact invalidation matrix still has 51 unresolved blocking rows.
- `phase9_promotion_ready=false`, `publication_ready=false`,
  `final_study_ready=false`, and `formal_acceptance_evidence=false` remain
  unchanged.

