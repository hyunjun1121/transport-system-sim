# -*- coding: utf-8 -*-
"""Render KIIE paper figures from hash-verified revision analysis.

Reads:
  results/paper_revision_top10_corridor_v4_20260721/analysis/full/* (figures 3--6)
  paper/figures/_build/map_geo.json       (graphml road geometry + 행정경계 coastline
                                           + 철도중심선 rail; see build_geo_layers.py)
  results/bpr_noop_sweep.csv              (BPR sweep)

Outputs (filenames aligned to paper 그림 numbering):
  fig1_framework.png            그림 1  vector fallback, explicit opt-in only
  fig2_corridor_map.png         그림 2  corridor map, pinned nodes, two alternatives
  fig3_bpr_noop.png             그림 3  graph-scope structural and ranking stability
  fig4_segment_decomposition.png 그림 4  paired completion and makespan intervals
  fig5_rail_substitution.png    그림 5  break-even curve and road-rail decision map
  fig6_assumption_collapse.png  그림 6  demand-fleet and adaptive-policy results

Claim discipline: figures 3--6 load only a complete, hash-matched full analysis.
Coordinate policy: public administrative centroids / public rail stations only.
"""
import argparse
import sys, os, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib import patheffects as PE
from matplotlib.patches import FancyBboxPatch, Rectangle, Patch
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
from matplotlib.collections import LineCollection
import numpy as np

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
from revision_figure_data import load_revision_figure_data

FONT = r"C:\Windows\Fonts\malgun.ttf"
fm.fontManager.addfont(FONT)
plt.rcParams["font.family"] = fm.FontProperties(fname=FONT).get_name()
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["pdf.fonttype"] = 42

OUT = "paper/figures"
BUILD = "paper/figures/_build"
DEFAULT_ANALYSIS_DIR = Path(
    "results/paper_revision_top10_corridor_v4_20260721/analysis/full"
)
FORBIDDEN_FIGURE_WORDS = ("운용", "예측", "보정", "검증", "최적경로", "실측")

# unified palette
BUS_C = "#2c6fbb"     # 버스 단독
MULTI_C = "#d1495b"   # 복합운송
RAIL_C = "#2e7d32"    # 전세 철도
OK_C = "#cfe8d0"; OK_EDGE = "#2e7d32"
BAD_C = "#f6c9c9"; BAD_EDGE = "#b23a3a"
INK = "#222222"; MUTED = "#888888"
# 그림 3-5: 그리드선·기준선 위에 놓이는 소형 텍스트의 흰 스트로크 할로
HALO_FX = [PE.withStroke(linewidth=2.4, foreground="white")]


def save(fig, name, *, output_dir=OUT):
    path = Path(output_dir) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", path, os.path.getsize(path), "bytes")
    return path


def data_box_to_axes_fraction(ax, x0, y0, x1, y1):
    """DATA box -> axes-fraction [x0, y0, w, h] via the robust transform chain
    (data -> display -> axes). Correct way to place an inset at exact data coords."""
    disp = ax.transData.transform([(x0, y0), (x1, y1)])
    frac = ax.transAxes.inverted().transform(disp)
    (fx0, fy0), (fx1, fy1) = frac
    return [fx0, fy0, fx1 - fx0, fy1 - fy0]


def axes_fraction_to_data_box(ax, arg):
    """axes-fraction [x0, y0, w, h] -> DATA box (xmin, xmax, ymin, ymax). Inverse of above.
    NB: ax.transLimits encodes the OPPOSITE direction and must not be used for this."""
    disp = ax.transAxes.transform([(arg[0], arg[1]), (arg[0] + arg[2], arg[1] + arg[3])])
    d = ax.transData.inverted().transform(disp)
    (dx0, dy0), (dx1, dy1) = d
    return (min(dx0, dx1), max(dx0, dx1), min(dy0, dy1), max(dy0, dy1))


def segments_cross(p1, p2, p3, p4):
    """True if line segment p1-p2 properly crosses segment p3-p4 (2D orientation test)."""
    def _ccw(a, b, c):
        return (c[1] - a[1]) * (b[0] - a[0]) - (b[1] - a[1]) * (c[0] - a[0])
    d1, d2 = _ccw(p3, p4, p1), _ccw(p3, p4, p2)
    d3, d4 = _ccw(p1, p2, p3), _ccw(p1, p2, p4)
    return (((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0))
            and ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)))


def _acad(ax, grid_axis="y"):
    """그림 3-5 공용 축 스타일: open frame, 얇은 그리드, 작은 눈금."""
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#9a9a9a"); ax.spines[s].set_linewidth(0.8)
    ax.tick_params(colors="#555555", labelsize=9, length=3, width=0.8)
    if grid_axis:
        ax.grid(axis=grid_axis, color="#e4e4e4", lw=0.7)
        ax.set_axisbelow(True)


def _texts_clear(fig, tag):
    """그림 3-5 가드: 표시 텍스트 전쌍의 렌더러 bbox 교차(>1px^2)를 빌드 실패로 처리.
    Annotation은 화살표 합집합이 아닌 텍스트 상자만 측정한다."""
    from matplotlib.text import Text as _T
    fig.canvas.draw()
    rnd = fig.canvas.get_renderer()
    ts = [t for t in fig.findobj(_T) if t.get_visible() and t.get_text().strip()]
    bbs = [_T.get_window_extent(t, renderer=rnd) for t in ts]
    bad = []
    for i in range(len(ts)):
        for j in range(i + 1, len(ts)):
            w = min(bbs[i].x1, bbs[j].x1) - max(bbs[i].x0, bbs[j].x0)
            h = min(bbs[i].y1, bbs[j].y1) - max(bbs[i].y0, bbs[j].y0)
            if w > 0 and h > 0 and w * h > 1.0:
                bad.append(f"'{ts[i].get_text()[:14]}' x '{ts[j].get_text()[:14]}' = {w*h:.0f}px^2")
    assert not bad, f"{tag} text overlaps: " + " | ".join(bad)
    print(f"{tag} text-overlap guard: pass ({len(ts)} texts)")


def _assert_figure_text(fig, tag):
    """Reject reserved claim terms before any paper figure is written."""
    from matplotlib.text import Text as _T

    rendered = [t.get_text() for t in fig.findobj(_T) if t.get_visible()]
    violations = sorted(
        {word for word in FORBIDDEN_FIGURE_WORDS for text in rendered if word in text}
    )
    assert not violations, f"{tag} forbidden rendered words: {', '.join(violations)}"


