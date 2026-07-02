"""Typed records and validators for real-world region specifications."""

from __future__ import annotations

from dataclasses import dataclass
import math
import operator
from typing import Any, Mapping


MetadataValue = str | int | float | bool | None
Metadata = dict[str, MetadataValue]
ALLOWED_BOUNDARY_TYPES = frozenset({"bbox", "polygon"})
ALLOWED_SENSITIVITY_LEVELS = frozenset(
    {
        "unspecified",
        "non_sensitive",
        "public",
        "synthetic",
        "privacy_review_required",
        "sensitive_review_required",
        "restricted",
    }
)
# Sensitivity levels permitted for mobilization corridors. The data type
# (ALLOWED_SENSITIVITY_LEVELS) accepts restricted / review-pending records so
# they can be CARRIED, but the simulator's public-coordinate policy REJECTS
# them before any mode/corridor expansion (no military unit coordinates, OOB,
# or movement schedules). See assert_public_coordinate_policy.
PUBLIC_COORDINATE_LEVELS = frozenset(
    {"unspecified", "non_sensitive", "public", "synthetic"}
)
# Coordinate classes permitted on a service port (station / port / airfield)
# and on the region ``metadata.coordinate_class`` marker. Mobilization
# corridors use only public administrative centroids / public transport
# networks, or declared synthetic fixtures — never military-unit coordinates,
# OOB, or movement schedules. Enforced at ``PortPointSpec`` construction AND by
# the public-coordinate policy guard (see ``assert_public_coordinate_policy``).
ALLOWED_PORT_COORDINATE_CLASSES = frozenset({"public", "synthetic"})


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
    """An extraction boundary in WGS84 coordinates.

    Polygon boundaries are represented by a polygon artifact path plus a bbox
    envelope. The envelope keeps current fast point and graph checks stable
    until polygon geometry validation is introduced.
    """

    type: str
    north: float
    south: float
    east: float
    west: float
    polygon_path: str | None = None

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any], path: str = "boundary") -> "BoundarySpec":
        mapping = _require_mapping(value, path)
        boundary_type = _require_string(mapping.get("type"), f"{path}.type")
        if boundary_type not in ALLOWED_BOUNDARY_TYPES:
            raise ValueError(f"{path}.type must be 'bbox' or 'polygon'")
        return cls(
            type=boundary_type,
            north=_require_lat(mapping.get("north"), f"{path}.north"),
            south=_require_lat(mapping.get("south"), f"{path}.south"),
            east=_require_lon(mapping.get("east"), f"{path}.east"),
            west=_require_lon(mapping.get("west"), f"{path}.west"),
            polygon_path=_require_optional_string(
                mapping.get("polygon_path"),
                f"{path}.polygon_path",
            ),
        )

    def __post_init__(self) -> None:
        if self.type not in ALLOWED_BOUNDARY_TYPES:
            raise ValueError("boundary.type must be 'bbox' or 'polygon'")
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
        if self.type == "polygon":
            object.__setattr__(
                self,
                "polygon_path",
                _require_string(self.polygon_path, "boundary.polygon_path"),
            )
        else:
            object.__setattr__(
                self,
                "polygon_path",
                _require_optional_string(self.polygon_path, "boundary.polygon_path"),
            )

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
class SourceRefSpec:
    """A review-aid reference to one source provenance record."""

    source_id: str
    role: str
    local_artifact_path: str | None = None
    review_status: str | None = None

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any], path: str) -> "SourceRefSpec":
        mapping = _require_mapping(value, path)
        return cls(
            source_id=_require_string(mapping.get("source_id"), f"{path}.source_id"),
            role=_require_string(mapping.get("role"), f"{path}.role"),
            local_artifact_path=_require_optional_string(
                mapping.get("local_artifact_path"),
                f"{path}.local_artifact_path",
            ),
            review_status=_require_optional_string(
                mapping.get("review_status"),
                f"{path}.review_status",
            ),
        )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "source_id",
            _require_string(self.source_id, "source_ref.source_id"),
        )
        object.__setattr__(self, "role", _require_string(self.role, "source_ref.role"))
        object.__setattr__(
            self,
            "local_artifact_path",
            _require_optional_string(
                self.local_artifact_path,
                f"source_ref {self.source_id}.local_artifact_path",
            ),
        )
        object.__setattr__(
            self,
            "review_status",
            _require_optional_string(
                self.review_status,
                f"source_ref {self.source_id}.review_status",
            ),
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


ALLOWED_SERVICE_MODES = frozenset({"rail", "sea", "air"})
ALLOWED_FUEL_TYPES = frozenset({"electric", "diesel", "lng", "none", "unspecified"})


@dataclass(frozen=True)
class PortPointSpec:
    """A mode-agnostic service access or egress port (station / port / airfield).

    Generalizes ``RailPointSpec`` for the multi-service contract (rail / sea /
    air). ``coordinate_class`` defaults to ``public`` and must be one of
    ``ALLOWED_PORT_COORDINATE_CLASSES`` (``public`` administrative centroid or
    a declared ``synthetic`` fixture); a non-public coordinate class (e.g.
    ``military_unit``) is rejected at construction, before any region build or
    simulator entry. The public-coordinate policy guard is the redundant
    region-level backstop (see ``assert_public_coordinate_policy``).
    """

    id: str
    lat: float
    lon: float
    name: str | None = None
    coordinate_class: str = "public"
    metadata: Metadata | None = None

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any], path: str) -> "PortPointSpec":
        mapping = _require_mapping(value, path)
        return cls(
            id=_require_string(mapping.get("id"), f"{path}.id"),
            lat=_require_lat(mapping.get("lat"), f"{path}.lat"),
            lon=_require_lon(mapping.get("lon"), f"{path}.lon"),
            name=_require_optional_string(mapping.get("name"), f"{path}.name"),
            coordinate_class=_require_string(
                mapping.get("coordinate_class", "public"), f"{path}.coordinate_class"
            ),
            metadata=validate_metadata(mapping.get("metadata"), f"{path}.metadata"),
        )

    def __post_init__(self) -> None:
        object.__setattr__(self, "id", _require_string(self.id, "port.id"))
        object.__setattr__(self, "lat", _require_lat(self.lat, f"port {self.id}.lat"))
        object.__setattr__(self, "lon", _require_lon(self.lon, f"port {self.id}.lon"))
        object.__setattr__(
            self,
            "name",
            _require_optional_string(self.name, f"port {self.id}.name"),
        )
        coordinate_class = _require_string(
            self.coordinate_class, f"port {self.id}.coordinate_class"
        )
        if coordinate_class not in ALLOWED_PORT_COORDINATE_CLASSES:
            raise ValueError(
                f"port {self.id}.coordinate_class={coordinate_class!r}; "
                f"only {sorted(ALLOWED_PORT_COORDINATE_CLASSES)} are permitted "
                "(public administrative centroids / synthetic fixtures only; "
                "military-unit, OOB, and movement-schedule coordinates are "
                "rejected at construction)"
            )
        object.__setattr__(self, "coordinate_class", coordinate_class)
        object.__setattr__(
            self,
            "metadata",
            validate_metadata(self.metadata, f"port {self.id}.metadata"),
        )


