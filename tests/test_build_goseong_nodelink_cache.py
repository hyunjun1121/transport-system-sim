"""Direct-execution tests for the 표준노드링크 cache build script."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "build_goseong_nodelink_cache.py"


def _load_builder():
    spec = importlib.util.spec_from_file_location("build_goseong_nodelink_cache", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _geodata_available() -> bool:
    try:
        import pyproj  # noqa: F401
        import shapefile  # noqa: F401

        return True
    except ModuleNotFoundError:
        return False


def _skip_if_no_geodata() -> bool:
    if not _geodata_available():
        print("SKIP: pyshp/pyproj not installed (requirements-geodata.txt)")
        return True
    return False


def _write_node_shp(base: str, nodes: list[tuple[str, float, float]]) -> None:
    import shapefile

    writer = shapefile.Writer(base, shapeType=shapefile.POINT, encoding="cp949")
    writer.encodingErrors = "replace"
    writer.field("NODE_ID", "C", size=10)
    for node_id, easting, northing in nodes:
        writer.point(easting, northing)
        writer.record(NODE_ID=node_id)
    writer.close()


def _write_link_shp(base: str, links: list[dict]) -> None:
    import shapefile

    writer = shapefile.Writer(base, shapeType=shapefile.POLYLINE, encoding="cp949")
    writer.encodingErrors = "replace"
    writer.field("LINK_ID", "C", size=10)
    writer.field("F_NODE", "C", size=10)
    writer.field("T_NODE", "C", size=10)
    writer.field("ROAD_RANK", "C", size=3)
    writer.field("LENGTH", "N", size=18, decimal=12)
    for link in links:
        writer.line([[(link["fx"], link["fy"]), (link["tx"], link["ty"])]])
        writer.record(
            LINK_ID=link["LINK_ID"], F_NODE=link["F_NODE"], T_NODE=link["T_NODE"],
            ROAD_RANK=str(link["ROAD_RANK"]), LENGTH=link.get("LENGTH", 1000.0),
        )
    writer.close()


def _synthetic_shp(tmp: Path) -> tuple[str, str]:
    node_base = str(tmp / "MOCT_NODE")
    link_base = str(tmp / "MOCT_LINK")
    _write_node_shp(node_base, [("10", 200000.0, 600000.0), ("20", 201000.0, 600000.0)])
    _write_link_shp(
        link_base,
        [
            {"LINK_ID": "1", "F_NODE": "10", "T_NODE": "20", "ROAD_RANK": 103, "LENGTH": 1234.5,
             "fx": 200000.0, "fy": 600000.0, "tx": 201000.0, "ty": 600000.0}
        ],
    )
    return link_base + ".shp", node_base + ".shp"


def test_build_script_preserves_existing_cache() -> None:
    """--source existing with an existing cache+manifest returns without reading SHP."""

    builder = _load_builder()
    with TemporaryDirectory() as tmp:
        cache = Path(tmp) / "cache.graphml"
        manifest = Path(tmp) / "cache_manifest.json"
        cache.write_bytes(b"x" * 60000)  # > 50 KB placeholder
        manifest.write_text(json.dumps({"source": "korean_nodelink_official"}), encoding="utf-8")

        status = builder.main(
            [
                "--cache", str(cache),
                "--manifest", str(manifest),
                "--source", "existing",
                "--link-shp", str(Path(tmp) / "absent.shp"),
                "--node-shp", str(Path(tmp) / "absent.shp"),
            ]
        )

    assert status == "preserved"
    # The placeholder bytes survived (script never read or rewrote the SHP).
    print("PASS: build script preserves an existing cache without reading SHP")


def test_build_script_manifest_source_label_and_claim_limit() -> None:
    """A real build writes a manifest with the official source label and claim boundary."""

    if _skip_if_no_geodata():
        return
    builder = _load_builder()
    with TemporaryDirectory() as tmp:
        link_shp, node_shp = _synthetic_shp(Path(tmp))
        cache = Path(tmp) / "nodelink.graphml"
        manifest = Path(tmp) / "nodelink_manifest.json"
        region = ROOT / "data" / "regions" / "goseong_mobilization.yaml"

        status = builder.main(
            [
                "--region", str(region),
                "--cache", str(cache),
                "--manifest", str(manifest),
                "--link-shp", link_shp,
                "--node-shp", node_shp,
                "--source", "build",
                "--bbox-south", "37.9", "--bbox-west", "126.9",
                "--bbox-north", "38.1", "--bbox-east", "127.2",
            ]
        )
        assert status == "built"
        assert cache.exists() and manifest.exists()

        data = json.loads(manifest.read_text(encoding="utf-8"))
        assert data["source"] == "korean_nodelink_official"
        claim_limit = data["claim_limit"]
        assert "NOT calibrated" in claim_limit
        assert "final_study_ready=false" in claim_limit
        expected_sha = hashlib.sha256(cache.read_bytes()).hexdigest()
        assert data["graphml_sha256"] == expected_sha
        assert data["edge_count"] >= 1

    print("PASS: build script manifest carries official source label + claim boundary")


if __name__ == "__main__":
    test_build_script_preserves_existing_cache()
    test_build_script_manifest_source_label_and_claim_limit()
    print("\n=== BUILD GOSEONG NODELINK CACHE TESTS PASSED ===")
