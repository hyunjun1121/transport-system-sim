"""Optional fetch and parse helpers for the data.go.kr Seoul train schedule API.

Default validation remains offline. These helpers separate live API access from
deterministic payload parsing and cache writing so tests can validate behavior
without contacting public services.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen

from src.realworld.rail_timetable import (
    REQUIRED_TIMETABLE_COLUMNS,
    RailTimetableEvent,
)


DEFAULT_TRAIN_SCHEDULE_ENDPOINT = "https://apis.data.go.kr/B553766/schedule/getTrainSch"

TRIP_ID_KEYS: tuple[str, ...] = (
    "trainno",
    "trainnumber",
    "lnkgtrainno",
)
DEPARTURE_TIME_KEYS: tuple[str, ...] = (
    "dptretm",
    "dptrehr",
    "dptretime",
    "departuretime",
)
ARRIVAL_TIME_KEYS: tuple[str, ...] = (
    "arvltm",
    "arvlhr",
    "arvltime",
    "arrivaltime",
)
DEPARTURE_STATION_NAME_KEYS: tuple[str, ...] = (
    "dptrestnnm",
    "departurestationname",
)
DEPARTURE_STATION_CODE_KEYS: tuple[str, ...] = (
    "dptrestncd",
    "departurestationcode",
)
ARRIVAL_STATION_NAME_KEYS: tuple[str, ...] = (
    "arvlstnnm",
    "arrivalstationname",
)
ARRIVAL_STATION_CODE_KEYS: tuple[str, ...] = (
    "arvlstncd",
    "arrivalstationcode",
)


def train_schedule_api_url(
    *,
    service_key: str,
    line_name: str,
    upbdnb_se: str,
    wknd_se: str,
    temporary_timetable_yn: str = "N",
    data_type: str = "JSON",
    page_no: int = 1,
    num_of_rows: int = 100,
    station_name: str = "",
    station_code: str = "",
    departure_station_name: str = "",
    departure_station_code: str = "",
    arrival_station_name: str = "",
    arrival_station_code: str = "",
    search_dt: str = "",
    train_no: str = "",
    endpoint: str = DEFAULT_TRAIN_SCHEDULE_ENDPOINT,
) -> str:
    """Return the data.go.kr train schedule API URL."""

    if page_no <= 0:
        raise ValueError("page_no must be positive")
    if num_of_rows <= 0:
        raise ValueError("num_of_rows must be positive")
    params: dict[str, str | int] = {
        "serviceKey": _require_text(service_key, "service_key"),
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "dataType": _require_text(data_type, "data_type"),
        "tmprTmtblYn": _require_text(
            temporary_timetable_yn,
            "temporary_timetable_yn",
        ),
        "upbdnbSe": _require_text(upbdnb_se, "upbdnb_se"),
        "wkndSe": _require_text(wknd_se, "wknd_se"),
        "lineNm": _require_text(line_name, "line_name"),
    }
    optional = {
        "stnNm": station_name,
        "stnCd": station_code,
        "dptreStnNm": departure_station_name,
        "dptreStnCd": departure_station_code,
        "arvlStnNm": arrival_station_name,
        "arvlStnCd": arrival_station_code,
        "searchDt": search_dt,
        "trainno": train_no,
    }
    for key, value in optional.items():
        text = str(value or "").strip()
        if text:
            params[key] = text
    return f"{endpoint}?{urlencode(params, safe='%')}"


def fetch_train_schedule_payload(
    *,
    service_key: str,
    line_name: str,
    upbdnb_se: str,
    wknd_se: str,
    temporary_timetable_yn: str = "N",
    data_type: str = "JSON",
    page_no: int = 1,
    num_of_rows: int = 100,
    station_name: str = "",
    station_code: str = "",
    departure_station_name: str = "",
    departure_station_code: str = "",
    arrival_station_name: str = "",
    arrival_station_code: str = "",
    search_dt: str = "",
    train_no: str = "",
    endpoint: str = DEFAULT_TRAIN_SCHEDULE_ENDPOINT,
    timeout_s: float = 30.0,
) -> dict[str, Any]:
    """Fetch one train schedule API payload.

    This function is intentionally not used by default tests.
    """

    url = train_schedule_api_url(
        service_key=service_key,
        line_name=line_name,
        upbdnb_se=upbdnb_se,
        wknd_se=wknd_se,
        temporary_timetable_yn=temporary_timetable_yn,
        data_type=data_type,
        page_no=page_no,
        num_of_rows=num_of_rows,
        station_name=station_name,
        station_code=station_code,
        departure_station_name=departure_station_name,
        departure_station_code=departure_station_code,
        arrival_station_name=arrival_station_name,
        arrival_station_code=arrival_station_code,
        search_dt=search_dt,
        train_no=train_no,
        endpoint=endpoint,
    )
    with urlopen(url, timeout=timeout_s) as response:  # nosec B310: opt-in public API fetch
        text = response.read().decode("utf-8-sig")
    payload = json.loads(text)
    if not isinstance(payload, dict):
        raise ValueError("train schedule API response must be a JSON object")
    return payload


def timetable_events_from_schedule_payload(
    payload: dict[str, Any],
    *,
    access_station_name: str,
    access_station_code: str,
    egress_station_name: str = "",
    egress_station_code: str = "",
    direction: str,
    service_day: str,
) -> list[RailTimetableEvent]:
    """Convert a train schedule API payload into local station-event rows."""

    events: list[RailTimetableEvent] = []
    for index, item in enumerate(_schedule_items(payload), start=1):
        normalized = {_normalize_key(key): value for key, value in item.items()}
        trip_id = _first_text(normalized, TRIP_ID_KEYS) or f"schedule_row_{index}"

        departure_time = _first_text(normalized, DEPARTURE_TIME_KEYS)
        if departure_time:
            events.append(
                RailTimetableEvent(
                    trip_id=trip_id,
                    station_role="access",
                    station_name=(
                        _first_text(normalized, DEPARTURE_STATION_NAME_KEYS)
                        or _require_text(access_station_name, "access_station_name")
                    ),
                    station_code=(
                        _first_text(normalized, DEPARTURE_STATION_CODE_KEYS)
                        or _require_text(access_station_code, "access_station_code")
                    ),
                    event_time_min=_parse_api_time_min(departure_time),
                    event_type="departure",
                    direction=_require_text(direction, "direction"),
                    service_day=_require_text(service_day, "service_day"),
                )
            )

        arrival_time = _first_text(normalized, ARRIVAL_TIME_KEYS)
        if arrival_time and (egress_station_name or egress_station_code):
            events.append(
                RailTimetableEvent(
                    trip_id=trip_id,
                    station_role="egress",
                    station_name=(
                        _first_text(normalized, ARRIVAL_STATION_NAME_KEYS)
                        or _require_text(egress_station_name, "egress_station_name")
                    ),
                    station_code=(
                        _first_text(normalized, ARRIVAL_STATION_CODE_KEYS)
                        or _require_text(egress_station_code, "egress_station_code")
                    ),
                    event_time_min=_parse_api_time_min(arrival_time),
                    event_type="arrival",
                    direction=_require_text(direction, "direction"),
                    service_day=_require_text(service_day, "service_day"),
                )
            )

    if not events:
        raise ValueError("train schedule API payload did not contain timetable events")
    return events


def write_timetable_cache(
    events: list[RailTimetableEvent],
    path: str | Path,
) -> Path:
    """Write local timetable cache rows."""

    if not events:
        raise ValueError("at least one timetable event is required")
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_TIMETABLE_COLUMNS)
        writer.writeheader()
        for event in events:
            writer.writerow(_event_row(event))
    return output_path


def _schedule_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for value in _walk(payload):
        if not isinstance(value, dict):
            continue
        normalized = {_normalize_key(key): item for key, item in value.items()}
        has_trip = any(key in normalized for key in TRIP_ID_KEYS)
        has_time = any(
            key in normalized for key in (*DEPARTURE_TIME_KEYS, *ARRIVAL_TIME_KEYS)
        )
        if has_trip and has_time:
            items.append(value)
    if not items:
        raise ValueError("train schedule API payload does not contain schedule item rows")
    return items


def _walk(value: Any):
    yield value
    if isinstance(value, dict):
        for item in value.values():
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)


def _event_row(event: RailTimetableEvent) -> dict[str, object]:
    return {
        "trip_id": event.trip_id,
        "station_role": event.station_role,
        "station_name": event.station_name,
        "station_code": event.station_code,
        "event_time": _format_service_time(event.event_time_min),
        "event_type": event.event_type,
        "direction": event.direction,
        "service_day": event.service_day,
    }


def _parse_api_time_min(value: str) -> float:
    text = _require_text(value, "event_time")
    if ":" in text:
        parts = [part.strip() for part in text.split(":")]
        if len(parts) not in (2, 3):
            raise ValueError(f"invalid API time {value!r}")
        try:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2]) if len(parts) == 3 else 0
        except ValueError as exc:
            raise ValueError(f"invalid API time {value!r}") from exc
    else:
        digits = "".join(ch for ch in text if ch.isdigit())
        if len(digits) not in (4, 6):
            raise ValueError(f"invalid compact API time {value!r}")
        hours = int(digits[:2])
        minutes = int(digits[2:4])
        seconds = int(digits[4:6]) if len(digits) == 6 else 0
    if hours < 0 or not 0 <= minutes < 60 or not 0 <= seconds < 60:
        raise ValueError(f"invalid API time {value!r}")
    return hours * 60.0 + minutes + seconds / 60.0


def _format_service_time(event_time_min: float) -> str:
    total_seconds = int(round(event_time_min * 60.0))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def _first_text(normalized: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = normalized.get(key)
        text = str(value or "").strip()
        if text:
            return text
    return ""


def _normalize_key(value: object) -> str:
    return str(value).replace("_", "").replace("-", "").strip().lower()


def _require_text(value: str, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field_name} must be non-empty")
    return text


__all__ = [
    "DEFAULT_TRAIN_SCHEDULE_ENDPOINT",
    "fetch_train_schedule_payload",
    "timetable_events_from_schedule_payload",
    "train_schedule_api_url",
    "write_timetable_cache",
]
