"""Tests for real-world road attribute mapping."""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.attributes import (
    DEFAULT_LENGTH_M,
    DEFAULT_ROUTEABLE_HIGHWAY_CLASSES,
    HIGHWAY_DEFAULTS,
    is_routeable_vehicle_highway,
    map_edge_attributes,
    normalize_highway,
    parse_length_m,
    parse_speed_kph,
    travel_time_min,
)


def assert_close(actual: float, expected: float, tol: float = 1e-9) -> None:
    """Assert that two floats are nearly equal."""
    assert abs(actual - expected) <= tol, f"{actual!r} != {expected!r}"


def assert_raises_value_error(func) -> None:
    """Assert that a zero-argument function raises ValueError."""
    try:
        func()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_maps_common_osm_edge_to_simulator_fields() -> None:
    """Primary road attributes should produce simulator-ready fields."""
    mapped = map_edge_attributes(
        {
            "highway": "primary",
            "maxspeed": "50 km/h",
            "length": 1000,
            "osmid": 12345,
        }
    )

    assert_close(mapped["t0"], 1.2)
    assert mapped["capacity"] == HIGHWAY_DEFAULTS["primary"].capacity
    assert mapped["base_p_fail"] == HIGHWAY_DEFAULTS["primary"].base_p_fail
    assert mapped["p_fail"] == mapped["base_p_fail"]
    assert mapped["mode"] == "road"
    assert mapped["length_m"] == 1000.0
    assert mapped["speed_kph"] == 50.0
    assert mapped["highway"] == "primary"
    assert mapped["source"] == "osm"
    assert mapped["realworld_edge_id"] == "12345"
    assert math.isfinite(mapped["t0"]) and mapped["t0"] > 0.0
    assert math.isfinite(mapped["capacity"]) and mapped["capacity"] > 0.0
    assert 0.0 <= mapped["base_p_fail"] <= 1.0
    print("PASS: common OSM edge maps to simulator fields")


def test_speed_parser_handles_numeric_units_and_lists_conservatively() -> None:
    """OSM maxspeed variants should parse deterministically."""
    assert parse_speed_kph(50) == 50.0
    assert parse_speed_kph("50") == 50.0
    assert parse_speed_kph("50 km/h") == 50.0
    assert_close(parse_speed_kph("30 mph"), 30.0 * 1.609344)
    assert parse_speed_kph(["80", "50 km/h"]) == 50.0
    assert_close(parse_speed_kph(("90", "30 mph")), 30.0 * 1.609344)
    assert parse_speed_kph("signals") is None
    print("PASS: speed parser handles numeric values, units, and lists")


def test_highway_list_selects_conservative_known_class() -> None:
    """List-like highway values should select the slower/lower-capacity class."""
    highway, defaulted = normalize_highway(["motorway", "service"])
    assert highway == "service"
    assert not defaulted

    mapped = map_edge_attributes(
        {"highway": ["motorway", "service"], "length": 200.0}
    )
    assert mapped["highway"] == "service"
    assert mapped["speed_kph"] == HIGHWAY_DEFAULTS["service"].speed_kph
    assert mapped["capacity"] == HIGHWAY_DEFAULTS["service"].capacity
    assert mapped["base_p_fail"] == HIGHWAY_DEFAULTS["service"].base_p_fail
    print("PASS: highway lists select conservative known class")


def test_missing_and_messy_osm_values_use_documented_defaults() -> None:
    """Missing or unparseable OSM fields should not produce invalid attributes."""
    mapped = map_edge_attributes(
        {
            "highway": "mystery_path",
            "maxspeed": "signals",
            "length": "unknown",
        }
    )

    defaults = HIGHWAY_DEFAULTS["unclassified"]
    assert mapped["highway"] == "unclassified"
    assert mapped["speed_kph"] == defaults.speed_kph
    assert mapped["length_m"] == DEFAULT_LENGTH_M
    assert mapped["capacity"] == defaults.capacity
    assert mapped["base_p_fail"] == defaults.base_p_fail
    assert set(mapped["attribute_assumptions"]) >= {
        "highway",
        "speed_kph",
        "length_m",
        "capacity",
    }
    assert math.isfinite(mapped["t0"]) and mapped["t0"] > 0.0
    assert math.isfinite(mapped["capacity"]) and mapped["capacity"] > 0.0
    assert 0.0 <= mapped["base_p_fail"] <= 1.0
    print("PASS: missing and messy OSM values use documented defaults")


def test_length_parser_uses_largest_positive_candidate() -> None:
    """List-like lengths should avoid understating travel time."""
    assert parse_length_m(125.5) == 125.5
    assert parse_length_m(["100", "250"]) == 250.0
    assert parse_length_m(["bad", -5, 0]) is None
    assert_close(travel_time_min(length_m=1000.0, speed_kph=60.0), 1.0)
    print("PASS: length parser uses positive finite meter values")


def test_metadata_preservation_and_overrides() -> None:
    """Source and stable edge identifiers should be preserved where available."""
    geometry = object()
    mapped = map_edge_attributes(
        {
            "highway": "secondary",
            "maxspeed": 40,
            "length": 500,
            "source": "cache",
            "realworld_edge_id": ("u", "v", 0),
            "geometry": geometry,
            "base_p_fail": 0.2,
            "capacity": 750,
        }
    )

    assert mapped["source"] == "cache"
    assert mapped["realworld_edge_id"] == "u,v,0"
    assert mapped["geometry"] is geometry
    assert mapped["base_p_fail"] == 0.2
    assert mapped["p_fail"] == 0.2
    assert mapped["capacity"] == 750.0
    print("PASS: metadata and explicit valid overrides are preserved")


def test_invalid_explicit_failure_probability_raises() -> None:
    """Explicit model probabilities should fail loudly if out of range."""
    assert_raises_value_error(lambda: map_edge_attributes({"base_p_fail": -0.01}))
    assert_raises_value_error(lambda: map_edge_attributes({"p_fail": 1.01}))
    assert_raises_value_error(lambda: map_edge_attributes({"base_p_fail": float("nan")}))
    print("PASS: invalid explicit failure probabilities raise ValueError")


def test_vehicle_highway_filter_excludes_non_bus_practical_classes() -> None:
    """Route adapters should not treat footways or service roads as bus roads."""

    assert is_routeable_vehicle_highway("primary")
    assert is_routeable_vehicle_highway(["footway", "secondary"])
    assert not is_routeable_vehicle_highway("footway")
    assert not is_routeable_vehicle_highway("cycleway")
    assert not is_routeable_vehicle_highway("service")
    assert not is_routeable_vehicle_highway("mystery_path")
    assert "service" not in DEFAULT_ROUTEABLE_HIGHWAY_CLASSES

    print("PASS: vehicle highway filter excludes non-bus-practical classes")


TESTS = [
    test_maps_common_osm_edge_to_simulator_fields,
    test_speed_parser_handles_numeric_units_and_lists_conservatively,
    test_highway_list_selects_conservative_known_class,
    test_missing_and_messy_osm_values_use_documented_defaults,
    test_length_parser_uses_largest_positive_candidate,
    test_metadata_preservation_and_overrides,
    test_invalid_explicit_failure_probability_raises,
    test_vehicle_highway_filter_excludes_non_bus_practical_classes,
]


if __name__ == "__main__":
    for test in TESTS:
        test()
    print("\n=== REALWORLD ATTRIBUTE TESTS PASSED ===")
