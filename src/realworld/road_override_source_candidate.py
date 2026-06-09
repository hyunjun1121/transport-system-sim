"""Road-class override source-candidate packet generation.

This module turns the current draft road-class override worksheet into a
source-candidate review packet. It intentionally does not write the formal
``data/parameters/road_class_overrides.csv`` target and cannot close road,
publication, final-study, or formal acceptance gates.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.realworld.road_override_audit import DEFAULT_ROAD_CLASS_OVERRIDE_DRAFT_PATH
from src.realworld.road_overrides import load_road_class_overrides


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROAD_OVERRIDE_SOURCE_CANDIDATE_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "road_class_override_source_candidate.csv"
)
DEFAULT_ROAD_OVERRIDE_SOURCE_CANDIDATE_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "road_class_override_source_candidate_manifest.json"
)
DEFAULT_ROAD_OVERRIDE_SOURCE_CANDIDATE_DOC_PATH = (
    PROJECT_ROOT / "docs" / "road_class_override_source_candidate.md"
)
FORMAL_ROAD_CLASS_OVERRIDE_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "road_class_overrides.csv"
)

SPEED_LIMIT_SOURCE_URL = (
    "https://www.law.go.kr/LSW/lsPdfPrint.do?"
    "ancYnChk=0&bylChaChk=N&efGubun=Y&efYd=20220420&"
    "joAllCheck=Y&joEfOutPutYn=on&lsiSeq=241893&mokChaChk=N"
)
SPEED_5030_SOURCE_URL = (
    "https://www.easylaw.go.kr/CSP/IssueQaRetrieve.laf?"
    "issueqaSeq=110&targetRow=221&topMenu=openUl7"
)
FHWA_FREEWAY_CAPACITY_URL = "https://www.fhwa.dot.gov/ohim/hpmsmanl/appn1.cfm"
FHWA_URBAN_CAPACITY_URL = "https://www.fhwa.dot.gov/ohim/hpmsmanl/appn7.cfm"

ROAD_OVERRIDE_SOURCE_CANDIDATE_SCOPE = (
    "Road-class override source-candidate packet only; not a reviewed override "
    "table, not source-backed speed or capacity evidence, not calibrated "
    "disruption evidence, not proof that overrides were applied, and not "
    "publication, final-study, or formal acceptance evidence."
)

ROAD_OVERRIDE_SOURCE_CANDIDATE_COLUMNS: tuple[str, ...] = (
    "highway",
    "speed_kph",
    "capacity_veh_per_hr",
    "base_p_fail",
    "source_class",
    "source_name",
    "source_url_or_citation",
    "notes",
    "speed_source_class",
    "speed_source_name",
    "speed_source_url_or_citation",
    "capacity_source_class",
    "capacity_source_name",
    "capacity_source_url_or_citation",
    "base_p_fail_source_class",
    "base_p_fail_source_name",
    "base_p_fail_source_url_or_citation",
    "review_priority",
    "routeable_length_share",
    "routeable_edge_count",
    "current_speed_kph",
    "current_capacity_veh_per_hr",
    "current_base_p_fail",
    "speed_candidate_value_kph",
    "speed_candidate_source_class",
    "speed_candidate_source_name",
    "speed_candidate_url_or_citation",
    "speed_candidate_scope",
    "capacity_candidate_value_veh_per_hr",
    "capacity_candidate_source_class",
    "capacity_candidate_source_name",
    "capacity_candidate_url_or_citation",
    "capacity_candidate_scope",
    "base_p_fail_candidate_value",
    "base_p_fail_candidate_source_class",
    "base_p_fail_candidate_source_name",
    "base_p_fail_candidate_url_or_citation",
    "base_p_fail_candidate_scope",
    "candidate_status",
    "review_status",
    "formal_acceptance_status",
    "can_support_formal_override",
    "can_support_publication_gate",
    "can_support_final_study_gate",
    "claim_boundary",
    "remaining_review_need",
)


def build_road_override_source_candidate_rows(
    draft_path: str | Path = DEFAULT_ROAD_CLASS_OVERRIDE_DRAFT_PATH,
) -> list[dict[str, str]]:
    """Build conservative source-candidate rows from the current draft table."""

    path = Path(draft_path)
    load_road_class_overrides(path)
    raw_rows = _load_rows(path)
    return [_candidate_row(row) for row in raw_rows if _has_highway(row)]


def write_road_override_source_candidate_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_ROAD_OVERRIDE_SOURCE_CANDIDATE_PATH,
    manifest_path: str | Path = DEFAULT_ROAD_OVERRIDE_SOURCE_CANDIDATE_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_ROAD_OVERRIDE_SOURCE_CANDIDATE_DOC_PATH,
    draft_path: str | Path = DEFAULT_ROAD_CLASS_OVERRIDE_DRAFT_PATH,
) -> dict[str, Any]:
    """Write source-candidate CSV, manifest, and Markdown review packet."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=ROAD_OVERRIDE_SOURCE_CANDIDATE_COLUMNS,
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in ROAD_OVERRIDE_SOURCE_CANDIDATE_COLUMNS
                }
            )

    summary = build_road_override_source_candidate_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        draft_path=draft_path,
    )
    manifest.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_road_override_source_candidate_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_road_override_source_candidate_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_ROAD_OVERRIDE_SOURCE_CANDIDATE_PATH,
    manifest_path: str | Path = DEFAULT_ROAD_OVERRIDE_SOURCE_CANDIDATE_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_ROAD_OVERRIDE_SOURCE_CANDIDATE_DOC_PATH,
    draft_path: str | Path = DEFAULT_ROAD_CLASS_OVERRIDE_DRAFT_PATH,
) -> dict[str, Any]:
    """Return a fail-closed manifest for the source-candidate packet."""

    draft = Path(draft_path)
    field_counts = {
        "speed_candidate_source_class": _counts(
            row.get("speed_candidate_source_class", "") for row in rows
        ),
        "capacity_candidate_source_class": _counts(
            row.get("capacity_candidate_source_class", "") for row in rows
        ),
        "base_p_fail_candidate_source_class": _counts(
            row.get("base_p_fail_candidate_source_class", "") for row in rows
        ),
    }
    return {
        "schema_version": 1,
        "result_scope": ROAD_OVERRIDE_SOURCE_CANDIDATE_SCOPE,
        "claim_boundary": (
            ROAD_OVERRIDE_SOURCE_CANDIDATE_SCOPE
            + " The packet can support reviewer triage only."
        ),
        "candidate_table_present": True,
        "reviewed_override_table_present": False,
        "row_count": len(rows),
        "highway_classes": sorted(
            {
                str(row.get("highway", "")).strip()
                for row in rows
                if str(row.get("highway", "")).strip()
            }
        ),
        "field_source_class_counts": field_counts,
        "formal_target_path": _display_path(FORMAL_ROAD_CLASS_OVERRIDE_PATH),
        "formal_target_written": False,
        "formal_target_written_by_this_packet": False,
        "formal_target_present_at_write": FORMAL_ROAD_CLASS_OVERRIDE_PATH.exists(),
        "formal_acceptance_evidence": False,
        "formal_acceptance_ready": False,
        "gate_closure_supported": False,
        "publication_ready": False,
        "final_study_ready": False,
        "can_mark_complete": False,
        "can_support_road_evidence_gate": False,
        "can_support_road_application_gate": False,
        "road_class_overrides_applied": False,
        "overrides_applied": False,
        "graph_source_records_override": False,
        "inputs": {
            "draft_path": _display_path(draft),
            "draft_sha256": _file_sha256(draft) if draft.exists() else "",
            "road_class_override_source_candidate_path": _display_path(
                Path(output_path)
            ),
            "road_class_override_source_candidate_sha256": (
                _file_sha256(Path(output_path)) if Path(output_path).exists() else ""
            ),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "sources_consulted": {
            "speed_limit_bounds": [
                SPEED_LIMIT_SOURCE_URL,
                SPEED_5030_SOURCE_URL,
            ],
            "capacity_proxy_references": [
                FHWA_FREEWAY_CAPACITY_URL,
                FHWA_URBAN_CAPACITY_URL,
            ],
        },
        "remaining_blockers": [
            "review whether Korean statutory speed-limit bounds justify each road-class free-flow speed",
            "replace FHWA/HCM-derived capacity proxy candidates with Korean agency, count, or benchmark-calibrated capacity evidence where available",
            "replace sensitivity-only base-disruption probabilities with hazard, incident, literature, or accepted scenario evidence",
            "write data/parameters/road_class_overrides.csv only after source-backed review",
            "rerun accepted pilot outputs with the reviewed override table and record matching SHA256 application evidence",
        ],
    }


def build_road_override_source_candidate_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return a human-readable source-candidate packet."""

    lines = [
        "# Road Class Override Source Candidate",
        "",
        str(manifest.get("claim_boundary", ROAD_OVERRIDE_SOURCE_CANDIDATE_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Final study ready: `{str(manifest.get('final_study_ready', False)).lower()}`",
        f"- Formal acceptance evidence: `{str(manifest.get('formal_acceptance_evidence', False)).lower()}`",
        f"- Formal target written: `{str(manifest.get('formal_target_written', False)).lower()}`",
        f"- Rows: {manifest.get('row_count', 0)}",
        f"- Formal target path: `{manifest.get('formal_target_path', '')}`",
        "",
        "## Candidate Rows",
        "",
        "| Highway | Priority | Current speed | Current capacity | Current base p_fail | Speed source scope | Capacity source scope | Remaining need |",
        "| --- | --- | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {highway} | {priority} | {speed} | {capacity} | {base} | {speed_scope} | {capacity_scope} | {need} |".format(
                highway=_cell(row.get("highway", "")),
                priority=_cell(row.get("review_priority", "")),
                speed=_cell(row.get("current_speed_kph", "")),
                capacity=_cell(row.get("current_capacity_veh_per_hr", "")),
                base=_cell(row.get("current_base_p_fail", "")),
                speed_scope=_cell(row.get("speed_candidate_scope", "")),
                capacity_scope=_cell(row.get("capacity_candidate_scope", "")),
                need=_cell(row.get("remaining_review_need", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Source Constraints",
            "",
            "- Speed rows use public legal speed-limit bounds as a candidate constraint, not a calibrated free-flow-speed estimate.",
            "- Capacity rows use FHWA/HCM-derived capacity references as a proxy screen, not Korean road-class calibration.",
            "- Base disruption probabilities remain sensitivity-only in every row.",
            "- Do not copy this file to `data/parameters/road_class_overrides.csv` without review and accepted application evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def _candidate_row(row: Mapping[str, str]) -> dict[str, str]:
    highway = str(row.get("highway", "")).strip().lower()
    return {
        "highway": highway,
        "speed_kph": str(row.get("speed_kph", "")).strip(),
        "capacity_veh_per_hr": str(row.get("capacity_veh_per_hr", "")).strip(),
        "base_p_fail": str(row.get("base_p_fail", "")).strip(),
        "source_class": str(row.get("source_class", "")).strip(),
        "source_name": str(row.get("source_name", "")).strip(),
        "source_url_or_citation": str(row.get("source_url_or_citation", "")).strip(),
        "notes": (
            str(row.get("notes", "")).strip()
            + " Candidate-only source suggestions are not reviewed evidence."
        ),
        "speed_source_class": str(row.get("speed_source_class", "")).strip(),
        "speed_source_name": str(row.get("speed_source_name", "")).strip(),
        "speed_source_url_or_citation": str(
            row.get("speed_source_url_or_citation", "")
        ).strip(),
        "capacity_source_class": str(row.get("capacity_source_class", "")).strip(),
        "capacity_source_name": str(row.get("capacity_source_name", "")).strip(),
        "capacity_source_url_or_citation": str(
            row.get("capacity_source_url_or_citation", "")
        ).strip(),
        "base_p_fail_source_class": str(row.get("base_p_fail_source_class", "")).strip(),
        "base_p_fail_source_name": str(row.get("base_p_fail_source_name", "")).strip(),
        "base_p_fail_source_url_or_citation": str(
            row.get("base_p_fail_source_url_or_citation", "")
        ).strip(),
        "review_priority": str(row.get("review_priority", "")).strip(),
        "routeable_length_share": str(row.get("routeable_length_share", "")).strip(),
        "routeable_edge_count": str(row.get("routeable_edge_count", "")).strip(),
        "current_speed_kph": str(row.get("speed_kph", "")).strip(),
        "current_capacity_veh_per_hr": str(row.get("capacity_veh_per_hr", "")).strip(),
        "current_base_p_fail": str(row.get("base_p_fail", "")).strip(),
        "speed_candidate_value_kph": str(row.get("speed_kph", "")).strip(),
        "speed_candidate_source_class": "public-data-derived",
        "speed_candidate_source_name": (
            "Korean road speed-limit bounds; Road Traffic Act Enforcement Rule "
            "Article 19 and Safety Speed 5030 public legal explanation"
        ),
        "speed_candidate_url_or_citation": (
            f"{SPEED_LIMIT_SOURCE_URL}; {SPEED_5030_SOURCE_URL}"
        ),
        "speed_candidate_scope": _speed_scope(highway),
        "capacity_candidate_value_veh_per_hr": str(
            row.get("capacity_veh_per_hr", "")
        ).strip(),
        "capacity_candidate_source_class": "literature-derived",
        "capacity_candidate_source_name": (
            "FHWA HPMS Appendix N HCM-derived freeway and urban street "
            "capacity procedures"
        ),
        "capacity_candidate_url_or_citation": (
            f"{FHWA_FREEWAY_CAPACITY_URL}; {FHWA_URBAN_CAPACITY_URL}"
        ),
        "capacity_candidate_scope": (
            "Screen current BPR capacity proxy against HCM-derived lane-capacity "
            "ranges; not Korean traffic-count calibration."
        ),
        "base_p_fail_candidate_value": str(row.get("base_p_fail", "")).strip(),
        "base_p_fail_candidate_source_class": "sensitivity-only",
        "base_p_fail_candidate_source_name": (
            "Current scenario disruption proxy pending hazard or incident review"
        ),
        "base_p_fail_candidate_url_or_citation": "src/realworld/attributes.py",
        "base_p_fail_candidate_scope": (
            "Scenario sensitivity value only; not observed disruption probability."
        ),
        "candidate_status": "candidate_only_not_reviewed",
        "review_status": "requires_source_review",
        "formal_acceptance_status": "not_formal_acceptance_evidence",
        "can_support_formal_override": "false",
        "can_support_publication_gate": "false",
        "can_support_final_study_gate": "false",
        "claim_boundary": ROAD_OVERRIDE_SOURCE_CANDIDATE_SCOPE,
        "remaining_review_need": _remaining_need(highway),
    }


def _speed_scope(highway: str) -> str:
    if highway == "residential":
        return (
            "Candidate is consistent with urban residential/local 30 km/h safety "
            "speed framing, but still needs road-class mapping review."
        )
    if highway in {"trunk", "motorway", "motorway_link", "trunk_link"}:
        return (
            "Candidate is bounded by motorway/controlled-access speed-limit "
            "rules, but exact free-flow speed still needs facility review."
        )
    return (
        "Candidate is bounded by Korean general-road speed-limit ranges, but "
        "exact free-flow speed remains a reviewed modeling assumption."
    )


def _remaining_need(highway: str) -> str:
    if highway in {"trunk", "motorway", "motorway_link", "trunk_link"}:
        return (
            "Confirm controlled-access class mapping, lane count, heavy-vehicle "
            "adjustment, and disruption source before formal override use."
        )
    return (
        "Confirm urban/rural context, lane count, signal/access effects, and "
        "disruption source before formal override use."
    )


def _load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _has_highway(row: Mapping[str, str]) -> bool:
    return bool(str(row.get("highway", "")).strip())


def _counts(values: Sequence[str] | Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


__all__ = [
    "DEFAULT_ROAD_OVERRIDE_SOURCE_CANDIDATE_DOC_PATH",
    "DEFAULT_ROAD_OVERRIDE_SOURCE_CANDIDATE_MANIFEST_PATH",
    "DEFAULT_ROAD_OVERRIDE_SOURCE_CANDIDATE_PATH",
    "FORMAL_ROAD_CLASS_OVERRIDE_PATH",
    "ROAD_OVERRIDE_SOURCE_CANDIDATE_COLUMNS",
    "ROAD_OVERRIDE_SOURCE_CANDIDATE_SCOPE",
    "build_road_override_source_candidate_manifest",
    "build_road_override_source_candidate_markdown",
    "build_road_override_source_candidate_rows",
    "write_road_override_source_candidate_packet",
]
