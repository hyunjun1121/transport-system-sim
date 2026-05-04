"""Rail timing source-request packet generation.

The final rail-evidence blocker requires reviewed cached timing artifacts, not
more assumptions. This module writes a small source-request worksheet that names
the exact public source candidates, credentials or reviewed files required,
cache outputs, derivation commands, and evidence fields each source can close.
It does not fetch live data and does not upgrade rail claims.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.rail_evidence_review_packet import DEFAULT_RAIL_ASSUMPTIONS_PATH
from src.realworld.rail_station_binding import (
    DEFAULT_RAIL_STATION_BINDING_PATH,
    RailStationBinding,
    load_rail_station_bindings,
    summarize_rail_station_bindings,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RAIL_TIMING_SOURCE_REQUEST_PACKET_PATH = (
    PROJECT_ROOT / "data" / "rail" / "rail_timing_source_request_packet.csv"
)
DEFAULT_RAIL_TIMING_SOURCE_REQUEST_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "rail" / "rail_timing_source_request_manifest.json"
)
RAIL_TIMING_SOURCE_REQUEST_SCOPE = (
    "Rail timing source-request packet; not cached rail timing evidence, "
    "not GTFS validation, not rail-service calibration, and not operational "
    "rail availability evidence."
)
RAIL_TIMING_SOURCE_REQUEST_COLUMNS: tuple[str, ...] = (
    "request_id",
    "region_id",
    "evidence_fields",
    "source_type",
    "source_name",
    "source_url_or_citation",
    "required_external_input",
    "access_station_name",
    "access_station_code",
    "egress_station_name",
    "egress_station_code",
    "source_cache_path",
    "raw_payload_path",
    "fetch_command",
    "derive_command",
    "expected_source_status",
    "expected_derived_fields",
    "can_close_rail_timing_gate",
    "publication_use_status",
    "claim_boundary",
    "notes",
)


def build_rail_timing_source_request_rows(
    *,
    station_binding_path: str | Path = DEFAULT_RAIL_STATION_BINDING_PATH,
    assumptions_path: str | Path = DEFAULT_RAIL_ASSUMPTIONS_PATH,
) -> list[dict[str, str]]:
    """Return exact source-request rows for the current pilot rail leg."""

    station_records = load_rail_station_bindings(station_binding_path)
    station_summary = summarize_rail_station_bindings(station_records)
    assumptions = _load_assumptions(assumptions_path)
    access = _preferred_binding(station_records, point_id="S", preferred_codes=("936",))
    egress = _preferred_binding(station_records, point_id="R", preferred_codes=("814",))
    region_id = access.region_id if access else (station_records[0].region_id if station_records else "")
    station_ready = bool(station_summary["binding_ready"])
    access_name = access.station_name if access else ""
    access_code = access.station_code if access else ""
    egress_name = egress.station_name if egress else ""
    egress_code = egress.station_code if egress else ""
    capacity = assumptions.get("rail_capacity", {}).get("value", "500")

    rows = [
        _row(
            request_id="rail_timetable_headway_request",
            region_id=region_id,
            evidence_fields="headway",
            source_type="public_api_key_required",
            source_name="data.go.kr Seoul Subway train schedule API",
            source_url_or_citation="https://www.data.go.kr/en/data/15143847/openapi.do",
            required_external_input="DATA_GO_KR_KEY; reviewed line, direction, service-day, station-code, and service-window choices",
            access_station_name=access_name,
            access_station_code=access_code,
            egress_station_name=egress_name,
            egress_station_code=egress_code,
            source_cache_path="data/rail/pilot_rail_timetable_cache.csv",
            raw_payload_path="data/rail/pilot_rail_timetable_raw.json",
            fetch_command=_timetable_fetch_command(access_name, access_code),
            derive_command=_headway_derive_command(egress_name, capacity),
            expected_source_status="cached_timetable_derived",
            expected_derived_fields="headway",
            can_close_rail_timing_gate=False,
            publication_use_status=(
                "headway_only; pair with shortest-path, GTFS, or matched timetable travel-time evidence"
            ),
            notes=(
                "This request can create headway evidence after source review. It cannot close travel-time evidence alone."
            ),
        ),
        _row(
            request_id="rail_shortest_path_travel_time_request",
            region_id=region_id,
            evidence_fields="travel_time",
            source_type="public_api_key_required",
            source_name="data.go.kr Seoul Metro shortest-path API",
            source_url_or_citation="https://data.seoul.go.kr/dataList/OA-22724/A/1/datasetView.do",
            required_external_input="DATA_GO_KR_KEY; reviewed station names, station codes, search datetime, and route type",
            access_station_name=access_name,
            access_station_code=access_code,
            egress_station_name=egress_name,
            egress_station_code=egress_code,
            source_cache_path="data/rail/pilot_rail_shortest_path_cache.csv",
            raw_payload_path="data/rail/pilot_rail_shortest_path_raw.json",
            fetch_command=_shortest_path_fetch_command(
                access_name,
                access_code,
                egress_name,
                egress_code,
            ),
            derive_command=_shortest_path_derive_command(capacity),
            expected_source_status="cached_shortest_path_derived",
            expected_derived_fields="travel_time",
            can_close_rail_timing_gate=False,
            publication_use_status=(
                "travel_time_only; pair with timetable or GTFS headway evidence"
            ),
            notes=(
                "This request can create station-to-station travel-time evidence after source review. It cannot close headway evidence alone."
            ),
        ),
        _row(
            request_id="rail_static_gtfs_timing_request",
            region_id=region_id,
            evidence_fields="headway;travel_time",
            source_type="reviewed_static_gtfs_file_required",
            source_name="Reviewed static GTFS feed",
            source_url_or_citation="GTFS source URL or citation to be filled during review",
            required_external_input="reviewed GTFS zip or directory; access_stop_id; egress_stop_id; route_id; service window",
            access_station_name=access_name,
            access_station_code=access_code,
            egress_station_name=egress_name,
            egress_station_code=egress_code,
            source_cache_path="data/rail/pilot_gtfs.zip",
            raw_payload_path="",
            fetch_command="manual reviewed GTFS acquisition; do not synthesize feed rows",
            derive_command=_gtfs_derive_command(capacity),
            expected_source_status="cached_gtfs_derived",
            expected_derived_fields="headway;travel_time",
            can_close_rail_timing_gate=station_ready,
            publication_use_status="candidate full timing source after reviewed feed acquisition",
            notes=(
                "GTFS can close both timing fields if a reviewed feed covers the selected access and egress stops."
            ),
        ),
        _row(
            request_id="rail_capacity_treatment_request",
            region_id=region_id,
            evidence_fields="capacity",
            source_type="operator_or_literature_or_sensitivity_decision",
            source_name="Line capacity source or explicit sensitivity-only treatment",
            source_url_or_citation="data/parameters/rail_assumptions.csv",
            required_external_input="reviewed train capacity source or explicit final sensitivity-only acceptance",
            access_station_name=access_name,
            access_station_code=access_code,
            egress_station_name=egress_name,
            egress_station_code=egress_code,
            source_cache_path="data/parameters/rail_assumptions.csv",
            raw_payload_path="",
            fetch_command="not applicable",
            derive_command="keep capacity as sensitivity-only or replace with reviewed source-backed capacity before final claims",
            expected_source_status="source_backed_or_sensitivity_only",
            expected_derived_fields="capacity",
            can_close_rail_timing_gate=False,
            publication_use_status="capacity treatment only; does not close timing evidence",
            notes="Capacity is currently de-rated and sensitivity-only; this is acceptable only with explicit claim boundaries.",
        ),
        _row(
            request_id="rail_availability_scenario_request",
            region_id=region_id,
            evidence_fields="availability;delay;partial_unavailability",
            source_type="scenario_or_public_disruption_source_required",
            source_name="Rail delay, unavailability, and station-access scenario evidence",
            source_url_or_citation="data/scenarios/disruption_scenarios.csv; docs/rail_evidence.md",
            required_external_input="reviewed scenario rules for rail delay, station access degradation, and partial service unavailability",
            access_station_name=access_name,
            access_station_code=access_code,
            egress_station_name=egress_name,
            egress_station_code=egress_code,
            source_cache_path="data/scenarios/disruption_scenarios.csv",
            raw_payload_path="",
            fetch_command="not applicable",
            derive_command="add or review rail delay/unavailability scenarios before stronger resilience claims",
            expected_source_status="accepted_scenario_or_source_backed_rule",
            expected_derived_fields="availability",
            can_close_rail_timing_gate=False,
            publication_use_status="scenario support only; not timing evidence",
            notes="Rail timing evidence does not certify emergency rail availability.",
        ),
    ]
    return rows


def write_rail_timing_source_request_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_RAIL_TIMING_SOURCE_REQUEST_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_RAIL_TIMING_SOURCE_REQUEST_MANIFEST_PATH,
    station_binding_path: str | Path = DEFAULT_RAIL_STATION_BINDING_PATH,
    assumptions_path: str | Path = DEFAULT_RAIL_ASSUMPTIONS_PATH,
) -> dict[str, Any]:
    """Write rail timing source-request rows and a conservative manifest."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=RAIL_TIMING_SOURCE_REQUEST_COLUMNS,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)

    timing_closure_candidates = [
        row
        for row in rows
        if str(row.get("can_close_rail_timing_gate", "")).lower() == "true"
    ]
    value = {
        "schema_version": 1,
        "result_scope": RAIL_TIMING_SOURCE_REQUEST_SCOPE,
        "inputs": {
            "rail_station_bindings": _display_path(station_binding_path),
            "rail_assumptions": _display_path(assumptions_path),
        },
        "outputs": {
            "rail_timing_source_request_packet": _display_path(output),
            "manifest": _display_path(manifest),
        },
        "row_count": len(rows),
        "source_type_counts": _counts(row["source_type"] for row in rows),
        "evidence_field_counts": _field_counts(row["evidence_fields"] for row in rows),
        "timing_closure_candidate_count": len(timing_closure_candidates),
        "requires_private_or_reviewed_input_count": sum(
            1
            for row in rows
            if row["source_type"]
            in {"public_api_key_required", "reviewed_static_gtfs_file_required"}
        ),
        "publication_ready": False,
        "claim_boundary": (
            "This packet identifies required rail timing sources and commands. "
            "It does not contain cached source observations, derived rail-service "
            "evidence, accepted capacity evidence, or emergency rail availability "
            "evidence."
        ),
        "review_items": [
            "obtain DATA_GO_KR_KEY or a reviewed static GTFS feed before running timing-source fetches",
            "retain raw payloads or reviewed source files with SHA256 digests",
            "derive headway and travel time into rail_service_evidence.csv only after source review",
            "rerun rail evidence, rail review packet, publication-readiness, and final-study-readiness audits after timing evidence changes",
        ],
    }
    with manifest.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return value


