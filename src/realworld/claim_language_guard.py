"""Fail-closed lexical guard for claim-bearing language.

This module is broader than the manuscript claim-alignment packet. It scans
selected reports, package docs, manifests, and planning text for reserved claim
terms, then marks lines as bounded only when nearby text explicitly preserves a
non-approval or non-operational boundary. It is a release guard, not acceptance.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CLAIM_LANGUAGE_GUARD_PATH = (
    PROJECT_ROOT / "data" / "validation" / "claim_language_guard.csv"
)
DEFAULT_CLAIM_LANGUAGE_GUARD_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "claim_language_guard_manifest.json"
)
DEFAULT_CLAIM_LANGUAGE_GUARD_DOC_PATH = PROJECT_ROOT / "docs" / "claim_language_guard.md"
CLAIM_LANGUAGE_GUARD_SCOPE = (
    "Lexical claim-language guard only; not manuscript acceptance, not formal "
    "approval, not calibrated validation, and not operational readiness."
)
CLAIM_LANGUAGE_GUARD_COLUMNS: tuple[str, ...] = (
    "finding_id",
    "source_path",
    "line_number",
    "term",
    "status",
    "evidence_context",
    "excerpt",
    "required_action",
    "can_support_release",
    "claim_boundary",
)
BOUNDED_NON_CLAIM_REFERENCE_STATUS = "bounded_non_claim_reference"

RESERVED_TERM_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (term, re.compile(pattern, re.IGNORECASE))
    for term, pattern in (
        ("accepted", r"\baccept(?:ed|ance|ing|s)?\b"),
        ("final", r"\bfinal(?:[-_ ]study(?:_ready)?|ity|ized|ise|ize|s)?\b"),
        ("ready", r"\bready\b|\breadiness\b|\bfinal_study_ready\b|\bpublication_ready\b"),
        ("validated", r"\bvalidat(?:ed|ion|e|es|ing)\b"),
        ("calibrated", r"\bcalibrat(?:ed|ion|e|es|ing)\b"),
        ("operational", r"\boperational(?:ly)?\b"),
        ("forecast", r"\bforecast(?:s|ed|ing)?\b"),
        ("real-time", r"\breal[- ]time\b"),
        ("approved", r"\bapprov(?:ed|al|e|es|ing)\b"),
    )
)

BOUNDARY_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bnot\b",
        r"\bno\b.{0,80}\b(approval|acceptance|validation|calibration|operational|forecast|ready|final)\b",
        r"\b(non[- ]approval|non[- ]acceptance|non[- ]operational|non[- ]final)\b",
        r"\b(blocked|blocking|absent|missing|unavailable|pending|draft|scaffold|guardrail|fail[- ]closed)\b",
        r"\b(does not|do not|must not|should not|cannot|can't)\b",
        r"\b(can_mark_complete|final_study_ready|publication_ready|accepted)\b.{0,40}\b(false|0)\b",
        r"\b(false|0)\b.{0,40}\b(can_mark_complete|final_study_ready|publication_ready|accepted)\b",
        r"\bclaim[_ -]?boundary\b|\breview aid\b|\breview packet\b|\btemplate only\b",
        r"\bdecision[- ]support\b",
        r"\buntil\b.{0,120}\b(evidence|gate|acceptance|review|approval)\b",
    )
)


def default_claim_language_scan_paths(
    *, project_root: str | Path = PROJECT_ROOT
) -> list[Path]:
    """Return deterministic default files for lexical release-claim scanning."""

    root = Path(project_root)
    candidates: list[Path] = [
        root / "README.md",
        root / "agents.md",
        root / "AGENTS.md",
        root / "plan.md",
        root / "status.md",
        root / "report_draft.md",
        root / "paper" / "paper_draft.md",
        root / "results" / "realworld_pilot" / "tables" / "figure_table_manifest.json",
        root / "data" / "manifests" / "publication_readiness_audit.json",
        root / "data" / "manifests" / "current_goal_completion_audit.json",
        root / "data" / "manifests" / "phase_gate_ledger_audit.json",
    ]
    docs_root = root / "docs"
    if docs_root.exists():
        candidates.extend(sorted(docs_root.glob("*.md")))
    manifests_root = root / "data" / "manifests"
    if manifests_root.exists():
        candidates.extend(sorted(manifests_root.glob("*.json")))
        candidates.extend(sorted((manifests_root / "phase_gates").glob("*.json")))
    figure_table_root = root / "results" / "realworld_pilot" / "tables"
    if figure_table_root.exists():
        candidates.extend(sorted(figure_table_root.glob("*.json")))
    excluded = {
        DEFAULT_CLAIM_LANGUAGE_GUARD_PATH.resolve().as_posix().lower(),
        DEFAULT_CLAIM_LANGUAGE_GUARD_MANIFEST_PATH.resolve().as_posix().lower(),
        DEFAULT_CLAIM_LANGUAGE_GUARD_DOC_PATH.resolve().as_posix().lower(),
    }
    return [
        path
        for path in _unique_paths(candidates)
        if path.resolve().as_posix().lower() not in excluded
    ]


def build_claim_language_guard_rows(
    *,
    scan_paths: Sequence[str | Path] | None = None,
    context_window: int = 2,
    project_root: str | Path = PROJECT_ROOT,
) -> list[dict[str, str]]:
    """Return fail-closed line-level reserved-language findings."""

    root = Path(project_root)
    paths = (
        [Path(path) for path in scan_paths]
        if scan_paths is not None
        else default_claim_language_scan_paths(project_root=root)
    )
    rows: list[dict[str, str]] = []
    for path in _unique_paths(paths):
        rows.extend(_scan_path(path, project_root=root, context_window=context_window))
    for index, row in enumerate(rows, start=1):
        row["finding_id"] = f"claim_language_{index:04d}"
    return rows


def write_claim_language_guard(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_CLAIM_LANGUAGE_GUARD_PATH,
    manifest_path: str | Path = DEFAULT_CLAIM_LANGUAGE_GUARD_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_CLAIM_LANGUAGE_GUARD_DOC_PATH,
    scan_paths: Sequence[str | Path] | None = None,
) -> dict[str, Any]:
    """Write CSV, manifest, and Markdown claim-language guard artifacts."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CLAIM_LANGUAGE_GUARD_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in CLAIM_LANGUAGE_GUARD_COLUMNS
                }
            )
    summary = build_claim_language_guard_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        scan_paths=scan_paths,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_claim_language_guard_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def summarize_claim_language_guard(
    *,
    manifest_path: str | Path = DEFAULT_CLAIM_LANGUAGE_GUARD_MANIFEST_PATH,
) -> dict[str, Any]:
    """Load an existing claim-language guard manifest conservatively."""

    path = Path(manifest_path)
    if not path.exists():
        return {
            "manifest_present": False,
            "row_count": 0,
        "blocking_finding_count": 1,
        "bounded_finding_count": 0,
        "explicit_non_approval_count": 0,
        "formal_evidence_backed_count": 0,
        "bounded_non_claim_reference_count": 0,
        "scan_complete": False,
        "release_blocked": True,
        "claims_approved": False,
        "formal_acceptance_created": False,
        "claim_language_guard_ready": False,
        "publication_ready": False,
        "final_study_ready": False,
        "can_mark_complete": False,
            "remaining_blockers": [
                f"{_display_path(path)} is missing; lexical claim-language guard has not run"
            ],
            "claim_boundary": CLAIM_LANGUAGE_GUARD_SCOPE,
        }
    value = json.loads(path.read_text(encoding="utf-8"))
    value["manifest_present"] = True
    value.setdefault("claim_language_guard_ready", False)
    value.setdefault("publication_ready", False)
    value.setdefault("final_study_ready", False)
    value.setdefault("can_mark_complete", False)
    return value


