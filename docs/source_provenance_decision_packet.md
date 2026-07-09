# Source Provenance Decision Packet

Source-provenance decision packet only; not source acceptance, not license certification, not cached source evidence, not provenance gate closure, not calibrated real-world validation, and not operational routing approval. It cannot create data/manifests/provenance_acceptance.json.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Provenance decision recorded: `false`
- Decision rows: 7
- Blocking decisions: 1
- Human-review decisions: 6
- Status counts: `{'blocked_missing_context_cache_retention_or_exclusion_decisions': 1, 'needs_human_review_cached_snapshot_and_repository_scope': 1, 'needs_human_review_existing_provenance_acceptance': 1, 'needs_human_review_license_attribution': 1, 'needs_human_review_reproducibility_source_scope': 1, 'needs_human_review_source_inventory': 1, 'needs_human_review_url_remediation': 1}`

## Decision Rows

| Decision | Status | Candidate | Required Action |
| --- | --- | --- | --- |
| source_inventory_review_decision | needs_human_review_source_inventory | Retain the current 11-row source manifest only after reviewer confirms source identity, scope, and local artifacts | Confirm the retained source inventory and any excluded sources before the provenance review record is created. |
| license_attribution_decision | needs_human_review_license_attribution | Confirm source license, attribution, derivative-use, snapshot, and privacy abstraction treatment only after row-level review | Review every source/license row and record reviewed license scope in provenance_acceptance.json. |
| context_source_cache_retention_or_exclusion_decision | blocked_missing_context_cache_retention_or_exclusion_decisions | Cache retained context-source target artifacts or explicitly retain the source as sensitivity/context-only evidence, or exclude the source from release-scope claims | Resolve cache, sensitivity/context-only retention, or exclusion treatment for each context source before release-scope provenance claims. |
| url_remediation_decision | needs_human_review_url_remediation | Retain reachable URLs, local citations, and alternate URL replacements only after reviewer confirmation | Confirm URL identity, local-citation rows, and alternate URL candidates before the provenance review record is created. |
| cached_snapshot_repository_scope_decision | needs_human_review_cached_snapshot_and_repository_scope | Retain cached public snapshots and repository-owned inputs only inside a not-operational, non-calibrated claim boundary | Review cached snapshots, repository-owned inputs, and privacy abstraction before retaining them for release-scope claims. |
| reproducibility_source_scope_decision | needs_human_review_reproducibility_source_scope | Replace the scaffold-only reproduction scope with reviewed source snapshot and cache reproduction evidence | Confirm retained source snapshots and cache reproduction evidence before the provenance review record is created. |
| formal_provenance_acceptance_boundary | needs_human_review_existing_provenance_acceptance | Record reviewed sources, reviewer, date, license scope, cache/retention/exclusion decisions, evidence paths, and claim boundary only in the formal provenance acceptance path | Create or validate provenance_acceptance.json only after source-backed human review; do not copy this packet into the formal path. |

## Boundary

- This packet is a reviewer worksheet, not a provenance acceptance record.
- It does not certify licenses, accept source snapshots, cache context-source target artifacts, or close the provenance gate.
- Keep provenance claims blocked until `data/manifests/provenance_acceptance.json` is reviewed.
