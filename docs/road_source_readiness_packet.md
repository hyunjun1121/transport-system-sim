# Road Source Readiness Packet

Road source-readiness packet only; not reviewed road-class overrides, not calibrated speed or capacity evidence, not accepted disruption evidence, not proof that overrides were applied, and not operational routing evidence. This packet cannot close cached-road, parameter, validation, or formal road acceptance gates.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Request rows: 5
- Blocking requests: 2
- Human-review requests: 3
- Status counts: `{'blocked_missing_capacity_source': 1, 'blocked_missing_reviewed_road_class_overrides': 1, 'needs_human_review_benchmark_strategy': 1, 'needs_human_review_disruption_scenario': 1, 'needs_human_review_sparse_speed_candidates': 1}`

## Readiness Rows

| Request | Source | Source Type | Status | Source Cache | Target | Required Input | Required Action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| road_speed_limit_source_request | Reviewed OSM maxspeed extract, public speed-limit source, or routing benchmark<br>data/parameters/road_speed_evidence_candidates.csv | public_speed_limit_or_benchmark_source_required | needs_human_review_sparse_speed_candidates | present | absent | reviewed speed-limit evidence for high-priority road classes; fallback classes must be explicitly accepted as assumptions | review sparse maxspeed candidates or replace them with public speed-limit or benchmark evidence |
| road_capacity_lane_count_source_request | Reviewed lane counts, traffic counts, or literature/agency capacity reference<br>data/parameters/road_capacity_evidence_candidates.csv | traffic_count_or_capacity_reference_required | blocked_missing_capacity_source | present | absent | reviewed lane-count coverage, traffic counts, agency road-class capacity table, or literature capacity proxy | provide traffic counts, agency capacity references, or reviewed capacity assumptions |
| road_background_traffic_benchmark_request | Reviewed route benchmark or observed traffic-speed source<br>data/validation/external_route_benchmarks.csv; data/validation/validation_summary.md | routing_or_observed_traffic_benchmark_required | needs_human_review_benchmark_strategy | present | present | reviewed OSRM/Valhalla/routingpy/R5/OTP/UXsim benchmark decision, observed speed source, or explicit background-traffic sensitivity treatment | decide whether current route benchmarks are plausibility-only or support a bounded traffic assumption |
| road_disruption_probability_source_request | Reviewed hazard, incident, exposure, or scenario-rule source<br>data/scenarios/disruption_scenarios.csv | hazard_incident_or_reviewed_scenario_source_required | needs_human_review_disruption_scenario | present | absent | public hazard/exposure layer, incident history, literature rule, or explicitly reviewed scenario-only disruption treatment | accept scenario-only disruption treatment or replace it with hazard, incident, or literature evidence |
| reviewed_road_class_override_application_request | Reviewed road_class_overrides.csv plus accepted pilot manifest<br>docs/road_class_override_schema.md | reviewed_override_table_and_manifest_application_required | blocked_missing_reviewed_road_class_overrides | present | absent | reviewed road_class_overrides.csv with strong source classes; rerun pilot outputs with --road-class-overrides-path; reviewer acceptance | create reviewed road_class_overrides.csv after source-backed road evidence review |

## Required Reviewer Actions

- Supply reviewed speed, capacity, disruption, and benchmark evidence or bounded assumptions.
- Move accepted road-class values into `data/parameters/road_class_overrides.csv` only after review.
- Re-run pilot outputs with the reviewed override table before road-calibration claims.
- Do not create formal acceptance artifacts from this readiness packet alone.
