# OSRM Route Benchmark Manifest

> Current project status (2026-05-08): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


`data/validation/osrm_route_benchmark_manifest.json` describes the optional
OSRM route benchmark CSV that is already cached in `data/validation/`. It also
records the configured raw-response directory and any retained raw OSRM JSON
payload files found there.

This manifest is review support only. It is not validation acceptance, not
ground truth, not calibrated local traffic evidence, and not operational
routing guidance.

## Artifacts

| Artifact | Role | Scope |
| --- | --- | --- |
| `data/validation/external_route_benchmarks_osrm.csv` | Optional OSRM route-distance and travel-time comparison rows | plausibility review only |
| `data/validation/osrm_route_benchmark_summary.md` | Human-readable OSRM benchmark summary | plausibility review only |
| `data/validation/osrm_route_benchmark_manifest.json` | CSV checksum, query URLs, source classes, row counts, raw-payload inventory, and claim boundary | non-acceptance provenance |
| `data/validation/osrm_route_raw/` | Optional retained OSRM JSON response payloads when live capture is run with `--raw-output-dir` | traceability review only |
| `scripts/write_osrm_snapshot_manifest.py` | Regenerates the manifest from cached CSV, summary, and optional raw payload artifacts | deterministic offline command |
| `scripts/run_osrm_route_benchmark.py` | Optional live OSRM query path that can retain raw payloads and rewrites the manifest | explicit live command only |

## Current Interpretation

The current OSRM CSV has three pass rows after bus-practical road filtering.
Those rows are marked as a cached external-router snapshot with retained raw
response files. The manifest currently records `raw_response_file_count=3`
and `unpinned_row_count=0`, but it still keeps OSRM in review-only scope rather
than treating it as accepted benchmark evidence.

If reviewers choose to refresh the OSRM snapshot again, keep using raw-payload
capture so the manifest can list retained response files and SHA256 values.
That extra traceability still does not make OSRM ground truth or validation
acceptance; it only gives reviewers the response payloads behind the cached CSV
rows.

Use this manifest to review whether the current OSRM snapshot is sufficient for
paper-scope plausibility support or whether a reviewed cached OSRM, Valhalla,
routingpy, R5/OpenTripPlanner, UXsim, or agency benchmark should replace it.

## Regeneration

Offline manifest regeneration:

```powershell
.\.venv\Scripts\python scripts\write_osrm_snapshot_manifest.py
```

Offline manifest regeneration with an explicit raw-response directory:

```powershell
.\.venv\Scripts\python scripts\write_osrm_snapshot_manifest.py --raw-response-dir data\validation\osrm_route_raw
```

Optional live refresh without raw payload retention:

```powershell
.\.venv\Scripts\python scripts\run_osrm_route_benchmark.py
```

Optional live refresh with raw payload retention:

```powershell
.\.venv\Scripts\python scripts\run_osrm_route_benchmark.py --raw-output-dir data\validation\osrm_route_raw
```

Run the validation review packet again after either command:

```powershell
.\.venv\Scripts\python scripts\write_validation_review_packet.py
```

Do not create `data/manifests/validation_acceptance.json` from this manifest
alone.
