"""Tests for fail-closed lexical claim-language guard."""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.claim_language_guard import (  # noqa: E402
    CLAIM_LANGUAGE_GUARD_COLUMNS,
    CLAIM_LANGUAGE_GUARD_SCOPE,
    build_claim_language_guard_rows,
    summarize_claim_language_guard,
    write_claim_language_guard,
)
from src.realworld.phase_gate_ledger import (  # noqa: E402
    PHASE_GATE_LEDGER_CLAIM_BOUNDARY,
)


def test_reserved_terms_without_boundary_block_release() -> None:
    with TemporaryDirectory() as directory:
        path = Path(directory) / "claims.md"
        path.write_text(
            "The operational forecast is final, approved, ready, accepted, "
            "validated, calibrated, and real-time.\n",
            encoding="utf-8",
        )
        rows = build_claim_language_guard_rows(scan_paths=[path])

    terms = {row["term"] for row in rows}
    assert {
        "operational",
        "forecast",
        "final",
        "approved",
        "ready",
        "accepted",
        "validated",
        "calibrated",
        "real-time",
    }.issubset(terms)
    assert all(row["status"] == "release_blocking_unbounded" for row in rows)

    print("PASS: unbounded reserved terms block release")


def test_explicit_non_approval_bounds_only_matching_clause() -> None:
    with TemporaryDirectory() as directory:
        path = Path(directory) / "mixed.md"
        path.write_text(
            "This is not final, but the model is operational and approved.\n",
            encoding="utf-8",
        )
        rows = build_claim_language_guard_rows(scan_paths=[path])

    by_term = {row["term"]: row["status"] for row in rows}
    assert by_term["final"] == "explicit_non_approval"
    assert by_term["operational"] == "release_blocking_unbounded"
    assert by_term["approved"] == "release_blocking_unbounded"

    print("PASS: non-approval clause does not clear separate overclaim clause")


