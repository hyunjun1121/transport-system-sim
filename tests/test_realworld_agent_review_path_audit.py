"""Tests for sub-agent review-record path hygiene."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.agent_review_path_audit import (  # noqa: E402
    audit_agent_review_paths,
    write_agent_review_path_audit,
)
from src.realworld.acceptance_orchestration import (  # noqa: E402
    write_acceptance_orchestration_outputs,
)


def test_agent_review_path_audit_allows_missing_formal_targets_only() -> None:
    write_acceptance_orchestration_outputs()
    summary = audit_agent_review_paths()
    assert summary["record_count"] == 12
    assert summary["invalid_record_count"] == 0
    assert summary["missing_required_path_count"] == 0
    assert summary["missing_formal_target_count"] >= 1
    assert summary["agent_review_paths_ready"] is True
    assert summary["can_mark_complete"] is False


def test_agent_review_path_audit_flags_missing_required_path() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        review_dir = root / "agent_reviews"
        review_dir.mkdir()
        record = {
            "gate_id": "pilot_region_accepted",
            "agent": "Pilot Region & Privacy Review Agent",
            "status": "needs_human_review",
            "decision": "review needed",
            "evidence": ["docs/missing_required.md"],
            "source_paths": ["data/manifests/pilot_acceptance.json"],
            "reviewed_inputs": ["docs/missing_required.md"],
            "risks": ["missing evidence"],
            "required_actions": ["add evidence"],
            "generated_at": "2026-05-04T00:00:00+00:00",
            "can_mark_complete": False,
        }
        (review_dir / "pilot.json").write_text(
            json.dumps(record),
            encoding="utf-8",
        )
        summary = audit_agent_review_paths(root=root, review_dir=review_dir)
    assert summary["agent_review_paths_ready"] is False
    assert summary["missing_required_path_count"] == 2
    assert summary["missing_formal_target_count"] == 1


def test_write_agent_review_path_audit_outputs_files() -> None:
    write_acceptance_orchestration_outputs()
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        summary = write_agent_review_path_audit(
            manifest_path=root / "agent_review_path_audit.json",
            doc_path=root / "agent_review_path_audit.md",
        )
        loaded = json.loads((root / "agent_review_path_audit.json").read_text())
        assert loaded["record_count"] == summary["record_count"]
        assert (root / "agent_review_path_audit.md").exists()
        assert summary["can_mark_complete"] is False


if __name__ == "__main__":
    test_agent_review_path_audit_allows_missing_formal_targets_only()
    test_agent_review_path_audit_flags_missing_required_path()
    test_write_agent_review_path_audit_outputs_files()
    print("PASS: agent review path audit")
