# Phase 11 Reproducibility Smoke Claim-Boundary Sprint - 2026-06-04

## Objective

Reduce release-blocking lexical claim-language findings in
`docs/reproducibility_smoke.md` while preserving bounded current-worktree smoke
semantics.

## Claim Boundary

This sprint is lexical claim-boundary cleanup and smoke-artifact regeneration
only. It does not approve reproducibility, certify clean-checkout execution,
approve artifact regeneration, create
`data/manifests/reproducibility_acceptance.json`, create publication readiness,
create study-closeout readiness, or create formal reviewer approval.

## Main-Thread Inspection

Inspected current blocker evidence and related owned paths:

- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `docs/reproducibility_smoke.md`
- `data/validation/reproducibility_smoke_manifest.json`
- `src/realworld/reproducibility_smoke.py`
- `scripts/run_reproducibility_smoke.py`
- `tests/test_realworld_reproducibility_smoke.py`

Initial release-blocking blocker slice for `docs/reproducibility_smoke.md`:

- `validated` through required-action wording about the full validation ladder
- `accepted` through required-action wording about human review accepting the
  clean-checkout package

## Edits

- `src/realworld/reproducibility_smoke.py`
  - replaced `full validation ladder` with `full command ladder`
  - replaced `human review accepts the clean-checkout package` with
    `human review records the clean-checkout package decision`
- regenerated from existing smoke command results:
  - `data/validation/reproducibility_smoke_manifest.json`
  - `data/validation/reproducibility_smoke_log.jsonl`
  - `docs/reproducibility_smoke.md`

The regenerated smoke manifest still reports `smoke_passed=true`,
`command_count=9`, `passed_count=9`, `acceptance_ready=false`,
`publication_ready=false`, `final_study_ready=false`, and
`can_mark_complete=false`.

## Commands

| command | exit | evidence |
| --- | ---: | --- |
| `Import-Csv data\validation\claim_language_guard.csv | Where-Object { $_.source_path -eq 'docs/reproducibility_smoke.md' -and $_.status -eq 'release_blocking_unbounded' }` | 0 | found two starting blockers in the reproducibility smoke Markdown |
| `rg -n "full validation ladder\|accepted\|acceptance\|validated\|validation" src\realworld\reproducibility_smoke.py scripts\run_reproducibility_smoke.py tests\test_realworld_reproducibility_smoke.py docs\reproducibility_smoke.md data\validation\reproducibility_smoke_manifest.json` | 0 | located smoke generator and generated output terms |
| `Get-Content src\realworld\reproducibility_smoke.py` | 0 | inspected manifest and Markdown generation code |
| inline Python using `write_reproducibility_smoke_outputs(results=...)` from existing manifest commands | 0 | regenerated smoke manifest, log, and Markdown without rerunning the full smoke command ladder |
| `.\.venv\Scripts\python tests\test_realworld_reproducibility_smoke.py` | 0 | reproducibility smoke tests passed |
| `.\.venv\Scripts\python scripts\audit_claim_language.py --scan-path docs\reproducibility_smoke.md --output data\validation\tmp_claim_language_guard_reproducibility_smoke.csv --doc docs\tmp_claim_language_guard_reproducibility_smoke.md --manifest data\validation\tmp_claim_language_guard_reproducibility_smoke_manifest.json --fail-on-blockers` | 0 | focused guard reported 0 blocking findings for the document |
| `rg -n "full validation ladder\|human review accepts the clean-checkout package" src\realworld\reproducibility_smoke.py docs\reproducibility_smoke.md data\validation\reproducibility_smoke_manifest.json` | 1 | no remaining matches in touched smoke paths |
| `Remove-Item ...tmp_claim_language_guard_reproducibility_smoke...` | 0 | temporary focused guard artifacts removed |
| `.\.venv\Scripts\python scripts\audit_claim_language.py` | 0 | full guard regenerated; blocking findings reduced from 38 to 36 |
| `.\.venv\Scripts\python tests\test_realworld_claim_language_guard.py` | 0 | claim-language guard tests passed |
| `Import-Csv data\validation\claim_language_guard.csv | Where-Object { $_.source_path -eq 'docs/reproducibility_smoke.md' -and $_.status -eq 'release_blocking_unbounded' } | Measure-Object` | 0 | confirmed 0 release-blocking rows remain for the document |
| `git diff --check -- src\realworld\reproducibility_smoke.py docs\reproducibility_smoke.md data\validation\reproducibility_smoke_manifest.json data\validation\reproducibility_smoke_log.jsonl data\validation\claim_language_guard.csv data\validation\claim_language_guard_manifest.json docs\claim_language_guard.md` | 0 | whitespace check passed; CRLF warning only for the Python file |

## Results

- `docs/reproducibility_smoke.md` no longer appears in the full
  release-blocking claim-language blocker list.
- Full claim-language blocker count is now 36.
- Reproducibility remains blocked for publication and study-closeout claims
  because this smoke run is current-worktree scope only and
  `data/manifests/reproducibility_acceptance.json` remains absent.
- No phase gate or formal acceptance gate was closed.

## Remaining Blocker Direction

Next claim-language cleanup candidates include
`docs/clean_checkout_reproducibility_smoke.md`, `docs/rail_evidence.md`,
`docs/road_evidence_source_request_packet.md`,
`docs/source_provenance_decision_packet.md`, and related generated manifests.
