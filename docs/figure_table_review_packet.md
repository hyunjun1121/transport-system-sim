# Figure/Table Review Packet

Figure/table review packet only; not manuscript decision, not calibrated real-world results, and not operational routing evidence. It cannot create or replace data/manifests/manuscript_acceptance.json.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Review rows: 8
- Blocking reviews: 2
- Human-review rows: 6
- Status counts: `{'blocked_reduced_graph_scope_dependency': 1, 'blocked_upstream_evidence_dependency': 1, 'needs_human_review_artifact_inventory': 1, 'needs_human_review_caption_boundary': 1, 'needs_human_review_formal_manuscript_acceptance': 1, 'needs_human_review_morris_index_handling': 1, 'needs_human_review_proxy_interpretation': 1, 'needs_human_review_table_lineage': 1}`

## Review Rows

| Review | Status | Evidence | Required Action |
| --- | --- | --- | --- |
| artifact_inventory | needs_human_review_artifact_inventory | figures=6; tables=5; missing_paths=0 | Confirm every listed figure/table exists and is regenerated from the current pilot and sensitivity outputs. |
| table_lineage_and_row_counts | needs_human_review_table_lineage | manifest_row_counts=bottleneck_attribution_table=414; claim_boundary_table=3; main_result_table=414; policy_regime_table=54; sensitivity_result_table=61824; row_count_mismatches=0 | Verify tables were regenerated from current CSV outputs and that row counts match the manifest before manuscript review. |
| caption_and_claim_boundary | needs_human_review_caption_boundary | result_scope=Generated from current pilot scaffold CSVs only; not calibrated real-world results or an operational forecast.; claim_boundary=All generated artifacts are scaffold-only outputs and must not be described as calibrated real-world or operational outputs.; captions_missing_boundary=0 | Keep captions and table language explicit that current figures are scaffold-only until final evidence gates and manuscript acceptance close. |
| graph_scope_dependency | blocked_reduced_graph_scope_dependency | pilot: source=197823/298020; analysis=2850/3002; reduced=true; sensitivity: source=4608/9148; analysis=118/174; reduced=true | Review graph-scale acceptance before using figures/tables as publication-result evidence. |
| sensitivity_index_handling | needs_human_review_morris_index_handling | morris_index_handling_fields=audit,figures,tables; selected_metric=penalized_makespan | Review how blank, masked, NaN, or non-finite Morris rows are kept in tables and excluded from plotted top rankings. |
| bottleneck_and_regime_interpretation | needs_human_review_proxy_interpretation | bottleneck_rows=414; policy_regime_rows=54 | Treat bottleneck attribution and policy-regime rows as proxy interpretation aids, not causal bottleneck evidence, until benchmark-reviewed and decision-reviewed. |
| upstream_evidence_dependency | blocked_upstream_evidence_dependency | source_scopes_scaffold=true; result_scope=Generated from current pilot scaffold CSVs only; not calibrated real-world results or an operational forecast. | Do not promote current figures/tables into release-scope manuscript claims until pilot inputs, validation, experiments, and sensitivity outputs are decision-reviewed or regenerated. |
| formal_manuscript_acceptance_boundary | needs_human_review_formal_manuscript_acceptance | manuscript_acceptance_present=true | Record figure/table review only in formal manuscript acceptance after evidence gates and result claims are reviewed. |

## Boundary

- This packet does not approve figure/table use in release-scope manuscript claims.
- It does not replace graph-scale, experiment, sensitivity, benchmark, or manuscript decision records.
- Keep figures/tables in scaffold scope until the formal manuscript decision is reviewed.
