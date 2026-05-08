"""Pilot scaffold sensitivity screening helpers.

This module provides a SALib-compatible problem frame and a deterministic
one-at-a-time screening fallback. The default runner is intentionally offline
and uses the cached pilot scaffold path; outputs are screening artifacts, not
calibrated sensitivity indices or operational forecasts.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import math
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import networkx as nx

from src import scenario as scenario_module
from src.policies import StrictPolicy
from src.realworld.disruption_scenarios import DEFAULT_SCENARIO_PATH, load_disruption_scenarios
from src.realworld.pilot_experiments import (
    DEFAULT_CACHE_PATH,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_REGION_PATH,
    PilotDisruptionCase,
    PilotInputs,
    load_pilot_inputs,
    make_pilot_base_config,
    select_disruption_cases,
)
from src.realworld.policy_alternatives import (
    DEFAULT_POLICY_ALTERNATIVES_PATH,
    PolicyAlternative,
    build_policy_config_variant,
    load_policy_alternatives,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DESIGN_PATH = PROJECT_ROOT / "data" / "scenarios" / "sensitivity_design.csv"
DEFAULT_RESULTS_PATH = DEFAULT_OUTPUT_DIR / "sensitivity_results.csv"
DEFAULT_SUMMARY_PATH = DEFAULT_OUTPUT_DIR / "sensitivity_summary.csv"
DEFAULT_MANIFEST_PATH = DEFAULT_OUTPUT_DIR / "sensitivity_manifest.json"
DEFAULT_MORRIS_RESULTS_PATH = DEFAULT_OUTPUT_DIR / "morris_results.csv"
DEFAULT_MORRIS_SUMMARY_PATH = DEFAULT_OUTPUT_DIR / "morris_summary.csv"
DEFAULT_MORRIS_MANIFEST_PATH = DEFAULT_OUTPUT_DIR / "morris_manifest.json"

METHOD_DETERMINISTIC = "deterministic_oat_screening"
METHOD_MORRIS = "salib_morris"
CLAIM_SCOPE = (
    "Pilot scaffold sensitivity screening only; not calibrated real-world "
    "sensitivity indices or an operational forecast."
)
MORRIS_CLAIM_SCOPE = (
    "Pilot scaffold SALib Morris sensitivity output; not calibrated real-world "
    "sensitivity evidence or an operational forecast."
)
DEFAULT_SENSITIVITY_SEED = 2201
DEFAULT_SAMPLE_POLICY_IDS = ("bus_only", "baseline_multimodal")
DEFAULT_SAMPLE_SCENARIO_IDS = (
    "songpa_random_capacity_reduction",
    "songpa_last_mile_station_to_destination",
)

REQUIRED_PARAMETER_IDS = frozenset(
    {
        "passenger_volume",
        "passenger_arrival_variability",
        "direct_bus_fleet_size",
        "feeder_fleet_size",
        "last_mile_fleet_size",
        "dispatch_interval",
        "road_background_traffic_multiplier",
        "capacity_reduction_factor",
        "rail_headway",
        "rail_capacity",
        "transfer_fixed_delay",
        "transfer_per_passenger_delay",
        "turnaround_time",
        "last_mile_access_disruption_probability",
    }
)
DESIGN_COLUMNS = (
    "parameter_id",
    "salib_name",
    "target",
    "value_type",
    "unit",
    "baseline",
    "low",
    "high",
    "applies_to",
    "scenario_filter",
    "source_parameter",
    "source_class",
    "notes",
)
VALUE_TYPES = frozenset({"float", "int"})
APPLIES_TO_VALUES = frozenset({"all", "bus_only", "multimodal"})
SCENARIO_FILTER_VALUES = frozenset(
    {
        "all",
        "capacity_reduction",
        "random",
        "last_mile",
        "critical_link",
        "no_disruption",
    }
)
SCREENING_LEVELS = ("low", "high")
RANK_METRICS = (
    "completion_rate",
    "censored_count",
    "penalized_makespan",
    "p80_arrival_time",
    "p95_arrival_time",
    "total_service_minutes",
    "passengers_per_total_service_minute",
)
RESULT_COLUMNS = (
    "region_id",
    "graph_source",
    "method",
    "parameter_id",
    "salib_name",
    "level",
    "parameter_value",
    "baseline_value",
    "low_value",
    "high_value",
    "unit",
    "applies_to",
    "scenario_filter",
    "policy_id",
    "scenario_id",
    "scenario_family",
    "scenario_type",
    "seed",
    "mode",
    "completion_rate",
    "censored_count",
    "penalized_makespan",
    "p80_arrival_time",
    "p95_arrival_time",
    "total_service_minutes",
    "passengers_per_total_service_minute",
    "delta_completion_rate",
    "abs_delta_completion_rate",
    "delta_censored_count",
    "abs_delta_censored_count",
    "delta_penalized_makespan",
    "abs_delta_penalized_makespan",
    "delta_p80_arrival_time",
    "abs_delta_p80_arrival_time",
    "delta_p95_arrival_time",
    "abs_delta_p95_arrival_time",
    "delta_total_service_minutes",
    "abs_delta_total_service_minutes",
    "delta_passengers_per_total_service_minute",
    "abs_delta_passengers_per_total_service_minute",
    "selected_edge_count",
    "selected_edge_probability",
    "notes",
    "claim_scope",
)
SUMMARY_COLUMNS = (
    "metric",
    "rank",
    "parameter_id",
    "salib_name",
    "method",
    "max_abs_delta",
    "mean_abs_delta",
    "max_abs_delta_level",
    "max_abs_delta_policy_id",
    "max_abs_delta_scenario_id",
    "baseline_value",
    "low_value",
    "high_value",
    "unit",
    "applies_to",
    "scenario_filter",
    "run_count",
    "claim_scope",
)
MORRIS_RESULT_COLUMNS = (
    "region_id",
    "graph_source",
    "method",
    "sample_index",
    "policy_id",
    "scenario_id",
    "scenario_family",
    "scenario_type",
    "seed",
    "mode",
    "completion_rate",
    "censored_count",
    "penalized_makespan",
    "p80_arrival_time",
    "p95_arrival_time",
    "total_service_minutes",
    "passengers_per_total_service_minute",
    "selected_edge_count",
    "selected_edge_probability",
    "parameter_values_json",
    "claim_scope",
)
MORRIS_SUMMARY_COLUMNS = (
    "metric",
    "policy_id",
    "scenario_id",
    "rank",
    "parameter_id",
    "salib_name",
    "method",
    "mu",
    "mu_star",
    "sigma",
    "mu_star_conf",
    "index_status",
    "index_issue_reason",
    "sample_count",
    "num_trajectories",
    "num_levels",
    "claim_scope",
)
BASELINE_PARAMETER_ID = "__baseline__"


@dataclass(frozen=True)
class SensitivityParameter:
    """One row in the sensitivity design table."""

    parameter_id: str
    salib_name: str
    target: str
    value_type: str
    unit: str
    baseline: float
    low: float
    high: float
    applies_to: str
    scenario_filter: str
    source_parameter: str
    source_class: str
    notes: str = ""

    def value_for_level(self, level: str) -> float | int:
        """Return a typed value for ``baseline``, ``low``, or ``high``."""

        if level == "baseline":
            value = self.baseline
        elif level == "low":
            value = self.low
        elif level == "high":
            value = self.high
        else:
            raise ValueError(f"unknown sensitivity level: {level!r}")

        if self.value_type == "int":
            return int(round(value))
        return float(value)

    @property
    def salib_bounds(self) -> list[float]:
        """Return bounds in the structure expected by SALib problem dicts."""

        return [float(self.low), float(self.high)]


def load_sensitivity_design(
    path: str | Path = DEFAULT_DESIGN_PATH,
    *,
    parameter_ids: Sequence[str] | None = None,
) -> tuple[SensitivityParameter, ...]:
    """Load and validate the sensitivity design CSV."""

    filepath = Path(path)
    with filepath.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        _validate_design_header(reader.fieldnames, filepath)
        parameters = tuple(
            _parameter_from_row(row, row_number)
            for row_number, row in enumerate(reader, start=2)
            if _row_has_content(row)
        )

    validate_sensitivity_design(parameters)
    if parameter_ids is None:
        return parameters

    by_id = {parameter.parameter_id: parameter for parameter in parameters}
    missing = [parameter_id for parameter_id in parameter_ids if parameter_id not in by_id]
    if missing:
        raise KeyError(f"unknown sensitivity parameter_id values: {missing}")
    return tuple(by_id[parameter_id] for parameter_id in parameter_ids)


def validate_sensitivity_design(parameters: Sequence[SensitivityParameter]) -> None:
    """Validate parameter identity, values, and required Workstream 9 coverage."""

    if not parameters:
        raise ValueError("sensitivity design must contain at least one parameter")

    seen: set[str] = set()
    salib_names: set[str] = set()
    for index, parameter in enumerate(parameters, start=1):
        _validate_parameter(parameter, line_label=f"row {index}")
        if parameter.parameter_id in seen:
            raise ValueError(f"duplicate parameter_id: {parameter.parameter_id!r}")
        if parameter.salib_name in salib_names:
            raise ValueError(f"duplicate salib_name: {parameter.salib_name!r}")
        seen.add(parameter.parameter_id)
        salib_names.add(parameter.salib_name)

    missing = sorted(REQUIRED_PARAMETER_IDS - seen)
    if missing:
        raise ValueError(f"missing required sensitivity parameters: {missing}")


def salib_problem(parameters: Sequence[SensitivityParameter]) -> dict[str, Any]:
    """Return a SALib-compatible problem dictionary."""

    return {
        "num_vars": len(parameters),
        "names": [parameter.salib_name for parameter in parameters],
        "bounds": [parameter.salib_bounds for parameter in parameters],
    }


def run_sensitivity_screening(
    *,
    region_path: str | Path = DEFAULT_REGION_PATH,
    cache_path: str | Path = DEFAULT_CACHE_PATH,
    scenarios_path: str | Path = DEFAULT_SCENARIO_PATH,
    policies_path: str | Path = DEFAULT_POLICY_ALTERNATIVES_PATH,
    design_path: str | Path = DEFAULT_DESIGN_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    seed: int = DEFAULT_SENSITIVITY_SEED,
    sample: bool = True,
    policy_ids: Sequence[str] | None = None,
    scenario_ids: Sequence[str] | None = None,
    parameter_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Run deterministic OAT screening and write result CSVs plus manifest."""

    method = METHOD_DETERMINISTIC
    inputs = load_pilot_inputs(region_path=region_path, cache_path=cache_path)
    baseline_parameters = load_sensitivity_design(design_path)
    parameters = _filter_parameters(baseline_parameters, parameter_ids)
    policies = _select_policies(policies_path, policy_ids=policy_ids, sample=sample)
    cases = _select_cases(
        inputs=inputs,
        scenarios_path=scenarios_path,
        scenario_ids=scenario_ids,
        sample=sample,
    )

    rows = run_sensitivity_rows(
        inputs=inputs,
        parameters=parameters,
        baseline_parameters=baseline_parameters,
        policies=policies,
        cases=cases,
        seed=int(seed),
        method=method,
    )
    summary_rows = summarize_sensitivity_rows(rows, parameters=parameters, method=method)

    paths = write_sensitivity_outputs(
        rows=rows,
        summary_rows=summary_rows,
        output_dir=output_dir,
        manifest=build_sensitivity_manifest(
            inputs=inputs,
            parameters=parameters,
            policies=policies,
            cases=cases,
            rows=rows,
            summary_rows=summary_rows,
            seed=int(seed),
            method=method,
            region_path=region_path,
            cache_path=cache_path,
            scenarios_path=scenarios_path,
            policies_path=policies_path,
            design_path=design_path,
            sample=sample,
        ),
    )
    return {
        "rows": rows,
        "summary_rows": summary_rows,
        "manifest": paths["manifest"],
        "results_path": paths["results"],
        "summary_path": paths["summary"],
        "manifest_path": paths["manifest_path"],
    }


