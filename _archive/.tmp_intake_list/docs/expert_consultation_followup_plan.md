# Expert Consultation Follow-Up Plan

Date: 2026-05-11

This plan translates the external expert reply in
`docs/expert_consultation_request_reply.md` into repository work items. The
reply reviewed `required_deliverables.zip` as the primary evidence package and
found a materially complete implementation/review bundle with 813 files, including
the core simulator, scripts, tests, data, results, docs, plans, and reports.

## Evidence Boundary

The current inspection confirms package completeness relative to implementation,
review, and reproducibility materials. The immediate consequence is therefore a
non-final but complete review intake: technical mechanics and result claims can be
inspected from package contents, but acceptance is still blocked by unresolved
evidence/formal-gate decisions.

The ZIP also excludes these handoff-sidecar files by default:

- `review_packages/expert_review_handoff_20260510.md`
- `review_packages/expert_review_handoff_20260510.json`
- `docs/review_package_build.md`
- `docs/review_package_path_audit.md`

These, plus `docs/expert_consultation_request.md`,
`docs/expert_consultation_request_reply.md`, and
`docs/expert_consultation_followup_plan.md`, must be supplied together for strict
intake checks. Their absence in the ZIP is acceptable for mechanics review but is
an intake-blocking condition for strict traceable review.

Treat every finding below as a follow-up requirement derived from the reply,
not as new acceptance. This document does not approve road data, rail data,
parameters, validation, sensitivity results, experiment outputs,
reproducibility, manuscript language, or the final audit.

## Consultation Verdict To Preserve

The reply's operative verdict is: not ready for acceptance.

The plan must preserve these constraints:

- The current study remains `final_study_ready=false`.
- The accepted final-study gate count remains 3 / 15 until reviewed evidence
  changes it.
- Formal acceptance remains 0 / 12 unless reviewer-signed, source-backed
  formal records replace templates and placeholders.
- Generated templates, copied acceptance-looking files, current-worktree smoke
  outputs, path hygiene, OSRM plausibility checks, and OSM-derived road data do
  not close gates by themselves.
- No bus-only versus bus+rail benefit claim can be made as a formal conclusion
  until road, rail, parameter, graph-scale, validation, sensitivity,
  experiment, manuscript, reproducibility, and final-audit blockers are closed.
- The model must be described as a decision-support and resilience-evaluation
  framework, not an operational route plan, evacuation plan, mobilization
  order, dispatch schedule, or validated deployment instruction.

## Immediate File-Package Correction

The first blocker is not a modeling change. It is packaging and review
traceability.

Required package contents for the next expert review:

- `main.py`, `config.yaml`, `requirements.txt`, and report-generation entry
  points.
- `src/`, including the core simulator modules and `src/realworld/`.
- `scripts/`, including audit, evidence, experiment, sensitivity, and
  reproducibility commands.
- `tests/`, or an explicit test-inventory file if tests are intentionally
  excluded from a lightweight review package.
- `data/`, including manifests, source-review packets, region specs,
  parameter packets, road and rail packets, validation packets, and scenario
  tables.
- `results/`, including pilot result CSVs, summary CSVs, figure/table
  manifests, sensitivity outputs, and statistics tables when those outputs are
  being reviewed.
- `docs/`, including runbooks, acceptance schemas, review packets, readiness
  packets, audit outputs, and claim-alignment packets.
- `paper/`, `report_draft.md`, and generated report artifacts if
  manuscript/report alignment is in scope.
- `plan.md`, `status.md`, `IMPLEMENTATION_PLAN.md`, `agents.md`, and this
  follow-up plan.
- A package inventory with path, byte size, checksum, source category, and
  whether the artifact is code, configuration, input evidence, generated
  output, review worksheet, formal acceptance target, or narrative text.

Current package-correction status:

- `required_deliverables.zip` has been rebuilt from the package inventory as
  the renewed expert-review handoff ZIP.
