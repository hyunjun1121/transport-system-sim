"""Extract the Songpa-Yangju corridor OSM graph and cache to GraphML.

Run once. If the cache GraphML already exists, this is a no-op.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import yaml

from src.realworld import osm_network


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract corridor OSM graph")
    parser.add_argument(
        "--region",
        type=Path,
        default=ROOT / "data" / "regions" / "songpa_yangju_corridor.yaml",
    )
    parser.add_argument(
        "--cache",
        type=Path,
        default=ROOT / "data" / "cache" / "songpa_yangju_corridor.graphml",
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    if args.cache.exists() and not args.force:
        print(f"Cache exists: {args.cache}")
        return 0

    with args.region.open(encoding="utf-8") as fh:
        region = yaml.safe_load(fh)
    bbox = region["boundary"]
    args.cache.parent.mkdir(parents=True, exist_ok=True)

    graph = osm_network.extract_bbox_graph(
        north=bbox["north"],
        south=bbox["south"],
        east=bbox["east"],
        west=bbox["west"],
        network_type="drive",
    )
    osm_network.save_graphml(graph, args.cache)
    print(
        f"Extracted graph: nodes={graph.number_of_nodes()}, "
        f"edges={graph.number_of_edges()} -> {args.cache}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
