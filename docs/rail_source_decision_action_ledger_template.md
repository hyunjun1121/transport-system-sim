# Rail Source Decision Action Template

Template only. This CSV is a reviewer worksheet for the optional --action-ledger input. It is not rail timing evidence, not GTFS validation, not rail-service calibration, not emergency rail availability evidence, not publication gate evidence, not study-closeout evidence, and not a formal decision record.

## Verdict

- Template only: `true`
- Ledger compatible: `true`
- Publication gate supported: `false`
- Can mark complete: `false`
- Template rows: 6
- CSV: `data/rail/rail_source_decision_action_ledger_template.csv`

## How To Use

1. Copy the CSV to a reviewer-owned action ledger path.
2. Edit only the columns present in the CSV.
3. Choose exactly one listed `decision_choice` for each `request_id`.
4. Use ISO `YYYY-MM-DD` format for `decision_date` on every non-pending row.
5. For source-backed acquisition choices, set `artifact_sha256s` as semicolon-separated `path=64hex_sha256` entries for every retained `source_cache_path` and `raw_payload_path` artifact.
6. Run `scripts/write_rail_source_decision_packet.py --action-ledger <edited_csv>`.
7. Rerun publication-gate and study-closeout gate audits.

## Non-Formal Example Rows

These examples are guidance for a copied, reviewer-owned action ledger.
Do not paste them into the generated template unless a reviewer has made
the corresponding bounded-treatment decision.

| request_id | example_decision_choice | required reviewer additions |
| --- | --- | --- |
| rail_capacity_treatment_request | retain_capacity_as_sensitivity_only_with_bounds | reviewer, decision_date, decision_basis, excluded_or_retained_claim_scope, not_operational_claim_boundary, bounded_treatment_or_exclusion_rationale |
| rail_availability_scenario_request | record_scenario_only_availability_scope | reviewer, decision_date, decision_basis, excluded_or_retained_claim_scope, not_operational_claim_boundary, bounded_treatment_or_exclusion_rationale |

Source-backed acquisition examples are intentionally omitted here because
they require retained local source artifacts and `path=64hex_sha256`
entries for every required cache/raw payload before the action row can
be complete.

## Decision Context

| Request | Topic | Current Status | Options | Required Evidence Or Scope |
| --- | --- | --- | --- | --- |
| rail_shortest_path_travel_time_request | Reviewed API cache, live fetch, or alternate rail timing source | blocked_missing_rail_source_decision | provide_reviewed_cached_api_payload; run_reviewed_live_api_fetch_and_cache_raw_payload; use_reviewed_gtfs_or_alternate_timing_source; retain_current_timing_assumption_as_sensitivity_only; exclude_timing_dependent_release_scope_claims | provide reviewed API cache or run reviewed live fetch; retain raw payload, cache file, source citation, extraction date, station binding, and license/provenance review |
| rail_static_gtfs_timing_request | Reviewed static GTFS acquisition and derivation decision | blocked_missing_rail_source_decision | provide_reviewed_static_gtfs_feed; pair_reviewed_timetable_headway_with_shortest_path_travel_time; use_other_reviewed_transit_timing_source; retain_current_timing_assumption_as_sensitivity_only; exclude_timing_dependent_release_scope_claims | provide reviewed static GTFS zip or directory plus retained GTFS Validator report, reviewed stop/route/service-window choices, source citation, extraction date, and license/provenance review |
| rail_timetable_headway_request | Reviewed API cache, live fetch, or alternate rail timing source | blocked_missing_rail_source_decision | provide_reviewed_cached_api_payload; run_reviewed_live_api_fetch_and_cache_raw_payload; use_reviewed_gtfs_or_alternate_timing_source; retain_current_timing_assumption_as_sensitivity_only; exclude_timing_dependent_release_scope_claims | provide reviewed API cache or run reviewed live fetch; retain raw payload, cache file, source citation, extraction date, station binding, and license/provenance review |
| rail_availability_scenario_request | Rail availability source or scenario treatment | needs_human_review_rail_source_decision | replace_with_public_disruption_or_incident_source; record_scenario_only_availability_scope; retain_availability_as_sensitivity_only; exclude_availability_dependent_release_scope_claims | provide public disruption/availability source, or record reviewed scenario-only rail availability bounds and excluded claim scope |
| rail_capacity_treatment_request | Rail capacity source or sensitivity-only treatment | needs_human_review_rail_source_decision | replace_with_operator_or_literature_capacity_source; retain_capacity_as_sensitivity_only_with_bounds; exclude_capacity_dependent_release_scope_claims | provide operator or literature capacity evidence, or record reviewed sensitivity-only capacity bounds with source and scope |
| rail_static_timetable_csv_headway_request | Reviewed static timetable CSV normalization and derivation decision | needs_human_review_ready_rail_source_decision | provide_reviewed_static_timetable_csv_and_mapping; pair_reviewed_static_timetable_headway_with_shortest_path_travel_time; use_reviewed_gtfs_or_alternate_timing_source; retain_current_timing_assumption_as_sensitivity_only; exclude_timing_dependent_release_scope_claims | provide reviewed static timetable CSV, explicit source-column mapping, retained normalization manifest, reviewed station/line/direction/service-day/service-window choices, source citation, extraction date, and license/provenance review |

## Boundary

- This template is not a formal decision record.
- It does not fetch data, validate GTFS, derive rail service evidence, or certify rail availability.
- Acquisition choices remain incomplete unless all listed local source/cache/raw artifacts exist and their SHA256 values match the action ledger.
- Completed non-formal source decisions must still be checked by rail evidence, publication-gate, study-closeout, and formal-decision gates.