def run_morris_sensitivity(
    *,
    region_path: str | Path = DEFAULT_REGION_PATH,
    cache_path: str | Path = DEFAULT_CACHE_PATH,
    scenarios_path: str | Path = DEFAULT_SCENARIO_PATH,
    policies_path: str | Path = DEFAULT_POLICY_ALTERNATIVES_PATH,
    design_path: str | Path = DEFAULT_DESIGN_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    seed: int = DEFAULT_SENSITIVITY_SEED,
    sample: bool = True,
    policy_ids: Sequence[str] | None = None,
    scenario_ids: Sequence[str] | None = None,
    parameter_ids: Sequence[str] | None = None,
    num_trajectories: int = 4,
    num_levels: int = 4,
) -> dict[str, Any]:
    """Run SALib Morris screening and write formal sensitivity artifacts."""

    _require_salib()
    _validate_morris_controls(num_trajectories=num_trajectories, num_levels=num_levels)
    inputs = load_pilot_inputs(region_path=region_path, cache_path=cache_path)
    baseline_parameters = load_sensitivity_design(design_path)
    parameters = _filter_parameters(baseline_parameters, parameter_ids)
    policies = _select_policies(policies_path, policy_ids=policy_ids, sample=sample)
    cases = _select_cases(
        inputs=inputs,
        scenarios_path=scenarios_path,
        scenario_ids=scenario_ids,
        sample=sample,
    )
    sample_matrix = _morris_sample_matrix(
        parameters,
        num_trajectories=num_trajectories,
        num_levels=num_levels,
        seed=int(seed),
    )
    rows = run_morris_rows(
        inputs=inputs,
        parameters=parameters,
        baseline_parameters=baseline_parameters,
        policies=policies,
        cases=cases,
        sample_matrix=sample_matrix,
        seed=int(seed),
    )
    summary_rows = summarize_morris_rows(
        rows,
        parameters=parameters,
        sample_matrix=sample_matrix,
        num_trajectories=num_trajectories,
        num_levels=num_levels,
        seed=int(seed),
    )
    paths = write_morris_outputs(
        rows=rows,
        summary_rows=summary_rows,
        output_dir=output_dir,
        manifest=build_morris_manifest(
            inputs=inputs,
            parameters=parameters,
            policies=policies,
            cases=cases,
            rows=rows,
            summary_rows=summary_rows,
            seed=int(seed),
            sample_matrix=sample_matrix,
            num_trajectories=num_trajectories,
            num_levels=num_levels,
            region_path=region_path,
            cache_path=cache_path,
            scenarios_path=scenarios_path,
            policies_path=policies_path,
            design_path=design_path,
            sample=sample,
        ),
    )
    return {
        "rows": rows,
        "summary_rows": summary_rows,
        "manifest": paths["manifest"],
        "results_path": paths["results"],
        "summary_path": paths["summary"],
        "manifest_path": paths["manifest_path"],
    }


