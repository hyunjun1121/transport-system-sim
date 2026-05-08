"""Tests for parameter source-readiness packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.parameter_source_readiness_packet import (  # noqa: E402
    DEFAULT_PARAMETER_SOURCE_READINESS_MANIFEST_PATH,
    DEFAULT_PARAMETER_SOURCE_READINESS_PACKET_PATH,
    PARAMETER_SOURCE_READINESS_COLUMNS,
    PARAMETER_SOURCE_READINESS_SCOPE,
    build_parameter_source_readiness_rows,
    write_parameter_source_readiness_packet,
)


def test_parameter_source_readiness_rows_classify_blockers() -> None:
    """Parameter source requests should become concrete preflight statuses."""

    with TemporaryDirectory() as directory:
        root = Path(directory)
        scenario = _touch(root / "sensitivity_design.csv")
        target = _touch(root / "parameter_sources.csv")

        rows = build_parameter_source_readiness_rows(
            request_rows=[
                _request(
                    "demand",
                    "planning_scenario_or_literature_source_required",
                    scenario,
                    "",
                    target,
                ),
                _request(
                    "transfer",
                    "station_layout_or_pedestrian_flow_source_required",
                    target,
                    "",
                    target,
                ),
                _request(
                    "traffic",
                    "traffic_benchmark_or_literature_calibration_required",
                    root / "benchmarks.csv",
                    root / "osrm.csv",
                    target,
                ),
            ]
        )
    by_id = {row["request_id"]: row for row in rows}

    assert by_id["demand"]["readiness_status"] == (
        "needs_human_review_demand_scenario"
    )
    assert by_id["demand"]["source_url_or_citation"] == (
        "fixture citation for demand"
    )
    assert by_id["demand"]["required_external_input"] == "fixture input for demand"
    assert by_id["transfer"]["readiness_status"] == "blocked_missing_transfer_source"
    assert by_id["traffic"]["readiness_status"] == "blocked_missing_traffic_bpr_source"
    assert {row["claim_boundary"] for row in rows} == {
        PARAMETER_SOURCE_READINESS_SCOPE
    }
    assert all(row["can_support_parameter_evidence_gate"] == "false" for row in rows)

    print("PASS: parameter source-readiness rows classify blockers")


def test_parameter_source_readiness_rows_notice_benchmark_snapshot() -> None:
    """Traffic/BPR rows should expose benchmark snapshots for human review."""

    with TemporaryDirectory() as directory:
        root = Path(directory)
        cache = _touch(root / "benchmarks.csv")
        raw = _touch(root / "osrm.csv")
        target = _touch(root / "parameter_sources.csv")

        rows = build_parameter_source_readiness_rows(
            request_rows=[
                _request(
                    "traffic",
                    "traffic_benchmark_or_literature_calibration_required",
                    cache,
                    raw,
                    target,
                ),
            ]
        )

    assert rows[0]["readiness_status"] == (
        "needs_human_review_traffic_bpr_with_benchmark_snapshot"
    )
    assert rows[0]["raw_payload_present"] == "true"

    print("PASS: parameter source-readiness rows notice benchmark snapshot")


def test_write_parameter_source_readiness_packet_outputs_artifacts() -> None:
    """Writer should emit CSV, manifest, and Markdown artifacts."""

    rows = build_parameter_source_readiness_rows(
        request_rows=[
            _request(
                "fleet",
                "agency_fleet_roster_or_planning_source_required",
                "data/parameters/fleet_assumptions.csv",
                "",
                "data/parameters/fleet_assumptions.csv; data/parameters/parameter_sources.csv",
            ),
            _request(
                "disruption",
                "hazard_incident_or_scenario_rule_source_required",
                "data/scenarios/disruption_scenarios.csv",
                "data/validation/accessibility_loss_summary.md",
                "data/scenarios/disruption_scenarios.csv; data/parameters/parameter_sources.csv",
            ),
        ]
    )

    with TemporaryDirectory() as directory:
        output = Path(directory) / "parameter_source_readiness.csv"
        manifest = Path(directory) / "parameter_source_readiness_manifest.json"
        doc = Path(directory) / "parameter_source_readiness.md"
        value = write_parameter_source_readiness_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
            doc_path=doc,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == PARAMETER_SOURCE_READINESS_COLUMNS
        with manifest.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)
        text = doc.read_text(encoding="utf-8")

        assert len(written_rows) == len(rows)
        assert value["publication_ready"] is False
        assert value["can_mark_complete"] is False
        assert value["source_url_or_citation_present_count"] == len(rows)
        assert value["required_external_input_present_count"] == len(rows)
        assert written_manifest["parameter_evidence_gate_closure_candidate_count"] == 0
        assert "Parameter Source Readiness Packet" in text
        assert "fixture citation for fleet" in text
        assert "fixture input for fleet" in text

    print("PASS: parameter source-readiness writer emits artifacts")


def test_shipped_parameter_source_readiness_packet_matches_current_requests() -> None:
    """Current shipped readiness packet should stay non-accepting."""

    rows = build_parameter_source_readiness_rows()

    assert DEFAULT_PARAMETER_SOURCE_READINESS_PACKET_PATH.exists()
    assert DEFAULT_PARAMETER_SOURCE_READINESS_MANIFEST_PATH.exists()
    with DEFAULT_PARAMETER_SOURCE_READINESS_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    with DEFAULT_PARAMETER_SOURCE_READINESS_MANIFEST_PATH.open(
        "r",
        encoding="utf-8",
    ) as handle:
        manifest = json.load(handle)

    assert len(written_rows) == len(rows)
    assert [row["request_id"] for row in written_rows] == [
        row["request_id"] for row in rows
    ]
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["result_scope"] == PARAMETER_SOURCE_READINESS_SCOPE
    assert manifest["parameter_evidence_gate_closure_candidate_count"] == 0
    assert manifest["source_url_or_citation_present_count"] == len(rows)
    assert manifest["required_external_input_present_count"] == len(rows)
    assert all(row["source_url_or_citation"] for row in written_rows)
    assert all(row["required_external_input"] for row in written_rows)

    print("PASS: shipped parameter source-readiness packet matches current requests")


def _request(
    request_id: str,
    source_type: str,
    cache_path: str | Path,
    raw_path: str | Path,
    target_path: str | Path,
) -> dict[str, str]:
    return {
        "request_id": request_id,
        "region_id": "songpa_public_demo",
        "parameter_groups": "fixture",
        "covered_parameters": "parameter_a;parameter_b",
        "weak_parameter_count": "2",
        "source_type": source_type,
        "source_name": request_id,
        "source_url_or_citation": f"fixture citation for {request_id}",
        "required_external_input": f"fixture input for {request_id}",
        "source_cache_path": str(cache_path),
        "raw_payload_path": str(raw_path),
        "target_output_path": str(target_path),
        "acquisition_command": "fixture acquisition",
        "review_or_derivation_command": "fixture review",
        "notes": "fixture",
    }


def _touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("fixture\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    test_parameter_source_readiness_rows_classify_blockers()
    test_parameter_source_readiness_rows_notice_benchmark_snapshot()
    test_write_parameter_source_readiness_packet_outputs_artifacts()
    test_shipped_parameter_source_readiness_packet_matches_current_requests()
    print("\n=== REALWORLD PARAMETER SOURCE READINESS PACKET TESTS PASSED ===")
