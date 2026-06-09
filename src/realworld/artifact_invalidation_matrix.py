"""Artifact invalidation matrix for Phase 9 preflight review.

This module maps upstream evidence/configuration groups to downstream artifact
groups that become stale. It intentionally does not inspect ``git status``;
clean-checkout and dirty-worktree risk is handled by ``tracked_artifact_audit``.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
import zipfile

from src.realworld.manifest_timestamp import (
    preserve_generated_at_when_unchanged,
    write_json_manifest_if_changed,
    write_text_if_changed,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT_INVALIDATION_CSV = (
    PROJECT_ROOT / "data" / "validation" / "artifact_invalidation_matrix.csv"
)
DEFAULT_ARTIFACT_INVALIDATION_MANIFEST = (
    PROJECT_ROOT / "data" / "validation" / "artifact_invalidation_matrix_manifest.json"
)
DEFAULT_ARTIFACT_INVALIDATION_DOC = (
    PROJECT_ROOT / "docs" / "artifact_invalidation_matrix.md"
)
DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_TEMPLATE = (
    PROJECT_ROOT / "data" / "validation" / "artifact_invalidation_closeout_template.csv"
)
DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_MANIFEST = (
    PROJECT_ROOT / "data" / "validation" / "artifact_invalidation_closeout_manifest.json"
)
DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_DOC = (
    PROJECT_ROOT / "docs" / "artifact_invalidation_closeout_template.md"
)
DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_QUEUE = (
    PROJECT_ROOT / "data" / "validation" / "artifact_invalidation_closeout_action_queue.csv"
)
DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_MANIFEST = (
    PROJECT_ROOT / "data" / "validation" / "artifact_invalidation_closeout_action_queue_manifest.json"
)
DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_DOC = (
    PROJECT_ROOT / "docs" / "artifact_invalidation_closeout_action_queue.md"
)
DEFAULT_ARTIFACT_INVALIDATION_ACTION_BATCH_INSPECTION = (
    PROJECT_ROOT / "data" / "validation" / "artifact_invalidation_action_batch_inspection.csv"
)
DEFAULT_ARTIFACT_INVALIDATION_ACTION_BATCH_INSPECTION_MANIFEST = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "artifact_invalidation_action_batch_inspection_manifest.json"
)
DEFAULT_ARTIFACT_INVALIDATION_ACTION_BATCH_INSPECTION_DOC = (
    PROJECT_ROOT / "docs" / "artifact_invalidation_action_batch_inspection.md"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_TEMPLATE = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "artifact_invalidation_quarantine_closeout_template.csv"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_MANIFEST = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "artifact_invalidation_quarantine_closeout_manifest.json"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_DOC = (
    PROJECT_ROOT / "docs" / "artifact_invalidation_quarantine_closeout_template.md"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_AUDIT = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "artifact_invalidation_quarantine_scope_audit.csv"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_AUDIT_MANIFEST = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "artifact_invalidation_quarantine_scope_audit_manifest.json"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_AUDIT_DOC = (
    PROJECT_ROOT / "docs" / "artifact_invalidation_quarantine_scope_audit.md"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_NON_EVIDENCE_INDEX = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "artifact_invalidation_quarantine_non_evidence_index.csv"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_NON_EVIDENCE_INDEX_MANIFEST = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "artifact_invalidation_quarantine_non_evidence_index_manifest.json"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_NON_EVIDENCE_INDEX_DOC = (
    PROJECT_ROOT / "docs" / "artifact_invalidation_quarantine_non_evidence_index.md"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "artifact_invalidation_quarantine_non_evidence_transfer_packet.csv"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET_MANIFEST = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "artifact_invalidation_quarantine_non_evidence_transfer_packet_manifest.json"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET_DOC = (
    PROJECT_ROOT
    / "docs"
    / "artifact_invalidation_quarantine_non_evidence_transfer_packet.md"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "artifact_invalidation_quarantine_closeout_prefill.csv"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL_MANIFEST = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "artifact_invalidation_quarantine_closeout_prefill_manifest.json"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL_DOC = (
    PROJECT_ROOT / "docs" / "artifact_invalidation_quarantine_closeout_prefill.md"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL_GAP_AUDIT = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "artifact_invalidation_quarantine_closeout_prefill_gap_audit.csv"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL_GAP_AUDIT_MANIFEST = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "artifact_invalidation_quarantine_closeout_prefill_gap_audit_manifest.json"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL_GAP_AUDIT_DOC = (
    PROJECT_ROOT / "docs" / "artifact_invalidation_quarantine_closeout_prefill_gap_audit.md"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_COPY_AUDIT = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "artifact_invalidation_quarantine_main_closeout_copy_audit.csv"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_COPY_AUDIT_MANIFEST = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "artifact_invalidation_quarantine_main_closeout_copy_audit_manifest.json"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_COPY_AUDIT_DOC = (
    PROJECT_ROOT / "docs" / "artifact_invalidation_quarantine_main_closeout_copy_audit.md"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_DRAFT_OVERLAY = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "artifact_invalidation_quarantine_main_closeout_draft_overlay.csv"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_DRAFT_OVERLAY_MANIFEST = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "artifact_invalidation_quarantine_main_closeout_draft_overlay_manifest.json"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_DRAFT_OVERLAY_DOC = (
    PROJECT_ROOT
    / "docs"
    / "artifact_invalidation_quarantine_main_closeout_draft_overlay.md"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_REFERENCE_TRIAGE = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "artifact_invalidation_quarantine_reference_triage.csv"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_REFERENCE_TRIAGE_MANIFEST = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "artifact_invalidation_quarantine_reference_triage_manifest.json"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_REFERENCE_TRIAGE_DOC = (
    PROJECT_ROOT / "docs" / "artifact_invalidation_quarantine_reference_triage.md"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLAIM_REFERENCE_REMEDIATION = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "artifact_invalidation_quarantine_claim_reference_remediation_packet.csv"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLAIM_REFERENCE_REMEDIATION_MANIFEST = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "artifact_invalidation_quarantine_claim_reference_remediation_packet_manifest.json"
)
DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLAIM_REFERENCE_REMEDIATION_DOC = (
    PROJECT_ROOT
    / "docs"
    / "artifact_invalidation_quarantine_claim_reference_remediation_packet.md"
)
DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_READINESS_AUDIT = (
    PROJECT_ROOT / "data" / "validation" / "artifact_invalidation_closeout_readiness_audit.csv"
)
DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_READINESS_AUDIT_MANIFEST = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "artifact_invalidation_closeout_readiness_audit_manifest.json"
)
DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_READINESS_AUDIT_DOC = (
    PROJECT_ROOT / "docs" / "artifact_invalidation_closeout_readiness_audit.md"
)

ARTIFACT_INVALIDATION_CLAIM_BOUNDARY = (
    "Artifact invalidation matrix for Phase 9 preflight review only; not an "
    "artifact regeneration record, not evidence-quality validation, not "
    "publication readiness, not final-study approval, and not formal acceptance."
)

ARTIFACT_INVALIDATION_FIELDS: tuple[str, ...] = (
    "upstream_change_group",
    "upstream_change_trigger",
    "stale_downstream_group",
    "stale_downstream_description",
    "required_disposition",
    "disposition_status",
    "claim_boundary_effect",
    "audit_or_regeneration_command",
    "phase9_promotion_effect",
    "can_support_phase9_promotion",
    "publication_ready",
    "final_study_ready",
    "formal_acceptance_evidence",
    "claim_boundary",
)

ARTIFACT_INVALIDATION_CLOSEOUT_FIELDS: tuple[str, ...] = (
    "closeout_schema_version",
    "invalidation_row_id",
    "upstream_change_group",
    "stale_downstream_group",
    "required_disposition",
    "actual_disposition",
    "closeout_status",
    "affected_artifacts_json",
    "upstream_artifacts_json",
    "downstream_before_artifacts_json",
    "downstream_after_artifacts_json",
    "exclusion_scope",
    "rerun_command",
    "rerun_exit_code",
    "rerun_result",
    "audit_command",
    "audit_exit_code",
    "audit_result",
    "targeted_test_command",
    "targeted_test_exit_code",
    "targeted_test_result",
    "reviewer_signoff_status",
    "reviewer_id",
    "reviewed_at_utc",
    "reviewer_evidence_path",
    "reviewer_evidence_sha256",
    "claim_boundary_effect",
    "claim_boundary_review_result",
    "phase9_promotion_effect",
    "can_clear_invalidation_gate",
    "publication_ready",
    "final_study_ready",
    "formal_acceptance_evidence",
    "claim_boundary",
    "review_notes",
)

ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_FIELDS: tuple[str, ...] = (
    "action_order",
    "action_batch",
    "dependency_stage",
    "invalidation_row_id",
    "upstream_change_group",
    "stale_downstream_group",
    "required_disposition",
    "recommended_disposition",
    "closeout_dependency",
    "minimum_evidence_required",
    "producer_or_audit_command",
    "targeted_test_command",
    "reviewer_role",
    "blocks_phase9_until_closed",
    "can_close_without_reviewer_signoff",
    "publication_ready",
    "final_study_ready",
    "formal_acceptance_evidence",
    "claim_boundary",
)

ARTIFACT_INVALIDATION_ACTION_BATCH_INSPECTION_FIELDS: tuple[str, ...] = (
    "inspection_schema_version",
    "action_order",
    "action_batch",
    "dependency_stage",
    "invalidation_row_id",
    "upstream_change_group",
    "stale_downstream_group",
    "required_disposition",
    "recommended_disposition",
    "actual_disposition",
    "closeout_status",
    "inspection_classification",
    "can_clear_invalidation_gate",
    "missing_evidence_json",
    "next_closeout_focus",
    "blocking_prerequisite_batch",
    "blocking_prerequisite_status",
    "minimum_evidence_package_json",
    "allowed_next_operation",
    "source_manifest_status",
    "source_manifest_path",
    "compact_closeout_eligibility_status",
    "reviewer_signoff_status",
    "blocks_phase9_until_closed",
    "can_close_without_reviewer_signoff",
    "publication_ready",
    "final_study_ready",
    "formal_acceptance_evidence",
    "claim_boundary",
)

ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_FIELDS: tuple[str, ...] = (
    "invalidation_row_id",
    "action_batch",
    "stale_downstream_group",
    "scope_id",
    "finding_type",
    "searched_path_or_glob",
    "matched_path",
    "matched_detail",
    "status",
    "sha256",
    "suggested_closeout_field",
    "claim_boundary",
)

ARTIFACT_INVALIDATION_QUARANTINE_NON_EVIDENCE_INDEX_FIELDS: tuple[str, ...] = (
    "index_schema_version",
    "action_batch",
    "dependency_stage",
    "stale_downstream_group",
    "candidate_type",
    "matched_path",
    "sha256",
    "invalidation_row_ids_json",
    "source_row_count",
    "scope_ids_json",
    "source_finding_count",
    "source_scope_audit_manifest",
    "source_quarantine_template_manifest",
    "reviewer_handoff_note",
    "review_next_step",
    "claim_boundary",
)

ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET_FIELDS: tuple[str, ...] = (
    "transfer_schema_version",
    "action_batch",
    "dependency_stage",
    "invalidation_row_id",
    "upstream_change_group",
    "stale_downstream_group",
    "required_disposition",
    "recommended_disposition",
    "candidate_artifact_count",
    "candidate_artifacts_json",
    "current_reference_hit_count",
    "reference_hit_paths_json",
    "source_scope_ids_json",
    "source_non_evidence_index_manifest",
    "source_scope_audit_manifest",
    "source_quarantine_template_manifest",
    "transfer_status",
    "required_reviewer_action",
    "claim_boundary",
)

ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL_GAP_FIELDS: tuple[str, ...] = (
    "gap_schema_version",
    "invalidation_row_id",
    "action_batch",
    "dependency_stage",
    "upstream_change_group",
    "stale_downstream_group",
    "required_disposition",
    "main_closeout_template_row_number",
    "actual_disposition",
    "closeout_status",
    "candidate_artifact_count",
    "reference_hit_count",
    "source_transfer_packet_manifest",
    "source_transfer_packet_manifest_sha256",
    "source_transfer_packet_manifest_status",
    "artifact_or_exclusion_gap",
    "rerun_gap",
    "audit_gap",
    "targeted_test_gap",
    "claim_boundary_review_gap",
    "reviewer_signoff_gap",
    "main_closeout_copy_gap",
    "blocking_gap_codes_json",
    "next_reviewer_action",
    "can_clear_invalidation_gate",
    "phase9_promotion_ready",
    "publication_ready",
    "final_study_ready",
    "formal_acceptance_evidence",
    "must_not_be_used_as_closeout_manifest",
    "claim_boundary",
)

ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_COPY_AUDIT_FIELDS: tuple[str, ...] = (
    "copy_audit_schema_version",
    "invalidation_row_id",
    "action_batch",
    "upstream_change_group",
    "stale_downstream_group",
    "required_disposition",
    "main_closeout_row_found",
    "main_closeout_template_row_number",
    "prefill_actual_disposition",
    "main_actual_disposition",
    "prefill_closeout_status",
    "main_closeout_status",
    "prefill_candidate_artifact_count",
    "main_candidate_artifact_count",
    "affected_artifacts_copy_status",
    "exclusion_scope_copy_status",
    "actual_disposition_copy_status",
    "main_closeout_evidence_status",
    "main_closeout_gap_codes_json",
    "copy_audit_status",
    "next_required_action",
    "can_clear_invalidation_gate",
    "phase9_promotion_ready",
    "publication_ready",
    "final_study_ready",
    "formal_acceptance_evidence",
    "must_not_be_used_as_closeout_manifest",
    "claim_boundary",
)

ARTIFACT_INVALIDATION_QUARANTINE_REFERENCE_TRIAGE_FIELDS: tuple[str, ...] = (
    "triage_schema_version",
    "action_batch",
    "dependency_stage",
    "invalidation_row_id",
    "stale_downstream_group",
    "reference_path",
    "reference_classification",
    "review_priority",
    "required_reviewer_action",
    "source_transfer_packet_manifest",
    "source_transfer_packet_manifest_sha256",
    "source_transfer_packet_manifest_status",
    "can_clear_invalidation_gate",
    "phase9_promotion_ready",
    "publication_ready",
    "final_study_ready",
    "formal_acceptance_evidence",
    "must_not_be_used_as_closeout_manifest",
    "claim_boundary",
)

ARTIFACT_INVALIDATION_QUARANTINE_CLAIM_REFERENCE_REMEDIATION_FIELDS: tuple[str, ...] = (
    "remediation_schema_version",
    "action_batch",
    "dependency_stage",
    "invalidation_row_id",
    "stale_downstream_group",
    "reference_path",
    "reference_classification",
    "review_priority",
    "line_scan_status",
    "line_number",
    "matched_pattern",
    "excerpt",
    "source_scope_id",
    "source_scope_matched_detail",
    "triage_required_reviewer_action",
    "suggested_remediation",
    "source_reference_triage_manifest",
    "source_reference_triage_manifest_sha256",
    "source_reference_triage_manifest_status",
    "source_scope_audit_manifest",
    "source_scope_audit_manifest_sha256",
    "source_scope_audit_manifest_status",
    "can_clear_invalidation_gate",
    "phase9_promotion_ready",
    "publication_ready",
    "final_study_ready",
    "formal_acceptance_evidence",
    "must_not_be_used_as_closeout_manifest",
    "claim_boundary",
)

ARTIFACT_INVALIDATION_CLOSEOUT_READINESS_FIELDS: tuple[str, ...] = (
    "readiness_schema_version",
    "invalidation_row_id",
    "action_batch",
    "dependency_stage",
    "upstream_change_group",
    "stale_downstream_group",
    "required_disposition",
    "actual_disposition",
    "closeout_status",
    "artifact_or_exclusion_status",
    "rerun_status",
    "audit_status",
    "targeted_test_status",
    "claim_boundary_review_status",
    "reviewer_signoff_status",
    "reviewer_identity_status",
    "reviewer_evidence_status",
    "reviewer_evidence_path",
    "reviewer_evidence_sha256",
    "source_manifest_status",
    "source_manifest_path",
    "source_manifest_sha256",
    "source_run_profile",
    "source_run_stage",
    "source_engineering_only",
    "source_engineering_only_bypass",
    "source_phase8_preflight_status",
    "source_artifact_invalidation_blocks_phase9",
    "source_rail_source_decisions_pending",
    "source_publication_ready",
    "source_final_study_ready",
    "source_formal_acceptance_evidence",
    "source_result_scope",
    "source_clean_checkout_status",
    "compact_closeout_eligibility_status",
    "missing_evidence_json",
    "can_clear_invalidation_gate",
    "publication_ready",
    "final_study_ready",
    "formal_acceptance_evidence",
    "claim_boundary",
)

UPSTREAM_GROUPS: frozenset[str] = frozenset(
    {
        "region_boundary",
        "road_snapshot_or_evidence",
        "rail_source_or_timing",
        "demand_fleet_behavior_transfer_dispatch",
        "disruption_library_or_exposure",
        "benchmark_cache_or_threshold",
        "result_csv_or_manifest",
        "claim_boundary_or_readiness_logic",
    }
)

REQUIRED_PHASE9_GROUPS: frozenset[str] = frozenset(
    {
        "compact_outputs",
        "statistics",
        "ml_outputs",
        "figures",
        "reports",
        "review_packages",
    }
)

ALLOWED_REQUIRED_DISPOSITIONS: frozenset[str] = frozenset(
    {"regenerate", "explicitly_exclude", "mark_non_evidence"}
)
ALLOWED_DISPOSITION_STATUSES: frozenset[str] = frozenset(
    {
        "stale_pending_disposition",
        "regenerated_pending_audit",
        "excluded_pending_audit",
        "non_evidence_pending_audit",
        "cleared_after_reaudit",
        "blocked_unknown_impact",
    }
)
ALLOWED_CLAIM_BOUNDARY_EFFECTS: frozenset[str] = frozenset(
    {
        "blocks_claim_support",
        "excluded_from_current_claim_scope",
        "non_evidence_only",
        "claim_eligible_after_reaudit",
    }
)

DEFAULT_QUARANTINE_CITATION_SEARCH_ROOTS: tuple[str, ...] = (
    "README.md",
    "plan.md",
    "status.md",
    "agents.md",
    "report_draft.md",
    "paper",
    "docs",
    "review_packages",
)
QUARANTINE_AUDIT_SELF_PATHS: frozenset[str] = frozenset(
    {
        "data/validation/artifact_invalidation_quarantine_scope_audit.csv",
        "data/validation/artifact_invalidation_quarantine_scope_audit_manifest.json",
        "docs/artifact_invalidation_quarantine_scope_audit.md",
        "data/validation/artifact_invalidation_quarantine_non_evidence_index.csv",
        "data/validation/artifact_invalidation_quarantine_non_evidence_index_manifest.json",
        "docs/artifact_invalidation_quarantine_non_evidence_index.md",
        "data/validation/artifact_invalidation_quarantine_non_evidence_transfer_packet.csv",
        "data/validation/artifact_invalidation_quarantine_non_evidence_transfer_packet_manifest.json",
        "docs/artifact_invalidation_quarantine_non_evidence_transfer_packet.md",
        "data/validation/artifact_invalidation_quarantine_closeout_prefill.csv",
        "data/validation/artifact_invalidation_quarantine_closeout_prefill_manifest.json",
        "docs/artifact_invalidation_quarantine_closeout_prefill.md",
        "data/validation/artifact_invalidation_quarantine_closeout_prefill_gap_audit.csv",
        "data/validation/artifact_invalidation_quarantine_closeout_prefill_gap_audit_manifest.json",
        "docs/artifact_invalidation_quarantine_closeout_prefill_gap_audit.md",
        "data/validation/artifact_invalidation_quarantine_main_closeout_copy_audit.csv",
        "data/validation/artifact_invalidation_quarantine_main_closeout_copy_audit_manifest.json",
        "docs/artifact_invalidation_quarantine_main_closeout_copy_audit.md",
        "data/validation/artifact_invalidation_quarantine_main_closeout_draft_overlay.csv",
        "data/validation/artifact_invalidation_quarantine_main_closeout_draft_overlay_manifest.json",
        "docs/artifact_invalidation_quarantine_main_closeout_draft_overlay.md",
        "data/validation/artifact_invalidation_quarantine_reference_triage.csv",
        "data/validation/artifact_invalidation_quarantine_reference_triage_manifest.json",
        "docs/artifact_invalidation_quarantine_reference_triage.md",
        "data/validation/artifact_invalidation_quarantine_claim_reference_remediation_packet.csv",
        "data/validation/artifact_invalidation_quarantine_claim_reference_remediation_packet_manifest.json",
        "docs/artifact_invalidation_quarantine_claim_reference_remediation_packet.md",
    }
)
QUARANTINE_TEXT_SUFFIXES: frozenset[str] = frozenset(
    {".csv", ".json", ".md", ".py", ".txt", ".yaml", ".yml"}
)

BLOCKING_DISPOSITION_STATUSES: frozenset[str] = frozenset(
    {
        "stale_pending_disposition",
        "regenerated_pending_audit",
        "excluded_pending_audit",
        "non_evidence_pending_audit",
        "blocked_unknown_impact",
    }
)

ALLOWED_CLOSEOUT_DISPOSITIONS: frozenset[str] = frozenset(
    {
        "pending",
        "regenerated",
        "explicitly_excluded",
        "marked_non_evidence",
        "blocked_unknown_impact",
    }
)
ALLOWED_CLOSEOUT_STATUSES: frozenset[str] = frozenset(
    {
        "pending",
        "closed_invalidation_only",
        "blocked_unknown_impact",
        "needs_rework",
    }
)
ALLOWED_CLOSEOUT_RESULT_STATUSES: frozenset[str] = frozenset(
    {
        "not_run",
        "pass",
        "fail",
        "not_applicable",
    }
)
ALLOWED_CLOSEOUT_SIGNOFF_STATUSES: frozenset[str] = frozenset(
    {
        "unsigned",
        "signed_off_for_invalidation_closeout_only",
        "rejected",
        "needs_rework",
    }
)
ALLOWED_CLAIM_BOUNDARY_REVIEW_RESULTS: frozenset[str] = frozenset(
    {
        "pending",
        "pass",
        "fail",
        "not_applicable",
    }
)
READY_CLOSEOUT_DISPOSITIONS: frozenset[str] = frozenset(
    {
        "regenerated",
        "explicitly_excluded",
        "marked_non_evidence",
    }
)
ARTIFACT_INVALIDATION_REVIEWER_EVIDENCE_RECORD_TYPE = (
    "artifact_invalidation_closeout_reviewer_evidence"
)
ARTIFACT_INVALIDATION_REVIEWER_EVIDENCE_SCOPE = (
    "artifact_invalidation_closeout_only"
)
ARTIFACT_INVALIDATION_REVIEWER_EVIDENCE_DECISION = (
    "signed_off_for_invalidation_closeout_only"
)
ARTIFACT_INVALIDATION_REVIEWER_EVIDENCE_REQUIRED_FIELDS: tuple[str, ...] = (
    "schema_version",
    "record_type",
    "scope",
    "invalidation_row_id",
    "reviewer_id",
    "reviewed_at_utc",
    "decision",
    "reviewed_paths",
    "evidence_paths",
    "publication_ready",
    "final_study_ready",
    "formal_acceptance_evidence",
)
ARTIFACT_INVALIDATION_REVIEWER_SUPPORT_BASENAMES: frozenset[str] = frozenset(
    {
        "artifact_invalidation_action_batch_inspection.csv",
        "artifact_invalidation_action_batch_inspection_manifest.json",
        "artifact_invalidation_closeout_readiness_audit.csv",
        "artifact_invalidation_closeout_readiness_audit_manifest.json",
        "artifact_invalidation_quarantine_closeout_prefill.csv",
        "artifact_invalidation_quarantine_closeout_prefill_manifest.json",
        "artifact_invalidation_quarantine_closeout_prefill_gap_audit.csv",
        "artifact_invalidation_quarantine_closeout_prefill_gap_audit_manifest.json",
        "artifact_invalidation_quarantine_main_closeout_copy_audit.csv",
        "artifact_invalidation_quarantine_main_closeout_copy_audit_manifest.json",
        "artifact_invalidation_quarantine_main_closeout_draft_overlay.csv",
        "artifact_invalidation_quarantine_main_closeout_draft_overlay_manifest.json",
        "artifact_invalidation_quarantine_closeout_template.csv",
        "artifact_invalidation_quarantine_closeout_manifest.json",
        "artifact_invalidation_quarantine_scope_audit.csv",
        "artifact_invalidation_quarantine_scope_audit_manifest.json",
    }
)


@dataclass(frozen=True)
class InvalidationRowSpec:
    """One upstream group to stale downstream group rule."""

    upstream_change_group: str
    upstream_change_trigger: str
    stale_downstream_group: str
    stale_downstream_description: str
    required_disposition: str
    audit_or_regeneration_command: str


INVALIDATION_ROW_SPECS: tuple[InvalidationRowSpec, ...] = (
    InvalidationRowSpec(
        "region_boundary",
        "Region registry, polygon, source boundary, zone, connector, or sensitive-location abstraction changes",
        "road_snapshots",
        "Road GraphML/PBF/cache snapshots derived from the old region definition",
        "regenerate",
        "rerun the road snapshot and connector-audit producers",
    ),
    InvalidationRowSpec(
        "region_boundary",
        "Region registry, polygon, source boundary, zone, connector, or sensitive-location abstraction changes",
        "connector_audits",
        "Origin/access/egress/destination connector audits",
        "regenerate",
        "rerun connector distance and travel-time reasonableness audits",
    ),
    InvalidationRowSpec(
        "region_boundary",
        "Region registry, polygon, source boundary, zone, connector, or sensitive-location abstraction changes",
        "benchmarks",
        "External route or multimodal benchmarks tied to old zone coordinates",
        "regenerate",
        "rerun benchmark review cache and threshold packets",
    ),
    InvalidationRowSpec(
        "region_boundary",
        "Region registry, polygon, source boundary, zone, connector, or sensitive-location abstraction changes",
        "compact_outputs",
        "Compact outputs whose routes or connectors depend on the old region",
        "regenerate",
        "rerun compact output producer and audit package",
    ),
    InvalidationRowSpec(
        "region_boundary",
        "Region registry, polygon, source boundary, zone, connector, or sensitive-location abstraction changes",
        "full_outputs",
        "Full-run outputs whose routes or connectors depend on the old region",
        "mark_non_evidence",
        "exclude old full outputs from Phase 9 and rerun after compact gate",
    ),
    InvalidationRowSpec(
        "region_boundary",
        "Region registry, polygon, source boundary, zone, connector, or sensitive-location abstraction changes",
        "figures",
        "Maps and figures that display old region geometry or labels",
        "regenerate",
        "rerun figure scripts after source artifact audit",
    ),
    InvalidationRowSpec(
        "region_boundary",
        "Region registry, polygon, source boundary, zone, connector, or sensitive-location abstraction changes",
        "reports",
        "Report or manuscript text that describes old region assumptions",
        "regenerate",
        "rerun claim-alignment and manuscript/report review packets",
    ),
    InvalidationRowSpec(
        "road_snapshot_or_evidence",
        "OSM/GraphML/PBF snapshot, road edge table, road-class override, or road-attribute evidence changes",
        "route_exposure",
        "Route-level road evidence exposure records",
        "regenerate",
        "rerun route-road evidence exposure writer",
    ),
    InvalidationRowSpec(
        "road_snapshot_or_evidence",
        "OSM/GraphML/PBF snapshot, road edge table, road-class override, or road-attribute evidence changes",
        "graph_scale_diagnostics",
        "Full-vs-reduced graph diagnostics and alternate-route tables",
        "regenerate",
        "rerun graph-scale diagnostics and review packet",
    ),
    InvalidationRowSpec(
        "road_snapshot_or_evidence",
        "OSM/GraphML/PBF snapshot, road edge table, road-class override, or road-attribute evidence changes",
        "benchmarks",
        "Road route benchmark comparisons tied to old edge geometry",
        "regenerate",
        "rerun external route benchmark cache and threshold comparison",
    ),
    InvalidationRowSpec(
        "road_snapshot_or_evidence",
        "OSM/GraphML/PBF snapshot, road edge table, road-class override, or road-attribute evidence changes",
        "compact_outputs",
        "Compact outputs produced from old road attributes",
        "regenerate",
        "rerun compact output producer and audit package",
    ),
    InvalidationRowSpec(
        "road_snapshot_or_evidence",
        "OSM/GraphML/PBF snapshot, road edge table, road-class override, or road-attribute evidence changes",
        "full_outputs",
        "Full outputs produced from old road attributes",
        "mark_non_evidence",
        "exclude old full outputs until rerun after compact promotion",
    ),
    InvalidationRowSpec(
        "road_snapshot_or_evidence",
        "OSM/GraphML/PBF snapshot, road edge table, road-class override, or road-attribute evidence changes",
        "figures",
        "Road maps, route charts, and road-exposure figures",
        "regenerate",
        "rerun figure scripts from audited road outputs",
    ),
    InvalidationRowSpec(
        "road_snapshot_or_evidence",
        "OSM/GraphML/PBF snapshot, road edge table, road-class override, or road-attribute evidence changes",
        "reports",
        "Report text citing old road evidence or route metrics",
        "regenerate",
        "rerun claim-alignment and manuscript/report review packets",
    ),
    InvalidationRowSpec(
        "rail_source_or_timing",
        "Rail GTFS, timetable, shortest-path, source-decision, capacity, or availability evidence changes",
        "multimodal_benchmarks",
        "Rail/transit benchmark comparisons tied to old rail evidence",
        "regenerate",
        "rerun multimodal benchmark or timetable comparison packets",
    ),
    InvalidationRowSpec(
        "rail_source_or_timing",
        "Rail GTFS, timetable, shortest-path, source-decision, capacity, or availability evidence changes",
        "rail_stress_profiles",
        "Rail stress-profile packets and bounded-treatment audits",
        "regenerate",
        "rerun rail stress-profile and bounded-treatment audits",
    ),
    InvalidationRowSpec(
        "rail_source_or_timing",
        "Rail GTFS, timetable, shortest-path, source-decision, capacity, or availability evidence changes",
        "compact_outputs",
        "Compact multimodal outputs tied to old rail assumptions",
        "regenerate",
        "rerun compact output producer and audit package",
    ),
    InvalidationRowSpec(
        "rail_source_or_timing",
        "Rail GTFS, timetable, shortest-path, source-decision, capacity, or availability evidence changes",
        "full_outputs",
        "Full multimodal outputs tied to old rail assumptions",
        "mark_non_evidence",
        "exclude old full outputs until rerun after compact promotion",
    ),
    InvalidationRowSpec(
        "rail_source_or_timing",
        "Rail GTFS, timetable, shortest-path, source-decision, capacity, or availability evidence changes",
        "figures",
        "Rail/multimodal figures and tables",
        "regenerate",
        "rerun figure scripts from audited rail outputs",
    ),
    InvalidationRowSpec(
        "rail_source_or_timing",
        "Rail GTFS, timetable, shortest-path, source-decision, capacity, or availability evidence changes",
        "reports",
        "Report text citing old rail evidence or multimodal assumptions",
        "regenerate",
        "rerun claim-alignment and manuscript/report review packets",
    ),
    InvalidationRowSpec(
        "demand_fleet_behavior_transfer_dispatch",
        "Demand, fleet, behavior, transfer, dispatch, policy, or experiment design changes",
        "compact_outputs",
        "Compact outputs generated from old demand/fleet/dispatch assumptions",
        "regenerate",
        "rerun compact output producer and audit package",
    ),
    InvalidationRowSpec(
        "demand_fleet_behavior_transfer_dispatch",
        "Demand, fleet, behavior, transfer, dispatch, policy, or experiment design changes",
        "full_outputs",
        "Full outputs generated from old demand/fleet/dispatch assumptions",
        "mark_non_evidence",
        "exclude old full outputs until rerun after compact promotion",
    ),
    InvalidationRowSpec(
        "demand_fleet_behavior_transfer_dispatch",
        "Demand, fleet, behavior, transfer, dispatch, policy, or experiment design changes",
        "statistics",
        "Metric confidence intervals and paired deltas from old outputs",
        "regenerate",
        "rerun statistics and replication adequacy packets",
    ),
    InvalidationRowSpec(
        "demand_fleet_behavior_transfer_dispatch",
        "Demand, fleet, behavior, transfer, dispatch, policy, or experiment design changes",
        "sensitivity",
        "Sensitivity inputs and Morris/Sobol outputs derived from old behavior assumptions",
        "regenerate",
        "rerun sensitivity analysis and diagnostics",
    ),
    InvalidationRowSpec(
        "demand_fleet_behavior_transfer_dispatch",
        "Demand, fleet, behavior, transfer, dispatch, policy, or experiment design changes",
        "ml_labels",
        "Risk labels derived from old output metrics",
        "regenerate",
        "rerun ML label derivation from audited outputs",
    ),
    InvalidationRowSpec(
        "demand_fleet_behavior_transfer_dispatch",
        "Demand, fleet, behavior, transfer, dispatch, policy, or experiment design changes",
        "ml_outputs",
        "ML metrics, feature importance, or explanation outputs from old labels",
        "regenerate",
        "rerun ML analysis after output audit and leakage checks",
    ),
    InvalidationRowSpec(
        "demand_fleet_behavior_transfer_dispatch",
        "Demand, fleet, behavior, transfer, dispatch, policy, or experiment design changes",
        "figures",
        "Figures derived from old output or statistics tables",
        "regenerate",
        "rerun figure scripts after statistics audit",
    ),
    InvalidationRowSpec(
        "demand_fleet_behavior_transfer_dispatch",
        "Demand, fleet, behavior, transfer, dispatch, policy, or experiment design changes",
        "reports",
        "Report text citing old demand, fleet, behavior, or output metrics",
        "regenerate",
        "rerun claim-alignment and manuscript/report review packets",
    ),
    InvalidationRowSpec(
        "disruption_library_or_exposure",
        "Disruption scenario library, exposure mapping, or disruption probability changes",
        "compact_outputs",
        "Compact outputs generated from old disruption scenarios",
        "regenerate",
        "rerun compact output producer and audit package",
    ),
    InvalidationRowSpec(
        "disruption_library_or_exposure",
        "Disruption scenario library, exposure mapping, or disruption probability changes",
        "full_outputs",
        "Full outputs generated from old disruption scenarios",
        "mark_non_evidence",
        "exclude old full outputs until rerun after compact promotion",
    ),
    InvalidationRowSpec(
        "disruption_library_or_exposure",
        "Disruption scenario library, exposure mapping, or disruption probability changes",
        "sensitivity",
        "Sensitivity outputs based on old disruption factors",
        "regenerate",
        "rerun sensitivity analysis and diagnostics",
    ),
    InvalidationRowSpec(
        "disruption_library_or_exposure",
        "Disruption scenario library, exposure mapping, or disruption probability changes",
        "ml_labels",
        "Risk labels derived from old disruption outcomes",
        "regenerate",
        "rerun ML label derivation from audited outputs",
    ),
    InvalidationRowSpec(
        "disruption_library_or_exposure",
        "Disruption scenario library, exposure mapping, or disruption probability changes",
        "ml_outputs",
        "ML outputs trained or explained from old disruption labels",
        "regenerate",
        "rerun ML analysis after output audit and leakage checks",
    ),
    InvalidationRowSpec(
        "disruption_library_or_exposure",
        "Disruption scenario library, exposure mapping, or disruption probability changes",
        "figures",
        "Stress-response figures based on old disruption scenarios",
        "regenerate",
        "rerun figure scripts after output audit",
    ),
    InvalidationRowSpec(
        "disruption_library_or_exposure",
        "Disruption scenario library, exposure mapping, or disruption probability changes",
        "reports",
        "Report text citing old disruption scenarios or stress conclusions",
        "regenerate",
        "rerun claim-alignment and manuscript/report review packets",
    ),
    InvalidationRowSpec(
        "benchmark_cache_or_threshold",
        "External benchmark cache, OSRM/R5 snapshot, validation threshold, or benchmark decision changes",
        "benchmark_review_packets",
        "Benchmark review, benchmark decision, and threshold packets",
        "regenerate",
        "rerun benchmark review and decision packets",
    ),
    InvalidationRowSpec(
        "benchmark_cache_or_threshold",
        "External benchmark cache, OSRM/R5 snapshot, validation threshold, or benchmark decision changes",
        "claim_boundaries",
        "Compact/full travel-time plausibility claim boundaries",
        "regenerate",
        "rerun claim-boundary review for benchmark wording",
    ),
    InvalidationRowSpec(
        "benchmark_cache_or_threshold",
        "External benchmark cache, OSRM/R5 snapshot, validation threshold, or benchmark decision changes",
        "figures",
        "Benchmark or plausibility figures",
        "regenerate",
        "rerun figure scripts from audited benchmark outputs",
    ),
    InvalidationRowSpec(
        "benchmark_cache_or_threshold",
        "External benchmark cache, OSRM/R5 snapshot, validation threshold, or benchmark decision changes",
        "reports",
        "Report text citing old benchmark thresholds or pass/warn/fail results",
        "regenerate",
        "rerun claim-alignment and manuscript/report review packets",
    ),
    InvalidationRowSpec(
        "result_csv_or_manifest",
        "Compact or full result CSV, manifest, run log, or experiment-output changes",
        "statistics",
        "Confidence intervals, paired deltas, and replication adequacy derived from old results",
        "regenerate",
        "rerun statistics, CRN, deterministic rerun, and replication adequacy audits",
    ),
    InvalidationRowSpec(
        "result_csv_or_manifest",
        "Compact or full result CSV, manifest, run log, or experiment-output changes",
        "sensitivity",
        "Sensitivity outputs derived from old results",
        "regenerate",
        "rerun sensitivity analysis and diagnostics",
    ),
    InvalidationRowSpec(
        "result_csv_or_manifest",
        "Compact or full result CSV, manifest, run log, or experiment-output changes",
        "ml_outputs",
        "Risk models, feature importance, clusters, and explanation outputs derived from old results",
        "regenerate",
        "rerun ML label derivation, model metrics, and explanation review",
    ),
    InvalidationRowSpec(
        "result_csv_or_manifest",
        "Compact or full result CSV, manifest, run log, or experiment-output changes",
        "figures",
        "Figures generated from old result/statistics/ML outputs",
        "regenerate",
        "rerun figure scripts after source-data audit",
    ),
    InvalidationRowSpec(
        "result_csv_or_manifest",
        "Compact or full result CSV, manifest, run log, or experiment-output changes",
        "reports",
        "Report text citing old results, statistics, or ML outputs",
        "regenerate",
        "rerun claim-alignment and manuscript/report review packets",
    ),
    InvalidationRowSpec(
        "result_csv_or_manifest",
        "Compact or full result CSV, manifest, run log, or experiment-output changes",
        "review_packages",
        "Review packages containing old outputs or reports",
        "regenerate",
        "rebuild review package inventory, ZIP, path audit, and handoff sidecar",
    ),
    InvalidationRowSpec(
        "claim_boundary_or_readiness_logic",
        "Claim-boundary wording, readiness logic, formal guard, or review-package logic changes",
        "publication_readiness",
        "Publication readiness audit derived from old gate logic",
        "regenerate",
        "rerun publication readiness audit with blocker flags",
    ),
    InvalidationRowSpec(
        "claim_boundary_or_readiness_logic",
        "Claim-boundary wording, readiness logic, formal guard, or review-package logic changes",
        "final_study_readiness",
        "Final-study readiness audit derived from old gate logic",
        "regenerate",
        "rerun final-study readiness audit with blocker flags",
    ),
    InvalidationRowSpec(
        "claim_boundary_or_readiness_logic",
        "Claim-boundary wording, readiness logic, formal guard, or review-package logic changes",
        "formal_guard",
        "Formal guard and acceptance-package checks derived from old logic",
        "regenerate",
        "rerun formal guard and formal package validation",
    ),
    InvalidationRowSpec(
        "claim_boundary_or_readiness_logic",
        "Claim-boundary wording, readiness logic, formal guard, or review-package logic changes",
        "review_package_text",
        "Review-package notes, handoff text, and package-path audit wording",
        "regenerate",
        "rebuild review package inventory/path audit/handoff sidecar",
    ),
    InvalidationRowSpec(
        "claim_boundary_or_readiness_logic",
        "Claim-boundary wording, readiness logic, formal guard, or review-package logic changes",
        "review_packages",
        "Review package ZIPs assembled with old claim-boundary logic",
        "mark_non_evidence",
        "exclude old review packages or rebuild and re-audit them",
    ),
    InvalidationRowSpec(
        "claim_boundary_or_readiness_logic",
        "Claim-boundary wording, readiness logic, formal guard, or review-package logic changes",
        "reports",
        "Reports or manuscripts using old claim-boundary wording",
        "regenerate",
        "rerun claim-alignment and manuscript/report review packets",
    ),
)


def build_artifact_invalidation_rows(
    *,
    default_status: str = "stale_pending_disposition",
) -> list[dict[str, str]]:
    """Return the static pre-Phase-9 invalidation matrix rows."""

    if default_status not in ALLOWED_DISPOSITION_STATUSES:
        raise ValueError(f"unsupported disposition status: {default_status}")
    return [_row_from_spec(spec, default_status=default_status) for spec in INVALIDATION_ROW_SPECS]


def write_artifact_invalidation_matrix(
    *,
    rows: Sequence[Mapping[str, str]] | None = None,
    output_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_CSV,
    manifest_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_MANIFEST,
    doc_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_DOC,
) -> dict[str, Any]:
    """Write CSV, JSON manifest, and Markdown review-support matrix."""

    matrix_rows = [dict(row) for row in rows] if rows is not None else build_artifact_invalidation_rows()
    _validate_rows(matrix_rows)

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ARTIFACT_INVALIDATION_FIELDS)
        writer.writeheader()
        writer.writerows(matrix_rows)

    summary = summarize_artifact_invalidation_rows(matrix_rows)
    summary.update(
        {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
            "outputs": {
                "csv": _display_path(output),
                "manifest": _display_path(manifest),
                "doc": _display_path(doc),
            },
            "can_mark_complete": False,
            "phase9_promotion_ready": False,
            "publication_ready": False,
            "final_study_ready": False,
            "formal_acceptance_evidence": False,
        }
    )
    preserve_generated_at_when_unchanged(summary, manifest)
    write_json_manifest_if_changed(summary, manifest, sort_keys=True)
    write_text_if_changed(build_artifact_invalidation_markdown(summary, matrix_rows), doc)
    return summary


def build_artifact_invalidation_closeout_template_rows(
    rows: Sequence[Mapping[str, str]] | None = None,
) -> list[dict[str, str]]:
    """Return a reviewer closeout template for invalidation rows.

    The template is intentionally pending by default. It is a worksheet for
    recording rerun/exclusion/non-evidence dispositions after downstream
    artifacts are handled; it is not a gate approval.
    """

    matrix_rows = [dict(row) for row in rows] if rows is not None else build_artifact_invalidation_rows()
    _validate_rows(matrix_rows)
    closeout_rows: list[dict[str, str]] = []
    for row in matrix_rows:
        closeout_rows.append(
            {
                "closeout_schema_version": "1",
                "invalidation_row_id": _row_key(row),
                "upstream_change_group": row["upstream_change_group"],
                "stale_downstream_group": row["stale_downstream_group"],
                "required_disposition": row["required_disposition"],
                "actual_disposition": "pending",
                "closeout_status": "pending",
                "affected_artifacts_json": "[]",
                "upstream_artifacts_json": "[]",
                "downstream_before_artifacts_json": "[]",
                "downstream_after_artifacts_json": "[]",
                "exclusion_scope": "",
                "rerun_command": row["audit_or_regeneration_command"],
                "rerun_exit_code": "",
                "rerun_result": "not_run",
                "audit_command": "",
                "audit_exit_code": "",
                "audit_result": "not_run",
                "targeted_test_command": "",
                "targeted_test_exit_code": "",
                "targeted_test_result": "not_run",
                "reviewer_signoff_status": "unsigned",
                "reviewer_id": "",
                "reviewed_at_utc": "",
                "reviewer_evidence_path": "",
                "reviewer_evidence_sha256": "",
                "claim_boundary_effect": "blocks_claim_support",
                "claim_boundary_review_result": "pending",
                "phase9_promotion_effect": "blocks_phase9_promotion",
                "can_clear_invalidation_gate": "false",
                "publication_ready": "false",
                "final_study_ready": "false",
                "formal_acceptance_evidence": "false",
                "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
                "review_notes": "",
            }
        )
    return closeout_rows


def read_artifact_invalidation_closeout_rows(path: str | Path) -> list[dict[str, str]]:
    """Read and validate a filled artifact invalidation closeout CSV."""

    input_path = Path(path)
    with input_path.open("r", encoding="utf-8", newline="") as handle:
        rows = [dict(row) for row in csv.DictReader(handle)]
    for row in rows:
        for field in ARTIFACT_INVALIDATION_CLOSEOUT_FIELDS:
            row.setdefault(field, "")
    _validate_closeout_rows(rows)
    return rows


def write_artifact_invalidation_closeout_rows(
    closeout_rows: Sequence[Mapping[str, str]],
    *,
    output_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_TEMPLATE,
    manifest_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_MANIFEST,
    doc_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_DOC,
) -> dict[str, Any]:
    """Write a concrete artifact-invalidation closeout worksheet.

    This writer is used after separate reviewer-evidence application. It does
    not create reviewer evidence and never promotes publication or study
    closeout readiness by itself.
    """

    rows = [dict(row) for row in closeout_rows]
    for row in rows:
        for field in ARTIFACT_INVALIDATION_CLOSEOUT_FIELDS:
            row.setdefault(field, "")
    _validate_closeout_rows(rows)

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ARTIFACT_INVALIDATION_CLOSEOUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    summary = summarize_artifact_invalidation_closeout_rows(rows)
    summary.update(
        {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
            "outputs": {
                "csv": _display_path(output),
                "manifest": _display_path(manifest),
                "doc": _display_path(doc),
            },
            "can_mark_complete": False,
            "phase9_promotion_ready": False,
            "publication_ready": False,
            "final_study_ready": False,
            "formal_acceptance_evidence": False,
        }
    )
    preserve_generated_at_when_unchanged(summary, manifest)
    write_json_manifest_if_changed(summary, manifest, sort_keys=True)
    write_text_if_changed(
        build_artifact_invalidation_closeout_markdown(summary, rows),
        doc,
    )
    return summary


def write_artifact_invalidation_closeout_template(
    *,
    matrix_rows: Sequence[Mapping[str, str]] | None = None,
    output_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_TEMPLATE,
    manifest_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_MANIFEST,
    doc_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_DOC,
) -> dict[str, Any]:
    """Write a pending closeout worksheet for stale artifact disposition."""

    closeout_rows = build_artifact_invalidation_closeout_template_rows(matrix_rows)
    return write_artifact_invalidation_closeout_rows(
        closeout_rows,
        output_path=output_path,
        manifest_path=manifest_path,
        doc_path=doc_path,
    )


def apply_artifact_invalidation_reviewer_evidence(
    closeout_rows: Sequence[Mapping[str, str]],
    evidence_dir: str | Path,
    *,
    project_root: str | Path = PROJECT_ROOT,
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    """Apply machine-readable closeout reviewer evidence to closeout rows.

    The function only links evidence records that already exist on disk and
    pass the same fail-closed validation used by the readiness audit. It does
    not synthesize reviewer evidence from worksheet values.
    """

    root = Path(project_root)
    rows = [dict(row) for row in closeout_rows]
    for row in rows:
        for field in ARTIFACT_INVALIDATION_CLOSEOUT_FIELDS:
            row.setdefault(field, "")
    _validate_closeout_rows(rows)

    records_by_row: dict[str, tuple[Path, Mapping[str, Any]]] = {}
    evidence_root = Path(evidence_dir)
    load_blockers: list[str] = []
    for path in sorted(evidence_root.glob("*.json")):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - defensive path
            load_blockers.append(f"{_display_path(path)}:unreadable:{type(exc).__name__}")
            continue
        if not isinstance(value, Mapping):
            load_blockers.append(f"{_display_path(path)}:not_object")
            continue
        row_id = str(value.get("invalidation_row_id", "")).strip()
        if not row_id:
            load_blockers.append(f"{_display_path(path)}:missing_invalidation_row_id")
            continue
        if row_id in records_by_row:
            load_blockers.append(f"{row_id}:duplicate_reviewer_evidence")
            continue
        records_by_row[row_id] = (path, value)

    output_rows: list[dict[str, str]] = []
    applied_rows: list[str] = []
    rejected_rows: list[str] = []
    missing_rows: list[str] = []

    for row in rows:
        row_id = str(row["invalidation_row_id"])
        match = records_by_row.get(row_id)
        if match is None:
            missing_rows.append(row_id)
            output_rows.append(row)
            continue
        evidence_path, record = match
        candidate = dict(row)
        candidate["reviewer_id"] = str(record.get("reviewer_id", "")).strip()
        candidate["reviewed_at_utc"] = str(record.get("reviewed_at_utc", "")).strip()
        candidate["reviewer_signoff_status"] = str(record.get("decision", "")).strip()
        candidate["reviewer_evidence_path"] = _display_path(evidence_path)
        candidate["reviewer_evidence_sha256"] = _sha256_file(evidence_path)
        candidate["can_clear_invalidation_gate"] = "true"

        if _closeout_row_is_closed(candidate, project_root=root):
            applied_rows.append(row_id)
            output_rows.append(candidate)
            continue

        candidate["can_clear_invalidation_gate"] = "false"
        missing = _closeout_missing_evidence(
            candidate,
            _compact_closeout_source_manifest_review(candidate, root),
            project_root=root,
        )
        rejected_rows.append(f"{row_id}:{missing}")
        output_rows.append(row)

    summary = {
        "schema_version": 1,
        "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
        "input_row_count": len(rows),
        "evidence_record_count": len(records_by_row),
        "applied_row_count": len(applied_rows),
        "missing_evidence_record_count": len(missing_rows),
        "rejected_evidence_record_count": len(rejected_rows),
        "load_blocker_count": len(load_blockers),
        "applied_rows": applied_rows,
        "missing_rows": missing_rows,
        "rejected_rows": rejected_rows,
        "load_blockers": load_blockers,
        "can_mark_complete": False,
        "phase9_promotion_ready": False,
        "publication_ready": False,
        "final_study_ready": False,
        "formal_acceptance_evidence": False,
    }
    return output_rows, summary


def build_artifact_invalidation_closeout_action_rows(
    closeout_rows: Sequence[Mapping[str, str]] | None = None,
) -> list[dict[str, str]]:
    """Return dependency-ordered action rows for pending closeout work."""

    rows = (
        [dict(row) for row in closeout_rows]
        if closeout_rows is not None
        else build_artifact_invalidation_closeout_template_rows()
    )
    _validate_closeout_rows(rows)
    action_rows = [_closeout_action_row(row) for row in rows]
    return sorted(
        action_rows,
        key=lambda row: (
            int(row["action_order"]),
            row["dependency_stage"],
            row["upstream_change_group"],
            row["stale_downstream_group"],
        ),
    )


def write_artifact_invalidation_closeout_action_queue(
    *,
    closeout_rows: Sequence[Mapping[str, str]] | None = None,
    output_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_QUEUE,
    manifest_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_MANIFEST,
    doc_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_DOC,
) -> dict[str, Any]:
    """Write the non-acceptance action queue for closeout work."""

    action_rows = build_artifact_invalidation_closeout_action_rows(closeout_rows)
    _validate_action_rows(action_rows)

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_FIELDS,
        )
        writer.writeheader()
        writer.writerows(action_rows)

    summary = summarize_artifact_invalidation_closeout_action_rows(action_rows)
    summary.update(
        {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
            "outputs": {
                "csv": _display_path(output),
                "manifest": _display_path(manifest),
                "doc": _display_path(doc),
            },
            "can_mark_complete": False,
            "phase9_promotion_ready": False,
            "publication_ready": False,
            "final_study_ready": False,
            "formal_acceptance_evidence": False,
        }
    )
    preserve_generated_at_when_unchanged(summary, manifest)
    write_json_manifest_if_changed(summary, manifest, sort_keys=True)
    write_text_if_changed(
        build_artifact_invalidation_closeout_action_markdown(summary, action_rows),
        doc,
    )
    return summary


def build_artifact_invalidation_action_batch_inspection_rows(
    closeout_rows: Sequence[Mapping[str, str]] | None = None,
    *,
    project_root: str | Path = PROJECT_ROOT,
) -> list[dict[str, str]]:
    """Merge action-queue and readiness rows for non-closeout inspection."""

    action_rows = build_artifact_invalidation_closeout_action_rows(closeout_rows)
    readiness_rows = build_artifact_invalidation_closeout_readiness_rows(
        closeout_rows,
        project_root=project_root,
    )
    readiness_by_id = {
        str(row["invalidation_row_id"]): row for row in readiness_rows
    }
    rows: list[dict[str, str]] = []
    for action in action_rows:
        row_id = str(action["invalidation_row_id"])
        readiness = readiness_by_id.get(row_id)
        if readiness is None:
            raise ValueError(f"missing readiness row for action row {row_id}")
        classification = _action_batch_inspection_classification(
            action,
            readiness,
        )
        next_focus = _action_row_next_closeout_focus(action, classification)
        prerequisite_batch = _action_row_prerequisite_batch(action)
        rows.append(
            {
                "inspection_schema_version": "1",
                "action_order": str(action["action_order"]),
                "action_batch": str(action["action_batch"]),
                "dependency_stage": str(action["dependency_stage"]),
                "invalidation_row_id": row_id,
                "upstream_change_group": str(action["upstream_change_group"]),
                "stale_downstream_group": str(action["stale_downstream_group"]),
                "required_disposition": str(action["required_disposition"]),
                "recommended_disposition": str(action["recommended_disposition"]),
                "actual_disposition": str(readiness["actual_disposition"]),
                "closeout_status": str(readiness["closeout_status"]),
                "inspection_classification": classification,
                "can_clear_invalidation_gate": str(
                    readiness["can_clear_invalidation_gate"]
                ).lower(),
                "missing_evidence_json": str(readiness["missing_evidence_json"]),
                "next_closeout_focus": next_focus,
                "blocking_prerequisite_batch": prerequisite_batch,
                "blocking_prerequisite_status": _action_row_prerequisite_status(
                    action,
                    prerequisite_batch,
                ),
                "minimum_evidence_package_json": json.dumps(
                    _action_row_minimum_evidence_package(action),
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                "allowed_next_operation": _action_row_allowed_next_operation(action),
                "source_manifest_status": str(readiness["source_manifest_status"]),
                "source_manifest_path": str(readiness["source_manifest_path"]),
                "compact_closeout_eligibility_status": str(
                    readiness["compact_closeout_eligibility_status"]
                ),
                "reviewer_signoff_status": str(readiness["reviewer_signoff_status"]),
                "blocks_phase9_until_closed": str(
                    action["blocks_phase9_until_closed"]
                ).lower(),
                "can_close_without_reviewer_signoff": str(
                    action["can_close_without_reviewer_signoff"]
                ).lower(),
                "publication_ready": "false",
                "final_study_ready": "false",
                "formal_acceptance_evidence": "false",
                "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
            }
        )
    _validate_action_batch_inspection_rows(rows)
    return rows


def write_artifact_invalidation_action_batch_inspection(
    *,
    closeout_rows: Sequence[Mapping[str, str]] | None = None,
    source_closeout_path: str | Path | None = None,
    project_root: str | Path = PROJECT_ROOT,
    output_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_ACTION_BATCH_INSPECTION,
    manifest_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_ACTION_BATCH_INSPECTION_MANIFEST,
    doc_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_ACTION_BATCH_INSPECTION_DOC,
) -> dict[str, Any]:
    """Write action-batch inspection support without closing any row."""

    inspection_rows = build_artifact_invalidation_action_batch_inspection_rows(
        closeout_rows,
        project_root=project_root,
    )
    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    csv_text = _dict_csv_text(
        inspection_rows,
        ARTIFACT_INVALIDATION_ACTION_BATCH_INSPECTION_FIELDS,
    )
    write_text_if_changed(csv_text, output)
    csv_sha256 = _sha256_file(output)

    summary = summarize_artifact_invalidation_action_batch_inspection_rows(
        inspection_rows
    )
    summary.update(
        {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
            "csv_sha256": csv_sha256,
            "outputs": {
                "csv": _display_path(output),
                "manifest": _display_path(manifest),
                "doc": _display_path(doc),
            },
            "source_closeout_input": (
                _display_path(Path(source_closeout_path))
                if source_closeout_path is not None
                else "default_pending_template"
            ),
            "can_mark_complete": False,
            "can_clear_invalidation_gate": False,
            "phase9_promotion_ready": False,
            "publication_ready": False,
            "final_study_ready": False,
            "formal_acceptance_evidence": False,
            "must_not_be_used_as_closeout_manifest": True,
        }
    )
    preserve_generated_at_when_unchanged(summary, manifest)
    write_json_manifest_if_changed(summary, manifest, sort_keys=True)
    write_text_if_changed(
        build_artifact_invalidation_action_batch_inspection_markdown(
            summary,
            inspection_rows,
        ),
        doc,
    )
    return summary


def build_artifact_invalidation_closeout_readiness_rows(
    closeout_rows: Sequence[Mapping[str, str]] | None = None,
    *,
    project_root: str | Path = PROJECT_ROOT,
) -> list[dict[str, str]]:
    """Return a non-acceptance row-level audit of closeout evidence gaps."""

    rows = (
        [dict(row) for row in closeout_rows]
        if closeout_rows is not None
        else build_artifact_invalidation_closeout_template_rows()
    )
    _validate_closeout_rows(rows)
    action_by_id = {
        str(row["invalidation_row_id"]): row
        for row in build_artifact_invalidation_closeout_action_rows(rows)
    }
    root = Path(project_root)
    readiness_rows = [
        _closeout_readiness_row(row, action_by_id.get(str(row["invalidation_row_id"])), root)
        for row in rows
    ]
    _validate_closeout_readiness_rows(readiness_rows)
    return readiness_rows


def write_artifact_invalidation_closeout_readiness_audit(
    *,
    closeout_rows: Sequence[Mapping[str, str]] | None = None,
    source_closeout_path: str | Path | None = None,
    project_root: str | Path = PROJECT_ROOT,
    output_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_READINESS_AUDIT,
    manifest_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_READINESS_AUDIT_MANIFEST,
    doc_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_READINESS_AUDIT_DOC,
) -> dict[str, Any]:
    """Write a non-closeout audit of missing closeout evidence."""

    readiness_rows = build_artifact_invalidation_closeout_readiness_rows(
        closeout_rows,
        project_root=project_root,
    )
    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=ARTIFACT_INVALIDATION_CLOSEOUT_READINESS_FIELDS,
        )
        writer.writeheader()
        writer.writerows(readiness_rows)

    summary = summarize_artifact_invalidation_closeout_readiness_rows(readiness_rows)
    summary.update(
        {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
            "outputs": {
                "csv": _display_path(output),
                "manifest": _display_path(manifest),
                "doc": _display_path(doc),
            },
            "source_closeout_input": (
                _display_path(Path(source_closeout_path))
                if source_closeout_path is not None
                else "default_pending_template"
            ),
            "can_mark_complete": False,
            "can_clear_invalidation_gate": False,
            "phase9_promotion_ready": False,
            "publication_ready": False,
            "final_study_ready": False,
            "formal_acceptance_evidence": False,
            "must_not_be_used_as_closeout_manifest": True,
        }
    )
    preserve_generated_at_when_unchanged(summary, manifest)
    write_json_manifest_if_changed(summary, manifest, sort_keys=True)
    write_text_if_changed(
        build_artifact_invalidation_closeout_readiness_markdown(
            summary, readiness_rows
        ),
        doc,
    )
    return summary


def build_artifact_invalidation_quarantine_closeout_template_rows(
    closeout_rows: Sequence[Mapping[str, str]] | None = None,
) -> list[dict[str, str]]:
    """Return pending closeout rows for the immediate non-evidence quarantine batch."""

    rows = (
        [dict(row) for row in closeout_rows]
        if closeout_rows is not None
        else build_artifact_invalidation_closeout_template_rows()
    )
    _validate_closeout_rows(rows)
    action_rows = build_artifact_invalidation_closeout_action_rows(rows)
    quarantine_keys = {
        str(row["invalidation_row_id"])
        for row in action_rows
        if row["action_batch"] == "quarantine_non_evidence"
    }
    quarantine_rows = [
        dict(row) for row in rows if str(row["invalidation_row_id"]) in quarantine_keys
    ]
    return sorted(quarantine_rows, key=lambda row: str(row["invalidation_row_id"]))


def write_artifact_invalidation_quarantine_closeout_template(
    *,
    closeout_rows: Sequence[Mapping[str, str]] | None = None,
    output_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_TEMPLATE,
    manifest_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_MANIFEST,
    doc_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_DOC,
) -> dict[str, Any]:
    """Write a pending reviewer worksheet for the first quarantine batch."""

    quarantine_rows = build_artifact_invalidation_quarantine_closeout_template_rows(
        closeout_rows
    )
    _validate_closeout_rows(quarantine_rows)

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    csv_text = _dict_csv_text(
        quarantine_rows,
        ARTIFACT_INVALIDATION_CLOSEOUT_FIELDS,
    )
    write_text_if_changed(csv_text, output)
    csv_sha256 = _sha256_file(output)

    summary = summarize_artifact_invalidation_closeout_rows(quarantine_rows)
    summary.update(
        {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
            "source_action_batch": "quarantine_non_evidence",
            "quarantine_batch_only": True,
            "csv_sha256": csv_sha256,
            "outputs": {
                "csv": _display_path(output),
                "manifest": _display_path(manifest),
                "doc": _display_path(doc),
            },
            "can_mark_complete": False,
            "phase9_promotion_ready": False,
            "publication_ready": False,
            "final_study_ready": False,
            "formal_acceptance_evidence": False,
        }
    )
    preserve_generated_at_when_unchanged(summary, manifest)
    write_json_manifest_if_changed(summary, manifest, sort_keys=True)
    write_text_if_changed(
        build_artifact_invalidation_quarantine_closeout_markdown(
            summary, quarantine_rows
        ),
        doc,
    )
    return summary


def build_artifact_invalidation_quarantine_scope_rows(
    *,
    closeout_rows: Sequence[Mapping[str, str]] | None = None,
    project_root: str | Path = PROJECT_ROOT,
    search_roots: Sequence[str] = DEFAULT_QUARANTINE_CITATION_SEARCH_ROOTS,
) -> list[dict[str, str]]:
    """Return a non-acceptance scope/citation audit for quarantine rows."""

    root = Path(project_root)
    quarantine_rows = build_artifact_invalidation_quarantine_closeout_template_rows(
        closeout_rows
    )
    audit_rows: list[dict[str, str]] = []
    for row in quarantine_rows:
        audit_rows.extend(
            _quarantine_scope_finding_rows(
                row,
                project_root=root,
                search_roots=search_roots,
            )
        )
    _validate_quarantine_scope_rows(audit_rows)
    return audit_rows


def write_artifact_invalidation_quarantine_scope_audit(
    *,
    closeout_rows: Sequence[Mapping[str, str]] | None = None,
    project_root: str | Path = PROJECT_ROOT,
    search_roots: Sequence[str] = DEFAULT_QUARANTINE_CITATION_SEARCH_ROOTS,
    output_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_AUDIT,
    manifest_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_AUDIT_MANIFEST,
    doc_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_AUDIT_DOC,
) -> dict[str, Any]:
    """Write quarantine scope/citation audit support without closing rows."""

    audit_rows = build_artifact_invalidation_quarantine_scope_rows(
        closeout_rows=closeout_rows,
        project_root=project_root,
        search_roots=search_roots,
    )
    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_FIELDS,
        )
        writer.writeheader()
        writer.writerows(audit_rows)

    summary = summarize_artifact_invalidation_quarantine_scope_rows(audit_rows)
    summary.update(
        {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
            "source_action_batch": "quarantine_non_evidence",
            "outputs": {
                "csv": _display_path(output),
                "manifest": _display_path(manifest),
                "doc": _display_path(doc),
            },
            "can_mark_complete": False,
            "can_clear_invalidation_gate": False,
            "phase9_promotion_ready": False,
            "publication_ready": False,
            "final_study_ready": False,
            "formal_acceptance_evidence": False,
        }
    )
    preserve_generated_at_when_unchanged(summary, manifest)
    write_json_manifest_if_changed(summary, manifest, sort_keys=True)
    write_text_if_changed(
        build_artifact_invalidation_quarantine_scope_markdown(summary, audit_rows),
        doc,
    )
    return summary


def build_artifact_invalidation_quarantine_non_evidence_index_rows(
    *,
    scope_rows: Sequence[Mapping[str, str]] | None = None,
    closeout_rows: Sequence[Mapping[str, str]] | None = None,
    project_root: str | Path = PROJECT_ROOT,
    search_roots: Sequence[str] = DEFAULT_QUARANTINE_CITATION_SEARCH_ROOTS,
    source_scope_audit_manifest: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_AUDIT_MANIFEST,
    source_quarantine_template_manifest: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_MANIFEST,
) -> list[dict[str, str]]:
    """Return a deduped non-evidence index for immediate quarantine candidates."""

    findings = (
        [dict(row) for row in scope_rows]
        if scope_rows is not None
        else build_artifact_invalidation_quarantine_scope_rows(
            closeout_rows=closeout_rows,
            project_root=project_root,
            search_roots=search_roots,
        )
    )
    _validate_quarantine_scope_rows(findings)
    action_by_id = {
        str(row["invalidation_row_id"]): row
        for row in build_artifact_invalidation_closeout_action_rows(closeout_rows)
        if row["action_batch"] == "quarantine_non_evidence"
    }
    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    for row in findings:
        if row["finding_type"] not in {"stale_artifact_candidate", "zip_candidate"}:
            continue
        if row["status"] != "present" or not row["matched_path"]:
            continue
        row_id = str(row["invalidation_row_id"])
        action = action_by_id.get(row_id)
        if action is None:
            continue
        key = (str(row["matched_path"]), str(row["finding_type"]))
        bucket = grouped.setdefault(
            key,
            {
                "row_ids": set(),
                "scope_ids": set(),
                "sha_values": set(),
                "finding_count": 0,
                "action": action,
            },
        )
        bucket["row_ids"].add(row_id)
        bucket["scope_ids"].add(str(row["scope_id"]))
        if row["sha256"]:
            bucket["sha_values"].add(str(row["sha256"]))
        bucket["finding_count"] += 1

    index_rows: list[dict[str, str]] = []
    for (matched_path, candidate_type), bucket in grouped.items():
        action = bucket["action"]
        row_ids = sorted(bucket["row_ids"])
        scope_ids = sorted(bucket["scope_ids"])
        sha_values = sorted(bucket["sha_values"])
        index_rows.append(
            {
                "index_schema_version": "1",
                "action_batch": "quarantine_non_evidence",
                "dependency_stage": str(action["dependency_stage"]),
                "stale_downstream_group": str(action["stale_downstream_group"]),
                "candidate_type": candidate_type,
                "matched_path": matched_path,
                "sha256": sha_values[0] if len(sha_values) == 1 else "",
                "invalidation_row_ids_json": json.dumps(row_ids, ensure_ascii=False),
                "source_row_count": str(len(row_ids)),
                "scope_ids_json": json.dumps(scope_ids, ensure_ascii=False),
                "source_finding_count": str(bucket["finding_count"]),
                "source_scope_audit_manifest": _display_path(Path(source_scope_audit_manifest)),
                "source_quarantine_template_manifest": _display_path(
                    Path(source_quarantine_template_manifest)
                ),
                "reviewer_handoff_note": (
                    "Reviewer may use this triage row as a source note when "
                    "preparing the separate main closeout record."
                ),
                "review_next_step": (
                    "If confirmed stale, copy this path, hash, and source row IDs "
                    "into the main closeout record; then record citation-removal "
                    "audit evidence and non-acceptance reviewer signoff."
                ),
                "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
            }
        )
    index_rows = sorted(
        index_rows,
        key=lambda row: (
            row["stale_downstream_group"],
            row["candidate_type"],
            row["matched_path"],
        ),
    )
    _validate_quarantine_non_evidence_index_rows(index_rows)
    return index_rows


def write_artifact_invalidation_quarantine_non_evidence_index(
    *,
    scope_rows: Sequence[Mapping[str, str]] | None = None,
    closeout_rows: Sequence[Mapping[str, str]] | None = None,
    project_root: str | Path = PROJECT_ROOT,
    search_roots: Sequence[str] = DEFAULT_QUARANTINE_CITATION_SEARCH_ROOTS,
    output_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_NON_EVIDENCE_INDEX,
    manifest_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_NON_EVIDENCE_INDEX_MANIFEST,
    doc_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_NON_EVIDENCE_INDEX_DOC,
    source_scope_audit_manifest: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_AUDIT_MANIFEST,
    source_quarantine_template_manifest: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_MANIFEST,
) -> dict[str, Any]:
    """Write the deduped non-evidence index without closing quarantine rows."""

    index_rows = build_artifact_invalidation_quarantine_non_evidence_index_rows(
        scope_rows=scope_rows,
        closeout_rows=closeout_rows,
        project_root=project_root,
        search_roots=search_roots,
        source_scope_audit_manifest=source_scope_audit_manifest,
        source_quarantine_template_manifest=source_quarantine_template_manifest,
    )
    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=ARTIFACT_INVALIDATION_QUARANTINE_NON_EVIDENCE_INDEX_FIELDS,
        )
        writer.writeheader()
        writer.writerows(index_rows)

    scope_summary = summarize_artifact_invalidation_quarantine_scope_rows(
        [dict(row) for row in scope_rows]
        if scope_rows is not None
        else build_artifact_invalidation_quarantine_scope_rows(
            closeout_rows=closeout_rows,
            project_root=project_root,
            search_roots=search_roots,
        )
    )
    summary = summarize_artifact_invalidation_quarantine_non_evidence_index_rows(
        index_rows,
        source_scope_summary=scope_summary,
    )
    summary.update(
        {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
            "source_action_batch": "quarantine_non_evidence",
            "quarantine_batch_only": True,
            "outputs": {
                "csv": _display_path(output),
                "manifest": _display_path(manifest),
                "doc": _display_path(doc),
            },
            "can_mark_complete": False,
            "can_clear_invalidation_gate": False,
            "phase9_promotion_ready": False,
            "publication_ready": False,
            "final_study_ready": False,
            "formal_acceptance_evidence": False,
            "acceptance_ready": False,
            "must_not_be_used_as_closeout_manifest": True,
        }
    )
    preserve_generated_at_when_unchanged(summary, manifest)
    write_json_manifest_if_changed(summary, manifest, sort_keys=True)
    write_text_if_changed(
        build_artifact_invalidation_quarantine_non_evidence_index_markdown(
            summary, index_rows
        ),
        doc,
    )
    return summary


def build_artifact_invalidation_quarantine_transfer_packet_rows(
    *,
    index_rows: Sequence[Mapping[str, str]] | None = None,
    scope_rows: Sequence[Mapping[str, str]] | None = None,
    closeout_rows: Sequence[Mapping[str, str]] | None = None,
    project_root: str | Path = PROJECT_ROOT,
    search_roots: Sequence[str] = DEFAULT_QUARANTINE_CITATION_SEARCH_ROOTS,
    source_non_evidence_index_manifest: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_NON_EVIDENCE_INDEX_MANIFEST,
    source_scope_audit_manifest: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_AUDIT_MANIFEST,
    source_quarantine_template_manifest: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_MANIFEST,
) -> list[dict[str, str]]:
    """Return row-level transfer notes for the immediate quarantine batch."""

    findings = (
        [dict(row) for row in scope_rows]
        if scope_rows is not None
        else build_artifact_invalidation_quarantine_scope_rows(
            closeout_rows=closeout_rows,
            project_root=project_root,
            search_roots=search_roots,
        )
    )
    _validate_quarantine_scope_rows(findings)
    index = (
        [dict(row) for row in index_rows]
        if index_rows is not None
        else build_artifact_invalidation_quarantine_non_evidence_index_rows(
            scope_rows=findings,
            closeout_rows=closeout_rows,
            project_root=project_root,
            search_roots=search_roots,
            source_scope_audit_manifest=source_scope_audit_manifest,
            source_quarantine_template_manifest=source_quarantine_template_manifest,
        )
    )
    _validate_quarantine_non_evidence_index_rows(index)
    action_rows = [
        row
        for row in build_artifact_invalidation_closeout_action_rows(closeout_rows)
        if row["action_batch"] == "quarantine_non_evidence"
    ]

    artifacts_by_row_id: dict[str, list[dict[str, str]]] = {}
    scope_ids_by_row_id: dict[str, set[str]] = {}
    for index_row_number, row in enumerate(index, start=1):
        row_ids = [str(item) for item in json.loads(row["invalidation_row_ids_json"])]
        scope_ids = [str(item) for item in json.loads(row["scope_ids_json"])]
        for row_id in row_ids:
            artifacts_by_row_id.setdefault(row_id, []).append(
                _candidate_artifact_transfer_record(
                    {
                        "source_index_row_number": str(index_row_number),
                        "path": str(row["matched_path"]),
                        "candidate_type": str(row["candidate_type"]),
                        "sha256": str(row["sha256"]),
                        "source_finding_count": str(row["source_finding_count"]),
                    },
                    Path(project_root),
                )
            )
            scope_ids_by_row_id.setdefault(row_id, set()).update(scope_ids)

    current_refs_by_row_id: dict[str, set[str]] = {}
    for row in findings:
        if row["finding_type"] != "reference_hit":
            continue
        matched_path = str(row["matched_path"])
        if _is_archival_reference_path(matched_path):
            continue
        current_refs_by_row_id.setdefault(str(row["invalidation_row_id"]), set()).add(
            matched_path
        )
        if row.get("scope_id"):
            scope_ids_by_row_id.setdefault(str(row["invalidation_row_id"]), set()).add(
                str(row["scope_id"])
            )

    transfer_rows: list[dict[str, str]] = []
    for action in action_rows:
        row_id = str(action["invalidation_row_id"])
        candidate_artifacts = sorted(
            artifacts_by_row_id.get(row_id, []),
            key=lambda item: (item["candidate_type"], item["path"]),
        )
        reference_paths = sorted(current_refs_by_row_id.get(row_id, set()))
        scope_ids = sorted(scope_ids_by_row_id.get(row_id, set()))
        transfer_rows.append(
            {
                "transfer_schema_version": "1",
                "action_batch": "quarantine_non_evidence",
                "dependency_stage": str(action["dependency_stage"]),
                "invalidation_row_id": row_id,
                "upstream_change_group": str(action["upstream_change_group"]),
                "stale_downstream_group": str(action["stale_downstream_group"]),
                "required_disposition": str(action["required_disposition"]),
                "recommended_disposition": str(action["recommended_disposition"]),
                "candidate_artifact_count": str(len(candidate_artifacts)),
                "candidate_artifacts_json": json.dumps(
                    candidate_artifacts, ensure_ascii=False
                ),
                "current_reference_hit_count": str(len(reference_paths)),
                "reference_hit_paths_json": json.dumps(reference_paths, ensure_ascii=False),
                "source_scope_ids_json": json.dumps(scope_ids, ensure_ascii=False),
                "source_non_evidence_index_manifest": _display_path(
                    Path(source_non_evidence_index_manifest)
                ),
                "source_scope_audit_manifest": _display_path(Path(source_scope_audit_manifest)),
                "source_quarantine_template_manifest": _display_path(
                    Path(source_quarantine_template_manifest)
                ),
                "transfer_status": "draft_pending_reviewer_confirmation",
                "required_reviewer_action": (
                    "Confirm stale/non-evidence treatment, copy confirmed "
                    "paths and hashes into the separate main closeout record, "
                    "run citation-removal or exclusion audit, and sign off only "
                    "for invalidation closeout."
                ),
                "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
            }
        )
    transfer_rows = sorted(
        transfer_rows,
        key=lambda row: (
            row["stale_downstream_group"],
            row["upstream_change_group"],
            row["invalidation_row_id"],
        ),
    )
    _validate_quarantine_transfer_packet_rows(transfer_rows)
    return transfer_rows


def summarize_artifact_invalidation_quarantine_transfer_packet_rows(
    rows: Sequence[Mapping[str, str]],
    *,
    source_index_summary: Mapping[str, Any] | None = None,
    source_scope_summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Summarize transfer notes without granting closeout or readiness."""

    _validate_quarantine_transfer_packet_rows(rows)
    expected_ids = _expected_quarantine_row_ids()
    covered_ids = {str(row.get("invalidation_row_id", "")) for row in rows}
    missing_ids = sorted(expected_ids - covered_ids)
    candidate_count = sum(int(row.get("candidate_artifact_count", "0")) for row in rows)
    artifact_match_count = 0
    artifact_missing_count = 0
    artifact_mismatch_count = 0
    for row in rows:
        for artifact in json.loads(str(row.get("candidate_artifacts_json", "[]"))):
            status = str(artifact.get("current_integrity_status", "unchecked"))
            if status == "hash_match":
                artifact_match_count += 1
            elif status == "missing":
                artifact_missing_count += 1
            elif status == "hash_mismatch":
                artifact_mismatch_count += 1
    current_reference_hit_count = sum(
        int(row.get("current_reference_hit_count", "0")) for row in rows
    )
    source_index_artifact_count = (
        int(source_index_summary.get("indexed_artifact_count", 0))
        if source_index_summary is not None
        else candidate_count
    )
    source_index_candidate_assignment_count = (
        int(source_index_summary.get("source_candidate_finding_count", 0))
        if source_index_summary is not None
        else candidate_count
    )
    source_scope_current_reference_hit_count = (
        int(source_scope_summary.get("unresolved_current_reference_count", 0))
        if source_scope_summary is not None
        else current_reference_hit_count
    )
    source_reference_dedup_delta_count = max(
        source_scope_current_reference_hit_count - current_reference_hit_count,
        0,
    )
    source_integrity_ready = (
        not missing_ids
        and candidate_count == source_index_candidate_assignment_count
        and candidate_count == artifact_match_count
        and artifact_missing_count == 0
        and artifact_mismatch_count == 0
        and current_reference_hit_count <= source_scope_current_reference_hit_count
    )
    return {
        "row_count": len(rows),
        "quarantine_batch_only": True,
        "expected_quarantine_row_count": len(expected_ids),
        "covered_quarantine_row_count": len(covered_ids & expected_ids),
        "missing_quarantine_row_ids": missing_ids,
        "candidate_artifact_count": candidate_count,
        "candidate_artifact_hash_match_count": artifact_match_count,
        "candidate_artifact_missing_count": artifact_missing_count,
        "candidate_artifact_hash_mismatch_count": artifact_mismatch_count,
        "source_index_artifact_count": source_index_artifact_count,
        "source_index_candidate_assignment_count": source_index_candidate_assignment_count,
        "current_reference_hit_count": current_reference_hit_count,
        "source_scope_raw_current_reference_hit_count": source_scope_current_reference_hit_count,
        "source_reference_dedup_delta_count": source_reference_dedup_delta_count,
        "source_integrity_ready": source_integrity_ready,
        "draft_pending_reviewer_confirmation_count": sum(
            1
            for row in rows
            if row["transfer_status"] == "draft_pending_reviewer_confirmation"
        ),
        "can_clear_invalidation_gate": False,
        "can_mark_complete": False,
        "phase9_promotion_ready": False,
        "publication_ready": False,
        "final_study_ready": False,
        "formal_acceptance_evidence": False,
        "acceptance_ready": False,
        "must_not_be_used_as_closeout_manifest": True,
        "remaining_blockers": [
            "transfer packet is reviewer triage only and covers only immediate full-output/review-package quarantine rows",
            "transfer packet rows require reviewer confirmation, copied main closeout entries, citation-removal or exclusion audit evidence, and non-acceptance signoff"
        ],
    }


