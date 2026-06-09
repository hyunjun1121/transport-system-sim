# Phase 11 Reproducibility Review Claim-Boundary Sprint - 2026-06-04

## Objective

Reduce release-blocking lexical claim-language findings in
`docs/reproducibility_review_packet.md` while preserving its reviewer-worksheet
and non-acceptance boundary.

## Claim Boundary

This sprint is lexical claim-boundary cleanup only. It does not approve
reproducibility, certify clean-checkout execution, approve artifact
regeneration, create `data/manifests/reproducibility_acceptance.json`, create
publication readiness, create study-closeout readiness, or create formal
reviewer approval.

## Main-Thread Inspection

Inspected current blocker evidence and related owned paths:

- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `docs/reproducibility_review_packet.md`
- `scripts/write_reproducibility_review_packet.py`
- `src/realworld/reproducibility_review_packet.py`
- `tests/test_realworld_reproducibility_review_packet.py`

Initial release-blocking blocker slice for
`docs/reproducibility_review_packet.md`:

- `validated` through purpose text that said the validation command ladder was
  present
- `accepted` through claim-boundary text that said the package is accepted

## Edits

- `docs/reproducibility_review_packet.md`
  - replaced `validation command ladder` with `command ladder` in the purpose
    checklist
  - replaced `if the package is accepted` with a source-backed reviewer
    decision condition

The Markdown file is static support text. The CSV/manifest writer was inspected
but not changed because this sprint did not change row semantics or generated
evidence structure.

## Commands

| command | exit | evidence |
| --- | ---: | --- |
| `Import-Csv data\validation\claim_language_guard.csv | Where-Object { $_.source_path -eq 'docs/reproducibility_review_packet.md' -and $_.status -eq 'release_blocking_unbounded' }` | 0 | found two starting blockers in the reproducibility review Markdown |
| `rg -n "validated\|accepted\|final\|ready\|validation\|accept" src\realworld\reproducibility_review_packet.py tests\test_realworld_reproducibility_review_packet.py docs\reproducibility_review_packet.md data\validation\reproducibility_review_packet.csv data\validation\reproducibility_review_manifest.json` | 0 | inspected generator, generated artifacts, tests, and Markdown terms |
| `Get-Content scripts\write_reproducibility_review_packet.py` | 0 | confirmed the writer emits CSV/manifest and does not regenerate the Markdown file |
| `Get-Content docs\reproducibility_review_packet.md` | 0 | inspected static Markdown before editing |
| `.\.venv\Scripts\python scripts\audit_claim_language.py --scan-path docs\reproducibility_review_packet.md --output data\validation\tmp_claim_language_guard_reproducibility_review.csv --doc docs\tmp_claim_language_guard_reproducibility_review.md --manifest data\validation\tmp_claim_language_guard_reproducibility_review_manifest.json --fail-on-blockers` | 0 | focused guard reported 0 blocking findings for the document |
| `Remove-Item ...tmp_claim_language_guard_reproducibility_review...` | 0 | temporary focused guard artifacts removed |
| `.\.venv\Scripts\python scripts\audit_claim_language.py` | 0 | full guard regenerated; blocking findings reduced from 40 to 38 |
| `.\.venv\Scripts\python tests\test_realworld_claim_language_guard.py` | 0 | claim-language guard tests passed |
| `Import-Csv data\validation\claim_language_guard.csv | Where-Object { $_.source_path -eq 'docs/reproducibility_review_packet.md' -and $_.status -eq 'release_blocking_unbounded' } | Measure-Object` | 0 | confirmed 0 release-blocking rows remain for the document |
| `git diff --check -- docs\reproducibility_review_packet.md data\validation\claim_language_guard.csv data\validation\claim_language_guard_manifest.json docs\claim_language_guard.md` | 0 | whitespace check passed; CRLF warning only for the Markdown file |

## Results

- `docs/reproducibility_review_packet.md` no longer appears in the full
  release-blocking claim-language blocker list.
- Full claim-language blocker count is now 38.
- Reproducibility remains blocked for publication and study-closeout claims
  because full clean-environment reproduction, package-state closure, and
  `data/manifests/reproducibility_acceptance.json` remain unresolved.
- No phase gate or formal acceptance gate was closed.

## Remaining Blocker Direction

Next claim-language cleanup candidates include `docs/reproducibility_smoke.md`,
`docs/rail_evidence.md`, `docs/road_evidence_source_request_packet.md`,
`docs/source_provenance_decision_packet.md`, and related generated manifests.
