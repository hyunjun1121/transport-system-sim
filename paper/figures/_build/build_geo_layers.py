# -*- coding: utf-8 -*-
"""Add data-derived geo layers (coastline, rail centerline) to map_geo.json.

Sources (all public national base map / admin boundary data under data-collections/):
  data-collections/행정경계(시도)/N3A_G0010000.zip   (연속수치지형도 시도 경계 폴리곤)
      -> "coastline": 강원특별자치도 폴리곤 경계 중 동해안 구간 (south→north)
  data-collections/철도중심선/N3L_A0171119.zip       (연속수치지형도 철도중심선)
      -> "rail_centerline": 청량리(S)→강릉(R) 실제 선로 정렬
         = NAME∈{중앙선(회랑 필터), KTX강릉선, 강릉선} 레코드를 중복 제거·연결한 단일 폴리라인

Existing keys of map_geo.json (nodes / routes / motorway_skeleton / rail_waypoints)
are preserved untouched: this script only ADDS layer keys. CRS: EPSG:5179 -> WGS84.
The 중앙선 corridor filter chain uses public station coordinates only (filter input,
never drawn); the drawn geometry is the official centerline itself.
"""
import sys, io, json, zipfile, math
sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
import shapefile
from pyproj import Transformer

MG = "paper/figures/_build/map_geo.json"
SIDO_ZIP = r"data-collections/행정경계(시도)/N3A_G0010000.zip"

RAIL_ZIP = r"data-collections/철도중심선/N3L_A0171119.zip"
T = Transformer.from_crs(5179, 4326, always_xy=True)

# public station centroids, corridor spine for filtering 중앙선 records and ordering
# joined chains along S->R (filter/ordering input only, never drawn)
CHAIN_BASE = [
    (127.0484, 37.5806),  # 청량리 (S)
    (127.0910, 37.5990),  # 망우
    (127.1610, 37.6080),  # 도농
    (127.2085, 37.5866),  # 덕소
    (127.2440, 37.5460),  # 팔당
    (127.3400, 37.5480),  # 양수 부근
    (127.4877, 37.4926),  # 양평
    (127.5750, 37.4820),  # 용문
    (127.6600, 37.4500),  # 지평-일신 부근
    (127.7570, 37.4084),  # 양동
    (127.8703, 37.4041),  # 서원주
]
KTX_STATIONS = [
    (127.9850, 37.4780),  # 횡성
    (128.1550, 37.4920),  # 둔내
    (128.3985, 37.5580),  # 평창 (용평면 백옥포리)
    (128.5660, 37.6450),  # 진부
    (128.9000, 37.7500),  # 강릉 진입
]
S = (127.0484, 37.5806)
R = (128.8996, 37.7645)
LONSC = math.cos(math.radians(37.8))  # lon->km anisotropy factor for distances


def _rd(zippath, base):
    zf = zipfile.ZipFile(zippath)
    return shapefile.Reader(
        shp=io.BytesIO(zf.read(base + ".shp")),
        dbf=io.BytesIO(zf.read(base + ".dbf")),
        shx=io.BytesIO(zf.read(base + ".shx")), encoding="cp949")


def dist_pt_seg(p, a, b):
    ax, ay = (a[0] - p[0]) * LONSC, a[1] - p[1]
    bx, by = (b[0] - p[0]) * LONSC, b[1] - p[1]
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, -(ax * dx + ay * dy) / L2))
    cx, cy = ax + t * dx, ay + t * dy
    return math.hypot(cx, cy)


def dist_to_chain(p, chain):
    return min(dist_pt_seg(p, chain[i], chain[i + 1]) for i in range(len(chain) - 1))


def thin(poly, step=0.0012):
    out = [poly[0]]
    for p in poly[1:-1]:
        q = out[-1]
        if max(abs(p[0] - q[0]), abs(p[1] - q[1])) >= step:
            out.append(p)
    out.append(poly[-1])
    return out


def _longest_run(shape, window):
    """Longest consecutive point run of a (multi-part) polygon boundary inside window."""
    pts = np.array(shape.points)
    parts = list(shape.parts) + [len(pts)]
    best = []
    for pi in range(len(parts) - 1):
        seg = pts[parts[pi]:parts[pi + 1]]
        if len(seg) < 2:
            continue
        lon, lat = T.transform(seg[:, 0], seg[:, 1])
        ok = window(lon, lat)
        i = 0
        while i < len(ok):
            if ok[i]:
                j = i
                while j < len(ok) and ok[j]:
                    j += 1
                if j - i > len(best):
                    best = list(zip(lon[i:j], lat[i:j]))
                i = j
            else:
                i += 1
    return best


