"""Generate a synthetic Songpa-Goseong mobilization corridor GraphML.

This script creates a minimal but realistic corridor graph for the
full-scale mobilization simulation.  It includes key cities and
intermediate road segments with estimated travel times.

Nodes:
  A   - Songpa Olympic Park (assembly)
  S   - Cheongnyangni Station (rail access)
  R   - Gangneung Station (rail egress)
  D   - Goseong Hakya-ri (destination)
  + intermediate road cities

Edges: road segments with t0 (free-flow minutes), capacity, highway class
"""

from __future__ import annotations

import math
from pathlib import Path

import networkx as nx

# --- Coordinate definitions -----------------------------------------------

NODES = {
    # Intermediate road cities (approximate coords)
    # NOTE: A, S, R, D are NOT in the road graph; they are snapped from
    # the region YAML by the adapter.  Road nodes near them are named
    # with a "road_" prefix to avoid canonical-ID conflicts.
    "road_songpa": {"x": 127.1210, "y": 37.5202, "label": "Songpa Road Node"},
    "road_cheongnyangni": {"x": 127.0484, "y": 37.5806, "label": "Cheongnyangni Road Node"},
    "road_gangneung": {"x": 128.8996, "y": 37.7645, "label": "Gangneung Road Node"},
    "road_goseong": {"x": 128.5500, "y": 38.3000, "label": "Goseong Road Node"},
    # Intermediate cities
    "Namyangju": {"x": 127.2100, "y": 37.6200, "label": "Namyangju"},
    "Guri": {"x": 127.1500, "y": 37.5900, "label": "Guri"},
    "Hanam": {"x": 127.2100, "y": 37.5400, "label": "Hanam"},
    "Seongnam": {"x": 127.1300, "y": 37.3800, "label": "Seongnam"},
    "Wabu": {"x": 127.2200, "y": 37.5800, "label": "Wabu"},
    "Seoul": {"x": 126.9800, "y": 37.5600, "label": "Seoul Center"},
    "Wonju": {"x": 127.9500, "y": 37.3400, "label": "Wonju"},
    "Chuncheon": {"x": 127.7300, "y": 37.8800, "label": "Chuncheon"},
    "Hongcheon": {"x": 128.2000, "y": 37.6900, "label": "Hongcheon"},
    "Neungseon": {"x": 127.8500, "y": 37.7200, "label": "Neungseon"},
    "Jeongseon": {"x": 128.6600, "y": 37.3800, "label": "Jeongseon"},
    "Taebaek": {"x": 128.9700, "y": 37.1700, "label": "Taebaek"},
    "Sokcho": {"x": 128.5900, "y": 38.1800, "label": "Sokcho"},
    "Yangyang": {"x": 128.4200, "y": 38.0700, "label": "Yangyang"},
    "Inje": {"x": 128.1700, "y": 38.0600, "label": "Inje"},
    "Goseong_town": {"x": 128.4500, "y": 38.3300, "label": "Goseong Town"},
}


