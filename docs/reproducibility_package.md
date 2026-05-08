# Reproducibility Package

This package records how to reproduce the current real-world or quasi-real
study scaffold. It does not certify calibrated real-world accuracy.

## Scope

Current reproducible artifacts are scaffold-only:

- current final-study status remains `final_study_ready=false`;
- the plan-level audit reports 3 / 15 ready gates
  (`real_input_smoke`, `structured_disruptions`, and `policy_alternatives`) and
  12 / 15 blocked gates;
- formal acceptance remains 0 / 12 ready, with all required formal acceptance
  artifacts absent and no final approval recorded;
- graph-scale, validation, sensitivity, and experiment strategy-readiness
  packets are present as review aids at
  `docs/graph_scale_strategy_readiness_packet.md`,
  `docs/validation_strategy_readiness_packet.md`,
  `docs/sensitivity_strategy_readiness_packet.md`, and
  `docs/experiment_strategy_readiness_packet.md`;
- cached public-coordinate Overpass/OSM pilot graph input
- cached road-input evidence audit for OSM length, highway, maxspeed,
  capacity, and base-disruption proxy coverage
- road-class evidence diagnostics that rank routeable highway classes by
  speed, capacity, and base-disruption evidence gaps without accepting them
- cached OSM `maxspeed` candidate evidence by routeable road class; this
  summarizes sparse public tags for reviewer triage without creating reviewed
  overrides or calibrated speed evidence
- cached OSM `lanes` capacity-candidate evidence by routeable road class; the
  current cache has no parseable lane observations, so this documents the
  remaining capacity evidence gap without accepting fallback capacities
- optional road-class override loader for reviewed speed, capacity, and
  base-disruption evidence tables
- draft road-class override template generator for reviewer worksheets, using
  diagnostics and current mapper defaults without creating acceptance evidence
- road-class override audit that keeps the missing reviewed default override
  table visible as a final-claim blocker and separately checks whether an
  accepted pilot manifest applied the reviewed table with a matching SHA256
- optional cached rail-timetable derivation path that records source artifact
  path, SHA256, and field-level timing evidence when a reviewed timetable
  extract is available; derived rows are ready only when the artifact resolves
  and the digest matches, and timetable station codes match official rail-point
  station bindings
- optional headway-only rail derivation and data.go.kr train-schedule fetch
  helper for reviewed access-station departure caches; this can support
  headway evidence but not travel-time evidence by itself
- optional cached static-GTFS derivation path that records source artifact
  path, SHA256, and field-level timing evidence when a reviewed GTFS zip or
  directory is available; derived rows are ready only when the artifact
  resolves and the digest matches
- optional cached rail shortest-path derivation path that records
  station-to-station travel-time evidence only, preserves source artifact path
  and SHA256, and checks shortest-path station codes against official
  rail-point station bindings
- optional data.go.kr shortest-path fetch helper that can create the local
  shortest-path cache from a reviewed live API request when `DATA_GO_KR_KEY`
  is available
- cached official line-specific station-code binding for the pilot rail points,
  kept separate from rail-service evidence
- optional station-binding derivation path that records source artifact path
  and SHA256 when a reviewed station extract is available
- bus-practical OSM edge filtering before simulator routing and connector
  snapping
- pilot smoke run
- graph-scale route parity diagnostic comparing the full bus-practical graph
  and reduced analysis corridor for the three canonical road legs; current
  rows are scaffold evidence only, not graph-scale acceptance
- graph-scale alternate-route sensitivity diagnostic comparing the top
  full-graph route candidates with the reduced corridor; current rank-1 paths
  are preserved, but alternate candidates warn and remain graph-scale
  uncertainty rather than acceptance evidence
- graph-scale multi-corridor candidate diagnostic preserving the top
  full-graph route candidates in a 164-node / 246-edge candidate graph; current
  rows all pass, but this is an upgrade path rather than final graph-scale
  acceptance
- graph-scale method review packet comparing the reduced corridor,
  multi-corridor candidate, and full bus-practical graph; it is review support
  only, not acceptance
- parameter-source, rail-assumption, and fleet-assumption tables
- parameter-acceptance schema for future reviewed weak assumptions retained
  within bounded final claims; no acceptance CSV is committed in the current
  scaffold
- parameter evidence readiness audit separating source-backed,
  benchmark-supported, assumption-only, and sensitivity-only core inputs
- parameter evidence review packet that turns the current audit into a 29-row
  reviewer worksheet; it is review support only and not accepted calibration
- parameter evidence source-request packet that names the cross-cutting demand,
  fleet, dispatch, transfer, disruption, and traffic/BPR source inputs still
  needed before weak parameters can be strengthened
- rail service evidence cache that currently marks timing values as an
  assumption proxy and capacity as sensitivity-only
- rail evidence review packet that consolidates station-binding readiness,
  rail-service timing gaps, capacity treatment, service-window assumptions, and
  available derivation paths; it is review support only
- rail timing source-request packet that lists the API-key or reviewed-file
  inputs and commands needed before cached rail timing evidence can be derived
- route plausibility sanity checks
- optional OSRM route benchmark snapshot
- optional OSRM route benchmark manifest that records CSV and summary
  checksums, query URLs, source-status counts, raw-payload inventory, and
  non-acceptance claim limits
- route-level accessibility-loss diagnostics for current baseline road legs
- route-level road-evidence exposure diagnostics linking weak speed, capacity,
  disruption, and connector assumptions to canonical route candidates
- structured disruption scenarios
- policy alternatives
- pilot experiment design metadata for sample, staged, and full profiles
- pilot scaffold sample experiment outputs
- deterministic one-at-a-time sensitivity screening outputs
- staged and full pilot profile outputs
- SALib Morris sensitivity outputs for the current full policy/scenario scaffold
- Morris sensitivity diagnostic audit for row-count consistency, blank/non-finite
  indices, zero-effect rows, reduced-graph scope, and scaffold claim boundaries
- sensitivity review packet that converts Morris diagnostics into a 6-row
  reviewer worksheet for index handling, zero-effect interpretation,
  reduced-graph scope, and Morris-vs-Sobol decision support without accepting
  sensitivity evidence
- sensitivity strategy-readiness packet that records Morris, graph-scope,
  scaffold-result, method-decision, and missing-acceptance blockers without
  accepting sensitivity evidence
- experiment strategy-readiness packet that records current full-pilot scope,
  graph/input dependencies, row-count/checksum, scenario-policy-seed, CRN, and
  missing-acceptance review items without accepting experiment outputs
- scaffold-only figures, result tables, bottleneck attribution proxy, policy
  regime map, and claim-boundary table
- scaffold-aligned English paper and Korean report source that state the
  current graph scales, full pilot row counts, Morris row counts, and
  non-calibrated claim boundary; `report.docx` is regenerated from
  `report_draft.md`
- current plan-gate audit separating executable scaffold evidence from
  remaining final-study blockers
- source provenance manifest that lists source URLs, license/terms notes,
  snapshot/access dates, local artifacts, review status, and claim boundaries
  without accepting final-study provenance
- graph-scale acceptance schema for a future reviewed
  `data/manifests/graph_scale_acceptance.json` record; the record is
  intentionally absent in the current scaffold
- validation acceptance schema for a future reviewed
  `data/manifests/validation_acceptance.json` record; the record is
  intentionally absent in the current scaffold
- sensitivity acceptance schema for a future reviewed
  `data/manifests/sensitivity_acceptance.json` record; the record is
  intentionally absent in the current scaffold
- experiment-output acceptance schema for a future reviewed
  `data/manifests/experiment_acceptance.json` record; the record is
  intentionally absent in the current scaffold
