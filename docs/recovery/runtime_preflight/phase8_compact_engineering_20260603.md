# Phase 8 Compact Engineering-Only Runtime Preflight

Date: 2026-06-03

Purpose: preflight for a bounded Phase 8 compact engineering-only pilot run.
This run is not publication evidence, not final-study evidence, not formal
acceptance evidence, and not an operational route plan or forecast.

## Planned Command

```powershell
.\.venv\Scripts\python .\scripts\run_pilot_experiments.py --staged --output-dir .\results\realworld_pilot\phase8_compact_engineering_20260603 --seeds 8201,8202,8203 --policy-ids bus_only,baseline_multimodal,multimodal_lastmile_redundancy --scenario-ids no_disruption,songpa_critical_link_blockage,songpa_last_mile_station_to_destination --engineering-only
```

## Output Policy

- Output directory:
  `results\realworld_pilot\phase8_compact_engineering_20260603`.
- `Test-Path` before launch returned `False`.
- Expected row count: 3 policies x 3 scenarios x 3 seeds = 27 result rows.
- Expected summary rows: 3 policies x 3 scenarios = 9 summary rows.
- Actual worker count: 1, because the current runner has no tested worker-count
  controller.
- GPU use: none for simulation. The SimPy/NetworkX runner remains CPU-based.
- Cleanup policy: no cleanup or deletion during this run. Generated files stay
  in the fresh output directory for audit.

## Blocking Context

- Rail source decisions remain pending.
- Artifact invalidation closeout remains unresolved.
- Therefore this compact run is allowed only with `--engineering-only`.
- It cannot promote Phase 9, close publication readiness, close final-study
  readiness, or support formal acceptance.

## Dirty Path Classification

`git status --short --branch` was inspected before launch. The worktree has many
modified and untracked files from earlier Phase 3 to Phase 8 recovery,
source-evidence, rail, validation, artifact-invalidation, and plan updates.
These are treated as active recovery/Phase evidence work, not as a clean
release state. No broad delete, clean, prune, or move operation is authorized by
this preflight.

Current Phase 8 touched paths for this run:

- `src/realworld/pilot_experiments.py`
- `tests/test_realworld_pilot_experiments.py`
- `docs/recovery/runtime_preflight/phase8_compact_engineering_20260603.md`
- planned generated output directory:
  `results/realworld_pilot/phase8_compact_engineering_20260603`

## Runtime Evidence

Python and package check:

```text
Python 3.12.10
No broken requirements found.
```

CPU:

```text
AMD Ryzen 7 5800X3D 8-Core Processor
NumberOfCores: 8
NumberOfLogicalProcessors: 16
```

RAM:

```text
TotalVisibleMemorySize: 33466472 KiB
FreePhysicalMemory: 15174824 KiB
```

GPU driver visibility:

```text
NVIDIA GeForce RTX 3090, 24576 MiB, driver 610.47, utilization 4 %, memory used 1413 MiB
```

Disk:

```text
C: used 732809388032 bytes, free 1266499981312 bytes
```

## Gate Decision

Proceed with a bounded engineering-only compact probe after narrow runner tests
pass. Do not treat the output as publication, final-study, Phase 9 promotion, or
formal acceptance evidence.
