"""Audit rail-point station bindings without upgrading rail claims."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.rail_station_binding import (  # noqa: E402
    DEFAULT_RAIL_STATION_BINDING_PATH,
    load_rail_station_bindings,
    summarize_rail_station_bindings,
)


def main() -> int:
    """Print a JSON station-binding audit and fail only on invalid schema."""

    records = load_rail_station_bindings(DEFAULT_RAIL_STATION_BINDING_PATH)
    summary = summarize_rail_station_bindings(records)
    summary["path"] = str(DEFAULT_RAIL_STATION_BINDING_PATH.relative_to(ROOT))
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
