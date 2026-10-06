"""Run isolated, restartable paper-revision simulation campaigns."""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
import gc
import hashlib
from importlib import metadata as package_metadata
import json
import math
import os
from pathlib import Path
import platform
import sys
import tempfile
from typing import Any

import networkx as nx

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
os.environ.setdefault("PYTORCH_NO_CUDA_MEMORY_CACHING", "1")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.realworld.disruption_scenarios import (
    CENTRAL_TRUNK_TARGET_SEGMENT,
    DisruptionScenario,
    load_disruption_scenarios,
    select_candidate_edges,
    select_corridor_time_band_edges,
)
from src.realworld.pilot_experiments import (
    DEFAULT_DEMAND_PROFILES_PATH,
    DEFAULT_FLEET_PROFILES_PATH,
    apply_pilot_demand_fleet_profiles,
    load_pilot_inputs,
    make_pilot_base_config,
    pilot_experiment_multi_corridor_subgraphs,
)
from src.realworld.revision_campaign import (
    CheckpointJournal,
    CheckpointError,
    RunSpec,
    assert_isolated_output_path,
)
from src.realworld.revision_design import (
    EXPECTED_CAMPAIGNS,
    RevisionExperimentDesign,
    load_revision_design,
)
from src.realworld.revision_execution import (
    PreparedDisruption,
    effective_rail_condition,
    execute_condition,
)
from src.realworld.revision_graph_validation import (
    compute_corridor_target_scope_metrics,
    compute_graph_scope_route_metrics,
    write_corridor_target_scope_evidence,
    write_graph_scope_route_evidence,
)
from src.realworld.revision_graph_scope_cache import (
    GraphScopeCacheError,
    GraphScopeCacheResult,
    load_or_build_graph_scope_cache,
)
from src.realworld.revision_planner import PlannedCondition, plan_campaign_conditions
from src.realworld.revision_runner import (
    selected_edges_checksum,
    select_seeded_random_edges,
    write_campaign_csv,
)


DEFAULT_DESIGN_PATH = (
    ROOT / "data" / "manifests" / "paper_revision_experiment_design.json"
)
GRAPH_PATH_COUNTS = (3, 5, 10)
IMPLEMENTATION_RELATIVE_PATHS = (
    "scripts/run_paper_revision_experiments.py",
    "requirements.txt",
)
INPUT_ARTIFACT_NAMES = (
    "design",
    "region",
    "cache",
    "overrides",
    "scenarios",
    "demand_profiles",
    "fleet_profiles",
)


