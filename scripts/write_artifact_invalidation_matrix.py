"""Write the Phase 9 artifact invalidation review matrix."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.artifact_invalidation_matrix import (  # noqa: E402
    ALLOWED_DISPOSITION_STATUSES,
    DEFAULT_ARTIFACT_INVALIDATION_ACTION_BATCH_INSPECTION,
    DEFAULT_ARTIFACT_INVALIDATION_ACTION_BATCH_INSPECTION_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_ACTION_BATCH_INSPECTION_MANIFEST,
    DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_MANIFEST,
    DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_QUEUE,
    DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_MANIFEST,
    DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_READINESS_AUDIT,
    DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_READINESS_AUDIT_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_READINESS_AUDIT_MANIFEST,
    DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_TEMPLATE,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL_GAP_AUDIT,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL_GAP_AUDIT_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL_GAP_AUDIT_MANIFEST,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL_MANIFEST,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_COPY_AUDIT,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_COPY_AUDIT_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_COPY_AUDIT_MANIFEST,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_DRAFT_OVERLAY,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_DRAFT_OVERLAY_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_DRAFT_OVERLAY_MANIFEST,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_MANIFEST,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_TEMPLATE,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLAIM_REFERENCE_REMEDIATION,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLAIM_REFERENCE_REMEDIATION_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLAIM_REFERENCE_REMEDIATION_MANIFEST,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_REFERENCE_TRIAGE,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_REFERENCE_TRIAGE_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_REFERENCE_TRIAGE_MANIFEST,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_NON_EVIDENCE_INDEX,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_NON_EVIDENCE_INDEX_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_NON_EVIDENCE_INDEX_MANIFEST,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET_MANIFEST,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_AUDIT,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_AUDIT_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_AUDIT_MANIFEST,
    DEFAULT_ARTIFACT_INVALIDATION_CSV,
    DEFAULT_ARTIFACT_INVALIDATION_DOC,
    DEFAULT_ARTIFACT_INVALIDATION_MANIFEST,
    read_artifact_invalidation_closeout_rows,
    apply_artifact_invalidation_reviewer_evidence,
    write_artifact_invalidation_action_batch_inspection,
    write_artifact_invalidation_closeout_action_queue,
    write_artifact_invalidation_closeout_rows,
    write_artifact_invalidation_closeout_readiness_audit,
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


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    if args.write_closeout_template and args.apply_reviewer_evidence_dir is not None:
        print(
            "Refusing to combine --write-closeout-template with "
            "--apply-reviewer-evidence-dir. Generate or restore the filled "
            "closeout CSV first, then apply reviewer evidence in a separate "
            "command using --apply-reviewer-evidence-closeout-input.",
            file=sys.stderr,
        )
        return 2

    rows = None
    if args.default_status:
        from src.realworld.artifact_invalidation_matrix import build_artifact_invalidation_rows

        rows = build_artifact_invalidation_rows(default_status=args.default_status)
    summary = write_artifact_invalidation_matrix(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
    )
    if args.write_closeout_template:
        closeout_summary = write_artifact_invalidation_closeout_template(
            matrix_rows=rows,
            output_path=args.closeout_output,
            manifest_path=args.closeout_manifest,
            doc_path=args.closeout_doc,
        )
        summary["closeout_template"] = closeout_summary
    if args.apply_reviewer_evidence_dir is not None:
        closeout_input = args.apply_reviewer_evidence_closeout_input or args.closeout_output
        closeout_rows = read_artifact_invalidation_closeout_rows(closeout_input)
        applied_rows, apply_summary = apply_artifact_invalidation_reviewer_evidence(
            closeout_rows,
            args.apply_reviewer_evidence_dir,
        )
        closeout_summary = write_artifact_invalidation_closeout_rows(
            applied_rows,
            output_path=args.closeout_output,
            manifest_path=args.closeout_manifest,
            doc_path=args.closeout_doc,
        )
        summary["reviewer_evidence_apply"] = apply_summary
        summary["closeout_template"] = closeout_summary
    if args.write_closeout_action_queue:
        action_summary = write_artifact_invalidation_closeout_action_queue(
            output_path=args.action_output,
            manifest_path=args.action_manifest,
            doc_path=args.action_doc,
        )
        summary["closeout_action_queue"] = action_summary
    if args.write_action_batch_inspection:
        closeout_input = args.action_batch_inspection_closeout_input
        if closeout_input is None and args.closeout_output.exists():
            closeout_input = args.closeout_output
        closeout_rows = (
            read_artifact_invalidation_closeout_rows(closeout_input)
            if closeout_input is not None
            else None
        )
        inspection_summary = write_artifact_invalidation_action_batch_inspection(
            closeout_rows=closeout_rows,
            source_closeout_path=closeout_input,
            output_path=args.action_batch_inspection_output,
            manifest_path=args.action_batch_inspection_manifest,
            doc_path=args.action_batch_inspection_doc,
        )
        summary["action_batch_inspection"] = inspection_summary
    if args.write_closeout_readiness_audit:
        closeout_input = args.closeout_readiness_closeout_input
        if closeout_input is None and args.closeout_output.exists():
            closeout_input = args.closeout_output
        closeout_rows = (
            read_artifact_invalidation_closeout_rows(closeout_input)
            if closeout_input is not None
            else None
        )
        readiness_summary = write_artifact_invalidation_closeout_readiness_audit(
            closeout_rows=closeout_rows,
            source_closeout_path=closeout_input,
            output_path=args.closeout_readiness_output,
            manifest_path=args.closeout_readiness_manifest,
            doc_path=args.closeout_readiness_doc,
        )
        summary["closeout_readiness_audit"] = readiness_summary
    if args.write_quarantine_closeout_template:
        quarantine_summary = write_artifact_invalidation_quarantine_closeout_template(
            output_path=args.quarantine_output,
            manifest_path=args.quarantine_manifest,
            doc_path=args.quarantine_doc,
        )
        summary["quarantine_closeout_template"] = quarantine_summary
    if args.write_quarantine_scope_audit:
        scope_summary = write_artifact_invalidation_quarantine_scope_audit(
            output_path=args.quarantine_scope_output,
            manifest_path=args.quarantine_scope_manifest,
            doc_path=args.quarantine_scope_doc,
        )
        summary["quarantine_scope_audit"] = scope_summary
    if args.write_quarantine_non_evidence_index:
        index_summary = write_artifact_invalidation_quarantine_non_evidence_index(
            output_path=args.quarantine_non_evidence_index_output,
            manifest_path=args.quarantine_non_evidence_index_manifest,
            doc_path=args.quarantine_non_evidence_index_doc,
            source_scope_audit_manifest=args.quarantine_scope_manifest,
            source_quarantine_template_manifest=args.quarantine_manifest,
        )
        summary["quarantine_non_evidence_index"] = index_summary
    if args.write_quarantine_non_evidence_transfer_packet:
        transfer_summary = write_artifact_invalidation_quarantine_transfer_packet(
            output_path=args.quarantine_non_evidence_transfer_output,
            manifest_path=args.quarantine_non_evidence_transfer_manifest,
            doc_path=args.quarantine_non_evidence_transfer_doc,
            source_non_evidence_index_manifest=args.quarantine_non_evidence_index_manifest,
            source_scope_audit_manifest=args.quarantine_scope_manifest,
            source_quarantine_template_manifest=args.quarantine_manifest,
        )
        summary["quarantine_non_evidence_transfer_packet"] = transfer_summary
    if args.write_quarantine_closeout_prefill:
        prefill_summary = write_artifact_invalidation_quarantine_closeout_prefill(
            output_path=args.quarantine_closeout_prefill_output,
            manifest_path=args.quarantine_closeout_prefill_manifest,
            doc_path=args.quarantine_closeout_prefill_doc,
            source_transfer_packet_manifest=args.quarantine_closeout_prefill_source_transfer_manifest,
        )
        summary["quarantine_closeout_prefill"] = prefill_summary
    if args.write_quarantine_closeout_prefill_gap_audit:
        gap_summary = write_artifact_invalidation_quarantine_closeout_prefill_gap_audit(
            output_path=args.quarantine_closeout_prefill_gap_audit_output,
            manifest_path=args.quarantine_closeout_prefill_gap_audit_manifest,
            doc_path=args.quarantine_closeout_prefill_gap_audit_doc,
            source_transfer_packet_manifest=args.quarantine_closeout_prefill_gap_audit_source_transfer_manifest,
        )
        summary["quarantine_closeout_prefill_gap_audit"] = gap_summary
    if args.write_quarantine_main_closeout_copy_audit:
        prefill_rows = (
            read_artifact_invalidation_closeout_rows(
                args.quarantine_main_closeout_copy_audit_prefill_input
            )
            if args.quarantine_main_closeout_copy_audit_prefill_input.exists()
            else None
        )
        main_closeout_input = args.quarantine_main_closeout_copy_audit_main_closeout_input
        if main_closeout_input is None and args.closeout_output.exists():
            main_closeout_input = args.closeout_output
        main_closeout_rows = (
            read_artifact_invalidation_closeout_rows(main_closeout_input)
            if main_closeout_input is not None and main_closeout_input.exists()
            else None
        )
        copy_summary = write_artifact_invalidation_quarantine_main_closeout_copy_audit(
            prefill_rows=prefill_rows,
            main_closeout_rows=main_closeout_rows,
            output_path=args.quarantine_main_closeout_copy_audit_output,
            manifest_path=args.quarantine_main_closeout_copy_audit_manifest,
            doc_path=args.quarantine_main_closeout_copy_audit_doc,
            source_prefill_path=args.quarantine_main_closeout_copy_audit_prefill_input,
            source_main_closeout_path=(
                main_closeout_input if main_closeout_input is not None else args.closeout_output
            ),
        )
        summary["quarantine_main_closeout_copy_audit"] = copy_summary
    if args.write_quarantine_main_closeout_draft_overlay:
        prefill_rows = (
            read_artifact_invalidation_closeout_rows(
                args.quarantine_main_closeout_draft_overlay_prefill_input
            )
            if args.quarantine_main_closeout_draft_overlay_prefill_input.exists()
            else None
        )
        main_closeout_input = args.quarantine_main_closeout_draft_overlay_main_closeout_input
        if main_closeout_input is None and args.closeout_output.exists():
            main_closeout_input = args.closeout_output
        main_closeout_rows = (
            read_artifact_invalidation_closeout_rows(main_closeout_input)
            if main_closeout_input is not None and main_closeout_input.exists()
            else None
        )
        overlay_summary = (
            write_artifact_invalidation_quarantine_main_closeout_draft_overlay(
                prefill_rows=prefill_rows,
                main_closeout_rows=main_closeout_rows,
                output_path=args.quarantine_main_closeout_draft_overlay_output,
                manifest_path=args.quarantine_main_closeout_draft_overlay_manifest,
                doc_path=args.quarantine_main_closeout_draft_overlay_doc,
                source_prefill_path=args.quarantine_main_closeout_draft_overlay_prefill_input,
                source_main_closeout_path=(
                    main_closeout_input if main_closeout_input is not None else args.closeout_output
                ),
            )
        )
        summary["quarantine_main_closeout_draft_overlay"] = overlay_summary
    if args.write_quarantine_reference_triage:
        triage_summary = write_artifact_invalidation_quarantine_reference_triage(
            output_path=args.quarantine_reference_triage_output,
            manifest_path=args.quarantine_reference_triage_manifest,
            doc_path=args.quarantine_reference_triage_doc,
            source_transfer_packet_manifest=args.quarantine_reference_triage_source_transfer_manifest,
        )
        summary["quarantine_reference_triage"] = triage_summary
    if args.write_quarantine_claim_reference_remediation_packet:
        remediation_summary = (
            write_artifact_invalidation_quarantine_claim_reference_remediation_packet(
                output_path=args.quarantine_claim_reference_remediation_output,
                manifest_path=args.quarantine_claim_reference_remediation_manifest,
                doc_path=args.quarantine_claim_reference_remediation_doc,
                source_reference_triage_manifest=(
                    args.quarantine_claim_reference_remediation_source_triage_manifest
                ),
                source_scope_audit_manifest=(
                    args.quarantine_claim_reference_remediation_source_scope_manifest
                ),
            )
        )
        summary["quarantine_claim_reference_remediation_packet"] = remediation_summary
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.fail_on_blockers and summary["blocking_row_count"] > 0:
        return 1
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write the Phase 9 artifact invalidation matrix. Outputs are "
            "review support only and do not regenerate artifacts."
        )
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_CSV,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_MANIFEST,
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_DOC,
    )
    parser.add_argument(
        "--default-status",
        choices=sorted(ALLOWED_DISPOSITION_STATUSES),
        default="stale_pending_disposition",
        help="Disposition status to assign to generated matrix rows.",
    )
    parser.add_argument(
        "--fail-on-blockers",
        action="store_true",
        help="Return exit code 1 when unresolved stale rows remain.",
    )
    parser.add_argument(
        "--write-closeout-template",
        action="store_true",
        help="Also write the pending artifact invalidation closeout worksheet.",
    )
    parser.add_argument(
        "--closeout-output",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_TEMPLATE,
    )
    parser.add_argument(
        "--closeout-manifest",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_MANIFEST,
    )
    parser.add_argument(
        "--closeout-doc",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_DOC,
    )
    parser.add_argument(
        "--apply-reviewer-evidence-dir",
        type=Path,
        default=None,
        help=(
            "Directory containing artifact_invalidation_closeout_reviewer_evidence "
            "JSON files. Matching records are hash-linked into --closeout-output "
            "only when they pass fail-closed validation."
        ),
    )
    parser.add_argument(
        "--apply-reviewer-evidence-closeout-input",
        type=Path,
        default=None,
        help=(
            "Filled closeout CSV to update when applying reviewer evidence. "
            "If omitted, --closeout-output is read."
        ),
    )
    parser.add_argument(
        "--write-closeout-action-queue",
        action="store_true",
        help="Also write the dependency-ordered closeout action queue.",
    )
    parser.add_argument(
        "--action-output",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_QUEUE,
    )
    parser.add_argument(
        "--action-manifest",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_MANIFEST,
    )
    parser.add_argument(
        "--action-doc",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_ACTION_DOC,
    )
    parser.add_argument(
        "--write-action-batch-inspection",
        action="store_true",
        help=(
            "Also write a non-closeout inspection that merges action batches "
            "with closeout-readiness gaps."
        ),
    )
    parser.add_argument(
        "--action-batch-inspection-closeout-input",
        type=Path,
        default=None,
        help=(
            "Filled closeout CSV to inspect. If omitted, the command reads "
            "--closeout-output when that file already exists; otherwise it "
            "inspects a default pending template."
        ),
    )
    parser.add_argument(
        "--action-batch-inspection-output",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_ACTION_BATCH_INSPECTION,
    )
    parser.add_argument(
        "--action-batch-inspection-manifest",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_ACTION_BATCH_INSPECTION_MANIFEST,
    )
    parser.add_argument(
        "--action-batch-inspection-doc",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_ACTION_BATCH_INSPECTION_DOC,
    )
    parser.add_argument(
        "--write-closeout-readiness-audit",
        action="store_true",
        help=(
            "Also write a non-acceptance closeout evidence-gap audit. This "
            "does not close artifact invalidation rows."
        ),
    )
    parser.add_argument(
        "--closeout-readiness-closeout-input",
        type=Path,
        default=None,
        help=(
            "Filled closeout CSV to audit. If omitted, the command reads "
            "--closeout-output when that file already exists; otherwise it "
            "audits a default pending template."
        ),
    )
    parser.add_argument(
        "--closeout-readiness-output",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_READINESS_AUDIT,
    )
    parser.add_argument(
        "--closeout-readiness-manifest",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_READINESS_AUDIT_MANIFEST,
    )
    parser.add_argument(
        "--closeout-readiness-doc",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_CLOSEOUT_READINESS_AUDIT_DOC,
    )
    parser.add_argument(
        "--write-quarantine-closeout-template",
        action="store_true",
        help=(
            "Also write the pending closeout worksheet for the immediate "
            "non-evidence quarantine batch."
        ),
    )
    parser.add_argument(
        "--quarantine-output",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_TEMPLATE,
    )
    parser.add_argument(
        "--quarantine-manifest",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_MANIFEST,
    )
    parser.add_argument(
        "--quarantine-doc",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_DOC,
    )
    parser.add_argument(
        "--write-quarantine-scope-audit",
        action="store_true",
        help=(
            "Also write the non-acceptance finding-row scope/citation audit "
            "for the immediate quarantine batch."
        ),
    )
    parser.add_argument(
        "--quarantine-scope-output",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_AUDIT,
    )
    parser.add_argument(
        "--quarantine-scope-manifest",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_AUDIT_MANIFEST,
    )
    parser.add_argument(
        "--quarantine-scope-doc",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_AUDIT_DOC,
    )
    parser.add_argument(
        "--write-quarantine-non-evidence-index",
        action="store_true",
        help=(
            "Also write a deduped non-closeout index of stale full-output and "
            "review-package candidates for the immediate quarantine batch."
        ),
    )
    parser.add_argument(
        "--quarantine-non-evidence-index-output",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_NON_EVIDENCE_INDEX,
    )
    parser.add_argument(
        "--quarantine-non-evidence-index-manifest",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_NON_EVIDENCE_INDEX_MANIFEST,
    )
    parser.add_argument(
        "--quarantine-non-evidence-index-doc",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_NON_EVIDENCE_INDEX_DOC,
    )
    parser.add_argument(
        "--write-quarantine-non-evidence-transfer-packet",
        action="store_true",
        help=(
            "Also write a non-closeout row-level handoff packet for the "
            "immediate quarantine non-evidence batch."
        ),
    )
    parser.add_argument(
        "--quarantine-non-evidence-transfer-output",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET,
    )
    parser.add_argument(
        "--quarantine-non-evidence-transfer-manifest",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET_MANIFEST,
    )
    parser.add_argument(
        "--quarantine-non-evidence-transfer-doc",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET_DOC,
    )
    parser.add_argument(
        "--write-quarantine-closeout-prefill",
        action="store_true",
        help=(
            "Also write a closeout-schema prefill worksheet from the immediate "
            "quarantine transfer packet. This remains pending and cannot close "
            "artifact invalidation rows."
        ),
    )
    parser.add_argument(
        "--quarantine-closeout-prefill-output",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL,
    )
    parser.add_argument(
        "--quarantine-closeout-prefill-manifest",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL_MANIFEST,
    )
    parser.add_argument(
        "--quarantine-closeout-prefill-doc",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL_DOC,
    )
    parser.add_argument(
        "--quarantine-closeout-prefill-source-transfer-manifest",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET_MANIFEST,
        help=(
            "Source quarantine transfer-packet manifest to record in the "
            "prefill lineage summary."
        ),
    )
    parser.add_argument(
        "--write-quarantine-closeout-prefill-gap-audit",
        action="store_true",
        help=(
            "Also write a non-closing reviewer-action gap audit for the "
            "quarantine closeout prefill."
        ),
    )
    parser.add_argument(
        "--quarantine-closeout-prefill-gap-audit-output",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL_GAP_AUDIT,
    )
    parser.add_argument(
        "--quarantine-closeout-prefill-gap-audit-manifest",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL_GAP_AUDIT_MANIFEST,
    )
    parser.add_argument(
        "--quarantine-closeout-prefill-gap-audit-doc",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL_GAP_AUDIT_DOC,
    )
    parser.add_argument(
        "--quarantine-closeout-prefill-gap-audit-source-transfer-manifest",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET_MANIFEST,
        help=(
            "Source quarantine transfer-packet manifest to record in the "
            "prefill gap-audit lineage summary."
        ),
    )
    parser.add_argument(
        "--write-quarantine-main-closeout-copy-audit",
        action="store_true",
        help=(
            "Also write a non-closing audit comparing quarantine prefill rows "
            "with the separate main closeout record."
        ),
    )
    parser.add_argument(
        "--quarantine-main-closeout-copy-audit-output",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_COPY_AUDIT,
    )
    parser.add_argument(
        "--quarantine-main-closeout-copy-audit-manifest",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_COPY_AUDIT_MANIFEST,
    )
    parser.add_argument(
        "--quarantine-main-closeout-copy-audit-doc",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_COPY_AUDIT_DOC,
    )
    parser.add_argument(
        "--quarantine-main-closeout-copy-audit-prefill-input",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL,
        help="Quarantine closeout prefill CSV to compare against the main closeout record.",
    )
    parser.add_argument(
        "--quarantine-main-closeout-copy-audit-main-closeout-input",
        type=Path,
        default=None,
        help=(
            "Main closeout CSV to audit. If omitted, the command reads "
            "--closeout-output when that file exists; otherwise it audits the "
            "default pending main closeout template."
        ),
    )
    parser.add_argument(
        "--write-quarantine-main-closeout-draft-overlay",
        action="store_true",
        help=(
            "Also write a non-authoritative closeout-schema draft overlay "
            "that places quarantine prefill rows into the main closeout row "
            "order while keeping all rows pending."
        ),
    )
    parser.add_argument(
        "--quarantine-main-closeout-draft-overlay-output",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_DRAFT_OVERLAY,
    )
    parser.add_argument(
        "--quarantine-main-closeout-draft-overlay-manifest",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_DRAFT_OVERLAY_MANIFEST,
    )
    parser.add_argument(
        "--quarantine-main-closeout-draft-overlay-doc",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_MAIN_CLOSEOUT_DRAFT_OVERLAY_DOC,
    )
    parser.add_argument(
        "--quarantine-main-closeout-draft-overlay-prefill-input",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLOSEOUT_PREFILL,
        help="Quarantine closeout prefill CSV to overlay onto the main closeout row order.",
    )
    parser.add_argument(
        "--quarantine-main-closeout-draft-overlay-main-closeout-input",
        type=Path,
        default=None,
        help=(
            "Main closeout CSV to use for row order. If omitted, the command "
            "reads --closeout-output when that file exists; otherwise it uses "
            "the default pending main closeout template."
        ),
    )
    parser.add_argument(
        "--write-quarantine-reference-triage",
        action="store_true",
        help=(
            "Also write a non-closing triage audit for current quarantine "
            "reference-hit paths."
        ),
    )
    parser.add_argument(
        "--quarantine-reference-triage-output",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_REFERENCE_TRIAGE,
    )
    parser.add_argument(
        "--quarantine-reference-triage-manifest",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_REFERENCE_TRIAGE_MANIFEST,
    )
    parser.add_argument(
        "--quarantine-reference-triage-doc",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_REFERENCE_TRIAGE_DOC,
    )
    parser.add_argument(
        "--quarantine-reference-triage-source-transfer-manifest",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_TRANSFER_PACKET_MANIFEST,
        help=(
            "Source quarantine transfer-packet manifest to record in the "
            "reference triage lineage summary."
        ),
    )
    parser.add_argument(
        "--write-quarantine-claim-reference-remediation-packet",
        action="store_true",
        help=(
            "Also write a non-closing line-level remediation packet for "
            "review-first quarantine reference-hit paths."
        ),
    )
    parser.add_argument(
        "--quarantine-claim-reference-remediation-output",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLAIM_REFERENCE_REMEDIATION,
    )
    parser.add_argument(
        "--quarantine-claim-reference-remediation-manifest",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLAIM_REFERENCE_REMEDIATION_MANIFEST,
    )
    parser.add_argument(
        "--quarantine-claim-reference-remediation-doc",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_CLAIM_REFERENCE_REMEDIATION_DOC,
    )
    parser.add_argument(
        "--quarantine-claim-reference-remediation-source-triage-manifest",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_REFERENCE_TRIAGE_MANIFEST,
        help=(
            "Source quarantine reference-triage manifest to record in the "
            "line-level remediation packet lineage summary."
        ),
    )
    parser.add_argument(
        "--quarantine-claim-reference-remediation-source-scope-manifest",
        type=Path,
        default=DEFAULT_ARTIFACT_INVALIDATION_QUARANTINE_SCOPE_AUDIT_MANIFEST,
        help=(
            "Source quarantine scope-audit manifest to record in the "
            "line-level remediation packet lineage summary."
        ),
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
