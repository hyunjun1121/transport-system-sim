"""Structural common-random-number pairing audit for pilot outputs.

The audit checks whether the result table follows the manifest's
scenario-policy-seed design and whether the scenario runner still exposes the
documented seed split. It is structural review support only; it cannot prove
statistical sufficiency or approve experiment acceptance.
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
DEFAULT_PILOT_FULL_RESULTS_PATH = (
    PROJECT_ROOT / "results" / "realworld_pilot" / "pilot_full_results.csv"
)
DEFAULT_PILOT_FULL_MANIFEST_PATH = (
    PROJECT_ROOT / "results" / "realworld_pilot" / "pilot_full_manifest.json"
)
DEFAULT_SCENARIO_SOURCE_PATH = PROJECT_ROOT / "src" / "scenario.py"
DEFAULT_CRN_PAIRING_AUDIT_CSV = (
    PROJECT_ROOT / "data" / "manifests" / "crn_pairing_audit.csv"
)
DEFAULT_CRN_PAIRING_AUDIT_MANIFEST = (
    PROJECT_ROOT / "data" / "manifests" / "crn_pairing_audit_manifest.json"
)
DEFAULT_CRN_PAIRING_AUDIT_DOC = PROJECT_ROOT / "docs" / "crn_pairing_audit.md"

CRN_PAIRING_CLAIM_BOUNDARY = (
    "This audit checks structural common-random-number pairing in result files "
    "and seed-splitting source markers. It does not prove statistical power, "
    "validate stochastic model adequacy, approve experiment acceptance, or "
    "close final-study gates."
)
CRN_PAIRING_COLUMNS: tuple[str, ...] = (
    "check_id",
    "status",
    "observed",
    "expected",
    "review_action",
    "evidence_paths",
    "claim_boundary",
)


def build_crn_pairing_audit_rows(
    *,
    results_path: str | Path = DEFAULT_PILOT_FULL_RESULTS_PATH,
    manifest_path: str | Path = DEFAULT_PILOT_FULL_MANIFEST_PATH,
    scenario_source_path: str | Path = DEFAULT_SCENARIO_SOURCE_PATH,
) -> list[dict[str, str]]:
    """Return structural CRN pairing audit rows."""

    results_file = Path(results_path)
    manifest_file = Path(manifest_path)
    source_file = Path(scenario_source_path)
    manifest = _load_json_object(manifest_file)
    rows = _load_csv_rows(results_file)
    policy_ids = tuple(str(item) for item in manifest.get("policy_ids", []))
    scenario_ids = tuple(str(item) for item in manifest.get("scenario_ids", []))
    seeds = tuple(str(item) for item in manifest.get("seeds", []))
    design = manifest.get("scenario_policy_seed_design", {})
    if not isinstance(design, Mapping):
        design = {}
    expected_row_count = _int(design.get("expected_row_count")) or (
        len(policy_ids) * len(scenario_ids) * len(seeds)
    )
    result_keys = _result_key_counts(rows)
    duplicate_keys = [key for key, count in result_keys.items() if count > 1]
    expected_scope_keys = _expected_scope_keys(rows, manifest)
    missing_policy_groups = _missing_policy_groups(
        rows,
        policy_ids=policy_ids,
        scenario_ids=scenario_ids,
        seeds=seeds,
        scope_keys=expected_scope_keys,
    )
    missing_seed_groups = _missing_seed_groups(
        rows,
        policy_ids=policy_ids,
        scenario_ids=scenario_ids,
        seeds=seeds,
        scope_keys=expected_scope_keys,
    )

    source_text = _read_text(source_file)
    stream_markers_present = (
        "default_rng(seed)" in source_text
        and "default_rng(seed + 10_000)" in source_text
    )

    evidence = "; ".join(
        _display_path(path)
        for path in (results_file, manifest_file, source_file)
    )
    return [
        _check_row(
            "manifest_present",
            manifest_file.exists(),
            observed=_display_path(manifest_file) if manifest_file.exists() else "missing",
            expected="pilot full manifest exists",
            review_action="Include the manifest in the experiment acceptance evidence.",
            evidence_paths=_display_path(manifest_file),
        ),
        _check_row(
            "results_present",
            results_file.exists(),
            observed=_display_path(results_file) if results_file.exists() else "missing",
            expected="pilot full results CSV exists",
            review_action="Include result CSV and checksum in the experiment acceptance evidence.",
            evidence_paths=_display_path(results_file),
        ),
        _check_row(
            "crn_declared_in_manifest",
            bool(design.get("common_random_numbers") is True)
            and bool(manifest.get("common_random_numbers")),
            observed=str(design.get("common_random_numbers")),
            expected="scenario_policy_seed_design.common_random_numbers=true",
            review_action=(
                "Confirm the declared same-seed design is retained in the formal "
                "experiment acceptance record."
            ),
            evidence_paths=_display_path(manifest_file),
        ),
        _check_row(
            "seed_stream_source_markers",
            stream_markers_present,
            observed=(
                "arrival=default_rng(seed); failure=default_rng(seed + 10_000)"
                if stream_markers_present
                else "seed split markers missing"
            ),
            expected="separate arrival and failure RNG streams derived from same seed",
            review_action=(
                "Review source code to confirm all compared policies use the same "
                "seed-derived demand and disruption streams."
            ),
            evidence_paths=_display_path(source_file),
            status_if_pass="needs_human_review",
        ),
        _scope_check_row(
            "region_set_matches_manifest",
            rows=rows,
            field="region_id",
            expected=str(manifest.get("region_id", "")),
            review_action=(
                "Resolve region mismatch before treating the result table as the "
                "manifested experiment package."
            ),
            evidence_paths=evidence,
        ),
        _scope_check_row(
            "graph_source_set_matches_manifest",
            rows=rows,
            field="graph_source",
            expected=str(manifest.get("graph_source", "")),
            review_action=(
                "Resolve graph-source mismatch before paired policy or graph-scope "
                "claims."
            ),
            evidence_paths=evidence,
        ),
        _check_row(
            "row_count_matches_design",
            len(rows) == expected_row_count,
            observed=str(len(rows)),
            expected=str(expected_row_count),
            review_action="Regenerate results or revise manifest if row counts differ.",
            evidence_paths=evidence,
        ),
        _check_row(
            "policy_set_matches_manifest",
            set(_values(rows, "policy_id")) == set(policy_ids),
            observed=", ".join(sorted(set(_values(rows, "policy_id")))),
            expected=", ".join(policy_ids),
            review_action="Resolve policy inclusion/exclusion before experiment acceptance.",
            evidence_paths=evidence,
        ),
        _check_row(
            "scenario_set_matches_manifest",
            set(_values(rows, "scenario_id")) == set(scenario_ids),
            observed=", ".join(sorted(set(_values(rows, "scenario_id")))),
            expected=", ".join(scenario_ids),
            review_action="Resolve scenario inclusion/exclusion before experiment acceptance.",
            evidence_paths=evidence,
        ),
        _check_row(
            "seed_set_matches_manifest",
            set(_values(rows, "seed")) == set(seeds),
            observed=", ".join(sorted(set(_values(rows, "seed")), key=_sort_key)),
            expected=", ".join(seeds),
            review_action="Resolve seed-set mismatch before paired policy claims.",
            evidence_paths=evidence,
        ),
        _check_row(
            "scenario_seed_policy_completeness",
            not missing_policy_groups,
            observed=_limited_join(missing_policy_groups),
            expected="every scenario/seed group has every expected policy exactly once",
            review_action="Regenerate missing policy rows before paired policy claims.",
            evidence_paths=evidence,
        ),
        _check_row(
            "policy_scenario_seed_completeness",
            not missing_seed_groups,
            observed=_limited_join(missing_seed_groups),
            expected="every policy/scenario group has every expected seed exactly once",
            review_action="Regenerate missing seed rows before confidence intervals.",
            evidence_paths=evidence,
        ),
        _check_row(
            "duplicate_policy_scenario_seed_rows",
            not duplicate_keys,
            observed=_limited_join(["|".join(key) for key in duplicate_keys]),
            expected="no duplicate region/graph/policy/scenario/seed rows",
            review_action="Remove or explain duplicate result rows before acceptance.",
            evidence_paths=evidence,
        ),
    ]


def write_crn_pairing_audit(
    *,
    rows: Sequence[Mapping[str, str]] | None = None,
    results_path: str | Path = DEFAULT_PILOT_FULL_RESULTS_PATH,
    manifest_path: str | Path = DEFAULT_PILOT_FULL_MANIFEST_PATH,
    scenario_source_path: str | Path = DEFAULT_SCENARIO_SOURCE_PATH,
    output_path: str | Path = DEFAULT_CRN_PAIRING_AUDIT_CSV,
    audit_manifest_path: str | Path = DEFAULT_CRN_PAIRING_AUDIT_MANIFEST,
    doc_path: str | Path = DEFAULT_CRN_PAIRING_AUDIT_DOC,
) -> dict[str, Any]:
    """Write CSV, JSON, and Markdown CRN pairing audit outputs."""

    audit_rows = (
        list(rows)
        if rows is not None
        else build_crn_pairing_audit_rows(
            results_path=results_path,
            manifest_path=manifest_path,
            scenario_source_path=scenario_source_path,
        )
    )
    output = Path(output_path)
    audit_manifest = Path(audit_manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    audit_manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CRN_PAIRING_COLUMNS)
        writer.writeheader()
        writer.writerows(audit_rows)

    summary = build_crn_pairing_audit_manifest(
        rows=audit_rows,
        output_path=output,
        manifest_path=audit_manifest,
        doc_path=doc,
        results_path=results_path,
        pilot_manifest_path=manifest_path,
        scenario_source_path=scenario_source_path,
    )
    preserve_generated_at_when_unchanged(summary, audit_manifest)
    write_json_manifest_if_changed(summary, audit_manifest, sort_keys=True)
    write_text_if_changed(build_crn_pairing_audit_markdown(summary, audit_rows), doc)
    return summary


def build_crn_pairing_audit_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_CRN_PAIRING_AUDIT_CSV,
    manifest_path: str | Path = DEFAULT_CRN_PAIRING_AUDIT_MANIFEST,
    doc_path: str | Path = DEFAULT_CRN_PAIRING_AUDIT_DOC,
    results_path: str | Path = DEFAULT_PILOT_FULL_RESULTS_PATH,
    pilot_manifest_path: str | Path = DEFAULT_PILOT_FULL_MANIFEST_PATH,
    scenario_source_path: str | Path = DEFAULT_SCENARIO_SOURCE_PATH,
) -> dict[str, Any]:
    """Return a conservative CRN pairing audit manifest."""

    status_counts = _counts(row.get("status", "") for row in rows)
    blocking = [
        row
        for row in rows
        if row.get("status") in {"blocked", "missing", "mismatch"}
    ]
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "claim_boundary": CRN_PAIRING_CLAIM_BOUNDARY,
        "row_count": len(rows),
        "status_counts": status_counts,
        "blocking_check_count": len(blocking),
        "needs_human_review_count": status_counts.get("needs_human_review", 0),
        "structural_crn_pairing_ready": len(blocking) == 0,
        "acceptance_ready": False,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "results": _display_path(Path(results_path)),
            "pilot_manifest": _display_path(Path(pilot_manifest_path)),
            "scenario_source": _display_path(Path(scenario_source_path)),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "remaining_blockers": [
            f"{row.get('check_id', '')}: {row.get('review_action', '')}"
            for row in blocking
        ],
        "review_items": [
            "confirm source-level seed stream use before common-random-number acceptance",
            "retain this audit with experiment_package_review_packet evidence",
            "do not treat structural pairing as statistical power or validation acceptance",
        ],
    }


def build_crn_pairing_audit_markdown(
    manifest: Mapping[str, Any],
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return a human-readable CRN pairing audit."""

    lines = [
        "# CRN Pairing Audit",
        "",
        str(manifest.get("claim_boundary", CRN_PAIRING_CLAIM_BOUNDARY)),
        "",
        "## Verdict",
        "",
        f"- Structural CRN pairing ready: `{str(manifest.get('structural_crn_pairing_ready', False)).lower()}`",
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
            "Use this audit with the experiment package review before drafting "
            "`data/manifests/experiment_acceptance.json`. A passing structural "
            "audit is necessary review support, but it is not formal CRN "
            "acceptance and does not prove replication adequacy.",
            "",
        ]
    )
    return "\n".join(lines)


