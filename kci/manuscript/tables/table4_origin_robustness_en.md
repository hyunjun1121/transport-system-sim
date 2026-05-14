**Table 4.** Origin robustness: mean Δ penalized_makespan and 95% paired-t confidence intervals by origin × `p_fail_scale`.

| Origin | `p_fail_scale` | R | Δ penalized_makespan (min) [mean, 95% CI] |
|---|---|---|---|
| A (Songpa-gu Job Center) | 0.0 | 30 | −58.5  [−58.5, −58.5] |
| A | 0.5 | 30 | −144,123.3  [−308,278.4, +20,031.7] |
| A | 1.0 | 30 | −192,140.2  [−378,147.9, −6,132.6] |
| A | 1.5 | 30 | −432,259.1  [−683,013.6, −181,504.6] |
| B | 0.0 | 20 | −57.2  [−57.2, −57.2] |
| B | 0.5 | 20 | −72,089.9  [−222,866.0, +78,686.2] |
| B | 1.0 | 20 | −504,310.9  [−834,283.1, −174,338.8] |
| B | 1.5 | 20 | −720,413.1  [−1,066,321.8, −374,504.3] |
| C | 0.0 | 20 | −60.9  [−60.9, −60.9] |
| C | 0.5 | 20 | −72,086.4  [−222,862.7, +78,689.9] |
| C | 1.0 | 20 | −360,228.3  [−659,792.2, −60,664.5] |
| C | 1.5 | 20 | −504,290.7  [−834,268.4, −174,312.9] |
| D† | 0.0 | 20 | −66.7  [−66.7, −66.7] |
| D† | 0.5 | 20 | −144,130.8  [−351,673.1, +63,411.5] |
| D† | 1.0 | 20 | −504,312.1  [−834,284.9, −174,339.3] |
| D† | 1.5 | 20 | −720,410.1  [−1,066,321.8, −374,498.3] |

*Note.* Δ = bus_only − multimodal (per `_safe_delta(left=bus, right=multi)`; negative ⇒ bus_only has smaller penalized makespan, indicating direct-bus advantage / multimodal disadvantage). Origin A is drawn from Phase 1a (R = 30, 8 `p_fail_scale` levels) and subsetted to the four focal levels shown; Origins B and C are verified origin variants from Phase 1b (R = 20). Confidence intervals are paired-t (df = R − 1) at 95%. At `p_fail_scale = 0.0` all replications converge to identical deterministic output under CRN, so the CI width is zero. **† Origin D is an unverified variant; per the constraint in `plan.md` §4.2, Origin D results are cited for comparison only and are not foregrounded in robustness conclusions.** Values are rounded to one decimal place.
