# Phase 4 Real Rail Evidence Explorer Wave Ledger

Date: 2026-06-03 06:05:49 KST

Objective: run a read-only GPT-5.5 xhigh explorer wave to decide what real
rail/transit evidence is present, missing, or must remain excluded before any
rail builder or compact experiment starts.

## Baseline

- Active plan: `plan.md`.
- Current phase: Phase 4 - Rail, Transit, And Multimodal Evidence.
- Formal acceptance status: unchanged; no formal rail, parameter,
  publication, final-study, or acceptance artifact may be created by this wave.
- Claim boundary: evidence triage only. This wave cannot approve rail service
  calibration, operational routing, emergency availability, or final-study
  readiness.

## Current Git Status Summary

`git status --short --branch` was inspected by the main thread before this
ledger was created. The worktree is already dirty with modified and untracked
files across documentation, rail packets, road packets, source-context caches,
scripts, tests, and `src/realworld/`.

Current-phase owned paths include Phase 4 rail/transit guard files under:

- `data/rail/`
- `docs/rail_*`
- `docs/source_context_hash_audit.md`
- `docs/recovery/agent_ledgers/`
- `scripts/*rail*`
- `scripts/audit_source_context_hashes.py`
- `src/realworld/*rail*`
- `src/realworld/source_artifacts.py`
- `src/realworld/source_context_hash_audit.py`
- `tests/test_realworld_*rail*`
- `tests/test_realworld_source_artifacts.py`
- `tests/test_realworld_source_context_hash_audit.py`

Dirty road, region, publication, README/status, and acceptance/audit paths are
treated as outside this read-only explorer wave unless specifically referenced
as upstream context.

## Expected Read Set

- `plan.md`
- `status.md`
- `README.md`
- `data/rail/`
- `docs/rail_*`
- `docs/source_context_hash_audit.md`
- `docs/recovery/phase4_*.md`
- `docs/recovery/agent_ledgers/phase4_*.md`
- `src/realworld/rail_*.py`
- `src/realworld/source_artifacts.py`
- `src/realworld/source_context_hash_audit.py`
- `tests/test_realworld_*rail*.py`
- `tests/test_realworld_source_artifacts.py`
- public web or package documentation only where required for method context

## Expected Write Set

Read-only agents: none.

Main thread ledger path:

- `docs/recovery/agent_ledgers/phase4_real_rail_evidence_explorer_wave_20260603_060549.md`

## Sub-Agents

Wave 1 runs in parallel because all agents are read-only and answer distinct
questions.

1. GPT-5.5 xhigh GTFS/timetable evidence explorer
   - Write lock: none.
   - Focus: retained GTFS/timetable/shortest-path evidence, report/hash guards,
     unresolved source-decision rows.
2. GPT-5.5 xhigh rail capacity and availability explorer
   - Write lock: none.
   - Focus: capacity, availability, headway, emergency/special-service
     assumptions, source-context caches, exclusion options.
3. GPT-5.5 xhigh rail overclaim/adversarial explorer
   - Write lock: none.
   - Focus: false readiness, operational claims, formal acceptance leakage,
     whether current packets are still review support only.

## Dependency DAG

```text
Main-thread baseline and ledger
  -> Wave 1A GTFS/timetable explorer
  -> Wave 1B capacity/availability explorer
  -> Wave 1C adversarial overclaim explorer
  -> main-thread synthesis
  -> gate decision: implement bounded patch, acquire evidence, exclude evidence,
     or keep Phase 4 blocked
```

## Join Condition

Main thread will wait for explorer reports only when synthesis is needed. No
builder starts until:

- every explorer reports files inspected;
- unsupported claims are discarded;
- remaining rail source-decision rows are classified as source-backed,
  sensitivity-only, scenario-only, excluded, or pending;
- the next implementation or evidence-acquisition step has a frozen write set.

## Required Verification Before Builder Work

- Re-run touched rail tests if a later patch is made.
- Re-run packet writers and publication/final-study audits only when generated
  packet or readiness logic changes.
- Preserve formal acceptance targets as absent.

## Gate Decision

No-go for rail builder, compact experiment, full experiment, or final-study
rail readiness. The three read-only GPT-5.5 xhigh explorers agreed that current
Phase 4 rail/transit status is blocked by missing or unreviewed evidence, not
by missing simulation code.

