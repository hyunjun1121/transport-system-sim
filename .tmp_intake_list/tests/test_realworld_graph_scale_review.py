"""Tests for graph-scale method review packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.graph_scale_review import (  # noqa: E402
    DEFAULT_GRAPH_SCALE_REVIEW_MANIFEST_PATH,
    DEFAULT_GRAPH_SCALE_REVIEW_PACKET_PATH,
    GRAPH_SCALE_REVIEW_COLUMNS,
    GRAPH_SCALE_REVIEW_SCOPE,
    build_graph_scale_review_rows,
    write_graph_scale_review_packet,
)


def test_graph_scale_review_rows_cover_method_options() -> None:
    """The review packet should expose the current graph-scale choices."""

    rows = build_graph_scale_review_rows()
    by_option = {row["option_id"]: row for row in rows}

    assert len(rows) == 4
    assert set(by_option) == {
        "current_reduced_corridor",
        "multi_corridor_candidate",
        "multi_corridor_full_candidate",
        "full_bus_practical_graph",
    }
    assert by_option["current_reduced_corridor"]["alternate_route_warn"] == "6"
    assert by_option["multi_corridor_candidate"]["alternate_route_pass"] == "9"
    assert by_option["multi_corridor_full_candidate"]["experiment_row_count"] == "1890"
    assert (
        by_option["multi_corridor_full_candidate"]["experiment_summary_row_count"]
        == "63"
    )
    assert by_option["full_bus_practical_graph"]["analysis_graph_reduced"] == "false"
    assert {row["claim_boundary"] for row in rows} == {GRAPH_SCALE_REVIEW_SCOPE}

    print("PASS: graph-scale review rows cover method options")


def test_write_graph_scale_review_packet_outputs_csv_and_manifest() -> None:
    """Writer should emit stable CSV fields and non-acceptance manifest."""

    rows = build_graph_scale_review_rows()

    with TemporaryDirectory() as directory:
        output = Path(directory) / "graph_scale_review.csv"
        manifest = Path(directory) / "graph_scale_review_manifest.json"
        value = write_graph_scale_review_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == GRAPH_SCALE_REVIEW_COLUMNS
        with manifest.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)

        assert len(written_rows) == 4
        assert value["publication_ready"] is False
        assert written_manifest["row_count"] == 4
        assert "does not accept a graph-scale method" in written_manifest["claim_boundary"]

    print("PASS: graph-scale review packet writer emits CSV and manifest")


def test_shipped_graph_scale_review_packet_matches_current_options() -> None:
    """Current shipped review packet should match deterministic graph inputs."""

    rows = build_graph_scale_review_rows()

    assert DEFAULT_GRAPH_SCALE_REVIEW_PACKET_PATH.exists()
    assert DEFAULT_GRAPH_SCALE_REVIEW_MANIFEST_PATH.exists()
    with DEFAULT_GRAPH_SCALE_REVIEW_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    with DEFAULT_GRAPH_SCALE_REVIEW_MANIFEST_PATH.open(
        "r",
        encoding="utf-8",
    ) as handle:
        manifest = json.load(handle)

    assert len(written_rows) == len(rows)
    assert [row["option_id"] for row in written_rows] == [
        row["option_id"] for row in rows
    ]
    assert manifest["publication_ready"] is False
    assert manifest["result_scope"] == GRAPH_SCALE_REVIEW_SCOPE

    print("PASS: shipped graph-scale review packet matches current options")


if __name__ == "__main__":
    test_graph_scale_review_rows_cover_method_options()
    test_write_graph_scale_review_packet_outputs_csv_and_manifest()
    test_shipped_graph_scale_review_packet_matches_current_options()
    print("\n=== REALWORLD GRAPH-SCALE REVIEW TESTS PASSED ===")
