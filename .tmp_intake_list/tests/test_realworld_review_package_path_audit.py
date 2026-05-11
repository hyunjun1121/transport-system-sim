"""Tests for ZIP-internal expert-review package path audit."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.review_package_path_audit import (  # noqa: E402
    audit_review_package_paths,
    build_review_package_path_audit_markdown,
    write_review_package_path_audit,
)


def test_review_package_path_audit_allows_missing_formal_targets_only() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = Path(tmpdir) / "package.zip"
        _write_package(zip_path, include_review_packet=True)
        summary = audit_review_package_paths(zip_path)
    assert summary["zip_present"] is True
    assert summary["zip_valid"] is True
    assert summary["record_count"] == 1
    assert summary["missing_package_path_count"] == 0
    assert summary["missing_formal_target_count"] == 1
    assert summary["unique_missing_formal_targets"] == [
        "data/manifests/pilot_acceptance.json"
    ]
    assert summary["review_package_paths_ready"] is True
    assert summary["can_mark_complete"] is False
    assert any(
        "expert_review_handoff_20260510.md" in item
        and "expert_review_handoff_20260510.json" in item
        for item in summary["review_items"]
    )
    markdown = build_review_package_path_audit_markdown(summary)
    assert "expert_review_handoff_20260510.md" in markdown
    assert "expert_review_handoff_20260510.json" in markdown


def test_review_package_path_audit_flags_missing_package_paths() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = Path(tmpdir) / "package.zip"
        _write_package(zip_path, include_review_packet=False)
        summary = audit_review_package_paths(zip_path)
    assert summary["review_package_paths_ready"] is False
    assert summary["missing_package_path_count"] == 1
    assert summary["unique_missing_package_paths"] == ["docs/review_packet.md"]
    assert summary["remaining_blockers"] == [
        "include referenced package path: docs/review_packet.md"
    ]


def test_write_review_package_path_audit_outputs_files() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        zip_path = root / "package.zip"
        _write_package(zip_path, include_review_packet=True)
        summary = write_review_package_path_audit(
            zip_path=zip_path,
            manifest_path=root / "review_package_path_audit.json",
            doc_path=root / "review_package_path_audit.md",
        )
        loaded = json.loads(
            (root / "review_package_path_audit.json").read_text(encoding="utf-8")
        )
        doc_exists = (root / "review_package_path_audit.md").exists()
    assert loaded["zip_sha256"] == summary["zip_sha256"]
    assert loaded["review_package_paths_ready"] is True
    assert doc_exists


def _write_package(zip_path: Path, *, include_review_packet: bool) -> None:
    record = {
        "gate_id": "pilot_region_accepted",
        "agent_id": "pilot_region_privacy_review_agent",
        "agent": "Pilot Region & Privacy Review Agent",
        "status": "needs_human_review",
        "decision": "review needed",
        "evidence": ["README.md"],
        "source_paths": ["data/manifests/pilot_acceptance.json"],
        "reviewed_inputs": ["README.md"],
        "review_packet_paths": ["docs/review_packet.md"],
        "risks": ["formal acceptance missing"],
        "required_actions": ["review pilot scope"],
        "generated_at": "2026-05-10T00:00:00+00:00",
        "can_mark_complete": False,
    }
    with ZipFile(zip_path, "w") as archive:
        archive.writestr("README.md", "readme\n")
        archive.writestr(
            "data/manifests/agent_reviews/pilot.json",
            json.dumps(record) + "\n",
        )
        if include_review_packet:
            archive.writestr("docs/review_packet.md", "# Review\n")


if __name__ == "__main__":
    test_review_package_path_audit_allows_missing_formal_targets_only()
    test_review_package_path_audit_flags_missing_package_paths()
    test_write_review_package_path_audit_outputs_files()
    print("PASS: review package path audit")
