"""Tests for sensitivity diagnostics review packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.sensitivity import MORRIS_SUMMARY_COLUMNS  # noqa: E402
from src.realworld.sensitivity_review_packet import (  # noqa: E402
    DEFAULT_SENSITIVITY_REVIEW_MANIFEST_PATH,
    DEFAULT_SENSITIVITY_REVIEW_PACKET_PATH,
    SENSITIVITY_REVIEW_COLUMNS,
    SENSITIVITY_REVIEW_PACKET_SCOPE,
    build_sensitivity_review_rows,
    write_sensitivity_review_packet,
)


def test_sensitivity_review_rows_summarize_current_morris_diagnostics() -> None:
    """Current Morris diagnostics should become conservative review rows."""

    rows = build_sensitivity_review_rows()
    by_category = {row["category_id"]: row for row in rows}

    assert len(rows) == 6
    assert set(by_category) == {
        "structural_readiness",
        "missing_or_nonfinite_morris_indices",
        "zero_mu_star_rows",
        "reduced_graph_scope",
        "result_scope",
        "sobol_decision_requirement",
    }
    assert by_category["structural_readiness"]["diagnostic_status"] == "available_for_review"
    assert by_category["missing_or_nonfinite_morris_indices"]["diagnostic_status"] == (
        "review_required_unavailable_indices"
    )
    assert by_category["missing_or_nonfinite_morris_indices"]["affected_row_count"] == "4872"
    assert "mu_star=0" in by_category["missing_or_nonfinite_morris_indices"]["diagnostic_detail"]
    assert "unavailable_index_rows=4872" in by_category["missing_or_nonfinite_morris_indices"]["diagnostic_detail"]
    assert by_category["zero_mu_star_rows"]["affected_row_count"] == "29601"
    assert by_category["reduced_graph_scope"]["affected_row_count"] == "54096"
    assert by_category["result_scope"]["publication_ready"] == "false"
    assert by_category["sobol_decision_requirement"]["acceptance_ready"] == "false"
    assert {row["claim_boundary"] for row in rows} == {
        SENSITIVITY_REVIEW_PACKET_SCOPE
    }

    print("PASS: sensitivity review rows summarize current Morris diagnostics")


def test_write_sensitivity_review_packet_outputs_csv_and_manifest() -> None:
    """Writer should emit stable CSV fields and non-acceptance manifest."""

    rows = build_sensitivity_review_rows()

    with TemporaryDirectory() as directory:
        output = Path(directory) / "sensitivity_review.csv"
        manifest = Path(directory) / "sensitivity_review_manifest.json"
        value = write_sensitivity_review_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == SENSITIVITY_REVIEW_COLUMNS
        with manifest.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)

        assert len(written_rows) == 6
        assert value["publication_ready"] is False
        assert value["acceptance_ready"] is False
        assert value["review_required"] is True
        assert value["acceptance_gate_closure_candidate_count"] == 0
        assert written_manifest["row_count"] == 6
        assert written_manifest["rows_with_index_issues"] == 0
        assert written_manifest["all_rows_with_index_issues"] == 4872
        assert written_manifest["unavailable_index_row_count"] == 4872
        assert written_manifest["index_issue_counts"]["mu_star"] == 0
        assert written_manifest["all_index_issue_counts"]["mu_star"] == 4872
        assert written_manifest["zero_mu_star_count"] == 29601
        assert "does not close the sensitivity gate" in written_manifest["claim_boundary"]

    print("PASS: sensitivity review packet writer emits CSV and manifest")


def test_sensitivity_review_rows_handle_temp_fixture_index_issues() -> None:
    """A temp Morris fixture should surface blank indices and zero mu_star rows."""

    with TemporaryDirectory() as directory:
        summary_path, manifest_path = _write_morris_fixture(Path(directory))
        rows = build_sensitivity_review_rows(
            summary_path=summary_path,
            morris_manifest_path=manifest_path,
        )
        by_category = {row["category_id"]: row for row in rows}

        assert by_category["structural_readiness"]["diagnostic_status"] == "available_for_review"
        assert by_category["missing_or_nonfinite_morris_indices"]["affected_row_count"] == "1"
        assert "sigma=1" in by_category["missing_or_nonfinite_morris_indices"]["diagnostic_detail"]
        assert by_category["zero_mu_star_rows"]["affected_row_count"] == "1"
        assert by_category["reduced_graph_scope"]["affected_row_count"] == "0"

    print("PASS: sensitivity review rows handle temp fixture index issues")


def test_shipped_sensitivity_review_packet_matches_current_diagnostics() -> None:
    """Current shipped review packet should match deterministic Morris diagnostics."""

    rows = build_sensitivity_review_rows()

    assert DEFAULT_SENSITIVITY_REVIEW_PACKET_PATH.exists()
    assert DEFAULT_SENSITIVITY_REVIEW_MANIFEST_PATH.exists()
    with DEFAULT_SENSITIVITY_REVIEW_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    with DEFAULT_SENSITIVITY_REVIEW_MANIFEST_PATH.open(
        "r",
        encoding="utf-8",
    ) as handle:
        manifest = json.load(handle)

    assert len(written_rows) == len(rows)
    assert [row["category_id"] for row in written_rows] == [
        row["category_id"] for row in rows
    ]
    assert manifest["publication_ready"] is False
    assert manifest["acceptance_ready"] is False
    assert manifest["result_scope"] == SENSITIVITY_REVIEW_PACKET_SCOPE
    assert manifest["row_count"] == 6
    assert manifest["acceptance_gate_closure_candidate_count"] == 0

    print("PASS: shipped sensitivity review packet matches current diagnostics")


def _write_morris_fixture(directory: Path) -> tuple[Path, Path]:
    summary_path = directory / "morris_summary.csv"
    manifest_path = directory / "morris_manifest.json"
    rows = [
        _morris_row(
            parameter_id="passenger_volume",
            salib_name="passenger_volume",
            mu="1.0",
            mu_star="0.0",
            sigma="0.0",
            mu_star_conf="0.0",
        ),
        _morris_row(
            parameter_id="rail_headway",
            salib_name="rail_headway",
            mu="",
            mu_star="2.0",
            sigma="nan",
            mu_star_conf="0.1",
        ),
    ]
    with summary_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(MORRIS_SUMMARY_COLUMNS))
        writer.writeheader()
        writer.writerows(rows)

    manifest = {
        "schema_version": 1,
        "summary_row_count": 2,
        "rank_metrics": ["completion_rate"],
        "policy_ids": ["bus_only"],
        "scenario_ids": ["no_disruption"],
        "parameter_ids": ["passenger_volume", "rail_headway"],
        "method": "salib_morris",
        "analysis_graph_reduced": False,
        "graph_scale": {
            "source": {"nodes": 20, "edges": 40},
            "analysis": {"nodes": 20, "edges": 40, "reduced": False},
        },
        "result_scope": "Fixture Morris output; not calibrated evidence.",
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return summary_path, manifest_path


def _morris_row(
    *,
    parameter_id: str,
    salib_name: str,
    mu: str,
    mu_star: str,
    sigma: str,
    mu_star_conf: str,
) -> dict[str, str]:
    row = {column: "" for column in MORRIS_SUMMARY_COLUMNS}
    row.update(
        {
            "metric": "completion_rate",
            "policy_id": "bus_only",
            "scenario_id": "no_disruption",
            "rank": "1",
            "parameter_id": parameter_id,
            "salib_name": salib_name,
            "method": "salib_morris",
            "mu": mu,
            "mu_star": mu_star,
            "sigma": sigma,
            "mu_star_conf": mu_star_conf,
            "index_status": "available",
            "index_issue_reason": "",
            "sample_count": "4",
            "num_trajectories": "2",
            "num_levels": "4",
            "claim_scope": "fixture scaffold output",
        }
    )
    return row


if __name__ == "__main__":
    test_sensitivity_review_rows_summarize_current_morris_diagnostics()
    test_write_sensitivity_review_packet_outputs_csv_and_manifest()
    test_sensitivity_review_rows_handle_temp_fixture_index_issues()
    test_shipped_sensitivity_review_packet_matches_current_diagnostics()
    print("\n=== REALWORLD SENSITIVITY REVIEW PACKET TESTS PASSED ===")
