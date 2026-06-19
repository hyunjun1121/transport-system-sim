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
        record["recommendation"] == "recommended_approve"
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
    assert all(record["review_packets"] for record in records)
    assert all(record["source_paths"] for record in records)
    assert all(record["reviewed_inputs"] for record in records)
    assert all(record["evidence_checked"] for record in records)
    assert all(record.get("missing_evidence", []) is not None for record in records)
    by_gate = {record["gate"]: record for record in records}
    assert "data/manifests/source_url_review_packet.csv" in (
        by_gate["data_provenance"]["review_packets"]
    )
    assert "data/manifests/source_url_review_packet.csv" in (
        by_gate["data_provenance"]["source_paths"]
    )


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
        assert "Formal Gate Pre-Review" in text
        assert "Draft pre-review recommendations only" in text
        assert "source-backed human approval exists" not in text
        assert "formal approval if copied into a final acceptance path" not in text
        assert "Blocked non-approval item:" in text

        compact = summarize_formal_acceptance_pre_review(manifest_path)
        assert compact["manifest_present"] is True
        assert compact["record_count"] == 12
        assert compact["can_mark_complete"] is False


def test_write_pre_review_preserves_timestamps_when_unchanged() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        out_dir = root / "draft_acceptance"
        manifest_path = out_dir / "manifest.json"
        doc_path = root / "formal_acceptance_pre_review.md"
        write_formal_acceptance_pre_review(
            output_dir=out_dir,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )
        first_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        first_manifest["generated_at"] = "2000-01-01T00:00:00+00:00"
        manifest_path.write_text(
            json.dumps(first_manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        first_record_path = next(out_dir.glob("*_pre_review.json"))
        first_record = json.loads(first_record_path.read_text(encoding="utf-8"))
        first_record["generated_at"] = "2000-01-01T00:00:00+00:00"
        first_record_path.write_text(
            json.dumps(first_record, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        manifest = write_formal_acceptance_pre_review(
            output_dir=out_dir,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )
        loaded_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        loaded_record = json.loads(first_record_path.read_text(encoding="utf-8"))

        assert manifest["generated_at"] == "2000-01-01T00:00:00+00:00"
        assert loaded_manifest["generated_at"] == "2000-01-01T00:00:00+00:00"
        assert loaded_record["generated_at"] == "2000-01-01T00:00:00+00:00"


if __name__ == "__main__":
    test_pre_review_records_cover_current_formal_targets_without_approval()
    test_write_pre_review_outputs_draft_only_artifacts()
    test_write_pre_review_preserves_timestamps_when_unchanged()
    print("PASS: formal acceptance pre-review remains draft-only")
