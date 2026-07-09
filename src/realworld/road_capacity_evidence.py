"""OSM lane-count evidence summaries for road-capacity review.

The cached OSM graph does not provide calibrated traffic capacities. This
module summarizes sparse public ``lanes`` tags by routeable road class and
translates observed lane counts into candidate directional capacity proxies for
review. It deliberately produces candidate evidence, not reviewed road-class
overrides or calibrated traffic counts.
"""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from re import findall
from typing import Any, Iterable, Mapping, Sequence

import networkx as nx

from src.realworld.attributes import (
    HIGHWAY_DEFAULTS,
    is_routeable_vehicle_highway,
    normalize_highway,
    parse_length_m,
    parse_positive_float,
)
from src.realworld.osm_network import load_graphml
from src.realworld.road_evidence import DEFAULT_ROAD_GRAPH_PATH


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CAPACITY_PER_LANE_VPH = 800.0

# MOLIT "도로의 구조·시설기준에 관한 규칙" (Korean Road Act structural-design
# standard) — conservative per-direction design lane count by OSM highway class.
# Used as a transparent lane basis when OSM ``lanes`` tags are absent: the cached
# Goseong corridor graph carries 0/10 classes with parseable lanes tags. Official
# doctrine / public-law source; a design-standard lane count, not a field count.
MOLIT_DESIGN_LANES_BY_HIGHWAY: dict[str, int] = {
    "motorway": 2,
    "motorway_link": 1,
    "trunk": 2,
    "trunk_link": 1,
    "primary": 2,
    "primary_link": 1,
    "secondary": 2,
    "secondary_link": 1,
    "tertiary": 1,
    "tertiary_link": 1,
    "unclassified": 1,
    "residential": 1,
    "living_street": 1,
    "service": 1,
    "track": 1,
    "road": 1,
}

# KOTI Korean Highway Capacity Manual (KOTI HCM Korea 2013) 단속류 (signalized
# urban arterial) per-lane service-capacity direction, veh/h/lane. Motorway is
# 연속류 (uninterrupted) but carries no edges in the Goseong bus-practical graph.
# Combined with the design-lane count above to derive a transparent directional
# capacity proxy when observed lanes are absent. HCM-direction planning proxy,
# not a calibrated traffic count.
HCM_SIGNALIZED_PER_LANE_VPH_BY_HIGHWAY: dict[str, float] = {
    "motorway": 1800.0,
    "motorway_link": 900.0,
    "trunk": 1000.0,
    "trunk_link": 600.0,
    "primary": 900.0,
    "primary_link": 540.0,
    "secondary": 800.0,
    "secondary_link": 480.0,
    "tertiary": 700.0,
    "tertiary_link": 420.0,
    "unclassified": 500.0,
    "residential": 400.0,
    "living_street": 200.0,
    "service": 200.0,
    "track": 150.0,
    "road": 500.0,
}
DEFAULT_ROAD_CAPACITY_EVIDENCE_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "road_capacity_evidence_candidates.csv"
)
DEFAULT_ROAD_CAPACITY_EVIDENCE_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "road_capacity_evidence_manifest.json"
)
ROAD_CAPACITY_EVIDENCE_COLUMNS: tuple[str, ...] = (
    "highway",
    "routeable_edge_count",
    "routeable_length_km",
    "lanes_observed_count",
    "lanes_observed_rate",
    "observed_length_km",
    "observed_length_share",
    "min_observed_lanes",
    "median_observed_lanes",
    "p85_observed_lanes",
    "length_weighted_mean_lanes",
    "mapper_default_capacity_veh_per_hr",
    "candidate_capacity_per_lane_veh_per_hr",
    "candidate_capacity_veh_per_hr",
    "candidate_source_class",
    "candidate_source_name",
    "claim_boundary",
    "review_note",
)
ROAD_CAPACITY_EVIDENCE_SCOPE = (
    "OSM lane-count capacity candidate table; not reviewed road calibration, "
    "traffic counts, or operational capacity evidence."
)


