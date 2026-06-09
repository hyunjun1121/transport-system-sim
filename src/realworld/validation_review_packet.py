"""Validation-package review packet generation.

This module summarizes current validation artifacts for human review. It helps
reviewers choose a validation and benchmark strategy, but it is not a
validation acceptance record and does not close any final-study gate.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.validation_acceptance import ALLOWED_BENCHMARK_STRATEGIES


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROUTE_PLAUSIBILITY_PATH = (
    PROJECT_ROOT / "data" / "validation" / "route_plausibility.csv"
)
DEFAULT_FALLBACK_BENCHMARK_PATH = (
    PROJECT_ROOT / "data" / "validation" / "external_route_benchmarks.csv"
)
DEFAULT_OSRM_BENCHMARK_PATH = (
    PROJECT_ROOT / "data" / "validation" / "external_route_benchmarks_osrm.csv"
)
DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "osrm_route_benchmark_manifest.json"
)
DEFAULT_ACCESSIBILITY_LOSS_PATH = (
    PROJECT_ROOT / "data" / "validation" / "accessibility_loss.csv"
)
DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_PATH = (
    PROJECT_ROOT / "data" / "validation" / "canonical_route_road_evidence_exposure.csv"
)
DEFAULT_VALIDATION_SUMMARY_PATH = (
    PROJECT_ROOT / "data" / "validation" / "validation_summary.md"
)
DEFAULT_VALIDATION_ACCEPTANCE_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "validation_acceptance.json"
)
DEFAULT_VALIDATION_REVIEW_PACKET_PATH = (
    PROJECT_ROOT / "data" / "validation" / "validation_review_packet.csv"
)
DEFAULT_VALIDATION_REVIEW_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "validation_review_manifest.json"
)

VALIDATION_REVIEW_PACKET_SCOPE = (
    "validation_review_packet_not_validation_acceptance"
)
VALIDATION_REVIEW_COLUMNS: tuple[str, ...] = (
    "category_id",
    "evidence_category",
    "artifact_path",
    "artifact_present",
    "row_count",
    "status_counts",
    "coverage_counts",
    "review_status",
    "review_required",
    "acceptance_ready",
    "publication_ready",
    "review_action",
    "publication_use_status",
    "claim_boundary",
)


def build_validation_review_rows(
    *,
    route_plausibility_path: str | Path = DEFAULT_ROUTE_PLAUSIBILITY_PATH,
    fallback_benchmark_path: str | Path = DEFAULT_FALLBACK_BENCHMARK_PATH,
    osrm_benchmark_path: str | Path = DEFAULT_OSRM_BENCHMARK_PATH,
    osrm_benchmark_manifest_path: str | Path = DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH,
    accessibility_loss_path: str | Path = DEFAULT_ACCESSIBILITY_LOSS_PATH,
    route_road_evidence_exposure_path: str | Path = DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_PATH,
    validation_summary_path: str | Path = DEFAULT_VALIDATION_SUMMARY_PATH,
    validation_acceptance_path: str | Path = DEFAULT_VALIDATION_ACCEPTANCE_PATH,
) -> list[dict[str, str]]:
    """Return conservative validation-package review rows."""

    rows = [
        _internal_route_plausibility_row(route_plausibility_path),
        _fallback_benchmark_row(fallback_benchmark_path),
    ]
    if Path(osrm_benchmark_path).exists():
        rows.append(
            _osrm_benchmark_row(
                osrm_benchmark_path,
                osrm_benchmark_manifest_path,
            )
        )
    rows.extend(
        [
            _accessibility_loss_row(accessibility_loss_path),
            _route_road_evidence_exposure_row(route_road_evidence_exposure_path),
            _validation_summary_scope_row(validation_summary_path),
            _benchmark_strategy_decision_row(
                validation_acceptance_path=validation_acceptance_path,
                fallback_benchmark_path=fallback_benchmark_path,
                osrm_benchmark_path=osrm_benchmark_path,
                osrm_benchmark_manifest_path=osrm_benchmark_manifest_path,
            ),
        ]
    )
    return rows


def write_validation_review_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_VALIDATION_REVIEW_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_VALIDATION_REVIEW_MANIFEST_PATH,
    route_plausibility_path: str | Path = DEFAULT_ROUTE_PLAUSIBILITY_PATH,
    fallback_benchmark_path: str | Path = DEFAULT_FALLBACK_BENCHMARK_PATH,
    osrm_benchmark_path: str | Path = DEFAULT_OSRM_BENCHMARK_PATH,
    osrm_benchmark_manifest_path: str | Path = DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH,
    accessibility_loss_path: str | Path = DEFAULT_ACCESSIBILITY_LOSS_PATH,
    route_road_evidence_exposure_path: str | Path = DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_PATH,
    validation_summary_path: str | Path = DEFAULT_VALIDATION_SUMMARY_PATH,
    validation_acceptance_path: str | Path = DEFAULT_VALIDATION_ACCEPTANCE_PATH,
) -> dict[str, Any]:
    """Write the validation review worksheet and non-acceptance manifest."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=VALIDATION_REVIEW_COLUMNS,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)

    route_rows = _read_csv_rows(route_plausibility_path)
    fallback_rows = _read_csv_rows(fallback_benchmark_path)
    osrm_present = Path(osrm_benchmark_path).exists()
    osrm_rows = _read_csv_rows(osrm_benchmark_path) if osrm_present else []
    osrm_manifest = _read_json_object(osrm_benchmark_manifest_path)
    accessibility_rows = _read_csv_rows(accessibility_loss_path)
    route_exposure_rows = _read_csv_rows(route_road_evidence_exposure_path)
    summary_flags = _summary_scope_flags(_read_text(validation_summary_path))
    status_counts = _counts(row.get("review_status", "") for row in rows)

    value = {
        "schema_version": 1,
        "result_scope": VALIDATION_REVIEW_PACKET_SCOPE,
        "input_artifact_paths": {
            "route_plausibility": _display_path(route_plausibility_path),
            "fallback_benchmarks": _display_path(fallback_benchmark_path),
            "osrm_benchmarks": _display_path(osrm_benchmark_path),
            "osrm_benchmark_manifest": _display_path(
                osrm_benchmark_manifest_path
            ),
            "accessibility_loss": _display_path(accessibility_loss_path),
            "route_road_evidence_exposure": _display_path(
                route_road_evidence_exposure_path
            ),
            "validation_summary": _display_path(validation_summary_path),
            "validation_acceptance_record": _display_path(
                validation_acceptance_path
            ),
        },
        "outputs": {
            "validation_review_packet": _display_path(output),
            "manifest": _display_path(manifest),
        },
        "row_count": len(rows),
        "category_ids": [str(row.get("category_id", "")) for row in rows],
        "status_counts": status_counts,
        "review_status_counts": status_counts,
        "artifact_presence_counts": _counts(
            row.get("artifact_present", "") for row in rows
        ),
        "internal_plausibility_status_counts": _status_counts(route_rows),
        "fallback_benchmark_status_counts": _status_counts(fallback_rows),
        "optional_osrm_benchmark_present": osrm_present,
        "optional_osrm_benchmark_manifest_present": Path(
            osrm_benchmark_manifest_path
        ).exists(),
        "optional_osrm_benchmark_manifest_scope": str(
            (osrm_manifest or {}).get("result_scope", "")
        ),
        "optional_osrm_benchmark_unpinned_row_count": int(
            (osrm_manifest or {}).get("unpinned_row_count", 0) or 0
        ),
        "optional_osrm_benchmark_raw_response_file_count": int(
            (osrm_manifest or {}).get("raw_response_file_count", 0) or 0
        ),
        "optional_osrm_benchmark_raw_response_binding_mismatch_count": int(
            (osrm_manifest or {}).get("raw_response_binding_mismatch_count", 0) or 0
        ),
        "optional_osrm_benchmark_raw_response_missing_for_row_count": int(
            (osrm_manifest or {}).get("raw_response_missing_for_row_count", 0) or 0
        ),
        "optional_osrm_benchmark_snap_status_counts": _dict_value(
            osrm_manifest or {},
            "snap_status_counts",
        ),
        "osrm_benchmark_status_counts": _status_counts(osrm_rows)
        if osrm_present
        else {},
        "accessibility_criticality_counts": _counts(
            row.get("criticality_class", "") for row in accessibility_rows
        ),
        "accessibility_route_count": _unique_count(
            row.get("route_id", "") for row in accessibility_rows
        ),
        "route_road_evidence_exposure_row_count": len(route_exposure_rows),
        "route_road_evidence_exposure_weak_counts": _counts(
            row.get("weak_for_final_claim", "") for row in route_exposure_rows
        ),
        "route_road_evidence_exposure_variant_counts": _counts(
            row.get("graph_variant", "") for row in route_exposure_rows
        ),
        "validation_summary_scope_flags": summary_flags,
        "validation_acceptance_record_present": Path(
            validation_acceptance_path
        ).exists(),
        "publication_ready": False,
        "acceptance_ready": False,
        "acceptance_gate_closure_candidate_count": 0,
        "review_required": True,
        "claim_boundary": (
            "This packet summarizes validation artifacts for human strategy "
            "review only. It does not create "
            "data/manifests/validation_acceptance.json, does not close the "
            "validation gate, does not treat benchmarks as ground truth, and "
            "does not support operational routing or real-world forecasts."
        ),
        "review_items": [
            "review internal route plausibility warning and failure rows",
            "decide whether documented fallback benchmarks are sufficient or only a placeholder",
            "if using OSRM or another route engine, review the cached manifest and convert live snapshots into reviewed cached evidence",
            "review accessibility-loss rows as route-fragility diagnostics, not outage probabilities",
            "review route-level road-evidence exposure before prioritizing road-class evidence collection",
            "record any release-scope benchmark strategy only in data/manifests/validation_acceptance.json after review",
        ],
    }
    with manifest.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return value


