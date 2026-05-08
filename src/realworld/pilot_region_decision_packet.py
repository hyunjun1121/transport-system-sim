"""Focused pilot-region decision worksheet.

The pilot privacy packet exposes row-level privacy and sensitivity review work.
This module turns that state into explicit pilot-region reviewer decisions
without creating ``data/manifests/pilot_acceptance.json`` or approving the
pilot case for final-study claims.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import yaml

from src.realworld.graph_scale_acceptance import DEFAULT_GRAPH_SCALE_ACCEPTANCE_PATH
from src.realworld.pilot_acceptance import DEFAULT_PILOT_ACCEPTANCE_PATH
from src.realworld.pilot_privacy_review_packet import (
    DEFAULT_PILOT_DATA_CARD_PATH,
    DEFAULT_PILOT_PRIVACY_REVIEW_MANIFEST_PATH,
    DEFAULT_PILOT_PRIVACY_REVIEW_PACKET_PATH,
    DEFAULT_PILOT_REGION_PATH,
)
from src.realworld.provenance_acceptance import DEFAULT_PROVENANCE_ACCEPTANCE_PATH


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PILOT_REGION_DECISION_PACKET_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "pilot_region_decision_packet.csv"
)
DEFAULT_PILOT_REGION_DECISION_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "pilot_region_decision_manifest.json"
)
DEFAULT_PILOT_REGION_DECISION_DOC_PATH = (
    PROJECT_ROOT / "docs" / "pilot_region_decision_packet.md"
)
PILOT_REGION_DECISION_SCOPE = (
    "Pilot-region decision packet only; not pilot acceptance, not privacy "
    "approval, not graph-scale acceptance, not calibrated real-world validation, "
    "and not operational routing evidence."
)
PILOT_REGION_DECISION_COLUMNS: tuple[str, ...] = (
    "decision_id",
    "decision_topic",
    "candidate_decision",
    "current_evidence",
    "decision_status",
    "blocking_reason",
    "required_reviewer_action",
    "followup_artifacts",
    "evidence_input_paths",
    "can_support_pilot_acceptance",
    "claim_boundary",
)


def build_pilot_region_decision_rows(
    *,
    region_path: str | Path = DEFAULT_PILOT_REGION_PATH,
    data_card_path: str | Path = DEFAULT_PILOT_DATA_CARD_PATH,
    privacy_manifest_path: str | Path = DEFAULT_PILOT_PRIVACY_REVIEW_MANIFEST_PATH,
    pilot_acceptance_path: str | Path = DEFAULT_PILOT_ACCEPTANCE_PATH,
    graph_scale_acceptance_path: str | Path = DEFAULT_GRAPH_SCALE_ACCEPTANCE_PATH,
    provenance_acceptance_path: str | Path = DEFAULT_PROVENANCE_ACCEPTANCE_PATH,
) -> list[dict[str, str]]:
    """Return reviewer rows for the pilot-region acceptance decision."""

    region = _read_yaml_mapping(region_path)
    privacy_manifest = _read_json_object(privacy_manifest_path)
    data_card_text = _read_text(data_card_path)
    pilot_acceptance = Path(pilot_acceptance_path)
    graph_acceptance = Path(graph_scale_acceptance_path)
    provenance_acceptance = Path(provenance_acceptance_path)
    region_id = str(region.get("region_id", "")).strip()
    evidence_paths = _evidence_paths(
        region_path=region_path,
        data_card_path=data_card_path,
        privacy_manifest_path=privacy_manifest_path,
    )

    return [
        _row(
            decision_id="pilot_case_scope_decision",
            decision_topic="Pilot case scope",
            candidate_decision=(
                "Retain the current Songpa public demonstration region only as "
                "a non-sensitive quasi-real pilot case"
            ),
            current_evidence=_region_scope_evidence(region),
            decision_status="needs_human_review_pilot_case_scope",
            blocking_reason="",
            required_reviewer_action=(
                "Decide whether the current public/synthetic case scope is "
                "acceptable for the intended manuscript and review boundary."
            ),
            followup_artifacts="data/manifests/pilot_acceptance.json",
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="privacy_review_completion_decision",
            decision_topic="Privacy review completion",
            candidate_decision=(
                "Mark privacy review complete only after all row-level privacy "
                "items are reviewed by a human reviewer"
            ),
            current_evidence=_privacy_evidence(privacy_manifest),
            decision_status="needs_human_review_privacy_completion",
            blocking_reason="",
            required_reviewer_action=(
                "Review each privacy packet row and record the final privacy "
                "decision in pilot_acceptance.json, not in this worksheet."
            ),
            followup_artifacts=(
                "data/manifests/pilot_privacy_review_packet.csv; "
                "data/manifests/pilot_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="graph_scale_dependency_decision",
            decision_topic="Graph-scale dependency",
            candidate_decision=(
                "Bind the pilot case to the graph-scale method selected by "
                "formal graph-scale review"
            ),
            current_evidence=(
                f"graph_scale_acceptance_path={_display_path(graph_acceptance)}; "
                f"graph_scale_acceptance_present={str(graph_acceptance.exists()).lower()}"
            ),
            decision_status=(
                "needs_human_review_existing_graph_scale_acceptance"
                if graph_acceptance.exists()
                else "blocked_missing_graph_scale_acceptance_record"
            ),
            blocking_reason=(
                ""
                if graph_acceptance.exists()
                else "data/manifests/graph_scale_acceptance.json is absent"
            ),
            required_reviewer_action=(
                "Record the graph_scale_decision in pilot_acceptance.json only "
                "after graph-scale review selects an accepted method."
            ),
            followup_artifacts=(
                "data/manifests/graph_scale_acceptance.json; "
                "data/manifests/pilot_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="cache_and_provenance_scope_decision",
            decision_topic="Cache and provenance dependency",
            candidate_decision=(
                "Use the cached OSM-derived pilot input only after source, "
                "license, cache, and attribution scope are reviewed"
            ),
            current_evidence=(
                f"cache_path={_clean(_mapping_value(region, 'metadata').get('cache_path'))}; "
                f"provenance_acceptance_path={_display_path(provenance_acceptance)}; "
                f"provenance_acceptance_present={str(provenance_acceptance.exists()).lower()}"
            ),
            decision_status=(
                "needs_human_review_existing_provenance_acceptance"
                if provenance_acceptance.exists()
                else "blocked_missing_provenance_acceptance_record"
            ),
            blocking_reason=(
                ""
                if provenance_acceptance.exists()
                else "data/manifests/provenance_acceptance.json is absent"
            ),
            required_reviewer_action=(
                "Confirm whether pilot acceptance is limited to case privacy "
                "or also requires reviewed source/cache provenance before final claims."
            ),
            followup_artifacts=(
                "data/cache/pilot_region_road_manifest.json; "
                "data/manifests/provenance_acceptance.json; "
                "data/manifests/pilot_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="not_operational_claim_boundary_decision",
            decision_topic="Not-operational claim boundary",
            candidate_decision=(
                "Keep all pilot-region claims bounded as non-operational and "
                "not calibrated until formal acceptance says otherwise"
            ),
            current_evidence=_data_card_evidence(data_card_text),
            decision_status="needs_human_review_claim_boundary",
            blocking_reason="",
            required_reviewer_action=(
                "Confirm the accepted claim boundary text and carry it into "
                "pilot_acceptance.json."
            ),
            followup_artifacts=(
                "docs/pilot_region_data_card.md; "
                "data/manifests/pilot_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="formal_pilot_acceptance_boundary",
            decision_topic="Formal pilot acceptance",
            candidate_decision=(
                "Record accepted region ID, reviewer, date, privacy completion, "
                "graph-scale decision, evidence paths, and claim boundary only "
                "in the formal pilot acceptance path"
            ),
            current_evidence=(
                f"acceptance_path={_display_path(pilot_acceptance)}; "
                f"acceptance_present={str(pilot_acceptance.exists()).lower()}; "
                f"region_id={region_id}"
            ),
            decision_status=(
                "needs_human_review_existing_pilot_acceptance"
                if pilot_acceptance.exists()
                else "blocked_missing_pilot_acceptance_record"
            ),
            blocking_reason=(
                ""
                if pilot_acceptance.exists()
                else "data/manifests/pilot_acceptance.json is absent"
            ),
            required_reviewer_action=(
                "Create or validate pilot_acceptance.json only after "
                "source-backed human review; do not copy this packet into the "
                "formal path."
            ),
            followup_artifacts="data/manifests/pilot_acceptance.json",
            evidence_input_paths=evidence_paths,
        ),
    ]


def write_pilot_region_decision_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_PILOT_REGION_DECISION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_PILOT_REGION_DECISION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_PILOT_REGION_DECISION_DOC_PATH,
    region_path: str | Path = DEFAULT_PILOT_REGION_PATH,
    data_card_path: str | Path = DEFAULT_PILOT_DATA_CARD_PATH,
    privacy_manifest_path: str | Path = DEFAULT_PILOT_PRIVACY_REVIEW_MANIFEST_PATH,
) -> dict[str, Any]:
    """Write pilot-region decision CSV, manifest, and Markdown."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PILOT_REGION_DECISION_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in PILOT_REGION_DECISION_COLUMNS
                }
            )

    summary = build_pilot_region_decision_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        region_path=region_path,
        data_card_path=data_card_path,
        privacy_manifest_path=privacy_manifest_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_pilot_region_decision_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_pilot_region_decision_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_PILOT_REGION_DECISION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_PILOT_REGION_DECISION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_PILOT_REGION_DECISION_DOC_PATH,
    region_path: str | Path = DEFAULT_PILOT_REGION_PATH,
    data_card_path: str | Path = DEFAULT_PILOT_DATA_CARD_PATH,
    privacy_manifest_path: str | Path = DEFAULT_PILOT_PRIVACY_REVIEW_MANIFEST_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for pilot-region decisions."""

    status_counts = _counts(row.get("decision_status", "") for row in rows)
    blocking_count = sum(
        1 for row in rows if str(row.get("decision_status", "")).startswith("blocked_")
    )
    human_review_count = sum(
        1
        for row in rows
        if str(row.get("decision_status", "")).startswith("needs_human_review_")
    )
    return {
        "schema_version": 1,
        "result_scope": PILOT_REGION_DECISION_SCOPE,
        "claim_boundary": (
            PILOT_REGION_DECISION_SCOPE
            + " It cannot create data/manifests/pilot_acceptance.json."
        ),
        "row_count": len(rows),
        "decision_ids": [str(row.get("decision_id", "")) for row in rows],
        "decision_status_counts": status_counts,
        "blocking_decision_count": blocking_count,
        "human_review_decision_count": human_review_count,
        "pilot_region_decision_recorded": False,
        "privacy_completion_decision_recorded": False,
        "pilot_acceptance_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "region_spec": _display_path(Path(region_path)),
            "data_card": _display_path(Path(data_card_path)),
            "pilot_privacy_review_manifest": _display_path(
                Path(privacy_manifest_path)
            ),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": [
            "decide whether the current public/synthetic Songpa demo is acceptable as the pilot case",
            "review all privacy packet rows before marking privacy_review_complete",
            "bind pilot acceptance to the accepted graph-scale method or keep the pilot blocked",
            "confirm source/cache provenance dependency before final pilot claims",
            "record final pilot decisions only in data/manifests/pilot_acceptance.json",
        ],
        "remaining_blockers": _remaining_blockers(rows),
    }


def build_pilot_region_decision_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return Markdown pilot-region decision worksheet."""

    lines = [
        "# Pilot Region Decision Packet",
        "",
        str(manifest.get("claim_boundary", PILOT_REGION_DECISION_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Pilot region decision recorded: `{str(manifest.get('pilot_region_decision_recorded', False)).lower()}`",
        f"- Privacy completion decision recorded: `{str(manifest.get('privacy_completion_decision_recorded', False)).lower()}`",
        f"- Decision rows: {manifest.get('row_count', 0)}",
        f"- Blocking decisions: {manifest.get('blocking_decision_count', 0)}",
        f"- Human-review decisions: {manifest.get('human_review_decision_count', 0)}",
        f"- Status counts: `{manifest.get('decision_status_counts', {})}`",
        "",
        "## Decision Rows",
        "",
        "| Decision | Status | Candidate | Required Action |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {decision} | {status} | {candidate} | {action} |".format(
                decision=_cell(row.get("decision_id", "")),
                status=_cell(row.get("decision_status", "")),
                candidate=_cell(row.get("candidate_decision", "")),
                action=_cell(row.get("required_reviewer_action", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This packet is a reviewer worksheet, not an acceptance record.",
            "- It does not approve privacy, select graph scale, accept provenance, or accept the pilot case.",
            "- Keep pilot-region claims blocked until `data/manifests/pilot_acceptance.json` is reviewed.",
            "",
        ]
    )
    return "\n".join(lines)


def _row(
    *,
    decision_id: str,
    decision_topic: str,
    candidate_decision: str,
    current_evidence: str,
    decision_status: str,
    blocking_reason: str,
    required_reviewer_action: str,
    followup_artifacts: str,
    evidence_input_paths: str,
) -> dict[str, str]:
    return {
        "decision_id": decision_id,
        "decision_topic": decision_topic,
        "candidate_decision": candidate_decision,
        "current_evidence": current_evidence,
        "decision_status": decision_status,
        "blocking_reason": blocking_reason,
        "required_reviewer_action": required_reviewer_action,
        "followup_artifacts": followup_artifacts,
        "evidence_input_paths": evidence_input_paths,
        "can_support_pilot_acceptance": "false",
        "claim_boundary": PILOT_REGION_DECISION_SCOPE,
    }


def _region_scope_evidence(region: Mapping[str, Any]) -> str:
    metadata = _mapping_value(region, "metadata")
    return (
        f"region_id={_clean(region.get('region_id'))}; "
        f"pilot_status={_clean(metadata.get('pilot_status'))}; "
        f"data_sensitivity={_clean(metadata.get('data_sensitivity'))}; "
        f"assembly_zones={len(_sequence(region.get('assembly_zones')))}; "
        f"destination_zones={len(_sequence(region.get('destination_zones')))}"
    )


def _privacy_evidence(manifest: Mapping[str, Any]) -> str:
    return (
        f"privacy_rows={_int(manifest.get('row_count'))}; "
        f"review_required_count={_int(manifest.get('review_required_count'))}; "
        f"closure_candidate_count={_int(manifest.get('pilot_acceptance_closure_candidate_count'))}; "
        f"publication_ready={str(manifest.get('publication_ready', False)).lower()}"
    )


def _data_card_evidence(text: str) -> str:
    lowered = text.lower()
    return (
        f"data_card_present={str(bool(text)).lower()}; "
        f"mentions_not_operational={str('not operational' in lowered).lower()}; "
        f"mentions_not_calibrated={str('not calibrated' in lowered).lower()}; "
        f"mentions_public_or_synthetic={str('public or synthetic' in lowered).lower()}"
    )


def _evidence_paths(
    *,
    region_path: str | Path,
    data_card_path: str | Path,
    privacy_manifest_path: str | Path,
) -> str:
    paths = [
        region_path,
        data_card_path,
        DEFAULT_PILOT_PRIVACY_REVIEW_PACKET_PATH,
        privacy_manifest_path,
    ]
    return "; ".join(_display_path(Path(path)) for path in paths)


def _remaining_blockers(rows: Sequence[Mapping[str, str]]) -> list[str]:
    blockers: list[str] = []
    for row in rows:
        status = str(row.get("decision_status", ""))
        reason = str(row.get("blocking_reason", "")).strip()
        if status.startswith("blocked_") and reason:
            blockers.append(reason)
    return blockers


def _read_yaml_mapping(path: str | Path) -> dict[str, Any]:
    yaml_path = Path(path)
    if not yaml_path.exists():
        return {}
    with yaml_path.open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    return dict(value) if isinstance(value, Mapping) else {}


def _read_json_object(path: str | Path) -> dict[str, Any]:
    json_path = Path(path)
    if not json_path.exists():
        return {}
    with json_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    return value if isinstance(value, dict) else {}


def _read_text(path: str | Path) -> str:
    text_path = Path(path)
    if not text_path.exists():
        return ""
    return text_path.read_text(encoding="utf-8")


def _mapping_value(mapping: Mapping[str, Any], key: str) -> dict[str, Any]:
    value = mapping.get(key, {})
    return dict(value) if isinstance(value, Mapping) else {}


def _sequence(value: object) -> tuple[object, ...]:
    if isinstance(value, Sequence) and not isinstance(value, str):
        return tuple(value)
    return ()


def _counts(values: Iterable[Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value).strip() or "blank"
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _int(value: object) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return 0


def _clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


__all__ = [
    "DEFAULT_PILOT_REGION_DECISION_DOC_PATH",
    "DEFAULT_PILOT_REGION_DECISION_MANIFEST_PATH",
    "DEFAULT_PILOT_REGION_DECISION_PACKET_PATH",
    "PILOT_REGION_DECISION_COLUMNS",
    "PILOT_REGION_DECISION_SCOPE",
    "build_pilot_region_decision_manifest",
    "build_pilot_region_decision_markdown",
    "build_pilot_region_decision_rows",
    "write_pilot_region_decision_packet",
]
