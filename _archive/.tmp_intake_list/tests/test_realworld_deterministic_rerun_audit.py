"""Tests for deterministic rerun audit rows and outputs."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.deterministic_rerun_audit import (  # noqa: E402
    build_deterministic_rerun_rows,
    write_deterministic_rerun_audit,
)


def test_deterministic_rerun_rows_pass_matching_hashes() -> None:
    rows = _rows()
    summary = [{"policy_id": "bus_only", "run_count": 2}]
    audit_rows = build_deterministic_rerun_rows(
        first_rows=rows,
        second_rows=rows,
        first_summary_rows=summary,
        second_summary_rows=summary,
        metadata=_metadata(),
    )
    by_id = {row["check_id"]: row for row in audit_rows}
    assert by_id["rerun_row_hash_match"]["status"] == "pass"
    assert by_id["rerun_summary_hash_match"]["status"] == "pass"
    assert by_id["rerun_profile_scope"]["status"] == "needs_human_review_profile_scope"
    assert by_id["formal_experiment_acceptance"]["status"].startswith("blocked")


def test_deterministic_rerun_rows_block_mismatched_rows() -> None:
    first = _rows()
    second = _rows(value=0.9)
    audit_rows = build_deterministic_rerun_rows(
        first_rows=first,
        second_rows=second,
        first_summary_rows=[],
        second_summary_rows=[],
        metadata=_metadata(),
    )
    by_id = {row["check_id"]: row for row in audit_rows}
    assert by_id["rerun_row_hash_match"]["status"] == "blocked_rerun_row_hash_mismatch"


def test_write_deterministic_rerun_audit_outputs_files() -> None:
    rows = build_deterministic_rerun_rows(
        first_rows=_rows(),
        second_rows=_rows(),
        first_summary_rows=[],
        second_summary_rows=[],
        metadata=_metadata(),
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        summary = write_deterministic_rerun_audit(
            rows=rows,
            metadata=_metadata(),
            output_path=root / "rerun.csv",
            audit_manifest_path=root / "rerun.json",
            doc_path=root / "rerun.md",
        )
        loaded = json.loads((root / "rerun.json").read_text(encoding="utf-8"))
        doc = (root / "rerun.md").read_text(encoding="utf-8")
    assert loaded["acceptance_ready"] is False
    assert loaded["deterministic_rerun_structurally_ready"] is True
    assert loaded["row_hashes_match"] is True
    assert loaded["summary_hashes_match"] is True
    assert summary["can_mark_complete"] is False
    assert "Deterministic Rerun Audit" in doc


def _rows(*, value: float = 1.0) -> list[dict[str, object]]:
    return [
        {
            "policy_id": "bus_only",
            "scenario_id": "no_disruption",
            "seed": 1,
            "completion_rate": value,
        },
        {
            "policy_id": "baseline_multimodal",
            "scenario_id": "no_disruption",
            "seed": 1,
            "completion_rate": value,
        },
    ]


def _metadata() -> dict[str, object]:
    return {
        "profile_id": "sample_scaffold",
        "run_stage": "sample",
        "sample_scaffold": True,
        "result_scope": "scaffold",
        "policy_count": 2,
        "scenario_count": 1,
        "seed_count": 1,
        "row_count": 2,
        "summary_row_count": 0,
        "inputs": {"design_path": "design.json"},
    }


if __name__ == "__main__":
    test_deterministic_rerun_rows_pass_matching_hashes()
    test_deterministic_rerun_rows_block_mismatched_rows()
    test_write_deterministic_rerun_audit_outputs_files()
    print("PASS: deterministic rerun audit")
