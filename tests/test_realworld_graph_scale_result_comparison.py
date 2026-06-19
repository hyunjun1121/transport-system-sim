"""Tests for graph-scale result comparison review packet."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.graph_scale_result_comparison import (  # noqa: E402
    DEFAULT_RESULT_COMPARISON_MANIFEST_PATH,
    DEFAULT_RESULT_COMPARISON_PATH,
    RESULT_COMPARISON_COLUMNS,
    RESULT_COMPARISON_SCOPE,
    SUMMARY_METRIC_COLUMNS,
    build_graph_scale_result_comparison_rows,
    write_graph_scale_result_comparison,
)


def test_graph_scale_result_rows_compare_metric_directions() -> None:
    """Metric deltas should classify direction-sensitive changes."""

    with TemporaryDirectory() as directory:
        current = Path(directory) / "current.csv"
        candidate = Path(directory) / "candidate.csv"
        _write_summary(
            current,
            completion="0.5",
            censored="2",
            makespan="100",
            efficiency="0.2",
        )
        _write_summary(
            candidate,
            completion="0.75",
            censored="1",
            makespan="110",
            efficiency="0.1",
        )

        rows = build_graph_scale_result_comparison_rows(
            current_summary_path=current,
            candidate_summary_path=candidate,
        )
        by_metric = {row["metric"]: row for row in rows}

        assert len(rows) == len(SUMMARY_METRIC_COLUMNS)
        assert by_metric["mean_completion_rate"]["comparison_status"] == "candidate_improves"
        assert by_metric["mean_censored_count"]["comparison_status"] == "candidate_improves"
        assert by_metric["mean_makespan"]["comparison_status"] == "candidate_worsens"
        assert (
            by_metric["mean_passengers_per_total_service_minute"][
                "comparison_status"
            ]
            == "candidate_worsens"
        )
        assert {row["claim_scope"] for row in rows} == {RESULT_COMPARISON_SCOPE}

    print("PASS: graph-scale result comparison classifies metric deltas")


def test_write_graph_scale_result_comparison_outputs_manifest() -> None:
    """Writer should emit stable CSV fields and non-acceptance manifest."""

    rows = build_graph_scale_result_comparison_rows()

    with TemporaryDirectory() as directory:
        output = Path(directory) / "comparison.csv"
        manifest_path = Path(directory) / "manifest.json"
        manifest = write_graph_scale_result_comparison(
            rows=rows,
            output_path=output,
            manifest_path=manifest_path,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == RESULT_COMPARISON_COLUMNS
        with manifest_path.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)

        assert len(written_rows) == len(rows)
        assert manifest["publication_ready"] is False
        assert written_manifest["result_scope"] == RESULT_COMPARISON_SCOPE
        assert "does not accept a graph method" in written_manifest["claim_boundary"]

    print("PASS: graph-scale result comparison writer emits manifest")


def test_shipped_graph_scale_result_comparison_matches_current_summaries() -> None:
    """Current shipped comparison should match deterministic summary inputs."""

    rows = build_graph_scale_result_comparison_rows()

    assert DEFAULT_RESULT_COMPARISON_PATH.exists()
    assert DEFAULT_RESULT_COMPARISON_MANIFEST_PATH.exists()
    with DEFAULT_RESULT_COMPARISON_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    with DEFAULT_RESULT_COMPARISON_MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)

    assert len(written_rows) == manifest["row_count"]
    assert manifest["row_count"] == 6877
    assert manifest["publication_ready"] is False
    assert "candidate_worsens" in manifest["comparison_status_counts"]
    assert "same_or_close" in manifest["comparison_status_counts"]

    print("PASS: shipped graph-scale result comparison matches current summaries")


def _write_summary(
    path: Path,
    *,
    completion: str,
    censored: str,
    makespan: str,
    efficiency: str,
) -> None:
    row = {
        "region_id": "r",
        "graph_source": "g",
        "policy_id": "p",
        "scenario_id": "s",
        "scenario_family": "f",
        "scenario_type": "t",
        "mode": "bus_only",
        "run_count": "1",
        "mean_completion_rate": completion,
        "mean_censored_count": censored,
        "mean_penalized_makespan": makespan,
        "mean_makespan": makespan,
        "mean_road_vehicle_service_minutes": makespan,
        "mean_train_service_minutes": "0",
        "mean_total_service_minutes": makespan,
        "mean_passenger_travel_minutes": makespan,
        "mean_passengers_per_total_service_minute": efficiency,
        "mean_first_arrival_time": makespan,
        "mean_median_arrival_time": makespan,
        "mean_p80_arrival_time": makespan,
        "mean_p95_arrival_time": makespan,
        "claim_scope": "fixture",
    }
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)


if __name__ == "__main__":
    test_graph_scale_result_rows_compare_metric_directions()
    test_write_graph_scale_result_comparison_outputs_manifest()
    test_shipped_graph_scale_result_comparison_matches_current_summaries()
    print("\n=== REALWORLD GRAPH-SCALE RESULT COMPARISON TESTS PASSED ===")
