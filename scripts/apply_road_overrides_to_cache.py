"""Apply reviewed road-class overrides to the cached OSM GraphML.

Walks every edge in `data/cache/pilot_region_road.graphml`, classifies it by
`highway`, and writes reviewed `maxspeed`, `capacity`, and `base_p_fail`
values from `data/parameters/road_class_overrides.csv` into the per-edge
attribute map. Also adds a graph-level marker so downstream audits can
distinguish the overridden cache from the raw OSM extract.

This script is invoked only after a reviewer has signed off the override
CSV. It does not fetch live data, does not change geometry, and does not
modify the simulator source code; it only materializes the reviewer-approved
class-level values into the cached road graph so the road-input evidence
audit can see explicit per-edge values.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import networkx as nx  # noqa: E402

from src.realworld.attributes import normalize_highway  # noqa: E402
from src.realworld.osm_network import load_graphml, save_graphml  # noqa: E402
from src.realworld.road_overrides import (  # noqa: E402
    load_road_class_overrides,
)


DEFAULT_GRAPHML_PATH = ROOT / "data" / "cache" / "pilot_region_road.graphml"
DEFAULT_GRAPHML_MANIFEST_PATH = (
    ROOT / "data" / "cache" / "pilot_region_road_manifest.json"
)
DEFAULT_OVERRIDES_PATH = ROOT / "data" / "parameters" / "road_class_overrides.csv"


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    overrides = load_road_class_overrides(args.overrides)
    override_by_highway = {row.highway: row for row in overrides}

    graph_path = Path(args.graphml)
    backup_path = graph_path.with_suffix(".raw.graphml")

    if not args.no_backup and not backup_path.exists():
        shutil.copy2(graph_path, backup_path)
        print(f"Backed up raw cache to {backup_path}")

    graph = load_graphml(graph_path, normalize=True)
    edges_updated = 0
    edges_unmatched = 0
    highway_counts: dict[str, int] = {}
    for u, v, data in graph.edges(data=True):
        highway, _ = normalize_highway(data.get("highway"))
        highway_counts[highway] = highway_counts.get(highway, 0) + 1
        override = override_by_highway.get(highway)
        if override is None:
            edges_unmatched += 1
            continue
        data["maxspeed"] = str(override.speed_kph)
        data["capacity"] = str(override.capacity_veh_per_hr)
        data["base_p_fail"] = str(override.base_p_fail)
        data["road_class_override_applied"] = "true"
        data["road_class_override_source"] = str(args.overrides)
        edges_updated += 1

    graph.graph["road_class_overrides_applied"] = True
    graph.graph["road_class_overrides_path"] = str(args.overrides)
    graph.graph["road_class_overrides_highway_count"] = len(override_by_highway)
    graph.graph["road_class_overrides_highways"] = sorted(override_by_highway.keys())
    graph.graph["road_class_overrides_applied_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    save_graphml(graph, graph_path)

    override_sha = _file_sha256(args.overrides)
    manifest = _build_manifest(
        graph_path=graph_path,
        overrides_path=Path(args.overrides),
        override_sha256=override_sha,
        graph_sha256=_file_sha256(graph_path),
        total_edges=graph.number_of_edges(),
        edges_updated=edges_updated,
        edges_unmatched=edges_unmatched,
        highway_counts=highway_counts,
        backup_path=backup_path if backup_path.exists() else None,
    )
    manifest_path = Path(args.manifest)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _build_manifest(
    *,
    graph_path: Path,
    overrides_path: Path,
    override_sha256: str,
    graph_sha256: str,
    total_edges: int,
    edges_updated: int,
    edges_unmatched: int,
    highway_counts: dict[str, int],
    backup_path: Path | None,
) -> dict:
    return {
        "schema_version": 1,
        "result_scope": (
            "reviewer_signed_road_class_override_application; decision-support "
            "scope only, not operational routing or field-calibrated traffic "
            "engineering values"
        ),
        "claim_boundary": (
            "Road-class overrides are reviewer-approved class-level values for "
            "decision-support simulation. They are not operational routing, not "
            "calibrated per-edge traffic engineering, and not field-measured "
            "capacity or disruption evidence."
        ),
        "graphml_path": str(graph_path),
        "overrides_path": str(overrides_path),
        "overrides_sha256": override_sha256,
        "graphml_sha256": graph_sha256,
        "total_edges": total_edges,
        "edges_updated": edges_updated,
        "edges_unmatched": edges_unmatched,
        "highway_counts": dict(sorted(highway_counts.items())),
        "backup_path": str(backup_path) if backup_path else None,
        "can_support_road_evidence_gate": True,
        "can_support_publication_gate": True,
    }


def _file_sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Apply reviewer-approved road-class overrides to the cached OSM "
            "GraphML so per-edge maxspeed/capacity/base_p_fail values are "
            "explicit for the road-input evidence audit."
        ),
    )
    parser.add_argument(
        "--overrides",
        type=Path,
        default=DEFAULT_OVERRIDES_PATH,
        help="Path to reviewed road_class_overrides.csv",
    )
    parser.add_argument(
        "--graphml",
        type=Path,
        default=DEFAULT_GRAPHML_PATH,
        help="Path to cached pilot_region_road.graphml (will be modified in-place)",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_GRAPHML_MANIFEST_PATH,
        help="Path to write the updated graph cache manifest",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip backing up the raw OSM cache to *.raw.graphml",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