@dataclass(frozen=True)
class RegionServiceSpec:
    """A composable transport service in a mobilization corridor.

    One ``RegionServiceSpec`` per fixed-headway service (rail / sea / air). The
    simulator composes ``assembly -> shuttle -> service.access -> service-leg ->
    service.egress -> last-mile -> destination`` for the runtime ``ServiceSpec``
    (mode / access_id / egress_id / travel / headway / capacity).

    ``fuel_type``, ``fallback``, and ``service_id`` are DECLARED-ONLY inputs
    carried for the future L3 power-loss electric->diesel rail fallback and
    service-degradation substitution (planned for Phase 3 mode leaves). They
    are validated here and otherwise inert — the current runtime does not read
    them. Sea/air run as fixed-headway services, which is a modeling proxy, not
    a validated sea/air reliability model (decision-support / sensitivity only).
    """

    mode: str
    access: PortPointSpec
    egress: PortPointSpec
    travel_time_min: float
    headway_min: float
    capacity_pax_per_unit: int
    service_id: str | None = None
    fuel_type: str | None = None
    fallback: str | None = None
    metadata: Metadata | None = None

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any], path: str) -> "RegionServiceSpec":
        mapping = _require_mapping(value, path)
        mode = _require_string(mapping.get("mode"), f"{path}.mode")
        if mode not in ALLOWED_SERVICE_MODES:
            raise ValueError(
                f"{path}.mode must be one of {sorted(ALLOWED_SERVICE_MODES)}"
            )
        return cls(
            mode=mode,
            access=PortPointSpec.from_mapping(mapping.get("access"), f"{path}.access"),
            egress=PortPointSpec.from_mapping(mapping.get("egress"), f"{path}.egress"),
            travel_time_min=_require_positive_number(
                mapping.get("travel_time_min"), f"{path}.travel_time_min"
            ),
            headway_min=_require_positive_number(
                mapping.get("headway_min"), f"{path}.headway_min"
            ),
            capacity_pax_per_unit=_require_int_at_least(
                mapping.get("capacity_pax_per_unit"),
                f"{path}.capacity_pax_per_unit",
                1,
            ),
            service_id=_require_optional_string(
                mapping.get("service_id"), f"{path}.service_id"
            ),
            fuel_type=_require_optional_string(
                mapping.get("fuel_type"), f"{path}.fuel_type"
            ),
            fallback=_require_optional_string(
                mapping.get("fallback"), f"{path}.fallback"
            ),
            metadata=validate_metadata(mapping.get("metadata"), f"{path}.metadata"),
        )

    def __post_init__(self) -> None:
        if self.mode not in ALLOWED_SERVICE_MODES:
            raise ValueError(
                f"service.mode must be one of {sorted(ALLOWED_SERVICE_MODES)}"
            )
        if not isinstance(self.access, PortPointSpec):
            raise ValueError("service.access must be a PortPointSpec")
        if not isinstance(self.egress, PortPointSpec):
            raise ValueError("service.egress must be a PortPointSpec")
        object.__setattr__(
            self,
            "travel_time_min",
            _require_positive_number(self.travel_time_min, "service.travel_time_min"),
        )
        object.__setattr__(
            self,
            "headway_min",
            _require_positive_number(self.headway_min, "service.headway_min"),
        )
        object.__setattr__(
            self,
            "capacity_pax_per_unit",
            _require_int_at_least(
                self.capacity_pax_per_unit, "service.capacity_pax_per_unit", 1
            ),
        )
        if self.fuel_type is not None and self.fuel_type not in ALLOWED_FUEL_TYPES:
            raise ValueError(
                f"service.fuel_type must be one of {sorted(ALLOWED_FUEL_TYPES)} or null"
            )
        object.__setattr__(
            self, "metadata", validate_metadata(self.metadata, "service.metadata")
        )


