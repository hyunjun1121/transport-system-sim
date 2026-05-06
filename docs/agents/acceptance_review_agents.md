# Acceptance Review Agents

> Current project status (2026-05-06): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


Sub-agent records are review aids. They do not replace formal acceptance artifacts, source-backed reviewer decisions, calibrated validation, or operational routing approval.

These deterministic sub-agents convert final-study blockers into auditable review tasks. They do not approve the study by themselves.

## Current Readiness Snapshot

- Final-study ready: `false`
- Ready plan gates: 3 / 15 (`real_input_smoke`, `structured_disruptions`, and
  `policy_alternatives`)
- Blocked plan gates: 12 / 15
- Formal acceptance ready: 0 / 12 formal gates
- Formal acceptance artifacts: absent
- Final approval recorded: `false`

## Pilot Region & Privacy Review Agent

- Agent ID: `pilot_region_privacy_review_agent`
- Gates: `pilot_region_accepted`
- Non-ready status: `needs_human_review`
- Mission: Review pilot-region choice, privacy risk, sensitive geography, re-identification risk, and whether region use is acceptable.
- Formal acceptance artifacts: `data/manifests/pilot_acceptance.json`

Decision rules:
- Accept only after privacy, sensitivity, and not-operational claim boundaries are reviewed.
- Treat missing privacy decision as needs_human_review, not accepted.

Required actions when not ready:
- Record an explicit pilot acceptance decision with reviewer, scope, privacy review, evidence paths, and not-operational claim boundary.

## OSM / Source / License / Provenance Review Agent

- Agent ID: `osm_source_license_provenance_review_agent`
- Gates: `data_provenance`
- Non-ready status: `blocked`
- Mission: Review OpenStreetMap and other source provenance, license terms, attribution duties, derivative-use constraints, snapshots, and reproducibility.
- Formal acceptance artifacts: `data/manifests/provenance_acceptance.json`

Decision rules:
- Do not assume license compatibility without cited or source-backed evidence.
- Block final claims while source records are pending review or context-only.

Required actions when not ready:
- Review source URLs, licenses, attribution, local snapshots, privacy abstraction, and reproducibility scope.
- Create data/manifests/provenance_acceptance.json only after source-backed review.

## Graph Scale Method Review Agent

- Agent ID: `graph_scale_method_review_agent`
- Gates: `graph_scale_strategy`
- Non-ready status: `needs_human_review`
- Mission: Review graph-scale computation methodology, reproducible node/edge coverage metrics, route-parity diagnostics, and corridor/full-graph assumptions.
- Formal acceptance artifacts: `data/manifests/graph_scale_acceptance.json`

Decision rules:
- Accept only one graph-scale strategy whose node/edge counts match the pilot manifest.
- Do not treat route-parity diagnostics alone as final graph-scale acceptance.

Required actions when not ready:
- Choose and document reduced-corridor, multi-corridor, or full-graph strategy.
- Review `docs/graph_scale_strategy_readiness_packet.md` for the latest
  graph-scale blockers and human-review items.
- Create graph_scale_acceptance.json with matching graph counts and evidence paths.

## Road / Rail / Parameter Evidence Agent

- Agent ID: `road_rail_parameter_evidence_agent`
- Gates: `cached_osm_input`, `parameter_evidence`, `rail_evidence`
- Non-ready status: `blocked`
- Mission: Review road overrides, rail assumptions, speeds, capacities, costs, weights, dispatch parameters, and parameter provenance.
- Formal acceptance artifacts: `data/parameters/road_class_overrides.csv`, `data/parameters/parameter_acceptance.csv`

Decision rules:
- Flag unsupported parameters; never accept weak defaults silently.
- Use reviewed overrides or accepted weak-parameter records before final claims.

Required actions when not ready:
- Replace weak road, rail, and parameter assumptions with source-backed evidence or explicit accepted overrides.
- Create road_class_overrides.csv and parameter_acceptance.csv only after review.

## Validation Benchmark Strategy Agent

- Agent ID: `validation_benchmark_strategy_agent`
- Gates: `validation_package`
- Non-ready status: `needs_human_review`
- Mission: Review validation benchmark design, metrics, thresholds, sampling strategy, failure cases, and implemented-versus-proposed validation scope.
- Formal acceptance artifacts: `data/manifests/validation_acceptance.json`

