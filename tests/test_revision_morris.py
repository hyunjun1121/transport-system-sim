"""Tests for the revision-study Morris sensitivity workflow."""

from __future__ import annotations

import math
import os
import sys
from dataclasses import replace

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.revision_morris import (
    aggregate_morris_outcomes,
    analyze_morris,
    sample_morris,
)


PROBLEM = {
    "num_vars": 2,
    "names": ["dominant", "minor"],
    "bounds": [[0.0, 1.0], [0.0, 1.0]],
}


def test_seeded_samples_and_factor_mapping_are_deterministic() -> None:
    first = sample_morris(PROBLEM, N=8, num_levels=4, seed=20260722)
    second = sample_morris(PROBLEM, N=8, num_levels=4, seed=20260722)
    changed_seed = sample_morris(PROBLEM, N=8, num_levels=4, seed=20260723)

    assert np.array_equal(first.matrix, second.matrix)
    assert first.sample_ids == second.sample_ids
    assert first.changed_factors == second.changed_factors
    assert not np.array_equal(first.matrix, changed_seed.matrix)
    assert first.sample_ids == tuple(f"morris_{index:06d}" for index in range(24))

    rows = first.rows()
    assert len(rows) == 8 * (len(PROBLEM["names"]) + 1)
    for index, row in enumerate(rows):
        assert row["sample_id"] == first.sample_ids[index]
        assert row["trajectory_id"] == index // 3
        assert row["step_id"] == index % 3
        if row["step_id"] == 0:
            assert row["changed_factor"] is None
        else:
            previous = rows[index - 1]
            changed = [
                name
                for name in PROBLEM["names"]
                if not math.isclose(row[name], previous[name], abs_tol=1e-12)
            ]
            assert changed == [row["changed_factor"]]

    print("PASS: seeded Morris samples and factor mapping are deterministic")


def test_aggregation_uses_finite_repetitions_and_reports_incomplete_groups() -> None:
    design = sample_morris(PROBLEM, N=4, num_levels=4, seed=20260722)
    rows: list[dict[str, object]] = []
    for sample in design.rows():
        for arrival_seed in (3101, 3102):
            rows.append(
                {
                    **sample,
                    "policy_id": "complete",
                    "arrival_seed": arrival_seed,
                    "outcome": 10.0 * sample["dominant"] + sample["minor"],
                }
            )

    first_sample = design.rows()[0]
    rows.extend(
        [
            {
                **sample,
                "policy_id": "incomplete",
                "arrival_seed": 3101,
                "outcome": 10.0 * sample["dominant"] + sample["minor"],
            }
            for sample in design.rows()
        ]
    )
    rows.append(
        {
            **first_sample,
            "policy_id": "incomplete",
            "arrival_seed": 3102,
            "outcome": float("inf"),
        }
    )

    aggregated = aggregate_morris_outcomes(
        design,
        rows,
        policy_ids=("complete", "incomplete"),
        expected_arrival_seeds=(3101, 3102),
    )

    assert np.isfinite(aggregated["complete"].outcomes).all()
    assert aggregated["complete"].incomplete_groups == ()
    assert np.isfinite(aggregated["incomplete"].outcomes).all()
    incomplete = aggregated["incomplete"].incomplete_groups
    assert len(incomplete) == len(design.sample_ids)
    assert incomplete[0].sample_id == first_sample["sample_id"]
    assert incomplete[0].nonfinite_seeds == (3102,)
    assert incomplete[0].missing_seeds == ()
    assert incomplete[1].missing_seeds == (3102,)

    print("PASS: finite Morris repetitions aggregate and incompleteness stays explicit")


