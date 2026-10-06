"""Deterministic paired and nested statistics for manuscript revision.

The helpers in this module keep incomplete simulation outcomes separate from
finite timing comparisons.  They never replace a missing or infinite outcome
with an arbitrary time penalty.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import random
import statistics
from typing import Callable, Hashable, Mapping, Sequence


@dataclass(frozen=True)
class IncompletePair:
    """One seed that cannot contribute a finite paired difference."""

    seed: Hashable
    left: object
    right: object
    reason: str


@dataclass(frozen=True)
class PairingResult:
    """Finite left-minus-right differences and separately reported exclusions."""

    matched_seeds: tuple[Hashable, ...]
    differences: tuple[float, ...]
    incomplete: tuple[IncompletePair, ...]
    total_seed_count: int


@dataclass(frozen=True)
class IntervalEstimate:
    """Point estimate and two-sided confidence interval."""

    estimate: float
    lower: float
    upper: float
    confidence: float
    n: int
    standard_error: float
    critical_value: float

    @property
    def half_width(self) -> float:
        return (self.upper - self.lower) / 2.0


@dataclass(frozen=True)
class BootstrapInterval:
    """Seeded percentile-bootstrap result."""

    estimate: float
    lower: float
    upper: float
    confidence: float
    n: int
    replicates: int
    seed: int


@dataclass(frozen=True)
class ConvergencePoint:
    """Prefix-based replication diagnostic at one replicate count."""

    count: int
    estimate: float
    lower: float
    upper: float
    half_width: float
    estimate_change_from_previous: float | None
    half_width_ratio_to_previous: float | None


@dataclass(frozen=True)
class ZeroCrossingEstimate:
    """Observed-bracket zero crossing; no extrapolation is performed."""

    status: str
    crossing: float | None
    lower_x: float | None
    upper_x: float | None
    lower_y: float | None
    upper_y: float | None
    bracket_count: int


@dataclass(frozen=True)
class ExcludedObservation:
    """Nonfinite observation excluded from a hierarchical bootstrap."""

    threat_draw: Hashable
    arrival_seed: Hashable
    value: object
    reason: str = "nonfinite"


@dataclass(frozen=True)
class HierarchicalBootstrapInterval:
    """Two-level threat-draw/arrival-seed percentile-bootstrap result."""

    estimate: float
    lower: float
    upper: float
    confidence: float
    replicates: int
    seed: int
    threat_draw_count: int
    finite_observation_count: int
    excluded: tuple[ExcludedObservation, ...]
    empty_threat_draws: tuple[Hashable, ...]


@dataclass(frozen=True)
class JointSeedCrossingInterval:
    """Percentile interval from jointly resampled CRN response curves."""

    estimate: float
    lower: float
    upper: float
    confidence: float
    complete_seed_count: int
    excluded_seeds: tuple[Hashable, ...]
    replicates: int
    successful_replicates: int
    seed: int


_MISSING = object()


def pair_finite_outcomes(
    left: Mapping[Hashable, object],
    right: Mapping[Hashable, object],
) -> PairingResult:
    """Match outcomes by seed and return finite ``left - right`` differences.

    Missing and nonfinite outcomes remain visible in ``incomplete``.  This
    prevents a failed run from silently becoming an arbitrary makespan value.
    """

    matched_seeds: list[Hashable] = []
    differences: list[float] = []
    incomplete: list[IncompletePair] = []
    seeds = sorted(set(left) | set(right), key=_stable_key)

    for seed in seeds:
        left_value = left.get(seed, _MISSING)
        right_value = right.get(seed, _MISSING)
        if left_value is _MISSING:
            incomplete.append(
                IncompletePair(seed, None, right_value, "missing_left")
            )
            continue
        if right_value is _MISSING:
            incomplete.append(
                IncompletePair(seed, left_value, None, "missing_right")
            )
            continue

        finite_left = _as_finite_float(left_value)
        finite_right = _as_finite_float(right_value)
        if finite_left is None or finite_right is None:
            if finite_left is None and finite_right is None:
                reason = "nonfinite_both"
            elif finite_left is None:
                reason = "nonfinite_left"
            else:
                reason = "nonfinite_right"
            incomplete.append(
                IncompletePair(seed, left_value, right_value, reason)
            )
            continue

        matched_seeds.append(seed)
        differences.append(finite_left - finite_right)

    return PairingResult(
        matched_seeds=tuple(matched_seeds),
        differences=tuple(differences),
        incomplete=tuple(incomplete),
        total_seed_count=len(seeds),
    )


def t_paired_confidence_interval(
    differences: Sequence[float],
    *,
    confidence: float = 0.95,
) -> IntervalEstimate:
    """Return a Student-t interval for already paired finite differences."""

    values = _require_finite_values(differences, minimum=2)
    _validate_confidence(confidence)
    estimate = statistics.fmean(values)
    standard_deviation = statistics.stdev(values)
    standard_error = standard_deviation / math.sqrt(len(values))
    if standard_error == 0.0:
        critical_value = _student_t_quantile(
            (1.0 + confidence) / 2.0, len(values) - 1
        )
        return IntervalEstimate(
            estimate,
            estimate,
            estimate,
            confidence,
            len(values),
            0.0,
            critical_value,
        )

    critical_value = _student_t_quantile(
        (1.0 + confidence) / 2.0, len(values) - 1
    )
    half_width = critical_value * standard_error
    return IntervalEstimate(
        estimate=estimate,
        lower=estimate - half_width,
        upper=estimate + half_width,
        confidence=confidence,
        n=len(values),
        standard_error=standard_error,
        critical_value=critical_value,
    )


def percentile_bootstrap_ci(
    values: Sequence[float],
    *,
    statistic: Callable[[Sequence[float]], float] = statistics.fmean,
    confidence: float = 0.95,
    replicates: int = 10_000,
    seed: int = 20260721,
) -> BootstrapInterval:
    """Return a deterministic percentile-bootstrap interval.

    Nonfinite inputs raise an error instead of being converted into penalties.
    """

    finite_values = _require_finite_values(values, minimum=1)
    _validate_confidence(confidence)
    _validate_replicates(replicates)
    point_estimate = float(statistic(finite_values))
    if not math.isfinite(point_estimate):
        raise ValueError("statistic must return a finite value")

    rng = random.Random(seed)
    sample_size = len(finite_values)
    distribution: list[float] = []
    for _ in range(replicates):
        sample = [rng.choice(finite_values) for _ in range(sample_size)]
        bootstrap_value = float(statistic(sample))
        if not math.isfinite(bootstrap_value):
            raise ValueError("statistic returned a nonfinite bootstrap value")
        distribution.append(bootstrap_value)

    alpha = (1.0 - confidence) / 2.0
    distribution.sort()
    return BootstrapInterval(
        estimate=point_estimate,
        lower=_quantile_sorted(distribution, alpha),
        upper=_quantile_sorted(distribution, 1.0 - alpha),
        confidence=confidence,
        n=sample_size,
        replicates=replicates,
        seed=seed,
    )


def replicate_count_convergence(
    values: Sequence[float],
    *,
    counts: Sequence[int],
    confidence: float = 0.95,
) -> tuple[ConvergencePoint, ...]:
    """Summarize paired-estimate stability over deterministic value prefixes."""

    finite_values = _require_finite_values(values, minimum=2)
    if not counts:
        raise ValueError("counts must not be empty")
    normalized_counts = [int(count) for count in counts]
    if any(count < 2 for count in normalized_counts):
        raise ValueError("each replicate count must be at least 2")
    if normalized_counts != sorted(set(normalized_counts)):
        raise ValueError("counts must be unique and strictly increasing")
    if normalized_counts[-1] > len(finite_values):
        raise ValueError("replicate count exceeds available values")

    diagnostics: list[ConvergencePoint] = []
    previous_estimate: float | None = None
    previous_half_width: float | None = None
    for count in normalized_counts:
        interval = t_paired_confidence_interval(
            finite_values[:count], confidence=confidence
        )
        estimate_change = (
            None
            if previous_estimate is None
            else interval.estimate - previous_estimate
        )
        if previous_half_width is None:
            width_ratio = None
        elif previous_half_width == 0.0:
            width_ratio = 1.0 if interval.half_width == 0.0 else math.inf
        else:
            width_ratio = interval.half_width / previous_half_width
        diagnostics.append(
            ConvergencePoint(
                count=count,
                estimate=interval.estimate,
                lower=interval.lower,
                upper=interval.upper,
                half_width=interval.half_width,
                estimate_change_from_previous=estimate_change,
                half_width_ratio_to_previous=width_ratio,
            )
        )
        previous_estimate = interval.estimate
        previous_half_width = interval.half_width
    return tuple(diagnostics)


def estimate_piecewise_linear_zero_crossing(
    points: Sequence[tuple[float, float]],
) -> ZeroCrossingEstimate:
    """Interpolate a zero only inside an observed sign-change bracket."""

    if len(points) < 2:
        raise ValueError("at least two points are required")
    normalized: list[tuple[float, float]] = []
    for index, (x_value, y_value) in enumerate(points):
        x_float = _as_finite_float(x_value)
        y_float = _as_finite_float(y_value)
        if x_float is None or y_float is None:
            raise ValueError(f"point {index} must contain finite values")
        normalized.append((x_float, y_float))
    normalized.sort(key=lambda item: item[0])
    if len({item[0] for item in normalized}) != len(normalized):
        raise ValueError("x values must be unique")

    exact = [item for item in normalized if item[1] == 0.0]
    if len(exact) == 1:
        x_value, y_value = exact[0]
        return ZeroCrossingEstimate(
            "exact", x_value, x_value, x_value, y_value, y_value, 1
        )
    if len(exact) > 1:
        return ZeroCrossingEstimate(
            "multiple_exact", None, None, None, None, None, len(exact)
        )

    brackets: list[tuple[float, float, float, float]] = []
    for (left_x, left_y), (right_x, right_y) in zip(
        normalized, normalized[1:]
    ):
        if left_y * right_y < 0.0:
            brackets.append((left_x, left_y, right_x, right_y))

    if not brackets:
        return ZeroCrossingEstimate(
            "unbracketed", None, None, None, None, None, 0
        )
    if len(brackets) > 1:
        return ZeroCrossingEstimate(
            "multiple_brackets", None, None, None, None, None, len(brackets)
        )

    left_x, left_y, right_x, right_y = brackets[0]
    crossing = left_x + (-left_y) * (right_x - left_x) / (right_y - left_y)
    return ZeroCrossingEstimate(
        status="bracketed",
        crossing=crossing,
        lower_x=left_x,
        upper_x=right_x,
        lower_y=left_y,
        upper_y=right_y,
        bracket_count=1,
    )


def joint_seed_zero_crossing_bootstrap(
    outcomes: Mapping[Hashable, Mapping[float, object]],
    *,
    confidence: float = 0.95,
    replicates: int = 10_000,
    seed: int = 20260721,
) -> JointSeedCrossingInterval:
    """Bootstrap zero crossing while keeping each seed's response curve joint.

    Only seeds containing finite outcomes at every observed x value contribute.
    Resampling whole seed trajectories preserves common-random-number dependence
    across multiplier levels.
    """

    if not outcomes:
        raise ValueError("outcomes must not be empty")
    _validate_confidence(confidence)
    _validate_replicates(replicates)
    x_values: set[float] = set()
    for curve in outcomes.values():
        for raw_x in curve:
            x_value = _as_finite_float(raw_x)
            if x_value is None:
                raise ValueError("curve x values must be finite")
            x_values.add(x_value)
    grid = tuple(sorted(x_values))
    if len(grid) < 2:
        raise ValueError("at least two multiplier values are required")

    complete: dict[Hashable, tuple[float, ...]] = {}
    excluded: list[Hashable] = []
    for arrival_seed in sorted(outcomes, key=_stable_key):
        curve = outcomes[arrival_seed]
        normalized: dict[float, object] = {}
        for raw_x, value in curve.items():
            x_value = _as_finite_float(raw_x)
            if x_value is not None:
                normalized[x_value] = value
        values = tuple(_as_finite_float(normalized.get(x_value)) for x_value in grid)
        if any(value is None for value in values):
            excluded.append(arrival_seed)
            continue
        complete[arrival_seed] = tuple(float(value) for value in values)
    if not complete:
        raise ValueError("no seed has a complete finite response curve")

    seed_keys = tuple(sorted(complete, key=_stable_key))
    point_values = [
        statistics.fmean(complete[arrival_seed][index] for arrival_seed in seed_keys)
        for index in range(len(grid))
    ]
    point_crossing = estimate_piecewise_linear_zero_crossing(
        tuple(zip(grid, point_values, strict=True))
    )
    if point_crossing.crossing is None:
        raise ValueError("mean response curve has no unique observed zero crossing")

    rng = random.Random(seed)
    distribution: list[float] = []
    for _ in range(replicates):
        sampled = [rng.choice(seed_keys) for _ in range(len(seed_keys))]
        sampled_values = [
            statistics.fmean(complete[item][index] for item in sampled)
            for index in range(len(grid))
        ]
        crossing = estimate_piecewise_linear_zero_crossing(
            tuple(zip(grid, sampled_values, strict=True))
        )
        if crossing.crossing is not None:
            distribution.append(crossing.crossing)
    if not distribution:
        raise ValueError("no bootstrap replicate has a unique observed zero crossing")
    distribution.sort()
    alpha = (1.0 - confidence) / 2.0
    return JointSeedCrossingInterval(
        estimate=point_crossing.crossing,
        lower=_quantile_sorted(distribution, alpha),
        upper=_quantile_sorted(distribution, 1.0 - alpha),
        confidence=confidence,
        complete_seed_count=len(seed_keys),
        excluded_seeds=tuple(excluded),
        replicates=replicates,
        successful_replicates=len(distribution),
        seed=seed,
    )


def hierarchical_bootstrap_ci(
    outcomes: Mapping[Hashable, Mapping[Hashable, object]],
    *,
    confidence: float = 0.95,
    replicates: int = 10_000,
    seed: int = 20260721,
) -> HierarchicalBootstrapInterval:
    """Bootstrap threat draws outside and arrival seeds inside each draw.

    Each threat draw has equal weight in the estimand.  Nonfinite arrival
    outcomes and threat draws with no finite outcomes are returned explicitly.
    """

    if not outcomes:
        raise ValueError("outcomes must not be empty")
    _validate_confidence(confidence)
    _validate_replicates(replicates)

    finite_by_threat: dict[Hashable, tuple[float, ...]] = {}
    excluded: list[ExcludedObservation] = []
    empty_threat_draws: list[Hashable] = []
    for threat_draw in sorted(outcomes, key=_stable_key):
        arrivals = outcomes[threat_draw]
        finite_values: list[float] = []
        for arrival_seed in sorted(arrivals, key=_stable_key):
            raw_value = arrivals[arrival_seed]
            finite_value = _as_finite_float(raw_value)
            if finite_value is None:
                excluded.append(
                    ExcludedObservation(threat_draw, arrival_seed, raw_value)
                )
            else:
                finite_values.append(finite_value)
        if finite_values:
            finite_by_threat[threat_draw] = tuple(finite_values)
        else:
            empty_threat_draws.append(threat_draw)

    if not finite_by_threat:
        raise ValueError("no threat draw contains a finite outcome")

    threat_keys = tuple(sorted(finite_by_threat, key=_stable_key))
    point_estimate = statistics.fmean(
        statistics.fmean(finite_by_threat[key]) for key in threat_keys
    )
    rng = random.Random(seed)
    distribution: list[float] = []
    for _ in range(replicates):
        sampled_threat_means: list[float] = []
        for _ in range(len(threat_keys)):
            sampled_threat = rng.choice(threat_keys)
            arrival_values = finite_by_threat[sampled_threat]
            sampled_arrivals = [
                rng.choice(arrival_values) for _ in range(len(arrival_values))
            ]
            sampled_threat_means.append(statistics.fmean(sampled_arrivals))
        distribution.append(statistics.fmean(sampled_threat_means))

    alpha = (1.0 - confidence) / 2.0
    distribution.sort()
    return HierarchicalBootstrapInterval(
        estimate=point_estimate,
        lower=_quantile_sorted(distribution, alpha),
        upper=_quantile_sorted(distribution, 1.0 - alpha),
        confidence=confidence,
        replicates=replicates,
        seed=seed,
        threat_draw_count=len(threat_keys),
        finite_observation_count=sum(map(len, finite_by_threat.values())),
        excluded=tuple(excluded),
        empty_threat_draws=tuple(empty_threat_draws),
    )


@dataclass(frozen=True)
class CrossedBootstrapInterval(HierarchicalBootstrapInterval):
    """Two-way (crossed) threat-draw/arrival-seed percentile-bootstrap result."""

    failed_replicates: int = 0


def crossed_two_way_bootstrap_ci(
    outcomes: Mapping[Hashable, Mapping[Hashable, object]],
    *,
    confidence: float = 0.95,
    replicates: int = 10_000,
    seed: int = 20260721,
) -> CrossedBootstrapInterval:
    """Bootstrap crossed threat draws and arrival seeds jointly.

    For designs where the same arrival-seed block is reused across every
    threat draw (crossed factors), resampling seeds independently inside each
    resampled threat destroys the cross-threat seed dependence and can
    understate uncertainty.  Each replicate therefore resamples threat draws
    with replacement AND resamples the arrival-seed index set globally once,
    then averages the resampled Cartesian submatrix; policy pairing is
    preserved cell-wise.  The point estimate matches
    ``hierarchical_bootstrap_ci`` (mean of threat means) so the two intervals
    are directly comparable.  Replicates with no finite cell are counted in
    ``failed_replicates`` and excluded from the percentile distribution.
    """

    if not outcomes:
        raise ValueError("outcomes must not be empty")
    _validate_confidence(confidence)
    _validate_replicates(replicates)

    finite_by_threat: dict[Hashable, dict[Hashable, float]] = {}
    excluded: list[ExcludedObservation] = []
    empty_threat_draws: list[Hashable] = []
    for threat_draw in sorted(outcomes, key=_stable_key):
        arrivals = outcomes[threat_draw]
        finite_values: dict[Hashable, float] = {}
        for arrival_seed in sorted(arrivals, key=_stable_key):
            raw_value = arrivals[arrival_seed]
            finite_value = _as_finite_float(raw_value)
            if finite_value is None:
                excluded.append(
                    ExcludedObservation(threat_draw, arrival_seed, raw_value)
                )
            else:
                finite_values[arrival_seed] = finite_value
        if finite_values:
            finite_by_threat[threat_draw] = finite_values
        else:
            empty_threat_draws.append(threat_draw)

    if not finite_by_threat:
        raise ValueError("no threat draw contains a finite outcome")

    threat_keys = tuple(sorted(finite_by_threat, key=_stable_key))
    seed_universe = tuple(
        sorted(
            {seed for cell in finite_by_threat.values() for seed in cell},
            key=_stable_key,
        )
    )
    point_estimate = statistics.fmean(
        statistics.fmean(cell.values()) for cell in finite_by_threat.values()
    )
    rng = random.Random(seed)
    distribution: list[float] = []
    failed_replicates = 0
    for _ in range(replicates):
        sampled_threats = [rng.choice(threat_keys) for _ in range(len(threat_keys))]
        sampled_seeds = [rng.choice(seed_universe) for _ in range(len(seed_universe))]
        threat_means: list[float] = []
        for threat_draw in sampled_threats:
            cell = finite_by_threat[threat_draw]
            draw_values = [cell[s] for s in sampled_seeds if s in cell]
            if draw_values:
                threat_means.append(statistics.fmean(draw_values))
        if threat_means:
            distribution.append(statistics.fmean(threat_means))
        else:
            failed_replicates += 1

    if not distribution:
        raise ValueError("no crossed bootstrap replicate contains a finite outcome")

    alpha = (1.0 - confidence) / 2.0
    distribution.sort()
    return CrossedBootstrapInterval(
        estimate=point_estimate,
        lower=_quantile_sorted(distribution, alpha),
        upper=_quantile_sorted(distribution, 1.0 - alpha),
        confidence=confidence,
        replicates=replicates,
        seed=seed,
        threat_draw_count=len(threat_keys),
        finite_observation_count=sum(len(cell) for cell in finite_by_threat.values()),
        excluded=tuple(excluded),
        empty_threat_draws=tuple(empty_threat_draws),
        failed_replicates=failed_replicates,
    )


def _require_finite_values(
    values: Sequence[float],
    *,
    minimum: int,
) -> tuple[float, ...]:
    normalized: list[float] = []
    for index, value in enumerate(values):
        finite_value = _as_finite_float(value)
        if finite_value is None:
            raise ValueError(f"value at index {index} is not finite")
        normalized.append(finite_value)
    if len(normalized) < minimum:
        raise ValueError(f"at least {minimum} finite values are required")
    return tuple(normalized)


def _as_finite_float(value: object) -> float | None:
    try:
        normalized = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return normalized if math.isfinite(normalized) else None


def _stable_key(value: Hashable) -> tuple[str, str]:
    return type(value).__name__, repr(value)


def _validate_confidence(confidence: float) -> None:
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be between 0 and 1")


def _validate_replicates(replicates: int) -> None:
    if (
        isinstance(replicates, bool)
        or not isinstance(replicates, int)
        or replicates < 1
    ):
        raise ValueError("replicates must be a positive integer")


def _quantile_sorted(sorted_values: Sequence[float], probability: float) -> float:
    if not sorted_values:
        raise ValueError("cannot calculate a quantile of an empty sequence")
    position = (len(sorted_values) - 1) * probability
    lower_index = math.floor(position)
    upper_index = math.ceil(position)
    if lower_index == upper_index:
        return float(sorted_values[lower_index])
    fraction = position - lower_index
    return float(
        sorted_values[lower_index]
        + fraction * (sorted_values[upper_index] - sorted_values[lower_index])
    )


def _student_t_quantile(probability: float, degrees_of_freedom: int) -> float:
    """Invert Student-t CDF by deterministic bisection."""

    if degrees_of_freedom < 1:
        raise ValueError("degrees_of_freedom must be positive")
    if not 0.0 < probability < 1.0:
        raise ValueError("probability must be between 0 and 1")
    if probability == 0.5:
        return 0.0
    if probability < 0.5:
        return -_student_t_quantile(1.0 - probability, degrees_of_freedom)

    lower = 0.0
    upper = 1.0
    while _student_t_cdf(upper, degrees_of_freedom) < probability:
        upper *= 2.0
        if upper > 1e12:
            raise ArithmeticError("could not bracket Student-t quantile")
    for _ in range(100):
        midpoint = (lower + upper) / 2.0
        if _student_t_cdf(midpoint, degrees_of_freedom) < probability:
            lower = midpoint
        else:
            upper = midpoint
    return (lower + upper) / 2.0


def _student_t_cdf(value: float, degrees_of_freedom: int) -> float:
    if value == 0.0:
        return 0.5
    x_value = degrees_of_freedom / (degrees_of_freedom + value * value)
    beta_value = _regularized_incomplete_beta(
        x_value, degrees_of_freedom / 2.0, 0.5
    )
    if value > 0.0:
        return 1.0 - beta_value / 2.0
    return beta_value / 2.0


def _regularized_incomplete_beta(x_value: float, a_value: float, b_value: float) -> float:
    """Numerically stable regularized incomplete beta from continued fraction."""

    if x_value <= 0.0:
        return 0.0
    if x_value >= 1.0:
        return 1.0
    log_term = (
        math.lgamma(a_value + b_value)
        - math.lgamma(a_value)
        - math.lgamma(b_value)
        + a_value * math.log(x_value)
        + b_value * math.log1p(-x_value)
    )
    front = math.exp(log_term)
    if x_value < (a_value + 1.0) / (a_value + b_value + 2.0):
        return front * _beta_continued_fraction(a_value, b_value, x_value) / a_value
    return 1.0 - front * _beta_continued_fraction(
        b_value, a_value, 1.0 - x_value
    ) / b_value


def _beta_continued_fraction(a_value: float, b_value: float, x_value: float) -> float:
    max_iterations = 300
    epsilon = 3e-14
    floor = 1e-300
    qab = a_value + b_value
    qap = a_value + 1.0
    qam = a_value - 1.0
    c_value = 1.0
    d_value = 1.0 - qab * x_value / qap
    if abs(d_value) < floor:
        d_value = floor
    d_value = 1.0 / d_value
    result = d_value
    for iteration in range(1, max_iterations + 1):
        doubled = 2 * iteration
        numerator = (
            iteration
            * (b_value - iteration)
            * x_value
            / ((qam + doubled) * (a_value + doubled))
        )
        d_value = 1.0 + numerator * d_value
        if abs(d_value) < floor:
            d_value = floor
        c_value = 1.0 + numerator / c_value
        if abs(c_value) < floor:
            c_value = floor
        d_value = 1.0 / d_value
        result *= d_value * c_value

        numerator = -(
            (a_value + iteration)
            * (qab + iteration)
            * x_value
            / ((a_value + doubled) * (qap + doubled))
        )
        d_value = 1.0 + numerator * d_value
        if abs(d_value) < floor:
            d_value = floor
        c_value = 1.0 + numerator / c_value
        if abs(c_value) < floor:
            c_value = floor
        d_value = 1.0 / d_value
        delta = d_value * c_value
        result *= delta
        if abs(delta - 1.0) <= epsilon:
            return result
    raise ArithmeticError("incomplete-beta continued fraction did not converge")


__all__ = [
    "BootstrapInterval",
    "ConvergencePoint",
    "CrossedBootstrapInterval",
    "ExcludedObservation",
    "HierarchicalBootstrapInterval",
    "IncompletePair",
    "IntervalEstimate",
    "JointSeedCrossingInterval",
    "PairingResult",
    "ZeroCrossingEstimate",
    "crossed_two_way_bootstrap_ci",
    "estimate_piecewise_linear_zero_crossing",
    "hierarchical_bootstrap_ci",
    "joint_seed_zero_crossing_bootstrap",
    "pair_finite_outcomes",
    "percentile_bootstrap_ci",
    "replicate_count_convergence",
    "t_paired_confidence_interval",
]
