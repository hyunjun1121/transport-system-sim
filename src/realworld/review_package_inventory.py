"""Review-package inventory for external expert handoff.

This inventory checks that a review package can expose the repository-owned
implementation, evidence, results, and documentation needed for expert review.
It is package hygiene only and never approves evidence or closes final-study
gates.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.formal_evidence_path_audit import FORMAL_ARTIFACT_RELATIVE_PATHS
from src.realworld.manifest_timestamp import (
    preserve_generated_at_when_unchanged,
    write_json_manifest_if_changed,
    write_text_if_changed,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REVIEW_PACKAGE_INVENTORY_CSV = (
    PROJECT_ROOT / "data" / "manifests" / "review_package_inventory.csv"
)
DEFAULT_REVIEW_PACKAGE_INVENTORY_MANIFEST = (
    PROJECT_ROOT / "data" / "manifests" / "review_package_inventory_manifest.json"
)
DEFAULT_REVIEW_PACKAGE_INVENTORY_DOC = PROJECT_ROOT / "docs" / "review_package_inventory.md"

REVIEW_PACKAGE_CLAIM_BOUNDARY = (
    "This inventory checks package completeness and file traceability for "
    "external review. It does not validate evidence quality, approve formal "
    "acceptance records, certify calibration, or close final-study gates."
)
REVIEW_PACKAGE_FIELDS: tuple[str, ...] = (
    "path",
    "size_bytes",
    "sha256",
    "artifact_role",
    "source_category",
    "artifact_stage",
    "review_package_action",
    "is_formal_acceptance_target",
    "is_draft_or_template",
    "claim_boundary",
)
PACKAGE_INCLUDE_DIRS: tuple[str, ...] = (
    "agents",
    "data",
    "docs",
    "paper",
    "results",
    "schemas",
    "scripts",
    "src",
    "tests",
)
PACKAGE_ROOT_FILES: tuple[str, ...] = (
    "README.md",
    "agents.md",
    "AGENTS.md",
    "IMPLEMENTATION_PLAN.md",
    "plan.md",
    "status.md",
    "main.py",
    "config.yaml",
    "requirements.txt",
    "generate_report.py",
    "report_draft.md",
    "report.docx",
    "cloned_repo_manifest.md",
    ".gitignore",
)
REQUIRED_PATH_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("readme", ("README.md",)),
    ("agent_instructions", ("AGENTS.md", "agents.md")),
    ("plan", ("plan.md",)),
    ("status", ("status.md",)),
    ("implementation_plan", ("IMPLEMENTATION_PLAN.md",)),
    ("main_entrypoint", ("main.py",)),
    ("config", ("config.yaml",)),
    ("requirements", ("requirements.txt",)),
    ("source_tree", ("src",)),
    ("script_tree", ("scripts",)),
    ("test_tree", ("tests",)),
    ("data_tree", ("data",)),
    ("docs_tree", ("docs",)),
    ("paper_tree", ("paper",)),
    ("results_tree", ("results",)),
)
EXCLUDED_DIR_NAMES: frozenset[str] = frozenset(
    {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "cloned_repo",
        "refs",
    }
)
SELF_OUTPUT_PATHS: frozenset[str] = frozenset(
    {
        "data/manifests/review_package_inventory.csv",
        "data/manifests/review_package_inventory_manifest.json",
        "data/manifests/review_package_build_manifest.json",
        "data/manifests/review_package_path_audit.json",
        "docs/review_package_inventory.md",
        "docs/review_package_build.md",
        "docs/review_package_path_audit.md",
    }
)
REVIEW_PACKAGE_ARCHIVE_PATHS: frozenset[str] = frozenset(
    {
        "review_packages/expert_review_package.zip",
        "data/manifests/review_package_closeout_20260609.zip",
    }
)
FORMAL_TARGET_PATHS: frozenset[str] = frozenset(
    set(FORMAL_ARTIFACT_RELATIVE_PATHS)
    | {
        "docs/final_study_audit.md",
    }
)


@dataclass(frozen=True)
class ReviewPackageInventoryRow:
    """One file that should be considered for the expert review package."""

    path: str
    size_bytes: int
    sha256: str
    artifact_role: str
    source_category: str
    artifact_stage: str
    review_package_action: str
    is_formal_acceptance_target: bool
    is_draft_or_template: bool
    claim_boundary: str = REVIEW_PACKAGE_CLAIM_BOUNDARY

    def to_csv_row(self) -> dict[str, str]:
        return {
            "path": self.path,
            "size_bytes": str(self.size_bytes),
            "sha256": self.sha256,
            "artifact_role": self.artifact_role,
            "source_category": self.source_category,
            "artifact_stage": self.artifact_stage,
            "review_package_action": self.review_package_action,
            "is_formal_acceptance_target": str(self.is_formal_acceptance_target).lower(),
            "is_draft_or_template": str(self.is_draft_or_template).lower(),
            "claim_boundary": self.claim_boundary,
        }


def build_review_package_inventory_rows(
    *,
    root: str | Path = PROJECT_ROOT,
) -> list[dict[str, str]]:
    """Return review-package inventory rows for repository-owned artifacts."""

    project_root = Path(root)
    rows: list[ReviewPackageInventoryRow] = []
    for path in _iter_package_files(project_root):
        relative = _display_path(project_root, path)
        if relative in SELF_OUTPUT_PATHS or _is_review_package_archive(relative):
            continue
        role = _artifact_role(relative)
        stage = _artifact_stage(relative)
        rows.append(
            ReviewPackageInventoryRow(
                path=relative,
                size_bytes=path.stat().st_size,
                sha256=_sha256(path),
                artifact_role=role,
                source_category=_source_category(relative, role, stage),
                artifact_stage=stage,
                review_package_action=_review_package_action(relative, stage),
                is_formal_acceptance_target=relative in FORMAL_TARGET_PATHS,
                is_draft_or_template=stage == "draft_or_template",
            )
        )
    return [row.to_csv_row() for row in sorted(rows, key=lambda item: item.path)]


def write_review_package_inventory(
    *,
    root: str | Path = PROJECT_ROOT,
    rows: Sequence[Mapping[str, str]] | None = None,
    output_path: str | Path = DEFAULT_REVIEW_PACKAGE_INVENTORY_CSV,
    manifest_path: str | Path = DEFAULT_REVIEW_PACKAGE_INVENTORY_MANIFEST,
    doc_path: str | Path = DEFAULT_REVIEW_PACKAGE_INVENTORY_DOC,
) -> dict[str, Any]:
    """Write CSV, JSON, and Markdown review-package inventory artifacts."""

    project_root = Path(root)
    inventory_rows = (
        list(rows)
        if rows is not None
        else build_review_package_inventory_rows(root=project_root)
    )
    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REVIEW_PACKAGE_FIELDS)
        writer.writeheader()
        writer.writerows(inventory_rows)

    summary = summarize_review_package_inventory_rows(
        inventory_rows,
        root=project_root,
    )
    summary.update(
        {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "claim_boundary": REVIEW_PACKAGE_CLAIM_BOUNDARY,
            "outputs": {
                "csv": _display_path(project_root, output),
                "manifest": _display_path(project_root, manifest),
                "doc": _display_path(project_root, doc),
            },
            "excluded_directories": sorted(EXCLUDED_DIR_NAMES),
            "self_output_paths": sorted(SELF_OUTPUT_PATHS),
            "can_mark_complete": False,
        }
    )
    preserve_generated_at_when_unchanged(summary, manifest)
    write_json_manifest_if_changed(summary, manifest, sort_keys=True)
    write_text_if_changed(
        build_review_package_inventory_markdown(summary, inventory_rows),
        doc,
    )
    return summary


def summarize_review_package_inventory(
    manifest_path: str | Path = DEFAULT_REVIEW_PACKAGE_INVENTORY_MANIFEST,
) -> dict[str, Any]:
    """Return a compact summary of the last written review-package inventory."""

    path = Path(manifest_path)
    if not path.exists():
        return {
            "manifest_present": False,
            "path": _display_path(PROJECT_ROOT, path),
            "row_count": 0,
            "review_package_inventory_ready": False,
            "can_mark_complete": False,
            "remaining_blockers": ["run scripts/write_review_package_inventory.py"],
        }
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return {
        "manifest_present": True,
        "path": _display_path(PROJECT_ROOT, path),
        "row_count": int(value.get("row_count", 0)),
        "total_size_bytes": int(value.get("total_size_bytes", 0)),
        "missing_required_group_count": int(value.get("missing_required_group_count", 0)),
        "formal_target_present_count": int(value.get("formal_target_present_count", 0)),
        "draft_or_template_count": int(value.get("draft_or_template_count", 0)),
        "review_package_inventory_ready": bool(
            value.get("review_package_inventory_ready", False)
        ),
        "can_mark_complete": bool(value.get("can_mark_complete", False)),
        "remaining_blockers": list(value.get("remaining_blockers", [])),
    }


def summarize_review_package_inventory_rows(
    rows: Sequence[Mapping[str, str]],
    *,
    root: str | Path = PROJECT_ROOT,
) -> dict[str, Any]:
    """Summarize review-package inventory rows without approving acceptance."""

    project_root = Path(root)
    role_counts = _counts(row.get("artifact_role", "") for row in rows)
    source_category_counts = _counts(row.get("source_category", "") for row in rows)
    stage_counts = _counts(row.get("artifact_stage", "") for row in rows)
    total_size = sum(_int(row.get("size_bytes", "0")) for row in rows)
    formal_target_present = [
        row for row in rows if row.get("is_formal_acceptance_target") == "true"
    ]
    draft_or_template_count = sum(
        1 for row in rows if row.get("is_draft_or_template") == "true"
    )
    required_groups = _required_group_status(project_root)
    missing_required = [
        group for group in required_groups if not bool(group["present"])
    ]
    blockers = [
        f"required package group missing: {group['group_id']} ({'; '.join(group['candidate_paths'])})"
        for group in missing_required
    ]
    return {
        "row_count": len(rows),
        "total_size_bytes": total_size,
        "role_counts": role_counts,
        "source_category_counts": source_category_counts,
        "stage_counts": stage_counts,
        "formal_target_present_count": len(formal_target_present),
        "formal_target_paths_present": [row.get("path", "") for row in formal_target_present],
        "draft_or_template_count": draft_or_template_count,
        "required_groups": required_groups,
        "missing_required_group_count": len(missing_required),
        "review_package_inventory_ready": bool(rows) and not missing_required,
        "remaining_blockers": blockers,
        "review_items": [
            "confirm this inventory is used to assemble the next external review package",
            "verify formal target files are absent unless they contain real reviewer decisions",
            "run formal evidence-path and acceptance artifact guards before sending the package",
            "treat inventory completeness as package hygiene only, not evidence acceptance",
        ],
    }


def build_review_package_inventory_markdown(
    summary: Mapping[str, Any],
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Render a concise Markdown review-package inventory summary."""

    lines = [
        "# Review Package Inventory",
        "",
        str(summary.get("claim_boundary", REVIEW_PACKAGE_CLAIM_BOUNDARY)),
        "",
        "## Summary",
        "",
        f"- Review package inventory ready: `{str(summary.get('review_package_inventory_ready', False)).lower()}`",
        f"- Can mark complete: `{str(summary.get('can_mark_complete', False)).lower()}`",
        f"- Inventory rows: {summary.get('row_count', 0)}",
        f"- Total size bytes: {summary.get('total_size_bytes', 0)}",
        f"- Missing required groups: {summary.get('missing_required_group_count', 0)}",
        f"- Formal target files present: {summary.get('formal_target_present_count', 0)}",
        f"- Draft or template files present: {summary.get('draft_or_template_count', 0)}",
        "",
        "## Required Groups",
        "",
        "| Group | Present | Matched Path | Candidate Paths |",
        "| --- | --- | --- | --- |",
    ]
    for group in summary.get("required_groups", []):
        if not isinstance(group, Mapping):
            continue
        lines.append(
            "| "
            + " | ".join(
                [
                    _cell(str(group.get("group_id", ""))),
                    str(group.get("present", False)).lower(),
                    f"`{_cell(str(group.get('matched_path', '')))}`",
                    _cell("; ".join(str(item) for item in group.get("candidate_paths", []))),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Role Counts",
            "",
            "| Role | Count |",
            "| --- | --- |",
        ]
    )
    for role, count in dict(summary.get("role_counts", {})).items():
        lines.append(f"| {_cell(str(role))} | {count} |")

    lines.extend(
        [
            "",
            "## Formal Target Files Present",
            "",
        ]
    )
    formal_paths = list(summary.get("formal_target_paths_present", []))
    if formal_paths:
        for path in formal_paths:
            lines.append(f"- `{path}`")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## First Inventory Rows",
            "",
            "| Role | Stage | Size | Path |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in rows[:100]:
        lines.append(
            "| {role} | {stage} | {size} | `{path}` |".format(
                role=_cell(str(row.get("artifact_role", ""))),
                stage=_cell(str(row.get("artifact_stage", ""))),
                size=_cell(str(row.get("size_bytes", ""))),
                path=_cell(str(row.get("path", ""))),
            )
        )
    if len(rows) > 100:
        lines.append(f"| ... | ... | ... | {len(rows) - 100} additional rows in CSV |")
    if not rows:
        lines.append("| none | none | 0 | `.` |")

    lines.extend(
        [
            "",
            "## Use",
            "",
            "Use this inventory before assembling a renewed expert-review ZIP. "
            "It proves what files are available for packaging, but it does not "
            "prove that evidence is sufficient or that formal acceptance gates "
            "are closed.",
            "",
        ]
    )
    return "\n".join(lines)


def _iter_package_files(project_root: Path) -> Iterable[Path]:
    seen: set[Path] = set()
    for name in PACKAGE_ROOT_FILES:
        path = project_root / name
        if path.exists() and path.is_file():
            resolved = path.resolve()
            if resolved not in seen:
                seen.add(resolved)
                yield path
    for directory in PACKAGE_INCLUDE_DIRS:
        root = project_root / directory
        if not root.exists() or not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in EXCLUDED_DIR_NAMES for part in path.relative_to(project_root).parts):
                continue
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            yield path