def _check_row(
    check_id: str,
    ok: bool,
    *,
    observed: str,
    expected: str,
    review_action: str,
    evidence_paths: str,
    status_if_pass: str = "pass",
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "status": status_if_pass if ok else "blocked",
        "observed": observed or "none",
        "expected": expected,
        "review_action": review_action,
        "evidence_paths": evidence_paths,
        "claim_boundary": CRN_PAIRING_CLAIM_BOUNDARY,
    }


def _scope_check_row(
    check_id: str,
    *,
    rows: Sequence[Mapping[str, str]],
    field: str,
    expected: str,
    review_action: str,
    evidence_paths: str,
) -> dict[str, str]:
    observed_values = sorted(set(_nonblank_values(rows, field)))
    if expected:
        ok = set(observed_values) == {expected}
        expected_text = expected
    else:
        ok = True
        expected_text = "not declared in manifest"
    return _check_row(
        check_id,
        ok,
        observed=", ".join(observed_values) if observed_values else "none",
        expected=expected_text,
        review_action=review_action,
        evidence_paths=evidence_paths,
    )


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


def _result_key_counts(
    rows: Sequence[Mapping[str, str]],
) -> dict[tuple[str, str, str, str, str], int]:
    counts: dict[tuple[str, str, str, str, str], int] = {}
    for row in rows:
        key = (
            str(row.get("region_id", "")),
            str(row.get("graph_source", "")),
            str(row.get("policy_id", "")),
            str(row.get("scenario_id", "")),
            str(row.get("seed", "")),
        )
        counts[key] = counts.get(key, 0) + 1
    return counts


