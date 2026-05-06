# Road Source Readiness Packet

> Current project status (2026-05-06): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


Road source-readiness packet only; not reviewed road-class overrides, not calibrated speed or capacity evidence, not accepted disruption evidence, not proof that overrides were applied, and not operational routing evidence. This packet cannot close cached-road, parameter, validation, or formal road acceptance gates.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Request rows: 5
- Blocking requests: 2
- Human-review requests: 3
- Status counts: `{'blocked_missing_capacity_source': 1, 'blocked_missing_reviewed_road_class_overrides': 1, 'needs_human_review_benchmark_strategy': 1, 'needs_human_review_disruption_scenario': 1, 'needs_human_review_sparse_speed_candidates': 1}`

## Readiness Rows

| Request | Source Type | Status | Source Cache | Target | Required Action |
| --- | --- | --- | --- | --- | --- |
| road_speed_limit_source_request | public_speed_limit_or_benchmark_source_required | needs_human_review_sparse_speed_candidates | present | absent | review sparse maxspeed candidates or replace them with public speed-limit or benchmark evidence |
| road_capacity_lane_count_source_request | traffic_count_or_capacity_reference_required | blocked_missing_capacity_source | present | absent | provide traffic counts, agency capacity references, or reviewed capacity assumptions |
| road_background_traffic_benchmark_request | routing_or_observed_traffic_benchmark_required | needs_human_review_benchmark_strategy | present | present | decide whether current route benchmarks are plausibility-only or support a bounded traffic assumption |
| road_disruption_probability_source_request | hazard_incident_or_reviewed_scenario_source_required | needs_human_review_disruption_scenario | present | absent | accept scenario-only disruption treatment or replace it with hazard, incident, or literature evidence |
| reviewed_road_class_override_application_request | reviewed_override_table_and_manifest_application_required | blocked_missing_reviewed_road_class_overrides | present | absent | create reviewed road_class_overrides.csv after source-backed road evidence review |

## Required Reviewer Actions

- Supply reviewed speed, capacity, disruption, and benchmark evidence or bounded assumptions.
- Move accepted road-class values into `data/parameters/road_class_overrides.csv` only after review.
- Re-run pilot outputs with the reviewed override table before road-calibration claims.
- Do not create formal acceptance artifacts from this readiness packet alone.
