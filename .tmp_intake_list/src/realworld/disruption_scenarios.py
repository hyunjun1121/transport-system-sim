"""Deterministic structured disruption scenarios for real-world graphs.

The helpers in this module map scenario-table rows to simulator graph edges.
They do not claim that any listed hazard is observed disaster data; the default
CSV is a reproducible scenario design for quasi-real resilience experiments.
"""

from __future__ import annotations

import csv
import hashlib
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from math import isfinite
from pathlib import Path
from typing import Any

import networkx as nx

from src.sim_types import EdgeDisruption


Edge = tuple[Any, Any]
HazardBbox = tuple[float, float, float, float]

ALLOWED_FAMILIES = frozenset(
    {
        "random",
        "critical_link",
        "access_road",
        "last_mile",
        "rail_station_access",
        "spatial_hazard_overlay",
    }
)
REQUIRED_FAMILIES = ALLOWED_FAMILIES
ALLOWED_DISRUPTION_MODES = frozenset({"blocked", "capacity_reduction"})
ALLOWED_SELECTION_METHODS = frozenset(
    {
        "hash_rank",
        "edge_betweenness",
        "shortest_path",
        "station_access",
        "bbox_midpoint",
    }
)
FAMILY_SELECTION_METHODS = {
    "random": frozenset({"hash_rank"}),
    "critical_link": frozenset({"edge_betweenness"}),
    "access_road": frozenset({"shortest_path"}),
    "last_mile": frozenset({"shortest_path"}),
    "rail_station_access": frozenset({"station_access"}),
    "spatial_hazard_overlay": frozenset({"bbox_midpoint"}),
}
CSV_COLUMNS = (
    "scenario_id",
    "region_id",
    "family",
    "label",
    "selection_method",
    "target_segment",
    "disruption_mode",
    "capacity_factor",
    "p_fail_scale",
    "max_edges",
    "hazard_bbox_west",
    "hazard_bbox_south",
    "hazard_bbox_east",
    "hazard_bbox_north",
    "evidence_class",
    "observed_disaster_data",
    "notes",
)
DEFAULT_REQUIRED_NODES = {
    "assembly": "A",
    "destination": "D",
    "rail_access": "S",
    "rail_egress": "R",
}
SCENARIO_EDGE_ATTRS = (
    "disruption_scenario_id",
    "disruption_family",
    "disruption_reason_category",
    "disruption_selection_rank",
    "disruption_mode",
    "disruption_capacity_factor",
)
DEFAULT_SCENARIO_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "scenarios"
    / "disruption_scenarios.csv"
)


@dataclass(frozen=True)
class DisruptionScenario:
    """One deterministic disruption scenario row."""

    scenario_id: str
    region_id: str
    family: str
    label: str
    selection_method: str
    target_segment: str
    disruption_mode: str
    capacity_factor: float
    p_fail_scale: float
    max_edges: int | None = None
    hazard_bbox: HazardBbox | None = None
    evidence_class: str = "scenario_based"
    observed_disaster_data: bool = False
    notes: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "scenario_id", _clean_required_text(self.scenario_id, "scenario_id"))
        object.__setattr__(self, "region_id", _clean_required_text(self.region_id, "region_id"))
        object.__setattr__(self, "family", _clean_required_text(self.family, "family"))
        object.__setattr__(self, "label", _clean_required_text(self.label, "label"))
        object.__setattr__(
            self,
            "selection_method",
            _clean_required_text(self.selection_method, "selection_method"),
        )
        object.__setattr__(
            self,
            "target_segment",
            _clean_required_text(self.target_segment, "target_segment"),
        )
        object.__setattr__(
            self,
            "disruption_mode",
            _clean_required_text(self.disruption_mode, "disruption_mode"),
        )
        object.__setattr__(
            self,
            "evidence_class",
            _clean_required_text(self.evidence_class, "evidence_class"),
        )
        object.__setattr__(self, "notes", "" if self.notes is None else str(self.notes).strip())

        capacity_factor = _finite_float(self.capacity_factor, "capacity_factor")
        p_fail_scale = _finite_float(self.p_fail_scale, "p_fail_scale")
        object.__setattr__(self, "capacity_factor", capacity_factor)
        object.__setattr__(self, "p_fail_scale", p_fail_scale)
        if self.max_edges is not None:
            object.__setattr__(self, "max_edges", _positive_int(self.max_edges, "max_edges"))
        if self.hazard_bbox is not None:
            object.__setattr__(self, "hazard_bbox", _validate_bbox(self.hazard_bbox))

        _validate_scenario(self)

    @property
    def reason_category(self) -> str:
        """Return the reason category assigned to selected edges."""

        if self.family in {"access_road", "last_mile"}:
            return f"{self.family}:{self.target_segment}"
        if self.family == "spatial_hazard_overlay":
            return "scenario_based_hazard_overlay"
        return self.family

    @property
    def edge_disruption(self) -> EdgeDisruption:
        """Return the simulator disruption state for selected edges."""

        if self.disruption_mode == "blocked":
            return EdgeDisruption(status="blocked", capacity_factor=0.0)
        return EdgeDisruption(status="degraded", capacity_factor=self.capacity_factor)


