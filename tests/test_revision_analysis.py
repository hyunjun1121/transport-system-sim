"""Tests for row-level revision experiment postprocessing."""

from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.revision_analysis import (
    break_even_from_rows,
    compare_outcomes,
    graph_scope_stability_table,
    hierarchical_paired_delta_summaries,
    pair_policy_rows,
    paired_replicate_convergence,
    summarize_paired_makespan,
)


def _row(
    policy_id,
    arrival_seed,
    completion_rate,
    makespan,
    **configuration,
):
    return {
        **configuration,
        "policy_id": policy_id,
        "arrival_seed": arrival_seed,
        "completion_rate": completion_rate,
        "makespan": makespan,
    }


def _configuration(summary):
    return dict(summary.configuration)


def test_policy_pairing_uses_configuration_fields_and_lexicographic_outcomes():
    rows = [
        _row("bus_only", 1, 1.0, 100.0, scenario_id="normal"),
        _row("static_multimodal", 1, 1.0, 120.0, scenario_id="normal"),
        _row("bus_only", 2, 0.5, 50.0, scenario_id="normal"),
        _row("static_multimodal", 2, 1.0, 500.0, scenario_id="normal"),
        _row("bus_only", 3, 1.0, math.inf, scenario_id="normal"),
    ]

    pairs = pair_policy_rows(rows)

    assert len(pairs) == 3
    assert dict(pairs[0].configuration) == {
        "arrival_seed": 1,
        "scenario_id": "normal",
    }
    assert pairs[0].comparison.winner == "left"
    assert pairs[0].comparison.reason == "makespan"
    assert pairs[1].comparison.winner == "right"
    assert pairs[1].comparison.reason == "completion_rate"
    assert pairs[2].right is None
    assert pairs[2].comparison is None

    assert compare_outcomes(0.9, 1.0, 1.0, 999.0).winner == "right"
    assert compare_outcomes(1.0, 9.0, 1.0, 10.0).winner == "left"
    assert compare_outcomes(1.0, math.inf, 1.0, 10.0).winner == "right"
    assert compare_outcomes(0.0, math.inf, 0.0, math.inf).winner == "tie"
    print("PASS: configuration pairing and lexicographic comparison")


def test_paired_summary_reports_finite_delta_intervals_and_incomplete_reasons():
    rows = [
        _row("bus_only", 1, 1.0, 90.0, scenario_id="normal"),
        _row("static_multimodal", 1, 1.0, 100.0, scenario_id="normal"),
        _row("bus_only", 2, 1.0, 100.0, scenario_id="normal"),
        _row("static_multimodal", 2, 1.0, 120.0, scenario_id="normal"),
        _row("bus_only", 3, 0.5, math.inf, scenario_id="normal"),
        _row("static_multimodal", 3, 1.0, 200.0, scenario_id="normal"),
        _row("bus_only", 4, 1.0, 100.0, scenario_id="normal"),
    ]

    first = summarize_paired_makespan(rows, bootstrap_replicates=300, bootstrap_seed=17)
    second = summarize_paired_makespan(rows, bootstrap_replicates=300, bootstrap_seed=17)

    assert first == second
    assert len(first) == 1
    summary = first[0]
    assert _configuration(summary) == {"scenario_id": "normal"}
    assert summary.total_pair_count == 4
    assert summary.finite_pair_count == 2
    assert summary.mean_left_makespan == 95.0
    assert summary.mean_right_makespan == 110.0
    assert summary.mean_delta == -15.0
    assert summary.mean_left_completion_rate == 5.0 / 6.0
    assert summary.mean_right_completion_rate == 1.0
    assert abs(summary.mean_completion_rate_delta + 1.0 / 6.0) < 1e-12
    assert summary.completion_winner == "right"
    assert summary.completion_t_interval is not None
    assert summary.completion_bootstrap_interval is not None
    assert abs(
        summary.completion_t_interval.estimate
        - summary.mean_completion_rate_delta
    ) < 1e-12
    assert summary.completion_statistical_resolution == "not_resolved"
    assert summary.overall_winner == "right"
    assert summary.overall_winner_basis == "completion_rate"
    assert summary.t_interval is not None
    assert summary.bootstrap_interval is not None
    assert dict(summary.incomplete_reason_counts) == {
        "completion_rate_mismatch": 1,
        "missing_right": 1,
    }
    print("PASS: paired intervals preserve incomplete outcomes")


