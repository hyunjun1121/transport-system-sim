"""Regenerate the summary truth table from pilot_full_summary.csv."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE = PROJECT_ROOT / "results" / "realworld_pilot" / "pilot_full_summary.csv"
DEST_CSV = PROJECT_ROOT / "data" / "validation" / "summary_truth_table.csv"
DEST_MANIFEST = PROJECT_ROOT / "data" / "validation" / "summary_truth_manifest.json"


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(f"source not found: {SOURCE}")

    with SOURCE.open("rb") as f:
        source_bytes = f.read()
    source_sha256 = hashlib.sha256(source_bytes).hexdigest()

    shutil.copy2(SOURCE, DEST_CSV)

    with DEST_CSV.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    row_count = len(rows)
    policies = sorted({r["policy_id"] for r in rows})
    scenarios = sorted({r["scenario_id"] for r in rows})
    cross_product = len(policies) * len(scenarios)

    manifest = {
        "source_file": "results/realworld_pilot/pilot_full_summary.csv",
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
    print(f"Output: {DEST_CSV}")


if __name__ == "__main__":
    main()
