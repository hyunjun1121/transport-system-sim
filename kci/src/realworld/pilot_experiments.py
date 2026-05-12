"""Pilot experiment runner for quasi-real transport-resilience profiles.

This module connects the cached pilot GraphML, structured disruption scenario
table, policy-alternative table, and the existing ``run_scenario(...)`` API.
Outputs remain decision-support experiments, not calibrated real-world forecasts
or operational route plans.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from itertools import islice
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import networkx as nx
import yaml

from src import scenario as scenario_module
from src.policies import StrictPolicy
from src.realworld.adapter import build_simulator_graph, realworld_network_config
from src.realworld.disruption_scenarios import (
    DEFAULT_SCENARIO_PATH,
    DisruptionScenario,
    ScenarioEdge,
    load_disruption_scenarios,
    select_candidate_edges,
)
from src.realworld.osm_network import load_graphml
from src.realworld.policy_alternatives import (
    DEFAULT_POLICY_ALTERNATIVES_PATH,
    PolicyAlternative,
    build_policy_config_variant,
    load_policy_alternatives,
)
from src.realworld.road_overrides import (
    build_highway_defaults_with_overrides,
    load_road_class_overrides,
)
from src.realworld.validation import assert_graph_ready


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGION_PATH = PROJECT_ROOT / "data" / "regions" / "pilot_region.yaml"
DEFAULT_CACHE_PATH = PROJECT_ROOT / "data" / "cache" / "pilot_region_road.graphml"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "results" / "realworld_pilot"
DEFAULT_DESIGN_PATH = PROJECT_ROOT / "data" / "manifests" / "pilot_experiment_design.json"
DEFAULT_RESULTS_PATH = DEFAULT_OUTPUT_DIR / "pilot_sample_results.csv"
DEFAULT_SUMMARY_PATH = DEFAULT_OUTPUT_DIR / "pilot_sample_summary.csv"
DEFAULT_MANIFEST_PATH = DEFAULT_OUTPUT_DIR / "pilot_result_manifest.json"
DEFAULT_SAMPLE_MANIFEST_PATH = DEFAULT_OUTPUT_DIR / "pilot_sample_manifest.json"

DEFAULT_SAMPLE_PROFILE_ID = "sample_scaffold"
DEFAULT_STAGED_PROFILE_ID = "staged_pilot"
DEFAULT_FULL_PROFILE_ID = "full_pilot"
DEFAULT_MULTI_CORRIDOR_PROFILE_ID = "multi_corridor_candidate"
DEFAULT_MULTI_CORRIDOR_FULL_PROFILE_ID = "multi_corridor_full_candidate"
RUN_STAGES = frozenset({"sample", "staged", "full"})
GRAPH_REDUCTION_SINGLE_CORRIDOR = "single_corridor"
GRAPH_REDUCTION_MULTI_CORRIDOR = "multi_corridor"
GRAPH_REDUCTION_STRATEGIES = frozenset(
    {GRAPH_REDUCTION_SINGLE_CORRIDOR, GRAPH_REDUCTION_MULTI_CORRIDOR}
)

DEFAULT_SAMPLE_SEEDS = (1101, 1102)
DEFAULT_SAMPLE_POLICY_IDS = (
    "bus_only",
    "baseline_multimodal",
    "multimodal_lastmile_redundancy",
    "staggered_or_adaptive_dispatch",
)
DEFAULT_SAMPLE_SCENARIO_IDS = (
    "no_disruption",
    "songpa_random_capacity_reduction",
    "songpa_critical_link_blockage",
    "songpa_last_mile_station_to_destination",
)
DEFAULT_ROUTE_CORRIDOR_PAIRS = (("A", "D"), ("A", "S"), ("R", "D"))
CLAIM_SCOPE = (
    "Pilot scaffold sample output only; not calibrated real-world results or an "
    "operational forecast."
)
PILOT_STAGED_CLAIM_SCOPE = (
    "Pilot staged scenario-policy-seed output for quasi-real decision-support "
    "evaluation; not calibrated real-world results or an operational forecast."
)
PILOT_FULL_CLAIM_SCOPE = (
    "Pilot full scenario-policy-seed output for quasi-real decision-support "
    "evaluation; not calibrated real-world results or an operational forecast."
)
PILOT_MULTI_CORRIDOR_CANDIDATE_CLAIM_SCOPE = (
    "Pilot multi-corridor candidate output for graph-scale method review; not "
    "calibrated real-world results or an operational forecast."
)
PILOT_MULTI_CORRIDOR_FULL_CANDIDATE_CLAIM_SCOPE = (
    "Pilot full multi-corridor candidate output for graph-scale method review; "
    "not calibrated real-world results or an operational forecast."
)

RESULT_COLUMNS = (
    "region_id",
    "graph_source",
    "policy_id",
    "scenario_id",
    "scenario_family",
    "scenario_type",
    "seed",
    "mode",
    "completion_rate",
    "censored_count",
    "penalized_makespan",
    "makespan",
    "road_vehicle_service_minutes",
    "train_service_minutes",
    "total_service_minutes",
    "passenger_travel_minutes",
    "passengers_per_total_service_minute",
    "first_arrival_time",
    "median_arrival_time",
    "p80_arrival_time",
    "p95_arrival_time",
    "selected_edge_count",
    "selected_realworld_edge_ids",
    "notes",
    "claim_scope",
)
SUMMARY_GROUP_COLUMNS = (
    "region_id",
    "graph_source",
    "policy_id",
    "scenario_id",
    "scenario_family",
    "scenario_type",
    "mode",
)
SUMMARY_COLUMNS = SUMMARY_GROUP_COLUMNS + (
    "run_count",
    "mean_completion_rate",
    "mean_censored_count",
    "mean_penalized_makespan",
    "mean_makespan",
    "mean_road_vehicle_service_minutes",
    "mean_train_service_minutes",
    "mean_total_service_minutes",
    "mean_passenger_travel_minutes",
    "mean_passengers_per_total_service_minute",
    "mean_first_arrival_time",
    "mean_median_arrival_time",
    "mean_p80_arrival_time",
    "mean_p95_arrival_time",
    "claim_scope",
)
METRIC_COLUMNS = (
    "completion_rate",
    "censored_count",
    "penalized_makespan",
    "makespan",
    "road_vehicle_service_minutes",
    "train_service_minutes",
    "total_service_minutes",
    "passenger_travel_minutes",
    "passengers_per_total_service_minute",
    "first_arrival_time",
    "median_arrival_time",
    "p80_arrival_time",
    "p95_arrival_time",
)


@dataclass(frozen=True)
class PilotInputs:
    """Cached pilot input bundle used by the experiment runner."""

    region: Mapping[str, Any]
    graph: nx.DiGraph
    graph_source: str
    source_graph_nodes: int = 0
    source_graph_edges: int = 0

    @property
    def region_id(self) -> str:
        """Return the pilot region identifier."""

        return str(self.region["region_id"])


@dataclass(frozen=True)
class PilotDisruptionCase:
    """One no-disruption or structured disruption case for the runner."""

    scenario_id: str
    scenario_family: str
    scenario_type: str
    failure_mode: str
    capacity_factor: float
    p_fail_scale: float
    selected_edges: tuple[ScenarioEdge, ...] = ()
    notes: str = ""

    @property
    def selected_realworld_edge_ids(self) -> tuple[str, ...]:
        """Return stable selected edge identifiers for result traceability."""

        ids: list[str] = []
        for selected in self.selected_edges:
            if selected.realworld_edge_id:
                ids.append(selected.realworld_edge_id)
            else:
                ids.append(f"{selected.edge[0]!r}->{selected.edge[1]!r}")
        return tuple(ids)


@dataclass(frozen=True)
class PilotExperimentProfile:
    """One named scenario-policy-seed execution profile from the design manifest."""

    profile_id: str
    run_stage: str
    output_prefix: str
    sample_scaffold: bool
    result_scope: str
    design_status: str
    analysis_graph_strategy: str
    reduce_graph: bool
    policy_ids: tuple[str, ...]
    scenario_ids: tuple[str, ...]
    seeds: tuple[int, ...]
    graph_reduction_strategy: str = GRAPH_REDUCTION_SINGLE_CORRIDOR
    corridor_path_count: int = 1
    description: str = ""


@dataclass(frozen=True)
class PilotExperimentDesign:
    """Accepted pilot experiment design metadata loaded from JSON."""

    schema_version: int
    region_id: str
    design_scope: str
    claim_boundary: str
    profiles: Mapping[str, PilotExperimentProfile]
    excluded_policy_ids: Mapping[str, str]


def run_pilot_experiments(
    *,
    region_path: str | Path = DEFAULT_REGION_PATH,
    cache_path: str | Path = DEFAULT_CACHE_PATH,
    scenarios_path: str | Path = DEFAULT_SCENARIO_PATH,
    policies_path: str | Path = DEFAULT_POLICY_ALTERNATIVES_PATH,
    design_path: str | Path = DEFAULT_DESIGN_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    road_class_overrides_path: str | Path | None = None,
    seeds: Sequence[int] | None = None,
    sample: bool = True,
    run_profile: str | None = None,
    policy_ids: Sequence[str] | None = None,
    scenario_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Run a named pilot design profile and write separated CSV plus manifest outputs."""

    design, profile = resolve_pilot_experiment_profile(
        design_path=design_path,
        run_profile=run_profile,
        sample=sample,
    )
    resolved_seeds = tuple(int(seed) for seed in (seeds if seeds is not None else profile.seeds))
    resolved_policy_ids = tuple(policy_ids) if policy_ids is not None else profile.policy_ids
    resolved_scenario_ids = tuple(scenario_ids) if scenario_ids is not None else profile.scenario_ids

    inputs = load_pilot_inputs(
        region_path=region_path,
        cache_path=cache_path,
        road_class_overrides_path=road_class_overrides_path,
        reduce_graph=profile.reduce_graph,
        graph_reduction_strategy=profile.graph_reduction_strategy,
        corridor_path_count=profile.corridor_path_count,
    )
    if design.region_id != inputs.region_id:
        raise ValueError(
            f"design region_id {design.region_id!r} does not match inputs "
            f"region_id {inputs.region_id!r}"
        )
    policies = select_policy_alternatives(
        load_policy_alternatives(policies_path),
        policy_ids=resolved_policy_ids,
        sample=profile.sample_scaffold,
    )
    cases = select_disruption_cases(
        inputs.graph,
        load_disruption_scenarios(scenarios_path, region_id=inputs.region_id),
        scenario_ids=resolved_scenario_ids,
        sample=profile.sample_scaffold,
    )
    rows = run_pilot_rows(
        inputs=inputs,
        policies=policies,
        cases=cases,
        seeds=resolved_seeds,
        claim_scope=profile.result_scope,
    )
    summary_rows = summarize_pilot_rows(rows)

    paths = write_pilot_outputs(
        rows=rows,
        summary_rows=summary_rows,
        output_dir=output_dir,
        output_prefix=profile.output_prefix,
        write_legacy_sample_manifest=profile.profile_id == DEFAULT_SAMPLE_PROFILE_ID,
        manifest=build_result_manifest(
            design=design,
            profile=profile,
            inputs=inputs,
            rows=rows,
            summary_rows=summary_rows,
            policies=policies,
            cases=cases,
            seeds=resolved_seeds,
            region_path=region_path,
            cache_path=cache_path,
            scenarios_path=scenarios_path,
            policies_path=policies_path,
            design_path=design_path,
            output_dir=output_dir,
            road_class_overrides_path=road_class_overrides_path,
            overrides={
                "policy_ids": policy_ids is not None,
                "scenario_ids": scenario_ids is not None,
                "seeds": seeds is not None,
            },
        ),
    )
    result = {
        "rows": rows,
        "summary_rows": summary_rows,
        "manifest": paths["manifest"],
        "results_path": paths["results"],
        "summary_path": paths["summary"],
        "manifest_path": paths["manifest_path"],
    }
    if "legacy_manifest_path" in paths:
        result["legacy_manifest_path"] = paths["legacy_manifest_path"]
    return result


