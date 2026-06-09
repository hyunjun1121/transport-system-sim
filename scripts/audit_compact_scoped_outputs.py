"""Audit scoped compact-output regeneration artifacts.

This audit is intentionally narrow. It checks that a staged compact output was
generated as invalidation-regeneration material only, and that its CSV files
match the row counts recorded in its manifest. It does not approve publication,
final-study, formal-acceptance, or operational use.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


DEFAULT_MANIFEST_PATH = (
    ROOT
    / "results"
    / "realworld_pilot"
    / "phase8_compact_scoped_20260605"
    / "pilot_staged_manifest.json"
)
DEFAULT_OUTPUT_PATH = ROOT / "data" / "validation" / "compact_scoped_output_audit.csv"
DEFAULT_MANIFEST_OUTPUT = (
    ROOT / "data" / "validation" / "compact_scoped_output_audit_manifest.json"
)
DEFAULT_DOC_OUTPUT = ROOT / "docs" / "compact_scoped_output_audit.md"


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    summary, rows = audit_compact_scoped_outputs(args.manifest_path)
    _write_csv(args.output_path, rows)
    _write_json(args.manifest_output, summary)
    _write_markdown(args.doc_output, summary, rows)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if summary["audit_passed"] else 1


def audit_compact_scoped_outputs(path: str | Path) -> tuple[dict[str, Any], list[dict[str, str]]]:
    manifest_path = Path(path)
    rows: list[dict[str, str]] = []
    blockers: list[str] = []
    manifest = _read_json_object(manifest_path, blockers)
    if manifest is None:
        return _summary(manifest_path, rows, blockers), rows

    checks = {
        "run_profile_staged_pilot": manifest.get("run_profile") == "staged_pilot",
        "run_stage_staged": manifest.get("run_stage") == "staged",
        "scope_compact_outputs": manifest.get("closeout_regeneration_scope")
        == "compact_outputs",
        "scope_status_passed": manifest.get("closeout_regeneration_scope_status")
        == "passed",
        "engineering_only_false": manifest.get("engineering_only") is False,
        "publication_ready_false": manifest.get("publication_ready") is False,
        "final_study_ready_false": manifest.get("final_study_ready") is False,
        "formal_acceptance_evidence_false": manifest.get("formal_acceptance_evidence")
        is False,
        "row_count_positive": _int(manifest.get("row_count")) > 0,
        "summary_row_count_positive": _int(manifest.get("summary_row_count")) > 0,
        "profile_design_complete": manifest.get("profile_design_complete") is True,
    }
    for check_id, passed in checks.items():
        rows.append(_check_row(check_id, passed, str(manifest.get(check_id, ""))))
        if not passed:
            blockers.append(check_id)

    outputs = manifest.get("outputs", {})
    if not isinstance(outputs, Mapping):
        blockers.append("outputs_not_object")
        rows.append(_check_row("outputs_object", False, ""))
    else:
        _audit_csv_output(
            rows,
            blockers,
            output_name="results",
            raw_path=str(outputs.get("results", "")),
            expected_rows=_int(manifest.get("row_count")),
        )
        _audit_csv_output(
            rows,
            blockers,
            output_name="summary",
            raw_path=str(outputs.get("summary", "")),
            expected_rows=_int(manifest.get("summary_row_count")),
        )
        _audit_file_output(
            rows,
            blockers,
            output_name="output_lock_receipt",
            raw_path=str(outputs.get("output_lock_receipt", "")),
        )

    return _summary(manifest_path, rows, blockers), rows


def _audit_csv_output(
    rows: list[dict[str, str]],
    blockers: list[str],
    *,
    output_name: str,
    raw_path: str,
    expected_rows: int,
) -> None:
    path = _resolve_path(raw_path)
    exists = path.is_file()
    rows.append(_check_row(f"{output_name}_exists", exists, raw_path))
    if not exists:
        blockers.append(f"{output_name}_missing")
        return
    actual_rows = _csv_data_row_count(path)
    row_match = actual_rows == expected_rows
    rows.append(_check_row(f"{output_name}_row_count_matches", row_match, str(actual_rows)))
    if not row_match:
        blockers.append(f"{output_name}_row_count_mismatch")
    rows.append(_check_row(f"{output_name}_sha256", True, _sha256(path)))


def _audit_file_output(
    rows: list[dict[str, str]],
    blockers: list[str],
    *,
    output_name: str,
    raw_path: str,
) -> None:
    path = _resolve_path(raw_path)
    exists = path.is_file()
    rows.append(_check_row(f"{output_name}_exists", exists, raw_path))
    if not exists:
        blockers.append(f"{output_name}_missing")
        return
    rows.append(_check_row(f"{output_name}_sha256", True, _sha256(path)))


def _summary(
    manifest_path: Path,
    rows: list[dict[str, str]],
    blockers: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "manifest_path": _display_path(manifest_path),
        "row_count": len(rows),
        "blocking_finding_count": len(blockers),
        "audit_passed": not blockers,
        "phase9_promotion_ready": False,
        "publication_ready": False,
        "final_study_ready": False,
        "formal_acceptance_evidence": False,
        "claim_boundary": (
            "Scoped compact-output audit only; not publication evidence, not "
            "final-study evidence, not formal acceptance evidence, and not "
            "operational evidence."
        ),
        "remaining_blockers": blockers,
        "outputs": {
            "csv": _display_path(DEFAULT_OUTPUT_PATH),
            "manifest": _display_path(DEFAULT_MANIFEST_OUTPUT),
            "doc": _display_path(DEFAULT_DOC_OUTPUT),
        },
    }


def _read_json_object(path: Path, blockers: list[str]) -> dict[str, Any] | None:
    if not path.is_file():
        blockers.append("manifest_missing")
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        blockers.append(f"manifest_unreadable:{type(exc).__name__}")
        return None
    if not isinstance(payload, dict):
        blockers.append("manifest_not_object")
        return None
    return payload


def _check_row(check_id: str, passed: bool, observed: str) -> dict[str, str]:
    return {
        "check_id": check_id,
        "status": "pass" if passed else "fail",
        "observed": observed,
        "claim_boundary": "compact scoped output audit only",
    }


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["check_id", "status", "observed", "claim_boundary"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, summary: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_markdown(
    path: Path,
    summary: Mapping[str, Any],
    rows: list[dict[str, str]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Compact Scoped Output Audit",
        "",
        str(summary["claim_boundary"]),
        "",
        f"- Audit passed: `{str(summary['audit_passed']).lower()}`",
        f"- Blocking findings: {summary['blocking_finding_count']}",
        f"- Publication ready: `{str(summary['publication_ready']).lower()}`",
        f"- Final study ready: `{str(summary['final_study_ready']).lower()}`",
        f"- Formal acceptance evidence: `{str(summary['formal_acceptance_evidence']).lower()}`",
        "",
        "| Check | Status | Observed |",
        "| --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| {row['check_id']} | {row['status']} | {row['observed']} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _csv_data_row_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return sum(1 for _row in csv.DictReader(handle))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve_path(raw: str) -> Path:
    path = Path(raw)
    if path.is_absolute():
        return path
    return ROOT / path


def _display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest-path", type=Path, default=DEFAULT_MANIFEST_PATH)
    parser.add_argument("--output-path", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--manifest-output", type=Path, default=DEFAULT_MANIFEST_OUTPUT)
    parser.add_argument("--doc-output", type=Path, default=DEFAULT_DOC_OUTPUT)
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
