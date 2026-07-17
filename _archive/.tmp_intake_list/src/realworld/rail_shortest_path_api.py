"""Optional fetch and parse helpers for the Seoul Metro shortest-path API.

The default validation path must remain offline. These helpers therefore
separate live API access from deterministic parsing and CSV writing so tests
can exercise response handling without contacting public services.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen

from src.realworld.rail_shortest_path import (
    REQUIRED_SHORTEST_PATH_COLUMNS,
    RailShortestPathRecord,
)


DEFAULT_SHORTEST_PATH_ENDPOINT = "https://apis.data.go.kr/B553766/path/getShtrmPath"

TIME_KEYS_SECONDS: tuple[str, ...] = (
    "totalreqhr",
    "totalreqtime",
    "totaltime",
    "reqhr",
)
TIME_KEYS_MINUTES: tuple[str, ...] = (
    "traveltimemin",
    "time_min",
    "durationmin",
)
DISTANCE_KEYS_METERS: tuple[str, ...] = (
    "totaldstc",
    "totaldstnc",
    "totaldistance",
    "distance",
)
DISTANCE_KEYS_KM: tuple[str, ...] = (
    "distancekm",
    "distance_km",
)
TRANSFER_KEYS: tuple[str, ...] = (
    "transfercount",
    "transfercnt",
    "trsitcnt",
    "trnsitcnt",
    "transfrcnt",
)


def shortest_path_api_url(
    *,
    service_key: str,
    departure_station_name: str,
    arrival_station_name: str,
    search_dt: str,
    search_type: str = "duration",
    data_type: str = "JSON",
    schedule_include: str = "N",
    endpoint: str = DEFAULT_SHORTEST_PATH_ENDPOINT,
) -> str:
    """Return the data.go.kr shortest-path API URL."""

    params = {
        "serviceKey": _require_text(service_key, "service_key"),
        "dataType": _require_text(data_type, "data_type"),
        "dptreStnNm": _require_text(
            departure_station_name,
            "departure_station_name",
        ),
        "arvlStnNm": _require_text(arrival_station_name, "arrival_station_name"),
        "searchDt": _require_text(search_dt, "search_dt"),
        "searchType": _require_text(search_type, "search_type"),
        "schInclYn": _require_text(schedule_include, "schedule_include"),
    }
    return f"{endpoint}?{urlencode(params, safe='%')}"


def fetch_shortest_path_payload(
    *,
    service_key: str,
    departure_station_name: str,
    arrival_station_name: str,
    search_dt: str,
    search_type: str = "duration",
    data_type: str = "JSON",
    schedule_include: str = "N",
    endpoint: str = DEFAULT_SHORTEST_PATH_ENDPOINT,
    timeout_s: float = 30.0,
) -> dict[str, Any]:
    """Fetch one shortest-path API payload.

    This function is intentionally not used by default tests.
    """

    url = shortest_path_api_url(
        service_key=service_key,
        departure_station_name=departure_station_name,
        arrival_station_name=arrival_station_name,
        search_dt=search_dt,
        search_type=search_type,
        data_type=data_type,
        schedule_include=schedule_include,
        endpoint=endpoint,
    )
    with urlopen(url, timeout=timeout_s) as response:  # nosec B310: opt-in public API fetch
        text = response.read().decode("utf-8-sig")
    payload = json.loads(text)
    if not isinstance(payload, dict):
        raise ValueError("shortest-path API response must be a JSON object")
    return payload


def shortest_path_record_from_api_payload(
    payload: dict[str, Any],
    *,
    route_id: str,
    access_station_name: str,
    access_station_code: str,
    egress_station_name: str,
    egress_station_code: str,
    route_type: str = "minimum_time",
) -> RailShortestPathRecord:
    """Convert a data.go.kr shortest-path payload to the local cache schema."""

    candidate = _find_route_candidate(payload)
    travel_time_min = _extract_travel_time_min(candidate)
    distance_km = _extract_distance_km(candidate)
    transfer_count = _extract_transfer_count(candidate)
    return RailShortestPathRecord(
        route_id=_require_text(route_id, "route_id"),
        access_station_name=_require_text(access_station_name, "access_station_name"),
        access_station_code=_require_text(access_station_code, "access_station_code"),
        egress_station_name=_require_text(egress_station_name, "egress_station_name"),
        egress_station_code=_require_text(egress_station_code, "egress_station_code"),
        travel_time_min=travel_time_min,
        distance_km=distance_km,
        transfer_count=transfer_count,
        route_type=_require_text(route_type, "route_type"),
    )


def write_shortest_path_cache(
    records: list[RailShortestPathRecord],
    path: str | Path,
) -> Path:
    """Write local shortest-path cache rows."""

    if not records:
        raise ValueError("at least one shortest-path record is required")
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_SHORTEST_PATH_COLUMNS)
        writer.writeheader()
        for record in records:
            writer.writerow(_record_row(record))
    return output_path


def _find_route_candidate(payload: dict[str, Any]) -> dict[str, Any]:
    route_like: list[dict[str, Any]] = []
    for value in _walk(payload):
        if not isinstance(value, dict):
            continue
        normalized = {_normalize_key(key): item for key, item in value.items()}
        has_time = any(key in normalized for key in (*TIME_KEYS_SECONDS, *TIME_KEYS_MINUTES))
        has_distance = any(
            key in normalized for key in (*DISTANCE_KEYS_METERS, *DISTANCE_KEYS_KM)
        )
        if has_time and has_distance:
            route_like.append(value)
    if not route_like:
        raise ValueError(
            "shortest-path API payload does not contain route-level total "
            "time and distance fields"
        )
    return route_like[0]


def _walk(value: Any):
    yield value
    if isinstance(value, dict):
        for item in value.values():
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)


def _extract_travel_time_min(candidate: dict[str, Any]) -> float:
    normalized = {_normalize_key(key): value for key, value in candidate.items()}
    for key in TIME_KEYS_MINUTES:
        if key in normalized:
            return _positive_float(normalized[key], key)
    for key in TIME_KEYS_SECONDS:
        if key in normalized:
            return _positive_float(normalized[key], key) / 60.0
    raise ValueError("route candidate is missing total travel-time field")


def _extract_distance_km(candidate: dict[str, Any]) -> float:
    normalized = {_normalize_key(key): value for key, value in candidate.items()}
    for key in DISTANCE_KEYS_KM:
        if key in normalized:
            return _positive_float(normalized[key], key)
    for key in DISTANCE_KEYS_METERS:
        if key in normalized:
            return _positive_float(normalized[key], key) / 1000.0
    raise ValueError("route candidate is missing total distance field")


def _extract_transfer_count(candidate: dict[str, Any]) -> int:
    normalized = {_normalize_key(key): value for key, value in candidate.items()}
    for key in TRANSFER_KEYS:
        if key in normalized:
            return _non_negative_int(normalized[key], key)
    paths = normalized.get("paths")
    if isinstance(paths, list):
        return sum(
            1
            for path in paths
            if isinstance(path, dict)
            and str(path.get("trsitYn", path.get("transitYn", ""))).strip().upper()
            in {"Y", "1", "TRUE"}
        )
    return 0


def _record_row(record: RailShortestPathRecord) -> dict[str, object]:
    return {
        "route_id": record.route_id,
        "access_station_name": record.access_station_name,
        "access_station_code": record.access_station_code,
        "egress_station_name": record.egress_station_name,
        "egress_station_code": record.egress_station_code,
        "travel_time_min": _format_number(record.travel_time_min),
        "distance_km": _format_number(record.distance_km),
        "transfer_count": record.transfer_count,
        "route_type": record.route_type,
    }


def _normalize_key(value: object) -> str:
    return str(value).replace("_", "").replace("-", "").strip().lower()


def _require_text(value: str, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field_name} must be non-empty")
    return text


def _positive_float(value: Any, field_name: str) -> float:
    try:
        parsed = float(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be numeric, got {value!r}") from exc
    if parsed <= 0.0:
        raise ValueError(f"{field_name} must be positive, got {value!r}")
    return parsed


def _non_negative_int(value: Any, field_name: str) -> int:
    try:
        parsed = int(float(str(value).strip()))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be an integer, got {value!r}") from exc
    if parsed < 0:
        raise ValueError(f"{field_name} must be non-negative, got {value!r}")
    return parsed


def _format_number(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.3f}".rstrip("0").rstrip(".")


__all__ = [
    "DEFAULT_SHORTEST_PATH_ENDPOINT",
    "fetch_shortest_path_payload",
    "shortest_path_api_url",
    "shortest_path_record_from_api_payload",
    "write_shortest_path_cache",
]
