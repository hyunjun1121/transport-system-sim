"""Tests for stable generated-manifest timestamp helpers."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.manifest_timestamp import (  # noqa: E402
    preserve_generated_at_when_unchanged,
    write_json_manifest_if_changed,
    write_text_if_changed,
)


def test_preserve_generated_at_when_manifest_content_matches() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "manifest.json"
        path.write_text(
            json.dumps(
                {
                    "generated_at": "2000-01-01T00:00:00+00:00",
                    "row_count": 3,
                }
            ),
            encoding="utf-8",
        )
        manifest = {
            "generated_at": "2099-01-01T00:00:00+00:00",
            "row_count": 3,
        }

        preserve_generated_at_when_unchanged(manifest, path)

        assert manifest["generated_at"] == "2000-01-01T00:00:00+00:00"


def test_preserve_generated_at_keeps_new_timestamp_when_content_changes() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "manifest.json"
        path.write_text(
            json.dumps(
                {
                    "generated_at": "2000-01-01T00:00:00+00:00",
                    "row_count": 3,
                }
            ),
            encoding="utf-8",
        )
        manifest = {
            "generated_at": "2099-01-01T00:00:00+00:00",
            "row_count": 4,
        }

        preserve_generated_at_when_unchanged(manifest, path)

        assert manifest["generated_at"] == "2099-01-01T00:00:00+00:00"


def test_write_json_manifest_skips_equivalent_content() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "manifest.json"
        original_bytes = b'{\r\n  "row_count": 3\r\n}\r\n'
        path.write_bytes(original_bytes)

        changed = write_json_manifest_if_changed({"row_count": 3}, path)

        assert changed is False
        assert path.read_bytes() == original_bytes


def test_write_json_manifest_treats_tuple_like_json_array() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "manifest.json"
        original_bytes = b'{\r\n  "items": [\r\n    "a"\r\n  ]\r\n}\r\n'
        path.write_bytes(original_bytes)

        changed = write_json_manifest_if_changed({"items": ("a",)}, path)

        assert changed is False
        assert path.read_bytes() == original_bytes


def test_write_json_manifest_writes_changed_content() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "manifest.json"
        path.write_text('{"row_count": 3}', encoding="utf-8")

        changed = write_json_manifest_if_changed({"row_count": 4}, path)
        loaded = json.loads(path.read_text(encoding="utf-8"))

        assert changed is True
        assert loaded["row_count"] == 4


def test_write_text_if_changed_skips_logically_equal_text() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "packet.md"
        original_bytes = b"# Packet\r\n\r\nNo changes.\r\n"
        path.write_bytes(original_bytes)

        changed = write_text_if_changed("# Packet\n\nNo changes.\n", path)

        assert changed is False
        assert path.read_bytes() == original_bytes


if __name__ == "__main__":
    test_preserve_generated_at_when_manifest_content_matches()
    test_preserve_generated_at_keeps_new_timestamp_when_content_changes()
    test_write_json_manifest_skips_equivalent_content()
    test_write_json_manifest_treats_tuple_like_json_array()
    test_write_json_manifest_writes_changed_content()
    test_write_text_if_changed_skips_logically_equal_text()
    print("PASS: manifest timestamp helpers")
