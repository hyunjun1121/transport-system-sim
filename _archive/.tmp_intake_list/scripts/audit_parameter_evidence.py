"""Audit current parameter evidence status without upgrading claims."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.parameter_audit import (  # noqa: E402
    audit_shipped_parameter_evidence,
)


def main() -> int:
    """Print a JSON parameter-evidence audit and fail only on invalid schema."""

    summary = audit_shipped_parameter_evidence()
    summary["parameter_directory"] = "data/parameters"
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
