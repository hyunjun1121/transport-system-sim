# Phase 11 Pilot Experiment Design Claim-Boundary Sprint - 2026-06-04

## Scope

- Objective: remove release-blocking claim-language findings from the pilot
  experiment design manifest without changing profile dimensions, seeds,
  policy IDs, scenario IDs, or graph-reduction semantics.
- Ownership:
  - `data/manifests/pilot_experiment_design.json`
  - claim-language guard outputs
  - dirty-worktree classification outputs
- Out of scope:
  - Phase 8 or Phase 9 gate closure
  - graph-scale method selection
  - experiment acceptance
  - publication-readiness or final-study signoff

## Inspected Evidence

- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `data/manifests/pilot_experiment_design.json`
- `src/realworld/pilot_experiments.py`
- `scripts/run_pilot_experiments.py`
- `tests/test_realworld_pilot_experiments.py`
- `docs/recovery/agent_ledgers/phase8_compact_engineering_probe_20260603.md`

## Edits

- Reworded non-formal design status values:
  - `accepted_staged_profile_for_prepublication_execution` ->
    `review_scoped_staged_profile_for_prepublication_execution`
  - `accepted_full_profile_pending_input_validation_and_compute_budget` ->
    `review_scoped_full_profile_pending_input_validation_and_compute_budget`
  - `candidate_graph_scale_upgrade_pending_acceptance` ->
    `candidate_graph_scale_upgrade_pending_review`
  - `candidate_graph_scale_full_profile_pending_acceptance` ->
    `candidate_graph_scale_full_profile_pending_review`
- Reworded graph-scale and profile descriptions:
  - `accepted real-world redundant-corridor graph variant` ->
    `reviewed real-world redundant-corridor graph variant`
  - `accepted policy alternatives` -> `current policy-alternative list`
  - `accepted scenario-policy matrix` -> `current scenario-policy matrix`
  - `method is accepted` -> `method is reviewed`
  - `not_accepted` -> `not_selected`
  - `input validation` -> `input checks`
  - `treating either method as accepted` -> `treating either method as selected`

## Verification Commands

```powershell
.\.venv\Scripts\python - <<'PY'
import json
from pathlib import Path
json.loads(Path('data/manifests/pilot_experiment_design.json').read_text(encoding='utf-8'))
print('json_ok')
PY
.\.venv\Scripts\python .\tests\test_realworld_pilot_experiments.py
.\.venv\Scripts\python .\scripts\audit_claim_language.py --scan-path .\data\manifests\pilot_experiment_design.json --output .\data\validation\tmp_claim_language_guard_pilot_design.csv --manifest .\data\validation\tmp_claim_language_guard_pilot_design_manifest.json --doc .\docs\tmp_claim_language_guard_pilot_design.md
Remove-Item -LiteralPath .\data\validation\tmp_claim_language_guard_pilot_design.csv, .\data\validation\tmp_claim_language_guard_pilot_design_manifest.json, .\docs\tmp_claim_language_guard_pilot_design.md
.\.venv\Scripts\python .\scripts\audit_claim_language.py
.\.venv\Scripts\python .\tests\test_realworld_claim_language_guard.py
.\.venv\Scripts\python .\scripts\write_dirty_worktree_classification.py
.\.venv\Scripts\python .\tests\test_realworld_plan_audit.py
```

## Results

- JSON parse check passed.
- Pilot experiment tests passed.
- Focused claim-language guard for `data/manifests/pilot_experiment_design.json`:
  - initial focused blocker count: `4`
  - final focused blocker count: `0`
  - `claim_language_guard_ready=true`
  - `release_blocked=false`
- Full claim-language guard:
  - before this sprint: `blocking_finding_count=91`
  - after this sprint: `blocking_finding_count=87`
  - `claim_language_guard_ready=false`
  - `release_blocked=true`
- Claim-language guard tests passed.
- Dirty worktree classification before this ledger was added:
  - `classified_path_count=534`
  - `unclassified_path_count=0`
- Plan artifact audit test passed.

## Residual Risks

- The edits are claim-boundary wording only; no experiment, graph-scale,
  publication, or final-study gate was closed.
- The pilot design manifest remains a non-acceptance experiment design input.
- Full claim-language guard still has 87 release-blocking findings.
- Dirty worktree paths still require owner, lineage, and package decisions
  before release or final-study claims.
