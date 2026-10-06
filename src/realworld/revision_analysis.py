"""Pure row-level postprocessing for paper-revision experiments.

Outcome comparisons are lexicographic: maximize completion rate first, then
minimize makespan only when completion rates match.  Failed or missing runs
remain explicit and never become arbitrary time penalties.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import math
from typing import Callable, Hashable, Mapping, Sequence

from .revision_statistics import (
    BootstrapInterval,
    HierarchicalBootstrapInterval,
    IntervalEstimate,
    JointSeedCrossingInterval,
    ZeroCrossingEstimate,
    estimate_piecewise_linear_zero_crossing,
    hierarchical_bootstrap_ci,
    joint_seed_zero_crossing_bootstrap,
    pair_finite_outcomes,
    percentile_bootstrap_ci,
    replicate_count_convergence,
    t_paired_confidence_interval,
)


DEFAULT_METRIC_FIELDS = frozenset(
    {
        "completion_rate",
        "censored_count",
        "penalized_makespan",
        "makespan",
        "makespan_min",
        "road_vehicle_service_minutes",
        "train_service_minutes",
        "total_service_minutes",
        "passenger_travel_minutes",
        "passengers_per_total_service_minute",
        "first_arrival_time",
        "median_arrival_time",
        "p80_arrival_time",
        "p95_arrival_time",
        "empty_return_trips",
        "empty_return_minutes",
        "vehicle_cycles",
        "road_vehicle_cycles",
        "road_deployed_seat_capacity",
        "road_boarded_passengers",
        "road_mean_vehicle_load_factor",
        "rail_deployed_seat_capacity",
        "rail_boarded_passengers",
        "rail_mean_load_factor",
        "mean_vehicle_load_factor",
        "assembly_wait_minutes",
        "transfer_wait_minutes",
        "rail_wait_minutes",
        "notes",
        "claim_scope",
        "mode",
        "seed_stream_id",
        "run_key",
    }
)


@dataclass(frozen=True)
class OutcomeComparison:
    """Lexicographic comparison of left and right outcomes."""

    winner: str
    reason: str


@dataclass(frozen=True)
class PolicyRowPair:
    """Rows for two policies under one exact configuration replication."""

    configuration: tuple[tuple[str, Hashable], ...]
    left: Mapping[str, object] | None
    right: Mapping[str, object] | None
    comparison: OutcomeComparison | None


@dataclass(frozen=True)
class PairedMakespanSummary:
    """Finite left-minus-right makespan inference for one configuration."""

    configuration: tuple[tuple[str, Hashable], ...]
    total_pair_count: int
    finite_pair_count: int
    mean_left_makespan: float | None
    mean_right_makespan: float | None
    mean_delta: float | None
    t_interval: IntervalEstimate | None
    bootstrap_interval: BootstrapInterval | None
    incomplete_reason_counts: tuple[tuple[str, int], ...]
    completion_pair_count: int
    mean_left_completion_rate: float | None
    mean_right_completion_rate: float | None
    mean_completion_rate_delta: float | None
    completion_winner: str
    completion_t_interval: IntervalEstimate | None
    completion_bootstrap_interval: BootstrapInterval | None
    completion_statistical_resolution: str
    completion_incomplete_reason_counts: tuple[tuple[str, int], ...]
    overall_winner: str
    overall_winner_basis: str


@dataclass(frozen=True)
class BreakEvenSeries:
    """Observed paired-mean curve and its bracketed zero crossing."""

    configuration: tuple[tuple[str, Hashable], ...]
    multiplier_field: str
    paired_mean_points: tuple[tuple[float, float], ...]
    crossing: ZeroCrossingEstimate
    joint_seed_bootstrap: JointSeedCrossingInterval | None


@dataclass(frozen=True)
class PairedConvergenceRow:
    """Paired estimate stability for one deterministic CRN seed prefix."""

    configuration: tuple[tuple[str, Hashable], ...]
    count: int
    seed_max: Hashable
    estimate: float
    lower: float
    upper: float
    half_width: float
    estimate_change_from_previous: float | None
    half_width_ratio_to_previous: float | None


@dataclass(frozen=True)
class HierarchicalDeltaSummary:
    """Threat-outer, arrival-inner bootstrap of paired makespan deltas."""

    configuration: tuple[tuple[str, Hashable], ...]
    total_pair_count: int
    finite_pair_count: int
    interval: HierarchicalBootstrapInterval | None
    incomplete_reason_counts: tuple[tuple[str, int], ...]
    completion_pair_count: int
    completion_delta_interval: HierarchicalBootstrapInterval | None
    completion_incomplete_reason_counts: tuple[tuple[str, int], ...]
    left_positive_completion_proxy_interval: HierarchicalBootstrapInterval | None
    right_positive_completion_proxy_interval: HierarchicalBootstrapInterval | None
    left_full_completion_proxy_interval: HierarchicalBootstrapInterval | None
    right_full_completion_proxy_interval: HierarchicalBootstrapInterval | None
    probability_proxy_scope: str


@dataclass(frozen=True)
class GraphScopeStabilityRow:
    """One reduced graph's agreement with full-graph outcomes."""

    graph_scope: Hashable
    normal_time_match_count: int
    normal_time_mean_absolute_error: float | None
    normal_time_mean_absolute_percentage_error: float | None
    connectivity_match_count: int
    connectivity_agreement: float | None
    policy_ranking_match_count: int
    policy_ranking_agreement: float | None


