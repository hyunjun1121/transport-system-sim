"""Seed-stream manifest for pilot experiment review.

This module documents the current stochastic streams used by the scenario
runner. It is review support only; it does not prove statistical adequacy,
approve common-random-number pairing, or close experiment decision review.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.realworld.manifest_timestamp import (
    preserve_generated_at_when_unchanged,
    write_json_manifest_if_changed,
    write_text_if_changed,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PILOT_FULL_MANIFEST_PATH = (
    PROJECT_ROOT / "results" / "realworld_pilot" / "pilot_full_manifest.json"
)
DEFAULT_SCENARIO_SOURCE_PATH = PROJECT_ROOT / "src" / "scenario.py"
DEFAULT_MODELS_SOURCE_PATH = PROJECT_ROOT / "src" / "models.py"
DEFAULT_DISRUPTIONS_SOURCE_PATH = PROJECT_ROOT / "src" / "disruptions.py"
DEFAULT_DISPATCH_SOURCE_PATH = PROJECT_ROOT / "src" / "dispatch.py"
DEFAULT_FLEET_SOURCE_PATH = PROJECT_ROOT / "src" / "fleet.py"
DEFAULT_RAIL_SOURCE_PATH = PROJECT_ROOT / "src" / "rail.py"
DEFAULT_TRANSFERS_SOURCE_PATH = PROJECT_ROOT / "src" / "transfers.py"
DEFAULT_TRAFFIC_SOURCE_PATH = PROJECT_ROOT / "src" / "traffic.py"
DEFAULT_SEED_STREAM_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "seed_stream_manifest.json"
)
DEFAULT_SEED_STREAM_DOC_PATH = PROJECT_ROOT / "docs" / "seed_stream_manifest.md"

SEED_STREAM_CLAIM_BOUNDARY = (
    "This seed-stream manifest documents current scenario-runner stochastic "
    "streams and deterministic dispatch components. It does not prove "
    "statistical power, accept CRN design, validate stochastic assumptions, or "
    "close final-study gates."
)


def build_seed_stream_manifest(
    *,
    pilot_manifest_path: str | Path = DEFAULT_PILOT_FULL_MANIFEST_PATH,
    scenario_source_path: str | Path = DEFAULT_SCENARIO_SOURCE_PATH,
    models_source_path: str | Path = DEFAULT_MODELS_SOURCE_PATH,
    disruptions_source_path: str | Path = DEFAULT_DISRUPTIONS_SOURCE_PATH,
    dispatch_source_path: str | Path = DEFAULT_DISPATCH_SOURCE_PATH,
    fleet_source_path: str | Path = DEFAULT_FLEET_SOURCE_PATH,
    rail_source_path: str | Path = DEFAULT_RAIL_SOURCE_PATH,
    transfers_source_path: str | Path = DEFAULT_TRANSFERS_SOURCE_PATH,
    traffic_source_path: str | Path = DEFAULT_TRAFFIC_SOURCE_PATH,
) -> dict[str, Any]:
    """Return a source-backed seed-stream manifest."""

    pilot_manifest_file = Path(pilot_manifest_path)
    scenario_file = Path(scenario_source_path)
    models_file = Path(models_source_path)
    disruptions_file = Path(disruptions_source_path)
    dispatch_file = Path(dispatch_source_path)
    fleet_file = Path(fleet_source_path)
    rail_file = Path(rail_source_path)
    transfers_file = Path(transfers_source_path)
    traffic_file = Path(traffic_source_path)

    pilot_manifest = _load_json_object(pilot_manifest_file)
    source_text = {
        "scenario": _read_text(scenario_file),
        "models": _read_text(models_file),
        "disruptions": _read_text(disruptions_file),
        "dispatch": _read_text(dispatch_file),
        "fleet": _read_text(fleet_file),
        "rail": _read_text(rail_file),
        "transfers": _read_text(transfers_file),
        "traffic": _read_text(traffic_file),
    }
    marker_checks = _marker_checks(source_text)
    stream_records = _stream_records(
        pilot_manifest=pilot_manifest,
        scenario_file=scenario_file,
        models_file=models_file,
        disruptions_file=disruptions_file,
        dispatch_file=dispatch_file,
        fleet_file=fleet_file,
        rail_file=rail_file,
        transfers_file=transfers_file,
        traffic_file=traffic_file,
    )
    blocking_checks = [row for row in marker_checks if row["status"] == "blocked"]
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "claim_boundary": SEED_STREAM_CLAIM_BOUNDARY,
        "pilot_manifest_path": _display_path(pilot_manifest_file),
        "run_profile": pilot_manifest.get("run_profile", ""),
        "region_id": pilot_manifest.get("region_id", ""),
        "graph_source": pilot_manifest.get("graph_source", ""),
        "seed_count": len(pilot_manifest.get("seeds", []) or []),
        "seeds": pilot_manifest.get("seeds", []) or [],
        "policy_ids": pilot_manifest.get("policy_ids", []) or [],
        "scenario_ids": pilot_manifest.get("scenario_ids", []) or [],
        "stream_records": stream_records,
        "stream_record_count": len(stream_records),
        "marker_checks": marker_checks,
        "blocking_check_count": len(blocking_checks),
        "seed_stream_manifest_ready": len(blocking_checks) == 0,
        "acceptance_ready": False,
        "publication_ready": False,
        "can_mark_complete": False,
        "remaining_blockers": [
            f"{row['check_id']}: {row['review_action']}" for row in blocking_checks
        ],
        "review_items": [
            "confirm demand and disruption streams are intentionally shared across policies by seed",
            "confirm deterministic dispatch and fleet components do not need additional RNG streams",
            "extend this manifest before adding stochastic dispatch, routing tie-breaking, or future sampling logic",
            "use with CRN pairing audit and paired-delta statistics before experiment decision review",
        ],
    }


def write_seed_stream_manifest(
    *,
    output_path: str | Path = DEFAULT_SEED_STREAM_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_SEED_STREAM_DOC_PATH,
    **kwargs: Any,
) -> dict[str, Any]:
    """Write the seed-stream JSON manifest and Markdown note."""

    manifest = build_seed_stream_manifest(**kwargs)
    output = Path(output_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)
    preserve_generated_at_when_unchanged(manifest, output)
    write_json_manifest_if_changed(manifest, output, sort_keys=True)
    write_text_if_changed(build_seed_stream_markdown(manifest), doc)
    return manifest


def build_seed_stream_markdown(manifest: Mapping[str, Any]) -> str:
    """Return a human-readable seed-stream note."""

    lines = [
        "# Seed Stream Manifest",
        "",
        str(manifest.get("claim_boundary", SEED_STREAM_CLAIM_BOUNDARY)),
        "",
        "## Verdict",
        "",
        f"- Seed-stream manifest ready: `{str(manifest.get('seed_stream_manifest_ready', False)).lower()}`",
        f"- Acceptance ready: `{str(manifest.get('acceptance_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Blocking checks: {manifest.get('blocking_check_count', 0)}",
        f"- Run profile: `{manifest.get('run_profile', '')}`",
        f"- Seed count: {manifest.get('seed_count', 0)}",
        "",
        "## Streams",
        "",
        "| Stream | Seed Rule | Consumer | Shared Across Policies | Evidence | Review Note |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in manifest.get("stream_records", []):
        if not isinstance(row, Mapping):
            continue
        lines.append(
            "| {stream} | {seed_rule} | {consumer} | {shared} | {evidence} | {note} |".format(
                stream=_cell(str(row.get("stream_id", ""))),
                seed_rule=_cell(str(row.get("seed_rule", ""))),
                consumer=_cell(str(row.get("consumer", ""))),
                shared=_cell(str(row.get("shared_across_policies", ""))),
                evidence=_cell(str(row.get("evidence_paths", ""))),
                note=_cell(str(row.get("review_note", ""))),
            )
        )
    lines.extend(["", "## Marker Checks", "", "| Check | Status | Review Action |", "| --- | --- | --- |"])
    for row in manifest.get("marker_checks", []):
        if not isinstance(row, Mapping):
            continue
        lines.append(
            "| {check} | {status} | {action} |".format(
                check=_cell(str(row.get("check_id", ""))),
                status=_cell(str(row.get("status", ""))),
                action=_cell(str(row.get("review_action", ""))),
            )
        )
    lines.extend(
        [
            "",
            "## Use",
            "",
            "Use this manifest with `docs/crn_pairing_audit.md` and the paired "
            "delta statistics tables before any formal experiment decision review. "
            "If stochastic dispatch tie-breaking, random routing, or additional "
            "sampling is added, update this manifest before interpreting policy "
            "differences.",
            "",
        ]
    )
    return "\n".join(lines)


def _stream_records(
    *,
    pilot_manifest: Mapping[str, Any],
    scenario_file: Path,
    models_file: Path,
    disruptions_file: Path,
    dispatch_file: Path,
    fleet_file: Path,
    rail_file: Path,
    transfers_file: Path,
    traffic_file: Path,
) -> list[dict[str, Any]]:
    policies = len(pilot_manifest.get("policy_ids", []) or [])
    scenarios = len(pilot_manifest.get("scenario_ids", []) or [])
    seeds = len(pilot_manifest.get("seeds", []) or [])
    shared_scope = (
        f"{policies} policies x {scenarios} scenarios x {seeds} seeds"
        if policies and scenarios and seeds
        else "pilot manifest dimensions unavailable"
    )
    return [
        {
            "stream_id": "demand_arrival_lateness",
            "stream_type": "stochastic",
            "seed_rule": "np.random.default_rng(seed)",
            "consumer": "sample_arrival_delays(..., rng=rng_arrival)",
            "distribution_or_logic": "LogNormal(mu, sigma) passenger arrival delays",
            "shared_across_policies": True,
            "shared_scope": shared_scope,
            "evidence_paths": "; ".join(
                _display_path(path) for path in (scenario_file, models_file)
            ),
            "review_note": "same scenario/seed rows across policies share the demand stream by construction",
        },
        {
            "stream_id": "road_disruption_sampling",
            "stream_type": "stochastic",
            "seed_rule": "np.random.default_rng(seed + 10_000)",
            "consumer": "_sample_disruptions(..., rng_failure)",
            "distribution_or_logic": "Bernoulli road-edge disruption draws using configured mode and probability scale",
            "shared_across_policies": True,
            "shared_scope": shared_scope,
            "evidence_paths": "; ".join(
                _display_path(path) for path in (scenario_file, disruptions_file)
            ),
            "review_note": "same scenario/seed rows across policies share the disruption stream by construction",
        },
        {
            "stream_id": "dispatch_and_fleet_ordering",
            "stream_type": "deterministic",
            "seed_rule": "not_applicable",
            "consumer": "plan_dispatches, FleetAvailability, rail headway, transfers, dynamic traffic",
            "distribution_or_logic": "sorted queues, policy thresholds, finite fleet availability, fixed schedules, BPR route traversal",
            "shared_across_policies": "not_random",
            "shared_scope": "deterministic conditional on passengers, policy, config, graph, and disruptions",
            "evidence_paths": "; ".join(
                _display_path(path)
                for path in (
                    scenario_file,
                    dispatch_file,
                    fleet_file,
                    rail_file,
                    transfers_file,
                    traffic_file,
                )
            ),
            "review_note": "no current random tie-breaking stream is present; add a named stream if stochastic dispatch logic is introduced",
        },
    ]


def _marker_checks(source_text: Mapping[str, str]) -> list[dict[str, str]]:
    return [
        _marker_check(
            "arrival_rng_seed_rule",
            "default_rng(seed)" in source_text["scenario"],
            "src/scenario.py declares rng_arrival from the scenario seed",
            "Restore or document the demand-stream seed rule.",
        ),
        _marker_check(
            "failure_rng_seed_rule",
            "default_rng(seed + 10_000)" in source_text["scenario"],
            "src/scenario.py declares rng_failure from seed + 10_000",
            "Restore or document the disruption-stream seed rule.",
        ),
        _marker_check(
            "arrival_rng_consumed_by_lognormal",
            "rng.lognormal" in source_text["models"],
            "src/models.py consumes the arrival RNG via lognormal sampling",
            "Review demand sampling implementation before CRN design signoff.",
        ),
        _marker_check(
            "disruption_rng_consumed_by_edge_draws",
            "rng.random()" in source_text["disruptions"],
            "src/disruptions.py consumes the disruption RNG for edge draws",
            "Review disruption sampling implementation before CRN design signoff.",
        ),
        _marker_check(
            "dispatch_has_no_rng_marker",
            "rng" not in source_text["dispatch"]
            and "random" not in source_text["dispatch"],
            "src/dispatch.py has no RNG marker",
            "Add a named dispatch stream before stochastic dispatch is introduced.",
        ),
        _marker_check(
            "fleet_rail_transfer_traffic_have_no_rng_marker",
            all(
                "rng" not in source_text[name] and "random" not in source_text[name]
                for name in ("fleet", "rail", "transfers", "traffic")
            ),
            "fleet, rail, transfers, and traffic modules have no RNG marker",
            "Add named streams before stochastic fleet, rail, transfer, or traffic logic is introduced.",
        ),
    ]


def _marker_check(
    check_id: str,
    ok: bool,
    observed: str,
    review_action: str,
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "status": "pass" if ok else "blocked",
        "observed": observed if ok else "marker missing or unexpected RNG marker present",
        "review_action": review_action,
    }


def _load_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _display_path(path: Path | str) -> str:
    filepath = Path(path)
    try:
        return filepath.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return filepath.as_posix()


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


__all__ = [
    "DEFAULT_SEED_STREAM_DOC_PATH",
    "DEFAULT_SEED_STREAM_MANIFEST_PATH",
    "SEED_STREAM_CLAIM_BOUNDARY",
    "build_seed_stream_manifest",
    "build_seed_stream_markdown",
    "write_seed_stream_manifest",
]
