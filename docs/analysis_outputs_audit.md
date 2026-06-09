# Analysis Outputs Audit

- Audit passed: `true`
- Blocking findings: `0`
- Scope: Scoped analysis-output audit only; not publication evidence, not final-study evidence, not formal acceptance evidence, and not operational evidence.

| check | group | status | expected | actual |
| --- | --- | --- | --- | --- |
| statistics_manifest_exists | statistics | pass | file exists | loaded |
| statistics_metric_rows | statistics | pass | 819 | 819 |
| statistics_paired_rows | statistics | pass | 702 | 702 |
| statistics_source_manifest_hash | statistics | pass | 07cd065794a546f33df7ffa0493a993715131efed7148d0d19a1a1c3a098e288 | 07cd065794a546f33df7ffa0493a993715131efed7148d0d19a1a1c3a098e288 |
| sensitivity_manifest_exists | sensitivity | pass | file exists | loaded |
| sensitivity_result_rows | sensitivity | pass | 1584 | 1584 |
| sensitivity_summary_rows | sensitivity | pass | 98 | 98 |
| ml_outputs_manifest_exists | ml_outputs | pass | file exists | loaded |
| ml_label_rows | ml_labels | pass | 315 | 315 |
| ml_prediction_rows | ml_outputs | pass | 315 | 315 |
| ml_importance_rows | ml_outputs | pass | 23 | 23 |
| ml_source_results_hash | ml_outputs | pass | 6f311a3d659fa9d7b2b6494fa7bfebd5235d3301f65c41b54b537a99707228a7 | 6f311a3d659fa9d7b2b6494fa7bfebd5235d3301f65c41b54b537a99707228a7 |
| ml_source_manifest_hash | ml_outputs | pass | 07cd065794a546f33df7ffa0493a993715131efed7148d0d19a1a1c3a098e288 | 07cd065794a546f33df7ffa0493a993715131efed7148d0d19a1a1c3a098e288 |
| ml_publication_ready | ml_outputs | pass | False | False |
| ml_final_study_ready | ml_outputs | pass | False | False |
| ml_formal_acceptance_evidence | ml_outputs | pass | False | False |
