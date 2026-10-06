"""Direct tests for fast, isolated paper-revision graph-scope caches."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.realworld.pilot_experiments import (
    HYBRID_CORRIDOR_METHOD_VERSION,
    pilot_experiment_multi_corridor_subgraphs,
)
from src.realworld.revision_graph_scope_cache import (
    GraphScopeCacheError,
    load_or_build_graph_scope_cache,
)


def _many_route_graph() -> nx.DiGraph:
    graph = nx.DiGraph()
    for source, target in (("A", "D"), ("A", "S"), ("R", "D")):
        for index in range(12):
            middle = f"{source}_{target}_{index:02d}"
            # Strict ordering makes exact top-3 observable. Higher candidates
            # remain available to penalty diversification.
            graph.add_edge(
                source,
                middle,
                mode="road",
                t0=1.0 + index,
                length_m=100.0 + index,
            )
            graph.add_edge(
                middle,
                target,
                mode="road",
                t0=1.0,
                length_m=100.0,
            )
    graph.graph["fixture"] = "many_routes"
    return graph


def _scope_edges(graph: nx.DiGraph) -> set[tuple[str, str]]:
    return {(str(u), str(v)) for u, v in graph.edges}


def test_hybrid_scopes_keep_exact_top3_and_nested_penalty_expansion() -> None:
    events: list[dict[str, object]] = []
    scopes = pilot_experiment_multi_corridor_subgraphs(
        _many_route_graph(),
        path_counts=(3, 5, 10),
        progress=lambda event: events.append(dict(event)),
    )

    assert set(scopes) == {3, 5, 10}
    assert _scope_edges(scopes[3]) < _scope_edges(scopes[5])
    assert _scope_edges(scopes[5]) < _scope_edges(scopes[10])
    for path_count, graph in scopes.items():
        metadata = json.loads(graph.graph["corridor_leg_candidates_json"])
        assert graph.graph["corridor_method_version"] == HYBRID_CORRIDOR_METHOD_VERSION
        assert graph.graph["corridor_path_count"] == path_count
        assert set(metadata) == {"A_to_D", "A_to_S", "R_to_D"}
        assert {item["candidate_count"] for item in metadata.values()} == {
            path_count
        }
        assert {item["exact_shortest_count"] for item in metadata.values()} == {3}
        assert {item["expansion_count"] for item in metadata.values()} == {
            path_count - 3
        }
        expected_method = (
            "exact_shortest_simple_paths"
            if path_count == 3
            else "exact_top3_plus_deterministic_penalty_diversification"
        )
        assert graph.graph["corridor_candidate_method"] == expected_method
        assert {item["method"] for item in metadata.values()} == {expected_method}

    # Exact top-3 paths must be rank 0, 1, 2 on every leg.
    for source, target in (("A", "D"), ("A", "S"), ("R", "D")):
        for index in range(3):
            middle = f"{source}_{target}_{index:02d}"
            assert (source, middle) in scopes[3].edges
            assert (middle, target) in scopes[3].edges
        assert (source, f"{source}_{target}_03") not in scopes[3].edges
    assert any(event["event"] == "leg_candidates_ready" for event in events)
    print("PASS: exact top3 and nested deterministic expanded scopes")


def test_hybrid_builder_never_enumerates_a_fourth_exact_simple_path() -> None:
    original_simple = nx.shortest_simple_paths
    exact_yields: dict[tuple[str, str], int] = {}

    def guarded_simple_paths(graph, source, target, weight=None):
        key = (str(source), str(target))
        for index, path in enumerate(
            original_simple(graph, source, target, weight=weight), start=1
        ):
            if index > 3:
                raise AssertionError("hybrid builder requested exact path rank > 3")
            exact_yields[key] = index
            yield path

    nx.shortest_simple_paths = guarded_simple_paths
    try:
        scopes = pilot_experiment_multi_corridor_subgraphs(
            _many_route_graph(), path_counts=(3, 5, 10)
        )
    finally:
        nx.shortest_simple_paths = original_simple

    assert set(scopes) == {3, 5, 10}
    assert exact_yields == {("A", "D"): 3, ("A", "S"): 3, ("R", "D"): 3}
    print("PASS: exact simple-path enumeration is hard-capped at top3")


def test_scope_cache_round_trip_reuses_files_and_records_strict_manifest() -> None:
    with TemporaryDirectory() as temp_dir:
        cache_root = Path(temp_dir) / "isolated" / "_graph_scope_cache"
        source_sha = "a" * 64
        builder_fingerprint = "1" * 64
        scope_input_fingerprint = "2" * 64
        first = load_or_build_graph_scope_cache(
            _many_route_graph(),
            cache_root=cache_root,
            source_graphml_sha256=source_sha,
            builder_fingerprint=builder_fingerprint,
            scope_input_fingerprint=scope_input_fingerprint,
            path_counts=(3, 5, 10),
        )
        assert first.status == "built"
        assert set(first.graphs) == {3, 5, 10}
        manifest = json.loads(first.manifest_path.read_text(encoding="utf-8"))
        assert manifest["source_graphml_sha256"] == source_sha
        assert manifest["builder_fingerprint"] == builder_fingerprint
        assert manifest["scope_input_fingerprint"] == scope_input_fingerprint
        assert manifest["method_version"] == HYBRID_CORRIDOR_METHOD_VERSION
        assert manifest["source_graph_nodes"] == _many_route_graph().number_of_nodes()
        assert manifest["source_graph_edges"] == _many_route_graph().number_of_edges()
        assert set(manifest["scopes"]) == {"top3", "top5", "top10"}
        for item in manifest["scopes"].values():
            assert len(item["sha256"]) == 64
            assert item["nodes"] > 0
            assert item["edges"] > 0

        second = load_or_build_graph_scope_cache(
            _many_route_graph(),
            cache_root=cache_root,
            source_graphml_sha256=source_sha,
            builder_fingerprint=builder_fingerprint,
            scope_input_fingerprint=scope_input_fingerprint,
            path_counts=(3, 5, 10),
            builder=lambda *args, **kwargs: (_ for _ in ()).throw(
                AssertionError("cache hit must not rebuild")
            ),
        )
        assert second.status == "hit"
        assert set(second.graphs) == {3, 5, 10}
        progress_rows = [
            json.loads(line)
            for line in second.progress_path.read_text(encoding="utf-8").splitlines()
        ]
        assert progress_rows[-1]["event"] == "cache_hit"
    print("PASS: isolated strict graph-scope cache is reused")


def test_scope_cache_rejects_stale_source_and_corrupt_graph() -> None:
    with TemporaryDirectory() as temp_dir:
        cache_root = Path(temp_dir) / "isolated" / "_graph_scope_cache"
        built = load_or_build_graph_scope_cache(
            _many_route_graph(),
            cache_root=cache_root,
            source_graphml_sha256="b" * 64,
            builder_fingerprint="3" * 64,
            scope_input_fingerprint="4" * 64,
            path_counts=(3, 5, 10),
        )
        try:
            load_or_build_graph_scope_cache(
                _many_route_graph(),
                cache_root=cache_root,
                source_graphml_sha256="c" * 64,
                builder_fingerprint="3" * 64,
                scope_input_fingerprint="4" * 64,
                path_counts=(3, 5, 10),
            )
        except GraphScopeCacheError as error:
            assert "source GraphML SHA-256" in str(error)
        else:
            raise AssertionError("stale graph-scope cache was accepted")

        top5 = cache_root / "top5.graphml"
        top5.write_bytes(top5.read_bytes() + b"corrupt")
        try:
            load_or_build_graph_scope_cache(
                _many_route_graph(),
                cache_root=cache_root,
                source_graphml_sha256="b" * 64,
                builder_fingerprint="3" * 64,
                scope_input_fingerprint="4" * 64,
                path_counts=(3, 5, 10),
            )
        except GraphScopeCacheError as error:
            assert "SHA-256" in str(error)
        else:
            raise AssertionError("corrupt graph-scope cache was accepted")
        assert built.manifest_path.exists()
    print("PASS: stale and corrupt graph-scope caches are rejected")


def test_scope_cache_rejects_changed_builder_or_scope_inputs() -> None:
    with TemporaryDirectory() as temp_dir:
        cache_root = Path(temp_dir) / "isolated" / "_graph_scope_cache"
        graph = _many_route_graph()
        load_or_build_graph_scope_cache(
            graph,
            cache_root=cache_root,
            source_graphml_sha256="5" * 64,
            builder_fingerprint="6" * 64,
            scope_input_fingerprint="7" * 64,
        )

        for keyword, changed_value, expected_message in (
            ("builder_fingerprint", "8" * 64, "builder fingerprint"),
            ("scope_input_fingerprint", "9" * 64, "scope input fingerprint"),
        ):
            arguments = {
                "cache_root": cache_root,
                "source_graphml_sha256": "5" * 64,
                "builder_fingerprint": "6" * 64,
                "scope_input_fingerprint": "7" * 64,
            }
            arguments[keyword] = changed_value
            try:
                load_or_build_graph_scope_cache(graph, **arguments)
            except GraphScopeCacheError as error:
                assert expected_message in str(error)
            else:
                raise AssertionError(f"changed {keyword} was accepted")
    print("PASS: builder and scope-input fingerprint changes invalidate cache")


def test_scope_cache_rejects_legacy_manifest_without_fingerprints() -> None:
    with TemporaryDirectory() as temp_dir:
        cache_root = Path(temp_dir) / "isolated" / "_graph_scope_cache"
        graph = _many_route_graph()
        result = load_or_build_graph_scope_cache(
            graph,
            cache_root=cache_root,
            source_graphml_sha256="a" * 64,
            builder_fingerprint="b" * 64,
            scope_input_fingerprint="c" * 64,
        )
        manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
        manifest.pop("builder_fingerprint")
        manifest.pop("scope_input_fingerprint")
        result.manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        try:
            load_or_build_graph_scope_cache(
                graph,
                cache_root=cache_root,
                source_graphml_sha256="a" * 64,
                builder_fingerprint="b" * 64,
                scope_input_fingerprint="c" * 64,
            )
        except GraphScopeCacheError as error:
            assert "builder fingerprint" in str(error)
        else:
            raise AssertionError("legacy manifest without fingerprints was accepted")
    print("PASS: legacy manifests without fingerprints fail closed")


if __name__ == "__main__":
    test_hybrid_scopes_keep_exact_top3_and_nested_penalty_expansion()
    test_hybrid_builder_never_enumerates_a_fourth_exact_simple_path()
    test_scope_cache_round_trip_reuses_files_and_records_strict_manifest()
    test_scope_cache_rejects_stale_source_and_corrupt_graph()
    test_scope_cache_rejects_changed_builder_or_scope_inputs()
    test_scope_cache_rejects_legacy_manifest_without_fingerprints()
    print("test_revision_graph_scope_cache: all checks passed")
