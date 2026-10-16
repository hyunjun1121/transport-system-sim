# -*- coding: utf-8 -*-
"""Fail-closed adapter from full revision analysis to figures 3--6.

This module stores no route geometry or coordinates.  It accepts only the
coordinate-free CSV summaries written by ``analyze_paper_revision_results.py``.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Iterable, Mapping, Sequence


GRAPH_SCOPES = ("top3", "top5", "top10", "full")
GRAPH_LEGS = ("A_to_D", "A_to_S", "R_to_D", "S_to_R")
KEY_PAIRED_SCENARIOS = (
    "no_disruption",
    "goseong_access_road_damage_severe",
    "goseong_last_mile_damage_severe",
    "goseong_long_haul_damage_mild",
    "goseong_long_haul_damage_moderate",
    "goseong_long_haul_damage_severe",
    "goseong_critical_link_blockage",
    "goseong_rail_unavailable",
)
ADAPTIVE_POLICIES = (
    "bus_only",
    "static_multimodal",
    "precheck_switch",
    "split_600_400",
    "station_fallback_30",
    "station_fallback_60",
    "station_fallback_90",
)
REQUIRED_ANALYSES = (
    "graph_scope_route_metrics",
    "graph_scope_stability",
    "paired_summary",
    "break_even",
    "road_rail_map",
    "demand_fleet",
    "adaptive_policies",
)
REQUIRED_FILES = {f"{name}.csv" for name in REQUIRED_ANALYSES}


@dataclass(frozen=True)
class GraphRoutePoint:
    scope: str
    leg: str
    connected: bool
    detour_ratio: float | None


@dataclass(frozen=True)
class GraphAgreementPoint:
    scope: str
    connectivity: float
    ranking: float


@dataclass(frozen=True)
class GraphScopeFigureData:
    scopes: tuple[str, ...]
    legs: tuple[str, ...]
    routes: tuple[GraphRoutePoint, ...]
    agreements: tuple[GraphAgreementPoint, ...]


@dataclass(frozen=True)
class PairedPoint:
    scenario_id: str
    bus_completion_rate: float
    multimodal_completion_rate: float
    finite_pair_count: int
    mean_delta: float | None
    ci_lower: float | None
    ci_upper: float | None
    confidence: float | None


@dataclass(frozen=True)
class PairedFigureData:
    points: tuple[PairedPoint, ...]


@dataclass(frozen=True)
class BreakEvenFigureData:
    status: str
    points: tuple[tuple[float, float], ...]
    crossing: float | None
    ci_lower: float | None
    ci_upper: float | None
    confidence: float | None


@dataclass(frozen=True)
class DecisionCell:
    road_multiplier: float
    rail_status: str
    rail_multiplier: float | None
    winner: str
    mean_delta: float | None
    bus_completion_rate: float
    multimodal_completion_rate: float


@dataclass(frozen=True)
class RoadRailFigureData:
    road_multipliers: tuple[float, ...]
    rail_conditions: tuple[tuple[str, float | None], ...]
    cells: tuple[DecisionCell, ...]


@dataclass(frozen=True)
class DemandFleetCell:
    demand: int
    road_fleet_total: int
    winner: str
    mean_delta: float | None
    bus_completion_rate: float
    multimodal_completion_rate: float


@dataclass(frozen=True)
class DemandFleetFigureData:
    demands: tuple[int, ...]
    fleets: tuple[int, ...]
    cells: tuple[DemandFleetCell, ...]


@dataclass(frozen=True)
class AdaptiveCell:
    rail_status: str
    rail_multiplier: float | None
    policy_id: str
    completion_rate: float
    makespan: float | None
    rank: int
    winner: bool


@dataclass(frozen=True)
class AdaptiveFigureData:
    rail_conditions: tuple[tuple[str, float | None], ...]
    policies: tuple[str, ...]
    cells: tuple[AdaptiveCell, ...]


@dataclass(frozen=True)
class RevisionFigureData:
    analysis_dir: Path
    graph_scope: GraphScopeFigureData
    paired: PairedFigureData
    break_even: BreakEvenFigureData
    road_rail: RoadRailFigureData
    demand_fleet: DemandFleetFigureData
    adaptive: AdaptiveFigureData


def load_revision_figure_data(analysis_dir: str | Path) -> RevisionFigureData:
    """Load one hash-verified, publishable full-analysis directory."""

    root = Path(analysis_dir).resolve()
    manifest_path = root / "analysis_manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"analysis manifest is missing: {manifest_path}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read analysis manifest: {manifest_path}") from error
    if not isinstance(manifest, Mapping):
        raise ValueError("analysis manifest must contain an object")
    if manifest.get("stage") != "full":
        raise ValueError("paper figures require analysis stage=full")
    if manifest.get("analysis_complete_full") is not True:
        raise ValueError("paper figures require analysis_complete_full=true")
    if manifest.get("final_study_ready") is not False:
        raise ValueError("analysis manifest must preserve final_study_ready=false")
    blockers = manifest.get("analysis_completeness_blockers")
    if blockers not in ([], ()):
        raise ValueError("publishable full analysis must have no publication blockers")

    analyses = manifest.get("analyses")
    if not isinstance(analyses, Mapping):
        raise ValueError("analysis manifest lacks analysis states")
    unavailable = [
        name
        for name in REQUIRED_ANALYSES
        if not isinstance(analyses.get(name), Mapping)
        or analyses[name].get("status") != "available"
    ]
    if unavailable:
        raise ValueError("required analyses are unavailable: " + ", ".join(unavailable))

    records = _verify_generated_csv_files(root, manifest.get("generated_csv_files"))
    missing = sorted(REQUIRED_FILES - set(records))
    if missing:
        raise ValueError("analysis manifest lacks required CSV files: " + ", ".join(missing))
    tables = {name: _read_csv(root / name) for name in REQUIRED_FILES}

    return RevisionFigureData(
        analysis_dir=root,
        graph_scope=_map_graph_scope(
            tables["graph_scope_route_metrics.csv"],
            tables["graph_scope_stability.csv"],
        ),
        paired=_map_paired(tables["paired_summary.csv"]),
        break_even=_map_break_even(tables["break_even.csv"]),
        road_rail=_map_road_rail(tables["road_rail_map.csv"]),
        demand_fleet=_map_demand_fleet(tables["demand_fleet.csv"]),
        adaptive=_map_adaptive(tables["adaptive_policies.csv"]),
    )


def _verify_generated_csv_files(
    root: Path, raw_records: object
) -> dict[str, Mapping[str, object]]:
    if not isinstance(raw_records, Sequence) or isinstance(raw_records, (str, bytes)):
        raise ValueError("analysis manifest lacks generated CSV records")
    records: dict[str, Mapping[str, object]] = {}
    for index, record in enumerate(raw_records, start=1):
        if not isinstance(record, Mapping):
            raise ValueError(f"generated CSV record {index} must be an object")
        name = str(record.get("path", ""))
        if not name or Path(name).name != name or Path(name).suffix.lower() != ".csv":
            raise ValueError(f"generated CSV record {index} has unsafe path")
        if name in records:
            raise ValueError(f"duplicate generated CSV record: {name}")
        path = root / name
        if not path.is_file():
            raise FileNotFoundError(f"generated analysis CSV is missing: {path}")
        expected_hash = str(record.get("sha256", ""))
        actual_hash = _sha256(path)
        if len(expected_hash) != 64 or actual_hash != expected_hash:
            raise ValueError(f"generated analysis CSV SHA-256 mismatch: {name}")
        expected_rows = _nonnegative_int(record.get("data_row_count"), f"{name} row count")
        actual_rows = _csv_row_count(path)
        if actual_rows != expected_rows:
            raise ValueError(f"generated analysis CSV row-count mismatch: {name}")
        records[name] = record
    return records


def _map_graph_scope(
    route_rows: Sequence[Mapping[str, str]],
    stability_rows: Sequence[Mapping[str, str]],
) -> GraphScopeFigureData:
    _require_columns(
        route_rows,
        {
            "graph_scope",
            "leg_id",
            "connected",
            "travel_time_detour_ratio_vs_full",
        },
        "graph-scope route",
    )
    _require_columns(
        stability_rows,
        {"graph_scope", "connectivity_agreement", "policy_ranking_agreement"},
        "graph-scope stability",
    )
    route_index: dict[tuple[str, str], Mapping[str, str]] = {}
    for row in route_rows:
        key = (row["graph_scope"].strip(), row["leg_id"].strip())
        if key in route_index:
            raise ValueError(f"duplicate graph route row: {key}")
        route_index[key] = row
    expected = {(scope, leg) for scope in GRAPH_SCOPES for leg in GRAPH_LEGS}
    if set(route_index) != expected:
        raise ValueError("graph route matrix must cover top3/top5/top10/full x four legs")
    routes = []
    for scope in GRAPH_SCOPES:
        for leg in GRAPH_LEGS:
            row = route_index[(scope, leg)]
            connected = _bool(row["connected"], f"{scope}/{leg} connected")
            ratio = _optional_float(
                row["travel_time_detour_ratio_vs_full"], f"{scope}/{leg} detour"
            )
            if connected and ratio is None:
                raise ValueError(f"connected graph route lacks detour ratio: {scope}/{leg}")
            routes.append(GraphRoutePoint(scope, leg, connected, ratio))

    stability_index = _unique_index(stability_rows, "graph_scope", "graph stability")
    if set(stability_index) != set(GRAPH_SCOPES):
        raise ValueError("graph stability must cover top3/top5/top10/full")
    agreements = tuple(
        GraphAgreementPoint(
            scope,
            _rate(stability_index[scope]["connectivity_agreement"], "connectivity agreement"),
            _rate(stability_index[scope]["policy_ranking_agreement"], "ranking agreement"),
        )
        for scope in GRAPH_SCOPES
    )
    return GraphScopeFigureData(GRAPH_SCOPES, GRAPH_LEGS, tuple(routes), agreements)


def _map_paired(rows: Sequence[Mapping[str, str]]) -> PairedFigureData:
    required = {
        "scenario_id",
        "resource_frame",
        "graph_scope",
        "rail_status",
        "return_strategy",
        "departure_policy_id",
        "mean_bus_completion_rate",
        "mean_multimodal_completion_rate",
        "finite_pair_count",
        "mean_delta_bus_minus_multimodal",
        "bootstrap_ci_lower",
        "bootstrap_ci_upper",
        "bootstrap_confidence",
    }
    _require_columns(rows, required, "paired summary")
    selected = [
        row
        for row in rows
        if row["scenario_id"] in KEY_PAIRED_SCENARIOS
        and row["resource_frame"] == "matched_road_fleet"
        and row["graph_scope"] == "top10"
        and row["return_strategy"] == "reverse_network"
        and row["departure_policy_id"] == "strict"
    ]
    index = _unique_index(selected, "scenario_id", "key paired scenario")
    if set(index) != set(KEY_PAIRED_SCENARIOS):
        missing = sorted(set(KEY_PAIRED_SCENARIOS) - set(index))
        raise ValueError("paired summary lacks key scenarios: " + ", ".join(missing))
    points = []
    for scenario in KEY_PAIRED_SCENARIOS:
        row = index[scenario]
        finite_count = _nonnegative_int(row["finite_pair_count"], "finite pair count")
        delta = _optional_float(row["mean_delta_bus_minus_multimodal"], "paired mean delta")
        lower = _optional_float(row["bootstrap_ci_lower"], "paired CI lower")
        upper = _optional_float(row["bootstrap_ci_upper"], "paired CI upper")
        confidence = _optional_float(row["bootstrap_confidence"], "paired confidence")
        if finite_count:
            if None in (delta, lower, upper, confidence):
                raise ValueError(f"finite paired scenario lacks bootstrap interval: {scenario}")
            if not (0.0 < confidence < 1.0 and lower <= delta <= upper):
                raise ValueError(f"invalid paired bootstrap interval: {scenario}")
        elif any(value is not None for value in (delta, lower, upper, confidence)):
            raise ValueError(f"non-finite paired scenario has makespan estimate: {scenario}")
        points.append(
            PairedPoint(
                scenario,
                _rate(row["mean_bus_completion_rate"], "bus completion rate"),
                _rate(row["mean_multimodal_completion_rate"], "multimodal completion rate"),
                finite_count,
                delta,
                lower,
                upper,
                confidence,
            )
        )
    return PairedFigureData(tuple(points))


def _map_break_even(rows: Sequence[Mapping[str, str]]) -> BreakEvenFigureData:
    required = {
        "scenario_id",
        "resource_frame",
        "graph_scope",
        "rail_status",
        "return_strategy",
        "status",
        "crossing_road_multiplier",
        "paired_mean_points",
        "joint_seed_bootstrap_ci_lower",
        "joint_seed_bootstrap_ci_upper",
        "joint_seed_bootstrap_confidence",
    }
    _require_columns(rows, required, "break-even")
    selected = [
        row
        for row in rows
        if row["resource_frame"] == "matched_road_fleet"
        and row["graph_scope"] == "top10"
        and row["rail_status"] == "available"
        and row["return_strategy"] == "reverse_network"
    ]
    if len(selected) != 1:
        raise ValueError("break-even analysis must contain one matched top10 series")
    row = selected[0]
    try:
        raw_points = json.loads(row["paired_mean_points"])
    except json.JSONDecodeError as error:
        raise ValueError("break-even paired_mean_points is invalid JSON") from error
    if not isinstance(raw_points, list) or len(raw_points) < 2:
        raise ValueError("break-even curve needs at least two paired mean points")
    points = tuple(
        (
            _required_float(item[0], "break-even multiplier"),
            _required_float(item[1], "break-even delta"),
        )
        for item in raw_points
        if isinstance(item, list) and len(item) == 2
    )
    if len(points) != len(raw_points) or tuple(sorted(points)) != points:
        raise ValueError("break-even points must be sorted numeric pairs")
    crossing = _optional_float(row["crossing_road_multiplier"], "crossing")
    lower = _optional_float(row["joint_seed_bootstrap_ci_lower"], "crossing CI lower")
    upper = _optional_float(row["joint_seed_bootstrap_ci_upper"], "crossing CI upper")
    confidence = _optional_float(row["joint_seed_bootstrap_confidence"], "crossing confidence")
    if crossing is not None:
        if None in (lower, upper, confidence):
            raise ValueError("observed crossing lacks joint bootstrap interval")
        if not (lower <= crossing <= upper and 0.0 < confidence < 1.0):
            raise ValueError("invalid break-even bootstrap interval")
    return BreakEvenFigureData(row["status"].strip(), points, crossing, lower, upper, confidence)


def _map_road_rail(rows: Sequence[Mapping[str, str]]) -> RoadRailFigureData:
    required = {
        "road_multiplier",
        "rail_status",
        "rail_multiplier",
        "resource_frame",
        "graph_scope",
        "return_strategy",
        "overall_winner",
        "mean_delta_bus_minus_multimodal",
        "mean_bus_completion_rate",
        "mean_multimodal_completion_rate",
    }
    _require_columns(rows, required, "road-rail map")
    selected = [
        row
        for row in rows
        if row["resource_frame"] == "matched_road_fleet"
        and row["graph_scope"] == "top10"
        and row["return_strategy"] == "reverse_network"
    ]
    cells = tuple(
        DecisionCell(
            _required_float(row["road_multiplier"], "road multiplier"),
            row["rail_status"].strip(),
            _optional_float(row["rail_multiplier"], "rail multiplier"),
            _winner(row["overall_winner"]),
            _optional_float(row["mean_delta_bus_minus_multimodal"], "road-rail delta"),
            _rate(row["mean_bus_completion_rate"], "bus completion rate"),
            _rate(row["mean_multimodal_completion_rate"], "multimodal completion rate"),
        )
        for row in selected
    )
    roads = tuple(sorted({cell.road_multiplier for cell in cells}))
    conditions = tuple(
        sorted(
            {(cell.rail_status, cell.rail_multiplier) for cell in cells},
            key=_rail_condition_key,
        )
    )
    _assert_rectangular(cells, roads, conditions, "road-rail", lambda c: (c.road_multiplier, (c.rail_status, c.rail_multiplier)))
    if len(roads) < 2 or len(conditions) < 2:
        raise ValueError("road-rail map needs at least a 2 x 2 grid")
    return RoadRailFigureData(roads, conditions, cells)


def _map_demand_fleet(rows: Sequence[Mapping[str, str]]) -> DemandFleetFigureData:
    required = {
        "demand",
        "road_fleet_total",
        "resource_frame",
        "graph_scope",
        "return_strategy",
        "overall_winner",
        "mean_delta_bus_minus_multimodal",
        "mean_bus_completion_rate",
        "mean_multimodal_completion_rate",
    }
    _require_columns(rows, required, "demand-fleet")
    selected = [
        row
        for row in rows
        if row["resource_frame"] == "matched_road_fleet"
        and row["graph_scope"] == "top10"
        and row["return_strategy"] == "reverse_network"
    ]
    cells = tuple(
        DemandFleetCell(
            _positive_int(row["demand"], "demand"),
            _positive_int(row["road_fleet_total"], "road fleet"),
            _winner(row["overall_winner"]),
            _optional_float(row["mean_delta_bus_minus_multimodal"], "demand-fleet delta"),
            _rate(row["mean_bus_completion_rate"], "bus completion rate"),
            _rate(row["mean_multimodal_completion_rate"], "multimodal completion rate"),
        )
        for row in selected
    )
    demands = tuple(sorted({cell.demand for cell in cells}))
    fleets = tuple(sorted({cell.road_fleet_total for cell in cells}))
    _assert_rectangular(cells, demands, fleets, "demand-fleet", lambda c: (c.demand, c.road_fleet_total))
    if len(demands) < 2 or len(fleets) < 2:
        raise ValueError("demand-fleet map needs at least a 2 x 2 grid")
    return DemandFleetFigureData(demands, fleets, cells)


def _map_adaptive(rows: Sequence[Mapping[str, str]]) -> AdaptiveFigureData:
    required = {
        "resource_frame",
        "rail_status",
        "rail_multiplier",
        "graph_scope",
        "return_strategy",
        "policy_id",
        "mean_completion_rate",
        "mean_finite_makespan",
        "rank",
        "winner",
    }
    _require_columns(rows, required, "adaptive policies")
    selected = [
        row
        for row in rows
        if row["resource_frame"] == "matched_road_fleet"
        and row["graph_scope"] == "top10"
        and row["return_strategy"] == "reverse_network"
    ]
    cells = tuple(
        AdaptiveCell(
            row["rail_status"].strip(),
            _optional_float(row["rail_multiplier"], "adaptive rail multiplier"),
            row["policy_id"].strip(),
            _rate(row["mean_completion_rate"], "adaptive completion rate"),
            _optional_float(row["mean_finite_makespan"], "adaptive makespan"),
            _positive_int(row["rank"], "adaptive rank"),
            _bool(row["winner"], "adaptive winner"),
        )
        for row in selected
    )
    conditions = tuple(
        sorted(
            {(cell.rail_status, cell.rail_multiplier) for cell in cells},
            key=_rail_condition_key,
        )
    )
    policies = tuple(policy for policy in ADAPTIVE_POLICIES if any(cell.policy_id == policy for cell in cells))
    if policies != ADAPTIVE_POLICIES:
        raise ValueError("adaptive analysis lacks one or more specified policies")
    _assert_rectangular(cells, conditions, policies, "adaptive", lambda c: ((c.rail_status, c.rail_multiplier), c.policy_id))
    if len(conditions) < 2:
        raise ValueError("adaptive analysis needs at least two rail conditions")
    return AdaptiveFigureData(conditions, policies, cells)


def _assert_rectangular(
    cells: Iterable[object],
    first: Sequence[object],
    second: Sequence[object],
    name: str,
    key_function,
) -> None:
    keys = [key_function(cell) for cell in cells]
    expected = {(left, right) for left in first for right in second}
    if len(keys) != len(set(keys)) or set(keys) != expected:
        raise ValueError(f"{name} rows do not form a complete rectangular matrix")


def _winner(value: object) -> str:
    text = str(value).strip()
    allowed = {"bus_only", "static_multimodal", "tie", "unavailable"}
    if text not in allowed:
        raise ValueError(f"invalid winner label: {text!r}")
    return text


def _rail_condition_key(item: tuple[str, float | None]) -> tuple[int, float]:
    status, multiplier = item
    order = {"available": 0, "degraded": 1, "unavailable": 2}
    if status not in order:
        raise ValueError(f"invalid rail status: {status!r}")
    return order[status], math.inf if multiplier is None else multiplier


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"required analysis CSV has no rows: {path.name}")
    return rows


def _require_columns(
    rows: Sequence[Mapping[str, str]], required: set[str], name: str
) -> None:
    if not rows:
        raise ValueError(f"{name} rows are empty")
    missing = sorted(required - set(rows[0]))
    if missing:
        raise ValueError(f"{name} CSV lacks columns: " + ", ".join(missing))


def _unique_index(
    rows: Iterable[Mapping[str, str]], key: str, name: str
) -> dict[str, Mapping[str, str]]:
    result: dict[str, Mapping[str, str]] = {}
    for row in rows:
        value = row[key].strip()
        if value in result:
            raise ValueError(f"duplicate {name}: {value}")
        result[value] = row
    return result


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _csv_row_count(path: Path) -> int:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def _required_float(value: object, name: str) -> float:
    number = _optional_float(value, name)
    if number is None:
        raise ValueError(f"{name} must be finite")
    return number


def _optional_float(value: object, name: str) -> float | None:
    text = "" if value is None else str(value).strip()
    if not text:
        return None
    try:
        number = float(text)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be numeric") from error
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    return number


def _rate(value: object, name: str) -> float:
    number = _required_float(value, name)
    if not 0.0 <= number <= 1.0:
        raise ValueError(f"{name} must lie in [0, 1]")
    return number


def _nonnegative_int(value: object, name: str) -> int:
    number = _required_float(value, name)
    if number < 0 or not number.is_integer():
        raise ValueError(f"{name} must be a non-negative integer")
    return int(number)


def _positive_int(value: object, name: str) -> int:
    number = _nonnegative_int(value, name)
    if number < 1:
        raise ValueError(f"{name} must be positive")
    return number


def _bool(value: object, name: str) -> bool:
    text = str(value).strip().lower()
    if text in {"true", "1"}:
        return True
    if text in {"false", "0"}:
        return False
    raise ValueError(f"{name} must be boolean")


__all__ = [
    "ADAPTIVE_POLICIES",
    "GRAPH_LEGS",
    "GRAPH_SCOPES",
    "KEY_PAIRED_SCENARIOS",
    "RevisionFigureData",
    "load_revision_figure_data",
]