# ============================================================ 그림 1 framework
def fig1_framework(*, output_dir=OUT):
    """픽토그램형 1x7 파이프라인. 층 상세 정의는 표 2와 캡션이 담당한다."""
    from matplotlib.patches import Circle, Polygon
    from matplotlib.transforms import Bbox

    fig, ax = plt.subplots(figsize=(10.4, 3.9))
    ax.set_xlim(0, 14); ax.set_ylim(0, 5.10); ax.axis("off")
    stages = [
        ("1", "Region\ninput", "B"),
        ("2", "Network\nprep", "B"),
        ("3", "Threat", "C"),
        ("4", "Policy", "C"),
        ("5", "Micro-\nsimulation", "B"),
        ("6", "Evaluation", "C"),
        ("7", "Evidence\ncheck", "A"),
    ]
    lcolor = {"A": "#c8742f", "B": BUS_C, "C": RAIL_C}
    fb = "#b23a3a"
    bw, gap, x0, y0, bh = 1.66, 0.3167, 0.24, 1.32, 1.70
    top = y0 + bh
    centers, boxes, number_texts, name_texts = [], [], [], []
    for i, (n, name, lay) in enumerate(stages):
        x = x0 + i * (bw + gap)
        ax.add_patch(FancyBboxPatch((x, y0), bw, bh,
                                    boxstyle="round,pad=0.02,rounding_size=0.06",
                                    fc="white", ec=lcolor[lay], lw=1.25))
        number_texts.append(ax.text(x + 0.13, top - 0.13, n, fontsize=8.2,
                                    fontweight="bold", color=lcolor[lay],
                                    ha="center", va="center"))
        name_texts.append(ax.text(x + bw / 2, y0 + 0.30, name, fontsize=8.6, color=INK,
                                  ha="center", va="center", linespacing=1.18))
        centers.append(x + bw / 2)
        boxes.append((x - 0.02, x + bw + 0.02, y0 - 0.02, top + 0.02))  # boxstyle pad=0.02 포함

    # 픽토그램 로컬 좌표: 각 박스 안의 상부 영역만 사용한다.
    icon_artists = [[] for _ in stages]
    icon_x0, icon_x1 = 0.18, bw - 0.16
    icon_y0, icon_y1 = 0.64, bh - 0.18

    def pt(i, u, v):
        x = x0 + i * (bw + gap)
        return (x + icon_x0 + u * (icon_x1 - icon_x0),
                y0 + icon_y0 + v * (icon_y1 - icon_y0))

    def line(i, uv, **kwargs):
        xy = [pt(i, u, v) for u, v in uv]
        art, = ax.plot([p[0] for p in xy], [p[1] for p in xy], **kwargs)
        icon_artists[i].append(art)
        return art

    def patch(i, art):
        ax.add_patch(art)
        icon_artists[i].append(art)
        return art

    def circle(i, u, v, r, **kwargs):
        cx, cy = pt(i, u, v)
        sx = (icon_x1 - icon_x0) * r
        sy = (icon_y1 - icon_y0) * r
        return patch(i, Circle((cx, cy), min(sx, sy), **kwargs))

    def polygon(i, uv, **kwargs):
        return patch(i, Polygon([pt(i, u, v) for u, v in uv], closed=True, **kwargs))

    grey, dark = "#9a9a9a", "#555555"

    # 1 권역 입력: 실지리와 무관한 불규칙 개념 윤곽 + 출발/도착 표식.
    region = [(0.10, 0.28), (0.18, 0.72), (0.42, 0.88), (0.70, 0.80),
              (0.91, 0.57), (0.82, 0.22), (0.55, 0.12), (0.30, 0.18)]
    polygon(0, region, fc="#f4f4f4", ec=grey, lw=1.1)
    line(0, [(0.29, 0.37), (0.70, 0.63)], color=grey, lw=1.0)
    circle(0, 0.29, 0.37, 0.055, fc="white", ec=BUS_C, lw=1.3)
    polygon(0, [(0.70, 0.71), (0.63, 0.56), (0.77, 0.56)],
            fc="white", ec=MULTI_C, lw=1.3)

    # 2 망 준비: 표준노드링크를 뜻하는 소형 노드-링크 그래프.
    nodes2 = [(0.12, 0.25), (0.25, 0.73), (0.48, 0.46),
              (0.66, 0.82), (0.83, 0.55), (0.91, 0.18)]
    edges2 = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (2, 4), (3, 4), (4, 5)]
    for a, b in edges2:
        line(1, [nodes2[a], nodes2[b]], color=grey, lw=1.05)
    for u, v in nodes2:
        circle(1, u, v, 0.035, fc=dark, ec=dark, lw=0.8)

    # 3 위협: 같은 망의 한 간선이 절단된 상태와 절단부 강조 2획.
    nodes3 = nodes2
    edges3 = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 4), (3, 4), (4, 5)]
    for a, b in edges3:
        line(2, [nodes3[a], nodes3[b]], color=grey, lw=1.05)
    line(2, [(0.48, 0.46), (0.548, 0.595)], color=grey, lw=1.05)
    line(2, [(0.586, 0.676), (0.66, 0.82)], color=grey, lw=1.05)
    line(2, [(0.535, 0.625), (0.566, 0.603)], color=MULTI_C, lw=1.4)
    line(2, [(0.570, 0.690), (0.601, 0.668)], color=MULTI_C, lw=1.4)
    for u, v in nodes3:
        circle(2, u, v, 0.035, fc=dark, ec=dark, lw=0.8)

    # 4 정책: 버스 단독과 버스-철도 복합운송을 동등하게 병렬 제시.
    line(3, [(0.12, 0.72), (0.88, 0.72)], color=BUS_C, lw=1.4,
         solid_capstyle="round")
    circle(3, 0.12, 0.72, 0.032, fc="white", ec=BUS_C, lw=1.1)
    polygon(3, [(0.88, 0.78), (0.88, 0.66), (0.95, 0.72)],
            fc=BUS_C, ec=BUS_C, lw=0.8)
    line(3, [(0.12, 0.28), (0.34, 0.28)], color=MULTI_C, lw=1.4,
         solid_capstyle="round")
    line(3, [(0.34, 0.28), (0.72, 0.28)], color=RAIL_C, lw=1.4,
         ls=(0, (3.0, 1.8)), dash_capstyle="round")
    line(3, [(0.72, 0.28), (0.88, 0.28)], color=MULTI_C, lw=1.4,
         solid_capstyle="round")
    circle(3, 0.12, 0.28, 0.032, fc="white", ec=MULTI_C, lw=1.1)
    circle(3, 0.34, 0.28, 0.024, fc="white", ec=dark, lw=0.9)
    circle(3, 0.72, 0.28, 0.024, fc="white", ec=dark, lw=0.9)
    polygon(3, [(0.88, 0.34), (0.88, 0.22), (0.95, 0.28)],
            fc=MULTI_C, ec=MULTI_C, lw=0.8)

    # 5 미세-시뮬레이션: 시계 + 이산 위치의 차량이 놓인 시간축.
    circle(4, 0.50, 0.68, 0.18, fc="white", ec=dark, lw=1.2)
    line(4, [(0.50, 0.68), (0.50, 0.81)], color=dark, lw=1.15,
         solid_capstyle="round")
    line(4, [(0.50, 0.68), (0.61, 0.61)], color=dark, lw=1.15,
         solid_capstyle="round")
    line(4, [(0.10, 0.20), (0.91, 0.20)], color=grey, lw=1.0)
    for u in (0.18, 0.46, 0.76):
        x, y = pt(4, u, 0.20)
        w, h = (icon_x1 - icon_x0) * 0.13, (icon_y1 - icon_y0) * 0.13
        patch(4, Rectangle((x - w / 2, y - h * 0.15), w, h,
                           fc=BUS_C, ec=BUS_C, lw=0.8))

    # 6 평가: 두 대안의 막대와 공통 기준선.
    line(5, [(0.14, 0.15), (0.91, 0.15)], color=dark, lw=1.0)
    line(5, [(0.14, 0.15), (0.14, 0.88)], color=dark, lw=1.0)
    for u, height, color in ((0.38, 0.43, BUS_C), (0.69, 0.70, MULTI_C)):
        x, y = pt(5, u, 0.15)
        w = (icon_x1 - icon_x0) * 0.19
        h = (icon_y1 - icon_y0) * height
        patch(5, Rectangle((x - w / 2, y), w, h, fc=color, ec=color, lw=0.8))
    line(5, [(0.14, 0.61), (0.91, 0.61)], color=grey, lw=1.0, ls=(0, (2.4, 2.0)))

    # 7 증거-점검·민감도: 기준선 양쪽 민감도 밴드 + 돋보기.
    line(6, [(0.50, 0.16), (0.50, 0.86)], color=dark, lw=1.0)
    for lo, hi, v, color in ((0.16, 0.79, 0.38, "#c8742f"),
                             (0.30, 0.68, 0.64, grey)):
        xlo, y = pt(6, lo, v)
        xhi, _ = pt(6, hi, v)
        h = (icon_y1 - icon_y0) * 0.10
        patch(6, Rectangle((xlo, y - h / 2), xhi - xlo, h,
                           fc=color, ec=color, lw=0.8, alpha=0.92))
    circle(6, 0.69, 0.70, 0.13, fc="white", ec=dark, lw=1.25)
    line(6, [(0.78, 0.61), (0.91, 0.46)], color=dark, lw=1.4,
         solid_capstyle="round")

    # forward arrows
    for i in range(len(stages) - 1):
        ax.annotate("", xy=(centers[i + 1] - bw / 2 - 0.05, y0 + bh / 2),
                    xytext=(centers[i] + bw / 2 + 0.05, y0 + bh / 2),
                    arrowprops=dict(arrowstyle="-|>", color="#999999", lw=1.1))
    # 환류: 7 상단 -> 박스 위 수평 레일 -> 3·4 상단 하강 진입 (직교 배선, 박스 관통 없는 경로)
    rail_y, dash = 4.08, (0, (3.6, 2.2))
    x3c, x4c, x7c = centers[2], centers[3], centers[6]
    ax.plot([x7c, x7c, x3c], [top + 0.03, rail_y, rail_y],
            color=fb, lw=1.05, ls=dash, solid_capstyle="butt", zorder=2)
    drops = [((x3c, rail_y), (x3c, top + 0.05)), ((x4c, rail_y), (x4c, top + 0.05))]
    for p_from, p_to in drops:
        ax.annotate("", xy=p_to, xytext=p_from,
                    arrowprops=dict(arrowstyle="-|>", color=fb, lw=1.05,
                                    ls=dash, shrinkA=0, shrinkB=0))
    ax.text((x3c + x7c) / 2, rail_y + 0.18, "Feedback: evidence checks return to threat and policy inputs",
            fontsize=8, color=fb, ha="center", va="bottom", path_effects=HALO_FX)
    # layer key (상세 정의는 표 2·캡션으로 위임)
    handles = [Patch(fc="white", ec=lcolor[k], lw=1.2, label=lb)
               for k, lb in (("A", "A: assumption handling"), ("B", "B: empirical data core"),
                              ("C", "C: comparison stage"))]
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.025),
              ncol=3, fontsize=8.2, frameon=False,
              handlelength=1.35, handleheight=0.85, columnspacing=1.7)
    # 가드: 환류 배선 세그먼트는 어떤 단계 박스 모서리와도 교차하지 않는다
    # (구판의 '환류 호가 박스 5·6 관통' 회귀 방지; 직교 배선이라 세그먼트 검사로 충분)
    fb_segs = [((x7c, top + 0.03), (x7c, rail_y)), ((x7c, rail_y), (x3c, rail_y))] + drops
    hits = []
    for p1, p2 in fb_segs:
        for bi, (bx0, bx1, by0, by1) in enumerate(boxes):
            for e1, e2 in (((bx0, by0), (bx1, by0)), ((bx1, by0), (bx1, by1)),
                           ((bx1, by1), (bx0, by1)), ((bx0, by1), (bx0, by0))):
                if segments_cross(p1, p2, e1, e2):
                    hits.append(f"feedback x box{bi + 1}")
    assert not hits, "fig1 feedback wiring crosses stage boxes: " + " | ".join(sorted(set(hits)))
    print(f"fig1 feedback-wiring guard: pass ({len(fb_segs)} segs vs {len(boxes)} boxes)")

    # 가드: 각 픽토그램 아티스트 bbox는 자기 박스 안에 있고 번호·단계명과 겹치지 않는다.
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()

    def overlap_area(a, b):
        w = min(a.x1, b.x1) - max(a.x0, b.x0)
        h = min(a.y1, b.y1) - max(a.y0, b.y0)
        return max(0.0, w) * max(0.0, h)

    icon_fails = []
    for i, arts in enumerate(icon_artists):
        bx0, bx1, by0, by1 = boxes[i]
        p0, p1 = ax.transData.transform([(bx0, by0), (bx1, by1)])
        outer = Bbox.from_extents(p0[0], p0[1], p1[0], p1[1])
        text_boxes = [number_texts[i].get_window_extent(renderer=renderer),
                      name_texts[i].get_window_extent(renderer=renderer)]
        for j, art in enumerate(arts):
            bb = art.get_window_extent(renderer=renderer)
            if not (bb.x0 >= outer.x0 and bb.x1 <= outer.x1
                    and bb.y0 >= outer.y0 and bb.y1 <= outer.y1):
                icon_fails.append(f"box{i + 1} pictogram{j + 1} leaves frame")
            for k, tb in enumerate(text_boxes):
                if overlap_area(bb, tb) > 1.0:
                    icon_fails.append(f"box{i + 1} pictogram{j + 1} x text{k + 1}")
    assert not icon_fails, "fig1 pictogram bbox guard failed: " + " | ".join(icon_fails)
    print(f"fig1 pictogram-bbox guard: pass ({sum(map(len, icon_artists))} artists)")

    forbidden = ("운용", "예측", "보정", "검증", "최적경로", "실측")
    rendered = [t.get_text() for t in fig.findobj(matplotlib.text.Text) if t.get_text()]
    bad_words = sorted({word for word in forbidden for value in rendered if word in value})
    assert not bad_words, "fig1 forbidden rendered text: " + ", ".join(bad_words)
    _texts_clear(fig, "fig1")
    save(fig, "fig1_framework.png", output_dir=output_dir)