def build_claim_language_guard_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_CLAIM_LANGUAGE_GUARD_PATH,
    manifest_path: str | Path = DEFAULT_CLAIM_LANGUAGE_GUARD_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_CLAIM_LANGUAGE_GUARD_DOC_PATH,
    scan_paths: Sequence[str | Path] | None = None,
) -> dict[str, Any]:
    """Return a conservative manifest for lexical claim-language findings."""

    status_counts = _counts(row.get("status", "") for row in rows)
    term_counts = _counts(row.get("term", "") for row in rows)
    source_counts = _counts(row.get("source_path", "") for row in rows)
    structural_blocking_rows = [
        row
        for row in rows
        if row.get("status")
        in {
            "missing_scan_target",
            "invalid_json_target",
            "unsupported_scan_target",
            "empty_scan_inventory",
        }
    ]
    release_blocking_rows = [
        row for row in rows if row.get("status") == "release_blocking_unbounded"
    ]
    blocking_rows = [*structural_blocking_rows, *release_blocking_rows]
    explicit_non_approval_count = sum(
        1 for row in rows if row.get("status") == "explicit_non_approval"
    )
    formal_evidence_backed_count = sum(
        1 for row in rows if row.get("status") == "formal_evidence_backed"
    )
    bounded_non_claim_reference_count = sum(
        1
        for row in rows
        if row.get("status") == BOUNDED_NON_CLAIM_REFERENCE_STATUS
    )
    bounded_count = (
        explicit_non_approval_count
        + formal_evidence_backed_count
        + bounded_non_claim_reference_count
    )
    scan_display = [
        _display_path(Path(path))
        for path in (
            scan_paths
            if scan_paths is not None
            else default_claim_language_scan_paths()
        )
    ]
    if not scan_display:
        structural_blocking_rows.append(
            {
                "source_path": "<scan_inventory>",
                "line_number": "0",
                "term": "empty",
            }
        )
        blocking_rows.append(structural_blocking_rows[-1])
    scan_complete = not structural_blocking_rows
    return {
        "schema_version": 1,
        "claim_boundary": CLAIM_LANGUAGE_GUARD_SCOPE,
        "result_scope": CLAIM_LANGUAGE_GUARD_SCOPE,
        "manifest_present": True,
        "scan_complete": scan_complete,
        "release_blocked": bool(blocking_rows),
        "claims_approved": False,
        "formal_acceptance_created": False,
        "target_file_count": len(scan_display),
        "scanned_file_count": len(
            {
                row.get("source_path", "")
                for row in rows
                if row.get("status")
                not in {
                    "missing_scan_target",
                    "invalid_json_target",
                    "unsupported_scan_target",
                    "empty_scan_inventory",
                }
            }
        ),
        "missing_target_count": sum(
            1 for row in rows if row.get("status") == "missing_scan_target"
        ),
        "unreadable_target_count": sum(
            1 for row in rows if row.get("status") == "invalid_json_target"
        ),
        "row_count": len(rows),
        "reserved_match_count": len(rows),
        "blocking_finding_count": len(blocking_rows),
        "bounded_finding_count": bounded_count,
        "explicit_non_approval_count": explicit_non_approval_count,
        "formal_evidence_backed_count": formal_evidence_backed_count,
        "bounded_non_claim_reference_count": bounded_non_claim_reference_count,
        "status_counts": status_counts,
        "term_counts": term_counts,
        "source_counts": source_counts,
        "claim_language_guard_ready": scan_complete and len(blocking_rows) == 0,
        "publication_ready": False,
        "final_study_ready": False,
        "can_mark_complete": False,
        "inputs": {"scan_paths": scan_display},
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": [
            "downgrade unbounded final, ready, accepted, validated, calibrated, operational, forecast, real-time, and approved language",
            "preserve explicit non-approval and decision-support boundary language",
            "rerun this guard before public/package/report release",
        ],
        "remaining_blockers": [
            f"{row.get('source_path')}:{row.get('line_number')} {row.get('term')} requires boundary review"
            for row in blocking_rows[:50]
        ]
        + (
            [f"{len(blocking_rows) - 50} additional blocking claim-language findings"]
            if len(blocking_rows) > 50
            else []
        ),
    }


