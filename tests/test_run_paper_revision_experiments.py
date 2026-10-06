"""Direct tests for restartable paper-revision experiment CLI."""

from __future__ import annotations

import csv
from dataclasses import replace
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import run_paper_revision_experiments as cli
from src.realworld.revision_campaign import CampaignPathError, CheckpointError
from src.realworld.revision_design import load_revision_design
from src.realworld.revision_planner import PlannedCondition


DESIGN_PATH = ROOT / "data" / "manifests" / "paper_revision_experiment_design.json"


def _implementation_provenance(fingerprint: str = "f" * 64):
    return {
        "fingerprint": fingerprint,
        "artifacts": {
            "scripts/run_paper_revision_experiments.py": {
                "path": str(ROOT / "scripts" / "run_paper_revision_experiments.py"),
                "sha256": "e" * 64,
                "size_bytes": 1,
            }
        },
    }


def _runtime_provenance(fingerprint: str = "r" * 64):
    return {
        "fingerprint": fingerprint,
        "python": {"implementation": "CPython", "version": "3.12.10"},
        "packages": {
            "networkx": "3.6.1",
            "numpy": "2.4.6",
            "scipy": "1.17.1",
            "SALib": "1.5.2",
            "PyYAML": "6.0.3",
        },
    }


def _input_provenance(paths, fingerprint: str = "i" * 64):
    return {
        "fingerprint": fingerprint,
        "artifacts": {
            name: cli._artifact_record(path)
            for name, path in paths.items()
        },
    }


def _condition(
    *,
    campaign_id: str = "paired_reanalysis",
    configuration_id: str = "a" * 16,
    graph_scope: str = "top10",
    scenario_id: str = "no_disruption",
    seed: int = 3101,
    policy_id: str = "bus_only",
    threat_seed: int | None = None,
) -> PlannedCondition:
    return PlannedCondition(
        campaign_id=campaign_id,
        configuration_id=configuration_id,
        policy_id=policy_id,
        resource_frame="configured_bundle",
        graph_scope=graph_scope,
        corridor_path_count=None if graph_scope == "full" else int(graph_scope[3:]),
        arrival_seed=seed,
        threat_seed=threat_seed,
        threat_draw=None,
        rail_status="available",
        rail_multiplier=1.0,
        scenario_id=scenario_id,
        parameters={
            "departure_policy_id": "strict",
            "return_strategy": "reverse_network",
        },
    )


def _graph(marker: str = "full") -> nx.DiGraph:
    graph = nx.DiGraph()
    graph.add_edge("A", "D", mode="road", t0=2.0, realworld_edge_id="ad")
    graph.add_edge("A", "B", mode="road", t0=1.0, realworld_edge_id="ab")
    graph.add_edge("B", "A", mode="road", t0=1.0, realworld_edge_id="ba")
    graph.add_edge("A", "S", mode="road", t0=1.0, realworld_edge_id="as")
    graph.add_edge("S", "A", mode="road", t0=1.0, realworld_edge_id="sa")
    graph.add_edge("R", "D", mode="road", t0=1.0, realworld_edge_id="rd")
    graph.add_edge("D", "R", mode="road", t0=1.0, realworld_edge_id="dr")
    graph.graph["marker"] = marker
    return graph


class _Patch:
    def __init__(self, **replacements):
        self.replacements = replacements
        self.originals = {}

    def __enter__(self):
        for name, value in self.replacements.items():
            self.originals[name] = getattr(cli, name)
            setattr(cli, name, value)
        return self

    def __exit__(self, exc_type, exc, traceback):
        for name, value in self.originals.items():
            setattr(cli, name, value)


