# Plan Completion Audit

Audit date: 2026-05-08

This is a static plan-gate snapshot retained for review history. For the
current regenerated active-goal completion audit, use
`docs/current_goal_completion_audit.md` and
`data/manifests/current_goal_completion_audit.json`.

Scope: compare the current repository artifacts against `plan.md` for the
final real-world or quasi-real transport-resilience study goal.

Independent review: a read-only GPT-5.5 xhigh audit on 2026-05-03 reached the
same verdict: the repository is an executable quasi-real scaffold with
generated evidence artifacts, not a completed final real-world or quasi-real
study.

## Verdict

The project has reached an executable quasi-real scaffold state, not the final
calibrated real-world study state.

Current plan-gate status is `final_study_ready: false`: 3 / 15 gates are ready
(`real_input_smoke`, `structured_disruptions`, and `policy_alternatives`) and
12 / 15 gates remain blocked. Formal acceptance is not ready: 0 / 12 formal
gates are ready, the current formal guard reports 0 target files present and
12 missing after placeholder copies were moved to draft storage, and no final
approval has been recorded.

The current implementation now supports a cached OSM-derived pilot road graph,
bus-practical road filtering, region specs, connector creation, structured
disruptions, policy alternatives, sample/staged/full pilot experiment profiles,
Morris sensitivity outputs, scaffold figures/tables, conservative paper/report
language, a reproducibility manifest, and aggregated publication-readiness
auditing. It also includes a plan-level final-study readiness audit that maps
every `plan.md` final gate to concrete artifacts and keeps scaffold artifact
presence separate from final-study completion.

The project should still not be described as a calibrated real-world result or
operational route plan. The remaining blockers are evidence and acceptance
gates: reviewed pilot input acceptance, stronger rail/timetable evidence,
parameter calibration or source strengthening, publication-level route
validation, and final manuscript/report acceptance against those inputs.

## 2026-05-10 Consultation Addendum

The expert consultation reply in
`docs/expert_consultation_request_reply.md` has been incorporated as a
follow-up planning constraint, not as acceptance evidence. The reply reports
that the submitted `required_deliverables.zip` exposed acceptance/audit
artifacts but did not include enough implementation, data, script, result,
test, and documentation material to verify model mechanics or experiment
execution. The active remediation plan is now recorded in
`docs/expert_consultation_followup_plan.md`.

This addendum does not change the gate verdict above. It sharpens the
remaining work:

- package completeness and path integrity must be proven before the next
  external review;
- acceptance-looking files must be absent from formal target paths unless they
  are real reviewed decisions; blocker-state placeholder copies now live in
  draft storage rather than final target paths;
- draft road overrides, weak parameter rows, rail assumptions, validation
plausibility checks, Morris outputs, current-worktree smoke evidence, and
manuscript/report text remain scaffold evidence until reviewed;
- graph-scale method, CRN pairing, paired statistical reporting,
multiple-comparison handling, and clean-checkout artifact regeneration are
now explicit acceptance blockers;
- claim language must remain decision-support-only until all evidence gates and
formal acceptance records pass.

Reply implementation updates to this static audit are limited to review control and
do not alter gate facts above:

- `required_deliverables.zip` was rebuilt from `write_review_package_inventory.py`
  output and now includes implementation, tests, data, cache, result, docs, and
  planning artifacts.
- `review_packages/original_required_deliverables_incomplete_20260510.zip` is
  retained for provenance only and is not used for acceptance.
- Formal acceptance target paths remain empty unless a human-signed acceptance
  artifact exists; the new rule set is now enforced in `plan.md` and
  `status.md`.

Reply control impact on static gate tracking:

- Any future static gate snapshot must continue to show: 3/15 ready, 12/15 blocked,
  `final_study_ready=false`, 0/12 formal targets present.
- The active `final_study_ready: false` condition is non-negotiable until each
  reviewer-controlled blocker queue row is accepted in its formal target path.
- Track non-functional acceptance blockers (path-integrity and naming-risk prevention)
  separately from evidence blockers in `docs/current_goal_completion_audit.md`.

## Gate Status

