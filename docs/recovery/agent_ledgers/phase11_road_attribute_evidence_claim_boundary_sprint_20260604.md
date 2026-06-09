# Phase 11 Road Attribute Evidence Claim-Boundary Sprint - 2026-06-04

## Objective

Remove release-blocking approval-style language from
`docs/road_attribute_evidence.md` and the associated road-attribute evidence
manifest review text while preserving the non-calibrated road-input boundary.

## Scope

Inspected:

- `data/validation/claim_language_guard.csv`
- `docs/road_attribute_evidence.md`
- `src/realworld/road_attribute_evidence.py`
- `scripts/write_road_attribute_evidence.py`
- `tests/test_realworld_road_attribute_evidence.py`

Edited:

- `docs/road_attribute_evidence.md`
- `src/realworld/road_attribute_evidence.py`

Regenerated:

- `data/parameters/road_attribute_evidence_table.csv`
- `data/parameters/road_attribute_evidence_manifest.json`
- `data/validation/claim_language_guard.csv`
- `data/validation/claim_language_guard_manifest.json`
- `docs/claim_language_guard.md`

## Change

The document boundary was downgraded from `accepted evidence` and `formal
acceptance gates` wording to `evidence records` and `formal review gates`.

Generator review items were also downgraded:

- `final road claims` -> `release-scope road claims`
- removed `accepted` from the road-class override review item

## Verification

| command | result | claim impact |
| --- | --- | --- |
| `.\.venv\Scripts\python scripts\write_road_attribute_evidence.py` | passed, wrote 28,947-row edge table and conservative manifest | Regenerates road-attribute review artifacts only; does not create reviewed road overrides. |
| `.\.venv\Scripts\python -m py_compile src\realworld\road_attribute_evidence.py scripts\write_road_attribute_evidence.py` | passed | Confirms edited module and owner script parse. |
| `.\.venv\Scripts\python tests\test_realworld_road_attribute_evidence.py` | passed | Confirms edge IDs, source-backed marker behavior, capacity-candidate separation, writer outputs, and cached graph behavior. |
| focused `scripts\audit_claim_language.py --scan-path docs\road_attribute_evidence.md --fail-on-blockers` | passed with `blocking_finding_count=0` | Confirms this document no longer has release-blocking unbounded wording. |
| `.\.venv\Scripts\python scripts\audit_claim_language.py` | passed generation; manifest reports `blocking_finding_count=22`, `release_blocked=true` | Reduces global claim-language blockers from 23 to 22. |
| `.\.venv\Scripts\python tests\test_realworld_claim_language_guard.py` | passed | Confirms guard behavior after regeneration. |
| `git diff --check -- ...` | passed | Confirms touched files have no whitespace errors. |

Temporary focused guard outputs were removed after the focused check.

## Remaining Blockers

- Claim-language guard still reports 22 release-blocking findings.
- Road-attribute evidence remains a review aid: all 28,947 rows are still
  `weak_for_final_claim`.
- Publication and final-study readiness remain false.

## Boundary

This sprint changes claim language only. It does not convert OSM-derived or
expert-proxy road attributes into calibrated road inputs, does not create
reviewed road-class overrides, and does not close road evidence, validation,
publication, or formal review gates.
