# Expert Review Submission Request: transport-system-sim

Date: 2026-05-11

## 1) Submission package (single required ZIP)

- **Bundle ZIP**: `expert_review_intake.zip`
- **Submission format for the expert**: attach only this document text and one ZIP file (`expert_review_intake.zip`).
- This archive contains the reviewed core package (`required_deliverables.zip`) plus required review sidecars, so only one file is attached.
- Verified bundle identity:
  - File count: `818`
  - Size bytes: `6457990`
  - SHA256: `e44976873570651fd78f86c0ae7e9bc67f482ee0504821d6b0e24eb19aad9b6f`
  - Missing paths: `0`
  - Excluded formal targets: `0`
  - Bundle state: `review-intake`, `acceptance-ready=false`

This is review material only and is not a final acceptance package.

## 2) Files included in the ZIP

All files required for strict reviewer intake are inside `expert_review_intake.zip`:

- `docs/review_package_build.md`
- `docs/review_package_path_audit.md`
- `docs/expert_consultation_request.md`
- `docs/expert_consultation_request_reply.md`
- `docs/expert_consultation_followup_plan.md`
- `review_packages/expert_review_handoff_20260510.md`
- `review_packages/expert_review_handoff_20260510.json`
- `docs/expert_verification_request.md`

## 3) Current blocker baseline (expected)

- `final_study_ready = false`
- Final-study gates ready: `3 / 15`
- Formal acceptance ready: `0 / 12`

All blocker statements must be supported by audited artifacts in the package.

## 4) Required review dimensions (A-I)

### A. Package completeness and traceability
- Check that the ZIP is sufficient to reproduce model mechanics, scenario runs, and audit workflows.
- Classify missing items as BLOCKER, TOLERABLE, or INTENTIONALLY_EXTERNAL.

### B. Formal acceptance artifact hygiene
- Verify strict separation of formal targets, templates, and draft sheets.
- Do not infer acceptance by filename alone (`*_acceptance.*`, `*_pre_review.*`, `accepted=false`).

### C. Pilot scope and framing
- Confirm decision-support framing is preserved and no operational dispatching claims are made.

### D. Evidence domains
- Validate road / rail / parameter / source / license / provenance evidence level:
  source-backed, declared assumption, or sensitivity-only.

### E. Graph-scale and scenario method
- Confirm graph method is explicitly chosen and interpreted consistently.
- Confirm downstream effect on figures, tables, statistics, and claims.

### F. Validation, sensitivity, and experiment integrity
- Validate CRN pairing, replication adequacy, uncertainty logic, and CI/statistical handling.

### G. Reproducibility
- Validate clean checkout reproducibility, environment controls, deterministic rerun evidence, and manifest consistency.

### H. Manuscript/report language
- Check for overclaim, operational wording, and unsupported uncertainty/calibration statements.

### I. Final-gate posture
- Confirm each final gate is either correctly blocked or truly accepted with evidence.

## 5) Required reviewer output

Please return:

1. A-I matrix using PASS / PARTIAL / BLOCKED.
2. At least 10 prioritized BLOCKED items with:
   - Issue
   - Evidence
   - Why it matters
   - Minimum correction
   - Priority (P1/P2/P3)
   - Verification check
3. Blocker ranking: Critical / High / Medium / Low.
4. One-sentence recommendation:
   - `Request another review round` or
   - `Can proceed to next review stage`

Also explicitly state whether a new review round is required.

## 6) Core files that must be inspected

- `main.py`, `config.yaml`, `requirements.txt`
- `src/*`, `scripts/*`, `tests/*`
- `data/*`, `results/*`
- `docs/*`, `paper/*`
- `plan.md`, `status.md`, `IMPLEMENTATION_PLAN.md`, `agents.md`
- `review_packages/*`

Claims must reference inspected files. If a claim depends on uninspected files, mark as limited.

## 7) Reproducible submission sequence

```powershell
.\.venv\Scripts\python scripts\write_review_package_inventory.py
.\.venv\Scripts\python scripts\build_review_package.py --output required_deliverables.zip --fail-on-missing
.\.venv\Scripts\python scripts\audit_review_package_paths.py --fail-on-missing
Copy-Item required_deliverables.zip review_packages\expert_review_package.zip
.\.venv\Scripts\python scripts\write_expert_review_handoff.py --fail-on-zip-mismatch

$staging = Join-Path (Get-Location) "tmp_expert_submission_bundle"
if (Test-Path $staging) { Remove-Item -Recurse -Force $staging }
New-Item -ItemType Directory -Path $staging | Out-Null
Expand-Archive -Path "required_deliverables.zip" -DestinationPath $staging -Force

@(
  'docs/review_package_build.md',
  'docs/review_package_path_audit.md',
  'docs/expert_consultation_request.md',
  'docs/expert_consultation_request_reply.md',
  'docs/expert_consultation_followup_plan.md',
  'review_packages/expert_review_handoff_20260510.md',
  'review_packages/expert_review_handoff_20260510.json',
  'docs/expert_verification_request.md'
) | ForEach-Object {
  $source = $_
  $target = Join-Path $staging $_
  $targetDir = Split-Path $target -Parent
  if (-not (Test-Path $targetDir)) { New-Item -ItemType Directory -Path $targetDir -Force | Out-Null }
  Copy-Item -Path $source -Destination $target -Force
}

Compress-Archive -Path (Join-Path $staging '*') -DestinationPath expert_review_intake.zip -Force
Remove-Item -Recurse -Force $staging
```

If `--fail-on-zip-mismatch` fails, treat that as an intake-preparation blocker and report it before technical scoring.

## 8) Expected baseline recommendation

Given current blockers, expected recommendation for this intake is:

- `Request another review round`

If and only if all above blockers are closed, the recommendation may be reconsidered.

## 9) Suggested validation commands for reviewers

```powershell
.\.venv\Scripts\python scripts\validate_formal_acceptance_package.py
.\.venv\Scripts\python scripts\audit_publication_readiness.py --fail-on-blockers
.\.venv\Scripts\python scripts\audit_final_study_readiness.py --fail-on-blockers
.\.venv\Scripts\python scripts\audit_review_package_paths.py --fail-on-missing
.\.venv\Scripts\python scripts\write_expert_review_handoff.py --fail-on-zip-mismatch
```

Reviewer note: if any required path in section 2 is missing, flag intake blocker status before technical scoring.
