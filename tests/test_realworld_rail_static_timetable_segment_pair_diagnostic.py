"""Tests for static timetable segment-pair diagnostics."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.rail_static_timetable_segment_pair_diagnostic import (  # noqa: E402
    CLAIM_BOUNDARY,
    DEFAULT_DIAGNOSTIC_CSV_PATH,
    DEFAULT_DIAGNOSTIC_MANIFEST_PATH,
    DEFAULT_STATIC_TIMETABLE_SOURCE_PATH,
    build_static_timetable_segment_pair_diagnostic,
    write_static_timetable_segment_pair_diagnostic,
)
from src.realworld.source_artifacts import file_sha256  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]


def test_static_timetable_segment_pair_diagnostic_fixture() -> None:
    """Fixture source should produce segment rows and an explicitly non-evidence manifest."""

    with TemporaryDirectory(dir=ROOT) as directory:
        root = Path(directory)
        source = root / "static_source.csv"
        output = root / "diagnostic.csv"
        manifest = root / "diagnostic_manifest.json"
        doc = root / "diagnostic.md"
        _write_fixture_source(source)

        value = write_static_timetable_segment_pair_diagnostic(
            source_path=source,
            output_path=output,
            manifest_path=manifest,
            doc_path=doc,
            assumed_transfer_buffer_min=5.0,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        written_manifest = json.loads(manifest.read_text(encoding="utf-8"))
        text = doc.read_text(encoding="utf-8")

        assert len(rows) == 3
        by_id = {row["segment_id"]: row for row in rows}
        assert by_id["line9_olympic_park_to_seokchon"]["median_segment_minutes"] == "6"
        assert by_id["line8_seokchon_to_jamsil"]["median_segment_minutes"] == "2"
        pair = by_id["line9_olympic_park_to_seokchon+line8_seokchon_to_jamsil"]
        assert pair["feasible_connection_count"] == "3"
        assert pair["median_total_minutes"] == "14"
        assert value["source_sha256"] == file_sha256(source)
        assert written_manifest["publication_ready"] is False
        assert written_manifest["final_study_ready"] is False
        assert written_manifest["formal_acceptance_evidence"] is False
        assert written_manifest["can_support_rail_evidence_gate"] is False
        assert written_manifest["can_support_transfer_evidence_gate"] is False
        assert CLAIM_BOUNDARY in text

    print("PASS: static timetable segment-pair diagnostic fixture is bounded")


def test_static_timetable_segment_pair_diagnostic_builder_exposes_current_source() -> None:
    """Current retained source should support a diagnostic without creating rail evidence."""

    rows, manifest = build_static_timetable_segment_pair_diagnostic(
        DEFAULT_STATIC_TIMETABLE_SOURCE_PATH,
        assumed_transfer_buffer_min=5.0,
    )
    by_id = {row["segment_id"]: row for row in rows}

    assert manifest["diagnostic_only"] is True
    assert manifest["publication_ready"] is False
    assert manifest["final_study_ready"] is False
    assert manifest["can_support_rail_evidence_gate"] is False
    assert manifest["source_sha256"] == file_sha256(DEFAULT_STATIC_TIMETABLE_SOURCE_PATH)
    assert by_id["line9_olympic_park_to_seokchon"]["matched_trip_count"] == "241"
    assert by_id["line8_seokchon_to_jamsil"]["matched_trip_count"] == "160"
    assert int(by_id[
        "line9_olympic_park_to_seokchon+line8_seokchon_to_jamsil"
    ]["feasible_connection_count"]) > 0

    print("PASS: static timetable segment-pair builder exposes current source")


def test_shipped_static_timetable_segment_pair_diagnostic_matches_current_source() -> None:
    """Shipped diagnostic artifact should remain non-evidence and source-hash aligned."""

    assert DEFAULT_DIAGNOSTIC_CSV_PATH.exists()
    assert DEFAULT_DIAGNOSTIC_MANIFEST_PATH.exists()
    with DEFAULT_DIAGNOSTIC_CSV_PATH.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    manifest = json.loads(DEFAULT_DIAGNOSTIC_MANIFEST_PATH.read_text(encoding="utf-8"))

    assert len(rows) == 3
    assert manifest["source_sha256"] == file_sha256(DEFAULT_STATIC_TIMETABLE_SOURCE_PATH)
    assert manifest["publication_ready"] is False
    assert manifest["final_study_ready"] is False
    assert manifest["formal_acceptance_evidence"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["can_support_rail_evidence_gate"] is False
    assert manifest["can_support_transfer_evidence_gate"] is False
    assert manifest["feasible_connection_count"] > 0
    assert "does not validate rail capacity" in " ".join(manifest["remaining_blockers"])

    print("PASS: shipped static timetable segment-pair diagnostic remains non-evidence")


def _write_fixture_source(path: Path) -> None:
    fieldnames = (
        "ROWNUM",
        "LINE",
        "SI_ID",
        "STATION_NM",
        "WEEKTAG",
        "INOUTTAG",
        "GUBHANG",
        "TRAIN_NO",
        "STT",
        "EDT",
        "ST_STT_NM",
        "ED_STT_NM",
    )
    rows: list[dict[str, str]] = []
    rownum = 1
    for index, minute in enumerate((0, 10, 20), start=1):
        train = f"L9{index}"
        rows.append(_row(rownum, "9", "4136", "올림픽공원", "DOWN", train, f"08:{minute:02d}:00", f"08:{minute:02d}:00"))
        rownum += 1
        rows.append(_row(rownum, "9", "4133", "석촌", "DOWN", train, f"08:{minute + 6:02d}:00", f"08:{minute + 6:02d}:30"))
        rownum += 1
        train = f"L8{index}"
        rows.append(_row(rownum, "8", "2816", "석촌", "UP", train, f"08:{minute + 12:02d}:00", f"08:{minute + 12:02d}:00"))
        rownum += 1
        rows.append(_row(rownum, "8", "2815", "잠실", "UP", train, f"08:{minute + 14:02d}:00", f"08:{minute + 14:02d}:30"))
        rownum += 1
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _row(
    rownum: int,
    line: str,
    station_id: str,
    station_name: str,
    direction: str,
    train_no: str,
    stt: str,
    edt: str,
) -> dict[str, str]:
    return {
        "ROWNUM": str(rownum),
        "LINE": line,
        "SI_ID": station_id,
        "STATION_NM": station_name,
        "WEEKTAG": "DAY",
        "INOUTTAG": direction,
        "GUBHANG": "0",
        "TRAIN_NO": train_no,
        "STT": stt,
        "EDT": edt,
        "ST_STT_NM": "fixture",
        "ED_STT_NM": "fixture",
    }


if __name__ == "__main__":
    test_static_timetable_segment_pair_diagnostic_fixture()
    test_static_timetable_segment_pair_diagnostic_builder_exposes_current_source()
    test_shipped_static_timetable_segment_pair_diagnostic_matches_current_source()
    print("\n=== REALWORLD RAIL STATIC TIMETABLE SEGMENT-PAIR DIAGNOSTIC TESTS PASSED ===")
