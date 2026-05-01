"""Unit tests for censoring-safe metric KPIs."""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.metrics import MetricsCollector


def assert_close(actual, expected, tolerance=1e-9, label="value"):
    assert abs(actual - expected) <= tolerance, (
        f"{label}: expected {expected}, got {actual}"
    )


def test_complete_run_keeps_legacy_makespan():
    """A complete run should keep penalized makespan equal to makespan."""
    metrics = MetricsCollector(total_personnel=2, time_limit=100.0, late_penalty_min=50.0)
    metrics.record_arrival(0, 20.0)
    metrics.record_arrival(1, 30.0)

    assert metrics.makespan == 30.0
    assert metrics.success_count == 2
    assert metrics.censored_count == 0
    assert_close(metrics.completion_rate, 1.0, label="completion rate")
    assert metrics.penalized_makespan == metrics.makespan

    result = metrics.as_dict()
    assert result["makespan"] == 30.0
    assert result["success_rate"] == 1.0
    assert result["censored_count"] == 0
    assert result["completion_rate"] == 1.0
    assert result["penalized_makespan"] == 30.0
    print("PASS: complete run keeps legacy makespan")


def test_complete_run_reports_unit_consistent_resources():
    """Service-minute KPIs should not mix in ambiguous legacy fields."""
    metrics = MetricsCollector(total_personnel=2, time_limit=100.0)
    metrics.record_arrival(0, 20.0)
    metrics.record_arrival(1, 30.0)
    metrics.bus_minutes = 30.0
    metrics.train_minutes = 10.0
    metrics.lastmile_vehicle_minutes = 5.0
    metrics.lastmile_minutes = 80.0
    metrics.passenger_travel_minutes = 120.0

    assert_close(
        metrics.road_vehicle_service_minutes,
        35.0,
        label="road vehicle service minutes",
    )
    assert_close(metrics.train_service_minutes, 10.0, label="train service minutes")
    assert_close(metrics.total_service_minutes, 45.0, label="total service minutes")
    assert_close(
        metrics.passengers_per_vehicle_minute,
        2.0 / 35.0,
        label="passengers per road vehicle minute",
    )
    assert_close(
        metrics.passengers_per_total_service_minute,
        2.0 / 45.0,
        label="passengers per total service minute",
    )
    assert_close(
        metrics.resource_efficiency,
        metrics.passengers_per_total_service_minute,
        label="resource efficiency alias",
    )

    result = metrics.as_dict()
    assert result["lastmile_minutes"] == 80.0
    assert result["lastmile_vehicle_minutes"] == 5.0
    assert result["road_vehicle_service_minutes"] == 35.0
    assert result["train_service_minutes"] == 10.0
    assert result["total_service_minutes"] == 45.0
    assert result["passenger_travel_minutes"] == 120.0
    assert_close(
        result["passengers_per_vehicle_minute"],
        round(2.0 / 35.0, 4),
        label="dict passengers per vehicle minute",
    )
    assert_close(
        result["passengers_per_total_service_minute"],
        round(2.0 / 45.0, 4),
        label="dict passengers per total service minute",
    )
    assert_close(
        result["resource_efficiency"],
        round(2.0 / 45.0, 4),
        label="dict resource efficiency",
    )
    print("PASS: complete run reports unit-consistent resources")


def test_partial_run_adds_censoring_penalty():
    """Undelivered personnel should raise the penalized makespan."""
    metrics = MetricsCollector(total_personnel=4, time_limit=150.0, late_penalty_min=150.0)
    metrics.record_arrival(0, 100.0)
    metrics.record_arrival(1, 100.0)

    assert metrics.makespan == 100.0
    assert metrics.success_count == 2
    assert metrics.censored_count == 2
    assert_close(metrics.completion_rate, 0.5, label="completion rate")
    assert metrics.penalized_makespan == 450.0

    result = metrics.as_dict()
    assert result["censored_count"] == 2
    assert result["completion_rate"] == 0.5
    assert result["penalized_makespan"] == 450.0
    print("PASS: partial run adds censoring penalty")


def test_no_arrivals_gets_finite_penalized_makespan():
    """A fully censored run should keep legacy inf but expose a finite penalty KPI."""
    metrics = MetricsCollector(total_personnel=3, time_limit=60.0, late_penalty_min=10.0)

    assert math.isinf(metrics.makespan)
    assert metrics.success_count == 0
    assert metrics.censored_count == 3
    assert_close(metrics.completion_rate, 0.0, label="completion rate")
    assert metrics.penalized_makespan == 90.0
    print("PASS: no-arrival run exposes finite penalized makespan")


def test_zero_resource_rates_are_zero():
    """Delivered passengers with no recorded service time should not divide by zero."""
    metrics = MetricsCollector(total_personnel=2, time_limit=100.0)
    metrics.record_arrival(0, 20.0)
    metrics.record_arrival(1, 25.0)

    assert metrics.road_vehicle_service_minutes == 0.0
    assert metrics.total_service_minutes == 0.0
    assert metrics.passengers_per_vehicle_minute == 0.0
    assert metrics.passengers_per_total_service_minute == 0.0
    assert metrics.resource_efficiency == 0.0

    result = metrics.as_dict()
    assert result["passengers_per_vehicle_minute"] == 0.0
    assert result["passengers_per_total_service_minute"] == 0.0
    assert result["resource_efficiency"] == 0.0
    print("PASS: zero-resource rates are zero")


def test_late_arrivals_are_censored():
    """Arrivals after the time limit should count against completion."""
    metrics = MetricsCollector(total_personnel=2, time_limit=60.0, late_penalty_min=5.0)
    metrics.record_arrival(0, 50.0)
    metrics.record_arrival(1, 70.0)

    assert metrics.success_count == 1
    assert metrics.censored_count == 1
    assert_close(metrics.completion_rate, 0.5, label="completion rate")
    assert metrics.penalized_makespan == 75.0
    print("PASS: late arrivals are censored")


TESTS = [
    test_complete_run_keeps_legacy_makespan,
    test_complete_run_reports_unit_consistent_resources,
    test_partial_run_adds_censoring_penalty,
    test_no_arrivals_gets_finite_penalized_makespan,
    test_zero_resource_rates_are_zero,
    test_late_arrivals_are_censored,
]


if __name__ == "__main__":
    for test in TESTS:
        test()
    print("\n=== ALL METRICS TESTS PASSED ===")