- The renewed ZIP contains the inventory-selected review files and has no
  missing inventory paths. The current file count and SHA256 are recorded in
  `docs/review_package_build.md` after each package build rather than being
  hard-coded here.
- `scripts/audit_review_package_paths.py` checks that agent-review records
  inside the ZIP do not cite missing non-formal local paths. Its report is a
  sidecar generated after ZIP assembly, like `docs/review_package_build.md`.
- `scripts/write_expert_review_handoff.py` writes
  `review_packages/expert_review_handoff_20260510.md` and
  `review_packages/expert_review_handoff_20260510.json` outside the ZIP so
  the final ZIP checksum, send-list, and non-acceptance cover note can be
  reviewed without mutating the package.
- The previous 12-file acceptance-artifact-only ZIP was preserved at
  `review_packages/original_required_deliverables_incomplete_20260510.zip`.
- The ZIP currently excludes the handoff-sidecar files listed above by design; this
  is intentional to keep review-package checksums stable.
- This resolves the immediate package-completeness handoff correction only.
  It does not approve evidence, validate calibration, or close formal
  acceptance gates.

## Cross-Document Control Synchronization

The follow-up actions below must stay synchronized with companion plan files:

- `plan.md` and `status.md` track same package-completeness and blocker state as this plan.
- `IMPLEMENTATION_PLAN.md` carries the same hard controls: no artifact-name acceptance and no closure of gates from copied placeholders/templates.
- `README.md` and `docs/formal_acceptance_artifact_guard.md` inherit the same definition of “accepted artifact.”
- `docs/current_goal_completion_audit.md` and `docs/plan_completion_audit.md` record every helper audit command result, while this document carries remediation sequencing.

If any companion file changes the meaning of a blocker, `docs/expert_consultation_followup_plan.md` is the authority for remediation sequencing for the next expert round.

Minimum package verification before sending a new ZIP:

```powershell
Get-ChildItem -Recurse -File | Select-Object FullName,Length
.\.venv\Scripts\python scripts\write_review_package_inventory.py
.\.venv\Scripts\python scripts\build_review_package.py --output required_deliverables.zip --fail-on-missing
.\.venv\Scripts\python scripts\audit_review_package_paths.py --fail-on-missing
Copy-Item required_deliverables.zip review_packages\expert_review_package.zip
.\.venv\Scripts\python scripts\write_expert_review_handoff.py --fail-on-zip-mismatch
.\.venv\Scripts\python scripts\audit_tracked_artifacts.py
.\.venv\Scripts\python scripts\audit_formal_evidence_paths.py
.\.venv\Scripts\python scripts\validate_formal_acceptance_package.py
```

Send `required_deliverables.zip`, `docs/review_package_build.md`,
`docs/review_package_path_audit.md`, `docs/expert_consultation_request.md`,
`docs/expert_consultation_request_reply.md`,
`docs/expert_consultation_followup_plan.md`,
`review_packages/expert_review_handoff_20260510.md`, and
`review_packages/expert_review_handoff_20260510.json` together.

Expected outcome before final acceptance: no referenced local evidence path is
missing from the review package unless it is intentionally marked as external
with a durable URL or citation, retrieval date, checksum or archive note,
license disposition, and reviewer decision.

## Artifact-Naming Risk Control

The reply flags "acceptance by artifact naming" as a material risk. The plan
therefore requires a hard distinction between templates, drafts, pre-review,
and formal approvals.

Rules:

- A file named `*_acceptance.json` in a formal target path must either be a
  real reviewed decision or be absent.
- A template, copied worksheet, AI-generated pre-review, unresolved
  `REVIEW_REQUIRED`, `accepted=false` placeholder, or draft road override must
  not occupy a formal target path and must not be treated as progress toward
  gate closure.
- If unreviewed acceptance-like artifacts are needed for reviewer drafting,
  keep them under a draft/template directory and make the filename explicit,
  such as `*_acceptance_template.json` or `draft_acceptance/*_pre_review.json`.
- `data/parameters/parameter_acceptance.csv` and
  `data/parameters/road_class_overrides.csv` require the same discipline:
  final-path files should mean reviewed decisions, while draft assumptions
  should remain in clearly named draft files.

