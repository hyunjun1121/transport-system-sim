"""Tests for the formal acceptance evidence matrix."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.formal_acceptance_evidence_matrix import (  # noqa: E402
    build_formal_acceptance_evidence_matrix_rows,
    summarize_formal_acceptance_evidence_matrix,
    write_formal_acceptance_evidence_matrix,
)
from src.realworld.formal_acceptance_package import (  # noqa: E402
    build_formal_acceptance_package_summary,
)


def test_evidence_matrix_covers_current_formal_targets() -> None:
    package = build_formal_acceptance_package_summary()
    rows = build_formal_acceptance_evidence_matrix_rows(package_summary=package)
    by_gate = {row["gate_id"]: row for row in rows}

    assert len(rows) == 12
    assert {row["can_mark_complete"] for row in rows} == {"false"}
    assert {row["human_decision_required"] for row in rows} == {"true"}
    assert {row["formal_ready"] for row in rows} == {"false"}
    assert all(row["assigned_agent_id"] for row in rows)
    assert all(row["formal_target"] for row in rows)
    assert any(row["gate_id"] == "final_audit_document" for row in rows)
    assert any(
        row["gate_id"] == "road_class_overrides"
        and row["assigned_agent_id"] == "road_rail_parameter_evidence_agent"
        for row in rows
    )
    assert (
        "data/manifests/pilot_privacy_review_packet.csv"
        in by_gate["pilot_region_accepted"]["review_packets"]
    )
    assert (
        "data/manifests/pilot_privacy_review_manifest.json"
        in by_gate["pilot_region_accepted"]["source_paths"]
    )
    assert (
        "data/manifests/source_url_review_packet.csv"
        in by_gate["data_provenance"]["review_packets"]
    )
    assert (
        "data/manifests/source_url_review_packet.csv"
        in by_gate["data_provenance"]["source_paths"]
    )
    assert (
        "data/validation/graph_scale_strategy_readiness_packet.csv"
        in by_gate["graph_scale_strategy"]["source_paths"]
    )
    assert (
        "data/validation/full_graph_runtime_readiness_packet.csv"
        in by_gate["graph_scale_strategy"]["review_packets"]
    )
    assert (
        "data/parameters/parameter_source_readiness_packet.csv"
        in by_gate["parameter_acceptance"]["source_paths"]
    )
    assert (
        "data/road/road_source_readiness_packet.csv"
        in by_gate["road_class_overrides"]["source_paths"]
    )
    assert (
        "data/validation/validation_strategy_readiness_packet.csv"
        in by_gate["validation_package"]["source_paths"]
    )
    assert (
        "data/validation/sensitivity_strategy_readiness_packet.csv"
        in by_gate["sensitivity_analysis"]["source_paths"]
    )
    assert (
        "data/manifests/experiment_strategy_readiness_packet.csv"
        in by_gate["full_experiment_output"]["source_paths"]
    )
    assert (
        "data/validation/tracked_artifact_audit_manifest.json"
        in by_gate["reproducibility"]["source_paths"]
    )
    assert (
        "data/manifests/current_goal_completion_audit.json"
        in by_gate["reproducibility"]["source_paths"]
    )
    assert (
        "data/manifests/current_goal_completion_audit.json"
        in by_gate["final_audit"]["source_paths"]
    )


def test_write_evidence_matrix_outputs_non_approval_artifacts() -> None:
    package = build_formal_acceptance_package_summary()
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        output = root / "matrix.csv"
        manifest = root / "matrix.json"
        doc = root / "matrix.md"
        value = write_formal_acceptance_evidence_matrix(
            output_path=output,
            manifest_path=manifest,
            doc_path=doc,
            package_summary=package,
        )

        assert value["row_count"] == 12
        assert value["human_decision_required_count"] == 12
        assert value["can_mark_complete"] is False
        assert output.exists()
        assert manifest.exists()
        assert doc.exists()

        with output.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        loaded = json.loads(manifest.read_text(encoding="utf-8"))
        text = doc.read_text(encoding="utf-8")

        assert len(rows) == 12
        assert loaded["can_mark_complete"] is False
        assert "Formal Review Evidence Matrix" in text
        assert "do not approve evidence" in text

        compact = summarize_formal_acceptance_evidence_matrix(manifest)
        assert compact["manifest_present"] is True
        assert compact["row_count"] == 12
        assert compact["can_mark_complete"] is False


def test_write_evidence_matrix_preserves_timestamp_when_unchanged() -> None:
    package = build_formal_acceptance_package_summary()
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        output = root / "matrix.csv"
        manifest = root / "matrix.json"
        doc = root / "matrix.md"
        write_formal_acceptance_evidence_matrix(
            output_path=output,
            manifest_path=manifest,
            doc_path=doc,
            package_summary=package,
        )
        first = json.loads(manifest.read_text(encoding="utf-8"))
        first["generated_at"] = "2000-01-01T00:00:00+00:00"
        manifest.write_text(
            json.dumps(first, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        value = write_formal_acceptance_evidence_matrix(
            output_path=output,
            manifest_path=manifest,
            doc_path=doc,
            package_summary=package,
        )
        loaded = json.loads(manifest.read_text(encoding="utf-8"))

        assert value["generated_at"] == "2000-01-01T00:00:00+00:00"
        assert loaded["generated_at"] == "2000-01-01T00:00:00+00:00"


if __name__ == "__main__":
    test_evidence_matrix_covers_current_formal_targets()
    test_write_evidence_matrix_outputs_non_approval_artifacts()
    test_write_evidence_matrix_preserves_timestamp_when_unchanged()
    print("PASS: formal acceptance evidence matrix")
