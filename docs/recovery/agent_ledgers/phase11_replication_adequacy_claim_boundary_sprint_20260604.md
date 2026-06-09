# Phase 11 Replication Adequacy Claim-Boundary Sprint - 2026-06-04

## Objective

Remove release-blocking approval-style language from the generated
replication-adequacy audit while preserving the scaffold and non-acceptance
boundary required by `plan.md`.

## Scope

Inspected:

- `data/validation/claim_language_guard.csv`
- `docs/replication_adequacy_audit.md`
- `src/realworld/replication_adequacy_audit.py`
- `scripts/audit_replication_adequacy.py`
- `tests/test_realworld_replication_adequacy_audit.py`
- `data/manifests/replication_adequacy_audit_manifest.json`

Edited:

- `src/realworld/replication_adequacy_audit.py`

Regenerated:

- `data/manifests/replication_adequacy_audit.csv`
- `data/manifests/replication_adequacy_audit_manifest.json`
- `docs/replication_adequacy_audit.md`
- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `docs/claim_language_guard.md`

## Change

Approval-like wording was downgraded:

- `formal experiment acceptance record` -> `formal experiment review record`
- `before accepting paired policy statistics` -> `before relying on paired policy statistics`
- `final claims` -> `release-scope claims`
- `experiment acceptance gates` -> `experiment review gates`

## Verification

| command | result | claim impact |
| --- | --- | --- |
| `.\.venv\Scripts\python scripts\audit_replication_adequacy.py` | passed, wrote 11-row audit with `acceptance_ready=false`, `publication_ready=false`, `can_mark_complete=false` | Regenerates replication review artifacts only; does not approve replication adequacy. |
| `.\.venv\Scripts\python -m py_compile src\realworld\replication_adequacy_audit.py scripts\audit_replication_adequacy.py` | passed | Confirms edited module and owner script parse. |
| `.\.venv\Scripts\python tests\test_realworld_replication_adequacy_audit.py` | passed | Confirms audit rows and output writer behavior. |
| focused `scripts\audit_claim_language.py --scan-path docs\replication_adequacy_audit.md --fail-on-blockers` | passed with `blocking_finding_count=0` | Confirms Markdown output no longer has release-blocking unbounded wording. |
| `.\.venv\Scripts\python scripts\audit_claim_language.py` | passed generation; manifest reports `blocking_finding_count=23`, `release_blocked=true` | Reduces global claim-language blockers from 26 at sprint start to 23 after resolving Markdown and manifest wording. |
| `.\.venv\Scripts\python tests\test_realworld_claim_language_guard.py` | passed | Confirms guard behavior after regeneration. |
| `git diff --check -- ...` | passed with CRLF warning only for the edited Python file | Confirms touched files have no whitespace errors. |

Temporary focused guard outputs were removed after the focused check.

## Remaining Blockers

- Claim-language guard still reports 23 release-blocking findings.
- Publication and final-study readiness remain false.
- Replication audit still requires human review for replication-count adequacy,
  CI method suitability, and comparison handling.

## Boundary

This sprint reduces approval-style wording only. It does not establish that 30
seeds are statistically adequate, does not approve paired policy statistics,
does not close experiment review gates, and does not support operational or
release-scope performance claims.
