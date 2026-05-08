# Reproducibility Review Packet

> Current project status (2026-05-08): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


`data/validation/reproducibility_review_packet.csv` is a reviewer worksheet for
the clean-checkout reproducibility gate. It is not an acceptance record and it
does not close `data/manifests/reproducibility_acceptance.json`.

## Purpose

The packet makes the clean-checkout blocker auditable by checking:

- whether the reproducibility manifest still declares scaffold-only scope;
- whether the formal reproducibility acceptance record is absent or separate;
- whether the current Git worktree is clean enough for a reproducible package;
- whether untracked generated artifacts could be missing from a fresh checkout;
- whether the validation command ladder is present;
- whether runtime code imports from `cloned_repo`;
- whether bounded clean source-checkout smoke evidence exists;
- whether a full clean-environment reproduction is still required.

## Command

```powershell
.\.venv\Scripts\python scripts\write_reproducibility_review_packet.py
```

The command writes:

- `data/validation/reproducibility_review_packet.csv`
- `data/validation/reproducibility_review_manifest.json`

## Current-Worktree Smoke Companion

Use this command when a reviewer needs bounded execution evidence from the
current worktree:

```powershell
.\.venv\Scripts\python scripts\run_reproducibility_smoke.py
```

It writes `data/validation/reproducibility_smoke_manifest.json`,
`data/validation/reproducibility_smoke_log.jsonl`, and
`docs/reproducibility_smoke.md`. The smoke output is useful for command-ladder
review, but it is not clean-checkout reproduction and cannot close
`data/manifests/reproducibility_acceptance.json`.

## Bounded Clean-Checkout Smoke Companion

Use this command when a reviewer needs evidence from a fresh clone of the
committed source tree:

```powershell
.\.venv\Scripts\python scripts\run_clean_checkout_smoke.py
```

It writes `data/validation/clean_checkout_reproducibility_smoke_manifest.json`,
`data/validation/clean_checkout_reproducibility_smoke_log.jsonl`, and
`docs/clean_checkout_reproducibility_smoke.md`. This is bounded
source-checkout evidence using the current Python environment. It is not a
clean-environment dependency reinstall, full validation ladder, artifact
regeneration acceptance, or formal reviewer approval.

## Tracked-Artifact Audit Companion

Use this command when a reviewer needs a concrete list of changed artifacts
that a clean checkout of current Git HEAD would not reproduce:

```powershell
.\.venv\Scripts\python scripts\audit_tracked_artifacts.py
```

It writes `data/validation/tracked_artifact_audit.csv`,
`data/validation/tracked_artifact_audit_manifest.json`, and
`docs/tracked_artifact_audit.md`. This is packaging hygiene only; it does not
commit files, accept reproducibility, or close the final-study gate. The audit
excludes those three generated outputs from candidate rows so reruns do not
create self-blockers.

## Claim Boundary

This packet records review status only. A reviewer still needs to decide
whether bounded clean-checkout smoke is sufficient for the intended scope or
whether a full clean-environment reproduction is required, review command logs,
confirm artifact regeneration, verify manifest paths, check the runtime import
boundary, and then create `data/manifests/reproducibility_acceptance.json` if
the package is accepted.
