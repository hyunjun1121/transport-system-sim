"""Tests for optional data.go.kr train schedule API cache helpers."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.rail_timetable import load_cached_timetable_events  # noqa: E402
from src.realworld.rail_timetable_api import (  # noqa: E402
    timetable_events_from_schedule_payload,
    train_schedule_api_url,
    write_timetable_cache,
)


def assert_raises_value_error(func, expected_message: str) -> None:
    """Assert that a zero-argument function raises ValueError with context."""

    try:
        func()
    except ValueError as exc:
        message = str(exc)
        assert expected_message in message, message
        return
    raise AssertionError("expected ValueError")


def test_train_schedule_api_url_contains_required_parameters() -> None:
    """URL builder should preserve required data.go.kr query parameters."""

    url = train_schedule_api_url(
        service_key="abc%2B123",
        line_name="9호선",
        upbdnb_se="상행",
        wknd_se="평일",
        station_name="올림픽공원",
        station_code="936",
    )

    assert "serviceKey=abc%2B123" in url
    assert "lineNm=" in url
    assert "upbdnbSe=" in url
    assert "wkndSe=" in url
    assert "tmprTmtblYn=N" in url
    assert "stnCd=936" in url

    print("PASS: train schedule API URL contains required parameters")


def test_schedule_payload_parses_to_timetable_events() -> None:
    """Nested API-like payloads should become station-event cache rows."""

    events = timetable_events_from_schedule_payload(
        _payload_fixture(),
        access_station_name="올림픽공원",
        access_station_code="936",
        egress_station_name="잠실",
        egress_station_code="814",
        direction="상행",
        service_day="평일",
    )

    assert len(events) == 6
    assert events[0].trip_id == "9001"
    assert events[0].station_role == "access"
    assert events[0].event_type == "departure"
    assert events[0].event_time_min == 480.0
    assert events[1].station_role == "egress"
    assert events[1].event_type == "arrival"
    assert events[1].event_time_min == 492.0

    print("PASS: train schedule payload parses to timetable events")


def test_schedule_cache_reloads_with_production_validator() -> None:
    """Written timetable cache should be accepted by the offline validator."""

    events = timetable_events_from_schedule_payload(
        _payload_fixture(),
        access_station_name="올림픽공원",
        access_station_code="936",
        egress_station_name="잠실",
        egress_station_code="814",
        direction="상행",
        service_day="평일",
    )
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "pilot_rail_timetable_cache.csv"
        write_timetable_cache(events, path)
        loaded = load_cached_timetable_events(path)

    assert len(loaded) == 6
    assert loaded[0].station_code == "936"

    print("PASS: train schedule cache reloads with production validator")


def test_schedule_parser_rejects_missing_rows() -> None:
    """Payloads without schedule items should fail explicitly."""

    assert_raises_value_error(
        lambda: timetable_events_from_schedule_payload(
            {"response": {"body": {"items": []}}},
            access_station_name="올림픽공원",
            access_station_code="936",
            direction="상행",
            service_day="평일",
        ),
        "does not contain schedule item rows",
    )

    print("PASS: train schedule parser rejects missing rows")


def _payload_fixture() -> dict[str, object]:
    return {
        "response": {
            "body": {
                "items": {
                    "item": [
                        _item("9001", "08:00:00", "08:12:00"),
                        _item("9002", "08:10:00", "08:22:00"),
                        _item("9003", "08:20:00", "08:32:00"),
                    ]
                }
            }
        }
    }


def _item(train_no: str, departure: str, arrival: str) -> dict[str, str]:
    return {
        "trainno": train_no,
        "dptreStnNm": "올림픽공원",
        "dptreStnCd": "936",
        "arvlStnNm": "잠실",
        "arvlStnCd": "814",
        "dptreTm": departure,
        "arvlTm": arrival,
    }


if __name__ == "__main__":
    test_train_schedule_api_url_contains_required_parameters()
    test_schedule_payload_parses_to_timetable_events()
    test_schedule_cache_reloads_with_production_validator()
    test_schedule_parser_rejects_missing_rows()
    print("\n=== REALWORLD RAIL TIMETABLE API TESTS PASSED ===")
