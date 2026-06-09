# Phase 11 Source URL Review Claim-Boundary Sprint - 2026-06-04

## Objective

Lower unbounded `final claims` wording in the source URL review packet while
preserving the existing live URL-check rows and keeping all provenance gates
blocked.

## Scope

Inspected:

- `data/validation/claim_language_guard.csv`
- `src/realworld/source_url_review_packet.py`
- `scripts/write_source_url_review_packet.py`
- `tests/test_realworld_source_url_review_packet.py`
- `docs/source_url_review_packet.md`
- `data/manifests/source_url_review_manifest.json`

Edited or regenerated:

- `src/realworld/source_url_review_packet.py`
- `data/manifests/source_url_review_packet.csv`
- `data/manifests/source_url_review_manifest.json`
- `docs/source_url_review_packet.md`
- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `docs/claim_language_guard.md`

## Changes

The sprint changed source-owned packet prose from unbounded final-claim wording
to release-scope wording:

- `exclude them from final claims` -> `exclude them from release-scope claims`
- `explicit exclusion from final claims` -> `explicit exclusion from release-scope claims`

The CSV schema field `can_support_final_provenance_gate` was left unchanged as
a stable data-contract field. Its shipped values remain `false`.

## Command Evidence

| Command | Result | Claim Impact |
| --- | --- | --- |
| `.\.venv\Scripts\python scripts\write_source_url_review_packet.py --preserve-existing-live` | Exit 0; regenerated CSV, manifest, and Markdown while preserving `live_http=13`, `not_checked=4`, `reachable=12`, `network_error=1`, and `no_url_detected=4`. | Updates wording only; URL reachability remains review aid, not provenance evidence. |
| `.\.venv\Scripts\python -m py_compile src\realworld\source_url_review_packet.py scripts\write_source_url_review_packet.py` | Exit 0. | Syntax check for touched source and writer. |
| `.\.venv\Scripts\python tests\test_realworld_source_url_review_packet.py` | Exit 0; all source URL review packet tests passed. | Confirms URL parsing, live preservation, fallback checks, and shipped non-acceptance outputs. |
| `.\.venv\Scripts\python scripts\audit_claim_language.py --scan-path docs\source_url_review_packet.md ... --fail-on-blockers` | Exit 0; focused doc guard reported `blocking_finding_count=0`. | Confirms generated Markdown no longer has release-blocking unbounded terms. |
| `.\.venv\Scripts\python scripts\audit_claim_language.py --scan-path data\manifests\source_url_review_manifest.json ... --fail-on-blockers` | Exit 0; focused manifest guard reported `blocking_finding_count=0`. | Confirms generated manifest no longer has release-blocking unbounded terms. |
| `git diff --check -- src\realworld\source_url_review_packet.py scripts\write_source_url_review_packet.py tests\test_realworld_source_url_review_packet.py docs\source_url_review_packet.md data\manifests\source_url_review_packet.csv data\manifests\source_url_review_manifest.json` | Exit 0; warning only for LF/CRLF normalization in the touched Python source. | Whitespace check passed for this sprint scope. |
| `.\.venv\Scripts\python scripts\audit_claim_language.py` | Exit 0; global blocker count decreased from 12 to 11. | Release remains blocked; this sprint removed only the source-url-review blocker. |
| `.\.venv\Scripts\python tests\test_realworld_claim_language_guard.py` | Exit 0; claim-language guard tests passed. | Confirms guard semantics still fail closed. |

Temporary focused-guard artifacts were removed after successful focused scans.

## Remaining Blockers

`data/validation/claim_language_guard_manifest.json` now reports
`blocking_finding_count=11`, `claim_language_guard_ready=false`,
`publication_ready=false`, and `final_study_ready=false`.

Remaining release-blocking claim-language rows are:

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

The project remains non-operational, non-final, and blocked from study-closeout
claims.