Decision rules:
- Benchmark snapshots are plausibility checks, not ground truth.
- Accept only with explicit thresholds, sample scope, and failure-case handling.

Required actions when not ready:
- Review validation thresholds, benchmark scope, snapshot pinning, and failure cases.
- Review `docs/validation_strategy_readiness_packet.md` for the latest
  validation-strategy blockers and human-review items.
- Create validation_acceptance.json after benchmark-strategy review.

## Sensitivity Analysis Review Agent

- Agent ID: `sensitivity_analysis_review_agent`
- Gates: `sensitivity_analysis`
- Non-ready status: `blocked`
- Mission: Review sensitivity method, scenario ranges, outputs, interpretation, and whether Morris or Sobol evidence is sufficient for the target claim.
- Formal acceptance artifacts: `data/manifests/sensitivity_acceptance.json`

Decision rules:
- Do not interpret scaffold Morris screening as final calibrated sensitivity evidence.
- Accept only if parameter ranges, outputs, and Sobol/Morris decision are justified.

Required actions when not ready:
- Review parameter ranges and decide whether Morris is enough or Sobol is required.
- Create sensitivity_acceptance.json after final input and graph scope are accepted.

## Full Experiment Package Agent

- Agent ID: `full_experiment_package_agent`
- Gates: `full_experiment_output`
- Non-ready status: `blocked`
- Mission: Review scripts, configs, manifests, outputs, checksums where available, scenario-policy-seed design, and run instructions for the experiment package.
- Formal acceptance artifacts: `data/manifests/experiment_acceptance.json`

Decision rules:
- Do not accept experiment outputs before input-evidence and graph-scale gates are accepted.
- Expected row counts must match the pilot manifest.

Required actions when not ready:
- Regenerate or accept full outputs after input, graph-scale, and validation gates close.
- Create experiment_acceptance.json with matching run profile and row counts.

## Paper / Report Claim Alignment Agent

- Agent ID: `paper_report_claim_alignment_agent`
- Gates: `manuscript_report_alignment`
- Non-ready status: `blocked`
- Mission: Review paper/report claims against available evidence and flag unsupported, overstated, stale, or operationally risky claims.
- Formal acceptance artifacts: `data/manifests/manuscript_acceptance.json`

Decision rules:
- Do not let manuscript claims outrun accepted evidence gates.
- Keep not-operational and scaffold claim boundaries visible until final acceptance.

Required actions when not ready:
- Revise or hold claims until all supporting evidence gates are accepted.
- Create manuscript_acceptance.json after claim-by-claim review.

## Clean-Checkout Reproducibility Agent

- Agent ID: `clean_checkout_reproducibility_agent`
- Gates: `reproducibility`
- Non-ready status: `blocked`
- Mission: Perform or script clean-checkout reproduction, smoke validation, import-boundary checks, and artifact regeneration without faking a successful full reproduction.
- Formal acceptance artifacts: `data/manifests/reproducibility_acceptance.json`

Decision rules:
- If full clean-checkout reproduction is too expensive, record smoke scope and keep full reproduction blocked.
- Do not treat local passing tests as clean-checkout reproduction.

Required actions when not ready:
- Run or document clean-checkout validation with command log and artifact regeneration evidence.
- Create reproducibility_acceptance.json only after accepted reproduction scope is complete.

## Final Independent Audit Agent

- Agent ID: `final_independent_audit_agent`
- Gates: `final_audit`
- Non-ready status: `blocked`
- Mission: Aggregate all acceptance records, verify every gate is accepted or blocked, and produce the final audit summary only after pre-final gates close.
- Formal acceptance artifacts: `docs/final_study_audit.md`, `data/manifests/final_audit_acceptance.json`

Decision rules:
- Keep final_study_ready false unless every pre-final gate is accepted with evidence.
- Do not create docs/final_study_audit.md as a proxy for actual acceptance.

Required actions when not ready:
- After all pre-final gates are ready, write the independent prompt-to-artifact final audit.
- Create final_audit_acceptance.json only when gate lists and readiness counts match current evidence.
