# Tracked Artifact Audit

This audit checks whether current changed artifacts would be present in a clean checkout of the current Git HEAD. It does not commit files, approve reproducibility, validate evidence quality, or close final-study gates.

## Summary

- Clean-checkout reproducibility ready: `false`
- Can mark complete: `false`
- Changed reproducibility artifacts: 6
- Blocking changed artifacts: 6
- Untracked artifacts: 0
- Modified or staged artifacts: 6

## Changed Artifacts

| Status | Category | Path | Required Action |
| --- | --- | --- | --- |
| M | data_or_manifest | `data/manifests/source_provenance_priority_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_url_remediation_manifest.json` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | data_or_manifest | `data/manifests/source_url_remediation_packet.csv` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | documentation | `docs/source_url_remediation_packet.md` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | realworld_code | `src/realworld/source_url_remediation_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |
| M | test | `tests/test_realworld_source_url_remediation_packet.py` | Commit, stash, or document this change before clean-checkout reproduction. |

## Use

Run this before clean-checkout reproducibility acceptance. Any row means the current working tree contains changes that a clean checkout of the current Git HEAD would not reproduce unless they are committed, packaged, or explicitly excluded from the accepted reproduction scope. The audit excludes its own generated CSV, manifest, and Markdown outputs from candidate rows so reruns do not create self-blockers.
