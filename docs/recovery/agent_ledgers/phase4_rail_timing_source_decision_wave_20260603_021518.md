# Phase 4 Agent Ledger: Rail Timing Source Decision Wave

## Phase

Phase 4 rail/transit evidence continuation.

## Objective

Determine the next defensible rail timing step after the bounded-treatment
audit. The target is to decide whether current files support acquiring reviewed
rail timing evidence now, or whether the plan should proceed by recording a
strict sensitivity-only or exclusion path for timing-dependent claims.

This wave must not derive rail service evidence, synthesize GTFS feeds, fetch
live API payloads without reviewed credentials, close publication readiness,
close final-study readiness, or create formal acceptance artifacts.

## Baseline Evidence

Current inspected files show:

- `data/rail/rail_fetch_readiness_manifest.json` reports
  `blocking_request_count=3`, `data_go_kr_key_required_count=2`,
  `data_go_kr_key_present_request_count=0`, and
  `rail_evidence_gate_closure_candidate_count=0`.
- `data/rail/rail_fetch_readiness_packet.csv` reports two
  `blocked_missing_data_go_kr_key` rows, one
  `blocked_missing_reviewed_gtfs_file` row, one capacity human-review row, and
  one availability human-review row.
- `data/rail/rail_source_decision_packet.csv` reports three
  `blocked_missing_rail_source_decision` timing rows and zero completed
  non-formal source decisions.
- `data/rail/ktdb_gtfs_source_extract.csv` records source metadata only for the
  KTDB public transport GTFS candidate. It records the access route as a KTDB
  information-disclosure/data-request path, not a retained reviewed GTFS feed.
- `data/rail/rail_bounded_treatment_audit.json` reports
  `mismatch_count=0`, `unchecked_pending_decision_count=2`, and all
  readiness/support flags false.
- Local file inventory under `data/rail` shows cached KTDB/Metro9 HTML and
  review extracts, but no `pilot_gtfs.zip`, no
  `pilot_gtfs_validator_report.json`, no `pilot_rail_timetable_cache.csv`, and
  no `pilot_rail_shortest_path_cache.csv`.
- Environment lookup for `DATA_GO_KR_KEY` did not return a key in the current
  shell.

## Read Set

Read-only agents may inspect:

- `plan.md`
- `status.md`
- `src/realworld/rail_timing_request_packet.py`
- `src/realworld/rail_fetch_readiness_packet.py`
- `src/realworld/rail_source_decision_packet.py`
- `src/realworld/rail_timetable.py`
- `src/realworld/rail_shortest_path.py`
- `src/realworld/rail_gtfs.py`
- `src/realworld/ktdb_gtfs_source.py`
- `src/realworld/source_context_hash_audit.py`
- `scripts/fetch_rail_timetable_cache.py`
- `scripts/fetch_rail_shortest_path_cache.py`
- `scripts/derive_rail_gtfs_evidence.py`
- `scripts/derive_rail_headway_evidence.py`
- `scripts/derive_rail_shortest_path_evidence.py`
- `data/rail/*`
- `data/parameters/rail_service_evidence.csv`
- `data/parameters/rail_assumptions.csv`
- `docs/rail_timing_source_request_packet.md`
- `docs/rail_fetch_readiness_packet.md`
- `docs/rail_source_decision_packet.md`
- `docs/source_context_hash_audit.md`
- relevant rail tests.

## Forbidden Paths And Actions

- No edits by read-only agents.
- No live data fetch.
- No synthetic GTFS feed creation.
- No edits to `data/parameters/rail_service_evidence.csv`.
- No formal acceptance targets.
- No readiness flag may be changed to true.
- No operational rail-service, dispatch, availability, or route-plan claims.

## Agents

Wave 1 read-only agents, all GPT-5.5 xhigh:

- Agent A: GTFS and timetable evidence acquisition reviewer.
  - Decide whether current KTDB/data.go.kr context supports immediate evidence
    derivation, and list the exact missing reviewer-provided inputs.
- Agent B: rail timing sensitivity/exclusion reviewer.
  - Decide which timing-dependent claims must be retained as sensitivity-only
    or excluded if API/GTFS evidence is not supplied.
- Agent C: adversarial methodology reviewer.
  - Check for false realism, source-context misuse, invalid use of sample GTFS
    files, and hidden acceptance/readiness overclaims.

## Join Condition

After Wave 1, the main thread must synthesize:

1. whether a safe implementation step exists without external credentials or a
   reviewed GTFS feed;
2. if yes, the exact disjoint write set and tests;
3. if no, the exact blocker/evidence request and whether to write a
   non-acceptance timing-decision audit.

## Expected Verification If Implemented

```powershell
.\.venv\Scripts\python -m py_compile <touched modules/scripts/tests>
.\.venv\Scripts\python <new-or-touched script>
.\.venv\Scripts\python <new-or-touched test>
.\.venv\Scripts\python tests\test_realworld_rail_fetch_readiness_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_ktdb_gtfs_source.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
```

## Initial Gate

Proceed to Wave 1 read-only agent review.

## Wave 1 Result

Read-only agents completed.

Accepted findings:

- Current files do not support immediate source-backed rail timing evidence
  derivation.
- `DATA_GO_KR_KEY` is absent in the current shell.
- `data/rail/pilot_gtfs.zip`,
  `data/rail/pilot_gtfs_validator_report.json`,
  `data/rail/pilot_rail_timetable_cache.csv`,
  `data/rail/pilot_rail_timetable_raw.json`,
  `data/rail/pilot_rail_shortest_path_cache.csv`, and
  `data/rail/pilot_rail_shortest_path_raw.json` are absent.
- KTDB files are source-context metadata and raw HTML only; they are not a
  retained reviewed GTFS feed, not GTFS validation, and not timing evidence.
- Current rail timing values may be described only as documented assumptions or
  sensitivity proxies unless reviewed timing evidence is supplied.
- A new audit that merely repeats missing API key / missing GTFS blockers would
  be duplicative.
- A real guardrail issue exists: final-study rail readiness must not treat
  `rail_source_decision_recorded=true` plus zero blocker/human-review counts as
  enough unless every rail source-decision row is complete.

Rejected or unsupported actions:

- No live data fetch was justified.
- No GTFS feed may be synthesized.
- No fixture or sample GTFS file may be used as project evidence.
- No rail service evidence, publication readiness, final-study readiness, or
  formal acceptance gate can be closed from this wave.

## Implementation Result

Implemented one bounded guardrail improvement:

- `src/realworld/final_study_readiness.py` now requires
  `completed_source_decision_count == row_count` in addition to
  `rail_source_decision_recorded=true`, zero blocking rows, and zero
  human-review rows before `rail_source_decision_ready` can become true.
- `tests/test_realworld_final_study_readiness.py` now includes a regression
  test proving recorded-but-incomplete rail source decisions keep the rail gate
  blocked.
- `scripts/write_goal_completion_audit.py` was rerun so
  `docs/current_goal_completion_audit.md` and
  `data/manifests/current_goal_completion_audit.json` reflect the stricter rail
  source-decision blocker.

## Verification

Commands executed and passed:

```powershell
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_fetch_readiness_packet.py
.\.venv\Scripts\python tests\test_realworld_source_context_hash_audit.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
.\.venv\Scripts\python scripts\write_goal_completion_audit.py
```

## Remaining Blockers

- Reviewed rail timing evidence still requires external reviewer-provided API
  caches or reviewed GTFS plus validator report.
- Current rail timing remains assumption/proxy-scoped.
- Capacity and availability remain unresolved source-backed,
  sensitivity-only, scenario-only, or exclusion decisions.
- Final-study readiness remains false.
