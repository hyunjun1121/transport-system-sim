"""Tests for formal acceptance artifact placeholder/template guard."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.formal_acceptance_guard import (  # noqa: E402
    audit_formal_acceptance_artifacts,
)


def test_formal_acceptance_guard_blocks_current_missing_final_artifacts() -> None:
    summary = audit_formal_acceptance_artifacts()

    assert summary["artifact_count"] == 12
    assert summary["formal_acceptance_ready"] is False
    assert summary["can_mark_complete"] is False
    assert summary["present_count"] == 0
    assert summary["template_or_placeholder_count"] == 0
    assert summary["missing_count"] == 12
    assert summary["remaining_blockers"]

    print("PASS: formal acceptance guard blocks missing final artifacts")


def test_formal_acceptance_guard_detects_copied_json_template() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        target = root / "data" / "manifests" / "pilot_acceptance.json"
        target.parent.mkdir(parents=True)
        target.write_text(
            json.dumps(
                {
                    "template_only": True,
                    "record_type": "formal_acceptance_template_not_approval",
                    "region_id": "songpa_public_demo",
                    "accepted": False,
                    "accepted_by": "REVIEW_REQUIRED",
                    "accepted_date": "REVIEW_REQUIRED",
                    "acceptance_scope": "REVIEW_REQUIRED",
                    "privacy_review_complete": False,
                    "graph_scale_decision": "corridor_abstraction",
                    "claim_boundary": "TEMPLATE ONLY",
                    "evidence_paths": ["REVIEW_REQUIRED"],
                }
            ),
            encoding="utf-8",
        )

        summary = audit_formal_acceptance_artifacts(
            project_root=root,
            artifacts=("data/manifests/pilot_acceptance.json",),
        )

    assert summary["present_count"] == 1
    assert summary["template_or_placeholder_count"] == 1
    assert summary["checks"][0]["status"] == "blocked_template_or_placeholder"

    print("PASS: formal acceptance guard detects copied JSON template")


def test_formal_acceptance_guard_detects_parameter_template_csv() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        target = root / "data" / "parameters" / "parameter_acceptance.csv"
        target.parent.mkdir(parents=True)
        with target.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "parameter",
                    "accepted",
                    "accepted_by",
                    "accepted_date",
                    "acceptance_scope",
                    "claim_boundary",
                    "sensitivity_reviewed",
                    "evidence_paths",
                    "notes",
                ],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "parameter": "bus_capacity",
                    "accepted": "false",
                    "accepted_by": "REVIEW_REQUIRED",
                    "accepted_date": "REVIEW_REQUIRED",
                    "acceptance_scope": "REVIEW_REQUIRED",
                    "claim_boundary": "TEMPLATE ONLY",
                    "sensitivity_reviewed": "false",
                    "evidence_paths": "REVIEW_REQUIRED",
                    "notes": "template",
                }
            )

        summary = audit_formal_acceptance_artifacts(
            project_root=root,
            artifacts=("data/parameters/parameter_acceptance.csv",),
        )

    assert summary["present_count"] == 1
    assert summary["template_or_placeholder_count"] == 1
    assert summary["checks"][0]["status"] == "blocked_template_or_placeholder"

    print("PASS: formal acceptance guard detects parameter template CSV")


if __name__ == "__main__":
    test_formal_acceptance_guard_blocks_current_missing_final_artifacts()
    test_formal_acceptance_guard_detects_copied_json_template()
    test_formal_acceptance_guard_detects_parameter_template_csv()
    print("\n=== REALWORLD FORMAL ACCEPTANCE GUARD TESTS PASSED ===")
