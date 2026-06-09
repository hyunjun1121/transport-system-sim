"""Tests for source-context raw-file hash audit."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.source_context_hash_audit import (  # noqa: E402
    DEFAULT_SOURCE_CONTEXT_HASH_AUDIT_DOC_PATH,
    DEFAULT_SOURCE_CONTEXT_HASH_AUDIT_MANIFEST_PATH,
    SOURCE_CONTEXT_HASH_AUDIT_SCOPE,
    build_source_context_hash_audit,
    write_source_context_hash_audit,
)
from scripts import audit_source_context_hashes as audit_script  # noqa: E402


def test_source_context_hash_audit_classifies_current_cached_sources() -> None:
    """Current KTDB and Metro9 source contexts should pass hash integrity only."""

    manifest = build_source_context_hash_audit()

    assert manifest["result_scope"] == SOURCE_CONTEXT_HASH_AUDIT_SCOPE
    assert manifest["generated_at_utc"]
    assert manifest["row_count"] == 3
    assert manifest["source_count"] == 2
    assert manifest["raw_file_count"] == 3
    assert manifest["source_context_count"] == 2
    assert manifest["raw_file_integrity_ready"] is True
    assert manifest["raw_file_integrity_ready_count"] == 2
    assert manifest["raw_file_integrity_blocker_count"] == 0
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["can_support_rail_evidence_gate"] is False
    assert manifest["can_support_final_provenance_gate"] is False
    assert manifest["provenance_gate_closure_candidate_count"] == 0
    assert manifest["rail_evidence_gate_closure_candidate_count"] == 0
    assert manifest["remaining_hash_blockers"] == []
    assert manifest["remaining_gate_blockers"]
    by_id = {row["source_id"]: row for row in manifest["sources"]}
    assert set(by_id) == {
        "ktdb_gtfs_source_context",
        "metro9_capacity_source_context",
    }
    assert "ktdb_gtfs_source_extract.csv" in by_id[
        "ktdb_gtfs_source_context"
    ]["extract_path"]
    assert "metro9_capacity_source_raw.html" in "; ".join(
        by_id["metro9_capacity_source_context"]["raw_paths"]
    )
    file_records = manifest["file_records"]
    assert len(file_records) == 3
    assert {record["sha256_matches"] for record in file_records} == {True}
    assert all(record["recorded_sha256"] for record in file_records)
    assert all(record["computed_sha256"] for record in file_records)

    print("PASS: source-context hash audit classifies current cached sources")


def test_source_context_hash_audit_writer_outputs_manifest_and_doc() -> None:
    """Writer should emit stable manifest and Markdown review support."""

    with TemporaryDirectory() as directory:
        root = Path(directory)
        manifest_path = root / "source_context_hash_audit.json"
        doc_path = root / "source_context_hash_audit.md"
        manifest = write_source_context_hash_audit(
            manifest_path=manifest_path,
            doc_path=doc_path,
        )
        written = json.loads(manifest_path.read_text(encoding="utf-8"))
        doc = doc_path.read_text(encoding="utf-8")

    assert written == manifest
    assert "Source Context Hash Audit" in doc
    assert "Raw-file integrity ready: `true`" in doc
    assert "Publication ready: `false`" in doc
    assert "Can support final provenance gate: `false`" in doc
    assert "Recorded SHA256" in doc
    assert "not provenance gate closure" in manifest["result_scope"]

    print("PASS: source-context hash audit writer emits manifest and doc")


def test_source_context_hash_audit_script_writes_default_outputs() -> None:
    """CLI should write the shipped default manifest and Markdown audit."""

    exit_code = audit_script.main([])

    assert exit_code == 0
    assert DEFAULT_SOURCE_CONTEXT_HASH_AUDIT_MANIFEST_PATH.exists()
    assert DEFAULT_SOURCE_CONTEXT_HASH_AUDIT_DOC_PATH.exists()
    manifest = json.loads(
        DEFAULT_SOURCE_CONTEXT_HASH_AUDIT_MANIFEST_PATH.read_text(
            encoding="utf-8"
        )
    )
    assert manifest["raw_file_integrity_ready"] is True
    assert manifest["publication_ready"] is False
    assert manifest["can_mark_complete"] is False
    assert manifest["can_support_rail_evidence_gate"] is False
    assert manifest["can_support_final_provenance_gate"] is False

    print("PASS: source-context hash audit script writes default outputs")


if __name__ == "__main__":
    test_source_context_hash_audit_classifies_current_cached_sources()
    test_source_context_hash_audit_writer_outputs_manifest_and_doc()
    test_source_context_hash_audit_script_writes_default_outputs()
    print("\n=== REALWORLD SOURCE CONTEXT HASH AUDIT TESTS PASSED ===")