def run_revision_campaigns(
    *,
    design_path: str | Path,
    campaign_ids: Sequence[str],
    stage: str,
    region_path: str | Path,
    cache_path: str | Path,
    overrides_path: str | Path,
    scenarios_path: str | Path,
    output_root: str | Path | None = None,
    max_runs: int | None = None,
    resume: bool = True,
) -> dict[str, Any]:
    """Execute requested campaigns while loading source graph exactly once."""

    if stage not in {"smoke", "full"}:
        raise ValueError("stage must be smoke or full")
    if max_runs is not None and (
        isinstance(max_runs, bool) or not isinstance(max_runs, int) or max_runs < 1
    ):
        raise ValueError("max_runs must be None or a positive integer")

    design = load_revision_design(design_path)
    selected_campaigns = _normalize_campaign_ids(campaign_ids)
    resolved_output_root = _resolve_output_root(design, output_root)
    # Safety gate precedes GraphML loading. Canonical pilot outputs stay read-only.
    resolved_output_root = assert_isolated_output_path(resolved_output_root)
    input_paths = {
        "design": Path(design_path),
        "region": Path(region_path),
        "cache": Path(cache_path),
        "overrides": Path(overrides_path),
        "scenarios": Path(scenarios_path),
        "demand_profiles": Path(DEFAULT_DEMAND_PROFILES_PATH),
        "fleet_profiles": Path(DEFAULT_FLEET_PROFILES_PATH),
    }
    input_provenance = _input_provenance(input_paths)
    input_artifacts = input_provenance["artifacts"]
    implementation_provenance = _implementation_provenance()
    runtime_provenance = _runtime_provenance()
    campaign_paths = {
        campaign_id: _campaign_output_paths(
            resolved_output_root,
            campaign_id,
            stage,
        )
        for campaign_id in selected_campaigns
    }
    for paths in campaign_paths.values():
        if resume:
            _assert_resume_implementation_matches(
                checkpoint_path=paths["checkpoint"],
                manifest_path=paths["manifest"],
                implementation_fingerprint=implementation_provenance["fingerprint"],
                runtime_fingerprint=runtime_provenance["fingerprint"],
                input_fingerprint=input_provenance["fingerprint"],
            )
        else:
            # Explicit replacement authorizes a clean run under current code.
            _atomic_replace_bytes(paths["checkpoint"], b"")
            _atomic_replace_bytes(paths["results"], b"run_key\n")

    source_graphml_sha256 = input_artifacts["cache"].get("sha256")
    if not isinstance(source_graphml_sha256, str):
        raise FileNotFoundError(f"source GraphML cache is missing: {cache_path}")

    inputs = load_pilot_inputs(
        region_path=region_path,
        cache_path=cache_path,
        road_class_overrides_path=overrides_path,
        reduce_graph=False,
    )
    graph_scope_cache = load_or_build_graph_scope_cache(
        inputs.graph,
        cache_root=resolved_output_root / "_graph_scope_cache",
        source_graphml_sha256=source_graphml_sha256,
        builder_fingerprint=implementation_provenance["fingerprint"],
        scope_input_fingerprint=input_provenance["fingerprint"],
        path_counts=GRAPH_PATH_COUNTS,
        progress=_print_graph_scope_progress,
    )
    graphs = _build_graph_scopes(inputs.graph, graph_scope_cache)
    graph_scope_cache_evidence = _graph_scope_cache_evidence(graph_scope_cache)
    base_config, profile_metadata = apply_pilot_demand_fleet_profiles(
        make_pilot_base_config(inputs.region),
        demand_profile_id="pilot_default_demand",
    )
    region_id = str(getattr(inputs, "region_id", inputs.region["region_id"]))
    scenarios = load_disruption_scenarios(scenarios_path, region_id=region_id)
    scenario_lookup = {item.scenario_id: item for item in scenarios}
    graph_scope_freeze_id = str(
        design.campaign("graph_scope")["freeze_selected_edges_from"]
    )
    main_scope_id = str(design.defaults["graph_scope"])
    graph_scope_frozen_edges, graph_scope_frozen_errors = _freeze_scenario_edges(
        graphs[graph_scope_freeze_id],
        scenarios,
        corridor_path_count=int(graph_scope_freeze_id[3:]),
    )
    if main_scope_id == graph_scope_freeze_id:
        main_frozen_edges = graph_scope_frozen_edges
        main_frozen_errors = graph_scope_frozen_errors
    else:
        main_frozen_edges, main_frozen_errors = _freeze_scenario_edges(
            graphs[main_scope_id],
            scenarios,
            corridor_path_count=int(design.defaults["corridor_path_count"]),
        )
    graph_route_rows = compute_graph_scope_route_metrics(
        graphs,
        diversity_limits={
            **{f"top{count}": count for count in GRAPH_PATH_COUNTS},
            "full": max(GRAPH_PATH_COUNTS),
        },
    )
    graph_route_evidence = write_graph_scope_route_evidence(
        resolved_output_root,
        graph_route_rows,
        input_artifacts=input_artifacts,
        claim_boundary=design.claim_boundary,
    )

    graph_scope_corridor_edges = graph_scope_frozen_edges.get(
        "goseong_long_haul_damage_mild", ()
    )
    if not graph_scope_corridor_edges:
        graph_scope_corridor_edges = tuple(
            (str(u), str(v))
            for u, v in select_corridor_time_band_edges(
                graphs[graph_scope_freeze_id],
                source="A",
                target="D",
                path_count=int(graph_scope_freeze_id[3:]),
            )
        )
        missing_graph_scope_edges = [
            edge for edge in graph_scope_corridor_edges
            if not graphs[graph_scope_freeze_id].has_edge(*edge)
        ]
        if missing_graph_scope_edges:
            raise ValueError(
                "graph-scope corridor-envelope target is incomplete: "
                f"missing_count={len(missing_graph_scope_edges)}"
            )

    main_corridor_edges = main_frozen_edges.get(
        "goseong_long_haul_damage_mild", ()
    )
    if not main_corridor_edges:
        main_corridor_edges = tuple(
            (str(u), str(v))
            for u, v in select_corridor_time_band_edges(
                graphs[main_scope_id],
                source="A",
                target="D",
                path_count=int(design.defaults["corridor_path_count"]),
            )
        )
        missing_main_edges = [
            edge for edge in main_corridor_edges
            if not graphs[main_scope_id].has_edge(*edge)
        ]
        if missing_main_edges:
            raise ValueError(
                "main corridor-envelope target is incomplete on execution scope: "
                f"missing_count={len(missing_main_edges)}"
            )
    corridor_scope_rows = compute_corridor_target_scope_metrics(
        {
            main_scope_id: graphs[main_scope_id],
            "full": graphs["full"],
        },
        selected_edges=main_corridor_edges,
        road_multipliers=tuple(
            float(value)
            for value in design.campaign("break_even")["road_multipliers"]
        ),
    )
    corridor_scope_evidence = write_corridor_target_scope_evidence(
        resolved_output_root,
        corridor_scope_rows,
        input_artifacts=input_artifacts,
        claim_boundary=design.claim_boundary,
    )

    invocation_new_runs = 0
    campaign_results: dict[str, Any] = {}
    longhaul_cache: dict[tuple[str, int], tuple[tuple[str, str], ...]] = {}
    if main_corridor_edges:
        longhaul_cache[
            (
                CENTRAL_TRUNK_TARGET_SEGMENT,
                int(design.defaults["corridor_path_count"]),
            )
        ] = tuple(main_corridor_edges)
    for campaign_id in selected_campaigns:
        planned = plan_campaign_conditions(design, campaign_id, stage)
        output_paths = campaign_paths[campaign_id]
        checkpoint_path = output_paths["checkpoint"]
        results_path = output_paths["results"]
        manifest_path = output_paths["manifest"]
        journal = CheckpointJournal(
            checkpoint_path,
            repair_truncated_tail=resume,
        )
        existing_rows = _checkpoint_rows(journal.records) if resume else {}
        completed_keys = set(journal.completed_keys) if resume else set()

        prepared: list[
            tuple[PlannedCondition, nx.DiGraph, PreparedDisruption, RunSpec]
        ] = []
        for condition in planned:
            graph = graphs[condition.graph_scope]
            graph_scope_comparison = condition.campaign_id == "graph_scope"
            selection_graph = (
                graphs[graph_scope_freeze_id]
                if graph_scope_comparison
                else graphs[main_scope_id]
            )
            selected_edges = (
                graph_scope_frozen_edges
                if graph_scope_comparison
                else main_frozen_edges
            )
            selection_errors = (
                graph_scope_frozen_errors
                if graph_scope_comparison
                else main_frozen_errors
            )
            disruption = _prepare_disruption(
                condition,
                selection_graph=selection_graph,
                execution_graph=graph,
                scenario_lookup=scenario_lookup,
                frozen_edges=selected_edges,
                frozen_errors=selection_errors,
                longhaul_cache=longhaul_cache,
                region=inputs.region,
            )
            prepared.append(
                (condition, graph, disruption, _run_spec_for(condition, disruption))
            )

        planned_keys = {item[3].run_key for item in prepared}
        resumed_at_start = planned_keys.intersection(completed_keys)
        rows_by_key = {
            key: row
            for key, row in existing_rows.items()
            if key in planned_keys
        }
        if not _is_nonempty_file(checkpoint_path):
            _write_resume_preflight_manifest(
                manifest_path,
                design=design,
                campaign_id=campaign_id,
                stage=stage,
                implementation_provenance=implementation_provenance,
                runtime_provenance=runtime_provenance,
                input_provenance=input_provenance,
            )
        new_run_count = 0
        for condition, graph, disruption, run_spec in prepared:
            if run_spec.run_key in completed_keys:
                continue
            if max_runs is not None and invocation_new_runs >= max_runs:
                break
            raw_row = execute_condition(
                graph,
                base_config,
                condition,
                disruption=disruption,
            )
            row = _completed_row(raw_row, condition, run_spec)
            appended = journal.append(run_spec, row)
            if not appended:
                raise CheckpointError(
                    f"run key appeared during single-process append: {run_spec.run_key}"
                )
            completed_keys.add(run_spec.run_key)
            rows_by_key[run_spec.run_key] = row
            invocation_new_runs += 1
            new_run_count += 1

        ordered_rows = [
            rows_by_key[item[3].run_key]
            for item in prepared
            if item[3].run_key in rows_by_key
        ]
        _write_results(results_path, ordered_rows)
        manifest = _campaign_manifest(
            design=design,
            campaign_id=campaign_id,
            stage=stage,
            planned=planned,
            ordered_rows=ordered_rows,
            resumed_run_count=len(resumed_at_start),
            new_run_count=new_run_count,
            resume=resume,
            max_runs=max_runs,
            graphs=graphs,
            main_frozen_edges=main_frozen_edges,
            main_corridor_edges=main_corridor_edges,
            main_frozen_errors=main_frozen_errors,
            graph_scope_frozen_edges=graph_scope_frozen_edges,
            graph_scope_corridor_edges=graph_scope_corridor_edges,
            graph_scope_frozen_errors=graph_scope_frozen_errors,
            profile_metadata=profile_metadata,
            input_artifacts=input_artifacts,
            input_fingerprint=input_provenance["fingerprint"],
            implementation_provenance=implementation_provenance,
            runtime_provenance=runtime_provenance,
            graph_route_evidence=graph_route_evidence,
            corridor_scope_evidence=corridor_scope_evidence,
            graph_scope_cache=graph_scope_cache_evidence,
            paths={
                **input_paths,
                "results": results_path,
                "checkpoint": checkpoint_path,
            },
        )
        _atomic_write_json(manifest_path, manifest)
        campaign_results[campaign_id] = {
            "planned_run_count": len(planned),
            "completed_run_count": len(ordered_rows),
            "new_run_count": new_run_count,
            "results_path": results_path,
            "checkpoint_path": checkpoint_path,
            "manifest_path": manifest_path,
        }
        del prepared, ordered_rows, rows_by_key, existing_rows, completed_keys
        gc.collect()
        _print_memory_usage(campaign_id, new_run_count)

    return {
        "design_id": design.design_id,
        "stage": stage,
        "output_root": resolved_output_root,
        "new_run_count": invocation_new_runs,
        "implementation_fingerprint": implementation_provenance["fingerprint"],
        "runtime_fingerprint": runtime_provenance["fingerprint"],
        "input_fingerprint": input_provenance["fingerprint"],
        "graph_scope_route_evidence": graph_route_evidence,
        "corridor_target_scope_evidence": corridor_scope_evidence,
        "graph_scope_cache": graph_scope_cache_evidence,
        "campaigns": campaign_results,
    }


