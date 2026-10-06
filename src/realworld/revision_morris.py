"""Deterministic Morris sensitivity utilities for the paper-revision study.

The module keeps three concerns separate:

* SALib creates a genuine Morris trajectory design.
* simulator replications are reduced to one finite response per design row.
* SALib computes elementary-effect statistics only after strict alignment checks.

No function mutates the supplied problem, design matrix, or result rows.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
import math
from typing import Any

import numpy as np
from SALib.analyze.morris import analyze as salib_analyze
from SALib.sample.morris import sample as salib_sample


@dataclass(frozen=True)
class MorrisDesign:
    """Seeded SALib design plus stable row and trajectory identifiers."""

    problem: Mapping[str, Any]
    factor_names: tuple[str, ...]
    matrix: np.ndarray
    sample_ids: tuple[str, ...]
    trajectory_ids: tuple[int, ...]
    step_ids: tuple[int, ...]
    changed_factors: tuple[str | None, ...]
    trajectories: int
    num_levels: int
    seed: int

    def rows(self) -> tuple[dict[str, object], ...]:
        """Return CSV-ready rows in exact SALib matrix order."""

        rows: list[dict[str, object]] = []
        for row_index, values in enumerate(self.matrix):
            row: dict[str, object] = {
                "sample_id": self.sample_ids[row_index],
                "trajectory_id": self.trajectory_ids[row_index],
                "step_id": self.step_ids[row_index],
                "changed_factor": self.changed_factors[row_index],
            }
            row.update(
                {
                    name: float(values[factor_index])
                    for factor_index, name in enumerate(self.factor_names)
                }
            )
            rows.append(row)
        return tuple(rows)


@dataclass(frozen=True)
class IncompleteOutcomeGroup:
    """Missing or nonfinite arrival-seed replications for one design row."""

    policy_id: str
    sample_id: str
    finite_count: int
    expected_count: int
    missing_seeds: tuple[int, ...]
    nonfinite_seeds: tuple[int, ...]


@dataclass(frozen=True)
class MorrisPolicyOutcomes:
    """One arrival-seed-aggregated response per ordered Morris design row."""

    policy_id: str
    sample_ids: tuple[str, ...]
    outcomes: np.ndarray
    expected_arrival_seeds: tuple[int, ...]
    incomplete_groups: tuple[IncompleteOutcomeGroup, ...]


@dataclass(frozen=True)
class MorrisEffect:
    """Elementary-effect statistics for one named input factor."""

    factor_name: str
    mu: float
    mu_star: float
    sigma: float
    mu_star_conf: float


@dataclass(frozen=True)
class MorrisAnalysis:
    """Morris elementary-effect results for one policy response."""

    policy_id: str
    effects: tuple[MorrisEffect, ...]

    def rows(self) -> tuple[dict[str, object], ...]:
        """Return CSV-ready factor rows."""

        return tuple(
            {
                "policy_id": self.policy_id,
                "factor_name": effect.factor_name,
                "mu": effect.mu,
                "mu_star": effect.mu_star,
                "sigma": effect.sigma,
                "mu_star_conf": effect.mu_star_conf,
            }
            for effect in self.effects
        )


def sample_morris(
    problem: Mapping[str, Any],
    N: int,
    num_levels: int = 4,
    seed: int = 20260722,
) -> MorrisDesign:
    """Create a deterministic, ungrouped Morris design through SALib.

    ``N`` is the number of trajectories. Each ungrouped trajectory contains
    ``num_vars + 1`` rows. Stable ``sample_id`` values refer to individual rows,
    not whole trajectories, so simulator output can be joined without relying on
    row position alone.
    """

    normalized_problem, factor_names = _normalize_problem(problem)
    trajectories = _positive_integer(N, "N")
    levels = _positive_integer(num_levels, "num_levels")
    if levels < 2:
        raise ValueError("num_levels must be at least 2")
    normalized_seed = _integer(seed, "seed")

    sampled = np.asarray(
        salib_sample(
            normalized_problem,
            N=trajectories,
            num_levels=levels,
            seed=normalized_seed,
        ),
        dtype=float,
    )
    expected_rows = trajectories * (len(factor_names) + 1)
    expected_shape = (expected_rows, len(factor_names))
    if sampled.shape != expected_shape:
        raise ValueError(
            "SALib Morris sample shape does not match the ungrouped design: "
            f"expected {expected_shape}, got {sampled.shape}"
        )
    if not np.isfinite(sampled).all():
        raise ValueError("SALib Morris design contains nonfinite factor values")

    sample_ids = tuple(f"morris_{index:06d}" for index in range(expected_rows))
    trajectory_ids: list[int] = []
    step_ids: list[int] = []
    changed_factors: list[str | None] = []
    rows_per_trajectory = len(factor_names) + 1
    for row_index in range(expected_rows):
        step_id = row_index % rows_per_trajectory
        trajectory_ids.append(row_index // rows_per_trajectory)
        step_ids.append(step_id)
        if step_id == 0:
            changed_factors.append(None)
            continue
        changed_indices = np.flatnonzero(
            ~np.isclose(
                sampled[row_index],
                sampled[row_index - 1],
                rtol=1e-12,
                atol=1e-12,
            )
        )
        if len(changed_indices) != 1:
            raise ValueError(
                "SALib Morris trajectory step must change exactly one factor; "
                f"row {row_index} changed {len(changed_indices)}"
            )
        changed_factors.append(factor_names[int(changed_indices[0])])

    matrix = sampled.copy()
    matrix.setflags(write=False)
    return MorrisDesign(
        problem=normalized_problem,
        factor_names=factor_names,
        matrix=matrix,
        sample_ids=sample_ids,
        trajectory_ids=tuple(trajectory_ids),
        step_ids=tuple(step_ids),
        changed_factors=tuple(changed_factors),
        trajectories=trajectories,
        num_levels=levels,
        seed=normalized_seed,
    )


def aggregate_morris_outcomes(
    design: MorrisDesign,
    rows: Iterable[Mapping[str, object]],
    *,
    policy_ids: Sequence[str] | None = None,
    expected_arrival_seeds: Sequence[int] | None = None,
    outcome_key: str = "outcome",
    policy_key: str = "policy_id",
    sample_key: str = "sample_id",
    arrival_seed_key: str = "arrival_seed",
) -> dict[str, MorrisPolicyOutcomes]:
    """Average finite arrival-seed responses for each policy and design row.

    Missing and nonfinite replications are excluded from the mean and retained in
    ``incomplete_groups``. A group with no finite response receives ``NaN``; the
    analysis guard rejects such a vector. Duplicate replications, unknown sample
    IDs, unexpected seeds, and factor/sample mismatches fail immediately.
    """

    materialized_rows = list(rows)
    expected_samples = {
        sample_id: row_index
        for row_index, sample_id in enumerate(design.sample_ids)
    }
    selected_policies = _normalize_policy_ids(
        policy_ids,
        materialized_rows,
        policy_key,
    )
    selected_policy_set = set(selected_policies)
    arrival_seeds = _normalize_arrival_seeds(
        expected_arrival_seeds,
        materialized_rows,
        arrival_seed_key,
    )
    arrival_seed_set = set(arrival_seeds)
    expected_factor_rows = design.rows()
    responses: dict[tuple[str, str, int], float] = {}

    for row_number, row in enumerate(materialized_rows, start=1):
        if not isinstance(row, Mapping):
            raise TypeError(f"Morris result row {row_number} must be a mapping")
        policy_id = _required_string(row, policy_key, row_number)
        if policy_id not in selected_policy_set:
            raise ValueError(
                f"Morris result row {row_number} has unexpected policy_id {policy_id!r}"
            )
        sample_id = _required_string(row, sample_key, row_number)
        if sample_id not in expected_samples:
            raise ValueError(
                f"Morris result row {row_number} has unknown sample_id {sample_id!r}"
            )
        arrival_seed = _integer(
            _required_value(row, arrival_seed_key, row_number),
            f"row {row_number} {arrival_seed_key}",
        )
        if arrival_seed not in arrival_seed_set:
            raise ValueError(
                f"Morris result row {row_number} has unexpected arrival_seed "
                f"{arrival_seed}"
            )

        sample_index = expected_samples[sample_id]
        expected_factor_row = expected_factor_rows[sample_index]
        for factor_name in design.factor_names:
            actual_value = _finite_float(
                _required_value(row, factor_name, row_number),
                f"row {row_number} factor {factor_name}",
            )
            expected_value = float(expected_factor_row[factor_name])
            if not math.isclose(
                actual_value,
                expected_value,
                rel_tol=1e-10,
                abs_tol=1e-12,
            ):
                raise ValueError(
                    f"Morris result row {row_number} factor values do not match "
                    f"sample_id {sample_id!r}: {factor_name} expected "
                    f"{expected_value}, got {actual_value}"
                )

        outcome = _float(
            _required_value(row, outcome_key, row_number),
            f"row {row_number} {outcome_key}",
        )
        response_key = (policy_id, sample_id, arrival_seed)
        if response_key in responses:
            raise ValueError(
                "duplicate Morris policy/sample/arrival_seed row: "
                f"{response_key!r}"
            )
        responses[response_key] = outcome

    aggregated: dict[str, MorrisPolicyOutcomes] = {}
    for policy_id in selected_policies:
        values: list[float] = []
        incomplete_groups: list[IncompleteOutcomeGroup] = []
        for sample_id in design.sample_ids:
            finite_values: list[float] = []
            missing_seeds: list[int] = []
            nonfinite_seeds: list[int] = []
            for arrival_seed in arrival_seeds:
                response_key = (policy_id, sample_id, arrival_seed)
                if response_key not in responses:
                    missing_seeds.append(arrival_seed)
                    continue
                outcome = responses[response_key]
                if math.isfinite(outcome):
                    finite_values.append(outcome)
                else:
                    nonfinite_seeds.append(arrival_seed)

            values.append(
                float(np.mean(finite_values)) if finite_values else float("nan")
            )
            if missing_seeds or nonfinite_seeds:
                incomplete_groups.append(
                    IncompleteOutcomeGroup(
                        policy_id=policy_id,
                        sample_id=sample_id,
                        finite_count=len(finite_values),
                        expected_count=len(arrival_seeds),
                        missing_seeds=tuple(missing_seeds),
                        nonfinite_seeds=tuple(nonfinite_seeds),
                    )
                )

        outcome_array = np.asarray(values, dtype=float)
        outcome_array.setflags(write=False)
        aggregated[policy_id] = MorrisPolicyOutcomes(
            policy_id=policy_id,
            sample_ids=design.sample_ids,
            outcomes=outcome_array,
            expected_arrival_seeds=arrival_seeds,
            incomplete_groups=tuple(incomplete_groups),
        )
    return aggregated


def analyze_morris(
    design: MorrisDesign,
    outcomes: MorrisPolicyOutcomes,
    *,
    num_resamples: int = 1000,
    conf_level: float = 0.95,
    seed: int = 20260722,
) -> MorrisAnalysis:
    """Compute genuine SALib elementary effects for aligned finite outcomes."""

    if outcomes.sample_ids != design.sample_ids:
        raise ValueError("Morris outcome sample_id order does not match the design")
    outcome_values = np.asarray(outcomes.outcomes, dtype=float)
    if outcome_values.shape != (len(design.sample_ids),):
        raise ValueError(
            "Morris outcome vector length does not match the design matrix"
        )
    if design.matrix.shape[0] != len(design.sample_ids):
        raise ValueError("Morris design matrix and sample_id rows are misaligned")
    if not np.isfinite(design.matrix).all():
        raise ValueError("Morris analysis requires finite design inputs")
    if not np.isfinite(outcome_values).all():
        raise ValueError("Morris analysis requires finite outcome inputs")

    resamples = _positive_integer(num_resamples, "num_resamples")
    confidence = _float(conf_level, "conf_level")
    if not 0.0 < confidence < 1.0:
        raise ValueError("conf_level must be between 0 and 1")
    normalized_seed = _integer(seed, "seed")
    result = salib_analyze(
        dict(design.problem),
        design.matrix,
        outcome_values,
        num_resamples=resamples,
        conf_level=confidence,
        scaled=False,
        print_to_console=False,
        num_levels=design.num_levels,
        seed=normalized_seed,
    )

    result_names = tuple(str(name) for name in result["names"])
    if result_names != design.factor_names:
        raise ValueError(
            "SALib Morris result factor order does not match the design problem"
        )
    mu = _effect_values(result, "mu", len(result_names))
    mu_star = _effect_values(result, "mu_star", len(result_names))
    sigma = _effect_values(result, "sigma", len(result_names))
    mu_star_conf = _effect_values(result, "mu_star_conf", len(result_names))
    effects = tuple(
        MorrisEffect(
            factor_name=factor_name,
            mu=float(mu[index]),
            mu_star=float(mu_star[index]),
            sigma=float(sigma[index]),
            mu_star_conf=float(mu_star_conf[index]),
        )
        for index, factor_name in enumerate(result_names)
    )
    return MorrisAnalysis(policy_id=outcomes.policy_id, effects=effects)


def _normalize_problem(
    problem: Mapping[str, Any],
) -> tuple[dict[str, Any], tuple[str, ...]]:
    if not isinstance(problem, Mapping):
        raise TypeError("Morris problem must be a mapping")
    if problem.get("groups") is not None:
        raise ValueError("grouped Morris problems are not supported by row factor mapping")
    try:
        names_value = problem["names"]
        bounds_value = problem["bounds"]
        num_vars_value = problem["num_vars"]
    except KeyError as error:
        raise ValueError(f"Morris problem is missing {error.args[0]!r}") from error
    if isinstance(names_value, (str, bytes)) or not isinstance(names_value, Sequence):
        raise ValueError("Morris problem names must be a sequence")
    factor_names = tuple(str(name) for name in names_value)
    if not factor_names or any(not name.strip() for name in factor_names):
        raise ValueError("Morris problem factor names must be nonempty")
    if len(set(factor_names)) != len(factor_names):
        raise ValueError("Morris problem factor names must be unique")
    num_vars = _positive_integer(num_vars_value, "problem num_vars")
    if num_vars != len(factor_names):
        raise ValueError("Morris problem num_vars does not match names")
    bounds = np.asarray(bounds_value, dtype=float)
    if bounds.shape != (num_vars, 2):
        raise ValueError("Morris problem bounds must have shape (num_vars, 2)")
    if not np.isfinite(bounds).all():
        raise ValueError("Morris problem bounds must be finite")
    if np.any(bounds[:, 0] >= bounds[:, 1]):
        raise ValueError("each Morris problem lower bound must be below its upper bound")

    normalized = deepcopy(dict(problem))
    normalized["num_vars"] = num_vars
    normalized["names"] = list(factor_names)
    normalized["bounds"] = bounds.tolist()
    return normalized, factor_names


def _normalize_policy_ids(
    policy_ids: Sequence[str] | None,
    rows: Sequence[Mapping[str, object]],
    policy_key: str,
) -> tuple[str, ...]:
    if policy_ids is None:
        inferred = {
            _required_string(row, policy_key, row_number)
            for row_number, row in enumerate(rows, start=1)
        }
        selected = tuple(sorted(inferred))
    else:
        if isinstance(policy_ids, (str, bytes)):
            raise ValueError("policy_ids must be a sequence of identifiers")
        selected = tuple(str(policy_id) for policy_id in policy_ids)
    if not selected or any(not policy_id.strip() for policy_id in selected):
        raise ValueError("policy_ids must contain nonempty identifiers")
    if len(set(selected)) != len(selected):
        raise ValueError("policy_ids must be unique")
    return selected


def _normalize_arrival_seeds(
    expected_arrival_seeds: Sequence[int] | None,
    rows: Sequence[Mapping[str, object]],
    arrival_seed_key: str,
) -> tuple[int, ...]:
    if expected_arrival_seeds is None:
        selected = tuple(
            sorted(
                {
                    _integer(
                        _required_value(row, arrival_seed_key, row_number),
                        f"row {row_number} {arrival_seed_key}",
                    )
                    for row_number, row in enumerate(rows, start=1)
                }
            )
        )
    else:
        if isinstance(expected_arrival_seeds, (str, bytes)):
            raise ValueError("expected_arrival_seeds must be a sequence")
        selected = tuple(
            _integer(seed, "expected arrival seed")
            for seed in expected_arrival_seeds
        )
    if not selected:
        raise ValueError("expected_arrival_seeds must not be empty")
    if len(set(selected)) != len(selected):
        raise ValueError("expected_arrival_seeds must be unique")
    return selected


def _effect_values(
    result: Mapping[str, object],
    key: str,
    expected_length: int,
) -> np.ndarray:
    values = np.ma.asarray(result[key], dtype=float)
    if values.shape != (expected_length,):
        raise ValueError(f"SALib Morris result {key!r} has unexpected shape")
    if np.ma.getmaskarray(values).any():
        raise ValueError(f"SALib Morris result {key!r} contains masked values")
    return np.asarray(values, dtype=float)


def _required_value(
    row: Mapping[str, object],
    key: str,
    row_number: int,
) -> object:
    if key not in row:
        raise ValueError(f"Morris result row {row_number} is missing {key!r}")
    return row[key]


def _required_string(
    row: Mapping[str, object],
    key: str,
    row_number: int,
) -> str:
    value = _required_value(row, key, row_number)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"Morris result row {row_number} {key!r} must be a nonempty string"
        )
    return value


def _positive_integer(value: object, label: str) -> int:
    integer = _integer(value, label)
    if integer <= 0:
        raise ValueError(f"{label} must be positive")
    return integer


def _integer(value: object, label: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be an integer")
    try:
        integer = int(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{label} must be an integer") from error
    try:
        numeric = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{label} must be an integer") from error
    if not math.isfinite(numeric) or numeric != integer:
        raise ValueError(f"{label} must be an integer")
    return integer


def _finite_float(value: object, label: str) -> float:
    number = _float(value, label)
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite")
    return number


def _float(value: object, label: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be numeric")
    try:
        return float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{label} must be numeric") from error
