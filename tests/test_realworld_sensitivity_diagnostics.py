"""Tests for Morris sensitivity diagnostic audits."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.sensitivity import MORRIS_SUMMARY_COLUMNS  # noqa: E402
from src.realworld.sensitivity_diagnostics import (  # noqa: E402
    audit_morris_sensitivity_diagnostics,
)


def test_shipped_morris_diagnostics_are_structurally_ready() -> None:
    """Current scaffold Morris files should be diagnosable without acceptance."""

    summary = audit_morris_sensitivity_diagnostics()

    assert summary["diagnostics_ready"] is True
    assert summary["row_count"] == 7056
    assert summary["manifest_summary_row_count"] == 7056
    assert summary["expected_summary_row_count_from_manifest_dimensions"] == 7056
    assert summary["zero_mu_star_count"] == 4272
    assert summary["remaining_blockers"] == []
    assert summary["review_items"]
    assert "not-calibrated" in " ".join(summary["review_items"])

    print("PASS: shipped Morris diagnostics are structurally ready")


def test_diagnostics_detect_count_mismatch() -> None:
    """Manifest and summary row-count mismatches should be structural blockers."""

    with TemporaryDirectory() as tmp:
        summary_path, manifest_path = _write_fixture(Path(tmp), manifest_summary_count=2)

        summary = audit_morris_sensitivity_diagnostics(
            summary_path=summary_path,
            manifest_path=manifest_path,
        )

        assert summary["diagnostics_ready"] is False
        assert any("row count" in item for item in summary["remaining_blockers"])

    print("PASS: Morris diagnostics detect count mismatch")


def test_diagnostics_count_blank_and_nonfinite_indices() -> None:
    """Blank, NaN, and infinite Morris index values should be visible to review."""

    with TemporaryDirectory() as tmp:
        summary_path, manifest_path = _write_fixture(Path(tmp), bad_indices=True)

        summary = audit_morris_sensitivity_diagnostics(
            summary_path=summary_path,
            manifest_path=manifest_path,
        )

        assert summary["diagnostics_ready"] is True
        assert summary["rows_with_index_issues"] == 1
        assert summary["index_issue_counts"]["mu"] == 1
        assert summary["index_issue_counts"]["sigma"] == 1
        assert any("missing or non-finite" in item for item in summary["review_items"])

    print("PASS: Morris diagnostics count blank and nonfinite indices")


def _write_fixture(
    directory: Path,
    *,
    manifest_summary_count: int = 1,
    bad_indices: bool = False,
) -> tuple[Path, Path]:
    summary_path = directory / "morris_summary.csv"
    manifest_path = directory / "morris_manifest.json"
    row = {column: "" for column in MORRIS_SUMMARY_COLUMNS}
    row.update(
        {
            "metric": "completion_rate",
            "policy_id": "bus_only",
            "scenario_id": "no_disruption",
            "rank": "1",
            "parameter_id": "passenger_volume",
            "salib_name": "passenger_volume",
            "method": "salib_morris",
            "mu": "1.0",
            "mu_star": "1.0",
            "sigma": "0.0",
            "mu_star_conf": "0.0",
            "sample_count": "4",
            "num_trajectories": "2",
            "num_levels": "4",
            "claim_scope": "fixture scaffold output",
        }
    )
    if bad_indices:
        row["mu"] = ""
        row["sigma"] = "nan"
    with summary_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(MORRIS_SUMMARY_COLUMNS))
        writer.writeheader()
        writer.writerow(row)

    manifest = {
        "summary_row_count": manifest_summary_count,
        "rank_metrics": ["completion_rate"],
        "policy_ids": ["bus_only"],
        "scenario_ids": ["no_disruption"],
        "parameter_ids": ["passenger_volume"],
        "analysis_graph_reduced": True,
        "result_scope": "Pilot scaffold output; not calibrated real-world evidence.",
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return summary_path, manifest_path


if __name__ == "__main__":
    test_shipped_morris_diagnostics_are_structurally_ready()
    test_diagnostics_detect_count_mismatch()
    test_diagnostics_count_blank_and_nonfinite_indices()
    print("\n=== REALWORLD SENSITIVITY DIAGNOSTICS TESTS PASSED ===")
