# Sensitivity Index Review Packet

This packet summarizes Morris index handling by metric. It does not create sensitivity acceptance, does not waive Sobol analysis, and does not support calibrated final-study sensitivity claims.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Metrics: 7
- Unavailable index rows: 168
- Zero `mu_star` rows: 4272
- All-zero metric/policy/scenario groups: 150
- Status counts: `{'needs_human_review_unavailable_indices': 2, 'needs_human_review_zero_mu_star_rows': 5}`

## Rows

| Metric | Unavailable | Zero mu_star | Positive mu_star | All-zero groups | Status | Required action |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| censored_count | 0 | 1002 | 6 | 66 | needs_human_review_zero_mu_star_rows | interpret zero mu_star rows before claiming parameter influence or no effect |
| completion_rate | 0 | 1008 | 0 | 72 | needs_human_review_zero_mu_star_rows | interpret zero mu_star rows before claiming parameter influence or no effect |
| p80_arrival_time | 84 | 402 | 522 | 0 | needs_human_review_unavailable_indices | document unavailable index handling for this metric before using rankings |
| p95_arrival_time | 84 | 402 | 522 | 0 | needs_human_review_unavailable_indices | document unavailable index handling for this metric before using rankings |
| passengers_per_total_service_minute | 0 | 522 | 486 | 6 | needs_human_review_zero_mu_star_rows | interpret zero mu_star rows before claiming parameter influence or no effect |
| penalized_makespan | 0 | 414 | 594 | 0 | needs_human_review_zero_mu_star_rows | interpret zero mu_star rows before claiming parameter influence or no effect |
| total_service_minutes | 0 | 522 | 486 | 6 | needs_human_review_zero_mu_star_rows | interpret zero mu_star rows before claiming parameter influence or no effect |

## Boundary

- This packet is metric-level index-handling review support only.
- It does not accept Morris results, waive Sobol analysis, or prove no-effect parameter findings.
- It cannot create or replace `data/manifests/sensitivity_acceptance.json`.
