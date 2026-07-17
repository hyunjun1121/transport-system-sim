"""Write sub-agent task assignments for unresolved formal acceptance blockers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.acceptance_task_assignments import (  # noqa: E402
    DEFAULT_TASK_ASSIGNMENT_DOC_PATH,
    DEFAULT_TASK_ASSIGNMENT_MANIFEST_PATH,
    DEFAULT_TASK_ASSIGNMENT_PATH,
    write_acceptance_task_assignments,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(DEFAULT_TASK_ASSIGNMENT_PATH))
    parser.add_argument("--manifest", default=str(DEFAULT_TASK_ASSIGNMENT_MANIFEST_PATH))
    parser.add_argument("--doc", default=str(DEFAULT_TASK_ASSIGNMENT_DOC_PATH))
    parser.add_argument(
        "--fail-on-blockers",
        action="store_true",
        help="Return non-zero while assignments still contain unresolved tasks.",
    )
    args = parser.parse_args()

    summary = write_acceptance_task_assignments(
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.fail_on_blockers and int(summary["task_count"]) > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
