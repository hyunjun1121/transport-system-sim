"""Tests for the pilot seed-stream manifest."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.seed_stream_manifest import (  # noqa: E402
    build_seed_stream_manifest,
    write_seed_stream_manifest,
)


def test_seed_stream_manifest_passes_source_markers() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        paths = _write_source_bundle(root)
        pilot_manifest = root / "pilot_manifest.json"
        _write_pilot_manifest(pilot_manifest)
        manifest = build_seed_stream_manifest(
            pilot_manifest_path=pilot_manifest,
            scenario_source_path=paths["scenario"],
            models_source_path=paths["models"],
            disruptions_source_path=paths["disruptions"],
            dispatch_source_path=paths["dispatch"],
            fleet_source_path=paths["fleet"],
            rail_source_path=paths["rail"],
            transfers_source_path=paths["transfers"],
            traffic_source_path=paths["traffic"],
        )
    assert manifest["blocking_check_count"] == 0
    assert manifest["seed_stream_manifest_ready"] is True
    assert manifest["acceptance_ready"] is False
    assert manifest["stream_record_count"] == 3
    stream_ids = {row["stream_id"] for row in manifest["stream_records"]}
    assert "demand_arrival_lateness" in stream_ids
    assert "road_disruption_sampling" in stream_ids
    assert "dispatch_and_fleet_ordering" in stream_ids


def test_seed_stream_manifest_blocks_missing_failure_marker() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        paths = _write_source_bundle(root)
        paths["scenario"].write_text(
            "np.random.default_rng(seed)\n",
            encoding="utf-8",
        )
        pilot_manifest = root / "pilot_manifest.json"
        _write_pilot_manifest(pilot_manifest)
        manifest = build_seed_stream_manifest(
            pilot_manifest_path=pilot_manifest,
            scenario_source_path=paths["scenario"],
            models_source_path=paths["models"],
            disruptions_source_path=paths["disruptions"],
            dispatch_source_path=paths["dispatch"],
            fleet_source_path=paths["fleet"],
            rail_source_path=paths["rail"],
            transfers_source_path=paths["transfers"],
            traffic_source_path=paths["traffic"],
        )
    by_id = {row["check_id"]: row for row in manifest["marker_checks"]}
    assert by_id["failure_rng_seed_rule"]["status"] == "blocked"
    assert manifest["seed_stream_manifest_ready"] is False


def test_write_seed_stream_manifest_outputs_files() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        paths = _write_source_bundle(root)
        pilot_manifest = root / "pilot_manifest.json"
        _write_pilot_manifest(pilot_manifest)
        summary = write_seed_stream_manifest(
            pilot_manifest_path=pilot_manifest,
            scenario_source_path=paths["scenario"],
            models_source_path=paths["models"],
            disruptions_source_path=paths["disruptions"],
            dispatch_source_path=paths["dispatch"],
            fleet_source_path=paths["fleet"],
            rail_source_path=paths["rail"],
            transfers_source_path=paths["transfers"],
            traffic_source_path=paths["traffic"],
            output_path=root / "seed_stream_manifest.json",
            doc_path=root / "seed_stream_manifest.md",
        )
        loaded = json.loads(
            (root / "seed_stream_manifest.json").read_text(encoding="utf-8")
        )
        doc = (root / "seed_stream_manifest.md").read_text(encoding="utf-8")
    assert loaded["blocking_check_count"] == 0
    assert summary["can_mark_complete"] is False
    assert "Seed Stream Manifest" in doc


def _write_pilot_manifest(path: Path) -> None:
    value = {
        "run_profile": "full_pilot",
        "region_id": "demo_region",
        "graph_source": "cached_graphml:demo.graphml",
        "policy_ids": ["bus_only", "baseline_multimodal"],
        "scenario_ids": ["no_disruption", "blocked"],
        "seeds": [1, 2, 3],
    }
    path.write_text(json.dumps(value), encoding="utf-8")


def _write_source_bundle(root: Path) -> dict[str, Path]:
    paths = {
        "scenario": root / "scenario.py",
        "models": root / "models.py",
        "disruptions": root / "disruptions.py",
        "dispatch": root / "dispatch.py",
        "fleet": root / "fleet.py",
        "rail": root / "rail.py",
        "transfers": root / "transfers.py",
        "traffic": root / "traffic.py",
    }
    paths["scenario"].write_text(
        "np.random.default_rng(seed)\nnp.random.default_rng(seed + 10_000)\n",
        encoding="utf-8",
    )
    paths["models"].write_text("return rng.lognormal(mu, sigma, size=n)\n", encoding="utf-8")
    paths["disruptions"].write_text("if rng.random() < probability:\n", encoding="utf-8")
    for key in ("dispatch", "fleet", "rail", "transfers", "traffic"):
        paths[key].write_text("deterministic = True\n", encoding="utf-8")
    return paths


if __name__ == "__main__":
    test_seed_stream_manifest_passes_source_markers()
    test_seed_stream_manifest_blocks_missing_failure_marker()
    test_write_seed_stream_manifest_outputs_files()
    print("PASS: seed stream manifest")
