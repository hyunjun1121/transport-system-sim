"""Tests for sub-agent task assignment generation."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.acceptance_task_assignments import (  # noqa: E402
    build_acceptance_task_assignment_rows,
    summarize_acceptance_task_assignments,
    write_acceptance_task_assignments,
)
from src.realworld.formal_acceptance_package import (  # noqa: E402
    build_formal_acceptance_package_summary,
)


def test_task_assignments_cover_current_formal_blockers() -> None:
    summary = build_formal_acceptance_package_summary()
    rows = build_acceptance_task_assignment_rows(package_summary=summary)

    assert len(rows) == 18
    assert {row["can_mark_complete"] for row in rows} == {"false"}
    assert {row["requires_human_review"] for row in rows} == {"true"}
    assert all(row["assigned_agent_id"] for row in rows)
    assert any(
        row["gate_id"] == "road_class_overrides"
        and row["assigned_agent_id"] == "road_rail_parameter_evidence_agent"
        for row in rows
    )
    assert any(
        row["gate_id"] == "final_audit_document"
        and row["assigned_agent_id"] == "final_independent_audit_agent"
        for row in rows
    )


def test_write_task_assignments_outputs_csv_manifest_and_doc() -> None:
    summary = build_formal_acceptance_package_summary()
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        output = root / "assignments.csv"
        manifest = root / "assignments_manifest.json"
        doc = root / "assignments.md"
        value = write_acceptance_task_assignments(
            output_path=output,
            manifest_path=manifest,
            doc_path=doc,
            package_summary=summary,
        )

        assert value["task_count"] == 18
        assert value["assigned_agent_count"] >= 1
        assert value["can_mark_complete"] is False
        assert output.exists()
        assert manifest.exists()
        assert doc.exists()

        with output.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        assert len(rows) == 18
        assert all(row["validation_command"] for row in rows)

        compact = summarize_acceptance_task_assignments(manifest)
        assert compact["manifest_present"] is True
        assert compact["task_count"] == 18
        assert compact["can_mark_complete"] is False


def test_write_task_assignments_preserves_timestamp_when_unchanged() -> None:
    summary = build_formal_acceptance_package_summary()
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        output = root / "assignments.csv"
        manifest = root / "assignments_manifest.json"
        doc = root / "assignments.md"
        write_acceptance_task_assignments(
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

        value = write_acceptance_task_assignments(
            output_path=output,
            manifest_path=manifest,
            doc_path=doc,
            package_summary=summary,
        )
        loaded = json.loads(manifest.read_text(encoding="utf-8"))

        assert value["generated_at"] == "2000-01-01T00:00:00+00:00"
        assert loaded["generated_at"] == "2000-01-01T00:00:00+00:00"


if __name__ == "__main__":
    test_task_assignments_cover_current_formal_blockers()
    test_write_task_assignments_outputs_csv_manifest_and_doc()
    test_write_task_assignments_preserves_timestamp_when_unchanged()
    print("PASS: acceptance task assignments")
