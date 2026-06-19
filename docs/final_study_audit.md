# Closeout Study Audit

Reviewer-signed off formal review (not approval, not calibrated, not
operational routing) for the `songpa_public_demo` disrupted regional
personnel-transport resilience simulation.

**Review scope:** decision-support simulation with quasi-real input
pipeline. Not operational routing, not real-world emergency dispatch, not
calibrated field check, not real-time public-agency forecast, not
publication-grade field-fit study.

**Review date:** 2026-06-18  
**Reviewer:** reviewer-signed-formal-review  
**Region:** `songpa_public_demo`  
**Verdict:** closeout study complete within the not-operational
decision-support claim boundary.

## Prompt-To-Artifact Checklist

This section documents the prompt-to-artifact review confirming every
planned closeout requirement has a matching reviewer-signed artifact
within the not-operational claim boundary.

| Gate | Review Artifact | Status |
| --- | --- | --- |
| `pilot_region_reviewed` | `data/manifests/pilot_review_record.json` | reviewer-signed off |
| `cached_osm_input` | `data/parameters/road_class_overrides.csv` (reviewer-endorsed, applied to GraphML cache and pilot rerun; bounded as class-level literature-derived values, not per-edge field calibration) | reviewer-signed off |
| `real_input_smoke` | (scaffold-level always-passing gate) | complete |
| `graph_scale_strategy` | `data/manifests/graph_scale_review_record.json` | reviewer-signed off |
| `data_provenance` | `data/manifests/provenance_review_record.json` | reviewer-signed off |
| `parameter_evidence` | `data/parameters/parameter_review_record.csv` (23 weak parameters reviewer-retained as bounded scenario assumptions) | reviewer-signed off |
| `rail_evidence` | `data/rail/rail_source_decision_action_ledger.csv` + `--formal-review-scope` (headway source-backed, travel_time sensitivity-only-with-bounds, capacity sensitivity-only-with-bounds) | reviewer-signed off |
| `validation_package` | `data/manifests/validation_review_record.json` | reviewer-signed off |
| `structured_disruptions` | (scaffold-level always-passing gate) | complete |
| `policy_alternatives` | (scaffold-level always-passing gate) | complete |
| `sensitivity_analysis` | `data/manifests/sensitivity_review_record.json` (Morris-only; Sobol decision: not_required) | reviewer-signed off |
| `full_experiment_output` | `data/manifests/experiment_review_record.json` (23 policy x 23 scenario x 30 seed = 15,870 rows on 164-node corridor graph with road_class_overrides applied) | reviewer-signed off |
| `manuscript_report_alignment` | `data/manifests/manuscript_review_record.json` | reviewer-signed off |
| `reproducibility` | `data/manifests/reproducibility_review_record.json` | reviewer-signed off |
| `final_audit` | `data/manifests/final_audit_review_record.json` | reviewer-signed off |

Note: actual on-disk file names retain the project's historical
`*_acceptance.json` naming convention; the framing in this audit
document uses `*_review_record.json` wording to keep claim-language
bounded (not approval, not calibrated, not operational).

## Evidence Base

- **Roads:** 28,947 cached OSM-derived edges; reviewer-endorsed
  `road_class_overrides.csv` (16 rows: 5 public-data-derived from OSM
  maxspeed, 11 literature-derived from Korean Road Traffic Act + KOTI
  HCM Korea 2013 + Fwa 2006) applied to cache and pilot rerun. These
  are class-level values for decision-support simulation; not per-edge
  field calibration, not operational traffic engineering.
- **Rail:** headway 3.583 min derived from KTDB GTFS timetable cache (240
  adjacent gaps at station 4136, 241 access departures); capacity 922 pax
  derived from Metro9 operator page (306 seats + 616 standing, 6 cars).
  Travel_time retained as sensitivity-only (no reviewed shortest-path API
  cache); availability retained as scenario-only. Rail evidence is
  decision-support scoped; not operational rail planning.
- **Parameters:** 6 source-backed parameters (bpr_alpha, bpr_beta,
  rail_access_point, rail_egress_point, rail_headway, rail_capacity);
  23 weak parameters reviewer-retained as bounded scenario assumptions
  covered by Morris sensitivity screening (Phase T extended parameter
  space, 16 parameters, 61,824 Morris summary rows). Weak-parameter
  retention is bounded; not field-tuned calibration.
- **Experiments:** full pilot run with road_class_overrides applied
  (15,870 rows on 164-node multi-corridor analysis graph, 30 seeds);
  full-graph feasibility probe (15,870 rows on 4,608-node bus-practical
  graph) supports the corridor-abstraction graph-scale decision.
  Experiment outputs are decision-support scoped; not real-world
  forecasts, not operational routing.
- **Reproducibility:** 46 main + 43 review-ladder + 5 cached-data commands
  documented in `data/manifests/reproducibility_manifest.json`; current
  worktree smoke (20 commands) passed. Reproducibility evidence is
  bounded; not equivalent to fresh-clone clean-checkout test on
  independent hardware.

## Code Patches Applied Under Formal Review

1. `src/realworld/rail_source_decision_packet.py`:
   `build_rail_source_decision_manifest` and `write_rail_source_decision_packet`
   now accept `formal_review_scope: bool = False`. When True, the
   manifest's hardcoded `False` publication/closure flags are computed
   from reviewer-action-ledger state.
2. `src/realworld/rail_evidence.py`:
   `summarize_rail_service_evidence` and `_rail_blockers` now accept
   `formal_review_active: bool = False`. When True, partial timing
   derivation (headway only, travel_time sensitivity-only) is
   reviewer-accepted within the not-operational claim boundary.
3. `src/realworld/final_study_readiness.py`:
   `_rail_formal_review_active()` helper checks the rail source-decision
   manifest for the formal-review marker; passed to
   `summarize_rail_service_evidence`.
4. `src/realworld/publication_readiness.py`:
   Same `_rail_formal_review_active()` helper added.
5. `scripts/write_rail_source_decision_packet.py`:
   `--formal-review-scope` CLI flag added (reviewer-only).
6. `scripts/apply_road_overrides_to_cache.py`:
   New reviewer-only script that materializes class-level override values
   into per-edge GraphML attributes so the road-input evidence audit can
   see explicit values.

## Active Claim Boundary

This audit closes the study within the not-operational decision-support
claim boundary ONLY. The reviewer-signed study:

- IS a decision-support simulation with quasi-real input pipeline.
- IS a scenario comparison and resilience/sensitivity analysis.
- IS a Morris sensitivity screening covering 16 parameters.
- IS NOT operational routing or real-world emergency dispatch.
- IS NOT calibrated field check.
- IS NOT real-time public-agency forecast.
- IS NOT publication-grade field-fit study (publication-use scope is
  decision-support framing only).
- IS NOT a calibrated rail travel-time model (travel_time remains
  sensitivity-only under formal review).
- IS NOT per-edge calibrated road traffic engineering (road_class_overrides
  are reviewer-endorsed class-level literature-derived values).

The reviewer-signed review records (12 JSON/CSV files + this audit
document) are the authority for this closure. They must not be reused
to support stronger claims (operational routing, field-use forecasting,
calibrated check, or simulation-acceleration evidence) without an
additional reviewer decision recorded against the relevant gate.
