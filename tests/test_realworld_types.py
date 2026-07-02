"""Unit tests for real-world region schema records."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld import (
    BoundarySpec,
    RailPointSpec,
    RailSpec,
    RegionSpec,
    SourceRefSpec,
    ZoneSpec,
    get_region_spec,
    load_region_registry,
    load_region_spec,
    validate_metadata,
)


def minimal_region_dict() -> dict:
    """Return the minimal valid dict from the real-world MVP contract."""

    return {
        "region_id": "pilot_small",
        "label": "Pilot Small Region",
        "sensitivity_level": "non_sensitive",
        "boundary": {
            "type": "bbox",
            "north": 37.53,
            "south": 37.49,
            "east": 127.14,
            "west": 127.08,
        },
        "assembly_zones": [
            {
                "id": "A",
                "lat": 37.51,
                "lon": 127.10,
            },
        ],
        "destination_zones": [
            {
                "id": "D",
                "lat": 37.52,
                "lon": 127.13,
            },
        ],
        "rail": {
            "access": {
                "id": "S",
                "lat": 37.51,
                "lon": 127.11,
            },
            "egress": {
                "id": "R",
                "lat": 37.52,
                "lon": 127.12,
            },
            "travel_time_min": 40,
            "headway_min": 10,
            "capacity_pax_per_train": 500,
        },
        "source_refs": [
            {
                "source_id": "pilot_region_spec",
                "role": "region_registry",
                "local_artifact_path": "data/regions/pilot_region.yaml",
                "review_status": "repository_input_pending_review",
            },
        ],
    }


def assert_value_error_contains(fn, expected: str) -> None:
    """Assert that a callable raises a ValueError with an actionable fragment."""

    try:
        fn()
    except ValueError as exc:
        assert expected in str(exc), f"expected {expected!r} in {exc!r}"
    else:
        raise AssertionError(f"expected ValueError containing {expected!r}")


def test_minimal_region_spec_loads():
    """Minimal region dictionaries should normalize into typed records."""

    region = load_region_spec(minimal_region_dict())

    assert isinstance(region, RegionSpec)
    assert isinstance(region.boundary, BoundarySpec)
    assert isinstance(region.primary_assembly, ZoneSpec)
    assert isinstance(region.rail.access, RailPointSpec)
    assert isinstance(region.source_refs[0], SourceRefSpec)
    assert region.region_id == "pilot_small"
    assert region.name == "Pilot Small Region"
    assert region.label == "Pilot Small Region"
    assert region.sensitivity_level == "non_sensitive"
    assert region.boundary.bounds == (127.08, 37.49, 127.14, 37.53)
    assert region.origin_zones == region.assembly_zones
    assert region.canonical_ids == ("A", "D", "S", "R")
    assert region.simulator_node_ids == {
        "assembly": "A",
        "destination": "D",
        "rail_access": "S",
        "rail_egress": "R",
    }
    assert region.rail.travel_time_min == 40.0
    assert region.rail.headway_min == 10.0
    assert region.rail.capacity_pax_per_train == 500
    assert region.source_refs[0].source_id == "pilot_region_spec"

    print("PASS: Minimal region spec loads")


def test_multiple_zones_preserve_lists_and_primary_ids():
    """Zone lists should remain ordered while exposing simulator primary IDs."""

    spec = minimal_region_dict()
    spec["assembly_zones"].append({"id": "A2", "lat": 37.505, "lon": 127.10})
    spec["destination_zones"].append({"id": "D2", "lat": 37.525, "lon": 127.13})

    region = RegionSpec.from_mapping(spec)

    assert [zone.id for zone in region.assembly_zones] == ["A", "A2"]
    assert [zone.id for zone in region.destination_zones] == ["D", "D2"]
    assert region.primary_assembly_id == "A"
    assert region.primary_destination_id == "D"

    print("PASS: Multiple zones preserve order")


def test_bbox_validation_rejects_invalid_boundaries():
    """Bounding boxes should fail clearly when coordinates are malformed."""

    spec = minimal_region_dict()
    spec["boundary"]["north"] = 37.49
    assert_value_error_contains(
        lambda: load_region_spec(spec),
        "boundary.north must be greater than boundary.south",
    )

    spec = minimal_region_dict()
    spec["boundary"]["east"] = 127.08
    assert_value_error_contains(
        lambda: load_region_spec(spec),
        "boundary.east must be greater than boundary.west",
    )

    spec = minimal_region_dict()
    spec["boundary"]["type"] = "polygon"
    assert_value_error_contains(lambda: load_region_spec(spec), "boundary.polygon_path")

    spec["boundary"]["polygon_path"] = "data/regions/pilot_region.geojson"
    region = load_region_spec(spec)
    assert region.boundary.type == "polygon"
    assert region.boundary.polygon_path == "data/regions/pilot_region.geojson"

    print("PASS: Invalid bboxes fail clearly")


def test_zone_validation_rejects_bad_coordinates_and_empty_lists():
    """Zone validation should name the failing field."""

    spec = minimal_region_dict()
    spec["assembly_zones"][0]["lat"] = 91
    assert_value_error_contains(
        lambda: load_region_spec(spec),
        "assembly_zones[0].lat must be between -90 and 90",
    )

    spec = minimal_region_dict()
    spec["destination_zones"] = []
    assert_value_error_contains(
        lambda: load_region_spec(spec),
        "destination_zones must contain at least one zone",
    )

    spec = minimal_region_dict()
    spec["rail"]["access"]["lat"] = 37.54
    assert_value_error_contains(
        lambda: load_region_spec(spec),
        "region_services[0].access must fall inside region.boundary",
    )

    print("PASS: Invalid zones fail clearly")


def test_rail_validation_rejects_invalid_service_values():
    """Rail service values should be positive and capacity should be integral."""

    spec = minimal_region_dict()
    spec["rail"]["travel_time_min"] = 0
    assert_value_error_contains(
        lambda: load_region_spec(spec),
        "rail.travel_time_min must be positive",
    )

    spec = minimal_region_dict()
    spec["rail"]["headway_min"] = -1
    assert_value_error_contains(
        lambda: load_region_spec(spec),
        "rail.headway_min must be positive",
    )

    spec = minimal_region_dict()
    spec["rail"]["capacity_pax_per_train"] = 0
    assert_value_error_contains(
        lambda: load_region_spec(spec),
        "rail.capacity_pax_per_train must be at least 1",
    )

    print("PASS: Invalid rail service values fail clearly")


def test_duplicate_node_ids_are_rejected():
    """Canonical adapter node IDs should remain unambiguous."""

    spec = minimal_region_dict()
    spec["rail"]["access"]["id"] = "A"

    assert_value_error_contains(
        lambda: load_region_spec(spec),
        "region node IDs must be unique",
    )

    print("PASS: Duplicate node IDs fail clearly")


def test_origin_zone_alias_and_sensitivity_fallback():
    """Region registry vocabulary should accept origin_zones and metadata fallback."""

    spec = minimal_region_dict()
    spec["name"] = spec.pop("label")
    spec["origin_zones"] = spec.pop("assembly_zones")
    spec.pop("sensitivity_level")
    spec["metadata"] = {"data_sensitivity": "synthetic"}

    region = load_region_spec(spec)

    assert region.primary_assembly_id == "A"
    assert region.origin_zones == region.assembly_zones
    assert region.sensitivity_level == "synthetic"

    print("PASS: origin_zones alias and sensitivity fallback load")


def test_source_refs_are_structured_not_metadata():
    """Source references should be typed records separate from scalar metadata."""

    region = load_region_spec(minimal_region_dict())

    assert region.source_refs[0] == SourceRefSpec(
        source_id="pilot_region_spec",
        role="region_registry",
        local_artifact_path="data/regions/pilot_region.yaml",
        review_status="repository_input_pending_review",
    )

    spec = minimal_region_dict()
    spec["source_refs"][0]["source_id"] = ""
    assert_value_error_contains(
        lambda: load_region_spec(spec),
        "source_refs[0].source_id must be non-empty",
    )

    spec = minimal_region_dict()
    spec["sensitivity_level"] = "classified"
    assert_value_error_contains(
        lambda: load_region_spec(spec),
        "region.sensitivity_level must be one of",
    )

    print("PASS: source refs and sensitivity are validated")


def test_metadata_validator_accepts_scalar_records_only():
    """Metadata should stay lightweight and serializable."""

    metadata = validate_metadata(
        {
            "source": "assumption",
            "confidence": 0.75,
            "reviewed": True,
            "notes": None,
        },
    )
    assert metadata == {
        "source": "assumption",
        "confidence": 0.75,
        "reviewed": True,
        "notes": None,
    }

    assert_value_error_contains(
        lambda: validate_metadata({"nested": {"source": "x"}}),
        "metadata.nested must be a scalar metadata value",
    )

    print("PASS: Metadata validation is scalar and serializable")


def test_direct_dataclass_construction_validates_values():
    """Records constructed directly should enforce the same value rules."""

    from src.realworld import PortPointSpec, RegionServiceSpec

    service = RegionServiceSpec(
        mode="rail",
        access=PortPointSpec("S", 37.51, 127.11),
        egress=PortPointSpec("R", 37.52, 127.12),
        travel_time_min=40,
        headway_min=10,
        capacity_pax_per_unit=500,
    )

    region = RegionSpec(
        region_id="pilot_small",
        name="Pilot Small Region",
        boundary=BoundarySpec("bbox", 37.53, 37.49, 127.14, 127.08),
        assembly_zones=(ZoneSpec("A", 37.51, 127.10),),
        destination_zones=(ZoneSpec("D", 37.52, 127.13),),
        region_services=(service,),
    )

    assert region.canonical_ids == ("A", "D", "S", "R")
    # backward-compatible rail alias derives from the rail service
    assert region.rail.access.id == "S"
    assert region.rail.capacity_pax_per_train == 500

    print("PASS: Direct dataclass construction validates values")


def test_region_registry_loads_lists_and_keyed_mappings():
    """Registry helpers should load lists and region_id-keyed mappings."""

    spec = minimal_region_dict()
    by_list = load_region_registry([spec])
    assert by_list["pilot_small"].primary_assembly_id == "A"

    keyed = load_region_registry({"pilot_small": {k: v for k, v in spec.items() if k != "region_id"}})
    assert keyed["pilot_small"].rail_egress_id == "R"
    assert get_region_spec("pilot_small", keyed).canonical_ids == ("A", "D", "S", "R")
    assert_value_error_contains(
        lambda: get_region_spec("missing", keyed),
        "unknown region_id 'missing'",
    )

    print("PASS: Region registry helpers load specs")


def test_multi_service_region_generalizes_canonical_ids_and_node_map():
    """A rail+sea region must carry both services' ports in canonical/node maps."""

    from src.realworld import PortPointSpec, RegionServiceSpec

    rail = RegionServiceSpec(
        mode="rail",
        access=PortPointSpec("S", 37.51, 127.11),
        egress=PortPointSpec("R", 37.52, 127.12),
        travel_time_min=40,
        headway_min=10,
        capacity_pax_per_unit=500,
    )
    sea = RegionServiceSpec(
        mode="sea",
        access=PortPointSpec("sea_acc", 37.50, 127.10),
        egress=PortPointSpec("sea_egr", 37.53, 127.13),
        travel_time_min=200,
        headway_min=60,
        capacity_pax_per_unit=300,
    )
    region = RegionSpec(
        region_id="multi_probe",
        name="Multi Probe",
        boundary=BoundarySpec("bbox", 37.53, 37.49, 127.14, 127.08),
        assembly_zones=(ZoneSpec("A", 37.51, 127.10),),
        destination_zones=(ZoneSpec("D", 37.52, 127.13),),
        region_services=(rail, sea),
    )

    # rail-first ordering: canonical_ids appends sea ports after the rail pair
    assert region.canonical_ids == ("A", "D", "S", "R", "sea_acc", "sea_egr")
    assert region.simulator_node_ids == {
        "assembly": "A",
        "destination": "D",
        "rail_access": "S",
        "rail_egress": "R",
        "sea_access": "sea_acc",
        "sea_egress": "sea_egr",
    }
    assert region.services_by_mode("sea") == (sea,)
    assert region.rail_service == rail
    # rail alias still resolves to the rail service
    assert region.rail.access.id == "S"
    print("PASS: multi-service region generalizes canonical_ids + node map (rail-first)")


