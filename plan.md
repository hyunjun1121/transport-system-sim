# Recovery and Rebuild Plan After Local Workspace Loss

## Purpose

This plan controls the recovery work after the local
`C:\project\transport-system-sim` workspace was emptied and later restored.

The immediate objective is not to continue experiments blindly. The objective is
to determine exactly what is present, what is missing, what is corrupt, what can
be recovered, and what must be regenerated. All later work must follow this
plan until the repository and experiment artifacts are trustworthy again.

## Current Working Assumption

The current repository appears to be restored to a clean Git state from
`origin/main`, but recent local work that was not committed may be missing.

Known high-risk missing areas:

- `transport_simulation_core/`
- recent real-world simulation upgrade work
- event-transport contest folder:
  `국방AI_활용_아이디어_경연대회/2026 철도·교통·물류 대국민 아이디어 공모/`
- event transport scripts and outputs
- generated event transport figures
- `results/realworld/`
- `results/ai_analysis/`
- untracked logs, caches, manifests, and run artifacts

Known currently preserved areas must still be checked before use:

- Git-tracked source files
- Git-tracked tests
- Git-tracked data and result files
- KCI materials
- defense AI competition materials
- web demo files
- document and image artifacts

## Execution Status as of 2026-06-02 15:05 KST

Completed evidence-producing steps:

- Phase 0 baseline created under `docs/recovery/`.
- Phase 1 high-risk path and loss-scope matrix created under `docs/recovery/`.
- Phase 2 present-file integrity audit completed.
- Rail schema Markdown text corruption found and corrected in:
  - `docs/schemas/rail_shortest_path_cache_schema.md`
  - `docs/schemas/rail_timetable_cache_schema.md`
  - `.tmp_intake_list/docs/rail_shortest_path_cache_schema.md`
  - `.tmp_intake_list/docs/rail_timetable_cache_schema.md`
- Active-scope integrity audit rerun after the fixes:
  - Python compile failures: 0
  - JSON failures: 0
  - CSV failures: 0
  - YAML failures: 0
  - text failures: 0
  - PNG failures: 0
  - DOCX failures: 0
  - PDF failures: 0
  - ZIP failures: 0
- `web_demo/tsconfig*.json` files are treated as valid TypeScript JSONC
  configs rather than strict JSON files.
- Minimal current-root smoke checks passed:
  - `py -3 tests\test_config.py`
  - `py -3 tests\test_scenario.py`
  - `py -3 main.py --test`

Current confirmed missing work:

- `transport_simulation_core/` is still absent.
- The event-transport contest folder is still absent.
- Event transport scripts/results/figures are still absent.
- No direct filesystem backup copy of those newest missing files has been found
  yet.
- Additional `C:\project\contest*` candidate folders were checked by targeted
  filename search. They did not contain the missing event-transport target
  files and must not be copied into this repository as recovery sources.

Useful recovery evidence:

- `docs/recovery/log_evidence_prior_path_inventory_20260602.csv` records 205
  prior file paths found in Codex session logs after normalizing noisy
  `path:line:text` search-result snippets. The evidence includes missing
  `transport_simulation_core/` paths and missing event-transport contest paths.
- The log evidence proves those paths existed in an earlier workspace listing;
  it does not preserve file contents.
- `docs/recovery/transport_core_reconstruction_decision_20260602.md` maps
  prior `transport_simulation_core/` paths to current root-level equivalents.
  It finds that most reusable source/test equivalents are already present at
  the repository root, while 6 compact non-arrival scripts/tests, 2
  document/input files, and 13 generated artifacts remain missing without root
  equivalents.
- `docs/recovery/reconstruction_decision_register_20260602.md` and
  `docs/recovery/reconstruction_decision_register_20260602.csv` convert the
  recovery audit into specific use/rebuild/regenerate decisions.
- `docs/recovery/additional_candidate_check_20260602.md` records the targeted
  inspection of external `C:\project\contest*` candidate folders.
