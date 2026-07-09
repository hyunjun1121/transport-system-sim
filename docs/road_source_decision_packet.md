# Road Source Decision Packet

Road source-decision packet only; not road evidence, not road-input tuning evidence, not reviewed road-class override approval, not cached OSM input gate closure, and not publication approval. It cannot create data/parameters/road_class_overrides.csv.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Road-class overrides present: `true`
- Decision rows: 5
- Blocking decisions: 0
- Human-review decisions: 5

## Decision Rows

| Request | Status | Options | Target | Required Action |
| --- | --- | --- | --- | --- |
| reviewed_road_class_override_application_request | needs_human_review_road_source_decision | create_reviewed_road_class_overrides; rerun_pilot_with_reviewed_overrides; retain_current_mapper_defaults_as_sensitivity_only; exclude_road_input_tuning_release_scope_claims | data/parameters/road_class_overrides.csv; results/realworld_pilot/pilot_full_manifest.json | Choose whether to replace with source-backed road evidence, create reviewed road-class overrides, retain the value as sensitivity-only or benchmark-only, or exclude the affected claim from study-scope interpretation. |
| road_background_traffic_benchmark_request | needs_human_review_road_source_decision | keep_benchmark_as_plausibility_only; use_benchmark_bounded_background_traffic_with_limits; collect_observed_traffic_source; retain_background_traffic_as_sensitivity_only | data/parameters/parameter_sources.csv | Choose whether to replace with source-backed road evidence, create reviewed road-class overrides, retain the value as sensitivity-only or benchmark-only, or exclude the affected claim from study-scope interpretation. |
| road_capacity_lane_count_source_request | needs_human_review_road_source_decision | replace_with_traffic_count_or_capacity_reference; create_reviewed_capacity_override_assumption; retain_capacity_as_sensitivity_only; exclude_capacity_dependent_release_scope_claims | data/parameters/road_class_overrides.csv | Choose whether to replace with source-backed road evidence, create reviewed road-class overrides, retain the value as sensitivity-only or benchmark-only, or exclude the affected claim from study-scope interpretation. |
| road_disruption_probability_source_request | needs_human_review_road_source_decision | replace_with_hazard_or_incident_source; record_scenario_only_disruption_with_scope; retain_disruption_as_sensitivity_only; exclude_disruption_probability_release_scope_claims | data/parameters/road_class_overrides.csv | Choose whether to replace with source-backed road evidence, create reviewed road-class overrides, retain the value as sensitivity-only or benchmark-only, or exclude the affected claim from study-scope interpretation. |
| road_speed_limit_source_request | needs_human_review_road_source_decision | replace_with_source_backed_speed_values; record_fallback_speed_assumption_with_scope; retain_speed_as_sensitivity_only; exclude_speed_dependent_release_scope_claims | data/parameters/road_class_overrides.csv | Choose whether to replace with source-backed road evidence, create reviewed road-class overrides, retain the value as sensitivity-only or benchmark-only, or exclude the affected claim from study-scope interpretation. |

## Boundary

- This packet is a reviewer worksheet, not a formal decision record.
- It does not create reviewed overrides, apply overrides, tune road inputs, or record cached OSM input claims.
- Keep road and cached-input claims blocked until source-backed changes or formal reviewer decisions exist.