def _internal_route_plausibility_row(path: str | Path) -> dict[str, str]:
    rows = _read_csv_rows(path)
    status_counts = _status_counts(rows)
    category_counts = _counts(row.get("category", "") for row in rows)
    coverage_counts: dict[str, object] = {
        "subjects": _unique_count(row.get("subject", "") for row in rows),
        "metrics": _unique_count(row.get("metric", "") for row in rows),
    }
    coverage_counts.update(_prefixed_counts("category", category_counts))
    fail_count = status_counts.get("fail", 0)
    warn_count = status_counts.get("warn", 0)
    if not Path(path).exists():
        review_status = "missing_validation_artifact"
    elif not rows:
        review_status = "empty_validation_artifact"
    elif fail_count:
        review_status = "review_required_fail_rows"
    elif warn_count:
        review_status = "review_required_warn_rows"
    else:
        review_status = "ready_for_review_no_warn_or_fail"
    return _review_row(
        category_id="internal_route_plausibility",
        evidence_category="Internal route plausibility status counts",
        artifact_path=path,
        artifact_present=Path(path).exists(),
        row_count=len(rows),
        status_counts=status_counts,
        coverage_counts=coverage_counts,
        review_status=review_status,
        review_action=(
            "Review internal sanity-check warnings and failures against the "
            "selected final graph, road inputs, and claim boundary."
        ),
        publication_use_status="review_support_only_not_validation_acceptance",
    )