@dataclass(frozen=True)
class ScenarioEdge:
    """A graph edge selected by a structured disruption scenario."""

    scenario_id: str
    family: str
    edge: Edge
    reason_category: str
    rank: int
    realworld_edge_id: str | None
    mode: str
    source: str | None


def load_disruption_scenarios(
    path: str | Path = DEFAULT_SCENARIO_PATH,
    *,
    region_id: str | None = None,
) -> tuple[DisruptionScenario, ...]:
    """Load and validate disruption scenarios from a CSV file."""

    filepath = Path(path)
    with filepath.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        _validate_csv_header(reader.fieldnames, filepath)
        scenarios = tuple(
            _scenario_from_row(row, row_number)
            for row_number, row in enumerate(reader, start=2)
            if _row_has_content(row)
        )

    if not scenarios:
        raise ValueError(f"{filepath} contains no disruption scenarios")
    validate_scenario_table(scenarios)
    if region_id is None:
        return scenarios

    selected = tuple(scenario for scenario in scenarios if scenario.region_id == region_id)
    if not selected:
        raise ValueError(f"{filepath} contains no scenarios for region_id {region_id!r}")
    return selected


def validate_scenario_table(
    scenarios: Sequence[DisruptionScenario],
    *,
    required_families: set[str] | frozenset[str] | None = None,
) -> None:
    """Validate scenario identity uniqueness and optional family coverage."""

    if not scenarios:
        raise ValueError("scenario table must contain at least one row")

    counts = Counter(scenario.scenario_id for scenario in scenarios)
    duplicates = sorted(scenario_id for scenario_id, count in counts.items() if count > 1)
    if duplicates:
        raise ValueError(f"duplicate disruption scenario_id values: {', '.join(duplicates)}")

    if required_families is not None:
        families = set(scenario_family_coverage(scenarios))
        missing = sorted(set(required_families) - families)
        if missing:
            raise ValueError(f"missing disruption scenario families: {', '.join(missing)}")


def assert_required_family_coverage(
    scenarios: Sequence[DisruptionScenario],
    required_families: set[str] | frozenset[str] = REQUIRED_FAMILIES,
) -> None:
    """Raise unless all required Workstream 7 scenario families are present."""

    validate_scenario_table(scenarios, required_families=required_families)


def scenario_family_coverage(
    scenarios: Sequence[DisruptionScenario],
) -> dict[str, int]:
    """Return scenario counts by family."""

    return dict(Counter(scenario.family for scenario in scenarios))