# ============================================================ 그림 2 corridor map
def fig2_map(*, output_dir=OUT):
    geo = json.load(open(f"{BUILD}/map_geo.json", encoding="utf-8"))
    nodes = geo["nodes"]
    # Extent notes: LAT0=37.10 opens an empty south band clear of the real rail dip
    # (원주 부근 lat 37.342) so the legend occludes nothing; LAT1=38.38 matches the
    # admin-boundary dataset coverage cap (coast data tops out at 38.376 near the CCL).
    LON0, LON1, LAT0, LAT1 = 126.80, 129.62, 37.10, 38.38
    fig, ax = plt.subplots(figsize=(9.0, 6.8))

    # real east coast from 행정경계(시도) 강원 polygon (south→north; see build_geo_layers.py)
    coast = [tuple(p) for p in geo["coastline"]]
    sea_x = [c[0] for c in coast] + [LON1, LON1]
    sea_y = [c[1] for c in coast] + [LAT1, LAT0]
    ax.fill(sea_x, sea_y, color="#eaf2fb", zorder=0)
    ax.plot([c[0] for c in coast], [c[1] for c in coast], color="#9dbbd6", lw=1.0, zorder=1)

    # expressway skeleton
    segs = [[(s[0][0], s[0][1]), (s[1][0], s[1][1])] for s in geo["motorway_skeleton"]]
    ax.add_collection(LineCollection(segs, colors="#d9dade", linewidths=0.5, zorder=2))

    # routes
    R = geo["routes"]
    # bus_only trunk A->D
    ax.plot([p[0] for p in R["road_A_D"]], [p[1] for p in R["road_A_D"]],
            color=BUS_C, lw=2.4, zorder=5, solid_capstyle="round")
    # multimodal road legs A->S, R->D
    for k in ("road_A_S", "road_R_D"):
        ax.plot([p[0] for p in R[k]], [p[1] for p in R[k]],
                color=MULTI_C, lw=2.4, zorder=5, solid_capstyle="round")
    # real rail centerline S->R from 철도중심선 (연속수치지형도; tunnel stretches are
    # straight joins — the legend keeps calling it 개념선, which stays conservative)
    rail = [tuple(p) for p in geo["rail_centerline"]]
    ax.plot([p[0] for p in rail], [p[1] for p in rail],
            color=RAIL_C, lw=2.6, ls=(0, (5, 3)), zorder=6, dash_capstyle="round")

    # node pins
    mk = {"A": ("o", BUS_C), "S": ("s", RAIL_C), "R": ("s", RAIL_C), "D": ("^", "#b23a3a")}
    _letters = []
    for k, nd in nodes.items():
        m, c = mk[k]
        ax.plot(nd["lon"], nd["lat"], marker=m, ms=11, mfc=c,
                mec="white", mew=1.6, zorder=8)
        _letters.append(ax.text(nd["lon"], nd["lat"], k, fontsize=8.6, fontweight="bold",
                                color="white", ha="center", va="center", zorder=9))

    # main-map node labels: white halo + offsets into zones that the renderer-based
    # guards below prove empty. With the real rail centerline the 한강 valley band
    # (lat 37.51-37.62, lon 127.0-127.5) is fully occupied, so the A label moves to the
    # empty area south of the rail and points at its pin with a thin leader.
    _HALO = dict(fontsize=9.3, color=INK, zorder=9,
                 bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.85))
    _lab_A = ax.annotate("A Songpa", xy=(nodes["A"]["lon"], nodes["A"]["lat"]),
                         xytext=(127.235, 37.458), ha="left", va="center",
                         arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6,
                                         shrinkA=4, shrinkB=8), **_HALO)
    _lab_S = ax.text(126.835, 37.695, "S Cheongnyangni Stn", ha="left", va="center", **_HALO)
    # R pin is coastal: keep the label east of the pin in open sea (same slot as the
    # original long Korean label, which cleared both coast and rail).
    _lab_R = ax.text(129.115, 37.695, "R Gangneung Stn", ha="left", va="center", **_HALO)
    # D pin is at the top-right; label left of the marker, below the pin letter.
    _lab_D = ax.annotate("D Goseong", xy=(nodes["D"]["lon"], nodes["D"]["lat"]),
                         xytext=(128.400, 38.270), ha="right", va="center",
                         arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6,
                                         shrinkA=4, shrinkB=8), **_HALO)

    # dashed rectangle on the main map marking the Seoul A-S region the inset zooms.
    SRC_X0, SRC_Y0, SRC_W, SRC_H = 126.985, 37.490, 0.210, 0.140
    ax.add_patch(Rectangle((SRC_X0, SRC_Y0), SRC_W, SRC_H, fill=False,
                           ec="#7a7a7a", ls=(0, (3, 2)), lw=1.0, zorder=7))

    # finalize axes geometry BEFORE placing the inset, so the data<->axes transforms used
    # below are the FINAL ones. (The earlier version read transforms before set_xlim/aspect,
    # which mismatched and silently let the inset overlap the D label in the upper-right.)
    ax.set_xlim(LON0, LON1); ax.set_ylim(LAT0, LAT1)
    ax.set_aspect(1.32)  # lon/lat aspect at ~38N (cos38)
    ax.set_xlabel("Longitude (E)"); ax.set_ylabel("Latitude (N)")
    # 지도 제목은 캡션(captions.md)으로 이동 — 그림 상단 텍스트 없음
    ax.grid(alpha=0.15)
    fig.canvas.draw()  # stabilize transData/transAxes for precise inset placement

    # --- Seoul inset in the EMPTY upper-left land region (guards below PROVE it empty:
    # bus trunk stays south of lat 37.762 for lon<=127.95, rail south of 37.615).
    # The content x-span is DERIVED from the realized box pixel aspect so the inset is
    # letterbox-free by construction; the fixed y-span leaves room above S for its 2-line
    # label and below A's for the bottom margin. NB: transData<->transAxes chain only —
    # ax.transLimits encodes the opposite direction and must not be used here.
    _INSET_BOX = (126.97, 37.86, 127.94, 38.31)  # x0, y0, x1, y1 in MAIN-map DATA coords
    _ifrac = data_box_to_axes_fraction(ax, *_INSET_BOX)
    axins = ax.inset_axes(_ifrac)
    axins.set_facecolor("white")
    for sp in axins.spines.values():
        sp.set_edgecolor("#444"); sp.set_linewidth(1.4)
    axins.add_collection(LineCollection(
        [[(s[0][0], s[0][1]), (s[1][0], s[1][1])] for s in geo["motorway_skeleton"]],
        colors="#e2e3e8", linewidths=0.6))
    AS = R["road_A_S"]
    axins.plot([p[0] for p in AS], [p[1] for p in AS], color=MULTI_C, lw=2.6, zorder=5)
    # Markers drawn WITHOUT the single-letter overlay: the verbose annotations identify
    # each marker via short leaders, so the letter is redundant — and removing it
    # eliminates the marker-letter vs annotation overlap seen in earlier attempts.
    for k in ("A", "S"):
        nd = nodes[k]
        m, c = mk[k]
        axins.plot(nd["lon"], nd["lat"], marker=m, ms=13, mfc=c, mec="white", mew=1.6, zorder=8)
    _nA, _nS = nodes["A"], nodes["S"]
    _abb = ax.get_window_extent(renderer=fig.canvas.get_renderer())
    _wpx, _hpx = _ifrac[2] * _abb.width, _ifrac[3] * _abb.height
    _DLAT = 0.150
    _DLON = (_wpx / _hpx) * 1.32 * _DLAT  # exact content aspect == box aspect
    axins.set_xlim(127.024, 127.024 + _DLON); axins.set_ylim(37.493, 37.493 + _DLAT)
    axins.set_aspect(1.32)
    axins.set_xticks([127.05, 127.15, 127.25])
    axins.set_yticks([37.52, 37.56, 37.60])
    axins.tick_params(labelsize=7, length=2)
    # A sits bottom-center -> label into the empty right zone, level with the marker.
    _ins_A = axins.annotate("A Songpa assembly\n(administrative centroid)",
                            xy=(_nA["lon"], _nA["lat"]),
                            xytext=(_nA["lon"] + 0.0243, _nA["lat"] + 0.002),
                            fontsize=8.6, color=INK, ha="left", va="center",
                            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.5, shrinkB=3))
    # S sits top-left -> label ABOVE-RIGHT of the marker (left zone is outside the frame).
    _ins_S = axins.annotate("S Cheongnyangni Stn\n(rail access)",
                            xy=(_nS["lon"], _nS["lat"]),
                            xytext=(_nS["lon"] + 0.0116, _nS["lat"] + 0.0154),
                            fontsize=8.6, color=INK, ha="left", va="bottom",
                            arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.5, shrinkB=3))
    # route label in the mid gap between the S label (above) and the A label (below)
    _ins_T = axins.text(127.212, 37.566, "Access A\u2192S (shuttle)", fontsize=8.2,
                        color=MULTI_C, ha="center", va="center")
    axins.set_title("Seoul inset (access A\u2192S, ~12 km)", fontsize=9.2, fontweight="bold", pad=3)

    # No zoom connector lines: an earlier attempt drew two dashed lines from the Seoul
    # source-rectangle up to the inset, but the left one crossed the "S 청량리역" label.
    # The inset title plus the dashed source-rectangle convey the zoom relationship.

    # "동해" in the lower-right open sea (east of the real coast, max lon 129.26 at this
    # band); north arrow in the upper-right sea (coast stays west of 128.75 up there).
    _sea = ax.text(129.42, 37.38, "East Sea", fontsize=12, color="#5b7fa0", ha="center",
                   va="center", zorder=2, style="italic")
    _N_XY, _N_TXT = (129.40, 38.30), (129.40, 38.02)
    _ann_N = ax.annotate("N", xy=_N_XY, xytext=_N_TXT,
                         arrowprops=dict(arrowstyle="->", color=INK, lw=1.3),
                         ha="center", fontsize=10, fontweight="bold")

    handles = [
        plt.Line2D([], [], color=BUS_C, lw=2.4, label="Bus-only A\u2192D road (~185 km)"),
        plt.Line2D([], [], color=MULTI_C, lw=2.4, label="Multimodal road legs  A\u2192S \u00b7 R\u2192D"),
        plt.Line2D([], [], color=RAIL_C, lw=2.8, ls=(0, (1, 0.6)), label="Chartered rail  S\u2192R (assumption A1, schematic)"),
    ]
    # legend in the south band opened by LAT0=37.10: fully below the rail's 원주 dip
    # (min lat 37.342) — verified by the legend-vs-line guard below.
    _leg = ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.42, 0.010),
                     ncol=1, fontsize=9.0, framealpha=0.95, edgecolor="#bbbbbb")

    # ================= build-time overlap guards (renderer bboxes = ground truth) =====
    # Vision cannot be trusted to judge dense Korean labels; every check below measures
    # display-pixel geometry. ANY pairwise text overlap > 1 px^2, any label-line hit,
    # any element under the inset/legend, or any spillover past its frame fails the build.
    fig.canvas.draw()
    _rnd = fig.canvas.get_renderer()
    from matplotlib.text import Annotation as _Annotation, Text as _Text

    def _win(o):
        # Annotation.get_window_extent unions the TEXT bbox with its leader-ARROW bbox,
        # which would make every leadered label "overlap" its own marker/line. Leaders
        # are modeled separately in the line set, so measure the text glyph box only.
        if isinstance(o, _Annotation):
            return _Text.get_window_extent(o, renderer=_rnd)
        return o.get_window_extent(renderer=_rnd)

    def _ovl(a, b):
        _x0, _x1 = max(a.x0, b.x0), min(a.x1, b.x1)
        _y0, _y1 = max(a.y0, b.y0), min(a.y1, b.y1)
        return max(0.0, _x1 - _x0) * max(0.0, _y1 - _y0)

    def _seg_hits_box(p, q, bb, pad=1.5):
        x0, y0, x1, y1 = bb.x0 - pad, bb.y0 - pad, bb.x1 + pad, bb.y1 + pad
        if (x0 <= p[0] <= x1 and y0 <= p[1] <= y1) or (x0 <= q[0] <= x1 and y0 <= q[1] <= y1):
            return True
        cs = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        return any(segments_cross(p, q, cs[i], cs[(i + 1) % 4]) for i in range(4))

    def _poly_hits_box(pts, bb, pad=1.5):
        return any(_seg_hits_box(pts[i], pts[i + 1], bb, pad) for i in range(len(pts) - 1))

    def _inside_box(bb, outer, margin=1.5):
        return (bb.x0 >= outer.x0 + margin and bb.x1 <= outer.x1 - margin
                and bb.y0 >= outer.y0 + margin and bb.y1 <= outer.y1 - margin)

    _fails = []

    # (1) original guard: inset footprint occludes no node/route/rail/coast point.
    _ibox = axes_fraction_to_data_box(ax, _ifrac)
    _occluders = ([(nd["lon"], nd["lat"]) for nd in nodes.values()]
                  + [tuple(pt) for k in ("road_A_D", "road_A_S", "road_R_D") for pt in R[k]]
                  + list(rail) + list(coast))
    _inside = [(round(x, 3), round(y, 3)) for x, y in _occluders
               if _ibox[0] <= x <= _ibox[1] and _ibox[2] <= y <= _ibox[3]]
    assert not _inside, f"inset footprint occludes node/waypoint/route: {_inside[:6]}"

    # (2) original guard: inset internal text bboxes (labels + title) pairwise disjoint.
    _arts = [axins.title] + [t for t in axins.texts if t.get_text().strip()]
    _bad = [(repr(a.get_text()[:22]), repr(b.get_text()[:22]), round(_ovl(_win(a), _win(b)), 1))
            for i, a in enumerate(_arts) for b in _arts[i + 1:]
            if _ovl(_win(a), _win(b)) > 1.0]
    assert not _bad, f"inset text bbox overlap: {_bad}"

    # (3) retired: the main-map title moved to the caption file, so the
    # inset-text-vs-title check has no subject anymore.

    # (4) reinforced guard: EVERY text bbox in the figure pairwise disjoint — main node
    # labels, marker letters, sea/N labels, legend entries, axis tick labels, axis titles,
    # inset labels and inset tick labels.
    _ins_ticks = [t for t in axins.get_xticklabels() + axins.get_yticklabels() if t.get_text()]
    _main_ticks = [t for t in ax.get_xticklabels() + ax.get_yticklabels() if t.get_text()]
    _main_labels = [_lab_A, _lab_S, _lab_R, _lab_D, _sea, _ann_N]
    _all_texts = (_arts + _ins_ticks + _main_labels + _letters + list(_leg.get_texts())
                  + _main_ticks + [ax.xaxis.label, ax.yaxis.label])
    for i, a in enumerate(_all_texts):
        for b in _all_texts[i + 1:]:
            o = _ovl(_win(a), _win(b))
            if o > 1.0:
                _fails.append(f"text-text {a.get_text()[:18]!r} x {b.get_text()[:18]!r}: {o:.1f}px2")

    # (5) reinforced guard: no label bbox is crossed by any drawn line. Lines checked:
    # the three road routes, the rail centerline, the coastline, the source-rectangle
    # edges, the N-arrow shaft and each annotation leader (excluding its own label).
    _T = ax.transData.transform
    _rect = [(SRC_X0, SRC_Y0), (SRC_X0 + SRC_W, SRC_Y0), (SRC_X0 + SRC_W, SRC_Y0 + SRC_H),
             (SRC_X0, SRC_Y0 + SRC_H), (SRC_X0, SRC_Y0)]
    _lines = {
        "bus": _T(R["road_A_D"]), "road_A_S": _T(R["road_A_S"]), "road_R_D": _T(R["road_R_D"]),
        "rail": _T(rail), "coast": _T(coast), "src-rect": _T(_rect),
        "N-arrow": _T([_N_XY, _N_TXT]),
        "leader-A": _T([_lab_A.xy, (127.235, 37.458)]),
        "ins-AS": axins.transData.transform(AS),
        "leader-iA": axins.transData.transform([_ins_A.xy, (_nA["lon"] + 0.0243, _nA["lat"] + 0.002)]),
        "leader-iS": axins.transData.transform([_ins_S.xy, (_nS["lon"] + 0.0116, _nS["lat"] + 0.0154)]),
    }
    _own = {id(_ann_N): {"N-arrow"}, id(_lab_A): {"leader-A"},
            id(_ins_A): {"leader-iA"}, id(_ins_S): {"leader-iS"}}
    for t in _main_labels + _arts + _ins_ticks:
        bb = _win(t)
        for key, pts in _lines.items():
            if key in _own.get(id(t), ()):
                continue
            if _poly_hits_box(pts, bb):
                _fails.append(f"line-text {key} crosses {t.get_text()[:18]!r} "
                              f"bb=({bb.x0:.0f},{bb.y0:.0f})-({bb.x1:.0f},{bb.y1:.0f})")

    # (6) reinforced guard: the legend box and inset panel occlude nothing.
    _leg_bb = _win(_leg)
    _ins_bb = _win(axins)
    for key in ("bus", "road_A_S", "road_R_D", "rail", "coast"):
        if _poly_hits_box(_lines[key], _leg_bb, pad=2.0):
            _fails.append(f"legend box overlaps line {key}")
        if _poly_hits_box(_lines[key], _ins_bb, pad=2.0):
            _fails.append(f"inset panel overlaps line {key}")
    for t in _main_labels + _main_ticks:
        if _ovl(_win(t), _leg_bb) > 1.0:
            _fails.append(f"legend box overlaps text {t.get_text()[:18]!r}")
        if _ovl(_win(t), _ins_bb) > 1.0:
            _fails.append(f"inset panel overlaps text {t.get_text()[:18]!r}")

    # (7) reinforced guard: markers vs labels (marker bbox = center +- radius px).
    from matplotlib.transforms import Bbox
    _marks = {k: (_T([(nd["lon"], nd["lat"])])[0], 9.0) for k, nd in nodes.items()}
    _imk = {f"ins-{k}": (axins.transData.transform([(nodes[k]["lon"], nodes[k]["lat"])])[0], 10.5)
            for k in ("A", "S")}
    _letter_of = dict(zip(_letters, nodes.keys()))
    for name, (c, r) in {**_marks, **_imk}.items():
        mb = Bbox([[c[0] - r, c[1] - r], [c[0] + r, c[1] + r]])
        for t in _main_labels + _arts + _ins_ticks:
            if _ovl(_win(t), mb) > 1.0:
                tb = _win(t)
                _fails.append(f"marker {name} overlaps text {t.get_text()[:18]!r} "
                              f"mark=({c[0]:.0f},{c[1]:.0f},r{r}) "
                              f"tb=({tb.x0:.0f},{tb.y0:.0f})-({tb.x1:.0f},{tb.y1:.0f})")
        for lt, lk in _letter_of.items():
            if name != lk and _ovl(_win(lt), mb) > 1.0:
                _fails.append(f"marker {name} overlaps letter {lk}")

    # (8) reinforced guard: containment — inset content labels stay INSIDE the inset
    # frame; inset title/ticks and every main-map label stay inside the main axes.
    _ax_bb = ax.get_window_extent(renderer=_rnd)
    for t in (_ins_A, _ins_S, _ins_T):
        if not _inside_box(_win(t), _ins_bb):
            _fails.append(f"inset label spills past inset frame: {t.get_text()[:18]!r}")
    for t in [axins.title] + _ins_ticks + _main_labels:
        if not _inside_box(_win(t), _ax_bb, margin=0.5):
            _fails.append(f"text spills past main axes: {t.get_text()[:18]!r}")
    if not _inside_box(_leg_bb, _ax_bb, margin=0.5):
        _fails.append("legend spills past main axes")

    assert not _fails, "fig2 overlap guards FAILED:\n  " + "\n  ".join(_fails)
    print(f"fig2 overlap guards: all pass ({len(_all_texts)} texts, {len(_lines)} line groups)")
    save(fig, "fig2_corridor_map.png", output_dir=output_dir)


