"""Non-approval templates for formal final-study acceptance decisions.

The templates generated here are reviewer worksheets. They intentionally set
``accepted: false`` and live outside the formal acceptance paths so they cannot
close final-study gates by accident.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.realworld.experiment_acceptance import summarize_experiment_acceptance
from src.realworld.final_audit_acceptance import summarize_final_audit_acceptance
from src.realworld.final_study_readiness import audit_final_study_readiness
from src.realworld.graph_scale_acceptance import summarize_graph_scale_acceptance
from src.realworld.manuscript_acceptance import summarize_manuscript_acceptance
from src.realworld.manifest_timestamp import (
    preserve_generated_at_when_unchanged,
    write_json_manifest_if_changed,
    write_text_if_changed,
)
from src.realworld.parameter_acceptance import (
    REQUIRED_COLUMNS as PARAMETER_ACCEPTANCE_COLUMNS,
    summarize_parameter_acceptance,
)
from src.realworld.parameter_review_packet import build_parameter_review_rows
from src.realworld.pilot_acceptance import summarize_pilot_acceptance
from src.realworld.provenance_acceptance import summarize_provenance_acceptance
from src.realworld.reproducibility_acceptance import (
    summarize_reproducibility_acceptance,
)
from src.realworld.sensitivity_acceptance import summarize_sensitivity_acceptance
from src.realworld.validation_acceptance import summarize_validation_acceptance


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ACCEPTANCE_TEMPLATE_DIR = (
    PROJECT_ROOT / "data" / "manifests" / "acceptance_templates"
)
DEFAULT_ACCEPTANCE_TEMPLATE_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "acceptance_decision_template_manifest.json"
)
DEFAULT_ACCEPTANCE_TEMPLATE_DOC_PATH = (
    PROJECT_ROOT / "docs" / "acceptance_decision_templates.md"
)
DEFAULT_PARAMETER_ACCEPTANCE_TEMPLATE_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "parameter_acceptance_template.csv"
)
TEMPLATE_CLAIM_BOUNDARY = (
    "TEMPLATE ONLY: this is not approval, not calibrated real-world validation, "
    "and not operational routing. Keep accepted false until a reviewer replaces "
    "all placeholders and records a source-backed decision."
)


@dataclass(frozen=True)
class AcceptanceTemplateSpec:
    """One generated JSON acceptance-template target."""

    gate_id: str
    target_artifact: str
    filename: str
    template: Mapping[str, Any]


def write_acceptance_decision_templates(
    *,
    template_dir: str | Path = DEFAULT_ACCEPTANCE_TEMPLATE_DIR,
    manifest_path: str | Path = DEFAULT_ACCEPTANCE_TEMPLATE_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_ACCEPTANCE_TEMPLATE_DOC_PATH,
    parameter_template_path: str | Path = DEFAULT_PARAMETER_ACCEPTANCE_TEMPLATE_PATH,
) -> dict[str, Any]:
    """Write all formal-decision templates and a non-acceptance manifest."""

    output_dir = Path(template_dir)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    parameter_output = Path(parameter_template_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)
    parameter_output.parent.mkdir(parents=True, exist_ok=True)

    final_audit = audit_final_study_readiness()
    specs = build_acceptance_decision_template_specs(final_audit=final_audit)
    written_json_paths: list[str] = []
    non_ready_summaries: dict[str, Any] = {}
    for spec in specs:
        target = output_dir / spec.filename
        target.write_text(
            json.dumps(dict(spec.template), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        written_json_paths.append(_display_path(target))
        non_ready_summaries[spec.gate_id] = _summarize_template_non_ready(
            spec.gate_id,
            target,
        )

    parameter_rows = build_parameter_acceptance_template_rows()
    with parameter_output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=PARAMETER_ACCEPTANCE_COLUMNS,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(parameter_rows)
    if parameter_rows:
        non_ready_summaries["parameter_acceptance"] = summarize_parameter_acceptance(
            parameter_output
        )
    else:
        non_ready_summaries["parameter_acceptance"] = {
            "record_present": False,
            "ready_parameter_count": 0,
            "accepted_parameter_count": 0,
            "ready_parameters": [],
            "remaining_blockers": [
                "create reviewed parameter acceptance records only for weak assumptions retained in final claims"
            ],
        }

    value = _build_manifest(
        specs=specs,
        json_paths=written_json_paths,
        parameter_template_path=parameter_output,
        parameter_row_count=len(parameter_rows),
        final_audit=final_audit,
        non_ready_summaries=non_ready_summaries,
    )
    preserve_generated_at_when_unchanged(value, manifest)
    write_json_manifest_if_changed(value, manifest, sort_keys=True)
    write_text_if_changed(build_acceptance_decision_template_markdown(value), doc)
    return value


def build_acceptance_decision_template_specs(
    *,
    final_audit: Mapping[str, Any] | None = None,
) -> list[AcceptanceTemplateSpec]:
    """Return JSON templates for formal acceptance artifacts."""

    audit = final_audit or audit_final_study_readiness()
    gate_map = {str(gate["gate_id"]): gate for gate in audit["gates"]}
    gates = {
        gate_id: gate_map.get(gate_id, {})
        for gate_id in (
            "pilot_region_accepted",
            "graph_scale_strategy",
            "data_provenance",
            "validation_package",
            "sensitivity_analysis",
            "full_experiment_output",
            "manuscript_report_alignment",
            "reproducibility",
            "final_audit",
        )
    }
    common = _common_template_fields()

    graph_details = _details(gates["graph_scale_strategy"])
    validation_details = _details(gates["validation_package"])
    sensitivity_details = _details(gates["sensitivity_analysis"])
    experiment_details = _details(gates["full_experiment_output"])
    repro_details = _details(gates["reproducibility"])

    return [
        AcceptanceTemplateSpec(
            gate_id="pilot_region_accepted",
            target_artifact="data/manifests/pilot_acceptance.json",
            filename="pilot_acceptance_template.json",
            template={
                **common,
                "acceptance_scope": "REVIEW_REQUIRED",
                "privacy_review_complete": False,
                "graph_scale_decision": "corridor_abstraction",
                "evidence_paths": _evidence(gates["pilot_region_accepted"]),
            },
        ),
        AcceptanceTemplateSpec(
            gate_id="graph_scale_strategy",
            target_artifact="data/manifests/graph_scale_acceptance.json",
            filename="graph_scale_acceptance_template.json",
            template={
                **common,
                "graph_scale_decision": "corridor_abstraction",
                "source_graph_nodes": _positive_or_one(
                    graph_details.get("source_graph_nodes")
                ),
                "source_graph_edges": _positive_or_one(
                    graph_details.get("source_graph_edges")
                ),
                "analysis_graph_nodes": _positive_or_one(
                    graph_details.get("analysis_graph_nodes")
                ),
                "analysis_graph_edges": _positive_or_one(
                    graph_details.get("analysis_graph_edges")
                ),
                "corridor_reduction_accepted": False,
                "alternate_corridor_sensitivity_reviewed": False,
                "evidence_paths": _evidence(gates["graph_scale_strategy"]),
            },
        ),
        AcceptanceTemplateSpec(
            gate_id="data_provenance",
            target_artifact="data/manifests/provenance_acceptance.json",
            filename="provenance_acceptance_template.json",
            template={
                **common,
                "source_snapshot_reviewed": False,
                "license_attribution_reviewed": False,
                "privacy_abstraction_reviewed": False,
                "cache_manifest_reviewed": False,
                "reproducibility_manifest_reviewed": False,
                "source_urls_or_citations": ["REVIEW_REQUIRED_SOURCE_OR_CITATION"],
                "data_snapshot_paths": [
                    "data/cache/pilot_region_road.graphml",
                    "data/cache/pilot_region_road_manifest.json",
                ],
                "evidence_paths": _evidence(gates["data_provenance"]),
            },
        ),
        AcceptanceTemplateSpec(
            gate_id="validation_package",
            target_artifact="data/manifests/validation_acceptance.json",
            filename="validation_acceptance_template.json",
            template={
                **common,
                "validation_scope": "REVIEW_REQUIRED",
                "benchmark_strategy": "documented_plausibility_only",
                "internal_validation_reviewed": False,
                "external_plausibility_reviewed": False,
                "benchmark_validation_reviewed": False,
                "benchmark_is_not_ground_truth_acknowledged": False,
                "evidence_paths": _evidence(gates["validation_package"]),
                "current_review_packet_row_count": validation_details.get(
                    "review_packet_row_count"
                ),
            },
        ),
        AcceptanceTemplateSpec(
            gate_id="sensitivity_analysis",
            target_artifact="data/manifests/sensitivity_acceptance.json",
            filename="sensitivity_acceptance_template.json",
            template={
                **common,
                "sensitivity_method": "salib_morris",
                "result_scope": "REVIEW_REQUIRED",
                "expected_row_count": _positive_or_one(
                    sensitivity_details.get("row_count")
                ),
                "expected_summary_row_count": _positive_or_one(
                    sensitivity_details.get("summary_row_count")
                ),
                "graph_scope_accepted": False,
                "parameter_ranges_reviewed": False,
                "salib_output_reviewed": False,
                "nan_or_masked_values_reviewed": False,
                "sobol_requirement_decision": "required_pending",
                "evidence_paths": _evidence(gates["sensitivity_analysis"]),
            },
        ),
        AcceptanceTemplateSpec(
            gate_id="full_experiment_output",
            target_artifact="data/manifests/experiment_acceptance.json",
            filename="experiment_acceptance_template.json",
            template={
                **common,
                "run_profile": "full_pilot",
                "expected_row_count": _positive_or_one(
                    experiment_details.get("row_count")
                ),
                "expected_summary_row_count": _positive_or_one(
                    experiment_details.get("summary_row_count")
                ),
                "policy_count": 7,
                "scenario_count": 9,
                "seed_count": 30,
                "graph_scope_accepted": False,
                "input_validation_accepted": False,
                "scenario_policy_seed_design_reviewed": False,
                "common_random_numbers_reviewed": False,
                "evidence_paths": _evidence(gates["full_experiment_output"]),
            },
        ),
        AcceptanceTemplateSpec(
            gate_id="manuscript_report_alignment",
            target_artifact="data/manifests/manuscript_acceptance.json",
            filename="manuscript_acceptance_template.json",
            template={
                **common,
                "paper_reviewed": False,
                "korean_report_reviewed": False,
                "docx_regenerated": False,
                "figure_table_manifest_reviewed": False,
                "evidence_gates_reviewed": False,
                "result_claims_aligned": False,
                "evidence_paths": _evidence(gates["manuscript_report_alignment"]),
            },
        ),
        AcceptanceTemplateSpec(
            gate_id="reproducibility",
            target_artifact="data/manifests/reproducibility_acceptance.json",
            filename="reproducibility_acceptance_template.json",
            template={
                **common,
                "clean_checkout_tested": False,
                "validation_ladder_passed": False,
                "artifact_regeneration_tested": False,
                "manifest_paths_reviewed": False,
                "no_runtime_cloned_repo_imports": False,
                "expected_validation_command_count": _positive_or_one(
                    repro_details.get("validation_command_count")
                ),
                "evidence_paths": _evidence(gates["reproducibility"]),
            },
        ),
        AcceptanceTemplateSpec(
            gate_id="final_audit",
            target_artifact="data/manifests/final_audit_acceptance.json",
            filename="final_audit_acceptance_template.json",
            template={
                **common,
                "final_study_ready": False,
                "prompt_to_artifact_checklist_reviewed": False,
                "all_gate_evidence_reviewed": False,
                "no_proxy_completion_reviewed": False,
                "expected_gate_count": _positive_or_one(audit.get("gate_count")),
                "reviewed_gate_ids": list(audit.get("ready_gate_ids", []))
                + list(audit.get("blocked_gate_ids", [])),
                "ready_gate_ids": list(audit.get("ready_gate_ids", [])),
                "blocked_gate_ids": list(audit.get("blocked_gate_ids", [])),
                "evidence_paths": _evidence(gates["final_audit"]),
            },
        ),
    ]


def build_parameter_acceptance_template_rows() -> list[dict[str, str]]:
    """Return non-approval parameter-acceptance template rows for weak inputs."""

    rows = []
    for review_row in build_parameter_review_rows():
        if str(review_row.get("weak_for_final_claim", "")).lower() != "true":
            continue
        rows.append(
            {
                "parameter": str(review_row["parameter"]),
                "accepted": "false",
                "accepted_by": "REVIEW_REQUIRED",
                "accepted_date": "REVIEW_REQUIRED",
                "acceptance_scope": "REVIEW_REQUIRED",
                "claim_boundary": TEMPLATE_CLAIM_BOUNDARY,
                "sensitivity_reviewed": "false",
                "evidence_paths": str(review_row.get("candidate_artifacts", ""))
                or "REVIEW_REQUIRED",
                "notes": (
                    "Template row only. Recommended upgrade: "
                    + str(review_row.get("recommended_upgrade", "REVIEW_REQUIRED"))
                ),
            }
        )
    return rows


def build_acceptance_decision_template_markdown(manifest: Mapping[str, Any]) -> str:
    """Render a concise human guide for the generated templates."""

    lines = [
        "# Formal Review Templates",
        "",
        TEMPLATE_CLAIM_BOUNDARY,
        "",
        "These files are copy/edit starting points for human reviewers. They are not formal acceptance artifacts and do not close final-study gates.",
        "",
        f"- Final-study ready at generation: `{str(manifest.get('final_study_ready', False)).lower()}`",
        f"- JSON templates: {manifest.get('json_template_count', 0)}",
        f"- Parameter acceptance template rows: {manifest.get('parameter_template_row_count', 0)}",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        "",
        "## JSON Templates",
        "",
        "| Gate | Template | Formal Target | Current Status |",
        "| --- | --- | --- | --- |",
    ]
    for row in manifest.get("templates", []):
        if not isinstance(row, Mapping):
            continue
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row.get('gate_id', '')}`",
                    f"`{row.get('template_path', '')}`",
                    f"`{row.get('target_artifact', '')}`",
                    f"`{row.get('current_status', '')}`",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Parameter Template",
            "",
            f"- Template: `{manifest.get('parameter_template_path', '')}`",
            "- Formal target: `data/parameters/parameter_acceptance.csv`",
            "- Keep `accepted=false` until weak assumptions are reviewed and retained inside a conservative claim boundary.",
            "",
            "## Required Use",
            "",
            "- Review the corresponding packet in `docs/review_packets/` first.",
            "- Replace every `REVIEW_REQUIRED` placeholder with a real source-backed decision.",
            "- Copy a template to the formal target path only after review.",
            "- Re-run `scripts/audit_final_study_readiness.py --fail-on-blockers` after formal records are created.",
            "",
        ]
    )
    return "\n".join(lines)


def summarize_acceptance_decision_templates(
    path: str | Path = DEFAULT_ACCEPTANCE_TEMPLATE_MANIFEST_PATH,
) -> dict[str, Any]:
    """Return conservative status for generated acceptance-decision templates."""

    manifest_path = Path(path)
    if not manifest_path.exists():
        return {
            "manifest_present": False,
            "path": _display_path(manifest_path),
            "json_template_count": 0,
            "parameter_template_row_count": 0,
            "can_mark_complete": False,
            "final_study_ready": False,
            "formal_acceptance_created": False,
            "remaining_blockers": ["run scripts/write_acceptance_decision_templates.py"],
        }
    with manifest_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, Mapping):
        raise ValueError(f"{manifest_path} must contain a JSON object")
    return {
        "manifest_present": True,
        "path": _display_path(manifest_path),
        "json_template_count": int(value.get("json_template_count", 0)),
        "parameter_template_row_count": int(
            value.get("parameter_template_row_count", 0)
        ),
        "can_mark_complete": bool(value.get("can_mark_complete", False)),
        "final_study_ready": bool(value.get("final_study_ready", False)),
        "formal_acceptance_created": bool(
            value.get("formal_acceptance_created", False)
        ),
        "remaining_blockers": [
            "templates are non-approval aids; create formal acceptance records only after review"
        ],
    }


def _build_manifest(
    *,
    specs: Sequence[AcceptanceTemplateSpec],
    json_paths: Sequence[str],
    parameter_template_path: Path,
    parameter_row_count: int,
    final_audit: Mapping[str, Any],
    non_ready_summaries: Mapping[str, Any],
) -> dict[str, Any]:
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    templates = []
    for spec, path in zip(specs, json_paths, strict=True):
        gate = _gate_by_id(final_audit, spec.gate_id)
        templates.append(
            {
                "gate_id": spec.gate_id,
                "template_path": path,
                "target_artifact": spec.target_artifact,
                "current_status": "ready" if bool(gate.get("ready")) else "blocked",
                "blocker_count": len(gate.get("blockers", []))
                if isinstance(gate.get("blockers", []), list)
                else 0,
            }
        )
    return {
        "schema_version": 1,
        "generated_at": generated_at,
        "claim_boundary": TEMPLATE_CLAIM_BOUNDARY,
        "result_scope": "formal_acceptance_templates_not_approval",
        "final_study_ready": bool(final_audit.get("final_study_ready", False)),
        "can_mark_complete": False,
        "formal_acceptance_created": False,
        "json_template_count": len(json_paths),
        "parameter_template_row_count": parameter_row_count,
        "parameter_template_path": _display_path(parameter_template_path),
        "templates": templates,
        "non_ready_summary_keys": sorted(non_ready_summaries),
        "review_items": [
            "do not treat templates as acceptance records",
            "copy templates to formal target paths only after source-backed review",
            "keep accepted false unless the corresponding gate evidence is genuinely accepted",
            "rerun final-study readiness after any formal acceptance artifact is added",
        ],
    }


def _summarize_template_non_ready(gate_id: str, path: Path) -> dict[str, Any]:
    if gate_id == "pilot_region_accepted":
        return summarize_pilot_acceptance(path)
    if gate_id == "graph_scale_strategy":
        return summarize_graph_scale_acceptance(path)
    if gate_id == "data_provenance":
        return summarize_provenance_acceptance(path)
    if gate_id == "validation_package":
        return summarize_validation_acceptance(path)
    if gate_id == "sensitivity_analysis":
        return summarize_sensitivity_acceptance(path)
    if gate_id == "full_experiment_output":
        return summarize_experiment_acceptance(path)
    if gate_id == "manuscript_report_alignment":
        return summarize_manuscript_acceptance(path)
    if gate_id == "reproducibility":
        return summarize_reproducibility_acceptance(path)
    if gate_id == "final_audit":
        return summarize_final_audit_acceptance(path)
    raise ValueError(f"unsupported gate template: {gate_id}")


def _common_template_fields() -> dict[str, Any]:
    return {
        "record_type": "formal_acceptance_template_not_approval",
        "template_only": True,
        "region_id": "songpa_public_demo",
        "accepted": False,
        "accepted_by": "REVIEW_REQUIRED",
        "accepted_date": "REVIEW_REQUIRED",
        "claim_boundary": TEMPLATE_CLAIM_BOUNDARY,
    }


def _gate_by_id(final_audit: Mapping[str, Any], gate_id: str) -> Mapping[str, Any]:
    gates = final_audit.get("gates", [])
    if not isinstance(gates, list):
        return {}
    for gate in gates:
        if isinstance(gate, Mapping) and str(gate.get("gate_id")) == gate_id:
            return gate
    return {}


def _details(gate: Mapping[str, Any]) -> Mapping[str, Any]:
    value = gate.get("details", {})
    return value if isinstance(value, Mapping) else {}


def _evidence(gate: Mapping[str, Any]) -> list[str]:
    value = gate.get("evidence", [])
    if not isinstance(value, list) or not value:
        return ["REVIEW_REQUIRED_EVIDENCE_PATH"]
    return [str(item) for item in value if str(item).strip()]


def _positive_or_one(value: object) -> int:
    if isinstance(value, bool):
        return 1
    if isinstance(value, int) and value > 0:
        return value
    return 1


def _display_path(path: str | Path) -> str:
    value = Path(path)
    try:
        return value.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return value.as_posix()


__all__ = [
    "DEFAULT_ACCEPTANCE_TEMPLATE_DIR",
    "DEFAULT_ACCEPTANCE_TEMPLATE_DOC_PATH",
    "DEFAULT_ACCEPTANCE_TEMPLATE_MANIFEST_PATH",
    "DEFAULT_PARAMETER_ACCEPTANCE_TEMPLATE_PATH",
    "TEMPLATE_CLAIM_BOUNDARY",
    "AcceptanceTemplateSpec",
    "build_acceptance_decision_template_markdown",
    "build_acceptance_decision_template_specs",
    "build_parameter_acceptance_template_rows",
    "summarize_acceptance_decision_templates",
    "write_acceptance_decision_templates",
]
