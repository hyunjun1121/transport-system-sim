# Unit 5: Rail GTFS Derivation Attempt

## Mission

Document that GTFS-derived rail timing evidence cannot be produced from the
current cached KTDB source. The KTDB extract is a metadata-only CSV, not a
GTFS feed (no stops.txt, trips.txt, stop_times.txt). Attempt the derivation
script to confirm the failure mode, then record the attempt result so the
rail fetch preflight packet and source decision packet reflect a documented
"GTFS attempted, feed absent" state.

## Claim Boundary

This is a decision-support simulation pipeline. GTFS derivation is attempted
on cached metadata only; no live API calls, no fabricated GTFS rows, no rail
timing evidence creation. The attempt record is documentation only and does
not close the rail evidence gate or any study-closeout gate.

## Context

- Cached KTDB source: `data/rail/ktdb_gtfs_source_extract.csv` (1 row,
  metadata-only, review_status=`cached_ktdb_metadata_pending_review`).
- Derivation script: `scripts/derive_rail_gtfs_evidence.py` requires a GTFS
  zip or directory with `stops.txt`, `trips.txt`, `stop_times.txt`.
- Rail fetch preflight row 5 (`rail_static_gtfs_timing_request`) already
  shows `readiness_status=blocked_missing_reviewed_gtfs_file`.

## Steps

### Step 1: Attempt derivation against cached metadata

Run `derive_rail_gtfs_evidence.py --input data/rail/ktdb_gtfs_source_extract.csv`.
Expect ValueError (not a GTFS zip or directory). Capture the error message.

### Step 2: Record GTFS attempt result in an audit manifest

Write `scripts/record_gtfs_derivation_attempt.py` that:
- Loads the cached KTDB extract path.
- Attempts `load_cached_gtfs_feed()`.
- Records the result in `data/rail/gtfs_derivation_attempt_manifest.json`
  with: input_path, input_sha256, input_is_gtfs_feed (false),
  gtfs_feed_files_present ([]), failure_reason, conclusion, claim_boundary.
- conclusion: "GTFS derivation attempted; cached KTDB extract is metadata
  only, not a GTFS feed; rail timing evidence via GTFS remains blocked".

### Step 3: Regenerate rail fetch preflight packet

Re-run `write_rail_fetch_readiness_packet.py` to confirm the packet still
reflects `blocked_missing_reviewed_gtfs_file` with row 5 intact.

### Step 4: Add tests for the attempt manifest

Write `tests/test_realworld_gtfs_derivation_attempt.py` that:
- Asserts the shipped manifest records `input_is_gtfs_feed=false`.
- Asserts `gtfs_feed_files_present=[]`.
- Asserts the conclusion contains "metadata only" and "not a GTFS feed".
- Asserts the manifest SHA256 matches the current cached extract.
- Asserts a directory with all required GTFS files is classified as a feed.

## Stop Conditions

1. GTFS derivation attempt executed and failure captured.
2. Attempt manifest written with honest "feed absent" conclusion.
3. Rail fetch preflight packet still shows blocked GTFS row.
4. Claim guard clean, affected tests pass.

## Sub-Agent Review Plan

After execution, spawn a read-only reviewer to confirm:
- The attempt manifest honestly records the failure mode.
- No evidence is fabricated or overclaimed.
- The fetch preflight packet remains correctly blocked.
