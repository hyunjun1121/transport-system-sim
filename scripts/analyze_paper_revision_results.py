"""Analyze isolated paper-revision campaign CSV outputs.

The command never writes into canonical pilot results.  It preserves failed,
missing, and partial-completion runs as explicit exclusions; finite makespan
inference is performed only for policy pairs with equal completion rates.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
from importlib import metadata as package_metadata
import json
import math
from pathlib import Path
import platform
import sys
from typing import Any, Callable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.realworld.revision_analysis import (
    break_even_from_rows,
    graph_scope_stability_table,
    hierarchical_paired_delta_summaries,
    paired_replicate_convergence,
    summarize_paired_makespan,
)
from src.realworld.revision_campaign import assert_isolated_output_path
from src.realworld.revision_design import (
    EXPECTED_CAMPAIGNS,
    EXPECTED_MORRIS_FACTORS,
    RevisionExperimentDesign,
    load_revision_design,
)
from src.realworld.revision_graph_validation import CANONICAL_PUBLIC_ROAD_LEGS
from src.realworld.revision_morris import (
    MorrisDesign,
    aggregate_morris_outcomes,
    analyze_morris,
    sample_morris,
)
from src.realworld.revision_runner import write_campaign_csv
from src.realworld.revision_statistics import crossed_two_way_bootstrap_ci


DEFAULT_DESIGN_PATH = (
    ROOT / "data" / "manifests" / "paper_revision_experiment_design.json"
)
LEFT_POLICY = "bus_only"
RIGHT_POLICY = "static_multimodal"
EXPECTED_INPUT_ARTIFACTS = frozenset(
    {
        "design",
        "region",
        "cache",
        "overrides",
        "scenarios",
        "demand_profiles",
        "fleet_profiles",
    }
)

_INTEGER_FIELDS = frozenset(
    {
        "arrival_seed",
        "threat_seed",
        "threat_draw",
        "corridor_path_count",
        "demand",
        "road_fleet_total",
        "morris_point",
        "morris_trajectory",
        "selected_edge_count",
        "analysis_graph_nodes",
        "analysis_graph_edges",
        "censored_count",
        "vehicle_cycles",
        "road_vehicle_cycles",
        "road_deployed_seat_capacity",
        "road_boarded_passengers",
        "rail_deployed_seat_capacity",
        "rail_boarded_passengers",
        "empty_return_trips",
        "train_trips",
        "graph_node_count",
        "graph_edge_count",
        "path_edge_count",
        "path_diversity_limit",
        "path_diversity_count",
        "full_path_edge_count",
        "selected_target_edge_count",
        "selected_target_edges_present",
        "path_target_edge_count",
        "interdiction_k",
    }
)
_FLOAT_FIELDS = frozenset(
    {
        "completion_rate",
        "makespan",
        "makespan_min",
        "penalized_makespan",
        "rail_multiplier",
        "road_multiplier",
        "road_travel_time_multiplier",
        "disruption_capacity_factor",
        "road_longhaul_multiplier",
        "rail_travel_multiplier",
        "transfer_time_min",
        "arrival_sigma",
        "empty_return_minutes",
        "mean_vehicle_load_factor",
        "road_mean_vehicle_load_factor",
        "rail_mean_load_factor",
        "assembly_wait_minutes",
        "transfer_wait_minutes",
        "rail_wait_minutes",
        "shortest_travel_time_min",
        "shortest_distance_m",
        "full_path_edge_overlap_ratio",
        "full_path_edge_jaccard",
        "path_target_edge_ratio",
        "full_reference_travel_time_min",
        "travel_time_ratio_vs_full",
        "travel_time_detour_ratio_vs_full",
        "distance_detour_ratio_vs_full",
    }
    | set(EXPECTED_MORRIS_FACTORS)
)

_PAIR_DIMENSIONS = (
    "scenario_id",
    "resource_frame",
    "graph_scope",
    "corridor_path_count",
    "rail_status",
    "rail_multiplier",
    "return_strategy",
    "departure_policy_id",
)
_PAIRED_FIELDS = (
    *_PAIR_DIMENSIONS,
    "total_pair_count",
    "completion_pair_count",
    "mean_bus_completion_rate",
    "mean_multimodal_completion_rate",
    "mean_completion_rate_delta_bus_minus_multimodal",
    "completion_winner",
    "completion_winner_scope",
    "completion_statistical_resolution",
    "completion_inference_basis",
    "completion_t_ci_lower",
    "completion_t_ci_upper",
    "completion_t_confidence",
    "completion_t_n",
    "completion_t_standard_error",
    "completion_bootstrap_ci_lower",
    "completion_bootstrap_ci_upper",
    "completion_bootstrap_confidence",
    "completion_bootstrap_n",
    "completion_bootstrap_replicates",
    "completion_bootstrap_seed",
    "completion_incomplete_reason_counts",
    "overall_winner",
    "overall_winner_basis",
    "finite_pair_count",
    "excluded_pair_count",
    "mean_bus_makespan",
    "mean_multimodal_makespan",
    "mean_delta_bus_minus_multimodal",
    "t_ci_lower",
    "t_ci_upper",
    "t_confidence",
    "t_n",
    "t_standard_error",
    "bootstrap_ci_lower",
    "bootstrap_ci_upper",
    "bootstrap_confidence",
    "bootstrap_n",
    "bootstrap_replicates",
    "bootstrap_seed",
    "incomplete_reason_counts",
    "comparison_scope",
)
_BREAK_EVEN_FIELDS = (
    "scenario_id",
    "resource_frame",
    "graph_scope",
    "rail_status",
    "return_strategy",
    "status",
    "crossing_road_multiplier",
    "lower_road_multiplier",
    "upper_road_multiplier",
    "lower_mean_delta",
    "upper_mean_delta",
    "bracket_count",
    "paired_mean_points",
    "joint_seed_bootstrap_ci_lower",
    "joint_seed_bootstrap_ci_upper",
    "joint_seed_bootstrap_confidence",
    "joint_seed_bootstrap_complete_seed_count",
    "joint_seed_bootstrap_excluded_seeds",
    "joint_seed_bootstrap_replicates",
    "joint_seed_bootstrap_successful_replicates",
    "joint_seed_bootstrap_seed",
)
_GRAPH_FIELDS = (
    "graph_scope",
    "normal_time_match_count",
    "normal_time_mean_absolute_error",
    "normal_time_mean_absolute_percentage_error",
    "connectivity_match_count",
    "connectivity_agreement",
    "policy_ranking_match_count",
    "policy_ranking_agreement",
)
_GRAPH_ROUTE_FIELDS = (
    "graph_scope",
    "corridor_path_count",
    "graph_node_count",
    "graph_edge_count",
    "leg_id",
    "source_id",
    "target_id",
    "connected",
    "shortest_travel_time_min",
    "shortest_distance_m",
    "distance_status",
    "path_edge_count",
    "path_signature_sha256",
    "path_diversity_limit",
    "path_diversity_count",
    "path_diversity_status",
    "path_diversity_method",
    "full_reference_connected",
    "full_path_edge_count",
    "full_path_edge_overlap_ratio",
    "full_path_edge_jaccard",
    "travel_time_detour_ratio_vs_full",
    "distance_detour_ratio_vs_full",
    "comparison_status",
)
_CORRIDOR_SCOPE_FIELDS = (
    "graph_scope",
    "corridor_path_count",
    "graph_node_count",
    "graph_edge_count",
    "road_multiplier",
    "selected_target_edge_count",
    "selected_target_edges_present",
    "selected_target_checksum",
    "connected",
    "shortest_travel_time_min",
    "path_edge_count",
    "path_target_edge_count",
    "path_target_edge_ratio",
    "path_signature_sha256",
    "full_reference_travel_time_min",
    "travel_time_ratio_vs_full",
    "comparison_status",
)
_RANDOM_FIELDS = (
    "scenario_id",
    "resource_frame",
    "graph_scope",
    "rail_status",
    "return_strategy",
    "total_pair_count",
    "finite_pair_count",
    "excluded_pair_count",
    "mean_delta_bus_minus_multimodal",
    "bootstrap_ci_lower",
    "bootstrap_ci_upper",
    "bootstrap_confidence",
    "bootstrap_replicates",
    "bootstrap_seed",
    "threat_draw_count",
    "finite_observation_count",
    "empty_threat_draws",
    "bootstrap_excluded_observation_count",
    "incomplete_reason_counts",
    "comparison_scope",
    "completion_pair_count",
    "mean_completion_rate_delta_bus_minus_multimodal",
    "completion_delta_bootstrap_ci_lower",
    "completion_delta_bootstrap_ci_upper",
    "completion_delta_bootstrap_confidence",
    "completion_delta_bootstrap_replicates",
    "completion_delta_bootstrap_seed",
    "completion_threat_draw_count",
    "completion_observation_count",
    "completion_empty_threat_draws",
    "completion_incomplete_reason_counts",
    "bus_positive_completion_probability_proxy",
    "bus_positive_completion_proxy_ci_lower",
    "bus_positive_completion_proxy_ci_upper",
    "multimodal_positive_completion_probability_proxy",
    "multimodal_positive_completion_proxy_ci_lower",
    "multimodal_positive_completion_proxy_ci_upper",
    "bus_full_completion_probability_proxy",
    "bus_full_completion_proxy_ci_lower",
    "bus_full_completion_proxy_ci_upper",
    "multimodal_full_completion_probability_proxy",
    "multimodal_full_completion_proxy_ci_lower",
    "multimodal_full_completion_proxy_ci_upper",
    "probability_proxy_confidence",
    "probability_proxy_observation_count",
    "probability_proxy_scope",
)
_RANDOM_CROSSED_FIELDS = (
    "scenario_id",
    "resource_frame",
    "graph_scope",
    "rail_status",
    "return_strategy",
    "total_pair_count",
    "finite_pair_count",
    "excluded_pair_count",
    "mean_delta_bus_minus_multimodal",
    "crossed_ci_lower",
    "crossed_ci_upper",
    "crossed_confidence",
    "crossed_replicates",
    "crossed_seed",
    "crossed_failed_replicates",
    "threat_draw_count",
    "finite_observation_count",
    "comparison_scope",
    "completion_pair_count",
    "mean_completion_rate_delta_bus_minus_multimodal",
    "completion_crossed_ci_lower",
    "completion_crossed_ci_upper",
    "completion_crossed_confidence",
    "completion_crossed_replicates",
    "completion_crossed_seed",
    "completion_crossed_failed_replicates",
    "resampling_scope",
)
_MORRIS_FIELDS = (
    "policy_id",
    "response_metric",
    "analysis_status",
    "factor_name",
    "mu",
    "mu_star",
    "sigma",
    "mu_star_conf",
    "trajectory_count",
    "sample_point_count",
    "expected_arrival_seed_count",
    "incomplete_group_count",
    "missing_seed_count",
    "nonfinite_seed_count",
    "outcome_scope",
)
_CONVERGENCE_FIELDS = (
    *_PAIR_DIMENSIONS,
    "replicate_count",
    "seed_max",
    "mean_delta_bus_minus_multimodal",
    "t_ci_lower",
    "t_ci_upper",
    "t_ci_half_width",
    "estimate_change_from_previous",
    "half_width_ratio_to_previous",
)
_DEMAND_FLEET_DIMENSIONS = (
    "demand",
    "road_fleet_total",
    "resource_frame",
    "graph_scope",
    "return_strategy",
)
_ROAD_RAIL_DIMENSIONS = (
    "road_multiplier",
    "rail_status",
    "rail_multiplier",
    "resource_frame",
    "graph_scope",
    "return_strategy",
)
_PAIR_RESULT_FIELDS = (
    "total_pair_count",
    "completion_pair_count",
    "mean_bus_completion_rate",
    "mean_multimodal_completion_rate",
    "mean_completion_rate_delta_bus_minus_multimodal",
    "completion_winner",
    "completion_winner_scope",
    "completion_statistical_resolution",
    "completion_inference_basis",
    "completion_t_ci_lower",
    "completion_t_ci_upper",
    "completion_bootstrap_ci_lower",
    "completion_bootstrap_ci_upper",
    "completion_incomplete_reason_counts",
    "overall_winner",
    "overall_winner_basis",
    "finite_pair_count",
    "excluded_pair_count",
    "mean_bus_makespan",
    "mean_multimodal_makespan",
    "mean_delta_bus_minus_multimodal",
    "t_ci_lower",
    "t_ci_upper",
    "bootstrap_ci_lower",
    "bootstrap_ci_upper",
    "incomplete_reason_counts",
    "comparison_scope",
)
_DEMAND_FLEET_FIELDS = (*_DEMAND_FLEET_DIMENSIONS, *_PAIR_RESULT_FIELDS)
_ROAD_RAIL_FIELDS = (*_ROAD_RAIL_DIMENSIONS, *_PAIR_RESULT_FIELDS)
_ADAPTIVE_FIELDS = (
    "resource_frame",
    "rail_status",
    "rail_multiplier",
    "graph_scope",
    "return_strategy",
    "policy_id",
    "run_count",
    "valid_completion_count",
    "mean_completion_rate",
    "full_completion_count",
    "finite_makespan_count",
    "mean_finite_makespan",
    "rank",
    "winner",
    "ranking_basis",
)


def analyze_output_root(
    output_root: str | Path,
    *,
    stage: str,
    design_path: str | Path = DEFAULT_DESIGN_PATH,
    bootstrap_replicates: int | None = None,
    morris_resamples: int = 1_000,
) -> dict[str, Any]:
    """Read one manifested campaign stage and write deterministic artifacts."""

    if stage not in {"smoke", "full"}:
        raise ValueError("stage must be smoke or full")
    design = load_revision_design(design_path)
    root = assert_isolated_output_path(output_root)
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"revision output root is not a directory: {root}")
    analysis_dir = assert_isolated_output_path(root / "analysis" / stage)
    analysis_dir.mkdir(parents=True, exist_ok=True)

    replicates = (
        design.bootstrap_replicates
        if bootstrap_replicates is None
        else _positive_int(bootstrap_replicates, "bootstrap_replicates")
    )
    resamples = _positive_int(morris_resamples, "morris_resamples")
    loaded = _load_campaign_csvs(
        root,
        stage=stage,
        design_id=design.design_id,
    )
    graph_route_evidence = _load_graph_scope_route_evidence(root)
    corridor_scope_evidence = _load_corridor_target_scope_evidence(root)
    _validate_corridor_evidence_alignment(loaded, corridor_scope_evidence)
    rows_by_campaign = loaded["rows_by_campaign"]
    available = tuple(
        campaign for campaign in EXPECTED_CAMPAIGNS if rows_by_campaign.get(campaign)
    )
    missing = tuple(
        campaign for campaign in EXPECTED_CAMPAIGNS if campaign not in available
    )

    analyses: dict[str, dict[str, Any]] = {}
    artifacts: list[dict[str, Any]] = []

    structural_rows = graph_route_evidence["rows"]
    structural_path = _write_rows(
        analysis_dir / "graph_scope_route_metrics.csv",
        _GRAPH_ROUTE_FIELDS,
        structural_rows,
    )
    structural_state = {
        "status": (
            "available" if structural_rows else "missing_evidence"
        ),
        "input_row_count": len(structural_rows),
        "output_row_count": len(structural_rows),
        "stage_independent": True,
    }
    analyses["graph_scope_route_metrics"] = structural_state
    artifacts.append(_file_record(structural_path, len(structural_rows)))

    corridor_scope_rows = corridor_scope_evidence["rows"]
    corridor_scope_path = _write_rows(
        analysis_dir / "corridor_target_scope_metrics.csv",
        _CORRIDOR_SCOPE_FIELDS,
        corridor_scope_rows,
    )
    corridor_scope_state = {
        "status": "available" if corridor_scope_rows else "missing_evidence",
        "input_row_count": len(corridor_scope_rows),
        "output_row_count": len(corridor_scope_rows),
        "stage_independent": True,
    }
    analyses["corridor_target_scope_metrics"] = corridor_scope_state
    artifacts.append(_file_record(corridor_scope_path, len(corridor_scope_rows)))

    paired_rows, paired_state = _guarded_analysis(
        "paired_summary",
        "paired_reanalysis",
        rows_by_campaign,
        lambda rows: _paired_summary(rows, design, replicates),
    )
    paired_path = _write_rows(
        analysis_dir / "paired_summary.csv", _PAIRED_FIELDS, paired_rows
    )
    analyses["paired_summary"] = paired_state
    artifacts.append(_file_record(paired_path, len(paired_rows)))

    convergence_rows, convergence_state = _guarded_analysis(
        "replicate_convergence",
        "paired_reanalysis",
        rows_by_campaign,
        lambda rows: _replicate_convergence(rows, design),
    )
    convergence_path = _write_rows(
        analysis_dir / "replicate_convergence.csv",
        _CONVERGENCE_FIELDS,
        convergence_rows,
    )
    analyses["replicate_convergence"] = convergence_state
    artifacts.append(_file_record(convergence_path, len(convergence_rows)))

    crossing_rows, crossing_state = _guarded_analysis(
        "break_even",
        "break_even",
        rows_by_campaign,
        lambda rows: _break_even(rows, design, replicates),
    )
    crossing_path = _write_rows(
        analysis_dir / "break_even.csv", _BREAK_EVEN_FIELDS, crossing_rows
    )
    analyses["break_even"] = crossing_state
    artifacts.append(_file_record(crossing_path, len(crossing_rows)))

    graph_rows, graph_state = _guarded_analysis(
        "graph_scope_stability",
        "graph_scope",
        rows_by_campaign,
        _graph_scope_stability,
    )
    graph_path = _write_rows(
        analysis_dir / "graph_scope_stability.csv", _GRAPH_FIELDS, graph_rows
    )
    analyses["graph_scope_stability"] = graph_state
    artifacts.append(_file_record(graph_path, len(graph_rows)))

    random_rows, random_state = _guarded_analysis(
        "random_threat_hierarchical",
        "random_threat_outer",
        rows_by_campaign,
        lambda rows: _random_threat(rows, design, replicates),
    )
    random_path = _write_rows(
        analysis_dir / "random_threat_hierarchical.csv",
        _RANDOM_FIELDS,
        random_rows,
    )
    analyses["random_threat_hierarchical"] = random_state
    artifacts.append(_file_record(random_path, len(random_rows)))

    crossed_rows, crossed_state = _guarded_analysis(
        "random_threat_crossed",
        "random_threat_outer",
        rows_by_campaign,
        lambda rows: _random_threat_crossed(rows, design, replicates),
    )
    crossed_path = _write_rows(
        analysis_dir / "random_threat_crossed.csv",
        _RANDOM_CROSSED_FIELDS,
        crossed_rows,
    )
    analyses["random_threat_crossed"] = crossed_state
    artifacts.append(_file_record(crossed_path, len(crossed_rows)))

    demand_rows, demand_state = _guarded_analysis(
        "demand_fleet",
        "demand_fleet",
        rows_by_campaign,
        lambda rows: _paired_summary_for_dimensions(
            rows, design, replicates, _DEMAND_FLEET_DIMENSIONS
        ),
    )
    demand_path = _write_rows(
        analysis_dir / "demand_fleet.csv", _DEMAND_FLEET_FIELDS, demand_rows
    )
    analyses["demand_fleet"] = demand_state
    artifacts.append(_file_record(demand_path, len(demand_rows)))

    map_rows, map_state = _guarded_analysis(
        "road_rail_map",
        "road_rail_map",
        rows_by_campaign,
        lambda rows: _paired_summary_for_dimensions(
            rows, design, replicates, _ROAD_RAIL_DIMENSIONS
        ),
    )
    map_path = _write_rows(
        analysis_dir / "road_rail_map.csv", _ROAD_RAIL_FIELDS, map_rows
    )
    analyses["road_rail_map"] = map_state
    artifacts.append(_file_record(map_path, len(map_rows)))

    adaptive_rows, adaptive_state = _guarded_analysis(
        "adaptive_policies",
        "adaptive_policies",
        rows_by_campaign,
        _adaptive_policy_summary,
    )
    adaptive_path = _write_rows(
        analysis_dir / "adaptive_policies.csv", _ADAPTIVE_FIELDS, adaptive_rows
    )
    analyses["adaptive_policies"] = adaptive_state
    artifacts.append(_file_record(adaptive_path, len(adaptive_rows)))

    morris_rows, morris_state = _guarded_analysis(
        "morris_effects",
        "morris",
        rows_by_campaign,
        lambda rows: _morris_effects(rows, design, resamples),
    )
    morris_path = _write_rows(
        analysis_dir / "morris_effects.csv", _MORRIS_FIELDS, morris_rows
    )
    analyses["morris_effects"] = morris_state
    artifacts.append(_file_record(morris_path, len(morris_rows)))

    analysis_completeness_blockers = list(loaded["analysis_completeness_blockers"])
    analysis_completeness_blockers.extend(
        f"analysis:{name}:{state['status']}"
        for name, state in analyses.items()
        if state["status"] != "available"
    )
    analysis_complete_full = stage == "full" and not analysis_completeness_blockers
    analysis_provenance = _analysis_implementation_provenance()
    analysis_runtime = _analysis_runtime_provenance()
    if (
        loaded["runtime_fingerprint"] is not None
        and loaded["runtime_fingerprint"] != analysis_runtime["fingerprint"]
    ):
        raise ValueError(
            "analysis runtime fingerprint differs from simulation campaigns"
        )
    manifest: dict[str, Any] = {
        "schema_version": 2,
        "final_study_ready": False,
        "design_id": design.design_id,
        "claim_boundary": design.claim_boundary,
        "stage": stage,
        "analysis_complete_full": analysis_complete_full,
        "analysis_completeness_blockers": analysis_completeness_blockers,
        "output_root": str(root),
        "analysis_directory": str(analysis_dir),
        "comparison_definition": (
            "bus_only minus static_multimodal; makespan inference uses only "
            "finite pairs with equal completion rates"
        ),
        "inference_definitions": {
            "paired_completion_rate": (
                "all seed-paired valid completion-rate differences; paired t and "
                "seeded percentile-bootstrap confidence intervals"
            ),
            "descriptive_winner": (
                "lexicographic point-estimate label; separate from confidence-"
                "interval statistical resolution"
            ),
            "random_threat_probability_proxies": (
                "empirical result frequencies from two-level threat-draw/arrival-"
                "seed bootstrap; not event probabilities"
            ),
            "random_threat_nested_sample_sizes": (
                "completion_threat_draw_count and completion_observation_count "
                "describe completion-delta bootstrap input; "
                "completion_empty_threat_draws lists draws without paired valid "
                "completion results; probability_proxy_observation_count counts "
                "paired valid result observations used by every probability proxy"
            ),
            "adaptive_ranking": "dense_rank_with_exact_ties_and_co_winners",
        },
        "bootstrap": {
            "replicates": replicates,
            "seed": design.bootstrap_seed,
            "confidence": design.confidence,
        },
        "morris": {
            "resamples": resamples,
            "seed": design.morris_seed,
            "confidence": design.confidence,
        },
        "available_campaigns": list(available),
        "missing_campaigns": list(missing),
        "source_files": [
            *loaded["source_files"],
            *graph_route_evidence["source_files"],
            *corridor_scope_evidence["source_files"],
        ],
        "campaign_manifests": loaded["campaign_manifests"],
        "input_fingerprint": loaded["input_fingerprint"],
        "input_artifacts": loaded["input_artifacts"],
        "central_target_checksum": loaded["central_target_checksum"],
        "implementation_fingerprint": loaded["implementation_fingerprint"],
        "runtime_fingerprint": loaded["runtime_fingerprint"],
        "runtime_environment": loaded["runtime_environment"],
        "analysis_implementation_fingerprint": analysis_provenance["fingerprint"],
        "analysis_implementation_artifacts": analysis_provenance["artifacts"],
        "analysis_runtime_fingerprint": analysis_runtime["fingerprint"],
        "analysis_runtime_environment": analysis_runtime,
        "graph_scope_route_evidence_manifest": graph_route_evidence[
            "manifest_record"
        ],
        "corridor_target_scope_evidence_manifest": corridor_scope_evidence[
            "manifest_record"
        ],
        "skipped_source_files": loaded["skipped_source_files"],
        "blank_numeric_value_count": loaded["blank_numeric_value_count"],
        "analyses": analyses,
        "generated_csv_files": artifacts,
        "written_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    manifest_path = assert_isolated_output_path(
        analysis_dir / "analysis_manifest.json"
    )
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def _guarded_analysis(
    analysis_name: str,
    campaign_id: str,
    rows_by_campaign: Mapping[str, Sequence[Mapping[str, object]]],
    function: Callable[[Sequence[Mapping[str, object]]], list[dict[str, Any]]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = rows_by_campaign.get(campaign_id, ())
    if not rows:
        return [], {
            "status": "missing_campaign",
            "campaign_id": campaign_id,
            "input_row_count": 0,
            "output_row_count": 0,
        }
    try:
        output = function(rows)
    except (KeyError, TypeError, ValueError) as error:
        return [], {
            "status": "error",
            "campaign_id": campaign_id,
            "input_row_count": len(rows),
            "output_row_count": 0,
            "error": f"{type(error).__name__}: {error}",
        }
    return output, {
        "status": "available" if output else "insufficient_data",
        "campaign_id": campaign_id,
        "input_row_count": len(rows),
        "output_row_count": len(output),
    }


def _paired_summary(
    rows: Sequence[Mapping[str, object]],
    design: RevisionExperimentDesign,
    replicates: int,
) -> list[dict[str, Any]]:
    return _paired_summary_for_dimensions(
        rows, design, replicates, _PAIR_DIMENSIONS
    )


def _paired_summary_for_dimensions(
    rows: Sequence[Mapping[str, object]],
    design: RevisionExperimentDesign,
    replicates: int,
    dimensions: Sequence[str],
) -> list[dict[str, Any]]:
    projected = _project_pair_rows(rows, dimensions)
    summaries = summarize_paired_makespan(
        projected,
        confidence=design.confidence,
        bootstrap_replicates=replicates,
        bootstrap_seed=design.bootstrap_seed,
    )
    output: list[dict[str, Any]] = []
    for summary in summaries:
        row = _dimension_row(dict(summary.configuration), dimensions)
        t_interval = summary.t_interval
        bootstrap = summary.bootstrap_interval
        completion_t = summary.completion_t_interval
        completion_bootstrap = summary.completion_bootstrap_interval
        row.update(
            {
                "total_pair_count": summary.total_pair_count,
                "completion_pair_count": summary.completion_pair_count,
                "mean_bus_completion_rate": summary.mean_left_completion_rate,
                "mean_multimodal_completion_rate": summary.mean_right_completion_rate,
                "mean_completion_rate_delta_bus_minus_multimodal": (
                    summary.mean_completion_rate_delta
                ),
                "completion_winner": _policy_winner(summary.completion_winner),
                "completion_winner_scope": "descriptive_mean_difference",
                "completion_statistical_resolution": _policy_resolution(
                    summary.completion_statistical_resolution
                ),
                "completion_inference_basis": (
                    "paired_t_and_percentile_bootstrap_confidence_intervals"
                ),
                "completion_t_ci_lower": (
                    None if completion_t is None else completion_t.lower
                ),
                "completion_t_ci_upper": (
                    None if completion_t is None else completion_t.upper
                ),
                "completion_t_confidence": (
                    None if completion_t is None else completion_t.confidence
                ),
                "completion_t_n": (
                    None if completion_t is None else completion_t.n
                ),
                "completion_t_standard_error": (
                    None if completion_t is None else completion_t.standard_error
                ),
                "completion_bootstrap_ci_lower": (
                    None
                    if completion_bootstrap is None
                    else completion_bootstrap.lower
                ),
                "completion_bootstrap_ci_upper": (
                    None
                    if completion_bootstrap is None
                    else completion_bootstrap.upper
                ),
                "completion_bootstrap_confidence": (
                    None
                    if completion_bootstrap is None
                    else completion_bootstrap.confidence
                ),
                "completion_bootstrap_n": (
                    None
                    if completion_bootstrap is None
                    else completion_bootstrap.n
                ),
                "completion_bootstrap_replicates": (
                    None
                    if completion_bootstrap is None
                    else completion_bootstrap.replicates
                ),
                "completion_bootstrap_seed": (
                    None
                    if completion_bootstrap is None
                    else completion_bootstrap.seed
                ),
                "completion_incomplete_reason_counts": dict(
                    summary.completion_incomplete_reason_counts
                ),
                "overall_winner": _policy_winner(summary.overall_winner),
                "overall_winner_basis": summary.overall_winner_basis,
                "finite_pair_count": summary.finite_pair_count,
                "excluded_pair_count": (
                    summary.total_pair_count - summary.finite_pair_count
                ),
                "mean_bus_makespan": summary.mean_left_makespan,
                "mean_multimodal_makespan": summary.mean_right_makespan,
                "mean_delta_bus_minus_multimodal": summary.mean_delta,
                "t_ci_lower": None if t_interval is None else t_interval.lower,
                "t_ci_upper": None if t_interval is None else t_interval.upper,
                "t_confidence": (
                    None if t_interval is None else t_interval.confidence
                ),
                "t_n": None if t_interval is None else t_interval.n,
                "t_standard_error": (
                    None if t_interval is None else t_interval.standard_error
                ),
                "bootstrap_ci_lower": (
                    None if bootstrap is None else bootstrap.lower
                ),
                "bootstrap_ci_upper": (
                    None if bootstrap is None else bootstrap.upper
                ),
                "bootstrap_confidence": (
                    None if bootstrap is None else bootstrap.confidence
                ),
                "bootstrap_n": None if bootstrap is None else bootstrap.n,
                "bootstrap_replicates": (
                    None if bootstrap is None else bootstrap.replicates
                ),
                "bootstrap_seed": None if bootstrap is None else bootstrap.seed,
                "incomplete_reason_counts": dict(
                    summary.incomplete_reason_counts
                ),
                "comparison_scope": "equal_completion_finite_makespan_only",
            }
        )
        output.append(row)
    return output


def _replicate_convergence(
    rows: Sequence[Mapping[str, object]],
    design: RevisionExperimentDesign,
) -> list[dict[str, Any]]:
    projected = _project_pair_rows(rows, _PAIR_DIMENSIONS)
    diagnostics = paired_replicate_convergence(
        projected,
        confidence=design.confidence,
    )
    output: list[dict[str, Any]] = []
    for item in diagnostics:
        output.append(
            {
                **_dimension_row(dict(item.configuration), _PAIR_DIMENSIONS),
                "replicate_count": item.count,
                "seed_max": item.seed_max,
                "mean_delta_bus_minus_multimodal": item.estimate,
                "t_ci_lower": item.lower,
                "t_ci_upper": item.upper,
                "t_ci_half_width": item.half_width,
                "estimate_change_from_previous": item.estimate_change_from_previous,
                "half_width_ratio_to_previous": item.half_width_ratio_to_previous,
            }
        )
    return output


def _break_even(
    rows: Sequence[Mapping[str, object]],
    design: RevisionExperimentDesign,
    replicates: int,
) -> list[dict[str, Any]]:
    dimensions = (
        "scenario_id",
        "resource_frame",
        "graph_scope",
        "rail_status",
        "return_strategy",
        "road_multiplier",
    )
    projected = _project_pair_rows(rows, dimensions)
    series = break_even_from_rows(
        projected,
        multiplier_field="road_multiplier",
        confidence=design.confidence,
        bootstrap_replicates=replicates,
        bootstrap_seed=design.bootstrap_seed,
    )
    output: list[dict[str, Any]] = []
    for item in series:
        values = dict(item.configuration)
        crossing = item.crossing
        joint = item.joint_seed_bootstrap
        output.append(
            {
                **_dimension_row(values, _BREAK_EVEN_FIELDS[:5]),
                "status": crossing.status,
                "crossing_road_multiplier": crossing.crossing,
                "lower_road_multiplier": crossing.lower_x,
                "upper_road_multiplier": crossing.upper_x,
                "lower_mean_delta": crossing.lower_y,
                "upper_mean_delta": crossing.upper_y,
                "bracket_count": crossing.bracket_count,
                "paired_mean_points": [list(point) for point in item.paired_mean_points],
                "joint_seed_bootstrap_ci_lower": (
                    None if joint is None else joint.lower
                ),
                "joint_seed_bootstrap_ci_upper": (
                    None if joint is None else joint.upper
                ),
                "joint_seed_bootstrap_confidence": (
                    None if joint is None else joint.confidence
                ),
                "joint_seed_bootstrap_complete_seed_count": (
                    None if joint is None else joint.complete_seed_count
                ),
                "joint_seed_bootstrap_excluded_seeds": (
                    [] if joint is None else list(joint.excluded_seeds)
                ),
                "joint_seed_bootstrap_replicates": (
                    None if joint is None else joint.replicates
                ),
                "joint_seed_bootstrap_successful_replicates": (
                    None if joint is None else joint.successful_replicates
                ),
                "joint_seed_bootstrap_seed": None if joint is None else joint.seed,
            }
        )
    return output


def _graph_scope_stability(
    rows: Sequence[Mapping[str, object]],
) -> list[dict[str, Any]]:
    dimensions = (
        "scenario_id",
        "resource_frame",
        "graph_scope",
        "corridor_path_count",
        "rail_status",
        "return_strategy",
    )
    projected = _project_pair_rows(rows, dimensions)
    usable = [row for row in projected if _valid_completion(row["completion_rate"])]
    table = graph_scope_stability_table(usable)
    return [
        {
            "graph_scope": item.graph_scope,
            "normal_time_match_count": item.normal_time_match_count,
            "normal_time_mean_absolute_error": (
                item.normal_time_mean_absolute_error
            ),
            "normal_time_mean_absolute_percentage_error": (
                item.normal_time_mean_absolute_percentage_error
            ),
            "connectivity_match_count": item.connectivity_match_count,
            "connectivity_agreement": item.connectivity_agreement,
            "policy_ranking_match_count": item.policy_ranking_match_count,
            "policy_ranking_agreement": item.policy_ranking_agreement,
        }
        for item in table
    ]


def _random_threat(
    rows: Sequence[Mapping[str, object]],
    design: RevisionExperimentDesign,
    replicates: int,
) -> list[dict[str, Any]]:
    dimensions = (
        "scenario_id",
        "resource_frame",
        "graph_scope",
        "rail_status",
        "return_strategy",
        "threat_draw",
    )
    projected = _project_pair_rows(rows, dimensions)
    summaries = hierarchical_paired_delta_summaries(
        projected,
        confidence=design.confidence,
        bootstrap_replicates=replicates,
        bootstrap_seed=design.bootstrap_seed,
    )
    output: list[dict[str, Any]] = []
    for summary in summaries:
        interval = summary.interval
        completion_interval = summary.completion_delta_interval
        bus_positive = summary.left_positive_completion_proxy_interval
        multimodal_positive = summary.right_positive_completion_proxy_interval
        bus_full = summary.left_full_completion_proxy_interval
        multimodal_full = summary.right_full_completion_proxy_interval
        probability_intervals = (
            bus_positive,
            multimodal_positive,
            bus_full,
            multimodal_full,
        )
        probability_counts = {
            item.finite_observation_count
            for item in probability_intervals
            if item is not None
        }
        if len(probability_counts) > 1:
            raise ValueError(
                "probability proxies must use one paired-valid observation set"
            )
        row = _dimension_row(dict(summary.configuration), _RANDOM_FIELDS[:5])
        row.update(
            {
                "total_pair_count": summary.total_pair_count,
                "finite_pair_count": summary.finite_pair_count,
                "excluded_pair_count": (
                    summary.total_pair_count - summary.finite_pair_count
                ),
                "mean_delta_bus_minus_multimodal": (
                    None if interval is None else interval.estimate
                ),
                "bootstrap_ci_lower": None if interval is None else interval.lower,
                "bootstrap_ci_upper": None if interval is None else interval.upper,
                "bootstrap_confidence": (
                    None if interval is None else interval.confidence
                ),
                "bootstrap_replicates": (
                    None if interval is None else interval.replicates
                ),
                "bootstrap_seed": None if interval is None else interval.seed,
                "threat_draw_count": (
                    None if interval is None else interval.threat_draw_count
                ),
                "finite_observation_count": (
                    None if interval is None else interval.finite_observation_count
                ),
                "empty_threat_draws": (
                    [] if interval is None else list(interval.empty_threat_draws)
                ),
                "bootstrap_excluded_observation_count": (
                    None if interval is None else len(interval.excluded)
                ),
                "incomplete_reason_counts": dict(
                    summary.incomplete_reason_counts
                ),
                "comparison_scope": "equal_completion_finite_makespan_only",
                "completion_pair_count": summary.completion_pair_count,
                "mean_completion_rate_delta_bus_minus_multimodal": (
                    None
                    if completion_interval is None
                    else completion_interval.estimate
                ),
                "completion_delta_bootstrap_ci_lower": (
                    None
                    if completion_interval is None
                    else completion_interval.lower
                ),
                "completion_delta_bootstrap_ci_upper": (
                    None
                    if completion_interval is None
                    else completion_interval.upper
                ),
                "completion_delta_bootstrap_confidence": (
                    None
                    if completion_interval is None
                    else completion_interval.confidence
                ),
                "completion_delta_bootstrap_replicates": (
                    None
                    if completion_interval is None
                    else completion_interval.replicates
                ),
                "completion_delta_bootstrap_seed": (
                    None
                    if completion_interval is None
                    else completion_interval.seed
                ),
                "completion_threat_draw_count": (
                    None
                    if completion_interval is None
                    else completion_interval.threat_draw_count
                ),
                "completion_observation_count": (
                    None
                    if completion_interval is None
                    else completion_interval.finite_observation_count
                ),
                "completion_empty_threat_draws": (
                    []
                    if completion_interval is None
                    else list(completion_interval.empty_threat_draws)
                ),
                "completion_incomplete_reason_counts": dict(
                    summary.completion_incomplete_reason_counts
                ),
                "bus_positive_completion_probability_proxy": (
                    None if bus_positive is None else bus_positive.estimate
                ),
                "bus_positive_completion_proxy_ci_lower": (
                    None if bus_positive is None else bus_positive.lower
                ),
                "bus_positive_completion_proxy_ci_upper": (
                    None if bus_positive is None else bus_positive.upper
                ),
                "multimodal_positive_completion_probability_proxy": (
                    None
                    if multimodal_positive is None
                    else multimodal_positive.estimate
                ),
                "multimodal_positive_completion_proxy_ci_lower": (
                    None
                    if multimodal_positive is None
                    else multimodal_positive.lower
                ),
                "multimodal_positive_completion_proxy_ci_upper": (
                    None
                    if multimodal_positive is None
                    else multimodal_positive.upper
                ),
                "bus_full_completion_probability_proxy": (
                    None if bus_full is None else bus_full.estimate
                ),
                "bus_full_completion_proxy_ci_lower": (
                    None if bus_full is None else bus_full.lower
                ),
                "bus_full_completion_proxy_ci_upper": (
                    None if bus_full is None else bus_full.upper
                ),
                "multimodal_full_completion_probability_proxy": (
                    None if multimodal_full is None else multimodal_full.estimate
                ),
                "multimodal_full_completion_proxy_ci_lower": (
                    None if multimodal_full is None else multimodal_full.lower
                ),
                "multimodal_full_completion_proxy_ci_upper": (
                    None if multimodal_full is None else multimodal_full.upper
                ),
                "probability_proxy_confidence": next(
                    (
                        item.confidence
                        for item in (
                            bus_positive,
                            multimodal_positive,
                            bus_full,
                            multimodal_full,
                        )
                        if item is not None
                    ),
                    None,
                ),
                "probability_proxy_observation_count": (
                    next(iter(probability_counts)) if probability_counts else None
                ),
                "probability_proxy_scope": summary.probability_proxy_scope,
            }
        )
        output.append(row)
    return output


def _random_threat_crossed(
    rows: Sequence[Mapping[str, object]],
    design: RevisionExperimentDesign,
    replicates: int,
) -> list[dict[str, Any]]:
    """Crossed two-way alternative to ``_random_threat``.

    Uses the same pairing but resamples threat draws and the arrival-seed
    index set jointly (one global seed resample per replicate), preserving
    the cross-threat seed dependence of the crossed experimental design.
    """
    dimensions = (
        "scenario_id",
        "resource_frame",
        "graph_scope",
        "rail_status",
        "return_strategy",
        "threat_draw",
    )
    projected = _project_pair_rows(rows, dimensions)
    summaries = hierarchical_paired_delta_summaries(
        projected,
        confidence=design.confidence,
        bootstrap_replicates=replicates,
        bootstrap_seed=design.bootstrap_seed,
        interval_factory=crossed_two_way_bootstrap_ci,
    )
    output: list[dict[str, Any]] = []
    for summary in summaries:
        interval = summary.interval
        completion_interval = summary.completion_delta_interval
        row = _dimension_row(dict(summary.configuration), _RANDOM_CROSSED_FIELDS[:5])
        row.update(
            {
                "total_pair_count": summary.total_pair_count,
                "finite_pair_count": summary.finite_pair_count,
                "excluded_pair_count": (
                    summary.total_pair_count - summary.finite_pair_count
                ),
                "mean_delta_bus_minus_multimodal": (
                    None if interval is None else interval.estimate
                ),
                "crossed_ci_lower": None if interval is None else interval.lower,
                "crossed_ci_upper": None if interval is None else interval.upper,
                "crossed_confidence": (
                    None if interval is None else interval.confidence
                ),
                "crossed_replicates": (
                    None if interval is None else interval.replicates
                ),
                "crossed_seed": None if interval is None else interval.seed,
                "crossed_failed_replicates": (
                    None
                    if interval is None
                    else getattr(interval, "failed_replicates", 0)
                ),
                "threat_draw_count": (
                    None if interval is None else interval.threat_draw_count
                ),
                "finite_observation_count": (
                    None if interval is None else interval.finite_observation_count
                ),
                "comparison_scope": "equal_completion_finite_makespan_only",
                "completion_pair_count": summary.completion_pair_count,
                "mean_completion_rate_delta_bus_minus_multimodal": (
                    None
                    if completion_interval is None
                    else completion_interval.estimate
                ),
                "completion_crossed_ci_lower": (
                    None
                    if completion_interval is None
                    else completion_interval.lower
                ),
                "completion_crossed_ci_upper": (
                    None
                    if completion_interval is None
                    else completion_interval.upper
                ),
                "completion_crossed_confidence": (
                    None
                    if completion_interval is None
                    else completion_interval.confidence
                ),
                "completion_crossed_replicates": (
                    None
                    if completion_interval is None
                    else completion_interval.replicates
                ),
                "completion_crossed_seed": (
                    None
                    if completion_interval is None
                    else completion_interval.seed
                ),
                "completion_crossed_failed_replicates": (
                    None
                    if completion_interval is None
                    else getattr(completion_interval, "failed_replicates", 0)
                ),
                "resampling_scope": (
                    "crossed_two_way_threat_draw_and_global_arrival_seed_resample"
                ),
            }
        )
        output.append(row)
    return output


def _adaptive_policy_summary(
    rows: Sequence[Mapping[str, object]],
) -> list[dict[str, Any]]:
    dimensions = (
        "resource_frame",
        "rail_status",
        "rail_multiplier",
        "graph_scope",
        "return_strategy",
    )
    active = tuple(field for field in dimensions if any(field in row for row in rows))
    grouped: dict[tuple[object, ...], dict[str, list[Mapping[str, object]]]] = {}
    seen: set[tuple[tuple[object, ...], str, object]] = set()
    for row_number, row in enumerate(rows, start=1):
        policy = str(row.get("policy_id", "")).strip()
        if not policy:
            raise ValueError(f"adaptive row {row_number} is missing policy_id")
        seed = row.get("arrival_seed")
        key = tuple(row.get(field) for field in active)
        identity = (key, policy, seed)
        if identity in seen:
            raise ValueError("duplicate adaptive policy seed row")
        seen.add(identity)
        grouped.setdefault(key, {}).setdefault(policy, []).append(row)

    output: list[dict[str, Any]] = []
    for key in sorted(grouped, key=repr):
        summaries: list[dict[str, Any]] = []
        for policy in sorted(grouped[key]):
            policy_rows = grouped[key][policy]
            completions = [
                value
                for value in (_finite_float(row.get("completion_rate")) for row in policy_rows)
                if value is not None and 0.0 <= value <= 1.0
            ]
            finite_times = [
                value
                for row in policy_rows
                for value in [_finite_float(row.get("makespan"))]
                if value is not None
            ]
            summaries.append(
                {
                    **dict(zip(active, key, strict=True)),
                    "policy_id": policy,
                    "run_count": len(policy_rows),
                    "valid_completion_count": len(completions),
                    "mean_completion_rate": (
                        sum(completions) / len(completions) if completions else None
                    ),
                    "full_completion_count": sum(
                        math.isclose(value, 1.0, abs_tol=1e-12)
                        for value in completions
                    ),
                    "finite_makespan_count": len(finite_times),
                    "mean_finite_makespan": (
                        sum(finite_times) / len(finite_times) if finite_times else None
                    ),
                }
            )
        ranked = sorted(
            summaries,
            key=lambda item: (
                _adaptive_rank_key(item),
                str(item.get("policy_id", "")),
            ),
        )
        previous_score: tuple[float, float] | None = None
        dense_rank = 0
        for item in ranked:
            score = _adaptive_rank_key(item)
            if previous_score is None or score != previous_score:
                dense_rank += 1
                previous_score = score
            item["rank"] = dense_rank
            item["winner"] = dense_rank == 1
            item["ranking_basis"] = "completion_rate_then_finite_makespan"
            output.append(item)
    return output


def _adaptive_rank_key(row: Mapping[str, object]) -> tuple[float, float]:
    completion = _finite_float(row.get("mean_completion_rate"))
    makespan = _finite_float(row.get("mean_finite_makespan"))
    return (
        -(completion if completion is not None else -math.inf),
        makespan if makespan is not None else math.inf,
    )


def _policy_winner(value: str) -> str:
    return {
        "left": LEFT_POLICY,
        "right": RIGHT_POLICY,
        "tie": "tie",
        "unavailable": "unavailable",
    }.get(value, value)


def _policy_resolution(value: str) -> str:
    return {
        "left_advantage": "bus_only_advantage",
        "right_advantage": "static_multimodal_advantage",
    }.get(value, value)


def _morris_effects(
    rows: Sequence[Mapping[str, object]],
    design: RevisionExperimentDesign,
    resamples: int,
) -> list[dict[str, Any]]:
    campaign = design.campaign("morris")
    problem = {
        "num_vars": len(EXPECTED_MORRIS_FACTORS),
        "names": list(EXPECTED_MORRIS_FACTORS),
        "bounds": [list(campaign["factors"][name]) for name in EXPECTED_MORRIS_FACTORS],
    }
    morris_design = _match_morris_design(rows, design, problem)
    prepared: list[dict[str, object]] = []
    design_rows = morris_design.rows()
    for row_number, row in enumerate(rows, start=1):
        point = _required_index(row.get("morris_point"), "morris_point", row_number)
        if point >= len(design_rows):
            raise ValueError(f"Morris row {row_number} point is outside design")
        factors = _factor_values(row, row_number)
        prepared.append(
            {
                "policy_id": str(row.get("policy_id", "")),
                "sample_id": morris_design.sample_ids[point],
                "arrival_seed": row.get("arrival_seed"),
                "makespan_response": _morris_outcome(row),
                "completion_response": _morris_completion_outcome(row),
                **factors,
            }
        )

    policies = tuple(
        policy
        for policy in campaign["policies"]
        if any(str(row.get("policy_id")) == policy for row in prepared)
    )
    if not policies:
        return []
    smoke_trajectories = min(2, int(campaign["trajectories"]))
    seed_count = (
        min(2, int(campaign["arrival_seed_count"]))
        if morris_design.trajectories == smoke_trajectories
        else int(campaign["arrival_seed_count"])
    )
    expected_seeds = design.arrival_seeds[:seed_count]
    output: list[dict[str, Any]] = []
    responses = (
        (
            "makespan",
            "makespan_response",
            "all_expected_seeds_full_completion_and_finite_makespan",
        ),
        (
            "completion_rate",
            "completion_response",
            "all_expected_seeds_valid_completion_rate",
        ),
    )
    for response_metric, outcome_key, outcome_scope in responses:
        outcomes = aggregate_morris_outcomes(
            morris_design,
            prepared,
            policy_ids=policies,
            expected_arrival_seeds=expected_seeds,
            outcome_key=outcome_key,
        )
        for policy in policies:
            policy_outcomes = outcomes[policy]
            incomplete = policy_outcomes.incomplete_groups
            missing_count = sum(len(item.missing_seeds) for item in incomplete)
            nonfinite_count = sum(len(item.nonfinite_seeds) for item in incomplete)
            if incomplete or not all(
                math.isfinite(float(value)) for value in policy_outcomes.outcomes
            ):
                output.append(
                    {
                        "policy_id": policy,
                        "response_metric": response_metric,
                        "analysis_status": "incomplete_replications",
                        "factor_name": None,
                        "mu": None,
                        "mu_star": None,
                        "sigma": None,
                        "mu_star_conf": None,
                        "trajectory_count": morris_design.trajectories,
                        "sample_point_count": len(morris_design.sample_ids),
                        "expected_arrival_seed_count": len(expected_seeds),
                        "incomplete_group_count": len(incomplete),
                        "missing_seed_count": missing_count,
                        "nonfinite_seed_count": nonfinite_count,
                        "outcome_scope": outcome_scope,
                    }
                )
                continue
            result = analyze_morris(
                morris_design,
                policy_outcomes,
                num_resamples=resamples,
                conf_level=design.confidence,
                seed=design.morris_seed,
            )
            for effect in result.effects:
                output.append(
                {
                    "policy_id": policy,
                    "response_metric": response_metric,
                    "analysis_status": "available",
                    "factor_name": effect.factor_name,
                    "mu": effect.mu,
                    "mu_star": effect.mu_star,
                    "sigma": effect.sigma,
                    "mu_star_conf": effect.mu_star_conf,
                    "trajectory_count": morris_design.trajectories,
                    "sample_point_count": len(morris_design.sample_ids),
                    "expected_arrival_seed_count": len(expected_seeds),
                    "incomplete_group_count": 0,
                    "missing_seed_count": 0,
                    "nonfinite_seed_count": 0,
                    "outcome_scope": outcome_scope,
                }
            )
    return output


def _match_morris_design(
    rows: Sequence[Mapping[str, object]],
    design: RevisionExperimentDesign,
    problem: Mapping[str, Any],
) -> MorrisDesign:
    campaign = design.campaign("morris")
    smoke = min(2, int(campaign["trajectories"]))
    candidates = tuple(dict.fromkeys((smoke, int(campaign["trajectories"]))))
    matches: list[MorrisDesign] = []
    for trajectories in candidates:
        candidate = sample_morris(
            problem,
            N=trajectories,
            num_levels=int(campaign["levels"]),
            seed=design.morris_seed,
        )
        expected = candidate.rows()
        matches_candidate = True
        for row_number, row in enumerate(rows, start=1):
            point = _required_index(
                row.get("morris_point"), "morris_point", row_number
            )
            if point >= len(expected):
                matches_candidate = False
                break
            factors = _factor_values(row, row_number)
            if any(
                not math.isclose(
                    factors[name],
                    float(expected[point][name]),
                    rel_tol=1e-10,
                    abs_tol=1e-12,
                )
                for name in EXPECTED_MORRIS_FACTORS
            ):
                matches_candidate = False
                break
        if matches_candidate:
            matches.append(candidate)
    if not matches:
        raise ValueError(
            "Morris factor rows do not align with smoke or full committed design"
        )
    return min(matches, key=lambda candidate: candidate.trajectories)


def _factor_values(
    row: Mapping[str, object], row_number: int
) -> dict[str, float]:
    nested = row.get("factor_values")
    if nested is not None and not isinstance(nested, Mapping):
        raise ValueError(f"Morris row {row_number} factor_values must be a mapping")
    values: dict[str, float] = {}
    for name in EXPECTED_MORRIS_FACTORS:
        raw = nested.get(name) if isinstance(nested, Mapping) else row.get(name)
        try:
            value = float(raw)
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"Morris row {row_number} has invalid factor {name!r}"
            ) from error
        if not math.isfinite(value):
            raise ValueError(
                f"Morris row {row_number} has nonfinite factor {name!r}"
            )
        values[name] = value
    return values


def _morris_outcome(row: Mapping[str, object]) -> float:
    completion = _finite_float(row.get("completion_rate"))
    makespan = _finite_float(row.get("makespan"))
    if completion is None or not math.isclose(completion, 1.0, abs_tol=1e-12):
        return math.inf
    return math.inf if makespan is None else makespan


def _morris_completion_outcome(row: Mapping[str, object]) -> float:
    completion = _finite_float(row.get("completion_rate"))
    if completion is None or completion < 0.0 or completion > 1.0:
        return math.inf
    return completion


def _project_pair_rows(
    rows: Sequence[Mapping[str, object]],
    dimensions: Sequence[str],
) -> list[dict[str, object]]:
    active_dimensions = tuple(
        field for field in dimensions if any(field in row for row in rows)
    )
    projected: list[dict[str, object]] = []
    for row in rows:
        projected.append(
            {
                **{field: row.get(field) for field in active_dimensions},
                "policy_id": row.get("policy_id"),
                "arrival_seed": row.get("arrival_seed"),
                "completion_rate": row.get("completion_rate"),
                "makespan": row.get("makespan"),
            }
        )
    return projected


def _dimension_row(
    values: Mapping[str, object], fields: Sequence[str]
) -> dict[str, object]:
    return {field: values.get(field) for field in fields}


def _load_corridor_target_scope_evidence(root: Path) -> dict[str, Any]:
    metrics_path = root / "corridor_target_scope_metrics.csv"
    manifest_path = root / "corridor_target_scope_metrics_manifest.json"
    if not metrics_path.exists() and not manifest_path.exists():
        return {"rows": [], "source_files": [], "manifest_record": None}
    if metrics_path.exists() != manifest_path.exists():
        missing = "manifest" if metrics_path.exists() else "metrics CSV"
        raise ValueError(f"corridor-target scope evidence is missing matching {missing}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("cannot read corridor-target scope manifest") from error
    if not isinstance(manifest, Mapping):
        raise ValueError("corridor-target scope manifest must contain an object")
    required = {
        "schema_version": 1,
        "final_study_ready": False,
        "contains_coordinates": False,
        "public_canonical_node_ids_only": True,
        "fixed_target_across_scopes": True,
        "dynamic_rerouting_reflected_by_shortest_path": True,
    }
    for field, expected in required.items():
        if manifest.get(field) != expected:
            raise ValueError(
                f"corridor-target scope manifest has invalid {field}"
            )
    artifact = manifest.get("output_artifact")
    if not isinstance(artifact, Mapping):
        raise ValueError("corridor-target scope manifest lacks output artifact")
    recorded_path = artifact.get("path")
    if (
        not isinstance(recorded_path, str)
        or Path(recorded_path).expanduser().resolve() != metrics_path.resolve()
    ):
        raise ValueError("corridor-target scope artifact path mismatch")
    if artifact.get("size_bytes") != metrics_path.stat().st_size:
        raise ValueError("corridor-target scope artifact size mismatch")
    if not _is_sha256(artifact.get("sha256")) or str(
        artifact["sha256"]
    ).lower() != _sha256(metrics_path):
        raise ValueError("corridor-target scope artifact SHA-256 mismatch")

    with metrics_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or set(reader.fieldnames) != set(
            _CORRIDOR_SCOPE_FIELDS
        ):
            raise ValueError(
                "corridor-target scope columns must match coordinate-free schema"
            )
        raw_rows = list(reader)
    if manifest.get("row_count") != len(raw_rows) or not raw_rows:
        raise ValueError("corridor-target scope manifest row_count mismatch")
    rows: list[dict[str, object]] = []
    for row_number, raw in enumerate(raw_rows, start=2):
        parsed: dict[str, object] = {}
        for field in _CORRIDOR_SCOPE_FIELDS:
            value, _ = _parse_csv_value(field, raw.get(field))
            parsed[field] = value
        parsed["connected"] = _required_bool_text(
            parsed["connected"], "connected", row_number
        )
        if parsed["graph_scope"] not in {"top10", "full"}:
            raise ValueError(
                f"corridor-target scope row {row_number} has invalid graph_scope"
            )
        if not _is_sha256(parsed["selected_target_checksum"]):
            raise ValueError(
                f"corridor-target scope row {row_number} has invalid checksum"
            )
        if parsed["selected_target_edge_count"] != parsed[
            "selected_target_edges_present"
        ]:
            raise ValueError(
                f"corridor-target scope row {row_number} has incomplete target"
            )
        rows.append(parsed)
    checksums = {row["selected_target_checksum"] for row in rows}
    if len(checksums) != 1 or next(iter(checksums)) != manifest.get(
        "selected_target_checksum"
    ):
        raise ValueError("corridor-target scope checksum is not fixed")
    scopes = {str(row["graph_scope"]) for row in rows}
    multipliers = {float(row["road_multiplier"]) for row in rows}
    if scopes != {"top10", "full"} or len(rows) != len(scopes) * len(multipliers):
        raise ValueError("corridor-target scope matrix is incomplete")
    return {
        "rows": rows,
        "source_files": [
            {
                "path": metrics_path.relative_to(root).as_posix(),
                "sha256": _sha256(metrics_path),
                "data_row_count": len(rows),
                "accepted_row_count": len(rows),
                "evidence_type": "fixed_corridor_target_graph_scope_response",
            }
        ],
        "manifest_record": {
            "path": manifest_path.relative_to(root).as_posix(),
            "sha256": _sha256(manifest_path),
            "final_study_ready": False,
            "stage_independent": True,
            "row_count": len(rows),
            "selected_target_checksum": manifest["selected_target_checksum"],
            "input_artifacts": manifest.get("input_artifacts", {}),
        },
    }


def _load_graph_scope_route_evidence(root: Path) -> dict[str, Any]:
    metrics_path = root / "graph_scope_route_metrics.csv"
    manifest_path = root / "graph_scope_route_metrics_manifest.json"
    if not metrics_path.exists() and not manifest_path.exists():
        return {"rows": [], "source_files": [], "manifest_record": None}
    if metrics_path.exists() != manifest_path.exists():
        missing = "manifest" if metrics_path.exists() else "metrics CSV"
        raise ValueError(f"graph-scope route evidence is missing matching {missing}")

    manifest = _read_graph_scope_route_manifest(manifest_path, metrics_path)
    with metrics_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or set(reader.fieldnames) != set(_GRAPH_ROUTE_FIELDS):
            raise ValueError(
                "graph-scope route metrics columns must match coordinate-free schema"
            )
        raw_rows = list(reader)
    if manifest["row_count"] != len(raw_rows):
        raise ValueError(
            "graph-scope route manifest row_count does not match metrics CSV"
        )
    rows = [
        _parse_graph_scope_route_row(raw, row_number)
        for row_number, raw in enumerate(raw_rows, start=2)
    ]
    _validate_graph_scope_route_matrix(rows)
    return {
        "rows": rows,
        "source_files": [
            {
                "path": metrics_path.relative_to(root).as_posix(),
                "sha256": _sha256(metrics_path),
                "data_row_count": len(rows),
                "accepted_row_count": len(rows),
                "evidence_type": "coordinate_free_graph_scope_route_metrics",
            }
        ],
        "manifest_record": {
            "path": manifest_path.relative_to(root).as_posix(),
            "sha256": _sha256(manifest_path),
            "final_study_ready": False,
            "stage_independent": True,
            "row_count": manifest["row_count"],
            "input_artifacts": manifest["input_artifacts"],
        },
    }


def _read_graph_scope_route_manifest(
    manifest_path: Path, metrics_path: Path
) -> dict[str, Any]:
    try:
        value = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(
            f"cannot read graph-scope route manifest {manifest_path}: {error}"
        ) from error
    if not isinstance(value, dict):
        raise ValueError("graph-scope route manifest must contain an object")
    required_flags = {
        "final_study_ready": False,
        "contains_coordinates": False,
        "public_canonical_node_ids_only": True,
        "stage_independent": True,
        "road_mode_only": True,
    }
    for field, expected in required_flags.items():
        if value.get(field) is not expected:
            raise ValueError(
                f"graph-scope route manifest {field} must be {str(expected).lower()}"
            )
    if value.get("schema_version") != 2:
        raise ValueError("graph-scope route manifest schema_version must be 2")
    if value.get("path_diversity_method_field") != "path_diversity_method":
        raise ValueError("graph-scope route manifest lacks path-diversity method field")
    if value.get("path_diversity_count_source") != (
        "reduced-scope corridor_leg_candidates_json metadata"
    ):
        raise ValueError("graph-scope route manifest has invalid path-diversity source")
    cost_guard = value.get("path_diversity_cost_guard")
    if not isinstance(cost_guard, Mapping) or (
        cost_guard.get("sentinel_count") != 0
        or cost_guard.get("status") != "not_enumerated_cost_guard"
        or cost_guard.get("scopes") != ["full"]
        or cost_guard.get("legs") != ["S_to_R"]
    ):
        raise ValueError("graph-scope route manifest has invalid path-diversity cost guard")
    row_count = value.get("row_count")
    if isinstance(row_count, bool) or not isinstance(row_count, int) or row_count < 0:
        raise ValueError("graph-scope route manifest has invalid row_count")
    expected_scopes = {"top3", "top5", "top10", "full"}
    if set(value.get("graph_scopes", ())) != expected_scopes:
        raise ValueError("graph-scope route manifest must cover top3/top5/top10/full")
    expected_legs = [item[0] for item in CANONICAL_PUBLIC_ROAD_LEGS]
    if value.get("leg_ids") != expected_legs:
        raise ValueError("graph-scope route manifest has invalid canonical leg IDs")
    input_artifacts = value.get("input_artifacts")
    if not isinstance(input_artifacts, Mapping) or not input_artifacts:
        raise ValueError("graph-scope route manifest lacks input_artifacts")
    for name, artifact in input_artifacts.items():
        if not isinstance(name, str) or not name or not isinstance(artifact, Mapping):
            raise ValueError("graph-scope route input artifact record is invalid")
        recorded_path = artifact.get("path")
        recorded_size = artifact.get("size_bytes")
        if not isinstance(recorded_path, str) or not recorded_path.strip():
            raise ValueError("graph-scope route input artifact path is invalid")
        if (
            isinstance(recorded_size, bool)
            or not isinstance(recorded_size, int)
            or recorded_size < 0
        ):
            raise ValueError("graph-scope route input artifact size is invalid")
        if not _is_sha256(artifact.get("sha256")):
            raise ValueError("graph-scope route input artifact SHA-256 is invalid")
    _verify_graph_scope_route_artifact(value, metrics_path, manifest_path)
    return value


def _verify_graph_scope_route_artifact(
    manifest: Mapping[str, Any], metrics_path: Path, manifest_path: Path
) -> None:
    artifact = manifest.get("output_artifact")
    if not isinstance(artifact, Mapping):
        raise ValueError("graph-scope route manifest lacks output_artifact")
    recorded_path = artifact.get("path")
    if (
        not isinstance(recorded_path, str)
        or Path(recorded_path).expanduser().resolve() != metrics_path.resolve()
    ):
        raise ValueError(
            f"graph-scope route artifact path mismatch: {manifest_path}"
        )
    recorded_size = artifact.get("size_bytes")
    if (
        isinstance(recorded_size, bool)
        or not isinstance(recorded_size, int)
        or recorded_size != metrics_path.stat().st_size
    ):
        raise ValueError(
            f"graph-scope route artifact size mismatch: {manifest_path}"
        )
    recorded_sha = artifact.get("sha256")
    if not _is_sha256(recorded_sha) or str(recorded_sha).lower() != _sha256(metrics_path):
        raise ValueError(
            f"graph-scope route artifact SHA-256 mismatch: {manifest_path}"
        )


def _parse_graph_scope_route_row(
    raw: Mapping[str, str | None], row_number: int
) -> dict[str, object]:
    parsed: dict[str, object] = {}
    for field in _GRAPH_ROUTE_FIELDS:
        value, _ = _parse_csv_value(field, raw.get(field))
        parsed[field] = value
    for field in ("connected", "full_reference_connected"):
        parsed[field] = _required_bool_text(parsed[field], field, row_number)

    scope = str(parsed["graph_scope"])
    expected_counts = {"top3": 3, "top5": 5, "top10": 10, "full": None}
    if scope not in expected_counts:
        raise ValueError(f"graph-scope route row {row_number} has invalid scope")
    if parsed["corridor_path_count"] != expected_counts[scope]:
        raise ValueError(
            f"graph-scope route row {row_number} has invalid corridor_path_count"
        )
    expected_leg_nodes = {
        leg_id: (source, target)
        for leg_id, source, target in CANONICAL_PUBLIC_ROAD_LEGS
    }
    leg_id = str(parsed["leg_id"])
    if expected_leg_nodes.get(leg_id) != (
        str(parsed["source_id"]),
        str(parsed["target_id"]),
    ):
        raise ValueError(
            f"graph-scope route row {row_number} has invalid public canonical leg"
        )
    for field in (
        "graph_node_count",
        "graph_edge_count",
        "path_edge_count",
        "path_diversity_limit",
        "path_diversity_count",
        "full_path_edge_count",
    ):
        value = parsed[field]
        positive_fields = {
            "graph_node_count",
            "graph_edge_count",
            "path_diversity_limit",
        }
        minimum = 1 if field in positive_fields else 0
        if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
            raise ValueError(
                f"graph-scope route row {row_number} has invalid {field}"
            )
    for field in (
        "shortest_travel_time_min",
        "shortest_distance_m",
        "full_path_edge_overlap_ratio",
        "full_path_edge_jaccard",
        "travel_time_detour_ratio_vs_full",
        "distance_detour_ratio_vs_full",
    ):
        value = parsed[field]
        if value is not None and (
            isinstance(value, bool)
            or not isinstance(value, float)
            or not math.isfinite(value)
            or value < 0.0
        ):
            raise ValueError(
                f"graph-scope route row {row_number} has invalid {field}"
            )
    signature = parsed["path_signature_sha256"]
    if signature and not _is_sha256(signature):
        raise ValueError(
            f"graph-scope route row {row_number} has invalid path signature"
        )
    connected = bool(parsed["connected"])
    if connected:
        if (
            parsed["shortest_travel_time_min"] is None
            or parsed["path_edge_count"] < 1
            or not signature
        ):
            raise ValueError(
                f"graph-scope route row {row_number} has incomplete connected path"
            )
    elif any(
        (
            parsed["shortest_travel_time_min"] is not None,
            parsed["shortest_distance_m"] is not None,
            parsed["path_edge_count"] != 0,
            bool(signature),
        )
    ):
        raise ValueError(
            f"graph-scope route row {row_number} exposes path data while unreachable"
        )
    if parsed["path_diversity_count"] > parsed["path_diversity_limit"]:
        raise ValueError(
            f"graph-scope route row {row_number} exceeds path diversity limit"
        )
    if parsed["distance_status"] not in {
        "available",
        "missing_or_invalid_length_m",
        "unreachable",
    }:
        raise ValueError(
            f"graph-scope route row {row_number} has invalid distance_status"
        )
    if parsed["path_diversity_status"] not in {
        "capped_at_limit",
        "exhausted_before_limit",
        "candidate_metadata_missing",
        "not_enumerated_cost_guard",
    }:
        raise ValueError(
            f"graph-scope route row {row_number} has invalid path_diversity_status"
        )
    diversity_status = str(parsed["path_diversity_status"])
    diversity_method = str(parsed["path_diversity_method"])
    sentinel_statuses = {
        "candidate_metadata_missing",
        "not_enumerated_cost_guard",
    }
    if diversity_status in sentinel_statuses:
        if (
            parsed["path_diversity_count"] != 0
            or diversity_method != diversity_status
        ):
            raise ValueError(
                f"graph-scope route row {row_number} has ambiguous path diversity sentinel"
            )
    elif not diversity_method or diversity_method in sentinel_statuses:
        raise ValueError(
            f"graph-scope route row {row_number} lacks candidate metadata method"
        )
    cost_guard_required = scope == "full" or leg_id == "S_to_R"
    if cost_guard_required != (diversity_status == "not_enumerated_cost_guard"):
        raise ValueError(
            f"graph-scope route row {row_number} violates path-diversity cost guard"
        )
    if parsed["comparison_status"] not in {
        "available",
        "scope_unreachable",
        "full_reference_unreachable",
    }:
        raise ValueError(
            f"graph-scope route row {row_number} has invalid comparison_status"
        )
    return parsed


def _validate_graph_scope_route_matrix(rows: Sequence[Mapping[str, object]]) -> None:
    expected = {
        (scope, leg_id)
        for scope in ("top3", "top5", "top10", "full")
        for leg_id, _, _ in CANONICAL_PUBLIC_ROAD_LEGS
    }
    observed = [(str(row["graph_scope"]), str(row["leg_id"])) for row in rows]
    if len(observed) != len(set(observed)):
        raise ValueError("graph-scope route metrics contain duplicate scope-leg rows")
    if set(observed) != expected:
        raise ValueError(
            "graph-scope route metrics must contain every top3/top5/top10/full canonical leg"
        )
    by_key = {
        (str(row["graph_scope"]), str(row["leg_id"])): row for row in rows
    }
    for scope in ("top3", "top5", "top10", "full"):
        scope_rows = [row for row in rows if row["graph_scope"] == scope]
        graph_sizes = {
            (row["graph_node_count"], row["graph_edge_count"]) for row in scope_rows
        }
        if len(graph_sizes) != 1:
            raise ValueError(f"graph-scope route metrics disagree on {scope} graph size")
    for leg_id, _, _ in CANONICAL_PUBLIC_ROAD_LEGS:
        reference = by_key[("full", leg_id)]
        for scope in ("top3", "top5", "top10", "full"):
            row = by_key[(scope, leg_id)]
            if row["full_reference_connected"] is not reference["connected"]:
                raise ValueError(
                    f"graph-scope route metrics disagree on full connectivity for {leg_id}"
                )
            if row["full_path_edge_count"] != reference["path_edge_count"]:
                raise ValueError(
                    f"graph-scope route metrics disagree on full path size for {leg_id}"
                )


def _required_bool_text(value: object, field: str, row_number: int) -> bool:
    normalized = str(value).strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValueError(
        f"graph-scope route row {row_number} has invalid boolean {field}"
    )


def _load_campaign_csvs(
    root: Path,
    *,
    stage: str,
    design_id: str,
) -> dict[str, Any]:
    rows_by_campaign: dict[str, list[dict[str, object]]] = {
        campaign: [] for campaign in EXPECTED_CAMPAIGNS
    }
    source_files: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    campaign_manifests: list[dict[str, Any]] = []
    analysis_completeness_blockers: list[str] = []
    blank_numeric_count = 0
    global_run_keys: set[str] = set()
    input_fingerprints: set[str] = set()
    input_artifact_identities: set[str] = set()
    input_artifact_sets: list[Mapping[str, Any]] = []
    central_target_checksums: set[str] = set()
    implementation_fingerprints: set[str] = set()
    runtime_fingerprints: set[str] = set()
    runtime_environments: list[Mapping[str, Any]] = []
    for campaign_id in EXPECTED_CAMPAIGNS:
        campaign_dir = root / campaign_id
        path = campaign_dir / f"{stage}_results.csv"
        manifest_path = campaign_dir / f"{stage}_manifest.json"
        if not path.exists() and not manifest_path.exists():
            continue
        if path.exists() != manifest_path.exists():
            missing_name = "manifest" if path.exists() else "results CSV"
            raise ValueError(
                f"campaign {campaign_id!r} is missing matching {stage} {missing_name}"
            )
        manifest = _read_campaign_manifest(
            manifest_path,
            campaign_id=campaign_id,
            stage=stage,
            design_id=design_id,
            results_path=path,
        )
        implementation_fingerprints.add(manifest["implementation_fingerprint"])
        input_fingerprints.add(manifest["input_fingerprint"])
        input_artifact_identities.add(
            _input_artifact_identity(manifest["input_artifacts"])
        )
        input_artifact_sets.append(manifest["input_artifacts"])
        central_target_checksums.add(
            str(
                manifest["central_trunk_target_audit"][
                    "selected_edge_checksum"
                ]
            ).lower()
        )
        runtime_fingerprints.add(manifest["runtime_fingerprint"])
        runtime_environments.append(manifest["runtime_environment"])
        relative = path.relative_to(root)
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            raw_rows = list(reader)
        if int(manifest["completed_run_count"]) != len(raw_rows):
            raise ValueError(
                f"campaign {campaign_id!r} manifest completed_run_count does not "
                "match results rows"
            )
        if manifest["status"] == "complete" and (
            int(manifest["planned_run_count"]) != len(raw_rows)
        ):
            raise ValueError(
                f"complete campaign {campaign_id!r} does not contain every planned run"
            )
        if manifest["status"] != "complete":
            analysis_completeness_blockers.append(f"{campaign_id}:partial")
        if not raw_rows:
            skipped.append({"path": relative.as_posix(), "reason": "no_data_rows"})
            campaign_manifests.append(_manifest_record(manifest_path, manifest))
            continue
        required_columns = {"campaign_id", "run_key"}
        missing_columns = required_columns - set(raw_rows[0])
        if missing_columns:
            raise ValueError(
                f"campaign {campaign_id!r} is missing columns: "
                + ", ".join(sorted(missing_columns))
            )
        accepted = 0
        campaign_keys: set[str] = set()
        campaign_rows: list[dict[str, object]] = []
        for row_number, raw in enumerate(raw_rows, start=2):
            row_campaign = str(raw.get("campaign_id", "")).strip()
            if row_campaign != campaign_id:
                raise ValueError(
                    f"{relative.as_posix()} row {row_number} has campaign_id "
                    f"{row_campaign!r}, expected {campaign_id!r}"
                )
            run_key = str(raw.get("run_key", "")).strip().lower()
            if not _is_sha256(run_key):
                raise ValueError(
                    f"{relative.as_posix()} row {row_number} has invalid run_key"
                )
            if run_key in campaign_keys or run_key in global_run_keys:
                raise ValueError(f"duplicate run_key: {run_key}")
            campaign_keys.add(run_key)
            global_run_keys.add(run_key)
            parsed: dict[str, object] = {}
            for field, value in raw.items():
                normalized, blank_numeric = _parse_csv_value(field, value)
                parsed[field] = normalized
                blank_numeric_count += int(blank_numeric)
            rows_by_campaign[campaign_id].append(parsed)
            campaign_rows.append(parsed)
            accepted += 1
        _validate_campaign_result_checksum_contract(
            manifest,
            campaign_rows,
            campaign_id=campaign_id,
            manifest_path=manifest_path,
        )
        source_files.append(
            {
                "path": relative.as_posix(),
                "sha256": _sha256(path),
                "data_row_count": len(raw_rows),
                "accepted_row_count": accepted,
            }
        )
        campaign_manifests.append(_manifest_record(manifest_path, manifest))
    missing_campaigns = [
        campaign for campaign, rows in rows_by_campaign.items() if not rows
    ]
    analysis_completeness_blockers.extend(
        f"{campaign}:missing" for campaign in missing_campaigns
    )
    if stage != "full":
        analysis_completeness_blockers.insert(0, "analysis_stage_is_not_full")
    if len(implementation_fingerprints) > 1:
        raise ValueError(
            "all selected campaign manifests must use the same implementation fingerprint"
        )
    if len(input_fingerprints) > 1 or len(input_artifact_identities) > 1:
        raise ValueError(
            "all selected campaign manifests must use the same input fingerprint "
            "and input artifacts"
        )
    if len(central_target_checksums) > 1:
        raise ValueError(
            "all selected campaign manifests must use the same central target checksum"
        )
    if len(runtime_fingerprints) > 1:
        raise ValueError(
            "all selected campaign manifests must use the same runtime fingerprint"
        )
    return {
        "rows_by_campaign": rows_by_campaign,
        "source_files": source_files,
        "skipped_source_files": skipped,
        "blank_numeric_value_count": blank_numeric_count,
        "campaign_manifests": campaign_manifests,
        "analysis_completeness_blockers": analysis_completeness_blockers,
        "input_fingerprint": (
            next(iter(input_fingerprints)) if input_fingerprints else None
        ),
        "input_artifacts": (
            dict(input_artifact_sets[0]) if input_artifact_sets else None
        ),
        "central_target_checksum": (
            next(iter(central_target_checksums))
            if central_target_checksums
            else None
        ),
        "implementation_fingerprint": (
            next(iter(implementation_fingerprints))
            if implementation_fingerprints
            else None
        ),
        "runtime_fingerprint": (
            next(iter(runtime_fingerprints)) if runtime_fingerprints else None
        ),
        "runtime_environment": (
            dict(runtime_environments[0]) if runtime_environments else None
        ),
    }


def _read_campaign_manifest(
    path: Path,
    *,
    campaign_id: str,
    stage: str,
    design_id: str,
    results_path: Path,
) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read campaign manifest {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"campaign manifest must contain an object: {path}")
    if value.get("final_study_ready") is not False:
        raise ValueError(
            f"campaign manifest must set final_study_ready=false: {path}"
        )
    expected = {
        "design_id": design_id,
        "campaign_id": campaign_id,
        "stage": stage,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            raise ValueError(
                f"campaign manifest {field} must be {expected_value!r}: {path}"
            )
    if value.get("status") not in {"complete", "partial"}:
        raise ValueError(f"campaign manifest has invalid status: {path}")
    for field in ("planned_run_count", "completed_run_count", "pending_run_count"):
        raw = value.get(field)
        if isinstance(raw, bool) or not isinstance(raw, int) or raw < 0:
            raise ValueError(f"campaign manifest has invalid {field}: {path}")
    if value["completed_run_count"] + value["pending_run_count"] != value["planned_run_count"]:
        raise ValueError(f"campaign manifest counts do not reconcile: {path}")
    _validate_campaign_input_provenance(value, path)
    _validate_campaign_implementation_provenance(value, path)
    _validate_campaign_runtime_provenance(value, path)
    _validate_campaign_edge_selection_audits(value, path, campaign_id)
    _verify_results_artifact(value, results_path, path)
    return value


def _validate_campaign_input_provenance(
    manifest: Mapping[str, Any],
    manifest_path: Path,
) -> None:
    fingerprint = manifest.get("input_fingerprint")
    artifacts = manifest.get("input_artifacts")
    if not _is_sha256(fingerprint):
        raise ValueError(
            f"campaign manifest has invalid input_fingerprint: {manifest_path}"
        )
    if not isinstance(artifacts, Mapping) or not artifacts:
        raise ValueError(
            f"campaign manifest lacks input_artifacts: {manifest_path}"
        )
    if set(artifacts) != EXPECTED_INPUT_ARTIFACTS:
        raise ValueError(
            "campaign input_artifacts must contain exact run inputs: "
            f"{manifest_path}"
        )
    entries: list[dict[str, str]] = []
    for name, artifact in sorted(artifacts.items(), key=lambda item: str(item[0])):
        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                f"campaign input artifact has invalid name: {manifest_path}"
            )
        if not isinstance(artifact, Mapping):
            raise ValueError(
                f"campaign input artifact must be an object: {manifest_path}"
            )
        sha256 = artifact.get("sha256")
        path = artifact.get("path")
        size_bytes = artifact.get("size_bytes")
        if not _is_sha256(sha256):
            raise ValueError(
                f"campaign input artifact has invalid sha256: {manifest_path}"
            )
        if not isinstance(path, str) or not path.strip():
            raise ValueError(
                f"campaign input artifact has invalid path: {manifest_path}"
            )
        if (
            isinstance(size_bytes, bool)
            or not isinstance(size_bytes, int)
            or size_bytes < 0
        ):
            raise ValueError(
                f"campaign input artifact has invalid size_bytes: {manifest_path}"
            )
        entries.append({"name": name, "sha256": str(sha256).lower()})
    expected = _sha256_json(entries)
    if str(fingerprint).lower() != expected:
        raise ValueError(
            "campaign input_fingerprint does not match input_artifacts: "
            f"{manifest_path}"
        )


def _input_artifact_identity(artifacts: Mapping[str, Any]) -> str:
    entries = [
        {
            "name": str(name),
            "sha256": str(artifact["sha256"]).lower(),
        }
        for name, artifact in sorted(artifacts.items(), key=lambda item: str(item[0]))
    ]
    return json.dumps(
        entries,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _validate_campaign_implementation_provenance(
    manifest: Mapping[str, Any],
    manifest_path: Path,
) -> None:
    fingerprint = manifest.get("implementation_fingerprint")
    if not _is_sha256(fingerprint):
        raise ValueError(
            f"campaign manifest has invalid implementation_fingerprint: {manifest_path}"
        )
    artifacts = manifest.get("implementation_artifacts")
    if not isinstance(artifacts, Mapping) or not artifacts:
        raise ValueError(
            f"campaign manifest lacks implementation_artifacts: {manifest_path}"
        )
    entries: list[dict[str, str]] = []
    for relative_path, artifact in sorted(
        artifacts.items(), key=lambda item: str(item[0])
    ):
        if not isinstance(relative_path, str) or not relative_path.strip():
            raise ValueError(
                f"campaign implementation artifact has invalid key: {manifest_path}"
            )
        if not isinstance(artifact, Mapping):
            raise ValueError(
                f"campaign implementation artifact must be an object: {manifest_path}"
            )
        sha256 = artifact.get("sha256")
        if not _is_sha256(sha256):
            raise ValueError(
                "campaign implementation artifact has invalid sha256: "
                f"{manifest_path}"
            )
        entries.append(
            {"relative_path": relative_path, "sha256": str(sha256).lower()}
        )
    encoded = json.dumps(
        entries,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    expected = hashlib.sha256(encoded).hexdigest()
    if str(fingerprint).lower() != expected:
        raise ValueError(
            "campaign implementation_fingerprint does not match "
            f"implementation_artifacts: {manifest_path}"
        )


def _validate_campaign_runtime_provenance(
    manifest: Mapping[str, Any],
    manifest_path: Path,
) -> None:
    fingerprint = manifest.get("runtime_fingerprint")
    environment = manifest.get("runtime_environment")
    if not _is_sha256(fingerprint) or not isinstance(environment, Mapping):
        raise ValueError(
            f"campaign manifest lacks valid runtime provenance: {manifest_path}"
        )
    if environment.get("fingerprint") != fingerprint:
        raise ValueError(
            f"campaign runtime fingerprint record is inconsistent: {manifest_path}"
        )
    python = environment.get("python")
    packages = environment.get("packages")
    if not isinstance(python, Mapping) or not isinstance(packages, Mapping):
        raise ValueError(
            f"campaign runtime environment is incomplete: {manifest_path}"
        )
    implementation = python.get("implementation")
    version = python.get("version")
    required_packages = ("networkx", "numpy", "scipy", "SALib", "PyYAML")
    if not all(isinstance(value, str) and value for value in (implementation, version)):
        raise ValueError(
            f"campaign Python runtime record is invalid: {manifest_path}"
        )
    if any(
        not isinstance(packages.get(name), str) or not packages.get(name)
        for name in required_packages
    ):
        raise ValueError(
            f"campaign package runtime record is invalid: {manifest_path}"
        )
    identity = {
        "python": {
            "implementation": implementation,
            "version": version,
        },
        "packages": {name: packages[name] for name in required_packages},
    }
    encoded = json.dumps(
        identity,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    expected = hashlib.sha256(encoded).hexdigest()
    if str(fingerprint).lower() != expected:
        raise ValueError(
            f"campaign runtime_fingerprint does not match environment: {manifest_path}"
        )


def _validate_campaign_edge_selection_audits(
    manifest: Mapping[str, Any],
    manifest_path: Path,
    campaign_id: str,
) -> None:
    target = manifest.get("central_trunk_target_audit")
    if not isinstance(target, Mapping):
        raise ValueError(
            f"campaign manifest lacks central target audit: {manifest_path}"
        )
    if (
        not isinstance(target.get("selected_edge_count"), int)
        or isinstance(target.get("selected_edge_count"), bool)
        or int(target["selected_edge_count"]) < 1
        or not _is_sha256(target.get("selected_edge_checksum"))
        or target.get("contains_coordinates") is not False
    ):
        raise ValueError(f"campaign central target audit is invalid: {manifest_path}")
    for field in (
        "non_road_edge_count",
        "connector_edge_count",
        "nonpositive_length_edge_count",
    ):
        if target.get(field) != 0:
            raise ValueError(
                f"campaign central target audit {field} must be zero: {manifest_path}"
            )
    overlaps = target.get("endpoint_shortest_path_overlap_counts")
    expected_pairs = {"A_to_S", "S_to_A", "R_to_D", "D_to_R"}
    if (
        not isinstance(overlaps, Mapping)
        or set(overlaps) != expected_pairs
        or any(value != 0 for value in overlaps.values())
    ):
        raise ValueError(
            f"campaign central target endpoint overlap audit failed: {manifest_path}"
        )
    endpoint_status = target.get("endpoint_shortest_path_status")
    if (
        not isinstance(endpoint_status, Mapping)
        or set(endpoint_status) != expected_pairs
        or any(value != "available" for value in endpoint_status.values())
    ):
        raise ValueError(
            f"campaign central target endpoint path audit failed: {manifest_path}"
        )

    graph_scope_target = manifest.get("graph_scope_fixed_target_audit")
    if (
        not isinstance(graph_scope_target, Mapping)
        or graph_scope_target.get("selection_scope") != "top3"
        or not isinstance(graph_scope_target.get("selected_edge_count"), int)
        or isinstance(graph_scope_target.get("selected_edge_count"), bool)
        or int(graph_scope_target["selected_edge_count"]) < 1
        or not _is_sha256(graph_scope_target.get("selected_edge_checksum"))
        or graph_scope_target.get("contains_coordinates") is not False
    ):
        raise ValueError(
            f"campaign graph-scope fixed target audit is invalid: {manifest_path}"
        )
    for field in (
        "non_road_edge_count",
        "connector_edge_count",
        "nonpositive_length_edge_count",
    ):
        if graph_scope_target.get(field) != 0:
            raise ValueError(
                "campaign graph-scope fixed target audit "
                f"{field} must be zero: {manifest_path}"
            )
    graph_overlaps = graph_scope_target.get(
        "endpoint_shortest_path_overlap_counts"
    )
    graph_endpoint_status = graph_scope_target.get(
        "endpoint_shortest_path_status"
    )
    if (
        not isinstance(graph_overlaps, Mapping)
        or set(graph_overlaps) != expected_pairs
        or any(value != 0 for value in graph_overlaps.values())
        or not isinstance(graph_endpoint_status, Mapping)
        or set(graph_endpoint_status) != expected_pairs
        or any(value != "available" for value in graph_endpoint_status.values())
    ):
        raise ValueError(
            "campaign graph-scope fixed target audit endpoint check failed: "
            f"{manifest_path}"
        )

    central_checksum = str(target["selected_edge_checksum"]).lower()
    main_checksums = _scenario_checksum_mapping(
        manifest.get("main_scenario_edge_checksums"),
        "main_scenario_edge_checksums",
        manifest_path,
    )
    graph_scope_checksums = _scenario_checksum_mapping(
        manifest.get("graph_scope_scenario_edge_checksums"),
        "graph_scope_scenario_edge_checksums",
        manifest_path,
    )
    main_longhaul = {
        scenario_id: checksum
        for scenario_id, checksum in main_checksums.items()
        if scenario_id.startswith("goseong_long_haul_damage_")
    }
    if not main_longhaul or any(
        checksum != central_checksum for checksum in main_longhaul.values()
    ):
        raise ValueError(
            f"campaign main long-haul checksum disagrees with central target: {manifest_path}"
        )
    if not any(
        scenario_id.startswith("goseong_long_haul_damage_")
        for scenario_id in graph_scope_checksums
    ):
        raise ValueError(
            f"campaign graph-scope long-haul checksum is missing: {manifest_path}"
        )
    graph_scope_target_checksum = str(
        graph_scope_target["selected_edge_checksum"]
    ).lower()
    graph_scope_longhaul = {
        scenario_id: checksum
        for scenario_id, checksum in graph_scope_checksums.items()
        if scenario_id.startswith("goseong_long_haul_damage_")
    }
    if any(
        checksum != graph_scope_target_checksum
        for checksum in graph_scope_longhaul.values()
    ):
        raise ValueError(
            "campaign graph-scope long-haul checksum disagrees with fixed target "
            f"audit: {manifest_path}"
        )

    random_audit = manifest.get("random_threat_selection_audit")
    if campaign_id != "random_threat_outer":
        if random_audit is not None:
            raise ValueError(
                f"non-random campaign has random edge audit: {manifest_path}"
            )
        return
    if not isinstance(random_audit, Mapping):
        raise ValueError(
            f"random-threat campaign lacks edge-selection audit: {manifest_path}"
        )
    if (
        not isinstance(random_audit.get("threat_draw_count"), int)
        or isinstance(random_audit.get("threat_draw_count"), bool)
        or int(random_audit["threat_draw_count"]) < 1
        or random_audit.get("contains_coordinates") is not False
    ):
        raise ValueError(f"random-threat edge audit is invalid: {manifest_path}")
    edge_count_values = random_audit.get("selected_edge_count_values")
    distinct_checksum_count = random_audit.get(
        "distinct_selected_edge_checksum_count"
    )
    if (
        not isinstance(edge_count_values, list)
        or not edge_count_values
        or any(
            isinstance(value, bool) or not isinstance(value, int) or value < 1
            for value in edge_count_values
        )
        or edge_count_values != sorted(set(edge_count_values))
        or isinstance(distinct_checksum_count, bool)
        or not isinstance(distinct_checksum_count, int)
        or distinct_checksum_count < 1
    ):
        raise ValueError(f"random-threat checksum audit is invalid: {manifest_path}")
    for field in (
        "max_non_road_edge_count",
        "max_connector_edge_count",
        "max_nonpositive_length_edge_count",
    ):
        if random_audit.get(field) != 0:
            raise ValueError(
                f"random-threat edge audit {field} must be zero: {manifest_path}"
            )


def _scenario_checksum_mapping(
    value: object,
    field: str,
    manifest_path: Path,
) -> dict[str, str]:
    if not isinstance(value, Mapping) or not value:
        raise ValueError(f"campaign manifest lacks {field}: {manifest_path}")
    normalized: dict[str, str] = {}
    for scenario_id, checksum in value.items():
        if (
            not isinstance(scenario_id, str)
            or not scenario_id.strip()
            or not _is_sha256(checksum)
        ):
            raise ValueError(
                f"campaign manifest has invalid {field}: {manifest_path}"
            )
        normalized[scenario_id] = str(checksum).lower()
    return normalized


def _validate_campaign_result_checksum_contract(
    manifest: Mapping[str, Any],
    rows: Sequence[Mapping[str, object]],
    *,
    campaign_id: str,
    manifest_path: Path,
) -> None:
    central_audit = manifest["central_trunk_target_audit"]
    central_checksum = str(central_audit["selected_edge_checksum"]).lower()
    central_edge_count = int(central_audit["selected_edge_count"])
    graph_scope_checksums = _scenario_checksum_mapping(
        manifest["graph_scope_scenario_edge_checksums"],
        "graph_scope_scenario_edge_checksums",
        manifest_path,
    )
    for row_number, row in enumerate(rows, start=2):
        scenario_id = str(row.get("scenario_id", ""))
        if campaign_id == "path_interdiction_threat":
            main_checksums = _scenario_checksum_mapping(
                manifest.get("main_scenario_edge_checksums"),
                "main_scenario_edge_checksums",
                manifest_path,
            )
            k_value = row.get("interdiction_k")
            if isinstance(k_value, bool) or not isinstance(k_value, int) or k_value < 1:
                raise ValueError(
                    "path-interdiction result lacks a positive integer interdiction_k: "
                    f"{manifest_path} row {row_number}"
                )
            expected_checksum = main_checksums.get(
                f"goseong_path_interdiction_k{k_value}"
            )
            if expected_checksum is None:
                raise ValueError(
                    "path-interdiction result lacks a frozen scenario checksum: "
                    f"{manifest_path} row {row_number}"
                )
            expected_edge_count = k_value
            actual_checksum = row.get("selected_edges_checksum")
            if (
                not _is_sha256(actual_checksum)
                or str(actual_checksum).lower() != expected_checksum
            ):
                raise ValueError(
                    "path-interdiction result checksum disagrees with its frozen target: "
                    f"{manifest_path} row {row_number}"
                )
            edge_count = row.get("selected_edge_count")
            if (
                isinstance(edge_count, bool)
                or not isinstance(edge_count, int)
                or edge_count < 1
                or edge_count != expected_edge_count
            ):
                raise ValueError(
                    "path-interdiction result edge count disagrees with its frozen target: "
                    f"{manifest_path} row {row_number}"
                )
            continue
        uses_target = (
            campaign_id in {"break_even", "break_even_fine", "road_rail_map", "morris"}
            or scenario_id.startswith("goseong_long_haul_damage_")
            or scenario_id.startswith("goseong_path_interdiction_")
        )
        if not uses_target:
            continue
        if campaign_id == "graph_scope":
            expected_checksum = graph_scope_checksums.get(scenario_id)
            expected_edge_count = None
            if expected_checksum is None:
                raise ValueError(
                    "graph-scope long-haul result lacks frozen scenario checksum: "
                    f"{manifest_path} row {row_number}"
                )
        else:
            expected_checksum = central_checksum
            expected_edge_count = central_edge_count
        actual_checksum = row.get("selected_edges_checksum")
        if (
            not _is_sha256(actual_checksum)
            or str(actual_checksum).lower() != expected_checksum
        ):
            raise ValueError(
                "long-haul result checksum disagrees with its frozen target: "
                f"{manifest_path} row {row_number}"
            )
        edge_count = row.get("selected_edge_count")
        if (
            isinstance(edge_count, bool)
            or not isinstance(edge_count, int)
            or edge_count < 1
            or (
                expected_edge_count is not None
                and edge_count != expected_edge_count
            )
        ):
            raise ValueError(
                "long-haul result edge count disagrees with its frozen target: "
                f"{manifest_path} row {row_number}"
            )

    if campaign_id == "random_threat_outer":
        _validate_random_threat_result_audit(manifest, rows, manifest_path)


def _validate_random_threat_result_audit(
    manifest: Mapping[str, Any],
    rows: Sequence[Mapping[str, object]],
    manifest_path: Path,
) -> None:
    audit = manifest["random_threat_selection_audit"]
    by_draw: dict[int, tuple[str, int]] = {}
    for row_number, row in enumerate(rows, start=2):
        draw = row.get("threat_draw")
        checksum = row.get("selected_edges_checksum")
        edge_count = row.get("selected_edge_count")
        if isinstance(draw, bool) or not isinstance(draw, int) or draw < 1:
            raise ValueError(
                f"random-threat result has invalid threat_draw: {manifest_path} row {row_number}"
            )
        if not _is_sha256(checksum):
            raise ValueError(
                "random-threat result has invalid selected edge checksum: "
                f"{manifest_path} row {row_number}"
            )
        if (
            isinstance(edge_count, bool)
            or not isinstance(edge_count, int)
            or edge_count < 1
        ):
            raise ValueError(
                f"random-threat result has invalid edge count: {manifest_path} row {row_number}"
            )
        observation = (str(checksum).lower(), edge_count)
        prior = by_draw.setdefault(draw, observation)
        if prior[0] != observation[0]:
            raise ValueError(
                "random-threat draw checksum is inconsistent across result rows: "
                f"{manifest_path} draw {draw}"
            )
        if prior[1] != observation[1]:
            raise ValueError(
                "random-threat draw edge count is inconsistent across result rows: "
                f"{manifest_path} draw {draw}"
            )

    observed_checksums = {checksum for checksum, _ in by_draw.values()}
    observed_edge_counts = sorted({count for _, count in by_draw.values()})
    expected_draw_count = int(audit["threat_draw_count"])
    expected_distinct = int(audit["distinct_selected_edge_checksum_count"])
    expected_edge_counts = list(audit["selected_edge_count_values"])
    complete = manifest["status"] == "complete"
    if complete and len(by_draw) != expected_draw_count:
        raise ValueError(
            f"random-threat result draw count disagrees with audit: {manifest_path}"
        )
    if not complete and len(by_draw) > expected_draw_count:
        raise ValueError(
            f"partial random-threat results exceed audited draw count: {manifest_path}"
        )
    if complete and len(observed_checksums) != expected_distinct:
        raise ValueError(
            "random-threat result checksum count disagrees with audit: "
            f"{manifest_path}"
        )
    if not complete and len(observed_checksums) > expected_distinct:
        raise ValueError(
            "partial random-threat checksum count exceeds audit: "
            f"{manifest_path}"
        )
    if complete and observed_edge_counts != expected_edge_counts:
        raise ValueError(
            f"random-threat result edge counts disagree with audit: {manifest_path}"
        )
    if not complete and not set(observed_edge_counts).issubset(expected_edge_counts):
        raise ValueError(
            "partial random-threat edge counts fall outside audit: "
            f"{manifest_path}"
        )


def _validate_corridor_evidence_alignment(
    loaded: Mapping[str, Any],
    corridor_scope_evidence: Mapping[str, Any],
) -> None:
    campaign_checksum = loaded.get("central_target_checksum")
    evidence_manifest = corridor_scope_evidence.get("manifest_record")
    if campaign_checksum is None or evidence_manifest is None:
        return
    evidence_checksum = evidence_manifest.get("selected_target_checksum")
    if (
        not _is_sha256(evidence_checksum)
        or str(evidence_checksum).lower() != str(campaign_checksum).lower()
    ):
        raise ValueError(
            "corridor evidence checksum disagrees with campaign central target checksum"
        )


def _verify_results_artifact(
    manifest: Mapping[str, Any],
    results_path: Path,
    manifest_path: Path,
) -> None:
    output_artifacts = manifest.get("output_artifacts")
    if not isinstance(output_artifacts, Mapping):
        raise ValueError(f"campaign manifest lacks output_artifacts: {manifest_path}")
    artifact = output_artifacts.get("results")
    if not isinstance(artifact, Mapping):
        raise ValueError(
            f"campaign manifest lacks results output artifact: {manifest_path}"
        )
    recorded_path = artifact.get("path")
    if not isinstance(recorded_path, str) or not recorded_path.strip():
        raise ValueError(f"results artifact has invalid path: {manifest_path}")
    if Path(recorded_path).expanduser().resolve() != results_path.resolve():
        raise ValueError(f"results artifact path does not match selected CSV: {manifest_path}")
    recorded_size = artifact.get("size_bytes")
    if (
        isinstance(recorded_size, bool)
        or not isinstance(recorded_size, int)
        or recorded_size != results_path.stat().st_size
    ):
        raise ValueError(f"results artifact size mismatch: {manifest_path}")
    recorded_sha = artifact.get("sha256")
    actual_sha = _sha256(results_path)
    if not _is_sha256(recorded_sha) or str(recorded_sha).lower() != actual_sha:
        raise ValueError(f"results artifact SHA-256 mismatch: {manifest_path}")


def _manifest_record(path: Path, manifest: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "path": path.name,
        "sha256": _sha256(path),
        "campaign_id": manifest["campaign_id"],
        "stage": manifest["stage"],
        "status": manifest["status"],
        "planned_run_count": manifest["planned_run_count"],
        "completed_run_count": manifest["completed_run_count"],
        "input_fingerprint": manifest["input_fingerprint"],
        "central_target_checksum": manifest["central_trunk_target_audit"][
            "selected_edge_checksum"
        ],
    }


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdefABCDEF" for character in value)
    )


def _sha256_json(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _parse_csv_value(field: str, value: str | None) -> tuple[object, bool]:
    text = "" if value is None else value.strip()
    numeric = field in _INTEGER_FIELDS or field in _FLOAT_FIELDS
    if not text:
        return (None, True) if numeric else ("", False)
    if field == "factor_values":
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid factor_values JSON: {error.msg}") from error
        if not isinstance(parsed, Mapping):
            raise ValueError("factor_values JSON must contain an object")
        return dict(parsed), False
    if field in _INTEGER_FIELDS:
        try:
            number = float(text)
        except ValueError as error:
            raise ValueError(f"invalid integer field {field!r}: {text!r}") from error
        if not math.isfinite(number) or not number.is_integer():
            raise ValueError(f"invalid integer field {field!r}: {text!r}")
        return int(number), False
    if field in _FLOAT_FIELDS:
        try:
            return float(text), False
        except ValueError as error:
            raise ValueError(f"invalid numeric field {field!r}: {text!r}") from error
    return text, False


def _write_rows(
    path: Path,
    fields: Sequence[str],
    rows: Sequence[Mapping[str, Any]],
) -> Path:
    normalized = [{field: row.get(field) for field in fields} for row in rows]
    if normalized:
        return write_campaign_csv(path, normalized)
    target = assert_isolated_output_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8-sig", newline="") as handle:
        csv.DictWriter(handle, fieldnames=list(fields)).writeheader()
    return target


def _file_record(path: Path, row_count: int) -> dict[str, Any]:
    return {
        "path": path.name,
        "sha256": _sha256(path),
        "data_row_count": row_count,
    }


def _analysis_implementation_provenance() -> dict[str, Any]:
    """Hash analysis code and its local source envelope."""

    relative_paths = {
        "scripts/analyze_paper_revision_results.py",
        "requirements.txt",
    }
    relative_paths.update(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "src").rglob("*.py")
        if path.is_file()
    )
    artifacts: dict[str, dict[str, Any]] = {}
    entries: list[dict[str, str]] = []
    for relative_path in sorted(relative_paths):
        path = ROOT / relative_path
        if not path.is_file():
            raise FileNotFoundError(
                f"analysis implementation file is missing: {relative_path}"
            )
        sha256 = _sha256(path)
        artifacts[relative_path] = {
            "path": str(path.resolve()),
            "sha256": sha256,
            "size_bytes": path.stat().st_size,
        }
        entries.append({"relative_path": relative_path, "sha256": sha256})
    encoded = json.dumps(
        entries,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return {
        "fingerprint": hashlib.sha256(encoded).hexdigest(),
        "artifacts": artifacts,
    }


def _analysis_runtime_provenance() -> dict[str, Any]:
    package_names = ("networkx", "numpy", "scipy", "SALib", "PyYAML")
    packages: dict[str, str] = {}
    for name in package_names:
        try:
            packages[name] = package_metadata.version(name)
        except package_metadata.PackageNotFoundError as exc:
            raise RuntimeError(f"required analysis package is missing: {name}") from exc
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


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _finite_float(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) else None


def _valid_completion(value: object) -> bool:
    number = _finite_float(value)
    return number is not None and 0.0 <= number <= 1.0


def _required_index(value: object, name: str, row_number: int) -> int:
    if isinstance(value, bool):
        raise ValueError(f"row {row_number} {name} must be a non-negative integer")
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"row {row_number} {name} must be a non-negative integer"
        ) from error
    if not math.isfinite(number) or not number.is_integer() or number < 0:
        raise ValueError(f"row {row_number} {name} must be a non-negative integer")
    return int(number)


def _positive_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("smoke", "full"), required=True)
    parser.add_argument("--design-path", type=Path, default=DEFAULT_DESIGN_PATH)
    parser.add_argument(
        "--output-root",
        type=Path,
        help="isolated revision result root; defaults to design output_root",
    )
    parser.add_argument("--bootstrap-replicates", type=int)
    parser.add_argument("--morris-resamples", type=int, default=1_000)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    design = load_revision_design(args.design_path)
    output_root = args.output_root or (ROOT / design.output_root)
    manifest = analyze_output_root(
        output_root,
        stage=args.stage,
        design_path=args.design_path,
        bootstrap_replicates=args.bootstrap_replicates,
        morris_resamples=args.morris_resamples,
    )
    print(f"saved {manifest['analysis_directory']}")
    if manifest["missing_campaigns"]:
        print("missing campaigns: " + ", ".join(manifest["missing_campaigns"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