def compare_outcomes(
    left_completion_rate: object,
    left_makespan: object,
    right_completion_rate: object,
    right_makespan: object,
    *,
    tolerance: float = 1e-12,
) -> OutcomeComparison:
    """Compare outcomes by completion first and finite makespan second."""

    left_completion = _completion_rate(left_completion_rate)
    right_completion = _completion_rate(right_completion_rate)
    if left_completion > right_completion + tolerance:
        return OutcomeComparison("left", "completion_rate")
    if right_completion > left_completion + tolerance:
        return OutcomeComparison("right", "completion_rate")

    left_time = _finite_float(left_makespan)
    right_time = _finite_float(right_makespan)
    if left_time is not None and right_time is not None:
        if left_time < right_time - tolerance:
            return OutcomeComparison("left", "makespan")
        if right_time < left_time - tolerance:
            return OutcomeComparison("right", "makespan")
        return OutcomeComparison("tie", "equal")
    if left_time is not None:
        return OutcomeComparison("left", "finite_makespan")
    if right_time is not None:
        return OutcomeComparison("right", "finite_makespan")
    return OutcomeComparison("tie", "makespan_unavailable")


def pair_policy_rows(
    rows: Sequence[Mapping[str, object]],
    *,
    left_policy: str = "bus_only",
    right_policy: str = "static_multimodal",
    policy_field: str = "policy_id",
    completion_field: str = "completion_rate",
    makespan_field: str = "makespan",
    metric_fields: Sequence[str] = (),
) -> tuple[PolicyRowPair, ...]:
    """Pair policy rows by every non-policy, non-result configuration field."""

    selected = _selected_rows(rows, policy_field, left_policy, right_policy)
    if not selected:
        return ()
    excluded = set(DEFAULT_METRIC_FIELDS) | set(metric_fields) | {policy_field}
    configuration_fields = _configuration_fields(selected, excluded)
    grouped: dict[
        tuple[tuple[str, Hashable], ...], dict[str, Mapping[str, object]]
    ] = {}
    for row in selected:
        policy = str(row[policy_field])
        configuration = _row_configuration(row, configuration_fields)
        policies = grouped.setdefault(configuration, {})
        if policy in policies:
            raise ValueError(
                f"duplicate {policy!r} row for configuration {configuration!r}"
            )
        policies[policy] = dict(row)

    pairs: list[PolicyRowPair] = []
    for configuration in sorted(grouped, key=_stable_configuration_key):
        policies = grouped[configuration]
        left = policies.get(left_policy)
        right = policies.get(right_policy)
        comparison = None
        if left is not None and right is not None:
            comparison = compare_outcomes(
                left.get(completion_field),
                left.get(makespan_field),
                right.get(completion_field),
                right.get(makespan_field),
            )
        pairs.append(PolicyRowPair(configuration, left, right, comparison))
    return tuple(pairs)


def summarize_paired_makespan(
    rows: Sequence[Mapping[str, object]],
    *,
    left_policy: str = "bus_only",
    right_policy: str = "static_multimodal",
    policy_field: str = "policy_id",
    seed_field: str = "arrival_seed",
    completion_field: str = "completion_rate",
    makespan_field: str = "makespan",
    metric_fields: Sequence[str] = (),
    confidence: float = 0.95,
    bootstrap_replicates: int = 10_000,
    bootstrap_seed: int = 20260721,
) -> tuple[PairedMakespanSummary, ...]:
    """Summarize seed-paired finite deltas, retaining every exclusion reason."""

    pairs = pair_policy_rows(
        rows,
        left_policy=left_policy,
        right_policy=right_policy,
        policy_field=policy_field,
        completion_field=completion_field,
        makespan_field=makespan_field,
        metric_fields=metric_fields,
    )
    grouped = _group_pairs(pairs, excluded_fields={seed_field})
    summaries: list[PairedMakespanSummary] = []
    for configuration in sorted(grouped, key=_stable_configuration_key):
        completion = _paired_completion_summary(
            grouped[configuration], completion_field=completion_field
        )
        completion_deltas, completion_reasons = _paired_completion_deltas(
            grouped[configuration],
            seed_field=seed_field,
            completion_field=completion_field,
        )
        completion_values = tuple(completion_deltas.values())
        completion_t_interval = (
            t_paired_confidence_interval(completion_values, confidence=confidence)
            if len(completion_values) >= 2
            else None
        )
        completion_bootstrap_interval = (
            percentile_bootstrap_ci(
                completion_values,
                confidence=confidence,
                replicates=bootstrap_replicates,
                seed=bootstrap_seed,
            )
            if completion_values
            else None
        )
        deltas, total_count, reasons = _paired_deltas(
            grouped[configuration],
            seed_field=seed_field,
            completion_field=completion_field,
            makespan_field=makespan_field,
        )
        values = tuple(deltas.values())
        mean_left_makespan, mean_right_makespan = _paired_makespan_means(
            grouped[configuration],
            included_seeds=frozenset(deltas),
            seed_field=seed_field,
            makespan_field=makespan_field,
        )
        t_interval = (
            t_paired_confidence_interval(values, confidence=confidence)
            if len(values) >= 2
            else None
        )
        bootstrap_interval = (
            percentile_bootstrap_ci(
                values,
                confidence=confidence,
                replicates=bootstrap_replicates,
                seed=bootstrap_seed,
            )
            if values
            else None
        )
        completion_delta = completion[3]
        if completion_delta is None:
            completion_winner = "unavailable"
        elif completion_delta > 1e-12:
            completion_winner = "left"
        elif completion_delta < -1e-12:
            completion_winner = "right"
        else:
            completion_winner = "tie"
        if completion_winner != "tie":
            overall_winner = completion_winner
            overall_basis = "completion_rate"
        elif values:
            mean_delta = sum(values) / len(values)
            if mean_delta < -1e-12:
                overall_winner = "left"
            elif mean_delta > 1e-12:
                overall_winner = "right"
            else:
                overall_winner = "tie"
            overall_basis = "finite_makespan"
        else:
            overall_winner = "unavailable"
            overall_basis = "insufficient_data"
        summaries.append(
            PairedMakespanSummary(
                configuration=configuration,
                total_pair_count=total_count,
                finite_pair_count=len(values),
                mean_left_makespan=mean_left_makespan,
                mean_right_makespan=mean_right_makespan,
                mean_delta=(sum(values) / len(values)) if values else None,
                t_interval=t_interval,
                bootstrap_interval=bootstrap_interval,
                incomplete_reason_counts=_reason_counts(reasons),
                completion_pair_count=completion[0],
                mean_left_completion_rate=completion[1],
                mean_right_completion_rate=completion[2],
                mean_completion_rate_delta=completion_delta,
                completion_winner=completion_winner,
                completion_t_interval=completion_t_interval,
                completion_bootstrap_interval=completion_bootstrap_interval,
                completion_statistical_resolution=_interval_resolution(
                    completion_t_interval,
                    completion_bootstrap_interval,
                ),
                completion_incomplete_reason_counts=_reason_counts(
                    completion_reasons
                ),
                overall_winner=overall_winner,
                overall_winner_basis=overall_basis,
            )
        )
    return tuple(summaries)


