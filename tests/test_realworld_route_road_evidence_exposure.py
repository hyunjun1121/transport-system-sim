"""Tests for canonical route road-evidence exposure artifacts."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

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

    assert written_rows == expected_rows
    assert manifest["row_count"] == len(expected_rows)
    assert manifest["result_scope"] == ROUTE_ROAD_EVIDENCE_EXPOSURE_SCOPE
    assert manifest["publication_ready"] is False
    assert manifest["acceptance_ready"] is False

    print("PASS: shipped route road-evidence exposure matches current artifacts")


if __name__ == "__main__":
    test_route_road_evidence_exposure_rows_cover_current_routes()
    test_route_road_evidence_exposure_writer_outputs_manifest()
    test_shipped_route_road_evidence_exposure_matches_current_artifacts()
    print("\n=== REALWORLD ROUTE ROAD-EVIDENCE EXPOSURE TESTS PASSED ===")