def _common_fakes(conditions, calls):
    full_graph = _graph()

    def fake_load(**kwargs):
        calls["loads"] = calls.get("loads", 0) + 1
        return SimpleNamespace(
            region={"region_id": "goseong", "network": {}},
            region_id="goseong",
            graph=full_graph,
        )

    def fake_reduce_all(graph, *, path_counts):
        calls.setdefault("reductions", []).append(tuple(path_counts))
        reduced = {}
        for path_count in path_counts:
            item = graph.copy()
            item.graph["marker"] = f"top{path_count}"
            reduced[path_count] = item
        return reduced

    def fake_scope_cache(
        graph,
        *,
        cache_root,
        source_graphml_sha256,
        builder_fingerprint,
        scope_input_fingerprint,
        path_counts,
        progress=None,
    ):
        calls.setdefault("scope_cache", []).append(
            (
                Path(cache_root),
                source_graphml_sha256,
                builder_fingerprint,
                scope_input_fingerprint,
                tuple(path_counts),
            )
        )
        reduced = fake_reduce_all(graph, path_counts=path_counts)
        root = Path(cache_root)
        root.mkdir(parents=True, exist_ok=True)
        manifest_path = root / "manifest.json"
        progress_path = root / "build_progress.jsonl"
        manifest_path.write_text("{}\n", encoding="utf-8")
        progress_path.write_text('{"event":"cache_hit"}\n', encoding="utf-8")
        return SimpleNamespace(
            graphs=reduced,
            status="hit",
            manifest_path=manifest_path,
            progress_path=progress_path,
            manifest={
                "method_version": "fixture",
                "builder_fingerprint": builder_fingerprint,
                "scope_input_fingerprint": scope_input_fingerprint,
                "scopes": {
                    "top10": {
                        "candidate_method": (
                            "exact_top3_plus_deterministic_penalty_diversification"
                        )
                    }
                },
            },
        )

    def fake_execute(graph, base_config, condition, *, disruption):
        calls.setdefault("executions", []).append(
            (condition.configuration_id, graph.graph["marker"], disruption.edges)
        )
        return {"completion_rate": 1.0, "makespan": 10.0}

    return {
        "load_pilot_inputs": fake_load,
        "pilot_experiment_multi_corridor_subgraphs": fake_reduce_all,
        "load_or_build_graph_scope_cache": fake_scope_cache,
        "_implementation_provenance": _implementation_provenance,
        "_runtime_provenance": _runtime_provenance,
        "_input_provenance": _input_provenance,
        "_artifact_record": lambda path: {
            "path": str(Path(path)),
            "sha256": "0" * 64,
            "size_bytes": 1,
        },
        "make_pilot_base_config": lambda region: {"personnel": {"total": 1000}},
        "apply_pilot_demand_fleet_profiles": lambda config, **kwargs: (config, {}),
        "load_disruption_scenarios": lambda *args, **kwargs: (),
        "plan_campaign_conditions": lambda design, campaign_id, stage: tuple(conditions),
        "execute_condition": fake_execute,
    }


