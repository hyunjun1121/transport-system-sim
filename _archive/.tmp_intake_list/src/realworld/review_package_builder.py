"""Build an external expert-review ZIP from the package inventory.

The builder packages repository-owned evidence for review. It is deliberately
separate from formal acceptance: a complete ZIP does not approve evidence,
validate claims, or close final-study gates.
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence
from zipfile import ZIP_DEFLATED, ZipFile

from src.realworld.manifest_timestamp import (
    preserve_generated_at_when_unchanged,
    write_json_manifest_if_changed,
    write_text_if_changed,
)
from src.realworld.review_package_inventory import (
    DEFAULT_REVIEW_PACKAGE_INVENTORY_CSV,
    DEFAULT_REVIEW_PACKAGE_INVENTORY_MANIFEST,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REVIEW_PACKAGE_ZIP = (
    PROJECT_ROOT / "review_packages" / "expert_review_package.zip"
)
DEFAULT_REVIEW_PACKAGE_BUILD_MANIFEST = (
    PROJECT_ROOT / "data" / "manifests" / "review_package_build_manifest.json"
)
DEFAULT_REVIEW_PACKAGE_BUILD_DOC = PROJECT_ROOT / "docs" / "review_package_build.md"
DEFAULT_REVIEW_PACKAGE_SIDECAR_PATHS: tuple[str, ...] = (
    "data/manifests/review_package_inventory.csv",
    "data/manifests/review_package_inventory_manifest.json",
    "docs/review_package_inventory.md",
)

REVIEW_PACKAGE_BUILD_CLAIM_BOUNDARY = (
    "This ZIP builder assembles files for external review from the package "
    "inventory. It does not validate evidence quality, approve formal "
    "acceptance records, certify calibration, or close final-study gates."
)


def build_review_package_zip(
    *,
    root: str | Path = PROJECT_ROOT,
    inventory_csv_path: str | Path = DEFAULT_REVIEW_PACKAGE_INVENTORY_CSV,
    inventory_manifest_path: str | Path = DEFAULT_REVIEW_PACKAGE_INVENTORY_MANIFEST,
    output_zip_path: str | Path = DEFAULT_REVIEW_PACKAGE_ZIP,
    build_manifest_path: str | Path = DEFAULT_REVIEW_PACKAGE_BUILD_MANIFEST,
    doc_path: str | Path = DEFAULT_REVIEW_PACKAGE_BUILD_DOC,
    include_formal_targets: bool = False,
) -> dict[str, Any]:
    """Build a review ZIP and write package-build summary artifacts."""

    project_root = Path(root)
    inventory_csv = Path(inventory_csv_path)
    inventory_manifest = Path(inventory_manifest_path)
    output_zip = Path(output_zip_path)
    build_manifest = Path(build_manifest_path)
    doc = Path(doc_path)
    rows = load_review_package_inventory_rows(inventory_csv)
    selected, excluded = select_review_package_rows(
        rows,
        include_formal_targets=include_formal_targets,
    )
    selected = _with_sidecar_rows(project_root, selected)
    missing = [
        row
        for row in selected
        if not _safe_project_file(project_root, str(row.get("path", ""))).exists()
    ]
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    if output_zip.exists():
        output_zip.unlink()
    with ZipFile(output_zip, "w", compression=ZIP_DEFLATED) as archive:
        for row in selected:
            relative = str(row.get("path", "")).strip()
            source = _safe_project_file(project_root, relative)
            if not source.exists():
                continue
            archive.write(source, arcname=relative)

    manifest = build_review_package_build_manifest(
        rows=rows,
        selected_rows=selected,
        excluded_rows=excluded,
        missing_rows=missing,
        root=project_root,
        inventory_csv_path=inventory_csv,
        inventory_manifest_path=inventory_manifest,
        output_zip_path=output_zip,
        build_manifest_path=build_manifest,
        doc_path=doc,
        include_formal_targets=include_formal_targets,
    )
    build_manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)
    preserve_generated_at_when_unchanged(manifest, build_manifest)
    write_json_manifest_if_changed(manifest, build_manifest, sort_keys=True)
    write_text_if_changed(build_review_package_build_markdown(manifest), doc)
    return manifest


def load_review_package_inventory_rows(
    inventory_csv_path: str | Path,
) -> list[dict[str, str]]:
    """Load package inventory CSV rows."""

    path = Path(inventory_csv_path)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def select_review_package_rows(
    rows: Sequence[Mapping[str, str]],
    *,
    include_formal_targets: bool = False,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Select rows for packaging and return selected/excluded row lists."""

    selected: list[dict[str, str]] = []
    excluded: list[dict[str, str]] = []
    for row in rows:
        copied = {str(key): str(value) for key, value in row.items()}
        if _is_formal_target(copied) and not include_formal_targets:
            excluded.append(copied)
            continue
        if not str(copied.get("path", "")).strip():
            excluded.append(copied)
            continue
        selected.append(copied)
    return selected, excluded


