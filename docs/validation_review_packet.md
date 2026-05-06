# Validation Review Packet

## Scope

`data/validation/validation_review_packet.csv` summarizes the current validation
package so reviewers can decide the validation and benchmark strategy. It is
review support only. It is not validation acceptance, not benchmark ground
truth, not calibrated real-world validation, and not operational route
guidance.

The packet intentionally does not create
`data/manifests/validation_acceptance.json`.

The latest validation strategy-readiness packet also exists at
`docs/validation_strategy_readiness_packet.md` with data artifacts
`data/validation/validation_strategy_readiness_packet.csv` and
`data/validation/validation_strategy_readiness_manifest.json`. It records
current blockers and human-review items, but it is not validation acceptance.

## Generated Artifacts

| Artifact | Role | Current Scope |
| --- | --- | --- |
| `data/validation/validation_review_packet.csv` | Validation-strategy review worksheet | review support only |
| `data/validation/validation_review_manifest.json` | Conservative packet summary and counts | review support only |
| `data/validation/validation_strategy_readiness_packet.csv` | Current blocker and human-review worksheet | review support only |
| `data/validation/validation_strategy_readiness_manifest.json` | Strategy-readiness counts and claim boundary | review support only |
| `data/validation/osrm_route_benchmark_manifest.json` | Optional OSRM CSV checksum, query URLs, and source-status manifest | review support only |
| `data/validation/canonical_route_road_evidence_exposure.csv` | Route-level road-evidence exposure input | review support only |
| `scripts/write_osrm_snapshot_manifest.py` | Regenerates the OSRM snapshot manifest from cached artifacts | deterministic scaffold command |
| `scripts/write_validation_review_packet.py` | Regenerates the worksheet and manifest | deterministic scaffold command |
| `src/realworld/validation_review_packet.py` | Library implementation for artifact summaries | project-owned code |

## Packet Rows

The worksheet uses a small stable schema and currently summarizes:

- internal route plausibility status counts;
- documented fallback benchmark status counts;
- optional OSRM benchmark status counts when the OSRM CSV is present;
- accessibility-loss route coverage and criticality counts;
- route-level road-evidence exposure counts;
- validation-summary scope-boundary status;
- benchmark-strategy decision requirement.

Every row sets `review_required=true`, `acceptance_ready=false`, and
`publication_ready=false`.

## Interpretation

The current validation artifacts support scaffold plausibility review. They do
not accept a benchmark strategy. Fallback benchmarks remain assumption-based
comparators, optional OSRM rows are external route snapshots with a
non-acceptance checksum/query manifest, and
accessibility-loss rows are route-fragility diagnostics rather than calibrated
outage or accessibility evidence. Route-level road-evidence exposure rows show
where weak road speed, capacity, disruption, and connector assumptions appear
on canonical route candidates; they do not accept those assumptions.

Final claims require a reviewer-created
`data/manifests/validation_acceptance.json` after the benchmark strategy and
claim boundary are reviewed. Current final-study status remains
`final_study_ready=false` with 3 / 15 plan gates ready, 12 / 15 blocked, and
formal acceptance 0 / 12 ready.

## Regeneration

```powershell
.\.venv\Scripts\python scripts\write_osrm_snapshot_manifest.py
.\.venv\Scripts\python scripts\write_route_road_evidence_exposure.py
.\.venv\Scripts\python scripts\write_validation_review_packet.py
.\.venv\Scripts\python scripts\write_validation_strategy_readiness_packet.py
.\.venv\Scripts\python tests\test_realworld_osrm_snapshot_manifest.py
.\.venv\Scripts\python tests\test_realworld_route_road_evidence_exposure.py
.\.venv\Scripts\python tests\test_realworld_validation_review_packet.py
.\.venv\Scripts\python tests\test_realworld_validation_strategy_readiness_packet.py
```

Do not create `data/manifests/validation_acceptance.json` from this packet
alone.