def load_pilot_experiment_design(
    path: str | Path = DEFAULT_DESIGN_PATH,
) -> PilotExperimentDesign:
    """Load and validate the accepted pilot experiment design manifest."""

    design_path = Path(path)
    with design_path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    if not isinstance(raw, Mapping):
        raise ValueError(f"{design_path} must contain a JSON object")

    schema_version = _positive_int(raw.get("schema_version"), "schema_version")
    region_id = _required_text(raw.get("region_id"), "region_id")
    design_scope = _required_text(raw.get("design_scope"), "design_scope")
    claim_boundary = _required_text(raw.get("claim_boundary"), "claim_boundary")
    excluded = raw.get("excluded_policy_ids", {})
    if not isinstance(excluded, Mapping):
        raise ValueError("excluded_policy_ids must be a JSON object")
    excluded_policy_ids = {
        _required_text(policy_id, "excluded_policy_ids key"): _required_text(
            reason,
            f"excluded_policy_ids[{policy_id!r}]",
        )
        for policy_id, reason in excluded.items()
    }

    raw_profiles = raw.get("profiles")
    if not isinstance(raw_profiles, Mapping) or not raw_profiles:
        raise ValueError("profiles must be a non-empty JSON object")
    profiles = {
        str(profile_id): _profile_from_mapping(str(profile_id), profile_raw)
        for profile_id, profile_raw in raw_profiles.items()
    }
    for required_profile in (
        DEFAULT_SAMPLE_PROFILE_ID,
        DEFAULT_STAGED_PROFILE_ID,
        DEFAULT_FULL_PROFILE_ID,
        DEFAULT_MULTI_CORRIDOR_PROFILE_ID,
        DEFAULT_MULTI_CORRIDOR_FULL_PROFILE_ID,
    ):
        if required_profile not in profiles:
            raise ValueError(f"missing required pilot experiment profile: {required_profile}")

    return PilotExperimentDesign(
        schema_version=schema_version,
        region_id=region_id,
        design_scope=design_scope,
        claim_boundary=claim_boundary,
        profiles=profiles,
        excluded_policy_ids=excluded_policy_ids,
    )


