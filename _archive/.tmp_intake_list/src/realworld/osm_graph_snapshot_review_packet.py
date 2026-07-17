"""OSM/GraphML snapshot review worksheet.

The current pilot road graph is a cached Overpass/OSM-derived GraphML file.
This module consolidates cache metadata, source-provenance status, road-input
evidence gaps, road-source decisions, and graph-scale manifest fields into one
review worksheet. It does not refresh OSM, certify ODbL/Overpass compliance,
accept road-class overrides, select a graph-scale method, or close final-study
gates.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OSM_GRAPH_CACHE_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "cache" / "pilot_region_road_manifest.json"
)
DEFAULT_SOURCE_PROVENANCE_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "source_provenance_manifest.json"
)
DEFAULT_ROAD_EVIDENCE_PRIORITY_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "road" / "road_evidence_priority_manifest.json"
)
DEFAULT_ROAD_SOURCE_DECISION_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "road" / "road_source_decision_manifest.json"
)
DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_PATH = (
    PROJECT_ROOT / "data" / "validation" / "graph_scale_manifest_audit_manifest.json"
)
DEFAULT_PROVENANCE_ACCEPTANCE_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "provenance_acceptance.json"
)
DEFAULT_GRAPH_SCALE_ACCEPTANCE_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "graph_scale_acceptance.json"
)
DEFAULT_ROAD_CLASS_OVERRIDES_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "road_class_overrides.csv"
)
DEFAULT_OSM_GRAPH_SNAPSHOT_REVIEW_PACKET_PATH = (
    PROJECT_ROOT / "data" / "validation" / "osm_graph_snapshot_review_packet.csv"
)
DEFAULT_OSM_GRAPH_SNAPSHOT_REVIEW_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "osm_graph_snapshot_review_manifest.json"
)
DEFAULT_OSM_GRAPH_SNAPSHOT_REVIEW_DOC_PATH = (
    PROJECT_ROOT / "docs" / "osm_graph_snapshot_review_packet.md"
)
OSM_GRAPH_SNAPSHOT_REVIEW_SCOPE = (
    "OSM graph snapshot review packet only; not source-provenance acceptance, "
    "not reviewed road calibration, not graph-scale acceptance, not validation "
    "acceptance, and not operational routing evidence."
)
OSM_GRAPH_SNAPSHOT_REVIEW_COLUMNS: tuple[str, ...] = (
    "review_id",
    "review_topic",
    "current_evidence",
    "review_status",
    "blocking_reason",
    "required_reviewer_action",
    "followup_artifacts",
    "evidence_input_paths",
    "can_support_cached_osm_gate",
    "claim_boundary",
)


def build_osm_graph_snapshot_review_rows(
    *,
    cache_manifest_path: str | Path = DEFAULT_OSM_GRAPH_CACHE_MANIFEST_PATH,
    source_provenance_manifest_path: str
    | Path = DEFAULT_SOURCE_PROVENANCE_MANIFEST_PATH,
    road_evidence_priority_manifest_path: str
    | Path = DEFAULT_ROAD_EVIDENCE_PRIORITY_MANIFEST_PATH,
    road_source_decision_manifest_path: str
    | Path = DEFAULT_ROAD_SOURCE_DECISION_MANIFEST_PATH,
    graph_scale_manifest_audit_path: str
    | Path = DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_PATH,
    provenance_acceptance_path: str | Path = DEFAULT_PROVENANCE_ACCEPTANCE_PATH,
    graph_scale_acceptance_path: str | Path = DEFAULT_GRAPH_SCALE_ACCEPTANCE_PATH,
    road_class_overrides_path: str | Path = DEFAULT_ROAD_CLASS_OVERRIDES_PATH,
) -> list[dict[str, str]]:
    """Return conservative review rows for the current OSM GraphML snapshot."""

    cache = _read_json_object(cache_manifest_path)
    provenance = _read_json_object(source_provenance_manifest_path)
    road_priority = _read_json_object(road_evidence_priority_manifest_path)
    road_decision = _read_json_object(road_source_decision_manifest_path)
    graph_scale = _read_json_object(graph_scale_manifest_audit_path)
    provenance_acceptance = Path(provenance_acceptance_path)
    graph_scale_acceptance = Path(graph_scale_acceptance_path)
    road_class_overrides = Path(road_class_overrides_path)
    osm_source = _source_record(provenance, "osm_overpass_road_snapshot")
    evidence_paths = _evidence_paths(
        cache_manifest_path=cache_manifest_path,
        source_provenance_manifest_path=source_provenance_manifest_path,
        road_evidence_priority_manifest_path=road_evidence_priority_manifest_path,
        road_source_decision_manifest_path=road_source_decision_manifest_path,
        graph_scale_manifest_audit_path=graph_scale_manifest_audit_path,
    )

    cache_metadata_complete = bool(cache) and all(
        cache.get(field) not in (None, "")
        for field in ("source", "created_utc", "attribution", "node_count", "edge_count")
    )
    live_tests_disabled = cache.get("live_services_required_for_default_tests") is False
    provenance_blocked = (
        not provenance_acceptance.exists()
        or str(osm_source.get("review_status", "")) != "accepted"
    )
    road_priority_blocking = _int(road_priority.get("blocking_priority_count"))
    road_decision_blocking = _int(road_decision.get("blocking_decision_count"))
    graph_scale_blocked = not graph_scale_acceptance.exists()
    boundary_blocked = (
        provenance_blocked
        or road_priority_blocking > 0
        or road_decision_blocking > 0
        or graph_scale_blocked
        or not road_class_overrides.exists()
    )

    return [
        _row(
            review_id="osm_graph_cache_metadata",
            review_topic="OSM GraphML cache metadata and attribution",
            current_evidence=_format_evidence(
                {
                    "cache_manifest_present": bool(cache),
                    "cache_path": cache.get("cache_path", ""),
                    "source": cache.get("source", ""),
                    "created_utc": cache.get("created_utc", ""),
                    "node_count": cache.get("node_count", ""),
                    "edge_count": cache.get("edge_count", ""),
                    "graph_type": cache.get("graph_type", ""),
                    "attribution_present": bool(cache.get("attribution")),
                    "live_services_required_for_default_tests": cache.get(
                        "live_services_required_for_default_tests",
                    ),
                }
            ),
            review_status=(
                "needs_human_review_osm_cache_metadata"
                if cache_metadata_complete and live_tests_disabled
                else "blocked_missing_or_incomplete_osm_cache_metadata"
            ),
            blocking_reason=(
                ""
                if cache_metadata_complete and live_tests_disabled
                else "cache metadata, attribution, counts, or offline-test boundary is incomplete"
            ),
            required_reviewer_action=(
                "Review snapshot date, bbox, source, attribution, Overpass scope, "
                "and offline-test boundary before relying on the cached graph."
            ),
            followup_artifacts=(
                "data/cache/pilot_region_road_manifest.json; "
                "data/manifests/provenance_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            review_id="osm_source_provenance_dependency",
            review_topic="OSM source provenance and license dependency",
            current_evidence=_format_evidence(
                {
                    "source_record_present": bool(osm_source),
                    "source_review_status": osm_source.get("review_status", ""),
                    "source_url_or_citation": osm_source.get("source_url_or_citation", ""),
                    "local_artifact_count": len(
                        _list_value(osm_source.get("local_artifact_paths"))
                    ),
                    "provenance_acceptance_present": provenance_acceptance.exists(),
                }
            ),
            review_status=(
                "blocked_osm_source_provenance_pending"
                if provenance_blocked
                else "needs_human_review_osm_source_provenance"
            ),
            blocking_reason=(
                "OSM source snapshot remains pending review or provenance acceptance is absent"
                if provenance_blocked
                else ""
            ),
            required_reviewer_action=(
                "Review OSM/Overpass source terms, attribution, snapshot date, "
                "local artifacts, and claim boundary before provenance acceptance."
            ),
            followup_artifacts="data/manifests/provenance_acceptance.json",
            evidence_input_paths=evidence_paths,
        ),
        _row(
            review_id="road_evidence_priority_dependency",
            review_topic="Route-exposed road evidence priority",
            current_evidence=_format_evidence(
                {
                    "priority_row_count": road_priority.get("row_count", ""),
                    "blocking_priority_count": road_priority_blocking,
                    "exposed_highway_count": road_priority.get(
                        "exposed_highway_count",
                        "",
                    ),
                    "priority_status_counts": road_priority.get(
                        "priority_status_counts",
                        {},
                    ),
                    "road_class_overrides_present": road_class_overrides.exists(),
                }
            ),
            review_status=(
                "blocked_road_evidence_priority_dependencies"
                if road_priority_blocking or not road_class_overrides.exists()
                else "needs_human_review_road_evidence_priority"
            ),
            blocking_reason=_first_blocker(road_priority),
            required_reviewer_action=(
                "Prioritize exposed road classes and connector assumptions before "
                "using the cached graph for route-level final claims."
            ),
            followup_artifacts=(
                "data/road/road_evidence_priority_packet.csv; "
                "data/parameters/road_class_overrides.csv"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            review_id="road_source_decision_dependency",
            review_topic="Road source decisions and override application",
            current_evidence=_format_evidence(
                {
                    "decision_row_count": road_decision.get("row_count", ""),
                    "blocking_decision_count": road_decision_blocking,
                    "human_review_decision_count": road_decision.get(
                        "human_review_decision_count",
                        "",
                    ),
                    "decision_status_counts": road_decision.get(
                        "decision_status_counts",
                        {},
                    ),
                    "road_source_decision_recorded": road_decision.get(
                        "road_source_decision_recorded",
                        "",
                    ),
                }
            ),
            review_status=(
                "blocked_road_source_decisions_pending"
                if road_decision_blocking
                else "needs_human_review_road_source_decisions"
            ),
            blocking_reason=_first_blocker(road_decision),
            required_reviewer_action=(
                "Choose source-backed, benchmark-only, sensitivity-only, or "
                "excluded treatment for road speed, capacity, disruption, and "
                "override-application requests."
            ),
            followup_artifacts=(
                "data/road/road_source_decision_packet.csv; "
                "data/parameters/road_class_overrides.csv"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            review_id="graph_scale_manifest_dependency",
            review_topic="Source-vs-analysis graph-scale dependency",
            current_evidence=_format_evidence(
                {
                    "source_graph_node_counts": graph_scale.get(
                        "source_graph_node_counts",
                        [],
                    ),
                    "source_graph_edge_counts": graph_scale.get(
                        "source_graph_edge_counts",
                        [],
                    ),
                    "analysis_graph_node_counts": graph_scale.get(
                        "analysis_graph_node_counts",
                        [],
                    ),
                    "analysis_graph_edge_counts": graph_scale.get(
                        "analysis_graph_edge_counts",
                        [],
                    ),
                    "graph_scale_acceptance_present": graph_scale_acceptance.exists(),
                }
            ),
            review_status=(
                "blocked_graph_scale_acceptance_missing"
                if graph_scale_blocked
                else "needs_human_review_graph_scale_manifest_scope"
            ),
            blocking_reason=(
                "data/manifests/graph_scale_acceptance.json is absent"
                if graph_scale_blocked
                else ""
            ),
            required_reviewer_action=(
                "Decide whether reduced analysis graphs are final method or "
                "scaffold shortcut before treating OSM snapshot scale as accepted."
            ),
            followup_artifacts="data/manifests/graph_scale_acceptance.json",
            evidence_input_paths=evidence_paths,
        ),
        _row(
            review_id="osm_snapshot_claim_boundary",
            review_topic="Cached OSM input claim boundary",
            current_evidence=_format_evidence(
                {
                    "boundary_blocked": boundary_blocked,
                    "provenance_acceptance_present": provenance_acceptance.exists(),
                    "graph_scale_acceptance_present": graph_scale_acceptance.exists(),
                    "road_class_overrides_present": road_class_overrides.exists(),
                    "cached_osm_gate_closure_candidate_count": 0,
                    "publication_ready": False,
                }
            ),
            review_status=(
                "blocked_osm_snapshot_claim_boundary"
                if boundary_blocked
                else "needs_human_review_osm_snapshot_claim_boundary"
            ),
            blocking_reason=(
                "source provenance, road overrides, road source decisions, or graph-scale acceptance remain unresolved"
                if boundary_blocked
                else ""
            ),
            required_reviewer_action=(
                "Keep the cached GraphML input scoped as quasi-real scaffold "
                "evidence until source, road-input, and graph-scale decisions are accepted."
            ),
            followup_artifacts=(
                "data/manifests/provenance_acceptance.json; "
                "data/parameters/road_class_overrides.csv; "
                "data/manifests/graph_scale_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
    ]


def write_osm_graph_snapshot_review_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_OSM_GRAPH_SNAPSHOT_REVIEW_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_OSM_GRAPH_SNAPSHOT_REVIEW_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_OSM_GRAPH_SNAPSHOT_REVIEW_DOC_PATH,
    cache_manifest_path: str | Path = DEFAULT_OSM_GRAPH_CACHE_MANIFEST_PATH,
    source_provenance_manifest_path: str
    | Path = DEFAULT_SOURCE_PROVENANCE_MANIFEST_PATH,
    road_evidence_priority_manifest_path: str
    | Path = DEFAULT_ROAD_EVIDENCE_PRIORITY_MANIFEST_PATH,
    road_source_decision_manifest_path: str
    | Path = DEFAULT_ROAD_SOURCE_DECISION_MANIFEST_PATH,
    graph_scale_manifest_audit_path: str
    | Path = DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_PATH,
) -> dict[str, Any]:
    """Write OSM graph snapshot review CSV, manifest, and Markdown."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=OSM_GRAPH_SNAPSHOT_REVIEW_COLUMNS,
            lineterminator="\n",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in OSM_GRAPH_SNAPSHOT_REVIEW_COLUMNS
                }
            )

    summary = build_osm_graph_snapshot_review_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        cache_manifest_path=cache_manifest_path,
        source_provenance_manifest_path=source_provenance_manifest_path,
        road_evidence_priority_manifest_path=road_evidence_priority_manifest_path,
        road_source_decision_manifest_path=road_source_decision_manifest_path,
        graph_scale_manifest_audit_path=graph_scale_manifest_audit_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_osm_graph_snapshot_review_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_osm_graph_snapshot_review_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_OSM_GRAPH_SNAPSHOT_REVIEW_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_OSM_GRAPH_SNAPSHOT_REVIEW_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_OSM_GRAPH_SNAPSHOT_REVIEW_DOC_PATH,
    cache_manifest_path: str | Path = DEFAULT_OSM_GRAPH_CACHE_MANIFEST_PATH,
    source_provenance_manifest_path: str
    | Path = DEFAULT_SOURCE_PROVENANCE_MANIFEST_PATH,
    road_evidence_priority_manifest_path: str
    | Path = DEFAULT_ROAD_EVIDENCE_PRIORITY_MANIFEST_PATH,
    road_source_decision_manifest_path: str
    | Path = DEFAULT_ROAD_SOURCE_DECISION_MANIFEST_PATH,
    graph_scale_manifest_audit_path: str
    | Path = DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for OSM snapshot review."""

    status_counts = _counts(row.get("review_status", "") for row in rows)
    blocking_count = sum(
        1 for row in rows if str(row.get("review_status", "")).startswith("blocked_")
    )
    human_review_count = sum(
        1
        for row in rows
        if str(row.get("review_status", "")).startswith("needs_human_review_")
    )
    return {
        "schema_version": 1,
        "result_scope": OSM_GRAPH_SNAPSHOT_REVIEW_SCOPE,
        "claim_boundary": (
            OSM_GRAPH_SNAPSHOT_REVIEW_SCOPE
            + " It cannot create provenance, road override, validation, or graph-scale acceptance."
        ),
        "row_count": len(rows),
        "review_ids": [str(row.get("review_id", "")) for row in rows],
        "review_status_counts": status_counts,
        "blocking_review_count": blocking_count,
        "human_review_count": human_review_count,
        "cached_osm_gate_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "cache_manifest": _display_path(Path(cache_manifest_path)),
            "source_provenance_manifest": _display_path(
                Path(source_provenance_manifest_path)
            ),
            "road_evidence_priority_manifest": _display_path(
                Path(road_evidence_priority_manifest_path)
            ),
            "road_source_decision_manifest": _display_path(
                Path(road_source_decision_manifest_path)
            ),
            "graph_scale_manifest_audit": _display_path(
                Path(graph_scale_manifest_audit_path)
            ),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": [
            "review OSM/Overpass attribution, snapshot date, bbox, and local cache metadata",
            "resolve source-provenance review before using the cached graph for final claims",
            "prioritize exposed road classes and connector assumptions before route-level claims",
            "decide graph-scale method before interpreting source-vs-analysis graph counts",
            "record accepted decisions only in formal provenance, graph-scale, and road override artifacts",
        ],
        "remaining_blockers": _remaining_blockers(rows),
    }


def build_osm_graph_snapshot_review_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return Markdown OSM graph snapshot review worksheet."""

    lines = [
        "# OSM Graph Snapshot Review Packet",
        "",
        str(manifest.get("claim_boundary", OSM_GRAPH_SNAPSHOT_REVIEW_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Review rows: {manifest.get('row_count', 0)}",
        f"- Blocking rows: {manifest.get('blocking_review_count', 0)}",
        f"- Human-review rows: {manifest.get('human_review_count', 0)}",
        f"- Status counts: `{manifest.get('review_status_counts', {})}`",
        "",
        "## Review Rows",
        "",
        "| Review | Status | Evidence | Required Action |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {review} | {status} | {evidence} | {action} |".format(
                review=_cell(row.get("review_id", "")),
                status=_cell(row.get("review_status", "")),
                evidence=_cell(row.get("current_evidence", "")),
                action=_cell(row.get("required_reviewer_action", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This packet is a reviewer worksheet, not an acceptance record.",
            "- It does not refresh or validate live OSM/Overpass data.",
            "- It does not create reviewed road-class overrides or graph-scale acceptance.",
            "- Keep cached OSM claims scaffold-scoped until formal evidence artifacts are reviewed.",
            "",
        ]
    )
    return "\n".join(lines)


def _row(
    *,
    review_id: str,
    review_topic: str,
    current_evidence: str,
    review_status: str,
    blocking_reason: str,
    required_reviewer_action: str,
    followup_artifacts: str,
    evidence_input_paths: str,
) -> dict[str, str]:
    return {
        "review_id": review_id,
        "review_topic": review_topic,
        "current_evidence": current_evidence,
        "review_status": review_status,
        "blocking_reason": blocking_reason,
        "required_reviewer_action": required_reviewer_action,
        "followup_artifacts": followup_artifacts,
        "evidence_input_paths": evidence_input_paths,
        "can_support_cached_osm_gate": "false",
        "claim_boundary": OSM_GRAPH_SNAPSHOT_REVIEW_SCOPE,
    }


def _source_record(provenance_manifest: Mapping[str, Any], source_id: str) -> dict[str, Any]:
    records = provenance_manifest.get("records", [])
    if not isinstance(records, list):
        return {}
    for record in records:
        if isinstance(record, Mapping) and record.get("source_id") == source_id:
            return dict(record)
    return {}


def _evidence_paths(
    *,
    cache_manifest_path: str | Path,
    source_provenance_manifest_path: str | Path,
    road_evidence_priority_manifest_path: str | Path,
    road_source_decision_manifest_path: str | Path,
    graph_scale_manifest_audit_path: str | Path,
) -> str:
    paths = [
        cache_manifest_path,
        source_provenance_manifest_path,
        road_evidence_priority_manifest_path,
        PROJECT_ROOT / "data" / "road" / "road_evidence_priority_packet.csv",
        road_source_decision_manifest_path,
        PROJECT_ROOT / "data" / "road" / "road_source_decision_packet.csv",
        graph_scale_manifest_audit_path,
        PROJECT_ROOT / "data" / "validation" / "graph_scale_manifest_audit.csv",
    ]
    return "; ".join(_display_path(Path(path)) for path in paths)


def _format_evidence(fields: Mapping[str, object]) -> str:
    return "; ".join(
        f"{key}={_format_value(value)}" for key, value in fields.items()
    )


def _format_value(value: object) -> str:
    if isinstance(value, Mapping):
        return json.dumps(value, sort_keys=True)
    if isinstance(value, list):
        return json.dumps(value)
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def _first_blocker(manifest: Mapping[str, Any]) -> str:
    blockers = manifest.get("remaining_blockers")
    if isinstance(blockers, list) and blockers:
        return str(blockers[0])
    return ""


def _remaining_blockers(rows: Sequence[Mapping[str, str]]) -> list[str]:
    blockers: list[str] = []
    for row in rows:
        status = str(row.get("review_status", ""))
        reason = str(row.get("blocking_reason", "")).strip()
        if status.startswith("blocked_") and reason:
            blockers.append(reason)
    return blockers


def _read_json_object(path: str | Path) -> dict[str, Any]:
    candidate = Path(path)
    if not candidate.exists():
        return {}
    try:
        value = json.loads(candidate.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def _list_value(value: object) -> list[object]:
    return value if isinstance(value, list) else []


def _counts(values: Iterable[object]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _int(value: object) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()
