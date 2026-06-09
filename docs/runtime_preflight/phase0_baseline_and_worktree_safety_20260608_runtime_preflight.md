# Runtime Preflight Manifest

Runtime preflight evidence only; not simulation output evidence, not calibrated validation, not publication readiness, not final-study approval, and not formal acceptance.

## Verdict

- Phase ID: `phase0_baseline_and_worktree_safety_20260608`
- Execution scope: `cpu`
- Runtime preflight blockers absent: `true`
- CPU simulation default: `true`
- Simulation engine GPU accelerated: `false`
- Final-study ready: `false`

## Runtime Evidence

- Git HEAD: `0faedef2f166da44c1d795372f708149ae99860e`
- Git branch: `main`
- Python: `3.12.10`
- OS CPU count: `16`
- Pip check: `passed`
- Dirty manifest hash: `sha256:b865a61bfb54aa03071b690d953b4eb722ffb3b75087e1c41f3a2777823627d0`

## Package Imports

| Distribution | Import | Version | Status |
| --- | --- | --- | --- |
| simpy | simpy | 4.1.2 | imported |
| networkx | networkx | 3.6.1 | imported |
| numpy | numpy | 2.4.6 | imported |
| pandas | pandas | 3.0.3 | imported |
| PyYAML | yaml | 6.0.3 | imported |
| matplotlib | matplotlib | 3.10.9 | imported |
| seaborn | seaborn | 0.13.2 | imported |
| python-docx | docx | 1.2.0 | imported |
| SALib | SALib | 1.5.2 | imported |

## Remaining Blockers

- none for this runtime-preflight scope

## Use

This manifest records environment and dependency state before a run. It does not validate simulation outputs, does not certify source evidence, and does not close publication or final-study gates.
