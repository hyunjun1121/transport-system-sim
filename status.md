# Project Status

## Current Date And Workspace

- Date: 2026-06-09
- Workspace: `C:\project\transport-system-sim`
- Platform: Windows PowerShell
- Git branch: `main`
- Remote: `https://github.com/hyunjun1121/transport-system-sim.git`

## Latest Audit Snapshot

- `final_study_ready=false`
- Gate count: 15
- Ready gates: 3/15: `real_input_smoke`, `structured_disruptions`, `policy_alternatives`
- Blocked gates: 12/15: `pilot_region_accepted`, `cached_osm_input`, `graph_scale_strategy`, `data_provenance`, `parameter_evidence`, `rail_evidence`, `validation_package`, `sensitivity_analysis`, `full_experiment_output`, `manuscript_report_alignment`, `reproducibility`, `final_audit`
- Formal acceptance: 0/12 (all 12 formal artifacts intentionally absent until reviewer signoff)
- `publication_ready=false`
- `formal_acceptance_evidence=false`
- Claim-language guard: `blocking_finding_count=0`, `release_blocked=false`
- Dirty worktree: 616 uncommitted paths

## Key Metrics

- Phase gate ledgers: 13/13 present, 0 closed
- Artifact invalidation: 51 rows, 31 closed, 20 pending
- Review package ZIP: rebuilt 2026-06-09, 1319 files, mirror synced
- Pilot result files: 88
- Codebase: src 167 files, tests 163 files, scripts 135 files, docs 128 files
- No stub or empty source/test/script files

## Known Limitations

- Road speed: OSM `maxspeed` coverage sparse (5/10 classes have observed tags)
- Road capacity: OSM `lanes` tags absent (0/10 classes observed)
- Rail timing: headway/travel time are assumption proxies, not derived from GTFS/timetable
- Reproducibility: `clean_checkout_test_performed=false` (current-worktree smoke only)
- Critical-link blockage: reduced corridor multimodal fails 100% vs multi-corridor 0%
  in `songpa_critical_link_blockage` scenario (alternate-route gap documented in
  graph-scale decision packet)

## Review Package State

- `required_deliverables.zip`: expert-review handoff ZIP, rebuilt 2026-06-09
- `review_packages/expert_review_package.zip`: mirror copy, SHA256 matching
- `review_packages/expert_review_handoff_20260510.json`: sidecar with checksum and
  non-acceptance cover note, regenerated 2026-06-09
- `docs/review_package_build.md`: build manifest with file list and SHA256

## Study Scope

This is a decision-support simulation framework. It is not:
- an operational route plan
- a real-world forecast
- calibrated field validation
- publication-ready
- final-study-ready

Allowed framing: decision-support simulation, quasi-real input pipeline, stochastic
scenario comparison, resilience/sensitivity analysis, ML-assisted post-simulation
risk classification when runtime evidence supports the specific claim.

## Detailed Records

Detailed implementation notes, artifact lists, and per-phase status are in:
- `AGENTS.md`: repository structure and conventions
- `plan.md`: remaining work guide
- `docs/plan_completion_audit.md`: gate-by-gate audit snapshot
- `docs/current_goal_completion_audit.md`: goal completion audit
- `docs/publication_readiness_audit.md`: publication readiness audit
- `docs/phase_gate_ledger_audit.md`: phase gate ledger audit
- `docs/artifact_invalidation_matrix.md`: stale artifact disposition
