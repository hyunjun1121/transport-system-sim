# Accessibility-Loss Diagnostic

> Current project status (2026-05-06): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


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
