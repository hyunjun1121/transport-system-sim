"""Unit tests for censoring-safe metric KPIs."""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.metrics import MetricsCollector


LEGACY_AS_DICT_KEYS = {
    "makespan",
    "success_count",
    "success_rate",
    "total_personnel",
    "bus_trips",
    "train_trips",
    "bus_minutes",
    "train_minutes",
    "lastmile_minutes",
    "lastmile_vehicle_minutes",
    "road_vehicle_service_minutes",
    "train_service_minutes",
    "total_service_minutes",
    "passenger_travel_minutes",
    "passengers_per_vehicle_minute",
    "passengers_per_total_service_minute",
    "resource_efficiency",
    "rerouting_events",
    "leftover_count",
    "censored_count",
    "completion_rate",
    "penalized_makespan",
    "first_arrival_time",
    "median_arrival_time",
    "p80_arrival_time",
    "p95_arrival_time",
    "service_breakdown",
}


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
    assert result["first_arrival_time"] == 20.0
    assert result["median_arrival_time"] == 25.0
    assert result["p80_arrival_time"] == 28.0
    assert result["p95_arrival_time"] == 29.5
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
    metrics.record_empty_return(4.0)

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
    assert metrics.first_arrival_time == 50.0
    assert metrics.median_arrival_time == 50.0
    assert metrics.p80_arrival_time == 50.0
    assert metrics.p95_arrival_time == 50.0
    assert metrics.penalized_makespan == 75.0
    print("PASS: late arrivals are censored")


def test_extended_transport_accounting_arithmetic():
    """Opt-in accounting should separate road and rail resource denominators."""
    metrics = MetricsCollector(total_personnel=10, time_limit=100.0)
    metrics.record_vehicle_load(boarded_passengers=8, seat_capacity=10)
    metrics.record_vehicle_load(boarded_passengers=3, seat_capacity=5)
    metrics.record_vehicle_cycle(2)
    metrics.record_rail_load(boarded_passengers=9, seat_capacity=12)
    metrics.record_empty_return(travel_time_min=12.5, trips=2)
    metrics.record_passenger_wait("assembly", wait_time_min=5.0, passenger_count=4)
    metrics.record_passenger_wait("assembly", wait_time_min=10.0, passenger_count=2)
    metrics.record_passenger_wait("transfer", wait_time_min=3.0, passenger_count=5)
    metrics.record_passenger_wait("rail", wait_time_min=7.0, passenger_count=3)

    result = metrics.as_dict(include_extended=True)

    assert result["empty_return_trips"] == 2
    assert result["empty_return_minutes"] == 25.0
    assert result["road_vehicle_operating_minutes"] == 25.0
    assert result["total_operating_minutes"] == 25.0
    assert result["vehicle_cycles"] == 2
    assert result["deployed_seat_capacity"] == 15
    assert result["boarded_passengers"] == 11
    assert_close(
        result["mean_vehicle_load_factor"],
        round(11.0 / 15.0, 4),
        label="mean vehicle load factor",
    )
    assert result["road_vehicle_cycles"] == 2
    assert result["road_deployed_seat_capacity"] == 15
    assert result["road_boarded_passengers"] == 11
    assert_close(
        result["road_mean_vehicle_load_factor"],
        round(11.0 / 15.0, 4),
        label="road mean vehicle load factor",
    )
    assert result["rail_deployed_seat_capacity"] == 12
    assert result["rail_boarded_passengers"] == 9
    assert_close(
        result["rail_mean_load_factor"],
        0.75,
        label="rail mean load factor",
    )
    assert result["assembly_wait_passenger_minutes"] == 40.0
    assert result["assembly_wait_passenger_count"] == 6
    assert_close(
        result["mean_assembly_wait_min"],
        round(40.0 / 6.0, 2),
        label="mean assembly wait",
    )
    assert result["transfer_wait_passenger_minutes"] == 15.0
    assert result["transfer_wait_passenger_count"] == 5
    assert result["mean_transfer_wait_min"] == 3.0
    assert result["rail_wait_passenger_minutes"] == 21.0
    assert result["rail_wait_passenger_count"] == 3
    assert result["mean_rail_wait_min"] == 7.0
    print("PASS: extended accounting arithmetic")