@dataclass(frozen=True)
class RegionSpec:
    """Validated region, zone, and service inputs."""

    region_id: str
    name: str
    boundary: BoundarySpec
    assembly_zones: tuple[ZoneSpec, ...]
    destination_zones: tuple[ZoneSpec, ...]
    region_services: tuple[RegionServiceSpec, ...]
    metadata: Metadata | None = None
    sensitivity_level: str = "unspecified"
    source_refs: tuple[SourceRefSpec, ...] = ()

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any], path: str = "region") -> "RegionSpec":
        mapping = _require_mapping(value, path)
        name_value = mapping.get("name", mapping.get("label"))
        return cls(
            region_id=_require_string(mapping.get("region_id"), f"{path}.region_id"),
            name=_require_string(name_value, f"{path}.name"),
            boundary=BoundarySpec.from_mapping(mapping.get("boundary"), f"{path}.boundary"),
            assembly_zones=_load_zones(
                _zone_alias_value(mapping, "assembly_zones", "origin_zones"),
                f"{path}.assembly_zones",
            ),
            destination_zones=_load_zones(
                mapping.get("destination_zones"),
                f"{path}.destination_zones",
            ),
            region_services=_load_region_services(mapping, f"{path}"),
            metadata=validate_metadata(mapping.get("metadata"), f"{path}.metadata"),
            sensitivity_level=_region_sensitivity_level(mapping),
            source_refs=_load_source_refs(mapping.get("source_refs"), f"{path}.source_refs"),
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
        if not isinstance(self.region_services, tuple):
            raise ValueError("region.region_services must be a tuple of RegionServiceSpec")
        object.__setattr__(
            self,
            "region_services",
            _validate_service_tuple(self.region_services, "region.region_services"),
        )
        object.__setattr__(self, "metadata", validate_metadata(self.metadata, "region.metadata"))
        object.__setattr__(
            self,
            "sensitivity_level",
            _validate_sensitivity_level(
                self.sensitivity_level,
                "region.sensitivity_level",
            ),
        )
        object.__setattr__(
            self,
            "source_refs",
            _validate_source_ref_tuple(self.source_refs, "region.source_refs"),
        )
        _validate_unique_ids(self)
        _validate_points_inside_boundary(self)
        # Security boundary (C4): enforce the public-coordinate policy at
        # construction so NO public API can bypass it. load_region_spec /
        # load_region_registry / get_region_spec / build_simulator_graph all
        # route through RegionSpec.from_mapping -> __post_init__, so a
        # restricted / sensitive / privacy-review-pending coordinate source
        # cannot ENTER the simulator under any entry path (no real-unit
        # coordinates, OOB, or movement schedules). The schema vocabulary still
        # CARRIES such levels (ALLOWED_SENSITIVITY_LEVELS) for raw-dict review
        # packets, but a validated RegionSpec is public-coordinate only.
        assert_public_coordinate_policy(self, context=f"region {self.region_id!r}")

    @property
    def label(self) -> str:
        """Return the human-readable region label."""

        return self.name

    @property
    def origin_zones(self) -> tuple[ZoneSpec, ...]:
        """Return assembly zones using the broader Phase 1 registry vocabulary."""

        return self.assembly_zones

    @property
    def primary_assembly(self) -> ZoneSpec:
        """Return the first assembly zone, normally simulator node ``A``."""

        return self.assembly_zones[0]

    @property
    def primary_destination(self) -> ZoneSpec:
        """Return the first destination zone, normally simulator node ``D``."""

        return self.destination_zones[0]

    def services_by_mode(self, mode: str) -> tuple[RegionServiceSpec, ...]:
        """Return the region's services of a given mode (rail / sea / air)."""

        return tuple(svc for svc in self.region_services if svc.mode == mode)

    @property
    def rail_service(self) -> RegionServiceSpec:
        """Return the first rail service (raises if the region has no rail)."""

        for svc in self.region_services:
            if svc.mode == "rail":
                return svc
        raise ValueError(
            f"region {self.region_id!r} has no rail service; "
            f"modes present: {[svc.mode for svc in self.region_services]}"
        )

    @property
    def rail(self) -> RailSpec:
        """Backward-compatible ``RailSpec`` view of the first rail service.

        Composes a legacy ``RailSpec`` (with ``RailPointSpec`` access/egress)
        from the first rail ``RegionServiceSpec`` so existing callers that read
        ``region.rail`` keep working after the multi-service contract widening.
        """

        svc = self.rail_service
        return RailSpec(
            access=RailPointSpec(
                id=svc.access.id,
                lat=svc.access.lat,
                lon=svc.access.lon,
                name=svc.access.name,
                metadata=svc.access.metadata,
            ),
            egress=RailPointSpec(
                id=svc.egress.id,
                lat=svc.egress.lat,
                lon=svc.egress.lon,
                name=svc.egress.name,
                metadata=svc.egress.metadata,
            ),
            travel_time_min=svc.travel_time_min,
            headway_min=svc.headway_min,
            capacity_pax_per_train=svc.capacity_pax_per_unit,
            metadata=svc.metadata,
        )

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
    def canonical_ids(self) -> tuple[str, ...]:
        """Return simulator-friendly node IDs.

        ``(assembly, destination, <service access/egress pairs in declaration
        order, rail first>)``. A single-rail region yields exactly
        ``(A, D, S, R)`` for backward compatibility; a multi-service region
        appends the extra service ports (e.g. ``(A, D, S, R, sea_acc,
        sea_egr)``).
        """

        ids: list[str] = [self.primary_assembly_id, self.primary_destination_id]
        for svc in self.region_services:
            ids.append(svc.access.id)
            ids.append(svc.egress.id)
        return tuple(ids)

    @property
    def simulator_node_ids(self) -> dict[str, str]:
        """Return named node IDs for adapter and validation modules.

        Always includes ``assembly`` / ``destination``. ``rail_access`` /
        ``rail_egress`` are emitted only when a rail service exists (a
        sea/air-only region has none). Every non-rail service emits
        ``<mode>_access`` / ``<mode>_egress``. A single-rail region yields
        exactly the legacy 4-key mapping.
        """

        nodes: dict[str, str] = {
            "assembly": self.primary_assembly_id,
            "destination": self.primary_destination_id,
        }
        rail = next((svc for svc in self.region_services if svc.mode == "rail"), None)
        if rail is not None:
            nodes["rail_access"] = rail.access.id
            nodes["rail_egress"] = rail.egress.id
        for svc in self.region_services:
            if svc.mode == "rail":
                continue
            nodes[f"{svc.mode}_access"] = svc.access.id
            nodes[f"{svc.mode}_egress"] = svc.egress.id
        return nodes


def _load_zones(value: Any, path: str) -> tuple[ZoneSpec, ...]:
    if isinstance(value, Mapping):
        return (ZoneSpec.from_mapping(value, path),)
    if isinstance(value, (str, bytes)) or not isinstance(value, list | tuple):
        raise ValueError(f"{path} must be a non-empty list of zone mappings")
    if not value:
        raise ValueError(f"{path} must contain at least one zone")
    return tuple(ZoneSpec.from_mapping(item, f"{path}[{index}]") for index, item in enumerate(value))


def _zone_alias_value(mapping: Mapping[str, Any], primary: str, alias: str) -> Any:
    if primary in mapping:
        return mapping.get(primary)
    return mapping.get(alias)


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


def _load_region_services(
    mapping: Mapping[str, Any], path: str
) -> tuple[RegionServiceSpec, ...]:
    """Load services from a ``region_services`` list or the legacy ``rail`` key.

    Backward compatibility: a region YAML may still define a top-level ``rail``
    mapping; it is normalized into a single rail ``RegionServiceSpec``. New
    multi-service regions (rail + sea + air) use the explicit
    ``region_services`` list.
    """

    if "region_services" in mapping:
        value = mapping.get("region_services")
        if isinstance(value, Mapping):
            return (
                RegionServiceSpec.from_mapping(value, f"{path}.region_services"),
            )
        if not isinstance(value, list | tuple):
            raise ValueError(
                f"{path}.region_services must be a list of service mappings"
            )
        if not value:
            raise ValueError(f"{path}.region_services must be non-empty")
        return tuple(
            RegionServiceSpec.from_mapping(item, f"{path}.region_services[{index}]")
            for index, item in enumerate(value)
        )
    if "rail" in mapping:
        return (
            _region_service_from_legacy_rail(mapping.get("rail"), f"{path}.rail"),
        )
    raise ValueError(f"{path} must define region_services or a legacy rail service")


def _region_service_from_legacy_rail(
    value: Mapping[str, Any], path: str
) -> RegionServiceSpec:
    """Normalize a legacy ``rail`` mapping into a rail ``RegionServiceSpec``."""

    rail = RailSpec.from_mapping(value, path)
    # RailPointSpec has no coordinate_class field, so a hostile
    # coordinate_class on a legacy ``rail.access``/``rail.egress`` mapping would
    # otherwise be silently dropped (port normalized to 'public') — diverging
    # from the region_services path, which rejects it loudly. Forward the raw
    # marker so PortPointSpec.__post_init__ validates it the same way.
    access_raw = _require_mapping(value.get("access"), f"{path}.access")
    egress_raw = _require_mapping(value.get("egress"), f"{path}.egress")
    return RegionServiceSpec(
        mode="rail",
        access=PortPointSpec(
            id=rail.access.id,
            lat=rail.access.lat,
            lon=rail.access.lon,
            name=rail.access.name,
            coordinate_class=access_raw.get("coordinate_class", "public"),
            metadata=rail.access.metadata,
        ),
        egress=PortPointSpec(
            id=rail.egress.id,
            lat=rail.egress.lat,
            lon=rail.egress.lon,
            name=rail.egress.name,
            coordinate_class=egress_raw.get("coordinate_class", "public"),
            metadata=rail.egress.metadata,
        ),
        travel_time_min=rail.travel_time_min,
        headway_min=rail.headway_min,
        capacity_pax_per_unit=rail.capacity_pax_per_train,
        metadata=rail.metadata,
    )


def _validate_service_tuple(
    value: Any, path: str
) -> tuple[RegionServiceSpec, ...]:
    if isinstance(value, RegionServiceSpec):
        services = (value,)
    elif isinstance(value, tuple):
        services = value
    elif isinstance(value, list):
        services = tuple(value)
    else:
        raise ValueError(f"{path} must contain RegionServiceSpec records")
    if not services:
        raise ValueError(f"{path} must contain at least one service")
    for index, svc in enumerate(services):
        if not isinstance(svc, RegionServiceSpec):
            raise ValueError(f"{path}[{index}] must be a RegionServiceSpec")
    # At most one service per mode: the simulator resolves a single
    # fixed-headway ServiceSpec per run and keys simulator_node_ids by mode, so
    # two same-mode services would silently collide (last-wins, first port
    # evaporates) and produce ambiguous boundary error labels.
    modes_seen: set[str] = set()
    duplicate_modes: list[str] = []
    for svc in services:
        if svc.mode in modes_seen and svc.mode not in duplicate_modes:
            duplicate_modes.append(svc.mode)
        modes_seen.add(svc.mode)
    if duplicate_modes:
        raise ValueError(
            f"{path} must contain at most one service per mode; duplicate "
            f"modes: {', '.join(duplicate_modes)} (use distinct modes "
            "rail / sea / air, or split corridors across regions)"
        )
    return services


def _load_source_refs(value: Any | None, path: str) -> tuple[SourceRefSpec, ...]:
    if value is None:
        return ()
    if isinstance(value, Mapping):
        return (SourceRefSpec.from_mapping(value, path),)
    if isinstance(value, (str, bytes)) or not isinstance(value, list | tuple):
        raise ValueError(f"{path} must be a list of source reference mappings")
    return tuple(
        SourceRefSpec.from_mapping(item, f"{path}[{index}]")
        for index, item in enumerate(value)
    )


def _validate_source_ref_tuple(value: Any, path: str) -> tuple[SourceRefSpec, ...]:
    if isinstance(value, SourceRefSpec):
        refs = (value,)
    elif isinstance(value, tuple):
        refs = value
    elif isinstance(value, list):
        refs = tuple(value)
    else:
        raise ValueError(f"{path} must contain SourceRefSpec records")
    for index, source_ref in enumerate(refs):
        if not isinstance(source_ref, SourceRefSpec):
            raise ValueError(f"{path}[{index}] must be a SourceRefSpec")
    return refs


def _region_sensitivity_level(mapping: Mapping[str, Any]) -> str:
    if "sensitivity_level" in mapping:
        return _require_string(mapping.get("sensitivity_level"), "region.sensitivity_level")
    metadata = mapping.get("metadata")
    if isinstance(metadata, Mapping) and "data_sensitivity" in metadata:
        return _require_string(metadata.get("data_sensitivity"), "region.metadata.data_sensitivity")
    return "unspecified"


def _validate_sensitivity_level(value: Any, path: str) -> str:
    level = _require_string(value, path)
    if level not in ALLOWED_SENSITIVITY_LEVELS:
        allowed = ", ".join(sorted(ALLOWED_SENSITIVITY_LEVELS))
        raise ValueError(f"{path} must be one of: {allowed}")
    return level


def _validate_unique_ids(region: RegionSpec) -> None:
    ids = [
        *(zone.id for zone in region.assembly_zones),
        *(zone.id for zone in region.destination_zones),
    ]
    for svc in region.region_services:
        ids.append(svc.access.id)
        ids.append(svc.egress.id)
    seen: set[str] = set()
    duplicates: list[str] = []
    for node_id in ids:
        if node_id in seen and node_id not in duplicates:
            duplicates.append(node_id)
        seen.add(node_id)
    if duplicates:
        raise ValueError(f"region node IDs must be unique; duplicates: {', '.join(duplicates)}")


def _validate_points_inside_boundary(region: RegionSpec) -> None:
    points: list[tuple[str, float, float]] = [
        *((f"assembly_zones[{index}]", zone.lat, zone.lon) for index, zone in enumerate(region.assembly_zones)),
        *(
            (f"destination_zones[{index}]", zone.lat, zone.lon)
            for index, zone in enumerate(region.destination_zones)
        ),
    ]
    for index, svc in enumerate(region.region_services):
        points.append((f"region_services[{index}].access", svc.access.lat, svc.access.lon))
        points.append((f"region_services[{index}].egress", svc.egress.lat, svc.egress.lon))
    for path, lat, lon in points:
        if not region.boundary.contains(lat, lon):
            raise ValueError(f"{path} must fall inside region.boundary")


def assert_public_coordinate_policy(
    region: RegionSpec,
    *,
    context: str = "mobilization region",
) -> None:
    """Reject non-public coordinate sources before mode/corridor expansion.

    Mobilization corridors must use only public administrative centroids and
    public transport networks (per CLAUDE.md security boundary). A region may
    CARRY a restricted / sensitive / privacy-review-pending sensitivity level,
    but it cannot ENTER the simulator until cleared. Also rejects an explicit
    non-public ``metadata.coordinate_class`` marker. This is the precondition
    guard for sea/air mode and multi-corridor expansion.
    """

    level = region.sensitivity_level
    if level not in PUBLIC_COORDINATE_LEVELS:
        raise ValueError(
            f"{context} {region.region_id!r} uses a non-public coordinate source "
            f"(sensitivity_level={level!r}); only {sorted(PUBLIC_COORDINATE_LEVELS)} "
            f"are permitted. Clear privacy/sensitivity review or restrict the "
            f"region to public administrative centroids."
        )
    coordinate_class = (region.metadata or {}).get("coordinate_class")
    if coordinate_class is not None and coordinate_class not in ALLOWED_PORT_COORDINATE_CLASSES:
        raise ValueError(
            f"{context} {region.region_id!r} metadata.coordinate_class="
            f"{coordinate_class!r}; only {sorted(ALLOWED_PORT_COORDINATE_CLASSES)} "
            f"coordinate classes are permitted."
        )


__all__ = [
    "ALLOWED_BOUNDARY_TYPES",
    "ALLOWED_FUEL_TYPES",
    "ALLOWED_PORT_COORDINATE_CLASSES",
    "ALLOWED_SENSITIVITY_LEVELS",
    "ALLOWED_SERVICE_MODES",
    "PUBLIC_COORDINATE_LEVELS",
    "BoundarySpec",
    "Metadata",
    "MetadataValue",
    "PortPointSpec",
    "RailPointSpec",
    "RailSpec",
    "RegionServiceSpec",
    "RegionSpec",
    "SourceRefSpec",
    "ZoneSpec",
    "assert_public_coordinate_policy",
    "validate_metadata",
]