def run_morris_rows(
    *,
    inputs: PilotInputs,
    parameters: Sequence[SensitivityParameter],
    baseline_parameters: Sequence[SensitivityParameter],
    policies: Sequence[PolicyAlternative],
    cases: Sequence[PilotDisruptionCase],
    sample_matrix: Any,
    seed: int,
) -> list[dict[str, Any]]:
    """Evaluate every Morris sample point for the selected policies and cases."""

    baseline_values = {
        parameter.parameter_id: parameter.value_for_level("baseline")
        for parameter in baseline_parameters
    }
    base_config = make_pilot_base_config(inputs.region)
    rows: list[dict[str, Any]] = []
    for sample_index, sample_values in enumerate(sample_matrix):
        values = dict(baseline_values)
        for parameter, raw_value in zip(parameters, sample_values):
            values[parameter.parameter_id] = _typed_sample_value(parameter, raw_value)

        sampled_values = {
            parameter.parameter_id: values[parameter.parameter_id]
            for parameter in parameters
        }
        for policy in policies:
            for case in cases:
                metrics, edge_probability = _evaluate_point(
                    inputs=inputs,
                    base_config=base_config,
                    policies=policies,
                    policy=policy,
                    case=case,
                    values=values,
                    seed=seed,
                )
                rows.append(
                    _morris_result_row(
                        inputs=inputs,
                        sample_index=sample_index,
                        policy=policy,
                        case=case,
                        seed=seed,
                        metrics=metrics,
                        selected_edge_probability=edge_probability,
                        sampled_values=sampled_values,
                    )
                )
    return rows


def summarize_morris_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    parameters: Sequence[SensitivityParameter],
    sample_matrix: Any,
    num_trajectories: int,
    num_levels: int,
    seed: int,
) -> list[dict[str, Any]]:
    """Analyze Morris elementary effects for each metric-policy-scenario group."""

    _require_salib()
    from SALib.analyze import morris as morris_analyze
    import numpy as np

    problem = salib_problem(parameters)
    grouped: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["policy_id"]), str(row["scenario_id"]))].append(row)

    summary_rows: list[dict[str, Any]] = []
    sample_count = len(sample_matrix)
    for (policy_id, scenario_id), group_rows in sorted(grouped.items()):
        ordered_rows = sorted(group_rows, key=lambda row: int(row["sample_index"]))
        if len(ordered_rows) != sample_count:
            raise ValueError(
                f"Morris group {policy_id}/{scenario_id} has {len(ordered_rows)} rows; "
                f"expected {sample_count}"
            )
        for metric in RANK_METRICS:
            outputs = np.array([float(row[metric]) for row in ordered_rows], dtype=float)
            nonfinite_output_count = int(np.count_nonzero(~np.isfinite(outputs)))
            if nonfinite_output_count:
                analysis = None
                index_status = "unavailable_nonfinite_metric_outputs"
                index_issue_reason = (
                    f"{nonfinite_output_count}/{sample_count} metric outputs "
                    "were non-finite before Morris analysis"
                )
            else:
                analysis = morris_analyze.analyze(
                    problem,
                    sample_matrix,
                    outputs,
                    num_levels=num_levels,
                    print_to_console=False,
                    seed=seed,
                )
                index_status = "available"
                index_issue_reason = ""
            metric_rows = _morris_metric_rows(
                metric=metric,
                policy_id=policy_id,
                scenario_id=scenario_id,
                parameters=parameters,
                analysis=analysis,
                index_status=index_status,
                index_issue_reason=index_issue_reason,
                sample_count=sample_count,
                num_trajectories=num_trajectories,
                num_levels=num_levels,
            )
            summary_rows.extend(metric_rows)
    return summary_rows


def write_morris_outputs(
    *,
    rows: Sequence[Mapping[str, Any]],
    summary_rows: Sequence[Mapping[str, Any]],
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    manifest: Mapping[str, Any],
) -> dict[str, Any]:
    """Write Morris result CSVs and manifest."""

    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    results_path = directory / "morris_results.csv"
    summary_path = directory / "morris_summary.csv"
    manifest_path = directory / "morris_manifest.json"

    _write_csv(results_path, MORRIS_RESULT_COLUMNS, rows)
    _write_csv(summary_path, MORRIS_SUMMARY_COLUMNS, summary_rows)
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(dict(manifest), handle, indent=2, sort_keys=True)
        handle.write("\n")

    return {
        "results": results_path,
        "summary": summary_path,
        "manifest_path": manifest_path,
        "manifest": dict(manifest),
    }