def test_paired_summary_omits_policy_means_without_finite_paired_makespan():
    rows = [
        _row("bus_only", 1, 1.0, math.inf, scenario_id="blocked"),
        _row("static_multimodal", 1, 1.0, 120.0, scenario_id="blocked"),
        _row("bus_only", 2, 0.5, 100.0, scenario_id="blocked"),
        _row("static_multimodal", 2, 1.0, 120.0, scenario_id="blocked"),
    ]

    summaries = summarize_paired_makespan(
        rows, bootstrap_replicates=20, bootstrap_seed=17
    )

    assert len(summaries) == 1
    summary = summaries[0]
    assert summary.finite_pair_count == 0
    assert summary.mean_left_makespan is None
    assert summary.mean_right_makespan is None
    assert summary.mean_delta is None
    assert dict(summary.incomplete_reason_counts) == {
        "completion_rate_mismatch": 1,
        "nonfinite_left": 1,
    }
    print("PASS: paired policy means require finite equal-completion pairs")


def test_break_even_uses_per_multiplier_paired_means_and_never_extrapolates():
    rows = []
    for multiplier, deltas in ((1.0, (-12.0, -8.0)), (2.0, (8.0, 12.0))):
        for seed, delta in enumerate(deltas, start=1):
            rows.extend(
                [
                    _row(
                        "bus_only",
                        seed,
                        1.0,
                        100.0 + delta,
                        scenario_id="long_haul",
                        road_multiplier=multiplier,
                    ),
                    _row(
                        "static_multimodal",
                        seed,
                        1.0,
                        100.0,
                        scenario_id="long_haul",
                        road_multiplier=multiplier,
                    ),
                ]
            )

    series = break_even_from_rows(
        rows,
        multiplier_field="road_multiplier",
        bootstrap_replicates=100,
    )

    assert len(series) == 1
    assert series[0].paired_mean_points == ((1.0, -10.0), (2.0, 10.0))
    assert series[0].crossing.status == "bracketed"
    assert series[0].crossing.crossing == 1.5
    assert series[0].joint_seed_bootstrap is not None
    assert series[0].joint_seed_bootstrap.complete_seed_count == 2

    unbracketed_rows = [row for row in rows if row["road_multiplier"] == 1.0]
    absent = break_even_from_rows(
        unbracketed_rows,
        multiplier_field="road_multiplier",
        bootstrap_replicates=100,
    )
    assert absent[0].crossing.status == "insufficient_points"
    assert absent[0].crossing.crossing is None
    print("PASS: break-even uses observed paired-mean bracket")


def test_break_even_point_and_joint_ci_use_same_complete_seed_curves():
    rows = []

    def add(seed, multiplier, delta):
        rows.extend(
            [
                _row(
                    "bus_only",
                    seed,
                    1.0,
                    100.0 + delta,
                    scenario_id="long_haul",
                    road_multiplier=multiplier,
                ),
                _row(
                    "static_multimodal",
                    seed,
                    1.0,
                    100.0,
                    scenario_id="long_haul",
                    road_multiplier=multiplier,
                ),
            ]
        )

    add(1, 1.0, -10.0)
    add(2, 1.0, -100.0)
    add(1, 2.0, 10.0)

    result = break_even_from_rows(
        rows,
        multiplier_field="road_multiplier",
        bootstrap_replicates=20,
    )[0]

    assert result.paired_mean_points == ((1.0, -10.0), (2.0, 10.0))
    assert result.joint_seed_bootstrap is not None
    assert result.crossing.crossing == result.joint_seed_bootstrap.estimate == 1.5
    assert result.joint_seed_bootstrap.excluded_seeds == (2,)
    print("PASS: break-even point and interval share complete seed curves")


