# Accessibility-Loss Diagnostic

This note documents the current route-level accessibility-loss scaffold.

The diagnostic removes one directed edge at a time from each baseline
shortest-time road route and recomputes whether the route remains available,
how much free-flow time increases, and whether the edge removal disconnects the
route. It is intended to support critical-link and accessibility-loss review
without claiming calibrated disruption probabilities or operational route
guidance.

## Implemented Files

- `src/realworld/accessibility.py`
- `scripts/run_accessibility_loss_analysis.py`
- `tests/test_realworld_accessibility.py`
- `data/validation/accessibility_loss.csv`
- `data/validation/accessibility_loss_summary.md`

## Current Route Set

The default route set matches the current road-mode planning legs:

- `bus_direct`: `A -> D`
- `rail_access`: `A -> S`
- `last_mile`: `R -> D`

## Claim Boundary

Allowed interpretation:

- scaffold route-fragility diagnostic;
- adapted-graph edge-removal sensitivity;
- evidence for where accessibility could be fragile in the current pilot
  scaffold.

Not allowed interpretation:

- calibrated real-world accessibility loss;
- observed disruption impact;
- emergency route recommendation;
- proof that one transport policy is operationally superior.

Final manuscript claims still require accepted graph-scale, road evidence,
validation, experiment, sensitivity, and manuscript/report gates.

## Regeneration

```powershell
.\.venv\Scripts\python scripts\run_accessibility_loss_analysis.py
.\.venv\Scripts\python tests\test_realworld_accessibility.py
```