def build_review_package_build_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    selected_rows: Sequence[Mapping[str, str]],
    excluded_rows: Sequence[Mapping[str, str]],
    missing_rows: Sequence[Mapping[str, str]],
    root: str | Path = PROJECT_ROOT,
    inventory_csv_path: str | Path = DEFAULT_REVIEW_PACKAGE_INVENTORY_CSV,
    inventory_manifest_path: str | Path = DEFAULT_REVIEW_PACKAGE_INVENTORY_MANIFEST,
    output_zip_path: str | Path = DEFAULT_REVIEW_PACKAGE_ZIP,
    build_manifest_path: str | Path = DEFAULT_REVIEW_PACKAGE_BUILD_MANIFEST,
    doc_path: str | Path = DEFAULT_REVIEW_PACKAGE_BUILD_DOC,
    include_formal_targets: bool = False,
) -> dict[str, Any]:
    """Return a conservative ZIP build manifest."""

    project_root = Path(root)
    output_zip = Path(output_zip_path)
    missing_paths = [str(row.get("path", "")) for row in missing_rows]
    selected_size = sum(_int(row.get("size_bytes", "0")) for row in selected_rows)
    zip_size = output_zip.stat().st_size if output_zip.exists() else 0
    ready = bool(selected_rows) and not missing_rows and output_zip.exists()
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "claim_boundary": REVIEW_PACKAGE_BUILD_CLAIM_BOUNDARY,
        "inventory_row_count": len(rows),
        "selected_file_count": len(selected_rows),
        "excluded_file_count": len(excluded_rows),
        "excluded_formal_target_count": sum(1 for row in excluded_rows if _is_formal_target(row)),
        "missing_file_count": len(missing_rows),
        "missing_paths": missing_paths,
        "selected_size_bytes": selected_size,
        "zip_size_bytes": zip_size,
        "zip_sha256": _sha256(output_zip) if output_zip.exists() else "",
        "include_formal_targets": include_formal_targets,
        "review_package_zip_ready": ready,
        "acceptance_ready": False,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "inventory_csv": _display_path(project_root, Path(inventory_csv_path)),
            "inventory_manifest": _display_path(project_root, Path(inventory_manifest_path)),
        },
        "outputs": {
            "zip": _display_path(project_root, output_zip),
            "manifest": _display_path(project_root, Path(build_manifest_path)),
            "doc": _display_path(project_root, Path(doc_path)),
        },
        "remaining_blockers": [
            f"missing package file: {path}" for path in missing_paths
        ],
        "review_items": [
            "confirm this ZIP is the package sent to the next external reviewer",
            "send docs/review_package_build.md or the printed build manifest as a sidecar with the ZIP",
            "run scripts/write_expert_review_handoff.py --fail-on-zip-mismatch after mirroring the ZIP so Markdown and JSON checksum sidecars are recorded outside the package",
            "keep unreviewed formal acceptance targets excluded unless the reviewer explicitly asks for blocker-state files",
            "run formal acceptance artifact and evidence-path guards before sending",
            "treat ZIP completeness as package hygiene only, not evidence acceptance",
        ],
    }


