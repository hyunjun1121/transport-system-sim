# Replication Adequacy Audit

This audit checks internal consistency of seed-replication and paired-delta statistics. It does not prove that the replication count is sufficient for final claims, approve a multiple-comparison procedure, validate stochastic assumptions, or close experiment acceptance.

## Verdict

- Paired statistics structurally ready: `true`
- Acceptance ready: `false`
- Can mark complete: `false`
- Blocking checks: 0
- Human-review checks: 5

## Checks

| Check | Status | Observed | Expected | Review Action |
| --- | --- | --- | --- | --- |
| statistics_manifest_present | pass | results/realworld_pilot/tables/pilot_full_statistics_manifest.json | pilot statistics manifest exists | Regenerate pilot statistics before experiment review. |
| metric_ci_table_present | pass | results/realworld_pilot/tables/pilot_full_metric_ci.csv | metric confidence-interval CSV exists | Regenerate metric CI table before experiment review. |
| paired_delta_table_present | pass | results/realworld_pilot/tables/pilot_full_paired_delta_ci.csv | paired-delta confidence-interval CSV exists | Regenerate paired-delta table before paired policy claims. |
| metric_ci_row_count_matches_manifest | pass | 819 | 819 | Resolve metric CI row-count mismatch. |
| paired_delta_row_count_matches_manifest | pass | 702 | 702 | Resolve paired-delta row-count mismatch. |
| paired_counts_match_seed_count | needs_human_review | min=0; max=30; rows=702 | paired_count values should not exceed seed_count 30; lower finite counts need review | Review zero or partial finite paired counts before interpreting affected metrics. |
| metric_counts_match_seed_count | needs_human_review | min=0; max=30; rows=819 | sample_count values should not exceed seed_count 30; lower finite counts need review | Review zero or partial finite metric counts before interpreting affected metrics. |
| baseline_policy_declared | pass | bus_only | bus_only | Confirm the formal experiment acceptance record names the baseline policy. |
| replication_count_human_review | needs_human_review | 30 | minimum structural seed count 30; adequacy still reviewer-decided | Decide whether this replication count is sufficient for each primary metric, especially tail-risk metrics. |
| ci_method_human_review | needs_human_review | normal_approximation_mean_plus_minus_1_96_standard_errors | CI method declared and reviewed for sample size and metric distribution | Review whether normal-approximation CIs are acceptable or replace with a selected method. |
| multiple_comparison_procedure | needs_human_review | No formal multiple-comparison correction is accepted for the current scaffold outputs. Primary comparisons must be selected before formal experiment acceptance; all other scenario, policy, and metric comparisons are exploratory. | primary/secondary comparison procedure or exploratory boundary declared | Document the multiple-comparison procedure or explicitly label secondary comparisons as exploratory before final claims. |

## Use

Use this audit with the seed-stream manifest, CRN pairing audit, and experiment package review before accepting paired policy statistics. A structurally complete table is not evidence that replication count, CI method, or comparison handling is adequate.