def _fallback_benchmark_row(path: str | Path) -> dict[str, str]:
    rows = _read_csv_rows(path)
    status_counts = _status_counts(rows)
    if not Path(path).exists():
        review_status = "missing_validation_artifact"
    elif not rows:
        review_status = "empty_validation_artifact"
    elif status_counts.get("fail", 0) or status_counts.get("warn", 0):
        review_status = "review_required_fallback_warn_or_fail_rows"
    else:
        review_status = "review_required_documented_fallback_benchmark"
    return _review_row(
        category_id="fallback_route_benchmarks",
        evidence_category="Fallback benchmark status counts",
        artifact_path=path,
        artifact_present=Path(path).exists(),
        row_count=len(rows),
        status_counts=status_counts,
        coverage_counts=_benchmark_coverage(rows),
        review_status=review_status,
        review_action=(
            "Decide whether documented fallback detour-speed benchmarks remain "
            "inside the final validation scope or must be replaced by cached "
            "third-party route-engine evidence."
        ),
        publication_use_status="fallback_benchmark_review_support_only",
    )


def _osrm_benchmark_row(
    path: str | Path,
    manifest_path: str | Path,
) -> dict[str, str]:
    rows = _read_csv_rows(path)
    status_counts = _status_counts(rows)
    manifest = _read_json_object(manifest_path)
    manifest_present = Path(manifest_path).exists()
    raw_binding_mismatch_count = int(
        (manifest or {}).get("raw_response_binding_mismatch_count", 0) or 0
    )
    raw_missing_count = int(
        (manifest or {}).get("raw_response_missing_for_row_count", 0) or 0
    )
    snap_status_counts = _dict_value(manifest or {}, "snap_status_counts")
    unpinned = any(
        "unpinned" in str(row.get("reference_version", "")).lower()
        or "live" in str(row.get("source_class", "")).lower()
        for row in rows
    )
    if not rows:
        review_status = "empty_validation_artifact"
    elif raw_binding_mismatch_count or raw_missing_count:
        review_status = "review_required_osrm_raw_payload_mismatch"
    elif snap_status_counts.get("fail", 0) or snap_status_counts.get("warn", 0):
        review_status = "review_required_osrm_snap_distance_review"
    elif status_counts.get("fail", 0) or status_counts.get("warn", 0):
        review_status = "review_required_osrm_warn_or_fail_rows"
    elif unpinned:
        review_status = "review_required_unpinned_external_snapshot"
    elif not manifest_present:
        review_status = "review_required_missing_osrm_snapshot_manifest"
    else:
        review_status = "ready_for_review_cached_external_snapshot"
    return _review_row(
        category_id="optional_osrm_route_benchmarks",
        evidence_category="Optional OSRM benchmark status counts",
        artifact_path=path,
        artifact_present=Path(path).exists(),
        row_count=len(rows),
        status_counts=status_counts,
        coverage_counts={
            **_benchmark_coverage(rows),
            "snapshot_manifest_present": manifest_present,
            "snapshot_manifest_unpinned_rows": int(
                (manifest or {}).get("unpinned_row_count", 0) or 0
            ),
            "snapshot_manifest_raw_response_files": int(
                (manifest or {}).get("raw_response_file_count", 0) or 0
            ),
            "snapshot_manifest_raw_binding_mismatches": raw_binding_mismatch_count,
            "snapshot_manifest_raw_missing_rows": raw_missing_count,
            "snapshot_manifest_max_snap_distance_m": str(
                (manifest or {}).get("max_waypoint_snap_distance_m", "")
            ),
            **_prefixed_counts("snapshot_snap_status", snap_status_counts),
        },
        review_status=review_status,
        review_action=(
            "Review OSRM rows as an optional external plausibility snapshot; "
            "review the non-acceptance manifest, retain raw response payloads "
            "when refreshing live rows, pin/cache source evidence, and "
            "document provenance before using them in an accepted benchmark "
            "strategy."
        ),
        publication_use_status="optional_external_snapshot_review_support_only",
    )


