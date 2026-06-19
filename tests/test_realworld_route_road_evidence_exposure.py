"""Tests for canonical route road-evidence exposure artifacts."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.pilot_experiments import load_pilot_inputs  # noqa: E402
from src.realworld.route_road_evidence_exposure import (  # noqa: E402
    DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_MANIFEST_PATH,
    DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_PATH,
    DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_SUMMARY_PATH,
    ROUTE_ROAD_EVIDENCE_EXPOSURE_COLUMNS,
    ROUTE_ROAD_EVIDENCE_EXPOSURE_SCOPE,
    build_route_road_evidence_exposure_rows,
    write_route_road_evidence_exposure,
)


def test_route_road_evidence_exposure_rows_cover_current_routes() -> None:
    """Current graph-scale route candidates should map to road-evidence rows."""

    inputs = load_pilot_inputs(reduce_graph=False)
    rows = build_route_road_evidence_exposure_rows(inputs.graph)
    variants = {row["graph_variant"] for row in rows}
    route_keys = {
        (row["graph_variant"], row["route_check_id"], row["route_rank"])
        for row in rows
    }
    highways = {row["highway"] for row in rows}

    assert len(rows) == 76
    assert variants == {"current_reduced_corridor", "multi_corridor_candidate"}
    assert len(route_keys) == 18
    assert {"connector", "residential", "primary", "secondary"}.issubset(highways)
    assert {row["claim_scope"] for row in rows} == {
        ROUTE_ROAD_EVIDENCE_EXPOSURE_SCOPE
    }
    assert {row["weak_for_final_claim"] for row in rows} == {"true"}

    connector_rows = [row for row in rows if row["highway"] == "connector"]
    assert connector_rows
    assert connector_rows[0]["speed_evidence_status"] == (
        "connector_geometry_sanity_only"
    )

    print("PASS: route road-evidence exposure rows cover current routes")


def test_route_road_evidence_exposure_writer_outputs_manifest() -> None:
    """Writer should emit stable CSV, summary, and non-acceptance manifest."""

    inputs = load_pilot_inputs(reduce_graph=False)
    rows = build_route_road_evidence_exposure_rows(inputs.graph)

    with TemporaryDirectory() as directory:
        output = Path(directory) / "route_exposure.csv"
        summary = Path(directory) / "route_exposure.md"
        manifest = Path(directory) / "route_exposure_manifest.json"
        value = write_route_road_evidence_exposure(
            rows=rows,
            output_path=output,
            summary_path=summary,
            manifest_path=manifest,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == (
                ROUTE_ROAD_EVIDENCE_EXPOSURE_COLUMNS
            )
        with manifest.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)

        assert len(written_rows) == len(rows)
        assert summary.exists()
        assert value["publication_ready"] is False
        assert value["acceptance_ready"] is False
        assert value["row_count"] == 76
        assert written_manifest["route_candidate_count"] == 18
        assert "does not create reviewed road inputs" in written_manifest[
            "claim_boundary"
        ]

    print("PASS: route road-evidence exposure writer emits manifest")


def test_route_road_evidence_exposure_reports_edge_override_source() -> None:
    """Route exposure should surface applied road-class override source metadata."""

    graph = nx.DiGraph()
    graph.add_edge(
        "A",
        "B",
        highway="primary",
        length_m=1000.0,
        t0=10.0,
        realworld_edge_id="ab",
        road_class_override_applied=True,
        road_class_override_source_class="literature-derived",
    )
    graph.add_edge(
        "B",
        "D",
        highway="primary",
        length_m=1000.0,
        t0=10.0,
        realworld_edge_id="bd",
        road_class_override_applied=True,
        road_class_override_source_class="literature-derived",
    )

    with TemporaryDirectory() as directory:
        route_path = Path(directory) / "routes.csv"
        evidence_path = Path(directory) / "road_evidence.csv"
        _write_route_fixture(route_path)
        _write_road_evidence_fixture(evidence_path)

        rows = build_route_road_evidence_exposure_rows(
            graph,
            road_evidence_review_path=evidence_path,
            graph_variant_paths=(("fixture_graph", route_path),),
        )

    assert len(rows) == 1
    row = rows[0]
    assert row["highway"] == "primary"
    assert row["override_source_class"] == "literature-derived"
    assert row["weak_for_final_claim"] == "true"
    assert "edge_override_source_class=literature-derived" in row["notes"]

    print("PASS: route road-evidence exposure reports edge override source")


def test_shipped_route_road_evidence_exposure_matches_current_artifacts() -> None:
    """Shipped exposure artifacts should match deterministic inputs."""

    inputs = load_pilot_inputs(reduce_graph=False)
    expected_rows = build_route_road_evidence_exposure_rows(inputs.graph)

    assert DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_PATH.exists()
    assert DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_SUMMARY_PATH.exists()
    assert DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_MANIFEST_PATH.exists()
    with DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)
        written_rows = list(reader)
        assert tuple(reader.fieldnames or ()) == (
            ROUTE_ROAD_EVIDENCE_EXPOSURE_COLUMNS
        )
    with DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_MANIFEST_PATH.open(
        "r",
        encoding="utf-8",
    ) as handle:
        manifest = json.load(handle)

    assert len(written_rows) == len(expected_rows)
    for w, e in zip(written_rows, expected_rows):
        for k in w:
            if k not in ("time_min", "time_share"):
                assert w[k] == e[k], f"Mismatch {k}: {w[k]!r} != {e[k]!r}"
    assert manifest["row_count"] == len(expected_rows)
    assert manifest["result_scope"] == ROUTE_ROAD_EVIDENCE_EXPOSURE_SCOPE
    assert manifest["publication_ready"] is False
    assert manifest["acceptance_ready"] is False

    print("PASS: shipped route road-evidence exposure matches current artifacts")


def _write_route_fixture(path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "region_id",
                "route_check_id",
                "route_label",
                "full_route_rank",
                "full_path_nodes",
                "source",
                "target",
                "full_path_available",
                "exact_full_path_present_in_analysis",
                "status",
            ),
        )
        writer.writeheader()
        writer.writerow(
            {
                "region_id": "fixture",
                "route_check_id": "fixture_A_D",
                "route_label": "fixture route",
                "full_route_rank": "1",
                "full_path_nodes": "A>B>D",
                "source": "A",
                "target": "D",
                "full_path_available": "true",
                "exact_full_path_present_in_analysis": "true",
                "status": "available",
            }
        )


def _write_road_evidence_fixture(path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "highway",
                "speed_evidence_status",
                "capacity_evidence_status",
                "base_disruption_evidence_status",
                "override_source_class",
                "review_priority",
                "weak_for_final_claim",
                "candidate_artifacts",
            ),
        )
        writer.writeheader()
        writer.writerow(
            {
                "highway": "primary",
                "speed_evidence_status": "reviewed_source_candidate",
                "capacity_evidence_status": "reviewed_source_candidate",
                "base_disruption_evidence_status": "reviewed_source_candidate",
                "override_source_class": "expert assumption",
                "review_priority": "high",
                "weak_for_final_claim": "true",
                "candidate_artifacts": "fixture",
            }
        )


if __name__ == "__main__":
    test_route_road_evidence_exposure_rows_cover_current_routes()
    test_route_road_evidence_exposure_writer_outputs_manifest()
    test_route_road_evidence_exposure_reports_edge_override_source()
    test_shipped_route_road_evidence_exposure_matches_current_artifacts()
    print("\n=== REALWORLD ROUTE ROAD-EVIDENCE EXPOSURE TESTS PASSED ===")