def build_morris_manifest(
    *,
    inputs: PilotInputs,
    parameters: Sequence[SensitivityParameter],
    policies: Sequence[PolicyAlternative],
    cases: Sequence[PilotDisruptionCase],
    rows: Sequence[Mapping[str, Any]],
    summary_rows: Sequence[Mapping[str, Any]],
    seed: int,
    sample_matrix: Any,
    num_trajectories: int,
    num_levels: int,
    region_path: str | Path,
    cache_path: str | Path,
    scenarios_path: str | Path,
    policies_path: str | Path,
    design_path: str | Path,
    sample: bool,
) -> dict[str, Any]:
    """Return reproducibility metadata for SALib Morris outputs."""

    graph_scale = _graph_scale_metadata(
        inputs,
        strategy=(
            "route_corridor_reduced_for_sensitivity_scaffold_execution"
            if bool(inputs.graph.graph.get("experiment_subgraph", False))
            else "full_graph_sensitivity_scaffold_execution"
        ),
    )
    index_status_counts = _counts(row.get("index_status", "") for row in summary_rows)
    return {
        "schema_version": 1,
        "morris_summary_schema_version": 2,
        "result_scope": MORRIS_CLAIM_SCOPE,
        "command": "scripts/run_sensitivity.py --method morris --sample"
        if sample
        else "scripts/run_sensitivity.py --method morris --all",
        "method": METHOD_MORRIS,
        "salib_available": _salib_available(),
        "salib_problem": salib_problem(parameters),
        "morris_sample_count": len(sample_matrix),
        "num_trajectories": int(num_trajectories),
        "num_levels": int(num_levels),
        "region_id": inputs.region_id,
        "graph_source": inputs.graph_source,
        "graph_nodes": inputs.graph.number_of_nodes(),
        "graph_edges": inputs.graph.number_of_edges(),
        "source_graph_nodes": inputs.source_graph_nodes,
        "source_graph_edges": inputs.source_graph_edges,
        "analysis_graph_reduced": bool(inputs.graph.graph.get("experiment_subgraph", False)),
        "analysis_graph_strategy": graph_scale["analysis"]["strategy"],
        "graph_scale": graph_scale,
        "inputs": {
            "region_path": _display_path(region_path),
            "cache_path": _display_path(cache_path),
            "disruption_scenarios_path": _display_path(scenarios_path),
            "policy_alternatives_path": _display_path(policies_path),
            "sensitivity_design_path": _display_path(design_path),
        },
        "policy_ids": [policy.policy_id for policy in policies],
        "scenario_ids": [case.scenario_id for case in cases],
        "parameter_ids": [parameter.parameter_id for parameter in parameters],
        "seed": int(seed),
        "row_count": len(rows),
        "summary_row_count": len(summary_rows),
        "index_status_counts": index_status_counts,
        "unavailable_index_row_count": sum(
            count
            for status, count in index_status_counts.items()
            if str(status).startswith("unavailable_")
        ),
        "rank_metrics": list(RANK_METRICS),
        "claim_boundary": (
            "Morris indices are computed for the current pilot scaffold design "
            "and reduced analysis graph. They are not calibrated real-world "
            "sensitivity evidence."
        ),
    }


def run_sensitivity_rows(
    *,
    inputs: PilotInputs,
    parameters: Sequence[SensitivityParameter],
    baseline_parameters: Sequence[SensitivityParameter] | None = None,
    policies: Sequence[PolicyAlternative],
    cases: Sequence[PilotDisruptionCase],
    seed: int,
    method: str = METHOD_DETERMINISTIC,
) -> list[dict[str, Any]]:
    """Execute baseline rows and one-at-a-time low/high perturbation rows."""

    baseline_parameters = tuple(baseline_parameters or parameters)
    baseline_values = {
        parameter.parameter_id: parameter.value_for_level("baseline")
        for parameter in baseline_parameters
    }
    base_config = make_pilot_base_config(inputs.region)
    rows: list[dict[str, Any]] = []
    baseline_metrics: dict[tuple[str, str], Mapping[str, Any]] = {}

    for policy in policies:
        for case in cases:
            metrics, edge_probability = _evaluate_point(
                inputs=inputs,
                base_config=base_config,
                policies=policies,
                policy=policy,
                case=case,
                values=baseline_values,
                seed=seed,
            )
            baseline_metrics[(policy.policy_id, case.scenario_id)] = metrics
            rows.append(
                _result_row(
                    inputs=inputs,
                    method=method,
                    parameter=None,
                    level="baseline",
                    value="",
                    policy=policy,
                    case=case,
                    seed=seed,
                    metrics=metrics,
                    baseline_metrics=metrics,
                    selected_edge_probability=edge_probability,
                )
            )

    for parameter in parameters:
        for level in SCREENING_LEVELS:
            values = dict(baseline_values)
            values[parameter.parameter_id] = parameter.value_for_level(level)
            for policy in policies:
                if not _parameter_applies_to_policy(parameter, policy):
                    continue
                for case in cases:
                    if not _parameter_applies_to_case(parameter, case):
                        continue

                    metrics, edge_probability = _evaluate_point(
                        inputs=inputs,
                        base_config=base_config,
                        policies=policies,
                        policy=policy,
                        case=case,
                        values=values,
                        seed=seed,
                    )
                    baseline = baseline_metrics[(policy.policy_id, case.scenario_id)]
                    rows.append(
                        _result_row(
                            inputs=inputs,
                            method=method,
                            parameter=parameter,
                            level=level,
                            value=values[parameter.parameter_id],
                            policy=policy,
                            case=case,
                            seed=seed,
                            metrics=metrics,
                            baseline_metrics=baseline,
                            selected_edge_probability=edge_probability,
                        )
                    )
    return rows