def break_even_from_rows(
    rows: Sequence[Mapping[str, object]],
    *,
    multiplier_field: str,
    left_policy: str = "bus_only",
    right_policy: str = "static_multimodal",
    policy_field: str = "policy_id",
    seed_field: str = "arrival_seed",
    completion_field: str = "completion_rate",
    makespan_field: str = "makespan",
    metric_fields: Sequence[str] = (),
    confidence: float = 0.95,
    bootstrap_replicates: int = 10_000,
    bootstrap_seed: int = 20260721,
) -> tuple[BreakEvenSeries, ...]:
    """Estimate zero crossings from observed per-multiplier paired means."""

    summaries = summarize_paired_makespan(
        rows,
        left_policy=left_policy,
        right_policy=right_policy,
        policy_field=policy_field,
        seed_field=seed_field,
        completion_field=completion_field,
        makespan_field=makespan_field,
        metric_fields=metric_fields,
        confidence=confidence,
        bootstrap_replicates=bootstrap_replicates,
        bootstrap_seed=bootstrap_seed,
    )
    grouped: dict[
        tuple[tuple[str, Hashable], ...], list[tuple[float, float]]
    ] = defaultdict(list)
    for summary in summaries:
        values = dict(summary.configuration)
        if multiplier_field not in values:
            raise ValueError(
                f"multiplier field {multiplier_field!r} is absent from configuration"
            )
        multiplier = _finite_float(values.pop(multiplier_field))
        if multiplier is None:
            raise ValueError("multiplier values must be finite")
        if summary.mean_delta is not None:
            grouped[tuple(sorted(values.items()))].append(
                (multiplier, summary.mean_delta)
            )

    joint_evidence = _joint_break_even_evidence(
        rows,
        multiplier_field=multiplier_field,
        left_policy=left_policy,
        right_policy=right_policy,
        policy_field=policy_field,
        seed_field=seed_field,
        completion_field=completion_field,
        makespan_field=makespan_field,
        metric_fields=metric_fields,
        confidence=confidence,
        bootstrap_replicates=bootstrap_replicates,
        bootstrap_seed=bootstrap_seed,
    )

    output: list[BreakEvenSeries] = []
    for configuration in sorted(grouped, key=_stable_configuration_key):
        evidence = joint_evidence.get(configuration)
        points = (
            evidence[0]
            if evidence is not None
            else tuple(sorted(grouped[configuration]))
        )
        if len({point[0] for point in points}) != len(points):
            raise ValueError("duplicate multiplier within a break-even series")
        if len(points) < 2:
            crossing = ZeroCrossingEstimate(
                "insufficient_points", None, None, None, None, None, 0
            )
        else:
            crossing = estimate_piecewise_linear_zero_crossing(points)
        output.append(
            BreakEvenSeries(
                configuration=configuration,
                multiplier_field=multiplier_field,
                paired_mean_points=points,
                crossing=crossing,
                joint_seed_bootstrap=(None if evidence is None else evidence[1]),
            )
        )
    return tuple(output)