# ============================================================ figures 3--6: revision analysis
_SCOPE_LABELS = {"top3": "top-3", "top5": "top-5", "top10": "top-10", "full": "full"}
_LEG_LABELS = {"A_to_D": "A\u2192D", "A_to_S": "A\u2192S", "R_to_D": "R\u2192D", "S_to_R": "S\u2192R"}
_SCENARIO_LABELS = {
    "no_disruption": "baseline",
    "goseong_access_road_damage_severe": "access severe",
    "goseong_last_mile_damage_severe": "last-mile severe",
    "goseong_long_haul_damage_mild": "long-haul mild",
    "goseong_long_haul_damage_moderate": "long-haul moderate",
    "goseong_long_haul_damage_severe": "long-haul severe",
    "goseong_critical_link_blockage": "critical-link block",
    "goseong_rail_unavailable": "rail unavail.",
}
_POLICY_LABELS = {
    "bus_only": "bus-only",
    "static_multimodal": "static multi.",
    "precheck_switch": "precheck switch",
    "split_600_400": "split 600/400",
    "station_fallback_30": "station fb 30",
    "station_fallback_60": "station fb 60",
    "station_fallback_90": "station fb 90",
}
_WINNER_CODE = {"bus_only": 0, "static_multimodal": 1, "tie": 2, "unavailable": 3}
_WINNER_CMAP = ListedColormap(["#b8d0eb", "#efbbc3", "#dedede", "#f2f2f2"])