def resolve_pilot_experiment_profile(
    *,
    design_path: str | Path = DEFAULT_DESIGN_PATH,
    run_profile: str | None = None,
    sample: bool = True,
) -> tuple[PilotExperimentDesign, PilotExperimentProfile]:
    """Return the design and selected profile for backward-compatible calls."""

    design = load_pilot_experiment_design(design_path)
    profile_id = run_profile or (DEFAULT_SAMPLE_PROFILE_ID if sample else DEFAULT_FULL_PROFILE_ID)
    try:
        profile = design.profiles[profile_id]
    except KeyError as exc:
        available = ", ".join(sorted(design.profiles))
        raise KeyError(f"unknown pilot experiment profile {profile_id!r}; available={available}") from exc
    return design, profile


def load_pilot_inputs(
    *,
    region_path: str | Path = DEFAULT_REGION_PATH,
    cache_path: str | Path = DEFAULT_CACHE_PATH,
    road_class_overrides_path: str | Path | None = None,
    reduce_graph: bool = True,
    graph_reduction_strategy: str = GRAPH_REDUCTION_SINGLE_CORRIDOR,
    corridor_path_count: int = 1,
) -> PilotInputs:
    """Load the pilot region spec and cached GraphML without live OSM calls."""

    region_file = Path(region_path)
    cache_file = Path(cache_path)
    region = _load_yaml_mapping(region_file)
    road_graph = load_graphml(cache_file, normalize=True)
    highway_defaults = None
    if road_class_overrides_path is not None:
        override_records = load_road_class_overrides(road_class_overrides_path)
        highway_defaults = build_highway_defaults_with_overrides(override_records)
    graph = build_simulator_graph(
        road_graph,
        region,
        highway_defaults=highway_defaults,
    )
    assert_graph_ready(graph)
    source_graph_nodes = graph.number_of_nodes()
    source_graph_edges = graph.number_of_edges()
    if reduce_graph:
        graph = reduce_pilot_analysis_graph(
            graph,
            strategy=graph_reduction_strategy,
            path_count=corridor_path_count,
        )
        assert_graph_ready(graph)
    if road_class_overrides_path is not None:
        graph.graph["road_class_overrides_path"] = _display_path(
            road_class_overrides_path
        )
        graph.graph["road_class_overrides_sha256"] = _file_sha256(
            road_class_overrides_path
        )
    return PilotInputs(
        region=region,
        graph=graph,
        graph_source=_graph_source_label(
            cache_file,
            road_class_overrides_path=road_class_overrides_path,
        ),
        source_graph_nodes=source_graph_nodes,
        source_graph_edges=source_graph_edges,
    )


def pilot_experiment_subgraph(graph: nx.DiGraph) -> nx.DiGraph:
    """Return a compact route-corridor graph for fast sample experiments.

    The full OSM-derived graph can contain tens of thousands of edges. The
    existing scenario runner recomputes dynamic shortest-path weights over all
    edges at every dispatch, which is useful for the abstract graph but too slow
    for pilot scaffold sample runs. This helper preserves the route corridors required
    by the current policy comparison: A->D, A->S, and R->D.
    """

    return _route_corridor_subgraph(
        graph,
        route_pairs=DEFAULT_ROUTE_CORRIDOR_PAIRS,
        path_count=1,
        strategy="single_shortest_time_route_corridor",
    )