| Gate | Status | Evidence | Remaining Work |
| --- | --- | --- | --- |
| Pilot region accepted | Scaffold complete | `data/regions/pilot_region.yaml`, `docs/pilot_region_data_card.md`, `docs/pilot_acceptance_schema.md`, `src/realworld/pilot_acceptance.py` | Human acceptance of the non-sensitive pilot case and corridor abstraction through `data/manifests/pilot_acceptance.json`. |
| Cached OSM input | Scaffold complete | `data/cache/pilot_region_road.graphml`, cache manifest records Overpass/OSM provenance, `data/parameters/road_class_overrides_draft.csv` has 10 draft review rows, `data/parameters/road_speed_evidence_candidates.csv` has 10 routeable road-class speed-candidate rows with 5 classes containing observed OSM `maxspeed` tags, `data/parameters/road_capacity_evidence_candidates.csv` has 10 routeable road-class capacity-candidate rows with 0 parseable OSM `lanes` observations, `data/parameters/road_evidence_review_packet.csv` consolidates 10 weak road-class evidence rows, `data/parameters/road_evidence_review_manifest.json` summarizes non-acceptance status, `data/road/road_evidence_source_request_packet.csv` names 5 source-request rows for road evidence collection, `scripts/audit_road_evidence.py`, `scripts/audit_road_evidence_diagnostics.py`, `scripts/write_road_speed_evidence.py`, `scripts/write_road_capacity_evidence.py`, `scripts/write_road_evidence_review_packet.py`, `scripts/write_road_evidence_source_request_packet.py`, `scripts/write_road_class_override_template.py`, `scripts/audit_road_overrides.py`, `src/realworld/road_speed_evidence.py`, `src/realworld/road_capacity_evidence.py`, `src/realworld/road_evidence_review_packet.py`, `src/realworld/road_evidence_request_packet.py`, `src/realworld/road_overrides.py`, `src/realworld/road_override_template.py`, `src/realworld/road_override_audit.py`, `docs/road_evidence_review_packet.md`, and `docs/road_evidence_source_request_packet.md` | Source review, publication attribution review, replacement of the draft worksheet and speed/capacity-candidate/review-packet rows with reviewed speed/capacity/disruption evidence, and accepted manifest proof that overrides were applied if final claims require calibrated road inputs. |
| Real input smoke | Complete | `scripts/run_pilot_smoke.py` returns both bus-only and multimodal completion on the cached graph | None for scaffold; rerun after any cache refresh. |
| Graph-scale strategy | Scaffold documented | manifests record 4,608/9,148 filtered source graph, 118/174 canonical analysis graph, and separated 164/246 multi-corridor candidate manifests; `docs/analysis_corridor_method_note.md`, `docs/graph_scale_diagnostics.md`, `docs/graph_scale_review_packet.md`, `docs/graph_scale_result_comparison.md`, and `docs/graph_scale_strategy_readiness_packet.md` record the current method boundary; `data/validation/graph_scale_route_comparison.csv`, `data/validation/graph_scale_route_comparison_summary.md`, `data/validation/graph_scale_alternate_routes.csv`, `data/validation/graph_scale_alternate_routes_summary.md`, `data/validation/graph_scale_multi_corridor_routes.csv`, `data/validation/graph_scale_multi_corridor_routes_summary.md`, `data/validation/graph_scale_review_packet.csv`, `data/validation/graph_scale_review_manifest.json`, `data/validation/full_graph_smoke_manifest.json`, `data/validation/full_graph_runtime_readiness_packet.csv`, `data/validation/full_graph_runtime_readiness_manifest.json`, `data/validation/graph_scale_result_comparison.csv`, `data/validation/graph_scale_result_comparison_manifest.json`, `data/validation/graph_scale_strategy_readiness_packet.csv`, `data/validation/graph_scale_strategy_readiness_manifest.json`, `results/realworld_pilot/pilot_multi_corridor_manifest.json`, `results/realworld_pilot/pilot_multi_corridor_full_manifest.json`, `src/realworld/graph_scale_diagnostics.py`, `src/realworld/graph_scale_review.py`, `src/realworld/full_graph_runtime_readiness_packet.py`, `src/realworld/graph_scale_result_comparison.py`, `src/realworld/graph_scale_strategy_readiness_packet.py`, `scripts/run_graph_scale_diagnostics.py`, `scripts/run_full_graph_smoke.py`, `scripts/write_full_graph_runtime_readiness_packet.py`, `scripts/write_graph_scale_review_packet.py`, `scripts/write_graph_scale_result_comparison.py`, and `scripts/write_graph_scale_strategy_readiness_packet.py` provide 3-row baseline route-parity evidence, 9-row alternate-route sensitivity evidence, a 9-row multi-corridor candidate diagnostic, a 2-row full-graph smoke manifest, a 4-row full-graph runtime-readiness packet, a 4-option method review packet, a 5-row strategy-readiness packet, a 32-row smoke-scale candidate output, a 1,890-row full-profile candidate output, and an 819-row current-vs-candidate result comparison; `docs/graph_scale_acceptance_schema.md` and `src/realworld/graph_scale_acceptance.py` define the explicit acceptance record | Current decision is scaffold/performance abstraction; final study must choose corridor abstraction, full-graph runtime, or multi-corridor ensemble, resolve or formally accept the 3 blocking and 2 human-review items in the strategy-readiness packet plus the full-graph runtime-readiness blockers, decide whether to accept current warnings or adopt the 164-node / 246-edge candidate graph, and record the decision in `data/manifests/graph_scale_acceptance.json`. |
| Data provenance | Review packet complete for scaffold | `data/manifests/reproducibility_manifest.json`, `data/manifests/source_provenance_manifest.json`, data card, reproducibility docs, `docs/source_provenance_manifest.md`, `docs/provenance_acceptance_schema.md`, `scripts/audit_source_provenance.py`, and `src/realworld/provenance_acceptance.py` | Add `data/manifests/provenance_acceptance.json` only after source snapshots, license/attribution, privacy abstraction, cache manifests, reproduction paths, and not-operational claim boundaries are reviewed. |
| Parameter evidence | Scaffold complete | `data/parameters/parameter_sources.csv`, `data/parameters/parameter_evidence_review_packet.csv`, `data/parameters/parameter_evidence_review_manifest.json`, `data/parameters/parameter_evidence_source_request_packet.csv`, `data/parameters/parameter_evidence_source_request_manifest.json`, validators, tests, `docs/parameter_acceptance_schema.md`, `docs/parameter_evidence_review_packet.md`, `docs/parameter_evidence_source_request_packet.md`, `src/realworld/parameter_acceptance.py`, `src/realworld/parameter_review_packet.py`, `src/realworld/parameter_evidence_request_packet.py`, `scripts/audit_parameter_evidence.py`, `scripts/write_parameter_review_packet.py`, and `scripts/write_parameter_evidence_source_request_packet.py` | Current audit has 0 missing core parameters but 25 weak core parameters; the 29-row review packet prioritizes replacement or explicit acceptance, and the 7-row source-request packet names cross-cutting demand, fleet, dispatch, transfer, rail, disruption, and traffic/BPR source inputs. No weak-parameter acceptance CSV is committed yet. |
| Rail evidence | Scaffold complete | `data/rail/pilot_station_binding_cache.csv`, `data/parameters/rail_assumptions.csv`, `data/parameters/rail_service_evidence.csv`, `data/parameters/rail_station_bindings.csv`, `data/parameters/rail_evidence_review_packet.csv`, `data/parameters/rail_evidence_review_manifest.json`, `data/rail/rail_timing_source_request_packet.csv`, `data/rail/rail_timing_source_request_manifest.json`, `docs/rail_evidence.md`, `docs/rail_evidence_review_packet.md`, `docs/rail_timing_source_request_packet.md`, `docs/rail_station_cache_schema.md`, `docs/rail_timetable_cache_schema.md`, `docs/rail_gtfs_cache_schema.md`, `docs/rail_shortest_path_cache_schema.md`, `scripts/audit_rail_evidence.py`, `scripts/write_rail_evidence_review_packet.py`, `scripts/write_rail_timing_source_request_packet.py`, `scripts/audit_rail_station_bindings.py`, `scripts/derive_rail_station_bindings.py`, `scripts/fetch_rail_timetable_cache.py`, `scripts/derive_rail_headway_evidence.py`, `scripts/derive_rail_service_evidence.py`, `scripts/derive_rail_gtfs_evidence.py`, `scripts/fetch_rail_shortest_path_cache.py`, `scripts/derive_rail_shortest_path_evidence.py`, `src/realworld/rail_evidence_review_packet.py`, and `src/realworld/rail_timing_request_packet.py` | Official line-specific station-code bindings are now cached for `S` and `R`; the 10-row rail evidence review packet makes timing, capacity, service-window, availability, and derivation-path gaps explicit; the 5-row rail timing source-request packet names the API-key or reviewed-file inputs and commands needed next; optional train-schedule, static-GTFS, and shortest-path derivation paths exist, but current rail service values are still an assumption proxy, capacity is explicitly sensitivity-only, and no reviewed cached timetable, GTFS, or shortest-path timing evidence is committed yet. |
| Validation package | Scaffold complete | offline plausibility CSVs, optional OSRM snapshot and manifest, accessibility-loss diagnostic CSV, route-level road-evidence exposure CSV/manifest, validation tests, `data/validation/validation_review_packet.csv`, `data/validation/validation_review_manifest.json`, `data/validation/validation_strategy_readiness_packet.csv`, `data/validation/validation_strategy_readiness_manifest.json`, `scripts/write_osrm_snapshot_manifest.py`, `scripts/write_route_road_evidence_exposure.py`, `scripts/write_validation_review_packet.py`, `scripts/write_validation_strategy_readiness_packet.py`, `docs/osrm_route_benchmark_manifest.md`, `docs/route_road_evidence_exposure.md`, `docs/validation_review_packet.md`, `docs/validation_strategy_readiness_packet.md`, `docs/validation_acceptance_schema.md`, `src/realworld/validation_strategy_readiness_packet.py`, and `src/realworld/validation_acceptance.py` | Use the 7-row validation review packet and 7-row strategy-readiness packet to review internal plausibility warnings, fallback benchmark warnings, optional OSRM snapshot/manifest scope, accessibility-loss coverage, route-level road-evidence exposure, validation summary scope, and the benchmark-strategy decision; resolve or formally accept the 3 blocking and 4 human-review items before adding `data/manifests/validation_acceptance.json` and revising `validation_summary.md` out of scaffold/sanity scope. |
| Structured disruptions | Complete for scaffold | random, critical-link, access/last-mile, and spatial scenario rows exist | Tie spatial hazards to stronger public hazard data if required by target journal. |
| Policy alternatives | Complete for scaffold | 8 policy rows and policy knob tests | Interpret as planning alternatives, not recommended operations. |
| Sensitivity analysis | Complete for scaffold | `morris_results.csv`, `morris_summary.csv`, `morris_manifest.json`, `scripts/audit_sensitivity_diagnostics.py`, `data/validation/sensitivity_review_packet.csv`, `data/validation/sensitivity_review_manifest.json`, `scripts/write_sensitivity_review_packet.py`, `docs/sensitivity_diagnostics.md`, `docs/sensitivity_review_packet.md`, `docs/sensitivity_acceptance_schema.md`, and `src/realworld/sensitivity_acceptance.py` | Use the 6-row sensitivity review packet to review explicitly unavailable Morris indices, any unexplained blank/non-finite indices, zero-effect rows, reduced-graph scope, scaffold claim boundaries, and the Morris-vs-Sobol method decision; then record the decision in `data/manifests/sensitivity_acceptance.json`. |
| Full experiment output | Complete for scaffold | 1,890 full pilot rows, 63 full summary rows, 30 seeds, `docs/experiment_acceptance_schema.md`, and `src/realworld/experiment_acceptance.py` | Accept graph scope, input validation, scenario-policy-seed design, CRN pairing, counts, and claim boundary in `data/manifests/experiment_acceptance.json` before manuscript claims. |
| Manuscript/report alignment | Scaffold aligned | `paper/paper_draft.md`, `report_draft.md`, regenerated `report.docx`, `docs/manuscript_acceptance_schema.md`, and `src/realworld/manuscript_acceptance.py`; paper/report text now reflects the current OSM-derived scaffold, reduced analysis corridor, Morris output scale, and non-calibrated claim boundary | Add `data/manifests/manuscript_acceptance.json` only after paper/report text, regenerated docx, figures/tables, evidence gates, result claims, and not-operational claim boundaries are reviewed. |
| Reproducibility | Scaffold complete | manifest commands, full tests pass, figure/table artifacts exist, `docs/reproducibility_acceptance_schema.md`, and `src/realworld/reproducibility_acceptance.py` | Add `data/manifests/reproducibility_acceptance.json` only after clean-checkout validation, validation ladder, artifact regeneration, manifest paths, runtime import boundaries, command count, and not-operational claim boundaries are reviewed. |
| Publication readiness | Scaffold complete | `scripts/audit_publication_readiness.py` aggregates parameter, road, rail-service, and station-binding gates | Current verdict is blocked; run with `--fail-on-blockers` only for strict final audits after evidence gates close. |
| Final audit | Partial | this audit note; `scripts/audit_final_study_readiness.py`, `docs/final_audit_acceptance_schema.md`, and `src/realworld/final_audit_acceptance.py` report plan-level blocked gates | Add `data/manifests/final_audit_acceptance.json` only after an independent prompt-to-artifact audit verifies every pre-final gate, rejects proxy-only completion evidence, and confirms no blocked gates remain. |