- provenance acceptance schema for a future reviewed
  `data/manifests/provenance_acceptance.json` record; the record is
  intentionally absent in the current scaffold
- manuscript/report acceptance schema for a future reviewed
  `data/manifests/manuscript_acceptance.json` record; the record is
  intentionally absent in the current scaffold
- clean-checkout reproducibility acceptance schema for a future reviewed
  `data/manifests/reproducibility_acceptance.json` record; the record is
  intentionally absent in the current scaffold
- independent final-audit acceptance schema for a future reviewed
  `data/manifests/final_audit_acceptance.json` record; the record is
  intentionally absent in the current scaffold
- pilot acceptance schema for a future human-reviewed
  `data/manifests/pilot_acceptance.json` record; the record is intentionally
  absent in the current scaffold
- publication-readiness audit aggregating parameter, road, rail-service, and
  station-binding evidence gates
- final-study readiness audit mapping every `plan.md` final gate to concrete
  artifacts while separating scaffold artifact presence from final-study
  readiness
- current active-goal completion audit that restates the objective as concrete
  gates, lists named acceptance artifacts, rejects proxy-only completion
  signals, and keeps the project blocked until reviewed final-study gates close
- clean-checkout reproducibility review packet that records scaffold manifest
  scope, formal acceptance-record absence, current Git worktree state,
  untracked artifact risk, validation command ladder coverage, runtime
  `cloned_repo` import boundary, and the fact that full clean-checkout
  reproduction has not been accepted
- bounded clean source-checkout smoke manifest, command log, and markdown
  summary; the current clean-checkout smoke clones the committed tree with
  Windows long-path support and runs an 8-command minimal profile using the
  current Python environment, but it is not clean-environment dependency
  reinstall evidence and does not close reproducibility acceptance
- bounded current-worktree reproducibility smoke manifest and command log; the
  current smoke records passing command counts in
  `data/validation/reproducibility_smoke_manifest.json`, but it is not a
  formal clean-checkout acceptance record and cannot close reproducibility
  acceptance
- reduced-corridor method note and route-parity diagnostic explaining the
  current graph-scale boundary

The current package is appropriate for implementation verification and
manuscript scaffolding. It is not an operational forecast, route plan, or
publication-grade calibrated case study.

## Reproduction Commands

Run from the repository root on Windows PowerShell:

```powershell
.\.venv\Scripts\python scripts\run_pilot_smoke.py
.\.venv\Scripts\python scripts\run_full_graph_smoke.py
.\.venv\Scripts\python scripts\run_graph_scale_diagnostics.py
.\.venv\Scripts\python scripts\write_full_graph_runtime_readiness_packet.py
.\.venv\Scripts\python scripts\write_graph_scale_review_packet.py
.\.venv\Scripts\python scripts\write_graph_scale_result_comparison.py
.\.venv\Scripts\python scripts\audit_rail_evidence.py
.\.venv\Scripts\python scripts\write_rail_evidence_review_packet.py
.\.venv\Scripts\python scripts\write_rail_timing_source_request_packet.py
.\.venv\Scripts\python scripts\audit_rail_station_bindings.py
.\.venv\Scripts\python scripts\audit_parameter_evidence.py
.\.venv\Scripts\python scripts\write_parameter_review_packet.py
.\.venv\Scripts\python scripts\write_parameter_evidence_source_request_packet.py
.\.venv\Scripts\python scripts\audit_road_evidence.py
.\.venv\Scripts\python scripts\audit_road_evidence_diagnostics.py
.\.venv\Scripts\python scripts\write_road_capacity_evidence.py
.\.venv\Scripts\python scripts\write_road_speed_evidence.py
.\.venv\Scripts\python scripts\write_road_evidence_review_packet.py
.\.venv\Scripts\python scripts\write_road_evidence_source_request_packet.py
.\.venv\Scripts\python scripts\write_road_class_override_template.py --output data\parameters\road_class_overrides_draft.csv --overwrite
.\.venv\Scripts\python scripts\audit_road_overrides.py
.\.venv\Scripts\python scripts\audit_source_provenance.py
.\.venv\Scripts\python scripts\audit_publication_readiness.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
.\.venv\Scripts\python scripts\run_plausibility_validation.py
.\.venv\Scripts\python scripts\run_accessibility_loss_analysis.py
.\.venv\Scripts\python scripts\write_osrm_snapshot_manifest.py --raw-response-dir data\validation\osrm_route_raw
.\.venv\Scripts\python scripts\write_route_road_evidence_exposure.py
.\.venv\Scripts\python scripts\write_validation_review_packet.py
.\.venv\Scripts\python scripts\write_reproducibility_review_packet.py
.\.venv\Scripts\python scripts\run_reproducibility_smoke.py
.\.venv\Scripts\python scripts\run_clean_checkout_smoke.py
.\.venv\Scripts\python scripts\run_pilot_experiments.py --sample
.\.venv\Scripts\python scripts\run_pilot_experiments.py --staged
.\.venv\Scripts\python scripts\run_pilot_experiments.py --multi-corridor
.\.venv\Scripts\python scripts\run_pilot_experiments.py --multi-corridor-full
.\.venv\Scripts\python scripts\run_pilot_experiments.py --full
.\.venv\Scripts\python scripts\run_sensitivity.py --sample
.\.venv\Scripts\python scripts\run_sensitivity.py --method morris --all
.\.venv\Scripts\python scripts\audit_sensitivity_diagnostics.py
.\.venv\Scripts\python scripts\write_sensitivity_review_packet.py
.\.venv\Scripts\python scripts\write_sensitivity_strategy_readiness_packet.py
.\.venv\Scripts\python scripts\write_experiment_strategy_readiness_packet.py
.\.venv\Scripts\python scripts\make_pilot_statistics.py
.\.venv\Scripts\python scripts\make_pilot_statistics.py --input results\realworld_pilot\pilot_multi_corridor_results.csv --source-manifest results\realworld_pilot\pilot_multi_corridor_manifest.json --output-prefix pilot_multi_corridor
.\.venv\Scripts\python scripts\make_pilot_statistics.py --input results\realworld_pilot\pilot_multi_corridor_full_results.csv --source-manifest results\realworld_pilot\pilot_multi_corridor_full_manifest.json --output-prefix pilot_multi_corridor_full
.\.venv\Scripts\python scripts\make_pilot_figures.py
.\.venv\Scripts\python scripts\audit_plan_artifacts.py
.\.venv\Scripts\python scripts\write_goal_completion_audit.py
.\.venv\Scripts\python generate_report.py
```

Optional live external-router snapshot:

```powershell
.\.venv\Scripts\python scripts\run_osrm_route_benchmark.py
```

Optional live external-router snapshot with retained raw payloads:

```powershell
.\.venv\Scripts\python scripts\run_osrm_route_benchmark.py --raw-output-dir data\validation\osrm_route_raw
```

Offline OSRM snapshot manifest:

```powershell
.\.venv\Scripts\python scripts\write_osrm_snapshot_manifest.py --raw-response-dir data\validation\osrm_route_raw
```

Optional live rail shortest-path cache fetch:

```powershell
.\.venv\Scripts\python scripts\fetch_rail_shortest_path_cache.py `
  --departure-station-name 올림픽공원 `
  --arrival-station-name 잠실 `
  --search-dt "2026-05-04 09:00:00" `
  --access-station-name 올림픽공원 `
  --access-station-code 936 `
  --egress-station-name 잠실 `
  --egress-station-code 814 `
  --output data\rail\pilot_rail_shortest_path_cache.csv `
  --raw-output data\rail\pilot_rail_shortest_path_raw.json
