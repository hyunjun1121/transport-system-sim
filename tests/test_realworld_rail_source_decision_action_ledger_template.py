"""Tests for rail source-decision action-ledger template generation."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.write_rail_source_decision_action_ledger_template import (  # noqa: E402
    main as write_action_ledger_template_main,
)
from src.realworld.rail_source_decision_packet import (  # noqa: E402
    DEFAULT_RAIL_SOURCE_DECISION_PACKET_PATH,
    RAIL_SOURCE_DECISION_ACTION_COLUMNS,
    apply_rail_source_decision_action_ledger,
    build_rail_source_decision_action_ledger_template_rows,
    build_rail_source_decision_rows,
    write_rail_source_decision_action_ledger_template,
)


PROTECTED_FIELDS = {
    "decision_status",
    "blocking_reason",
    "source_cache_present",
    "can_support_timing_fields_after_review",
    "can_support_rail_evidence_gate",
    "can_support_acceptance_gate",
    "claim_boundary",
}


def test_action_ledger_template_rows_are_pending_and_header_safe() -> None:
    """Generated template rows should expose only safe action-ledger columns."""

    source_rows = build_rail_source_decision_rows()
    template_rows = build_rail_source_decision_action_ledger_template_rows(source_rows)

    assert len(template_rows) == len(source_rows)
    assert all(tuple(row.keys()) == RAIL_SOURCE_DECISION_ACTION_COLUMNS for row in template_rows)
    assert all(row["request_id"] for row in template_rows)
    assert {row["decision_choice"] for row in template_rows} == {
        "pending_reviewer_decision"
    }
    for row in template_rows:
        assert PROTECTED_FIELDS.isdisjoint(row.keys())
        assert row["reviewer"] == ""
        assert row["decision_date"] == ""
        assert row["decision_basis"] == ""
        assert row["artifact_sha256s"] == ""
        assert row["excluded_or_retained_claim_scope"] == ""
        assert row["not_operational_claim_boundary"] == ""
        assert row["bounded_treatment_or_exclusion_rationale"] == ""

    print("PASS: rail source-decision action-ledger template rows are safe")


def test_action_ledger_template_writes_non_acceptance_artifacts() -> None:
    """Template writer should emit separate non-acceptance CSV/manifest/doc."""

    rows = build_rail_source_decision_rows()
    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "rail_source_decision_action_ledger_template.csv"
        manifest_path = root / "template_manifest.json"
        doc_path = root / "template.md"
        manifest = write_rail_source_decision_action_ledger_template(
            rows=rows,
            output_path=output,
            manifest_path=manifest_path,
            doc_path=doc_path,
        )
        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            fieldnames = tuple(reader.fieldnames or ())
        written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        doc_text = doc_path.read_text(encoding="utf-8")

    assert fieldnames == RAIL_SOURCE_DECISION_ACTION_COLUMNS
    assert len(written_rows) == len(rows)
    assert "rail_source_decision_packet.csv" not in manifest["outputs"]["csv"]
    assert manifest["template_only"] is True
    assert manifest["ledger_compatible"] is True
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["can_support_rail_evidence_gate"] is False
    assert manifest["can_support_final_study_gate"] is False
    assert manifest["can_support_acceptance_gate"] is False
    assert written_manifest["result_scope"] == (
        "rail_source_decision_action_ledger_template_not_acceptance"
    )
    assert "Template only" in doc_text
    assert "not a formal decision record" in doc_text
    assert "Non-Formal Example Rows" in doc_text
    assert "retain_capacity_as_sensitivity_only_with_bounds" in doc_text
    assert "record_scenario_only_availability_scope" in doc_text
    assert "Source-backed acquisition examples are intentionally omitted" in doc_text
    assert {row["decision_choice"] for row in written_rows} == {
        "pending_reviewer_decision"
    }
    assert all(row["reviewer"] == "" for row in written_rows)

    print("PASS: rail source-decision action-ledger template writes artifacts")


def test_action_ledger_template_round_trip_keeps_decisions_pending() -> None:
    """Using the blank template as --action-ledger should not complete decisions."""

    rows = build_rail_source_decision_rows()
    template_rows = build_rail_source_decision_action_ledger_template_rows(rows)
    merged = apply_rail_source_decision_action_ledger(
        rows,
        action_rows=template_rows,
    )

    assert {
        row["decision_status"] for row in merged
    } == {
        "blocked_missing_rail_source_decision",
        "needs_human_review_rail_source_decision",
        "needs_human_review_ready_rail_source_decision",
    }
    assert all(row["decision_choice"] == "pending_reviewer_decision" for row in merged)

    print("PASS: blank action-ledger template keeps source decisions pending")


def test_action_ledger_template_cli_uses_separate_paths() -> None:
    """CLI should write template files without touching the decision packet path."""

    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "template.csv"
        manifest_path = root / "manifest.json"
        doc_path = root / "template.md"
        exit_code = write_action_ledger_template_main(
            [
                "--output",
                str(output),
                "--manifest",
                str(manifest_path),
                "--doc",
                str(doc_path),
            ]
        )
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            fieldnames = tuple(reader.fieldnames or ())
            written_rows = list(reader)

    assert exit_code == 0
    assert fieldnames == RAIL_SOURCE_DECISION_ACTION_COLUMNS
    assert len(written_rows) == 6
    assert manifest["outputs"]["csv"] != DEFAULT_RAIL_SOURCE_DECISION_PACKET_PATH.as_posix()
    assert manifest["template_action_status_counts"] == {
        "pending_action_decision": 6
    }

    print("PASS: rail source-decision action-ledger template CLI uses separate paths")


if __name__ == "__main__":
    test_action_ledger_template_rows_are_pending_and_header_safe()
    test_action_ledger_template_writes_non_acceptance_artifacts()
    test_action_ledger_template_round_trip_keeps_decisions_pending()
    test_action_ledger_template_cli_uses_separate_paths()
    print("\n=== REALWORLD RAIL SOURCE DECISION ACTION LEDGER TEMPLATE TESTS PASSED ===")
