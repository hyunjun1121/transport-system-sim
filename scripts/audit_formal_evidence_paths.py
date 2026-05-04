"""Audit evidence paths referenced by formal acceptance artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.formal_evidence_path_audit import (  # noqa: E402
    write_formal_evidence_path_audit,
)


def main() -> int:
    """Write formal evidence-path audit artifacts and print the summary."""

    summary = write_formal_evidence_path_audit()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
