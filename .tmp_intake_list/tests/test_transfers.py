"""Unit tests for transfer delay helpers."""

import os
import sys

import simpy

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.transfers import (
    TransferDelayConfig,
    compute_transfer_delay,
    transfer_batch,
    wait_for_transfer,
)


def assert_close(actual, expected, tolerance=0.001, label="value"):
    assert abs(actual - expected) <= tolerance, (
        f"{label}: expected {expected}, got {actual}"
    )


def test_transfer_delay_supports_fixed_and_per_passenger_terms():
    """Transfer delay should represent fixed and crowd-dependent delay."""
    assert_close(
        compute_transfer_delay(4, base_min=2.0, per_passenger_min=0.5),
        4.0,
        label="transfer delay",
    )
    assert_close(
        compute_transfer_delay(4, base_min=2.0),
        2.0,
        label="fixed-only transfer delay",
    )
    config = TransferDelayConfig(base_min=1.0, per_passenger_min=0.25)
    assert_close(config.delay_for(8), 3.0, label="configured transfer delay")
    print("PASS: transfer delay supports fixed and per-passenger terms")


def test_transfer_delay_rejects_negative_inputs():
    """Negative delay inputs should fail fast."""
    for passenger_count in (-1, float("nan")):
        try:
            compute_transfer_delay(passenger_count, base_min=0.0, per_passenger_min=0.0)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid passenger_count should raise ValueError")

    try:
        compute_transfer_delay(1, base_min=-1.0, per_passenger_min=0.0)
    except ValueError:
        pass
    else:
        raise AssertionError("negative base_min should raise ValueError")

    try:
        compute_transfer_delay(1, base_min=0.0, per_passenger_min=-0.1)
    except ValueError:
        pass
    else:
        raise AssertionError("negative per_passenger_min should raise ValueError")

    print("PASS: transfer delay validation rejects negative inputs")


def test_wait_for_transfer_advances_simpy_time_by_delay():
    """The SimPy transfer wait should advance by the computed delay."""
    env = simpy.Environment()
    observed = []

    def flow():
        delay = yield env.process(
            wait_for_transfer(
                env,
                passenger_count=3,
                base_min=1.0,
                per_passenger_min=0.5,
            )
        )
        observed.append((env.now, delay))

    env.process(flow())
    env.run()

    assert observed == [(2.5, 2.5)]
    print("PASS: transfer wait advances by computed delay")


def test_transfer_batch_releases_passengers_after_delay():
    """Transfer batches should become available only after the delay."""
    env = simpy.Environment()
    station_queue = []
    ready_results = []

    env.process(
        transfer_batch(
            env,
            passengers=[101, 102, 103, 104],
            destination_queue=station_queue,
            base_min=2.0,
            per_passenger_min=0.25,
            on_ready=ready_results.append,
        )
    )

    env.run(until=2.9)
    assert station_queue == []

    env.run(until=3.1)
    assert station_queue == [101, 102, 103, 104]
    assert len(ready_results) == 1
    assert_close(ready_results[0].ready_time, 3.0, label="ready time")
    assert_close(ready_results[0].delay_min, 3.0, label="delay")
    print("PASS: transfer batch releases passengers after delay")


if __name__ == "__main__":
    test_transfer_delay_supports_fixed_and_per_passenger_terms()
    test_transfer_delay_rejects_negative_inputs()
    test_wait_for_transfer_advances_simpy_time_by_delay()
    test_transfer_batch_releases_passengers_after_delay()
    print("\n=== ALL TRANSFER TESTS PASSED ===")
