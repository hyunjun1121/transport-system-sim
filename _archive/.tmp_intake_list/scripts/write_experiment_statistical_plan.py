"""Write the experiment statistical-analysis plan and design note."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.experiment_statistical_plan import (  # noqa: E402
    DEFAULT_EXPERIMENT_STATISTICAL_PLAN_DOC_PATH,
    DEFAULT_EXPERIMENT_STATISTICAL_PLAN_MANIFEST_PATH,
    write_experiment_statistical_plan,
)


def main() -> int:
    """Write the non-acceptance experiment statistical-analysis plan."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        default=str(DEFAULT_EXPERIMENT_STATISTICAL_PLAN_MANIFEST_PATH),
        help="Output JSON manifest path.",
    )
    parser.add_argument(
        "--doc",
        default=str(DEFAULT_EXPERIMENT_STATISTICAL_PLAN_DOC_PATH),
        help="Output Markdown document path.",
    )
    parser.add_argument(
        "--fail-on-blockers",
        action="store_true",
        help="Return non-zero when structural blockers remain.",
    )
    args = parser.parse_args()
    manifest = write_experiment_statistical_plan(
        manifest_path=args.manifest,
        doc_path=args.doc,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    if args.fail_on_blockers and manifest["blocking_check_count"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
