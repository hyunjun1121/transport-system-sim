"""Pilot experiment runner for quasi-real transport-resilience profiles.

This module connects the cached pilot GraphML, structured disruption scenario
table, policy-alternative table, and the existing ``run_scenario(...)`` API.
Outputs remain decision-support experiments, not calibrated real-world forecasts
or operational route plans.
"""

from __future__ import annotations

import csv
import ctypes
from datetime import datetime, timezone
import hashlib
import json
import math
import os
import time
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from itertools import islice
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import networkx as nx
import yaml

from src import scenario as scenario_module
from src.policies import StrictPolicy
from src.realworld.adapter import build_simulator_graph, realworld_network_config
from src.realworld.artifact_invalidation_matrix import (
    DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_QUEUE,
    DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_MANIFEST,
    DEFAULT_ARTIFACT_INVALIDATION_MANIFEST,
    artifact_invalidation_blocks_phase9,
    read_artifact_invalidation_closeout_rows,
)
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
    build_road_class_override_metadata,
    load_road_class_overrides,
)
from src.realworld.validation import assert_graph_ready


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGION_PATH = PROJECT_ROOT / "data" / "regions" / "pilot_region.yaml"
DEFAULT_CACHE_PATH = PROJECT_ROOT / "data" / "cache" / "pilot_region_road.graphml"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "results" / "realworld_pilot"
DEFAULT_DESIGN_PATH = PROJECT_ROOT / "data" / "manifests" / "pilot_experiment_design.json"
DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "rail" / "rail_source_decision_manifest.json"
)
DEFAULT_ARTIFACT_INVALIDATION_MANIFEST_PATH = DEFAULT_ARTIFACT_INVALIDATION_MANIFEST
DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_MANIFEST_PATH = (
    DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_MANIFEST
)
DEFAULT_RESULTS_PATH = DEFAULT_OUTPUT_DIR / "pilot_sample_results.csv"
DEFAULT_SUMMARY_PATH = DEFAULT_OUTPUT_DIR / "pilot_sample_summary.csv"
DEFAULT_MANIFEST_PATH = DEFAULT_OUTPUT_DIR / "pilot_result_manifest.json"
DEFAULT_SAMPLE_MANIFEST_PATH = DEFAULT_OUTPUT_DIR / "pilot_sample_manifest.json"
DEFAULT_DEMAND_PROFILES_PATH = PROJECT_ROOT / "data" / "scenarios" / "demand_profiles.csv"
DEFAULT_FLEET_PROFILES_PATH = PROJECT_ROOT / "data" / "scenarios" / "fleet_profiles.csv"
COMPACT_CLOSEOUT_REGENERATION_SCOPE = "compact_outputs"
CLOSEOUT_REGENERATION_SCOPES = frozenset({COMPACT_CLOSEOUT_REGENERATION_SCOPE})

DEFAULT_SAMPLE_PROFILE_ID = "sample_scaffold"
DEFAULT_STAGED_PROFILE_ID = "staged_pilot"
DEFAULT_FULL_PROFILE_ID = "full_pilot"
DEFAULT_MULTI_CORRIDOR_PROFILE_ID = "multi_corridor_candidate"
DEFAULT_MULTI_CORRIDOR_FULL_PROFILE_ID = "multi_corridor_full_candidate"
DEFAULT_FULL_GRAPH_PROFILE_ID = "full_graph"
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
ENGINEERING_ONLY_CLAIM_SCOPE = (
    "Engineering-only pilot output for quasi-real decision-support method review "
    "(non-publication, non-acceptance, non-operational); not publication "
    "evidence, not final-study evidence, not formal acceptance evidence, not "
    "calibrated real-world results, and not an operational route plan or "
    "forecast."
)

RESULT_COLUMNS = (
    "region_id",
    "graph_source",
    "policy_id",
    "scenario_id",
    "scenario_family",
    "scenario_type",
    "disruption_mode",
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
    "disruption_mode",
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
    rail_travel_time_multiplier: float | None = None
    rail_headway_multiplier: float | None = None
    rail_capacity_multiplier: float | None = None
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
    demand_profile_id: str = "pilot_default_demand"
    fleet_profile_id: str = "pilot_default_fleet"
    rail_service_profile_id: str = "pilot_fixed_headway_rail_proxy"
    validation_profile_id: str = "pilot_graph_ready_and_plausibility_review"
    road_network_profile_id: str = "pilot_cached_osm_graph"
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


class PilotExperimentPreflightError(RuntimeError):
    """Raised when a pilot experiment profile fails Phase 8 evidence preflight."""


def run_pilot_experiments(
    *,
    region_path: str | Path = DEFAULT_REGION_PATH,
    cache_path: str | Path = DEFAULT_CACHE_PATH,
    scenarios_path: str | Path = DEFAULT_SCENARIO_PATH,
    policies_path: str | Path = DEFAULT_POLICY_ALTERNATIVES_PATH,
    design_path: str | Path = DEFAULT_DESIGN_PATH,
    rail_source_decision_manifest_path: str | Path = (
        DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH
    ),
    artifact_invalidation_manifest_path: str | Path = (
        DEFAULT_ARTIFACT_INVALIDATION_MANIFEST_PATH
    ),
    artifact_invalidation_closeout_manifest_path: str | Path = (
        DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_MANIFEST_PATH
    ),
    closeout_action_queue_path: str | Path = (
        DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_QUEUE
    ),
    demand_profiles_path: str | Path = DEFAULT_DEMAND_PROFILES_PATH,
    fleet_profiles_path: str | Path = DEFAULT_FLEET_PROFILES_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    road_class_overrides_path: str | Path | None = None,
    seeds: Sequence[int] | None = None,
    sample: bool = True,
    run_profile: str | None = None,
    policy_ids: Sequence[str] | None = None,
    scenario_ids: Sequence[str] | None = None,
    engineering_only: bool = False,
    closeout_regeneration_scope: str | None = None,
) -> dict[str, Any]:
    """Run a named pilot design profile and write separated CSV plus manifest outputs."""

    started_at_utc = _utc_now()
    start_counter = time.perf_counter()
    memory_before = _memory_status_snapshot()
    design, profile = resolve_pilot_experiment_profile(
        design_path=design_path,
        run_profile=run_profile,
        sample=sample,
    )
    phase8_preflight = assert_pilot_experiment_preflight(
        profile,
        engineering_only=engineering_only,
        rail_source_decision_manifest_path=rail_source_decision_manifest_path,
        artifact_invalidation_manifest_path=artifact_invalidation_manifest_path,
        artifact_invalidation_closeout_manifest_path=(
            artifact_invalidation_closeout_manifest_path
        ),
        closeout_action_queue_path=closeout_action_queue_path,
        closeout_regeneration_scope=closeout_regeneration_scope,
    )
    result_scope = (
        _engineering_only_claim_scope(profile.result_scope)
        if engineering_only and not profile.sample_scaffold
        else _closeout_regeneration_claim_scope(profile.result_scope)
        if closeout_regeneration_scope and not profile.sample_scaffold
        else profile.result_scope
    )
    resolved_seeds = tuple(int(seed) for seed in (seeds if seeds is not None else profile.seeds))
    resolved_policy_ids = tuple(policy_ids) if policy_ids is not None else profile.policy_ids
    resolved_scenario_ids = tuple(scenario_ids) if scenario_ids is not None else profile.scenario_ids
    output_lock = _acquire_output_lock(output_dir, profile.output_prefix, started_at_utc)

    try:
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
            claim_scope=result_scope,
            demand_profile_id=profile.demand_profile_id,
            fleet_profile_id=profile.fleet_profile_id,
            demand_profiles_path=demand_profiles_path,
            fleet_profiles_path=fleet_profiles_path,
        )
        summary_rows = summarize_pilot_rows(rows)
        finished_at_utc = _utc_now()
        runtime_metadata = _runtime_metadata(
            started_at_utc=started_at_utc,
            finished_at_utc=finished_at_utc,
            wall_time_seconds=time.perf_counter() - start_counter,
            memory_before=memory_before,
            memory_after=_memory_status_snapshot(),
        )

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
                rail_source_decision_manifest_path=rail_source_decision_manifest_path,
                artifact_invalidation_manifest_path=artifact_invalidation_manifest_path,
                artifact_invalidation_closeout_manifest_path=(
                    artifact_invalidation_closeout_manifest_path
                ),
                closeout_action_queue_path=closeout_action_queue_path,
                demand_profiles_path=demand_profiles_path,
                fleet_profiles_path=fleet_profiles_path,
                output_dir=output_dir,
                road_class_overrides_path=road_class_overrides_path,
                overrides={
                    "policy_ids": policy_ids is not None,
                    "scenario_ids": scenario_ids is not None,
                    "seeds": seeds is not None,
                },
                result_scope=result_scope,
                phase8_preflight=phase8_preflight,
                runtime=runtime_metadata,
                output_lock=output_lock,
            ),
        )
        release = _release_output_lock(output_lock)
        updated_manifest = _finalize_manifest_after_output_write(
            manifest=paths["manifest"],
            output_lock_release=release,
            manifest_path=paths["manifest_path"],
            results_path=paths["results"],
            summary_path=paths["summary"],
        )
        paths["manifest"] = updated_manifest
        receipt_path = _write_output_lock_receipt(
            output_lock=output_lock,
            release=release,
            manifest_path=paths["manifest_path"],
            results_path=paths["results"],
            summary_path=paths["summary"],
        )
        result = {
            "rows": rows,
            "summary_rows": summary_rows,
            "manifest": paths["manifest"],
            "results_path": paths["results"],
            "summary_path": paths["summary"],
            "manifest_path": paths["manifest_path"],
            "output_lock_receipt_path": receipt_path,
        }
        if "legacy_manifest_path" in paths:
            result["legacy_manifest_path"] = paths["legacy_manifest_path"]
        return result
    finally:
        _release_output_lock(output_lock)


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