def paired_replicate_convergence(
    rows: Sequence[Mapping[str, object]],
    *,
    counts: Sequence[int] = (5, 10, 20, 30),
    left_policy: str = "bus_only",
    right_policy: str = "static_multimodal",
    policy_field: str = "policy_id",
    seed_field: str = "arrival_seed",
    completion_field: str = "completion_rate",
    makespan_field: str = "makespan",
    metric_fields: Sequence[str] = (),
    confidence: float = 0.95,
) -> tuple[PairedConvergenceRow, ...]:
    """Report paired t-interval stability over ascending CRN seed prefixes."""

    pairs = pair_policy_rows(
        rows,
        left_policy=left_policy,
        right_policy=right_policy,
        policy_field=policy_field,
        completion_field=completion_field,
        makespan_field=makespan_field,
        metric_fields=metric_fields,
    )
    grouped = _group_pairs(pairs, excluded_fields={seed_field})
    output: list[PairedConvergenceRow] = []
    for configuration in sorted(grouped, key=_stable_configuration_key):
        deltas, _, _ = _paired_deltas(
            grouped[configuration],
            seed_field=seed_field,
            completion_field=completion_field,
            makespan_field=makespan_field,
        )
        ordered = sorted(deltas.items(), key=lambda item: _seed_order_key(item[0]))
        if len(ordered) < 2:
            continue
        requested = sorted({int(count) for count in counts if 2 <= int(count) <= len(ordered)})
        if len(ordered) not in requested:
            requested.append(len(ordered))
        points = replicate_count_convergence(
            [value for _, value in ordered],
            counts=requested,
            confidence=confidence,
        )
        for point in points:
            output.append(
                PairedConvergenceRow(
                    configuration=configuration,
                    count=point.count,
                    seed_max=ordered[point.count - 1][0],
                    estimate=point.estimate,
                    lower=point.lower,
                    upper=point.upper,
                    half_width=point.half_width,
                    estimate_change_from_previous=point.estimate_change_from_previous,
                    half_width_ratio_to_previous=point.half_width_ratio_to_previous,
                )
            )
    return tuple(output)


def hierarchical_paired_delta_summaries(
    rows: Sequence[Mapping[str, object]],
    *,
    left_policy: str = "bus_only",
    right_policy: str = "static_multimodal",
    policy_field: str = "policy_id",
    seed_field: str = "arrival_seed",
    threat_field: str = "threat_draw",
    completion_field: str = "completion_rate",
    makespan_field: str = "makespan",
    metric_fields: Sequence[str] = (),
    confidence: float = 0.95,
    bootstrap_replicates: int = 10_000,
    bootstrap_seed: int = 20260721,
    interval_factory: Callable[
        [Mapping[Hashable, Mapping[Hashable, object]]], HierarchicalBootstrapInterval
    ]
    | None = None,
) -> tuple[HierarchicalDeltaSummary, ...]:
    """Apply two-level bootstrap to finite policy deltas, not raw outcomes.

    ``interval_factory`` optionally replaces the nested threat/arrival
    resampling (e.g. with crossed two-way resampling for crossed designs);
    it must accept ``(outcomes, *, confidence, replicates, seed)`` and return
    a ``HierarchicalBootstrapInterval`` (or subclass).
    """

    pairs = pair_policy_rows(
        rows,
        left_policy=left_policy,
        right_policy=right_policy,
        policy_field=policy_field,
        completion_field=completion_field,
        makespan_field=makespan_field,
        metric_fields=metric_fields,
    )
    grouped = _group_pairs(pairs, excluded_fields={seed_field, threat_field})
    output: list[HierarchicalDeltaSummary] = []
    for configuration in sorted(grouped, key=_stable_configuration_key):
        by_threat: dict[Hashable, list[PolicyRowPair]] = defaultdict(list)
        for pair in grouped[configuration]:
            values = dict(pair.configuration)
            if threat_field not in values:
                raise ValueError(f"missing threat field {threat_field!r}")
            by_threat[values[threat_field]].append(pair)

        outcomes: dict[Hashable, dict[Hashable, object]] = {}
        completion_outcomes: dict[Hashable, dict[Hashable, object]] = {}
        left_positive_outcomes: dict[Hashable, dict[Hashable, object]] = {}
        right_positive_outcomes: dict[Hashable, dict[Hashable, object]] = {}
        left_full_outcomes: dict[Hashable, dict[Hashable, object]] = {}
        right_full_outcomes: dict[Hashable, dict[Hashable, object]] = {}
        reasons: list[str] = []
        completion_reasons: list[str] = []
        total_count = 0
        finite_count = 0
        completion_pair_count = 0
        for threat_draw in sorted(by_threat, key=_stable_value_key):
            deltas, threat_total, threat_reasons = _paired_deltas(
                by_threat[threat_draw],
                seed_field=seed_field,
                completion_field=completion_field,
                makespan_field=makespan_field,
            )
            total_count += threat_total
            finite_count += len(deltas)
            reasons.extend(threat_reasons)
            all_seeds = {
                dict(pair.configuration)[seed_field]
                for pair in by_threat[threat_draw]
            }
            outcomes[threat_draw] = {
                seed: deltas.get(seed, math.inf)
                for seed in sorted(all_seeds, key=_stable_value_key)
            }

            completion_deltas, threat_completion_reasons = (
                _paired_completion_deltas(
                    by_threat[threat_draw],
                    seed_field=seed_field,
                    completion_field=completion_field,
                )
            )
            completion_pair_count += len(completion_deltas)
            completion_reasons.extend(threat_completion_reasons)
            completion_outcomes[threat_draw] = {
                seed: completion_deltas.get(seed, math.inf)
                for seed in sorted(all_seeds, key=_stable_value_key)
            }
            left_positive: dict[Hashable, object] = {}
            right_positive: dict[Hashable, object] = {}
            left_full: dict[Hashable, object] = {}
            right_full: dict[Hashable, object] = {}
            for pair in by_threat[threat_draw]:
                seed = dict(pair.configuration)[seed_field]
                left_completion = _optional_completion_rate(
                    None
                    if pair.left is None
                    else pair.left.get(completion_field)
                )
                right_completion = _optional_completion_rate(
                    None
                    if pair.right is None
                    else pair.right.get(completion_field)
                )
                if left_completion is not None and right_completion is not None:
                    left_positive[seed] = float(left_completion > 0.0)
                    left_full[seed] = float(
                        math.isclose(left_completion, 1.0, abs_tol=1e-12)
                    )
                    right_positive[seed] = float(right_completion > 0.0)
                    right_full[seed] = float(
                        math.isclose(right_completion, 1.0, abs_tol=1e-12)
                    )
            left_positive_outcomes[threat_draw] = {
                seed: left_positive.get(seed, math.inf)
                for seed in sorted(all_seeds, key=_stable_value_key)
            }
            right_positive_outcomes[threat_draw] = {
                seed: right_positive.get(seed, math.inf)
                for seed in sorted(all_seeds, key=_stable_value_key)
            }
            left_full_outcomes[threat_draw] = {
                seed: left_full.get(seed, math.inf)
                for seed in sorted(all_seeds, key=_stable_value_key)
            }
            right_full_outcomes[threat_draw] = {
                seed: right_full.get(seed, math.inf)
                for seed in sorted(all_seeds, key=_stable_value_key)
            }

        nested_factory = interval_factory or hierarchical_bootstrap_ci
        interval = None
        if finite_count:
            interval = nested_factory(
                outcomes,
                confidence=confidence,
                replicates=bootstrap_replicates,
                seed=bootstrap_seed,
            )
        output.append(
            HierarchicalDeltaSummary(
                configuration=configuration,
                total_pair_count=total_count,
                finite_pair_count=finite_count,
                interval=interval,
                incomplete_reason_counts=_reason_counts(reasons),
                completion_pair_count=completion_pair_count,
                completion_delta_interval=_hierarchical_interval_or_none(
                    completion_outcomes,
                    confidence=confidence,
                    replicates=bootstrap_replicates,
                    seed=bootstrap_seed,
                    interval_factory=interval_factory,
                ),
                completion_incomplete_reason_counts=_reason_counts(
                    completion_reasons
                ),
                left_positive_completion_proxy_interval=(
                    _hierarchical_interval_or_none(
                        left_positive_outcomes,
                        confidence=confidence,
                        replicates=bootstrap_replicates,
                        seed=bootstrap_seed,
                        interval_factory=interval_factory,
                    )
                ),
                right_positive_completion_proxy_interval=(
                    _hierarchical_interval_or_none(
                        right_positive_outcomes,
                        confidence=confidence,
                        replicates=bootstrap_replicates,
                        seed=bootstrap_seed,
                        interval_factory=interval_factory,
                    )
                ),
                left_full_completion_proxy_interval=(
                    _hierarchical_interval_or_none(
                        left_full_outcomes,
                        confidence=confidence,
                        replicates=bootstrap_replicates,
                        seed=bootstrap_seed,
                        interval_factory=interval_factory,
                    )
                ),
                right_full_completion_proxy_interval=(
                    _hierarchical_interval_or_none(
                        right_full_outcomes,
                        confidence=confidence,
                        replicates=bootstrap_replicates,
                        seed=bootstrap_seed,
                        interval_factory=interval_factory,
                    )
                ),
                probability_proxy_scope=(
                    "empirical_result_frequency_among_paired_valid_simulation_"
                    "results_across_simulated_threat_draws_and_arrival_seeds_"
                    "not_event_probability"
                ),
            )
        )
    return tuple(output)


