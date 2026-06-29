"""Tests for bounded Phase 10 ML analysis outputs."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.ml_analysis import (  # noqa: E402
    ML_CLAIM_SCOPE,
    build_label_rows,
    write_ml_analysis_outputs,
)


def test_label_derivation_is_deterministic() -> None:
    rows = [
        _row("bus_only", "no_disruption", completion="1.0", censored="0"),
        _row("bus_only", "road_loss", completion="0.85", censored="2"),
        _row("bus_only", "station_loss", completion="0.65", censored="4"),
        _row("bus_only", "terminal_loss", completion="0.25", censored="9"),
    ]

    labels = build_label_rows(rows)

    assert [row["risk_label"] for row in labels] == [
        "normal",
        "watch",
        "risk",
        "failure",
    ]
    assert all(row["claim_scope"] == ML_CLAIM_SCOPE for row in labels)

    print("PASS: ML risk label derivation is deterministic")


def test_write_ml_outputs_with_baseline_fallback() -> None:
    rows = [
        _row("bus_only", "no_disruption", completion="1.0", censored="0", seed="1"),
        _row("bus_only", "road_loss", completion="0.0", censored="8", seed="2"),
        _row("multimodal", "no_disruption", completion="1.0", censored="0", seed="3"),
        _row("multimodal", "road_loss", completion="0.0", censored="8", seed="4"),
        _row("adaptive", "no_disruption", completion="1.0", censored="0", seed="5"),
        _row("adaptive", "road_loss", completion="0.0", censored="8", seed="6"),
    ]
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        source_results = root / "results.csv"
        source_manifest = root / "manifest.json"
        _write_source_results(source_results, rows)
        source_manifest.write_text('{"row_count": 6}\n', encoding="utf-8")
        result = write_ml_analysis_outputs(
            rows=rows,
            output_dir=root / "analysis",
            source_results_path=source_results,
            source_manifest_path=source_manifest,
            allow_xgboost=False,
            command=("fixture",),
        )
        manifest = json.loads(result["manifest_path"].read_text(encoding="utf-8"))
        predictions = list(
            csv.DictReader(result["predictions_path"].open("r", encoding="utf-8", newline=""))
        )

    assert manifest["model_status"] == "majority_fallback_disabled_by_request"
    assert manifest["label_row_count"] == 6
    assert manifest["prediction_row_count"] == 6
    assert manifest["publication_ready"] is False
    assert manifest["final_study_ready"] is False
    assert manifest["formal_acceptance_evidence"] is False
    assert manifest["leakage_boundary"].startswith("Features are limited")
    assert predictions
    assert all("completion_rate" in row for row in predictions)

    print("PASS: ML output writer records bounded fallback artifacts")


def test_cli_help_renders() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "run_ml_analysis.py"),
            "--help",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "--input" in result.stdout
    assert "--no-xgboost" in result.stdout

    print("PASS: ML analysis CLI help renders")


def test_kmeans_shap_and_nl_summary_artifacts() -> None:
    """KMeans clustering, SHAP (optional), and templated NL summary are emitted."""
    rows = [
        _row("bus_only", "no_disruption", completion="1.0", censored="0", seed="1"),
        _row("bus_only", "no_disruption", completion="1.0", censored="0", seed="2"),
        _row("bus_only", "road_loss", completion="0.2", censored="8", seed="3"),
        _row("bus_only", "road_loss", completion="0.1", censored="9", seed="4"),
        _row("multimodal", "no_disruption", completion="1.0", censored="0", seed="5"),
        _row("multimodal", "no_disruption", completion="1.0", censored="0", seed="6"),
        _row("multimodal", "road_loss", completion="0.3", censored="7", seed="7"),
        _row("multimodal", "road_loss", completion="0.2", censored="8", seed="8"),
        _row("adaptive", "no_disruption", completion="1.0", censored="0", seed="9"),
        _row("adaptive", "road_loss", completion="0.2", censored="8", seed="10"),
    ]
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        source_results = root / "results.csv"
        source_manifest = root / "manifest.json"
        _write_source_results(source_results, rows)
        source_manifest.write_text('{"row_count": 10}\n', encoding="utf-8")
        result = write_ml_analysis_outputs(
            rows=rows,
            output_dir=root / "analysis",
            source_results_path=source_results,
            source_manifest_path=source_manifest,
            allow_xgboost=True,
            command=("fixture",),
        )
        manifest = json.loads(result["manifest_path"].read_text(encoding="utf-8"))
        clusters = list(
            csv.DictReader(result["clusters_path"].open("r", encoding="utf-8", newline=""))
        )
        shap_rows = list(
            csv.DictReader(result["shap_path"].open("r", encoding="utf-8", newline=""))
        )
        predictions = list(
            csv.DictReader(result["predictions_path"].open("r", encoding="utf-8", newline=""))
        )

    assert manifest["kmeans_status"] == "kmeans_fit"
    assert manifest["kmeans_cluster_count"] >= 1
    assert manifest["shap_status"] in {"shap_computed", "missing_shap", "not_available"}
    assert manifest["nl_summary"].startswith("[준실험")
    assert "final_study_ready=false" in manifest["nl_summary"]
    assert clusters, "cluster summary must have rows"
    assert shap_rows, "shap importance CSV must have rows"
    assert all("cluster_id" in row for row in predictions)
    assert any(row["cluster_id"] for row in predictions), "cluster_id must be populated"

    print("PASS: KMeans + SHAP(optional) + NL summary artifacts emitted")


def _row(
    policy: str,
    scenario: str,
    *,
    completion: str,
    censored: str,
    seed: str = "1",
) -> dict[str, str]:
    return {
        "region_id": "fixture_region",
        "graph_source": "fixture_graph",
        "policy_id": policy,
        "scenario_id": scenario,
        "scenario_family": scenario,
        "scenario_type": "fixture",
        "disruption_mode": "fixture",
        "seed": seed,
        "mode": "bus_only" if policy == "bus_only" else "multimodal",
        "completion_rate": completion,
        "censored_count": censored,
        "selected_edge_count": "2",
    }


def _write_source_results(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    test_label_derivation_is_deterministic()
    test_write_ml_outputs_with_baseline_fallback()
    test_cli_help_renders()
    test_kmeans_shap_and_nl_summary_artifacts()
    print("\n=== REALWORLD ML ANALYSIS TESTS PASSED ===")