def summarize_sensitivity_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    parameters: Sequence[SensitivityParameter],
    method: str = METHOD_DETERMINISTIC,
) -> list[dict[str, Any]]:
    """Rank parameters by absolute low/high change for each screening metric."""

    parameter_map = {parameter.parameter_id: parameter for parameter in parameters}
    perturbation_rows = [
        row for row in rows if row.get("parameter_id") in parameter_map
    ]
    grouped: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for row in perturbation_rows:
        for metric in RANK_METRICS:
            grouped[(metric, str(row["parameter_id"]))].append(row)

    summary_rows: list[dict[str, Any]] = []
    for metric in RANK_METRICS:
        metric_rows: list[dict[str, Any]] = []
        for parameter in parameters:
            group_rows = grouped.get((metric, parameter.parameter_id), [])
            delta_column = f"abs_delta_{metric}"
            if group_rows:
                abs_values = [float(row[delta_column]) for row in group_rows]
                max_index = max(
                    range(len(group_rows)),
                    key=lambda index: (abs_values[index], str(group_rows[index]["level"])),
                )
                max_row = group_rows[max_index]
                max_abs_delta = abs_values[max_index]
                mean_abs_delta = _mean(abs_values)
                max_level = str(max_row["level"])
                max_policy_id = str(max_row["policy_id"])
                max_scenario_id = str(max_row["scenario_id"])
            else:
                max_abs_delta = 0.0
                mean_abs_delta = 0.0
                max_level = ""
                max_policy_id = ""
                max_scenario_id = ""

            metric_rows.append(
                {
                    "metric": metric,
                    "rank": 0,
                    "parameter_id": parameter.parameter_id,
                    "salib_name": parameter.salib_name,
                    "method": method,
                    "max_abs_delta": _round_metric(max_abs_delta, metric),
                    "mean_abs_delta": _round_metric(mean_abs_delta, metric),
                    "max_abs_delta_level": max_level,
                    "max_abs_delta_policy_id": max_policy_id,
                    "max_abs_delta_scenario_id": max_scenario_id,
                    "baseline_value": _format_value(parameter.value_for_level("baseline")),
                    "low_value": _format_value(parameter.value_for_level("low")),
                    "high_value": _format_value(parameter.value_for_level("high")),
                    "unit": parameter.unit,
                    "applies_to": parameter.applies_to,
                    "scenario_filter": parameter.scenario_filter,
                    "run_count": len(group_rows),
                    "claim_scope": CLAIM_SCOPE,
                }
            )

        metric_rows.sort(
            key=lambda row: (-float(row["max_abs_delta"]), str(row["parameter_id"]))
        )
        for rank, row in enumerate(metric_rows, start=1):
            row["rank"] = rank
            summary_rows.append(row)

    return summary_rows


def write_sensitivity_outputs(
    *,
    rows: Sequence[Mapping[str, Any]],
    summary_rows: Sequence[Mapping[str, Any]],
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    manifest: Mapping[str, Any],
) -> dict[str, Any]:
    """Write sensitivity result CSVs and manifest."""

    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    results_path = directory / "sensitivity_results.csv"
    summary_path = directory / "sensitivity_summary.csv"
    manifest_path = directory / "sensitivity_manifest.json"

    _write_csv(results_path, RESULT_COLUMNS, rows)
    _write_csv(summary_path, SUMMARY_COLUMNS, summary_rows)
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(dict(manifest), handle, indent=2, sort_keys=True)
        handle.write("\n")

    return {
        "results": results_path,
        "summary": summary_path,
        "manifest_path": manifest_path,
        "manifest": dict(manifest),
    }


def build_sensitivity_manifest(
    *,
    inputs: PilotInputs,
    parameters: Sequence[SensitivityParameter],
    policies: Sequence[PolicyAlternative],
    cases: Sequence[PilotDisruptionCase],
    rows: Sequence[Mapping[str, Any]],
    summary_rows: Sequence[Mapping[str, Any]],
    seed: int,
    method: str,
    region_path: str | Path,
    cache_path: str | Path,
    scenarios_path: str | Path,
    policies_path: str | Path,
    design_path: str | Path,
    sample: bool,
) -> dict[str, Any]:
    """Return reproducibility metadata for sensitivity screening outputs."""

    graph_scale = _graph_scale_metadata(
        inputs,
        strategy=(
            "route_corridor_reduced_for_sensitivity_scaffold_execution"
            if bool(inputs.graph.graph.get("experiment_subgraph", False))
            else "full_graph_sensitivity_scaffold_execution"
        ),
    )
    return {
        "schema_version": 1,
        "result_scope": CLAIM_SCOPE,
        "command": "scripts/run_sensitivity.py --sample" if sample else "scripts/run_sensitivity.py --all",
        "method": method,
        "salib_available": _salib_available(),
        "salib_problem": salib_problem(parameters),
        "salib_note": (
            "The design is compatible with SALib problem dictionaries, but the "
            "default offline run uses deterministic one-at-a-time screening."
        ),
        "region_id": inputs.region_id,
        "graph_source": inputs.graph_source,
        "graph_nodes": inputs.graph.number_of_nodes(),
        "graph_edges": inputs.graph.number_of_edges(),
        "source_graph_nodes": inputs.source_graph_nodes,
        "source_graph_edges": inputs.source_graph_edges,
        "analysis_graph_reduced": bool(inputs.graph.graph.get("experiment_subgraph", False)),
        "analysis_graph_strategy": graph_scale["analysis"]["strategy"],
        "graph_scale": graph_scale,
        "inputs": {
            "region_path": _display_path(region_path),
            "cache_path": _display_path(cache_path),
            "disruption_scenarios_path": _display_path(scenarios_path),
            "policy_alternatives_path": _display_path(policies_path),
            "sensitivity_design_path": _display_path(design_path),
        },
        "policy_ids": [policy.policy_id for policy in policies],
        "scenario_ids": [case.scenario_id for case in cases],
        "parameter_ids": [parameter.parameter_id for parameter in parameters],
        "seed": int(seed),
        "row_count": len(rows),
        "summary_row_count": len(summary_rows),
        "rank_metrics": list(RANK_METRICS),
        "screening_design": (
            "Each parameter is evaluated at one low and one high value around "
            "the sensitivity-design baseline while other parameters stay fixed."
        ),
    }


def _graph_scale_metadata(
    inputs: PilotInputs,
    *,
    strategy: str,
) -> dict[str, Any]:
    """Return source-vs-analysis graph scale metadata for result manifests."""

    reduced = bool(inputs.graph.graph.get("experiment_subgraph", False))
    return {
        "source": {
            "nodes": int(inputs.source_graph_nodes),
            "edges": int(inputs.source_graph_edges),
        },
        "analysis": {
            "nodes": int(inputs.graph.number_of_nodes()),
            "edges": int(inputs.graph.number_of_edges()),
            "reduced": reduced,
            "strategy": strategy,
        },
    }


def graph_with_selected_edge_probability(
    graph: nx.DiGraph,
    case: PilotDisruptionCase,
    *,
    selected_edge_probability: float,
) -> nx.DiGraph:
    """Copy a graph and assign one probability to selected disruption edges."""

    probability = _finite_float(selected_edge_probability, "selected_edge_probability")
    if probability < 0.0 or probability > 1.0:
        raise ValueError("selected_edge_probability must satisfy 0 <= p <= 1")

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
            data["p_fail"] = probability
            data["base_p_fail"] = probability
    return prepared


