# Manuscript/Report Decision Packet

Manuscript/report decision packet only; not manuscript acceptance, not evidence-gate acceptance, not calibrated real-world validation, and not operational routing approval. It cannot create or replace data/manifests/manuscript_acceptance.json.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Decision rows: 7
- Blocking decisions: 4
- Human-review decisions: 3
- Status counts: `{'blocked_claim_alignment_review_dependency': 1, 'blocked_figure_table_review_dependency': 1, 'blocked_missing_manuscript_acceptance_record': 1, 'blocked_upstream_evidence_gate_dependency': 1, 'needs_human_review_docx_regeneration': 1, 'needs_human_review_korean_report_scope': 1, 'needs_human_review_paper_claims': 1}`

## Decision Rows

| Decision | Status | Evidence | Required Action |
| --- | --- | --- | --- |
| paper_claim_review_decision | needs_human_review_paper_claims | paper_present=true; paper_line_count=1275; paper_claim_rows=121; overclaim_candidate_count=91; guardrail_language_count=39 | Review paper claim rows and revise any language that implies accepted validation, calibration, operational use, or finality. |
| korean_report_review_decision | needs_human_review_korean_report_scope | report_present=true; report_line_count=229; report_claim_rows=1; overclaim_candidate_count=91; guardrail_language_count=39 | Review Korean report text against current scaffold limitations and regenerate the docx only after accepted manuscript changes. |
| figure_table_use_decision | blocked_figure_table_review_dependency | figures=6; tables=5; result_scope=Generated from current pilot scaffold CSVs only; not calibrated real-world results or an operational forecast.; blocking_review_count=3; human_review_count=5 | Resolve figure/table blocker rows and keep captions in scaffold scope until formal manuscript acceptance. |
| result_claim_alignment_decision | blocked_claim_alignment_review_dependency | claim_rows=130; overclaim_candidate_count=91; guardrail_language_count=39; review_status_counts={'guardrail_language': 39, 'requires_revision_or_acceptance': 91} | Review or revise every overclaim candidate before recording result_claims_aligned in manuscript acceptance. |
| upstream_evidence_gate_dependency | blocked_upstream_evidence_gate_dependency | ready_gate_count=0; blocked_gate_count=0; blocked_upstream_gates=pilot_region_accepted,cached_osm_input,graph_scale_strategy,data_provenance,parameter_evidence,rail_evidence,validation_package,sensitivity_analysis,full_experiment_output | Keep manuscript/report result language in scaffold scope until the upstream evidence gates are accepted or explicitly limited. |
| docx_regeneration_decision | needs_human_review_docx_regeneration | report_docx_present=true; report_docx_size_bytes=1347735; report_source_present=true; report_source_size_bytes=32120 | Regenerate and review report.docx after any accepted report or figure/table changes. |
| formal_manuscript_acceptance_boundary | blocked_missing_manuscript_acceptance_record | manuscript_acceptance_present=false | Record formal manuscript acceptance only after placeholders are removed and source-backed evidence decisions support the claims. |

## Boundary

- This packet does not approve paper, report, docx, figure, or table claims.
- It does not replace pilot, provenance, graph-scale, input-evidence, validation, sensitivity, experiment, or manuscript acceptance.
- Keep manuscript/report claims in scaffold scope until formal manuscript acceptance is reviewed.