def select_candidate_edges(
    graph: nx.DiGraph,
    scenario: DisruptionScenario,
    *,
    required_nodes: Mapping[str, Any] | Sequence[Any] | None = None,
) -> tuple[ScenarioEdge, ...]:
    """Map one scenario to deterministic candidate graph edges."""

    _validate_mapping_graph(graph, scenario)
    node_ids = _normalize_required_nodes(required_nodes)

    if scenario.selection_method == "hash_rank":
        edges = _select_hash_rank_edges(graph, scenario)
    elif scenario.selection_method == "edge_betweenness":
        edges = _select_critical_link_edges(graph, scenario)
    elif scenario.selection_method == "shortest_path":
        edges = _select_shortest_path_edges(graph, scenario, node_ids)
    elif scenario.selection_method == "station_access":
        edges = _select_station_access_edges(graph, scenario, node_ids)
    elif scenario.selection_method == "bbox_midpoint":
        edges = _select_bbox_edges(graph, scenario)
    else:
        raise ValueError(f"unsupported selection_method: {scenario.selection_method!r}")

    if not edges:
        raise ValueError(f"scenario {scenario.scenario_id!r} selected no candidate edges")

    limited = _limit_edges(edges, scenario.max_edges)
    return tuple(
        _scenario_edge(graph, scenario, edge, rank=index + 1)
        for index, edge in enumerate(limited)
    )


def build_scenario_edge_map(
    graph: nx.DiGraph,
    scenarios: Sequence[DisruptionScenario],
    *,
    region_id: str | None = None,
    required_nodes: Mapping[str, Any] | Sequence[Any] | None = None,
) -> dict[str, tuple[ScenarioEdge, ...]]:
    """Return selected candidate edges for each scenario."""

    return {
        scenario.scenario_id: select_candidate_edges(
            graph,
            scenario,
            required_nodes=required_nodes,
        )
        for scenario in scenarios
        if region_id is None or scenario.region_id == region_id
    }


def build_scenario_disruption_map(
    graph: nx.DiGraph,
    scenario: DisruptionScenario,
    *,
    required_nodes: Mapping[str, Any] | Sequence[Any] | None = None,
    include_normal: bool = False,
) -> dict[Edge, EdgeDisruption]:
    """Return simulator disruption states for one deterministic scenario."""

    disruptions = {
        (u, v): EdgeDisruption()
        for u, v in graph.edges()
    } if include_normal else {}
    for selected in select_candidate_edges(graph, scenario, required_nodes=required_nodes):
        disruptions[selected.edge] = scenario.edge_disruption
    return disruptions


def mark_scenario_edges(
    graph: nx.DiGraph,
    scenario: DisruptionScenario,
    *,
    required_nodes: Mapping[str, Any] | Sequence[Any] | None = None,
    inplace: bool = False,
    clear_existing: bool = False,
) -> nx.DiGraph:
    """Annotate selected edges with scenario family and reason metadata."""

    target = graph if inplace else graph.copy()
    if clear_existing:
        for _, _, data in target.edges(data=True):
            for attr in SCENARIO_EDGE_ATTRS:
                data.pop(attr, None)

    for selected in select_candidate_edges(target, scenario, required_nodes=required_nodes):
        edge_data = target.edges[selected.edge]
        edge_data["disruption_scenario_id"] = scenario.scenario_id
        edge_data["disruption_family"] = scenario.family
        edge_data["disruption_reason_category"] = selected.reason_category
        edge_data["disruption_selection_rank"] = selected.rank
        edge_data["disruption_mode"] = scenario.disruption_mode
        edge_data["disruption_capacity_factor"] = scenario.edge_disruption.capacity_factor
    return target


def _scenario_from_row(row: Mapping[str, str], row_number: int) -> DisruptionScenario:
    if None in row:
        raise ValueError(f"row {row_number} has extra CSV values without headers")

    bbox = _bbox_from_row(row, row_number)
    return DisruptionScenario(
        scenario_id=_required_row_text(row, "scenario_id", row_number),
        region_id=_required_row_text(row, "region_id", row_number),
        family=_required_row_text(row, "family", row_number),
        label=_required_row_text(row, "label", row_number),
        selection_method=_required_row_text(row, "selection_method", row_number),
        target_segment=_required_row_text(row, "target_segment", row_number),
        disruption_mode=_required_row_text(row, "disruption_mode", row_number),
        capacity_factor=_row_float(row, "capacity_factor", row_number),
        p_fail_scale=_row_float(row, "p_fail_scale", row_number),
        max_edges=_optional_row_int(row, "max_edges", row_number),
        hazard_bbox=bbox,
        evidence_class=_required_row_text(row, "evidence_class", row_number),
        observed_disaster_data=_row_bool(row, "observed_disaster_data", row_number),
        notes=str(row.get("notes", "") or "").strip(),
    )