def _build_graph_scopes(
    full_graph: nx.DiGraph,
    cache: GraphScopeCacheResult,
) -> dict[str, nx.DiGraph]:
    graphs: dict[str, nx.DiGraph] = {"full": full_graph}
    for count, graph in cache.graphs.items():
        graphs[f"top{count}"] = graph
    return graphs


def _graph_scope_cache_evidence(
    cache: GraphScopeCacheResult,
) -> dict[str, Any]:
    return {
        "status": cache.status,
        "manifest_path": str(cache.manifest_path),
        "progress_path": str(cache.progress_path),
        "schema_version": cache.manifest.get("schema_version"),
        "method_version": cache.manifest.get("method_version"),
        "source_graphml_sha256": cache.manifest.get("source_graphml_sha256"),
        "builder_fingerprint": cache.manifest.get("builder_fingerprint"),
        "scope_input_fingerprint": cache.manifest.get(
            "scope_input_fingerprint"
        ),
        "scopes": cache.manifest.get("scopes", {}),
    }


def _print_graph_scope_progress(event: Mapping[str, Any]) -> None:
    name = str(event.get("event", "progress"))
    details = []
    for key in ("leg", "scope", "candidate_count", "nodes", "edges"):
        if key in event:
            details.append(f"{key}={event[key]}")
    suffix = f" ({', '.join(details)})" if details else ""
    print(f"graph-scope cache: {name}{suffix}", flush=True)


