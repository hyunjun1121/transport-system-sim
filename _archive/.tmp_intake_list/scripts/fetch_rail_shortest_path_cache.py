"""Fetch a reviewed Seoul Metro shortest-path API response into a local cache.

This is an optional live-data command. It is not used by default tests and it
requires a data.go.kr service key.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.rail_shortest_path import (  # noqa: E402
    load_cached_shortest_path_records,
)
from src.realworld.rail_shortest_path_api import (  # noqa: E402
    DEFAULT_SHORTEST_PATH_ENDPOINT,
    fetch_shortest_path_payload,
    shortest_path_record_from_api_payload,
    write_shortest_path_cache,
)


def main(argv: list[str] | None = None) -> int:
    """Run the optional live shortest-path cache fetch."""

    args = _parse_args(argv)
    service_key = args.service_key or os.environ.get(args.service_key_env, "")
    if not service_key:
        print(
            f"Missing data.go.kr service key. Set {args.service_key_env} or pass --service-key.",
            file=sys.stderr,
        )
        return 2

    payload = fetch_shortest_path_payload(
        service_key=service_key,
        departure_station_name=args.departure_station_name,
        arrival_station_name=args.arrival_station_name,
        search_dt=args.search_dt,
        search_type=args.search_type,
        schedule_include=args.schedule_include,
        endpoint=args.endpoint,
        timeout_s=args.timeout_s,
    )
    if args.raw_output:
        raw_path = Path(args.raw_output)
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    record = shortest_path_record_from_api_payload(
        payload,
        route_id=args.route_id,
        access_station_name=args.access_station_name,
        access_station_code=args.access_station_code,
        egress_station_name=args.egress_station_name,
        egress_station_code=args.egress_station_code,
        route_type=args.route_type,
    )
    output_path = write_shortest_path_cache([record], args.output)
    # Re-load through the production validator so this command fails on schema drift.
    load_cached_shortest_path_records(output_path)
    print(f"wrote {output_path}")
    print("source_status candidate: cached_shortest_path_derived")
    print(
        "next: run scripts\\derive_rail_shortest_path_evidence.py to convert "
        "this cache into rail_service_evidence.csv"
    )
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--service-key-env",
        default="DATA_GO_KR_KEY",
        help="Environment variable that stores the data.go.kr service key.",
    )
    parser.add_argument(
        "--service-key",
        default="",
        help="Optional data.go.kr service key. Prefer the environment variable.",
    )
    parser.add_argument(
        "--endpoint",
        default=DEFAULT_SHORTEST_PATH_ENDPOINT,
        help="Shortest-path API endpoint.",
    )
    parser.add_argument(
        "--output",
        default="data\\rail\\pilot_rail_shortest_path_cache.csv",
        help="Local shortest-path cache CSV path.",
    )
    parser.add_argument(
        "--raw-output",
        default="",
        help="Optional raw JSON payload path for source review.",
    )
    parser.add_argument("--departure-station-name", required=True)
    parser.add_argument("--arrival-station-name", required=True)
    parser.add_argument("--search-dt", required=True)
    parser.add_argument("--search-type", default="duration")
    parser.add_argument("--schedule-include", default="N")
    parser.add_argument("--route-id", default="songpa_public_demo_minimum_time")
    parser.add_argument("--route-type", default="minimum_time")
    parser.add_argument("--access-station-name", required=True)
    parser.add_argument("--access-station-code", required=True)
    parser.add_argument("--egress-station-name", required=True)
    parser.add_argument("--egress-station-code", required=True)
    parser.add_argument("--timeout-s", type=float, default=30.0)
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
