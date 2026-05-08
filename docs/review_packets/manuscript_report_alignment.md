# Manuscript Report Alignment Review Packet

Sub-agent records are review aids. They do not replace formal acceptance artifacts, source-backed reviewer decisions, calibrated validation, or operational routing approval.

- Gate ID: `manuscript_report_alignment`
- Agent: `Paper / Report Claim Alignment Agent`
- Status: `blocked`
- Can mark complete: `false`
- Generated at: `2026-05-08T13:32:46+00:00`

## Decision

Paper / Report Claim Alignment Agent cannot accept gate manuscript_report_alignment; the current final-study readiness audit reports blockers.

## Reviewed Inputs

- scripts/audit_publication_readiness.py
- docs/current_goal_completion_audit.md
- paper/paper_draft.md
- report_draft.md
- data/manifests/claim_alignment_review_manifest.json
- data/manifests/manuscript_acceptance.json
- report.docx
- results/realworld_pilot/tables/figure_table_manifest.json
- data/manifests/claim_alignment_review_packet.csv
- docs/claim_alignment_review_packet.md

## Evidence And Source Paths

- data/manifests/manuscript_acceptance.json
- paper/paper_draft.md
- report_draft.md
- report.docx
- results/realworld_pilot/tables/figure_table_manifest.json
- data/manifests/claim_alignment_review_packet.csv
- data/manifests/claim_alignment_review_manifest.json
- docs/claim_alignment_review_packet.md
- docs/review_packets/manuscript_report_alignment.md

## Risks

- Paper/report can overstate scaffold results as calibrated real-world findings.
- Figures and tables can imply finality before evidence gates close.
- close evidence gates before final paper/report claims
- create an explicit manuscript/report acceptance record after evidence gates, figures, paper, report, and claim boundaries are reviewed
- revise figure/table claim boundary from scaffold to accepted study scope
- review or revise claim-alignment overclaim candidates before manuscript acceptance
- claim alignment: formal manuscript/report acceptance record is absent
- claim alignment: claim-alignment rows are review aids and do not approve manuscript claims
- claim alignment: evidence gates remain blocked, so result claims cannot be accepted as final-study claims

## Required Actions

- Revise or hold claims until all supporting evidence gates are accepted.
- Create manuscript_acceptance.json after claim-by-claim review.
- close evidence gates before final paper/report claims
- create an explicit manuscript/report acceptance record after evidence gates, figures, paper, report, and claim boundaries are reviewed
- revise figure/table claim boundary from scaffold to accepted study scope
- review or revise claim-alignment overclaim candidates before manuscript acceptance
- claim alignment: formal manuscript/report acceptance record is absent
- claim alignment: claim-alignment rows are review aids and do not approve manuscript claims
- claim alignment: evidence gates remain blocked, so result claims cannot be accepted as final-study claims

## Formal Acceptance Boundary

To close this final-study gate, create or update the formal acceptance artifact listed in the agent definition. Do not edit this review packet as a substitute for formal acceptance.

Formal acceptance artifacts:

- data/manifests/manuscript_acceptance.json

## Current Final-Study Gate Details

```json
{
  "artifact_present": true,
  "blockers": [
    "close evidence gates before final paper/report claims",
    "create an explicit manuscript/report acceptance record after evidence gates, figures, paper, report, and claim boundaries are reviewed",
    "revise figure/table claim boundary from scaffold to accepted study scope",
    "review or revise claim-alignment overclaim candidates before manuscript acceptance",
    "claim alignment: formal manuscript/report acceptance record is absent",
    "claim alignment: claim-alignment rows are review aids and do not approve manuscript claims",
    "claim alignment: evidence gates remain blocked, so result claims cannot be accepted as final-study claims"
  ],
  "details": {
    "acceptance_path": "data/manifests/manuscript_acceptance.json",
    "acceptance_record_present": false,
    "claim_alignment_claim_category_counts": {
      "acceptance_claim": 20,
      "calibration_claim": 19,
      "causal_or_superiority_claim": 4,
      "figure_caption_boundary": 6,
      "figure_table_boundary": 2,
      "operational_claim": 23,
      "publication_claim": 4,
      "readiness_claim": 3,
      "real_world_claim": 4,
      "validation_claim": 46
    },
    "claim_alignment_gate_dependency_counts": {
      "final_audit": 20,
      "manuscript_report_alignment": 46,
      "parameter_evidence": 19,
      "validation_package": 46
    },
    "claim_alignment_guardrail_language_count": 23,
    "claim_alignment_overclaim_candidate_count": 108,
    "claim_alignment_publication_ready": false,
    "claim_alignment_remaining_blockers": [
      "formal manuscript/report acceptance record is absent",
      "claim-alignment rows are review aids and do not approve manuscript claims",
      "evidence gates remain blocked, so result claims cannot be accepted as final-study claims"
    ],
    "claim_alignment_review_manifest_present": true,
    "claim_alignment_review_row_count": 131,
    "claim_alignment_review_status_counts": {
      "guardrail_language": 23,
      "requires_revision_or_acceptance": 108
    },
    "figure_claim_boundary_scope_blocked": true,
    "publication_ready": false
  },
  "evidence": [
    "data/manifests/manuscript_acceptance.json",
    "paper/paper_draft.md",
    "report_draft.md",
    "report.docx",
    "results/realworld_pilot/tables/figure_table_manifest.json",
    "data/manifests/claim_alignment_review_packet.csv",
    "data/manifests/claim_alignment_review_manifest.json",
    "docs/claim_alignment_review_packet.md"
  ],
  "gate_id": "manuscript_report_alignment",
  "label": "Manuscript Report Alignment",
  "ready": false
}
```
