"""Tests for full experiment-package review packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.experiment_package_review_packet import (  # noqa: E402
    DEFAULT_EXPERIMENT_PACKAGE_REVIEW_MANIFEST_PATH,
    DEFAULT_EXPERIMENT_PACKAGE_REVIEW_PACKET_PATH,
    EXPERIMENT_PACKAGE_REVIEW_COLUMNS,
    EXPERIMENT_PACKAGE_REVIEW_SCOPE,
    build_experiment_package_review_rows,
    write_experiment_package_review_packet,
)


def test_experiment_package_rows_summarize_current_full_outputs() -> None:
    """Current full pilot outputs should become conservative review rows."""

    rows = build_experiment_package_review_rows()
    by_category = {row["category_id"]: row for row in rows}

    assert len(rows) == 9
    assert by_category["results_row_count"]["row_count"] == "1890"
    assert by_category["results_row_count"]["expected_row_count"] == "1890"
    assert by_category["summary_row_count"]["row_count"] == "63"
    assert by_category["scenario_policy_seed_design"]["expected_row_count"] == "1890"
    assert by_category["graph_scope_dependency"]["review_status"] == (
        "blocked_until_graph_scale_acceptance"
    )
    assert by_category["input_evidence_dependency"]["review_status"] == (
        "blocked_until_input_evidence_acceptance"
    )
    assert by_category["formal_experiment_acceptance_requirement"][
        "artifact_present"
    ] == "false"
    assert by_category["artifact_checksums"]["expected_row_count"] == "3"
    assert "results=" in by_category["artifact_checksums"]["sha256"]
    assert {row["acceptance_ready"] for row in rows} == {"false"}
    assert {row["publication_ready"] for row in rows} == {"false"}
    assert {row["claim_boundary"] for row in rows} == {
        EXPERIMENT_PACKAGE_REVIEW_SCOPE
    }

    print("PASS: experiment package rows summarize current full outputs")


def test_write_experiment_package_review_packet_outputs_artifacts() -> None:
    """Writer should emit stable CSV, manifest, and Markdown review artifacts."""

    rows = build_experiment_package_review_rows()

    with TemporaryDirectory() as directory:
        output = Path(directory) / "experiment_package_review.csv"
        manifest = Path(directory) / "experiment_package_review_manifest.json"
        doc = Path(directory) / "experiment_package_review.md"
        value = write_experiment_package_review_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
            doc_path=doc,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == EXPERIMENT_PACKAGE_REVIEW_COLUMNS
        with manifest.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)
        text = doc.read_text(encoding="utf-8")

        assert len(written_rows) == len(rows)
        assert value["publication_ready"] is False
        assert value["acceptance_ready"] is False
        assert value["can_mark_complete"] is False
        assert value["experiment_acceptance_gate_closure_candidate_count"] == 0
        assert written_manifest["row_count"] == len(rows)
        assert "Experiment Package Review Packet" in text

    print("PASS: experiment package review writer emits artifacts")


def test_shipped_experiment_package_review_packet_matches_current_outputs() -> None:
    """Current shipped packet should match deterministic full-pilot outputs."""

    rows = build_experiment_package_review_rows()

    assert DEFAULT_EXPERIMENT_PACKAGE_REVIEW_PACKET_PATH.exists()
    assert DEFAULT_EXPERIMENT_PACKAGE_REVIEW_MANIFEST_PATH.exists()
    with DEFAULT_EXPERIMENT_PACKAGE_REVIEW_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    with DEFAULT_EXPERIMENT_PACKAGE_REVIEW_MANIFEST_PATH.open(
        "r",
        encoding="utf-8",
    ) as handle:
        manifest = json.load(handle)

    assert len(written_rows) == len(rows)
    assert [row["category_id"] for row in written_rows] == [
        row["category_id"] for row in rows
    ]
    assert manifest["publication_ready"] is False
    assert manifest["acceptance_ready"] is False
    assert manifest["result_scope"] == EXPERIMENT_PACKAGE_REVIEW_SCOPE
    assert manifest["row_count"] == 9

    print("PASS: shipped experiment package review packet matches current outputs")


if __name__ == "__main__":
    test_experiment_package_rows_summarize_current_full_outputs()
    test_write_experiment_package_review_packet_outputs_artifacts()
    test_shipped_experiment_package_review_packet_matches_current_outputs()
    print("\n=== REALWORLD EXPERIMENT PACKAGE REVIEW PACKET TESTS PASSED ===")
