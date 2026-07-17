"""Tests for optional Seoul Metro shortest-path API parsing."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.rail_shortest_path import (  # noqa: E402
    load_cached_shortest_path_records,
)
from src.realworld.rail_shortest_path_api import (  # noqa: E402
    shortest_path_api_url,
    shortest_path_record_from_api_payload,
    write_shortest_path_cache,
)


def test_shortest_path_api_url_contains_required_parameters() -> None:
    """URL builder should preserve data.go.kr request parameters."""

    url = shortest_path_api_url(
        service_key="abc%2B123",
        departure_station_name="Olympic Park",
        arrival_station_name="Jamsil",
        search_dt="2026-05-04 09:00:00",
    )

    assert "serviceKey=abc%2B123" in url
    assert "dptreStnNm=Olympic+Park" in url
    assert "arvlStnNm=Jamsil" in url
    assert "searchDt=2026-05-04+09%3A00%3A00" in url
    assert "dataType=JSON" in url

    print("PASS: shortest-path API URL contains required parameters")


def test_parse_nested_shortest_path_payload_to_cache_record() -> None:
    """Parser should convert a nested API payload into the local cache schema."""

    record = shortest_path_record_from_api_payload(
        _payload(),
        route_id="fixture_route",
        access_station_name="Olympic Park",
        access_station_code="936",
        egress_station_name="Jamsil",
        egress_station_code="814",
    )

    assert record.route_id == "fixture_route"
    assert record.travel_time_min == 20.0
    assert record.distance_km == 8.7
    assert record.transfer_count == 1
    assert record.route_type == "minimum_time"

    print("PASS: shortest-path payload parses to cache record")


def test_write_shortest_path_cache_reloads_with_production_validator() -> None:
    """Written API cache rows should satisfy the production cache loader."""

    record = shortest_path_record_from_api_payload(
        _payload(),
        route_id="fixture_route",
        access_station_name="Olympic Park",
        access_station_code="936",
        egress_station_name="Jamsil",
        egress_station_code="814",
    )

    with TemporaryDirectory() as tmp:
        path = write_shortest_path_cache([record], Path(tmp) / "cache.csv")
        loaded = load_cached_shortest_path_records(path)

    assert len(loaded) == 1
    assert loaded[0].travel_time_min == 20.0
    assert loaded[0].distance_km == 8.7

    print("PASS: shortest-path cache reloads with production validator")


def test_missing_route_totals_raise_clear_error() -> None:
    """Payloads without total time and distance should not silently pass."""

    try:
        shortest_path_record_from_api_payload(
            {"response": {"body": {"item": {"paths": []}}}},
            route_id="bad",
            access_station_name="Olympic Park",
            access_station_code="936",
            egress_station_name="Jamsil",
            egress_station_code="814",
        )
    except ValueError as exc:
        assert "total time and distance" in str(exc)
    else:
        raise AssertionError("expected ValueError")

    print("PASS: shortest-path parser rejects missing totals")


def _payload() -> dict[str, object]:
    return {
        "response": {
            "header": {"resultCode": "00"},
            "body": {
                "items": {
                    "item": {
                        "totalDstc": "8700",
                        "totalreqHr": "1200",
                        "paths": [
                            {"trainno": "fixture-1", "trsitYn": "N"},
                            {"trainno": "fixture-2", "trsitYn": "Y"},
                        ],
                    }
                }
            },
        }
    }


if __name__ == "__main__":
    test_shortest_path_api_url_contains_required_parameters()
    test_parse_nested_shortest_path_payload_to_cache_record()
    test_write_shortest_path_cache_reloads_with_production_validator()
    test_missing_route_totals_raise_clear_error()
    print("\n=== REALWORLD RAIL SHORTEST PATH API TESTS PASSED ===")
