"""Tests for road-class override evidence audit."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.road_override_audit import (  # noqa: E402
    audit_road_class_override_application,
    audit_road_class_override_evidence,
)
from src.realworld.road_overrides import (  # noqa: E402
    OPTIONAL_FIELD_SOURCE_COLUMNS,
    REQUIRED_COLUMNS,
)


def test_missing_default_override_table_is_reported_not_failed() -> None:
    """The shipped scaffold should expose missing override evidence as blocker."""

    summary = audit_road_class_override_evidence()

    assert summary["publication_ready"] is False
    assert summary["override_table_present"] is False
    assert summary["remaining_blockers"]

    print("PASS: missing reviewed override table is reported with draft context")


def test_strong_override_fixture_can_pass_source_strength_gate() -> None:
    """A source-backed override table should pass this narrow audit."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "road_class_overrides.csv"
        _write_override_csv(path, source_class="literature-derived")
        summary = audit_road_class_override_evidence(path)

        assert summary["publication_ready"] is True
        assert summary["override_table_present"] is True
        assert summary["row_count"] == 1
        assert summary["weak_row_count"] == 0

    print("PASS: strong override fixture passes source-strength gate")


def test_weak_override_fixture_blocks_publication_readiness() -> None:
    """Expert-assumption override rows should remain weak for final claims."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "road_class_overrides.csv"
        _write_override_csv(path, source_class="expert assumption")
        summary = audit_road_class_override_evidence(path)

        assert summary["publication_ready"] is False
        assert summary["weak_row_count"] == 1
        assert summary["weak_highway_classes"] == ["primary"]

    print("PASS: weak override fixture blocks publication readiness")


def test_field_level_weak_source_blocks_publication_readiness() -> None:
    """A strong row source should not hide a weak field-level source."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "road_class_overrides.csv"
        _write_override_csv(
            path,
            source_class="literature-derived",
            base_p_fail_source_class="sensitivity-only",
        )
        summary = audit_road_class_override_evidence(path)

        assert summary["publication_ready"] is False
        assert summary["weak_row_count"] == 0
        assert summary["weak_field_count"] == 1
        assert summary["weak_field_entries"] == [
            {
                "highway": "primary",
                "field": "base_p_fail",
                "source_class": "sensitivity-only",
            }
        ]

    print("PASS: field-level weak source blocks publication readiness")


def test_override_application_requires_matching_manifest_digest() -> None:
    """A manifest must prove the reviewed override table was applied."""

    with TemporaryDirectory() as tmp:
        directory = Path(tmp)
        override_path = directory / "road_class_overrides.csv"
        manifest_path = directory / "pilot_full_manifest.json"
        _write_override_csv(override_path, source_class="literature-derived")
        _write_manifest(manifest_path, override_path, _file_sha256(override_path))

        summary = audit_road_class_override_application(
            override_path=override_path,
            manifest_path=manifest_path,
        )

        assert summary["publication_ready"] is True
        assert summary["overrides_applied"] is True
        assert summary["path_matches"] is True
        assert summary["sha256_matches"] is True
        assert summary["graph_source_records_override"] is True

    print("PASS: override application accepts matching manifest digest")


def test_override_application_blocks_missing_or_stale_manifest() -> None:
    """A source-backed table alone should not unlock road-calibration claims."""

    with TemporaryDirectory() as tmp:
        directory = Path(tmp)
        override_path = directory / "road_class_overrides.csv"
        manifest_path = directory / "pilot_full_manifest.json"
        _write_override_csv(override_path, source_class="literature-derived")
        _write_manifest(manifest_path, override_path, "0" * 64)

        summary = audit_road_class_override_application(
            override_path=override_path,
            manifest_path=manifest_path,
        )

        assert summary["publication_ready"] is False
        assert summary["sha256_matches"] is False
        assert any("sha256" in blocker for blocker in summary["remaining_blockers"])

    print("PASS: override application blocks stale manifest digest")


def _write_override_csv(
    path: Path,
    *,
    source_class: str,
    base_p_fail_source_class: str | None = None,
) -> None:
    row = {
        "highway": "primary",
        "speed_kph": "42",
        "capacity_veh_per_hr": "1234",
        "base_p_fail": "0.01",
        "source_class": source_class,
        "source_name": "fixture",
        "source_url_or_citation": "fixture",
        "notes": "fixture row",
    }
    if base_p_fail_source_class is not None:
        row.update(
            {
                "speed_source_class": source_class,
                "speed_source_name": "fixture",
                "speed_source_url_or_citation": "fixture",
                "capacity_source_class": source_class,
                "capacity_source_name": "fixture",
                "capacity_source_url_or_citation": "fixture",
                "base_p_fail_source_class": base_p_fail_source_class,
                "base_p_fail_source_name": "fixture",
                "base_p_fail_source_url_or_citation": "fixture",
            }
        )
    fieldnames = (
        REQUIRED_COLUMNS
        if base_p_fail_source_class is None
        else REQUIRED_COLUMNS + OPTIONAL_FIELD_SOURCE_COLUMNS
    )
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(row)


def _write_manifest(path: Path, override_path: Path, digest: str) -> None:
    manifest = {
        "road_class_overrides_applied": True,
        "graph_source": f"cached_graphml:g.graphml;road_class_overrides:{override_path}",
        "inputs": {
            "road_class_overrides_path": str(override_path),
            "road_class_overrides_sha256": digest,
        },
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle)


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    test_missing_default_override_table_is_reported_not_failed()
    test_strong_override_fixture_can_pass_source_strength_gate()
    test_weak_override_fixture_blocks_publication_readiness()
    test_field_level_weak_source_blocks_publication_readiness()
    test_override_application_requires_matching_manifest_digest()
    test_override_application_blocks_missing_or_stale_manifest()
    print("\n=== REALWORLD ROAD OVERRIDE AUDIT TESTS PASSED ===")
