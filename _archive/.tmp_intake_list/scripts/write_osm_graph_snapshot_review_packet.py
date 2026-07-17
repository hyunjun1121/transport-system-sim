"""Write the OSM/GraphML snapshot review packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.osm_graph_snapshot_review_packet import (  # noqa: E402
    DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_PATH,
    DEFAULT_OSM_GRAPH_CACHE_MANIFEST_PATH,
    DEFAULT_OSM_GRAPH_SNAPSHOT_REVIEW_DOC_PATH,
    DEFAULT_OSM_GRAPH_SNAPSHOT_REVIEW_MANIFEST_PATH,
    DEFAULT_OSM_GRAPH_SNAPSHOT_REVIEW_PACKET_PATH,
    DEFAULT_ROAD_EVIDENCE_PRIORITY_MANIFEST_PATH,
    DEFAULT_ROAD_SOURCE_DECISION_MANIFEST_PATH,
    DEFAULT_SOURCE_PROVENANCE_MANIFEST_PATH,
    build_osm_graph_snapshot_review_rows,
    write_osm_graph_snapshot_review_packet,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_osm_graph_snapshot_review_rows(
        cache_manifest_path=args.cache_manifest,
        source_provenance_manifest_path=args.source_provenance_manifest,
        road_evidence_priority_manifest_path=args.road_evidence_priority_manifest,
        road_source_decision_manifest_path=args.road_source_decision_manifest,
        graph_scale_manifest_audit_path=args.graph_scale_manifest_audit,
    )
    manifest = write_osm_graph_snapshot_review_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        cache_manifest_path=args.cache_manifest,
        source_provenance_manifest_path=args.source_provenance_manifest,
        road_evidence_priority_manifest_path=args.road_evidence_priority_manifest,
        road_source_decision_manifest_path=args.road_source_decision_manifest,
        graph_scale_manifest_audit_path=args.graph_scale_manifest_audit,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a non-approval OSM/GraphML snapshot review packet."
        )
    )
    parser.add_argument(
        "--cache-manifest",
        type=Path,
        default=DEFAULT_OSM_GRAPH_CACHE_MANIFEST_PATH,
    )
    parser.add_argument(
        "--source-provenance-manifest",
        type=Path,
        default=DEFAULT_SOURCE_PROVENANCE_MANIFEST_PATH,
    )
    parser.add_argument(
        "--road-evidence-priority-manifest",
        type=Path,
        default=DEFAULT_ROAD_EVIDENCE_PRIORITY_MANIFEST_PATH,
    )
    parser.add_argument(
        "--road-source-decision-manifest",
        type=Path,
        default=DEFAULT_ROAD_SOURCE_DECISION_MANIFEST_PATH,
    )
    parser.add_argument(
        "--graph-scale-manifest-audit",
        type=Path,
        default=DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_PATH,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OSM_GRAPH_SNAPSHOT_REVIEW_PACKET_PATH,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_OSM_GRAPH_SNAPSHOT_REVIEW_MANIFEST_PATH,
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_OSM_GRAPH_SNAPSHOT_REVIEW_DOC_PATH,
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
