# Formal Acceptance Artifact Guard

This guard checks formal acceptance paths for copied templates and unresolved
review placeholders. It does not approve any gate and does not replace the
gate-specific acceptance validators.

Run:

```powershell
.\.venv\Scripts\python scripts\audit_formal_acceptance_artifacts.py
```

Expected current scaffold behavior:

- formal acceptance artifacts are absent;
- template artifacts remain under `data/manifests/acceptance_templates/`;
- `template_or_placeholder_count` is `0`;
- `formal_acceptance_ready` remains `false`.

If a formal path contains `template_only`, `TEMPLATE ONLY`, `REVIEW_REQUIRED`,
or draft weak road-override rows, the guard reports a blocker. A reviewer must
replace placeholders with source-backed decisions and then rerun the
gate-specific validator and final-study readiness audit.
