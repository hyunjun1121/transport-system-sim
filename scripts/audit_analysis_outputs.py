"""Audit scoped statistics, sensitivity, and ML analysis outputs."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ANALYSIS_DIR = (
    ROOT
    / "results"
    / "realworld_pilot"
    / "phase8_compact_scoped_20260605"
    / "analysis"
)
DEFAULT_SOURCE_RESULTS = (
    ROOT
    / "results"
    / "realworld_pilot"
    / "phase8_compact_scoped_20260605"
    / "pilot_staged_results.csv"
)
DEFAULT_SOURCE_MANIFEST = (
    ROOT
    / "results"
    / "realworld_pilot"
    / "phase8_compact_scoped_20260605"
    / "pilot_staged_manifest.json"
)
DEFAULT_OUTPUT_CSV = ROOT / "data" / "validation" / "analysis_outputs_audit.csv"
DEFAULT_OUTPUT_MANIFEST = (
    ROOT / "data" / "validation" / "analysis_outputs_audit_manifest.json"
)
DEFAULT_OUTPUT_DOC = ROOT / "docs" / "analysis_outputs_audit.md"
CLAIM_BOUNDARY = (
    "Scoped analysis-output audit only; not publication evidence, not "
    "final-study evidence, not formal acceptance evidence, and not operational "
    "evidence."
)
FIELDNAMES = (
    "check_id",
    "artifact_group",
    "path",
    "status",
    "expected",
    "actual",
    "claim_scope",
)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    summary = audit_analysis_outputs(
        analysis_dir=args.analysis_dir,
        source_results=args.source_results,
        source_manifest=args.source_manifest,
        output_csv=args.output_csv,
        output_manifest=args.output_manifest,
        output_doc=args.output_doc,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    if args.fail_on_blockers and summary["blocking_finding_count"] > 0:
        return 1
    return 0


def audit_analysis_outputs(
    *,
    analysis_dir: str | Path = DEFAULT_ANALYSIS_DIR,
    source_results: str | Path = DEFAULT_SOURCE_RESULTS,
    source_manifest: str | Path = DEFAULT_SOURCE_MANIFEST,
    output_csv: str | Path = DEFAULT_OUTPUT_CSV,
    output_manifest: str | Path = DEFAULT_OUTPUT_MANIFEST,
    output_doc: str | Path = DEFAULT_OUTPUT_DOC,
) -> dict[str, Any]:
    analysis = Path(analysis_dir)
    rows: list[dict[str, str]] = []
    source_results_sha = _sha256_file(source_results)
    source_manifest_sha = _sha256_file(source_manifest)

    stats_manifest = _read_json(
        analysis / "pilot_staged_scoped_statistics_manifest.json", rows, "statistics"
    )
    if stats_manifest:
        _check_count(
            rows,
            "statistics_metric_rows",
            "statistics",
            analysis / "pilot_staged_scoped_metric_ci.csv",
            int(stats_manifest.get("metric_ci_row_count", -1)),
        )
        _check_count(
            rows,
            "statistics_paired_rows",
            "statistics",
            analysis / "pilot_staged_scoped_paired_delta_ci.csv",
            int(stats_manifest.get("paired_delta_ci_row_count", -1)),
        )
        _check_manifest_source_hash(
            rows,
            "statistics_source_manifest_hash",
            "statistics",
            stats_manifest,
            source_manifest_sha,
        )

    sensitivity_manifest = _read_json(
        analysis / "sensitivity_manifest.json", rows, "sensitivity"
    )
    if sensitivity_manifest:
        _check_count(
            rows,
            "sensitivity_result_rows",
            "sensitivity",
            analysis / "sensitivity_results.csv",
            int(sensitivity_manifest.get("row_count", -1)),
        )
        _check_count(
            rows,
            "sensitivity_summary_rows",
            "sensitivity",
            analysis / "sensitivity_summary.csv",
            int(sensitivity_manifest.get("summary_row_count", -1)),
        )

    ml_manifest = _read_json(
        analysis / "pilot_staged_scoped_ml_manifest.json", rows, "ml_outputs"
    )
    if ml_manifest:
        _check_count(
            rows,
            "ml_label_rows",
            "ml_labels",
            analysis / "pilot_staged_scoped_ml_labels.csv",
            int(ml_manifest.get("label_row_count", -1)),
        )
        _check_count(
            rows,
            "ml_prediction_rows",
            "ml_outputs",
            analysis / "pilot_staged_scoped_ml_predictions.csv",
            int(ml_manifest.get("prediction_row_count", -1)),
        )
        _check_count(
            rows,
            "ml_importance_rows",
            "ml_outputs",
            analysis / "pilot_staged_scoped_ml_feature_importance.csv",
            int(ml_manifest.get("feature_importance_row_count", -1)),
        )
        _check_json_field(
            rows,
            "ml_source_results_hash",
            "ml_outputs",
            analysis / "pilot_staged_scoped_ml_manifest.json",
            source_results_sha,
            str(ml_manifest.get("source_results_sha256", "")),
        )
        _check_json_field(
            rows,
            "ml_source_manifest_hash",
            "ml_outputs",
            analysis / "pilot_staged_scoped_ml_manifest.json",
            source_manifest_sha,
            str(ml_manifest.get("source_manifest_sha256", "")),
        )
        for field in ("publication_ready", "final_study_ready", "formal_acceptance_evidence"):
            _check_json_field(
                rows,
                f"ml_{field}",
                "ml_outputs",
                analysis / "pilot_staged_scoped_ml_manifest.json",
                "False",
                str(ml_manifest.get(field)),
            )

    blocking = [row for row in rows if row["status"] != "pass"]
    summary = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "claim_boundary": CLAIM_BOUNDARY,
        "analysis_dir": _display_path(analysis),
        "source_results": _display_path(source_results),
        "source_manifest": _display_path(source_manifest),
        "row_count": len(rows),
        "blocking_finding_count": len(blocking),
        "audit_passed": len(blocking) == 0,
        "publication_ready": False,
        "final_study_ready": False,
        "formal_acceptance_evidence": False,
        "outputs": {
            "csv": _display_path(output_csv),
            "manifest": _display_path(output_manifest),
            "doc": _display_path(output_doc),
        },
        "remaining_blockers": [
            f"{row['check_id']}: {row['actual']}" for row in blocking
        ],
    }
    _write_csv(Path(output_csv), rows)
    Path(output_manifest).parent.mkdir(parents=True, exist_ok=True)
    Path(output_manifest).write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    Path(output_doc).parent.mkdir(parents=True, exist_ok=True)
    Path(output_doc).write_text(_markdown(summary, rows), encoding="utf-8")
    return summary


def _read_json(path: Path, rows: list[dict[str, str]], group: str) -> dict[str, Any]:
    if not path.is_file():
        rows.append(_row(f"{group}_manifest_exists", group, path, "block", "file exists", "missing"))
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        rows.append(_row(f"{group}_manifest_json", group, path, "block", "valid JSON", str(exc)))
        return {}
    rows.append(_row(f"{group}_manifest_exists", group, path, "pass", "file exists", "loaded"))
    return payload if isinstance(payload, dict) else {}


def _check_count(
    rows: list[dict[str, str]],
    check_id: str,
    group: str,
    path: Path,
    expected: int,
) -> None:
    actual = _csv_row_count(path)
    rows.append(
        _row(
            check_id,
            group,
            path,
            "pass" if actual == expected else "block",
            str(expected),
            str(actual),
        )
    )


def _check_manifest_source_hash(
    rows: list[dict[str, str]],
    check_id: str,
    group: str,
    manifest: Mapping[str, Any],
    expected_hash: str,
) -> None:
    actual = str(manifest.get("source_manifest_sha256", ""))
    rows.append(
        _row(
            check_id,
            group,
            Path(str(manifest.get("source_manifest_path", ""))),
            "pass" if actual == expected_hash else "block",
            expected_hash,
            actual,
        )
    )


def _check_json_field(
    rows: list[dict[str, str]],
    check_id: str,
    group: str,
    path: Path,
    expected: str,
    actual: str,
) -> None:
    rows.append(
        _row(
            check_id,
            group,
            path,
            "pass" if actual == expected else "block",
            expected,
            actual,
        )
    )


def _row(
    check_id: str,
    group: str,
    path: Path,
    status: str,
    expected: str,
    actual: str,
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "artifact_group": group,
        "path": _display_path(path),
        "status": status,
        "expected": expected,
        "actual": actual,
        "claim_scope": CLAIM_BOUNDARY,
    }


def _csv_row_count(path: Path) -> int:
    if not path.is_file():
        return -1
    with path.open("r", encoding="utf-8", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def _markdown(summary: Mapping[str, Any], rows: list[dict[str, str]]) -> str:
    lines = [
        "# Analysis Outputs Audit",
        "",
        f"- Audit passed: `{str(summary['audit_passed']).lower()}`",
        f"- Blocking findings: `{summary['blocking_finding_count']}`",
        f"- Scope: {summary['claim_boundary']}",
        "",
        "| check | group | status | expected | actual |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['check_id']} | {row['artifact_group']} | {row['status']} | "
            f"{row['expected']} | {row['actual']} |"
        )
    lines.append("")
    return "\n".join(lines)


def _sha256_file(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _display_path(path: str | Path) -> str:
    try:
        return Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return Path(path).as_posix()


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-dir", type=Path, default=DEFAULT_ANALYSIS_DIR)
    parser.add_argument("--source-results", type=Path, default=DEFAULT_SOURCE_RESULTS)
    parser.add_argument("--source-manifest", type=Path, default=DEFAULT_SOURCE_MANIFEST)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--output-manifest", type=Path, default=DEFAULT_OUTPUT_MANIFEST)
    parser.add_argument("--output-doc", type=Path, default=DEFAULT_OUTPUT_DOC)
    parser.add_argument("--fail-on-blockers", action="store_true")
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
