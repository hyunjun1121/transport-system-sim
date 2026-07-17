"""Tests for pilot scaffold sensitivity screening scaffolding."""

from __future__ import annotations

import csv
import json
import os
import sys
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.pilot_experiments import DEFAULT_CACHE_PATH, DEFAULT_REGION_PATH
from src.realworld.sensitivity import (
    CLAIM_SCOPE,
    DEFAULT_SAMPLE_POLICY_IDS,
    DEFAULT_SAMPLE_SCENARIO_IDS,
    METHOD_DETERMINISTIC,
    METHOD_MORRIS,
    MORRIS_CLAIM_SCOPE,
    MORRIS_RESULT_COLUMNS,
    MORRIS_SUMMARY_COLUMNS,
    RANK_METRICS,
    REQUIRED_PARAMETER_IDS,
    RESULT_COLUMNS,
    SUMMARY_COLUMNS,
    graph_with_selected_edge_probability,
    load_sensitivity_design,
    run_morris_sensitivity,
    run_sensitivity_screening,
    salib_problem,
)


def test_sensitivity_design_loads_required_parameters_and_salib_problem() -> None:
    """The design table should cover Workstream 9 parameters and SALib bounds."""

    parameters = load_sensitivity_design()
    by_id = {parameter.parameter_id: parameter for parameter in parameters}
    problem = salib_problem(parameters)

    assert REQUIRED_PARAMETER_IDS <= set(by_id)
    assert problem["num_vars"] == len(parameters)
    assert problem["names"] == [parameter.salib_name for parameter in parameters]
    assert len(problem["bounds"]) == len(parameters)
    assert by_id["passenger_volume"].value_for_level("low") == 16
    assert by_id["last_mile_access_disruption_probability"].high == 1.0

    print("PASS: sensitivity design loads required parameters and SALib frame")


def test_selected_edge_probability_graph_copy_is_non_mutating() -> None:
    """Sensitivity disruption probability should not mutate cached inputs."""

    _assert_cached_inputs_exist()
    with TemporaryDirectory() as directory:
        result = run_sensitivity_screening(
            parameter_ids=("last_mile_access_disruption_probability",),
            policy_ids=("baseline_multimodal",),
            scenario_ids=("songpa_last_mile_station_to_destination",),
            output_dir=directory,
        )
    rows = result["rows"]
    baseline = next(row for row in rows if row["level"] == "baseline")
    low = next(row for row in rows if row["parameter_id"] == "last_mile_access_disruption_probability" and row["level"] == "low")
    assert baseline["selected_edge_probability"] == 1.0
    assert low["selected_edge_probability"] == 0.0

    from src.realworld.disruption_scenarios import load_disruption_scenarios
    from src.realworld.pilot_experiments import load_pilot_inputs, select_disruption_cases

    inputs = load_pilot_inputs()
    scenarios = load_disruption_scenarios(region_id=inputs.region_id)
    case = select_disruption_cases(
        inputs.graph,
        scenarios,
        scenario_ids=["songpa_last_mile_station_to_destination"],
    )[0]
    prepared = graph_with_selected_edge_probability(
        inputs.graph,
        case,
        selected_edge_probability=0.25,
    )
    for selected in case.selected_edges:
        assert prepared.edges[selected.edge]["p_fail"] == 0.25
        assert inputs.graph.edges[selected.edge]["p_fail"] != 0.25

    print("PASS: selected-edge disruption probability is non-mutating")