def _validate_csv_header(fieldnames: Sequence[str] | None, filepath: Path) -> None:
    if fieldnames is None:
        raise ValueError(f"{filepath} has no CSV header")
    missing = [column for column in CSV_COLUMNS if column not in fieldnames]
    if missing:
        raise ValueError(f"{filepath} missing required columns: {', '.join(missing)}")


def _row_has_content(row: Mapping[str, Any]) -> bool:
    return any(str(value or "").strip() for value in row.values())


def _required_row_text(row: Mapping[str, str], field: str, row_number: int) -> str:
    value = str(row.get(field, "") or "").strip()
    if not value:
        raise ValueError(f"row {row_number} field {field!r} must be non-empty")
    return value


def _row_float(row: Mapping[str, str], field: str, row_number: int) -> float:
    text = _required_row_text(row, field, row_number)
    return _finite_float(text, f"row {row_number} field {field}")


def _optional_row_float(
    row: Mapping[str, str],
    field: str,
    row_number: int,
) -> float | None:
    text = str(row.get(field, "") or "").strip()
    if not text:
        return None
    return _finite_float(text, f"row {row_number} field {field}")


def _optional_row_int(row: Mapping[str, str], field: str, row_number: int) -> int | None:
    text = str(row.get(field, "") or "").strip()
    if not text:
        return None
    return _positive_int(text, f"row {row_number} field {field}")


def _row_bool(row: Mapping[str, str], field: str, row_number: int) -> bool:
    text = _required_row_text(row, field, row_number).lower()
    if text in {"false", "f", "no", "n", "0"}:
        return False
    if text in {"true", "t", "yes", "y", "1"}:
        return True
    raise ValueError(f"row {row_number} field {field!r} must be boolean text")


def _bbox_from_row(row: Mapping[str, str], row_number: int) -> HazardBbox | None:
    fields = (
        "hazard_bbox_west",
        "hazard_bbox_south",
        "hazard_bbox_east",
        "hazard_bbox_north",
    )
    values = tuple(_optional_row_float(row, field, row_number) for field in fields)
    if all(value is None for value in values):
        return None
    if any(value is None for value in values):
        raise ValueError(f"row {row_number} must provide all hazard bbox fields or none")
    return _validate_bbox(values)  # type: ignore[arg-type]


def _validate_scenario(scenario: DisruptionScenario) -> None:
    if scenario.family not in ALLOWED_FAMILIES:
        raise ValueError(f"unknown disruption family: {scenario.family!r}")
    if scenario.disruption_mode not in ALLOWED_DISRUPTION_MODES:
        raise ValueError(f"unknown disruption_mode: {scenario.disruption_mode!r}")
    if scenario.selection_method not in ALLOWED_SELECTION_METHODS:
        raise ValueError(f"unknown selection_method: {scenario.selection_method!r}")
    if scenario.selection_method not in FAMILY_SELECTION_METHODS[scenario.family]:
        allowed = ", ".join(sorted(FAMILY_SELECTION_METHODS[scenario.family]))
        raise ValueError(
            f"family {scenario.family!r} must use selection_method {allowed}; "
            f"got {scenario.selection_method!r}"
        )
    if scenario.capacity_factor < 0.0 or scenario.capacity_factor > 1.0:
        raise ValueError("capacity_factor must satisfy 0 <= factor <= 1")
    if scenario.disruption_mode == "capacity_reduction" and scenario.capacity_factor <= 0.0:
        raise ValueError("capacity_reduction scenarios require capacity_factor > 0")
    if scenario.p_fail_scale < 0.0:
        raise ValueError("p_fail_scale must be non-negative")
    if scenario.selection_method == "shortest_path" and "->" not in scenario.target_segment:
        raise ValueError("shortest_path scenarios require target_segment like 'A->D'")
    if scenario.selection_method == "bbox_midpoint" and scenario.hazard_bbox is None:
        raise ValueError("bbox_midpoint scenarios require hazard bbox fields")
    if scenario.family == "spatial_hazard_overlay":
        if scenario.evidence_class != "scenario_based" or scenario.observed_disaster_data:
            raise ValueError(
                "spatial_hazard_overlay rows must be scenario_based and "
                "observed_disaster_data=false"
            )


