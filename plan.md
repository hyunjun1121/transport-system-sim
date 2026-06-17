# Units 3+4: Rail Headway + Capacity Evidence Derivation

Parent: `high_level_plan.md` Phase U. This is a decision-support simulation
project; outputs are not operational route plans. Sub-Agent architecture
(Builder / Reviewer / Verifier) inherited from Phase T.

## Mission

Unit 3: Derive rail headway from the cached static timetable (241 access
departures at station 4136 / Olympic Park). Write a headway-derived
evidence row with source SHA256 into `data/parameters/rail_service_evidence.csv`.

Unit 4: Derive rail capacity (922 pax / 6 cars) from the cached Metro9
operator-page extract. Create a thin `derive_rail_capacity_evidence.py`
wrapper that reads `metro9_capacity_source_extract.csv`, extracts the
capacity value with source SHA256, and writes a documented-public-source
evidence row.

Both rows are added alongside the existing assumption-proxy row (total
3 rows). Neither row closes the rail evidence gate (travel time still
not derived). Capacity remains sensitivity-only.

## Claim Boundary

These units produce cached-source evidence rows only. They do NOT
create `rail_acceptance.json`, do NOT close the rail evidence gate
(travel_time still missing), and do NOT claim calibrated rail timing or
operational rail capacity. The headway value is derived from an
unreviewed static timetable cache; the capacity value is from an
unreviewed operator web page. Both carry pending-review status.

## Stop Conditions

1. Headway row derived from 241 access departures with correct SHA256.
2. Capacity row written from Metro9 extract with correct SHA256.
3. Evidence CSV schema checks pass (3 rows, 1 derived, 2 assumption/source).
4. Rail evidence audit shows derived_record_count >= 1, headway derived-field satisfied.
5. Rail evidence review packet regenerated; row count stays 12.
6. Affected tests updated and passing.
7. Claim guard: blocking_finding_count=0.
8. Rail evidence gate remains blocked (travel_time not derived).

## Builder Steps

### Step 1: Run headway derivation
```
python scripts/derive_rail_headway_evidence.py \
  --input data/rail/pilot_rail_timetable_cache.csv \
  --output <temp_headway.csv> \
  --evidence-id songpa_public_demo_rail_headway_v1 \
  --egress-station-name "Jamsil Station area" \
  --source-name "KTDB static timetable cache (line 9, station 4136 Olympic Park, UP/DAY)" \
  --source-url-or-citation "data/rail/pilot_rail_timetable_cache.csv; data/rail/pilot_rail_timetable_static_source.csv" \
  --extraction-date 2026-05-08 \
  --travel-time-min-proxy 20 \
  --capacity-pax-per-train 922 \
  --service-window "scheduled public service" \
  --direction UP \
  --service-day DAY
```

### Step 2: Create capacity derivation script
Create `scripts/derive_rail_capacity_evidence.py`:
- Reads Metro9 extract CSV
- Extracts total_capacity_6_cars (922)
- Computes source SHA256
- Writes a `documented_public_source_available` evidence row

### Step 3: Merge evidence rows
Write all 3 rows (assumption proxy + headway derived + capacity source)
to `data/parameters/rail_service_evidence.csv` using
`write_rail_service_evidence`.

### Step 4: Regenerate rail evidence review packet
```
python scripts/write_rail_evidence_review_packet.py
```

### Step 5: Update tests
- `test_realworld_rail_evidence.py`: shipped evidence now has 3 rows,
  1 derived, headway evidence strengthened.
- `test_realworld_rail_evidence_review_packet.py`: headway row now
  shows `cached_timing_derived`, `weak_for_final_claim=false`.

### Step 6: Run affected tests + claim guard + commit