## Validation Run

Commands run successfully in the current workspace:

```powershell
.\.venv\Scripts\python -m compileall main.py src tests scripts generate_report.py
Get-ChildItem tests\test_*.py | ForEach-Object { .\.venv\Scripts\python $_.FullName }
.\.venv\Scripts\python scripts\run_pilot_smoke.py
.\.venv\Scripts\python scripts\run_full_graph_smoke.py
.\.venv\Scripts\python scripts\run_graph_scale_diagnostics.py
.\.venv\Scripts\python scripts\write_full_graph_runtime_readiness_packet.py
.\.venv\Scripts\python scripts\write_graph_scale_review_packet.py
.\.venv\Scripts\python scripts\write_graph_scale_result_comparison.py
.\.venv\Scripts\python scripts\audit_rail_evidence.py
.\.venv\Scripts\python scripts\write_rail_evidence_review_packet.py
.\.venv\Scripts\python scripts\write_rail_timing_source_request_packet.py
.\.venv\Scripts\python scripts\audit_parameter_evidence.py
.\.venv\Scripts\python scripts\write_parameter_review_packet.py
.\.venv\Scripts\python scripts\write_parameter_evidence_source_request_packet.py
.\.venv\Scripts\python scripts\audit_road_evidence.py
.\.venv\Scripts\python scripts\audit_road_evidence_diagnostics.py
.\.venv\Scripts\python scripts\write_road_capacity_evidence.py
.\.venv\Scripts\python scripts\write_road_speed_evidence.py
.\.venv\Scripts\python scripts\write_road_evidence_review_packet.py
.\.venv\Scripts\python scripts\write_road_evidence_source_request_packet.py
.\.venv\Scripts\python scripts\audit_road_overrides.py
.\.venv\Scripts\python scripts\audit_rail_station_bindings.py
.\.venv\Scripts\python tests\test_realworld_road_evidence_diagnostics.py
.\.venv\Scripts\python tests\test_realworld_rail_shortest_path.py
.\.venv\Scripts\python tests\test_realworld_rail_shortest_path_api.py
.\.venv\Scripts\python tests\test_realworld_rail_timetable.py
.\.venv\Scripts\python tests\test_realworld_rail_timetable_api.py
.\.venv\Scripts\python tests\test_realworld_rail_gtfs.py
.\.venv\Scripts\python tests\test_realworld_graph_scale_acceptance.py
.\.venv\Scripts\python tests\test_realworld_graph_scale_diagnostics.py
.\.venv\Scripts\python tests\test_realworld_validation_acceptance.py
.\.venv\Scripts\python tests\test_realworld_osrm_snapshot_manifest.py
.\.venv\Scripts\python tests\test_realworld_validation_review_packet.py
.\.venv\Scripts\python tests\test_realworld_route_road_evidence_exposure.py
.\.venv\Scripts\python scripts\audit_source_provenance.py --fail-on-blockers
.\.venv\Scripts\python scripts\audit_publication_readiness.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
.\.venv\Scripts\python scripts\write_osrm_snapshot_manifest.py
.\.venv\Scripts\python scripts\write_route_road_evidence_exposure.py
.\.venv\Scripts\python scripts\write_validation_review_packet.py
.\.venv\Scripts\python scripts\audit_sensitivity_diagnostics.py
.\.venv\Scripts\python scripts\write_sensitivity_review_packet.py
.\.venv\Scripts\python scripts\audit_plan_artifacts.py
.\.venv\Scripts\python scripts\write_goal_completion_audit.py
.\.venv\Scripts\python generate_report.py
rg -n "(^|\s)(from|import)\s+cloned_repo" src tests scripts
git diff --check
```

