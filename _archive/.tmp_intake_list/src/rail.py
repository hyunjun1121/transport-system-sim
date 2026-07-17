"""Fixed-headway rail service helpers.

The dispatcher in this module treats train departures as schedule events. A
train trip is spawned as its own SimPy process so later departures are not
blocked while earlier trains are still in transit.
"""

from __future__ import annotations

from collections import deque
from collections.abc import MutableSequence
from dataclasses import dataclass
from math import ceil
from typing import Any, Callable, Generic, TypeVar

from src.sim_types import require_int_at_least, require_non_negative, require_positive


T = TypeVar("T")
TrainCallback = Callable[["TrainTrip[T]"], None]


@dataclass(frozen=True)
class RailServiceConfig:
    """Configuration for a single fixed-headway rail service."""

    headway_min: float
    capacity: int
    travel_time_min: float
    first_departure_min: float | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "headway_min",
            require_positive(self.headway_min, "headway_min"),
        )
        object.__setattr__(
            self,
            "capacity",
            require_int_at_least(self.capacity, "capacity", 1),
        )
        object.__setattr__(
            self,
            "travel_time_min",
            require_non_negative(self.travel_time_min, "travel_time_min"),
        )
        if self.first_departure_min is not None:
            object.__setattr__(
                self,
                "first_departure_min",
                require_non_negative(
                    self.first_departure_min,
                    "first_departure_min",
                ),
            )

    @property
    def first_departure_time(self) -> float:
        """First scheduled departure time.

        By default, the first departure occurs after one headway. Pass
        ``first_departure_min=0`` for an immediate first departure.
        """

        if self.first_departure_min is None:
            return self.headway_min
        return self.first_departure_min


@dataclass(frozen=True)
class TrainTrip(Generic[T]):
    """A rail trip event with its boarded passenger manifest."""

    train_id: int
    depart_time: float
    arrival_time: float
    passenger_ids: tuple[T, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "train_id",
            require_int_at_least(self.train_id, "train_id", 0),
        )
        depart_time = require_non_negative(self.depart_time, "train depart_time")
        arrival_time = require_non_negative(self.arrival_time, "train arrival_time")
        if arrival_time < depart_time:
            raise ValueError("train arrival_time must be at or after depart_time")
        object.__setattr__(self, "depart_time", depart_time)
        object.__setattr__(self, "arrival_time", arrival_time)
        object.__setattr__(self, "passenger_ids", tuple(self.passenger_ids))

    @property
    def passenger_count(self) -> int:
        return len(self.passenger_ids)

    @property
    def passengers(self) -> tuple[T, ...]:
        """Alias for callers that store passenger records instead of IDs."""

        return self.passenger_ids


def board_passengers(waiting_queue: Any, capacity: int) -> tuple[Any, ...]:
    """Board up to ``capacity`` passengers and leave excess in the queue.

    ``waiting_queue`` may be a list-like object, a ``collections.deque``, or a
    SimPy Store-like object exposing an ``items`` list.
    """

    capacity = require_int_at_least(capacity, "capacity", 1)

    items = _queue_items(waiting_queue)
    board_count = min(len(items), capacity)
    if board_count == 0:
        return ()

    if isinstance(items, deque):
        return tuple(items.popleft() for _ in range(board_count))

    boarded = tuple(items[:board_count])
    del items[:board_count]
    return boarded


def next_departure_time(
    now: float,
    headway_min: float,
    first_departure_min: float | None = None,
) -> float:
    """Return the next scheduled departure at or after ``now``."""

    now = require_non_negative(now, "now")
    headway_min = require_positive(headway_min, "headway_min")
    first_departure = headway_min if first_departure_min is None else first_departure_min
    first_departure = require_non_negative(first_departure, "first_departure_min")
    if now <= first_departure:
        return first_departure
    return first_departure + ceil((now - first_departure) / headway_min) * headway_min


def departure_times(
    headway_min: float,
    count: int,
    first_departure_min: float | None = None,
) -> list[float]:
    """Return ``count`` scheduled fixed-headway departure times."""

    count = require_int_at_least(count, "count", 0)
    first_departure = next_departure_time(
        0.0,
        headway_min=headway_min,
        first_departure_min=first_departure_min,
    )
    return [first_departure + i * headway_min for i in range(count)]


def fixed_headway_dispatcher(
    env: Any,
    waiting_queue: Any,
    *,
    headway_min: float,
    capacity: int,
    travel_time_min: float,
    first_departure_min: float | None = None,
    until: float | None = None,
    on_depart: TrainCallback[Any] | None = None,
    on_arrive: TrainCallback[Any] | None = None,
):
    """SimPy process for fixed-headway rail departures.

    At each scheduled departure, the process boards up to ``capacity`` from the
    station queue. If passengers board, it records a ``TrainTrip`` and starts a
    separate travel process. The dispatcher then immediately schedules the next
    headway, so train travel time cannot serialize later departures.
    """

    config = RailServiceConfig(
        headway_min=headway_min,
        capacity=capacity,
        travel_time_min=travel_time_min,
        first_departure_min=first_departure_min,
    )
    if until is not None:
        until = require_non_negative(until, "until")

    next_departure = next_departure_time(
        float(env.now),
        headway_min=config.headway_min,
        first_departure_min=config.first_departure_time,
    )
    train_id = 0

    while until is None or next_departure <= until:
        if env.now < next_departure:
            yield env.timeout(next_departure - env.now)

        boarded = board_passengers(waiting_queue, config.capacity)
        if boarded:
            depart_time = float(env.now)
            trip = TrainTrip(
                train_id=train_id,
                depart_time=depart_time,
                arrival_time=depart_time + config.travel_time_min,
                passenger_ids=boarded,
            )
            train_id += 1

            if on_depart is not None:
                on_depart(trip)

            env.process(_complete_train_trip(env, trip, on_arrive))

        next_departure += config.headway_min


def start_fixed_headway_service(
    env: Any,
    waiting_queue: Any,
    **kwargs: Any,
) -> Any:
    """Start ``fixed_headway_dispatcher`` as a SimPy process."""

    return env.process(fixed_headway_dispatcher(env, waiting_queue, **kwargs))


def _complete_train_trip(
    env: Any,
    trip: TrainTrip[Any],
    on_arrive: TrainCallback[Any] | None,
):
    """Complete one train trip without blocking the rail dispatcher."""

    travel_delay = max(0.0, trip.arrival_time - float(env.now))
    yield env.timeout(travel_delay)
    if on_arrive is not None:
        on_arrive(trip)


def _queue_items(queue: Any) -> MutableSequence[Any] | deque[Any]:
    """Return the mutable sequence backing a station queue."""

    if hasattr(queue, "items"):
        return queue.items
    if isinstance(queue, deque):
        return queue
    if isinstance(queue, MutableSequence):
        return queue
    raise TypeError("waiting_queue must be list-like, deque-like, or Store-like")


rail_dispatcher = fixed_headway_dispatcher


__all__ = [
    "RailServiceConfig",
    "TrainTrip",
    "board_passengers",
    "next_departure_time",
    "departure_times",
    "fixed_headway_dispatcher",
    "start_fixed_headway_service",
    "rail_dispatcher",
]
