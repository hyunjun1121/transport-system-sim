# Phase 0 Forward Baseline Results - 2026-06-02

## Scope

This record captures the Phase 0 baseline check required by `plan.md` before
new real-world simulation implementation work begins.

## Worktree Safety

Command:

```powershell
git status --short --branch
```

Observed result:

```text
## main...origin/main
 M plan.md
```

Interpretation:

- No unexpected tracked deletions were visible.
- The only tracked dirty file at this checkpoint was `plan.md`.

Command:

```powershell
git log -1 --oneline
```

Observed result:

```text
0faedef2 docs: add recovery goal completion audit
```

## Recovery Artifact Check

`docs/recovery/` was present and contained the recovery audit, current-state
inventory, integrity audit, reconstruction matrix, test ladder results, and
baseline bundle records created on 2026-06-02.

## Environment Restoration

The project virtual environment was absent at the start of this checkpoint:

```powershell
Test-Path .\.venv\Scripts\python.exe
```

Observed result:

```text
False
```

The virtual environment was recreated with Python 3.12:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt
```

Installation completed successfully. `.venv/` is ignored by `.gitignore`.

## Minimal Smoke Tests

### `.\.venv\Scripts\python tests\test_config.py`

Result: pass.

Observed checks:

- operational namespaces exist;
- failure-rate levels are multipliers;
- network variants are declared and routable;
- failure sensitivity levels are explicit;
- legacy keys remain available;
- operational values are in valid ranges.

### `.\.venv\Scripts\python tests\test_scenario.py`

Result: pass.

Observed checks:

- origin schedule defaults;
- explicit first departures;
- strict and grace dispatch behavior;
- fleet overlap behavior;
- fixed-headway rail behavior;
- finite last-mile fleet behavior;
- censoring and penalized KPI exposure.

### `.\.venv\Scripts\python main.py --test`

Result: pass.

Observed output summary:

- abstract seven-node network built;
- bus-only completed 1,000 of 1,000 passengers;
- multimodal completed 1,000 of 1,000 passengers;
- bus-only completion rate: `1.0`;
- multimodal completion rate: `1.0`;
- bus-only penalized makespan: `645.029769019392`;
- multimodal penalized makespan: `675.0291392474074`;
- reported delta makespan: `-30.00 min`.

## Interpretation

The restored root-level simulator is executable for the Phase 0 abstract-network
smoke path. This does not prove real-world calibration, full-study readiness,
or recovery of previously missing untracked event-transport artifacts.

## Next Gate

Proceed to Phase 1 region and scenario registry inspection only after preserving
this baseline result.
