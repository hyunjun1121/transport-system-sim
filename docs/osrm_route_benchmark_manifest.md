# OSRM Route Benchmark Manifest

`data/validation/osrm_route_benchmark_manifest.json` describes the optional
OSRM route benchmark CSV that is already cached in `data/validation/`.

This manifest is review support only. It is not validation acceptance, not
ground truth, not calibrated local traffic evidence, and not operational
routing guidance.

## Artifacts

| Artifact | Role | Scope |
| --- | --- | --- |
| `data/validation/external_route_benchmarks_osrm.csv` | Optional OSRM route-distance and travel-time comparison rows | plausibility review only |
| `data/validation/osrm_route_benchmark_summary.md` | Human-readable OSRM benchmark summary | plausibility review only |
| `data/validation/osrm_route_benchmark_manifest.json` | CSV checksum, query URLs, source classes, row counts, and claim boundary | non-acceptance provenance |
| `scripts/write_osrm_snapshot_manifest.py` | Regenerates the manifest from cached CSV and summary artifacts | deterministic offline command |
| `scripts/run_osrm_route_benchmark.py` | Optional live OSRM query path that also rewrites the manifest | explicit live command only |

## Current Interpretation

The current OSRM CSV has three pass rows after bus-practical road filtering.
Those rows remain marked as a live, unpinned external-router snapshot. The
manifest records that status and keeps the validation review packet blocked
from treating OSRM as accepted benchmark evidence.

Use this manifest to review whether the current OSRM snapshot is sufficient for
paper-scope plausibility support or whether a reviewed cached OSRM, Valhalla,
routingpy, R5/OpenTripPlanner, UXsim, or agency benchmark should replace it.

## Regeneration

Offline manifest regeneration:

```powershell
.\.venv\Scripts\python scripts\write_osrm_snapshot_manifest.py
```

Optional live refresh:

```powershell
.\.venv\Scripts\python scripts\run_osrm_route_benchmark.py
```

Run the validation review packet again after either command:

```powershell
.\.venv\Scripts\python scripts\write_validation_review_packet.py
```

Do not create `data/manifests/validation_acceptance.json` from this manifest
alone.
