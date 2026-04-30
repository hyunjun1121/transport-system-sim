"""Abstract transport network builder.

Creates a NetworkX DiGraph from config.yaml parameters.
Nodes: H(거주지), A(집결지), S(허브/역), R(철도 도착역), D(전방 목적지)
plus intermediate road nodes (D1, D2) for multi-link routes.
"""

import networkx as nx


def build_network(config: dict) -> nx.DiGraph:
    """Build abstract transport network from config.

    Returns a directed graph where each edge has attributes:
        t0: free-flow travel time (min)
        capacity: link capacity (veh/hr)
        p_fail: base failure probability
        mode: 'road' or 'rail'
        headway: (rail only) interval between trains (min)
    """
    G = nx.DiGraph()

    # Add nodes
    for node in config["network"]["nodes"]:
        G.add_node(node)
    # Add intermediate road nodes (e.g. D1, D2)
    for link in config["network"]["road_links"]:
        if link[0] not in G:
            G.add_node(link[0])
        if link[1] not in G:
            G.add_node(link[1])

    # Add road links
    for link in config["network"]["road_links"]:
        G.add_edge(
            link[0], link[1],
            t0=link[2],
            capacity=link[3],
            p_fail=link[4],
            mode="road",
        )

    # Add rail link
    rail = config["network"]["rail_link"][0]
    G.add_edge(
        rail[0], rail[1],
        t0=rail[2],
        headway=rail[3],
        capacity=rail[4],
        p_fail=0.0,  # rail doesn't fail in this model
        mode="rail",
    )

    return G


def get_road_path(G: nx.DiGraph) -> list[str]:
    """Return the bus-only route: A → D via road network."""
    return nx.shortest_path(G, "A", "D", weight="t0")


def get_multimodal_path(G: nx.DiGraph) -> list[tuple[str, str, str]]:
    """Return the multimodal route segments as (from, to, mode).

    Route: A → S (shuttle/road), S → R (rail), R → D (last-mile/road)
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
        print(f"  {u} → {v} [{mode}] t0={t0}min")