def test_max_runs_loads_full_graph_once_and_writes_campaign_artifacts():
    calls = {}
    conditions = tuple(
        _condition(configuration_id=character * 16, seed=3101 + index)
        for index, character in enumerate(("a", "b", "c"))
    )
    with TemporaryDirectory() as temp_dir:
        output_root = Path(temp_dir) / "revision-output"
        input_paths = {
            name: Path(temp_dir) / name
            for name in ("region.yaml", "network.graphml", "overrides.csv", "scenarios.csv")
        }
        for name, path in input_paths.items():
            path.write_text(name, encoding="utf-8")
        with _Patch(**_common_fakes(conditions, calls)):
            result = cli.run_revision_campaigns(
                design_path=DESIGN_PATH,
                campaign_ids=("paired_reanalysis",),
                stage="smoke",
                region_path=input_paths["region.yaml"],
                cache_path=input_paths["network.graphml"],
                overrides_path=input_paths["overrides.csv"],
                scenarios_path=input_paths["scenarios.csv"],
                output_root=output_root,
                max_runs=1,
                resume=True,
            )

        assert calls["loads"] == 1
        assert calls["reductions"] == [(3, 5, 10)]
        assert calls["scope_cache"] == [
            (
                output_root.resolve() / "_graph_scope_cache",
                "0" * 64,
                "f" * 64,
                "i" * 64,
                (3, 5, 10),
            )
        ]
        assert len(calls["executions"]) == 1
        campaign = result["campaigns"]["paired_reanalysis"]
        manifest = json.loads(Path(campaign["manifest_path"]).read_text(encoding="utf-8"))
        assert manifest["planned_run_count"] == 3
        assert manifest["completed_run_count"] == 1
        assert manifest["new_run_count"] == 1
        assert manifest["status"] == "partial"
        assert manifest["final_study_ready"] is False
        assert manifest["graph_scope_cache"]["status"] == "hit"
        assert manifest["graph_scope_cache"]["method_version"] == "fixture"
        assert manifest["graph_scope_cache"]["builder_fingerprint"] == "f" * 64
        assert (
            manifest["graph_scope_cache"]["scope_input_fingerprint"] == "i" * 64
        )
        assert manifest["main_execution_scope"] == "top10"
        assert manifest["main_corridor_path_count"] == 10
        assert manifest["main_scope_candidate_method"] == (
            "exact_top3_plus_deterministic_penalty_diversification"
        )
        assert "not exact global top-10" in manifest["main_scope_interpretation"]
        assert manifest["edge_selection_scopes"] == {
            "graph_scope_campaign": "top3",
            "main_campaigns": "top10",
        }
        assert manifest["central_trunk_target_segment"] == (
            "A_to_D_corridor_time_band_20_80"
        )
        assert manifest["central_trunk_selection_method"] == (
            "corridor_time_band"
        )
        assert manifest["random_threat_candidate_rule"] == (
            "physical_road_edges_excluding_synthetic_connectors"
        )
        target_audit = manifest["central_trunk_target_audit"]
        assert target_audit["selected_edge_count"] == 1
        assert target_audit["non_road_edge_count"] == 0
        assert target_audit["connector_edge_count"] == 0
        assert target_audit["nonpositive_length_edge_count"] == 0
        assert set(target_audit["endpoint_shortest_path_overlap_counts"]) == {
            "A_to_S",
            "S_to_A",
            "R_to_D",
            "D_to_R",
        }
        assert not any(
            target_audit["endpoint_shortest_path_overlap_counts"].values()
        )
        assert target_audit["endpoint_shortest_path_status"] == {
            "A_to_S": "available",
            "S_to_A": "available",
            "R_to_D": "available",
            "D_to_R": "available",
        }
        scope_target_audit = manifest["graph_scope_fixed_target_audit"]
        assert scope_target_audit["selection_scope"] == "top3"
        assert scope_target_audit["selected_edge_count"] == 1
        assert scope_target_audit["non_road_edge_count"] == 0
        assert scope_target_audit["connector_edge_count"] == 0
        assert scope_target_audit["nonpositive_length_edge_count"] == 0
        assert set(scope_target_audit["endpoint_shortest_path_status"].values()) == {
            "available"
        }
        assert manifest["implementation_fingerprint"] == "f" * 64
        assert manifest["runtime_fingerprint"] == "r" * 64
        assert manifest["input_fingerprint"] == "i" * 64
        assert manifest["runtime_environment"]["packages"]["networkx"] == "3.6.1"
        assert manifest["runtime_environment"]["packages"]["PyYAML"] == "6.0.3"
        assert set(manifest["implementation_artifacts"]) == {
            "scripts/run_paper_revision_experiments.py"
        }
        assert set(manifest["input_artifacts"]) == {
            "design",
            "region",
            "cache",
            "overrides",
            "scenarios",
            "demand_profiles",
            "fleet_profiles",
        }
        assert set(manifest["output_artifacts"]) == {"results", "checkpoint"}
        for artifact in manifest["output_artifacts"].values():
            assert len(artifact["sha256"]) == 64
        for artifact in manifest["input_artifacts"].values():
            assert len(artifact["sha256"]) == 64
        assert Path(campaign["results_path"]).exists()
        assert Path(campaign["checkpoint_path"]).exists()
        graph_evidence = result["graph_scope_route_evidence"]
        assert Path(graph_evidence["metrics_path"]).exists()
        graph_manifest = json.loads(
            Path(graph_evidence["manifest_path"]).read_text(encoding="utf-8")
        )
        assert graph_manifest["final_study_ready"] is False
        assert graph_manifest["row_count"] == 16
        assert graph_manifest["contains_coordinates"] is False
        assert len(graph_manifest["output_artifact"]["sha256"]) == 64


