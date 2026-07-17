"""Cache the Metro 9 rolling-stock source page for review.

This optional live command writes a raw operator-page snapshot and a one-row
capacity source extract. It does not accept rail capacity or source terms.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.metro9_capacity_source import (  # noqa: E402
    DEFAULT_METRO9_CAPACITY_EXTRACT_PATH,
    DEFAULT_METRO9_CAPACITY_RAW_PATH,
    DEFAULT_METRO9_CAPACITY_URL,
    METRO9_CAPACITY_SOURCE_SCOPE,
    fetch_metro9_capacity_html,
    write_metro9_capacity_cache,
)


def main(argv: list[str] | None = None) -> int:
    """Fetch and cache the Metro 9 source-review extract."""

    args = _parse_args(argv)
    html_text = fetch_metro9_capacity_html(url=args.url, timeout_s=args.timeout_s)
    row = write_metro9_capacity_cache(
        html_text=html_text,
        raw_output_path=args.raw_output,
        extract_output_path=args.extract_output,
        source_url=args.url,
        fetched_at_utc=args.fetched_at_utc or None,
    )
    print(f"wrote_raw: {args.raw_output}")
    print(f"wrote_extract: {args.extract_output}")
    print(f"total_capacity_6_cars: {row['total_capacity_6_cars']}")
    print(f"review_status: {row['review_status']}")
    print(f"claim_scope: {METRO9_CAPACITY_SOURCE_SCOPE}")
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_METRO9_CAPACITY_URL)
    parser.add_argument(
        "--raw-output",
        type=Path,
        default=DEFAULT_METRO9_CAPACITY_RAW_PATH,
    )
    parser.add_argument(
        "--extract-output",
        type=Path,
        default=DEFAULT_METRO9_CAPACITY_EXTRACT_PATH,
    )
    parser.add_argument(
        "--fetched-at-utc",
        default="",
        help="Optional fixed timestamp for deterministic fixture runs.",
    )
    parser.add_argument("--timeout-s", type=float, default=30.0)
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
