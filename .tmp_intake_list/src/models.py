"""Stochastic and physical models for the transport simulation.

- BPR travel time with wartime scaling
- Bernoulli link failure
- LogNormal arrival delay (lateness)
- Reroute cost computation
"""

import networkx as nx
import numpy as np

from src.disruptions import blocked_edges, sample_edge_disruptions


def bpr_travel_time(
    t0: float,
    volume: float,
    capacity: float,
    alpha: float = 0.15,
    beta: float = 4.0,
    scale: float = 1.0,
) -> float:
    """BPR volume-delay function with wartime congestion scaling.

    t_e = t0 * (1 + alpha * (v/C)^beta)
    where v/C is scaled by `scale` factor (s >= 1 means worse congestion).

    Args:
        t0: free-flow travel time (min)
        volume: traffic volume (veh/hr)
        capacity: link capacity (veh/hr)
        alpha: BPR alpha parameter
        beta: BPR beta parameter
        scale: wartime congestion scaling factor

    Returns:
        Congested travel time (min)
    """
    if capacity <= 0:
        return float("inf")
    vc = scale * volume / capacity
    return t0 * (1.0 + alpha * vc**beta)


def sample_link_failures(
    G: nx.DiGraph,
    p_fail_scale: float,
    rng: np.random.Generator,
    *,
    mode: str = "blocked",
    capacity_reduction_factor: float = 0.5,
    rail_immune: bool = True,
) -> list[tuple[str, str]]:
    """Sample which road links fail using Bernoulli trials.

    Each road link fails with probability min(p_fail * p_fail_scale, 1.0).
    Rail links are not subject to failure.

    Args:
        G: transport network graph
        p_fail_scale: multiplier for base failure probabilities
        rng: numpy random generator

    Returns:
        List of (from, to) tuples for failed edges
    """
    disruptions = sample_edge_disruptions(
        G,
        p_fail_scale,
        rng,
        mode=mode,
        capacity_reduction_factor=capacity_reduction_factor,
        rail_immune=rail_immune,
    )
    return blocked_edges(disruptions)


def sample_arrival_delays(
    n_personnel: int,
    mu: float,
    sigma: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Sample arrival delays (lateness) for each person.

    Uses LogNormal distribution: Y ~ LogNormal(mu, sigma^2)
    Returns delays in minutes.

    Args:
        n_personnel: total number of personnel
        mu: LogNormal mu parameter
        sigma: LogNormal sigma parameter (controls tail heaviness)
        rng: numpy random generator

    Returns:
        Array of delay values (min) for each person
    """
    return rng.lognormal(mu, sigma, size=n_personnel)


def compute_travel_times(
    G: nx.DiGraph,
    scale: float,
    p_fail_scale: float,
    failed_edges: list[tuple[str, str]],
    volume: float = 100.0,
    alpha: float = 0.15,
    beta: float = 4.0,
) -> dict[tuple[str, str], float]:
    """Compute travel time for each edge considering congestion and failures.

    Failed edges get infinite travel time (unreachable via that link).
    Non-failed edges use BPR with wartime scaling.

    Args:
        G: transport network
        scale: congestion scaling factor
        p_fail_scale: failure rate multiplier (for reference)
        failed_edges: list of failed edge tuples
        volume: assumed traffic volume for BPR
        alpha, beta: BPR parameters

    Returns:
        Dict mapping (from, to) -> travel time (min)
    """
    failed_set = set(failed_edges)
    times = {}
    for u, v, data in G.edges(data=True):
        if (u, v) in failed_set:
            times[(u, v)] = float("inf")
        else:
            times[(u, v)] = bpr_travel_time(
                t0=data["t0"],
                volume=volume,
                capacity=data["capacity"],
                alpha=alpha,
                beta=beta,
                scale=scale,
            )
    return times


def find_shortest_path_time(
    G: nx.DiGraph,
    travel_times: dict[tuple[str, str], float],
    source: str,
    target: str,
) -> tuple[float, list[str]]:
    """Find shortest path considering current travel times.

    Returns (total_time, path). If unreachable, returns (inf, []).
    """
    G_temp = G.copy()
    for u, v in G_temp.edges():
        G_temp[u][v]["weight"] = travel_times.get((u, v), float("inf"))

    try:
        path = nx.shortest_path(G_temp, source, target, weight="weight")
        total_time = nx.shortest_path_length(G_temp, source, target, weight="weight")
        return total_time, path
    except nx.NetworkXNoPath:
        return float("inf"), []
