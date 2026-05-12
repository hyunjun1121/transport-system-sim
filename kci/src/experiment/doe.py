"""Design of Experiments grid generation."""

from __future__ import annotations

from itertools import product
from typing import NamedTuple

from src.network import network_variant_levels
from src.policies import build_policies


class Phase1Point(NamedTuple):
    """One Phase 1 sensitivity point."""

    s: float
    p_fail_scale: float
    network_variant: str
    failure_mode: str
    capacity_reduction_factor: float | None


class Phase2Point(NamedTuple):
    """One Phase 2 policy/lateness point plus active experiment metadata."""

    sigma: float
    policy: object
    network_variant: str
    failure_mode: str
    capacity_reduction_factor: float | None


def phase1_grid(config: dict) -> list[Phase1Point]:
    """Phase 1: congestion x failure x network/failure-semantics grid."""
    s_levels = config["congestion_scale"]["levels"]
    p_levels = config["failure_rate"]["levels"]
    variants = network_variant_levels(config)
    failure_points = failure_sensitivity_points(config)

    rows: list[Phase1Point] = []
    for s, p_fail_scale, variant, failure_point in product(
        s_levels,
        p_levels,
        variants,
        failure_points,
    ):
        failure_mode, capacity_reduction_factor = failure_point
        rows.append(
            Phase1Point(
                s=float(s),
                p_fail_scale=float(p_fail_scale),
                network_variant=variant,
                failure_mode=failure_mode,
                capacity_reduction_factor=capacity_reduction_factor,
            )
        )
    return rows


def phase2_grid(config: dict) -> list[Phase2Point]:
    """Phase 2: lateness_sigma x policy grid with active network/failure metadata."""
    sigma_levels = config["lateness"]["sigma_levels"]
    policies = build_policies(config)
    variant = active_network_variant(config)
    failure_mode, capacity_reduction_factor = active_failure_point(config)

    return [
        Phase2Point(
            sigma=float(sigma),
            policy=policy,
            network_variant=variant,
            failure_mode=failure_mode,
            capacity_reduction_factor=capacity_reduction_factor,
        )
        for sigma, policy in product(sigma_levels, policies)
    ]


def active_network_variant(config: dict) -> str:
    """Return the single active network variant."""
    return str(config.get("network", {}).get("variant", "baseline"))


def active_failure_point(config: dict) -> tuple[str, float | None]:
    """Return the active failure mode/factor pair."""
    failure = config.get("failure", {})
    mode = str(failure.get("mode", "blocked"))
    factor = failure.get("capacity_reduction_factor", 0.5)
    return _failure_point(mode, factor)


def failure_sensitivity_points(config: dict) -> list[tuple[str, float | None]]:
    """Return configured failure-mode sensitivity points.

    Capacity-reduction factors are only crossed with ``capacity_reduction``.
    ``blocked`` rows carry ``None`` for the factor to keep semantics explicit.
    """
    failure = config.get("failure", {})
    modes = failure.get("mode_levels", [failure.get("mode", "blocked")])
    factors = failure.get(
        "capacity_reduction_factor_levels",
        [failure.get("capacity_reduction_factor", 0.5)],
    )

    if isinstance(modes, str):
        modes = [modes]

    points: list[tuple[str, float | None]] = []
    for mode in modes:
        mode = str(mode)
        if mode == "blocked":
            points.append((mode, None))
        elif mode == "capacity_reduction":
            for factor in factors:
                points.append(_failure_point(mode, factor))
        else:
            raise ValueError(
                "failure mode must be 'blocked' or 'capacity_reduction', "
                f"got {mode!r}"
            )

    if not points:
        raise ValueError("failure.mode_levels must contain at least one mode")
    return points


def _failure_point(mode: str, factor: object) -> tuple[str, float | None]:
    if mode == "blocked":
        return mode, None
    if mode != "capacity_reduction":
        raise ValueError(
            "failure mode must be 'blocked' or 'capacity_reduction', "
            f"got {mode!r}"
        )

    factor_value = float(factor)
    if not 0.0 < factor_value <= 1.0:
        raise ValueError(
            "capacity_reduction_factor must satisfy 0 < factor <= 1, "
            f"got {factor!r}"
        )
    return mode, factor_value
