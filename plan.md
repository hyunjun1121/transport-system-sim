# Unit 2: Clean-Checkout Reproducibility Smoke — Detailed Plan

Parent: `high_level_plan.md` Phase U. This is a decision-support
simulation project; outputs are not operational route plans. Sub-Agent
architecture (Builder / Reviewer / Verifier) inherited from Phase T.

## Mission

Refresh `data/validation/clean_checkout_reproducibility_smoke_manifest.json`
so it references the current HEAD (`55327c4b`) instead of the stale
2026-05-10 commit (`2c15e0f9`). The reproducibility gate itself stays
blocked (needs `reproducibility_acceptance.json`, a human-signoff
artifact the agent must not create). This unit strengthens evidence
freshness, reduces the source-commit lag, and updates downstream review
packets to reference current source state.

## Claim Boundary

This unit produces bounded clean-checkout smoke evidence only. It does
NOT create `reproducibility_acceptance.json`, does NOT close the
reproducibility gate, and does NOT claim clean-environment certification
or publication acceptance. The reproducibility gate stays blocked until
a human reviewer records the acceptance decision.

## Stop Conditions

1. Manifest refreshed with current HEAD as source_commit.
2. `smoke_passed=true`, `clean_checkout_test_performed=true`.
3. `dependency_install_tested=true`, `artifact_regeneration_tested=true`.
4. Affected reproducibility tests pass (smoke, acceptance, decision,
   review packet).
5. Claim guard: `blocking_finding_count=0`.
6. Reproducibility gate remains blocked (acceptance.json absent).

## Root Cause (Confirmed)

The existing manifest was written 2026-05-10 against commit
`2c15e0f9` with 99 dirty source files. Since then Phase T
(commit `163aa75d`) and Phase U1 (commit `55327c4b`) changed the
source tree substantially. The manifest's `source_commit` lags the
review head by many commits, and the reproducibility review/decision
packets report a stale freshness snapshot.

## What This Unit Does NOT Do

- Does NOT create `data/manifests/reproducibility_acceptance.json`
  (human signoff artifact; agent must never create).
- Does NOT flip `reproducibility` gate from blocked to passing
  (still needs acceptance.json).
- Does NOT claim clean-environment certification or publication
  acceptance.

## Steps

### Step 1: Run the clean-checkout smoke

Run with dependency install + artifact regeneration (bounded profile):

```
.\.venv\Scripts\python scripts\run_clean_checkout_smoke.py `
  --install-dependencies --artifact-regeneration
```

This clones the committed source tree into a temp dir, checks out the
exact HEAD (`55327c4b`), creates a fresh venv, installs
requirements.txt, runs the `clean-checkout-minimal` smoke profile, then
regenerates 5 bounded review/audit artifacts inside the clone. Writes
manifest + log + doc back to the source repo.

Expected outer steps (11):
1. git_clone_source_tree
2. git_checkout_source_commit
3. create_clean_checkout_venv
4. upgrade_clean_checkout_pip
5. install_clean_checkout_requirements
6. run_reproducibility_smoke_in_clean_checkout
7. regenerate_reproducibility_review_packet
8. regenerate_reproducibility_decision_packet
9. regenerate_final_audit_decision_packet
10. regenerate_acceptance_audit
11. regenerate_plan_artifact_audit

### Step 2: Verify the refreshed manifest

Confirm the new manifest fields:

- `smoke_passed is True`
- `clean_checkout_test_performed is True`
- `full_clean_environment_tested is True`
- `artifact_regeneration_tested is True`
- `source_commit` matches `55327c4b` (the pre-smoke HEAD)
- `acceptance_ready is False`
- `can_mark_complete is False`
- `final_study_ready is False`

Note: after committing the smoke outputs, the source_commit will be an
ancestor of the new HEAD (lag_count=1), which is expected and handled
by downstream review packets.

### Step 3: Run affected reproducibility tests

```
.\.venv\Scripts\python tests\test_realworld_reproducibility_smoke.py
.\.venv\Scripts\python tests\test_realworld_reproducibility_acceptance.py
.\.venv\Scripts\python tests\test_realworld_reproducibility_decision_packet.py
.\.venv\Scripts\python tests\test_realworld_reproducibility_review_packet.py
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
```

### Step 4: Refresh dirty-worktree classification + claim guard

```
.\.venv\Scripts\python scripts\write_dirty_worktree_classification.py
.\.venv\Scripts\python scripts\audit_claim_language.py
```

Confirm: `blocking_finding_count == 0`, `release_blocked is False`.

### Step 5: Run plan_audit test

```
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
```

### Step 6: Commit + push

```
git add -A
git commit -m "phase U2: refresh clean-checkout smoke manifest to current HEAD"
git push
```

## Expected Outcome

- Manifest source_commit advances from `2c15e0f9` to `55327c4b`.
- Reproducibility review/decision packets reference current freshness.
- Reproducibility gate remains blocked (acceptance.json absent).
- 0 claim-guard blockers; affected tests pass.