def _accessibility_loss_row(path: str | Path) -> dict[str, str]:
    rows = _read_csv_rows(path)
    criticality_counts = _counts(row.get("criticality_class", "") for row in rows)
    if not Path(path).exists():
        review_status = "missing_validation_artifact"
    elif not rows:
        review_status = "empty_validation_artifact"
    elif criticality_counts.get("baseline_disconnected", 0) or criticality_counts.get(
        "disconnected", 0
    ):
        review_status = "review_required_disconnected_accessibility_cases"
    elif criticality_counts.get("high_time_loss", 0):
        review_status = "review_required_high_accessibility_loss_cases"
    else:
        review_status = "ready_for_review_accessibility_coverage"
    coverage_counts: dict[str, object] = {
        "routes": _unique_count(row.get("route_id", "") for row in rows),
    }
    coverage_counts.update(
        _prefixed_counts(
            "baseline_available",
            _counts(row.get("baseline_available", "") for row in rows),
        )
    )
    coverage_counts.update(
        _prefixed_counts(
            "disrupted_available",
            _counts(row.get("disrupted_available", "") for row in rows),
        )
    )
    return _review_row(
        category_id="accessibility_loss_coverage",
        evidence_category="Accessibility-loss coverage counts",
        artifact_path=path,
        artifact_present=Path(path).exists(),
        row_count=len(rows),
        status_counts=criticality_counts,
        coverage_counts=coverage_counts,
        review_status=review_status,
        review_action=(
            "Review accessibility-loss coverage as route-fragility evidence "
            "only; decide whether directed-edge, bidirectional-link, or "
            "corridor-level disruption is the accepted validation design."
        ),
        publication_use_status="accessibility_diagnostic_review_support_only",
    )


