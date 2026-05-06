# Formal Acceptance Blocker Queue

Formal acceptance blocker queue only. Rows are work items for reviewers; they do not create approvals, source evidence, calibrated validation, or operational routing permission.

## Summary

- Queue rows: 15
- Formal acceptance ready: `false`
- Final-study ready: `false`
- Can mark complete: `false`
- CSV: `data/manifests/formal_acceptance_blocker_queue.csv`

## Queue

| Gate | Action Type | Formal Target | Review Packet | Blocker |
| --- | --- | --- | --- | --- |
| pilot_region_accepted | create_or_supply_formal_evidence | `data/manifests/pilot_acceptance.json` | `docs/review_packets/pilot_region_accepted.md` | create an explicit pilot acceptance record after privacy and case-scope review |
| graph_scale_strategy | create_or_supply_formal_evidence | `data/manifests/graph_scale_acceptance.json` | `docs/review_packets/graph_scale_strategy.md` | create an explicit graph-scale acceptance record after source-vs-analysis graph review |
| data_provenance | create_or_supply_formal_evidence | `data/manifests/provenance_acceptance.json` | `docs/review_packets/data_provenance.md` | create an explicit provenance acceptance record after source, license, snapshot, privacy, and reproducibility review |
| parameter_acceptance | create_or_supply_formal_evidence | `data/parameters/parameter_acceptance.csv` | `docs/review_packets/parameter_evidence.md` | create reviewed parameter acceptance records only for weak assumptions retained in final claims |
| parameter_acceptance | create_or_supply_formal_evidence | `data/parameters/parameter_acceptance.csv` | `docs/review_packets/parameter_evidence.md` | parameter_acceptance.csv is missing |
| road_class_overrides | replace_weak_or_scaffold_evidence | `data/parameters/road_class_overrides.csv` | `docs/review_packets/cached_osm_input.md` | replace the draft road-class override worksheet with a reviewed road_class_overrides.csv table containing source-backed speed, capacity, and base-disruption evidence |
| road_class_overrides | apply_reviewed_input_and_regenerate | `data/parameters/road_class_overrides.csv` | `docs/review_packets/cached_osm_input.md` | apply the reviewed overrides when adapting the pilot graph if final claims require calibrated road inputs |
| road_class_overrides | create_or_supply_formal_evidence | `data/parameters/road_class_overrides.csv` | `docs/review_packets/cached_osm_input.md` | reviewed road-class override table is absent |
| validation_package | create_or_supply_formal_evidence | `data/manifests/validation_acceptance.json` | `docs/review_packets/validation_package.md` | create an explicit validation acceptance record after benchmark-strategy review |
| sensitivity_analysis | create_or_supply_formal_evidence | `data/manifests/sensitivity_acceptance.json` | `docs/review_packets/sensitivity_analysis.md` | create an explicit sensitivity acceptance record after SALib output and Sobol-decision review |
| full_experiment_output | create_or_supply_formal_evidence | `data/manifests/experiment_acceptance.json` | `docs/review_packets/full_experiment_output.md` | create an explicit experiment acceptance record after input validation, graph-scope, and scenario-policy-seed review |
| manuscript_report_alignment | create_or_supply_formal_evidence | `data/manifests/manuscript_acceptance.json` | `docs/review_packets/manuscript_report_alignment.md` | create an explicit manuscript/report acceptance record after evidence gates, figures, paper, report, and claim boundaries are reviewed |
| reproducibility | create_or_supply_formal_evidence | `data/manifests/reproducibility_acceptance.json` | `docs/review_packets/reproducibility.md` | create an explicit reproducibility acceptance record after clean-checkout validation, artifact regeneration, manifest review, and import-boundary checks |
| final_audit_document | create_or_supply_formal_evidence | `docs/final_study_audit.md` | `docs/review_packets/final_audit.md` | create docs/final_study_audit.md after all other gates close |
| final_audit | create_or_supply_formal_evidence | `data/manifests/final_audit_acceptance.json` | `docs/review_packets/final_audit.md` | create an explicit final-audit acceptance record only after prompt-to-artifact review confirms every final gate is closed |

## Use

Work this queue from top to bottom. If evidence is missing, leave the formal target absent. If evidence exists, update the formal target with a real reviewed decision and rerun the formal acceptance audits.
