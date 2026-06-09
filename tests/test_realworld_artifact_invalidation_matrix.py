"""Tests for Phase 9 artifact invalidation matrix guard."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import zipfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.artifact_invalidation_matrix import (  # noqa: E402
    ARTIFACT_INVALIDATION_ACTION_BATCH_INSPECTION_FIELDS,
    ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_FIELDS,
    ARTIFACT_INVALIDATION_CLOSEOUT_FIELDS,
    ARTIFACT_INVALIDATION_CLOSEOUT_READINESS_FIELDS,
    ALLOWED_REQUIRED_DISPOSITIONS,
    ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
    ARTIFACT_INVALIDATION_FIELDS,
    ARTIFACT_INVALIDATION_QUARANTINE_NON_EVIDENCE_INDEX_FIELDS,
    ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL_GAP_FIELDS,
    ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_COPY_AUDIT_FIELDS,
    ARTIFACT_INVALIDATION_QUARANTINE_CLAIM_REFERENCE_REMEDIATION_FIELDS,
    ARTIFACT_INVALIDATION_QUARANTINE_REFERENCE_TRIAGE_FIELDS,
    ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_FIELDS,
    ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET_FIELDS,
    REQUIRED_PHASE9_GROUPS,
    UPSTREAM_GROUPS,
    build_artifact_invalidation_closeout_action_rows,
    build_artifact_invalidation_action_batch_inspection_rows,
    artifact_invalidation_blocks_phase9,
    build_artifact_invalidation_closeout_readiness_rows,
    build_artifact_invalidation_closeout_template_rows,
    build_artifact_invalidation_quarantine_non_evidence_index_rows,
    build_artifact_invalidation_quarantine_transfer_packet_rows,
    build_artifact_invalidation_quarantine_closeout_prefill_rows,
    build_artifact_invalidation_quarantine_closeout_prefill_gap_audit_rows,
    build_artifact_invalidation_quarantine_main_closeout_copy_audit_rows,
    build_artifact_invalidation_quarantine_main_closeout_draft_overlay_rows,
    build_artifact_invalidation_quarantine_claim_reference_remediation_rows,
    build_artifact_invalidation_quarantine_reference_triage_rows,
    build_artifact_invalidation_quarantine_closeout_template_rows,
    build_artifact_invalidation_quarantine_scope_rows,
    build_artifact_invalidation_rows,
    apply_artifact_invalidation_reviewer_evidence,
    summarize_artifact_invalidation_closeout_action_rows,
    summarize_artifact_invalidation_action_batch_inspection_rows,
    summarize_artifact_invalidation_closeout_readiness_rows,
    summarize_artifact_invalidation_closeout_rows,
    summarize_artifact_invalidation_quarantine_non_evidence_index_rows,
    summarize_artifact_invalidation_quarantine_scope_rows,
    summarize_artifact_invalidation_quarantine_transfer_packet_rows,
    summarize_artifact_invalidation_quarantine_closeout_prefill_rows,
    summarize_artifact_invalidation_quarantine_closeout_prefill_gap_audit_rows,
    summarize_artifact_invalidation_quarantine_main_closeout_copy_audit_rows,
    summarize_artifact_invalidation_quarantine_main_closeout_draft_overlay_rows,
    summarize_artifact_invalidation_quarantine_claim_reference_remediation_rows,
    summarize_artifact_invalidation_quarantine_reference_triage_rows,
    summarize_artifact_invalidation_rows,
    read_artifact_invalidation_closeout_rows,
    write_artifact_invalidation_closeout_action_queue,
    write_artifact_invalidation_action_batch_inspection,
    write_artifact_invalidation_closeout_readiness_audit,
    write_artifact_invalidation_closeout_rows,
    write_artifact_invalidation_closeout_template,
    write_artifact_invalidation_matrix,
    write_artifact_invalidation_quarantine_closeout_template,
    write_artifact_invalidation_quarantine_closeout_prefill,
    write_artifact_invalidation_quarantine_closeout_prefill_gap_audit,
    write_artifact_invalidation_quarantine_main_closeout_copy_audit,
    write_artifact_invalidation_quarantine_main_closeout_draft_overlay,
    write_artifact_invalidation_quarantine_claim_reference_remediation_packet,
    write_artifact_invalidation_quarantine_reference_triage,
    write_artifact_invalidation_quarantine_non_evidence_index,
    write_artifact_invalidation_quarantine_scope_audit,
    write_artifact_invalidation_quarantine_transfer_packet,
)


def test_invalidation_schema_does_not_duplicate_tracked_artifact_audit() -> None:
    """This matrix should not become another git-status packaging audit."""

    forbidden_fields = {
        "path",
        "git_status",
        "artifact_category",
        "clean_checkout_risk",
        "required_action",
    }
    assert not forbidden_fields.intersection(ARTIFACT_INVALIDATION_FIELDS)
    rows = build_artifact_invalidation_rows()
    assert rows
    assert all(not forbidden_fields.intersection(row) for row in rows)
    assert all("git status" not in row["audit_or_regeneration_command"].lower() for row in rows)

    print("PASS: invalidation matrix does not duplicate tracked artifact audit")


def test_matrix_covers_plan_minimum_upstream_and_phase9_groups() -> None:
    rows = build_artifact_invalidation_rows()
    upstream_groups = {row["upstream_change_group"] for row in rows}
    downstream_groups = {row["stale_downstream_group"] for row in rows}
    assert UPSTREAM_GROUPS.issubset(upstream_groups)
    assert REQUIRED_PHASE9_GROUPS.issubset(downstream_groups)

    print("PASS: invalidation matrix covers required upstream and Phase 9 groups")


def test_required_dispositions_match_phase9_action_set() -> None:
    rows = build_artifact_invalidation_rows()
    assert {row["required_disposition"] for row in rows}.issubset(
        ALLOWED_REQUIRED_DISPOSITIONS
    )
    assert {"regenerate", "mark_non_evidence"}.issubset(
        {row["required_disposition"] for row in rows}
    )

    print("PASS: invalidation dispositions match allowed Phase 9 actions")


def test_result_csv_invalidation_marks_downstream_outputs_stale() -> None:
    rows = [
        row
        for row in build_artifact_invalidation_rows()
        if row["upstream_change_group"] == "result_csv_or_manifest"
    ]
    groups = {row["stale_downstream_group"] for row in rows}
    assert {
        "statistics",
        "sensitivity",
        "ml_outputs",
        "figures",
        "reports",
        "review_packages",
    }.issubset(groups)
    assert all(row["disposition_status"] == "stale_pending_disposition" for row in rows)
    assert all(row["claim_boundary_effect"] == "blocks_claim_support" for row in rows)

    print("PASS: result CSV invalidation marks downstream outputs stale")


def test_summary_blocks_phase9_until_reaudit() -> None:
    rows = build_artifact_invalidation_rows()
    summary = summarize_artifact_invalidation_rows(rows)
    assert summary["blocking_row_count"] == len(rows)
    assert summary["required_upstream_groups_covered"] is True
    assert summary["required_phase9_downstream_groups_covered"] is True
    assert summary["remaining_blockers"]

    print("PASS: invalidation summary blocks Phase 9 until reaudit")


def test_write_artifact_invalidation_outputs_are_non_acceptance() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        summary = write_artifact_invalidation_matrix(
            output_path=root / "matrix.csv",
            manifest_path=root / "matrix.json",
            doc_path=root / "matrix.md",
        )
        loaded = json.loads((root / "matrix.json").read_text(encoding="utf-8"))
        with (root / "matrix.csv").open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        text = (root / "matrix.md").read_text(encoding="utf-8")

    assert rows
    assert summary["phase9_promotion_ready"] is False
    assert loaded["publication_ready"] is False
    assert loaded["final_study_ready"] is False
    assert loaded["formal_acceptance_evidence"] is False
    assert ARTIFACT_INVALIDATION_CLAIM_BOUNDARY in text
    assert "does not perform the regeneration" not in text
    assert "not an artifact regeneration record" in text

    print("PASS: invalidation outputs remain non-acceptance")


def test_phase9_preflight_blocks_missing_or_unresolved_matrix() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        missing = root / "missing.json"
        blocks, blockers, summary = artifact_invalidation_blocks_phase9(missing)
        assert blocks is True
        assert summary["manifest_present"] is False
        assert blockers

        matrix_manifest = root / "matrix.json"
        write_artifact_invalidation_matrix(
            output_path=root / "matrix.csv",
            manifest_path=matrix_manifest,
            doc_path=root / "matrix.md",
        )
        blocks, blockers, summary = artifact_invalidation_blocks_phase9(matrix_manifest)
        assert blocks is True
        assert summary["manifest_present"] is True
        assert summary["blocking_row_count"] > 0
        assert blockers

    print("PASS: Phase 9 preflight blocks missing or unresolved invalidation matrix")


def test_phase9_preflight_does_not_trust_ready_boolean_with_blockers() -> None:
    """A hand-edited ready flag must not bypass coverage or stale-row blockers."""

    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        manifest = root / "matrix.json"
        _write_matrix_manifest(
            manifest,
            row_count=51,
            blocking_row_count=1,
            phase9_promotion_ready=True,
            upstream_ok=True,
            phase9_ok=True,
        )
        blocks, blockers, _summary = artifact_invalidation_blocks_phase9(
            manifest,
            closeout_manifest_path=None,
        )
        assert blocks is True
        assert any("unresolved stale rows" in blocker for blocker in blockers)

        _write_matrix_manifest(
            manifest,
            row_count=51,
            blocking_row_count=0,
            phase9_promotion_ready=True,
            upstream_ok=False,
            phase9_ok=True,
        )
        blocks, blockers, _summary = artifact_invalidation_blocks_phase9(
            manifest,
            closeout_manifest_path=None,
        )
        assert blocks is True
        assert any("missing upstream group coverage" in blocker for blocker in blockers)

    print("PASS: Phase 9 preflight does not trust ready boolean with blockers")


def test_closeout_template_is_pending_and_non_acceptance() -> None:
    """The closeout template should be a pending worksheet, not acceptance evidence."""

    rows = build_artifact_invalidation_closeout_template_rows()
    assert rows
    assert set(ARTIFACT_INVALIDATION_CLOSEOUT_FIELDS).issubset(rows[0])
    summary = summarize_artifact_invalidation_closeout_rows(rows)
    assert summary["row_count"] == len(rows)
    assert summary["closed_row_count"] == 0
    assert summary["pending_or_invalid_row_count"] == len(rows)
    assert all(row["actual_disposition"] == "pending" for row in rows)
    assert all(row["reviewer_signoff_status"] == "unsigned" for row in rows)
    assert all(row["publication_ready"] == "false" for row in rows)
    assert all(row["final_study_ready"] == "false" for row in rows)
    assert all(row["formal_acceptance_evidence"] == "false" for row in rows)

    print("PASS: closeout template is pending and non-acceptance")


def test_write_closeout_template_outputs_are_non_acceptance() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        summary = write_artifact_invalidation_closeout_template(
            output_path=root / "closeout.csv",
            manifest_path=root / "closeout.json",
            doc_path=root / "closeout.md",
        )
        loaded = json.loads((root / "closeout.json").read_text(encoding="utf-8"))
        text = (root / "closeout.md").read_text(encoding="utf-8")

    assert summary["pending_or_invalid_row_count"] == summary["row_count"]
    assert loaded["phase9_promotion_ready"] is False
    assert loaded["publication_ready"] is False
    assert loaded["final_study_ready"] is False
    assert loaded["formal_acceptance_evidence"] is False
    assert "reviewer worksheet" in text
    assert "does not grant publication readiness" in text

    print("PASS: closeout template outputs remain non-acceptance")


def test_closeout_action_queue_orders_dependency_batches_without_acceptance() -> None:
    rows = build_artifact_invalidation_closeout_action_rows()
    assert rows
    assert set(ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_FIELDS).issubset(rows[0])

    orders = [int(row["action_order"]) for row in rows]
    assert orders == sorted(orders)
    assert rows[0]["action_batch"] == "quarantine_non_evidence"
    assert "upstream_evidence_and_benchmarks" in {row["action_batch"] for row in rows}
    assert all(
        int(row["action_order"]) == 1
        for row in rows
        if row["stale_downstream_group"] == "full_outputs"
    )
    assert all(
        int(row["action_order"]) == 2
        for row in rows
        if row["upstream_change_group"] == "claim_boundary_or_readiness_logic"
        and row["stale_downstream_group"] == "review_packages"
    )
    assert all(row["blocks_phase9_until_closed"] == "true" for row in rows)
    assert all(row["can_close_without_reviewer_signoff"] == "false" for row in rows)
    assert all(row["publication_ready"] == "false" for row in rows)
    assert all(row["final_study_ready"] == "false" for row in rows)
    assert all(row["formal_acceptance_evidence"] == "false" for row in rows)

    summary = summarize_artifact_invalidation_closeout_action_rows(rows)
    assert summary["row_count"] == len(rows)
    assert summary["blocks_phase9_row_count"] == len(rows)
    assert summary["reviewer_signoff_required_row_count"] == len(rows)
    assert "quarantine_non_evidence" in summary["action_batch_counts"]
    assert "upstream_evidence_and_benchmarks" in summary["action_batch_counts"]
    assert "complete action queue rows" in summary["remaining_blockers"][0]

    print("PASS: closeout action queue orders dependencies without acceptance")


def test_write_closeout_action_queue_outputs_are_non_acceptance() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        summary = write_artifact_invalidation_closeout_action_queue(
            output_path=root / "action_queue.csv",
            manifest_path=root / "action_queue.json",
            doc_path=root / "action_queue.md",
        )
        loaded = json.loads((root / "action_queue.json").read_text(encoding="utf-8"))
        text = (root / "action_queue.md").read_text(encoding="utf-8")

    assert summary["row_count"] == 51
    assert loaded["phase9_promotion_ready"] is False
    assert loaded["publication_ready"] is False
    assert loaded["final_study_ready"] is False
    assert loaded["formal_acceptance_evidence"] is False
    assert "does not close any artifact invalidation row" in text
    assert "or authorize Phase 9" in text

    print("PASS: closeout action queue outputs remain non-acceptance")


def test_action_batch_inspection_merges_queue_and_readiness_without_closing() -> None:
    rows = build_artifact_invalidation_action_batch_inspection_rows()
    assert rows
    assert set(ARTIFACT_INVALIDATION_ACTION_BATCH_INSPECTION_FIELDS).issubset(rows[0])
    summary = summarize_artifact_invalidation_action_batch_inspection_rows(rows)

    assert summary["row_count"] == 51
    assert summary["regeneration_candidate_count"] == 45
    assert summary["exclusion_or_non_evidence_candidate_count"] == 6
    assert summary["evidence_backed_closeout_row_count"] == 0
    assert summary["pending_or_blocked_row_count"] == 51
    assert summary["action_queue_blocks_phase9_row_count"] == 51
    assert summary["can_clear_invalidation_gate_count"] == 0
    assert summary["action_batch_counts"]["quarantine_non_evidence"] == 6
    rollup = summary["action_batch_rollup"]
    assert len(rollup) == len(summary["action_batch_counts"])
    assert rollup[0]["action_batch"] == "quarantine_non_evidence"
    assert rollup[0]["pending_or_blocked_row_count"] == 6
    assert (
        rollup[0]["next_closeout_focus"]
        == "confirm_non_evidence_scope_remove_citations_and_record_reviewer_signoff"
    )
    assert rollup[0]["blocking_prerequisite_batches"] == []
    assert "actual_disposition" in rollup[0]["missing_evidence"]
    quarantine_rows = [
        row for row in rows if row["action_batch"] == "quarantine_non_evidence"
    ]
    assert quarantine_rows
    assert all(
        row["next_closeout_focus"]
        == "confirm_non_evidence_scope_remove_citations_and_record_reviewer_signoff"
        for row in quarantine_rows
    )
    assert all(
        row["blocking_prerequisite_status"]
        == "first_batch_pending_main_closeout_and_reviewer_confirmation"
        for row in quarantine_rows
    )
    first_package = json.loads(quarantine_rows[0]["minimum_evidence_package_json"])
    assert "confirmed_stale_paths_and_hashes" in first_package
    assert "can_clear_invalidation_gate" in first_package
    compact_rows = [row for row in rows if row["action_batch"] == "compact_outputs"]
    assert compact_rows
    assert all(
        row["blocking_prerequisite_batch"] == "upstream_evidence_and_benchmarks"
        for row in compact_rows
    )
    assert "compact_manifest_not_engineering_only" in json.loads(
        compact_rows[0]["minimum_evidence_package_json"]
    )
    assert summary["inspection_classification_counts"][
        "regeneration_candidate_pending_evidence"
    ] == 45
    assert summary["inspection_classification_counts"][
        "exclusion_or_non_evidence_candidate_pending_evidence"
    ] == 6
    assert summary["phase9_promotion_ready"] is False
    assert summary["publication_ready"] is False
    assert summary["final_study_ready"] is False
    assert summary["formal_acceptance_evidence"] is False
    assert summary["must_not_be_used_as_closeout_manifest"] is True

    print("PASS: action-batch inspection merges queue and readiness without closing")


def test_action_batch_inspection_blocks_compact_regeneration_without_source_manifest() -> None:
    row = _closed_closeout_row()
    rows = build_artifact_invalidation_action_batch_inspection_rows([row])
    summary = summarize_artifact_invalidation_action_batch_inspection_rows(rows)

    assert len(rows) == 1
    assert rows[0]["source_manifest_status"] == "missing"
    assert rows[0]["compact_closeout_eligibility_status"].startswith("blocked")
    assert rows[0]["can_clear_invalidation_gate"] == "false"
    assert (
        rows[0]["next_closeout_focus"]
        == "complete_regeneration_manifest_audit_test_and_reviewer_signoff"
    )
    assert rows[0]["blocking_prerequisite_batch"] == "upstream_evidence_and_benchmarks"
    assert rows[0]["blocking_prerequisite_status"].startswith("blocked_until_")
    assert (
        rows[0]["inspection_classification"]
        == "regeneration_attempt_blocked_missing_evidence"
    )
    assert summary["evidence_backed_closeout_row_count"] == 0
    assert summary["pending_or_blocked_row_count"] == 1

    print("PASS: action-batch inspection blocks compact regeneration without source manifest")


def test_write_action_batch_inspection_outputs_are_non_acceptance() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        summary = write_artifact_invalidation_action_batch_inspection(
            output_path=root / "inspection.csv",
            manifest_path=root / "inspection.json",
            doc_path=root / "inspection.md",
        )
        loaded = json.loads((root / "inspection.json").read_text(encoding="utf-8"))
        text = (root / "inspection.md").read_text(encoding="utf-8")
        with (root / "inspection.csv").open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        csv_hash = hashlib.sha256((root / "inspection.csv").read_bytes()).hexdigest()

    assert rows
    assert summary["row_count"] == 51
    assert loaded["phase9_promotion_ready"] is False
    assert loaded["publication_ready"] is False
    assert loaded["final_study_ready"] is False
    assert loaded["formal_acceptance_evidence"] is False
    assert loaded["can_clear_invalidation_gate"] is False
    assert loaded["must_not_be_used_as_closeout_manifest"] is True
    assert loaded["csv_sha256"] == csv_hash
    assert loaded["action_batch_rollup"]
    assert "Batch Rollup" in text
    assert "Minimum Package" in text
    assert "not the main closeout manifest" in text
    assert "not authorization for Phase 9" in text

    print("PASS: action-batch inspection outputs remain non-acceptance")


def test_write_action_batch_inspection_skips_unchanged_csv_rewrite() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        csv_path = root / "inspection.csv"
        write_artifact_invalidation_action_batch_inspection(
            output_path=csv_path,
            manifest_path=root / "inspection.json",
            doc_path=root / "inspection.md",
        )
        first_mtime = csv_path.stat().st_mtime_ns
        first_hash = hashlib.sha256(csv_path.read_bytes()).hexdigest()

        write_artifact_invalidation_action_batch_inspection(
            output_path=csv_path,
            manifest_path=root / "inspection.json",
            doc_path=root / "inspection.md",
        )

        assert csv_path.stat().st_mtime_ns == first_mtime
        assert hashlib.sha256(csv_path.read_bytes()).hexdigest() == first_hash

    print("PASS: action-batch inspection skips unchanged CSV rewrite")


def test_closeout_readiness_audit_covers_rows_without_closing() -> None:
    rows = build_artifact_invalidation_closeout_readiness_rows()
    assert rows
    assert set(ARTIFACT_INVALIDATION_CLOSEOUT_READINESS_FIELDS).issubset(rows[0])
    summary = summarize_artifact_invalidation_closeout_readiness_rows(rows)
    assert summary["row_count"] == len(build_artifact_invalidation_closeout_template_rows())
    assert summary["closeout_ready_row_count"] == 0
    assert summary["pending_or_blocked_row_count"] == summary["row_count"]
    assert summary["phase9_promotion_ready"] is False
    assert summary["must_not_be_used_as_closeout_manifest"] is True

    print("PASS: closeout readiness audit covers rows without closing")


def test_write_closeout_readiness_audit_outputs_are_non_acceptance() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        summary = write_artifact_invalidation_closeout_readiness_audit(
            output_path=root / "readiness.csv",
            manifest_path=root / "readiness.json",
            doc_path=root / "readiness.md",
        )
        loaded = json.loads((root / "readiness.json").read_text(encoding="utf-8"))
        text = (root / "readiness.md").read_text(encoding="utf-8")
    assert summary["must_not_be_used_as_closeout_manifest"] is True
    assert loaded["must_not_be_used_as_closeout_manifest"] is True
    assert loaded["phase9_promotion_ready"] is False
    assert "not the closeout manifest" in text

    print("PASS: closeout readiness audit outputs remain non-acceptance")


def test_compact_engineering_only_manifest_cannot_close_invalidation() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        manifest_path = root / "pilot_staged_manifest.json"
        _write_compact_manifest(manifest_path, engineering_only=True)
        row = _closed_closeout_row()
        row["affected_artifacts_json"] = _artifact_json_for_path(manifest_path)
        row["downstream_after_artifacts_json"] = _artifact_json_for_path(manifest_path)
        summary = summarize_artifact_invalidation_closeout_rows([row])
        readiness_rows = build_artifact_invalidation_closeout_readiness_rows([row])
        readiness_summary = summarize_artifact_invalidation_closeout_readiness_rows(
            readiness_rows
        )
    assert summary["closed_row_count"] == 0
    assert summary["pending_or_invalid_row_count"] == 1
    assert readiness_rows[0]["source_engineering_only"] == "true"
    assert readiness_rows[0]["compact_closeout_eligibility_status"].startswith("blocked")
    assert readiness_summary["compact_source_blocked_count"] == 1

    print("PASS: compact engineering-only manifest cannot close invalidation")


def test_compact_mixed_manifest_row_fails_if_any_source_manifest_is_blocked() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        eligible_path = root / "eligible_manifest.json"
        blocked_path = root / "blocked_manifest.json"
        _write_compact_manifest(eligible_path, engineering_only=False)
        _write_compact_manifest(blocked_path, engineering_only=True)
        row = _closed_closeout_row()
        row["affected_artifacts_json"] = json.dumps(
            json.loads(_artifact_json_for_path(eligible_path))
            + json.loads(_artifact_json_for_path(blocked_path))
        )
        row["downstream_after_artifacts_json"] = row["affected_artifacts_json"]
        summary = summarize_artifact_invalidation_closeout_rows([row])
        readiness_rows = build_artifact_invalidation_closeout_readiness_rows([row])
    assert summary["closed_row_count"] == 0
    assert readiness_rows[0]["source_manifest_path"].endswith("blocked_manifest.json")
    assert readiness_rows[0]["compact_closeout_eligibility_status"].startswith("blocked")

    print("PASS: compact mixed manifest row fails if any source manifest is blocked")


def test_compact_eligible_manifest_can_close_invalidation_only() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        manifest_path = root / "eligible_manifest.json"
        _write_compact_manifest(manifest_path, engineering_only=False)
        row = _closed_closeout_row()
        row["affected_artifacts_json"] = _artifact_json_for_path(manifest_path)
        row["downstream_after_artifacts_json"] = _artifact_json_for_path(manifest_path)
        _write_reviewer_evidence(root, row)
        summary = summarize_artifact_invalidation_closeout_rows([row])
        readiness_rows = build_artifact_invalidation_closeout_readiness_rows([row])
    assert summary["closed_row_count"] == 1
    assert readiness_rows[0]["compact_closeout_eligibility_status"] == "eligible"
    assert readiness_rows[0]["can_clear_invalidation_gate"] == "true"

    print("PASS: compact eligible manifest can close invalidation only")


def test_compact_scoped_regeneration_manifest_can_close_invalidation_only() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        manifest_path = root / "scoped_regeneration_manifest.json"
        _write_compact_manifest(
            manifest_path,
            engineering_only=False,
            scoped_regeneration=True,
        )
        row = _closed_closeout_row()
        row["affected_artifacts_json"] = _artifact_json_for_path(manifest_path)
        row["downstream_after_artifacts_json"] = _artifact_json_for_path(manifest_path)
        _write_reviewer_evidence(root, row)
        summary = summarize_artifact_invalidation_closeout_rows([row])
        readiness_rows = build_artifact_invalidation_closeout_readiness_rows([row])
    assert summary["closed_row_count"] == 1
    assert readiness_rows[0]["source_engineering_only"] == "false"
    assert readiness_rows[0]["source_phase8_preflight_status"] == (
        "scoped_closeout_regeneration"
    )
    assert readiness_rows[0]["source_artifact_invalidation_blocks_phase9"] == "true"
    assert readiness_rows[0]["source_rail_source_decisions_pending"] == "true"
    assert readiness_rows[0]["compact_closeout_eligibility_status"] == "eligible"
    assert readiness_rows[0]["can_clear_invalidation_gate"] == "true"

    print("PASS: compact scoped regeneration manifest can close invalidation only")


def test_missing_reviewer_evidence_cannot_close_current_invalidation() -> None:
    row = _closed_closeout_row()
    row["invalidation_row_id"] = "region_boundary->statistics"
    row["stale_downstream_group"] = "statistics"

    summary = summarize_artifact_invalidation_closeout_rows([row])
    readiness_rows = build_artifact_invalidation_closeout_readiness_rows([row])
    missing = json.loads(readiness_rows[0]["missing_evidence_json"])

    assert summary["closed_row_count"] == 0
    assert readiness_rows[0]["reviewer_identity_status"] == (
        "missing_reviewer_evidence_path"
    )
    assert "reviewer_identity:missing_reviewer_evidence_path" in missing

    print("PASS: missing reviewer evidence cannot close current invalidation")


def test_user_reported_human_reviewer_marker_cannot_close_current_invalidation() -> None:
    row = _closed_closeout_row()
    row["reviewer_id"] = "user_reported_human_reviewer_20260605"

    summary = summarize_artifact_invalidation_closeout_rows([row])
    readiness_rows = build_artifact_invalidation_closeout_readiness_rows([row])
    missing = json.loads(readiness_rows[0]["missing_evidence_json"])

    assert summary["closed_row_count"] == 0
    assert readiness_rows[0]["reviewer_identity_status"] == (
        "obsolete_human_reviewer_marker"
    )
    assert readiness_rows[0]["can_clear_invalidation_gate"] == "false"
    assert "reviewer_identity:obsolete_human_reviewer_marker" in missing

    print("PASS: obsolete human reviewer marker cannot close current invalidation")


def test_closeout_readiness_summary_keeps_support_blocker_when_rows_ready() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        row = _closed_closeout_row()
        row["invalidation_row_id"] = "region_boundary->statistics"
        row["stale_downstream_group"] = "statistics"
        _write_reviewer_evidence(root, row)
        readiness_rows = build_artifact_invalidation_closeout_readiness_rows([row])
        readiness_summary = summarize_artifact_invalidation_closeout_readiness_rows(
            readiness_rows
        )

    assert readiness_summary["closeout_ready_row_count"] == 1
    assert readiness_summary["can_clear_invalidation_gate_count"] == 1
    assert readiness_summary["phase9_promotion_ready"] is False
    assert readiness_summary["must_not_be_used_as_closeout_manifest"] is True
    assert any(
        "support-only" in blocker
        for blocker in readiness_summary["remaining_blockers"]
    )

    print("PASS: closeout readiness summary keeps support-only blocker")


def test_gate_shaped_reviewer_evidence_cannot_close_invalidation() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        row = _closed_closeout_row()
        row["invalidation_row_id"] = "region_boundary->statistics"
        row["stale_downstream_group"] = "statistics"
        _write_reviewer_evidence(root, row, gate_shaped=True)

        summary = summarize_artifact_invalidation_closeout_rows([row])
        readiness_rows = build_artifact_invalidation_closeout_readiness_rows([row])
        missing = json.loads(readiness_rows[0]["missing_evidence_json"])

    assert summary["closed_row_count"] == 0
    assert readiness_rows[0]["reviewer_identity_status"] == (
        "reviewer_evidence_invalid_record_type"
    )
    assert "reviewer_identity:reviewer_evidence_invalid_record_type" in missing

    print("PASS: gate-shaped reviewer evidence cannot close invalidation")


def test_support_only_reviewer_evidence_paths_cannot_close_invalidation() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        row = _closed_closeout_row()
        row["invalidation_row_id"] = "region_boundary->statistics"
        row["stale_downstream_group"] = "statistics"
        _write_reviewer_evidence(root, row, support_only=True)

        summary = summarize_artifact_invalidation_closeout_rows([row])
        readiness_rows = build_artifact_invalidation_closeout_readiness_rows([row])
        missing = json.loads(readiness_rows[0]["missing_evidence_json"])

    assert summary["closed_row_count"] == 0
    assert readiness_rows[0]["reviewer_identity_status"] == (
        "reviewer_evidence_support_only_paths"
    )
    assert "reviewer_identity:reviewer_evidence_support_only_paths" in missing

    print("PASS: support-only reviewer evidence cannot close invalidation")


def test_apply_reviewer_evidence_links_valid_record_only() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        row = _closed_closeout_row()
        row["invalidation_row_id"] = "region_boundary->statistics"
        row["stale_downstream_group"] = "statistics"
        row["reviewer_id"] = "user_reported_human_reviewer_20260605"
        row["reviewed_at_utc"] = "2026-06-05T01:21:04+00:00"
        row["reviewer_evidence_path"] = ""
        row["reviewer_evidence_sha256"] = ""
        row["can_clear_invalidation_gate"] = "false"

        evidence_ref = root / "reviewer_source_manifest.json"
        evidence_ref.write_text(
            json.dumps({"fixture": "source-backed review"}, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        reviewer_record = {
            "schema_version": 1,
            "record_type": "artifact_invalidation_closeout_reviewer_evidence",
            "scope": "artifact_invalidation_closeout_only",
            "invalidation_row_id": row["invalidation_row_id"],
            "reviewer_id": "gpt55_xhigh_artifact_invalidation_reviewer",
            "reviewed_at_utc": "2026-06-09T00:00:00+00:00",
            "decision": "signed_off_for_invalidation_closeout_only",
            "reviewed_paths": [row["invalidation_row_id"]],
            "evidence_paths": [evidence_ref.as_posix()],
            "publication_ready": False,
            "final_study_ready": False,
            "formal_acceptance_evidence": False,
        }
        evidence_dir = root / "reviewer_evidence"
        evidence_dir.mkdir()
        reviewer_path = evidence_dir / "reviewer_record.json"
        reviewer_path.write_text(
            json.dumps(reviewer_record, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        rows, summary = apply_artifact_invalidation_reviewer_evidence(
            [row],
            evidence_dir,
            project_root=root,
        )
        closeout_summary = summarize_artifact_invalidation_closeout_rows(rows)
        readiness_rows = build_artifact_invalidation_closeout_readiness_rows(
            rows,
            project_root=root,
        )

    assert summary["applied_row_count"] == 1
    assert summary["rejected_evidence_record_count"] == 0
    assert rows[0]["reviewer_id"] == "gpt55_xhigh_artifact_invalidation_reviewer"
    assert rows[0]["reviewer_evidence_path"].endswith("reviewer_record.json")
    assert rows[0]["can_clear_invalidation_gate"] == "true"
    assert closeout_summary["closed_row_count"] == 1
    assert readiness_rows[0]["reviewer_identity_status"] == "current_reviewer_evidence"

    print("PASS: valid reviewer evidence can be hash-linked into closeout rows")


def test_apply_reviewer_evidence_rejects_missing_payload_evidence_path() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        row = _closed_closeout_row()
        row["invalidation_row_id"] = "region_boundary->statistics"
        row["stale_downstream_group"] = "statistics"
        row["can_clear_invalidation_gate"] = "false"
        reviewer_record = {
            "schema_version": 1,
            "record_type": "artifact_invalidation_closeout_reviewer_evidence",
            "scope": "artifact_invalidation_closeout_only",
            "invalidation_row_id": row["invalidation_row_id"],
            "reviewer_id": "gpt55_xhigh_artifact_invalidation_reviewer",
            "reviewed_at_utc": "2026-06-09T00:00:00+00:00",
            "decision": "signed_off_for_invalidation_closeout_only",
            "reviewed_paths": [row["invalidation_row_id"]],
            "evidence_paths": [(root / "missing_source_manifest.json").as_posix()],
            "publication_ready": False,
            "final_study_ready": False,
            "formal_acceptance_evidence": False,
        }
        evidence_dir = root / "reviewer_evidence"
        evidence_dir.mkdir()
        reviewer_path = evidence_dir / "reviewer_record.json"
        reviewer_path.write_text(
            json.dumps(reviewer_record, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        rows, summary = apply_artifact_invalidation_reviewer_evidence(
            [row],
            evidence_dir,
            project_root=root,
        )
        readiness_rows = build_artifact_invalidation_closeout_readiness_rows(
            rows,
            project_root=root,
        )

    assert summary["applied_row_count"] == 0
    assert summary["rejected_evidence_record_count"] == 1
    assert "reviewer_evidence_referenced_path_missing" in summary["rejected_rows"][0]
    assert rows[0]["can_clear_invalidation_gate"] == "false"
    assert readiness_rows[0]["reviewer_identity_status"] == "missing_reviewer_evidence_path"

    print("PASS: reviewer evidence with missing referenced evidence path is rejected")


def test_cli_applies_reviewer_evidence_when_requested() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        closeout_csv = root / "closeout.csv"
        closeout_manifest = root / "closeout.json"
        closeout_doc = root / "closeout.md"
        row = _closed_closeout_row()
        row["invalidation_row_id"] = "region_boundary->statistics"
        row["stale_downstream_group"] = "statistics"
        row["can_clear_invalidation_gate"] = "false"
        write_artifact_invalidation_closeout_rows(
            [row],
            output_path=closeout_csv,
            manifest_path=closeout_manifest,
            doc_path=closeout_doc,
        )

        evidence_ref = root / "reviewer_source_manifest.json"
        evidence_ref.write_text(
            json.dumps({"fixture": "source-backed review"}, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        evidence_dir = root / "reviewer_evidence"
        evidence_dir.mkdir()
        reviewer_record = {
            "schema_version": 1,
            "record_type": "artifact_invalidation_closeout_reviewer_evidence",
            "scope": "artifact_invalidation_closeout_only",
            "invalidation_row_id": row["invalidation_row_id"],
            "reviewer_id": "gpt55_xhigh_artifact_invalidation_reviewer",
            "reviewed_at_utc": "2026-06-09T00:00:00+00:00",
            "decision": "signed_off_for_invalidation_closeout_only",
            "reviewed_paths": [row["invalidation_row_id"]],
            "evidence_paths": [evidence_ref.as_posix()],
            "publication_ready": False,
            "final_study_ready": False,
            "formal_acceptance_evidence": False,
        }
        (evidence_dir / "reviewer_record.json").write_text(
            json.dumps(reviewer_record, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        result = subprocess.run(
            [
                sys.executable,
                "scripts/write_artifact_invalidation_matrix.py",
                "--output",
                str(root / "matrix.csv"),
                "--manifest",
                str(root / "matrix.json"),
                "--doc",
                str(root / "matrix.md"),
                "--closeout-output",
                str(closeout_csv),
                "--closeout-manifest",
                str(closeout_manifest),
                "--closeout-doc",
                str(closeout_doc),
                "--apply-reviewer-evidence-dir",
                str(evidence_dir),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        rows = read_artifact_invalidation_closeout_rows(closeout_csv)

    assert result.returncode == 0, result.stderr
    assert rows[0]["can_clear_invalidation_gate"] == "true"
    assert rows[0]["reviewer_id"] == "gpt55_xhigh_artifact_invalidation_reviewer"

    print("PASS: CLI applies reviewer evidence when requested")


def test_cli_refuses_template_regeneration_during_reviewer_evidence_apply() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        evidence_dir = root / "reviewer_evidence"
        evidence_dir.mkdir()
        closeout_csv = root / "closeout.csv"

        result = subprocess.run(
            [
                sys.executable,
                "scripts/write_artifact_invalidation_matrix.py",
                "--output",
                str(root / "matrix.csv"),
                "--manifest",
                str(root / "matrix.json"),
                "--doc",
                str(root / "matrix.md"),
                "--closeout-output",
                str(closeout_csv),
                "--write-closeout-template",
                "--apply-reviewer-evidence-dir",
                str(evidence_dir),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    assert result.returncode == 2
    assert "Refusing to combine --write-closeout-template" in result.stderr
    assert not closeout_csv.exists()

    print("PASS: CLI refuses template regeneration during reviewer evidence apply")


def test_compact_closeout_requires_source_manifest_not_only_csv_outputs() -> None:
    row = _closed_closeout_row()
    artifact = json.dumps(
        [
            {
                "path": "results/realworld_pilot/phase8_compact_engineering_20260603/pilot_staged_results.csv",
                "sha256": "a" * 64,
                "role": "stale_downstream",
            }
        ]
    )
    row["affected_artifacts_json"] = artifact
    row["downstream_after_artifacts_json"] = artifact
    summary = summarize_artifact_invalidation_closeout_rows([row])
    readiness_rows = build_artifact_invalidation_closeout_readiness_rows([row])
    assert summary["closed_row_count"] == 0
    assert readiness_rows[0]["source_manifest_status"] == "missing"
    assert (
        readiness_rows[0]["compact_closeout_eligibility_status"]
        == "blocked_missing_source_manifest"
    )

    print("PASS: compact closeout requires source manifest, not only CSV outputs")


def test_quarantine_closeout_template_filters_first_batch_without_closing() -> None:
    rows = build_artifact_invalidation_quarantine_closeout_template_rows()
    action_rows = build_artifact_invalidation_closeout_action_rows()
    expected_ids = {
        row["invalidation_row_id"]
        for row in action_rows
        if row["action_batch"] == "quarantine_non_evidence"
    }
    actual_ids = {row["invalidation_row_id"] for row in rows}
    assert len(rows) == 6
    assert actual_ids == expected_ids
    assert all(row["required_disposition"] == "mark_non_evidence" for row in rows)
    assert all(row["actual_disposition"] == "pending" for row in rows)
    assert all(row["closeout_status"] == "pending" for row in rows)
    assert all(row["reviewer_signoff_status"] == "unsigned" for row in rows)
    assert all(row["can_clear_invalidation_gate"] == "false" for row in rows)
    assert all(row["publication_ready"] == "false" for row in rows)
    assert all(row["final_study_ready"] == "false" for row in rows)
    assert all(row["formal_acceptance_evidence"] == "false" for row in rows)
    assert {
        row["stale_downstream_group"] for row in rows
    } == {"full_outputs", "review_packages"}
    assert sum(1 for row in rows if row["stale_downstream_group"] == "full_outputs") == 5
    assert sum(1 for row in rows if row["stale_downstream_group"] == "review_packages") == 1
    assert "result_csv_or_manifest->review_packages" not in actual_ids

    summary = summarize_artifact_invalidation_closeout_rows(rows)
    assert summary["row_count"] == 6
    assert summary["closed_row_count"] == 0
    assert summary["pending_or_invalid_row_count"] == 6

    print("PASS: quarantine closeout template filters first batch without closing")


def test_write_quarantine_closeout_template_does_not_mutate_main_closeout() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        main_csv = root / "main_closeout.csv"
        main_manifest = root / "main_closeout.json"
        main_doc = root / "main_closeout.md"
        write_artifact_invalidation_closeout_template(
            output_path=main_csv,
            manifest_path=main_manifest,
            doc_path=main_doc,
        )
        before = {
            "csv": main_csv.read_text(encoding="utf-8"),
            "manifest": main_manifest.read_text(encoding="utf-8"),
            "doc": main_doc.read_text(encoding="utf-8"),
        }

        write_artifact_invalidation_quarantine_closeout_template(
            output_path=root / "quarantine.csv",
            manifest_path=root / "quarantine.json",
            doc_path=root / "quarantine.md",
        )

        after = {
            "csv": main_csv.read_text(encoding="utf-8"),
            "manifest": main_manifest.read_text(encoding="utf-8"),
            "doc": main_doc.read_text(encoding="utf-8"),
        }

    assert before == after

    print("PASS: quarantine closeout template does not mutate main closeout")


def test_write_quarantine_closeout_template_outputs_are_non_acceptance() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        summary = write_artifact_invalidation_quarantine_closeout_template(
            output_path=root / "quarantine.csv",
            manifest_path=root / "quarantine.json",
            doc_path=root / "quarantine.md",
        )
        loaded = json.loads((root / "quarantine.json").read_text(encoding="utf-8"))
        text = (root / "quarantine.md").read_text(encoding="utf-8")
        csv_sha256 = hashlib.sha256((root / "quarantine.csv").read_bytes()).hexdigest()

    assert summary["row_count"] == 6
    assert summary["pending_or_invalid_row_count"] == 6
    assert summary["source_action_batch"] == "quarantine_non_evidence"
    assert len(summary["csv_sha256"]) == 64
    assert summary["csv_sha256"] == csv_sha256
    assert loaded["csv_sha256"] == summary["csv_sha256"]
    assert loaded["phase9_promotion_ready"] is False
    assert loaded["publication_ready"] is False
    assert loaded["final_study_ready"] is False
    assert loaded["formal_acceptance_evidence"] is False
    assert "reviewer input template only" in text
    assert "does not authorize Phase 9" in text

    print("PASS: quarantine closeout template outputs remain non-acceptance")


def test_write_quarantine_closeout_template_skips_unchanged_csv_rewrite() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        csv_path = root / "quarantine.csv"
        write_artifact_invalidation_quarantine_closeout_template(
            output_path=csv_path,
            manifest_path=root / "quarantine.json",
            doc_path=root / "quarantine.md",
        )
        csv_text = csv_path.read_text(encoding="utf-8")
        old_time = 1_700_000_000
        os.utime(csv_path, (old_time, old_time))
        csv_mtime = csv_path.stat().st_mtime_ns

        write_artifact_invalidation_quarantine_closeout_template(
            output_path=csv_path,
            manifest_path=root / "quarantine.json",
            doc_path=root / "quarantine.md",
        )

        assert csv_path.read_text(encoding="utf-8") == csv_text
        assert csv_path.stat().st_mtime_ns == csv_mtime

    print("PASS: quarantine closeout template skips unchanged CSV rewrite")


def test_quarantine_scope_audit_uses_finding_rows_not_closeout_fields() -> None:
    forbidden_fields = {
        "actual_disposition",
        "closeout_status",
        "reviewer_signoff_status",
        "reviewed_at_utc",
        "can_clear_invalidation_gate",
        "phase9_promotion_ready",
        "publication_ready",
        "final_study_ready",
        "formal_acceptance_evidence",
        "suggested_main_closeout_fields",
    }
    assert not forbidden_fields.intersection(ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_FIELDS)

    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _write_quarantine_scope_fixture(root)
        rows = build_artifact_invalidation_quarantine_scope_rows(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
        )
        summary = summarize_artifact_invalidation_quarantine_scope_rows(rows)

    assert rows
    assert set(ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_FIELDS).issubset(rows[0])
    assert all(not forbidden_fields.intersection(row) for row in rows)
    assert {row["finding_type"] for row in rows}.issuperset(
        {"stale_artifact_candidate", "zip_candidate", "reference_hit"}
    )
    assert all(row["action_batch"] == "quarantine_non_evidence" for row in rows)
    assert summary["expected_quarantine_row_count"] == 6
    assert summary["covered_quarantine_row_count"] == 6
    assert summary["phase9_promotion_ready"] is False
    assert summary["publication_ready"] is False
    assert summary["formal_acceptance_evidence"] is False
    assert summary["acceptance_ready"] is False
    assert summary["must_not_be_used_as_closeout_manifest"] is True
    assert summary["remaining_blockers"]

    print("PASS: quarantine scope audit uses finding rows without closeout fields")


def test_write_quarantine_scope_audit_outputs_are_non_acceptance() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _write_quarantine_scope_fixture(root)
        summary = write_artifact_invalidation_quarantine_scope_audit(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
            output_path=root / "scope.csv",
            manifest_path=root / "scope.json",
            doc_path=root / "scope.md",
        )
        loaded = json.loads((root / "scope.json").read_text(encoding="utf-8"))
        text = (root / "scope.md").read_text(encoding="utf-8")
        with (root / "scope.csv").open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))

    assert rows
    assert summary["must_not_be_used_as_closeout_manifest"] is True
    assert loaded["phase9_promotion_ready"] is False
    assert loaded["publication_ready"] is False
    assert loaded["final_study_ready"] is False
    assert loaded["formal_acceptance_evidence"] is False
    assert loaded["acceptance_ready"] is False
    assert "not the main closeout manifest" in text
    assert "not Phase 9 readiness" in text
    assert any(
        "accepted validation" in row["matched_detail"]
        for row in rows
        if row["finding_type"] == "reference_hit"
    )
    assert "accepted validation" not in text
    assert "excerpt omitted; see CSV evidence row" in text

    print("PASS: quarantine scope audit outputs remain non-acceptance")


def test_quarantine_non_evidence_index_dedupes_candidate_paths() -> None:
    forbidden_fields = {
        "actual_disposition",
        "closeout_status",
        "reviewer_signoff_status",
        "reviewed_at_utc",
        "can_clear_invalidation_gate",
        "phase9_promotion_ready",
        "publication_ready",
        "final_study_ready",
        "formal_acceptance_evidence",
    }
    assert not forbidden_fields.intersection(
        ARTIFACT_INVALIDATION_QUARANTINE_NON_EVIDENCE_INDEX_FIELDS
    )

    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _write_quarantine_scope_fixture(root)
        scope_rows = build_artifact_invalidation_quarantine_scope_rows(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
        )
        index_rows = build_artifact_invalidation_quarantine_non_evidence_index_rows(
            scope_rows=scope_rows,
        )
        scope_summary = summarize_artifact_invalidation_quarantine_scope_rows(scope_rows)
        index_summary = summarize_artifact_invalidation_quarantine_non_evidence_index_rows(
            index_rows,
            source_scope_summary=scope_summary,
        )

    assert index_rows
    assert set(ARTIFACT_INVALIDATION_QUARANTINE_NON_EVIDENCE_INDEX_FIELDS).issubset(
        index_rows[0]
    )
    assert all(not forbidden_fields.intersection(row) for row in index_rows)
    assert all(row["action_batch"] == "quarantine_non_evidence" for row in index_rows)
    assert all(
        row["candidate_type"] in {"stale_artifact_candidate", "zip_candidate"}
        for row in index_rows
    )
    assert not any(row["candidate_type"] == "reference_hit" for row in index_rows)
    assert len({row["matched_path"] for row in index_rows}) == len(index_rows)
    assert any(int(row["source_row_count"]) > 1 for row in index_rows)
    assert index_summary["covered_quarantine_row_count"] == 6
    assert index_summary["deduped_duplicate_count"] > 0
    assert index_summary["phase9_promotion_ready"] is False
    assert index_summary["must_not_be_used_as_closeout_manifest"] is True

    print("PASS: quarantine non-evidence index dedupes candidate paths")


def test_write_quarantine_non_evidence_index_outputs_are_non_acceptance() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _write_quarantine_scope_fixture(root)
        summary = write_artifact_invalidation_quarantine_non_evidence_index(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
            output_path=root / "index.csv",
            manifest_path=root / "index.json",
            doc_path=root / "index.md",
        )
        loaded = json.loads((root / "index.json").read_text(encoding="utf-8"))
        text = (root / "index.md").read_text(encoding="utf-8")
        with (root / "index.csv").open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))

    assert rows
    assert summary["source_action_batch"] == "quarantine_non_evidence"
    assert loaded["phase9_promotion_ready"] is False
    assert loaded["publication_ready"] is False
    assert loaded["final_study_ready"] is False
    assert loaded["formal_acceptance_evidence"] is False
    assert loaded["can_clear_invalidation_gate"] is False
    assert loaded["acceptance_ready"] is False
    assert loaded["must_not_be_used_as_closeout_manifest"] is True
    assert "not a closeout manifest" in text
    assert "not Phase 9 readiness" in text

    print("PASS: quarantine non-evidence index outputs remain non-acceptance")


def test_quarantine_non_evidence_index_cannot_be_used_as_main_closeout_manifest() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _write_quarantine_scope_fixture(root)
        matrix_manifest = root / "ready_matrix.json"
        index_manifest = root / "index.json"
        _write_matrix_manifest(
            matrix_manifest,
            row_count=51,
            blocking_row_count=0,
            phase9_promotion_ready=True,
            upstream_ok=True,
            phase9_ok=True,
        )
        write_artifact_invalidation_quarantine_non_evidence_index(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
            output_path=root / "index.csv",
            manifest_path=index_manifest,
            doc_path=root / "index.md",
        )

        blocks, blockers, _summary = artifact_invalidation_blocks_phase9(
            matrix_manifest,
            index_manifest,
        )

    assert blocks is True
    assert any("does not cover every matrix row" in blocker for blocker in blockers)
    assert any("cannot be used" in blocker for blocker in blockers)

    print("PASS: quarantine non-evidence index cannot be used as main closeout")


def test_quarantine_transfer_packet_groups_six_row_handoff_without_closing() -> None:
    forbidden_fields = {
        "actual_disposition",
        "closeout_status",
        "reviewer_signoff_status",
        "reviewed_at_utc",
        "can_clear_invalidation_gate",
        "phase9_promotion_ready",
        "publication_ready",
        "final_study_ready",
        "formal_acceptance_evidence",
    }
    assert not forbidden_fields.intersection(
        ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET_FIELDS
    )

    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _write_quarantine_scope_fixture(root)
        scope_rows = build_artifact_invalidation_quarantine_scope_rows(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
        )
        index_rows = build_artifact_invalidation_quarantine_non_evidence_index_rows(
            scope_rows=scope_rows,
        )
        transfer_rows = build_artifact_invalidation_quarantine_transfer_packet_rows(
            index_rows=index_rows,
            scope_rows=scope_rows,
        )
        index_summary = summarize_artifact_invalidation_quarantine_non_evidence_index_rows(
            index_rows,
            source_scope_summary=summarize_artifact_invalidation_quarantine_scope_rows(
                scope_rows
            ),
        )
        transfer_summary = summarize_artifact_invalidation_quarantine_transfer_packet_rows(
            transfer_rows,
            source_index_summary=index_summary,
            source_scope_summary=summarize_artifact_invalidation_quarantine_scope_rows(
                scope_rows
            ),
        )

    assert len(transfer_rows) == 6
    assert set(ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET_FIELDS).issubset(
        transfer_rows[0]
    )
    assert all(not forbidden_fields.intersection(row) for row in transfer_rows)
    assert all(row["action_batch"] == "quarantine_non_evidence" for row in transfer_rows)
    assert all(row["transfer_status"] == "draft_pending_reviewer_confirmation" for row in transfer_rows)
    assert transfer_summary["covered_quarantine_row_count"] == 6
    assert transfer_summary["source_index_artifact_count"] == index_summary["indexed_artifact_count"]
    assert (
        transfer_summary["candidate_artifact_count"]
        == index_summary["source_candidate_finding_count"]
    )
    assert (
        transfer_summary["candidate_artifact_hash_match_count"]
        == transfer_summary["candidate_artifact_count"]
    )
    assert transfer_summary["candidate_artifact_missing_count"] == 0
    assert transfer_summary["candidate_artifact_hash_mismatch_count"] == 0
    assert transfer_summary["source_integrity_ready"] is True
    assert transfer_summary["phase9_promotion_ready"] is False
    assert transfer_summary["must_not_be_used_as_closeout_manifest"] is True
    first_artifacts = json.loads(transfer_rows[0]["candidate_artifacts_json"])
    assert first_artifacts
    assert all(
        artifact["current_integrity_status"] == "hash_match"
        for artifact in first_artifacts
    )
    assert all(
        artifact["hash_matches_current_file"] == "true"
        for artifact in first_artifacts
    )

    print("PASS: quarantine transfer packet groups six-row handoff without closing")


def test_quarantine_transfer_packet_detects_changed_candidate_artifacts() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _write_quarantine_scope_fixture(root)
        scope_rows = build_artifact_invalidation_quarantine_scope_rows(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
        )
        index_rows = build_artifact_invalidation_quarantine_non_evidence_index_rows(
            scope_rows=scope_rows,
        )
        (root / "results" / "realworld_pilot" / "pilot_full_results.csv").write_text(
            "policy,completion_rate\nbus,0.7\n",
            encoding="utf-8",
        )
        transfer_rows = build_artifact_invalidation_quarantine_transfer_packet_rows(
            index_rows=index_rows,
            scope_rows=scope_rows,
            project_root=root,
        )
        transfer_summary = summarize_artifact_invalidation_quarantine_transfer_packet_rows(
            transfer_rows
        )

    artifacts = [
        artifact
        for row in transfer_rows
        for artifact in json.loads(row["candidate_artifacts_json"])
    ]
    assert any(
        artifact["path"].endswith("results/realworld_pilot/pilot_full_results.csv")
        and artifact["current_integrity_status"] == "hash_mismatch"
        and artifact["hash_matches_current_file"] == "false"
        for artifact in artifacts
    )
    assert transfer_summary["candidate_artifact_hash_mismatch_count"] >= 1
    assert transfer_summary["source_integrity_ready"] is False
    assert transfer_summary["phase9_promotion_ready"] is False

    print("PASS: quarantine transfer packet detects changed candidate artifacts")


def test_write_quarantine_transfer_packet_outputs_are_non_acceptance() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _write_quarantine_scope_fixture(root)
        summary = write_artifact_invalidation_quarantine_transfer_packet(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
            output_path=root / "transfer.csv",
            manifest_path=root / "transfer.json",
            doc_path=root / "transfer.md",
        )
        loaded = json.loads((root / "transfer.json").read_text(encoding="utf-8"))
        text = (root / "transfer.md").read_text(encoding="utf-8")
        with (root / "transfer.csv").open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))

    assert rows
    assert summary["source_action_batch"] == "quarantine_non_evidence"
    assert loaded["phase9_promotion_ready"] is False
    assert loaded["publication_ready"] is False
    assert loaded["final_study_ready"] is False
    assert loaded["formal_acceptance_evidence"] is False
    assert loaded["can_clear_invalidation_gate"] is False
    assert loaded["acceptance_ready"] is False
    assert loaded["must_not_be_used_as_closeout_manifest"] is True
    assert "not closeout evidence" in text
    assert "not transfer calibration" in text
    assert "not Phase 9 readiness" in text

    print("PASS: quarantine transfer packet outputs remain non-acceptance")


def test_quarantine_transfer_packet_cannot_be_used_as_main_closeout_manifest() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _write_quarantine_scope_fixture(root)
        matrix_manifest = root / "ready_matrix.json"
        transfer_manifest = root / "transfer.json"
        _write_matrix_manifest(
            matrix_manifest,
            row_count=51,
            blocking_row_count=0,
            phase9_promotion_ready=True,
            upstream_ok=True,
            phase9_ok=True,
        )
        write_artifact_invalidation_quarantine_transfer_packet(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
            output_path=root / "transfer.csv",
            manifest_path=transfer_manifest,
            doc_path=root / "transfer.md",
        )

        blocks, blockers, _summary = artifact_invalidation_blocks_phase9(
            matrix_manifest,
            transfer_manifest,
        )

    assert blocks is True
    assert any("does not cover every matrix row" in blocker for blocker in blockers)
    assert any("cannot be used" in blocker for blocker in blockers)

    print("PASS: quarantine transfer packet cannot be used as main closeout")


def test_quarantine_closeout_prefill_maps_transfer_packet_without_closing() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _write_quarantine_scope_fixture(root)
        scope_rows = build_artifact_invalidation_quarantine_scope_rows(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
        )
        index_rows = build_artifact_invalidation_quarantine_non_evidence_index_rows(
            scope_rows=scope_rows,
        )
        transfer_rows = build_artifact_invalidation_quarantine_transfer_packet_rows(
            index_rows=index_rows,
            scope_rows=scope_rows,
            project_root=root,
        )
        prefill_rows = build_artifact_invalidation_quarantine_closeout_prefill_rows(
            transfer_rows=transfer_rows,
        )
        prefill_summary = summarize_artifact_invalidation_quarantine_closeout_prefill_rows(
            prefill_rows
        )

    assert len(prefill_rows) == 6
    assert set(ARTIFACT_INVALIDATION_CLOSEOUT_FIELDS).issubset(prefill_rows[0])
    assert all(row["actual_disposition"] == "marked_non_evidence" for row in prefill_rows)
    assert all(row["closeout_status"] == "pending" for row in prefill_rows)
    assert all(row["rerun_result"] == "not_run" for row in prefill_rows)
    assert all(row["audit_result"] == "not_run" for row in prefill_rows)
    assert all(row["targeted_test_result"] == "not_run" for row in prefill_rows)
    assert all(row["reviewer_signoff_status"] == "unsigned" for row in prefill_rows)
    assert all(row["can_clear_invalidation_gate"] == "false" for row in prefill_rows)
    assert all(row["publication_ready"] == "false" for row in prefill_rows)
    assert all(row["final_study_ready"] == "false" for row in prefill_rows)
    assert prefill_summary["source_action_batch"] == "quarantine_non_evidence"
    assert prefill_summary["prefill_only"] is True
    assert prefill_summary["prefilled_row_count"] == 6
    assert prefill_summary["pending_or_invalid_row_count"] == 6
    assert prefill_summary["phase9_promotion_ready"] is False
    assert prefill_summary["must_not_be_used_as_closeout_manifest"] is True
    first_artifacts = json.loads(prefill_rows[0]["affected_artifacts_json"])
    assert first_artifacts
    assert all(
        artifact["current_integrity_status"] == "hash_match"
        for artifact in first_artifacts
    )

    print("PASS: quarantine closeout prefill maps transfer packet without closing")


def test_write_quarantine_closeout_prefill_outputs_are_non_acceptance() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _write_quarantine_scope_fixture(root)
        write_artifact_invalidation_quarantine_transfer_packet(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
            output_path=root / "transfer.csv",
            manifest_path=root / "transfer.json",
            doc_path=root / "transfer.md",
        )
        summary = write_artifact_invalidation_quarantine_closeout_prefill(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
            output_path=root / "prefill.csv",
            manifest_path=root / "prefill.json",
            doc_path=root / "prefill.md",
            source_transfer_packet_manifest=root / "transfer.json",
        )
        loaded = json.loads((root / "prefill.json").read_text(encoding="utf-8"))
        text = (root / "prefill.md").read_text(encoding="utf-8")
        with (root / "prefill.csv").open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        csv_sha256 = hashlib.sha256((root / "prefill.csv").read_bytes()).hexdigest()
        transfer_sha256 = hashlib.sha256((root / "transfer.json").read_bytes()).hexdigest()
        transfer_manifest = json.loads((root / "transfer.json").read_text(encoding="utf-8"))

    assert rows
    assert loaded["csv_sha256"] == csv_sha256
    assert loaded["source_transfer_packet_manifest"].endswith("transfer.json")
    assert loaded["source_transfer_packet_manifest_status"] == "loaded"
    assert loaded["source_transfer_packet_manifest_sha256"] == transfer_sha256
    assert loaded["source_transfer_packet_row_count"] == transfer_manifest["row_count"]
    assert (
        loaded["source_transfer_packet_candidate_artifact_count"]
        == transfer_manifest["candidate_artifact_count"]
    )
    assert (
        loaded["source_transfer_packet_integrity_ready"]
        is transfer_manifest["source_integrity_ready"]
    )
    assert loaded["source_transfer_packet_must_not_be_used_as_closeout_manifest"] is True
    assert summary["prefill_only"] is True
    assert loaded["phase9_promotion_ready"] is False
    assert loaded["publication_ready"] is False
    assert loaded["final_study_ready"] is False
    assert loaded["formal_acceptance_evidence"] is False
    assert loaded["can_clear_invalidation_gate"] is False
    assert loaded["acceptance_ready"] is False
    assert loaded["must_not_be_used_as_closeout_manifest"] is True
    assert "prefill only" in text
    assert "not closeout evidence" in text
    assert "not authorization for Phase 9" in text
    assert "Source transfer packet SHA256" in text

    print("PASS: quarantine closeout prefill outputs remain non-acceptance")


def test_quarantine_closeout_prefill_cannot_be_used_as_main_closeout_manifest() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _write_quarantine_scope_fixture(root)
        matrix_manifest = root / "ready_matrix.json"
        prefill_manifest = root / "prefill.json"
        _write_matrix_manifest(
            matrix_manifest,
            row_count=51,
            blocking_row_count=0,
            phase9_promotion_ready=True,
            upstream_ok=True,
            phase9_ok=True,
        )
        write_artifact_invalidation_quarantine_closeout_prefill(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
            output_path=root / "prefill.csv",
            manifest_path=prefill_manifest,
            doc_path=root / "prefill.md",
        )

        blocks, blockers, summary = artifact_invalidation_blocks_phase9(
            matrix_manifest,
            prefill_manifest,
        )

    assert blocks is True
    assert summary["closeout_snapshot"]["pending_or_invalid_row_count"] == 6
    assert any("does not cover every matrix row" in blocker for blocker in blockers)
    assert any("pending or invalid rows" in blocker for blocker in blockers)
    assert any("cannot be used as closeout manifest" in blocker for blocker in blockers)

    print("PASS: quarantine closeout prefill cannot be used as main closeout")


def test_quarantine_closeout_prefill_gap_audit_lists_remaining_work() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _write_quarantine_scope_fixture(root)
        write_artifact_invalidation_quarantine_transfer_packet(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
            output_path=root / "transfer.csv",
            manifest_path=root / "transfer.json",
            doc_path=root / "transfer.md",
        )
        gap_rows = build_artifact_invalidation_quarantine_closeout_prefill_gap_audit_rows(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
            source_transfer_packet_manifest=root / "transfer.json",
        )
        gap_summary = (
            summarize_artifact_invalidation_quarantine_closeout_prefill_gap_audit_rows(
                gap_rows
            )
        )

    assert len(gap_rows) == 6
    assert set(ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL_GAP_FIELDS).issubset(
        gap_rows[0]
    )
    assert gap_summary["prefill_gap_audit_only"] is True
    assert gap_summary["blocking_gap_row_count"] == 6
    assert gap_summary["can_clear_invalidation_gate"] is False
    assert gap_summary["phase9_promotion_ready"] is False
    assert gap_summary["must_not_be_used_as_closeout_manifest"] is True
    assert gap_summary["candidate_artifact_count"] > 0
    assert gap_summary["reference_hit_count"] > 0
    assert all(row["can_clear_invalidation_gate"] == "false" for row in gap_rows)
    assert all(row["must_not_be_used_as_closeout_manifest"] == "true" for row in gap_rows)
    row_number_by_id = {
        row["invalidation_row_id"]: row["main_closeout_template_row_number"]
        for row in gap_rows
    }
    assert row_number_by_id["region_boundary->full_outputs"] == "5"
    assert row_number_by_id["road_snapshot_or_evidence->full_outputs"] == "12"
    assert row_number_by_id["rail_source_or_timing->full_outputs"] == "18"
    assert (
        row_number_by_id["demand_fleet_behavior_transfer_dispatch->full_outputs"]
        == "22"
    )
    assert row_number_by_id["disruption_library_or_exposure->full_outputs"] == "30"
    assert row_number_by_id["claim_boundary_or_readiness_logic->review_packages"] == "50"
    first_codes = json.loads(gap_rows[0]["blocking_gap_codes_json"])
    assert "artifact_or_exclusion_confirmation_missing" in first_codes
    assert "audit_not_passed" in first_codes
    assert "targeted_test_not_passed" in first_codes
    assert "reviewer_signoff_missing" in first_codes
    assert "main_closeout_copy_required" in first_codes

    print("PASS: quarantine closeout prefill gap audit lists remaining work")


def test_quarantine_closeout_prefill_gap_audit_uses_closeout_schema_status_values() -> None:
    row = build_artifact_invalidation_quarantine_closeout_prefill_rows(
        transfer_rows=[]
    )[0]
    row.update(
        {
            "closeout_status": "closed_invalidation_only",
            "rerun_result": "pass",
            "audit_result": "pass",
            "targeted_test_result": "pass",
            "claim_boundary_review_result": "pass",
            "reviewer_signoff_status": "signed_off_for_invalidation_closeout_only",
            "can_clear_invalidation_gate": "false",
        }
    )
    gap_rows = build_artifact_invalidation_quarantine_closeout_prefill_gap_audit_rows(
        prefill_rows=[row],
        transfer_rows=[],
    )

    assert len(gap_rows) == 1
    gap_row = gap_rows[0]
    gap_codes = json.loads(gap_row["blocking_gap_codes_json"])
    assert "closeout_status_not_closed" not in gap_codes
    assert "rerun_not_passed" not in gap_codes
    assert "audit_not_passed" not in gap_codes
    assert "targeted_test_not_passed" not in gap_codes
    assert "claim_boundary_review_missing" not in gap_codes
    assert "reviewer_signoff_missing" not in gap_codes
    assert "main_closeout_copy_required" in gap_codes
    assert gap_row["rerun_gap"] == "no_gap_detected"
    assert gap_row["audit_gap"] == "no_gap_detected"
    assert gap_row["targeted_test_gap"] == "no_gap_detected"
    assert gap_row["claim_boundary_review_gap"] == "no_gap_detected"
    assert gap_row["reviewer_signoff_gap"] == "no_gap_detected"
    assert gap_row["can_clear_invalidation_gate"] == "false"
    assert gap_row["phase9_promotion_ready"] == "false"
    assert gap_row["main_closeout_template_row_number"]

    print("PASS: quarantine closeout prefill gap audit uses closeout schema status values")


def test_write_quarantine_closeout_prefill_gap_audit_outputs_are_non_acceptance() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _write_quarantine_scope_fixture(root)
        write_artifact_invalidation_quarantine_transfer_packet(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
            output_path=root / "transfer.csv",
            manifest_path=root / "transfer.json",
            doc_path=root / "transfer.md",
        )
        summary = write_artifact_invalidation_quarantine_closeout_prefill_gap_audit(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
            output_path=root / "gap.csv",
            manifest_path=root / "gap.json",
            doc_path=root / "gap.md",
            source_transfer_packet_manifest=root / "transfer.json",
        )
        loaded = json.loads((root / "gap.json").read_text(encoding="utf-8"))
        text = (root / "gap.md").read_text(encoding="utf-8")
        with (root / "gap.csv").open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        csv_sha256 = hashlib.sha256((root / "gap.csv").read_bytes()).hexdigest()
        transfer_sha256 = hashlib.sha256((root / "transfer.json").read_bytes()).hexdigest()

    assert rows
    assert loaded["csv_sha256"] == csv_sha256
    assert loaded["source_transfer_packet_manifest"].endswith("transfer.json")
    assert loaded["source_transfer_packet_manifest_status"] == "loaded"
    assert loaded["source_transfer_packet_manifest_sha256"] == transfer_sha256
    assert loaded["prefill_gap_audit_only"] is True
    assert summary["blocking_gap_row_count"] == 6
    assert loaded["phase9_promotion_ready"] is False
    assert loaded["publication_ready"] is False
    assert loaded["final_study_ready"] is False
    assert loaded["formal_acceptance_evidence"] is False
    assert loaded["can_clear_invalidation_gate"] is False
    assert loaded["must_not_be_used_as_closeout_manifest"] is True
    assert "reviewer-action checklist" in text
    assert "does not replace the main closeout record" in text
    assert "does not promote Phase 9 outputs" in text

    print("PASS: quarantine closeout prefill gap audit outputs remain non-acceptance")


def test_quarantine_main_closeout_copy_audit_detects_missing_main_copy() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _write_quarantine_scope_fixture(root)
        prefill_rows = build_artifact_invalidation_quarantine_closeout_prefill_rows(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
        )
        rows = build_artifact_invalidation_quarantine_main_closeout_copy_audit_rows(
            prefill_rows=prefill_rows,
            main_closeout_rows=build_artifact_invalidation_closeout_template_rows(),
        )
        summary = summarize_artifact_invalidation_quarantine_main_closeout_copy_audit_rows(
            rows
        )

    assert len(rows) == 6
    assert set(ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_COPY_AUDIT_FIELDS).issubset(
        rows[0]
    )
    assert summary["copy_audit_only"] is True
    assert summary["main_row_found_count"] == 6
    assert summary["affected_artifacts_copied_count"] == 0
    assert summary["actual_disposition_copied_count"] == 0
    assert summary["blocking_copy_audit_row_count"] == 6
    assert summary["can_clear_invalidation_gate"] is False
    assert summary["must_not_be_used_as_closeout_manifest"] is True
    first_codes = json.loads(rows[0]["main_closeout_gap_codes_json"])
    assert "main_affected_artifacts_not_copied" in first_codes
    assert "main_actual_disposition_not_copied" in first_codes
    assert "main:actual_disposition_not_confirmed" in first_codes
    assert "main:reviewer_signoff_missing" in first_codes
    assert rows[0]["copy_audit_status"] == "main_closeout_copy_incomplete"
    assert rows[0]["can_clear_invalidation_gate"] == "false"

    print("PASS: quarantine main closeout copy audit detects missing main copy")


def test_write_quarantine_main_closeout_copy_audit_outputs_are_non_acceptance() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _write_quarantine_scope_fixture(root)
        prefill_path = root / "prefill.csv"
        main_path = root / "main_closeout.csv"
        write_artifact_invalidation_quarantine_closeout_prefill(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
            output_path=prefill_path,
            manifest_path=root / "prefill.json",
            doc_path=root / "prefill.md",
        )
        write_artifact_invalidation_closeout_template(
            output_path=main_path,
            manifest_path=root / "main_closeout.json",
            doc_path=root / "main_closeout.md",
        )
        prefill_rows = read_artifact_invalidation_closeout_rows(prefill_path)
        main_rows = read_artifact_invalidation_closeout_rows(main_path)
        summary = write_artifact_invalidation_quarantine_main_closeout_copy_audit(
            prefill_rows=prefill_rows,
            main_closeout_rows=main_rows,
            output_path=root / "copy.csv",
            manifest_path=root / "copy.json",
            doc_path=root / "copy.md",
            source_prefill_path=prefill_path,
            source_main_closeout_path=main_path,
        )
        loaded = json.loads((root / "copy.json").read_text(encoding="utf-8"))
        text = (root / "copy.md").read_text(encoding="utf-8")
        with (root / "copy.csv").open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        csv_sha256 = hashlib.sha256((root / "copy.csv").read_bytes()).hexdigest()

    assert rows
    assert summary["row_count"] == 6
    assert loaded["csv_sha256"] == csv_sha256
    assert loaded["source_prefill_path"].endswith("prefill.csv")
    assert loaded["source_main_closeout_path"].endswith("main_closeout.csv")
    assert loaded["copy_audit_only"] is True
    assert loaded["blocking_copy_audit_row_count"] == 6
    assert loaded["phase9_promotion_ready"] is False
    assert loaded["publication_ready"] is False
    assert loaded["final_study_ready"] is False
    assert loaded["formal_acceptance_evidence"] is False
    assert loaded["must_not_be_used_as_closeout_manifest"] is True
    assert "does not close any invalidation row" in text
    assert "passing main closeout support audit" in text

    print("PASS: quarantine main closeout copy audit outputs remain non-acceptance")


def test_quarantine_main_closeout_draft_overlay_prefills_without_closing() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _write_quarantine_scope_fixture(root)
        prefill_rows = build_artifact_invalidation_quarantine_closeout_prefill_rows(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
        )
        rows = build_artifact_invalidation_quarantine_main_closeout_draft_overlay_rows(
            prefill_rows=prefill_rows,
            main_closeout_rows=build_artifact_invalidation_closeout_template_rows(),
        )
        summary = summarize_artifact_invalidation_quarantine_main_closeout_draft_overlay_rows(
            rows,
            prefill_row_ids=[row["invalidation_row_id"] for row in prefill_rows],
        )

    overlay_rows = [
        row
        for row in rows
        if "draft overlay from quarantine prefill" in row["review_notes"]
    ]
    assert len(rows) == 51
    assert len(overlay_rows) == 6
    assert summary["draft_overlay_only"] is True
    assert summary["overlayed_row_count"] == 6
    assert summary["closed_candidate_count"] == 0
    assert summary["pending_or_invalid_row_count"] == 51
    assert summary["can_clear_invalidation_gate"] is False
    assert summary["must_not_be_used_as_closeout_manifest"] is True
    assert summary["must_not_replace_main_closeout_record"] is True
    assert all(row["closeout_status"] == "pending" for row in rows)
    assert all(row["rerun_result"] == "not_run" for row in rows)
    assert all(row["audit_result"] == "not_run" for row in rows)
    assert all(row["targeted_test_result"] == "not_run" for row in rows)
    assert all(row["reviewer_signoff_status"] == "unsigned" for row in rows)
    assert all(row["can_clear_invalidation_gate"] == "false" for row in rows)
    assert any(row["actual_disposition"] == "marked_non_evidence" for row in overlay_rows)
    assert all(row["affected_artifacts_json"] != "[]" for row in overlay_rows)

    print("PASS: quarantine main closeout draft overlay pre-fills without closing")


def test_write_quarantine_main_closeout_draft_overlay_outputs_are_non_acceptance() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _write_quarantine_scope_fixture(root)
        prefill_path = root / "prefill.csv"
        main_path = root / "main_closeout.csv"
        write_artifact_invalidation_quarantine_closeout_prefill(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
            output_path=prefill_path,
            manifest_path=root / "prefill.json",
            doc_path=root / "prefill.md",
        )
        write_artifact_invalidation_closeout_template(
            output_path=main_path,
            manifest_path=root / "main_closeout.json",
            doc_path=root / "main_closeout.md",
        )
        prefill_rows = read_artifact_invalidation_closeout_rows(prefill_path)
        main_rows = read_artifact_invalidation_closeout_rows(main_path)
        summary = write_artifact_invalidation_quarantine_main_closeout_draft_overlay(
            prefill_rows=prefill_rows,
            main_closeout_rows=main_rows,
            output_path=root / "overlay.csv",
            manifest_path=root / "overlay.json",
            doc_path=root / "overlay.md",
            source_prefill_path=prefill_path,
            source_main_closeout_path=main_path,
        )
        loaded = json.loads((root / "overlay.json").read_text(encoding="utf-8"))
        text = (root / "overlay.md").read_text(encoding="utf-8")
        with (root / "overlay.csv").open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        csv_sha256 = hashlib.sha256((root / "overlay.csv").read_bytes()).hexdigest()

    assert rows
    assert summary["row_count"] == 51
    assert loaded["csv_sha256"] == csv_sha256
    assert loaded["source_prefill_path"].endswith("prefill.csv")
    assert loaded["source_main_closeout_path"].endswith("main_closeout.csv")
    assert loaded["draft_overlay_only"] is True
    assert loaded["overlayed_row_count"] == 6
    assert loaded["closed_candidate_count"] == 0
    assert loaded["phase9_promotion_ready"] is False
    assert loaded["publication_ready"] is False
    assert loaded["final_study_ready"] is False
    assert loaded["formal_acceptance_evidence"] is False
    assert loaded["must_not_be_used_as_closeout_manifest"] is True
    assert loaded["must_not_replace_main_closeout_record"] is True
    assert "non-authoritative" in text
    assert "keeps every row pending" in text
    assert len(rows) == 51
    assert set(ARTIFACT_INVALIDATION_CLOSEOUT_FIELDS).issubset(rows[0])

    print("PASS: quarantine main closeout draft overlay outputs remain non-acceptance")


def test_quarantine_reference_triage_splits_reference_priorities() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _write_quarantine_scope_fixture(root)
        transfer_rows = build_artifact_invalidation_quarantine_transfer_packet_rows(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
        )
        transfer_rows[0]["current_reference_hit_count"] = "4"
        transfer_rows[0]["reference_hit_paths_json"] = json.dumps(
            [
                "README.md",
                "plan.md",
                "docs/artifact_invalidation_closeout_action_queue.md",
                "docs/realworld_pipeline.md",
            ]
        )
        rows = build_artifact_invalidation_quarantine_reference_triage_rows(
            transfer_rows=transfer_rows,
            source_transfer_packet_manifest=root / "missing_transfer.json",
        )
        summary = summarize_artifact_invalidation_quarantine_reference_triage_rows(
            rows
        )

    assert len(rows) >= 4
    assert set(ARTIFACT_INVALIDATION_QUARANTINE_REFERENCE_TRIAGE_FIELDS).issubset(
        rows[0]
    )
    assert summary["reference_triage_only"] is True
    assert summary["can_clear_invalidation_gate"] is False
    assert summary["phase9_promotion_ready"] is False
    assert summary["must_not_be_used_as_closeout_manifest"] is True
    classes = {row["reference_path"]: row["reference_classification"] for row in rows}
    assert classes["README.md"] == "active_claim_text_candidate"
    assert classes["plan.md"] == "planning_or_status_reference"
    assert (
        classes["docs/artifact_invalidation_closeout_action_queue.md"]
        == "generated_audit_or_review_support_reference"
    )
    assert classes["docs/realworld_pipeline.md"] == "documentation_claim_candidate"
    assert any(row["review_priority"] == "review_first" for row in rows)
    assert all(row["can_clear_invalidation_gate"] == "false" for row in rows)

    print("PASS: quarantine reference triage splits reference priorities")


def test_write_quarantine_reference_triage_outputs_are_non_acceptance() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _write_quarantine_scope_fixture(root)
        write_artifact_invalidation_quarantine_transfer_packet(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
            output_path=root / "transfer.csv",
            manifest_path=root / "transfer.json",
            doc_path=root / "transfer.md",
        )
        summary = write_artifact_invalidation_quarantine_reference_triage(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
            output_path=root / "triage.csv",
            manifest_path=root / "triage.json",
            doc_path=root / "triage.md",
            source_transfer_packet_manifest=root / "transfer.json",
        )
        loaded = json.loads((root / "triage.json").read_text(encoding="utf-8"))
        text = (root / "triage.md").read_text(encoding="utf-8")
        with (root / "triage.csv").open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        csv_sha256 = hashlib.sha256((root / "triage.csv").read_bytes()).hexdigest()
        transfer_sha256 = hashlib.sha256((root / "transfer.json").read_bytes()).hexdigest()

    assert rows
    assert loaded["csv_sha256"] == csv_sha256
    assert loaded["source_transfer_packet_manifest"].endswith("transfer.json")
    assert loaded["source_transfer_packet_manifest_sha256"] == transfer_sha256
    assert loaded["reference_triage_only"] is True
    assert summary["row_count"] == len(rows)
    assert loaded["phase9_promotion_ready"] is False
    assert loaded["publication_ready"] is False
    assert loaded["final_study_ready"] is False
    assert loaded["formal_acceptance_evidence"] is False
    assert loaded["must_not_be_used_as_closeout_manifest"] is True
    assert "not citation-removal evidence" in text
    assert "Reference Rows" in text
    assert set(ARTIFACT_INVALIDATION_QUARANTINE_REFERENCE_TRIAGE_FIELDS).issubset(
        rows[0]
    )

    print("PASS: quarantine reference triage outputs remain non-acceptance")


def test_claim_reference_remediation_filters_review_first_line_hits() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _write_quarantine_scope_fixture(root)
        scope_rows = build_artifact_invalidation_quarantine_scope_rows(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
        )
        triage_rows = build_artifact_invalidation_quarantine_reference_triage_rows(
            scope_rows=scope_rows,
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
            source_transfer_packet_manifest=root / "missing_transfer.json",
        )
        rows = build_artifact_invalidation_quarantine_claim_reference_remediation_rows(
            triage_rows=triage_rows,
            scope_rows=scope_rows,
            source_reference_triage_manifest=root / "missing_triage.json",
            source_scope_audit_manifest=root / "missing_scope.json",
        )
        summary = summarize_artifact_invalidation_quarantine_claim_reference_remediation_rows(
            rows
        )

    assert rows
    assert set(ARTIFACT_INVALIDATION_QUARANTINE_CLAIM_REFERENCE_REMEDIATION_FIELDS).issubset(
        rows[0]
    )
    assert all(row["review_priority"] == "review_first" for row in rows)
    assert all(row["line_scan_status"] == "line_hit" for row in rows)
    assert all(row["line_number"].isdigit() for row in rows)
    reference_paths = {row["reference_path"].replace("\\", "/") for row in rows}
    assert any(path.endswith("docs/scope_reference.md") for path in reference_paths)
    assert not any(path.endswith("plan.md") for path in reference_paths)
    assert summary["claim_reference_remediation_only"] is True
    assert summary["phase9_promotion_ready"] is False
    assert summary["must_not_be_used_as_closeout_manifest"] is True

    print("PASS: claim reference remediation filters review-first line hits")


def test_write_claim_reference_remediation_outputs_are_non_acceptance() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _write_quarantine_scope_fixture(root)
        write_artifact_invalidation_quarantine_scope_audit(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
            output_path=root / "scope.csv",
            manifest_path=root / "scope.json",
            doc_path=root / "scope.md",
        )
        write_artifact_invalidation_quarantine_transfer_packet(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
            output_path=root / "transfer.csv",
            manifest_path=root / "transfer.json",
            doc_path=root / "transfer.md",
            source_scope_audit_manifest=root / "scope.json",
        )
        write_artifact_invalidation_quarantine_reference_triage(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
            output_path=root / "triage.csv",
            manifest_path=root / "triage.json",
            doc_path=root / "triage.md",
            source_transfer_packet_manifest=root / "transfer.json",
        )
        summary = write_artifact_invalidation_quarantine_claim_reference_remediation_packet(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
            output_path=root / "remediation.csv",
            manifest_path=root / "remediation.json",
            doc_path=root / "remediation.md",
            source_reference_triage_manifest=root / "triage.json",
            source_scope_audit_manifest=root / "scope.json",
        )
        loaded = json.loads((root / "remediation.json").read_text(encoding="utf-8"))
        text = (root / "remediation.md").read_text(encoding="utf-8")
        with (root / "remediation.csv").open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        remediation_sha256 = hashlib.sha256((root / "remediation.csv").read_bytes()).hexdigest()
        triage_sha256 = hashlib.sha256((root / "triage.json").read_bytes()).hexdigest()
        scope_sha256 = hashlib.sha256((root / "scope.json").read_bytes()).hexdigest()

    assert rows
    assert loaded["csv_sha256"] == remediation_sha256
    assert loaded["source_reference_triage_manifest"].endswith("triage.json")
    assert loaded["source_reference_triage_manifest_sha256"] == triage_sha256
    assert loaded["source_scope_audit_manifest"].endswith("scope.json")
    assert loaded["source_scope_audit_manifest_sha256"] == scope_sha256
    assert loaded["claim_reference_remediation_only"] is True
    assert summary["row_count"] == len(rows)
    assert loaded["phase9_promotion_ready"] is False
    assert loaded["publication_ready"] is False
    assert loaded["final_study_ready"] is False
    assert loaded["formal_acceptance_evidence"] is False
    assert loaded["must_not_be_used_as_closeout_manifest"] is True
    assert "line-level edit tasks" in text
    assert "not the main closeout record" in text
    assert set(ARTIFACT_INVALIDATION_QUARANTINE_CLAIM_REFERENCE_REMEDIATION_FIELDS).issubset(
        rows[0]
    )

    print("PASS: claim reference remediation outputs remain non-acceptance")


def test_quarantine_manifest_cannot_be_used_as_main_closeout_manifest() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        matrix_manifest = root / "ready_matrix.json"
        quarantine_manifest = root / "quarantine.json"
        _write_matrix_manifest(
            matrix_manifest,
            row_count=51,
            blocking_row_count=0,
            phase9_promotion_ready=True,
            upstream_ok=True,
            phase9_ok=True,
        )
        write_artifact_invalidation_quarantine_closeout_template(
            output_path=root / "quarantine.csv",
            manifest_path=quarantine_manifest,
            doc_path=root / "quarantine.md",
        )

        blocks, blockers, _summary = artifact_invalidation_blocks_phase9(
            matrix_manifest,
            quarantine_manifest,
        )

    assert blocks is True
    assert any("does not cover every matrix row" in blocker for blocker in blockers)
    assert any("pending or invalid rows" in blocker for blocker in blockers)

    print("PASS: quarantine manifest cannot be used as the main closeout manifest")


def test_quarantine_scope_audit_cannot_be_used_as_main_closeout_manifest() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _write_quarantine_scope_fixture(root)
        matrix_manifest = root / "ready_matrix.json"
        scope_manifest = root / "scope.json"
        _write_matrix_manifest(
            matrix_manifest,
            row_count=51,
            blocking_row_count=0,
            phase9_promotion_ready=True,
            upstream_ok=True,
            phase9_ok=True,
        )
        write_artifact_invalidation_quarantine_scope_audit(
            project_root=root,
            search_roots=("docs", "plan.md", "review_packages"),
            output_path=root / "scope.csv",
            manifest_path=scope_manifest,
            doc_path=root / "scope.md",
        )

        blocks, blockers, _summary = artifact_invalidation_blocks_phase9(
            matrix_manifest,
            scope_manifest,
        )

    assert blocks is True
    assert any("non-closeout support manifest cannot be used" in blocker for blocker in blockers)

    print("PASS: quarantine scope audit cannot be used as the main closeout manifest")


def test_cli_writes_quarantine_template_without_main_closeout_when_requested() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        closeout_csv = root / "main_closeout.csv"
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "write_artifact_invalidation_matrix.py"),
                "--output",
                str(root / "matrix.csv"),
                "--manifest",
                str(root / "matrix.json"),
                "--doc",
                str(root / "matrix.md"),
                "--closeout-output",
                str(closeout_csv),
                "--closeout-manifest",
                str(root / "main_closeout.json"),
                "--closeout-doc",
                str(root / "main_closeout.md"),
                "--write-quarantine-closeout-template",
                "--quarantine-output",
                str(root / "quarantine.csv"),
                "--quarantine-manifest",
                str(root / "quarantine.json"),
                "--quarantine-doc",
                str(root / "quarantine.md"),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        payload = json.loads(result.stdout)
        quarantine_manifest = json.loads(
            (root / "quarantine.json").read_text(encoding="utf-8")
        )
        with (root / "quarantine.csv").open("r", encoding="utf-8", newline="") as handle:
            quarantine_rows = list(csv.DictReader(handle))

        assert (root / "matrix.csv").exists()
        assert (root / "quarantine.csv").exists()
        assert not closeout_csv.exists()

    assert payload["quarantine_closeout_template"]["row_count"] == 6
    assert "closeout_template" not in payload
    assert quarantine_manifest["phase9_promotion_ready"] is False
    assert quarantine_manifest["publication_ready"] is False
    assert len(quarantine_rows) == 6

    print("PASS: CLI writes quarantine template without main closeout")


def test_cli_writes_closeout_readiness_audit_when_requested() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "write_artifact_invalidation_matrix.py"),
                "--output",
                str(root / "matrix.csv"),
                "--manifest",
                str(root / "matrix.json"),
                "--doc",
                str(root / "matrix.md"),
                "--write-closeout-readiness-audit",
                "--closeout-readiness-output",
                str(root / "readiness.csv"),
                "--closeout-readiness-manifest",
                str(root / "readiness.json"),
                "--closeout-readiness-doc",
                str(root / "readiness.md"),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        payload = json.loads(result.stdout)
        readiness_manifest = json.loads(
            (root / "readiness.json").read_text(encoding="utf-8")
        )
        with (root / "readiness.csv").open("r", encoding="utf-8", newline="") as handle:
            readiness_rows = list(csv.DictReader(handle))

    assert payload["closeout_readiness_audit"]["row_count"] == 51
    assert readiness_manifest["must_not_be_used_as_closeout_manifest"] is True
    assert readiness_manifest["phase9_promotion_ready"] is False
    assert readiness_rows
    assert set(ARTIFACT_INVALIDATION_CLOSEOUT_READINESS_FIELDS).issubset(
        readiness_rows[0]
    )

    print("PASS: CLI writes closeout readiness audit when requested")


def test_cli_writes_action_batch_inspection_when_requested() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "write_artifact_invalidation_matrix.py"),
                "--output",
                str(root / "matrix.csv"),
                "--manifest",
                str(root / "matrix.json"),
                "--doc",
                str(root / "matrix.md"),
                "--write-action-batch-inspection",
                "--action-batch-inspection-output",
                str(root / "inspection.csv"),
                "--action-batch-inspection-manifest",
                str(root / "inspection.json"),
                "--action-batch-inspection-doc",
                str(root / "inspection.md"),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        payload = json.loads(result.stdout)
        inspection_manifest = json.loads(
            (root / "inspection.json").read_text(encoding="utf-8")
        )
        with (root / "inspection.csv").open("r", encoding="utf-8", newline="") as handle:
            inspection_rows = list(csv.DictReader(handle))

    assert payload["action_batch_inspection"]["row_count"] == 51
    assert inspection_manifest["must_not_be_used_as_closeout_manifest"] is True
    assert inspection_manifest["phase9_promotion_ready"] is False
    assert inspection_manifest["publication_ready"] is False
    assert inspection_rows
    assert set(ARTIFACT_INVALIDATION_ACTION_BATCH_INSPECTION_FIELDS).issubset(
        inspection_rows[0]
    )

    print("PASS: CLI writes action-batch inspection when requested")


def test_cli_closeout_readiness_audit_reads_filled_closeout_input() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        manifest_path = root / "blocked_manifest.json"
        closeout_csv = root / "filled_closeout.csv"
        _write_compact_manifest(manifest_path, engineering_only=True)
        row = _closed_closeout_row()
        row["affected_artifacts_json"] = _artifact_json_for_path(manifest_path)
        row["downstream_after_artifacts_json"] = _artifact_json_for_path(manifest_path)
        with closeout_csv.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=ARTIFACT_INVALIDATION_CLOSEOUT_FIELDS)
            writer.writeheader()
            writer.writerow(row)
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "write_artifact_invalidation_matrix.py"),
                "--output",
                str(root / "matrix.csv"),
                "--manifest",
                str(root / "matrix.json"),
                "--doc",
                str(root / "matrix.md"),
                "--write-closeout-readiness-audit",
                "--closeout-readiness-closeout-input",
                str(closeout_csv),
                "--closeout-readiness-output",
                str(root / "readiness.csv"),
                "--closeout-readiness-manifest",
                str(root / "readiness.json"),
                "--closeout-readiness-doc",
                str(root / "readiness.md"),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        readiness_manifest = json.loads(
            (root / "readiness.json").read_text(encoding="utf-8")
        )
        with (root / "readiness.csv").open("r", encoding="utf-8", newline="") as handle:
            readiness_rows = list(csv.DictReader(handle))

    assert payload["closeout_readiness_audit"]["row_count"] == 1
    assert readiness_manifest["source_closeout_input"].endswith("filled_closeout.csv")
    assert readiness_manifest["compact_source_blocked_count"] == 1
    assert readiness_rows[0]["source_engineering_only"] == "true"
    assert readiness_rows[0]["compact_closeout_eligibility_status"].startswith("blocked")

    print("PASS: CLI closeout readiness audit reads filled closeout input")


def test_cli_writes_quarantine_scope_audit_when_requested() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "write_artifact_invalidation_matrix.py"),
                "--output",
                str(root / "matrix.csv"),
                "--manifest",
                str(root / "matrix.json"),
                "--doc",
                str(root / "matrix.md"),
                "--write-quarantine-scope-audit",
                "--quarantine-scope-output",
                str(root / "scope.csv"),
                "--quarantine-scope-manifest",
                str(root / "scope.json"),
                "--quarantine-scope-doc",
                str(root / "scope.md"),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        payload = json.loads(result.stdout)
        scope_manifest = json.loads((root / "scope.json").read_text(encoding="utf-8"))
        with (root / "scope.csv").open("r", encoding="utf-8", newline="") as handle:
            scope_rows = list(csv.DictReader(handle))

    assert payload["quarantine_scope_audit"]["must_not_be_used_as_closeout_manifest"] is True
    assert scope_manifest["phase9_promotion_ready"] is False
    assert scope_manifest["publication_ready"] is False
    assert scope_rows
    assert set(ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_FIELDS).issubset(scope_rows[0])

    print("PASS: CLI writes quarantine scope audit when requested")


def test_cli_writes_quarantine_non_evidence_index_when_requested() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "write_artifact_invalidation_matrix.py"),
                "--output",
                str(root / "matrix.csv"),
                "--manifest",
                str(root / "matrix.json"),
                "--doc",
                str(root / "matrix.md"),
                "--write-quarantine-non-evidence-index",
                "--quarantine-non-evidence-index-output",
                str(root / "index.csv"),
                "--quarantine-non-evidence-index-manifest",
                str(root / "index.json"),
                "--quarantine-non-evidence-index-doc",
                str(root / "index.md"),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        payload = json.loads(result.stdout)
        index_manifest = json.loads((root / "index.json").read_text(encoding="utf-8"))
        with (root / "index.csv").open("r", encoding="utf-8", newline="") as handle:
            index_rows = list(csv.DictReader(handle))

    assert "quarantine_non_evidence_index" in payload
    assert "closeout_template" not in payload
    assert "quarantine_closeout_template" not in payload
    assert "quarantine_scope_audit" not in payload
    assert index_manifest["phase9_promotion_ready"] is False
    assert index_manifest["must_not_be_used_as_closeout_manifest"] is True
    assert index_rows

    print("PASS: CLI writes quarantine non-evidence index when requested")


def test_cli_writes_quarantine_non_evidence_transfer_packet_when_requested() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "write_artifact_invalidation_matrix.py"),
                "--output",
                str(root / "matrix.csv"),
                "--manifest",
                str(root / "matrix.json"),
                "--doc",
                str(root / "matrix.md"),
                "--write-quarantine-non-evidence-transfer-packet",
                "--quarantine-non-evidence-transfer-output",
                str(root / "transfer.csv"),
                "--quarantine-non-evidence-transfer-manifest",
                str(root / "transfer.json"),
                "--quarantine-non-evidence-transfer-doc",
                str(root / "transfer.md"),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        payload = json.loads(result.stdout)
        transfer_manifest = json.loads((root / "transfer.json").read_text(encoding="utf-8"))
        transfer_text = (root / "transfer.md").read_text(encoding="utf-8")
        with (root / "transfer.csv").open("r", encoding="utf-8", newline="") as handle:
            transfer_rows = list(csv.DictReader(handle))

    assert "quarantine_non_evidence_transfer_packet" in payload
    assert "closeout_template" not in payload
    assert transfer_manifest["row_count"] == 6
    assert transfer_manifest["phase9_promotion_ready"] is False
    assert transfer_manifest["must_not_be_used_as_closeout_manifest"] is True
    assert "not closeout evidence" in transfer_text
    assert len(transfer_rows) == 6

    print("PASS: CLI writes quarantine non-evidence transfer packet when requested")


def test_cli_writes_quarantine_closeout_prefill_when_requested() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "write_artifact_invalidation_matrix.py"),
                "--output",
                str(root / "matrix.csv"),
                "--manifest",
                str(root / "matrix.json"),
                "--doc",
                str(root / "matrix.md"),
                "--write-quarantine-non-evidence-transfer-packet",
                "--quarantine-non-evidence-transfer-output",
                str(root / "transfer.csv"),
                "--quarantine-non-evidence-transfer-manifest",
                str(root / "transfer.json"),
                "--quarantine-non-evidence-transfer-doc",
                str(root / "transfer.md"),
                "--write-quarantine-closeout-prefill",
                "--quarantine-closeout-prefill-output",
                str(root / "prefill.csv"),
                "--quarantine-closeout-prefill-manifest",
                str(root / "prefill.json"),
                "--quarantine-closeout-prefill-doc",
                str(root / "prefill.md"),
                "--quarantine-closeout-prefill-source-transfer-manifest",
                str(root / "transfer.json"),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        payload = json.loads(result.stdout)
        prefill_manifest = json.loads((root / "prefill.json").read_text(encoding="utf-8"))
        prefill_text = (root / "prefill.md").read_text(encoding="utf-8")
        with (root / "prefill.csv").open("r", encoding="utf-8", newline="") as handle:
            prefill_rows = list(csv.DictReader(handle))
        transfer_sha256 = hashlib.sha256((root / "transfer.json").read_bytes()).hexdigest()
        transfer_manifest = json.loads((root / "transfer.json").read_text(encoding="utf-8"))

    assert "quarantine_closeout_prefill" in payload
    assert "quarantine_non_evidence_transfer_packet" in payload
    assert prefill_manifest["row_count"] == 6
    assert prefill_manifest["prefill_only"] is True
    assert prefill_manifest["source_transfer_packet_manifest_status"] == "loaded"
    assert prefill_manifest["source_transfer_packet_manifest_sha256"] == transfer_sha256
    assert (
        prefill_manifest["source_transfer_packet_candidate_artifact_count"]
        == transfer_manifest["candidate_artifact_count"]
    )
    assert (
        prefill_manifest["source_transfer_packet_integrity_ready"]
        is transfer_manifest["source_integrity_ready"]
    )
    assert prefill_manifest["phase9_promotion_ready"] is False
    assert prefill_manifest["must_not_be_used_as_closeout_manifest"] is True
    assert "not closeout evidence" in prefill_text
    assert len(prefill_rows) == 6
    assert set(ARTIFACT_INVALIDATION_CLOSEOUT_FIELDS).issubset(prefill_rows[0])

    print("PASS: CLI writes quarantine closeout prefill when requested")


def test_cli_writes_quarantine_closeout_prefill_gap_audit_when_requested() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "write_artifact_invalidation_matrix.py"),
                "--output",
                str(root / "matrix.csv"),
                "--manifest",
                str(root / "matrix.json"),
                "--doc",
                str(root / "matrix.md"),
                "--write-quarantine-non-evidence-transfer-packet",
                "--quarantine-non-evidence-transfer-output",
                str(root / "transfer.csv"),
                "--quarantine-non-evidence-transfer-manifest",
                str(root / "transfer.json"),
                "--quarantine-non-evidence-transfer-doc",
                str(root / "transfer.md"),
                "--write-quarantine-closeout-prefill-gap-audit",
                "--quarantine-closeout-prefill-gap-audit-output",
                str(root / "gap.csv"),
                "--quarantine-closeout-prefill-gap-audit-manifest",
                str(root / "gap.json"),
                "--quarantine-closeout-prefill-gap-audit-doc",
                str(root / "gap.md"),
                "--quarantine-closeout-prefill-gap-audit-source-transfer-manifest",
                str(root / "transfer.json"),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        payload = json.loads(result.stdout)
        gap_manifest = json.loads((root / "gap.json").read_text(encoding="utf-8"))
        gap_text = (root / "gap.md").read_text(encoding="utf-8")
        with (root / "gap.csv").open("r", encoding="utf-8", newline="") as handle:
            gap_rows = list(csv.DictReader(handle))
        transfer_sha256 = hashlib.sha256((root / "transfer.json").read_bytes()).hexdigest()

    assert "quarantine_closeout_prefill_gap_audit" in payload
    assert "quarantine_non_evidence_transfer_packet" in payload
    assert gap_manifest["row_count"] == 6
    assert gap_manifest["prefill_gap_audit_only"] is True
    assert gap_manifest["blocking_gap_row_count"] == 6
    assert gap_manifest["source_transfer_packet_manifest_status"] == "loaded"
    assert gap_manifest["source_transfer_packet_manifest_sha256"] == transfer_sha256
    assert gap_manifest["phase9_promotion_ready"] is False
    assert gap_manifest["must_not_be_used_as_closeout_manifest"] is True
    assert "does not close artifact invalidation rows" in gap_text
    assert len(gap_rows) == 6
    assert set(ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL_GAP_FIELDS).issubset(
        gap_rows[0]
    )

    print("PASS: CLI writes quarantine closeout prefill gap audit when requested")


def test_cli_writes_quarantine_main_closeout_copy_audit_when_requested() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "write_artifact_invalidation_matrix.py"),
                "--output",
                str(root / "matrix.csv"),
                "--manifest",
                str(root / "matrix.json"),
                "--doc",
                str(root / "matrix.md"),
                "--write-closeout-template",
                "--closeout-output",
                str(root / "main_closeout.csv"),
                "--closeout-manifest",
                str(root / "main_closeout.json"),
                "--closeout-doc",
                str(root / "main_closeout.md"),
                "--write-quarantine-non-evidence-transfer-packet",
                "--quarantine-non-evidence-transfer-output",
                str(root / "transfer.csv"),
                "--quarantine-non-evidence-transfer-manifest",
                str(root / "transfer.json"),
                "--quarantine-non-evidence-transfer-doc",
                str(root / "transfer.md"),
                "--write-quarantine-closeout-prefill",
                "--quarantine-closeout-prefill-output",
                str(root / "prefill.csv"),
                "--quarantine-closeout-prefill-manifest",
                str(root / "prefill.json"),
                "--quarantine-closeout-prefill-doc",
                str(root / "prefill.md"),
                "--write-quarantine-main-closeout-copy-audit",
                "--quarantine-main-closeout-copy-audit-output",
                str(root / "copy.csv"),
                "--quarantine-main-closeout-copy-audit-manifest",
                str(root / "copy.json"),
                "--quarantine-main-closeout-copy-audit-doc",
                str(root / "copy.md"),
                "--quarantine-main-closeout-copy-audit-prefill-input",
                str(root / "prefill.csv"),
                "--quarantine-main-closeout-copy-audit-main-closeout-input",
                str(root / "main_closeout.csv"),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        payload = json.loads(result.stdout)
        copy_manifest = json.loads((root / "copy.json").read_text(encoding="utf-8"))
        copy_text = (root / "copy.md").read_text(encoding="utf-8")
        with (root / "copy.csv").open("r", encoding="utf-8", newline="") as handle:
            copy_rows = list(csv.DictReader(handle))

    assert "quarantine_main_closeout_copy_audit" in payload
    assert "quarantine_closeout_prefill" in payload
    assert "closeout_template" in payload
    assert copy_manifest["copy_audit_only"] is True
    assert copy_manifest["row_count"] == 6
    assert copy_manifest["blocking_copy_audit_row_count"] == 6
    assert copy_manifest["main_row_found_count"] == 6
    assert copy_manifest["phase9_promotion_ready"] is False
    assert copy_manifest["must_not_be_used_as_closeout_manifest"] is True
    assert "does not close any invalidation row" in copy_text
    assert len(copy_rows) == 6
    assert set(ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_COPY_AUDIT_FIELDS).issubset(
        copy_rows[0]
    )

    print("PASS: CLI writes quarantine main closeout copy audit when requested")


def test_cli_writes_quarantine_main_closeout_draft_overlay_when_requested() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "write_artifact_invalidation_matrix.py"),
                "--output",
                str(root / "matrix.csv"),
                "--manifest",
                str(root / "matrix.json"),
                "--doc",
                str(root / "matrix.md"),
                "--write-closeout-template",
                "--closeout-output",
                str(root / "main_closeout.csv"),
                "--closeout-manifest",
                str(root / "main_closeout.json"),
                "--closeout-doc",
                str(root / "main_closeout.md"),
                "--write-quarantine-non-evidence-transfer-packet",
                "--quarantine-non-evidence-transfer-output",
                str(root / "transfer.csv"),
                "--quarantine-non-evidence-transfer-manifest",
                str(root / "transfer.json"),
                "--quarantine-non-evidence-transfer-doc",
                str(root / "transfer.md"),
                "--write-quarantine-closeout-prefill",
                "--quarantine-closeout-prefill-output",
                str(root / "prefill.csv"),
                "--quarantine-closeout-prefill-manifest",
                str(root / "prefill.json"),
                "--quarantine-closeout-prefill-doc",
                str(root / "prefill.md"),
                "--write-quarantine-main-closeout-draft-overlay",
                "--quarantine-main-closeout-draft-overlay-output",
                str(root / "overlay.csv"),
                "--quarantine-main-closeout-draft-overlay-manifest",
                str(root / "overlay.json"),
                "--quarantine-main-closeout-draft-overlay-doc",
                str(root / "overlay.md"),
                "--quarantine-main-closeout-draft-overlay-prefill-input",
                str(root / "prefill.csv"),
                "--quarantine-main-closeout-draft-overlay-main-closeout-input",
                str(root / "main_closeout.csv"),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        payload = json.loads(result.stdout)
        overlay_manifest = json.loads((root / "overlay.json").read_text(encoding="utf-8"))
        overlay_text = (root / "overlay.md").read_text(encoding="utf-8")
        with (root / "overlay.csv").open("r", encoding="utf-8", newline="") as handle:
            overlay_rows = list(csv.DictReader(handle))

    assert "quarantine_main_closeout_draft_overlay" in payload
    assert "quarantine_closeout_prefill" in payload
    assert "closeout_template" in payload
    assert overlay_manifest["draft_overlay_only"] is True
    assert overlay_manifest["row_count"] == 51
    assert overlay_manifest["overlayed_row_count"] == 6
    assert overlay_manifest["closed_candidate_count"] == 0
    assert overlay_manifest["phase9_promotion_ready"] is False
    assert overlay_manifest["must_not_be_used_as_closeout_manifest"] is True
    assert overlay_manifest["must_not_replace_main_closeout_record"] is True
    assert "not Phase 9 readiness" in overlay_text
    assert len(overlay_rows) == 51
    assert set(ARTIFACT_INVALIDATION_CLOSEOUT_FIELDS).issubset(overlay_rows[0])

    print("PASS: CLI writes quarantine main closeout draft overlay when requested")


def test_cli_writes_quarantine_reference_triage_when_requested() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "write_artifact_invalidation_matrix.py"),
                "--output",
                str(root / "matrix.csv"),
                "--manifest",
                str(root / "matrix.json"),
                "--doc",
                str(root / "matrix.md"),
                "--write-quarantine-non-evidence-transfer-packet",
                "--quarantine-non-evidence-transfer-output",
                str(root / "transfer.csv"),
                "--quarantine-non-evidence-transfer-manifest",
                str(root / "transfer.json"),
                "--quarantine-non-evidence-transfer-doc",
                str(root / "transfer.md"),
                "--write-quarantine-reference-triage",
                "--quarantine-reference-triage-output",
                str(root / "triage.csv"),
                "--quarantine-reference-triage-manifest",
                str(root / "triage.json"),
                "--quarantine-reference-triage-doc",
                str(root / "triage.md"),
                "--quarantine-reference-triage-source-transfer-manifest",
                str(root / "transfer.json"),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        payload = json.loads(result.stdout)
        triage_manifest = json.loads((root / "triage.json").read_text(encoding="utf-8"))
        triage_text = (root / "triage.md").read_text(encoding="utf-8")
        with (root / "triage.csv").open("r", encoding="utf-8", newline="") as handle:
            triage_rows = list(csv.DictReader(handle))
        transfer_sha256 = hashlib.sha256((root / "transfer.json").read_bytes()).hexdigest()

    assert "quarantine_reference_triage" in payload
    assert "quarantine_non_evidence_transfer_packet" in payload
    assert triage_manifest["reference_triage_only"] is True
    assert triage_manifest["source_transfer_packet_manifest_status"] == "loaded"
    assert triage_manifest["source_transfer_packet_manifest_sha256"] == transfer_sha256
    assert triage_manifest["phase9_promotion_ready"] is False
    assert triage_manifest["must_not_be_used_as_closeout_manifest"] is True
    assert "not the main closeout record" in triage_text
    assert triage_rows
    assert set(ARTIFACT_INVALIDATION_QUARANTINE_REFERENCE_TRIAGE_FIELDS).issubset(
        triage_rows[0]
    )

    print("PASS: CLI writes quarantine reference triage when requested")


def test_cli_writes_quarantine_claim_reference_remediation_when_requested() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "write_artifact_invalidation_matrix.py"),
                "--output",
                str(root / "matrix.csv"),
                "--manifest",
                str(root / "matrix.json"),
                "--doc",
                str(root / "matrix.md"),
                "--write-quarantine-scope-audit",
                "--quarantine-scope-output",
                str(root / "scope.csv"),
                "--quarantine-scope-manifest",
                str(root / "scope.json"),
                "--quarantine-scope-doc",
                str(root / "scope.md"),
                "--write-quarantine-reference-triage",
                "--quarantine-reference-triage-output",
                str(root / "triage.csv"),
                "--quarantine-reference-triage-manifest",
                str(root / "triage.json"),
                "--quarantine-reference-triage-doc",
                str(root / "triage.md"),
                "--write-quarantine-claim-reference-remediation-packet",
                "--quarantine-claim-reference-remediation-output",
                str(root / "remediation.csv"),
                "--quarantine-claim-reference-remediation-manifest",
                str(root / "remediation.json"),
                "--quarantine-claim-reference-remediation-doc",
                str(root / "remediation.md"),
                "--quarantine-claim-reference-remediation-source-triage-manifest",
                str(root / "triage.json"),
                "--quarantine-claim-reference-remediation-source-scope-manifest",
                str(root / "scope.json"),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        payload = json.loads(result.stdout)
        remediation_manifest = json.loads(
            (root / "remediation.json").read_text(encoding="utf-8")
        )
        remediation_text = (root / "remediation.md").read_text(encoding="utf-8")
        with (root / "remediation.csv").open("r", encoding="utf-8", newline="") as handle:
            remediation_rows = list(csv.DictReader(handle))
        triage_sha256 = hashlib.sha256((root / "triage.json").read_bytes()).hexdigest()
        scope_sha256 = hashlib.sha256((root / "scope.json").read_bytes()).hexdigest()

    assert "quarantine_claim_reference_remediation_packet" in payload
    assert "quarantine_reference_triage" in payload
    assert "quarantine_scope_audit" in payload
    assert remediation_manifest["claim_reference_remediation_only"] is True
    assert remediation_manifest["source_reference_triage_manifest_status"] == "loaded"
    assert remediation_manifest["source_reference_triage_manifest_sha256"] == triage_sha256
    assert remediation_manifest["source_scope_audit_manifest_status"] == "loaded"
    assert remediation_manifest["source_scope_audit_manifest_sha256"] == scope_sha256
    assert remediation_manifest["phase9_promotion_ready"] is False
    assert remediation_manifest["must_not_be_used_as_closeout_manifest"] is True
    assert "line-level edit tasks" in remediation_text
    assert remediation_manifest["row_count"] == len(remediation_rows)
    if remediation_rows:
        assert set(
            ARTIFACT_INVALIDATION_QUARANTINE_CLAIM_REFERENCE_REMEDIATION_FIELDS
        ).issubset(remediation_rows[0])
    else:
        assert remediation_manifest["review_priority_scope"] == "review_first"
        assert remediation_manifest["unique_reference_path_count"] == 0

    print("PASS: CLI writes quarantine claim-reference remediation when requested")


def test_phase9_preflight_requires_closeout_when_matrix_otherwise_ready() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        manifest = root / "ready_matrix.json"
        _write_matrix_manifest(
            manifest,
            row_count=1,
            blocking_row_count=0,
            phase9_promotion_ready=True,
            upstream_ok=True,
            phase9_ok=True,
        )

        blocks, blockers, _summary = artifact_invalidation_blocks_phase9(
            manifest,
            root / "missing_closeout.json",
        )
        assert blocks is True
        assert any("closeout manifest is missing" in blocker for blocker in blockers)

        closeout_manifest = root / "pending_closeout.json"
        write_artifact_invalidation_closeout_template(
            matrix_rows=build_artifact_invalidation_rows()[:1],
            output_path=root / "pending_closeout.csv",
            manifest_path=closeout_manifest,
            doc_path=root / "pending_closeout.md",
        )
        blocks, blockers, _summary = artifact_invalidation_blocks_phase9(
            manifest,
            closeout_manifest,
        )
        assert blocks is True
        assert any("pending or invalid rows" in blocker for blocker in blockers)

    print("PASS: Phase 9 preflight requires closeout when matrix is otherwise ready")


def test_valid_closeout_can_clear_invalidation_only() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        manifest = root / "ready_matrix.json"
        closeout_csv = root / "closed_closeout.csv"
        closeout_manifest = root / "closed_closeout.json"
        _write_matrix_manifest(
            manifest,
            row_count=1,
            blocking_row_count=0,
            phase9_promotion_ready=True,
            upstream_ok=True,
            phase9_ok=True,
        )
        closeout_row = _closed_closeout_row()
        closeout_row["invalidation_row_id"] = "region_boundary->statistics"
        closeout_row["stale_downstream_group"] = "statistics"
        _write_reviewer_evidence(root, closeout_row)
        _write_closeout_csv(closeout_csv, [closeout_row])
        closeout_summary = summarize_artifact_invalidation_closeout_rows([closeout_row])
        closeout_payload = {
            **closeout_summary,
            "outputs": {
                "csv": closeout_csv.as_posix(),
                "manifest": closeout_manifest.as_posix(),
                "doc": (root / "closed_closeout.md").as_posix(),
            },
            "phase9_promotion_ready": False,
            "can_mark_complete": False,
            "publication_ready": False,
            "final_study_ready": False,
            "formal_acceptance_evidence": False,
            "remaining_blockers": [],
        }
        closeout_manifest.write_text(
            json.dumps(closeout_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        blocks, blockers, summary = artifact_invalidation_blocks_phase9(
            manifest,
            closeout_manifest,
        )
        assert blocks is False
        assert blockers == []
        assert summary["closeout_snapshot"]["publication_ready"] is False
        assert summary["closeout_snapshot"]["final_study_ready"] is False
        assert summary["closeout_snapshot"]["formal_acceptance_evidence"] is False
        assert summary["closeout_snapshot"]["closeout_csv_verification_status"] == "verified"
        assert summary["closeout_snapshot"]["closeout_csv_summary_matches_manifest"] is True

    print("PASS: valid closeout can clear invalidation only")


def test_support_manifest_cannot_clear_when_csv_is_closed() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        manifest = root / "ready_matrix.json"
        closeout_csv = root / "closed_closeout.csv"
        support_manifest = root / "copy_audit_support.json"
        _write_matrix_manifest(
            manifest,
            row_count=1,
            blocking_row_count=0,
            phase9_promotion_ready=True,
            upstream_ok=True,
            phase9_ok=True,
        )
        closeout_row = _closed_closeout_row()
        closeout_row["invalidation_row_id"] = "region_boundary->statistics"
        closeout_row["stale_downstream_group"] = "statistics"
        _write_reviewer_evidence(root, closeout_row)
        _write_closeout_csv(closeout_csv, [closeout_row])
        closeout_summary = summarize_artifact_invalidation_closeout_rows([closeout_row])
        support_payload = {
            **closeout_summary,
            "copy_audit_only": True,
            "outputs": {
                "csv": closeout_csv.as_posix(),
                "manifest": support_manifest.as_posix(),
                "doc": (root / "copy_audit_support.md").as_posix(),
            },
            "phase9_promotion_ready": False,
            "can_mark_complete": False,
            "publication_ready": False,
            "final_study_ready": False,
            "formal_acceptance_evidence": False,
            "remaining_blockers": [],
        }
        support_manifest.write_text(
            json.dumps(support_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        blocks, blockers, summary = artifact_invalidation_blocks_phase9(
            manifest,
            support_manifest,
        )

    assert blocks is True
    assert any("support manifest cannot be used" in blocker for blocker in blockers)
    assert summary["closeout_snapshot"]["closeout_csv_verification_status"] == "verified"
    assert summary["closeout_snapshot"]["must_not_be_used_as_closeout_manifest"] is True
    assert any(
        "support manifest cannot be used" in blocker
        for blocker in summary["closeout_snapshot"]["remaining_blockers"]
    )

    print("PASS: support manifest cannot clear invalidation even with closed CSV")


def test_phase9_preflight_recomputes_closeout_csv_instead_of_trusting_manifest() -> None:
    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        manifest = root / "ready_matrix.json"
        closeout_csv = root / "pending_closeout.csv"
        closeout_manifest = root / "spoofed_closeout.json"
        _write_matrix_manifest(
            manifest,
            row_count=1,
            blocking_row_count=0,
            phase9_promotion_ready=True,
            upstream_ok=True,
            phase9_ok=True,
        )
        pending_row = build_artifact_invalidation_closeout_template_rows(
            build_artifact_invalidation_rows()[:1]
        )[0]
        _write_closeout_csv(closeout_csv, [pending_row])
        spoofed_payload = {
            "row_count": 1,
            "closed_row_count": 1,
            "pending_or_invalid_row_count": 0,
            "outputs": {
                "csv": closeout_csv.as_posix(),
                "manifest": closeout_manifest.as_posix(),
                "doc": (root / "spoofed_closeout.md").as_posix(),
            },
            "phase9_promotion_ready": False,
            "can_mark_complete": False,
            "publication_ready": False,
            "final_study_ready": False,
            "formal_acceptance_evidence": False,
            "remaining_blockers": [],
        }
        closeout_manifest.write_text(
            json.dumps(spoofed_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        blocks, blockers, summary = artifact_invalidation_blocks_phase9(
            manifest,
            closeout_manifest,
        )

    assert blocks is True
    assert summary["closeout_snapshot"]["pending_or_invalid_row_count"] == 1
    assert summary["closeout_snapshot"]["closeout_csv_verification_status"] == "verified"
    assert summary["closeout_snapshot"]["closeout_csv_summary_matches_manifest"] is False
    assert any("summary does not match" in blocker for blocker in blockers)
    assert any("pending or invalid rows" in blocker for blocker in blockers)

    print("PASS: Phase 9 preflight recomputes closeout CSV instead of trusting manifest")


def _write_matrix_manifest(
    path: Path,
    *,
    row_count: int,
    blocking_row_count: int,
    phase9_promotion_ready: bool,
    upstream_ok: bool,
    phase9_ok: bool,
) -> None:
    payload = {
        "row_count": row_count,
        "blocking_row_count": blocking_row_count,
        "required_upstream_groups_covered": upstream_ok,
        "required_phase9_downstream_groups_covered": phase9_ok,
        "phase9_promotion_ready": phase9_promotion_ready,
        "can_mark_complete": False,
        "remaining_blockers": [],
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_quarantine_scope_fixture(root: Path) -> None:
    (root / "results" / "realworld_pilot" / "tables").mkdir(parents=True)
    (root / "review_packages").mkdir(parents=True)
    (root / "docs").mkdir(parents=True)

    (root / "results" / "realworld_pilot" / "pilot_full_results.csv").write_text(
        "policy,completion_rate\nbus,0.8\n",
        encoding="utf-8",
    )
    (root / "results" / "realworld_pilot" / "pilot_full_manifest.json").write_text(
        json.dumps({"run": "pilot_full"}) + "\n",
        encoding="utf-8",
    )
    (
        root
        / "results"
        / "realworld_pilot"
        / "tables"
        / "pilot_full_metric_ci.csv"
    ).write_text("metric,mean\ncompletion_rate,0.8\n", encoding="utf-8")
    (root / "review_packages" / "expert_review_handoff_20260510.md").write_text(
        "Review package handoff references pilot_full outputs.\n",
        encoding="utf-8",
    )
    with zipfile.ZipFile(root / "review_packages" / "expert_review_package.zip", "w") as archive:
        archive.writestr("manifest.json", "{}\n")
        archive.writestr("docs/review.md", "expert_review_package.zip\n")
    (root / "docs" / "scope_reference.md").write_text(
        "The current claim text mentions full_outputs and accepted validation "
        "plus expert_review_package.zip.\n",
        encoding="utf-8",
    )
    (root / "plan.md").write_text(
        "pilot_multi_corridor_full remains a full experiment reference.\n",
        encoding="utf-8",
    )


def _write_closeout_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ARTIFACT_INVALIDATION_CLOSEOUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _artifact_json_for_path(path: Path) -> str:
    try:
        relative = path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        relative = path.as_posix()
    digest = path.read_bytes()
    import hashlib

    return json.dumps(
        [
            {
                "path": relative,
                "sha256": hashlib.sha256(digest).hexdigest(),
                "role": "source_manifest",
            }
        ]
    )


def _write_compact_manifest(
    path: Path,
    *,
    engineering_only: bool,
    scoped_regeneration: bool = False,
) -> None:
    preflight_status = (
        "scoped_closeout_regeneration"
        if scoped_regeneration
        else "engineering_only_bypass"
        if engineering_only
        else "passed"
    )
    payload = {
        "run_profile": "staged_pilot",
        "run_stage": "staged",
        "engineering_only": engineering_only,
        "engineering_only_bypass": engineering_only,
        "closeout_regeneration_scope": (
            "compact_outputs" if scoped_regeneration else ""
        ),
        "closeout_regeneration_scope_status": (
            "passed" if scoped_regeneration else "not_requested"
        ),
        "scope_invalidation_blocks": False,
        "artifact_invalidation_blocks_phase9": engineering_only or scoped_regeneration,
        "rail_source_decisions_pending": engineering_only or scoped_regeneration,
        "publication_ready": False,
        "final_study_ready": False,
        "formal_acceptance_evidence": False,
        "result_scope": "fixture compact closeout source",
        "clean_checkout_status": "clean_checkout_ready",
        "phase8_preflight": {
            "status": preflight_status,
            "engineering_only_bypass": engineering_only,
            "closeout_regeneration_scope": (
                "compact_outputs" if scoped_regeneration else ""
            ),
            "closeout_regeneration_scope_status": (
                "passed" if scoped_regeneration else "not_requested"
            ),
            "scope_invalidation_blocks": False,
            "artifact_invalidation_blocks_phase9": engineering_only or scoped_regeneration,
            "rail_source_decisions_pending": engineering_only or scoped_regeneration,
        },
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_reviewer_evidence(
    root: Path,
    row: dict[str, str],
    *,
    gate_shaped: bool = False,
    support_only: bool = False,
) -> None:
    evidence_ref = root / "reviewer_source_manifest.json"
    evidence_ref.write_text(
        json.dumps({"fixture": "reviewer source"}, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    support_ref = root / "artifact_invalidation_closeout_readiness_audit.csv"
    support_ref.write_text("support_only\ntrue\n", encoding="utf-8")

    if gate_shaped:
        payload = {
            "schema_version": 1,
            "record_type": "sub_agent_gate_review",
            "scope": "artifact_invalidation_closeout_only",
            "gate_id": "phase9",
            "status": "accepted",
            "invalidation_row_id": row["invalidation_row_id"],
            "reviewer_id": row["reviewer_id"],
            "reviewed_at_utc": row["reviewed_at_utc"],
            "decision": "signed_off_for_invalidation_closeout_only",
            "reviewed_paths": [row["invalidation_row_id"]],
            "evidence_paths": [evidence_ref.as_posix()],
            "publication_ready": False,
            "final_study_ready": False,
            "formal_acceptance_evidence": False,
            "can_mark_complete": True,
        }
    else:
        evidence_paths = [support_ref.as_posix()] if support_only else [evidence_ref.as_posix()]
        payload = {
            "schema_version": 1,
            "record_type": "artifact_invalidation_closeout_reviewer_evidence",
            "scope": "artifact_invalidation_closeout_only",
            "invalidation_row_id": row["invalidation_row_id"],
            "reviewer_id": row["reviewer_id"],
            "reviewed_at_utc": row["reviewed_at_utc"],
            "decision": "signed_off_for_invalidation_closeout_only",
            "reviewed_paths": [row["invalidation_row_id"]],
            "evidence_paths": evidence_paths,
            "publication_ready": False,
            "final_study_ready": False,
            "formal_acceptance_evidence": False,
        }

    path = root / f"{row['invalidation_row_id'].replace('->', '__')}_reviewer.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    row["reviewer_evidence_path"] = path.as_posix()
    row["reviewer_evidence_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()


def _closed_closeout_row() -> dict[str, str]:
    sha = "a" * 64
    artifact = json.dumps([{"path": "results/example.csv", "sha256": sha, "role": "stale_downstream"}])
    return {
        "closeout_schema_version": "1",
        "invalidation_row_id": "region_boundary->compact_outputs",
        "upstream_change_group": "region_boundary",
        "stale_downstream_group": "compact_outputs",
        "required_disposition": "regenerate",
        "actual_disposition": "regenerated",
        "closeout_status": "closed_invalidation_only",
        "affected_artifacts_json": artifact,
        "upstream_artifacts_json": artifact,
        "downstream_before_artifacts_json": artifact,
        "downstream_after_artifacts_json": artifact,
        "exclusion_scope": "",
        "rerun_command": ".\\.venv\\Scripts\\python scripts\\run_pilot_experiments.py --staged",
        "rerun_exit_code": "0",
        "rerun_result": "pass",
        "audit_command": ".\\.venv\\Scripts\\python scripts\\audit_tracked_artifacts.py",
        "audit_exit_code": "0",
        "audit_result": "pass",
        "targeted_test_command": ".\\.venv\\Scripts\\python tests\\test_realworld_pilot_experiments.py",
        "targeted_test_exit_code": "0",
        "targeted_test_result": "pass",
        "reviewer_signoff_status": "signed_off_for_invalidation_closeout_only",
        "reviewer_id": "fixture-reviewer",
        "reviewed_at_utc": "2026-06-03T00:00:00+00:00",
        "reviewer_evidence_path": "",
        "reviewer_evidence_sha256": "",
        "claim_boundary_effect": "claim_eligible_after_reaudit",
        "claim_boundary_review_result": "pass",
        "phase9_promotion_effect": "review_only_after_reaudit",
        "can_clear_invalidation_gate": "true",
        "publication_ready": "false",
        "final_study_ready": "false",
        "formal_acceptance_evidence": "false",
        "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
        "review_notes": "fixture closeout only",
    }


if __name__ == "__main__":
    test_invalidation_schema_does_not_duplicate_tracked_artifact_audit()
    test_matrix_covers_plan_minimum_upstream_and_phase9_groups()
    test_required_dispositions_match_phase9_action_set()
    test_result_csv_invalidation_marks_downstream_outputs_stale()
    test_summary_blocks_phase9_until_reaudit()
    test_write_artifact_invalidation_outputs_are_non_acceptance()
    test_phase9_preflight_blocks_missing_or_unresolved_matrix()
    test_phase9_preflight_does_not_trust_ready_boolean_with_blockers()
    test_closeout_template_is_pending_and_non_acceptance()
    test_write_closeout_template_outputs_are_non_acceptance()
    test_closeout_action_queue_orders_dependency_batches_without_acceptance()
    test_write_closeout_action_queue_outputs_are_non_acceptance()
    test_action_batch_inspection_merges_queue_and_readiness_without_closing()
    test_action_batch_inspection_blocks_compact_regeneration_without_source_manifest()
    test_write_action_batch_inspection_outputs_are_non_acceptance()
    test_write_action_batch_inspection_skips_unchanged_csv_rewrite()
    test_closeout_readiness_audit_covers_rows_without_closing()
    test_write_closeout_readiness_audit_outputs_are_non_acceptance()
    test_compact_engineering_only_manifest_cannot_close_invalidation()
    test_compact_mixed_manifest_row_fails_if_any_source_manifest_is_blocked()
    test_compact_eligible_manifest_can_close_invalidation_only()
    test_compact_scoped_regeneration_manifest_can_close_invalidation_only()
    test_missing_reviewer_evidence_cannot_close_current_invalidation()
    test_user_reported_human_reviewer_marker_cannot_close_current_invalidation()
    test_closeout_readiness_summary_keeps_support_blocker_when_rows_ready()
    test_gate_shaped_reviewer_evidence_cannot_close_invalidation()
    test_support_only_reviewer_evidence_paths_cannot_close_invalidation()
    test_apply_reviewer_evidence_links_valid_record_only()
    test_apply_reviewer_evidence_rejects_missing_payload_evidence_path()
    test_cli_applies_reviewer_evidence_when_requested()
    test_cli_refuses_template_regeneration_during_reviewer_evidence_apply()
    test_compact_closeout_requires_source_manifest_not_only_csv_outputs()
    test_quarantine_closeout_template_filters_first_batch_without_closing()
    test_write_quarantine_closeout_template_does_not_mutate_main_closeout()
    test_write_quarantine_closeout_template_outputs_are_non_acceptance()
    test_write_quarantine_closeout_template_skips_unchanged_csv_rewrite()
    test_quarantine_scope_audit_uses_finding_rows_not_closeout_fields()
    test_write_quarantine_scope_audit_outputs_are_non_acceptance()
    test_quarantine_non_evidence_index_dedupes_candidate_paths()
    test_write_quarantine_non_evidence_index_outputs_are_non_acceptance()
    test_quarantine_non_evidence_index_cannot_be_used_as_main_closeout_manifest()
    test_quarantine_transfer_packet_groups_six_row_handoff_without_closing()
    test_quarantine_transfer_packet_detects_changed_candidate_artifacts()
    test_write_quarantine_transfer_packet_outputs_are_non_acceptance()
    test_quarantine_transfer_packet_cannot_be_used_as_main_closeout_manifest()
    test_quarantine_closeout_prefill_maps_transfer_packet_without_closing()
    test_write_quarantine_closeout_prefill_outputs_are_non_acceptance()
    test_quarantine_closeout_prefill_cannot_be_used_as_main_closeout_manifest()
    test_quarantine_closeout_prefill_gap_audit_lists_remaining_work()
    test_quarantine_closeout_prefill_gap_audit_uses_closeout_schema_status_values()
    test_write_quarantine_closeout_prefill_gap_audit_outputs_are_non_acceptance()
    test_quarantine_main_closeout_copy_audit_detects_missing_main_copy()
    test_write_quarantine_main_closeout_copy_audit_outputs_are_non_acceptance()
    test_quarantine_main_closeout_draft_overlay_prefills_without_closing()
    test_write_quarantine_main_closeout_draft_overlay_outputs_are_non_acceptance()
    test_quarantine_reference_triage_splits_reference_priorities()
    test_write_quarantine_reference_triage_outputs_are_non_acceptance()
    test_claim_reference_remediation_filters_review_first_line_hits()
    test_write_claim_reference_remediation_outputs_are_non_acceptance()
    test_quarantine_manifest_cannot_be_used_as_main_closeout_manifest()
    test_quarantine_scope_audit_cannot_be_used_as_main_closeout_manifest()
    test_cli_writes_quarantine_template_without_main_closeout_when_requested()
    test_cli_writes_closeout_readiness_audit_when_requested()
    test_cli_writes_action_batch_inspection_when_requested()
    test_cli_closeout_readiness_audit_reads_filled_closeout_input()
    test_cli_writes_quarantine_scope_audit_when_requested()
    test_cli_writes_quarantine_non_evidence_index_when_requested()
    test_cli_writes_quarantine_non_evidence_transfer_packet_when_requested()
    test_cli_writes_quarantine_closeout_prefill_when_requested()
    test_cli_writes_quarantine_closeout_prefill_gap_audit_when_requested()
    test_cli_writes_quarantine_main_closeout_copy_audit_when_requested()
    test_cli_writes_quarantine_main_closeout_draft_overlay_when_requested()
    test_cli_writes_quarantine_reference_triage_when_requested()
    test_cli_writes_quarantine_claim_reference_remediation_when_requested()
    test_phase9_preflight_requires_closeout_when_matrix_otherwise_ready()
    test_valid_closeout_can_clear_invalidation_only()
    test_support_manifest_cannot_clear_when_csv_is_closed()
    test_phase9_preflight_recomputes_closeout_csv_instead_of_trusting_manifest()
    print("\n=== REALWORLD ARTIFACT INVALIDATION MATRIX TESTS PASSED ===")