def _route_road_evidence_exposure_row(path: str | Path) -> dict[str, str]:
    rows = _read_csv_rows(path)
    weak_counts = _counts(row.get("weak_for_final_claim", "") for row in rows)
    variant_counts = _counts(row.get("graph_variant", "") for row in rows)
    if not Path(path).exists():
        review_status = "missing_validation_artifact"
    elif not rows:
        review_status = "empty_validation_artifact"
    elif weak_counts.get("true", 0):
        review_status = "review_required_weak_route_road_evidence_exposure"
    else:
        review_status = "ready_for_review_route_road_evidence_exposure"
    coverage_counts: dict[str, object] = {
        "routes": _unique_count(row.get("route_check_id", "") for row in rows),
        "route_candidates": _unique_count(
            (
                row.get("graph_variant", ""),
                row.get("route_check_id", ""),
                row.get("route_rank", ""),
            )
            for row in rows
        ),
    }
    coverage_counts.update(_prefixed_counts("variant", variant_counts))
    coverage_counts.update(_prefixed_counts("weak_for_final_claim", weak_counts))
    return _review_row(
        category_id="route_road_evidence_exposure",
        evidence_category="Route-level road-evidence exposure counts",
        artifact_path=path,
        artifact_present=Path(path).exists(),
        row_count=len(rows),
        status_counts=weak_counts,
        coverage_counts=coverage_counts,
        review_status=review_status,
        review_action=(
            "Review which weak speed, capacity, disruption, and connector "
            "assumptions appear on canonical route candidates before "
            "prioritizing road evidence collection."
        ),
        publication_use_status="route_exposure_review_support_only",
    )


def _validation_summary_scope_row(path: str | Path) -> dict[str, str]:
    text = _read_text(path)
    flags = _summary_scope_flags(text)
    present = Path(path).exists()
    if not present:
        review_status = "missing_validation_artifact"
    elif all(flags.values()):
        review_status = "scope_boundary_present_review_required"
    else:
        review_status = "scope_boundary_incomplete_review_required"
    return _review_row(
        category_id="validation_summary_scope",
        evidence_category="Validation-summary scope status",
        artifact_path=path,
        artifact_present=present,
        row_count=len(text.splitlines()) if present else 0,
        status_counts={},
        coverage_counts={
            "chars": len(text),
            "lines": len(text.splitlines()) if present else 0,
            **flags,
        },
        review_status=review_status,
        review_action=(
            "Keep the validation summary inside scaffold, plausibility, and "
            "not-operational wording until a separate validation acceptance "
            "record chooses the benchmark strategy."
        ),
        publication_use_status="scope_review_support_only_not_acceptance",
    )


def _benchmark_strategy_decision_row(
    *,
    validation_acceptance_path: str | Path,
    fallback_benchmark_path: str | Path,
    osrm_benchmark_path: str | Path,
    osrm_benchmark_manifest_path: str | Path,
) -> dict[str, str]:
    acceptance_present = Path(validation_acceptance_path).exists()
    review_status = (
        "review_required_existing_acceptance_record_is_separate"
        if acceptance_present
        else "review_required_no_validation_acceptance_record"
    )
    return _review_row(
        category_id="benchmark_strategy_decision_requirement",
        evidence_category="Benchmark-strategy decision requirement",
        artifact_path=validation_acceptance_path,
        artifact_present=acceptance_present,
        row_count=0,
        status_counts={},
        coverage_counts={
            "allowed_strategy_options": len(ALLOWED_BENCHMARK_STRATEGIES),
            "fallback_benchmark_present": Path(fallback_benchmark_path).exists(),
            "osrm_benchmark_present": Path(osrm_benchmark_path).exists(),
            "osrm_benchmark_manifest_present": Path(
                osrm_benchmark_manifest_path
            ).exists(),
            "validation_acceptance_record_present": acceptance_present,
        },
        review_status=review_status,
        review_action=(
            "Reviewer must choose the release-scope benchmark strategy and record it "
            "only in data/manifests/validation_acceptance.json after reviewing "
            "internal checks, fallback benchmarks, optional external snapshots, "
            "and claim boundaries."
        ),
        publication_use_status="blocked_until_separate_validation_acceptance",
    )


def _benchmark_coverage(rows: Sequence[Mapping[str, str]]) -> dict[str, object]:
    coverage: dict[str, object] = {
        "subjects": _unique_count(row.get("subject", "") for row in rows),
        "methods": _unique_count(row.get("benchmark_method", "") for row in rows),
    }
    coverage.update(
        _prefixed_counts(
            "source_class",
            _counts(row.get("source_class", "") for row in rows),
        )
    )
    return coverage


