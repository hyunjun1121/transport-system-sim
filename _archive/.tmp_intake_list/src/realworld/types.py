"""Typed records and validators for real-world region specifications."""

from __future__ import annotations

from dataclasses import dataclass
import math
import operator
from typing import Any, Mapping


MetadataValue = str | int | float | bool | None
Metadata = dict[str, MetadataValue]


def _require_mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{path} must be a mapping")
    return value


def _require_string(value: Any, path: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{path} must be a string")
    text = value.strip()
    if not text:
        raise ValueError(f"{path} must be non-empty")
    return text


def _require_optional_string(value: Any, path: str) -> str | None:
    if value is None:
        return None
    return _require_string(value, path)


def _require_finite_number(value: Any, path: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{path} must be a finite number")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{path} must be a finite number") from exc
    if not math.isfinite(number):
        raise ValueError(f"{path} must be a finite number")
    return number


def _require_positive_number(value: Any, path: str) -> float:
    number = _require_finite_number(value, path)
    if number <= 0.0:
        raise ValueError(f"{path} must be positive")
    return number


def _require_int_at_least(value: Any, path: str, minimum: int) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{path} must be an integer")
    try:
        integer = operator.index(value)
    except TypeError:
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{path} must be an integer") from exc
        if not math.isfinite(number) or not number.is_integer():
            raise ValueError(f"{path} must be an integer")
        integer = int(number)

    if integer < minimum:
        raise ValueError(f"{path} must be at least {minimum}")
    return int(integer)


def _require_lat(value: Any, path: str) -> float:
    lat = _require_finite_number(value, path)
    if lat < -90.0 or lat > 90.0:
        raise ValueError(f"{path} must be between -90 and 90")
    return lat


def _require_lon(value: Any, path: str) -> float:
    lon = _require_finite_number(value, path)
    if lon < -180.0 or lon > 180.0:
        raise ValueError(f"{path} must be between -180 and 180")
    return lon


def validate_metadata(value: Any | None, path: str = "metadata") -> Metadata:
    """Return a normalized metadata mapping with scalar YAML/JSON values."""

    if value is None:
        return {}
    mapping = _require_mapping(value, path)
    normalized: Metadata = {}
    for key, item in mapping.items():
        key_path = f"{path}.{key}"
        text_key = _require_string(key, f"{path} key")
        if not isinstance(item, (str, int, float, bool)) and item is not None:
            raise ValueError(f"{key_path} must be a scalar metadata value")
        if isinstance(item, float) and not math.isfinite(item):
            raise ValueError(f"{key_path} must be finite when numeric")
        normalized[text_key] = item
    return normalized


@dataclass(frozen=True)
class BoundarySpec:
    """A rectangular extraction boundary in WGS84 coordinates."""

    type: str
    north: float
    south: float
    east: float
    west: float

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any], path: str = "boundary") -> "BoundarySpec":
        mapping = _require_mapping(value, path)
        boundary_type = _require_string(mapping.get("type"), f"{path}.type")
        if boundary_type != "bbox":
            raise ValueError(f"{path}.type must be 'bbox'")
        return cls(
            type=boundary_type,
            north=_require_lat(mapping.get("north"), f"{path}.north"),
            south=_require_lat(mapping.get("south"), f"{path}.south"),
            east=_require_lon(mapping.get("east"), f"{path}.east"),
            west=_require_lon(mapping.get("west"), f"{path}.west"),
        )

    def __post_init__(self) -> None:
        if self.type != "bbox":
            raise ValueError("boundary.type must be 'bbox'")
        north = _require_lat(self.north, "boundary.north")
        south = _require_lat(self.south, "boundary.south")
        east = _require_lon(self.east, "boundary.east")
        west = _require_lon(self.west, "boundary.west")
        if north <= south:
            raise ValueError("boundary.north must be greater than boundary.south")
        if east <= west:
            raise ValueError("boundary.east must be greater than boundary.west")
        object.__setattr__(self, "north", north)
        object.__setattr__(self, "south", south)
        object.__setattr__(self, "east", east)
        object.__setattr__(self, "west", west)

    def contains(self, lat: float, lon: float) -> bool:
        """Return whether a coordinate falls inside or on the bbox."""

        return self.south <= lat <= self.north and self.west <= lon <= self.east

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        """Return bounds as ``(west, south, east, north)``."""

        return (self.west, self.south, self.east, self.north)


