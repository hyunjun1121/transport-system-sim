# GPU ML Runtime Check

GPU ML runtime preflight only; not simulation acceleration evidence, not ML model-quality evidence, not publication readiness, not final-study approval, and not formal acceptance.

## Verdict

- GPU ML runtime passed: `true`
- Can support GPU ML claim: `true`
- CPU fallback recorded: `true`
- Simulation engine GPU accelerated: `false`
- NVIDIA SMI available: `true`

## Package Results

| Package | Version | Requested | Actual | Import | GPU Check | CPU Fallback | Claim Support |
| --- | --- | --- | --- | --- | --- | --- | --- |
| xgboost | 3.2.0 | cuda | cuda | imported | passed | passed | True |

## Remaining Blockers

- none for the checked GPU ML runtime scope

## Use

This file can only support a bounded post-simulation GPU ML runtime claim for packages whose package-specific GPU check and CPU fallback both passed. It does not make the SimPy/NetworkX simulator GPU accelerated, does not prove the simulator is GPU accelerated, and does not prove model validity.
