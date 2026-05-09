"""Helpers for stable generated-manifest timestamps."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def preserve_generated_at_when_unchanged(
    manifest: dict[str, Any],
    manifest_path: str | Path,
) -> None:
    """Avoid timestamp-only churn when manifest content is unchanged."""

    path = Path(manifest_path)
    if not path.exists():
        return
    try:
        previous = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    if not isinstance(previous, dict):
        return

    previous_generated_at = previous.get("generated_at")
    if not isinstance(previous_generated_at, str) or not previous_generated_at:
        return

    previous_without_time = dict(previous)
    current_without_time = dict(manifest)
    previous_without_time.pop("generated_at", None)
    current_without_time.pop("generated_at", None)
    if previous_without_time == current_without_time:
        manifest["generated_at"] = previous_generated_at


def write_json_manifest_if_changed(
    manifest: dict[str, Any],
    manifest_path: str | Path,
    *,
    sort_keys: bool = True,
    ensure_ascii: bool = True,
) -> bool:
    """Write a JSON manifest only when the parsed content changed."""

    path = Path(manifest_path)
    if path.exists():
        try:
            previous = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            previous = None
        if previous == manifest:
            return False

    path.write_text(
        json.dumps(manifest, indent=2, sort_keys=sort_keys, ensure_ascii=ensure_ascii)
        + "\n",
        encoding="utf-8",
    )
    return True


__all__ = [
    "preserve_generated_at_when_unchanged",
    "write_json_manifest_if_changed",
]
