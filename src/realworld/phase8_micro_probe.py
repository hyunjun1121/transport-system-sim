"""Phase 8 executable micro-probe wrapper.

This module freezes the smallest allowed Phase 8 pilot execution slice before
compact or full experiments. It records execution checks separately from any
publication, formal-acceptance, or final-study claim.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
import hashlib
from pathlib import Path
from typing import Any, Mapping

from src.realworld.pilot_experiments import (
    DEFAULT_STAGED_PROFILE_ID,
    run_pilot_experiments,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PHASE8_MICRO_PROBE_ID = "phase8_micro_probe"
PHASE8_MICRO_PROBE_SCOPE = (
    "Phase 8 executable micro-probe only; not compact evidence, not calibrated "
    "real-world results, not publication readiness, not final-study approval, "
    "and not formal acceptance."
)
MICRO_PROBE_PROFILE_ID = DEFAULT_STAGED_PROFILE_ID
MICRO_PROBE_SEEDS = (2101,)
MICRO_PROBE_POLICY_IDS = ("bus_only", "baseline_multimodal")
MICRO_PROBE_SCENARIO_IDS = ("songpa_last_mile_station_to_destination",)
MICRO_PROBE_EXPECTED_ROW_COUNT = (
    len(MICRO_PROBE_SEEDS) * len(MICRO_PROBE_POLICY_IDS) * len(MICRO_PROBE_SCENARIO_IDS)
)
MICRO_PROBE_EXPECTED_SUMMARY_ROW_COUNT = (
    len(MICRO_PROBE_POLICY_IDS) * len(MICRO_PROBE_SCENARIO_IDS)
)
MICRO_PROBE_ROUTE_SCOPE = {
    "road_paths": ["A->D", "A->S", "R->D"],
    "rail_or_transit_paths": ["S->R"],
    "disruption_target_segment": "R->D",
    "graph_reduction_strategy": "single_corridor",
}
DEFAULT_MICRO_PROBE_OUTPUT_DIR = (
    PROJECT_ROOT / "results" / "realworld_pilot" / PHASE8_MICRO_PROBE_ID
)
DEFAULT_MICRO_PROBE_RERUN_OUTPUT_DIR = (
    PROJECT_ROOT
    / "results"
    / "realworld_pilot"
    / f"{PHASE8_MICRO_PROBE_ID}_deterministic_rerun"
)
DEFAULT_MICRO_PROBE_MANIFEST_PATH = (
    DEFAULT_MICRO_PROBE_OUTPUT_DIR / f"{PHASE8_MICRO_PROBE_ID}_manifest.json"
)


def run_phase8_micro_probe(
    *,
    output_dir: str | Path = DEFAULT_MICRO_PROBE_OUTPUT_DIR,
    rerun_output_dir: str | Path = DEFAULT_MICRO_PROBE_RERUN_OUTPUT_DIR,
    manifest_path: str | Path = DEFAULT_MICRO_PROBE_MANIFEST_PATH,
    runtime_preflight_manifest_path: str | Path | None = None,
) -> dict[str, Any]:
    """Run the frozen one-worker, one-seed Phase 8 micro-probe twice."""

    output_dir = Path(output_dir)
    rerun_output_dir = Path(rerun_output_dir)
    manifest_path = Path(manifest_path)
    if output_dir.resolve() == rerun_output_dir.resolve():
        raise ValueError("output_dir and rerun_output_dir must be different")

    primary = _run_frozen_profile(output_dir)
    rerun = _run_frozen_profile(rerun_output_dir)
    runtime_preflight = _runtime_preflight_snapshot(runtime_preflight_manifest_path)
    manifest = build_phase8_micro_probe_manifest(
        primary=primary,
        rerun=rerun,
        output_dir=output_dir,
        rerun_output_dir=rerun_output_dir,
        runtime_preflight=runtime_preflight,
    )
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest["manifest_path"] = _display_path(manifest_path)
    manifest["manifest_self_hash_policy"] = (
        "The wrapper manifest SHA256 is reported by the caller after write; it "
        "is not embedded in the manifest to avoid self-referential hashing."
    )
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "manifest": manifest,
        "manifest_path": manifest_path,
        "manifest_sha256": _file_sha256(manifest_path),
        "primary": primary,
        "rerun": rerun,
    }


def build_phase8_micro_probe_manifest(
    *,
    primary: Mapping[str, Any],
    rerun: Mapping[str, Any],
    output_dir: Path,
    rerun_output_dir: Path,
    runtime_preflight: Mapping[str, Any],
) -> dict[str, Any]:
    """Return the deterministic execution-check manifest for the micro-probe."""

    primary_manifest = dict(primary["manifest"])
    rerun_manifest = dict(rerun["manifest"])
    primary_profile_application = _profile_application(primary_manifest)
    rerun_profile_application = _profile_application(rerun_manifest)
    primary_results_hash = _file_sha256(primary["results_path"])
    rerun_results_hash = _file_sha256(rerun["results_path"])
    primary_summary_hash = _file_sha256(primary["summary_path"])
    rerun_summary_hash = _file_sha256(rerun["summary_path"])

    checks = {
        "profile_id_frozen": primary_manifest.get("run_profile") == MICRO_PROBE_PROFILE_ID,
        "engineering_only_boundary": bool(primary_manifest.get("engineering_only")) is True,
        "worker_count_is_one": (
            primary_manifest.get("runtime", {}).get("actual_worker_count") == 1
            and rerun_manifest.get("runtime", {}).get("actual_worker_count") == 1
        ),
        "row_count_matches": (
            primary_manifest.get("row_count") == MICRO_PROBE_EXPECTED_ROW_COUNT
            and rerun_manifest.get("row_count") == MICRO_PROBE_EXPECTED_ROW_COUNT
        ),
        "summary_row_count_matches": (
            primary_manifest.get("summary_row_count")
            == MICRO_PROBE_EXPECTED_SUMMARY_ROW_COUNT
            and rerun_manifest.get("summary_row_count")
            == MICRO_PROBE_EXPECTED_SUMMARY_ROW_COUNT
        ),
        "policy_ids_frozen": tuple(primary_manifest.get("policy_ids", ()))
        == MICRO_PROBE_POLICY_IDS,
        "scenario_ids_frozen": tuple(primary_manifest.get("scenario_ids", ()))
        == MICRO_PROBE_SCENARIO_IDS,
        "seeds_frozen": tuple(primary_manifest.get("seeds", ())) == MICRO_PROBE_SEEDS,
        "profile_inputs_consumed": (
            primary_profile_application.get("runtime_profile_inputs_consumed") is True
            and rerun_profile_application.get("runtime_profile_inputs_consumed") is True
        ),
        "profile_input_hashes_match": (
            primary_profile_application.get("demand_profiles_sha256")
            == rerun_profile_application.get("demand_profiles_sha256")
            and primary_profile_application.get("fleet_profiles_sha256")
            == rerun_profile_application.get("fleet_profiles_sha256")
        ),
        "profile_ids_match_design": (
            primary_profile_application.get("demand_profile_id")
            == "pilot_default_demand"
            and primary_profile_application.get("fleet_profile_id")
            == "pilot_default_fleet"
        ),
        "deterministic_results_hash_match": primary_results_hash == rerun_results_hash,
        "deterministic_summary_hash_match": primary_summary_hash == rerun_summary_hash,
        "runtime_preflight_ready_for_micro_probe": bool(
            runtime_preflight.get("runtime_preflight_ready_for_micro_probe", False)
        ),
        "non_publication_boundary": (
            primary_manifest.get("publication_ready") is False
            and primary_manifest.get("final_study_ready") is False
            and primary_manifest.get("formal_acceptance_evidence") is False
        ),
    }
    execution_blockers = [
        f"{name} failed" for name, passed in checks.items() if not bool(passed)
    ]
    promotion_blockers = _promotion_blockers(primary_manifest)
    return {
        "schema_version": 1,
        "phase_id": PHASE8_MICRO_PROBE_ID,
        "generated_at": _utc_now(),
        "result_scope": PHASE8_MICRO_PROBE_SCOPE,
        "claim_boundary": PHASE8_MICRO_PROBE_SCOPE,
        "profile_id": MICRO_PROBE_PROFILE_ID,
        "run_stage": primary_manifest.get("run_stage"),
        "worker_count": 1,
        "r_equivalent": 1,
        "common_random_number_pair_count": 1,
        "seeds": list(MICRO_PROBE_SEEDS),
        "policy_ids": list(MICRO_PROBE_POLICY_IDS),
        "scenario_ids": list(MICRO_PROBE_SCENARIO_IDS),
        "route_scope": dict(MICRO_PROBE_ROUTE_SCOPE),
        "expected_row_count": MICRO_PROBE_EXPECTED_ROW_COUNT,
        "actual_row_count": primary_manifest.get("row_count"),
        "expected_summary_row_count": MICRO_PROBE_EXPECTED_SUMMARY_ROW_COUNT,
        "actual_summary_row_count": primary_manifest.get("summary_row_count"),
        "pass_fail_rules": {
            "row_count": "must equal 2 rows: two policies x one scenario x one seed",
            "summary_row_count": "must equal 2 rows: two policies x one scenario",
            "worker_count": "primary and deterministic rerun must both report one worker",
            "deterministic_rerun": "primary and rerun result/summary CSV SHA256 values must match",
            "profile_inputs": (
                "primary and rerun pilot manifests must prove Phase 5 "
                "demand/fleet profile CSVs were consumed with matching hashes"
            ),
            "runtime_preflight": (
                "runtime preflight manifest must exist, be ready, and use "
                "execution_scope=micro_probe"
            ),
            "claim_boundary": (
                "outputs must remain non-publication, non-final-study, "
                "non-formal-acceptance, and non-operational"
            ),
        },
        "checks": checks,
        "execution_blockers": execution_blockers,
        "micro_probe_execution_ready": not execution_blockers,
        "promotion_ready": False,
        "promotion_blockers": promotion_blockers,
        "can_mark_complete": False,
        "publication_ready": False,
        "final_study_ready": False,
        "formal_acceptance_evidence": False,
        "operational_use_allowed": False,
        "runtime_preflight": dict(runtime_preflight),
        "profile_runtime_inputs": {
            "primary": _profile_runtime_input_record(primary_profile_application),
            "deterministic_rerun": _profile_runtime_input_record(rerun_profile_application),
        },
        "primary_outputs": {
            "output_dir": _display_path(output_dir),
            "results": _path_record(primary["results_path"]),
            "summary": _path_record(primary["summary_path"]),
            "pilot_manifest": _path_record(primary["manifest_path"]),
            "output_lock_receipt": _path_record(primary["output_lock_receipt_path"]),
        },
        "deterministic_rerun_outputs": {
            "output_dir": _display_path(rerun_output_dir),
            "results": _path_record(rerun["results_path"]),
            "summary": _path_record(rerun["summary_path"]),
            "pilot_manifest": _path_record(rerun["manifest_path"]),
            "output_lock_receipt": _path_record(rerun["output_lock_receipt_path"]),
        },
        "deterministic_comparison": {
            "primary_results_sha256": primary_results_hash,
            "rerun_results_sha256": rerun_results_hash,
            "primary_summary_sha256": primary_summary_hash,
            "rerun_summary_sha256": rerun_summary_hash,
        },
    }


def _run_frozen_profile(output_dir: Path) -> dict[str, Any]:
    return run_pilot_experiments(
        output_dir=output_dir,
        sample=False,
        run_profile=MICRO_PROBE_PROFILE_ID,
        seeds=MICRO_PROBE_SEEDS,
        policy_ids=MICRO_PROBE_POLICY_IDS,
        scenario_ids=MICRO_PROBE_SCENARIO_IDS,
        engineering_only=True,
    )


def _runtime_preflight_snapshot(path: str | Path | None) -> dict[str, Any]:
    if path is None:
        return {
            "path": None,
            "exists": False,
            "runtime_preflight_ready": False,
            "execution_scope": "",
            "runtime_preflight_ready_for_micro_probe": False,
            "remaining_blockers": ["runtime preflight manifest path was not provided"],
        }
    manifest_path = Path(path)
    if not manifest_path.exists():
        return {
            "path": _display_path(manifest_path),
            "exists": False,
            "runtime_preflight_ready": False,
            "execution_scope": "",
            "runtime_preflight_ready_for_micro_probe": False,
            "remaining_blockers": ["runtime preflight manifest is missing"],
        }
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "path": _display_path(manifest_path),
            "exists": True,
            "sha256": _file_sha256(manifest_path),
            "runtime_preflight_ready": False,
            "execution_scope": "",
            "runtime_preflight_ready_for_micro_probe": False,
            "remaining_blockers": [f"runtime preflight manifest could not be read: {exc}"],
        }
    remaining_blockers = manifest.get("remaining_blockers", [])
    if not isinstance(remaining_blockers, list):
        remaining_blockers = ["runtime preflight remaining_blockers is not a list"]
    ready = bool(manifest.get("runtime_preflight_ready", False))
    execution_scope = str(manifest.get("execution_scope", ""))
    ready_for_micro_probe = bool(ready and execution_scope == "micro_probe")
    return {
        "path": _display_path(manifest_path),
        "exists": True,
        "sha256": _file_sha256(manifest_path),
        "runtime_preflight_ready": ready,
        "execution_scope": execution_scope,
        "runtime_preflight_ready_for_micro_probe": ready_for_micro_probe,
        "remaining_blockers": remaining_blockers,
    }


def _promotion_blockers(manifest: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = [
        "micro-probe is execution evidence only and cannot promote compact/full outputs",
        "formal acceptance evidence is not created by this wrapper",
        "final study readiness remains outside this wrapper",
    ]
    if manifest.get("rail_source_decisions_pending"):
        blockers.append("rail source decisions remain pending")
    if manifest.get("artifact_invalidation_blocks_phase9"):
        blockers.append("artifact invalidation still blocks Phase 9 promotion")
    if manifest.get("engineering_only_bypass"):
        blockers.append("profile ran under engineering-only bypass")
    if not _profile_application(manifest).get("runtime_profile_inputs_consumed"):
        blockers.append("Phase 5 demand/fleet profiles were not consumed")
    return blockers


def _profile_application(manifest: Mapping[str, Any]) -> Mapping[str, Any]:
    application = manifest.get("profile_application", {})
    return application if isinstance(application, Mapping) else {}


def _profile_runtime_input_record(application: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "runtime_profile_inputs_consumed": bool(
            application.get("runtime_profile_inputs_consumed", False)
        ),
        "demand_profile_id": application.get("demand_profile_id"),
        "fleet_profile_id": application.get("fleet_profile_id"),
        "demand_profiles_path": application.get("demand_profiles_path"),
        "demand_profiles_sha256": application.get("demand_profiles_sha256"),
        "fleet_profiles_path": application.get("fleet_profiles_path"),
        "fleet_profiles_sha256": application.get("fleet_profiles_sha256"),
        "applied_field_count": application.get("applied_field_count"),
        "can_support_final_study_gate": application.get(
            "can_support_final_study_gate",
        ),
        "remaining_blockers": list(application.get("remaining_blockers", []))
        if isinstance(application.get("remaining_blockers", []), list)
        else [],
    }


def _path_record(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    return {
        "path": _display_path(file_path),
        "exists": file_path.exists(),
        "sha256": _file_sha256(file_path) if file_path.exists() else None,
    }


def _file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _display_path(path: str | Path) -> str:
    file_path = Path(path)
    try:
        return str(file_path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(file_path)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


__all__ = [
    "DEFAULT_MICRO_PROBE_MANIFEST_PATH",
    "DEFAULT_MICRO_PROBE_OUTPUT_DIR",
    "DEFAULT_MICRO_PROBE_RERUN_OUTPUT_DIR",
    "MICRO_PROBE_EXPECTED_ROW_COUNT",
    "MICRO_PROBE_EXPECTED_SUMMARY_ROW_COUNT",
    "MICRO_PROBE_POLICY_IDS",
    "MICRO_PROBE_PROFILE_ID",
    "MICRO_PROBE_SCENARIO_IDS",
    "MICRO_PROBE_SEEDS",
    "PHASE8_MICRO_PROBE_ID",
    "PHASE8_MICRO_PROBE_SCOPE",
    "build_phase8_micro_probe_manifest",
    "run_phase8_micro_probe",
]
