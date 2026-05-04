# Road Evidence Diagnostics

`scripts/audit_road_evidence_diagnostics.py` summarizes the cached
OSM/GraphML road graph by normalized highway class. It is a review aid for the
road-input evidence gate, not an acceptance record.

## What It Checks

- Cached GraphML presence and routeable road-edge availability.
- Edge counts, parseable length coverage, and total length by road class.
- Bus-practical routeable length by road class, used to rank review priority.
- OSM `maxspeed` coverage by road class.
- Explicit road-capacity coverage by road class.
- Explicit base-disruption probability coverage by road class.
- Dominant source tag and high-impact road classes that should be reviewed
  first.

## Current Interpretation

The current pilot cache is structurally diagnosable, but it is not
publication-ready road evidence. Length coverage is complete, while most
free-flow speed values still rely on road-class fallbacks, road capacity is a
built-in proxy, and base-disruption probability is a scenario proxy.

The current high-priority review classes are based on routeable length, so
pedestrian, cycle, path, and service edges do not dominate the road-calibration
priority merely because they exist in the raw OSM snapshot.

`data/parameters/road_class_overrides_draft.csv` has been generated from the
current diagnostics as a reviewer worksheet. It contains 10 routeable road-class
rows and all rows are still labeled `expert assumption`, so it is not reviewed
road evidence and does not close the road-input gate.

`data/parameters/road_speed_evidence_candidates.csv` has also been generated
from sparse cached OSM `maxspeed` tags. It contains 10 routeable road-class
rows; 5 classes have at least one parseable `maxspeed` observation, while the
remaining rows retain mapper fallback speeds. This table is a review aid for
speed evidence only. It is not a reviewed override table, calibrated traffic
speed evidence, or proof that speed overrides were applied to any result.

`data/parameters/road_capacity_evidence_candidates.csv` has been generated
from cached OSM `lanes` tags and a documented per-lane planning proxy. The
current cache has 10 routeable road-class rows but 0 rows with parseable lane
observations, so all candidate capacities remain mapper fallbacks. This makes
the lane-count evidence gap explicit without accepting those capacities.

## What It Does Not Do

This diagnostic does not create `road_class_overrides.csv`, does not prove that
any override table was applied to a result manifest, does not calibrate BPR
capacity, and does not validate route choice against observed operations. The
speed- and capacity-candidate tables likewise do not replace reviewer
acceptance of source-backed speeds or capacities.

## Command

```powershell
.\.venv\Scripts\python scripts\audit_road_evidence_diagnostics.py
```

Optional structural check:

```powershell
.\.venv\Scripts\python scripts\audit_road_evidence_diagnostics.py --fail-on-structural-blockers
```

The strict flag fails only when the cached graph is missing, empty, or has no
bus-practical routeable edges. Weak speed, capacity, and disruption evidence
remain review items rather than being silently accepted.

Candidate speed-evidence table:

```powershell
.\.venv\Scripts\python scripts\write_road_speed_evidence.py
```

Candidate capacity-evidence table:

```powershell
.\.venv\Scripts\python scripts\write_road_capacity_evidence.py
```