@dataclass
class RoadCapacityClassStats:
    """Mutable lane-count evidence accumulator for one road class."""

    highway: str
    capacity_per_lane_vph: float = DEFAULT_CAPACITY_PER_LANE_VPH
    routeable_edge_count: int = 0
    routeable_length_m: float = 0.0
    observed_length_m: float = 0.0
    observed_lanes: list[float] = field(default_factory=list)
    observed_weighted_lanes: list[tuple[float, float]] = field(default_factory=list)

    def add(self, data: Mapping[str, Any]) -> None:
        """Add one routeable edge."""

        self.routeable_edge_count += 1
        length_m = parse_length_m(data.get("length_m", data.get("length"))) or 0.0
        self.routeable_length_m += length_m
        lanes = parse_lane_count(data)
        if lanes is None:
            return
        self.observed_lanes.append(lanes)
        self.observed_length_m += length_m
        if length_m > 0.0:
            self.observed_weighted_lanes.append((lanes, length_m))

    def to_row(self) -> dict[str, str]:
        """Return a CSV-ready class evidence row."""

        defaults = HIGHWAY_DEFAULTS.get(self.highway)
        default_capacity = defaults.capacity if defaults is not None else 0.0
        observed_count = len(self.observed_lanes)
        median_lanes = _percentile(self.observed_lanes, 50.0)
        design_lanes = infer_lanes_by_design_standard(self.highway)
        per_lane = HCM_SIGNALIZED_PER_LANE_VPH_BY_HIGHWAY.get(
            self.highway, self.capacity_per_lane_vph
        )
        if median_lanes is not None:
            candidate_capacity = median_lanes * per_lane
            candidate_per_lane = per_lane
            source_class = "public-data-derived"
            source_name = (
                "cached OSM observed median lanes x KOTI HCM per-lane proxy"
            )
            review_note = (
                "Candidate uses the median observed OSM lane count times a "
                "KOTI HCM signalized per-lane planning proxy; review lane-tag "
                "coverage and directional capacity assumptions before replacing "
                "mapper defaults."
            )
        elif design_lanes is not None:
            candidate_capacity = float(design_lanes) * per_lane
            candidate_per_lane = per_lane
            source_class = "design-standard-derived"
            source_name = (
                "MOLIT design-standard lanes x KOTI HCM per-lane proxy "
                "(OSM lanes tags absent for this class)"
            )
            review_note = (
                "No parseable OSM lane tags for this class; candidate derived "
                "from the MOLIT design-standard lane count times a KOTI HCM "
                "signalized per-lane planning proxy. Review the design-lane and "
                "per-lane assumptions before replacing mapper defaults."
            )
        else:
            candidate_capacity = default_capacity
            candidate_per_lane = self.capacity_per_lane_vph
            source_class = "expert assumption"
            source_name = "mapper fallback pending review"
            review_note = (
                "No parseable OSM lane tags and no design-standard mapping for "
                "this class; current value remains the mapper fallback."
            )
        return {
            "highway": self.highway,
            "routeable_edge_count": str(self.routeable_edge_count),
            "routeable_length_km": _fmt(self.routeable_length_m / 1000.0),
            "lanes_observed_count": str(observed_count),
            "lanes_observed_rate": _fmt(_rate(observed_count, self.routeable_edge_count)),
            "observed_length_km": _fmt(self.observed_length_m / 1000.0),
            "observed_length_share": _fmt(
                self.observed_length_m / self.routeable_length_m
                if self.routeable_length_m > 0.0
                else 0.0
            ),
            "min_observed_lanes": _fmt(_min(self.observed_lanes)),
            "median_observed_lanes": _fmt(median_lanes),
            "p85_observed_lanes": _fmt(_percentile(self.observed_lanes, 85.0)),
            "length_weighted_mean_lanes": _fmt(
                _weighted_mean(self.observed_weighted_lanes)
            ),
            "mapper_default_capacity_veh_per_hr": _fmt(default_capacity),
            "candidate_capacity_per_lane_veh_per_hr": _fmt(candidate_per_lane),
            "candidate_capacity_veh_per_hr": _fmt(candidate_capacity),
            "candidate_source_class": source_class,
            "candidate_source_name": source_name,
            "claim_boundary": ROAD_CAPACITY_EVIDENCE_SCOPE,
            "review_note": review_note,
        }


