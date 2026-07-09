# OSM Graph Snapshot Review Packet

OSM graph snapshot review packet only; not source-provenance acceptance, not reviewed road calibration, not graph-scale acceptance, not validation acceptance, and not operational routing evidence. It cannot create provenance, road override, validation, or graph-scale acceptance.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Review rows: 6
- Blocking rows: 4
- Human-review rows: 2
- Status counts: `{'blocked_missing_or_incomplete_osm_cache_metadata': 1, 'blocked_osm_snapshot_claim_boundary': 1, 'blocked_osm_source_provenance_pending': 1, 'blocked_road_evidence_priority_dependencies': 1, 'needs_human_review_graph_scale_manifest_scope': 1, 'needs_human_review_road_source_decisions': 1}`

## Review Rows

| Review | Status | Evidence | Required Action |
| --- | --- | --- | --- |
| osm_graph_cache_metadata | blocked_missing_or_incomplete_osm_cache_metadata | cache_manifest_present=true; cache_path=; source=; created_utc=; node_count=; edge_count=; graph_type=; attribution_present=false; live_services_required_for_default_tests=None | Review snapshot date, bbox, source, attribution, Overpass scope, and offline-test boundary before relying on the cached graph. |
| osm_source_provenance_dependency | blocked_osm_source_provenance_pending | source_record_present=true; source_review_status=cached_snapshot_pending_review; source_url_or_citation=https://www.openstreetmap.org/copyright; https://overpass-api.de/; local_artifact_count=6; provenance_acceptance_present=true | Review OSM/Overpass source terms, attribution, snapshot date, local artifacts, and claim boundary before provenance acceptance. |
| road_evidence_priority_dependency | blocked_road_evidence_priority_dependencies | priority_row_count=11; blocking_priority_count=1; exposed_highway_count=7; priority_status_counts={"blocked_exposed_connector_assumption": 1, "needs_review_exposed_medium_priority_road_evidence_gap": 6, "queued_no_current_canonical_route_exposure": 4}; road_class_overrides_present=true | Prioritize exposed road classes and connector assumptions before using the cached graph for route-level final claims. |
| road_source_decision_dependency | needs_human_review_road_source_decisions | decision_row_count=5; blocking_decision_count=0; human_review_decision_count=5; decision_status_counts={"needs_human_review_road_source_decision": 5}; road_source_decision_recorded=false | Choose source-backed, benchmark-only, sensitivity-only, or excluded treatment for road speed, capacity, disruption, and override-application requests. |
| graph_scale_manifest_dependency | needs_human_review_graph_scale_manifest_scope | source_graph_node_counts=[4608, 197823]; source_graph_edge_counts=[9148, 298020]; analysis_graph_node_counts=[118, 164, 2850]; analysis_graph_edge_counts=[174, 246, 3002]; graph_scale_acceptance_present=true | Decide whether reduced analysis graphs are final method or scaffold shortcut before treating OSM snapshot scale as accepted. |
| osm_snapshot_claim_boundary | blocked_osm_snapshot_claim_boundary | boundary_blocked=true; provenance_acceptance_present=true; graph_scale_acceptance_present=true; road_class_overrides_present=true; cached_osm_gate_closure_candidate_count=0; publication_ready=false | Keep the cached GraphML input scoped as quasi-real scaffold evidence until source, road-input, and graph-scale decisions are accepted. |

## Boundary

- This packet is a reviewer worksheet, not an acceptance record.
- It does not refresh or validate live OSM/Overpass data.
- It does not create reviewed road-class overrides or graph-scale acceptance.
- Keep cached OSM claims scaffold-scoped until formal evidence artifacts are reviewed.