def _row(
    *,
    request_id: str,
    region_id: str,
    evidence_fields: str,
    source_type: str,
    source_name: str,
    source_url_or_citation: str,
    required_external_input: str,
    access_station_name: str,
    access_station_code: str,
    egress_station_name: str,
    egress_station_code: str,
    source_cache_path: str,
    raw_payload_path: str,
    fetch_command: str,
    derive_command: str,
    expected_source_status: str,
    expected_derived_fields: str,
    can_close_rail_timing_gate: bool,
    publication_use_status: str,
    notes: str,
) -> dict[str, str]:
    return {
        "request_id": request_id,
        "region_id": region_id,
        "evidence_fields": evidence_fields,
        "source_type": source_type,
        "source_name": source_name,
        "source_url_or_citation": source_url_or_citation,
        "required_external_input": required_external_input,
        "access_station_name": access_station_name,
        "access_station_code": access_station_code,
        "egress_station_name": egress_station_name,
        "egress_station_code": egress_station_code,
        "source_cache_path": source_cache_path,
        "raw_payload_path": raw_payload_path,
        "fetch_command": fetch_command,
        "derive_command": derive_command,
        "expected_source_status": expected_source_status,
        "expected_derived_fields": expected_derived_fields,
        "can_close_rail_timing_gate": str(can_close_rail_timing_gate).lower(),
        "publication_use_status": publication_use_status,
        "claim_boundary": RAIL_TIMING_SOURCE_REQUEST_SCOPE,
        "notes": notes,
    }


