# Deterministic Rerun Audit

This deterministic rerun audit checks whether a bounded pilot profile produces identical rows across two local executions with the same inputs. It does not approve CRN design, prove replication adequacy, certify full experiment reproducibility, or close final-study gates.

## Verdict

- Deterministic rerun structural checks passed: `true`
- Row hashes match: `true`
- Summary hashes match: `true`
- Acceptance ready: `false`
- Can mark complete: `false`
- Blocking checks: 1
- Deterministic blocking checks: 0
- Human-review checks: 1

## Profile

- Profile: `sample_scaffold`
- Run stage: `sample`
- Sample scaffold: `true`
- Policies: 4
- Scenarios: 4
- Seeds: 2
- Result rows per run: 32
- Summary rows per run: 16

## Hashes

- First rows SHA256: `88b8533c94c090b02c4a7bcf9c6a4c167d39ac200cdb513eb4d5c2e29505949d`
- Second rows SHA256: `88b8533c94c090b02c4a7bcf9c6a4c167d39ac200cdb513eb4d5c2e29505949d`
- First summary SHA256: `eb7768d4247ae01084f104b6c4a0476d485b29fd871f09af942b3ea4fc6c1275`
- Second summary SHA256: `eb7768d4247ae01084f104b6c4a0476d485b29fd871f09af942b3ea4fc6c1275`

## Checks

| Check | Status | Observed | Required Action |
| --- | --- | --- | --- |
| first_rerun_completed | pass | 32 | Debug pilot runner errors before determinism review. |
| second_rerun_completed | pass | 32 | Debug pilot runner errors before determinism review. |
| row_count_matches_profile_design | pass | 32 / 32 | Resolve run-design row-count mismatch before interpreting rerun comparison. |
| rerun_row_hash_match | pass | 88b8533c94c090b02c4a7bcf9c6a4c167d39ac200cdb513eb4d5c2e29505949d / 88b8533c94c090b02c4a7bcf9c6a4c167d39ac200cdb513eb4d5c2e29505949d | Investigate nondeterministic row generation before paired claims. |
| rerun_summary_hash_match | pass | eb7768d4247ae01084f104b6c4a0476d485b29fd871f09af942b3ea4fc6c1275 / eb7768d4247ae01084f104b6c4a0476d485b29fd871f09af942b3ea4fc6c1275 | Investigate nondeterministic summary generation before reporting statistics. |
| rerun_profile_scope | needs_human_review_profile_scope | sample_scaffold | Decide whether the accepted full profile also needs a deterministic rerun check after graph and input gates close. |
| formal_experiment_acceptance | blocked_missing_experiment_acceptance_record | data/manifests/experiment_acceptance.json absent unless reviewer supplies it | Do not treat deterministic rerun success as formal experiment acceptance. |

## Use

Use this audit with the seed-stream manifest, CRN pairing audit, replication adequacy audit, and experiment statistical-analysis plan before drafting `data/manifests/experiment_acceptance.json`.
