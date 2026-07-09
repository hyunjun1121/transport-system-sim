# Data Provenance Review Packet

Sub-agent records are review aids. They do not replace formal acceptance artifacts, source-backed reviewer decisions, calibrated validation, or operational routing approval.

- Gate ID: `data_provenance`
- Agent: `OSM / Source / License / Provenance Review Agent`
- Status: `accepted`
- Can mark complete: `true`
- Generated at: `2026-07-05T07:30:47+00:00`

## Decision

OSM / Source / License / Provenance Review Agent can mark gate data_provenance complete because the final-study readiness audit already reports this gate as ready.

## Reviewed Inputs

- data/manifests/source_provenance_manifest.json
- data/manifests/source_license_review_manifest.json
- data/manifests/source_url_review_manifest.json
- data/manifests/source_url_remediation_manifest.json
- data/manifests/source_provenance_priority_manifest.json
- data/manifests/source_context_cache_request_manifest.json
- data/manifests/source_context_cache_decision_manifest.json
- data/manifests/source_provenance_decision_manifest.json
- docs/source_provenance_decision_packet.md
- data/manifests/reproducibility_manifest.json
- data/manifests/current_goal_completion_audit.json
- docs/reproducibility_package.md
- cloned_repo_manifest.md
- data/manifests/provenance_acceptance.json
- data/manifests/source_license_review_packet.csv
- data/manifests/source_url_review_packet.csv
- data/manifests/source_url_remediation_packet.csv
- data/manifests/source_provenance_priority_packet.csv
- data/manifests/source_context_cache_request_packet.csv
- data/manifests/source_context_cache_decision_packet.csv
- data/manifests/source_provenance_decision_packet.csv
- docs/source_license_review_packet.md
- docs/source_url_review_packet.md
- docs/source_url_remediation_packet.md
- docs/source_provenance_priority_packet.md
- docs/source_context_cache_request_packet.md
- docs/source_context_cache_decision_packet.md
- docs/pilot_region_data_card.md
- scripts/audit_source_provenance.py
- scripts/write_source_license_review_packet.py
- scripts/write_source_url_review_packet.py
- scripts/write_source_url_remediation_packet.py
- scripts/write_source_provenance_priority_packet.py
- scripts/write_source_context_cache_request_packet.py
- scripts/write_source_context_cache_decision_packet.py
- scripts/write_source_provenance_decision_packet.py

## Evidence And Source Paths

- data/manifests/provenance_acceptance.json
- data/manifests/source_provenance_manifest.json
- data/manifests/source_license_review_packet.csv
- data/manifests/source_license_review_manifest.json
- data/manifests/source_url_review_packet.csv
- data/manifests/source_url_review_manifest.json
- data/manifests/source_url_remediation_packet.csv
- data/manifests/source_url_remediation_manifest.json
- data/manifests/source_provenance_priority_packet.csv
- data/manifests/source_provenance_priority_manifest.json
- data/manifests/source_context_cache_request_packet.csv
- data/manifests/source_context_cache_request_manifest.json
- data/manifests/source_context_cache_decision_packet.csv
- data/manifests/source_context_cache_decision_manifest.json
- data/manifests/source_provenance_decision_packet.csv
- data/manifests/source_provenance_decision_manifest.json
- data/manifests/reproducibility_manifest.json
- docs/source_license_review_packet.md
- docs/source_url_review_packet.md
- docs/source_url_remediation_packet.md
- docs/source_provenance_priority_packet.md
- docs/source_context_cache_request_packet.md
- docs/source_context_cache_decision_packet.md
- docs/source_provenance_decision_packet.md
- docs/reproducibility_package.md
- docs/pilot_region_data_card.md
- scripts/audit_source_provenance.py
- scripts/write_source_license_review_packet.py
- scripts/write_source_url_review_packet.py
- scripts/write_source_url_remediation_packet.py
- scripts/write_source_provenance_priority_packet.py
- scripts/write_source_context_cache_request_packet.py
- scripts/write_source_context_cache_decision_packet.py
- scripts/write_source_provenance_decision_packet.py
- docs/review_packets/data_provenance.md
- data/cache/pilot_region_road_manifest.json
- cloned_repo_manifest.md