def _panel_letter(ax, letter):
    ax.text(0.0, 1.02, f"({letter})", transform=ax.transAxes, ha="left", va="bottom",
            fontsize=9.5, fontweight="bold", color=INK)


def _rail_condition_label(condition):
    status, multiplier = condition
    if status == "available":
        return f"avail. {multiplier:g}\u00d7"
    if status == "degraded":
        return f"degraded {multiplier:g}\u00d7"
    return "unavailable"


def _decision_annotation(cell):
    if abs(cell.bus_completion_rate - cell.multimodal_completion_rate) > 1e-10:
        return f"bus {cell.bus_completion_rate:.2f}\nmulti {cell.multimodal_completion_rate:.2f}"
    if cell.mean_delta is None:
        return "\u2014"
    return f"{cell.mean_delta:+.0f} min"


def fig3_graph_scope(data, *, output_dir=OUT):
    g = data.graph_scope
    fig, axes = plt.subplots(1, 3, figsize=(10.0, 3.45),
                             gridspec_kw={"width_ratios": [2.05, 1.0, 1.0]})
    x = np.arange(len(g.scopes))
    styles = {
        "A_to_D": (BUS_C, "o", "-"),
        "A_to_S": (MULTI_C, "s", "-"),
        "R_to_D": (RAIL_C, "^", "-"),
        "S_to_R": ("#666666", "D", (0, (3, 2))),
    }
    route_index = {(row.scope, row.leg): row for row in g.routes}
    for leg in g.legs:
        values = [route_index[(scope, leg)].detour_ratio for scope in g.scopes]
        color, marker, linestyle = styles[leg]
        axes[0].plot(x, [np.nan if value is None else value for value in values],
                     color=color, marker=marker, ls=linestyle, lw=1.45, ms=4.5,
                     mec="white", mew=0.6, label=_LEG_LABELS[leg])
        for xi, value, scope in zip(x, values, g.scopes):
            if value is None:
                axes[0].scatter([xi], [0.985], marker="x", s=32, color=BAD_EDGE, zorder=5)
    axes[0].axhline(1.0, color="#999999", lw=0.8, ls=(0, (2, 2)))
    axes[0].set_ylabel("Travel-time ratio vs full graph", fontsize=9)
    axes[0].set_xticks(x, [_SCOPE_LABELS[item] for item in g.scopes])
    axes[0].set_ylim(bottom=min(0.95, axes[0].get_ylim()[0]))
    _acad(axes[0])
    _panel_letter(axes[0], "a")

    agreements = {row.scope: row for row in g.agreements}
    for ax, field, letter, ylabel, color in (
        (axes[1], "connectivity", "b", "Connectivity agreement", RAIL_C),
        (axes[2], "ranking", "c", "Policy-ranking agreement", "#6a6a6a"),
    ):
        values = [getattr(agreements[scope], field) for scope in g.scopes]
        ax.bar(x, values, width=0.58, color=color, alpha=0.82, edgecolor="white", lw=0.5)
        for xi, value in zip(x, values):
            ax.text(xi, value + 0.025, f"{value:.2f}", ha="center", va="bottom",
                    fontsize=7.7, color=INK)
        ax.set_xticks(x, [_SCOPE_LABELS[item] for item in g.scopes], rotation=35, ha="right")
        ax.set_ylim(0, 1.10)
        ax.set_ylabel(ylabel, fontsize=9)
        _acad(ax)
        _panel_letter(ax, letter)
    fig.legend(loc="lower left", bbox_to_anchor=(0.07, -0.01), ncol=4,
               frameon=False, fontsize=8.2, handlelength=1.8, columnspacing=1.2)
    fig.subplots_adjust(left=0.08, right=0.99, top=0.92, bottom=0.25, wspace=0.36)
    _assert_figure_text(fig, "fig3")
    _texts_clear(fig, "fig3")
    return save(fig, "fig3_bpr_noop.png", output_dir=output_dir)


