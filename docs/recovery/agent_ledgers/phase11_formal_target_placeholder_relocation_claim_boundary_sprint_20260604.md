# Phase 11 Formal Target Placeholder Relocation Claim-Boundary Sprint - 2026-06-04

## Objective

Remove the release-blocking lexical claim-language finding at
`docs/formal_target_placeholder_relocation.md:29` while preserving the note as a
formal-artifact hygiene record.

## Scope Boundary

This sprint changed one hand-written prose phrase in the relocation note. It did
not restore any moved placeholder, create any formal acceptance artifact, close
publication readiness, close final-study readiness, or authorize operational
routing.

## Main-Thread Inspection

- Inspected the blocker row in `data/validation/claim_language_guard.csv`.
- Inspected `docs/formal_target_placeholder_relocation.md`.
- Searched `src`, `scripts`, `tests`, `docs`, and `data/manifests` for
  ownership references to the relocation note and related formal-target
  placeholder wording.

## Edit

- Replaced `final-study audit` with `study-closeout audit` in the sentence
  that states moved placeholder files are not approval evidence.

The sentence still says moved files remain draft/reference material only and
are not formal acceptance records, reviewed road overrides, accepted parameter
records, or a study-closeout audit.

## Commands

| Command | Result | Claim Impact |
| --- | --- | --- |
| `Import-Csv data\validation\claim_language_guard.csv ... docs/formal_target_placeholder_relocation.md ... Format-List` | Exit 0; identified `docs/formal_target_placeholder_relocation.md:29 final` as the release-blocking row | Established the exact target and evidence context before editing. |
| `Get-Content docs\formal_target_placeholder_relocation.md -Raw` | Exit 0; showed the relocation note and the blocker sentence | Confirmed the blocker was in prose, not a structured acceptance artifact. |
| `rg -n "formal_target_placeholder_relocation\|placeholder relocation\|Formal Target\|target_placeholder\|final audit\|final-study\|accepted" src scripts tests docs data\manifests` | Exit 0; did not identify a focused owner generator for this note | Supported a direct Markdown edit rather than regenerating from source. |
| `.\.venv\Scripts\python scripts\audit_claim_language.py --scan-path docs\formal_target_placeholder_relocation.md --output data\validation\tmp_claim_language_guard_placeholder_relocation.csv --doc docs\tmp_claim_language_guard_placeholder_relocation.md --manifest data\validation\tmp_claim_language_guard_placeholder_relocation_manifest.json --fail-on-blockers` | Exit 0; focused scan reported `blocking_finding_count=0` | Confirms this note no longer has a release-blocking lexical finding. |
| Temp focused-guard cleanup for `data\validation\tmp_claim_language_guard_placeholder_relocation.csv`, `docs\tmp_claim_language_guard_placeholder_relocation.md`, and `data\validation\tmp_claim_language_guard_placeholder_relocation_manifest.json` | Exit 0; all temp files absent after cleanup | Prevents temporary guard outputs from entering review packages. |
| `.\.venv\Scripts\python scripts\audit_claim_language.py` | Exit 0; full scan reported `blocking_finding_count=30` | Reduced total release-blocking lexical findings from 31 to 30. Release remains blocked. |
| `.\.venv\Scripts\python tests\test_realworld_claim_language_guard.py` | Exit 0; claim-language guard tests passed | Confirms guard behavior after the full refresh. |
| `git diff --check -- docs\formal_target_placeholder_relocation.md data\validation\claim_language_guard.csv docs\claim_language_guard.md data\validation\claim_language_guard_manifest.json` | Exit 0; PowerShell printed a CRLF normalization warning for `docs/formal_target_placeholder_relocation.md` | No whitespace errors were reported. |

## Result

- `docs/formal_target_placeholder_relocation.md` release-blocking lexical rows:
  `1 -> 0`.
- Overall claim-language guard release-blocking rows: `31 -> 30`.
- `release_blocked=true`, `final_study_ready=false`, and
  `can_mark_complete=false` remain unchanged.

## Remaining Work

Continue Phase 11 claim-language cleanup from the next row in
`data/validation/claim_language_guard_manifest.json`, currently
`docs/integrated_evidence_review_packet.md:21 final`. This sprint did not
address publication-readiness, parameter, road, rail, benchmark, experiment,
manuscript, reproducibility, or formal human-review blockers.
