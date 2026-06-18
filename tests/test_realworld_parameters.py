"""Tests for real-world parameter evidence table validation."""

from __future__ import annotations

import csv
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.parameters import (
    ALLOWED_SOURCE_CLASSES,
    ASSUMPTION_SOURCE_CLASSES,
    MINIMUM_PARAMETER_NAMES,
    REQUIRED_COLUMNS,
    REQUIRED_FLEET_PARAMETERS,
    REQUIRED_RAIL_PARAMETERS,
    SHIPPED_TABLE_REQUIREMENTS,
    numeric_tokens,
    validate_parameter_table,
    validate_shipped_parameter_tables,
)


ROOT = Path(__file__).resolve().parents[1]
PARAMETER_DIR = ROOT / "data" / "parameters"


def assert_raises_value_error(func, expected_message: str) -> None:
    """Assert that a zero-argument function raises ValueError with context."""

    try:
        func()
    except ValueError as exc:
        message = str(exc)
        assert expected_message in message, message
        return
    raise AssertionError("expected ValueError")


def test_shipped_parameter_tables_validate() -> None:
    """The committed parameter evidence package should pass schema checks."""

    tables = validate_shipped_parameter_tables(PARAMETER_DIR)

    assert set(tables) == set(SHIPPED_TABLE_REQUIREMENTS)
    for filename, records in tables.items():
        assert records, f"{filename} should contain records"
        for record in records:
            assert record.source_class in ALLOWED_SOURCE_CLASSES
            if record.source_class in ASSUMPTION_SOURCE_CLASSES:
                assert record.uncertainty_range
                assert record.notes

    print("PASS: shipped parameter tables validate")


def test_workstream_4_minimum_parameters_are_covered() -> None:
    """The primary source table should cover every Workstream 4 minimum."""

    records = validate_parameter_table(
        PARAMETER_DIR / "parameter_sources.csv",
        required_parameters=MINIMUM_PARAMETER_NAMES,
    )
    by_parameter = {record.parameter: record for record in records}

    assert set(MINIMUM_PARAMETER_NAMES) <= set(by_parameter)
    assert by_parameter["disruption_probability"].source_class == "sensitivity-only"
    assert by_parameter["rail_headway"].source_class == "agency/timetable-derived"
    assert numeric_tokens(by_parameter["road_capacity_proxy"].value)

    print("PASS: Workstream 4 minimum parameters are covered")


def test_specialized_rail_and_fleet_tables_have_required_rows() -> None:
    """Rail and fleet evidence tables should cover their focused parameters."""

    rail_records = validate_parameter_table(
        PARAMETER_DIR / "rail_assumptions.csv",
        required_parameters=REQUIRED_RAIL_PARAMETERS,
    )
    fleet_records = validate_parameter_table(
        PARAMETER_DIR / "fleet_assumptions.csv",
        required_parameters=REQUIRED_FLEET_PARAMETERS,
    )

    rail_parameters = {record.parameter for record in rail_records}
    fleet_parameters = {record.parameter for record in fleet_records}
    assert set(REQUIRED_RAIL_PARAMETERS) <= rail_parameters
    assert set(REQUIRED_FLEET_PARAMETERS) <= fleet_parameters

    print("PASS: specialized rail and fleet tables have required rows")


def test_failing_fixture_rejects_missing_required_columns() -> None:
    """A CSV without the required evidence fields should fail deterministically."""

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "missing_columns.csv"
        path.write_text(
            "parameter,value,unit\nroad_free_flow_speed,35,km/h\n",
            encoding="utf-8",
        )

        assert_raises_value_error(
            lambda: validate_parameter_table(path),
            "missing required columns",
        )

    print("PASS: missing required columns are rejected")


def test_failing_fixture_rejects_weak_assumption_rows() -> None:
    """Assumption rows need a numeric value where applicable and uncertainty notes."""

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "weak_assumption.csv"
        _write_parameter_csv(
            path,
            {
                "parameter": "road_free_flow_speed",
                "value": "35",
                "unit": "km/h",
                "source_class": "expert assumption",
                "source_name": "fixture",
                "source_url_or_citation": "fixture",
                "applies_to": "test",
                "uncertainty_range": "",
                "notes": "",
            },
        )

        assert_raises_value_error(
            lambda: validate_parameter_table(
                path,
                required_parameters=("road_free_flow_speed",),
            ),
            "must include uncertainty_range",
        )

    print("PASS: weak assumption rows are rejected")


def test_failing_fixture_rejects_bad_numeric_values() -> None:
    """Numeric units should not accept non-numeric value text."""

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "bad_numeric.csv"
        _write_parameter_csv(
            path,
            {
                "parameter": "road_capacity_proxy",
                "value": "unknown",
                "unit": "veh/hr",
                "source_class": "public-data-derived",
                "source_name": "fixture",
                "source_url_or_citation": "fixture",
                "applies_to": "test",
                "uncertainty_range": "",
                "notes": "",
            },
        )

        assert_raises_value_error(
            lambda: validate_parameter_table(path),
            "non-numeric value",
        )

    print("PASS: bad numeric values are rejected")


def _write_parameter_csv(path: Path, row: dict[str, str]) -> None:
    """Write a temporary parameter CSV using the production header."""

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerow(row)


TESTS = [
    test_shipped_parameter_tables_validate,
    test_workstream_4_minimum_parameters_are_covered,
    test_specialized_rail_and_fleet_tables_have_required_rows,
    test_failing_fixture_rejects_missing_required_columns,
    test_failing_fixture_rejects_weak_assumption_rows,
    test_failing_fixture_rejects_bad_numeric_values,
]


if __name__ == "__main__":
    for test in TESTS:
        test()
    print("\n=== REALWORLD PARAMETER TESTS PASSED ===")