def build_claim_language_guard_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return a human-readable claim-language guard report."""

    lines = [
        "# Claim Language Guard",
        "",
        str(manifest.get("claim_boundary", CLAIM_LANGUAGE_GUARD_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Claim-language guard ready: `{str(manifest.get('claim_language_guard_ready', False)).lower()}`",
        f"- Release blocked: `{str(manifest.get('release_blocked', True)).lower()}`",
        f"- Claims approved: `{str(manifest.get('claims_approved', False)).lower()}`",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Final-study ready: `{str(manifest.get('final_study_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Findings: {manifest.get('row_count', 0)}",
        f"- Blocking findings: {manifest.get('blocking_finding_count', 0)}",
        f"- Bounded guardrail findings: {manifest.get('bounded_finding_count', 0)}",
        "",
        "## Findings",
        "",
        "| ID | Source | Term | Status | Required Action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows[:120]:
        lines.append(
            "| {finding} | {source}:{line} | {term} | {status} | {action} |".format(
                finding=_cell(row.get("finding_id", "")),
                source=_cell(row.get("source_path", "")),
                line=_cell(row.get("line_number", "")),
                term=_cell(row.get("term", "")),
                status=_cell(row.get("status", "")),
                action=_cell(row.get("required_action", "")),
            )
        )
    if len(rows) > 120:
        lines.append(
            f"| ... | ... | ... | ... | {len(rows) - 120} additional rows in CSV |"
        )
    lines.extend(
        [
            "",
            "## Required Use",
            "",
            "- Treat every `release_blocking_unbounded` row as a wording or evidence blocker.",
            "- Treat `explicit_non_approval` and `formal_evidence_backed` rows as reviewable boundary language, not approval.",
            "- Do not use this guard as formal acceptance or final-study approval.",
            "",
        ]
    )
    return "\n".join(lines)


def _scan_path(path: Path, *, project_root: Path, context_window: int) -> list[dict[str, str]]:
    if not path.exists():
        return [
            _row(
                source_path=path,
                project_root=project_root,
                line_number=0,
                term="missing",
                status="missing_scan_target",
                evidence_context="",
                excerpt="",
                required_action="restore scan target or remove it from claim-language guard scope with rationale",
            )
        ]
    if path.suffix.lower() not in {".md", ".json"}:
        return [
            _row(
                source_path=path,
                project_root=project_root,
                line_number=0,
                term=path.suffix.lower() or "unsupported",
                status="unsupported_scan_target",
                evidence_context="",
                excerpt="",
                required_action="remove unsupported scan target or add a parser before using it for claim-language guard evidence",
            )
        ]
    text = path.read_text(encoding="utf-8", errors="replace")
    json_value: object | None = None
    if path.suffix.lower() == ".json":
        try:
            json_value = json.loads(text)
        except json.JSONDecodeError as exc:
            return [
                _row(
                    source_path=path,
                    project_root=project_root,
                    line_number=exc.lineno,
                    term="invalid_json",
                    status="invalid_json_target",
                    evidence_context="",
                    excerpt=str(exc),
                    required_action="repair invalid JSON before claim-language guard can scan manifest text",
                )
            ]
    lines = text.splitlines()
    rows: list[dict[str, str]] = []
    in_fail_closed_phase_gate_ledger = _is_fail_closed_phase_gate_ledger(
        json_value,
    )
    in_fenced_code = False
    in_json_non_approval_inventory_depth = 0
    in_markdown_non_approval_inventory = False
    for index, line in enumerate(lines):
        if line.strip().startswith("```"):
            in_fenced_code = not in_fenced_code
            continue
        if path.suffix.lower() == ".md" and line.lstrip().startswith("#"):
            in_markdown_non_approval_inventory = _is_non_approval_markdown_section(
                line
            )
        in_json_non_approval_inventory = in_json_non_approval_inventory_depth > 0
        if path.suffix.lower() == ".json" and _starts_non_approval_json_inventory(
            line
        ):
            in_json_non_approval_inventory = True
        matches = _reserved_term_matches(line)
        if not matches:
            if path.suffix.lower() == ".json":
                in_json_non_approval_inventory_depth = (
                    _next_json_inventory_depth(
                        line,
                        in_json_non_approval_inventory_depth,
                    )
                )
            continue
        context = _context(lines, index, window=context_window)
        terms: dict[str, list[tuple[int, int]]] = {}
        for term, span in matches:
            terms.setdefault(term, []).append(span)
        for term, spans in terms.items():
            status = _classify_term(
                term,
                line=line,
                context=context,
                spans=spans,
                in_fenced_code=in_fenced_code,
                in_non_approval_inventory=(
                    in_json_non_approval_inventory
                    or in_markdown_non_approval_inventory
                ),
                in_fail_closed_phase_gate_ledger=(
                    in_fail_closed_phase_gate_ledger
                ),
            )
            rows.append(
                _row(
                    source_path=path,
                    project_root=project_root,
                    line_number=index + 1,
                    term=term,
                    status=status,
                    evidence_context=_excerpt(context, limit=300),
                    excerpt=_excerpt(line),
                    required_action=(
                        "verify this formal evidence reference actually supports the claim"
                        if status == "formal_evidence_backed"
                        else "verify this non-approval boundary remains accurate and does not imply approval"
                        if status == "explicit_non_approval"
                        else "verify this literal code/path reference remains non-claim-bearing"
                        if status == BOUNDED_NON_CLAIM_REFERENCE_STATUS
                        else "downgrade wording or add formal evidence-backed non-approval boundary before release"
                    ),
                )
            )
        if path.suffix.lower() == ".json":
            in_json_non_approval_inventory_depth = _next_json_inventory_depth(
                line,
                in_json_non_approval_inventory_depth,
            )
    return rows


def _row(
    *,
    source_path: Path,
    project_root: Path,
    line_number: int,
    term: str,
    status: str,
    evidence_context: str,
    excerpt: str,
    required_action: str,
) -> dict[str, str]:
    return {
        "finding_id": "",
        "source_path": _display_path(source_path, project_root=project_root),
        "line_number": str(line_number),
        "term": term,
        "status": status,
        "evidence_context": evidence_context,
        "excerpt": excerpt,
        "required_action": required_action,
        "can_support_release": "false",
        "claim_boundary": CLAIM_LANGUAGE_GUARD_SCOPE,
    }


def _reserved_terms(line: str) -> list[str]:
    return [term for term, _span in _reserved_term_matches(line)]


def _reserved_term_matches(line: str) -> list[tuple[str, tuple[int, int]]]:
    found: list[tuple[str, tuple[int, int]]] = []
    for term, pattern in RESERVED_TERM_PATTERNS:
        for match in pattern.finditer(line):
            found.append((term, match.span()))
    return sorted(found, key=lambda item: item[1])


def _classify_term(
    term: str,
    *,
    line: str,
    context: str,
    spans: Sequence[tuple[int, int]] | None = None,
    in_fenced_code: bool = False,
    in_non_approval_inventory: bool = False,
    in_fail_closed_phase_gate_ledger: bool = False,
) -> str:
    if in_non_approval_inventory:
        return "explicit_non_approval"
    if (
        in_fail_closed_phase_gate_ledger
        and _is_bounded_phase_gate_ledger_line(term, line)
    ):
        return "explicit_non_approval"
    if _has_explicit_non_approval_context(term, line, context):
        return "explicit_non_approval"
    if spans and _all_spans_are_bounded_non_claim_references(
        line=line,
        context=context,
        spans=spans,
        in_fenced_code=in_fenced_code,
    ):
        return BOUNDED_NON_CLAIM_REFERENCE_STATUS
    if _has_formal_evidence_context(term, line):
        return "formal_evidence_backed"
    return "release_blocking_unbounded"


def _starts_non_approval_json_inventory(line: str) -> bool:
    return bool(
        re.search(
            r'"(?:remaining_blockers|missing_or_weak_requirements|proxy_signals_rejected)"\s*:\s*\[',
            line,
        )
    )


def _next_json_inventory_depth(line: str, current_depth: int) -> int:
    starts_inventory = _starts_non_approval_json_inventory(line)
    if current_depth <= 0 and not starts_inventory:
        return 0
    depth = current_depth
    if starts_inventory:
        depth = 0
    depth += line.count("[")
    depth -= line.count("]")
    return max(depth, 0)


def _is_non_approval_markdown_section(line: str) -> bool:
    heading = line.lstrip("#").strip().lower()
    return any(
        marker in heading
        for marker in (
            "remaining blocker",
            "missing or weak requirement",
            "proxy signals rejected",
        )
    )


def _is_fail_closed_phase_gate_ledger(value: object | None) -> bool:
    if not isinstance(value, Mapping):
        return False
    claim_boundary = str(value.get("claim_boundary", "")).lower()
    return (
        "phase-gate ledger control only" in claim_boundary
        and "do not close phases" in claim_boundary
        and value.get("can_mark_complete") is False
        and value.get("final_study_ready") is False
    )


def _is_bounded_phase_gate_ledger_line(term: str, line: str) -> bool:
    scan = line.lower()
    field_markers = (
        '"can_mark_complete"',
        '"claim_boundary"',
        '"command"',
        '"decision_authority"',
        '"dependency_status"',
        '"final_study_ready"',
        '"gate_decision"',
        '"parallelism_mode"',
        '"review_scope"',
        '"role"',
        '"status"',
        '"sub_agents"',
        '"synthesis_barrier"',
    )
    if any(marker in scan for marker in field_markers):
        return True
    if "gpt-5.5-xhigh" in scan and any(
        marker in scan for marker in ("review", "reviewer", "scout")
    ):
        return True
    aliases = _term_aliases(term)
    if not any(alias in scan for alias in aliases):
        return False
    bounded_markers = (
        "blocked",
        "before",
        "do not",
        "does not",
        "missing",
        "not ",
        "only",
        "proxy",
        "rejected",
        "remain",
        "requires",
        "review",
        "reviewer",
        "support",
        "traceability",
    )
    return any(marker in scan for marker in bounded_markers)


def _all_spans_are_bounded_non_claim_references(
    *,
    line: str,
    context: str,
    spans: Sequence[tuple[int, int]],
    in_fenced_code: bool,
) -> bool:
    literal_ranges = _literal_reference_ranges(line, in_fenced_code=in_fenced_code)
    vocabulary_ranges = _guard_vocabulary_ranges(line, context)
    fenced_inventory_ranges = (
        _fenced_inventory_allowed_reserved_ranges(line) if in_fenced_code else []
    )
    reference_ranges = [*literal_ranges, *vocabulary_ranges, *fenced_inventory_ranges]
    return bool(reference_ranges) and all(
        _span_is_inside_any(span, reference_ranges) for span in spans
    )


def _literal_reference_ranges(
    line: str,
    *,
    in_fenced_code: bool,
) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    for match in re.finditer(r"`([^`]+)`", line):
        if _is_literal_reference(match.group(1)):
            ranges.append(match.span())
    ranges.extend(_bare_literal_reference_ranges(line))
    return _merge_ranges(ranges)


def _bare_literal_reference_ranges(line: str) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    token_pattern = re.compile(
        r"(?<![A-Za-z0-9_./\\-])"
        r"[A-Za-z0-9_.\\/-]*(?:"
        r"\.(?:py|json|jsonl|csv|md|yaml|yml|txt|graphml|gpkg)"
        r"|[/\\]"
        r")[A-Za-z0-9_.\\/-]*"
    )
    for match in token_pattern.finditer(line):
        text = match.group(0).strip("`'\".,;:()[]{}")
        if _is_literal_reference(text):
            start = match.start() + match.group(0).find(text)
            ranges.append((start, start + len(text)))
    return ranges


def _is_literal_reference(text: str) -> bool:
    value = text.strip().strip("`'\"")
    if not value or " " in value:
        return False
    if value in {"final", "ready", "validated", "approved", "accepted"}:
        return False
    if re.search(r"\.(py|json|jsonl|csv|md|yaml|yml|txt|graphml|gpkg)$", value):
        return True
    if "/" in value or "\\" in value:
        return True
    return False


def _fenced_inventory_allowed_reserved_ranges(line: str) -> list[tuple[int, int]]:
    if not _is_fenced_inventory_line(line):
        return []
    allowed_terms = {"accepted", "final", "ready", "validated"}
    ranges: list[tuple[int, int]] = []
    for term, pattern in RESERVED_TERM_PATTERNS:
        if term not in allowed_terms:
            continue
        ranges.extend(match.span() for match in pattern.finditer(line))
    return _merge_ranges(ranges)


def _is_fenced_inventory_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith(("#", "//")):
        return False
    token = stripped.split(maxsplit=1)[0].strip("`'\".,;:()[]{}")
    return _is_literal_reference(token)


def _guard_vocabulary_ranges(line: str, context: str) -> list[tuple[int, int]]:
    scan = f"{context} {line}".lower()
    if not (
        "reserved for evidence-backed contexts" in scan
        or "reserved claim" in scan
        or "reserved terms" in scan
        or "reserved-word list" in scan
    ):
        return []
    ranges: list[tuple[int, int]] = []
    for match in re.finditer(r"`([^`]+)`", line):
        value = match.group(1).strip().lower()
        if value in {
            "accepted",
            "final",
            "ready",
            "validated",
            "calibrated",
            "operational",
            "forecast",
            "real-time",
            "approved",
        }:
            ranges.append(match.span())
    return ranges


def _span_is_inside_any(
    span: tuple[int, int],
    ranges: Sequence[tuple[int, int]],
) -> bool:
    return any(start <= span[0] and span[1] <= end for start, end in ranges)


def _merge_ranges(ranges: Sequence[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[tuple[int, int]] = []
    for start, end in sorted(ranges):
        if not merged or start > merged[-1][1]:
            merged.append((start, end))
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
    return merged


def _has_formal_evidence_context(term: str, context: str) -> bool:
    scan = context.lower()
    return (
        term in scan
        and "formal" in scan
        and (
            "acceptance" in scan
            or "reviewer" in scan
            or "evidence" in scan
            or "manifest" in scan
        )
        and not any(negative in scan for negative in ("absent", "missing", "blocked", "false"))
    )


def _has_explicit_non_approval_context(term: str, line: str, context: str) -> bool:
    line_scan = line.lower()
    if _term_has_boundary_in_clause(term, line_scan):
        return True
    context_scan = context.lower()
    if _term_has_wrapped_boundary_in_neighbor_clause(term, line_scan, context_scan):
        return True
    if _term_has_false_field_boundary(term, line_scan):
        return True
    return False


def _term_aliases(term: str) -> tuple[str, ...]:
    return {
        "accepted": (
            "accept",
            "accepted",
            "accepting",
            "accepts",
            "acceptance",
            "approval",
            "approved",
        ),
        "approved": (
            "approve",
            "approves",
            "approved",
            "approving",
            "approval",
            "accepted",
            "acceptance",
        ),
        "validated": ("validate", "validates", "validated", "validating", "validation"),
        "calibrated": ("calibrate", "calibrates", "calibrated", "calibrating", "calibration"),
        "final": ("final", "final-study", "final study"),
        "ready": ("ready", "readiness"),
        "operational": ("operational", "operation"),
        "forecast": ("forecast",),
        "real-time": ("real-time", "real time"),
    }.get(term, (term,))


def _term_has_boundary_in_clause(term: str, line_scan: str) -> bool:
    aliases = _term_aliases(term)
    clauses = re.split(r";|\.\s+|,\s+but\s+|\s+but\s+|\s+however\s+", line_scan)
    markers = (
        "not",
        "no ",
        "non-",
        "blocked",
        "blocker",
        "blockers",
        "false",
        "absent",
        "missing",
        "lacks",
        "pending",
        "must not",
        "do not",
        "does not",
        "doesn't",
        "did not",
        "didn't",
        "will not",
        "won't",
        "isn't",
        "aren't",
        "wasn't",
        "weren't",
        "hasn't",
        "haven't",
        "cannot",
        "can't",
        "without",
        "never",
    )
    return any(
        any(alias in clause for alias in aliases)
        and any(marker in clause for marker in markers)
        for clause in clauses
    )


def _term_has_false_field_boundary(term: str, context_scan: str) -> bool:
    term_aliases = _term_aliases(term)
    false_field_patterns = (
        r"\b(can_mark_complete|final_study_ready|publication_ready|accepted|approved|validated|calibrated|operational|forecast)\b.{0,40}\b(false|0)\b",
        r"\b(false|0)\b.{0,40}\b(can_mark_complete|final_study_ready|publication_ready|accepted|approved|validated|calibrated|operational|forecast)\b",
    )
    return any(alias in context_scan for alias in term_aliases) and any(
        re.search(pattern, context_scan) for pattern in false_field_patterns
    )


def _term_has_wrapped_boundary_in_neighbor_clause(
    term: str,
    line_scan: str,
    context_scan: str,
) -> bool:
    context_lines = context_scan.splitlines()
    if not context_lines:
        return False
    matches = [
        index
        for index, context_line in enumerate(context_lines)
        if context_line.strip() == line_scan.strip()
    ]
    for index in matches:
        if index > 0 and _line_wraps_into_next(context_lines[index - 1]):
            if _term_has_boundary_in_clause(
                term,
                f"{context_lines[index - 1]} {context_lines[index]}",
            ):
                return True
        if index + 1 < len(context_lines) and _line_wraps_into_next(context_lines[index]):
            if _term_has_boundary_in_clause(
                term,
                f"{context_lines[index]} {context_lines[index + 1]}",
            ):
                return True
    return False


def _line_wraps_into_next(line_scan: str) -> bool:
    stripped = line_scan.strip()
    if not stripped:
        return False
    if stripped.startswith("`") and stripped.endswith("`"):
        return False
    return not stripped.endswith((".", ";", ":", "!", "?"))


def _context(lines: Sequence[str], index: int, *, window: int) -> str:
    start = max(0, index - window)
    end = min(len(lines), index + window + 1)
    return "\n".join(lines[start:end])


def _unique_paths(paths: Iterable[Path]) -> list[Path]:
    unique: dict[str, Path] = {}
    for path in paths:
        try:
            key = str(path.resolve()).lower()
        except OSError:
            key = str(path).lower()
        unique.setdefault(key, path)
    return list(unique.values())


def _counts(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _excerpt(text: object, *, limit: int = 240) -> str:
    return " ".join(str(text).strip().split())[:limit]


def _display_path(path: Path, *, project_root: Path = PROJECT_ROOT) -> str:
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


__all__ = [
    "CLAIM_LANGUAGE_GUARD_COLUMNS",
    "CLAIM_LANGUAGE_GUARD_SCOPE",
    "DEFAULT_CLAIM_LANGUAGE_GUARD_DOC_PATH",
    "DEFAULT_CLAIM_LANGUAGE_GUARD_MANIFEST_PATH",
    "DEFAULT_CLAIM_LANGUAGE_GUARD_PATH",
    "build_claim_language_guard_manifest",
    "build_claim_language_guard_markdown",
    "build_claim_language_guard_rows",
    "default_claim_language_scan_paths",
    "summarize_claim_language_guard",
    "write_claim_language_guard",
]
