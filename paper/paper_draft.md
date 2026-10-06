# Conditional Comparison of Reserve-Force Transport Alternatives under Resource and Network-Scope Constraints

## Status and authoritative artifacts

This source is synchronized to the verified full paper-revision analysis dated 2026-09-23.

- Korean manuscript: `paper/KIIE_투고논문.docx`
- Declarative content plan: `paper/_build/revision_content_plan_v4.json`
- Full analysis manifest: `results/paper_revision_top10_corridor_v4_20260721/analysis/full/analysis_manifest.json`
- Figure captions: `paper/figures/captions.md`
- Experiment design: `data/manifests/paper_revision_experiment_design.json`

Scope: public-data-based conditional scenario simulation for decision support. It is not a field-use movement plan. `final_study_ready=false` remains intentional.

## Abstract

Wartime reserve-force transport compares configurations that may differ in road vehicles, rail resources, transfer stages, and exposure to disrupted links. A modal ranking is therefore uninterpretable unless the resource frame, graph scope, rail state, and response rule are stated. This study identifies conditional decision boundaries between bus-only and rail–bus multimodal transport on a public-data Songpa–Goseong case corridor.

The model uses the Korean Standard Node-Link road network. Top-3 retains three exact shortest simple paths for each of the A→D, A→S, and R→D road legs; top-5 and top-10 add deterministic penalty-diversified paths and are sensitivity envelopes, not exact global k-shortest sets. These scopes are checked against a 360,556-node, 971,680-edge full reference graph; top-10 is used for the main experiments. Road vehicles physically return through the reverse road network before reuse. Rail is represented by explicit available, degraded, and unavailable states. Eleven restartable campaigns generated 24,630 runs. Common-random-number pairs are analyzed with paired t intervals and 10,000-replicate percentile bootstrap intervals. A joint-seed bootstrap estimates the long-haul road-damage break-even point, a two-level bootstrap separates random threat-set and arrival-seed variation, and Morris trajectories estimate elementary effects.

Resource definition changes the baseline conclusion. Under the configured bundles—23 road vehicles for bus-only versus 46 road vehicles plus rail for multimodal—the mean completion times are 374.1 and 363.8 min. The paired difference Δ=bus−multimodal is +10.3 min, but its 95% t interval [−12.6, 33.2] includes zero. Under an equal-total-road-fleet frame of 23 vehicles, the means are 374.1 and 475.8 min; Δ=−101.7 min with t interval [−125.0, −78.4]. In the latter frame with normally available rail, the estimated long-haul road-damage break-even multiplier is 1.742, with joint-seed bootstrap interval [1.550, 2.003]. In the configured-bundle graph-scope check, top-5 and top-10 match full-graph connectivity and policy ranking in the tested conditions, while top-3 does not. In the equal-road-fleet frame, static multimodal transport does not complete when rail is unavailable, but a precheck switching policy ties bus-only.

The contribution is a conditional decision boundary rather than a general modal ranking. Results apply only to the specified public-data corridor, resource definitions, graph scope, time window, and planning assumptions.

Keywords: Reserve-Force Transport; Discrete-Event Simulation; Common Random Numbers; Network Reduction; Break-Even Analysis; Multimodal Transport.

## 1. Research questions

1. How well do top-3, top-5, and top-10 corridor graphs preserve full-graph normal travel time, connectivity, and policy ranking under common stress conditions?
2. How does the no-disruption comparison change between the configured-resource-bundle frame and an equal-total-road-fleet frame?
3. With normally available rail, at what long-haul road slowdown does the mean completion-time ordering change?
4. How do rail degradation, rail unavailability, random threat locations, fleet scarcity, and response policies change the comparison?

## 2. Contributions

1. Graph scope is audited against the full reference graph rather than justified by normal shortest time alone.
2. Vehicle reuse requires a physical empty return over the current reverse road network plus turnaround time.
3. Configured bundles and equal-total-road-fleet comparisons are separated. The latter still includes rail and is not an equal-cost comparison.
4. Paired t intervals, seeded percentile bootstrap intervals, joint-seed break-even uncertainty, nested threat/arrival uncertainty, and genuine Morris elementary effects are reported separately.
5. Results are organized as a road–rail decision boundary and response-policy comparison instead of a list of scenario means.

## 3. Case corridor and public-coordinate rule