```

This command requires `DATA_GO_KR_KEY` or `--service-key`. It creates a local
cache only; the cache must be reviewed before
`scripts\derive_rail_shortest_path_evidence.py` is used for final-study rail
travel-time evidence.

Optional live rail timetable cache fetch:

```powershell
.\.venv\Scripts\python scripts\fetch_rail_timetable_cache.py `
  --line-name "9호선" `
  --upbdnb-se "상행" `
  --wknd-se "평일" `
  --station-name "올림픽공원" `
  --station-code 936 `
  --access-station-name "올림픽공원" `
  --access-station-code 936 `
  --output data\rail\pilot_rail_timetable_cache.csv `
  --raw-output data\rail\pilot_rail_timetable_raw.json
```

This command also requires `DATA_GO_KR_KEY` or `--service-key`. It creates a
local cache only; the cache must be reviewed before timetable or headway
evidence derivation is used for final-study claims.

Optional reruns for individual pilot experiment profiles:

```powershell
.\.venv\Scripts\python scripts\run_pilot_experiments.py --staged
.\.venv\Scripts\python scripts\run_pilot_experiments.py --multi-corridor
.\.venv\Scripts\python scripts\run_pilot_experiments.py --full
```

Optional reviewed road-class override run:

```powershell
.\.venv\Scripts\python scripts\run_pilot_experiments.py --sample --road-class-overrides-path data\parameters\road_class_overrides.csv
```

When supplied, the pilot manifest records the override path and SHA256 digest
so later results can be tied to the reviewed table version.

Optional draft road-class override worksheet:

```powershell
.\.venv\Scripts\python scripts\write_road_class_override_template.py --output data\parameters\road_class_overrides_draft.csv --overwrite
```

This creates a review worksheet only. It mirrors current mapper defaults and
does not close the road evidence gate until values and sources are replaced by
reviewed evidence.

Optional cached OSM maxspeed candidate table:

```powershell
.\.venv\Scripts\python scripts\write_road_speed_evidence.py
```

This writes `data/parameters/road_speed_evidence_candidates.csv` and
`data/parameters/road_speed_evidence_manifest.json`. The current table has 10
routeable road-class rows and 5 rows with observed `maxspeed` tags. It is a
speed-evidence review aid only; reviewed values still need to be accepted in
`data/parameters/road_class_overrides.csv` before final road-calibration
claims.

Optional cached OSM lane-count capacity candidate table:

```powershell
.\.venv\Scripts\python scripts\write_road_capacity_evidence.py
```

This writes `data/parameters/road_capacity_evidence_candidates.csv` and
`data/parameters/road_capacity_evidence_manifest.json`. The current table has
10 routeable road-class rows and 0 rows with parseable lane observations, so it
documents that capacity still depends on fallback mapper proxies.

Road-input evidence review packet:

```powershell
.\.venv\Scripts\python scripts\write_road_evidence_review_packet.py
```

This writes `data/parameters/road_evidence_review_packet.csv` and
`data/parameters/road_evidence_review_manifest.json`. The current packet has
10 routeable road-class rows and marks all 10 rows weak for final-study road
claims. It consolidates speed, capacity, disruption, and draft-override review
status without accepting or applying any road-class override.

Road evidence source-request packet:

```powershell
.\.venv\Scripts\python scripts\write_road_evidence_source_request_packet.py
```

This writes `data/road/road_evidence_source_request_packet.csv` and
`data/road/road_evidence_source_request_manifest.json`. The current packet has
5 request rows for speed, capacity, benchmark, disruption, and
override-application source inputs. It does not create
`road_class_overrides.csv` and does not close road evidence gates.

Core-parameter evidence review packet:

```powershell
.\.venv\Scripts\python scripts\write_parameter_review_packet.py
```

This writes `data/parameters/parameter_evidence_review_packet.csv` and
`data/parameters/parameter_evidence_review_manifest.json`. The current packet
has 29 core-parameter rows and 25 rows marked weak for final-study claims. It
prioritizes evidence upgrades but does not accept any value.

Parameter evidence source-request packet:

```powershell
.\.venv\Scripts\python scripts\write_parameter_evidence_source_request_packet.py
```

This writes `data/parameters/parameter_evidence_source_request_packet.csv` and
`data/parameters/parameter_evidence_source_request_manifest.json`. The current
packet has 6 request rows covering 22 demand, fleet, dispatch, transfer,
disruption, and traffic/BPR parameters. It is a source-request worksheet only,
not source evidence, accepted calibration, or weak-parameter acceptance.

Optional cached station binding derivation:

```powershell
.\.venv\Scripts\python scripts\derive_rail_station_bindings.py --input data\rail\pilot_station_binding_cache.csv --output data\parameters\rail_station_bindings.csv --binding-id-prefix songpa_public_demo_station_binding_v1 --region-id songpa_public_demo --source-name "Seoul Open Data Plaza SearchInfoBySubwayNameService cached extract" --source-url-or-citation "https://data.seoul.go.kr/dataList/OA-121/S/1/datasetView.do" --source-accessed-date 2026-05-04 --required-points S,R
```

Optional cached rail shortest-path derivation:

```powershell
.\.venv\Scripts\python scripts\derive_rail_shortest_path_evidence.py --input data\rail\pilot_rail_shortest_path_cache.csv --output data\parameters\rail_service_evidence.csv --evidence-id songpa_public_demo_rail_shortest_path_v1 --region-id songpa_public_demo --access-point S --egress-point R --source-name "Cached Seoul subway shortest-path extract" --source-url-or-citation "https://data.seoul.go.kr/dataList/OA-22724/A/1/datasetView.do" --extraction-date 2026-05-04 --headway-min-proxy 10 --capacity-pax-per-train 500 --service-window "weekday selected service window" --route-type minimum_time --station-bindings data\parameters\rail_station_bindings.csv
```

This command can strengthen rail travel-time evidence only. Headway and
capacity still need separate timetable/source-backed evidence or explicit
sensitivity-only treatment before publication claims.

Optional cached static-GTFS derivation:

```powershell
.\.venv\Scripts\python scripts\derive_rail_gtfs_evidence.py --input data\rail\pilot_gtfs.zip --output data\parameters\rail_service_evidence.csv --evidence-id songpa_public_demo_rail_gtfs_v1 --region-id songpa_public_demo --access-point S --egress-point R --access-stop-id ACCESS_STOP_ID --egress-stop-id EGRESS_STOP_ID --source-name "Reviewed static GTFS feed" --source-url-or-citation "GTFS source URL or citation" --extraction-date 2026-05-04 --capacity-pax-per-train 500 --service-window "weekday selected service window" --route-id ROUTE_ID
```

This command can strengthen scheduled headway and access-to-egress travel-time
evidence only after the GTFS artifact is reviewed and reproducible. It does
not prove emergency rail availability, station processing capacity, or train
capacity.

Validation ladder:

