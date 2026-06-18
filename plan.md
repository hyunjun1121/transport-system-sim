# Unit 6: Road Override Candidate Refinement

## Mission

Update `road_class_overrides_draft.csv` to classify the 5 highway classes with
observed OSM maxspeed tags as `speed_source_class=public-data-derived`. The
remaining 5 classes (no observed tags) stay as `expert assumption`. Do NOT
create `road_class_overrides.csv` (human signoff).

## Claim Boundary

This is a decision-support simulation pipeline. The draft CSV remains a
reviewer worksheet. No speed value changes (mapper defaults retained); only
the speed source classification changes for observed classes. No gate closes.

## Context

Speed evidence candidates table (`road_speed_evidence_candidates.csv`):
- 5 classes with observed OSM maxspeed tags (`maxspeed_observed_count > 0`):
  residential, tertiary, secondary, primary, trunk
- 5 classes without: trunk_link, primary_link, secondary_link, unclassified,
  tertiary_link

Draft CSV is loaded via `load_road_class_overrides` so `speed_source_class`
must be in `ALLOWED_SOURCE_CLASSES`. Use `public-data-derived` (not
`observed_osm_tag` which is not an allowed value).

Row-level `source_class` stays `expert assumption` for all 10 rows because
capacity and base_p_fail are still assumptions.

## Steps

### Step 1: Modify `_template_row` in `road_override_template.py`

Add logic: if `maxspeed_parseable_rate > 0`, set speed field source to
`public-data-derived` with name/citation pointing to the speed evidence
candidates table. Otherwise keep `expert assumption`.

### Step 2: Regenerate draft CSV

Run `write_road_class_override_template.py --overwrite`.

### Step 3: Verify audit + tests

Run road override audit, template tests, plan audit, road evidence tests.
Confirm 5 rows now have `speed_source_class=public-data-derived` and 5 have
`expert assumption`.

## Stop Conditions

1. 5/10 rows classified `speed_source_class=public-data-derived`.
2. 5/10 rows remain `speed_source_class=expert assumption`.
3. Row-level `source_class` stays `expert assumption` for all 10.
4. Claim guard clean, affected tests pass.

## Sub-Agent Review Plan

After execution, spawn a read-only reviewer to confirm:
- The 5 observed classes match the speed evidence candidates table.
- No speed values were changed (mapper defaults retained).
- Row-level source_class stays expert assumption for all 10 rows.
- No gate closes or overclaims.
