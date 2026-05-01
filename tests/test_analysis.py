"""Unit tests for robust experiment analysis helpers."""

import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.experiment.analysis import compute_ci, find_breakeven, summarize_phase1
from src.experiment.doe import phase1_grid
from src.experiment import runner as runner_module


def assert_close(actual, expected, tolerance=1e-9, label="value"):
    assert abs(actual - expected) <= tolerance, (
        f"{label}: expected {expected}, got {actual}"
    )


def test_compute_ci_uses_finite_values_only():
    """CI stats should ignore inf/NaN while reporting non-finite counts."""
    df = pd.DataFrame({
        "group": ["A", "A", "A", "A", "B", "B", "C"],
        "metric": [10.0, 12.0, np.inf, np.nan, np.inf, np.nan, 7.0],
    })

    ci = compute_ci(df, "metric", ["group"])
    row_a = ci[ci["group"] == "A"].iloc[0]
    row_b = ci[ci["group"] == "B"].iloc[0]
    row_c = ci[ci["group"] == "C"].iloc[0]

    assert row_a["count"] == 2
    assert row_a["finite_count"] == 2
    assert row_a["nonfinite_count"] == 2
    assert_close(row_a["mean"], 11.0, label="A mean")
    assert math.isfinite(row_a["ci_lower"])
    assert math.isfinite(row_a["ci_upper"])

    assert row_b["count"] == 0
    assert row_b["finite_count"] == 0
    assert row_b["nonfinite_count"] == 2
    assert math.isnan(row_b["mean"])
    assert math.isnan(row_b["ci_lower"])
    assert math.isnan(row_b["ci_upper"])

    assert row_c["count"] == 1
    assert row_c["std"] == 0.0
    assert row_c["ci_lower"] == 7.0
    assert row_c["ci_upper"] == 7.0
    print("PASS: compute_ci handles non-finite values")


def test_compute_ci_empty_grouped_result_keeps_schema():
    """Empty CI outputs should still have predictable columns."""
    df = pd.DataFrame({"group": [], "metric": []})

    ci = compute_ci(df, "metric", ["group"])

    expected = {
        "group",
        "mean",
        "std",
        "count",
        "ci_lower",
        "ci_upper",
        "finite_count",
        "nonfinite_count",
    }
    assert expected <= set(ci.columns)
    assert len(ci) == 0
    print("PASS: compute_ci keeps schema for empty grouped results")


def test_compute_ci_accepts_new_resource_kpis():
    """CI helper should work for new unit-explicit resource KPI columns."""
    df = pd.DataFrame({
        "group": ["A", "A", "B"],
        "bus_total_service_minutes": [100.0, 140.0, 0.0],
    })

    ci = compute_ci(df, "bus_total_service_minutes", "group")
    row_a = ci[ci["group"] == "A"].iloc[0]
    row_b = ci[ci["group"] == "B"].iloc[0]

    assert_close(row_a["mean"], 120.0, label="A total service mean")
    assert row_a["count"] == 2
    assert_close(row_b["mean"], 0.0, label="B total service mean")
    assert row_b["count"] == 1
    print("PASS: compute_ci accepts new resource KPIs")


def test_find_breakeven_ignores_nonfinite_deltas():
    """Break-even interpolation should use finite group means only."""
    df = pd.DataFrame({
        "s": [1.0, 1.0, 1.0, 1.0, 1.0, 2.0],
        "p_fail_scale": [0.0, 0.0, 0.2, 0.2, 0.4, 0.0],
        "delta_makespan": [-10.0, np.inf, np.nan, 10.0, 20.0, -1.0],
    })

    assert_close(find_breakeven(df, 1.0), 0.1, label="break-even")
    assert find_breakeven(df, 2.0) is None
    assert find_breakeven(df, 3.0) is None
    print("PASS: find_breakeven ignores non-finite deltas")


def test_find_breakeven_can_use_penalized_metric():
    """Break-even should support censoring-aware delta metrics."""
    df = pd.DataFrame({
        "s": [1.0, 1.0, 1.0],
        "p_fail_scale": [0.0, 0.2, 0.4],
        "delta_makespan": [np.inf, np.inf, np.inf],
        "delta_penalized_makespan": [-10.0, 10.0, 20.0],
    })

    assert_close(
        find_breakeven(df, 1.0),
        0.1,
        label="default penalized break-even",
    )
    assert find_breakeven(df, 1.0, metric="delta_makespan") is None
    assert_close(
        find_breakeven(df, 1.0, metric="delta_penalized_makespan"),
        0.1,
        label="penalized break-even",
    )
    print("PASS: find_breakeven supports selected delta metric")


