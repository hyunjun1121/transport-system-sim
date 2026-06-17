"""Tests for rail evidence cache validation."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.rail_evidence import (
    DEFAULT_RAIL_SERVICE_EVIDENCE_PATH,
    OPTIONAL_COLUMNS,
    REQUIRED_COLUMNS,
    load_rail_service_evidence,
    summarize_rail_service_evidence,
)


ROOT = Path(__file__).resolve().parents[1]
AUDIT_SCRIPT_PATH = ROOT / "scripts" / "audit_rail_evidence.py"


def assert_raises_value_error(func, expected_message: str) -> None:
    """Assert that a zero-argument function raises ValueError with context."""

    try:
        func()
    except ValueError as exc:
        message = str(exc)
        assert expected_message in message, message
        return
    raise AssertionError("expected ValueError")


def test_shipped_rail_service_evidence_validates_with_mixed_evidence() -> None:
    """The current rail cache should validate while blocking final claims."""

    records = load_rail_service_evidence(DEFAULT_RAIL_SERVICE_EVIDENCE_PATH)
    summary = summarize_rail_service_evidence(records)

    assert len(records) >= 1
    assumption_rows = [
        record for record in records
        if record.source_status == "documented_assumption_proxy"
    ]
    assert len(assumption_rows) >= 1
    assert "not calibrated" in assumption_rows[0].claim_scope
    assert summary["publication_ready"] is False
    assert summary["remaining_blockers"]
    assert summary["derived_record_count"] >= 1
    assert summary["derived_field_ready"]["headway"] is True
    assert summary["derived_field_ready"]["travel_time"] is False

    print("PASS: shipped rail evidence validates with mixed derived + assumption rows")


def test_derived_fixture_can_be_publication_ready() -> None:
    """A cached timetable-derived row should be recognized as stronger evidence."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "rail_service_evidence.csv"
        source_path = Path(tmp) / "source_timetable.csv"
        source_path.write_text("fixture source\n", encoding="utf-8")
        _write_rail_csv(
            path,
            source_status="cached_timetable_derived",
            claim_scope=(
                "cached timetable-derived rail timing evidence; capacity remains "
                "sensitivity-only; not operational forecast"
            ),
            source_artifact_path=str(source_path),
            source_artifact_sha256=_file_sha256(source_path),
        )
        records = load_rail_service_evidence(path)
        summary = summarize_rail_service_evidence(records)

        assert records[0].is_derived
        assert records[0].derived_field_set == frozenset({"headway", "travel_time"})
        assert summary["publication_ready"] is True
        assert summary["derived_record_count"] == 1
        assert summary["timing_evidence_ready"] is True
        assert summary["source_artifact_ready"] is True
        assert summary["capacity_sensitivity_acknowledged"] is True
        assert summary["remaining_blockers"] == []

    print("PASS: derived fixture can be publication-ready evidence")


def test_derived_fixture_requires_source_artifact_fields() -> None:
    """Derived rows must preserve cached source artifact metadata."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "bad_rail_service_evidence.csv"
        _write_rail_csv(
            path,
            source_status="cached_timetable_derived",
            claim_scope=(
                "cached timetable-derived rail timing evidence; capacity remains "
                "sensitivity-only; not operational forecast"
            ),
            source_artifact_path="",
            source_artifact_sha256="",
        )

        assert_raises_value_error(
            lambda: load_rail_service_evidence(path),
            "source_artifact_path",
        )

    print("PASS: derived rows require source artifact metadata")


def test_mixed_timetable_and_shortest_path_rows_can_satisfy_timing_gate() -> None:
    """Headway and travel time may come from separate cached artifacts."""

    with TemporaryDirectory() as tmp:
        directory = Path(tmp)
        path = directory / "rail_service_evidence.csv"
        timetable_source = directory / "timetable.csv"
        shortest_path_source = directory / "shortest_path.json"
        timetable_source.write_text("fixture timetable\n", encoding="utf-8")
        shortest_path_source.write_text('{"fixture": true}\n', encoding="utf-8")
        _write_rail_rows(
            path,
            [
                _rail_row(
                    evidence_id="headway",
                    source_status="cached_timetable_derived",
                    derived_fields="headway",
                    source_artifact_path=str(timetable_source),
                    source_artifact_sha256=_file_sha256(timetable_source),
                ),
                _rail_row(
                    evidence_id="travel_time",
                    source_status="cached_shortest_path_derived",
                    derived_fields="travel_time",
                    source_artifact_path=str(shortest_path_source),
                    source_artifact_sha256=_file_sha256(shortest_path_source),
                ),
            ],
        )

        records = load_rail_service_evidence(path)
        summary = summarize_rail_service_evidence(records)

        assert summary["derived_record_count"] == 2
        assert summary["derived_field_ready"]["headway"] is True
        assert summary["derived_field_ready"]["travel_time"] is True
        assert summary["source_artifact_ready"] is True
        assert summary["publication_ready"] is True

    print("PASS: mixed rail timing evidence can satisfy timing gate")


def test_assumption_fixture_requires_claim_boundary() -> None:
    """Assumption proxy rows must explicitly block calibrated claims."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "bad_rail_service_evidence.csv"
        _write_rail_csv(
            path,
            source_status="documented_assumption_proxy",
            claim_scope="ready for use",
        )

        assert_raises_value_error(
            lambda: load_rail_service_evidence(path),
            "must include 'not calibrated'",
        )

    print("PASS: assumption rows require conservative claim boundary")


