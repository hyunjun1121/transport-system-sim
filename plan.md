# Unit 1: Disruption Scenario Manifest — Detailed Plan

Parent: `high_level_plan.md` Phase U. This is a decision-support
simulation project; outputs are not operational route plans. Sub-Agent
architecture (Builder / Reviewer / Verifier) inherited from Phase T.

## Mission

Close the `structured_disruptions` closeout gate by regenerating
`data/scenarios/disruption_scenarios_manifest.json` so it matches the
current `data/scenarios/disruption_scenarios.csv`.

## Root Cause (Confirmed)

The gate check in `src/realworld/final_study_readiness.py:2540-2588`
requires:

1. CSV contains families: `random`, `critical_link`, `access_road`,
   `last_mile`, `rail_station_access`, `spatial_hazard_overlay`. STATUS:
   all present (plus extra `rail_service`). PASS.
2. Manifest `row_count == len(csv_rows)`. STATUS: manifest says 11, CSV
   has 22 data rows. FAIL (stale).
3. Manifest `scenario_table_sha256 == file_sha256(csv)`. STATUS:
   `bf18b140...` vs current `f2eef4e4...`. FAIL (stale).
4. Manifest `publication_ready is False`. STATUS: PASS.
5. Manifest `final_study_ready is False`. STATUS: PASS.

Only conditions 2 and 3 fail. The CSV was expanded (11 → 22 rows) after
the manifest was last written; the manifest was never refreshed.

## Steps

### Step 1: Regenerate the manifest

Run with defaults (script reads the canonical CSV and writes the
canonical manifest path):

```
.\.venv\Scripts\python scripts\write_disruption_scenario_manifest.py
```

If the script default paths differ, pass them explicitly:

```
.\.venv\Scripts\python scripts\write_disruption_scenario_manifest.py `
  --scenarios data/scenarios/disruption_scenarios.csv `
  --manifest data/scenarios/disruption_scenarios_manifest.json `
  --include-pilot-edge-map
```

Use `--include-pilot-edge-map` only if the script supports it and the
pilot graph edge checksums add value; otherwise use
`--no-include-pilot-edge-map` to keep the manifest stable across graph
cache changes.

### Step 2: Verify the regenerated manifest

Confirm the new manifest fields:

- `row_count == 22`
- `scenario_table_sha256 == f2eef4e4...` (lowercase, matching
  `file_sha256()` output)
- `publication_ready is False`
- `final_study_ready is False`

Command:

```
$m = Get-Content data\scenarios\disruption_scenarios_manifest.json -Raw | ConvertFrom-Json
$m.row_count; $m.scenario_table_sha256; $m.publication_ready; "publication_ready must be False, not accepted"; $m.final_study_ready; "final_study_ready must be False, not accepted"
```

### Step 3: Confirm the gate is satisfied

Run the closeout completeness audit and confirm `structured_disruptions`
appears in the passing-gate list (expected: 4/15 passing, up from 3/15):

```
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
```

### Step 4: Refresh dirty-worktree classification

The plan_audit test compares the current worktree state against a cached
classification. After regenerating the manifest, refresh it:

```
.\.venv\Scripts\python scripts\write_dirty_worktree_classification.py
```

### Step 5: Run relevant tests

Run the tests most likely to be affected by the manifest change:

```
.\.venv\Scripts\python tests\test_realworld_disruption_scenarios.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
```

All must pass. If a test hardcodes the old row count (11) or old SHA,
update the hardcoded value to match the regenerated manifest — but first
check whether the test reads the live manifest (preferred) versus a
hardcoded literal.

### Step 6: Commit and push

```
git add -A
git commit -m "phase U1: regenerate disruption scenarios manifest, close structured_disruptions gate"
git push
```

## Stop Conditions

- Manifest `row_count == 22` and SHA matches the current CSV.
- `audit_final_study_readiness.py` lists `structured_disruptions` in
  `ready_gate_ids`.
- `test_realworld_disruption_scenarios.py`,
  `test_realworld_plan_audit.py`, and
  `test_realworld_final_study_readiness.py` pass.
- Claim guard remains clean (no new blocking findings).
- `final_study_ready` is still false (other gates remain blocked).

## Risks

- The script may write additional fields or docs that shift other
  audits. If so, refresh the affected review packets.
- If `--include-pilot-edge-map` produces a graph-dependent SHA that
  changes whenever the cache changes, prefer `--no-include-pilot-edge-map`
  for stability unless the gate explicitly requires edge checksums.
- The plan_audit test may fail if the dirty-worktree classification is
  not refreshed after the manifest regeneration.

## Claim Boundary

This unit only regenerates a review-support manifest from an existing
scenario library CSV. It does not create observed disaster data, does
not calibrate disruption probabilities, and does not create formal
acceptance. The manifest remains review support only.
