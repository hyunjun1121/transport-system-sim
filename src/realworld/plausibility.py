"""Deterministic plausibility checks for adapted real-world pilot graphs.

The helpers in this module inspect an already adapted simulator graph. They do
not call live OSM, routing engines, or web services. The resulting records are
sanity checks for decision-support inputs, not calibrated validation against
ground truth operations.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from math import isfinite
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import urlencode
from urllib.request import urlopen

import networkx as nx

from .zones import approximate_distance_m


PASS = "pass"
WARN = "warn"
FAIL = "fail"
STATUSES = (PASS, WARN, FAIL)
CLAIM_SCOPE = "scaffold_sanity_check_not_ground_truth"
BENCHMARK_CLAIM_SCOPE = "external_or_fallback_benchmark_not_ground_truth"
DEFAULT_FALLBACK_BENCHMARK_METHOD = "documented_fallback_urban_detour_speed"
DEFAULT_FALLBACK_BENCHMARK_SOURCE_CLASS = "documented_executable_fallback"
DEFAULT_FALLBACK_DETOUR_FACTOR = 1.40
DEFAULT_FALLBACK_SPEED_KPH = 35.0
DEFAULT_FALLBACK_ROUTE_ASSUMPTIONS = {
    "route_bus_direct": {"detour_factor": 1.35, "speed_kph": 35.0},
    "route_rail_access": {"detour_factor": 1.45, "speed_kph": 30.0},
    "route_last_mile": {"detour_factor": 1.35, "speed_kph": 35.0},
}
DEFAULT_OSRM_BASE_URL = "https://router.project-osrm.org"
OSRM_BENCHMARK_METHOD = "osrm_route_v1_driving"
OSRM_BENCHMARK_SOURCE_CLASS = "live_external_router_snapshot"

CSV_FIELDS = (
    "region_id",
    "check_id",
    "category",
    "subject",
    "metric",
    "observed_value",
    "unit",
    "status",
    "pass_min",
    "pass_max",
    "warn_min",
    "warn_max",
    "reference_value",
    "reference_unit",
    "reference_source",
    "path",
    "claim_scope",
    "notes",
)

BENCHMARK_CSV_FIELDS = (
    "region_id",
    "benchmark_id",
    "route_check_id",
    "subject",
    "route_label",
    "benchmark_method",
    "source_class",
    "reference_source",
    "reference_version",
    "benchmark_distance_m",
    "benchmark_duration_min",
    "simulator_distance_m",
    "simulator_free_flow_time_min",
    "distance_ratio",
    "distance_status",
    "time_ratio",
    "time_status",
    "status",
    "distance_pass_min",
    "distance_pass_max",
    "distance_warn_min",
    "distance_warn_max",
    "time_pass_min",
    "time_pass_max",
    "time_warn_min",
    "time_warn_max",
    "claim_scope",
    "notes",
)


@dataclass(frozen=True)
class RouteCheck:
    """A road-mode route to inspect in the adapted simulator graph."""

    check_id: str
    source: Any
    target: Any
    label: str


@dataclass(frozen=True)
class PlausibilityRecord:
    """One deterministic validation row for CSV or report output."""

    region_id: str
    check_id: str
    category: str
    subject: str
    metric: str
    observed_value: float
    unit: str
    status: str
    pass_min: float | None = None
    pass_max: float | None = None
    warn_min: float | None = None
    warn_max: float | None = None
    reference_value: float | None = None
    reference_unit: str = ""
    reference_source: str = "scaffold_sanity_range"
    path: tuple[Any, ...] = ()
    claim_scope: str = CLAIM_SCOPE
    notes: str = ""

    def as_csv_row(self) -> dict[str, str]:
        """Return this record using the stable shipped CSV schema."""

        values = {
            "region_id": self.region_id,
            "check_id": self.check_id,
            "category": self.category,
            "subject": self.subject,
            "metric": self.metric,
            "observed_value": _format_float(self.observed_value),
            "unit": self.unit,
            "status": self.status,
            "pass_min": _format_optional_float(self.pass_min),
            "pass_max": _format_optional_float(self.pass_max),
            "warn_min": _format_optional_float(self.warn_min),
            "warn_max": _format_optional_float(self.warn_max),
            "reference_value": _format_optional_float(self.reference_value),
            "reference_unit": self.reference_unit,
            "reference_source": self.reference_source,
            "path": ">".join(str(node) for node in self.path),
            "claim_scope": self.claim_scope,
            "notes": self.notes,
        }
        return {field: values[field] for field in CSV_FIELDS}


@dataclass(frozen=True)
class ExternalRouteBenchmark:
    """One route benchmark from a cached external tool or executable fallback."""

    benchmark_id: str
    route: RouteCheck
    benchmark_distance_m: float
    benchmark_duration_min: float
    method: str = DEFAULT_FALLBACK_BENCHMARK_METHOD
    source_class: str = DEFAULT_FALLBACK_BENCHMARK_SOURCE_CLASS
    reference_source: str = "coordinate_detour_and_urban_speed_fallback"
    reference_version: str = ""
    notes: str = ""


@dataclass(frozen=True)
class ExternalBenchmarkRecord:
    """Comparison between an adapted-graph route and a benchmark route value."""

    region_id: str
    benchmark_id: str
    route_check_id: str
    subject: str
    route_label: str
    benchmark_method: str
    source_class: str
    reference_source: str
    reference_version: str
    benchmark_distance_m: float
    benchmark_duration_min: float
    simulator_distance_m: float
    simulator_free_flow_time_min: float
    distance_ratio: float
    distance_status: str
    time_ratio: float
    time_status: str
    status: str
    distance_pass_min: float
    distance_pass_max: float
    distance_warn_min: float
    distance_warn_max: float
    time_pass_min: float
    time_pass_max: float
    time_warn_min: float
    time_warn_max: float
    claim_scope: str = BENCHMARK_CLAIM_SCOPE
    notes: str = ""

    def as_csv_row(self) -> dict[str, str]:
        """Return this record using the stable shipped benchmark CSV schema."""

        values = {
            "region_id": self.region_id,
            "benchmark_id": self.benchmark_id,
            "route_check_id": self.route_check_id,
            "subject": self.subject,
            "route_label": self.route_label,
            "benchmark_method": self.benchmark_method,
            "source_class": self.source_class,
            "reference_source": self.reference_source,
            "reference_version": self.reference_version,
            "benchmark_distance_m": _format_float(self.benchmark_distance_m),
            "benchmark_duration_min": _format_float(self.benchmark_duration_min),
            "simulator_distance_m": _format_float(self.simulator_distance_m),
            "simulator_free_flow_time_min": _format_float(
                self.simulator_free_flow_time_min
            ),
            "distance_ratio": _format_float(self.distance_ratio),
            "distance_status": self.distance_status,
            "time_ratio": _format_float(self.time_ratio),
            "time_status": self.time_status,
            "status": self.status,
            "distance_pass_min": _format_float(self.distance_pass_min),
            "distance_pass_max": _format_float(self.distance_pass_max),
            "distance_warn_min": _format_float(self.distance_warn_min),
            "distance_warn_max": _format_float(self.distance_warn_max),
            "time_pass_min": _format_float(self.time_pass_min),
            "time_pass_max": _format_float(self.time_pass_max),
            "time_warn_min": _format_float(self.time_warn_min),
            "time_warn_max": _format_float(self.time_warn_max),
            "claim_scope": self.claim_scope,
            "notes": self.notes,
        }
        return {field: values[field] for field in BENCHMARK_CSV_FIELDS}


DEFAULT_ROUTE_CHECKS = (
    RouteCheck("route_bus_direct", "A", "D", "bus direct road leg"),
    RouteCheck("route_rail_access", "A", "S", "assembly to rail access road leg"),
    RouteCheck("route_last_mile", "R", "D", "rail egress to destination road leg"),
)

DEFAULT_CONNECTOR_POINTS = ("A", "D", "S", "R")


def classify_value(
    value: Any,
    *,
    pass_min: float | None = None,
    pass_max: float | None = None,
    warn_min: float | None = None,
    warn_max: float | None = None,
) -> str:
    """Classify a numeric value as pass, warn, or fail by nested bounds.

    Values inside the pass interval pass. Values outside the pass interval but
    still inside the wider warn interval warn. Non-finite values or values
    outside the warn interval fail.
    """

    parsed = _finite_float(value)
    if parsed is None:
        return FAIL
    if warn_min is not None and parsed < warn_min:
        return FAIL
    if warn_max is not None and parsed > warn_max:
        return FAIL
    if pass_min is not None and parsed < pass_min:
        return WARN
    if pass_max is not None and parsed > pass_max:
        return WARN
    return PASS


def evaluate_graph_plausibility(
    graph: nx.DiGraph,
    *,
    region_id: str | None = None,
    routes: Sequence[RouteCheck] = DEFAULT_ROUTE_CHECKS,
    connector_points: Sequence[Any] = DEFAULT_CONNECTOR_POINTS,
) -> tuple[PlausibilityRecord, ...]:
    """Return deterministic route, connector, and edge-attribute checks."""

    resolved_region_id = region_id or str(graph.graph.get("region_id", "unknown_region"))
    records: list[PlausibilityRecord] = []
    for route in routes:
        records.extend(evaluate_route_check(graph, route, region_id=resolved_region_id))
    records.extend(
        evaluate_connector_checks(
            graph,
            connector_points=connector_points,
            region_id=resolved_region_id,
        )
    )
    records.extend(evaluate_road_attribute_checks(graph, region_id=resolved_region_id))
    return tuple(records)


def build_fallback_route_benchmarks(
    graph: nx.DiGraph,
    *,
    routes: Sequence[RouteCheck] = DEFAULT_ROUTE_CHECKS,
    route_assumptions: Mapping[str, Mapping[str, float]] | None = None,
) -> tuple[ExternalRouteBenchmark, ...]:
    """Build deterministic route benchmarks when no external router is cached.

    This fallback is intentionally independent of adapted route topology: it
    uses only endpoint coordinates, a documented detour factor, and a coarse
    urban free-flow speed. It is a benchmark-style plausibility check, not a
    replacement for OSRM, Valhalla, routingpy, R5, OpenTripPlanner, or UXsim.
    """

    assumptions_by_route = route_assumptions or DEFAULT_FALLBACK_ROUTE_ASSUMPTIONS
    benchmarks: list[ExternalRouteBenchmark] = []
    for route in routes:
        route_assumptions = assumptions_by_route.get(route.check_id, {})
        detour_factor = float(
            route_assumptions.get("detour_factor", DEFAULT_FALLBACK_DETOUR_FACTOR)
        )
        speed_kph = float(
            route_assumptions.get("speed_kph", DEFAULT_FALLBACK_SPEED_KPH)
        )
        straight_m = _straight_line_distance_m(graph, route.source, route.target)
        benchmark_distance_m = (
            float("nan") if straight_m is None else straight_m * detour_factor
        )
        benchmark_duration_min = _duration_min_from_distance_speed(
            benchmark_distance_m,
            speed_kph,
        )
        benchmarks.append(
            ExternalRouteBenchmark(
                benchmark_id=f"{route.check_id}_fallback",
                route=route,
                benchmark_distance_m=benchmark_distance_m,
                benchmark_duration_min=benchmark_duration_min,
                notes=(
                    "documented offline fallback; "
                    f"straight_line_m={_format_optional_float(straight_m)}, "
                    f"detour_factor={detour_factor:.2f}, "
                    f"speed_kph={speed_kph:.1f}"
                ),
            )
        )
    return tuple(benchmarks)


def build_osrm_route_benchmarks(
    graph: nx.DiGraph,
    *,
    routes: Sequence[RouteCheck] = DEFAULT_ROUTE_CHECKS,
    base_url: str = DEFAULT_OSRM_BASE_URL,
    timeout_s: float = 20.0,
    fetch_json: Any | None = None,
) -> tuple[ExternalRouteBenchmark, ...]:
    """Build route benchmarks from the OSRM public route API.

    This function is intentionally optional and should not be used in default
    tests. Generated values are still plausibility benchmarks, not ground truth.
    """

    fetcher = fetch_json or _fetch_json_url
    benchmarks: list[ExternalRouteBenchmark] = []
    clean_base = str(base_url).rstrip("/")
    for route in routes:
        source_lon, source_lat = _node_lon_lat(graph, route.source)
        target_lon, target_lat = _node_lon_lat(graph, route.target)
        coordinates = (
            f"{source_lon:.7f},{source_lat:.7f};"
            f"{target_lon:.7f},{target_lat:.7f}"
        )
        query = urlencode(
            {
                "overview": "false",
                "alternatives": "false",
                "steps": "false",
            }
        )
        url = f"{clean_base}/route/v1/driving/{coordinates}?{query}"
        payload = fetcher(url, timeout_s)
        try:
            route_payload = payload["routes"][0]
            distance_m = float(route_payload["distance"])
            duration_min = float(route_payload["duration"]) / 60.0
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise ValueError(f"OSRM response does not contain route metrics for {route.check_id}") from exc
        benchmarks.append(
            ExternalRouteBenchmark(
                benchmark_id=f"{route.check_id}_osrm",
                route=route,
                benchmark_distance_m=distance_m,
                benchmark_duration_min=duration_min,
                method=OSRM_BENCHMARK_METHOD,
                source_class=OSRM_BENCHMARK_SOURCE_CLASS,
                reference_source=clean_base,
                reference_version="live_snapshot_unpinned",
                notes=(
                    "optional live OSRM route API snapshot; not ground truth; "
                    f"url={url}"
                ),
            )
        )
    return tuple(benchmarks)


def evaluate_external_route_benchmarks(
    graph: nx.DiGraph,
    benchmarks: Sequence[ExternalRouteBenchmark],
    *,
    region_id: str | None = None,
    distance_pass_min: float = 0.75,
    distance_pass_max: float = 1.50,
    distance_warn_min: float = 0.50,
    distance_warn_max: float = 2.50,
    time_pass_min: float = 0.33,
    time_pass_max: float = 2.50,
    time_warn_min: float = 0.20,
    time_warn_max: float = 4.00,
) -> tuple[ExternalBenchmarkRecord, ...]:
    """Compare adapted route metrics with cached or fallback benchmarks."""

    resolved_region_id = region_id or str(graph.graph.get("region_id", "unknown_region"))
    road_graph = _road_mode_view(graph)
    records: list[ExternalBenchmarkRecord] = []
    for benchmark in benchmarks:
        route = benchmark.route
        subject = f"{route.source}->{route.target}"
        has_route = _has_path(road_graph, route.source, route.target)
        if has_route:
            distance_path = tuple(
                nx.shortest_path(road_graph, route.source, route.target, weight="length_m")
            )
            time_path = tuple(
                nx.shortest_path(road_graph, route.source, route.target, weight="t0")
            )
            simulator_distance_m = _path_sum(road_graph, distance_path, "length_m")
            simulator_time_min = _path_sum(road_graph, time_path, "t0")
            notes = benchmark.notes
        else:
            simulator_distance_m = float("nan")
            simulator_time_min = float("nan")
            notes = _append_note(benchmark.notes, "simulator road route unavailable")

        distance_ratio = _ratio(simulator_distance_m, benchmark.benchmark_distance_m)
        time_ratio = _ratio(simulator_time_min, benchmark.benchmark_duration_min)
        distance_status = classify_value(
            distance_ratio,
            pass_min=distance_pass_min,
            pass_max=distance_pass_max,
            warn_min=distance_warn_min,
            warn_max=distance_warn_max,
        )
        time_status = classify_value(
            time_ratio,
            pass_min=time_pass_min,
            pass_max=time_pass_max,
            warn_min=time_warn_min,
            warn_max=time_warn_max,
        )
        status = _combine_statuses((distance_status, time_status))
        if not has_route:
            status = FAIL

        records.append(
            ExternalBenchmarkRecord(
                region_id=resolved_region_id,
                benchmark_id=benchmark.benchmark_id,
                route_check_id=route.check_id,
                subject=subject,
                route_label=route.label,
                benchmark_method=benchmark.method,
                source_class=benchmark.source_class,
                reference_source=benchmark.reference_source,
                reference_version=benchmark.reference_version,
                benchmark_distance_m=benchmark.benchmark_distance_m,
                benchmark_duration_min=benchmark.benchmark_duration_min,
                simulator_distance_m=simulator_distance_m,
                simulator_free_flow_time_min=simulator_time_min,
                distance_ratio=distance_ratio,
                distance_status=distance_status,
                time_ratio=time_ratio,
                time_status=time_status,
                status=status,
                distance_pass_min=distance_pass_min,
                distance_pass_max=distance_pass_max,
                distance_warn_min=distance_warn_min,
                distance_warn_max=distance_warn_max,
                time_pass_min=time_pass_min,
                time_pass_max=time_pass_max,
                time_warn_min=time_warn_min,
                time_warn_max=time_warn_max,
                notes=notes,
            )
        )
    return tuple(records)


def evaluate_route_check(
    graph: nx.DiGraph,
    route: RouteCheck,
    *,
    region_id: str | None = None,
) -> tuple[PlausibilityRecord, ...]:
    """Inspect one road-mode route for distance and free-flow-time plausibility."""

    resolved_region_id = region_id or str(graph.graph.get("region_id", "unknown_region"))
    subject = f"{route.source}->{route.target}"
    road_graph = _road_mode_view(graph)
    has_route = _has_path(road_graph, route.source, route.target)
    records: list[PlausibilityRecord] = [
        _record(
            region_id=resolved_region_id,
            check_id=f"{route.check_id}_available",
            category="route",
            subject=subject,
            metric="road_route_available",
            observed_value=1.0 if has_route else 0.0,
            unit="binary",
            pass_min=1.0,
            pass_max=1.0,
            warn_min=1.0,
            warn_max=1.0,
            reference_source="adapter_road_mode_routeability",
            notes=route.label,
        )
    ]
    if not has_route:
        return tuple(records)

    distance_path = tuple(nx.shortest_path(road_graph, route.source, route.target, weight="length_m"))
    time_path = tuple(nx.shortest_path(road_graph, route.source, route.target, weight="t0"))
    distance_m = _path_sum(road_graph, distance_path, "length_m")
    time_min = _path_sum(road_graph, time_path, "t0")
    time_path_distance_m = _path_sum(road_graph, time_path, "length_m")
    straight_m = _straight_line_distance_m(graph, route.source, route.target)

    records.append(
        _record(
            region_id=resolved_region_id,
            check_id=f"{route.check_id}_distance",
            category="route",
            subject=subject,
            metric="route_distance_m",
            observed_value=distance_m,
            unit="m",
            pass_min=None if straight_m is None else 0.95 * straight_m,
            pass_max=None if straight_m is None else 3.0 * straight_m,
            warn_min=None if straight_m is None else 0.80 * straight_m,
            warn_max=None if straight_m is None else 6.0 * straight_m,
            reference_value=straight_m,
            reference_unit="m",
            reference_source="straight_line_coordinate_lower_bound",
            path=distance_path,
            notes="adapted graph path length compared with coordinate lower bound",
        )
    )
    records.append(
        _record(
            region_id=resolved_region_id,
            check_id=f"{route.check_id}_free_flow_time",
            category="route",
            subject=subject,
            metric="route_free_flow_time_min",
            observed_value=time_min,
            unit="min",
            pass_min=0.01,
            pass_max=30.0,
            warn_min=0.001,
            warn_max=90.0,
            reference_source="scaffold_local_trip_time_sanity_range",
            path=time_path,
            notes="uses adapted edge t0 values only",
        )
    )

    implied_speed = _implied_speed_kph(time_path_distance_m, time_min)
    records.append(
        _record(
            region_id=resolved_region_id,
            check_id=f"{route.check_id}_implied_speed",
            category="route",
            subject=subject,
            metric="route_implied_free_flow_speed_kph",
            observed_value=implied_speed,
            unit="kph",
            pass_min=10.0,
            pass_max=70.0,
            warn_min=5.0,
            warn_max=100.0,
            reference_source="urban_road_free_flow_sanity_range",
            path=time_path,
            notes="sanity range only not calibration",
        )
    )
    return tuple(records)


def evaluate_connector_checks(
    graph: nx.DiGraph,
    *,
    connector_points: Sequence[Any] = DEFAULT_CONNECTOR_POINTS,
    region_id: str | None = None,
) -> tuple[PlausibilityRecord, ...]:
    """Check snap connector distances for canonical region points."""

    resolved_region_id = region_id or str(graph.graph.get("region_id", "unknown_region"))
    records: list[PlausibilityRecord] = []
    for point_id in connector_points:
        data = graph.nodes[point_id] if point_id in graph else {}
        distance_m = _finite_float(data.get("connector_distance_m"))
        records.append(
            _record(
                region_id=resolved_region_id,
                check_id=f"connector_{point_id}_distance",
                category="connector",
                subject=str(point_id),
                metric="connector_distance_m",
                observed_value=float("nan") if distance_m is None else distance_m,
                unit="m",
                pass_min=0.0,
                pass_max=250.0,
                warn_min=0.0,
                warn_max=1500.0,
                reference_source="snap_distance_scaffold_sanity_range",
                notes="distance from region point to snapped road node",
            )
        )
    return tuple(records)


def evaluate_road_attribute_checks(
    graph: nx.DiGraph,
    *,
    region_id: str | None = None,
) -> tuple[PlausibilityRecord, ...]:
    """Check coarse speed and capacity ranges on non-connector road edges."""

    resolved_region_id = region_id or str(graph.graph.get("region_id", "unknown_region"))
    road_edges = [
        data
        for _, _, data in graph.edges(data=True)
        if data.get("mode") == "road" and data.get("source") != "connector"
    ]
    speeds = [_finite_float(data.get("speed_kph")) for data in road_edges]
    capacities = [_finite_float(data.get("capacity")) for data in road_edges]
    finite_speeds = [value for value in speeds if value is not None]
    finite_capacities = [value for value in capacities if value is not None]

    records = [
        _record(
            region_id=resolved_region_id,
            check_id="road_edge_count",
            category="edge_attributes",
            subject="non_connector_road_edges",
            metric="road_edge_count",
            observed_value=float(len(road_edges)),
            unit="edges",
            pass_min=1.0,
            warn_min=1.0,
            reference_source="adapted_graph_edge_inventory",
            notes="connectors excluded from road default checks",
        ),
        _range_record(
            region_id=resolved_region_id,
            check_id="road_edge_min_speed",
            metric="road_edge_min_speed_kph",
            value=min(finite_speeds) if finite_speeds else float("nan"),
            unit="kph",
            pass_min=10.0,
            pass_max=80.0,
            warn_min=5.0,
            warn_max=120.0,
            notes="minimum non-connector road speed proxy",
        ),
        _range_record(
            region_id=resolved_region_id,
            check_id="road_edge_max_speed",
            metric="road_edge_max_speed_kph",
            value=max(finite_speeds) if finite_speeds else float("nan"),
            unit="kph",
            pass_min=10.0,
            pass_max=80.0,
            warn_min=5.0,
            warn_max=120.0,
            notes="maximum non-connector road speed proxy",
        ),
        _range_record(
            region_id=resolved_region_id,
            check_id="road_edge_min_capacity",
            metric="road_edge_min_capacity_vph",
            value=min(finite_capacities) if finite_capacities else float("nan"),
            unit="veh_per_hour",
            pass_min=100.0,
            pass_max=2500.0,
            warn_min=50.0,
            warn_max=4000.0,
            notes="minimum non-connector road capacity proxy",
        ),
        _range_record(
            region_id=resolved_region_id,
            check_id="road_edge_max_capacity",
            metric="road_edge_max_capacity_vph",
            value=max(finite_capacities) if finite_capacities else float("nan"),
            unit="veh_per_hour",
            pass_min=100.0,
            pass_max=2500.0,
            warn_min=50.0,
            warn_max=4000.0,
            notes="maximum non-connector road capacity proxy",
        ),
    ]
    return tuple(records)


def status_counts(records: Iterable[PlausibilityRecord]) -> dict[str, int]:
    """Return pass/warn/fail counts for a record collection."""

    counts = {status: 0 for status in STATUSES}
    for record in records:
        counts[record.status] = counts.get(record.status, 0) + 1
    return counts


def records_to_csv_rows(
    records: Iterable[PlausibilityRecord],
) -> tuple[dict[str, str], ...]:
    """Convert records to CSV-ready dictionaries with stable field names."""

    return tuple(record.as_csv_row() for record in records)


def benchmark_status_counts(records: Iterable[ExternalBenchmarkRecord]) -> dict[str, int]:
    """Return pass/warn/fail counts for benchmark comparison records."""

    counts = {status: 0 for status in STATUSES}
    for record in records:
        counts[record.status] = counts.get(record.status, 0) + 1
    return counts


def benchmark_records_to_csv_rows(
    records: Iterable[ExternalBenchmarkRecord],
) -> tuple[dict[str, str], ...]:
    """Convert benchmark records to CSV-ready dictionaries."""

    return tuple(record.as_csv_row() for record in records)


def _range_record(
    *,
    region_id: str,
    check_id: str,
    metric: str,
    value: float,
    unit: str,
    pass_min: float,
    pass_max: float,
    warn_min: float,
    warn_max: float,
    notes: str,
) -> PlausibilityRecord:
    return _record(
        region_id=region_id,
        check_id=check_id,
        category="edge_attributes",
        subject="non_connector_road_edges",
        metric=metric,
        observed_value=value,
        unit=unit,
        pass_min=pass_min,
        pass_max=pass_max,
        warn_min=warn_min,
        warn_max=warn_max,
        reference_source="coarse_road_attribute_sanity_range",
        notes=notes,
    )


def _record(
    *,
    region_id: str,
    check_id: str,
    category: str,
    subject: str,
    metric: str,
    observed_value: float,
    unit: str,
    pass_min: float | None = None,
    pass_max: float | None = None,
    warn_min: float | None = None,
    warn_max: float | None = None,
    reference_value: float | None = None,
    reference_unit: str = "",
    reference_source: str = "scaffold_sanity_range",
    path: Sequence[Any] = (),
    notes: str = "",
) -> PlausibilityRecord:
    status = classify_value(
        observed_value,
        pass_min=pass_min,
        pass_max=pass_max,
        warn_min=warn_min,
        warn_max=warn_max,
    )
    return PlausibilityRecord(
        region_id=region_id,
        check_id=check_id,
        category=category,
        subject=subject,
        metric=metric,
        observed_value=observed_value,
        unit=unit,
        status=status,
        pass_min=pass_min,
        pass_max=pass_max,
        warn_min=warn_min,
        warn_max=warn_max,
        reference_value=reference_value,
        reference_unit=reference_unit,
        reference_source=reference_source,
        path=tuple(path),
        notes=notes,
    )


def _road_mode_view(graph: nx.DiGraph) -> nx.DiGraph:
    return nx.subgraph_view(
        graph,
        filter_edge=lambda u, v: graph.edges[u, v].get("mode") == "road",
    )


def _has_path(graph: nx.DiGraph, source: Any, target: Any) -> bool:
    try:
        return nx.has_path(graph, source, target)
    except nx.NodeNotFound:
        return False


def _path_sum(graph: nx.DiGraph, path: Sequence[Any], attr: str) -> float:
    total = 0.0
    for u, v in zip(path, path[1:]):
        value = _finite_float(graph.edges[u, v].get(attr))
        if value is None:
            return float("nan")
        total += value
    return total


def _duration_min_from_distance_speed(distance_m: float, speed_kph: float) -> float:
    parsed_distance = _finite_float(distance_m)
    parsed_speed = _finite_float(speed_kph)
    if parsed_distance is None or parsed_speed is None or parsed_speed <= 0.0:
        return float("nan")
    return (parsed_distance / 1000.0) / parsed_speed * 60.0


def _straight_line_distance_m(
    graph: nx.DiGraph,
    source: Any,
    target: Any,
) -> float | None:
    try:
        source_data = graph.nodes[source]
        target_data = graph.nodes[target]
    except KeyError:
        return None

    source_lon = _finite_float(source_data.get("x"))
    source_lat = _finite_float(source_data.get("y"))
    target_lon = _finite_float(target_data.get("x"))
    target_lat = _finite_float(target_data.get("y"))
    if None in (source_lon, source_lat, target_lon, target_lat):
        return None
    return approximate_distance_m(source_lat, source_lon, target_lat, target_lon)


def _node_lon_lat(graph: nx.DiGraph, node: Any) -> tuple[float, float]:
    try:
        node_data = graph.nodes[node]
    except KeyError as exc:
        raise KeyError(f"node {node!r} is missing from graph") from exc
    lon = _finite_float(node_data.get("x"))
    lat = _finite_float(node_data.get("y"))
    if lon is None or lat is None:
        raise ValueError(f"node {node!r} must have finite x/y lon/lat coordinates")
    return lon, lat


def _fetch_json_url(url: str, timeout_s: float) -> dict[str, Any]:
    with urlopen(url, timeout=float(timeout_s)) as response:  # noqa: S310 - optional user-triggered benchmark URL
        body = response.read().decode("utf-8")
    payload = json.loads(body)
    if not isinstance(payload, dict):
        raise ValueError(f"URL did not return a JSON object: {url}")
    return payload


def _implied_speed_kph(distance_m: float, time_min: float) -> float:
    parsed_distance = _finite_float(distance_m)
    parsed_time = _finite_float(time_min)
    if parsed_distance is None or parsed_time is None or parsed_time <= 0.0:
        return float("nan")
    return (parsed_distance / 1000.0) / (parsed_time / 60.0)


def _ratio(numerator: float, denominator: float) -> float:
    parsed_numerator = _finite_float(numerator)
    parsed_denominator = _finite_float(denominator)
    if (
        parsed_numerator is None
        or parsed_denominator is None
        or parsed_denominator <= 0.0
    ):
        return float("nan")
    return parsed_numerator / parsed_denominator


def _combine_statuses(statuses: Iterable[str]) -> str:
    result = PASS
    for status in statuses:
        if status == FAIL:
            return FAIL
        if status == WARN:
            result = WARN
    return result


def _append_note(base: str, extra: str) -> str:
    if not base:
        return extra
    return f"{base}; {extra}"


def _finite_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if not isfinite(parsed):
        return None
    return parsed


def _format_float(value: float) -> str:
    parsed = _finite_float(value)
    if parsed is None:
        return ""
    return f"{parsed:.6f}"


def _format_optional_float(value: float | None) -> str:
    if value is None:
        return ""
    return _format_float(value)


__all__ = [
    "CLAIM_SCOPE",
    "BENCHMARK_CLAIM_SCOPE",
    "BENCHMARK_CSV_FIELDS",
    "CSV_FIELDS",
    "DEFAULT_CONNECTOR_POINTS",
    "DEFAULT_FALLBACK_BENCHMARK_METHOD",
    "DEFAULT_FALLBACK_BENCHMARK_SOURCE_CLASS",
    "DEFAULT_FALLBACK_DETOUR_FACTOR",
    "DEFAULT_FALLBACK_ROUTE_ASSUMPTIONS",
    "DEFAULT_FALLBACK_SPEED_KPH",
    "DEFAULT_OSRM_BASE_URL",
    "DEFAULT_ROUTE_CHECKS",
    "FAIL",
    "PASS",
    "STATUSES",
    "WARN",
    "ExternalBenchmarkRecord",
    "ExternalRouteBenchmark",
    "OSRM_BENCHMARK_METHOD",
    "OSRM_BENCHMARK_SOURCE_CLASS",
    "PlausibilityRecord",
    "RouteCheck",
    "benchmark_records_to_csv_rows",
    "benchmark_status_counts",
    "build_fallback_route_benchmarks",
    "build_osrm_route_benchmarks",
    "classify_value",
    "evaluate_connector_checks",
    "evaluate_external_route_benchmarks",
    "evaluate_graph_plausibility",
    "evaluate_road_attribute_checks",
    "evaluate_route_check",
    "records_to_csv_rows",
    "status_counts",
]