def test_resume_skips_existing_run_keys_before_simulation():
    calls = {}
    conditions = (
        _condition(configuration_id="a" * 16, seed=3101),
        _condition(configuration_id="b" * 16, seed=3102),
    )
    with TemporaryDirectory() as temp_dir:
        output_root = Path(temp_dir) / "revision-output"
        fakes = _common_fakes(conditions, calls)
        with _Patch(**fakes):
            cli.run_revision_campaigns(
                design_path=DESIGN_PATH,
                campaign_ids=("paired_reanalysis",),
                stage="smoke",
                region_path=Path("region.yaml"),
                cache_path=Path("network.graphml"),
                overrides_path=Path("overrides.csv"),
                scenarios_path=Path("scenarios.csv"),
                output_root=output_root,
                max_runs=1,
                resume=True,
            )
            result = cli.run_revision_campaigns(
                design_path=DESIGN_PATH,
                campaign_ids=("paired_reanalysis",),
                stage="smoke",
                region_path=Path("region.yaml"),
                cache_path=Path("network.graphml"),
                overrides_path=Path("overrides.csv"),
                scenarios_path=Path("scenarios.csv"),
                output_root=output_root,
                max_runs=None,
                resume=True,
            )

        assert len(calls["executions"]) == 2
        manifest_path = result["campaigns"]["paired_reanalysis"]["manifest_path"]
        manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        assert manifest["resumed_run_count"] == 1
        assert manifest["new_run_count"] == 1
        assert manifest["completed_run_count"] == 2
        checkpoint = Path(result["campaigns"]["paired_reanalysis"]["checkpoint_path"])
        assert len(checkpoint.read_text(encoding="utf-8").splitlines()) == 2


def test_changed_implementation_fingerprint_blocks_resume_and_no_resume_replaces():
    calls = {}
    conditions = (
        _condition(configuration_id="a" * 16, seed=3101),
        _condition(configuration_id="b" * 16, seed=3102),
    )
    with TemporaryDirectory() as temp_dir:
        output_root = Path(temp_dir) / "revision-output"
        first_fakes = _common_fakes(conditions, calls)
        first_fakes["_implementation_provenance"] = lambda: (
            _implementation_provenance("a" * 64)
        )
        with _Patch(**first_fakes):
            cli.run_revision_campaigns(
                design_path=DESIGN_PATH,
                campaign_ids=("paired_reanalysis",),
                stage="smoke",
                region_path=Path("region.yaml"),
                cache_path=Path("network.graphml"),
                overrides_path=Path("overrides.csv"),
                scenarios_path=Path("scenarios.csv"),
                output_root=output_root,
                max_runs=1,
                resume=True,
            )

        second_fakes = _common_fakes(conditions, calls)
        second_fakes["_implementation_provenance"] = lambda: (
            _implementation_provenance("b" * 64)
        )
        with _Patch(**second_fakes):
            try:
                cli.run_revision_campaigns(
                    design_path=DESIGN_PATH,
                    campaign_ids=("paired_reanalysis",),
                    stage="smoke",
                    region_path=Path("region.yaml"),
                    cache_path=Path("network.graphml"),
                    overrides_path=Path("overrides.csv"),
                    scenarios_path=Path("scenarios.csv"),
                    output_root=output_root,
                    max_runs=None,
                    resume=True,
                )
            except CheckpointError as exc:
                assert "implementation fingerprint mismatch" in str(exc)
                assert "--no-resume" in str(exc)
            else:
                raise AssertionError("changed implementation was allowed to resume")

            result = cli.run_revision_campaigns(
                design_path=DESIGN_PATH,
                campaign_ids=("paired_reanalysis",),
                stage="smoke",
                region_path=Path("region.yaml"),
                cache_path=Path("network.graphml"),
                overrides_path=Path("overrides.csv"),
                scenarios_path=Path("scenarios.csv"),
                output_root=output_root,
                max_runs=None,
                resume=False,
            )

        campaign = result["campaigns"]["paired_reanalysis"]
        checkpoint = Path(campaign["checkpoint_path"])
        results_path = Path(campaign["results_path"])
        manifest = json.loads(
            Path(campaign["manifest_path"]).read_text(encoding="utf-8")
        )
        assert len(checkpoint.read_text(encoding="utf-8").splitlines()) == 2
        assert len(results_path.read_text(encoding="utf-8").splitlines()) == 3
        assert manifest["implementation_fingerprint"] == "b" * 64
        assert manifest["resume_enabled"] is False
        assert manifest["resumed_run_count"] == 0
        assert manifest["new_run_count"] == 2


def test_changed_runtime_fingerprint_blocks_resume():
    with TemporaryDirectory() as temp_dir:
        checkpoint = Path(temp_dir) / "checkpoint.jsonl"
        manifest = Path(temp_dir) / "manifest.json"
        checkpoint.write_text("{}\n", encoding="utf-8")
        manifest.write_text(
            json.dumps(
                {
                    "implementation_fingerprint": "f" * 64,
                    "runtime_fingerprint": "a" * 64,
                }
            ),
            encoding="utf-8",
        )
        try:
            cli._assert_resume_implementation_matches(
                checkpoint_path=checkpoint,
                manifest_path=manifest,
                implementation_fingerprint="f" * 64,
                runtime_fingerprint="b" * 64,
                input_fingerprint="i" * 64,
            )
        except CheckpointError as exc:
            assert "runtime fingerprint mismatch" in str(exc)
        else:
            raise AssertionError("changed runtime was allowed to resume")


