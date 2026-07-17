"""Unit tests for fixed-headway rail helpers."""

import os
import sys

import simpy

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rail import (
    RailServiceConfig,
    board_passengers,
    departure_times,
    next_departure_time,
    start_fixed_headway_service,
)


def assert_close(actual, expected, tolerance=0.001, label="value"):
    assert abs(actual - expected) <= tolerance, (
        f"{label}: expected {expected}, got {actual}"
    )


def test_board_passengers_leaves_excess_queued():
    """Capacity-limited boarding should not drop excess passengers."""
    station_queue = [1, 2, 3, 4, 5]

    boarded = board_passengers(station_queue, capacity=3)

    assert boarded == (1, 2, 3)
    assert station_queue == [4, 5]
    print("PASS: rail boarding leaves excess passengers queued")


def test_departure_schedule_defaults_to_one_headway():
    """The default first train follows the current scenario convention."""
    assert departure_times(headway_min=10.0, count=3) == [10.0, 20.0, 30.0]
    assert departure_times(
        headway_min=10.0,
        count=3,
        first_departure_min=0.0,
    ) == [0.0, 10.0, 20.0]
    assert_close(
        next_departure_time(now=21.0, headway_min=10.0),
        30.0,
        label="next departure",
    )
    print("PASS: rail departure schedule uses fixed headway")


def test_fixed_headway_dispatches_while_prior_trains_are_in_transit():
    """Train travel must not serialize the next scheduled departures."""
    env = simpy.Environment()
    station_queue = [1, 2, 3, 4, 5, 6]
    departures = []
    arrivals = []

    start_fixed_headway_service(
        env,
        station_queue,
        headway_min=10.0,
        capacity=2,
        travel_time_min=100.0,
        until=30.0,
        on_depart=departures.append,
        on_arrive=arrivals.append,
    )
    env.run(until=131.0)

    assert [trip.passenger_ids for trip in departures] == [
        (1, 2),
        (3, 4),
        (5, 6),
    ]
    assert [trip.depart_time for trip in departures] == [10.0, 20.0, 30.0]
    assert [trip.arrival_time for trip in arrivals] == [110.0, 120.0, 130.0]
    assert departures[1].depart_time < arrivals[0].arrival_time
    assert station_queue == []
    print("PASS: fixed-headway rail dispatch overlaps in-transit trains")


def test_fixed_headway_skips_empty_departure_and_keeps_running():
    """An empty departure slot should not stop later trains."""
    env = simpy.Environment()
    station_queue = []
    departures = []

    def add_passengers():
        yield env.timeout(15.0)
        station_queue.extend([10, 11, 12, 13])

    env.process(add_passengers())
    start_fixed_headway_service(
        env,
        station_queue,
        headway_min=10.0,
        capacity=3,
        travel_time_min=0.0,
        until=30.0,
        on_depart=departures.append,
    )
    env.run(until=31.0)

    assert [trip.depart_time for trip in departures] == [20.0, 30.0]
    assert [trip.passenger_ids for trip in departures] == [(10, 11, 12), (13,)]
    assert station_queue == []
    print("PASS: rail service keeps running after an empty departure slot")


def test_rail_validation_rejects_non_finite_and_non_integral_inputs():
    """Rail helpers should reject invalid schedule and capacity values."""
    invalid_calls = [
        lambda: RailServiceConfig(
            headway_min=float("nan"),
            capacity=1,
            travel_time_min=0.0,
        ),
        lambda: board_passengers([], capacity=1.5),
        lambda: next_departure_time(now=float("nan"), headway_min=10.0),
        lambda: departure_times(headway_min=10.0, count=1.5),
    ]

    for call in invalid_calls:
        try:
            call()
        except ValueError:
            pass
        else:
            raise AssertionError("invalid rail input should raise ValueError")
    print("PASS: rail validation rejects invalid inputs")


if __name__ == "__main__":
    test_board_passengers_leaves_excess_queued()
    test_departure_schedule_defaults_to_one_headway()
    test_fixed_headway_dispatches_while_prior_trains_are_in_transit()
    test_fixed_headway_skips_empty_departure_and_keeps_running()
    test_rail_validation_rejects_non_finite_and_non_integral_inputs()
    print("\n=== ALL RAIL TESTS PASSED ===")
