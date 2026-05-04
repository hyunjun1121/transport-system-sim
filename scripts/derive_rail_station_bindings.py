"""Derive rail station bindings from a reviewed cached station extract."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.rail_station_binding import (  # noqa: E402
    load_rail_station_bindings,
    summarize_rail_station_bindings,
)
from src.realworld.rail_station_cache import (  # noqa: E402
    StationBindingDerivationConfig,
    derive_rail_station_bindings_from_cache,
    file_sha256,
    load_cached_station_binding_candidates,
    write_derived_rail_station_bindings,
)


def main() -> int:
    """Write official station bindings from a cached source CSV."""

    args = _parse_args()
    candidates = load_cached_station_binding_candidates(args.input)
    digest = file_sha256(args.input)
    records = derive_rail_station_bindings_from_cache(
        candidates,
        StationBindingDerivationConfig(
            binding_id_prefix=args.binding_id_prefix,
            region_id=args.region_id,
            source_name=args.source_name,
            source_url_or_citation=args.source_url_or_citation,
            source_accessed_date=args.source_accessed_date,
            source_artifact_path=str(Path(args.input)),
            source_artifact_sha256=digest,
        ),
    )
    output_path = write_derived_rail_station_bindings(records, args.output)
    loaded = load_rail_station_bindings(output_path)
    summary = summarize_rail_station_bindings(
        loaded,
        required_points=_split_required_points(args.required_points),
    )
    print(
        f"Wrote {len(loaded)} station binding rows to "
        f"{Path(output_path).resolve().relative_to(ROOT)}"
    )
    print(
        "binding_ready="
        f"{summary['binding_ready']} required_points={summary['required_points']}"
    )
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Cached station source CSV")
    parser.add_argument("--output", required=True, help="Output station binding CSV")
    parser.add_argument("--binding-id-prefix", required=True)
    parser.add_argument("--region-id", required=True)
    parser.add_argument("--source-name", required=True)
    parser.add_argument("--source-url-or-citation", required=True)
    parser.add_argument("--source-accessed-date", required=True)
    parser.add_argument(
        "--required-points",
        default="S,R",
        help="Comma-separated required simulator rail points to summarize",
    )
    return parser.parse_args()


def _split_required_points(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(",") if item.strip())


if __name__ == "__main__":
    raise SystemExit(main())
