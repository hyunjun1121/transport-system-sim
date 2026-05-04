# Human Acceptance Runbook

This runbook explains how a reviewer should close final-study gates without
fabricating approval, source evidence, calibration, validation, or operational
routing claims. The repository can generate review packets, templates, guards,
and package audits, but only source-backed reviewer decisions can create formal
acceptance artifacts.

## Current Boundary

- `docs/current_goal_completion_audit.md` is the current-state gap audit.
- `docs/final_study_audit.md` must not be created until every pre-final gate is
  accepted with evidence.
- `data/manifests/agent_reviews/*.json` are sub-agent review records, not
  formal acceptance records.
- `data/manifests/formal_acceptance_evidence_matrix.csv` is a reviewer intake
  index, not a formal acceptance record.
- `docs/formal_acceptance_pre_review.md` and
  `data/manifests/draft_acceptance/*_pre_review.json` are AI-generated
  pre-review recommendations. They classify gates for human review but are not
  formal approval records.
- `data/manifests/acceptance_templates/*.json` and
  `data/parameters/parameter_acceptance_template.csv` are non-approval
  worksheets. They intentionally keep `accepted: false`.
- A copied template, unresolved `REVIEW_REQUIRED` value, draft road override,
  or current-state audit text cannot close a gate.

## Reviewer Workflow

1. Refresh review artifacts:

```powershell
.\.venv\Scripts\python scripts\run_acceptance_audit.py
.\.venv\Scripts\python scripts\run_reproducibility_smoke.py
.\.venv\Scripts\python scripts\audit_tracked_artifacts.py
.\.venv\Scripts\python scripts\write_formal_acceptance_pre_review.py
```

2. Inspect the aggregate blockers:

```powershell
Get-Content docs\current_goal_completion_audit.md
Get-Content docs\review_packets\acceptance_review_index.md
Get-Content docs\formal_acceptance_package_audit.md
Get-Content docs\formal_acceptance_blocker_queue.md
Get-Content docs\formal_acceptance_evidence_matrix.md
Get-Content docs\formal_acceptance_pre_review.md
```

3. For each gate, inspect the gate-specific review packet and supporting
   source paths listed in that packet.

4. If the evidence is still missing, leave the formal artifact absent and keep
   the gate `blocked` or `needs_human_review`.

5. If a reviewer has source-backed evidence and a bounded decision, copy the
   relevant non-approval template into the formal target path, replace every
   placeholder, set the accepted field according to the real decision, and keep
   the claim boundary non-operational.

6. After adding any formal artifact, run:

```powershell
.\.venv\Scripts\python scripts\audit_formal_acceptance_artifacts.py
.\.venv\Scripts\python scripts\audit_formal_evidence_paths.py
.\.venv\Scripts\python scripts\audit_tracked_artifacts.py
.\.venv\Scripts\python scripts\validate_formal_acceptance_package.py
.\.venv\Scripts\python scripts\write_formal_acceptance_evidence_matrix.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
.\.venv\Scripts\python scripts\audit_plan_artifacts.py
```

7. If all pre-final gates are accepted, create `docs/final_study_audit.md` as
   an independent prompt-to-artifact review. Then create
   `data/manifests/final_audit_acceptance.json` only if the final audit confirms
   the gate list, evidence, and non-operational claim boundary.

## Gate Worklist

| Gate | Review Packet | Formal Target | Reviewer Decision Needed |
| --- | --- | --- | --- |
| `pilot_region_accepted` | `docs/review_packets/pilot_region_accepted.md`; `docs/pilot_privacy_review_packet.md` | `data/manifests/pilot_acceptance.json` | Privacy, sensitivity, region scope, and not-operational boundary acceptance |
| `data_provenance` | `docs/review_packets/data_provenance.md`; `docs/source_license_review_packet.md` | `data/manifests/provenance_acceptance.json` | Source URLs, OSM/license/attribution, snapshot, reproducibility, and privacy abstraction review |
| `graph_scale_strategy` | `docs/review_packets/graph_scale_strategy.md` | `data/manifests/graph_scale_acceptance.json` | Reduced-corridor, multi-corridor, or full-graph method choice with matching graph counts |
| `cached_osm_input` | `docs/review_packets/cached_osm_input.md` | `data/parameters/road_class_overrides.csv` | Reviewed road speed, capacity, and base-disruption evidence or bounded override decision |
| `parameter_evidence` | `docs/review_packets/parameter_evidence.md` | `data/parameters/parameter_acceptance.csv` | Acceptance or replacement of weak demand, fleet, transfer, disruption, traffic, and censoring parameters |
| `rail_evidence` | `docs/review_packets/rail_evidence.md` | `data/parameters/parameter_acceptance.csv` | Rail headway, travel time, station, and capacity evidence or explicit sensitivity-only boundary |
| `validation_package` | `docs/review_packets/validation_package.md` | `data/manifests/validation_acceptance.json` | Benchmark strategy, thresholds, sample scope, failure cases, and benchmark-not-ground-truth acknowledgement |
| `sensitivity_analysis` | `docs/review_packets/sensitivity_analysis.md` | `data/manifests/sensitivity_acceptance.json` | Parameter ranges, Morris diagnostics, Sobol decision, and interpretation caveats |
| `full_experiment_output` | `docs/review_packets/full_experiment_output.md`; `docs/experiment_package_review_packet.md` | `data/manifests/experiment_acceptance.json` | Scenario-policy-seed package, row counts, manifests, checksums where available, and rerun requirement after upstream changes |
| `manuscript_report_alignment` | `docs/review_packets/manuscript_report_alignment.md`; `docs/claim_alignment_review_packet.md` | `data/manifests/manuscript_acceptance.json` | Claim-by-claim alignment of paper/report/figures against accepted evidence |
| `reproducibility` | `docs/review_packets/reproducibility.md` | `data/manifests/reproducibility_acceptance.json` | Clean-checkout reproduction with command log; current-worktree smoke is supporting evidence only |
| `final_audit` | `docs/review_packets/final_audit.md` | `docs/final_study_audit.md` and `data/manifests/final_audit_acceptance.json` | Independent final review after every pre-final gate closes |

## Acceptance Package Checks

The formal package should stay blocked until all required evidence is present.
These commands are expected to fail with blockers until the human/source-backed
records exist:

```powershell
.\.venv\Scripts\python scripts\validate_formal_acceptance_package.py --fail-on-blockers
.\.venv\Scripts\python scripts\audit_publication_readiness.py --fail-on-blockers
.\.venv\Scripts\python scripts\audit_final_study_readiness.py --fail-on-blockers
```

## Reviewer Safety Rules

- Do not approve a gate from passing tests alone.
- Do not approve a gate from evidence-path hygiene alone; existing paths only
  prove that files are present, not that the evidence is sufficient.
- Do not approve road or rail inputs from OSM/GraphML presence alone.
- Do not approve validation from OSRM or fallback-router checks without a
  benchmark-strategy decision.
- Do not approve sensitivity results while upstream graph/input evidence gates
  are still blocked.
- Do not approve reproducibility from current-worktree smoke alone; it is not a
  fresh-clone or clean-checkout reproduction.
- Do not approve paper/report claims before evidence gates and claim boundaries
  are aligned.
- Do not mark `final_study_ready: true` until the final-study readiness audit and
  formal acceptance package audit both agree.
