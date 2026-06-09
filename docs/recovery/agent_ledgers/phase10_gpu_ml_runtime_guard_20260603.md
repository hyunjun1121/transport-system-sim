# Phase 10 GPU ML Runtime Guard Ledger - 2026-06-03

## Objective

Implement a bounded GPU ML runtime preflight guard so the project can separate
three claims:

1. the workstation exposes an NVIDIA GPU;
2. an optional Python ML package actually used CUDA for a package-specific
   runtime check;
3. the SimPy/NetworkX simulation engine itself is GPU accelerated.

Only item 2 can support a bounded post-simulation GPU ML claim. Item 3 remains
false.

## Sub-Agent Review Wave

- Rawls (`019e8b68-a831-7652-b19d-5772665c7d82`): read-only GPU/ML
  methodology reviewer. Required package-specific CUDA proof, package versions,
  `pip check`, `nvidia-smi`, CPU fallback, fail-closed status, and explicit
  non-acceptance flags.
- Euler (`019e8b68-f054-7662-9c0e-c15993703320`): read-only CLI/test
  integration reviewer. Recommended a thin script wrapper, implementation logic
  under `src/realworld/`, deterministic tests without requiring a physical GPU,
  generated JSON/JSONL/Markdown outputs, and no default CPU simulation
  dependency on GPU packages.

## Files Added Or Updated

- `src/realworld/gpu_ml_runtime.py`
- `scripts/check_gpu_ml_runtime.py`
- `tests/test_realworld_gpu_ml_runtime.py`
- `data/validation/gpu_ml_runtime_manifest.json`
- `data/validation/gpu_ml_runtime_log.jsonl`
- `docs/gpu_ml_runtime_check.md`
- `plan.md`
- `status.md`
- `agents.md`

## Current Runtime Evidence

The generated manifest at `data/validation/gpu_ml_runtime_manifest.json`
records:

- `nvidia_smi_available=true`
- `pip_check_passed=true`
- `python_version=3.12.10`
- checked package: `xgboost`
- `package_version=not_installed`
- `can_support_gpu_ml_claim=false`
- `gpu_ml_runtime_passed=false`
- `cpu_fallback_recorded=false`
- `simulation_engine_gpu_accelerated=false`
- `simulation_correctness_blocked=false`

Interpretation: the RTX 3090 is visible through driver evidence, but the active
Python environment does not currently support a GPU-backed ML claim because the
selected ML package is absent. CPU simulation correctness is not blocked.

## Commands Run

```powershell
.\.venv\Scripts\python -m py_compile src\realworld\gpu_ml_runtime.py scripts\check_gpu_ml_runtime.py tests\test_realworld_gpu_ml_runtime.py
.\.venv\Scripts\python scripts\check_gpu_ml_runtime.py --help
.\.venv\Scripts\python tests\test_realworld_gpu_ml_runtime.py
.\.venv\Scripts\python scripts\check_gpu_ml_runtime.py
```

Observed result: all compile/test/help commands passed. The runtime preflight
command completed and wrote a fail-closed manifest because `xgboost` is not
installed.

## Remaining Blockers

- GPU-backed ML claims remain blocked until an intended package is installed in
  the active venv and the guard records both confirmed CUDA use and CPU
  fallback.
- The guard is not publication readiness, final-study readiness, formal
  acceptance, ML model-quality evidence, or simulation acceleration evidence.
- Phase 9 artifact-invalidation closeout remains separately blocked and is not
  affected by this Phase 10 runtime guard.
