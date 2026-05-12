"""Generate Figure 2 for the KCI manuscript: Songpa-Yangju corridor map.

The figure shows the corridor bounding box, the cached OSMnx road graph
(arterial-class edges emphasised, minor edges drawn pale), the four
candidate origins (A/B/C/D), the canonical destination T (72사단 부곡리),
and the two rail nodes S (잠실역) and R (의정부역). Korean labels are
rendered with Malgun Gothic when available.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import networkx as nx
import yaml
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from matplotlib.offsetbox import AnchoredText
from matplotlib.patches import FancyArrowPatch, Rectangle


ROOT = Path(__file__).resolve().parents[1]
REGION_YAML = ROOT / "data" / "regions" / "songpa_yangju_corridor.yaml"
ORIGINS_JSON = ROOT / "data" / "regions" / "origin_candidates.json"
GRAPHML = ROOT / "data" / "cache" / "songpa_yangju_corridor.graphml"
OUTPUT_PNG = ROOT / "manuscript" / "figures" / "figure2_corridor_map.png"
CAPTION_MD = ROOT / "manuscript" / "figures" / "figure2_caption_ko.md"

ROUTEABLE_HIGHWAY_CLASSES = frozenset({
    "motorway",
    "motorway_link",
    "trunk",
    "trunk_link",
    "primary",
    "primary_link",
    "secondary",
    "secondary_link",
})

# Approximate metres-per-degree at mid-Korea latitude (~37.6 N).
KM_PER_DEG_LAT = 111.0


def _configure_korean_font() -> str:
    candidates = [
        "Malgun Gothic",
        "NanumGothic",
        "Nanum Gothic",
        "AppleGothic",
        "Hancom Gothic",
        "Noto Sans CJK KR",
    ]
    installed = {f.name for f in fm.fontManager.ttflist}
    chosen = next((c for c in candidates if c in installed), None)
    if chosen is None:
        chosen = "DejaVu Sans"
        print(
            f"WARNING: no Korean font found, falling back to {chosen}. "
            f"Tried: {candidates}",
            file=sys.stderr,
        )
    matplotlib.rcParams["font.family"] = chosen
    matplotlib.rcParams["axes.unicode_minus"] = False
    return chosen


_LINESTRING_RE = re.compile(r"LINESTRING\s*\(\s*(.*?)\s*\)", re.IGNORECASE | re.DOTALL)


def _parse_linestring(wkt: str) -> list[tuple[float, float]] | None:
    """Parse a WKT 'LINESTRING (lon lat, lon lat, ...)' into (lon, lat) tuples."""
    m = _LINESTRING_RE.search(wkt)
    if not m:
        return None
    pts = []
    for piece in m.group(1).split(","):
        parts = piece.strip().split()
        if len(parts) >= 2:
            try:
                pts.append((float(parts[0]), float(parts[1])))
            except ValueError:
                return None
    return pts or None


def _edge_segments(graph: nx.Graph) -> tuple[list, list]:
    """Return (arterial_segments, other_segments) as lists of (lon, lat) polylines."""
    arterial: list[list[tuple[float, float]]] = []
    other: list[list[tuple[float, float]]] = []
    for u, v, data in graph.edges(data=True):
        hwy_raw = data.get("highway", "")
        # OSMnx stores some tag values as Python-literal lists (e.g. "['primary','primary_link']").
        hwy_tokens: list[str] = []
        if isinstance(hwy_raw, str):
            stripped = hwy_raw.strip()
            if stripped.startswith("["):
                hwy_tokens = re.findall(r"'([^']+)'|\"([^\"]+)\"", stripped)
                hwy_tokens = [a or b for a, b in hwy_tokens]
            else:
                hwy_tokens = [stripped]
        elif isinstance(hwy_raw, (list, tuple)):
            hwy_tokens = [str(t) for t in hwy_raw]
        is_arterial = any(t in ROUTEABLE_HIGHWAY_CLASSES for t in hwy_tokens)

        geom = data.get("geometry")
        line = _parse_linestring(geom) if isinstance(geom, str) else None
        if line is None:
            ux = graph.nodes[u].get("x")
            uy = graph.nodes[u].get("y")
            vx = graph.nodes[v].get("x")
            vy = graph.nodes[v].get("y")
            if None in (ux, uy, vx, vy):
                continue
            line = [(float(ux), float(uy)), (float(vx), float(vy))]
        (arterial if is_arterial else other).append(line)
    return arterial, other


def _add_scale_bar(ax: plt.Axes, bbox: dict, lat_mid: float) -> None:
    """Draw a physical-distance scale bar in km in the lower-left."""
    import math

    width_deg_lon = bbox["east"] - bbox["west"]
    km_per_deg_lon = KM_PER_DEG_LAT * math.cos(math.radians(lat_mid))
    width_km = width_deg_lon * km_per_deg_lon
    # Pick a "nice" length about 1/5 of the width.
    target = width_km / 5.0
    nice_steps = [1, 2, 5, 10, 20, 25, 50]
    bar_km = min(nice_steps, key=lambda v: abs(v - target))
    bar_deg = bar_km / km_per_deg_lon

    x0 = bbox["west"] + 0.04 * width_deg_lon
    y0 = bbox["south"] + 0.04 * (bbox["north"] - bbox["south"])
    bar_h = 0.006 * (bbox["north"] - bbox["south"])

    ax.add_patch(
        Rectangle(
            (x0, y0),
            bar_deg,
            bar_h,
            facecolor="black",
            edgecolor="black",
            zorder=10,
        )
    )
    ax.add_patch(
        Rectangle(
            (x0 + bar_deg, y0),
            bar_deg,
            bar_h,
            facecolor="white",
            edgecolor="black",
            zorder=10,
        )
    )
    ax.text(
        x0,
        y0 + bar_h * 2.0,
        "0",
        ha="center",
        va="bottom",
        fontsize=8,
        zorder=10,
    )
    ax.text(
        x0 + bar_deg,
        y0 + bar_h * 2.0,
        f"{bar_km:g}",
        ha="center",
        va="bottom",
        fontsize=8,
        zorder=10,
    )
    ax.text(
        x0 + 2 * bar_deg,
        y0 + bar_h * 2.0,
        f"{2 * bar_km:g} km",
        ha="center",
        va="bottom",
        fontsize=8,
        zorder=10,
    )


def _add_north_arrow(ax: plt.Axes, bbox: dict) -> None:
    width = bbox["east"] - bbox["west"]
    height = bbox["north"] - bbox["south"]
    # Upper-left, just inside the bbox border.
    x = bbox["west"] + 0.05 * width
    y0 = bbox["north"] - 0.16 * height
    y1 = bbox["north"] - 0.06 * height
    ax.add_patch(
        FancyArrowPatch(
            (x, y0),
            (x, y1),
            arrowstyle="-|>",
            mutation_scale=18,
            color="black",
            linewidth=1.6,
            zorder=10,
        )
    )
    ax.text(
        x,
        y1 + 0.01 * height,
        "N",
        ha="center",
        va="bottom",
        fontsize=11,
        fontweight="bold",
        zorder=10,
    )


def main() -> int:
    font_used = _configure_korean_font()
    print(f"Using font: {font_used}")

    with REGION_YAML.open(encoding="utf-8") as fh:
        region = yaml.safe_load(fh)
    bbox = region["boundary"]
    with ORIGINS_JSON.open(encoding="utf-8") as fh:
        origins_data = json.load(fh)

    print(f"Reading graph: {GRAPHML}")
    graph = nx.read_graphml(GRAPHML)
    n_nodes = graph.number_of_nodes()
    n_edges = graph.number_of_edges()
    print(f"  nodes={n_nodes}, edges={n_edges}")

    arterial, other = _edge_segments(graph)
    print(f"  arterial edges (after highway filter)={len(arterial)}, other={len(other)}")

    # ------------- figure -------------
    fig, ax = plt.subplots(figsize=(9.0, 9.0))

    # Minor roads first (pale), then arterials on top.
    if other:
        ax.add_collection(
            LineCollection(
                other,
                colors="#d8d8d8",
                linewidths=0.25,
                zorder=1,
            )
        )
    if arterial:
        ax.add_collection(
            LineCollection(
                arterial,
                colors="#7a7a7a",
                linewidths=0.7,
                zorder=2,
            )
        )

    # bbox rectangle
    ax.add_patch(
        Rectangle(
            (bbox["west"], bbox["south"]),
            bbox["east"] - bbox["west"],
            bbox["north"] - bbox["south"],
            fill=False,
            edgecolor="#444444",
            linestyle=":",
            linewidth=0.8,
            zorder=3,
        )
    )

    # Origins A/B/C/D — distinct markers
    origin_markers = {
        "A": ("o", "#d62728"),
        "B": ("s", "#1f77b4"),
        "C": ("^", "#2ca02c"),
        "D": ("D", "#9467bd"),
    }
    # Origin label placement. The four origins cluster tightly in Songpa
    # (lon 127.07-127.13, lat 37.48-37.52). Stack labels vertically along
    # the lower edge so they don't overlap each other, the rail nodes, or
    # the legend.
    # Coords reminder: A=(127.1057, 37.5147), B=(127.0857, 37.5036),
    # C=(127.1262, 37.4784), D=(127.0727, 37.5159).
    label_offsets = {
        "A": (0.035, 0.014),    # upper-right of A — clear of D and S
        "B": (0.020, -0.020),   # below-right of B — clear of S below A
        "C": (-0.018, -0.012),  # below-left of C
        "D": (-0.045, 0.012),   # upper-left of D
    }
    label_ha = {"A": "left", "B": "left", "C": "right", "D": "right"}
    legend_handles: list[Line2D] = []
    for o in origins_data["origins"]:
        oid = o["id"]
        marker, color = origin_markers[oid]
        unverified = o.get("verification", "").startswith("unverified")
        edge = "black" if not unverified else "#555555"
        ax.scatter(
            o["lon"],
            o["lat"],
            marker=marker,
            s=120,
            c=color,
            edgecolors=edge,
            linewidths=1.4,
            zorder=6,
            hatch="///" if unverified else None,
        )
        dx, dy = label_offsets[oid]
        suffix = " *미검증" if unverified else ""
        ax.annotate(
            f"{oid}: {o['name']}{suffix}",
            xy=(o["lon"], o["lat"]),
            xytext=(o["lon"] + dx, o["lat"] + dy),
            fontsize=8.5,
            fontweight="bold",
            color="black",
            ha=label_ha[oid],
            va="center",
            arrowprops=dict(arrowstyle="-", color=color, lw=0.7),
            bbox=dict(
                facecolor="white",
                edgecolor=color,
                boxstyle="round,pad=0.2",
                alpha=0.92,
            ),
            zorder=7,
        )
        legend_handles.append(
            Line2D(
                [0],
                [0],
                marker=marker,
                color="none",
                markerfacecolor=color,
                markeredgecolor=edge,
                markersize=10,
                label=f"기점 {oid} ({o['name']})" + (" — 미검증" if unverified else ""),
                linestyle="None",
            )
        )

    # Destination T — canonical D node from YAML
    dest = region["destination_zones"][0]
    ax.scatter(
        dest["lon"],
        dest["lat"],
        marker="*",
        s=380,
        c="#ff7f0e",
        edgecolors="black",
        linewidths=1.4,
        zorder=8,
    )
    ax.annotate(
        f"T: {dest['name']}",
        xy=(dest["lon"], dest["lat"]),
        xytext=(dest["lon"] - 0.005, dest["lat"] - 0.012),
        fontsize=10,
        fontweight="bold",
        ha="right",
        bbox=dict(
            facecolor="white",
            edgecolor="#ff7f0e",
            boxstyle="round,pad=0.2",
            alpha=0.95,
        ),
        zorder=9,
    )
    legend_handles.append(
        Line2D(
            [0],
            [0],
            marker="*",
            color="none",
            markerfacecolor="#ff7f0e",
            markeredgecolor="black",
            markersize=15,
            label=f"종점 T ({dest['name']})",
            linestyle="None",
        )
    )

    # Rail nodes S and R
    rail_access = region["rail"]["access"]
    rail_egress = region["rail"]["egress"]
    # S (잠실역, lat 37.5133 lon 127.1002) sits right under D and between
    # A (upper-right label) and B (right label). Place S label down-left
    # so it tucks between D and B vertically without colliding with either.
    # R (의정부역, lat 37.738 lon 127.0455) is at the top — place label
    # below-left to clear both the upper-left north arrow and the legend.
    rail_label_specs = (
        (rail_access, "S", "잠실역", (0.005, -0.018), "left"),
        (rail_egress, "R", "의정부역", (-0.012, -0.012), "right"),
    )
    for node, sid, short, offset, ha in rail_label_specs:
        ax.scatter(
            node["lon"],
            node["lat"],
            marker="P",
            s=160,
            c="#17becf",
            edgecolors="black",
            linewidths=1.3,
            zorder=6,
        )
        ax.annotate(
            f"{sid}: {short}",
            xy=(node["lon"], node["lat"]),
            xytext=(node["lon"] + offset[0], node["lat"] + offset[1]),
            fontsize=8.5,
            fontweight="bold",
            color="black",
            ha=ha,
            va="center",
            arrowprops=dict(arrowstyle="-", color="#17becf", lw=0.7),
            bbox=dict(
                facecolor="white",
                edgecolor="#17becf",
                boxstyle="round,pad=0.2",
                alpha=0.92,
            ),
            zorder=7,
        )
    legend_handles.append(
        Line2D(
            [0],
            [0],
            marker="P",
            color="none",
            markerfacecolor="#17becf",
            markeredgecolor="black",
            markersize=11,
            label="철도 접근/이탈 (S: 잠실역, R: 의정부역)",
            linestyle="None",
        )
    )
    # Edge styles for legend
    legend_handles.append(
        Line2D(
            [0],
            [0],
            color="#7a7a7a",
            linewidth=1.5,
            label="간선도로 (motorway/trunk/primary/secondary, ±_link)",
        )
    )
    legend_handles.append(
        Line2D(
            [0],
            [0],
            color="#d8d8d8",
            linewidth=1.5,
            label="기타 도로 (보조 가시화용)",
        )
    )

    # Axes setup — fix to bbox.
    ax.set_xlim(bbox["west"], bbox["east"])
    ax.set_ylim(bbox["south"], bbox["north"])
    lat_mid = 0.5 * (bbox["north"] + bbox["south"])
    # Use cos(lat) aspect so the bbox isn't visually distorted.
    import math
    ax.set_aspect(1.0 / math.cos(math.radians(lat_mid)))

    ax.set_xlabel("경도 (°E)", fontsize=11)
    ax.set_ylabel("위도 (°N)", fontsize=11)
    ax.set_title(
        "그림 2. 송파-부곡리 예비군 동원 회랑 (가상 간선도로 회랑) — "
        f"OSM 기반 캐시 그래프 (노드 {n_nodes:,}, 엣지 {n_edges:,})",
        fontsize=11.5,
        pad=10,
    )
    ax.grid(True, linestyle=":", linewidth=0.4, color="#bbbbbb", alpha=0.7)

    _add_scale_bar(ax, bbox, lat_mid)
    _add_north_arrow(ax, bbox)

    # Legend in upper-right where the bbox is mostly empty (the corridor
    # runs SW->N, so the NE corner above 의정부 has space).
    leg = ax.legend(
        handles=legend_handles,
        loc="upper right",
        fontsize=8.5,
        framealpha=0.92,
        title="범례",
        title_fontsize=9.5,
    )
    leg.set_zorder(20)

    # bbox annotation (compact two-line label). The middle-left strip
    # (around lon 126.86-126.94, lat 37.55-37.65) is empty road network
    # between the T destination (upper-left) and the Songpa cluster
    # (lower-right), so place the annotation there.
    bbox_text = (
        f"BBox\nN={bbox['north']:.2f}  S={bbox['south']:.2f}\n"
        f"E={bbox['east']:.2f}  W={bbox['west']:.2f}"
    )
    at = AnchoredText(
        bbox_text,
        loc="center left",
        prop=dict(size=8.0),
        frameon=True,
        pad=0.3,
        borderpad=0.5,
    )
    at.patch.set_alpha(0.88)
    at.patch.set_edgecolor("#444")
    ax.add_artist(at)

    fig.tight_layout()
    OUTPUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PNG, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {OUTPUT_PNG}")

    # ------------- caption -------------
    caption = (
        "**그림 2.** 송파-부곡리 예비군 동원 회랑(가상 간선도로 회랑)의 지리적 구성. "
        f"OSM 기반 캐시 그래프(노드 {n_nodes:,}개, 엣지 {n_edges:,}개)에서 "
        "간선도로(motorway·trunk·primary·secondary 및 _link)만 강조하여 표시하고, "
        "송파 측 4개 후보 기점 A(송파구청 일자리센터)·B(삼전동 구민회관)·C(장지역 4번 출구)·"
        "D(잠실종합운동장, 미검증 변형)과 캐노니컬 종점 T(72사단 부곡리 동원훈련장, ≈37.74°N 126.95°E), "
        "그리고 철도 접근/이탈 노드 S(잠실역)·R(의정부역, ≈37.738°N 127.046°E)를 함께 표시하였다."
    )
    CAPTION_MD.write_text(caption + "\n", encoding="utf-8")
    print(f"Wrote {CAPTION_MD}")

    # ------------- console report -------------
    file_size = OUTPUT_PNG.stat().st_size
    print(f"PNG size: {file_size:,} bytes ({file_size / 1024:.1f} KiB)")
    print(
        f"Plot bbox (lon×lat): "
        f"[{bbox['west']}, {bbox['east']}] × [{bbox['south']}, {bbox['north']}]"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