def _preferred_binding(
    records: Sequence[RailStationBinding],
    *,
    point_id: str,
    preferred_codes: Sequence[str],
) -> RailStationBinding | None:
    point_records = [
        record for record in records if record.point_id == point_id and record.is_official
    ]
    preferred = [
        record for record in point_records if record.station_code in set(preferred_codes)
    ]
    if preferred:
        return preferred[0]
    if point_records:
        return point_records[0]
    return None


def _load_assumptions(path: str | Path) -> dict[str, dict[str, str]]:
    assumption_path = Path(path)
    if not assumption_path.exists():
        return {}
    with assumption_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return {
            str(row.get("parameter", "")).strip(): {
                str(key): str(value or "").strip()
                for key, value in row.items()
                if key is not None
            }
            for row in reader
            if str(row.get("parameter", "")).strip()
        }


def _timetable_fetch_command(access_name: str, access_code: str) -> str:
    return (
        ".\\.venv\\Scripts\\python scripts\\fetch_rail_timetable_cache.py "
        "--line-name \"9%ED%98%B8%EC%84%A0\" "
        "--upbdnb-se \"%EC%83%81%ED%96%89\" "
        "--wknd-se \"%ED%8F%89%EC%9D%BC\" "
        f"--station-name \"{access_name}\" --station-code {access_code} "
        f"--access-station-name \"{access_name}\" --access-station-code {access_code} "
        "--output data\\rail\\pilot_rail_timetable_cache.csv "
        "--raw-output data\\rail\\pilot_rail_timetable_raw.json"
    )


