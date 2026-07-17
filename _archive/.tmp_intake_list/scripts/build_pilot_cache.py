"""Build or preserve the offline pilot road-graph cache.

The default mode preserves an existing cache so an unqualified command cannot
accidentally replace the current OSM-derived pilot snapshot with the compact
fixture. Use ``--source fixture`` for deterministic fallback work or
``--source overpass`` for an intentional live Overpass refresh.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from math import cos, radians, sqrt
from pathlib import Path
import sys
from typing import Any, Mapping
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import networkx as nx
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.osm_network import save_graphml


DEFAULT_REGION_PATH = ROOT / "data" / "regions" / "pilot_region.yaml"
DEFAULT_CACHE_PATH = ROOT / "data" / "cache" / "pilot_region_road.graphml"
DEFAULT_MANIFEST_PATH = ROOT / "data" / "cache" / "pilot_region_road_manifest.json"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
EARTH_M_PER_DEG_LAT = 111_320.0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region", default=str(DEFAULT_REGION_PATH))
    parser.add_argument("--cache", default=str(DEFAULT_CACHE_PATH))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST_PATH))
    parser.add_argument(
        "--source",
        choices=("existing", "fixture", "overpass"),
        default="existing",
        help=(
            "Preserve an existing cache by default; use fixture for deterministic "
            "offline fallback, or overpass for manual live extraction."
        ),
    )
    args = parser.parse_args()

    region_path = Path(args.region)
    cache_path = Path(args.cache)
    manifest_path = Path(args.manifest)
    region = _load_yaml(region_path)

    if args.source == "existing" and cache_path.exists() and manifest_path.exists():
        print(f"preserved existing {cache_path}")
        print(f"preserved existing {manifest_path}")
        return

    if args.source == "existing":
        graph = build_fixture_graph(region)
        source_note = "curated_public_coordinate_osm_style_fixture"
        attribution = "No external OSM data are required for the curated fixture."
        claim_limit = (
            "Curated fixture cache was created because no existing cache was "
            "available. It supports offline smoke tests only; publication "
            "claims require a reviewed OSM-derived snapshot and validation."
        )
    elif args.source == "fixture":
        graph = build_fixture_graph(region)
        source_note = "curated_public_coordinate_osm_style_fixture"
        attribution = "No external OSM data are required for the curated fixture."
        claim_limit = (
            "Curated fixture cache supports offline smoke tests only; "
            "publication claims require a reviewed OSM-derived snapshot and validation."
        )
    else:
        graph = build_overpass_graph(region)
        source_note = "live_overpass_osm_snapshot"
        attribution = "OpenStreetMap contributors; respect OSM/Overpass attribution requirements."
        claim_limit = (
            "Cached Overpass/OSM snapshot supports offline pilot smoke and sample runs; "
            "publication claims still require human source review, parameter evidence, "
            "rail evidence, external plausibility benchmarks, and uncertainty analysis."
        )

    save_graphml(graph, cache_path)
    manifest = build_cache_manifest(
        region=region,
        region_path=region_path,
        cache_path=cache_path,
        graph=graph,
        source_note=source_note,
        attribution=attribution,
        claim_limit=claim_limit,
    )
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"wrote {cache_path}")
    print(f"wrote {manifest_path}")


def build_cache_manifest(
    *,
    region: dict[str, Any],
    region_path: Path,
    cache_path: Path,
    graph: nx.Graph,
    source_note: str,
    attribution: str,
    claim_limit: str,
    created_utc: str | None = None,
) -> dict[str, Any]:
    """Return cache metadata for review and reproducibility manifests."""

    return {
        "region_id": region["region_id"],
        "cache_path": _relative(cache_path),
        "region_path": _relative(region_path),
        "source": source_note,
        "created_utc": created_utc
        or datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "boundary": _boundary_metadata(region),
        "tooling": _tooling_metadata(source_note),
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
        "graph_type": graph.__class__.__name__,
        "live_services_required_for_default_tests": False,
        "attribution": attribution,
        "claim_limit": claim_limit,
    }


def build_fixture_graph(region: dict[str, Any]) -> nx.MultiDiGraph:
    """Return a compact routeable OSM-style graph around public pilot points."""

    graph = nx.MultiDiGraph(
        region_id=region["region_id"],
        source="curated_public_coordinate_osm_style_fixture",
        cache_role="offline_pilot_smoke",
    )
    nodes = {
        "n_olympic_park": (127.1210, 37.5202),
        "n_olympic_station": (127.1302, 37.5166),
        "n_baekjegobun": (127.1140, 37.5148),
        "n_jamsil_station": (127.1002, 37.5133),
        "n_jamsil_public_zone": (127.1025, 37.5180),
        "n_tancheon_corridor": (127.1080, 37.5200),
    }
    for node_id, (lon, lat) in nodes.items():
        graph.add_node(node_id, x=lon, y=lat, source="fixture_public_coordinate")

    undirected_edges = [
        ("n_olympic_park", "n_olympic_station", "pilot-001", "primary", 50),
        ("n_olympic_park", "n_baekjegobun", "pilot-002", "primary", 50),
        ("n_baekjegobun", "n_jamsil_station", "pilot-003", "secondary", 40),
        ("n_jamsil_station", "n_jamsil_public_zone", "pilot-004", "secondary", 40),
        ("n_olympic_park", "n_tancheon_corridor", "pilot-005", "secondary", 40),
        ("n_tancheon_corridor", "n_jamsil_public_zone", "pilot-006", "secondary", 40),
        ("n_olympic_station", "n_baekjegobun", "pilot-007", "tertiary", 35),
    ]
    for u, v, osmid, highway, speed in undirected_edges:
        _add_bidirectional_edge(graph, u, v, osmid=osmid, highway=highway, maxspeed=speed)

    return graph


def build_overpass_graph(region: dict[str, Any]) -> nx.MultiDiGraph:
    """Build a road graph from live Overpass data for manual cache refreshes."""

    boundary = region["boundary"]
    south = float(boundary["south"])
    west = float(boundary["west"])
    north = float(boundary["north"])
    east = float(boundary["east"])
    query = f"""
    [out:json][timeout:60];
    (
      way["highway"]({south},{west},{north},{east});
    );
    (._;>;);
    out body;
    """
    payload = urlencode({"data": query}).encode("utf-8")
    request = Request(OVERPASS_URL, data=payload, headers={"User-Agent": "transport-system-sim/1.0"})
    with urlopen(request, timeout=90) as response:
        data = json.loads(response.read().decode("utf-8"))

    nodes = {
        element["id"]: element
        for element in data["elements"]
        if element.get("type") == "node" and "lat" in element and "lon" in element
    }
    graph = nx.MultiDiGraph(
        region_id=region["region_id"],
        source="live_overpass_osm_snapshot",
        overpass_url=OVERPASS_URL,
    )
    for node_id, node in nodes.items():
        graph.add_node(str(node_id), x=float(node["lon"]), y=float(node["lat"]), source="osm_overpass")

    for way in data["elements"]:
        if way.get("type") != "way":
            continue
        tags = way.get("tags", {})
        highway = tags.get("highway")
        way_nodes = [node_id for node_id in way.get("nodes", []) if node_id in nodes]
        for start, end in zip(way_nodes, way_nodes[1:]):
            u = str(start)
            v = str(end)
            attrs = {
                "osmid": str(way["id"]),
                "highway": str(highway or "road"),
                "source": "osm_overpass",
                "length": _distance_between_nodes(graph, u, v),
                "name": tags.get("name", ""),
            }
            if "maxspeed" in tags:
                attrs["maxspeed"] = tags["maxspeed"]
            graph.add_edge(u, v, **attrs)
            if tags.get("oneway") not in {"yes", "true", "1"}:
                graph.add_edge(v, u, **attrs)
    if graph.number_of_edges() == 0:
        raise RuntimeError("Overpass extraction returned no road edges for the pilot bbox.")
    return graph


def _add_bidirectional_edge(
    graph: nx.MultiDiGraph,
    u: str,
    v: str,
    *,
    osmid: str,
    highway: str,
    maxspeed: int,
) -> None:
    length = _distance_between_nodes(graph, u, v)
    attrs = {
        "osmid": osmid,
        "highway": highway,
        "maxspeed": maxspeed,
        "length": length,
        "source": "fixture_public_coordinate",
    }
    graph.add_edge(u, v, **attrs)
    graph.add_edge(v, u, **attrs)


def _distance_between_nodes(graph: nx.Graph, u: str, v: str) -> float:
    u_data = graph.nodes[u]
    v_data = graph.nodes[v]
    return _distance_m(float(u_data["y"]), float(u_data["x"]), float(v_data["y"]), float(v_data["x"]))


def _distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    mean_lat = radians((lat1 + lat2) / 2.0)
    dx = (lon2 - lon1) * EARTH_M_PER_DEG_LAT * cos(mean_lat)
    dy = (lat2 - lat1) * EARTH_M_PER_DEG_LAT
    return sqrt(dx * dx + dy * dy)


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def _boundary_metadata(region: Mapping[str, Any]) -> dict[str, Any]:
    boundary = region.get("boundary", {})
    if not isinstance(boundary, Mapping):
        return {}
    return {
        "type": str(boundary.get("type", "")),
        "north": float(boundary["north"]),
        "south": float(boundary["south"]),
        "east": float(boundary["east"]),
        "west": float(boundary["west"]),
    }


def _tooling_metadata(source_note: str) -> dict[str, str]:
    metadata = {
        "builder": "scripts/build_pilot_cache.py",
        "graph_writer": "src.realworld.osm_network.save_graphml",
        "python_package": "networkx",
    }
    if source_note == "live_overpass_osm_snapshot":
        metadata.update(
            {
                "extractor": "Overpass API",
                "overpass_url": OVERPASS_URL,
                "query_filter": "way[\"highway\"](south,west,north,east)",
            }
        )
    else:
        metadata.update(
            {
                "extractor": "repository fixture builder",
                "query_filter": "curated public/synthetic pilot road edges",
            }
        )
    return metadata


def _relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    main()
