# Phase 4 Source Decision Evidence Barrier Ledger

Date: 2026-06-03 07:21:57 KST

Objective: continue Phase 4 by deciding the next evidence-backed rail/transit
step after the source-decision packet added the static timetable CSV row. This
ledger controls a read-only GPT-5.5 xhigh explorer wave before any builder or
compact experiment starts.

## Baseline Status

- Active plan: `plan.md`.
- Current phase: Phase 4 - Rail, Transit, And Multimodal Evidence.
- Current worktree: dirty before this wave; the main thread inspected
  `git status --short --branch`.
- Formal acceptance status: unchanged and blocked. No formal rail, parameter,
  final-study, or acceptance artifact may be created by this wave.
- Claim boundary: evidence triage only. This wave cannot approve rail service
  calibration, operational routing, emergency availability, publication
  readiness, final-study readiness, or formal acceptance.

## Current Rail Source-Decision State

The main thread inspected:

- `data/rail/rail_source_decision_manifest.json`
- `data/rail/rail_fetch_readiness_manifest.json`
- `data/rail/rail_source_decision_packet.csv`
- `data/rail/rail_timing_source_request_manifest.json`
- `data/rail/rail_transit_stress_profile_manifest.json`
- `data/rail/rail_bounded_treatment_audit.json`

Observed current manifest state:

- rail source-decision row count: 6.
- source-decision rows completed: 0.
- source-decision rows pending: 6.
- blocking source-decision rows: 4.
- human-review source-decision rows: 2.
- timing source-decision rows: 4.
- `can_support_rail_evidence_gate=false`.
- `can_support_acceptance_gate=false`.
- `publication_ready=false`.
- `can_mark_complete=false`.

Current source-decision rows:

- `rail_shortest_path_travel_time_request`: pending/blocking.
- `rail_static_gtfs_timing_request`: pending/blocking.
- `rail_static_timetable_csv_headway_request`: pending/blocking.
- `rail_timetable_headway_request`: pending/blocking.
- `rail_availability_scenario_request`: pending/human review.
- `rail_capacity_treatment_request`: pending/human review.

## Read Snapshot

Key artifact SHA256 values recorded before the explorer wave:

| Path | SHA256 |
|---|---|
| `plan.md` | `1489D9B6A5154CF54CE4BFBB5A3A449EC4E0DF82F64CF73202A2D67812FEF02E` |
| `data/rail/rail_source_decision_manifest.json` | `9360637D9FB7AE81181EB5E765FB3451989ADD7E7AE8AF745082C072BA3C64DE` |
| `data/rail/rail_source_decision_packet.csv` | `CB625252527B115EF8FEFBE7DA33D00B6111DF681DB334B35904B83A5B8DCB5A` |
| `data/rail/rail_fetch_readiness_manifest.json` | `4DD332400A81F2B4E70792D01C1ADCA3F994B6FAAAF212B7CF45A75573F6744F` |
| `data/rail/rail_timing_source_request_manifest.json` | `7A9815DD49CF23C25A75AF4427A0D2BB5C70197F2D2856FEB37BD6A47F96F900` |
| `data/rail/rail_transit_stress_profile_manifest.json` | `A17EC543A2C5DED42CBFDBCB7818706C108FC4FA79F425AA9A03AD785E8D433E` |
| `data/rail/rail_bounded_treatment_audit.json` | `773ADF788470F219DCA02FF06568E3C093F3874CE6C1456D1786F85A0C4E6BF3` |
| `src/realworld/rail_source_decision_packet.py` | `CA0A51FE8022CC62CC02A4D99BED2EA507BD2DFF0754DC6CA7084C9DE3F3773E` |
| `src/realworld/rail_fetch_readiness_packet.py` | `F011C055E2EAB1BC4B622C8C6A9796DD6DD5771C8CC4DF9E956E55D0A8633388` |
| `src/realworld/rail_timing_request_packet.py` | `66520AF3978FE5695C8EF296345EE2A0D2AF372763068E416F26C140592E96A6` |
| `src/realworld/rail_bounded_treatment_audit.py` | `80516DC8D953033B07B442FA7CB5464897BA8CD098F735AECAD8FDC3CD37718A` |
| `src/realworld/rail_transit_stress_profile_packet.py` | `ABD5B6CE4C4C7CCDEF2AC63A4644041EEB725B6D1DBF13CFBD0C6F9369700E13` |

