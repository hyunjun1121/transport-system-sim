"""Unit tests for passenger queue dispatch helpers."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.dispatch import (
    normalize_passengers,
    plan_dispatches,
    plan_dispatches_with_fleet,
    trips_to_ready_batches,
)
from src.policies import GracePolicy, StrictPolicy
from src.sim_types import Passenger


class NeverDepartPolicy(StrictPolicy):
    """Test policy that violates the dispatch contract."""

    def should_depart(
        self,
        elapsed_wait,
        arrived_count,
        total_expected,
        vehicle_capacity,
    ):
        return False

    def name(self):
        return "NEVER"


def test_strict_departs_on_schedule_with_arrived_passengers_only():
    """STRICT should not wait for passengers who miss the scheduled time."""
    trips = plan_dispatches(
        passengers=[
            Passenger(id=0, arrival_time=0.0),
            Passenger(id=1, arrival_time=0.0),
            Passenger(id=2, arrival_time=6.0),
            Passenger(id=3, arrival_time=6.0),
        ],
        policy=StrictPolicy(),
        vehicle_capacity=4,
        dispatch_interval=10.0,
        travel_time=5.0,
    )

    assert len(trips) == 2
    assert trips[0].depart_time == 0.0
    assert trips[0].arrival_time == 5.0
    assert trips[0].passenger_ids == (0, 1)
    assert trips[1].depart_time == 10.0
    assert trips[1].arrival_time == 15.0
    assert trips[1].passenger_ids == (2, 3)
    print("PASS: STRICT leaves late arrivals queued")


def test_strict_honors_explicit_first_departure_time():
    """STRICT should evaluate arrivals against the configured timetable."""
    trips = plan_dispatches(
        passengers=[(0, 6.0)],
        policy=StrictPolicy(),
        vehicle_capacity=1,
        dispatch_interval=10.0,
        travel_time=1.0,
        first_depart_time=0.0,
    )

    assert len(trips) == 1
    assert trips[0].depart_time == 10.0
    assert trips[0].arrival_time == 11.0
    assert trips[0].passenger_ids == (0,)
    print("PASS: STRICT honors explicit first departure time")


def test_grace_waits_until_threshold_is_met():
    """GRACE should depart when the configured arrival threshold is met."""
    trips = plan_dispatches(
        passengers=[(0, 0.0), (1, 0.0), (2, 6.0), (3, 6.0)],
        policy=GracePolicy(W=10.0, theta=1.0),
        vehicle_capacity=4,
        dispatch_interval=10.0,
        travel_time=5.0,
    )

    assert len(trips) == 1
    assert trips[0].depart_time == 6.0
    assert trips[0].arrival_time == 11.0
    assert trips[0].passenger_ids == (0, 1, 2, 3)
    print("PASS: GRACE waits for threshold")


def test_grace_max_wait_leaves_later_arrivals_queued():
    """GRACE should leave arrivals after max wait for a later dispatch."""
    trips = plan_dispatches(
        passengers=[(0, 0.0), (1, 0.0), (2, 20.0), (3, 20.0)],
        policy=GracePolicy(W=10.0, theta=1.0),
        vehicle_capacity=4,
        dispatch_interval=10.0,
        travel_time=5.0,
    )

    assert len(trips) == 2
    assert trips[0].depart_time == 10.0
    assert trips[0].passenger_ids == (0, 1)
    assert trips[1].depart_time == 20.0
    assert trips[1].passenger_ids == (2, 3)
    print("PASS: GRACE max wait leaves late arrivals queued")


def test_grace_capacity_trigger_boards_only_vehicle_capacity():
    """Vehicle capacity should trigger departure without losing overflow queue."""
    trips = plan_dispatches(
        passengers=[(0, 0.0), (1, 0.0), (2, 0.0), (3, 0.0)],
        policy=GracePolicy(W=10.0, theta=1.0),
        vehicle_capacity=2,
        dispatch_interval=10.0,
        travel_time=5.0,
        expected_passengers_per_dispatch=4,
    )

    assert len(trips) == 2
    assert trips[0].depart_time == 0.0
    assert trips[0].passenger_ids == (0, 1)
    assert trips[1].depart_time == 10.0
    assert trips[1].passenger_ids == (2, 3)
    print("PASS: GRACE capacity trigger preserves overflow queue")


def test_dispatch_with_fleet_allows_overlapping_trips():
    """Dispatch plus fleet should allow overlap when more than one vehicle exists."""
    trips = plan_dispatches_with_fleet(
        passengers=[0.0, 0.0, 0.0, 0.0],
        policy=StrictPolicy(),
        vehicle_capacity=2,
        dispatch_interval=10.0,
        travel_time=100.0,
        fleet_size=2,
        turnaround_time=100.0,
    )

    assert len(trips) == 2
    assert [trip.depart_time for trip in trips] == [0.0, 10.0]
    assert [trip.arrival_time for trip in trips] == [100.0, 110.0]
    print("PASS: dispatch with fleet allows overlapping trips")


def test_fleet_delay_does_not_retroactively_board_late_arrivals():
    """Fleet-delayed trips should keep the manifest chosen at policy time."""
    trips = plan_dispatches_with_fleet(
        passengers=[(0, 0.0), (1, 5.0), (2, 60.0)],
        policy=StrictPolicy(),
        vehicle_capacity=2,
        dispatch_interval=10.0,
        travel_time=100.0,
        fleet_size=1,
        turnaround_time=0.0,
    )

    assert len(trips) == 3
    assert [trip.depart_time for trip in trips] == [0.0, 100.0, 200.0]
    assert [trip.arrival_time for trip in trips] == [100.0, 200.0, 300.0]
    assert [trip.passenger_ids for trip in trips] == [(0,), (1,), (2,)]
    print("PASS: fleet delay preserves policy-time manifests")


def test_trips_to_ready_batches_uses_trip_arrivals():
    """Vehicle trip arrivals should become downstream-ready passenger batches."""
    trips = plan_dispatches(
        passengers=[(0, 0.0), (1, 6.0)],
        policy=StrictPolicy(),
        vehicle_capacity=1,
        dispatch_interval=10.0,
        travel_time=5.0,
    )

    batches = trips_to_ready_batches(trips)

    assert [batch.ready_time for batch in batches] == [5.0, 15.0]
    assert [batch.passenger_ids for batch in batches] == [(0,), (1,)]
    print("PASS: trip arrivals become ready batches")


def test_normalize_passengers_is_stable_and_validates_ids():
    """Normalization should sort by arrival time and reject duplicate ids."""
    passengers = normalize_passengers([
        {"id": 2, "arrival_time": 5.0},
        Passenger(id=1, arrival_time=0.0),
        (3, 0.0),
    ])

    assert [passenger.id for passenger in passengers] == [1, 3, 2]

    try:
        normalize_passengers([(1, 0.0), (1, 5.0)])
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate passenger ids should raise ValueError")
    print("PASS: passenger normalization is stable and validates ids")


def test_normalize_passengers_rejects_invalid_arrival_times():
    """Passenger arrivals should be finite and non-negative."""
    for records in ([-1.0], [float("nan")]):
        try:
            normalize_passengers(records)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid passenger arrival should raise ValueError")
    print("PASS: passenger normalization rejects invalid arrival times")


def test_dispatch_rejects_policy_that_never_releases_arrivals():
    """A bad custom policy should fail instead of leaving the loop unbounded."""
    try:
        plan_dispatches(
            passengers=[(0, 0.0)],
            policy=NeverDepartPolicy(),
            vehicle_capacity=1,
            dispatch_interval=10.0,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("non-releasing policy should raise ValueError")
    print("PASS: dispatch rejects non-releasing policies")


if __name__ == "__main__":
    test_strict_departs_on_schedule_with_arrived_passengers_only()
    test_strict_honors_explicit_first_departure_time()
    test_grace_waits_until_threshold_is_met()
    test_grace_max_wait_leaves_later_arrivals_queued()
    test_grace_capacity_trigger_boards_only_vehicle_capacity()
    test_dispatch_with_fleet_allows_overlapping_trips()
    test_fleet_delay_does_not_retroactively_board_late_arrivals()
    test_trips_to_ready_batches_uses_trip_arrivals()
    test_normalize_passengers_is_stable_and_validates_ids()
    test_normalize_passengers_rejects_invalid_arrival_times()
    test_dispatch_rejects_policy_that_never_releases_arrivals()
    print("\n=== ALL DISPATCH TESTS PASSED ===")