@dataclass(frozen=True)
class ZoneSpec:
    """A mobilization assembly or destination zone centroid."""

    id: str
    lat: float
    lon: float
    name: str | None = None
    metadata: Metadata | None = None

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any], path: str) -> "ZoneSpec":
        mapping = _require_mapping(value, path)
        return cls(
            id=_require_string(mapping.get("id"), f"{path}.id"),
            lat=_require_lat(mapping.get("lat"), f"{path}.lat"),
            lon=_require_lon(mapping.get("lon"), f"{path}.lon"),
            name=_require_optional_string(mapping.get("name"), f"{path}.name"),
            metadata=validate_metadata(mapping.get("metadata"), f"{path}.metadata"),
        )

    def __post_init__(self) -> None:
        object.__setattr__(self, "id", _require_string(self.id, "zone.id"))
        object.__setattr__(self, "lat", _require_lat(self.lat, f"zone {self.id}.lat"))
        object.__setattr__(self, "lon", _require_lon(self.lon, f"zone {self.id}.lon"))
        object.__setattr__(self, "name", _require_optional_string(self.name, f"zone {self.id}.name"))
        object.__setattr__(self, "metadata", validate_metadata(self.metadata, f"zone {self.id}.metadata"))


@dataclass(frozen=True)
class RailPointSpec:
    """A rail access or egress point used by the current simulator."""

    id: str
    lat: float
    lon: float
    name: str | None = None
    metadata: Metadata | None = None

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any], path: str) -> "RailPointSpec":
        mapping = _require_mapping(value, path)
        return cls(
            id=_require_string(mapping.get("id"), f"{path}.id"),
            lat=_require_lat(mapping.get("lat"), f"{path}.lat"),
            lon=_require_lon(mapping.get("lon"), f"{path}.lon"),
            name=_require_optional_string(mapping.get("name"), f"{path}.name"),
            metadata=validate_metadata(mapping.get("metadata"), f"{path}.metadata"),
        )

    def __post_init__(self) -> None:
        object.__setattr__(self, "id", _require_string(self.id, "rail point.id"))
        object.__setattr__(self, "lat", _require_lat(self.lat, f"rail point {self.id}.lat"))
        object.__setattr__(self, "lon", _require_lon(self.lon, f"rail point {self.id}.lon"))
        object.__setattr__(
            self,
            "name",
            _require_optional_string(self.name, f"rail point {self.id}.name"),
        )
        object.__setattr__(
            self,
            "metadata",
            validate_metadata(self.metadata, f"rail point {self.id}.metadata"),
        )


@dataclass(frozen=True)
class RailSpec:
    """Fixed-headway rail service inputs for the regional pipeline."""

    access: RailPointSpec
    egress: RailPointSpec
    travel_time_min: float
    headway_min: float
    capacity_pax_per_train: int
    metadata: Metadata | None = None

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any], path: str = "rail") -> "RailSpec":
        mapping = _require_mapping(value, path)
        return cls(
            access=RailPointSpec.from_mapping(mapping.get("access"), f"{path}.access"),
            egress=RailPointSpec.from_mapping(mapping.get("egress"), f"{path}.egress"),
            travel_time_min=_require_positive_number(
                mapping.get("travel_time_min"),
                f"{path}.travel_time_min",
            ),
            headway_min=_require_positive_number(mapping.get("headway_min"), f"{path}.headway_min"),
            capacity_pax_per_train=_require_int_at_least(
                mapping.get("capacity_pax_per_train"),
                f"{path}.capacity_pax_per_train",
                1,
            ),
            metadata=validate_metadata(mapping.get("metadata"), f"{path}.metadata"),
        )

    def __post_init__(self) -> None:
        if not isinstance(self.access, RailPointSpec):
            raise ValueError("rail.access must be a RailPointSpec")
        if not isinstance(self.egress, RailPointSpec):
            raise ValueError("rail.egress must be a RailPointSpec")
        object.__setattr__(
            self,
            "travel_time_min",
            _require_positive_number(self.travel_time_min, "rail.travel_time_min"),
        )
        object.__setattr__(
            self,
            "headway_min",
            _require_positive_number(self.headway_min, "rail.headway_min"),
        )
        object.__setattr__(
            self,
            "capacity_pax_per_train",
            _require_int_at_least(
                self.capacity_pax_per_train,
                "rail.capacity_pax_per_train",
                1,
            ),
        )
        object.__setattr__(self, "metadata", validate_metadata(self.metadata, "rail.metadata"))


