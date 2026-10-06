"""Tests for restartable paper-revision campaign primitives."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.realworld.revision_campaign import (
    CampaignPathError,
    CheckpointJournal,
    CheckpointError,
    RunSpec,
    append_checkpoint,
    assert_isolated_output_path,
    expand_run_matrix,
    load_resume_keys,
    pending_run_specs,
)


def _base_spec(**overrides: object) -> RunSpec:
    values: dict[str, object] = {
        "campaign_id": "paper_revision_top5_20260721",
        "configuration_id": "baseline",
        "policy_id": "bus_only",
        "departure_policy_id": "strict",
        "resource_frame": "configured_bundle",
        "graph_scope": "top3",
        "corridor_path_count": 3,
        "arrival_seed": 3101,
        "threat_seed": None,
        "threat_draw": None,
        "selected_edges_checksum": "",
        "rail_status": "available",
        "return_strategy": "reverse_network",
    }
    values.update(overrides)
    return RunSpec.from_mapping(values)


def test_run_spec_key_is_stable_and_content_addressed() -> None:
    spec = _base_spec()
    reordered = RunSpec.from_mapping(dict(reversed(list(spec.to_mapping().items()))))

    assert spec == reordered
    assert spec.run_key == reordered.run_key
    assert len(spec.run_key) == 64
    assert _base_spec(arrival_seed=3102).run_key != spec.run_key

    try:
        _base_spec(rail_status="unknown")
    except ValueError as exc:
        assert "rail_status" in str(exc)
    else:
        raise AssertionError("unknown rail status must be rejected")

    print("PASS: run spec key is stable and content-addressed")


def test_matrix_expansion_has_deterministic_field_order() -> None:
    first_matrix = {
        "policy_id": ["bus_only", "baseline_multimodal"],
        "configuration_id": ["cfg-b", "cfg-a"],
        "campaign_id": "paper_revision_top5_20260721",
        "departure_policy_id": "strict",
        "resource_frame": "configured_bundle",
        "graph_scope": "top3",
        "corridor_path_count": 3,
        "arrival_seed": [3101, 3102],
        "rail_status": "available",
        "return_strategy": "reverse_network",
    }
    second_matrix = dict(reversed(list(first_matrix.items())))

    first = expand_run_matrix(first_matrix)
    second = expand_run_matrix(second_matrix)

    assert first == second
    assert len(first) == 8
    assert [
        (item.configuration_id, item.policy_id, item.arrival_seed)
        for item in first
    ] == [
        ("cfg-b", "bus_only", 3101),
        ("cfg-b", "bus_only", 3102),
        ("cfg-b", "baseline_multimodal", 3101),
        ("cfg-b", "baseline_multimodal", 3102),
        ("cfg-a", "bus_only", 3101),
        ("cfg-a", "bus_only", 3102),
        ("cfg-a", "baseline_multimodal", 3101),
        ("cfg-a", "baseline_multimodal", 3102),
    ]

    print("PASS: matrix expansion order is deterministic")


def test_checkpoint_resume_skips_completed_and_duplicate_specs() -> None:
    completed = _base_spec(arrival_seed=3101)
    pending = _base_spec(arrival_seed=3102)

    with TemporaryDirectory() as directory:
        checkpoint = Path(directory) / "campaign.jsonl"
        assert append_checkpoint(checkpoint, completed, {"makespan": 283.1}) is True
        assert append_checkpoint(checkpoint, completed, {"makespan": 999.0}) is False

        completed_keys = load_resume_keys(checkpoint)
        assert completed_keys == frozenset({completed.run_key})
        remaining = pending_run_specs(
            [completed, pending, pending],
            completed_keys,
        )
        assert remaining == (pending,)

        records = [
            json.loads(line)
            for line in checkpoint.read_text(encoding="utf-8").splitlines()
        ]
        assert len(records) == 1
        assert records[0]["run_key"] == completed.run_key
        assert records[0]["run_spec"] == completed.to_mapping()
        assert records[0]["result"] == {"makespan": 283.1}
        assert not list(checkpoint.parent.glob(f".{checkpoint.name}.*.tmp"))

    print("PASS: checkpoint resume skips completed and duplicate specs")


def test_malformed_checkpoint_is_rejected() -> None:
    with TemporaryDirectory() as directory:
        checkpoint = Path(directory) / "campaign.jsonl"
        CheckpointJournal(checkpoint).append(_base_spec(), {"makespan": 283.1})
        with checkpoint.open("a", encoding="utf-8") as handle:
            handle.write("not-json\n")

        try:
            load_resume_keys(checkpoint)
        except CheckpointError as exc:
            assert "line 2" in str(exc)
        else:
            raise AssertionError("malformed checkpoint must be rejected")

    print("PASS: malformed checkpoint is rejected")


def test_checkpoint_journal_appends_without_rewriting_previous_bytes() -> None:
    first = _base_spec(arrival_seed=3101)
    second = _base_spec(arrival_seed=3102)

    with TemporaryDirectory() as directory:
        checkpoint = Path(directory) / "campaign.jsonl"
        journal = CheckpointJournal(checkpoint)
        assert journal.append(first, {"makespan": 283.1}) is True
        previous = checkpoint.read_bytes()

        with patch(
            "src.realworld.revision_campaign.os.replace",
            side_effect=AssertionError("append must not replace checkpoint"),
        ):
            assert journal.append(second, {"makespan": 284.0}) is True

        current = checkpoint.read_bytes()
        assert current.startswith(previous)
        assert len(current) > len(previous)
        assert load_resume_keys(checkpoint) == frozenset(
            {first.run_key, second.run_key}
        )

    print("PASS: checkpoint journal appends without rewriting old records")


def test_checkpoint_detects_record_corruption() -> None:
    spec = _base_spec()

    with TemporaryDirectory() as directory:
        checkpoint = Path(directory) / "campaign.jsonl"
        CheckpointJournal(checkpoint).append(spec, {"makespan": 283.1})
        payload = checkpoint.read_bytes().replace(b"283.1", b"283.2", 1)
        checkpoint.write_bytes(payload)

        try:
            load_resume_keys(checkpoint)
        except CheckpointError as exc:
            assert "checksum" in str(exc)
        else:
            raise AssertionError("modified checkpoint record must be rejected")

    print("PASS: checkpoint detects record corruption")


def test_checkpoint_repairs_only_truncated_final_record() -> None:
    first = _base_spec(arrival_seed=3101)
    second = _base_spec(arrival_seed=3102)

    with TemporaryDirectory() as directory:
        checkpoint = Path(directory) / "campaign.jsonl"
        CheckpointJournal(checkpoint).append(first, {"makespan": 283.1})
        with checkpoint.open("ab") as handle:
            handle.write(b'{"schema_version":1,"run_key":"truncated')

        journal = CheckpointJournal(checkpoint, repair_truncated_tail=True)
        assert journal.completed_keys == frozenset({first.run_key})
        assert checkpoint.read_bytes().endswith(b"\n")
        assert journal.append(second, {"makespan": 284.0}) is True
        assert load_resume_keys(checkpoint) == frozenset(
            {first.run_key, second.run_key}
        )

    print("PASS: checkpoint repairs only truncated final record")


def test_output_isolation_guard_blocks_canonical_tree() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        canonical = root / "results" / "realworld_pilot_nodelink"

        for unsafe in (canonical, canonical / "nested" / "campaign.jsonl"):
            try:
                assert_isolated_output_path(unsafe, canonical_dir=canonical)
            except CampaignPathError as exc:
                assert "canonical" in str(exc)
            else:
                raise AssertionError(f"canonical path must be rejected: {unsafe}")

        safe = root / "results" / "paper_revision_top5_20260721"
        assert assert_isolated_output_path(safe, canonical_dir=canonical) == safe.resolve()

    print("PASS: output isolation guard blocks canonical result tree")


if __name__ == "__main__":
    test_run_spec_key_is_stable_and_content_addressed()
    test_matrix_expansion_has_deterministic_field_order()
    test_checkpoint_resume_skips_completed_and_duplicate_specs()
    test_malformed_checkpoint_is_rejected()
    test_checkpoint_journal_appends_without_rewriting_previous_bytes()
    test_checkpoint_detects_record_corruption()
    test_checkpoint_repairs_only_truncated_final_record()
    test_output_isolation_guard_blocks_canonical_tree()
