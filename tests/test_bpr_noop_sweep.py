"""Tests for the BPR volume-delay no-op sweep (offline, fast).

The sweep's REAL-graph measurement is a committed artifact produced by running
``scripts/run_bpr_noop_sweep.py``. These unit tests verify the sweep ARITHMETIC
with a deterministic injected run_fn so they stay offline and fast: the
free-flow reference is alpha=0 (BPR term exactly 0), bpr_delay_pct is measured
relative to it, and delay is monotonic in volume.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"),
)

import run_bpr_noop_sweep as sweep  # noqa: E402


def _fake_run(G, config, scenario_type, policy, params, seed):
    """Deterministic stand-in: makespan grows linearly with alpha*volume*scale."""
    alpha = config["bpr"]["alpha"]
    volume = config["traffic"]["background_volume"]
    scale = params["s"]
    return {
        "makespan": 1000.0 + alpha * volume * scale,
        "completion_rate": 1.0,
    }


def test_compute_bpr_delay_pct_zero_and_scaled():
    assert sweep.compute_bpr_delay_pct(1000.0, 1000.0) == 0.0
    assert abs(sweep.compute_bpr_delay_pct(1000.0, 1036.0) - 3.6) <= 1e-9
    # guard against divide-by-zero
    assert sweep.compute_bpr_delay_pct(0.0, 100.0) == 0.0
    print("PASS: compute_bpr_delay_pct zero/scaled/guard")


def test_sweep_emits_documented_schema():
    rows = sweep.run_bpr_noop_sweep(
        None,
        {},
        volumes=(0.0, 100.0),
        alphas=(0.36,),
        scales=(1.0,),
        run_fn=_fake_run,
    )
    assert rows
    assert set(rows[0].keys()) == set(sweep.SWEEP_COLUMNS)
    print("PASS: sweep emits documented schema")


def test_alpha_zero_reference_is_freeflow():
    """At volume=0 every alpha row equals the alpha=0 free-flow reference."""
    rows = sweep.run_bpr_noop_sweep(
        None,
        {},
        volumes=(0.0,),
        alphas=(0.15, 0.36, 0.74),
        scales=(1.0,),
        run_fn=_fake_run,
    )
    for row in rows:
        # fake makespan = 1000 + alpha*0*1 = 1000 for all alpha at volume=0
        assert row["makespan"] == 1000.0
        assert row["bpr_delay_pct"] == 0.0
    print("PASS: alpha=0 reference is free-flow; volume=0 -> zero BPR delay")


def test_bpr_delay_monotonic_in_volume_and_deterministic():
    rows = sweep.run_bpr_noop_sweep(
        None,
        {},
        volumes=(100.0, 2000.0, 5000.0),
        alphas=(0.36,),
        scales=(1.0,),
        run_fn=_fake_run,
    )
    by_volume = {r["background_volume"]: r["bpr_delay_pct"] for r in rows}
    assert by_volume[2000.0] > by_volume[100.0]
    assert by_volume[5000.0] > by_volume[2000.0]

    rows_again = sweep.run_bpr_noop_sweep(
        None,
        {},
        volumes=(100.0, 2000.0, 5000.0),
        alphas=(0.36,),
        scales=(1.0,),
        run_fn=_fake_run,
    )
    assert rows == rows_again
    print("PASS: BPR delay monotonic in volume; deterministic")


def test_scale_amplifies_bpr_delay():
    """Higher wartime congestion scale should not reduce BPR delay."""
    rows = sweep.run_bpr_noop_sweep(
        None,
        {},
        volumes=(2000.0,),
        alphas=(0.36,),
        scales=(1.0, 2.0),
        run_fn=_fake_run,
    )
    by_scale = {r["scale"]: r["bpr_delay_pct"] for r in rows}
    assert by_scale[2.0] >= by_scale[1.0]
    print("PASS: scale amplifies BPR delay")


if __name__ == "__main__":
    test_compute_bpr_delay_pct_zero_and_scaled()
    test_sweep_emits_documented_schema()
    test_alpha_zero_reference_is_freeflow()
    test_bpr_delay_monotonic_in_volume_and_deterministic()
    test_scale_amplifies_bpr_delay()
    print("\n=== BPR NO-OP SWEEP TESTS PASSED ===")
