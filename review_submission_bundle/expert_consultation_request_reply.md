# Expert Consultation Review Reply (Latest Inspected Bundle)

Date: 2026-05-11  
Primary artifact reviewed: `/mnt/data/required_deliverables(3).zip`

## 1. Scope of Evidence Reviewed

I inspected the uploaded ZIP as the primary evidence source and confirmed it is a large
implementation/review bundle with **813 files**. The package includes:

- core implementation modules and configuration (`main.py`, `config.yaml`, `requirements.txt`, `src/`, `scripts/`, `tests/`, `data/`, `docs/`, `paper/`, `results/`, `agents.md`)
- planning/operational text (`plan.md`, `IMPLEMENTATION_PLAN.md`, `status.md`)
- acceptance/review aids, test outputs, manifests, and decision packets
- review-package metadata (`docs/review_package_inventory.md`, `data/manifests/review_package_inventory_manifest.json`)

Companion paths intentionally missing from the extracted ZIP were:

- `review_packages/expert_review_handoff_20260510.md`
- `review_packages/expert_review_handoff_20260510.json`
- `docs/review_package_build.md`
- `docs/review_package_path_audit.md`

Those are expected as ZIP-external handoff sidecars (not model-mechanics blocker evidence), but for strict review intake they are required files and must be supplied together.

As of this inspection, audit files still report `final_study_ready=false` with **3/15** gates ready and **12/15** blocked, while formal acceptance remains **0/12**.

---

## 2. Acceptability Matrix (A-I)

| Item | Status | Verification finding |
| --- | --- | --- |
| A. Package completeness and traceability | PASS | The ZIP is materially complete for a renewed technical review package (implementation, cache, scripts, tests, docs, manifests, results). Inventory reports 813 files, 0 missing required groups, 0 missing non-formal package paths, and 0 missing paths after path-audit. |
| B. Formal acceptance artifact hygiene | PASS | Formal target files are absent/clean rather than filled by placeholders. `formal_target_placeholder_relocation` confirms placeholder files were moved out of final target locations. Path-audit and formal guard indicate no placeholder/template occupies final acceptance paths as accepted evidence. |
| C. Pilot and scope | PASS | The requested project framing is still decision-support-oriented, not operational. Report/paper front matter emphasizes non-operational, non-final status. |
| D. Evidence domains | BLOCKED | Road/rail/parameter/provenance domains remain unaccepted. Road speed/capacity/disruption are still draft/assumption-based where final claims are expected; rail timing/headway evidence lacks reviewed cached timing artifacts; weak parameters remain unaccepted. |
| E. Graph-scale and scenario method | BLOCKED | `analysis_corridor_method` and `graph_scale_method_decision` remain unresolved for final acceptance. A reduced corridor is explicitly marked scaffold/reasoned abstraction, and full-method acceptance is absent. |
| F. Validation, sensitivity, experiment integrity | PARTIAL | Framework now documents plausibility, CRN pairing, replication checks, and CI methods, but acceptance records remain blocked for validated experiment scope, sensitivity method finalization, multiple-comparison handling, and final inferential certainty. |
| G. Reproducibility | BLOCKED | A bounded clean-checkout smoke exists; full reproducibility acceptance is still blocked pending clean-checkout parity of full accepted profile, manifest-complete regeneration, and stronger environment pinning/lifecycle controls. |
| H. Manuscript/reporting language | PARTIAL | Caveats are present, and forecast/operational disclaimers are largely aligned; however claim-overreach candidates remain (reported in claim-alignment packet), and 91 overclaim candidates were identified pending rewrite/clearance. |
| I. Final-gate posture | BLOCKED | `final_study_ready=false`; formal acceptance package remains 0/12. Remaining gates (`pilot_region`, `graph_scale`, `provenance`, `parameter`, `rail`, `validation`, `sensitivity`, `experiment`, `manuscript`, `reproducibility`, `final_audit`) are still blockers. |

---

## 3. Non-final / Blocked Component Classification

- **Materially complete (non-blocking):** code, configs, simulations, experiments, scripts, tests, data/cache, manifests, results, docs, reports, plans. This satisfies renewed package-completeness intent.
- **Intake blocker for strict audit traceability:** handoff sidecars above must be supplied even though they are ZIP-external artifacts, because they are required to verify checksum coverage and transfer intent.
- **Critical blocker (formal):** the 12 missing/formally absent target acceptance artifacts:
  - `pilot_acceptance.json`
  - `graph_scale_acceptance.json`
  - `provenance_acceptance.json`
  - `parameter_acceptance.csv`
  - `road_class_overrides.csv`
  - `validation_acceptance.json`
  - `sensitivity_acceptance.json`
  - `experiment_acceptance.json`
  - `manuscript_acceptance.json`
  - `reproducibility_acceptance.json`
  - `docs/final_study_audit.md`
  - `final_audit_acceptance.json`
