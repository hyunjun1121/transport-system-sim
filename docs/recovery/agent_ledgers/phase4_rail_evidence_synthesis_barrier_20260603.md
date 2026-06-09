# Phase 4 Rail Evidence Synthesis Barrier - 2026-06-03

## Objective

Record the dependency barrier after the Phase 4 read-only sub-agent wave before
any further rail packet wording or source-decision edits. This barrier controls
the next write scope and keeps rail timing, capacity, and availability claims
blocked unless source-backed evidence or reviewer-scoped bounded decisions are
actually recorded.

## Local Evidence Checked

The main thread inspected the current rail source-decision packet, action-ledger
template, and required local artifact paths.

Current action-ledger state:

- `data/rail/rail_source_decision_action_ledger_template.csv` has six rows.
- Every row still has `decision_choice=pending_reviewer_decision`.

Current artifact presence:

- absent: `data/rail/pilot_gtfs.zip`;
- absent: `data/rail/pilot_gtfs_validator_report.json`;
- absent: `data/rail/pilot_rail_timetable_cache.csv`;
- absent: `data/rail/pilot_rail_timetable_raw.json`;
- absent: `data/rail/pilot_rail_timetable_static_source.csv`;
- absent: `data/rail/pilot_rail_timetable_cache_manifest.json`;
- absent: `data/rail/pilot_rail_shortest_path_cache.csv`;
- absent: `data/rail/pilot_rail_shortest_path_raw.json`;
- present: `data/rail/ktdb_gtfs_source_extract.csv`;
- present: `data/rail/ktdb_gtfs_notice_raw.html`;
- present: `data/rail/ktdb_gtfs_dataset_list_raw.html`;
- present: `data/rail/metro9_capacity_source_extract.csv`;
- present: `data/rail/metro9_capacity_source_raw.html`;
- present: `data/parameters/rail_service_evidence.csv`;
- present: `data/parameters/rail_assumptions.csv`;
- present: `data/scenarios/disruption_scenarios.csv`.

Current manifest state:

- `publication_ready=false`;
- `can_mark_complete=false`;
- `can_support_rail_evidence_gate=false`;
- `can_support_acceptance_gate=false`;
- `completed_source_decision_count=0`;
- `action_decision_status_counts={"pending_action_decision": 6}`;
- `rail_source_decision_recorded=false`.

## Sub-Agent Wave

All three agents were GPT-5.5 xhigh read-only explorers/reviewers. No agent was
assigned a write set.

### Rail Timing Evidence Explorer

Agent: `019e8a93-ea0a-7c02-a309-576e1a9f55bf`.

Findings:

- `rail_static_gtfs_timing_request`: pending; source-backed path requires
  reviewed `data/rail/pilot_gtfs.zip`, same-feed
  `data/rail/pilot_gtfs_validator_report.json`, reviewed stop/route/service
  choices, source citation, extraction date, and follow-on provenance and
  validation acceptance.
- `rail_static_timetable_csv_headway_request`: pending; source-backed path
  requires reviewed static timetable CSV, reviewed source-column mapping,
  normalization manifest, reviewed service-window/station choices, and
  retained raw/cache artifacts.
- `rail_timetable_headway_request`: pending; source-backed path requires
  `DATA_GO_KR_KEY` or reviewed cached API payload plus raw/cache retention.
- `rail_shortest_path_travel_time_request`: pending; source-backed path
  requires `DATA_GO_KR_KEY` or reviewed cached API payload plus raw/cache
  retention.

The existing `data/parameters/rail_service_evidence.csv` is present only as a
proxy/scaffold artifact and is not source-backed timing evidence.

### Rail Capacity And Availability Reviewer

Agent: `019e8a93-eaea-7e11-aabf-3e96625cbd9b`.

Findings:

- `rail_capacity_treatment_request` is not source-backed now. Cached Metro9
  context records capacity context, but the local model value remains a
  sensitivity-only proxy. Recommendation: retain only as sensitivity-only with
  bounds or exclude capacity-dependent final claims unless a reviewer records
  source-backed capacity evidence.
- `rail_availability_scenario_request` is not source-backed now. Current
  artifacts document scenario coverage only. Recommendation: retain only as
  scenario-only availability scope or exclude availability-dependent final
  claims unless public/operator availability evidence is acquired and reviewed.
- The current rail model remains a scheduled-service proxy, not calibrated rail
  operations.

### Claim-Boundary Reviewer

Agent: `019e8a93-eb99-7343-8203-fda930c88bde`.

Findings:

- No critical overclaim was found.
- Publication, final-study, rail-evidence, and formal-acceptance gates remain
  correctly blocked.
- Several phrases could be overread if copied without context:
  - `Rail-service evidence artifact present`;
  - `rail_station_binding_ready`;
  - `This closes station binding only`;
  - stress-class and bounded-treatment audit labels that could be mistaken for
    validation;
  - historical plan wording saying readiness tests passed without emphasizing
    that the audits remained blocked;
  - `Multimodal transport becomes competitive only when rail access and
    last-mile redundancy remain available`.

## Synthesis Decision

Do not start compact or full experiments from the current rail state except as
an explicitly labeled engineering-only compact test with bounded proxy rail
assumptions.

