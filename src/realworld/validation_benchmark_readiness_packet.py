"""Validation benchmark readiness packet.

This module summarizes benchmark-specific validation evidence: the deterministic
fallback route checks, optional cached OSRM snapshot, alternative benchmark
engine decision, and missing validation acceptance record. It is a reviewer aid
only and does not treat any route engine as ground truth.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FALLBACK_BENCHMARK_PATH = (
    PROJECT_ROOT / "data" / "validation" / "external_route_benchmarks.csv"
)
DEFAULT_OSRM_BENCHMARK_PATH = (
    PROJECT_ROOT / "data" / "validation" / "external_route_benchmarks_osrm.csv"
)
DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "osrm_route_benchmark_manifest.json"
)
DEFAULT_VALIDATION_ACCEPTANCE_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "validation_acceptance.json"
)
DEFAULT_VALIDATION_BENCHMARK_READINESS_PACKET_PATH = (
    PROJECT_ROOT / "data" / "validation" / "validation_benchmark_readiness_packet.csv"
)
DEFAULT_VALIDATION_BENCHMARK_READINESS_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "validation_benchmark_readiness_manifest.json"
)
DEFAULT_VALIDATION_BENCHMARK_READINESS_DOC_PATH = (
    PROJECT_ROOT / "docs" / "validation_benchmark_readiness_packet.md"
)
VALIDATION_BENCHMARK_READINESS_SCOPE = (
    "Validation benchmark readiness packet only; not validation acceptance, "
    "not route-engine ground truth, not calibrated traffic validation, and not "
    "operational routing evidence."
)
VALIDATION_BENCHMARK_READINESS_COLUMNS: tuple[str, ...] = (
    "benchmark_option_id",
    "option_label",
    "artifact_path",
    "artifact_present",
    "row_count",
    "status_counts",
    "method_counts",
    "source_class_counts",
    "manifest_path",
    "manifest_present",
    "raw_response_file_count",
    "raw_response_binding_mismatch_count",
    "raw_response_missing_for_row_count",
    "snap_status_counts",
    "max_waypoint_snap_distance_m",
    "unpinned_row_count",
    "query_url_count",
    "source_pinning_status",
    "readiness_status",
    "blocking_reason",
    "required_reviewer_action",
    "can_support_validation_gate",
    "claim_boundary",
)


def build_validation_benchmark_readiness_rows(
    *,
    fallback_benchmark_path: str | Path = DEFAULT_FALLBACK_BENCHMARK_PATH,
    osrm_benchmark_path: str | Path = DEFAULT_OSRM_BENCHMARK_PATH,
    osrm_benchmark_manifest_path: str | Path = DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH,
    validation_acceptance_path: str | Path = DEFAULT_VALIDATION_ACCEPTANCE_PATH,
) -> list[dict[str, str]]:
    """Return benchmark-strategy readiness rows from current validation artifacts."""

    fallback_rows = _read_csv_rows(fallback_benchmark_path)
    osrm_rows = _read_csv_rows(osrm_benchmark_path)
    osrm_manifest = _read_json_object(osrm_benchmark_manifest_path)
    return [
        _fallback_row(Path(fallback_benchmark_path), fallback_rows),
        _osrm_row(Path(osrm_benchmark_path), Path(osrm_benchmark_manifest_path), osrm_rows, osrm_manifest),
        _alternative_engine_row(),
        _validation_acceptance_row(Path(validation_acceptance_path)),
    ]


def write_validation_benchmark_readiness_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_VALIDATION_BENCHMARK_READINESS_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_VALIDATION_BENCHMARK_READINESS_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_VALIDATION_BENCHMARK_READINESS_DOC_PATH,
    fallback_benchmark_path: str | Path = DEFAULT_FALLBACK_BENCHMARK_PATH,
    osrm_benchmark_path: str | Path = DEFAULT_OSRM_BENCHMARK_PATH,
    osrm_benchmark_manifest_path: str | Path = DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH,
    validation_acceptance_path: str | Path = DEFAULT_VALIDATION_ACCEPTANCE_PATH,
) -> dict[str, Any]:
    """Write benchmark readiness CSV, manifest, and Markdown review packet."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=VALIDATION_BENCHMARK_READINESS_COLUMNS,
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in VALIDATION_BENCHMARK_READINESS_COLUMNS
                }
            )

    summary = build_validation_benchmark_readiness_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        fallback_benchmark_path=fallback_benchmark_path,
        osrm_benchmark_path=osrm_benchmark_path,
        osrm_benchmark_manifest_path=osrm_benchmark_manifest_path,
        validation_acceptance_path=validation_acceptance_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_validation_benchmark_readiness_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_validation_benchmark_readiness_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_VALIDATION_BENCHMARK_READINESS_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_VALIDATION_BENCHMARK_READINESS_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_VALIDATION_BENCHMARK_READINESS_DOC_PATH,
    fallback_benchmark_path: str | Path = DEFAULT_FALLBACK_BENCHMARK_PATH,
    osrm_benchmark_path: str | Path = DEFAULT_OSRM_BENCHMARK_PATH,
    osrm_benchmark_manifest_path: str | Path = DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH,
    validation_acceptance_path: str | Path = DEFAULT_VALIDATION_ACCEPTANCE_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for benchmark readiness rows."""

    readiness_counts = _counts(row.get("readiness_status", "") for row in rows)
    blocking_count = sum(
        1
        for row in rows
        if str(row.get("readiness_status", "")).startswith("blocked_")
    )
    human_review_count = sum(
        1
        for row in rows
        if str(row.get("readiness_status", "")).startswith("needs_human_review_")
    )
    osrm = next(
        (
            row
            for row in rows
            if row.get("benchmark_option_id") == "cached_osrm_route_snapshot"
        ),
        {},
    )
    return {
        "schema_version": 1,
        "result_scope": VALIDATION_BENCHMARK_READINESS_SCOPE,
        "claim_boundary": (
            "This packet supports benchmark-strategy review only. It does not "
            "create validation acceptance, does not certify OSRM or fallback "
            "benchmarks as ground truth, and does not support operational "
            "routing or real-world forecast claims."
        ),
        "row_count": len(rows),
        "readiness_status_counts": readiness_counts,
        "blocking_request_count": blocking_count,
        "human_review_request_count": human_review_count,
        "benchmark_gate_closure_candidate_count": 0,
        "fallback_benchmark_present": Path(fallback_benchmark_path).exists(),
        "osrm_benchmark_present": Path(osrm_benchmark_path).exists(),
        "osrm_manifest_present": Path(osrm_benchmark_manifest_path).exists(),
        "osrm_raw_response_file_count": _int_value(
            osrm.get("raw_response_file_count", "")
        )
        or 0,
        "osrm_raw_response_binding_mismatch_count": _int_value(
            osrm.get("raw_response_binding_mismatch_count", "")
        )
        or 0,
        "osrm_raw_response_missing_for_row_count": _int_value(
            osrm.get("raw_response_missing_for_row_count", "")
        )
        or 0,
        "osrm_snap_status_counts": osrm.get("snap_status_counts", ""),
        "osrm_max_waypoint_snap_distance_m": osrm.get(
            "max_waypoint_snap_distance_m",
            "",
        ),
        "osrm_unpinned_row_count": _int_value(osrm.get("unpinned_row_count", ""))
        or 0,
        "osrm_query_url_count": _int_value(osrm.get("query_url_count", "")) or 0,
        "validation_acceptance_record_present": Path(
            validation_acceptance_path
        ).exists(),
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "fallback_benchmarks": _display_path(Path(fallback_benchmark_path)),
            "osrm_benchmarks": _display_path(Path(osrm_benchmark_path)),
            "osrm_benchmark_manifest": _display_path(
                Path(osrm_benchmark_manifest_path)
            ),
            "validation_acceptance": _display_path(
                Path(validation_acceptance_path)
            ),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": [
            "decide whether fallback detour-speed rows are retained, replaced, or excluded",
            "review cached OSRM rows, query URLs, raw response files, and license/attribution before publication use",
            "decide whether OSRM is sufficient as a plausibility snapshot or whether Valhalla, routingpy, R5/OpenTripPlanner, UXsim, or agency benchmark evidence is needed",
            "record any final benchmark strategy only in data/manifests/validation_acceptance.json",
        ],
        "remaining_blockers": _remaining_blockers(rows),
    }


def build_validation_benchmark_readiness_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return Markdown benchmark readiness packet."""

    lines = [
        "# Benchmark Strategy Review Packet",
        "",
        str(manifest.get("claim_boundary", VALIDATION_BENCHMARK_READINESS_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Benchmark rows: {manifest.get('row_count', 0)}",
        f"- Blocking requests: {manifest.get('blocking_request_count', 0)}",
        f"- Human-review requests: {manifest.get('human_review_request_count', 0)}",
        f"- OSRM raw response files: {manifest.get('osrm_raw_response_file_count', 0)}",
        f"- OSRM unpinned rows: {manifest.get('osrm_unpinned_row_count', 0)}",
        f"- Status counts: `{manifest.get('readiness_status_counts', {})}`",
        "",
        "## Rows",
        "",
        "| Option | Rows | Status | Required Action |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {option} | {rows} | {status} | {action} |".format(
                option=_cell(row.get("benchmark_option_id", "")),
                rows=_cell(row.get("row_count", "")),
                status=_cell(row.get("readiness_status", "")),
                action=_cell(row.get("required_reviewer_action", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This packet does not choose the accepted benchmark strategy.",
            "- It does not treat OSRM, fallback detour checks, or any alternative route engine as ground truth.",
            "- It cannot create or replace `data/manifests/validation_acceptance.json`.",
            "",
        ]
    )
    return "\n".join(lines)


def _fallback_row(path: Path, rows: Sequence[Mapping[str, str]]) -> dict[str, str]:
    status_counts = _status_counts(rows)
    if not path.exists():
        status, reason, action = (
            "blocked_missing_fallback_benchmark",
            "fallback benchmark CSV is absent",
            "regenerate fallback route benchmarks or document why they are excluded",
        )
    elif not rows:
        status, reason, action = (
            "blocked_empty_fallback_benchmark",
            "fallback benchmark CSV has no rows",
            "regenerate fallback route benchmarks before benchmark review",
        )
    elif status_counts.get("fail", 0) or status_counts.get("warn", 0):
        status, reason, action = (
            "needs_human_review_fallback_warn_rows",
            "",
            "decide whether fallback warning rows are acceptable placeholders or must be replaced",
        )
    else:
        status, reason, action = (
            "needs_human_review_fallback_scope_decision",
            "",
            "decide whether fallback rows remain in the final validation scope",
        )
    return _row(
        option_id="fallback_detour_speed_benchmark",
        option_label="Documented fallback detour-speed benchmark rows",
        artifact_path=path,
        artifact_present=path.exists(),
        rows=rows,
        manifest_path=None,
        manifest_present=False,
        raw_response_file_count="",
        raw_response_binding_mismatch_count="",
        raw_response_missing_for_row_count="",
        snap_status_counts="",
        max_waypoint_snap_distance_m="",
        unpinned_row_count="",
        query_url_count="",
        source_pinning_status="not_applicable_fallback",
        readiness_status=status,
        blocking_reason=reason,
        required_action=action,
    )


def _osrm_row(
    path: Path,
    manifest_path: Path,
    rows: Sequence[Mapping[str, str]],
    manifest: Mapping[str, Any] | None,
) -> dict[str, str]:
    status_counts = _status_counts(rows)
    manifest_present = manifest_path.exists() and manifest is not None
    raw_count = _manifest_int(manifest, "raw_response_file_count")
    raw_mismatch_count = _manifest_int(manifest, "raw_response_binding_mismatch_count")
    raw_missing_count = _manifest_int(manifest, "raw_response_missing_for_row_count")
    unpinned_count = _manifest_int(manifest, "unpinned_row_count")
    query_count = _manifest_int(manifest, "query_url_count")
    snap_counts = _manifest_counts(manifest, "snap_status_counts")
    max_snap_distance = "" if not manifest else str(
        manifest.get("max_waypoint_snap_distance_m", "")
    )
    if not path.exists():
        status, reason, action = (
            "needs_human_review_external_snapshot_absent",
            "",
            "decide whether to add a cached external route-engine snapshot",
        )
    elif not manifest_present:
        status, reason, action = (
            "blocked_missing_osrm_snapshot_manifest",
            "OSRM benchmark CSV is present but manifest is absent",
            "write the OSRM snapshot manifest before benchmark review",
        )
    elif raw_mismatch_count > 0 or raw_missing_count > 0:
        status, reason, action = (
            "blocked_osrm_raw_payload_mismatch",
            "OSRM manifest reports missing or mismatched raw payload bindings",
            "regenerate or repair OSRM CSV/raw payloads before benchmark review",
        )
    elif unpinned_count > 0:
        status, reason, action = (
            "blocked_unpinned_osrm_snapshot_rows",
            "OSRM manifest reports unpinned reference versions",
            "replace live or unpinned rows with a reviewed cached snapshot",
        )
    elif raw_count == 0:
        status, reason, action = (
            "blocked_missing_osrm_raw_payloads",
            "OSRM manifest has no retained raw response payloads",
            "retain raw OSRM payloads and SHA256 values before publication use",
        )
    elif snap_counts.get("fail", 0) or snap_counts.get("warn", 0):
        status, reason, action = (
            "needs_human_review_osrm_snap_distance",
            "",
            "review OSRM waypoint snap distances before relying on route-comparison wording",
        )
    elif status_counts.get("fail", 0) or status_counts.get("warn", 0):
        status, reason, action = (
            "needs_human_review_osrm_warn_or_fail_rows",
            "",
            "review OSRM warn/fail rows before deciding benchmark scope",
        )
    else:
        status, reason, action = (
            "needs_human_review_cached_osrm_snapshot",
            "",
            "review OSRM as optional plausibility evidence, including terms and attribution",
        )
    return _row(
        option_id="cached_osrm_route_snapshot",
        option_label="Cached OSRM route API snapshot",
        artifact_path=path,
        artifact_present=path.exists(),
        rows=rows,
        manifest_path=manifest_path,
        manifest_present=manifest_present,
        raw_response_file_count=str(raw_count),
        raw_response_binding_mismatch_count=str(raw_mismatch_count),
        raw_response_missing_for_row_count=str(raw_missing_count),
        snap_status_counts=_format_counts(snap_counts),
        max_waypoint_snap_distance_m=max_snap_distance,
        unpinned_row_count=str(unpinned_count),
        query_url_count=str(query_count),
        source_pinning_status="pinned_cached_payloads"
        if raw_count and not unpinned_count
        else "unverified_or_unpinned_source",
        readiness_status=status,
        blocking_reason=reason,
        required_action=action,
    )


def _alternative_engine_row() -> dict[str, str]:
    return {
        "benchmark_option_id": "alternative_route_engine_decision",
        "option_label": "Alternative route-engine or agency benchmark decision",
        "artifact_path": "",
        "artifact_present": "false",
        "row_count": "0",
        "status_counts": "",
        "method_counts": "",
        "source_class_counts": "",
        "manifest_path": "",
        "manifest_present": "false",
        "raw_response_file_count": "",
        "raw_response_binding_mismatch_count": "",
        "raw_response_missing_for_row_count": "",
        "snap_status_counts": "",
        "max_waypoint_snap_distance_m": "",
        "unpinned_row_count": "",
        "query_url_count": "",
        "source_pinning_status": "not_reviewed",
        "readiness_status": "needs_human_review_alternative_benchmark_decision",
        "blocking_reason": "",
        "required_reviewer_action": (
            "decide whether OSRM/fallback checks are sufficient or whether "
            "Valhalla, routingpy, R5/OpenTripPlanner, UXsim, or agency "
            "benchmark evidence is needed"
        ),
        "can_support_validation_gate": "false",
        "claim_boundary": VALIDATION_BENCHMARK_READINESS_SCOPE,
    }


def _validation_acceptance_row(path: Path) -> dict[str, str]:
    present = path.exists()
    return {
        "benchmark_option_id": "validation_acceptance_record",
        "option_label": "Formal validation benchmark strategy decision",
        "artifact_path": _display_path(path),
        "artifact_present": str(present).lower(),
        "row_count": "0",
        "status_counts": "",
        "method_counts": "",
        "source_class_counts": "",
        "manifest_path": "",
        "manifest_present": "false",
        "raw_response_file_count": "",
        "raw_response_binding_mismatch_count": "",
        "raw_response_missing_for_row_count": "",
        "snap_status_counts": "",
        "max_waypoint_snap_distance_m": "",
        "unpinned_row_count": "",
        "query_url_count": "",
        "source_pinning_status": "not_applicable_acceptance_record",
        "readiness_status": (
            "needs_human_review_existing_validation_acceptance"
            if present
            else "blocked_missing_validation_acceptance_record"
        ),
        "blocking_reason": "" if present else "data/manifests/validation_acceptance.json is absent",
        "required_reviewer_action": (
            "review the existing validation acceptance record"
            if present
            else "record final benchmark strategy only after reviewer decision"
        ),
        "can_support_validation_gate": "false",
        "claim_boundary": VALIDATION_BENCHMARK_READINESS_SCOPE,
    }


def _row(
    *,
    option_id: str,
    option_label: str,
    artifact_path: Path,
    artifact_present: bool,
    rows: Sequence[Mapping[str, str]],
    manifest_path: Path | None,
    manifest_present: bool,
    raw_response_file_count: str,
    raw_response_binding_mismatch_count: str,
    raw_response_missing_for_row_count: str,
    snap_status_counts: str,
    max_waypoint_snap_distance_m: str,
    unpinned_row_count: str,
    query_url_count: str,
    source_pinning_status: str,
    readiness_status: str,
    blocking_reason: str,
    required_action: str,
) -> dict[str, str]:
    return {
        "benchmark_option_id": option_id,
        "option_label": option_label,
        "artifact_path": _display_path(artifact_path),
        "artifact_present": str(artifact_present).lower(),
        "row_count": str(len(rows)),
        "status_counts": _format_counts(_status_counts(rows)),
        "method_counts": _format_counts(
            _counts(row.get("benchmark_method", "") for row in rows)
        ),
        "source_class_counts": _format_counts(
            _counts(row.get("source_class", "") for row in rows)
        ),
        "manifest_path": "" if manifest_path is None else _display_path(manifest_path),
        "manifest_present": str(manifest_present).lower(),
        "raw_response_file_count": raw_response_file_count,
        "raw_response_binding_mismatch_count": raw_response_binding_mismatch_count,
        "raw_response_missing_for_row_count": raw_response_missing_for_row_count,
        "snap_status_counts": snap_status_counts,
        "max_waypoint_snap_distance_m": max_waypoint_snap_distance_m,
        "unpinned_row_count": unpinned_row_count,
        "query_url_count": query_url_count,
        "source_pinning_status": source_pinning_status,
        "readiness_status": readiness_status,
        "blocking_reason": blocking_reason,
        "required_reviewer_action": required_action,
        "can_support_validation_gate": "false",
        "claim_boundary": VALIDATION_BENCHMARK_READINESS_SCOPE,
    }


def _remaining_blockers(rows: Sequence[Mapping[str, str]]) -> list[str]:
    blockers = [
        f"{row.get('benchmark_option_id')}: {row.get('blocking_reason')}"
        for row in rows
        if str(row.get("blocking_reason", "")).strip()
    ]
    if not blockers:
        blockers.append(
            "benchmark strategy still requires human review and validation_acceptance.json"
        )
    return blockers


def _read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    filepath = Path(path)
    if not filepath.exists():
        return []
    with filepath.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _read_json_object(path: str | Path) -> dict[str, Any] | None:
    filepath = Path(path)
    if not filepath.exists():
        return None
    with filepath.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{filepath} must contain a JSON object")
    return value


def _status_counts(rows: Sequence[Mapping[str, str]]) -> dict[str, int]:
    return _counts(row.get("status", "") for row in rows)


def _counts(values: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value).strip() or "blank"
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _format_counts(counts: Mapping[str, int]) -> str:
    return "; ".join(f"{key}={counts[key]}" for key in sorted(counts))


def _manifest_int(manifest: Mapping[str, Any] | None, key: str) -> int:
    if not manifest:
        return 0
    return _int_value(manifest.get(key, "")) or 0


def _manifest_counts(manifest: Mapping[str, Any] | None, key: str) -> dict[str, int]:
    if not manifest:
        return {}
    value = manifest.get(key, {})
    if not isinstance(value, Mapping):
        return {}
    counts: dict[str, int] = {}
    for item_key, item_value in value.items():
        parsed = _int_value(item_value)
        if parsed is not None:
            counts[str(item_key)] = parsed
    return dict(sorted(counts.items()))


def _int_value(value: Any) -> int | None:
    try:
        text = str(value).strip()
        if not text:
            return None
        return int(float(text))
    except (TypeError, ValueError):
        return None


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


__all__ = [
    "DEFAULT_FALLBACK_BENCHMARK_PATH",
    "DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH",
    "DEFAULT_OSRM_BENCHMARK_PATH",
    "DEFAULT_VALIDATION_ACCEPTANCE_PATH",
    "DEFAULT_VALIDATION_BENCHMARK_READINESS_DOC_PATH",
    "DEFAULT_VALIDATION_BENCHMARK_READINESS_MANIFEST_PATH",
    "DEFAULT_VALIDATION_BENCHMARK_READINESS_PACKET_PATH",
    "VALIDATION_BENCHMARK_READINESS_COLUMNS",
    "VALIDATION_BENCHMARK_READINESS_SCOPE",
    "build_validation_benchmark_readiness_manifest",
    "build_validation_benchmark_readiness_markdown",
    "build_validation_benchmark_readiness_rows",
    "write_validation_benchmark_readiness_packet",
]