`git diff --check` reported only Windows LF-to-CRLF warnings. The
`cloned_repo` import check returned no matches.

Current generated artifact checks:

| Artifact | Rows / Status |
| --- | --- |
| `results/realworld_pilot/pilot_sample_results.csv` | 32 rows |
| `results/realworld_pilot/pilot_staged_results.csv` | 315 rows |
| `results/realworld_pilot/pilot_multi_corridor_results.csv` | 32 rows on the 164-node / 246-edge multi-corridor candidate graph |
| `results/realworld_pilot/pilot_multi_corridor_summary.csv` | 16 rows |
| `results/realworld_pilot/pilot_multi_corridor_full_results.csv` | 1,890 rows on the 164-node / 246-edge multi-corridor candidate graph |
| `results/realworld_pilot/pilot_multi_corridor_full_summary.csv` | 63 rows |
| `results/realworld_pilot/pilot_full_results.csv` | 1,890 rows |
| `results/realworld_pilot/pilot_full_summary.csv` | 63 rows |
| `results/realworld_pilot/tables/pilot_full_metric_ci.csv` | 819 full-pilot metric confidence-interval rows |
| `results/realworld_pilot/tables/pilot_full_paired_delta_ci.csv` | 702 paired policy-delta confidence-interval rows |
| `results/realworld_pilot/tables/pilot_multi_corridor_metric_ci.csv` | 208 multi-corridor candidate metric confidence-interval rows |
| `results/realworld_pilot/tables/pilot_multi_corridor_paired_delta_ci.csv` | 156 multi-corridor candidate paired policy-delta confidence-interval rows |
| `results/realworld_pilot/tables/pilot_multi_corridor_full_metric_ci.csv` | 819 full-profile multi-corridor candidate metric confidence-interval rows |
| `results/realworld_pilot/tables/pilot_multi_corridor_full_paired_delta_ci.csv` | 702 full-profile multi-corridor candidate paired policy-delta confidence-interval rows |
| `data/parameters/rail_service_evidence.csv` | 1 row |
| `data/parameters/rail_station_bindings.csv` | 4 official station-code rows; `binding_ready: true` |
| `data/parameters/rail_evidence_review_packet.csv` | 10 rail review rows; 7 rows weak for final-study rail claims; service timing still blocked |
| `data/parameters/rail_evidence_review_manifest.json` | station-binding ready, service publication not ready, and non-acceptance claim boundary |
| `data/rail/rail_timing_source_request_packet.csv` | 5 source-request rows for timetable, shortest-path, GTFS, capacity, and availability evidence |
| `data/rail/rail_timing_source_request_manifest.json` | source type counts, required external-input counts, and non-acceptance claim boundary |
| `scripts/audit_parameter_evidence.py` | `publication_ready: false`; 25 weak core parameters; 0 missing |
| `data/parameters/parameter_evidence_review_packet.csv` | 29 core-parameter review rows; 25 rows weak for final-study claims; review aid only |
| `data/parameters/parameter_evidence_review_manifest.json` | review priorities: 11 high, 14 medium, 4 low; non-acceptance claim boundary |
| `data/parameters/parameter_evidence_source_request_packet.csv` | 7 cross-cutting parameter evidence source-request rows; request aid only |
| `data/parameters/parameter_evidence_source_request_manifest.json` | covers 25 parameters; `publication_ready: false` |
| `scripts/audit_road_evidence.py` | `publication_ready: false`; 28,947 cached edges; 1.292% maxspeed parseable; 0% explicit capacity |
| `scripts/audit_road_evidence_diagnostics.py` | structurally ready; routeable review priorities currently emphasize residential, tertiary, secondary, primary, and trunk-class evidence gaps |
| `data/parameters/road_speed_evidence_candidates.csv` | 10 routeable road-class speed-candidate rows; 5 rows have observed OSM `maxspeed`; review aid only |
| `data/parameters/road_capacity_evidence_candidates.csv` | 10 routeable road-class capacity-candidate rows; 0 rows have parseable OSM `lanes`; evidence-gap review aid only |
| `data/parameters/road_evidence_review_packet.csv` | 10 routeable road-class review rows; all 10 weak for final-study road claims; review aid only |
| `data/parameters/road_evidence_review_manifest.json` | speed, capacity, base-disruption, and priority counts; non-acceptance claim boundary |
| `data/road/road_evidence_source_request_packet.csv` | 5 road evidence source-request rows; request aid only |
| `data/road/road_evidence_source_request_manifest.json` | source-type and evidence-field counts; `publication_ready: false` |
| `data/parameters/road_class_overrides_draft.csv` | 10 draft road-class override rows; all `expert assumption`; review worksheet only |
| `scripts/audit_road_overrides.py` | reviewed default override table absent, draft worksheet present, and accepted manifest does not apply overrides; `publication_ready: false` |
| `data/validation/accessibility_loss.csv` | 127 edge-removal diagnostic rows; 22 disconnected edge-removal cases |
| `data/validation/graph_scale_route_comparison.csv` | 3 full-vs-reduced route parity rows; all 3 pass for baseline shortest-time paths |
| `data/validation/graph_scale_alternate_routes.csv` | 9 alternate-route rows; 3 rank-1 paths pass and 6 alternate paths warn |
| `data/validation/graph_scale_multi_corridor_routes.csv` | 9 multi-corridor candidate rows; all 9 pass for top full-graph route candidates |
| `data/validation/full_graph_smoke_manifest.json` | 2 full-graph smoke rows on the 4,608-node / 9,148-edge bus-practical graph |
| `data/validation/full_graph_runtime_readiness_packet.csv` | 4 full-graph runtime-readiness rows; review aid only |
| `data/validation/graph_scale_review_packet.csv` | 4 graph-scale method option rows; review aid only |
| `data/validation/graph_scale_result_comparison.csv` | 819 current-vs-full-profile-candidate metric-delta rows; review aid only |
| `scripts/audit_source_provenance.py` | structurally ready; 11 source records, 52 local artifacts, 3 cached snapshots pending review, 4 context-only sources not cached, and 4 repository inputs pending review |
| `scripts/audit_publication_readiness.py` | `publication_ready: false`; final-study claims blocked |
| `scripts/audit_final_study_readiness.py` | `final_study_ready: false`; plan-level final gates blocked |
| `data/validation/canonical_route_road_evidence_exposure.csv` | 76 route-level road-evidence exposure rows across 18 route candidates; review aid only |
| `data/validation/canonical_route_road_evidence_exposure_manifest.json` | `publication_ready: false`, `acceptance_ready: false`, and 76 weak exposure rows |
| `data/validation/osrm_route_benchmark_manifest.json` | `publication_ready: false`, `acceptance_ready: false`, OSRM 3 pass rows, 3 cached external-router rows, 0 unpinned rows, 3 retained raw response files, query URLs, and CSV/summary checksums |
| `data/validation/validation_review_packet.csv` | 7 validation review rows; review aid only |
| `data/validation/validation_review_manifest.json` | `publication_ready: false`, `acceptance_ready: false`, internal plausibility 19 pass / 2 warn, fallback benchmark 2 pass / 1 warn, OSRM 3 pass with manifest present, route road-evidence exposure 76 weak rows, and 0 acceptance-gate closure candidates |
| `results/realworld_pilot/morris_results.csv` | 4,320 rows |
| `results/realworld_pilot/morris_summary.csv` | 7,056 rows |
| `scripts/audit_sensitivity_diagnostics.py` | structurally ready; current diagnostics report 0 unexplained missing/non-finite index rows, 168 explicitly unavailable index rows, 4,272 zero `mu_star` rows, reduced-graph scope, and scaffold claim boundaries; generated tables retain unavailable rows while ranking figures exclude non-finite values |
| `data/validation/sensitivity_review_packet.csv` | 6 sensitivity review rows; review aid only |
| `data/validation/sensitivity_review_manifest.json` | `publication_ready: false`, 0 unexplained missing/non-finite Morris index rows, 168 explicitly unavailable index rows, 4,272 zero `mu_star` rows, and 0 acceptance-gate closure candidates |
| `results/realworld_pilot/tables/main_result_table.csv` | 63 rows |
| `results/realworld_pilot/tables/sensitivity_result_table.csv` | 7,056 rows |
| `results/realworld_pilot/tables/bottleneck_attribution_table.csv` | 63 rows |
| `results/realworld_pilot/tables/policy_regime_table.csv` | 27 rows |
| `results/realworld_pilot/tables/figure_table_manifest.json` | valid JSON |
| `results/realworld_pilot/morris_manifest.json` | valid JSON |
| `data/manifests/reproducibility_manifest.json` | valid JSON |
| `scripts/audit_plan_artifacts.py` graph-scale checks | all pilot, sensitivity, Morris, and figure/table manifests record source and analysis graph scale |
| `docs/current_goal_completion_audit.md` | non-acceptance active-goal prompt-to-artifact checklist; `final_study_ready: false` |
| `data/manifests/current_goal_completion_audit.json` | structured non-acceptance active-goal prompt-to-artifact checklist; `can_mark_complete: false` |