def build_review_package_build_markdown(manifest: Mapping[str, Any]) -> str:
    """Return a Markdown summary for the ZIP build."""

    lines = [
        "# Review Package Build",
        "",
        str(manifest.get("claim_boundary", REVIEW_PACKAGE_BUILD_CLAIM_BOUNDARY)),
        "",
        "## Verdict",
        "",
        f"- Review package ZIP ready: `{str(manifest.get('review_package_zip_ready', False)).lower()}`",
        f"- Acceptance ready: `{str(manifest.get('acceptance_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Selected files: {manifest.get('selected_file_count', 0)}",
        f"- Excluded files: {manifest.get('excluded_file_count', 0)}",
        f"- Excluded formal targets: {manifest.get('excluded_formal_target_count', 0)}",
        f"- Missing files: {manifest.get('missing_file_count', 0)}",
        "",
        "## ZIP",
        "",
        f"- Path: `{manifest.get('outputs', {}).get('zip', '')}`",
        f"- Size bytes: {manifest.get('zip_size_bytes', 0)}",
        f"- SHA256: `{manifest.get('zip_sha256', '')}`",
        f"- Include formal targets: `{str(manifest.get('include_formal_targets', False)).lower()}`",
        "",
        "## Missing Paths",
        "",
    ]
    missing_paths = list(manifest.get("missing_paths", []))
    if missing_paths:
        for path in missing_paths:
            lines.append(f"- `{path}`")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Use",
            "",
            "Send this ZIP only with the consultation context and package "
            "inventory. It is a review handoff bundle, not an acceptance "
            "package. Formal acceptance still depends on reviewer decisions "
            "and the formal gate audits. After copying the ZIP to the mirrored "
            "review-package path, run "
            "`scripts\\write_expert_review_handoff.py --fail-on-zip-mismatch` "
            "and send `review_packages/expert_review_handoff_20260510.md` plus "
            "`review_packages/expert_review_handoff_20260510.json` outside "
            "the ZIP so checksum reporting does not mutate the package.",
            "",
        ]
    )
    return "\n".join(lines)


def _safe_project_file(project_root: Path, relative_path: str) -> Path:
    path = PurePosixPath(relative_path)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"unsafe package path: {relative_path!r}")
    return project_root / Path(*path.parts)


def _with_sidecar_rows(
    project_root: Path,
    selected_rows: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    selected = [{str(key): str(value) for key, value in row.items()} for row in selected_rows]
    existing_paths = {row.get("path", "") for row in selected}
    for relative in DEFAULT_REVIEW_PACKAGE_SIDECAR_PATHS:
        if relative in existing_paths:
            continue
        path = _safe_project_file(project_root, relative)
        if not path.exists() or not path.is_file():
            continue
        selected.append(
            {
                "path": relative,
                "size_bytes": str(path.stat().st_size),
                "sha256": _sha256(path),
                "artifact_role": "data_or_manifest" if relative.startswith("data/") else "documentation",
                "source_category": "review_aid",
                "artifact_stage": "review_aid",
                "review_package_action": "Include as package sidecar; do not treat as acceptance.",
                "is_formal_acceptance_target": "false",
                "is_draft_or_template": "false",
                "claim_boundary": REVIEW_PACKAGE_BUILD_CLAIM_BOUNDARY,
            }
        )
        existing_paths.add(relative)
    return selected


def _is_formal_target(row: Mapping[str, str]) -> bool:
    return str(row.get("is_formal_acceptance_target", "")).lower() == "true"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _display_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


__all__ = [
    "DEFAULT_REVIEW_PACKAGE_BUILD_DOC",
    "DEFAULT_REVIEW_PACKAGE_BUILD_MANIFEST",
    "DEFAULT_REVIEW_PACKAGE_SIDECAR_PATHS",
    "DEFAULT_REVIEW_PACKAGE_ZIP",
    "REVIEW_PACKAGE_BUILD_CLAIM_BOUNDARY",
    "build_review_package_build_manifest",
    "build_review_package_build_markdown",
    "build_review_package_zip",
    "load_review_package_inventory_rows",
    "select_review_package_rows",
]