```powershell
.\.venv\Scripts\python -m compileall main.py src tests scripts generate_report.py
Get-ChildItem tests\test_*.py | ForEach-Object { .\.venv\Scripts\python $_.FullName }
.\.venv\Scripts\python tests\test_realworld_experiment_acceptance.py
.\.venv\Scripts\python tests\test_realworld_provenance_acceptance.py
.\.venv\Scripts\python tests\test_realworld_manuscript_acceptance.py
.\.venv\Scripts\python tests\test_realworld_reproducibility_acceptance.py
.\.venv\Scripts\python tests\test_realworld_reproducibility_review_packet.py
.\.venv\Scripts\python tests\test_realworld_reproducibility_smoke.py
.\.venv\Scripts\python tests\test_realworld_final_audit_acceptance.py
.\.venv\Scripts\python tests\test_realworld_rail_shortest_path_api.py
.\.venv\Scripts\python tests\test_realworld_rail_timetable_api.py
.\.venv\Scripts\python tests\test_realworld_rail_gtfs.py
.\.venv\Scripts\python tests\test_realworld_road_override_template.py
.\.venv\Scripts\python tests\test_realworld_graph_scale_diagnostics.py
.\.venv\Scripts\python scripts\run_full_graph_smoke.py
.\.venv\Scripts\python scripts\run_graph_scale_diagnostics.py
.\.venv\Scripts\python scripts\write_full_graph_runtime_readiness_packet.py
.\.venv\Scripts\python scripts\write_graph_scale_review_packet.py
.\.venv\Scripts\python scripts\write_graph_scale_result_comparison.py
.\.venv\Scripts\python scripts\audit_rail_evidence.py
.\.venv\Scripts\python scripts\write_rail_evidence_review_packet.py
.\.venv\Scripts\python scripts\write_rail_timing_source_request_packet.py
.\.venv\Scripts\python scripts\audit_rail_station_bindings.py
.\.venv\Scripts\python scripts\audit_parameter_evidence.py
.\.venv\Scripts\python scripts\write_parameter_review_packet.py
.\.venv\Scripts\python scripts\write_parameter_evidence_source_request_packet.py
.\.venv\Scripts\python scripts\audit_road_evidence.py
.\.venv\Scripts\python scripts\audit_road_evidence_diagnostics.py
.\.venv\Scripts\python scripts\write_road_capacity_evidence.py
.\.venv\Scripts\python scripts\write_road_speed_evidence.py
.\.venv\Scripts\python scripts\write_road_evidence_review_packet.py
.\.venv\Scripts\python scripts\write_road_evidence_source_request_packet.py
.\.venv\Scripts\python scripts\write_road_class_override_template.py --output data\parameters\road_class_overrides_draft.csv --overwrite
.\.venv\Scripts\python scripts\audit_road_overrides.py
.\.venv\Scripts\python scripts\audit_source_provenance.py
.\.venv\Scripts\python scripts\audit_publication_readiness.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
.\.venv\Scripts\python scripts\audit_sensitivity_diagnostics.py
.\.venv\Scripts\python scripts\write_sensitivity_review_packet.py
.\.venv\Scripts\python scripts\write_sensitivity_strategy_readiness_packet.py
.\.venv\Scripts\python scripts\write_experiment_strategy_readiness_packet.py
.\.venv\Scripts\python scripts\write_osrm_snapshot_manifest.py --raw-response-dir data\validation\osrm_route_raw
.\.venv\Scripts\python scripts\write_route_road_evidence_exposure.py
.\.venv\Scripts\python scripts\write_validation_review_packet.py
.\.venv\Scripts\python scripts\audit_plan_artifacts.py
.\.venv\Scripts\python scripts\write_goal_completion_audit.py
rg -n "(^|\s)(from|import)\s+cloned_repo" src tests scripts
git diff --check
```

## Input Manifest

