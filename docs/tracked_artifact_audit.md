# Tracked Artifact Audit

This audit checks whether current changed artifacts would be present in a clean checkout of the current Git HEAD. It does not commit files, approve reproducibility, validate evidence quality, or close final-study gates.

## Summary

- Clean-checkout reproducibility ready: `false`
- Can mark complete: `false`
- Changed reproducibility artifacts: 28
- Blocking changed artifacts: 28
- Untracked artifacts: 5
- Modified or staged artifacts: 23

## Changed Artifacts

| Status | Category | Path | Required Action |
| --- | --- | --- | --- |
| M | data_or_manifest | `data/manifests/source_context_cache_decision_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_context_cache_decision_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_context_cache_request_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_context_cache_request_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_license_review_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_license_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_provenance_decision_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_provenance_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_provenance_priority_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_provenance_priority_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_url_review_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/source_context_cache_decision_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/source_context_cache_request_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/source_license_review_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/source_provenance_priority_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | script | `scripts/audit_plan_artifacts.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/reproducibility_smoke.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_acceptance_orchestration.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_final_study_readiness.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_plan_audit.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_source_context_cache_decision_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_source_context_cache_request_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_source_provenance_priority_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| ?? | data_or_manifest | `data/rail/metro9_capacity_source_extract.csv` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | data_or_manifest | `data/rail/metro9_capacity_source_raw.html` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | script | `scripts/cache_metro9_capacity_source.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | realworld_code | `src/realworld/metro9_capacity_source.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |
| ?? | test | `tests/test_realworld_metro9_capacity_source.py` | Add to version control, package explicitly, or exclude from accepted reproduction scope. |

## Use

Run this before clean-checkout reproducibility acceptance. Any row means the current working tree contains changes that a clean checkout of the current Git HEAD would not reproduce unless they are committed, packaged, or explicitly excluded from the accepted reproduction scope. The audit excludes its own generated CSV, manifest, and Markdown outputs from candidate rows so reruns do not create self-blockers.