def assert_pilot_experiment_preflight(
    profile: PilotExperimentProfile,
    *,
    engineering_only: bool,
    rail_source_decision_manifest_path: str | Path = (
        DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH
    ),
    artifact_invalidation_manifest_path: str | Path = (
        DEFAULT_ARTIFACT_INVALIDATION_MANIFEST_PATH
    ),
    artifact_invalidation_closeout_manifest_path: str | Path = (
        DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_MANIFEST_PATH
    ),
    closeout_action_queue_path: str | Path = (
        DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_QUEUE
    ),
    closeout_regeneration_scope: str | None = None,
) -> dict[str, Any]:
    """Return Phase 8 preflight metadata or block overread-prone profiles."""

    manifest_path = Path(rail_source_decision_manifest_path)
    manifest, load_error = _load_rail_source_decision_manifest(manifest_path)
    pending_reasons = _rail_source_decision_pending_reasons(manifest, load_error)
    pending = bool(pending_reasons)
    invalidation_path = Path(artifact_invalidation_manifest_path)
    closeout_path = Path(artifact_invalidation_closeout_manifest_path)
    scope = _validated_closeout_regeneration_scope(closeout_regeneration_scope)
    invalidation_blocks, invalidation_reasons, invalidation_summary = (
        artifact_invalidation_blocks_phase9(invalidation_path, closeout_path)
    )
    non_sample = not profile.sample_scaffold
    has_blocker = bool(pending or invalidation_blocks)
    bypass = bool(engineering_only and non_sample and has_blocker)

    preflight = {
        "schema_version": 1,
        "profile_id": profile.profile_id,
        "run_stage": profile.run_stage,
        "sample_scaffold": profile.sample_scaffold,
        "engineering_only": bool(engineering_only),
        "engineering_only_bypass": bypass,
        "required_for_non_sample": non_sample,
        "rail_source_decision_manifest_path": _display_path(manifest_path),
        "rail_source_decision_manifest_exists": manifest_path.exists(),
        "rail_source_decision_manifest_sha256": (
            _file_sha256(manifest_path) if manifest_path.exists() else None
        ),
        "rail_source_decisions_pending": pending,
        "pending_reasons": pending_reasons,
        "rail_source_decision_snapshot": _rail_source_decision_snapshot(manifest),
        "artifact_invalidation_manifest_path": _display_path(invalidation_path),
        "artifact_invalidation_manifest_exists": invalidation_path.exists(),
        "artifact_invalidation_manifest_sha256": (
            _file_sha256(invalidation_path) if invalidation_path.exists() else None
        ),
        "artifact_invalidation_closeout_manifest_path": _display_path(closeout_path),
        "artifact_invalidation_closeout_manifest_exists": closeout_path.exists(),
        "artifact_invalidation_closeout_manifest_sha256": (
            _file_sha256(closeout_path) if closeout_path.exists() else None
        ),
        "artifact_invalidation_blocks_phase9": invalidation_blocks,
        "artifact_invalidation_pending_reasons": invalidation_reasons,
        "artifact_invalidation_snapshot": invalidation_summary,
        "closeout_regeneration_scope": scope or "",
        "closeout_regeneration_scope_status": "not_requested",
        "closeout_regeneration_scope_review": {},
        "scope_invalidation_blocks": False,
        "status": "passed",
    }
    if profile.sample_scaffold:
        preflight["status"] = "sample_skipped"
        return preflight
    if scope:
        scope_review = _closeout_regeneration_scope_review(
            scope=scope,
            closeout_manifest_path=closeout_path,
            closeout_action_queue_path=Path(closeout_action_queue_path),
        )
        preflight["closeout_regeneration_scope_status"] = scope_review["status"]
        preflight["closeout_regeneration_scope_review"] = scope_review
        preflight["scope_invalidation_blocks"] = bool(scope_review["blocks_scope"])
        if scope_review["blocks_scope"]:
            preflight["status"] = "blocked_closeout_regeneration_prerequisites"
            reasons = "; ".join(scope_review["blocking_reasons"])
            raise PilotExperimentPreflightError(
                f"{profile.profile_id} cannot run as scoped closeout regeneration "
                f"for {scope}: {reasons}."
            )
        if invalidation_blocks:
            preflight["status"] = "scoped_closeout_regeneration"
            return preflight
    if has_blocker and engineering_only:
        preflight["status"] = "engineering_only_bypass"
        return preflight
    if pending:
        preflight["status"] = "blocked_pending_rail_source_decisions"
        reasons = "; ".join(pending_reasons)
        raise PilotExperimentPreflightError(
            f"{profile.profile_id} cannot run as {profile.run_stage} evidence while "
            f"rail source decisions remain pending: {reasons}. Use "
            "engineering_only=True only for explicitly non-publication, "
            "non-acceptance, non-operational method checks."
        )
    if invalidation_blocks:
        preflight["status"] = "blocked_unresolved_artifact_invalidation"
        reasons = "; ".join(invalidation_reasons)
        raise PilotExperimentPreflightError(
            f"{profile.profile_id} cannot run as {profile.run_stage} evidence while "
            f"artifact invalidation blockers remain unresolved: {reasons}. Use "
            "engineering_only=True only for explicitly non-publication, "
            "non-acceptance, non-operational method checks."
        )
    return preflight


def _load_rail_source_decision_manifest(
    path: Path,
) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return None, "rail source-decision manifest is missing"
    try:
        with path.open("r", encoding="utf-8") as handle:
            loaded = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"rail source-decision manifest could not be read: {exc}"
    if not isinstance(loaded, dict):
        return None, "rail source-decision manifest is not a JSON object"
    return loaded, None


