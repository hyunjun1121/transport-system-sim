# Manuscript Report Alignment Review Packet

Sub-agent records are review aids. They do not replace formal acceptance artifacts, source-backed reviewer decisions, calibrated validation, or operational routing approval.

- Gate ID: `manuscript_report_alignment`
- Agent: `Paper / Report Claim Alignment Agent`
- Status: `blocked`
- Can mark complete: `false`
- Generated at: `2026-05-10T08:28:03+00:00`

## Decision

Paper / Report Claim Alignment Agent cannot accept gate manuscript_report_alignment; the current final-study readiness audit reports blockers.

## Reviewed Inputs

- scripts/audit_publication_readiness.py
- docs/current_goal_completion_audit.md
- data/manifests/current_goal_completion_audit.json
- paper/paper_draft.md
- report_draft.md
- data/manifests/claim_alignment_review_manifest.json
- data/manifests/figure_table_review_manifest.json
- data/manifests/manuscript_report_decision_manifest.json
- docs/figure_table_review_packet.md
- docs/manuscript_report_decision_packet.md
- data/manifests/manuscript_acceptance.json
- report.docx
- results/realworld_pilot/tables/figure_table_manifest.json
- data/manifests/figure_table_review_packet.csv
- data/manifests/claim_alignment_review_packet.csv
- docs/claim_alignment_review_packet.md
- data/manifests/manuscript_report_decision_packet.csv

## Evidence And Source Paths

- data/manifests/manuscript_acceptance.json
- paper/paper_draft.md
- report_draft.md
- report.docx
- results/realworld_pilot/tables/figure_table_manifest.json
- data/manifests/figure_table_review_packet.csv
- data/manifests/figure_table_review_manifest.json
- docs/figure_table_review_packet.md
- data/manifests/claim_alignment_review_packet.csv
- data/manifests/claim_alignment_review_manifest.json
- docs/claim_alignment_review_packet.md
- data/manifests/manuscript_report_decision_packet.csv
- data/manifests/manuscript_report_decision_manifest.json
- docs/manuscript_report_decision_packet.md
- docs/review_packets/manuscript_report_alignment.md

## Risks

- Paper/report can overstate scaffold results as calibrated real-world findings.
- Figures and tables can imply finality before evidence gates close.
- close evidence gates before final paper/report claims
- create an explicit manuscript/report acceptance record after evidence gates, figures, paper, report, and claim boundaries are reviewed
- revise figure/table claim boundary from scaffold to accepted study scope
- resolve figure/table review blockers before manuscript acceptance
- figure/table review: figure/table outputs depend on reduced analysis graph scope
- figure/table review: figure/table source outputs remain scaffold or not calibrated
- figure/table review: data/manifests/manuscript_acceptance.json is absent
- review figure/table human-review rows before manuscript acceptance
- review or revise claim-alignment overclaim candidates before manuscript acceptance
- claim alignment: formal manuscript/report acceptance record is absent
- claim alignment: claim-alignment rows are review aids and do not approve manuscript claims
- claim alignment: evidence gates remain blocked, so result claims cannot be accepted as final-study claims
- resolve manuscript/report decision blockers before manuscript acceptance
- manuscript/report decision: figure/table outputs depend on reduced analysis graph scope; figure/table source outputs remain scaffold or not calibrated; data/manifests/manuscript_acceptance.json is absent
- manuscript/report decision: claim-alignment packet has 91 rows requiring revision or acceptance
- manuscript/report decision: upstream evidence gates blocked: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output
- manuscript/report decision: data/manifests/manuscript_acceptance.json is absent
- review manuscript/report human-decision rows before manuscript acceptance

## Required Actions

