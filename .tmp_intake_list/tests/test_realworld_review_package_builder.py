"""Tests for expert-review ZIP builder."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys
import tempfile
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.review_package_builder import (  # noqa: E402
    build_review_package_build_markdown,
    build_review_package_zip,
    select_review_package_rows,
)


def test_select_review_package_rows_excludes_formal_targets_by_default() -> None:
    rows = [
        _row("README.md"),
        _row("data/manifests/pilot_acceptance.json", formal=True),
    ]
    selected, excluded = select_review_package_rows(rows)
    assert [row["path"] for row in selected] == ["README.md"]
    assert [row["path"] for row in excluded] == [
        "data/manifests/pilot_acceptance.json"
    ]


def test_build_review_package_zip_excludes_formal_targets_by_default() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "data" / "manifests").mkdir(parents=True)
        (root / "docs").mkdir()
        (root / "README.md").write_text("readme\n", encoding="utf-8")
        (root / "data" / "manifests" / "review_package_inventory_manifest.json").write_text(
            "{}\n",
            encoding="utf-8",
        )
        (root / "docs" / "review_package_inventory.md").write_text(
            "# Inventory\n",
            encoding="utf-8",
        )
        formal = root / "data" / "manifests" / "pilot_acceptance.json"
        formal.write_text('{"accepted": false}\n', encoding="utf-8")
        inventory = root / "inventory.csv"
        _write_inventory(inventory, [_row("README.md"), _row("data/manifests/pilot_acceptance.json", formal=True)])
        summary = build_review_package_zip(
            root=root,
            inventory_csv_path=inventory,
            inventory_manifest_path=root / "inventory.json",
            output_zip_path=root / "package.zip",
            build_manifest_path=root / "build.json",
            doc_path=root / "build.md",
        )
        with ZipFile(root / "package.zip") as archive:
            names = set(archive.namelist())
    assert summary["review_package_zip_ready"] is True
    assert summary["excluded_formal_target_count"] == 1
    assert "README.md" in names
    assert "docs/review_package_inventory.md" in names
    assert "data/manifests/review_package_inventory_manifest.json" in names
    assert "data/manifests/pilot_acceptance.json" not in names


def test_build_review_package_zip_can_include_formal_targets() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "data" / "manifests").mkdir(parents=True)
        (root / "README.md").write_text("readme\n", encoding="utf-8")
        formal = root / "data" / "manifests" / "pilot_acceptance.json"
        formal.write_text('{"accepted": false}\n', encoding="utf-8")
        inventory = root / "inventory.csv"
        _write_inventory(inventory, [_row("README.md"), _row("data/manifests/pilot_acceptance.json", formal=True)])
        summary = build_review_package_zip(
            root=root,
            inventory_csv_path=inventory,
            inventory_manifest_path=root / "inventory.json",
            output_zip_path=root / "package.zip",
            build_manifest_path=root / "build.json",
            doc_path=root / "build.md",
            include_formal_targets=True,
        )
        with ZipFile(root / "package.zip") as archive:
            names = set(archive.namelist())
        loaded = json.loads((root / "build.json").read_text(encoding="utf-8"))
    assert summary["excluded_formal_target_count"] == 0
    assert "data/manifests/pilot_acceptance.json" in names
    assert loaded["zip_sha256"]


def test_build_review_package_zip_reports_missing_files() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        inventory = root / "inventory.csv"
        _write_inventory(inventory, [_row("missing.txt")])
        summary = build_review_package_zip(
            root=root,
            inventory_csv_path=inventory,
            inventory_manifest_path=root / "inventory.json",
            output_zip_path=root / "package.zip",
            build_manifest_path=root / "build.json",
            doc_path=root / "build.md",
        )
    assert summary["review_package_zip_ready"] is False
    assert summary["missing_file_count"] == 1
    assert summary["remaining_blockers"] == ["missing package file: missing.txt"]
    assert any(
        "write_expert_review_handoff.py" in item
        for item in summary["review_items"]
    )
    markdown = build_review_package_build_markdown(summary)
    assert "write_expert_review_handoff.py" in markdown
    assert "expert_review_handoff_20260510.json" in markdown


def _row(path: str, *, formal: bool = False) -> dict[str, str]:
    return {
        "path": path,
        "size_bytes": "1",
        "sha256": "abc",
        "artifact_role": "documentation",
        "source_category": "supporting_documentation",
        "artifact_stage": "formal_target" if formal else "supporting_artifact",
        "review_package_action": "include",
        "is_formal_acceptance_target": str(formal).lower(),
        "is_draft_or_template": "false",
        "claim_boundary": "test",
    }


def _write_inventory(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    test_select_review_package_rows_excludes_formal_targets_by_default()
    test_build_review_package_zip_excludes_formal_targets_by_default()
    test_build_review_package_zip_can_include_formal_targets()
    test_build_review_package_zip_reports_missing_files()
    print("PASS: review package builder")