def _rail_source_decision_pending_reasons(
    manifest: Mapping[str, Any] | None,
    load_error: str | None,
) -> list[str]:
    if load_error:
        return [load_error]
    if manifest is None:
        return ["rail source-decision manifest is unavailable"]

    reasons: list[str] = []
    if not bool(manifest.get("rail_source_decision_recorded", False)):
        reasons.append("rail_source_decision_recorded is false")

    required_true_flags = (
        "publication_ready",
        "can_mark_complete",
        "can_support_rail_evidence_gate",
        "can_support_acceptance_gate",
    )
    for flag in required_true_flags:
        if not bool(manifest.get(flag, False)):
            reasons.append(f"{flag} is false")

    closure_candidate_count = _optional_int(
        manifest.get("rail_service_evidence_gate_closure_candidate_count")
    )
    if closure_candidate_count is not None and closure_candidate_count <= 0:
        reasons.append(
            "rail_service_evidence_gate_closure_candidate_count is zero"
        )

    row_count = _optional_int(manifest.get("row_count"))
    completed_count = _optional_int(manifest.get("completed_source_decision_count"))
    if row_count is not None and completed_count is not None and completed_count < row_count:
        reasons.append(
            f"completed_source_decision_count {completed_count} is below row_count {row_count}"
        )

    action_counts = _positive_status_counts(
        manifest.get("action_decision_status_counts"),
        tokens=("pending", "blocked", "invalid", "incomplete", "needs"),
    )
    if action_counts:
        reasons.append(f"action_decision_status_counts has unresolved rows: {action_counts}")

    decision_counts = _positive_status_counts(
        manifest.get("decision_status_counts"),
        tokens=("pending", "blocked", "invalid", "incomplete", "needs"),
    )
    if decision_counts:
        reasons.append(f"decision_status_counts has unresolved rows: {decision_counts}")

    remaining_blockers = manifest.get("remaining_blockers")
    if isinstance(remaining_blockers, list) and remaining_blockers:
        reasons.append(f"remaining_blockers has {len(remaining_blockers)} item(s)")
    return reasons


