"""Diagnostics for reviewing scaffold Morris sensitivity outputs.

This module does not accept sensitivity results for final-study claims. It only
surfaces structural counts, missing or non-finite Morris index values, and
claim-scope warnings so a reviewer can make an explicit review decision.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from collections.abc import Iterable
from typing import Any, Mapping

from src.realworld.sensitivity import (
    DEFAULT_MORRIS_MANIFEST_PATH,
    DEFAULT_MORRIS_SUMMARY_PATH,
    MORRIS_SUMMARY_COLUMNS,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MORRIS_INDEX_COLUMNS: tuple[str, ...] = ("mu", "mu_star", "sigma", "mu_star_conf")
UNAVAILABLE_INDEX_STATUSES: frozenset[str] = frozenset(
    {"unavailable_nonfinite_metric_outputs"}
)


def audit_morris_sensitivity_diagnostics(
    *,
    summary_path: str | Path = DEFAULT_MORRIS_SUMMARY_PATH,
    manifest_path: str | Path = DEFAULT_MORRIS_MANIFEST_PATH,
) -> dict[str, Any]:
    """Return review diagnostics for current Morris sensitivity artifacts."""

    summary_file = Path(summary_path)
    manifest_file = Path(manifest_path)
    structural_blockers: list[str] = []
    if not summary_file.exists():
        structural_blockers.append("Morris summary CSV is missing")
    if not manifest_file.exists():
        structural_blockers.append("Morris manifest JSON is missing")
    if structural_blockers:
        return _missing_result(summary_file, manifest_file, structural_blockers)

    rows, fieldnames = _read_summary_rows(summary_file)
    manifest = _read_manifest(manifest_file)
    missing_columns = [
        column for column in MORRIS_SUMMARY_COLUMNS if column not in set(fieldnames)
    ]
    if missing_columns:
        structural_blockers.append(
            "Morris summary missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    manifest_count = _int_or_none(manifest.get("summary_row_count"))
    if manifest_count is not None and manifest_count != len(rows):
        structural_blockers.append(
            "Morris summary row count does not match manifest: "
            f"{len(rows)} != {manifest_count}"
        )

    expected_from_manifest = _expected_summary_count(manifest)
    if expected_from_manifest is not None and expected_from_manifest != len(rows):
        structural_blockers.append(
            "Morris summary row count does not match manifest dimensions: "
            f"{len(rows)} != {expected_from_manifest}"
        )

    index_issue_counts = _index_issue_counts(rows, include_unavailable=False)
    all_index_issue_counts = _index_issue_counts(rows, include_unavailable=True)
    rows_with_index_issues = _rows_with_index_issues(rows, include_unavailable=False)
    all_rows_with_index_issues = _rows_with_index_issues(rows, include_unavailable=True)
    unavailable_index_row_count = _unavailable_index_row_count(rows)
    unavailable_index_status_counts = _counts(
        row.get("index_status", "")
        for row in rows
        if _is_unavailable_index_row(row)
    )
    zero_mu_star_count = _zero_mu_star_count(rows)
    review_items = _review_items(
        manifest=manifest,
        index_issue_counts=index_issue_counts,
        rows_with_index_issues=rows_with_index_issues,
        unavailable_index_row_count=unavailable_index_row_count,
        zero_mu_star_count=zero_mu_star_count,
    )

    return {
        "diagnostics_ready": not structural_blockers,
        "path": _display_path(summary_file),
        "manifest_path": _display_path(manifest_file),
        "summary_present": True,
        "manifest_present": True,
        "row_count": len(rows),
        "manifest_summary_row_count": manifest_count,
        "expected_summary_row_count_from_manifest_dimensions": expected_from_manifest,
        "metric_count": _unique_count(rows, "metric"),
        "policy_count": _unique_count(rows, "policy_id"),
        "scenario_count": _unique_count(rows, "scenario_id"),
        "parameter_count": _unique_count(rows, "parameter_id"),
        "index_issue_counts": index_issue_counts,
        "all_index_issue_counts": all_index_issue_counts,
        "rows_with_index_issues": rows_with_index_issues,
        "all_rows_with_index_issues": all_rows_with_index_issues,
        "unavailable_index_row_count": unavailable_index_row_count,
        "unavailable_index_status_counts": unavailable_index_status_counts,
        "zero_mu_star_count": zero_mu_star_count,
        "analysis_graph_reduced": bool(manifest.get("analysis_graph_reduced", False)),
        "result_scope": str(manifest.get("result_scope", "")),
        "claim_boundary": (
            "This audit supports human review of Morris output quality. It does "
            "not accept sensitivity outputs for final-study claims and does not "
            "make the scaffold operational."
        ),
        "review_items": review_items,
        "remaining_blockers": structural_blockers,
    }


def _missing_result(
    summary_file: Path,
    manifest_file: Path,
    blockers: list[str],
) -> dict[str, Any]:
    return {
        "diagnostics_ready": False,
        "path": _display_path(summary_file),
        "manifest_path": _display_path(manifest_file),
        "summary_present": summary_file.exists(),
        "manifest_present": manifest_file.exists(),
        "row_count": 0,
        "index_issue_counts": {column: 0 for column in MORRIS_INDEX_COLUMNS},
        "all_index_issue_counts": {column: 0 for column in MORRIS_INDEX_COLUMNS},
        "rows_with_index_issues": 0,
        "all_rows_with_index_issues": 0,
        "unavailable_index_row_count": 0,
        "unavailable_index_status_counts": {},
        "zero_mu_star_count": 0,
        "claim_boundary": (
            "Morris diagnostics cannot run until both summary and manifest "
            "artifacts exist."
        ),
        "review_items": [],
        "remaining_blockers": blockers,
    }


def _read_summary_rows(path: Path) -> tuple[list[dict[str, str]], tuple[str, ...]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [dict(row) for row in reader]
        return rows, tuple(reader.fieldnames or ())


def _read_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _index_issue_counts(
    rows: list[Mapping[str, str]],
    *,
    include_unavailable: bool,
) -> dict[str, int]:
    return {
        column: sum(
            _row_has_index_issue(row, column, include_unavailable=include_unavailable)
            for row in rows
        )
        for column in MORRIS_INDEX_COLUMNS
    }


def _rows_with_index_issues(
    rows: list[Mapping[str, str]],
    *,
    include_unavailable: bool,
) -> int:
    return sum(
        any(
            _row_has_index_issue(
                row,
                column,
                include_unavailable=include_unavailable,
            )
            for column in MORRIS_INDEX_COLUMNS
        )
        for row in rows
    )


def _row_has_index_issue(
    row: Mapping[str, str],
    column: str,
    *,
    include_unavailable: bool,
) -> bool:
    if _is_unavailable_index_row(row) and not include_unavailable:
        return False
    return _is_missing_or_nonfinite(row.get(column, ""))


def _unavailable_index_row_count(rows: list[Mapping[str, str]]) -> int:
    return sum(_is_unavailable_index_row(row) for row in rows)


def _is_unavailable_index_row(row: Mapping[str, str]) -> bool:
    return str(row.get("index_status", "")).strip() in UNAVAILABLE_INDEX_STATUSES


def _zero_mu_star_count(rows: list[Mapping[str, str]]) -> int:
    count = 0
    for row in rows:
        if _is_unavailable_index_row(row):
            continue
        value = _optional_float(row.get("mu_star", ""))
        if value is not None and value == 0.0:
            count += 1
    return count


def _is_missing_or_nonfinite(value: object) -> bool:
    number = _optional_float(value)
    return number is None or not math.isfinite(number)


def _optional_float(value: object) -> float | None:
    text = "" if value is None else str(value).strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _expected_summary_count(manifest: Mapping[str, Any]) -> int | None:
    metrics = _list_len(manifest.get("rank_metrics"))
    policies = _list_len(manifest.get("policy_ids"))
    scenarios = _list_len(manifest.get("scenario_ids"))
    parameters = _list_len(manifest.get("parameter_ids"))
    if None in {metrics, policies, scenarios, parameters}:
        return None
    return int(metrics) * int(policies) * int(scenarios) * int(parameters)


def _list_len(value: object) -> int | None:
    return len(value) if isinstance(value, list) else None


def _int_or_none(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _unique_count(rows: list[Mapping[str, str]], column: str) -> int:
    return len({str(row.get(column, "")).strip() for row in rows if str(row.get(column, "")).strip()})


def _counts(values: Iterable[object]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value).strip()
        if not key:
            continue
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _review_items(
    *,
    manifest: Mapping[str, Any],
    index_issue_counts: Mapping[str, int],
    rows_with_index_issues: int,
    unavailable_index_row_count: int,
    zero_mu_star_count: int,
) -> list[str]:
    items: list[str] = []
    if rows_with_index_issues:
        items.append(
            "review missing or non-finite Morris index values before relying on "
            f"sensitivity outputs ({rows_with_index_issues} affected rows)"
        )
    if zero_mu_star_count:
        items.append(
            "review zero mu_star rows as potential no-variation or inactive-parameter cases "
            f"({zero_mu_star_count} rows)"
        )
    if rows_with_index_issues:
        items.append(
            "document how blank Morris indices are handled in tables, figures, and manuscript text"
        )
    if unavailable_index_row_count:
        items.append(
            "review explicitly unavailable Morris index rows caused by non-finite metric outputs "
            f"({unavailable_index_row_count} rows)"
        )
    if bool(manifest.get("analysis_graph_reduced", False)):
        items.append(
            "sensitivity outputs use the reduced analysis graph; graph-scale acceptance is still required"
        )
    scope = str(manifest.get("result_scope", "")).lower()
    if "scaffold" in scope or "not calibrated" in scope:
        items.append(
            "current result scope remains scaffold or not-calibrated; do not use as final-study evidence without formal review"
        )
    return items


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


__all__ = [
    "MORRIS_INDEX_COLUMNS",
    "audit_morris_sensitivity_diagnostics",
]