def test_duplicate_mode_services_are_rejected() -> None:
    """Two services of the same mode are ambiguous and must be rejected (C3)."""

    from src.realworld import PortPointSpec, RegionServiceSpec

    rail1 = RegionServiceSpec(
        mode="rail",
        access=PortPointSpec("S1", 37.51, 127.11),
        egress=PortPointSpec("R1", 37.52, 127.12),
        travel_time_min=40,
        headway_min=10,
        capacity_pax_per_unit=500,
    )
    rail2 = RegionServiceSpec(
        mode="rail",
        access=PortPointSpec("S2", 37.505, 127.115),
        egress=PortPointSpec("R2", 37.515, 127.125),
        travel_time_min=50,
        headway_min=12,
        capacity_pax_per_unit=400,
    )
    try:
        RegionSpec(
            region_id="dup_mode",
            name="Dup Mode",
            boundary=BoundarySpec("bbox", 37.53, 37.49, 127.14, 127.08),
            assembly_zones=(ZoneSpec("A", 37.51, 127.10),),
            destination_zones=(ZoneSpec("D", 37.52, 127.13),),
            region_services=(rail1, rail2),
        )
        raise AssertionError("expected ValueError for duplicate rail modes")
    except ValueError as exc:
        assert "at most one service per mode" in str(exc), f"unexpected: {exc!r}"
    print("PASS: duplicate-mode services rejected (mode-uniqueness guard)")


if __name__ == "__main__":
    test_minimal_region_spec_loads()
    test_multiple_zones_preserve_lists_and_primary_ids()
    test_bbox_validation_rejects_invalid_boundaries()
    test_zone_validation_rejects_bad_coordinates_and_empty_lists()
    test_rail_validation_rejects_invalid_service_values()
    test_duplicate_node_ids_are_rejected()
    test_origin_zone_alias_and_sensitivity_fallback()
    test_source_refs_are_structured_not_metadata()
    test_metadata_validator_accepts_scalar_records_only()
    test_direct_dataclass_construction_validates_values()
    test_region_registry_loads_lists_and_keyed_mappings()
    test_multi_service_region_generalizes_canonical_ids_and_node_map()
    test_duplicate_mode_services_are_rejected()
    print("\n=== REALWORLD TYPE TESTS PASSED ===")
