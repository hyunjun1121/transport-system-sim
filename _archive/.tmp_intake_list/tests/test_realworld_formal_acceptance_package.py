"""Tests for the formal acceptance package intake audit."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.formal_acceptance_package import (
    build_formal_acceptance_package_markdown,
    build_formal_acceptance_package_summary,
    write_formal_acceptance_package_audit,
)


def test_formal_acceptance_package_blocks_current_scaffold() -> None:
    summary = build_formal_acceptance_package_summary()

    assert summary["gate_count"] == 12
    assert summary["ready_gate_count"] == 0
    assert summary["blocked_gate_count"] == 12
    assert summary["formal_acceptance_ready"] is False
    assert summary["final_study_ready"] is False
    assert summary["can_mark_complete"] is False
    assert summary["formal_acceptance_guard"]["missing_count"] == 12
    assert summary["formal_evidence_path_audit"]["present_artifact_count"] == 0
    assert summary["formal_evidence_path_audit"]["can_mark_complete"] is False
    assert summary["remaining_blockers"]


def test_formal_acceptance_package_detects_template_in_formal_path() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        target = root / "data" / "manifests" / "pilot_acceptance.json"
        target.parent.mkdir(parents=True)
        target.write_text(
            json.dumps(
                {
                    "record_type": "formal_acceptance_template_not_approval",
                    "template_only": True,
                    "gate_id": "pilot_region_accepted",
                    "accepted": False,
                    "accepted_by": "REVIEW_REQUIRED",
                }
            ),
            encoding="utf-8",
        )

        summary = build_formal_acceptance_package_summary(root=root)

    assert summary["can_mark_complete"] is False
    assert summary["invalid_gate_count"] >= 1
    assert summary["formal_acceptance_guard"]["template_or_placeholder_count"] == 1
    assert summary["formal_evidence_path_audit"]["present_artifact_count"] == 1
    assert summary["formal_evidence_path_audit"]["empty_evidence_record_count"] == 1
    assert any(
        "pilot_region_accepted" in blocker for blocker in summary["remaining_blockers"]
    )


def test_write_formal_acceptance_package_outputs_non_ready_audit() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        manifest = Path(tmpdir) / "package.json"
        doc = Path(tmpdir) / "package.md"
        summary = write_formal_acceptance_package_audit(
            manifest_path=manifest,
            doc_path=doc,
        )
        loaded = json.loads(manifest.read_text(encoding="utf-8"))
        text = doc.read_text(encoding="utf-8")

    assert summary["can_mark_complete"] is False
    assert loaded["can_mark_complete"] is False
    assert "Formal Acceptance Package Audit" in text
    assert "does not create approvals" in text
    assert "Evidence Path Summary" in text
    assert "Can mark complete: `false`" in text
    assert build_formal_acceptance_package_markdown(summary)


if __name__ == "__main__":
    test_formal_acceptance_package_blocks_current_scaffold()
    test_formal_acceptance_package_detects_template_in_formal_path()
    test_write_formal_acceptance_package_outputs_non_ready_audit()
    print("PASS: formal acceptance package audit remains non-approval")
