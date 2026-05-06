# Manuscript And Report Acceptance Schema

> Current project status (2026-05-06): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


## Purpose

`data/manifests/manuscript_acceptance.json` is the explicit review record that
can close the final-study manuscript/report-alignment gate.

Paper and report files may exist while still describing scaffold results. They
become final-study evidence only after the paper, Korean report, generated
Word document, figure/table manifest, evidence gates, result claims, and claim
boundaries are reviewed together.

Do not create this file to make audits pass. Create it only after a real review
accepts the manuscript/report package for a quasi-real decision-support study.

## Location

```text
data/manifests/manuscript_acceptance.json
```

The current scaffold intentionally does not include this file.

## Required Fields

| Field | Type | Requirement |
| --- | --- | --- |
| `region_id` | string | Non-empty pilot region identifier. |
| `accepted` | boolean | Must be `true` only after review. |
| `accepted_by` | string | Reviewer, group, or decision record identifier. |
| `accepted_date` | string | Review date in `YYYY-MM-DD` form where possible. |
| `paper_reviewed` | boolean | Must be `true` after English manuscript review. |
| `korean_report_reviewed` | boolean | Must be `true` after Korean report-source review. |
| `docx_regenerated` | boolean | Must be `true` after Word report regeneration from source. |
| `figure_table_manifest_reviewed` | boolean | Must be `true` after figure/table manifest review. |
| `evidence_gates_reviewed` | boolean | Must be `true` after final evidence gates are checked. |
| `result_claims_aligned` | boolean | Must be `true` after result text matches accepted outputs. |
| `claim_boundary` | string | Must include `not operational`. |
| `evidence_paths` | array of strings | Non-empty list of reviewed paper, report, figure, table, and audit artifacts. |

## Example Shape

```json
{
  "region_id": "songpa_public_demo",
  "accepted": true,
  "accepted_by": "review record id",
  "accepted_date": "2026-05-04",
  "paper_reviewed": true,
  "korean_report_reviewed": true,
  "docx_regenerated": true,
  "figure_table_manifest_reviewed": true,
  "evidence_gates_reviewed": true,
  "result_claims_aligned": true,
  "claim_boundary": "Accepted for quasi-real decision-support analysis; not operational routing.",
  "evidence_paths": [
    "paper/paper_draft.md",
    "report_draft.md",
    "report.docx",
    "results/realworld_pilot/tables/figure_table_manifest.json",
    "docs/final_study_audit.md"
  ]
}
```

This example is a schema illustration only. It is not evidence that the current
paper or report is final-study aligned.

## Validation

The schema is enforced by:

```powershell
.\.venv\Scripts\python tests\test_realworld_manuscript_acceptance.py
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
```

The final-study readiness audit also requires publication evidence gates and
figure/table claim boundaries to be final-study scoped. A manuscript acceptance
record alone cannot close the gate while the evidence package remains blocked.
