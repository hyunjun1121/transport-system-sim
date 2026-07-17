"""Aggregate formal acceptance artifacts into one conservative intake audit."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from src.realworld.experiment_acceptance import summarize_experiment_acceptance
from src.realworld.final_audit_acceptance import summarize_final_audit_acceptance
from src.realworld.final_study_readiness import audit_final_study_readiness
from src.realworld.formal_acceptance_guard import (
    audit_formal_acceptance_artifacts,
)
from src.realworld.formal_evidence_path_audit import (
    audit_formal_evidence_paths,
    write_formal_evidence_path_audit,
)
from src.realworld.graph_scale_acceptance import summarize_graph_scale_acceptance
from src.realworld.manuscript_acceptance import summarize_manuscript_acceptance
from src.realworld.parameter_acceptance import summarize_parameter_acceptance
from src.realworld.pilot_acceptance import summarize_pilot_acceptance
from src.realworld.provenance_acceptance import summarize_provenance_acceptance
from src.realworld.reproducibility_acceptance import (
    summarize_reproducibility_acceptance,
)
from src.realworld.road_override_audit import (
    audit_road_class_override_application,
    audit_road_class_override_evidence,
)
from src.realworld.sensitivity_acceptance import summarize_sensitivity_acceptance
from src.realworld.validation_acceptance import summarize_validation_acceptance


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FORMAL_ACCEPTANCE_PACKAGE_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "formal_acceptance_package_audit.json"
)
DEFAULT_FORMAL_ACCEPTANCE_PACKAGE_DOC_PATH = (
    PROJECT_ROOT / "docs" / "formal_acceptance_package_audit.md"
)

CLAIM_BOUNDARY = (
    "This package validates formal acceptance artifacts supplied by reviewers. "
    "It does not create approvals, invent evidence, or convert scaffold outputs "
    "into calibrated real-world findings."
)


@dataclass(frozen=True)
class FormalGateSpec:
    """One formal acceptance artifact expected by the final study."""

    gate_id: str
    label: str
    path: Path
    summarizer: Callable[[str | Path], dict[str, Any]]


def build_formal_acceptance_package_summary(
    *,
    root: str | Path = PROJECT_ROOT,
) -> dict[str, Any]:
    """Return one intake summary for all formal acceptance artifacts."""

    project_root = Path(root)
    gates = [_evaluate_gate(spec) for spec in _formal_gate_specs(project_root)]
    guard = audit_formal_acceptance_artifacts(project_root=project_root)
    evidence_paths = audit_formal_evidence_paths(root=project_root)
    final_study = audit_final_study_readiness()

    ready_count = sum(1 for gate in gates if gate["ready"])
    invalid_count = sum(1 for gate in gates if gate["status"] == "invalid")
    blocked_count = len(gates) - ready_count
    blockers: list[str] = []
    for gate in gates:
        for blocker in gate["remaining_blockers"]:
            blockers.append(f"{gate['gate_id']}: {blocker}")
    for blocker in guard.get("remaining_blockers", []):
        blockers.append(f"formal_acceptance_guard: {blocker}")
    for blocker in evidence_paths.get("remaining_blockers", []):
        blockers.append(f"formal_evidence_paths: {blocker}")
    if not final_study.get("final_study_ready", False):
        blockers.append(
            "final_study_readiness: final-study readiness audit is still false"
        )

    formal_acceptance_ready = (
        ready_count == len(gates)
        and invalid_count == 0
        and bool(guard.get("can_mark_complete", False))
    )
    can_mark_complete = formal_acceptance_ready and bool(
        final_study.get("final_study_ready", False)
    )
    return {
        "schema_version": 1,
        "claim_boundary": CLAIM_BOUNDARY,
        "gate_count": len(gates),
        "ready_gate_count": ready_count,
        "blocked_gate_count": blocked_count,
        "invalid_gate_count": invalid_count,
        "formal_acceptance_ready": formal_acceptance_ready,
        "final_study_ready": bool(final_study.get("final_study_ready", False)),
        "can_mark_complete": can_mark_complete,
        "gates": gates,
        "formal_acceptance_guard": {
            "artifact_count": guard.get("artifact_count", 0),
            "present_count": guard.get("present_count", 0),
            "missing_count": guard.get("missing_count", 0),
            "template_or_placeholder_count": guard.get(
                "template_or_placeholder_count",
                0,
            ),
            "formal_acceptance_ready": guard.get("formal_acceptance_ready", False),
            "can_mark_complete": guard.get("can_mark_complete", False),
        },
        "formal_evidence_path_audit": {
            "artifact_count": evidence_paths.get("artifact_count", 0),
            "present_artifact_count": evidence_paths.get("present_artifact_count", 0),
            "evidence_item_count": evidence_paths.get("evidence_item_count", 0),
            "missing_local_evidence_count": evidence_paths.get(
                "missing_local_evidence_count",
                0,
            ),
            "placeholder_evidence_count": evidence_paths.get(
                "placeholder_evidence_count",
                0,
            ),
            "empty_evidence_record_count": evidence_paths.get(
                "empty_evidence_record_count",
                0,
            ),
            "can_mark_complete": evidence_paths.get("can_mark_complete", False),
        },
        "final_study_readiness": {
            "gate_count": final_study.get("gate_count", 0),
            "ready_gate_ids": list(final_study.get("ready_gate_ids", [])),
            "blocked_gate_ids": list(final_study.get("blocked_gate_ids", [])),
            "verdict": final_study.get("verdict", ""),
        },
        "remaining_blockers": blockers,
    }


def write_formal_acceptance_package_audit(
    *,
    root: str | Path = PROJECT_ROOT,
    manifest_path: str | Path = DEFAULT_FORMAL_ACCEPTANCE_PACKAGE_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_FORMAL_ACCEPTANCE_PACKAGE_DOC_PATH,
) -> dict[str, Any]:
    """Write JSON and Markdown package-audit artifacts."""

    summary = build_formal_acceptance_package_summary(root=root)
    project_root = Path(root)
    write_formal_evidence_path_audit(
        root=project_root,
        manifest_path=project_root
        / "data"
        / "manifests"
        / "formal_evidence_path_audit.json",
        doc_path=project_root / "docs" / "formal_evidence_path_audit.md",
    )
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    doc.write_text(build_formal_acceptance_package_markdown(summary), encoding="utf-8")
    return summary


def build_formal_acceptance_package_markdown(summary: dict[str, Any]) -> str:
    """Return a human-readable package intake report."""

    lines = [
        "# Formal Acceptance Package Audit",
        "",
        summary.get("claim_boundary", CLAIM_BOUNDARY),
        "",
        "## Verdict",
        "",
        f"- Formal acceptance ready: `{str(summary.get('formal_acceptance_ready', False)).lower()}`",
        f"- Final-study ready: `{str(summary.get('final_study_ready', False)).lower()}`",
        f"- Can mark complete: `{str(summary.get('can_mark_complete', False)).lower()}`",
        f"- Ready formal gates: {summary.get('ready_gate_count', 0)} / {summary.get('gate_count', 0)}",
        f"- Invalid formal gates: {summary.get('invalid_gate_count', 0)}",
        "",
        "## Gate Intake",
        "",
        "| Gate | Status | Artifact | Blockers |",
        "| --- | --- | --- | --- |",
    ]
    for gate in summary.get("gates", []):
        blockers = gate.get("remaining_blockers", [])
        blocker_text = "<br>".join(str(item) for item in blockers) or "none"
        lines.append(
            "| {label} | {status} | `{path}` | {blockers} |".format(
                label=_cell(str(gate.get("label", gate.get("gate_id", "")))),
                status=_cell(str(gate.get("status", ""))),
                path=_cell(str(gate.get("path", ""))),
                blockers=_cell(blocker_text),
            )
        )

    guard = summary.get("formal_acceptance_guard", {})
    readiness = summary.get("final_study_readiness", {})
    evidence_paths = summary.get("formal_evidence_path_audit", {})
    lines.extend(
        [
            "",
            "## Guard Summary",
            "",
            f"- Formal artifacts present: {guard.get('present_count', 0)} / {guard.get('artifact_count', 0)}",
            f"- Missing formal artifacts: {guard.get('missing_count', 0)}",
            f"- Template or placeholder artifacts detected: {guard.get('template_or_placeholder_count', 0)}",
            f"- Guard can mark complete: `{str(guard.get('can_mark_complete', False)).lower()}`",
            "",
            "## Evidence Path Summary",
            "",
            f"- Evidence items: {evidence_paths.get('evidence_item_count', 0)}",
            f"- Missing local evidence: {evidence_paths.get('missing_local_evidence_count', 0)}",
            f"- Placeholder evidence values: {evidence_paths.get('placeholder_evidence_count', 0)}",
            f"- Empty evidence records: {evidence_paths.get('empty_evidence_record_count', 0)}",
            f"- Evidence-path audit can mark complete: `{str(evidence_paths.get('can_mark_complete', False)).lower()}`",
            "",
            "## Final Readiness Cross-Check",
            "",
            f"- Final-study verdict: `{readiness.get('verdict', '')}`",
            f"- Ready plan gates: {len(readiness.get('ready_gate_ids', []))} / {readiness.get('gate_count', 0)}",
            f"- Blocked plan gates: {len(readiness.get('blocked_gate_ids', []))} / {readiness.get('gate_count', 0)}",
            "",
            "## Use",
            "",
            "Run this audit after a reviewer adds or edits any formal acceptance artifact. A `ready` package only means the repository has reviewed acceptance evidence; it still must agree with the final-study readiness audit before the active goal can be marked complete.",
            "",
        ]
    )
    return "\n".join(lines)


def _formal_gate_specs(root: Path) -> list[FormalGateSpec]:
    return [
        FormalGateSpec(
            "pilot_region_accepted",
            "Pilot Region Acceptance",
            root / "data" / "manifests" / "pilot_acceptance.json",
            summarize_pilot_acceptance,
        ),
        FormalGateSpec(
            "graph_scale_strategy",
            "Graph-Scale Acceptance",
            root / "data" / "manifests" / "graph_scale_acceptance.json",
            summarize_graph_scale_acceptance,
        ),
        FormalGateSpec(
            "data_provenance",
            "Source/License/Provenance Acceptance",
            root / "data" / "manifests" / "provenance_acceptance.json",
            summarize_provenance_acceptance,
        ),
        FormalGateSpec(
            "parameter_acceptance",
            "Weak-Parameter Acceptance",
            root / "data" / "parameters" / "parameter_acceptance.csv",
            _summarize_parameter_acceptance_for_package,
        ),
        FormalGateSpec(
            "road_class_overrides",
            "Road-Class Override Acceptance",
            root / "data" / "parameters" / "road_class_overrides.csv",
            _summarize_road_overrides_for_package,
        ),
        FormalGateSpec(
            "validation_package",
            "Validation Acceptance",
            root / "data" / "manifests" / "validation_acceptance.json",
            summarize_validation_acceptance,
        ),
        FormalGateSpec(
            "sensitivity_analysis",
            "Sensitivity Acceptance",
            root / "data" / "manifests" / "sensitivity_acceptance.json",
            summarize_sensitivity_acceptance,
        ),
        FormalGateSpec(
            "full_experiment_output",
            "Experiment Acceptance",
            root / "data" / "manifests" / "experiment_acceptance.json",
            summarize_experiment_acceptance,
        ),
        FormalGateSpec(
            "manuscript_report_alignment",
            "Manuscript/Report Acceptance",
            root / "data" / "manifests" / "manuscript_acceptance.json",
            summarize_manuscript_acceptance,
        ),
        FormalGateSpec(
            "reproducibility",
            "Reproducibility Acceptance",
            root / "data" / "manifests" / "reproducibility_acceptance.json",
            summarize_reproducibility_acceptance,
        ),
        FormalGateSpec(
            "final_audit_document",
            "Final Study Audit Document",
            root / "docs" / "final_study_audit.md",
            _summarize_final_study_audit_document,
        ),
        FormalGateSpec(
            "final_audit",
            "Final Audit Acceptance",
            root / "data" / "manifests" / "final_audit_acceptance.json",
            summarize_final_audit_acceptance,
        ),
    ]


def _evaluate_gate(spec: FormalGateSpec) -> dict[str, Any]:
    try:
        summary = spec.summarizer(spec.path)
        blockers = _remaining_blockers(summary)
        ready = _summary_ready(summary)
        status = "ready" if ready else "blocked"
    except Exception as exc:  # pragma: no cover - exercised through script paths
        summary = {
            "record_present": spec.path.exists(),
            "remaining_blockers": [f"invalid formal artifact: {exc}"],
        }
        blockers = list(summary["remaining_blockers"])
        ready = False
        status = "invalid"

    return {
        "gate_id": spec.gate_id,
        "label": spec.label,
        "path": _display_path(spec.path),
        "record_present": bool(summary.get("record_present", spec.path.exists())),
        "ready": ready,
        "status": status,
        "remaining_blockers": blockers,
        "summary": summary,
    }


def _summarize_parameter_acceptance_for_package(path: str | Path) -> dict[str, Any]:
    summary = summarize_parameter_acceptance(path)
    ready = (
        bool(summary.get("record_present", False))
        and not summary.get("remaining_blockers", [])
        and int(summary.get("ready_parameter_count", 0)) > 0
    )
    blockers = list(summary.get("remaining_blockers", []))
    if not summary.get("record_present", False):
        blockers.append("parameter_acceptance.csv is missing")
    elif int(summary.get("ready_parameter_count", 0)) <= 0:
        blockers.append("parameter_acceptance.csv has no ready accepted parameter rows")
    return {
        **summary,
        "acceptance_ready": ready,
        "remaining_blockers": blockers,
    }


def _summarize_road_overrides_for_package(path: str | Path) -> dict[str, Any]:
    evidence = audit_road_class_override_evidence(path)
    application = audit_road_class_override_application(override_path=path)
    blockers = list(evidence.get("remaining_blockers", [])) + list(
        application.get("remaining_blockers", [])
    )
    ready = bool(evidence.get("publication_ready", False)) and bool(
        application.get("publication_ready", False)
    )
    return {
        "acceptance_ready": ready,
        "record_present": bool(evidence.get("override_table_present", False)),
        "path": evidence.get("path", _display_path(Path(path))),
        "evidence_publication_ready": evidence.get("publication_ready", False),
        "application_publication_ready": application.get("publication_ready", False),
        "remaining_blockers": blockers,
        "evidence": evidence,
        "application": application,
    }


def _summarize_final_study_audit_document(path: str | Path) -> dict[str, Any]:
    audit_path = Path(path)
    if not audit_path.exists():
        return {
            "acceptance_ready": False,
            "record_present": False,
            "path": _display_path(audit_path),
            "remaining_blockers": [
                "create docs/final_study_audit.md after all other gates close"
            ],
        }
    text = audit_path.read_text(encoding="utf-8", errors="replace")
    blockers: list[str] = []
    lowered = text.lower()
    if "final_study_ready: true" not in lowered and "final-study ready: `true`" not in lowered:
        blockers.append("final study audit document does not state final_study_ready true")
    if "not operational" not in lowered:
        blockers.append("final study audit document must include a not-operational claim boundary")
    if "current-state completion gap audit" in lowered:
        blockers.append("current-state completion gap audit text cannot be used as final audit")
    return {
        "acceptance_ready": not blockers,
        "record_present": True,
        "path": _display_path(audit_path),
        "remaining_blockers": blockers,
    }


def _summary_ready(summary: dict[str, Any]) -> bool:
    if "acceptance_ready" in summary:
        return bool(summary["acceptance_ready"])
    if "publication_ready" in summary:
        return bool(summary["publication_ready"])
    return bool(summary.get("ready", False)) and not summary.get(
        "remaining_blockers",
        [],
    )


def _remaining_blockers(summary: dict[str, Any]) -> list[str]:
    blockers = summary.get("remaining_blockers", [])
    if isinstance(blockers, list):
        return [str(item) for item in blockers if str(item)]
    return [str(blockers)] if blockers else []


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


__all__ = [
    "CLAIM_BOUNDARY",
    "DEFAULT_FORMAL_ACCEPTANCE_PACKAGE_DOC_PATH",
    "DEFAULT_FORMAL_ACCEPTANCE_PACKAGE_MANIFEST_PATH",
    "FormalGateSpec",
    "build_formal_acceptance_package_markdown",
    "build_formal_acceptance_package_summary",
    "write_formal_acceptance_package_audit",
]
