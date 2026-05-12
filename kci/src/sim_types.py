"""Shared simulation record types and validation helpers.

These small immutable records keep cross-module contracts explicit while the
scenario orchestrator wires dispatch, traffic, disruption, and rail behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import operator
from typing import Any, Literal


DisruptionStatus = Literal["normal", "degraded", "blocked"]
_DISRUPTION_STATUSES = {"normal", "degraded", "blocked"}


def require_finite(value: float, name: str) -> float:
    """Return ``value`` as a finite float or raise ``ValueError``."""

    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"{name} must be finite")
    return numeric


def require_non_negative(value: float, name: str) -> float:
    """Return ``value`` as a finite, non-negative float."""

    numeric = require_finite(value, name)
    if numeric < 0.0:
        raise ValueError(f"{name} must be non-negative")
    return numeric


def require_non_negative_or_inf(value: float, name: str) -> float:
    """Return ``value`` as a non-negative float, allowing positive infinity."""

    numeric = float(value)
    if math.isnan(numeric) or numeric < 0.0:
        raise ValueError(f"{name} must be non-negative")
    return numeric


def require_positive(value: float, name: str) -> float:
    """Return ``value`` as a finite, positive float."""

    numeric = require_finite(value, name)
    if numeric <= 0.0:
        raise ValueError(f"{name} must be positive")
    return numeric


def require_int_at_least(value: Any, name: str, minimum: int) -> int:
    """Return ``value`` as an integer greater than or equal to ``minimum``."""

    if isinstance(value, bool):
        raise ValueError(f"{name} must be an integer")

    try:
        integer = operator.index(value)
    except TypeError:
        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{name} must be an integer") from exc
        if not math.isfinite(numeric) or not numeric.is_integer():
            raise ValueError(f"{name} must be an integer")
        integer = int(numeric)

    if integer < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return int(integer)


@dataclass(frozen=True)
class Passenger:
    """A passenger with an absolute arrival time at the current origin."""

    id: int
    arrival_time: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "id", require_int_at_least(self.id, "passenger id", 0))
        object.__setattr__(
            self,
            "arrival_time",
            require_non_negative(self.arrival_time, "passenger arrival_time"),
        )


@dataclass(frozen=True)
class VehicleTrip:
    """A dispatched vehicle trip and its passenger manifest."""

    mode: str
    depart_time: float
    arrival_time: float
    passenger_ids: tuple[int, ...]
    route: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.mode:
            raise ValueError("vehicle trip mode must be non-empty")

        depart_time = require_non_negative(self.depart_time, "vehicle depart_time")
        arrival_time = require_non_negative(self.arrival_time, "vehicle arrival_time")
        if arrival_time < depart_time:
            raise ValueError("vehicle arrival_time must be at or after depart_time")

        object.__setattr__(self, "depart_time", depart_time)
        object.__setattr__(self, "arrival_time", arrival_time)
        object.__setattr__(
            self,
            "passenger_ids",
            tuple(
                require_int_at_least(passenger_id, "passenger id", 0)
                for passenger_id in self.passenger_ids
            ),
        )
        object.__setattr__(self, "route", tuple(self.route))


@dataclass(frozen=True)
class EdgeDisruption:
    """Per-edge disruption state consumed by traffic and route traversal."""

    status: DisruptionStatus = "normal"
    capacity_factor: float = 1.0

    def __post_init__(self) -> None:
        if self.status not in _DISRUPTION_STATUSES:
            raise ValueError(f"unknown disruption status: {self.status!r}")

        capacity_factor = require_non_negative(
            self.capacity_factor,
            "disruption capacity_factor",
        )
        if capacity_factor > 1.0:
            raise ValueError("disruption capacity_factor must be at most 1")
        object.__setattr__(self, "capacity_factor", capacity_factor)

    @property
    def is_blocked(self) -> bool:
        return self.status == "blocked"


@dataclass(frozen=True)
class EdgeTraversal:
    """A vehicle traversal of one graph edge."""

    edge: tuple[str, str]
    entry_time: float
    exit_time: float
    travel_time: float
    effective_volume: float
    effective_capacity: float

    def __post_init__(self) -> None:
        if len(self.edge) != 2:
            raise ValueError("edge must contain exactly two endpoints")

        entry_time = require_non_negative(self.entry_time, "edge entry_time")
        exit_time = require_non_negative_or_inf(self.exit_time, "edge exit_time")
        travel_time = require_non_negative_or_inf(self.travel_time, "edge travel_time")
        if math.isfinite(exit_time) and exit_time < entry_time:
            raise ValueError("edge exit_time must be at or after entry_time")

        object.__setattr__(self, "edge", tuple(self.edge))
        object.__setattr__(self, "entry_time", entry_time)
        object.__setattr__(self, "exit_time", exit_time)
        object.__setattr__(self, "travel_time", travel_time)
        object.__setattr__(
            self,
            "effective_volume",
            require_non_negative(self.effective_volume, "edge effective_volume"),
        )
        object.__setattr__(
            self,
            "effective_capacity",
            require_non_negative_or_inf(
                self.effective_capacity,
                "edge effective_capacity",
            ),
        )


@dataclass(frozen=True)
class StationBatch:
    """Passengers becoming ready in a station queue at a shared time."""

    ready_time: float
    passenger_ids: tuple[int, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "ready_time",
            require_non_negative(self.ready_time, "station batch ready_time"),
        )
        object.__setattr__(
            self,
            "passenger_ids",
            tuple(
                require_int_at_least(passenger_id, "passenger id", 0)
                for passenger_id in self.passenger_ids
            ),
        )


__all__ = [
    "DisruptionStatus",
    "Passenger",
    "VehicleTrip",
    "EdgeDisruption",
    "EdgeTraversal",
    "StationBatch",
    "require_finite",
    "require_non_negative",
    "require_non_negative_or_inf",
    "require_positive",
    "require_int_at_least",
]
