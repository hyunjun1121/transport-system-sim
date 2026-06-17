# Sensitivity Index Review Packet

This packet summarizes Morris index handling by metric. It does not create sensitivity acceptance, does not waive Sobol analysis, and does not support calibrated final-study sensitivity claims.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Metrics: 7
- Unavailable index rows: 4832
- Zero `mu_star` rows: 33619
- All-zero metric/policy/scenario groups: 878
- Status counts: `{'needs_human_review_unavailable_indices': 2, 'needs_human_review_zero_mu_star_rows': 5}`

## Rows

| Metric | Unavailable | Zero mu_star | Positive mu_star | All-zero groups | Status | Required action |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| censored_count | 0 | 8349 | 483 | 374 | needs_human_review_zero_mu_star_rows | interpret zero mu_star rows before claiming parameter influence or no effect |
| completion_rate | 0 | 8483 | 349 | 418 | needs_human_review_zero_mu_star_rows | interpret zero mu_star rows before claiming parameter influence or no effect |
| p80_arrival_time | 2416 | 2264 | 4152 | 0 | needs_human_review_unavailable_indices | document unavailable index handling for this metric before using rankings |
| p95_arrival_time | 2416 | 2176 | 4240 | 0 | needs_human_review_unavailable_indices | document unavailable index handling for this metric before using rankings |
| passengers_per_total_service_minute | 0 | 4374 | 4458 | 44 | needs_human_review_zero_mu_star_rows | interpret zero mu_star rows before claiming parameter influence or no effect |
| penalized_makespan | 0 | 3977 | 4855 | 0 | needs_human_review_zero_mu_star_rows | interpret zero mu_star rows before claiming parameter influence or no effect |
| total_service_minutes | 0 | 3996 | 4836 | 42 | needs_human_review_zero_mu_star_rows | interpret zero mu_star rows before claiming parameter influence or no effect |

## Boundary

- This packet is metric-level index-handling review support only.
- It does not accept Morris results, waive Sobol analysis, or prove no-effect parameter findings.
- It cannot create or replace `data/manifests/sensitivity_acceptance.json`.
