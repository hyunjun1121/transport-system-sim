# Phase 11 OSRM Route Benchmark Claim-Boundary Sprint - 2026-06-04

## Objective

Reduce release-blocking lexical claim-language findings in
`docs/osrm_route_benchmark_manifest.md` and its owned OSRM benchmark manifest
generation path while preserving the route-plausibility-only claim boundary.

## Claim Boundary

This sprint is lexical claim-boundary and generated-artifact consistency cleanup
only. It does not create route validation acceptance, traffic calibration,
publication readiness, study-closeout readiness, route-use guidance, or formal
reviewer approval.

## Main-Thread Inspection

Inspected current blocker evidence and owned generation paths:

- `data/validation/claim_language_guard.csv`
- `docs/osrm_route_benchmark_manifest.md`
- `data/validation/osrm_route_benchmark_manifest.json`
- `data/validation/osrm_route_benchmark_summary.md`
- `scripts/run_osrm_route_benchmark.py`
- `scripts/write_osrm_snapshot_manifest.py`
- `src/realworld/osrm_snapshot_manifest.py`
- `tests/test_realworld_osrm_snapshot_manifest.py`
- `tests/test_realworld_plausibility.py`

Initial blocker slice for `docs/osrm_route_benchmark_manifest.md`:

- `accepted` in benchmark-evidence wording
- `validated` in review-packet rerun wording

## Edits

- `docs/osrm_route_benchmark_manifest.md`
  - replaced route-use and local-traffic overclaim wording with review-support
    wording
  - replaced benchmark acceptance wording with benchmark gate-closure wording
  - changed validation-review rerun wording to benchmark-review wording
- `src/realworld/osrm_snapshot_manifest.py`
  - bounded generated manifest claim boundary to plausibility review only
  - replaced local-traffic, final-strategy, and final-claim wording with
    release-scope review wording
- `scripts/run_osrm_route_benchmark.py`
  - bounded generated summary and raw-payload claim boundary wording
  - replaced public-agency forecast and operational route-plan wording with
    non-route-use wording
  - replaced accepted analysis-corridor wording with selected
    analysis-corridor wording

Regenerated using cached raw OSRM payload replay:

- `data/validation/external_route_benchmarks_osrm.csv`
- `data/validation/osrm_route_benchmark_summary.md`
- `data/validation/osrm_route_benchmark_manifest.json`

## Commands

| command | exit | evidence |
| --- | ---: | --- |
| `Select-String ... docs\osrm_route_benchmark_manifest.md data\validation\osrm_route_benchmark_manifest.json scripts\run_osrm_route_benchmark.py scripts\write_osrm_snapshot_manifest.py src\realworld\osrm_snapshot_manifest.py tests\test_realworld_osrm_snapshot_manifest.py` | 0 | identified OSRM claim-boundary terms and owned paths |
| `.\.venv\Scripts\python scripts\write_osrm_snapshot_manifest.py` | 0 | regenerated manifest JSON from cached CSV, summary, and raw payload directory |
| `.\.venv\Scripts\python scripts\run_osrm_route_benchmark.py` | 0 | replayed cached raw OSRM payloads; wrote 3 rows and status `{'pass': 3, 'warn': 0, 'fail': 0}` |
| `Select-String ... osrm files ...` | 0 | after regeneration, remaining natural-language OSRM overclaim terms were removed; only false status-field names and path literals remained |
| `.\.venv\Scripts\python -m py_compile src\realworld\osrm_snapshot_manifest.py scripts\run_osrm_route_benchmark.py scripts\write_osrm_snapshot_manifest.py tests\test_realworld_osrm_snapshot_manifest.py tests\test_realworld_plausibility.py` | 0 | syntax compile passed |
| `.\.venv\Scripts\python tests\test_realworld_osrm_snapshot_manifest.py` | 0 | OSRM snapshot manifest tests passed |
| `.\.venv\Scripts\python tests\test_realworld_plausibility.py` | 0 | route plausibility tests passed |
| `.\.venv\Scripts\python tests\test_realworld_claim_language_guard.py` | 0 | claim-language guard tests passed |
| `git diff --check -- docs\osrm_route_benchmark_manifest.md src\realworld\osrm_snapshot_manifest.py scripts\run_osrm_route_benchmark.py data\validation\external_route_benchmarks_osrm.csv data\validation\osrm_route_benchmark_summary.md data\validation\osrm_route_benchmark_manifest.json` | 0 | whitespace check passed; CRLF warnings only |
| `.\.venv\Scripts\python scripts\audit_claim_language.py` | 0 | full guard regenerated; blocking findings reduced from 52 to 50 |
| `.\.venv\Scripts\python scripts\write_dirty_worktree_classification.py` | 0 | dirty classification refreshed; manifest reports 573 classified dirty paths and 0 unclassified paths |
| `.\.venv\Scripts\python tests\test_realworld_plan_audit.py` | 0 | plan artifact audit test passed |
| `.\.venv\Scripts\python scripts\audit_plan_artifacts.py` | 1 | expected blocked closeout state remained; verdict `executable_quasi_real_scaffold_not_final_calibrated_study` |

## Results

- `docs/osrm_route_benchmark_manifest.md` no longer appears in the full
  release-blocking claim-language blocker list.
- Full claim-language blocker count is now 50.
- OSRM remains a cached external-router plausibility comparator only.
- Study closeout remains blocked, publication readiness remains false, and no
  formal acceptance artifact was created.

## Remaining Blocker Direction

Next claim-language cleanup candidates include
`docs/parameter_evidence_review_packet.md`,
`docs/parameter_evidence_source_request_packet.md`,
`docs/validation_benchmark_readiness_packet.md`,
`docs/graph_scale_method_decision_packet.md`,
`docs/reproducibility_decision_packet.md`, and related generated manifests.
