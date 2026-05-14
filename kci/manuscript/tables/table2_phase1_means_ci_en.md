**Table 2.** Phase 1a baseline robustness: means and 95% confidence intervals by `p_fail_scale` (Origin A, R = 30 paired CRN, paired-t df = 29).

| `p_fail_scale` | Δ penalized_makespan (min) [mean, 95% CI] | Δ q90 arrival time (min) [mean, 95% CI] | Δ P(complete ≤ 1500 min) [mean, 95% CI] |
|---|---|---|---|
| 0.00 | −58.5  [−58.5, −58.5] | −58.5  [−58.5, −58.5] | 0.000  [0.000, 0.000] |
| 0.10 | −55.2  [−60.9, −49.6] | −55.2  [−60.9, −49.6] | 0.000  [0.000, 0.000] |
| 0.25 | −53.4  [−60.2, −46.6] | −53.4  [−60.2, −46.6] | 0.000  [0.000, 0.000] |
| 0.50 | −144,123.3  [−308,278.4, +20,031.7] | −124.8  [−212.8, −36.8] | +0.100  [−0.014, +0.214] |
| 0.75 | −192,148.0  [−378,154.5, −6,141.4] | −149.9  [−249.4, −50.3] | +0.133  [+0.004, +0.262] |
| 1.00 | −192,140.2  [−378,147.9, −6,132.6] | −142.2  [−243.0, −41.4] | +0.133  [+0.004, +0.262] |
| 1.50 | −432,259.1  [−683,013.6, −181,504.6] | −263.5  [−401.1, −125.8] | +0.300  [+0.126, +0.474] |
| 2.00 | −624,351.8  [−895,506.7, −353,196.9] | −358.1  [−508.9, −207.3] | +0.433  [+0.245, +0.622] |

*Note.* Δ = bus_only − multimodal (per `_safe_delta(left=bus, right=multi)`; negative ⇒ bus_only has smaller penalized makespan, indicating direct-bus advantage / multimodal disadvantage). Paired common-random-numbers (CRN) sample R = 30; 95% confidence intervals are paired-t (df = 29). `delta_penalized_makespan` is the micro-passenger-weighted makespan difference (minutes) inclusive of the censoring penalty; for `p_fail_scale ≥ 0.5` the penalty term (`deadline_min = 1500`, penalty multiplier ×1500) on multimodal-route censored passengers dominates, which inflates the absolute magnitude sharply. `delta_arrival_q90_min` is the 90th-percentile arrival-time difference. `delta_prob_completion_within_window` is the difference in the probability of completion within 1,500 minutes. At `p_fail_scale = 0.0`, all 30 paired replications converge to identical deterministic output under CRN, so the CI width is zero. Values are rounded to one decimal (makespan, q90) or three decimals (probability).
