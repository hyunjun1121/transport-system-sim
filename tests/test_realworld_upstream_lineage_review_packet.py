"""Tests for Phase 9 upstream lineage review packet."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.upstream_lineage_review_packet import (  # noqa: E402
    AFFECTED_ARTIFACTS_BY_ROW,
    CLAIM_BOUNDARY,
    SOURCE_ACTION_BATCH,
    build_upstream_lineage_review_rows,
    write_upstream_lineage_review_packet,
)


def test_upstream_lineage_rows_cover_current_batch_without_signoff() -> None:
    rows = build_upstream_lineage_review_rows()

    assert len(rows) == 10
    assert {row["invalidation_row_id"] for row in rows} == set(AFFECTED_ARTIFACTS_BY_ROW)
    assert {row["action_batch"] for row in rows} == {SOURCE_ACTION_BATCH}
    assert {row["reviewer_signoff_status"] for row in rows} == {"unsigned"}
    assert {row["packet_can_close_row"] for row in rows} == {"false"}
    assert {row["claim_boundary"] for row in rows} == {CLAIM_BOUNDARY}
    assert all(int(row["affected_artifact_count"]) > 0 for row in rows)
    assert all(int(row["missing_artifact_count"]) == 0 for row in rows)

    road_snapshot = _row(rows, "region_boundary->road_snapshots")
    artifacts = json.loads(road_snapshot["affected_artifacts_json"])
    assert any(item["path"].endswith("road_snapshot_manifest.json") for item in artifacts)
    assert all(item["exists"] is True for item in artifacts)
    assert all(item["sha256"] for item in artifacts if item["path"].endswith((".csv", ".json", ".graphml", ".md")))

    print("PASS: upstream lineage rows cover current batch without signoff")


def test_upstream_lineage_writer_emits_non_acceptance_artifacts() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        output = root / "packet.csv"
        manifest = root / "packet.json"
        doc = root / "packet.md"

        summary = write_upstream_lineage_review_packet(
            output_path=output,
            manifest_path=manifest,
            doc_path=doc,
        )

        assert output.exists()
        assert manifest.exists()
        assert doc.exists()
        assert summary["row_count"] == 10
        assert summary["missing_artifact_count"] == 0
        assert summary["reviewer_signoff_status_counts"] == {"unsigned": 10}
        assert summary["packet_can_close_row_count"] == 0
        assert summary["can_clear_invalidation_gate"] is False
        assert summary["phase9_promotion_ready"] is False
        assert summary["publication_ready"] is False
        assert summary["final_study_ready"] is False
        assert summary["formal_acceptance_evidence"] is False
        assert summary["can_mark_complete"] is False
        assert "not an artifact-invalidation closeout record" in summary["claim_boundary"]

    print("PASS: upstream lineage writer emits non-acceptance artifacts")


def _row(rows: list[dict[str, str]], row_id: str) -> dict[str, str]:
    matches = [row for row in rows if row["invalidation_row_id"] == row_id]
    assert len(matches) == 1
    return matches[0]


if __name__ == "__main__":
    test_upstream_lineage_rows_cover_current_batch_without_signoff()
    test_upstream_lineage_writer_emits_non_acceptance_artifacts()
    print("\n=== REALWORLD UPSTREAM LINEAGE REVIEW PACKET TESTS PASSED ===")
