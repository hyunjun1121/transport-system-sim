"""Graph-scale acceptance record validation.

The final study can use a reduced analysis corridor, a full graph, or a
multi-corridor ensemble. This module validates the explicit review record that
documents that choice before plan-level final-study readiness is allowed.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GRAPH_SCALE_ACCEPTANCE_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "graph_scale_acceptance.json"
)

REQUIRED_GRAPH_SCALE_FIELDS: tuple[str, ...] = (
    "region_id",
    "accepted",
    "accepted_by",
    "accepted_date",
    "graph_scale_decision",
    "source_graph_nodes",
    "source_graph_edges",
    "analysis_graph_nodes",
    "analysis_graph_edges",
    "corridor_reduction_accepted",
    "alternate_corridor_sensitivity_reviewed",
    "claim_boundary",
    "evidence_paths",
)
ALLOWED_GRAPH_SCALE_DECISIONS: frozenset[str] = frozenset(
    {"corridor_abstraction", "full_graph_runtime", "multi_corridor_ensemble"}
)


@dataclass(frozen=True)
class GraphScaleAcceptance:
    """One explicit graph-scale acceptance record."""

    region_id: str
    accepted: bool
    accepted_by: str
    accepted_date: str
    graph_scale_decision: str
    source_graph_nodes: int
    source_graph_edges: int
    analysis_graph_nodes: int
    analysis_graph_edges: int
    corridor_reduction_accepted: bool
    alternate_corridor_sensitivity_reviewed: bool
    claim_boundary: str
    evidence_paths: tuple[str, ...]

    @property
    def ready(self) -> bool:
        """Return whether this record can satisfy the graph-scale gate."""

        corridor_ready = (
            self.graph_scale_decision != "corridor_abstraction"
            or (
                self.corridor_reduction_accepted
                and self.alternate_corridor_sensitivity_reviewed
            )
        )
        return (
            self.accepted
            and self.graph_scale_decision in ALLOWED_GRAPH_SCALE_DECISIONS
            and self.source_graph_nodes > 0
            and self.source_graph_edges > 0
            and self.analysis_graph_nodes > 0
            and self.analysis_graph_edges > 0
            and corridor_ready
            and "not operational" in self.claim_boundary.lower()
            and bool(self.evidence_paths)
        )


def load_graph_scale_acceptance(
    path: str | Path = DEFAULT_GRAPH_SCALE_ACCEPTANCE_PATH,
) -> GraphScaleAcceptance:
    """Load and validate a graph-scale acceptance JSON record."""

    acceptance_path = Path(path)
    with acceptance_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{acceptance_path} must contain a JSON object")
    record = _acceptance_from_mapping(value, acceptance_path)
    validate_graph_scale_acceptance(record, table_name=str(acceptance_path))
    return record


def summarize_graph_scale_acceptance(
    path: str | Path = DEFAULT_GRAPH_SCALE_ACCEPTANCE_PATH,
) -> dict[str, Any]:
    """Return conservative graph-scale acceptance readiness."""

    acceptance_path = Path(path)
    if not acceptance_path.exists():
        return {
            "acceptance_ready": False,
            "path": _display_path(acceptance_path),
            "record_present": False,
            "remaining_blockers": [
                "create an explicit graph-scale acceptance record after source-vs-analysis graph review"
            ],
        }

    record = load_graph_scale_acceptance(acceptance_path)
    blockers: list[str] = []
    if not record.accepted:
        blockers.append("graph-scale acceptance record does not set accepted: true")
    if record.graph_scale_decision not in ALLOWED_GRAPH_SCALE_DECISIONS:
        blockers.append("graph-scale acceptance record has an unsupported graph_scale_decision")
    if record.source_graph_nodes <= 0 or record.source_graph_edges <= 0:
        blockers.append("graph-scale acceptance record must include positive source graph counts")
    if record.analysis_graph_nodes <= 0 or record.analysis_graph_edges <= 0:
        blockers.append("graph-scale acceptance record must include positive analysis graph counts")
    if (
        record.graph_scale_decision == "corridor_abstraction"
        and not record.corridor_reduction_accepted
    ):
        blockers.append("corridor abstraction requires corridor_reduction_accepted: true")
    if (
        record.graph_scale_decision == "corridor_abstraction"
        and not record.alternate_corridor_sensitivity_reviewed
    ):
        blockers.append(
            "corridor abstraction requires alternate_corridor_sensitivity_reviewed: true"
        )
    if "not operational" not in record.claim_boundary.lower():
        blockers.append("graph-scale acceptance claim_boundary must include 'not operational'")
    if not record.evidence_paths:
        blockers.append("graph-scale acceptance record must list evidence_paths")

    return {
        "acceptance_ready": not blockers,
        "path": _display_path(acceptance_path),
        "record_present": True,
        "region_id": record.region_id,
        "graph_scale_decision": record.graph_scale_decision,
        "source_graph_nodes": record.source_graph_nodes,
        "source_graph_edges": record.source_graph_edges,
        "analysis_graph_nodes": record.analysis_graph_nodes,
        "analysis_graph_edges": record.analysis_graph_edges,
        "corridor_reduction_accepted": record.corridor_reduction_accepted,
        "alternate_corridor_sensitivity_reviewed": (
            record.alternate_corridor_sensitivity_reviewed
        ),
        "evidence_paths": list(record.evidence_paths),
        "remaining_blockers": blockers,
    }


def validate_graph_scale_acceptance(
    record: GraphScaleAcceptance,
    *,
    table_name: str = "graph-scale acceptance",
) -> None:
    """Validate field-level graph-scale acceptance semantics."""

    if not record.region_id:
        raise ValueError(f"{table_name} region_id must be non-empty")
    if not record.accepted_by:
        raise ValueError(f"{table_name} accepted_by must be non-empty")
    if not record.accepted_date:
        raise ValueError(f"{table_name} accepted_date must be non-empty")
    if record.graph_scale_decision not in ALLOWED_GRAPH_SCALE_DECISIONS:
        allowed = ", ".join(sorted(ALLOWED_GRAPH_SCALE_DECISIONS))
        raise ValueError(
            f"{table_name} graph_scale_decision must be one of: {allowed}"
        )
    for field_name in (
        "source_graph_nodes",
        "source_graph_edges",
        "analysis_graph_nodes",
        "analysis_graph_edges",
    ):
        if getattr(record, field_name) <= 0:
            raise ValueError(f"{table_name} {field_name} must be positive")
    if not record.claim_boundary:
        raise ValueError(f"{table_name} claim_boundary must be non-empty")
    if not record.evidence_paths:
        raise ValueError(f"{table_name} evidence_paths must be non-empty")


def _acceptance_from_mapping(
    row: Mapping[str, Any],
    path: Path,
) -> GraphScaleAcceptance:
    missing = [field for field in REQUIRED_GRAPH_SCALE_FIELDS if field not in row]
    if missing:
        raise ValueError(f"{path} missing required fields: {', '.join(missing)}")
    evidence_paths = row["evidence_paths"]
    if not isinstance(evidence_paths, Sequence) or isinstance(evidence_paths, str):
        raise ValueError(f"{path} evidence_paths must be a list of paths")
    return GraphScaleAcceptance(
        region_id=_clean(row["region_id"]),
        accepted=_bool_field(row, "accepted", path),
        accepted_by=_clean(row["accepted_by"]),
        accepted_date=_clean(row["accepted_date"]),
        graph_scale_decision=_clean(row["graph_scale_decision"]),
        source_graph_nodes=_positive_int(row, "source_graph_nodes", path),
        source_graph_edges=_positive_int(row, "source_graph_edges", path),
        analysis_graph_nodes=_positive_int(row, "analysis_graph_nodes", path),
        analysis_graph_edges=_positive_int(row, "analysis_graph_edges", path),
        corridor_reduction_accepted=_bool_field(
            row, "corridor_reduction_accepted", path
        ),
        alternate_corridor_sensitivity_reviewed=_bool_field(
            row, "alternate_corridor_sensitivity_reviewed", path
        ),
        claim_boundary=_clean(row["claim_boundary"]),
        evidence_paths=tuple(_clean(item) for item in evidence_paths if _clean(item)),
    )


def _positive_int(row: Mapping[str, Any], field: str, path: Path) -> int:
    value = row[field]
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{path} field {field!r} must be an integer")
    return value


def _bool_field(row: Mapping[str, Any], field: str, path: Path) -> bool:
    value = row[field]
    if not isinstance(value, bool):
        raise ValueError(f"{path} field {field!r} must be boolean")
    return value


def _clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


__all__ = [
    "ALLOWED_GRAPH_SCALE_DECISIONS",
    "DEFAULT_GRAPH_SCALE_ACCEPTANCE_PATH",
    "GraphScaleAcceptance",
    "REQUIRED_GRAPH_SCALE_FIELDS",
    "load_graph_scale_acceptance",
    "summarize_graph_scale_acceptance",
    "validate_graph_scale_acceptance",
]