def _freeze_scenario_edges(
    selection_graph: nx.DiGraph,
    scenarios: Sequence[DisruptionScenario],
    *,
    corridor_path_count: int | None = None,
) -> tuple[
    dict[str, tuple[tuple[str, str], ...]],
    dict[str, str],
]:
    """Select physical scenario edges once on one declared selection scope."""

    frozen: dict[str, tuple[tuple[str, str], ...]] = {}
    errors: dict[str, str] = {}
    corridor_edges_cache: tuple[tuple[Any, Any], ...] | None = None
    for scenario in scenarios:
        if scenario.selection_method == "rail_param":
            frozen[scenario.scenario_id] = ()
            continue
        try:
            if scenario.selection_method == "corridor_time_band":
                if corridor_edges_cache is None:
                    corridor_edges_cache = select_corridor_time_band_edges(
                        selection_graph,
                        source="A",
                        target="D",
                        path_count=corridor_path_count,
                    )
                corridor_edges = corridor_edges_cache
                missing = [
                    edge for edge in corridor_edges
                    if not selection_graph.has_edge(*edge)
                ]
                if missing:
                    raise ValueError(
                        "corridor candidate edges absent from selection graph: "
                        f"missing_count={len(missing)}"
                    )
                frozen[scenario.scenario_id] = tuple(
                    (str(u), str(v)) for u, v in corridor_edges
                )
                continue
            selected = select_candidate_edges(selection_graph, scenario)
        except ValueError as exc:
            errors[scenario.scenario_id] = str(exc)
            continue
        frozen[scenario.scenario_id] = tuple(
            (str(item.edge[0]), str(item.edge[1])) for item in selected
        )
    return frozen, errors


def _prepare_disruption(
    condition: PlannedCondition,
    *,
    selection_graph: nx.DiGraph,
    execution_graph: nx.DiGraph,
    scenario_lookup: Mapping[str, DisruptionScenario],
    frozen_edges: Mapping[str, tuple[tuple[str, str], ...]],
    frozen_errors: Mapping[str, str],
    longhaul_cache: dict[tuple[str, int], tuple[tuple[str, str], ...]],
    region: Mapping[str, Any],
) -> PreparedDisruption:
    if condition.campaign_id in {"demand_fleet", "adaptive_policies"}:
        return PreparedDisruption.none()
    if condition.campaign_id == "random_threat_outer":
        count = int(condition.parameters["blocked_edge_count"])
        if condition.threat_seed is None:
            raise ValueError("random threat condition requires threat_seed")
        edges = select_seeded_random_edges(
            selection_graph,
            count=count,
            seed=condition.threat_seed,
        )
        _assert_edges_present(execution_graph, edges, condition)
        return PreparedDisruption(edges, "blocked", 0.0, 1.0)
    if condition.campaign_id in {"break_even", "break_even_fine", "road_rail_map", "morris"}:
        target_segment = str(
            condition.parameters.get(
                "target_segment", CENTRAL_TRUNK_TARGET_SEGMENT
            )
        )
        if target_segment != CENTRAL_TRUNK_TARGET_SEGMENT:
            raise ValueError(
                "long-haul revision condition must target "
                f"{CENTRAL_TRUNK_TARGET_SEGMENT}"
            )
        selected_path_count = condition.corridor_path_count or 3
        cache_key = (target_segment, int(selected_path_count))
        edges = longhaul_cache.get(cache_key)
        if edges is None:
            edges = select_corridor_time_band_edges(
                selection_graph,
                source="A",
                target="D",
                path_count=int(selected_path_count),
                lower_fraction=0.2,
                upper_fraction=0.8,
            )
            longhaul_cache[cache_key] = edges
        _assert_edges_present(execution_graph, edges, condition)
        multiplier = _condition_road_multiplier(condition)
        return PreparedDisruption(edges, "capacity_reduction", 1.0, multiplier)

    if condition.campaign_id == "path_interdiction_threat":
        k = int(condition.parameters.get("interdiction_k", 3))
        source = str(region["assembly_zones"][0]["id"])
        target = str(region["destination_zones"][0]["id"])
        try:
            shortest_path = nx.shortest_path(selection_graph, source=source, target=target, weight="t0")
        except nx.NetworkXNoPath:
            raise ValueError(f"path_interdiction_threat: no A->D path exists")
        path_edges = list(zip(shortest_path[:-1], shortest_path[1:]))
        if len(path_edges) <= k:
            edges = path_edges
        else:
            edge_weights = []
            for u, v in path_edges:
                wt = selection_graph[u][v].get("t0", 1.0)
                impact = wt * selection_graph[u][v].get("capacity", 1.0)
                edge_weights.append((impact, (u, v)))
            edge_weights.sort(reverse=True)
            edges = [edge for _, edge in edge_weights[:k]]
        _assert_edges_present(execution_graph, edges, condition)
        return PreparedDisruption(edges, "blocked", 0.0, 1.0)

    if condition.rail_status == "unavailable" or condition.scenario_id == "no_disruption":
        return PreparedDisruption.none()
    try:
        scenario = scenario_lookup[condition.scenario_id]
    except KeyError as exc:
        raise KeyError(
            f"planned scenario missing from scenario CSV: {condition.scenario_id!r}"
        ) from exc
    if scenario.selection_method == "rail_param":
        return PreparedDisruption.none()
    if condition.scenario_id in frozen_errors:
        raise ValueError(
            "scenario cannot be represented on declared selection graph: "
            f"{condition.scenario_id}: {frozen_errors[condition.scenario_id]}"
        )
    edges = frozen_edges.get(condition.scenario_id, ())
    if not edges:
        raise ValueError(
            f"scenario has no frozen road edges: {condition.scenario_id}"
        )
    _assert_edges_present(execution_graph, edges, condition)
    mode = str(scenario.disruption_mode)
    capacity = 0.0 if mode == "blocked" else float(scenario.capacity_factor)
    multiplier = (
        1.0
        if scenario.road_travel_time_multiplier is None
        else float(scenario.road_travel_time_multiplier)
    )
    return PreparedDisruption(edges, mode, capacity, multiplier)


def _condition_road_multiplier(condition: PlannedCondition) -> float:
    factors = condition.parameters.get("factor_values", {})
    if isinstance(factors, Mapping) and "road_longhaul_multiplier" in factors:
        return float(factors["road_longhaul_multiplier"])
    return float(condition.parameters.get("road_multiplier", 1.0))