@dataclass(frozen=True)
class RegionSpec:
    """Validated region, zone, and rail-service inputs."""

    region_id: str
    name: str
    boundary: BoundarySpec
    assembly_zones: tuple[ZoneSpec, ...]
    destination_zones: tuple[ZoneSpec, ...]
    rail: RailSpec
    metadata: Metadata | None = None

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any], path: str = "region") -> "RegionSpec":
        mapping = _require_mapping(value, path)
        return cls(
            region_id=_require_string(mapping.get("region_id"), f"{path}.region_id"),
            name=_require_string(mapping.get("name"), f"{path}.name"),
            boundary=BoundarySpec.from_mapping(mapping.get("boundary"), f"{path}.boundary"),
            assembly_zones=_load_zones(mapping.get("assembly_zones"), f"{path}.assembly_zones"),
            destination_zones=_load_zones(
                mapping.get("destination_zones"),
                f"{path}.destination_zones",
            ),
            rail=RailSpec.from_mapping(mapping.get("rail"), f"{path}.rail"),
            metadata=validate_metadata(mapping.get("metadata"), f"{path}.metadata"),
        )

    def __post_init__(self) -> None:
        object.__setattr__(self, "region_id", _require_string(self.region_id, "region.region_id"))
        object.__setattr__(self, "name", _require_string(self.name, "region.name"))
        if not isinstance(self.boundary, BoundarySpec):
            raise ValueError("region.boundary must be a BoundarySpec")
        object.__setattr__(
            self,
            "assembly_zones",
            _validate_zone_tuple(self.assembly_zones, "region.assembly_zones"),
        )
        object.__setattr__(
            self,
            "destination_zones",
            _validate_zone_tuple(self.destination_zones, "region.destination_zones"),
        )
        if not isinstance(self.rail, RailSpec):
            raise ValueError("region.rail must be a RailSpec")
        object.__setattr__(self, "metadata", validate_metadata(self.metadata, "region.metadata"))
        _validate_unique_ids(self)
        _validate_points_inside_boundary(self)

    @property
    def primary_assembly(self) -> ZoneSpec:
        """Return the first assembly zone, normally simulator node ``A``."""

        return self.assembly_zones[0]

    @property
    def primary_destination(self) -> ZoneSpec:
        """Return the first destination zone, normally simulator node ``D``."""

        return self.destination_zones[0]

    @property
    def primary_assembly_id(self) -> str:
        return self.primary_assembly.id

    @property
    def primary_destination_id(self) -> str:
        return self.primary_destination.id

    @property
    def rail_access_id(self) -> str:
        return self.rail.access.id

    @property
    def rail_egress_id(self) -> str:
        return self.rail.egress.id

    @property
    def canonical_ids(self) -> tuple[str, str, str, str]:
        """Return simulator-friendly IDs as ``(assembly, destination, access, egress)``."""

        return (
            self.primary_assembly_id,
            self.primary_destination_id,
            self.rail_access_id,
            self.rail_egress_id,
        )

    @property
    def simulator_node_ids(self) -> dict[str, str]:
        """Return named node IDs for adapter and validation modules."""

        return {
            "assembly": self.primary_assembly_id,
            "destination": self.primary_destination_id,
            "rail_access": self.rail_access_id,
            "rail_egress": self.rail_egress_id,
        }


def _load_zones(value: Any, path: str) -> tuple[ZoneSpec, ...]:
    if isinstance(value, Mapping):
        return (ZoneSpec.from_mapping(value, path),)
    if isinstance(value, (str, bytes)) or not isinstance(value, list | tuple):
        raise ValueError(f"{path} must be a non-empty list of zone mappings")
    if not value:
        raise ValueError(f"{path} must contain at least one zone")
    return tuple(ZoneSpec.from_mapping(item, f"{path}[{index}]") for index, item in enumerate(value))


def _validate_zone_tuple(value: Any, path: str) -> tuple[ZoneSpec, ...]:
    if isinstance(value, ZoneSpec):
        zones = (value,)
    elif isinstance(value, tuple):
        zones = value
    elif isinstance(value, list):
        zones = tuple(value)
    else:
        raise ValueError(f"{path} must contain ZoneSpec records")

    if not zones:
        raise ValueError(f"{path} must contain at least one zone")
    for index, zone in enumerate(zones):
        if not isinstance(zone, ZoneSpec):
            raise ValueError(f"{path}[{index}] must be a ZoneSpec")
    return zones


def _validate_unique_ids(region: RegionSpec) -> None:
    ids = [
        *(zone.id for zone in region.assembly_zones),
        *(zone.id for zone in region.destination_zones),
        region.rail.access.id,
        region.rail.egress.id,
    ]
    seen: set[str] = set()
    duplicates: list[str] = []
    for node_id in ids:
        if node_id in seen and node_id not in duplicates:
            duplicates.append(node_id)
        seen.add(node_id)
    if duplicates:
        raise ValueError(f"region node IDs must be unique; duplicates: {', '.join(duplicates)}")


def _validate_points_inside_boundary(region: RegionSpec) -> None:
    points = [
        *((f"assembly_zones[{index}]", zone.lat, zone.lon) for index, zone in enumerate(region.assembly_zones)),
        *(
            (f"destination_zones[{index}]", zone.lat, zone.lon)
            for index, zone in enumerate(region.destination_zones)
        ),
        ("rail.access", region.rail.access.lat, region.rail.access.lon),
        ("rail.egress", region.rail.egress.lat, region.rail.egress.lon),
    ]
    for path, lat, lon in points:
        if not region.boundary.contains(lat, lon):
            raise ValueError(f"{path} must fall inside region.boundary")


__all__ = [
    "BoundarySpec",
    "Metadata",
    "MetadataValue",
    "RailPointSpec",
    "RailSpec",
    "RegionSpec",
    "ZoneSpec",
    "validate_metadata",
]
