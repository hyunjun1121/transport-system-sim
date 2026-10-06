"""Tests for paired and nested uncertainty summaries used by paper revision."""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.revision_statistics import (
    crossed_two_way_bootstrap_ci,
    estimate_piecewise_linear_zero_crossing,
    hierarchical_bootstrap_ci,
    joint_seed_zero_crossing_bootstrap,
    pair_finite_outcomes,
    percentile_bootstrap_ci,
    replicate_count_convergence,
    t_paired_confidence_interval,
)


def assert_close(actual, expected, tolerance=1e-7, label="value"):
    assert abs(actual - expected) <= tolerance, (
        f"{label}: expected {expected}, got {actual}"
    )


def test_pairing_keeps_only_finite_seed_matches_and_reports_every_exclusion():
    left = {1: 10.0, 2: math.inf, 3: 30.0, 4: 40.0}
    right = {1: 12.0, 2: 20.0, 3: math.nan, 5: 50.0}

    result = pair_finite_outcomes(left, right)

    assert result.matched_seeds == (1,)
    assert result.differences == (-2.0,)
    assert [(item.seed, item.reason) for item in result.incomplete] == [
        (2, "nonfinite_left"),
        (3, "nonfinite_right"),
        (4, "missing_right"),
        (5, "missing_left"),
    ]
    assert result.total_seed_count == 5
    print("PASS: finite seed pairing reports incomplete outcomes")


def test_paired_t_interval_uses_student_t_not_independent_means():
    result = t_paired_confidence_interval([1.0, 2.0, 3.0, 4.0, 5.0])

    assert result.n == 5
    assert_close(result.estimate, 3.0, label="paired mean")
    assert_close(result.critical_value, 2.776445105, tolerance=2e-6, label="t critical")
    assert_close(result.lower, 1.03675684, tolerance=2e-6, label="lower CI")
    assert_close(result.upper, 4.96324316, tolerance=2e-6, label="upper CI")

    exact = t_paired_confidence_interval([7.0, 7.0, 7.0])
    assert exact.lower == exact.estimate == exact.upper == 7.0
    print("PASS: paired t interval uses Student-t critical value")


def test_percentile_bootstrap_is_seeded_and_deterministic():
    first = percentile_bootstrap_ci(
        [1.0, 2.0, 4.0, 8.0], replicates=400, seed=20260721
    )
    second = percentile_bootstrap_ci(
        [1.0, 2.0, 4.0, 8.0], replicates=400, seed=20260721
    )

    assert first == second
    assert first.replicates == 400
    assert first.seed == 20260721
    assert first.lower <= first.estimate <= first.upper
    assert_close(first.estimate, 3.75, label="bootstrap point estimate")
    print("PASS: percentile bootstrap is deterministic")


def test_bootstrap_replicates_rejects_float_values_even_when_integral():
    for replicates in (2.0, 2.5, True, 0, -1):
        try:
            percentile_bootstrap_ci([1.0, 2.0], replicates=replicates)
        except ValueError as error:
            assert "positive integer" in str(error)
        else:
            raise AssertionError(f"replicates={replicates!r} must be rejected")
    print("PASS: bootstrap replicate count requires integer type")


def test_replicate_count_diagnostics_use_prefixes_and_report_stability():
    points = replicate_count_convergence(
        [2.0, 2.0, 2.0, 2.0, 2.0], counts=[2, 3, 5]
    )

    assert [point.count for point in points] == [2, 3, 5]
    assert all(point.estimate == 2.0 for point in points)
    assert all(point.half_width == 0.0 for point in points)
    assert points[0].estimate_change_from_previous is None
    assert points[1].estimate_change_from_previous == 0.0
    print("PASS: replicate-count convergence uses deterministic prefixes")


def test_zero_crossing_requires_an_observed_bracket():
    bracketed = estimate_piecewise_linear_zero_crossing(
        [(1.0, -4.0), (2.0, -2.0), (4.0, 2.0)]
    )
    assert bracketed.status == "bracketed"
    assert_close(bracketed.crossing, 3.0, label="zero crossing")
    assert (bracketed.lower_x, bracketed.upper_x) == (2.0, 4.0)

    exact = estimate_piecewise_linear_zero_crossing(
        [(1.0, -1.0), (2.0, 0.0), (3.0, 1.0)]
    )
    assert exact.status == "exact"
    assert exact.crossing == 2.0

    absent = estimate_piecewise_linear_zero_crossing(
        [(1.0, 2.0), (2.0, 3.0)]
    )
    assert absent.status == "unbracketed"
    assert absent.crossing is None
    print("PASS: zero crossing never extrapolates beyond evidence")


