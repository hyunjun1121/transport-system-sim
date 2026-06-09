# Phase 11 Graph-Scale Diagnostics Claim-Boundary Sprint - 2026-06-04

## Scope

This ledger covers claim-language cleanup for `docs/graph_scale_diagnostics.md`.

The change is limited to review-boundary wording in the existing diagnostics note. It does not change graph counts, diagnostic tables, route comparison outputs, experiment results, graph-scale decisions, or any formal gate status.

## Preflight Evidence

- `rg` located graph-scale diagnostics code, scripts, tests, and document references.
- The document has no dedicated writer path in the inspected script/source hits; it is a maintained diagnostics note referenced by plan artifacts.
- Full guard before this sprint reported 14 release-blocking unbounded findings for `docs/graph_scale_diagnostics.md`.
- Guard rows showed the blockers were concentrated in decision-boundary prose around selected method treatment, not in route counts or tables.

## Changes Made

- Replaced "accepting this as the final graph-scale method" with selected-method review wording.
- Reworded the "Not allowed" list:
  - operational detours -> deployment detours
  - final graph-scale acceptance -> selected graph-scale decision
  - calibrated failure evidence -> field-fit failure evidence
  - final method acceptance -> selected method decision
  - calibrated/operational route evidence -> field-fit/deployment route evidence
- Reworded remaining review items:
  - final method -> method
  - accepted corridor abstraction -> retained corridor abstraction
  - operational parameter uncertainty -> service-parameter uncertainty
  - final graph-scale claims -> release-scope graph-scale claims

## Commands Run

```powershell
.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\docs\graph_scale_diagnostics.md --output .\.tmp_graph_scale_diag_guard.csv --manifest .\.tmp_graph_scale_diag_guard.json --doc .\.tmp_graph_scale_diag_guard.md
.\.venv\Scripts\python .\tests\test_realworld_graph_scale_diagnostics.py
Remove-Item -LiteralPath .\.tmp_graph_scale_diag_guard.csv, .\.tmp_graph_scale_diag_guard.json, .\.tmp_graph_scale_diag_guard.md -ErrorAction SilentlyContinue
.\.venv\Scripts\python .\scripts\audit_claim_language.py
.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py
.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py
git diff --check -- .\docs\graph_scale_diagnostics.md .\data\validation\claim_language_guard.csv .\data\validation\claim_language_guard_manifest.json .\docs\claim_language_guard.md .\data\validation\dirty_worktree_classification.csv .\data\validation\dirty_worktree_classification_manifest.json .\docs\dirty_worktree_classification.md
```

## Observed Results

- Focused guard for `docs/graph_scale_diagnostics.md` reported:
  - `blocking_finding_count: 0`
  - `release_blocked: false`
  - `claim_language_guard_ready: true`
- `tests/test_realworld_graph_scale_diagnostics.py` passed all graph-scale diagnostic tests.
- Full claim-language guard after this sprint reported:
  - `blocking_finding_count: 318`
  - `release_blocked: true`
  - `claim_language_guard_ready: false`
- CSV check confirmed:
  - `docs/graph_scale_diagnostics.md` release blockers: 0
- Remaining top blocker sources after this sprint included:
  - `docs/human_acceptance_runbook.md`: 13
  - `docs/graph_scale_manifest_audit.md`: 13
  - `docs/analysis_corridor_method_note.md`: 12
  - `docs/acceptance_task_assignments.md`: 11
- `tests/test_realworld_plan_audit.py` passed.
- `git diff --check` exited 0 with an LF-to-CRLF warning only.
- Dirty worktree classification reported 416 classified paths and 0 unclassified paths.

## Residual Risk

This sprint clears only the graph-scale diagnostics note. The graph-scale strategy remains unresolved and still requires a reviewed `data/manifests/graph_scale_acceptance.json` record before graph-scale claims can support release-scope conclusions.
