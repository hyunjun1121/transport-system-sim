# Source Provenance Decision Packet

Source-provenance decision packet only; not source acceptance, not license certification, not cached source evidence, not provenance gate closure, not calibrated real-world validation, and not operational routing approval. It cannot create data/manifests/provenance_acceptance.json.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Provenance decision recorded: `false`
- Decision rows: 7
- Blocking decisions: 3
- Human-review decisions: 4
- Status counts: `{'blocked_missing_context_cache_or_exclusion_decisions': 1, 'blocked_missing_provenance_acceptance_record': 1, 'blocked_scaffold_reproducibility_manifest_scope': 1, 'needs_human_review_cached_snapshot_and_repository_scope': 1, 'needs_human_review_license_attribution': 1, 'needs_human_review_source_inventory': 1, 'needs_human_review_url_remediation': 1}`

## Decision Rows

| Decision | Status | Candidate | Required Action |
| --- | --- | --- | --- |
| source_inventory_review_decision | needs_human_review_source_inventory | Retain the current 11-row source manifest only after reviewer confirms source identity, scope, and local artifacts | Confirm the retained source inventory and any excluded sources before provenance acceptance. |
| license_attribution_decision | needs_human_review_license_attribution | Accept source license, attribution, derivative-use, snapshot, and privacy abstraction treatment only after row-level review | Review every source/license row and record accepted license scope in provenance_acceptance.json. |
| context_source_cache_or_exclusion_decision | blocked_missing_context_cache_or_exclusion_decisions | Cache retained context-only public source extracts or explicitly exclude them from final claims | Resolve cache, exclusion, or sensitivity-only treatment for each context source before final provenance claims. |
| url_remediation_decision | needs_human_review_url_remediation | Retain reachable URLs, local citations, and alternate URL replacements only after reviewer confirmation | Confirm URL identity, local-citation rows, and alternate URL candidates before provenance acceptance. |
| cached_snapshot_repository_scope_decision | needs_human_review_cached_snapshot_and_repository_scope | Accept cached public snapshots and repository-owned inputs only inside a not-operational, non-calibrated claim boundary | Review cached snapshots, repository-owned inputs, and privacy abstraction before retaining them for final claims. |
| reproducibility_source_scope_decision | blocked_scaffold_reproducibility_manifest_scope | Replace the scaffold-only reproduction scope with reviewed source snapshot and cache reproduction evidence | Confirm retained source snapshots and cache reproduction evidence before provenance acceptance. |
| formal_provenance_acceptance_boundary | blocked_missing_provenance_acceptance_record | Record accepted sources, reviewer, date, license scope, cache/exclusion decisions, evidence paths, and claim boundary only in the formal provenance acceptance path | Create or validate provenance_acceptance.json only after source-backed human review; do not copy this packet into the formal path. |

## Boundary

- This packet is a reviewer worksheet, not a provenance acceptance record.
- It does not certify licenses, accept source snapshots, cache context sources, or close the provenance gate.
- Keep provenance claims blocked until `data/manifests/provenance_acceptance.json` is reviewed.