def fig4_paired_results(data, *, output_dir=OUT):
    points = data.paired.points
    labels = [_SCENARIO_LABELS[item.scenario_id] for item in points]
    y = np.arange(len(points))[::-1]
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.25), sharey=True,
                             gridspec_kw={"width_ratios": [1.0, 1.45]})

    bus = [item.bus_completion_rate for item in points]
    multi = [item.multimodal_completion_rate for item in points]
    for yi, left, right in zip(y, bus, multi):
        axes[0].plot([left, right], [yi, yi], color="#b7b7b7", lw=1.0, zorder=1)
    axes[0].scatter(bus, y, s=35, color=BUS_C, marker="o", edgecolor="white", lw=0.6,
                    zorder=3, label="bus-only")
    axes[0].scatter(multi, y, s=34, color=MULTI_C, marker="s", edgecolor="white", lw=0.6,
                    zorder=3, label="multimodal")
    axes[0].set_xlim(-0.05, 1.05)
    axes[0].set_xticks([0.0, 0.5, 1.0])
    axes[0].set_yticks(y, labels)
    axes[0].set_xlabel("Completion rate in 24 h", fontsize=9)
    _acad(axes[0], grid_axis="x")
    _panel_letter(axes[0], "a")

    finite_values = [
        value
        for item in points
        for value in (item.ci_lower, item.ci_upper)
        if value is not None
    ]
    span = max(abs(value) for value in finite_values) if finite_values else 1.0
    axes[1].axvline(0, color="#777777", lw=0.9, ls=(0, (2, 2)))
    for yi, item in zip(y, points):
        if item.mean_delta is None:
            axes[1].text(0, yi, "makespan comparison excluded", ha="center", va="center",
                         fontsize=7.8, color="#777777", path_effects=HALO_FX)
            continue
        color = BUS_C if item.mean_delta < 0 else MULTI_C
        axes[1].errorbar(
            item.mean_delta,
            yi,
            xerr=[[item.mean_delta - item.ci_lower], [item.ci_upper - item.mean_delta]],
            fmt="o",
            ms=4.8,
            color=color,
            ecolor=color,
            elinewidth=1.3,
            capsize=2.5,
            zorder=3,
        )
    axes[1].set_xlim(-span * 1.18, span * 1.18)
    axes[1].set_xlabel(r"Bus $-$ multi. completion time (min, 95\% CI)", fontsize=9)
    axes[1].text(0.02, 0.02, r"$\leftarrow$ bus faster", transform=axes[1].transAxes,
                 ha="left", va="bottom", color=BUS_C, fontsize=8)
    axes[1].text(0.98, 0.02, r"multimodal faster $\rightarrow$", transform=axes[1].transAxes,
                 ha="right", va="bottom", color=MULTI_C, fontsize=8)
    _acad(axes[1], grid_axis="x")
    _panel_letter(axes[1], "b")
    fig.legend(
        handles=[
            plt.Line2D([], [], marker="o", color="none", markerfacecolor=BUS_C,
                       markeredgecolor="white", label="bus-only"),
            plt.Line2D([], [], marker="s", color="none", markerfacecolor=MULTI_C,
                       markeredgecolor="white", label="multimodal"),
        ],
        loc="lower left",
        bbox_to_anchor=(0.16, 0.005),
        ncol=2,
        frameon=False,
        fontsize=8.2,
        handletextpad=0.4,
        columnspacing=1.1,
    )
    fig.subplots_adjust(left=0.16, right=0.99, top=0.94, bottom=0.20, wspace=0.18)
    _assert_figure_text(fig, "fig4")
    _texts_clear(fig, "fig4")
    return save(fig, "fig4_segment_decomposition.png", output_dir=output_dir)


