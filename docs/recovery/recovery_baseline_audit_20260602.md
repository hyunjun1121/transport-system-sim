# Recovery Baseline Audit - 2026-06-02

Generated: 2026-06-02 15:59:13 +09:00

## Purpose

This audit records the current recovery baseline after the local workspace loss
and restore event. It separates what is currently usable from what remains
missing or must be regenerated.

## Current Verified Baseline

The current repository root remains the authoritative simulation codebase for
now. The previously discussed `transport_simulation_core/` directory is absent,
but the reconstruction matrix shows that most prior `transport_simulation_core/`
source/test paths map to tracked root-level equivalents.

Current evidence:

- `docs/recovery/current_git_state_20260602.md`
- `docs/recovery/current_path_inventory_20260602.csv`
- `docs/recovery/high_risk_path_check_20260602.csv`
- `docs/recovery/transport_core_reconstruction_matrix_20260602.csv`
- `docs/recovery/transport_core_reconstruction_decision_20260602.md`

## Present-File Integrity

The active-scope integrity audit reports zero failures after correcting four
rail schema Markdown strings that contained replacement-character corruption.

Evidence:

- `docs/recovery/present_file_integrity_audit_20260602.md`
- `docs/recovery/present_file_integrity_failures_20260602.csv`
- `docs/recovery/present_file_integrity_notes_20260602.csv`

Corrected files:

- `docs/schemas/rail_shortest_path_cache_schema.md`
- `docs/schemas/rail_timetable_cache_schema.md`
- `.tmp_intake_list/docs/rail_shortest_path_cache_schema.md`
- `.tmp_intake_list/docs/rail_timetable_cache_schema.md`

## Smoke-Test Baseline

The restored root-level committed simulator passed narrow smoke checks. These
checks prove only that the current root simulator can run its abstract-network
smoke path; they do not prove recovery of missing untracked real-world or
event-transport work.

Evidence:

- `docs/recovery/test_ladder_results_20260602.md`

Recorded passing commands:

- `py -3 tests\test_config.py`
- `py -3 tests\test_scenario.py`
- `py -3 main.py --test`

## Confirmed Missing or Unavailable Work

The following remain absent in the current workspace:

- `transport_simulation_core/` as an exact folder path
- `국방AI_활용_아이디어_경연대회/2026 철도·교통·물류 대국민 아이디어 공모/`
- event-transport scripts, results, and generated figures
- `results/realworld/`
- `results/ai_analysis/`
- old generated `transport_simulation_core/outputs/runs/gate2_20260601_232844/`
  artifacts

The prior path evidence in session logs proves that some missing paths existed
earlier, but it does not preserve file contents.

Evidence:

- `docs/recovery/log_evidence_prior_path_inventory_20260602.md`
- `docs/recovery/log_evidence_prior_path_inventory_20260602.csv`
- `docs/recovery/loss_scope_summary_20260602.md`
- `docs/recovery/loss_scope_matrix_20260602.csv`

## Candidate Recovery Search

Candidate folders were inspected without copying them into the repository.
No direct filesystem backup copy of the missing event-transport target files was
found.

Evidence:

- `docs/recovery/recovery_candidate_inventory_20260602.csv`
- `docs/recovery/recovery_candidate_summary_20260602.md`
- `docs/recovery/additional_candidate_check_20260602.md`

Decision:

- Do not copy `C:\project\contest*` into this repository as recovery material.
- Do not recreate generated outputs from filenames alone.

## Reconstruction Decisions

Recovery should proceed from the decision register:

- `docs/recovery/reconstruction_decision_register_20260602.md`
- `docs/recovery/reconstruction_decision_register_20260602.csv`

Immediate rules:

1. Keep the repository root as the simulation source of truth.
2. Do not bulk-recreate `transport_simulation_core/`.
3. Rebuild only specific missing non-equivalent files if they remain required.
4. Treat missing generated results as unavailable until regenerated from
   verified scripts and inputs.
5. If the event-transport contest work is still needed, rebuild the pipeline
   and rerun compact/audit/figure steps before using any result claims.

## Current Worktree Preservation Set

Tracked modified files expected in this recovery baseline:

- `plan.md`
- `docs/schemas/rail_shortest_path_cache_schema.md`
- `docs/schemas/rail_timetable_cache_schema.md`
- `.tmp_intake_list/docs/rail_shortest_path_cache_schema.md`
- `.tmp_intake_list/docs/rail_timetable_cache_schema.md`

Untracked recovery artifacts expected:

- all files under `docs/recovery/`

## Baseline Archive

A compact recovery archive was created after this audit baseline:

- `docs/recovery/recovery_baseline_bundle_20260602.zip`
- `docs/recovery/recovery_baseline_bundle_manifest_20260602.md`

Verification:

- ZIP open check: `zip_entries=24`
- SHA256 manifest check: `sha256_match=true`

## Completion Status

Recovery planning and baseline classification are now substantially complete.
Full recovery is not complete because missing untracked event-transport and
generated experiment artifacts have not been recovered or regenerated.

The next safe action is to preserve this recovery baseline in version control or
an archive, then decide whether to rebuild the event-transport pipeline or leave
it unavailable.
