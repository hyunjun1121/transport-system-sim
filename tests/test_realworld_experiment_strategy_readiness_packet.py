"""Tests for experiment strategy review packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.experiment_package_review_packet import (  # noqa: E402
    build_experiment_package_review_rows,
)
from src.realworld.experiment_strategy_readiness_packet import (  # noqa: E402
    DEFAULT_EXPERIMENT_STRATEGY_READINESS_MANIFEST_PATH,
    DEFAULT_EXPERIMENT_STRATEGY_READINESS_PACKET_PATH,
    EXPERIMENT_STRATEGY_READINESS_COLUMNS,
    EXPERIMENT_STRATEGY_READINESS_SCOPE,
    build_experiment_strategy_readiness_rows,
    write_experiment_strategy_readiness_packet,
)


def test_experiment_strategy_readiness_rows_classify_current_package() -> None:
    """Current full-pilot package rows should become concrete blockers."""

    rows = build_experiment_strategy_readiness_rows()
    by_category = {row["category_id"]: row for row in rows}

    assert len(rows) == 9
    assert by_category["manifest_scope"]["readiness_status"] == (
        "blocked_scaffold_or_not_calibrated_experiment_scope"
    )
    assert by_category["results_row_count"]["readiness_status"] == (
        "needs_human_review_experiment_row_counts"
    )
    assert by_category["summary_row_count"]["readiness_status"] == (
        "needs_human_review_experiment_row_counts"
    )
    assert by_category["scenario_policy_seed_design"]["readiness_status"] == (
        "needs_human_review_scenario_policy_seed_design"
    )
    assert by_category["graph_scope_dependency"]["readiness_status"] == (
        "blocked_graph_scale_dependency"
    )
    assert by_category["input_evidence_dependency"]["readiness_status"] == (
        "blocked_input_evidence_dependency"
    )
    assert by_category["common_random_numbers"]["readiness_status"] == (
        "needs_human_review_common_random_numbers"
    )
    assert by_category["artifact_checksums"]["readiness_status"] == (
        "needs_human_review_experiment_checksums"
    )
    assert by_category["formal_experiment_acceptance_requirement"][
        "readiness_status"
    ] == "blocked_missing_experiment_acceptance_record"
    assert {row["claim_boundary"] for row in rows} == {
        EXPERIMENT_STRATEGY_READINESS_SCOPE
    }
    assert all(row["can_support_experiment_gate"] == "false" for row in rows)

    print("PASS: experiment strategy review rows classify current package")


def test_experiment_strategy_readiness_rows_handle_fixture_review_rows() -> None:
    """Fixture rows should classify count mismatches and unknown categories."""

    rows = build_experiment_strategy_readiness_rows(
        review_rows=[
            _row("results_row_count", "blocked_row_count_mismatch"),
            _row("scenario_policy_seed_design", "blocked_design_count_mismatch"),
            _row("common_random_numbers", "blocked_crn_not_declared"),
            _row("unexpected_category", "fixture"),
        ],
        acceptance_path=Path("missing_experiment_acceptance.json"),
    )
    by_category = {row["category_id"]: row for row in rows}

    assert by_category["results_row_count"]["readiness_status"] == (
        "blocked_experiment_row_count_or_artifact"
    )
    assert by_category["scenario_policy_seed_design"]["readiness_status"] == (
        "blocked_scenario_policy_seed_design_mismatch"
    )
    assert by_category["common_random_numbers"]["readiness_status"] == (
        "blocked_common_random_numbers_not_declared"
    )
    assert by_category["unexpected_category"]["readiness_status"] == (
        "blocked_unclassified_experiment_category"
    )
    assert by_category["formal_experiment_acceptance_requirement"][
        "readiness_status"
    ] == "blocked_missing_experiment_acceptance_record"

    print("PASS: experiment strategy review rows handle fixture rows")


def test_write_experiment_strategy_readiness_packet_outputs_artifacts() -> None:
    """Writer should emit CSV, manifest, and Markdown artifacts."""

    rows = build_experiment_strategy_readiness_rows(
        review_rows=build_experiment_package_review_rows(),
    )

    with TemporaryDirectory() as directory:
        output = Path(directory) / "experiment_strategy_review.csv"
        manifest = Path(directory) / "experiment_strategy_review_manifest.json"
        doc = Path(directory) / "experiment_strategy_review.md"
        value = write_experiment_strategy_readiness_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
            doc_path=doc,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == (
                EXPERIMENT_STRATEGY_READINESS_COLUMNS
            )
        with manifest.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)
        text = doc.read_text(encoding="utf-8")

        assert len(written_rows) == len(rows)
        assert value["publication_ready"] is False
        assert value["can_mark_complete"] is False
        assert written_manifest["experiment_gate_closure_candidate_count"] == 0
        assert "Experiment Strategy Review Packet" in text
        assert "cannot close data/manifests/experiment_acceptance.json" in text

    print("PASS: experiment strategy review writer emits artifacts")


def test_shipped_experiment_strategy_readiness_packet_matches_current_review() -> None:
    """Current shipped strategy review packet should stay non-accepting."""

    rows = build_experiment_strategy_readiness_rows()

    assert DEFAULT_EXPERIMENT_STRATEGY_READINESS_PACKET_PATH.exists()
    assert DEFAULT_EXPERIMENT_STRATEGY_READINESS_MANIFEST_PATH.exists()
    with DEFAULT_EXPERIMENT_STRATEGY_READINESS_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    with DEFAULT_EXPERIMENT_STRATEGY_READINESS_MANIFEST_PATH.open(
        "r",
        encoding="utf-8",
    ) as handle:
        manifest = json.load(handle)

    assert len(written_rows) == len(rows)
    assert [row["category_id"] for row in written_rows] == [
        row["category_id"] for row in rows
    ]
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["result_scope"] == EXPERIMENT_STRATEGY_READINESS_SCOPE
    assert manifest["experiment_gate_closure_candidate_count"] == 0

    print("PASS: shipped experiment strategy review packet matches current review")


def _row(category_id: str, review_status: str) -> dict[str, str]:
    return {
        "category_id": category_id,
        "artifact_path": "fixture.csv",
        "artifact_present": "true",
        "row_count": "1",
        "expected_row_count": "1",
        "review_status": review_status,
        "publication_use_status": "fixture",
        "evidence_detail": "fixture detail",
    }


if __name__ == "__main__":
    test_experiment_strategy_readiness_rows_classify_current_package()
    test_experiment_strategy_readiness_rows_handle_fixture_review_rows()
    test_write_experiment_strategy_readiness_packet_outputs_artifacts()
    test_shipped_experiment_strategy_readiness_packet_matches_current_review()
    print("\n=== REALWORLD EXPERIMENT STRATEGY REVIEW TESTS PASSED ===")
