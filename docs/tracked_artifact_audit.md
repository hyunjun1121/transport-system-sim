# Tracked Artifact Audit

This audit checks whether current changed artifacts would be present in a clean checkout of the current Git HEAD. It does not commit files, approve reproducibility, validate evidence quality, or close final-study gates.

## Summary

- Clean-checkout reproducibility ready: `false`
- Can mark complete: `false`
- Changed reproducibility artifacts: 16
- Blocking changed artifacts: 16
- Untracked artifacts: 6
- Modified or staged artifacts: 10

## Changed Artifacts

| Status | Category | Path | Required Action |
| --- | --- | --- | --- |
| M | root_document_or_config | `plan.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | script | `scripts/audit_plan_artifacts.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | script | `scripts/run_acceptance_audit.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/acceptance_orchestration.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/final_study_readiness.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/reproducibility_smoke.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | root_document_or_config | `status.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_acceptance_orchestration.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_final_study_readiness.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_plan_audit.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| ?? | data_or_manifest | `data/parameters/parameter_source_decision_manifest.json` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | data_or_manifest | `data/parameters/parameter_source_decision_packet.csv` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | documentation | `docs/parameter_source_decision_packet.md` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | script | `scripts/write_parameter_source_decision_packet.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | realworld_code | `src/realworld/parameter_source_decision_packet.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_parameter_source_decision_packet.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |

## Use

Run this before clean-checkout reproducibility acceptance. Any row means the current working tree contains changes that a clean checkout of the current Git HEAD would not reproduce unless they are committed, packaged, or explicitly excluded from the accepted reproduction scope. The audit excludes its own generated CSV, manifest, and Markdown outputs from candidate rows so reruns do not create self-blockers.