def test_compute_ci_preserves_experiment_context_columns():
    """CI grouping should not silently mix network or failure semantics."""
    df = pd.DataFrame({
        "s": [1.0, 1.0, 1.0, 1.0],
        "p_fail_scale": [0.0, 0.0, 0.0, 0.0],
        "network_variant": ["baseline", "baseline", "matched", "matched"],
        "failure_mode": ["blocked", "capacity_reduction", "blocked", "blocked"],
        "capacity_reduction_factor": [np.nan, 0.5, np.nan, np.nan],
        "delta_penalized_makespan": [10.0, 20.0, 30.0, 40.0],
    })

    ci = compute_ci(df, "delta_penalized_makespan", ["s", "p_fail_scale"])

    assert {
        "network_variant",
        "failure_mode",
        "capacity_reduction_factor",
    } <= set(ci.columns)
    assert len(ci) == 3
    print("PASS: compute_ci preserves experiment context")


def test_find_breakeven_does_not_mix_context_without_filter():
    """Break-even should require one network/failure context."""
    df = pd.DataFrame({
        "s": [1.0, 1.0, 1.0, 1.0],
        "p_fail_scale": [0.0, 0.2, 0.0, 0.2],
        "network_variant": ["baseline", "baseline", "matched", "matched"],
        "failure_mode": ["blocked", "blocked", "blocked", "blocked"],
        "capacity_reduction_factor": [np.nan, np.nan, np.nan, np.nan],
        "delta_penalized_makespan": [-10.0, 10.0, 50.0, 60.0],
    })

    assert find_breakeven(df, 1.0) is None
    assert_close(
        find_breakeven(df, 1.0, filters={"network_variant": "baseline"}),
        0.1,
        label="filtered break-even",
    )
    print("PASS: find_breakeven avoids context mixing")


def test_summarize_phase1_uses_finite_values_and_optional_kpis():
    """Phase 1 summary should keep legacy columns and include optional KPI means."""
    df = pd.DataFrame({
        "s": [1.0, 1.0],
        "p_fail_scale": [0.0, 0.0],
        "bus_makespan": [100.0, np.inf],
        "multi_makespan": [50.0, 60.0],
        "delta_makespan": [50.0, np.inf],
        "bus_success_rate": [0.5, 1.0],
        "multi_success_rate": [1.0, 1.0],
        "bus_leftover": [2.0, 0.0],
        "multi_leftover": [0.0, 0.0],
        "bus_completion_rate": [0.5, 1.0],
        "multi_completion_rate": [1.0, 1.0],
        "bus_censored_count": [2.0, 0.0],
        "multi_censored_count": [0.0, 0.0],
        "bus_penalized_makespan": [450.0, 100.0],
        "multi_penalized_makespan": [50.0, 60.0],
        "delta_penalized_makespan": [400.0, 40.0],
        "delta_completion_rate": [-0.5, 0.0],
        "bus_success_count": [2.0, 4.0],
        "multi_success_count": [4.0, 4.0],
        "bus_resource_eff": [0.1, 0.2],
        "multi_resource_eff": [0.3, 0.4],
        "bus_lastmile_vehicle_minutes": [0.0, 10.0],
        "multi_lastmile_vehicle_minutes": [20.0, 30.0],
        "bus_road_vehicle_service_minutes": [100.0, 140.0],
        "multi_road_vehicle_service_minutes": [80.0, 90.0],
        "bus_train_service_minutes": [0.0, 0.0],
        "multi_train_service_minutes": [50.0, 60.0],
        "bus_total_service_minutes": [100.0, 140.0],
        "multi_total_service_minutes": [130.0, 150.0],
        "bus_passenger_travel_minutes": [200.0, 240.0],
        "multi_passenger_travel_minutes": [180.0, 210.0],
        "bus_passengers_per_vehicle_minute": [0.02, 0.03],
        "multi_passengers_per_vehicle_minute": [0.04, 0.05],
        "bus_passengers_per_total_service_minute": [0.02, 0.03],
        "multi_passengers_per_total_service_minute": [0.03, 0.04],
        "delta_total_service_minutes": [-30.0, -10.0],
        "delta_passengers_per_total_service_minute": [-0.01, -0.01],
    })

    summary = summarize_phase1(df)
    row = summary.iloc[0]

    assert_close(row["bus_makespan_mean"], 100.0, label="bus makespan mean")
    assert_close(row["multi_makespan_mean"], 55.0, label="multi makespan mean")
    assert_close(row["delta_mean"], 50.0, label="delta mean")
    assert math.isnan(row["delta_std"])
    assert_close(row["bus_sr_mean"], 0.75, label="bus success-rate mean")
    assert_close(row["bus_completion_rate_mean"], 0.75, label="bus completion mean")
    assert_close(row["bus_censored_count_mean"], 1.0, label="bus censored mean")
    assert_close(row["bus_penalized_makespan_mean"], 275.0, label="bus penalty mean")
    assert_close(row["delta_penalized_makespan_mean"], 220.0, label="delta penalty mean")
    assert_close(row["delta_completion_rate_mean"], -0.25, label="delta completion mean")
    assert_close(row["bus_success_count_mean"], 3.0, label="bus success count mean")
    assert_close(row["multi_resource_eff_mean"], 0.35, label="multi resource mean")
    assert_close(
        row["bus_road_vehicle_service_minutes_mean"],
        120.0,
        label="bus road service mean",
    )
    assert_close(
        row["multi_train_service_minutes_mean"],
        55.0,
        label="multi train service mean",
    )
    assert_close(
        row["multi_total_service_minutes_mean"],
        140.0,
        label="multi total service mean",
    )
    assert_close(
        row["bus_passenger_travel_minutes_mean"],
        220.0,
        label="bus passenger travel mean",
    )
    assert_close(
        row["multi_passengers_per_total_service_minute_mean"],
        0.035,
        label="multi passengers per total service mean",
    )
    assert_close(
        row["delta_total_service_minutes_std"],
        math.sqrt(200.0),
        label="delta total service std",
    )
    print("PASS: summarize_phase1 handles finite and optional KPI columns")


