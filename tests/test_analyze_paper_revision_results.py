"""Direct tests for revision-campaign analysis CLI."""

from __future__ import annotations

import csv
from dataclasses import replace
from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.analyze_paper_revision_results import (
    _paired_summary_for_dimensions,
    analyze_output_root,
)
from src.realworld.revision_design import (
    EXPECTED_MORRIS_FACTORS,
    load_revision_design,
)
from src.realworld.revision_morris import sample_morris
from src.realworld.revision_graph_validation import (
    compute_corridor_target_scope_metrics,
    compute_graph_scope_route_metrics,
    write_corridor_target_scope_evidence,
    write_graph_scope_route_evidence,
)


DESIGN_PATH = ROOT / "data" / "manifests" / "paper_revision_experiment_design.json"


def test_paired_analysis_uses_design_confidence() -> None:
    base = load_revision_design(DESIGN_PATH)
    design = replace(
        base,
        defaults={**dict(base.defaults), "confidence": 0.80},
    )
    rows = []
    for seed, delta in ((1, -10.0), (2, -20.0)):
        rows.extend(
            [
                {
                    "policy_id": "bus_only",
                    "arrival_seed": seed,
                    "scenario_id": "normal",
                    "completion_rate": 1.0,
                    "makespan": 100.0 + delta,
                },
                {
                    "policy_id": "static_multimodal",
                    "arrival_seed": seed,
                    "scenario_id": "normal",
                    "completion_rate": 1.0,
                    "makespan": 100.0,
                },
            ]
        )

    result = _paired_summary_for_dimensions(
        rows,
        design,
        50,
        ("scenario_id",),
    )[0]

    assert result["t_confidence"] == 0.80
    assert result["bootstrap_confidence"] == 0.80
    assert result["completion_t_confidence"] == 0.80
    assert result["completion_bootstrap_confidence"] == 0.80
    print("PASS: paired analysis uses design confidence")


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    fields: list[str] = []
    for row in rows:
        for field in row:
            if field not in fields:
                fields.append(field)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _implementation_identity(sha256: str = "e" * 64) -> tuple[str, dict]:
    artifacts = {
        "scripts/run_paper_revision_experiments.py": {
            "path": str(ROOT / "scripts" / "run_paper_revision_experiments.py"),
            "sha256": sha256,
            "size_bytes": 1,
        }
    }
    entries = [
        {"relative_path": relative_path, "sha256": artifact["sha256"]}
        for relative_path, artifact in sorted(artifacts.items())
    ]
    encoded = json.dumps(
        entries,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest(), artifacts


def _runtime_identity() -> tuple[str, dict]:
    identity = {
        "python": {"implementation": "CPython", "version": "3.12.10"},
        "packages": {
            "networkx": "3.6.1",
            "numpy": "2.4.6",
            "scipy": "1.17.1",
            "SALib": "1.5.2",
            "PyYAML": "6.0.3",
        },
    }
    encoded = json.dumps(
        identity,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    fingerprint = hashlib.sha256(encoded).hexdigest()
    return fingerprint, {"fingerprint": fingerprint, **identity}


def _input_identity(sha256: str = "c" * 64) -> tuple[str, dict]:
    names = (
        "design",
        "region",
        "cache",
        "overrides",
        "scenarios",
        "demand_profiles",
        "fleet_profiles",
    )
    artifacts = {
        name: {
            "path": str(ROOT / "data" / f"{name}.fixture"),
            "sha256": sha256 if name == "design" else "d" * 64,
            "size_bytes": 1,
        }
        for name in names
    }
    entries = [
        {"name": name, "sha256": artifact["sha256"]}
        for name, artifact in sorted(artifacts.items())
    ]
    encoded = json.dumps(
        entries,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest(), artifacts


def _install_graph_scope_route_evidence(root: Path) -> None:
    full = nx.DiGraph()
    for source, target, time in (
        ("A", "D", 10.0),
        ("A", "S", 2.0),
        ("R", "D", 3.0),
        ("S", "R", 7.0),
    ):
        full.add_edge(
            source,
            target,
            mode="road",
            t0=time,
            length_m=time * 1_000.0,
        )
    graphs = {scope: full.copy() for scope in ("top3", "top5", "top10", "full")}
    for scope, count in (("top3", 3), ("top5", 5), ("top10", 10)):
        graphs[scope].graph["corridor_path_count"] = count
        method = (
            "exact_shortest_simple_paths"
            if scope == "top3"
            else "exact_top3_plus_deterministic_penalty_diversification"
        )
        graphs[scope].graph["corridor_leg_candidates_json"] = json.dumps(
            {
                leg_id: {
                    "candidate_count": 1,
                    "exact_shortest_count": 1,
                    "expansion_count": 0,
                    "method": method,
                }
                for leg_id in ("A_to_D", "A_to_S", "R_to_D")
            },
            sort_keys=True,
        )
    rows = compute_graph_scope_route_metrics(
        graphs,
        diversity_limits={"top3": 3, "top5": 5, "top10": 10, "full": 10},
    )
    write_graph_scope_route_evidence(
        root,
        rows,
        input_artifacts={
            "cache": {
                "path": "data/cache/goseong_nodelink_road.graphml",
                "sha256": "b" * 64,
                "size_bytes": 123,
            }
        },
    )
    corridor_rows = compute_corridor_target_scope_metrics(
        {"top10": graphs["top10"], "full": graphs["full"]},
        selected_edges=(("A", "D"),),
        road_multipliers=(1.0, 2.0, 3.0),
    )
    write_corridor_target_scope_evidence(
        root,
        corridor_rows,
        input_artifacts={
            "cache": {
                "path": "data/cache/goseong_nodelink_road.graphml",
                "sha256": "b" * 64,
                "size_bytes": 123,
            }
        },
    )


def _install_campaign(
    root: Path,
    campaign_id: str,
    rows: list[dict[str, object]],
    *,
    stage: str = "smoke",
    status: str = "complete",
    planned_run_count: int | None = None,
    implementation_sha256: str = "e" * 64,
    input_sha256: str = "c" * 64,
    central_checksum: str = "a" * 64,
    graph_scope_checksum: str = "b" * 64,
) -> None:
    normalized = []
    for index, row in enumerate(rows):
        item = dict(row)
        item["campaign_id"] = campaign_id
        scenario_id = str(item.get("scenario_id", ""))
        uses_central_target = (
            campaign_id in {"break_even", "road_rail_map", "morris"}
            or scenario_id.startswith("goseong_long_haul_damage_")
        )
        if uses_central_target:
            expected_checksum = (
                graph_scope_checksum
                if campaign_id == "graph_scope"
                else central_checksum
            )
            item.setdefault("selected_edges_checksum", expected_checksum)
            item.setdefault("selected_edge_count", 1)
        if campaign_id == "random_threat_outer":
            draw = int(item["threat_draw"])
            item.setdefault(
                "selected_edges_checksum",
                hashlib.sha256(f"random:{draw}".encode()).hexdigest(),
            )
            item.setdefault("selected_edge_count", 8)
        item.setdefault(
            "run_key",
            hashlib.sha256(f"{campaign_id}:{stage}:{index}".encode()).hexdigest(),
        )
        normalized.append(item)
    campaign_dir = root / campaign_id
    results_path = campaign_dir / f"{stage}_results.csv"
    _write_csv(results_path, normalized)
    planned = len(normalized) if planned_run_count is None else planned_run_count
    implementation_fingerprint, implementation_artifacts = (
        _implementation_identity(implementation_sha256)
    )
    input_fingerprint, input_artifacts = _input_identity(input_sha256)
    runtime_fingerprint, runtime_environment = _runtime_identity()
    random_draws = {
        int(item["threat_draw"]): (
            str(item["selected_edges_checksum"]),
            int(item["selected_edge_count"]),
        )
        for item in normalized
        if campaign_id == "random_threat_outer"
    }
    manifest = {
        "schema_version": 1,
        "final_study_ready": False,
        "design_id": "paper_revision_top10_corridor_v4_20260721",
        "campaign_id": campaign_id,
        "stage": stage,
        "status": status,
        "planned_run_count": planned,
        "completed_run_count": len(normalized),
        "pending_run_count": planned - len(normalized),
        "implementation_fingerprint": implementation_fingerprint,
        "implementation_artifacts": implementation_artifacts,
        "input_fingerprint": input_fingerprint,
        "input_artifacts": input_artifacts,
        "runtime_fingerprint": runtime_fingerprint,
        "runtime_environment": runtime_environment,
        "central_trunk_target_audit": {
            "selected_edge_count": 1,
            "selected_edge_checksum": central_checksum,
            "non_road_edge_count": 0,
            "connector_edge_count": 0,
            "nonpositive_length_edge_count": 0,
            "endpoint_shortest_path_overlap_counts": {
                "A_to_S": 0,
                "S_to_A": 0,
                "R_to_D": 0,
                "D_to_R": 0,
            },
            "endpoint_shortest_path_status": {
                "A_to_S": "available",
                "S_to_A": "available",
                "R_to_D": "available",
                "D_to_R": "available",
            },
            "contains_coordinates": False,
        },
        "graph_scope_fixed_target_audit": {
            "selection_scope": "top3",
            "selected_edge_count": 1,
            "selected_edge_checksum": graph_scope_checksum,
            "non_road_edge_count": 0,
            "connector_edge_count": 0,
            "nonpositive_length_edge_count": 0,
            "endpoint_shortest_path_overlap_counts": {
                "A_to_S": 0,
                "S_to_A": 0,
                "R_to_D": 0,
                "D_to_R": 0,
            },
            "endpoint_shortest_path_status": {
                "A_to_S": "available",
                "S_to_A": "available",
                "R_to_D": "available",
                "D_to_R": "available",
            },
            "contains_coordinates": False,
        },
        "random_threat_selection_audit": (
            {
                "threat_draw_count": len(random_draws),
                "selected_edge_count_values": sorted(
                    {count for _, count in random_draws.values()}
                ),
                "distinct_selected_edge_checksum_count": len(
                    {checksum for checksum, _ in random_draws.values()}
                ),
                "max_non_road_edge_count": 0,
                "max_connector_edge_count": 0,
                "max_nonpositive_length_edge_count": 0,
                "contains_coordinates": False,
            }
            if campaign_id == "random_threat_outer"
            else None
        ),
        "main_scenario_edge_checksums": {
            "goseong_long_haul_damage_mild": central_checksum,
            "goseong_long_haul_damage_moderate": central_checksum,
            "goseong_long_haul_damage_severe": central_checksum,
        },
        "graph_scope_scenario_edge_checksums": {
            "goseong_long_haul_damage_mild": graph_scope_checksum,
            "goseong_long_haul_damage_moderate": graph_scope_checksum,
            "goseong_long_haul_damage_severe": graph_scope_checksum,
        },
        "output_artifacts": {
            "results": {
                "path": str(results_path.resolve()),
                "sha256": hashlib.sha256(results_path.read_bytes()).hexdigest(),
                "size_bytes": results_path.stat().st_size,
            }
        },
    }
    (campaign_dir / f"{stage}_manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )


def _refresh_results_artifact(
    root: Path, campaign_id: str, *, stage: str = "smoke"
) -> None:
    results_path = root / campaign_id / f"{stage}_results.csv"
    manifest_path = root / campaign_id / f"{stage}_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["output_artifacts"]["results"] = {
        "path": str(results_path.resolve()),
        "sha256": hashlib.sha256(results_path.read_bytes()).hexdigest(),
        "size_bytes": results_path.stat().st_size,
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")


def _paired_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for seed, delta in ((3101, -10.0), (3102, -20.0)):
        rows.extend(
            [
                {
                    "campaign_id": "paired_reanalysis",
                    "policy_id": "bus_only",
                    "scenario_id": "no_disruption",
                    "resource_frame": "configured_bundle",
                    "graph_scope": "top3",
                    "corridor_path_count": 3,
                    "arrival_seed": seed,
                    "completion_rate": 1.0,
                    "makespan": 100.0 + delta,
                },
                {
                    "campaign_id": "paired_reanalysis",
                    "policy_id": "static_multimodal",
                    "scenario_id": "no_disruption",
                    "resource_frame": "configured_bundle",
                    "graph_scope": "top3",
                    "corridor_path_count": 3,
                    "arrival_seed": seed,
                    "completion_rate": 1.0,
                    "makespan": 100.0,
                },
            ]
        )
    rows.extend(
        [
            {
                "campaign_id": "paired_reanalysis",
                "policy_id": "bus_only",
                "scenario_id": "no_disruption",
                "resource_frame": "configured_bundle",
                "graph_scope": "top3",
                "corridor_path_count": 3,
                "arrival_seed": 3103,
                "completion_rate": 1.0,
                "makespan": "",
            },
            {
                "campaign_id": "paired_reanalysis",
                "policy_id": "static_multimodal",
                "scenario_id": "no_disruption",
                "resource_frame": "configured_bundle",
                "graph_scope": "top3",
                "corridor_path_count": 3,
                "arrival_seed": 3103,
                "completion_rate": 1.0,
                "makespan": 100.0,
            },
        ]
    )
    return rows


def _break_even_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for multiplier, delta in ((1.0, -10.0), (2.0, 10.0)):
        for seed in (3101, 3102):
            rows.extend(
                [
                    {
                        "campaign_id": "break_even",
                        "policy_id": "bus_only",
                        "scenario_id": "long_haul_break_even",
                        "road_multiplier": multiplier,
                        "arrival_seed": seed,
                        "completion_rate": 1.0,
                        "makespan": 100.0 + delta,
                    },
                    {
                        "campaign_id": "break_even",
                        "policy_id": "static_multimodal",
                        "scenario_id": "long_haul_break_even",
                        "road_multiplier": multiplier,
                        "arrival_seed": seed,
                        "completion_rate": 1.0,
                        "makespan": 100.0,
                    },
                ]
            )
    return rows


def test_available_campaigns_write_paired_intervals_and_breakpoint() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        output_root = Path(temp_dir) / "paper_revision_top5_20260721"
        _install_campaign(output_root, "paired_reanalysis", _paired_rows())
        _install_campaign(output_root, "break_even", _break_even_rows())

        manifest = analyze_output_root(
            output_root,
            stage="smoke",
            design_path=DESIGN_PATH,
            bootstrap_replicates=200,
            morris_resamples=100,
        )

        paired = _read_csv(output_root / "analysis" / "smoke" / "paired_summary.csv")
        assert len(paired) == 1
        assert float(paired[0]["mean_bus_makespan"]) == 85.0
        assert float(paired[0]["mean_multimodal_makespan"]) == 100.0
        assert float(paired[0]["mean_delta_bus_minus_multimodal"]) == -15.0
        assert paired[0]["t_ci_lower"]
        assert paired[0]["t_ci_upper"]
        assert paired[0]["bootstrap_ci_lower"]
        assert paired[0]["bootstrap_ci_upper"]
        assert paired[0]["finite_pair_count"] == "2"
        assert paired[0]["excluded_pair_count"] == "1"
        assert paired[0]["mean_completion_rate_delta_bus_minus_multimodal"] == "0.0"
        assert paired[0]["completion_winner"] == "tie"
        assert paired[0]["completion_t_ci_lower"] == "0.0"
        assert paired[0]["completion_t_ci_upper"] == "0.0"
        assert paired[0]["completion_bootstrap_ci_lower"] == "0.0"
        assert paired[0]["completion_bootstrap_ci_upper"] == "0.0"
        assert paired[0]["completion_statistical_resolution"] == "tie_resolved"
        assert paired[0]["completion_winner_scope"] == "descriptive_mean_difference"
        assert paired[0]["overall_winner"] == "bus_only"
        reasons = json.loads(paired[0]["incomplete_reason_counts"])
        assert reasons == {"nonfinite_left": 1}

        crossing = _read_csv(output_root / "analysis" / "smoke" / "break_even.csv")
        assert len(crossing) == 1
        assert crossing[0]["status"] == "bracketed"
        assert float(crossing[0]["crossing_road_multiplier"]) == 1.5
        assert float(crossing[0]["joint_seed_bootstrap_ci_lower"]) <= 1.5
        assert float(crossing[0]["joint_seed_bootstrap_ci_upper"]) >= 1.5

        assert set(manifest["available_campaigns"]) == {
            "break_even",
            "paired_reanalysis",
        }
        assert "graph_scope" in manifest["missing_campaigns"]
        assert "morris" in manifest["missing_campaigns"]
        stored = json.loads(
            (output_root / "analysis" / "smoke" / "analysis_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        assert stored["missing_campaigns"] == manifest["missing_campaigns"]
        assert stored["stage"] == "smoke"
        assert stored["final_study_ready"] is False
        assert stored["analysis_complete_full"] is False
        assert stored["schema_version"] == 2
        assert "scripts/analyze_paper_revision_results.py" in stored[
            "analysis_implementation_artifacts"
        ]
        assert len(stored["analysis_implementation_fingerprint"]) == 64
        assert len(stored["runtime_fingerprint"]) == 64
        assert len(stored["input_fingerprint"]) == 64
        assert set(stored["input_artifacts"]) == {
            "design",
            "region",
            "cache",
            "overrides",
            "scenarios",
            "demand_profiles",
            "fleet_profiles",
        }
        assert stored["runtime_environment"]["packages"]["PyYAML"] == "6.0.3"
        datetime.fromisoformat(stored["written_at_utc"])
        assert stored["inference_definitions"]["adaptive_ranking"] == (
            "dense_rank_with_exact_ties_and_co_winners"
        )
        assert "completion_threat_draw_count" in stored["inference_definitions"][
            "random_threat_nested_sample_sizes"
        ]

    print("PASS: paired signs, intervals, breakpoint, and missing campaigns")


def test_analysis_rejects_canonical_output_tree() -> None:
    canonical = ROOT / "results" / "realworld_pilot_nodelink"
    try:
        analyze_output_root(
            canonical,
            stage="smoke",
            design_path=DESIGN_PATH,
            bootstrap_replicates=20,
        )
    except ValueError as error:
        assert "canonical results" in str(error)
    else:
        raise AssertionError("canonical result tree was accepted")

    print("PASS: analysis output stays outside canonical tree")


def test_analysis_rejects_float_bootstrap_replicates() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "paper_revision_top5_20260721"
        root.mkdir(parents=True)
        try:
            analyze_output_root(root, stage="smoke", bootstrap_replicates=2.0)
        except ValueError as error:
            assert "positive integer" in str(error)
        else:
            raise AssertionError("integral float bootstrap count must be rejected")
    print("PASS: analysis bootstrap count requires integer type")


def test_morris_rows_are_reconstructed_from_committed_design() -> None:
    design = load_revision_design(DESIGN_PATH)
    campaign = design.campaign("morris")
    problem = {
        "num_vars": len(EXPECTED_MORRIS_FACTORS),
        "names": list(EXPECTED_MORRIS_FACTORS),
        "bounds": [
            list(campaign["factors"][name]) for name in EXPECTED_MORRIS_FACTORS
        ],
    }
    sampled = sample_morris(
        problem,
        N=2,
        num_levels=int(campaign["levels"]),
        seed=design.morris_seed,
    )
    rows: list[dict[str, object]] = []
    for point, factor_row in enumerate(sampled.rows()):
        factor_values = {
            name: factor_row[name] for name in EXPECTED_MORRIS_FACTORS
        }
        response = sum(
            (index + 1) * float(factor_values[name])
            for index, name in enumerate(EXPECTED_MORRIS_FACTORS)
        )
        for policy in ("bus_only", "static_multimodal"):
            for arrival_seed in (3101, 3102):
                rows.append(
                    {
                        "campaign_id": "morris",
                        "policy_id": policy,
                        "morris_point": point,
                        "morris_trajectory": point // 7,
                        "factor_values": json.dumps(factor_values),
                        "arrival_seed": arrival_seed,
                        "completion_rate": 1.0,
                        "makespan": response + (arrival_seed - 3101) * 0.01,
                    }
                )

    with tempfile.TemporaryDirectory() as temp_dir:
        output_root = Path(temp_dir) / "paper_revision_top5_20260721"
        _install_campaign(output_root, "morris", rows)
        manifest = analyze_output_root(
            output_root,
            stage="smoke",
            design_path=DESIGN_PATH,
            bootstrap_replicates=20,
            morris_resamples=100,
        )
        effects = _read_csv(output_root / "analysis" / "smoke" / "morris_effects.csv")

    assert len(effects) == 4 * len(EXPECTED_MORRIS_FACTORS)
    assert {row["factor_name"] for row in effects} == set(
        EXPECTED_MORRIS_FACTORS
    )
    assert {row["response_metric"] for row in effects} == {
        "makespan",
        "completion_rate",
    }
    assert {row["analysis_status"] for row in effects} == {"available"}
    assert manifest["analyses"]["morris_effects"]["status"] == "available"
    print("PASS: Morris sample points align to committed seeded design")


def test_morris_makespan_rejects_partial_seed_but_completion_response_remains() -> None:
    design = load_revision_design(DESIGN_PATH)
    campaign = design.campaign("morris")
    problem = {
        "num_vars": len(EXPECTED_MORRIS_FACTORS),
        "names": list(EXPECTED_MORRIS_FACTORS),
        "bounds": [list(campaign["factors"][name]) for name in EXPECTED_MORRIS_FACTORS],
    }
    sampled = sample_morris(
        problem, N=2, num_levels=int(campaign["levels"]), seed=design.morris_seed
    )
    rows = []
    for point, factor_row in enumerate(sampled.rows()):
        factors = {name: factor_row[name] for name in EXPECTED_MORRIS_FACTORS}
        for arrival_seed in (3101, 3102):
            failed = point == 0 and arrival_seed == 3102
            rows.append(
                {
                    "policy_id": "bus_only",
                    "morris_point": point,
                    "factor_values": json.dumps(factors),
                    "arrival_seed": arrival_seed,
                    "completion_rate": 0.5 if failed else 1.0,
                    "makespan": "" if failed else 100.0 + point,
                }
            )
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "paper_revision_top5_20260721"
        _install_campaign(root, "morris", rows)
        analyze_output_root(root, stage="smoke", bootstrap_replicates=20, morris_resamples=50)
        effects = _read_csv(root / "analysis" / "smoke" / "morris_effects.csv")

    makespan = [row for row in effects if row["response_metric"] == "makespan"]
    completion = [row for row in effects if row["response_metric"] == "completion_rate"]
    assert len(makespan) == 1
    assert makespan[0]["analysis_status"] == "incomplete_replications"
    assert makespan[0]["factor_name"] == ""
    assert int(makespan[0]["incomplete_group_count"]) == 1
    assert len(completion) == len(EXPECTED_MORRIS_FACTORS)
    assert {row["analysis_status"] for row in completion} == {"available"}
    print("PASS: Morris makespan is complete-case and completion response remains")


def test_stage_filter_manifest_and_run_key_guards() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "paper_revision_top5_20260721"
        smoke_rows = _paired_rows()[:4]
        full_rows = _paired_rows()[:4]
        full_rows[0]["makespan"] = 999.0
        _install_campaign(root, "paired_reanalysis", smoke_rows, stage="smoke")
        _install_campaign(root, "paired_reanalysis", full_rows, stage="full")

        analyze_output_root(root, stage="smoke", bootstrap_replicates=20)
        smoke = _read_csv(root / "analysis" / "smoke" / "paired_summary.csv")
        assert float(smoke[0]["mean_delta_bus_minus_multimodal"]) == -15.0

        (root / "paired_reanalysis" / "smoke_manifest.json").unlink()
        try:
            analyze_output_root(root, stage="smoke", bootstrap_replicates=20)
        except ValueError as error:
            assert "manifest" in str(error)
        else:
            raise AssertionError("campaign CSV without manifest was accepted")

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "paper_revision_top5_20260721"
        rows = _paired_rows()[:4]
        duplicate = "a" * 64
        rows[0]["run_key"] = duplicate
        rows[1]["run_key"] = duplicate
        _install_campaign(root, "paired_reanalysis", rows)
        try:
            analyze_output_root(root, stage="smoke", bootstrap_replicates=20)
        except ValueError as error:
            assert "duplicate run_key" in str(error)
        else:
            raise AssertionError("duplicate run_key was accepted")

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "paper_revision_top5_20260721"
        rows = _paired_rows()[:4]
        _install_campaign(
            root,
            "paired_reanalysis",
            rows,
            stage="full",
            status="partial",
            planned_run_count=5,
        )
        manifest = analyze_output_root(
            root, stage="full", bootstrap_replicates=20
        )
        assert manifest["analysis_complete_full"] is False
        assert "paired_reanalysis:partial" in manifest[
            "analysis_completeness_blockers"
        ]
    print("PASS: stage, manifest, and run-key guards")


def test_results_artifact_integrity_is_enforced() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "paper_revision_top5_20260721"
        _install_campaign(root, "paired_reanalysis", _paired_rows()[:4])
        results_path = root / "paired_reanalysis" / "smoke_results.csv"
        with results_path.open("a", encoding="utf-8") as handle:
            handle.write("corruption\n")
        try:
            analyze_output_root(root, stage="smoke", bootstrap_replicates=20)
        except ValueError as error:
            assert "artifact" in str(error)
        else:
            raise AssertionError("results artifact corruption was accepted")
        process = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "analyze_paper_revision_results.py"),
                "--stage",
                "smoke",
                "--output-root",
                str(root),
                "--bootstrap-replicates",
                "20",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert process.returncode != 0
        assert "artifact" in (process.stderr + process.stdout)
    print("PASS: selected-stage results artifact integrity")


def test_campaign_implementation_fingerprint_integrity_and_consistency() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "paper_revision_top5_20260721"
        _install_campaign(root, "paired_reanalysis", _paired_rows()[:4])
        manifest_path = root / "paired_reanalysis" / "smoke_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest.pop("implementation_fingerprint")
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        try:
            analyze_output_root(root, stage="smoke", bootstrap_replicates=20)
        except ValueError as error:
            assert "implementation_fingerprint" in str(error)
        else:
            raise AssertionError("missing implementation fingerprint must fail")

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "paper_revision_top5_20260721"
        _install_campaign(root, "paired_reanalysis", _paired_rows()[:4])
        manifest_path = root / "paired_reanalysis" / "smoke_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["implementation_fingerprint"] = "f" * 64
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        try:
            analyze_output_root(root, stage="smoke", bootstrap_replicates=20)
        except ValueError as error:
            assert "does not match implementation_artifacts" in str(error)
        else:
            raise AssertionError("internally inconsistent fingerprint must fail")

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "paper_revision_top5_20260721"
        _install_campaign(root, "paired_reanalysis", _paired_rows()[:4])
        _install_campaign(
            root,
            "break_even",
            _break_even_rows(),
            implementation_sha256="d" * 64,
        )
        try:
            analyze_output_root(root, stage="smoke", bootstrap_replicates=20)
        except ValueError as error:
            assert "same implementation fingerprint" in str(error)
        else:
            raise AssertionError("mixed implementation fingerprints must fail")
    print("PASS: campaign implementation fingerprint integrity and consistency")


def test_campaign_input_fingerprint_integrity_and_consistency() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "paper_revision_top10_corridor_v4_20260721"
        _install_campaign(root, "paired_reanalysis", _paired_rows()[:4])
        manifest_path = root / "paired_reanalysis" / "smoke_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["input_fingerprint"] = "f" * 64
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        try:
            analyze_output_root(root, stage="smoke", bootstrap_replicates=20)
        except ValueError as error:
            assert "input_fingerprint does not match input_artifacts" in str(error)
        else:
            raise AssertionError("internally inconsistent input fingerprint must fail")

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "paper_revision_top10_corridor_v4_20260721"
        _install_campaign(root, "paired_reanalysis", _paired_rows()[:4])
        _install_campaign(
            root,
            "break_even",
            _break_even_rows(),
            input_sha256="9" * 64,
        )
        try:
            analyze_output_root(root, stage="smoke", bootstrap_replicates=20)
        except ValueError as error:
            assert "same input fingerprint" in str(error)
        else:
            raise AssertionError("mixed campaign input fingerprints must fail")
    print("PASS: campaign input fingerprint integrity and consistency")


def test_central_target_checksums_cross_campaign_evidence_and_rows() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "paper_revision_top10_corridor_v4_20260721"
        _install_campaign(root, "paired_reanalysis", _paired_rows()[:4])
        manifest_path = root / "paired_reanalysis" / "smoke_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["central_trunk_target_audit"]["endpoint_shortest_path_status"][
            "S_to_A"
        ] = "unavailable"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        try:
            analyze_output_root(root, stage="smoke", bootstrap_replicates=20)
        except ValueError as error:
            assert "endpoint path audit" in str(error)
        else:
            raise AssertionError("unavailable endpoint audit path must fail")

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "paper_revision_top10_corridor_v4_20260721"
        _install_campaign(root, "paired_reanalysis", _paired_rows()[:4])
        _install_campaign(
            root,
            "break_even",
            _break_even_rows(),
            central_checksum="9" * 64,
        )
        try:
            analyze_output_root(root, stage="smoke", bootstrap_replicates=20)
        except ValueError as error:
            assert "same central target checksum" in str(error)
        else:
            raise AssertionError("mixed central target checksums must fail")

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "paper_revision_top10_corridor_v4_20260721"
        _install_graph_scope_route_evidence(root)
        evidence = json.loads(
            (root / "corridor_target_scope_metrics_manifest.json").read_text(
                encoding="utf-8"
            )
        )
        evidence_checksum = evidence["selected_target_checksum"]
        mismatched = "f" * 64 if evidence_checksum != "f" * 64 else "e" * 64
        _install_campaign(
            root,
            "break_even",
            _break_even_rows(),
            central_checksum=mismatched,
        )
        try:
            analyze_output_root(root, stage="smoke", bootstrap_replicates=20)
        except ValueError as error:
            assert "corridor evidence checksum" in str(error)
        else:
            raise AssertionError("campaign/evidence target mismatch must fail")

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "paper_revision_top10_corridor_v4_20260721"
        _install_campaign(root, "break_even", _break_even_rows())
        results_path = root / "break_even" / "smoke_results.csv"
        rows = _read_csv(results_path)
        rows[0]["selected_edges_checksum"] = "8" * 64
        _write_csv(results_path, rows)
        _refresh_results_artifact(root, "break_even")
        try:
            analyze_output_root(root, stage="smoke", bootstrap_replicates=20)
        except ValueError as error:
            assert "long-haul result checksum" in str(error)
        else:
            raise AssertionError("long-haul row checksum mismatch must fail")

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "paper_revision_top10_corridor_v4_20260721"
        graph_rows = [
            {
                "policy_id": policy,
                "scenario_id": "goseong_long_haul_damage_severe",
                "graph_scope": "top3",
                "arrival_seed": 3101,
                "completion_rate": 1.0,
                "makespan": makespan,
            }
            for policy, makespan in (
                ("bus_only", 120.0),
                ("static_multimodal", 100.0),
            )
        ]
        _install_campaign(
            root,
            "graph_scope",
            graph_rows,
            central_checksum="a" * 64,
            graph_scope_checksum="b" * 64,
        )
        analyze_output_root(root, stage="smoke", bootstrap_replicates=20)

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "paper_revision_top10_corridor_v4_20260721"
        _install_campaign(root, "graph_scope", graph_rows)
        manifest_path = root / "graph_scope" / "smoke_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["graph_scope_fixed_target_audit"]["connector_edge_count"] = 1
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        try:
            analyze_output_root(root, stage="smoke", bootstrap_replicates=20)
        except ValueError as error:
            assert "graph-scope fixed target audit" in str(error)
        else:
            raise AssertionError("graph-scope target hygiene failure must fail")
    print("PASS: central and graph-scope target checksum contracts")


def test_random_threat_audit_matches_result_draw_checksums() -> None:
    rows = []
    for draw in (1, 2):
        for policy in ("bus_only", "static_multimodal"):
            rows.append(
                {
                    "policy_id": policy,
                    "scenario_id": "random_blockage",
                    "threat_draw": draw,
                    "arrival_seed": 3101,
                    "completion_rate": 1.0,
                    "makespan": 100.0,
                }
            )
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "paper_revision_top10_corridor_v4_20260721"
        _install_campaign(root, "random_threat_outer", rows)
        results_path = root / "random_threat_outer" / "smoke_results.csv"
        stored_rows = _read_csv(results_path)
        stored_rows[1]["selected_edges_checksum"] = "7" * 64
        _write_csv(results_path, stored_rows)
        _refresh_results_artifact(root, "random_threat_outer")
        try:
            analyze_output_root(root, stage="smoke", bootstrap_replicates=20)
        except ValueError as error:
            assert "random-threat draw checksum" in str(error)
        else:
            raise AssertionError("mixed checksum within one threat draw must fail")
    print("PASS: random-threat audit matches result draw checksums")


def test_new_campaign_outputs_are_materialized() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "paper_revision_top5_20260721"
        base_pairs = []
        for policy, makespan in (("bus_only", 90.0), ("static_multimodal", 100.0)):
            base_pairs.append(
                {
                    "policy_id": policy,
                    "arrival_seed": 3101,
                    "completion_rate": 1.0,
                    "makespan": makespan,
                }
            )
        demand = [
            {**row, "demand": 1000, "road_fleet_total": 23, "resource_frame": "configured_bundle"}
            for row in base_pairs
        ]
        road_rail = [
            {**row, "road_multiplier": 1.4, "rail_status": "available", "rail_multiplier": 1.0}
            for row in base_pairs
        ]
        adaptive = [
            {**row, "resource_frame": "configured_bundle", "rail_status": "available", "rail_multiplier": 1.0}
            for row in base_pairs
        ] + [
            {
                "policy_id": "precheck_switch",
                "arrival_seed": 3101,
                "completion_rate": 1.0,
                "makespan": 90.0,
                "resource_frame": "configured_bundle",
                "rail_status": "available",
                "rail_multiplier": 1.0,
            }
        ]
        _install_campaign(root, "demand_fleet", demand)
        _install_campaign(root, "road_rail_map", road_rail)
        _install_campaign(root, "adaptive_policies", adaptive)

        analyze_output_root(root, stage="smoke", bootstrap_replicates=20)

        demand_rows = _read_csv(root / "analysis" / "smoke" / "demand_fleet.csv")
        map_rows = _read_csv(root / "analysis" / "smoke" / "road_rail_map.csv")
        adaptive_rows = _read_csv(root / "analysis" / "smoke" / "adaptive_policies.csv")
        assert demand_rows[0]["mean_bus_makespan"] == "90.0"
        assert demand_rows[0]["mean_multimodal_makespan"] == "100.0"
        assert map_rows[0]["mean_bus_makespan"] == "90.0"
        assert map_rows[0]["mean_multimodal_makespan"] == "100.0"
        assert demand_rows[0]["overall_winner"] == "bus_only"
        assert map_rows[0]["overall_winner"] == "bus_only"
        assert {row["policy_id"] for row in adaptive_rows} == {
            "bus_only", "static_multimodal", "precheck_switch"
        }
        co_winners = {
            row["policy_id"]
            for row in adaptive_rows
            if row["winner"] == "True"
        }
        assert co_winners == {"bus_only", "precheck_switch"}
        assert {
            row["rank"] for row in adaptive_rows if row["policy_id"] in co_winners
        } == {"1"}
        assert next(
            row for row in adaptive_rows if row["policy_id"] == "static_multimodal"
        )["rank"] == "2"
    print("PASS: demand-fleet, road-rail, and adaptive outputs")


def test_paired_output_omits_policy_means_without_finite_pairs() -> None:
    rows = [
        {
            "policy_id": "bus_only",
            "scenario_id": "blocked",
            "arrival_seed": 3101,
            "completion_rate": 1.0,
            "makespan": "",
        },
        {
            "policy_id": "static_multimodal",
            "scenario_id": "blocked",
            "arrival_seed": 3101,
            "completion_rate": 1.0,
            "makespan": 100.0,
        },
    ]
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "paper_revision_top5_20260721"
        _install_campaign(root, "paired_reanalysis", rows)

        analyze_output_root(root, stage="smoke", bootstrap_replicates=20)

        paired = _read_csv(root / "analysis" / "smoke" / "paired_summary.csv")
        assert len(paired) == 1
        assert paired[0]["finite_pair_count"] == "0"
        assert paired[0]["mean_bus_makespan"] == ""
        assert paired[0]["mean_multimodal_makespan"] == ""
        assert paired[0]["mean_delta_bus_minus_multimodal"] == ""
    print("PASS: paired output leaves unavailable makespan means blank")


def test_random_threat_outputs_completion_and_probability_proxies() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "paper_revision_top5_20260721"
        rows: list[dict[str, object]] = []
        completions = {
            1: ((0.5, 1.0), (0.0, 1.0)),
            2: ((1.0, 0.5), (1.0, 0.0)),
        }
        for threat_draw, pairs in completions.items():
            for seed, (bus_completion, multimodal_completion) in enumerate(
                pairs, start=3101
            ):
                for policy, completion in (
                    ("bus_only", bus_completion),
                    ("static_multimodal", multimodal_completion),
                ):
                    rows.append(
                        {
                            "policy_id": policy,
                            "arrival_seed": seed,
                            "threat_draw": threat_draw,
                            "scenario_id": "random_blockage",
                            "completion_rate": completion,
                            "makespan": "",
                        }
                    )
        _install_campaign(root, "random_threat_outer", rows)

        analyze_output_root(root, stage="smoke", bootstrap_replicates=100)

        output = _read_csv(
            root / "analysis" / "smoke" / "random_threat_hierarchical.csv"
        )
        assert len(output) == 1
        row = output[0]
        assert row["threat_draw_count"] == ""
        assert row["completion_pair_count"] == "4"
        assert row["completion_threat_draw_count"] == "2"
        assert row["completion_observation_count"] == "4"
        assert json.loads(row["completion_empty_threat_draws"]) == []
        assert row["probability_proxy_observation_count"] == "4"
        assert float(row["mean_completion_rate_delta_bus_minus_multimodal"]) == 0.0
        assert float(row["bus_positive_completion_probability_proxy"]) == 0.75
        assert float(row["multimodal_positive_completion_probability_proxy"]) == 0.75
        assert float(row["bus_full_completion_probability_proxy"]) == 0.5
        assert float(row["multimodal_full_completion_probability_proxy"]) == 0.5
        assert row["completion_delta_bootstrap_ci_lower"]
        assert row["bus_positive_completion_proxy_ci_lower"]
        assert row["probability_proxy_scope"].endswith("not_event_probability")
    print("PASS: random-threat result-frequency proxy schema")


def test_structural_graph_scope_evidence_is_integrity_checked_and_exposed() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / "paper_revision_top5_20260721"
        _install_graph_scope_route_evidence(root)
        manifest = analyze_output_root(
            root,
            stage="smoke",
            design_path=DESIGN_PATH,
            bootstrap_replicates=20,
        )
        output = _read_csv(
            root / "analysis" / "smoke" / "graph_scope_route_metrics.csv"
        )
        assert len(output) == 16
        assert {row["graph_scope"] for row in output} == {
            "top3", "top5", "top10", "full"
        }
        assert {row["leg_id"] for row in output} == {
            "A_to_D", "A_to_S", "R_to_D", "S_to_R"
        }
        full_a_to_d = next(
            row
            for row in output
            if row["graph_scope"] == "full" and row["leg_id"] == "A_to_D"
        )
        assert full_a_to_d["path_diversity_count"] == "0"
        assert full_a_to_d["path_diversity_status"] == "not_enumerated_cost_guard"
        assert full_a_to_d["path_diversity_method"] == "not_enumerated_cost_guard"
        top10_a_to_d = next(
            row
            for row in output
            if row["graph_scope"] == "top10" and row["leg_id"] == "A_to_D"
        )
        assert top10_a_to_d["path_diversity_method"] == (
            "exact_top3_plus_deterministic_penalty_diversification"
        )
        assert manifest["analyses"]["graph_scope_route_metrics"]["status"] == "available"
        assert manifest["graph_scope_route_evidence_manifest"]["final_study_ready"] is False
        assert manifest["graph_scope_route_evidence_manifest"]["stage_independent"] is True

        evidence_manifest_path = root / "graph_scope_route_metrics_manifest.json"
        original_manifest_text = evidence_manifest_path.read_text(encoding="utf-8")
        invalid_manifest = json.loads(original_manifest_text)
        invalid_manifest["path_diversity_cost_guard"]["sentinel_count"] = 1
        evidence_manifest_path.write_text(
            json.dumps(invalid_manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        try:
            analyze_output_root(
                root,
                stage="smoke",
                design_path=DESIGN_PATH,
                bootstrap_replicates=20,
            )
        except ValueError as error:
            assert "path-diversity cost guard" in str(error)
        else:
            raise AssertionError("invalid path-diversity cost guard was accepted")
        evidence_manifest_path.write_text(original_manifest_text, encoding="utf-8")

        source = root / "graph_scope_route_metrics.csv"
        with source.open("a", encoding="utf-8") as handle:
            handle.write("tamper\n")
        try:
            analyze_output_root(
                root,
                stage="smoke",
                design_path=DESIGN_PATH,
                bootstrap_replicates=20,
            )
        except ValueError as error:
            assert "graph-scope route artifact" in str(error)
        else:
            raise AssertionError("tampered graph-scope route evidence was accepted")
    print("PASS: structural graph-scope evidence integrity and analysis exposure")


if __name__ == "__main__":
    test_paired_analysis_uses_design_confidence()
    test_available_campaigns_write_paired_intervals_and_breakpoint()
    test_analysis_rejects_canonical_output_tree()
    test_analysis_rejects_float_bootstrap_replicates()
    test_morris_rows_are_reconstructed_from_committed_design()
    test_morris_makespan_rejects_partial_seed_but_completion_response_remains()
    test_stage_filter_manifest_and_run_key_guards()
    test_results_artifact_integrity_is_enforced()
    test_campaign_implementation_fingerprint_integrity_and_consistency()
    test_campaign_input_fingerprint_integrity_and_consistency()
    test_central_target_checksums_cross_campaign_evidence_and_rows()
    test_random_threat_audit_matches_result_draw_checksums()
    test_new_campaign_outputs_are_materialized()
    test_paired_output_omits_policy_means_without_finite_pairs()
    test_random_threat_outputs_completion_and_probability_proxies()
    test_structural_graph_scope_evidence_is_integrity_checked_and_exposed()
    print("\n=== REVISION ANALYSIS CLI TESTS PASSED ===")
