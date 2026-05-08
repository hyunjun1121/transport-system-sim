"""Context-source cache request packet.

This module turns context-only public source blockers into concrete cache or
exclusion work items. It is a reviewer aid only: it does not fetch public data,
cache source extracts, certify licenses, or create provenance acceptance.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.source_provenance import (
    DEFAULT_SOURCE_PROVENANCE_PATH,
    load_source_provenance_manifest,
)
from src.realworld.source_provenance_priority_packet import (
    DEFAULT_SOURCE_PROVENANCE_PRIORITY_PACKET_PATH,
    SOURCE_PROVENANCE_PRIORITY_SCOPE,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_PACKET_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "source_context_cache_request_packet.csv"
)
DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "source_context_cache_request_manifest.json"
)
DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_DOC_PATH = (
    PROJECT_ROOT / "docs" / "source_context_cache_request_packet.md"
)
SOURCE_CONTEXT_CACHE_REQUEST_SCOPE = (
    "Source context-cache request packet only; not source acceptance, not "
    "license certification, not cached source evidence, not provenance gate "
    "closure, and not operational routing approval."
)
SOURCE_CONTEXT_CACHE_REQUEST_COLUMNS: tuple[str, ...] = (
    "source_id",
    "source_name",
    "source_type",
    "review_priority",
    "cache_request_status",
    "source_url_or_citation",
    "context_local_artifacts",
    "target_cache_artifacts",
    "target_cache_artifacts_present",
    "available_fetch_or_derivation_helpers",
    "required_reviewer_decision",
    "required_cache_action",
    "url_required_reviewer_actions",
    "target_acceptance_artifact",
    "publication_use_status",
    "can_support_final_provenance_gate",
    "claim_boundary",
    "notes",
)

_TARGETS_BY_SOURCE_ID: dict[str, tuple[tuple[str, ...], tuple[str, ...], str]] = {
    "seoul_shortest_path_api_context": (
        (
            "data/rail/pilot_rail_shortest_path_cache.csv",
            "data/rail/pilot_rail_shortest_path_raw.json",
        ),
        (
            "scripts/fetch_rail_shortest_path_cache.py",
            "scripts/derive_rail_shortest_path_evidence.py",
            "docs/rail_shortest_path_cache_schema.md",
        ),
        (
            "provide DATA_GO_KR_KEY or reviewed cached API payload, retain raw "
            "response, derive travel-time evidence, or exclude this source"
        ),
    ),
    "seoul_timetable_api_context": (
        (
            "data/rail/pilot_rail_timetable_cache.csv",
            "data/rail/pilot_rail_timetable_raw.json",
        ),
        (
            "scripts/fetch_rail_timetable_cache.py",
            "scripts/derive_rail_service_evidence.py",
            "scripts/derive_rail_headway_evidence.py",
            "docs/rail_timetable_cache_schema.md",
        ),
        (
            "provide DATA_GO_KR_KEY or reviewed cached timetable payload, "
            "retain raw response, derive headway/travel-time evidence, or "
            "exclude this source"
        ),
    ),
    "ktdb_public_transport_gtfs_context": (
        (
            "data/rail/pilot_gtfs.zip",
            "data/rail/pilot_gtfs/",
        ),
        (
            "scripts/derive_rail_gtfs_evidence.py",
            "docs/rail_gtfs_cache_schema.md",
        ),
        (
            "provide reviewed KTDB or equivalent GTFS zip/directory with "
            "license and attribution review, derive rail timing evidence, or "
            "exclude this source"
        ),
    ),
    "metro9_capacity_context": (
        (
            "data/rail/metro9_capacity_source_extract.csv",
            "data/rail/metro9_capacity_source_raw.html",
        ),
        (
            "data/parameters/rail_assumptions.csv",
            "data/parameters/rail_service_evidence.csv",
        ),
        (
            "cache a reviewed operator capacity extract or explicitly retain "
            "rail capacity as sensitivity-only within the final claim boundary"
        ),
    ),
}


def build_source_context_cache_request_rows(
    *,
    source_priority_rows: Sequence[Mapping[str, str]] | None = None,
    source_priority_path: str | Path = DEFAULT_SOURCE_PROVENANCE_PRIORITY_PACKET_PATH,
    provenance_manifest_path: str | Path = DEFAULT_SOURCE_PROVENANCE_PATH,
) -> list[dict[str, str]]:
    """Return one cache-request row per context-only public source."""

    priority_rows = (
        list(source_priority_rows)
        if source_priority_rows is not None
        else _read_csv_rows(source_priority_path)
    )
    provenance = load_source_provenance_manifest(provenance_manifest_path)
    records_by_id = {record.source_id: record for record in provenance.records}
    rows = [
        _request_row(row, records_by_id.get(str(row.get("source_id", ""))))
        for row in priority_rows
        if row.get("review_status") == "context_only_not_cached"
        or row.get("priority_status") == "blocked_context_only_source_not_cached"
    ]
    rows.sort(key=lambda row: (row["review_priority"], row["source_id"]))
    return rows


def write_source_context_cache_request_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_DOC_PATH,
    source_priority_path: str | Path = DEFAULT_SOURCE_PROVENANCE_PRIORITY_PACKET_PATH,
    provenance_manifest_path: str | Path = DEFAULT_SOURCE_PROVENANCE_PATH,
) -> dict[str, Any]:
    """Write source context-cache request CSV, manifest, and Markdown."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=SOURCE_CONTEXT_CACHE_REQUEST_COLUMNS,
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in SOURCE_CONTEXT_CACHE_REQUEST_COLUMNS
                }
            )

    summary = build_source_context_cache_request_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        source_priority_path=source_priority_path,
        provenance_manifest_path=provenance_manifest_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_source_context_cache_request_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_source_context_cache_request_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_DOC_PATH,
    source_priority_path: str | Path = DEFAULT_SOURCE_PROVENANCE_PRIORITY_PACKET_PATH,
    provenance_manifest_path: str | Path = DEFAULT_SOURCE_PROVENANCE_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for context-source cache requests."""

    status_counts = _counts(row.get("cache_request_status", "") for row in rows)
    blocking_count = sum(
        1
        for row in rows
        if str(row.get("cache_request_status", "")).startswith("blocked_")
    )
    missing_target_count = sum(
        1
        for row in rows
        if str(row.get("target_cache_artifacts_present", "")).lower() != "true"
    )
    return {
        "schema_version": 1,
        "result_scope": SOURCE_CONTEXT_CACHE_REQUEST_SCOPE,
        "claim_boundary": (
            "This packet converts context-only public sources into cache or "
            "exclusion requests. It does not fetch data, certify terms, create "
            "source snapshots, or close data-provenance, rail-evidence, "
            "validation, reproducibility, or final-study gates."
        ),
        "row_count": len(rows),
        "context_source_count": len(rows),
        "blocking_request_count": blocking_count,
        "missing_target_cache_artifact_count": missing_target_count,
        "cache_request_status_counts": status_counts,
        "review_priority_counts": _counts(
            row.get("review_priority", "") for row in rows
        ),
        "provenance_gate_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "source_provenance_priority_packet": _display_path(source_priority_path),
            "source_provenance_manifest": _display_path(provenance_manifest_path),
        },
        "outputs": {
            "csv": _display_path(output_path),
            "manifest": _display_path(manifest_path),
            "doc": _display_path(doc_path),
        },
        "review_items": [
            "for each row, either cache the reviewed source extract with terms/attribution review or exclude the source from final claims",
            "retain raw API/page responses when a source is cached for reproducibility",
            "preserve SHA256 or equivalent digest evidence before deriving rail-service rows",
            "do not create data/manifests/provenance_acceptance.json until retained sources are reviewed",
        ],
        "remaining_blockers": [
            "context-only public sources still lack reviewed cached extracts or explicit exclusion decisions",
            "license, attribution, snapshot, and reproducibility review are still required for retained public sources",
            "formal provenance acceptance record is absent",
        ],
    }


def build_source_context_cache_request_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return Markdown for the context-source cache request packet."""

    lines = [
        "# Source Context Cache Request Packet",
        "",
        str(manifest.get("claim_boundary", SOURCE_CONTEXT_CACHE_REQUEST_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Context source requests: {manifest.get('row_count', 0)}",
        f"- Blocking requests: {manifest.get('blocking_request_count', 0)}",
        f"- Missing target cache artifacts: {manifest.get('missing_target_cache_artifact_count', 0)}",
        "",
        "## Cache Requests",
        "",
        "| Source | Status | Target Cache Artifacts | Helpers | Required Action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {source} | {status} | {targets} | {helpers} | {action} |".format(
                source=_cell(row.get("source_id", "")),
                status=_cell(row.get("cache_request_status", "")),
                targets=_cell(row.get("target_cache_artifacts", "")),
                helpers=_cell(row.get("available_fetch_or_derivation_helpers", "")),
                action=_cell(row.get("required_cache_action", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Required Reviewer Actions",
            "",
            "- Cache reviewed source extracts or explicitly exclude each context-only source from final claims.",
            "- Review terms, attribution, extraction date, retained raw response, and reproducibility before using a cached source.",
            "- Treat helper scripts as derivation paths only; they do not prove source suitability or close acceptance gates.",
            "- Create `data/manifests/provenance_acceptance.json` only after source-backed review.",
            "",
        ]
    )
    return "\n".join(lines)


def _request_row(
    row: Mapping[str, str],
    record: object | None,
) -> dict[str, str]:
    source_id = str(row.get("source_id", ""))
    targets, helpers, cache_action = _TARGETS_BY_SOURCE_ID.get(
        source_id,
        (
            ("reviewer_defined_cached_source_extract",),
            (),
            "cache a reviewed source extract or exclude this source from final claims",
        ),
    )
    target_present = all(_path_exists(path) for path in targets)
    context_artifacts = (
        tuple(getattr(record, "local_artifact_paths", ())) if record is not None else ()
    )
    status = (
        "needs_human_review_cached_extract_present"
        if target_present
        else "blocked_missing_context_source_cache"
    )
    return {
        "source_id": source_id,
        "source_name": str(row.get("source_name", "")),
        "source_type": str(row.get("source_type", "")),
        "review_priority": str(row.get("review_priority", "")),
        "cache_request_status": status,
        "source_url_or_citation": str(row.get("source_url_or_citation", "")),
        "context_local_artifacts": "; ".join(context_artifacts),
        "target_cache_artifacts": "; ".join(targets),
        "target_cache_artifacts_present": _bool_text(target_present),
        "available_fetch_or_derivation_helpers": "; ".join(helpers),
        "required_reviewer_decision": str(row.get("required_reviewer_decision", "")),
        "required_cache_action": cache_action,
        "url_required_reviewer_actions": str(row.get("url_required_reviewer_actions", "")),
        "target_acceptance_artifact": str(
            row.get("target_acceptance_artifact", "data/manifests/provenance_acceptance.json")
        ),
        "publication_use_status": str(row.get("publication_use_status", "")),
        "can_support_final_provenance_gate": "false",
        "claim_boundary": SOURCE_CONTEXT_CACHE_REQUEST_SCOPE,
        "notes": str(row.get("notes", "")),
    }


def _read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _path_exists(path: str) -> bool:
    if path.endswith("/"):
        return (PROJECT_ROOT / path).is_dir()
    return (PROJECT_ROOT / path).exists()


def _counts(values: Iterable[object]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value).strip()
        if not key:
            continue
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _bool_text(value: object) -> str:
    return str(bool(value)).lower()


def _display_path(path: str | Path) -> str:
    filepath = Path(path)
    try:
        return filepath.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return filepath.as_posix()


def _cell(value: object) -> str:
    text = str(value).replace("\n", " ").replace("|", "\\|").strip()
    return text or "-"


__all__ = [
    "DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_DOC_PATH",
    "DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_MANIFEST_PATH",
    "DEFAULT_SOURCE_CONTEXT_CACHE_REQUEST_PACKET_PATH",
    "SOURCE_CONTEXT_CACHE_REQUEST_COLUMNS",
    "SOURCE_CONTEXT_CACHE_REQUEST_SCOPE",
    "build_source_context_cache_request_rows",
    "write_source_context_cache_request_packet",
]
