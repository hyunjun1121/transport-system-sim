# Phase 4 Static Timetable Adapter Ledger

## Phase

Phase 4 rail/transit evidence acquisition support.

## Objective

Add or document a safe path for converting a reviewed official static timetable
CSV into the repository's normalized `rail_timetable_cache` schema without
claiming rail evidence before the retained source artifact, field mapping,
hashes, and downstream derivation checks are present.

## Baseline Status

Timestamp: 2026-06-03 06:28:50 KST.

Current worktree is dirty from ongoing rail, road, readiness, and recovery
work. The main thread inspected `git status --short` before this ledger and
will not run cleanup, deletion, broad moves, compact experiments, or full
experiments in this phase.

Hardware snapshot for this phase:

- CPU observed by WMI: AMD Ryzen 7 5800X3D 8-Core Processor.
- RAM observed by WMI: about 31.9 GB.
- GPU observed by `nvidia-smi`: NVIDIA GeForce RTX 3090, 24,576 MiB VRAM,
  KMD 610.47, CUDA UMD 13.3.

## Expected Read Set

- `plan.md`
- `docs/schemas/rail_timetable_cache_schema.md`
- `scripts/fetch_rail_timetable_cache.py`
- `scripts/derive_rail_service_evidence.py`
- `scripts/derive_rail_headway_evidence.py`
- `src/realworld/rail_timetable.py`
- `src/realworld/rail_timetable_api.py`
- `src/realworld/source_artifacts.py`
- `tests/test_realworld_rail_timetable.py`
- `tests/test_realworld_rail_derivation_scripts.py`
- `data/rail/rail_source_decision_packet.csv`
- `data/rail/rail_source_decision_manifest.json`

## Expected Write Set

Allowed for this phase only:

- `scripts/normalize_rail_timetable_cache.py`
- `src/realworld/rail_timetable_static.py`
- `tests/test_realworld_rail_timetable_static.py`
- `docs/schemas/rail_timetable_cache_schema.md`
- this ledger file

If the source CSV cannot be inspected or if the adapter design would require
guessing source headers, the implementation must stop at documentation and
tests for explicit user-supplied column mapping. It must not create
`data/rail/pilot_rail_timetable_cache.csv` from invented data.

## Forbidden Paths

- formal acceptance targets;
- broad top-level directories;
- generated compact/full experiment outputs;
- existing rail evidence CSVs unless a separate main-thread synthesis grants a
  write lock;
- deletion, recursive cleanup, or broad moves.

## Sub-Agents

Planned GPT-5.5 xhigh read-only explorer wave:

1. Static timetable evidence explorer:
   - inspect current rail timetable schema, scripts, and source-decision files;
   - recommend a safe static-file acquisition or normalization path;
   - read-only.
2. Test and adapter-scope explorer:
   - inspect rail timetable tests and derivation scripts;
   - recommend minimal tests for explicit-column static normalization;
   - read-only.
3. Adversarial rail evidence reviewer:
   - inspect claim boundaries and acceptance hygiene for the proposed adapter;
   - identify ways the adapter could be overread as evidence;
   - read-only.

## Dependency DAG

```text
main-thread local inspection
  -> parallel read-only explorer wave
  -> main-thread synthesis
  -> scoped implementation or documentation-only blocker record
  -> narrow tests
  -> gate decision
```

## Narrow Tests

Candidate tests if implementation proceeds:

```powershell
.\.venv\Scripts\python tests\test_realworld_rail_timetable_static.py
.\.venv\Scripts\python tests\test_realworld_rail_timetable.py
.\.venv\Scripts\python tests\test_realworld_rail_derivation_scripts.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
```

## Gate Rules

- Proceed only if the adapter uses explicit source-column mappings and writes
  the normalized repository schema.
- Block evidence upgrade if the official CSV file itself is not retained and
  hashable.
- Block evidence upgrade if actual source headers are not inspected or mapped
  by user-supplied arguments.
- Keep rail final-study and formal acceptance gates open.

## Main-Thread Synthesis

Accepted findings from the GPT-5.5 xhigh explorer wave:

- The existing rail timetable evidence path is already built around a
  normalized station-event cache schema, not an arbitrary official CSV schema.
- The current live acquisition helper is API-key based and does not support
  static file-data CSV normalization.
- The repository must not infer unseen official source headers.
- A static CSV helper is acceptable only as a source-cache preparation adapter
  with explicit source-column mappings.
- The adapter output must remain non-acceptance review support. It cannot close
  rail evidence, publication-readiness, final-study, or formal acceptance gates.
- Headway-only normalized rows cannot satisfy travel-time, capacity, or
  availability gates.

Rejected or unsupported findings:

- No claim was accepted that the official static data.go.kr CSV headers are
  known locally. The static public file itself was not retained or inspected in
  this phase.
- No claim was accepted that a normalized cache row is accepted rail evidence.

Implementation scope frozen:

- Add a static timetable normalization helper that requires exact source-column
  mappings.
- Add a CLI wrapper with explicit required mapping arguments.
- Add tests with arbitrary source headers to prove no header inference is used.
- Update schema/status/agent documentation with the non-acceptance boundary.

## Implemented Changes

- Added `src/realworld/rail_timetable_static.py`.
- Added `scripts/normalize_rail_timetable_cache.py`.
- Added `tests/test_realworld_rail_timetable_static.py`.
- Updated `docs/schemas/rail_timetable_cache_schema.md`.
- Updated `agents.md` and `status.md` so the new script is represented in the
  project command inventory.

