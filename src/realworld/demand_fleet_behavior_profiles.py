"""Phase 5 demand, fleet, and behavior profile review artifacts.

These helpers make scenario demand, finite-fleet, and behavior assumptions
explicit before compact or final experiments consume them. The outputs are
review inputs only; they do not calibrate OD demand, certify fleet availability,
or approve behavior assumptions.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml

from src.realworld.pilot_experiments import make_pilot_base_config
from src.realworld.source_artifacts import file_sha256


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config.yaml"
DEFAULT_REGION_PATH = PROJECT_ROOT / "data" / "regions" / "pilot_region.yaml"
DEFAULT_PILOT_DESIGN_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "pilot_experiment_design.json"
)
DEFAULT_SENSITIVITY_DESIGN_PATH = (
    PROJECT_ROOT / "data" / "scenarios" / "sensitivity_design.csv"
)
DEFAULT_POLICY_ALTERNATIVES_PATH = (
    PROJECT_ROOT / "data" / "scenarios" / "policy_alternatives.csv"
)
DEFAULT_FLEET_ASSUMPTIONS_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "fleet_assumptions.csv"
)
DEFAULT_PILOT_EXPERIMENTS_SOURCE_PATH = (
    PROJECT_ROOT / "src" / "realworld" / "pilot_experiments.py"
)
DEFAULT_RECOVERY_DECISION_PATH = (
    PROJECT_ROOT
    / "docs"
    / "recovery"
    / "transport_core_reconstruction_decision_20260602.md"
)
DEFAULT_DEMAND_PROFILE_PATH = (
    PROJECT_ROOT / "data" / "scenarios" / "demand_profiles.csv"
)
DEFAULT_FLEET_PROFILE_PATH = PROJECT_ROOT / "data" / "scenarios" / "fleet_profiles.csv"
DEFAULT_BEHAVIOR_PROFILE_PATH = (
    PROJECT_ROOT / "data" / "scenarios" / "behavior_profiles.csv"
)
DEFAULT_PROFILE_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "scenarios" / "demand_fleet_behavior_profile_manifest.json"
)
DEFAULT_PROFILE_DOC_PATH = (
    PROJECT_ROOT / "docs" / "demand_fleet_behavior_profiles.md"
)

PROFILE_SCOPE = (
    "Phase 5 demand/fleet/behavior profile packet only; bounded scenario "
    "inputs for decision-support simulation, not calibrated OD demand, not an "
    "agency fleet roster, not observed no-show behavior, not an operational "
    "transport plan, not a public-agency forecast, not publication readiness, "
    "not final-study readiness, and not formal acceptance."
)

DEMAND_PROFILE_COLUMNS: tuple[str, ...] = (
    "profile_id",
    "region_id",
    "origin_id",
    "origin_share",
    "total_demand_pax",
    "assembly_time_min",
    "arrival_distribution",
    "arrival_param_mu",
    "arrival_param_sigma",
    "arrival_window_start_min",
    "arrival_window_end_min",
    "no_show_fraction",
    "late_arrival_fraction",
    "late_arrival_threshold_min",
    "boarding_batch_size_pax",
    "completion_denominator",
    "source_class",
    "source_name",
    "source_url_or_citation",
    "evidence_status",
    "can_support_parameter_evidence_gate",
    "can_support_acceptance_gate",
    "claim_boundary",
    "notes",
)

FLEET_PROFILE_COLUMNS: tuple[str, ...] = (
    "profile_id",
    "region_id",
    "role",
    "vehicle_capacity_pax",
    "fleet_size",
    "dispatch_interval_min",
    "first_departure_min",
    "turnaround_min",
    "source_class",
    "source_name",
    "source_url_or_citation",
    "evidence_status",
    "can_support_parameter_evidence_gate",
    "can_support_acceptance_gate",
    "claim_boundary",
    "notes",
)

BEHAVIOR_PROFILE_COLUMNS: tuple[str, ...] = (
    "profile_id",
    "region_id",
    "behavior_class",
    "model_field",
    "baseline_value",
    "sensitivity_low",
    "sensitivity_high",
    "implementation_status",
    "denominator_treatment",
    "source_class",
    "source_name",
    "source_url_or_citation",
    "evidence_status",
    "can_support_parameter_evidence_gate",
    "can_support_acceptance_gate",
    "claim_boundary",
    "notes",
)


def build_phase5_profile_rows(
    *,
    config_path: str | Path = DEFAULT_CONFIG_PATH,
    region_path: str | Path = DEFAULT_REGION_PATH,
    pilot_design_path: str | Path = DEFAULT_PILOT_DESIGN_PATH,
    sensitivity_design_path: str | Path = DEFAULT_SENSITIVITY_DESIGN_PATH,
) -> dict[str, list[dict[str, str]]]:
    """Return demand, fleet, and behavior profile rows."""

    config = _read_yaml_object(config_path)
    region = _read_yaml_object(region_path)
    pilot_design = _read_json_object(pilot_design_path)
    sensitivity = _sensitivity_by_id(sensitivity_design_path)
    pilot_config = make_pilot_base_config(region)
    region_id = str(pilot_design.get("region_id") or region.get("region_id") or "")

    demand_rows = [
        _demand_row(
            profile_id="pilot_default_demand",
            region_id=region_id,
            origin_id="A",
            origin_share="1.0",
            total_demand_pax=_config_value(pilot_config, ("personnel", "total")),
            assembly_time_min=_config_value(
                pilot_config,
                ("personnel", "assembly_time"),
            ),
            arrival_distribution=_config_value(
                pilot_config,
                ("lateness", "distribution"),
            ),
            arrival_param_mu=_config_value(pilot_config, ("lateness", "mu")),
            arrival_param_sigma=_config_value(
                pilot_config,
                ("lateness", "sigma"),
                fallback=_first_config_list_value(
                    pilot_config,
                    ("lateness", "sigma_levels"),
                ),
            ),
            arrival_window_start_min="0",
            arrival_window_end_min="",
            no_show_fraction="0",
            late_arrival_fraction="0",
            late_arrival_threshold_min="",
            boarding_batch_size_pax=_config_value(
                pilot_config,
                ("personnel", "group_size"),
            ),
            completion_denominator="total_scenario_demand",
            source_class="sensitivity-only",
            source_name="Pilot fixture demand profile",
            source_url_or_citation="src/realworld/pilot_experiments.py; data/manifests/pilot_experiment_design.json",
            evidence_status="bounded_scenario_assumption_not_calibration",
            notes=(
                "Fixture-scale demand used for fast pilot screening; not a "
                "calibrated OD demand estimate."
            ),
        ),
        _demand_row(
            profile_id="config_default_demand",
            region_id=region_id,
            origin_id="A",
            origin_share="1.0",
            total_demand_pax=_config_value(config, ("personnel", "total")),
            assembly_time_min=_config_value(config, ("personnel", "assembly_time")),
            arrival_distribution=_config_value(config, ("lateness", "distribution")),
            arrival_param_mu=_config_value(config, ("lateness", "mu")),
            arrival_param_sigma=";".join(
                str(value) for value in _config_list(config, ("lateness", "sigma_levels"))
            ),
            arrival_window_start_min="",
            arrival_window_end_min="",
            no_show_fraction="0",
            late_arrival_fraction="0",
            late_arrival_threshold_min="",
            boarding_batch_size_pax=_config_value(config, ("personnel", "group_size")),
            completion_denominator="total_scenario_demand",
            source_class="expert assumption",
            source_name="Config personnel and lateness defaults",
            source_url_or_citation="config.yaml",
            evidence_status="review_required_scenario_assumption",
            notes=(
                "Repository default demand profile for abstract experiments; "
                "not calibrated to observed OD demand."
            ),
        ),
    ]

    fleet_rows = _fleet_rows_for_config(
        profile_id="pilot_default_fleet",
        region_id=region_id,
        config=pilot_config,
        source_class="sensitivity-only",
        source_name="Pilot fixture finite-fleet profile",
        source_url_or_citation="src/realworld/pilot_experiments.py; data/manifests/pilot_experiment_design.json",
        evidence_status="bounded_scenario_assumption_not_inventory",
    ) + _fleet_rows_for_config(
        profile_id="config_default_fleet",
        region_id=region_id,
        config=config,
        source_class="expert assumption",
        source_name="Config finite-fleet defaults",
        source_url_or_citation="config.yaml; data/parameters/fleet_assumptions.csv",
        evidence_status="review_required_fleet_assumption",
    )

    arrival_sensitivity = sensitivity.get("passenger_arrival_variability", {})
    volume_sensitivity = sensitivity.get("passenger_volume", {})
    transfer_fixed = sensitivity.get("transfer_fixed_delay", {})
    transfer_per_passenger = sensitivity.get("transfer_per_passenger_delay", {})
    behavior_rows = [
        _behavior_row(
            profile_id="pilot_default_behavior",
            region_id=region_id,
            behavior_class="concentrated_arrival",
            model_field="lateness.sigma",
            baseline_value=_field(arrival_sensitivity, "baseline", "0.25"),
            sensitivity_low=_field(arrival_sensitivity, "low", "0.15"),
            sensitivity_high=_field(arrival_sensitivity, "high", "0.50"),
            implementation_status="represented_by_lognormal_sigma_sensitivity",
            denominator_treatment="total_scenario_demand",
            source_class="sensitivity-only",
            source_name="Sensitivity design arrival-tail row",
            source_url_or_citation="data/scenarios/sensitivity_design.csv",
            evidence_status="bounded_sensitivity_not_observed_behavior",
            notes="Low sigma represents more concentrated arrivals in the current fixture.",
        ),
        _behavior_row(
            profile_id="pilot_default_behavior",
            region_id=region_id,
            behavior_class="staggered_arrival",
            model_field="policy_id=staggered_or_adaptive_dispatch",
            baseline_value="policy scenario",
            sensitivity_low="",
            sensitivity_high="",
            implementation_status="represented_by_policy_alternative",
            denominator_treatment="total_scenario_demand",
            source_class="scenario-only",
            source_name="Policy alternative dispatch scenario",
            source_url_or_citation="data/scenarios/policy_alternatives.csv",
            evidence_status="scenario_policy_not_behavior_calibration",
            notes="Dispatch staggering is a policy scenario, not observed traveler behavior.",
        ),
        _behavior_row(
            profile_id="pilot_default_behavior",
            region_id=region_id,
            behavior_class="heavy_tailed_lateness",
            model_field="lateness.sigma",
            baseline_value=_field(arrival_sensitivity, "baseline", "0.25"),
            sensitivity_low=_field(arrival_sensitivity, "low", "0.15"),
            sensitivity_high=_field(arrival_sensitivity, "high", "0.50"),
            implementation_status="represented_by_lognormal_sigma_sensitivity",
            denominator_treatment="total_scenario_demand",
            source_class="sensitivity-only",
            source_name="Sensitivity design arrival-tail row",
            source_url_or_citation="data/scenarios/sensitivity_design.csv",
            evidence_status="bounded_sensitivity_not_observed_behavior",
            notes="High sigma represents heavier late-arrival tails in the current fixture.",
        ),
        _behavior_row(
            profile_id="pilot_default_behavior",
            region_id=region_id,
            behavior_class="partial_non_arrival",
            model_field="no_show_fraction",
            baseline_value="0",
            sensitivity_low="0",
            sensitivity_high="0",
            implementation_status="not_implemented_contract_pending",
            denominator_treatment="not separated; all passengers are instantiated and non-completion is metric censoring",
            source_class="not_implemented",
            source_name="Phase 5 behavior contract review",
            source_url_or_citation="docs/recovery/transport_core_reconstruction_decision_20260602.md",
            evidence_status="blocked_until_behavior_contract",
            notes=(
                "Do not reconstruct compact non-arrival scripts until denominator "
                "semantics are reviewed."
            ),
        ),
        _behavior_row(
            profile_id="pilot_default_behavior",
            region_id=region_id,
            behavior_class="boarding_delay",
            model_field="multimodal.transfer_time_min; multimodal.transfer_per_passenger_min",
            baseline_value=(
                f"{_field(transfer_fixed, 'baseline', '3')} fixed; "
                f"{_field(transfer_per_passenger, 'baseline', '0.02')} per passenger"
            ),
            sensitivity_low=(
                f"{_field(transfer_fixed, 'low', '0')}; "
                f"{_field(transfer_per_passenger, 'low', '0')}"
            ),
            sensitivity_high=(
                f"{_field(transfer_fixed, 'high', '10')}; "
                f"{_field(transfer_per_passenger, 'high', '0.10')}"
            ),
            implementation_status="represented_by_transfer_delay_sensitivity",
            denominator_treatment="total_scenario_demand",
            source_class="sensitivity-only",
            source_name="Transfer delay sensitivity rows",
            source_url_or_citation="data/scenarios/sensitivity_design.csv",
            evidence_status="proxy_only_not_boarding_observation",
            notes="Transfer delay is a proxy for boarding or station processing burden.",
        ),
        _behavior_row(
            profile_id="pilot_default_behavior",
            region_id=region_id,
            behavior_class="volume_stress",
            model_field="personnel.total",
            baseline_value=_field(volume_sensitivity, "baseline", "24"),
            sensitivity_low=_field(volume_sensitivity, "low", "16"),
            sensitivity_high=_field(volume_sensitivity, "high", "32"),
            implementation_status="represented_by_sensitivity_design",
            denominator_treatment="total_scenario_demand",
            source_class="sensitivity-only",
            source_name="Sensitivity design passenger-volume row",
            source_url_or_citation="data/scenarios/sensitivity_design.csv",
            evidence_status="bounded_sensitivity_not_demand_forecast",
            notes="Fixture-scale passenger-volume stress is not calibrated demand.",
        ),
    ]

    return {
        "demand": demand_rows,
        "fleet": fleet_rows,
        "behavior": behavior_rows,
    }


def write_phase5_profile_packet(
    *,
    rows: Mapping[str, Sequence[Mapping[str, str]]],
    demand_path: str | Path = DEFAULT_DEMAND_PROFILE_PATH,
    fleet_path: str | Path = DEFAULT_FLEET_PROFILE_PATH,
    behavior_path: str | Path = DEFAULT_BEHAVIOR_PROFILE_PATH,
    manifest_path: str | Path = DEFAULT_PROFILE_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_PROFILE_DOC_PATH,
    input_paths: Sequence[str | Path] = (
        DEFAULT_CONFIG_PATH,
        DEFAULT_REGION_PATH,
        DEFAULT_PILOT_DESIGN_PATH,
        DEFAULT_SENSITIVITY_DESIGN_PATH,
        DEFAULT_POLICY_ALTERNATIVES_PATH,
        DEFAULT_FLEET_ASSUMPTIONS_PATH,
        DEFAULT_PILOT_EXPERIMENTS_SOURCE_PATH,
        DEFAULT_RECOVERY_DECISION_PATH,
    ),
) -> dict[str, Any]:
    """Write Phase 5 profile CSVs, manifest, and Markdown document."""

    demand = [dict(row) for row in rows["demand"]]
    fleet = [dict(row) for row in rows["fleet"]]
    behavior = [dict(row) for row in rows["behavior"]]
    _validate_demand_rows(demand)
    _validate_fleet_rows(fleet)
    _validate_behavior_rows(behavior)
    _validate_flag_columns(demand + fleet + behavior)

    _write_csv(Path(demand_path), DEMAND_PROFILE_COLUMNS, demand)
    _write_csv(Path(fleet_path), FLEET_PROFILE_COLUMNS, fleet)
    _write_csv(Path(behavior_path), BEHAVIOR_PROFILE_COLUMNS, behavior)

    manifest = build_phase5_profile_manifest(
        demand_rows=demand,
        fleet_rows=fleet,
        behavior_rows=behavior,
        demand_path=demand_path,
        fleet_path=fleet_path,
        behavior_path=behavior_path,
        manifest_path=manifest_path,
        doc_path=doc_path,
        input_paths=input_paths,
    )
    Path(manifest_path).parent.mkdir(parents=True, exist_ok=True)
    Path(manifest_path).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    Path(doc_path).parent.mkdir(parents=True, exist_ok=True)
    Path(doc_path).write_text(
        build_phase5_profile_markdown(manifest, rows=rows),
        encoding="utf-8",
    )
    return manifest


def build_phase5_profile_manifest(
    *,
    demand_rows: Sequence[Mapping[str, str]],
    fleet_rows: Sequence[Mapping[str, str]],
    behavior_rows: Sequence[Mapping[str, str]],
    demand_path: str | Path = DEFAULT_DEMAND_PROFILE_PATH,
    fleet_path: str | Path = DEFAULT_FLEET_PROFILE_PATH,
    behavior_path: str | Path = DEFAULT_BEHAVIOR_PROFILE_PATH,
    manifest_path: str | Path = DEFAULT_PROFILE_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_PROFILE_DOC_PATH,
    input_paths: Sequence[str | Path] = (
        DEFAULT_CONFIG_PATH,
        DEFAULT_REGION_PATH,
        DEFAULT_PILOT_DESIGN_PATH,
        DEFAULT_SENSITIVITY_DESIGN_PATH,
        DEFAULT_POLICY_ALTERNATIVES_PATH,
        DEFAULT_FLEET_ASSUMPTIONS_PATH,
        DEFAULT_PILOT_EXPERIMENTS_SOURCE_PATH,
        DEFAULT_RECOVERY_DECISION_PATH,
    ),
) -> dict[str, Any]:
    """Return a conservative Phase 5 profile manifest."""

    all_rows = [*demand_rows, *fleet_rows, *behavior_rows]
    return {
        "schema_version": 1,
        "result_scope": PROFILE_SCOPE,
        "claim_boundary": PROFILE_SCOPE,
        "publication_ready": False,
        "final_study_ready": False,
        "formal_acceptance_evidence": False,
        "can_mark_complete": False,
        "can_support_parameter_evidence_gate": False,
        "can_support_acceptance_gate": False,
        "can_support_publication_gate": False,
        "can_support_final_study_gate": False,
        "row_counts": {
            "demand": len(demand_rows),
            "fleet": len(fleet_rows),
            "behavior": len(behavior_rows),
        },
        "profile_ids": {
            "demand": sorted({row["profile_id"] for row in demand_rows}),
            "fleet": sorted({row["profile_id"] for row in fleet_rows}),
            "behavior": sorted({row["profile_id"] for row in behavior_rows}),
        },
        "demand_origin_share_sums": _origin_share_sums(demand_rows),
        "runtime_profile_consumption": {
            "pilot_experiments_consumes_profiles": True,
            "runtime_consumer": "src/realworld/pilot_experiments.py",
            "consumption_scope": (
                "pilot_default demand and fleet rows are consumed as bounded "
                "runtime inputs; this is not calibration, operating roster "
                "evidence, publication readiness, final-study readiness, or "
                "formal acceptance"
            ),
        },
        "evidence_status_counts": _counts(
            row.get("evidence_status", "") for row in all_rows
        ),
        "source_class_counts": _counts(row.get("source_class", "") for row in all_rows),
        "behavior_implementation_status_counts": _counts(
            row.get("implementation_status", "") for row in behavior_rows
        ),
        "inputs": {
            _display_path(path): file_sha256(Path(path))
            for path in input_paths
            if Path(path).exists()
        },
        "outputs": {
            "demand_profiles": _display_path(demand_path),
            "fleet_profiles": _display_path(fleet_path),
            "behavior_profiles": _display_path(behavior_path),
            "manifest": _display_path(manifest_path),
            "doc": _display_path(doc_path),
        },
        "review_items": [
            "review total demand, origin split, and arrival distribution before compact results consume final claims",
            "review fleet counts, vehicle capacities, dispatch intervals, and turnaround by role",
            "define no-show and partial non-arrival denominator semantics before reimplementing compact non-arrival scripts",
            "keep profile rows bounded scenario assumptions unless source-backed evidence or formal parameter acceptance is added",
            "verify any non-default profile before it is consumed by pilot_experiments.py",
        ],
        "remaining_blockers": [
            "demand profiles are not calibrated OD demand",
            "fleet profiles are not agency fleet rosters or operating timetables",
            "partial non-arrival semantics are not implemented in the scenario engine",
            "formal parameter acceptance remains absent",
        ],
    }


def build_phase5_profile_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Mapping[str, Sequence[Mapping[str, str]]],
) -> str:
    """Return a Markdown summary for Phase 5 profile review."""

    lines = [
        "# Demand, Fleet, And Behavior Profiles",
        "",
        str(manifest.get("claim_boundary", PROFILE_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Final-study ready: `{str(manifest.get('final_study_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Row counts: `{manifest.get('row_counts', {})}`",
        f"- Profile IDs: `{manifest.get('profile_ids', {})}`",
        "",
        "## Demand Profiles",
        "",
    ]
    for row in rows["demand"]:
        lines.append(
            f"- `{row['profile_id']}` origin `{row['origin_id']}`: "
            f"{row['total_demand_pax']} pax, distribution `{row['arrival_distribution']}`, "
            f"evidence `{row['evidence_status']}`."
        )
    lines.extend(["", "## Fleet Profiles", ""])
    for row in rows["fleet"]:
        lines.append(
            f"- `{row['profile_id']}` role `{row['role']}`: "
            f"fleet {row['fleet_size']}, capacity {row['vehicle_capacity_pax']}, "
            f"dispatch {row['dispatch_interval_min']} min, turnaround {row['turnaround_min']} min."
        )
    lines.extend(["", "## Behavior Profiles", ""])
    for row in rows["behavior"]:
        lines.append(
            f"- `{row['behavior_class']}`: `{row['implementation_status']}`; "
            f"denominator `{row['denominator_treatment']}`."
        )
    lines.extend(["", "## Remaining Blockers", ""])
    lines.extend(f"- {item}" for item in manifest.get("remaining_blockers", []))
    lines.append("")
    return "\n".join(lines)


def _demand_row(**kwargs: str) -> dict[str, str]:
    return {
        **{column: "" for column in DEMAND_PROFILE_COLUMNS},
        **kwargs,
        "can_support_parameter_evidence_gate": "false",
        "can_support_acceptance_gate": "false",
        "claim_boundary": PROFILE_SCOPE,
    }


def _fleet_row(**kwargs: str) -> dict[str, str]:
    return {
        **{column: "" for column in FLEET_PROFILE_COLUMNS},
        **kwargs,
        "can_support_parameter_evidence_gate": "false",
        "can_support_acceptance_gate": "false",
        "claim_boundary": PROFILE_SCOPE,
    }


def _behavior_row(**kwargs: str) -> dict[str, str]:
    return {
        **{column: "" for column in BEHAVIOR_PROFILE_COLUMNS},
        **kwargs,
        "can_support_parameter_evidence_gate": "false",
        "can_support_acceptance_gate": "false",
        "claim_boundary": PROFILE_SCOPE,
    }


def _fleet_rows_for_config(
    *,
    profile_id: str,
    region_id: str,
    config: Mapping[str, Any],
    source_class: str,
    source_name: str,
    source_url_or_citation: str,
    evidence_status: str,
) -> list[dict[str, str]]:
    group_size = _config_value(config, ("personnel", "group_size"))
    return [
        _fleet_row(
            profile_id=profile_id,
            region_id=region_id,
            role="direct_bus",
            vehicle_capacity_pax=group_size,
            fleet_size=_config_value(config, ("bus", "fleet_size")),
            dispatch_interval_min=_config_value(
                config,
                ("bus", "dispatch_interval_min"),
            ),
            first_departure_min=_config_value(config, ("bus", "first_departure_min")),
            turnaround_min=_config_value(config, ("bus", "turnaround_min")),
            source_class=source_class,
            source_name=source_name,
            source_url_or_citation=source_url_or_citation,
            evidence_status=evidence_status,
            notes="Finite fleet role used by the simulator; not an operating roster.",
        ),
        _fleet_row(
            profile_id=profile_id,
            region_id=region_id,
            role="feeder_shuttle",
            vehicle_capacity_pax=group_size,
            fleet_size=_config_value(config, ("multimodal", "shuttle_fleet_size")),
            dispatch_interval_min=_config_value(
                config,
                ("multimodal", "shuttle_dispatch_interval_min"),
            ),
            first_departure_min=_config_value(
                config,
                ("multimodal", "shuttle_first_departure_min"),
            ),
            turnaround_min=_config_value(
                config,
                ("multimodal", "shuttle_turnaround_min"),
                fallback="5.0",
            ),
            source_class=source_class,
            source_name=source_name,
            source_url_or_citation=source_url_or_citation,
            evidence_status=evidence_status,
            notes=(
                "Feeder fleet role used by the simulator; shuttle turnaround "
                "may rely on the scenario default if absent from config."
            ),
        ),
        _fleet_row(
            profile_id=profile_id,
            region_id=region_id,
            role="last_mile",
            vehicle_capacity_pax=_config_value(
                config,
                ("multimodal", "lastmile_vehicle_capacity"),
                fallback=group_size,
            ),
            fleet_size=_config_value(config, ("multimodal", "lastmile_fleet_size")),
            dispatch_interval_min=_config_value(
                config,
                ("multimodal", "lastmile_dispatch_interval_min"),
            ),
            first_departure_min=_config_value(
                config,
                ("multimodal", "lastmile_first_departure_min"),
                fallback="after_rail_arrival",
            ),
            turnaround_min=_config_value(
                config,
                ("multimodal", "lastmile_turnaround_min"),
            ),
            source_class=source_class,
            source_name=source_name,
            source_url_or_citation=source_url_or_citation,
            evidence_status=evidence_status,
            notes="Last-mile fleet role used by the simulator; not an operating roster.",
        ),
    ]


def _validate_demand_rows(rows: Sequence[Mapping[str, str]]) -> None:
    seen: set[tuple[str, str]] = set()
    for row in rows:
        key = (row["profile_id"], row["origin_id"])
        if key in seen:
            raise ValueError(f"duplicate demand profile origin row: {key}")
        seen.add(key)
        total = _float(row["total_demand_pax"])
        if total <= 0:
            raise ValueError(f"demand must be positive for {key}")
        share = _float(row["origin_share"])
        if share < 0 or share > 1:
            raise ValueError(f"origin share must be in [0,1] for {key}")
        if not row.get("arrival_distribution"):
            raise ValueError(f"arrival_distribution is required for {key}")
        if not row.get("arrival_param_sigma"):
            raise ValueError(f"arrival_param_sigma is required for {key}")
        if not row.get("completion_denominator"):
            raise ValueError(f"completion_denominator is required for {key}")
        for column in ("no_show_fraction", "late_arrival_fraction"):
            value = _float(row[column])
            if value < 0 or value > 1:
                raise ValueError(f"{column} must be in [0,1] for {key}")
        for column in ("source_class", "evidence_status", "claim_boundary"):
            if not row.get(column):
                raise ValueError(f"{column} is required for {key}")
    for profile_id, share_sum in _origin_share_sums(rows).items():
        if abs(float(share_sum) - 1.0) > 1e-6:
            raise ValueError(f"origin shares for {profile_id} sum to {share_sum}")


def _validate_fleet_rows(rows: Sequence[Mapping[str, str]]) -> None:
    seen: set[tuple[str, str]] = set()
    for row in rows:
        key = (row["profile_id"], row["role"])
        if key in seen:
            raise ValueError(f"duplicate fleet profile role row: {key}")
        seen.add(key)
        for column in ("source_class", "evidence_status", "claim_boundary"):
            if not row.get(column):
                raise ValueError(f"{column} is required for {key}")
        for column in ("vehicle_capacity_pax", "fleet_size"):
            value = _float(row[column])
            if value <= 0:
                raise ValueError(f"{column} must be positive for {key}")
        for column in ("dispatch_interval_min", "turnaround_min"):
            value = _float(row[column])
            if value < 0:
                raise ValueError(f"{column} must be non-negative for {key}")


def _validate_behavior_rows(rows: Sequence[Mapping[str, str]]) -> None:
    seen: set[tuple[str, str]] = set()
    for row in rows:
        key = (row["profile_id"], row["behavior_class"])
        if key in seen:
            raise ValueError(f"duplicate behavior profile row: {key}")
        seen.add(key)
        for column in (
            "model_field",
            "baseline_value",
            "implementation_status",
            "denominator_treatment",
            "source_class",
            "evidence_status",
            "claim_boundary",
        ):
            if not row.get(column):
                raise ValueError(f"{column} is required for {key}")


def _validate_flag_columns(rows: Sequence[Mapping[str, str]]) -> None:
    for row in rows:
        for column in ("can_support_parameter_evidence_gate", "can_support_acceptance_gate"):
            if str(row.get(column, "")).lower() != "false":
                raise ValueError(f"{column} must remain false for {row}")


def _write_csv(
    path: Path,
    fieldnames: Sequence[str],
    rows: Sequence[Mapping[str, str]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: str(row.get(field, "")) for field in fieldnames})


def _read_yaml_object(path: str | Path) -> dict[str, Any]:
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected YAML object: {path}")
    return value


def _read_json_object(path: str | Path) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _sensitivity_by_id(path: str | Path) -> dict[str, dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        return {
            str(row.get("parameter_id", "")): {
                str(key): str(value or "") for key, value in row.items()
            }
            for row in csv.DictReader(handle)
            if str(row.get("parameter_id", ""))
        }


def _config_value(
    config: Mapping[str, Any],
    path: Sequence[str],
    *,
    fallback: str = "",
) -> str:
    value: Any = config
    for key in path:
        if not isinstance(value, Mapping) or key not in value or value[key] is None:
            return fallback
        value = value[key]
    return str(value)


def _config_list(config: Mapping[str, Any], path: Sequence[str]) -> list[Any]:
    value: Any = config
    for key in path:
        if not isinstance(value, Mapping) or key not in value:
            return []
        value = value[key]
    return list(value) if isinstance(value, list) else []


def _first_config_list_value(config: Mapping[str, Any], path: Sequence[str]) -> str:
    values = _config_list(config, path)
    return str(values[0]) if values else ""


def _field(row: Mapping[str, str], key: str, fallback: str = "") -> str:
    return str(row.get(key) or fallback)


def _origin_share_sums(rows: Sequence[Mapping[str, str]]) -> dict[str, str]:
    sums: dict[str, float] = defaultdict(float)
    for row in rows:
        sums[row["profile_id"]] += _float(row["origin_share"])
    return {key: f"{value:.6g}" for key, value in sorted(sums.items())}


def _counts(values: Sequence[str] | Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"expected numeric value, got {value!r}") from exc


def _display_path(path: str | Path) -> str:
    value = Path(path)
    try:
        return str(value.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(value)


__all__ = [
    "BEHAVIOR_PROFILE_COLUMNS",
    "DEFAULT_BEHAVIOR_PROFILE_PATH",
    "DEFAULT_DEMAND_PROFILE_PATH",
    "DEFAULT_FLEET_ASSUMPTIONS_PATH",
    "DEFAULT_FLEET_PROFILE_PATH",
    "DEFAULT_PILOT_EXPERIMENTS_SOURCE_PATH",
    "DEFAULT_POLICY_ALTERNATIVES_PATH",
    "DEFAULT_PROFILE_DOC_PATH",
    "DEFAULT_PROFILE_MANIFEST_PATH",
    "DEFAULT_RECOVERY_DECISION_PATH",
    "DEMAND_PROFILE_COLUMNS",
    "FLEET_PROFILE_COLUMNS",
    "PROFILE_SCOPE",
    "build_phase5_profile_manifest",
    "build_phase5_profile_markdown",
    "build_phase5_profile_rows",
    "write_phase5_profile_packet",
]
