"""Simple vehicle fleet availability helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.sim_types import VehicleTrip, require_int_at_least, require_non_negative


@dataclass(frozen=True)
class FleetAssignment:
    """A vehicle reservation for one trip."""

    vehicle_id: int
    requested_depart_time: float
    depart_time: float
    arrival_time: float
    available_time: float

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "vehicle_id",
            require_int_at_least(self.vehicle_id, "vehicle_id", 0),
        )
        requested_depart_time = require_non_negative(
            self.requested_depart_time,
            "requested_depart_time",
        )
        depart_time = require_non_negative(self.depart_time, "depart_time")
        arrival_time = require_non_negative(self.arrival_time, "arrival_time")
        available_time = require_non_negative(self.available_time, "available_time")
        if depart_time < requested_depart_time:
            raise ValueError("depart_time must be at or after requested_depart_time")
        if arrival_time < depart_time:
            raise ValueError("arrival_time must be at or after depart_time")
        if available_time < arrival_time:
            raise ValueError("available_time must be at or after arrival_time")

        object.__setattr__(self, "requested_depart_time", requested_depart_time)
        object.__setattr__(self, "depart_time", depart_time)
        object.__setattr__(self, "arrival_time", arrival_time)
        object.__setattr__(self, "available_time", available_time)


class FleetAvailability:
    """Track vehicle availability with deterministic earliest-vehicle assignment."""

    def __init__(self, fleet_size: int, turnaround_time: float = 0.0):
        self.fleet_size = require_int_at_least(fleet_size, "fleet_size", 1)
        self.turnaround_time = require_non_negative(turnaround_time, "turnaround_time")
        self._available_times = [0.0 for _ in range(self.fleet_size)]

    @property
    def next_available_times(self) -> tuple[float, ...]:
        """Return each vehicle's next available time."""

        return tuple(self._available_times)

    def reserve(self, requested_depart_time: float, travel_time: float) -> FleetAssignment:
        """Reserve the earliest available vehicle for a trip.

        The actual departure is delayed only when every vehicle is still busy.
        Ties are broken by the lowest vehicle id to keep assignments stable.
        """

        requested_depart_time = require_non_negative(
            requested_depart_time,
            "requested_depart_time",
        )
        travel_time = require_non_negative(travel_time, "travel_time")

        vehicle_id, vehicle_available = min(
            enumerate(self._available_times), key=lambda item: (item[1], item[0])
        )
        depart_time = max(requested_depart_time, vehicle_available)
        arrival_time = depart_time + travel_time
        available_time = arrival_time + self.turnaround_time
        self._available_times[vehicle_id] = available_time

        return FleetAssignment(
            vehicle_id=vehicle_id,
            requested_depart_time=requested_depart_time,
            depart_time=depart_time,
            arrival_time=arrival_time,
            available_time=available_time,
        )

    def reset(self) -> None:
        """Reset all vehicles to be available at time zero."""

        self._available_times = [0.0 for _ in range(self.fleet_size)]


def apply_fleet_availability(
    trips: Iterable[VehicleTrip],
    fleet_size: int,
    turnaround_time: float = 0.0,
) -> list[VehicleTrip]:
    """Delay planned trips according to fleet size and turnaround time.

    Passenger manifests stay fixed. A passenger who was late for the policy
    departure remains queued for a later planned dispatch even if fleet
    availability pushes the physical trip later.
    """

    fleet = FleetAvailability(fleet_size=fleet_size, turnaround_time=turnaround_time)
    scheduled_trips = sorted(enumerate(trips), key=lambda item: (item[1].depart_time, item[0]))
    adjusted: list[tuple[int, VehicleTrip]] = []

    for original_index, trip in scheduled_trips:
        travel_time = trip.arrival_time - trip.depart_time
        require_non_negative(trip.depart_time, "trip.depart_time")
        travel_time = require_non_negative(travel_time, "trip travel_time")
        assignment = fleet.reserve(trip.depart_time, travel_time)
        adjusted.append((
            original_index,
            VehicleTrip(
                mode=trip.mode,
                depart_time=assignment.depart_time,
                arrival_time=assignment.arrival_time,
                passenger_ids=trip.passenger_ids,
                route=trip.route,
            ),
        ))

    return [trip for _, trip in sorted(adjusted, key=lambda item: (item[1].depart_time, item[0]))]


__all__ = [
    "FleetAssignment",
    "FleetAvailability",
    "apply_fleet_availability",
]
