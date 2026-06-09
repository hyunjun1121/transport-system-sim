# Phase 10 GPU ML Optional Requirements Ledger

## Objective

Make the Phase 10 post-simulation ML/GPU runtime preflight reproducible without
moving GPU dependencies into the core simulator dependency set.

This sprint does not make the simulator GPU-accelerated, does not validate ML
model quality, and does not close publication, final-study, or formal
acceptance gates.

## Evidence Reviewed

- `requirements.txt`
- `scripts/check_gpu_ml_runtime.py`
- `src/realworld/gpu_ml_runtime.py`
- `tests/test_realworld_gpu_ml_runtime.py`
- `docs/gpu_ml_runtime_check.md`
- `data/validation/gpu_ml_runtime_manifest.json`
- `plan.md`
- `status.md`
- `README.md`
- `agents.md`

Current package index probes on 2026-06-04 reported:

- `xgboost`: latest available version `3.2.0`
- `scikit-learn`: latest available version `1.9.0`

## Files Edited

- `requirements-ml.txt`
- `README.md`
- `agents.md`
- `plan.md`
- `status.md`
- `scripts/check_gpu_ml_runtime.py`
- `tests/test_realworld_gpu_ml_runtime.py`

## Generated Or Refreshed Outputs

- `data/validation/gpu_ml_runtime_manifest.json`
- `data/validation/gpu_ml_runtime_log.jsonl`
- `docs/gpu_ml_runtime_check.md`
- `data/validation/dirty_worktree_classification.csv`
- `data/validation/dirty_worktree_classification_manifest.json`
- `docs/dirty_worktree_classification.md`

## Key Hashes

- `requirements-ml.txt`:
  `8eb1cd2c5917ad4d42861c4580ccd00f09b9e6d63dccbfb6300cba67a589da15`
- `scripts/check_gpu_ml_runtime.py`:
  `0cb40bc78db00f04c64c14b8a3f95f001f1557b4fc324596a741c3aca161f1e1`
- `tests/test_realworld_gpu_ml_runtime.py`:
  `6e70d178f257d6cfa2665730ebc51959357470fd198a6114c7bc34e04fe5f262`
- `data/validation/gpu_ml_runtime_manifest.json`:
  `c6308a5cc4923f0efbcfc3a812435f7b766110df9334faad3719e6318c56e63a`
- `docs/gpu_ml_runtime_check.md`:
  `5e9511e4d52448abcef6196b7c46eab81284aeac69a66fac65bb17d092c74a1b`
- `README.md`:
  `493c2e0b0e11f383175d480709727437e194489279ed9abad699517494ff1bad`
- `agents.md`:
  `5f1f6f4a396cfd1d1e82df4124f51414316c297226c26732185cc57cf018eca3`
- `plan.md`:
  `f364f8bd92b057e9b3174d3acfd526a522717d6d5d873f63fb05ffb2f409abf6`
- `status.md`:
  `34c28203bb8a10e155c512f4ab0d9e8bf48eb6714fb80016ae4fd5df9acbabe5`

## Commands And Results

- `.\.venv\Scripts\python -m pip index versions xgboost`
  - passed; latest shown as `3.2.0`
- `.\.venv\Scripts\python -m pip index versions scikit-learn`
  - passed; latest shown as `1.9.0`
- `.\.venv\Scripts\python -m pip install -r requirements-ml.txt`
  - passed; installed `xgboost==3.2.0`, `scikit-learn==1.9.0`, and
    transitive dependencies
- `.\.venv\Scripts\python .\scripts\check_gpu_ml_runtime.py --package xgboost --requested-device cuda --requirements requirements-ml.txt --require-gpu`
  - passed
- `.\.venv\Scripts\python .\tests\test_realworld_gpu_ml_runtime.py`
  - passed
- `.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py`
  - passed after dirty classification refresh
- `.\.venv\Scripts\python -m py_compile .\src\realworld\gpu_ml_runtime.py .\scripts\check_gpu_ml_runtime.py .\tests\test_realworld_gpu_ml_runtime.py`
  - passed

## GPU Runtime Result

The refreshed manifest records:

- `nvidia_smi_available=true`
- GPU: NVIDIA GeForce RTX 3090, 24,576 MiB VRAM
- `package_name=xgboost`
- `package_version=3.2.0`
- `requested_device=cuda`
- `actual_device=cuda`
- `gpu_check_status=passed`
- `cpu_fallback_status=passed`
- `can_support_gpu_ml_claim=true`
- `gpu_ml_runtime_passed=true`
- `simulation_engine_gpu_accelerated=false`
- `publication_ready=false`
- `final_study_ready=false`
- `formal_acceptance_evidence=false`

## Self-Refine

The first successful GPU manifest did not record the exact CLI arguments used
for `--requirements requirements-ml.txt` and `--require-gpu`. The CLI command
capture was changed to record the actual argument vector, and a regression test
was added to verify exact command recording.

The first plan-audit rerun failed because dirty-worktree classification was
stale after edits and generated-output refresh. The dirty classification ledger
was regenerated and the plan-audit test passed.

## Remaining Blockers

- The bounded GPU result supports only post-simulation XGBoost/CUDA runtime
  wording for the active environment.
- It is not simulation acceleration evidence.
- It is not ML model-quality evidence.
- It does not close Phase 10, publication, final-study, reproducibility, or
  formal acceptance gates.
- Any future GPU wording still requires the latest manifest and claim-language
  guard review.

## Claim Boundary

The SimPy/NetworkX simulation remains CPU-based. The RTX 3090 can be used for
post-simulation ML and explainability only when package-specific runtime
evidence and CPU fallback evidence are present.