def _validate_mapping_graph(graph: nx.DiGraph, scenario: DisruptionScenario) -> None:
    if graph.is_multigraph():
        raise ValueError("disruption scenario mapping expects a simulator DiGraph, not a MultiGraph")
    graph_region_id = graph.graph.get("region_id")
    if graph_region_id is not None and str(graph_region_id) != scenario.region_id:
        raise ValueError(
            f"scenario region_id {scenario.region_id!r} does not match graph region_id "
            f"{graph_region_id!r}"
        )


def _normalize_required_nodes(
    required_nodes: Mapping[str, Any] | Sequence[Any] | None,
) -> dict[str, Any]:
    if required_nodes is None:
        return dict(DEFAULT_REQUIRED_NODES)
    if isinstance(required_nodes, Mapping):
        aliases = {
            "A": "assembly",
            "D": "destination",
            "S": "rail_access",
            "R": "rail_egress",
        }
        normalized = dict(DEFAULT_REQUIRED_NODES)
        for key, value in required_nodes.items():
            normalized[aliases.get(str(key), str(key))] = value
        return normalized
    if isinstance(required_nodes, (str, bytes)) or len(required_nodes) != 4:
        raise ValueError("required_nodes must be a mapping or a four-item sequence")
    assembly, destination, rail_access, rail_egress = required_nodes
    return {
        "assembly": assembly,
        "destination": destination,
        "rail_access": rail_access,
        "rail_egress": rail_egress,
    }


def _select_hash_rank_edges(graph: nx.DiGraph, scenario: DisruptionScenario) -> list[Edge]:
    edges = _road_edges(graph, include_connectors=False)
    return sorted(edges, key=lambda edge: _stable_hash_key(graph, scenario, edge))


def _select_critical_link_edges(graph: nx.DiGraph, scenario: DisruptionScenario) -> list[Edge]:
    road_graph = _road_subgraph(graph, include_connectors=False)
    scores = nx.edge_betweenness_centrality(road_graph, normalized=True, weight="t0")
    return sorted(
        _road_edges(graph, include_connectors=False),
        key=lambda edge: (-float(scores.get(edge, 0.0)), _edge_sort_key(graph, edge)),
    )


def _select_shortest_path_edges(
    graph: nx.DiGraph,
    scenario: DisruptionScenario,
    required_nodes: Mapping[str, Any],
) -> list[Edge]:
    source, target = _parse_target_segment(scenario.target_segment, required_nodes, graph)
    road_graph = _road_subgraph(graph, include_connectors=True)
    try:
        path = nx.shortest_path(road_graph, source, target, weight="t0")
    except (nx.NetworkXNoPath, nx.NodeNotFound) as exc:
        raise ValueError(
            f"scenario {scenario.scenario_id!r} has no road path {source!r}->{target!r}"
        ) from exc
    return list(zip(path, path[1:]))


def _select_station_access_edges(
    graph: nx.DiGraph,
    scenario: DisruptionScenario,
    required_nodes: Mapping[str, Any],
) -> list[Edge]:
    station_nodes = [
        _resolve_target_node(part.strip(), required_nodes, graph)
        for part in scenario.target_segment.split(",")
        if part.strip()
    ]
    if not station_nodes:
        raise ValueError("station_access scenarios require station target nodes")

    edges: set[Edge] = set()
    for station_node in station_nodes:
        nearby_nodes = {station_node}
        snapped = graph.nodes[station_node].get("snapped_road_node")
        if snapped is not None and snapped in graph:
            nearby_nodes.add(snapped)
        for node in nearby_nodes:
            edges.update(_incident_road_edges(graph, node, include_connectors=True))
    return sorted(edges, key=lambda edge: _edge_sort_key(graph, edge))


