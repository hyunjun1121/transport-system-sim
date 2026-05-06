# Sensitivity Diagnostics

> Current project status (2026-05-06): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


`scripts/audit_sensitivity_diagnostics.py` reviews the current SALib Morris
scaffold outputs without accepting them for final-study claims.

`scripts/write_sensitivity_review_packet.py` converts the same diagnostics into
`data/validation/sensitivity_review_packet.csv` and
`data/validation/sensitivity_review_manifest.json` for human review. That
packet is still review support only; it does not create
`data/manifests/sensitivity_acceptance.json`.

The diagnostic audit exists because Morris output can be structurally
reproducible while still containing blank, non-finite, or degenerate index
values that require human interpretation before manuscript claims are written.

## What It Checks

- `morris_summary.csv` and `morris_manifest.json` are present.
- Summary row count matches the manifest count.
- Summary row count matches manifest dimensions: metrics, policies, scenarios,
  and parameters.
- Morris index columns `mu`, `mu_star`, `sigma`, and `mu_star_conf` are scanned
  for blank, NaN, infinite, or unparsable values.
- Zero `mu_star` rows are counted as potential inactive-parameter or
  no-variation cases.
- Reduced analysis graph and scaffold claim boundaries remain visible.

## Current Handling In Generated Tables And Figures

- Sensitivity result tables retain blank, masked, NaN, or infinite Morris
  index values so reviewers can inspect the raw diagnostic issue rather than
  receiving an imputed value.
- Sensitivity ranking figures coerce index values to numeric and exclude
  non-finite rows from the plotted top rankings.
- The figure/table manifest records this handling rule. The diagnostic audit
  still counts affected rows and keeps them as review items before any
  sensitivity acceptance decision.

## What It Does Not Do

This diagnostic does not create or replace
`data/manifests/sensitivity_acceptance.json`. It does not decide whether Sobol
analysis is required, does not calibrate parameter ranges, and does not convert
the current scaffold into publication-ready real-world sensitivity evidence.

## Command

```powershell
.\.venv\Scripts\python scripts\audit_sensitivity_diagnostics.py
.\.venv\Scripts\python scripts\write_sensitivity_review_packet.py
```

Optional strict structural check:

```powershell
.\.venv\Scripts\python scripts\audit_sensitivity_diagnostics.py --fail-on-structural-blockers
```

The strict flag fails only for missing files, schema/count mismatches, or other
structural blockers. Review items such as blank Morris indices, zero-effect
rows, reduced-graph scope, or scaffold claim boundaries should remain visible
for human review rather than being silently accepted.