## Remaining Blockers Before Final-Study Claim

1. Accept the pilot input package: region, OSM snapshot, source/analysis graph
   distinction, and privacy treatment.
2. Review source snapshots, license/attribution, privacy abstraction, cache
   manifests, reproduction paths, and claim limits, then create
   `data/manifests/provenance_acceptance.json` only after the provenance
   package is accepted.
3. Choose and implement the final graph-scale method: accepted corridor
   abstraction, full-graph runtime, or multi-corridor ensemble. The current
   3-row route-parity diagnostic, 9-row alternate-route diagnostic, 9-row
   multi-corridor candidate diagnostic, 2-row full-graph smoke manifest,
   4-row full-graph runtime-readiness packet, 4-option graph-scale review
   packet, 5-row graph-scale strategy-readiness packet, and 819-row
   current-vs-candidate result comparison
   support that review, but the 6 alternate-route warning rows must either be
   accepted under a documented corridor-selection rule or resolved by rerunning
   on the 164-node / 246-edge candidate graph, full-graph runtime evidence,
   multi-corridor experiments, or a reviewed
   `data/manifests/graph_scale_acceptance.json` decision.
4. Strengthen rail inputs with GTFS, public timetable, shortest-path, capacity,
   or equivalent service evidence. Official station-code binding now exists for
   `S`/`R`; timetable, headway-only, and shortest-path derivation scripts now
   exist; and optional data.go.kr train-schedule and shortest-path fetch
   helpers can create local caches when reviewed API requests and raw-response
   retention plans exist. Capacity is explicitly sensitivity-only. The current
   rail evidence cache still keeps headway, travel time, and availability as
   documented assumption proxies until reviewed target source payloads are
   accepted.