def _required_group_status(project_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group_id, candidates in REQUIRED_PATH_GROUPS:
        matched = ""
        for candidate in candidates:
            actual = _existing_relative_path(project_root, candidate)
            if actual:
                matched = actual
                break
        rows.append(
            {
                "group_id": group_id,
                "present": bool(matched),
                "matched_path": matched,
                "candidate_paths": list(candidates),
            }
        )
    return rows


def _existing_relative_path(project_root: Path, relative_path: str) -> str:
    current = project_root
    actual_parts: list[str] = []
    for part in Path(relative_path).parts:
        if not current.exists() or not current.is_dir():
            return ""
        match = None
        for child in current.iterdir():
            if child.name.lower() == part.lower():
                match = child
                break
        if match is None:
            return ""
        actual_parts.append(match.name)
        current = match
    return Path(*actual_parts).as_posix() if current.exists() else ""


def _artifact_role(path: str) -> str:
    if path.startswith("src/") or path in {"main.py", "generate_report.py"}:
        return "source_code"
    if path.startswith("scripts/"):
        return "script"
    if path.startswith("tests/"):
        return "test"
    if path.startswith("schemas/"):
        return "schema"
    if path.startswith("agents/"):
        return "agent_definition"
    if path.startswith("results/"):
        return "generated_result"
    if path.startswith("paper/") or path in {"report_draft.md", "report.docx"}:
        return "paper_or_report"
    if path in {"config.yaml", "requirements.txt"}:
        return "configuration"
    if path.startswith("data/"):
        return "data_or_manifest"
    if path.startswith("docs/") or path.endswith(".md"):
        return "documentation"
    return "other"


def _artifact_stage(path: str) -> str:
    lowered = path.lower()
    if path in FORMAL_TARGET_PATHS:
        return "formal_target"
    if (
        "acceptance_templates/" in lowered
        or "draft_acceptance/" in lowered
        or lowered.endswith("_template.json")
        or "_draft" in lowered
        or "pre_review" in lowered
    ):
        return "draft_or_template"
    if any(
        token in lowered
        for token in (
            "review_packet",
            "readiness_packet",
            "decision_packet",
            "blocker_queue",
            "evidence_matrix",
        )
    ):
        return "review_aid"
    if path.startswith("results/"):
        return "generated_output"
    if path.startswith("data/cache/"):
        return "cached_input"
    if path.startswith("src/") or path.startswith("scripts/") or path.startswith("tests/"):
        return "implementation"
    return "supporting_artifact"


def _source_category(path: str, role: str, stage: str) -> str:
    if stage == "formal_target":
        return "formal_acceptance_target"
    if stage == "draft_or_template":
        return "draft_or_template"
    if stage == "review_aid":
        return "review_aid"
    if stage == "cached_input":
        return "cached_source_snapshot"
    if stage == "generated_output" or role == "generated_result":
        return "generated_output"
    if role in {"source_code", "script", "test", "configuration", "schema"}:
        return "project_owned"
    if role == "paper_or_report":
        return "narrative_report"
    return "supporting_documentation"


def _review_package_action(path: str, stage: str) -> str:
    if path in FORMAL_TARGET_PATHS:
        return (
            "Include only if this is a real reviewed decision; otherwise keep "
            "the formal target absent from the acceptance package."
        )
    if stage == "draft_or_template":
        return "Include as draft/template context only; do not treat as approval."
    if stage == "review_aid":
        return "Include as reviewer worksheet; do not treat as acceptance."
    return "Include in the next complete expert-review package when in scope."


def _is_review_package_archive(path: str) -> bool:
    """Return true for generated review-package ZIP archives."""

    if path in REVIEW_PACKAGE_ARCHIVE_PATHS:
        return True
    return path.startswith("review_packages/") and path.endswith(".zip")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _display_path(root: Path, path: str | Path) -> str:
    candidate = Path(path)
    try:
        return candidate.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return candidate.as_posix()


def _counts(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for raw in values:
        value = str(raw).strip() or "<blank>"
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def _int(value: object) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


__all__ = [
    "DEFAULT_REVIEW_PACKAGE_INVENTORY_CSV",
    "DEFAULT_REVIEW_PACKAGE_INVENTORY_DOC",
    "DEFAULT_REVIEW_PACKAGE_INVENTORY_MANIFEST",
    "PACKAGE_INCLUDE_DIRS",
    "PACKAGE_ROOT_FILES",
    "REQUIRED_PATH_GROUPS",
    "REVIEW_PACKAGE_CLAIM_BOUNDARY",
    "REVIEW_PACKAGE_FIELDS",
    "REVIEW_PACKAGE_ARCHIVE_PATHS",
    "SELF_OUTPUT_PATHS",
    "build_review_package_inventory_markdown",
    "build_review_package_inventory_rows",
    "summarize_review_package_inventory",
    "summarize_review_package_inventory_rows",
    "write_review_package_inventory",
]
