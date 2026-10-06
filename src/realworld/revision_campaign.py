"""Pure, restartable primitives for paper-revision experiment campaigns.

This module does not execute simulations.  It defines stable run identities,
deterministic matrix expansion, isolated output paths, and an atomic JSONL
checkpoint used by higher-level runners.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import MISSING, dataclass, fields
from itertools import product
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_RESULTS_DIR = PROJECT_ROOT / "results" / "realworld_pilot_nodelink"

RAIL_STATUSES = frozenset({"available", "degraded", "unavailable"})
RETURN_STRATEGIES = frozenset({"legacy_none", "reverse_network"})


class CampaignPathError(ValueError):
    """Raised when revision output could modify canonical pilot results."""


class CheckpointError(ValueError):
    """Raised when a JSONL checkpoint cannot be read safely."""


@dataclass(frozen=True, slots=True)
class RunSpec:
    """Complete, content-addressed identity for one campaign replication."""

    campaign_id: str
    configuration_id: str
    policy_id: str
    departure_policy_id: str
    resource_frame: str
    graph_scope: str
    corridor_path_count: int | None
    arrival_seed: int
    threat_seed: int | None = None
    threat_draw: int | None = None
    selected_edges_checksum: str = ""
    rail_status: str = "available"
    return_strategy: str = "legacy_none"

    def __post_init__(self) -> None:
        for field_name in (
            "campaign_id",
            "configuration_id",
            "policy_id",
            "departure_policy_id",
            "resource_frame",
            "graph_scope",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")

        _validate_optional_positive_int(
            "corridor_path_count",
            self.corridor_path_count,
            allow_zero=False,
        )
        _validate_required_nonnegative_int("arrival_seed", self.arrival_seed)
        _validate_optional_positive_int("threat_seed", self.threat_seed)
        _validate_optional_positive_int("threat_draw", self.threat_draw)

        if not isinstance(self.selected_edges_checksum, str):
            raise ValueError("selected_edges_checksum must be a string")
        if self.selected_edges_checksum:
            checksum = self.selected_edges_checksum.lower()
            if len(checksum) != 64 or any(
                character not in "0123456789abcdef" for character in checksum
            ):
                raise ValueError(
                    "selected_edges_checksum must be empty or a SHA-256 hex digest"
                )

        if self.rail_status not in RAIL_STATUSES:
            raise ValueError(
                "rail_status must be one of " + ", ".join(sorted(RAIL_STATUSES))
            )
        if self.return_strategy not in RETURN_STRATEGIES:
            raise ValueError(
                "return_strategy must be one of "
                + ", ".join(sorted(RETURN_STRATEGIES))
            )

    @classmethod
    def from_mapping(cls, values: Mapping[str, Any]) -> "RunSpec":
        """Build a validated spec and reject silent schema drift."""

        if not isinstance(values, Mapping):
            raise TypeError("run spec values must be a mapping")
        field_names = {item.name for item in fields(cls)}
        unknown = sorted(set(values) - field_names)
        if unknown:
            raise ValueError(f"unknown run spec fields: {', '.join(unknown)}")

        required = {
            item.name
            for item in fields(cls)
            if item.default is MISSING and item.default_factory is MISSING
        }
        missing = sorted(required - set(values))
        if missing:
            raise ValueError(f"missing run spec fields: {', '.join(missing)}")
        return cls(**dict(values))

    def to_mapping(self) -> dict[str, Any]:
        """Return fields in canonical schema order."""

        return {item.name: getattr(self, item.name) for item in fields(self)}

    @property
    def run_key(self) -> str:
        """SHA-256 identity over canonical JSON representation."""

        payload = json.dumps(
            self.to_mapping(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()


def expand_run_matrix(matrix: Mapping[str, Any]) -> tuple[RunSpec, ...]:
    """Expand matrix dimensions in RunSpec field order.

    Mapping insertion order never changes output order.  Sequence item order is
    preserved because experiment authors often use it to stage cheap runs first.
    Unordered set dimensions are rejected.
    """

    if not isinstance(matrix, Mapping):
        raise TypeError("campaign matrix must be a mapping")

    schema_fields = fields(RunSpec)
    schema_names = {item.name for item in schema_fields}
    unknown = sorted(set(matrix) - schema_names)
    if unknown:
        raise ValueError(f"unknown campaign matrix fields: {', '.join(unknown)}")

    names: list[str] = []
    dimensions: list[tuple[Any, ...]] = []
    missing: list[str] = []
    for item in schema_fields:
        names.append(item.name)
        if item.name in matrix:
            dimensions.append(_dimension_values(item.name, matrix[item.name]))
        elif item.default is not MISSING:
            dimensions.append((item.default,))
        elif item.default_factory is not MISSING:  # pragma: no cover - future schema
            dimensions.append((item.default_factory(),))
        else:
            missing.append(item.name)
            dimensions.append(())
    if missing:
        raise ValueError(f"missing campaign matrix fields: {', '.join(missing)}")

    return tuple(
        RunSpec.from_mapping(dict(zip(names, combination, strict=True)))
        for combination in product(*dimensions)
    )


def pending_run_specs(
    specs: Iterable[RunSpec],
    completed_keys: Iterable[str] = (),
) -> tuple[RunSpec, ...]:
    """Return stable, de-duplicated specs absent from checkpoint keys."""

    completed = set(completed_keys)
    seen: set[str] = set()
    pending: list[RunSpec] = []
    for spec in specs:
        if not isinstance(spec, RunSpec):
            raise TypeError("pending_run_specs accepts RunSpec values only")
        key = spec.run_key
        if key in completed or key in seen:
            continue
        seen.add(key)
        pending.append(spec)
    return tuple(pending)


def append_checkpoint(
    checkpoint_path: str | Path,
    spec: RunSpec,
    result: Mapping[str, Any] | None = None,
) -> bool:
    """Append through a one-shot journal.

    Campaign runners should keep one :class:`CheckpointJournal` open logically
    for the whole run, so checkpoint validation is O(N) once and each append is
    O(1).  This wrapper preserves the small-call API for tests and utilities.
    """

    return CheckpointJournal(checkpoint_path).append(spec, result)


class CheckpointJournal:
    """Validated append-only JSONL journal with restart-tail recovery.

    Every complete record carries a SHA-256 over its canonical payload.  Startup
    scans once, rejects modified/duplicate records, and may discard only an
    unterminated final fragment left by an interrupted append.  Completed bytes
    are never recopied during normal appends.
    """

    def __init__(
        self,
        checkpoint_path: str | Path,
        *,
        repair_truncated_tail: bool = True,
    ) -> None:
        self.path = assert_isolated_output_path(checkpoint_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._records = list(
            load_checkpoint_records(
                self.path,
                repair_truncated_tail=repair_truncated_tail,
            )
        )
        self._completed_keys = {str(record["run_key"]) for record in self._records}

    @property
    def completed_keys(self) -> frozenset[str]:
        return frozenset(self._completed_keys)

    @property
    def records(self) -> tuple[dict[str, Any], ...]:
        return tuple(dict(record) for record in self._records)

    def append(
        self,
        spec: RunSpec,
        result: Mapping[str, Any] | None = None,
    ) -> bool:
        if not isinstance(spec, RunSpec):
            raise TypeError("checkpoint spec must be a RunSpec")
        if result is not None and not isinstance(result, Mapping):
            raise TypeError("checkpoint result must be a mapping or None")
        if spec.run_key in self._completed_keys:
            return False

        payload = {
            "schema_version": 1,
            "run_key": spec.run_key,
            "run_spec": spec.to_mapping(),
            "result": dict(result or {}),
        }
        try:
            payload_bytes = _canonical_json_bytes(payload)
            record = dict(payload)
            record["record_sha256"] = hashlib.sha256(payload_bytes).hexdigest()
            encoded_record = _canonical_json_bytes(record) + b"\n"
        except (TypeError, ValueError) as exc:
            raise CheckpointError(
                f"checkpoint record is not JSON-safe: {exc}"
            ) from exc

        flags = os.O_APPEND | os.O_CREAT | os.O_WRONLY
        flags |= getattr(os, "O_BINARY", 0)
        descriptor = os.open(self.path, flags, 0o600)
        try:
            offset = 0
            while offset < len(encoded_record):
                written = os.write(descriptor, encoded_record[offset:])
                if written <= 0:  # pragma: no cover - defensive OS contract
                    raise OSError("checkpoint append made no progress")
                offset += written
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

        self._records.append(record)
        self._completed_keys.add(spec.run_key)
        return True


def load_resume_keys(checkpoint_path: str | Path) -> frozenset[str]:
    """Load completed run keys from a validated JSONL checkpoint."""

    return frozenset(
        str(record["run_key"])
        for record in load_checkpoint_records(checkpoint_path)
    )


def load_checkpoint_records(
    checkpoint_path: str | Path,
    *,
    repair_truncated_tail: bool = False,
) -> tuple[dict[str, Any], ...]:
    """Read and validate checkpoint records, optionally repairing crash tail."""

    path = Path(checkpoint_path)
    if not path.exists():
        return ()
    if not path.is_file():
        raise CheckpointError(f"checkpoint is not a file: {path}")

    try:
        content = path.read_bytes()
    except OSError as exc:
        raise CheckpointError(f"cannot read checkpoint {path}: {exc}") from exc

    if content and not content.endswith(b"\n"):
        if not repair_truncated_tail:
            raise CheckpointError(f"checkpoint has a truncated final record: {path}")
        final_newline = content.rfind(b"\n")
        valid_size = final_newline + 1
        try:
            with path.open("r+b") as handle:
                handle.truncate(valid_size)
                handle.flush()
                os.fsync(handle.fileno())
        except OSError as exc:
            raise CheckpointError(
                f"cannot repair truncated checkpoint {path}: {exc}"
            ) from exc
        content = content[:valid_size]

    records: list[dict[str, Any]] = []
    keys: set[str] = set()
    for line_number, encoded_line in enumerate(content.splitlines(), start=1):
        if not encoded_line.strip():
            continue
        try:
            line = encoded_line.decode("utf-8")
            record = json.loads(line)
        except UnicodeDecodeError as exc:
            raise CheckpointError(
                f"invalid checkpoint UTF-8 at line {line_number}"
            ) from exc
        except json.JSONDecodeError as exc:
            raise CheckpointError(
                f"invalid checkpoint JSON at line {line_number}: {exc.msg}"
            ) from exc
        validated = _validate_checkpoint_record(record, line_number)
        key = str(validated["run_key"])
        if key in keys:
            raise CheckpointError(f"checkpoint contains duplicate run_key: {key}")
        keys.add(key)
        records.append(validated)
    return tuple(records)


def assert_isolated_output_path(
    output_path: str | Path,
    *,
    canonical_dir: str | Path = CANONICAL_RESULTS_DIR,
) -> Path:
    """Resolve output and reject canonical result directory or descendants."""

    target = Path(output_path).expanduser().resolve()
    canonical = Path(canonical_dir).expanduser().resolve()
    if target == canonical or canonical in target.parents:
        raise CampaignPathError(
            "revision campaign output must not use canonical results tree: "
            f"{canonical}"
        )
    return target


def _dimension_values(name: str, value: Any) -> tuple[Any, ...]:
    if isinstance(value, (set, frozenset)):
        raise ValueError(f"campaign matrix field {name} cannot use an unordered set")
    if isinstance(value, Mapping):
        raise ValueError(f"campaign matrix field {name} cannot use a mapping dimension")
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        values = tuple(value)
        if not values:
            raise ValueError(f"campaign matrix field {name} cannot be empty")
        return values
    return (value,)


def _canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _validate_checkpoint_record(value: Any, line_number: int) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CheckpointError(
            f"checkpoint line {line_number} must contain a JSON object"
        )
    expected_fields = {
        "schema_version",
        "run_key",
        "run_spec",
        "result",
        "record_sha256",
    }
    if set(value) != expected_fields:
        raise CheckpointError(
            f"checkpoint line {line_number} has invalid record schema"
        )
    if value.get("schema_version") != 1:
        raise CheckpointError(
            f"checkpoint line {line_number} has unsupported schema_version"
        )
    key = value.get("run_key")
    if not _is_sha256(key):
        raise CheckpointError(f"checkpoint line {line_number} has invalid run_key")
    try:
        spec = RunSpec.from_mapping(value.get("run_spec"))
    except (TypeError, ValueError) as exc:
        raise CheckpointError(
            f"checkpoint line {line_number} has invalid run_spec: {exc}"
        ) from exc
    if spec.run_key != str(key).lower():
        raise CheckpointError(
            f"checkpoint line {line_number} run_key does not match run_spec"
        )
    if not isinstance(value.get("result"), dict):
        raise CheckpointError(
            f"checkpoint line {line_number} must contain object result"
        )
    record_checksum = value.get("record_sha256")
    if not _is_sha256(record_checksum):
        raise CheckpointError(
            f"checkpoint line {line_number} has invalid record checksum"
        )
    payload = {name: value[name] for name in expected_fields - {"record_sha256"}}
    expected_checksum = hashlib.sha256(_canonical_json_bytes(payload)).hexdigest()
    if str(record_checksum).lower() != expected_checksum:
        raise CheckpointError(
            f"checkpoint line {line_number} record checksum mismatch"
        )
    validated = dict(value)
    validated["run_key"] = str(key).lower()
    validated["record_sha256"] = str(record_checksum).lower()
    return validated


def _validate_required_nonnegative_int(name: str, value: Any) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")


def _validate_optional_positive_int(
    name: str,
    value: Any,
    *,
    allow_zero: bool = True,
) -> None:
    if value is None:
        return
    minimum = 0 if allow_zero else 1
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        qualifier = "non-negative" if allow_zero else "positive"
        raise ValueError(f"{name} must be None or a {qualifier} integer")


def _is_sha256(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    return all(character in "0123456789abcdefABCDEF" for character in value)