If any scoped file changes before synthesis, the affected explorer result is
invalid and must be rerun.

## Expected Read Set

- `plan.md`
- `status.md`
- `data/rail/rail_*`
- `docs/rail_*`
- `docs/source_context_hash_audit.md`
- `docs/recovery/phase4_*.md`
- `docs/recovery/agent_ledgers/phase4_*.md`
- `src/realworld/rail_*.py`
- `src/realworld/source_artifacts.py`
- `src/realworld/source_context_hash_audit.py`
- `tests/test_realworld_*rail*.py`
- `tests/test_realworld_source_artifacts.py`
- `tests/test_realworld_source_context_hash_audit.py`

## Expected Write Set

Read-only agents: none.

Main thread may later edit this ledger only, then may freeze a new write set if
the synthesis identifies a concrete implementation guard. No builder write lock
is granted yet.

## Sub-Agent Wave

Wave 1 runs in parallel because all agents are read-only and inspect distinct
questions.

1. GPT-5.5 xhigh GTFS/timetable evidence explorer
   - Focus: static GTFS, static timetable CSV, public timetable, shortest-path
     cache, source artifacts, hash/validator requirements, and whether current
     timing rows should be acquired, excluded, or left pending.
2. GPT-5.5 xhigh capacity/availability explorer
   - Focus: capacity treatment, availability scenario treatment, stress
     profiles, bounded-treatment audit, and whether source decisions should be
     source-backed, sensitivity-only, scenario-only, excluded, or pending.
3. GPT-5.5 xhigh overclaim/adversarial explorer
   - Focus: false readiness, generated packet overread risk, hidden
     operational rail-service assumptions, and whether any wording or manifest
     field still permits overclaim.

## Dependency DAG

```text
Main-thread baseline and ledger
  -> Wave 1A GTFS/timetable evidence explorer
  -> Wave 1B capacity/availability explorer
  -> Wave 1C overclaim/adversarial explorer
  -> main-thread synthesis
  -> gate decision: acquire evidence, record exclusion/sensitivity/scenario
     decision support, implement a narrow guard, or keep Phase 4 blocked
```

## Join Condition

No builder starts until:

- every explorer reports files inspected;
- unsupported recommendations are discarded;
- every rail source-decision row is classified as source-backed,
  sensitivity-only, scenario-only, excluded, or pending;
- the next implementation or evidence-acquisition step has a frozen write set;
- the main thread records the synthesis in this ledger.

## Required Verification If A Later Patch Is Made

- Run the touched rail tests first.
- Rerun rail packet writers if generated packets change.
- Rerun publication and final-study readiness tests if readiness logic or
  source-decision semantics change.
- Rerun `git status --short --branch` after every writer, audit, or test command
  that may touch files.

## Initial Gate Decision

Blocked for compact experiment, full experiment, rail evidence gate closure,
publication readiness, final-study readiness, and formal acceptance. The next
step is evidence-decision synthesis, not a simulation run.

## Explorer Synthesis

The read-only GPT-5.5 xhigh wave completed with three independent conclusions:

1. GTFS/timetable timing evidence:
   - `rail_static_gtfs_timing_request`: classify as `acquire` if this phase is
     intended to improve real timing evidence. It is the best primary path
     because it can support both headway and travel-time fields after review.
     It still lacks `data/rail/pilot_gtfs.zip` and a same-feed
     `data/rail/pilot_gtfs_validator_report.json`.
   - `rail_static_timetable_csv_headway_request`: classify as `pending`
     fallback. It can support headway only and still lacks reviewed static CSV,
     mapping, citation, and normalization manifest.
   - `rail_timetable_headway_request`: classify as `pending` fallback. It can
     support headway only and still lacks `DATA_GO_KR_KEY` or reviewed
     cache/raw payloads.
   - `rail_shortest_path_travel_time_request`: classify as `pending` fallback.
     It can support travel time only and still lacks `DATA_GO_KR_KEY` or
     reviewed cache/raw payloads.
   - No timing row should be treated as scenario-only. Timing rows may be
     sensitivity-only or excluded only if a reviewer explicitly chooses not to
     acquire timing evidence for the current phase.
2. Capacity and availability:
   - `rail_capacity_treatment_request`: currently `pending`; recommended
     bounded classification is `sensitivity-only` unless operator/literature
     capacity evidence is reviewed and retained with hashes.
   - `rail_availability_scenario_request`: currently `pending`; recommended
     bounded classification is `scenario-only` unless public disruption or
     availability evidence is acquired and reviewed.
   - Current stress-profile and bounded-treatment artifacts are enough for
     compact engineering tests only after this synthesis is recorded. They are
     not enough for publication readiness, rail evidence closure, final-study
     readiness, formal acceptance, or operational interpretation.
3. Overclaim and wording risk:
   - Readiness logic is conservative and still blocks publication/final-study
     readiness.
   - Ambiguous fields and wording can still be overread outside context:
     `rail_service_evidence_present`, `missing_decision_evidence_count`,
     `required_external_input_present_count`, and non-formal uses of
     `accept` or `acceptance` around bounded assumptions.
   - `status.md` should avoid saying rail is "operationally available"; use
     "scheduled-service proxy; not evidence of operational rail availability."

## Accepted Findings

- Timing evidence remains blocked by missing reviewed GTFS/timetable/
  shortest-path artifacts, not missing simulation code.
- Capacity and availability can be recorded as bounded non-formal decisions,
  but doing so still cannot close rail evidence, publication, final-study, or
  formal acceptance gates.
- The immediate implementation target is a wording and manifest overread guard,
  not an evidence artifact or simulation run.

## Rejected Or Deferred Findings

- Do not create formal acceptance artifacts.
- Do not treat source-context hashes, stress-profile coverage, or bounded
  treatment consistency as rail evidence.
- Do not start compact or full experiments from current proxy rail timing.
- Defer actual GTFS acquisition until a reviewed feed, validator report,
  station/route/window choices, citation, license/provenance, and retained
  SHA256 evidence are available.

## Scoped Implementation Target

Patch non-formal rail packet wording and manifest field names so future workers
cannot overread current rail review-support artifacts as evidence or acceptance:

- supplement or rename `rail_service_evidence_present` as
  `rail_service_evidence_artifact_present`;
- supplement or rename `missing_decision_evidence_count` as
  `missing_evidence_for_non_pending_actions_count`;
- supplement or rename `required_external_input_present_count` as
  `required_external_input_specified_count`;
- replace non-formal `accept`/`acceptance` wording for bounded rail treatments
  with `record reviewer-scoped bounded treatment` wording where it does not
  refer to formal acceptance;
- update `status.md` wording for rail availability proxy scope;
- preserve all existing false readiness and gate-support booleans.

## Tests Required After Patch

```powershell
.\.venv\Scripts\python tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_fetch_readiness_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_transit_stress_profile_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_bounded_treatment_audit.py
.\.venv\Scripts\python tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
```

## Implementation Result

Implemented the scoped overread guard after the explorer synthesis.

Edited source/test scope:

- `src/realworld/rail_source_decision_packet.py`
- `src/realworld/rail_fetch_readiness_packet.py`
- `src/realworld/rail_timing_request_packet.py`
- `src/realworld/rail_transit_stress_profile_packet.py`
- `status.md`
- `tests/test_realworld_rail_source_decision_packet.py`
- `tests/test_realworld_rail_fetch_readiness_packet.py`
- `tests/test_realworld_rail_transit_stress_profile_packet.py`

