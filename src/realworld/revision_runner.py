"""Execution helpers for isolated paper-revision simulation campaigns.

Canonical pilot outputs remain read-only.  This module builds explicit revision
configs, stable run identities, deterministic threat-edge samples, and CSV
artifacts under a separate result tree.  Higher-level campaign planning lives
in the CLI so these helpers stay small and directly testable.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import json
import math
import random
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import networkx as nx

from src.realworld.revision_campaign import assert_isolated_output_path
from src.realworld.revision_policies import (
    ResourceFrameId,
    RevisionPolicyId,
    resolve_road_fleet,
)


Edge = tuple[str, str]


def build_configuration_id(parameters: Mapping[str, Any]) -> str:
    """Return stable short SHA-256 identity for JSON-safe parameters."""

    if not isinstance(parameters, Mapping):
        raise TypeError("configuration parameters must be a mapping")
    payload = _canonical_json(dict(parameters)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def selected_edges_checksum(edges: Sequence[Edge]) -> str:
    """Return order-invariant SHA-256 over a directed edge set."""

    normalized = sorted({(str(u), str(v)) for u, v in edges})
    return hashlib.sha256(_canonical_json(normalized).encode("utf-8")).hexdigest()


def select_seeded_random_edges(
    graph: nx.DiGraph,
    *,
    count: int,
    seed: int,
) -> tuple[Edge, ...]:
    """Select reproducible physical-road edges, excluding synthetic connectors."""

    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        raise ValueError("count must be a positive integer")
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ValueError("seed must be a non-negative integer")

    candidates = sorted(
        (
            (str(u), str(v))
            for u, v, data in graph.edges(data=True)
            if data.get("mode", "road") == "road"
            and data.get("source") != "connector"
            and data.get("highway") != "connector"
            and (
                data.get("length_m") is None
                or float(data.get("length_m")) > 0.0
            )
        ),
        key=lambda edge: (
            str(graph.edges[edge].get("realworld_edge_id", "")),
            edge[0],
            edge[1],
        ),
    )
    if count > len(candidates):
        raise ValueError(
            f"count={count} exceeds available road edges={len(candidates)}"
        )
    sampled = random.Random(seed).sample(candidates, count)
    return tuple(sorted(sampled))


def apply_revision_config(
    base_config: Mapping[str, Any],
    *,
    policy_id: RevisionPolicyId | str,
    resource_frame: ResourceFrameId | str,
    demand: int,
    road_fleet_total: int | None = None,
    return_strategy: str = "reverse_network",
    rail_status: str = "available",
    rail_multiplier: float | None = 1.0,
) -> dict[str, Any]:
    """Copy base config and apply one explicit policy/resource condition."""

    policy = _coerce_policy(policy_id)
    frame = _coerce_frame(resource_frame)
    demand = _positive_int(demand, "demand")
    if return_strategy not in {"legacy_none", "reverse_network"}:
        raise ValueError("return_strategy must be legacy_none or reverse_network")
    if rail_status not in {"available", "degraded", "unavailable"}:
        raise ValueError("rail_status must be available, degraded, or unavailable")
    if rail_status == "degraded":
        rail_multiplier = _at_least_one(rail_multiplier, "rail_multiplier")
    elif rail_status == "available":
        rail_multiplier = 1.0
    else:
        rail_multiplier = None

    config = copy.deepcopy(dict(base_config))
    config.setdefault("personnel", {})["total"] = demand
    config.setdefault("metrics", {})["include_extended"] = True
    config.setdefault("fleet", {})["return_strategy"] = return_strategy
    config.setdefault("failure", {}).setdefault("rerouting", {})[
        "cache_departure_path"
    ] = True
    multimodal = config.setdefault("multimodal", {})
    multimodal["rail_status"] = rail_status
    multimodal["rail_degradation_multiplier"] = rail_multiplier

    allocation = _scaled_allocation(policy, frame, road_fleet_total)
    bus = config.setdefault("bus", {})
    if allocation["direct_bus"] > 0:
        bus["fleet_size"] = allocation["direct_bus"]
    multimodal["shuttle_fleet_size"] = max(1, allocation["feeder_shuttle"])
    multimodal["lastmile_fleet_size"] = max(1, allocation["last_mile_bus"])

    adaptation = config.setdefault("adaptation", {})
    adaptation["policy_id"] = policy.value
    if allocation["fallback_bus"] > 0:
        adaptation["fallback_fleet_size"] = allocation["fallback_bus"]
        adaptation["fallback_fleet_location"] = "S_prepositioned"
    else:
        adaptation.pop("fallback_fleet_size", None)
        adaptation.pop("fallback_fleet_location", None)
    if policy.value.startswith("station_fallback_"):
        adaptation["station_fallback_min"] = float(policy.value.rsplit("_", 1)[1])
    if policy is RevisionPolicyId.SPLIT_600_400:
        adaptation["rail_share"] = 0.6
    return config


def apply_forced_failure_config(
    base_config: Mapping[str, Any],
    *,
    edges: Sequence[Edge],
    mode: str,
    capacity_factor: float = 1.0,
    travel_time_multiplier: float = 1.0,
) -> dict[str, Any]:
    """Copy config and attach a sparse deterministic edge-disruption set."""

    if mode not in {"none", "blocked", "capacity_reduction"}:
        raise ValueError("mode must be none, blocked, or capacity_reduction")
    capacity_factor = float(capacity_factor)
    travel_time_multiplier = float(travel_time_multiplier)
    if not math.isfinite(capacity_factor) or not 0.0 <= capacity_factor <= 1.0:
        raise ValueError("capacity_factor must be finite and between zero and one")
    if (
        not math.isfinite(travel_time_multiplier)
        or travel_time_multiplier <= 0.0
    ):
        raise ValueError("travel_time_multiplier must be finite and positive")

    normalized = sorted({(str(u), str(v)) for u, v in edges})
    if mode != "none" and not normalized:
        raise ValueError("a forced disruption requires at least one edge")
    config = copy.deepcopy(dict(base_config))
    failure = config.setdefault("failure", {})
    failure["forced_edges"] = [[u, v] for u, v in normalized]
    failure["mode"] = mode
    failure["capacity_reduction_factor"] = (
        capacity_factor if mode == "capacity_reduction" else 1.0
    )
    failure["road_travel_time_multiplier"] = travel_time_multiplier
    return config


def write_campaign_csv(
    output_path: str | Path,
    rows: Sequence[Mapping[str, Any]],
) -> Path:
    """Write stable union-schema CSV outside canonical results."""

    path = assert_isolated_output_path(output_path)
    fieldnames: list[str] = []
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping):
            raise TypeError("campaign rows must be mappings")
        for key in row:
            key_text = str(key)
            if key_text not in seen:
                seen.add(key_text)
                fieldnames.append(key_text)
    if not fieldnames:
        raise ValueError("campaign rows must not be empty")

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: _csv_value(row.get(key, ""))
                    for key in fieldnames
                }
            )
    return path


def _scaled_allocation(
    policy: RevisionPolicyId,
    frame: ResourceFrameId,
    road_fleet_total: int | None,
) -> dict[str, int]:
    if road_fleet_total is None:
        fixed = resolve_road_fleet(policy, frame)
        return {
            "direct_bus": fixed.direct_bus,
            "feeder_shuttle": fixed.feeder_shuttle,
            "last_mile_bus": fixed.last_mile_bus,
            "fallback_bus": fixed.fallback_bus,
        }

    total = _positive_int(road_fleet_total, "road_fleet_total")
    if policy is RevisionPolicyId.BUS_ONLY:
        return {
            "direct_bus": total,
            "feeder_shuttle": 0,
            "last_mile_bus": 0,
            "fallback_bus": 0,
        }
    if frame is ResourceFrameId.CONFIGURED_BUNDLE:
        if policy is RevisionPolicyId.SPLIT_600_400:
            return {
                "direct_bus": total,
                "feeder_shuttle": total,
                "last_mile_bus": total,
                "fallback_bus": 0,
            }
        if policy.value.startswith("station_fallback_"):
            return {
                "direct_bus": 0,
                "feeder_shuttle": total,
                "last_mile_bus": total,
                "fallback_bus": total,
            }
        return {
            "direct_bus": 0,
            "feeder_shuttle": total,
            "last_mile_bus": total,
            "fallback_bus": 0,
        }
    if policy is RevisionPolicyId.SPLIT_600_400:
        direct, feeder, last = _largest_remainder(total, (6, 9, 8))
        return {
            "direct_bus": direct,
            "feeder_shuttle": feeder,
            "last_mile_bus": last,
            "fallback_bus": 0,
        }
    if policy.value.startswith("station_fallback_"):
        feeder, last, fallback = _largest_remainder(total, (8, 8, 7))
        return {
            "direct_bus": 0,
            "feeder_shuttle": feeder,
            "last_mile_bus": last,
            "fallback_bus": fallback,
        }
    feeder, last = _largest_remainder(total, (12, 11))
    return {
        "direct_bus": 0,
        "feeder_shuttle": feeder,
        "last_mile_bus": last,
        "fallback_bus": 0,
    }


def _largest_remainder(total: int, weights: Sequence[int]) -> tuple[int, ...]:
    weight_sum = sum(weights)
    raw = [total * weight / weight_sum for weight in weights]
    allocated = [math.floor(value) for value in raw]
    remaining = total - sum(allocated)
    order = sorted(
        range(len(weights)),
        key=lambda index: (-(raw[index] - allocated[index]), index),
    )
    for index in order[:remaining]:
        allocated[index] += 1
    if total >= len(weights) and any(value == 0 for value in allocated):
        raise ValueError("road fleet allocation left an active role empty")
    return tuple(allocated)


def _coerce_policy(value: RevisionPolicyId | str) -> RevisionPolicyId:
    try:
        return RevisionPolicyId(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"unknown revision policy: {value!r}") from exc


def _coerce_frame(value: ResourceFrameId | str) -> ResourceFrameId:
    try:
        return ResourceFrameId(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"unknown resource frame: {value!r}") from exc


def _positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _at_least_one(value: Any, name: str) -> float:
    if value is None:
        raise ValueError(f"{name} is required")
    numeric = float(value)
    if not math.isfinite(numeric) or numeric < 1.0:
        raise ValueError(f"{name} must be finite and at least one")
    return numeric


def _canonical_json(value: Any) -> str:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(f"value must be canonical JSON: {exc}") from exc


def _csv_value(value: Any) -> Any:
    if isinstance(value, (dict, list, tuple)):
        return _canonical_json(value)
    return value


__all__ = [
    "apply_forced_failure_config",
    "apply_revision_config",
    "build_configuration_id",
    "selected_edges_checksum",
    "select_seeded_random_edges",
    "write_campaign_csv",
]
