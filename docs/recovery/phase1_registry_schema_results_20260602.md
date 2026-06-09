# Phase 1 Registry Schema Results - 2026-06-02

## Scope

This record captures the first Phase 1 implementation step from `plan.md`.
The work keeps the root repository as the authoritative simulation core and
does not create final acceptance artifacts.

## Sub-Agent Review Inputs

Three read-only GPT-5.5 xhigh explorer agents reviewed:

- region schema and registry files;
- scenario/config/profile files;
- provenance and formal-acceptance separation.

The main implementation kept the scope to backward-compatible schema and
traceability improvements.

## Changes

### Region Registry

- Added boundary support for `type: polygon` with a required `polygon_path`.
- Polygon support currently stores the polygon artifact path and bbox envelope;
  it does not yet perform polygon geometry containment validation.
- Added `RegionSpec.label` as an alias for `name`.
- Added `origin_zones` input/property alias while preserving
  `assembly_zones`.
- Added top-level `sensitivity_level` with fallback from
  `metadata.data_sensitivity`.
- Added structured `SourceRefSpec` records and `RegionSpec.source_refs`.
- Updated `data/regions/pilot_region.yaml` with explicit sensitivity and
  source-reference rows.

### Scenario/Profile Registry

- Added profile reference IDs to `PilotExperimentProfile`:
  `demand_profile_id`, `fleet_profile_id`, `rail_service_profile_id`,
  `validation_profile_id`, and `road_network_profile_id`.
- Added these IDs to `data/manifests/pilot_experiment_design.json`.
- Added a `profile_refs` block to generated pilot result manifests.
- Added `disruption_mode` to pilot result and summary rows while preserving
  the existing `scenario_type` column for compatibility.
- Fixed `_case_from_scenario()` so scenario `p_fail_scale` is preserved instead
  of being overwritten to `1.0`.

### Provenance Review Hygiene

- Added a source-provenance test confirming that current region and scenario
  registry artifacts are covered by review-aid records.
- No `data/manifests/provenance_acceptance.json` or other formal acceptance
  target was created.

## Commands Run

```powershell
.\.venv\Scripts\python tests\test_realworld_types.py
.\.venv\Scripts\python tests\test_realworld_pilot_experiments.py
.\.venv\Scripts\python tests\test_realworld_source_provenance.py
.\.venv\Scripts\python tests\test_config.py
.\.venv\Scripts\python tests\test_scenario.py
.\.venv\Scripts\python main.py --test
.\.venv\Scripts\python tests\test_realworld_disruption_scenarios.py
.\.venv\Scripts\python tests\test_realworld_policy_alternatives.py
.\.venv\Scripts\python tests\test_realworld_source_license_review_packet.py
.\.venv\Scripts\python tests\test_realworld_validation.py
```

All listed commands passed in the current environment.

## Remaining Phase 1 Work

- Add a dedicated scenario package or experiment-context registry if the next
  phase needs cross-table ID validation.
- Add a formal rail service profile converter only after the first real-road
  Phase 2 graph snapshot requirements are frozen.
- Keep provenance rows as review aids until human/source-backed review closes
  the formal provenance gate.
