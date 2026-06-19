"""Tests for Morris-vs-Sobol sensitivity method decision packet."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.sensitivity_method_decision_packet import (  # noqa: E402
    DEFAULT_SENSITIVITY_METHOD_DECISION_MANIFEST_PATH,
    DEFAULT_SENSITIVITY_METHOD_DECISION_PACKET_PATH,
    SENSITIVITY_METHOD_DECISION_COLUMNS,
    SENSITIVITY_METHOD_DECISION_SCOPE,
    build_sensitivity_method_decision_rows,
    write_sensitivity_method_decision_packet,
)


def test_sensitivity_method_decision_rows_surface_current_blockers() -> None:
    """Current method-decision rows should expose Morris/Sobol blockers."""

    rows = build_sensitivity_method_decision_rows()
    by_id = {row["decision_id"]: row for row in rows}

    assert len(rows) == 7
    assert by_id["retain_morris_screening_option"]["decision_status"] == (
        "needs_human_review_morris_screening_scope"
    )
    assert by_id["run_sobol_extension_option"]["decision_status"] == (
        "blocked_missing_morris_vs_sobol_decision"
    )
    assert by_id["index_handling_policy"]["decision_status"] == (
        "needs_human_review_index_handling_policy"
    )
    assert "unavailable_index_rows=4832" in by_id["index_handling_policy"][
        "current_evidence"
    ]
    assert "zero_mu_star_rows=33619" in by_id["index_handling_policy"][
        "current_evidence"
    ]
    assert by_id["graph_scope_dependency"]["decision_status"] == (
        "blocked_reduced_graph_scope_dependency"
    )
    assert by_id["result_scope_boundary"]["decision_status"] == (
        "needs_human_review_result_scope"
    )
    assert by_id["formal_sensitivity_acceptance_boundary"]["decision_status"] == (
        "needs_human_review_existing_sensitivity_acceptance"
    )
    assert {row["claim_boundary"] for row in rows} == {
        SENSITIVITY_METHOD_DECISION_SCOPE
    }
    assert all(row["can_support_sensitivity_gate"] == "false" for row in rows)

    print("PASS: sensitivity method-decision rows surface current blockers")


def test_sensitivity_method_decision_writer_outputs_artifacts() -> None:
    """Writer should emit CSV, manifest, and Markdown artifacts."""

    rows = build_sensitivity_method_decision_rows()
    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "method_decision.csv"
        manifest_path = root / "method_decision_manifest.json"
        doc_path = root / "method_decision.md"
        manifest = write_sensitivity_method_decision_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == SENSITIVITY_METHOD_DECISION_COLUMNS
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        doc_text = doc_path.read_text(encoding="utf-8")

    assert len(written_rows) == len(rows)
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["sobol_decision_recorded"] is False
    assert manifest["sobol_waiver_created"] is False
    assert written_manifest["sensitivity_gate_closure_candidate_count"] == 0
    assert "Sensitivity Method Decision Packet" in doc_text
    assert "does not run Sobol, waive Sobol, accept Morris" in doc_text

    print("PASS: sensitivity method-decision writer emits artifacts")


def test_shipped_sensitivity_method_decision_packet_matches_current_outputs() -> None:
    """Committed method-decision packet should match current artifacts."""

    rows = build_sensitivity_method_decision_rows()

    assert DEFAULT_SENSITIVITY_METHOD_DECISION_PACKET_PATH.exists()
    assert DEFAULT_SENSITIVITY_METHOD_DECISION_MANIFEST_PATH.exists()
    with DEFAULT_SENSITIVITY_METHOD_DECISION_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    manifest = json.loads(
        DEFAULT_SENSITIVITY_METHOD_DECISION_MANIFEST_PATH.read_text(
            encoding="utf-8"
        )
    )

    assert len(written_rows) == len(rows)
    assert [row["decision_id"] for row in written_rows] == [
        row["decision_id"] for row in rows
    ]
    assert manifest["row_count"] == 7
    assert manifest["blocking_decision_count"] == 2
    assert manifest["human_review_decision_count"] == 5
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False

    print("PASS: shipped sensitivity method-decision packet matches outputs")


if __name__ == "__main__":
    test_sensitivity_method_decision_rows_surface_current_blockers()
    test_sensitivity_method_decision_writer_outputs_artifacts()
    test_shipped_sensitivity_method_decision_packet_matches_current_outputs()
    print("\n=== REALWORLD SENSITIVITY METHOD DECISION TESTS PASSED ===")