def fig5_decision_boundary(data, *, output_dir=OUT):
    curve = data.break_even
    decision = data.road_rail
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 3.85),
                             gridspec_kw={"width_ratios": [1.0, 1.35]})

    x = [item[0] for item in curve.points]
    y = [item[1] for item in curve.points]
    axes[0].axhline(0, color="#777777", lw=0.9, ls=(0, (2, 2)))
    axes[0].plot(x, y, color=INK, marker="o", lw=1.5, ms=4.5,
                 mec="white", mew=0.6)
    if curve.crossing is not None:
        axes[0].axvspan(curve.ci_lower, curve.ci_upper, color=RAIL_C, alpha=0.14, lw=0)
        axes[0].axvline(curve.crossing, color=RAIL_C, lw=1.2)
        axes[0].text(curve.crossing, axes[0].get_ylim()[1] * 0.82,
                     f"{curve.crossing:.2f}×", ha="center", va="top", fontsize=8,
                     color=RAIL_C, path_effects=HALO_FX)
    else:
        axes[0].text(0.98, 0.94, "no crossing in tested range", transform=axes[0].transAxes,
                     ha="right", va="top", fontsize=8, color="#666666")
    axes[0].set_xlabel("Long-haul road slowdown multiplier", fontsize=9)
    axes[0].set_ylabel(r"Bus $-$ multi. completion time (min)", fontsize=9)
    _acad(axes[0])
    _panel_letter(axes[0], "a")

    roads = decision.road_multipliers
    conditions = decision.rail_conditions
    index = {(cell.road_multiplier, (cell.rail_status, cell.rail_multiplier)): cell
             for cell in decision.cells}
    matrix = np.array([
        [_WINNER_CODE[index[(road, condition)].winner] for road in roads]
        for condition in conditions
    ])
    axes[1].imshow(matrix, cmap=_WINNER_CMAP, vmin=-0.5, vmax=3.5, aspect="auto")
    for row_index, condition in enumerate(conditions):
        for col_index, road in enumerate(roads):
            cell = index[(road, condition)]
            axes[1].text(col_index, row_index, _decision_annotation(cell),
                         ha="center", va="center", fontsize=7.2, color=INK,
                         linespacing=1.2)
    axes[1].set_xticks(np.arange(len(roads)), [f"{value:g}×" for value in roads])
    axes[1].set_yticks(np.arange(len(conditions)), [_rail_condition_label(item) for item in conditions])
    axes[1].set_xlabel("Long-haul road slowdown multiplier", fontsize=9)
    axes[1].set_ylabel("Rail state", fontsize=9)
    axes[1].set_xticks(np.arange(-0.5, len(roads), 1), minor=True)
    axes[1].set_yticks(np.arange(-0.5, len(conditions), 1), minor=True)
    axes[1].grid(which="minor", color="white", lw=1.2)
    axes[1].tick_params(which="minor", bottom=False, left=False)
    for spine in axes[1].spines.values():
        spine.set_visible(False)
    _panel_letter(axes[1], "b")
    legend = [Patch(fc="#b8d0eb", label="bus advantage"),
              Patch(fc="#efbbc3", label="multimodal advantage"), Patch(fc="#dedede", label="tie")]
    fig.legend(handles=legend, loc="lower center", ncol=3, frameon=False,
               fontsize=8.2, bbox_to_anchor=(0.72, 0.005), handlelength=1.3)
    fig.subplots_adjust(left=0.08, right=0.99, top=0.93, bottom=0.21, wspace=0.30)
    _assert_figure_text(fig, "fig5")
    _texts_clear(fig, "fig5")
    return save(fig, "fig5_rail_substitution.png", output_dir=output_dir)