def _expected_scope_keys(
    rows: Sequence[Mapping[str, str]],
    manifest: Mapping[str, Any],
) -> tuple[tuple[str, str], ...]:
    manifest_region = str(manifest.get("region_id", ""))
    manifest_graph = str(manifest.get("graph_source", ""))
    if manifest_region or manifest_graph:
        return ((manifest_region, manifest_graph),)
    observed = sorted(
        {
            (str(row.get("region_id", "")), str(row.get("graph_source", "")))
            for row in rows
        }
    )
    return tuple(observed) if observed else (("", ""),)


def _missing_policy_groups(
    rows: Sequence[Mapping[str, str]],
    *,
    policy_ids: Sequence[str],
    scenario_ids: Sequence[str],
    seeds: Sequence[str],
    scope_keys: Sequence[tuple[str, str]],
) -> list[str]:
    observed: dict[tuple[str, str, str, str], set[str]] = {}
    for row in rows:
        key = (
            str(row.get("region_id", "")),
            str(row.get("graph_source", "")),
            str(row.get("scenario_id", "")),
            str(row.get("seed", "")),
        )
        observed.setdefault(key, set()).add(str(row.get("policy_id", "")))
    expected_policies = set(policy_ids)
    missing: list[str] = []
    for region_id, graph_source in scope_keys:
        for scenario_id in scenario_ids:
            for seed in seeds:
                found = observed.get((region_id, graph_source, scenario_id, seed), set())
                if found != expected_policies:
                    missing.append(
                        f"{region_id or '<none>'}/{graph_source or '<none>'}/{scenario_id}/{seed}: missing={','.join(sorted(expected_policies - found))}; extra={','.join(sorted(found - expected_policies))}"
                    )
    return missing