def test_hierarchical_bootstrap_resamples_threat_then_arrival_and_reports_exclusions():
    outcomes = {
        "threat-a": {101: 1.0, 102: 3.0, 103: math.nan},
        "threat-b": {101: 5.0, 102: 7.0},
        "threat-empty": {101: math.inf},
    }

    first = hierarchical_bootstrap_ci(
        outcomes, replicates=500, seed=20260721
    )
    second = hierarchical_bootstrap_ci(
        outcomes, replicates=500, seed=20260721
    )

    assert first == second
    assert_close(first.estimate, 4.0, label="equal-threat point estimate")
    assert first.threat_draw_count == 2
    assert first.finite_observation_count == 4
    assert first.empty_threat_draws == ("threat-empty",)
    assert [(item.threat_draw, item.arrival_seed) for item in first.excluded] == [
        ("threat-a", 103),
        ("threat-empty", 101),
    ]
    assert first.lower <= first.estimate <= first.upper
    print("PASS: hierarchical bootstrap separates both uncertainty levels")


def test_joint_seed_break_even_bootstrap_preserves_crn_trajectories():
    outcomes = {
        3101: {1.0: -12.0, 2.0: 8.0},
        3102: {1.0: -8.0, 2.0: 12.0},
        3103: {1.0: -9.0},
    }

    first = joint_seed_zero_crossing_bootstrap(
        outcomes, replicates=400, seed=20260721
    )
    second = joint_seed_zero_crossing_bootstrap(
        outcomes, replicates=400, seed=20260721
    )

    assert first == second
    assert_close(first.estimate, 1.5, label="joint-seed crossing")
    assert first.complete_seed_count == 2
    assert first.excluded_seeds == (3103,)
    assert first.successful_replicates == 400
    assert first.lower <= first.estimate <= first.upper
    print("PASS: break-even bootstrap resamples complete CRN seed trajectories")


def test_crossed_bootstrap_matches_nested_point_estimate_and_is_deterministic():
    outcomes = {
        "threat-a": {101: 1.0, 102: 3.0, 103: math.nan},
        "threat-b": {101: 5.0, 102: 7.0},
        "threat-empty": {101: math.inf},
    }

    first = crossed_two_way_bootstrap_ci(
        outcomes, replicates=500, seed=20260721
    )
    second = crossed_two_way_bootstrap_ci(
        outcomes, replicates=500, seed=20260721
    )
    nested = hierarchical_bootstrap_ci(
        outcomes, replicates=500, seed=20260721
    )

    assert first == second
    assert_close(first.estimate, nested.estimate, label="shared point estimate")
    assert_close(first.estimate, 4.0, label="equal-threat point estimate")
    assert first.threat_draw_count == 2
    assert first.finite_observation_count == 4
    assert first.empty_threat_draws == ("threat-empty",)
    assert first.failed_replicates == 0
    assert [(item.threat_draw, item.arrival_seed) for item in first.excluded] == [
        ("threat-a", 103),
        ("threat-empty", 101),
    ]
    assert first.lower <= first.estimate <= first.upper
    print("PASS: crossed bootstrap is deterministic with shared point estimate")


def test_crossed_bootstrap_preserves_shared_seed_effects():
    # Every threat repeats the same arrival-seed pattern, so seed resampling
    # must move jointly across threats; independent within-threat resampling
    # understates the seed-effect variance.
    outcomes = {
        f"threat-{index}": {201: 0.0, 202: 10.0, 203: 20.0}
        for index in range(6)
    }

    crossed = crossed_two_way_bootstrap_ci(
        outcomes, replicates=2000, seed=20260721
    )
    nested = hierarchical_bootstrap_ci(
        outcomes, replicates=2000, seed=20260721
    )

    assert_close(crossed.estimate, 10.0, label="crossed point estimate")
    crossed_width = crossed.upper - crossed.lower
    nested_width = nested.upper - nested.lower
    assert crossed_width >= nested_width, (
        f"crossed width {crossed_width} must cover shared seed effects "
        f"at least as well as nested width {nested_width}"
    )
    print("PASS: crossed bootstrap preserves cross-threat seed dependence")


def test_crossed_bootstrap_rejects_empty_and_fully_nonfinite_input():
    for bad in ({}, {"threat-a": {101: math.inf}}):
        try:
            crossed_two_way_bootstrap_ci(bad, replicates=50)
        except ValueError:
            pass
        else:
            raise AssertionError(f"input {bad!r} must be rejected")
    print("PASS: crossed bootstrap rejects degenerate inputs")


TESTS = [
    test_pairing_keeps_only_finite_seed_matches_and_reports_every_exclusion,
    test_paired_t_interval_uses_student_t_not_independent_means,
    test_percentile_bootstrap_is_seeded_and_deterministic,
    test_bootstrap_replicates_rejects_float_values_even_when_integral,
    test_replicate_count_diagnostics_use_prefixes_and_report_stability,
    test_zero_crossing_requires_an_observed_bracket,
    test_hierarchical_bootstrap_resamples_threat_then_arrival_and_reports_exclusions,
    test_crossed_bootstrap_matches_nested_point_estimate_and_is_deterministic,
    test_crossed_bootstrap_preserves_shared_seed_effects,
    test_crossed_bootstrap_rejects_empty_and_fully_nonfinite_input,
    test_joint_seed_break_even_bootstrap_preserves_crn_trajectories,
]


if __name__ == "__main__":
    for test in TESTS:
        test()
    print("\n=== ALL REVISION STATISTICS TESTS PASSED ===")
