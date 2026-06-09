# Experiment Statistical Analysis Plan

This statistical-analysis plan and scenario-policy-seed note is a pre-review planning artifact. It does not approve experiment decision artifacts, prove replication adequacy, verify common-random-number design, select a multiple-comparison procedure, or close study-closeout gates.

## Verdict

- Selected profile: `full_pilot`
- Statistical plan ready for review: `false`
- Acceptance ready: `false`
- Can mark complete: `false`
- Blocking checks: 1
- Human-review checks: 4

## Scenario-Policy-Seed Design

- Region: `songpa_public_demo`
- Graph source: `cached_graphml:data/cache/pilot_region_road.graphml`
- Analysis graph strategy: `route_corridor_reduced_with_source_and_analysis_graph_scale_recorded_until_full_network_method_is_accepted`
- Policies: 7
- Scenarios: 9
- Seeds: 30
- Expected result rows: 1890
- Observed result rows: 1890
- Expected summary rows: 63
- Observed summary rows: 63
- Common random numbers declared: `true`

## Primary Analysis Proposal

Primary metrics proposed for review:

- `completion_rate`
- `penalized_makespan`
- `p95_arrival_time`
- `passengers_per_total_service_minute`

Primary policy comparisons proposed for review:

- `bus_only` vs `baseline_multimodal`: rail-bus multimodal candidate compared with bus-only baseline

Secondary comparison boundary: All other policy, scenario, and metric contrasts remain exploratory until a reviewer selects a primary/secondary comparison family and any required multiplicity adjustment.

CI method: `normal_approximation_mean_plus_minus_1_96_standard_errors`
Multiplicity note: No formal multiple-comparison correction is accepted for the current scaffold outputs. Primary comparisons must be selected before formal experiment acceptance; all other scenario, policy, and metric comparisons are exploratory.

## Checks

| Check | Status | Observed | Required Action |
| --- | --- | --- | --- |
| selected_profile_present | pass | full_pilot | Restore the selected run profile before experiment review. |
| result_row_count_matches_design | pass | 1890 / 1890 | Regenerate results or revise the scenario-policy-seed design before review closure. |
| summary_row_count_matches_design | pass | 63 / 63 | Regenerate summary outputs or revise the run design before review closure. |
| primary_metrics_pre_specified | needs_human_review_primary_metrics | completion_rate, penalized_makespan, p95_arrival_time, passengers_per_total_service_minute | Confirm, revise, or narrow the proposed primary metric set. |
| primary_policy_contrast_pre_specified | needs_human_review_primary_comparison | bus_only vs baseline_multimodal | Confirm whether this is the reviewer-selected primary contrast or mark all contrasts exploratory. |
| crn_structural_pairing | pass | True | Resolve structural CRN blockers before paired policy claims. |
| replication_statistics_structure | pass | True | Regenerate paired statistics or resolve replication audit blockers. |
| replication_adequacy_human_review | needs_human_review_replication_adequacy | 5 replication audit rows need review | Decide whether seed count, finite paired counts, and CI method are adequate for release-scope claims. |
| multiple_comparison_boundary | needs_human_review_multiple_comparisons | No formal multiple-comparison correction is accepted for the current scaffold outputs. Primary comparisons must be selected before formal experiment acceptance; all other scenario, policy, and metric comparisons are exploratory. | Select a multiplicity procedure or keep secondary comparisons exploratory. |
| formal_experiment_acceptance | blocked_missing_experiment_acceptance_record | data/manifests/experiment_acceptance.json absent unless reviewer supplies it | Create the formal experiment decision record only after graph, input, CRN, counts, and claim-scope review. |

## Use

Use this note with `docs/crn_pairing_audit.md`, `docs/replication_adequacy_audit.md`, and `docs/experiment_package_review_packet.md` before drafting `data/manifests/experiment_acceptance.json`. It is a planning and review artifact only.
