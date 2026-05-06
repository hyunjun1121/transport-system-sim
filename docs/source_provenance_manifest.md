# Source Provenance Manifest

> Current project status (2026-05-06): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


`data/manifests/source_provenance_manifest.json` is a review packet for the
current quasi-real pilot package. It is not an acceptance record and does not
close the final data-provenance gate by itself.

## Purpose

The manifest lists source-level provenance for:

- cached OSM/Overpass road input;
- sparse cached OSM `maxspeed` candidate evidence;
- cached OSM `lanes` capacity-candidate evidence;
- public/synthetic pilot region specification;
- repository parameter, scenario, policy, and sensitivity tables;
- the validation review packet used to plan benchmark-strategy review across
  internal plausibility, fallback benchmark, OSRM, accessibility-loss, and
  validation-summary scope evidence;
- the sensitivity review packet used to plan Morris-index, zero-effect,
  reduced-graph, and Morris-vs-Sobol review before final claims;
- the parameter evidence review packet used to prioritize weak assumptions;
- the parameter evidence source-request packet used to plan demand, fleet,
  dispatch, transfer, disruption, and traffic/BPR evidence collection;
- the draft road-class override worksheet used for road evidence review;
- the road evidence source-request packet used to plan speed, capacity,
  background-traffic, disruption, and override-application evidence collection;
- cached station-code binding source;
- rail shortest-path and timetable source contexts that still lack cached
  extracts;
- optional key-required train-schedule and shortest-path cache fetch helpers
  for reviewed live data.go.kr requests;
- optional OSRM route benchmark snapshot;
- optional OSRM route benchmark checksum/query manifest;
- scaffold reproducibility package.
- clean-checkout reproducibility review packet and manifest.

Each record includes a source or citation, license or terms note, snapshot or
access date, local artifact paths, review status, and claim boundary. This lets
reviewers distinguish cached source snapshots from context-only source
references and repository-defined assumptions.

## Review Status Values

| Status | Meaning |
| --- | --- |
| `cached_snapshot_pending_review` | A local source snapshot exists, but source quality, license, and attribution still need review. |
| `context_only_not_cached` | The public source is documented, but no local extract is cached for final claims. |
| `repository_input_pending_review` | The artifact is project-owned input or assumption material that still needs methodological review. |
| `reviewed` | Reserved for a reviewer-updated manifest after review; this still does not replace `provenance_acceptance.json`. |

## Audit Command

```powershell
.\.venv\Scripts\python scripts\audit_source_provenance.py
```

Strict structural check:

```powershell
.\.venv\Scripts\python scripts\audit_source_provenance.py --fail-on-blockers
```

The audit validates schema, source text, local artifact paths, review-status
values, source types, and the not-operational claim boundary. It does not
certify calibrated real-world accuracy or operational readiness.

## Final Gate Relationship

The final data-provenance gate still requires:

- a reviewer-created `data/manifests/provenance_acceptance.json`;
- a reproducibility manifest that no longer declares scaffold-only scope;
- closed source, license, cache, privacy, and reproducibility review items.

Do not create acceptance records merely to pass audits.
