"""Experiment statistical-analysis and scenario-policy-seed plan.

This module turns the existing pilot design, CRN audit, and replication audit
into one reviewer-facing plan. It is deliberately non-acceptance evidence: the
plan pre-specifies candidate primary outcomes and comparison handling for
review, but it cannot approve the experiment package or close final-study gates.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.realworld.manifest_timestamp import (
    preserve_generated_at_when_unchanged,
    write_json_manifest_if_changed,
    write_text_if_changed,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PILOT_EXPERIMENT_DESIGN_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "pilot_experiment_design.json"
)
DEFAULT_PILOT_FULL_MANIFEST_PATH = (
    PROJECT_ROOT / "results" / "realworld_pilot" / "pilot_full_manifest.json"
)
DEFAULT_STATISTICS_MANIFEST_PATH = (
    PROJECT_ROOT
    / "results"
    / "realworld_pilot"
    / "tables"
    / "pilot_full_statistics_manifest.json"
)
DEFAULT_CRN_PAIRING_AUDIT_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "crn_pairing_audit_manifest.json"
)
DEFAULT_REPLICATION_ADEQUACY_AUDIT_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "replication_adequacy_audit_manifest.json"
)
DEFAULT_EXPERIMENT_STATISTICAL_PLAN_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "experiment_statistical_analysis_plan.json"
)
DEFAULT_EXPERIMENT_STATISTICAL_PLAN_DOC_PATH = (
    PROJECT_ROOT / "docs" / "experiment_statistical_analysis_plan.md"
)

EXPERIMENT_STATISTICAL_PLAN_CLAIM_BOUNDARY = (
    "This statistical-analysis plan and scenario-policy-seed note is a "
    "pre-review planning artifact. It does not approve experiment decision "
    "artifacts, prove replication adequacy, verify common-random-number design, "
    "select a multiple-comparison procedure, or close study-closeout gates."
)
PRIMARY_METRICS: tuple[str, ...] = (
    "completion_rate",
    "penalized_makespan",
    "p95_arrival_time",
    "passengers_per_total_service_minute",
)
PRIMARY_COMPARISONS: tuple[dict[str, str], ...] = (
    {
        "baseline_policy_id": "bus_only",
        "comparison_policy_id": "baseline_multimodal",
        "comparison_scope": "candidate_primary_policy_contrast",
        "interpretation": "rail-bus multimodal candidate compared with bus-only baseline",
    },
)
SECONDARY_COMPARISON_BOUNDARY = (
    "All other policy, scenario, and metric contrasts remain exploratory until "
    "a reviewer selects a primary/secondary comparison family and any required "
    "multiplicity adjustment."
)


def build_experiment_statistical_plan(
    *,
    design_path: str | Path = DEFAULT_PILOT_EXPERIMENT_DESIGN_PATH,
    pilot_manifest_path: str | Path = DEFAULT_PILOT_FULL_MANIFEST_PATH,
    statistics_manifest_path: str | Path = DEFAULT_STATISTICS_MANIFEST_PATH,
    crn_manifest_path: str | Path = DEFAULT_CRN_PAIRING_AUDIT_MANIFEST_PATH,
    replication_manifest_path: str | Path = DEFAULT_REPLICATION_ADEQUACY_AUDIT_MANIFEST_PATH,
    selected_profile_id: str | None = None,
) -> dict[str, Any]:
    """Return the conservative statistical-analysis plan manifest."""

    design_file = Path(design_path)
    pilot_file = Path(pilot_manifest_path)
    statistics_file = Path(statistics_manifest_path)
    crn_file = Path(crn_manifest_path)
    replication_file = Path(replication_manifest_path)

    design = _load_json_object(design_file)
    pilot_manifest = _load_json_object(pilot_file)
    statistics_manifest = _load_json_object(statistics_file)
    crn_manifest = _load_json_object(crn_file)
    replication_manifest = _load_json_object(replication_file)

    profile_id = (
        selected_profile_id
        or str(pilot_manifest.get("run_profile", "")).strip()
        or str(statistics_manifest.get("source_run_profile", "")).strip()
        or "full_pilot"
    )
    profile = _profile(design, profile_id)
    policy_ids = _string_sequence(profile.get("policy_ids"))
    scenario_ids = _string_sequence(profile.get("scenario_ids"))
    seeds = [int(value) for value in _integer_sequence(profile.get("seeds"))]
    expected_row_count = len(policy_ids) * len(scenario_ids) * len(seeds)
    observed_row_count = _int(pilot_manifest.get("row_count"))
    observed_summary_row_count = _int(pilot_manifest.get("summary_row_count"))
    expected_summary_row_count = len(policy_ids) * len(scenario_ids)

    checks = _build_checks(
        profile_id=profile_id,
        profile=profile,
        expected_row_count=expected_row_count,
        observed_row_count=observed_row_count,
        expected_summary_row_count=expected_summary_row_count,
        observed_summary_row_count=observed_summary_row_count,
        statistics_manifest=statistics_manifest,
        crn_manifest=crn_manifest,
        replication_manifest=replication_manifest,
    )
    blocking = [check for check in checks if str(check["status"]).startswith("blocked")]
    human_review = [
        check for check in checks if str(check["status"]).startswith("needs_human_review")
    ]

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "claim_boundary": EXPERIMENT_STATISTICAL_PLAN_CLAIM_BOUNDARY,
        "selected_profile_id": profile_id,
        "design_status": profile.get("design_status", ""),
        "result_scope": profile.get("result_scope", ""),
        "region_id": design.get("region_id", pilot_manifest.get("region_id", "")),
        "graph_source": pilot_manifest.get("graph_source", ""),
        "analysis_graph_strategy": profile.get("analysis_graph_strategy", ""),
        "scenario_policy_seed_design": {
            "policy_count": len(policy_ids),
            "scenario_count": len(scenario_ids),
            "seed_count": len(seeds),
            "expected_row_count": expected_row_count,
            "observed_row_count": observed_row_count,
            "expected_summary_row_count": expected_summary_row_count,
            "observed_summary_row_count": observed_summary_row_count,
            "common_random_numbers": True,
            "policy_ids": policy_ids,
            "scenario_ids": scenario_ids,
            "seeds": seeds,
        },
        "primary_metrics": list(PRIMARY_METRICS),
        "primary_comparisons": list(PRIMARY_COMPARISONS),
        "secondary_comparison_boundary": SECONDARY_COMPARISON_BOUNDARY,
        "ci_method": statistics_manifest.get("ci_method", ""),
        "multiple_comparison_method": statistics_manifest.get(
            "multiple_comparison_method", ""
        ),
        "checks": checks,
        "blocking_check_count": len(blocking),
        "needs_human_review_count": len(human_review),
        "statistical_plan_ready_for_review": len(blocking) == 0,
        "acceptance_ready": False,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "design": _display_path(design_file),
            "pilot_manifest": _display_path(pilot_file),
            "statistics_manifest": _display_path(statistics_file),
            "crn_pairing_audit_manifest": _display_path(crn_file),
            "replication_adequacy_audit_manifest": _display_path(replication_file),
        },
        "outputs": {
            "manifest": _display_path(DEFAULT_EXPERIMENT_STATISTICAL_PLAN_MANIFEST_PATH),
            "doc": _display_path(DEFAULT_EXPERIMENT_STATISTICAL_PLAN_DOC_PATH),
        },
        "review_items": [
            "confirm or revise the candidate primary policy contrast before a formal experiment decision",
            "confirm whether the primary metrics are sufficient for completion, tail risk, and resource efficiency claims",
            "review CRN source-code markers and structural pairing before interpreting paired deltas",
            "decide whether 30 seeds and normal-approximation intervals are sufficient for reviewer-selected primary metrics",
            "record any selected multiplicity procedure only in the formal experiment decision evidence",
        ],
    }


def write_experiment_statistical_plan(
    *,
    manifest_path: str | Path = DEFAULT_EXPERIMENT_STATISTICAL_PLAN_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_EXPERIMENT_STATISTICAL_PLAN_DOC_PATH,
    **kwargs: Any,
) -> dict[str, Any]:
    """Write the plan manifest and Markdown note."""

    manifest = build_experiment_statistical_plan(**kwargs)
    output_manifest = Path(manifest_path)
    output_doc = Path(doc_path)
    manifest["outputs"] = {
        "manifest": _display_path(output_manifest),
        "doc": _display_path(output_doc),
    }
    output_manifest.parent.mkdir(parents=True, exist_ok=True)
    output_doc.parent.mkdir(parents=True, exist_ok=True)
    preserve_generated_at_when_unchanged(manifest, output_manifest)
    write_json_manifest_if_changed(manifest, output_manifest, sort_keys=True)
    write_text_if_changed(build_experiment_statistical_plan_markdown(manifest), output_doc)
    return manifest


def build_experiment_statistical_plan_markdown(manifest: Mapping[str, Any]) -> str:
    """Return a reviewer-facing Markdown plan."""

    design = manifest.get("scenario_policy_seed_design", {})
    if not isinstance(design, Mapping):
        design = {}
    lines = [
        "# Experiment Statistical Analysis Plan",
        "",
        str(manifest.get("claim_boundary", EXPERIMENT_STATISTICAL_PLAN_CLAIM_BOUNDARY)),
        "",
        "## Verdict",
        "",
        f"- Selected profile: `{manifest.get('selected_profile_id', '')}`",
        f"- Statistical plan ready for review: `{str(manifest.get('statistical_plan_ready_for_review', False)).lower()}`",
        f"- Acceptance ready: `{str(manifest.get('acceptance_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Blocking checks: {manifest.get('blocking_check_count', 0)}",
        f"- Human-review checks: {manifest.get('needs_human_review_count', 0)}",
        "",
        "## Scenario-Policy-Seed Design",
        "",
        f"- Region: `{manifest.get('region_id', '')}`",
        f"- Graph source: `{manifest.get('graph_source', '')}`",
        f"- Analysis graph strategy: `{manifest.get('analysis_graph_strategy', '')}`",
        f"- Policies: {design.get('policy_count', 0)}",
        f"- Scenarios: {design.get('scenario_count', 0)}",
        f"- Seeds: {design.get('seed_count', 0)}",
        f"- Expected result rows: {design.get('expected_row_count', 0)}",
        f"- Observed result rows: {design.get('observed_row_count', 0)}",
        f"- Expected summary rows: {design.get('expected_summary_row_count', 0)}",
        f"- Observed summary rows: {design.get('observed_summary_row_count', 0)}",
        f"- Common random numbers declared: `{str(design.get('common_random_numbers', False)).lower()}`",
        "",
        "## Primary Analysis Proposal",
        "",
        "Primary metrics proposed for review:",
        "",
    ]
    lines.extend(f"- `{metric}`" for metric in manifest.get("primary_metrics", []))
    lines.extend(
        [
            "",
            "Primary policy comparisons proposed for review:",
            "",
        ]
    )
    for comparison in manifest.get("primary_comparisons", []):
        if not isinstance(comparison, Mapping):
            continue
        lines.append(
            "- "
            f"`{comparison.get('baseline_policy_id', '')}` vs "
            f"`{comparison.get('comparison_policy_id', '')}`: "
            f"{comparison.get('interpretation', '')}"
        )
    lines.extend(
        [
            "",
            f"Secondary comparison boundary: {manifest.get('secondary_comparison_boundary', '')}",
            "",
            f"CI method: `{manifest.get('ci_method', '')}`",
            f"Multiplicity note: {manifest.get('multiple_comparison_method', '')}",
            "",
            "## Checks",
            "",
            "| Check | Status | Observed | Required Action |",
            "| --- | --- | --- | --- |",
        ]
    )
    for check in manifest.get("checks", []):
        if not isinstance(check, Mapping):
            continue
        lines.append(
            "| "
            f"{check.get('check_id', '')} | "
            f"{check.get('status', '')} | "
            f"{_md(check.get('observed', ''))} | "
            f"{_md(check.get('review_action', ''))} |"
        )
    lines.extend(
        [
            "",
            "## Use",
            "",
            "Use this note with `docs/crn_pairing_audit.md`, `docs/replication_adequacy_audit.md`, and `docs/experiment_package_review_packet.md` before drafting `data/manifests/experiment_acceptance.json`. It is a planning and review artifact only.",
        ]
    )
    return "\n".join(lines) + "\n"


def _build_checks(
    *,
    profile_id: str,
    profile: Mapping[str, Any],
    expected_row_count: int,
    observed_row_count: int,
    expected_summary_row_count: int,
    observed_summary_row_count: int,
    statistics_manifest: Mapping[str, Any],
    crn_manifest: Mapping[str, Any],
    replication_manifest: Mapping[str, Any],
) -> list[dict[str, str]]:
    return [
        _check(
            "selected_profile_present",
            "pass" if bool(profile) else "blocked_missing_profile",
            observed=profile_id if profile else "missing",
            review_action="Restore the selected run profile before experiment review.",
        ),
        _check(
            "result_row_count_matches_design",
            "pass" if expected_row_count == observed_row_count else "blocked_row_count_mismatch",
            observed=f"{observed_row_count} / {expected_row_count}",
            review_action="Regenerate results or revise the scenario-policy-seed design before review closure.",
        ),
        _check(
            "summary_row_count_matches_design",
            "pass"
            if expected_summary_row_count == observed_summary_row_count
            else "blocked_summary_count_mismatch",
            observed=f"{observed_summary_row_count} / {expected_summary_row_count}",
            review_action="Regenerate summary outputs or revise the run design before review closure.",
        ),
        _check(
            "primary_metrics_pre_specified",
            "needs_human_review_primary_metrics",
            observed=", ".join(PRIMARY_METRICS),
            review_action="Confirm, revise, or narrow the proposed primary metric set.",
        ),
        _check(
            "primary_policy_contrast_pre_specified",
            "needs_human_review_primary_comparison",
            observed="bus_only vs baseline_multimodal",
            review_action="Confirm whether this is the reviewer-selected primary contrast or mark all contrasts exploratory.",
        ),
        _check(
            "crn_structural_pairing",
            "pass"
            if crn_manifest.get("structural_crn_pairing_ready") is True
            else "blocked_crn_pairing_not_ready",
            observed=str(crn_manifest.get("structural_crn_pairing_ready", "missing")),
            review_action="Resolve structural CRN blockers before paired policy claims.",
        ),
        _check(
            "replication_statistics_structure",
            "pass"
            if replication_manifest.get("paired_statistics_structurally_ready") is True
            else "blocked_replication_statistics_not_ready",
            observed=str(
                replication_manifest.get(
                    "paired_statistics_structurally_ready", "missing"
                )
            ),
            review_action="Regenerate paired statistics or resolve replication audit blockers.",
        ),
        _check(
            "replication_adequacy_human_review",
            "needs_human_review_replication_adequacy",
            observed=(
                f"{replication_manifest.get('needs_human_review_count', 'missing')} "
                "replication audit rows need review"
            ),
            review_action="Decide whether seed count, finite paired counts, and CI method are adequate for release-scope claims.",
        ),
        _check(
            "multiple_comparison_boundary",
            "needs_human_review_multiple_comparisons",
            observed=str(statistics_manifest.get("multiple_comparison_method", "")),
            review_action="Select a multiplicity procedure or keep secondary comparisons exploratory.",
        ),
        _check(
            "formal_experiment_acceptance",
            "blocked_missing_experiment_acceptance_record",
            observed="data/manifests/experiment_acceptance.json absent unless reviewer supplies it",
            review_action="Create the formal experiment decision record only after graph, input, CRN, counts, and claim-scope review.",
        ),
    ]


def _check(check_id: str, status: str, *, observed: str, review_action: str) -> dict[str, str]:
    return {
        "check_id": check_id,
        "status": status,
        "observed": observed,
        "review_action": review_action,
        "claim_boundary": EXPERIMENT_STATISTICAL_PLAN_CLAIM_BOUNDARY,
    }


def _profile(design: Mapping[str, Any], profile_id: str) -> Mapping[str, Any]:
    profiles = design.get("profiles", {})
    if isinstance(profiles, Mapping):
        profile = profiles.get(profile_id, {})
        if isinstance(profile, Mapping):
            return profile
    return {}


def _load_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    return value if isinstance(value, dict) else {}


def _string_sequence(value: object) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [str(item) for item in value]


def _integer_sequence(value: object) -> list[int]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    integers: list[int] = []
    for item in value:
        try:
            integers.append(int(item))
        except (TypeError, ValueError):
            continue
    return integers


def _int(value: object) -> int:
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
    "DEFAULT_EXPERIMENT_STATISTICAL_PLAN_DOC_PATH",
    "DEFAULT_EXPERIMENT_STATISTICAL_PLAN_MANIFEST_PATH",
    "EXPERIMENT_STATISTICAL_PLAN_CLAIM_BOUNDARY",
    "PRIMARY_COMPARISONS",
    "PRIMARY_METRICS",
    "SECONDARY_COMPARISON_BOUNDARY",
    "build_experiment_statistical_plan",
    "build_experiment_statistical_plan_markdown",
    "write_experiment_statistical_plan",
]
