# Unit 7: Parameter Evidence Priority Refresh

## Mission

Update `parameter_sources.csv` to reflect derived rail evidence (U3/U4) and
refined road evidence (U6). Then regenerate the full parameter packet chain so
the priority worksheet statuses reflect the strongest available evidence.

## Claim Boundary

This is a decision-support simulation pipeline. No simulation values change
(config stays at 10 min headway, 500 pax capacity). The parameter_sources.csv
adds evidence rows documenting derived values alongside simulation defaults.
No gate closes, no calibration claim, no acceptance artifact created.

## Context

Current parameter_sources.csv (31 rows) has rail parameters as expert
assumption. After U3/U4:
- rail_headway: 3.583 min derived from KTDB GTFS timetable
  (rail_service_evidence.csv row 2, source_artifact_sha256 verified)
- rail_capacity: 922 pax from Metro9 operator page
  (rail_service_evidence.csv row 3, source_artifact_sha256 verified)
- rail_travel_time: still assumption (GTFS derivation attempted in U5,
  feed was not a real GTFS feed)

After U6:
- road_free_flow_speed: 5/10 highway classes have observed OSM maxspeed
  tags; draft override template marks them public-data-derived but the
  override is not applied (simulation uses mapper defaults).

The parameter audit (`audit_parameter_evidence.py`) reads
parameter_sources.csv and picks the strongest source_class per parameter
when multiple rows exist.

## Steps

### Step 1: Update parameter_sources.csv

Add derived evidence rows:
- rail_headway: 3.583 min, agency/timetable-derived, KTDB GTFS
- rail_capacity: 922 pax, public-data-derived, Metro9 operator page

Update notes for:
- rail_travel_time: mention GTFS derivation attempted, no real feed found
- road_free_flow_speed: mention 5/10 classes have observed maxspeed

### Step 2: Regenerate parameter packet chain

1. audit_parameter_evidence.py
2. write_parameter_review_packet.py
3. write_parameter_evidence_source_request_packet.py
4. write_parameter_source_readiness_packet.py
5. write_parameter_evidence_priority_packet.py

### Step 3: Verify audit + tests

Run parameter audit, plan audit, publication gate check, study-closeout
gate check, parameter review packet tests. Confirm rail_headway and
rail_capacity are now source-backed in the audit.

## Stop Conditions

1. parameter_sources.csv has derived rail evidence rows.
2. Parameter audit shows rail_headway and rail_capacity as source-backed.
3. Priority packet regenerated with updated statuses.
4. Claim guard clean, affected tests pass.

## Sub-Agent Review Plan

After execution, spawn a read-only reviewer to confirm:
- Derived rail values match rail_service_evidence.csv.
- Simulation config values unchanged.
- road_free_flow_speed stays expert assumption (draft not applied).
- No gate closes or overclaims.
