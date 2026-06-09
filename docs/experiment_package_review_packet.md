# Experiment Package Review Packet

Experiment-package review packet only; not experiment acceptance, not calibrated real-world validation, and not operational routing approval. A reviewer must still create data/manifests/experiment_acceptance.json after graph scope, input checks, scenario-policy-seed design, CRN pairing, counts, and claim boundaries are reviewed.

## Verdict

- Publication ready: `false`
- Acceptance ready: `false`
- Can mark complete: `false`
- Review rows: 9
- Count mismatches: 0

## Review Rows

| Category | Artifact | Status | Rows | Required Action |
| --- | --- | --- | --- | --- |
| manifest_scope | results/realworld_pilot/phase8_compact_scoped_20260605/pilot_staged_manifest.json | review_required_scaffold_or_not_calibrated_scope | 315 / 315 | Confirm result_scope is bounded to decision support and update only through formal experiment acceptance. |
| results_row_count | results/realworld_pilot/phase8_compact_scoped_20260605/pilot_staged_results.csv | ready_for_review_count_matches | 315 / 315 | Verify full result rows match the manifest and were regenerated after the reviewer-selected graph/input scope was documented. |
| summary_row_count | results/realworld_pilot/phase8_compact_scoped_20260605/pilot_staged_summary.csv | ready_for_review_count_matches | 63 / 63 | Verify summary rows match the manifest and summarize only the review-selected run profile. |
| scenario_policy_seed_design | data/manifests/pilot_experiment_design.json | ready_for_review_design_counts_match | 315 / 315 | Confirm policies, scenarios, seeds, exclusions, and row-count multiplication before accepting the experiment package. |
| graph_scope_dependency | data/manifests/graph_scale_acceptance.json | blocked_until_graph_scale_acceptance | 118 / 4608 | Close graph-scale method review or regenerate outputs on the selected graph method before using full experiment outputs. |
| input_evidence_dependency | data/manifests/experiment_acceptance.json | blocked_until_input_evidence_acceptance | 12 / 5 | Confirm all input source, road override, parameter, validation, and provenance gates before accepting current outputs. |
| common_random_numbers | results/realworld_pilot/pilot_full_manifest.json | ready_for_review_crn_declared | 5 / 5 | Confirm same-seed paired comparisons and scenario runner seed splitting before accepting paired policy claims. |
| artifact_checksums | results/realworld_pilot/phase8_compact_scoped_20260605/pilot_staged_manifest.json | ready_for_review_checksums_available | 3 / 3 | Record these checksums or regenerated equivalents in the formal experiment decision evidence. |
| formal_experiment_acceptance_requirement | data/manifests/experiment_acceptance.json | blocked_formal_acceptance_absent | 0 / 1 | Create or review experiment_acceptance.json only after graph scope, input checks, scenario-policy-seed design, CRN, counts, and claim boundary are genuinely reviewed. |

## Required Reviewer Actions

- Review `results/realworld_pilot/pilot_full_manifest.json` with the full result and summary CSVs.
- Confirm graph-scale, input checks, scenario-policy-seed, and CRN decisions before the experiment decision.
- Retain artifact checksums in the experiment decision evidence when the run package is reviewer-selected.
- Create `data/manifests/experiment_acceptance.json` only after a real review decision.