def test_paired_replicate_convergence_reports_seed_prefixes():
    rows = []
    for seed, delta in enumerate((-4.0, -2.0, 0.0, 2.0, 4.0), start=1):
        rows.extend(
            [
                _row("bus_only", seed, 1.0, 100.0 + delta, scenario_id="normal"),
                _row("static_multimodal", seed, 1.0, 100.0, scenario_id="normal"),
            ]
        )

    diagnostics = paired_replicate_convergence(rows, counts=(2, 3, 5))

    assert [item.count for item in diagnostics] == [2, 3, 5]
    assert [item.seed_max for item in diagnostics] == [2, 3, 5]
    assert diagnostics[-1].estimate == 0.0
    print("PASS: paired convergence reports deterministic CRN seed prefixes")


def test_paired_replicate_convergence_orders_numeric_seeds_numerically():
    rows = []
    for seed, delta in ((1, 1.0), (2, 2.0), (10, 10.0)):
        rows.extend(
            [
                _row("bus_only", seed, 1.0, 100.0 + delta, scenario_id="normal"),
                _row("static_multimodal", seed, 1.0, 100.0, scenario_id="normal"),
            ]
        )

    diagnostics = paired_replicate_convergence(rows, counts=(2, 3))

    assert [item.seed_max for item in diagnostics] == [2, 10]
    assert [item.estimate for item in diagnostics] == [1.5, 13.0 / 3.0]
    print("PASS: paired convergence orders numeric seeds numerically")


def test_hierarchical_summary_resamples_threat_draws_outside_arrival_seeds():
    rows = []
    for threat_draw, deltas in (("a", (1.0, 3.0)), ("b", (5.0, 7.0))):
        for seed, delta in enumerate(deltas, start=1):
            rows.extend(
                [
                    _row(
                        "bus_only",
                        seed,
                        1.0,
                        100.0 + delta,
                        scenario_id="random",
                        threat_draw=threat_draw,
                    ),
                    _row(
                        "static_multimodal",
                        seed,
                        1.0,
                        100.0,
                        scenario_id="random",
                        threat_draw=threat_draw,
                    ),
                ]
            )
    rows.append(
        _row(
            "bus_only",
            3,
            1.0,
            110.0,
            scenario_id="random",
            threat_draw="b",
        )
    )

    first = hierarchical_paired_delta_summaries(
        rows, bootstrap_replicates=400, bootstrap_seed=23
    )
    second = hierarchical_paired_delta_summaries(
        rows, bootstrap_replicates=400, bootstrap_seed=23
    )

    assert first == second
    assert len(first) == 1
    summary = first[0]
    assert summary.interval is not None
    assert summary.interval.estimate == 4.0
    assert summary.total_pair_count == 5
    assert summary.finite_pair_count == 4
    assert dict(summary.incomplete_reason_counts) == {"missing_right": 1}
    print("PASS: hierarchical paired-delta uncertainty is deterministic")


def test_hierarchical_summary_infers_completion_and_result_frequency_proxies():
    rows = []
    completions = {
        "a": ((0.5, 1.0), (0.0, 1.0)),
        "b": ((1.0, 0.5), (1.0, 0.0)),
    }
    for threat_draw, pairs in completions.items():
        for seed, (bus_completion, multimodal_completion) in enumerate(
            pairs, start=1
        ):
            rows.extend(
                [
                    _row(
                        "bus_only",
                        seed,
                        bus_completion,
                        math.inf,
                        scenario_id="random",
                        threat_draw=threat_draw,
                    ),
                    _row(
                        "static_multimodal",
                        seed,
                        multimodal_completion,
                        math.inf,
                        scenario_id="random",
                        threat_draw=threat_draw,
                    ),
                ]
            )

    summary = hierarchical_paired_delta_summaries(
        rows, bootstrap_replicates=400, bootstrap_seed=29
    )[0]

    assert summary.interval is None
    assert summary.completion_pair_count == 4
    assert summary.completion_delta_interval is not None
    assert summary.completion_delta_interval.estimate == 0.0
    assert summary.completion_delta_interval.threat_draw_count == 2
    assert summary.completion_delta_interval.finite_observation_count == 4
    assert summary.completion_delta_interval.empty_threat_draws == ()
    assert summary.left_positive_completion_proxy_interval is not None
    assert summary.right_positive_completion_proxy_interval is not None
    assert summary.left_positive_completion_proxy_interval.estimate == 0.75
    assert summary.right_positive_completion_proxy_interval.estimate == 0.75
    assert summary.left_full_completion_proxy_interval is not None
    assert summary.right_full_completion_proxy_interval is not None
    assert summary.left_full_completion_proxy_interval.estimate == 0.5
    assert summary.right_full_completion_proxy_interval.estimate == 0.5
    assert {
        interval.finite_observation_count
        for interval in (
            summary.left_positive_completion_proxy_interval,
            summary.right_positive_completion_proxy_interval,
            summary.left_full_completion_proxy_interval,
            summary.right_full_completion_proxy_interval,
        )
        if interval is not None
    } == {4}
    assert summary.probability_proxy_scope == (
        "empirical_result_frequency_among_paired_valid_simulation_results_across_"
        "simulated_threat_draws_and_arrival_seeds_not_event_probability"
    )
    print("PASS: random-threat completion and result-frequency proxies are nested")


