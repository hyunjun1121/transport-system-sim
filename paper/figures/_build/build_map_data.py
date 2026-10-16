# -*- coding: utf-8 -*-
"""Build corridor-map geometry (그림 2) from the cached nodelink graphml.

Output: paper/figures/_build/map_geo.json with
  - nodes : {A,S,R,D -> {name,role,lon,lat}}
  - motorway_skeleton : list of [[lon,lat],[lon,lat]] expressway segments
                        (highway in {motorway,trunk} within corridor bbox, subsampled)
  - routes : {road_A_S, road_R_D, road_A_D, road_S_R} -> list of [lon,lat] polyline
  - rail_waypoints : stylized S->R KTX 경강선 alignment (public station centroids)

Graphml load is ~49s, so this is a one-time builder; the figure renderer reads JSON.
All coordinates are PUBLIC administrative centroids / public rail stations only.
"""
import sys, json, time
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import networkx as nx

GRAPHML = "data/cache/goseong_nodelink_road.graphml"
OUT = "paper/figures/_build/map_geo.json"

# Public coordinates (region yaml + public rail stations) -- coordinate_class: public
NODES = {
    "A": {"name": "A Songpa assembly", "role": "assembly (Olympic Park)", "lon": 127.1210, "lat": 37.5202},
    "S": {"name": "S Cheongnyangni Stn", "role": "rail access station", "lon": 127.0484, "lat": 37.5806},
    "R": {"name": "R Gangneung Stn", "role": "rail egress station", "lon": 128.8996, "lat": 37.7645},
    "D": {"name": "D Goseong destination", "role": "destination (Tochon-myeon centroid)", "lon": 128.5500, "lat": 38.3000},
}

# Corridor bbox (matches region yaml boundary) for skeleton subsetting
BBOX = {"w": 126.95, "s": 37.45, "e": 128.95, "n": 38.35}


def main():
    t0 = time.time()
    print("loading graphml ...")
    G = nx.read_graphml(GRAPHML)
    print(f"  loaded {G.number_of_nodes()} nodes / {G.number_of_edges()} edges in {time.time()-t0:.1f}s")

    nds = list(G.nodes())
    xs = np.array([float(G.nodes[n]["x"]) for n in nds])
    ys = np.array([float(G.nodes[n]["y"]) for n in nds])

    def snap(lon, lat):
        d = (xs - lon) ** 2 + (ys - lat) ** 2
        return nds[int(d.argmin())]

    sn = {k: snap(v["lon"], v["lat"]) for k, v in NODES.items()}
    print("snapped:", sn)

    # collapse parallel edges to a simple graph, weight = min length_m
    print("building simple weighted graph ...")
    H = nx.Graph()
    for u, v, d in G.edges(data=True):
        try:
            w = float(d.get("length_m") or d.get("length") or 1.0)
        except Exception:
            w = 1.0
        if H.has_edge(u, v):
            if w < H[u][v]["_w"]:
                H[u][v]["_w"] = w
        else:
            H.add_edge(u, v, _w=w, highway=d.get("highway", ""))

    def path_poly(a, b):
        try:
            p = nx.shortest_path(H, sn[a], sn[b], weight="_w")
        except Exception as e:
            print(f"  {a}->{b} path FAIL: {e}")
            return []
        poly = [[float(G.nodes[n]["x"]), float(G.nodes[n]["y"])] for n in p]
        km = sum(H[p[i]][p[i + 1]]["_w"] for i in range(len(p) - 1)) / 1000.0
        print(f"  {a}->{b}: {len(p)} nodes, {km:.1f} km")
        return poly

    t1 = time.time()
    routes = {
        "road_A_S": path_poly("A", "S"),   # multimodal access shuttle (bus)
        "road_R_D": path_poly("R", "D"),   # multimodal last-mile (bus)
        "road_A_D": path_poly("A", "D"),   # bus_only trunk (full road)
        "road_S_R": path_poly("S", "R"),   # road alternative to rail (for reference)
    }
    print(f"  routes in {time.time()-t1:.1f}s")

    # motorway/trunk skeleton within bbox (expressway backbone)
    print("extracting expressway skeleton ...")
    motorway = []   # 고속도로 (clean expressway backbone)
    trunk = []      # trunk arterial (context)
    for u, v, d in G.edges(data=True):
        hw = d.get("highway", "")
        if hw not in ("motorway", "trunk"):
            continue
        xu, yu = float(G.nodes[u]["x"]), float(G.nodes[u]["y"])
        xv, yv = float(G.nodes[v]["x"]), float(G.nodes[v]["y"])
        if not (BBOX["w"] <= (xu + xv) / 2 <= BBOX["e"] and BBOX["s"] <= (yu + yv) / 2 <= BBOX["n"]):
            continue
        seg = [[xu, yu], [xv, yv]]
        (motorway if hw == "motorway" else trunk).append(seg)
    print(f"  motorway={len(motorway)} trunk={len(trunk)}")

    # stylized rail S->R along public KTX 경강선 station centroids (NOT from graphml -- no rail geometry)
    rail_waypoints = [
        [127.0484, 37.5806],  # S 청량리
        [127.4910, 37.4910],  # 양평
        [128.0590, 37.4915],  # 횡성
        [128.3300, 37.6300],  # 평창진부
        [128.6200, 37.6900],  # 정선·예미
        [128.8996, 37.7645],  # R 강릉
    ]

    out = {
        "nodes": NODES,
        "bbox": BBOX,
        "motorway_skeleton": motorway,
        "routes": routes,
        "rail_waypoints": rail_waypoints,
        "_meta": {"graph_nodes": G.number_of_nodes(), "graph_edges": G.number_of_edges(),
                  "coordinate_policy": "public administrative centroids / public rail stations only"},
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print(f"wrote {OUT} ({len(json.dumps(out))} chars) total {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
