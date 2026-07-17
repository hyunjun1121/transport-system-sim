"""Tests for source provenance manifest diagnostics."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.source_provenance import (  # noqa: E402
    load_source_provenance_manifest,
    summarize_source_provenance_manifest,
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


def test_shipped_source_provenance_manifest_is_diagnosable() -> None:
    """The current manifest should be structurally ready but not accepted."""

    summary = summarize_source_provenance_manifest()

    assert summary["diagnostics_ready"] is True
    assert summary["manifest_present"] is True
    assert summary["record_count"] >= 8
    assert summary["remaining_blockers"] == []
    assert summary["review_items"]
    assert any("sensitivity/context-only" in item for item in summary["review_items"])
    assert summary["local_artifact_count"] >= 30
    assert summary["review_status_counts"]["context_only_not_cached"] >= 1
    assert "not operational" in summary["claim_boundary"]

    print("PASS: shipped source provenance manifest is diagnosable")


def test_source_provenance_rejects_missing_required_fields() -> None:
    """Manifest records should not silently omit required provenance fields."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "source_provenance_manifest.json"
        value = _manifest_value()
        del value["records"][0]["license_or_terms"]
        path.write_text(json.dumps(value), encoding="utf-8")

        assert_raises_value_error(
            lambda: load_source_provenance_manifest(path),
            "missing fields",
        )

    print("PASS: source provenance rejects missing required fields")


def test_source_provenance_reports_missing_local_artifact() -> None:
    """Missing artifact paths should be structural blockers for review packets."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "source_provenance_manifest.json"
        value = _manifest_value()
        value["records"][0]["local_artifact_paths"] = ["missing/artifact.csv"]
        path.write_text(json.dumps(value), encoding="utf-8")

        summary = summarize_source_provenance_manifest(path)

        assert summary["diagnostics_ready"] is False
        assert any("missing local artifacts" in item for item in summary["remaining_blockers"])

    print("PASS: source provenance reports missing local artifact")


def test_source_provenance_requires_not_operational_boundary() -> None:
    """The manifest must not open an operational claim boundary."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "source_provenance_manifest.json"
        value = _manifest_value()
        value["claim_boundary"] = "accepted for operational routing"
        path.write_text(json.dumps(value), encoding="utf-8")

        summary = summarize_source_provenance_manifest(path)

        assert summary["diagnostics_ready"] is False
        assert any("not operational" in item for item in summary["remaining_blockers"])

    print("PASS: source provenance requires not-operational boundary")


def _manifest_value() -> dict[str, object]:
    return {
        "schema_version": 1,
        "region_id": "songpa_public_demo",
        "claim_boundary": "review packet only; not operational routing.",
        "records": [
            {
                "source_id": "fixture_source",
                "source_name": "Fixture source",
                "source_type": "repository_input",
                "source_url_or_citation": "plan.md",
                "license_or_terms": "project-owned fixture",
                "snapshot_or_access_date": "2026-05-04",
                "local_artifact_paths": ["plan.md"],
                "used_for": "test fixture",
                "review_status": "repository_input_pending_review",
                "claim_boundary": "fixture only; not operational routing.",
                "notes": "test row",
            }
        ],
    }


if __name__ == "__main__":
    test_shipped_source_provenance_manifest_is_diagnosable()
    test_source_provenance_rejects_missing_required_fields()
    test_source_provenance_reports_missing_local_artifact()
    test_source_provenance_requires_not_operational_boundary()
    print("\n=== REALWORLD SOURCE PROVENANCE TESTS PASSED ===")
