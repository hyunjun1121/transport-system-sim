"""Region registry helpers for validated real-world pipeline specs."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from .types import RegionSpec


REGION_REGISTRY: dict[str, Mapping[str, Any]] = {}


def load_region_spec(value: Mapping[str, Any] | RegionSpec) -> RegionSpec:
    """Load one region spec from a mapping or return an existing spec."""

    if isinstance(value, RegionSpec):
        return value
    return RegionSpec.from_mapping(value)


def load_region_registry(
    values: Mapping[str, Mapping[str, Any] | RegionSpec] | Sequence[Mapping[str, Any] | RegionSpec],
) -> dict[str, RegionSpec]:
    """Load a mapping of region IDs to validated region specs.

    A registry can be provided as either a list of full region mappings or a
    mapping keyed by region ID. If a keyed mapping omits ``region_id`` inside
    the child spec, the key is copied in before validation.
    """

    items: list[tuple[str | None, Mapping[str, Any] | RegionSpec]]
    if isinstance(values, Mapping):
        items = [(str(key), value) for key, value in values.items()]
    elif isinstance(values, Sequence) and not isinstance(values, (str, bytes)):
        items = [(None, value) for value in values]
    else:
        raise ValueError("region registry must be a mapping or a list of region specs")

    registry: dict[str, RegionSpec] = {}
    for key, value in items:
        spec_value: Mapping[str, Any] | RegionSpec = value
        if key is not None and isinstance(value, Mapping) and "region_id" not in value:
            spec_value = {**value, "region_id": key}
        spec = load_region_spec(spec_value)
        if key is not None and spec.region_id != key:
            raise ValueError(
                f"region registry key {key!r} does not match region_id {spec.region_id!r}"
            )
        if spec.region_id in registry:
            raise ValueError(f"duplicate region_id in registry: {spec.region_id}")
        registry[spec.region_id] = spec
    return registry


def get_region_spec(
    region_id: str,
    registry: Mapping[str, Mapping[str, Any] | RegionSpec] | None = None,
) -> RegionSpec:
    """Return a validated registered region by ID."""

    source = REGION_REGISTRY if registry is None else registry
    if region_id not in source:
        available = ", ".join(sorted(source)) or "none"
        raise ValueError(f"unknown region_id {region_id!r}; available: {available}")
    return load_region_spec(source[region_id])


__all__ = [
    "REGION_REGISTRY",
    "get_region_spec",
    "load_region_registry",
    "load_region_spec",
]