| Artifact | Role | Scope |
| --- | --- | --- |
| `data/regions/pilot_region.yaml` | Pilot region, zones, rail points, and rail service assumptions | public/synthetic pilot scaffold |
| `docs/pilot_acceptance_schema.md` | Optional final-study pilot acceptance schema | future human acceptance record only; no accepted record is committed |
| `docs/graph_scale_acceptance_schema.md` | Optional final-study graph-scale acceptance schema | future reviewed graph-scale decision only; no accepted record is committed |
| `docs/graph_scale_diagnostics.md` | Full-vs-reduced route parity diagnostic note | current scaffold review support, not graph-scale acceptance |
| `docs/graph_scale_review_packet.md` | Graph-scale method review packet documentation | review support only; not graph-scale acceptance |
| `docs/validation_acceptance_schema.md` | Optional final-study validation acceptance schema | future reviewed benchmark strategy only; no accepted record is committed |
| `docs/validation_review_packet.md` | Validation-strategy review packet documentation | review support only; not validation acceptance |
| `docs/validation_strategy_readiness_packet.md` | Validation strategy-readiness packet documentation | blocker/readiness review support only; not validation acceptance |
| `docs/route_road_evidence_exposure.md` | Route-level road-evidence exposure documentation | review support only; not road calibration or validation acceptance |
| `docs/sensitivity_acceptance_schema.md` | Optional final-study sensitivity acceptance schema | future reviewed sensitivity method and Sobol decision only; no accepted record is committed |
| `docs/sensitivity_diagnostics.md` | Morris sensitivity diagnostic note | current scaffold review support, not sensitivity acceptance |
| `docs/sensitivity_strategy_readiness_packet.md` | Sensitivity strategy-readiness packet documentation | blocker/readiness review support only; not sensitivity acceptance or Sobol waiver |
| `docs/experiment_acceptance_schema.md` | Optional final-study experiment-output acceptance schema | future reviewed graph-scope, validation, design, CRN, count, and claim-boundary decision only; no accepted record is committed |
| `docs/experiment_strategy_readiness_packet.md` | Experiment strategy-readiness packet documentation | blocker/readiness review support only; not experiment acceptance |
| `docs/provenance_acceptance_schema.md` | Optional final-study provenance acceptance schema | future reviewed source/license/snapshot/privacy decision only; no accepted record is committed |
| `data/manifests/source_provenance_manifest.json` | Source provenance review packet | source/license/snapshot manifest only; not acceptance |
| `docs/source_provenance_manifest.md` | Source provenance manifest documentation | review support for provenance gate |
| `docs/manuscript_acceptance_schema.md` | Optional final-study manuscript/report acceptance schema | future reviewed paper/report/figure/claim-boundary decision only; no accepted record is committed |
| `docs/reproducibility_acceptance_schema.md` | Optional final-study reproducibility acceptance schema | future reviewed clean-checkout reproduction decision only; no accepted record is committed |
| `docs/reproducibility_review_packet.md` | Clean-checkout reproducibility review packet documentation | review support only; not reproducibility acceptance |
| `docs/reproducibility_smoke.md` | Current-worktree reproducibility smoke summary | execution evidence only; not clean-checkout acceptance |
| `docs/clean_checkout_reproducibility_smoke.md` | Bounded clean source-checkout smoke summary | source-checkout smoke evidence only; not clean-environment reproduction or acceptance |
| `docs/final_audit_acceptance_schema.md` | Optional final-study independent-audit acceptance schema | future reviewed prompt-to-artifact completion decision only; no accepted record is committed |
| `docs/parameter_evidence_review_packet.md` | Parameter review packet documentation | review support only; not accepted calibration |
| `docs/parameter_evidence_source_request_packet.md` | Parameter evidence source-request packet documentation | request support only; not accepted calibration |
| `data/cache/pilot_region_road.graphml` | Cached road graph input | offline Overpass/OSM snapshot |
| `data/cache/pilot_region_road_manifest.json` | Cache metadata | OSM attribution and claim-limit note |
| `docs/road_evidence_diagnostics.md` | Road-class evidence diagnostic note | review support for routeable-class speed, capacity, and disruption proxy gaps |
| `docs/road_evidence_review_packet.md` | Road-input evidence review packet documentation | review support only; not accepted road calibration |
| `docs/road_evidence_source_request_packet.md` | Road evidence source-request packet documentation | request support only; not accepted road calibration |
| `data/parameters/road_speed_evidence_candidates.csv` | Cached OSM maxspeed candidate evidence by routeable road class | 10 rows, 5 rows with observed `maxspeed`; review aid only |
| `data/parameters/road_speed_evidence_manifest.json` | Candidate speed evidence manifest | records sparse-tag claim boundary and non-publication-ready status |
| `data/parameters/road_capacity_evidence_candidates.csv` | Cached OSM lane-count capacity candidate evidence by routeable road class | 10 rows, 0 rows with observed `lanes`; documents capacity evidence gap |
| `data/parameters/road_capacity_evidence_manifest.json` | Candidate capacity evidence manifest | records lane-tag claim boundary and non-publication-ready status |
| `data/parameters/road_evidence_review_packet.csv` | Road-input evidence review worksheet | 10 routeable road-class rows; all weak for final-study road claims |
| `data/parameters/road_evidence_review_manifest.json` | Road-input review-packet manifest | summarizes speed, capacity, disruption, priority, and non-acceptance claim boundary |
| `data/road/road_evidence_source_request_packet.csv` | Road evidence source-request worksheet | 5 request rows for speed, capacity, benchmark, disruption, and override-application evidence; request aid only |
| `data/road/road_evidence_source_request_manifest.json` | Road evidence source-request manifest | summarizes required source inputs and keeps `publication_ready: false` |
| road-class override table | Optional reviewed speed/capacity/disruption evidence | not committed or applied in current default pilot outputs |
| `docs/road_class_override_schema.md` | Road-class override schema and claim limits | optional upgrade path for reviewed speed/capacity/disruption inputs |
| `scripts/write_road_class_override_template.py` | Draft road-class override worksheet generator | non-acceptance reviewer aid populated from diagnostics and current mapper defaults |
| `data/parameters/road_class_overrides_draft.csv` | Current draft road-class override worksheet | 10 routeable road-class rows, all `expert assumption`; review aid only |
| `scripts/audit_road_overrides.py` | Optional road-class override evidence audit | reports the missing default override table without failing |
| `data/parameters/parameter_sources.csv` | Parameter-source table | assumption and sensitivity evidence |
| `data/parameters/parameter_evidence_review_packet.csv` | Core-parameter evidence review worksheet | 29 rows, 25 weak for final-study claims; review support only |
| `data/parameters/parameter_evidence_review_manifest.json` | Parameter review-packet manifest | summarizes weak rows, priorities, groups, and non-acceptance claim boundary |
| `data/parameters/parameter_evidence_source_request_packet.csv` | Cross-cutting parameter evidence source-request worksheet | 6 rows for demand, fleet, dispatch, transfer, disruption, and traffic/BPR source inputs; request aid only |
| `data/parameters/parameter_evidence_source_request_manifest.json` | Parameter source-request manifest | summarizes covered parameters and keeps `publication_ready: false` |
| `docs/parameter_acceptance_schema.md` | Optional weak-parameter acceptance schema | future reviewed acceptance only; no accepted record is committed |
| `data/parameters/rail_assumptions.csv` | Rail evidence table | documented assumptions |
| `data/parameters/rail_evidence_sources.csv` | Rail source review index | context for station, timetable, shortest-path, and capacity evidence |
| `data/parameters/rail_service_evidence.csv` | Rail service value evidence cache | current row is assumption proxy for timing and sensitivity-only for capacity, not timetable-derived |
| `data/rail/pilot_station_binding_cache.csv` | Cached Seoul Open Data Plaza station-name search extract | official station identifiers only; not service evidence |
| `data/parameters/rail_station_bindings.csv` | Rail-point station binding evidence | official line-specific station-code bindings for `S` and `R`; not service evidence |
| `data/parameters/rail_evidence_review_packet.csv` | Rail evidence review worksheet | 10 rows; station binding ready, timing evidence weak, service publication not ready |
| `data/parameters/rail_evidence_review_manifest.json` | Rail review-packet manifest | summarizes rail status counts and non-acceptance claim boundary |
| `docs/rail_evidence_review_packet.md` | Rail evidence review packet documentation | review support only; not rail-service calibration |
| `data/rail/rail_timing_source_request_packet.csv` | Rail timing source-request worksheet | 5 rows naming required API-key, GTFS, capacity, and availability inputs |
| `data/rail/rail_timing_source_request_manifest.json` | Rail timing source-request manifest | source request counts and non-acceptance claim boundary |
| `docs/rail_timing_source_request_packet.md` | Rail timing source-request documentation | request support only; not cached timing evidence |
| `docs/rail_station_cache_schema.md` | Cached station extract schema and derivation command | optional upgrade path for official station binding evidence |
| `docs/rail_timetable_cache_schema.md` | Cached timetable extract schema and derivation command | optional upgrade path for derived rail timing evidence |
| `docs/rail_gtfs_cache_schema.md` | Cached static-GTFS extract schema and derivation command | optional upgrade path for scheduled headway and access-to-egress travel-time evidence |
| `scripts/fetch_rail_timetable_cache.py` | Optional live data.go.kr train-schedule cache fetcher | key-required source-caching helper; not default validation |
| `scripts/derive_rail_headway_evidence.py` | Optional cached timetable headway derivation | headway-only evidence path; does not satisfy travel-time evidence alone |
| `docs/rail_shortest_path_cache_schema.md` | Cached shortest-path extract schema and derivation command | optional upgrade path for station-to-station travel-time evidence only |
| `scripts/fetch_rail_shortest_path_cache.py` | Optional live data.go.kr shortest-path cache fetcher | key-required source-caching helper; not default validation |
| `data/parameters/fleet_assumptions.csv` | Fleet evidence table | documented assumptions |
| `data/validation/route_plausibility.csv` | Route plausibility checks | scaffold sanity evidence |
| `data/validation/external_route_benchmarks.csv` | Offline fallback route benchmark checks | deterministic fallback plausibility evidence |
| `data/validation/external_route_benchmarks_osrm.csv` | Optional OSRM route benchmark snapshot | external-router plausibility evidence, not ground truth |
| `data/validation/osrm_route_benchmark_summary.md` | Optional OSRM benchmark summary | records status rows and claim limits |
| `data/validation/osrm_route_benchmark_manifest.json` | Optional OSRM benchmark manifest | CSV/summary SHA256, query URLs, source-status counts, raw-payload inventory, and non-acceptance boundary |
| `data/validation/osrm_route_raw/` | Optional retained OSRM raw responses | traceability support only when live capture is run with `--raw-output-dir`; absent or empty raw payloads block cached-evidence treatment |
| `data/validation/accessibility_loss.csv` | Directed edge-removal accessibility-loss diagnostics | scaffold route-fragility evidence, not calibrated |
| `data/validation/accessibility_loss_summary.md` | Accessibility-loss diagnostic summary | claim-boundary and review notes |
| `data/validation/canonical_route_road_evidence_exposure.csv` | Route-level road-evidence exposure worksheet | 76 rows linking weak road evidence to canonical route candidates; review aid only |
| `data/validation/canonical_route_road_evidence_exposure_manifest.json` | Route exposure manifest | non-acceptance summary; `publication_ready: false` and `acceptance_ready: false` |
| `data/validation/validation_review_packet.csv` | Validation-strategy review worksheet | 7 rows summarizing internal plausibility, fallback/OSRM benchmarks, accessibility loss, route road-evidence exposure, summary scope, and benchmark-strategy decision requirement |
| `data/validation/validation_strategy_readiness_packet.csv` | Validation strategy-readiness worksheet | 7 blocker/human-review rows; not validation acceptance |
| `data/validation/reproducibility_review_packet.csv` | Clean-checkout reproducibility review worksheet | 8 rows summarizing scaffold scope, formal acceptance absence, Git worktree state, untracked artifact risk, validation command ladder, runtime import boundary, bounded clean-checkout smoke, and clean-environment execution scope |
| `data/validation/reproducibility_smoke_manifest.json` | Current-worktree smoke manifest | bounded smoke summary with `can_mark_complete: false` |
| `data/validation/reproducibility_smoke_log.jsonl` | Current-worktree smoke command log | JSONL command records for smoke review |
| `data/validation/clean_checkout_reproducibility_smoke_manifest.json` | Bounded clean source-checkout smoke manifest | 8-command clean-checkout minimal profile; `can_mark_complete: false` |
| `data/validation/clean_checkout_reproducibility_smoke_log.jsonl` | Bounded clean source-checkout smoke command log | JSONL outer-step and inner-command records for smoke review |
| `data/validation/validation_review_manifest.json` | Validation review manifest | non-acceptance summary; `publication_ready: false`, `acceptance_ready: false`, and 0 acceptance-gate closure candidates |
| `data/validation/graph_scale_route_comparison.csv` | Full-vs-reduced route parity checks for `A -> D`, `A -> S`, and `R -> D` | scaffold graph-scale review evidence, not acceptance |
| `data/validation/graph_scale_route_comparison_summary.md` | Route parity summary and claim boundary | current 3-row diagnostic summary, not acceptance |
| `data/validation/graph_scale_alternate_routes.csv` | Top full-graph alternate-route checks for `A -> D`, `A -> S`, and `R -> D` | scaffold alternate-corridor sensitivity evidence, not acceptance |
| `data/validation/graph_scale_alternate_routes_summary.md` | Alternate-route summary and claim boundary | current 9-row diagnostic summary with 3 pass and 6 warn rows, not acceptance |
| `data/validation/graph_scale_multi_corridor_routes.csv` | Top full-graph route checks against a candidate multi-corridor graph | scaffold multi-corridor upgrade evidence, not acceptance |
| `data/validation/graph_scale_multi_corridor_routes_summary.md` | Multi-corridor candidate summary and claim boundary | current 9-row diagnostic summary with 9 pass rows, not acceptance |
| `data/validation/graph_scale_review_packet.csv` | Graph-scale method option worksheet | 4 rows comparing reduced, small multi-corridor, full-profile multi-corridor, and full graph options; review support only |
| `data/validation/graph_scale_review_manifest.json` | Graph-scale review-packet manifest | non-acceptance option summary and review items |
| `data/validation/graph_scale_result_comparison.csv` | Current full-pilot versus full-profile multi-corridor candidate metric deltas | 819 review rows, not graph-scale acceptance |
| `data/validation/graph_scale_result_comparison_manifest.json` | Graph-scale result-comparison manifest | status counts and review items; non-acceptance |
| `data/validation/sensitivity_review_packet.csv` | Sensitivity diagnostic review worksheet | 6 rows summarizing Morris structural readiness, explicitly unavailable index rows, unexplained missing/non-finite index checks, zero `mu_star`, reduced graph scope, result scope, and Sobol-decision review |
| `data/validation/sensitivity_review_manifest.json` | Sensitivity review manifest | non-acceptance summary with 0 unexplained index-issue rows, 168 explicitly unavailable index rows, and 4,272 zero `mu_star` rows |
| `data/validation/sensitivity_strategy_readiness_packet.csv` | Sensitivity strategy-readiness worksheet | 7 blocker/human-review rows; not sensitivity acceptance |
| `data/manifests/experiment_strategy_readiness_packet.csv` | Experiment strategy-readiness worksheet | 9 blocker/human-review rows; not experiment acceptance |
| `data/scenarios/disruption_scenarios.csv` | Structured disruption scenarios | scenario-based definitions |
| `data/scenarios/policy_alternatives.csv` | Policy alternatives | decision-support variants |
| `data/scenarios/sensitivity_design.csv` | Sensitivity screening design | deterministic OAT and SALib Morris scaffold |
| `data/manifests/pilot_experiment_design.json` | Sample, staged, full, and graph-scale candidate pilot scenario-policy-seed design | quasi-real experiment design metadata |
| `docs/analysis_corridor_method_note.md` | Current source-vs-analysis graph-scale explanation | method boundary, not final acceptance |
| `scripts/audit_publication_readiness.py` | Aggregated final-study evidence gate | reports current blockers and can fail with `--fail-on-blockers` |
| `scripts/audit_final_study_readiness.py` | Plan-level final-study gate audit | reports blocked final gates across pilot acceptance, graph scale, evidence, validation, experiments, sensitivity, manuscript/report, reproducibility, and final audit |