def test_aggregation_rejects_unknown_or_misaligned_samples() -> None:
    design = sample_morris(PROBLEM, N=2, num_levels=4, seed=20260722)
    base = {
        **design.rows()[0],
        "policy_id": "policy",
        "arrival_seed": 3101,
        "outcome": 1.0,
    }

    unknown = {**base, "sample_id": "morris_999999"}
    try:
        aggregate_morris_outcomes(
            design,
            [unknown],
            policy_ids=("policy",),
            expected_arrival_seeds=(3101,),
        )
    except ValueError as error:
        assert "unknown sample_id" in str(error)
    else:
        raise AssertionError("unknown sample_id was accepted")

    misaligned = {**base, "dominant": float(base["dominant"]) + 0.1}
    try:
        aggregate_morris_outcomes(
            design,
            [misaligned],
            policy_ids=("policy",),
            expected_arrival_seeds=(3101,),
        )
    except ValueError as error:
        assert "factor values do not match" in str(error)
    else:
        raise AssertionError("misaligned factor values were accepted")

    print("PASS: Morris aggregation rejects row/sample misalignment")


def test_linear_function_identifies_dominant_factor() -> None:
    design = sample_morris(PROBLEM, N=32, num_levels=4, seed=20260722)
    rows: list[dict[str, object]] = []
    for sample in design.rows():
        response = 10.0 * sample["dominant"] + sample["minor"]
        for arrival_seed in (3101, 3102, 3103):
            rows.append(
                {
                    **sample,
                    "policy_id": "synthetic",
                    "arrival_seed": arrival_seed,
                    "outcome": response + 0.001 * (arrival_seed - 3102),
                }
            )

    outcomes = aggregate_morris_outcomes(
        design,
        rows,
        policy_ids=("synthetic",),
        expected_arrival_seeds=(3101, 3102, 3103),
    )["synthetic"]
    analysis = analyze_morris(
        design,
        outcomes,
        num_resamples=200,
        seed=20260722,
    )
    effects = {effect.factor_name: effect for effect in analysis.effects}

    assert tuple(effects) == ("dominant", "minor")
    assert effects["dominant"].mu_star > 5.0 * effects["minor"].mu_star
    for effect in effects.values():
        assert math.isfinite(effect.mu)
        assert math.isfinite(effect.mu_star)
        assert math.isfinite(effect.sigma)
        assert math.isfinite(effect.mu_star_conf)

    print("PASS: genuine Morris effects rank the synthetic dominant factor first")


def test_analysis_rejects_sample_order_and_nonfinite_inputs() -> None:
    design = sample_morris(PROBLEM, N=4, num_levels=4, seed=20260722)
    rows = [
        {
            **sample,
            "policy_id": "policy",
            "arrival_seed": 3101,
            "outcome": 10.0 * sample["dominant"] + sample["minor"],
        }
        for sample in design.rows()
    ]
    outcomes = aggregate_morris_outcomes(
        design,
        rows,
        policy_ids=("policy",),
        expected_arrival_seeds=(3101,),
    )["policy"]

    shuffled = replace(outcomes, sample_ids=tuple(reversed(outcomes.sample_ids)))
    try:
        analyze_morris(design, shuffled, seed=20260722)
    except ValueError as error:
        assert "sample_id order" in str(error)
    else:
        raise AssertionError("misordered sample IDs were accepted")

    nonfinite_values = outcomes.outcomes.copy()
    nonfinite_values[0] = np.nan
    nonfinite = replace(outcomes, outcomes=nonfinite_values)
    try:
        analyze_morris(design, nonfinite, seed=20260722)
    except ValueError as error:
        assert "finite" in str(error)
    else:
        raise AssertionError("nonfinite Morris outcomes were accepted")

    print("PASS: Morris analysis rejects misordered and nonfinite inputs")


if __name__ == "__main__":
    test_seeded_samples_and_factor_mapping_are_deterministic()
    test_aggregation_uses_finite_repetitions_and_reports_incomplete_groups()
    test_aggregation_rejects_unknown_or_misaligned_samples()
    test_linear_function_identifies_dominant_factor()
    test_analysis_rejects_sample_order_and_nonfinite_inputs()