- `docs/recovery/recovery_baseline_audit_20260602.md` records the current
  verified baseline, remaining missing artifacts, and immediate recovery
  decision.
- `docs/recovery/recovery_baseline_bundle_20260602.zip` and
  `docs/recovery/recovery_baseline_bundle_manifest_20260602.md` preserve the
  recovery plan, recovery evidence, and rail schema fixes as a small baseline
  archive.

Immediate next step:

Do not bulk-recreate `transport_simulation_core/` as a second copy of the
repository. Treat the current root repository as the authoritative simulation
core unless a specific missing file has no root equivalent. If the event
transport contest artifacts have already been submitted or abandoned, do not
prioritize their reconstruction. If they remain needed, regenerate them from
verified scripts and fresh outputs rather than claiming old missing results.

Current execution queue:

1. Preserve the recovery baseline:
   - review and commit `plan.md`, the rail schema text fixes, and
     `docs/recovery/` evidence artifacts.
   - baseline archive has been created under `docs/recovery/`; version-control
     commit remains the next preservation step.
2. Decide active recovery scope:
   - if event-transport contest artifacts are no longer needed, mark them as
     unavailable and do not rebuild them;
   - if they are still needed, rebuild the event pipeline from verified scripts
     and rerun compact/audit/figure steps before using any result claims.
3. For reusable simulation work, keep the repository root as the source of
   truth and only recreate missing non-equivalent compact non-arrival
   scripts/tests if that research scope remains required.
4. Do not rerun or cite full-scale generated outputs until:
   - inputs exist;
   - scripts exist;
   - compact profile passes;
   - audit script passes;
   - command logs and row counts are recorded.

## Non-Negotiable Safety Rules

1. Do not run destructive commands while recovery is active.
2. Do not overwrite restored files until they are audited.
3. Do not treat Git-clean state as proof that local experiment artifacts were
   preserved.
4. Do not rerun full experiments before input scripts, manifests, and output
   paths are verified.
5. Do not edit recovered candidate files in place. Copy them into a quarantine
   or staging area first.
6. Do not claim a file was read, checked, validated, or recovered unless there
   is command output or file evidence.
7. Prefer read-only inspection first, then staged reconstruction, then tests,
   then commit.

## Recovery Artifacts Already Found

Recovery reports under `C:\project`:

- `recovery_top_summary_20260602.csv`
- `recovery_final_top_status_20260602.csv`
- `recovery_processed_repo_status_20260602.csv`
- `recovery_attach_small_results_20260602.csv`
- `recovery_large_git_results_20260602.csv`
- `recovery_additional_same_name_results_20260602.csv`
- `recovery_empty_dirs_20260602.csv`
- `recovery_git_dirs_20260602.csv`
- `recovery_clone_empty_results_20260602.csv`
- `recovery_large_copy_results_20260602.csv`

External or auxiliary evidence locations:

- `C:\Users\mnb92\.codex\sessions\2026\06\01`
- `C:\Users\mnb92\.codex\sessions\2026\06\02`
- `C:\Users\mnb92\.gemini\antigravity-cli\brain`
- `C:\Users\mnb92\Downloads`
- `C:\Users\mnb92\AppData\Local\Temp`
- `C:\tss99a63fe6`
- `C:\tsscc`
- `C:\tsssrc40469350`

## Phase 0: Freeze and Baseline

Goal: establish a reliable current-state baseline before changing anything
else.

Actions:

1. Record Git state:
   - branch
   - HEAD commit
   - remote URL
   - dirty status
   - deleted/modified tracked files
   - `git fsck` result
2. Record top-level directory inventory:
   - file count
   - byte count
   - top-level directories
   - last-write timestamps
3. Record high-risk path existence:
   - `transport_simulation_core/`
   - event contest folder
   - event transport scripts
   - event transport final text
   - final generated event figures
   - `results/realworld/`
   - `results/ai_analysis/`
4. Save all baseline outputs under:

```text
docs/recovery/
```

Expected artifacts:

