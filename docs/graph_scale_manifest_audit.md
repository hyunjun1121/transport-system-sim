# Graph-Scale Manifest Audit

This audit checks whether generated scaffold manifests expose source and analysis graph-scale fields. It does not select a graph-scale method, confirm route sufficiency, tune inputs, or close study gates.

## Summary

- Row count: 13
- Audited manifest count: 12
- Missing or incomplete rows: 0
- Reduced analysis graph rows: 13
- Source node counts: `[4608]`
- Analysis node counts: `[118, 164]`
- Coverage status counts: `{'complete_reduced_analysis_graph_recorded': 13}`

## Rows

| Manifest | Component | Family | Source | Analysis | Status | Required action |
| --- | --- | --- | --- | --- | --- | --- |
| results/realworld_pilot/pilot_result_manifest.json | default | pilot_experiment | 4608/9148 | 118/174 | complete_reduced_analysis_graph_recorded | review reduced/candidate graph method before graph-scale decision record |
| results/realworld_pilot/pilot_sample_manifest.json | default | pilot_experiment | 4608/9148 | 118/174 | complete_reduced_analysis_graph_recorded | review reduced/candidate graph method before graph-scale decision record |
| results/realworld_pilot/pilot_staged_manifest.json | default | pilot_experiment | 4608/9148 | 118/174 | complete_reduced_analysis_graph_recorded | review reduced/candidate graph method before graph-scale decision record |
| results/realworld_pilot/pilot_full_manifest.json | default | pilot_experiment | 4608/9148 | 118/174 | complete_reduced_analysis_graph_recorded | review reduced/candidate graph method before graph-scale decision record |
| results/realworld_pilot/pilot_multi_corridor_manifest.json | default | pilot_experiment | 4608/9148 | 164/246 | complete_reduced_analysis_graph_recorded | review reduced/candidate graph method before graph-scale decision record |
| results/realworld_pilot/pilot_multi_corridor_full_manifest.json | default | pilot_experiment | 4608/9148 | 164/246 | complete_reduced_analysis_graph_recorded | review reduced/candidate graph method before graph-scale decision record |
| results/realworld_pilot/sensitivity_manifest.json | default | deterministic_sensitivity | 4608/9148 | 118/174 | complete_reduced_analysis_graph_recorded | review reduced/candidate graph method before graph-scale decision record |
| results/realworld_pilot/morris_manifest.json | default | morris_sensitivity | 4608/9148 | 118/174 | complete_reduced_analysis_graph_recorded | review reduced/candidate graph method before graph-scale decision record |
| results/realworld_pilot/tables/pilot_full_statistics_manifest.json | default | pilot_statistics | 4608/9148 | 118/174 | complete_reduced_analysis_graph_recorded | review reduced/candidate graph method before graph-scale decision record |
| results/realworld_pilot/tables/pilot_multi_corridor_statistics_manifest.json | default | pilot_statistics | 4608/9148 | 164/246 | complete_reduced_analysis_graph_recorded | review reduced/candidate graph method before graph-scale decision record |
| results/realworld_pilot/tables/pilot_multi_corridor_full_statistics_manifest.json | default | pilot_statistics | 4608/9148 | 164/246 | complete_reduced_analysis_graph_recorded | review reduced/candidate graph method before graph-scale decision record |
| results/realworld_pilot/tables/figure_table_manifest.json | pilot | figure_table_pilot | 4608/9148 | 118/174 | complete_reduced_analysis_graph_recorded | review reduced/candidate graph method before graph-scale decision record |
| results/realworld_pilot/tables/figure_table_manifest.json | sensitivity | figure_table_sensitivity | 4608/9148 | 118/174 | complete_reduced_analysis_graph_recorded | review reduced/candidate graph method before graph-scale decision record |

## Boundary

- This packet is graph-scale visibility evidence only.
- It does not decide whether the reduced corridor, multi-corridor candidate, or full graph is the selected method.
- It cannot create or replace `data/manifests/graph_scale_acceptance.json`.