def fig6_resource_adaptive(data, *, output_dir=OUT):
    demand = data.demand_fleet
    adaptive = data.adaptive
    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.75),
                             gridspec_kw={"width_ratios": [1.0, 1.42]})

    demand_index = {(cell.demand, cell.road_fleet_total): cell for cell in demand.cells}
    demand_matrix = np.array([
        [_WINNER_CODE[demand_index[(demand_value, fleet)].winner] for fleet in demand.fleets]
        for demand_value in demand.demands
    ])
    axes[0].imshow(demand_matrix, cmap=_WINNER_CMAP, vmin=-0.5, vmax=3.5, aspect="auto")
    for row_index, demand_value in enumerate(demand.demands):
        for col_index, fleet in enumerate(demand.fleets):
            cell = demand_index[(demand_value, fleet)]
            axes[0].text(col_index, row_index, _decision_annotation(cell),
                         ha="center", va="center", fontsize=7.5, color=INK,
                         linespacing=1.2)
    axes[0].set_xticks(np.arange(len(demand.fleets)), [str(value) for value in demand.fleets])
    axes[0].set_yticks(np.arange(len(demand.demands)), [f"{value:,}" for value in demand.demands])
    axes[0].set_xlabel("Road vehicles", fontsize=9)
    axes[0].set_ylabel("Demand (pax)", fontsize=9)
    axes[0].set_xticks(np.arange(-0.5, len(demand.fleets), 1), minor=True)
    axes[0].set_yticks(np.arange(-0.5, len(demand.demands), 1), minor=True)
    axes[0].grid(which="minor", color="white", lw=1.2)
    axes[0].tick_params(which="minor", bottom=False, left=False)
    for spine in axes[0].spines.values():
        spine.set_visible(False)
    _panel_letter(axes[0], "a")

    conditions = adaptive.rail_conditions
    policies = adaptive.policies
    adaptive_index = {(cell.policy_id, (cell.rail_status, cell.rail_multiplier)): cell
                      for cell in adaptive.cells}
    completion_matrix = np.array([
        [adaptive_index[(policy, condition)].completion_rate for condition in conditions]
        for policy in policies
    ])
    completion_cmap = LinearSegmentedColormap.from_list(
        "completion", [BAD_C, "#f7f7f7", OK_C]
    )
    image = axes[1].imshow(completion_matrix, cmap=completion_cmap, vmin=0, vmax=1,
                           aspect="auto")
    for row_index, policy in enumerate(policies):
        for col_index, condition in enumerate(conditions):
            cell = adaptive_index[(policy, condition)]
            time_label = "\u2014" if cell.makespan is None else f"{cell.makespan:.0f} min"
            axes[1].text(col_index, row_index,
                         f"#{cell.rank}\n{cell.completion_rate:.2f}\u00b7{time_label}",
                         ha="center", va="center", fontsize=7.0, color=INK,
                         linespacing=1.18)
            if cell.winner:
                axes[1].add_patch(Rectangle((col_index - 0.48, row_index - 0.48), 0.96, 0.96,
                                            fill=False, edgecolor=RAIL_C, lw=1.6))
    axes[1].set_xticks(np.arange(len(conditions)), [_rail_condition_label(item) for item in conditions])
    axes[1].set_yticks(np.arange(len(policies)), [_POLICY_LABELS[item] for item in policies])
    axes[1].set_xlabel("Rail state", fontsize=9)
    axes[1].set_xticks(np.arange(-0.5, len(conditions), 1), minor=True)
    axes[1].set_yticks(np.arange(-0.5, len(policies), 1), minor=True)
    axes[1].grid(which="minor", color="white", lw=1.2)
    axes[1].tick_params(which="minor", bottom=False, left=False)
    for spine in axes[1].spines.values():
        spine.set_visible(False)
    _panel_letter(axes[1], "b")
    colorbar = fig.colorbar(image, ax=axes[1], fraction=0.035, pad=0.025,
                            ticks=[0, 0.5, 1.0])
    colorbar.set_label("Completion rate", fontsize=8.5)
    colorbar.ax.tick_params(labelsize=8, length=2)
    fig.legend(handles=[Patch(fc="#b8d0eb", label="bus advantage"),
                        Patch(fc="#efbbc3", label="multimodal advantage"),
                        Patch(fc="none", ec=RAIL_C, lw=1.6, label="rank-1 in state")],
               loc="lower left", bbox_to_anchor=(0.055, 0.002), ncol=3,
               frameon=False, fontsize=8.0, handlelength=1.25, columnspacing=1.1)
    fig.subplots_adjust(left=0.09, right=0.96, top=0.94, bottom=0.18, wspace=0.32)
    _assert_figure_text(fig, "fig6")
    _texts_clear(fig, "fig6")
    return save(fig, "fig6_assumption_collapse.png", output_dir=output_dir)


def build_revision_figures(data, *, output_dir=OUT):
    """Render figures 3--6 from already verified revision data."""
    if not all(hasattr(data, field) for field in (
        "graph_scope", "paired", "break_even", "road_rail", "demand_fleet", "adaptive"
    )):
        raise TypeError("data must expose the verified RevisionFigureData contract")
    return (
        fig3_graph_scope(data, output_dir=output_dir),
        fig4_paired_results(data, output_dir=output_dir),
        fig5_decision_boundary(data, output_dir=output_dir),
        fig6_resource_adaptive(data, output_dir=output_dir),
    )


def build_figures(
    *,
    include_vector_fig1=False,
    revision_data=None,
    analysis_dir=DEFAULT_ANALYSIS_DIR,
    output_dir=OUT,
):
    """Build figures while preserving user-generated figure 1 by default."""
    data = revision_data or load_revision_figure_data(analysis_dir)
    if include_vector_fig1:
        fig1_framework(output_dir=output_dir)
    fig2_map(output_dir=output_dir)
    outputs = (
        fig3_graph_scope(data, output_dir=output_dir),
        fig4_paired_results(data, output_dir=output_dir),
        fig5_decision_boundary(data, output_dir=output_dir),
        fig6_resource_adaptive(data, output_dir=output_dir),
    )
    print("done.")
    return outputs


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--include-vector-fig1",
        action="store_true",
        help="explicitly replace user-generated fig1_framework.png with vector fallback",
    )
    parser.add_argument(
        "--analysis-dir",
        default=str(DEFAULT_ANALYSIS_DIR),
        help="hash-verified full revision analysis directory",
    )
    parser.add_argument("--output-dir", default=OUT)
    args = parser.parse_args(argv)
    build_figures(
        include_vector_fig1=args.include_vector_fig1,
        analysis_dir=args.analysis_dir,
        output_dir=args.output_dir,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