## Risks

- License or attribution requirements may be incomplete.
- Scaffold reproducibility scope cannot support final calibrated claims.

## Required Actions

- No further action for this gate scope.

## Formal Acceptance Boundary

To close this final-study gate, create or update the formal acceptance artifact listed in the agent definition. Do not edit this review packet as a substitute for formal acceptance.

Formal acceptance artifacts:

- data/manifests/provenance_acceptance.json

## Current Final-Study Gate Details

```json
{
  "artifact_present": true,
  "blockers": [
    "source provenance priority: formal provenance acceptance record is absent",
    "source provenance priority: context-source target artifacts still need reviewed payloads, sensitivity/context-only retention decisions, or exclusion decisions",
    "source provenance priority: cached public snapshots still require license, attribution, snapshot, and reproducibility review",
    "source provenance priority: repository inputs still require human scope/privacy/reproducibility review",
    "source provenance priority: URL remediation rows still require reviewer confirmation",
    "source context cache request: context-source target cache artifacts still lack reviewed source payloads, sensitivity/context-only retention decisions, or explicit exclusion decisions",
    "source context cache request: license, attribution, snapshot, and reproducibility review are still required for retained public sources",
    "source context cache request: formal provenance acceptance record is absent",
    "source context cache decision: formal provenance acceptance record is absent",
    "source context cache decision: target cache/retention/exclusion decisions are pending for context-source rows",
    "source context cache decision: retained context sources still require license, attribution, snapshot, and reproducibility review",
    "source context cache decision: ktdb_public_transport_gtfs_context: no reviewed cache artifact, sensitivity/context-only retention decision, or explicit exclusion decision is present",
    "source context cache decision: seoul_shortest_path_api_context: no reviewed cache artifact, sensitivity/context-only retention decision, or explicit exclusion decision is present",
    "source context cache decision: seoul_timetable_api_context: no reviewed cache artifact, sensitivity/context-only retention decision, or explicit exclusion decision is present"
  ],
  "details": {
    "acceptance_path": "data/manifests/provenance_acceptance.json",
    "acceptance_record_present": true,
    "remaining_upgrade_count": 0,
    "scope": "Reviewer-accepted real-world pilot reproduction package within formal-acceptance claim boundary",
    "source_context_cache_decision_artifacts_present": true,
    "source_context_cache_decision_blocking_decision_count": 3,
    "source_context_cache_decision_can_mark_complete": false,
    "source_context_cache_decision_human_review_decision_count": 0,
    "source_context_cache_decision_publication_ready": false,
    "source_context_cache_decision_recorded": false,
    "source_context_cache_decision_row_count": 3,
    "source_context_cache_decision_status_counts": {
      "blocked_missing_context_source_cache_retention_or_exclusion_decision": 3
    },
    "source_context_cache_request_artifacts_present": true,
    "source_context_cache_request_blocking_request_count": 3,
    "source_context_cache_request_can_mark_complete": false,
    "source_context_cache_request_missing_target_cache_artifact_count": 3,
    "source_context_cache_request_publication_ready": false,
    "source_context_cache_request_row_count": 3,
    "source_context_cache_request_status_counts": {
      "blocked_missing_context_source_cache": 3
    },
    "source_license_review_manifest_present": true,
    "source_license_review_packet_present": true,
    "source_provenance_decision_artifacts_present": true,
    "source_provenance_decision_blocking_decision_count": 1,
    "source_provenance_decision_can_mark_complete": false,
    "source_provenance_decision_context_cache_retention_or_exclusion_recorded": false,
    "source_provenance_decision_human_review_decision_count": 6,
    "source_provenance_decision_manifest_present": true,
    "source_provenance_decision_publication_ready": false,
    "source_provenance_decision_recorded": false,
    "source_provenance_decision_remaining_blockers": [
      "context-source target cache artifacts still lack reviewed source payloads, sensitivity/context-only retention decisions, or explicit exclusion decisions"
    ],
    "source_provenance_decision_row_count": 7,
    "source_provenance_decision_status_counts": {
      "blocked_missing_context_cache_retention_or_exclusion_decisions": 1,
      "needs_human_review_cached_snapshot_and_repository_scope": 1,
      "needs_human_review_existing_provenance_acceptance": 1,
      "needs_human_review_license_attribution": 1,
      "needs_human_review_reproducibility_source_scope": 1,
      "needs_human_review_source_inventory": 1,
      "needs_human_review_url_remediation": 1
    },
    "source_provenance_manifest_present": true,
    "source_provenance_path": "data/manifests/source_provenance_manifest.json",
    "source_provenance_priority_artifacts_present": true,
    "source_provenance_priority_blocking_source_count": 2,
    "source_provenance_priority_cached_snapshot_source_count": 5,
    "source_provenance_priority_can_mark_complete": false,
    "source_provenance_priority_context_only_source_count": 2,
    "source_provenance_priority_human_review_source_count": 9,
    "source_provenance_priority_publication_ready": false,
    "source_provenance_priority_repository_input_source_count": 4,
    "source_provenance_priority_row_count": 11,
    "source_provenance_priority_status_counts": {
      "blocked_context_only_source_not_cached": 2,
      "needs_human_review_cached_snapshot_source": 5,
      "needs_human_review_repository_input_source": 4
    },
    "source_provenance_record_count": 11,
    "source_provenance_review_status_counts": {
      "cached_snapshot_pending_review": 5,
      "context_only_not_cached": 2,
      "repository_input_pending_review": 4
    },
    "source_url_can_mark_complete": false,
    "source_url_live_check_performed": true,
    "source_url_publication_ready": false,
    "source_url_remediation_blocking_issue_count": 0,
    "source_url_remediation_can_mark_complete": false,
    "source_url_remediation_live_check_required_count": 0,
    "source_url_remediation_manifest_present": true,
    "source_url_remediation_publication_ready": false,
    "source_url_remediation_row_count": 17,
    "source_url_remediation_status_counts": {
      "alternate_reachable_url_needs_review": 1,
      "local_citation_needs_review": 4,
      "reachable_needs_license_review": 12
    },
    "source_url_review_manifest_present": true,
    "source_url_review_packet_present": true,
    "source_url_status_counts": {
      "network_error": 1,
      "no_url_detected": 4,
      "reachable": 12
    },
    "source_url_unreachable_or_error_count": 1
  },
  "evidence": [
    "data/manifests/provenance_acceptance.json",
    "data/manifests/source_provenance_manifest.json",
    "data/manifests/source_license_review_packet.csv",
    "data/manifests/source_license_review_manifest.json",
    "data/manifests/source_url_review_packet.csv",
    "data/manifests/source_url_review_manifest.json",
    "data/manifests/source_url_remediation_packet.csv",
    "data/manifests/source_url_remediation_manifest.json",
    "data/manifests/source_provenance_priority_packet.csv",
    "data/manifests/source_provenance_priority_manifest.json",
    "data/manifests/source_context_cache_request_packet.csv",
    "data/manifests/source_context_cache_request_manifest.json",
    "data/manifests/source_context_cache_decision_packet.csv",
    "data/manifests/source_context_cache_decision_manifest.json",
    "data/manifests/source_provenance_decision_packet.csv",
    "data/manifests/source_provenance_decision_manifest.json",
    "data/manifests/reproducibility_manifest.json",
    "docs/source_license_review_packet.md",
    "docs/source_url_review_packet.md",
    "docs/source_url_remediation_packet.md",
    "docs/source_provenance_priority_packet.md",
    "docs/source_context_cache_request_packet.md",
    "docs/source_context_cache_decision_packet.md",
    "docs/source_provenance_decision_packet.md",
    "docs/reproducibility_package.md",
    "docs/pilot_region_data_card.md",
    "scripts/audit_source_provenance.py",
    "scripts/write_source_license_review_packet.py",
    "scripts/write_source_url_review_packet.py",
    "scripts/write_source_url_remediation_packet.py",
    "scripts/write_source_provenance_priority_packet.py",
    "scripts/write_source_context_cache_request_packet.py",
    "scripts/write_source_context_cache_decision_packet.py",
    "scripts/write_source_provenance_decision_packet.py"
  ],
  "gate_id": "data_provenance",
  "label": "Data Provenance",
  "ready": true
}
```