def test_extended_accounting_zero_denominators():
    """Empty accounting should expose finite zero ratios and explicit denominators."""
    result = MetricsCollector().as_dict(include_extended=True)

    assert result["mean_vehicle_load_factor"] == 0.0
    assert result["mean_assembly_wait_min"] == 0.0
    assert result["mean_transfer_wait_min"] == 0.0
    assert result["mean_rail_wait_min"] == 0.0
    assert result["deployed_seat_capacity"] == 0
    assert result["road_deployed_seat_capacity"] == 0
    assert result["road_boarded_passengers"] == 0
    assert result["road_mean_vehicle_load_factor"] == 0.0
    assert result["rail_deployed_seat_capacity"] == 0
    assert result["rail_boarded_passengers"] == 0
    assert result["rail_mean_load_factor"] == 0.0
    assert result["assembly_wait_passenger_count"] == 0
    assert result["transfer_wait_passenger_count"] == 0
    assert result["rail_wait_passenger_count"] == 0
    print("PASS: extended accounting zero denominators")


def test_default_as_dict_preserves_legacy_contract():
    """Extended mutations must not change default key set or legacy KPI values."""
    metrics = MetricsCollector(total_personnel=1, time_limit=100.0)
    metrics.record_arrival(0, 20.0)
    baseline = metrics.as_dict()

    metrics.record_vehicle_load(boarded_passengers=1, seat_capacity=2)
    metrics.record_vehicle_cycle()
    metrics.record_empty_return(travel_time_min=4.0)
    metrics.record_passenger_wait("assembly", wait_time_min=2.0)

    default_result = metrics.as_dict()
    explicit_default = metrics.as_dict(include_extended=False)
    extended_result = metrics.as_dict(include_extended=True)

    assert set(default_result) == LEGACY_AS_DICT_KEYS
    assert default_result == baseline
    assert explicit_default == baseline
    assert set(extended_result) > LEGACY_AS_DICT_KEYS
    print("PASS: default as_dict preserves legacy contract")


def test_extended_accounting_rejects_negative_inputs():
    """Counts, capacities, and durations must be nonnegative."""
    metrics = MetricsCollector()
    invalid_calls = [
        lambda: metrics.record_vehicle_load(-1, 10),
        lambda: metrics.record_vehicle_load(1, -10),
        lambda: metrics.record_rail_load(-1, 10),
        lambda: metrics.record_rail_load(1, -10),
        lambda: metrics.record_rail_load(11, 10),
        lambda: metrics.record_vehicle_cycle(-1),
        lambda: metrics.record_empty_return(-1.0),
        lambda: metrics.record_empty_return(1.0, trips=-1),
        lambda: metrics.record_passenger_wait("assembly", -1.0),
        lambda: metrics.record_passenger_wait("assembly", 1.0, passenger_count=-1),
        lambda: metrics.record_passenger_wait("unknown", 1.0),
    ]

    for invalid_call in invalid_calls:
        try:
            invalid_call()
        except ValueError:
            continue
        raise AssertionError("negative/unknown extended input did not raise ValueError")

    try:
        MetricsCollector(empty_return_trips=-1)
    except ValueError:
        pass
    else:
        raise AssertionError("negative dataclass field did not raise ValueError")

    try:
        MetricsCollector(
            rail_deployed_seat_capacity=1,
            rail_boarded_passengers=2,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("rail boardings above deployed seats were accepted")
    print("PASS: extended accounting rejects negative inputs")


TESTS = [
    test_complete_run_keeps_legacy_makespan,
    test_complete_run_reports_unit_consistent_resources,
    test_partial_run_adds_censoring_penalty,
    test_no_arrivals_gets_finite_penalized_makespan,
    test_zero_resource_rates_are_zero,
    test_late_arrivals_are_censored,
    test_extended_transport_accounting_arithmetic,
    test_extended_accounting_zero_denominators,
    test_default_as_dict_preserves_legacy_contract,
    test_extended_accounting_rejects_negative_inputs,
]


if __name__ == "__main__":
    for test in TESTS:
        test()
    print("\n=== ALL METRICS TESTS PASSED ===")
