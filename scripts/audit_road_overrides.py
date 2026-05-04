"""Audit optional road-class override evidence status."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.road_override_audit import (  # noqa: E402
    audit_road_class_override_application,
    audit_road_class_override_evidence,
)


def main() -> int:
    """Print a JSON road-class override audit."""

    evidence = audit_road_class_override_evidence()
    application = audit_road_class_override_application()
    summary = {
        "publication_ready": bool(
            evidence["publication_ready"] and application["publication_ready"]
        ),
        "claim_boundary": (
            "Road override readiness requires source-backed override rows and "
            "an accepted pilot manifest proving those rows were applied."
        ),
        "evidence": evidence,
        "application": application,
        "remaining_blockers": [
            *[f"evidence: {item}" for item in evidence.get("remaining_blockers", [])],
            *[f"application: {item}" for item in application.get("remaining_blockers", [])],
        ],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
