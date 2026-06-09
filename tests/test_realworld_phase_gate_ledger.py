"""Tests for fail-closed phase-gate ledger templates and audits."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.phase_gate_ledger import (
    CANONICAL_PHASE_GATE_SPECS,
    DEFAULT_PHASE_GATE_DECISION_AUTHORITY,
    PHASE_GATE_LEDGER_CLAIM_BOUNDARY,
    REQUIRED_PHASE_GATE_LEDGER_FIELDS,
    build_phase_gate_template,
    phase_gate_ledger_schema,
    validate_phase_gate_ledger_mapping,
    audit_phase_gate_ledgers,
    write_phase_gate_ledgers,
)


def test_phase_gate_schema_exposes_required_fields() -> None:
    """The schema should encode the plan.md minimum ledger fields."""

    schema = phase_gate_ledger_schema()

    assert schema["type"] == "object"
    assert set(REQUIRED_PHASE_GATE_LEDGER_FIELDS).issubset(
        set(schema["required"])
    )
    assert "closed" in schema["properties"]["status"]["enum"]
    assert "closed" in schema["properties"]["gate_decision"]["enum"]


def test_phase_gate_template_is_fail_closed() -> None:
    """Generated templates must never mark a phase complete."""

    ledger = build_phase_gate_template(CANONICAL_PHASE_GATE_SPECS[0])

    validate_phase_gate_ledger_mapping(ledger)
    assert ledger["status"] == "blocked"
    assert ledger["gate_decision"] == "not_closed"
    assert ledger["can_mark_complete"] is False
    assert ledger["final_study_ready"] is False
    assert ledger["command_results"] == []
    assert ledger["artifact_hashes"] == {}
    assert ledger["self_refine"]["performed"] is False
    assert ledger["dependency_control"]["dependency_status"] == "not_satisfied"
    assert "do not close phases" in ledger["claim_boundary"]


def test_phase_gate_validation_blocks_unsupported_completion() -> None:
    """Completion wording requires closed status and closed gate decision."""

    ledger = build_phase_gate_template(CANONICAL_PHASE_GATE_SPECS[0])
    ledger["can_mark_complete"] = True

    try:
        validate_phase_gate_ledger_mapping(ledger)
    except ValueError as exc:
        assert "status 'closed'" in str(exc)
    else:  # pragma: no cover - explicit failure path
        raise AssertionError("unsupported phase completion was accepted")


def test_phase_gate_validation_requires_minimum_fields() -> None:
    """Missing minimum fields should fail before a phase can be audited."""

    ledger = build_phase_gate_template(CANONICAL_PHASE_GATE_SPECS[0])
    ledger.pop("tests")

    try:
        validate_phase_gate_ledger_mapping(ledger)
    except ValueError as exc:
        assert "missing required fields" in str(exc)
        assert "tests" in str(exc)
    else:  # pragma: no cover - explicit failure path
        raise AssertionError("ledger with missing required field was accepted")


def test_phase_gate_validation_blocks_empty_evidence_self_closure() -> None:
    """A structurally closed ledger still needs substantive evidence."""

    ledger = build_phase_gate_template(CANONICAL_PHASE_GATE_SPECS[0])
    ledger.update(
        {
            "status": "closed",
            "gate_decision": "closed",
            "can_mark_complete": True,
            "decision_authority": "reviewer: evidence board",
        }
    )

    try:
        validate_phase_gate_ledger_mapping(ledger)
    except ValueError as exc:
        assert "requires non-empty source_inputs" in str(exc)
    else:  # pragma: no cover - explicit failure path
        raise AssertionError("empty closed ledger was accepted")


def test_phase_gate_validation_blocks_blank_evidence_items() -> None:
    """Blank array entries are not substantive closure evidence."""

    ledger = _closed_ledger()
    ledger["source_inputs"] = ["   "]

    try:
        validate_phase_gate_ledger_mapping(ledger)
    except ValueError as exc:
        assert "source_inputs entries must be non-empty" in str(exc)
    else:  # pragma: no cover - explicit failure path
        raise AssertionError("blank closure evidence was accepted")


def test_phase_gate_validation_blocks_weak_hash_and_authority() -> None:
    """Closure needs hash-shaped artifact evidence and reviewer authority."""

    weak_hash = _closed_ledger()
    weak_hash["artifact_hashes"] = {"artifact": "sha256:example"}
    try:
        validate_phase_gate_ledger_mapping(weak_hash)
    except ValueError as exc:
        assert "sha256:<64 hex>" in str(exc)
    else:  # pragma: no cover - explicit failure path
        raise AssertionError("weak artifact hash was accepted")

    weak_authority = _closed_ledger()
    weak_authority["decision_authority"] = "x"
    try:
        validate_phase_gate_ledger_mapping(weak_authority)
    except ValueError as exc:
        assert "must start with reviewer:" in str(exc)
    else:  # pragma: no cover - explicit failure path
        raise AssertionError("weak decision authority was accepted")


def test_phase_gate_validation_accepts_reviewed_closed_ledger() -> None:
    """A closed ledger is valid only with command, hash, dependency, and review evidence."""

    ledger = _closed_ledger()

    validate_phase_gate_ledger_mapping(ledger)


def test_phase_gate_writer_preserves_reviewed_ledger() -> None:
    """Rerunning the writer must not overwrite reviewed closure evidence."""

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        ledger_dir = root / "phase_gates"
        ledger_dir.mkdir(parents=True)
        path = ledger_dir / f"{CANONICAL_PHASE_GATE_SPECS[0].phase_id}.json"
        path.write_text(
            json.dumps(_closed_ledger(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        audit = write_phase_gate_ledgers(
            ledger_dir=ledger_dir,
            schema_path=root / "schemas" / "phase_gate_ledger.schema.json",
            audit_manifest_path=root / "phase_gate_ledger_audit.json",
            audit_doc_path=root / "phase_gate_ledger_audit.md",
        )
        saved = json.loads(path.read_text(encoding="utf-8"))

        assert saved["status"] == "closed"
        assert saved["gate_decision"] == "closed"
        assert saved["can_mark_complete"] is True
        assert saved["decision_authority"] != DEFAULT_PHASE_GATE_DECISION_AUTHORITY
        assert audit["closed_phase_count"] == 1
        assert audit["phase_gate_ledgers_ready"] is False


def test_write_phase_gate_ledgers_creates_nonready_audit() -> None:
    """Writing default ledgers should create support artifacts without closure."""

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        audit = write_phase_gate_ledgers(
            ledger_dir=root / "phase_gates",
            schema_path=root / "schemas" / "phase_gate_ledger.schema.json",
            audit_manifest_path=root / "phase_gate_ledger_audit.json",
            audit_doc_path=root / "phase_gate_ledger_audit.md",
        )

        ledgers = sorted((root / "phase_gates").glob("*.json"))
        assert len(ledgers) == len(CANONICAL_PHASE_GATE_SPECS)
        assert (root / "schemas" / "phase_gate_ledger.schema.json").exists()
        assert (root / "phase_gate_ledger_audit.json").exists()
        assert (root / "phase_gate_ledger_audit.md").exists()
        assert audit["phase_gate_support_present"] is True
        assert audit["phase_gate_ledgers_ready"] is False
        assert audit["can_mark_complete"] is False
        assert audit["final_study_ready"] is False

        saved = json.loads(
            (root / "phase_gate_ledger_audit.json").read_text(encoding="utf-8")
        )
        assert saved["valid_ledger_count"] == len(CANONICAL_PHASE_GATE_SPECS)


def test_phase_gate_audit_detects_missing_ledgers() -> None:
    """Missing ledger files should be explicit blockers."""

    with tempfile.TemporaryDirectory() as tmp:
        audit = audit_phase_gate_ledgers(ledger_dir=Path(tmp) / "missing")

    assert audit["phase_gate_support_present"] is False
    assert audit["missing_phase_count"] == len(CANONICAL_PHASE_GATE_SPECS)
    assert audit["remaining_blockers"]


def run_all_tests() -> None:
    test_phase_gate_schema_exposes_required_fields()
    test_phase_gate_template_is_fail_closed()
    test_phase_gate_validation_blocks_unsupported_completion()
    test_phase_gate_validation_requires_minimum_fields()
    test_phase_gate_validation_blocks_empty_evidence_self_closure()
    test_phase_gate_validation_blocks_blank_evidence_items()
    test_phase_gate_validation_blocks_weak_hash_and_authority()
    test_phase_gate_validation_accepts_reviewed_closed_ledger()
    test_phase_gate_writer_preserves_reviewed_ledger()
    test_write_phase_gate_ledgers_creates_nonready_audit()
    test_phase_gate_audit_detects_missing_ledgers()


def _closed_ledger() -> dict[str, object]:
    ledger = build_phase_gate_template(CANONICAL_PHASE_GATE_SPECS[0])
    ledger.update(
        {
            "status": "closed",
            "source_inputs": ["plan.md"],
            "generated_outputs": ["data/manifests/phase_gates/phase0_baseline_and_worktree_safety.json"],
            "tests": ["tests/test_realworld_phase_gate_ledger.py"],
            "sub_agents": ["reviewer:gpt-5.5-xhigh:no-open-blockers"],
            "command_results": [
                {
                    "command": ".\\.venv\\Scripts\\python tests\\test_realworld_phase_gate_ledger.py",
                    "status": "passed",
                    "exit_code": 0,
                }
            ],
            "artifact_hashes": {
                "data/manifests/phase_gates/phase0_baseline_and_worktree_safety.json": (
                    "sha256:"
                    "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
                )
            },
            "self_refine": {
                "performed": True,
                "status": "passed",
                "notes": "reviewed and no open blocker remains",
            },
            "dependency_control": {
                "dependency_status": "satisfied",
                "parallelism_mode": "single_thread",
                "synthesis_barrier": "passed",
                "write_locks": ["data/manifests/phase_gates/phase0_baseline_and_worktree_safety.json"],
            },
            "findings": ["no open high or medium findings after review"],
            "claim_boundary": PHASE_GATE_LEDGER_CLAIM_BOUNDARY,
            "gate_decision": "closed",
            "decision_authority": "reviewer:evidence-board:2026-06-03",
            "can_mark_complete": True,
        }
    )
    return ledger


if __name__ == "__main__":
    run_all_tests()
    print("PASS: phase gate ledger")
