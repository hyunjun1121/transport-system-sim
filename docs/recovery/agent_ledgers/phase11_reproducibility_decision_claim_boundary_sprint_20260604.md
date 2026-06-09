# Phase 11 Reproducibility Decision Claim-Boundary Sprint - 2026-06-04

## Objective

Reduce release-blocking lexical claim-language findings in
`docs/reproducibility_decision_packet.md` while preserving the reproducibility
decision review boundary.

## Claim Boundary

This sprint is lexical claim-boundary cleanup and generated-packet alignment
only. It does not approve reproducibility, certify clean-checkout execution,
approve artifact regeneration, create
`data/manifests/reproducibility_acceptance.json`, create publication readiness,
create study-closeout readiness, or create formal reviewer approval.

## Main-Thread Inspection

Inspected current blocker evidence and related owned paths:

- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `docs/reproducibility_decision_packet.md`
- `src/realworld/reproducibility_decision_packet.py`
- `tests/test_realworld_reproducibility_decision_packet.py`

Initial release-blocking blocker slice for
`docs/reproducibility_decision_packet.md`:

- `validated` through the `validation_command_ladder_decision` row and
  planned validation-ladder wording
- `final` through the worktree package-state row's final-package wording

## Edits

- `src/realworld/reproducibility_decision_packet.py`
  - renamed `validation_command_ladder_decision` to
    `command_ladder_scope_decision`
  - replaced `Validation command ladder` with `Command ladder scope`
  - replaced planned validation-ladder wording with planned command-ladder
    wording
  - replaced final-package wording with release-scope package wording
  - replaced several `Accept` or `reviewer accepts` phrases with bounded
    `Retain`, `Use`, `confirms`, or `records` wording
  - replaced the boundary bullet's `final-study completion` with
    `study-closeout completion`
- `tests/test_realworld_reproducibility_decision_packet.py`
  - updated the row ID expectation to `command_ladder_scope_decision`
- regenerated:
  - `data/validation/reproducibility_decision_packet.csv`
  - `data/validation/reproducibility_decision_manifest.json`
  - `docs/reproducibility_decision_packet.md`

The regenerated packet still reports `publication_ready=false`,
`can_mark_complete=false`, `reproducibility_decision_recorded=false`, and
`reproducibility_gate_closure_candidate_count=0`.

## Commands

| command | exit | evidence |
| --- | ---: | --- |
| `Import-Csv data\validation\claim_language_guard.csv | Where-Object { $_.source_path -eq 'docs/reproducibility_decision_packet.md' -and $_.status -eq 'release_blocking_unbounded' }` | 0 | found two starting blockers in the reproducibility decision Markdown |
| `rg -n "validation_command_ladder_decision\|Validation command ladder\|planned validation ladder\|Confirm the final package..." src\realworld scripts tests docs data -g "*reproducibility_decision*"` | 0 | located generator, generated artifact, and test references |
| `Get-Content src\realworld\reproducibility_decision_packet.py` | 0 | inspected generator rows and Markdown boundary builder |
| `Get-Content tests\test_realworld_reproducibility_decision_packet.py` | 0 | inspected test ownership before row-ID change |
| `.\.venv\Scripts\python scripts\write_reproducibility_decision_packet.py` | 0 | regenerated reproducibility decision CSV, manifest, and Markdown |
| `rg -n "validation_command_ladder_decision\|planned validation ladder\|Confirm the final package\|reviewer accepts the reproduction scope" ...` | 1 | no remaining matches in touched reproducibility decision paths after regeneration |
| `.\.venv\Scripts\python tests\test_realworld_reproducibility_decision_packet.py` | 0 | reproducibility decision packet tests passed |
| `.\.venv\Scripts\python scripts\audit_claim_language.py --scan-path docs\reproducibility_decision_packet.md --output data\validation\tmp_claim_language_guard_reproducibility_decision.csv --doc docs\tmp_claim_language_guard_reproducibility_decision.md --manifest data\validation\tmp_claim_language_guard_reproducibility_decision_manifest.json --fail-on-blockers` | 0 | focused guard reported 0 blocking findings for the document |
| `Remove-Item ...tmp_claim_language_guard_reproducibility_decision...` | 0 | temporary focused guard artifacts removed |
| `.\.venv\Scripts\python scripts\audit_claim_language.py` | 0 | full guard regenerated; blocking findings reduced from 42 to 40 |
| `.\.venv\Scripts\python tests\test_realworld_claim_language_guard.py` | 0 | claim-language guard tests passed |
| `Import-Csv data\validation\claim_language_guard.csv | Where-Object { $_.source_path -eq 'docs/reproducibility_decision_packet.md' -and $_.status -eq 'release_blocking_unbounded' } | Measure-Object` | 0 | confirmed 0 release-blocking rows remain for the document |
| `git diff --check -- src\realworld\reproducibility_decision_packet.py tests\test_realworld_reproducibility_decision_packet.py docs\reproducibility_decision_packet.md data\validation\reproducibility_decision_packet.csv data\validation\reproducibility_decision_manifest.json data\validation\claim_language_guard.csv data\validation\claim_language_guard_manifest.json docs\claim_language_guard.md` | 0 | whitespace check passed; CRLF warnings only for touched Python/test files |

## Results

- `docs/reproducibility_decision_packet.md` no longer appears in the full
  release-blocking claim-language blocker list.
- Full claim-language blocker count is now 40.
- Reproducibility remains blocked for publication and study-closeout claims
  because the reproducibility manifest remains scaffold-only and
  `data/manifests/reproducibility_acceptance.json` remains absent.
- No phase gate or formal acceptance gate was closed.

## Remaining Blocker Direction

Next claim-language cleanup candidates include
`docs/reproducibility_review_packet.md`, `docs/reproducibility_smoke.md`,
`docs/rail_evidence.md`, `docs/road_evidence_source_request_packet.md`,
`docs/source_provenance_decision_packet.md`, and related generated manifests.