def test_changed_input_fingerprint_blocks_resume():
    with TemporaryDirectory() as temp_dir:
        checkpoint = Path(temp_dir) / "checkpoint.jsonl"
        manifest = Path(temp_dir) / "manifest.json"
        checkpoint.write_text("{}\n", encoding="utf-8")
        manifest.write_text(
            json.dumps(
                {
                    "implementation_fingerprint": "f" * 64,
                    "runtime_fingerprint": "r" * 64,
                    "input_fingerprint": "a" * 64,
                }
            ),
            encoding="utf-8",
        )
        try:
            cli._assert_resume_implementation_matches(
                checkpoint_path=checkpoint,
                manifest_path=manifest,
                implementation_fingerprint="f" * 64,
                runtime_fingerprint="r" * 64,
                input_fingerprint="b" * 64,
            )
        except CheckpointError as exc:
            assert "input fingerprint mismatch" in str(exc)
        else:
            raise AssertionError("changed inputs were allowed to resume")


def test_input_fingerprint_is_path_relocation_safe():
    names = (
        "design",
        "region",
        "cache",
        "overrides",
        "scenarios",
        "demand_profiles",
        "fleet_profiles",
    )
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        left = root / "left"
        right = root / "right"
        left.mkdir()
        right.mkdir()
        left_paths = {}
        right_paths = {}
        for index, name in enumerate(names):
            left_path = left / f"{name}.input"
            right_path = right / f"{name}.input"
            content = f"input-{index}\n"
            left_path.write_text(content, encoding="utf-8")
            right_path.write_text(content, encoding="utf-8")
            left_paths[name] = left_path
            right_paths[name] = right_path

        left_provenance = cli._input_provenance(left_paths)
        right_provenance = cli._input_provenance(right_paths)

    assert left_provenance["fingerprint"] == right_provenance["fingerprint"]
    assert len(left_provenance["fingerprint"]) == 64
    assert set(left_provenance["artifacts"]) == set(names)
    assert {
        name: artifact["sha256"]
        for name, artifact in left_provenance["artifacts"].items()
    } == {
        name: artifact["sha256"]
        for name, artifact in right_provenance["artifacts"].items()
    }
    assert left_provenance["artifacts"]["design"]["path"] != (
        right_provenance["artifacts"]["design"]["path"]
    )


def test_missing_edge_errors_report_count_not_identifiers():
    graph = _graph("top10")
    condition = _condition()
    missing_edge = ("sensitive-node-u", "sensitive-node-v")
    try:
        cli._assert_edges_present(graph, (missing_edge,), condition)
    except ValueError as exc:
        message = str(exc)
        assert "missing_count=1" in message
        assert "sensitive-node-u" not in message
        assert "sensitive-node-v" not in message
    else:
        raise AssertionError("missing selected edge was accepted")


def test_random_threat_manifest_audit_proves_physical_edge_selection():
    graph = _graph("top10")
    graph.add_edge(
        "connector-source",
        "connector-target",
        mode="road",
        source="connector",
        highway="connector",
        length_m=0.0,
    )
    conditions = tuple(
        _condition(
            campaign_id="random_threat_outer",
            configuration_id=character * 16,
            threat_seed=5101 + index,
        )
        for index, character in enumerate(("a", "b"))
    )
    conditions = tuple(
        replace(item, parameters={"blocked_edge_count": 1})
        for item in conditions
    )
    audit = cli._random_threat_selection_audit(graph, conditions)
    assert audit["threat_draw_count"] == 2
    assert audit["selected_edge_count_values"] == [1]
    assert audit["max_non_road_edge_count"] == 0
    assert audit["max_connector_edge_count"] == 0
    assert audit["max_nonpositive_length_edge_count"] == 0
    assert audit["contains_coordinates"] is False


def test_implementation_fingerprint_covers_exact_active_python_files():
    provenance = cli._implementation_provenance()
    repeated = cli._implementation_provenance()
    artifacts = provenance["artifacts"]
    required = {
        "scripts/run_paper_revision_experiments.py",
        "requirements.txt",
    }
    required.update(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "src").rglob("*.py")
    )
    assert set(artifacts) == required
    assert len(provenance["fingerprint"]) == 64
    assert repeated == provenance
    for relative_path, artifact in artifacts.items():
        assert Path(artifact["path"]).resolve() == (ROOT / relative_path).resolve()
        assert len(artifact["sha256"]) == 64
        assert artifact["size_bytes"] > 0