def reduce_pilot_analysis_graph(
    graph: nx.DiGraph,
    *,
    strategy: str = GRAPH_REDUCTION_SINGLE_CORRIDOR,
    path_count: int = 1,
) -> nx.DiGraph:
    """Return the configured reduced analysis graph for pilot experiments."""

    strategy = _validated_graph_reduction_strategy(strategy)
    if strategy == GRAPH_REDUCTION_SINGLE_CORRIDOR:
        if path_count != 1:
            raise ValueError("single_corridor graph reduction requires path_count=1")
        return pilot_experiment_subgraph(graph)
    return pilot_experiment_multi_corridor_subgraph(graph, path_count=path_count)


def pilot_experiment_multi_corridor_subgraph(
    graph: nx.DiGraph,
    *,
    path_count: int = 3,
) -> nx.DiGraph:
    """Return a route-corridor graph preserving multiple full-graph paths.

    This is a graph-scale review aid for corridor uncertainty. It does not
    change the default pilot outputs or accept a final graph-scale method.
    """

    return _route_corridor_subgraph(
        graph,
        route_pairs=DEFAULT_ROUTE_CORRIDOR_PAIRS,
        path_count=path_count,
        strategy="multi_shortest_time_route_corridor_candidate",
    )


def _route_corridor_subgraph(
    graph: nx.DiGraph,
    *,
    route_pairs: Sequence[tuple[Any, Any]],
    path_count: int,
    strategy: str,
) -> nx.DiGraph:
    if path_count < 1:
        raise ValueError("path_count must be at least 1")
    selected_edges: set[tuple[Any, Any]] = set()
    road_view = _road_mode_view(graph)
    for source, target in route_pairs:
        paths = _route_candidate_paths(
            road_view,
            source,
            target,
            path_count=path_count,
        )
        if not paths:
            return graph.copy()
        for path in paths:
            selected_edges.update(zip(path, path[1:]))

    # Include the reverse directions where present so scenario edge selection
    # and route alternatives can remain bidirectional around the corridors.
    for u, v in tuple(selected_edges):
        if graph.has_edge(v, u):
            selected_edges.add((v, u))

    compact = nx.DiGraph()
    compact.graph.update(graph.graph)
    compact.graph["source_graph_nodes"] = graph.number_of_nodes()
    compact.graph["source_graph_edges"] = graph.number_of_edges()
    compact.graph["experiment_subgraph"] = True
    compact.graph["corridor_strategy"] = strategy
    compact.graph["corridor_path_count"] = path_count
    for u, v in sorted(selected_edges, key=lambda edge: (repr(edge[0]), repr(edge[1]))):
        compact.add_node(u, **graph.nodes[u])
        compact.add_node(v, **graph.nodes[v])
        compact.add_edge(u, v, **graph.edges[u, v])
    return compact


def _route_candidate_paths(
    graph: nx.DiGraph,
    source: Any,
    target: Any,
    *,
    path_count: int,
) -> tuple[tuple[Any, ...], ...]:
    try:
        if path_count == 1:
            return (tuple(nx.shortest_path(graph, source, target, weight="t0")),)
        paths = nx.shortest_simple_paths(graph, source, target, weight="t0")
        return tuple(tuple(path) for path in islice(paths, path_count))
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return ()


def _road_mode_view(graph: nx.DiGraph) -> nx.DiGraph:
    return nx.subgraph_view(
        graph,
        filter_edge=lambda u, v: graph.edges[u, v].get("mode") == "road",
    )


def make_pilot_base_config(region: Mapping[str, Any]) -> dict[str, Any]:
    """Return the compact pilot experiment config before policy variants."""

    network = realworld_network_config(region)
    return {
        "network": {
            "nodes": network["nodes"],
            "rail_link": network["rail_link"],
            "road_links": [],
            "variant": "cached_pilot_fixture",
        },
        "personnel": {
            "total": 24,
            "group_size": 8,
            "assembly_time": 0.0,
        },
        "bus": {
            "first_departure_min": 0.0,
            "dispatch_interval_min": 5.0,
            "fleet_size": 3,
            "turnaround_min": 8.0,
        },
        "multimodal": {
            "shuttle_first_departure_min": 0.0,
            "shuttle_dispatch_interval_min": 5.0,
            "shuttle_fleet_size": 3,
            "shuttle_turnaround_min": 8.0,
            "transfer_time_min": 3.0,
            "transfer_per_passenger_min": 0.02,
            "rail_first_departure_min": 0.0,
            "lastmile_first_departure_min": 0.0,
            "lastmile_dispatch_interval_min": 5.0,
            "lastmile_fleet_size": 2,
            "lastmile_turnaround_min": 8.0,
            "lastmile_vehicle_capacity": 8,
        },
        "traffic": {
            "volume_window_min": 60.0,
            "background_volume": 150.0,
        },
        "failure": {
            "mode": "blocked",
            "capacity_reduction_factor": 1.0,
        },
        "metrics": {
            "late_penalty_min": 300.0,
        },
        "bpr": {
            "alpha": 0.15,
            "beta": 4.0,
        },
        "lateness": {
            "distribution": "lognormal_sample_fixture",
            "mu": 1.2,
            "sigma_levels": [0.25],
        },
        "experiment": {
            "R": 1,
            "seed_base": 1,
            "time_limit": 240.0,
        },
    }


def select_policy_alternatives(
    alternatives: Sequence[PolicyAlternative],
    *,
    policy_ids: Sequence[str] | None = None,
    sample: bool = True,
) -> tuple[PolicyAlternative, ...]:
    """Return policy rows in a deterministic requested/sample/table order."""

    requested = tuple(policy_ids or (DEFAULT_SAMPLE_POLICY_IDS if sample else ()))
    if not requested:
        return tuple(alternatives)

    by_id = {alternative.policy_id: alternative for alternative in alternatives}
    missing = [policy_id for policy_id in requested if policy_id not in by_id]
    if missing:
        raise KeyError(f"unknown policy_id values: {missing}")
    return tuple(by_id[policy_id] for policy_id in requested)


