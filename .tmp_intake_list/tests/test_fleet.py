"""Unit tests for fleet availability helpers."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.fleet import FleetAvailability, apply_fleet_availability
from src.sim_types import VehicleTrip


def make_trip(depart_time, arrival_time, passenger_ids):
    return VehicleTrip(
        mode="bus",
        depart_time=depart_time,
        arrival_time=arrival_time,
        passenger_ids=tuple(passenger_ids),
        route=("A", "D"),
    )


def test_single_vehicle_waits_for_turnaround():
    """One vehicle should serialize trips until travel plus turnaround is done."""
    trips = [
        make_trip(0.0, 100.0, [0, 1]),
        make_trip(10.0, 110.0, [2, 3]),
    ]

    adjusted = apply_fleet_availability(
        trips=trips,
        fleet_size=1,
        turnaround_time=100.0,
    )

    assert [trip.depart_time for trip in adjusted] == [0.0, 200.0]
    assert [trip.arrival_time for trip in adjusted] == [100.0, 300.0]
    assert adjusted[1].passenger_ids == (2, 3)
    print("PASS: single vehicle waits for turnaround")


def test_multiple_vehicles_allow_overlapping_trips():
    """A fleet larger than one should not serialize all scheduled trips."""
    trips = [
        make_trip(0.0, 100.0, [0, 1]),
        make_trip(10.0, 110.0, [2, 3]),
    ]

    adjusted = apply_fleet_availability(
        trips=trips,
        fleet_size=2,
        turnaround_time=100.0,
    )

    assert [trip.depart_time for trip in adjusted] == [0.0, 10.0]
    assert [trip.arrival_time for trip in adjusted] == [100.0, 110.0]
    print("PASS: multiple vehicles overlap trips")


def test_fleet_delay_preserves_requested_manifests():
    """Availability delays should not alter passenger manifests."""
    trips = [
        make_trip(0.0, 100.0, [0]),
        make_trip(10.0, 110.0, [1]),
        make_trip(60.0, 160.0, [2]),
    ]

    adjusted = apply_fleet_availability(
        trips=trips,
        fleet_size=1,
        turnaround_time=0.0,
    )

    assert [trip.depart_time for trip in adjusted] == [0.0, 100.0, 200.0]
    assert [trip.arrival_time for trip in adjusted] == [100.0, 200.0, 300.0]
    assert [trip.passenger_ids for trip in adjusted] == [(0,), (1,), (2,)]
    print("PASS: fleet delays preserve requested manifests")


def test_fleet_assignment_is_deterministic():
    """Equal availability ties should choose the lowest vehicle id."""
    fleet = FleetAvailability(fleet_size=2, turnaround_time=5.0)

    first = fleet.reserve(requested_depart_time=0.0, travel_time=10.0)
    second = fleet.reserve(requested_depart_time=0.0, travel_time=10.0)
    third = fleet.reserve(requested_depart_time=1.0, travel_time=10.0)

    assert first.vehicle_id == 0
    assert second.vehicle_id == 1
    assert third.vehicle_id == 0
    assert third.depart_time == 15.0
    print("PASS: fleet assignment is deterministic")


def test_invalid_fleet_inputs_raise():
    """Fleet size and time inputs should reject invalid values."""
    for fleet_size in (0, 1.5):
        try:
            FleetAvailability(fleet_size=fleet_size)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid fleet_size should raise ValueError")

    fleet = FleetAvailability(fleet_size=1)
    for requested_depart_time, travel_time in ((0.0, -1.0), (float("nan"), 1.0)):
        try:
            fleet.reserve(
                requested_depart_time=requested_depart_time,
                travel_time=travel_time,
            )
        except ValueError:
            pass
        else:
            raise AssertionError("invalid reserve input should raise ValueError")
    print("PASS: invalid fleet inputs raise")


if __name__ == "__main__":
    test_single_vehicle_waits_for_turnaround()
    test_multiple_vehicles_allow_overlapping_trips()
    test_fleet_delay_preserves_requested_manifests()
    test_fleet_assignment_is_deterministic()
    test_invalid_fleet_inputs_raise()
    print("\n=== ALL FLEET TESTS PASSED ===")