- Revise or hold claims until all supporting evidence gates are accepted.
- Create manuscript_acceptance.json after claim-by-claim review.
- close evidence gates before final paper/report claims
- create an explicit manuscript/report acceptance record after evidence gates, figures, paper, report, and claim boundaries are reviewed
- revise figure/table claim boundary from scaffold to accepted study scope
- resolve figure/table review blockers before manuscript acceptance
- figure/table review: figure/table outputs depend on reduced analysis graph scope
- figure/table review: figure/table source outputs remain scaffold or not calibrated
- figure/table review: data/manifests/manuscript_acceptance.json is absent
- review figure/table human-review rows before manuscript acceptance
- review or revise claim-alignment overclaim candidates before manuscript acceptance
- claim alignment: formal manuscript/report acceptance record is absent
- claim alignment: claim-alignment rows are review aids and do not approve manuscript claims
- claim alignment: evidence gates remain blocked, so result claims cannot be accepted as final-study claims
- resolve manuscript/report decision blockers before manuscript acceptance
- manuscript/report decision: figure/table outputs depend on reduced analysis graph scope; figure/table source outputs remain scaffold or not calibrated; data/manifests/manuscript_acceptance.json is absent
- manuscript/report decision: claim-alignment packet has 91 rows requiring revision or acceptance
- manuscript/report decision: upstream evidence gates blocked: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output
- manuscript/report decision: data/manifests/manuscript_acceptance.json is absent
- review manuscript/report human-decision rows before manuscript acceptance

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
    "resolve figure/table review blockers before manuscript acceptance",
    "figure/table review: figure/table outputs depend on reduced analysis graph scope",
    "figure/table review: figure/table source outputs remain scaffold or not calibrated",
    "figure/table review: data/manifests/manuscript_acceptance.json is absent",
    "review figure/table human-review rows before manuscript acceptance",
    "review or revise claim-alignment overclaim candidates before manuscript acceptance",
    "claim alignment: formal manuscript/report acceptance record is absent",
    "claim alignment: claim-alignment rows are review aids and do not approve manuscript claims",
    "claim alignment: evidence gates remain blocked, so result claims cannot be accepted as final-study claims",
    "resolve manuscript/report decision blockers before manuscript acceptance",
    "manuscript/report decision: figure/table outputs depend on reduced analysis graph scope; figure/table source outputs remain scaffold or not calibrated; data/manifests/manuscript_acceptance.json is absent",
    "manuscript/report decision: claim-alignment packet has 91 rows requiring revision or acceptance",
    "manuscript/report decision: upstream evidence gates blocked: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output",
    "manuscript/report decision: data/manifests/manuscript_acceptance.json is absent",
    "review manuscript/report human-decision rows before manuscript acceptance"
  ],
  "details": {
    "acceptance_path": "data/manifests/manuscript_acceptance.json",
    "acceptance_record_present": false,
    "claim_alignment_claim_category_counts": {
      "acceptance_claim": 25,
      "calibration_claim": 19,
      "causal_or_superiority_claim": 4,
      "figure_caption_boundary": 6,
      "figure_table_boundary": 2,
      "operational_claim": 23,
      "publication_claim": 4,
      "readiness_claim": 3,
      "real_world_claim": 4,
      "validation_claim": 40
    },
    "claim_alignment_gate_dependency_counts": {
      "final_audit": 25,
      "manuscript_report_alignment": 46,
      "parameter_evidence": 19,
      "validation_package": 40
    },
    "claim_alignment_guardrail_language_count": 39,
    "claim_alignment_overclaim_candidate_count": 91,
    "claim_alignment_publication_ready": false,
    "claim_alignment_remaining_blockers": [
      "formal manuscript/report acceptance record is absent",
      "claim-alignment rows are review aids and do not approve manuscript claims",
      "evidence gates remain blocked, so result claims cannot be accepted as final-study claims"
    ],
    "claim_alignment_review_manifest_present": true,
    "claim_alignment_review_row_count": 130,
    "claim_alignment_review_status_counts": {
      "guardrail_language": 39,
      "requires_revision_or_acceptance": 91
    },
    "figure_claim_boundary_scope_blocked": true,
    "figure_table_review_blocking_review_count": 3,
    "figure_table_review_can_mark_complete": false,
    "figure_table_review_human_review_count": 5,
    "figure_table_review_manifest_present": true,
    "figure_table_review_publication_ready": false,
    "figure_table_review_remaining_blockers": [
      "figure/table outputs depend on reduced analysis graph scope",
      "figure/table source outputs remain scaffold or not calibrated",
      "data/manifests/manuscript_acceptance.json is absent"
    ],
    "figure_table_review_status_counts": {
      "blocked_missing_manuscript_acceptance_record": 1,
      "blocked_reduced_graph_scope_dependency": 1,
      "blocked_upstream_evidence_dependency": 1,
      "needs_human_review_artifact_inventory": 1,
      "needs_human_review_caption_boundary": 1,
      "needs_human_review_morris_index_handling": 1,
      "needs_human_review_proxy_interpretation": 1,
      "needs_human_review_table_lineage": 1
    },
    "manuscript_report_decision_blocking_decision_count": 4,
    "manuscript_report_decision_can_mark_complete": false,
    "manuscript_report_decision_human_review_decision_count": 3,
    "manuscript_report_decision_manifest_present": true,
    "manuscript_report_decision_publication_ready": false,
    "manuscript_report_decision_remaining_blockers": [
      "figure/table outputs depend on reduced analysis graph scope; figure/table source outputs remain scaffold or not calibrated; data/manifests/manuscript_acceptance.json is absent",
      "claim-alignment packet has 91 rows requiring revision or acceptance",
      "upstream evidence gates blocked: pilot_region_accepted, cached_osm_input, graph_scale_strategy, data_provenance, parameter_evidence, rail_evidence, validation_package, sensitivity_analysis, full_experiment_output",
      "data/manifests/manuscript_acceptance.json is absent"
    ],
    "manuscript_report_decision_row_count": 7,
    "manuscript_report_decision_status_counts": {
      "blocked_claim_alignment_review_dependency": 1,
      "blocked_figure_table_review_dependency": 1,
      "blocked_missing_manuscript_acceptance_record": 1,
      "blocked_upstream_evidence_gate_dependency": 1,
      "needs_human_review_docx_regeneration": 1,
      "needs_human_review_korean_report_scope": 1,
      "needs_human_review_paper_claims": 1
    },
    "publication_ready": false
  },
  "evidence": [
    "data/manifests/manuscript_acceptance.json",
    "paper/paper_draft.md",
    "report_draft.md",
    "report.docx",
    "results/realworld_pilot/tables/figure_table_manifest.json",
    "data/manifests/figure_table_review_packet.csv",
    "data/manifests/figure_table_review_manifest.json",
    "docs/figure_table_review_packet.md",
    "data/manifests/claim_alignment_review_packet.csv",
    "data/manifests/claim_alignment_review_manifest.json",
    "docs/claim_alignment_review_packet.md",
    "data/manifests/manuscript_report_decision_packet.csv",
    "data/manifests/manuscript_report_decision_manifest.json",
    "docs/manuscript_report_decision_packet.md"
  ],
  "gate_id": "manuscript_report_alignment",
  "label": "Manuscript Report Alignment",
  "ready": false
}
```
