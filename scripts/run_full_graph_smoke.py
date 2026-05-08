"""Run a tiny full-graph pilot smoke without reducing to an analysis corridor."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.disruption_scenarios import (  # noqa: E402
    DEFAULT_SCENARIO_PATH,
    load_disruption_scenarios,
)
from src.realworld.pilot_experiments import (  # noqa: E402
    DEFAULT_CACHE_PATH,
    DEFAULT_POLICY_ALTERNATIVES_PATH,
    DEFAULT_REGION_PATH,
    load_pilot_inputs,
    run_pilot_rows,
    select_disruption_cases,
    select_policy_alternatives,
)
from src.realworld.policy_alternatives import load_policy_alternatives  # noqa: E402


FULL_GRAPH_SMOKE_SCOPE = (
    "Full bus-practical graph smoke only; not calibrated real-world results "
    "or an operational forecast."
)
DEFAULT_FULL_GRAPH_SMOKE_MANIFEST_PATH = (
    ROOT / "data" / "validation" / "full_graph_smoke_manifest.json"
)
DEFAULT_FULL_GRAPH_SMOKE_DOC_PATH = ROOT / "docs" / "full_graph_smoke.md"


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for the full-graph smoke check."""

    args = _parse_args(argv)
    started = time.perf_counter()
    result = run_full_graph_smoke()
    duration_sec = time.perf_counter() - started
    manifest = build_full_graph_smoke_manifest(
        result=result,
        duration_sec=duration_sec,
        manifest_path=args.manifest,
        doc_path=args.doc,
    )
    if not args.no_write:
        write_full_graph_smoke_outputs(
            manifest=manifest,
            manifest_path=args.manifest,
            doc_path=args.doc,
        )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def run_full_graph_smoke(
    *,
    region_path: str | Path = DEFAULT_REGION_PATH,
    cache_path: str | Path = DEFAULT_CACHE_PATH,
    scenarios_path: str | Path = DEFAULT_SCENARIO_PATH,
    policies_path: str | Path = DEFAULT_POLICY_ALTERNATIVES_PATH,
    seed: int = 9999,
) -> dict[str, Any]:
    """Run bus-only and baseline multimodal on the full simulator graph."""

    inputs = load_pilot_inputs(
        region_path=region_path,
        cache_path=cache_path,
        reduce_graph=False,
    )
    policies = select_policy_alternatives(
        load_policy_alternatives(policies_path),
        policy_ids=("bus_only", "baseline_multimodal"),
        sample=False,
    )
    cases = select_disruption_cases(
        inputs.graph,
        load_disruption_scenarios(scenarios_path, region_id=inputs.region_id),
        scenario_ids=("no_disruption",),
        sample=False,
    )
    rows = run_pilot_rows(
        inputs=inputs,
        policies=policies,
        cases=cases,
        seeds=(int(seed),),
        claim_scope=FULL_GRAPH_SMOKE_SCOPE,
    )
    return {
        "schema_version": 1,
        "region_id": inputs.region_id,
        "graph_nodes": inputs.graph.number_of_nodes(),
        "graph_edges": inputs.graph.number_of_edges(),
        "graph_scale": {
            "source": {
                "nodes": inputs.source_graph_nodes,
                "edges": inputs.source_graph_edges,
            },
            "analysis": {
                "nodes": inputs.graph.number_of_nodes(),
                "edges": inputs.graph.number_of_edges(),
                "reduced": bool(
                    inputs.graph.graph.get("experiment_subgraph", False)
                ),
                "strategy": "full_bus_practical_graph_smoke_without_corridor_reduction",
            },
        },
        "analysis_graph_reduced": bool(
            inputs.graph.graph.get("experiment_subgraph", False)
        ),
        "row_count": len(rows),
        "policies": [str(row["policy_id"]) for row in rows],
        "scenario_ids": ["no_disruption"],
        "seed": int(seed),
        "completion_rates": {
            str(row["policy_id"]): float(row["completion_rate"]) for row in rows
        },
        "penalized_makespan": {
            str(row["policy_id"]): float(row["penalized_makespan"]) for row in rows
        },
        "claim_scope": FULL_GRAPH_SMOKE_SCOPE,
    }


