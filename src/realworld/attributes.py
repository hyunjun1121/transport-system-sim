"""Deterministic road-attribute mapping for OSM-style edges.

The simulator needs a small, stable set of edge fields: ``t0`` in minutes,
``capacity`` in vehicles/hour, ``base_p_fail`` as a disruption probability
proxy, and ``mode``. OSM road data are often incomplete or encoded as strings
and lists, so this module keeps all fallback values explicit and deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from re import findall
from typing import Any, Mapping


MPH_TO_KPH = 1.609344
DEFAULT_HIGHWAY = "unclassified"
DEFAULT_LENGTH_M = 100.0


@dataclass(frozen=True)
class RoadClassDefaults:
    """Default simulator proxies for an OSM highway class."""

    speed_kph: float
    capacity: float
    base_p_fail: float


# Korean urban road defaults derived from:
# - Road Traffic Act (도로교통법) Enforcement Regulations Art. 19 for legal speed limits
# - Korea HCM 2004 (도로용량편람) for capacity values
# - MOLIT Road Design Standards (도로설계기준) for design speeds
# - Suh et al. 1990, Seoul field capacity measurements
# - Kim & Jung 2021, Seoul urban speed limit study
# Speeds reflect urban Seoul posting practice; capacities from Korea HCM classes.
# Capacities are directional proxy values used by the BPR congestion model.
HIGHWAY_DEFAULTS: dict[str, RoadClassDefaults] = {
    "motorway": RoadClassDefaults(speed_kph=100.0, capacity=2100.0, base_p_fail=0.010),
    "motorway_link": RoadClassDefaults(speed_kph=60.0, capacity=1200.0, base_p_fail=0.020),
    "trunk": RoadClassDefaults(speed_kph=60.0, capacity=1700.0, base_p_fail=0.015),
    "trunk_link": RoadClassDefaults(speed_kph=40.0, capacity=900.0, base_p_fail=0.025),
    "primary": RoadClassDefaults(speed_kph=50.0, capacity=1300.0, base_p_fail=0.020),
    "primary_link": RoadClassDefaults(speed_kph=35.0, capacity=750.0, base_p_fail=0.030),
    "secondary": RoadClassDefaults(speed_kph=40.0, capacity=1000.0, base_p_fail=0.025),
    "secondary_link": RoadClassDefaults(speed_kph=30.0, capacity=600.0, base_p_fail=0.035),
    "tertiary": RoadClassDefaults(speed_kph=30.0, capacity=750.0, base_p_fail=0.030),
    "tertiary_link": RoadClassDefaults(speed_kph=25.0, capacity=450.0, base_p_fail=0.040),
    "unclassified": RoadClassDefaults(speed_kph=30.0, capacity=500.0, base_p_fail=0.040),
    "residential": RoadClassDefaults(speed_kph=30.0, capacity=400.0, base_p_fail=0.040),
    "living_street": RoadClassDefaults(speed_kph=10.0, capacity=100.0, base_p_fail=0.050),
    "service": RoadClassDefaults(speed_kph=20.0, capacity=200.0, base_p_fail=0.050),
    "track": RoadClassDefaults(speed_kph=15.0, capacity=100.0, base_p_fail=0.060),
    "road": RoadClassDefaults(speed_kph=30.0, capacity=500.0, base_p_fail=0.040),
}

# Bus-oriented regional movement should not silently route over OSM pedestrian,
# cycling, platform, or minor internal-service geometries. The mapper can still
# normalize those tags for diagnostics, but the real-world adapter filters them
# before building simulator routes.
DEFAULT_ROUTEABLE_HIGHWAY_CLASSES = frozenset(
    highway
    for highway in HIGHWAY_DEFAULTS
    if highway not in {"service", "track", "living_street"}
)


def map_osm_edge_attributes(
    edge_data: Mapping[str, Any] | None,
    *,
    edge_id: Any | None = None,
    source: str = "osm",
    default_length_m: float = DEFAULT_LENGTH_M,
    highway_defaults: Mapping[str, RoadClassDefaults] | None = None,
) -> dict[str, Any]:
    """Map OSM-style edge attributes to simulator-ready edge attributes.

    Missing or unparseable OSM values fall back as follows:

    - ``highway``: ``unclassified``
    - ``maxspeed``: default speed for the selected highway class
    - ``length``: ``default_length_m``, 100 m unless overridden
    - ``capacity`` and ``base_p_fail``: default proxy values for the selected
      highway class

    If a list/tuple is supplied for ``highway``, the most conservative known
    road class is selected by lower speed, then lower capacity, then higher
    failure probability. If a list/tuple is supplied for ``maxspeed``, the
    lowest parseable positive speed is used.
    """

    attrs = dict(edge_data or {})
    default_length_m = _require_positive_finite(default_length_m, "default_length_m")
    defaults_by_highway = dict(highway_defaults or HIGHWAY_DEFAULTS)

    assumptions: list[str] = []
    highway, highway_defaulted = normalize_highway(attrs.get("highway"))
    if highway_defaulted:
        assumptions.append("highway")

    defaults = defaults_by_highway.get(highway, HIGHWAY_DEFAULTS[highway])

    speed_kph = parse_speed_kph(attrs.get("maxspeed"))
    if speed_kph is None:
        speed_kph = defaults.speed_kph
        assumptions.append("speed_kph")

    length_m = parse_length_m(attrs.get("length"))
    if length_m is None:
        length_m = default_length_m
        assumptions.append("length_m")

    capacity = parse_positive_float(attrs.get("capacity"))
    if capacity is None:
        capacity = defaults.capacity
        assumptions.append("capacity")

    base_p_fail_value = attrs.get("base_p_fail", attrs.get("p_fail"))
    if base_p_fail_value is None:
        base_p_fail_value = defaults.base_p_fail
        assumptions.append("base_p_fail")
    base_p_fail = _parse_probability(base_p_fail_value, "base_p_fail")

    t0 = travel_time_min(length_m=length_m, speed_kph=speed_kph)

    mapped: dict[str, Any] = {
        "t0": t0,
        "capacity": capacity,
        "base_p_fail": base_p_fail,
        "p_fail": base_p_fail,
        "mode": str(attrs.get("mode", "road") or "road"),
        "length_m": length_m,
        "speed_kph": speed_kph,
        "highway": highway,
        "source": str(attrs.get("source", source) or source),
        "attribute_assumptions": tuple(assumptions),
    }

    realworld_edge_id = _realworld_edge_id(attrs, edge_id)
    if realworld_edge_id is not None:
        mapped["realworld_edge_id"] = realworld_edge_id

    if "geometry" in attrs:
        mapped["geometry"] = attrs["geometry"]

    _validate_mapped_attributes(mapped)
    return mapped


def normalize_highway(value: Any) -> tuple[str, bool]:
    """Return ``(highway_class, defaulted)`` for an OSM highway value."""

    candidates = [
        str(item).strip().lower()
        for item in _flatten_values(value)
        if str(item).strip().lower() in HIGHWAY_DEFAULTS
    ]
    if not candidates:
        return DEFAULT_HIGHWAY, True

    highway = min(candidates, key=_highway_conservative_key)
    return highway, False


def is_routeable_vehicle_highway(
    value: Any,
    *,
    allowed_classes: frozenset[str] | set[str] | tuple[str, ...] | list[str] | None = None,
) -> bool:
    """Return true when an OSM highway value is usable by the simulator.

    The real-world route adapter uses this as an explicit guard before mapping
    OSM edges. Unknown classes such as ``footway`` and ``cycleway`` are not
    allowed to fall through as default ``unclassified`` vehicle links.
    """

    allowed = (
        DEFAULT_ROUTEABLE_HIGHWAY_CLASSES
        if allowed_classes is None
        else frozenset(str(item).strip().lower() for item in allowed_classes)
    )
    return any(
        str(item).strip().lower() in allowed
        for item in _flatten_values(value)
    )


def parse_speed_kph(value: Any) -> float | None:
    """Parse an OSM ``maxspeed`` value into kph.

    Numeric values and numeric strings are treated as kph. Strings containing
    ``mph`` are converted to kph. For list-like values, the lowest parseable
    positive speed is returned.
    """

    speeds: list[float] = []
    for item in _flatten_values(value):
        speeds.extend(_parse_speed_item(item))
    if not speeds:
        return None
    return min(speeds)


def parse_length_m(value: Any) -> float | None:
    """Parse an OSM edge length in meters.

    OSMnx usually stores ``length`` as a scalar meter value. If a list-like
    value appears, the largest positive finite candidate is used to avoid
    understating traversal time.
    """

    lengths = [parsed for item in _flatten_values(value) if (parsed := parse_positive_float(item))]
    if not lengths:
        return None
    return max(lengths)


def parse_positive_float(value: Any) -> float | None:
    """Return a positive finite float, or ``None`` when parsing fails."""

    if isinstance(value, bool) or value is None:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if parsed > 0.0 and isfinite(parsed):
        return parsed
    return None


def travel_time_min(*, length_m: float, speed_kph: float) -> float:
    """Return free-flow travel time in minutes."""

    length_m = _require_positive_finite(length_m, "length_m")
    speed_kph = _require_positive_finite(speed_kph, "speed_kph")
    return length_m / (speed_kph * 1000.0 / 60.0)


def _parse_speed_item(value: Any) -> list[float]:
    if isinstance(value, bool) or value is None:
        return []
    if isinstance(value, (int, float)):
        parsed = parse_positive_float(value)
        return [] if parsed is None else [parsed]

    text = str(value).strip().lower()
    if not text:
        return []

    multiplier = MPH_TO_KPH if "mph" in text else 1.0
    speeds: list[float] = []
    for token in findall(r"\d+(?:\.\d+)?", text):
        parsed = parse_positive_float(token)
        if parsed is not None:
            speeds.append(parsed * multiplier)
    return speeds


def _flatten_values(value: Any) -> tuple[Any, ...]:
    if value is None:
        return ()
    if isinstance(value, (list, tuple, set, frozenset)):
        flattened: list[Any] = []
        for item in value:
            flattened.extend(_flatten_values(item))
        return tuple(flattened)
    return (value,)


def _highway_conservative_key(highway: str) -> tuple[float, float, float, str]:
    defaults = HIGHWAY_DEFAULTS[highway]
    return (defaults.speed_kph, defaults.capacity, -defaults.base_p_fail, highway)


def _parse_probability(value: Any, field_name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be a finite probability, got {value!r}")
    try:
        probability = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a finite probability, got {value!r}") from exc
    if not isfinite(probability) or not 0.0 <= probability <= 1.0:
        raise ValueError(f"{field_name} must satisfy 0 <= p <= 1, got {value!r}")
    return probability


def _require_positive_finite(value: float, field_name: str) -> float:
    parsed = parse_positive_float(value)
    if parsed is None:
        raise ValueError(f"{field_name} must be positive and finite, got {value!r}")
    return parsed


def _realworld_edge_id(attrs: Mapping[str, Any], edge_id: Any | None) -> str | None:
    candidate = edge_id
    for key in ("realworld_edge_id", "osmid", "id"):
        if candidate is None and key in attrs:
            candidate = attrs[key]

    if candidate is None:
        return None
    if isinstance(candidate, (list, tuple)):
        return ",".join(str(item) for item in candidate)
    if isinstance(candidate, (set, frozenset)):
        return ",".join(sorted(str(item) for item in candidate))
    return str(candidate)


def _validate_mapped_attributes(mapped: Mapping[str, Any]) -> None:
    _require_positive_finite(float(mapped["t0"]), "t0")
    _require_positive_finite(float(mapped["capacity"]), "capacity")
    _parse_probability(mapped["base_p_fail"], "base_p_fail")


map_edge_attributes = map_osm_edge_attributes
map_road_attributes = map_osm_edge_attributes
normalize_edge_attributes = map_osm_edge_attributes


__all__ = [
    "DEFAULT_HIGHWAY",
    "DEFAULT_LENGTH_M",
    "HIGHWAY_DEFAULTS",
    "DEFAULT_ROUTEABLE_HIGHWAY_CLASSES",
    "RoadClassDefaults",
    "is_routeable_vehicle_highway",
    "map_edge_attributes",
    "map_osm_edge_attributes",
    "map_road_attributes",
    "normalize_edge_attributes",
    "normalize_highway",
    "parse_length_m",
    "parse_positive_float",
    "parse_speed_kph",
    "travel_time_min",
]
