"""Passenger queue dispatch helpers for scheduled transport services."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
import math
from typing import Any

from src.fleet import apply_fleet_availability
from src.policies import DeparturePolicy
from src.sim_types import (
    Passenger,
    StationBatch,
    VehicleTrip,
    require_finite,
    require_int_at_least,
    require_non_negative,
    require_positive,
)


PassengerRecord = Passenger | Mapping[str, Any] | Sequence[Any] | float | int


def normalize_passengers(records: Iterable[PassengerRecord]) -> tuple[Passenger, ...]:
    """Normalize deterministic passenger arrival records.

    Accepted records are ``Passenger`` objects, mappings with ``id`` and
    ``arrival_time`` keys, ``(id, arrival_time)`` pairs, or bare numeric arrival
    times. Bare times receive stable zero-based ids in input order.
    """

    passengers = tuple(
        _coerce_passenger(record, fallback_id=index)
        for index, record in enumerate(records)
    )
    seen_ids: set[int] = set()
    for passenger in passengers:
        if passenger.id in seen_ids:
            raise ValueError(f"duplicate passenger id: {passenger.id}")
        seen_ids.add(passenger.id)
        require_finite(passenger.arrival_time, "passenger arrival_time")
    return tuple(sorted(passengers, key=lambda passenger: (passenger.arrival_time, passenger.id)))


def plan_dispatches(
    passengers: Iterable[PassengerRecord],
    policy: DeparturePolicy,
    vehicle_capacity: int,
    dispatch_interval: float,
    travel_time: float = 0.0,
    *,
    first_depart_time: float = 0.0,
    expected_passengers_per_dispatch: int | None = None,
    mode: str = "bus",
    route: Sequence[str] = (),
) -> list[VehicleTrip]:
    """Plan deterministic passenger manifests from a single origin queue.

    The GRACE denominator is the scheduled batch target, capped by remaining
    demand. If ``expected_passengers_per_dispatch`` is omitted, vehicle capacity
    is used as the scheduled batch target.
    """

    (
        vehicle_capacity,
        dispatch_interval,
        travel_time,
        first_depart_time,
        expected_passengers_per_dispatch,
    ) = _normalize_dispatch_inputs(
        vehicle_capacity=vehicle_capacity,
        dispatch_interval=dispatch_interval,
        travel_time=travel_time,
        first_depart_time=first_depart_time,
        expected_passengers_per_dispatch=expected_passengers_per_dispatch,
    )

    queue = list(normalize_passengers(passengers))
    trips: list[VehicleTrip] = []
    if not queue:
        return trips

    batch_target = expected_passengers_per_dispatch or vehicle_capacity
    schedule_index = 0
    scheduled_time = first_depart_time
    max_wait = _policy_max_wait(policy)

    while queue:
        next_arrival = queue[0].arrival_time
        if next_arrival > scheduled_time + max_wait:
            schedule_index = _next_schedule_index_covering_arrival(
                first_depart_time=first_depart_time,
                dispatch_interval=dispatch_interval,
                max_wait=max_wait,
                arrival_time=next_arrival,
                minimum_index=schedule_index + 1,
            )
            scheduled_time = first_depart_time + schedule_index * dispatch_interval
            continue

        expected_count = min(batch_target, len(queue))
        depart_time = _select_departure_time(
            queue=queue,
            policy=policy,
            scheduled_time=scheduled_time,
            max_wait=max_wait,
            expected_count=expected_count,
            vehicle_capacity=vehicle_capacity,
        )

        if depart_time is not None:
            boarded, queue = _board_arrived(queue, depart_time, vehicle_capacity)
            if boarded:
                trips.append(
                    VehicleTrip(
                        mode=mode,
                        depart_time=depart_time,
                        arrival_time=depart_time + travel_time,
                        passenger_ids=tuple(passenger.id for passenger in boarded),
                        route=tuple(route),
                    )
                )
        elif _count_arrived(queue, scheduled_time + max_wait) > 0:
            raise ValueError("departure policy did not release arrived passengers")

        schedule_index += 1
        scheduled_time = first_depart_time + schedule_index * dispatch_interval

    return trips


def plan_dispatches_with_fleet(
    passengers: Iterable[PassengerRecord],
    policy: DeparturePolicy,
    vehicle_capacity: int,
    dispatch_interval: float,
    travel_time: float = 0.0,
    *,
    fleet_size: int,
    turnaround_time: float = 0.0,
    first_depart_time: float = 0.0,
    expected_passengers_per_dispatch: int | None = None,
    mode: str = "bus",
    route: Sequence[str] = (),
) -> list[VehicleTrip]:
    """Plan manifests and then apply fleet availability to departure times."""

    planned = plan_dispatches(
        passengers=passengers,
        policy=policy,
        vehicle_capacity=vehicle_capacity,
        dispatch_interval=dispatch_interval,
        travel_time=travel_time,
        first_depart_time=first_depart_time,
        expected_passengers_per_dispatch=expected_passengers_per_dispatch,
        mode=mode,
        route=route,
    )
    return apply_fleet_availability(
        trips=planned,
        fleet_size=fleet_size,
        turnaround_time=turnaround_time,
    )


def trips_to_ready_batches(trips: Iterable[VehicleTrip]) -> list[StationBatch]:
    """Convert vehicle arrivals into downstream-ready passenger batches."""

    return [
        StationBatch(ready_time=trip.arrival_time, passenger_ids=trip.passenger_ids)
        for trip in sorted(trips, key=lambda trip: (trip.arrival_time, trip.depart_time))
    ]


def _select_departure_time(
    queue: Sequence[Passenger],
    policy: DeparturePolicy,
    scheduled_time: float,
    max_wait: float,
    expected_count: int,
    vehicle_capacity: int,
) -> float | None:
    candidates = {float(scheduled_time), float(scheduled_time) + max_wait}
    deadline = float(scheduled_time) + max_wait
    for passenger in queue:
        if passenger.arrival_time < scheduled_time:
            continue
        if passenger.arrival_time <= deadline:
            candidates.add(passenger.arrival_time)
        else:
            break

    for candidate_time in sorted(candidates):
        arrived_count = _count_arrived(queue, candidate_time)
        elapsed_wait = max(0.0, candidate_time - float(scheduled_time))
        if arrived_count > 0 and policy.should_depart(
            elapsed_wait=elapsed_wait,
            arrived_count=arrived_count,
            total_expected=expected_count,
            vehicle_capacity=vehicle_capacity,
        ):
            return candidate_time

    return None


def _board_arrived(
    queue: Sequence[Passenger],
    depart_time: float,
    vehicle_capacity: int,
) -> tuple[list[Passenger], list[Passenger]]:
    split_index = 0
    for passenger in queue:
        if passenger.arrival_time > depart_time:
            break
        split_index += 1

    arrived = list(queue[:split_index])
    not_arrived = list(queue[split_index:])
    boarded = arrived[:vehicle_capacity]
    still_queued = arrived[vehicle_capacity:] + not_arrived
    return boarded, still_queued


def _count_arrived(queue: Sequence[Passenger], time: float) -> int:
    count = 0
    for passenger in queue:
        if passenger.arrival_time > time:
            break
        count += 1
    return count


def _policy_max_wait(policy: DeparturePolicy) -> float:
    return require_non_negative(getattr(policy, "W", 0.0), "policy max wait")


def _next_schedule_index_covering_arrival(
    first_depart_time: float,
    dispatch_interval: float,
    max_wait: float,
    arrival_time: float,
    minimum_index: int,
) -> int:
    target_start = arrival_time - max_wait
    raw_index = math.ceil((target_start - first_depart_time) / dispatch_interval)
    return max(0, minimum_index, raw_index)


def _normalize_dispatch_inputs(
    vehicle_capacity: int,
    dispatch_interval: float,
    travel_time: float,
    first_depart_time: float,
    expected_passengers_per_dispatch: int | None,
) -> tuple[int, float, float, float, int | None]:
    expected_count = (
        None
        if expected_passengers_per_dispatch is None
        else require_int_at_least(
            expected_passengers_per_dispatch,
            "expected_passengers_per_dispatch",
            1,
        )
    )
    return (
        require_int_at_least(vehicle_capacity, "vehicle_capacity", 1),
        require_positive(dispatch_interval, "dispatch_interval"),
        require_non_negative(travel_time, "travel_time"),
        require_non_negative(first_depart_time, "first_depart_time"),
        expected_count,
    )


def _coerce_passenger(record: PassengerRecord, fallback_id: int) -> Passenger:
    if isinstance(record, Passenger):
        return record

    if isinstance(record, Mapping):
        passenger_id = record.get("id", record.get("person_id", fallback_id))
        arrival_time = record.get("arrival_time")
        if arrival_time is None:
            arrival_time = record.get("ready_time")
        if arrival_time is None:
            raise ValueError("passenger mapping requires arrival_time or ready_time")
        return Passenger(id=int(passenger_id), arrival_time=float(arrival_time))

    if isinstance(record, (int, float)):
        return Passenger(id=fallback_id, arrival_time=float(record))

    if (
        isinstance(record, Sequence)
        and not isinstance(record, (str, bytes, bytearray))
        and len(record) == 2
    ):
        return Passenger(id=int(record[0]), arrival_time=float(record[1]))

    raise TypeError(f"unsupported passenger record: {record!r}")


__all__ = [
    "PassengerRecord",
    "normalize_passengers",
    "plan_dispatches",
    "plan_dispatches_with_fleet",
    "trips_to_ready_batches",
]