def test_graph_scope_reuses_edges_selected_only_on_top3():
    calls = {}
    conditions = (
        _condition(
            campaign_id="graph_scope",
            configuration_id="a" * 16,
            graph_scope="top3",
            scenario_id="critical",
        ),
        _condition(
            campaign_id="graph_scope",
            configuration_id="b" * 16,
            graph_scope="full",
            scenario_id="critical",
        ),
    )
    scenario = SimpleNamespace(
        scenario_id="critical",
        selection_method="edge_betweenness",
        disruption_mode="blocked",
        capacity_factor=0.0,
        road_travel_time_multiplier=None,
    )
    fakes = _common_fakes(conditions, calls)
    fakes["load_disruption_scenarios"] = lambda *args, **kwargs: (scenario,)

    def fake_select(graph, selected_scenario):
        calls.setdefault("selection_graphs", []).append(graph.graph["marker"])
        edge = ("A", "B") if graph.graph["marker"] == "top3" else ("B", "A")
        return (SimpleNamespace(edge=edge),)

    fakes["select_candidate_edges"] = fake_select
    with TemporaryDirectory() as temp_dir, _Patch(**fakes):
        cli.run_revision_campaigns(
            design_path=DESIGN_PATH,
            campaign_ids=("graph_scope",),
            stage="smoke",
            region_path=Path("region.yaml"),
            cache_path=Path("network.graphml"),
            overrides_path=Path("overrides.csv"),
            scenarios_path=Path("scenarios.csv"),
            output_root=Path(temp_dir) / "revision-output",
            max_runs=None,
            resume=True,
        )

    assert calls["selection_graphs"] == ["top3", "top10"]
    assert [item[2] for item in calls["executions"]] == [
        (("A", "B"),),
        (("A", "B"),),
    ]


def test_main_physical_scenario_selects_top10_and_pairs_edge_checksum():
    calls = {}
    conditions = (
        _condition(
            campaign_id="paired_reanalysis",
            configuration_id="a" * 16,
            scenario_id="critical",
            policy_id="bus_only",
        ),
        _condition(
            campaign_id="paired_reanalysis",
            configuration_id="a" * 16,
            scenario_id="critical",
            policy_id="static_multimodal",
        ),
    )
    scenario = SimpleNamespace(
        scenario_id="critical",
        selection_method="edge_betweenness",
        disruption_mode="blocked",
        capacity_factor=0.0,
        road_travel_time_multiplier=None,
    )
    fakes = _common_fakes(conditions, calls)
    fakes["load_disruption_scenarios"] = lambda *args, **kwargs: (scenario,)

    def fake_select(graph, selected_scenario):
        calls.setdefault("selection_graphs", []).append(graph.graph["marker"])
        edge = ("A", "B") if graph.graph["marker"] == "top3" else ("B", "A")
        return (SimpleNamespace(edge=edge),)

    fakes["select_candidate_edges"] = fake_select
    with TemporaryDirectory() as temp_dir, _Patch(**fakes):
        result = cli.run_revision_campaigns(
            design_path=DESIGN_PATH,
            campaign_ids=("paired_reanalysis",),
            stage="smoke",
            region_path=Path("region.yaml"),
            cache_path=Path("network.graphml"),
            overrides_path=Path("overrides.csv"),
            scenarios_path=Path("scenarios.csv"),
            output_root=Path(temp_dir) / "revision-output",
            max_runs=None,
            resume=True,
        )
        manifest = json.loads(
            Path(
                result["campaigns"]["paired_reanalysis"]["manifest_path"]
            ).read_text(encoding="utf-8")
        )
        checksum = cli.selected_edges_checksum((("B", "A"),))
        with Path(
            result["campaigns"]["paired_reanalysis"]["results_path"]
        ).open(encoding="utf-8", newline="") as handle:
            results = list(csv.DictReader(handle))

    assert calls["selection_graphs"] == ["top3", "top10"]
    assert [item[1] for item in calls["executions"]] == ["top10", "top10"]
    assert [item[2] for item in calls["executions"]] == [
        (("B", "A"),),
        (("B", "A"),),
    ]
    assert manifest["main_scenario_edge_checksums"]["critical"] == checksum
    assert {row["arrival_seed"] for row in results} == {"3101"}
    assert {row["selected_edges_checksum"] for row in results} == {checksum}