- `docs/recovery/current_git_state_20260602.md`
- `docs/recovery/current_path_inventory_20260602.csv`
- `docs/recovery/high_risk_path_check_20260602.csv`

Go/no-go:

- Go if current tracked files are internally consistent.
- Stop if Git object integrity fails or tracked files are missing.

## Phase 1: Determine Loss Scope

Goal: separate preserved, missing, corrupt, and unknown artifacts.

Classification labels:

- `PRESENT_TRACKED`: exists and is tracked by Git.
- `PRESENT_UNTRACKED`: exists but is not tracked.
- `MISSING_TRACKED`: expected by Git but absent.
- `MISSING_UNTRACKED`: known from logs or prior work but absent from Git.
- `POSSIBLY_RECOVERABLE`: absent from current workspace but present in logs,
  temp folders, backups, downloads, or candidate copies.
- `REGENERABLE`: absent but can be recreated by scripts.
- `CORRUPT_OR_UNREADABLE`: exists but cannot be opened or parsed.
- `UNKNOWN`: evidence is insufficient.

Actions:

1. Compare current Git-tracked inventory against `git status` and `git ls-files`.
2. Search current workspace for recent known artifact names.
3. Search recovery CSV files for candidate locations.
4. Search Codex/Gemini logs for:
   - paths written
   - scripts created
   - commands run
   - output row counts
   - final filenames
5. Search candidate backup/temp folders for:
   - `transport_simulation_core`
   - `철도물류_이벤트수송_최종본.txt`
   - `run_event_realworld_simulation.py`
   - `event_transport_summary.csv`
   - `event_route_context_map.png`
   - `event_arrival_guarantee_heatmap.png`
   - `event_ai_risk_or_bottleneck.png`
6. Produce a loss matrix.

Expected artifact:

- `docs/recovery/loss_scope_matrix_20260602.csv`
- `docs/recovery/loss_scope_summary_20260602.md`

Go/no-go:

- Go if each important path has a classification and evidence source.
- Stop if we cannot distinguish missing untracked work from intentionally absent
  work.

## Phase 2: Integrity Audit of Present Files

Goal: identify files that exist but are broken, partial, or stale.

Actions:

1. Python source check:
   - compile all tracked Python files
   - identify syntax failures
2. Text and Markdown check:
   - open key `.md` and `.txt` files
   - check for zero-byte files
   - check for replacement-character or encoding failures
3. CSV/JSON/YAML check:
   - parse key structured files
   - check row counts for important result tables
   - validate known manifests when scripts exist
4. Binary artifact check:
   - verify `.png` dimensions can be read
   - verify `.docx` opens as zip/docx
   - verify `.pdf` has nonzero pages when possible
5. Record all failures.

Expected artifacts:

- `docs/recovery/present_file_integrity_audit_20260602.md`
- `docs/recovery/present_file_integrity_failures_20260602.csv`

Go/no-go:

- Go if current tracked repo is readable enough to rebuild.
- Stop if source, data, or document corruption affects core execution.

## Phase 3: Recovery Candidate Inspection

Goal: inspect candidate copies without modifying the current repo.

Actions:

1. Inspect candidate directories:
   - `C:\tss99a63fe6`
   - `C:\tsscc`
   - `C:\tsssrc40469350`
   - relevant `Temp` clean-checkout and handoff directories
2. For each candidate:
   - count files
   - list top-level directories
   - determine Git state if `.git` exists
   - search for missing high-risk paths
   - compute selected file hashes
3. If a candidate has useful files, copy them to:

```text
recovery_staging/
```

Do not merge them into the repo yet.

Expected artifacts:

- `docs/recovery/recovery_candidate_inventory_20260602.csv`
- `docs/recovery/recovery_candidate_summary_20260602.md`
- staged candidate files under `recovery_staging/` if found

Go/no-go:

- Go if candidates are clearly old, irrelevant, or useful.
- Stop if a candidate is likely newer than current repo and must be preserved
  before any further work.