def test_graph_scope_stability_compares_time_connectivity_and_policy_ranking():
    rows = []
    for graph_scope, path_count, values in (
        (
            "full",
            None,
            {
                "normal": ((1.0, 100.0), (1.0, 120.0)),
                "stress": ((1.0, 90.0), (1.0, 100.0)),
            },
        ),
        (
            "top3",
            3,
            {
                "normal": ((1.0, 105.0), (1.0, 119.0)),
                "stress": ((1.0, 110.0), (1.0, 100.0)),
            },
        ),
    ):
        for scenario_id, (bus, multimodal) in values.items():
            rows.extend(
                [
                    _row(
                        "bus_only",
                        1,
                        bus[0],
                        bus[1],
                        graph_scope=graph_scope,
                        corridor_path_count=path_count,
                        scenario_id=scenario_id,
                    ),
                    _row(
                        "static_multimodal",
                        1,
                        multimodal[0],
                        multimodal[1],
                        graph_scope=graph_scope,
                        corridor_path_count=path_count,
                        scenario_id=scenario_id,
                    ),
                ]
            )

    table = graph_scope_stability_table(
        rows,
        full_scope="full",
        normal_scenario_value="normal",
    )

    assert {row.graph_scope for row in table} == {"top3", "full"}
    top3 = next(row for row in table if row.graph_scope == "top3")
    assert top3.graph_scope == "top3"
    assert top3.normal_time_match_count == 2
    assert top3.normal_time_mean_absolute_error == 3.0
    assert top3.connectivity_match_count == 4
    assert top3.connectivity_agreement == 1.0
    assert top3.policy_ranking_match_count == 2
    assert top3.policy_ranking_agreement == 0.5
    full = next(row for row in table if row.graph_scope == "full")
    assert full.normal_time_match_count == 2
    assert full.normal_time_mean_absolute_error == 0.0
    assert full.normal_time_mean_absolute_percentage_error == 0.0
    assert full.connectivity_match_count == 4
    assert full.connectivity_agreement == 1.0
    assert full.policy_ranking_match_count == 2
    assert full.policy_ranking_agreement == 1.0
    print("PASS: graph-scope stability table compares all three criteria")


TESTS = [
    test_policy_pairing_uses_configuration_fields_and_lexicographic_outcomes,
    test_paired_summary_reports_finite_delta_intervals_and_incomplete_reasons,
    test_paired_summary_omits_policy_means_without_finite_paired_makespan,
    test_break_even_uses_per_multiplier_paired_means_and_never_extrapolates,
    test_break_even_point_and_joint_ci_use_same_complete_seed_curves,
    test_paired_replicate_convergence_reports_seed_prefixes,
    test_paired_replicate_convergence_orders_numeric_seeds_numerically,
    test_hierarchical_summary_resamples_threat_draws_outside_arrival_seeds,
    test_hierarchical_summary_infers_completion_and_result_frequency_proxies,
    test_graph_scope_stability_compares_time_connectivity_and_policy_ranking,
]


if __name__ == "__main__":
    for test in TESTS:
        test()
    print("\n=== ALL REVISION ANALYSIS TESTS PASSED ===")
