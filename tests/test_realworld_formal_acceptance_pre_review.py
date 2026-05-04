"""Tests for draft-only formal acceptance pre-review recommendations."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.formal_acceptance_pre_review import (  # noqa: E402
    RECOMMENDATIONS,
    build_formal_acceptance_pre_review_records,
    summarize_formal_acceptance_pre_review,
    write_formal_acceptance_pre_review,
)


def test_pre_review_records_cover_current_formal_targets_without_approval() -> None:
    records = build_formal_acceptance_pre_review_records()

    assert len(records) == 12
    assert {record["formal_approval"] for record in records} == {False}
    assert {record["can_mark_complete"] for record in records} == {False}
    assert {record["final_study_ready"] for record in records} == {False}
    assert {record["human_decision_required"] for record in records} == {True}
    assert set(record["recommendation"] for record in records) <= set(RECOMMENDATIONS)
    assert any(
        record["recommendation"] == "blocked_requires_human_decision"
        for record in records
    )
    assert any(
        record["recommendation"] == "blocked_missing_evidence"
        for record in records
    )
    assert all(
        record["must_not_be_used_as_final_acceptance"] is True
        for record in records
    )
    assert all(record["evidence_checked"] for record in records)
    assert all(record["missing_evidence"] for record in records)


def test_write_pre_review_outputs_draft_only_artifacts() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        out_dir = root / "draft_acceptance"
        manifest_path = out_dir / "manifest.json"
        doc_path = root / "formal_acceptance_pre_review.md"

        manifest = write_formal_acceptance_pre_review(
            output_dir=out_dir,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )
        loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
        text = doc_path.read_text(encoding="utf-8")

        assert manifest["record_count"] == 12
        assert loaded["formal_approval"] is False
        assert loaded["can_mark_complete"] is False
        assert loaded["must_not_be_used_as_final_acceptance"] is True
        assert len(list(out_dir.glob("*_pre_review.json"))) == 12
        assert "Formal Acceptance Pre-Review" in text
        assert "Draft pre-review recommendations only" in text

        compact = summarize_formal_acceptance_pre_review(manifest_path)
        assert compact["manifest_present"] is True
        assert compact["record_count"] == 12
        assert compact["can_mark_complete"] is False


if __name__ == "__main__":
    test_pre_review_records_cover_current_formal_targets_without_approval()
    test_write_pre_review_outputs_draft_only_artifacts()
    print("PASS: formal acceptance pre-review remains draft-only")
