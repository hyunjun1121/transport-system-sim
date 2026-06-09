"""Static timetable rail-service candidate packet generation.

The packet combines a retained static timetable cache with the existing
segment-pair diagnostic. It is reviewer-triage support only and intentionally
does not modify ``data/parameters/rail_service_evidence.csv``.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from statistics import median
from typing import Any, Mapping, Sequence

from src.realworld.rail_evidence import DEFAULT_RAIL_SERVICE_EVIDENCE_PATH
from src.realworld.rail_timetable import load_cached_timetable_events


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STATIC_TIMETABLE_CACHE_PATH = (
    PROJECT_ROOT / "data" / "rail" / "pilot_rail_static_timetable_cache.csv"
)
DEFAULT_STATIC_TIMETABLE_CACHE_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "rail" / "pilot_rail_static_timetable_cache_manifest.json"
)
DEFAULT_SEGMENT_PAIR_DIAGNOSTIC_PATH = (
    PROJECT_ROOT / "data" / "rail" / "pilot_rail_static_timetable_segment_pair_diagnostic.csv"
)
DEFAULT_SEGMENT_PAIR_DIAGNOSTIC_MANIFEST_PATH = (
    PROJECT_ROOT
    / "data"
    / "rail"
    / "pilot_rail_static_timetable_segment_pair_diagnostic_manifest.json"
)
DEFAULT_RAIL_STATIC_CANDIDATE_PATH = (
    PROJECT_ROOT / "data" / "rail" / "rail_service_evidence_static_candidate.csv"
)
DEFAULT_RAIL_STATIC_CANDIDATE_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "rail" / "rail_service_evidence_static_candidate_manifest.json"
)
DEFAULT_RAIL_STATIC_CANDIDATE_DOC_PATH = (
    PROJECT_ROOT / "docs" / "rail_service_evidence_static_candidate.md"
)

RAIL_STATIC_CANDIDATE_SCOPE = (
    "Static timetable rail-service candidate only; not rail_service_evidence.csv, "
    "not rail evidence gate closure, not source/provenance acceptance, not "
    "observed transfer calibration, not publication readiness, not final-study "
    "readiness, and not formal acceptance."
)

RAIL_STATIC_CANDIDATE_COLUMNS: tuple[str, ...] = (
    "candidate_id",
    "artifact_class",
    "candidate_only",
    "region_id",
    "access_point",
    "egress_point",
    "access_station_name",
    "egress_station_name",
    "headway_candidate_min",
    "travel_time_candidate_min",
    "capacity_candidate_pax_per_train",
    "derived_fields_candidate",
    "derived_field_counts",
    "headway_source_class",
    "travel_time_source_class",
    "capacity_source_class",
    "headway_source_path",
    "headway_source_sha256",
    "travel_time_source_path",
    "travel_time_source_sha256",
    "source_status_candidate",
    "transfer_treatment",
    "travel_time_value_status",
    "capacity_value_status",
    "candidate_status",
    "review_status",
    "can_support_rail_evidence_gate",
    "can_support_publication_gate",
    "can_support_final_study_gate",
    "can_support_acceptance_gate",
    "accepted_source_backed_rail_service_evidence",
    "rail_source_decision_recorded",
    "source_license_or_provenance_review_status",
    "writes_default_rail_service_evidence_path",
    "replaces_data_parameters_rail_service_evidence",
    "gate_decision_authority",
    "claim_boundary",
    "remaining_review_need",
)


def build_rail_static_candidate_rows(
    *,
    timetable_cache_path: str | Path = DEFAULT_STATIC_TIMETABLE_CACHE_PATH,
    segment_pair_diagnostic_path: str | Path = DEFAULT_SEGMENT_PAIR_DIAGNOSTIC_PATH,
    current_capacity_pax_per_train: float = 500.0,
) -> list[dict[str, str]]:
    """Return one static timetable rail-service candidate row."""

    cache_path = Path(timetable_cache_path)
    diagnostic_path = Path(segment_pair_diagnostic_path)
    events = load_cached_timetable_events(cache_path)
    access_departures = sorted(
        event.event_time_min
        for event in events
        if event.station_role == "access" and event.event_type == "departure"
    )
    if len(access_departures) < 2:
        raise ValueError("at least two access departures are required")
    headways = [
        access_departures[index + 1] - access_departures[index]
        for index in range(len(access_departures) - 1)
    ]
    if any(value <= 0.0 for value in headways):
        raise ValueError("access departures must be strictly increasing")

    pair = _load_segment_pair_row(diagnostic_path)
    access_station = next(
        event.station_name for event in events if event.station_role == "access"
    )
    return [
        {
            "candidate_id": "songpa_static_timetable_segment_pair_candidate_v1",
            "artifact_class": "non_formal_static_rail_service_candidate",
            "candidate_only": "true",
            "region_id": "songpa_public_demo",
            "access_point": "S",
            "egress_point": "R",
            "access_station_name": access_station,
            "egress_station_name": str(pair.get("destination_station_name", "")),
            "headway_candidate_min": _format_number(median(headways)),
            "travel_time_candidate_min": str(pair.get("median_total_minutes", "")),
            "capacity_candidate_pax_per_train": _format_number(
                current_capacity_pax_per_train
            ),
            "derived_fields_candidate": "headway",
            "derived_field_counts": "headway=1;travel_time=0;capacity=0",
            "headway_source_class": "cached-static-timetable-candidate",
            "travel_time_source_class": (
                "proxy-from-segment-pair-diagnostic-with-assumed-transfer"
            ),
            "capacity_source_class": "sensitivity-only",
            "headway_source_path": _display_path(cache_path),
            "headway_source_sha256": _file_sha256(cache_path),
            "travel_time_source_path": _display_path(diagnostic_path),
            "travel_time_source_sha256": _file_sha256(diagnostic_path),
            "source_status_candidate": "non_formal_static_timetable_candidate",
            "transfer_treatment": (
                "includes assumed Seokchon transfer buffer; not observed walking, "
                "platform circulation, crowding, or transfer calibration"
            ),
            "travel_time_value_status": "proxy_not_derived_rail_service_evidence",
            "capacity_value_status": "sensitivity_only_or_pending",
            "candidate_status": "candidate_only_not_reviewed",
            "review_status": "requires_rail_source_and_transfer_review",
            "can_support_rail_evidence_gate": "false",
            "can_support_publication_gate": "false",
            "can_support_final_study_gate": "false",
            "can_support_acceptance_gate": "false",
            "accepted_source_backed_rail_service_evidence": "false",
            "rail_source_decision_recorded": "false",
            "source_license_or_provenance_review_status": "pending_or_not_recorded",
            "writes_default_rail_service_evidence_path": "false",
            "replaces_data_parameters_rail_service_evidence": "false",
            "gate_decision_authority": "none",
            "claim_boundary": RAIL_STATIC_CANDIDATE_SCOPE,
            "remaining_review_need": (
                "Review retained timetable source/provenance/license, station "
                "identifier namespace, transfer buffer, capacity treatment, and "
                "formal source decision before editing rail_service_evidence.csv."
            ),
        }
    ]


def write_rail_static_candidate_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_RAIL_STATIC_CANDIDATE_PATH,
    manifest_path: str | Path = DEFAULT_RAIL_STATIC_CANDIDATE_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_RAIL_STATIC_CANDIDATE_DOC_PATH,
    timetable_cache_manifest_path: str | Path = DEFAULT_STATIC_TIMETABLE_CACHE_MANIFEST_PATH,
    segment_pair_diagnostic_manifest_path: str | Path = DEFAULT_SEGMENT_PAIR_DIAGNOSTIC_MANIFEST_PATH,
) -> dict[str, Any]:
    """Write static rail candidate CSV, manifest, and Markdown doc."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RAIL_STATIC_CANDIDATE_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {column: str(row.get(column, "")) for column in RAIL_STATIC_CANDIDATE_COLUMNS}
            )

    summary = build_rail_static_candidate_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        timetable_cache_manifest_path=timetable_cache_manifest_path,
        segment_pair_diagnostic_manifest_path=segment_pair_diagnostic_manifest_path,
    )
    manifest.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_rail_static_candidate_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_rail_static_candidate_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_RAIL_STATIC_CANDIDATE_PATH,
    manifest_path: str | Path = DEFAULT_RAIL_STATIC_CANDIDATE_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_RAIL_STATIC_CANDIDATE_DOC_PATH,
    timetable_cache_manifest_path: str | Path = DEFAULT_STATIC_TIMETABLE_CACHE_MANIFEST_PATH,
    segment_pair_diagnostic_manifest_path: str | Path = DEFAULT_SEGMENT_PAIR_DIAGNOSTIC_MANIFEST_PATH,
) -> dict[str, Any]:
    """Return fail-closed manifest for the static rail candidate."""

    return {
        "schema_version": 1,
        "result_scope": RAIL_STATIC_CANDIDATE_SCOPE,
        "claim_boundary": (
            RAIL_STATIC_CANDIDATE_SCOPE
            + " It can support reviewer triage only."
        ),
        "row_count": len(rows),
        "artifact_class": "non_formal_static_rail_service_candidate",
        "candidate_only": True,
        "candidate_table_present": True,
        "formal_target_path": _display_path(DEFAULT_RAIL_SERVICE_EVIDENCE_PATH),
        "formal_target_written": False,
        "rail_service_evidence_written": False,
        "writes_default_rail_service_evidence_path": False,
        "replaces_data_parameters_rail_service_evidence": False,
        "formal_acceptance_evidence": False,
        "publication_ready": False,
        "final_study_ready": False,
        "can_mark_complete": False,
        "can_support_rail_evidence_gate": False,
        "can_support_publication_gate": False,
        "can_support_final_study_gate": False,
        "can_support_acceptance_gate": False,
        "accepted_source_backed_rail_service_evidence": False,
        "rail_source_decision_recorded": False,
        "gate_decision_authority": "none",
        "source_provenance_accepted": False,
        "source_license_or_provenance_review_status": "pending_or_not_recorded",
        "observed_transfer_calibration": False,
        "capacity_source_backed": False,
        "derived_field_counts": {
            "headway": len(rows),
            "travel_time": 0,
            "capacity": 0,
        },
        "travel_time_value_status": "proxy_not_derived",
        "capacity_value_status": "sensitivity_only_or_pending",
        "inputs": {
            "timetable_cache_manifest": _display_path(
                Path(timetable_cache_manifest_path)
            ),
            "segment_pair_diagnostic_manifest": _display_path(
                Path(segment_pair_diagnostic_manifest_path)
            ),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "remaining_blockers": [
            "review static timetable source provenance, license, station identifier namespace, and filters",
            "replace assumed transfer buffer with source-backed or reviewed bounded transfer treatment",
            "record rail capacity as source-backed or explicitly retained sensitivity-only treatment",
            "record formal rail source decisions before editing data/parameters/rail_service_evidence.csv",
            "rerun rail, parameter, publication, and final-study audits after any formal rail evidence update",
        ],
    }


def build_rail_static_candidate_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return a human-readable static rail candidate packet."""

    lines = [
        "# Rail Service Static Timetable Candidate",
        "",
        str(manifest.get("claim_boundary", RAIL_STATIC_CANDIDATE_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Final study ready: `{str(manifest.get('final_study_ready', False)).lower()}`",
        f"- Can support rail evidence gate: `{str(manifest.get('can_support_rail_evidence_gate', False)).lower()}`",
        f"- Formal target written: `{str(manifest.get('formal_target_written', False)).lower()}`",
        f"- Rows: {manifest.get('row_count', 0)}",
        "",
        "## Candidate Rows",
        "",
        "| Candidate | Access | Egress | Headway | Travel time | Capacity | Transfer treatment |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            "| {candidate} | {access} | {egress} | {headway} | {travel} | {capacity} | {transfer} |".format(
                candidate=_cell(row.get("candidate_id", "")),
                access=_cell(row.get("access_station_name", "")),
                egress=_cell(row.get("egress_station_name", "")),
                headway=_cell(row.get("headway_candidate_min", "")),
                travel=_cell(row.get("travel_time_candidate_min", "")),
                capacity=_cell(row.get("capacity_candidate_pax_per_train", "")),
                transfer=_cell(row.get("transfer_treatment", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Source Constraints",
            "",
            "- Headway is a static timetable candidate, not an accepted rail evidence row.",
            "- Travel time comes from a segment-pair diagnostic that includes an assumed transfer buffer.",
            "- Capacity remains sensitivity-only.",
            "- Do not use this candidate as `data/parameters/rail_service_evidence.csv` without formal source decisions.",
            "",
        ]
    )
    return "\n".join(lines)


def _load_segment_pair_row(path: Path) -> dict[str, str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = [
            row
            for row in csv.DictReader(handle)
            if row.get("row_type") == "segment_pair_with_assumed_transfer_buffer"
        ]
    if len(rows) != 1:
        raise ValueError(f"{path} must contain exactly one segment-pair row")
    if not rows[0].get("median_total_minutes"):
        raise ValueError(f"{path} segment-pair row must include median_total_minutes")
    return rows[0]


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


def _format_number(value: float) -> str:
    parsed = float(value)
    if parsed.is_integer():
        return str(int(parsed))
    return f"{parsed:.3f}".rstrip("0").rstrip(".")


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


__all__ = [
    "DEFAULT_RAIL_STATIC_CANDIDATE_DOC_PATH",
    "DEFAULT_RAIL_STATIC_CANDIDATE_MANIFEST_PATH",
    "DEFAULT_RAIL_STATIC_CANDIDATE_PATH",
    "RAIL_STATIC_CANDIDATE_COLUMNS",
    "RAIL_STATIC_CANDIDATE_SCOPE",
    "build_rail_static_candidate_manifest",
    "build_rail_static_candidate_markdown",
    "build_rail_static_candidate_rows",
    "write_rail_static_candidate_packet",
]