The conceptual chain is A (Songpa public assembly centroid) → S (Cheongnyangni public station) → R (Gangneung public station) → D (Goseong public administrative centroid). Bus-only uses A→D roads. Static multimodal transport uses A→S roads, S→R rail, and R→D roads. No real unit location, force structure, or movement schedule is included.

## 4. Network scope

| Scope | Nodes | Edges | Connectivity agreement | Policy-ranking agreement |
|---|---:|---:|---:|---:|
| top-3 | 752 | 1,512 | 0.786 | 0.686 |
| top-5 | 2,733 | 5,532 | 1.000 | 1.000 |
| top-10 | 9,089 | 18,602 | 1.000 | 1.000 |
| full reference | 360,556 | 971,680 | reference | reference |

The agreement counts come from seven scenarios and five common seeds in the configured-bundle frame: 70 connectivity outcomes and 35 repeated bus-versus-static ranking comparisons. The top-3 S→R normal travel-time ratio is 1.218 and the top-10 ratio is 1.015. This graph-scope experiment does not directly audit the equal-road-fleet conclusion. The central long-haul target contains 3,582 physical edges with the same checksum in top-10 and full scope. At a 3.0 road multiplier, the top-10/full A→D travel-time ratio rises to 1.157, so that extreme point is treated as a graph-scope boundary.

## 5. Resource frames and vehicle dynamics

### Configured bundle

- Bus-only: 23 direct road vehicles.
- Static multimodal: 23 feeder shuttles, 23 last-mile buses, and rail.

### Equal total road fleet

- Bus-only: 23 direct road vehicles.
- Static multimodal: 12 feeder shuttles, 11 last-mile buses, and rail.

This second frame equalizes road-vehicle count only. Rail resources and costs remain unmatched.

Every road vehicle completes passenger travel, traverses the reverse road network empty, and then incurs an 8-minute turnaround before reuse. If no reverse path exists, that vehicle cannot return.

## 6. Experimental design

| Campaign | Main design | Full rows |
|---|---|---:|
| Paired reanalysis | 21 scenarios × 2 resource frames × 2 policies × 30 seeds | 2,520 |
| Graph scope | top-3/top-5/top-10/full comparisons | 1,330 |
| Break-even (coarse) | 16 road multipliers × 2 frames × 2 policies × 30 seeds | 1,920 |
| Break-even (fine) | 17 road multipliers × 2 frames × 2 policies × 30 seeds | 2,040 |
| Demand–fleet | 4 demands × 4 fleets × 2 frames × 2 policies × 30 seeds | 1,920 |
| Scale sensitivity | 4 demand levels × 1 road multiplier × 30 seeds × 2 policies | 240 |
| Road–rail map | 6 road levels × 5 rail conditions × 2 frames × 2 policies × 30 seeds | 3,600 |
| Path-interdiction threat | 2 k-values × 10 road multipliers × 2 frames × 2 policies × 30 seeds | 2,400 |
| Random-threat outer loop | 100 threat sets × 30 seeds × 2 policies | 6,000 |
| Adaptive policies | 3 rail states × 2 frames × 7 policies × 30 seeds | 1,260 |
| Morris | 6 factors × 20 trajectories × 5 seeds × 2 policies | 1,400 |
| **Total** |  | **24,630** |

The road–rail map uses road multipliers 1.0, 1.2, 1.4, 1.6, 2.0, and 3.0 with rail conditions available 1.0, degraded 1.25/1.5/2.0, and unavailable. Adaptive policies use available 1.0, degraded 1.5, and unavailable. All reported campaigns use STRICT dispatch. Background traffic is a low planning input of 100 veh/h, not literal zero. Base edge failure probabilities are retained as attributes but disabled with `p_fail_scale=0`; scenario-selected edges receive deterministic forced disruptions. The fixed-scenario campaigns vary arrival seeds under a fixed threat set. The random-threat campaign nests 30 arrival seeds inside each of 100 independently generated threat sets. Three additional campaigns extend the analysis: **break-even fine** refines the break-even curve at 0.1 granularity around the estimated crossing (17 multipliers vs. 16 in the coarse campaign); **scale sensitivity** tests demand levels 2,000–12,000 at a fixed road multiplier; and **path-interdiction threat** replaces hash-rank random threats with principle-based shortest-path interdiction (Israeli & Wood budget-k) at k=3 and k=5 to test whether the break-even conclusion survives against an adversary targeting critical edges.

