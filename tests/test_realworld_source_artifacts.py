"""Tests for shared real-world source-artifact integrity helpers."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.source_artifacts import (  # noqa: E402
    file_sha256,
    validate_loaded_source_matches_metadata,
    validate_sha256,
    validate_source_artifact_metadata,
)
import src.realworld as realworld  # noqa: E402


def assert_raises_value_error(func, expected_message: str) -> None:
    """Assert that a zero-argument function raises ValueError with context."""

    try:
        func()
    except ValueError as exc:
        message = str(exc)
        assert expected_message in message, message
        return
    raise AssertionError("expected ValueError")


def test_source_artifact_file_hash_must_match() -> None:
    """A retained file artifact should be checked against its SHA256."""

    with TemporaryDirectory() as tmp:
        artifact = Path(tmp) / "source.csv"
        artifact.write_text("id,value\n1,a\n", encoding="utf-8")

        summary = validate_source_artifact_metadata(
            artifact,
            expected_sha256=file_sha256(artifact),
        )

        assert summary["hash_verified"] is True
        assert summary["sha256"] == file_sha256(artifact)

    print("PASS: source artifact file hash must match")


def test_source_artifact_hash_mismatch_is_rejected() -> None:
    """A retained file should not pass with unrelated SHA metadata."""

    with TemporaryDirectory() as tmp:
        artifact = Path(tmp) / "source.csv"
        artifact.write_text("id,value\n1,a\n", encoding="utf-8")

        assert_raises_value_error(
            lambda: validate_source_artifact_metadata(
                artifact,
                expected_sha256="0" * 64,
            ),
            "source artifact SHA256 does not match",
        )

    print("PASS: source artifact hash mismatch is rejected")


def test_loaded_source_must_match_metadata_path() -> None:
    """Loaded records from one file cannot be certified with another file hash."""

    with TemporaryDirectory() as tmp:
        loaded = Path(tmp) / "loaded.csv"
        metadata = Path(tmp) / "metadata.csv"
        loaded.write_text("id,value\n1,a\n", encoding="utf-8")
        metadata.write_text("id,value\n1,b\n", encoding="utf-8")

        assert_raises_value_error(
            lambda: validate_loaded_source_matches_metadata(
                loaded,
                metadata,
                expected_sha256=file_sha256(metadata),
            ),
            "loaded source artifact path",
        )

    print("PASS: loaded source must match metadata path")


def test_malformed_sha_is_rejected() -> None:
    """SHA fields should be explicit 64-hex digests."""

    assert_raises_value_error(
        lambda: validate_sha256("abc", "test SHA"),
        "64-hex",
    )

    print("PASS: malformed SHA is rejected")


def test_source_artifact_helpers_are_exported_with_explicit_names() -> None:
    """Top-level realworld exports should avoid ambiguous generic hash names."""

    with TemporaryDirectory() as tmp:
        artifact = Path(tmp) / "source.csv"
        artifact.write_text("id,value\n1,a\n", encoding="utf-8")

        digest = realworld.source_artifact_file_sha256(artifact)
        summary = realworld.validate_source_artifact_metadata(
            artifact,
            expected_sha256=digest,
        )

        assert digest == file_sha256(artifact)
        assert summary["hash_verified"] is True
        assert realworld.resolve_source_artifact_path(artifact).exists()
        assert realworld.validate_source_artifact_sha256(digest, "digest") == digest
        assert (
            realworld.validate_loaded_source_matches_metadata(
                artifact,
                artifact,
                expected_sha256=digest,
            )["sha256"]
            == digest
        )

    print("PASS: source artifact helpers are exported with explicit names")


if __name__ == "__main__":
    test_source_artifact_file_hash_must_match()
    test_source_artifact_hash_mismatch_is_rejected()
    test_loaded_source_must_match_metadata_path()
    test_malformed_sha_is_rejected()
    test_source_artifact_helpers_are_exported_with_explicit_names()
    print("\n=== REALWORLD SOURCE ARTIFACT TESTS PASSED ===")
