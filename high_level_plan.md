# Phase U: Automated Gate Closure & Evidence Strengthening

## Mission

Phase T complete. 13/15 gates blocked. Most need human-signoff acceptance
artifacts (agent must not create). Phase U executes every automated action
that advances gates without overclaiming, then leaves human-signoff gates
honestly blocked.

## Core Values

1. Honest evidence from cached sources; never fabricate or accept.
2. True reproducibility via clean-checkout, not worktree smoke.
3. Decision-ready packets so reviewers face minimal extra work.
4. Claim discipline: agent never writes `*_acceptance.json`.
5. No regression: 163 tests pass, claim guard clean.

## Phase T Summary (Complete)

Mechanism A reverted; disruptions deterministic. Road noise (sigma) +
turnaround noise (lambda) are sole within-scenario variance sources.
Morris: 16 params, 61,824 rows, 23,373 non-zero mu_star. Paper §9.9/§10.7
honest. 163 tests pass. Commit `163aa75d` (2026-06-17).

## Stop Conditions

1. structured_disruptions gate ready.
2. reproducibility: clean_checkout_test_performed=true.
3. Rail headway + capacity evidence derived; GTFS attempt documented.
4. Road override refined from observed candidates.
5. Strengthened evidence flows into regenerated review packets.
6. Truth table / stats / figures regenerated if results changed.
7. Claim guard clean; 163 tests pass.
8. final_study_ready stays false (human gates remain blocked).
9. 2 sub-agent reviewers confirm zero critical findings.

---

## Task Units

Status legend: [ ] pending, [~] in-progress, [x] done.

### 1. Disruption scenario manifest [x]
Run `write_disruption_scenario_manifest.py` → emit
`data/scenarios/disruption_scenarios_manifest.json` (SHA256, row count,
claim flags). Dep: none. Impact: +1 ready gate (3→4).

### 2. Clean-checkout reproducibility smoke [x]
Run `run_clean_checkout_smoke.py --install-dependencies
--artifact-regeneration` → fresh clone + venv + smoke ladder. Expected:
`clean_checkout_test_performed=true`. Dep: best after #1. Impact:
reproducibility blockers 6→ fewer.

### 3. Rail headway evidence derivation [x]
Run `derive_rail_headway_evidence.py` against static timetable cache (241
access events, station 4136). Write headway evidence rows with source
SHA256. Dep: none. Impact: rail_evidence headway blockers resolve.

### 4. Rail capacity evidence derivation [x]
Derive Metro9 capacity (922 total, 6 cars) from
`metro9_capacity_source_extract.csv` into evidence row with pending-review
flag + source SHA256. Check `cache_metro9_capacity_source.py`; add thin
derive wrapper if needed. Dep: none. Impact: rail_evidence capacity
blockers weaken.

### 5. Rail GTFS derivation attempt [ ]
KTDB extract is metadata only, not a feed. Run
`derive_rail_gtfs_evidence.py`; expected documented "feed absent" result.
Ensure rail fetch readiness packet shows clean "GTFS attempted, feed
absent". Dep: none. Impact: documentation only, no overclaim.

### 6. Road override candidate refinement [ ]
Update `road_class_overrides_draft.csv` to mark observed maxspeed rows
(5/10 classes) as `source_kind=observed_osm_tag`; keep rest as
`expert_assumption`. Do NOT create `road_class_overrides.csv` (human
signoff). Dep: none. Impact: weakens cached_osm_input blockers for
observed classes.

### 7. Parameter evidence priority refresh [ ]
Rerun `write_parameter_evidence_priority_packet.py` to reflect derived
rail + refined road evidence. Dep: #3, #4, #6. Impact: parameter
worksheet statuses update.

### 8. Full-graph experiment feasibility probe [ ]
Multi-corridor-full already done (2.2 MB). Probe full bus-practical graph
(4,608 nodes) with reduced seeds first; scale to 30 seeds only if bounded.
If tractable: write `pilot_full_graph_*` outputs. If not: document runtime
estimate, keep multi-corridor-full as strongest. Dep: #1. Impact:
strengthens graph_scale_strategy; no gate close.

### 9. Integrated review packet regeneration [ ]
Regenerate cross-cutting packets after #1-#8: claim_alignment,
manuscript_report, experiment_package, rail_evidence, road_evidence,
integrated_evidence, upstream_lineage. Dep: #1-#8. Impact: reviewer
decision-ready intake.

### 10. Result regeneration (conditional) [ ]
If #8 produced new results OR evidence changed assumptions: regenerate
truth table, statistics, figures. If nothing changed: skip, document why.
Dep: #8 outcome.

### 11. Full verification [ ]
Run 163 tests in batches. Claim guard: blocking=0, release_blocked=false.
Record ready/blocked gate counts. Refresh dirty-worktree classification +
plan audit test. Dep: #1-#10.

### 12. Independent sub-agent review [ ]
Spawn 2-3 read-only reviewers: evidence integrity, packet consistency,
claim boundary. Expected: zero critical findings; fix cycle if any (max 3).
Dep: #11.

### 13. Closeout [ ]
Update status.md + AGENTS.md with Phase U results. Commit + push. Confirm
final_study_ready value. Dep: #12.

---

## Priority Order

1 → 2 → (3+4 parallel) → 5 → 6 → 7 → 8 (probe then decide) → 9 → 10
(conditional) → 11 → 12 → 13.

## Hard Constraints

- Never create `*_acceptance.json`, `parameter_acceptance.csv`,
  `final_study_audit.md` without human signoff.
- Never claim calibration, operational authority, acceptance.
- Never weaken a test to pass; fix underlying issue.
- Keep final_study_ready=false, publication_ready=false,
  formal_acceptance_evidence=false unless every gate independently ready.

## Workflow Per Task Unit

1. Read this file → identify current unit.
2. Write detailed `plan.md` (English) for current unit only.
3. Context compact.
4. Execute `plan.md` (Builder → Verifier → Reviewer → self-refine).
5. Context compact.
6. Review completed work, mark done.
7. `git add -A && git commit && git push` (every unit ends with commit/push).
8. Move to next unit.