def test_main_longhaul_and_random_use_declared_execution_scope():
    top10 = nx.DiGraph()
    top10.graph["marker"] = "top10"
    top10.add_edge("A", "n0", mode="road", t0=1.0)
    for index in range(5):
        top10.add_edge(f"n{index}", f"n{index + 1}", mode="road", t0=1.0)
    top10.add_edge("n5", "D", mode="road", t0=1.0)
    full = top10.copy()
    full.graph["marker"] = "full"
    longhaul = PlannedCondition(
        campaign_id="break_even",
        configuration_id="c" * 16,
        policy_id="bus_only",
        resource_frame="configured_bundle",
        graph_scope="top10",
        corridor_path_count=10,
        arrival_seed=3101,
        threat_seed=None,
        threat_draw=None,
        rail_status="available",
        rail_multiplier=1.0,
        scenario_id="long_haul_break_even",
        parameters={
            "road_multiplier": 1.6,
            "target_segment": "A_to_D_corridor_time_band_20_80",
        },
    )
    selector_calls = []

    def fake_corridor_selector(graph, *, source, target, path_count, **kwargs):
        selector_calls.append((graph.graph["marker"], source, target, path_count))
        return tuple((f"n{index}", f"n{index + 1}") for index in range(5))

    with _Patch(select_corridor_time_band_edges=fake_corridor_selector):
        disruption = cli._prepare_disruption(
            longhaul,
            selection_graph=top10,
            execution_graph=top10,
            scenario_lookup={},
            frozen_edges={},
            frozen_errors={},
            longhaul_cache={},
            region={"region_id": "goseong", "network": {}},
        )
    assert selector_calls == [("top10", "A", "D", 10)]
    assert disruption.edges == (
        ("n0", "n1"),
        ("n1", "n2"),
        ("n2", "n3"),
        ("n3", "n4"),
        ("n4", "n5"),
    )

    random_condition = PlannedCondition(
        campaign_id="random_threat_outer",
        configuration_id="d" * 16,
        policy_id="bus_only",
        resource_frame="configured_bundle",
        graph_scope="top10",
        corridor_path_count=10,
        arrival_seed=3101,
        threat_seed=5101,
        threat_draw=1,
        rail_status="available",
        rail_multiplier=1.0,
        scenario_id="random_blockage_outer",
        parameters={"blocked_edge_count": 1},
    )
    seen = []

    def fake_random(graph, *, count, seed):
        seen.append((graph.graph["marker"], count, seed))
        return (("n1", "n2"),)

    with _Patch(select_seeded_random_edges=fake_random):
        random_disruption = cli._prepare_disruption(
            random_condition,
            selection_graph=top10,
            execution_graph=top10,
            scenario_lookup={},
            frozen_edges={},
            frozen_errors={},
            longhaul_cache={},
            region={"region_id": "goseong", "network": {}},
        )
    assert seen == [("top10", 1, 5101)]
    assert random_disruption.edges == (("n1", "n2"),)


def test_canonical_output_is_rejected_before_graph_load():
    calls = {"loads": 0}

    def fail_load(**kwargs):
        calls["loads"] += 1
        raise AssertionError("graph must not load for rejected output")

    with _Patch(load_pilot_inputs=fail_load):
        try:
            cli.run_revision_campaigns(
                design_path=DESIGN_PATH,
                campaign_ids=("paired_reanalysis",),
                stage="smoke",
                region_path=Path("region.yaml"),
                cache_path=Path("network.graphml"),
                overrides_path=Path("overrides.csv"),
                scenarios_path=Path("scenarios.csv"),
                output_root=ROOT / "results" / "realworld_pilot_nodelink",
                max_runs=1,
                resume=True,
            )
        except CampaignPathError:
            pass
        else:
            raise AssertionError("canonical result output was accepted")
    assert calls["loads"] == 0


