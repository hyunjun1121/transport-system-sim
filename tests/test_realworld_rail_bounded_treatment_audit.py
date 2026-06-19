"""Tests for rail bounded-treatment consistency audit."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.rail_bounded_treatment_audit import (  # noqa: E402
    DEFAULT_RAIL_BOUNDED_TREATMENT_AUDIT_PATH,
    AVAILABILITY_REQUEST_ID,
    CAPACITY_REQUEST_ID,
    build_rail_bounded_treatment_audit,
    write_rail_bounded_treatment_audit,
)
from src.realworld.rail_source_decision_packet import (  # noqa: E402
    build_rail_source_decision_rows,
)
from src.realworld.rail_transit_stress_profile_packet import (  # noqa: E402
    build_rail_transit_stress_profile_rows,
)


def test_current_packets_are_bounded_review_support_only() -> None:
    """Current shipped packets should align without becoming evidence."""

    audit = build_rail_bounded_treatment_audit()
    by_request = {row["request_id"]: row for row in audit["results"]}

    assert audit["mismatch_count"] == 0
    assert audit["audit_verdict"] == "bounded_review_support_only"
    assert audit["unchecked_pending_decision_count"] == 0
    assert audit["publication_ready"] is False
    assert audit["can_mark_complete"] is False
    assert audit["can_support_rail_evidence_gate"] is False
    assert audit["can_support_acceptance_gate"] is False
    assert by_request[CAPACITY_REQUEST_ID]["matched_stress_classes"] == [
        "partial_capacity_reduction"
    ]
    assert by_request[CAPACITY_REQUEST_ID]["matched_source_treatments"] == [
        "sensitivity_only"
    ]
    assert set(by_request[AVAILABILITY_REQUEST_ID]["matched_stress_classes"]) == {
        "increased_headway",
        "partial_unavailability_or_delay",
        "rail_access_egress_degradation",
    }

    print("PASS: current rail bounded treatments are review support only")


def test_missing_capacity_decision_or_stress_row_blocks_audit() -> None:
    """Audit should flag missing capacity decision and stress profile rows."""

    source_rows = [
        row
        for row in build_rail_source_decision_rows()
        if row["request_id"] != CAPACITY_REQUEST_ID
    ]
    stress_rows = [
        row
        for row in build_rail_transit_stress_profile_rows()
        if row["stress_class"] != "partial_capacity_reduction"
    ]
    audit = build_rail_bounded_treatment_audit(
        source_decision_rows=source_rows,
        stress_profile_rows=stress_rows,
    )
    capacity = _result(audit, CAPACITY_REQUEST_ID)

    assert audit["mismatch_count"] >= 1
    assert capacity["status"] == "mismatch"
    assert any("capacity source-decision row" in item for item in capacity["blockers"])
    assert any("partial-capacity stress-profile row" in item for item in capacity["blockers"])

    print("PASS: missing capacity decision or stress rows block audit")


def test_capacity_stress_must_remain_sensitivity_only_not_evidence() -> None:
    """Capacity stress row must not be promoted into evidence-like status."""

    stress_rows = [dict(row) for row in build_rail_transit_stress_profile_rows()]
    for row in stress_rows:
        if row["stress_class"] == "partial_capacity_reduction":
            row["source_treatment"] = "source_backed"
            row["evidence_status"] = "capacity_evidence"
    audit = build_rail_bounded_treatment_audit(
        source_decision_rows=build_rail_source_decision_rows(),
        stress_profile_rows=stress_rows,
    )
    capacity = _result(audit, CAPACITY_REQUEST_ID)

    assert capacity["status"] == "mismatch"
    assert "partial-capacity stress is not sensitivity-only" in capacity["blockers"]
    assert "partial-capacity stress status no longer blocks evidence use" in capacity[
        "blockers"
    ]

    print("PASS: capacity stress cannot be promoted to evidence-like status")


def test_true_gate_flags_are_blocked() -> None:
    """Any true readiness or gate-support flag should become a mismatch."""

    stress_rows = [dict(row) for row in build_rail_transit_stress_profile_rows()]
    for row in stress_rows:
        if row["stress_class"] == "partial_capacity_reduction":
            row["can_support_rail_evidence_gate"] = "true"
            row["publication_ready"] = "true"
    source_rows = [dict(row) for row in build_rail_source_decision_rows()]
    for row in source_rows:
        if row["request_id"] == CAPACITY_REQUEST_ID:
            row["can_support_acceptance_gate"] = "true"
    audit = build_rail_bounded_treatment_audit(
        source_decision_rows=source_rows,
        stress_profile_rows=stress_rows,
    )
    capacity = _result(audit, CAPACITY_REQUEST_ID)

    assert capacity["status"] == "mismatch"
    assert any("publication_ready=true" in item for item in capacity["blockers"])
    assert any(
        "can_support_rail_evidence_gate=true" in item
        for item in capacity["blockers"]
    )
    assert any(
        "can_support_acceptance_gate=true" in item for item in capacity["blockers"]
    )
    assert audit["publication_ready"] is False
    assert audit["can_support_rail_evidence_gate"] is False

    print("PASS: true gate flags are blocked")


def test_missing_runtime_hook_in_matched_stress_blocks_audit() -> None:
    """Matched stress rows must still have an implemented runtime hook."""

    stress_rows = [dict(row) for row in build_rail_transit_stress_profile_rows()]
    for row in stress_rows:
        if row["stress_class"] == "partial_capacity_reduction":
            row["implementation_status"] = "missing_runtime_hook"
    audit = build_rail_bounded_treatment_audit(
        source_decision_rows=build_rail_source_decision_rows(),
        stress_profile_rows=stress_rows,
    )
    capacity = _result(audit, CAPACITY_REQUEST_ID)

    assert capacity["status"] == "mismatch"
    assert any("missing runtime hook" in item for item in capacity["blockers"])
    assert audit["mismatch_count"] >= 1

    print("PASS: matched stress rows require runtime hooks")


def test_unresolved_linked_artifact_key_blocks_audit() -> None:
    """Matched stress rows must resolve linked artifact keys used as coverage proof."""

    stress_rows = [dict(row) for row in build_rail_transit_stress_profile_rows()]
    for row in stress_rows:
        if row["stress_class"] == "increased_headway":
            row["linked_artifact_key"] = (
                "rail_delay_or_partial_unavailability;missing_policy"
            )
    audit = build_rail_bounded_treatment_audit(
        source_decision_rows=build_rail_source_decision_rows(),
        stress_profile_rows=stress_rows,
    )
    availability = _result(audit, AVAILABILITY_REQUEST_ID)

    assert availability["status"] == "mismatch"
    assert any("missing_policy" in item for item in availability["blockers"])
    assert audit["mismatch_count"] >= 1

    print("PASS: linked artifact keys must resolve")


def test_semicolon_linked_artifact_keys_resolve_individually() -> None:
    """Semicolon-delimited linked keys should resolve token by token."""

    stress_rows = [dict(row) for row in build_rail_transit_stress_profile_rows()]
    for row in stress_rows:
        if row["stress_class"] == "increased_headway":
            row["linked_artifact_key"] = (
                "rail_delay_or_partial_unavailability;fleet_shortage_stress"
            )
    audit = build_rail_bounded_treatment_audit(
        source_decision_rows=build_rail_source_decision_rows(),
        stress_profile_rows=stress_rows,
    )
    availability = _result(audit, AVAILABILITY_REQUEST_ID)

    assert availability["status"] == "coverage_documented_not_evidence"
    assert not any("linked artifact key is missing" in item for item in availability["blockers"])
    assert audit["mismatch_count"] == 0

    print("PASS: semicolon linked artifact keys resolve individually")


def test_bounded_decision_requires_reviewer_fields_without_closing_gates() -> None:
    """Bounded reviewer decisions require basis fields and still do not close gates."""

    source_rows = [dict(row) for row in build_rail_source_decision_rows()]
    for row in source_rows:
        if row["request_id"] == CAPACITY_REQUEST_ID:
            row["decision_choice"] = "retain_capacity_as_sensitivity_only_with_bounds"
    audit = build_rail_bounded_treatment_audit(
        source_decision_rows=source_rows,
        stress_profile_rows=build_rail_transit_stress_profile_rows(),
    )
    capacity = _result(audit, CAPACITY_REQUEST_ID)
    assert capacity["status"] == "mismatch"
    assert any("bounded decision missing required fields" in item for item in capacity["blockers"])

    reviewed_rows = [_reviewed(row) for row in source_rows]
    reviewed_audit = build_rail_bounded_treatment_audit(
        source_decision_rows=reviewed_rows,
        stress_profile_rows=build_rail_transit_stress_profile_rows(),
    )
    reviewed_capacity = _result(reviewed_audit, CAPACITY_REQUEST_ID)
    assert reviewed_capacity["status"] == "coverage_documented_not_evidence"
    assert reviewed_audit["publication_ready"] is False
    assert reviewed_audit["can_mark_complete"] is False
    assert reviewed_audit["can_support_acceptance_gate"] is False

    print("PASS: bounded decisions require reviewer fields without closing gates")


def test_availability_sensitivity_only_choice_is_warned() -> None:
    """Availability sensitivity-only choice should warn because current coverage is scenario-only."""

    source_rows = [dict(row) for row in build_rail_source_decision_rows()]
    for row in source_rows:
        if row["request_id"] == AVAILABILITY_REQUEST_ID:
            row["decision_choice"] = "retain_availability_as_sensitivity_only"
            row.update(_review_fields())
    audit = build_rail_bounded_treatment_audit(
        source_decision_rows=source_rows,
        stress_profile_rows=build_rail_transit_stress_profile_rows(),
    )
    availability = _result(audit, AVAILABILITY_REQUEST_ID)

    assert availability["status"] == "coverage_documented_not_evidence"
    assert any("not sensitivity-only" in item for item in availability["warnings"])

    print("PASS: availability sensitivity-only choice is warned")


def test_writer_emits_non_acceptance_audit_artifacts() -> None:
    """Writer should emit stable JSON and Markdown without acceptance flags."""

    audit = build_rail_bounded_treatment_audit()
    with TemporaryDirectory() as directory:
        root = Path(directory)
        output = root / "audit.json"
        doc = root / "audit.md"
        write_rail_bounded_treatment_audit(audit=audit, output_path=output, doc_path=doc)
        written = json.loads(output.read_text(encoding="utf-8"))
        doc_text = doc.read_text(encoding="utf-8")

    assert written["mismatch_count"] == 0
    assert written["publication_ready"] is False
    assert "Rail Bounded Treatment Audit" in doc_text
    assert "Internal mapping mismatches" in doc_text
    assert "internal consistency check only" in doc_text
    assert "does not validate rail timing" in doc_text

    print("PASS: rail bounded-treatment writer emits non-acceptance artifacts")


def test_shipped_audit_matches_current_outputs() -> None:
    """Default audit artifact should match current generated audit if present."""

    audit = build_rail_bounded_treatment_audit()

    assert DEFAULT_RAIL_BOUNDED_TREATMENT_AUDIT_PATH.exists()
    written = json.loads(
        DEFAULT_RAIL_BOUNDED_TREATMENT_AUDIT_PATH.read_text(encoding="utf-8")
    )

    assert written["row_count"] == audit["row_count"]
    assert written["audit_scope"] == audit["audit_scope"]
    assert written["mismatch_count"] == 0
    assert written["can_mark_complete"] is False
    assert written["publication_ready"] is False

    print("PASS: shipped rail bounded-treatment audit matches current outputs")


def _result(audit: dict[str, object], request_id: str) -> dict[str, object]:
    return {
        str(row["request_id"]): row
        for row in audit["results"]  # type: ignore[index]
    }[request_id]


def _reviewed(row: dict[str, str]) -> dict[str, str]:
    value = dict(row)
    if value["request_id"] == CAPACITY_REQUEST_ID:
        value["decision_choice"] = "retain_capacity_as_sensitivity_only_with_bounds"
    value.update(_review_fields())
    return value


def _review_fields() -> dict[str, str]:
    return {
        "reviewer": "review fixture",
        "decision_date": "2026-06-03",
        "decision_basis": "test fixture bounded treatment review",
        "excluded_or_retained_claim_scope": "bounded stress-only claim scope",
        "not_operational_claim_boundary": (
            "not operational routing, not rail-service calibration, not final acceptance"
        ),
        "bounded_treatment_or_exclusion_rationale": (
            "test fixture confirms bounded treatment remains non-acceptance"
        ),
    }


if __name__ == "__main__":
    test_current_packets_are_bounded_review_support_only()
    test_missing_capacity_decision_or_stress_row_blocks_audit()
    test_capacity_stress_must_remain_sensitivity_only_not_evidence()
    test_true_gate_flags_are_blocked()
    test_missing_runtime_hook_in_matched_stress_blocks_audit()
    test_unresolved_linked_artifact_key_blocks_audit()
    test_semicolon_linked_artifact_keys_resolve_individually()
    test_bounded_decision_requires_reviewer_fields_without_closing_gates()
    test_availability_sensitivity_only_choice_is_warned()
    test_writer_emits_non_acceptance_audit_artifacts()
    test_shipped_audit_matches_current_outputs()
    print("\n=== REALWORLD RAIL BOUNDED TREATMENT AUDIT TESTS PASSED ===")
