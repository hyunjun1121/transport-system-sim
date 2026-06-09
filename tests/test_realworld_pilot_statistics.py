"""Tests for pilot experiment uncertainty-summary tables."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.pilot_statistics import (
    DEFAULT_PILOT_FULL_RESULTS_PATH,
    DEFAULT_PILOT_TABLE_DIR,
    METRIC_CI_COLUMNS,
    PAIRED_DELTA_CI_COLUMNS,
    build_metric_ci_rows,
    build_paired_delta_ci_rows,
    load_pilot_result_rows,
    write_pilot_statistics_outputs,
)


def test_metric_ci_rows_group_seed_replications() -> None:
    """Metric CI rows should summarize repeated seeds by policy/scenario group."""

    rows = [
        _row("bus_only", "bus_only", seed=1, completion_rate=0.5, makespan=100.0),
        _row("bus_only", "bus_only", seed=2, completion_rate=1.0, makespan=120.0),
    ]

    ci_rows = build_metric_ci_rows(
        rows,
        metrics=("completion_rate", "makespan"),
        claim_scope="test scope",
    )

    assert len(ci_rows) == 2
    completion = next(row for row in ci_rows if row["metric"] == "completion_rate")
    makespan = next(row for row in ci_rows if row["metric"] == "makespan")
    assert tuple(completion.keys()) == METRIC_CI_COLUMNS
    assert completion["sample_count"] == 2
    assert completion["mean"] == 0.75
    assert completion["ci95_low"] < completion["mean"] < completion["ci95_high"]
    assert makespan["mean"] == 110.0
    assert makespan["claim_scope"] == "test scope"

    print("PASS: metric CI rows summarize seed replications")


def test_paired_delta_rows_compare_against_bus_only_by_seed() -> None:
    """Paired deltas should compare each policy against bus-only for the same seed."""

    rows = [
        _row("bus_only", "bus_only", seed=1, completion_rate=0.5, makespan=100.0),
        _row("bus_only", "bus_only", seed=2, completion_rate=0.75, makespan=130.0),
        _row("baseline_multimodal", "multimodal", seed=1, completion_rate=1.0, makespan=90.0),
        _row("baseline_multimodal", "multimodal", seed=2, completion_rate=1.0, makespan=120.0),
    ]

    delta_rows = build_paired_delta_ci_rows(
        rows,
        metrics=("completion_rate", "makespan"),
        claim_scope="test scope",
    )

    assert len(delta_rows) == 2
    completion = next(row for row in delta_rows if row["metric"] == "completion_rate")
    makespan = next(row for row in delta_rows if row["metric"] == "makespan")
    assert tuple(completion.keys()) == PAIRED_DELTA_CI_COLUMNS
    assert completion["paired_count"] == 2
    assert completion["mean_delta"] == 0.375
    assert completion["metric_direction"] == "higher_is_better"
    assert completion["delta_interpretation"] == "positive_delta_favors_comparison_policy"
    assert makespan["mean_delta"] == -10.0
    assert makespan["metric_direction"] == "lower_is_better"
    assert makespan["delta_interpretation"] == "negative_delta_favors_comparison_policy"

    print("PASS: paired-delta rows compare policies against bus-only by seed")


def test_write_statistics_outputs_records_manifest() -> None:
    """The writer should create both CI tables and a conservative manifest."""

    rows = [
        _row("bus_only", "bus_only", seed=1, completion_rate=0.5, makespan=100.0),
        _row("baseline_multimodal", "multimodal", seed=1, completion_rate=1.0, makespan=90.0),
    ]
    with TemporaryDirectory() as directory:
        manifest_path = Path(directory) / "source_manifest.json"
        results_path = Path(directory) / "fixture_results.csv"
        results_path.write_text("fixture results\n", encoding="utf-8")
        manifest_path.write_text(
            json.dumps({"run_profile": "fixture", "row_count": 2}),
            encoding="utf-8",
        )
        result = write_pilot_statistics_outputs(
            rows=rows,
            output_dir=directory,
            output_prefix="fixture",
            source_results_path=results_path,
            source_manifest_path=manifest_path,
        )

        with result["metric_path"].open("r", encoding="utf-8", newline="") as handle:
            metric_rows = list(csv.DictReader(handle))
        with result["paired_delta_path"].open("r", encoding="utf-8", newline="") as handle:
            paired_rows = list(csv.DictReader(handle))
        with result["manifest_path"].open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)

        assert metric_rows
        assert paired_rows
        assert manifest["source_run_profile"] == "fixture"
        assert manifest["source_results_sha256"] == hashlib.sha256(
            results_path.read_bytes()
        ).hexdigest()
        assert manifest["source_manifest_sha256"] == hashlib.sha256(
            manifest_path.read_bytes()
        ).hexdigest()
        assert manifest["metric_ci_row_count"] == len(result["metric_rows"])
        assert manifest["paired_delta_ci_row_count"] == len(result["paired_delta_rows"])
        assert "not calibrated real-world" in manifest["result_scope"]
        assert "exploratory" in manifest["multiple_comparison_method"]

    print("PASS: statistics writer records manifest")


def test_shipped_full_pilot_statistics_are_reproducible() -> None:
    """Generated full-pilot statistics should match current scaffold dimensions."""

    assert DEFAULT_PILOT_FULL_RESULTS_PATH.exists()
    rows = load_pilot_result_rows(DEFAULT_PILOT_FULL_RESULTS_PATH)
    metric_rows = build_metric_ci_rows(rows)
    delta_rows = build_paired_delta_ci_rows(rows)

    assert len(rows) == 1890
    assert len(metric_rows) == 819
    assert len(delta_rows) == 702

    print("PASS: shipped full-pilot statistics match current scaffold dimensions")


def test_shipped_multi_corridor_statistics_are_reproducible() -> None:
    """Generated multi-corridor candidate statistics should match current dimensions."""

    results_path = DEFAULT_PILOT_TABLE_DIR.parent / "pilot_multi_corridor_results.csv"
    assert results_path.exists()
    rows = load_pilot_result_rows(results_path)
    metric_rows = build_metric_ci_rows(rows)
    delta_rows = build_paired_delta_ci_rows(rows)

    assert len(rows) == 32
    assert len(metric_rows) == 208
    assert len(delta_rows) == 156

    print("PASS: shipped multi-corridor statistics match current candidate dimensions")


def test_shipped_multi_corridor_full_statistics_are_reproducible() -> None:
    """Generated full multi-corridor statistics should match full-pilot dimensions."""

    results_path = (
        DEFAULT_PILOT_TABLE_DIR.parent / "pilot_multi_corridor_full_results.csv"
    )
    assert results_path.exists()
    rows = load_pilot_result_rows(results_path)
    metric_rows = build_metric_ci_rows(rows)
    delta_rows = build_paired_delta_ci_rows(rows)

    assert len(rows) == 1890
    assert len(metric_rows) == 819
    assert len(delta_rows) == 702

    print("PASS: shipped full multi-corridor statistics match current dimensions")


def _row(
    policy_id: str,
    mode: str,
    *,
    seed: int,
    completion_rate: float,
    makespan: float,
) -> dict[str, object]:
    return {
        "region_id": "fixture_region",
        "graph_source": "fixture_graph",
        "policy_id": policy_id,
        "scenario_id": "no_disruption",
        "scenario_family": "no_disruption",
        "scenario_type": "none",
        "seed": seed,
        "mode": mode,
        "completion_rate": completion_rate,
        "censored_count": 0,
        "penalized_makespan": makespan,
        "makespan": makespan,
        "road_vehicle_service_minutes": makespan,
        "train_service_minutes": 0.0,
        "total_service_minutes": makespan,
        "passenger_travel_minutes": makespan,
        "passengers_per_total_service_minute": 1.0,
        "first_arrival_time": makespan,
        "median_arrival_time": makespan,
        "p80_arrival_time": makespan,
        "p95_arrival_time": makespan,
    }


if __name__ == "__main__":
    test_metric_ci_rows_group_seed_replications()
    test_paired_delta_rows_compare_against_bus_only_by_seed()
    test_write_statistics_outputs_records_manifest()
    test_shipped_full_pilot_statistics_are_reproducible()
    test_shipped_multi_corridor_statistics_are_reproducible()
    test_shipped_multi_corridor_full_statistics_are_reproducible()
    print("\n=== REALWORLD PILOT STATISTICS TESTS PASSED ===")
