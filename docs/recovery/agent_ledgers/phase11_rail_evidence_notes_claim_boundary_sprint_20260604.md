# Phase 11 Rail Evidence Notes Claim-Boundary Sprint - 2026-06-04

## Objective

Remove the release-blocking lexical claim-language findings at
`docs/rail_evidence.md:79` and `docs/rail_evidence.md:208` while preserving the
document as a current-state rail evidence note.

## Scope Boundary

This sprint changed two hand-written prose phrases in `docs/rail_evidence.md`.
It did not create rail timing evidence, rail capacity evidence, GTFS evidence,
publication readiness, final-study readiness, formal acceptance, or operational
rail routing authority.

## Main-Thread Inspection

- Inspected both blocker rows in `data/validation/claim_language_guard.csv`.
- Inspected `docs/rail_evidence.md`.
- Searched `src/realworld`, `scripts`, `tests`, `docs`, `data/rail`, and
  `data/manifests` for rail evidence document ownership references.
- Inspected `src/realworld/rail_evidence.py`.
- Inspected `scripts/audit_rail_evidence.py`.
- Inspected `tests/test_realworld_rail_evidence.py`.

## Edit

- Replaced `Validation and audit helpers:` with `Schema and audit helpers:`.
- Replaced `For final-study rail claims` with `For release-scope rail claims`.

The surrounding text still says current rail values are assumption proxies,
publication readiness is false until cached evidence is supplied, and official
station-code binding is separate from rail-service evidence.

## Commands

| Command | Result | Claim Impact |
| --- | --- | --- |
| `Import-Csv data\validation\claim_language_guard.csv ... docs/rail_evidence.md ... Format-List` | Exit 0; identified two release-blocking rows: `docs/rail_evidence.md:79 validated` and `docs/rail_evidence.md:208 final` | Established the exact target rows and evidence context before editing. |
| `Get-Content docs\rail_evidence.md -Raw` | Exit 0; showed the current rail evidence note and both blocker phrases | Confirmed the blocker phrases were hand-written Markdown. |
| `rg -n "rail_evidence.md\|Rail Evidence Notes\|Validation and audit helpers\|For final-study rail claims\|final-study rail claims\|Validation and audit" ...` | Exit 0; no source generator for `docs/rail_evidence.md` was found | Supported a direct Markdown edit rather than regenerating from source. |
| `Get-Content src\realworld\rail_evidence.py -Raw` | Exit 0; inspected rail evidence validator and current conservative boundary logic | Confirmed no rail evidence readiness semantics needed to change. |
| `.\.venv\Scripts\python scripts\audit_claim_language.py --scan-path docs\rail_evidence.md --output data\validation\tmp_claim_language_guard_rail_evidence.csv --doc docs\tmp_claim_language_guard_rail_evidence.md --manifest data\validation\tmp_claim_language_guard_rail_evidence_manifest.json --fail-on-blockers` | Exit 0; focused scan reported `blocking_finding_count=0` | Confirms this document no longer has release-blocking lexical findings. |
| `.\.venv\Scripts\python tests\test_realworld_rail_evidence.py` | Exit 0; rail evidence tests passed | Confirms rail evidence cache validation remains unchanged. |
| Temp focused-guard cleanup for `data\validation\tmp_claim_language_guard_rail_evidence.csv`, `docs\tmp_claim_language_guard_rail_evidence.md`, and `data\validation\tmp_claim_language_guard_rail_evidence_manifest.json` | Exit 0; all temp files absent after cleanup | Prevents temporary guard outputs from entering review packages. |
| `.\.venv\Scripts\python scripts\audit_claim_language.py` | Exit 0; full scan reported `blocking_finding_count=27` | Reduced total release-blocking lexical findings from 29 to 27. Release remains blocked. |
| `.\.venv\Scripts\python tests\test_realworld_claim_language_guard.py` | Exit 0; claim-language guard tests passed | Confirms guard behavior after the full refresh. |
| `git diff --check -- docs\rail_evidence.md data\validation\claim_language_guard.csv docs\claim_language_guard.md data\validation\claim_language_guard_manifest.json` | Exit 0; PowerShell printed a CRLF normalization warning for `docs/rail_evidence.md` | No whitespace errors were reported. |

## Result

- `docs/rail_evidence.md` release-blocking lexical rows: `2 -> 0`.
- Overall claim-language guard release-blocking rows: `29 -> 27`.
- `release_blocked=true`, `final_study_ready=false`, and
  `can_mark_complete=false` remain unchanged.

## Remaining Work

Continue Phase 11 claim-language cleanup from the next row in
`data/validation/claim_language_guard_manifest.json`, currently
`docs/rail_transit_stress_profile_packet.md:33 final`. This sprint did not
address rail source decisions, publication-readiness, parameter, road,
benchmark, experiment, manuscript, reproducibility, or formal human-review
blockers.