def _assert_edges_present(
    graph: nx.DiGraph,
    edges: Sequence[tuple[str, str]],
    condition: PlannedCondition,
) -> None:
    missing = [edge for edge in edges if not graph.has_edge(*edge)]
    if missing:
        raise ValueError(
            f"selected edges absent from {condition.graph_scope}: "
            f"missing_count={len(missing)}"
        )


def _edge_selection_audit(
    graph: nx.DiGraph,
    edges: Sequence[tuple[str, str]],
) -> dict[str, Any]:
    """Return coordinate-free evidence that a target contains physical roads."""

    selected = tuple(dict.fromkeys(tuple(edge) for edge in edges))
    missing = [edge for edge in selected if not graph.has_edge(*edge)]
    if missing:
        raise ValueError(
            "edge-selection audit found missing edges: "
            f"missing_count={len(missing)}"
        )
    non_road = 0
    connectors = 0
    nonpositive_length = 0
    for edge in selected:
        data = graph.edges[edge]
        non_road += int(data.get("mode", "road") != "road")
        connectors += int(
            data.get("source") == "connector"
            or data.get("highway") == "connector"
        )
        raw_length = data.get("length_m")
        if raw_length is not None:
            try:
                length = float(raw_length)
            except (TypeError, ValueError, OverflowError):
                nonpositive_length += 1
            else:
                nonpositive_length += int(not math.isfinite(length) or length <= 0.0)

    road = nx.subgraph_view(
        graph,
        filter_edge=lambda u, v: graph.edges[u, v].get("mode", "road") == "road",
    )
    selected_set = set(selected)
    endpoint_overlaps: dict[str, int | None] = {}
    endpoint_status: dict[str, str] = {}
    for label, source, target in (
        ("A_to_S", "A", "S"),
        ("S_to_A", "S", "A"),
        ("R_to_D", "R", "D"),
        ("D_to_R", "D", "R"),
    ):
        try:
            path = nx.shortest_path(road, source, target, weight="t0")
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            endpoint_overlaps[label] = None
            endpoint_status[label] = "unavailable"
            continue
        endpoint_status[label] = "available"
        endpoint_overlaps[label] = len(
            selected_set.intersection(zip(path, path[1:]))
        )
    return {
        "selected_edge_count": len(selected),
        "selected_edge_checksum": selected_edges_checksum(selected),
        "non_road_edge_count": non_road,
        "connector_edge_count": connectors,
        "nonpositive_length_edge_count": nonpositive_length,
        "endpoint_shortest_path_overlap_counts": endpoint_overlaps,
        "endpoint_shortest_path_status": endpoint_status,
        "contains_coordinates": False,
    }


def _random_threat_selection_audit(
    graph: nx.DiGraph,
    planned: Sequence[PlannedCondition],
) -> dict[str, Any]:
    """Recompute unique outer-threat draws and summarize target hygiene."""

    draw_specs = sorted(
        {
            (int(item.threat_seed), int(item.parameters["blocked_edge_count"]))
            for item in planned
            if item.campaign_id == "random_threat_outer"
            and item.threat_seed is not None
        }
    )
    checksums: set[str] = set()
    edge_counts: set[int] = set()
    maximums = {
        "non_road": 0,
        "connector": 0,
        "nonpositive_length": 0,
    }
    for seed, count in draw_specs:
        selected = select_seeded_random_edges(graph, count=count, seed=seed)
        checksums.add(selected_edges_checksum(selected))
        edge_counts.add(len(selected))
        for edge in selected:
            data = graph.edges[edge]
            maximums["non_road"] = max(
                maximums["non_road"],
                int(data.get("mode", "road") != "road"),
            )
            maximums["connector"] = max(
                maximums["connector"],
                int(
                    data.get("source") == "connector"
                    or data.get("highway") == "connector"
                ),
            )
            raw_length = data.get("length_m")
            invalid_length = 0
            if raw_length is not None:
                try:
                    length = float(raw_length)
                except (TypeError, ValueError, OverflowError):
                    invalid_length = 1
                else:
                    invalid_length = int(
                        not math.isfinite(length) or length <= 0.0
                    )
            maximums["nonpositive_length"] = max(
                maximums["nonpositive_length"], invalid_length
            )
    return {
        "threat_draw_count": len(draw_specs),
        "selected_edge_count_values": sorted(edge_counts),
        "distinct_selected_edge_checksum_count": len(checksums),
        "max_non_road_edge_count": maximums["non_road"],
        "max_connector_edge_count": maximums["connector"],
        "max_nonpositive_length_edge_count": maximums["nonpositive_length"],
        "contains_coordinates": False,
    }


def _run_spec_for(
    condition: PlannedCondition,
    disruption: PreparedDisruption,
) -> RunSpec:
    effective_rail_status, _ = effective_rail_condition(condition)
    return RunSpec(
        campaign_id=condition.campaign_id,
        configuration_id=condition.configuration_id,
        policy_id=condition.policy_id,
        departure_policy_id=str(
            condition.parameters.get("departure_policy_id", "strict")
        ),
        resource_frame=condition.resource_frame,
        graph_scope=condition.graph_scope,
        corridor_path_count=condition.corridor_path_count,
        arrival_seed=condition.arrival_seed,
        threat_seed=condition.threat_seed,
        threat_draw=condition.threat_draw,
        selected_edges_checksum=selected_edges_checksum(disruption.edges),
        rail_status=effective_rail_status,
        return_strategy=str(
            condition.parameters.get("return_strategy", "reverse_network")
        ),
    )


