"""Tests for formal acceptance evidence-path hygiene auditing."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.formal_evidence_path_audit import (  # noqa: E402
    audit_formal_evidence_paths,
    write_formal_evidence_path_audit,
)


def test_formal_evidence_path_audit_blocks_current_empty_package() -> None:
    """No formal artifacts should mean no path-based completion."""

    summary = audit_formal_evidence_paths()

    assert summary["artifact_count"] >= 11
    assert summary["present_artifact_count"] >= 0
    assert summary["evidence_item_count"] >= 1
    assert summary["can_mark_complete"] is False
    assert summary["formal_evidence_paths_ready"] is False

    print("PASS: empty formal evidence package remains blocked")


def test_formal_evidence_path_audit_flags_placeholders_and_missing_paths() -> None:
    """Formal JSON evidence paths should resolve to concrete files."""

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        evidence = root / "docs" / "evidence.md"
        evidence.parent.mkdir(parents=True)
        evidence.write_text("reviewed evidence\n", encoding="utf-8")
        target = root / "data" / "manifests" / "pilot_acceptance.json"
        target.parent.mkdir(parents=True)
        target.write_text(
            json.dumps(
                {
                    "evidence_paths": [
                        "docs/evidence.md",
                        "docs/missing.md",
                        "REVIEW_REQUIRED",
                        "https://example.com/source",
                    ]
                }
            ),
            encoding="utf-8",
        )

        summary = audit_formal_evidence_paths(root=root)

    assert summary["present_artifact_count"] == 1
    assert summary["evidence_item_count"] == 4
    assert summary["status_counts"]["present_local_evidence"] == 1
    assert summary["status_counts"]["missing_local_evidence"] == 1
    assert summary["status_counts"]["placeholder_evidence"] == 1
    assert summary["status_counts"]["external_reference_needs_review"] == 1
    assert summary["can_mark_complete"] is False
    assert summary["remaining_blockers"]

    print("PASS: formal evidence path audit flags weak JSON evidence paths")


def test_formal_evidence_path_audit_reads_csv_evidence_paths() -> None:
    """CSV acceptance records should be checked row by row."""

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        evidence = root / "docs" / "parameter.md"
        evidence.parent.mkdir(parents=True)
        evidence.write_text("parameter evidence\n", encoding="utf-8")
        target = root / "data" / "parameters" / "parameter_acceptance.csv"
        target.parent.mkdir(parents=True)
        with target.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["parameter", "evidence_paths"])
            writer.writeheader()
            writer.writerow(
                {
                    "parameter": "bus.capacity",
                    "evidence_paths": "docs/parameter.md; docs/missing.md",
                }
            )

        summary = audit_formal_evidence_paths(root=root)

    assert summary["present_artifact_count"] == 1
    assert summary["status_counts"]["present_local_evidence"] == 1
    assert summary["status_counts"]["missing_local_evidence"] == 1
    assert summary["can_mark_complete"] is False

    print("PASS: formal evidence path audit reads CSV evidence paths")


def test_write_formal_evidence_path_audit_outputs_json_and_markdown() -> None:
    """Writer should emit non-acceptance JSON and markdown artifacts."""

    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        manifest = root / "manifest.json"
        doc = root / "audit.md"
        summary = write_formal_evidence_path_audit(
            root=root,
            manifest_path=manifest,
            doc_path=doc,
        )
        loaded = json.loads(manifest.read_text(encoding="utf-8"))
        text = doc.read_text(encoding="utf-8")

    assert summary["can_mark_complete"] is False
    assert loaded["can_mark_complete"] is False
    assert "Formal Evidence Path Audit" in text
    assert "does not approve the evidence" in text

    print("PASS: formal evidence path audit writer emits artifacts")


if __name__ == "__main__":
    test_formal_evidence_path_audit_blocks_current_empty_package()
    test_formal_evidence_path_audit_flags_placeholders_and_missing_paths()
    test_formal_evidence_path_audit_reads_csv_evidence_paths()
    test_write_formal_evidence_path_audit_outputs_json_and_markdown()
    print("\n=== REALWORLD FORMAL EVIDENCE PATH AUDIT TESTS PASSED ===")