def test_sample_sensitivity_screening_writes_csvs_and_manifest() -> None:
    """A narrow sample run should write deterministic screening artifacts."""

    _assert_cached_inputs_exist()
    with TemporaryDirectory() as directory:
        result = run_sensitivity_screening(
            output_dir=directory,
            sample=True,
            parameter_ids=(
                "passenger_volume",
                "direct_bus_fleet_size",
                "last_mile_access_disruption_probability",
            ),
            policy_ids=DEFAULT_SAMPLE_POLICY_IDS,
            scenario_ids=DEFAULT_SAMPLE_SCENARIO_IDS,
        )

        rows = result["rows"]
        summary_rows = result["summary_rows"]
        assert rows
        assert len(summary_rows) == 3 * len(RANK_METRICS)

        with result["results_path"].open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == RESULT_COLUMNS

        with result["summary_path"].open("r", encoding="utf-8", newline="") as handle:
            summary_reader = csv.DictReader(handle)
            written_summary_rows = list(summary_reader)
            assert tuple(summary_reader.fieldnames or ()) == SUMMARY_COLUMNS

        with result["manifest_path"].open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)

        assert len(written_rows) == len(rows)
        assert len(written_summary_rows) == len(summary_rows)
        assert manifest["method"] == METHOD_DETERMINISTIC
        assert manifest["row_count"] == len(rows)
        assert manifest["summary_row_count"] == len(summary_rows)
        assert manifest["salib_problem"]["num_vars"] == 3
        assert manifest["graph_scale"]["source"]["nodes"] > manifest["graph_scale"]["analysis"]["nodes"]
        assert manifest["graph_scale"]["analysis"]["reduced"] is True
        assert "sensitivity_scaffold" in manifest["analysis_graph_strategy"]
        assert manifest["result_scope"] == CLAIM_SCOPE
        assert "not calibrated real-world" in CLAIM_SCOPE
        assert all(row["claim_scope"] == CLAIM_SCOPE for row in written_rows)

    print("PASS: sample sensitivity screening writes CSVs and manifest")


def test_sample_morris_sensitivity_writes_indices_and_manifest() -> None:
    """A narrow Morris run should write formal sensitivity artifacts."""

    _assert_cached_inputs_exist()
    selected_parameters = (
        "passenger_volume",
        "direct_bus_fleet_size",
        "last_mile_access_disruption_probability",
    )
    selected_scenarios = ("songpa_random_capacity_reduction",)
    with TemporaryDirectory() as directory:
        result = run_morris_sensitivity(
            output_dir=directory,
            sample=True,
            num_trajectories=2,
            num_levels=4,
            parameter_ids=selected_parameters,
            policy_ids=DEFAULT_SAMPLE_POLICY_IDS,
            scenario_ids=selected_scenarios,
        )

        rows = result["rows"]
        summary_rows = result["summary_rows"]
        assert rows
        assert summary_rows

        with result["results_path"].open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == MORRIS_RESULT_COLUMNS

        with result["summary_path"].open("r", encoding="utf-8", newline="") as handle:
            summary_reader = csv.DictReader(handle)
            written_summary_rows = list(summary_reader)
            assert tuple(summary_reader.fieldnames or ()) == MORRIS_SUMMARY_COLUMNS

        with result["manifest_path"].open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)

        assert len(written_rows) == len(rows)
        assert len(written_summary_rows) == len(summary_rows)
        assert manifest["method"] == METHOD_MORRIS
        assert manifest["salib_available"] is True
        assert manifest["morris_sample_count"] == 2 * (len(selected_parameters) + 1)
        assert manifest["row_count"] == len(rows)
        assert manifest["summary_row_count"] == len(summary_rows)
        assert manifest["graph_scale"]["source"]["nodes"] > manifest["graph_scale"]["analysis"]["nodes"]
        assert manifest["graph_scale"]["analysis"]["reduced"] is True
        assert "sensitivity_scaffold" in manifest["analysis_graph_strategy"]
        assert manifest["result_scope"] == MORRIS_CLAIM_SCOPE
        assert "not calibrated real-world" in MORRIS_CLAIM_SCOPE
        assert all(row["claim_scope"] == MORRIS_CLAIM_SCOPE for row in written_rows)
        assert {
            row["parameter_id"]
            for row in written_summary_rows
        } == set(selected_parameters)

    print("PASS: sample Morris sensitivity writes indices and manifest")


def _assert_cached_inputs_exist() -> None:
    assert DEFAULT_REGION_PATH.exists(), f"missing pilot region file: {DEFAULT_REGION_PATH}"
    assert DEFAULT_CACHE_PATH.exists(), f"missing pilot cache file: {DEFAULT_CACHE_PATH}"


if __name__ == "__main__":
    test_sensitivity_design_loads_required_parameters_and_salib_problem()
    test_selected_edge_probability_graph_copy_is_non_mutating()
    test_sample_sensitivity_screening_writes_csvs_and_manifest()
    test_sample_morris_sensitivity_writes_indices_and_manifest()
    print("\n=== REALWORLD SENSITIVITY TESTS PASSED ===")
