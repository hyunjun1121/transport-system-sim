"""Tests for experiment design decision packet."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.experiment_design_decision_packet import (  # noqa: E402
    DEFAULT_EXPERIMENT_DESIGN_DECISION_MANIFEST_PATH,
    DEFAULT_EXPERIMENT_DESIGN_DECISION_PACKET_PATH,
    EXPERIMENT_DESIGN_DECISION_COLUMNS,
    EXPERIMENT_DESIGN_DECISION_SCOPE,
    build_experiment_design_decision_rows,
    write_experiment_design_decision_packet,
)


def test_experiment_design_decision_rows_classify_current_state() -> None:
    """Current experiment outputs should become conservative design decisions."""

    rows = build_experiment_design_decision_rows()
    by_id = {row["decision_id"]: row for row in rows}

    assert len(rows) == 8
    assert by_id["sample_staged_full_profile_context"]["decision_status"] == (
        "needs_human_review_current_full_profile_scope"
    )
    assert by_id["multi_corridor_profile_option"]["decision_status"] == (
        "needs_human_review_multi_corridor_profile_scope"
    )
    assert by_id["scenario_policy_seed_design"]["decision_status"] == (
        "needs_human_review_scenario_policy_seed_design"
    )
    assert by_id["graph_scope_dependency"]["decision_status"] == (
        "blocked_graph_scale_dependency"
    )
    assert by_id["input_evidence_dependency"]["decision_status"] == (
        "blocked_input_evidence_dependency"
    )
    assert by_id["result_scope_boundary"]["decision_status"] == (
        "blocked_scaffold_or_not_calibrated_experiment_scope"
    )
    assert by_id["regenerate_or_retain_outputs"]["decision_status"] == (
        "needs_human_review_regenerate_or_retain_outputs"
    )
    assert by_id["formal_experiment_acceptance_boundary"]["decision_status"] == (
        "blocked_missing_experiment_acceptance_record"
    )
    assert {row["claim_boundary"] for row in rows} == {
        EXPERIMENT_DESIGN_DECISION_SCOPE
    }
    assert all(row["can_support_experiment_gate"] == "false" for row in rows)

    print("PASS: experiment design decision rows classify current state")


def test_experiment_design_decision_writer_outputs_artifacts() -> None:
    """Writer should emit stable CSV, manifest, and Markdown artifacts."""

    rows = build_experiment_design_decision_rows()
    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "experiment_design_decision.csv"
        manifest_path = root / "manifest.json"
        doc_path = root / "packet.md"
        manifest = write_experiment_design_decision_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == EXPERIMENT_DESIGN_DECISION_COLUMNS
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        doc_text = doc_path.read_text(encoding="utf-8")

    assert len(written_rows) == len(rows)
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert written_manifest["row_count"] == 8
    assert written_manifest["experiment_gate_closure_candidate_count"] == 0
    assert "Experiment Design Decision Packet" in doc_text

    print("PASS: experiment design decision writer emits artifacts")


def test_shipped_experiment_design_decision_packet_matches_current_outputs() -> None:
    """Committed design decision packet should match current artifacts."""

    rows = build_experiment_design_decision_rows()

    assert DEFAULT_EXPERIMENT_DESIGN_DECISION_PACKET_PATH.exists()
    assert DEFAULT_EXPERIMENT_DESIGN_DECISION_MANIFEST_PATH.exists()
    with DEFAULT_EXPERIMENT_DESIGN_DECISION_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    manifest = json.loads(
        DEFAULT_EXPERIMENT_DESIGN_DECISION_MANIFEST_PATH.read_text(
            encoding="utf-8"
        )
    )

    assert written_rows == rows
    assert manifest["row_count"] == len(rows)
    assert manifest["blocking_decision_count"] == 4
    assert manifest["human_review_decision_count"] == 4
    assert manifest["selected_run_profile_recorded"] is False
    assert manifest["scenario_policy_seed_decision_recorded"] is False
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False

    print("PASS: shipped experiment design decision packet matches outputs")


if __name__ == "__main__":
    test_experiment_design_decision_rows_classify_current_state()
    test_experiment_design_decision_writer_outputs_artifacts()
    test_shipped_experiment_design_decision_packet_matches_current_outputs()
    print("\n=== REALWORLD EXPERIMENT DESIGN DECISION TESTS PASSED ===")
