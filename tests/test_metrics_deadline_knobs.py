"""G2 deadline/censoring knob-isolation proof.

Proves at the metrics layer (no scenario machinery):

  * ``time_limit`` drives ``success_count`` / ``censored_count`` /
    ``completion_rate`` — monotonically: a longer horizon censors fewer people.
  * ``late_penalty_min`` does NOT affect ``censored_count`` /
    ``completion_rate`` / ``success_count``. It only reweights
    ``penalized_makespan`` (= max(makespan, time_limit) + censored * penalty).

This isolates the knobs that the submitted planning-doc "5h deadline ladder"
concept must map onto: **censoring = ``time_limit``, NOT ``late_penalty_min``**.
See ``docs/deadline_mechanism.md``.

Direct-executable (no pytest): ``python tests/test_metrics_deadline_knobs.py``.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.metrics import MetricsCollector


def assert_close(actual, expected, tolerance=1e-9, label="value"):
    assert abs(actual - expected) <= tolerance, (
        f"{label}: expected {expected}, got {actual}"
    )


def build_populated(total_personnel, leftover_count):
    """Return a collector with a fixed spread of arrival times.

    Arrival buckets (min): 840 @150, 60 @280, 60 @340 (=960 delivered).
    ``leftover_count`` people get no arrival record (stranded floor).

    Bucket layout chosen so a 200/300/360-min horizon sweep crosses each bucket:
      time_limit=200 -> only @150 counted (success=840)
      time_limit=300 -> @150 + @280 counted      (success=900)
      time_limit=360 -> @150 + @280 + @340       (success=960)
    """
    metrics = MetricsCollector(total_personnel=total_personnel)
    for _ in range(840):
        metrics.record_arrival(0, 150.0)
    for _ in range(60):
        metrics.record_arrival(0, 280.0)
    for _ in range(60):
        metrics.record_arrival(0, 340.0)
    metrics.leftover_count = leftover_count
    return metrics


def test_time_limit_drives_censored_count():
    """Sweeping time_limit moves censored_count and completion_rate."""
    expectations = [
        # (time_limit, success, censored, completion_rate, ladder_label)
        (200.0, 840, 160, 0.84, "3.3h horizon"),
        (300.0, 900, 100, 0.90, "5.0h horizon"),
        (360.0, 960, 40, 0.96, "6.0h horizon"),
    ]
    for time_limit, exp_success, exp_censored, exp_completion, label in expectations:
        m = build_populated(total_personnel=1000, leftover_count=40)
        m.time_limit = time_limit
        assert m.success_count == exp_success, (
            f"{label}: success_count={m.success_count}, want {exp_success}"
        )
        assert m.censored_count == exp_censored, (
            f"{label}: censored_count={m.censored_count}, want {exp_censored}"
        )
        assert_close(m.completion_rate, exp_completion, label=f"completion@{label}")
        # raw makespan is independent of time_limit (max of all arrivals)
        assert m.makespan == 340.0, f"{label}: makespan={m.makespan}, want 340.0"
    print("PASS: time_limit drives censored_count / completion (160->100->40)")


def test_late_penalty_does_not_drive_censored_count():
    """Sweeping late_penalty_min leaves censored_count / completion_rate invariant."""
    for late_penalty in (300.0, 600.0, 999.0):
        m = build_populated(total_personnel=1000, leftover_count=40)
        m.time_limit = 200.0
        m.late_penalty_min = late_penalty
        assert m.success_count == 840, (
            f"penalty={late_penalty}: success_count leaked to {m.success_count}"
        )
        assert m.censored_count == 160, (
            f"penalty={late_penalty}: censored leaked to {m.censored_count}"
        )
        assert_close(m.completion_rate, 0.84, label=f"completion@penalty={late_penalty}")
        assert m.makespan == 340.0
    print("PASS: late_penalty_min does NOT drive censored_count (stays 160)")


def test_late_penalty_only_reweights_penalized_makespan():
    """penalized_makespan = max(makespan, time_limit) + censored * late_penalty_min."""
    for late_penalty in (300.0, 600.0, 999.0):
        m = build_populated(total_personnel=1000, leftover_count=40)
        m.time_limit = 200.0
        m.late_penalty_min = late_penalty
        expected = max(340.0, 200.0) + 160 * late_penalty
        assert_close(
            m.penalized_makespan,
            expected,
            label=f"penalized@penalty={late_penalty}",
        )
    print("PASS: late_penalty_min only reweights penalized_makespan")


def test_default_late_penalty_equals_time_limit():
    """When late_penalty_min is None, each censored person is charged time_limit min."""
    m = build_populated(total_personnel=1000, leftover_count=40)
    m.time_limit = 200.0
    m.late_penalty_min = None  # collector default
    expected = max(340.0, 200.0) + 160 * 200.0
    assert_close(m.penalized_makespan, expected, label="default-late-penalty")
    print("PASS: default late_penalty_min == time_limit (340 + 160*200)")


def test_success_deadline_decoupled_from_time_limit():
    """success_deadline_min drives completion independent of the censor horizon.

    With time_limit=360 (observe all 960 arrivals) but success_deadline_min=200,
    only the @150 bucket counts as successful (840) even though later arrivals
    were observed before the censor cutoff. This is the Phase-5 ladder
    mechanism: a generous censor horizon + a swept operational deadline.
    """
    # deadline set, shorter than censor horizon -> completion follows deadline
    m = build_populated(total_personnel=1000, leftover_count=40)
    m.time_limit = 360.0
    m.success_deadline_min = 200.0
    assert m.success_deadline == 200.0
    assert m.success_count == 840, f"deadline success={m.success_count}, want 840"
    assert m.completion_rate == 0.84
    # deadline None -> falls back to time_limit (legacy behaviour)
    m2 = build_populated(total_personnel=1000, leftover_count=40)
    m2.time_limit = 360.0
    m2.success_deadline_min = None
    assert m2.success_deadline == 360.0
    assert m2.success_count == 960, f"fallback success={m2.success_count}, want 960"
    print("PASS: success_deadline decoupled from time_limit (200 deadline -> 840; None -> time_limit)")


TESTS = [
    test_time_limit_drives_censored_count,
    test_late_penalty_does_not_drive_censored_count,
    test_late_penalty_only_reweights_penalized_makespan,
    test_default_late_penalty_equals_time_limit,
    test_success_deadline_decoupled_from_time_limit,
]


if __name__ == "__main__":
    for test in TESTS:
        test()
    print("\n=== ALL DEADLINE-KNOB TESTS PASSED ===")
