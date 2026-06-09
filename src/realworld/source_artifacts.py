"""Shared source-artifact integrity helpers for real-world evidence rows."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def file_sha256(path: str | Path) -> str:
    """Return the SHA256 digest for a retained source artifact file."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_source_artifact_metadata(
    path: str | Path,
    *,
    expected_sha256: str,
) -> dict[str, Any]:
    """Validate retained source-artifact path and SHA metadata.

    File artifacts are hash-verified directly. Directory artifacts cannot be
    reduced to a stable single-file hash here, so this function verifies only
    that a 64-hex digest was supplied and that the directory exists.
    """

    digest = validate_sha256(expected_sha256, "source artifact SHA256")
    artifact_path = resolve_artifact_path(path)
    if artifact_path.is_file():
        actual = file_sha256(artifact_path)
        if actual.lower() != digest:
            raise ValueError("source artifact SHA256 does not match retained source file")
        return {
            "path": str(artifact_path),
            "sha256": actual,
            "hash_verified": True,
        }
    if artifact_path.is_dir():
        return {
            "path": str(artifact_path),
            "sha256": digest,
            "hash_verified": False,
        }
    raise ValueError("source_artifact_path must reference a retained source file or directory")


def validate_loaded_source_matches_metadata(
    loaded_path: str | Path,
    metadata_path: str | Path,
    *,
    expected_sha256: str,
) -> dict[str, Any]:
    """Validate artifact metadata and require it to match the loaded source."""

    summary = validate_source_artifact_metadata(
        metadata_path,
        expected_sha256=expected_sha256,
    )
    loaded = resolve_artifact_path(loaded_path)
    metadata = resolve_artifact_path(metadata_path)
    if _resolved_identity(loaded) != _resolved_identity(metadata):
        raise ValueError("loaded source artifact path does not match source_artifact_path")
    return summary


def resolve_artifact_path(path: str | Path) -> Path:
    """Resolve an artifact path as-is first, then relative to the project root."""

    artifact_path = Path(path)
    if artifact_path.exists():
        return artifact_path
    project_path = PROJECT_ROOT / artifact_path
    if project_path.exists():
        return project_path
    return artifact_path


def _resolved_identity(path: Path) -> str:
    try:
        return str(path.resolve()).lower()
    except OSError:
        return str(path).lower()


def validate_sha256(value: object, label: str) -> str:
    """Return a lowercase digest after requiring a 64-hex SHA256 value."""

    digest = "" if value is None else str(value).strip().lower()
    if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise ValueError(f"{label} must be a 64-hex digest")
    return digest


__all__ = [
    "file_sha256",
    "resolve_artifact_path",
    "validate_sha256",
    "validate_loaded_source_matches_metadata",
    "validate_source_artifact_metadata",
]