def coastline():
    # 시도 폴리곤 (강원) east-coast run. Dataset coverage note: every polygon in the
    # N3A layers is clipped near the civilian-control line, so the coast tops out at
    # (128.507, 38.376) — the map's LAT1 is chosen at 38.38 to stay inside coverage.
    # The lat-dependent lon threshold excludes the inland 강원/경북 southern border
    # (lat<37.30 runs at lon 128.2..129.25; the true coast there is lon>129.30).
    r = _rd(SIDO_ZIP, "N3A_G0010000")
    idx = next(i for i, rec in enumerate(r.iterRecords()) if rec[2] == "강원특별자치도")
    best = _longest_run(
        r.shape(idx),
        lambda lon, lat: (lon > 128.20) & (lat > 37.00) & (lat < 38.62)
                         & ((lat >= 37.30) | (lon > 129.28)))
    assert len(best) > 100, f"coast run too short: {len(best)}"
    if best[0][1] > best[-1][1]:
        best.reverse()  # order south -> north
    out = thin([list(p) for p in best], 0.004)
    lats = [p[1] for p in out]
    assert min(lats) < 37.12 and max(lats) > 38.37, f"coast does not span map lat range: {min(lats)}..{max(lats)}"
    print(f"coastline: {len(out)} pts, lat {min(lats):.3f}..{max(lats):.3f}, "
          f"lon {min(p[0] for p in out):.3f}..{max(p[0] for p in out):.3f}")
    return out