No source-backed rail timing, capacity, or availability row is available now.
The next write scope is limited to overread-hardening wording in generated
packet source, status text, plan text, and matching tests. The patch must not
change any readiness boolean, create `data/parameters/rail_service_evidence.csv`
from proxy data, create formal acceptance artifacts, or mark publication,
final-study, rail-evidence, or formal-acceptance gates ready.

## Required Verification After Wording Patch

Run narrow tests first:

```powershell
.\.venv\Scripts\python tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_transit_stress_profile_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_bounded_treatment_audit.py
.\.venv\Scripts\python tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
```

Regenerate affected packet docs and readiness audits if source generators
change.

## Gate Decision

Phase 4 rail source-evidence remains blocked. The barrier permits only a narrow
claim-boundary wording hardening patch.

## Wording Patch Result

Patched the narrow overread wording scope authorized by this barrier:

- `src/realworld/rail_source_decision_packet.py` now labels the local
  `rail_service_evidence.csv` file as a proxy/scaffold artifact for inspection
  and prints `Accepted source-backed rail-service evidence: false`.
- `src/realworld/publication_readiness.py` now states that
  `rail_station_binding_ready` is only an identifier-binding prerequisite and
  does not prove rail timing, capacity, availability, or operational service.
- `src/realworld/rail_transit_stress_profile_packet.py` now labels stress rows
  as coverage-taxonomy support only.
- `src/realworld/rail_bounded_treatment_audit.py` now labels mismatch counts as
  internal consistency checks only, not validation evidence.
- `src/realworld/integrated_evidence_review_packet.py` now reports
  `rail_service_evidence_artifact_present` and
  `accepted_source_backed_rail_service_evidence=false` instead of the
  overread-prone `rail_service_evidence_present=true` summary.
- `status.md` now says station binding satisfies only a prerequisite and that
  multimodal competitiveness depends on modeled scenarios where rail access and
  last-mile redundancy are assumed available or source-backed.
- `plan.md` now clarifies that GTFS Validator success is necessary before a
  reviewer may consider GTFS timing evidence source-backed, but validator
  success alone is not acceptance. It also clarifies that readiness test
  commands passed while the audits remained blocked.

Regenerated:

- `docs/rail_source_decision_packet.md`;
- `data/rail/rail_source_decision_packet.csv`;
- `data/rail/rail_source_decision_manifest.json`;
- `docs/rail_transit_stress_profile_packet.md`;
- `data/rail/rail_transit_stress_profile_packet.csv`;
- `data/rail/rail_transit_stress_profile_manifest.json`;
- `docs/rail_bounded_treatment_audit.md`;
- `data/rail/rail_bounded_treatment_audit.json`;
- `docs/integrated_evidence_review_packet.md`;
- `data/validation/integrated_evidence_review_packet.csv`;
- `data/validation/integrated_evidence_review_manifest.json`;
- `docs/publication_readiness_audit.md`;
- `data/manifests/publication_readiness_audit.json`;
- `docs/current_goal_completion_audit.md`;
- `data/manifests/current_goal_completion_audit.json`.

## Verification Result

Passed:

```powershell
.\.venv\Scripts\python -m py_compile src\realworld\rail_source_decision_packet.py src\realworld\publication_readiness.py src\realworld\rail_transit_stress_profile_packet.py src\realworld\rail_bounded_treatment_audit.py src\realworld\integrated_evidence_review_packet.py tests\test_realworld_rail_source_decision_packet.py tests\test_realworld_publication_readiness.py tests\test_realworld_rail_transit_stress_profile_packet.py tests\test_realworld_rail_bounded_treatment_audit.py tests\test_realworld_integrated_evidence_review_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_source_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_transit_stress_profile_packet.py
.\.venv\Scripts\python tests\test_realworld_rail_bounded_treatment_audit.py
.\.venv\Scripts\python tests\test_realworld_publication_readiness.py
.\.venv\Scripts\python tests\test_realworld_integrated_evidence_review_packet.py
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
```

Regeneration commands:

```powershell
.\.venv\Scripts\python scripts\write_rail_source_decision_packet.py
.\.venv\Scripts\python scripts\write_rail_transit_stress_profile_packet.py
.\.venv\Scripts\python scripts\write_integrated_evidence_review_packet.py
.\.venv\Scripts\python scripts\audit_rail_bounded_treatments.py
.\.venv\Scripts\python scripts\audit_publication_readiness.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
```

Targeted stale-pattern search across active docs/status/plan and the integrated
review CSV, excluding `docs/recovery/**`, returned no matches for the old
overread-prone phrases:

- `Rail-service evidence artifact present`;
- `Required structural stress classes present`;
- `Mismatches:`;
- `publication and final-study readiness tests passed`;
- `Use GTFS Validator before GTFS-derived evidence is accepted`;
- `This closes station binding only`;
- `Multimodal transport becomes competitive only when rail access and last-mile redundancy remain available`;
- `rail_service_evidence_present=true`.

## Gate Decision After Patch

No readiness gate changed. Rail evidence, publication readiness, final-study
readiness, and formal acceptance remain blocked. The next Phase 4 work remains
real rail/transit evidence acquisition or explicit reviewer-scoped exclusion
and bounded-treatment decisions.
