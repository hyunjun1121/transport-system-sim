"""Tests for sensitivity strategy-readiness packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.sensitivity_review_packet import (  # noqa: E402
    build_sensitivity_review_rows,
)
from src.realworld.sensitivity_strategy_readiness_packet import (  # noqa: E402
    DEFAULT_SENSITIVITY_STRATEGY_READINESS_MANIFEST_PATH,
    DEFAULT_SENSITIVITY_STRATEGY_READINESS_PACKET_PATH,
    SENSITIVITY_STRATEGY_READINESS_COLUMNS,
    SENSITIVITY_STRATEGY_READINESS_SCOPE,
    build_sensitivity_strategy_readiness_rows,
    write_sensitivity_strategy_readiness_packet,
)


def test_sensitivity_strategy_readiness_rows_classify_current_diagnostics() -> None:
    """Current Morris review rows should become concrete gate blockers."""

    rows = build_sensitivity_strategy_readiness_rows()
    by_category = {row["category_id"]: row for row in rows}

    assert len(rows) == 7
    assert by_category["structural_readiness"]["readiness_status"] == (
        "needs_human_review_morris_artifact_selection"
    )
    assert by_category["missing_or_nonfinite_morris_indices"]["readiness_status"] == (
        "needs_human_review_unavailable_morris_indices"
    )
    assert by_category["zero_mu_star_rows"]["readiness_status"] == (
        "needs_human_review_zero_mu_star_interpretation"
    )
    assert by_category["reduced_graph_scope"]["readiness_status"] == (
        "blocked_reduced_graph_scope_for_sensitivity_claims"
    )
    assert by_category["result_scope"]["readiness_status"] == (
        "blocked_scaffold_or_not_calibrated_result_scope"
    )
    assert by_category["sobol_decision_requirement"]["readiness_status"] == (
        "blocked_missing_morris_vs_sobol_decision"
    )
    assert by_category["sensitivity_acceptance_record"]["readiness_status"] == (
        "blocked_missing_sensitivity_acceptance_record"
    )
    assert {row["claim_boundary"] for row in rows} == {
        SENSITIVITY_STRATEGY_READINESS_SCOPE
    }
    assert all(row["can_support_sensitivity_gate"] == "false" for row in rows)

    print("PASS: sensitivity strategy-readiness rows classify current diagnostics")


def test_sensitivity_strategy_readiness_rows_handle_fixture_review_rows() -> None:
    """Fixture rows should classify non-blocking diagnostics conservatively."""

    rows = build_sensitivity_strategy_readiness_rows(
        review_rows=[
            _row(
                category_id="structural_readiness",
                diagnostic_status="ready_for_review",
                affected_row_count="0",
            ),
            _row(
                category_id="missing_or_nonfinite_morris_indices",
                diagnostic_status="no_missing_or_nonfinite_indices_detected",
                affected_row_count="0",
            ),
            _row(
                category_id="reduced_graph_scope",
                diagnostic_status="not_reduced_but_graph_scope_still_requires_review",
                affected_row_count="0",
            ),
            _row(
                category_id="unexpected_category",
                diagnostic_status="fixture",
                affected_row_count="0",
            ),
        ],
        acceptance_path=Path("missing_sensitivity_acceptance.json"),
    )
    by_category = {row["category_id"]: row for row in rows}

    assert by_category["missing_or_nonfinite_morris_indices"]["readiness_status"] == (
        "needs_human_review_index_handling"
    )
    unavailable_rows = build_sensitivity_strategy_readiness_rows(
        review_rows=[
            _row(
                category_id="missing_or_nonfinite_morris_indices",
                diagnostic_status="review_required_unavailable_indices",
                affected_row_count="2",
            ),
        ],
        acceptance_path=Path("missing_sensitivity_acceptance.json"),
    )
    assert unavailable_rows[0]["readiness_status"] == (
        "needs_human_review_unavailable_morris_indices"
    )
    assert by_category["reduced_graph_scope"]["readiness_status"] == (
        "needs_human_review_sensitivity_graph_scope"
    )
    assert by_category["unexpected_category"]["readiness_status"] == (
        "blocked_unclassified_sensitivity_category"
    )

    print("PASS: sensitivity strategy-readiness rows handle fixture review rows")


def test_write_sensitivity_strategy_readiness_packet_outputs_artifacts() -> None:
    """Writer should emit CSV, manifest, and Markdown artifacts."""

    rows = build_sensitivity_strategy_readiness_rows(
        review_rows=build_sensitivity_review_rows(),
    )

    with TemporaryDirectory() as directory:
        output = Path(directory) / "sensitivity_strategy_readiness.csv"
        manifest = Path(directory) / "sensitivity_strategy_readiness_manifest.json"
        doc = Path(directory) / "sensitivity_strategy_readiness.md"
        value = write_sensitivity_strategy_readiness_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
            doc_path=doc,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == (
                SENSITIVITY_STRATEGY_READINESS_COLUMNS
            )
        with manifest.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)
        text = doc.read_text(encoding="utf-8")

        assert len(written_rows) == len(rows)
        assert value["publication_ready"] is False
        assert value["can_mark_complete"] is False
        assert written_manifest["sensitivity_gate_closure_candidate_count"] == 0
        assert "Sensitivity Strategy Review Packet" in text
        assert "cannot close data/manifests/sensitivity_acceptance.json" in text

    print("PASS: sensitivity strategy-readiness writer emits artifacts")


def test_shipped_sensitivity_strategy_readiness_packet_matches_current_review() -> None:
    """Current shipped readiness packet should stay non-accepting."""

    rows = build_sensitivity_strategy_readiness_rows()

    assert DEFAULT_SENSITIVITY_STRATEGY_READINESS_PACKET_PATH.exists()
    assert DEFAULT_SENSITIVITY_STRATEGY_READINESS_MANIFEST_PATH.exists()
    with DEFAULT_SENSITIVITY_STRATEGY_READINESS_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    with DEFAULT_SENSITIVITY_STRATEGY_READINESS_MANIFEST_PATH.open(
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
    assert manifest["result_scope"] == SENSITIVITY_STRATEGY_READINESS_SCOPE
    assert manifest["sensitivity_gate_closure_candidate_count"] == 0

    print("PASS: shipped sensitivity strategy-readiness packet matches current review")


def _row(
    *,
    category_id: str,
    diagnostic_status: str,
    affected_row_count: str,
) -> dict[str, str]:
    return {
        "category_id": category_id,
        "issue_category": category_id,
        "diagnostic_status": diagnostic_status,
        "affected_row_count": affected_row_count,
        "diagnostic_detail": "fixture detail",
        "publication_use_status": "fixture",
        "evidence_input_paths": "fixture.csv",
    }


if __name__ == "__main__":
    test_sensitivity_strategy_readiness_rows_classify_current_diagnostics()
    test_sensitivity_strategy_readiness_rows_handle_fixture_review_rows()
    test_write_sensitivity_strategy_readiness_packet_outputs_artifacts()
    test_shipped_sensitivity_strategy_readiness_packet_matches_current_review()
    print("\n=== REALWORLD SENSITIVITY STRATEGY READINESS TESTS PASSED ===")
