"""Validation strategy-readiness packet generation.

The validation review packet summarizes internal checks, fallback benchmarks,
optional OSRM snapshots, accessibility diagnostics, route-level road evidence,
summary scope, and the missing validation acceptance record. This module turns
those rows into concrete pre-review readiness statuses without accepting a
benchmark strategy or treating plausibility checks as ground truth.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.realworld.validation_review_packet import (
    DEFAULT_VALIDATION_REVIEW_PACKET_PATH,
    VALIDATION_REVIEW_PACKET_SCOPE,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_VALIDATION_STRATEGY_READINESS_PACKET_PATH = (
    PROJECT_ROOT / "data" / "validation" / "validation_strategy_readiness_packet.csv"
)
DEFAULT_VALIDATION_STRATEGY_READINESS_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "validation_strategy_readiness_manifest.json"
)
DEFAULT_VALIDATION_STRATEGY_READINESS_DOC_PATH = (
    PROJECT_ROOT / "docs" / "validation_strategy_readiness_packet.md"
)
VALIDATION_STRATEGY_READINESS_SCOPE = (
    "Validation strategy-readiness packet only; not validation acceptance, "
    "not benchmark ground truth, not calibrated traffic validation, not "
    "operational routing evidence, and not publication-readiness approval."
)
VALIDATION_STRATEGY_READINESS_COLUMNS: tuple[str, ...] = (
    "category_id",
    "evidence_category",
    "artifact_path",
    "artifact_present",
    "row_count",
    "review_status",
    "readiness_status",
    "blocking_reason",
    "required_reviewer_action",
    "status_counts",
    "coverage_counts",
    "publication_use_status",
    "can_support_validation_gate",
    "claim_boundary",
)


def build_validation_strategy_readiness_rows(
    *,
    review_rows: Sequence[Mapping[str, str]] | None = None,
    review_packet_path: str | Path = DEFAULT_VALIDATION_REVIEW_PACKET_PATH,
) -> list[dict[str, str]]:
    """Return strategy-readiness rows for validation review categories."""

    rows = (
        list(review_rows)
        if review_rows is not None
        else _load_review_rows(review_packet_path)
    )
    return [_readiness_row(row) for row in rows]


def write_validation_strategy_readiness_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_VALIDATION_STRATEGY_READINESS_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_VALIDATION_STRATEGY_READINESS_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_VALIDATION_STRATEGY_READINESS_DOC_PATH,
    review_packet_path: str | Path = DEFAULT_VALIDATION_REVIEW_PACKET_PATH,
) -> dict[str, Any]:
    """Write validation strategy-readiness CSV, manifest, and Markdown."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=VALIDATION_STRATEGY_READINESS_COLUMNS,
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in VALIDATION_STRATEGY_READINESS_COLUMNS
                }
            )

    summary = build_validation_strategy_readiness_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        review_packet_path=review_packet_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_validation_strategy_readiness_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_validation_strategy_readiness_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_VALIDATION_STRATEGY_READINESS_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_VALIDATION_STRATEGY_READINESS_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_VALIDATION_STRATEGY_READINESS_DOC_PATH,
    review_packet_path: str | Path = DEFAULT_VALIDATION_REVIEW_PACKET_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for validation readiness rows."""

    status_counts = _counts(row.get("readiness_status", "") for row in rows)
    blocking_count = sum(
        1 for row in rows if str(row.get("readiness_status", "")).startswith("blocked_")
    )
    human_review_count = sum(
        1
        for row in rows
        if str(row.get("readiness_status", "")).startswith("needs_human_review_")
    )
    raw_payload_missing = any(
        row.get("category_id") == "optional_osrm_route_benchmarks"
        and _parse_counts(str(row.get("coverage_counts", ""))).get(
            "snapshot_manifest_raw_response_files", 0
        )
        == 0
        for row in rows
    )
    osrm_unpinned_blocked = any(
        row.get("readiness_status") == "blocked_unpinned_external_route_snapshot"
        for row in rows
    )
    validation_acceptance_missing = any(
        row.get("readiness_status") == "blocked_missing_validation_acceptance_record"
        for row in rows
    )
    weak_route_exposure = any(
        row.get("readiness_status") == "blocked_weak_route_road_evidence_exposure"
        for row in rows
    )
    review_items = [
        "review internal warning rows and fallback benchmark warning rows",
        "review accessibility-loss and route road-evidence exposure as diagnostics only",
        "choose the final benchmark strategy only in data/manifests/validation_acceptance.json",
    ]
    if osrm_unpinned_blocked:
        review_items.insert(
            1,
            "pin or replace unpinned external route-engine snapshots before final benchmark use",
        )
    else:
        review_items.insert(
            1,
            "review cached external route-engine snapshots before final benchmark use",
        )
    remaining_blockers = []
    if validation_acceptance_missing:
        remaining_blockers.append("validation_acceptance.json is absent")
    if osrm_unpinned_blocked:
        remaining_blockers.append(
            "optional OSRM rows remain live/unpinned unless reviewer accepts or replaces the snapshot"
        )
    if raw_payload_missing:
        review_items.insert(
            2,
            "retain raw external-route payloads before treating live OSRM rows as cached evidence",
        )
        remaining_blockers.insert(
            2,
            "retained raw OSRM response payloads are absent from the current snapshot manifest",
        )
    if weak_route_exposure:
        remaining_blockers.append(
            "route-level road evidence exposure remains weak until road evidence gates close"
        )
    return {
        "schema_version": 1,
        "claim_boundary": (
            VALIDATION_STRATEGY_READINESS_SCOPE
            + " This packet cannot close data/manifests/validation_acceptance.json."
        ),
        "result_scope": VALIDATION_STRATEGY_READINESS_SCOPE,
        "row_count": len(rows),
        "readiness_status_counts": status_counts,
        "blocking_request_count": blocking_count,
        "human_review_request_count": human_review_count,
        "validation_gate_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "validation_review_packet": _display_path(Path(review_packet_path)),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": review_items,
        "remaining_blockers": remaining_blockers,
    }


def build_validation_strategy_readiness_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return a human-readable validation strategy-readiness packet."""

    lines = [
        "# Validation Strategy Readiness Packet",
        "",
        str(manifest.get("claim_boundary", VALIDATION_STRATEGY_READINESS_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Review rows: {manifest.get('row_count', 0)}",
        f"- Blocking requests: {manifest.get('blocking_request_count', 0)}",
        f"- Human-review requests: {manifest.get('human_review_request_count', 0)}",
        f"- Status counts: `{manifest.get('readiness_status_counts', {})}`",
        "",
        "## Readiness Rows",
        "",
        "| Category | Status | Artifact | Required Action |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        artifact = "present" if _is_true(row.get("artifact_present", "")) else "absent"
        lines.append(
            "| {category} | {status} | {artifact} | {action} |".format(
                category=_cell(row.get("category_id", "")),
                status=_cell(row.get("readiness_status", "")),
                artifact=artifact,
                action=_cell(row.get("required_reviewer_action", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Required Reviewer Actions",
            "",
            "- Decide whether fallback and optional external benchmarks are retained, replaced, or excluded.",
            "- Keep validation claims at plausibility and decision-support scope until formal acceptance exists.",
            "- Do not treat OSRM, fallback routes, or internal checks as ground truth.",
            "- Do not create formal acceptance artifacts from this readiness packet alone.",
            "",
        ]
    )
    return "\n".join(lines)


def _readiness_row(row: Mapping[str, str]) -> dict[str, str]:
    category_id = str(row.get("category_id", ""))
    status, reason, action = _classify(row)
    return {
        "category_id": category_id,
        "evidence_category": str(row.get("evidence_category", "")),
        "artifact_path": str(row.get("artifact_path", "")),
        "artifact_present": str(row.get("artifact_present", "")).lower(),
        "row_count": str(row.get("row_count", "")),
        "review_status": str(row.get("review_status", "")),
        "readiness_status": status,
        "blocking_reason": reason,
        "required_reviewer_action": action,
        "status_counts": str(row.get("status_counts", "")),
        "coverage_counts": str(row.get("coverage_counts", "")),
        "publication_use_status": str(row.get("publication_use_status", "")),
        "can_support_validation_gate": "false",
        "claim_boundary": VALIDATION_STRATEGY_READINESS_SCOPE,
    }


def _classify(row: Mapping[str, str]) -> tuple[str, str, str]:
    category_id = str(row.get("category_id", ""))
    artifact_present = _is_true(str(row.get("artifact_present", "")))
    review_status = str(row.get("review_status", ""))
    counts = _parse_counts(str(row.get("status_counts", "")))
    coverage = _parse_counts(str(row.get("coverage_counts", "")))
    if category_id == "benchmark_strategy_decision_requirement":
        return (
            "blocked_missing_validation_acceptance_record",
            "data/manifests/validation_acceptance.json is absent",
            "record final benchmark strategy only after reviewer decision",
        )
    if not artifact_present:
        return (
            "blocked_missing_validation_artifact",
            f"{category_id} artifact is absent",
            "generate or supply the validation artifact before strategy review",
        )
    if category_id == "internal_route_plausibility":
        if counts.get("fail", 0) > 0:
            return (
                "blocked_internal_plausibility_failures",
                "internal route plausibility has failure rows",
                "resolve or explicitly accept internal route-plausibility failures",
            )
        if counts.get("warn", 0) > 0:
            return (
                "needs_human_review_internal_plausibility_warnings",
                "",
                "review internal route-plausibility warning rows against final graph scope",
            )
        return (
            "needs_human_review_internal_plausibility_pass_rows",
            "",
            "review pass-only internal checks as sanity evidence, not ground truth",
        )
    if category_id == "fallback_route_benchmarks":
        if counts.get("fail", 0) > 0:
            return (
                "blocked_fallback_benchmark_failures",
                "fallback route benchmarks have failure rows",
                "replace fallback benchmark rows or justify failures before acceptance",
            )
        if counts.get("warn", 0) > 0:
            return (
                "needs_human_review_fallback_benchmark_warnings",
                "",
                "decide whether fallback benchmarks remain placeholders or bounded checks",
            )
        return (
            "needs_human_review_fallback_benchmark_scope",
            "",
            "review fallback benchmark scope before final validation claims",
        )
    if category_id == "optional_osrm_route_benchmarks":
        raw_response_file_count = coverage.get("snapshot_manifest_raw_response_files", 0)
        if coverage.get("snapshot_manifest_unpinned_rows", 0) > 0:
            if raw_response_file_count > 0:
                action = (
                    "pin/cache or replace OSRM snapshot, and review source/provenance before use"
                )
            else:
                action = (
                    "retain raw payloads, pin/cache or replace OSRM snapshot, "
                    "and review source/provenance before use"
                )
            return (
                "blocked_unpinned_external_route_snapshot",
                "optional OSRM snapshot has unpinned live rows",
                action,
            )
        if raw_response_file_count == 0:
            return (
                "blocked_missing_external_route_raw_payloads",
                "optional OSRM snapshot has no retained raw response payloads",
                "retain raw payloads or document why the external snapshot is excluded from acceptance",
            )
        return (
            "needs_human_review_external_route_snapshot",
            "",
            "review optional external route snapshot as plausibility evidence only",
        )
    if category_id == "accessibility_loss_coverage":
        if counts.get("disconnected", 0) > 0:
            return (
                "needs_human_review_accessibility_disconnections",
                "",
                "review disconnected accessibility cases as fragility diagnostics, not observed outages",
            )
        return (
            "needs_human_review_accessibility_scope",
            "",
            "review accessibility-loss coverage against final disruption design",
        )
    if category_id == "route_road_evidence_exposure":
        if coverage.get("weak_for_final_claim_true", 0) > 0:
            return (
                "blocked_weak_route_road_evidence_exposure",
                "route-level road evidence exposure contains weak final-claim rows",
                "close or bound road evidence before validation claims use route exposure",
            )
        return (
            "needs_human_review_route_road_evidence_exposure",
            "",
            "review route-level road evidence exposure against accepted road inputs",
        )
    if category_id == "validation_summary_scope":
        if "scaffold" in review_status or coverage.get("scaffold_or_sanity_scope", 0):
            return (
                "needs_human_review_validation_summary_scope",
                "",
                "keep validation summary in scaffold scope until acceptance chooses strategy",
            )
        return (
            "needs_human_review_validation_summary_claims",
            "",
            "review validation summary wording against accepted benchmark strategy",
        )
    return (
        "blocked_unclassified_validation_category",
        f"unrecognized category_id {category_id!r}",
        "classify this validation category before strategy review",
    )


def _load_review_rows(path: str | Path) -> list[dict[str, str]]:
    packet = Path(path)
    if not packet.exists():
        return []
    with packet.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _parse_counts(value: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for part in str(value or "").split(";"):
        if "=" not in part:
            continue
        key, raw = part.split("=", 1)
        try:
            counts[key.strip()] = int(raw.strip())
        except ValueError:
            text = raw.strip().lower()
            counts[key.strip()] = 1 if text == "true" else 0
    return counts


def _counts(values: Sequence[str] | Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _is_true(value: str) -> bool:
    return str(value).strip().lower() == "true"


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


__all__ = [
    "DEFAULT_VALIDATION_STRATEGY_READINESS_DOC_PATH",
    "DEFAULT_VALIDATION_STRATEGY_READINESS_MANIFEST_PATH",
    "DEFAULT_VALIDATION_STRATEGY_READINESS_PACKET_PATH",
    "VALIDATION_STRATEGY_READINESS_COLUMNS",
    "VALIDATION_STRATEGY_READINESS_SCOPE",
    "build_validation_strategy_readiness_manifest",
    "build_validation_strategy_readiness_markdown",
    "build_validation_strategy_readiness_rows",
    "write_validation_strategy_readiness_packet",
]