def graph_scope_stability_table(
    rows: Sequence[Mapping[str, object]],
    *,
    full_scope: Hashable = "full",
    normal_scenario_field: str = "scenario_id",
    normal_scenario_value: Hashable = "no_disruption",
    scope_field: str = "graph_scope",
    scope_variant_fields: Sequence[str] = ("corridor_path_count",),
    left_policy: str = "bus_only",
    right_policy: str = "static_multimodal",
    policy_field: str = "policy_id",
    completion_field: str = "completion_rate",
    makespan_field: str = "makespan",
    metric_fields: Sequence[str] = (),
) -> tuple[GraphScopeStabilityRow, ...]:
    """Compare graph scopes with full graph on time, reachability, and rank."""

    selected = _selected_rows(rows, policy_field, left_policy, right_policy)
    if not selected:
        return ()
    for row in selected:
        if scope_field not in row:
            raise ValueError(f"missing graph scope field {scope_field!r}")
    reduced_scopes = sorted(
        {row[scope_field] for row in selected if row[scope_field] != full_scope},
        key=_stable_value_key,
    )
    excluded = set(DEFAULT_METRIC_FIELDS) | set(metric_fields)
    config_fields = _configuration_fields(selected, excluded)
    match_exclusions = {scope_field, *scope_variant_fields}
    match_fields = tuple(
        field for field in config_fields if field not in match_exclusions
    )
    indexed: dict[Hashable, dict[tuple[tuple[str, Hashable], ...], Mapping[str, object]]] = defaultdict(dict)
    for row in selected:
        key = _row_configuration(row, match_fields)
        scope_rows = indexed[row[scope_field]]
        if key in scope_rows:
            raise ValueError(f"duplicate graph-scope row for {key!r}")
        scope_rows[key] = row

    full_rows = indexed.get(full_scope, {})
    if not full_rows:
        raise ValueError(f"full reference graph scope {full_scope!r} is missing")
    scopes = [*reduced_scopes, full_scope]
    policy_pairs = pair_policy_rows(
        selected,
        left_policy=left_policy,
        right_policy=right_policy,
        policy_field=policy_field,
        completion_field=completion_field,
        makespan_field=makespan_field,
        metric_fields=metric_fields,
    )
    pair_index: dict[
        Hashable, dict[tuple[tuple[str, Hashable], ...], OutcomeComparison]
    ] = defaultdict(dict)
    for pair in policy_pairs:
        values = dict(pair.configuration)
        scope = values.pop(scope_field)
        for field in scope_variant_fields:
            values.pop(field, None)
        if pair.comparison is not None:
            key = tuple(sorted(values.items()))
            if key in pair_index[scope]:
                raise ValueError(f"duplicate graph-scope policy pair for {key!r}")
            pair_index[scope][key] = pair.comparison

    output: list[GraphScopeStabilityRow] = []
    for scope in scopes:
        candidate_rows = indexed.get(scope, {})
        matched_keys = sorted(
            set(full_rows) & set(candidate_rows), key=_stable_configuration_key
        )
        absolute_errors: list[float] = []
        percentage_errors: list[float] = []
        connectivity_matches = 0
        for key in matched_keys:
            full_row = full_rows[key]
            candidate_row = candidate_rows[key]
            full_connected = _is_connected(full_row, completion_field)
            candidate_connected = _is_connected(candidate_row, completion_field)
            connectivity_matches += full_connected == candidate_connected
            if full_row.get(normal_scenario_field) != normal_scenario_value:
                continue
            full_time = _finite_float(full_row.get(makespan_field))
            candidate_time = _finite_float(candidate_row.get(makespan_field))
            if full_time is None or candidate_time is None:
                continue
            error = abs(candidate_time - full_time)
            absolute_errors.append(error)
            if full_time != 0.0:
                percentage_errors.append(error / abs(full_time))

        full_rankings = pair_index.get(full_scope, {})
        candidate_rankings = pair_index.get(scope, {})
        ranking_keys = set(full_rankings) & set(candidate_rankings)
        ranking_matches = sum(
            full_rankings[key].winner == candidate_rankings[key].winner
            for key in ranking_keys
        )
        output.append(
            GraphScopeStabilityRow(
                graph_scope=scope,
                normal_time_match_count=len(absolute_errors),
                normal_time_mean_absolute_error=(
                    sum(absolute_errors) / len(absolute_errors)
                    if absolute_errors
                    else None
                ),
                normal_time_mean_absolute_percentage_error=(
                    sum(percentage_errors) / len(percentage_errors)
                    if percentage_errors
                    else None
                ),
                connectivity_match_count=len(matched_keys),
                connectivity_agreement=(
                    connectivity_matches / len(matched_keys)
                    if matched_keys
                    else None
                ),
                policy_ranking_match_count=len(ranking_keys),
                policy_ranking_agreement=(
                    ranking_matches / len(ranking_keys)
                    if ranking_keys
                    else None
                ),
            )
        )
    return tuple(output)


