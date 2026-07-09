"""Tests for non-approval formal acceptance decision templates."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.acceptance_decision_templates import (  # noqa: E402
    TEMPLATE_CLAIM_BOUNDARY,
    build_acceptance_decision_template_specs,
    build_parameter_acceptance_template_rows,
    write_acceptance_decision_templates,
)
from src.realworld.parameter_acceptance import summarize_parameter_acceptance  # noqa: E402
from src.realworld.pilot_acceptance import summarize_pilot_acceptance  # noqa: E402


def test_acceptance_decision_templates_are_non_approval() -> None:
    specs = build_acceptance_decision_template_specs()

    assert len(specs) == 9
    assert {spec.gate_id for spec in specs} >= {
        "pilot_region_accepted",
        "graph_scale_strategy",
        "data_provenance",
        "validation_package",
        "sensitivity_analysis",
        "full_experiment_output",
        "manuscript_report_alignment",
        "reproducibility",
        "final_audit",
    }
    for spec in specs:
        assert spec.template["accepted"] is False
        assert spec.template["template_only"] is True
        assert "TEMPLATE ONLY" in str(spec.template["claim_boundary"])

    print("PASS: acceptance decision templates are non-approval")


def test_parameter_acceptance_template_rows_stay_unaccepted() -> None:
    rows = build_parameter_acceptance_template_rows()

    assert not rows

    print("PASS: parameter acceptance template rows stay unaccepted")


def test_write_acceptance_decision_templates_outputs_non_ready_files() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        manifest = write_acceptance_decision_templates(
            template_dir=root / "templates",
            manifest_path=root / "manifest.json",
            doc_path=root / "templates.md",
            parameter_template_path=root / "parameter_acceptance_template.csv",
        )

        # Templates are non-approval scaffolding; the study is NOT final-ready.
        assert manifest["final_study_ready"] is False
        assert manifest["can_mark_complete"] is False
        assert manifest["formal_acceptance_created"] is False
        assert manifest["json_template_count"] == 9
        assert manifest["parameter_template_row_count"] >= 0
        assert (root / "manifest.json").exists()
        assert (root / "templates.md").exists()

        pilot_template = root / "templates" / "pilot_acceptance_template.json"
        pilot_summary = summarize_pilot_acceptance(pilot_template)
        assert pilot_summary["record_present"] is True
        assert pilot_summary["acceptance_ready"] is False

        parameter_csv = root / "parameter_acceptance_template.csv"
        if parameter_csv.exists() and parameter_csv.stat().st_size > 0:
            with parameter_csv.open("r", encoding="utf-8") as fh:
                non_empty = any(line.strip() and not line.startswith("parameter") for line in fh)
        else:
            non_empty = False
        if non_empty:
            parameter_summary = summarize_parameter_acceptance(parameter_csv)
            assert parameter_summary["ready_parameter_count"] == 0

        with (root / "manifest.json").open("r", encoding="utf-8") as handle:
            reloaded = json.load(handle)
        assert reloaded["claim_boundary"] == TEMPLATE_CLAIM_BOUNDARY

    print("PASS: acceptance decision templates write non-ready files")


def test_write_acceptance_decision_templates_preserves_timestamp_when_unchanged() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        manifest_path = root / "manifest.json"
        write_acceptance_decision_templates(
            template_dir=root / "templates",
            manifest_path=manifest_path,
            doc_path=root / "templates.md",
            parameter_template_path=root / "parameter_acceptance_template.csv",
        )
        first = json.loads(manifest_path.read_text(encoding="utf-8"))
        first["generated_at"] = "2000-01-01T00:00:00+00:00"
        manifest_path.write_text(
            json.dumps(first, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        value = write_acceptance_decision_templates(
            template_dir=root / "templates",
            manifest_path=manifest_path,
            doc_path=root / "templates.md",
            parameter_template_path=root / "parameter_acceptance_template.csv",
        )
        loaded = json.loads(manifest_path.read_text(encoding="utf-8"))

        assert value["generated_at"] == "2000-01-01T00:00:00+00:00"
        assert loaded["generated_at"] == "2000-01-01T00:00:00+00:00"


if __name__ == "__main__":
    test_acceptance_decision_templates_are_non_approval()
    test_parameter_acceptance_template_rows_stay_unaccepted()
    test_write_acceptance_decision_templates_outputs_non_ready_files()
    test_write_acceptance_decision_templates_preserves_timestamp_when_unchanged()
    print("\n=== REALWORLD ACCEPTANCE DECISION TEMPLATE TESTS PASSED ===")