## Result Manifest

| Artifact | Role | Scope |
| --- | --- | --- |
| `results/realworld_pilot/pilot_sample_results.csv` | Raw pilot scaffold sample rows | not calibrated |
| `results/realworld_pilot/pilot_sample_summary.csv` | Grouped pilot scaffold sample summary | not calibrated |
| `results/realworld_pilot/pilot_sample_manifest.json` | Pilot sample metadata | reproducibility index |
| `results/realworld_pilot/pilot_result_manifest.json` | Legacy pilot sample manifest alias | compatibility index |
| `results/realworld_pilot/pilot_staged_results.csv` | Staged pilot profile rows when `--staged` is run | not calibrated |
| `results/realworld_pilot/pilot_staged_summary.csv` | Staged pilot profile summary when `--staged` is run | not calibrated |
| `results/realworld_pilot/pilot_staged_manifest.json` | Staged pilot profile metadata when `--staged` is run | reproducibility index |
| `results/realworld_pilot/pilot_multi_corridor_results.csv` | Multi-corridor candidate profile rows when `--multi-corridor` is run | graph-scale review evidence, not calibrated |
| `results/realworld_pilot/pilot_multi_corridor_summary.csv` | Multi-corridor candidate profile summary when `--multi-corridor` is run | graph-scale review evidence, not calibrated |
| `results/realworld_pilot/pilot_multi_corridor_manifest.json` | Multi-corridor candidate metadata with 164-node / 246-edge analysis graph counts | reproducibility index, not acceptance |
| `results/realworld_pilot/pilot_multi_corridor_full_results.csv` | Full-profile multi-corridor candidate rows when `--multi-corridor-full` is run | 1,890-row graph-scale review evidence, not calibrated |
| `results/realworld_pilot/pilot_multi_corridor_full_summary.csv` | Full-profile multi-corridor candidate summary when `--multi-corridor-full` is run | 63-row graph-scale review evidence, not calibrated |
| `results/realworld_pilot/pilot_multi_corridor_full_manifest.json` | Full-profile multi-corridor candidate metadata with 164-node / 246-edge analysis graph counts | reproducibility index, not acceptance |
| `results/realworld_pilot/pilot_full_results.csv` | Full pilot profile rows when `--full` is run | not calibrated |
| `results/realworld_pilot/pilot_full_summary.csv` | Full pilot profile summary when `--full` is run | not calibrated |
| `results/realworld_pilot/pilot_full_manifest.json` | Full pilot profile metadata when `--full` is run | reproducibility index |
| `results/realworld_pilot/sensitivity_results.csv` | Deterministic sensitivity screening rows | not formal SALib indices |
| `results/realworld_pilot/sensitivity_summary.csv` | Sensitivity ranking summary | not formal SALib indices |
| `results/realworld_pilot/sensitivity_manifest.json` | Sensitivity metadata and SALib-compatible problem | reproducibility index |
| `results/realworld_pilot/morris_results.csv` | SALib Morris rows for current full policy/scenario scaffold | formal scaffold indices, not calibrated |
| `results/realworld_pilot/tables/pilot_full_metric_ci.csv` | Seed-replication metric confidence intervals for the full pilot scaffold | uncertainty summary, not calibration |
| `results/realworld_pilot/tables/pilot_full_paired_delta_ci.csv` | Paired comparison-policy minus bus-only confidence intervals by scenario and metric | paired uncertainty summary, not calibration |
| `results/realworld_pilot/tables/pilot_full_statistics_manifest.json` | Statistics table provenance and claim boundary | reproducibility index, not acceptance |
| `results/realworld_pilot/tables/pilot_multi_corridor_metric_ci.csv` | Seed-replication metric confidence intervals for the multi-corridor candidate | graph-scale review uncertainty summary, not calibration |
| `results/realworld_pilot/tables/pilot_multi_corridor_paired_delta_ci.csv` | Paired policy-delta confidence intervals for the multi-corridor candidate | graph-scale review uncertainty summary, not calibration |
| `results/realworld_pilot/tables/pilot_multi_corridor_statistics_manifest.json` | Multi-corridor statistics provenance and claim boundary | reproducibility index, not acceptance |
| `results/realworld_pilot/tables/pilot_multi_corridor_full_metric_ci.csv` | Seed-replication metric confidence intervals for the full-profile multi-corridor candidate | graph-scale review uncertainty summary, not calibration |
| `results/realworld_pilot/tables/pilot_multi_corridor_full_paired_delta_ci.csv` | Paired policy-delta confidence intervals for the full-profile multi-corridor candidate | graph-scale review uncertainty summary, not calibration |
| `results/realworld_pilot/tables/pilot_multi_corridor_full_statistics_manifest.json` | Full-profile multi-corridor statistics provenance and claim boundary | reproducibility index, not acceptance |
| `results/realworld_pilot/morris_summary.csv` | SALib Morris ranking summary for current full policy/scenario scaffold | formal scaffold indices, not calibrated |
| `results/realworld_pilot/morris_manifest.json` | SALib Morris metadata and problem frame | reproducibility index |
| `scripts/audit_sensitivity_diagnostics.py` | Morris output diagnostic audit | flags index review items but does not accept sensitivity evidence |
| `scripts/write_sensitivity_review_packet.py` | Sensitivity review packet generator | review support only, not sensitivity acceptance or Sobol waiver |
| `scripts/write_validation_review_packet.py` | Validation review packet generator | review support only, not validation acceptance or benchmark-strategy approval |
| `scripts/write_reproducibility_review_packet.py` | Reproducibility review packet generator | review support only, not clean-checkout acceptance |
| `scripts/run_reproducibility_smoke.py` | Current-worktree reproducibility smoke runner | bounded execution evidence only, not clean-checkout acceptance |
| `scripts/run_clean_checkout_smoke.py` | Bounded clean source-checkout smoke runner | clones the committed source tree and runs a minimal smoke profile; not full clean-environment acceptance |
| `scripts/write_osrm_snapshot_manifest.py` | OSRM snapshot manifest generator | records CSV, summary, query URL, source-status, and optional raw-payload inventory; review support only, not validation acceptance |
| `scripts/write_route_road_evidence_exposure.py` | Route road-evidence exposure generator | review support only, not road calibration or validation acceptance |
| `scripts/audit_road_evidence_diagnostics.py` | Road-class evidence diagnostic audit | ranks current cached OSM road classes for speed/capacity/disruption review |
| `scripts/write_road_speed_evidence.py` | Cached OSM maxspeed candidate table generator | review support only, not accepted road-speed calibration |
| `scripts/write_road_capacity_evidence.py` | Cached OSM lane-count capacity candidate table generator | review support only, not accepted capacity calibration |
| `scripts/write_road_evidence_review_packet.py` | Road-input evidence review packet generator | review support only, not accepted road calibration |
| `scripts/write_road_evidence_source_request_packet.py` | Road evidence source-request packet generator | request support only, not accepted road calibration |
| `scripts/write_rail_evidence_review_packet.py` | Rail evidence review packet generator | review support only, not accepted rail-service timing evidence |
| `scripts/write_rail_timing_source_request_packet.py` | Rail timing source-request generator | request support only, not cached timing evidence |
| `scripts/write_parameter_review_packet.py` | Core-parameter review packet generator | review support only, not accepted parameter calibration |
| `scripts/write_parameter_evidence_source_request_packet.py` | Parameter evidence source-request generator | request support only, not accepted parameter calibration |
| `scripts/run_graph_scale_diagnostics.py` | Full-vs-reduced route parity and alternate-route diagnostic generator | graph-scale review support only |
| `scripts/write_graph_scale_review_packet.py` | Graph-scale method option packet generator | review support only, not graph-scale acceptance |
| `scripts/write_graph_scale_result_comparison.py` | Current-vs-candidate graph-scale result comparison generator | review support only, not graph-scale acceptance |
| `results/realworld_pilot/figures/` | Scaffold-only PNG figures | not publication-grade evidence |
| `results/realworld_pilot/tables/` | Result, Morris sensitivity, bottleneck attribution, policy regime, and claim-boundary tables | scaffold-only |
| `docs/plan_completion_audit.md` | Current gate-by-gate plan audit | scaffold status and blockers, not final acceptance |
| `docs/current_goal_completion_audit.md` | Current active-goal prompt-to-artifact completion gap audit | non-acceptance blocker summary; not `docs/final_study_audit.md` |