def parse_lane_count(data: Mapping[str, Any]) -> float | None:
    """Parse OSM lane-count fields into a conservative lane count.

    ``lanes`` is preferred. If absent, directional lane fields are considered.
    For ambiguous multi-value tags, the lowest positive candidate is used to
    avoid inflating capacity in the review aid.
    """

    candidates = _parse_lane_values(data.get("lanes"))
    if not candidates:
        candidates = [
            *_parse_lane_values(data.get("lanes:forward")),
            *_parse_lane_values(data.get("lanes:backward")),
        ]
    if not candidates:
        return None
    return min(candidates)


def infer_lanes_by_design_standard(highway: str) -> int | None:
    """Return the MOLIT design-standard per-direction lane count, or ``None``."""

    return MOLIT_DESIGN_LANES_BY_HIGHWAY.get(highway)


def design_standard_capacity_veh_per_hr(highway: str) -> float | None:
    """Return design-standard lanes × HCM per-lane capacity, or ``None``.

    Transparent directional capacity proxy used when OSM ``lanes`` tags are
    absent. Equals ``MOLIT_DESIGN_LANES_BY_HIGHWAY[highway] *
    HCM_SIGNALIZED_PER_LANE_VPH_BY_HIGHWAY[highway]``.
    """

    lanes = MOLIT_DESIGN_LANES_BY_HIGHWAY.get(highway)
    per_lane = HCM_SIGNALIZED_PER_LANE_VPH_BY_HIGHWAY.get(highway)
    if lanes is None or per_lane is None:
        return None
    return float(lanes) * per_lane


def build_road_capacity_evidence_rows(
    graph: nx.Graph,
    *,
    capacity_per_lane_vph: float = DEFAULT_CAPACITY_PER_LANE_VPH,
) -> list[dict[str, str]]:
    """Return routeable road-class lane-count capacity candidate rows."""

    capacity_per_lane_vph = _positive_float(
        capacity_per_lane_vph,
        "capacity_per_lane_vph",
    )
    by_class: dict[str, RoadCapacityClassStats] = {}
    for _, _, data in _iter_edge_data(graph):
        if not is_routeable_vehicle_highway(data.get("highway")):
            continue
        highway, _ = normalize_highway(data.get("highway"))
        if highway not in HIGHWAY_DEFAULTS:
            continue
        if highway not in by_class:
            by_class[highway] = RoadCapacityClassStats(
                highway=highway,
                capacity_per_lane_vph=capacity_per_lane_vph,
            )
        by_class[highway].add(data)

    rows = [stats.to_row() for stats in by_class.values()]
    rows.sort(
        key=lambda row: (
            -float(row["routeable_length_km"] or 0.0),
            row["highway"],
        )
    )
    return rows


def build_cached_road_capacity_evidence_rows(
    path: str | Path = DEFAULT_ROAD_GRAPH_PATH,
    *,
    capacity_per_lane_vph: float = DEFAULT_CAPACITY_PER_LANE_VPH,
) -> list[dict[str, str]]:
    """Load cached GraphML and return capacity-evidence candidate rows."""

    graph = load_graphml(path, normalize=True)
    return build_road_capacity_evidence_rows(
        graph,
        capacity_per_lane_vph=capacity_per_lane_vph,
    )


def write_road_capacity_evidence(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_ROAD_CAPACITY_EVIDENCE_PATH,
    manifest_path: str | Path = DEFAULT_ROAD_CAPACITY_EVIDENCE_MANIFEST_PATH,
    source_graph_path: str | Path = DEFAULT_ROAD_GRAPH_PATH,
    capacity_per_lane_vph: float = DEFAULT_CAPACITY_PER_LANE_VPH,
) -> dict[str, Any]:
    """Write capacity candidate rows and a conservative manifest."""

    capacity_per_lane_vph = _positive_float(
        capacity_per_lane_vph,
        "capacity_per_lane_vph",
    )
    output = Path(output_path)
    manifest = Path(manifest_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=ROAD_CAPACITY_EVIDENCE_COLUMNS,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)

    observed_rows = [
        row for row in rows if int(str(row.get("lanes_observed_count", "0") or "0")) > 0
    ]
    value = {
        "schema_version": 1,
        "result_scope": ROAD_CAPACITY_EVIDENCE_SCOPE,
        "source_graph_path": _display_path(source_graph_path),
        "outputs": {
            "road_capacity_evidence_candidates": _display_path(output),
            "manifest": _display_path(manifest),
        },
        "row_count": len(rows),
        "rows_with_observed_lanes": len(observed_rows),
        "capacity_per_lane_veh_per_hr": capacity_per_lane_vph,
        "publication_ready": False,
        "claim_boundary": (
            "This table summarizes sparse cached OSM lanes tags and translates "
            "them with a documented per-lane planning proxy. It does not create "
            "reviewed capacity overrides, traffic-count calibration, or "
            "operational routing evidence."
        ),
        "review_items": [
            "review sparse OSM lane-count coverage before using candidate capacities",
            "compare candidate capacities with traffic counts, agency design references, or routing benchmarks",
            "move accepted values into data/parameters/road_class_overrides.csv only after review",
        ],
    }
    with manifest.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return value