The adapter writes normalized cache rows only, then reloads the output through
`load_cached_timetable_events()`. It optionally writes a manifest containing
source and output SHA256 values, the explicit source-column map, selection
filters, and a non-acceptance claim scope.

## Verification Results

Commands run and passed:

```powershell
.\.venv\Scripts\python -m py_compile .\src\realworld\rail_timetable_static.py .\scripts\normalize_rail_timetable_cache.py .\tests\test_realworld_rail_timetable_static.py
.\.venv\Scripts\python .\tests\test_realworld_rail_timetable_static.py
.\.venv\Scripts\python .\tests\test_realworld_rail_timetable.py
.\.venv\Scripts\python .\tests\test_realworld_rail_derivation_scripts.py
.\.venv\Scripts\python .\tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python .\tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python .\tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py
.\.venv\Scripts\python .\tests\test_rail.py
.\.venv\Scripts\python .\tests\test_transfers.py
```

The first `test_realworld_plan_audit.py` run failed because the new script was
not yet listed in both `agents.md` and `status.md`. The documentation inventory
was patched and the plan audit then passed.

## Remaining Blockers

- No official static timetable CSV has been retained in this repository for
  this phase.
- No actual official source headers were inspected from a retained CSV file in
  this phase.
- Rail source-decision manifest still reports
  `can_support_rail_evidence_gate=false` and
  `can_support_acceptance_gate=false`.
- Formal rail evidence, publication readiness, final-study readiness, and
  formal acceptance remain blocked.

## Gate Decision

Proceed with the adapter as non-acceptance source-cache preparation support.
Block any rail evidence upgrade until a reviewed raw timetable file, exact
field mapping, source URL/citation, extraction date, raw/cache hashes, station
binding, provenance/license review, and reviewer source decision are present.

## Source-Decision Integration

After the adapter was implemented, the rail source workflow was extended so the
static CSV path is visible to reviewers before evidence derivation.

Implemented changes:

- Added `rail_static_timetable_csv_headway_request` to
  `src/realworld/rail_timing_request_packet.py`.
- Added `reviewed_static_timetable_csv_required` handling to
  `src/realworld/rail_fetch_readiness_packet.py`.
- Added source-decision topic, candidate decisions, artifact status, required
  evidence, follow-up artifacts, and timing-support classification for
  `reviewed_static_timetable_csv_required` in
  `src/realworld/rail_source_decision_packet.py`.
- Regenerated:
  - `data/rail/rail_timing_source_request_packet.csv`
  - `data/rail/rail_timing_source_request_manifest.json`
  - `data/rail/rail_fetch_readiness_packet.csv`
  - `data/rail/rail_fetch_readiness_manifest.json`
  - `docs/rail_fetch_readiness_packet.md`
  - `data/rail/rail_source_decision_packet.csv`
  - `data/rail/rail_source_decision_manifest.json`
  - `docs/rail_source_decision_packet.md`
  - `data/rail/rail_source_decision_action_ledger_template.csv`
  - `data/rail/rail_source_decision_action_ledger_template_manifest.json`
  - `docs/rail_source_decision_action_ledger_template.md`
- Updated affected row-count expectations in tests and the plan-artifact audit.

The new request is explicitly headway-only and blocked until a reviewed static
timetable CSV, explicit column mapping, source citation, normalization manifest,
and retained hashes are present. It does not infer source headers and does not
close travel-time, capacity, availability, rail evidence, publication, final
study, or formal acceptance gates.

Additional verification commands run and passed:

```powershell
.\.venv\Scripts\python -m py_compile .\src\realworld\rail_timing_request_packet.py .\src\realworld\rail_fetch_readiness_packet.py .\src\realworld\rail_source_decision_packet.py
.\.venv\Scripts\python -m py_compile .\tests\test_realworld_rail_timing_request_packet.py .\tests\test_realworld_rail_fetch_readiness_packet.py .\tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python .\scripts\write_rail_timing_source_request_packet.py
.\.venv\Scripts\python .\scripts\write_rail_fetch_readiness_packet.py
.\.venv\Scripts\python .\scripts\write_rail_source_decision_packet.py
.\.venv\Scripts\python .\scripts\write_rail_source_decision_action_ledger_template.py
.\.venv\Scripts\python .\tests\test_realworld_rail_timing_request_packet.py
.\.venv\Scripts\python .\tests\test_realworld_rail_fetch_readiness_packet.py
.\.venv\Scripts\python .\tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python .\tests\test_realworld_rail_source_decision_action_ledger_template.py
.\.venv\Scripts\python .\tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python .\tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py
.\.venv\Scripts\python .\tests\test_realworld_rail_timetable_static.py
```

Additional failed-then-fixed checks:

- `test_realworld_rail_timing_request_packet.py` initially failed on a stale
  five-row expectation.
- `test_realworld_rail_source_decision_packet.py` initially failed on a stale
  complete-ledger row count.
- `test_realworld_rail_source_decision_action_ledger_template.py` initially
  failed on a stale five-row template expectation.
- `test_realworld_final_study_readiness.py` initially failed on stale
  fetch/source-decision counts.
- `test_realworld_plan_audit.py` initially failed because the audit expected
  five rail timing/source rows instead of six.

All were corrected without changing final-study readiness or formal acceptance
status.