def rail_centerline():
    r = _rd(RAIL_ZIP, "N3L_A0171119")
    keep, seen = [], set()
    pool = []  # (name, polyline)
    for sr in r.iterShapeRecords():
        nm = sr.record[1]
        if nm not in ("KTX강릉선", "강릉선", "중앙선"):
            continue
        pts = np.array(sr.shape.points)
        parts = list(sr.shape.parts) + [len(pts)]
        for pi in range(len(parts) - 1):
            seg = pts[parts[pi]:parts[pi + 1]]
            if len(seg) < 2:
                continue
            lon, lat = T.transform(seg[:, 0], seg[:, 1])
            poly = list(zip(lon, lat))
            key = (round(poly[0][0], 6), round(poly[0][1], 6), round(poly[-1][0], 6),
                   round(poly[-1][1], 6), len(poly))
            k2 = tuple(reversed(key[:4])) + (key[4],)
            if key in seen or k2 in seen:
                continue  # sheet-boundary duplicate
            seen.add(key)
            pool.append((nm, poly))
    # west end of the joined KTX강릉선 = dynamic junction target for the 중앙선 filter
    ktx_pts = [p for nm, poly in pool if nm == "KTX강릉선" for p in poly]
    W = min(ktx_pts, key=lambda p: p[0])
    chain = CHAIN_BASE + [W]
    print(f"KTX강릉선 west end (중앙선 junction target): {W[0]:.4f},{W[1]:.4f}")
    for nm, poly in pool:
        if nm != "중앙선":
            keep.append(poly)
            continue
        mid = poly[len(poly) // 2]
        cand = [poly[0], mid, poly[-1]]
        if all(127.035 <= p[0] <= max(127.97, W[0] + 0.01) and 37.28 <= p[1] <= 37.65 for p in cand) \
                and all(dist_to_chain(p, chain) <= 0.045 for p in cand):
            keep.append(poly)
    print(f"rail records kept: {len(keep)}")

    def length_km(c):
        return sum(math.hypot((c[i + 1][0] - c[i][0]) * LONSC, c[i + 1][1] - c[i][1])
                   for i in range(len(c) - 1)) * 111.0

    # Shortest path S->R on the segment graph (same pattern as the road builder):
    # nodes = record endpoints (rounded ~1 m), edges = record polylines weighted by
    # length. Endpoint pairs within BRIDGE_DEG get a penalized straight edge so tiny
    # sheet gaps close, while parallel tracks / sidings are simply never traversed.
    import networkx as nx
    G = nx.Graph()

    def nkey(p):
        return (round(p[0], 5), round(p[1], 5))

    for poly in keep:
        a, b = nkey(poly[0]), nkey(poly[-1])
        w = length_km(poly)
        if a == b:
            continue
        if not G.has_edge(a, b) or w < G[a][b]["w"]:
            G.add_edge(a, b, w=w, poly=poly)
    ends = list(G.nodes())
    # The 연속수치지형도 maps SURFACE features only: rail inside tunnels is absent
    # (대관령터널 ~22 km leaves the biggest hole), so surface fragments are linked by
    # penalized straight bridge edges. A tunnel alignment is near-straight, so the
    # bridge is also the geometrically faithful rendering of the missing stretch.
    BRIDGE_DEG, PENALTY, KNEAR = 0.25, 6.0, 30
    arr = np.array(ends)
    for i, e in enumerate(ends):
        d = np.hypot((arr[:, 0] - e[0]) * LONSC, arr[:, 1] - e[1])
        cand = np.nonzero((d > 1e-12) & (d < BRIDGE_DEG))[0]
        cand = cand[np.argsort(d[cand])][:KNEAR]
        for j in cand:
            o = ends[j]
            if not G.has_edge(e, o):
                G.add_edge(e, o, w=float(d[j]) * 111.0 * PENALTY,
                           poly=[list(e), list(o)], bridge=True)

    def nearest_node(p):
        d = np.hypot((arr[:, 0] - p[0]) * LONSC, arr[:, 1] - p[1])
        return ends[int(d.argmin())]

    nS, nR = nearest_node(S), nearest_node(R)
    print(f"  snap S->{nS} R->{nR}")
    path = nx.shortest_path(G, nS, nR, weight="w")
    line, n_bridge = [], 0
    for u, v in zip(path[:-1], path[1:]):
        e = G[u][v]
        poly = e["poly"]
        if e.get("bridge"):
            n_bridge += 1
        if nkey(poly[0]) != u:
            poly = poly[::-1]
        line.extend(poly if not line else poly[1:])
    print(f"  path: {len(path)} graph nodes, {n_bridge} small bridges")
    # anchor the drawn line at the public station pins S / R (개념선 label covers the join)
    if math.hypot(line[0][0] - S[0], line[0][1] - S[1]) > 1e-3:
        line = [list(S)] + line
    if math.hypot(line[-1][0] - R[0], line[-1][1] - R[1]) > 1e-3:
        line = line + [list(R)]
    out = thin([list(p) for p in line], 0.0012)
    lons = [p[0] for p in out]; lats = [p[1] for p in out]
    km = length_km(out)
    print(f"rail_centerline: {len(out)} pts, {km:.0f} km, "
          f"lon {min(lons):.3f}..{max(lons):.3f}, lat {min(lats):.3f}..{max(lats):.3f}")
    assert abs(out[0][0] - S[0]) < 1e-6 and abs(out[-1][0] - R[0]) < 1e-6
    assert 200 <= km <= 270, f"rail path length implausible: {km:.0f} km (청량리-강릉 ~ 230 km)"
    for st in KTX_STATIONS:
        dmin = min(math.hypot((p[0] - st[0]) * LONSC, p[1] - st[1]) for p in out)
        assert dmin < 0.06, f"rail path misses station {st}: {dmin:.3f} deg"
    return out


def main():
    geo = json.load(open(MG, encoding="utf-8"))
    before = {k: json.dumps(geo[k]) for k in ("nodes", "routes", "motorway_skeleton", "rail_waypoints")}
    geo["coastline"] = coastline()
    geo["rail_centerline"] = rail_centerline()
    geo["_layers_meta"] = {
        "coastline_source": "data-collections/행정경계(시도)/N3A_G0010000.zip (강원특별자치도 동해안 경계, EPSG:5179->WGS84)",
        "rail_source": "data-collections/철도중심선/N3L_A0171119.zip (NAME∈{중앙선(회랑필터),KTX강릉선,강릉선})",
        "note": "layers added for 그림 2 rendering; nodes/routes/skeleton/rail_waypoints unchanged",
    }
    for k, v in before.items():
        assert json.dumps(geo[k]) == v, f"existing key {k} mutated!"
    with open(MG, "w", encoding="utf-8") as f:
        json.dump(geo, f, ensure_ascii=False)
    print(f"wrote {MG}")


if __name__ == "__main__":
    main()
