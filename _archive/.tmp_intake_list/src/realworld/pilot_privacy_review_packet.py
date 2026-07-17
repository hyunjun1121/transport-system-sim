"""Pilot-region privacy review-packet generation.

The pilot-region gate requires a reviewer decision, not just a YAML file and
data card. This module converts the region spec and data card into concrete
privacy/sensitivity review rows. It does not create
``data/manifests/pilot_acceptance.json`` and does not accept the pilot case.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PILOT_REGION_PATH = PROJECT_ROOT / "data" / "regions" / "pilot_region.yaml"
DEFAULT_PILOT_DATA_CARD_PATH = PROJECT_ROOT / "docs" / "pilot_region_data_card.md"
DEFAULT_PILOT_PRIVACY_REVIEW_PACKET_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "pilot_privacy_review_packet.csv"
)
DEFAULT_PILOT_PRIVACY_REVIEW_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "pilot_privacy_review_manifest.json"
)
DEFAULT_PILOT_PRIVACY_REVIEW_DOC_PATH = (
    PROJECT_ROOT / "docs" / "pilot_privacy_review_packet.md"
)
PILOT_PRIVACY_REVIEW_SCOPE = (
    "Pilot privacy review packet only; not pilot acceptance, not privacy "
    "approval, not calibrated real-world validation, and not operational "
    "routing approval."
)
PILOT_PRIVACY_REVIEW_COLUMNS: tuple[str, ...] = (
    "review_item_id",
    "region_id",
    "item_type",
    "item_name",
    "coordinate_class",
    "sensitivity_label",
    "exact_coordinate_public",
    "synthetic_or_aggregated",
    "privacy_risk_level",
    "operational_misuse_risk",
    "required_reviewer_decision",
    "target_acceptance_artifact",
    "can_support_pilot_acceptance",
    "publication_use_status",
    "claim_boundary",
    "notes",
)


def build_pilot_privacy_review_rows(
    *,
    region_path: str | Path = DEFAULT_PILOT_REGION_PATH,
    data_card_path: str | Path = DEFAULT_PILOT_DATA_CARD_PATH,
) -> list[dict[str, str]]:
    """Return privacy-review rows for the current pilot region package."""

    region_file = Path(region_path)
    with region_file.open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, Mapping):
        raise ValueError(f"{region_file} must contain a YAML mapping")
    region_id = _clean(value.get("region_id"))
    if not region_id:
        raise ValueError(f"{region_file} region_id must be non-empty")

    rows: list[dict[str, str]] = [_boundary_row(region_id, value)]
    for zone in _sequence(value.get("assembly_zones")):
        rows.append(_zone_row(region_id, "assembly_zone", zone))
    for zone in _sequence(value.get("destination_zones")):
        rows.append(_zone_row(region_id, "destination_zone", zone))
    rail = value.get("rail", {})
    if isinstance(rail, Mapping):
        access = rail.get("access")
        egress = rail.get("egress")
        if isinstance(access, Mapping):
            rows.append(_zone_row(region_id, "rail_access_point", access))
        if isinstance(egress, Mapping):
            rows.append(_zone_row(region_id, "rail_egress_point", egress))
    rows.append(_coordinate_policy_row(region_id, value))
    rows.append(_data_card_row(region_id, data_card_path))
    return rows


def write_pilot_privacy_review_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_PILOT_PRIVACY_REVIEW_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_PILOT_PRIVACY_REVIEW_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_PILOT_PRIVACY_REVIEW_DOC_PATH,
    region_path: str | Path = DEFAULT_PILOT_REGION_PATH,
    data_card_path: str | Path = DEFAULT_PILOT_DATA_CARD_PATH,
) -> dict[str, Any]:
    """Write CSV, JSON, and Markdown privacy review artifacts."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PILOT_PRIVACY_REVIEW_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: str(row.get(column, "")) for column in PILOT_PRIVACY_REVIEW_COLUMNS})

    summary = build_pilot_privacy_review_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        region_path=region_path,
        data_card_path=data_card_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_pilot_privacy_review_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_pilot_privacy_review_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_PILOT_PRIVACY_REVIEW_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_PILOT_PRIVACY_REVIEW_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_PILOT_PRIVACY_REVIEW_DOC_PATH,
    region_path: str | Path = DEFAULT_PILOT_REGION_PATH,
    data_card_path: str | Path = DEFAULT_PILOT_DATA_CARD_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for the pilot privacy review packet."""

    risk_counts = _counts(row.get("privacy_risk_level", "") for row in rows)
    misuse_counts = _counts(row.get("operational_misuse_risk", "") for row in rows)
    coordinate_class_counts = _counts(row.get("coordinate_class", "") for row in rows)
    review_required_count = sum(
        1 for row in rows if row.get("required_reviewer_decision", "")
    )
    closure_candidate_count = sum(
        1 for row in rows if _is_true(row.get("can_support_pilot_acceptance", "false"))
    )
    return {
        "schema_version": 1,
        "claim_boundary": (
            PILOT_PRIVACY_REVIEW_SCOPE
            + " A reviewer must still create data/manifests/pilot_acceptance.json "
            "before the pilot-region gate can close."
        ),
        "result_scope": PILOT_PRIVACY_REVIEW_SCOPE,
        "row_count": len(rows),
        "coordinate_class_counts": coordinate_class_counts,
        "privacy_risk_counts": risk_counts,
        "operational_misuse_risk_counts": misuse_counts,
        "review_required_count": review_required_count,
        "pilot_acceptance_closure_candidate_count": closure_candidate_count,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "region_spec": _display_path(Path(region_path)),
            "data_card": _display_path(Path(data_card_path)),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": [
            "confirm that public points do not imply operational assembly or route instructions",
            "confirm that synthetic destination abstraction is sufficient for the intended publication scope",
            "confirm that the bbox and station points are acceptable public geography for a demo case",
            "confirm that the data card keeps all claims non-operational and non-sensitive",
            "create data/manifests/pilot_acceptance.json only after privacy and case-scope review",
        ],
        "remaining_blockers": [
            "formal pilot acceptance record is absent",
            "privacy packet rows are review aids and do not approve the pilot case",
            "graph-scale and provenance gates must still close before final-study claims",
        ],
    }


def build_pilot_privacy_review_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return a human-readable pilot privacy review packet."""

    lines = [
        "# Pilot Privacy Review Packet",
        "",
        str(manifest.get("claim_boundary", PILOT_PRIVACY_REVIEW_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Review rows: {manifest.get('row_count', 0)}",
        f"- Rows requiring review: {manifest.get('review_required_count', 0)}",
        f"- Closure candidates: {manifest.get('pilot_acceptance_closure_candidate_count', 0)}",
        "",
        "## Review Rows",
        "",
        "| Item | Type | Coordinate Class | Privacy Risk | Required Decision |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {item} | {item_type} | {coordinate_class} | {risk} | {decision} |".format(
                item=_cell(row.get("review_item_id", "")),
                item_type=_cell(row.get("item_type", "")),
                coordinate_class=_cell(row.get("coordinate_class", "")),
                risk=_cell(row.get("privacy_risk_level", "")),
                decision=_cell(row.get("required_reviewer_decision", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Required Reviewer Actions",
            "",
            "- Review `data/regions/pilot_region.yaml` and `docs/pilot_region_data_card.md` together.",
            "- Confirm that public and synthetic points are acceptable for a non-operational demo.",
            "- Confirm whether the pilot can be cited in the manuscript before evidence gates close.",
            "- Create `data/manifests/pilot_acceptance.json` only after a real reviewer decision.",
            "",
        ]
    )
    return "\n".join(lines)


def _boundary_row(region_id: str, region: Mapping[str, Any]) -> dict[str, str]:
    boundary = region.get("boundary", {})
    boundary_type = _clean(boundary.get("type") if isinstance(boundary, Mapping) else "")
    return _row(
        region_id=region_id,
        review_item_id="region_boundary",
        item_type="boundary",
        item_name=f"{region_id} {boundary_type} boundary",
        coordinate_class="public_admin_or_bbox",
        sensitivity_label=_clean((region.get("metadata") or {}).get("data_sensitivity"))
        if isinstance(region.get("metadata"), Mapping)
        else "",
        exact_coordinate_public=True,
        synthetic_or_aggregated=False,
        privacy_risk_level="low_pending_review",
        operational_misuse_risk="medium_if_overclaimed",
        required_reviewer_decision=(
            "confirm bbox is acceptable public geography and not an operational area definition"
        ),
        notes="Boundary supports OSM cache extraction and regional context only.",
    )


def _zone_row(region_id: str, item_type: str, item: Mapping[str, Any]) -> dict[str, str]:
    metadata = item.get("metadata", {})
    if not isinstance(metadata, Mapping):
        metadata = {}
    coordinate_class = _clean(metadata.get("coordinate_class"))
    sensitivity = _clean(metadata.get("sensitivity"))
    is_public = coordinate_class == "public"
    is_synthetic = coordinate_class in {"synthetic", "aggregated", "zone_centroid"}
    privacy_risk = "low_pending_review"
    if item_type == "destination_zone" and not is_synthetic:
        privacy_risk = "elevated_requires_review"
    elif is_synthetic:
        privacy_risk = "low_if_abstraction_accepted"
    decision = _decision_for_item(item_type, coordinate_class)
    return _row(
        region_id=region_id,
        review_item_id=f"{item_type}:{_clean(item.get('id'))}",
        item_type=item_type,
        item_name=_clean(item.get("name")),
        coordinate_class=coordinate_class,
        sensitivity_label=sensitivity,
        exact_coordinate_public=is_public,
        synthetic_or_aggregated=is_synthetic,
        privacy_risk_level=privacy_risk,
        operational_misuse_risk="medium_if_overclaimed",
        required_reviewer_decision=decision,
        notes=(
            "Review coordinate class, sensitivity label, and manuscript wording before "
            "pilot acceptance."
        ),
    )


def _coordinate_policy_row(region_id: str, region: Mapping[str, Any]) -> dict[str, str]:
    metadata = region.get("metadata", {})
    if not isinstance(metadata, Mapping):
        metadata = {}
    return _row(
        region_id=region_id,
        review_item_id="coordinate_policy",
        item_type="policy",
        item_name="Region coordinate policy",
        coordinate_class=_clean(metadata.get("coordinate_policy")),
        sensitivity_label=_clean(metadata.get("data_sensitivity")),
        exact_coordinate_public=False,
        synthetic_or_aggregated=True,
        privacy_risk_level="policy_pending_review",
        operational_misuse_risk="medium_if_ignored",
        required_reviewer_decision=(
            "confirm all retained points follow the public_or_synthetic_points_only policy"
        ),
        notes="Policy row prevents point-level metadata from being reviewed in isolation.",
    )


def _data_card_row(region_id: str, data_card_path: str | Path) -> dict[str, str]:
    data_card = Path(data_card_path)
    text = data_card.read_text(encoding="utf-8") if data_card.exists() else ""
    has_not_operational = "not a calibrated emergency" in text.lower() or "not an operational" in text.lower()
    return _row(
        region_id=region_id,
        review_item_id="data_card_claim_boundary",
        item_type="claim_boundary",
        item_name="Pilot region data card claim boundary",
        coordinate_class="documentation",
        sensitivity_label="claim_boundary",
        exact_coordinate_public=False,
        synthetic_or_aggregated=False,
        privacy_risk_level="low_if_claim_boundary_accepted",
        operational_misuse_risk="high_if_removed",
        required_reviewer_decision=(
            "confirm data card keeps the pilot non-sensitive, non-operational, and not calibrated"
        ),
        notes=(
            "Detected non-operational/calibration boundary in data card."
            if has_not_operational
            else "Data card claim boundary text needs reviewer attention."
        ),
    )


def _decision_for_item(item_type: str, coordinate_class: str) -> str:
    if item_type == "destination_zone":
        return (
            "confirm destination is synthetic or sufficiently generalized and cannot be read as a sensitive operational destination"
        )
    if item_type == "assembly_zone":
        return (
            "confirm public assembly demo point is not framed as an operational assembly order"
        )
    if item_type.startswith("rail_"):
        return "confirm public station point is acceptable for non-operational multimodal demonstration"
    if coordinate_class == "synthetic":
        return "confirm synthetic coordinate abstraction is adequate"
    return "confirm coordinate handling and sensitivity label"


def _row(
    *,
    region_id: str,
    review_item_id: str,
    item_type: str,
    item_name: str,
    coordinate_class: str,
    sensitivity_label: str,
    exact_coordinate_public: bool,
    synthetic_or_aggregated: bool,
    privacy_risk_level: str,
    operational_misuse_risk: str,
    required_reviewer_decision: str,
    notes: str,
) -> dict[str, str]:
    return {
        "review_item_id": review_item_id,
        "region_id": region_id,
        "item_type": item_type,
        "item_name": item_name,
        "coordinate_class": coordinate_class,
        "sensitivity_label": sensitivity_label,
        "exact_coordinate_public": _bool_text(exact_coordinate_public),
        "synthetic_or_aggregated": _bool_text(synthetic_or_aggregated),
        "privacy_risk_level": privacy_risk_level,
        "operational_misuse_risk": operational_misuse_risk,
        "required_reviewer_decision": required_reviewer_decision,
        "target_acceptance_artifact": "data/manifests/pilot_acceptance.json",
        "can_support_pilot_acceptance": "false",
        "publication_use_status": "review support only; formal pilot acceptance is absent",
        "claim_boundary": PILOT_PRIVACY_REVIEW_SCOPE,
        "notes": notes,
    }


def _sequence(value: object) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, Sequence) or isinstance(value, str):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _counts(values: Sequence[str] | Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


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
    "DEFAULT_PILOT_DATA_CARD_PATH",
    "DEFAULT_PILOT_PRIVACY_REVIEW_DOC_PATH",
    "DEFAULT_PILOT_PRIVACY_REVIEW_MANIFEST_PATH",
    "DEFAULT_PILOT_PRIVACY_REVIEW_PACKET_PATH",
    "DEFAULT_PILOT_REGION_PATH",
    "PILOT_PRIVACY_REVIEW_COLUMNS",
    "PILOT_PRIVACY_REVIEW_SCOPE",
    "build_pilot_privacy_review_manifest",
    "build_pilot_privacy_review_markdown",
    "build_pilot_privacy_review_rows",
    "write_pilot_privacy_review_packet",
]