def _review_row(
    *,
    category_id: str,
    evidence_category: str,
    artifact_path: str | Path,
    artifact_present: bool,
    row_count: int,
    status_counts: Mapping[str, Any],
    coverage_counts: Mapping[str, Any],
    review_status: str,
    review_action: str,
    publication_use_status: str,
) -> dict[str, str]:
    return {
        "category_id": category_id,
        "evidence_category": evidence_category,
        "artifact_path": _display_path(artifact_path),
        "artifact_present": _bool_text(artifact_present),
        "row_count": str(row_count),
        "status_counts": _counts_text(status_counts),
        "coverage_counts": _counts_text(coverage_counts),
        "review_status": review_status,
        "review_required": "true",
        "acceptance_ready": "false",
        "publication_ready": "false",
        "review_action": review_action,
        "publication_use_status": publication_use_status,
        "claim_boundary": VALIDATION_REVIEW_PACKET_SCOPE,
    }


def _read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    csv_path = Path(path)
    if not csv_path.exists():
        return []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _read_text(path: str | Path) -> str:
    text_path = Path(path)
    if not text_path.exists():
        return ""
    return text_path.read_text(encoding="utf-8")


def _read_json_object(path: str | Path) -> dict[str, Any] | None:
    json_path = Path(path)
    if not json_path.exists():
        return None
    with json_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    return value if isinstance(value, dict) else None


def _status_counts(
    rows: Sequence[Mapping[str, str]],
    *,
    field: str = "status",
) -> dict[str, int]:
    counts = {"fail": 0, "pass": 0, "warn": 0}
    for row in rows:
        status = str(row.get(field, "")).strip().lower()
        if status:
            counts[status] = counts.get(status, 0) + 1
    return dict(sorted(counts.items()))


def _counts(values: Iterable[object]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value).strip()
        if not key:
            continue
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _unique_count(values: Iterable[object]) -> int:
    return len({str(value).strip() for value in values if str(value).strip()})


def _counts_text(values: Mapping[str, Any]) -> str:
    parts: list[str] = []
    for key in sorted(values):
        value = values[key]
        if isinstance(value, bool):
            rendered = _bool_text(value)
        elif isinstance(value, Mapping):
            rendered = _counts_text(value)
        else:
            rendered = str(value)
        parts.append(f"{key}={rendered}")
    return "; ".join(parts)


def _dict_value(value: Mapping[str, Any], key: str) -> dict[str, int]:
    found = value.get(key, {})
    if not isinstance(found, Mapping):
        return {}
    result: dict[str, int] = {}
    for item_key, item_value in found.items():
        try:
            result[str(item_key)] = int(item_value)
        except (TypeError, ValueError):
            continue
    return dict(sorted(result.items()))


def _prefixed_counts(prefix: str, values: Mapping[str, int]) -> dict[str, int]:
    return {f"{prefix}_{key}": value for key, value in values.items()}


def _summary_scope_flags(text: str) -> dict[str, bool]:
    lower = text.lower()
    return {
        "scaffold_or_sanity_scope": "scaffold" in lower or "sanity" in lower,
        "not_ground_truth_boundary": "not ground truth" in lower,
        "not_operational_boundary": (
            "not operational" in lower
            or "not an operational" in lower
            or "does not justify operational" in lower
            or "operational route planning claims" in lower
        ),
        "benchmark_limitations_declared": (
            "fallback" in lower
            and ("benchmark" in lower or "route-engine" in lower)
        ),
    }


def _bool_text(value: object) -> str:
    return str(bool(value)).lower()


def _display_path(path: str | Path) -> str:
    filepath = Path(path)
    try:
        return filepath.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return filepath.as_posix()


__all__ = [
    "DEFAULT_ACCESSIBILITY_LOSS_PATH",
    "DEFAULT_FALLBACK_BENCHMARK_PATH",
    "DEFAULT_OSRM_BENCHMARK_PATH",
    "DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH",
    "DEFAULT_ROUTE_PLAUSIBILITY_PATH",
    "DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_PATH",
    "DEFAULT_VALIDATION_ACCEPTANCE_PATH",
    "DEFAULT_VALIDATION_REVIEW_MANIFEST_PATH",
    "DEFAULT_VALIDATION_REVIEW_PACKET_PATH",
    "DEFAULT_VALIDATION_SUMMARY_PATH",
    "VALIDATION_REVIEW_COLUMNS",
    "VALIDATION_REVIEW_PACKET_SCOPE",
    "build_validation_review_rows",
    "write_validation_review_packet",
]