Generated and refreshed review-support artifacts:

- `data/rail/rail_timing_source_request_packet.csv`
- `data/rail/rail_timing_source_request_manifest.json`
- `data/rail/rail_fetch_readiness_packet.csv`
- `data/rail/rail_fetch_readiness_manifest.json`
- `data/rail/rail_evidence_priority_packet.csv`
- `data/rail/rail_source_decision_packet.csv`
- `data/rail/rail_source_decision_manifest.json`
- `data/rail/rail_transit_stress_profile_packet.csv`
- `data/rail/rail_transit_stress_profile_manifest.json`
- `data/rail/rail_bounded_treatment_audit.json`
- `docs/rail_fetch_readiness_packet.md`
- `docs/rail_evidence_priority_packet.md`
- `docs/rail_source_decision_packet.md`
- `docs/rail_transit_stress_profile_packet.md`
- `docs/rail_bounded_treatment_audit.md`
- acceptance orchestration and review-packet artifacts refreshed by
  `scripts/run_acceptance_audit.py`

Guard behavior added:

- `rail_service_evidence_artifact_present` now distinguishes local file
  existence from rail evidence acceptance or gate closure.
- `missing_evidence_for_non_pending_actions_count` now distinguishes
  incomplete non-pending action-ledger rows from pending reviewer decisions.
- `required_external_input_specified_count` now distinguishes named external
  input requirements from evidence presence.
- Bounded capacity and availability wording now uses reviewer-scoped treatment
  language instead of non-formal `accept` language where formal acceptance is
  not meant.
- Stress-profile Markdown now labels required stress-class coverage as
  coverage-only.
- `status.md` now describes rail as a scheduled-service proxy, not evidence of
  operational rail availability.

## Verification Result

Passed:

```powershell
.\.venv\Scripts\python tests\test_realworld_rail_timing_request_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_fetch_readiness_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_evidence_priority_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_transit_stress_profile_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_bounded_treatment_audit.py
.\.venv\Scripts\python tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python tests\test_realworld_acceptance_orchestration.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
```

Also reran:

```powershell
.\.venv\Scripts\python scripts\write_rail_timing_source_request_packet.py
.\.venv\Scripts\python scripts\write_rail_fetch_readiness_packet.py
.\.venv\Scripts\python scripts\write_rail_evidence_priority_packet.py
.\.venv\Scripts\python scripts\write_rail_source_decision_packet.py
.\.venv\Scripts\python scripts\write_rail_transit_stress_profile_packet.py
.\.venv\Scripts\python scripts\audit_rail_bounded_treatments.py
.\.venv\Scripts\python scripts\audit_publication_readiness.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
.\.venv\Scripts\python scripts\run_acceptance_audit.py
```

Stale rail overread patterns were checked with `rg` across `data`, `docs`,
`src`, `tests`, and `status.md`. No matches remained for the targeted rail
patterns:

- `retained rail capacity and availability assumptions require source-backed
  updates, sensitivity-only limits, scenario-only limits, or explicit
  acceptance`
- `explicit final sensitivity-only acceptance`
- `accept sensitivity-only capacity bounds`
- `accept scenario-only rail availability bounds`
- `not sensitivity-only rail acceptance`
- `Rail-service evidence present`
- `Required stress classes present:`

## Gate Decision After Patch

The overread guard patch is complete and verified, but Phase 4 remains blocked
for stronger rail claims. Missing items remain:

- reviewed `data/rail/pilot_gtfs.zip`;
- same-feed `data/rail/pilot_gtfs_validator_report.json`;
- reviewed timetable or shortest-path cache/raw payloads, or `DATA_GO_KR_KEY`
  plus reviewed live-fetch choices;
- reviewer-scoped capacity and availability source decisions;
- source-backed rail service evidence before publication, final-study, or
  formal acceptance gates can close.

Do not start compact or full experiments from the current proxy rail timing
unless the next phase explicitly records that it is an engineering-only compact
test with bounded proxy assumptions.