def build_full_graph_smoke_manifest(
    *,
    result: dict[str, Any],
    duration_sec: float,
    manifest_path: str | Path = DEFAULT_FULL_GRAPH_SMOKE_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_FULL_GRAPH_SMOKE_DOC_PATH,
) -> dict[str, Any]:
    """Return a persisted manifest for the bounded full-graph smoke run."""

    row_count = int(result.get("row_count", 0))
    passed = (
        row_count == 2
        and not bool(result.get("analysis_graph_reduced", True))
        and int(result.get("graph_nodes", 0)) > 1000
        and int(result.get("graph_edges", 0)) > 1000
    )
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": "scripts/run_full_graph_smoke.py",
        "result_scope": FULL_GRAPH_SMOKE_SCOPE,
        "claim_boundary": (
            FULL_GRAPH_SMOKE_SCOPE
            + " This manifest is smoke evidence only and cannot close the "
            "graph-scale, validation, experiment, or final-study gates."
        ),
        "outputs": {
            "manifest": _display_path(manifest_path),
            "doc": _display_path(doc_path),
        },
        "smoke_passed": passed,
        "duration_sec": round(float(duration_sec), 3),
        "row_count": row_count,
        "policy_count": len(result.get("policies", [])),
        "scenario_count": len(result.get("scenario_ids", [])),
        "seed_count": 1 if result.get("seed") is not None else 0,
        "region_id": str(result.get("region_id", "")),
        "graph_nodes": int(result.get("graph_nodes", 0)),
        "graph_edges": int(result.get("graph_edges", 0)),
        "analysis_graph_reduced": bool(result.get("analysis_graph_reduced", True)),
        "graph_scale": result.get("graph_scale", {}),
        "policies": list(result.get("policies", [])),
        "scenario_ids": list(result.get("scenario_ids", [])),
        "seed": result.get("seed"),
        "completion_rates": dict(result.get("completion_rates", {})),
        "penalized_makespan": dict(result.get("penalized_makespan", {})),
        "full_graph_experiment_output_created": False,
        "publication_ready": False,
        "can_mark_complete": False,
        "required_actions": [
            "treat this as two-row full-graph smoke evidence only",
            "generate full scenario-policy-seed outputs if full-graph execution is selected",
            "or record a reviewed graph-scale acceptance decision that bounds final claims away from full-graph execution",
            "rerun downstream sensitivity, figures, tables, and manuscript interpretation on the accepted graph method",
        ],
    }


def write_full_graph_smoke_outputs(
    *,
    manifest: dict[str, Any],
    manifest_path: str | Path = DEFAULT_FULL_GRAPH_SMOKE_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_FULL_GRAPH_SMOKE_DOC_PATH,
) -> dict[str, Any]:
    """Write full-graph smoke manifest and Markdown summary."""

    manifest_file = Path(manifest_path)
    doc_file = Path(doc_path)
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    doc_file.parent.mkdir(parents=True, exist_ok=True)
    manifest_file.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc_file.write_text(build_full_graph_smoke_markdown(manifest), encoding="utf-8")
    return manifest


def build_full_graph_smoke_markdown(manifest: dict[str, Any]) -> str:
    """Return a compact Markdown summary for the full-graph smoke run."""

    lines = [
        "# Full Graph Smoke",
        "",
        str(manifest.get("claim_boundary", FULL_GRAPH_SMOKE_SCOPE)),
        "",
        "## Summary",
        "",
        f"- Smoke passed: `{str(manifest.get('smoke_passed', False)).lower()}`",
        f"- Graph nodes: {manifest.get('graph_nodes', 0)}",
        f"- Graph edges: {manifest.get('graph_edges', 0)}",
        f"- Analysis graph reduced: `{str(manifest.get('analysis_graph_reduced', True)).lower()}`",
        f"- Rows: {manifest.get('row_count', 0)}",
        f"- Duration seconds: {manifest.get('duration_sec', '')}",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        "",
        "## Required Actions",
        "",
    ]
    for action in manifest.get("required_actions", []):
        lines.append(f"- {action}")
    lines.append("")
    return "\n".join(lines)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run a bounded full bus-practical graph smoke. The output is "
            "runtime/smoke evidence only, not graph-scale acceptance."
        )
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_FULL_GRAPH_SMOKE_MANIFEST_PATH,
        help="Full-graph smoke manifest JSON path.",
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_FULL_GRAPH_SMOKE_DOC_PATH,
        help="Full-graph smoke Markdown path.",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Print the manifest without writing smoke artifacts.",
    )
    return parser.parse_args(argv)


def _display_path(path: str | Path) -> str:
    filepath = Path(path)
    try:
        return filepath.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return filepath.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
