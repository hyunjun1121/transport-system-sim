"""Audit road-class override evidence readiness."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

from src.realworld.road_overrides import load_road_class_overrides


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROAD_CLASS_OVERRIDE_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "road_class_overrides.csv"
)
DEFAULT_ROAD_CLASS_OVERRIDE_DRAFT_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "road_class_overrides_draft.csv"
)
DEFAULT_ACCEPTED_PILOT_MANIFEST_PATH = (
    PROJECT_ROOT / "results" / "realworld_pilot" / "pilot_full_manifest.json"
)

STRONG_SOURCE_CLASSES: frozenset[str] = frozenset(
    {
        "public-data-derived",
        "literature-derived",
        "agency/timetable-derived",
        "benchmark-calibrated",
    }
)


def audit_road_class_override_evidence(
    path: str | Path = DEFAULT_ROAD_CLASS_OVERRIDE_PATH,
    *,
    draft_path: str | Path = DEFAULT_ROAD_CLASS_OVERRIDE_DRAFT_PATH,
) -> dict[str, Any]:
    """Return conservative readiness for optional road-class override evidence."""

    override_path = Path(path)
    if not override_path.exists():
        draft = _draft_summary(Path(draft_path))
        return {
            "publication_ready": False,
            "path": _display_path(override_path),
            "override_table_present": False,
            "row_count": 0,
            **draft,
            "claim_boundary": (
                "Road-class override evidence is absent. The mapper still uses "
                "built-in fallback speed, capacity, and base-disruption proxies."
            ),
            "remaining_blockers": [
                _missing_override_blocker(draft),
                "apply the reviewed overrides when adapting the pilot graph if final claims require calibrated road inputs",
            ],
        }

    overrides = load_road_class_overrides(override_path)
    source_counts = Counter(override.source_class for override in overrides)
    weak_rows = [
        override
        for override in overrides
        if override.source_class not in STRONG_SOURCE_CLASSES
    ]
    return {
        "publication_ready": not weak_rows,
        "path": _display_path(override_path),
        "override_table_present": True,
        "row_count": len(overrides),
        "highway_classes": sorted({override.highway for override in overrides}),
        "source_class_counts": dict(sorted(source_counts.items())),
        "weak_row_count": len(weak_rows),
        "weak_highway_classes": sorted({override.highway for override in weak_rows}),
        "claim_boundary": (
            "This audit checks override-table source strength only. It does not "
            "prove the overrides were applied to a result graph or calibrated "
            "against observed traffic."
        ),
        "remaining_blockers": _blockers(weak_rows),
    }


def audit_road_class_override_application(
    *,
    override_path: str | Path = DEFAULT_ROAD_CLASS_OVERRIDE_PATH,
    manifest_path: str | Path = DEFAULT_ACCEPTED_PILOT_MANIFEST_PATH,
) -> dict[str, Any]:
    """Return whether an accepted pilot manifest used the reviewed overrides."""

    override_file = Path(override_path)
    manifest_file = Path(manifest_path)
    blockers: list[str] = []
    if not override_file.exists():
        blockers.append("reviewed road-class override table is absent")
    if not manifest_file.exists():
        blockers.append("accepted pilot result manifest is absent")

    if blockers:
        return {
            "publication_ready": False,
            "override_path": _display_path(override_file),
            "manifest_path": _display_path(manifest_file),
            "override_table_present": override_file.exists(),
            "manifest_present": manifest_file.exists(),
            "overrides_applied": False,
            "sha256_matches": False,
            "claim_boundary": (
                "Road-calibration claims require both reviewed override "
                "evidence and an accepted result manifest proving those "
                "overrides were applied."
            ),
            "remaining_blockers": blockers,
        }

    manifest = _load_manifest(manifest_file)
    inputs = manifest.get("inputs", {})
    if not isinstance(inputs, dict):
        inputs = {}

    applied = bool(manifest.get("road_class_overrides_applied", False))
    manifest_override_path = str(inputs.get("road_class_overrides_path") or "")
    manifest_override_sha = str(inputs.get("road_class_overrides_sha256") or "")
    expected_sha = _file_sha256(override_file)
    sha_matches = manifest_override_sha.lower() == expected_sha.lower()
    path_matches = _manifest_path_matches(manifest_override_path, override_file)
    graph_source_records_override = "road_class_overrides:" in str(
        manifest.get("graph_source", "")
    )

    if not applied:
        blockers.append("accepted pilot manifest does not record road_class_overrides_applied: true")
    if not manifest_override_path:
        blockers.append("accepted pilot manifest does not record road_class_overrides_path")
    elif not path_matches:
        blockers.append("accepted pilot manifest road_class_overrides_path does not match the reviewed table")
    if not manifest_override_sha:
        blockers.append("accepted pilot manifest does not record road_class_overrides_sha256")
    elif not sha_matches:
        blockers.append("accepted pilot manifest road_class_overrides_sha256 does not match the reviewed table")
    if not graph_source_records_override:
        blockers.append("accepted pilot manifest graph_source does not record road_class_overrides")

    return {
        "publication_ready": not blockers,
        "override_path": _display_path(override_file),
        "manifest_path": _display_path(manifest_file),
        "override_table_present": True,
        "manifest_present": True,
        "overrides_applied": applied,
        "manifest_override_path": manifest_override_path,
        "manifest_override_sha256": manifest_override_sha,
        "expected_override_sha256": expected_sha,
        "path_matches": path_matches,
        "sha256_matches": sha_matches,
        "graph_source_records_override": graph_source_records_override,
        "claim_boundary": (
            "This audit checks whether a result manifest records actual use of "
            "the reviewed road-class override table. It does not calibrate "
            "traffic assignment or validate observed operations."
        ),
        "remaining_blockers": blockers,
    }


def _blockers(weak_rows: list[object]) -> list[str]:
    blockers: list[str] = []
    if weak_rows:
        blockers.append(
            "replace expert-assumption or sensitivity-only road override rows with public, literature, agency, or benchmark-calibrated evidence"
        )
    blockers.append(
        "verify graph-adapter runs apply the reviewed override table before using road-calibration claims"
    )
    return blockers


def _draft_summary(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "draft_table_present": False,
            "draft_path": _display_path(path),
            "draft_row_count": 0,
            "draft_source_class_counts": {},
            "draft_claim_boundary": (
                "No draft road-class override worksheet is present."
            ),
        }
    overrides = load_road_class_overrides(path)
    source_counts = Counter(override.source_class for override in overrides)
    return {
        "draft_table_present": True,
        "draft_path": _display_path(path),
        "draft_row_count": len(overrides),
        "draft_highway_classes": sorted({override.highway for override in overrides}),
        "draft_source_class_counts": dict(sorted(source_counts.items())),
        "draft_claim_boundary": (
            "The draft override table is a reviewer worksheet populated with "
            "current mapper defaults. It is not reviewed road evidence and "
            "does not close publication-readiness gates."
        ),
    }


def _missing_override_blocker(draft: dict[str, Any]) -> str:
    if draft.get("draft_table_present"):
        return (
            "replace the draft road-class override worksheet with a reviewed "
            "road_class_overrides.csv table containing source-backed speed, "
            "capacity, and base-disruption evidence"
        )
    return (
        "create a reviewed road-class override table for speed, capacity, "
        "and base-disruption evidence"
    )


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _load_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _manifest_path_matches(manifest_path: str, override_path: Path) -> bool:
    if not manifest_path:
        return False
    manifest_file = Path(manifest_path)
    if not manifest_file.is_absolute():
        manifest_file = PROJECT_ROOT / manifest_file
    try:
        return manifest_file.resolve() == override_path.resolve()
    except OSError:
        return False


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


__all__ = [
    "DEFAULT_ROAD_CLASS_OVERRIDE_PATH",
    "DEFAULT_ROAD_CLASS_OVERRIDE_DRAFT_PATH",
    "DEFAULT_ACCEPTED_PILOT_MANIFEST_PATH",
    "STRONG_SOURCE_CLASSES",
    "audit_road_class_override_application",
    "audit_road_class_override_evidence",
]
