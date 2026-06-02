# Transport Simulation Core Reconstruction Decision - 2026-06-02

## Purpose

This corrected note maps prior `transport_simulation_core/` file paths found in session logs to current root-level equivalents. Search-result snippets have been normalized out before this matrix was generated.

## Summary

- code_or_test_missing_from_root: 6
- document_or_input_missing_from_root: 2
- generated_artifact_missing: 13
- root_equivalent_present_tracked: 149

## Decision

The current root repository already contains most reusable source/test equivalents that were visible through the prior `transport_simulation_core/` path list. The missing `transport_simulation_core/` exact folder path is therefore mainly a layout loss, not proof that all simulation code content is gone.

Do not recreate `transport_simulation_core/` by bulk-copying the whole repository yet. The safer recovery path is to keep the root repository as the authoritative simulation core and only reimplement or regenerate the specific missing files that do not have root equivalents.

Generated outputs under the old `transport_simulation_core/outputs` and `transport_simulation_core/results` paths remain missing. They must be regenerated or treated as unavailable; they must not be reconstructed from filenames alone.

## Missing Non-Equivalent Paths

- `transport_simulation_core\full_scale_run_status.md` -> document_or_input_missing_from_root: recover_from_logs_or_regenerate_from_verified_sources
- `transport_simulation_core\outputs\runs\gate2_20260601_232844\gate2\compact_nonarrival_probe_design.md` -> generated_artifact_missing: regenerate_after_scripts_inputs_and_scope_are_verified
- `transport_simulation_core\outputs\runs\gate2_20260601_232844\gate2\assumption_bounds_input_manifest.json` -> generated_artifact_missing: regenerate_after_scripts_inputs_and_scope_are_verified
- `transport_simulation_core\outputs\runs\gate2_20260601_232844\gate2\compact_nonarrival_probe_design.json` -> generated_artifact_missing: regenerate_after_scripts_inputs_and_scope_are_verified
- `transport_simulation_core\outputs\runs\gate2_20260601_232844\gate2\compact_nonarrival_probe_design.csv` -> generated_artifact_missing: regenerate_after_scripts_inputs_and_scope_are_verified
- `transport_simulation_core\outputs\runs\gate2_20260601_232844\gate2\accessibility_loss_summary.md` -> generated_artifact_missing: regenerate_after_scripts_inputs_and_scope_are_verified
- `transport_simulation_core\outputs\runs\gate2_20260601_232844\gate2\assumption_bounds_register.csv` -> generated_artifact_missing: regenerate_after_scripts_inputs_and_scope_are_verified
- `transport_simulation_core\outputs\runs\gate2_20260601_232844\gate2\demand_behavior_orchestrator_decision.json` -> generated_artifact_missing: regenerate_after_scripts_inputs_and_scope_are_verified
- `transport_simulation_core\data\scenarios\demand_profiles.csv` -> document_or_input_missing_from_root: recover_from_logs_or_regenerate_from_verified_sources
- `transport_simulation_core\tests\test_compact_nonarrival_execution_output_validator.py` -> code_or_test_missing_from_root: recover_from_session_content_if_available_or_reimplement_tests_first
- `transport_simulation_core\tests\test_compact_nonarrival_execution_contract.py` -> code_or_test_missing_from_root: recover_from_session_content_if_available_or_reimplement_tests_first
- `transport_simulation_core\tests\test_compact_nonarrival_probe_mapping.py` -> code_or_test_missing_from_root: recover_from_session_content_if_available_or_reimplement_tests_first
- `transport_simulation_core\scripts\validate_compact_nonarrival_execution_outputs.py` -> code_or_test_missing_from_root: recover_from_session_content_if_available_or_reimplement_tests_first
- `transport_simulation_core\scripts\write_compact_nonarrival_probe_mapping.py` -> code_or_test_missing_from_root: recover_from_session_content_if_available_or_reimplement_tests_first
- `transport_simulation_core\scripts\write_compact_nonarrival_execution_contract.py` -> code_or_test_missing_from_root: recover_from_session_content_if_available_or_reimplement_tests_first
- `transport_simulation_core\outputs\runs\gate2_20260601_232844\gate2\compact_nonarrival_probe_edge_mapping.json` -> generated_artifact_missing: regenerate_after_scripts_inputs_and_scope_are_verified
- `transport_simulation_core\outputs\runs\gate2_20260601_232844\gate2\compact_nonarrival_probe_edge_mapping.csv` -> generated_artifact_missing: regenerate_after_scripts_inputs_and_scope_are_verified
- `transport_simulation_core\outputs\runs\gate2_20260601_232844\handoffs\wave6\adversarial_qa_wave4_wave5_review.json` -> generated_artifact_missing: regenerate_after_scripts_inputs_and_scope_are_verified
- `transport_simulation_core\outputs\runs\gate2_20260601_232844\handoffs\wave5\disruption_compact_stress_review.json` -> generated_artifact_missing: regenerate_after_scripts_inputs_and_scope_are_verified
- `transport_simulation_core\outputs\runs\gate2_20260601_232844\gate2\compact_nonarrival_probe_execution_contract.json` -> generated_artifact_missing: regenerate_after_scripts_inputs_and_scope_are_verified
- `transport_simulation_core\outputs\runs\gate2_20260601_232844\gate2\compact_nonarrival_probe_edge_mapping.md` -> generated_artifact_missing: regenerate_after_scripts_inputs_and_scope_are_verified