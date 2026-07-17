"""Tests for road-class evidence override tables."""

from __future__ import annotations

import csv
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.attributes import HIGHWAY_DEFAULTS, map_edge_attributes  # noqa: E402
from src.realworld.road_overrides import (  # noqa: E402
    REQUIRED_COLUMNS,
    build_highway_defaults_with_overrides,
    load_road_class_overrides,
)


def assert_raises_value_error(func, expected_message: str) -> None:
    """Assert that a zero-argument function raises ValueError with context."""

    try:
        func()
    except ValueError as exc:
        message = str(exc)
        assert expected_message in message, message
        return
    raise AssertionError("expected ValueError")


def test_road_class_override_changes_mapper_fallback_values() -> None:
    """Override tables should affect fallback speed and capacity explicitly."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "road_class_overrides.csv"
        _write_override_csv(path)
        overrides = load_road_class_overrides(path)
        defaults = build_highway_defaults_with_overrides(overrides)

        mapped = map_edge_attributes(
            {"highway": "primary", "length": 1000},
            highway_defaults=defaults,
        )

        assert mapped["speed_kph"] == 42.0
        assert mapped["capacity"] == 1234.0
        assert mapped["base_p_fail"] == 0.01
        assert HIGHWAY_DEFAULTS["primary"].speed_kph != 42.0

    print("PASS: road class override changes mapper fallback values")


def test_road_class_override_rejects_unknown_highway() -> None:
    """Unknown highway classes should not silently alter mapper behavior."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "bad_road_class_overrides.csv"
        _write_override_csv(path, highway="mystery")

        assert_raises_value_error(
            lambda: load_road_class_overrides(path),
            "unknown highway class",
        )

    print("PASS: road class override rejects unknown highway")


def _write_override_csv(path: Path, *, highway: str = "primary") -> None:
    row = {
        "highway": highway,
        "speed_kph": "42",
        "capacity_veh_per_hr": "1234",
        "base_p_fail": "0.01",
        "source_class": "literature-derived",
        "source_name": "fixture",
        "source_url_or_citation": "fixture",
        "notes": "fixture row",
    }
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerow(row)


if __name__ == "__main__":
    test_road_class_override_changes_mapper_fallback_values()
    test_road_class_override_rejects_unknown_highway()
    print("\n=== REALWORLD ROAD OVERRIDE TESTS PASSED ===")
