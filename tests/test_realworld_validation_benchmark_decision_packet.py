"""Tests for validation benchmark decision packet."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.validation_benchmark_decision_packet import (  # noqa: E402
    DEFAULT_VALIDATION_BENCHMARK_DECISION_MANIFEST_PATH,
    DEFAULT_VALIDATION_BENCHMARK_DECISION_PACKET_PATH,
    VALIDATION_BENCHMARK_DECISION_COLUMNS,
    VALIDATION_BENCHMARK_DECISION_SCOPE,
    build_validation_benchmark_decision_rows,
    write_validation_benchmark_decision_packet,
)


def test_validation_benchmark_decision_rows_classify_current_state() -> None:
    """Current benchmark artifacts should become conservative decision rows."""

    rows = build_validation_benchmark_decision_rows()
    by_id = {row["decision_id"]: row for row in rows}

    assert len(rows) == 6
    assert by_id["fallback_benchmark_scope_option"]["decision_status"] == (
        "needs_human_review_fallback_warn_or_fail_policy"
    )
    assert by_id["cached_osrm_snapshot_scope_option"]["decision_status"] == (
        "needs_human_review_cached_osrm_scope_policy"
    )
    assert by_id["alternative_benchmark_engine_option"]["decision_status"] == (
        "needs_human_review_alternative_benchmark_scope"
    )
    assert by_id["validation_summary_scope_boundary"]["decision_status"] == (
        "blocked_scaffold_validation_scope"
    )
    assert by_id["road_evidence_dependency"]["decision_status"] == (
        "blocked_weak_route_road_evidence_dependency"
    )
    assert (
        "data/validation/canonical_route_road_evidence_exposure_manifest.json"
        in by_id["road_evidence_dependency"]["followup_artifacts"]
    )
    assert (
        "data/road/road_evidence_priority_manifest.json"
        in by_id["road_evidence_dependency"]["evidence_input_paths"]
    )
    assert by_id["formal_validation_acceptance_boundary"]["decision_status"] == (
        "needs_human_review_existing_validation_acceptance"
    )
    assert {row["claim_boundary"] for row in rows} == {
        VALIDATION_BENCHMARK_DECISION_SCOPE
    }
    assert all(row["can_support_validation_gate"] == "false" for row in rows)

    print("PASS: validation benchmark decision rows classify current state")


def test_validation_benchmark_decision_writer_outputs_artifacts() -> None:
    """Writer should emit stable CSV, manifest, and Markdown artifacts."""

    rows = build_validation_benchmark_decision_rows()
    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "validation_benchmark_decision.csv"
        manifest_path = root / "manifest.json"
        doc_path = root / "packet.md"
        manifest = write_validation_benchmark_decision_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == VALIDATION_BENCHMARK_DECISION_COLUMNS
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        doc_text = doc_path.read_text(encoding="utf-8")

    assert len(written_rows) == len(rows)
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert written_manifest["row_count"] == 6
    assert written_manifest["validation_gate_closure_candidate_count"] == 0
    assert written_manifest["inputs"]["route_road_evidence_exposure_manifest"] == (
        "data/validation/canonical_route_road_evidence_exposure_manifest.json"
    )
    assert written_manifest["inputs"]["road_evidence_priority_manifest"] == (
        "data/road/road_evidence_priority_manifest.json"
    )
    assert "Benchmark Strategy Decision Packet" in doc_text

    print("PASS: validation benchmark decision writer emits artifacts")


def test_shipped_validation_benchmark_decision_packet_matches_current_outputs() -> None:
    """Committed benchmark decision packet should match current artifacts."""

    rows = build_validation_benchmark_decision_rows()

    assert DEFAULT_VALIDATION_BENCHMARK_DECISION_PACKET_PATH.exists()
    assert DEFAULT_VALIDATION_BENCHMARK_DECISION_MANIFEST_PATH.exists()
    with DEFAULT_VALIDATION_BENCHMARK_DECISION_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    manifest = json.loads(
        DEFAULT_VALIDATION_BENCHMARK_DECISION_MANIFEST_PATH.read_text(
            encoding="utf-8"
        )
    )

    assert written_rows == rows
    assert manifest["row_count"] == len(rows)
    assert manifest["blocking_decision_count"] == 2
    assert manifest["human_review_decision_count"] == 4
    assert manifest["alternative_benchmark_decision_recorded"] is False
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["inputs"]["route_road_evidence_exposure_manifest"] == (
        "data/validation/canonical_route_road_evidence_exposure_manifest.json"
    )
    assert manifest["inputs"]["road_evidence_priority_manifest"] == (
        "data/road/road_evidence_priority_manifest.json"
    )

    print("PASS: shipped validation benchmark decision packet matches outputs")


if __name__ == "__main__":
    test_validation_benchmark_decision_rows_classify_current_state()
    test_validation_benchmark_decision_writer_outputs_artifacts()
    test_shipped_validation_benchmark_decision_packet_matches_current_outputs()
    print("\n=== REALWORLD VALIDATION BENCHMARK DECISION TESTS PASSED ===")
