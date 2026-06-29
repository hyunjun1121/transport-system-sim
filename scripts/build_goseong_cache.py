"""Build the Goseong case-study road-graph cache from live OSM (Overpass).

Phase-1 (D-GOSEONG) replacement for the synthetic ``build_goseong_corridor.py``
skeleton. The Goseong corridor spans ~100x176 km (Seoul+Gangwon diagonal); a
naive single Overpass ``way["highway"]`` query over that bbox times out, so this
extracts only the bus-relevant major-road classes (motorway/trunk/primary/
secondary) and tiles the corridor along its public centroid waypoints, then
stitches the tiles into one graph. All coordinates are public administrative
centroids / public transport network only (coordinate_class=public); no real
unit coordinates.

Usage (explicit live opt-in; offline-by-default is otherwise preserved)::

    ./.venv/Scripts/python scripts/build_goseong_cache.py --source overpass

Default ``--source existing`` preserves an existing cache. The output is a
decision-support / quasi-real snapshot, NOT calibrated — ``final_study_ready``
stays false.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from math import cos, radians, sqrt
from pathlib import Path
import sys
import time
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import networkx as nx
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.osm_network import save_graphml  # noqa: E402

DEFAULT_REGION_PATH = ROOT / "data" / "regions" / "goseong_mobilization.yaml"
DEFAULT_CACHE_PATH = ROOT / "data" / "cache" / "goseong_corridor_road.graphml"
DEFAULT_MANIFEST_PATH = ROOT / "data" / "cache" / "goseong_corridor_road_manifest.json"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
EARTH_M_PER_DEG_LAT = 111_320.0

# Major + connector road classes. tertiary/unclassified are required for
# end-to-end connectivity (motorway/trunk alone fragment into ~60 components
# across this 200km corridor); they bridge interchanges and access roads so
# A->D / A->S / S->R / R->D routes exist after adapter snapping.
HIGHWAY_FILTER = "motorway|trunk|primary|secondary|tertiary|unclassified"
# Public centroid corridor waypoints (lat, lon) — administrative centroids only.
# These TRACE the actual road corridor (Gyeongchun + Yeongdong expressway +
# coastal Route 7) via the intermediate cities the roads pass through
# (Hongcheon, Yangyang, Sokcho). A straight Songpa->Goseong skeleton fragments
# because the expressway weaves through the mountains away from the chord.
CORRIDOR_WAYPOINTS: list[tuple[float, float]] = [
    (37.5202, 127.1210),  # Songpa (assembly A) -- covers Seoul NE approach
    (37.8800, 127.7300),  # Chuncheon
    (37.6900, 128.2000),  # Hongcheon (Yeongdong expressway mountain pass)
    (37.7645, 128.8996),  # Gangneung (rail egress R)
    (38.0700, 128.4200),  # Yangyang
    (38.1800, 128.5900),  # Sokcho
    (38.3000, 128.5500),  # Goseong (destination D)
]
BUFFER_KM = 6.0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region", default=str(DEFAULT_REGION_PATH))
    parser.add_argument("--cache", default=str(DEFAULT_CACHE_PATH))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST_PATH))
    parser.add_argument(
        "--source",
        choices=("existing", "fixture", "overpass"),
        default="existing",
        help="Preserve existing by default; overpass = explicit live extraction.",
    )
    parser.add_argument(
        "--highway-filter",
        default=HIGHWAY_FILTER,
        help="Pipe-separated OSM highway classes to extract.",
    )
    parser.add_argument("--buffer-km", type=float, default=BUFFER_KM)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument(
        "--full-bbox",
        action="store_true",
        help=(
            "Extract the whole region boundary as a SINGLE Overpass query instead "
            "of corridor tiles. Avoids tile-boundary connectivity gaps on a long, "
            "winding mountain corridor; use a tight --highway-filter to stay tractable."
        ),
    )
    args = parser.parse_args()

    region = _load_yaml(Path(args.region))
    cache_path = Path(args.cache)
    manifest_path = Path(args.manifest)

    if args.source == "existing" and cache_path.exists() and manifest_path.exists():
        print(f"preserved existing {cache_path}")
        return

    if args.source in ("existing", "fixture"):
        print("No fixture fallback for Goseong; use --source overpass for live OSM.")
        print("The synthetic build_goseong_corridor.py skeleton is deprecated (Phase 1).")
        raise SystemExit(2)

    if args.full_bbox:
        boundary = region["boundary"]
        tiles = [(
            float(boundary["south"]), float(boundary["west"]),
            float(boundary["north"]), float(boundary["east"]),
        )]
        print(f"single full-bbox mode: {tiles[0]}")
    else:
        tiles = None  # derive from waypoints inside the builder

    graph = build_corridor_overpass_graph(
        highway_filter=args.highway_filter,
        buffer_km=args.buffer_km,
        timeout=args.timeout,
        tiles=tiles,
    )
    save_graphml(graph, cache_path)
    manifest = build_cache_manifest(
        region=region,
        region_path=Path(args.region),
        cache_path=cache_path,
        graph=graph,
        highway_filter=args.highway_filter,
        buffer_km=args.buffer_km,
        full_bbox=args.full_bbox,
    )
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"wrote {cache_path} ({graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges)")
    print(f"wrote {manifest_path}")


def build_corridor_overpass_graph(
    *,
    highway_filter: str,
    buffer_km: float,
    timeout: int,
    tiles: list[tuple[float, float, float, float]] | None = None,
) -> nx.MultiDiGraph:
    """Extract major roads per tile and stitch. ``tiles=None`` -> corridor waypoints."""

    tile_list = tiles if tiles is not None else corridor_tiles(
        CORRIDOR_WAYPOINTS, buffer_km=buffer_km
    )
    print(f"tiles: {len(tile_list)} (filter={highway_filter!r}, buffer {buffer_km} km)")
    merged = nx.MultiDiGraph(
        region_id="goseong_mobilization",
        source="live_overpass_osm_snapshot",
        overpass_url=OVERPASS_URL,
        highway_filter=highway_filter,
    )
    seen_ways: set[str] = set()
    for index, (south, west, north, east) in enumerate(tile_list, start=1):
        print(f"  tile {index}/{len(tile_list)} bbox(s={south:.4f} w={west:.4f} n={north:.4f} e={east:.4f})")
        elements = _overpass_tile(south, west, north, east, highway_filter, timeout)
        _merge_elements(merged, elements, seen_ways)
        time.sleep(15.0)  # respect the public Overpass rate limit (2 slots)
    if merged.number_of_edges() == 0:
        raise RuntimeError("Overpass extraction returned no major-road edges along the corridor.")
    return merged


def corridor_tiles(
    waypoints: list[tuple[float, float]],
    *,
    buffer_km: float,
) -> list[tuple[float, float, float, float]]:
    """Return (south, west, north, east) bboxes, one per waypoint-to-waypoint leg."""

    deg = buffer_km / EARTH_M_PER_DEG_LAT
    tiles: list[tuple[float, float, float, float]] = []
    for (lat1, lon1), (lat2, lon2) in zip(waypoints, waypoints[1:]):
        south = min(lat1, lat2) - deg
        north = max(lat1, lat2) + deg
        mean_lat = radians((lat1 + lat2) / 2.0)
        deg_lon = deg / cos(mean_lat)
        west = min(lon1, lon2) - deg_lon
        east = max(lon1, lon2) + deg_lon
        tiles.append((south, west, north, east))
    return tiles


def _overpass_tile(
    south: float, west: float, north: float, east: float,
    highway_filter: str, timeout: int,
) -> list[dict[str, Any]]:
    from urllib.error import HTTPError, URLError

    # Single anchored alternation: ^(motorway|trunk|...)$ — POSIX-clean and
    # correctly matches compound classes like motorway_link / trunk_link.
    classes = "^(" + "|".join(highway_filter.split("|")) + ")$"
    query = f"""
    [out:json][timeout:{timeout}];
    (
      way["highway"~"{classes}"]({south},{west},{north},{east});
    );
    (._;>;);
    out body;
    """
    payload = urlencode({"data": query}).encode("utf-8")
    last_error: Exception | None = None
    for attempt in range(4):
        request = Request(
            OVERPASS_URL,
            data=payload,
            headers={"User-Agent": "transport-system-sim/1.0 (goseong-case-study)"},
        )
        try:
            with urlopen(request, timeout=timeout + 30) as response:
                data = json.loads(response.read().decode("utf-8"))
            return data.get("elements", [])
        except HTTPError as exc:
            last_error = exc
            if exc.code == 429:
                wait = 30 * (attempt + 1)
                print(f"    429 Too Many Requests (attempt {attempt + 1}); waiting {wait}s")
                time.sleep(wait)
                continue
            raise
        except (URLError, TimeoutError) as exc:
            last_error = exc
            wait = 20 * (attempt + 1)
            print(f"    {type(exc).__name__} (attempt {attempt + 1}); waiting {wait}s")
            time.sleep(wait)
            continue
    raise RuntimeError(f"Overpass tile failed after retries: {last_error}")


def _merge_elements(
    graph: nx.MultiDiGraph, elements: list[dict[str, Any]], seen_ways: set[str],
) -> None:
    nodes = {
        el["id"]: el
        for el in elements
        if el.get("type") == "node" and "lat" in el and "lon" in el
    }
    for node_id, node in nodes.items():
        if not graph.has_node(str(node_id)):
            graph.add_node(
                str(node_id),
                x=float(node["lon"]),
                y=float(node["lat"]),
                source="osm_overpass",
            )
    for way in elements:
        if way.get("type") != "way":
            continue
        way_id = str(way["id"])
        tags = way.get("tags", {})
        highway = tags.get("highway")
        way_nodes = [nid for nid in way.get("nodes", []) if nid in nodes]
        for start, end in zip(way_nodes, way_nodes[1:]):
            u, v = str(start), str(end)
            attrs = {
                "osmid": way_id,
                "highway": str(highway or "road"),
                "source": "osm_overpass",
                "length": _distance_between_nodes(graph, u, v),
                "name": tags.get("name", ""),
            }
            if "maxspeed" in tags:
                attrs["maxspeed"] = tags["maxspeed"]
            if "lanes" in tags:
                attrs["lanes"] = tags["lanes"]
            graph.add_edge(u, v, **attrs)
            if tags.get("oneway") not in {"yes", "true", "1", "-1"}:
                graph.add_edge(v, u, **attrs)
        seen_ways.add(way_id)


def _distance_between_nodes(graph: nx.Graph, u: str, v: str) -> float:
    ud = graph.nodes[u]
    vd = graph.nodes[v]
    return _distance_m(float(ud["y"]), float(ud["x"]), float(vd["y"]), float(vd["x"]))


def _distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    mean_lat = radians((lat1 + lat2) / 2.0)
    dx = (lon2 - lon1) * EARTH_M_PER_DEG_LAT * cos(mean_lat)
    dy = (lat2 - lat1) * EARTH_M_PER_DEG_LAT
    return sqrt(dx * dx + dy * dy)


def build_cache_manifest(
    *,
    region: dict[str, Any],
    region_path: Path,
    cache_path: Path,
    graph: nx.Graph,
    highway_filter: str,
    buffer_km: float,
    full_bbox: bool = False,
    created_utc: str | None = None,
) -> dict[str, Any]:
    graphml_sha256 = hashlib.sha256(cache_path.read_bytes()).hexdigest()
    return {
        "region_id": region["region_id"],
        "cache_path": _relative(cache_path),
        "region_path": _relative(region_path),
        "source": "live_overpass_osm_snapshot",
        "created_utc": created_utc
        or datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "extraction": {
            "highway_filter": highway_filter,
            "buffer_km": buffer_km,
            "mode": "full_bbox" if full_bbox else "corridor_tiles",
            "waypoints": CORRIDOR_WAYPOINTS,
            "tile_count": 1 if full_bbox else len(corridor_tiles(CORRIDOR_WAYPOINTS, buffer_km=buffer_km)),
        },
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
        "graph_type": graph.__class__.__name__,
        "graphml_sha256": graphml_sha256,
        "live_services_required_for_default_tests": False,
        "attribution": "OpenStreetMap contributors; respect OSM/Overpass attribution requirements.",
        "coordinate_policy": "public_administrative_centroids_and_public_transport_network_only",
        "claim_limit": (
            "Cached Overpass/OSM snapshot of major roads along the public corridor; "
            "supports offline decision-support / quasi-real simulation only. NOT calibrated, "
            "NOT an operational route plan, NOT final-study evidence. final_study_ready=false."
        ),
    }


def _load_yaml(path: Path) -> dict[str, Any]:
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
