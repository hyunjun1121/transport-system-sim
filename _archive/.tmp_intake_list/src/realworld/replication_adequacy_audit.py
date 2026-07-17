"""Replication and paired-statistics adequacy audit.

The audit checks whether the generated pilot uncertainty tables are internally
consistent with the full pilot manifest. It is a review aid only; it does not
decide that 30 seeds are sufficient for tail-risk claims or approve experiment
acceptance.
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.manifest_timestamp import (
    preserve_generated_at_when_unchanged,
    write_json_manifest_if_changed,
    write_text_if_changed,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STATISTICS_MANIFEST_PATH = (
    PROJECT_ROOT
    / "results"
    / "realworld_pilot"
    / "tables"
    / "pilot_full_statistics_manifest.json"
)
DEFAULT_REPLICATION_AUDIT_CSV = (
    PROJECT_ROOT / "data" / "manifests" / "replication_adequacy_audit.csv"
)
DEFAULT_REPLICATION_AUDIT_MANIFEST = (
    PROJECT_ROOT / "data" / "manifests" / "replication_adequacy_audit_manifest.json"
)
DEFAULT_REPLICATION_AUDIT_DOC = PROJECT_ROOT / "docs" / "replication_adequacy_audit.md"

REPLICATION_AUDIT_CLAIM_BOUNDARY = (
    "This audit checks internal consistency of seed-replication and paired-delta "
    "statistics. It does not prove that the replication count is sufficient for "
    "final claims, approve a multiple-comparison procedure, validate stochastic "
    "assumptions, or close experiment acceptance."
)
REPLICATION_AUDIT_COLUMNS: tuple[str, ...] = (
    "check_id",
    "status",
    "observed",
    "expected",
    "review_action",
    "evidence_paths",
    "claim_boundary",
)


def build_replication_adequacy_rows(
    *,
    statistics_manifest_path: str | Path = DEFAULT_STATISTICS_MANIFEST_PATH,
    minimum_seed_count: int = 30,
) -> list[dict[str, str]]:
    """Return consistency and review rows for pilot statistics outputs."""

    manifest_file = Path(statistics_manifest_path)
    manifest = _load_json_object(manifest_file)
    metric_path = _project_path(manifest.get("outputs", {}).get("metric_ci", ""))
    paired_path = _project_path(manifest.get("outputs", {}).get("paired_delta_ci", ""))
    source_manifest_path = _project_path(manifest.get("source_manifest_path", ""))
    source_manifest = _load_json_object(source_manifest_path)
    metric_rows = _load_csv_rows(metric_path)
    paired_rows = _load_csv_rows(paired_path)
    seed_count = _int(source_manifest.get("scenario_policy_seed_design", {}).get("seed_count"))
    if not seed_count:
        seed_count = _int(source_manifest.get("seeds") and len(source_manifest.get("seeds", [])))
    paired_counts = [_int(row.get("paired_count")) for row in paired_rows]
    metric_counts = [_int(row.get("sample_count")) for row in metric_rows]
    baseline_ids = sorted(set(_values(paired_rows, "baseline_policy_id")))
    multiple_comparison_method = str(
        manifest.get("multiple_comparison_method", "")
        or manifest.get("multiple_comparison_procedure", "")
    ).strip()
    evidence = "; ".join(
        _display_path(path)
        for path in (manifest_file, metric_path, paired_path, source_manifest_path)
    )

    return [
        _row(
            "statistics_manifest_present",
            "pass" if manifest_file.exists() else "blocked",
            observed=_display_path(manifest_file) if manifest_file.exists() else "missing",
            expected="pilot statistics manifest exists",
            review_action="Regenerate pilot statistics before experiment review.",
            evidence_paths=_display_path(manifest_file),
        ),
        _row(
            "metric_ci_table_present",
            "pass" if metric_path.exists() else "blocked",
            observed=_display_path(metric_path) if metric_path.exists() else "missing",
            expected="metric confidence-interval CSV exists",
            review_action="Regenerate metric CI table before experiment review.",
            evidence_paths=evidence,
        ),
        _row(
            "paired_delta_table_present",
            "pass" if paired_path.exists() else "blocked",
            observed=_display_path(paired_path) if paired_path.exists() else "missing",
            expected="paired-delta confidence-interval CSV exists",
            review_action="Regenerate paired-delta table before paired policy claims.",
            evidence_paths=evidence,
        ),
        _row(
            "metric_ci_row_count_matches_manifest",
            "pass"
            if len(metric_rows) == _int(manifest.get("metric_ci_row_count"))
            else "blocked",
            observed=str(len(metric_rows)),
            expected=str(_int(manifest.get("metric_ci_row_count"))),
            review_action="Resolve metric CI row-count mismatch.",
            evidence_paths=evidence,
        ),
        _row(
            "paired_delta_row_count_matches_manifest",
            "pass"
            if len(paired_rows) == _int(manifest.get("paired_delta_ci_row_count"))
            else "blocked",
            observed=str(len(paired_rows)),
            expected=str(_int(manifest.get("paired_delta_ci_row_count"))),
            review_action="Resolve paired-delta row-count mismatch.",
            evidence_paths=evidence,
        ),
        _row(
            "paired_counts_match_seed_count",
            _count_status(paired_counts, seed_count),
            observed=_count_range(paired_counts),
            expected=f"paired_count values should not exceed seed_count {seed_count}; lower finite counts need review",
            review_action="Review zero or partial finite paired counts before interpreting affected metrics.",
            evidence_paths=evidence,
        ),
        _row(
            "metric_counts_match_seed_count",
            _count_status(metric_counts, seed_count),
            observed=_count_range(metric_counts),
            expected=f"sample_count values should not exceed seed_count {seed_count}; lower finite counts need review",
            review_action="Review zero or partial finite metric counts before interpreting affected metrics.",
            evidence_paths=evidence,
        ),
        _row(
            "baseline_policy_declared",
            "pass"
            if baseline_ids == [str(manifest.get("baseline_policy_id", ""))]
            else "blocked",
            observed=", ".join(baseline_ids) if baseline_ids else "none",
            expected=str(manifest.get("baseline_policy_id", "")),
            review_action="Confirm the formal experiment acceptance record names the baseline policy.",
            evidence_paths=evidence,
        ),
        _row(
            "replication_count_human_review",
            "needs_human_review" if seed_count >= minimum_seed_count else "blocked",
            observed=str(seed_count),
            expected=f"minimum structural seed count {minimum_seed_count}; adequacy still reviewer-decided",
            review_action=(
                "Decide whether this replication count is sufficient for each "
                "primary metric, especially tail-risk metrics."
            ),
            evidence_paths=evidence,
        ),
        _row(
            "ci_method_human_review",
            "needs_human_review" if manifest.get("ci_method") else "blocked",
            observed=str(manifest.get("ci_method", "")),
            expected="CI method declared and reviewed for sample size and metric distribution",
            review_action="Review whether normal-approximation CIs are acceptable or replace with a selected method.",
            evidence_paths=evidence,
        ),
        _row(
            "multiple_comparison_procedure",
            "needs_human_review" if multiple_comparison_method else "blocked",
            observed=multiple_comparison_method or "missing",
            expected="primary/secondary comparison procedure or exploratory boundary declared",
            review_action=(
                "Document the multiple-comparison procedure or explicitly label "
                "secondary comparisons as exploratory before final claims."
            ),
            evidence_paths=evidence,
        ),
    ]


def write_replication_adequacy_audit(
    *,
    rows: Sequence[Mapping[str, str]] | None = None,
    statistics_manifest_path: str | Path = DEFAULT_STATISTICS_MANIFEST_PATH,
    output_path: str | Path = DEFAULT_REPLICATION_AUDIT_CSV,
    audit_manifest_path: str | Path = DEFAULT_REPLICATION_AUDIT_MANIFEST,
    doc_path: str | Path = DEFAULT_REPLICATION_AUDIT_DOC,
    minimum_seed_count: int = 30,
) -> dict[str, Any]:
    """Write CSV, JSON, and Markdown replication-adequacy audit outputs."""

    audit_rows = (
        list(rows)
        if rows is not None
        else build_replication_adequacy_rows(
            statistics_manifest_path=statistics_manifest_path,
            minimum_seed_count=minimum_seed_count,
        )
    )
    output = Path(output_path)
    audit_manifest = Path(audit_manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    audit_manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REPLICATION_AUDIT_COLUMNS)
        writer.writeheader()
        writer.writerows(audit_rows)
    manifest = build_replication_adequacy_manifest(
        rows=audit_rows,
        output_path=output,
        manifest_path=audit_manifest,
        doc_path=doc,
        statistics_manifest_path=statistics_manifest_path,
    )
    preserve_generated_at_when_unchanged(manifest, audit_manifest)
    write_json_manifest_if_changed(manifest, audit_manifest, sort_keys=True)
    write_text_if_changed(build_replication_adequacy_markdown(manifest, audit_rows), doc)
    return manifest


def build_replication_adequacy_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_REPLICATION_AUDIT_CSV,
    manifest_path: str | Path = DEFAULT_REPLICATION_AUDIT_MANIFEST,
    doc_path: str | Path = DEFAULT_REPLICATION_AUDIT_DOC,
    statistics_manifest_path: str | Path = DEFAULT_STATISTICS_MANIFEST_PATH,
) -> dict[str, Any]:
    """Return a conservative replication audit manifest."""

    status_counts = _counts(row.get("status", "") for row in rows)
    blockers = [row for row in rows if row.get("status", "").startswith("blocked")]
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "claim_boundary": REPLICATION_AUDIT_CLAIM_BOUNDARY,
        "row_count": len(rows),
        "status_counts": status_counts,
        "blocking_check_count": len(blockers),
        "needs_human_review_count": status_counts.get("needs_human_review", 0),
        "paired_statistics_structurally_ready": len(blockers) == 0,
        "acceptance_ready": False,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "statistics_manifest": _display_path(Path(statistics_manifest_path)),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "remaining_blockers": [
            f"{row.get('check_id', '')}: {row.get('review_action', '')}"
            for row in blockers
        ],
        "review_items": [
            "review whether 30 seeds are adequate for primary metrics and tail-risk metrics",
            "document primary/secondary comparisons and multiple-comparison handling",
            "keep paired statistics in scaffold scope until graph/input/experiment acceptance gates close",
        ],
    }


def build_replication_adequacy_markdown(
    manifest: Mapping[str, Any],
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return a human-readable replication audit."""

    lines = [
        "# Replication Adequacy Audit",
        "",
        str(manifest.get("claim_boundary", REPLICATION_AUDIT_CLAIM_BOUNDARY)),
        "",
        "## Verdict",
        "",
        f"- Paired statistics structurally ready: `{str(manifest.get('paired_statistics_structurally_ready', False)).lower()}`",
        f"- Acceptance ready: `{str(manifest.get('acceptance_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Blocking checks: {manifest.get('blocking_check_count', 0)}",
        f"- Human-review checks: {manifest.get('needs_human_review_count', 0)}",
        "",
        "## Checks",
        "",
        "| Check | Status | Observed | Expected | Review Action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {check} | {status} | {observed} | {expected} | {action} |".format(
                check=_cell(row.get("check_id", "")),
                status=_cell(row.get("status", "")),
                observed=_cell(row.get("observed", "")),
                expected=_cell(row.get("expected", "")),
                action=_cell(row.get("review_action", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Use",
            "",
            "Use this audit with the seed-stream manifest, CRN pairing audit, "
            "and experiment package review before accepting paired policy "
            "statistics. A structurally complete table is not evidence that "
            "replication count, CI method, or comparison handling is adequate.",
            "",
        ]
    )
    return "\n".join(lines)


def _row(
    check_id: str,
    status: str,
    *,
    observed: str,
    expected: str,
    review_action: str,
    evidence_paths: str,
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "status": status,
        "observed": observed or "none",
        "expected": expected,
        "review_action": review_action,
        "evidence_paths": evidence_paths,
        "claim_boundary": REPLICATION_AUDIT_CLAIM_BOUNDARY,
    }


def _load_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _load_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _project_path(raw: Any) -> Path:
    text = str(raw or "").strip()
    if not text:
        return Path("")
    path = Path(text)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def _values(rows: Sequence[Mapping[str, str]], field: str) -> list[str]:
    return [str(row.get(field, "")).strip() for row in rows if str(row.get(field, "")).strip()]


def _count_range(values: Sequence[int]) -> str:
    if not values:
        return "none"
    return f"min={min(values)}; max={max(values)}; rows={len(values)}"


def _count_status(values: Sequence[int], seed_count: int) -> str:
    if not values or seed_count <= 0:
        return "blocked"
    if any(value < 0 or value > seed_count for value in values):
        return "blocked"
    if min(values) == max(values) == seed_count:
        return "pass"
    return "needs_human_review"


def _counts(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for raw in values:
        value = str(raw).strip() or "<blank>"
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def _int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _display_path(path: Path) -> str:
    if not str(path):
        return ""
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


__all__ = [
    "DEFAULT_REPLICATION_AUDIT_CSV",
    "DEFAULT_REPLICATION_AUDIT_DOC",
    "DEFAULT_REPLICATION_AUDIT_MANIFEST",
    "REPLICATION_AUDIT_CLAIM_BOUNDARY",
    "REPLICATION_AUDIT_COLUMNS",
    "build_replication_adequacy_manifest",
    "build_replication_adequacy_markdown",
    "build_replication_adequacy_rows",
    "write_replication_adequacy_audit",
]
