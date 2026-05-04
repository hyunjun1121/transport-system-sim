"""Run a tiny full-graph pilot smoke without reducing to an analysis corridor."""

from __future__ import annotations

import json
from pathlib import Path
import sys
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


def main() -> int:
    """CLI entry point for the full-graph smoke check."""

    result = run_full_graph_smoke()
    print(json.dumps(result, indent=2, sort_keys=True))
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
        "region_id": inputs.region_id,
        "graph_nodes": inputs.graph.number_of_nodes(),
        "graph_edges": inputs.graph.number_of_edges(),
        "analysis_graph_reduced": bool(
            inputs.graph.graph.get("experiment_subgraph", False)
        ),
        "row_count": len(rows),
        "policies": [str(row["policy_id"]) for row in rows],
        "completion_rates": {
            str(row["policy_id"]): float(row["completion_rate"]) for row in rows
        },
        "penalized_makespan": {
            str(row["policy_id"]): float(row["penalized_makespan"]) for row in rows
        },
        "claim_scope": FULL_GRAPH_SMOKE_SCOPE,
    }


if __name__ == "__main__":
    raise SystemExit(main())
