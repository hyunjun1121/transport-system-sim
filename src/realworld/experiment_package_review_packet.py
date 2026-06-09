"""Full experiment-package review packet generation.

The full pilot outputs can be structurally reproducible while still being
scaffold results. This module converts the full-pilot manifest, result files,
and experiment-acceptance absence into concrete review rows. It does not create
``data/manifests/experiment_acceptance.json`` and does not accept the
experiment package.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PILOT_FULL_MANIFEST_PATH = (
    PROJECT_ROOT / "results" / "realworld_pilot" / "pilot_full_manifest.json"
)
DEFAULT_EXPERIMENT_PACKAGE_REVIEW_PACKET_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "experiment_package_review_packet.csv"
)
DEFAULT_EXPERIMENT_PACKAGE_REVIEW_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "experiment_package_review_manifest.json"
)
DEFAULT_EXPERIMENT_PACKAGE_REVIEW_DOC_PATH = (
    PROJECT_ROOT / "docs" / "experiment_package_review_packet.md"
)
DEFAULT_EXPERIMENT_ACCEPTANCE_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "experiment_acceptance.json"
)
EXPERIMENT_PACKAGE_REVIEW_SCOPE = (
    "Experiment-package review packet only; not experiment acceptance, not "
    "calibrated real-world validation, and not operational routing approval."
)
EXPERIMENT_PACKAGE_REVIEW_COLUMNS: tuple[str, ...] = (
    "category_id",
    "artifact_path",
    "artifact_present",
    "row_count",
    "expected_row_count",
    "sha256",
    "review_status",
    "review_required",
    "acceptance_ready",
    "publication_ready",
    "review_action",
    "publication_use_status",
    "evidence_detail",
    "claim_boundary",
)


def build_experiment_package_review_rows(
    *,
    manifest_path: str | Path = DEFAULT_PILOT_FULL_MANIFEST_PATH,
    experiment_acceptance_path: str | Path = DEFAULT_EXPERIMENT_ACCEPTANCE_PATH,
) -> list[dict[str, str]]:
    """Return conservative review rows for the full pilot package."""

    manifest_file = Path(manifest_path)
    manifest = _load_json_object(manifest_file)
    outputs = manifest.get("outputs", {})
    if not isinstance(outputs, Mapping):
        outputs = {}
    results_path = _project_path(str(outputs.get("results", "")))
    summary_path = _project_path(str(outputs.get("summary", "")))
    output_manifest_path = _project_path(str(outputs.get("manifest", ""))) or manifest_file
    expected_rows = _int_value(manifest.get("row_count", manifest.get("expected_row_count", 0)))
    expected_summary_rows = _int_value(manifest.get("summary_row_count", 0))
    design = manifest.get("scenario_policy_seed_design", {})
    if not isinstance(design, Mapping):
        design = {}

    return [
        _manifest_scope_row(output_manifest_path, manifest),
        _csv_count_row(
            category_id="results_row_count",
            artifact_path=results_path,
            expected_row_count=expected_rows,
            review_action=(
                "Verify full result rows match the manifest and were regenerated "
                "after the reviewer-selected graph/input scope was documented."
            ),
        ),
        _csv_count_row(
            category_id="summary_row_count",
            artifact_path=summary_path,
            expected_row_count=expected_summary_rows,
            review_action=(
                "Verify summary rows match the manifest and summarize only the "
                "review-selected run profile."
            ),
        ),
        _scenario_policy_seed_row(manifest, design),
        _graph_scope_row(manifest),
        _input_dependency_row(manifest),
        _common_random_number_row(manifest),
        _checksum_row(
            manifest_path=output_manifest_path,
            results_path=results_path,
            summary_path=summary_path,
        ),
        _acceptance_record_requirement_row(Path(experiment_acceptance_path)),
    ]


def write_experiment_package_review_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_EXPERIMENT_PACKAGE_REVIEW_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_EXPERIMENT_PACKAGE_REVIEW_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_EXPERIMENT_PACKAGE_REVIEW_DOC_PATH,
    pilot_manifest_path: str | Path = DEFAULT_PILOT_FULL_MANIFEST_PATH,
    experiment_acceptance_path: str | Path = DEFAULT_EXPERIMENT_ACCEPTANCE_PATH,
) -> dict[str, Any]:
    """Write CSV, JSON, and Markdown experiment-package review artifacts."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=EXPERIMENT_PACKAGE_REVIEW_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in EXPERIMENT_PACKAGE_REVIEW_COLUMNS
                }
            )

    summary = build_experiment_package_review_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        pilot_manifest_path=pilot_manifest_path,
        experiment_acceptance_path=experiment_acceptance_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_experiment_package_review_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_experiment_package_review_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_EXPERIMENT_PACKAGE_REVIEW_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_EXPERIMENT_PACKAGE_REVIEW_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_EXPERIMENT_PACKAGE_REVIEW_DOC_PATH,
    pilot_manifest_path: str | Path = DEFAULT_PILOT_FULL_MANIFEST_PATH,
    experiment_acceptance_path: str | Path = DEFAULT_EXPERIMENT_ACCEPTANCE_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for experiment-package review."""

    review_status_counts = _counts(row.get("review_status", "") for row in rows)
    present_count = sum(1 for row in rows if _is_true(row.get("artifact_present", "false")))
    count_mismatch_count = sum(
        1 for row in rows if row.get("review_status") == "blocked_row_count_mismatch"
    )
    review_required_count = sum(
        1 for row in rows if _is_true(row.get("review_required", "false"))
    )
    closure_candidate_count = sum(
        1 for row in rows if _is_true(row.get("acceptance_ready", "false"))
    )
    return {
        "schema_version": 1,
        "claim_boundary": (
            EXPERIMENT_PACKAGE_REVIEW_SCOPE
            + " A reviewer must still create data/manifests/experiment_acceptance.json "
            "after graph scope, input checks, scenario-policy-seed design, "
            "CRN pairing, counts, and claim boundaries are reviewed."
        ),
        "result_scope": EXPERIMENT_PACKAGE_REVIEW_SCOPE,
        "row_count": len(rows),
        "present_artifact_row_count": present_count,
        "review_required_count": review_required_count,
        "row_count_mismatch_count": count_mismatch_count,
        "review_status_counts": review_status_counts,
        "experiment_acceptance_gate_closure_candidate_count": closure_candidate_count,
        "publication_ready": False,
        "acceptance_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "pilot_full_manifest": _display_path(Path(pilot_manifest_path)),
            "experiment_acceptance": _display_path(Path(experiment_acceptance_path)),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": [
            "verify result and summary row counts against pilot_full_manifest.json",
            "verify artifact checksums and retain them in the experiment decision record",
            "confirm graph scope and input checks before using full outputs",
            "confirm scenario-policy-seed design and CRN pairing before the experiment decision",
            "create data/manifests/experiment_acceptance.json only after a real review decision",
        ],
        "remaining_blockers": [
            "formal experiment acceptance record is absent",
            "experiment-package rows are review aids and do not approve full outputs",
            "upstream graph, parameter, validation, and provenance gates remain blocked",
        ],
    }


def build_experiment_package_review_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return a human-readable experiment-package review packet."""

    lines = [
        "# Experiment Package Review Packet",
        "",
        str(manifest.get("claim_boundary", EXPERIMENT_PACKAGE_REVIEW_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Acceptance ready: `{str(manifest.get('acceptance_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Review rows: {manifest.get('row_count', 0)}",
        f"- Count mismatches: {manifest.get('row_count_mismatch_count', 0)}",
        "",
        "## Review Rows",
        "",
        "| Category | Artifact | Status | Rows | Required Action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {category} | {artifact} | {status} | {rows} / {expected} | {action} |".format(
                category=_cell(row.get("category_id", "")),
                artifact=_cell(row.get("artifact_path", "")),
                status=_cell(row.get("review_status", "")),
                rows=_cell(row.get("row_count", "")),
                expected=_cell(row.get("expected_row_count", "")),
                action=_cell(row.get("review_action", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Required Reviewer Actions",
            "",
            "- Review `results/realworld_pilot/pilot_full_manifest.json` with the full result and summary CSVs.",
            "- Confirm graph-scale, input checks, scenario-policy-seed, and CRN decisions before the experiment decision.",
            "- Retain artifact checksums in the experiment decision evidence when the run package is reviewer-selected.",
            "- Create `data/manifests/experiment_acceptance.json` only after a real review decision.",
            "",
        ]
    )
    return "\n".join(lines)


def _manifest_scope_row(path: Path, manifest: Mapping[str, Any]) -> dict[str, str]:
    present = path.exists()
    result_scope = str(manifest.get("result_scope", ""))
    status = "review_required_scaffold_or_not_calibrated_scope"
    if not present:
        status = "blocked_missing_manifest"
    elif "not calibrated" not in result_scope.lower() and "not operational" not in result_scope.lower():
        status = "review_required_claim_boundary_incomplete"
    return _row(
        category_id="manifest_scope",
        artifact_path=path,
        artifact_present=present,
        row_count=_int_text(manifest.get("row_count", "")),
        expected_row_count=_int_text(manifest.get("expected_row_count", manifest.get("row_count", ""))),
        sha256=_sha256(path) if present else "",
        review_status=status,
        review_action=(
            "Confirm result_scope is bounded to decision support and update only "
            "through formal experiment acceptance."
        ),
        publication_use_status="review_support_only_not_experiment_acceptance",
        evidence_detail=result_scope,
    )


def _csv_count_row(
    *,
    category_id: str,
    artifact_path: Path,
    expected_row_count: int,
    review_action: str,
) -> dict[str, str]:
    present = artifact_path.exists()
    row_count = _csv_row_count(artifact_path) if present else 0
    status = "ready_for_review_count_matches"
    if not present:
        status = "blocked_missing_artifact"
    elif row_count != expected_row_count:
        status = "blocked_row_count_mismatch"
    return _row(
        category_id=category_id,
        artifact_path=artifact_path,
        artifact_present=present,
        row_count=str(row_count),
        expected_row_count=str(expected_row_count),
        sha256=_sha256(artifact_path) if present else "",
        review_status=status,
        review_action=review_action,
        publication_use_status="review_required_before_experiment_acceptance",
        evidence_detail=(
            f"observed_rows={row_count}; expected_rows={expected_row_count}"
        ),
    )


def _scenario_policy_seed_row(
    manifest: Mapping[str, Any],
    design: Mapping[str, Any],
) -> dict[str, str]:
    policy_count = _int_value(design.get("policy_count", len(_sequence(manifest.get("policy_ids")))))
    scenario_count = _int_value(design.get("scenario_count", len(_sequence(manifest.get("scenario_ids")))))
    seed_count = _int_value(design.get("seed_count", len(_sequence(manifest.get("seeds")))))
    expected = policy_count * scenario_count * seed_count
    observed = _int_value(manifest.get("row_count", 0))
    status = (
        "ready_for_review_design_counts_match"
        if expected == observed and expected > 0
        else "blocked_design_count_mismatch"
    )
    return _row(
        category_id="scenario_policy_seed_design",
        artifact_path=Path(str(manifest.get("design_path", "")) or "data/manifests/pilot_experiment_design.json"),
        artifact_present=_project_path(str(manifest.get("design_path", ""))).exists(),
        row_count=str(observed),
        expected_row_count=str(expected),
        sha256="",
        review_status=status,
        review_action=(
            "Confirm policies, scenarios, seeds, exclusions, and row-count "
            "multiplication before accepting the experiment package."
        ),
        publication_use_status="blocked_until_scenario_policy_seed_design_review",
        evidence_detail=(
            f"policy_count={policy_count}; scenario_count={scenario_count}; "
            f"seed_count={seed_count}; observed_rows={observed}"
        ),
    )


def _graph_scope_row(manifest: Mapping[str, Any]) -> dict[str, str]:
    graph_scale = manifest.get("graph_scale", {})
    if not isinstance(graph_scale, Mapping):
        graph_scale = {}
    analysis = graph_scale.get("analysis", {})
    source = graph_scale.get("source", {})
    if not isinstance(analysis, Mapping):
        analysis = {}
    if not isinstance(source, Mapping):
        source = {}
    reduced = bool(
        analysis.get("reduced", manifest.get("analysis_graph_reduced", False))
    )
    return _row(
        category_id="graph_scope_dependency",
        artifact_path=Path("data/manifests/graph_scale_acceptance.json"),
        artifact_present=(PROJECT_ROOT / "data" / "manifests" / "graph_scale_acceptance.json").exists(),
        row_count=str(analysis.get("nodes", manifest.get("graph_nodes", ""))),
        expected_row_count=str(source.get("nodes", manifest.get("source_graph_nodes", ""))),
        sha256="",
        review_status=(
            "blocked_until_graph_scale_acceptance"
            if reduced
            else "review_required_graph_scope_acceptance"
        ),
        review_action=(
            "Close graph-scale method review or regenerate outputs on the "
            "selected graph method before using full experiment outputs."
        ),
        publication_use_status="blocked_until_graph_scale_acceptance",
        evidence_detail=(
            f"analysis_graph_reduced={str(reduced).lower()}; "
            f"analysis_nodes={analysis.get('nodes', manifest.get('graph_nodes', ''))}; "
            f"analysis_edges={analysis.get('edges', manifest.get('graph_edges', ''))}; "
            f"source_nodes={source.get('nodes', manifest.get('source_graph_nodes', ''))}; "
            f"source_edges={source.get('edges', manifest.get('source_graph_edges', ''))}"
        ),
    )


def _input_dependency_row(manifest: Mapping[str, Any]) -> dict[str, str]:
    inputs = manifest.get("inputs", {})
    if not isinstance(inputs, Mapping):
        inputs = {}
    overrides_applied = bool(manifest.get("road_class_overrides_applied", False))
    missing_inputs = [
        key
        for key in (
            "region_path",
            "cache_path",
            "disruption_scenarios_path",
            "policy_alternatives_path",
            "pilot_experiment_design_path",
        )
        if not _project_path(str(inputs.get(key, ""))).exists()
    ]
    status = (
        "blocked_until_input_evidence_acceptance"
        if missing_inputs or not overrides_applied
        else "review_required_input_evidence_acceptance"
    )
    return _row(
        category_id="input_evidence_dependency",
        artifact_path=Path("data/manifests/experiment_acceptance.json"),
        artifact_present=False,
        row_count=str(len(inputs)),
        expected_row_count="5",
        sha256="",
        review_status=status,
        review_action=(
            "Confirm all input source, road override, parameter, validation, and "
            "provenance gates before accepting current outputs."
        ),
        publication_use_status="blocked_until_upstream_input_gates_close",
        evidence_detail=(
            f"missing_input_keys={';'.join(missing_inputs) or 'none'}; "
            f"road_class_overrides_applied={str(overrides_applied).lower()}"
        ),
    )


def _common_random_number_row(manifest: Mapping[str, Any]) -> dict[str, str]:
    design = manifest.get("scenario_policy_seed_design", {})
    if not isinstance(design, Mapping):
        design = {}
    crn = bool(design.get("common_random_numbers", False))
    return _row(
        category_id="common_random_numbers",
        artifact_path=Path("results/realworld_pilot/pilot_full_manifest.json"),
        artifact_present=True,
        row_count=str(_int_value(design.get("seed_count", 0))),
        expected_row_count=str(len(_sequence(manifest.get("seeds")))),
        sha256="",
        review_status=(
            "ready_for_review_crn_declared" if crn else "blocked_crn_not_declared"
        ),
        review_action=(
            "Confirm same-seed paired comparisons and scenario runner seed "
            "splitting before accepting paired policy claims."
        ),
        publication_use_status="review_required_before_paired_claims",
        evidence_detail=str(manifest.get("common_random_numbers", "")),
    )


def _checksum_row(*, manifest_path: Path, results_path: Path, summary_path: Path) -> dict[str, str]:
    hashes = {
        "manifest": _sha256(manifest_path) if manifest_path.exists() else "",
        "results": _sha256(results_path) if results_path.exists() else "",
        "summary": _sha256(summary_path) if summary_path.exists() else "",
    }
    complete = all(hashes.values())
    return _row(
        category_id="artifact_checksums",
        artifact_path=manifest_path,
        artifact_present=complete,
        row_count=str(sum(1 for value in hashes.values() if value)),
        expected_row_count="3",
        sha256=";".join(f"{key}={value}" for key, value in hashes.items()),
        review_status=(
            "ready_for_review_checksums_available"
            if complete
            else "blocked_missing_checksum_inputs"
        ),
        review_action=(
            "Record these checksums or regenerated equivalents in the formal "
            "experiment decision evidence."
        ),
        publication_use_status="review_support_only_not_reproducibility_acceptance",
        evidence_detail=";".join(f"{key}_sha256_present={str(bool(value)).lower()}" for key, value in hashes.items()),
    )


def _acceptance_record_requirement_row(path: Path) -> dict[str, str]:
    present = path.exists()
    return _row(
        category_id="formal_experiment_acceptance_requirement",
        artifact_path=path,
        artifact_present=present,
        row_count="1" if present else "0",
        expected_row_count="1",
        sha256=_sha256(path) if present else "",
        review_status=(
            "review_required_formal_acceptance_present"
            if present
            else "blocked_formal_acceptance_absent"
        ),
        review_action=(
            "Create or review experiment_acceptance.json only after graph scope, "
            "input checks, scenario-policy-seed design, CRN, counts, and "
            "claim boundary are genuinely reviewed."
        ),
        publication_use_status="cannot_close_experiment_gate_without_formal_acceptance",
        evidence_detail="formal experiment acceptance record controls gate closure",
    )


def _row(
    *,
    category_id: str,
    artifact_path: Path,
    artifact_present: bool,
    row_count: str,
    expected_row_count: str,
    sha256: str,
    review_status: str,
    review_action: str,
    publication_use_status: str,
    evidence_detail: str,
) -> dict[str, str]:
    return {
        "category_id": category_id,
        "artifact_path": _display_path(artifact_path),
        "artifact_present": _bool_text(artifact_present),
        "row_count": row_count,
        "expected_row_count": expected_row_count,
        "sha256": sha256,
        "review_status": review_status,
        "review_required": "true",
        "acceptance_ready": "false",
        "publication_ready": "false",
        "review_action": review_action,
        "publication_use_status": publication_use_status,
        "evidence_detail": evidence_detail,
        "claim_boundary": EXPERIMENT_PACKAGE_REVIEW_SCOPE,
    }


def _load_json_object(path: str | Path) -> dict[str, Any]:
    json_path = Path(path)
    if not json_path.exists():
        return {}
    with json_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    return value if isinstance(value, dict) else {}


def _csv_row_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return sum(1 for _row in csv.DictReader(handle))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _project_path(value: str) -> Path:
    path = Path(value)
    if not value:
        return Path("")
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def _sequence(value: object) -> tuple[object, ...]:
    if isinstance(value, Sequence) and not isinstance(value, str):
        return tuple(value)
    return ()


def _int_value(value: object) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return value
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return 0


def _int_text(value: object) -> str:
    parsed = _int_value(value)
    return str(parsed) if parsed else str(value or "")


def _counts(values: Sequence[str] | Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _is_true(value: str) -> bool:
    return str(value).strip().lower() == "true"


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except (ValueError, RuntimeError):
        return path.as_posix()


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


__all__ = [
    "DEFAULT_EXPERIMENT_ACCEPTANCE_PATH",
    "DEFAULT_EXPERIMENT_PACKAGE_REVIEW_DOC_PATH",
    "DEFAULT_EXPERIMENT_PACKAGE_REVIEW_MANIFEST_PATH",
    "DEFAULT_EXPERIMENT_PACKAGE_REVIEW_PACKET_PATH",
    "DEFAULT_PILOT_FULL_MANIFEST_PATH",
    "EXPERIMENT_PACKAGE_REVIEW_COLUMNS",
    "EXPERIMENT_PACKAGE_REVIEW_SCOPE",
    "build_experiment_package_review_manifest",
    "build_experiment_package_review_markdown",
    "build_experiment_package_review_rows",
    "write_experiment_package_review_packet",
]
