"""Deterministic policy and resource definitions for revision experiments.

This module contains no simulation state. It resolves road-fleet bundles and
passenger paths from explicit policy, resource-frame, and rail-status inputs.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping


class RevisionPolicyId(str, Enum):
    """Policy identifiers used by paper-revision experiments."""

    BUS_ONLY = "bus_only"
    STATIC_MULTIMODAL = "static_multimodal"
    PRECHECK_SWITCH = "precheck_switch"
    SPLIT_600_400 = "split_600_400"
    STATION_FALLBACK_30 = "station_fallback_30"
    STATION_FALLBACK_60 = "station_fallback_60"
    STATION_FALLBACK_90 = "station_fallback_90"


class ResourceFrameId(str, Enum):
    """Resource-accounting frames used for policy comparison."""

    CONFIGURED_BUNDLE = "configured_bundle"
    MATCHED_ROAD_FLEET = "matched_road_fleet"


class RailStatus(str, Enum):
    """Rail states relevant to policy decisions."""

    AVAILABLE = "available"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class RevisionPolicyDefinition:
    """Static metadata needed to resolve one policy."""

    policy_id: RevisionPolicyId
    uses_rail: bool
    fallback_after_min: float | None = None
    rail_share_numerator: int | None = None
    rail_share_denominator: int | None = None

    def __post_init__(self) -> None:
        if self.fallback_after_min is not None:
            if not math.isfinite(self.fallback_after_min):
                raise ValueError("fallback_after_min must be finite")
            if self.fallback_after_min < 0:
                raise ValueError("fallback_after_min must be non-negative")

        numerator = self.rail_share_numerator
        denominator = self.rail_share_denominator
        if (numerator is None) != (denominator is None):
            raise ValueError("rail share requires numerator and denominator")
        if numerator is not None and denominator is not None:
            if denominator <= 0 or numerator < 0 or numerator > denominator:
                raise ValueError("rail share must be between zero and one")


@dataclass(frozen=True)
class RoadFleetAllocation:
    """Road vehicles assigned to simultaneous transport roles."""

    direct_bus: int = 0
    feeder_shuttle: int = 0
    last_mile_bus: int = 0
    fallback_bus: int = 0

    def __post_init__(self) -> None:
        for field_name in (
            "direct_bus",
            "feeder_shuttle",
            "last_mile_bus",
            "fallback_bus",
        ):
            value = getattr(self, field_name)
            _require_nonnegative_integer(value, field_name)

    @property
    def total_road_vehicles(self) -> int:
        """Return sum across road-vehicle roles."""

        return (
            self.direct_bus
            + self.feeder_shuttle
            + self.last_mile_bus
            + self.fallback_bus
        )


@dataclass(frozen=True)
class PassengerAllocation:
    """Conservative passenger accounting for one policy decision."""

    demand: int
    direct_bus: int = 0
    rail: int = 0
    station_bus: int = 0
    station_waiting: int = 0
    incomplete: int = 0

    def __post_init__(self) -> None:
        for field_name in (
            "demand",
            "direct_bus",
            "rail",
            "station_bus",
            "station_waiting",
            "incomplete",
        ):
            value = getattr(self, field_name)
            _require_nonnegative_integer(value, field_name)
        if self.accounted_passengers != self.demand:
            raise ValueError("passenger categories must equal demand")

    @property
    def accounted_passengers(self) -> int:
        """Return passengers across all mutually exclusive categories."""

        return (
            self.direct_bus
            + self.rail
            + self.station_bus
            + self.station_waiting
            + self.incomplete
        )


_POLICY_DEFINITIONS: dict[RevisionPolicyId, RevisionPolicyDefinition] = {
    RevisionPolicyId.BUS_ONLY: RevisionPolicyDefinition(
        policy_id=RevisionPolicyId.BUS_ONLY,
        uses_rail=False,
    ),
    RevisionPolicyId.STATIC_MULTIMODAL: RevisionPolicyDefinition(
        policy_id=RevisionPolicyId.STATIC_MULTIMODAL,
        uses_rail=True,
    ),
    RevisionPolicyId.PRECHECK_SWITCH: RevisionPolicyDefinition(
        policy_id=RevisionPolicyId.PRECHECK_SWITCH,
        uses_rail=True,
    ),
    RevisionPolicyId.SPLIT_600_400: RevisionPolicyDefinition(
        policy_id=RevisionPolicyId.SPLIT_600_400,
        uses_rail=True,
        rail_share_numerator=3,
        rail_share_denominator=5,
    ),
    RevisionPolicyId.STATION_FALLBACK_30: RevisionPolicyDefinition(
        policy_id=RevisionPolicyId.STATION_FALLBACK_30,
        uses_rail=True,
        fallback_after_min=30.0,
    ),
    RevisionPolicyId.STATION_FALLBACK_60: RevisionPolicyDefinition(
        policy_id=RevisionPolicyId.STATION_FALLBACK_60,
        uses_rail=True,
        fallback_after_min=60.0,
    ),
    RevisionPolicyId.STATION_FALLBACK_90: RevisionPolicyDefinition(
        policy_id=RevisionPolicyId.STATION_FALLBACK_90,
        uses_rail=True,
        fallback_after_min=90.0,
    ),
}

POLICY_DEFINITIONS: Mapping[RevisionPolicyId, RevisionPolicyDefinition] = (
    MappingProxyType(_POLICY_DEFINITIONS)
)


def get_policy_definition(
    policy_id: RevisionPolicyId | str,
) -> RevisionPolicyDefinition:
    """Return immutable policy metadata after ID validation."""

    resolved = _coerce_enum(RevisionPolicyId, policy_id, "policy_id")
    return POLICY_DEFINITIONS[resolved]


def resolve_road_fleet(
    policy_id: RevisionPolicyId | str,
    resource_frame: ResourceFrameId | str,
) -> RoadFleetAllocation:
    """Resolve deterministic road-vehicle counts for one comparison frame."""

    policy = _coerce_enum(RevisionPolicyId, policy_id, "policy_id")
    frame = _coerce_enum(ResourceFrameId, resource_frame, "resource_frame")

    if frame is ResourceFrameId.CONFIGURED_BUNDLE:
        if policy is RevisionPolicyId.BUS_ONLY:
            return RoadFleetAllocation(direct_bus=23)
        if policy is RevisionPolicyId.SPLIT_600_400:
            return RoadFleetAllocation(
                direct_bus=23,
                feeder_shuttle=23,
                last_mile_bus=23,
            )
        if _is_station_fallback(policy):
            return RoadFleetAllocation(
                feeder_shuttle=23,
                last_mile_bus=23,
                fallback_bus=23,
            )
        return RoadFleetAllocation(feeder_shuttle=23, last_mile_bus=23)

    if policy is RevisionPolicyId.BUS_ONLY:
        return RoadFleetAllocation(direct_bus=23)
    if policy is RevisionPolicyId.SPLIT_600_400:
        return RoadFleetAllocation(
            direct_bus=6,
            feeder_shuttle=9,
            last_mile_bus=8,
        )
    if _is_station_fallback(policy):
        return RoadFleetAllocation(
            feeder_shuttle=8,
            last_mile_bus=8,
            fallback_bus=7,
        )
    return RoadFleetAllocation(feeder_shuttle=12, last_mile_bus=11)


def _is_station_fallback(policy: RevisionPolicyId) -> bool:
    return policy.value.startswith("station_fallback_")


def resolve_passenger_allocation(
    policy_id: RevisionPolicyId | str,
    demand: int,
    *,
    rail_status: RailStatus | str = RailStatus.AVAILABLE,
    station_wait_min: float = 0.0,
) -> PassengerAllocation:
    """Resolve passenger paths without mutating simulation state."""

    policy = _coerce_enum(RevisionPolicyId, policy_id, "policy_id")
    rail = _coerce_enum(RailStatus, rail_status, "rail_status")
    _require_nonnegative_integer(demand, "demand")
    wait = _require_nonnegative_finite(station_wait_min, "station_wait_min")

    if policy is RevisionPolicyId.BUS_ONLY:
        return PassengerAllocation(demand=demand, direct_bus=demand)

    if policy is RevisionPolicyId.STATIC_MULTIMODAL:
        if rail is RailStatus.UNAVAILABLE:
            return PassengerAllocation(demand=demand, incomplete=demand)
        return PassengerAllocation(demand=demand, rail=demand)

    if policy is RevisionPolicyId.PRECHECK_SWITCH:
        if rail is RailStatus.UNAVAILABLE:
            return PassengerAllocation(demand=demand, direct_bus=demand)
        return PassengerAllocation(demand=demand, rail=demand)

    if policy is RevisionPolicyId.SPLIT_600_400:
        definition = POLICY_DEFINITIONS[policy]
        numerator = definition.rail_share_numerator
        denominator = definition.rail_share_denominator
        if numerator is None or denominator is None:
            raise RuntimeError("split policy is missing rail share")
        rail_passengers = demand * numerator // denominator
        direct_passengers = demand - rail_passengers
        if rail is RailStatus.UNAVAILABLE:
            return PassengerAllocation(
                demand=demand,
                direct_bus=direct_passengers,
                incomplete=rail_passengers,
            )
        return PassengerAllocation(
            demand=demand,
            direct_bus=direct_passengers,
            rail=rail_passengers,
        )

    definition = POLICY_DEFINITIONS[policy]
    threshold = definition.fallback_after_min
    if threshold is None:
        raise RuntimeError("station fallback policy is missing threshold")
    if rail is not RailStatus.UNAVAILABLE:
        return PassengerAllocation(demand=demand, rail=demand)
    if wait < threshold:
        return PassengerAllocation(demand=demand, station_waiting=demand)
    return PassengerAllocation(demand=demand, station_bus=demand)


def _coerce_enum(enum_type, value, label: str):
    try:
        return enum_type(value)
    except (TypeError, ValueError) as exc:
        available = [member.value for member in enum_type]
        raise ValueError(f"{label} must be one of {available}, got {value!r}") from exc


def _require_nonnegative_integer(value: int, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an integer")
    if value < 0:
        raise ValueError(f"{label} must be non-negative")


def _require_nonnegative_finite(value: float, label: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be numeric")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be numeric") from exc
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite")
    if number < 0:
        raise ValueError(f"{label} must be non-negative")
    return number


__all__ = [
    "POLICY_DEFINITIONS",
    "PassengerAllocation",
    "RailStatus",
    "ResourceFrameId",
    "RevisionPolicyDefinition",
    "RevisionPolicyId",
    "RoadFleetAllocation",
    "get_policy_definition",
    "resolve_passenger_allocation",
    "resolve_road_fleet",
]
