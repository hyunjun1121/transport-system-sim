"""OSM maxspeed evidence summaries for road-class review.

The cached OSM graph contains sparse public maxspeed tags. This module extracts
class-level speed statistics so reviewers can replace coarse fallback speeds
with traceable evidence where coverage is adequate. It deliberately produces
candidate evidence, not reviewed road-class overrides.
"""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import networkx as nx

from src.realworld.attributes import (
    HIGHWAY_DEFAULTS,
    is_routeable_vehicle_highway,
    normalize_highway,
    parse_length_m,
    parse_speed_kph,
)
from src.realworld.osm_network import load_graphml
from src.realworld.road_evidence import DEFAULT_ROAD_GRAPH_PATH


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROAD_SPEED_EVIDENCE_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "road_speed_evidence_candidates.csv"
)
DEFAULT_ROAD_SPEED_EVIDENCE_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "road_speed_evidence_manifest.json"
)
ROAD_SPEED_EVIDENCE_COLUMNS: tuple[str, ...] = (
    "highway",
    "routeable_edge_count",
    "routeable_length_km",
    "maxspeed_observed_count",
    "maxspeed_observed_rate",
    "observed_length_km",
    "observed_length_share",
    "min_observed_speed_kph",
    "median_observed_speed_kph",
    "p85_observed_speed_kph",
    "length_weighted_mean_speed_kph",
    "mapper_default_speed_kph",
    "candidate_speed_kph",
    "candidate_source_class",
    "candidate_source_name",
    "claim_boundary",
    "review_note",
)
ROAD_SPEED_EVIDENCE_SCOPE = (
    "OSM maxspeed evidence candidate table; not reviewed road calibration or "
    "operational speed evidence."
)


@dataclass
class RoadSpeedClassStats:
    """Mutable speed evidence accumulator for one road class."""

    highway: str
    routeable_edge_count: int = 0
    routeable_length_m: float = 0.0
    observed_length_m: float = 0.0
    observed_speeds: list[float] = field(default_factory=list)
    observed_weighted_speeds: list[tuple[float, float]] = field(default_factory=list)

    def add(self, data: Mapping[str, Any]) -> None:
        """Add one routeable edge."""

        self.routeable_edge_count += 1
        length_m = parse_length_m(data.get("length_m", data.get("length"))) or 0.0
        self.routeable_length_m += length_m
        speed = parse_speed_kph(data.get("maxspeed"))
        if speed is None:
            return
        self.observed_speeds.append(speed)
        self.observed_length_m += length_m
        if length_m > 0.0:
            self.observed_weighted_speeds.append((speed, length_m))

    def to_row(self) -> dict[str, str]:
        """Return a CSV-ready class evidence row."""

        defaults = HIGHWAY_DEFAULTS.get(self.highway)
        default_speed = defaults.speed_kph if defaults is not None else 0.0
        observed_count = len(self.observed_speeds)
        candidate_speed = (
            _percentile(self.observed_speeds, 50.0)
            if observed_count > 0
            else default_speed
        )
        source_class = (
            "public-data-derived"
            if observed_count > 0
            else "expert assumption"
        )
        review_note = (
            "Candidate uses median OSM maxspeed for this class; review sparse "
            "coverage before replacing mapper defaults."
            if observed_count > 0
            else "No parseable OSM maxspeed tags for this class; current value remains a fallback."
        )
        return {
            "highway": self.highway,
            "routeable_edge_count": str(self.routeable_edge_count),
            "routeable_length_km": _fmt(self.routeable_length_m / 1000.0),
            "maxspeed_observed_count": str(observed_count),
            "maxspeed_observed_rate": _fmt(_rate(observed_count, self.routeable_edge_count)),
            "observed_length_km": _fmt(self.observed_length_m / 1000.0),
            "observed_length_share": _fmt(
                self.observed_length_m / self.routeable_length_m
                if self.routeable_length_m > 0.0
                else 0.0
            ),
            "min_observed_speed_kph": _fmt(_min(self.observed_speeds)),
            "median_observed_speed_kph": _fmt(_percentile(self.observed_speeds, 50.0)),
            "p85_observed_speed_kph": _fmt(_percentile(self.observed_speeds, 85.0)),
            "length_weighted_mean_speed_kph": _fmt(
                _weighted_mean(self.observed_weighted_speeds)
            ),
            "mapper_default_speed_kph": _fmt(default_speed),
            "candidate_speed_kph": _fmt(candidate_speed),
            "candidate_source_class": source_class,
            "candidate_source_name": "cached OSM maxspeed tags" if observed_count > 0 else "mapper fallback pending review",
            "claim_boundary": ROAD_SPEED_EVIDENCE_SCOPE,
            "review_note": review_note,
        }


