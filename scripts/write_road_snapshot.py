"""Write region-level road-network snapshot review artifacts.

The command is non-destructive by default. It writes a timestamped output
directory containing GraphML, node table, edge table, connector audit, and a
manifest. The outputs are review support only and do not create formal
acceptance records.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.osm_network import extract_bbox_graph, load_graphml
from src.realworld.regions import load_region_spec
from src.realworld.road_snapshot import (
    DEFAULT_ROAD_SNAPSHOT_ROOT,
    snapshot_id_for_region,
    write_road_snapshot_artifacts,
)


DEFAULT_REGION_PATH = ROOT / "data" / "regions" / "pilot_region.yaml"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region-id", required=True)
    parser.add_argument("--region-path", default=str(DEFAULT_REGION_PATH))
    parser.add_argument(
        "--source",
        choices=("cached", "live-osmnx"),
        default="cached",
        help="Use cached GraphML by default; live extraction requires optional OSMnx.",
    )
    parser.add_argument(
        "--source-graph",
        default="",
        help="Cached GraphML path. Defaults to region metadata cache_path.",
    )
    parser.add_argument("--output-root", default=str(DEFAULT_ROAD_SNAPSHOT_ROOT))
    parser.add_argument(
        "--output-dir",
        default="",
        help="Explicit output directory; otherwise a timestamped directory is used.",
    )
    parser.add_argument(
        "--created-utc",
        default="",
        help="Optional ISO timestamp for deterministic reruns/tests.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting a non-empty explicit output directory.",
    )
    args = parser.parse_args()

    region_path = Path(args.region_path)
    region = load_region_spec(_load_yaml(region_path))
    if region.region_id != args.region_id:
        raise SystemExit(
            f"region-id mismatch: requested {args.region_id!r}, "
            f"loaded {region.region_id!r} from {region_path}"
        )

    created_utc = args.created_utc or datetime.now(timezone.utc).replace(
        microsecond=0
    ).isoformat()
    output_dir = (
        Path(args.output_dir)
        if args.output_dir
        else Path(args.output_root) / snapshot_id_for_region(region.region_id, created_utc)
    )

    source_graph_path: Path | None = None
    if args.source == "cached":
        source_graph_path = Path(args.source_graph or _region_cache_path(region))
        graph = load_graphml(source_graph_path, normalize=True)
        source_type = "cached_graphml"
    else:
        boundary = region.boundary
        graph = extract_bbox_graph(
            north=boundary.north,
            south=boundary.south,
            east=boundary.east,
            west=boundary.west,
            normalize=True,
        )
        source_type = "live_osmnx_bbox"

    manifest = write_road_snapshot_artifacts(
        region=region,
        graph=graph,
        output_dir=output_dir,
        region_path=region_path,
        source_graph_path=source_graph_path,
        source_type=source_type,
        overwrite=args.overwrite,
        created_utc=created_utc,
    )

    print(manifest["outputs"]["manifest"]["path"])


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def _region_cache_path(region: Any) -> str:
    metadata = getattr(region, "metadata", {}) or {}
    cache_path = metadata.get("cache_path")
    if not cache_path:
        raise ValueError(
            "Cached road snapshot source requires --source-graph or "
            "region.metadata.cache_path"
        )
    return str(cache_path)


if __name__ == "__main__":
    main()