def test_summarize_phase1_accepts_old_data_without_new_resource_columns():
    """Old CSV schemas should summarize without requiring new resource columns."""
    df = pd.DataFrame({
        "s": [1.0],
        "p_fail_scale": [0.0],
        "bus_makespan": [100.0],
        "multi_makespan": [80.0],
        "delta_makespan": [20.0],
    })

    summary = summarize_phase1(df)
    row = summary.iloc[0]

    assert_close(row["bus_makespan_mean"], 100.0, label="old bus mean")
    assert "bus_total_service_minutes_mean" not in summary.columns
    print("PASS: summarize_phase1 accepts old data without new resource columns")


def test_summarize_phase1_groups_experiment_context():
    """Phase 1 summary should group by variant and failure semantics when present."""
    df = pd.DataFrame({
        "s": [1.0, 1.0],
        "p_fail_scale": [0.0, 0.0],
        "network_variant": ["baseline", "matched"],
        "failure_mode": ["blocked", "blocked"],
        "capacity_reduction_factor": [np.nan, np.nan],
        "bus_makespan": [100.0, 120.0],
        "multi_makespan": [80.0, 90.0],
        "delta_penalized_makespan": [20.0, 30.0],
    })

    summary = summarize_phase1(df)

    assert len(summary) == 2
    assert {"network_variant", "failure_mode"} <= set(summary.columns)
    assert set(summary["network_variant"]) == {"baseline", "matched"}
    print("PASS: summarize_phase1 groups experiment context")


def test_phase1_grid_and_runner_include_sensitivity_metadata():
    """DOE and runner rows should expose variant and failure semantics."""
    config = make_runner_metadata_config()
    grid = phase1_grid(config)

    assert len(grid) == 6
    blocked_points = [point for point in grid if point.failure_mode == "blocked"]
    degraded_points = [
        point for point in grid if point.failure_mode == "capacity_reduction"
    ]
    assert len(blocked_points) == 2
    assert all(point.capacity_reduction_factor is None for point in blocked_points)
    assert {point.capacity_reduction_factor for point in degraded_points} == {0.25, 0.5}

    original_run_scenario = runner_module.run_scenario

    def fake_run_scenario(G, config, scenario_type, policy, params, seed):
        assert G.graph["network_variant"] == config["network"]["variant"]
        assert config["failure"]["mode"] in {"blocked", "capacity_reduction"}
        if config["failure"]["mode"] == "capacity_reduction":
            assert config["failure"]["capacity_reduction_factor"] in {0.25, 0.5}
        base = 100.0 if scenario_type == "bus_only" else 90.0
        return {
            "makespan": base,
            "penalized_makespan": base,
            "success_rate": 1.0,
            "completion_rate": 1.0,
            "resource_efficiency": 1.0,
            "success_count": config["personnel"]["total"],
            "leftover_count": 0,
            "censored_count": 0,
            "total_personnel": config["personnel"]["total"],
        }

    runner_module.run_scenario = fake_run_scenario
    try:
        df = runner_module.run_phase1(config, verbose=False)
        df2 = runner_module.run_phase2(config, verbose=False)
    finally:
        runner_module.run_scenario = original_run_scenario

    assert len(df) == 6
    assert {
        "network_variant",
        "failure_mode",
        "capacity_reduction_factor",
    } <= set(df.columns)
    assert set(df["network_variant"]) == {"baseline", "matched_redundancy"}
    assert set(df["failure_mode"]) == {"blocked", "capacity_reduction"}
    assert df[df["failure_mode"] == "blocked"]["capacity_reduction_factor"].isna().all()
    assert_close(df["delta_penalized_makespan"].iloc[0], 10.0, label="runner delta")
    assert len(df2) == 1
    assert df2.iloc[0]["network_variant"] == "baseline"
    assert df2.iloc[0]["failure_mode"] == "blocked"
    assert pd.isna(df2.iloc[0]["capacity_reduction_factor"])
    print("PASS: DOE and runner include sensitivity metadata")


