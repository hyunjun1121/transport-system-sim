"""Write a draft road-class override template from cached OSM diagnostics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.road_evidence import DEFAULT_ROAD_GRAPH_PATH  # noqa: E402
from src.realworld.road_evidence_diagnostics import (
    audit_cached_road_evidence_diagnostics,
)  # noqa: E402
from src.realworld.road_override_template import (
    build_road_class_override_template_rows,
    write_road_class_override_template,
)  # noqa: E402


DEFAULT_OUTPUT_PATH = ROOT / "data" / "parameters" / "road_class_overrides_draft.csv"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Create a draft, non-acceptance road-class override CSV for reviewer "
            "source-strengthening work."
        )
    )
    parser.add_argument(
        "--input-graph",
        default=str(DEFAULT_ROAD_GRAPH_PATH),
        help="Cached OSM/GraphML graph to diagnose.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help="Draft CSV path to write.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=10,
        help="Maximum number of prioritized highway classes to include.",
    )
    parser.add_argument(
        "--include-low-priority",
        action="store_true",
        help="Include low-priority routeable road classes in addition to high/medium rows.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite an existing draft output file.",
    )
    args = parser.parse_args()

    output_path = Path(args.output)
    if output_path.exists() and not args.overwrite:
        print(
            json.dumps(
                {
                    "written": False,
                    "output": _display_path(output_path),
                    "error": "output exists; pass --overwrite to replace it",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

    diagnostics = audit_cached_road_evidence_diagnostics(args.input_graph)
    if not diagnostics.get("diagnostics_ready"):
        print(
            json.dumps(
                {
                    "written": False,
                    "output": _display_path(output_path),
                    "diagnostics_ready": False,
                    "remaining_blockers": diagnostics.get("remaining_blockers", []),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    rows = build_road_class_override_template_rows(
        diagnostics,
        include_low_priority=args.include_low_priority,
        top_n=args.top_n,
    )
    write_road_class_override_template(output_path, rows)
    print(
        json.dumps(
            {
                "written": True,
                "output": _display_path(output_path),
                "row_count": len(rows),
                "publication_ready": False,
                "claim_boundary": (
                    "This is a draft review template populated with current mapper "
                    "defaults. Replace values and sources before using it as "
                    "road-class override evidence."
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
