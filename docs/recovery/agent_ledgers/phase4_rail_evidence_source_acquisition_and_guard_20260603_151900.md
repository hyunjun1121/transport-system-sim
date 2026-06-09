# Phase 4 Rail Evidence Source Acquisition And Guard Ledger - 2026-06-03 15:19:00 KST

## Objective

Continue Phase 4 rail/transit evidence work under `plan.md` by checking whether
current rail timing, GTFS, capacity, and availability artifacts can support a
more real-world simulation claim. The wave must keep final-study, publication,
and formal-acceptance gates fail-closed unless source-backed rail evidence and
review decisions exist.

## Agents

All agents were GPT-5.5 xhigh read-only agents. They were closed after
synthesis.

1. GTFS/timetable evidence explorer
   - Agent id: `019e8c0b-1c84-7a41-8697-45723b7da317`.
   - Scope: local rail timing scripts, GTFS/timetable/shortest-path caches,
     station bindings, and rail evidence tests.
2. Official-source/package explorer
   - Agent id: `019e8c0b-6a3b-73e3-af0c-b559db550cef`.
   - Scope: official/public GTFS, timetable, shortest-path, license, and
     acquisition paths.
3. Adversarial rail-evidence reviewer
   - Agent id: `019e8c0b-d40c-7001-bef4-246538c8a01b`.
   - Scope: stale generated outputs, overclaim risk, readiness guards, and
     bounded-treatment dependency gaps.

## Files Inspected By Main Thread

- `scripts/cache_ktdb_gtfs_source.py`
- `src/realworld/ktdb_gtfs_source.py`
- `tests/test_realworld_ktdb_gtfs_source.py`
- `scripts/derive_rail_gtfs_evidence.py`
- `scripts/fetch_rail_timetable_cache.py`
- `scripts/fetch_rail_shortest_path_cache.py`
- `scripts/normalize_rail_timetable_cache.py`
- `scripts/audit_publication_readiness.py`
- `scripts/audit_final_study_readiness.py`
- `scripts/audit_plan_artifacts.py`
- `tests/test_realworld_publication_readiness.py`
- `tests/test_realworld_final_study_readiness.py`
- `tests/test_realworld_plan_audit.py`
- `src/realworld/publication_readiness.py`
- `src/realworld/final_study_readiness.py`
- `src/realworld/rail_bounded_treatment_audit.py`
- `data/rail/rail_source_decision_manifest.json`
- `data/rail/rail_source_decision_packet.csv`
- `data/rail/rail_transit_stress_profile_manifest.json`
- `data/rail/rail_bounded_treatment_audit.json`
- `data/parameters/rail_service_evidence.csv`

## Accepted Findings

- There is no current source-backed rail timing evidence in the repo. The
  existing rail service evidence row is still a proxy and remains blocked for
  publication/final-study claims.
- `cache_ktdb_gtfs_source.py` caches KTDB source-context metadata only. It does
  not download a reviewed GTFS feed and cannot create rail service evidence.
- The strongest GTFS acquisition path is reviewer/manual acquisition of KTDB
  GTFS, with retained raw zip, license/attribution notes, SHA256, extraction
  metadata, and a same-feed GTFS Validator report.
- data.go.kr timetable and shortest-path paths remain blocked without a service
  key and retained raw/cache payloads.
- Rail capacity is currently sensitivity-only, and rail availability is
  scenario-only. Those bounded treatments can be consistency-checked but cannot
  close rail evidence, publication, final-study, or formal acceptance gates.
- The prior guard chain could overread future optimistic source-decision
  manifests because it did not require explicit support flags or bounded
  treatment integrity.

## Patches Applied

- `src/realworld/publication_readiness.py`
  - Added `rail_bounded_treatment_integrity_ready`.
  - Made `rail_evidence_ready` depend on service evidence, station binding,
    source-decision support, transit stress-profile support, and bounded
    treatment integrity.
  - Required explicit rail source-decision support flags:
    `can_support_publication_gate`, `can_support_rail_evidence_gate`,
    `accepted_source_backed_rail_service_evidence`, and a positive
    `rail_service_evidence_gate_closure_candidate_count`.
- `src/realworld/final_study_readiness.py`
  - Made the rail gate require the same stricter source-decision flags.
  - Added bounded-treatment integrity as a rail gate dependency.
- `scripts/audit_plan_artifacts.py`
  - Reused `audit_publication_readiness()` for plan-level evidence gates.
  - Exposed bounded-treatment integrity, warning count, mismatch count, pending
    decision count, and blockers in `rail_evidence_audit`.
- Tests were expanded for publication readiness, final-study readiness, and
  plan audit so future optimistic non-evidence artifacts remain blocked.
- `data/manifests/publication_readiness_audit.json` and
  `docs/publication_readiness_audit.md` were regenerated. The audit now reports
  10 gates, 1 ready, 9 blocked.

## Verification Commands

All commands below passed:

```powershell
.\.venv\Scripts\python -m py_compile .\src\realworld\publication_readiness.py .\src\realworld\final_study_readiness.py .\tests\test_realworld_publication_readiness.py .\tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python -m py_compile .\scripts\audit_plan_artifacts.py .\tests\test_realworld_plan_audit.py
.\.venv\Scripts\python .\tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python .\tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python .\scripts\audit_publication_readiness.py
.\.venv\Scripts\python .\scripts\audit_final_study_readiness.py
.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py
.\.venv\Scripts\python .\scripts\audit_plan_artifacts.py
```

## Current Gate State

- Publication readiness remains blocked:
  - `publication_ready=false`
  - gate count `10`
  - ready gate count `1`
  - blocked gate count `9`
- Final-study readiness remains blocked:
  - `final_study_ready=false`
  - gate count `15`
  - blocked gates include `rail_evidence`.
- Rail bounded-treatment audit remains review support only:
  - `mismatch_count=0`
  - `warning_count=4`
  - `unchecked_pending_decision_count=2`
  - `publication_ready=false`
  - `can_mark_complete=false`
  - `can_support_rail_evidence_gate=false`
  - `can_support_acceptance_gate=false`

## Remaining Blockers

- Acquire and retain reviewed rail timing evidence:
  - KTDB GTFS zip plus same-feed GTFS Validator report, or
  - reviewed static timetable plus shortest-path cache payloads.
- Record reviewed rail source decisions with zero blocking and zero human-review
  rows before allowing rail evidence gate closure.
- Decide rail capacity and availability as source-backed, bounded
  sensitivity/scenario-only, or excluded from final claims.
- Refresh rail, parameter, publication-readiness, final-study, and plan audits
  after any source-backed rail acquisition.

