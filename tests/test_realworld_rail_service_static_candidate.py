"""Tests for non-formal static rail-service candidate packets."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.rail_service_static_candidate import (  # noqa: E402
    DEFAULT_RAIL_STATIC_CANDIDATE_MANIFEST_PATH,
    DEFAULT_RAIL_STATIC_CANDIDATE_PATH,
    RAIL_STATIC_CANDIDATE_COLUMNS,
    RAIL_STATIC_CANDIDATE_SCOPE,
    build_rail_static_candidate_rows,
    write_rail_static_candidate_packet,
)


def test_static_candidate_rows_combine_headway_and_segment_pair_diagnostic() -> None:
    """Candidate rows should expose timing candidates without gate support."""

    with TemporaryDirectory() as directory:
        root = Path(directory)
        timetable = root / "timetable.csv"
        diagnostic = root / "diagnostic.csv"
        _write_timetable(timetable)
        _write_diagnostic(diagnostic)

        rows = build_rail_static_candidate_rows(
            timetable_cache_path=timetable,
            segment_pair_diagnostic_path=diagnostic,
        )

    assert len(rows) == 1
    row = rows[0]
    assert row["headway_candidate_min"] == "10"
    assert row["travel_time_candidate_min"] == "16.25"
    assert row["capacity_source_class"] == "sensitivity-only"
    assert row["can_support_rail_evidence_gate"] == "false"
    assert row["claim_boundary"] == RAIL_STATIC_CANDIDATE_SCOPE

    print("PASS: static rail candidate combines headway and segment diagnostic")


def test_static_candidate_writer_outputs_fail_closed_manifest() -> None:
    """Writer should emit candidate artifacts and keep formal flags false."""

    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "rail_service_evidence_static_candidate.csv"
        manifest = root / "rail_service_evidence_static_candidate_manifest.json"
        doc = root / "rail_service_evidence_static_candidate.md"
        rows = [
            {
                column: ""
                for column in RAIL_STATIC_CANDIDATE_COLUMNS
            }
        ]
        rows[0].update(
            {
                "candidate_id": "fixture",
                "access_station_name": "Access",
                "egress_station_name": "Egress",
                "headway_candidate_min": "10",
                "travel_time_candidate_min": "16.25",
                "capacity_candidate_pax_per_train": "500",
                "transfer_treatment": "fixture",
                "claim_boundary": RAIL_STATIC_CANDIDATE_SCOPE,
            }
        )

        value = write_rail_static_candidate_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
            doc_path=doc,
            timetable_cache_manifest_path=root / "cache_manifest.json",
            segment_pair_diagnostic_manifest_path=root / "diagnostic_manifest.json",
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == RAIL_STATIC_CANDIDATE_COLUMNS
        written_manifest = json.loads(manifest.read_text(encoding="utf-8"))
        text = doc.read_text(encoding="utf-8")

        assert len(written_rows) == 1
        assert value["publication_ready"] is False
        assert value["final_study_ready"] is False
        assert value["can_support_rail_evidence_gate"] is False
        assert written_manifest["rail_service_evidence_written"] is False
        assert "Rail Service Static Timetable Candidate" in text

    print("PASS: static rail candidate writer emits fail-closed manifest")


def test_shipped_static_candidate_matches_current_artifacts() -> None:
    """Shipped candidate should be present and remain non-formal."""

    assert DEFAULT_RAIL_STATIC_CANDIDATE_PATH.exists()
    assert DEFAULT_RAIL_STATIC_CANDIDATE_MANIFEST_PATH.exists()

    rows = build_rail_static_candidate_rows()
    with DEFAULT_RAIL_STATIC_CANDIDATE_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    manifest = json.loads(
        DEFAULT_RAIL_STATIC_CANDIDATE_MANIFEST_PATH.read_text(encoding="utf-8")
    )

    assert len(written_rows) == len(rows) == 1
    assert manifest["row_count"] == 1
    assert manifest["formal_target_path"] == "data/parameters/rail_service_evidence.csv"
    assert manifest["formal_target_written"] is False
    assert manifest["publication_ready"] is False
    assert manifest["source_provenance_accepted"] is False
    assert float(written_rows[0]["headway_candidate_min"]) > 0.0
    assert float(written_rows[0]["travel_time_candidate_min"]) > 0.0

    print("PASS: shipped static rail candidate remains non-formal")


def _write_timetable(path: Path) -> None:
    rows = [
        _event("T1", "08:00:00"),
        _event("T2", "08:10:00"),
        _event("T3", "08:20:00"),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "trip_id",
                "station_role",
                "station_name",
                "station_code",
                "event_time",
                "event_type",
                "direction",
                "service_day",
            ),
        )
        writer.writeheader()
        writer.writerows(rows)


def _event(trip_id: str, event_time: str) -> dict[str, str]:
    return {
        "trip_id": trip_id,
        "station_role": "access",
        "station_name": "올림픽공원",
        "station_code": "4136",
        "event_time": event_time,
        "event_type": "departure",
        "direction": "UP",
        "service_day": "DAY",
    }


def _write_diagnostic(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "row_type",
                "segment_id",
                "destination_station_name",
                "median_total_minutes",
            ),
        )
        writer.writeheader()
        writer.writerow(
            {
                "row_type": "segment_pair_with_assumed_transfer_buffer",
                "segment_id": "fixture_pair",
                "destination_station_name": "잠실",
                "median_total_minutes": "16.25",
            }
        )


if __name__ == "__main__":
    test_static_candidate_rows_combine_headway_and_segment_pair_diagnostic()
    test_static_candidate_writer_outputs_fail_closed_manifest()
    test_shipped_static_candidate_matches_current_artifacts()
    print("\n=== REALWORLD RAIL SERVICE STATIC CANDIDATE TESTS PASSED ===")