def _rail_source_decision_snapshot(
    manifest: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if manifest is None:
        return {}
    keys = (
        "rail_source_decision_recorded",
        "can_support_rail_evidence_gate",
        "can_support_acceptance_gate",
        "can_mark_complete",
        "publication_ready",
        "rail_service_evidence_gate_closure_candidate_count",
        "claim_boundary",
        "result_scope",
        "remaining_blockers",
        "action_decision_status_counts",
        "decision_status_counts",
        "row_count",
        "completed_source_decision_count",
    )
    return {key: manifest.get(key) for key in keys if key in manifest}


def _positive_status_counts(raw: Any, *, tokens: Sequence[str]) -> dict[str, int]:
    if not isinstance(raw, Mapping):
        return {}
    result: dict[str, int] = {}
    for key, value in raw.items():
        count = _optional_int(value)
        if count is None or count <= 0:
            continue
        key_text = str(key).lower()
        if any(token in key_text for token in tokens):
            result[str(key)] = count
    return result


def _optional_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _validated_closeout_regeneration_scope(raw: str | None) -> str | None:
    if raw is None:
        return None
    scope = str(raw).strip()
    if not scope:
        return None
    if scope not in CLOSEOUT_REGENERATION_SCOPES:
        allowed = ", ".join(sorted(CLOSEOUT_REGENERATION_SCOPES))
        raise ValueError(f"closeout_regeneration_scope must be one of: {allowed}")
    return scope


def _closeout_regeneration_scope_review(
    *,
    scope: str,
    closeout_manifest_path: Path,
    closeout_action_queue_path: Path,
) -> dict[str, Any]:
    review: dict[str, Any] = {
        "scope": scope,
        "status": "blocked",
        "blocks_scope": True,
        "blocking_reasons": [],
        "prerequisite_action_batches": [],
        "target_row_ids": [],
        "closed_prerequisite_row_count": 0,
        "required_prerequisite_row_count": 0,
    }
    if not closeout_manifest_path.exists():
        review["blocking_reasons"].append("closeout manifest is missing")
        return review
    try:
        closeout_manifest = json.loads(
            closeout_manifest_path.read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as exc:
        review["blocking_reasons"].append(f"closeout manifest could not be read: {exc}")
        return review
    if not isinstance(closeout_manifest, dict):
        review["blocking_reasons"].append("closeout manifest is not a JSON object")
        return review
    outputs = closeout_manifest.get("outputs", {})
    closeout_csv_value = outputs.get("csv", "") if isinstance(outputs, dict) else ""
    if not closeout_csv_value:
        review["blocking_reasons"].append("closeout manifest does not name its CSV")
        return review
    closeout_csv = Path(str(closeout_csv_value))
    if not closeout_csv.is_absolute():
        closeout_csv = PROJECT_ROOT / closeout_csv
    try:
        closeout_rows = read_artifact_invalidation_closeout_rows(closeout_csv)
    except (OSError, ValueError) as exc:
        review["blocking_reasons"].append(f"closeout CSV could not be read: {exc}")
        return review
    try:
        action_rows = _read_closeout_action_queue_rows(closeout_action_queue_path)
    except ValueError as exc:
        review["blocking_reasons"].append(str(exc))
        return review
    target_orders = [
        order
        for order in (
            _optional_int(row.get("action_order"))
            for row in action_rows
            if row.get("action_batch") == scope
        )
        if order is not None
    ]
    if not target_orders:
        review["blocking_reasons"].append(f"action queue has no rows for {scope}")
        return review
    first_target_order = min(target_orders)
    prerequisite_rows = [
        row
        for row in action_rows
        if (_optional_int(row.get("action_order")) or 0) < first_target_order
    ]
    target_rows = [row for row in action_rows if row.get("action_batch") == scope]
    review["prerequisite_action_batches"] = sorted(
        {
            row.get("action_batch", "")
            for row in prerequisite_rows
            if row.get("action_batch")
        }
    )
    review["target_row_ids"] = [
        str(row.get("invalidation_row_id", "")) for row in target_rows
    ]
    closeout_by_id = {
        row.get("invalidation_row_id", ""): row
        for row in closeout_rows
        if row.get("invalidation_row_id")
    }
    missing_or_open: list[str] = []
    for action_row in prerequisite_rows:
        row_id = str(action_row.get("invalidation_row_id", ""))
        closeout_row = closeout_by_id.get(row_id)
        if closeout_row is None:
            missing_or_open.append(f"{row_id}:missing_closeout_row")
            continue
        if str(closeout_row.get("can_clear_invalidation_gate", "")).lower() != "true":
            missing_or_open.append(f"{row_id}:not_closed")
    review["required_prerequisite_row_count"] = len(prerequisite_rows)
    review["closed_prerequisite_row_count"] = (
        len(prerequisite_rows) - len(missing_or_open)
    )
    if missing_or_open:
        review["blocking_reasons"].append(
            "prerequisite closeout rows are not closed: " + ", ".join(missing_or_open)
        )
        return review
    review["status"] = "passed"
    review["blocks_scope"] = False
    return review


def _read_closeout_action_queue_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise ValueError(f"closeout action queue is missing: {_display_path(path)}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _engineering_only_claim_scope(base_scope: str) -> str:
    base = str(base_scope or "").strip()
    if not base:
        return ENGINEERING_ONLY_CLAIM_SCOPE
    if ENGINEERING_ONLY_CLAIM_SCOPE in base:
        return base
    return f"{ENGINEERING_ONLY_CLAIM_SCOPE} Base profile scope: {base}"


def _closeout_regeneration_claim_scope(base_scope: str) -> str:
    base = str(base_scope or "").strip()
    suffix = (
        "Scoped compact-output invalidation-regeneration artifact only; not "
        "publication evidence, not final-study evidence, not formal acceptance "
        "evidence, and not operational evidence."
    )
    if not base:
        return suffix
    if suffix in base:
        return base
    return f"{suffix} Base profile scope: {base}"


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
    road_class_override_metadata = None
    if road_class_overrides_path is not None:
        override_records = load_road_class_overrides(road_class_overrides_path)
        highway_defaults = build_highway_defaults_with_overrides(override_records)
        road_class_override_metadata = build_road_class_override_metadata(
            override_records
        )
    graph = build_simulator_graph(
        road_graph,
        region,
        highway_defaults=highway_defaults,
        road_class_override_metadata=road_class_override_metadata,
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
            "background_volume": 300.0,
        },
        "failure": {
            "mode": "blocked",
            "capacity_reduction_factor": 1.0,
        },
        "metrics": {
            "late_penalty_min": 300.0,
        },
        "bpr": {
            "alpha": 0.50,
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
            "time_limit": 200.0,
        },
        "stochastic": {
            "road_noise_sigma": 0.05,
            "turnaround_noise_lambda": 0.2,
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
    demand_profile_id: str = "pilot_default_demand",
    fleet_profile_id: str = "pilot_default_fleet",
    demand_profiles_path: str | Path = DEFAULT_DEMAND_PROFILES_PATH,
    fleet_profiles_path: str | Path = DEFAULT_FLEET_PROFILES_PATH,
) -> list[dict[str, Any]]:
    """Execute all policy, disruption, and seed combinations."""

    rows: list[dict[str, Any]] = []
    base_config, _ = apply_pilot_demand_fleet_profiles(
        make_pilot_base_config(inputs.region),
        demand_profile_id=demand_profile_id,
        fleet_profile_id=fleet_profile_id,
        demand_profiles_path=demand_profiles_path,
        fleet_profiles_path=fleet_profiles_path,
    )
    profile_sigma = _profile_run_sigma(base_config)
    for case in cases:
        disrupted_graph = graph_with_forced_disruption_probabilities(
            inputs.graph, case,
            force_deterministic=True,
        )
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
                        "sigma": profile_sigma,
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
    *,
    force_deterministic: bool = True,
    selection_p_fail: float = 0.8,
) -> nx.DiGraph:
    """Copy a graph and force deterministic selected-road disruption sampling."""

    prepared = graph.copy()
    if force_deterministic:
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
    else:
        for selected in case.selected_edges:
            if not prepared.has_edge(*selected.edge):
                raise ValueError(f"selected edge missing from graph: {selected.edge!r}")
            data = prepared.edges[selected.edge]
            if data.get("mode") == "road":
                data["p_fail"] = selection_p_fail
                data["base_p_fail"] = selection_p_fail
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
        unique_claim_scopes = sorted(set(claim_scopes))
        if len(unique_claim_scopes) > 1:
            raise ValueError(
                "summary group contains mixed claim_scope values; split outputs "
                "or rerun with one explicit claim boundary"
            )
        summary["claim_scope"] = unique_claim_scopes[0] if unique_claim_scopes else CLAIM_SCOPE
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
    rail_source_decision_manifest_path: str | Path = (
        DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH
    ),
    artifact_invalidation_manifest_path: str | Path = (
        DEFAULT_ARTIFACT_INVALIDATION_MANIFEST_PATH
    ),
    artifact_invalidation_closeout_manifest_path: str | Path = (
        DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_MANIFEST_PATH
    ),
    closeout_action_queue_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_QUEUE,
    demand_profiles_path: str | Path = DEFAULT_DEMAND_PROFILES_PATH,
    fleet_profiles_path: str | Path = DEFAULT_FLEET_PROFILES_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    road_class_overrides_path: str | Path | None = None,
    overrides: Mapping[str, bool] | None = None,
    result_scope: str | None = None,
    phase8_preflight: Mapping[str, Any] | None = None,
    runtime: Mapping[str, Any] | None = None,
    output_lock: Mapping[str, Any] | None = None,
    sample: bool | None = None,
) -> dict[str, Any]:
    """Return deterministic metadata for generated pilot experiment outputs."""

    if design is None or profile is None:
        design, profile = resolve_pilot_experiment_profile(
            design_path=design_path,
            sample=True if sample is None else bool(sample),
        )

    expected_row_count = len(policies) * len(cases) * len(seeds)
    executed_policy_ids = tuple(policy.policy_id for policy in policies)
    executed_scenario_ids = tuple(case.scenario_id for case in cases)
    executed_seeds = tuple(int(seed) for seed in seeds)
    profile_design_complete = (
        executed_policy_ids == tuple(profile.policy_ids)
        and executed_scenario_ids == tuple(profile.scenario_ids)
        and executed_seeds == tuple(int(seed) for seed in profile.seeds)
    )
    design_overrides = dict(overrides or {})
    engineering_override_run = bool(
        not profile_design_complete or any(bool(value) for value in design_overrides.values())
    )
    output_files = _output_file_manifest(
        output_dir=output_dir,
        output_prefix=profile.output_prefix,
        include_legacy_sample_manifest=profile.profile_id == DEFAULT_SAMPLE_PROFILE_ID,
    )
    effective_result_scope = str(result_scope or profile.result_scope)
    phase8_metadata = dict(phase8_preflight or {})
    runtime_metadata = dict(runtime or {})
    output_lock_metadata = dict(output_lock or {})
    closeout_scope = str(phase8_metadata.get("closeout_regeneration_scope", ""))
    closeout_scope_status = str(
        phase8_metadata.get("closeout_regeneration_scope_status", "")
    )
    clean_checkout_status = str(
        phase8_metadata.get(
            "clean_checkout_status",
            (
                "not_required_for_current_closeout"
                if closeout_scope == COMPACT_CLOSEOUT_REGENERATION_SCOPE
                and closeout_scope_status == "passed"
                else ""
            ),
        )
    )
    rail_manifest_path = Path(rail_source_decision_manifest_path)
    invalidation_manifest_path = Path(artifact_invalidation_manifest_path)
    invalidation_closeout_manifest_path = Path(artifact_invalidation_closeout_manifest_path)
    closeout_action_queue_file = Path(closeout_action_queue_path)
    base_config, profile_application = apply_pilot_demand_fleet_profiles(
        make_pilot_base_config(inputs.region),
        demand_profile_id=profile.demand_profile_id,
        fleet_profile_id=profile.fleet_profile_id,
        demand_profiles_path=demand_profiles_path,
        fleet_profiles_path=fleet_profiles_path,
    )
    config_hashes = _config_hash_summary(
        base_config=base_config,
        policies=policies,
        cases=cases,
    )
    executed_command = _executed_command(
        profile=profile,
        output_dir=output_dir,
        design_path=design_path,
        region_path=region_path,
        cache_path=cache_path,
        scenarios_path=scenarios_path,
        policies_path=policies_path,
        rail_source_decision_manifest_path=rail_source_decision_manifest_path,
        artifact_invalidation_manifest_path=artifact_invalidation_manifest_path,
        artifact_invalidation_closeout_manifest_path=(
            artifact_invalidation_closeout_manifest_path
        ),
        closeout_action_queue_path=closeout_action_queue_path,
        road_class_overrides_path=road_class_overrides_path,
        policy_ids=executed_policy_ids,
        scenario_ids=executed_scenario_ids,
        seeds=executed_seeds,
        engineering_only=bool(phase8_metadata.get("engineering_only", False)),
        closeout_regeneration_scope=str(
            phase8_metadata.get("closeout_regeneration_scope", "")
        ),
        design_overrides=design_overrides,
    )

    return {
        "schema_version": 2,
        "result_scope": effective_result_scope,
        "command": _profile_command(profile),
        "executed_command": executed_command,
        "run_profile": profile.profile_id,
        "run_stage": profile.run_stage,
        "sample_scaffold": profile.sample_scaffold,
        "output_prefix": profile.output_prefix,
        "output_dir": _display_path(output_dir),
        "design_status": profile.design_status,
        "design_status_is_approval": False,
        "design_scope": design.design_scope,
        "design_claim_boundary": design.claim_boundary,
        "engineering_only": bool(phase8_metadata.get("engineering_only", False)),
        "closeout_regeneration_scope": closeout_scope,
        "closeout_regeneration_scope_status": closeout_scope_status,
        "clean_checkout_status": clean_checkout_status,
        "scope_invalidation_blocks": bool(
            phase8_metadata.get("scope_invalidation_blocks", False)
        ),
        "engineering_only_bypass": bool(
            phase8_metadata.get("engineering_only_bypass", False)
        ),
        "artifact_invalidation_blocks_phase9": bool(
            phase8_metadata.get("artifact_invalidation_blocks_phase9", False)
        ),
        "rail_source_decisions_pending": bool(
            phase8_metadata.get("rail_source_decisions_pending", False)
        ),
        "engineering_override_run": engineering_override_run,
        "profile_design_complete": profile_design_complete,
        "publication_ready": False,
        "final_study_ready": False,
        "operational_use_allowed": False,
        "formal_acceptance_evidence": False,
        "publication_scope": "not publication evidence",
        "acceptance_scope": "not formal acceptance evidence",
        "operational_scope": "not operational route plan or forecast",
        "design_path": _display_path(design_path),
        "rail_source_decision_manifest_path": _display_path(rail_manifest_path),
        "rail_source_decision_manifest_sha256": (
            _file_sha256(rail_manifest_path) if rail_manifest_path.exists() else None
        ),
        "artifact_invalidation_manifest_path": _display_path(invalidation_manifest_path),
        "artifact_invalidation_manifest_sha256": (
            _file_sha256(invalidation_manifest_path)
            if invalidation_manifest_path.exists()
            else None
        ),
        "artifact_invalidation_closeout_manifest_path": _display_path(
            invalidation_closeout_manifest_path
        ),
        "artifact_invalidation_closeout_manifest_sha256": (
            _file_sha256(invalidation_closeout_manifest_path)
            if invalidation_closeout_manifest_path.exists()
            else None
        ),
        "closeout_action_queue_path": _display_path(closeout_action_queue_file),
        "closeout_action_queue_sha256": (
            _file_sha256(closeout_action_queue_file)
            if closeout_action_queue_file.exists()
            else None
        ),
        "phase8_preflight": phase8_metadata,
        "runtime": runtime_metadata,
        "output_lock": output_lock_metadata,
        "output_lock_release": {
            "release_status": "pending_until_outputs_are_written",
        },
        "output_inventory": {
            "status": "pending_until_outputs_are_written",
            "manifest_self_hash_policy": (
                "Final manifest SHA256 is recorded in the separate output-lock "
                "receipt to avoid self-referential manifest hashing."
            ),
        },
        "profile_refs": {
            "demand_profile_id": profile.demand_profile_id,
            "fleet_profile_id": profile.fleet_profile_id,
            "rail_service_profile_id": profile.rail_service_profile_id,
            "validation_profile_id": profile.validation_profile_id,
            "road_network_profile_id": profile.road_network_profile_id,
        },
        "profile_application": profile_application,
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
            "region_sha256": _file_sha256(region_path) if Path(region_path).exists() else None,
            "cache_path": _display_path(cache_path),
            "cache_sha256": _file_sha256(cache_path) if Path(cache_path).exists() else None,
            "disruption_scenarios_path": _display_path(scenarios_path),
            "disruption_scenarios_sha256": (
                _file_sha256(scenarios_path) if Path(scenarios_path).exists() else None
            ),
            "policy_alternatives_path": _display_path(policies_path),
            "policy_alternatives_sha256": (
                _file_sha256(policies_path) if Path(policies_path).exists() else None
            ),
            "pilot_experiment_design_path": _display_path(design_path),
            "pilot_experiment_design_sha256": (
                _file_sha256(design_path) if Path(design_path).exists() else None
            ),
            "demand_profiles_path": _display_path(demand_profiles_path),
            "demand_profiles_sha256": (
                _file_sha256(demand_profiles_path)
                if Path(demand_profiles_path).exists()
                else None
            ),
            "fleet_profiles_path": _display_path(fleet_profiles_path),
            "fleet_profiles_sha256": (
                _file_sha256(fleet_profiles_path)
                if Path(fleet_profiles_path).exists()
                else None
            ),
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
        "config_hashes": config_hashes,
        "policy_ids": [policy.policy_id for policy in policies],
        "scenario_ids": [case.scenario_id for case in cases],
        "seeds": [int(seed) for seed in seeds],
        "row_count": len(rows),
        "summary_row_count": len(summary_rows),
        "expected_row_count": expected_row_count,
        "profile_design_policy_count": len(profile.policy_ids),
        "profile_design_scenario_count": len(profile.scenario_ids),
        "profile_design_seed_count": len(profile.seeds),
        "profile_design_row_count": (
            len(profile.policy_ids) * len(profile.scenario_ids) * len(profile.seeds)
        ),
        "executed_policy_count": len(policies),
        "executed_scenario_count": len(cases),
        "executed_seed_count": len(seeds),
        "executed_row_count": len(rows),
        "scenario_policy_seed_design": {
            "policy_count": len(policies),
            "scenario_count": len(cases),
            "seed_count": len(seeds),
            "expected_row_count": expected_row_count,
            "common_random_numbers": True,
        },
        "design_overrides": design_overrides,
        "excluded_policy_ids": dict(design.excluded_policy_ids),
        "metric_columns": list(METRIC_COLUMNS),
        "common_random_numbers": (
            "Rows with the same seed use the existing run_scenario seed split "
            "for arrival and failure streams across compared policies."
        ),
        "disruption_sampling": (
            "Road p_fail/base_p_fail are reset to zero on a graph copy, then "
            "scenario-selected road edges are set to one before applying each "
            "scenario p_fail_scale."
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
        p_fail_scale=scenario.p_fail_scale if selected_edges else 0.0,
        selected_edges=selected_edges,
        rail_travel_time_multiplier=scenario.rail_travel_time_multiplier,
        rail_headway_multiplier=scenario.rail_headway_multiplier,
        rail_capacity_multiplier=scenario.rail_capacity_multiplier,
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
    if case.rail_travel_time_multiplier is not None or case.rail_headway_multiplier is not None or case.rail_capacity_multiplier is not None:
        network = run_config.setdefault("network", {})
        rail_links = network.get("rail_link")
        if rail_links and isinstance(rail_links, list) and len(rail_links) > 0:
            rail_link = rail_links[0]
            if not isinstance(rail_link, list) or len(rail_link) < 5:
                raise ValueError("rail_link[0] must be a list with at least 5 elements")
            if case.rail_travel_time_multiplier is not None:
                rail_link[2] = float(rail_link[2]) * case.rail_travel_time_multiplier
            if case.rail_headway_multiplier is not None:
                rail_link[3] = float(rail_link[3]) * case.rail_headway_multiplier
            if case.rail_capacity_multiplier is not None:
                rail_link[4] = max(1, round(float(rail_link[4]) * case.rail_capacity_multiplier))
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
        "disruption_mode": case.scenario_type,
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
        demand_profile_id=_required_text(
            raw.get("demand_profile_id", "pilot_default_demand"),
            f"{profile_id}.demand_profile_id",
        ),
        fleet_profile_id=_required_text(
            raw.get("fleet_profile_id", "pilot_default_fleet"),
            f"{profile_id}.fleet_profile_id",
        ),
        rail_service_profile_id=_required_text(
            raw.get("rail_service_profile_id", "pilot_fixed_headway_rail_proxy"),
            f"{profile_id}.rail_service_profile_id",
        ),
        validation_profile_id=_required_text(
            raw.get(
                "validation_profile_id",
                "pilot_graph_ready_and_plausibility_review",
            ),
            f"{profile_id}.validation_profile_id",
        ),
        road_network_profile_id=_required_text(
            raw.get("road_network_profile_id", "pilot_cached_osm_graph"),
            f"{profile_id}.road_network_profile_id",
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
        "output_lock_receipt": _display_path(
            directory / f"{output_prefix}_output_lock_receipt.json"
        ),
    }
    if include_legacy_sample_manifest:
        outputs["legacy_sample_manifest"] = _display_path(
            directory / "pilot_result_manifest.json"
        )
    return outputs


def apply_pilot_demand_fleet_profiles(
    config: Mapping[str, Any],
    *,
    demand_profile_id: str = "pilot_default_demand",
    fleet_profile_id: str = "pilot_default_fleet",
    demand_profiles_path: str | Path = DEFAULT_DEMAND_PROFILES_PATH,
    fleet_profiles_path: str | Path = DEFAULT_FLEET_PROFILES_PATH,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Apply Phase 5 demand/fleet profile CSV rows to a pilot config.

    This consumes bounded scenario-profile rows as runtime inputs. It does not
    calibrate demand, validate fleet availability, or implement no-show
    behavior.
    """

    updated = deepcopy(dict(config))
    demand_rows = _profile_rows_by_id(Path(demand_profiles_path), demand_profile_id)
    fleet_rows = _profile_rows_by_id(Path(fleet_profiles_path), fleet_profile_id)
    demand_row = _single_supported_demand_row(demand_rows, demand_profile_id)
    applied_fields: list[str] = []

    personnel = _mutable_section(updated, "personnel")
    personnel["total"] = _positive_int(demand_row.get("total_demand_pax"), "total_demand_pax")
    personnel["group_size"] = _positive_int(
        demand_row.get("boarding_batch_size_pax"),
        "boarding_batch_size_pax",
    )
    personnel["assembly_time"] = _non_negative_float(
        demand_row.get("assembly_time_min"),
        "assembly_time_min",
    )
    applied_fields.extend(
        [
            "personnel.total",
            "personnel.group_size",
            "personnel.assembly_time",
        ]
    )

    lateness = _mutable_section(updated, "lateness")
    lateness["distribution"] = _required_text(
        demand_row.get("arrival_distribution"),
        "arrival_distribution",
    )
    lateness["mu"] = _non_negative_float(demand_row.get("arrival_param_mu"), "arrival_param_mu")
    lateness["sigma_levels"] = _non_negative_float_list(
        demand_row.get("arrival_param_sigma"),
        "arrival_param_sigma",
    )
    applied_fields.extend(
        [
            "lateness.distribution",
            "lateness.mu",
            "lateness.sigma_levels",
        ]
    )

    for fleet_row in fleet_rows:
        applied_fields.extend(_apply_fleet_profile_row(updated, fleet_row))

    source_classes = sorted(
        {
            str(row.get("source_class", "")).strip()
            for row in [demand_row, *fleet_rows]
            if str(row.get("source_class", "")).strip()
        }
    )
    evidence_statuses = sorted(
        {
            str(row.get("evidence_status", "")).strip()
            for row in [demand_row, *fleet_rows]
            if str(row.get("evidence_status", "")).strip()
        }
    )
    metadata = {
        "schema_version": 1,
        "runtime_profile_inputs_consumed": True,
        "claim_boundary": (
            "Phase 5 profile CSV consumption only; not calibrated demand, "
            "not agency fleet validation, not no-show behavior, not "
            "publication readiness, and not final-study readiness."
        ),
        "demand_profile_id": demand_profile_id,
        "fleet_profile_id": fleet_profile_id,
        "demand_profiles_path": _display_path(demand_profiles_path),
        "demand_profiles_sha256": (
            _file_sha256(demand_profiles_path) if Path(demand_profiles_path).exists() else None
        ),
        "fleet_profiles_path": _display_path(fleet_profiles_path),
        "fleet_profiles_sha256": (
            _file_sha256(fleet_profiles_path) if Path(fleet_profiles_path).exists() else None
        ),
        "applied_field_count": len(applied_fields),
        "applied_fields": sorted(applied_fields),
        "demand_row_count": len(demand_rows),
        "fleet_row_count": len(fleet_rows),
        "source_classes": source_classes,
        "evidence_statuses": evidence_statuses,
        "can_support_parameter_evidence_gate": False,
        "can_support_acceptance_gate": False,
        "can_support_publication_gate": False,
        "can_support_final_study_gate": False,
        "remaining_blockers": [
            "profile rows are bounded scenario assumptions, not calibration evidence",
            "agency fleet roster and operating timetable evidence remain absent",
            "no-show and partial non-arrival semantics are still not implemented",
        ],
    }
    return updated, metadata


def _profile_rows_by_id(path: Path, profile_id: str) -> list[dict[str, str]]:
    """Return CSV rows for one profile ID, failing closed on missing inputs."""

    requested = _required_text(profile_id, "profile_id")
    if not path.exists():
        raise FileNotFoundError(f"profile CSV is missing: {_display_path(path)}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"{_display_path(path)} must have a CSV header")
        if "profile_id" not in reader.fieldnames:
            raise ValueError(f"{_display_path(path)} must contain profile_id")
        rows = [
            {key: str(value or "").strip() for key, value in row.items()}
            for row in reader
            if str(row.get("profile_id") or "").strip() == requested
        ]
    if not rows:
        raise ValueError(f"{_display_path(path)} has no rows for profile_id {requested!r}")
    return rows


def _single_supported_demand_row(
    rows: Sequence[Mapping[str, str]],
    profile_id: str,
) -> Mapping[str, str]:
    """Validate demand-profile semantics currently supported by run_scenario."""

    if len(rows) != 1:
        raise ValueError(
            f"demand profile {profile_id!r} must resolve to exactly one origin row"
        )
    row = rows[0]
    origin_share = _non_negative_float(row.get("origin_share"), "origin_share")
    if abs(origin_share - 1.0) > 1e-9:
        raise ValueError(
            "current pilot runner supports exactly one origin with origin_share=1.0"
        )
    for field in ("no_show_fraction", "late_arrival_fraction"):
        if _non_negative_float(row.get(field, "0"), field) != 0.0:
            raise ValueError(f"{field} is not implemented in the current runner")
    denominator = _required_text(
        row.get("completion_denominator"),
        "completion_denominator",
    )
    if denominator != "total_scenario_demand":
        raise ValueError(
            "completion_denominator must remain total_scenario_demand for current metrics"
        )
    return row


def _mutable_section(config: dict[str, Any], section: str) -> dict[str, Any]:
    """Return a mutable mapping section, creating an empty one if needed."""

    current = config.get(section)
    if current is None:
        config[section] = {}
    elif isinstance(current, Mapping):
        config[section] = dict(current)
    else:
        raise ValueError(f"config section {section!r} must be a mapping")
    return config[section]


def _non_negative_float(value: Any, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a non-negative number")
    text = str(value if value is not None else "").strip()
    if not text:
        raise ValueError(f"{name} must be a non-negative number")
    try:
        number = float(text)
    except ValueError as exc:
        raise ValueError(f"{name} must be a non-negative number") from exc
    if not math.isfinite(number) or number < 0.0:
        raise ValueError(f"{name} must be a non-negative number")
    return number


def _non_negative_float_list(value: Any, name: str) -> list[float]:
    text = str(value if value is not None else "").strip()
    if not text:
        raise ValueError(f"{name} must contain at least one non-negative number")
    normalized = text.replace("|", ";").replace(",", ";")
    numbers = [
        _non_negative_float(part, name)
        for part in normalized.split(";")
        if part.strip()
    ]
    if not numbers:
        raise ValueError(f"{name} must contain at least one non-negative number")
    return numbers


def _apply_fleet_profile_row(
    config: dict[str, Any],
    row: Mapping[str, str],
) -> list[str]:
    """Apply one finite-fleet profile row to the simulator config."""

    role = _required_text(row.get("role"), "role")
    capacity = _positive_int(row.get("vehicle_capacity_pax"), "vehicle_capacity_pax")
    fleet_size = _positive_int(row.get("fleet_size"), "fleet_size")
    dispatch_interval = _non_negative_float(
        row.get("dispatch_interval_min"),
        "dispatch_interval_min",
    )
    first_departure = _runtime_first_departure_min(
        row.get("first_departure_min"),
        "first_departure_min",
    )
    turnaround = _non_negative_float(row.get("turnaround_min"), "turnaround_min")
    personnel = _mutable_section(config, "personnel")
    group_size = _positive_int(personnel.get("group_size"), "personnel.group_size")

    if role == "direct_bus":
        if capacity != group_size:
            raise ValueError(
                "direct_bus vehicle_capacity_pax must match personnel.group_size "
                "until separate bus capacity is implemented"
            )
        bus = _mutable_section(config, "bus")
        bus["fleet_size"] = fleet_size
        bus["dispatch_interval_min"] = dispatch_interval
        bus["first_departure_min"] = first_departure
        bus["turnaround_min"] = turnaround
        return [
            "bus.fleet_size",
            "bus.dispatch_interval_min",
            "bus.first_departure_min",
            "bus.turnaround_min",
        ]

    if role == "feeder_shuttle":
        if capacity != group_size:
            raise ValueError(
                "feeder_shuttle vehicle_capacity_pax must match personnel.group_size "
                "until separate feeder capacity is implemented"
            )
        multimodal = _mutable_section(config, "multimodal")
        multimodal["shuttle_fleet_size"] = fleet_size
        multimodal["shuttle_dispatch_interval_min"] = dispatch_interval
        multimodal["shuttle_first_departure_min"] = first_departure
        multimodal["shuttle_turnaround_min"] = turnaround
        return [
            "multimodal.shuttle_fleet_size",
            "multimodal.shuttle_dispatch_interval_min",
            "multimodal.shuttle_first_departure_min",
            "multimodal.shuttle_turnaround_min",
        ]

    if role == "last_mile":
        multimodal = _mutable_section(config, "multimodal")
        multimodal["lastmile_fleet_size"] = fleet_size
        multimodal["lastmile_dispatch_interval_min"] = dispatch_interval
        multimodal["lastmile_first_departure_min"] = first_departure
        multimodal["lastmile_turnaround_min"] = turnaround
        multimodal["lastmile_vehicle_capacity"] = capacity
        return [
            "multimodal.lastmile_fleet_size",
            "multimodal.lastmile_dispatch_interval_min",
            "multimodal.lastmile_first_departure_min",
            "multimodal.lastmile_turnaround_min",
            "multimodal.lastmile_vehicle_capacity",
        ]

    raise ValueError(f"unsupported fleet profile role: {role!r}")


def _runtime_first_departure_min(value: Any, name: str) -> float:
    text = str(value if value is not None else "").strip()
    if text == "after_rail_arrival":
        raise ValueError(
            "after_rail_arrival first-departure semantics are review metadata only; "
            "runtime profile consumption requires an explicit minute value"
        )
    return _non_negative_float(text, name)


def _profile_run_sigma(config: Mapping[str, Any]) -> float:
    lateness = config.get("lateness", {})
    if not isinstance(lateness, Mapping):
        raise ValueError("config lateness section must be a mapping")
    sigma_levels = lateness.get("sigma_levels")
    if isinstance(sigma_levels, Sequence) and not isinstance(sigma_levels, (str, bytes)):
        if not sigma_levels:
            raise ValueError("lateness.sigma_levels must not be empty")
        return _non_negative_float(sigma_levels[0], "lateness.sigma_levels[0]")
    return _non_negative_float(lateness.get("sigma"), "lateness.sigma")


def _acquire_output_lock(
    output_dir: str | Path,
    output_prefix: str,
    started_at_utc: str,
) -> dict[str, Any]:
    """Create a small atomic lock file for one output prefix."""

    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    _validate_output_prefix(output_prefix)
    lock_path = directory / f"{output_prefix}.output.lock"
    receipt_path = directory / f"{output_prefix}_output_lock_receipt.json"
    payload = {
        "schema_version": 1,
        "lock_path": _display_path(lock_path),
        "receipt_path": _display_path(receipt_path),
        "output_prefix": output_prefix,
        "acquired": True,
        "acquired_at_utc": started_at_utc,
        "pid": os.getpid(),
        "lock_mechanism": "atomic_create_x_mode",
        "release_policy": "released_after_successful_output_write_or_exception",
    }
    try:
        with lock_path.open("x", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
    except FileExistsError as exc:
        raise RuntimeError(
            f"output lock already exists for {output_prefix}: {_display_path(lock_path)}"
        ) from exc
    payload["lock_file_sha256"] = _file_sha256(lock_path)
    return payload


def _release_output_lock(output_lock: Mapping[str, Any]) -> dict[str, Any]:
    """Release an output lock if it is still present and return release evidence."""

    lock_path = PROJECT_ROOT / str(output_lock.get("lock_path", ""))
    if not str(output_lock.get("lock_path", "")).strip():
        return {"released": False, "release_status": "missing_lock_path"}
    if not lock_path.exists():
        return {
            "released": False,
            "release_status": "already_absent",
            "released_at_utc": _utc_now(),
        }
    lock_path.unlink()
    return {
        "released": True,
        "release_status": "released",
        "released_at_utc": _utc_now(),
    }


def _write_output_lock_receipt(
    *,
    output_lock: Mapping[str, Any],
    release: Mapping[str, Any],
    manifest_path: Path,
    results_path: Path,
    summary_path: Path,
) -> Path:
    """Write retained evidence that the transient output lock was released."""

    receipt_value = str(output_lock.get("receipt_path", "")).strip()
    receipt_path = PROJECT_ROOT / receipt_value if receipt_value else (
        manifest_path.parent / "output_lock_receipt.json"
    )
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt = {
        "schema_version": 1,
        "output_lock": dict(output_lock),
        "release": dict(release),
        "outputs": {
            "manifest": _display_path(manifest_path),
            "results": _display_path(results_path),
            "summary": _display_path(summary_path),
            "manifest_sha256": _file_sha256(manifest_path),
            "results_sha256": _file_sha256(results_path),
            "summary_sha256": _file_sha256(summary_path),
        },
    }
    with receipt_path.open("w", encoding="utf-8") as handle:
        json.dump(receipt, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return receipt_path


def _finalize_manifest_after_output_write(
    *,
    manifest: Mapping[str, Any],
    output_lock_release: Mapping[str, Any],
    manifest_path: Path,
    results_path: Path,
    summary_path: Path,
) -> dict[str, Any]:
    """Rewrite the manifest with release evidence and non-self-referential inventory."""

    finalized = dict(manifest)
    finalized["output_lock_release"] = dict(output_lock_release)
    finalized["output_inventory"] = {
        "schema_version": 1,
        "manifest_self_hash_policy": (
            "Final manifest SHA256 is recorded in the separate output-lock "
            "receipt to avoid self-referential manifest hashing."
        ),
        "files": {
            "results": _file_inventory(results_path, csv_data_rows=True),
            "summary": _file_inventory(summary_path, csv_data_rows=True),
            "manifest": {
                "path": _display_path(manifest_path),
                "exists": manifest_path.exists(),
                "readable": manifest_path.exists(),
                "sha256": None,
                "sha256_record_location": "output_lock_receipt.outputs.manifest_sha256",
            },
        },
    }
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(finalized, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return finalized


def _file_inventory(path: str | Path, *, csv_data_rows: bool = False) -> dict[str, Any]:
    """Return existence, size, hash, and optional CSV row-count evidence."""

    file_path = Path(path)
    inventory: dict[str, Any] = {
        "path": _display_path(file_path),
        "exists": file_path.exists(),
        "readable": False,
        "byte_count": None,
        "sha256": None,
    }
    if not file_path.exists():
        if csv_data_rows:
            inventory["csv_data_row_count"] = None
        return inventory
    inventory["readable"] = True
    inventory["byte_count"] = file_path.stat().st_size
    inventory["sha256"] = _file_sha256(file_path)
    if csv_data_rows:
        inventory["csv_data_row_count"] = _csv_data_row_count(file_path)
    return inventory


def _csv_data_row_count(path: str | Path) -> int:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        rows = list(reader)
    if not rows:
        return 0
    return max(len(rows) - 1, 0)


def _runtime_metadata(
    *,
    started_at_utc: str,
    finished_at_utc: str,
    wall_time_seconds: float,
    memory_before: Mapping[str, Any],
    memory_after: Mapping[str, Any],
) -> dict[str, Any]:
    """Return Phase 8 runtime evidence for a serial pilot run."""

    return {
        "started_at_utc": started_at_utc,
        "finished_at_utc": finished_at_utc,
        "wall_time_seconds": round(float(wall_time_seconds), 6),
        "actual_worker_count": 1,
        "worker_count_control": "none_serial_current_runner",
        "cpu_simulation_engine": "SimPy/NetworkX via src.scenario.run_scenario",
        "gpu_used_for_simulation": False,
        "gpu_use_scope": "none_for_cpu_simulation",
        "memory_before": dict(memory_before),
        "memory_after": dict(memory_after),
    }


def _config_hash_summary(
    *,
    base_config: Mapping[str, Any],
    policies: Sequence[PolicyAlternative],
    cases: Sequence[PilotDisruptionCase],
) -> dict[str, Any]:
    """Return stable hashes for base and policy/scenario effective configs."""

    policy_hashes: dict[str, str] = {}
    case_hashes: dict[str, dict[str, Any]] = {}
    effective_hashes: dict[str, str] = {}
    policy_lookup = {policy.policy_id: policy for policy in policies}
    for policy in policies:
        variant = build_policy_config_variant(base_config, policy, policy_lookup)
        policy_hashes[policy.policy_id] = _json_sha256(variant.config)
        for case in cases:
            key = f"{policy.policy_id}::{case.scenario_id}"
            effective_hashes[key] = _json_sha256(
                _config_with_case_failure(variant.config, case)
            )
    for case in cases:
        case_hashes[case.scenario_id] = {
            "failure_mode": case.failure_mode,
            "capacity_factor": case.capacity_factor,
            "p_fail_scale": case.p_fail_scale,
            "selected_edge_count": len(case.selected_edges),
            "sha256": _json_sha256(
                {
                    "scenario_id": case.scenario_id,
                    "failure_mode": case.failure_mode,
                    "capacity_factor": case.capacity_factor,
                    "p_fail_scale": case.p_fail_scale,
                    "selected_realworld_edge_ids": case.selected_realworld_edge_ids,
                }
            ),
        }
    return {
        "schema_version": 1,
        "base_config_sha256": _json_sha256(base_config),
        "policy_config_sha256s": policy_hashes,
        "scenario_failure_config_sha256s": case_hashes,
        "effective_policy_scenario_config_sha256s": effective_hashes,
    }


def _json_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _memory_status_snapshot() -> dict[str, Any]:
    """Return Windows RAM evidence using only the standard library."""

    if os.name != "nt":
        return {
            "available": False,
            "method": "unsupported_non_windows_stdlib",
        }

    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    status = MEMORYSTATUSEX()
    status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        return {
            "available": False,
            "method": "GlobalMemoryStatusEx",
        }
    return {
        "available": True,
        "method": "GlobalMemoryStatusEx",
        "total_physical_bytes": int(status.ullTotalPhys),
        "available_physical_bytes": int(status.ullAvailPhys),
        "memory_load_percent": int(status.dwMemoryLoad),
    }


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


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


def _executed_command(
    *,
    profile: PilotExperimentProfile,
    output_dir: str | Path,
    design_path: str | Path,
    region_path: str | Path,
    cache_path: str | Path,
    scenarios_path: str | Path,
    policies_path: str | Path,
    rail_source_decision_manifest_path: str | Path,
    artifact_invalidation_manifest_path: str | Path,
    artifact_invalidation_closeout_manifest_path: str | Path,
    closeout_action_queue_path: str | Path,
    road_class_overrides_path: str | Path | None,
    policy_ids: Sequence[str],
    scenario_ids: Sequence[str],
    seeds: Sequence[int],
    engineering_only: bool,
    closeout_regeneration_scope: str,
    design_overrides: Mapping[str, bool],
) -> str:
    """Return a reproducible command string for the executed profile and overrides."""

    parts = [_profile_command(profile)]
    if Path(output_dir) != DEFAULT_OUTPUT_DIR:
        parts.extend(["--output-dir", _quote_arg(_display_path(output_dir))])
    if Path(region_path) != DEFAULT_REGION_PATH:
        parts.extend(["--region-path", _quote_arg(_display_path(region_path))])
    if Path(cache_path) != DEFAULT_CACHE_PATH:
        parts.extend(["--cache-path", _quote_arg(_display_path(cache_path))])
    if Path(scenarios_path) != DEFAULT_SCENARIO_PATH:
        parts.extend(["--scenarios-path", _quote_arg(_display_path(scenarios_path))])
    if Path(policies_path) != DEFAULT_POLICY_ALTERNATIVES_PATH:
        parts.extend(["--policies-path", _quote_arg(_display_path(policies_path))])
    if Path(design_path) != DEFAULT_DESIGN_PATH:
        parts.extend(["--design-path", _quote_arg(_display_path(design_path))])
    if Path(rail_source_decision_manifest_path) != DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH:
        parts.extend(
            [
                "--rail-source-decision-manifest-path",
                _quote_arg(_display_path(rail_source_decision_manifest_path)),
            ]
        )
    if Path(artifact_invalidation_manifest_path) != DEFAULT_ARTIFACT_INVALIDATION_MANIFEST_PATH:
        parts.extend(
            [
                "--artifact-invalidation-manifest-path",
                _quote_arg(_display_path(artifact_invalidation_manifest_path)),
            ]
        )
    if (
        Path(artifact_invalidation_closeout_manifest_path)
        != DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_MANIFEST_PATH
    ):
        parts.extend(
            [
                "--artifact-invalidation-closeout-manifest-path",
                _quote_arg(_display_path(artifact_invalidation_closeout_manifest_path)),
            ]
        )
    if Path(closeout_action_queue_path) != DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_QUEUE:
        parts.extend(
            [
                "--closeout-action-queue-path",
                _quote_arg(_display_path(closeout_action_queue_path)),
            ]
        )
    if road_class_overrides_path is not None:
        parts.extend(
            ["--road-class-overrides-path", _quote_arg(_display_path(road_class_overrides_path))]
        )
    if design_overrides.get("seeds"):
        parts.extend(["--seeds", _quote_arg(",".join(str(seed) for seed in seeds))])
    if design_overrides.get("policy_ids"):
        parts.extend(["--policy-ids", _quote_arg(",".join(policy_ids))])
    if design_overrides.get("scenario_ids"):
        parts.extend(["--scenario-ids", _quote_arg(",".join(scenario_ids))])
    if engineering_only:
        parts.append("--engineering-only")
    if closeout_regeneration_scope:
        parts.extend(["--closeout-regeneration-scope", closeout_regeneration_scope])
    return " ".join(parts)


def _quote_arg(value: str) -> str:
    if not value or any(character.isspace() for character in value):
        escaped = value.replace('"', '\\"')
        return f'"{escaped}"'
    return value


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
    "DEFAULT_DEMAND_PROFILES_PATH",
    "DEFAULT_DESIGN_PATH",
    "DEFAULT_FLEET_PROFILES_PATH",
    "DEFAULT_FULL_PROFILE_ID",
    "DEFAULT_FULL_GRAPH_PROFILE_ID",
    "DEFAULT_MANIFEST_PATH",
    "DEFAULT_MULTI_CORRIDOR_FULL_PROFILE_ID",
    "DEFAULT_MULTI_CORRIDOR_PROFILE_ID",
    "DEFAULT_OUTPUT_DIR",
    "DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH",
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
    "ENGINEERING_ONLY_CLAIM_SCOPE",
    "PilotDisruptionCase",
    "PilotExperimentDesign",
    "PilotExperimentProfile",
    "PilotExperimentPreflightError",
    "PilotInputs",
    "PILOT_FULL_CLAIM_SCOPE",
    "PILOT_MULTI_CORRIDOR_CANDIDATE_CLAIM_SCOPE",
    "PILOT_MULTI_CORRIDOR_FULL_CANDIDATE_CLAIM_SCOPE",
    "PILOT_STAGED_CLAIM_SCOPE",
    "RESULT_COLUMNS",
    "RUN_STAGES",
    "SUMMARY_COLUMNS",
    "apply_pilot_demand_fleet_profiles",
    "build_result_manifest",
    "assert_pilot_experiment_preflight",
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
