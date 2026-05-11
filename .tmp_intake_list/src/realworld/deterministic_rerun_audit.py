"""Deterministic rerun comparison for pilot experiment rows.

The audit reruns a bounded pilot profile twice with identical inputs and checks
whether result and summary rows are byte-stable after canonical serialization.
It is CRN/reproducibility review support only; it does not prove stochastic
model adequacy, approve the full experiment package, or close final-study gates.
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.realworld.manifest_timestamp import (
    preserve_generated_at_when_unchanged,
    write_json_manifest_if_changed,
    write_text_if_changed,
)
from src.realworld.pilot_experiments import (
    DEFAULT_CACHE_PATH,
    DEFAULT_DESIGN_PATH,
    DEFAULT_REGION_PATH,
    DEFAULT_SAMPLE_PROFILE_ID,
    PROJECT_ROOT,
    load_pilot_inputs,
    load_policy_alternatives,
    load_disruption_scenarios,
    resolve_pilot_experiment_profile,
    run_pilot_rows,
    select_disruption_cases,
    select_policy_alternatives,
    summarize_pilot_rows,
)
from src.realworld.disruption_scenarios import DEFAULT_SCENARIO_PATH
from src.realworld.policy_alternatives import DEFAULT_POLICY_ALTERNATIVES_PATH


DEFAULT_DETERMINISTIC_RERUN_AUDIT_CSV = (
    PROJECT_ROOT / "data" / "manifests" / "deterministic_rerun_audit.csv"
)
DEFAULT_DETERMINISTIC_RERUN_AUDIT_MANIFEST = (
    PROJECT_ROOT / "data" / "manifests" / "deterministic_rerun_audit_manifest.json"
)
DEFAULT_DETERMINISTIC_RERUN_AUDIT_DOC = (
    PROJECT_ROOT / "docs" / "deterministic_rerun_audit.md"
)

DETERMINISTIC_RERUN_CLAIM_BOUNDARY = (
    "This deterministic rerun audit checks whether a bounded pilot profile "
    "produces identical rows across two local executions with the same inputs. "
    "It does not approve CRN design, prove replication adequacy, certify full "
    "experiment reproducibility, or close final-study gates."
)
DETERMINISTIC_RERUN_COLUMNS: tuple[str, ...] = (
    "check_id",
    "status",
    "observed",
    "expected",
    "review_action",
    "evidence_paths",
    "claim_boundary",
)


def run_deterministic_rerun_audit(
    *,
    region_path: str | Path = DEFAULT_REGION_PATH,
    cache_path: str | Path = DEFAULT_CACHE_PATH,
    scenarios_path: str | Path = DEFAULT_SCENARIO_PATH,
    policies_path: str | Path = DEFAULT_POLICY_ALTERNATIVES_PATH,
    design_path: str | Path = DEFAULT_DESIGN_PATH,
    run_profile: str = DEFAULT_SAMPLE_PROFILE_ID,
    road_class_overrides_path: str | Path | None = None,
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    """Run the selected profile twice and return audit rows plus run metadata."""

    design, profile = resolve_pilot_experiment_profile(
        design_path=design_path,
        run_profile=run_profile,
        sample=run_profile == DEFAULT_SAMPLE_PROFILE_ID,
    )
    inputs = load_pilot_inputs(
        region_path=region_path,
        cache_path=cache_path,
        road_class_overrides_path=road_class_overrides_path,
        reduce_graph=profile.reduce_graph,
        graph_reduction_strategy=profile.graph_reduction_strategy,
        corridor_path_count=profile.corridor_path_count,
    )
    policies = select_policy_alternatives(
        load_policy_alternatives(policies_path),
        policy_ids=profile.policy_ids,
        sample=profile.sample_scaffold,
    )
    cases = select_disruption_cases(
        inputs.graph,
        load_disruption_scenarios(scenarios_path, region_id=inputs.region_id),
        scenario_ids=profile.scenario_ids,
        sample=profile.sample_scaffold,
    )
    first_rows = run_pilot_rows(
        inputs=inputs,
        policies=policies,
        cases=cases,
        seeds=profile.seeds,
        claim_scope=profile.result_scope,
    )
    second_rows = run_pilot_rows(
        inputs=inputs,
        policies=policies,
        cases=cases,
        seeds=profile.seeds,
        claim_scope=profile.result_scope,
    )
    first_summary = summarize_pilot_rows(first_rows)
    second_summary = summarize_pilot_rows(second_rows)
    metadata = {
        "profile_id": profile.profile_id,
        "run_stage": profile.run_stage,
        "sample_scaffold": profile.sample_scaffold,
        "result_scope": profile.result_scope,
        "region_id": design.region_id,
        "graph_source": inputs.graph_source,
        "policy_count": len(policies),
        "scenario_count": len(cases),
        "seed_count": len(profile.seeds),
        "row_count": len(first_rows),
        "summary_row_count": len(first_summary),
        "inputs": {
            "region_path": _display_path(region_path),
            "cache_path": _display_path(cache_path),
            "scenarios_path": _display_path(scenarios_path),
            "policies_path": _display_path(policies_path),
            "design_path": _display_path(design_path),
        },
        "hashes": {
            "first_rows_sha256": _rows_sha256(first_rows),
            "second_rows_sha256": _rows_sha256(second_rows),
            "first_summary_sha256": _rows_sha256(first_summary),
            "second_summary_sha256": _rows_sha256(second_summary),
        },
    }
    return build_deterministic_rerun_rows(
        first_rows=first_rows,
        second_rows=second_rows,
        first_summary_rows=first_summary,
        second_summary_rows=second_summary,
        metadata=metadata,
    ), metadata


def build_deterministic_rerun_rows(
    *,
    first_rows: Sequence[Mapping[str, Any]],
    second_rows: Sequence[Mapping[str, Any]],
    first_summary_rows: Sequence[Mapping[str, Any]],
    second_summary_rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
) -> list[dict[str, str]]:
    """Return deterministic rerun audit rows for two completed runs."""

    hashes = metadata.get("hashes", {})
    if not isinstance(hashes, Mapping):
        hashes = {}
    first_hash = str(hashes.get("first_rows_sha256") or _rows_sha256(first_rows))
    second_hash = str(hashes.get("second_rows_sha256") or _rows_sha256(second_rows))
    first_summary_hash = str(
        hashes.get("first_summary_sha256") or _rows_sha256(first_summary_rows)
    )
    second_summary_hash = str(
        hashes.get("second_summary_sha256") or _rows_sha256(second_summary_rows)
    )
    profile_id = str(metadata.get("profile_id", ""))
    expected_rows = (
        _int(metadata.get("policy_count"))
        * _int(metadata.get("scenario_count"))
        * _int(metadata.get("seed_count"))
    )
    evidence_paths = "; ".join(
        str(path)
        for path in (metadata.get("inputs") or {}).values()
        if str(path).strip()
    )
    return [
        _row(
            "first_rerun_completed",
            "pass" if first_rows else "blocked_no_first_rows",
            observed=str(len(first_rows)),
            expected="first execution returns at least one row",
            review_action="Debug pilot runner errors before determinism review.",
            evidence_paths=evidence_paths,
        ),
        _row(
            "second_rerun_completed",
            "pass" if second_rows else "blocked_no_second_rows",
            observed=str(len(second_rows)),
            expected="second execution returns at least one row",
            review_action="Debug pilot runner errors before determinism review.",
            evidence_paths=evidence_paths,
        ),
        _row(
            "row_count_matches_profile_design",
            "pass" if len(first_rows) == expected_rows else "blocked_row_count_mismatch",
            observed=f"{len(first_rows)} / {expected_rows}",
            expected="policy_count * scenario_count * seed_count",
            review_action="Resolve run-design row-count mismatch before interpreting rerun comparison.",
            evidence_paths=evidence_paths,
        ),
        _row(
            "rerun_row_hash_match",
            "pass" if first_hash == second_hash else "blocked_rerun_row_hash_mismatch",
            observed=f"{first_hash} / {second_hash}",
            expected="identical canonical row hashes",
            review_action="Investigate nondeterministic row generation before paired claims.",
            evidence_paths=evidence_paths,
        ),
        _row(
            "rerun_summary_hash_match",
            "pass"
            if first_summary_hash == second_summary_hash
            else "blocked_rerun_summary_hash_mismatch",
            observed=f"{first_summary_hash} / {second_summary_hash}",
            expected="identical canonical summary hashes",
            review_action="Investigate nondeterministic summary generation before reporting statistics.",
            evidence_paths=evidence_paths,
        ),
        _row(
            "rerun_profile_scope",
            "needs_human_review_profile_scope",
            observed=profile_id,
            expected="review whether this bounded rerun profile is sufficient",
            review_action=(
                "Decide whether the accepted full profile also needs a deterministic "
                "rerun check after graph and input gates close."
            ),
            evidence_paths=evidence_paths,
        ),
        _row(
            "formal_experiment_acceptance",
            "blocked_missing_experiment_acceptance_record",
            observed="data/manifests/experiment_acceptance.json absent unless reviewer supplies it",
            expected="formal experiment acceptance after graph, input, CRN, and statistics review",
            review_action="Do not treat deterministic rerun success as formal experiment acceptance.",
            evidence_paths=evidence_paths,
        ),
    ]


def write_deterministic_rerun_audit(
    *,
    output_path: str | Path = DEFAULT_DETERMINISTIC_RERUN_AUDIT_CSV,
    audit_manifest_path: str | Path = DEFAULT_DETERMINISTIC_RERUN_AUDIT_MANIFEST,
    doc_path: str | Path = DEFAULT_DETERMINISTIC_RERUN_AUDIT_DOC,
    rows: Sequence[Mapping[str, str]] | None = None,
    metadata: Mapping[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Write deterministic rerun CSV, manifest, and Markdown outputs."""

    if rows is None or metadata is None:
        generated_rows, generated_metadata = run_deterministic_rerun_audit(**kwargs)
        rows = generated_rows if rows is None else rows
        metadata = generated_metadata if metadata is None else metadata
    audit_rows = [dict(row) for row in rows]
    output = Path(output_path)
    audit_manifest = Path(audit_manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    audit_manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=DETERMINISTIC_RERUN_COLUMNS)
        writer.writeheader()
        writer.writerows(audit_rows)
    manifest = build_deterministic_rerun_manifest(
        rows=audit_rows,
        metadata=metadata,
        output_path=output,
        manifest_path=audit_manifest,
        doc_path=doc,
    )
    preserve_generated_at_when_unchanged(manifest, audit_manifest)
    write_json_manifest_if_changed(manifest, audit_manifest, sort_keys=True)
    write_text_if_changed(build_deterministic_rerun_markdown(manifest, audit_rows), doc)
    return manifest


