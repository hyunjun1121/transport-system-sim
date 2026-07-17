# Pilot Region Decision Packet

Pilot-region decision packet only; not pilot acceptance, not privacy approval, not graph-scale acceptance, not calibrated real-world validation, and not operational routing evidence. It cannot create data/manifests/pilot_acceptance.json.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Pilot region decision recorded: `false`
- Privacy completion decision recorded: `false`
- Decision rows: 6
- Blocking decisions: 3
- Human-review decisions: 3
- Status counts: `{'blocked_missing_graph_scale_acceptance_record': 1, 'blocked_missing_pilot_acceptance_record': 1, 'blocked_missing_provenance_acceptance_record': 1, 'needs_human_review_claim_boundary': 1, 'needs_human_review_pilot_case_scope': 1, 'needs_human_review_privacy_completion': 1}`

## Decision Rows

| Decision | Status | Candidate | Required Action |
| --- | --- | --- | --- |
| pilot_case_scope_decision | needs_human_review_pilot_case_scope | Retain the current Songpa public demonstration region only as a non-sensitive quasi-real pilot case | Decide whether the current public/synthetic case scope is acceptable for the intended manuscript and review boundary. |
| privacy_review_completion_decision | needs_human_review_privacy_completion | Mark privacy review complete only after all row-level privacy items are reviewed by a human reviewer | Review each privacy packet row and record the final privacy decision in pilot_acceptance.json, not in this worksheet. |
| graph_scale_dependency_decision | blocked_missing_graph_scale_acceptance_record | Bind the pilot case to the graph-scale method selected by formal graph-scale review | Record the graph_scale_decision in pilot_acceptance.json only after graph-scale review selects an accepted method. |
| cache_and_provenance_scope_decision | blocked_missing_provenance_acceptance_record | Use the cached OSM-derived pilot input only after source, license, cache, and attribution scope are reviewed | Confirm whether pilot acceptance is limited to case privacy or also requires reviewed source/cache provenance before final claims. |
| not_operational_claim_boundary_decision | needs_human_review_claim_boundary | Keep all pilot-region claims bounded as non-operational and not calibrated until formal acceptance says otherwise | Confirm the accepted claim boundary text and carry it into pilot_acceptance.json. |
| formal_pilot_acceptance_boundary | blocked_missing_pilot_acceptance_record | Record accepted region ID, reviewer, date, privacy completion, graph-scale decision, evidence paths, and claim boundary only in the formal pilot acceptance path | Create or validate pilot_acceptance.json only after source-backed human review; do not copy this packet into the formal path. |

## Boundary

- This packet is a reviewer worksheet, not an acceptance record.
- It does not approve privacy, select graph scale, accept provenance, or accept the pilot case.
- Keep pilot-region claims blocked until `data/manifests/pilot_acceptance.json` is reviewed.