def build_road_speed_evidence_rows(graph: nx.Graph) -> list[dict[str, str]]:
    """Return routeable road-class maxspeed evidence rows from a graph."""

    by_class: dict[str, RoadSpeedClassStats] = {}
    for _, _, data in _iter_edge_data(graph):
        if not is_routeable_vehicle_highway(data.get("highway")):
            continue
        highway, _ = normalize_highway(data.get("highway"))
        if highway not in HIGHWAY_DEFAULTS:
            continue
        if highway not in by_class:
            by_class[highway] = RoadSpeedClassStats(highway)
        by_class[highway].add(data)

    rows = [stats.to_row() for stats in by_class.values()]
    rows.sort(
        key=lambda row: (
            -float(row["routeable_length_km"] or 0.0),
            row["highway"],
        )
    )
    return rows


def build_cached_road_speed_evidence_rows(
    path: str | Path = DEFAULT_ROAD_GRAPH_PATH,
) -> list[dict[str, str]]:
    """Load cached GraphML and return speed-evidence candidate rows."""

    graph = load_graphml(path, normalize=True)
    return build_road_speed_evidence_rows(graph)


def write_road_speed_evidence(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_ROAD_SPEED_EVIDENCE_PATH,
    manifest_path: str | Path = DEFAULT_ROAD_SPEED_EVIDENCE_MANIFEST_PATH,
    source_graph_path: str | Path = DEFAULT_ROAD_GRAPH_PATH,
) -> dict[str, Any]:
    """Write speed evidence rows and a conservative manifest."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ROAD_SPEED_EVIDENCE_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    observed_rows = [
        row for row in rows if int(str(row.get("maxspeed_observed_count", "0") or "0")) > 0
    ]
    value = {
        "schema_version": 1,
        "result_scope": ROAD_SPEED_EVIDENCE_SCOPE,
        "source_graph_path": _display_path(source_graph_path),
        "outputs": {
            "road_speed_evidence_candidates": _display_path(output),
            "manifest": _display_path(manifest),
        },
        "row_count": len(rows),
        "rows_with_observed_maxspeed": len(observed_rows),
        "publication_ready": False,
        "claim_boundary": (
            "This table summarizes sparse cached OSM maxspeed tags and fallback "
            "values. It does not create reviewed speed overrides, calibrated "
            "traffic speeds, or operational routing evidence."
        ),
        "review_items": [
            "review sparse OSM maxspeed coverage before using candidate speeds",
            "compare candidate speeds with public speed limits, agency data, or routing benchmarks",
            "move accepted values into data/parameters/road_class_overrides.csv only after review",
        ],
    }
    with manifest.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return value


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
    "DEFAULT_ROAD_SPEED_EVIDENCE_MANIFEST_PATH",
    "DEFAULT_ROAD_SPEED_EVIDENCE_PATH",
    "ROAD_SPEED_EVIDENCE_COLUMNS",
    "ROAD_SPEED_EVIDENCE_SCOPE",
    "RoadSpeedClassStats",
    "build_cached_road_speed_evidence_rows",
    "build_road_speed_evidence_rows",
    "write_road_speed_evidence",
]
