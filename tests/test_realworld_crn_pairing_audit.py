"""Tests for structural CRN pairing audit."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.crn_pairing_audit import (  # noqa: E402
    build_crn_pairing_audit_rows,
    write_crn_pairing_audit,
)


def test_crn_pairing_audit_passes_complete_structural_design() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        manifest = root / "manifest.json"
        results = root / "results.csv"
        source = root / "scenario.py"
        _write_manifest(manifest)
        _write_results(results)
        source.write_text(
            "np.random.default_rng(seed)\nnp.random.default_rng(seed + 10_000)\n",
            encoding="utf-8",
        )
        rows = build_crn_pairing_audit_rows(
            results_path=results,
            manifest_path=manifest,
            scenario_source_path=source,
        )
    by_id = {row["check_id"]: row for row in rows}
    assert by_id["row_count_matches_design"]["status"] == "pass"
    assert by_id["scenario_seed_policy_completeness"]["status"] == "pass"
    assert by_id["policy_scenario_seed_completeness"]["status"] == "pass"
    assert by_id["seed_stream_source_markers"]["status"] == "needs_human_review"


def test_crn_pairing_audit_blocks_missing_policy_row() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        manifest = root / "manifest.json"
        results = root / "results.csv"
        source = root / "scenario.py"
        _write_manifest(manifest)
        _write_results(results, skip=("p2", "s2", 2))
        source.write_text(
            "np.random.default_rng(seed)\nnp.random.default_rng(seed + 10_000)\n",
            encoding="utf-8",
        )
        rows = build_crn_pairing_audit_rows(
            results_path=results,
            manifest_path=manifest,
            scenario_source_path=source,
        )
    by_id = {row["check_id"]: row for row in rows}
    assert by_id["row_count_matches_design"]["status"] == "blocked"
    assert by_id["scenario_seed_policy_completeness"]["status"] == "blocked"
    assert "p2" in by_id["scenario_seed_policy_completeness"]["observed"]


def test_crn_pairing_audit_blocks_region_graph_mismatch() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        manifest = root / "manifest.json"
        results = root / "results.csv"
        source = root / "scenario.py"
        _write_manifest(
            manifest,
            region_id="expected_region",
            graph_source="expected_graph",
        )
        _write_results(
            results,
            region_id="other_region",
            graph_source="other_graph",
        )
        source.write_text(
            "np.random.default_rng(seed)\nnp.random.default_rng(seed + 10_000)\n",
            encoding="utf-8",
        )
        rows = build_crn_pairing_audit_rows(
            results_path=results,
            manifest_path=manifest,
            scenario_source_path=source,
        )
    by_id = {row["check_id"]: row for row in rows}
    assert by_id["region_set_matches_manifest"]["status"] == "blocked"
    assert by_id["graph_source_set_matches_manifest"]["status"] == "blocked"
    assert by_id["scenario_seed_policy_completeness"]["status"] == "blocked"


def test_write_crn_pairing_audit_outputs_files() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        manifest = root / "manifest.json"
        results = root / "results.csv"
        source = root / "scenario.py"
        _write_manifest(manifest)
        _write_results(results)
        source.write_text(
            "np.random.default_rng(seed)\nnp.random.default_rng(seed + 10_000)\n",
            encoding="utf-8",
        )
        summary = write_crn_pairing_audit(
            results_path=results,
            manifest_path=manifest,
            scenario_source_path=source,
            output_path=root / "crn.csv",
            audit_manifest_path=root / "crn.json",
            doc_path=root / "crn.md",
        )
        loaded = json.loads((root / "crn.json").read_text(encoding="utf-8"))
        assert loaded["blocking_check_count"] == 0
        assert summary["structural_crn_pairing_ready"] is True
        assert summary["acceptance_ready"] is False
        assert (root / "crn.csv").exists()
        assert "CRN Pairing Audit" in (root / "crn.md").read_text(encoding="utf-8")


def _write_manifest(
    path: Path,
    *,
    region_id: str = "",
    graph_source: str = "",
) -> None:
    value = {
        "policy_ids": ["p1", "p2"],
        "scenario_ids": ["s1", "s2"],
        "seeds": [1, 2],
        "common_random_numbers": "same seed across policies",
        "scenario_policy_seed_design": {
            "common_random_numbers": True,
            "policy_count": 2,
            "scenario_count": 2,
            "seed_count": 2,
            "expected_row_count": 8,
        },
    }
    if region_id:
        value["region_id"] = region_id
    if graph_source:
        value["graph_source"] = graph_source
    path.write_text(json.dumps(value), encoding="utf-8")


def _write_results(
    path: Path,
    *,
    skip: tuple[str, str, int] | None = None,
    region_id: str = "",
    graph_source: str = "",
) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = ["policy_id", "scenario_id", "seed"]
        if region_id or graph_source:
            fieldnames = ["region_id", "graph_source", *fieldnames]
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
        )
        writer.writeheader()
        for policy in ("p1", "p2"):
            for scenario in ("s1", "s2"):
                for seed in (1, 2):
                    if skip == (policy, scenario, seed):
                        continue
                    row = {
                        "policy_id": policy,
                        "scenario_id": scenario,
                        "seed": seed,
                    }
                    if region_id or graph_source:
                        row["region_id"] = region_id
                        row["graph_source"] = graph_source
                    writer.writerow(row)


if __name__ == "__main__":
    test_crn_pairing_audit_passes_complete_structural_design()
    test_crn_pairing_audit_blocks_missing_policy_row()
    test_crn_pairing_audit_blocks_region_graph_mismatch()
    test_write_crn_pairing_audit_outputs_files()
    print("PASS: CRN pairing audit")
