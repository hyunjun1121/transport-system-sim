"""Fetch a reviewed data.go.kr Seoul train schedule payload into local cache."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.rail_timetable import load_cached_timetable_events  # noqa: E402
from src.realworld.rail_timetable_api import (  # noqa: E402
    fetch_train_schedule_payload,
    timetable_events_from_schedule_payload,
    write_timetable_cache,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "rail" / "pilot_rail_timetable_cache.csv"


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    service_key = args.service_key or os.environ.get("DATA_GO_KR_KEY", "")
    if not service_key:
        print("DATA_GO_KR_KEY or --service-key is required for live fetch")
        return 2

    payload = fetch_train_schedule_payload(
        service_key=service_key,
        line_name=args.line_name,
        upbdnb_se=args.upbdnb_se,
        wknd_se=args.wknd_se,
        temporary_timetable_yn=args.temporary_timetable_yn,
        data_type=args.data_type,
        page_no=args.page_no,
        num_of_rows=args.num_of_rows,
        station_name=args.station_name,
        station_code=args.station_code,
        departure_station_name=args.departure_station_name,
        departure_station_code=args.departure_station_code,
        arrival_station_name=args.arrival_station_name,
        arrival_station_code=args.arrival_station_code,
        search_dt=args.search_dt,
        train_no=args.train_no,
        timeout_s=args.timeout_s,
    )
    if args.raw_output:
        raw_path = Path(args.raw_output)
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    events = timetable_events_from_schedule_payload(
        payload,
        access_station_name=args.access_station_name,
        access_station_code=args.access_station_code,
        egress_station_name=args.egress_station_name,
        egress_station_code=args.egress_station_code,
        direction=args.cache_direction or args.upbdnb_se,
        service_day=args.cache_service_day or args.wknd_se,
    )
    output_path = write_timetable_cache(events, args.output)
    # Re-load through the production validator so this script fails on schema drift.
    load_cached_timetable_events(output_path)
    print(f"wrote {output_path}")
    print(f"event_count: {len(events)}")
    print("claim_scope: local timetable cache only; review before evidence derivation")
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch the data.go.kr Seoul train schedule API into the local "
            "station-event timetable cache schema. This is an optional live "
            "command and is not part of default validation."
        )
    )
    parser.add_argument("--service-key", default="")
    parser.add_argument("--line-name", required=True)
    parser.add_argument("--upbdnb-se", required=True)
    parser.add_argument("--wknd-se", required=True)
    parser.add_argument("--temporary-timetable-yn", default="N")
    parser.add_argument("--data-type", default="JSON")
    parser.add_argument("--page-no", type=int, default=1)
    parser.add_argument("--num-of-rows", type=int, default=100)
    parser.add_argument("--station-name", default="")
    parser.add_argument("--station-code", default="")
    parser.add_argument("--departure-station-name", default="")
    parser.add_argument("--departure-station-code", default="")
    parser.add_argument("--arrival-station-name", default="")
    parser.add_argument("--arrival-station-code", default="")
    parser.add_argument("--search-dt", default="")
    parser.add_argument("--train-no", default="")
    parser.add_argument("--access-station-name", required=True)
    parser.add_argument("--access-station-code", required=True)
    parser.add_argument("--egress-station-name", default="")
    parser.add_argument("--egress-station-code", default="")
    parser.add_argument("--cache-direction", default="")
    parser.add_argument("--cache-service-day", default="")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--raw-output", default="")
    parser.add_argument("--timeout-s", type=float, default=30.0)
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
