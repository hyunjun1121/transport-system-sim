# Phase 11 Source Provenance Decision Claim-Boundary Sprint - 2026-06-04

## Objective

Lower unbounded claim-language in the source-provenance decision packet without
changing provenance gate status, creating formal acceptance records, or
promoting any source/license/cache evidence.

## Scope

Inspected:

- `data/validation/claim_language_guard.csv`
- `src/realworld/source_provenance_decision_packet.py`
- `scripts/write_source_provenance_decision_packet.py`
- `tests/test_realworld_source_provenance_decision_packet.py`
- `docs/source_provenance_decision_packet.md`
- `data/manifests/source_provenance_decision_manifest.json`

Edited or regenerated:

- `src/realworld/source_provenance_decision_packet.py`
- `data/manifests/source_provenance_decision_packet.csv`
- `data/manifests/source_provenance_decision_manifest.json`
- `docs/source_provenance_decision_packet.md`
- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `docs/claim_language_guard.md`

## Changes

The sprint replaced release-blocking wording in source-owned packet prose:

- `final source-provenance decisions` -> `source-provenance review decisions`
- `before provenance acceptance` -> `before the provenance review record is created`
- `Accept source license...` -> `Confirm source license...`
- `record accepted license scope` -> `record reviewed license scope`
- `exclude the source from final claims` -> `exclude the source from release-scope claims`
- `before final provenance claims` -> `before release-scope provenance claims`
- `Accept cached public snapshots...` -> `Retain cached public snapshots...`
- `before retaining them for final claims` -> `before retaining them for release-scope claims`
- `Record accepted sources...` -> `Record reviewed sources...`
- `record final provenance only...` -> `record reviewed provenance only...`

The packet still states that it is review support only and cannot create
`data/manifests/provenance_acceptance.json`.

## Command Evidence

| Command | Result | Claim Impact |
| --- | --- | --- |
| `.\.venv\Scripts\python scripts\write_source_provenance_decision_packet.py` | Exit 0; rewrote CSV, manifest, and Markdown; manifest remains `publication_ready=false`, `can_mark_complete=false`, `blocking_decision_count=3`, `human_review_decision_count=4`. | Regenerated only review packet artifacts; no provenance gate closure. |
| `.\.venv\Scripts\python -m py_compile src\realworld\source_provenance_decision_packet.py scripts\write_source_provenance_decision_packet.py` | Exit 0. | Syntax check for touched source and writer. |
| `.\.venv\Scripts\python tests\test_realworld_source_provenance_decision_packet.py` | Exit 0; all three source-provenance decision tests passed. | Confirms row IDs, blocker exposure, and shipped output shape remain intact. |
| `.\.venv\Scripts\python scripts\audit_claim_language.py --scan-path docs\source_provenance_decision_packet.md ... --fail-on-blockers` | Exit 0; focused doc guard reported `blocking_finding_count=0`. | Confirms generated Markdown no longer has release-blocking unbounded terms. |
| `.\.venv\Scripts\python scripts\audit_claim_language.py --scan-path data\manifests\source_provenance_decision_manifest.json ... --fail-on-blockers` | Exit 0; focused manifest guard reported `blocking_finding_count=0`. | Confirms generated manifest no longer has release-blocking unbounded terms. |
| `git diff --check -- src\realworld\source_provenance_decision_packet.py scripts\write_source_provenance_decision_packet.py tests\test_realworld_source_provenance_decision_packet.py docs\source_provenance_decision_packet.md data\manifests\source_provenance_decision_packet.csv data\manifests\source_provenance_decision_manifest.json` | Exit 0; warning only for LF/CRLF normalization in the touched Python source. | Whitespace check passed for this sprint scope. |
| `.\.venv\Scripts\python scripts\audit_claim_language.py` | Exit 0; global blocker count decreased from 15 to 12. | Release remains blocked; this sprint removed only the source-provenance-decision blockers. |
| `.\.venv\Scripts\python tests\test_realworld_claim_language_guard.py` | Exit 0; claim-language guard tests passed. | Confirms guard semantics still fail closed. |

Temporary focused-guard artifacts were removed after successful focused scans.

## Remaining Blockers

`data/validation/claim_language_guard_manifest.json` now reports
`blocking_finding_count=12`, `claim_language_guard_ready=false`,
`publication_ready=false`, and `final_study_ready=false`.

Next release-blocking claim-language rows are:

- `docs/source_url_review_packet.md:38`
- `docs/transfer_evidence_review_packet.md:18`
- `docs/transfer_evidence_review_packet.md:19`
- `data/manifests/formal_evidence_path_audit.json:104`
- `data/manifests/pilot_region_decision_manifest.json:47`
- `data/manifests/source_provenance_manifest.json:73`
- `data/manifests/source_provenance_priority_manifest.json:37`
- `data/manifests/source_provenance_priority_manifest.json:40`
- `data/manifests/phase_gates/phase5_demand_fleet_behavior_profiles.json:20`
- `data/manifests/phase_gates/phase8_compact_experiment_gate.json:20`
- `data/manifests/phase_gates/phase9_full_experiment_gate.json:20`

The phase remains non-operational, non-final, and blocked from study-closeout
claims until the remaining evidence and formal review gates are genuinely
closed.