Verification commands:

```powershell
.\.venv\Scripts\python scripts\audit_formal_acceptance_artifacts.py
.\.venv\Scripts\python scripts\audit_formal_evidence_paths.py
.\.venv\Scripts\python scripts\validate_formal_acceptance_package.py
```

## Gate-Specific Remediation Matrix

| Gate | Immediate Remediation | Required Formal Artifact | Acceptance Condition |
| --- | --- | --- | --- |
| `pilot_region_accepted` | Complete privacy, sensitivity, case-scope, and non-operational review for the pilot region. Confirm the pilot is public/non-sensitive or appropriately abstracted. | `data/manifests/pilot_acceptance.json` | Reviewer signs region scope, privacy treatment, source/analysis graph dependency, and claim boundary. |
| `cached_osm_input` | Replace draft road-class defaults with reviewed speed, capacity, and base-disruption evidence, or explicitly approve sensitivity-only treatment. | `data/parameters/road_class_overrides.csv` | No final-claim row remains draft-only; source, derivation, and reviewer fields are complete. |
| `graph_scale_strategy` | Decide whether to use the reduced corridor, the 164-node / 246-edge candidate, full-graph runtime, or a multi-corridor ensemble. Quantify route and result deltas. | `data/manifests/graph_scale_acceptance.json` | Graph abstraction bias is accepted or bounded, and downstream result scope matches the chosen graph method. |
| `data_provenance` | Build source cards for road, rail, parameter, validation, and report inputs. Resolve URL durability, local cache, checksums, license, attribution, and privacy treatment. | `data/manifests/provenance_acceptance.json` | No source placeholder remains; cache and license/privacy decisions are reviewer-backed. |
| `parameter_evidence` | Split all weak parameters into source-derived, literature-derived, scenario-assumption, or sensitivity-only categories. Add ranges and claim boundaries. | `data/parameters/parameter_acceptance.csv` | Every row has units, source class, source/citation, derivation, sensitivity range, reviewer, status, and claim boundary. |
| `rail_evidence` | Add cached timetable, static GTFS, shortest-path, or equivalent rail evidence. Keep capacity sensitivity-only unless source-backed capacity is reviewed. | `data/parameters/parameter_acceptance.csv` plus rail evidence packets | Headway, travel time, station binding, capacity treatment, and availability are reviewed and traceable. |
| `validation_package` | Keep OSRM/fallback checks as plausibility unless stronger benchmarks are accepted. Define benchmark sources, tolerances, route classes, and limitations. | `data/manifests/validation_acceptance.json` | Validation scope is accepted as plausibility or stronger, with explicit error metrics and no ground-truth overclaim. |
| `sensitivity_analysis` | Review parameter ranges and Morris diagnostics. Decide whether Sobol or LHS/PRCC confirmatory analysis is required for final claims. | `data/manifests/sensitivity_acceptance.json` | Ranges, graph scope, non-finite handling, interaction decision, and interpretation limits are accepted. |
| `full_experiment_output` | Prove CRN correctness, scenario-policy-seed mapping, row counts, checksums, and paired-difference reporting. | `data/manifests/experiment_acceptance.json` | Same demand/disruption streams are verified across policies; result manifests match accepted graph and input scope. |
| `manuscript_report_alignment` | Freeze benefit claims until evidence gates close. Add claim-to-evidence matrix and revise forecast/operational language. | `data/manifests/manuscript_acceptance.json` | Every claim is accepted, weakened, removed, or explicitly exploratory; docx regeneration is reviewed. |
| `reproducibility` | Move from current-worktree smoke to clean checkout, clean environment, dependency pinning, artifact regeneration, and hash comparison. | `data/manifests/reproducibility_acceptance.json` | A reviewer can reproduce accepted artifacts from source, locked dependencies, frozen caches, and documented commands. |
| `final_audit` | Run only after every pre-final gate has accepted evidence. Reject proxy-only completion signals. | `docs/final_study_audit.md` and `data/manifests/final_audit_acceptance.json` | Independent audit confirms all gates ready, no blocked formal targets, and no operational overclaim. |

