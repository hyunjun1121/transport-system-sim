"""Pre-compact feasibility and benchmark-threshold review tables.

These helpers prepare Phase 8 compact-experiment guardrails. They do not
approve policies, calibrate validation benchmarks, or close acceptance gates.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import yaml

from src.realworld.policy_alternatives import (
    PolicyAlternative,
    build_policy_config_variant,
    load_policy_alternatives,
)
from src.realworld.pilot_experiments import make_pilot_base_config


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY_ALTERNATIVES_PATH = (
    PROJECT_ROOT / "data" / "scenarios" / "policy_alternatives.csv"
)
DEFAULT_PILOT_DESIGN_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "pilot_experiment_design.json"
)
DEFAULT_REGION_PATH = PROJECT_ROOT / "data" / "regions" / "pilot_region.yaml"
DEFAULT_FALLBACK_BENCHMARK_PATH = (
    PROJECT_ROOT / "data" / "validation" / "external_route_benchmarks.csv"
)
DEFAULT_OSRM_BENCHMARK_PATH = (
    PROJECT_ROOT / "data" / "validation" / "external_route_benchmarks_osrm.csv"
)
DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "osrm_route_benchmark_manifest.json"
)
DEFAULT_POLICY_FEASIBILITY_TABLE_PATH = (
    PROJECT_ROOT / "data" / "validation" / "policy_feasibility_fairness_table.csv"
)
DEFAULT_POLICY_FEASIBILITY_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "policy_feasibility_fairness_manifest.json"
)
DEFAULT_POLICY_FEASIBILITY_DOC_PATH = (
    PROJECT_ROOT / "docs" / "policy_feasibility_fairness_table.md"
)
DEFAULT_BENCHMARK_THRESHOLD_TABLE_PATH = (
    PROJECT_ROOT / "data" / "validation" / "benchmark_threshold_table.csv"
)
DEFAULT_BENCHMARK_THRESHOLD_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "benchmark_threshold_manifest.json"
)
DEFAULT_BENCHMARK_THRESHOLD_DOC_PATH = (
    PROJECT_ROOT / "docs" / "benchmark_threshold_table.md"
)

PHASE8_PRECOMPACT_SCOPE = (
    "Phase 8 pre-compact review table only; not policy acceptance, not "
    "validation acceptance, not calibrated real-world evidence, not final-study "
    "approval, and not operational routing or dispatch guidance."
)

POLICY_FEASIBILITY_COLUMNS: tuple[str, ...] = (
    "policy_id",
    "scenario_type",
    "profile_inclusion",
    "excluded_reason",
    "same_mode_baseline_policy_id",
    "comparison_role",
    "vehicle_budget_status",
    "bus_fleet_size",
    "shuttle_fleet_size",
    "lastmile_fleet_size",
    "road_vehicle_capacity_pax",
    "rail_capacity_pax_per_train",
    "rail_headway_min",
    "rail_travel_time_min",
    "vehicle_delta_vs_baseline",
    "service_minute_budget_status",
    "road_vehicle_service_min_budget",
    "train_service_min_budget",
    "total_service_min_budget",
    "route_leg_ids",
    "road_route_check_ids",
    "graph_variant_dependency",
    "corridor_overlap_class",
    "access_leg_count",
    "egress_leg_count",
    "transfer_delay_location",
    "fixed_transfer_min",
    "per_passenger_transfer_min",
    "egress_transfer_model",
    "rerouting_authority_class",
    "routing_adaptation_implemented",
    "dispatch_adaptation_implemented",
    "adaptive_label_status",
    "feasibility_status",
    "fairness_status",
    "blocking_reason",
    "required_reviewer_action",
    "evidence_input_paths",
    "can_support_publication_or_acceptance",
    "formal_acceptance_evidence",
    "claim_boundary",
)

BENCHMARK_THRESHOLD_COLUMNS: tuple[str, ...] = (
    "threshold_id",
    "schema_version",
    "profile_scope",
    "benchmark_family",
    "metric",
    "unit",
    "comparison_basis",
    "comparison_formula",
    "pass_rule",
    "warn_rule",
    "fail_rule",
    "source_requirement",
    "required_source_classes",
    "disallowed_source_classes",
    "applies_to_artifacts",
    "current_source_classification",
    "predeclared_before_compact",
    "post_hoc_change_policy",
    "claim_boundary_on_pass",
    "claim_boundary_on_warn",
    "claim_boundary_on_fail",
    "compact_claim_effect",
    "can_support_compact_promotion",
    "can_support_validation_gate",
    "claim_boundary",
)


def build_policy_feasibility_rows(
    *,
    policy_path: str | Path = DEFAULT_POLICY_ALTERNATIVES_PATH,
    design_path: str | Path = DEFAULT_PILOT_DESIGN_PATH,
    region_path: str | Path = DEFAULT_REGION_PATH,
) -> list[dict[str, str]]:
    """Return one pre-compact feasibility/fairness row per policy."""

    policies = load_policy_alternatives(policy_path)
    design = _read_json_object(design_path)
    profiles_by_policy = _profiles_by_policy(design)
    base_config = make_pilot_base_config(_read_yaml_object(region_path))
    evidence_paths = "; ".join(
        _display_path(Path(path)) for path in (policy_path, design_path, region_path)
    )
    rows: list[dict[str, str]] = []
    for policy in policies:
        rows.append(
            _policy_feasibility_row(
                policy,
                policies,
                base_config,
                profiles_by_policy,
                evidence_paths,
            )
        )
    return rows


def build_benchmark_threshold_rows(
    *,
    fallback_benchmark_path: str | Path = DEFAULT_FALLBACK_BENCHMARK_PATH,
    osrm_benchmark_path: str | Path = DEFAULT_OSRM_BENCHMARK_PATH,
    osrm_manifest_path: str | Path = DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH,
) -> list[dict[str, str]]:
    """Return predeclared benchmark threshold rows for compact experiments."""

    source_summary = _benchmark_source_summary(
        fallback_benchmark_path=fallback_benchmark_path,
        osrm_benchmark_path=osrm_benchmark_path,
        osrm_manifest_path=osrm_manifest_path,
    )
    current_source_classification = (
        f"fallback_source_classes={_format_counts(source_summary['fallback_source_classes'])}; "
        f"osrm_source_classes={_format_counts(source_summary['osrm_source_classes'])}; "
        f"osrm_raw_response_files={source_summary['osrm_raw_response_file_count']}; "
        f"osrm_unpinned_rows={source_summary['osrm_unpinned_row_count']}"
    )
    evidence_paths = "; ".join(
        _display_path(Path(path))
        for path in (fallback_benchmark_path, osrm_benchmark_path, osrm_manifest_path)
    )

    def row(
        *,
        threshold_id: str,
        benchmark_family: str,
        metric: str,
        unit: str,
        comparison_basis: str,
        comparison_formula: str,
        pass_rule: str,
        warn_rule: str,
        fail_rule: str,
        source_requirement: str,
        required_source_classes: str,
        disallowed_source_classes: str,
        claim_boundary_on_pass: str,
        claim_boundary_on_warn: str,
        claim_boundary_on_fail: str,
        compact_claim_effect: str,
        can_support_compact_promotion: str = "false",
    ) -> dict[str, str]:
        return {
            "threshold_id": threshold_id,
            "schema_version": "1",
            "profile_scope": "Phase 8 compact engineering profile before full-run promotion",
            "benchmark_family": benchmark_family,
            "metric": metric,
            "unit": unit,
            "comparison_basis": comparison_basis,
            "comparison_formula": comparison_formula,
            "pass_rule": pass_rule,
            "warn_rule": warn_rule,
            "fail_rule": fail_rule,
            "source_requirement": source_requirement,
            "required_source_classes": required_source_classes,
            "disallowed_source_classes": disallowed_source_classes,
            "applies_to_artifacts": evidence_paths,
            "current_source_classification": current_source_classification,
            "predeclared_before_compact": "true",
            "post_hoc_change_policy": (
                "Any threshold revision after compact outputs are generated must "
                "be recorded as post hoc and the affected result remains exploratory."
            ),
            "claim_boundary_on_pass": claim_boundary_on_pass,
            "claim_boundary_on_warn": claim_boundary_on_warn,
            "claim_boundary_on_fail": claim_boundary_on_fail,
            "compact_claim_effect": compact_claim_effect,
            "can_support_compact_promotion": can_support_compact_promotion,
            "can_support_validation_gate": "false",
            "claim_boundary": PHASE8_PRECOMPACT_SCOPE,
        }

    return [
        row(
            threshold_id="road_route_duration_difference",
            benchmark_family="road_route",
            metric="duration_percent_difference",
            unit="percent",
            comparison_basis="simulator free-flow duration versus cached route benchmark",
            comparison_formula="abs(simulator_free_flow_time_min - benchmark_duration_min) / benchmark_duration_min",
            pass_rule="pass when absolute difference is <= 20 percent",
            warn_rule="warn when absolute difference is > 20 and <= 40 percent",
            fail_rule=(
                "fail when absolute difference is > 40 percent unless a "
                "source-backed explanation is recorded"
            ),
            source_requirement=(
                "cached raw route payload or documented executable fallback; live "
                "unretained calls cannot support validation wording"
            ),
            required_source_classes=(
                "cached_external_router_snapshot; documented_executable_fallback"
            ),
            disallowed_source_classes="live_unpinned_router_response; missing_raw_payload",
            claim_boundary_on_pass=(
                "road-route plausibility comparator only; not ground truth or calibration"
            ),
            claim_boundary_on_warn=(
                "engineering-only route plausibility warning; keep compact output exploratory"
            ),
            claim_boundary_on_fail=(
                "block calibrated travel-time wording and compact-to-full promotion"
            ),
            compact_claim_effect=(
                "failed duration thresholds keep compact/full results exploratory "
                "and block calibrated travel-time wording"
            ),
            can_support_compact_promotion="true_only_if_all_required_road_rows_pass",
        ),
        row(
            threshold_id="road_route_distance_difference",
            benchmark_family="road_route",
            metric="distance_percent_difference",
            unit="percent",
            comparison_basis="simulator route distance versus cached route benchmark",
            comparison_formula="abs(simulator_distance_m - benchmark_distance_m) / benchmark_distance_m",
            pass_rule="pass when absolute difference is <= 10 percent",
            warn_rule="warn when absolute difference is > 10 and <= 25 percent",
            fail_rule="fail when absolute difference is > 25 percent",
            source_requirement=(
                "cached raw route payload or documented executable fallback with "
                "query/config metadata"
            ),
            required_source_classes=(
                "cached_external_router_snapshot; documented_executable_fallback"
            ),
            disallowed_source_classes="live_unpinned_router_response; missing_raw_payload",
            claim_boundary_on_pass=(
                "road-route plausibility comparator only; not ground truth or calibration"
            ),
            claim_boundary_on_warn=(
                "engineering-only route-distance warning; graph-scale interpretation remains bounded"
            ),
            claim_boundary_on_fail=(
                "block graph-scale plausibility wording until route source is reviewed or rerun"
            ),
            compact_claim_effect=(
                "failed distance thresholds keep graph-scale and route-plausibility "
                "claims exploratory"
            ),
            can_support_compact_promotion="true_only_if_all_required_road_rows_pass",
        ),
        row(
            threshold_id="rail_transit_travel_time_difference",
            benchmark_family="rail_or_transit",
            metric="travel_time_delta_or_percent_difference",
            unit="minutes_or_percent",
            comparison_basis="simulator rail/transit time versus reviewed timetable/GTFS/R5 benchmark",
            comparison_formula="abs(simulated_minutes - benchmark_minutes) <= max(minutes_band, percent_band * benchmark_minutes)",
            pass_rule="pass within the larger of 10 minutes or 15 percent",
            warn_rule="warn within the larger of 20 minutes or 30 percent",
            fail_rule="fail outside the warn band",
            source_requirement=(
                "reviewed timetable, GTFS plus validator report, shortest-path "
                "cache, or R5/OpenTripPlanner snapshot"
            ),
            required_source_classes=(
                "reviewed_timetable_cache; reviewed_gtfs_validator_snapshot; "
                "reviewed_shortest_path_cache; reviewed_r5_or_otp_snapshot"
            ),
            disallowed_source_classes="documented_assumption_proxy; missing_gtfs; missing_timetable_payload",
            claim_boundary_on_pass=(
                "rail/transit timing plausibility only; still not operational service availability"
            ),
            claim_boundary_on_warn=(
                "engineering-only rail/transit timing warning; no calibrated rail advantage wording"
            ),
            claim_boundary_on_fail=(
                "block real-world rail-performance wording and compact-to-full promotion"
            ),
            compact_claim_effect=(
                "pending or failed rail timing thresholds allow engineering-only "
                "runs but block real-world rail-performance wording"
            ),
        ),
        row(
            threshold_id="rail_transit_headway_difference",
            benchmark_family="rail_or_transit",
            metric="headway_delta_or_percent_difference",
            unit="minutes_or_percent",
            comparison_basis="simulator headway proxy versus reviewed schedule/source benchmark",
            comparison_formula="abs(simulated_headway_min - benchmark_headway_min) <= max(minutes_band, percent_band * benchmark_headway_min)",
            pass_rule="pass within the larger of 10 minutes or 15 percent",
            warn_rule="warn within the larger of 20 minutes or 30 percent",
            fail_rule="fail outside the warn band",
            source_requirement=(
                "reviewed headway/timetable source or explicitly sensitivity-only "
                "rail profile"
            ),
            required_source_classes="reviewed_timetable_cache; reviewed_gtfs_validator_snapshot",
            disallowed_source_classes="documented_assumption_proxy; missing_headway_source",
            claim_boundary_on_pass=(
                "headway plausibility only; not agency service commitment or emergency availability"
            ),
            claim_boundary_on_warn=(
                "engineering-only headway warning; keep rail sensitivity caveat"
            ),
            claim_boundary_on_fail=(
                "block rail-headway claim and compact-to-full promotion"
            ),
            compact_claim_effect=(
                "headway proxy remains sensitivity-only until source-reviewed; "
                "compact outputs cannot imply agency service availability"
            ),
        ),
        row(
            threshold_id="transit_itinerary_time_difference",
            benchmark_family="rail_or_transit",
            metric="end_to_end_itinerary_delta_or_percent_difference",
            unit="minutes_or_percent",
            comparison_basis="simulator multimodal itinerary versus reviewed R5/OpenTripPlanner/agency benchmark",
            comparison_formula="abs(simulated_itinerary_min - benchmark_itinerary_min) <= max(minutes_band, percent_band * benchmark_itinerary_min)",
            pass_rule="pass within the larger of 10 minutes or 15 percent",
            warn_rule="warn within the larger of 20 minutes or 30 percent",
            fail_rule="fail outside the warn band or when no itinerary benchmark exists",
            source_requirement=(
                "R5/OpenTripPlanner/agency itinerary snapshot with retained inputs, "
                "GTFS feed, and query metadata"
            ),
            required_source_classes="reviewed_r5_or_otp_snapshot; reviewed_agency_itinerary_snapshot",
            disallowed_source_classes="documented_assumption_proxy; no_multimodal_benchmark",
            claim_boundary_on_pass=(
                "multimodal itinerary plausibility only; not passenger forecast or operational routing"
            ),
            claim_boundary_on_warn=(
                "engineering-only itinerary warning; no calibrated multimodal superiority wording"
            ),
            claim_boundary_on_fail=(
                "block multimodal real-world travel-time interpretation"
            ),
            compact_claim_effect=(
                "missing itinerary benchmark keeps compact multimodal results exploratory"
            ),
        ),
        row(
            threshold_id="transfer_fixed_delay_range",
            benchmark_family="transfer_or_boarding",
            metric="fixed_transfer_or_station_processing_time",
            unit="minutes",
            comparison_basis="assumed fixed process time versus reviewed source range or sensitivity range",
            comparison_formula="source_min <= assumed_fixed_minutes <= source_max",
            pass_rule=(
                "pass only when the assumption is within a reviewed source range "
                "or explicitly bounded sensitivity range"
            ),
            warn_rule=(
                "warn when the process assumption is documented but not yet "
                "source-backed"
            ),
            fail_rule=(
                "fail when transfer/loading assumptions are missing or used for "
                "operational wording"
            ),
            source_requirement=(
                "reviewed station, loading, transfer, or sensitivity-profile artifact"
            ),
            required_source_classes="reviewed_station_process_source; accepted_sensitivity_range",
            disallowed_source_classes="missing_transfer_source; unbounded_assumption",
            claim_boundary_on_pass=(
                "process-time sensitivity is bounded; not observed passenger-processing calibration"
            ),
            claim_boundary_on_warn=(
                "engineering-only process-time warning; no calibrated transfer wording"
            ),
            claim_boundary_on_fail=(
                "block transfer/boarding calibration claims"
            ),
            compact_claim_effect=(
                "unreviewed transfer assumptions keep multimodal advantage claims "
                "conditional"
            ),
        ),
        row(
            threshold_id="transfer_per_passenger_delay_range",
            benchmark_family="transfer_or_boarding",
            metric="per_passenger_loading_or_transfer_delay",
            unit="minutes_per_passenger",
            comparison_basis="assumed per-passenger delay versus reviewed source range or sensitivity range",
            comparison_formula="source_min <= assumed_minutes_per_passenger <= source_max",
            pass_rule=(
                "pass only when the per-passenger assumption is within a reviewed "
                "source range or explicitly bounded sensitivity range"
            ),
            warn_rule=(
                "warn when a bounded sensitivity range exists but no source-backed "
                "review has accepted it"
            ),
            fail_rule=(
                "fail when per-passenger transfer/loading assumptions are missing, "
                "negative, unbounded, or used for operational wording"
            ),
            source_requirement="reviewed loading, transfer, or sensitivity-profile artifact",
            required_source_classes="reviewed_loading_source; accepted_sensitivity_range",
            disallowed_source_classes="missing_loading_source; unbounded_assumption",
            claim_boundary_on_pass=(
                "per-passenger process assumption is bounded; not observed operations"
            ),
            claim_boundary_on_warn=(
                "engineering-only per-passenger warning; no calibrated process claim"
            ),
            claim_boundary_on_fail="block loading/transfer calibration claims",
            compact_claim_effect=(
                "unreviewed per-passenger assumptions keep resource-efficiency claims conditional"
            ),
        ),
        row(
            threshold_id="boarding_station_process_coverage",
            benchmark_family="transfer_or_boarding",
            metric="process_component_coverage",
            unit="coverage_flag",
            comparison_basis="station access, boarding, loading, queueing, and transfer components",
            comparison_formula="all_required_components in {sourced, sensitivity_bounded, explicitly_excluded}",
            pass_rule=(
                "pass when transfer/loading/station-processing components are "
                "included, sourced, sensitivity-bounded, or explicitly excluded"
            ),
            warn_rule="warn when station context exists but observed process timing is absent",
            fail_rule=(
                "fail when calibrated process wording is claimed with source gaps"
            ),
            source_requirement="reviewed process component inventory",
            required_source_classes="reviewed_component_inventory; accepted_exclusion_record",
            disallowed_source_classes="missing_component_inventory; hidden_process_assumption",
            claim_boundary_on_pass="component coverage guard only; not operations certification",
            claim_boundary_on_warn="engineering-only process coverage warning",
            claim_boundary_on_fail="block calibrated station-process wording",
            compact_claim_effect=(
                "uncovered process components keep multimodal results exploratory"
            ),
        ),
        row(
            threshold_id="benchmark_snapshot_pinning",
            benchmark_family="source_integrity",
            metric="raw_payload_config_hash_and_reference_version",
            unit="integrity_flag",
            comparison_basis="retained benchmark artifacts and manifests",
            comparison_formula="raw_payload_exists and sha256_present and reference_version_pinned",
            pass_rule="pass when raw payloads/configs exist, are hashable, and are versioned",
            warn_rule="warn for documented executable fallback without external raw payload",
            fail_rule="fail for live, unpinned, or unretained benchmark rows",
            source_requirement="retained local payloads or explicit fallback contract",
            required_source_classes="cached_external_router_snapshot; documented_executable_fallback",
            disallowed_source_classes="live_unpinned_router_response; missing_raw_payload",
            claim_boundary_on_pass="snapshot can be used as plausibility comparator only",
            claim_boundary_on_warn="fallback remains engineering review aid only",
            claim_boundary_on_fail="block benchmark-dependent compact promotion",
            compact_claim_effect=(
                "unpinned benchmark rows cannot support validation or publication "
                "claims and remain review aids only"
            ),
        ),
        row(
            threshold_id="threshold_revision_policy",
            benchmark_family="governance",
            metric="post_hoc_threshold_change",
            unit="governance_flag",
            comparison_basis="threshold table timestamp relative to compact outputs",
            comparison_formula="threshold_table_sha256 recorded before compact output manifest",
            pass_rule="pass when thresholds are declared before compact outputs",
            warn_rule="warn when thresholds are clarified without changing pass/warn/fail bands",
            fail_rule=(
                "fail for threshold changes made after viewing compact results "
                "unless the affected results are marked post hoc and exploratory"
            ),
            source_requirement="phase ledger and immutable threshold table",
            required_source_classes="precompact_threshold_table_manifest",
            disallowed_source_classes="post_hoc_unversioned_threshold_change",
            claim_boundary_on_pass="threshold governance satisfied for engineering compact review",
            claim_boundary_on_warn="threshold clarification warning; record rationale",
            claim_boundary_on_fail=(
                "affected compact evidence is exploratory until rerun under predeclared thresholds"
            ),
            compact_claim_effect=(
                "post hoc threshold changes block promotion from compact to full "
                "evidence until rerun under the new predeclared table"
            ),
        ),
        row(
            threshold_id="benchmark_claim_boundary_presence",
            benchmark_family="governance",
            metric="claim_boundary_text",
            unit="text_presence_flag",
            comparison_basis="benchmark, compact, statistics, figure, and report outputs",
            comparison_formula="required_claim_boundary_tokens present in downstream artifacts",
            pass_rule="pass when non-ground-truth, non-operational, and non-acceptance boundaries are present",
            warn_rule="warn when boundaries are present but not tied to every downstream artifact",
            fail_rule="fail when benchmark rows can be read as ground truth or accepted validation",
            source_requirement="artifact manifest and claim-alignment review",
            required_source_classes="claim_alignment_review_packet",
            disallowed_source_classes="missing_claim_boundary",
            claim_boundary_on_pass="benchmark evidence remains bounded review support",
            claim_boundary_on_warn="manual claim-boundary review required",
            claim_boundary_on_fail="block compact promotion and report use",
            compact_claim_effect=(
                "missing benchmark claim boundaries block promotion and report/figure use"
            ),
        ),
    ]


def write_phase8_precompact_tables(
    *,
    policy_rows: Sequence[Mapping[str, str]] | None = None,
    benchmark_rows: Sequence[Mapping[str, str]] | None = None,
    policy_output_path: str | Path = DEFAULT_POLICY_FEASIBILITY_TABLE_PATH,
    policy_manifest_path: str | Path = DEFAULT_POLICY_FEASIBILITY_MANIFEST_PATH,
    policy_doc_path: str | Path = DEFAULT_POLICY_FEASIBILITY_DOC_PATH,
    benchmark_output_path: str | Path = DEFAULT_BENCHMARK_THRESHOLD_TABLE_PATH,
    benchmark_manifest_path: str | Path = DEFAULT_BENCHMARK_THRESHOLD_MANIFEST_PATH,
    benchmark_doc_path: str | Path = DEFAULT_BENCHMARK_THRESHOLD_DOC_PATH,
    policy_path: str | Path = DEFAULT_POLICY_ALTERNATIVES_PATH,
    design_path: str | Path = DEFAULT_PILOT_DESIGN_PATH,
    region_path: str | Path = DEFAULT_REGION_PATH,
    fallback_benchmark_path: str | Path = DEFAULT_FALLBACK_BENCHMARK_PATH,
    osrm_benchmark_path: str | Path = DEFAULT_OSRM_BENCHMARK_PATH,
    osrm_manifest_path: str | Path = DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH,
) -> dict[str, Any]:
    """Write both Phase 8 pre-compact review tables."""

    resolved_policy_rows = list(
        policy_rows
        if policy_rows is not None
        else build_policy_feasibility_rows(
            policy_path=policy_path,
            design_path=design_path,
            region_path=region_path,
        )
    )
    resolved_benchmark_rows = list(
        benchmark_rows
        if benchmark_rows is not None
        else build_benchmark_threshold_rows(
            fallback_benchmark_path=fallback_benchmark_path,
            osrm_benchmark_path=osrm_benchmark_path,
            osrm_manifest_path=osrm_manifest_path,
        )
    )

    policy_manifest = _write_table_artifacts(
        rows=resolved_policy_rows,
        columns=POLICY_FEASIBILITY_COLUMNS,
        output_path=policy_output_path,
        manifest_path=policy_manifest_path,
        doc_path=policy_doc_path,
        title="Policy Feasibility and Fairness Table",
        row_id_column="policy_id",
        status_column="feasibility_status",
        input_paths=(policy_path, design_path, region_path),
    )
    benchmark_manifest = _write_table_artifacts(
        rows=resolved_benchmark_rows,
        columns=BENCHMARK_THRESHOLD_COLUMNS,
        output_path=benchmark_output_path,
        manifest_path=benchmark_manifest_path,
        doc_path=benchmark_doc_path,
        title="Benchmark Threshold Table",
        row_id_column="threshold_id",
        status_column="predeclared_before_compact",
        input_paths=(fallback_benchmark_path, osrm_benchmark_path, osrm_manifest_path),
    )
    return {
        "schema_version": 1,
        "result_scope": PHASE8_PRECOMPACT_SCOPE,
        "publication_ready": False,
        "can_mark_complete": False,
        "policy_manifest": policy_manifest,
        "benchmark_manifest": benchmark_manifest,
    }


def _write_table_artifacts(
    *,
    rows: Sequence[Mapping[str, str]],
    columns: Sequence[str],
    output_path: str | Path,
    manifest_path: str | Path,
    doc_path: str | Path,
    title: str,
    row_id_column: str,
    status_column: str,
    input_paths: Sequence[str | Path],
) -> dict[str, Any]:
    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: str(row.get(column, "")) for column in columns})

    summary = {
        "schema_version": 1,
        "result_scope": PHASE8_PRECOMPACT_SCOPE,
        "claim_boundary": PHASE8_PRECOMPACT_SCOPE,
        "row_count": len(rows),
        "row_ids": [str(row.get(row_id_column, "")) for row in rows],
        "status_counts": _counts(row.get(status_column, "") for row in rows),
        "publication_ready": False,
        "can_mark_complete": False,
        "phase8_precompact_table_present": True,
        "validation_gate_closure_candidate_count": 0,
        "formal_acceptance_evidence": False,
        "inputs": [_display_path(Path(path)) for path in input_paths],
        "outputs": {
            "csv": _display_path(output),
            "manifest": _display_path(manifest),
            "doc": _display_path(doc),
        },
        "review_items": [
            "review before compact execution",
            "keep compact output exploratory when source dependencies remain pending",
            "do not copy this table into formal acceptance paths",
        ],
    }
    manifest.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(_build_markdown(title, summary, rows=rows, row_id=row_id_column), encoding="utf-8")
    return summary


def _build_markdown(
    title: str,
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
    row_id: str,
) -> str:
    lines = [
        f"# {title}",
        "",
        str(manifest.get("claim_boundary", PHASE8_PRECOMPACT_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Rows: {manifest.get('row_count', 0)}",
        f"- Status counts: `{manifest.get('status_counts', {})}`",
        "",
        "## Rows",
        "",
        "| Row | Key Status | Claim Boundary |",
        "| --- | --- | --- |",
    ]
    for row in rows:
        status = row.get("feasibility_status") or row.get("predeclared_before_compact") or ""
        lines.append(
            f"| {_cell(row.get(row_id, ''))} | {_cell(status)} | "
            f"{_cell(row.get('claim_boundary', PHASE8_PRECOMPACT_SCOPE))} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This table is a Phase 8 pre-compact guardrail.",
            "- It cannot close validation, policy, publication, final-study, or formal acceptance gates.",
            "- Any compact result that violates these rows remains exploratory unless rerun after review.",
            "",
        ]
    )
    return "\n".join(lines)


def _policy_feasibility_row(
    policy: PolicyAlternative,
    policies: Sequence[PolicyAlternative],
    base_config: Mapping[str, Any],
    profiles_by_policy: Mapping[str, Sequence[str]],
    evidence_paths: str,
) -> dict[str, str]:
    policy_id = policy.policy_id
    baseline_id = _same_mode_baseline_policy_id(policy)
    variant = build_policy_config_variant(base_config, policy, policies)
    baseline_variant = build_policy_config_variant(base_config, baseline_id, policies)
    config = variant.config
    baseline_config = baseline_variant.config
    rail = _rail_values(config)
    baseline_rail = _rail_values(baseline_config)
    vehicle_delta = _vehicle_delta_vs_baseline(config, baseline_config)
    no_effect = _policy_has_no_effect(policy, config, baseline_config)
    profile_ids = tuple(profiles_by_policy.get(policy_id, ()))
    excluded_reason = _excluded_reason(policy)
    feasibility = _policy_feasibility_status(policy, no_effect=no_effect)
    fairness = _policy_fairness_status(policy, no_effect=no_effect)
    return {
        "policy_id": policy_id,
        "scenario_type": policy.scenario_type,
        "profile_inclusion": "; ".join(profile_ids),
        "excluded_reason": excluded_reason,
        "same_mode_baseline_policy_id": baseline_id,
        "comparison_role": _policy_comparison_role(policy),
        "vehicle_budget_status": _vehicle_budget_status(policy, no_effect=no_effect),
        "bus_fleet_size": _format_config_value(config, ("bus", "fleet_size")),
        "shuttle_fleet_size": _multimodal_config_value(
            config,
            policy,
            ("multimodal", "shuttle_fleet_size"),
        ),
        "lastmile_fleet_size": _multimodal_config_value(
            config,
            policy,
            ("multimodal", "lastmile_fleet_size"),
        ),
        "road_vehicle_capacity_pax": _road_vehicle_capacity(config, policy),
        "rail_capacity_pax_per_train": _rail_config_value(policy, rail["capacity"]),
        "rail_headway_min": _rail_config_value(policy, rail["headway"]),
        "rail_travel_time_min": _rail_config_value(policy, rail["travel_time"]),
        "vehicle_delta_vs_baseline": vehicle_delta,
        "service_minute_budget_status": "missing_predeclared_budget",
        "road_vehicle_service_min_budget": "not_predeclared",
        "train_service_min_budget": "not_predeclared",
        "total_service_min_budget": "not_predeclared",
        "route_leg_ids": _route_leg_ids(policy),
        "road_route_check_ids": _road_route_check_ids(policy),
        "graph_variant_dependency": _graph_variant_dependency(policy),
        "corridor_overlap_class": _corridor_overlap_class(policy),
        "access_leg_count": _access_leg_count(policy),
        "egress_leg_count": _egress_leg_count(policy),
        "transfer_delay_location": _transfer_delay_location(policy),
        "fixed_transfer_min": _multimodal_config_value(
            config,
            policy,
            ("multimodal", "transfer_time_min"),
        ),
        "per_passenger_transfer_min": _multimodal_config_value(
            config,
            policy,
            ("multimodal", "transfer_per_passenger_min"),
        ),
        "egress_transfer_model": _egress_transfer_model(policy),
        "rerouting_authority_class": _rerouting_authority_class(policy),
        "routing_adaptation_implemented": "dynamic_shortest_path_at_road_leg_departure",
        "dispatch_adaptation_implemented": _dispatch_adaptation_implemented(policy),
        "adaptive_label_status": _adaptive_label_status(policy),
        "feasibility_status": feasibility,
        "fairness_status": fairness,
        "blocking_reason": _policy_blocking_reason(
            policy,
            no_effect=no_effect,
            excluded_reason=excluded_reason,
        ),
        "required_reviewer_action": _policy_required_reviewer_action(
            policy,
            no_effect=no_effect,
        ),
        "evidence_input_paths": evidence_paths,
        "can_support_publication_or_acceptance": "false",
        "formal_acceptance_evidence": "false",
        "claim_boundary": PHASE8_PRECOMPACT_SCOPE,
    }


def _same_mode_baseline_policy_id(policy: PolicyAlternative) -> str:
    return "bus_only" if policy.scenario_type == "bus_only" else "baseline_multimodal"


def _rail_values(config: Mapping[str, Any]) -> dict[str, float]:
    rail_links = _nested_value(config, ("network", "rail_link"), [])
    if not rail_links:
        return {"travel_time": 0.0, "headway": 0.0, "capacity": 0.0}
    rail = list(rail_links[0])
    return {
        "travel_time": _float(rail[2] if len(rail) > 2 else 0.0) or 0.0,
        "headway": _float(rail[3] if len(rail) > 3 else 0.0) or 0.0,
        "capacity": _float(rail[4] if len(rail) > 4 else 0.0) or 0.0,
    }


def _vehicle_delta_vs_baseline(
    config: Mapping[str, Any],
    baseline_config: Mapping[str, Any],
) -> str:
    fields = (
        ("bus_fleet_size", ("bus", "fleet_size")),
        ("shuttle_fleet_size", ("multimodal", "shuttle_fleet_size")),
        ("lastmile_fleet_size", ("multimodal", "lastmile_fleet_size")),
        ("lastmile_vehicle_capacity", ("multimodal", "lastmile_vehicle_capacity")),
    )
    deltas: list[str] = []
    for label, path in fields:
        current = _float(_nested_value(config, path, ""))
        baseline = _float(_nested_value(baseline_config, path, ""))
        if current is None or baseline is None:
            continue
        delta = current - baseline
        if abs(delta) > 1e-9:
            deltas.append(f"{label}={_format_signed(delta)}")
    rail = _rail_values(config)
    baseline_rail = _rail_values(baseline_config)
    for label in ("travel_time", "headway", "capacity"):
        delta = rail[label] - baseline_rail[label]
        if abs(delta) > 1e-9:
            deltas.append(f"rail_{label}={_format_signed(delta)}")
    return "; ".join(deltas) if deltas else "no_effect_vs_same_mode_baseline"


def _policy_has_no_effect(
    policy: PolicyAlternative,
    config: Mapping[str, Any],
    baseline_config: Mapping[str, Any],
) -> bool:
    if policy.policy_id in {"bus_only", "baseline_multimodal"}:
        return False
    return dict(config) == dict(baseline_config)


def _policy_comparison_role(policy: PolicyAlternative) -> str:
    if policy.policy_id == "bus_only":
        return "baseline direct-road comparator"
    if policy.policy_id == "baseline_multimodal":
        return "baseline rail-bus comparator"
    if policy.policy_id == "bus_corridor_redundancy":
        return "excluded graph-variant candidate"
    if policy.policy_id in {"rail_delay_or_partial_unavailability", "fleet_shortage_stress"}:
        return "stress/sensitivity row"
    if policy.policy_id == "staggered_or_adaptive_dispatch":
        return "deterministic dispatch variant"
    return "asymmetric resource sensitivity row"


def _vehicle_budget_status(policy: PolicyAlternative, *, no_effect: bool) -> str:
    if policy.policy_id in {"bus_only", "baseline_multimodal"}:
        return "baseline_budget_not_cost_calibrated"
    if policy.policy_id == "bus_corridor_redundancy":
        return "blocked_until_documented_corridor_budget_exists"
    if no_effect:
        return "configured_knob_has_no_current_effect"
    if policy.policy_id in {
        "multimodal_lastmile_redundancy",
        "multimodal_increased_feeder_capacity",
    }:
        return "adds_asymmetric_vehicle_budget"
    if policy.policy_id == "rail_delay_or_partial_unavailability":
        return "changes_rail_service_budget_for_stress_only"
    if policy.policy_id == "staggered_or_adaptive_dispatch":
        return "changes_schedule_not_fleet_budget"
    return "stress_budget_not_cost_calibrated"


def _road_vehicle_capacity(config: Mapping[str, Any], policy: PolicyAlternative) -> str:
    if policy.scenario_type == "bus_only":
        return _format_config_value(config, ("personnel", "group_size"))
    return _format_config_value(config, ("multimodal", "lastmile_vehicle_capacity"))


def _multimodal_config_value(
    config: Mapping[str, Any],
    policy: PolicyAlternative,
    path: Sequence[str],
) -> str:
    if policy.scenario_type == "bus_only":
        return "not_applicable"
    return _format_config_value(config, path)


def _rail_config_value(policy: PolicyAlternative, value: Any) -> str:
    if policy.scenario_type == "bus_only":
        return "not_applicable"
    return _format_number(value)


def _route_leg_ids(policy: PolicyAlternative) -> str:
    if policy.scenario_type == "bus_only":
        return "A->D"
    return "A->S; S->R; R->D"


def _road_route_check_ids(policy: PolicyAlternative) -> str:
    if policy.scenario_type == "bus_only":
        return "route_bus_direct"
    return "route_rail_access; route_last_mile"


def _graph_variant_dependency(policy: PolicyAlternative) -> str:
    variant = policy.knob("network_variant")
    if variant:
        return f"requires graph variant {variant}"
    return "current cached pilot graph"


def _corridor_overlap_class(policy: PolicyAlternative) -> str:
    if policy.policy_id == "bus_corridor_redundancy":
        return "blocked_missing_documented_redundant_corridor"
    if policy.scenario_type == "bus_only":
        return "direct_road_corridor_only"
    return "shared_local_access_egress_plus_rail_core"


def _access_leg_count(policy: PolicyAlternative) -> str:
    return "0" if policy.scenario_type == "bus_only" else "1"


def _egress_leg_count(policy: PolicyAlternative) -> str:
    return "0" if policy.scenario_type == "bus_only" else "1"


def _transfer_delay_location(policy: PolicyAlternative) -> str:
    if policy.scenario_type == "bus_only":
        return "none"
    return "pre_rail_after_feeder_arrival"


def _egress_transfer_model(policy: PolicyAlternative) -> str:
    if policy.scenario_type == "bus_only":
        return "none"
    return "implicit_lastmile_dispatch_no_separate_fixed_egress_transfer"


def _rerouting_authority_class(policy: PolicyAlternative) -> str:
    if policy.policy_id == "bus_corridor_redundancy":
        return "requires_external_authority_and_documented_corridor"
    return "no_public_agency_rerouting_authority_recorded"


def _dispatch_adaptation_implemented(policy: PolicyAlternative) -> str:
    if policy.policy_id == "staggered_or_adaptive_dispatch":
        return "partial_deterministic_feeder_spacing_and_on_demand_lastmile_release"
    return "fixed_schedule_or_policy_knob_only"


def _adaptive_label_status(policy: PolicyAlternative) -> str:
    if policy.policy_id == "staggered_or_adaptive_dispatch":
        return "partial_dispatch_only_not_adaptive_route_optimization"
    if "adaptive" in policy.policy_id:
        return "label_requires_review"
    return "no_adaptive_label"


def _policy_feasibility_status(policy: PolicyAlternative, *, no_effect: bool) -> str:
    if policy.policy_id == "bus_corridor_redundancy":
        return "blocked_excluded_until_documented_corridor"
    if no_effect:
        return "blocked_current_policy_no_effect"
    if policy.policy_id in {"bus_only", "baseline_multimodal"}:
        return "proxy_comparator_ready_for_engineering_compact_only"
    if policy.policy_id in {"rail_delay_or_partial_unavailability", "fleet_shortage_stress"}:
        return "stress_sensitivity_only"
    if policy.policy_id == "staggered_or_adaptive_dispatch":
        return "deterministic_dispatch_variant_not_adaptive_routing"
    return "resource_sensitivity_ready_for_engineering_compact_only"


def _policy_fairness_status(policy: PolicyAlternative, *, no_effect: bool) -> str:
    if policy.policy_id == "bus_corridor_redundancy":
        return "blocked_unreviewed_corridor_access_fairness"
    if no_effect:
        return "blocked_no_effect_cannot_support_fairness_comparison"
    if policy.policy_id in {
        "multimodal_lastmile_redundancy",
        "multimodal_increased_feeder_capacity",
    }:
        return "asymmetric_resource_increase_requires_budget_caveat"
    if policy.policy_id in {"rail_delay_or_partial_unavailability", "fleet_shortage_stress"}:
        return "stress_row_not_welfare_improving_policy"
    if policy.scenario_type == "bus_only":
        return "road_only_delay_burden_documented_not_accepted"
    return "multimodal_transfer_burden_documented_not_accepted"


def _excluded_reason(policy: PolicyAlternative) -> str:
    if policy.policy_id == "bus_corridor_redundancy":
        return "design excludes until accepted real-world redundant-corridor graph exists"
    return ""


def _policy_blocking_reason(
    policy: PolicyAlternative,
    *,
    no_effect: bool,
    excluded_reason: str,
) -> str:
    if excluded_reason:
        return excluded_reason
    if no_effect:
        return "configured knobs do not change current effective pilot config versus same-mode baseline"
    return "service-minute budget and fairness review remain missing before publication or acceptance use"


def _policy_required_reviewer_action(
    policy: PolicyAlternative,
    *,
    no_effect: bool,
) -> str:
    if policy.policy_id == "bus_corridor_redundancy":
        return "supply documented redundant-corridor graph variant or keep excluded"
    if no_effect:
        return "revise policy knob or remove policy from compact claims"
    if policy.policy_id == "staggered_or_adaptive_dispatch":
        return "label as deterministic dispatch variant and remove adaptive-routing wording"
    return "predeclare resource budget and fairness caveats before compact interpretation"


def _policy_role(policy: Mapping[str, str]) -> str:
    policy_id = str(policy.get("policy_id", ""))
    scenario_type = str(policy.get("scenario_type", ""))
    if policy_id == "bus_corridor_redundancy":
        return "excluded road-corridor redundancy candidate"
    if policy_id in {"rail_delay_or_partial_unavailability", "fleet_shortage_stress"}:
        return "stress/sensitivity policy"
    if policy_id in {
        "multimodal_lastmile_redundancy",
        "multimodal_increased_feeder_capacity",
    }:
        return "resource sensitivity policy"
    if policy_id == "staggered_or_adaptive_dispatch":
        return "deterministic dispatch variant"
    if scenario_type == "bus_only":
        return "direct road comparator"
    return "rail-bus multimodal comparator"


def _vehicle_service_minute_budget(policy: Mapping[str, str]) -> str:
    changes = _nonblank_changes(policy)
    if not changes:
        return "baseline config resource budget; service minutes are not cost-normalized"
    return "resource/schedule overrides present: " + "; ".join(changes)


def _capacity_and_fleet_assumptions(policy: Mapping[str, str]) -> str:
    fields = (
        "bus_fleet_size",
        "bus_fleet_multiplier",
        "multimodal_shuttle_fleet_size",
        "multimodal_shuttle_fleet_multiplier",
        "multimodal_lastmile_fleet_size",
        "multimodal_lastmile_fleet_multiplier",
        "multimodal_lastmile_vehicle_capacity",
        "multimodal_lastmile_vehicle_capacity_multiplier",
        "rail_capacity_multiplier",
    )
    values = [f"{field}={policy[field]}" for field in fields if str(policy.get(field, "")).strip()]
    if not values:
        return "inherits baseline config capacity and finite fleet assumptions"
    return "; ".join(values)


def _route_corridor_overlap(policy: Mapping[str, str]) -> str:
    policy_id = str(policy.get("policy_id", ""))
    scenario_type = str(policy.get("scenario_type", ""))
    if policy_id == "bus_corridor_redundancy":
        return "requires documented redundant road-network variant; excluded from compact evidence"
    if scenario_type == "bus_only":
        return "direct A-D road corridor; road-only overlap with disruption scenarios"
    return "A-S feeder road, S-R rail proxy, and R-D last-mile road; overlaps road-only option on local access/egress segments"


def _access_egress_transfer_burden(policy: Mapping[str, str]) -> str:
    if str(policy.get("scenario_type", "")) == "bus_only":
        return "no rail transfer burden; passengers stay on direct road vehicles"
    return "feeder access, rail wait/travel, transfer processing, and last-mile egress burden remain explicit"


def _rerouting_authority(policy: Mapping[str, str]) -> str:
    policy_id = str(policy.get("policy_id", ""))
    if policy_id == "bus_corridor_redundancy":
        return "requires external authority and documented redundant corridor; not implemented in current accepted graph"
    if str(policy.get("network_variant", "")).strip():
        return "network-variant dependent; must be reviewed before operational interpretation"
    return "no live rerouting authority modeled; route/corridor choices are preconfigured"


def _adaptive_routing_or_dispatch_status(policy: Mapping[str, str]) -> str:
    policy_id = str(policy.get("policy_id", ""))
    if policy_id == "staggered_or_adaptive_dispatch":
        return "partly implemented as deterministic dispatch spacing/on-demand last-mile release; no adaptive route optimization"
    if "stress" in policy_id or policy_id == "rail_delay_or_partial_unavailability":
        return "stress label only; no adaptive routing or dispatch implementation"
    return "not implemented; policy uses fixed scenario and schedule assumptions"


def _resource_parity_class(policy: Mapping[str, str]) -> str:
    values = [_float(value) for value in policy.values()]
    multipliers = [
        value
        for key, value in policy.items()
        if key.endswith("_multiplier") and _float(value) is not None
    ]
    if any(value is not None and value > 1.0 for value in multipliers):
        return "not resource-neutral; adds or stretches capacity/service resources"
    if any(value is not None and 0.0 < value < 1.0 for value in multipliers):
        return "not resource-neutral; removes capacity/service resources for stress testing"
    if any(value is not None and value > 0.0 for value in values) and str(
        policy.get("policy_id", "")
    ) == "staggered_or_adaptive_dispatch":
        return "schedule variant; compare separately from resource-neutral baselines"
    return "baseline resource parity assumed but not cost-calibrated"


def _fairness_risk(policy: Mapping[str, str]) -> str:
    policy_id = str(policy.get("policy_id", ""))
    scenario_type = str(policy.get("scenario_type", ""))
    if policy_id == "bus_corridor_redundancy":
        return "excluded option could advantage road users unless corridor access is documented"
    if "increased" in policy_id or "redundancy" in policy_id:
        return "extra resources can improve one mode or segment; compare with resource-budget caveat"
    if "shortage" in policy_id or "delay" in policy_id:
        return "stress policy intentionally worsens a mode; not a welfare-improving alternative"
    if scenario_type == "bus_only":
        return "road-only passengers bear congestion and blockage exposure"
    return "transfer, rail-access, and last-mile burdens may shift delay to multimodal passengers"


def _feasibility_status(policy: Mapping[str, str]) -> str:
    policy_id = str(policy.get("policy_id", ""))
    if policy_id == "bus_corridor_redundancy":
        return "excluded_pending_documented_corridor"
    if policy_id in {"rail_delay_or_partial_unavailability", "fleet_shortage_stress"}:
        return "stress_sensitivity_only"
    if policy_id in {
        "multimodal_lastmile_redundancy",
        "multimodal_increased_feeder_capacity",
    }:
        return "feasible_as_resource_sensitivity_with_caveat"
    if policy_id == "staggered_or_adaptive_dispatch":
        return "feasible_as_deterministic_dispatch_variant_not_adaptive_routing"
    return "feasible_as_proxy_comparator_with_pending_evidence"


def _policy_compact_claim_effect(policy: Mapping[str, str]) -> str:
    status = _feasibility_status(policy)
    if status == "excluded_pending_documented_corridor":
        return "exclude from compact profiles until a documented corridor variant is reviewed"
    if "sensitivity" in status:
        return "include only for sensitivity/stress interpretation; not as a superior operating policy"
    if "dispatch" in status:
        return "label as deterministic dispatch logic; do not claim adaptive AI routing"
    return "compact result remains exploratory while road/rail evidence gates remain pending"


def _nonblank_changes(policy: Mapping[str, str]) -> list[str]:
    ignored = {
        "policy_id",
        "scenario_type",
        "decision_interpretation",
        "claim_boundary",
        "notes",
    }
    return [
        f"{key}={value}"
        for key, value in policy.items()
        if key not in ignored and str(value).strip()
    ]


def _benchmark_source_summary(
    *,
    fallback_benchmark_path: str | Path,
    osrm_benchmark_path: str | Path,
    osrm_manifest_path: str | Path,
) -> dict[str, Any]:
    fallback_rows = _read_csv_rows(fallback_benchmark_path)
    osrm_rows = _read_csv_rows(osrm_benchmark_path)
    osrm_manifest = _read_json_object(osrm_manifest_path)
    return {
        "fallback_source_classes": _counts(row.get("source_class", "") for row in fallback_rows),
        "osrm_source_classes": _counts(row.get("source_class", "") for row in osrm_rows),
        "osrm_raw_response_file_count": _int(
            osrm_manifest.get("raw_response_file_count", 0)
        ),
        "osrm_unpinned_row_count": _int(osrm_manifest.get("unpinned_row_count", 0)),
    }


def _profiles_by_policy(design: Mapping[str, Any]) -> dict[str, tuple[str, ...]]:
    result: dict[str, list[str]] = {}
    profiles = design.get("profiles", {})
    if not isinstance(profiles, Mapping):
        return {}
    for profile_id, profile in profiles.items():
        if not isinstance(profile, Mapping):
            continue
        for policy_id in profile.get("policy_ids", ()):
            key = str(policy_id)
            result.setdefault(key, []).append(str(profile_id))
    return {key: tuple(values) for key, values in result.items()}


def _read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    filepath = Path(path)
    if not filepath.exists():
        return []
    with filepath.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _read_json_object(path: str | Path) -> dict[str, Any]:
    filepath = Path(path)
    if not filepath.exists():
        return {}
    with filepath.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    return value if isinstance(value, dict) else {}


def _read_yaml_object(path: str | Path) -> dict[str, Any]:
    filepath = Path(path)
    if not filepath.exists():
        return {}
    with filepath.open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    return value if isinstance(value, dict) else {}


def _nested_value(
    mapping: Mapping[str, Any],
    path: Sequence[str],
    default: Any = "",
) -> Any:
    current: Any = mapping
    for key in path:
        if not isinstance(current, Mapping) or key not in current:
            return default
        current = current[key]
    return current


def _format_config_value(mapping: Mapping[str, Any], path: Sequence[str]) -> str:
    return _format_number(_nested_value(mapping, path, ""))


def _format_number(value: Any) -> str:
    number = _float(value)
    if number is None:
        return ""
    if abs(number - round(number)) < 1e-9:
        return str(int(round(number)))
    return f"{number:.6f}".rstrip("0").rstrip(".")


def _format_signed(value: float) -> str:
    if abs(value - round(value)) < 1e-9:
        return f"{int(round(value)):+d}"
    return f"{value:+.6f}".rstrip("0").rstrip(".")


def _counts(values: Iterable[Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value).strip() or "blank"
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _format_counts(counts: Mapping[str, int]) -> str:
    if not counts:
        return "none"
    return "; ".join(f"{key}={counts[key]}" for key in sorted(counts))


def _float(value: Any) -> float | None:
    try:
        text = str(value).strip()
        if not text:
            return None
        return float(text)
    except (TypeError, ValueError):
        return None


def _int(value: Any) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return 0


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


__all__ = [
    "BENCHMARK_THRESHOLD_COLUMNS",
    "DEFAULT_BENCHMARK_THRESHOLD_DOC_PATH",
    "DEFAULT_BENCHMARK_THRESHOLD_MANIFEST_PATH",
    "DEFAULT_BENCHMARK_THRESHOLD_TABLE_PATH",
    "DEFAULT_POLICY_FEASIBILITY_DOC_PATH",
    "DEFAULT_POLICY_FEASIBILITY_MANIFEST_PATH",
    "DEFAULT_POLICY_FEASIBILITY_TABLE_PATH",
    "PHASE8_PRECOMPACT_SCOPE",
    "POLICY_FEASIBILITY_COLUMNS",
    "build_benchmark_threshold_rows",
    "build_policy_feasibility_rows",
    "write_phase8_precompact_tables",
]
