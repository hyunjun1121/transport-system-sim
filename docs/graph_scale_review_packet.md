# Graph-Scale Review Packet

## Scope

`data/validation/graph_scale_review_packet.csv` compares graph-scale method
options for the current quasi-real pilot scaffold. It is not graph-scale
acceptance, not calibrated real-world validation, and not an operational route
decision.

The packet exists because the current study has four graph-scale paths:

- the current 118-node reduced analysis corridor;
- the small 164-node multi-corridor candidate graph that preserves top route
  candidates;
- the full-profile 164-node multi-corridor candidate output generated on the
  same 7-policy, 9-scenario, 30-seed matrix as the current full pilot;
- the full 4,608-node / 9,148-edge bus-practical cached graph.

## Generated Artifacts

| Artifact | Role | Current Scope |
| --- | --- | --- |
| `data/validation/graph_scale_review_packet.csv` | Four-option method review worksheet | review support only |
| `data/validation/graph_scale_review_manifest.json` | Summary of option IDs and claim boundary | review support only |
| `data/validation/full_graph_smoke_manifest.json` | Two-row full bus-practical graph smoke manifest | feasibility evidence only |
| `data/validation/full_graph_runtime_readiness_packet.csv` | Full-graph runtime/readiness worksheet | review support only |
| `data/validation/full_graph_runtime_readiness_manifest.json` | Runtime worksheet status summary | review support only |
| `scripts/write_graph_scale_review_packet.py` | Regenerates the worksheet and manifest | deterministic scaffold command |
| `scripts/run_full_graph_smoke.py` | Regenerates the full-graph smoke manifest | bounded smoke command |
| `scripts/write_full_graph_runtime_readiness_packet.py` | Regenerates full-graph runtime readiness rows | deterministic scaffold command |
| `src/realworld/graph_scale_review.py` | Library implementation for option rows and manifest writing | project-owned code |
| `src/realworld/full_graph_runtime_readiness_packet.py` | Library implementation for runtime readiness rows | project-owned code |

## Interpretation

The current reduced corridor has full-graph baseline route parity, but its
alternate-route diagnostic still has warning rows. The small multi-corridor
candidate preserves the top route candidates and has a separated 32-row smoke
profile. The full-profile multi-corridor candidate uses the same 1,890-row
scenario-policy-seed matrix as the current full pilot. This improves the
graph-scale review evidence, but it still does not accept the candidate graph
as the final method. The companion result-comparison table has 819 metric-level
current-vs-candidate delta rows so reviewers can inspect whether the graph
choice changes outcomes before any acceptance record is created. The full
bus-practical graph has a current two-row smoke manifest on 4,608 nodes and
9,148 edges, plus a 4-row runtime-readiness packet. That packet records an
estimated full-profile runtime from the smoke rate, but the full graph still
has no full scenario-policy-seed experiment outputs and no downstream
regeneration decision.

Final claims require a reviewer-created
`data/manifests/graph_scale_acceptance.json` after deciding which graph-scale
method is valid for the study and after regenerating any affected outputs.
The latest graph-scale strategy-readiness packet is present at
`docs/graph_scale_strategy_readiness_packet.md` with data artifacts
`data/validation/graph_scale_strategy_readiness_packet.csv` and
`data/validation/graph_scale_strategy_readiness_manifest.json`; it records
current blockers and human-review items, not acceptance. Current final-study
status remains `final_study_ready=false` with 3 / 15 plan gates ready, 12 / 15
blocked, and formal acceptance 0 / 12 ready.

## Regeneration

```powershell
.\.venv\Scripts\python scripts\run_full_graph_smoke.py
.\.venv\Scripts\python scripts\write_full_graph_runtime_readiness_packet.py
.\.venv\Scripts\python scripts\write_graph_scale_review_packet.py
.\.venv\Scripts\python scripts\write_graph_scale_strategy_readiness_packet.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
.\.venv\Scripts\python tests\test_realworld_full_graph_runtime_readiness_packet.py
.\.venv\Scripts\python tests\test_realworld_graph_scale_strategy_readiness_packet.py
```

Do not create `data/manifests/graph_scale_acceptance.json` from this packet
alone.
