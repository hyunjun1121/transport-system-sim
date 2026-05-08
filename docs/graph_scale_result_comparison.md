# Graph-Scale Result Comparison

> Current project status (2026-05-08): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


## Scope

`data/validation/graph_scale_result_comparison.csv` compares the current
118-node reduced-corridor full pilot summary with the 164-node / 246-edge
full-profile multi-corridor candidate summary.

This is review support only. It does not accept a graph-scale method, validate
real-world calibration, or authorize operational routing claims.

## Generated Artifacts

| Artifact | Role | Current Scope |
| --- | --- | --- |
| `data/validation/graph_scale_result_comparison.csv` | Metric-level current-vs-candidate summary deltas | review support only |
| `data/validation/graph_scale_result_comparison_manifest.json` | Row counts, status counts, and review items | review support only |
| `scripts/write_graph_scale_result_comparison.py` | Regenerates the comparison CSV and manifest | deterministic scaffold command |
| `src/realworld/graph_scale_result_comparison.py` | Project-owned implementation | no runtime dependency on cloned repos |

## Current Interpretation

The current comparison has 819 rows: 63 policy-scenario-mode summary groups
times 13 summary metrics. It reports 741 `same_or_close` rows, 24
`candidate_improves` rows, 24 `candidate_worsens` rows, and 30
`nonfinite_difference` rows.

The large differences are expected to require review because some blocked-link
cases are disconnected under the current reduced corridor but remain reachable
under the multi-corridor candidate. That may indicate a better graph-scale
abstraction, or it may indicate that the scenario definition interacts with the
candidate graph differently than intended. The comparison table makes this
decision explicit; it does not resolve it.

## Regeneration

```powershell
.\.venv\Scripts\python scripts\write_graph_scale_result_comparison.py
.\.venv\Scripts\python scripts\audit_plan_artifacts.py
```

Do not create `data/manifests/graph_scale_acceptance.json` from this
comparison alone.
