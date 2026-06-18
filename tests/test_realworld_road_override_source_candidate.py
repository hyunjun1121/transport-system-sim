"""Tests for road-class override source-candidate packets."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.road_override_source_candidate import (  # noqa: E402
    DEFAULT_ROAD_OVERRIDE_SOURCE_CANDIDATE_MANIFEST_PATH,
    DEFAULT_ROAD_OVERRIDE_SOURCE_CANDIDATE_PATH,
    FORMAL_ROAD_CLASS_OVERRIDE_PATH,
    ROAD_OVERRIDE_SOURCE_CANDIDATE_COLUMNS,
    ROAD_OVERRIDE_SOURCE_CANDIDATE_SCOPE,
    build_road_override_source_candidate_rows,
    write_road_override_source_candidate_packet,
)


def test_source_candidate_rows_remain_non_acceptance() -> None:
    """Candidate rows should strengthen review triage without closing gates."""

    with TemporaryDirectory() as directory:
        draft = Path(directory) / "road_class_overrides_draft.csv"
        _write_draft(draft)

        rows = build_road_override_source_candidate_rows(draft)

    assert len(rows) == 1
    row = rows[0]
    assert row["highway"] == "residential"
    assert row["speed_candidate_source_class"] == "public-data-derived"
    assert row["capacity_candidate_source_class"] == "literature-derived"
    assert row["base_p_fail_candidate_source_class"] == "sensitivity-only"
    assert row["can_support_formal_override"] == "false"
    assert row["can_support_publication_gate"] == "false"
    assert row["claim_boundary"] == ROAD_OVERRIDE_SOURCE_CANDIDATE_SCOPE

    print("PASS: source-candidate rows remain non-acceptance")


def test_source_candidate_writer_outputs_fail_closed_manifest() -> None:
    """Writer should emit artifacts while preserving false readiness flags."""

    with TemporaryDirectory() as directory:
        root = Path(directory)
        draft = root / "road_class_overrides_draft.csv"
        output = root / "road_class_override_source_candidate.csv"
        manifest = root / "road_class_override_source_candidate_manifest.json"
        doc = root / "road_class_override_source_candidate.md"
        formal = root / "road_class_overrides.csv"
        _write_draft(draft)

        rows = build_road_override_source_candidate_rows(draft)
        value = write_road_override_source_candidate_packet(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
            doc_path=doc,
            draft_path=draft,
        )

        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == ROAD_OVERRIDE_SOURCE_CANDIDATE_COLUMNS
        written_manifest = json.loads(manifest.read_text(encoding="utf-8"))
        text = doc.read_text(encoding="utf-8")

        assert len(written_rows) == 1
        assert value["publication_ready"] is False
        assert value["final_study_ready"] is False
        assert value["formal_acceptance_evidence"] is False
        assert value["formal_target_written"] is False
        assert written_manifest["can_mark_complete"] is False
        assert "Road Class Override Source Candidate" in text
        assert not formal.exists()

    print("PASS: source-candidate writer outputs fail-closed manifest")


def test_shipped_source_candidate_matches_current_draft() -> None:
    """Generated candidate packet should track the shipped draft worksheet."""

    assert DEFAULT_ROAD_OVERRIDE_SOURCE_CANDIDATE_PATH.exists()
    assert DEFAULT_ROAD_OVERRIDE_SOURCE_CANDIDATE_MANIFEST_PATH.exists()
    assert not FORMAL_ROAD_CLASS_OVERRIDE_PATH.exists()

    rows = build_road_override_source_candidate_rows()
    with DEFAULT_ROAD_OVERRIDE_SOURCE_CANDIDATE_PATH.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        written_rows = list(csv.DictReader(handle))
    manifest = json.loads(
        DEFAULT_ROAD_OVERRIDE_SOURCE_CANDIDATE_MANIFEST_PATH.read_text(
            encoding="utf-8"
        )
    )

    assert len(written_rows) == len(rows)
    assert manifest["row_count"] == len(rows)
    assert manifest["publication_ready"] is False
    assert manifest["final_study_ready"] is False
    assert manifest["formal_target_written"] is False
    assert manifest["formal_target_path"] == "data/parameters/road_class_overrides.csv"
    assert manifest["field_source_class_counts"]["base_p_fail_candidate_source_class"] == {
        "sensitivity-only": len(rows)
    }

    print("PASS: shipped source-candidate packet matches current draft")


def _write_draft(path: Path) -> None:
    row = {
        "highway": "residential",
        "speed_kph": "30",
        "capacity_veh_per_hr": "400",
        "base_p_fail": "0.04",
        "source_class": "expert assumption",
        "source_name": "draft mapper default pending road-evidence review",
        "source_url_or_citation": "src/realworld/attributes.py",
        "notes": "draft only",
        "speed_source_class": "expert assumption",
        "speed_source_name": "draft mapper speed default pending road-evidence review",
        "speed_source_url_or_citation": "src/realworld/attributes.py",
        "capacity_source_class": "expert assumption",
        "capacity_source_name": "draft mapper capacity default pending road-evidence review",
        "capacity_source_url_or_citation": "src/realworld/attributes.py",
        "base_p_fail_source_class": "sensitivity-only",
        "base_p_fail_source_name": "draft mapper base-disruption scenario proxy",
        "base_p_fail_source_url_or_citation": "src/realworld/attributes.py",
        "review_priority": "high",
        "routeable_edge_count": "12",
        "routeable_length_km": "1.2",
        "routeable_length_share": "0.5",
        "maxspeed_parseable_rate": "0",
        "capacity_explicit_rate": "0",
        "base_disruption_explicit_rate": "0",
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(row))
        writer.writeheader()
        writer.writerow(row)


if __name__ == "__main__":
    test_source_candidate_rows_remain_non_acceptance()
    test_source_candidate_writer_outputs_fail_closed_manifest()
    test_shipped_source_candidate_matches_current_draft()
    print("\n=== REALWORLD ROAD OVERRIDE SOURCE CANDIDATE TESTS PASSED ===")
