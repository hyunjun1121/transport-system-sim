"""Deterministic structured disruption scenarios for real-world graphs.

The helpers in this module map scenario-table rows to simulator graph edges.
They do not claim that any listed hazard is observed disaster data; the default
CSV is a reproducible scenario design for quasi-real resilience experiments.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from itertools import islice
from math import isfinite
from pathlib import Path
from typing import Any, Callable

import networkx as nx

from src.realworld.source_artifacts import file_sha256
from src.sim_types import EdgeDisruption


Edge = tuple[Any, Any]
HazardBbox = tuple[float, float, float, float]

ALLOWED_FAMILIES = frozenset(
    {
        "random",
        "critical_link",
        "access_road",
        "long_haul",
        "last_mile",
        "rail_station_access",
        "spatial_hazard_overlay",
        "rail_service",
        "path_interdiction",
    }
)
REQUIRED_FAMILIES = ALLOWED_FAMILIES - {"rail_service"}
ALLOWED_DISRUPTION_MODES = frozenset({"blocked", "capacity_reduction", "none"})
ALLOWED_SELECTION_METHODS = frozenset(
    {
        "hash_rank",
        "edge_betweenness",
        "shortest_path",
        "shortest_path_time_band",
        "corridor_time_band",
        "station_access",
        "bbox_midpoint",
        "rail_param",
        "path_interdiction",
    }
)
FAMILY_SELECTION_METHODS = {
    "random": frozenset({"hash_rank"}),
    "critical_link": frozenset({"edge_betweenness"}),
    "access_road": frozenset({"shortest_path"}),
    "long_haul": frozenset({"corridor_time_band"}),
    "last_mile": frozenset({"shortest_path"}),
    "rail_station_access": frozenset({"station_access"}),
    "spatial_hazard_overlay": frozenset({"bbox_midpoint"}),
    "rail_service": frozenset({"rail_param"}),
    "path_interdiction": frozenset({"path_interdiction"}),
}
CENTRAL_TRUNK_TARGET_SEGMENT = "A_to_D_corridor_time_band_20_80"
CENTRAL_TRUNK_LOWER_FRACTION = 0.20
CENTRAL_TRUNK_UPPER_FRACTION = 0.80
CSV_COLUMNS = (
    "scenario_id",
    "region_id",
    "family",
    "label",
    "selection_method",
    "target_segment",
    "disruption_mode",
    "capacity_factor",
    "road_travel_time_multiplier",
    "p_fail_scale",
    "max_edges",
    "hazard_bbox_west",
    "hazard_bbox_south",
    "hazard_bbox_east",
    "hazard_bbox_north",
    "rail_travel_time_multiplier",
    "rail_headway_multiplier",
    "rail_capacity_multiplier",
    "evidence_class",
    "observed_disaster_data",
    "duration_min",
    "recovery_profile",
    "temporal_scope",
    "notes",
)
DEFAULT_RECOVERY_PROFILE = "static_full_horizon_no_recovery"
DEFAULT_TEMPORAL_SCOPE = "metadata_only_not_dynamic_recovery"
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
    "disruption_travel_time_multiplier",
)
DEFAULT_SCENARIO_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "scenarios"
    / "disruption_scenarios.csv"
)
DEFAULT_SCENARIO_MANIFEST_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "scenarios"
    / "disruption_scenarios_manifest.json"
)
DEFAULT_SCENARIO_DOC_PATH = (
    Path(__file__).resolve().parents[2] / "docs" / "disruption_scenarios.md"
)
DISRUPTION_SCENARIO_SCOPE = (
    "Phase 6 disruption scenario library only; deterministic scenario-design "
    "metadata for decision-support stress testing, not observed disaster data, "
    "not calibrated disruption probabilities, not dynamic recovery modeling, "
    "not an operational route plan, not publication readiness, not final-study "
    "readiness, and not formal acceptance."
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
    road_travel_time_multiplier: float | None = None
    max_edges: int | None = None
    hazard_bbox: HazardBbox | None = None
    rail_travel_time_multiplier: float | None = None
    rail_headway_multiplier: float | None = None
    rail_capacity_multiplier: float | None = None
    evidence_class: str = "scenario_based"
    observed_disaster_data: bool = False
    duration_min: float | None = None
    recovery_profile: str = DEFAULT_RECOVERY_PROFILE
    temporal_scope: str = DEFAULT_TEMPORAL_SCOPE
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
        object.__setattr__(
            self,
            "recovery_profile",
            _clean_required_text(self.recovery_profile, "recovery_profile"),
        )
        object.__setattr__(
            self,
            "temporal_scope",
            _clean_required_text(self.temporal_scope, "temporal_scope"),
        )

        capacity_factor = _finite_float(self.capacity_factor, "capacity_factor")
        p_fail_scale = _finite_float(self.p_fail_scale, "p_fail_scale")
        object.__setattr__(self, "capacity_factor", capacity_factor)
        object.__setattr__(self, "p_fail_scale", p_fail_scale)
        if self.duration_min is not None:
            duration_min = _finite_float(self.duration_min, "duration_min")
            if duration_min <= 0.0:
                raise ValueError("duration_min must be positive when provided")
            object.__setattr__(self, "duration_min", duration_min)
        if self.max_edges is not None:
            object.__setattr__(self, "max_edges", _positive_int(self.max_edges, "max_edges"))
        if self.hazard_bbox is not None:
            object.__setattr__(self, "hazard_bbox", _validate_bbox(self.hazard_bbox))

        _validate_scenario(self)

    @property
    def reason_category(self) -> str:
        """Return the reason category assigned to selected edges."""

        if self.family in {"access_road", "long_haul", "last_mile"}:
            return f"{self.family}:{self.target_segment}"
        if self.family == "spatial_hazard_overlay":
            return "scenario_based_hazard_overlay"
        return self.family

    @property
    def edge_disruption(self) -> EdgeDisruption:
        """Return the simulator disruption state for selected edges."""

        if self.disruption_mode == "blocked":
            return EdgeDisruption(status="blocked", capacity_factor=0.0)
        multiplier = (
            1.0
            if self.road_travel_time_multiplier is None
            else self.road_travel_time_multiplier
        )
        return EdgeDisruption(
            status="degraded",
            capacity_factor=self.capacity_factor,
            travel_time_multiplier=multiplier,
        )


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


def build_disruption_scenario_manifest(
    scenarios: Sequence[DisruptionScenario],
    *,
    scenario_path: str | Path = DEFAULT_SCENARIO_PATH,
    manifest_path: str | Path = DEFAULT_SCENARIO_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_SCENARIO_DOC_PATH,
    selected_edges: Mapping[str, Sequence[ScenarioEdge]] | None = None,
) -> dict[str, Any]:
    """Return a conservative Phase 6 scenario-library manifest."""

    validate_scenario_table(scenarios)
    scenario_rows = [_scenario_manifest_row(scenario) for scenario in scenarios]
    selected_edge_summary = _selected_edge_summary(selected_edges or {})
    return {
        "schema_version": 1,
        "result_scope": DISRUPTION_SCENARIO_SCOPE,
        "claim_boundary": DISRUPTION_SCENARIO_SCOPE,
        "publication_ready": False,
        "final_study_ready": False,
        "formal_acceptance_evidence": False,
        "can_mark_complete": False,
        "can_support_parameter_evidence_gate": False,
        "can_support_acceptance_gate": False,
        "can_support_publication_gate": False,
        "can_support_final_study_gate": False,
        "row_count": len(scenario_rows),
        "scenario_ids": sorted(row["scenario_id"] for row in scenario_rows),
        "family_counts": _counts(row["family"] for row in scenario_rows),
        "family_checksums": _family_checksums(scenario_rows),
        "selection_method_counts": _counts(row["selection_method"] for row in scenario_rows),
        "disruption_mode_counts": _counts(row["disruption_mode"] for row in scenario_rows),
        "temporal_scope_counts": _counts(row["temporal_scope"] for row in scenario_rows),
        "recovery_profile_counts": _counts(row["recovery_profile"] for row in scenario_rows),
        "observed_disaster_data_count": sum(
            1 for row in scenario_rows if row["observed_disaster_data"]
        ),
        "spatial_overlay_count": sum(
            1 for row in scenario_rows if row["family"] == "spatial_hazard_overlay"
        ),
        "scenario_table_sha256": (
            file_sha256(Path(scenario_path)) if Path(scenario_path).exists() else None
        ),
        "scenario_table_path": _display_path(scenario_path),
        "outputs": {
            "manifest": _display_path(manifest_path),
            "doc": _display_path(doc_path),
        },
        "selected_edges": selected_edge_summary,
        "review_items": [
            "review whether scenario-only disruption treatment remains acceptable or must be replaced with public hazard or incident evidence",
            "review temporal metadata before making any duration or recovery claim",
            "keep rail-headway stress as policy/stress metadata until a first-class runtime disruption override is implemented",
            "regenerate compact/full outputs after any scenario row, family, selected edge, or temporal metadata change",
        ],
        "remaining_blockers": [
            "scenario rows are not observed disaster or incident data",
            "duration and recovery columns are metadata only and are not dynamically applied by the scenario runner",
            "rail-headway disruption and multi-hazard composition are not first-class runtime disruption components",
            "formal parameter and final-study acceptance remain absent",
        ],
    }


def write_disruption_scenario_manifest(
    scenarios: Sequence[DisruptionScenario],
    *,
    scenario_path: str | Path = DEFAULT_SCENARIO_PATH,
    manifest_path: str | Path = DEFAULT_SCENARIO_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_SCENARIO_DOC_PATH,
    selected_edges: Mapping[str, Sequence[ScenarioEdge]] | None = None,
) -> dict[str, Any]:
    """Write Phase 6 manifest and Markdown review document."""

    manifest = build_disruption_scenario_manifest(
        scenarios,
        scenario_path=scenario_path,
        manifest_path=manifest_path,
        doc_path=doc_path,
        selected_edges=selected_edges,
    )
    Path(manifest_path).parent.mkdir(parents=True, exist_ok=True)
    Path(manifest_path).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    Path(doc_path).parent.mkdir(parents=True, exist_ok=True)
    Path(doc_path).write_text(
        build_disruption_scenario_markdown(manifest),
        encoding="utf-8",
    )
    return manifest


def build_disruption_scenario_markdown(manifest: Mapping[str, Any]) -> str:
    """Return a Markdown summary for the Phase 6 scenario library."""

    lines = [
        "# Disruption Scenario Library",
        "",
        str(manifest.get("claim_boundary", DISRUPTION_SCENARIO_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Final-study ready: `{str(manifest.get('final_study_ready', False)).lower()}`",
        f"- Row count: `{manifest.get('row_count', 0)}`",
        f"- Family counts: `{manifest.get('family_counts', {})}`",
        f"- Temporal scope counts: `{manifest.get('temporal_scope_counts', {})}`",
        "",
        "## Family Checksums",
        "",
    ]
    family_checksums = manifest.get("family_checksums", {})
    if isinstance(family_checksums, Mapping):
        for family, checksum in sorted(family_checksums.items()):
            lines.append(f"- `{family}`: `{checksum}`")
    lines.extend(["", "## Selected Edge Summary", ""])
    selected_edges = manifest.get("selected_edges", {})
    if isinstance(selected_edges, Mapping):
        for scenario_id, summary in sorted(selected_edges.items()):
            if not isinstance(summary, Mapping):
                continue
            lines.append(
                f"- `{scenario_id}`: {summary.get('edge_count', 0)} selected edges; "
                f"checksum `{summary.get('selected_edge_checksum', '')}`."
            )
    lines.extend(["", "## Remaining Blockers", ""])
    lines.extend(f"- {item}" for item in manifest.get("remaining_blockers", []))
    lines.append("")
    return "\n".join(lines)


def select_candidate_edges(
    graph: nx.DiGraph,
    scenario: DisruptionScenario,
    *,
    required_nodes: Mapping[str, Any] | Sequence[Any] | None = None,
) -> tuple[ScenarioEdge, ...]:
    """Map one scenario to deterministic candidate graph edges."""

    if scenario.selection_method == "rail_param":
        return ()

    _validate_mapping_graph(graph, scenario)
    node_ids = _normalize_required_nodes(required_nodes)

    if scenario.selection_method == "hash_rank":
        edges = _select_hash_rank_edges(graph, scenario)
    elif scenario.selection_method == "edge_betweenness":
        edges = _select_critical_link_edges(graph, scenario)
    elif scenario.selection_method == "shortest_path":
        edges = _select_shortest_path_edges(graph, scenario, node_ids)
    elif scenario.selection_method == "shortest_path_time_band":
        edges = list(
            select_shortest_path_time_band_edges(
                graph,
                source=node_ids["assembly"],
                target=node_ids["destination"],
                lower_fraction=CENTRAL_TRUNK_LOWER_FRACTION,
                upper_fraction=CENTRAL_TRUNK_UPPER_FRACTION,
            )
        )
    elif scenario.selection_method == "corridor_time_band":
        edges = list(
            select_corridor_time_band_edges(
                graph,
                source=node_ids["assembly"],
                target=node_ids["destination"],
                lower_fraction=CENTRAL_TRUNK_LOWER_FRACTION,
                upper_fraction=CENTRAL_TRUNK_UPPER_FRACTION,
            )
        )
    elif scenario.selection_method == "station_access":
        edges = _select_station_access_edges(graph, scenario, node_ids)
    elif scenario.selection_method == "bbox_midpoint":
        edges = _select_bbox_edges(graph, scenario)
    elif scenario.selection_method == "path_interdiction":
        edges = _select_path_interdiction_edges(graph, scenario, node_ids)
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
        edge_data["disruption_travel_time_multiplier"] = (
            scenario.edge_disruption.travel_time_multiplier
        )
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
        road_travel_time_multiplier=_optional_row_float(
            row, "road_travel_time_multiplier", row_number,
        ),
        max_edges=_optional_row_int(row, "max_edges", row_number),
        hazard_bbox=bbox,
        rail_travel_time_multiplier=_optional_row_float(
            row, "rail_travel_time_multiplier", row_number,
        ),
        rail_headway_multiplier=_optional_row_float(
            row, "rail_headway_multiplier", row_number,
        ),
        rail_capacity_multiplier=_optional_row_float(
            row, "rail_capacity_multiplier", row_number,
        ),
        evidence_class=_required_row_text(row, "evidence_class", row_number),
        observed_disaster_data=_row_bool(row, "observed_disaster_data", row_number),
        duration_min=_optional_row_float(row, "duration_min", row_number),
        recovery_profile=_optional_row_text(
            row,
            "recovery_profile",
            default=DEFAULT_RECOVERY_PROFILE,
        ),
        temporal_scope=_optional_row_text(
            row,
            "temporal_scope",
            default=DEFAULT_TEMPORAL_SCOPE,
        ),
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


def _optional_row_text(
    row: Mapping[str, str],
    field: str,
    *,
    default: str,
) -> str:
    text = str(row.get(field, "") or "").strip()
    return text or default


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
    if scenario.family == "rail_service":
        _validate_rail_service_scenario(scenario)
        return
    if scenario.selection_method == "shortest_path" and "->" not in scenario.target_segment:
        raise ValueError("shortest_path scenarios require target_segment like 'A->D'")
    if (
        scenario.selection_method == "corridor_time_band"
        and scenario.target_segment != CENTRAL_TRUNK_TARGET_SEGMENT
    ):
        raise ValueError(
            "corridor_time_band scenarios require target_segment "
            f"{CENTRAL_TRUNK_TARGET_SEGMENT!r}"
        )
    if scenario.selection_method == "bbox_midpoint" and scenario.hazard_bbox is None:
        raise ValueError("bbox_midpoint scenarios require hazard bbox fields")
    if scenario.selection_method == "path_interdiction" and (scenario.max_edges is None or scenario.max_edges < 1):
        raise ValueError("path_interdiction scenarios require max_edges >= 1")
    if scenario.family == "spatial_hazard_overlay":
        if scenario.evidence_class != "scenario_based" or scenario.observed_disaster_data:
            raise ValueError(
                "spatial_hazard_overlay rows must be scenario_based and "
                "observed_disaster_data=false"
            )
    if scenario.family == "path_interdiction":
        if scenario.evidence_class != "scenario_based":
            raise ValueError(
                "path_interdiction rows must be scenario_based"
            )


def _validate_rail_service_scenario(scenario: DisruptionScenario) -> None:
    if scenario.disruption_mode != "none":
        raise ValueError("rail_service scenarios must use disruption_mode 'none'")
    has_rail_knob = any(
        v is not None and v != 1.0
        for v in (
            scenario.rail_travel_time_multiplier,
            scenario.rail_headway_multiplier,
            scenario.rail_capacity_multiplier,
        )
    )
    if not has_rail_knob:
        raise ValueError("rail_service scenarios require at least one rail multiplier != 1.0")


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


def select_shortest_path_time_band_edges(
    graph: nx.DiGraph,
    *,
    source: Any,
    target: Any,
    lower_fraction: float = CENTRAL_TRUNK_LOWER_FRACTION,
    upper_fraction: float = CENTRAL_TRUNK_UPPER_FRACTION,
) -> tuple[Edge, ...]:
    """Select central directed edges of the minimum-free-flow-time road path.

    An edge is selected when its temporal midpoint along the source-to-target
    path falls inside the inclusive ``lower_fraction``--``upper_fraction``
    band.  The selector uses only graph topology and ``t0``; it does not expose
    path-node or coordinate details in any persisted artifact.
    """

    if graph.is_multigraph():
        raise ValueError("shortest-path time-band selection expects a DiGraph")
    lower = _finite_float(lower_fraction, "lower_fraction")
    upper = _finite_float(upper_fraction, "upper_fraction")
    if not (0.0 <= lower < upper <= 1.0):
        raise ValueError(
            "shortest-path time band must satisfy "
            "0 <= lower_fraction < upper_fraction <= 1"
        )

    road_graph = _road_subgraph(graph, include_connectors=True)
    try:
        path = nx.shortest_path(road_graph, source, target, weight="t0")
    except (nx.NetworkXNoPath, nx.NodeNotFound) as exc:
        raise ValueError("shortest-path time-band selector has no road path") from exc

    path_edges = tuple(zip(path, path[1:]))
    if not path_edges:
        raise ValueError("shortest-path time-band selector requires a non-empty road path")

    durations: list[float] = []
    for edge in path_edges:
        duration = _finite_float(graph.edges[edge].get("t0"), "path edge t0")
        if duration <= 0.0:
            raise ValueError("shortest-path time-band path edges require positive finite t0")
        durations.append(duration)

    total = sum(durations)
    lower_time = lower * total
    upper_time = upper * total
    tolerance = 1e-12 * max(1.0, total)
    selected: list[Edge] = []
    elapsed = 0.0
    for edge, duration in zip(path_edges, durations):
        midpoint = elapsed + duration / 2.0
        if (
            lower_time - tolerance <= midpoint <= upper_time + tolerance
            and _is_selectable_road_edge(
                graph.edges[edge], include_connectors=False
            )
        ):
            selected.append(edge)
        elapsed += duration

    if not selected:
        raise ValueError("shortest-path time band selected no central road edges")
    return tuple(selected)


def select_corridor_time_band_edges(
    graph: nx.DiGraph,
    *,
    source: Any,
    target: Any,
    path_count: int | None = None,
    lower_fraction: float = CENTRAL_TRUNK_LOWER_FRACTION,
    upper_fraction: float = CENTRAL_TRUNK_UPPER_FRACTION,
    excluded_endpoint_pairs: Sequence[tuple[Any, Any]] = (
        ("A", "S"),
        ("S", "A"),
        ("R", "D"),
        ("D", "R"),
    ),
) -> tuple[Edge, ...]:
    """Select central physical edges across a declared route envelope.

    The candidate routes use the same hybrid construction as the graph-scope
    builder: up to three exact shortest-simple paths followed by deterministic
    penalty diversification.  Each route contributes physical-road edges whose
    cumulative free-flow-time midpoint lies in the inclusive time band.
    Canonical access and return shortest paths are removed so this stress does
    not silently duplicate feeder or last-mile scenarios.
    """

    if graph.is_multigraph():
        raise ValueError("corridor time-band selection expects a DiGraph")
    lower = _finite_float(lower_fraction, "lower_fraction")
    upper = _finite_float(upper_fraction, "upper_fraction")
    if not (0.0 <= lower < upper <= 1.0):
        raise ValueError(
            "corridor time band must satisfy "
            "0 <= lower_fraction < upper_fraction <= 1"
        )
    count = _corridor_candidate_count(graph, path_count)
    road_graph = _road_subgraph(graph, include_connectors=True)
    paths = hybrid_corridor_candidate_paths(
        road_graph,
        source=source,
        target=target,
        path_count=count,
    )
    if not paths:
        raise ValueError("corridor time-band selector has no road path")

    excluded: set[Edge] = set()
    for endpoint_source, endpoint_target in excluded_endpoint_pairs:
        try:
            endpoint_path = nx.shortest_path(
                road_graph,
                endpoint_source,
                endpoint_target,
                weight="t0",
            )
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            continue
        excluded.update(zip(endpoint_path, endpoint_path[1:]))

    selected: list[Edge] = []
    seen: set[Edge] = set()
    for path in paths:
        for edge in _time_band_edges_for_path(
            graph,
            path,
            lower_fraction=lower,
            upper_fraction=upper,
        ):
            if edge in excluded or edge in seen:
                continue
            seen.add(edge)
            selected.append(edge)

    if not selected:
        raise ValueError("corridor time band selected no central road edges")
    return tuple(selected)


def _corridor_candidate_count(graph: nx.DiGraph, path_count: int | None) -> int:
    raw = graph.graph.get("corridor_path_count", 3) if path_count is None else path_count
    if isinstance(raw, bool):
        raise ValueError("corridor path_count must be a positive integer")
    try:
        numeric = float(raw)
        count = int(numeric)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("corridor path_count must be a positive integer") from exc
    if not isfinite(numeric) or numeric != count or count < 1:
        raise ValueError("corridor path_count must be a positive integer")
    return count


def hybrid_corridor_candidate_paths(
    graph: nx.DiGraph,
    *,
    source: Any,
    target: Any,
    path_count: int,
    seed_paths: Sequence[Sequence[Any]] | None = None,
    progress: Callable[[Mapping[str, Any]], None] | None = None,
    leg_id: str = "",
) -> tuple[tuple[Any, ...], ...]:
    """Build exact-seeded, deterministic penalty-diversified route candidates."""

    if isinstance(path_count, bool) or not isinstance(path_count, int) or path_count < 1:
        raise ValueError("corridor path_count must be a positive integer")
    if seed_paths is None:
        try:
            candidates = nx.shortest_simple_paths(graph, source, target, weight="t0")
            paths = [
                tuple(path)
                for path in islice(candidates, min(3, path_count))
            ]
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return ()
    else:
        paths = [tuple(path) for path in seed_paths]
    if not paths or len(paths) >= path_count:
        return tuple(paths[:path_count])

    seen = set(paths)
    usage: Counter[Edge] = Counter()
    for path in paths:
        usage.update(zip(path, path[1:]))
    first_edges = tuple(zip(paths[0], paths[0][1:]))
    first_cost = sum(
        _finite_float(graph.edges[edge].get("t0"), "candidate edge t0")
        for edge in first_edges
    )
    penalty_unit = max(first_cost * 2.0, 1e-9)
    attempts = 0
    max_attempts = max(12, (path_count - len(paths)) * 4)
    while len(paths) < path_count and attempts < max_attempts:
        attempts += 1

        def penalized_weight(u: Any, v: Any, data: Mapping[str, Any]) -> float:
            base = _finite_float(data.get("t0"), "candidate edge t0")
            return base + penalty_unit * float(usage[(u, v)])

        try:
            candidate = tuple(
                nx.shortest_path(
                    graph,
                    source,
                    target,
                    weight=penalized_weight,
                )
            )
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            break
        candidate_edges = tuple(zip(candidate, candidate[1:]))
        if candidate not in seen:
            paths.append(candidate)
            seen.add(candidate)
            if progress is not None:
                progress(
                    {
                        "event": "penalty_candidate_added",
                        "leg": leg_id,
                        "candidate_count": len(paths),
                        "target_count": path_count,
                        "search_attempt": attempts,
                    }
                )
        usage.update(candidate_edges)
    return tuple(paths)


def _time_band_edges_for_path(
    graph: nx.DiGraph,
    path: Sequence[Any],
    *,
    lower_fraction: float,
    upper_fraction: float,
) -> tuple[Edge, ...]:
    path_edges = tuple(zip(path, path[1:]))
    if not path_edges:
        return ()
    durations = [
        _finite_float(graph.edges[edge].get("t0"), "candidate edge t0")
        for edge in path_edges
    ]
    if any(duration <= 0.0 for duration in durations):
        raise ValueError("corridor time-band path edges require positive finite t0")
    total = sum(durations)
    lower_time = lower_fraction * total
    upper_time = upper_fraction * total
    tolerance = 1e-12 * max(1.0, total)
    selected: list[Edge] = []
    elapsed = 0.0
    for edge, duration in zip(path_edges, durations):
        midpoint = elapsed + duration / 2.0
        if (
            lower_time - tolerance <= midpoint <= upper_time + tolerance
            and _is_selectable_road_edge(
                graph.edges[edge], include_connectors=False
            )
        ):
            selected.append(edge)
        elapsed += duration
    return tuple(selected)


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


def _select_path_interdiction_edges(
    graph: nx.DiGraph, scenario: DisruptionScenario, node_ids: Mapping[str, Any]
) -> list[Edge]:
    """Budget-k shortest-path interdiction (Israeli & Wood 2002).

    Removes k edges from the shortest A->D path to maximize travel-time increase.
    Based on public road network topology (표준노드링크).
    """
    k = scenario.max_edges if scenario.max_edges is not None else 3
    source = str(node_ids["assembly"])
    target = str(node_ids["destination"])
    try:
        shortest_path = nx.shortest_path(graph, source=source, target=target, weight="t0")
    except nx.NetworkXNoPath:
        raise ValueError(f"scenario {scenario.scenario_id!r}: no A->D path exists")
    path_edges = list(zip(shortest_path[:-1], shortest_path[1:]))
    if len(path_edges) <= k:
        return path_edges
    edge_weights = []
    for u, v in path_edges:
        wt = graph[u][v].get("t0", 1.0)
        impact = wt * graph[u][v].get("capacity", 1.0)
        edge_weights.append((impact, (u, v)))
    edge_weights.sort(reverse=True)
    selected = [edge for _, edge in edge_weights[:k]]
    return selected


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


def _scenario_manifest_row(scenario: DisruptionScenario) -> dict[str, Any]:
    return {
        "scenario_id": scenario.scenario_id,
        "region_id": scenario.region_id,
        "family": scenario.family,
        "label": scenario.label,
        "selection_method": scenario.selection_method,
        "target_segment": scenario.target_segment,
        "disruption_mode": scenario.disruption_mode,
        "capacity_factor": scenario.capacity_factor,
        "p_fail_scale": scenario.p_fail_scale,
        "max_edges": scenario.max_edges,
        "hazard_bbox": scenario.hazard_bbox,
        "rail_travel_time_multiplier": scenario.rail_travel_time_multiplier,
        "rail_headway_multiplier": scenario.rail_headway_multiplier,
        "rail_capacity_multiplier": scenario.rail_capacity_multiplier,
        "evidence_class": scenario.evidence_class,
        "observed_disaster_data": scenario.observed_disaster_data,
        "duration_min": scenario.duration_min,
        "recovery_profile": scenario.recovery_profile,
        "temporal_scope": scenario.temporal_scope,
    }


def _family_checksums(rows: Sequence[Mapping[str, Any]]) -> dict[str, str]:
    grouped: dict[str, list[Mapping[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row["family"]), []).append(row)
    return {
        family: _json_digest(sorted(items, key=lambda item: str(item["scenario_id"])))
        for family, items in sorted(grouped.items())
    }


def _selected_edge_summary(
    selected_edges: Mapping[str, Sequence[ScenarioEdge]],
) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for scenario_id, edges in selected_edges.items():
        edge_rows = [
            {
                "edge": [str(selected.edge[0]), str(selected.edge[1])],
                "family": selected.family,
                "rank": selected.rank,
                "realworld_edge_id": selected.realworld_edge_id,
                "reason_category": selected.reason_category,
            }
            for selected in edges
        ]
        summary[scenario_id] = {
            "edge_count": len(edge_rows),
            "selected_edge_ids": [
                str(row["realworld_edge_id"] or "->".join(row["edge"]))
                for row in edge_rows
            ],
            "selected_edge_checksum": _json_digest(edge_rows),
        }
    return summary


def _counts(values: Sequence[str] | Any) -> dict[str, int]:
    return dict(sorted(Counter(str(value) for value in values).items()))


def _json_digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _display_path(path: str | Path) -> str:
    try:
        return str(Path(path).resolve().relative_to(Path(__file__).resolve().parents[2]))
    except ValueError:
        return str(path)


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
    "CENTRAL_TRUNK_LOWER_FRACTION",
    "CENTRAL_TRUNK_TARGET_SEGMENT",
    "CENTRAL_TRUNK_UPPER_FRACTION",
    "CSV_COLUMNS",
    "DEFAULT_RECOVERY_PROFILE",
    "DEFAULT_REQUIRED_NODES",
    "DEFAULT_SCENARIO_DOC_PATH",
    "DEFAULT_SCENARIO_MANIFEST_PATH",
    "DEFAULT_SCENARIO_PATH",
    "DEFAULT_TEMPORAL_SCOPE",
    "DISRUPTION_SCENARIO_SCOPE",
    "DisruptionScenario",
    "Edge",
    "HazardBbox",
    "REQUIRED_FAMILIES",
    "SCENARIO_EDGE_ATTRS",
    "ScenarioEdge",
    "assert_required_family_coverage",
    "build_disruption_scenario_manifest",
    "build_disruption_scenario_markdown",
    "build_scenario_disruption_map",
    "build_scenario_edge_map",
    "hybrid_corridor_candidate_paths",
    "load_disruption_scenarios",
    "mark_candidate_edges",
    "mark_scenario_edges",
    "scenario_family_coverage",
    "scenario_to_disruption_map",
    "scenario_to_edge_map",
    "select_candidate_edges",
    "select_corridor_time_band_edges",
    "select_shortest_path_time_band_edges",
    "validate_scenario_table",
    "write_disruption_scenario_manifest",
]