def write_artifact_invalidation_quarantine_transfer_packet(
    *,
    index_rows: Sequence[Mapping[str, str]] | None = None,
    scope_rows: Sequence[Mapping[str, str]] | None = None,
    closeout_rows: Sequence[Mapping[str, str]] | None = None,
    project_root: str | Path = PROJECT_ROOT,
    search_roots: Sequence[str] = DEFAULT_QUARANTINE_CITATION_SEARCH_ROOTS,
    output_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET,
    manifest_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET_MANIFEST,
    doc_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET_DOC,
    source_non_evidence_index_manifest: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_NON_EVIDENCE_INDEX_MANIFEST,
    source_scope_audit_manifest: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_AUDIT_MANIFEST,
    source_quarantine_template_manifest: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_MANIFEST,
) -> dict[str, Any]:
    """Write row-level transfer notes without closing any invalidation row."""

    findings = (
        [dict(row) for row in scope_rows]
        if scope_rows is not None
        else build_artifact_invalidation_quarantine_scope_rows(
            closeout_rows=closeout_rows,
            project_root=project_root,
            search_roots=search_roots,
        )
    )
    index = (
        [dict(row) for row in index_rows]
        if index_rows is not None
        else build_artifact_invalidation_quarantine_non_evidence_index_rows(
            scope_rows=findings,
            closeout_rows=closeout_rows,
            project_root=project_root,
            search_roots=search_roots,
            source_scope_audit_manifest=source_scope_audit_manifest,
            source_quarantine_template_manifest=source_quarantine_template_manifest,
        )
    )
    transfer_rows = build_artifact_invalidation_quarantine_transfer_packet_rows(
        index_rows=index,
        scope_rows=findings,
        closeout_rows=closeout_rows,
        project_root=project_root,
        search_roots=search_roots,
        source_non_evidence_index_manifest=source_non_evidence_index_manifest,
        source_scope_audit_manifest=source_scope_audit_manifest,
        source_quarantine_template_manifest=source_quarantine_template_manifest,
    )
    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET_FIELDS,
        )
        writer.writeheader()
        writer.writerows(transfer_rows)

    scope_summary = summarize_artifact_invalidation_quarantine_scope_rows(findings)
    index_summary = summarize_artifact_invalidation_quarantine_non_evidence_index_rows(
        index,
        source_scope_summary=scope_summary,
    )
    summary = summarize_artifact_invalidation_quarantine_transfer_packet_rows(
        transfer_rows,
        source_index_summary=index_summary,
        source_scope_summary=scope_summary,
    )
    summary.update(
        {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
            "source_action_batch": "quarantine_non_evidence",
            "quarantine_batch_only": True,
            "outputs": {
                "csv": _display_path(output),
                "manifest": _display_path(manifest),
                "doc": _display_path(doc),
            },
            "can_mark_complete": False,
            "can_clear_invalidation_gate": False,
            "phase9_promotion_ready": False,
            "publication_ready": False,
            "final_study_ready": False,
            "formal_acceptance_evidence": False,
            "acceptance_ready": False,
            "must_not_be_used_as_closeout_manifest": True,
        }
    )
    preserve_generated_at_when_unchanged(summary, manifest)
    write_json_manifest_if_changed(summary, manifest, sort_keys=True)
    write_text_if_changed(
        build_artifact_invalidation_quarantine_transfer_packet_markdown(
            summary, transfer_rows
        ),
        doc,
    )
    return summary