def _selected_rows(
    rows: Sequence[Mapping[str, object]],
    policy_field: str,
    left_policy: str,
    right_policy: str,
) -> tuple[Mapping[str, object], ...]:
    selected: list[Mapping[str, object]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise TypeError(f"row {index} must be a mapping")
        if policy_field not in row:
            raise ValueError(f"row {index} is missing {policy_field!r}")
        if row[policy_field] in {left_policy, right_policy}:
            selected.append(row)
    return tuple(selected)


def _configuration_fields(
    rows: Sequence[Mapping[str, object]],
    excluded: set[str],
) -> tuple[str, ...]:
    fields = sorted(set().union(*(row.keys() for row in rows)) - excluded)
    for index, row in enumerate(rows):
        missing = [field for field in fields if field not in row]
        if missing:
            raise ValueError(
                f"row {index} is missing configuration fields: {', '.join(missing)}"
            )
    return tuple(fields)


def _row_configuration(
    row: Mapping[str, object],
    fields: Sequence[str],
) -> tuple[tuple[str, Hashable], ...]:
    return tuple((field, _freeze_value(row[field])) for field in fields)


def _freeze_value(value: object) -> Hashable:
    if isinstance(value, Mapping):
        return tuple(
            sorted(
                ((_freeze_value(key), _freeze_value(item)) for key, item in value.items()),
                key=repr,
            )
        )
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_value(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return tuple(sorted((_freeze_value(item) for item in value), key=repr))
    try:
        hash(value)
    except TypeError as exc:
        raise TypeError(f"configuration value is not hashable: {value!r}") from exc
    return value  # type: ignore[return-value]


def _group_pairs(
    pairs: Sequence[PolicyRowPair],
    *,
    excluded_fields: set[str],
) -> dict[tuple[tuple[str, Hashable], ...], list[PolicyRowPair]]:
    grouped: dict[
        tuple[tuple[str, Hashable], ...], list[PolicyRowPair]
    ] = defaultdict(list)
    for pair in pairs:
        values = dict(pair.configuration)
        missing = excluded_fields - set(values)
        if missing:
            raise ValueError(
                "missing grouping fields: " + ", ".join(sorted(missing))
            )
        configuration = tuple(
            (field, value)
            for field, value in pair.configuration
            if field not in excluded_fields
        )
        grouped[configuration].append(pair)
    return dict(grouped)


def _paired_deltas(
    pairs: Sequence[PolicyRowPair],
    *,
    seed_field: str,
    completion_field: str,
    makespan_field: str,
) -> tuple[dict[Hashable, float], int, list[str]]:
    left: dict[Hashable, object] = {}
    right: dict[Hashable, object] = {}
    by_seed: dict[Hashable, PolicyRowPair] = {}
    for pair in pairs:
        values = dict(pair.configuration)
        if seed_field not in values:
            raise ValueError(f"missing seed field {seed_field!r}")
        seed = values[seed_field]
        if seed in by_seed:
            raise ValueError(f"duplicate policy pair for seed {seed!r}")
        by_seed[seed] = pair
        if pair.left is not None:
            left[seed] = pair.left.get(makespan_field)
        if pair.right is not None:
            right[seed] = pair.right.get(makespan_field)

    raw = pair_finite_outcomes(left, right)
    raw_reasons = {item.seed: item.reason for item in raw.incomplete}
    raw_deltas = dict(
        zip(raw.matched_seeds, raw.differences, strict=True)
    )
    reasons: list[str] = []
    deltas: dict[Hashable, float] = {}
    for seed in sorted(by_seed, key=_stable_value_key):
        pair = by_seed[seed]
        if pair.left is None or pair.right is None:
            reasons.append(raw_reasons[seed])
            continue
        try:
            left_completion = _completion_rate(pair.left.get(completion_field))
            right_completion = _completion_rate(pair.right.get(completion_field))
        except ValueError:
            reasons.append("invalid_completion_rate")
            continue
        if not math.isclose(
            left_completion, right_completion, rel_tol=0.0, abs_tol=1e-12
        ):
            reasons.append("completion_rate_mismatch")
            continue
        if seed in raw_reasons:
            reasons.append(raw_reasons[seed])
            continue
        deltas[seed] = raw_deltas[seed]
    return deltas, raw.total_seed_count, reasons


def _paired_makespan_means(
    pairs: Sequence[PolicyRowPair],
    *,
    included_seeds: frozenset[Hashable],
    seed_field: str,
    makespan_field: str,
) -> tuple[float | None, float | None]:
    """Return policy means over exactly the finite equal-completion pairs."""

    if not included_seeds:
        return None, None
    left_values: list[float] = []
    right_values: list[float] = []
    for pair in pairs:
        seed = dict(pair.configuration).get(seed_field)
        if seed not in included_seeds:
            continue
        if pair.left is None or pair.right is None:
            raise RuntimeError("included paired makespan is missing a policy row")
        left = _finite_float(pair.left.get(makespan_field))
        right = _finite_float(pair.right.get(makespan_field))
        if left is None or right is None:
            raise RuntimeError("included paired makespan is not finite")
        left_values.append(left)
        right_values.append(right)
    if len(left_values) != len(included_seeds):
        raise RuntimeError("included paired makespan seeds are incomplete")
    return (
        sum(left_values) / len(left_values),
        sum(right_values) / len(right_values),
    )


def _paired_completion_summary(
    pairs: Sequence[PolicyRowPair],
    *,
    completion_field: str,
) -> tuple[int, float | None, float | None, float | None]:
    left_values: list[float] = []
    right_values: list[float] = []
    for pair in pairs:
        if pair.left is None or pair.right is None:
            continue
        try:
            left = _completion_rate(pair.left.get(completion_field))
            right = _completion_rate(pair.right.get(completion_field))
        except ValueError:
            continue
        left_values.append(left)
        right_values.append(right)
    if not left_values:
        return 0, None, None, None
    left_mean = sum(left_values) / len(left_values)
    right_mean = sum(right_values) / len(right_values)
    return len(left_values), left_mean, right_mean, left_mean - right_mean


def _paired_completion_deltas(
    pairs: Sequence[PolicyRowPair],
    *,
    seed_field: str,
    completion_field: str,
) -> tuple[dict[Hashable, float], list[str]]:
    """Return valid seed-paired completion deltas and explicit exclusions."""

    deltas: dict[Hashable, float] = {}
    reasons: list[str] = []
    seen: set[Hashable] = set()
    for pair in pairs:
        values = dict(pair.configuration)
        if seed_field not in values:
            raise ValueError(f"missing seed field {seed_field!r}")
        seed = values[seed_field]
        if seed in seen:
            raise ValueError(f"duplicate policy pair for seed {seed!r}")
        seen.add(seed)
        if pair.left is None:
            reasons.append("missing_left")
            continue
        if pair.right is None:
            reasons.append("missing_right")
            continue
        left = _optional_completion_rate(pair.left.get(completion_field))
        right = _optional_completion_rate(pair.right.get(completion_field))
        if left is None and right is None:
            reasons.append("invalid_completion_rate_both")
        elif left is None:
            reasons.append("invalid_completion_rate_left")
        elif right is None:
            reasons.append("invalid_completion_rate_right")
        else:
            deltas[seed] = left - right
    return deltas, reasons


def _interval_resolution(
    t_interval: IntervalEstimate | None,
    bootstrap_interval: BootstrapInterval | None,
) -> str:
    """Resolve direction only when both paired intervals agree."""

    if t_interval is None or bootstrap_interval is None:
        return "insufficient_data"
    if (
        t_interval.lower == t_interval.upper == 0.0
        and bootstrap_interval.lower == bootstrap_interval.upper == 0.0
    ):
        return "tie_resolved"
    if t_interval.lower > 0.0 and bootstrap_interval.lower > 0.0:
        return "left_advantage"
    if t_interval.upper < 0.0 and bootstrap_interval.upper < 0.0:
        return "right_advantage"
    return "not_resolved"


def _hierarchical_interval_or_none(
    outcomes: Mapping[Hashable, Mapping[Hashable, object]],
    *,
    confidence: float,
    replicates: int,
    seed: int,
    interval_factory: Callable[
        [Mapping[Hashable, Mapping[Hashable, object]]], HierarchicalBootstrapInterval
    ]
    | None = None,
) -> HierarchicalBootstrapInterval | None:
    factory = interval_factory or hierarchical_bootstrap_ci
    try:
        return factory(
            outcomes,
            confidence=confidence,
            replicates=replicates,
            seed=seed,
        )
    except ValueError as error:
        if str(error) in (
            "no threat draw contains a finite outcome",
            "no crossed bootstrap replicate contains a finite outcome",
        ):
            return None
        raise


def _joint_break_even_evidence(
    rows: Sequence[Mapping[str, object]],
    *,
    multiplier_field: str,
    left_policy: str,
    right_policy: str,
    policy_field: str,
    seed_field: str,
    completion_field: str,
    makespan_field: str,
    metric_fields: Sequence[str],
    confidence: float,
    bootstrap_replicates: int,
    bootstrap_seed: int,
) -> dict[
    tuple[tuple[str, Hashable], ...],
    tuple[tuple[tuple[float, float], ...], JointSeedCrossingInterval],
]:
    pairs = pair_policy_rows(
        rows,
        left_policy=left_policy,
        right_policy=right_policy,
        policy_field=policy_field,
        completion_field=completion_field,
        makespan_field=makespan_field,
        metric_fields=metric_fields,
    )
    grouped = _group_pairs(pairs, excluded_fields={seed_field, multiplier_field})
    output: dict[
        tuple[tuple[str, Hashable], ...],
        tuple[tuple[tuple[float, float], ...], JointSeedCrossingInterval],
    ] = {}
    for configuration, group in grouped.items():
        curves: dict[Hashable, dict[float, float]] = defaultdict(dict)
        for pair in group:
            values = dict(pair.configuration)
            seed = values[seed_field]
            multiplier = _finite_float(values[multiplier_field])
            if multiplier is None:
                continue
            if pair.left is None or pair.right is None:
                continue
            try:
                left_completion = _completion_rate(pair.left.get(completion_field))
                right_completion = _completion_rate(pair.right.get(completion_field))
            except ValueError:
                continue
            if not math.isclose(
                left_completion,
                right_completion,
                rel_tol=0.0,
                abs_tol=1e-12,
            ):
                continue
            left_time = _finite_float(pair.left.get(makespan_field))
            right_time = _finite_float(pair.right.get(makespan_field))
            if left_time is None or right_time is None:
                continue
            if multiplier in curves[seed]:
                raise ValueError("duplicate seed and multiplier in break-even series")
            curves[seed][multiplier] = left_time - right_time
        try:
            interval = joint_seed_zero_crossing_bootstrap(
                curves,
                confidence=confidence,
                replicates=bootstrap_replicates,
                seed=bootstrap_seed,
            )
        except ValueError:
            continue
        excluded = set(interval.excluded_seeds)
        complete_seeds = tuple(seed for seed in curves if seed not in excluded)
        grid = tuple(sorted({x for curve in curves.values() for x in curve}))
        points = tuple(
            (
                multiplier,
                sum(curves[seed][multiplier] for seed in complete_seeds)
                / len(complete_seeds),
            )
            for multiplier in grid
        )
        output[configuration] = (points, interval)
    return output


def _completion_rate(value: object) -> float:
    result = _finite_float(value)
    if result is None or result < 0.0 or result > 1.0:
        raise ValueError("completion rate must be finite and between zero and one")
    return result


def _optional_completion_rate(value: object) -> float | None:
    try:
        return _completion_rate(value)
    except ValueError:
        return None


def _finite_float(value: object) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return result if math.isfinite(result) else None


def _is_connected(row: Mapping[str, object], completion_field: str) -> bool:
    return _completion_rate(row.get(completion_field)) > 0.0


def _reason_counts(reasons: Sequence[str]) -> tuple[tuple[str, int], ...]:
    return tuple(sorted(Counter(reasons).items()))


def _stable_value_key(value: object) -> tuple[str, str]:
    return type(value).__name__, repr(value)


def _seed_order_key(value: object) -> tuple[str, object]:
    """Order numeric CRN seeds by value and other hashables deterministically."""

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return "0_numeric", float(value)
    return "1_other", _stable_value_key(value)


def _stable_configuration_key(
    configuration: tuple[tuple[str, Hashable], ...],
) -> tuple[tuple[str, str, str], ...]:
    return tuple(
        (field, type(value).__name__, repr(value))
        for field, value in configuration
    )


__all__ = [
    "BreakEvenSeries",
    "DEFAULT_METRIC_FIELDS",
    "GraphScopeStabilityRow",
    "HierarchicalDeltaSummary",
    "OutcomeComparison",
    "PairedConvergenceRow",
    "PairedMakespanSummary",
    "PolicyRowPair",
    "break_even_from_rows",
    "compare_outcomes",
    "graph_scope_stability_table",
    "hierarchical_paired_delta_summaries",
    "pair_policy_rows",
    "paired_replicate_convergence",
    "summarize_paired_makespan",
]