def test_audit_script_reports_cached_derivation_path() -> None:
    """The rail audit should expose that a local derivation path exists."""

    module = _load_audit_script()
    records = module.load_rail_service_evidence(module.DEFAULT_RAIL_SERVICE_EVIDENCE_PATH)
    summary = module.summarize_rail_service_evidence(records)
    summary["cached_timetable_derivation_path_available"] = (
        (ROOT / "scripts" / "derive_rail_service_evidence.py").exists()
        and (ROOT / "docs" / "schemas" / "rail_timetable_cache_schema.md").exists()
    )
    summary["cached_shortest_path_derivation_path_available"] = (
        (ROOT / "scripts" / "derive_rail_shortest_path_evidence.py").exists()
        and (ROOT / "docs" / "schemas" / "rail_shortest_path_cache_schema.md").exists()
    )
    summary["cached_gtfs_derivation_path_available"] = (
        (ROOT / "scripts" / "derive_rail_gtfs_evidence.py").exists()
        and (ROOT / "docs" / "schemas" / "rail_gtfs_cache_schema.md").exists()
    )

    assert summary["publication_ready"] is False
    assert summary["cached_timetable_derivation_path_available"] is True
    assert summary["cached_shortest_path_derivation_path_available"] is True
    assert summary["cached_gtfs_derivation_path_available"] is True

    print("PASS: rail audit reports cached derivation path")


def _write_rail_csv(
    path: Path,
    *,
    source_status: str,
    claim_scope: str,
    source_artifact_path: str = "data/rail/fixture.csv",
    source_artifact_sha256: str = "a" * 64,
) -> None:
    row = {
        "evidence_id": "fixture",
        "region_id": "fixture_region",
        "access_point": "S",
        "egress_point": "R",
        "access_station_name": "Access Station",
        "egress_station_name": "Egress Station",
        "source_status": source_status,
        "source_name": "fixture",
        "source_url_or_citation": "fixture",
        "extraction_date": "2026-05-04",
        "headway_min": "8",
        "travel_time_min": "18",
        "capacity_pax_per_train": "500",
        "service_window": "fixture",
        "claim_scope": claim_scope,
        "notes": "fixture row",
        "derived_fields": (
            "headway;travel_time" if source_status.startswith("cached_") else ""
        ),
        "source_artifact_path": (
            source_artifact_path if source_status.startswith("cached_") else ""
        ),
        "source_artifact_sha256": (
            source_artifact_sha256 if source_status.startswith("cached_") else ""
        ),
    }
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS + OPTIONAL_COLUMNS)
        writer.writeheader()
        writer.writerow(row)


def _write_rail_rows(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS + OPTIONAL_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def _rail_row(
    *,
    evidence_id: str,
    source_status: str,
    derived_fields: str,
    source_artifact_path: str,
    source_artifact_sha256: str,
) -> dict[str, str]:
    return {
        "evidence_id": evidence_id,
        "region_id": "fixture_region",
        "access_point": "S",
        "egress_point": "R",
        "access_station_name": "Access Station",
        "egress_station_name": "Egress Station",
        "source_status": source_status,
        "source_name": "fixture",
        "source_url_or_citation": "fixture",
        "extraction_date": "2026-05-04",
        "headway_min": "8",
        "travel_time_min": "18",
        "capacity_pax_per_train": "500",
        "service_window": "fixture",
        "claim_scope": (
            "cached rail timing evidence; capacity remains sensitivity-only; "
            "not operational forecast"
        ),
        "notes": "fixture row",
        "derived_fields": derived_fields,
        "source_artifact_path": source_artifact_path,
        "source_artifact_sha256": source_artifact_sha256,
    }


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_audit_script():
    spec = importlib.util.spec_from_file_location("audit_rail_evidence", AUDIT_SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["audit_rail_evidence"] = module
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    test_shipped_rail_service_evidence_validates_with_mixed_evidence()
    test_derived_fixture_can_be_publication_ready()
    test_derived_fixture_requires_source_artifact_fields()
    test_mixed_timetable_and_shortest_path_rows_can_satisfy_timing_gate()
    test_assumption_fixture_requires_claim_boundary()
    test_audit_script_reports_cached_derivation_path()
    print("\n=== REALWORLD RAIL EVIDENCE TESTS PASSED ===")