## Phase 4: Reconstruct or Regenerate Missing Work

Goal: rebuild important missing work in controlled order.

Priority order:

1. Restore or recreate `transport_simulation_core/` if it remains required.
2. Restore or recreate the event transport contest folder if it remains needed.
3. Restore or recreate real-world event simulation scripts.
4. Restore or recreate event simulation input tables.
5. Restore or recreate simulation outputs.
6. Restore or recreate generated figures.
7. Restore or recreate final contest text only after outputs and figures are
   coherent.

Allowed sources:

- Git commits and branches
- recovered candidate folders
- Codex/Gemini logs
- existing root-level source files
- existing `src/`, `scripts/`, `tests/`, `data/`, and `results/`
- rerun commands after scripts and inputs are verified

Expected artifacts:

- reconstructed files in their intended paths
- `docs/recovery/reconstruction_log_20260602.md`
- `docs/recovery/reconstructed_artifact_manifest_20260602.csv`

Go/no-go:

- Go only after reconstructed files pass integrity checks.
- Do not claim recovered experiment results unless they are traceable to actual
  output files or rerun logs.

## Phase 5: Minimal Test Ladder

Goal: prove the restored repository is runnable.

Run in this order:

1. `git status --short --branch`
2. `git fsck --full --no-progress`
3. Python syntax compile on active source tree
4. Core smoke tests:
   - `tests/test_config.py`
   - `tests/test_scenario.py`
   - `main.py --test`
5. Focused real-world tests if relevant files exist:
   - realworld adapter tests
   - OSM/OSRM manifest tests
   - pilot experiment tests
6. Event transport tests if event folder is restored:
   - input builder
   - simulation runner compact profile
   - figure generation
   - audit script

Expected artifacts:

- `docs/recovery/test_ladder_results_20260602.md`
- command logs with exit codes

Go/no-go:

- Go if tests cover the restored work.
- Stop if tests only cover old code while reconstructed artifacts remain
  untested.

## Phase 6: Reproducibility and Artifact Lock

Goal: prevent the same loss from happening again.

Actions:

1. Move critical generated artifacts into tracked or explicitly archived paths.
2. Add important reproducibility logs under `docs/recovery/`.
3. Add a manifest for any ignored but important artifacts.
4. Create a backup zip of the restored workspace state.
5. Commit recovery plan, audits, and restored files.
6. Push the commit only after reviewing the diff.

Expected artifacts:

- `docs/recovery/recovery_completion_audit_20260602.md`
- `recovery_submission_bundle_20260602.zip` or equivalent archive
- Git commit containing the recovery state

Go/no-go:

- Go if recovery state is committed and important artifacts are no longer only
  local ephemeral files.
- Stop if large ignored artifacts remain essential but unarchived.

## Phase 7: Resume Real-World Simulation Work

Resume research work only after recovery is stable.

Next research direction:

- keep the current simulator as a decision-support framework;
- move toward OSM/OSRM/GTFS-backed quasi-real simulation;
- use compact and medium tests before full runs;
- keep all run outputs under run-scoped directories;
- use manifests, checksums, and command logs for every experiment;
- commit scripts and source-controlled evidence before running expensive full
  experiments.

Do not resume full-scale experiments until:

- the recovery audit is complete;
- current inputs are verified;
- output paths are safe;
- compact profile passes;
- generated figures are traceable;
- final text claims match audited outputs.

## Immediate Next Commands

The orchestrator should now run Phase 0 and Phase 1 checks:

```powershell
git status --short --branch
git fsck --full --no-progress
git ls-files --deleted
git ls-files --modified
rg --files
```

Then create:

```text
docs/recovery/current_git_state_20260602.md
docs/recovery/current_path_inventory_20260602.csv
docs/recovery/high_risk_path_check_20260602.csv
docs/recovery/loss_scope_matrix_20260602.csv
docs/recovery/loss_scope_summary_20260602.md
```

All subsequent work should proceed from those evidence files.
