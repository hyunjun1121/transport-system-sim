"""Tests for the expert-review handoff sidecar."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.review_package_handoff import (  # noqa: E402
    build_expert_review_handoff_markdown,
    build_expert_review_handoff_summary,
    write_expert_review_handoff,
)


def test_expert_review_handoff_records_zip_identity_without_packaging_it() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        package = root / "required_deliverables.zip"
        mirror = root / "review_packages" / "expert_review_package.zip"
        previous = root / "review_packages" / "original.zip"
        build_doc = root / "docs" / "review_package_build.md"
        path_audit_doc = root / "docs" / "review_package_path_audit.md"
        consultation_request = root / "docs" / "expert_consultation_request.md"
        mirror.parent.mkdir(parents=True)
        build_doc.parent.mkdir(parents=True)
        _write_zip(package)
        mirror.write_bytes(package.read_bytes())
        previous.write_bytes(b"old\n")
        build_doc.write_text("build\n", encoding="utf-8")
        path_audit_doc.write_text("path audit\n", encoding="utf-8")
        consultation_request.write_text("request\n", encoding="utf-8")
        build_manifest = root / "data" / "manifests" / "review_package_build_manifest.json"
        build_manifest.parent.mkdir(parents=True)
        build_manifest.write_text(
            json.dumps({"selected_file_count": 1, "zip_sha256": "placeholder"}),
            encoding="utf-8",
        )
        summary = build_expert_review_handoff_summary(
            root=root,
            zip_path=package,
            mirror_zip_path=mirror,
            previous_zip_path=previous,
            build_doc_path=build_doc,
            path_audit_doc_path=path_audit_doc,
            consultation_request_path=consultation_request,
            build_manifest_path=build_manifest,
            handoff_date="2026-05-10",
        )
        markdown = build_expert_review_handoff_markdown(summary)
    assert summary["zip"]["file_count"] == 1
    assert summary["mirror_zip"]["matches_zip"] is True
    assert len(summary["file_identities"]) == 4
    assert all(record["present"] for record in summary["file_identities"])
    assert summary["formal_status"]["missing_formal_target_count"] == 12
    assert "not an acceptance package" in markdown
    assert "required_deliverables.zip" in markdown
    assert "File Identities" in markdown


def test_write_expert_review_handoff_outputs_markdown() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        package = root / "required_deliverables.zip"
        mirror = root / "review_packages" / "expert_review_package.zip"
        previous = root / "review_packages" / "original.zip"
        output = root / "review_packages" / "handoff.md"
        manifest = root / "review_packages" / "handoff.json"
        build_doc = root / "docs" / "review_package_build.md"
        path_audit_doc = root / "docs" / "review_package_path_audit.md"
        consultation_request = root / "docs" / "expert_consultation_request.md"
        mirror.parent.mkdir(parents=True)
        build_doc.parent.mkdir(parents=True)
        _write_zip(package)
        mirror.write_bytes(package.read_bytes())
        previous.write_bytes(b"old\n")
        build_doc.write_text("build\n", encoding="utf-8")
        path_audit_doc.write_text("path audit\n", encoding="utf-8")
        consultation_request.write_text("request\n", encoding="utf-8")
        summary = write_expert_review_handoff(
            root=root,
            zip_path=package,
            mirror_zip_path=mirror,
            previous_zip_path=previous,
            build_doc_path=build_doc,
            path_audit_doc_path=path_audit_doc,
            consultation_request_path=consultation_request,
            output_path=output,
            manifest_path=manifest,
            handoff_date="2026-05-10",
        )
        exists = output.exists()
        manifest_exists = manifest.exists()
        text = output.read_text(encoding="utf-8")
        loaded = json.loads(manifest.read_text(encoding="utf-8"))
    assert exists
    assert manifest_exists
    assert summary["outputs"]["doc"].endswith("handoff.md")
    assert summary["outputs"]["manifest"].endswith("handoff.json")
    assert loaded["zip"]["sha256"] == summary["zip"]["sha256"]
    assert "SHA256" in text
    assert summary["zip"]["sha256"] in text
    assert "review_package_build.md" in text
    assert "handoff.json" in text


def _write_zip(path: Path) -> None:
    with ZipFile(path, "w") as archive:
        archive.writestr("README.md", "readme\n")


if __name__ == "__main__":
    test_expert_review_handoff_records_zip_identity_without_packaging_it()
    test_write_expert_review_handoff_outputs_markdown()
    print("PASS: review package handoff")
