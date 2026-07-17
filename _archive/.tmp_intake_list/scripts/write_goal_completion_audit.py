"""Write a non-acceptance completion audit for the active plan goal."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.goal_completion_audit import (  # noqa: E402
    DEFAULT_GOAL_COMPLETION_AUDIT_PATH,
    DEFAULT_GOAL_COMPLETION_MANIFEST_PATH,
    write_goal_completion_audit,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write docs/current_goal_completion_audit.md without claiming final acceptance.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_GOAL_COMPLETION_AUDIT_PATH,
        help="Markdown output path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_GOAL_COMPLETION_MANIFEST_PATH,
        help="JSON manifest output path.",
    )
    args = parser.parse_args()

    audit = write_goal_completion_audit(args.output, args.manifest)
    print(
        f"Wrote {args.output} and {args.manifest} with "
        f"final_study_ready={audit['final_study_ready']} and "
        f"blocked_gates={len(audit['blocked_gate_ids'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