def select_disruption_cases(
    graph: nx.DiGraph,
    scenarios: Sequence[DisruptionScenario],
    *,
    scenario_ids: Sequence[str] | None = None,
    sample: bool = True,
) -> tuple[PilotDisruptionCase, ...]:
    """Return no-disruption plus selected structured disruption cases."""

    requested = tuple(scenario_ids or (DEFAULT_SAMPLE_SCENARIO_IDS if sample else ()))
    no_disruption = PilotDisruptionCase(
        scenario_id="no_disruption",
        scenario_family="no_disruption",
        scenario_type="none",
        failure_mode="blocked",
        capacity_factor=1.0,
        p_fail_scale=0.0,
        notes="No structured road disruption; baseline comparison row.",
    )
    if not requested:
        selected_scenarios = tuple(scenarios)
        return (no_disruption, *(_case_from_scenario(graph, item) for item in selected_scenarios))

    by_id = {scenario.scenario_id: scenario for scenario in scenarios}
    cases: list[PilotDisruptionCase] = []
    for scenario_id in requested:
        if scenario_id == "no_disruption":
            cases.append(no_disruption)
            continue
        if scenario_id not in by_id:
            raise KeyError(f"unknown scenario_id: {scenario_id!r}")
        cases.append(_case_from_scenario(graph, by_id[scenario_id]))
    return tuple(cases)


def run_pilot_rows(
    *,
    inputs: PilotInputs,
    policies: Sequence[PolicyAlternative],
    cases: Sequence[PilotDisruptionCase],
    seeds: Sequence[int],
    claim_scope: str = CLAIM_SCOPE,
) -> list[dict[str, Any]]:
    """Execute all policy, disruption, and seed combinations."""

    rows: list[dict[str, Any]] = []
    base_config = make_pilot_base_config(inputs.region)
    for case in cases:
        disrupted_graph = graph_with_forced_disruption_probabilities(inputs.graph, case)
        for policy in policies:
            variant = build_policy_config_variant(base_config, policy, policies)
            run_config = _config_with_case_failure(variant.config, case)
            for seed in seeds:
                metrics = scenario_module.run_scenario(
                    G=disrupted_graph,
                    config=run_config,
                    scenario_type=variant.scenario_type,
                    policy=StrictPolicy(),
                    params={
                        "s": 1.0,
                        "p_fail_scale": case.p_fail_scale,
                        "sigma": 0.25,
                    },
                    seed=int(seed),
                )
                rows.append(
                    _result_row(
                        inputs=inputs,
                        policy=policy,
                        case=case,
                        seed=int(seed),
                        mode=variant.scenario_type,
                        metrics=metrics,
                        claim_scope=claim_scope,
                    )
                )
    return rows


def graph_with_forced_disruption_probabilities(
    graph: nx.DiGraph,
    case: PilotDisruptionCase,
) -> nx.DiGraph:
    """Copy a graph and force deterministic selected-road disruption sampling."""

    prepared = graph.copy()
    for _, _, data in prepared.edges(data=True):
        if data.get("mode") == "road":
            data["p_fail"] = 0.0
            data["base_p_fail"] = 0.0

    for selected in case.selected_edges:
        if not prepared.has_edge(*selected.edge):
            raise ValueError(f"selected edge missing from graph: {selected.edge!r}")
        data = prepared.edges[selected.edge]
        if data.get("mode") == "road":
            data["p_fail"] = 1.0
            data["base_p_fail"] = 1.0
    return prepared


