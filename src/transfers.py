"""Transfer delay helpers for multimodal movement."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable, MutableSequence
from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar

from src.sim_types import require_non_negative


T = TypeVar("T")
TransferCallback = Callable[["TransferResult[T]"], None]


@dataclass(frozen=True)
class TransferDelayConfig:
    """Fixed plus crowd-dependent transfer delay configuration."""

    base_min: float = 0.0
    per_passenger_min: float = 0.0

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "base_min",
            require_non_negative(self.base_min, "base_min"),
        )
        object.__setattr__(
            self,
            "per_passenger_min",
            require_non_negative(self.per_passenger_min, "per_passenger_min"),
        )

    def delay_for(self, passenger_count: int | float) -> float:
        return compute_transfer_delay(
            passenger_count,
            base_min=self.base_min,
            per_passenger_min=self.per_passenger_min,
        )


@dataclass(frozen=True)
class TransferResult(Generic[T]):
    """A completed transfer batch."""

    ready_time: float
    delay_min: float
    passenger_ids: tuple[T, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "ready_time",
            require_non_negative(self.ready_time, "transfer ready_time"),
        )
        object.__setattr__(
            self,
            "delay_min",
            require_non_negative(self.delay_min, "transfer delay_min"),
        )
        object.__setattr__(self, "passenger_ids", tuple(self.passenger_ids))

    @property
    def passenger_count(self) -> int:
        return len(self.passenger_ids)

    @property
    def passengers(self) -> tuple[T, ...]:
        """Alias for callers that store passenger records instead of IDs."""

        return self.passenger_ids


def compute_transfer_delay(
    passenger_count: int | float,
    *,
    base_min: float = 0.0,
    per_passenger_min: float = 0.0,
) -> float:
    """Return transfer delay as ``base_min + per_passenger_min * n``."""

    passenger_count = require_non_negative(passenger_count, "passenger_count")
    config = TransferDelayConfig(base_min=base_min, per_passenger_min=per_passenger_min)
    return config.base_min + config.per_passenger_min * passenger_count


def wait_for_transfer(
    env: Any,
    passenger_count: int | float,
    *,
    base_min: float = 0.0,
    per_passenger_min: float = 0.0,
):
    """SimPy process that waits for the computed transfer delay."""

    delay = compute_transfer_delay(
        passenger_count,
        base_min=base_min,
        per_passenger_min=per_passenger_min,
    )
    yield env.timeout(delay)
    return delay


def transfer_batch(
    env: Any,
    passengers: Iterable[T],
    destination_queue: Any | None = None,
    *,
    base_min: float = 0.0,
    per_passenger_min: float = 0.0,
    on_ready: TransferCallback[T] | None = None,
):
    """Wait for transfer delay, then make a passenger batch available.

    ``destination_queue`` may be a list-like object, a ``collections.deque``, or
    a SimPy Store-like object exposing an ``items`` list.
    """

    passenger_ids = tuple(passengers)
    delay = compute_transfer_delay(
        len(passenger_ids),
        base_min=base_min,
        per_passenger_min=per_passenger_min,
    )

    yield env.timeout(delay)

    if destination_queue is not None:
        _extend_queue(destination_queue, passenger_ids)

    result = TransferResult(
        ready_time=float(env.now),
        delay_min=delay,
        passenger_ids=passenger_ids,
    )
    if on_ready is not None:
        on_ready(result)
    return result


def _extend_queue(queue: Any, passenger_ids: tuple[Any, ...]) -> None:
    """Append a completed transfer batch to a queue."""

    if hasattr(queue, "items"):
        queue.items.extend(passenger_ids)
        return
    if isinstance(queue, deque):
        queue.extend(passenger_ids)
        return
    if isinstance(queue, MutableSequence):
        queue.extend(passenger_ids)
        return
    raise TypeError("destination_queue must be list-like, deque-like, or Store-like")


transfer_delay = compute_transfer_delay


__all__ = [
    "TransferDelayConfig",
    "TransferResult",
    "compute_transfer_delay",
    "wait_for_transfer",
    "transfer_batch",
    "transfer_delay",
]
