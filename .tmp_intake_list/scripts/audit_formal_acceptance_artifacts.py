"""Audit formal acceptance paths for template or placeholder misuse."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.formal_acceptance_guard import (  # noqa: E402
    audit_formal_acceptance_artifacts,
)


def main() -> int:
    """Run the guard and print JSON."""

    summary = audit_formal_acceptance_artifacts()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["template_or_placeholder_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
