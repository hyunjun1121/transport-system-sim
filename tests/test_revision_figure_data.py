"""TDD contract for revision-analysis-backed paper figures 3--6."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "paper" / "figures" / "_build"
DATA_MODULE_PATH = BUILD_DIR / "revision_figure_data.py"
FIGURE_MODULE_PATH = BUILD_DIR / "build_all_figures.py"

SCENARIOS = (
    "no_disruption",
    "goseong_access_road_damage_severe",
    "goseong_last_mile_damage_severe",
    "goseong_long_haul_damage_mild",
    "goseong_long_haul_damage_moderate",
    "goseong_long_haul_damage_severe",
    "goseong_critical_link_blockage",
    "goseong_rail_unavailable",
)
SCOPES = ("top3", "top5", "top10", "full")
LEGS = ("A_to_D", "A_to_S", "R_to_D", "S_to_R")
POLICIES = (
    "bus_only",
    "static_multimodal",
    "precheck_switch",
    "split_600_400",
    "station_fallback_30",
    "station_fallback_60",
    "station_fallback_90",
)


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    assert rows
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _make_full_fixture(root: Path) -> Path:
    analysis = root / "analysis" / "full"
    analysis.mkdir(parents=True)

    route_rows: list[dict[str, object]] = []
    for scope_index, scope in enumerate(SCOPES):
        for leg_index, leg in enumerate(LEGS):
            connected = not (scope == "top3" and leg == "S_to_R")
            route_rows.append(
                {
                    "graph_scope": scope,
                    "leg_id": leg,
                    "connected": str(connected),
                    "travel_time_detour_ratio_vs_full": (
                        "" if not connected else 1.0 + (3 - scope_index) * 0.04 + leg_index * 0.01
                    ),
                }
            )
    _write_csv(analysis / "graph_scope_route_metrics.csv", route_rows)

    stability_rows = [
        {
            "graph_scope": scope,
            "connectivity_agreement": 0.70 + index * 0.10,
            "policy_ranking_agreement": 0.65 + index * 0.11,
        }
        for index, scope in enumerate(SCOPES)
    ]
    _write_csv(analysis / "graph_scope_stability.csv", stability_rows)

    paired_rows: list[dict[str, object]] = []
    for index, scenario in enumerate(SCENARIOS):
        collapsed = scenario in {
            "goseong_critical_link_blockage",
            "goseong_rail_unavailable",
        }
        bus_cr = 0.0 if scenario == "goseong_critical_link_blockage" else 1.0
        multi_cr = 0.0 if scenario == "goseong_rail_unavailable" else 1.0
        delta = -80.0 + index * 35.0
        paired_rows.append(
            {
                "scenario_id": scenario,
                "resource_frame": "matched_road_fleet",
                "graph_scope": "top10",
                "rail_status": (
                    "unavailable" if scenario == "goseong_rail_unavailable" else "available"
                ),
                "return_strategy": "reverse_network",
                "departure_policy_id": "strict",
                "mean_bus_completion_rate": bus_cr,
                "mean_multimodal_completion_rate": multi_cr,
                "finite_pair_count": 0 if collapsed else 30,
                "mean_delta_bus_minus_multimodal": "" if collapsed else delta,
                "bootstrap_ci_lower": "" if collapsed else delta - 5.0,
                "bootstrap_ci_upper": "" if collapsed else delta + 5.0,
                "bootstrap_confidence": "" if collapsed else 0.95,
            }
        )
    _write_csv(analysis / "paired_summary.csv", paired_rows)

    break_even_rows = [
        {
            "scenario_id": "long_haul_break_even",
            "resource_frame": "matched_road_fleet",
            "graph_scope": "top10",
            "rail_status": "available",
            "return_strategy": "reverse_network",
            "status": "bracketed",
            "crossing_road_multiplier": 1.4667,
            "paired_mean_points": json.dumps(
                [[1.0, -30.0], [1.4, -5.0], [1.6, 10.0], [2.0, 50.0]]
            ),
            "joint_seed_bootstrap_ci_lower": 1.40,
            "joint_seed_bootstrap_ci_upper": 1.55,
            "joint_seed_bootstrap_confidence": 0.95,
        }
    ]
    _write_csv(analysis / "break_even.csv", break_even_rows)

    road_rows: list[dict[str, object]] = []
    rail_conditions = (
        ("available", 1.0),
        ("degraded", 1.25),
        ("degraded", 1.5),
        ("degraded", 2.0),
        ("unavailable", ""),
    )
    for road in (1.0, 1.2, 1.4, 1.6, 2.0, 3.0):
        for rail_status, rail_multiplier in rail_conditions:
            unavailable = rail_status == "unavailable"
            delta = road * 100.0 - (170.0 if not unavailable else 0.0)
            road_rows.append(
                {
                    "road_multiplier": road,
                    "rail_status": rail_status,
                    "rail_multiplier": rail_multiplier,
                    "resource_frame": "matched_road_fleet",
                    "graph_scope": "top10",
                    "return_strategy": "reverse_network",
                    "overall_winner": (
                        "bus_only"
                        if unavailable or delta < 0
                        else "static_multimodal"
                    ),
                    "mean_delta_bus_minus_multimodal": "" if unavailable else delta,
                    "mean_bus_completion_rate": 1.0,
                    "mean_multimodal_completion_rate": 0.0 if unavailable else 1.0,
                }
            )
    _write_csv(analysis / "road_rail_map.csv", road_rows)

    demand_rows: list[dict[str, object]] = []
    for demand in (500, 1000, 1500, 2000):
        for fleet in (10, 15, 20, 23):
            delta = (demand - 1000) / 10.0 - (fleet - 15) * 8.0
            demand_rows.append(
                {
                    "demand": demand,
                    "road_fleet_total": fleet,
                    "resource_frame": "matched_road_fleet",
                    "graph_scope": "top10",
                    "return_strategy": "reverse_network",
                    "overall_winner": "bus_only" if delta < 0 else "static_multimodal",
                    "mean_delta_bus_minus_multimodal": delta,
                    "mean_bus_completion_rate": 1.0,
                    "mean_multimodal_completion_rate": 1.0,
                }
            )
    _write_csv(analysis / "demand_fleet.csv", demand_rows)

    adaptive_rows: list[dict[str, object]] = []
    for state_index, (status, multiplier) in enumerate(
        (("available", 1.0), ("degraded", 1.5), ("unavailable", ""))
    ):
        for policy_index, policy in enumerate(POLICIES):
            completion = 0.0 if status == "unavailable" and policy == "static_multimodal" else 1.0
            adaptive_rows.append(
                {
                    "resource_frame": "matched_road_fleet",
                    "rail_status": status,
                    "rail_multiplier": multiplier,
                    "graph_scope": "top10",
                    "return_strategy": "reverse_network",
                    "policy_id": policy,
                    "mean_completion_rate": completion,
                    "mean_finite_makespan": "" if completion == 0.0 else 280 + state_index * 30 + policy_index * 7,
                    "rank": policy_index + 1,
                    "winner": str(policy_index == 0),
                }
            )
    _write_csv(analysis / "adaptive_policies.csv", adaptive_rows)

    csv_names = (
        "graph_scope_route_metrics.csv",
        "graph_scope_stability.csv",
        "paired_summary.csv",
        "break_even.csv",
        "road_rail_map.csv",
        "demand_fleet.csv",
        "adaptive_policies.csv",
    )
    analyses = {
        "graph_scope_route_metrics": {"status": "available"},
        "graph_scope_stability": {"status": "available"},
        "paired_summary": {"status": "available"},
        "break_even": {"status": "available"},
        "road_rail_map": {"status": "available"},
        "demand_fleet": {"status": "available"},
        "adaptive_policies": {"status": "available"},
    }
    artifacts = []
    for name in csv_names:
        path = analysis / name
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            row_count = sum(1 for _ in csv.DictReader(handle))
        artifacts.append(
            {"path": name, "sha256": _sha256(path), "data_row_count": row_count}
        )
    manifest = {
        "schema_version": 2,
        "final_study_ready": False,
        "stage": "full",
        "analysis_complete_full": True,
        "analysis_completeness_blockers": [],
        "analyses": analyses,
        "generated_csv_files": artifacts,
    }
    (analysis / "analysis_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return analysis


def test_loader_maps_full_analysis() -> None:
    module = _load(DATA_MODULE_PATH, "revision_figure_data_mapping_test")
    with TemporaryDirectory() as tmp:
        analysis = _make_full_fixture(Path(tmp))
        data = module.load_revision_figure_data(analysis)
    assert data.graph_scope.scopes == SCOPES
    assert len(data.graph_scope.routes) == 16
    assert len(data.paired.points) == len(SCENARIOS)
    assert data.break_even.points[2] == (1.6, 10.0)
    assert len(data.road_rail.cells) == 30
    assert len(data.demand_fleet.cells) == 16
    assert len(data.adaptive.cells) == 21


def test_loader_rejects_smoke_and_hash_mismatch() -> None:
    module = _load(DATA_MODULE_PATH, "revision_figure_data_guard_test")
    with TemporaryDirectory() as tmp:
        analysis = _make_full_fixture(Path(tmp))
        manifest_path = analysis / "analysis_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["stage"] = "smoke"
        manifest["analysis_complete_full"] = False
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        try:
            module.load_revision_figure_data(analysis)
        except ValueError as error:
            assert "full" in str(error)
        else:
            raise AssertionError("smoke analysis must be rejected")

        analysis = _make_full_fixture(Path(tmp) / "hash")
        with (analysis / "paired_summary.csv").open("a", encoding="utf-8") as handle:
            handle.write("tampered\n")
        try:
            module.load_revision_figure_data(analysis)
        except ValueError as error:
            assert "SHA-256" in str(error)
        else:
            raise AssertionError("hash mismatch must be rejected")


def test_synthetic_full_analysis_renders_figures_3_to_6() -> None:
    data_module = _load(DATA_MODULE_PATH, "revision_figure_data_render_test")
    figure_module = _load(FIGURE_MODULE_PATH, "revision_figure_render_test")
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        analysis = _make_full_fixture(root)
        data = data_module.load_revision_figure_data(analysis)
        output = root / "figures"
        output.mkdir()
        rendered = figure_module.build_revision_figures(data, output_dir=output)
        expected = {
            "fig3_bpr_noop.png",
            "fig4_segment_decomposition.png",
            "fig5_rail_substitution.png",
            "fig6_assumption_collapse.png",
        }
        assert {path.name for path in rendered} == expected
        assert all(path.is_file() and path.stat().st_size > 10_000 for path in rendered)


def test_forbidden_figure_text_guard() -> None:
    figure_module = _load(FIGURE_MODULE_PATH, "revision_figure_text_guard_test")
    figure, axis = figure_module.plt.subplots()
    axis.text(0.5, 0.5, "실측 결과")
    try:
        figure_module._assert_figure_text(figure, "synthetic")
    except AssertionError as error:
        assert "실측" in str(error)
    else:
        raise AssertionError("forbidden figure text must fail")
    finally:
        figure_module.plt.close(figure)


def main() -> int:
    test_loader_maps_full_analysis()
    print("PASS: full analysis maps to figure data")
    test_loader_rejects_smoke_and_hash_mismatch()
    print("PASS: stage and hash guards fail closed")
    test_synthetic_full_analysis_renders_figures_3_to_6()
    print("PASS: synthetic full analysis renders figures 3--6")
    test_forbidden_figure_text_guard()
    print("PASS: forbidden figure text guard")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
