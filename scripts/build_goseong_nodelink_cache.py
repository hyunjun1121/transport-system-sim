"""Build the Goseong case-study road-graph cache from the Korean 표준노드링크 (SHP).

This is the official-network parallel source. It reads the MOCT_LINK/MOCT_NODE
shapefiles (EPSG:5179-family WKT, CP949 DBF) under ``data-collections/``, reprojects
to WGS84, filters to the public corridor envelope (Songpa -> Cheongnyangni ->
Gangneung -> Goseong), and writes a GraphML cache consumable by the unchanged
runner via ``--cache-path data/cache/goseong_nodelink_road.graphml``.

Offline by default (reads only local SHP; no live network). Output is a
decision-support / quasi-real snapshot of the public road network, NOT calibrated
and NOT operational — ``final_study_ready`` stays false.

Usage::

    ./.venv/Scripts/python scripts/build_goseong_nodelink_cache.py

Default ``--source existing`` preserves an existing cache (mirrors
build_goseong_cache.py). Use ``--source build`` to rebuild. Requires the optional
geodata deps (requirements-geodata.txt).
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import networkx as nx
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.nodelink_network import (  # noqa: E402
    DEFAULT_CORRIDOR_BBOX,
    NODELINK_OFFICIAL_LABEL,
    NODELINK_SOURCE_LABEL,
    ROAD_RANK_TO_HIGHWAY,
    load_nodelink_graph,
    normalize_nodelink_graph,
    road_rank_to_highway,
)
from src.realworld.osm_network import save_graphml  # noqa: E402

DEFAULT_REGION_PATH = ROOT / "data" / "regions" / "goseong_mobilization.yaml"
DEFAULT_CACHE_PATH = ROOT / "data" / "cache" / "goseong_nodelink_road.graphml"
DEFAULT_MANIFEST_PATH = ROOT / "data" / "cache" / "goseong_nodelink_road_manifest.json"
DEFAULT_LINK_SHP = ROOT / "data-collections" / "전국표준노드링크" / "MOCT_LINK.shp"
DEFAULT_NODE_SHP = ROOT / "data-collections" / "전국표준노드링크" / "MOCT_NODE.shp"


def main(argv: list[str] | None = None) -> str:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region", default=str(DEFAULT_REGION_PATH))
    parser.add_argument("--cache", default=str(DEFAULT_CACHE_PATH))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST_PATH))
    parser.add_argument("--link-shp", default=str(DEFAULT_LINK_SHP))
    parser.add_argument("--node-shp", default=str(DEFAULT_NODE_SHP))
    parser.add_argument("--bbox-south", type=float, default=DEFAULT_CORRIDOR_BBOX[0])
    parser.add_argument("--bbox-west", type=float, default=DEFAULT_CORRIDOR_BBOX[1])
    parser.add_argument("--bbox-north", type=float, default=DEFAULT_CORRIDOR_BBOX[2])
    parser.add_argument("--bbox-east", type=float, default=DEFAULT_CORRIDOR_BBOX[3])
    parser.add_argument(
        "--source",
        choices=("existing", "build"),
        default="existing",
        help="Preserve an existing cache by default; build = rebuild from SHP.",
    )
    args = parser.parse_args(argv)

    cache_path = Path(args.cache)
    manifest_path = Path(args.manifest)

    if args.source == "existing" and cache_path.exists() and manifest_path.exists():
        print(f"preserved existing {cache_path}")
        return "preserved"

    region = _load_yaml(Path(args.region))
    corridor_bbox = (args.bbox_south, args.bbox_west, args.bbox_north, args.bbox_east)
    print(
        f"building from 표준노드링크 SHP; corridor bbox (S,W,N,E)={corridor_bbox}"
    )

    graph = load_nodelink_graph(
        link_shp_path=args.link_shp,
        node_shp_path=args.node_shp,
        corridor_bbox=corridor_bbox,
        source_label=NODELINK_SOURCE_LABEL,
        bidirectional=True,
    )
    graph = normalize_nodelink_graph(graph)
    _warn_on_unknown_road_ranks(graph)

    if graph.number_of_edges() == 0:
        raise RuntimeError(
            "표준노드링크 build returned no corridor edges; check the bbox and SHP paths."
        )

    save_graphml(graph, cache_path)
    manifest = build_cache_manifest(
        region=region,
        region_path=Path(args.region),
        cache_path=cache_path,
        graph=graph,
        corridor_bbox=corridor_bbox,
    )
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        f"wrote {cache_path} ({graph.number_of_nodes()} nodes, "
        f"{graph.number_of_edges()} edges)"
    )
    print(f"wrote {manifest_path}")
    return "built"


def _warn_on_unknown_road_ranks(graph: nx.Graph) -> None:
    """Log the ROAD_RANK histogram and warn if unseen codes dominate (R1)."""

    histogram = graph.graph.get("road_rank_histogram", {})
    if not histogram:
        return
    total = sum(histogram.values())
    known = {str(code) for code in ROAD_RANK_TO_HIGHWAY}
    unknown = {code: count for code, count in histogram.items() if code not in known}
    print("ROAD_RANK histogram:")
    for code, count in sorted(histogram.items()):
        highway = road_rank_to_highway(code)
        print(f"  rank={code!r:>6} -> {highway:<12} {count:>10}")
    if unknown:
        share = sum(unknown.values()) / max(total, 1)
        print(
            f"WARNING: {share:.1%} of links carry ROAD_RANK codes outside the "
            f"ROAD_RANK_TO_HIGHWAY table {sorted(unknown)}; review the mapping."
        )


def build_cache_manifest(
    *,
    region: dict,
    region_path: Path,
    cache_path: Path,
    graph: nx.Graph,
    corridor_bbox: tuple[float, float, float, float],
) -> dict:
    graphml_sha256 = hashlib.sha256(cache_path.read_bytes()).hexdigest()
    return {
        "region_id": region["region_id"],
        "cache_path": _relative(cache_path),
        "region_path": _relative(region_path),
        "source": NODELINK_OFFICIAL_LABEL,
        "source_label": NODELINK_SOURCE_LABEL,
        "created_utc_note": "one-time explicit build; timestamp omitted for deterministic replay",
        "extraction": {
            "network_source": "Korean 표준노드링크 (MOCT_LINK / MOCT_NODE SHP)",
            "corridor_bbox_south_west_north_east": list(corridor_bbox),
            "crs": "ITRF2000 Central Belt 60 (.prj WKT) -> WGS84 (EPSG:4326)",
            "road_rank_histogram": graph.graph.get("road_rank_histogram", {}),
        },
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
        "graph_type": graph.__class__.__name__,
        "graphml_sha256": graphml_sha256,
        "live_services_required_for_default_tests": False,
        "coordinate_policy": "public_administrative_centroids_and_public_road_network_only",
        "claim_limit": (
            "Official Korean 표준노드링크 road snapshot along the public corridor; "
            "supports offline decision-support / quasi-real simulation only. NOT calibrated, "
            "NOT an operational route plan, NOT final-study evidence. final_study_ready=false."
        ),
    }


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def _relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    main()
