"""Experiment strategy-readiness packet generation.

The experiment package review packet summarizes full-pilot outputs and run
metadata. This module turns those rows into explicit pre-review readiness
states without accepting the experiment package or treating scaffold outputs as
calibrated real-world evidence.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.realworld.experiment_acceptance import DEFAULT_EXPERIMENT_ACCEPTANCE_PATH
from src.realworld.experiment_package_review_packet import (
    DEFAULT_EXPERIMENT_PACKAGE_REVIEW_PACKET_PATH,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXPERIMENT_STRATEGY_READINESS_PACKET_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "experiment_strategy_readiness_packet.csv"
)
DEFAULT_EXPERIMENT_STRATEGY_READINESS_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "experiment_strategy_readiness_manifest.json"
)
DEFAULT_EXPERIMENT_STRATEGY_READINESS_DOC_PATH = (
    PROJECT_ROOT / "docs" / "experiment_strategy_readiness_packet.md"
)
EXPERIMENT_STRATEGY_READINESS_SCOPE = (
    "Experiment strategy-readiness packet only; not experiment acceptance, "
    "not calibrated real-world validation, not operational routing evidence, "
    "and not publication-readiness approval."
)
EXPERIMENT_STRATEGY_READINESS_COLUMNS: tuple[str, ...] = (
    "category_id",
    "artifact_path",
    "artifact_present",
    "row_count",
    "expected_row_count",
    "review_status",
    "readiness_status",
    "blocking_reason",
    "required_reviewer_action",
    "publication_use_status",
    "evidence_detail",
    "can_support_experiment_gate",
    "claim_boundary",
)


def build_experiment_strategy_readiness_rows(
    *,
    review_rows: Sequence[Mapping[str, str]] | None = None,
    review_packet_path: str | Path = DEFAULT_EXPERIMENT_PACKAGE_REVIEW_PACKET_PATH,
    acceptance_path: str | Path = DEFAULT_EXPERIMENT_ACCEPTANCE_PATH,
) -> list[dict[str, str]]:
    """Return experiment strategy-readiness rows for current review rows."""

    rows = (
        list(review_rows)
        if review_rows is not None
        else _load_review_rows(review_packet_path)
    )
    readiness_rows = [_readiness_row(row) for row in rows]
    if "formal_experiment_acceptance_requirement" not in {
        row.get("category_id", "") for row in rows
    }:
        readiness_rows.append(_acceptance_requirement_row(Path(acceptance_path)))
    return readiness_rows


def write_experiment_strategy_readiness_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_EXPERIMENT_STRATEGY_READINESS_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_EXPERIMENT_STRATEGY_READINESS_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_EXPERIMENT_STRATEGY_READINESS_DOC_PATH,
    review_packet_path: str | Path = DEFAULT_EXPERIMENT_PACKAGE_REVIEW_PACKET_PATH,
) -> dict[str, Any]:
    """Write experiment strategy-readiness CSV, manifest, and Markdown."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=EXPERIMENT_STRATEGY_READINESS_COLUMNS,
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in EXPERIMENT_STRATEGY_READINESS_COLUMNS
                }
            )

    summary = build_experiment_strategy_readiness_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        review_packet_path=review_packet_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_experiment_strategy_readiness_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_experiment_strategy_readiness_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_EXPERIMENT_STRATEGY_READINESS_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_EXPERIMENT_STRATEGY_READINESS_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_EXPERIMENT_STRATEGY_READINESS_DOC_PATH,
    review_packet_path: str | Path = DEFAULT_EXPERIMENT_PACKAGE_REVIEW_PACKET_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for experiment readiness rows."""

    status_counts = _counts(row.get("readiness_status", "") for row in rows)
    blocking_count = sum(
        1 for row in rows if str(row.get("readiness_status", "")).startswith("blocked_")
    )
    human_review_count = sum(
        1
        for row in rows
        if str(row.get("readiness_status", "")).startswith("needs_human_review_")
    )
    return {
        "schema_version": 1,
        "claim_boundary": (
            EXPERIMENT_STRATEGY_READINESS_SCOPE
            + " This packet cannot close data/manifests/experiment_acceptance.json."
        ),
        "result_scope": EXPERIMENT_STRATEGY_READINESS_SCOPE,
        "row_count": len(rows),
        "readiness_status_counts": status_counts,
        "blocking_request_count": blocking_count,
        "human_review_request_count": human_review_count,
        "experiment_gate_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "experiment_package_review_packet": _display_path(Path(review_packet_path)),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": [
            "review scaffold result scope before manuscript or report use",
            "confirm full result and summary row counts against the manifest",
            "close graph-scale and input-evidence dependencies before accepting full outputs",
            "review scenario-policy-seed design, CRN pairing, and checksums",
            "record the final experiment decision only in data/manifests/experiment_acceptance.json",
        ],
        "remaining_blockers": _remaining_blockers(rows),
    }


def build_experiment_strategy_readiness_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return a human-readable experiment strategy-readiness packet."""

    lines = [
        "# Experiment Strategy Readiness Packet",
        "",
        str(manifest.get("claim_boundary", EXPERIMENT_STRATEGY_READINESS_SCOPE)),
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
        "| Category | Status | Rows | Required Action |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {category} | {status} | {rows} / {expected} | {action} |".format(
                category=_cell(row.get("category_id", "")),
                status=_cell(row.get("readiness_status", "")),
                rows=_cell(row.get("row_count", "")),
                expected=_cell(row.get("expected_row_count", "")),
                action=_cell(row.get("required_reviewer_action", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Required Reviewer Actions",
            "",
            "- Keep full-pilot outputs in scaffold scope until graph-scale, input-evidence, validation, and experiment acceptance records exist.",
            "- Decide whether the current full-profile run is accepted, regenerated on another graph method, or retained only as review evidence.",
            "- Review row counts, checksums, scenario-policy-seed design, and CRN pairing before formal experiment acceptance.",
            "- Do not create formal acceptance artifacts from this readiness packet alone.",
            "",
        ]
    )
    return "\n".join(lines)


def _readiness_row(row: Mapping[str, str]) -> dict[str, str]:
    status, reason, action = _classify(row)
    return {
        "category_id": str(row.get("category_id", "")),
        "artifact_path": str(row.get("artifact_path", "")),
        "artifact_present": str(row.get("artifact_present", "")).lower(),
        "row_count": str(row.get("row_count", "")),
        "expected_row_count": str(row.get("expected_row_count", "")),
        "review_status": str(row.get("review_status", "")),
        "readiness_status": status,
        "blocking_reason": reason,
        "required_reviewer_action": action,
        "publication_use_status": str(row.get("publication_use_status", "")),
        "evidence_detail": str(row.get("evidence_detail", "")),
        "can_support_experiment_gate": "false",
        "claim_boundary": EXPERIMENT_STRATEGY_READINESS_SCOPE,
    }


def _acceptance_requirement_row(acceptance_path: Path) -> dict[str, str]:
    present = acceptance_path.exists()
    return {
        "category_id": "formal_experiment_acceptance_requirement",
        "artifact_path": _display_path(acceptance_path),
        "artifact_present": "true" if present else "false",
        "row_count": "1" if present else "0",
        "expected_row_count": "1",
        "review_status": (
            "review_required_formal_acceptance_present"
            if present
            else "blocked_formal_acceptance_absent"
        ),
        "readiness_status": (
            "needs_human_review_experiment_acceptance_record"
            if present
            else "blocked_missing_experiment_acceptance_record"
        ),
        "blocking_reason": (
            ""
            if present
            else "data/manifests/experiment_acceptance.json is absent"
        ),
        "required_reviewer_action": (
            "validate the existing experiment acceptance record"
            if present
            else "record the accepted run profile only after graph scope, input validation, design, CRN, counts, and claim-boundary review"
        ),
        "publication_use_status": "blocked_until_experiment_acceptance",
        "evidence_detail": "formal experiment acceptance record controls gate closure",
        "can_support_experiment_gate": "false",
        "claim_boundary": EXPERIMENT_STRATEGY_READINESS_SCOPE,
    }


def _classify(row: Mapping[str, str]) -> tuple[str, str, str]:
    category_id = str(row.get("category_id", ""))
    review_status = str(row.get("review_status", ""))

    if category_id == "manifest_scope":
        if "scaffold" in review_status or "not_calibrated" in review_status:
            return (
                "blocked_scaffold_or_not_calibrated_experiment_scope",
                "current full-pilot result scope is scaffold or not calibrated",
                "keep experiment claims bounded until formal acceptance chooses final result scope",
            )
        return (
            "needs_human_review_experiment_scope",
            "",
            "review result scope and claim boundary before acceptance",
        )
    if category_id in {"results_row_count", "summary_row_count"}:
        if "mismatch" in review_status or "missing" in review_status:
            return (
                "blocked_experiment_row_count_or_artifact",
                f"{category_id} is missing or has a count mismatch",
                "regenerate or repair the full-pilot output before acceptance",
            )
        return (
            "needs_human_review_experiment_row_counts",
            "",
            "confirm row counts are generated from the selected accepted run profile",
        )
    if category_id == "scenario_policy_seed_design":
        if "mismatch" in review_status:
            return (
                "blocked_scenario_policy_seed_design_mismatch",
                "scenario-policy-seed design count does not match result rows",
                "repair the design manifest or regenerate outputs before acceptance",
            )
        return (
            "needs_human_review_scenario_policy_seed_design",
            "",
            "review scenario, policy, seed, and exclusion design before acceptance",
        )
    if category_id == "graph_scope_dependency":
        return (
            "blocked_graph_scale_dependency",
            "full-pilot outputs depend on a graph method that is not accepted",
            "close graph-scale acceptance or regenerate outputs on the accepted graph method",
        )
    if category_id == "input_evidence_dependency":
        return (
            "blocked_input_evidence_dependency",
            "upstream input, road override, parameter, validation, or provenance gates are not accepted",
            "close upstream input-evidence gates before accepting full experiment outputs",
        )
    if category_id == "common_random_numbers":
        if "not_declared" in review_status:
            return (
                "blocked_common_random_numbers_not_declared",
                "common-random-number pairing is not declared",
                "declare or remove paired-claim assumptions before acceptance",
            )
        return (
            "needs_human_review_common_random_numbers",
            "",
            "review seed pairing and scenario runner RNG splitting before paired claims",
        )
    if category_id == "artifact_checksums":
        if "missing" in review_status:
            return (
                "blocked_missing_experiment_checksums",
                "manifest, results, or summary checksum evidence is missing",
                "regenerate checksum evidence before acceptance",
            )
        return (
            "needs_human_review_experiment_checksums",
            "",
            "record checksums or regenerated equivalents in formal experiment acceptance",
        )
    if category_id == "formal_experiment_acceptance_requirement":
        if "absent" in review_status:
            return (
                "blocked_missing_experiment_acceptance_record",
                "data/manifests/experiment_acceptance.json is absent",
                "create a formal acceptance record only after reviewer decision",
            )
        return (
            "needs_human_review_experiment_acceptance_record",
            "",
            "validate the existing experiment acceptance record",
        )
    return (
        "blocked_unclassified_experiment_category",
        f"unrecognized category_id {category_id!r}",
        "classify this experiment category before strategy review",
    )


def _remaining_blockers(rows: Sequence[Mapping[str, str]]) -> list[str]:
    blockers: list[str] = []
    for row in rows:
        status = str(row.get("readiness_status", ""))
        reason = str(row.get("blocking_reason", "")).strip()
        if status.startswith("blocked_") and reason:
            blockers.append(reason)
    return blockers


def _load_review_rows(path: str | Path) -> list[dict[str, str]]:
    packet = Path(path)
    if not packet.exists():
        return []
    with packet.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _counts(values: Sequence[str] | Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


__all__ = [
    "DEFAULT_EXPERIMENT_STRATEGY_READINESS_DOC_PATH",
    "DEFAULT_EXPERIMENT_STRATEGY_READINESS_MANIFEST_PATH",
    "DEFAULT_EXPERIMENT_STRATEGY_READINESS_PACKET_PATH",
    "EXPERIMENT_STRATEGY_READINESS_COLUMNS",
    "EXPERIMENT_STRATEGY_READINESS_SCOPE",
    "build_experiment_strategy_readiness_manifest",
    "build_experiment_strategy_readiness_markdown",
    "build_experiment_strategy_readiness_rows",
    "write_experiment_strategy_readiness_packet",
]
