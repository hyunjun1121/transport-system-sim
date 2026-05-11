"""Audit current rail evidence status without upgrading claims."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.rail_evidence import (  # noqa: E402
    DEFAULT_RAIL_SERVICE_EVIDENCE_PATH,
    load_rail_service_evidence,
    summarize_rail_service_evidence,
)
from src.realworld.rail_station_binding import (  # noqa: E402
    DEFAULT_RAIL_STATION_BINDING_PATH,
    load_rail_station_bindings,
    summarize_rail_station_bindings,
)


def main() -> int:
    """Print a JSON rail evidence audit and fail only on invalid schema."""

    records = load_rail_service_evidence(DEFAULT_RAIL_SERVICE_EVIDENCE_PATH)
    summary = summarize_rail_service_evidence(records)
    binding_records = load_rail_station_bindings(DEFAULT_RAIL_STATION_BINDING_PATH)
    binding_summary = summarize_rail_station_bindings(binding_records)
    summary["path"] = str(DEFAULT_RAIL_SERVICE_EVIDENCE_PATH.relative_to(ROOT))
    summary["service_publication_ready"] = summary["publication_ready"]
    summary["station_binding_ready"] = binding_summary["binding_ready"]
    summary["publication_ready"] = (
        bool(summary["service_publication_ready"])
        and bool(summary["station_binding_ready"])
    )
    summary["station_binding"] = {
        "path": str(DEFAULT_RAIL_STATION_BINDING_PATH.relative_to(ROOT)),
        "row_count": binding_summary["row_count"],
        "required_points": binding_summary["required_points"],
        "source_status_counts": binding_summary["source_status_counts"],
        "official_required_points": binding_summary["official_required_points"],
        "missing_required_points": binding_summary["missing_required_points"],
        "unofficial_required_points": binding_summary["unofficial_required_points"],
        "remaining_blockers": binding_summary["remaining_blockers"],
    }
    summary["cached_timetable_derivation_path_available"] = (
        (ROOT / "scripts" / "derive_rail_service_evidence.py").exists()
        and (ROOT / "docs" / "schemas" / "rail_timetable_cache_schema.md").exists()
    )
    summary["cached_shortest_path_derivation_path_available"] = (
        (ROOT / "scripts" / "derive_rail_shortest_path_evidence.py").exists()
        and (ROOT / "docs" / "schemas" / "rail_shortest_path_cache_schema.md").exists()
    )
    summary["cached_gtfs_derivation_path_available"] = (
        (ROOT / "scripts" / "derive_rail_gtfs_evidence.py").exists()
        and (ROOT / "docs" / "schemas" / "rail_gtfs_cache_schema.md").exists()
    )
    summary["current_source_statuses"] = sorted(
        {record.source_status for record in records}
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
