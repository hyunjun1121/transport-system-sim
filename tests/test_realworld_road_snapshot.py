"""Tests for road-network snapshot review artifacts."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.road_snapshot import (  # noqa: E402
    ROAD_SNAPSHOT_OUTPUTS,
    ROAD_SNAPSHOT_SCOPE,
    connector_audit_rows,
    snapshot_id_for_region,
    write_road_snapshot_artifacts,
)


def minimal_region_dict() -> dict:
    """Return a canonical simulator-compatible region spec."""

    return {
        "region_id": "road_snapshot_fixture",
        "label": "Road Snapshot Fixture",
        "sensitivity_level": "non_sensitive",
        "boundary": {
            "type": "bbox",
            "north": 37.53,
            "south": 37.49,
            "east": 127.14,
            "west": 127.08,
        },
        "origin_zones": [{"id": "A", "lat": 37.5001, "lon": 127.1001}],
        "destination_zones": [{"id": "D", "lat": 37.5201, "lon": 127.1301}],
        "rail": {
            "access": {"id": "S", "lat": 37.5051, "lon": 127.1101},
            "egress": {"id": "R", "lat": 37.5151, "lon": 127.1201},
            "travel_time_min": 40,
            "headway_min": 10,
            "capacity_pax_per_train": 500,
        },
        "source_refs": [
            {
                "source_id": "osm_overpass_road_snapshot",
                "role": "road_network_snapshot",
                "local_artifact_path": "data/cache/test.graphml",
                "review_status": "cached_snapshot_pending_review",
            }
        ],
    }


def synthetic_osm_like_graph() -> nx.MultiDiGraph:
    """Build a tiny routeable graph plus a closer non-routeable footway."""

    graph = nx.MultiDiGraph()
    graph.add_node(1, x=127.1000, y=37.5000)
    graph.add_node(2, x=127.1100, y=37.5050)
    graph.add_node(3, x=127.1200, y=37.5150)
    graph.add_node(4, x=127.1300, y=37.5200)
    graph.add_node("walk_a", x=127.1001, y=37.5001)
    graph.add_node("walk_b", x=127.1101, y=37.5051)

    graph.add_edge(1, 2, key=0, osmid="12", highway="primary", maxspeed=60, length=1_000)
    graph.add_edge(2, 3, key=0, osmid="23", highway="secondary", maxspeed=50, length=1_500)
    graph.add_edge(3, 4, key=0, osmid="34", highway="secondary", maxspeed=50, length=1_500)
    graph.add_edge(4, 3, key=0, osmid="43", highway="secondary", maxspeed=50, length=1_500)
    graph.add_edge("walk_a", "walk_b", key=0, osmid="walk", highway="footway", length=10)
    return graph


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_connector_audit_uses_routeable_vehicle_nodes() -> None:
    """Connector snapping should ignore closer pedestrian-only nodes."""

    rows = connector_audit_rows(synthetic_osm_like_graph(), minimal_region_dict())
    by_id = {row["point_id"]: row for row in rows}

    assert len(rows) == 4
    assert by_id["A"]["point_role"] == "assembly"
    assert by_id["A"]["road_node"] == "1"
    assert by_id["A"]["reasonableness_status"] == "ok_connector_distance"
    assert all(float(row["connector_t0_min"]) > 0.0 for row in rows)

    print("PASS: connector audit uses routeable vehicle nodes")


def test_road_snapshot_writer_outputs_manifest_tables_and_hashes() -> None:
    """Snapshot writer should emit all Phase 2 artifacts and checksums."""

    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "snapshot"
        manifest = write_road_snapshot_artifacts(
            region=minimal_region_dict(),
            graph=synthetic_osm_like_graph(),
            output_dir=output,
            region_path=root / "region.yaml",
            source_graph_path=root / "source.graphml",
            source_type="test_fixture",
            created_utc="2026-06-02T00:00:00+00:00",
        )

        graph_path = output / ROAD_SNAPSHOT_OUTPUTS["graphml"]
        nodes_path = output / ROAD_SNAPSHOT_OUTPUTS["nodes_csv"]
        edges_path = output / ROAD_SNAPSHOT_OUTPUTS["edges_csv"]
        connectors_path = output / ROAD_SNAPSHOT_OUTPUTS["connector_audit_csv"]
        manifest_path = output / ROAD_SNAPSHOT_OUTPUTS["manifest"]

        assert graph_path.exists()
        assert nodes_path.exists()
        assert edges_path.exists()
        assert connectors_path.exists()
        assert manifest_path.exists()
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        node_rows = read_csv_rows(nodes_path)
        edge_rows = read_csv_rows(edges_path)
        connector_rows = read_csv_rows(connectors_path)

    assert manifest == written_manifest
    assert manifest["result_scope"] == ROAD_SNAPSHOT_SCOPE
    assert manifest["formal_acceptance_created"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["node_table_row_count"] == len(node_rows)
    assert manifest["edge_table_row_count"] == len(edge_rows)
    assert manifest["connector_audit_row_count"] == len(connector_rows) == 4
    assert manifest["routeable_edge_count"] == 4
    for key in ("graphml", "nodes_csv", "edges_csv", "connector_audit_csv"):
        record = manifest["outputs"][key]
        assert len(record["sha256"]) == 64
        assert record["byte_count"] > 0

    print("PASS: road snapshot writer emits artifacts and hashes")


def test_road_snapshot_writer_refuses_nonempty_output_without_overwrite() -> None:
    """Existing snapshot directories should be protected by default."""

    with TemporaryDirectory() as directory:
        output = Path(directory) / "snapshot"
        output.mkdir()
        (output / "existing.txt").write_text("keep", encoding="utf-8")

        try:
            write_road_snapshot_artifacts(
                region=minimal_region_dict(),
                graph=synthetic_osm_like_graph(),
                output_dir=output,
            )
        except FileExistsError as exc:
            assert "Refusing to overwrite" in str(exc)
        else:
            raise AssertionError("Snapshot writer overwrote a non-empty directory")

    print("PASS: road snapshot writer refuses non-empty output")


def test_snapshot_id_is_timestamped_and_filesystem_safe() -> None:
    """Snapshot IDs should be stable for deterministic command tests."""

    snapshot_id = snapshot_id_for_region(
        "songpa public/demo",
        "2026-06-02T00:00:00+00:00",
    )

    assert snapshot_id == "songpa_public_demo_20260602T0000000000"

    print("PASS: road snapshot id is timestamped and safe")


if __name__ == "__main__":
    test_connector_audit_uses_routeable_vehicle_nodes()
    test_road_snapshot_writer_outputs_manifest_tables_and_hashes()
    test_road_snapshot_writer_refuses_nonempty_output_without_overwrite()
    test_snapshot_id_is_timestamped_and_filesystem_safe()
    print("\n=== REALWORLD ROAD SNAPSHOT TESTS PASSED ===")