5. Strengthen road speed/capacity, background traffic, disruption, fleet,
   transfer, demand/time, and censoring parameters with public, literature,
   agency, benchmark-calibrated, or expert-reviewed values. Use
   `parameter_evidence_review_packet.csv` to prioritize core-parameter review,
   and use the road-class diagnostics, `road_speed_evidence_candidates.csv`,
   `road_capacity_evidence_candidates.csv`, and
   `road_evidence_review_packet.csv` to prioritize routeable road classes.
   Use `road_evidence_source_request_packet.csv` to collect source-backed
   speed, capacity, benchmark, disruption, and override-application inputs
   before creating reviewed overrides.
   Use `parameter_evidence_source_request_packet.csv` to collect
   cross-cutting demand, fleet, dispatch, transfer, disruption, and traffic/BPR
   source inputs before replacing or accepting weak parameter rows.
6. Review the optional OSRM benchmark manifest and decide whether another
   benchmark source is needed for the target journal. Use
   `docs/validation_strategy_readiness_packet.md` to resolve the current 3
   blocking and 4 human-review validation-strategy items, then record the
   accepted validation strategy in `data/manifests/validation_acceptance.json`.
7. Review the Morris sensitivity output for NaN/masked-value behavior, decide
   whether Sobol analysis is required, and record that decision in
   `data/manifests/sensitivity_acceptance.json`.
