"""KCI runtime helpers: corridor graph build, origin selection, config merge."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as fh:
        value = yaml.safe_load(fh)
    if not isinstance(value, dict):
        raise ValueError(f"{path} did not contain a YAML mapping")
    return value


def load_region_with_origin(region_path: str | Path,
                            origin_candidates_path: str | Path | None,
                            origin_code: str | None) -> dict[str, Any]:
    """Load region YAML; optionally replace canonical A assembly_zone with the
    selected origin record from origin_candidates.json."""
    region = load_yaml(region_path)
    if origin_code is None:
        return region
    if origin_candidates_path is None:
        raise ValueError("origin_code given but origin_candidates_path is None")
    with Path(origin_candidates_path).open(encoding="utf-8") as fh:
        candidates = json.load(fh)
    origins = {o["id"]: o for o in candidates["origins"]}
    if origin_code not in origins:
        raise ValueError(
            f"Origin code {origin_code!r} not in {sorted(origins)}"
        )
    chosen = origins[origin_code]
    region = deepcopy(region)
    assembly = region["assembly_zones"][0]
    assembly["name"] = f"Origin {origin_code} — {chosen['name']}"
    assembly["lat"] = chosen["lat"]
    assembly["lon"] = chosen["lon"]
    assembly.setdefault("metadata", {})
    md = assembly["metadata"]
    md["origin_code"] = origin_code
    md["origin_name"] = chosen["name"]
    md["origin_verification"] = chosen.get("verification", "unspecified")
    return region


def build_corridor_graph(region: dict[str, Any], cache_path: str | Path):
    """Return the simulator-ready DiGraph from the cached OSM corridor."""
    from src.realworld import (
        build_simulator_graph,
        load_graphml,
    )

    road = load_graphml(cache_path, normalize=True)
    sim = build_simulator_graph(road, region)
    sim.graph["network_variant"] = region.get("network_variant", "baseline")
    return sim


def merge_config_paths(config: dict[str, Any]) -> dict[str, Any]:
    """Ensure expected KCI path defaults are present in config."""
    defaults = {
        "region_path": "data/regions/songpa_yangju_corridor.yaml",
        "cache_path": "data/cache/songpa_yangju_corridor.graphml",
        "origin_candidates_path": "data/regions/origin_candidates.json",
        "output_dir": "results",
    }
    for k, v in defaults.items():
        config.setdefault(k, v)
    return config


def apply_seeds_override(config: dict[str, Any], seeds: int | None) -> dict[str, Any]:
    if seeds is None:
        return config
    config = deepcopy(config)
    config.setdefault("experiment", {})
    config["experiment"]["R"] = int(seeds)
    return config


def apply_grid_preset(config: dict[str, Any], grid: str | None) -> dict[str, Any]:
    """Apply DoE grid density preset.

    pilot   : minimum cells used by smoke runs (2 s × 2 p).
    focused : robustness slice (2 s × 3 p) for origins B/C/D.
    full    : whatever the config already declares (no change).
    """
    if grid is None or grid == "full":
        return config
    config = deepcopy(config)
    if grid == "pilot":
        config["congestion_scale"]["levels"] = [1.0, 1.5]
        config["failure_rate"]["levels"] = [0.0, 1.0]
    elif grid == "focused":
        config["congestion_scale"]["levels"] = [1.0, 1.5]
        config["failure_rate"]["levels"] = [0.0, 1.0, 2.0]
    else:
        raise ValueError(f"Unknown --grid preset: {grid!r}")
    return config
