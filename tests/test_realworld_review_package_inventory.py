"""Tests for external-review package inventory generation."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.review_package_inventory import (  # noqa: E402
    build_review_package_inventory_rows,
    summarize_review_package_inventory_rows,
    write_review_package_inventory,
)


def test_review_package_inventory_classifies_core_files() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _write_required_fixture(root)
        (root / "src" / "realworld").mkdir(parents=True)
        (root / "src" / "realworld" / "example.py").write_text("x = 1\n", encoding="utf-8")
        (root / "docs" / "review_packet.md").write_text("# Packet\n", encoding="utf-8")
        (root / "data" / "cache").mkdir(parents=True)
        (root / "data" / "cache" / "snapshot.graphml").write_text("g\n", encoding="utf-8")
        rows = build_review_package_inventory_rows(root=root)
    by_path = {row["path"]: row for row in rows}
    assert by_path["src/realworld/example.py"]["artifact_role"] == "source_code"
    assert by_path["docs/review_packet.md"]["artifact_stage"] == "review_aid"
    assert by_path["data/cache/snapshot.graphml"]["source_category"] == (
        "cached_source_snapshot"
    )
    assert by_path["main.py"]["sha256"]


def test_review_package_inventory_excludes_reference_and_self_outputs() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _write_required_fixture(root)
        (root / "cloned_repo").mkdir()
        (root / "cloned_repo" / "README.md").write_text("reference\n", encoding="utf-8")
        (root / "data" / "manifests").mkdir(parents=True, exist_ok=True)
        (root / "data" / "manifests" / "review_package_inventory.csv").write_text(
            "self\n",
            encoding="utf-8",
        )
        (root / "data" / "manifests" / "review_package_closeout_20260609.zip").write_text(
            "zip\n",
            encoding="utf-8",
        )
        (root / "review_packages").mkdir()
        (root / "review_packages" / "expert_review_package.zip").write_text(
            "zip\n",
            encoding="utf-8",
        )
        rows = build_review_package_inventory_rows(root=root)
    paths = {row["path"] for row in rows}
    assert "cloned_repo/README.md" not in paths
    assert "data/manifests/review_package_inventory.csv" not in paths
    assert "data/manifests/review_package_closeout_20260609.zip" not in paths
    assert "review_packages/expert_review_package.zip" not in paths


def test_review_package_inventory_summary_reports_missing_required_groups() -> None:
    rows = [
        {
            "path": "README.md",
            "size_bytes": "1",
            "artifact_role": "documentation",
            "source_category": "supporting_documentation",
            "artifact_stage": "supporting_artifact",
            "is_formal_acceptance_target": "false",
            "is_draft_or_template": "false",
        }
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "README.md").write_text("readme\n", encoding="utf-8")
        summary = summarize_review_package_inventory_rows(rows, root=root)
    assert summary["missing_required_group_count"] > 0
    assert summary["review_package_inventory_ready"] is False
    assert summary["remaining_blockers"]


def test_write_review_package_inventory_outputs_files() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _write_required_fixture(root)
        summary = write_review_package_inventory(
            root=root,
            output_path=root / "data" / "manifests" / "inventory.csv",
            manifest_path=root / "data" / "manifests" / "inventory.json",
            doc_path=root / "docs" / "inventory.md",
        )
        loaded = json.loads(
            (root / "data" / "manifests" / "inventory.json").read_text(
                encoding="utf-8"
            )
        )
        by_group = {row["group_id"]: row for row in loaded["required_groups"]}
        assert loaded["row_count"] == summary["row_count"]
        assert loaded["review_package_inventory_ready"] is True
        assert loaded["can_mark_complete"] is False
        assert by_group["agent_instructions"]["matched_path"] == "agents.md"
        assert (root / "data" / "manifests" / "inventory.csv").exists()
        text = (root / "docs" / "inventory.md").read_text(encoding="utf-8")
        assert "Review Package Inventory" in text
        assert "does not prove that evidence is sufficient" in text


def _write_required_fixture(root: Path) -> None:
    for directory in ("src", "scripts", "tests", "data", "docs", "paper", "results"):
        (root / directory).mkdir(parents=True, exist_ok=True)
        (root / directory / ".keep").write_text("keep\n", encoding="utf-8")
    for name in (
        "README.md",
        "agents.md",
        "plan.md",
        "status.md",
        "IMPLEMENTATION_PLAN.md",
        "main.py",
        "config.yaml",
        "requirements.txt",
    ):
        (root / name).write_text(f"{name}\n", encoding="utf-8")


if __name__ == "__main__":
    test_review_package_inventory_classifies_core_files()
    test_review_package_inventory_excludes_reference_and_self_outputs()
    test_review_package_inventory_summary_reports_missing_required_groups()
    test_write_review_package_inventory_outputs_files()
    print("PASS: review package inventory")