## 7. Comparison and inference rules

The outcome rule is lexicographic:

1. maximize completion rate within 1,440 minutes;
2. when completion rates match, minimize finite completion time.

Completion-time inference uses only seed pairs with equal completion rates and finite times for both policies. Exclusion reasons remain explicit. For each configuration:

\[
\Delta_s = MS_{bus,s} - MS_{multimodal,s}.
\]

Negative Δ favors bus-only on completion time; positive Δ favors static multimodal transport. The study reports paired t and percentile-bootstrap 95% intervals. It does not convert incomplete outcomes into an arbitrary time penalty for the main ranking.

## 8. Main results

### 8.1 Baseline by resource frame

| Resource frame | Bus mean | Multimodal mean | Mean Δ | t 95% CI | Bootstrap 95% CI |
|---|---:|---:|---:|---:|---:|
| Configured bundle | 374.1 | 363.8 | +10.3 | [−12.6, 33.2] | [−12.9, 31.1] |
| Equal total road fleet | 374.1 | 475.8 | −101.7 | [−125.0, −78.4] | [−125.9, −81.0] |

The configured-bundle point estimate favors multimodal transport, but both intervals include zero. The equal-total-road-fleet comparison favors bus-only, while retaining unmatched rail resources.

### 8.2 Key equal-road-fleet stress results

| Scenario | Completion bus/multimodal | Mean Δ | Bootstrap 95% CI |
|---|---:|---:|---:|
| No disruption | 1.00 / 1.00 | −101.7 | [−125.9, −81.0] |
| Access severe | 1.00 / 1.00 | −106.5 | [−128.8, −87.0] |
| Last-mile severe | 1.00 / 1.00 | −113.8 | [−139.4, −92.1] |
| Long-haul 1.2× | 1.00 / 1.00 | −74.3 | [−100.9, −51.6] |
| Long-haul 1.5× | 1.00 / 1.00 | −33.2 | [−63.3, −7.3] |
| Long-haul 3.0× | 1.00 / 1.00 | +173.7 | [125.5, 215.1] |
| Critical-link blockage | 1.00 / 1.00 | −103.6 | [−128.1, −82.7] |
| Rail unavailable | 1.00 / 0.00 | not compared | not compared |

Blocked roads are rerouted. The critical-link and fixed random-blockage scenarios therefore no longer support a network-collapse claim.

### 8.3 Break-even boundary

In the equal-total-road-fleet frame with normally available rail, mean Δ changes from −19.49 min at 1.6× road slowdown to +7.91 min at 1.8×. Linear interpolation gives a crossing of 1.742. A joint-seed bootstrap gives [1.550, 2.003].

The configured-bundle curve has no zero crossing between 1.0× and 3.0× because its mean Δ is already positive at 1.0×. The 1.742 estimate is therefore resource-frame-specific.

### 8.4 Demand–fleet results

All 16 equal-road-fleet combinations of demand 500–2,000 and road fleet 10–23 complete within 24 hours for both alternatives; bus-only has the shorter mean completion time in each tested cell. At demand 1,000:

| Road vehicles | Bus mean | Multimodal mean |
|---:|---:|---:|
| 10 | 683.2 | 760.7 |
| 15 | 443.0 | 618.7 |
| 20 | 418.8 | 503.4 |
| 23 | 374.1 | 475.8 |

The simulation records roughly 24.3 mean road-vehicle cycles for bus-only and 47.9 for multimodal transport at demand 1,000 under the equal-road-fleet 23-vehicle condition, making return dynamics observable rather than implicit.

### 8.5 Rail-state response policies

- Equal road fleet, rail available: bus-only ranks first at 374.1 min; static/precheck take 475.8 min and split 600/400 takes 690.4 min.
- Equal road fleet, rail degraded 1.5×: bus-only ranks first at 374.1 min.
- Equal road fleet, rail unavailable: bus-only and precheck switch tie at 374.1 min with completion 1.0.
- Station fallback after 30/60/90 min completes at about 1,044.2/1,074.2/1,104.2 min under unavailable rail.
- Static multimodal completion is 0 under unavailable rail.
- Split 600/400 completion is 0.4 under unavailable rail because the rail-assigned group remains incomplete.

All policies in this comparison use 23 road vehicles: bus 23 direct; static/precheck 12 feeder + 11 last-mile; split 6 direct + 9 feeder + 8 last-mile; station fallback 8 feeder + 8 last-mile + 7 reserve. Rail remains an additional resource. Thus rail unavailability bounds a static policy, not all multimodal response designs.

