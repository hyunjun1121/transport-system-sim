"""Tests for rail station-binding evidence validation."""

from __future__ import annotations

import csv
import importlib.util
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.rail_station_binding import (  # noqa: E402
    DEFAULT_RAIL_STATION_BINDING_PATH,
    REQUIRED_COLUMNS,
    load_rail_station_bindings,
    summarize_rail_station_bindings,
)


ROOT = Path(__file__).resolve().parents[1]
AUDIT_SCRIPT_PATH = ROOT / "scripts" / "audit_rail_station_bindings.py"


def assert_raises_value_error(func, expected_message: str) -> None:
    """Assert that a zero-argument function raises ValueError with context."""

    try:
        func()
    except ValueError as exc:
        message = str(exc)
        assert expected_message in message, message
        return
    raise AssertionError("expected ValueError")


def test_shipped_station_bindings_are_official_but_service_claims_stay_separate() -> None:
    """Current S/R bindings use official IDs but do not validate rail service."""

    records = load_rail_station_bindings(DEFAULT_RAIL_STATION_BINDING_PATH)
    summary = summarize_rail_station_bindings(records)

    assert len(records) == 4
    assert summary["binding_ready"] is True
    assert summary["missing_required_points"] == []
    assert summary["unofficial_required_points"] == []
    assert summary["official_required_points"] == ["R", "S"]
    assert summary["remaining_blockers"] == []
    assert {record.point_id for record in records} == {"S", "R"}
    assert all(record.source_status == "official_station_code_bound" for record in records)
    assert all(
        "not operational rail service evidence" in record.claim_scope
        for record in records
    )

    print("PASS: shipped station bindings are official service-limited rows")


def test_official_fixture_is_binding_ready() -> None:
    """Official source rows for both required points should pass readiness."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "rail_station_bindings.csv"
        _write_binding_csv(path, official=True)
        records = load_rail_station_bindings(path)
        summary = summarize_rail_station_bindings(records)

        assert summary["binding_ready"] is True
        assert summary["official_required_points"] == ["R", "S"]
        assert summary["remaining_blockers"] == []

    print("PASS: official fixture is station-binding ready")


def test_non_official_fixture_requires_claim_boundary() -> None:
    """Station-area context rows must explicitly say they are non-official."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "bad_rail_station_bindings.csv"
        _write_binding_csv(path, official=False, claim_scope="station context")

        assert_raises_value_error(
            lambda: load_rail_station_bindings(path),
            "not official station-code binding",
        )

    print("PASS: non-official station rows require claim boundary")


def test_official_fixture_requires_identifier() -> None:
    """Official rows must not use placeholder station identifiers."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "bad_official_rail_station_bindings.csv"
        _write_binding_csv(path, official=True, station_id="pending", station_code="pending")

        assert_raises_value_error(
            lambda: load_rail_station_bindings(path),
            "requires station_id or station_code",
        )

    print("PASS: official station rows require identifiers")


def test_missing_required_point_is_not_reported_as_unofficial() -> None:
    """Missing rows should be separate from non-official present rows."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "partial_rail_station_bindings.csv"
        _write_binding_csv(path, official=True, points=(("S", "Access Station"),))
        records = load_rail_station_bindings(path)
        summary = summarize_rail_station_bindings(records)

        assert summary["binding_ready"] is False
        assert summary["missing_required_points"] == ["R"]
        assert summary["unofficial_required_points"] == []

    print("PASS: missing required point is not reported as unofficial")


def test_audit_script_reports_binding_ready() -> None:
    """The shipped audit should distinguish binding readiness from service evidence."""

    module = _load_audit_script()
    records = module.load_rail_station_bindings(module.DEFAULT_RAIL_STATION_BINDING_PATH)
    summary = module.summarize_rail_station_bindings(records)

    assert summary["binding_ready"] is True
    assert summary["unofficial_required_points"] == []
    assert summary["remaining_blockers"] == []

    print("PASS: station-binding audit reports official bindings ready")


def _write_binding_csv(
    path: Path,
    *,
    official: bool,
    points: tuple[tuple[str, str], ...] = (("S", "Access Station"), ("R", "Egress Station")),
    claim_scope: str | None = None,
    station_id: str = "official_fixture_id",
    station_code: str = "official_fixture_code",
) -> None:
    rows = []
    for point_id, station_name in points:
        rows.append(
            {
                "binding_id": f"fixture_{point_id}",
                "region_id": "songpa_public_demo",
                "point_id": point_id,
                "station_name": station_name,
                "station_id": station_id if official else "pending",
                "station_code": station_code if official else "pending",
                "source_name": "fixture source",
                "source_url_or_citation": "fixture citation",
                "source_accessed_date": "2026-05-04",
                "source_status": (
                    "official_station_code_bound"
                    if official
                    else "public_station_name_context"
                ),
                "claim_scope": claim_scope
                or (
                    "official station-code binding for test"
                    if official
                    else "public station-area context only; not official station-code binding"
                ),
                "notes": "fixture row",
            }
        )

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def _load_audit_script():
    spec = importlib.util.spec_from_file_location(
        "audit_rail_station_bindings", AUDIT_SCRIPT_PATH
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["audit_rail_station_bindings"] = module
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    test_shipped_station_bindings_are_official_but_service_claims_stay_separate()
    test_official_fixture_is_binding_ready()
    test_non_official_fixture_requires_claim_boundary()
    test_official_fixture_requires_identifier()
    test_missing_required_point_is_not_reported_as_unofficial()
    test_audit_script_reports_binding_ready()
    print("\n=== REALWORLD RAIL STATION BINDING TESTS PASSED ===")