def _headway_derive_command(egress_name: str, capacity: str) -> str:
    return (
        ".\\.venv\\Scripts\\python scripts\\derive_rail_headway_evidence.py "
        "--input data\\rail\\pilot_rail_timetable_cache.csv "
        "--output data\\parameters\\rail_service_evidence.csv "
        "--evidence-id songpa_public_demo_rail_headway_v1 "
        "--region-id songpa_public_demo --access-point S --egress-point R "
        f"--egress-station-name \"{egress_name}\" "
        "--source-name \"Cached Seoul subway train schedule extract\" "
        "--source-url-or-citation \"https://www.data.go.kr/en/data/15143847/openapi.do\" "
        "--extraction-date REVIEW_DATE --travel-time-min-proxy 20 "
        f"--capacity-pax-per-train {capacity} "
        "--service-window \"reviewed weekday service window\" "
        "--direction \"%EC%83%81%ED%96%89\" --service-day \"%ED%8F%89%EC%9D%BC\" "
        "--station-bindings data\\parameters\\rail_station_bindings.csv"
    )


def _shortest_path_fetch_command(
    access_name: str,
    access_code: str,
    egress_name: str,
    egress_code: str,
) -> str:
    return (
        ".\\.venv\\Scripts\\python scripts\\fetch_rail_shortest_path_cache.py "
        f"--departure-station-name \"{access_name}\" "
        f"--arrival-station-name \"{egress_name}\" "
        "--search-dt \"REVIEW_DATE 09:00:00\" "
        f"--access-station-name \"{access_name}\" --access-station-code {access_code} "
        f"--egress-station-name \"{egress_name}\" --egress-station-code {egress_code} "
        "--output data\\rail\\pilot_rail_shortest_path_cache.csv "
        "--raw-output data\\rail\\pilot_rail_shortest_path_raw.json"
    )


def _shortest_path_derive_command(capacity: str) -> str:
    return (
        ".\\.venv\\Scripts\\python scripts\\derive_rail_shortest_path_evidence.py "
        "--input data\\rail\\pilot_rail_shortest_path_cache.csv "
        "--output data\\parameters\\rail_service_evidence.csv "
        "--evidence-id songpa_public_demo_rail_shortest_path_v1 "
        "--region-id songpa_public_demo --access-point S --egress-point R "
        "--source-name \"Cached Seoul subway shortest-path extract\" "
        "--source-url-or-citation \"https://data.seoul.go.kr/dataList/OA-22724/A/1/datasetView.do\" "
        "--extraction-date REVIEW_DATE --headway-min-proxy 10 "
        f"--capacity-pax-per-train {capacity} "
        "--service-window \"reviewed weekday service window\" "
        "--route-type minimum_time "
        "--station-bindings data\\parameters\\rail_station_bindings.csv"
    )


def _gtfs_derive_command(capacity: str) -> str:
    return (
        ".\\.venv\\Scripts\\python scripts\\derive_rail_gtfs_evidence.py "
        "--input data\\rail\\pilot_gtfs.zip "
        "--output data\\parameters\\rail_service_evidence.csv "
        "--evidence-id songpa_public_demo_rail_gtfs_v1 "
        "--region-id songpa_public_demo --access-point S --egress-point R "
        "--access-stop-id REVIEWED_ACCESS_STOP_ID "
        "--egress-stop-id REVIEWED_EGRESS_STOP_ID "
        "--source-name \"Reviewed static GTFS feed\" "
        "--source-url-or-citation \"GTFS source URL or citation\" "
        "--extraction-date REVIEW_DATE "
        f"--capacity-pax-per-train {capacity} "
        "--service-window \"reviewed weekday service window\" "
        "--route-id REVIEWED_ROUTE_ID"
    )


def _field_counts(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        for token in str(value).replace("|", ";").split(";"):
            key = token.strip()
            if key:
                counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _counts(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _display_path(path: str | Path) -> str:
    value = Path(path)
    try:
        return str(value.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(value)


__all__ = [
    "DEFAULT_RAIL_TIMING_SOURCE_REQUEST_MANIFEST_PATH",
    "DEFAULT_RAIL_TIMING_SOURCE_REQUEST_PACKET_PATH",
    "RAIL_TIMING_SOURCE_REQUEST_COLUMNS",
    "RAIL_TIMING_SOURCE_REQUEST_SCOPE",
    "build_rail_timing_source_request_rows",
    "write_rail_timing_source_request_packet",
]
