# Sensitivity Review Packet

> Current project status (2026-05-06): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


## Scope

`data/validation/sensitivity_review_packet.csv` converts the current SALib
Morris diagnostics into a reviewer-facing worksheet. It is review support
only. It is not sensitivity acceptance, not a Sobol waiver, not calibrated
real-world sensitivity evidence, and not an operational forecast.

The packet preserves the current Morris outputs and adds a review layer for:

- structural readiness of the Morris summary and manifest;
- missing, blank, NaN, infinite, or unparsable Morris index values;
- zero `mu_star` rows that need interpretation before ranking claims;
- reduced analysis graph scope;
- scaffold or not-calibrated result scope;
- the reviewer decision on whether Morris screening is sufficient or Sobol
  analysis is required before final-study use.

## Generated Artifacts

| Artifact | Role | Current Scope |
| --- | --- | --- |
| `data/validation/sensitivity_review_packet.csv` | Six-row sensitivity review worksheet | review support only |
| `data/validation/sensitivity_review_manifest.json` | Summary of diagnostic counts, input paths, and claim boundary | review support only |
| `scripts/write_sensitivity_review_packet.py` | Regenerates the worksheet and manifest from Morris diagnostics | deterministic scaffold command |
| `src/realworld/sensitivity_review_packet.py` | Library implementation for rows and manifest writing | project-owned code |

## Current Interpretation

The current Morris artifacts are structurally ready for review, but they remain
inside the pilot scaffold boundary. The review packet keeps missing or
non-finite index counts, zero `mu_star` counts, reduced graph scope, and the
Morris-vs-Sobol method decision visible. It also keeps `publication_ready` and
`acceptance_ready` false.

Final-study sensitivity claims remain blocked until a real reviewer decision is
recorded separately in `data/manifests/sensitivity_acceptance.json`. This
packet must not be used to create that acceptance record automatically.

## Regeneration

```powershell
.\.venv\Scripts\python scripts\write_sensitivity_review_packet.py
.\.venv\Scripts\python scripts\audit_sensitivity_diagnostics.py
.\.venv\Scripts\python scripts\audit_publication_readiness.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
```

Do not cite the packet as calibrated sensitivity evidence. It organizes review
questions and blocker counts so the sensitivity gate can be evaluated later.
