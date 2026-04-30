"""Design of Experiments grid generation."""

from itertools import product

from src.policies import build_policies


def phase1_grid(config: dict) -> list[tuple[float, float]]:
    """Phase 1: congestion_scale (s) x failure_rate (p_fail_scale) grid.

    Returns list of (s, p_fail_scale) tuples.
    """
    s_levels = config["congestion_scale"]["levels"]
    p_levels = config["failure_rate"]["levels"]
    return list(product(s_levels, p_levels))


def phase2_grid(config: dict) -> list[tuple[float, object]]:
    """Phase 2: lateness_sigma x policy grid.

    Returns list of (sigma, policy) tuples.
    """
    sigma_levels = config["lateness"]["sigma_levels"]
    policies = build_policies(config)
    return list(product(sigma_levels, policies))