def _approx_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Equirectangular distance in meters."""
    mean_lat = math.radians((lat1 + lat2) / 2.0)
    m_per_deg_lat = 111_320.0
    m_per_deg_lon = m_per_deg_lat * math.cos(mean_lat)
    dy = (lat2 - lat1) * m_per_deg_lat
    dx = (lon2 - lon1) * m_per_deg_lon
    return math.sqrt(dx * dx + dy * dy)


def _road_edge(u: str, v: str, *, base_speed_kph: float = 80.0,
               highway: str = "trunk", capacity: float = 2000.0) -> dict:
    """Build a road edge attribute dict between two named nodes."""
    nu = NODES[u]
    nv = NODES[v]
    dist_m = _approx_distance_m(nu["y"], nu["x"], nv["y"], nv["x"])
    t0_min = dist_m / (base_speed_kph * 1000.0 / 60.0)
    return {
        "t0": round(t0_min, 2),
        "capacity": capacity,
        "base_p_fail": 0.02,
        "p_fail": 0.02,
        "mode": "road",
        "length_m": round(dist_m),
        "speed_kph": base_speed_kph,
        "highway": highway,
        "source": "synthetic_corridor",
    }


def build_corridor_graph() -> nx.DiGraph:
    """Return a directed corridor graph with bidirectional road edges."""
    G = nx.DiGraph()

    for node_id, data in NODES.items():
        G.add_node(node_id, **data)

    # --- Major corridor edges (bidirectional) ----------------------------

    road_edges = [
        # Seoul metro feeder (near region points)
        ("road_songpa", "road_cheongnyangni", 60, "trunk", 1500),
        ("road_songpa", "Seoul", 70, "trunk", 2000),
        ("road_cheongnyangni", "Seoul", 50, "trunk", 2000),
        ("road_songpa", "Guri", 60, "trunk", 1500),
        ("road_songpa", "Hanam", 60, "trunk", 1500),
        ("Guri", "Namyangju", 60, "trunk", 1500),
        ("Namyangju", "Wabu", 60, "trunk", 1200),
        ("Wabu", "Hanam", 60, "trunk", 1200),
        ("Guri", "Seoul", 70, "trunk", 2000),
        ("Hanam", "Seongnam", 80, "trunk", 1500),
        # Seoul -> Wonju (central corridor)
        ("Seoul", "Wonju", 100, "motorway", 2000),
        ("Wonju", "Chuncheon", 90, "trunk", 1500),
        # Wonju -> Jeongseon (eastern mountains)
        ("Wonju", "Neungseon", 70, "trunk", 1200),
        ("Neungseon", "Jeongseon", 70, "trunk", 800),
        ("Jeongseon", "Taebaek", 70, "trunk", 800),
        # Chuncheon -> Gangneung (eastern corridor)
        ("Chuncheon", "Hongcheon", 80, "trunk", 1200),
        ("Hongcheon", "Inje", 80, "trunk", 1000),
        ("Inje", "Yangyang", 80, "trunk", 1000),
        ("Yangyang", "road_gangneung", 80, "trunk", 1200),
        # Gangneung -> Goseong (coastal/northern)
        ("road_gangneung", "Yangyang", 80, "trunk", 1200),
        ("Yangyang", "Goseong_town", 80, "trunk", 1000),
        ("Goseong_town", "road_goseong", 60, "trunk", 800),
        # Cross connections
        ("Hongcheon", "road_gangneung", 80, "trunk", 1200),
        ("Inje", "Sokcho", 70, "trunk", 800),
        ("Sokcho", "Goseong_town", 70, "trunk", 600),
        ("Yangyang", "Sokcho", 70, "trunk", 600),
        # Seoul -> Chuncheon (existing expressway analog)
        ("Seoul", "Chuncheon", 100, "motorway", 2000),
    ]

    for u, v, speed, hw, cap in road_edges:
        attrs = _road_edge(u, v, base_speed_kph=speed, highway=hw, capacity=cap)
        G.add_edge(u, v, **attrs)
        G.add_edge(v, u, **attrs)

    return G


def write_graphml(G: nx.DiGraph, path: Path) -> None:
    """Write graph to GraphML."""
    path.parent.mkdir(parents=True, exist_ok=True)
    nx.write_graphml(G, str(path))
    print(f"Wrote {G.number_of_nodes()} nodes, {G.number_of_edges()} edges -> {path}")


if __name__ == "__main__":
    out = Path("data/cache/goseong_corridor_road.graphml")
    # DEPRECATED (Phase 1): this emits the synthetic corridor skeleton. Refuse
    # to overwrite a real OSM-derived cache (build_goseong_cache.py --source
    # overpass) so the synthetic stub cannot regress the case-study graph.
    if out.exists() and out.stat().st_size > 50_000:
        raise SystemExit(
            f"REFUSING to overwrite real cache {out} with the deprecated synthetic "
            "skeleton. Use scripts/build_goseong_cache.py --source overpass instead."
        )
    graph = build_corridor_graph()
    write_graphml(graph, out)
