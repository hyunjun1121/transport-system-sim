# Data Provenance Review Packet

Sub-agent records are review aids. They do not replace formal acceptance artifacts, source-backed reviewer decisions, calibrated validation, or operational routing approval.

- Gate ID: `data_provenance`
- Agent: `OSM / Source / License / Provenance Review Agent`
- Status: `blocked`
- Can mark complete: `false`
- Generated at: `2026-05-04T12:25:58+00:00`

## Decision

OSM / Source / License / Provenance Review Agent cannot accept gate data_provenance; the current final-study readiness audit reports blockers.

## Reviewed Inputs

- data/manifests/source_provenance_manifest.json
- data/manifests/reproducibility_manifest.json
- docs/reproducibility_package.md
- cloned_repo_manifest.md
- data/manifests/provenance_acceptance.json
- data/manifests/source_license_review_packet.csv
- data/manifests/source_license_review_manifest.json
- data/manifests/source_url_review_packet.csv
- data/manifests/source_url_review_manifest.json
- docs/source_license_review_packet.md
- docs/source_url_review_packet.md
- docs/pilot_region_data_card.md
- scripts/audit_source_provenance.py
- scripts/write_source_license_review_packet.py
- scripts/write_source_url_review_packet.py

## Evidence And Source Paths

- data/manifests/provenance_acceptance.json
- data/manifests/source_provenance_manifest.json
- data/manifests/source_license_review_packet.csv
- data/manifests/source_license_review_manifest.json
- data/manifests/source_url_review_packet.csv
- data/manifests/source_url_review_manifest.json
- data/manifests/reproducibility_manifest.json
- docs/source_license_review_packet.md
- docs/source_url_review_packet.md
- docs/reproducibility_package.md
- docs/pilot_region_data_card.md
- scripts/audit_source_provenance.py
- scripts/write_source_license_review_packet.py
- scripts/write_source_url_review_packet.py
- docs/review_packets/data_provenance.md
- data/cache/pilot_region_road_manifest.json
- cloned_repo_manifest.md

## Risks

- License or attribution requirements may be incomplete.
- Scaffold reproducibility scope cannot support final calibrated claims.
- create an explicit provenance acceptance record after source, license, snapshot, privacy, and reproducibility review
- replace scaffold-only reproducibility manifest with accepted source/license/snapshot provenance

## Required Actions

- Review source URLs, licenses, attribution, local snapshots, privacy abstraction, and reproducibility scope.
- Create data/manifests/provenance_acceptance.json only after source-backed review.
- create an explicit provenance acceptance record after source, license, snapshot, privacy, and reproducibility review
- replace scaffold-only reproducibility manifest with accepted source/license/snapshot provenance

## Formal Acceptance Boundary

To close this final-study gate, create or update the formal acceptance artifact listed in the agent definition. Do not edit this review packet as a substitute for formal acceptance.

Formal acceptance artifacts:

- data/manifests/provenance_acceptance.json

## Current Final-Study Gate Details

```json
{
  "artifact_present": true,
  "blockers": [
    "create an explicit provenance acceptance record after source, license, snapshot, privacy, and reproducibility review",
    "replace scaffold-only reproducibility manifest with accepted source/license/snapshot provenance"
  ],
  "details": {
    "acceptance_path": "data/manifests/provenance_acceptance.json",
    "acceptance_record_present": false,
    "remaining_upgrade_count": 25,
    "scope": "scaffold-only real-world pilot package",
    "source_license_review_manifest_present": true,
    "source_license_review_packet_present": true,
    "source_provenance_manifest_present": true,
    "source_provenance_path": "data/manifests/source_provenance_manifest.json",
    "source_provenance_record_count": 10,
    "source_provenance_review_status_counts": {
      "cached_snapshot_pending_review": 3,
      "context_only_not_cached": 3,
      "repository_input_pending_review": 4
    },
    "source_url_review_manifest_present": true,
    "source_url_review_packet_present": true
  },
  "evidence": [
    "data/manifests/provenance_acceptance.json",
    "data/manifests/source_provenance_manifest.json",
    "data/manifests/source_license_review_packet.csv",
    "data/manifests/source_license_review_manifest.json",
    "data/manifests/source_url_review_packet.csv",
    "data/manifests/source_url_review_manifest.json",
    "data/manifests/reproducibility_manifest.json",
    "docs/source_license_review_packet.md",
    "docs/source_url_review_packet.md",
    "docs/reproducibility_package.md",
    "docs/pilot_region_data_card.md",
    "scripts/audit_source_provenance.py",
    "scripts/write_source_license_review_packet.py",
    "scripts/write_source_url_review_packet.py"
  ],
  "gate_id": "data_provenance",
  "label": "Data Provenance",
  "ready": false
}
```
