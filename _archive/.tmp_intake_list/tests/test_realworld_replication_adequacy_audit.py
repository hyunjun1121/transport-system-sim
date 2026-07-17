"""Tests for replication adequacy audit."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.replication_adequacy_audit import (  # noqa: E402
    build_replication_adequacy_rows,
    write_replication_adequacy_audit,
)


def test_replication_audit_flags_missing_multiple_comparison_decision() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        manifest = _write_statistics_bundle(root)
        rows = build_replication_adequacy_rows(
            statistics_manifest_path=manifest,
            minimum_seed_count=3,
        )
    by_id = {row["check_id"]: row for row in rows}
    assert by_id["paired_counts_match_seed_count"]["status"] == "pass"
    assert by_id["replication_count_human_review"]["status"] == "needs_human_review"
    assert by_id["multiple_comparison_procedure"]["status"] == "blocked"


def test_replication_audit_reviews_incomplete_finite_counts() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        manifest = _write_statistics_bundle(root, paired_count=2)
        rows = build_replication_adequacy_rows(
            statistics_manifest_path=manifest,
            minimum_seed_count=3,
        )
    by_id = {row["check_id"]: row for row in rows}
    assert by_id["paired_counts_match_seed_count"]["status"] == "needs_human_review"


def test_write_replication_audit_outputs_files() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        manifest = _write_statistics_bundle(root)
        summary = write_replication_adequacy_audit(
            statistics_manifest_path=manifest,
            output_path=root / "replication.csv",
            audit_manifest_path=root / "replication.json",
            doc_path=root / "replication.md",
            minimum_seed_count=3,
        )
        loaded = json.loads((root / "replication.json").read_text(encoding="utf-8"))
        doc = (root / "replication.md").read_text(encoding="utf-8")
    assert loaded["blocking_check_count"] == 1
    assert summary["acceptance_ready"] is False
    assert "Replication Adequacy Audit" in doc


def _write_statistics_bundle(root: Path, *, paired_count: int = 3) -> Path:
    source_manifest = root / "pilot_manifest.json"
    metric_ci = root / "metric_ci.csv"
    paired_delta = root / "paired_delta.csv"
    stats_manifest = root / "statistics_manifest.json"
    source_manifest.write_text(
        json.dumps(
            {
                "scenario_policy_seed_design": {"seed_count": 3},
                "seeds": [1, 2, 3],
            }
        ),
        encoding="utf-8",
    )
    _write_csv(
        metric_ci,
        ["sample_count"],
        [{"sample_count": "3"}],
    )
    _write_csv(
        paired_delta,
        ["paired_count", "baseline_policy_id"],
        [{"paired_count": str(paired_count), "baseline_policy_id": "bus_only"}],
    )
    stats_manifest.write_text(
        json.dumps(
            {
                "source_manifest_path": str(source_manifest),
                "outputs": {
                    "metric_ci": str(metric_ci),
                    "paired_delta_ci": str(paired_delta),
                },
                "metric_ci_row_count": 1,
                "paired_delta_ci_row_count": 1,
                "baseline_policy_id": "bus_only",
                "ci_method": "normal_approximation",
            }
        ),
        encoding="utf-8",
    )
    return stats_manifest


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    test_replication_audit_flags_missing_multiple_comparison_decision()
    test_replication_audit_reviews_incomplete_finite_counts()
    test_write_replication_audit_outputs_files()
    print("PASS: replication adequacy audit")
