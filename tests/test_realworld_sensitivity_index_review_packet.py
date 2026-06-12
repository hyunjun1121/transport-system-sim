"""Tests for metric-level Morris index review packet."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.sensitivity_index_review_packet import (  # noqa: E402
    DEFAULT_SENSITIVITY_INDEX_REVIEW_MANIFEST_PATH,
    DEFAULT_SENSITIVITY_INDEX_REVIEW_PACKET_PATH,
    SENSITIVITY_INDEX_REVIEW_COLUMNS,
    SENSITIVITY_INDEX_REVIEW_SCOPE,
    build_sensitivity_index_review_rows,
    write_sensitivity_index_review_packet,
)


def test_sensitivity_index_rows_summarize_current_metrics() -> None:
    """Current Morris summary should yield one review row per metric."""

    rows = build_sensitivity_index_review_rows()
    by_metric = {row["metric"]: row for row in rows}

    assert len(rows) == 7
    assert by_metric["p80_arrival_time"]["unavailable_index_rows"] == "2436"
    assert by_metric["p95_arrival_time"]["unavailable_index_rows"] == "2436"
    assert by_metric["completion_rate"]["zero_mu_star_rows"] == "7386"
    assert by_metric["completion_rate"]["all_zero_groups"] == "456"
    assert by_metric["censored_count"]["positive_mu_star_rows"] == "479"
    assert by_metric["p80_arrival_time"]["affected_unavailable_scenarios"] == (
        "no_disruption; songpa_access_origin_to_destination; songpa_access_origin_to_station; songpa_combo_access_rail_capacity; songpa_combo_tancheon_rail_delay; songpa_critical_link_blockage; songpa_last_mile_station_to_destination; songpa_rail_capacity_reduction; songpa_rail_combined_stress; songpa_rail_combined_stress_mild; songpa_rail_combined_stress_severe; songpa_rail_delay; songpa_rail_delay_mild; songpa_rail_delay_severe; songpa_rail_station_access; songpa_rail_unavailable; songpa_random_blockage; songpa_random_capacity_reduction; songpa_spatial_assembly_egress; songpa_spatial_feeder_east; songpa_spatial_lastmile_west; songpa_spatial_tancheon_corridor; songpa_transfer_point_blockage"
    )
    assert by_metric["p80_arrival_time"]["index_review_status"] == (
        "needs_human_review_unavailable_indices"
    )
    assert {row["claim_boundary"] for row in rows} == {
        SENSITIVITY_INDEX_REVIEW_SCOPE
    }
    assert all(row["can_support_sensitivity_gate"] == "false" for row in rows)

    print("PASS: sensitivity index review rows summarize current metrics")


def test_sensitivity_index_writer_outputs_artifacts() -> None:
    """Writer should emit stable CSV, manifest, and Markdown artifacts."""

    rows = build_sensitivity_index_review_rows()
    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "sensitivity_index_review.csv"
        manifest_path = root / "manifest.json"
        doc_path = root / "review.md"
        manifest = write_sensitivity_index_review_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == SENSITIVITY_INDEX_REVIEW_COLUMNS
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        doc_text = doc_path.read_text(encoding="utf-8")

    assert len(written_rows) == len(rows)
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert written_manifest["unavailable_index_row_count"] == 4872
    assert written_manifest["zero_mu_star_row_count"] == 29601
    assert "Sensitivity Index Review Packet" in doc_text

    print("PASS: sensitivity index review writer emits artifacts")


def test_shipped_sensitivity_index_review_packet_matches_current_outputs() -> None:
    """Committed index review packet should match current Morris artifacts."""

    rows = build_sensitivity_index_review_rows()

    assert DEFAULT_SENSITIVITY_INDEX_REVIEW_PACKET_PATH.exists()
    assert DEFAULT_SENSITIVITY_INDEX_REVIEW_MANIFEST_PATH.exists()
    with DEFAULT_SENSITIVITY_INDEX_REVIEW_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    manifest = json.loads(
        DEFAULT_SENSITIVITY_INDEX_REVIEW_MANIFEST_PATH.read_text(encoding="utf-8")
    )

    assert len(written_rows) == len(rows)
    assert [row["metric"] for row in written_rows] == [row["metric"] for row in rows]
    assert manifest["row_count"] == 7
    assert manifest["unavailable_index_row_count"] == 4872
    assert manifest["zero_mu_star_row_count"] == 29601
    assert manifest["positive_mu_star_row_count"] == 19623
    assert manifest["all_zero_group_count"] == 954
    assert manifest["unavailable_group_count"] == 348
    assert manifest["publication_ready"] is False

    print("PASS: shipped sensitivity index review packet matches current outputs")


if __name__ == "__main__":
    test_sensitivity_index_rows_summarize_current_metrics()
    test_sensitivity_index_writer_outputs_artifacts()
    test_shipped_sensitivity_index_review_packet_matches_current_outputs()
    print("\n=== REALWORLD SENSITIVITY INDEX REVIEW TESTS PASSED ===")
