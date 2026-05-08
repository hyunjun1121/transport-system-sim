# Formal Acceptance Artifact Guard

> Current project status (2026-05-08): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


This guard checks formal acceptance paths for copied templates and unresolved
review placeholders. It does not approve any gate and does not replace the
gate-specific acceptance validators.

Run:

```powershell
.\.venv\Scripts\python scripts\audit_formal_acceptance_artifacts.py
```

Expected current scaffold behavior:

- formal acceptance artifacts are absent;
- formal acceptance readiness is 0 / 12 formal gates;
- final-study readiness remains `false` with 3 / 15 plan gates ready and
  12 / 15 blocked;
- template artifacts remain under `data/manifests/acceptance_templates/`;
- `template_or_placeholder_count` is `0`;
- `formal_acceptance_ready` remains `false`.

If a formal path contains `template_only`, `TEMPLATE ONLY`, `REVIEW_REQUIRED`,
or draft weak road-override rows, the guard reports a blocker. A reviewer must
replace placeholders with source-backed decisions and then rerun the
gate-specific validator and final-study readiness audit.

For current blocker context, cross-check
`docs/current_goal_completion_audit.md`,
`docs/formal_acceptance_package_audit.md`,
`docs/graph_scale_strategy_readiness_packet.md`, and
`docs/validation_strategy_readiness_packet.md`. For the sensitivity and full
experiment gates, also cross-check
`docs/sensitivity_strategy_readiness_packet.md` and
`docs/experiment_strategy_readiness_packet.md`. These documents are review
inputs only; none of them is final approval.
