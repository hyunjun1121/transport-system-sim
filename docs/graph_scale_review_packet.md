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
| `scripts/write_graph_scale_review_packet.py` | Regenerates the worksheet and manifest | deterministic scaffold command |
| `src/realworld/graph_scale_review.py` | Library implementation for option rows and manifest writing | project-owned code |

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
bus-practical graph has smoke evidence but not full scenario-policy-seed
experiment outputs.

Final claims require a reviewer-created
`data/manifests/graph_scale_acceptance.json` after deciding which graph-scale
method is valid for the study and after regenerating any affected outputs.

## Regeneration

```powershell
.\.venv\Scripts\python scripts\write_graph_scale_review_packet.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
```

Do not create `data/manifests/graph_scale_acceptance.json` from this packet
alone.