def test_road_rail_unavailable_condition_keeps_road_damage_axis():
    graph = nx.DiGraph()
    graph.add_edge("A", "n0", mode="road", t0=1.0)
    for index in range(5):
        graph.add_edge(f"n{index}", f"n{index + 1}", mode="road", t0=1.0)
    graph.add_edge("n5", "D", mode="road", t0=1.0)
    condition = PlannedCondition(
        campaign_id="road_rail_map",
        configuration_id="c" * 16,
        policy_id="bus_only",
        resource_frame="configured_bundle",
        graph_scope="top10",
        corridor_path_count=10,
        arrival_seed=3101,
        threat_seed=None,
        threat_draw=None,
        rail_status="unavailable",
        rail_multiplier=None,
        scenario_id="road_rail_decision_map",
        parameters={
            "road_multiplier": 1.6,
            "target_segment": "A_to_D_corridor_time_band_20_80",
        },
    )
    disruption = cli._prepare_disruption(
        condition,
        selection_graph=graph,
        execution_graph=graph,
        scenario_lookup={},
        frozen_edges={},
        frozen_errors={},
        longhaul_cache={},
        region={"region_id": "goseong", "network": {}},
    )
    assert disruption.edges == (
        ("n0", "n1"),
        ("n1", "n2"),
        ("n2", "n3"),
        ("n3", "n4"),
        ("n4", "n5"),
    )
    assert disruption.travel_time_multiplier == 1.6


def test_morris_run_spec_records_effective_degraded_rail_state():
    condition = PlannedCondition(
        campaign_id="morris",
        configuration_id="d" * 16,
        policy_id="static_multimodal",
        resource_frame="matched_road_fleet",
        graph_scope="top3",
        corridor_path_count=3,
        arrival_seed=3101,
        threat_seed=None,
        threat_draw=None,
        rail_status="available",
        rail_multiplier=1.0,
        scenario_id="morris_screening",
        parameters={
            "factor_values": {"rail_travel_multiplier": 2.0},
            "return_strategy": "reverse_network",
        },
    )
    spec = cli._run_spec_for(condition, cli.PreparedDisruption.none())
    assert spec.rail_status == "degraded"


def test_multiple_campaigns_hash_shared_inputs_once():
    calls = {}
    artifact_calls = []
    conditions = (_condition(),)
    fakes = _common_fakes(conditions, calls)

    def fake_artifact_record(path):
        artifact_calls.append(Path(path))
        return {"path": str(path), "sha256": "0" * 64, "size_bytes": 1}

    fakes["_artifact_record"] = fake_artifact_record
    with TemporaryDirectory() as temp_dir, _Patch(**fakes):
        cli.run_revision_campaigns(
            design_path=DESIGN_PATH,
            campaign_ids=("paired_reanalysis", "graph_scope"),
            stage="smoke",
            region_path=Path("region.yaml"),
            cache_path=Path("network.graphml"),
            overrides_path=Path("overrides.csv"),
            scenarios_path=Path("scenarios.csv"),
            output_root=Path(temp_dir) / "revision-output",
            max_runs=None,
            resume=True,
        )

    # Seven shared inputs once + two per-campaign outputs twice.
    assert len(artifact_calls) == 11


def test_checkpoint_row_error_reports_record_number():
    try:
        cli._checkpoint_rows(
            [{"run_key": "bad", "result": {"policy_id": "bus_only"}}]
        )
    except CheckpointError as exc:
        assert "checkpoint line 1 has invalid run_key" in str(exc)
    else:
        raise AssertionError("invalid checkpoint run_key was accepted")


if __name__ == "__main__":
    test_max_runs_loads_full_graph_once_and_writes_campaign_artifacts()
    test_resume_skips_existing_run_keys_before_simulation()
    test_changed_implementation_fingerprint_blocks_resume_and_no_resume_replaces()
    test_changed_runtime_fingerprint_blocks_resume()
    test_changed_input_fingerprint_blocks_resume()
    test_input_fingerprint_is_path_relocation_safe()
    test_missing_edge_errors_report_count_not_identifiers()
    test_random_threat_manifest_audit_proves_physical_edge_selection()
    test_implementation_fingerprint_covers_exact_active_python_files()
    test_graph_scope_reuses_edges_selected_only_on_top3()
    test_main_physical_scenario_selects_top10_and_pairs_edge_checksum()
    test_main_longhaul_and_random_use_declared_execution_scope()
    test_canonical_output_is_rejected_before_graph_load()
    test_road_rail_unavailable_condition_keeps_road_damage_axis()
    test_morris_run_spec_records_effective_degraded_rail_state()
    test_multiple_campaigns_hash_shared_inputs_once()
    test_checkpoint_row_error_reports_record_number()
    print("test_run_paper_revision_experiments: all checks passed")
