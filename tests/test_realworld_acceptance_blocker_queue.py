"""Tests for formal acceptance blocker queue generation."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.acceptance_blocker_queue import (  # noqa: E402
    build_acceptance_blocker_queue_rows,
    summarize_acceptance_blocker_queue,
    write_acceptance_blocker_queue,
)
from src.realworld.formal_acceptance_package import (  # noqa: E402
    build_formal_acceptance_package_summary,
)


def test_blocker_queue_rows_reflect_current_formal_package() -> None:
    summary = build_formal_acceptance_package_summary()
    rows = build_acceptance_blocker_queue_rows(package_summary=summary)

    assert len(rows) == 18
    assert {row["can_mark_complete"] for row in rows} == {"false"}
    assert {row["requires_human_review"] for row in rows} == {"true"}
    assert any(row["gate_id"] == "road_class_overrides" for row in rows)
    assert any(
        row["template_or_worksheet"] == "data/parameters/road_class_overrides_draft.csv"
        for row in rows
    )


def test_write_blocker_queue_outputs_csv_manifest_and_doc() -> None:
    summary = build_formal_acceptance_package_summary()
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        output = root / "queue.csv"
        manifest = root / "queue_manifest.json"
        doc = root / "queue.md"
        value = write_acceptance_blocker_queue(
            output_path=output,
            manifest_path=manifest,
            doc_path=doc,
            package_summary=summary,
        )

        assert value["row_count"] == 18
        assert value["can_mark_complete"] is False
        assert output.exists()
        assert manifest.exists()
        assert doc.exists()

        with output.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        assert len(rows) == 18
        assert all(row["formal_target"] for row in rows)

        compact = summarize_acceptance_blocker_queue(manifest)
        assert compact["manifest_present"] is True
        assert compact["row_count"] == 18
        assert compact["can_mark_complete"] is False


def test_write_blocker_queue_preserves_timestamp_when_unchanged() -> None:
    summary = build_formal_acceptance_package_summary()
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        output = root / "queue.csv"
        manifest = root / "queue_manifest.json"
        doc = root / "queue.md"
        write_acceptance_blocker_queue(
            output_path=output,
            manifest_path=manifest,
            doc_path=doc,
            package_summary=summary,
        )
        first = json.loads(manifest.read_text(encoding="utf-8"))
        first["generated_at"] = "2000-01-01T00:00:00+00:00"
        manifest.write_text(
            json.dumps(first, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        value = write_acceptance_blocker_queue(
            output_path=output,
            manifest_path=manifest,
            doc_path=doc,
            package_summary=summary,
        )
        loaded = json.loads(manifest.read_text(encoding="utf-8"))

        assert value["generated_at"] == "2000-01-01T00:00:00+00:00"
        assert loaded["generated_at"] == "2000-01-01T00:00:00+00:00"


def test_formal_blocker_queue_wrapper_is_runnable() -> None:
    """Plan-ladder compatibility command should delegate to the queue writer."""

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "write_formal_acceptance_blocker_queue.py"),
            "--help",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0
    assert "--fail-on-blockers" in result.stdout


if __name__ == "__main__":
    test_blocker_queue_rows_reflect_current_formal_package()
    test_write_blocker_queue_outputs_csv_manifest_and_doc()
    test_write_blocker_queue_preserves_timestamp_when_unchanged()
    test_formal_blocker_queue_wrapper_is_runnable()
    print("PASS: formal acceptance blocker queue")
