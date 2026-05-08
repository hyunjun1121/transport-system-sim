"""Tests for road source-readiness packet generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.road_source_readiness_packet import (  # noqa: E402
    DEFAULT_ROAD_SOURCE_READINESS_MANIFEST_PATH,
    DEFAULT_ROAD_SOURCE_READINESS_PACKET_PATH,
    ROAD_SOURCE_READINESS_COLUMNS,
    ROAD_SOURCE_READINESS_SCOPE,
    build_road_source_readiness_rows,
    write_road_source_readiness_packet,
)


def test_road_source_readiness_rows_classify_current_blockers() -> None:
    """Road source requests should become concrete preflight statuses."""

    with TemporaryDirectory() as directory:
        root = Path(directory)
        speed_manifest = _write_json(root / "speed.json", {"rows_with_observed_maxspeed": 3})
        capacity_manifest = _write_json(root / "capacity.json", {"rows_with_observed_lanes": 0})
        validation_manifest = _write_json(root / "validation.json", {})
        pilot_manifest = _write_json(
            root / "pilot.json",
            {"road_class_overrides_applied": False},
        )
        speed_cache = _touch(root / "speed.csv")
        graph_cache = _touch(root / "road.graphml")

        rows = build_road_source_readiness_rows(
            request_rows=[
                _request(
                    "speed",
                    "public_speed_limit_or_benchmark_source_required",
                    speed_cache,
                    graph_cache,
                    root / "road_class_overrides.csv",
                ),
                _request(
                    "capacity",
                    "traffic_count_or_capacity_reference_required",
                    root / "capacity.csv",
                    graph_cache,
                    root / "road_class_overrides.csv",
                ),
                _request(
                    "override",
                    "reviewed_override_table_and_manifest_application_required",
                    root / "road_class_overrides_draft.csv",
                    "",
                    root / "road_class_overrides.csv",
                ),
            ],
            speed_manifest_path=speed_manifest,
            capacity_manifest_path=capacity_manifest,
            validation_manifest_path=validation_manifest,
            pilot_manifest_path=pilot_manifest,
        )
    by_id = {row["request_id"]: row for row in rows}

    assert by_id["speed"]["readiness_status"] == (
        "needs_human_review_sparse_speed_candidates"
    )
    assert by_id["speed"]["source_url_or_citation"] == "fixture citation for speed"
    assert by_id["speed"]["required_external_input"] == "fixture input for speed"
    assert by_id["capacity"]["readiness_status"] == "blocked_missing_capacity_source"
    assert by_id["override"]["readiness_status"] == (
        "blocked_missing_reviewed_road_class_overrides"
    )
    assert {row["claim_boundary"] for row in rows} == {ROAD_SOURCE_READINESS_SCOPE}
    assert all(row["can_support_road_evidence_gate"] == "false" for row in rows)

    print("PASS: road source-readiness rows classify current blockers")


def test_road_source_readiness_rows_notice_applied_override_manifest() -> None:
    """Reviewed override targets should still require human manifest review."""

    with TemporaryDirectory() as directory:
        root = Path(directory)
        target = _touch(root / "road_class_overrides.csv")
        pilot_manifest = _write_json(
            root / "pilot.json",
            {"road_class_overrides_applied": True},
        )

        rows = build_road_source_readiness_rows(
            request_rows=[
                _request(
                    "override",
                    "reviewed_override_table_and_manifest_application_required",
                    root / "road_class_overrides_draft.csv",
                    "",
                    target,
                ),
            ],
            pilot_manifest_path=pilot_manifest,
        )

    assert rows[0]["readiness_status"] == (
        "needs_human_review_override_application_manifest"
    )
    assert rows[0]["target_output_present"] == "true"

    print("PASS: road source-readiness rows notice applied override manifest")


def test_write_road_source_readiness_packet_outputs_artifacts() -> None:
    """Writer should emit CSV, manifest, and Markdown artifacts."""

    rows = build_road_source_readiness_rows(
        request_rows=[
            _request(
                "benchmark",
                "routing_or_observed_traffic_benchmark_required",
                "data/validation/external_route_benchmarks.csv",
                "data/validation/external_route_benchmarks_osrm.csv",
                "data/parameters/parameter_sources.csv",
            ),
            _request(
                "disruption",
                "hazard_incident_or_reviewed_scenario_source_required",
                "data/scenarios/disruption_scenarios.csv",
                "",
                "data/parameters/road_class_overrides.csv",
            ),
        ],
    )

    with TemporaryDirectory() as directory:
        output = Path(directory) / "road_source_readiness.csv"
        manifest = Path(directory) / "road_source_readiness_manifest.json"
        doc = Path(directory) / "road_source_readiness.md"
        value = write_road_source_readiness_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
            doc_path=doc,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == ROAD_SOURCE_READINESS_COLUMNS
        with manifest.open("r", encoding="utf-8") as handle:
            written_manifest = json.load(handle)
        text = doc.read_text(encoding="utf-8")

        assert len(written_rows) == len(rows)
        assert value["publication_ready"] is False
        assert value["can_mark_complete"] is False
        assert value["source_url_or_citation_present_count"] == len(rows)
        assert value["required_external_input_present_count"] == len(rows)
        assert written_manifest["road_evidence_gate_closure_candidate_count"] == 0
        assert "Road Source Readiness Packet" in text
        assert "fixture citation for benchmark" in text
        assert "fixture input for benchmark" in text

    print("PASS: road source-readiness writer emits artifacts")


def test_shipped_road_source_readiness_packet_matches_current_requests() -> None:
    """Current shipped readiness packet should stay non-accepting."""

    rows = build_road_source_readiness_rows()

    assert DEFAULT_ROAD_SOURCE_READINESS_PACKET_PATH.exists()
    assert DEFAULT_ROAD_SOURCE_READINESS_MANIFEST_PATH.exists()
    with DEFAULT_ROAD_SOURCE_READINESS_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    with DEFAULT_ROAD_SOURCE_READINESS_MANIFEST_PATH.open(
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
    assert manifest["result_scope"] == ROAD_SOURCE_READINESS_SCOPE
    assert manifest["road_evidence_gate_closure_candidate_count"] == 0
    assert manifest["source_url_or_citation_present_count"] == len(rows)
    assert manifest["required_external_input_present_count"] == len(rows)
    assert all(row["source_url_or_citation"] for row in written_rows)
    assert all(row["required_external_input"] for row in written_rows)

    print("PASS: shipped road source-readiness packet matches current requests")


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
        "evidence_fields": "speed",
        "source_type": source_type,
        "source_name": request_id,
        "source_url_or_citation": f"fixture citation for {request_id}",
        "required_external_input": f"fixture input for {request_id}",
        "source_cache_path": str(cache_path),
        "raw_payload_path": str(raw_path),
        "target_output_path": str(target_path),
        "fetch_or_acquisition_command": "fixture fetch",
        "derive_or_review_command": "fixture derive",
        "notes": "fixture",
    }


def _touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("fixture\n", encoding="utf-8")
    return path


def _write_json(path: Path, value: dict[str, object]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


if __name__ == "__main__":
    test_road_source_readiness_rows_classify_current_blockers()
    test_road_source_readiness_rows_notice_applied_override_manifest()
    test_write_road_source_readiness_packet_outputs_artifacts()
    test_shipped_road_source_readiness_packet_matches_current_requests()
    print("\n=== REALWORLD ROAD SOURCE READINESS PACKET TESTS PASSED ===")
