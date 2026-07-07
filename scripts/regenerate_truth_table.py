"""Regenerate the summary truth table from a pilot_full_summary.csv.

Default source is the canonical OSM-era ``results/realworld_pilot/pilot_full_summary.csv``
(backward-compatible). Pass ``--source`` to regenerate from another summary — e.g. the
Phase-2 표준노드링크 run ``results/realworld_pilot_nodelink/pilot_full_summary.csv``. The
manifest's ``source_file`` label follows ``--source-file-label`` (defaults to the
repo-relative ``--source`` path with forward slashes).

Decision-support / quasi-real only — the truth table is a frozen reference snapshot, not a
calibrated or validated forecast. ``final_study_ready`` stays false.

Usage::

    # default (OSM-era canonical summary)
    .\\.venv\\Scripts\\python scripts/regenerate_truth_table.py
    # Phase-2 nodelink canonical summary
    .\\.venv\\Scripts\\python scripts/regenerate_truth_table.py `
      --source results/realworld_pilot_nodelink/pilot_full_summary.csv
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = PROJECT_ROOT / "results" / "realworld_pilot" / "pilot_full_summary.csv"
DEST_CSV = PROJECT_ROOT / "data" / "validation" / "summary_truth_table.csv"
DEST_MANIFEST = PROJECT_ROOT / "data" / "validation" / "summary_truth_manifest.json"


def _repo_relative(path: Path) -> str:
    """Repo-relative forward-slash label for the manifest source_file field."""
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help="pilot_full_summary.csv to freeze as the truth table.",
    )
    parser.add_argument(
        "--source-file-label",
        default=None,
        help="Manifest source_file label (defaults to the repo-relative --source path).",
    )
    args = parser.parse_args(argv)

    source_abs = args.source if args.source.is_absolute() else (PROJECT_ROOT / args.source)
    source_abs = source_abs.resolve()
    if not source_abs.exists():
        raise FileNotFoundError(f"source not found: {source_abs}")

    with source_abs.open("rb") as f:
        source_bytes = f.read()
    source_sha256 = hashlib.sha256(source_bytes).hexdigest()

    shutil.copy2(source_abs, DEST_CSV)

    with DEST_CSV.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    row_count = len(rows)
    policies = sorted({r["policy_id"] for r in rows})
    scenarios = sorted({r["scenario_id"] for r in rows})
    cross_product = len(policies) * len(scenarios)

    source_label = args.source_file_label or _repo_relative(source_abs)
    manifest = {
        "source_file": source_label,
        "source_sha256": source_sha256,
        "row_count": row_count,
        "unique_policy_count": len(policies),
        "unique_scenario_count": len(scenarios),
        "expected_cross_product": cross_product,
        "cross_product_matches": row_count == cross_product,
    }

    with DEST_MANIFEST.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Truth table: {row_count} rows, {len(policies)} policies, {len(scenarios)} scenarios")
    print(f"Cross-product matches: {manifest['cross_product_matches']}")
    print(f"SHA256: {source_sha256}")
    print(f"Source: {source_label}")
    print(f"Output: {DEST_CSV}")


if __name__ == "__main__":
    main()
