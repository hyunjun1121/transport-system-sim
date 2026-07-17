# Provenance Acceptance Schema

> Current project status (2026-05-08): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


## Purpose

`data/manifests/provenance_acceptance.json` is the explicit review record that
can close the final-study data-provenance gate.

The reproducibility manifest lists current inputs, commands, and outputs. It
does not by itself prove that source snapshots, licenses, privacy abstraction,
cache manifests, or publication claim boundaries have been reviewed.

Do not create this file to make audits pass. Create it only after a real review
accepts the source/license/snapshot package for a quasi-real decision-support
study.

## Location

```text
data/manifests/provenance_acceptance.json
```

The current scaffold intentionally does not include this file.

## Required Fields

| Field | Type | Requirement |
| --- | --- | --- |
| `region_id` | string | Non-empty pilot region identifier. |
| `accepted` | boolean | Must be `true` only after review. |
| `accepted_by` | string | Reviewer, group, or decision record identifier. |
| `accepted_date` | string | Review date in `YYYY-MM-DD` form where possible. |
| `source_snapshot_reviewed` | boolean | Must be `true` after source snapshot review. |
| `license_attribution_reviewed` | boolean | Must be `true` after source license and attribution review. |
| `privacy_abstraction_reviewed` | boolean | Must be `true` after non-sensitive zone and coordinate handling review. |
| `cache_manifest_reviewed` | boolean | Must be `true` after cache manifest and snapshot metadata review. |
| `reproducibility_manifest_reviewed` | boolean | Must be `true` after reproduction commands and artifact paths are reviewed. |
| `source_urls_or_citations` | array of strings | Non-empty source URL, license, or citation list. |
| `data_snapshot_paths` | array of strings | Non-empty list of reviewed data snapshot files. |
| `evidence_paths` | array of strings | Non-empty list of review notes, data cards, manifests, or provenance docs. |
| `claim_boundary` | string | Must include `not operational`. |

## Example Shape

```json
{
  "region_id": "songpa_public_demo",
  "accepted": true,
  "accepted_by": "review record id",
  "accepted_date": "2026-05-04",
  "source_snapshot_reviewed": true,
  "license_attribution_reviewed": true,
  "privacy_abstraction_reviewed": true,
  "cache_manifest_reviewed": true,
  "reproducibility_manifest_reviewed": true,
  "source_urls_or_citations": [
    "https://www.openstreetmap.org/copyright"
  ],
  "data_snapshot_paths": [
    "data/cache/pilot_region_road.graphml",
    "data/cache/pilot_region_road_manifest.json"
  ],
  "evidence_paths": [
    "docs/pilot_region_data_card.md",
    "docs/reproducibility_package.md",
    "data/manifests/reproducibility_manifest.json"
  ],
  "claim_boundary": "Accepted for quasi-real decision-support analysis; not operational routing."
}
```

This example is a schema illustration only. It is not evidence that the current
pilot data provenance has been reviewed or accepted.

## Validation

The schema is enforced by:

```powershell
.\.venv\Scripts\python tests\test_realworld_provenance_acceptance.py
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
```

The final-study readiness audit also requires the reproducibility manifest to
move out of scaffold-only scope. A provenance acceptance record alone cannot
close the data-provenance gate if the package still declares unresolved
remaining upgrades.