def _select_bbox_edges(graph: nx.DiGraph, scenario: DisruptionScenario) -> list[Edge]:
    if scenario.hazard_bbox is None:
        raise ValueError(f"scenario {scenario.scenario_id!r} has no hazard bbox")
    edges = [
        edge
        for edge in _road_edges(graph, include_connectors=False)
        if _edge_intersects_bbox(graph, edge, scenario.hazard_bbox)
    ]
    center = _bbox_center(scenario.hazard_bbox)
    return sorted(
        edges,
        key=lambda edge: (_edge_center_distance_sq(graph, edge, center), _edge_sort_key(graph, edge)),
    )


def _limit_edges(edges: Sequence[Edge], max_edges: int | None) -> list[Edge]:
    if max_edges is None:
        return list(edges)
    return list(edges[:max_edges])


def _scenario_edge(
    graph: nx.DiGraph,
    scenario: DisruptionScenario,
    edge: Edge,
    *,
    rank: int,
) -> ScenarioEdge:
    data = graph.edges[edge]
    realworld_edge_id = data.get("realworld_edge_id")
    source = data.get("source")
    return ScenarioEdge(
        scenario_id=scenario.scenario_id,
        family=scenario.family,
        edge=edge,
        reason_category=scenario.reason_category,
        rank=rank,
        realworld_edge_id=None if realworld_edge_id is None else str(realworld_edge_id),
        mode=str(data.get("mode", "")),
        source=None if source is None else str(source),
    )


def _road_subgraph(graph: nx.DiGraph, *, include_connectors: bool) -> nx.DiGraph:
    return nx.subgraph_view(
        graph,
        filter_edge=lambda u, v: _is_selectable_road_edge(
            graph.edges[u, v],
            include_connectors=include_connectors,
        ),
    )


def _road_edges(graph: nx.DiGraph, *, include_connectors: bool) -> list[Edge]:
    return sorted(
        (
            (u, v)
            for u, v, data in graph.edges(data=True)
            if _is_selectable_road_edge(data, include_connectors=include_connectors)
        ),
        key=lambda edge: _edge_sort_key(graph, edge),
    )


def _is_selectable_road_edge(data: Mapping[str, Any], *, include_connectors: bool) -> bool:
    if data.get("mode") != "road":
        return False
    if include_connectors:
        return True
    if data.get("source") == "connector" or data.get("highway") == "connector":
        return False
    length_m = _optional_finite_float(data.get("length_m"))
    return length_m is None or length_m > 0.0


def _incident_road_edges(
    graph: nx.DiGraph,
    node: Any,
    *,
    include_connectors: bool,
) -> set[Edge]:
    edges: set[Edge] = set()
    for u, v in graph.in_edges(node):
        if _is_selectable_road_edge(graph.edges[u, v], include_connectors=include_connectors):
            edges.add((u, v))
    for u, v in graph.out_edges(node):
        if _is_selectable_road_edge(graph.edges[u, v], include_connectors=include_connectors):
            edges.add((u, v))
    return edges


def _parse_target_segment(
    target_segment: str,
    required_nodes: Mapping[str, Any],
    graph: nx.DiGraph,
) -> tuple[Any, Any]:
    source_text, target_text = [part.strip() for part in target_segment.split("->", maxsplit=1)]
    return (
        _resolve_target_node(source_text, required_nodes, graph),
        _resolve_target_node(target_text, required_nodes, graph),
    )


def _resolve_target_node(
    target: str,
    required_nodes: Mapping[str, Any],
    graph: nx.DiGraph,
) -> Any:
    role_aliases = {
        "A": "assembly",
        "D": "destination",
        "S": "rail_access",
        "R": "rail_egress",
    }
    role = role_aliases.get(target, target)
    node = required_nodes.get(role, target)
    if node not in graph:
        raise ValueError(f"scenario target node {target!r} resolved to missing graph node {node!r}")
    return node


def _edge_intersects_bbox(
    graph: nx.DiGraph,
    edge: Edge,
    bbox: HazardBbox,
) -> bool:
    points = _edge_points(graph, edge)
    if len(points) != 2:
        return False
    midpoint = ((points[0][0] + points[1][0]) / 2.0, (points[0][1] + points[1][1]) / 2.0)
    return any(_point_in_bbox(point, bbox) for point in (*points, midpoint))


