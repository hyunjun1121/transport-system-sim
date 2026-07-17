"""Audit cached OSM road-input evidence without upgrading claims."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.road_evidence import audit_cached_road_evidence  # noqa: E402
from src.realworld.road_override_audit import (  # noqa: E402
    audit_road_class_override_evidence,
)


def main() -> int:
    """Print a JSON road-input evidence audit."""

    summary = audit_cached_road_evidence()
    summary["road_class_override_evidence"] = audit_road_class_override_evidence()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
