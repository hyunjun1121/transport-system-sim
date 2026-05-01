"""Abstract transport network builder.

Creates a NetworkX DiGraph from config.yaml parameters.
Nodes: H(home), A(assembly), S(hub/station), R(rail arrival), D(destination)
plus intermediate road nodes (D1, D2) for multi-link routes.
"""

from __future__ import annotations

from copy import deepcopy

import networkx as nx


DEFAULT_NETWORK_VARIANT = "baseline"


def build_network(config: dict, variant: str | None = None) -> nx.DiGraph:
    """Build abstract transport network from config.

    Args:
        config: Project configuration.
        variant: Optional named network variant. When omitted, the config's
            ``network.variant`` value is used, defaulting to ``baseline``.

    Returns a directed graph where each edge has attributes:
        t0: free-flow travel time (min)
        capacity: link capacity (veh/hr)
        p_fail: base failure probability
        mode: 'road' or 'rail'
        headway: (rail only) interval between trains (min)
    """
    spec = resolve_network_spec(config, variant)
    variant_name = spec["variant"]
    G = nx.DiGraph(network_variant=variant_name)

    for node in spec["nodes"]:
        G.add_node(node)

    for link in spec["road_links"]:
        G.add_node(link[0])
        G.add_node(link[1])
        G.add_edge(
            link[0],
            link[1],
            t0=link[2],
            capacity=link[3],
            p_fail=link[4],
            mode="road",
        )

    for rail in spec["rail_link"]:
        G.add_node(rail[0])
        G.add_node(rail[1])
        G.add_edge(
            rail[0],
            rail[1],
            t0=rail[2],
            headway=rail[3],
            capacity=rail[4],
            p_fail=0.0,  # rail doesn't fail in this model
            mode="rail",
        )

    return G


def config_for_network_variant(config: dict, variant: str | None = None) -> dict:
    """Return a deep-copied config with top-level network links resolved."""
    spec = resolve_network_spec(config, variant)
    resolved = deepcopy(config)
    network = resolved["network"]
    network["variant"] = spec["variant"]
    network["nodes"] = deepcopy(spec["nodes"])
    network["road_links"] = deepcopy(spec["road_links"])
    network["rail_link"] = deepcopy(spec["rail_link"])
    return resolved


def network_variant_levels(config: dict) -> list[str]:
    """Return configured network variants for experiment sweeps."""
    network = config.get("network", {})
    levels = network.get("variant_levels")
    if levels is None:
        levels = [network.get("variant", DEFAULT_NETWORK_VARIANT)]

    if isinstance(levels, str):
        levels = [levels]

    variants = [str(level) for level in levels]
    if not variants:
        raise ValueError("network.variant_levels must contain at least one variant")

    for variant in variants:
        resolve_network_spec(config, variant)
    return variants


def resolve_network_spec(config: dict, variant: str | None = None) -> dict:
    """Resolve one network variant into concrete nodes, road links, and rail."""
    network = config["network"]
    variant_name = str(
        variant
        if variant is not None
        else network.get("variant", DEFAULT_NETWORK_VARIANT)
    )

    variants = network.get("variants", {})
    if variant_name in variants:
        variant_config = variants.get(variant_name) or {}
    elif variant_name == DEFAULT_NETWORK_VARIANT:
        variant_config = {}
    else:
        available = sorted(available_network_variants(config))
        raise KeyError(
            f"unknown network variant {variant_name!r}; available={available}"
        )

    return {
        "variant": variant_name,
        "nodes": variant_config.get("nodes", network["nodes"]),
        "road_links": variant_config.get("road_links", network["road_links"]),
        "rail_link": variant_config.get("rail_link", network["rail_link"]),
    }


def available_network_variants(config: dict) -> list[str]:
    """Return all network variant names declared by config."""
    variants = set(config.get("network", {}).get("variants", {}))
    variants.add(config.get("network", {}).get("variant", DEFAULT_NETWORK_VARIANT))
    variants.add(DEFAULT_NETWORK_VARIANT)
    return sorted(variants)


def get_road_path(G: nx.DiGraph) -> list[str]:
    """Return the bus-only route: A -> D via road network."""
    return nx.shortest_path(G, "A", "D", weight="t0")


def get_multimodal_path(G: nx.DiGraph) -> list[tuple[str, str, str]]:
    """Return the multimodal route segments as (from, to, mode).

    Route: A -> S (shuttle/road), S -> R (rail), R -> D (last-mile/road)
    """
    return [
        ("A", "S", "road"),   # shuttle to hub
        ("S", "R", "rail"),   # main rail
        ("R", "D", "road"),   # last-mile
    ]


def print_network(G: nx.DiGraph) -> None:
    """Print network summary."""
    print(f"Nodes: {list(G.nodes())}")
    print(f"Edges:")
    for u, v, data in G.edges(data=True):
        mode = data.get("mode", "?")
        t0 = data.get("t0", "?")
        print(f"  {u} -> {v} [{mode}] t0={t0}min")
