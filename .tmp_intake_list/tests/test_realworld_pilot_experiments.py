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

from src.realworld.disruption_scenarios import load_disruption_scenarios
from src.realworld.pilot_experiments import (
    CLAIM_SCOPE,
    DEFAULT_CACHE_PATH,
    DEFAULT_FULL_PROFILE_ID,
    DEFAULT_MULTI_CORRIDOR_FULL_PROFILE_ID,
    DEFAULT_MULTI_CORRIDOR_PROFILE_ID,
    DEFAULT_REGION_PATH,
    DEFAULT_SAMPLE_PROFILE_ID,
    DEFAULT_SAMPLE_POLICY_IDS,
    DEFAULT_SAMPLE_SCENARIO_IDS,
    DEFAULT_SAMPLE_SEEDS,
    DEFAULT_STAGED_PROFILE_ID,
    GRAPH_REDUCTION_MULTI_CORRIDOR,
    GRAPH_REDUCTION_SINGLE_CORRIDOR,
    PILOT_MULTI_CORRIDOR_CANDIDATE_CLAIM_SCOPE,
    PILOT_MULTI_CORRIDOR_FULL_CANDIDATE_CLAIM_SCOPE,
    RESULT_COLUMNS,
    graph_with_forced_disruption_probabilities,
    load_pilot_inputs,
    load_pilot_experiment_design,
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
        assert manifest["outputs"]["results"].endswith("pilot_sample_results.csv")
        assert manifest["region_id"] == "songpa_public_demo"
        assert manifest["result_scope"] == CLAIM_SCOPE
        assert "not calibrated real-world results" in CLAIM_SCOPE
        assert {row["scenario_id"] for row in written_rows} == set(DEFAULT_SAMPLE_SCENARIO_IDS)
        assert {row["policy_id"] for row in written_rows} == set(DEFAULT_SAMPLE_POLICY_IDS)
        assert {int(row["seed"]) for row in written_rows} == set(DEFAULT_SAMPLE_SEEDS)
        assert all(row["claim_scope"] == CLAIM_SCOPE for row in written_rows)
        assert legacy_manifest_path is not None and legacy_manifest_path.exists()

    print("PASS: sample pilot experiment writes conservative CSVs and manifest")


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
    assert full.graph_reduction_strategy == GRAPH_REDUCTION_SINGLE_CORRIDOR
    assert multi_corridor.graph_reduction_strategy == GRAPH_REDUCTION_MULTI_CORRIDOR
    assert multi_corridor_full.graph_reduction_strategy == GRAPH_REDUCTION_MULTI_CORRIDOR
    assert multi_corridor.corridor_path_count == 3
    assert multi_corridor_full.corridor_path_count == 3
    assert len(staged.scenario_ids) > len(sample.scenario_ids)
    assert len(staged.policy_ids) > len(sample.policy_ids)
    assert len(full.seeds) > len(staged.seeds)
    assert len(multi_corridor.seeds) == len(DEFAULT_SAMPLE_SEEDS)
    assert multi_corridor_full.seeds == full.seeds
    assert multi_corridor_full.policy_ids == full.policy_ids
    assert multi_corridor_full.scenario_ids == full.scenario_ids
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
    assert expected_full_rows == 1890

    with TemporaryDirectory() as directory:
        result = run_pilot_experiments(
            output_dir=directory,
            run_profile=DEFAULT_MULTI_CORRIDOR_FULL_PROFILE_ID,
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
            seeds=(2101,),
            policy_ids=("bus_only", "baseline_multimodal"),
            scenario_ids=("no_disruption", "songpa_access_origin_to_station"),
        )

        with result["manifest_path"].open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)

        assert result["results_path"].name == "pilot_staged_results.csv"
        assert result["summary_path"].name == "pilot_staged_summary.csv"
        assert result["manifest_path"].name == "pilot_staged_manifest.json"
        assert "legacy_manifest_path" not in result
        assert manifest["run_profile"] == DEFAULT_STAGED_PROFILE_ID
        assert manifest["run_stage"] == "staged"
        assert manifest["sample_scaffold"] is False
        assert manifest["output_prefix"] == "pilot_staged"
        assert manifest["row_count"] == 4
        assert manifest["summary_row_count"] == 4
        assert manifest["expected_row_count"] == 4
        assert manifest["design_overrides"] == {
            "policy_ids": True,
            "scenario_ids": True,
            "seeds": True,
        }
        assert manifest["outputs"]["results"].endswith("pilot_staged_results.csv")
        assert manifest["outputs"]["manifest"].endswith("pilot_staged_manifest.json")
        assert manifest["analysis_graph_reduced"] is True
        assert "graph_scale" in manifest
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


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    test_forced_disruption_probabilities_are_deterministic_and_non_mutating()
    test_sample_pilot_experiment_writes_csvs_and_manifest()
    test_design_profiles_separate_sample_staged_and_full_runs()
    test_multi_corridor_candidate_uses_distinct_graph_and_outputs()
    test_multi_corridor_full_candidate_uses_full_matrix_and_distinct_outputs()
    test_staged_pilot_outputs_use_distinct_names_and_manifest_fields()
    test_pilot_runner_records_applied_road_class_overrides()
    test_summary_groups_policy_scenario_mode_means()
    print("\n=== REALWORLD PILOT EXPERIMENT TESTS PASSED ===")