## Explorer Synthesis

Classification after the read-only wave:

- Static GTFS: `pending`; KTDB metadata/raw HTML context exists, but
  `data/rail/pilot_gtfs.zip` and
  `data/rail/pilot_gtfs_validator_report.json` are absent. The KTDB context is
  not a reviewed GTFS feed and not timing evidence.
- Timetable headway: `pending`; `DATA_GO_KR_KEY` or a reviewed
  `data/rail/pilot_rail_timetable_cache.csv` plus raw payload is absent.
- Shortest-path travel time: `pending`; `DATA_GO_KR_KEY` or a reviewed
  `data/rail/pilot_rail_shortest_path_cache.csv` plus raw payload is absent.
- Station binding: prerequisite/source-backed only for station identifiers; not
  rail timing, capacity, or service availability evidence.
- Rail capacity: sensitivity/proxy-bounded; Metro9 source context exists, but
  capacity acceptance remains pending and is not source-backed for final claims.
- Rail availability: scenario-only stress coverage exists, but operational or
  emergency rail availability is not source-backed.
- Emergency or special rail service: excluded from current claims unless a
  separate reviewed source path is created.
- Transfer, last-mile fleet, dispatch, and station-processing behavior:
  scenario/sensitivity/expert assumptions only unless later source-backed.

All current rail source-decision rows remain pending:

- 3 timing rows are blocking.
- 2 capacity/availability rows require human review.
- 0 rows are completed non-formal source decisions.
- 0 rows are source-backed acquisition, exclusion, sensitivity-only, or
  scenario-only decisions.

## Accepted Findings

- The current guard state is strong enough to prevent false rail final-study
  readiness: publication readiness and final-study readiness tests passed, and
  current manifests keep `publication_ready=false` and
  `can_mark_complete=false`.
- Stress-profile artifacts are useful review support, but not evidence; they
  cannot close rail evidence, publication, final-study, or formal acceptance
  gates.
- The source-decision manifest schema is slightly ambiguous because it does not
  expose an explicit manifest-level `can_support_rail_evidence_gate` field.
  Current code still blocks readiness through `publication_ready=false` and
  `can_mark_complete=false`, but adding an explicit support flag would reduce
  future overread risk.
- The phrase `can_close_rail_timing_gate` in the timing-source request packet
  is a post-review candidate concept and can be overread. It must stay bounded
  by row-level source requirements and packet claim-boundary text.

## Verification Run By Main Thread

```powershell
.\.venv\Scripts\python .\tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python .\tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python .\tests\test_realworld_rail_source_decision_packet.py
```

Observed result: all three commands passed.

## Self-Refine Patch

Accepted the adversarial schema-clarity finding and made a bounded guard patch:

- `src/realworld/rail_source_decision_packet.py` now writes manifest-level
  `can_support_rail_evidence_gate=false` and
  `can_support_acceptance_gate=false` for rail source-decision packets.
- `docs/rail_source_decision_packet.md` now displays both support flags in the
  verdict section after regeneration.
- `data/rail/rail_source_decision_manifest.json` was regenerated with both
  explicit support flags set to false.
- `tests/test_realworld_rail_source_decision_packet.py` now asserts these
  flags stay false for current, mixed, complete non-formal, and CLI paths.

Verification after the patch:

```powershell
.\.venv\Scripts\python -m py_compile .\src\realworld\rail_source_decision_packet.py .\tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python .\scripts\write_rail_source_decision_packet.py
.\.venv\Scripts\python .\tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python .\tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python .\tests\test_realworld_final_study_readiness.py
```

Observed result: all commands passed.

## Next Action

Do not start compact or full experiments. Choose one of two Phase 4 paths:

1. Evidence acquisition path:
   - obtain reviewed `pilot_gtfs.zip` plus same-feed zero-error
     `pilot_gtfs_validator_report.json`; or
   - obtain reviewed timetable and shortest-path cache/raw payloads with
     matching SHA256 metadata.
2. Bounded decision path:
   - complete a reviewer-owned rail source-decision action ledger that marks
     timing claims as sensitivity-only or excluded, capacity as source-backed
     or sensitivity-only, and availability as scenario-only or excluded.

Before any later builder or compact experiment, rerun rail packet/audit
generation and the publication/final-study guard tests.