def build_deterministic_rerun_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    metadata: Mapping[str, Any],
    output_path: str | Path = DEFAULT_DETERMINISTIC_RERUN_AUDIT_CSV,
    manifest_path: str | Path = DEFAULT_DETERMINISTIC_RERUN_AUDIT_MANIFEST,
    doc_path: str | Path = DEFAULT_DETERMINISTIC_RERUN_AUDIT_DOC,
) -> dict[str, Any]:
    """Return the deterministic rerun audit manifest."""

    status_counts = _counts(row.get("status", "") for row in rows)
    blockers = [row for row in rows if row.get("status", "").startswith("blocked")]
    deterministic_blockers = [
        row
        for row in blockers
        if row.get("check_id") != "formal_experiment_acceptance"
    ]
    row_hashes_match = _check_status(rows, "rerun_row_hash_match") == "pass"
    summary_hashes_match = _check_status(rows, "rerun_summary_hash_match") == "pass"
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "claim_boundary": DETERMINISTIC_RERUN_CLAIM_BOUNDARY,
        "row_count": len(rows),
        "status_counts": status_counts,
        "blocking_check_count": len(blockers),
        "deterministic_blocking_check_count": len(deterministic_blockers),
        "needs_human_review_count": sum(
            1 for row in rows if row.get("status", "").startswith("needs_human_review")
        ),
        "row_hashes_match": row_hashes_match,
        "summary_hashes_match": summary_hashes_match,
        "deterministic_rerun_structurally_ready": len(deterministic_blockers) == 0,
        "acceptance_ready": False,
        "publication_ready": False,
        "can_mark_complete": False,
        "profile": {
            "profile_id": metadata.get("profile_id", ""),
            "run_stage": metadata.get("run_stage", ""),
            "sample_scaffold": bool(metadata.get("sample_scaffold", False)),
            "result_scope": metadata.get("result_scope", ""),
        },
        "design_counts": {
            "policy_count": metadata.get("policy_count", 0),
            "scenario_count": metadata.get("scenario_count", 0),
            "seed_count": metadata.get("seed_count", 0),
            "row_count": metadata.get("row_count", 0),
            "summary_row_count": metadata.get("summary_row_count", 0),
        },
        "hashes": dict(metadata.get("hashes", {})),
        "inputs": dict(metadata.get("inputs", {})),
        "outputs": {
            "csv": _display_path(output_path),
            "manifest": _display_path(manifest_path),
            "doc": _display_path(doc_path),
        },
        "review_items": [
            "review whether bounded sample-profile determinism is sufficient or rerun the accepted full profile",
            "treat row-hash equality as repeatability support only, not CRN or experiment acceptance",
            "rerun this audit after graph-scope, road/rail/parameter evidence, or runner logic changes",
        ],
    }