def _edge_center_distance_sq(
    graph: nx.DiGraph,
    edge: Edge,
    center: tuple[float, float],
) -> float:
    points = _edge_points(graph, edge)
    if len(points) != 2:
        return float("inf")
    midpoint = ((points[0][0] + points[1][0]) / 2.0, (points[0][1] + points[1][1]) / 2.0)
    return (midpoint[0] - center[0]) ** 2 + (midpoint[1] - center[1]) ** 2


def _edge_points(graph: nx.DiGraph, edge: Edge) -> tuple[tuple[float, float], ...]:
    points: list[tuple[float, float]] = []
    for node in edge:
        data = graph.nodes[node]
        lon = _optional_finite_float(data.get("x"))
        lat = _optional_finite_float(data.get("y"))
        if lon is None or lat is None:
            return ()
        points.append((lon, lat))
    return tuple(points)


def _point_in_bbox(point: tuple[float, float], bbox: HazardBbox) -> bool:
    lon, lat = point
    west, south, east, north = bbox
    return west <= lon <= east and south <= lat <= north


def _bbox_center(bbox: HazardBbox) -> tuple[float, float]:
    west, south, east, north = bbox
    return ((west + east) / 2.0, (south + north) / 2.0)


def _stable_hash_key(
    graph: nx.DiGraph,
    scenario: DisruptionScenario,
    edge: Edge,
) -> tuple[str, tuple[str, str, str]]:
    data = graph.edges[edge]
    edge_id = str(data.get("realworld_edge_id", ""))
    label = f"{edge[0]!r}->{edge[1]!r}"
    digest = hashlib.sha256(
        f"{scenario.scenario_id}|{edge_id}|{label}".encode("utf-8")
    ).hexdigest()
    return (digest, _edge_sort_key(graph, edge))


def _edge_sort_key(graph: nx.DiGraph, edge: Edge) -> tuple[str, str, str]:
    data = graph.edges[edge]
    return (
        str(data.get("realworld_edge_id", "")),
        repr(edge[0]),
        repr(edge[1]),
    )


def _clean_required_text(value: Any, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{name} must be non-empty")
    return text


def _finite_float(value: Any, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite number")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a finite number") from exc
    if not isfinite(number):
        raise ValueError(f"{name} must be a finite number")
    return number


def _optional_finite_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not isfinite(number):
        return None
    return number


def _positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a positive integer")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a positive integer") from exc
    if not isfinite(number) or not number.is_integer() or number < 1:
        raise ValueError(f"{name} must be a positive integer")
    return int(number)


def _validate_bbox(value: Sequence[float]) -> HazardBbox:
    if len(value) != 4:
        raise ValueError("hazard bbox must contain west, south, east, north")
    west, south, east, north = (_finite_float(item, "hazard bbox coordinate") for item in value)
    if east <= west:
        raise ValueError("hazard bbox east must be greater than west")
    if north <= south:
        raise ValueError("hazard bbox north must be greater than south")
    return (west, south, east, north)


mark_candidate_edges = mark_scenario_edges
scenario_to_edge_map = build_scenario_edge_map
scenario_to_disruption_map = build_scenario_disruption_map


__all__ = [
    "ALLOWED_DISRUPTION_MODES",
    "ALLOWED_FAMILIES",
    "ALLOWED_SELECTION_METHODS",
    "CSV_COLUMNS",
    "DEFAULT_REQUIRED_NODES",
    "DEFAULT_SCENARIO_PATH",
    "DisruptionScenario",
    "Edge",
    "HazardBbox",
    "REQUIRED_FAMILIES",
    "SCENARIO_EDGE_ATTRS",
    "ScenarioEdge",
    "assert_required_family_coverage",
    "build_scenario_disruption_map",
    "build_scenario_edge_map",
    "load_disruption_scenarios",
    "mark_candidate_edges",
    "mark_scenario_edges",
    "scenario_family_coverage",
    "scenario_to_disruption_map",
    "scenario_to_edge_map",
    "select_candidate_edges",
    "validate_scenario_table",
]