## Two-Week Execution Plan

### Workstream 1: Complete Review Package

Deliverable: a complete review ZIP or repository export with implementation,
configuration, scripts, tests, data/cache artifacts, results, docs, report
sources, package inventory, and checksums.

Success criteria:

- Every local evidence path referenced by formal records, review packets, or
  manifests exists inside the package or is deliberately classified as external.
- The package contains the implementation needed to verify model mechanics.
- The package contains the result files and manifests needed to verify row
  counts, graph scope, and result lineage.
- The package contains enough docs to reproduce the audit state without relying
  on filenames alone.
- The ZIP build manifest records package file count, SHA256, excluded formal
  targets, and any missing inventory rows.

Dependencies: current repository artifacts, cache policy, generated outputs,
and version-control hygiene.

Risk: the existing ZIP may have been assembled from acceptance artifacts only;
repackaging may reveal missing or stale generated outputs.

### Workstream 2: Formal Artifact Hygiene

Deliverable: a clean separation between final acceptance paths and draft or
template paths.

Success criteria:

- Formal target paths are absent unless real reviewer decisions exist.
- Draft templates stay under template/draft paths and retain non-approval
  language.
- Formal guard and evidence-path audits reject copied templates or unresolved
  placeholders.
- The blocker queue remains the authoritative list of unresolved human actions.

Dependencies: reviewer workflow discipline and current untracked artifact
state.

Risk: acceptance-looking files may already exist in final paths and could be
misread by future reviewers unless they are reviewed or relocated.

### Workstream 3: Road And Parameter Evidence

Deliverable: reviewed road-class and parameter evidence packets.

Success criteria:

- Road speed, capacity, and base-disruption rows are source-backed,
  literature-backed, benchmark-calibrated, or explicitly scenario/sensitivity
  only.
- The final road override table no longer contains draft-only rows for final
  claims.
- The parameter acceptance table covers demand, arrival process, fleet,
  dispatch, transfer, traffic/BPR, disruption, rail, horizon, and censoring
  assumptions with units and sensitivity ranges.

Dependencies: public agency data, literature sources, domain reviewer
availability, and benchmark strategy.

Risk: capacity, disruption probability, and background traffic evidence may be
hard to source; final claims may need to be narrowed to scenario analysis.

### Workstream 4: Rail Evidence

Deliverable: a rail evidence package covering station binding, timetable or
GTFS-derived headway, shortest-path or timetable-derived travel time, capacity
treatment, availability, cache metadata, and license terms.

Success criteria:

- Headway and travel time are derived from reviewed cached records or explicitly
  bounded as assumptions.
- Capacity is source-backed or retained as sensitivity-only with reviewer
  approval.
- Station binding remains separate from timing, capacity, and availability
  acceptance.

Dependencies: reviewed GTFS/timetable/shortest-path source access and API-key
or cached-file policy.

Risk: public timetable or GTFS license terms may restrict redistribution or
require source-specific handling.

### Workstream 5: Experiment And CRN Integrity

Deliverable: a seed-stream manifest, CRN pairing audit, scenario-policy-seed
design note, and paired-difference statistical summaries.

Current implementation support:

- `scripts/audit_crn_pairing.py` writes
  `data/manifests/crn_pairing_audit.csv`,
  `data/manifests/crn_pairing_audit_manifest.json`, and
  `docs/crn_pairing_audit.md`.
- `scripts/write_seed_stream_manifest.py` writes
  `data/manifests/seed_stream_manifest.json` and
  `docs/seed_stream_manifest.md`, documenting the current demand,
  disruption, and deterministic dispatch/fleet/rail/transfer/traffic streams.
- The audit checks structural pairing across region, graph source, policy,
  scenario, and seed dimensions, and records the current `src/scenario.py`
  seed-stream markers.
