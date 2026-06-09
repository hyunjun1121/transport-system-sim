# Evidence Candidate Rollup - 2026-06-08

## Scope

This ledger records the post-candidate audit state after adding the non-formal
road override source candidate and non-formal static rail-service candidate.
These artifacts support reviewer triage only. They do not close publication,
final-study, phase-gate, or formal acceptance gates.

## Candidate Packets Added

- `data/parameters/road_class_override_source_candidate.csv`
- `data/parameters/road_class_override_source_candidate_manifest.json`
- `docs/road_class_override_source_candidate.md`
- `data/rail/rail_service_evidence_static_candidate.csv`
- `data/rail/rail_service_evidence_static_candidate_manifest.json`
- `docs/rail_service_evidence_static_candidate.md`

Implementation and test files were added for both candidate packets under
`src/realworld/`, `scripts/`, and `tests/`.

## Provenance Traceability Update

After candidate packet generation, `data/manifests/source_provenance_manifest.json`
and `docs/source_provenance_manifest.md` were updated to list the new
candidate-only road and rail artifacts under the repository parameter/source
review row. This is traceability only. It does not change review status,
publication readiness, final-study readiness, or formal acceptance.

## Reviewer Model Evidence Used

Four read-only sub-agent reviewers were used before and during implementation:

- `019ea5f2-5c9a-7d71-af8f-63e1bbbfa35c`: road evidence/provenance review.
- `019ea5f2-8f31-7a30-a94f-32675b0c437c`: road claim-boundary review.
- `019ea5fb-4bba-7d30-8086-e40bb26c5440`: rail evidence/provenance review.
- `019ea5fb-883b-7673-b0ec-f12cd147527b`: rail claim-boundary review.

All four reviewers supported candidate-only artifacts and rejected formal gate
closure from the current evidence.

## Commands Run

```powershell
.\.venv\Scripts\python scripts\write_road_class_override_source_candidate.py
.\.venv\Scripts\python tests\test_realworld_road_override_source_candidate.py
.\.venv\Scripts\python tests\test_realworld_road_override_audit.py
.\.venv\Scripts\python tests\test_realworld_road_overrides.py
.\.venv\Scripts\python tests\test_realworld_road_source_readiness_packet.py
.\.venv\Scripts\python scripts\audit_road_overrides.py

.\.venv\Scripts\python scripts\write_rail_service_static_candidate.py
.\.venv\Scripts\python tests\test_realworld_rail_service_static_candidate.py
.\.venv\Scripts\python tests\test_realworld_rail_evidence.py
.\.venv\Scripts\python tests\test_realworld_rail_static_timetable_segment_pair_diagnostic.py
.\.venv\Scripts\python tests\test_realworld_rail_timetable_static.py
.\.venv\Scripts\python scripts\audit_rail_evidence.py

.\.venv\Scripts\python scripts\audit_publication_readiness.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
.\.venv\Scripts\python scripts\write_phase_gate_ledgers.py
.\.venv\Scripts\python tests\test_realworld_source_provenance.py
.\.venv\Scripts\python scripts\audit_source_provenance.py --fail-on-blockers
.\.venv\Scripts\python scripts\audit_claim_language.py --scan-path data\manifests\source_provenance_manifest.json --scan-path docs\source_provenance_manifest.md --scan-path docs\recovery\agent_ledgers\evidence_candidate_rollup_20260608.md --fail-on-blockers
.\.venv\Scripts\python scripts\audit_plan_artifacts.py
```

## Audit Results

- Targeted road and rail tests passed.
- `scripts\write_phase_gate_ledgers.py` reported:
  - `all_expected_phase_ledgers_present=true`
  - `all_expected_phase_ledgers_valid=true`
  - `closed_phase_count=0`
  - `gate_decision_counts={"blocked":2,"ready_for_review":11}`
  - `can_mark_complete=false`
  - `final_study_ready=false`
- `scripts\audit_plan_artifacts.py` completed with blocked status and reported:
  - `all_required_artifacts_present=true`
  - `publication_ready=false`
  - `final_study_ready=false`
  - `phase_gate_ledgers_ready=false`
  - `closed_phase_count=0`
  - `blocking_change_count=538`
  - `untracked_count=165`
  - verdict `executable_quasi_real_scaffold_not_final_calibrated_study`
- `scripts\audit_source_provenance.py --fail-on-blockers` passed after
  provenance traceability was updated:
  - `diagnostics_ready=true`
  - `record_count=11`
  - `local_artifact_count=66`
  - `missing_local_artifact_paths=[]`
  - `remaining_blockers=[]`
- Focused `scripts\audit_claim_language.py` over the updated provenance
  manifest, source-provenance doc, and this rollup ledger passed:
  - `blocking_finding_count=0`
  - `claim_language_guard_ready=true`
  - `release_blocked=false`

## Gate Impact

- Promoted phases: none.
- Closed phases: none.
- Closed gates: none.
- Publication readiness: still blocked.
- Final-study readiness: still blocked.
- Formal acceptance: not created.

## Remaining High-Value Blockers

- Formal reviewed road override table is absent.
- Road speed, capacity, and base-disruption values remain insufficient for
  release-scope evidence statements.
- Formal rail service evidence remains a documented assumption proxy.
- Rail source decisions, travel-time evidence, transfer-buffer evidence, and
  capacity evidence remain pending.
- Parameter evidence remains weak for demand, fleet, disruption, transfer,
  time-horizon, and censoring assumptions.
- Dirty/untracked worktree classification remains a reproducibility blocker.

## Next Dependency-Safe Work

Continue with source-provenance and parameter-source triage that is explicitly
candidate-only or review-support only. Do not write formal acceptance targets or
rerun Phase 9 full experiments until upstream road, rail, parameter,
provenance, validation, graph-scale, and artifact-invalidation blockers are
resolved.