def test_explicit_non_approval_handles_reserved_verb_forms() -> None:
    with TemporaryDirectory() as directory:
        path = Path(directory) / "morphology.md"
        path.write_text(
            "\n".join(
                [
                    "This packet does not accept or calibrate the study.",
                    "The reviewer cannot approve or validate the model.",
                    "The workflow proceeds without accepting final-study claims.",
                    "The system never validates operational forecasts.",
                    "This is not final, but the model is operational and approved.",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        rows = build_claim_language_guard_rows(scan_paths=[path])

    statuses_by_excerpt = {
        (row["excerpt"], row["term"]): row["status"] for row in rows
    }
    assert statuses_by_excerpt[
        ("This packet does not accept or calibrate the study.", "accepted")
    ] == "explicit_non_approval"
    assert statuses_by_excerpt[
        ("This packet does not accept or calibrate the study.", "calibrated")
    ] == "explicit_non_approval"
    assert statuses_by_excerpt[
        ("The reviewer cannot approve or validate the model.", "approved")
    ] == "explicit_non_approval"
    assert statuses_by_excerpt[
        ("The reviewer cannot approve or validate the model.", "validated")
    ] == "explicit_non_approval"
    assert statuses_by_excerpt[
        ("The workflow proceeds without accepting final-study claims.", "accepted")
    ] == "explicit_non_approval"
    assert statuses_by_excerpt[
        ("The system never validates operational forecasts.", "validated")
    ] == "explicit_non_approval"
    assert statuses_by_excerpt[
        ("This is not final, but the model is operational and approved.", "final")
    ] == "explicit_non_approval"
    assert statuses_by_excerpt[
        ("This is not final, but the model is operational and approved.", "operational")
    ] == "release_blocking_unbounded"
    assert statuses_by_excerpt[
        ("This is not final, but the model is operational and approved.", "approved")
    ] == "release_blocking_unbounded"

    print("PASS: reserved verb forms are bounded only by matching clause markers")


def test_explicit_non_approval_handles_negative_contractions() -> None:
    with TemporaryDirectory() as directory:
        path = Path(directory) / "negative_contractions.md"
        path.write_text(
            "\n".join(
                [
                    "This packet doesn't validate or approve the model.",
                    "This workflow won't create final acceptance.",
                    "This artifact isn't operational readiness evidence.",
                    "The simulator is operational and approved.",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        rows = build_claim_language_guard_rows(scan_paths=[path])

    statuses_by_excerpt = {
        (row["excerpt"], row["term"]): row["status"] for row in rows
    }
    assert statuses_by_excerpt[
        ("This packet doesn't validate or approve the model.", "validated")
    ] == "explicit_non_approval"
    assert statuses_by_excerpt[
        ("This packet doesn't validate or approve the model.", "approved")
    ] == "explicit_non_approval"
    assert statuses_by_excerpt[
        ("This workflow won't create final acceptance.", "final")
    ] == "explicit_non_approval"
    assert statuses_by_excerpt[
        ("This workflow won't create final acceptance.", "accepted")
    ] == "explicit_non_approval"
    assert statuses_by_excerpt[
        ("This artifact isn't operational readiness evidence.", "operational")
    ] == "explicit_non_approval"
    assert statuses_by_excerpt[
        ("This artifact isn't operational readiness evidence.", "ready")
    ] == "explicit_non_approval"
    assert statuses_by_excerpt[
        ("The simulator is operational and approved.", "operational")
    ] == "release_blocking_unbounded"
    assert statuses_by_excerpt[
        ("The simulator is operational and approved.", "approved")
    ] == "release_blocking_unbounded"

    print("PASS: negative contractions bound only matching non-approval claims")


def test_file_extension_dots_do_not_split_non_approval_clause() -> None:
    with TemporaryDirectory() as directory:
        path = Path(directory) / "generated_blockers.md"
        path.write_text(
            "parameter_acceptance.csv is missing before final claims.\n"
            "resolve graph-scale strategy-readiness blockers before graph-scale acceptance.\n"
            "The model is final and accepted.\n",
            encoding="utf-8",
        )
        rows = build_claim_language_guard_rows(scan_paths=[path])

    statuses_by_excerpt_term = {
        (row["excerpt"], row["term"]): row["status"] for row in rows
    }
    assert statuses_by_excerpt_term[
        ("parameter_acceptance.csv is missing before final claims.", "final")
    ] == "explicit_non_approval"
    assert statuses_by_excerpt_term[
        (
            "resolve graph-scale strategy-readiness blockers before graph-scale acceptance.",
            "ready",
        )
    ] == "explicit_non_approval"
    assert statuses_by_excerpt_term[
        (
            "resolve graph-scale strategy-readiness blockers before graph-scale acceptance.",
            "accepted",
        )
    ] == "explicit_non_approval"
    assert statuses_by_excerpt_term[
        ("The model is final and accepted.", "final")
    ] == "release_blocking_unbounded"
    assert statuses_by_excerpt_term[
        ("The model is final and accepted.", "accepted")
    ] == "release_blocking_unbounded"

    print("PASS: file extension dots do not split non-approval clauses")


def test_json_remaining_blockers_are_non_approval_inventory() -> None:
    with TemporaryDirectory() as directory:
        path = Path(directory) / "audit.json"
        path.write_text(
            json.dumps(
                {
                    "remaining_blockers": [
                        "replace accepted scenario evidence before final calibrated claims",
                    ],
                    "result": "The model is final and accepted.",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        rows = build_claim_language_guard_rows(scan_paths=[path])

    statuses_by_excerpt_term = {
        (row["excerpt"], row["term"]): row["status"] for row in rows
    }
    assert statuses_by_excerpt_term[
        (
            '"replace accepted scenario evidence before final calibrated claims"',
            "accepted",
        )
    ] == "explicit_non_approval"
    assert statuses_by_excerpt_term[
        (
            '"replace accepted scenario evidence before final calibrated claims"',
            "final",
        )
    ] == "explicit_non_approval"
    assert statuses_by_excerpt_term[
        (
            '"replace accepted scenario evidence before final calibrated claims"',
            "calibrated",
        )
    ] == "explicit_non_approval"
    assert statuses_by_excerpt_term[
        ('"result": "The model is final and accepted."', "final")
    ] == "release_blocking_unbounded"
    assert statuses_by_excerpt_term[
        ('"result": "The model is final and accepted."', "accepted")
    ] == "release_blocking_unbounded"

    print("PASS: JSON remaining blockers are non-approval inventory")


def test_markdown_remaining_blockers_are_non_approval_inventory() -> None:
    with TemporaryDirectory() as directory:
        path = Path(directory) / "audit.md"
        path.write_text(
            "\n".join(
                [
                    "# Audit",
                    "",
                    "## Remaining Blockers",
                    "",
                    "- replace accepted scenario evidence before final calibrated claims",
                    "",
                    "## Results",
                    "",
                    "The model is final and accepted.",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        rows = build_claim_language_guard_rows(scan_paths=[path])

    statuses_by_excerpt_term = {
        (row["excerpt"], row["term"]): row["status"] for row in rows
    }
    assert statuses_by_excerpt_term[
        (
            "- replace accepted scenario evidence before final calibrated claims",
            "accepted",
        )
    ] == "explicit_non_approval"
    assert statuses_by_excerpt_term[
        (
            "- replace accepted scenario evidence before final calibrated claims",
            "final",
        )
    ] == "explicit_non_approval"
    assert statuses_by_excerpt_term[
        (
            "- replace accepted scenario evidence before final calibrated claims",
            "calibrated",
        )
    ] == "explicit_non_approval"
    assert statuses_by_excerpt_term[
        ("The model is final and accepted.", "final")
    ] == "release_blocking_unbounded"
    assert statuses_by_excerpt_term[
        ("The model is final and accepted.", "accepted")
    ] == "release_blocking_unbounded"

    print("PASS: Markdown remaining blockers are non-approval inventory")


def test_literal_path_and_command_hits_are_bounded_non_claim_references() -> None:
    with TemporaryDirectory() as directory:
        path = Path(directory) / "inventory.md"
        path.write_text(
            "\n".join(
                [
                    "```text",
                    "data/validation/validation_strategy_readiness_manifest.json",
                    "src/realworld/validation_acceptance.py",
                    "tests/test_realworld_final_audit_acceptance.py",
                    "scripts\\write_final_audit_decision_packet.py",
                    "```",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        rows = build_claim_language_guard_rows(scan_paths=[path])

    assert rows
    assert {row["status"] for row in rows} == {"bounded_non_claim_reference"}
    assert {row["can_support_release"] for row in rows} == {"false"}

    print("PASS: literal path and command hits are bounded non-claim references")


def test_fenced_inventory_comments_are_bounded_but_overclaims_still_block() -> None:
    with TemporaryDirectory() as directory:
        path = Path(directory) / "repo_map.md"
        path.write_text(
            "\n".join(
                [
                    "```text",
                    "acceptance_records.py  # Common review-agent record schema validation",
                    "final_audit_acceptance.py # Explicit independent final-audit acceptance validation",
                    "publication_readiness.py # Aggregated final-claim readiness audit",
                    "validation.py # final operational forecast approved",
                    "The model is final and accepted.",
                    "```",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        rows = build_claim_language_guard_rows(scan_paths=[path])

    statuses_by_excerpt_term = {
        (row["excerpt"], row["term"]): row["status"] for row in rows
    }
    assert statuses_by_excerpt_term[
        (
            "acceptance_records.py # Common review-agent record schema validation",
            "validated",
        )
    ] == "bounded_non_claim_reference"
    assert statuses_by_excerpt_term[
        (
            "final_audit_acceptance.py # Explicit independent final-audit acceptance validation",
            "final",
        )
    ] == "bounded_non_claim_reference"
    assert statuses_by_excerpt_term[
        (
            "final_audit_acceptance.py # Explicit independent final-audit acceptance validation",
            "accepted",
        )
    ] == "bounded_non_claim_reference"
    assert statuses_by_excerpt_term[
        (
            "publication_readiness.py # Aggregated final-claim readiness audit",
            "ready",
        )
    ] == "bounded_non_claim_reference"
    assert statuses_by_excerpt_term[
        ("validation.py # final operational forecast approved", "final")
    ] == "bounded_non_claim_reference"
    assert statuses_by_excerpt_term[
        ("validation.py # final operational forecast approved", "operational")
    ] == "release_blocking_unbounded"
    assert statuses_by_excerpt_term[
        ("validation.py # final operational forecast approved", "forecast")
    ] == "release_blocking_unbounded"
    assert statuses_by_excerpt_term[
        ("validation.py # final operational forecast approved", "approved")
    ] == "release_blocking_unbounded"
    assert statuses_by_excerpt_term[
        ("The model is final and accepted.", "final")
    ] == "release_blocking_unbounded"
    assert statuses_by_excerpt_term[
        ("The model is final and accepted.", "accepted")
    ] == "release_blocking_unbounded"

    print("PASS: fenced inventory comments are bounded but overclaims still block")


def test_identifier_references_do_not_clear_same_line_overclaims() -> None:
    with TemporaryDirectory() as directory:
        path = Path(directory) / "mixed_identifier.md"
        path.write_text(
            "\n".join(
                [
                    "`validation.py` is listed here, but the model is operational and approved.",
                    "validation.py # final operational forecast approved",
                    "The model is `validated` and `approved`.",
                    "See `data/validation/validation_summary.md`; the model is validated and ready.",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        rows = build_claim_language_guard_rows(scan_paths=[path])

    statuses_by_excerpt_term = {
        (row["excerpt"], row["term"]): row["status"] for row in rows
    }
    assert statuses_by_excerpt_term[
        (
            "`validation.py` is listed here, but the model is operational and approved.",
            "validated",
        )
    ] == "bounded_non_claim_reference"
    assert statuses_by_excerpt_term[
        (
            "`validation.py` is listed here, but the model is operational and approved.",
            "operational",
        )
    ] == "release_blocking_unbounded"
    assert statuses_by_excerpt_term[
        (
            "`validation.py` is listed here, but the model is operational and approved.",
            "approved",
        )
    ] == "release_blocking_unbounded"
    assert statuses_by_excerpt_term[
        ("validation.py # final operational forecast approved", "validated")
    ] == "bounded_non_claim_reference"
    assert statuses_by_excerpt_term[
        ("validation.py # final operational forecast approved", "final")
    ] == "release_blocking_unbounded"
    assert statuses_by_excerpt_term[
        ("validation.py # final operational forecast approved", "operational")
    ] == "release_blocking_unbounded"
    assert statuses_by_excerpt_term[
        ("The model is `validated` and `approved`.", "validated")
    ] == "release_blocking_unbounded"
    assert statuses_by_excerpt_term[
        ("The model is `validated` and `approved`.", "approved")
    ] == "release_blocking_unbounded"
    assert statuses_by_excerpt_term[
        (
            "See `data/validation/validation_summary.md`; the model is validated and ready.",
            "validated",
        )
    ] == "release_blocking_unbounded"
    assert statuses_by_excerpt_term[
        (
            "See `data/validation/validation_summary.md`; the model is validated and ready.",
            "ready",
        )
    ] == "release_blocking_unbounded"

    print("PASS: identifier references do not clear same-line overclaims")


def test_wrapped_non_approval_clause_bounds_terms_without_clearing_new_claim() -> None:
    with TemporaryDirectory() as directory:
        path = Path(directory) / "wrapped_non_approval.md"
        path.write_text(
            "\n".join(
                [
                    "This supports only a bounded runtime claim; it does not prove",
                    "publication readiness, final-study readiness, or formal acceptance.",
                    "",
                    "The simulator is ready for final operational forecasts.",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        rows = build_claim_language_guard_rows(scan_paths=[path])

    statuses_by_excerpt_term = {
        (row["excerpt"], row["term"]): row["status"] for row in rows
    }
    wrapped_excerpt = "publication readiness, final-study readiness, or formal acceptance."
    assert statuses_by_excerpt_term[
        (wrapped_excerpt, "ready")
    ] == "explicit_non_approval"
    assert statuses_by_excerpt_term[
        (wrapped_excerpt, "final")
    ] == "explicit_non_approval"
    assert statuses_by_excerpt_term[
        (wrapped_excerpt, "accepted")
    ] == "explicit_non_approval"
    claim_excerpt = "The simulator is ready for final operational forecasts."
    assert statuses_by_excerpt_term[
        (claim_excerpt, "ready")
    ] == "release_blocking_unbounded"
    assert statuses_by_excerpt_term[
        (claim_excerpt, "final")
    ] == "release_blocking_unbounded"
    assert statuses_by_excerpt_term[
        (claim_excerpt, "operational")
    ] == "release_blocking_unbounded"
    assert statuses_by_excerpt_term[
        (claim_excerpt, "forecast")
    ] == "release_blocking_unbounded"

    print("PASS: wrapped non-approval clause bounds terms without clearing new claim")


def test_false_status_fields_are_bounded_only_when_false_or_zero() -> None:
    with TemporaryDirectory() as directory:
        path = Path(directory) / "status_fields.md"
        path.write_text(
            "\n".join(
                [
                    "`final_study_ready=false`",
                    "`publication_ready: false`",
                    "`accepted: false`",
                    "`final_study_ready=true`",
                    "`publication_ready: true`",
                    "`accepted: true`",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        rows = build_claim_language_guard_rows(scan_paths=[path])

    statuses_by_excerpt_term = {
        (row["excerpt"], row["term"]): row["status"] for row in rows
    }
    assert statuses_by_excerpt_term[
        ("`final_study_ready=false`", "final")
    ] == "explicit_non_approval"
    assert statuses_by_excerpt_term[
        ("`final_study_ready=false`", "ready")
    ] == "explicit_non_approval"
    assert statuses_by_excerpt_term[
        ("`publication_ready: false`", "ready")
    ] == "explicit_non_approval"
    assert statuses_by_excerpt_term[
        ("`accepted: false`", "accepted")
    ] == "explicit_non_approval"
    assert statuses_by_excerpt_term[
        ("`final_study_ready=true`", "final")
    ] == "release_blocking_unbounded"
    assert statuses_by_excerpt_term[
        ("`final_study_ready=true`", "ready")
    ] == "release_blocking_unbounded"
    assert statuses_by_excerpt_term[
        ("`publication_ready: true`", "ready")
    ] == "release_blocking_unbounded"
    assert statuses_by_excerpt_term[
        ("`accepted: true`", "accepted")
    ] == "release_blocking_unbounded"

    print("PASS: false status fields are bounded only when false or zero")


def test_fail_closed_phase_gate_ledgers_bound_internal_status_only() -> None:
    with TemporaryDirectory() as directory:
        path = Path(directory) / "phase_gate.json"
        path.write_text(
            json.dumps(
                {
                    "claim_boundary": PHASE_GATE_LEDGER_CLAIM_BOUNDARY,
                    "can_mark_complete": False,
                    "final_study_ready": False,
                    "status": "ready_for_review",
                    "gate_decision": "ready_for_review",
                    "decision_authority": (
                        "reviewer:gpt-5.5-xhigh-readiness-evidence"
                    ),
                    "command": "plan.md and formal acceptance modules inspected",
                    "reviewer_evidence": {
                        "review_scope": "read-only readiness review; not gate approval",
                    },
                    "findings": [
                        "Evidence is ready for review as traceability only.",
                        "Capacity values remain proxy/sensitivity-only for final claims.",
                    ],
                    "unsafe_summary": "The simulator is operational and approved.",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        rows = build_claim_language_guard_rows(scan_paths=[path])

    statuses_by_excerpt_term = {
        (row["excerpt"], row["term"]): row["status"] for row in rows
    }
    assert statuses_by_excerpt_term[
        (
            '"decision_authority": "reviewer:gpt-5.5-xhigh-readiness-evidence",',
            "ready",
        )
    ] == "explicit_non_approval"
    assert statuses_by_excerpt_term[
        ('"command": "plan.md and formal acceptance modules inspected",', "accepted")
    ] == "explicit_non_approval"
    assert statuses_by_excerpt_term[
        (
            '"review_scope": "read-only readiness review; not gate approval"',
            "ready",
        )
    ] == "explicit_non_approval"
    assert statuses_by_excerpt_term[
        ('"Evidence is ready for review as traceability only.",', "ready")
    ] == "explicit_non_approval"
    assert statuses_by_excerpt_term[
        (
            '"Capacity values remain proxy/sensitivity-only for final claims."',
            "final",
        )
    ] == "explicit_non_approval"
    assert statuses_by_excerpt_term[
        ('"unsafe_summary": "The simulator is operational and approved."', "operational")
    ] == "release_blocking_unbounded"
    assert statuses_by_excerpt_term[
        ('"unsafe_summary": "The simulator is operational and approved."', "approved")
    ] == "release_blocking_unbounded"

    print("PASS: fail-closed phase-gate ledgers bound internal status only")


def test_literal_reference_does_not_clear_neighboring_context() -> None:
    with TemporaryDirectory() as directory:
        path = Path(directory) / "neighboring.md"
        path.write_text(
            "`data/validation/validation_summary.md`\n"
            "The system is operational and approved.\n",
            encoding="utf-8",
        )
        rows = build_claim_language_guard_rows(scan_paths=[path])

    statuses_by_excerpt_term = {
        (row["excerpt"], row["term"]): row["status"] for row in rows
    }
    assert statuses_by_excerpt_term[
        ("`data/validation/validation_summary.md`", "validated")
    ] == "bounded_non_claim_reference"
    assert statuses_by_excerpt_term[
        ("The system is operational and approved.", "operational")
    ] == "release_blocking_unbounded"
    assert statuses_by_excerpt_term[
        ("The system is operational and approved.", "approved")
    ] == "release_blocking_unbounded"

    print("PASS: literal references do not clear neighboring prose")


def test_formal_context_does_not_override_non_approval() -> None:
    with TemporaryDirectory() as directory:
        path = Path(directory) / "formal_boundary.md"
        path.write_text(
            "This audit is not final acceptance evidence.\n"
            "This packet does not create formal acceptance.\n",
            encoding="utf-8",
        )
        rows = build_claim_language_guard_rows(scan_paths=[path])

    assert rows
    assert {row["status"] for row in rows} == {"explicit_non_approval"}

    print("PASS: formal context does not override explicit non-approval")


def test_missing_and_invalid_json_targets_are_fail_closed() -> None:
    with TemporaryDirectory() as directory:
        base = Path(directory)
        missing = base / "missing.md"
        invalid_json = base / "bad.json"
        invalid_json.write_text('{"publication_ready": tru', encoding="utf-8")

        rows = build_claim_language_guard_rows(scan_paths=[missing, invalid_json])

    statuses = {row["status"] for row in rows}
    assert "missing_scan_target" in statuses
    assert "invalid_json_target" in statuses

    print("PASS: missing and invalid JSON targets fail closed")


def test_writer_outputs_manifest_and_never_approves_claims() -> None:
    with TemporaryDirectory() as directory:
        base = Path(directory)
        source = base / "claims.md"
        source.write_text(
            "This is not operational.\nThis is a final forecast.\n",
            encoding="utf-8",
        )
        rows = build_claim_language_guard_rows(scan_paths=[source])
        output = base / "claim_language_guard.csv"
        manifest = base / "claim_language_guard_manifest.json"
        doc = base / "claim_language_guard.md"
        summary = write_claim_language_guard(
            rows=rows,
            output_path=output,
            manifest_path=manifest,
            doc_path=doc,
            scan_paths=[source],
        )
        with output.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            written_rows = list(reader)
            assert tuple(reader.fieldnames or ()) == CLAIM_LANGUAGE_GUARD_COLUMNS
        written_manifest = json.loads(manifest.read_text(encoding="utf-8"))
        loaded = summarize_claim_language_guard(manifest_path=manifest)

    assert len(written_rows) == len(rows)
    assert summary["result_scope"] == CLAIM_LANGUAGE_GUARD_SCOPE
    assert summary["release_blocked"] is True
    assert summary["claims_approved"] is False
    assert summary["publication_ready"] is False
    assert summary["final_study_ready"] is False
    assert summary["can_mark_complete"] is False
    assert written_manifest["blocking_finding_count"] >= 1
    assert loaded["manifest_present"] is True
    assert loaded["can_mark_complete"] is False

    print("PASS: writer emits fail-closed guard artifacts")


if __name__ == "__main__":
    test_reserved_terms_without_boundary_block_release()
    test_explicit_non_approval_bounds_only_matching_clause()
    test_explicit_non_approval_handles_reserved_verb_forms()
    test_explicit_non_approval_handles_negative_contractions()
    test_file_extension_dots_do_not_split_non_approval_clause()
    test_json_remaining_blockers_are_non_approval_inventory()
    test_markdown_remaining_blockers_are_non_approval_inventory()
    test_literal_path_and_command_hits_are_bounded_non_claim_references()
    test_fenced_inventory_comments_are_bounded_but_overclaims_still_block()
    test_identifier_references_do_not_clear_same_line_overclaims()
    test_wrapped_non_approval_clause_bounds_terms_without_clearing_new_claim()
    test_false_status_fields_are_bounded_only_when_false_or_zero()
    test_fail_closed_phase_gate_ledgers_bound_internal_status_only()
    test_literal_reference_does_not_clear_neighboring_context()
    test_formal_context_does_not_override_non_approval()
    test_missing_and_invalid_json_targets_are_fail_closed()
    test_writer_outputs_manifest_and_never_approves_claims()
    print("\n=== REALWORLD CLAIM LANGUAGE GUARD TESTS PASSED ===")