def summarize_pilot_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Group pilot rows by policy, disruption case, and mode and average KPIs."""

    grouped: dict[tuple[Any, ...], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        key = tuple(row[column] for column in SUMMARY_GROUP_COLUMNS)
        grouped[key].append(row)

    summary_rows: list[dict[str, Any]] = []
    for key in sorted(grouped, key=lambda item: tuple(str(part) for part in item)):
        group_rows = grouped[key]
        summary: dict[str, Any] = dict(zip(SUMMARY_GROUP_COLUMNS, key))
        summary["run_count"] = len(group_rows)
        for metric in METRIC_COLUMNS:
            summary[f"mean_{metric}"] = _round_metric(
                _mean(_metric_value(row, metric) for row in group_rows),
                precision=4 if metric == "passengers_per_total_service_minute" else 2,
            )
        claim_scopes = sorted(
            str(row.get("claim_scope", CLAIM_SCOPE))
            for row in group_rows
            if str(row.get("claim_scope", CLAIM_SCOPE)).strip()
        )
        summary["claim_scope"] = claim_scopes[0] if claim_scopes else CLAIM_SCOPE
        summary_rows.append(summary)
    return summary_rows


def write_pilot_outputs(
    *,
    rows: Sequence[Mapping[str, Any]],
    summary_rows: Sequence[Mapping[str, Any]],
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    output_prefix: str = "pilot_sample",
    write_legacy_sample_manifest: bool = False,
    manifest: Mapping[str, Any],
) -> dict[str, Any]:
    """Write result CSVs and manifest under a separated real-world output dir."""

    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    _validate_output_prefix(output_prefix)
    results_path = directory / f"{output_prefix}_results.csv"
    summary_path = directory / f"{output_prefix}_summary.csv"
    manifest_path = directory / f"{output_prefix}_manifest.json"

    _write_csv(results_path, RESULT_COLUMNS, rows)
    _write_csv(summary_path, SUMMARY_COLUMNS, summary_rows)
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(dict(manifest), handle, indent=2, sort_keys=True)
        handle.write("\n")

    result = {
        "results": results_path,
        "summary": summary_path,
        "manifest_path": manifest_path,
        "manifest": dict(manifest),
    }
    if write_legacy_sample_manifest:
        legacy_manifest_path = directory / "pilot_result_manifest.json"
        with legacy_manifest_path.open("w", encoding="utf-8") as handle:
            json.dump(dict(manifest), handle, indent=2, sort_keys=True)
            handle.write("\n")
        result["legacy_manifest_path"] = legacy_manifest_path
    return result


def build_result_manifest(
    *,
    inputs: PilotInputs,
    rows: Sequence[Mapping[str, Any]],
    summary_rows: Sequence[Mapping[str, Any]],
    policies: Sequence[PolicyAlternative],
    cases: Sequence[PilotDisruptionCase],
    seeds: Sequence[int],
    region_path: str | Path,
    cache_path: str | Path,
    scenarios_path: str | Path,
    policies_path: str | Path,
    design: PilotExperimentDesign | None = None,
    profile: PilotExperimentProfile | None = None,
    design_path: str | Path = DEFAULT_DESIGN_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    road_class_overrides_path: str | Path | None = None,
    overrides: Mapping[str, bool] | None = None,
    sample: bool | None = None,
) -> dict[str, Any]:
    """Return deterministic metadata for generated pilot experiment outputs."""

    if design is None or profile is None:
        design, profile = resolve_pilot_experiment_profile(
            design_path=design_path,
            sample=True if sample is None else bool(sample),
        )

    expected_row_count = len(policies) * len(cases) * len(seeds)
    output_files = _output_file_manifest(
        output_dir=output_dir,
        output_prefix=profile.output_prefix,
        include_legacy_sample_manifest=profile.profile_id == DEFAULT_SAMPLE_PROFILE_ID,
    )

    return {
        "schema_version": 2,
        "result_scope": profile.result_scope,
        "command": _profile_command(profile),
        "run_profile": profile.profile_id,
        "run_stage": profile.run_stage,
        "sample_scaffold": profile.sample_scaffold,
        "output_prefix": profile.output_prefix,
        "design_status": profile.design_status,
        "design_scope": design.design_scope,
        "design_claim_boundary": design.claim_boundary,
        "design_path": _display_path(design_path),
        "region_id": inputs.region_id,
        "graph_source": inputs.graph_source,
        "graph_nodes": inputs.graph.number_of_nodes(),
        "graph_edges": inputs.graph.number_of_edges(),
        "source_graph_nodes": inputs.source_graph_nodes,
        "source_graph_edges": inputs.source_graph_edges,
        "analysis_graph_reduced": bool(inputs.graph.graph.get("experiment_subgraph", False)),
        "analysis_graph_strategy": profile.analysis_graph_strategy,
        "graph_reduction_strategy": profile.graph_reduction_strategy,
        "corridor_path_count": profile.corridor_path_count,
        "graph_scale": {
            "source": {
                "nodes": inputs.source_graph_nodes,
                "edges": inputs.source_graph_edges,
            },
            "analysis": {
                "nodes": inputs.graph.number_of_nodes(),
                "edges": inputs.graph.number_of_edges(),
                "reduced": bool(inputs.graph.graph.get("experiment_subgraph", False)),
                "strategy": profile.analysis_graph_strategy,
                "graph_reduction_strategy": profile.graph_reduction_strategy,
                "corridor_path_count": profile.corridor_path_count,
                "graph_corridor_strategy": str(
                    inputs.graph.graph.get("corridor_strategy", "")
                ),
                "graph_corridor_path_count": inputs.graph.graph.get(
                    "corridor_path_count"
                ),
            },
        },
        "inputs": {
            "region_path": _display_path(region_path),
            "cache_path": _display_path(cache_path),
            "disruption_scenarios_path": _display_path(scenarios_path),
            "policy_alternatives_path": _display_path(policies_path),
            "pilot_experiment_design_path": _display_path(design_path),
            "road_class_overrides_path": (
                None
                if road_class_overrides_path is None
                else _display_path(road_class_overrides_path)
            ),
            "road_class_overrides_sha256": (
                None
                if road_class_overrides_path is None
                else _file_sha256(road_class_overrides_path)
            ),
        },
        "outputs": output_files,
        "policy_ids": [policy.policy_id for policy in policies],
        "scenario_ids": [case.scenario_id for case in cases],
        "seeds": [int(seed) for seed in seeds],
        "row_count": len(rows),
        "summary_row_count": len(summary_rows),
        "expected_row_count": expected_row_count,
        "scenario_policy_seed_design": {
            "policy_count": len(policies),
            "scenario_count": len(cases),
            "seed_count": len(seeds),
            "expected_row_count": expected_row_count,
            "common_random_numbers": True,
        },
        "design_overrides": dict(overrides or {}),
        "excluded_policy_ids": dict(design.excluded_policy_ids),
        "metric_columns": list(METRIC_COLUMNS),
        "common_random_numbers": (
            "Rows with the same seed use the existing run_scenario seed split "
            "for arrival and failure streams across compared policies."
        ),
        "disruption_sampling": (
            "Road p_fail/base_p_fail are reset to zero on a graph copy, then "
            "scenario-selected road edges are set to one with p_fail_scale=1."
        ),
        "road_class_overrides_applied": bool(
            inputs.graph.graph.get("road_class_overrides_applied", False)
        ),
    }


def _case_from_scenario(
    graph: nx.DiGraph,
    scenario: DisruptionScenario,
) -> PilotDisruptionCase:
    selected_edges = select_candidate_edges(graph, scenario)
    return PilotDisruptionCase(
        scenario_id=scenario.scenario_id,
        scenario_family=scenario.family,
        scenario_type=scenario.disruption_mode,
        failure_mode=scenario.disruption_mode,
        capacity_factor=scenario.capacity_factor,
        p_fail_scale=1.0 if selected_edges else 0.0,
        selected_edges=selected_edges,
        notes=scenario.notes,
    )


def _config_with_case_failure(
    config: Mapping[str, Any],
    case: PilotDisruptionCase,
) -> dict[str, Any]:
    run_config = _deepcopy_jsonable(config)
    run_config.setdefault("failure", {})
    run_config["failure"]["mode"] = case.failure_mode
    if case.failure_mode == "capacity_reduction":
        run_config["failure"]["capacity_reduction_factor"] = case.capacity_factor
    else:
        run_config["failure"]["capacity_reduction_factor"] = 1.0
    return run_config


def _result_row(
    *,
    inputs: PilotInputs,
    policy: PolicyAlternative,
    case: PilotDisruptionCase,
    seed: int,
    mode: str,
    metrics: Mapping[str, Any],
    claim_scope: str,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "region_id": inputs.region_id,
        "graph_source": inputs.graph_source,
        "policy_id": policy.policy_id,
        "scenario_id": case.scenario_id,
        "scenario_family": case.scenario_family,
        "scenario_type": case.scenario_type,
        "seed": seed,
        "mode": mode,
        "selected_edge_count": len(case.selected_edges),
        "selected_realworld_edge_ids": ";".join(case.selected_realworld_edge_ids),
        "notes": _combined_notes(policy, case),
        "claim_scope": claim_scope,
    }
    for metric in METRIC_COLUMNS:
        row[metric] = _round_metric(
            float(metrics[metric]),
            precision=4 if metric == "passengers_per_total_service_minute" else 2,
        )
    row["censored_count"] = int(metrics["censored_count"])
    return row


def _combined_notes(policy: PolicyAlternative, case: PilotDisruptionCase) -> str:
    parts = [
        f"policy={policy.decision_interpretation}",
        f"scenario={case.notes or case.scenario_id}",
    ]
    return " | ".join(parts)


def _write_csv(
    path: Path,
    columns: Sequence[str],
    rows: Sequence[Mapping[str, Any]],
) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def _profile_from_mapping(
    profile_id: str,
    raw: Any,
) -> PilotExperimentProfile:
    if not isinstance(raw, Mapping):
        raise ValueError(f"profile {profile_id!r} must be a JSON object")

    declared_id = str(raw.get("profile_id", profile_id)).strip()
    if declared_id != profile_id:
        raise ValueError(
            f"profile key {profile_id!r} does not match profile_id {declared_id!r}"
        )

    profile = PilotExperimentProfile(
        profile_id=profile_id,
        run_stage=_required_text(raw.get("run_stage"), f"{profile_id}.run_stage"),
        output_prefix=_required_text(
            raw.get("output_prefix"),
            f"{profile_id}.output_prefix",
        ),
        sample_scaffold=_required_bool(
            raw.get("sample_scaffold"),
            f"{profile_id}.sample_scaffold",
        ),
        result_scope=_required_text(raw.get("result_scope"), f"{profile_id}.result_scope"),
        design_status=_required_text(raw.get("design_status"), f"{profile_id}.design_status"),
        analysis_graph_strategy=_required_text(
            raw.get("analysis_graph_strategy"),
            f"{profile_id}.analysis_graph_strategy",
        ),
        reduce_graph=_required_bool(raw.get("reduce_graph"), f"{profile_id}.reduce_graph"),
        policy_ids=_required_text_tuple(raw.get("policy_ids"), f"{profile_id}.policy_ids"),
        scenario_ids=_required_text_tuple(
            raw.get("scenario_ids"),
            f"{profile_id}.scenario_ids",
        ),
        seeds=tuple(
            _positive_int(seed, f"{profile_id}.seeds")
            for seed in _required_sequence(raw.get("seeds"), f"{profile_id}.seeds")
        ),
        graph_reduction_strategy=_required_text(
            raw.get("graph_reduction_strategy", GRAPH_REDUCTION_SINGLE_CORRIDOR),
            f"{profile_id}.graph_reduction_strategy",
        ),
        corridor_path_count=_positive_int(
            raw.get("corridor_path_count", 1),
            f"{profile_id}.corridor_path_count",
        ),
        description=str(raw.get("description", "") or "").strip(),
    )
    _validate_profile(profile)
    return profile


def _validate_profile(profile: PilotExperimentProfile) -> None:
    if profile.run_stage not in RUN_STAGES:
        raise ValueError(
            f"{profile.profile_id}.run_stage must be one of {sorted(RUN_STAGES)}"
        )
    _validate_output_prefix(profile.output_prefix)
    if not profile.policy_ids:
        raise ValueError(f"{profile.profile_id}.policy_ids must not be empty")
    if not profile.scenario_ids:
        raise ValueError(f"{profile.profile_id}.scenario_ids must not be empty")
    if not profile.seeds:
        raise ValueError(f"{profile.profile_id}.seeds must not be empty")

    if profile.run_stage == "sample" and not profile.sample_scaffold:
        raise ValueError(f"{profile.profile_id} sample run must be marked sample_scaffold")
    if profile.run_stage != "sample" and profile.sample_scaffold:
        raise ValueError(
            f"{profile.profile_id} staged/full run must not be marked sample_scaffold"
        )
    _validated_graph_reduction_strategy(profile.graph_reduction_strategy)
    if (
        profile.graph_reduction_strategy == GRAPH_REDUCTION_SINGLE_CORRIDOR
        and profile.corridor_path_count != 1
    ):
        raise ValueError(
            f"{profile.profile_id}.corridor_path_count must be 1 for single_corridor"
        )
    if (
        profile.graph_reduction_strategy == GRAPH_REDUCTION_MULTI_CORRIDOR
        and profile.corridor_path_count < 2
    ):
        raise ValueError(
            f"{profile.profile_id}.corridor_path_count must be at least 2 for multi_corridor"
        )

    scope = profile.result_scope.lower()
    if "not calibrated" not in scope or "operational forecast" not in scope:
        raise ValueError(
            f"{profile.profile_id}.result_scope must block calibrated and "
            "operational forecast claims"
        )


def _output_file_manifest(
    *,
    output_dir: str | Path,
    output_prefix: str,
    include_legacy_sample_manifest: bool,
) -> dict[str, str]:
    directory = Path(output_dir)
    outputs = {
        "results": _display_path(directory / f"{output_prefix}_results.csv"),
        "summary": _display_path(directory / f"{output_prefix}_summary.csv"),
        "manifest": _display_path(directory / f"{output_prefix}_manifest.json"),
    }
    if include_legacy_sample_manifest:
        outputs["legacy_sample_manifest"] = _display_path(
            directory / "pilot_result_manifest.json"
        )
    return outputs


def _profile_command(profile: PilotExperimentProfile) -> str:
    if profile.profile_id == DEFAULT_SAMPLE_PROFILE_ID:
        return "scripts/run_pilot_experiments.py --sample"
    if profile.profile_id == DEFAULT_STAGED_PROFILE_ID:
        return "scripts/run_pilot_experiments.py --staged"
    if profile.profile_id == DEFAULT_FULL_PROFILE_ID:
        return "scripts/run_pilot_experiments.py --full"
    if profile.profile_id == DEFAULT_MULTI_CORRIDOR_PROFILE_ID:
        return "scripts/run_pilot_experiments.py --multi-corridor"
    if profile.profile_id == DEFAULT_MULTI_CORRIDOR_FULL_PROFILE_ID:
        return "scripts/run_pilot_experiments.py --multi-corridor-full"
    return f"scripts/run_pilot_experiments.py --profile {profile.profile_id}"


def _validated_graph_reduction_strategy(strategy: str) -> str:
    cleaned = str(strategy or "").strip()
    if cleaned not in GRAPH_REDUCTION_STRATEGIES:
        allowed = ", ".join(sorted(GRAPH_REDUCTION_STRATEGIES))
        raise ValueError(f"graph_reduction_strategy must be one of: {allowed}")
    return cleaned


def _required_text(value: Any, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{name} must be non-empty text")
    return text


def _required_bool(value: Any, name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be true or false")
    return value


def _required_sequence(value: Any, name: str) -> tuple[Any, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple)):
        raise ValueError(f"{name} must be a JSON array")
    if not value:
        raise ValueError(f"{name} must not be empty")
    return tuple(value)


def _required_text_tuple(value: Any, name: str) -> tuple[str, ...]:
    return tuple(_required_text(item, name) for item in _required_sequence(value, name))


def _positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a positive integer")
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a positive integer") from exc
    if number < 1 or str(value).strip() not in {str(number), f"{number}.0"}:
        raise ValueError(f"{name} must be a positive integer")
    return number


def _validate_output_prefix(output_prefix: str) -> None:
    if not output_prefix:
        raise ValueError("output_prefix must be non-empty")
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789_")
    if any(character not in allowed for character in output_prefix):
        raise ValueError(
            "output_prefix must use lowercase letters, digits, and underscores only"
        )


def _load_yaml_mapping(path: Path) -> Mapping[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, Mapping):
        raise ValueError(f"{path} must contain a YAML mapping")
    return value


def _display_path(path: str | Path) -> str:
    filepath = Path(path)
    try:
        return filepath.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return filepath.as_posix()


def _graph_source_label(
    cache_path: str | Path,
    *,
    road_class_overrides_path: str | Path | None,
) -> str:
    label = f"cached_graphml:{_display_path(cache_path)}"
    if road_class_overrides_path is None:
        return label
    return (
        f"{label};road_class_overrides:"
        f"{_display_path(road_class_overrides_path)}"
    )


def _file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _deepcopy_jsonable(value: Mapping[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(value))


def _mean(values: Iterable[float]) -> float:
    values_tuple = tuple(values)
    if not values_tuple:
        return float("nan")
    return sum(values_tuple) / len(values_tuple)


def _metric_value(row: Mapping[str, Any], metric: str) -> float:
    value = row.get(metric, float("nan"))
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def _round_metric(value: float, *, precision: int) -> float:
    if math.isfinite(value):
        return round(value, precision)
    return value


__all__ = [
    "CLAIM_SCOPE",
    "DEFAULT_CACHE_PATH",
    "DEFAULT_DESIGN_PATH",
    "DEFAULT_FULL_PROFILE_ID",
    "DEFAULT_MANIFEST_PATH",
    "DEFAULT_MULTI_CORRIDOR_FULL_PROFILE_ID",
    "DEFAULT_MULTI_CORRIDOR_PROFILE_ID",
    "DEFAULT_OUTPUT_DIR",
    "DEFAULT_REGION_PATH",
    "DEFAULT_SAMPLE_MANIFEST_PATH",
    "DEFAULT_SAMPLE_PROFILE_ID",
    "DEFAULT_RESULTS_PATH",
    "DEFAULT_ROUTE_CORRIDOR_PAIRS",
    "DEFAULT_SAMPLE_POLICY_IDS",
    "DEFAULT_SAMPLE_SCENARIO_IDS",
    "DEFAULT_SAMPLE_SEEDS",
    "DEFAULT_STAGED_PROFILE_ID",
    "DEFAULT_SUMMARY_PATH",
    "GRAPH_REDUCTION_MULTI_CORRIDOR",
    "GRAPH_REDUCTION_SINGLE_CORRIDOR",
    "GRAPH_REDUCTION_STRATEGIES",
    "PilotDisruptionCase",
    "PilotExperimentDesign",
    "PilotExperimentProfile",
    "PilotInputs",
    "PILOT_FULL_CLAIM_SCOPE",
    "PILOT_MULTI_CORRIDOR_CANDIDATE_CLAIM_SCOPE",
    "PILOT_MULTI_CORRIDOR_FULL_CANDIDATE_CLAIM_SCOPE",
    "PILOT_STAGED_CLAIM_SCOPE",
    "RESULT_COLUMNS",
    "RUN_STAGES",
    "SUMMARY_COLUMNS",
    "build_result_manifest",
    "graph_with_forced_disruption_probabilities",
    "load_pilot_inputs",
    "load_pilot_experiment_design",
    "make_pilot_base_config",
    "pilot_experiment_multi_corridor_subgraph",
    "pilot_experiment_subgraph",
    "reduce_pilot_analysis_graph",
    "resolve_pilot_experiment_profile",
    "run_pilot_experiments",
    "run_pilot_rows",
    "select_disruption_cases",
    "select_policy_alternatives",
    "summarize_pilot_rows",
    "write_pilot_outputs",
]
