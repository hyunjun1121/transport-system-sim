"""Tests for scaffold-only pilot figure and table generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.pilot_figures import (
    DEFAULT_PILOT_MANIFEST_PATH,
    DEFAULT_PILOT_SUMMARY_PATH,
    DEFAULT_SENSITIVITY_MANIFEST_PATH,
    DEFAULT_SENSITIVITY_SUMMARY_PATH,
    FIGURE_FILENAMES,
    FIXTURE_LABEL,
    TABLE_FILENAMES,
    build_pilot_figure_tables,
)


def test_build_pilot_figures_writes_expected_artifacts() -> None:
    """The builder should write every required scaffold-only artifact."""

    _assert_committed_sample_inputs_exist()
    with TemporaryDirectory() as directory:
        result = build_pilot_figure_tables(output_dir=directory)

        expected_figures = {Path(filename).stem for filename in FIGURE_FILENAMES}
        expected_tables = {Path(filename).stem for filename in TABLE_FILENAMES}

        assert set(result["figures"]) == expected_figures
        assert set(result["tables"]) == expected_tables

        for path in result["figures"].values():
            assert path.exists(), f"missing figure: {path}"
            assert path.stat().st_size > 0, f"empty figure: {path}"

        for path in result["tables"].values():
            assert path.exists(), f"missing table: {path}"
            assert path.stat().st_size > 0, f"empty table: {path}"

        with result["tables"]["main_result_table"].open(
            "r",
            encoding="utf-8",
            newline="",
        ) as handle:
            main_rows = list(csv.DictReader(handle))

        with result["tables"]["sensitivity_result_table"].open(
            "r",
            encoding="utf-8",
            newline="",
        ) as handle:
            sensitivity_rows = list(csv.DictReader(handle))

        assert main_rows
        assert sensitivity_rows
        assert all(row["evidence_label"] == FIXTURE_LABEL for row in main_rows)
        assert all(row["evidence_label"] == FIXTURE_LABEL for row in sensitivity_rows)

    print("PASS: pilot figure builder writes all required artifacts")


def test_claim_boundary_table_labels_scaffold_only_limitations() -> None:
    """Claim-boundary rows should block calibrated or operational claims."""

    _assert_committed_sample_inputs_exist()
    with TemporaryDirectory() as directory:
        result = build_pilot_figure_tables(output_dir=directory)
        path = result["tables"]["claim_boundary_table"]

        with path.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))

        assert rows
        assert all(row["evidence_label"] == FIXTURE_LABEL for row in rows)
        assert any("Scaffold-only" in row["limitation"] for row in rows)
        assert any("not calibrated real-world" in row["limitation"] for row in rows)
        assert all("Do not" in row["prohibited_use"] for row in rows)
        assert all(row["source_scope"] for row in rows)

    print("PASS: claim-boundary table marks scaffold-only limitations")


def test_manifest_records_source_inputs_and_claim_scope() -> None:
    """The generated manifest should trace inputs, files, and conservative scope."""

    _assert_committed_sample_inputs_exist()
    with TemporaryDirectory() as directory:
        result = build_pilot_figure_tables(output_dir=directory)
        manifest_path = result["tables"]["figure_table_manifest"]

        with manifest_path.open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)

        assert manifest["evidence_label"] == FIXTURE_LABEL
        assert "not calibrated real-world" in manifest["result_scope"]
        assert manifest["inputs"]["pilot_summary_path"].endswith(
            "results/realworld_pilot/pilot_full_summary.csv"
        )
        assert manifest["source_commands"]["pilot"].endswith("--full")
        assert manifest["inputs"]["sensitivity_summary_path"].endswith(
            "results/realworld_pilot/morris_summary.csv"
        )
        assert manifest["source_commands"]["sensitivity"].endswith("--method morris --all")
        assert "non-finite" in manifest["morris_index_handling"]["figures"]
        assert "counts blank" in manifest["morris_index_handling"]["audit"]
        assert manifest["graph_scale"]["pilot"]["source"]["nodes"] == 4608
        assert manifest["graph_scale"]["pilot"]["analysis"]["nodes"] == 118
        assert manifest["graph_scale"]["sensitivity"]["source"]["nodes"] == 4608
        assert manifest["graph_scale"]["sensitivity"]["analysis"]["nodes"] == 118
        assert manifest["graph_scale"]["sensitivity"]["analysis"]["reduced"] is True
        assert manifest["row_counts"]["main_result_table"] > 0
        assert manifest["row_counts"]["sensitivity_result_table"] > 0
        assert set(manifest["figures"]) == {Path(name).stem for name in FIGURE_FILENAMES}

    print("PASS: figure/table manifest records inputs and claim scope")


def _assert_committed_sample_inputs_exist() -> None:
    for path in (
        DEFAULT_PILOT_SUMMARY_PATH,
        DEFAULT_SENSITIVITY_SUMMARY_PATH,
        DEFAULT_PILOT_MANIFEST_PATH,
        DEFAULT_SENSITIVITY_MANIFEST_PATH,
    ):
        assert path.exists(), f"missing sample input: {path}"


if __name__ == "__main__":
    test_build_pilot_figures_writes_expected_artifacts()
    test_claim_boundary_table_labels_scaffold_only_limitations()
    test_manifest_records_source_inputs_and_claim_scope()
    print("\n=== REALWORLD PILOT FIGURE TESTS PASSED ===")
