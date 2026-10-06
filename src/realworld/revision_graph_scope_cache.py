"""Strict isolated caches for paper-revision graph sensitivity scopes."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any

import networkx as nx

from src.realworld.osm_network import load_graphml, save_graphml
from src.realworld.pilot_experiments import (
    EXACT_CORRIDOR_CANDIDATE_METHOD,
    EXPANDED_CORRIDOR_CANDIDATE_METHOD,
    HYBRID_CORRIDOR_METHOD_VERSION,
    pilot_experiment_multi_corridor_subgraphs,
)


CACHE_SCHEMA_VERSION = 2
CACHE_KIND = "paper_revision_graph_scope_cache"
CACHE_MANIFEST_NAME = "manifest.json"
CACHE_PROGRESS_NAME = "build_progress.jsonl"


class GraphScopeCacheError(RuntimeError):
    """Raised when an existing graph-scope cache is stale or corrupt."""


@dataclass(frozen=True)
class GraphScopeCacheResult:
    graphs: Mapping[int, nx.DiGraph]
    status: str
    manifest_path: Path
    progress_path: Path
    manifest: Mapping[str, Any]


def load_or_build_graph_scope_cache(
    full_graph: nx.DiGraph,
    *,
    cache_root: str | Path,
    source_graphml_sha256: str,
    builder_fingerprint: str,
    scope_input_fingerprint: str,
    path_counts: Sequence[int] = (3, 5, 10),
    builder: Callable[..., Mapping[int, nx.DiGraph]] = (
        pilot_experiment_multi_corridor_subgraphs
    ),
    progress: Callable[[Mapping[str, Any]], None] | None = None,
) -> GraphScopeCacheResult:
    """Load valid reduced scopes or build them once under isolated output root.

    Existing cache state is never silently replaced. Source SHA, builder and
    scope-input fingerprints, method version, GraphML byte hashes, graph sizes,
    and embedded candidate metadata must all match. Any stale or partial state
    raises ``GraphScopeCacheError``.
    """

    root = Path(cache_root).expanduser().resolve()
    counts = _validated_path_counts(path_counts)
    source_sha = _validated_sha256(source_graphml_sha256, "source GraphML")
    builder_sha = _validated_sha256(builder_fingerprint, "builder fingerprint")
    scope_input_sha = _validated_sha256(
        scope_input_fingerprint,
        "scope input fingerprint",
    )
    manifest_path = root / CACHE_MANIFEST_NAME
    progress_path = root / CACHE_PROGRESS_NAME

    if manifest_path.exists():
        manifest = _read_manifest(manifest_path)
        graphs = _load_valid_cache(
            full_graph,
            root=root,
            manifest=manifest,
            source_sha=source_sha,
            builder_fingerprint=builder_sha,
            scope_input_fingerprint=scope_input_sha,
            path_counts=counts,
        )
        _append_progress(progress_path, {"event": "cache_hit"}, progress)
        return GraphScopeCacheResult(
            graphs=graphs,
            status="hit",
            manifest_path=manifest_path,
            progress_path=progress_path,
            manifest=manifest,
        )

    if root.exists() and any(root.iterdir()):
        raise GraphScopeCacheError(
            f"graph-scope cache is partial: missing {CACHE_MANIFEST_NAME}"
        )
    root.mkdir(parents=True, exist_ok=True)
    _append_progress(
        progress_path,
        {
            "event": "build_started",
            "method_version": HYBRID_CORRIDOR_METHOD_VERSION,
            "builder_fingerprint": builder_sha,
            "scope_input_fingerprint": scope_input_sha,
            "path_counts": list(counts),
        },
        progress,
    )

    def forward(event: Mapping[str, Any]) -> None:
        _append_progress(progress_path, event, progress)

    graphs = dict(
        builder(
            full_graph,
            path_counts=counts,
            progress=forward,
        )
    )
    if set(graphs) != set(counts):
        raise GraphScopeCacheError(
            "graph-scope builder returned unexpected path-count keys"
        )

    scope_records: dict[str, dict[str, Any]] = {}
    for count in counts:
        graph = graphs[count]
        _validate_graph_metadata(graph, count)
        filename = f"top{count}.graphml"
        path = root / filename
        _atomic_save_graphml(graph, path)
        record = {
            "file": filename,
            "sha256": _sha256_file(path),
            "size_bytes": path.stat().st_size,
            "nodes": graph.number_of_nodes(),
            "edges": graph.number_of_edges(),
            "candidate_method": graph.graph["corridor_candidate_method"],
            "leg_candidates": json.loads(
                str(graph.graph["corridor_leg_candidates_json"])
            ),
        }
        scope_records[f"top{count}"] = record
        _append_progress(
            progress_path,
            {
                "event": "scope_cached",
                "scope": f"top{count}",
                "nodes": record["nodes"],
                "edges": record["edges"],
                "sha256": record["sha256"],
            },
            progress,
        )

    manifest: dict[str, Any] = {
        "schema_version": CACHE_SCHEMA_VERSION,
        "cache_kind": CACHE_KIND,
        "method_version": HYBRID_CORRIDOR_METHOD_VERSION,
        "builder_module": "src.realworld.pilot_experiments",
        "builder_name": "pilot_experiment_multi_corridor_subgraphs",
        "builder_fingerprint": builder_sha,
        "scope_input_fingerprint": scope_input_sha,
        "source_graphml_sha256": source_sha,
        "source_graph_nodes": full_graph.number_of_nodes(),
        "source_graph_edges": full_graph.number_of_edges(),
        "path_counts": list(counts),
        "scopes": scope_records,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "final_study_ready": False,
    }
    _atomic_write_json(manifest_path, manifest)
    _append_progress(progress_path, {"event": "build_complete"}, progress)
    return GraphScopeCacheResult(
        graphs=graphs,
        status="built",
        manifest_path=manifest_path,
        progress_path=progress_path,
        manifest=manifest,
    )


def _load_valid_cache(
    full_graph: nx.DiGraph,
    *,
    root: Path,
    manifest: Mapping[str, Any],
    source_sha: str,
    builder_fingerprint: str,
    scope_input_fingerprint: str,
    path_counts: tuple[int, ...],
) -> dict[int, nx.DiGraph]:
    if manifest.get("schema_version") != CACHE_SCHEMA_VERSION:
        raise GraphScopeCacheError("graph-scope cache schema version mismatch")
    if manifest.get("cache_kind") != CACHE_KIND:
        raise GraphScopeCacheError("graph-scope cache kind mismatch")
    if manifest.get("method_version") != HYBRID_CORRIDOR_METHOD_VERSION:
        raise GraphScopeCacheError("graph-scope cache method version mismatch")
    if manifest.get("builder_fingerprint") != builder_fingerprint:
        raise GraphScopeCacheError("graph-scope cache builder fingerprint mismatch")
    if manifest.get("scope_input_fingerprint") != scope_input_fingerprint:
        raise GraphScopeCacheError("graph-scope cache scope input fingerprint mismatch")
    if manifest.get("source_graphml_sha256") != source_sha:
        raise GraphScopeCacheError("graph-scope cache source GraphML SHA-256 mismatch")
    if manifest.get("source_graph_nodes") != full_graph.number_of_nodes():
        raise GraphScopeCacheError("graph-scope cache source node count mismatch")
    if manifest.get("source_graph_edges") != full_graph.number_of_edges():
        raise GraphScopeCacheError("graph-scope cache source edge count mismatch")
    if manifest.get("path_counts") != list(path_counts):
        raise GraphScopeCacheError("graph-scope cache path counts mismatch")
    scopes = manifest.get("scopes")
    if not isinstance(scopes, Mapping) or set(scopes) != {
        f"top{count}" for count in path_counts
    }:
        raise GraphScopeCacheError("graph-scope cache scope set mismatch")

    graphs: dict[int, nx.DiGraph] = {}
    for count in path_counts:
        scope_id = f"top{count}"
        record = scopes[scope_id]
        if not isinstance(record, Mapping):
            raise GraphScopeCacheError(f"{scope_id} cache record must be an object")
        expected_filename = f"{scope_id}.graphml"
        if record.get("file") != expected_filename:
            raise GraphScopeCacheError(f"{scope_id} cache filename mismatch")
        path = root / expected_filename
        if not path.is_file():
            raise GraphScopeCacheError(f"{scope_id} GraphML is missing")
        expected_sha = _validated_sha256(record.get("sha256"), f"{scope_id} GraphML")
        if _sha256_file(path) != expected_sha:
            raise GraphScopeCacheError(f"{scope_id} GraphML SHA-256 mismatch")
        try:
            loaded = load_graphml(path, force_multigraph=False, normalize=False)
        except Exception as exc:
            raise GraphScopeCacheError(f"{scope_id} GraphML cannot be read") from exc
        graph = loaded if isinstance(loaded, nx.DiGraph) else nx.DiGraph(loaded)
        if graph.number_of_nodes() != record.get("nodes"):
            raise GraphScopeCacheError(f"{scope_id} cached node count mismatch")
        if graph.number_of_edges() != record.get("edges"):
            raise GraphScopeCacheError(f"{scope_id} cached edge count mismatch")
        _validate_graph_metadata(graph, count)
        embedded = json.loads(str(graph.graph["corridor_leg_candidates_json"]))
        if embedded != record.get("leg_candidates"):
            raise GraphScopeCacheError(f"{scope_id} candidate metadata mismatch")
        if graph.graph["corridor_candidate_method"] != record.get(
            "candidate_method"
        ):
            raise GraphScopeCacheError(f"{scope_id} candidate method mismatch")
        graphs[count] = graph
    return graphs


def _validate_graph_metadata(graph: nx.DiGraph, path_count: int) -> None:
    if graph.graph.get("corridor_method_version") != HYBRID_CORRIDOR_METHOD_VERSION:
        raise GraphScopeCacheError(f"top{path_count} method metadata mismatch")
    try:
        stored_count = int(graph.graph.get("corridor_path_count"))
    except (TypeError, ValueError) as exc:
        raise GraphScopeCacheError(
            f"top{path_count} corridor path count is invalid"
        ) from exc
    if stored_count != path_count:
        raise GraphScopeCacheError(f"top{path_count} corridor path count mismatch")
    expected_method = (
        EXACT_CORRIDOR_CANDIDATE_METHOD
        if path_count <= 3
        else EXPANDED_CORRIDOR_CANDIDATE_METHOD
    )
    if graph.graph.get("corridor_candidate_method") != expected_method:
        raise GraphScopeCacheError(f"top{path_count} candidate method mismatch")
    raw = graph.graph.get("corridor_leg_candidates_json")
    try:
        metadata = json.loads(str(raw))
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise GraphScopeCacheError(
            f"top{path_count} candidate metadata is invalid"
        ) from exc
    if not isinstance(metadata, dict) or set(metadata) != {
        "A_to_D",
        "A_to_S",
        "R_to_D",
    }:
        raise GraphScopeCacheError(f"top{path_count} candidate leg set mismatch")
    for leg, item in metadata.items():
        if not isinstance(item, dict):
            raise GraphScopeCacheError(f"top{path_count} {leg} metadata is invalid")
        candidate_count = item.get("candidate_count")
        exact_count = item.get("exact_shortest_count")
        expansion_count = item.get("expansion_count")
        if not all(
            isinstance(value, int) and not isinstance(value, bool) and value >= 0
            for value in (candidate_count, exact_count, expansion_count)
        ):
            raise GraphScopeCacheError(f"top{path_count} {leg} counts are invalid")
        if candidate_count > path_count or exact_count > min(3, candidate_count):
            raise GraphScopeCacheError(f"top{path_count} {leg} counts are inconsistent")
        if expansion_count != candidate_count - exact_count:
            raise GraphScopeCacheError(f"top{path_count} {leg} expansion count mismatch")
        if item.get("method") != expected_method:
            raise GraphScopeCacheError(f"top{path_count} {leg} method mismatch")


def _validated_path_counts(values: Sequence[int]) -> tuple[int, ...]:
    counts = tuple(values)
    if counts != (3, 5, 10):
        raise ValueError("paper-revision graph scope path_counts must be (3, 5, 10)")
    return counts


def _validated_sha256(value: Any, label: str) -> str:
    text = str(value or "").lower()
    if len(text) != 64 or any(character not in "0123456789abcdef" for character in text):
        raise GraphScopeCacheError(f"{label} SHA-256 is invalid")
    return text


def _read_manifest(path: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GraphScopeCacheError("graph-scope cache manifest cannot be read") from exc
    if not isinstance(value, dict):
        raise GraphScopeCacheError("graph-scope cache manifest must be an object")
    return value


def _append_progress(
    path: Path,
    event: Mapping[str, Any],
    callback: Callable[[Mapping[str, Any]], None] | None,
) -> None:
    row = {
        "at_utc": datetime.now(timezone.utc).isoformat(),
        **{str(key): value for key, value in event.items()},
    }
    encoded = json.dumps(row, ensure_ascii=False, sort_keys=True, allow_nan=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(encoded + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    if callback is not None:
        callback(row)


def _atomic_save_graphml(graph: nx.DiGraph, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    os.close(descriptor)
    temp_path = Path(temp_name)
    try:
        save_graphml(graph, temp_path)
        os.replace(temp_path, path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def _atomic_write_json(path: Path, value: Mapping[str, Any]) -> None:
    encoded = (
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    descriptor, temp_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temp_path = Path(temp_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
