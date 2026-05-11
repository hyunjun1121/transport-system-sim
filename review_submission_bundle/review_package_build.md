# Review Package Build

This ZIP builder assembles files for external review from the package inventory. It does not validate evidence quality, approve formal acceptance records, certify calibration, or close final-study gates.

## Verdict

- Review package ZIP ready: `true`
- Acceptance ready: `false`
- Can mark complete: `false`
- Selected files: 813
- Excluded files: 0
- Excluded formal targets: 0
- Missing files: 0

## ZIP

- Path: `required_deliverables.zip`
- Size bytes: 6461279
- SHA256: `07668c32ae0d1be057e5801d8073496173fd3b67886e7d8755be000257b94356`
- Include formal targets: `false`

## Missing Paths

- none

## Use

Send this ZIP only with the consultation context and package inventory. It is a review handoff bundle, not an acceptance package. Formal acceptance still depends on reviewer decisions and the formal gate audits. After copying the ZIP to the mirrored review-package path, run `scripts\write_expert_review_handoff.py --fail-on-zip-mismatch` and send `review_packages/expert_review_handoff_20260510.md` plus `review_packages/expert_review_handoff_20260510.json` outside the ZIP so checksum reporting does not mutate the package.