- `scripts/make_pilot_statistics.py` writes paired-delta CI tables under
  `results/realworld_pilot/tables/`, including
  `pilot_full_paired_delta_ci.csv`.
- `scripts/audit_replication_adequacy.py` writes
  `data/manifests/replication_adequacy_audit.csv`,
  `data/manifests/replication_adequacy_audit_manifest.json`, and
  `docs/replication_adequacy_audit.md`, keeping seed-count adequacy, CI method,
  finite-count gaps, and multiple-comparison handling as explicit review items.
- `scripts/write_experiment_statistical_plan.py` writes
  `data/manifests/experiment_statistical_analysis_plan.json` and
  `docs/experiment_statistical_analysis_plan.md`, tying the candidate
  scenario-policy-seed design, primary metrics, primary policy contrast, CRN
  audit, replication audit, CI method, and multiplicity boundary into one
  non-acceptance statistical-analysis note.
- `scripts/audit_deterministic_rerun.py` writes
  `data/manifests/deterministic_rerun_audit.csv`,
  `data/manifests/deterministic_rerun_audit_manifest.json`, and
  `docs/deterministic_rerun_audit.md` by rerunning the bounded pilot sample
  profile twice and comparing canonical result and summary hashes.
- The audit remains review support only. It does not approve
  `data/manifests/experiment_acceptance.json`, prove replication adequacy, or
  replace paired-difference statistics.

Success criteria:

- Demand and disruption random streams are shared across policy alternatives
  for each scenario and replicate.
- Separate named streams exist for demand, disruption, dispatch tie-breaking,
  and any future sampling logic.
- Primary outcomes are pre-specified.
- Paired confidence intervals are reported for primary policy comparisons.
- Multiple-comparison handling is documented for secondary comparisons.

Dependencies: accepted graph scope, accepted input evidence, and stable result
manifests.

Risk: a seed-design defect would require rerunning pilot experiments and
regenerating figures/tables.

### Workstream 6: Reproducibility Package

Deliverable: clean-checkout reproduction log, dependency pinning, cache freeze
rules, result manifests, checksums, and artifact-regeneration log.

Success criteria:

- A clean checkout can recreate the accepted evidence profile.
- The environment can be recreated from pinned dependencies.
- Full or accepted-scope experiment outputs regenerate with matching schemas,
  row counts, and hashes or documented tolerances.
- Report and figure/table artifacts regenerate from current sources.

Dependencies: package completeness, cache freeze, and dependency stability.

Risk: path-specific Windows assumptions, optional external software, or
time-dependent live-source calls may need cached fallbacks.

### Workstream 7: Manuscript And Report Claim Control

Deliverable: claim-to-evidence matrix and revised paper/report language.

Success criteria:

- No bus+rail benefit claim appears without accepted evidence, uncertainty,
  graph scope, validation scope, and parameter-bound language.
- OSRM/fallback checks are described as route plausibility only.
- Censored passengers are interpreted with horizon, demand, fleet, and penalty
  sensitivity.
- The not-operational disclaimer appears near the front of report materials.

Dependencies: evidence gate outcomes and figure/table review.

Risk: accepted evidence may support only a narrower exploratory or
decision-support claim than the current narrative suggests.

## One-Month Execution Plan

### Workstream 8: Graph-Scale Validation

Deliverable: full-vs-reduced or multi-corridor comparison package.

Success criteria:

- Route-level travel-time deltas, alternate-route coverage, accessibility
  deltas, and result deltas are reported.
- The chosen graph method is linked to a formal graph-scale acceptance record.
- Downstream experiments, sensitivity, and figures use the accepted graph scope
  or clearly label current outputs as scaffold evidence.

Risk: full graph or multi-corridor results may change policy rankings.

### Workstream 9: Sensitivity Upgrade

Deliverable: reviewed Morris results plus confirmatory Sobol, LHS/PRCC, or
another accepted interaction-aware design for top factors if required.

Success criteria:

- Parameter ranges are reviewed before analysis.
- Non-finite and unavailable indices are classified and documented.
- Interactions among demand scale, road capacity, rail headway, shuttle fleet,
  and disruption severity are assessed or explicitly deferred with a claim
  boundary.
- Robustness is reported as stability across an uncertainty envelope, not as a
  single deterministic ranking.

Risk: compute cost may require a representative subset rather than a full
factorial confirmatory design.

### Workstream 10: Expanded Disruption Scenarios

Deliverable: accepted scenario additions for high-betweenness arterial or
bridge-like chokepoints, rail-adjacent transfer bottlenecks, fleet/terminal
constraints, and demand surges.

Success criteria:

- Each scenario has a rationale, source class, parameter range, and reviewer
  decision.
- Shared road chokepoints that affect both bus-only and rail access are tested.
- Station access, curb capacity, transfer delay, and last-mile turnaround
  bottlenecks are explicitly stressed.

Risk: added scenarios may require additional parameter evidence and reruns.

### Workstream 11: Validation Strengthening

Deliverable: benchmark comparison package using public route, timetable, or
agency references where available.

Success criteria:

- Benchmark sources, retrieval dates, licenses, route classes, tolerances, and
  error metrics are documented.
- Validation remains labeled as plausibility unless stronger empirical
  calibration evidence is actually available.
- Internal invariant checks cover conservation, censoring, dispatch, rail
  timing, and graph/path consistency.

Risk: public benchmarks may not cover disrupted operations, so the accepted
  claim may remain quasi-real scenario analysis.

### Workstream 12: Publication-Ready Evidence Package

Deliverable: data cards, model cards, reproducibility appendix, statistical
analysis plan, claim matrix, and final acceptance package.

Success criteria:

- An independent reviewer can reproduce each accepted claim from attached
  artifacts.
- All 15 final-study gates are ready.
- All 12 formal acceptance artifacts exist, are reviewed, and pass guard/path
  audits.
- Final manuscript/report text is regenerated after the accepted evidence
  profile is fixed.

Risk: remaining evidence gaps may force Path A or Path B acceptance rather than
  stronger policy-comparison acceptance.

## Claim Language To Apply Everywhere

Use this baseline wording until all acceptance blockers close:

> The current repository implements an executable quasi-real decision-support
> scaffold for stress-testing bus-only and rail-bus alternatives under
> documented assumptions. Current outputs are not calibrated real-world
> forecasts, operational routing instructions, or formal evidence that one mode
> is universally superior.

When evidence gates close, use bounded wording:

> Within the accepted pilot scenario set, graph scope, source-backed or
> reviewer-approved parameter bounds, and validation limitations, the model
> estimates relative decision-support indicators for bus-only and rail-bus
> alternatives. These indicators are not deployment instructions.

Avoid:

- "validated against OSRM";
- "bus+rail improves resilience" without scope and uncertainty;
- "the reduced corridor represents the regional network" without graph-scale
  acceptance;
- "incomplete passengers failed because of policy inadequacy" without
  censoring and horizon context;
- "the final study is accepted" while formal acceptance artifacts are missing,
  copied from templates, or marked `accepted=false`.

## Exit Criteria Before Re-Asking For Expert Acceptance

Do not request acceptance of the transport model or policy comparison until all
items below are true:

1. The review package includes implementation, data, results, docs, reports,
   tests, manifests, and acceptance materials.
2. A package inventory and path-integrity check show no accidental missing
   local evidence.
3. Formal target paths contain only real reviewed decisions or are absent.
4. Road, rail, parameter, graph-scale, validation, sensitivity, experiment,
   manuscript, reproducibility, provenance, and final-audit gates have explicit
   acceptance decisions or remain explicitly blocked.
5. Clean-checkout reproduction and artifact regeneration are reviewed.
6. Paper/report claims are traceable to accepted artifacts and uncertainty
   statements.
7. `scripts\audit_publication_readiness.py --fail-on-blockers` and
   `scripts\audit_final_study_readiness.py --fail-on-blockers` pass only after
   the formal evidence exists.