def make_runner_metadata_config():
    """Small config for runner metadata tests."""
    return {
        "network": {
            "nodes": ["H", "A", "S", "R", "D"],
            "variant": "baseline",
            "variant_levels": ["baseline", "matched_redundancy"],
            "road_links": [
                ["A", "D", 10.0, 1000.0, 0.0],
                ["A", "S", 5.0, 1000.0, 0.0],
                ["R", "D", 5.0, 1000.0, 0.0],
            ],
            "rail_link": [["S", "R", 20.0, 10.0, 100]],
            "variants": {
                "baseline": {},
                "matched_redundancy": {
                    "road_links": [
                        ["A", "D", 10.0, 1000.0, 0.0],
                        ["A", "X", 6.0, 1000.0, 0.0],
                        ["X", "D", 6.0, 1000.0, 0.0],
                        ["A", "S", 5.0, 1000.0, 0.0],
                        ["R", "D", 5.0, 1000.0, 0.0],
                        ["R", "Y", 3.0, 1000.0, 0.0],
                        ["Y", "D", 3.0, 1000.0, 0.0],
                    ],
                },
            },
        },
        "personnel": {
            "total": 2,
            "group_size": 2,
            "assembly_time": 0.0,
        },
        "bus": {
            "dispatch_interval_min": 5.0,
            "fleet_size": 1,
            "turnaround_min": 0.0,
        },
        "multimodal": {
            "shuttle_dispatch_interval_min": 5.0,
            "shuttle_fleet_size": 1,
            "transfer_time_min": 0.0,
            "transfer_per_passenger_min": 0.0,
            "lastmile_dispatch_interval_min": 5.0,
        },
        "traffic": {
            "volume_window_min": 60.0,
            "background_volume": 0.0,
        },
        "failure": {
            "mode": "blocked",
            "capacity_reduction_factor": 0.5,
            "mode_levels": ["blocked", "capacity_reduction"],
            "capacity_reduction_factor_levels": [0.25, 0.5],
        },
        "metrics": {
            "late_penalty_min": 100.0,
        },
        "bpr": {
            "alpha": 0.0,
            "beta": 4.0,
        },
        "congestion_scale": {
            "levels": [1.0],
        },
        "failure_rate": {
            "parameter": "p_fail_scale",
            "semantics": "multiplier",
            "levels": [0.0],
        },
        "lateness": {
            "distribution": "lognormal",
            "mu": 0.0,
            "sigma_levels": [0.0],
        },
        "policies": {
            "STRICT": {"type": "strict"},
        },
        "experiment": {
            "R": 1,
            "seed_base": 1,
            "time_limit": 100.0,
        },
    }


TESTS = [
    test_compute_ci_uses_finite_values_only,
    test_compute_ci_empty_grouped_result_keeps_schema,
    test_compute_ci_accepts_new_resource_kpis,
    test_find_breakeven_ignores_nonfinite_deltas,
    test_find_breakeven_can_use_penalized_metric,
    test_compute_ci_preserves_experiment_context_columns,
    test_find_breakeven_does_not_mix_context_without_filter,
    test_summarize_phase1_uses_finite_values_and_optional_kpis,
    test_summarize_phase1_accepts_old_data_without_new_resource_columns,
    test_summarize_phase1_groups_experiment_context,
    test_phase1_grid_and_runner_include_sensitivity_metadata,
]


if __name__ == "__main__":
    for test in TESTS:
        test()
    print("\n=== ALL ANALYSIS TESTS PASSED ===")
