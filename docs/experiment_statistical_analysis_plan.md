# Experiment Statistical Analysis Plan

This statistical-analysis plan and scenario-policy-seed note is a pre-review planning artifact. It does not approve experiment acceptance, prove replication adequacy, validate common-random-number design, certify a multiple-comparison procedure, or close final-study gates.

## Verdict

- Selected profile: `full_pilot`
- Statistical plan ready for review: `false`
- Acceptance ready: `false`
- Can mark complete: `false`
- Blocking checks: 1
- Human-review checks: 4

## Expert Reply Alignment

The expert reply confirmed that no model- or experiment-level claim can move from
scaffold to accepted status until package and formal-artifact hygiene is in place.
This plan remains a non-acceptance control artifact and must be kept aligned with
`docs/archive/2026-05-11/expert_review_cycle_archive_20260511.md`.

- The reviewed `required_deliverables.zip` now includes implementation, results,
  tests, and docs, so statistical claims can be checked against execution code.
- Formal acceptance remains blocked until:
  - `scripts/audit_formal_acceptance_artifacts.py` passes,
  - `scripts/audit_formal_evidence_paths.py` passes, and
  - `scripts/validate_formal_acceptance_package.py --fail-on-blockers` passes.

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

Secondary comparison boundary: All other policy, scenario, and metric contrasts remain exploratory until a reviewer accepts a primary/secondary comparison family and any required multiplicity adjustment.

CI method: `normal_approximation_mean_plus_minus_1_96_standard_errors`
Multiplicity note: No formal multiple-comparison correction is accepted for the current scaffold outputs. Primary comparisons must be selected before formal experiment acceptance; all other scenario, policy, and metric comparisons are exploratory.

## Checks

| Check | Status | Observed | Required Action |
| --- | --- | --- | --- |
| selected_profile_present | pass | full_pilot | Restore the selected run profile before experiment review. |
| result_row_count_matches_design | pass | 1890 / 1890 | Regenerate results or revise the scenario-policy-seed design before acceptance. |
| summary_row_count_matches_design | pass | 63 / 63 | Regenerate summary outputs or revise the run design before acceptance. |
| primary_metrics_pre_specified | needs_human_review_primary_metrics | completion_rate, penalized_makespan, p95_arrival_time, passengers_per_total_service_minute | Confirm, revise, or narrow the proposed primary metric set. If unchanged, add reviewer-ratified exploratory status for all non-primary metrics. |
| primary_policy_contrast_pre_specified | needs_human_review_primary_comparison | bus_only vs baseline_multimodal | Confirm whether this is the accepted primary contrast or mark all contrasts exploratory. |
| crn_structural_pairing | pass | True | Resolve structural CRN blockers before paired policy claims. |
| replication_statistics_structure | pass | True | Regenerate paired statistics or resolve replication audit blockers. |
| replication_adequacy_human_review | needs_human_review_replication_adequacy | 5 replication audit rows need review | Decide whether seed count, finite paired counts, and CI method are adequate for final claims. |
| multiple_comparison_boundary | needs_human_review_multiple_comparisons | No formal multiple-comparison correction is accepted for the current scaffold outputs. Primary comparisons must be selected before formal experiment acceptance; all other scenario, policy, and metric comparisons are exploratory. | Accept a multiplicity procedure (recommended Holm/FDR family) or explicitly designate all non-primary outcomes as exploratory with scope limits. |
| formal_experiment_acceptance | blocked_missing_experiment_acceptance_record | data/manifests/experiment_acceptance.json absent unless reviewer supplies it | Create the formal experiment acceptance record only after graph, input, CRN, counts, and claim-scope review. |

## Use

Use this note with `docs/crn_pairing_audit.md`, `docs/replication_adequacy_audit.md`, and `docs/experiment_package_review_packet.md` before drafting `data/manifests/experiment_acceptance.json`. It is a planning and review artifact only.

## Command Ladder (Reply-Triggered)

When this plan is updated or design inputs change, rerun at least:

- `.\.venv\Scripts\python scripts/write_seed_stream_manifest.py`
- `.\.venv\Scripts\python scripts/audit_crn_pairing.py`
- `.\.venv\Scripts\python scripts/audit_replication_adequacy.py`
- `.\.venv\Scripts\python scripts/write_experiment_statistical_plan.py`
- `.\.venv\Scripts\python scripts/write_experiment_package_review_packet.py`
- `.\.venv\Scripts\python scripts/make_pilot_statistics.py`
- `.\.venv\Scripts\python scripts/audit_formal_evidence_paths.py`
- `.\.venv\Scripts\python scripts\validate_formal_acceptance_package.py --fail-on-blockers`
