"""Tests for cached pilot scaffold experiment outputs."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.disruption_scenarios import (
    DEFAULT_SCENARIO_PATH,
    DisruptionScenario,
    load_disruption_scenarios,
)
from src.realworld.artifact_invalidation_matrix import write_artifact_invalidation_matrix
from src.realworld.pilot_experiments import (
    CLAIM_SCOPE,
    DEFAULT_CACHE_PATH,
    DEFAULT_DEMAND_PROFILES_PATH,
    DEFAULT_FLEET_PROFILES_PATH,
    DEFAULT_FULL_PROFILE_ID,
    DEFAULT_MULTI_CORRIDOR_FULL_PROFILE_ID,
    DEFAULT_MULTI_CORRIDOR_PROFILE_ID,
    DEFAULT_REGION_PATH,
    DEFAULT_SAMPLE_PROFILE_ID,
    DEFAULT_SAMPLE_POLICY_IDS,
    DEFAULT_SAMPLE_SCENARIO_IDS,
    DEFAULT_SAMPLE_SEEDS,
    DEFAULT_STAGED_PROFILE_ID,
    ENGINEERING_ONLY_CLAIM_SCOPE,
    GRAPH_REDUCTION_MULTI_CORRIDOR,
    GRAPH_REDUCTION_SINGLE_CORRIDOR,
    PILOT_MULTI_CORRIDOR_CANDIDATE_CLAIM_SCOPE,
    PILOT_MULTI_CORRIDOR_FULL_CANDIDATE_CLAIM_SCOPE,
    PilotExperimentPreflightError,
    RESULT_COLUMNS,
    apply_pilot_demand_fleet_profiles,
    graph_with_forced_disruption_probabilities,
    load_pilot_inputs,
    load_pilot_experiment_design,
    make_pilot_base_config,
    run_pilot_experiments,
    select_disruption_cases,
    summarize_pilot_rows,
)
from src.realworld.road_overrides import REQUIRED_COLUMNS


def test_forced_disruption_probabilities_are_deterministic_and_non_mutating() -> None:
    """Selected structured edges should be the only road edges with p_fail=1."""

    _assert_cached_inputs_exist()
    inputs = load_pilot_inputs()
    scenarios = load_disruption_scenarios(region_id=inputs.region_id)
    case = select_disruption_cases(
        inputs.graph,
        scenarios,
        scenario_ids=["songpa_last_mile_station_to_destination"],
    )[0]

    prepared = graph_with_forced_disruption_probabilities(inputs.graph, case)
    selected_edges = {selected.edge for selected in case.selected_edges}

    assert selected_edges
    assert prepared is not inputs.graph
    for edge in selected_edges:
        assert prepared.edges[edge]["p_fail"] == 1.0
        assert prepared.edges[edge]["base_p_fail"] == 1.0
        assert inputs.graph.edges[edge]["p_fail"] != 1.0

    for u, v, data in prepared.edges(data=True):
        if data.get("mode") == "road" and (u, v) not in selected_edges:
            assert data["p_fail"] == 0.0
            assert data["base_p_fail"] == 0.0

    print("PASS: deterministic disruption graph preparation is non-mutating")


def test_disruption_case_preserves_scenario_p_fail_scale() -> None:
    """Scenario p_fail_scale should survive registry conversion into runs."""

    _assert_cached_inputs_exist()
    inputs = load_pilot_inputs()
    scenario = DisruptionScenario(
        scenario_id="scaled_access_test",
        region_id=inputs.region_id,
        family="access_road",
        label="Scaled access road scenario",
        selection_method="shortest_path",
        target_segment="A->S",
        disruption_mode="capacity_reduction",
        capacity_factor=0.5,
        p_fail_scale=0.25,
        max_edges=1,
        evidence_class="scenario_based",
        observed_disaster_data=False,
    )

    case = select_disruption_cases(
        inputs.graph,
        (scenario,),
        scenario_ids=("scaled_access_test",),
    )[0]

    assert case.p_fail_scale == 0.25
    assert case.failure_mode == "capacity_reduction"
    assert case.selected_edges

    print("PASS: scenario p_fail_scale survives disruption-case conversion")


def test_sample_pilot_experiment_writes_csvs_and_manifest() -> None:
    """The sample runner should write separated conservative pilot outputs."""

    _assert_cached_inputs_exist()
    expected_rows = (
        len(DEFAULT_SAMPLE_POLICY_IDS)
        * len(DEFAULT_SAMPLE_SCENARIO_IDS)
        * len(DEFAULT_SAMPLE_SEEDS)
    )
    expected_summary_rows = len(DEFAULT_SAMPLE_POLICY_IDS) * len(DEFAULT_SAMPLE_SCENARIO_IDS)

    with TemporaryDirectory() as directory:
        result = run_pilot_experiments(output_dir=directory, sample=True)

        rows = result["rows"]
        summary_rows = result["summary_rows"]
        assert len(rows) == expected_rows
        assert len(summary_rows) == expected_summary_rows

        with result["results_path"].open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == RESULT_COLUMNS

        with result["summary_path"].open("r", encoding="utf-8", newline="") as handle:
            summary_reader = csv.DictReader(handle)
            written_summary_rows = list(summary_reader)

        with result["manifest_path"].open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)
        legacy_manifest_path = result.get("legacy_manifest_path")

        assert len(written_rows) == expected_rows
        assert len(written_summary_rows) == expected_summary_rows
        assert manifest["row_count"] == expected_rows
        assert manifest["summary_row_count"] == expected_summary_rows
        assert manifest["run_profile"] == DEFAULT_SAMPLE_PROFILE_ID
        assert manifest["sample_scaffold"] is True
        assert manifest["engineering_only"] is False
        assert manifest["publication_ready"] is False
        assert manifest["final_study_ready"] is False
        assert manifest["operational_use_allowed"] is False
        assert manifest["formal_acceptance_evidence"] is False
        assert manifest["design_status_is_approval"] is False
        assert manifest["phase8_preflight"]["status"] == "sample_skipped"
        assert manifest["phase8_preflight"]["rail_source_decisions_pending"] is False
        assert manifest["outputs"]["results"].endswith("pilot_sample_results.csv")
        assert manifest["region_id"] == "songpa_public_demo"
        disruption_path = manifest["inputs"]["disruption_scenarios_path"].replace(
            "/",
            "\\",
        )
        assert disruption_path.endswith(
            "data\\scenarios\\disruption_scenarios.csv"
        )
        assert manifest["inputs"]["disruption_scenarios_sha256"] == _file_sha256(
            DEFAULT_SCENARIO_PATH
        )
        assert manifest["inputs"]["demand_profiles_path"].endswith(
            "data/scenarios/demand_profiles.csv"
        )
        assert manifest["inputs"]["demand_profiles_sha256"] == _file_sha256(
            DEFAULT_DEMAND_PROFILES_PATH
        )
        assert manifest["inputs"]["fleet_profiles_path"].endswith(
            "data/scenarios/fleet_profiles.csv"
        )
        assert manifest["inputs"]["fleet_profiles_sha256"] == _file_sha256(
            DEFAULT_FLEET_PROFILES_PATH
        )
        assert manifest["result_scope"] == CLAIM_SCOPE
        assert manifest["profile_refs"] == {
            "demand_profile_id": "pilot_default_demand",
            "fleet_profile_id": "pilot_default_fleet",
            "rail_service_profile_id": "pilot_fixed_headway_rail_proxy",
            "validation_profile_id": "pilot_graph_ready_and_plausibility_review",
            "road_network_profile_id": "pilot_cached_osm_graph",
        }
        profile_application = manifest["profile_application"]
        assert profile_application["runtime_profile_inputs_consumed"] is True
        assert profile_application["demand_profile_id"] == "pilot_default_demand"
        assert profile_application["fleet_profile_id"] == "pilot_default_fleet"
        assert profile_application["demand_row_count"] == 1
        assert profile_application["fleet_row_count"] == 3
        assert profile_application["can_support_final_study_gate"] is False
        assert "personnel.total" in profile_application["applied_fields"]
        assert "multimodal.lastmile_vehicle_capacity" in profile_application[
            "applied_fields"
        ]
        assert "not calibrated real-world results" in CLAIM_SCOPE
        assert {row["scenario_id"] for row in written_rows} == set(DEFAULT_SAMPLE_SCENARIO_IDS)
        assert {row["policy_id"] for row in written_rows} == set(DEFAULT_SAMPLE_POLICY_IDS)
        assert {int(row["seed"]) for row in written_rows} == set(DEFAULT_SAMPLE_SEEDS)
        assert {row["disruption_mode"] for row in written_rows} >= {"none", "capacity_reduction"}
        assert all(row["claim_scope"] == CLAIM_SCOPE for row in written_rows)
        assert legacy_manifest_path is not None and legacy_manifest_path.exists()

    print("PASS: sample pilot experiment writes conservative CSVs and manifest")


def test_phase5_profiles_apply_to_pilot_runtime_config_without_gate_claims() -> None:
    """Phase 5 profile rows should be consumed as runtime inputs, not evidence gates."""

    _assert_cached_inputs_exist()
    inputs = load_pilot_inputs()
    config, metadata = apply_pilot_demand_fleet_profiles(
        make_pilot_base_config(inputs.region),
        demand_profile_id="pilot_default_demand",
        fleet_profile_id="pilot_default_fleet",
    )

    assert config["personnel"]["total"] == 24
    assert config["personnel"]["group_size"] == 8
    assert config["personnel"]["assembly_time"] == 0.0
    assert config["lateness"]["distribution"] == "lognormal_sample_fixture"
    assert config["lateness"]["mu"] == 2.45
    assert config["lateness"]["sigma_levels"] == [0.75]
    assert config["bus"]["fleet_size"] == 3
    assert config["bus"]["dispatch_interval_min"] == 5.0
    assert config["multimodal"]["shuttle_fleet_size"] == 3
    assert config["multimodal"]["shuttle_turnaround_min"] == 8.0
    assert config["multimodal"]["lastmile_fleet_size"] == 2
    assert config["multimodal"]["lastmile_vehicle_capacity"] == 8

    assert metadata["runtime_profile_inputs_consumed"] is True
    assert metadata["demand_profiles_sha256"] == _file_sha256(
        DEFAULT_DEMAND_PROFILES_PATH
    )
    assert metadata["fleet_profiles_sha256"] == _file_sha256(
        DEFAULT_FLEET_PROFILES_PATH
    )
    assert metadata["can_support_parameter_evidence_gate"] is False
    assert metadata["can_support_acceptance_gate"] is False
    assert metadata["can_support_publication_gate"] is False
    assert metadata["can_support_final_study_gate"] is False
    assert "profile rows are bounded scenario assumptions" in (
        "; ".join(metadata["remaining_blockers"])
    )

    print("PASS: Phase 5 profile rows apply to runtime config without gate claims")


def test_pending_rail_source_decisions_block_non_sample_profiles() -> None:
    """Staged/full profiles should not run as evidence while rail decisions are pending."""

    _assert_cached_inputs_exist()
    with TemporaryDirectory() as directory:
        directory_path = Path(directory)
        rail_manifest_path = directory_path / "pending_rail_source_decision_manifest.json"
        _write_pending_rail_source_decision_manifest(rail_manifest_path)

        try:
            run_pilot_experiments(
                output_dir=directory_path / "outputs",
                run_profile=DEFAULT_STAGED_PROFILE_ID,
                rail_source_decision_manifest_path=rail_manifest_path,
                seeds=(2101,),
                policy_ids=("bus_only",),
                scenario_ids=("no_disruption",),
            )
        except PilotExperimentPreflightError as exc:
            assert "rail source decisions remain pending" in str(exc)
        else:
            raise AssertionError("pending rail decisions should block staged runs")

        output_dir = directory_path / "outputs"
        assert not output_dir.exists() or not any(output_dir.iterdir())

    print("PASS: pending rail source decisions block non-sample profiles")


def test_completed_non_formal_rail_decisions_without_support_flags_block_profiles() -> None:
    """Completed non-formal rail decisions are not enough for evidence runs."""

    _assert_cached_inputs_exist()
    with TemporaryDirectory() as directory:
        directory_path = Path(directory)
        rail_manifest_path = directory_path / "completed_non_formal_rail_source_decision_manifest.json"
        _write_completed_rail_source_decision_manifest(rail_manifest_path)

        try:
            run_pilot_experiments(
                output_dir=directory_path / "outputs",
                run_profile=DEFAULT_STAGED_PROFILE_ID,
                rail_source_decision_manifest_path=rail_manifest_path,
                seeds=(2101,),
                policy_ids=("bus_only",),
                scenario_ids=("no_disruption",),
            )
        except PilotExperimentPreflightError as exc:
            message = str(exc)
            assert "rail source decisions remain pending" in message
            assert "publication_ready is false" in message
            assert "can_support_rail_evidence_gate is false" in message
            assert "can_support_acceptance_gate is false" in message
        else:
            raise AssertionError("completed non-formal rail decisions should still block")

        output_dir = directory_path / "outputs"
        assert not output_dir.exists() or not any(output_dir.iterdir())

    print("PASS: non-formal rail decisions without support flags block profiles")


def test_unresolved_artifact_invalidation_blocks_non_sample_profiles() -> None:
    """Staged/full profiles should not run as evidence with stale downstream artifacts."""

    _assert_cached_inputs_exist()
    with TemporaryDirectory() as directory:
        directory_path = Path(directory)
        rail_manifest_path = directory_path / "completed_rail_source_decision_manifest.json"
        invalidation_manifest_path = directory_path / "artifact_invalidation_matrix.json"
        _write_phase8_ready_rail_source_decision_manifest(rail_manifest_path)
        write_artifact_invalidation_matrix(
            output_path=directory_path / "artifact_invalidation_matrix.csv",
            manifest_path=invalidation_manifest_path,
            doc_path=directory_path / "artifact_invalidation_matrix.md",
        )

        try:
            run_pilot_experiments(
                output_dir=directory_path / "outputs",
                run_profile=DEFAULT_STAGED_PROFILE_ID,
                rail_source_decision_manifest_path=rail_manifest_path,
                artifact_invalidation_manifest_path=invalidation_manifest_path,
                seeds=(2101,),
                policy_ids=("bus_only",),
                scenario_ids=("no_disruption",),
            )
        except PilotExperimentPreflightError as exc:
            assert "artifact invalidation blockers remain unresolved" in str(exc)
        else:
            raise AssertionError("unresolved artifact invalidation should block staged runs")

        output_dir = directory_path / "outputs"
        assert not output_dir.exists() or not any(output_dir.iterdir())

    print("PASS: unresolved artifact invalidation blocks non-sample profiles")


def test_engineering_only_bypass_labels_rows_and_manifest() -> None:
    """Explicit engineering-only runs must remain non-publication and non-acceptance."""

    _assert_cached_inputs_exist()
    with TemporaryDirectory() as directory:
        directory_path = Path(directory)
        rail_manifest_path = directory_path / "pending_rail_source_decision_manifest.json"
        _write_pending_rail_source_decision_manifest(rail_manifest_path)
        result = run_pilot_experiments(
            output_dir=directory_path / "outputs",
            run_profile=DEFAULT_STAGED_PROFILE_ID,
            rail_source_decision_manifest_path=rail_manifest_path,
            engineering_only=True,
            seeds=(2101,),
            policy_ids=("bus_only",),
            scenario_ids=("no_disruption",),
        )

        with result["manifest_path"].open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)
        with result["results_path"].open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        with result["summary_path"].open("r", encoding="utf-8", newline="") as handle:
            summary_rows = list(csv.DictReader(handle))

        assert manifest["engineering_only"] is True
        assert manifest["phase8_preflight"]["status"] == "engineering_only_bypass"
        assert manifest["phase8_preflight"]["rail_source_decisions_pending"] is True
        assert manifest["phase8_preflight"]["artifact_invalidation_blocks_phase9"] is False
        assert manifest["publication_ready"] is False
        assert manifest["final_study_ready"] is False
        assert manifest["operational_use_allowed"] is False
        assert manifest["formal_acceptance_evidence"] is False
        assert manifest["rail_source_decision_manifest_sha256"] == _file_sha256(
            rail_manifest_path
        )
        assert "not publication evidence" in manifest["result_scope"]
        assert "not final-study evidence" in manifest["result_scope"]
        assert "not formal acceptance evidence" in manifest["result_scope"]
        assert "non-publication" in manifest["result_scope"]
        assert "non-acceptance" in manifest["result_scope"]
        assert "non-operational" in manifest["result_scope"]
        assert rows
        assert summary_rows
        assert all(row["claim_scope"] == manifest["result_scope"] for row in rows)
        assert all(row["claim_scope"] == manifest["result_scope"] for row in summary_rows)
        assert all(ENGINEERING_ONLY_CLAIM_SCOPE in row["claim_scope"] for row in rows)

    print("PASS: engineering-only bypass labels rows and manifest")


def test_scoped_compact_regeneration_runs_after_prerequisite_closeout() -> None:
    """Scoped compact regeneration should not require global Phase 9 readiness."""

    _assert_cached_inputs_exist()
    with TemporaryDirectory() as directory:
        directory_path = Path(directory)
        rail_manifest_path = directory_path / "pending_rail_source_decision_manifest.json"
        invalidation_manifest_path = directory_path / "artifact_invalidation_matrix.json"
        closeout_manifest_path = directory_path / "artifact_invalidation_closeout.json"
        closeout_csv_path = directory_path / "artifact_invalidation_closeout.csv"
        action_queue_path = directory_path / "artifact_invalidation_action_queue.csv"
        _write_pending_rail_source_decision_manifest(rail_manifest_path)
        write_artifact_invalidation_matrix(
            output_path=directory_path / "artifact_invalidation_matrix.csv",
            manifest_path=invalidation_manifest_path,
            doc_path=directory_path / "artifact_invalidation_matrix.md",
        )
        _write_compact_scope_action_queue(action_queue_path)
        _write_compact_scope_closeout(
            csv_path=closeout_csv_path,
            manifest_path=closeout_manifest_path,
            prerequisite_closed=True,
        )

        result = run_pilot_experiments(
            output_dir=directory_path / "outputs",
            run_profile=DEFAULT_STAGED_PROFILE_ID,
            rail_source_decision_manifest_path=rail_manifest_path,
            artifact_invalidation_manifest_path=invalidation_manifest_path,
            artifact_invalidation_closeout_manifest_path=closeout_manifest_path,
            closeout_action_queue_path=action_queue_path,
            closeout_regeneration_scope="compact_outputs",
            seeds=(2101,),
            policy_ids=("bus_only",),
            scenario_ids=("no_disruption",),
        )

        with result["manifest_path"].open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)
        with result["results_path"].open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))

    assert manifest["engineering_only"] is False
    assert manifest["closeout_regeneration_scope"] == "compact_outputs"
    assert manifest["closeout_regeneration_scope_status"] == "passed"
    assert manifest["clean_checkout_status"] == "not_required_for_current_closeout"
    assert manifest["phase8_preflight"]["status"] == "scoped_closeout_regeneration"
    assert manifest["artifact_invalidation_blocks_phase9"] is True
    assert manifest["scope_invalidation_blocks"] is False
    assert manifest["rail_source_decisions_pending"] is True
    assert manifest["phase8_preflight"]["rail_source_decisions_pending"] is True
    assert manifest["publication_ready"] is False
    assert manifest["final_study_ready"] is False
    assert manifest["formal_acceptance_evidence"] is False
    assert "--closeout-regeneration-scope compact_outputs" in manifest["executed_command"]
    assert rows
    assert all("Scoped compact-output" in row["claim_scope"] for row in rows)

    print("PASS: scoped compact regeneration runs after prerequisite closeout")


def test_scoped_compact_regeneration_blocks_until_prerequisites_close() -> None:
    """Scoped regeneration must fail if earlier invalidation batches are still open."""

    _assert_cached_inputs_exist()
    with TemporaryDirectory() as directory:
        directory_path = Path(directory)
        rail_manifest_path = directory_path / "ready_rail_source_decision_manifest.json"
        invalidation_manifest_path = directory_path / "artifact_invalidation_matrix.json"
        closeout_manifest_path = directory_path / "artifact_invalidation_closeout.json"
        closeout_csv_path = directory_path / "artifact_invalidation_closeout.csv"
        action_queue_path = directory_path / "artifact_invalidation_action_queue.csv"
        _write_phase8_ready_rail_source_decision_manifest(rail_manifest_path)
        write_artifact_invalidation_matrix(
            output_path=directory_path / "artifact_invalidation_matrix.csv",
            manifest_path=invalidation_manifest_path,
            doc_path=directory_path / "artifact_invalidation_matrix.md",
        )
        _write_compact_scope_action_queue(action_queue_path)
        _write_compact_scope_closeout(
            csv_path=closeout_csv_path,
            manifest_path=closeout_manifest_path,
            prerequisite_closed=False,
        )

        try:
            run_pilot_experiments(
                output_dir=directory_path / "outputs",
                run_profile=DEFAULT_STAGED_PROFILE_ID,
                rail_source_decision_manifest_path=rail_manifest_path,
                artifact_invalidation_manifest_path=invalidation_manifest_path,
                artifact_invalidation_closeout_manifest_path=closeout_manifest_path,
                closeout_action_queue_path=action_queue_path,
                closeout_regeneration_scope="compact_outputs",
                seeds=(2101,),
                policy_ids=("bus_only",),
                scenario_ids=("no_disruption",),
            )
        except PilotExperimentPreflightError as exc:
            assert "prerequisite closeout rows are not closed" in str(exc)
        else:
            raise AssertionError("open prerequisite rows should block scoped regeneration")

    print("PASS: scoped compact regeneration blocks until prerequisites close")


def test_design_profiles_separate_sample_staged_and_full_runs() -> None:
    """Design metadata should separate scaffold, staged, full, and candidate profiles."""

    design = load_pilot_experiment_design()
    sample = design.profiles[DEFAULT_SAMPLE_PROFILE_ID]
    staged = design.profiles[DEFAULT_STAGED_PROFILE_ID]
    full = design.profiles[DEFAULT_FULL_PROFILE_ID]
    multi_corridor = design.profiles[DEFAULT_MULTI_CORRIDOR_PROFILE_ID]
    multi_corridor_full = design.profiles[DEFAULT_MULTI_CORRIDOR_FULL_PROFILE_ID]

    assert sample.sample_scaffold is True
    assert staged.sample_scaffold is False
    assert full.sample_scaffold is False
    assert multi_corridor.sample_scaffold is False
    assert multi_corridor_full.sample_scaffold is False
    assert sample.output_prefix == "pilot_sample"
    assert staged.output_prefix == "pilot_staged"
    assert full.output_prefix == "pilot_full"
    assert multi_corridor.output_prefix == "pilot_multi_corridor"
    assert multi_corridor_full.output_prefix == "pilot_multi_corridor_full"
    assert sample.graph_reduction_strategy == GRAPH_REDUCTION_SINGLE_CORRIDOR
    assert staged.graph_reduction_strategy == GRAPH_REDUCTION_SINGLE_CORRIDOR
    assert full.graph_reduction_strategy == GRAPH_REDUCTION_MULTI_CORRIDOR
    assert multi_corridor.graph_reduction_strategy == GRAPH_REDUCTION_MULTI_CORRIDOR
    assert multi_corridor_full.graph_reduction_strategy == GRAPH_REDUCTION_MULTI_CORRIDOR
    assert multi_corridor.corridor_path_count == 3
    assert multi_corridor_full.corridor_path_count == 3
    assert len(staged.scenario_ids) > len(sample.scenario_ids)
    assert len(staged.policy_ids) > len(sample.policy_ids)
    assert len(full.seeds) > len(staged.seeds)
    assert len(multi_corridor.seeds) == len(DEFAULT_SAMPLE_SEEDS)
    assert multi_corridor_full.seeds == full.seeds
    assert set(multi_corridor_full.policy_ids).issubset(set(full.policy_ids))
    assert set(multi_corridor_full.scenario_ids).issubset(set(full.scenario_ids))
    assert sample.demand_profile_id == "pilot_default_demand"
    assert sample.fleet_profile_id == "pilot_default_fleet"
    assert sample.rail_service_profile_id == "pilot_fixed_headway_rail_proxy"
    assert sample.validation_profile_id == "pilot_graph_ready_and_plausibility_review"
    assert sample.road_network_profile_id == "pilot_cached_osm_graph"
    assert "bus_corridor_redundancy" in design.excluded_policy_ids
    assert "not calibrated" in staged.result_scope.lower()
    assert multi_corridor.result_scope == PILOT_MULTI_CORRIDOR_CANDIDATE_CLAIM_SCOPE
    assert (
        multi_corridor_full.result_scope
        == PILOT_MULTI_CORRIDOR_FULL_CANDIDATE_CLAIM_SCOPE
    )

    print("PASS: pilot experiment design separates sample, staged, full, and candidate profiles")


def test_multi_corridor_candidate_uses_distinct_graph_and_outputs() -> None:
    """The multi-corridor candidate profile should not overwrite canonical outputs."""

    _assert_cached_inputs_exist()
    single_inputs = load_pilot_inputs(
        reduce_graph=True,
        graph_reduction_strategy=GRAPH_REDUCTION_SINGLE_CORRIDOR,
        corridor_path_count=1,
    )
    multi_inputs = load_pilot_inputs(
        reduce_graph=True,
        graph_reduction_strategy=GRAPH_REDUCTION_MULTI_CORRIDOR,
        corridor_path_count=3,
    )

    assert single_inputs.graph.number_of_nodes() == 118
    assert single_inputs.graph.number_of_edges() == 174
    assert multi_inputs.graph.number_of_nodes() == 164
    assert multi_inputs.graph.number_of_edges() == 246
    assert multi_inputs.graph.graph["corridor_path_count"] == 3

    with TemporaryDirectory() as directory:
        result = run_pilot_experiments(
            output_dir=directory,
            run_profile=DEFAULT_MULTI_CORRIDOR_PROFILE_ID,
            engineering_only=True,
            seeds=(4101,),
            policy_ids=("bus_only",),
            scenario_ids=("no_disruption",),
        )

        with result["manifest_path"].open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)

        assert result["results_path"].name == "pilot_multi_corridor_results.csv"
        assert result["summary_path"].name == "pilot_multi_corridor_summary.csv"
        assert result["manifest_path"].name == "pilot_multi_corridor_manifest.json"
        assert "legacy_manifest_path" not in result
        assert manifest["run_profile"] == DEFAULT_MULTI_CORRIDOR_PROFILE_ID
        assert manifest["run_stage"] == "staged"
        assert manifest["output_prefix"] == "pilot_multi_corridor"
        assert manifest["graph_nodes"] == 164
        assert manifest["graph_edges"] == 246
        assert manifest["source_graph_nodes"] == 4608
        assert manifest["source_graph_edges"] == 9148
        assert manifest["analysis_graph_reduced"] is True
        assert manifest["graph_reduction_strategy"] == GRAPH_REDUCTION_MULTI_CORRIDOR
        assert manifest["corridor_path_count"] == 3
        assert (
            manifest["graph_scale"]["analysis"]["graph_reduction_strategy"]
            == GRAPH_REDUCTION_MULTI_CORRIDOR
        )
        assert manifest["graph_scale"]["analysis"]["graph_corridor_path_count"] == 3
        assert manifest["engineering_only"] is True
        assert manifest["profile_design_complete"] is False
        assert "not calibrated real-world" in manifest["result_scope"]

    print("PASS: multi-corridor candidate profile writes separated outputs")


def test_multi_corridor_full_candidate_uses_full_matrix_and_distinct_outputs() -> None:
    """The full multi-corridor candidate should mirror full-pilot dimensions."""

    _assert_cached_inputs_exist()
    design = load_pilot_experiment_design()
    full = design.profiles[DEFAULT_FULL_PROFILE_ID]

    expected_full_rows = (
        len(full.policy_ids) * len(full.scenario_ids) * len(full.seeds)
    )
    assert expected_full_rows == 15870

    with TemporaryDirectory() as directory:
        result = run_pilot_experiments(
            output_dir=directory,
            run_profile=DEFAULT_MULTI_CORRIDOR_FULL_PROFILE_ID,
            engineering_only=True,
            seeds=(3101,),
            policy_ids=("bus_only", "baseline_multimodal"),
            scenario_ids=("no_disruption", "songpa_critical_link_blockage"),
        )

        with result["manifest_path"].open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)

        assert result["results_path"].name == "pilot_multi_corridor_full_results.csv"
        assert result["summary_path"].name == "pilot_multi_corridor_full_summary.csv"
        assert result["manifest_path"].name == "pilot_multi_corridor_full_manifest.json"
        assert manifest["run_profile"] == DEFAULT_MULTI_CORRIDOR_FULL_PROFILE_ID
        assert manifest["run_stage"] == "full"
        assert manifest["output_prefix"] == "pilot_multi_corridor_full"
        assert manifest["row_count"] == 4
        assert manifest["expected_row_count"] == 4
        assert manifest["profile_design_row_count"] == 2520
        assert manifest["executed_row_count"] == 4
        assert manifest["profile_design_complete"] is False
        assert manifest["engineering_override_run"] is True
        assert manifest["engineering_only"] is True
        assert manifest["publication_ready"] is False
        assert manifest["final_study_ready"] is False
        assert manifest["formal_acceptance_evidence"] is False
        assert manifest["graph_nodes"] == 164
        assert manifest["graph_edges"] == 246
        assert manifest["graph_reduction_strategy"] == GRAPH_REDUCTION_MULTI_CORRIDOR
        assert manifest["corridor_path_count"] == 3
        assert "not calibrated real-world" in manifest["result_scope"]

    print("PASS: full multi-corridor candidate keeps full dimensions and separated outputs")


def test_staged_pilot_outputs_use_distinct_names_and_manifest_fields() -> None:
    """A narrow staged override should not overwrite sample output names."""

    _assert_cached_inputs_exist()
    with TemporaryDirectory() as directory:
        result = run_pilot_experiments(
            output_dir=directory,
            run_profile=DEFAULT_STAGED_PROFILE_ID,
            engineering_only=True,
            seeds=(2101,),
            policy_ids=("bus_only", "baseline_multimodal"),
            scenario_ids=("no_disruption", "songpa_access_origin_to_station"),
        )

        with result["manifest_path"].open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)

        assert result["results_path"].name == "pilot_staged_results.csv"
        assert result["summary_path"].name == "pilot_staged_summary.csv"
        assert result["manifest_path"].name == "pilot_staged_manifest.json"
        assert result["output_lock_receipt_path"].name == (
            "pilot_staged_output_lock_receipt.json"
        )
        assert result["output_lock_receipt_path"].exists()
        assert "legacy_manifest_path" not in result
        assert manifest["run_profile"] == DEFAULT_STAGED_PROFILE_ID
        assert manifest["run_stage"] == "staged"
        assert manifest["sample_scaffold"] is False
        assert manifest["output_prefix"] == "pilot_staged"
        assert manifest["output_dir"].endswith(directory.replace("\\", "/"))
        assert "--engineering-only" in manifest["executed_command"]
        assert "--seeds 2101" in manifest["executed_command"]
        assert "--policy-ids bus_only,baseline_multimodal" in manifest["executed_command"]
        assert (
            "--scenario-ids no_disruption,songpa_access_origin_to_station"
            in manifest["executed_command"]
        )
        assert manifest["row_count"] == 4
        assert manifest["summary_row_count"] == 4
        assert manifest["expected_row_count"] == 4
        assert manifest["engineering_only"] is True
        assert manifest["profile_design_complete"] is False
        assert manifest["engineering_override_run"] is True
        assert manifest["design_overrides"] == {
            "policy_ids": True,
            "scenario_ids": True,
            "seeds": True,
        }
        assert manifest["outputs"]["results"].endswith("pilot_staged_results.csv")
        assert manifest["outputs"]["manifest"].endswith("pilot_staged_manifest.json")
        assert manifest["outputs"]["output_lock_receipt"].endswith(
            "pilot_staged_output_lock_receipt.json"
        )
        assert manifest["output_lock"]["acquired"] is True
        assert manifest["output_lock"]["lock_mechanism"] == "atomic_create_x_mode"
        assert manifest["output_lock_release"]["release_status"] == "released"
        assert manifest["runtime"]["actual_worker_count"] == 1
        assert manifest["runtime"]["worker_count_control"] == "none_serial_current_runner"
        assert manifest["runtime"]["gpu_used_for_simulation"] is False
        assert manifest["runtime"]["wall_time_seconds"] >= 0.0
        assert manifest["runtime"]["memory_before"]["method"] in {
            "GlobalMemoryStatusEx",
            "unsupported_non_windows_stdlib",
        }
        assert manifest["inputs"]["region_sha256"] == _file_sha256(DEFAULT_REGION_PATH)
        assert manifest["inputs"]["cache_sha256"] == _file_sha256(DEFAULT_CACHE_PATH)
        assert manifest["inputs"]["policy_alternatives_sha256"]
        assert manifest["inputs"]["pilot_experiment_design_sha256"]
        assert manifest["config_hashes"]["base_config_sha256"]
        assert set(manifest["config_hashes"]["policy_config_sha256s"]) == {
            "bus_only",
            "baseline_multimodal",
        }
        assert len(
            manifest["config_hashes"]["effective_policy_scenario_config_sha256s"]
        ) == 4
        inventory = manifest["output_inventory"]["files"]
        assert inventory["results"]["exists"] is True
        assert inventory["results"]["csv_data_row_count"] == manifest["row_count"]
        assert inventory["summary"]["csv_data_row_count"] == manifest["summary_row_count"]
        assert inventory["manifest"]["sha256_record_location"] == (
            "output_lock_receipt.outputs.manifest_sha256"
        )
        with result["output_lock_receipt_path"].open("r", encoding="utf-8") as handle:
            receipt = json.load(handle)
        assert receipt["release"]["release_status"] == "released"
        assert receipt["outputs"]["manifest_sha256"] == _file_sha256(result["manifest_path"])
        assert manifest["analysis_graph_reduced"] is True
        assert "graph_scale" in manifest
        assert manifest["profile_refs"]["validation_profile_id"] == (
            "pilot_graph_ready_and_plausibility_review"
        )
        assert "not calibrated real-world" in manifest["result_scope"]

    print("PASS: staged pilot outputs use separated names and manifest metadata")


def test_pilot_runner_records_applied_road_class_overrides() -> None:
    """A reviewed override table should be applied and recorded in the manifest."""

    _assert_cached_inputs_exist()
    with TemporaryDirectory() as directory:
        override_path = Path(directory) / "road_class_overrides.csv"
        _write_road_override_csv(override_path)
        result = run_pilot_experiments(
            output_dir=directory,
            road_class_overrides_path=override_path,
            sample=True,
            seeds=(1101,),
            policy_ids=("bus_only",),
            scenario_ids=("no_disruption",),
        )

        with result["manifest_path"].open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)

        assert manifest["row_count"] == 1
        assert manifest["road_class_overrides_applied"] is True
        assert manifest["inputs"]["road_class_overrides_path"].endswith(
            "road_class_overrides.csv"
        )
        assert manifest["inputs"]["road_class_overrides_sha256"] == _file_sha256(
            override_path
        )
        assert "road_class_overrides:" in manifest["graph_source"]

    print("PASS: pilot runner records applied road-class overrides")


def test_summary_groups_policy_scenario_mode_means() -> None:
    """Summary rows should average metrics by policy, scenario, and mode."""

    rows = [
        {
            "region_id": "r",
            "graph_source": "cached_graphml:g.graphml",
            "policy_id": "p",
            "scenario_id": "s",
            "scenario_family": "no_disruption",
            "scenario_type": "none",
            "disruption_mode": "none",
            "mode": "bus_only",
            "completion_rate": 0.5,
            "censored_count": 1,
            "penalized_makespan": 100.0,
            "makespan": 80.0,
            "road_vehicle_service_minutes": 10.0,
            "train_service_minutes": 0.0,
            "total_service_minutes": 10.0,
            "passenger_travel_minutes": 40.0,
            "passengers_per_total_service_minute": 0.2,
        },
        {
            "region_id": "r",
            "graph_source": "cached_graphml:g.graphml",
            "policy_id": "p",
            "scenario_id": "s",
            "scenario_family": "no_disruption",
            "scenario_type": "none",
            "disruption_mode": "none",
            "mode": "bus_only",
            "completion_rate": 1.0,
            "censored_count": 0,
            "penalized_makespan": 50.0,
            "makespan": 50.0,
            "road_vehicle_service_minutes": 20.0,
            "train_service_minutes": 0.0,
            "total_service_minutes": 20.0,
            "passenger_travel_minutes": 60.0,
            "passengers_per_total_service_minute": 0.4,
        },
    ]

    summary = summarize_pilot_rows(rows)

    assert len(summary) == 1
    assert summary[0]["run_count"] == 2
    assert summary[0]["mean_completion_rate"] == 0.75
    assert summary[0]["mean_censored_count"] == 0.5
    assert summary[0]["mean_total_service_minutes"] == 15.0
    assert summary[0]["mean_passengers_per_total_service_minute"] == 0.3
    assert summary[0]["claim_scope"] == CLAIM_SCOPE

    print("PASS: summary rows group and average key metrics")


def _assert_cached_inputs_exist() -> None:
    assert DEFAULT_REGION_PATH.exists(), f"missing pilot region file: {DEFAULT_REGION_PATH}"
    assert DEFAULT_CACHE_PATH.exists(), f"missing pilot cache file: {DEFAULT_CACHE_PATH}"


def _write_road_override_csv(path: Path) -> None:
    row = {
        "highway": "primary",
        "speed_kph": "42",
        "capacity_veh_per_hr": "1234",
        "base_p_fail": "0.01",
        "source_class": "literature-derived",
        "source_name": "fixture",
        "source_url_or_citation": "fixture",
        "notes": "fixture row",
    }
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerow(row)


def _write_pending_rail_source_decision_manifest(path: Path) -> None:
    payload = {
        "schema_version": 1,
        "row_count": 2,
        "completed_source_decision_count": 0,
        "rail_source_decision_recorded": False,
        "can_support_rail_evidence_gate": False,
        "can_support_acceptance_gate": False,
        "can_mark_complete": False,
        "publication_ready": False,
        "rail_service_evidence_present": True,
        "rail_service_evidence_gate_closure_candidate_count": 0,
        "action_decision_status_counts": {"pending_action_decision": 2},
        "decision_status_counts": {
            "blocked_missing_rail_source_decision": 1,
            "needs_human_review_rail_source_decision": 1,
        },
        "claim_boundary": "fixture rail source-decision packet only",
        "result_scope": "fixture rail source-decision packet only",
        "remaining_blockers": ["fixture pending rail source decision"],
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _write_completed_rail_source_decision_manifest(path: Path) -> None:
    payload = {
        "schema_version": 1,
        "row_count": 2,
        "completed_source_decision_count": 2,
        "rail_source_decision_recorded": True,
        "can_support_rail_evidence_gate": False,
        "can_support_acceptance_gate": False,
        "can_mark_complete": False,
        "publication_ready": False,
        "rail_service_evidence_present": True,
        "rail_service_evidence_gate_closure_candidate_count": 0,
        "action_decision_status_counts": {"completed_non_formal_source_decision": 2},
        "decision_status_counts": {
            "source_backed_acquisition_complete_non_formal": 1,
            "excluded_non_formal": 1,
        },
        "claim_boundary": "fixture completed rail source-decision packet only",
        "result_scope": "fixture completed rail source-decision packet only",
        "remaining_blockers": [],
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _write_phase8_ready_rail_source_decision_manifest(path: Path) -> None:
    payload = {
        "schema_version": 1,
        "row_count": 2,
        "completed_source_decision_count": 2,
        "rail_source_decision_recorded": True,
        "can_support_rail_evidence_gate": True,
        "can_support_acceptance_gate": True,
        "can_mark_complete": True,
        "publication_ready": True,
        "rail_service_evidence_present": True,
        "rail_service_evidence_gate_closure_candidate_count": 1,
        "action_decision_status_counts": {"completed_non_formal_source_decision": 2},
        "decision_status_counts": {
            "source_backed_acquisition_complete_non_formal": 1,
            "excluded_non_formal": 1,
        },
        "claim_boundary": "fixture rail source-decision support gate ready",
        "result_scope": "fixture rail source-decision support gate ready",
        "remaining_blockers": [],
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _write_compact_scope_action_queue(path: Path) -> None:
    fieldnames = [
        "action_order",
        "action_batch",
        "dependency_stage",
        "invalidation_row_id",
    ]
    rows = [
        {
            "action_order": "10",
            "action_batch": "upstream_evidence_and_benchmarks",
            "dependency_stage": "before_phase9_promotion",
            "invalidation_row_id": "region_boundary->road_snapshots",
        },
        {
            "action_order": "30",
            "action_batch": "compact_outputs",
            "dependency_stage": "before_phase9_promotion",
            "invalidation_row_id": "region_boundary->compact_outputs",
        },
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_compact_scope_closeout(
    *,
    csv_path: Path,
    manifest_path: Path,
    prerequisite_closed: bool,
) -> None:
    fieldnames = list(_compact_scope_closeout_row("fixture", True))
    rows = [
        _compact_scope_closeout_row(
            "region_boundary->road_snapshots",
            prerequisite_closed,
        ),
        _compact_scope_closeout_row(
            "region_boundary->compact_outputs",
            False,
        ),
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    closed_count = sum(
        1 for row in rows if row["can_clear_invalidation_gate"] == "true"
    )
    manifest = {
        "schema_version": 1,
        "row_count": len(rows),
        "closed_row_count": closed_count,
        "pending_or_invalid_row_count": len(rows) - closed_count,
        "phase9_promotion_ready": False,
        "publication_ready": False,
        "final_study_ready": False,
        "formal_acceptance_evidence": False,
        "can_mark_complete": False,
        "outputs": {"csv": str(csv_path)},
    }
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _compact_scope_closeout_row(row_id: str, closed: bool) -> dict[str, str]:
    artifact = json.dumps(
        [{"path": f"results/{row_id.replace('->', '_')}.json", "sha256": "a" * 64}]
    )
    return {
        "closeout_schema_version": "1",
        "invalidation_row_id": row_id,
        "upstream_change_group": row_id.split("->", 1)[0],
        "stale_downstream_group": row_id.split("->", 1)[1] if "->" in row_id else "",
        "required_disposition": "regenerate",
        "actual_disposition": "regenerated" if closed else "pending",
        "closeout_status": "closed_invalidation_only" if closed else "pending",
        "affected_artifacts_json": artifact if closed else "[]",
        "upstream_artifacts_json": artifact if closed else "[]",
        "downstream_before_artifacts_json": artifact if closed else "[]",
        "downstream_after_artifacts_json": artifact if closed else "[]",
        "exclusion_scope": "",
        "rerun_command": "fixture rerun command" if closed else "",
        "rerun_exit_code": "0" if closed else "",
        "rerun_result": "pass" if closed else "not_run",
        "audit_command": "fixture audit command" if closed else "",
        "audit_exit_code": "0" if closed else "",
        "audit_result": "pass" if closed else "not_run",
        "targeted_test_command": "fixture targeted test" if closed else "",
        "targeted_test_exit_code": "0" if closed else "",
        "targeted_test_result": "pass" if closed else "not_run",
        "reviewer_signoff_status": (
            "signed_off_for_invalidation_closeout_only" if closed else "unsigned"
        ),
        "reviewer_id": "fixture-reviewer" if closed else "",
        "reviewed_at_utc": "2026-06-05T00:00:00+00:00" if closed else "",
        "claim_boundary_effect": (
            "claim_eligible_after_reaudit" if closed else "blocks_claim_support"
        ),
        "claim_boundary_review_result": "pass" if closed else "pending",
        "phase9_promotion_effect": (
            "review_only_after_reaudit" if closed else "blocks_phase9_promotion"
        ),
        "can_clear_invalidation_gate": "true" if closed else "false",
        "publication_ready": "false",
        "final_study_ready": "false",
        "formal_acceptance_evidence": "false",
        "claim_boundary": "fixture invalidation closeout only",
        "review_notes": "fixture",
    }


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    test_forced_disruption_probabilities_are_deterministic_and_non_mutating()
    test_disruption_case_preserves_scenario_p_fail_scale()
    test_sample_pilot_experiment_writes_csvs_and_manifest()
    test_phase5_profiles_apply_to_pilot_runtime_config_without_gate_claims()
    test_pending_rail_source_decisions_block_non_sample_profiles()
    test_completed_non_formal_rail_decisions_without_support_flags_block_profiles()
    test_unresolved_artifact_invalidation_blocks_non_sample_profiles()
    test_engineering_only_bypass_labels_rows_and_manifest()
    test_scoped_compact_regeneration_runs_after_prerequisite_closeout()
    test_scoped_compact_regeneration_blocks_until_prerequisites_close()
    test_design_profiles_separate_sample_staged_and_full_runs()
    test_multi_corridor_candidate_uses_distinct_graph_and_outputs()
    test_multi_corridor_full_candidate_uses_full_matrix_and_distinct_outputs()
    test_staged_pilot_outputs_use_distinct_names_and_manifest_fields()
    test_pilot_runner_records_applied_road_class_overrides()
    test_summary_groups_policy_scenario_mode_means()
    print("\n=== REALWORLD PILOT EXPERIMENT TESTS PASSED ===")
