"""Tests for full-graph runtime-readiness packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.full_graph_runtime_readiness_packet import (  # noqa: E402
    DEFAULT_FULL_GRAPH_RUNTIME_READINESS_MANIFEST_PATH,
    DEFAULT_FULL_GRAPH_RUNTIME_READINESS_PACKET_PATH,
    FULL_GRAPH_RUNTIME_READINESS_COLUMNS,
    FULL_GRAPH_RUNTIME_READINESS_SCOPE,
    build_full_graph_runtime_readiness_rows,
    write_full_graph_runtime_readiness_packet,
)


def test_full_graph_runtime_readiness_rows_classify_current_scope() -> None:
    """Runtime rows should separate smoke evidence from missing full outputs."""

    with TemporaryDirectory() as directory:
        root = Path(directory)
        smoke = root / "smoke.json"
        pilot = root / "pilot_full.json"
        missing_full = root / "missing_full_graph.json"
        _write_json(
            smoke,
            {
                "smoke_passed": True,
                "analysis_graph_reduced": False,
                "row_count": 2,
                "duration_sec": 4.0,
                "region_id": "fixture_region",
                "graph_nodes": 4608,
                "graph_edges": 9148,
            },
        )
        _write_json(
            pilot,
            {
                "region_id": "fixture_region",
                "expected_row_count": 1890,
                "source_graph_nodes": 4608,
                "source_graph_edges": 9148,
            },
        )

        rows = build_full_graph_runtime_readiness_rows(
            smoke_manifest_path=smoke,
            pilot_full_manifest_path=pilot,
            full_graph_full_profile_manifest_path=missing_full,
        )
    by_id = {row["item_id"]: row for row in rows}

    assert len(rows) == 4
    assert by_id["full_graph_smoke_execution"]["readiness_status"] == (
        "needs_human_review_full_graph_smoke_scope"
    )
    assert by_id["full_graph_full_profile_outputs"]["readiness_status"] == (
        "blocked_missing_full_graph_full_profile_outputs"
    )
    assert by_id["full_graph_runtime_scope_decision"]["readiness_status"] == (
        "needs_human_review_full_graph_runtime_scope_decision"
    )
    assert by_id["full_graph_downstream_regeneration"]["readiness_status"] == (
        "blocked_missing_downstream_full_graph_regeneration_decision"
    )
    assert by_id["full_graph_smoke_execution"]["estimated_full_profile_runtime_sec"] == (
        "3780.0"
    )
    assert {row["claim_boundary"] for row in rows} == {
        FULL_GRAPH_RUNTIME_READINESS_SCOPE
    }
    assert all(row["can_support_graph_scale_gate"] == "false" for row in rows)

    print("PASS: full-graph runtime-readiness rows classify current scope")


def test_full_graph_runtime_readiness_rows_block_missing_smoke() -> None:
    """Missing smoke evidence should stay a blocker."""

    with TemporaryDirectory() as directory:
        root = Path(directory)
        pilot = root / "pilot_full.json"
        _write_json(
            pilot,
            {
                "region_id": "fixture_region",
                "expected_row_count": 1890,
                "source_graph_nodes": 4608,
                "source_graph_edges": 9148,
            },
        )

        rows = build_full_graph_runtime_readiness_rows(
            smoke_manifest_path=root / "missing_smoke.json",
            pilot_full_manifest_path=pilot,
            full_graph_full_profile_manifest_path=root / "missing_full_graph.json",
        )
    by_id = {row["item_id"]: row for row in rows}

    assert by_id["full_graph_smoke_execution"]["readiness_status"] == (
        "blocked_missing_full_graph_smoke_evidence"
    )

    print("PASS: full-graph runtime-readiness rows block missing smoke")


def test_write_full_graph_runtime_readiness_packet_outputs_artifacts() -> None:
    """Writer should emit CSV, manifest, and Markdown artifacts."""

    rows = build_full_graph_runtime_readiness_rows(
        smoke_manifest_path=Path("missing_smoke.json"),
        pilot_full_manifest_path=Path("missing_pilot.json"),
        full_graph_full_profile_manifest_path=Path("missing_full_graph.json"),
    )

    with TemporaryDirectory() as directory:
        output = Path(directory) / "full_graph_runtime_readiness.csv"
        manifest = Path(directory) / "full_graph_runtime_readiness_manifest.json"
        doc = Path(directory) / "full_graph_runtime_readiness.md"
        value = write_full_graph_runtime_readiness_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
            doc_path=doc,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == (
                FULL_GRAPH_RUNTIME_READINESS_COLUMNS
            )
        with manifest.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)
        text = doc.read_text(encoding="utf-8")

        assert len(written_rows) == len(rows)
        assert value["publication_ready"] is False
        assert value["can_mark_complete"] is False
        assert written_manifest["full_graph_gate_closure_candidate_count"] == 0
        assert "Full Graph Runtime Readiness Packet" in text

    print("PASS: full-graph runtime-readiness writer emits artifacts")


def test_shipped_full_graph_runtime_readiness_packet_stays_non_accepting() -> None:
    """Current shipped runtime-readiness packet should remain non-acceptance."""

    rows = build_full_graph_runtime_readiness_rows()

    assert DEFAULT_FULL_GRAPH_RUNTIME_READINESS_PACKET_PATH.exists()
    assert DEFAULT_FULL_GRAPH_RUNTIME_READINESS_MANIFEST_PATH.exists()
    with DEFAULT_FULL_GRAPH_RUNTIME_READINESS_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    with DEFAULT_FULL_GRAPH_RUNTIME_READINESS_MANIFEST_PATH.open(
        "r",
        encoding="utf-8",
    ) as handle:
        manifest = json.load(handle)

    assert len(written_rows) == len(rows)
    assert [row["item_id"] for row in written_rows] == [
        row["item_id"] for row in rows
    ]
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["result_scope"] == FULL_GRAPH_RUNTIME_READINESS_SCOPE
    assert manifest["full_graph_gate_closure_candidate_count"] == 0

    print("PASS: shipped full-graph runtime-readiness packet is non-acceptance")


def _write_json(path: Path, value: dict[str, object]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    test_full_graph_runtime_readiness_rows_classify_current_scope()
    test_full_graph_runtime_readiness_rows_block_missing_smoke()
    test_write_full_graph_runtime_readiness_packet_outputs_artifacts()
    test_shipped_full_graph_runtime_readiness_packet_stays_non_accepting()
    print("\n=== REALWORLD FULL-GRAPH RUNTIME READINESS TESTS PASSED ===")
