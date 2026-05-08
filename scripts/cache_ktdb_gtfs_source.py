"""Cache public KTDB GTFS source metadata for reviewer inspection."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.ktdb_gtfs_source import (  # noqa: E402
    DEFAULT_KTDB_GTFS_EXTRACT_PATH,
    DEFAULT_KTDB_GTFS_LIST_RAW_PATH,
    DEFAULT_KTDB_GTFS_LIST_URL,
    DEFAULT_KTDB_GTFS_NOTICE_RAW_PATH,
    DEFAULT_KTDB_GTFS_NOTICE_URL,
    fetch_ktdb_gtfs_html,
    write_ktdb_gtfs_cache,
)


def main(argv: list[str] | None = None) -> int:
    """Fetch KTDB public pages and write raw HTML plus extract CSV."""

    args = _parse_args(argv)
    try:
        notice_html, list_html = fetch_ktdb_gtfs_html(
            notice_url=args.notice_url,
            list_url=args.list_url,
            timeout_s=args.timeout_s,
        )
    except OSError as exc:
        print(
            f"failed to fetch KTDB GTFS source metadata: {exc}",
            file=sys.stderr,
        )
        print(
            "claim_scope: no source metadata cache was written; target GTFS "
            "cache remains absent",
            file=sys.stderr,
        )
        return 1
    row = write_ktdb_gtfs_cache(
        notice_html=notice_html,
        list_html=list_html,
        notice_raw_output_path=args.notice_raw_output,
        list_raw_output_path=args.list_raw_output,
        extract_output_path=args.extract_output,
        notice_url=args.notice_url,
        list_url=args.list_url,
    )
    print(f"wrote {args.notice_raw_output}")
    print(f"wrote {args.list_raw_output}")
    print(f"wrote {args.extract_output}")
    print(f"dataset_code: {row['dataset_code']}")
    print(f"years_available: {row['years_available']}")
    print(f"review_status: {row['review_status']}")
    print(
        "claim_scope: source metadata only; not a GTFS feed cache and not rail evidence"
    )
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--notice-url",
        default=DEFAULT_KTDB_GTFS_NOTICE_URL,
        help="KTDB GTFS notice URL.",
    )
    parser.add_argument(
        "--list-url",
        default=DEFAULT_KTDB_GTFS_LIST_URL,
        help="KTDB public data-list URL.",
    )
    parser.add_argument(
        "--notice-raw-output",
        type=Path,
        default=DEFAULT_KTDB_GTFS_NOTICE_RAW_PATH,
        help="Raw notice HTML output path.",
    )
    parser.add_argument(
        "--list-raw-output",
        type=Path,
        default=DEFAULT_KTDB_GTFS_LIST_RAW_PATH,
        help="Raw data-list HTML output path.",
    )
    parser.add_argument(
        "--extract-output",
        type=Path,
        default=DEFAULT_KTDB_GTFS_EXTRACT_PATH,
        help="Source metadata extract CSV output path.",
    )
    parser.add_argument("--timeout-s", type=float, default=30.0)
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