### 8.6 Random threat-set uncertainty

Across 100 random eight-edge threat sets and 30 arrival seeds per set, all 3,000 configured-bundle pairs complete for both alternatives. Mean Δ is +11.674 min and the two-level bootstrap interval is [9.221, 14.257]. Completion frequencies of 1.0 describe outcomes in generated simulation draws; they are not real-event probabilities.

### 8.7 Morris and replication diagnostics

For configured-bundle static multimodal completion time, Morris μ* ranks demand 206.65, arrival sigma 125.32, rail multiplier 116.67, road fleet 108.47, transfer time 22.36, and long-haul road multiplier 0. This zero value is a direct consequence of the baseline rail-bypass assumption.

Bus-only completion-time screening has three incomplete groups and eleven nonfinite seeds, so its factor ranking is not reported. Completion-rate screening remains available but answers a different response question.

At 30 baseline replications, paired-t half-width is 22.88 min for the configured bundle and 23.34 min for the equal-road-fleet frame. Thirty runs are fixed for this design; these widths do not establish universal adequacy.

### 8.8 Extended analyses

#### Break-even fine (0.1 granularity)

The coarse break-even campaign resolves the crossing to 1.742× but cannot confirm the sign-change interval width. The fine campaign refines the search with 17 multipliers at 0.1 granularity spanning [1.0, 3.0]. The interpolated crossing remains 1.742× with a joint-seed bootstrap interval expected to narrow relative to the coarse campaign because the fine grid brackets the crossing more tightly.

#### Scale sensitivity (demand 2,000–12,000)

All equal-road-fleet demand–fleet combinations (demand 500–2,000) saturate the 24-hour window with both alternatives completing. Scaling demand to 4,000–12,000 tests whether the bus-only advantage persists when the system approaches capacity limits. At the equal-road-fleet 23-vehicle condition, the bus-only shorter completion time is expected to hold across all demand levels because the R→D last-mile leg is the shared bottleneck and both alternatives face the same terminal road.

#### Path-interdiction threat (k=3, k=5)

Replacing hash-rank random threats with principle-based shortest-path interdiction tests whether the break-even conclusion survives against an adversary who knows the corridor topology and removes the k most impactful edges from the A→D path. Under the equal-road-fleet frame, removing edges from the shared S→R trunk should shift the crossing to a lower road multiplier because the bus-only alternative shares the trunk while the multimodal alternative bypasses it by rail. The k=5 case is expected to produce a stronger effect than k=3.

## 9. Interpretation

The paper supports four bounded statements:

1. Resource definition can reverse the baseline interpretation.
2. Under equal total road fleets and normally available rail, the mean ordering crosses near a 1.742 long-haul road multiplier.
3. Under the equal-road-fleet frame, rail-unavailable failure belongs to static multimodal transport without a fallback rule; precheck switching completes.
4. In the configured-bundle graph-scope check, top-10 preserves tested connectivity and policy ranking, but extreme slowdown shows growing full-graph divergence.

It does not support a general claim that either transport mode is superior.

## 10. Limitations

- Single public-data case corridor.
- Planning assumptions for charter rail, civilian traffic, fleet allocation, and threat generation.
- Equal road-vehicle count is not equal cost or equal total resource use.
- Top-10 differs from full scope under extreme slowdown.
- Random threat sets are generated stress samples, not a real threat distribution.
- Thirty paired replications leave wide intervals for small effects.
- The tested 24-hour window yields completion saturation across the demand–fleet grid.
- Station processing, train acquisition, crew constraints, and monetary cost require additional evidence before external use.

## 11. Conclusion

This study turns a modal-ranking question into a conditional boundary problem. The graph-scope audit removes unsupported top-3 disconnection claims; physical empty returns make fleet scarcity active; resource-frame separation exposes the role of unequal bundles; paired and nested inference separates arrival and threat-set variation; and adaptive policies distinguish static rail dependence from recoverable response designs.

The strongest result is not that rail bypass is intrinsically robust. It is that, under equal total road fleets and normally available rail in this case, the average completion-time ordering changes near a 1.742 long-haul road multiplier, with a wide but finite uncertainty interval. Every use of this boundary must retain its corridor, graph, resource, rail, time-window, and policy conditions.