def _evaluate_point(
    *,
    inputs: PilotInputs,
    base_config: Mapping[str, Any],
    policies: Sequence[PolicyAlternative],
    policy: PolicyAlternative,
    case: PilotDisruptionCase,
    values: Mapping[str, float | int],
    seed: int,
) -> tuple[Mapping[str, Any], float]:
    run_params: dict[str, Any] = {
        "s": 1.0,
        "p_fail_scale": case.p_fail_scale,
        "sigma": 0.25,
    }
    variant = build_policy_config_variant(base_config, policy, policies)
    run_config = _config_with_case_failure(variant.config, case)
    edge_probability = _apply_sensitivity_values(run_config, run_params, case, values)
    graph = graph_with_selected_edge_probability(
        inputs.graph,
        case,
        selected_edge_probability=edge_probability,
    )
    metrics = scenario_module.run_scenario(
        G=graph,
        config=run_config,
        scenario_type=variant.scenario_type,
        policy=StrictPolicy(),
        params=run_params,
        seed=int(seed),
    )
    return metrics, edge_probability


def _apply_sensitivity_values(
    config: dict[str, Any],
    params: dict[str, Any],
    case: PilotDisruptionCase,
    values: Mapping[str, float | int],
) -> float:
    config["personnel"]["total"] = _int_value(values, "passenger_volume")
    params["sigma"] = _float_value(values, "passenger_arrival_variability")

    config["bus"]["fleet_size"] = _int_value(values, "direct_bus_fleet_size")
    config["bus"]["dispatch_interval_min"] = _float_value(values, "dispatch_interval")
    config["bus"]["turnaround_min"] = _float_value(values, "turnaround_time")

    multimodal = config["multimodal"]
    multimodal["shuttle_fleet_size"] = _int_value(values, "feeder_fleet_size")
    multimodal["lastmile_fleet_size"] = _int_value(values, "last_mile_fleet_size")
    multimodal["shuttle_dispatch_interval_min"] = _float_value(values, "dispatch_interval")
    multimodal["lastmile_dispatch_interval_min"] = _float_value(values, "dispatch_interval")
    multimodal["shuttle_turnaround_min"] = _float_value(values, "turnaround_time")
    multimodal["lastmile_turnaround_min"] = _float_value(values, "turnaround_time")
    multimodal["transfer_time_min"] = _float_value(values, "transfer_fixed_delay")
    multimodal["transfer_per_passenger_min"] = _float_value(
        values,
        "transfer_per_passenger_delay",
    )

    background_volume = float(config["traffic"]["background_volume"])
    config["traffic"]["background_volume"] = background_volume * _float_value(
        values,
        "road_background_traffic_multiplier",
    )

    config["failure"]["capacity_reduction_factor"] = _float_value(
        values,
        "capacity_reduction_factor",
    )

    rail_link = list(config["network"]["rail_link"][0])
    rail_link[3] = _float_value(values, "rail_headway")
    rail_link[4] = _int_value(values, "rail_capacity")
    config["network"]["rail_link"] = [rail_link]

    if case.scenario_family == "last_mile":
        return _float_value(values, "last_mile_access_disruption_probability")
    return 1.0 if case.selected_edges else 0.0


def _config_with_case_failure(
    config: Mapping[str, Any],
    case: PilotDisruptionCase,
) -> dict[str, Any]:
    run_config = json.loads(json.dumps(config))
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
    method: str,
    parameter: SensitivityParameter | None,
    level: str,
    value: float | int | str,
    policy: PolicyAlternative,
    case: PilotDisruptionCase,
    seed: int,
    metrics: Mapping[str, Any],
    baseline_metrics: Mapping[str, Any],
    selected_edge_probability: float,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "region_id": inputs.region_id,
        "graph_source": inputs.graph_source,
        "method": method,
        "parameter_id": BASELINE_PARAMETER_ID if parameter is None else parameter.parameter_id,
        "salib_name": "" if parameter is None else parameter.salib_name,
        "level": level,
        "parameter_value": value,
        "baseline_value": "" if parameter is None else _format_value(parameter.value_for_level("baseline")),
        "low_value": "" if parameter is None else _format_value(parameter.value_for_level("low")),
        "high_value": "" if parameter is None else _format_value(parameter.value_for_level("high")),
        "unit": "" if parameter is None else parameter.unit,
        "applies_to": "all" if parameter is None else parameter.applies_to,
        "scenario_filter": "all" if parameter is None else parameter.scenario_filter,
        "policy_id": policy.policy_id,
        "scenario_id": case.scenario_id,
        "scenario_family": case.scenario_family,
        "scenario_type": case.scenario_type,
        "seed": int(seed),
        "mode": policy.scenario_type,
        "selected_edge_count": len(case.selected_edges),
        "selected_edge_probability": round(selected_edge_probability, 4),
        "notes": _row_notes(parameter, policy, case),
        "claim_scope": CLAIM_SCOPE,
    }

    for metric in RANK_METRICS:
        precision = _metric_precision(metric)
        metric_value = _metric_number(metrics, metric)
        baseline_value = _metric_number(baseline_metrics, metric)
        delta = metric_value - baseline_value
        row[metric] = _round_with_precision(metric_value, precision)
        row[f"delta_{metric}"] = _round_with_precision(delta, precision)
        row[f"abs_delta_{metric}"] = _round_with_precision(abs(delta), precision)

    row["censored_count"] = int(metrics["censored_count"])
    row["delta_censored_count"] = int(row["delta_censored_count"])
    row["abs_delta_censored_count"] = int(row["abs_delta_censored_count"])
    return row


def _morris_sample_matrix(
    parameters: Sequence[SensitivityParameter],
    *,
    num_trajectories: int,
    num_levels: int,
    seed: int,
) -> Any:
    _require_salib()
    from SALib.sample import morris as morris_sample

    return morris_sample.sample(
        salib_problem(parameters),
        N=int(num_trajectories),
        num_levels=int(num_levels),
        seed=int(seed),
    )


def _morris_result_row(
    *,
    inputs: PilotInputs,
    sample_index: int,
    policy: PolicyAlternative,
    case: PilotDisruptionCase,
    seed: int,
    metrics: Mapping[str, Any],
    selected_edge_probability: float,
    sampled_values: Mapping[str, float | int],
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "region_id": inputs.region_id,
        "graph_source": inputs.graph_source,
        "method": METHOD_MORRIS,
        "sample_index": int(sample_index),
        "policy_id": policy.policy_id,
        "scenario_id": case.scenario_id,
        "scenario_family": case.scenario_family,
        "scenario_type": case.scenario_type,
        "seed": int(seed),
        "mode": policy.scenario_type,
        "selected_edge_count": len(case.selected_edges),
        "selected_edge_probability": round(selected_edge_probability, 4),
        "parameter_values_json": json.dumps(
            dict(sorted(sampled_values.items())),
            sort_keys=True,
            separators=(",", ":"),
        ),
        "claim_scope": MORRIS_CLAIM_SCOPE,
    }
    for metric in RANK_METRICS:
        row[metric] = _round_with_precision(
            _metric_number(metrics, metric),
            _metric_precision(metric),
        )
    row["censored_count"] = int(metrics["censored_count"])
    return row


