# Benchmark Strategy Decision Packet

Validation benchmark decision packet only; not validation acceptance, not route-engine ground truth, not calibrated traffic validation, and not operational routing evidence. It cannot create data/manifests/validation_acceptance.json.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Alternative benchmark decision recorded: `false`
- Decision rows: 6
- Blocking decisions: 3
- Human-review decisions: 3
- Status counts: `{'blocked_missing_validation_acceptance_record': 1, 'blocked_scaffold_validation_scope': 1, 'blocked_weak_route_road_evidence_dependency': 1, 'needs_human_review_alternative_benchmark_scope': 1, 'needs_human_review_cached_osrm_scope_policy': 1, 'needs_human_review_fallback_warn_or_fail_policy': 1}`

## Decision Rows

| Decision | Status | Candidate | Required Action |
| --- | --- | --- | --- |
| fallback_benchmark_scope_option | needs_human_review_fallback_warn_or_fail_policy | Retain documented fallback detour-speed checks only as placeholder plausibility evidence | Decide whether fallback warning rows are retained, replaced, or excluded before the formal benchmark-review record is written. |
| cached_osrm_snapshot_scope_option | needs_human_review_cached_osrm_scope_policy | Use cached OSRM route rows as optional plausibility evidence after source, license, and snapshot review | Review cached OSRM rows, retained raw responses, terms, attribution, and access-date treatment before publication use. |
| alternative_benchmark_engine_option | needs_human_review_alternative_benchmark_scope | Collect or require Valhalla, routingpy, R5/OpenTripPlanner, UXsim, agency, or literature benchmark evidence | Decide whether alternative route-engine or agency evidence is needed within the publication schedule. |
| validation_summary_scope_boundary | blocked_scaffold_validation_scope | Keep validation summary scoped as scaffold or sanity evidence until formal acceptance revises the claim boundary | Revise or accept validation summary scope only after benchmark strategy and evidence dependencies are reviewed. |
| road_evidence_dependency | blocked_weak_route_road_evidence_dependency | Treat route benchmark interpretation as blocked by weak route-level road evidence exposure | Close road evidence dependencies or keep validation benchmark claims bounded as plausibility checks. |
| formal_validation_acceptance_boundary | blocked_missing_validation_acceptance_record | Record release-scope benchmark strategy only in the formal benchmark-review artifact | Create or validate validation_acceptance.json only after source-backed human review; do not copy this packet into the formal path. |

## Boundary

- This packet is a reviewer worksheet, not an acceptance record.
- It does not make OSRM, fallback rows, or any alternative benchmark ground truth.
- Keep validation claims blocked until `data/manifests/validation_acceptance.json` is reviewed.