8. Review the staged/full pilot experiment package and create
   `data/manifests/experiment_acceptance.json` only after graph scope, input
   validation, scenario-policy-seed design, CRN pairing, row counts, and
   not-operational claim limits are accepted.
9. Keep the Korean report aligned with the broader public-sector disrupted
   regional mobility framing as evidence gates close.
10. Create `data/manifests/manuscript_acceptance.json` only after final
    paper/report wording, regenerated docx, figures/tables, evidence gates,
    result claims, and not-operational claim boundaries are reviewed.
11. Create `data/manifests/reproducibility_acceptance.json` only after
    clean-checkout validation, validation ladder, artifact regeneration,
    manifest paths, runtime import boundaries, command count, and
    not-operational claim boundaries are reviewed.
12. Commit/package the artifacts and prove clean-checkout reproduction.
13. Create `data/manifests/final_audit_acceptance.json` only after an
    independent prompt-to-artifact audit verifies every pre-final gate and no
    blocked gates remain.
14. Rewrite final manuscript/report result sections only after the accepted
   pilot inputs and evidence boundaries are closed.

## Claim Boundary

Allowed now:

- The repository implements an executable quasi-real pilot scaffold.
- The scaffold can convert a cached OSM-derived road graph into simulator-ready
  inputs.
- The scaffold can run bus-only, multimodal, disruption, policy, and Morris
  sensitivity experiments with reproducible outputs.
- The current figures and tables are planning-research scaffolds with explicit
  claim boundaries.

Not allowed yet:

- calibrated real-world performance claims;
- operational emergency or military route recommendations;
- universal superiority claims for bus-only or rail-bus transport;
- claims that OSM, OSRM, or current assumptions alone validate real operations.
