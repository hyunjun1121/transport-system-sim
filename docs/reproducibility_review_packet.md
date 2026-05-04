# Reproducibility Review Packet

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
- whether a real clean-checkout execution log exists.

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

## Tracked-Artifact Audit Companion

Use this command when a reviewer needs a concrete list of changed artifacts
that a clean checkout of current Git HEAD would not reproduce:

```powershell
.\.venv\Scripts\python scripts\audit_tracked_artifacts.py
```

It writes `data/validation/tracked_artifact_audit.csv`,
`data/validation/tracked_artifact_audit_manifest.json`, and
`docs/tracked_artifact_audit.md`. This is packaging hygiene only; it does not
commit files, accept reproducibility, or close the final-study gate.

## Claim Boundary

This packet records review status only. A reviewer still needs to run or inspect
a fresh-clone or exported-package reproduction, review command logs, confirm
artifact regeneration, verify manifest paths, check the runtime import
boundary, and then create `data/manifests/reproducibility_acceptance.json` if
the package is accepted.