def _parse_lane_values(value: Any) -> list[float]:
    parsed: list[float] = []
    for item in _flatten_values(value):
        if isinstance(item, bool) or item is None:
            continue
        numeric = parse_positive_float(item)
        if numeric is not None:
            parsed.append(numeric)
            continue
        for token in findall(r"\d+(?:\.\d+)?", str(item)):
            token_value = parse_positive_float(token)
            if token_value is not None:
                parsed.append(token_value)
    return parsed


def _flatten_values(value: Any) -> tuple[Any, ...]:
    if value is None:
        return ()
    if isinstance(value, (list, tuple, set, frozenset)):
        flattened: list[Any] = []
        for item in value:
            flattened.extend(_flatten_values(item))
        return tuple(flattened)
    return (value,)


def _iter_edge_data(graph: nx.Graph) -> Iterable[tuple[Any, Any, Mapping[str, Any]]]:
    if graph.is_multigraph():
        for u, v, _, data in graph.edges(keys=True, data=True):
            yield u, v, data
        return
    for u, v, data in graph.edges(data=True):
        yield u, v, data


def _percentile(values: Sequence[float], percentile: float) -> float | None:
    finite = sorted(value for value in values if math.isfinite(value))
    if not finite:
        return None
    if len(finite) == 1:
        return finite[0]
    position = (len(finite) - 1) * percentile / 100.0
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return finite[int(position)]
    fraction = position - lower
    return finite[lower] * (1.0 - fraction) + finite[upper] * fraction


def _weighted_mean(values: Sequence[tuple[float, float]]) -> float | None:
    total_weight = sum(weight for _, weight in values)
    if total_weight <= 0.0:
        return None
    return sum(value * weight for value, weight in values) / total_weight


def _min(values: Sequence[float]) -> float | None:
    finite = [value for value in values if math.isfinite(value)]
    return min(finite) if finite else None


def _rate(count: int, total: int) -> float:
    return count / total if total > 0 else 0.0


def _positive_float(value: float, field_name: str) -> float:
    parsed = parse_positive_float(value)
    if parsed is None:
        raise ValueError(f"{field_name} must be positive and finite, got {value!r}")
    return parsed


def _fmt(value: float | None) -> str:
    if value is None or not math.isfinite(value):
        return ""
    return f"{value:.6f}".rstrip("0").rstrip(".")


def _display_path(path: str | Path) -> str:
    filepath = Path(path)
    try:
        return filepath.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return filepath.as_posix()


__all__ = [
    "DEFAULT_CAPACITY_PER_LANE_VPH",
    "DEFAULT_ROAD_CAPACITY_EVIDENCE_MANIFEST_PATH",
    "DEFAULT_ROAD_CAPACITY_EVIDENCE_PATH",
    "HCM_SIGNALIZED_PER_LANE_VPH_BY_HIGHWAY",
    "MOLIT_DESIGN_LANES_BY_HIGHWAY",
    "ROAD_CAPACITY_EVIDENCE_COLUMNS",
    "ROAD_CAPACITY_EVIDENCE_SCOPE",
    "RoadCapacityClassStats",
    "build_cached_road_capacity_evidence_rows",
    "build_road_capacity_evidence_rows",
    "design_standard_capacity_veh_per_hr",
    "infer_lanes_by_design_standard",
    "parse_lane_count",
    "write_road_capacity_evidence",
]