- **Gate blocker risk:** if sidecars are missing from the delivery bundle, the intake is incomplete even when ZIP-internal mechanics are reproducible.

---

## 4. Evidence-domain Assessment and Minimum Required Additions

| Domain | Current class | Limitation | Minimum required evidence for final claims |
| --- | --- | --- | --- |
| Road speed/capacity/disruption | Draft + sparse evidence | Road overrides remain assumption-driven; capacity/disruption proxies not final | Source-backed speed/capacity/disruption table with derivation, units, citation, checksum, and reviewer decision |
| Transfer parameters | Assumption-only | Station transfer and service access timing treated as scenarios | Reviewed station-layout or literature evidence plus sensitivity boundaries |
| Traffic/BPR | Partially sourced, partially assumption | Literature defaults can remain if declared; traffic loading/disruption context still not fully calibrated | Explicit parameter provenance, range checks, and accepted calibration boundary |
| Disruption probabilities/modes | Assumption-only | Blocked/reduction behavior settings not finalized in source-backed form | Hazard or incident-derived support, scenario rationale, or explicit sensitivity-only statement |
| Rail timing/headway/capacity | Assumption-only in final scope | Cached timetable/shortest-path/GTFS timing evidence not generally accepted yet | Reviewed cached evidence packet per route/service class with traceability |
| Source/license/privacy | Review-only / pending | Source/license records and cache provenance remain pending | Final provenance acceptance record with URL/license/cache lifecycle and reviewer sign-off |

---

## 5. Corrective Actions for Blocked Items

1. **Create reviewer-accepted road, rail, and parameter evidence artifacts**
   - Replace draft-only road values with accepted or explicitly bounded sensitivity-only values.
   - Complete parameter provenance file (`parameter_acceptance.csv`) with source/review/range fields.
   - Add or explicitly reject cached rail timing/shortest-path/GTFS pathways with provenance.

2. **Select and publish formal graph-scale decision**
   - Populate `data/manifests/graph_scale_acceptance.json`.
   - Document route-parity and travel-time deltas by scenario and method.
   - Record downstream scope implications for figures, statistics, and conclusions.

3. **Upgrade validity and inference controls**
   - Keep plausibility checks labeled as such unless stronger benchmarks are accepted.
   - Add missing benchmark comparison decisions and decision boundaries.
   - Maintain blocked status on unaccepted pilot and final interpretation claims.

4. **Raise reproducibility from bounded smoke to auditable pipeline**
   - Clean-checkout full reproducibility, regenerate outputs, and verify with manifest hash checks.
   - Add stronger environment pinning or lock metadata for re-run exactness.

5. **Finalize manuscript/report mapping**
   - Tie every key claim to accepted artifacts and evidence status.
   - Remove/qualify unsupported bus+rail comparative language.

6. **Formal package closure sequencing**
   - Keep `final_study_audit.md` at blocked state until all 12 formal gates move from scaffold to reviewer acceptance.
   - Preserve the non-acceptance warning around OSRM/checkpoints/prefix smoke as supporting context, not proof.

---

## 6. Prioritized blocker ranking

### Critical
1. 0/12 formal acceptance and `final_study_ready=false`.
2. Unaccepted evidence foundations (road, rail, parameters, provenance).
3. Graph-scale acceptance not formally selected.

### High
4. Reproducibility acceptance is still scaffold/bounded, not full.
5. Validation/sensitivity/experiment acceptance remains blocked (CRN completeness + inferential controls).
6. Manuscript/report claim alignment still has overclaim candidates.

### Medium
7. Missing handoff sidecars inside ZIP (must be provided as separate sidecars for strict intake).

### Low
8. Agents instruction path naming (AGENTS.md vs `agents.md`) and cosmetic path conventions.

---

## 7. Recommendation

This package is suitable for **next-stage expert technical review only** (non-final),
not for formal acceptance.

Recommendation: **Request another review round** with the same reviewer framing,
retaining `final_study_ready=false`, until the formal acceptance gate set above is
closed with reviewed, source-backed records.


