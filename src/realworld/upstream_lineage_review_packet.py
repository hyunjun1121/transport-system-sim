"""Upstream evidence and benchmark lineage review packet.

This module builds a reviewer-facing packet for the Phase 9
``upstream_evidence_and_benchmarks`` invalidation rows. It is deliberately a
review aid only: it collects artifact paths, hashes, rerun commands, audit
commands, and tests, but it does not update the authoritative closeout CSV and
does not create reviewer signoff.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ACTION_QUEUE_PATH = (
    PROJECT_ROOT / "data" / "validation" / "artifact_invalidation_closeout_action_queue.csv"
)
DEFAULT_OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "artifact_invalidation_upstream_lineage_review_packet.csv"
)
DEFAULT_MANIFEST_PATH = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "artifact_invalidation_upstream_lineage_review_manifest.json"
)
DEFAULT_DOC_PATH = (
    PROJECT_ROOT / "docs" / "artifact_invalidation_upstream_lineage_review_packet.md"
)
DEFAULT_LEDGER_PATH = (
    PROJECT_ROOT
    / "docs"
    / "recovery"
    / "agent_ledgers"
    / "phase9_upstream_evidence_benchmark_regeneration_20260605.md"
)

SOURCE_ACTION_BATCH = "upstream_evidence_and_benchmarks"
CLAIM_BOUNDARY = (
    "Upstream evidence and benchmark lineage review packet only; not an "
    "artifact-invalidation closeout record, not reviewer signoff, not "
    "publication readiness, not final-study readiness, and not formal "
    "acceptance."
)

REVIEWER_STATUS = "unsigned"

FIELDNAMES = (
    "invalidation_row_id",
    "action_order",
    "action_batch",
    "upstream_change_group",
    "stale_downstream_group",
    "recommended_disposition",
    "reviewer_role",
    "reviewer_signoff_status",
    "packet_can_close_row",
    "suggested_closeout_status_after_signoff",
    "suggested_can_clear_invalidation_gate_after_signoff",
    "affected_artifact_count",
    "missing_artifact_count",
    "affected_artifacts_json",
    "rerun_commands_json",
    "audit_commands_json",
    "targeted_test_commands_json",
    "claim_boundary_review_commands_json",
    "lineage_status",
    "remaining_reviewer_action",
    "source_ledger",
    "claim_boundary",
)


SNAPSHOT_ROOT = "data/road/snapshots/songpa_public_demo_phase9_upstream_20260605T000000Z"

AFFECTED_ARTIFACTS_BY_ROW: dict[str, tuple[str, ...]] = {
    "region_boundary->road_snapshots": (
        f"{SNAPSHOT_ROOT}/road_snapshot_manifest.json",
        f"{SNAPSHOT_ROOT}/road.graphml",
        f"{SNAPSHOT_ROOT}/road_nodes.csv",
        f"{SNAPSHOT_ROOT}/road_edges.csv",
        "data/validation/osm_graph_snapshot_review_packet.csv",
        "data/validation/osm_graph_snapshot_review_manifest.json",
        "docs/osm_graph_snapshot_review_packet.md",
    ),
    "region_boundary->connector_audits": (
        f"{SNAPSHOT_ROOT}/connector_audit.csv",
        f"{SNAPSHOT_ROOT}/road_snapshot_manifest.json",
        "data/validation/osm_graph_snapshot_review_packet.csv",
        "data/validation/osm_graph_snapshot_review_manifest.json",
        "docs/osm_graph_snapshot_review_packet.md",
    ),
    "road_snapshot_or_evidence->route_exposure": (
        "data/validation/canonical_route_road_evidence_exposure.csv",
        "data/validation/canonical_route_road_evidence_exposure_manifest.json",
        "data/validation/canonical_route_road_evidence_exposure_summary.md",
        "docs/route_road_evidence_exposure.md",
    ),
    "road_snapshot_or_evidence->graph_scale_diagnostics": (
        "data/validation/graph_scale_route_comparison.csv",
        "data/validation/graph_scale_route_comparison_summary.md",
        "data/validation/graph_scale_alternate_routes.csv",
        "data/validation/graph_scale_alternate_routes_summary.md",
        "data/validation/graph_scale_multi_corridor_routes.csv",
        "data/validation/graph_scale_multi_corridor_routes_summary.md",
        "data/validation/graph_scale_review_packet.csv",
        "data/validation/graph_scale_review_manifest.json",
        "data/validation/graph_scale_result_comparison.csv",
        "data/validation/graph_scale_result_comparison_manifest.json",
        "data/validation/graph_scale_method_decision_packet.csv",
        "data/validation/graph_scale_method_decision_manifest.json",
        "data/validation/graph_scale_strategy_readiness_packet.csv",
        "data/validation/graph_scale_strategy_readiness_manifest.json",
        "data/validation/graph_scale_manifest_audit.csv",
        "data/validation/graph_scale_manifest_audit_manifest.json",
    ),
    "region_boundary->benchmarks": (
        "data/validation/external_route_benchmarks_osrm.csv",
        "data/validation/osrm_route_benchmark_manifest.json",
        "data/validation/osrm_route_benchmark_summary.md",
        "data/validation/validation_benchmark_readiness_packet.csv",
        "data/validation/validation_benchmark_readiness_manifest.json",
        "data/validation/validation_benchmark_decision_packet.csv",
        "data/validation/validation_benchmark_decision_manifest.json",
        "data/validation/osm_graph_snapshot_review_packet.csv",
        "data/validation/osm_graph_snapshot_review_manifest.json",
    ),
    "road_snapshot_or_evidence->benchmarks": (
        "data/validation/external_route_benchmarks_osrm.csv",
        "data/validation/osrm_route_benchmark_manifest.json",
        "data/validation/osrm_route_benchmark_summary.md",
        "data/validation/osrm_route_raw/route_bus_direct.json",
        "data/validation/osrm_route_raw/route_last_mile.json",
        "data/validation/osrm_route_raw/route_rail_access.json",
        "data/validation/canonical_route_road_evidence_exposure.csv",
        "data/validation/canonical_route_road_evidence_exposure_manifest.json",
    ),
    "rail_source_or_timing->multimodal_benchmarks": (
        "data/rail/rail_source_decision_packet.csv",
        "data/rail/rail_source_decision_manifest.json",
        "data/rail/rail_evidence_priority_packet.csv",
        "data/rail/rail_evidence_priority_manifest.json",
        "data/rail/rail_timing_source_request_packet.csv",
        "data/rail/rail_timing_source_request_manifest.json",
        "data/rail/rail_bounded_treatment_audit.json",
        "docs/rail_bounded_treatment_audit.md",
    ),
    "rail_source_or_timing->rail_stress_profiles": (
        "data/rail/rail_transit_stress_profile_packet.csv",
        "data/rail/rail_transit_stress_profile_manifest.json",
        "docs/rail_transit_stress_profile_packet.md",
        "data/rail/rail_bounded_treatment_audit.json",
        "docs/rail_bounded_treatment_audit.md",
    ),
    "benchmark_cache_or_threshold->benchmark_review_packets": (
        "data/validation/validation_benchmark_readiness_packet.csv",
        "data/validation/validation_benchmark_readiness_manifest.json",
        "docs/validation_benchmark_readiness_packet.md",
        "data/validation/validation_benchmark_decision_packet.csv",
        "data/validation/validation_benchmark_decision_manifest.json",
        "docs/validation_benchmark_decision_packet.md",
        "data/validation/osrm_route_benchmark_manifest.json",
        "docs/osrm_route_benchmark_manifest.md",
        "data/validation/benchmark_threshold_table.csv",
        "data/validation/benchmark_threshold_manifest.json",
    ),
    "benchmark_cache_or_threshold->claim_boundaries": (
        "data/manifests/claim_alignment_review_packet.csv",
        "data/manifests/claim_alignment_review_manifest.json",
        "docs/claim_alignment_review_packet.md",
        "data/validation/claim_language_guard.csv",
        "data/validation/claim_language_guard_manifest.json",
        "docs/claim_language_guard.md",
        "docs/validation_benchmark_decision_packet.md",
        "docs/validation_benchmark_readiness_packet.md",
    ),
}

RERUN_COMMANDS_BY_ROW: dict[str, tuple[str, ...]] = {
    "region_boundary->road_snapshots": (
        r".\.venv\Scripts\python scripts\write_road_snapshot.py --region-id songpa_public_demo --source cached --output-dir data\road\snapshots\songpa_public_demo_phase9_upstream_20260605T000000Z --created-utc 2026-06-05T00:00:00+00:00",
        r".\.venv\Scripts\python scripts\write_osm_graph_snapshot_review_packet.py",
    ),
    "region_boundary->connector_audits": (
        r".\.venv\Scripts\python scripts\write_road_snapshot.py --region-id songpa_public_demo --source cached --output-dir data\road\snapshots\songpa_public_demo_phase9_upstream_20260605T000000Z --created-utc 2026-06-05T00:00:00+00:00",
    ),
    "road_snapshot_or_evidence->route_exposure": (
        r".\.venv\Scripts\python scripts\write_route_road_evidence_exposure.py",
    ),
    "road_snapshot_or_evidence->graph_scale_diagnostics": (
        r".\.venv\Scripts\python scripts\run_graph_scale_diagnostics.py",
        r".\.venv\Scripts\python scripts\write_graph_scale_review_packet.py",
        r".\.venv\Scripts\python scripts\write_graph_scale_result_comparison.py",
        r".\.venv\Scripts\python scripts\write_graph_scale_method_decision_packet.py",
        r".\.venv\Scripts\python scripts\write_graph_scale_strategy_readiness_packet.py",
        r".\.venv\Scripts\python scripts\audit_graph_scale_manifests.py",
    ),
    "region_boundary->benchmarks": (
        r".\.venv\Scripts\python scripts\run_osrm_route_benchmark.py",
        r".\.venv\Scripts\python scripts\write_osrm_snapshot_manifest.py",
        r".\.venv\Scripts\python scripts\write_validation_benchmark_readiness_packet.py",
        r".\.venv\Scripts\python scripts\write_validation_benchmark_decision_packet.py",
    ),
    "road_snapshot_or_evidence->benchmarks": (
        r".\.venv\Scripts\python scripts\run_osrm_route_benchmark.py",
        r".\.venv\Scripts\python scripts\write_osrm_snapshot_manifest.py",
    ),
    "rail_source_or_timing->multimodal_benchmarks": (
        r".\.venv\Scripts\python scripts\write_rail_transit_stress_profile_packet.py",
        r".\.venv\Scripts\python scripts\audit_rail_bounded_treatments.py",
    ),
    "rail_source_or_timing->rail_stress_profiles": (
        r".\.venv\Scripts\python scripts\write_rail_transit_stress_profile_packet.py",
        r".\.venv\Scripts\python scripts\audit_rail_bounded_treatments.py",
    ),
    "benchmark_cache_or_threshold->benchmark_review_packets": (
        r".\.venv\Scripts\python scripts\write_validation_benchmark_readiness_packet.py",
        r".\.venv\Scripts\python scripts\write_validation_benchmark_decision_packet.py",
    ),
    "benchmark_cache_or_threshold->claim_boundaries": (
        r".\.venv\Scripts\python scripts\write_claim_alignment_review_packet.py",
        r".\.venv\Scripts\python scripts\audit_claim_language.py --fail-on-blockers",
    ),
}

AUDIT_COMMANDS_BY_ROW: dict[str, tuple[str, ...]] = {
    "region_boundary->road_snapshots": (
        r".\.venv\Scripts\python tests\test_realworld_osm_graph_snapshot_review_packet.py",
    ),
    "region_boundary->connector_audits": (
        r".\.venv\Scripts\python tests\test_realworld_osm_network.py",
    ),
    "road_snapshot_or_evidence->route_exposure": (
        r".\.venv\Scripts\python tests\test_realworld_route_road_evidence_exposure.py",
    ),
    "road_snapshot_or_evidence->graph_scale_diagnostics": (
        r".\.venv\Scripts\python tests\test_realworld_graph_scale_review.py",
        r".\.venv\Scripts\python tests\test_realworld_graph_scale_result_comparison.py",
        r".\.venv\Scripts\python tests\test_realworld_graph_scale_method_decision_packet.py",
        r".\.venv\Scripts\python tests\test_realworld_graph_scale_strategy_readiness_packet.py",
    ),
    "region_boundary->benchmarks": (
        r".\.venv\Scripts\python tests\test_realworld_osrm_snapshot_manifest.py",
        r".\.venv\Scripts\python tests\test_realworld_validation_benchmark_readiness_packet.py",
        r".\.venv\Scripts\python tests\test_realworld_validation_benchmark_decision_packet.py",
    ),
    "road_snapshot_or_evidence->benchmarks": (
        r".\.venv\Scripts\python tests\test_realworld_osrm_snapshot_manifest.py",
    ),
    "rail_source_or_timing->multimodal_benchmarks": (
        r".\.venv\Scripts\python tests\test_realworld_rail_evidence.py",
        r".\.venv\Scripts\python tests\test_realworld_rail_bounded_treatment_audit.py",
    ),
    "rail_source_or_timing->rail_stress_profiles": (
        r".\.venv\Scripts\python tests\test_realworld_rail_transit_stress_profile_packet.py",
        r".\.venv\Scripts\python tests\test_realworld_rail_bounded_treatment_audit.py",
    ),
    "benchmark_cache_or_threshold->benchmark_review_packets": (
        r".\.venv\Scripts\python tests\test_realworld_validation_benchmark_readiness_packet.py",
        r".\.venv\Scripts\python tests\test_realworld_validation_benchmark_decision_packet.py",
    ),
    "benchmark_cache_or_threshold->claim_boundaries": (
        r".\.venv\Scripts\python tests\test_realworld_claim_alignment_review_packet.py",
        r".\.venv\Scripts\python tests\test_realworld_claim_language_guard.py",
    ),
}

CLAIM_BOUNDARY_COMMANDS_BY_ROW: dict[str, tuple[str, ...]] = {
    row_id: (r".\.venv\Scripts\python scripts\audit_claim_language.py --fail-on-blockers",)
    for row_id in AFFECTED_ARTIFACTS_BY_ROW
}


def build_upstream_lineage_review_rows(
    *,
    action_queue_path: str | Path = DEFAULT_ACTION_QUEUE_PATH,
    project_root: str | Path = PROJECT_ROOT,
    source_ledger_path: str | Path = DEFAULT_LEDGER_PATH,
) -> list[dict[str, str]]:
    """Build review rows for the upstream action batch."""

    root = Path(project_root)
    queue_rows = [
        row
        for row in _read_csv_rows(action_queue_path)
        if row.get("action_batch") == SOURCE_ACTION_BATCH
    ]
    rows: list[dict[str, str]] = []
    for action in queue_rows:
        row_id = str(action["invalidation_row_id"])
        artifacts = _artifact_records(
            AFFECTED_ARTIFACTS_BY_ROW.get(row_id, ()),
            project_root=root,
        )
        missing = [item for item in artifacts if not item["exists"]]
        targeted_tests = tuple(
            item.strip()
            for item in str(action.get("targeted_test_command", "")).split("&&")
            if item.strip()
        )
        rows.append(
            {
                "invalidation_row_id": row_id,
                "action_order": str(action.get("action_order", "")),
                "action_batch": SOURCE_ACTION_BATCH,
                "upstream_change_group": str(action.get("upstream_change_group", "")),
                "stale_downstream_group": str(action.get("stale_downstream_group", "")),
                "recommended_disposition": str(action.get("recommended_disposition", "")),
                "reviewer_role": str(action.get("reviewer_role", "")),
                "reviewer_signoff_status": REVIEWER_STATUS,
                "packet_can_close_row": "false",
                "suggested_closeout_status_after_signoff": "closed_invalidation_only",
                "suggested_can_clear_invalidation_gate_after_signoff": "true",
                "affected_artifact_count": str(len(artifacts)),
                "missing_artifact_count": str(len(missing)),
                "affected_artifacts_json": _json(artifacts),
                "rerun_commands_json": _json(RERUN_COMMANDS_BY_ROW.get(row_id, ())),
                "audit_commands_json": _json(AUDIT_COMMANDS_BY_ROW.get(row_id, ())),
                "targeted_test_commands_json": _json(targeted_tests),
                "claim_boundary_review_commands_json": _json(
                    CLAIM_BOUNDARY_COMMANDS_BY_ROW.get(row_id, ())
                ),
                "lineage_status": (
                    "artifact_paths_present_pending_reviewer_signoff"
                    if not missing
                    else "missing_artifacts_pending_regeneration"
                ),
                "remaining_reviewer_action": (
                    "Review affected paths, hashes, rerun commands, audit commands, "
                    "targeted tests, and claim-boundary guard results before signing "
                    "the authoritative closeout row."
                ),
                "source_ledger": _display_path(source_ledger_path, root),
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    _validate_rows(rows)
    return rows


def write_upstream_lineage_review_packet(
    *,
    rows: Sequence[Mapping[str, str]] | None = None,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    manifest_path: str | Path = DEFAULT_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_DOC_PATH,
    action_queue_path: str | Path = DEFAULT_ACTION_QUEUE_PATH,
    source_ledger_path: str | Path = DEFAULT_LEDGER_PATH,
    project_root: str | Path = PROJECT_ROOT,
) -> dict[str, Any]:
    """Write upstream lineage review CSV, manifest, and Markdown."""

    root = Path(project_root)
    built_rows = list(rows) if rows is not None else build_upstream_lineage_review_rows(
        action_queue_path=action_queue_path,
        project_root=root,
        source_ledger_path=source_ledger_path,
    )
    _validate_rows(built_rows)

    output = Path(output_path)
    manifest_file = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(built_rows)

    summary = summarize_upstream_lineage_review_rows(
        built_rows,
        output_path=output,
        manifest_path=manifest_file,
        doc_path=doc,
        action_queue_path=action_queue_path,
    )
    manifest_file.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_upstream_lineage_review_markdown(built_rows, summary),
        encoding="utf-8",
    )
    return summary


def summarize_upstream_lineage_review_rows(
    rows: Sequence[Mapping[str, str]],
    *,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    manifest_path: str | Path = DEFAULT_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_DOC_PATH,
    action_queue_path: str | Path = DEFAULT_ACTION_QUEUE_PATH,
) -> dict[str, Any]:
    """Summarize review packet rows without creating closeout evidence."""

    _validate_rows(rows)
    missing_artifact_count = sum(int(row["missing_artifact_count"]) for row in rows)
    missing_artifact_row_count = sum(
        1 for row in rows if int(row["missing_artifact_count"]) > 0
    )
    signoff_counts = Counter(row["reviewer_signoff_status"] for row in rows)
    lineage_status_counts = Counter(row["lineage_status"] for row in rows)
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source_action_batch": SOURCE_ACTION_BATCH,
        "row_count": len(rows),
        "missing_artifact_count": missing_artifact_count,
        "missing_artifact_row_count": missing_artifact_row_count,
        "reviewer_signoff_status_counts": dict(sorted(signoff_counts.items())),
        "lineage_status_counts": dict(sorted(lineage_status_counts.items())),
        "packet_can_close_row_count": 0,
        "can_clear_invalidation_gate": False,
        "phase9_promotion_ready": False,
        "publication_ready": False,
        "final_study_ready": False,
        "formal_acceptance_evidence": False,
        "can_mark_complete": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "remaining_blockers": [
            "authoritative closeout CSV still requires row-level reviewer signoff",
            "this packet does not set can_clear_invalidation_gate",
            "Phase 9 promotion remains blocked until closeout rows are updated and audited",
        ],
        "inputs": {
            "action_queue": _display_path(action_queue_path, PROJECT_ROOT),
        },
        "outputs": {
            "csv": _display_path(output_path, PROJECT_ROOT),
            "manifest": _display_path(manifest_path, PROJECT_ROOT),
            "doc": _display_path(doc_path, PROJECT_ROOT),
        },
    }


def build_upstream_lineage_review_markdown(
    rows: Sequence[Mapping[str, str]],
    summary: Mapping[str, Any],
) -> str:
    """Return a concise Markdown reviewer packet."""

    lines = [
        "# Artifact Invalidation Upstream Lineage Review Packet",
        "",
        CLAIM_BOUNDARY,
        "",
        "## Summary",
        "",
        f"- Source action batch: `{summary.get('source_action_batch', '')}`",
        f"- Row count: {summary.get('row_count', 0)}",
        f"- Missing artifact rows: {summary.get('missing_artifact_row_count', 0)}",
        f"- Missing artifacts: {summary.get('missing_artifact_count', 0)}",
        f"- Reviewer signoff counts: `{json.dumps(summary.get('reviewer_signoff_status_counts', {}), sort_keys=True)}`",
        f"- Can clear invalidation gate: `{str(summary.get('can_clear_invalidation_gate', False)).lower()}`",
        "",
        "## Reviewer Rows",
        "",
        "| Row | Artifacts | Missing | Status | Reviewer Action |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {row_id} | {count} | {missing} | {status} | {action} |".format(
                row_id=_cell(row["invalidation_row_id"]),
                count=_cell(row["affected_artifact_count"]),
                missing=_cell(row["missing_artifact_count"]),
                status=_cell(row["lineage_status"]),
                action=_cell(row["remaining_reviewer_action"]),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Use this packet to inspect regenerated upstream artifacts and hashes.",
            "- Do not use this packet as reviewer signoff or closeout evidence by itself.",
            "- Update `data/validation/artifact_invalidation_closeout_template.csv` only after reviewer signoff.",
            "",
        ]
    )
    return "\n".join(lines)


def _artifact_records(
    paths: Iterable[str],
    *,
    project_root: Path,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path_text in paths:
        path = project_root / path_text
        exists = path.exists()
        records.append(
            {
                "path": path_text,
                "exists": exists,
                "sha256": _sha256(path) if exists and path.is_file() else "",
                "byte_count": path.stat().st_size if exists and path.is_file() else 0,
            }
        )
    return records


def _read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _display_path(path: str | Path, project_root: Path) -> str:
    filepath = Path(path)
    try:
        return filepath.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return filepath.as_posix()


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _validate_rows(rows: Sequence[Mapping[str, str]]) -> None:
    row_ids = [str(row.get("invalidation_row_id", "")) for row in rows]
    expected_ids = set(AFFECTED_ARTIFACTS_BY_ROW)
    if set(row_ids) != expected_ids:
        missing = sorted(expected_ids.difference(row_ids))
        extra = sorted(set(row_ids).difference(expected_ids))
        raise ValueError(f"unexpected upstream row ids: missing={missing}, extra={extra}")
    if len(row_ids) != len(set(row_ids)):
        raise ValueError("duplicate upstream lineage rows")
    for row in rows:
        for field in FIELDNAMES:
            if field not in row:
                raise ValueError(f"missing field {field!r} in {row.get('invalidation_row_id', '')}")
        if row["action_batch"] != SOURCE_ACTION_BATCH:
            raise ValueError(f"unexpected action batch {row['action_batch']!r}")
        if row["reviewer_signoff_status"] != REVIEWER_STATUS:
            raise ValueError("lineage packet must not create reviewer signoff")
        if row["packet_can_close_row"] != "false":
            raise ValueError("lineage packet must not close rows")


__all__ = [
    "AFFECTED_ARTIFACTS_BY_ROW",
    "CLAIM_BOUNDARY",
    "DEFAULT_DOC_PATH",
    "DEFAULT_MANIFEST_PATH",
    "DEFAULT_OUTPUT_PATH",
    "FIELDNAMES",
    "SOURCE_ACTION_BATCH",
    "build_upstream_lineage_review_markdown",
    "build_upstream_lineage_review_rows",
    "summarize_upstream_lineage_review_rows",
    "write_upstream_lineage_review_packet",
]