def _completed_row(
    raw_row: Mapping[str, Any],
    condition: PlannedCondition,
    run_spec: RunSpec,
) -> dict[str, Any]:
    if not isinstance(raw_row, Mapping):
        raise TypeError("execute_condition must return a mapping")
    row = _json_safe(raw_row)
    existing_key = row.get("run_key")
    if existing_key is not None and existing_key != run_spec.run_key:
        raise RuntimeError("execute_condition run_key disagrees with prepared run spec")
    row.update(run_spec.to_mapping())
    row["run_key"] = run_spec.run_key
    row.setdefault("scenario_id", condition.scenario_id)
    return row


def _checkpoint_rows(
    records: Sequence[Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for record_number, record in enumerate(records, start=1):
        if not isinstance(record, dict) or not isinstance(record.get("result"), dict):
            raise CheckpointError(
                f"checkpoint record {record_number} must contain object result"
            )
        key = record.get("run_key")
        if not isinstance(key, str) or len(key) != 64:
            raise CheckpointError(
                f"checkpoint line {record_number} has invalid run_key"
            )
        if key in rows:
            raise CheckpointError(f"checkpoint contains duplicate run_key: {key}")
        result = dict(record["result"])
        result.setdefault("run_key", key)
        rows[key] = result
    return rows


def _write_results(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path = assert_isolated_output_path(path)
    if rows:
        write_campaign_csv(path, rows)
        return
    _atomic_replace_bytes(path, b"run_key\n")


def _campaign_manifest(
    *,
    design: RevisionExperimentDesign,
    campaign_id: str,
    stage: str,
    planned: Sequence[PlannedCondition],
    ordered_rows: Sequence[Mapping[str, Any]],
    resumed_run_count: int,
    new_run_count: int,
    resume: bool,
    max_runs: int | None,
    graphs: Mapping[str, nx.DiGraph],
    main_frozen_edges: Mapping[str, Sequence[tuple[str, str]]],
    main_corridor_edges: Sequence[tuple[str, str]],
    main_frozen_errors: Mapping[str, str],
    graph_scope_frozen_edges: Mapping[str, Sequence[tuple[str, str]]],
    graph_scope_corridor_edges: Sequence[tuple[str, str]],
    graph_scope_frozen_errors: Mapping[str, str],
    profile_metadata: Mapping[str, Any],
    input_artifacts: Mapping[str, Mapping[str, Any]],
    input_fingerprint: str,
    implementation_provenance: Mapping[str, Any],
    runtime_provenance: Mapping[str, Any],
    graph_route_evidence: Mapping[str, Any],
    corridor_scope_evidence: Mapping[str, Any],
    graph_scope_cache: Mapping[str, Any],
    paths: Mapping[str, Path],
) -> dict[str, Any]:
    completed = len(ordered_rows)
    planned_count = len(planned)
    graph_stats = {
        scope: {"nodes": graph.number_of_nodes(), "edges": graph.number_of_edges()}
        for scope, graph in graphs.items()
    }
    main_scope_id = str(design.defaults["graph_scope"])
    graph_scope_freeze_id = str(
        design.campaign("graph_scope")["freeze_selected_edges_from"]
    )
    scope_records = graph_scope_cache.get("scopes", {})
    main_scope_record = (
        scope_records.get(main_scope_id, {})
        if isinstance(scope_records, Mapping)
        else {}
    )
    main_candidate_method = (
        main_scope_record.get("candidate_method")
        if isinstance(main_scope_record, Mapping)
        else None
    )
    if not isinstance(main_candidate_method, str):
        main_candidate_method = str(design.defaults["graph_scope_method"])
    output_names = ("results", "checkpoint")
    return {
        "schema_version": 1,
        "final_study_ready": False,
        "design_id": design.design_id,
        "campaign_id": campaign_id,
        "stage": stage,
        "status": "complete" if completed == planned_count else "partial",
        "claim_boundary": design.claim_boundary,
        "canonical_results_read_only": str(design.canonical_results_read_only),
        "planned_run_count": planned_count,
        "completed_run_count": completed,
        "pending_run_count": planned_count - completed,
        "resumed_run_count": resumed_run_count,
        "new_run_count": new_run_count,
        "resume_enabled": resume,
        "max_runs": max_runs,
        "graph_loaded_once": True,
        "graph_scopes": graph_stats,
        "main_execution_scope": main_scope_id,
        "main_corridor_path_count": design.defaults["corridor_path_count"],
        "main_scope_candidate_method": main_candidate_method,
        "main_scope_interpretation": str(
            design.defaults["graph_scope_interpretation"]
        ),
        "edge_selection_scopes": {
            "main_campaigns": main_scope_id,
            "graph_scope_campaign": graph_scope_freeze_id,
        },
        "central_trunk_target_segment": CENTRAL_TRUNK_TARGET_SEGMENT,
        "central_trunk_selection_method": "corridor_time_band",
        "central_trunk_target_audit": _edge_selection_audit(
            graphs[main_scope_id], main_corridor_edges
        ),
        "graph_scope_fixed_target_audit": {
            "selection_scope": graph_scope_freeze_id,
            **_edge_selection_audit(
                graphs[graph_scope_freeze_id], graph_scope_corridor_edges
            ),
        },
        "random_threat_candidate_rule": (
            "physical_road_edges_excluding_synthetic_connectors"
        ),
        "random_threat_selection_audit": (
            _random_threat_selection_audit(graphs[main_scope_id], planned)
            if campaign_id == "random_threat_outer"
            else None
        ),
        "main_scenario_edge_checksums": {
            scenario_id: selected_edges_checksum(edges)
            for scenario_id, edges in sorted(main_frozen_edges.items())
        },
        "graph_scope_scenario_edge_checksums": {
            scenario_id: selected_edges_checksum(edges)
            for scenario_id, edges in sorted(graph_scope_frozen_edges.items())
        },
        "main_unrepresented_scenarios": dict(sorted(main_frozen_errors.items())),
        "graph_scope_unrepresented_scenarios": dict(
            sorted(graph_scope_frozen_errors.items())
        ),
        "profile_inputs": _json_safe(profile_metadata),
        "paths": {name: str(path) for name, path in paths.items()},
        "input_artifacts": _json_safe(input_artifacts),
        "input_fingerprint": input_fingerprint,
        "implementation_fingerprint": implementation_provenance["fingerprint"],
        "implementation_artifacts": _json_safe(
            implementation_provenance["artifacts"]
        ),
        "runtime_fingerprint": runtime_provenance["fingerprint"],
        "runtime_environment": _json_safe(runtime_provenance),
        "graph_scope_route_evidence": _json_safe(graph_route_evidence),
        "corridor_target_scope_evidence": _json_safe(corridor_scope_evidence),
        "graph_scope_cache": _json_safe(graph_scope_cache),
        "output_artifacts": {
            name: _artifact_record(paths[name]) for name in output_names
        },
        "written_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def _campaign_output_paths(
    output_root: Path,
    campaign_id: str,
    stage: str,
) -> dict[str, Path]:
    campaign_dir = assert_isolated_output_path(output_root / campaign_id)
    return {
        "checkpoint": campaign_dir / f"{stage}_checkpoint.jsonl",
        "results": campaign_dir / f"{stage}_results.csv",
        "manifest": campaign_dir / f"{stage}_manifest.json",
    }


def _implementation_provenance() -> dict[str, Any]:
    """Hash every Python file whose semantics can affect revision outputs."""

    relative_paths = set(IMPLEMENTATION_RELATIVE_PATHS)
    relative_paths.update(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "src").rglob("*.py")
        if path.is_file()
    )
    artifacts: dict[str, dict[str, Any]] = {}
    fingerprint_entries: list[dict[str, str]] = []
    for relative_path in sorted(relative_paths):
        artifact = _artifact_record(ROOT / relative_path)
        sha256 = artifact.get("sha256")
        if not isinstance(sha256, str) or len(sha256) != 64:
            raise FileNotFoundError(
                f"active implementation file is missing: {relative_path}"
            )
        artifacts[relative_path] = artifact
        fingerprint_entries.append(
            {"relative_path": relative_path, "sha256": sha256}
        )
    encoded = json.dumps(
        fingerprint_entries,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return {
        "fingerprint": hashlib.sha256(encoded).hexdigest(),
        "artifacts": artifacts,
    }


def _input_provenance(paths: Mapping[str, Path]) -> dict[str, Any]:
    """Hash seven named run inputs without binding identity to local paths."""

    names = set(paths)
    required = set(INPUT_ARTIFACT_NAMES)
    if names != required:
        missing = sorted(required - names)
        unexpected = sorted(names - required)
        raise ValueError(
            "input provenance requires exact artifact set: "
            f"missing={missing}, unexpected={unexpected}"
        )
    artifacts: dict[str, dict[str, Any]] = {}
    fingerprint_entries: list[dict[str, str]] = []
    for name in sorted(INPUT_ARTIFACT_NAMES):
        artifact = _artifact_record(Path(paths[name]))
        sha256 = artifact.get("sha256")
        if (
            not isinstance(sha256, str)
            or len(sha256) != 64
            or any(character not in "0123456789abcdefABCDEF" for character in sha256)
        ):
            raise FileNotFoundError(
                f"required input artifact is missing or unreadable: {name}"
            )
        artifacts[name] = artifact
        fingerprint_entries.append({"name": name, "sha256": sha256.lower()})
    encoded = json.dumps(
        fingerprint_entries,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return {
        "fingerprint": hashlib.sha256(encoded).hexdigest(),
        "artifacts": artifacts,
    }


def _runtime_provenance() -> dict[str, Any]:
    """Return package/runtime identity used to prevent mixed checkpoints."""

    package_names = ("networkx", "numpy", "scipy", "SALib", "PyYAML")
    packages: dict[str, str] = {}
    for name in package_names:
        try:
            packages[name] = package_metadata.version(name)
        except package_metadata.PackageNotFoundError as exc:
            raise RuntimeError(f"required runtime package is missing: {name}") from exc
    identity = {
        "python": {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
        },
        "packages": packages,
    }
    encoded = json.dumps(
        identity,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return {
        "fingerprint": hashlib.sha256(encoded).hexdigest(),
        **identity,
        "executable": str(Path(sys.executable).resolve()),
    }


def _assert_resume_implementation_matches(
    *,
    checkpoint_path: Path,
    manifest_path: Path,
    implementation_fingerprint: str,
    runtime_fingerprint: str,
    input_fingerprint: str,
) -> None:
    """Reject checkpoint mixing when implementation, runtime, or inputs changed."""

    if not _is_nonempty_file(checkpoint_path):
        return
    if not manifest_path.is_file():
        raise CheckpointError(
            "cannot resume nonempty checkpoint without prior stage manifest; "
            "rerun with --no-resume to replace checkpoint/results"
        )
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CheckpointError(
            "cannot resume nonempty checkpoint because prior stage manifest is "
            "unreadable; rerun with --no-resume to replace checkpoint/results"
        ) from exc
    if not isinstance(manifest, Mapping):
        raise CheckpointError(
            "cannot resume nonempty checkpoint because prior stage manifest is "
            "not an object; rerun with --no-resume to replace checkpoint/results"
        )
    previous = manifest.get("implementation_fingerprint")
    if previous != implementation_fingerprint:
        prior_text = previous if isinstance(previous, str) else "missing"
        raise CheckpointError(
            "implementation fingerprint mismatch for nonempty checkpoint: "
            f"prior={prior_text}, current={implementation_fingerprint}; "
            "rerun with --no-resume to replace checkpoint/results"
        )
    previous_runtime = manifest.get("runtime_fingerprint")
    if previous_runtime != runtime_fingerprint:
        prior_text = (
            previous_runtime if isinstance(previous_runtime, str) else "missing"
        )
        raise CheckpointError(
            "runtime fingerprint mismatch for nonempty checkpoint: "
            f"prior={prior_text}, current={runtime_fingerprint}; "
            "rerun with --no-resume to replace checkpoint/results"
        )
    previous_input = manifest.get("input_fingerprint")
    if previous_input != input_fingerprint:
        prior_text = previous_input if isinstance(previous_input, str) else "missing"
        raise CheckpointError(
            "input fingerprint mismatch for nonempty checkpoint: "
            f"prior={prior_text}, current={input_fingerprint}; "
            "rerun with --no-resume to replace checkpoint/results"
        )


def _write_resume_preflight_manifest(
    path: Path,
    *,
    design: RevisionExperimentDesign,
    campaign_id: str,
    stage: str,
    implementation_provenance: Mapping[str, Any],
    runtime_provenance: Mapping[str, Any],
    input_provenance: Mapping[str, Any],
) -> None:
    """Persist implementation, runtime, and input identity before first append."""

    _atomic_write_json(
        path,
        {
            "schema_version": 1,
            "final_study_ready": False,
            "design_id": design.design_id,
            "campaign_id": campaign_id,
            "stage": stage,
            "status": "running",
            "input_fingerprint": input_provenance["fingerprint"],
            "input_artifacts": input_provenance["artifacts"],
            "implementation_fingerprint": implementation_provenance["fingerprint"],
            "implementation_artifacts": implementation_provenance["artifacts"],
            "runtime_fingerprint": runtime_provenance["fingerprint"],
            "runtime_environment": runtime_provenance,
            "written_at_utc": datetime.now(timezone.utc).isoformat(),
        },
    )


def _is_nonempty_file(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 0


def _normalize_campaign_ids(values: Sequence[str]) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        values = (str(values),)
    normalized = tuple(str(value).strip() for value in values if str(value).strip())
    if not normalized:
        raise ValueError("at least one campaign is required")
    if "all" in normalized:
        if normalized != ("all",):
            raise ValueError("campaign 'all' cannot be combined with named campaigns")
        return tuple(EXPECTED_CAMPAIGNS)
    unknown = sorted(set(normalized) - set(EXPECTED_CAMPAIGNS))
    if unknown:
        raise ValueError(f"unknown revision campaigns: {unknown}")
    if len(set(normalized)) != len(normalized):
        raise ValueError("campaign values must not contain duplicates")
    return normalized


def _resolve_output_root(
    design: RevisionExperimentDesign,
    override: str | Path | None,
) -> Path:
    selected = Path(override) if override is not None else design.output_root
    if not selected.is_absolute():
        selected = ROOT / selected
    return selected


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    item_method = getattr(value, "item", None)
    if callable(item_method):
        return _json_safe(item_method())
    raise TypeError(f"value is not JSON-safe: {type(value).__name__}")


def _atomic_write_json(path: Path, value: Mapping[str, Any]) -> None:
    encoded = (
        json.dumps(
            _json_safe(value),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    _atomic_replace_bytes(path, encoded)


def _artifact_record(path: Path) -> dict[str, Any]:
    resolved = path.expanduser().resolve()
    return {
        "path": str(resolved),
        "sha256": _sha256_file(resolved) if resolved.is_file() else None,
        "size_bytes": resolved.stat().st_size if resolved.is_file() else None,
    }


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_replace_bytes(path: str | Path, content: bytes) -> None:
    target = assert_isolated_output_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(
        dir=target.parent,
        prefix=f".{target.name}.",
        suffix=".tmp",
    )
    temp_path = Path(temp_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, target)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def _positive_int(raw: str) -> int:
    value = int(raw)
    if value < 1:
        raise argparse.ArgumentTypeError("value must be a positive integer")
    return value


def _print_memory_usage(campaign_id: str, new_run_count: int) -> None:
    pass  # memory tracking disabled; gc.collect() handles cleanup


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run isolated paper-revision experiment campaigns."
    )
    parser.add_argument(
        "--design",
        "--design-path",
        dest="design_path",
        type=Path,
        default=DEFAULT_DESIGN_PATH,
    )
    parser.add_argument(
        "--campaign",
        action="append",
        required=True,
        help="Repeat for named campaigns, or pass 'all' alone.",
    )
    parser.add_argument("--stage", choices=("smoke", "full"), default="smoke")
    parser.add_argument(
        "--region", "--region-path", dest="region_path", type=Path, required=True
    )
    parser.add_argument(
        "--cache", "--cache-path", dest="cache_path", type=Path, required=True
    )
    parser.add_argument(
        "--overrides",
        "--road-class-overrides-path",
        dest="overrides_path",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--scenarios",
        "--scenarios-path",
        dest="scenarios_path",
        type=Path,
        required=True,
    )
    parser.add_argument("--output-root", type=Path, default=None)
    parser.add_argument("--max-runs", type=_positive_int, default=None)
    parser.add_argument("--no-resume", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    result = run_revision_campaigns(
        design_path=args.design_path,
        campaign_ids=args.campaign,
        stage=args.stage,
        region_path=args.region_path,
        cache_path=args.cache_path,
        overrides_path=args.overrides_path,
        scenarios_path=args.scenarios_path,
        output_root=args.output_root,
        max_runs=args.max_runs,
        resume=not args.no_resume,
    )
    print(
        f"revision campaigns: {len(result['campaigns'])}; "
        f"new runs: {result['new_run_count']}"
    )
    for campaign_id, campaign in result["campaigns"].items():
        print(
            f"{campaign_id}: {campaign['completed_run_count']}/"
            f"{campaign['planned_run_count']} -> {campaign['results_path']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
