"""Tests for rail/transit stress-profile review packet."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.rail_transit_stress_profile_packet import (  # noqa: E402
    DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_MANIFEST_PATH,
    DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_PACKET_PATH,
    RAIL_TRANSIT_STRESS_PROFILE_COLUMNS,
    RAIL_TRANSIT_STRESS_PROFILE_SCOPE,
    REQUIRED_STRESS_CLASSES,
    build_rail_transit_stress_profile_rows,
    build_rail_transit_stress_profile_manifest,
    write_rail_transit_stress_profile_packet,
)


def test_stress_profile_rows_cover_required_phase4_classes() -> None:
    """Current rail/transit stress profile should cover Phase 4 stress classes."""

    rows = build_rail_transit_stress_profile_rows()
    by_class = {row["stress_class"]: row for row in rows}

    assert set(REQUIRED_STRESS_CLASSES).issubset(by_class)
    assert len(rows) == len(REQUIRED_STRESS_CLASSES)
    assert {row["publication_ready"] for row in rows} == {"false"}
    assert {row["can_support_rail_evidence_gate"] for row in rows} == {"false"}
    assert {row["can_support_acceptance_gate"] for row in rows} == {"false"}
    assert {row["claim_boundary"] for row in rows} == {
        RAIL_TRANSIT_STRESS_PROFILE_SCOPE
    }
    assert by_class["increased_headway"][
        "scenario_or_policy_id"
    ] == "rail_delay_or_partial_unavailability"
    assert by_class["partial_capacity_reduction"][
        "source_treatment"
    ] == "sensitivity_only"
    assert by_class["station_processing_delay_proxy"][
        "implementation_status"
    ] == "represented_by_transfer_sensitivity"

    print("PASS: rail/transit stress rows cover required Phase 4 classes")


def test_station_access_profile_is_not_rail_service_outage() -> None:
    """Station-access row must stay framed as road/connector degradation."""

    rows = build_rail_transit_stress_profile_rows()
    station_access = {
        row["stress_class"]: row for row in rows
    }["rail_access_egress_degradation"]

    assert station_access["runtime_hook_type"] == "road_connector_degradation"
    assert station_access["linked_artifact_key"] == "songpa_rail_station_access"
    assert "not a rail-service outage model" in station_access["notes"]
    assert station_access["evidence_status"] == (
        "scenario_only_station_access_road_stress"
    )

    print("PASS: station-access stress is not labeled rail-service outage")


def test_writer_outputs_non_acceptance_manifest_and_doc() -> None:
    """Writer should emit stable CSV, manifest, and Markdown review aid."""

    rows = build_rail_transit_stress_profile_rows()
    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "rail_transit_stress.csv"
        manifest_path = root / "rail_transit_stress_manifest.json"
        doc_path = root / "rail_transit_stress.md"
        manifest = write_rail_transit_stress_profile_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == (
                RAIL_TRANSIT_STRESS_PROFILE_COLUMNS
            )
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        doc_text = doc_path.read_text(encoding="utf-8")

    assert len(written_rows) == len(rows)
    assert manifest["publication_ready"] is False
    assert manifest["final_study_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["can_support_publication_gate"] is False
    assert manifest["can_support_final_study_gate"] is False
    assert manifest["can_support_rail_evidence_gate"] is False
    assert manifest["can_support_acceptance_gate"] is False
    assert manifest["formal_acceptance_evidence"] is False
    assert manifest["required_stress_classes_present"] is True
    assert written_manifest["row_count"] == len(rows)
    assert "Rail Transit Stress Profile Packet" in doc_text
    assert "not publication readiness" in doc_text
    assert "not final-study readiness" in doc_text
    assert "not formal acceptance" in doc_text
    assert "Stress-profile rows populated for coverage taxonomy only" in doc_text
    assert "does not certify rail timing" in doc_text

    print("PASS: rail/transit stress writer emits non-acceptance artifacts")


def test_stress_profile_manifest_blocks_missing_runtime_hook_and_bad_link() -> None:
    """Stress profile manifest should expose broken runtime hooks and linked keys."""

    rows = [dict(row) for row in build_rail_transit_stress_profile_rows()]
    for row in rows:
        if row["stress_class"] == "station_processing_delay_proxy":
            row["implementation_status"] = "missing_runtime_hook"
            row["linked_artifact_key"] = (
                "transfer_fixed_delay;missing_transfer_parameter"
            )
    with TemporaryDirectory() as directory:
        root = Path(directory)
        manifest = build_rail_transit_stress_profile_manifest(
            rows=rows,
            output_path=root / "rail_transit_stress.csv",
            manifest_path=root / "rail_transit_stress_manifest.json",
            doc_path=root / "rail_transit_stress.md",
        )

    assert manifest["missing_runtime_hook_count"] == 1
    assert manifest["unresolved_linked_artifact_count"] >= 1
    assert manifest["publication_ready"] is False
    assert manifest["final_study_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["can_support_publication_gate"] is False
    assert manifest["can_support_final_study_gate"] is False
    assert manifest["can_support_rail_evidence_gate"] is False
    assert manifest["can_support_acceptance_gate"] is False
    assert manifest["formal_acceptance_evidence"] is False
    assert any("missing runtime hook" in item for item in manifest["remaining_blockers"])
    assert any(
        "missing_transfer_parameter" in item
        for item in manifest["remaining_blockers"]
    )

    print("PASS: stress-profile manifest blocks missing runtime hooks and bad links")


def test_shipped_stress_profile_packet_matches_current_outputs() -> None:
    """Committed stress profile packet should match current generated rows."""

    rows = build_rail_transit_stress_profile_rows()

    assert DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_PACKET_PATH.exists()
    assert DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_MANIFEST_PATH.exists()
    with DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_PACKET_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    manifest = json.loads(
        DEFAULT_RAIL_TRANSIT_STRESS_PROFILE_MANIFEST_PATH.read_text(
            encoding="utf-8"
        )
    )

    assert written_rows == rows
    assert manifest["row_count"] == len(rows)
    assert manifest["publication_ready"] is False
    assert manifest["final_study_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["can_support_publication_gate"] is False
    assert manifest["can_support_final_study_gate"] is False
    assert manifest["can_support_rail_evidence_gate"] is False
    assert manifest["can_support_acceptance_gate"] is False
    assert manifest["formal_acceptance_evidence"] is False
    assert manifest["required_stress_classes_present"] is True
    assert manifest["missing_runtime_hook_count"] == 0
    assert manifest["unresolved_linked_artifact_count"] == 0
    assert manifest["rail_source_decision_blocker_count"] >= 1

    print("PASS: shipped rail/transit stress profile matches current outputs")


if __name__ == "__main__":
    test_stress_profile_rows_cover_required_phase4_classes()
    test_station_access_profile_is_not_rail_service_outage()
    test_writer_outputs_non_acceptance_manifest_and_doc()
    test_stress_profile_manifest_blocks_missing_runtime_hook_and_bad_link()
    test_shipped_stress_profile_packet_matches_current_outputs()
    print("\n=== REALWORLD RAIL TRANSIT STRESS PROFILE TESTS PASSED ===")