def _missing_seed_groups(
    rows: Sequence[Mapping[str, str]],
    *,
    policy_ids: Sequence[str],
    scenario_ids: Sequence[str],
    seeds: Sequence[str],
    scope_keys: Sequence[tuple[str, str]],
) -> list[str]:
    observed: dict[tuple[str, str, str, str], set[str]] = {}
    for row in rows:
        key = (
            str(row.get("region_id", "")),
            str(row.get("graph_source", "")),
            str(row.get("policy_id", "")),
            str(row.get("scenario_id", "")),
        )
        observed.setdefault(key, set()).add(str(row.get("seed", "")))
    expected_seeds = set(seeds)
    missing: list[str] = []
    for region_id, graph_source in scope_keys:
        for policy_id in policy_ids:
            for scenario_id in scenario_ids:
                found = observed.get((region_id, graph_source, policy_id, scenario_id), set())
                if found != expected_seeds:
                    missing.append(
                        f"{region_id or '<none>'}/{graph_source or '<none>'}/{policy_id}/{scenario_id}: missing={','.join(sorted(expected_seeds - found, key=_sort_key))}; extra={','.join(sorted(found - expected_seeds, key=_sort_key))}"
                    )
    return missing


def _values(rows: Sequence[Mapping[str, str]], field: str) -> list[str]:
    return [str(row.get(field, "")) for row in rows]


def _nonblank_values(rows: Sequence[Mapping[str, str]], field: str) -> list[str]:
    return [value for value in _values(rows, field) if value]


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


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


def _sort_key(value: str) -> tuple[int, str]:
    try:
        return (0, f"{int(value):020d}")
    except ValueError:
        return (1, value)


def _limited_join(values: Sequence[str], *, limit: int = 10) -> str:
    if not values:
        return "none"
    head = list(values[:limit])
    if len(values) > limit:
        head.append(f"{len(values) - limit} additional issue groups")
    return "; ".join(head)


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


__all__ = [
    "CRN_PAIRING_CLAIM_BOUNDARY",
    "CRN_PAIRING_COLUMNS",
    "DEFAULT_CRN_PAIRING_AUDIT_CSV",
    "DEFAULT_CRN_PAIRING_AUDIT_DOC",
    "DEFAULT_CRN_PAIRING_AUDIT_MANIFEST",
    "build_crn_pairing_audit_manifest",
    "build_crn_pairing_audit_markdown",
    "build_crn_pairing_audit_rows",
    "write_crn_pairing_audit",
]