def build_deterministic_rerun_markdown(
    manifest: Mapping[str, Any],
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return Markdown for the deterministic rerun audit."""

    profile = manifest.get("profile", {})
    counts = manifest.get("design_counts", {})
    hashes = manifest.get("hashes", {})
    if not isinstance(profile, Mapping):
        profile = {}
    if not isinstance(counts, Mapping):
        counts = {}
    if not isinstance(hashes, Mapping):
        hashes = {}
    lines = [
        "# Deterministic Rerun Audit",
        "",
        str(manifest.get("claim_boundary", DETERMINISTIC_RERUN_CLAIM_BOUNDARY)),
        "",
        "## Verdict",
        "",
        f"- Deterministic rerun structurally ready: `{str(manifest.get('deterministic_rerun_structurally_ready', False)).lower()}`",
        f"- Row hashes match: `{str(manifest.get('row_hashes_match', False)).lower()}`",
        f"- Summary hashes match: `{str(manifest.get('summary_hashes_match', False)).lower()}`",
        f"- Acceptance ready: `{str(manifest.get('acceptance_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Blocking checks: {manifest.get('blocking_check_count', 0)}",
        f"- Deterministic blocking checks: {manifest.get('deterministic_blocking_check_count', 0)}",
        f"- Human-review checks: {manifest.get('needs_human_review_count', 0)}",
        "",
        "## Profile",
        "",
        f"- Profile: `{profile.get('profile_id', '')}`",
        f"- Run stage: `{profile.get('run_stage', '')}`",
        f"- Sample scaffold: `{str(profile.get('sample_scaffold', False)).lower()}`",
        f"- Policies: {counts.get('policy_count', 0)}",
        f"- Scenarios: {counts.get('scenario_count', 0)}",
        f"- Seeds: {counts.get('seed_count', 0)}",
        f"- Result rows per run: {counts.get('row_count', 0)}",
        f"- Summary rows per run: {counts.get('summary_row_count', 0)}",
        "",
        "## Hashes",
        "",
        f"- First rows SHA256: `{hashes.get('first_rows_sha256', '')}`",
        f"- Second rows SHA256: `{hashes.get('second_rows_sha256', '')}`",
        f"- First summary SHA256: `{hashes.get('first_summary_sha256', '')}`",
        f"- Second summary SHA256: `{hashes.get('second_summary_sha256', '')}`",
        "",
        "## Checks",
        "",
        "| Check | Status | Observed | Required Action |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            f"{row.get('check_id', '')} | "
            f"{row.get('status', '')} | "
            f"{_md(row.get('observed', ''))} | "
            f"{_md(row.get('review_action', ''))} |"
        )
    lines.extend(
        [
            "",
            "## Use",
            "",
            "Use this audit with the seed-stream manifest, CRN pairing audit, replication adequacy audit, and experiment statistical-analysis plan before drafting `data/manifests/experiment_acceptance.json`.",
        ]
    )
    return "\n".join(lines) + "\n"


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
        "observed": observed,
        "expected": expected,
        "review_action": review_action,
        "evidence_paths": evidence_paths,
        "claim_boundary": DETERMINISTIC_RERUN_CLAIM_BOUNDARY,
    }


def _rows_sha256(rows: Sequence[Mapping[str, Any]]) -> str:
    return hashlib.sha256(_canonical_rows(rows).encode("utf-8")).hexdigest()


def _canonical_rows(rows: Sequence[Mapping[str, Any]]) -> str:
    return json.dumps(
        [_jsonable(dict(row)) for row in rows],
        ensure_ascii=True,
        sort_keys=True,
        allow_nan=True,
        separators=(",", ":"),
    )


def _jsonable(value: Any) -> Any:
    try:
        json.dumps(value, allow_nan=True)
    except (TypeError, ValueError):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _counts(values: Sequence[str] | Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        text = str(value)
        counts[text] = counts.get(text, 0) + 1
    return counts


def _check_status(rows: Sequence[Mapping[str, str]], check_id: str) -> str:
    for row in rows:
        if row.get("check_id") == check_id:
            return str(row.get("status", ""))
    return ""


def _int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _display_path(path: str | Path) -> str:
    filepath = Path(path)
    try:
        return filepath.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return filepath.as_posix()


def _md(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


__all__ = [
    "DEFAULT_DETERMINISTIC_RERUN_AUDIT_CSV",
    "DEFAULT_DETERMINISTIC_RERUN_AUDIT_DOC",
    "DEFAULT_DETERMINISTIC_RERUN_AUDIT_MANIFEST",
    "DETERMINISTIC_RERUN_CLAIM_BOUNDARY",
    "build_deterministic_rerun_manifest",
    "build_deterministic_rerun_markdown",
    "build_deterministic_rerun_rows",
    "run_deterministic_rerun_audit",
    "write_deterministic_rerun_audit",
]
