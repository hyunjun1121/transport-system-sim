"""Tests for graph-scale manifest coverage audit."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.graph_scale_manifest_audit import (  # noqa: E402
    DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_MANIFEST_PATH,
    DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_PATH,
    GRAPH_SCALE_MANIFEST_AUDIT_COLUMNS,
    GRAPH_SCALE_MANIFEST_AUDIT_SCOPE,
    build_graph_scale_manifest_audit_rows,
    write_graph_scale_manifest_audit,
)


def test_manifest_audit_handles_nested_and_statistics_manifests() -> None:
    """Audit rows should normalize direct, statistics, and nested graph-scale fields."""

    with TemporaryDirectory() as directory:
        root = Path(directory)
        direct = root / "pilot_full_manifest.json"
        statistics = root / "pilot_full_statistics_manifest.json"
        figure = root / "figure_table_manifest.json"
        direct.write_text(json.dumps(_graph_manifest("pilot", 10, 20, 5, 6)), encoding="utf-8")
        statistics.write_text(
            json.dumps({"source_graph_scale": _scale(10, 20, 5, 6)}),
            encoding="utf-8",
        )
        figure.write_text(
            json.dumps(
                {
                    "graph_scale": {
                        "pilot": _scale(10, 20, 5, 6),
                        "sensitivity": _scale(10, 20, 5, 6),
                    }
                }
            ),
            encoding="utf-8",
        )

        rows = build_graph_scale_manifest_audit_rows(
            manifest_paths=(direct, statistics, figure),
        )

    assert len(rows) == 4
    assert {row["component_id"] for row in rows} == {
        "default",
        "pilot",
        "sensitivity",
    }
    assert all(row["graph_scale_present"] == "true" for row in rows)
    assert all(
        row["coverage_status"] == "complete_reduced_analysis_graph_recorded"
        for row in rows
    )
    assert {row["claim_boundary"] for row in rows} == {
        GRAPH_SCALE_MANIFEST_AUDIT_SCOPE
    }

    print("PASS: graph-scale manifest audit normalizes manifest shapes")


def test_write_graph_scale_manifest_audit_outputs_artifacts() -> None:
    """Writer should emit stable CSV, manifest, and Markdown review artifacts."""

    rows = [
        {
            "manifest_path": "fixture.json",
            "component_id": "default",
            "artifact_family": "pilot_experiment",
            "manifest_present": "true",
            "graph_scale_present": "true",
            "source_graph_nodes": "10",
            "source_graph_edges": "20",
            "analysis_graph_nodes": "5",
            "analysis_graph_edges": "6",
            "analysis_graph_reduced": "true",
            "analysis_graph_strategy": "fixture",
            "graph_source": "fixture",
            "command": "fixture",
            "run_profile_or_method": "fixture",
            "result_scope": "fixture",
            "coverage_status": "complete_reduced_analysis_graph_recorded",
            "required_reviewer_action": "review reduced/candidate graph method before graph-scale acceptance",
            "claim_boundary": GRAPH_SCALE_MANIFEST_AUDIT_SCOPE,
        }
    ]
    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "audit.csv"
        manifest_path = root / "manifest.json"
        doc_path = root / "audit.md"
        manifest = write_graph_scale_manifest_audit(
            rows=rows,
            output_path=output,
            manifest_path=manifest_path,
            doc_path=doc_path,
            audited_manifest_paths=(Path("fixture.json"),),
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == GRAPH_SCALE_MANIFEST_AUDIT_COLUMNS
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        doc_text = doc_path.read_text(encoding="utf-8")

    assert len(written_rows) == 1
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert written_manifest["complete_graph_scale_row_count"] == 1
    assert "not accept a graph-scale method" in written_manifest["claim_boundary"]
    assert "Graph-Scale Manifest Audit" in doc_text

    print("PASS: graph-scale manifest audit writer emits artifacts")


def test_shipped_graph_scale_manifest_audit_matches_current_outputs() -> None:
    """Current shipped audit should cover all generated graph-scale manifests."""

    rows = build_graph_scale_manifest_audit_rows()

    assert DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_PATH.exists()
    assert DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_MANIFEST_PATH.exists()
    with DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    manifest = json.loads(
        DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_MANIFEST_PATH.read_text(encoding="utf-8")
    )

    assert len(rows) == 13
    assert len(written_rows) == len(rows)
    assert manifest["row_count"] == 13
    assert manifest["missing_or_incomplete_row_count"] == 0
    assert manifest["source_graph_node_counts"] == [4608]
    assert manifest["analysis_graph_node_counts"] == [118, 164]
    assert manifest["publication_ready"] is False

    print("PASS: shipped graph-scale manifest audit matches current outputs")


def _scale(
    source_nodes: int,
    source_edges: int,
    analysis_nodes: int,
    analysis_edges: int,
) -> dict[str, object]:
    return {
        "source": {"nodes": source_nodes, "edges": source_edges},
        "analysis": {
            "nodes": analysis_nodes,
            "edges": analysis_edges,
            "reduced": True,
            "strategy": "fixture_strategy",
        },
    }


def _graph_manifest(
    run_profile: str,
    source_nodes: int,
    source_edges: int,
    analysis_nodes: int,
    analysis_edges: int,
) -> dict[str, object]:
    return {
        "run_profile": run_profile,
        "graph_scale": _scale(
            source_nodes,
            source_edges,
            analysis_nodes,
            analysis_edges,
        ),
        "command": "fixture",
        "result_scope": "fixture scope",
    }


if __name__ == "__main__":
    test_manifest_audit_handles_nested_and_statistics_manifests()
    test_write_graph_scale_manifest_audit_outputs_artifacts()
    test_shipped_graph_scale_manifest_audit_matches_current_outputs()
    print("\n=== REALWORLD GRAPH-SCALE MANIFEST AUDIT TESTS PASSED ===")
