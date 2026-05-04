"""Tests for data-provenance acceptance record validation."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.provenance_acceptance import (  # noqa: E402
    load_provenance_acceptance,
    summarize_provenance_acceptance,
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


def test_missing_default_provenance_acceptance_is_blocked() -> None:
    """The current repository should not imply data-provenance acceptance."""

    summary = summarize_provenance_acceptance()

    assert summary["acceptance_ready"] is False
    assert summary["record_present"] is False
    assert summary["remaining_blockers"]

    print("PASS: missing default provenance acceptance is blocked")


def test_provenance_acceptance_fixture_can_pass() -> None:
    """A complete provenance acceptance record can satisfy the narrow gate."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "provenance_acceptance.json"
        _write_acceptance(path)

        record = load_provenance_acceptance(path)
        summary = summarize_provenance_acceptance(path)

        assert record.ready is True
        assert summary["acceptance_ready"] is True
        assert summary["remaining_blockers"] == []

    print("PASS: complete provenance acceptance fixture can pass")


def test_provenance_acceptance_rejects_string_booleans() -> None:
    """Acceptance booleans must not be coerced from strings."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "provenance_acceptance.json"
        _write_acceptance(path)
        value = json.loads(path.read_text(encoding="utf-8"))
        value["license_attribution_reviewed"] = "true"
        path.write_text(json.dumps(value), encoding="utf-8")

        assert_raises_value_error(
            lambda: load_provenance_acceptance(path),
            "must be boolean",
        )

    print("PASS: provenance acceptance rejects string booleans")


def test_provenance_acceptance_requires_source_urls() -> None:
    """Source URLs or citations must be reviewed and recorded."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "provenance_acceptance.json"
        _write_acceptance(path, source_urls_or_citations=[])

        assert_raises_value_error(
            lambda: load_provenance_acceptance(path),
            "source_urls_or_citations",
        )

    print("PASS: provenance acceptance requires source citations")


def test_provenance_acceptance_requires_privacy_review() -> None:
    """Privacy abstraction review is required before final provenance readiness."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "provenance_acceptance.json"
        _write_acceptance(path, privacy_abstraction_reviewed=False)

        summary = summarize_provenance_acceptance(path)

        assert summary["acceptance_ready"] is False
        assert any("privacy_abstraction_reviewed" in item for item in summary["remaining_blockers"])

    print("PASS: provenance acceptance requires privacy review")


def test_provenance_acceptance_requires_not_operational_boundary() -> None:
    """Data provenance acceptance must still block operational claims."""

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "provenance_acceptance.json"
        _write_acceptance(path, claim_boundary="accepted for routing")

        summary = summarize_provenance_acceptance(path)

        assert summary["acceptance_ready"] is False
        assert any("not operational" in item for item in summary["remaining_blockers"])

    print("PASS: provenance acceptance requires not-operational boundary")


def _write_acceptance(
    path: Path,
    *,
    source_urls_or_citations: list[str] | None = None,
    privacy_abstraction_reviewed: bool = True,
    claim_boundary: str = "Accepted for quasi-real decision-support study; not operational routing.",
) -> None:
    value = {
        "region_id": "songpa_public_demo",
        "accepted": True,
        "accepted_by": "fixture reviewer",
        "accepted_date": "2026-05-04",
        "source_snapshot_reviewed": True,
        "license_attribution_reviewed": True,
        "privacy_abstraction_reviewed": privacy_abstraction_reviewed,
        "cache_manifest_reviewed": True,
        "reproducibility_manifest_reviewed": True,
        "source_urls_or_citations": (
            ["https://www.openstreetmap.org/copyright"]
            if source_urls_or_citations is None
            else source_urls_or_citations
        ),
        "data_snapshot_paths": [
            "data/cache/pilot_region_road.graphml",
            "data/cache/pilot_region_road_manifest.json",
        ],
        "evidence_paths": [
            "docs/pilot_region_data_card.md",
            "docs/reproducibility_package.md",
            "data/manifests/reproducibility_manifest.json",
        ],
        "claim_boundary": claim_boundary,
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle)


if __name__ == "__main__":
    test_missing_default_provenance_acceptance_is_blocked()
    test_provenance_acceptance_fixture_can_pass()
    test_provenance_acceptance_rejects_string_booleans()
    test_provenance_acceptance_requires_source_urls()
    test_provenance_acceptance_requires_privacy_review()
    test_provenance_acceptance_requires_not_operational_boundary()
    print("\n=== REALWORLD PROVENANCE ACCEPTANCE TESTS PASSED ===")