def build_artifact_invalidation_quarantine_closeout_prefill_rows(
    *,
    transfer_rows: Sequence[Mapping[str, str]] | None = None,
    index_rows: Sequence[Mapping[str, str]] | None = None,
    scope_rows: Sequence[Mapping[str, str]] | None = None,
    closeout_rows: Sequence[Mapping[str, str]] | None = None,
    project_root: str | Path = PROJECT_ROOT,
    search_roots: Sequence[str] = DEFAULT_QUARANTINE_CITATION_SEARCH_ROOTS,
) -> list[dict[str, str]]:
    """Return prefilled quarantine closeout rows without closing them."""

    transfers = (
        [dict(row) for row in transfer_rows]
        if transfer_rows is not None
        else build_artifact_invalidation_quarantine_transfer_packet_rows(
            index_rows=index_rows,
            scope_rows=scope_rows,
            closeout_rows=closeout_rows,
            project_root=project_root,
            search_roots=search_roots,
        )
    )
    by_id = {str(row["invalidation_row_id"]): row for row in transfers}
    rows: list[dict[str, str]] = []
    for row in build_artifact_invalidation_quarantine_closeout_template_rows(
        closeout_rows
    ):
        prefilled = dict(row)
        transfer = by_id.get(str(row["invalidation_row_id"]))
        if transfer is None:
            rows.append(prefilled)
            continue
        artifacts = _closeout_prefill_artifacts_from_transfer(transfer)
        reference_paths = json.loads(str(transfer["reference_hit_paths_json"]))
        source_manifests = _closeout_prefill_source_manifests(transfer)
        prefilled.update(
            {
                "actual_disposition": "marked_non_evidence",
                "closeout_status": "pending",
                "affected_artifacts_json": json.dumps(
                    artifacts,
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                "upstream_artifacts_json": json.dumps(
                    source_manifests,
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                "downstream_before_artifacts_json": json.dumps(
                    artifacts,
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                "downstream_after_artifacts_json": "[]",
                "exclusion_scope": _closeout_prefill_exclusion_scope(
                    transfer,
                    artifacts,
                    reference_paths,
                ),
                "rerun_command": str(transfer["required_reviewer_action"]),
                "rerun_exit_code": "",
                "rerun_result": "not_run",
                "audit_command": (
                    ".\\.venv\\Scripts\\python scripts\\audit_claim_language.py "
                    "--fail-on-blockers"
                ),
                "audit_exit_code": "",
                "audit_result": "not_run",
                "targeted_test_command": (
                    ".\\.venv\\Scripts\\python "
                    "tests\\test_realworld_artifact_invalidation_matrix.py"
                ),
                "targeted_test_exit_code": "",
                "targeted_test_result": "not_run",
                "reviewer_signoff_status": "unsigned",
                "reviewer_id": "",
                "reviewed_at_utc": "",
                "reviewer_evidence_path": "",
                "reviewer_evidence_sha256": "",
                "claim_boundary_effect": "blocks_claim_support",
                "claim_boundary_review_result": "pending",
                "phase9_promotion_effect": "blocks_phase9_promotion",
                "can_clear_invalidation_gate": "false",
                "publication_ready": "false",
                "final_study_ready": "false",
                "formal_acceptance_evidence": "false",
                "review_notes": (
                    "prefilled from quarantine transfer packet; reviewer must "
                    "confirm stale/non-evidence scope before copying into the "
                    "main closeout record"
                ),
            }
        )
        rows.append(prefilled)
    _validate_closeout_rows(rows)
    return rows


def summarize_artifact_invalidation_quarantine_closeout_prefill_rows(
    rows: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    """Summarize prefilled quarantine closeout rows without accepting them."""

    _validate_closeout_rows(rows)
    base_summary = summarize_artifact_invalidation_closeout_rows(rows)
    artifact_count = sum(
        len(
            _parse_artifact_json_array(
                str(row.get("affected_artifacts_json", "[]")),
                row_index=index,
                field="affected_artifacts_json",
            )
        )
        for index, row in enumerate(rows, start=1)
    )
    prefilled_count = sum(
        1 for row in rows if str(row.get("actual_disposition", "")) == "marked_non_evidence"
    )
    base_summary.update(
        {
            "source_action_batch": "quarantine_non_evidence",
            "quarantine_batch_only": True,
            "prefill_only": True,
            "prefilled_row_count": prefilled_count,
            "prefilled_candidate_artifact_count": artifact_count,
            "can_mark_complete": False,
            "can_clear_invalidation_gate": False,
            "phase9_promotion_ready": False,
            "publication_ready": False,
            "final_study_ready": False,
            "formal_acceptance_evidence": False,
            "acceptance_ready": False,
            "must_not_be_used_as_closeout_manifest": True,
            "remaining_blockers": [
                "prefill rows are reviewer input only and do not close invalidation rows",
                "reviewer confirmation, citation-removal or exclusion audit, targeted test evidence, and non-acceptance signoff remain required",
            ],
        }
    )
    return base_summary


def write_artifact_invalidation_quarantine_closeout_prefill(
    *,
    transfer_rows: Sequence[Mapping[str, str]] | None = None,
    index_rows: Sequence[Mapping[str, str]] | None = None,
    scope_rows: Sequence[Mapping[str, str]] | None = None,
    closeout_rows: Sequence[Mapping[str, str]] | None = None,
    project_root: str | Path = PROJECT_ROOT,
    search_roots: Sequence[str] = DEFAULT_QUARANTINE_CITATION_SEARCH_ROOTS,
    output_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL,
    manifest_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL_MANIFEST,
    doc_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL_DOC,
    source_transfer_packet_manifest: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET_MANIFEST,
) -> dict[str, Any]:
    """Write a non-closing quarantine closeout prefill worksheet."""

    rows = build_artifact_invalidation_quarantine_closeout_prefill_rows(
        transfer_rows=transfer_rows,
        index_rows=index_rows,
        scope_rows=scope_rows,
        closeout_rows=closeout_rows,
        project_root=project_root,
        search_roots=search_roots,
    )
    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    csv_text = _dict_csv_text(rows, ARTIFACT_INVALIDATION_CLOSEOUT_FIELDS)
    write_text_if_changed(csv_text, output)
    csv_sha256 = _sha256_file(output)

    summary = summarize_artifact_invalidation_quarantine_closeout_prefill_rows(rows)
    source_summary = _quarantine_transfer_manifest_lineage(
        Path(source_transfer_packet_manifest)
    )
    summary.update(
        {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
            "csv_sha256": csv_sha256,
            **source_summary,
            "outputs": {
                "csv": _display_path(output),
                "manifest": _display_path(manifest),
                "doc": _display_path(doc),
            },
        }
    )
    preserve_generated_at_when_unchanged(summary, manifest)
    write_json_manifest_if_changed(summary, manifest, sort_keys=True)
    write_text_if_changed(
        build_artifact_invalidation_quarantine_closeout_prefill_markdown(
            summary,
            rows,
        ),
        doc,
    )
    return summary


def build_artifact_invalidation_quarantine_closeout_prefill_gap_audit_rows(
    *,
    prefill_rows: Sequence[Mapping[str, str]] | None = None,
    transfer_rows: Sequence[Mapping[str, str]] | None = None,
    index_rows: Sequence[Mapping[str, str]] | None = None,
    scope_rows: Sequence[Mapping[str, str]] | None = None,
    closeout_rows: Sequence[Mapping[str, str]] | None = None,
    project_root: str | Path = PROJECT_ROOT,
    search_roots: Sequence[str] = DEFAULT_QUARANTINE_CITATION_SEARCH_ROOTS,
    source_transfer_packet_manifest: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET_MANIFEST,
) -> list[dict[str, str]]:
    """Return non-closing gap rows for the quarantine closeout prefill."""

    transfers = (
        [dict(row) for row in transfer_rows]
        if transfer_rows is not None
        else build_artifact_invalidation_quarantine_transfer_packet_rows(
            index_rows=index_rows,
            scope_rows=scope_rows,
            closeout_rows=closeout_rows,
            project_root=project_root,
            search_roots=search_roots,
        )
    )
    prefill = (
        [dict(row) for row in prefill_rows]
        if prefill_rows is not None
        else build_artifact_invalidation_quarantine_closeout_prefill_rows(
            transfer_rows=transfers,
            index_rows=index_rows,
            scope_rows=scope_rows,
            closeout_rows=closeout_rows,
            project_root=project_root,
            search_roots=search_roots,
        )
    )
    _validate_closeout_rows(prefill)
    transfer_by_id = {str(row["invalidation_row_id"]): row for row in transfers}
    main_closeout_rows = (
        [dict(row) for row in closeout_rows]
        if closeout_rows is not None
        else build_artifact_invalidation_closeout_template_rows()
    )
    _validate_closeout_rows(main_closeout_rows)
    main_row_number_by_id = {
        str(row["invalidation_row_id"]): str(index)
        for index, row in enumerate(main_closeout_rows, start=1)
    }
    source_lineage = _quarantine_transfer_manifest_lineage(
        Path(source_transfer_packet_manifest)
    )

    rows: list[dict[str, str]] = []
    for index, row in enumerate(prefill, start=1):
        artifacts = _parse_artifact_json_array(
            str(row.get("affected_artifacts_json", "[]")),
            row_index=index,
            field="affected_artifacts_json",
        )
        transfer = transfer_by_id.get(str(row.get("invalidation_row_id", "")), {})
        reference_hit_count = int(str(transfer.get("current_reference_hit_count", "0") or "0"))
        gap_codes = _quarantine_prefill_gap_codes(row)
        artifact_gap = (
            "reviewer_confirmation_required"
            if artifacts or reference_hit_count
            else "reviewer_scope_confirmation_required"
        )
        if "artifact_or_exclusion_confirmation_missing" not in gap_codes:
            gap_codes.insert(0, "artifact_or_exclusion_confirmation_missing")
        rows.append(
            {
                "gap_schema_version": "1",
                "invalidation_row_id": str(row.get("invalidation_row_id", "")),
                "action_batch": "quarantine_non_evidence",
                "dependency_stage": str(
                    transfer.get("dependency_stage", "quarantine_closeout_prefill")
                ),
                "upstream_change_group": str(row.get("upstream_change_group", "")),
                "stale_downstream_group": str(row.get("stale_downstream_group", "")),
                "required_disposition": str(row.get("required_disposition", "")),
                "main_closeout_template_row_number": main_row_number_by_id.get(
                    str(row.get("invalidation_row_id", "")),
                    "",
                ),
                "actual_disposition": str(row.get("actual_disposition", "")),
                "closeout_status": str(row.get("closeout_status", "")),
                "candidate_artifact_count": str(len(artifacts)),
                "reference_hit_count": str(reference_hit_count),
                "source_transfer_packet_manifest": str(
                    source_lineage["source_transfer_packet_manifest"]
                ),
                "source_transfer_packet_manifest_sha256": str(
                    source_lineage["source_transfer_packet_manifest_sha256"]
                ),
                "source_transfer_packet_manifest_status": str(
                    source_lineage["source_transfer_packet_manifest_status"]
                ),
                "artifact_or_exclusion_gap": artifact_gap,
                "rerun_gap": _gap_status(
                    row,
                    "rerun_result",
                    passing_values={"pass", "not_applicable"},
                ),
                "audit_gap": _gap_status(
                    row,
                    "audit_result",
                    passing_values={"pass", "not_applicable"},
                ),
                "targeted_test_gap": _gap_status(
                    row,
                    "targeted_test_result",
                    passing_values={"pass", "not_applicable"},
                ),
                "claim_boundary_review_gap": _gap_status(
                    row,
                    "claim_boundary_review_result",
                    passing_values={"pass", "not_applicable"},
                ),
                "reviewer_signoff_gap": _gap_status(
                    row,
                    "reviewer_signoff_status",
                    passing_values={"signed_off_for_invalidation_closeout_only"},
                ),
                "main_closeout_copy_gap": "main_closeout_record_required",
                "blocking_gap_codes_json": json.dumps(
                    gap_codes,
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                "next_reviewer_action": (
                    "Confirm stale/non-evidence treatment, resolve claim-text "
                    "references, run the recorded audit and targeted test, then "
                    "copy the confirmed row into the main closeout record with "
                    "non-acceptance reviewer signoff."
                ),
                "can_clear_invalidation_gate": "false",
                "phase9_promotion_ready": "false",
                "publication_ready": "false",
                "final_study_ready": "false",
                "formal_acceptance_evidence": "false",
                "must_not_be_used_as_closeout_manifest": "true",
                "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
            }
        )
    return rows


def summarize_artifact_invalidation_quarantine_closeout_prefill_gap_audit_rows(
    rows: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    """Summarize quarantine prefill gaps without clearing any gate."""

    row_count = len(rows)
    candidate_artifact_count = sum(
        int(str(row.get("candidate_artifact_count", "0") or "0")) for row in rows
    )
    reference_hit_count = sum(
        int(str(row.get("reference_hit_count", "0") or "0")) for row in rows
    )
    gap_code_counts: dict[str, int] = {}
    for row in rows:
        for code in json.loads(str(row.get("blocking_gap_codes_json", "[]"))):
            gap_code_counts[str(code)] = gap_code_counts.get(str(code), 0) + 1
    blocking_rows = sum(
        1 for row in rows if json.loads(str(row.get("blocking_gap_codes_json", "[]")))
    )
    return {
        "schema_version": 1,
        "row_count": row_count,
        "prefill_gap_audit_only": True,
        "quarantine_batch_only": True,
        "source_action_batch": "quarantine_non_evidence",
        "candidate_artifact_count": candidate_artifact_count,
        "reference_hit_count": reference_hit_count,
        "blocking_gap_row_count": blocking_rows,
        "gap_code_counts": dict(sorted(gap_code_counts.items())),
        "can_mark_complete": False,
        "can_clear_invalidation_gate": False,
        "phase9_promotion_ready": False,
        "publication_ready": False,
        "final_study_ready": False,
        "formal_acceptance_evidence": False,
        "acceptance_ready": False,
        "must_not_be_used_as_closeout_manifest": True,
        "remaining_blockers": [
            "gap audit rows are reviewer-action support only",
            "artifact or exclusion confirmation, audit evidence, targeted test evidence, main closeout copy, and reviewer signoff remain required",
        ],
    }


def write_artifact_invalidation_quarantine_closeout_prefill_gap_audit(
    *,
    prefill_rows: Sequence[Mapping[str, str]] | None = None,
    transfer_rows: Sequence[Mapping[str, str]] | None = None,
    index_rows: Sequence[Mapping[str, str]] | None = None,
    scope_rows: Sequence[Mapping[str, str]] | None = None,
    closeout_rows: Sequence[Mapping[str, str]] | None = None,
    project_root: str | Path = PROJECT_ROOT,
    search_roots: Sequence[str] = DEFAULT_QUARANTINE_CITATION_SEARCH_ROOTS,
    output_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL_GAP_AUDIT,
    manifest_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL_GAP_AUDIT_MANIFEST,
    doc_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL_GAP_AUDIT_DOC,
    source_transfer_packet_manifest: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET_MANIFEST,
) -> dict[str, Any]:
    """Write a non-closing gap audit for quarantine closeout prefill rows."""

    rows = build_artifact_invalidation_quarantine_closeout_prefill_gap_audit_rows(
        prefill_rows=prefill_rows,
        transfer_rows=transfer_rows,
        index_rows=index_rows,
        scope_rows=scope_rows,
        closeout_rows=closeout_rows,
        project_root=project_root,
        search_roots=search_roots,
        source_transfer_packet_manifest=source_transfer_packet_manifest,
    )
    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    csv_text = _dict_csv_text(
        rows,
        ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL_GAP_FIELDS,
    )
    write_text_if_changed(csv_text, output)
    csv_sha256 = _sha256_file(output)

    summary = summarize_artifact_invalidation_quarantine_closeout_prefill_gap_audit_rows(
        rows
    )
    source_summary = _quarantine_transfer_manifest_lineage(
        Path(source_transfer_packet_manifest)
    )
    summary.update(
        {
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
            "csv_sha256": csv_sha256,
            **source_summary,
            "outputs": {
                "csv": _display_path(output),
                "manifest": _display_path(manifest),
                "doc": _display_path(doc),
            },
        }
    )
    preserve_generated_at_when_unchanged(summary, manifest)
    write_json_manifest_if_changed(summary, manifest, sort_keys=True)
    write_text_if_changed(
        build_artifact_invalidation_quarantine_closeout_prefill_gap_audit_markdown(
            summary,
            rows,
        ),
        doc,
    )
    return summary


def build_artifact_invalidation_quarantine_main_closeout_copy_audit_rows(
    *,
    prefill_rows: Sequence[Mapping[str, str]] | None = None,
    main_closeout_rows: Sequence[Mapping[str, str]] | None = None,
    transfer_rows: Sequence[Mapping[str, str]] | None = None,
    index_rows: Sequence[Mapping[str, str]] | None = None,
    scope_rows: Sequence[Mapping[str, str]] | None = None,
    closeout_rows: Sequence[Mapping[str, str]] | None = None,
    project_root: str | Path = PROJECT_ROOT,
    search_roots: Sequence[str] = DEFAULT_QUARANTINE_CITATION_SEARCH_ROOTS,
) -> list[dict[str, str]]:
    """Compare quarantine prefill rows against the main closeout record."""

    prefill = (
        [dict(row) for row in prefill_rows]
        if prefill_rows is not None
        else build_artifact_invalidation_quarantine_closeout_prefill_rows(
            transfer_rows=transfer_rows,
            index_rows=index_rows,
            scope_rows=scope_rows,
            closeout_rows=closeout_rows,
            project_root=project_root,
            search_roots=search_roots,
        )
    )
    main_rows = (
        [dict(row) for row in main_closeout_rows]
        if main_closeout_rows is not None
        else build_artifact_invalidation_closeout_template_rows()
    )
    _validate_closeout_rows(prefill)
    _validate_closeout_rows(main_rows)
    main_by_id = {str(row["invalidation_row_id"]): row for row in main_rows}
    main_row_number_by_id = {
        str(row["invalidation_row_id"]): str(index)
        for index, row in enumerate(main_rows, start=1)
    }

    rows: list[dict[str, str]] = []
    for index, prefill_row in enumerate(prefill, start=1):
        row_id = str(prefill_row.get("invalidation_row_id", ""))
        main_row = main_by_id.get(row_id)
        main_found = main_row is not None
        main = main_row or {}
        prefill_artifacts = _parse_artifact_json_array(
            str(prefill_row.get("affected_artifacts_json", "[]")),
            row_index=index,
            field="affected_artifacts_json",
        )
        main_artifacts = (
            _parse_artifact_json_array(
                str(main.get("affected_artifacts_json", "[]")),
                row_index=index,
                field="affected_artifacts_json",
            )
            if main_found
            else []
        )
        artifact_status = (
            "copied"
            if main_found and _artifact_records_equivalent(prefill_artifacts, main_artifacts)
            else "not_copied"
        )
        main_exclusion_scope = str(main.get("exclusion_scope", ""))
        prefill_exclusion_scope = str(prefill_row.get("exclusion_scope", ""))
        exclusion_status = (
            "copied"
            if main_found
            and main_exclusion_scope
            and (
                main_exclusion_scope == prefill_exclusion_scope
                or prefill_exclusion_scope.startswith("Prefill only.")
            )
            else "not_copied"
        )
        disposition_status = (
            "copied"
            if main_found
            and str(main.get("actual_disposition", ""))
            == str(prefill_row.get("actual_disposition", ""))
            else "not_copied"
        )
        main_gap_codes = (
            _quarantine_prefill_gap_codes(main)
            if main_found
            else ["main_closeout_row_missing"]
        )
        copy_gap_codes: list[str] = []
        if not main_found:
            copy_gap_codes.append("main_closeout_row_missing")
        if artifact_status != "copied":
            copy_gap_codes.append("main_affected_artifacts_not_copied")
        if exclusion_status != "copied":
            copy_gap_codes.append("main_exclusion_scope_not_copied")
        if disposition_status != "copied":
            copy_gap_codes.append("main_actual_disposition_not_copied")
        if main_gap_codes:
            copy_gap_codes.extend(f"main:{code}" for code in main_gap_codes)
        copy_status = (
            "copied_and_closeout_candidate_requires_support_audit"
            if main_found
            and not copy_gap_codes
            and _closeout_row_is_closed(main, project_root=project_root)
            else "main_closeout_copy_incomplete"
        )
        rows.append(
            {
                "copy_audit_schema_version": "1",
                "invalidation_row_id": row_id,
                "action_batch": "quarantine_non_evidence",
                "upstream_change_group": str(
                    prefill_row.get("upstream_change_group", "")
                ),
                "stale_downstream_group": str(
                    prefill_row.get("stale_downstream_group", "")
                ),
                "required_disposition": str(prefill_row.get("required_disposition", "")),
                "main_closeout_row_found": str(main_found).lower(),
                "main_closeout_template_row_number": main_row_number_by_id.get(row_id, ""),
                "prefill_actual_disposition": str(
                    prefill_row.get("actual_disposition", "")
                ),
                "main_actual_disposition": str(main.get("actual_disposition", "")),
                "prefill_closeout_status": str(prefill_row.get("closeout_status", "")),
                "main_closeout_status": str(main.get("closeout_status", "")),
                "prefill_candidate_artifact_count": str(len(prefill_artifacts)),
                "main_candidate_artifact_count": str(len(main_artifacts)),
                "affected_artifacts_copy_status": artifact_status,
                "exclusion_scope_copy_status": exclusion_status,
                "actual_disposition_copy_status": disposition_status,
                "main_closeout_evidence_status": (
                    "closed_candidate"
                    if main_found and _closeout_row_is_closed(main, project_root=project_root)
                    else "missing_or_incomplete"
                ),
                "main_closeout_gap_codes_json": json.dumps(
                    sorted(set(copy_gap_codes)),
                    ensure_ascii=False,
                ),
                "copy_audit_status": copy_status,
                "next_required_action": (
                    "Copy only reviewer-confirmed quarantine evidence into the "
                    "main closeout row, fill audit/test/signoff fields there, "
                    "then rerun the main closeout support audit."
                ),
                "can_clear_invalidation_gate": "false",
                "phase9_promotion_ready": "false",
                "publication_ready": "false",
                "final_study_ready": "false",
                "formal_acceptance_evidence": "false",
                "must_not_be_used_as_closeout_manifest": "true",
                "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
            }
        )
    _validate_quarantine_main_closeout_copy_audit_rows(rows)
    return rows


def summarize_artifact_invalidation_quarantine_main_closeout_copy_audit_rows(
    rows: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    """Summarize quarantine-to-main closeout copy state without clearing gates."""

    _validate_quarantine_main_closeout_copy_audit_rows(rows)
    blocker_counts: dict[str, int] = {}
    blocking_rows = 0
    for row in rows:
        codes = json.loads(str(row.get("main_closeout_gap_codes_json", "[]")))
        if codes:
            blocking_rows += 1
        for code in codes:
            blocker_counts[str(code)] = blocker_counts.get(str(code), 0) + 1
    return {
        "schema_version": 1,
        "row_count": len(rows),
        "copy_audit_only": True,
        "quarantine_batch_only": True,
        "source_action_batch": "quarantine_non_evidence",
        "main_row_found_count": sum(
            1 for row in rows if row["main_closeout_row_found"] == "true"
        ),
        "affected_artifacts_copied_count": sum(
            1 for row in rows if row["affected_artifacts_copy_status"] == "copied"
        ),
        "exclusion_scope_copied_count": sum(
            1 for row in rows if row["exclusion_scope_copy_status"] == "copied"
        ),
        "actual_disposition_copied_count": sum(
            1 for row in rows if row["actual_disposition_copy_status"] == "copied"
        ),
        "closed_candidate_count": sum(
            1 for row in rows if row["main_closeout_evidence_status"] == "closed_candidate"
        ),
        "blocking_copy_audit_row_count": blocking_rows,
        "copy_audit_blocker_counts": dict(sorted(blocker_counts.items())),
        "can_mark_complete": False,
        "can_clear_invalidation_gate": False,
        "phase9_promotion_ready": False,
        "publication_ready": False,
        "final_study_ready": False,
        "formal_acceptance_evidence": False,
        "acceptance_ready": False,
        "must_not_be_used_as_closeout_manifest": True,
        "remaining_blockers": [
            "copy audit rows are reviewer-action support only",
            "main closeout rows must contain reviewer-confirmed disposition, audit evidence, targeted-test evidence, and non-acceptance signoff before the main closeout support audit can clear invalidation only",
        ],
    }


def write_artifact_invalidation_quarantine_main_closeout_copy_audit(
    *,
    prefill_rows: Sequence[Mapping[str, str]] | None = None,
    main_closeout_rows: Sequence[Mapping[str, str]] | None = None,
    transfer_rows: Sequence[Mapping[str, str]] | None = None,
    index_rows: Sequence[Mapping[str, str]] | None = None,
    scope_rows: Sequence[Mapping[str, str]] | None = None,
    closeout_rows: Sequence[Mapping[str, str]] | None = None,
    project_root: str | Path = PROJECT_ROOT,
    search_roots: Sequence[str] = DEFAULT_QUARANTINE_CITATION_SEARCH_ROOTS,
    output_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_COPY_AUDIT,
    manifest_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_COPY_AUDIT_MANIFEST,
    doc_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_COPY_AUDIT_DOC,
    source_prefill_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL,
    source_main_closeout_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_TEMPLATE,
) -> dict[str, Any]:
    """Write a non-closing audit comparing prefill rows with main closeout rows."""

    rows = build_artifact_invalidation_quarantine_main_closeout_copy_audit_rows(
        prefill_rows=prefill_rows,
        main_closeout_rows=main_closeout_rows,
        transfer_rows=transfer_rows,
        index_rows=index_rows,
        scope_rows=scope_rows,
        closeout_rows=closeout_rows,
        project_root=project_root,
        search_roots=search_roots,
    )
    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    csv_text = _dict_csv_text(
        rows,
        ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_COPY_AUDIT_FIELDS,
    )
    write_text_if_changed(csv_text, output)
    csv_sha256 = _sha256_file(output)

    summary = summarize_artifact_invalidation_quarantine_main_closeout_copy_audit_rows(
        rows
    )
    prefill_path = Path(source_prefill_path)
    main_path = Path(source_main_closeout_path)
    summary.update(
        {
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
            "csv_sha256": csv_sha256,
            "source_prefill_path": _display_path(prefill_path),
            "source_prefill_sha256": _sha256_file(prefill_path) if prefill_path.exists() else "",
            "source_main_closeout_path": _display_path(main_path),
            "source_main_closeout_sha256": _sha256_file(main_path) if main_path.exists() else "",
            "outputs": {
                "csv": _display_path(output),
                "manifest": _display_path(manifest),
                "doc": _display_path(doc),
            },
        }
    )
    preserve_generated_at_when_unchanged(summary, manifest)
    write_json_manifest_if_changed(summary, manifest, sort_keys=True)
    write_text_if_changed(
        build_artifact_invalidation_quarantine_main_closeout_copy_audit_markdown(
            summary,
            rows,
        ),
        doc,
    )
    return summary


def build_artifact_invalidation_quarantine_main_closeout_draft_overlay_rows(
    *,
    prefill_rows: Sequence[Mapping[str, str]] | None = None,
    main_closeout_rows: Sequence[Mapping[str, str]] | None = None,
    transfer_rows: Sequence[Mapping[str, str]] | None = None,
    index_rows: Sequence[Mapping[str, str]] | None = None,
    scope_rows: Sequence[Mapping[str, str]] | None = None,
    closeout_rows: Sequence[Mapping[str, str]] | None = None,
    project_root: str | Path = PROJECT_ROOT,
    search_roots: Sequence[str] = DEFAULT_QUARANTINE_CITATION_SEARCH_ROOTS,
) -> list[dict[str, str]]:
    """Return a main-closeout-shaped draft with quarantine prefill overlaid.

    The output is deliberately non-closing. It reduces manual copy mistakes by
    placing reviewer-confirmation candidates in the main closeout row order, but
    every row remains pending and every readiness flag remains false.
    """

    prefill = (
        [dict(row) for row in prefill_rows]
        if prefill_rows is not None
        else build_artifact_invalidation_quarantine_closeout_prefill_rows(
            transfer_rows=transfer_rows,
            index_rows=index_rows,
            scope_rows=scope_rows,
            closeout_rows=closeout_rows,
            project_root=project_root,
            search_roots=search_roots,
        )
    )
    main_rows = (
        [dict(row) for row in main_closeout_rows]
        if main_closeout_rows is not None
        else build_artifact_invalidation_closeout_template_rows()
    )
    _validate_closeout_rows(prefill)
    _validate_closeout_rows(main_rows)

    prefill_by_id = {str(row["invalidation_row_id"]): row for row in prefill}
    overlay_rows: list[dict[str, str]] = []
    for main_row in main_rows:
        row_id = str(main_row.get("invalidation_row_id", ""))
        source_row = prefill_by_id.get(row_id, main_row)
        draft = _nonclosing_draft_closeout_row(source_row)
        if row_id in prefill_by_id:
            notes = str(draft.get("review_notes", "")).strip()
            overlay_note = (
                "draft overlay from quarantine prefill; reviewer must confirm "
                "before copying into the authoritative main closeout record"
            )
            draft["review_notes"] = (
                f"{notes}; {overlay_note}" if notes else overlay_note
            )
        overlay_rows.append(draft)

    _validate_quarantine_main_closeout_draft_overlay_rows(overlay_rows)
    return overlay_rows


def summarize_artifact_invalidation_quarantine_main_closeout_draft_overlay_rows(
    rows: Sequence[Mapping[str, str]],
    *,
    prefill_row_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Summarize a non-authoritative closeout draft overlay."""

    _validate_quarantine_main_closeout_draft_overlay_rows(rows)
    closeout_summary = summarize_artifact_invalidation_closeout_rows(rows)
    prefill_ids = {str(row_id) for row_id in (prefill_row_ids or [])}
    overlayed_rows = (
        sum(1 for row in rows if str(row.get("invalidation_row_id", "")) in prefill_ids)
        if prefill_ids
        else sum(
            1
            for row in rows
            if "draft overlay from quarantine prefill"
            in str(row.get("review_notes", ""))
        )
    )
    return {
        **closeout_summary,
        "schema_version": 1,
        "draft_overlay_only": True,
        "quarantine_batch_only": True,
        "source_action_batch": "quarantine_non_evidence",
        "prefill_row_count": len(prefill_ids) if prefill_ids else overlayed_rows,
        "overlayed_row_count": overlayed_rows,
        "closed_candidate_count": closeout_summary["closed_row_count"],
        "can_mark_complete": False,
        "can_clear_invalidation_gate": False,
        "phase9_promotion_ready": False,
        "publication_ready": False,
        "final_study_ready": False,
        "formal_acceptance_evidence": False,
        "acceptance_ready": False,
        "must_not_be_used_as_closeout_manifest": True,
        "must_not_replace_main_closeout_record": True,
        "remaining_blockers": [
            "draft overlay rows are reviewer-action support only",
            "authoritative main closeout rows still require reviewer-confirmed disposition, audit evidence, targeted-test evidence, claim-boundary review, and non-acceptance signoff",
        ],
    }


def write_artifact_invalidation_quarantine_main_closeout_draft_overlay(
    *,
    prefill_rows: Sequence[Mapping[str, str]] | None = None,
    main_closeout_rows: Sequence[Mapping[str, str]] | None = None,
    transfer_rows: Sequence[Mapping[str, str]] | None = None,
    index_rows: Sequence[Mapping[str, str]] | None = None,
    scope_rows: Sequence[Mapping[str, str]] | None = None,
    closeout_rows: Sequence[Mapping[str, str]] | None = None,
    project_root: str | Path = PROJECT_ROOT,
    search_roots: Sequence[str] = DEFAULT_QUARANTINE_CITATION_SEARCH_ROOTS,
    output_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_DRAFT_OVERLAY,
    manifest_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_DRAFT_OVERLAY_MANIFEST,
    doc_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_DRAFT_OVERLAY_DOC,
    source_prefill_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL,
    source_main_closeout_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_TEMPLATE,
) -> dict[str, Any]:
    """Write a non-authoritative closeout-schema draft overlay."""

    materialized_prefill = (
        [dict(row) for row in prefill_rows]
        if prefill_rows is not None
        else None
    )
    rows = build_artifact_invalidation_quarantine_main_closeout_draft_overlay_rows(
        prefill_rows=materialized_prefill,
        main_closeout_rows=main_closeout_rows,
        transfer_rows=transfer_rows,
        index_rows=index_rows,
        scope_rows=scope_rows,
        closeout_rows=closeout_rows,
        project_root=project_root,
        search_roots=search_roots,
    )
    prefill_ids = (
        [str(row["invalidation_row_id"]) for row in materialized_prefill]
        if materialized_prefill is not None
        else [
            str(row["invalidation_row_id"])
            for row in build_artifact_invalidation_quarantine_closeout_prefill_rows(
                transfer_rows=transfer_rows,
                index_rows=index_rows,
                scope_rows=scope_rows,
                closeout_rows=closeout_rows,
                project_root=project_root,
                search_roots=search_roots,
            )
        ]
    )

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    csv_text = _dict_csv_text(rows, ARTIFACT_INVALIDATION_CLOSEOUT_FIELDS)
    write_text_if_changed(csv_text, output)
    csv_sha256 = _sha256_file(output)

    summary = summarize_artifact_invalidation_quarantine_main_closeout_draft_overlay_rows(
        rows,
        prefill_row_ids=prefill_ids,
    )
    prefill_path = Path(source_prefill_path)
    main_path = Path(source_main_closeout_path)
    summary.update(
        {
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
            "csv_sha256": csv_sha256,
            "source_prefill_path": _display_path(prefill_path),
            "source_prefill_sha256": _sha256_file(prefill_path) if prefill_path.exists() else "",
            "source_main_closeout_path": _display_path(main_path),
            "source_main_closeout_sha256": _sha256_file(main_path) if main_path.exists() else "",
            "outputs": {
                "csv": _display_path(output),
                "manifest": _display_path(manifest),
                "doc": _display_path(doc),
            },
        }
    )
    preserve_generated_at_when_unchanged(summary, manifest)
    write_json_manifest_if_changed(summary, manifest, sort_keys=True)
    write_text_if_changed(
        build_artifact_invalidation_quarantine_main_closeout_draft_overlay_markdown(
            summary,
            rows,
        ),
        doc,
    )
    return summary


def build_artifact_invalidation_quarantine_reference_triage_rows(
    *,
    transfer_rows: Sequence[Mapping[str, str]] | None = None,
    index_rows: Sequence[Mapping[str, str]] | None = None,
    scope_rows: Sequence[Mapping[str, str]] | None = None,
    closeout_rows: Sequence[Mapping[str, str]] | None = None,
    project_root: str | Path = PROJECT_ROOT,
    search_roots: Sequence[str] = DEFAULT_QUARANTINE_CITATION_SEARCH_ROOTS,
    source_transfer_packet_manifest: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET_MANIFEST,
) -> list[dict[str, str]]:
    """Return non-closing triage rows for quarantine reference hits."""

    transfers = (
        [dict(row) for row in transfer_rows]
        if transfer_rows is not None
        else build_artifact_invalidation_quarantine_transfer_packet_rows(
            index_rows=index_rows,
            scope_rows=scope_rows,
            closeout_rows=closeout_rows,
            project_root=project_root,
            search_roots=search_roots,
        )
    )
    _validate_quarantine_transfer_packet_rows(transfers)
    source_lineage = _quarantine_transfer_manifest_lineage(
        Path(source_transfer_packet_manifest)
    )

    rows: list[dict[str, str]] = []
    for transfer in transfers:
        reference_paths = [
            str(item)
            for item in json.loads(str(transfer.get("reference_hit_paths_json", "[]")))
        ]
        for reference_path in sorted(set(reference_paths)):
            classification, priority, action = _quarantine_reference_triage(
                reference_path
            )
            rows.append(
                {
                    "triage_schema_version": "1",
                    "action_batch": "quarantine_non_evidence",
                    "dependency_stage": str(transfer.get("dependency_stage", "")),
                    "invalidation_row_id": str(
                        transfer.get("invalidation_row_id", "")
                    ),
                    "stale_downstream_group": str(
                        transfer.get("stale_downstream_group", "")
                    ),
                    "reference_path": reference_path,
                    "reference_classification": classification,
                    "review_priority": priority,
                    "required_reviewer_action": action,
                    "source_transfer_packet_manifest": str(
                        source_lineage["source_transfer_packet_manifest"]
                    ),
                    "source_transfer_packet_manifest_sha256": str(
                        source_lineage["source_transfer_packet_manifest_sha256"]
                    ),
                    "source_transfer_packet_manifest_status": str(
                        source_lineage["source_transfer_packet_manifest_status"]
                    ),
                    "can_clear_invalidation_gate": "false",
                    "phase9_promotion_ready": "false",
                    "publication_ready": "false",
                    "final_study_ready": "false",
                    "formal_acceptance_evidence": "false",
                    "must_not_be_used_as_closeout_manifest": "true",
                    "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
                }
            )
    priority_order = {
        "review_first": 0,
        "review_after_claim_text": 1,
        "review_for_context_only": 2,
        "confirm_excluded_from_release_scope": 3,
    }
    rows.sort(
        key=lambda row: (
            priority_order.get(str(row["review_priority"]), 9),
            row["reference_classification"],
            row["reference_path"],
            row["invalidation_row_id"],
        )
    )
    _validate_quarantine_reference_triage_rows(rows)
    return rows


def summarize_artifact_invalidation_quarantine_reference_triage_rows(
    rows: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    """Summarize quarantine reference triage without clearing any gate."""

    _validate_quarantine_reference_triage_rows(rows)
    return {
        "schema_version": 1,
        "row_count": len(rows),
        "reference_triage_only": True,
        "quarantine_batch_only": True,
        "source_action_batch": "quarantine_non_evidence",
        "reference_classification_counts": _counts(
            str(row.get("reference_classification", "")) for row in rows
        ),
        "review_priority_counts": _counts(
            str(row.get("review_priority", "")) for row in rows
        ),
        "unique_reference_path_count": len(
            {str(row.get("reference_path", "")) for row in rows}
        ),
        "can_mark_complete": False,
        "can_clear_invalidation_gate": False,
        "phase9_promotion_ready": False,
        "publication_ready": False,
        "final_study_ready": False,
        "formal_acceptance_evidence": False,
        "acceptance_ready": False,
        "must_not_be_used_as_closeout_manifest": True,
        "remaining_blockers": [
            "reference triage rows are reviewer-action support only",
            "active claim-text candidates still require reviewer-confirmed removal, replacement, or explicit non-evidence scope",
        ],
    }


def write_artifact_invalidation_quarantine_reference_triage(
    *,
    transfer_rows: Sequence[Mapping[str, str]] | None = None,
    index_rows: Sequence[Mapping[str, str]] | None = None,
    scope_rows: Sequence[Mapping[str, str]] | None = None,
    closeout_rows: Sequence[Mapping[str, str]] | None = None,
    project_root: str | Path = PROJECT_ROOT,
    search_roots: Sequence[str] = DEFAULT_QUARANTINE_CITATION_SEARCH_ROOTS,
    output_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_REFERENCE_TRIAGE,
    manifest_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_REFERENCE_TRIAGE_MANIFEST,
    doc_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_REFERENCE_TRIAGE_DOC,
    source_transfer_packet_manifest: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET_MANIFEST,
) -> dict[str, Any]:
    """Write a non-closing triage audit for quarantine reference hits."""

    rows = build_artifact_invalidation_quarantine_reference_triage_rows(
        transfer_rows=transfer_rows,
        index_rows=index_rows,
        scope_rows=scope_rows,
        closeout_rows=closeout_rows,
        project_root=project_root,
        search_roots=search_roots,
        source_transfer_packet_manifest=source_transfer_packet_manifest,
    )
    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    csv_text = _dict_csv_text(
        rows,
        ARTIFACT_INVALIDATION_QUARANTINE_REFERENCE_TRIAGE_FIELDS,
    )
    write_text_if_changed(csv_text, output)
    csv_sha256 = _sha256_file(output)

    summary = summarize_artifact_invalidation_quarantine_reference_triage_rows(rows)
    source_summary = _quarantine_transfer_manifest_lineage(
        Path(source_transfer_packet_manifest)
    )
    summary.update(
        {
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
            "csv_sha256": csv_sha256,
            **source_summary,
            "outputs": {
                "csv": _display_path(output),
                "manifest": _display_path(manifest),
                "doc": _display_path(doc),
            },
        }
    )
    preserve_generated_at_when_unchanged(summary, manifest)
    write_json_manifest_if_changed(summary, manifest, sort_keys=True)
    write_text_if_changed(
        build_artifact_invalidation_quarantine_reference_triage_markdown(
            summary,
            rows,
        ),
        doc,
    )
    return summary


def build_artifact_invalidation_quarantine_claim_reference_remediation_rows(
    *,
    triage_rows: Sequence[Mapping[str, str]] | None = None,
    transfer_rows: Sequence[Mapping[str, str]] | None = None,
    index_rows: Sequence[Mapping[str, str]] | None = None,
    scope_rows: Sequence[Mapping[str, str]] | None = None,
    closeout_rows: Sequence[Mapping[str, str]] | None = None,
    project_root: str | Path = PROJECT_ROOT,
    search_roots: Sequence[str] = DEFAULT_QUARANTINE_CITATION_SEARCH_ROOTS,
    source_reference_triage_manifest: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_REFERENCE_TRIAGE_MANIFEST,
    source_scope_audit_manifest: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_AUDIT_MANIFEST,
) -> list[dict[str, str]]:
    """Return line-level non-closing remediation rows for review-first references."""

    triage = (
        [dict(row) for row in triage_rows]
        if triage_rows is not None
        else build_artifact_invalidation_quarantine_reference_triage_rows(
            transfer_rows=transfer_rows,
            index_rows=index_rows,
            scope_rows=scope_rows,
            closeout_rows=closeout_rows,
            project_root=project_root,
            search_roots=search_roots,
        )
    )
    _validate_quarantine_reference_triage_rows(triage)
    findings = (
        [dict(row) for row in scope_rows]
        if scope_rows is not None
        else build_artifact_invalidation_quarantine_scope_rows(
            closeout_rows=closeout_rows,
            project_root=project_root,
            search_roots=search_roots,
        )
    )
    _validate_quarantine_scope_rows(findings)
    reference_hits_by_key: dict[tuple[str, str], list[Mapping[str, str]]] = {}
    for row in findings:
        if row["finding_type"] != "reference_hit" or row["status"] != "referenced":
            continue
        key = (str(row["invalidation_row_id"]), str(row["matched_path"]))
        reference_hits_by_key.setdefault(key, []).append(row)

    triage_lineage = _quarantine_reference_triage_manifest_lineage(
        Path(source_reference_triage_manifest)
    )
    scope_lineage = _quarantine_scope_manifest_lineage(Path(source_scope_audit_manifest))
    rows: list[dict[str, str]] = []
    for triage_row in triage:
        if str(triage_row.get("review_priority", "")) != "review_first":
            continue
        key = (
            str(triage_row["invalidation_row_id"]),
            str(triage_row["reference_path"]),
        )
        hits = sorted(
            reference_hits_by_key.get(key, []),
            key=lambda row: (
                _scope_detail_line_number(str(row.get("matched_detail", ""))),
                str(row.get("matched_detail", "")),
            ),
        )
        if not hits:
            rows.append(
                _claim_reference_remediation_row(
                    triage_row,
                    scope_row=None,
                    triage_lineage=triage_lineage,
                    scope_lineage=scope_lineage,
                )
            )
            continue
        for hit in hits:
            rows.append(
                _claim_reference_remediation_row(
                    triage_row,
                    scope_row=hit,
                    triage_lineage=triage_lineage,
                    scope_lineage=scope_lineage,
                )
            )
    rows.sort(
        key=lambda row: (
            row["reference_path"],
            _safe_int(row["line_number"], default=10**9),
            row["invalidation_row_id"],
            row["matched_pattern"],
        )
    )
    _validate_quarantine_claim_reference_remediation_rows(rows)
    return rows


def summarize_artifact_invalidation_quarantine_claim_reference_remediation_rows(
    rows: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    """Summarize line-level claim-reference remediation support without closing gates."""

    _validate_quarantine_claim_reference_remediation_rows(rows)
    line_hit_rows = [
        row for row in rows if str(row.get("line_scan_status", "")) == "line_hit"
    ]
    affected_refs = {str(row.get("reference_path", "")) for row in rows}
    affected_row_ids = {str(row.get("invalidation_row_id", "")) for row in rows}
    return {
        "schema_version": 1,
        "row_count": len(rows),
        "claim_reference_remediation_only": True,
        "quarantine_batch_only": True,
        "source_action_batch": "quarantine_non_evidence",
        "review_priority_scope": "review_first",
        "unique_reference_path_count": len(affected_refs),
        "impacted_invalidation_row_count": len(affected_row_ids),
        "line_hit_row_count": len(line_hit_rows),
        "line_not_found_row_count": len(rows) - len(line_hit_rows),
        "reference_classification_counts": _counts(
            str(row.get("reference_classification", "")) for row in rows
        ),
        "line_scan_status_counts": _counts(
            str(row.get("line_scan_status", "")) for row in rows
        ),
        "can_mark_complete": False,
        "can_clear_invalidation_gate": False,
        "phase9_promotion_ready": False,
        "publication_ready": False,
        "final_study_ready": False,
        "formal_acceptance_evidence": False,
        "acceptance_ready": False,
        "must_not_be_used_as_closeout_manifest": True,
        "remaining_blockers": [
            "line-level remediation rows are reviewer-action support only",
            "claim-text edits, citation-removal audit, targeted tests, main closeout copy, and non-acceptance reviewer signoff remain required",
        ],
    }


def write_artifact_invalidation_quarantine_claim_reference_remediation_packet(
    *,
    triage_rows: Sequence[Mapping[str, str]] | None = None,
    transfer_rows: Sequence[Mapping[str, str]] | None = None,
    index_rows: Sequence[Mapping[str, str]] | None = None,
    scope_rows: Sequence[Mapping[str, str]] | None = None,
    closeout_rows: Sequence[Mapping[str, str]] | None = None,
    project_root: str | Path = PROJECT_ROOT,
    search_roots: Sequence[str] = DEFAULT_QUARANTINE_CITATION_SEARCH_ROOTS,
    output_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLAIM_REFERENCE_REMEDIATION,
    manifest_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLAIM_REFERENCE_REMEDIATION_MANIFEST,
    doc_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLAIM_REFERENCE_REMEDIATION_DOC,
    source_reference_triage_manifest: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_REFERENCE_TRIAGE_MANIFEST,
    source_scope_audit_manifest: str | Path = DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_AUDIT_MANIFEST,
) -> dict[str, Any]:
    """Write a non-closing line-level remediation packet for review-first references."""

    rows = build_artifact_invalidation_quarantine_claim_reference_remediation_rows(
        triage_rows=triage_rows,
        transfer_rows=transfer_rows,
        index_rows=index_rows,
        scope_rows=scope_rows,
        closeout_rows=closeout_rows,
        project_root=project_root,
        search_roots=search_roots,
        source_reference_triage_manifest=source_reference_triage_manifest,
        source_scope_audit_manifest=source_scope_audit_manifest,
    )
    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    csv_text = _dict_csv_text(
        rows,
        ARTIFACT_INVALIDATION_QUARANTINE_CLAIM_REFERENCE_REMEDIATION_FIELDS,
    )
    write_text_if_changed(csv_text, output)
    csv_sha256 = _sha256_file(output)

    summary = summarize_artifact_invalidation_quarantine_claim_reference_remediation_rows(
        rows
    )
    triage_lineage = _quarantine_reference_triage_manifest_lineage(
        Path(source_reference_triage_manifest)
    )
    scope_lineage = _quarantine_scope_manifest_lineage(Path(source_scope_audit_manifest))
    summary.update(
        {
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
            "csv_sha256": csv_sha256,
            **triage_lineage,
            **scope_lineage,
            "outputs": {
                "csv": _display_path(output),
                "manifest": _display_path(manifest),
                "doc": _display_path(doc),
            },
        }
    )
    preserve_generated_at_when_unchanged(summary, manifest)
    write_json_manifest_if_changed(summary, manifest, sort_keys=True)
    write_text_if_changed(
        build_artifact_invalidation_quarantine_claim_reference_remediation_markdown(
            summary,
            rows,
        ),
        doc,
    )
    return summary


def summarize_artifact_invalidation_rows(rows: Sequence[Mapping[str, str]]) -> dict[str, Any]:
    """Summarize row status without granting readiness."""

    upstream_groups = sorted({str(row.get("upstream_change_group", "")) for row in rows})
    downstream_groups = sorted({str(row.get("stale_downstream_group", "")) for row in rows})
    blocking_rows = [
        row
        for row in rows
        if str(row.get("disposition_status", "")) in BLOCKING_DISPOSITION_STATUSES
    ]
    missing_upstream = sorted(UPSTREAM_GROUPS - set(upstream_groups))
    missing_phase9 = sorted(REQUIRED_PHASE9_GROUPS - set(downstream_groups))
    blockers = [
        "{upstream}->{downstream}: {status}".format(
            upstream=row.get("upstream_change_group", ""),
            downstream=row.get("stale_downstream_group", ""),
            status=row.get("disposition_status", ""),
        )
        for row in blocking_rows[:60]
    ]
    if len(blocking_rows) > 60:
        blockers.append(f"{len(blocking_rows) - 60} additional stale rows need disposition")
    if missing_upstream:
        blockers.append("missing upstream group coverage: " + ", ".join(missing_upstream))
    if missing_phase9:
        blockers.append("missing Phase 9 downstream group coverage: " + ", ".join(missing_phase9))

    cleared_rows = len(rows) - len(blocking_rows)
    return {
        "row_count": len(rows),
        "blocking_row_count": len(blocking_rows),
        "cleared_row_count": cleared_rows,
        "upstream_groups_covered": upstream_groups,
        "stale_downstream_groups_covered": downstream_groups,
        "required_upstream_groups_covered": not missing_upstream,
        "required_phase9_downstream_groups_covered": not missing_phase9,
        "disposition_status_counts": _counts(row.get("disposition_status", "") for row in rows),
        "claim_boundary_effect_counts": _counts(
            row.get("claim_boundary_effect", "") for row in rows
        ),
        "phase9_promotion_effect_counts": _counts(
            row.get("phase9_promotion_effect", "") for row in rows
        ),
        "remaining_blockers": blockers,
    }


def summarize_artifact_invalidation_closeout_rows(
    rows: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    """Summarize reviewer closeout rows without granting readiness."""

    _validate_closeout_rows(rows)
    closed_rows = [row for row in rows if _closeout_row_is_closed(row)]
    pending_rows = len(rows) - len(closed_rows)
    blockers = [
        "{row_key}: {status}/{audit}/{test}/{signoff}/{reviewer}".format(
            row_key=row.get("invalidation_row_id", ""),
            status=row.get("actual_disposition", ""),
            audit=row.get("audit_result", ""),
            test=row.get("targeted_test_result", ""),
            signoff=row.get("reviewer_signoff_status", ""),
            reviewer=_closeout_reviewer_identity_status(row),
        )
        for row in rows
        if not _closeout_row_is_closed(row)
    ][:60]
    if pending_rows > 60:
        blockers.append(f"{pending_rows - 60} additional closeout rows need review")

    return {
        "row_count": len(rows),
        "closed_row_count": len(closed_rows),
        "pending_or_invalid_row_count": pending_rows,
        "actual_disposition_counts": _counts(
            row.get("actual_disposition", "") for row in rows
        ),
        "closeout_status_counts": _counts(
            row.get("closeout_status", "") for row in rows
        ),
        "rerun_result_counts": _counts(
            row.get("rerun_result", "") for row in rows
        ),
        "audit_result_counts": _counts(
            row.get("audit_result", "") for row in rows
        ),
        "targeted_test_result_counts": _counts(
            row.get("targeted_test_result", "") for row in rows
        ),
        "reviewer_signoff_status_counts": _counts(
            row.get("reviewer_signoff_status", "") for row in rows
        ),
        "reviewer_identity_status_counts": _counts(
            _closeout_reviewer_identity_status(row) for row in rows
        ),
        "claim_boundary_effect_counts": _counts(
            row.get("claim_boundary_effect", "") for row in rows
        ),
        "phase9_promotion_effect_counts": _counts(
            row.get("phase9_promotion_effect", "") for row in rows
        ),
        "remaining_blockers": blockers,
    }


def summarize_artifact_invalidation_closeout_action_rows(
    rows: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    """Summarize closeout actions without closing any gate."""

    _validate_action_rows(rows)
    return {
        "row_count": len(rows),
        "action_batch_counts": _counts(row.get("action_batch", "") for row in rows),
        "dependency_stage_counts": _counts(row.get("dependency_stage", "") for row in rows),
        "recommended_disposition_counts": _counts(
            row.get("recommended_disposition", "") for row in rows
        ),
        "blocks_phase9_row_count": sum(
            1 for row in rows if str(row.get("blocks_phase9_until_closed", "")).lower() == "true"
        ),
        "reviewer_signoff_required_row_count": sum(
            1
            for row in rows
            if str(row.get("can_close_without_reviewer_signoff", "")).lower() == "false"
        ),
        "remaining_blockers": [
            "complete action queue rows in dependency order; this queue is not closeout evidence"
        ],
    }


def summarize_artifact_invalidation_action_batch_inspection_rows(
    rows: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    """Summarize action-batch inspection rows without granting readiness."""

    _validate_action_batch_inspection_rows(rows)
    can_clear_rows = [
        row
        for row in rows
        if str(row.get("can_clear_invalidation_gate", "")).lower() == "true"
    ]
    pending_rows = len(rows) - len(can_clear_rows)
    regeneration_candidates = [
        row for row in rows if row.get("recommended_disposition") == "regenerated"
    ]
    exclusion_candidates = [
        row
        for row in rows
        if str(row.get("recommended_disposition", "")).startswith(
            "marked_non_evidence"
        )
    ]
    action_queue_blocking_rows = [
        row
        for row in rows
        if str(row.get("blocks_phase9_until_closed", "")).lower() == "true"
    ]
    blockers = [
        "{row_key}: {classification}; missing={missing}".format(
            row_key=row.get("invalidation_row_id", ""),
            classification=row.get("inspection_classification", ""),
            missing=row.get("missing_evidence_json", "[]"),
        )
        for row in rows
        if str(row.get("can_clear_invalidation_gate", "")).lower() != "true"
    ][:60]
    if pending_rows > 60:
        blockers.append(
            f"{pending_rows - 60} additional action-batch rows remain pending"
        )
    return {
        "row_count": len(rows),
        "action_batch_counts": _counts(row.get("action_batch", "") for row in rows),
        "dependency_stage_counts": _counts(
            row.get("dependency_stage", "") for row in rows
        ),
        "recommended_disposition_counts": _counts(
            row.get("recommended_disposition", "") for row in rows
        ),
        "actual_disposition_counts": _counts(
            row.get("actual_disposition", "") for row in rows
        ),
        "inspection_classification_counts": _counts(
            row.get("inspection_classification", "") for row in rows
        ),
        "source_manifest_status_counts": _counts(
            row.get("source_manifest_status", "") for row in rows
        ),
        "compact_closeout_eligibility_status_counts": _counts(
            row.get("compact_closeout_eligibility_status", "") for row in rows
        ),
        "action_batch_rollup": build_artifact_invalidation_action_batch_rollup(rows),
        "regeneration_candidate_count": len(regeneration_candidates),
        "exclusion_or_non_evidence_candidate_count": len(exclusion_candidates),
        "evidence_backed_closeout_row_count": len(can_clear_rows),
        "pending_or_blocked_row_count": pending_rows,
        "action_queue_blocks_phase9_row_count": len(action_queue_blocking_rows),
        "reviewer_signoff_required_row_count": sum(
            1
            for row in rows
            if str(row.get("can_close_without_reviewer_signoff", "")).lower()
            == "false"
        ),
        "can_clear_invalidation_gate_count": len(can_clear_rows),
        "phase9_promotion_ready": False,
        "can_mark_complete": False,
        "publication_ready": False,
        "final_study_ready": False,
        "formal_acceptance_evidence": False,
        "must_not_be_used_as_closeout_manifest": True,
        "remaining_blockers": blockers
        or [
            "main closeout manifest, formal acceptance, and publication readiness remain separate gates"
        ],
    }


def build_artifact_invalidation_action_batch_rollup(
    rows: Sequence[Mapping[str, str]],
) -> list[dict[str, Any]]:
    """Return batch-level closeout triage without changing row status."""

    _validate_action_batch_inspection_rows(rows)
    grouped: dict[str, list[Mapping[str, str]]] = {}
    for row in rows:
        grouped.setdefault(str(row.get("action_batch", "")), []).append(row)

    rollup: list[dict[str, Any]] = []
    for batch, batch_rows in grouped.items():
        can_clear_count = sum(
            1
            for row in batch_rows
            if str(row.get("can_clear_invalidation_gate", "")).lower() == "true"
        )
        pending_count = len(batch_rows) - can_clear_count
        missing_evidence = sorted(
            {
                str(item)
                for row in batch_rows
                for item in json.loads(str(row.get("missing_evidence_json", "[]")))
            }
        )
        classifications = {
            str(row.get("inspection_classification", "")) for row in batch_rows
        }
        prerequisite_batches = sorted(
            {
                str(row.get("blocking_prerequisite_batch", ""))
                for row in batch_rows
                if str(row.get("blocking_prerequisite_batch", ""))
            }
        )
        allowed_operations = sorted(
            {
                str(row.get("allowed_next_operation", ""))
                for row in batch_rows
                if str(row.get("allowed_next_operation", ""))
            }
        )
        rollup.append(
            {
                "action_batch": batch,
                "first_action_order": min(
                    int(str(row.get("action_order", "0"))) for row in batch_rows
                ),
                "row_count": len(batch_rows),
                "dependency_stages": sorted(
                    {str(row.get("dependency_stage", "")) for row in batch_rows}
                ),
                "recommended_disposition_counts": _counts(
                    row.get("recommended_disposition", "") for row in batch_rows
                ),
                "inspection_classification_counts": _counts(
                    row.get("inspection_classification", "") for row in batch_rows
                ),
                "can_clear_invalidation_gate_count": can_clear_count,
                "pending_or_blocked_row_count": pending_count,
                "reviewer_signoff_required_row_count": sum(
                    1
                    for row in batch_rows
                    if str(row.get("can_close_without_reviewer_signoff", "")).lower()
                    == "false"
                ),
                "missing_evidence": missing_evidence,
                "next_closeout_focus": _action_batch_next_closeout_focus(
                    classifications
                ),
                "blocking_prerequisite_batches": prerequisite_batches,
                "allowed_next_operations": allowed_operations,
                "can_clear_invalidation_gate": False,
                "phase9_promotion_ready": False,
            }
        )
    return sorted(
        rollup,
        key=lambda item: (int(item["first_action_order"]), str(item["action_batch"])),
    )


def summarize_artifact_invalidation_closeout_readiness_rows(
    rows: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    """Summarize closeout evidence gaps without closing the invalidation gate."""

    _validate_closeout_readiness_rows(rows)
    ready_rows = [
        row for row in rows if str(row.get("can_clear_invalidation_gate", "")).lower() == "true"
    ]
    compact_blocked_rows = [
        row
        for row in rows
        if str(row.get("compact_closeout_eligibility_status", "")).startswith("blocked")
    ]
    missing_rows = [
        row
        for row in rows
        if json.loads(str(row.get("missing_evidence_json", "[]")))
    ]
    blockers = [
        "{row_key}: {missing}; compact={compact}".format(
            row_key=row.get("invalidation_row_id", ""),
            missing=row.get("missing_evidence_json", "[]"),
            compact=row.get("compact_closeout_eligibility_status", ""),
        )
        for row in rows
        if str(row.get("can_clear_invalidation_gate", "")).lower() != "true"
    ][:60]
    if len(rows) - len(ready_rows) > 60:
        blockers.append(f"{len(rows) - len(ready_rows) - 60} additional closeout rows need evidence")
    blockers.append(
        "closeout readiness audit is support-only and cannot be used as closeout manifest"
    )
    return {
        "row_count": len(rows),
        "closeout_ready_row_count": len(ready_rows),
        "pending_or_blocked_row_count": len(rows) - len(ready_rows),
        "missing_evidence_row_count": len(missing_rows),
        "compact_source_blocked_count": len(compact_blocked_rows),
        "actual_disposition_counts": _counts(row.get("actual_disposition", "") for row in rows),
        "closeout_status_counts": _counts(row.get("closeout_status", "") for row in rows),
        "source_manifest_status_counts": _counts(
            row.get("source_manifest_status", "") for row in rows
        ),
        "compact_closeout_eligibility_status_counts": _counts(
            row.get("compact_closeout_eligibility_status", "") for row in rows
        ),
        "reviewer_signoff_status_counts": _counts(
            row.get("reviewer_signoff_status", "") for row in rows
        ),
        "can_clear_invalidation_gate_count": len(ready_rows),
        "phase9_promotion_ready": False,
        "can_mark_complete": False,
        "publication_ready": False,
        "final_study_ready": False,
        "formal_acceptance_evidence": False,
        "must_not_be_used_as_closeout_manifest": True,
        "remaining_blockers": blockers,
    }


def summarize_artifact_invalidation_quarantine_scope_rows(
    rows: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    """Summarize quarantine scope rows without granting closeout."""

    _validate_quarantine_scope_rows(rows)
    expected_ids = _expected_quarantine_row_ids()
    covered_ids = {str(row.get("invalidation_row_id", "")) for row in rows}
    missing_ids = sorted(expected_ids - covered_ids)
    scan_error_count = sum(1 for row in rows if row["finding_type"] == "scan_error")
    reference_hit_count = sum(1 for row in rows if row["finding_type"] == "reference_hit")
    unresolved_current_reference_count = sum(
        1
        for row in rows
        if row["finding_type"] == "reference_hit"
        and not _is_archival_reference_path(str(row["matched_path"]))
    )
    stale_candidate_count = sum(
        1 for row in rows if row["finding_type"] == "stale_artifact_candidate"
    )
    zip_candidate_count = sum(1 for row in rows if row["finding_type"] == "zip_candidate")
    searched_scope_complete = not scan_error_count and not missing_ids
    return {
        "row_count": len(rows),
        "quarantine_batch_only": True,
        "expected_quarantine_row_count": len(expected_ids),
        "covered_quarantine_row_count": len(covered_ids & expected_ids),
        "missing_quarantine_row_ids": missing_ids,
        "scope_scan_error_count": scan_error_count,
        "stale_candidate_count": stale_candidate_count,
        "zip_candidate_count": zip_candidate_count,
        "missing_expected_count": sum(
            1 for row in rows if row["finding_type"] == "missing_expected"
        ),
        "reference_hit_count": reference_hit_count,
        "unresolved_current_reference_count": unresolved_current_reference_count,
        "finding_type_counts": _counts(row["finding_type"] for row in rows),
        "status_counts": _counts(row["status"] for row in rows),
        "searched_scope_complete": searched_scope_complete,
        "can_clear_invalidation_gate": False,
        "can_mark_complete": False,
        "phase9_promotion_ready": False,
        "publication_ready": False,
        "final_study_ready": False,
        "formal_acceptance_evidence": False,
        "acceptance_ready": False,
        "must_not_be_used_as_closeout_manifest": True,
        "remaining_blockers": [
            "copy reviewed scope evidence into main closeout record with non-acceptance reviewer signoff"
        ],
    }


def summarize_artifact_invalidation_quarantine_non_evidence_index_rows(
    rows: Sequence[Mapping[str, str]],
    *,
    source_scope_summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Summarize the deduped quarantine index without granting closeout."""

    _validate_quarantine_non_evidence_index_rows(rows)
    covered_ids: set[str] = set()
    for row in rows:
        covered_ids.update(
            str(item)
            for item in json.loads(str(row.get("invalidation_row_ids_json", "[]")))
        )
    expected_ids = _expected_quarantine_row_ids()
    missing_ids = sorted(expected_ids - covered_ids)
    source_candidate_count = (
        int(source_scope_summary.get("stale_candidate_count", 0))
        + int(source_scope_summary.get("zip_candidate_count", 0))
        if source_scope_summary is not None
        else sum(int(row.get("source_finding_count", "0")) for row in rows)
    )
    return {
        "row_count": len(rows),
        "quarantine_batch_only": True,
        "indexed_artifact_count": len(rows),
        "indexed_full_output_count": sum(
            1 for row in rows if row["stale_downstream_group"] == "full_outputs"
        ),
        "indexed_review_package_count": sum(
            1 for row in rows if row["stale_downstream_group"] == "review_packages"
        ),
        "indexed_zip_candidate_count": sum(
            1 for row in rows if row["candidate_type"] == "zip_candidate"
        ),
        "indexed_stale_artifact_candidate_count": sum(
            1 for row in rows if row["candidate_type"] == "stale_artifact_candidate"
        ),
        "source_candidate_finding_count": source_candidate_count,
        "deduped_duplicate_count": max(source_candidate_count - len(rows), 0),
        "expected_quarantine_row_count": len(expected_ids),
        "covered_quarantine_row_count": len(covered_ids & expected_ids),
        "missing_quarantine_row_ids": missing_ids,
        "source_scope_reference_hit_count": (
            int(source_scope_summary.get("reference_hit_count", 0))
            if source_scope_summary is not None
            else 0
        ),
        "source_scope_current_reference_hit_count": (
            int(source_scope_summary.get("unresolved_current_reference_count", 0))
            if source_scope_summary is not None
            else 0
        ),
        "source_scope_scan_error_count": (
            int(source_scope_summary.get("scope_scan_error_count", 0))
            if source_scope_summary is not None
            else 0
        ),
        "can_clear_invalidation_gate": False,
        "can_mark_complete": False,
        "phase9_promotion_ready": False,
        "publication_ready": False,
        "final_study_ready": False,
        "formal_acceptance_evidence": False,
        "acceptance_ready": False,
        "must_not_be_used_as_closeout_manifest": True,
        "remaining_blockers": [
            "review indexed stale paths, copy confirmed entries into the main closeout record, and obtain non-acceptance reviewer signoff"
        ],
    }


def summarize_artifact_invalidation_matrix(
    manifest_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_MANIFEST,
) -> dict[str, Any]:
    """Load a compact invalidation summary for preflight checks."""

    path = Path(manifest_path)
    if not path.exists():
        return {
            "manifest_present": False,
            "path": _display_path(path),
            "row_count": 0,
            "blocking_row_count": 1,
            "phase9_promotion_ready": False,
            "can_mark_complete": False,
            "remaining_blockers": ["run scripts/write_artifact_invalidation_matrix.py"],
        }
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return {
        "manifest_present": True,
        "path": _display_path(path),
        "row_count": int(value.get("row_count", 0)),
        "blocking_row_count": int(value.get("blocking_row_count", 0)),
        "required_upstream_groups_covered": bool(value.get("required_upstream_groups_covered", False)),
        "required_phase9_downstream_groups_covered": bool(
            value.get("required_phase9_downstream_groups_covered", False)
        ),
        "phase9_promotion_ready": bool(value.get("phase9_promotion_ready", False)),
        "can_mark_complete": bool(value.get("can_mark_complete", False)),
        "remaining_blockers": list(value.get("remaining_blockers", [])),
    }


def summarize_artifact_invalidation_closeout_manifest(
    manifest_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_MANIFEST,
) -> dict[str, Any]:
    """Load closeout summary for fail-closed Phase 9 checks."""

    path = Path(manifest_path)
    if not path.exists():
        return {
            "manifest_present": False,
            "path": _display_path(path),
            "row_count": 0,
            "pending_or_invalid_row_count": 1,
            "phase9_promotion_ready": False,
            "can_mark_complete": False,
            "publication_ready": False,
            "final_study_ready": False,
            "formal_acceptance_evidence": False,
            "remaining_blockers": [
                "run scripts/write_artifact_invalidation_matrix.py --write-closeout-template"
            ],
        }
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    csv_verification = _closeout_manifest_csv_verification(value)
    row_summary = csv_verification.get("row_summary", {})
    support_only = _closeout_manifest_is_support_only(value, csv_verification)
    support_blockers = (
        ["support manifest cannot be used as artifact invalidation closeout manifest"]
        if support_only
        else []
    )
    pending_or_invalid = int(
        row_summary.get(
            "pending_or_invalid_row_count",
            value.get("pending_or_invalid_row_count", 0),
        )
    )
    if support_only:
        pending_or_invalid = max(1, pending_or_invalid)
    return {
        "manifest_present": True,
        "path": _display_path(path),
        "row_count": int(row_summary.get("row_count", value.get("row_count", 0))),
        "closed_row_count": int(
            row_summary.get("closed_row_count", value.get("closed_row_count", 0))
        ),
        "pending_or_invalid_row_count": int(
            pending_or_invalid
        ),
        "closeout_csv_path": csv_verification.get("csv_path", ""),
        "closeout_csv_verification_status": csv_verification.get("status", ""),
        "closeout_csv_summary_matches_manifest": bool(
            csv_verification.get("summary_matches_manifest", False)
        ),
        "phase9_promotion_ready": bool(value.get("phase9_promotion_ready", False)),
        "can_mark_complete": bool(value.get("can_mark_complete", False)),
        "publication_ready": bool(value.get("publication_ready", False)),
        "final_study_ready": bool(value.get("final_study_ready", False)),
        "formal_acceptance_evidence": bool(value.get("formal_acceptance_evidence", False)),
        "must_not_be_used_as_closeout_manifest": bool(
            support_only or value.get("must_not_be_used_as_closeout_manifest", False)
        ),
        "remaining_blockers": support_blockers + list(value.get("remaining_blockers", [])),
    }


def _closeout_manifest_is_support_only(
    value: Mapping[str, Any],
    csv_verification: Mapping[str, Any],
) -> bool:
    support_markers = {
        "copy_audit_only",
        "draft_overlay_only",
        "prefill_only",
        "prefill_gap_audit_only",
        "quarantine_batch_only",
        "must_not_replace_main_closeout_record",
        "closeout_ready_row_count",
        "can_clear_invalidation_gate_count",
    }
    if any(marker in value for marker in support_markers):
        return True
    support_basenames = {
        "artifact_invalidation_closeout_readiness_audit.csv",
        "artifact_invalidation_quarantine_closeout_prefill.csv",
        "artifact_invalidation_quarantine_closeout_prefill_gap_audit.csv",
        "artifact_invalidation_quarantine_main_closeout_copy_audit.csv",
        "artifact_invalidation_quarantine_main_closeout_draft_overlay.csv",
        "artifact_invalidation_quarantine_closeout_template.csv",
    }
    csv_path = str(csv_verification.get("csv_path", ""))
    if csv_path and Path(csv_path).name in support_basenames:
        return True
    outputs = value.get("outputs", {})
    if isinstance(outputs, Mapping):
        output_csv = str(outputs.get("csv", ""))
        if output_csv and Path(output_csv).name in support_basenames:
            return True
    return False


def summarize_artifact_invalidation_action_batch_inspection_manifest(
    manifest_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_ACTION_BATCH_INSPECTION_MANIFEST,
) -> dict[str, Any]:
    """Load action-batch inspection summary for plan-audit exposure."""

    path = Path(manifest_path)
    if not path.exists():
        return {
            "manifest_present": False,
            "path": _display_path(path),
            "row_count": 0,
            "action_queue_blocks_phase9_row_count": 1,
            "pending_or_blocked_row_count": 1,
            "can_mark_complete": False,
            "can_clear_invalidation_gate": False,
            "phase9_promotion_ready": False,
            "publication_ready": False,
            "final_study_ready": False,
            "formal_acceptance_evidence": False,
            "must_not_be_used_as_closeout_manifest": True,
            "remaining_blockers": [
                "run scripts/write_artifact_invalidation_matrix.py --write-action-batch-inspection"
            ],
        }
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return {
        "manifest_present": True,
        "path": _display_path(path),
        "row_count": int(value.get("row_count", 0)),
        "action_batch_counts": dict(value.get("action_batch_counts", {})),
        "dependency_stage_counts": dict(value.get("dependency_stage_counts", {})),
        "recommended_disposition_counts": dict(
            value.get("recommended_disposition_counts", {})
        ),
        "inspection_classification_counts": dict(
            value.get("inspection_classification_counts", {})
        ),
        "regeneration_candidate_count": int(
            value.get("regeneration_candidate_count", 0)
        ),
        "exclusion_or_non_evidence_candidate_count": int(
            value.get("exclusion_or_non_evidence_candidate_count", 0)
        ),
        "evidence_backed_closeout_row_count": int(
            value.get("evidence_backed_closeout_row_count", 0)
        ),
        "pending_or_blocked_row_count": int(
            value.get("pending_or_blocked_row_count", 0)
        ),
        "action_queue_blocks_phase9_row_count": int(
            value.get("action_queue_blocks_phase9_row_count", 0)
        ),
        "reviewer_signoff_required_row_count": int(
            value.get("reviewer_signoff_required_row_count", 0)
        ),
        "can_clear_invalidation_gate": bool(
            value.get("can_clear_invalidation_gate", False)
        ),
        "can_mark_complete": bool(value.get("can_mark_complete", False)),
        "phase9_promotion_ready": bool(value.get("phase9_promotion_ready", False)),
        "publication_ready": bool(value.get("publication_ready", False)),
        "final_study_ready": bool(value.get("final_study_ready", False)),
        "formal_acceptance_evidence": bool(
            value.get("formal_acceptance_evidence", False)
        ),
        "must_not_be_used_as_closeout_manifest": bool(
            value.get("must_not_be_used_as_closeout_manifest", True)
        ),
        "remaining_blockers": list(value.get("remaining_blockers", [])),
    }


def artifact_invalidation_blocks_phase9(
    manifest_path: str | Path = DEFAULT_ARTIFACT_INVALIDATION_MANIFEST,
    closeout_manifest_path: str | Path | None = DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_MANIFEST,
) -> tuple[bool, list[str], dict[str, Any]]:
    """Return whether Phase 9 promotion is blocked by unresolved invalidation."""

    summary = summarize_artifact_invalidation_matrix(manifest_path)
    blockers = list(summary.get("remaining_blockers", []))
    if not summary.get("manifest_present", False):
        return True, blockers, summary
    if not summary.get("required_upstream_groups_covered", False):
        blockers.append("artifact invalidation matrix is missing upstream group coverage")
    if not summary.get("required_phase9_downstream_groups_covered", False):
        blockers.append("artifact invalidation matrix is missing Phase 9 downstream group coverage")
    if int(summary.get("blocking_row_count", 0)) > 0:
        blockers.append("artifact invalidation matrix has unresolved stale rows")
    closeout_summary: dict[str, Any] | None = None
    if closeout_manifest_path is not None:
        closeout_summary = summarize_artifact_invalidation_closeout_manifest(
            closeout_manifest_path
        )
        summary["closeout_snapshot"] = closeout_summary
        if not closeout_summary.get("manifest_present", False):
            blockers.append("artifact invalidation closeout manifest is missing")
        if closeout_summary.get("closeout_csv_verification_status") != "verified":
            blockers.append("artifact invalidation closeout CSV could not be verified")
        if closeout_summary.get("closeout_csv_summary_matches_manifest") is False:
            blockers.append(
                "artifact invalidation closeout manifest summary does not match its CSV rows"
            )
        if int(closeout_summary.get("row_count", 0)) < int(summary.get("row_count", 0)):
            blockers.append(
                "artifact invalidation closeout does not cover every matrix row"
            )
        if int(closeout_summary.get("pending_or_invalid_row_count", 0)) > 0:
            blockers.append("artifact invalidation closeout has pending or invalid rows")
        if closeout_summary.get("publication_ready", False):
            blockers.append("artifact invalidation closeout must not set publication_ready=true")
        if closeout_summary.get("final_study_ready", False):
            blockers.append("artifact invalidation closeout must not set final_study_ready=true")
        if closeout_summary.get("formal_acceptance_evidence", False):
            blockers.append(
                "artifact invalidation closeout must not set formal_acceptance_evidence=true"
            )
        if closeout_summary.get("phase9_promotion_ready", False):
            blockers.append(
                "artifact invalidation closeout must not mark phase9_promotion_ready=true"
            )
        if closeout_summary.get("must_not_be_used_as_closeout_manifest", False):
            blockers.append(
                "artifact invalidation non-closeout support manifest cannot be used as closeout manifest"
            )
    if blockers:
        return True, blockers, summary
    if summary.get("phase9_promotion_ready", False):
        return False, blockers, summary
    blockers.append("artifact invalidation manifest does not mark phase9_promotion_ready=true")
    return True, blockers, summary


def build_artifact_invalidation_markdown(
    summary: Mapping[str, Any],
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Render the invalidation matrix as Markdown."""

    lines = [
        "# Artifact Invalidation Matrix",
        "",
        str(summary.get("claim_boundary", ARTIFACT_INVALIDATION_CLAIM_BOUNDARY)),
        "",
        "## Summary",
        "",
        f"- Phase 9 promotion ready: `{str(summary.get('phase9_promotion_ready', False)).lower()}`",
        f"- Can mark complete: `{str(summary.get('can_mark_complete', False)).lower()}`",
        f"- Rows: {summary.get('row_count', 0)}",
        f"- Blocking rows: {summary.get('blocking_row_count', 0)}",
        f"- Required upstream groups covered: `{str(summary.get('required_upstream_groups_covered', False)).lower()}`",
        f"- Required Phase 9 downstream groups covered: `{str(summary.get('required_phase9_downstream_groups_covered', False)).lower()}`",
        "",
        "## Matrix",
        "",
        "| Upstream Group | Stale Downstream Group | Required Disposition | Status | Claim Effect |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {upstream} | {downstream} | {required} | {status} | {effect} |".format(
                upstream=_cell(str(row.get("upstream_change_group", ""))),
                downstream=_cell(str(row.get("stale_downstream_group", ""))),
                required=_cell(str(row.get("required_disposition", ""))),
                status=_cell(str(row.get("disposition_status", ""))),
                effect=_cell(str(row.get("claim_boundary_effect", ""))),
            )
        )
    lines.extend(
        [
            "",
            "## Use",
            "",
            "Before Phase 9, every blocking row must be regenerated, explicitly "
            "excluded, or marked non-evidence and then re-audited. `excluded` or "
            "`non-evidence` dispositions clear claim use only after text, figures, "
            "manifests, and package notes no longer cite the stale artifact.",
            "",
        ]
    )
    return "\n".join(lines)


def build_artifact_invalidation_closeout_markdown(
    summary: Mapping[str, Any],
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Render the closeout template as Markdown."""

    lines = [
        "# Artifact Invalidation Closeout Template",
        "",
        str(summary.get("claim_boundary", ARTIFACT_INVALIDATION_CLAIM_BOUNDARY)),
        "",
        "## Summary",
        "",
        f"- Phase 9 promotion ready: `{str(summary.get('phase9_promotion_ready', False)).lower()}`",
        f"- Can mark complete: `{str(summary.get('can_mark_complete', False)).lower()}`",
        f"- Rows: {summary.get('row_count', 0)}",
        f"- Closed rows: {summary.get('closed_row_count', 0)}",
        f"- Pending or invalid rows: {summary.get('pending_or_invalid_row_count', 0)}",
        f"- Reviewer evidence status counts: `{summary.get('reviewer_identity_status_counts', {})}`",
        "",
        "## Closeout Rows",
        "",
        "| Row Key | Required Disposition | Actual Disposition | Audit Result | Test Result | Reviewer Signoff | Reviewer Evidence | Claim Effect |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {row_key} | {required} | {closeout} | {audit} | {test} | {signoff} | {reviewer} | {effect} |".format(
                row_key=_cell(str(row.get("invalidation_row_id", ""))),
                required=_cell(str(row.get("required_disposition", ""))),
                closeout=_cell(str(row.get("actual_disposition", ""))),
                audit=_cell(str(row.get("audit_result", ""))),
                test=_cell(str(row.get("targeted_test_result", ""))),
                signoff=_cell(str(row.get("reviewer_signoff_status", ""))),
                reviewer=_cell(_closeout_reviewer_identity_status(row)),
                effect=_cell(str(row.get("claim_boundary_effect", ""))),
            )
        )
    lines.extend(
        [
            "",
            "## Use",
            "",
            "This file is a reviewer worksheet. A row should only be treated as "
            "closed after the required disposition is recorded, affected paths "
            "or exclusion scope are listed, rerun or audit evidence is retained, "
            "and a non-acceptance reviewer signoff is recorded. The template "
            "does not grant publication readiness, final-study readiness, formal "
            "acceptance, or operational use.",
            "",
        ]
    )
    return "\n".join(lines)


def build_artifact_invalidation_closeout_action_markdown(
    summary: Mapping[str, Any],
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Render closeout action queue as Markdown."""

    lines = [
        "# Artifact Invalidation Closeout Action Queue",
        "",
        str(summary.get("claim_boundary", ARTIFACT_INVALIDATION_CLAIM_BOUNDARY)),
        "",
        "## Summary",
        "",
        f"- Phase 9 promotion ready: `{str(summary.get('phase9_promotion_ready', False)).lower()}`",
        f"- Can mark complete: `{str(summary.get('can_mark_complete', False)).lower()}`",
        f"- Rows: {summary.get('row_count', 0)}",
        f"- Blocks Phase 9 rows: {summary.get('blocks_phase9_row_count', 0)}",
        f"- Reviewer signoff required rows: {summary.get('reviewer_signoff_required_row_count', 0)}",
        "",
        "## Queue",
        "",
        "| Order | Batch | Stage | Row | Recommended Disposition | Producer/Audit | Test | Reviewer |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {order} | {batch} | {stage} | {row_id} | {disp} | {cmd} | {test} | {reviewer} |".format(
                order=_cell(str(row.get("action_order", ""))),
                batch=_cell(str(row.get("action_batch", ""))),
                stage=_cell(str(row.get("dependency_stage", ""))),
                row_id=_cell(str(row.get("invalidation_row_id", ""))),
                disp=_cell(str(row.get("recommended_disposition", ""))),
                cmd=_cell(str(row.get("producer_or_audit_command", ""))),
                test=_cell(str(row.get("targeted_test_command", ""))),
                reviewer=_cell(str(row.get("reviewer_role", ""))),
            )
        )
    lines.extend(
        [
            "",
            "## Use",
            "",
            "This queue orders pending closeout work only. It does not close any "
            "artifact invalidation row, regenerate artifacts, approve evidence, "
            "or authorize Phase 9. Each row still requires the closeout template "
            "to be completed with affected artifact or exclusion-scope evidence, "
            "rerun/audit/test results, and non-acceptance reviewer signoff.",
            "",
        ]
    )
    return "\n".join(lines)


def build_artifact_invalidation_action_batch_inspection_markdown(
    summary: Mapping[str, Any],
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Render action-batch inspection as Markdown."""

    lines = [
        "# Artifact Invalidation Action-Batch Inspection",
        "",
        str(summary.get("claim_boundary", ARTIFACT_INVALIDATION_CLAIM_BOUNDARY)),
        "",
        "## Summary",
        "",
        f"- Phase 9 promotion ready: `{str(summary.get('phase9_promotion_ready', False)).lower()}`",
        f"- Can clear invalidation gate: `{str(summary.get('can_clear_invalidation_gate', False)).lower()}`",
        f"- Must not be used as closeout manifest: `{str(summary.get('must_not_be_used_as_closeout_manifest', True)).lower()}`",
        f"- Rows: {summary.get('row_count', 0)}",
        f"- Regeneration candidates: {summary.get('regeneration_candidate_count', 0)}",
        f"- Exclusion/non-evidence candidates: {summary.get('exclusion_or_non_evidence_candidate_count', 0)}",
        f"- Evidence-backed closeout rows: {summary.get('evidence_backed_closeout_row_count', 0)}",
        f"- Pending or blocked rows: {summary.get('pending_or_blocked_row_count', 0)}",
        "",
        "## Batch Counts",
        "",
        "| Batch | Count |",
        "| --- | --- |",
    ]
    for batch, count in dict(summary.get("action_batch_counts", {})).items():
        lines.append(f"| {_cell(str(batch))} | {count} |")
    lines.extend(
        [
            "",
            "## Batch Rollup",
            "",
            "| Order | Batch | Rows | Pending | Next Focus | Blocking Prerequisite | Missing Evidence |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in list(summary.get("action_batch_rollup", [])):
        lines.append(
            "| {order} | {batch} | {rows} | {pending} | {focus} | {prereq} | {missing} |".format(
                order=_cell(str(item.get("first_action_order", ""))),
                batch=_cell(str(item.get("action_batch", ""))),
                rows=item.get("row_count", 0),
                pending=item.get("pending_or_blocked_row_count", 0),
                focus=_cell(str(item.get("next_closeout_focus", ""))),
                prereq=_cell(
                    ", ".join(list(item.get("blocking_prerequisite_batches", [])))
                    or "none"
                ),
                missing=_cell(", ".join(list(item.get("missing_evidence", [])))),
            )
        )
    lines.extend(
        [
            "",
            "Batch rollup rows summarize closeout triage only. They do not close "
            "the main invalidation record and must still be copied into reviewed "
            "closeout evidence before any Phase 9 promotion decision.",
        ]
    )
    lines.extend(
        [
            "",
            "## Inspection Rows",
            "",
            "| Order | Batch | Row | Recommended | Actual | Classification | Next Focus | Prerequisite | Minimum Package | Can Clear | Missing Evidence |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(
            "| {order} | {batch} | {row_id} | {recommended} | {actual} | {classification} | {focus} | {prereq} | {package} | {can_clear} | {missing} |".format(
                order=_cell(str(row.get("action_order", ""))),
                batch=_cell(str(row.get("action_batch", ""))),
                row_id=_cell(str(row.get("invalidation_row_id", ""))),
                recommended=_cell(str(row.get("recommended_disposition", ""))),
                actual=_cell(str(row.get("actual_disposition", ""))),
                classification=_cell(str(row.get("inspection_classification", ""))),
                focus=_cell(str(row.get("next_closeout_focus", ""))),
                prereq=_cell(str(row.get("blocking_prerequisite_status", ""))),
                package=_cell(str(row.get("minimum_evidence_package_json", ""))),
                can_clear=_cell(str(row.get("can_clear_invalidation_gate", ""))),
                missing=_cell(str(row.get("missing_evidence_json", ""))),
            )
        )
    lines.extend(
        [
            "",
            "## Use",
            "",
            "This inspection merges the dependency-ordered action queue with the "
            "closeout-readiness gap audit. It identifies which rows are only "
            "regeneration candidates, exclusion/non-evidence candidates, or still "
            "missing closeout evidence. It is not the main closeout manifest, not "
            "artifact regeneration evidence, not reviewer signoff, not publication "
            "readiness, not final-study approval, not formal acceptance, and not "
            "authorization for Phase 9.",
            "",
        ]
    )
    return "\n".join(lines)


def build_artifact_invalidation_closeout_readiness_markdown(
    summary: Mapping[str, Any],
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Render closeout readiness gap audit rows as Markdown."""

    lines = [
        "# Artifact Invalidation Closeout Gap Audit",
        "",
        str(summary.get("claim_boundary", ARTIFACT_INVALIDATION_CLAIM_BOUNDARY)),
        "",
        "## Summary",
        "",
        f"- Phase 9 promotion ready: `{str(summary.get('phase9_promotion_ready', False)).lower()}`",
        f"- Can clear invalidation gate: `{str(summary.get('can_clear_invalidation_gate', False)).lower()}`",
        f"- Must not be used as closeout manifest: `{str(summary.get('must_not_be_used_as_closeout_manifest', True)).lower()}`",
        f"- Rows: {summary.get('row_count', 0)}",
        f"- Closeout eligible rows: {summary.get('closeout_ready_row_count', 0)}",
        f"- Pending or blocked rows: {summary.get('pending_or_blocked_row_count', 0)}",
        f"- Compact source blocked rows: {summary.get('compact_source_blocked_count', 0)}",
        "",
        "## Gap Rows",
        "",
        "| Row Key | Batch | Disposition | Artifact/Scope | Audit | Test | Signoff | Source Manifest | Compact Eligibility | Missing Evidence |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {row_key} | {batch} | {disp} | {artifact} | {audit} | {test} | {signoff} | {manifest} | {compact} | {missing} |".format(
                row_key=_cell(str(row.get("invalidation_row_id", ""))),
                batch=_cell(str(row.get("action_batch", ""))),
                disp=_cell(str(row.get("actual_disposition", ""))),
                artifact=_cell(str(row.get("artifact_or_exclusion_status", ""))),
                audit=_cell(str(row.get("audit_status", ""))),
                test=_cell(str(row.get("targeted_test_status", ""))),
                signoff=_cell(str(row.get("reviewer_signoff_status", ""))),
                manifest=_cell(str(row.get("source_manifest_status", ""))),
                compact=_cell(str(row.get("compact_closeout_eligibility_status", ""))),
                missing=_cell(str(row.get("missing_evidence_json", ""))),
            )
        )
    lines.extend(
        [
            "",
            "## Use",
            "",
            "This audit is a gap finder for the main artifact invalidation "
            "closeout record. It is not the closeout manifest, not reviewer "
            "signoff, not artifact regeneration evidence, not publication "
            "readiness, not final-study approval, not formal acceptance, and "
            "not Phase 9 readiness. Compact-output rows are fail-closed unless "
            "their referenced source manifest proves that the output is not "
            "engineering-only, not an engineering-only bypass, and not still "
            "blocked by upstream invalidation or rail-source decisions.",
            "",
        ]
    )
    return "\n".join(lines)


def build_artifact_invalidation_quarantine_closeout_markdown(
    summary: Mapping[str, Any],
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Render the first-batch quarantine closeout template."""

    lines = [
        "# Artifact Invalidation Quarantine Closeout Template",
        "",
        str(summary.get("claim_boundary", ARTIFACT_INVALIDATION_CLAIM_BOUNDARY)),
        "",
        "## Summary",
        "",
        f"- Source action batch: `{summary.get('source_action_batch', '')}`",
        f"- Phase 9 promotion ready: `{str(summary.get('phase9_promotion_ready', False)).lower()}`",
        f"- Can mark complete: `{str(summary.get('can_mark_complete', False)).lower()}`",
        f"- Rows: {summary.get('row_count', 0)}",
        f"- Closed rows: {summary.get('closed_row_count', 0)}",
        f"- Pending or invalid rows: {summary.get('pending_or_invalid_row_count', 0)}",
        f"- CSV SHA256: `{summary.get('csv_sha256', '')}`",
        "",
        "## Quarantine Rows",
        "",
        "| Row Key | Required Disposition | Actual Disposition | Exclusion Scope | Reviewer Signoff | Claim Effect |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {row_key} | {required} | {actual} | {scope} | {signoff} | {effect} |".format(
                row_key=_cell(str(row.get("invalidation_row_id", ""))),
                required=_cell(str(row.get("required_disposition", ""))),
                actual=_cell(str(row.get("actual_disposition", ""))),
                scope=_cell(str(row.get("exclusion_scope", ""))),
                signoff=_cell(str(row.get("reviewer_signoff_status", ""))),
                effect=_cell(str(row.get("claim_boundary_effect", ""))),
            )
        )
    lines.extend(
        [
            "",
            "## Use",
            "",
            "This file filters the immediate `quarantine_non_evidence` batch from "
            "the closeout action queue. It is a reviewer input template only. It "
            "does not close rows, does not prove citation removal, does not "
            "approve evidence, and does not authorize Phase 9. Each row remains "
            "pending until a reviewer records the stale path list or exclusion "
            "scope, audit/test evidence, claim-boundary review result, and "
            "non-acceptance signoff in the main closeout record.",
            "",
        ]
    )
    return "\n".join(lines)


def build_artifact_invalidation_quarantine_scope_markdown(
    summary: Mapping[str, Any],
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Render quarantine scope/citation audit support as Markdown."""

    lines = [
        "# Artifact Invalidation Quarantine Scope Audit",
        "",
        str(summary.get("claim_boundary", ARTIFACT_INVALIDATION_CLAIM_BOUNDARY)),
        "",
        "## Summary",
        "",
        f"- Source action batch: `{summary.get('source_action_batch', '')}`",
        f"- Phase 9 promotion ready: `{str(summary.get('phase9_promotion_ready', False)).lower()}`",
        f"- Can clear invalidation gate: `{str(summary.get('can_clear_invalidation_gate', False)).lower()}`",
        f"- Finding rows: {summary.get('row_count', 0)}",
        f"- Expected quarantine rows: {summary.get('expected_quarantine_row_count', 0)}",
        f"- Covered quarantine rows: {summary.get('covered_quarantine_row_count', 0)}",
        f"- Stale candidates: {summary.get('stale_candidate_count', 0)}",
        f"- ZIP candidates: {summary.get('zip_candidate_count', 0)}",
        f"- Reference hits: {summary.get('reference_hit_count', 0)}",
        f"- Current reference hits: {summary.get('unresolved_current_reference_count', 0)}",
        f"- Scan errors: {summary.get('scope_scan_error_count', 0)}",
        f"- Must not be used as closeout manifest: `{str(summary.get('must_not_be_used_as_closeout_manifest', True)).lower()}`",
        "",
        "## Finding Rows",
        "",
        "| Row Key | Type | Status | Scope | Match | Detail | Closeout Field |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {row_key} | {kind} | {status} | {scope} | {match} | {detail} | {field} |".format(
                row_key=_cell(str(row.get("invalidation_row_id", ""))),
                kind=_cell(str(row.get("finding_type", ""))),
                status=_cell(str(row.get("status", ""))),
                scope=_cell(str(row.get("scope_id", ""))),
                match=_cell(str(row.get("matched_path", ""))),
                detail=_cell(_quarantine_scope_markdown_detail(row)),
                field=_cell(str(row.get("suggested_closeout_field", ""))),
            )
        )
    lines.extend(
        [
            "",
            "## Use",
            "",
            "This audit lists candidate stale paths, ZIP package candidates, "
            "missing expected scopes, and claim-text reference hits for the "
            "immediate quarantine batch only. It is not a citation-removal "
            "approval, not reviewer signoff, not the main closeout manifest, "
            "and not Phase 9 readiness. Reviewers must copy any confirmed "
            "scope evidence into the main closeout record, decide whether "
            "references require removal or boundary wording, and sign off only "
            "for invalidation closeout.",
            "",
        ]
    )
    return "\n".join(lines)


def build_artifact_invalidation_quarantine_non_evidence_index_markdown(
    summary: Mapping[str, Any],
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Render the deduped quarantine non-evidence index as Markdown."""

    lines = [
        "# Artifact Invalidation Quarantine Non-Evidence Index",
        "",
        str(summary.get("claim_boundary", ARTIFACT_INVALIDATION_CLAIM_BOUNDARY)),
        "",
        "## Summary",
        "",
        f"- Source action batch: `{summary.get('source_action_batch', '')}`",
        f"- Phase 9 promotion ready: `{str(summary.get('phase9_promotion_ready', False)).lower()}`",
        f"- Can clear invalidation gate: `{str(summary.get('can_clear_invalidation_gate', False)).lower()}`",
        f"- Indexed artifacts: {summary.get('indexed_artifact_count', 0)}",
        f"- Deduped duplicate findings: {summary.get('deduped_duplicate_count', 0)}",
        f"- Covered quarantine rows: {summary.get('covered_quarantine_row_count', 0)} / {summary.get('expected_quarantine_row_count', 0)}",
        f"- Must not be used as closeout manifest: `{str(summary.get('must_not_be_used_as_closeout_manifest', True)).lower()}`",
        "",
        "## Index Rows",
        "",
        "| Group | Type | Path | Source Rows | Hash | Next Step |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {group} | {kind} | {path} | {source_rows} | {sha} | {next_step} |".format(
                group=_cell(str(row.get("stale_downstream_group", ""))),
                kind=_cell(str(row.get("candidate_type", ""))),
                path=_cell(str(row.get("matched_path", ""))),
                source_rows=_cell(str(row.get("invalidation_row_ids_json", ""))),
                sha=_cell(str(row.get("sha256", ""))),
                next_step=_cell(str(row.get("review_next_step", ""))),
            )
        )
    lines.extend(
        [
            "",
            "## Use",
            "",
            "This derived quarantine index is reviewer triage for the immediate "
            "`quarantine_non_evidence` batch only. It deduplicates candidate "
            "stale full-output and review-package paths from the scope audit. "
            "It is not a closeout manifest, not citation-removal approval, not "
            "reviewer signoff, not artifact regeneration evidence, not "
            "publication readiness, not final-study approval, not formal "
            "acceptance, and not Phase 9 readiness. Confirmed entries must be "
            "copied into the main artifact invalidation closeout record and "
            "signed off only for invalidation closeout.",
            "",
        ]
    )
    return "\n".join(lines)


def build_artifact_invalidation_quarantine_transfer_packet_markdown(
    summary: Mapping[str, Any],
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Render the quarantine non-evidence transfer packet as Markdown."""

    lines = [
        "# Artifact Invalidation Quarantine Non-Evidence Transfer Packet",
        "",
        str(summary.get("claim_boundary", ARTIFACT_INVALIDATION_CLAIM_BOUNDARY)),
        "",
        "## Summary",
        "",
        f"- Source action batch: `{summary.get('source_action_batch', '')}`",
        f"- Phase 9 promotion ready: `{str(summary.get('phase9_promotion_ready', False)).lower()}`",
        f"- Can clear invalidation gate: `{str(summary.get('can_clear_invalidation_gate', False)).lower()}`",
        f"- Rows: {summary.get('row_count', 0)}",
        f"- Candidate artifacts: {summary.get('candidate_artifact_count', 0)}",
        f"- Candidate artifact hash matches: {summary.get('candidate_artifact_hash_match_count', 0)}",
        f"- Candidate artifact missing: {summary.get('candidate_artifact_missing_count', 0)}",
        f"- Candidate artifact hash mismatches: {summary.get('candidate_artifact_hash_mismatch_count', 0)}",
        f"- Current reference hits: {summary.get('current_reference_hit_count', 0)}",
        "- Source integrity check: "
        f"`{'pass' if summary.get('source_integrity_ready', False) else 'fail'}`",
        f"- Covered quarantine rows: {summary.get('covered_quarantine_row_count', 0)} / {summary.get('expected_quarantine_row_count', 0)}",
        f"- Must not be used as closeout manifest: `{str(summary.get('must_not_be_used_as_closeout_manifest', True)).lower()}`",
        "",
        "## Transfer Rows",
        "",
        "| Row Key | Group | Candidates | Current References | Source Scopes | Reviewer Action |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {row_key} | {group} | {candidates} | {refs} | {scopes} | {action} |".format(
                row_key=_cell(str(row.get("invalidation_row_id", ""))),
                group=_cell(str(row.get("stale_downstream_group", ""))),
                candidates=_cell(str(row.get("candidate_artifact_count", ""))),
                refs=_cell(str(row.get("current_reference_hit_count", ""))),
                scopes=_cell(str(row.get("source_scope_ids_json", ""))),
                action=_cell(str(row.get("required_reviewer_action", ""))),
            )
        )
    lines.extend(
        [
            "",
            "## Use",
            "",
            "This packet is reviewer triage only for the immediate "
            "`quarantine_non_evidence` batch. It is not closeout evidence, not "
            "reviewer signoff, not citation-removal approval, not artifact "
            "regeneration evidence, not transfer calibration, not publication "
            "readiness, not final-study approval, not formal acceptance, and "
            "not Phase 9 readiness. It covers only stale full-output and "
            "review-package quarantine rows, not all transfer-profile "
            "invalidation rows. Confirmed entries must be copied into the "
            "separate main artifact invalidation closeout record with "
            "audit/test evidence and non-acceptance reviewer signoff.",
            "",
        ]
    )
    return "\n".join(lines)


def build_artifact_invalidation_quarantine_closeout_prefill_markdown(
    summary: Mapping[str, Any],
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Render the non-closing quarantine closeout prefill worksheet."""

    lines = [
        "# Artifact Invalidation Quarantine Closeout Prefill",
        "",
        str(summary.get("claim_boundary", ARTIFACT_INVALIDATION_CLAIM_BOUNDARY)),
        "",
        "## Summary",
        "",
        f"- Source action batch: `{summary.get('source_action_batch', '')}`",
        f"- Prefill only: `{str(summary.get('prefill_only', True)).lower()}`",
        f"- Phase 9 promotion ready: `{str(summary.get('phase9_promotion_ready', False)).lower()}`",
        f"- Can clear invalidation gate: `{str(summary.get('can_clear_invalidation_gate', False)).lower()}`",
        f"- Must not be used as closeout manifest: `{str(summary.get('must_not_be_used_as_closeout_manifest', True)).lower()}`",
        f"- Rows: {summary.get('row_count', 0)}",
        f"- Prefilled rows: {summary.get('prefilled_row_count', 0)}",
        f"- Candidate artifacts copied into prefill: {summary.get('prefilled_candidate_artifact_count', 0)}",
        f"- Pending or invalid rows: {summary.get('pending_or_invalid_row_count', 0)}",
        f"- CSV SHA256: `{summary.get('csv_sha256', '')}`",
        f"- Source transfer packet manifest: `{summary.get('source_transfer_packet_manifest', '')}`",
        f"- Source transfer packet SHA256: `{summary.get('source_transfer_packet_manifest_sha256', '')}`",
        f"- Source transfer packet status: `{summary.get('source_transfer_packet_manifest_status', '')}`",
        f"- Source transfer packet row count: {summary.get('source_transfer_packet_row_count', 0)}",
        f"- Source transfer packet integrity flag: `{str(summary.get('source_transfer_packet_integrity_ready', False)).lower()}`",
        "",
        "## Prefill Rows",
        "",
        "| Row Key | Actual Disposition | Status | Candidate Artifacts | Exclusion Scope | Audit | Signoff | Can Clear |",
        "| --- | --- | --- | ---: | --- | --- | --- | --- |",
    ]
    for index, row in enumerate(rows, start=1):
        artifacts = _parse_artifact_json_array(
            str(row.get("affected_artifacts_json", "[]")),
            row_index=index,
            field="affected_artifacts_json",
        )
        lines.append(
            "| {row_key} | {actual} | {status} | {count} | {scope} | {audit} | {signoff} | {clear} |".format(
                row_key=_cell(str(row.get("invalidation_row_id", ""))),
                actual=_cell(str(row.get("actual_disposition", ""))),
                status=_cell(str(row.get("closeout_status", ""))),
                count=len(artifacts),
                scope=_cell(str(row.get("exclusion_scope", ""))),
                audit=_cell(str(row.get("audit_result", ""))),
                signoff=_cell(str(row.get("reviewer_signoff_status", ""))),
                clear=_cell(str(row.get("can_clear_invalidation_gate", ""))),
            )
        )
    lines.extend(
        [
            "",
            "## Use",
            "",
            "This file converts the quarantine transfer packet into a closeout-schema "
            "worksheet so a reviewer can copy confirmed path and hash evidence "
            "into the separate main closeout record. It is prefill only: it keeps "
            "`closeout_status=pending`, audit/test results as `not_run`, reviewer "
            "signoff as `unsigned`, and `can_clear_invalidation_gate=false`. It is "
            "not closeout evidence, not citation-removal approval, not reviewer "
            "signoff, not artifact regeneration evidence, not publication "
            "readiness, not final-study approval, not formal acceptance, and not "
            "authorization for Phase 9.",
            "",
        ]
    )
    return "\n".join(lines)


def build_artifact_invalidation_quarantine_closeout_prefill_gap_audit_markdown(
    summary: Mapping[str, Any],
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Render the non-closing quarantine prefill gap audit."""

    lines = [
        "# Artifact Invalidation Quarantine Closeout Prefill Gap Audit",
        "",
        str(summary.get("claim_boundary", ARTIFACT_INVALIDATION_CLAIM_BOUNDARY)),
        "",
        "## Summary",
        "",
        f"- Source action batch: `{summary.get('source_action_batch', '')}`",
        f"- Gap audit only: `{str(summary.get('prefill_gap_audit_only', True)).lower()}`",
        f"- Can clear invalidation gate: `{str(summary.get('can_clear_invalidation_gate', False)).lower()}`",
        f"- Must not be used as closeout manifest: `{str(summary.get('must_not_be_used_as_closeout_manifest', True)).lower()}`",
        f"- Rows: {summary.get('row_count', 0)}",
        f"- Rows with blocking gaps: {summary.get('blocking_gap_row_count', 0)}",
        f"- Candidate artifacts: {summary.get('candidate_artifact_count', 0)}",
        f"- Reference hits: {summary.get('reference_hit_count', 0)}",
        f"- CSV SHA256: `{summary.get('csv_sha256', '')}`",
        f"- Source transfer packet manifest: `{summary.get('source_transfer_packet_manifest', '')}`",
        f"- Source transfer packet SHA256: `{summary.get('source_transfer_packet_manifest_sha256', '')}`",
        f"- Source transfer packet status: `{summary.get('source_transfer_packet_manifest_status', '')}`",
        "",
        "## Gap Counts",
        "",
        "| Gap Code | Rows |",
        "| --- | ---: |",
    ]
    gap_counts = summary.get("gap_code_counts", {})
    if isinstance(gap_counts, Mapping):
        for code, count in sorted(gap_counts.items()):
            lines.append(f"| {_cell(str(code))} | {count} |")
    lines.extend(
        [
            "",
            "## Row Gaps",
            "",
            "| Main Row | Row Key | Group | Candidates | References | Closeout Status | Gaps | Next Reviewer Action |",
            "| ---: | --- | --- | ---: | ---: | --- | --- | --- |",
        ]
    )
    for row in rows:
        gap_codes = json.loads(str(row.get("blocking_gap_codes_json", "[]")))
        lines.append(
            "| {main_row} | {row_key} | {group} | {candidates} | {refs} | {status} | {gaps} | {action} |".format(
                main_row=_cell(str(row.get("main_closeout_template_row_number", ""))),
                row_key=_cell(str(row.get("invalidation_row_id", ""))),
                group=_cell(str(row.get("stale_downstream_group", ""))),
                candidates=_cell(str(row.get("candidate_artifact_count", ""))),
                refs=_cell(str(row.get("reference_hit_count", ""))),
                status=_cell(str(row.get("closeout_status", ""))),
                gaps=_cell(", ".join(str(code) for code in gap_codes)),
                action=_cell(str(row.get("next_reviewer_action", ""))),
            )
        )
    lines.extend(
        [
            "",
            "## Use",
            "",
            "This gap audit is a reviewer-action checklist for the quarantine "
            "closeout prefill. It does not replace the main closeout record. It "
            "does not close artifact invalidation rows, does not approve "
            "citation removal or exclusion, does not provide reviewer signoff, "
            "does not promote Phase 9 outputs, and does not support publication "
            "or final-study claims. Confirmed evidence must be copied into the "
            "main closeout record with audit, targeted-test, and reviewer "
            "signoff fields filled.",
            "",
        ]
    )
    return "\n".join(lines)


def build_artifact_invalidation_quarantine_main_closeout_copy_audit_markdown(
    summary: Mapping[str, Any],
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Render the non-closing quarantine main-closeout copy audit."""

    lines = [
        "# Artifact Invalidation Quarantine Main Closeout Copy Audit",
        "",
        str(summary.get("claim_boundary", ARTIFACT_INVALIDATION_CLAIM_BOUNDARY)),
        "",
        "## Summary",
        "",
        f"- Source action batch: `{summary.get('source_action_batch', '')}`",
        f"- Copy audit only: `{str(summary.get('copy_audit_only', True)).lower()}`",
        f"- Can clear invalidation gate: `{str(summary.get('can_clear_invalidation_gate', False)).lower()}`",
        f"- Must not be used as closeout manifest: `{str(summary.get('must_not_be_used_as_closeout_manifest', True)).lower()}`",
        f"- Rows: {summary.get('row_count', 0)}",
        f"- Main rows found: {summary.get('main_row_found_count', 0)}",
        f"- Affected artifact fields copied: {summary.get('affected_artifacts_copied_count', 0)}",
        f"- Exclusion-scope fields copied: {summary.get('exclusion_scope_copied_count', 0)}",
        f"- Actual-disposition fields copied: {summary.get('actual_disposition_copied_count', 0)}",
        f"- Closed candidates: {summary.get('closed_candidate_count', 0)}",
        f"- Blocking copy-audit rows: {summary.get('blocking_copy_audit_row_count', 0)}",
        f"- CSV SHA256: `{summary.get('csv_sha256', '')}`",
        f"- Source prefill: `{summary.get('source_prefill_path', '')}`",
        f"- Source main closeout: `{summary.get('source_main_closeout_path', '')}`",
        "",
        "## Blocker Counts",
        "",
        "| Blocker Code | Rows |",
        "| --- | ---: |",
    ]
    blocker_counts = summary.get("copy_audit_blocker_counts", {})
    if isinstance(blocker_counts, Mapping):
        for code, count in sorted(blocker_counts.items()):
            lines.append(f"| {_cell(str(code))} | {count} |")
    lines.extend(
        [
            "",
            "## Row Copy State",
            "",
            "| Main Row | Row Key | Group | Main Found | Artifacts | Scope | Disposition | Main Status | Gaps | Next Action |",
            "| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        gap_codes = json.loads(str(row.get("main_closeout_gap_codes_json", "[]")))
        lines.append(
            "| {main_row} | {row_key} | {group} | {found} | {artifacts} | {scope} | {disposition} | {status} | {gaps} | {action} |".format(
                main_row=_cell(str(row.get("main_closeout_template_row_number", ""))),
                row_key=_cell(str(row.get("invalidation_row_id", ""))),
                group=_cell(str(row.get("stale_downstream_group", ""))),
                found=_cell(str(row.get("main_closeout_row_found", ""))),
                artifacts=_cell(str(row.get("affected_artifacts_copy_status", ""))),
                scope=_cell(str(row.get("exclusion_scope_copy_status", ""))),
                disposition=_cell(str(row.get("actual_disposition_copy_status", ""))),
                status=_cell(str(row.get("main_closeout_status", ""))),
                gaps=_cell(", ".join(str(code) for code in gap_codes)),
                action=_cell(str(row.get("next_required_action", ""))),
            )
        )
    lines.extend(
        [
            "",
            "## Use",
            "",
            "This copy audit checks whether the quarantine prefill rows have been "
            "copied into the separate main closeout record. It is not the main "
            "closeout record and does not close any invalidation row. Even a "
            "copied row remains blocked unless the main closeout row also has "
            "reviewer-confirmed disposition, audit evidence, targeted-test "
            "evidence, claim-boundary review, and non-acceptance reviewer "
            "signoff, followed by a passing main closeout support audit.",
            "",
        ]
    )
    return "\n".join(lines)


def build_artifact_invalidation_quarantine_main_closeout_draft_overlay_markdown(
    summary: Mapping[str, Any],
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Render the non-authoritative quarantine closeout draft overlay."""

    lines = [
        "# Artifact Invalidation Quarantine Main Closeout Draft Overlay",
        "",
        str(summary.get("claim_boundary", ARTIFACT_INVALIDATION_CLAIM_BOUNDARY)),
        "",
        "## Summary",
        "",
        f"- Source action batch: `{summary.get('source_action_batch', '')}`",
        f"- Draft overlay only: `{str(summary.get('draft_overlay_only', True)).lower()}`",
        f"- Can clear invalidation gate: `{str(summary.get('can_clear_invalidation_gate', False)).lower()}`",
        f"- Must not be used as closeout manifest: `{str(summary.get('must_not_be_used_as_closeout_manifest', True)).lower()}`",
        f"- Must not replace main closeout record: `{str(summary.get('must_not_replace_main_closeout_record', True)).lower()}`",
        f"- Rows: {summary.get('row_count', 0)}",
        f"- Prefill rows: {summary.get('prefill_row_count', 0)}",
        f"- Overlayed rows: {summary.get('overlayed_row_count', 0)}",
        f"- Closed candidates: {summary.get('closed_candidate_count', 0)}",
        f"- Pending or invalid rows: {summary.get('pending_or_invalid_row_count', 0)}",
        f"- CSV SHA256: `{summary.get('csv_sha256', '')}`",
        f"- Source prefill: `{summary.get('source_prefill_path', '')}`",
        f"- Source main closeout: `{summary.get('source_main_closeout_path', '')}`",
        "",
        "## Disposition Counts",
        "",
        "| Actual Disposition | Rows |",
        "| --- | ---: |",
    ]
    disposition_counts = summary.get("actual_disposition_counts", {})
    if isinstance(disposition_counts, Mapping):
        for status, count in sorted(disposition_counts.items()):
            lines.append(f"| {_cell(str(status))} | {count} |")
    lines.extend(
        [
            "",
            "## Overlay Rows",
            "",
            "| Row Key | Group | Actual Disposition | Status | Candidate Artifacts | Audit | Test | Signoff | Can Clear |",
            "| --- | --- | --- | --- | ---: | --- | --- | --- | --- |",
        ]
    )
    for index, row in enumerate(rows, start=1):
        if "draft overlay from quarantine prefill" not in str(row.get("review_notes", "")):
            continue
        artifacts = _parse_artifact_json_array(
            str(row.get("affected_artifacts_json", "[]")),
            row_index=index,
            field="affected_artifacts_json",
        )
        lines.append(
            "| {row_key} | {group} | {actual} | {status} | {count} | {audit} | {test} | {signoff} | {clear} |".format(
                row_key=_cell(str(row.get("invalidation_row_id", ""))),
                group=_cell(str(row.get("stale_downstream_group", ""))),
                actual=_cell(str(row.get("actual_disposition", ""))),
                status=_cell(str(row.get("closeout_status", ""))),
                count=len(artifacts),
                audit=_cell(str(row.get("audit_result", ""))),
                test=_cell(str(row.get("targeted_test_result", ""))),
                signoff=_cell(str(row.get("reviewer_signoff_status", ""))),
                clear=_cell(str(row.get("can_clear_invalidation_gate", ""))),
            )
        )
    lines.extend(
        [
            "",
            "## Use",
            "",
            "This file is a closeout-schema draft overlay that places the "
            "quarantine prefill rows into the same row order as the main "
            "artifact invalidation closeout record. It is intentionally "
            "non-authoritative: it keeps every row pending, every audit and "
            "targeted-test result as `not_run`, reviewer signoff as `unsigned`, "
            "and all readiness flags as false. It is not the main closeout "
            "record, not reviewer signoff, not artifact regeneration evidence, "
            "not publication readiness, not final-study approval, not formal "
            "acceptance, and not Phase 9 readiness.",
            "",
        ]
    )
    return "\n".join(lines)


def build_artifact_invalidation_quarantine_reference_triage_markdown(
    summary: Mapping[str, Any],
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Render the non-closing quarantine reference triage audit."""

    lines = [
        "# Artifact Invalidation Quarantine Reference Triage",
        "",
        str(summary.get("claim_boundary", ARTIFACT_INVALIDATION_CLAIM_BOUNDARY)),
        "",
        "## Summary",
        "",
        f"- Source action batch: `{summary.get('source_action_batch', '')}`",
        f"- Reference triage only: `{str(summary.get('reference_triage_only', True)).lower()}`",
        f"- Can clear invalidation gate: `{str(summary.get('can_clear_invalidation_gate', False)).lower()}`",
        f"- Must not be used as closeout manifest: `{str(summary.get('must_not_be_used_as_closeout_manifest', True)).lower()}`",
        f"- Rows: {summary.get('row_count', 0)}",
        f"- Unique reference paths: {summary.get('unique_reference_path_count', 0)}",
        f"- CSV SHA256: `{summary.get('csv_sha256', '')}`",
        f"- Source transfer packet manifest: `{summary.get('source_transfer_packet_manifest', '')}`",
        f"- Source transfer packet SHA256: `{summary.get('source_transfer_packet_manifest_sha256', '')}`",
        f"- Source transfer packet status: `{summary.get('source_transfer_packet_manifest_status', '')}`",
        "",
        "## Classification Counts",
        "",
        "| Classification | Rows |",
        "| --- | ---: |",
    ]
    classification_counts = summary.get("reference_classification_counts", {})
    if isinstance(classification_counts, Mapping):
        for classification, count in sorted(classification_counts.items()):
            lines.append(f"| {_cell(str(classification))} | {count} |")
    lines.extend(
        [
            "",
            "## Priority Counts",
            "",
            "| Priority | Rows |",
            "| --- | ---: |",
        ]
    )
    priority_counts = summary.get("review_priority_counts", {})
    if isinstance(priority_counts, Mapping):
        for priority, count in sorted(priority_counts.items()):
            lines.append(f"| {_cell(str(priority))} | {count} |")
    lines.extend(
        [
            "",
            "## Reference Rows",
            "",
            "| Priority | Classification | Row Key | Reference Path | Reviewer Action |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(
            "| {priority} | {classification} | {row_key} | {path} | {action} |".format(
                priority=_cell(str(row.get("review_priority", ""))),
                classification=_cell(str(row.get("reference_classification", ""))),
                row_key=_cell(str(row.get("invalidation_row_id", ""))),
                path=_cell(str(row.get("reference_path", ""))),
                action=_cell(str(row.get("required_reviewer_action", ""))),
            )
        )
    lines.extend(
        [
            "",
            "## Use",
            "",
            "This triage separates current quarantine reference paths by reviewer "
            "priority. It is not citation-removal evidence, not exclusion "
            "approval, not reviewer signoff, not the main closeout record, and "
            "not Phase 9 readiness. A reviewer must still confirm whether each "
            "reference is removed, replaced, or explicitly retained only as "
            "non-evidence context before the related main closeout row can be "
            "completed.",
            "",
        ]
    )
    return "\n".join(lines)


def build_artifact_invalidation_quarantine_claim_reference_remediation_markdown(
    summary: Mapping[str, Any],
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Render line-level claim-reference remediation support as Markdown."""

    lines = [
        "# Artifact Invalidation Quarantine Claim Reference Remediation Packet",
        "",
        str(summary.get("claim_boundary", ARTIFACT_INVALIDATION_CLAIM_BOUNDARY)),
        "",
        "## Summary",
        "",
        f"- Source action batch: `{summary.get('source_action_batch', '')}`",
        f"- Remediation only: `{str(summary.get('claim_reference_remediation_only', True)).lower()}`",
        f"- Review priority scope: `{summary.get('review_priority_scope', '')}`",
        f"- Can clear invalidation gate: `{str(summary.get('can_clear_invalidation_gate', False)).lower()}`",
        f"- Must not be used as closeout manifest: `{str(summary.get('must_not_be_used_as_closeout_manifest', True)).lower()}`",
        f"- Rows: {summary.get('row_count', 0)}",
        f"- Unique reference paths: {summary.get('unique_reference_path_count', 0)}",
        f"- Line-hit rows: {summary.get('line_hit_row_count', 0)}",
        f"- Line-not-found rows: {summary.get('line_not_found_row_count', 0)}",
        f"- CSV SHA256: `{summary.get('csv_sha256', '')}`",
        f"- Source reference triage manifest: `{summary.get('source_reference_triage_manifest', '')}`",
        f"- Source reference triage SHA256: `{summary.get('source_reference_triage_manifest_sha256', '')}`",
        f"- Source reference triage status: `{summary.get('source_reference_triage_manifest_status', '')}`",
        f"- Source scope audit manifest: `{summary.get('source_scope_audit_manifest', '')}`",
        f"- Source scope audit SHA256: `{summary.get('source_scope_audit_manifest_sha256', '')}`",
        f"- Source scope audit status: `{summary.get('source_scope_audit_manifest_status', '')}`",
        "",
        "## Remediation Rows",
        "",
        "| Reference | Line | Row Key | Classification | Pattern | Suggested Remediation |",
        "| --- | ---: | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {path} | {line} | {row_key} | {classification} | {pattern} | {remediation} |".format(
                path=_cell(str(row.get("reference_path", ""))),
                line=_cell(str(row.get("line_number", ""))),
                row_key=_cell(str(row.get("invalidation_row_id", ""))),
                classification=_cell(str(row.get("reference_classification", ""))),
                pattern=_cell(str(row.get("matched_pattern", ""))),
                remediation=_cell(str(row.get("suggested_remediation", ""))),
            )
        )
    lines.extend(
        [
            "",
            "## Use",
            "",
            "This packet narrows the `review_first` quarantine reference rows "
            "to line-level edit tasks. It is not citation-removal evidence, "
            "not exclusion approval, not reviewer signoff, not the main "
            "closeout record, not publication readiness, not final-study "
            "approval, and not Phase 9 readiness. Reviewers must edit or "
            "explicitly downgrade the referenced claim text, run the recorded "
            "claim-language and targeted tests, and copy confirmed evidence "
            "into the separate main artifact invalidation closeout record.",
            "",
        ]
    )
    return "\n".join(lines)


def _row_from_spec(spec: InvalidationRowSpec, *, default_status: str) -> dict[str, str]:
    claim_effect = (
        "claim_eligible_after_reaudit"
        if default_status == "cleared_after_reaudit"
        else "blocks_claim_support"
    )
    phase9_effect = (
        "review_only_after_reaudit"
        if default_status == "cleared_after_reaudit"
        else "blocks_phase9_promotion"
    )
    return {
        "upstream_change_group": spec.upstream_change_group,
        "upstream_change_trigger": spec.upstream_change_trigger,
        "stale_downstream_group": spec.stale_downstream_group,
        "stale_downstream_description": spec.stale_downstream_description,
        "required_disposition": spec.required_disposition,
        "disposition_status": default_status,
        "claim_boundary_effect": claim_effect,
        "audit_or_regeneration_command": spec.audit_or_regeneration_command,
        "phase9_promotion_effect": phase9_effect,
        "can_support_phase9_promotion": "false",
        "publication_ready": "false",
        "final_study_ready": "false",
        "formal_acceptance_evidence": "false",
        "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
    }


def _validate_rows(rows: Sequence[Mapping[str, str]]) -> None:
    for index, row in enumerate(rows, start=1):
        missing = [field for field in ARTIFACT_INVALIDATION_FIELDS if field not in row]
        if missing:
            raise ValueError(f"row {index} missing fields: {missing}")
        upstream = str(row["upstream_change_group"])
        if upstream not in UPSTREAM_GROUPS:
            raise ValueError(f"row {index} has unsupported upstream group: {upstream}")
        required = str(row["required_disposition"])
        if required not in ALLOWED_REQUIRED_DISPOSITIONS:
            raise ValueError(f"row {index} has unsupported required disposition: {required}")
        status = str(row["disposition_status"])
        if status not in ALLOWED_DISPOSITION_STATUSES:
            raise ValueError(f"row {index} has unsupported disposition status: {status}")
        effect = str(row["claim_boundary_effect"])
        if effect not in ALLOWED_CLAIM_BOUNDARY_EFFECTS:
            raise ValueError(f"row {index} has unsupported claim boundary effect: {effect}")


def _validate_closeout_rows(rows: Sequence[Mapping[str, str]]) -> None:
    for index, row in enumerate(rows, start=1):
        missing = [field for field in ARTIFACT_INVALIDATION_CLOSEOUT_FIELDS if field not in row]
        if missing:
            raise ValueError(f"closeout row {index} missing fields: {missing}")
        upstream = str(row["upstream_change_group"])
        if upstream not in UPSTREAM_GROUPS:
            raise ValueError(
                f"closeout row {index} has unsupported upstream group: {upstream}"
            )
        required = str(row["required_disposition"])
        if required not in ALLOWED_REQUIRED_DISPOSITIONS:
            raise ValueError(
                f"closeout row {index} has unsupported required disposition: {required}"
            )
        closeout = str(row["actual_disposition"])
        if closeout not in ALLOWED_CLOSEOUT_DISPOSITIONS:
            raise ValueError(
                f"closeout row {index} has unsupported closeout disposition: {closeout}"
            )
        status = str(row["closeout_status"])
        if status not in ALLOWED_CLOSEOUT_STATUSES:
            raise ValueError(
                f"closeout row {index} has unsupported closeout status: {status}"
            )
        for field in ("rerun_result", "audit_result", "targeted_test_result"):
            result = str(row[field])
            if result not in ALLOWED_CLOSEOUT_RESULT_STATUSES:
                raise ValueError(
                    f"closeout row {index} has unsupported {field}: {result}"
                )
        signoff = str(row["reviewer_signoff_status"])
        if signoff not in ALLOWED_CLOSEOUT_SIGNOFF_STATUSES:
            raise ValueError(
                f"closeout row {index} has unsupported reviewer signoff status: {signoff}"
            )
        claim_review = str(row["claim_boundary_review_result"])
        if claim_review not in ALLOWED_CLAIM_BOUNDARY_REVIEW_RESULTS:
            raise ValueError(
                f"closeout row {index} has unsupported claim boundary review result: {claim_review}"
            )
        effect = str(row["claim_boundary_effect"])
        if effect not in ALLOWED_CLAIM_BOUNDARY_EFFECTS:
            raise ValueError(
                f"closeout row {index} has unsupported claim boundary effect: {effect}"
            )
        for flag in (
            "can_clear_invalidation_gate",
            "publication_ready",
            "final_study_ready",
            "formal_acceptance_evidence",
        ):
            if str(row[flag]).lower() not in {"true", "false"}:
                raise ValueError(f"closeout row {index} has non-boolean flag {flag}")
        for field in (
            "affected_artifacts_json",
            "upstream_artifacts_json",
            "downstream_before_artifacts_json",
            "downstream_after_artifacts_json",
        ):
            _parse_artifact_json_array(str(row[field]), row_index=index, field=field)


def _validate_action_rows(rows: Sequence[Mapping[str, str]]) -> None:
    for index, row in enumerate(rows, start=1):
        missing = [
            field for field in ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_FIELDS if field not in row
        ]
        if missing:
            raise ValueError(f"action row {index} missing fields: {missing}")
        if str(row["publication_ready"]).lower() != "false":
            raise ValueError(f"action row {index} must keep publication_ready=false")
        if str(row["final_study_ready"]).lower() != "false":
            raise ValueError(f"action row {index} must keep final_study_ready=false")
        if str(row["formal_acceptance_evidence"]).lower() != "false":
            raise ValueError(
                f"action row {index} must keep formal_acceptance_evidence=false"
            )
        if str(row["can_close_without_reviewer_signoff"]).lower() != "false":
            raise ValueError(
                f"action row {index} must require reviewer signoff to close"
            )


def _validate_action_batch_inspection_rows(
    rows: Sequence[Mapping[str, str]],
) -> None:
    for index, row in enumerate(rows, start=1):
        missing = [
            field
            for field in ARTIFACT_INVALIDATION_ACTION_BATCH_INSPECTION_FIELDS
            if field not in row
        ]
        if missing:
            raise ValueError(
                f"action-batch inspection row {index} missing fields: {missing}"
            )
        if str(row["required_disposition"]) not in ALLOWED_REQUIRED_DISPOSITIONS:
            raise ValueError(
                f"action-batch inspection row {index} has unsupported required disposition"
            )
        if not str(row["next_closeout_focus"]):
            raise ValueError(
                f"action-batch inspection row {index} must include next_closeout_focus"
            )
        if not str(row["blocking_prerequisite_status"]):
            raise ValueError(
                f"action-batch inspection row {index} must include prerequisite status"
            )
        if not str(row["allowed_next_operation"]):
            raise ValueError(
                f"action-batch inspection row {index} must include allowed_next_operation"
            )
        package = json.loads(str(row["minimum_evidence_package_json"]))
        if not isinstance(package, list) or not package:
            raise ValueError(
                f"action-batch inspection row {index} must include evidence package list"
            )
        if "can_clear_invalidation_gate" not in package:
            raise ValueError(
                f"action-batch inspection row {index} evidence package must include gate flag"
            )
        for field in (
            "can_clear_invalidation_gate",
            "blocks_phase9_until_closed",
            "can_close_without_reviewer_signoff",
            "publication_ready",
            "final_study_ready",
            "formal_acceptance_evidence",
        ):
            if str(row[field]).lower() not in {"true", "false"}:
                raise ValueError(
                    f"action-batch inspection row {index} has non-boolean {field}"
                )
        if str(row["publication_ready"]).lower() != "false":
            raise ValueError(
                f"action-batch inspection row {index} must keep publication_ready=false"
            )
        if str(row["final_study_ready"]).lower() != "false":
            raise ValueError(
                f"action-batch inspection row {index} must keep final_study_ready=false"
            )
        if str(row["formal_acceptance_evidence"]).lower() != "false":
            raise ValueError(
                f"action-batch inspection row {index} must keep formal_acceptance_evidence=false"
            )
        try:
            missing_evidence = json.loads(str(row["missing_evidence_json"]))
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"action-batch inspection row {index} has invalid missing evidence JSON"
            ) from exc
        if not isinstance(missing_evidence, list) or not all(
            isinstance(item, str) for item in missing_evidence
        ):
            raise ValueError(
                f"action-batch inspection row {index} missing evidence must be a JSON string array"
            )


def _validate_closeout_readiness_rows(rows: Sequence[Mapping[str, str]]) -> None:
    for index, row in enumerate(rows, start=1):
        missing = [
            field
            for field in ARTIFACT_INVALIDATION_CLOSEOUT_READINESS_FIELDS
            if field not in row
        ]
        if missing:
            raise ValueError(f"closeout readiness row {index} missing fields: {missing}")
        if str(row["upstream_change_group"]) not in UPSTREAM_GROUPS:
            raise ValueError(
                f"closeout readiness row {index} has unsupported upstream group"
            )
        if str(row["required_disposition"]) not in ALLOWED_REQUIRED_DISPOSITIONS:
            raise ValueError(
                f"closeout readiness row {index} has unsupported required disposition"
            )
        for field in (
            "can_clear_invalidation_gate",
            "publication_ready",
            "final_study_ready",
            "formal_acceptance_evidence",
        ):
            if str(row[field]).lower() not in {"true", "false"}:
                raise ValueError(
                    f"closeout readiness row {index} has non-boolean {field}"
                )
        try:
            missing_evidence = json.loads(str(row["missing_evidence_json"]))
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"closeout readiness row {index} has invalid missing evidence JSON"
            ) from exc
        if not isinstance(missing_evidence, list) or not all(
            isinstance(item, str) for item in missing_evidence
        ):
            raise ValueError(
                f"closeout readiness row {index} missing evidence must be a JSON string array"
            )


def _validate_quarantine_scope_rows(rows: Sequence[Mapping[str, str]]) -> None:
    for index, row in enumerate(rows, start=1):
        missing = [
            field
            for field in ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_FIELDS
            if field not in row
        ]
        if missing:
            raise ValueError(f"quarantine scope row {index} missing fields: {missing}")
        if row["action_batch"] != "quarantine_non_evidence":
            raise ValueError(
                f"quarantine scope row {index} must stay in quarantine_non_evidence"
            )
        if row["finding_type"] not in {
            "stale_artifact_candidate",
            "reference_hit",
            "zip_candidate",
            "missing_expected",
            "scan_error",
        }:
            raise ValueError(
                f"quarantine scope row {index} has unsupported finding_type"
            )
        if row["status"] not in {"present", "referenced", "missing_expected", "scan_error"}:
            raise ValueError(f"quarantine scope row {index} has unsupported status")
        if row["suggested_closeout_field"] not in {
            "affected_artifacts_json",
            "exclusion_scope",
            "audit_notes",
        }:
            raise ValueError(
                f"quarantine scope row {index} has unsupported suggested closeout field"
            )
        sha = str(row["sha256"])
        if sha and len(sha) != 64:
            raise ValueError(f"quarantine scope row {index} has non-SHA256 hash")


def _validate_quarantine_non_evidence_index_rows(
    rows: Sequence[Mapping[str, str]],
) -> None:
    for index, row in enumerate(rows, start=1):
        missing = [
            field
            for field in ARTIFACT_INVALIDATION_QUARANTINE_NON_EVIDENCE_INDEX_FIELDS
            if field not in row
        ]
        if missing:
            raise ValueError(f"quarantine index row {index} missing fields: {missing}")
        if row["action_batch"] != "quarantine_non_evidence":
            raise ValueError(
                f"quarantine index row {index} must stay in quarantine_non_evidence"
            )
        if row["dependency_stage"] != "immediate_quarantine_before_regeneration":
            raise ValueError(
                f"quarantine index row {index} has unsupported dependency stage"
            )
        if row["stale_downstream_group"] not in {"full_outputs", "review_packages"}:
            raise ValueError(
                f"quarantine index row {index} has unsupported downstream group"
            )
        if row["candidate_type"] not in {"stale_artifact_candidate", "zip_candidate"}:
            raise ValueError(f"quarantine index row {index} has unsupported candidate type")
        if not str(row["matched_path"]).strip():
            raise ValueError(f"quarantine index row {index} must record matched_path")
        sha = str(row["sha256"])
        if sha and len(sha) != 64:
            raise ValueError(f"quarantine index row {index} has non-SHA256 hash")
        for field in ("invalidation_row_ids_json", "scope_ids_json"):
            parsed = json.loads(str(row[field]))
            if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
                raise ValueError(
                    f"quarantine index row {index} field {field} must be a JSON string array"
                )
            if field == "invalidation_row_ids_json" and not parsed:
                raise ValueError(
                    f"quarantine index row {index} must reference at least one invalidation row"
                )


def _validate_quarantine_transfer_packet_rows(
    rows: Sequence[Mapping[str, str]],
) -> None:
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
    expected_ids = _expected_quarantine_row_ids()
    seen_ids: set[str] = set()
    for index, row in enumerate(rows, start=1):
        missing = [
            field
            for field in ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET_FIELDS
            if field not in row
        ]
        if missing:
            raise ValueError(f"quarantine transfer row {index} missing fields: {missing}")
        if forbidden_fields.intersection(row):
            raise ValueError(
                f"quarantine transfer row {index} contains closeout-only fields"
            )
        if row["action_batch"] != "quarantine_non_evidence":
            raise ValueError(
                f"quarantine transfer row {index} must stay in quarantine_non_evidence"
            )
        if row["dependency_stage"] != "immediate_quarantine_before_regeneration":
            raise ValueError(
                f"quarantine transfer row {index} has unsupported dependency stage"
            )
        row_id = str(row["invalidation_row_id"])
        if row_id not in expected_ids:
            raise ValueError(f"quarantine transfer row {index} has unexpected row ID")
        seen_ids.add(row_id)
        if row["stale_downstream_group"] not in {"full_outputs", "review_packages"}:
            raise ValueError(
                f"quarantine transfer row {index} has unsupported downstream group"
            )
        if row["required_disposition"] != "mark_non_evidence":
            raise ValueError(
                f"quarantine transfer row {index} must require mark_non_evidence"
            )
        if row["transfer_status"] != "draft_pending_reviewer_confirmation":
            raise ValueError(f"quarantine transfer row {index} has unsupported status")
        for field in (
            "candidate_artifacts_json",
            "reference_hit_paths_json",
            "source_scope_ids_json",
        ):
            parsed = json.loads(str(row[field]))
            if not isinstance(parsed, list):
                raise ValueError(
                    f"quarantine transfer row {index} field {field} must be a JSON array"
                )
        for artifact in json.loads(str(row["candidate_artifacts_json"])):
            if not isinstance(artifact, dict):
                raise ValueError(
                    f"quarantine transfer row {index} candidate artifacts must be objects"
                )
            sha = str(artifact.get("sha256", ""))
            if sha and len(sha) != 64:
                raise ValueError(
                    f"quarantine transfer row {index} has non-SHA256 artifact hash"
                )
            current_status = str(artifact.get("current_integrity_status", ""))
            if current_status not in {"hash_match", "missing", "hash_mismatch"}:
                raise ValueError(
                    f"quarantine transfer row {index} has unsupported artifact integrity status"
                )
            current_sha = str(artifact.get("current_sha256", ""))
            if current_status != "missing" and len(current_sha) != 64:
                raise ValueError(
                    f"quarantine transfer row {index} has non-SHA256 current artifact hash"
                )
            if str(artifact.get("hash_matches_current_file", "")) not in {
                "true",
                "false",
            }:
                raise ValueError(
                    f"quarantine transfer row {index} has invalid artifact hash-match flag"
                )
    if seen_ids != expected_ids:
        missing_ids = sorted(expected_ids - seen_ids)
        extra_ids = sorted(seen_ids - expected_ids)
        raise ValueError(
            "quarantine transfer packet must cover exactly six quarantine rows; "
            f"missing={missing_ids}; extra={extra_ids}"
        )


def _validate_quarantine_main_closeout_copy_audit_rows(
    rows: Sequence[Mapping[str, str]],
) -> None:
    allowed_copy_statuses = {"copied", "not_copied"}
    allowed_evidence_statuses = {"closed_candidate", "missing_or_incomplete"}
    allowed_audit_statuses = {
        "copied_and_closeout_candidate_requires_support_audit",
        "main_closeout_copy_incomplete",
    }
    for index, row in enumerate(rows, start=1):
        missing = [
            field
            for field in ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_COPY_AUDIT_FIELDS
            if field not in row
        ]
        if missing:
            raise ValueError(
                f"quarantine copy-audit row {index} missing fields: {missing}"
            )
        if str(row["action_batch"]) != "quarantine_non_evidence":
            raise ValueError(
                f"quarantine copy-audit row {index} must stay in quarantine batch"
            )
        if str(row["main_closeout_row_found"]).lower() not in {"true", "false"}:
            raise ValueError(
                f"quarantine copy-audit row {index} has invalid main row flag"
            )
        for field in (
            "affected_artifacts_copy_status",
            "exclusion_scope_copy_status",
            "actual_disposition_copy_status",
        ):
            if str(row[field]) not in allowed_copy_statuses:
                raise ValueError(
                    f"quarantine copy-audit row {index} has invalid {field}"
                )
        if str(row["main_closeout_evidence_status"]) not in allowed_evidence_statuses:
            raise ValueError(
                f"quarantine copy-audit row {index} has invalid evidence status"
            )
        if str(row["copy_audit_status"]) not in allowed_audit_statuses:
            raise ValueError(
                f"quarantine copy-audit row {index} has invalid audit status"
            )
        codes = json.loads(str(row["main_closeout_gap_codes_json"]))
        if not isinstance(codes, list) or not all(
            isinstance(item, str) for item in codes
        ):
            raise ValueError(
                f"quarantine copy-audit row {index} gap codes must be a JSON string array"
            )
        for flag in (
            "can_clear_invalidation_gate",
            "phase9_promotion_ready",
            "publication_ready",
            "final_study_ready",
            "formal_acceptance_evidence",
        ):
            if str(row[flag]).lower() != "false":
                raise ValueError(
                    f"quarantine copy-audit row {index} must keep {flag}=false"
                )
        if str(row["must_not_be_used_as_closeout_manifest"]).lower() != "true":
            raise ValueError(
                f"quarantine copy-audit row {index} must not be closeout manifest"
            )


def _nonclosing_draft_closeout_row(row: Mapping[str, str]) -> dict[str, str]:
    draft = {
        field: str(row.get(field, ""))
        for field in ARTIFACT_INVALIDATION_CLOSEOUT_FIELDS
    }
    draft["closeout_schema_version"] = draft.get("closeout_schema_version") or "1"
    draft["closeout_status"] = "pending"
    draft["rerun_exit_code"] = ""
    draft["rerun_result"] = "not_run"
    draft["audit_exit_code"] = ""
    draft["audit_result"] = "not_run"
    draft["targeted_test_exit_code"] = ""
    draft["targeted_test_result"] = "not_run"
    draft["reviewer_signoff_status"] = "unsigned"
    draft["reviewer_id"] = ""
    draft["reviewed_at_utc"] = ""
    draft["reviewer_evidence_path"] = ""
    draft["reviewer_evidence_sha256"] = ""
    draft["claim_boundary_review_result"] = "pending"
    draft["claim_boundary_effect"] = "blocks_claim_support"
    draft["phase9_promotion_effect"] = "blocks_phase9_promotion"
    draft["can_clear_invalidation_gate"] = "false"
    draft["publication_ready"] = "false"
    draft["final_study_ready"] = "false"
    draft["formal_acceptance_evidence"] = "false"
    draft["claim_boundary"] = ARTIFACT_INVALIDATION_CLAIM_BOUNDARY
    return draft


def _validate_quarantine_main_closeout_draft_overlay_rows(
    rows: Sequence[Mapping[str, str]],
) -> None:
    _validate_closeout_rows(rows)
    for index, row in enumerate(rows, start=1):
        if _closeout_row_is_closed(row):
            raise ValueError(
                f"quarantine draft-overlay row {index} must not be closed"
            )
        if str(row["closeout_status"]) != "pending":
            raise ValueError(
                f"quarantine draft-overlay row {index} must keep closeout_status=pending"
            )
        if str(row["rerun_result"]) != "not_run":
            raise ValueError(
                f"quarantine draft-overlay row {index} must keep rerun_result=not_run"
            )
        if str(row["audit_result"]) != "not_run":
            raise ValueError(
                f"quarantine draft-overlay row {index} must keep audit_result=not_run"
            )
        if str(row["targeted_test_result"]) != "not_run":
            raise ValueError(
                f"quarantine draft-overlay row {index} must keep targeted_test_result=not_run"
            )
        if str(row["reviewer_signoff_status"]) != "unsigned":
            raise ValueError(
                f"quarantine draft-overlay row {index} must keep signoff unsigned"
            )
        if str(row["claim_boundary_review_result"]) != "pending":
            raise ValueError(
                f"quarantine draft-overlay row {index} must keep claim review pending"
            )
        if str(row["phase9_promotion_effect"]) != "blocks_phase9_promotion":
            raise ValueError(
                f"quarantine draft-overlay row {index} must block Phase 9 promotion"
            )
        for flag in (
            "can_clear_invalidation_gate",
            "publication_ready",
            "final_study_ready",
            "formal_acceptance_evidence",
        ):
            if str(row[flag]).lower() != "false":
                raise ValueError(
                    f"quarantine draft-overlay row {index} must keep {flag}=false"
                )


def _validate_quarantine_reference_triage_rows(
    rows: Sequence[Mapping[str, str]],
) -> None:
    allowed_priorities = {
        "review_first",
        "review_after_claim_text",
        "review_for_context_only",
        "confirm_excluded_from_release_scope",
    }
    for index, row in enumerate(rows, start=1):
        missing = [
            field
            for field in ARTIFACT_INVALIDATION_QUARANTINE_REFERENCE_TRIAGE_FIELDS
            if field not in row
        ]
        if missing:
            raise ValueError(
                f"reference triage row {index} missing fields: {missing}"
            )
        if str(row["action_batch"]) != "quarantine_non_evidence":
            raise ValueError(
                f"reference triage row {index} must stay in quarantine batch"
            )
        if str(row["review_priority"]) not in allowed_priorities:
            raise ValueError(
                f"reference triage row {index} has unsupported review priority"
            )
        for flag in (
            "can_clear_invalidation_gate",
            "phase9_promotion_ready",
            "publication_ready",
            "final_study_ready",
            "formal_acceptance_evidence",
        ):
            if str(row[flag]).lower() != "false":
                raise ValueError(
                    f"reference triage row {index} must keep {flag}=false"
                )
        if str(row["must_not_be_used_as_closeout_manifest"]).lower() != "true":
            raise ValueError(
                f"reference triage row {index} must not be closeout manifest"
            )


def _validate_quarantine_claim_reference_remediation_rows(
    rows: Sequence[Mapping[str, str]],
) -> None:
    allowed_statuses = {"line_hit", "line_not_found"}
    for index, row in enumerate(rows, start=1):
        missing = [
            field
            for field in ARTIFACT_INVALIDATION_QUARANTINE_CLAIM_REFERENCE_REMEDIATION_FIELDS
            if field not in row
        ]
        if missing:
            raise ValueError(
                f"claim reference remediation row {index} missing fields: {missing}"
            )
        if str(row["action_batch"]) != "quarantine_non_evidence":
            raise ValueError(
                f"claim reference remediation row {index} must stay in quarantine batch"
            )
        if str(row["review_priority"]) != "review_first":
            raise ValueError(
                f"claim reference remediation row {index} must be review_first only"
            )
        if str(row["line_scan_status"]) not in allowed_statuses:
            raise ValueError(
                f"claim reference remediation row {index} has unsupported line scan status"
            )
        if str(row["line_scan_status"]) == "line_hit" and not str(
            row["line_number"]
        ).isdigit():
            raise ValueError(
                f"claim reference remediation row {index} must include numeric line"
            )
        for flag in (
            "can_clear_invalidation_gate",
            "phase9_promotion_ready",
            "publication_ready",
            "final_study_ready",
            "formal_acceptance_evidence",
        ):
            if str(row[flag]).lower() != "false":
                raise ValueError(
                    f"claim reference remediation row {index} must keep {flag}=false"
                )
        if str(row["must_not_be_used_as_closeout_manifest"]).lower() != "true":
            raise ValueError(
                f"claim reference remediation row {index} must not be closeout manifest"
            )


def _closeout_readiness_row(
    row: Mapping[str, str],
    action_row: Mapping[str, str] | None,
    project_root: Path,
) -> dict[str, str]:
    source_info = _compact_closeout_source_manifest_review(row, project_root)
    missing_evidence = _closeout_missing_evidence(
        row, source_info, project_root=project_root
    )
    reviewer_evidence_status = _closeout_reviewer_evidence_status(
        row, project_root=project_root
    )
    return {
        "readiness_schema_version": "1",
        "invalidation_row_id": str(row.get("invalidation_row_id", "")),
        "action_batch": str(action_row.get("action_batch", "unknown")) if action_row else "unknown",
        "dependency_stage": str(action_row.get("dependency_stage", "unknown")) if action_row else "unknown",
        "upstream_change_group": str(row.get("upstream_change_group", "")),
        "stale_downstream_group": str(row.get("stale_downstream_group", "")),
        "required_disposition": str(row.get("required_disposition", "")),
        "actual_disposition": str(row.get("actual_disposition", "")),
        "closeout_status": str(row.get("closeout_status", "")),
        "artifact_or_exclusion_status": _artifact_or_exclusion_status(row),
        "rerun_status": _closeout_result_status(row, "rerun_result"),
        "audit_status": _closeout_result_status(row, "audit_result"),
        "targeted_test_status": _closeout_result_status(row, "targeted_test_result"),
        "claim_boundary_review_status": str(row.get("claim_boundary_review_result", "")),
        "reviewer_signoff_status": str(row.get("reviewer_signoff_status", "")),
        "reviewer_identity_status": _closeout_reviewer_identity_status(
            row, project_root=project_root
        ),
        "reviewer_evidence_status": reviewer_evidence_status,
        "reviewer_evidence_path": str(row.get("reviewer_evidence_path", "")),
        "reviewer_evidence_sha256": str(row.get("reviewer_evidence_sha256", "")),
        "source_manifest_status": source_info["source_manifest_status"],
        "source_manifest_path": source_info["source_manifest_path"],
        "source_manifest_sha256": source_info["source_manifest_sha256"],
        "source_run_profile": source_info["source_run_profile"],
        "source_run_stage": source_info["source_run_stage"],
        "source_engineering_only": source_info["source_engineering_only"],
        "source_engineering_only_bypass": source_info["source_engineering_only_bypass"],
        "source_phase8_preflight_status": source_info["source_phase8_preflight_status"],
        "source_artifact_invalidation_blocks_phase9": source_info[
            "source_artifact_invalidation_blocks_phase9"
        ],
        "source_rail_source_decisions_pending": source_info[
            "source_rail_source_decisions_pending"
        ],
        "source_publication_ready": source_info["source_publication_ready"],
        "source_final_study_ready": source_info["source_final_study_ready"],
        "source_formal_acceptance_evidence": source_info[
            "source_formal_acceptance_evidence"
        ],
        "source_result_scope": source_info["source_result_scope"],
        "source_clean_checkout_status": source_info["source_clean_checkout_status"],
        "compact_closeout_eligibility_status": source_info[
            "compact_closeout_eligibility_status"
        ],
        "missing_evidence_json": json.dumps(missing_evidence, ensure_ascii=False),
        "can_clear_invalidation_gate": str(
            _closeout_row_is_closed(row, project_root=project_root)
        ).lower(),
        "publication_ready": "false",
        "final_study_ready": "false",
        "formal_acceptance_evidence": "false",
        "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
    }


def _action_batch_inspection_classification(
    action_row: Mapping[str, str],
    readiness_row: Mapping[str, str],
) -> str:
    if str(readiness_row.get("can_clear_invalidation_gate", "")).lower() == "true":
        return "evidence_backed_invalidation_closeout_candidate"
    actual = str(readiness_row.get("actual_disposition", ""))
    recommended = str(action_row.get("recommended_disposition", ""))
    required = str(action_row.get("required_disposition", ""))
    missing = json.loads(str(readiness_row.get("missing_evidence_json", "[]")))
    if actual == "regenerated" and missing:
        return "regeneration_attempt_blocked_missing_evidence"
    if actual in {"explicitly_excluded", "marked_non_evidence"} and missing:
        return "exclusion_attempt_blocked_missing_evidence"
    if recommended == "regenerated" or required == "regenerate":
        return "regeneration_candidate_pending_evidence"
    if recommended.startswith("marked_non_evidence") or required in {
        "mark_non_evidence",
        "explicitly_exclude",
    }:
        return "exclusion_or_non_evidence_candidate_pending_evidence"
    return "pending_closeout_evidence"


def _action_batch_next_closeout_focus(classifications: set[str]) -> str:
    if "evidence_backed_invalidation_closeout_candidate" in classifications:
        return "reaudit_main_closeout_record_before_any_gate_change"
    if any(
        classification.startswith("exclusion")
        for classification in classifications
    ):
        return "confirm_non_evidence_scope_remove_citations_and_record_reviewer_signoff"
    if "regeneration_attempt_blocked_missing_evidence" in classifications:
        return "complete_regeneration_manifest_audit_test_and_reviewer_signoff"
    if "regeneration_candidate_pending_evidence" in classifications:
        return "regenerate_downstream_artifacts_then_record_audit_and_tests"
    return "complete_closeout_disposition_evidence_and_reviewer_signoff"


def _action_row_next_closeout_focus(
    action_row: Mapping[str, str],
    classification: str,
) -> str:
    batch = str(action_row.get("action_batch", ""))
    if batch == "quarantine_non_evidence":
        return "confirm_non_evidence_scope_remove_citations_and_record_reviewer_signoff"
    if classification == "evidence_backed_invalidation_closeout_candidate":
        return "reaudit_main_closeout_record_before_any_gate_change"
    if classification == "regeneration_attempt_blocked_missing_evidence":
        return "complete_regeneration_manifest_audit_test_and_reviewer_signoff"
    if batch == "upstream_evidence_and_benchmarks":
        return "regenerate_source_benchmark_artifacts_after_quarantine_closeout"
    if batch == "compact_outputs":
        return "rerun_compact_outputs_after_upstream_evidence_closeout"
    if batch == "analysis_outputs":
        return "rerun_statistics_sensitivity_or_ml_after_result_manifest_freeze"
    if batch == "claims_and_packages":
        return "refresh_figures_reports_claims_and_packages_after_analysis_closeout"
    return "complete_closeout_disposition_evidence_and_reviewer_signoff"


def _action_row_prerequisite_batch(action_row: Mapping[str, str]) -> str:
    batch = str(action_row.get("action_batch", ""))
    prerequisites = {
        "quarantine_non_evidence": "",
        "upstream_evidence_and_benchmarks": "quarantine_non_evidence",
        "compact_outputs": "upstream_evidence_and_benchmarks",
        "analysis_outputs": "compact_outputs",
        "claims_and_packages": "analysis_outputs",
    }
    return prerequisites.get(batch, "previous_action_batch")


def _action_row_prerequisite_status(
    action_row: Mapping[str, str],
    prerequisite_batch: str,
) -> str:
    batch = str(action_row.get("action_batch", ""))
    if not prerequisite_batch:
        return "first_batch_pending_main_closeout_and_reviewer_confirmation"
    return f"blocked_until_{prerequisite_batch}_rows_are_closed_in_main_closeout"


def _action_row_allowed_next_operation(action_row: Mapping[str, str]) -> str:
    batch = str(action_row.get("action_batch", ""))
    operations = {
        "quarantine_non_evidence": (
            "complete_quarantine_non_evidence_transfer_review_then_update_main_closeout"
        ),
        "upstream_evidence_and_benchmarks": (
            "regenerate_source_benchmark_and_boundary_artifacts_after_quarantine_closeout"
        ),
        "compact_outputs": (
            "rerun_compact_outputs_after_source_benchmark_rows_have_closeout_evidence"
        ),
        "analysis_outputs": (
            "rerun_statistics_sensitivity_and_ml_after_result_manifests_are_immutable"
        ),
        "claims_and_packages": (
            "refresh_figures_reports_claim_alignment_and_package_aids_after_analysis"
        ),
    }
    return operations.get(batch, "complete_next_dependency_safe_closeout_operation")


def _action_row_minimum_evidence_package(
    action_row: Mapping[str, str],
) -> list[str]:
    recommended = str(action_row.get("recommended_disposition", ""))
    batch = str(action_row.get("action_batch", ""))
    package = [
        "actual_disposition",
        "closeout_status",
        "affected_artifacts_or_exclusion_scope",
        "rerun_result",
        "audit_result",
        "targeted_test_result",
        "claim_boundary_review_result",
        "reviewer_signoff_status",
        "can_clear_invalidation_gate",
    ]
    if recommended.startswith(("marked_non_evidence", "explicitly_excluded")):
        package.extend(
            [
                "confirmed_stale_paths_and_hashes",
                "citation_removal_or_non_evidence_scope_audit",
                "non_acceptance_reviewer_signoff",
            ]
        )
    else:
        package.extend(
            [
                "source_manifest_path",
                "source_manifest_hash_or_integrity_review",
                "before_after_hashes",
                "rerun_command",
                "targeted_test_command",
            ]
        )
    if batch == "compact_outputs":
        package.append("compact_manifest_not_engineering_only")
    if batch == "analysis_outputs":
        package.append("immutable_result_manifest_hash")
    if batch == "claims_and_packages":
        package.append("stale_claim_and_caption_review")
    return package


def _closeout_missing_evidence(
    row: Mapping[str, str],
    source_info: Mapping[str, str],
    *,
    project_root: str | Path = PROJECT_ROOT,
) -> list[str]:
    missing: list[str] = []
    if str(row.get("actual_disposition", "")) not in READY_CLOSEOUT_DISPOSITIONS:
        missing.append("actual_disposition")
    if str(row.get("closeout_status", "")) != "closed_invalidation_only":
        missing.append("closeout_status")
    if _artifact_or_exclusion_status(row) != "present":
        missing.append("affected_artifacts_or_exclusion_scope")
    for field in ("rerun_result", "audit_result", "targeted_test_result"):
        if str(row.get(field, "")) not in {"pass", "not_applicable"}:
            missing.append(field)
    if str(row.get("claim_boundary_review_result", "")) not in {
        "pass",
        "not_applicable",
    }:
        missing.append("claim_boundary_review_result")
    if str(row.get("reviewer_signoff_status", "")) != (
        "signed_off_for_invalidation_closeout_only"
    ):
        missing.append("reviewer_signoff_status")
    reviewer_status = _closeout_reviewer_identity_status(
        row, project_root=project_root
    )
    if reviewer_status != "current_reviewer_evidence":
        missing.append(f"reviewer_identity:{reviewer_status}")
    if str(row.get("can_clear_invalidation_gate", "")).lower() != "true":
        missing.append("can_clear_invalidation_gate")
    if str(row.get("publication_ready", "")).lower() != "false":
        missing.append("publication_ready_false")
    if str(row.get("final_study_ready", "")).lower() != "false":
        missing.append("final_study_ready_false")
    if str(row.get("formal_acceptance_evidence", "")).lower() != "false":
        missing.append("formal_acceptance_evidence_false")
    compact_status = str(source_info.get("compact_closeout_eligibility_status", ""))
    if compact_status.startswith("blocked"):
        missing.append(f"compact_source_manifest:{compact_status}")
    return missing


def _artifact_or_exclusion_status(row: Mapping[str, str]) -> str:
    if _closeout_has_artifact_or_exclusion(row):
        return "present"
    return "missing"


def _closeout_result_status(row: Mapping[str, str], field: str) -> str:
    value = str(row.get(field, ""))
    if value in {"pass", "not_applicable"}:
        return "ready"
    return value or "missing"


def _closeout_reviewer_identity_status(
    row: Mapping[str, str],
    *,
    project_root: str | Path = PROJECT_ROOT,
) -> str:
    reviewer_id = str(row.get("reviewer_id", "")).strip()
    reviewed_at = str(row.get("reviewed_at_utc", "")).strip()
    if not reviewer_id:
        return "missing_reviewer_id"
    if reviewer_id.startswith("user_reported_human_reviewer"):
        return "obsolete_human_reviewer_marker"
    if not reviewed_at:
        return "missing_review_timestamp"
    return _closeout_reviewer_evidence_status(row, project_root=Path(project_root))


def _closeout_reviewer_evidence_status(
    row: Mapping[str, str],
    *,
    project_root: Path,
) -> str:
    path_text = str(row.get("reviewer_evidence_path", "")).strip()
    expected_sha = str(row.get("reviewer_evidence_sha256", "")).strip()
    if not path_text:
        return "missing_reviewer_evidence_path"
    if not expected_sha:
        return "missing_reviewer_evidence_sha256"
    if len(expected_sha) != 64:
        return "invalid_reviewer_evidence_sha256"

    evidence_path = Path(path_text)
    if not evidence_path.is_absolute():
        evidence_path = project_root / evidence_path
    if not evidence_path.exists():
        return "reviewer_evidence_file_missing"
    current_sha = _sha256_file(evidence_path)
    if current_sha != expected_sha:
        return "reviewer_evidence_hash_mismatch"
    try:
        value = json.loads(evidence_path.read_text(encoding="utf-8"))
    except Exception:
        return "reviewer_evidence_unreadable"
    if not isinstance(value, Mapping):
        return "reviewer_evidence_not_object"

    problems = _reviewer_evidence_record_problems(value, row, project_root=project_root)
    if problems:
        return problems[0]
    return "current_reviewer_evidence"


def _reviewer_evidence_record_problems(
    record: Mapping[str, Any],
    row: Mapping[str, str],
    *,
    project_root: Path,
) -> list[str]:
    problems: list[str] = []
    missing = [
        field
        for field in ARTIFACT_INVALIDATION_REVIEWER_EVIDENCE_REQUIRED_FIELDS
        if field not in record
    ]
    if missing:
        return [f"reviewer_evidence_missing_{missing[0]}"]
    if record.get("record_type") != ARTIFACT_INVALIDATION_REVIEWER_EVIDENCE_RECORD_TYPE:
        return ["reviewer_evidence_invalid_record_type"]
    if _positive_record_int(record.get("schema_version")) != 1:
        problems.append("reviewer_evidence_invalid_schema_version")
    if str(record.get("scope", "")).strip() != ARTIFACT_INVALIDATION_REVIEWER_EVIDENCE_SCOPE:
        problems.append("reviewer_evidence_invalid_scope")
    if str(record.get("invalidation_row_id", "")).strip() != str(
        row.get("invalidation_row_id", "")
    ).strip():
        problems.append("reviewer_evidence_row_id_mismatch")
    if str(record.get("reviewer_id", "")).strip() != str(row.get("reviewer_id", "")).strip():
        problems.append("reviewer_evidence_reviewer_id_mismatch")
    if str(record.get("reviewed_at_utc", "")).strip() != str(
        row.get("reviewed_at_utc", "")
    ).strip():
        problems.append("reviewer_evidence_reviewed_at_mismatch")
    if str(record.get("decision", "")).strip() != ARTIFACT_INVALIDATION_REVIEWER_EVIDENCE_DECISION:
        problems.append("reviewer_evidence_invalid_decision")

    if str(record.get("record_type", "")).strip() == "sub_agent_gate_review":
        problems.append("reviewer_evidence_gate_record_type_forbidden")
    if str(record.get("status", "")).strip() == "accepted":
        problems.append("reviewer_evidence_gate_acceptance_status_forbidden")
    if bool(record.get("can_mark_complete", False)):
        problems.append("reviewer_evidence_can_mark_complete_forbidden")
    for field in (
        "publication_ready",
        "final_study_ready",
        "formal_acceptance_evidence",
    ):
        if bool(record.get(field, False)):
            problems.append(f"reviewer_evidence_{field}_must_be_false")

    reviewed_paths = _record_string_sequence(record.get("reviewed_paths"))
    evidence_paths = _record_string_sequence(record.get("evidence_paths"))
    if not reviewed_paths:
        problems.append("reviewer_evidence_missing_reviewed_paths")
    if not evidence_paths:
        problems.append("reviewer_evidence_missing_evidence_paths")
    elif all(_is_reviewer_support_only_path(path) for path in evidence_paths):
        problems.append("reviewer_evidence_support_only_paths")
    else:
        for path_text in evidence_paths:
            evidence_path = Path(path_text)
            if not evidence_path.is_absolute():
                evidence_path = project_root / evidence_path
            if not evidence_path.exists():
                problems.append("reviewer_evidence_referenced_path_missing")
                break

    return problems


def _positive_record_int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        return -1
    return value


def _record_string_sequence(value: object) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, str):
        return ()
    return tuple(str(item).strip() for item in value if str(item).strip())


def _is_reviewer_support_only_path(path: str) -> bool:
    name = Path(path).name
    return name in ARTIFACT_INVALIDATION_REVIEWER_SUPPORT_BASENAMES


def _closeout_has_artifact_or_exclusion(row: Mapping[str, str]) -> bool:
    disposition = str(row.get("actual_disposition", ""))
    has_path_or_exclusion = bool(
        _parse_artifact_json_array(
            str(row.get("affected_artifacts_json", "[]")),
            row_index=0,
            field="affected_artifacts_json",
        )
    )
    if disposition in {"explicitly_excluded", "marked_non_evidence"}:
        has_path_or_exclusion = has_path_or_exclusion or bool(
            str(row.get("exclusion_scope", "")).strip()
        )
    return has_path_or_exclusion


def _closeout_row_is_closed(
    row: Mapping[str, str],
    *,
    project_root: str | Path = PROJECT_ROOT,
) -> bool:
    disposition = str(row.get("actual_disposition", ""))
    compact_source = _compact_closeout_source_manifest_review(row, Path(project_root))
    if str(compact_source["compact_closeout_eligibility_status"]).startswith("blocked"):
        return False
    return (
        disposition in READY_CLOSEOUT_DISPOSITIONS
        and str(row.get("closeout_status", "")) == "closed_invalidation_only"
        and str(row.get("can_clear_invalidation_gate", "")).lower() == "true"
        and str(row.get("publication_ready", "")).lower() == "false"
        and str(row.get("final_study_ready", "")).lower() == "false"
        and str(row.get("formal_acceptance_evidence", "")).lower() == "false"
        and str(row.get("rerun_result", "")) in {"pass", "not_applicable"}
        and str(row.get("audit_result", "")) in {"pass", "not_applicable"}
        and str(row.get("targeted_test_result", "")) in {"pass", "not_applicable"}
        and str(row.get("reviewer_signoff_status", ""))
        == "signed_off_for_invalidation_closeout_only"
        and _closeout_reviewer_identity_status(row, project_root=project_root)
        == "current_reviewer_evidence"
        and str(row.get("claim_boundary_review_result", "")) in {"pass", "not_applicable"}
        and str(row.get("phase9_promotion_effect", "")) == "review_only_after_reaudit"
        and str(row.get("claim_boundary_effect", "")) in {
            "claim_eligible_after_reaudit",
            "excluded_from_current_claim_scope",
            "non_evidence_only",
        }
        and _closeout_has_artifact_or_exclusion(row)
    )


def _compact_closeout_source_manifest_review(
    row: Mapping[str, str],
    project_root: Path,
) -> dict[str, str]:
    default = _empty_source_manifest_review()
    if not (
        str(row.get("stale_downstream_group", "")) == "compact_outputs"
        and str(row.get("actual_disposition", "")) == "regenerated"
    ):
        default["source_manifest_status"] = "not_applicable"
        default["compact_closeout_eligibility_status"] = "not_applicable"
        return default

    artifacts = _closeout_artifact_records(row)
    manifest_artifacts = [
        artifact for artifact in artifacts if _is_compact_source_manifest_path(artifact)
    ]
    if not manifest_artifacts:
        default["source_manifest_status"] = "missing"
        default["compact_closeout_eligibility_status"] = "blocked_missing_source_manifest"
        return default

    inspected: list[dict[str, str]] = []
    for artifact in manifest_artifacts:
        info = _inspect_compact_source_manifest_artifact(artifact, project_root)
        inspected.append(info)
    blocked = [
        info
        for info in inspected
        if str(info["compact_closeout_eligibility_status"]).startswith("blocked")
    ]
    if blocked:
        return blocked[0]
    eligible = [
        info
        for info in inspected
        if info["compact_closeout_eligibility_status"] == "eligible"
    ]
    if eligible:
        return eligible[0]
    return inspected[0]


def _closeout_manifest_csv_verification(value: Mapping[str, Any]) -> dict[str, Any]:
    outputs = value.get("outputs", {})
    if not isinstance(outputs, Mapping):
        return {
            "status": "missing_outputs_object",
            "csv_path": "",
            "summary_matches_manifest": False,
            "row_summary": {},
        }
    csv_path_value = str(outputs.get("csv", ""))
    if not csv_path_value:
        return {
            "status": "missing_csv_output_path",
            "csv_path": "",
            "summary_matches_manifest": False,
            "row_summary": {},
        }
    csv_path = _resolve_project_path(csv_path_value, PROJECT_ROOT)
    if not csv_path.is_file():
        return {
            "status": "missing_csv_file",
            "csv_path": csv_path_value,
            "summary_matches_manifest": False,
            "row_summary": {},
        }
    try:
        rows = read_artifact_invalidation_closeout_rows(csv_path)
        row_summary = summarize_artifact_invalidation_closeout_rows(rows)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {
            "status": f"invalid_csv:{type(exc).__name__}",
            "csv_path": csv_path_value,
            "summary_matches_manifest": False,
            "row_summary": {},
        }
    summary_matches = all(
        int(value.get(field, -1)) == int(row_summary.get(field, -2))
        for field in (
            "row_count",
            "closed_row_count",
            "pending_or_invalid_row_count",
        )
    )
    return {
        "status": "verified",
        "csv_path": csv_path_value,
        "summary_matches_manifest": summary_matches,
        "row_summary": row_summary,
    }


def _empty_source_manifest_review() -> dict[str, str]:
    return {
        "source_manifest_status": "",
        "source_manifest_path": "",
        "source_manifest_sha256": "",
        "source_run_profile": "",
        "source_run_stage": "",
        "source_engineering_only": "",
        "source_engineering_only_bypass": "",
        "source_phase8_preflight_status": "",
        "source_artifact_invalidation_blocks_phase9": "",
        "source_rail_source_decisions_pending": "",
        "source_publication_ready": "",
        "source_final_study_ready": "",
        "source_formal_acceptance_evidence": "",
        "source_result_scope": "",
        "source_clean_checkout_status": "",
        "compact_closeout_eligibility_status": "",
    }


def _closeout_artifact_records(row: Mapping[str, str]) -> list[Mapping[str, Any]]:
    records: list[Mapping[str, Any]] = []
    for field in (
        "affected_artifacts_json",
        "upstream_artifacts_json",
        "downstream_before_artifacts_json",
        "downstream_after_artifacts_json",
    ):
        records.extend(
            _parse_artifact_json_array(
                str(row.get(field, "[]")),
                row_index=0,
                field=field,
            )
        )
    return records


def _is_compact_source_manifest_path(artifact: Mapping[str, Any]) -> bool:
    if str(artifact.get("role", "")) != "source_manifest":
        return False
    path = str(artifact.get("path", "")).replace("\\", "/").lower()
    if not path.endswith(".json"):
        return False
    name = Path(path).name
    if "receipt" in name:
        return False
    return "manifest" in name


def _inspect_compact_source_manifest_artifact(
    artifact: Mapping[str, Any],
    project_root: Path,
) -> dict[str, str]:
    info = _empty_source_manifest_review()
    raw_path = str(artifact.get("path", ""))
    info["source_manifest_path"] = raw_path
    path = _resolve_project_path(raw_path, project_root)
    blockers: list[str] = []
    if not path.is_file():
        info["source_manifest_status"] = "missing"
        info["compact_closeout_eligibility_status"] = "blocked_missing_source_manifest"
        return info
    actual_sha = _sha256_file(path)
    info["source_manifest_sha256"] = actual_sha
    expected_sha = str(artifact.get("sha256", ""))
    if expected_sha and expected_sha != actual_sha:
        blockers.append("source_manifest_sha256_mismatch")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        info["source_manifest_status"] = f"unreadable:{type(exc).__name__}"
        info["compact_closeout_eligibility_status"] = "blocked_unreadable_source_manifest"
        return info
    if not isinstance(payload, dict):
        info["source_manifest_status"] = "invalid_non_object"
        info["compact_closeout_eligibility_status"] = "blocked_invalid_source_manifest"
        return info

    phase8_preflight = payload.get("phase8_preflight", {})
    if not isinstance(phase8_preflight, dict):
        phase8_preflight = {}
    info.update(
        {
            "source_manifest_status": "loaded",
            "source_run_profile": str(payload.get("run_profile", "")),
            "source_run_stage": str(payload.get("run_stage", "")),
            "source_engineering_only": _json_flag(payload.get("engineering_only")),
            "source_engineering_only_bypass": _json_flag(
                payload.get(
                    "engineering_only_bypass",
                    phase8_preflight.get("engineering_only_bypass"),
                )
            ),
            "source_phase8_preflight_status": str(phase8_preflight.get("status", "")),
            "source_artifact_invalidation_blocks_phase9": _json_flag(
                payload.get(
                    "artifact_invalidation_blocks_phase9",
                    phase8_preflight.get("artifact_invalidation_blocks_phase9"),
                )
            ),
            "source_rail_source_decisions_pending": _json_flag(
                payload.get(
                    "rail_source_decisions_pending",
                    phase8_preflight.get("rail_source_decisions_pending"),
                )
            ),
            "source_publication_ready": _json_flag(payload.get("publication_ready")),
            "source_final_study_ready": _json_flag(payload.get("final_study_ready")),
            "source_formal_acceptance_evidence": _json_flag(
                payload.get("formal_acceptance_evidence")
            ),
            "source_result_scope": str(payload.get("result_scope", "")),
            "source_clean_checkout_status": str(payload.get("clean_checkout_status", "")),
        }
    )
    blockers.extend(_compact_source_manifest_payload_blockers(payload, phase8_preflight))
    if blockers:
        info["compact_closeout_eligibility_status"] = "blocked_" + "_and_".join(
            sorted(set(blockers))
        )
    else:
        info["compact_closeout_eligibility_status"] = "eligible"
    return info


def _compact_source_manifest_payload_blockers(
    payload: Mapping[str, Any],
    phase8_preflight: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []
    scope = str(
        payload.get(
            "closeout_regeneration_scope",
            phase8_preflight.get("closeout_regeneration_scope", ""),
        )
    )
    scope_status = str(
        payload.get(
            "closeout_regeneration_scope_status",
            phase8_preflight.get("closeout_regeneration_scope_status", ""),
        )
    )
    scope_blocks = payload.get(
        "scope_invalidation_blocks",
        phase8_preflight.get("scope_invalidation_blocks"),
    )
    scoped_compact_regeneration = (
        scope == "compact_outputs"
        and scope_status == "passed"
        and scope_blocks is False
        and str(phase8_preflight.get("status", "")) == "scoped_closeout_regeneration"
    )
    if payload.get("engineering_only") is not False:
        blockers.append("engineering_only_not_false")
    if payload.get("engineering_only_bypass", phase8_preflight.get("engineering_only_bypass")) is not False:
        blockers.append("engineering_only_bypass_not_false")
    if str(phase8_preflight.get("status", "")) == "engineering_only_bypass":
        blockers.append("phase8_preflight_bypass")
    if scoped_compact_regeneration:
        if payload.get("publication_ready") is not False:
            blockers.append("publication_ready_not_false")
        if payload.get("final_study_ready") is not False:
            blockers.append("final_study_ready_not_false")
        if payload.get("formal_acceptance_evidence") is not False:
            blockers.append("formal_acceptance_evidence_not_false")
    elif payload.get(
        "artifact_invalidation_blocks_phase9",
        phase8_preflight.get("artifact_invalidation_blocks_phase9"),
    ) is not False:
        blockers.append("artifact_invalidation_blocks_phase9_not_false")
    if (
        not scoped_compact_regeneration
        and payload.get(
            "rail_source_decisions_pending",
            phase8_preflight.get("rail_source_decisions_pending"),
        )
        is not False
    ):
        blockers.append("rail_source_decisions_pending_not_false")
    clean_status = str(payload.get("clean_checkout_status", ""))
    if clean_status not in {
        "clean_checkout_ready",
        "tracked",
        "packaged",
        "included_in_review_package",
        "not_required_for_current_closeout",
    }:
        blockers.append("clean_checkout_status_not_supported")
    return blockers


def _resolve_project_path(path: str, project_root: Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return project_root / candidate


def _json_flag(value: Any) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    if value is None:
        return ""
    return str(value)


def _row_key(row: Mapping[str, str]) -> str:
    return "{upstream}->{downstream}".format(
        upstream=row.get("upstream_change_group", ""),
        downstream=row.get("stale_downstream_group", ""),
    )


def _quarantine_scope_finding_rows(
    row: Mapping[str, str],
    *,
    project_root: Path,
    search_roots: Sequence[str],
) -> list[dict[str, str]]:
    row_id = str(row["invalidation_row_id"])
    group = str(row["stale_downstream_group"])
    findings: list[dict[str, str]] = []
    for scope_id, pattern in _quarantine_candidate_globs(group):
        try:
            matched_paths = sorted(
                path for path in project_root.glob(pattern) if path.is_file()
            )
        except OSError as exc:
            findings.append(
                _quarantine_scope_finding_row(
                    row,
                    scope_id=scope_id,
                    finding_type="scan_error",
                    searched_path_or_glob=pattern,
                    matched_path="",
                    matched_detail=f"glob scan failed: {exc}",
                    status="scan_error",
                    sha256="",
                    suggested_closeout_field="audit_notes",
                )
            )
            continue
        if not matched_paths:
            findings.append(
                _quarantine_scope_finding_row(
                    row,
                    scope_id=scope_id,
                    finding_type="missing_expected",
                    searched_path_or_glob=pattern,
                    matched_path="",
                    matched_detail="no matching artifact found for expected quarantine scope",
                    status="missing_expected",
                    sha256="",
                    suggested_closeout_field="audit_notes",
                )
            )
            continue
        for path in matched_paths:
            relative = _display_path(path)
            finding_type = "zip_candidate" if path.suffix.lower() == ".zip" else "stale_artifact_candidate"
            detail = f"glob={pattern}"
            if finding_type == "zip_candidate":
                detail = _zip_candidate_detail(path, pattern)
            findings.append(
                _quarantine_scope_finding_row(
                    row,
                    scope_id=scope_id,
                    finding_type=finding_type,
                    searched_path_or_glob=pattern,
                    matched_path=relative,
                    matched_detail=detail,
                    status="present",
                    sha256=_sha256_file(path),
                    suggested_closeout_field="affected_artifacts_json",
                )
            )

    citation_patterns = _quarantine_citation_patterns(row_id, group)
    for hit in _citation_hits(
        project_root=project_root,
        search_roots=search_roots,
        patterns=citation_patterns,
    ):
        detail = "line={line}; pattern={pattern}; excerpt={excerpt}".format(
            line=hit.get("line", ""),
            pattern=hit.get("pattern", ""),
            excerpt=hit.get("excerpt", ""),
        )
        findings.append(
            _quarantine_scope_finding_row(
                row,
                scope_id="claim_text_reference",
                finding_type="reference_hit",
                searched_path_or_glob=";".join(search_roots),
                matched_path=str(hit.get("path", "")),
                matched_detail=detail,
                status="referenced",
                sha256="",
                suggested_closeout_field="audit_notes",
            )
        )
    return findings


def _quarantine_scope_finding_row(
    row: Mapping[str, str],
    *,
    scope_id: str,
    finding_type: str,
    searched_path_or_glob: str,
    matched_path: str,
    matched_detail: str,
    status: str,
    sha256: str,
    suggested_closeout_field: str,
) -> dict[str, str]:
    return {
        "invalidation_row_id": str(row["invalidation_row_id"]),
        "action_batch": "quarantine_non_evidence",
        "stale_downstream_group": str(row["stale_downstream_group"]),
        "scope_id": scope_id,
        "finding_type": finding_type,
        "searched_path_or_glob": searched_path_or_glob,
        "matched_path": matched_path,
        "matched_detail": _truncate(matched_detail, 260),
        "status": status,
        "sha256": sha256,
        "suggested_closeout_field": suggested_closeout_field,
        "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
    }


def _closeout_action_row(row: Mapping[str, str]) -> dict[str, str]:
    upstream = str(row["upstream_change_group"])
    group = str(row["stale_downstream_group"])
    stage = _dependency_stage(group, upstream)
    required = str(row["required_disposition"])
    recommended = _recommended_disposition(required, group)
    return {
        "action_order": str(_action_order(group, upstream)),
        "action_batch": _action_batch(group, upstream),
        "dependency_stage": stage,
        "invalidation_row_id": str(row["invalidation_row_id"]),
        "upstream_change_group": upstream,
        "stale_downstream_group": group,
        "required_disposition": required,
        "recommended_disposition": recommended,
        "closeout_dependency": _closeout_dependency(group, upstream),
        "minimum_evidence_required": _minimum_evidence_required(recommended),
        "producer_or_audit_command": str(row["rerun_command"]),
        "targeted_test_command": _targeted_test_command(group),
        "reviewer_role": _reviewer_role(group),
        "blocks_phase9_until_closed": "true",
        "can_close_without_reviewer_signoff": "false",
        "publication_ready": "false",
        "final_study_ready": "false",
        "formal_acceptance_evidence": "false",
        "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
    }


def _action_order(group: str, upstream: str = "") -> int:
    if group == "full_outputs":
        return 1
    if upstream == "claim_boundary_or_readiness_logic" and group == "review_packages":
        return 2
    order = {
        "road_snapshots": 10,
        "connector_audits": 11,
        "route_exposure": 12,
        "graph_scale_diagnostics": 13,
        "benchmarks": 14,
        "multimodal_benchmarks": 15,
        "rail_stress_profiles": 16,
        "benchmark_review_packets": 17,
        "claim_boundaries": 18,
        "compact_outputs": 30,
        "statistics": 40,
        "sensitivity": 41,
        "ml_labels": 42,
        "ml_outputs": 43,
        "figures": 50,
        "reports": 51,
        "publication_readiness": 52,
        "final_study_readiness": 53,
        "formal_guard": 54,
        "review_package_text": 55,
        "review_packages": 56,
    }
    return order.get(group, 80)


def _action_batch(group: str, upstream: str = "") -> str:
    order = _action_order(group, upstream)
    if order < 10:
        return "quarantine_non_evidence"
    if order < 20:
        return "upstream_evidence_and_benchmarks"
    if group == "compact_outputs":
        return "compact_outputs"
    if group in {"statistics", "sensitivity", "ml_labels", "ml_outputs"}:
        return "analysis_outputs"
    if group in {
        "figures",
        "reports",
        "publication_readiness",
        "final_study_readiness",
        "formal_guard",
        "review_package_text",
        "review_packages",
    }:
        return "claims_and_packages"
    return "other"


def _dependency_stage(group: str, upstream: str = "") -> str:
    if _action_order(group, upstream) < 10:
        return "immediate_quarantine_before_regeneration"
    return "before_phase9_promotion"


def _recommended_disposition(required: str, group: str) -> str:
    if group == "full_outputs":
        return "marked_non_evidence_until_new_full_run"
    if required == "mark_non_evidence":
        return "marked_non_evidence_or_regenerated"
    if required == "explicitly_exclude":
        return "explicitly_excluded_or_regenerated"
    return "regenerated"


def _closeout_dependency(group: str, upstream: str = "") -> str:
    if _action_order(group, upstream) < 10:
        return "exclude stale full outputs or review packages from current claims before regeneration work"
    if group in {"statistics", "sensitivity", "ml_labels", "ml_outputs"}:
        return "compact or full result CSV/manifest must be immutable first"
    if group in {"figures", "reports", "review_packages", "review_package_text"}:
        return "source outputs and analysis artifacts must be re-audited first"
    return "upstream source artifact or generated packet must be refreshed first"


def _minimum_evidence_required(disposition: str) -> str:
    if disposition.startswith("marked_non_evidence"):
        return "exclusion scope, stale path list, citation-removal audit, reviewer signoff"
    if disposition.startswith("explicitly_excluded"):
        return "exclusion scope, reason, stale path list, citation-removal audit, reviewer signoff"
    return "affected paths, before/after hashes, rerun command, audit command, targeted tests, reviewer signoff"


def _targeted_test_command(group: str) -> str:
    if group in {"road_snapshots", "route_exposure", "graph_scale_diagnostics"}:
        return ".\\.venv\\Scripts\\python tests\\test_realworld_osm_network.py"
    if group in {"multimodal_benchmarks", "rail_stress_profiles"}:
        return ".\\.venv\\Scripts\\python tests\\test_realworld_rail_evidence.py"
    if group in {"statistics", "sensitivity"}:
        return ".\\.venv\\Scripts\\python tests\\test_realworld_sensitivity.py"
    if group in {"ml_labels", "ml_outputs"}:
        return "add/run Phase 10 ML tests after audited simulation outputs exist"
    if group in {"figures", "reports", "publication_readiness", "final_study_readiness"}:
        return ".\\.venv\\Scripts\\python tests\\test_realworld_publication_readiness.py"
    if group in {"formal_guard", "review_package_text", "review_packages"}:
        return ".\\.venv\\Scripts\\python tests\\test_realworld_review_package_inventory.py"
    return ".\\.venv\\Scripts\\python tests\\test_realworld_artifact_invalidation_matrix.py"


def _reviewer_role(group: str) -> str:
    if group == "full_outputs":
        return "full-run preflight reviewer"
    if group in {"figures", "reports", "review_package_text", "review_packages"}:
        return "claim-boundary adversarial reviewer"
    if group in {"statistics", "sensitivity", "ml_labels", "ml_outputs"}:
        return "statistical or ML-method reviewer"
    return "source/output lineage reviewer"


def _quarantine_candidate_globs(group: str) -> list[tuple[str, str]]:
    if group == "full_outputs":
        return [
            ("full_run_outputs", "results/realworld_pilot/pilot_full*.csv"),
            ("full_run_outputs", "results/realworld_pilot/pilot_full*.json"),
            (
                "multi_corridor_full_outputs",
                "results/realworld_pilot/pilot_multi_corridor_full*.csv",
            ),
            (
                "multi_corridor_full_outputs",
                "results/realworld_pilot/pilot_multi_corridor_full*.json",
            ),
            ("full_statistics_tables", "results/realworld_pilot/tables/*full*.csv"),
            ("full_statistics_tables", "results/realworld_pilot/tables/*full*.json"),
        ]
    if group == "review_packages":
        return [
            ("expected_review_zip", "required_deliverables.zip"),
            ("expected_review_zip", "expert_review_intake.zip"),
            ("expected_review_zip", "review_submission_bundle.zip"),
            ("review_package_zip", "review_packages/*.zip"),
            ("review_package_handoff", "review_packages/*handoff*.md"),
            ("review_package_handoff", "review_packages/*handoff*.json"),
            ("review_package_docs", "docs/review_package*.md"),
            ("review_package_manifest", "data/manifests/review_package*.json"),
            ("review_package_manifest", "data/manifests/review_package*.csv"),
        ]
    return []


def _quarantine_citation_patterns(row_id: str, group: str) -> list[str]:
    patterns = [row_id]
    if group == "full_outputs":
        patterns.extend(
            [
                "pilot_full",
                "pilot_multi_corridor_full",
                "full_outputs",
                "full outputs",
                "full-run outputs",
                "full experiment",
            ]
        )
    elif group == "review_packages":
        patterns.extend(
            [
                "review_packages/",
                "expert_review_package.zip",
                "required_deliverables",
                "review package",
                "review-package",
            ]
        )
    return patterns


def _quarantine_exclusion_scope(row_id: str, group: str) -> str:
    if group == "full_outputs":
        return (
            "Exclude current full-output result, summary, manifest, table, and "
            "figure artifacts from Phase 9 claims until regenerated after compact "
            f"promotion for row {row_id}."
        )
    if group == "review_packages":
        return (
            "Exclude current review-package ZIP and handoff text from Phase 9 "
            f"promotion claims until rebuilt and re-audited for row {row_id}."
        )
    return f"Exclude stale artifacts for row {row_id} until reviewer closeout."


def _citation_hits(
    *,
    project_root: Path,
    search_roots: Sequence[str],
    patterns: Sequence[str],
) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    lowered_patterns = [pattern.lower() for pattern in patterns]
    for path in _iter_claim_text_files(project_root, search_roots):
        relative = _display_path(path)
        if relative in QUARANTINE_AUDIT_SELF_PATHS:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(lines, start=1):
            lowered = line.lower()
            for pattern, lowered_pattern in zip(patterns, lowered_patterns):
                if lowered_pattern and lowered_pattern in lowered:
                    hits.append(
                        {
                            "path": relative,
                            "line": str(line_number),
                            "pattern": pattern,
                            "excerpt": _truncate(line.strip(), 180),
                        }
                    )
                    break
            if len(hits) >= 120:
                return hits
    return hits


def _expected_quarantine_row_ids() -> set[str]:
    return {
        str(row["invalidation_row_id"])
        for row in build_artifact_invalidation_quarantine_closeout_template_rows()
    }


def _is_archival_reference_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return normalized.startswith("docs/archive/") or normalized.startswith(
        "docs/recovery/"
    )


def _quarantine_reference_triage(path: str) -> tuple[str, str, str]:
    normalized = path.replace("\\", "/")
    for marker in ("/docs/", "/paper/", "/review_packages/"):
        marker_index = normalized.find(marker)
        if marker_index >= 0:
            normalized = normalized[marker_index + 1 :]
            break
    filename = Path(normalized).name.lower()
    if filename == "readme.md":
        normalized = "README.md"
    elif filename == "report_draft.md":
        normalized = "report_draft.md"
    elif filename in {"plan.md", "status.md", "agents.md"}:
        normalized = filename
    if _is_archival_reference_path(normalized):
        return (
            "archival_or_recovery_reference",
            "confirm_excluded_from_release_scope",
            "Confirm this reference is archival or recovery-only and is not used as Phase 9 or publication evidence.",
        )
    if normalized in {
        "README.md",
        "report_draft.md",
    } or normalized.startswith("paper/"):
        return (
            "active_claim_text_candidate",
            "review_first",
            "Review first; remove, replace, or explicitly downgrade this reference before copying the closeout row.",
        )
    if normalized in {"plan.md", "status.md", "agents.md"}:
        return (
            "planning_or_status_reference",
            "review_after_claim_text",
            "Review after release claim text; retain only if it remains planning/status context and not closeout evidence.",
        )
    generated_markers = (
        "acceptance",
        "audit",
        "classification",
        "diagnostic",
        "packet",
        "readiness",
        "manifest",
        "invalidation",
        "review",
        "ledger",
        "handoff",
        "guard",
        "template",
        "queue",
        "matrix",
    )
    if normalized.startswith("docs/") and any(
        marker in filename for marker in generated_markers
    ):
        return (
            "generated_audit_or_review_support_reference",
            "review_for_context_only",
            "Confirm this generated support document is non-evidence context and is not cited as Phase 9 closeout.",
        )
    if normalized.startswith("review_packages/"):
        return (
            "review_package_context_reference",
            "review_for_context_only",
            "Confirm the review-package reference is stale/non-evidence or rebuild the package after upstream closeout.",
        )
    if normalized.startswith("docs/"):
        return (
            "documentation_claim_candidate",
            "review_first",
            "Review as possible claim-bearing documentation; remove, replace, or explicitly downgrade the reference.",
        )
    return (
        "planning_or_status_reference",
        "review_after_claim_text",
        "Review the path context before treating it as non-evidence.",
    )


def _claim_reference_remediation_row(
    triage_row: Mapping[str, str],
    *,
    scope_row: Mapping[str, str] | None,
    triage_lineage: Mapping[str, Any],
    scope_lineage: Mapping[str, Any],
) -> dict[str, str]:
    detail = (
        _parse_quarantine_scope_reference_detail(
            str(scope_row.get("matched_detail", "")) if scope_row is not None else ""
        )
        if scope_row is not None
        else {"line": "", "pattern": "", "excerpt": ""}
    )
    line_status = "line_hit" if scope_row is not None else "line_not_found"
    return {
        "remediation_schema_version": "1",
        "action_batch": "quarantine_non_evidence",
        "dependency_stage": str(triage_row.get("dependency_stage", "")),
        "invalidation_row_id": str(triage_row.get("invalidation_row_id", "")),
        "stale_downstream_group": str(triage_row.get("stale_downstream_group", "")),
        "reference_path": str(triage_row.get("reference_path", "")),
        "reference_classification": str(
            triage_row.get("reference_classification", "")
        ),
        "review_priority": str(triage_row.get("review_priority", "")),
        "line_scan_status": line_status,
        "line_number": str(detail.get("line", "")),
        "matched_pattern": str(detail.get("pattern", "")),
        "excerpt": str(detail.get("excerpt", "")),
        "source_scope_id": str(scope_row.get("scope_id", "")) if scope_row else "",
        "source_scope_matched_detail": str(scope_row.get("matched_detail", ""))
        if scope_row
        else "",
        "triage_required_reviewer_action": str(
            triage_row.get("required_reviewer_action", "")
        ),
        "suggested_remediation": _claim_reference_remediation_action(triage_row),
        "source_reference_triage_manifest": str(
            triage_lineage["source_reference_triage_manifest"]
        ),
        "source_reference_triage_manifest_sha256": str(
            triage_lineage["source_reference_triage_manifest_sha256"]
        ),
        "source_reference_triage_manifest_status": str(
            triage_lineage["source_reference_triage_manifest_status"]
        ),
        "source_scope_audit_manifest": str(scope_lineage["source_scope_audit_manifest"]),
        "source_scope_audit_manifest_sha256": str(
            scope_lineage["source_scope_audit_manifest_sha256"]
        ),
        "source_scope_audit_manifest_status": str(
            scope_lineage["source_scope_audit_manifest_status"]
        ),
        "can_clear_invalidation_gate": "false",
        "phase9_promotion_ready": "false",
        "publication_ready": "false",
        "final_study_ready": "false",
        "formal_acceptance_evidence": "false",
        "must_not_be_used_as_closeout_manifest": "true",
        "claim_boundary": ARTIFACT_INVALIDATION_CLAIM_BOUNDARY,
    }


def _claim_reference_remediation_action(triage_row: Mapping[str, str]) -> str:
    classification = str(triage_row.get("reference_classification", ""))
    path = str(triage_row.get("reference_path", ""))
    if classification == "active_claim_text_candidate":
        return (
            "Edit active claim text: remove stale full-output/review-package "
            "reference, replace it with current non-evidence boundary wording, "
            "or cite a refreshed source-backed artifact before closeout copy."
        )
    if classification == "documentation_claim_candidate":
        return (
            "Review documentation claim context: remove or downgrade the stale "
            "reference unless the document is explicitly excluded from release evidence."
        )
    return (
        "Review path context for `{path}` and retain only if explicitly marked "
        "as non-evidence support."
    ).format(path=path)


def _parse_quarantine_scope_reference_detail(detail: str) -> dict[str, str]:
    parsed = {"line": "", "pattern": "", "excerpt": ""}
    for key in ("line", "pattern", "excerpt"):
        marker = f"{key}="
        if marker not in detail:
            continue
        value = detail.split(marker, 1)[1]
        next_parts = [
            value.find(f"; {other}=")
            for other in ("line", "pattern", "excerpt")
            if other != key and value.find(f"; {other}=") >= 0
        ]
        if next_parts:
            value = value[: min(next_parts)]
        parsed[key] = value.strip()
    return parsed


def _scope_detail_line_number(detail: str) -> int:
    parsed = _parse_quarantine_scope_reference_detail(detail)
    return _safe_int(parsed.get("line", ""), default=10**9)


def _safe_int(value: Any, *, default: int) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return default


def _quarantine_reference_triage_manifest_lineage(path: Path) -> dict[str, Any]:
    lineage: dict[str, Any] = {
        "source_reference_triage_manifest": _display_path(path),
        "source_reference_triage_manifest_status": "missing",
        "source_reference_triage_manifest_sha256": "",
        "source_reference_triage_row_count": 0,
        "source_reference_triage_must_not_be_used_as_closeout_manifest": True,
    }
    if not path.exists():
        return lineage
    lineage["source_reference_triage_manifest_sha256"] = _sha256_file(path)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive path
        lineage["source_reference_triage_manifest_status"] = (
            f"unreadable:{type(exc).__name__}"
        )
        return lineage
    if not isinstance(value, dict):
        lineage["source_reference_triage_manifest_status"] = "invalid_non_object"
        return lineage
    lineage.update(
        {
            "source_reference_triage_manifest_status": "loaded",
            "source_reference_triage_row_count": int(value.get("row_count", 0)),
            "source_reference_triage_must_not_be_used_as_closeout_manifest": bool(
                value.get("must_not_be_used_as_closeout_manifest", True)
            ),
        }
    )
    return lineage


def _quarantine_scope_manifest_lineage(path: Path) -> dict[str, Any]:
    lineage: dict[str, Any] = {
        "source_scope_audit_manifest": _display_path(path),
        "source_scope_audit_manifest_status": "missing",
        "source_scope_audit_manifest_sha256": "",
        "source_scope_audit_row_count": 0,
        "source_scope_audit_reference_hit_count": 0,
        "source_scope_audit_must_not_be_used_as_closeout_manifest": True,
    }
    if not path.exists():
        return lineage
    lineage["source_scope_audit_manifest_sha256"] = _sha256_file(path)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive path
        lineage["source_scope_audit_manifest_status"] = (
            f"unreadable:{type(exc).__name__}"
        )
        return lineage
    if not isinstance(value, dict):
        lineage["source_scope_audit_manifest_status"] = "invalid_non_object"
        return lineage
    lineage.update(
        {
            "source_scope_audit_manifest_status": "loaded",
            "source_scope_audit_row_count": int(value.get("row_count", 0)),
            "source_scope_audit_reference_hit_count": int(
                value.get("reference_hit_count", 0)
            ),
            "source_scope_audit_must_not_be_used_as_closeout_manifest": bool(
                value.get("must_not_be_used_as_closeout_manifest", True)
            ),
        }
    )
    return lineage


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _candidate_artifact_transfer_record(
    artifact: Mapping[str, str],
    project_root: Path,
) -> dict[str, str]:
    record = {key: str(value) for key, value in artifact.items()}
    path_text = record.get("path", "")
    path = Path(path_text)
    artifact_path = path if path.is_absolute() else project_root / path
    expected_sha = record.get("sha256", "")
    if not artifact_path.exists():
        record.update(
            {
                "current_integrity_status": "missing",
                "current_sha256": "",
                "hash_matches_current_file": "false",
            }
        )
        return record

    current_sha = _sha256_file(artifact_path)
    hash_matches = current_sha == expected_sha
    record.update(
        {
            "current_integrity_status": (
                "hash_match" if hash_matches else "hash_mismatch"
            ),
            "current_sha256": current_sha,
            "hash_matches_current_file": str(hash_matches).lower(),
        }
    )
    return record


def _closeout_prefill_artifacts_from_transfer(
    transfer_row: Mapping[str, str],
) -> list[dict[str, str]]:
    artifacts: list[dict[str, str]] = []
    for artifact in json.loads(str(transfer_row["candidate_artifacts_json"])):
        artifacts.append(
            {
                "path": str(artifact.get("path", "")),
                "sha256": str(
                    artifact.get("current_sha256") or artifact.get("sha256", "")
                ),
                "candidate_type": str(artifact.get("candidate_type", "")),
                "source": "quarantine_non_evidence_transfer_packet",
                "source_index_row_number": str(
                    artifact.get("source_index_row_number", "")
                ),
                "source_finding_count": str(artifact.get("source_finding_count", "")),
                "current_integrity_status": str(
                    artifact.get("current_integrity_status", "")
                ),
                "hash_matches_current_file": str(
                    artifact.get("hash_matches_current_file", "")
                ),
            }
        )
    return artifacts


def _closeout_prefill_source_manifests(
    transfer_row: Mapping[str, str],
) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for field in (
        "source_non_evidence_index_manifest",
        "source_scope_audit_manifest",
        "source_quarantine_template_manifest",
    ):
        path = str(transfer_row.get(field, ""))
        if path:
            records.append({"path": path, "sha256": "", "source": field})
    return records


def _quarantine_transfer_manifest_lineage(path: Path) -> dict[str, Any]:
    lineage: dict[str, Any] = {
        "source_transfer_packet_manifest": _display_path(path),
        "source_transfer_packet_manifest_status": "missing",
        "source_transfer_packet_manifest_sha256": "",
        "source_transfer_packet_row_count": 0,
        "source_transfer_packet_candidate_artifact_count": 0,
        "source_transfer_packet_integrity_ready": False,
        "source_transfer_packet_must_not_be_used_as_closeout_manifest": True,
    }
    if not path.exists():
        return lineage
    lineage["source_transfer_packet_manifest_sha256"] = _sha256_file(path)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive path
        lineage["source_transfer_packet_manifest_status"] = (
            f"unreadable:{type(exc).__name__}"
        )
        return lineage
    if not isinstance(value, dict):
        lineage["source_transfer_packet_manifest_status"] = "invalid_non_object"
        return lineage
    lineage.update(
        {
            "source_transfer_packet_manifest_status": "loaded",
            "source_transfer_packet_row_count": int(value.get("row_count", 0)),
            "source_transfer_packet_candidate_artifact_count": int(
                value.get("candidate_artifact_count", 0)
            ),
            "source_transfer_packet_integrity_ready": bool(
                value.get("source_integrity_ready", False)
            ),
            "source_transfer_packet_must_not_be_used_as_closeout_manifest": bool(
                value.get("must_not_be_used_as_closeout_manifest", True)
            ),
        }
    )
    return lineage


def _closeout_prefill_exclusion_scope(
    transfer_row: Mapping[str, str],
    artifacts: Sequence[Mapping[str, str]],
    reference_paths: Sequence[str],
) -> str:
    group = str(transfer_row.get("stale_downstream_group", ""))
    return (
        "Prefill only. Reviewer must confirm whether "
        f"{len(artifacts)} candidate `{group}` artifacts are stale/non-evidence "
        f"for row `{transfer_row.get('invalidation_row_id', '')}` and resolve "
        f"{len(reference_paths)} current claim-text references before copying "
        "this row into the main closeout record."
    )


def _gap_status(
    row: Mapping[str, str],
    field: str,
    *,
    passing_values: set[str],
) -> str:
    value = str(row.get(field, "")).strip()
    if value in passing_values:
        return "no_gap_detected"
    if not value:
        return f"{field}_missing"
    return f"{field}_{value}"


def _quarantine_prefill_gap_codes(row: Mapping[str, str]) -> list[str]:
    gaps: list[str] = []
    if str(row.get("actual_disposition", "")) != "marked_non_evidence":
        gaps.append("actual_disposition_not_confirmed")
    if str(row.get("closeout_status", "")) != "closed_invalidation_only":
        gaps.append("closeout_status_not_closed")
    if str(row.get("rerun_result", "")) not in {"pass", "not_applicable"}:
        gaps.append("rerun_not_passed")
    if str(row.get("audit_result", "")) not in {"pass", "not_applicable"}:
        gaps.append("audit_not_passed")
    if str(row.get("targeted_test_result", "")) not in {"pass", "not_applicable"}:
        gaps.append("targeted_test_not_passed")
    if str(row.get("claim_boundary_review_result", "")) not in {
        "pass",
        "not_applicable",
    }:
        gaps.append("claim_boundary_review_missing")
    if str(row.get("reviewer_signoff_status", "")) != (
        "signed_off_for_invalidation_closeout_only"
    ):
        gaps.append("reviewer_signoff_missing")
    if str(row.get("can_clear_invalidation_gate", "")) != "true":
        gaps.append("main_closeout_copy_required")
    return gaps


def _artifact_records_equivalent(
    left: Sequence[Mapping[str, Any]],
    right: Sequence[Mapping[str, Any]],
) -> bool:
    def normalize(items: Sequence[Mapping[str, Any]]) -> list[str]:
        return sorted(json.dumps(dict(item), sort_keys=True) for item in items)

    return normalize(left) == normalize(right)


def _dict_csv_text(
    rows: Sequence[Mapping[str, str]],
    fieldnames: Sequence[str],
) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: row.get(field, "") for field in fieldnames})
    return buffer.getvalue()


def _zip_candidate_detail(path: Path, pattern: str) -> str:
    try:
        with zipfile.ZipFile(path) as archive:
            names = sorted(archive.namelist())
    except (OSError, zipfile.BadZipFile) as exc:
        return f"glob={pattern}; zip_member_scan_error={exc}"
    sample = ", ".join(names[:5])
    if len(names) > 5:
        sample += f", ... +{len(names) - 5} more"
    return f"glob={pattern}; zip_members={len(names)}; sample={sample}"


def _iter_claim_text_files(project_root: Path, search_roots: Sequence[str]) -> Iterable[Path]:
    for root_item in search_roots:
        path = project_root / root_item
        if path.is_file():
            if _is_claim_text_file(path):
                yield path
            continue
        if not path.is_dir():
            continue
        for child in path.rglob("*"):
            if child.is_file() and _is_claim_text_file(child):
                yield child


def _is_claim_text_file(path: Path) -> bool:
    if path.suffix.lower() not in QUARANTINE_TEXT_SUFFIXES:
        return False
    try:
        if path.stat().st_size > 2_000_000:
            return False
    except OSError:
        return False
    return True


def _truncate(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 3] + "..."


def _parse_artifact_json_array(value: str, *, row_index: int, field: str) -> list[Any]:
    if not value.strip():
        return []
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"closeout row {row_index} has invalid JSON in {field}: {exc}"
        ) from exc
    if not isinstance(parsed, list):
        raise ValueError(f"closeout row {row_index} field {field} must be a JSON array")
    for item in parsed:
        if not isinstance(item, dict):
            raise ValueError(
                f"closeout row {row_index} field {field} items must be JSON objects"
            )
        path = str(item.get("path", ""))
        sha = str(item.get("sha256", ""))
        if path and sha and len(sha) != 64:
            raise ValueError(
                f"closeout row {row_index} field {field} has non-SHA256 hash for {path}"
            )
    return parsed


def _counts(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = value or "unknown"
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def _quarantine_scope_markdown_detail(row: Mapping[str, str]) -> str:
    """Return a claim-safe Markdown detail while preserving full CSV evidence."""

    detail = str(row.get("matched_detail", ""))
    if str(row.get("finding_type", "")) != "reference_hit":
        return detail
    if "; excerpt=" not in detail:
        return detail
    line_and_pattern, _excerpt = detail.split("; excerpt=", 1)
    return f"{line_and_pattern}; excerpt omitted; see CSV evidence row"