All pilot, sensitivity, Morris, and figure/table manifests now expose both
source graph scale and analysis graph scale. This supports reproducibility of
the current reduced-corridor scaffold but does not close graph-scale
acceptance.

## Claim Boundary

Allowed:

- The current code can load a cached pilot graph and run both transport modes.
- The current tables document source classes and assumptions.
- The current parameter audit verifies that core parameters are present and
  identifies which remain weak for final-study claims.
- The current parameter review packet prioritizes weak values for replacement
  or explicit acceptance, but it does not close any evidence gate.
- The current road audit verifies cached-road input coverage and identifies
  free-flow speed, capacity, and disruption-probability proxy dependence.
- The current road diagnostic ranks routeable road classes that should be
  prioritized for reviewed speed, capacity, and disruption evidence.
- The current OSM `maxspeed` candidate table exposes sparse observed speed tags
  by routeable road class. It helps prioritize speed review but does not create
  accepted speed overrides.
- The current OSM `lanes` capacity-candidate table records that no routeable
  road class has parseable lane observations in the cache. It keeps capacity
  fallback dependence visible.
- The current scenario and policy tables are deterministic and reproducible.
- The current sample outputs verify the end-to-end pipeline.
- The staged and full profile metadata identify intended scenario, policy, and
  seed matrices before those outputs are accepted.
- The optional OSRM snapshot provides route-plausibility evidence. The current
  snapshot has 3 pass rows after bus-practical road filtering, and the OSRM
  manifest records 3 cached external-router rows, 0 unpinned rows, 3 retained
  raw response files, query URLs, and checksums. It is not calibration or
  ground truth.
- The graph-scale route parity diagnostic has 3 pass rows for the canonical
  baseline road legs, but it is not final graph-scale acceptance.
- The graph-scale alternate-route diagnostic has 9 rows: 3 rank-1 pass rows
  and 6 alternate-route warning rows, making corridor uncertainty visible
  without accepting the reduced graph as final evidence.
- The multi-corridor candidate diagnostic has 9 pass rows for the same top
  full-graph route candidates, and the separated candidate experiment profile
  now has 32 raw rows plus 16 summary rows on the 164-node / 246-edge graph.
- The full-profile multi-corridor candidate profile now has 1,890 raw rows
  plus 63 summary rows on the same 164-node / 246-edge graph, matching the
  current full-pilot scenario-policy-seed matrix for review.
- The current-vs-candidate graph-scale result comparison has 819 metric-level
  rows and flags same/changed/non-finite differences for reviewer inspection
  before any graph-scale acceptance.
  It still requires graph-scale acceptance before result claims can use it.
- The graph-scale review packet puts the reduced corridor, multi-corridor
  candidate, and full bus-practical graph into one worksheet; it is a review
  aid only and does not choose the final method.

Not allowed:

- The current outputs are calibrated real-world results.
- The current outputs prove operational superiority of any mode.
- The current Morris output is calibrated real-world sensitivity evidence.
- The current Morris output is a Sobol result.
- The current Morris diagnostic audit accepts blank or degenerate index behavior
  for publication claims.
- The sensitivity review packet accepts Morris outputs, waives Sobol analysis,
  or closes `data/manifests/sensitivity_acceptance.json`.
- The current pilot scaffold is an accepted operational Songpa-gu network.
- The current bottleneck attribution proxy is causal evidence from
  instrumented station, vehicle, or passenger logs.
- The current parameter evidence is publication-ready. It currently reports
  `publication_ready: false`.
- The current road-input evidence is publication-ready. It currently reports
  `publication_ready: false`.
- The current rail station binding does not prove rail service availability,
  station-to-station route choice, headway, travel time, or capacity. It only
  reports `binding_ready: true` for official station identifiers.
- The current rail evidence review packet does not derive or accept rail timing
  evidence. It currently reports `publication_ready: false`.
- The current rail timing source-request packet does not contain source
  observations. It currently reports `publication_ready: false`.
- The current aggregated publication-readiness audit passes final-study gates.
  It currently reports `publication_ready: false`.
- The current plan-level final-study readiness audit passes all gates. It
  currently reports `final_study_ready: false`.

## Remaining Reproducibility Upgrades

- Review or replace the current OSM-derived cache as an accepted pilot snapshot.
- Add `data/manifests/provenance_acceptance.json` only after source snapshots,
  license/attribution, privacy abstraction, cache manifests, reproduction
  paths, and not-operational claim boundaries are reviewed.
- Record a real pilot acceptance decision in `data/manifests/pilot_acceptance.json`
  only after privacy, graph-scale, evidence, and claim-boundary review.
- Add a reviewed GTFS feed, public timetable, shortest-path extract, or
  equivalent timing evidence for rail assumptions.
- Use `scripts/write_rail_evidence_review_packet.py` to keep the rail timing,
  capacity, service-window, availability, and derivation-path gaps visible
  until reviewed cached rail evidence replaces proxy timing values.
- Use `scripts/write_rail_timing_source_request_packet.py` to preserve the
  exact required rail timing source inputs before requesting API keys or
  reviewed GTFS files.
- Keep official station identifiers separate from rail service evidence; the
  next rail blocker is cached timetable, shortest-path, GTFS, or equivalent
  timing evidence. The shortest-path path can close travel-time evidence only;
  headway still needs timetable, GTFS, or equivalent service-frequency support.
- Use `scripts/fetch_rail_shortest_path_cache.py` only when a reviewed
  data.go.kr API key, station names, station codes, extraction date, and raw
  response retention plan are available.
- Replace weak road, fleet, transfer, disruption, demand/time, and censoring
  assumptions with source-backed, benchmark-supported, or explicitly accepted
  values where the final claim requires them.
- Use `scripts/audit_road_evidence_diagnostics.py` to prioritize routeable road
  classes before creating reviewed road-class override evidence.
- Use `scripts/write_road_speed_evidence.py` to inspect sparse OSM `maxspeed`
  evidence before deciding whether candidate speeds are strong enough for a
  reviewed override table.
- Use `scripts/write_road_capacity_evidence.py` to verify whether the current
  cache has enough lane-count evidence before accepting any capacity override.
- Use `scripts/write_road_evidence_review_packet.py` to consolidate speed,
  capacity, disruption, and draft-override gaps before replacing or accepting
  weak road-class inputs.
- Use `scripts/write_road_evidence_source_request_packet.py` before collecting
  source-backed road speed, capacity, benchmark, disruption, or
  override-application inputs.
- Use `scripts/write_parameter_review_packet.py` to regenerate the weak-core
  parameter worksheet before replacing or explicitly accepting retained
  assumptions.
- Use `scripts/write_parameter_evidence_source_request_packet.py` before
  collecting cross-cutting demand, fleet, dispatch, transfer, disruption, or
  traffic/BPR evidence.
- Add `data/parameters/parameter_acceptance.csv` only for weak assumptions that
  reviewers deliberately retain after sensitivity and claim-boundary review.
- Decide whether the current optional OSRM snapshot is enough for the
  publication schedule or whether another cached benchmark from Valhalla,
  routingpy, R5/OpenTripPlanner, UXsim, or an equivalent tool is needed.
- Review `data/validation/osrm_route_benchmark_manifest.json`, including raw
  response retention status, before using optional OSRM rows in any
  validation-acceptance decision.
- Use `data/validation/validation_review_packet.csv` as the worksheet for
  internal plausibility warnings, fallback benchmark warnings, optional OSRM
  snapshot review, accessibility-loss coverage, route-level road-evidence
  exposure, and benchmark-strategy choice.
- Add `data/manifests/validation_acceptance.json` only after the benchmark
  strategy, validation scope, and not-ground-truth limitation are reviewed.
- Add `data/manifests/sensitivity_acceptance.json` only after the Morris/Sobol
  method, parameter ranges, graph scope, NaN/masked-value behavior, and Sobol
  requirement decision are reviewed.
- Use `data/validation/sensitivity_review_packet.csv` as the worksheet for that
  review; do not treat the packet itself as acceptance evidence.
- Add `data/manifests/experiment_acceptance.json` only after graph scope,
  input validation, scenario-policy-seed design, CRN pairing, output counts,
  and the not-operational claim boundary are reviewed.
- Review the staged/full pilot profiles with stronger input validation and
  choose an accepted graph-scale method: corridor abstraction, full-graph
  runtime, or multi-corridor ensemble.
- Use the route-parity and alternate-route diagnostics as review support only;
  decide whether the 6 warning rows are acceptable under a documented
  corridor-selection rule, regenerate on the 164-node / 246-edge
  multi-corridor candidate graph, or add full-graph runtime evidence before
  graph-scale acceptance.
- Use `data/validation/graph_scale_review_packet.csv` to compare the three
  graph-scale options before recording any graph-scale acceptance decision.
- Add `data/manifests/graph_scale_acceptance.json` only after that graph-scale
  method is reviewed, source and analysis graph counts are confirmed, and the
  not-operational claim boundary is accepted.
- Add Sobol analysis only if compute budget and experimental design justify it.
- Regenerate manuscript/report figures only after accepted pilot outputs exist.
- Add `data/manifests/manuscript_acceptance.json` only after the English
  manuscript, Korean report source, regenerated docx, figures/tables,
  evidence gates, result claims, and not-operational claim boundaries are
  reviewed.
- Add `data/manifests/reproducibility_acceptance.json` only after
  clean-checkout validation, the validation ladder, artifact regeneration,
  manifest paths, runtime import boundaries, validation command count, and
  not-operational claim boundaries are reviewed.
- Use `data/validation/reproducibility_review_packet.csv` first to inspect
  scaffold scope, dirty or untracked worktree state, runtime import boundaries,
  and whether a true clean-checkout execution log exists.
- Use `data/validation/clean_checkout_reproducibility_smoke_manifest.json` and
  `data/validation/clean_checkout_reproducibility_smoke_log.jsonl` as bounded
  clean source-checkout smoke evidence. They show that the committed source
  tree can be cloned and a minimal evidence profile can pass, but they do not
  prove dependency reinstall, full validation-ladder execution, artifact
  regeneration, or final reproducibility acceptance.
- Use `data/validation/reproducibility_smoke_manifest.json` and
  `data/validation/reproducibility_smoke_log.jsonl` as current-worktree smoke
  evidence only. They can help reviewers inspect the command ladder, but they
  do not replace a fresh-clone or clean-checkout reproduction.
- Add `data/manifests/final_audit_acceptance.json` only after an independent
  prompt-to-artifact audit verifies every pre-final gate and rejects proxy-only
  completion evidence.