def _morris_metric_rows(
    *,
    metric: str,
    policy_id: str,
    scenario_id: str,
    parameters: Sequence[SensitivityParameter],
    analysis: Mapping[str, Any] | None,
    index_status: str,
    index_issue_reason: str,
    sample_count: int,
    num_trajectories: int,
    num_levels: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, parameter in enumerate(parameters):
        rows.append(
            {
                "metric": metric,
                "policy_id": policy_id,
                "scenario_id": scenario_id,
                "rank": 0,
                "parameter_id": parameter.parameter_id,
                "salib_name": parameter.salib_name,
                "method": METHOD_MORRIS,
                "mu": _analysis_number(analysis, "mu", index),
                "mu_star": _analysis_number(analysis, "mu_star", index),
                "sigma": _analysis_number(analysis, "sigma", index),
                "mu_star_conf": _analysis_number(analysis, "mu_star_conf", index),
                "index_status": index_status,
                "index_issue_reason": index_issue_reason,
                "sample_count": int(sample_count),
                "num_trajectories": int(num_trajectories),
                "num_levels": int(num_levels),
                "claim_scope": MORRIS_CLAIM_SCOPE,
            }
        )

    rows.sort(
        key=lambda row: (
            -_sort_value(row["mu_star"]),
            str(row["parameter_id"]),
        )
    )
    for rank, row in enumerate(rows, start=1):
        row["rank"] = rank
    return rows


def _typed_sample_value(parameter: SensitivityParameter, value: Any) -> float | int:
    number = _finite_float(value, f"Morris sample value for {parameter.parameter_id}")
    if parameter.value_type == "int":
        return max(0, int(round(number)))
    return float(number)


def _analysis_number(
    analysis: Mapping[str, Any] | None,
    key: str,
    index: int,
) -> float | str:
    if analysis is None:
        return ""
    values = analysis.get(key)
    if values is None:
        return ""
    try:
        value = float(values[index])
    except (TypeError, ValueError, IndexError):
        return ""
    if not math.isfinite(value):
        return ""
    return round(value, 6)


def _sort_value(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return float("-inf")
    if not math.isfinite(number):
        return float("-inf")
    return number


def _require_salib() -> None:
    if not _salib_available():
        raise RuntimeError(
            "SALib is required for method='morris'. Install requirements.txt "
            "or run deterministic_oat_screening instead."
        )


def _validate_morris_controls(*, num_trajectories: int, num_levels: int) -> None:
    if int(num_trajectories) < 1:
        raise ValueError("num_trajectories must be at least 1")
    if int(num_levels) < 2:
        raise ValueError("num_levels must be at least 2")
    if int(num_levels) % 2:
        raise ValueError("num_levels must be even for Morris sampling")


def _select_policies(
    policies_path: str | Path,
    *,
    policy_ids: Sequence[str] | None,
    sample: bool,
) -> tuple[PolicyAlternative, ...]:
    alternatives = load_policy_alternatives(policies_path)
    selected_ids = tuple(policy_ids) if policy_ids is not None else (
        DEFAULT_SAMPLE_POLICY_IDS if sample else ()
    )
    if not selected_ids:
        return tuple(alternatives)

    by_id = {alternative.policy_id: alternative for alternative in alternatives}
    missing = [policy_id for policy_id in selected_ids if policy_id not in by_id]
    if missing:
        raise KeyError(f"unknown policy_id values: {missing}")
    return tuple(by_id[policy_id] for policy_id in selected_ids)


def _select_cases(
    *,
    inputs: PilotInputs,
    scenarios_path: str | Path,
    scenario_ids: Sequence[str] | None,
    sample: bool,
) -> tuple[PilotDisruptionCase, ...]:
    scenarios = load_disruption_scenarios(scenarios_path, region_id=inputs.region_id)
    selected_ids = tuple(scenario_ids) if scenario_ids is not None else (
        DEFAULT_SAMPLE_SCENARIO_IDS if sample else ()
    )
    return select_disruption_cases(
        inputs.graph,
        scenarios,
        scenario_ids=selected_ids or None,
        sample=False,
    )


def _filter_parameters(
    parameters: Sequence[SensitivityParameter],
    parameter_ids: Sequence[str] | None,
) -> tuple[SensitivityParameter, ...]:
    if parameter_ids is None:
        return tuple(parameters)

    by_id = {parameter.parameter_id: parameter for parameter in parameters}
    missing = [parameter_id for parameter_id in parameter_ids if parameter_id not in by_id]
    if missing:
        raise KeyError(f"unknown sensitivity parameter_id values: {missing}")
    return tuple(by_id[parameter_id] for parameter_id in parameter_ids)


def _parameter_applies_to_policy(
    parameter: SensitivityParameter,
    policy: PolicyAlternative,
) -> bool:
    return parameter.applies_to == "all" or parameter.applies_to == policy.scenario_type


def _parameter_applies_to_case(
    parameter: SensitivityParameter,
    case: PilotDisruptionCase,
) -> bool:
    if parameter.scenario_filter == "all":
        return True
    if parameter.scenario_filter == "capacity_reduction":
        return case.scenario_type == "capacity_reduction"
    if parameter.scenario_filter == "no_disruption":
        return case.scenario_family == "no_disruption"
    return parameter.scenario_filter == case.scenario_family


def _parameter_from_row(
    row: Mapping[str | None, str | None],
    row_number: int,
) -> SensitivityParameter:
    if None in row:
        raise ValueError(f"row {row_number} has extra CSV values without headers")
    stripped = {str(key): str(value or "").strip() for key, value in row.items()}
    parameter = SensitivityParameter(
        parameter_id=stripped["parameter_id"],
        salib_name=stripped["salib_name"],
        target=stripped["target"],
        value_type=stripped["value_type"],
        unit=stripped["unit"],
        baseline=_finite_float(stripped["baseline"], f"row {row_number} baseline"),
        low=_finite_float(stripped["low"], f"row {row_number} low"),
        high=_finite_float(stripped["high"], f"row {row_number} high"),
        applies_to=stripped["applies_to"],
        scenario_filter=stripped["scenario_filter"],
        source_parameter=stripped["source_parameter"],
        source_class=stripped["source_class"],
        notes=stripped["notes"],
    )
    _validate_parameter(parameter, line_label=f"row {row_number}")
    return parameter


def _validate_parameter(parameter: SensitivityParameter, *, line_label: str) -> None:
    _validate_identifier(parameter.parameter_id, f"{line_label}: parameter_id")
    _validate_identifier(parameter.salib_name, f"{line_label}: salib_name")
    for field, value in (
        ("target", parameter.target),
        ("unit", parameter.unit),
        ("source_parameter", parameter.source_parameter),
        ("source_class", parameter.source_class),
    ):
        if not str(value).strip():
            raise ValueError(f"{line_label}: {field} is required")
    if parameter.value_type not in VALUE_TYPES:
        raise ValueError(f"{line_label}: value_type must be one of {sorted(VALUE_TYPES)}")
    if parameter.applies_to not in APPLIES_TO_VALUES:
        raise ValueError(f"{line_label}: applies_to must be one of {sorted(APPLIES_TO_VALUES)}")
    if parameter.scenario_filter not in SCENARIO_FILTER_VALUES:
        raise ValueError(
            f"{line_label}: scenario_filter must be one of {sorted(SCENARIO_FILTER_VALUES)}"
        )
    if parameter.low > parameter.baseline or parameter.baseline > parameter.high:
        raise ValueError(f"{line_label}: baseline must satisfy low <= baseline <= high")
    if parameter.low == parameter.high:
        raise ValueError(f"{line_label}: low and high must differ")
    if parameter.value_type == "int":
        for field, value in (
            ("baseline", parameter.baseline),
            ("low", parameter.low),
            ("high", parameter.high),
        ):
            if not float(value).is_integer():
                raise ValueError(f"{line_label}: {field} must be an integer")
            if value < 0:
                raise ValueError(f"{line_label}: {field} must be non-negative")
    if parameter.parameter_id == "last_mile_access_disruption_probability":
        if parameter.low < 0.0 or parameter.high > 1.0:
            raise ValueError(
                f"{line_label}: disruption probability bounds must stay within [0, 1]"
            )


def _validate_design_header(fieldnames: Sequence[str] | None, filepath: Path) -> None:
    if fieldnames is None:
        raise ValueError(f"{filepath} has no CSV header")
    actual = tuple(fieldnames)
    missing = [column for column in DESIGN_COLUMNS if column not in actual]
    extra = [column for column in actual if column not in DESIGN_COLUMNS]
    if missing or extra:
        raise ValueError(
            f"{filepath} has invalid sensitivity schema; missing={missing}, extra={extra}"
        )


def _validate_identifier(value: str, label: str) -> None:
    if not value:
        raise ValueError(f"{label} is required")
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789_")
    if any(character not in allowed for character in value):
        raise ValueError(f"{label} must use lowercase letters, digits, and underscores")


def _row_has_content(row: Mapping[str | None, str | None]) -> bool:
    return any((value or "").strip() for key, value in row.items() if key is not None)


def _finite_float(value: Any, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite number")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a finite number") from exc
    if not math.isfinite(number):
        raise ValueError(f"{name} must be a finite number")
    return number


def _int_value(values: Mapping[str, float | int], parameter_id: str) -> int:
    return max(0, int(round(float(values[parameter_id]))))


def _float_value(values: Mapping[str, float | int], parameter_id: str) -> float:
    return float(values[parameter_id])


def _metric_number(metrics: Mapping[str, Any], metric: str) -> float:
    return float(metrics[metric])


def _round_metric(value: float, metric: str) -> float:
    return _round_with_precision(value, _metric_precision(metric))


def _metric_precision(metric: str) -> int:
    if metric in {"completion_rate", "passengers_per_total_service_minute"}:
        return 4
    if metric == "censored_count":
        return 0
    return 2


def _round_with_precision(value: float, precision: int) -> float | int:
    if not math.isfinite(value):
        return value
    if precision == 0:
        return int(round(value))
    return round(value, precision)


def _mean(values: Iterable[float]) -> float:
    values_tuple = tuple(values)
    if not values_tuple:
        return 0.0
    return sum(values_tuple) / len(values_tuple)


def _counts(values: Iterable[object]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value).strip()
        if not key:
            continue
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _format_value(value: float | int) -> str:
    if isinstance(value, int):
        return str(value)
    if float(value).is_integer():
        return str(int(value))
    return f"{float(value):.6g}"


def _row_notes(
    parameter: SensitivityParameter | None,
    policy: PolicyAlternative,
    case: PilotDisruptionCase,
) -> str:
    if parameter is None:
        return f"baseline sensitivity-design values | policy={policy.policy_id} | scenario={case.scenario_id}"
    return (
        f"parameter={parameter.notes} | policy={policy.policy_id} | "
        f"scenario={case.notes or case.scenario_id}"
    )


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


def _display_path(path: str | Path) -> str:
    filepath = Path(path)
    try:
        return filepath.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return filepath.as_posix()


def _salib_available() -> bool:
    return importlib.util.find_spec("SALib") is not None


__all__ = [
    "BASELINE_PARAMETER_ID",
    "CLAIM_SCOPE",
    "DEFAULT_DESIGN_PATH",
    "DEFAULT_MANIFEST_PATH",
    "DEFAULT_MORRIS_MANIFEST_PATH",
    "DEFAULT_MORRIS_RESULTS_PATH",
    "DEFAULT_MORRIS_SUMMARY_PATH",
    "DEFAULT_RESULTS_PATH",
    "DEFAULT_SAMPLE_POLICY_IDS",
    "DEFAULT_SAMPLE_SCENARIO_IDS",
    "DEFAULT_SENSITIVITY_SEED",
    "DEFAULT_SUMMARY_PATH",
    "DESIGN_COLUMNS",
    "METHOD_DETERMINISTIC",
    "METHOD_MORRIS",
    "MORRIS_CLAIM_SCOPE",
    "MORRIS_RESULT_COLUMNS",
    "MORRIS_SUMMARY_COLUMNS",
    "RANK_METRICS",
    "REQUIRED_PARAMETER_IDS",
    "RESULT_COLUMNS",
    "SUMMARY_COLUMNS",
    "SensitivityParameter",
    "build_morris_manifest",
    "build_sensitivity_manifest",
    "graph_with_selected_edge_probability",
    "load_sensitivity_design",
    "run_morris_rows",
    "run_morris_sensitivity",
    "run_sensitivity_rows",
    "run_sensitivity_screening",
    "salib_problem",
    "summarize_morris_rows",
    "summarize_sensitivity_rows",
    "validate_sensitivity_design",
    "write_morris_outputs",
    "write_sensitivity_outputs",
]
