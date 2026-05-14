**Table 6.** Counterfactual lever cells where multimodal is favored — or, where none exist, cells nearest sign reversal.

*Note.* This table lists the counterfactual lever conditions under which multimodal becomes statistically superior to single-mode (or, failing that, the cells nearest to sign reversal). An empty subset means no cell decisively favors multimodal.

Total cells: **81** | bus_dominant: **54** | inconclusive: **27** | multi_dominant: **0**

*Remark.* Because no multi_dominant cells were observed, the five cells closest to sign reversal (minimum |mean Δ| / CI half-width) are listed instead.

| rail_headway_min | lastmile_fleet_size | rail_capacity | p_fail_scale | Mean Δ penalized_makespan (min) [95% CI] | Mean Δ q90 (min) [95% CI] | Mean Δ P(complete) [95% CI] | Classification |
|---|---|---|---|---|---|---|---|
| 3 | 23 | 500 | 1.5 | −192,127.9  [−472,873.2, 88,617.4] | −129.8  [−284.9, 25.2] | 0.133  [−0.062, 0.328] | inconclusive |
| 3 | 23 | 1000 | 1.5 | −192,127.9  [−472,873.2, 88,617.4] | −129.8  [−284.9, 25.2] | 0.133  [−0.062, 0.328] | inconclusive |
| 3 | 50 | 500 | 1.5 | −192,127.9  [−472,873.2, 88,617.4] | −129.8  [−284.9, 25.2] | 0.133  [−0.062, 0.328] | inconclusive |
| 3 | 23 | 2000 | 1.5 | −192,127.9  [−472,873.2, 88,617.4] | −129.8  [−284.9, 25.2] | 0.133  [−0.062, 0.328] | inconclusive |
| 3 | 50 | 1000 | 1.5 | −192,127.9  [−472,873.2, 88,617.4] | −129.8  [−284.9, 25.2] | 0.133  [−0.062, 0.328] | inconclusive |

*Interpretation.* Δ = bus_only − multimodal (negative ⇒ direct-bus advantage / multimodal disadvantage; positive ⇒ multimodal advantage). Classification is by 95% paired-t CI on penalized_makespan (df = R − 1 = 14): `bus_dominant` (CI upper < 0), `multi_dominant` (CI lower > 0), `inconclusive` (CI contains 0).
