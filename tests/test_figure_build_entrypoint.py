"""Focused guards for the paper-figure build entry point."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "paper" / "figures" / "_build" / "build_all_figures.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("build_all_figures_for_test", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_default_build_excludes_user_generated_fig1() -> None:
    module = _load_module()
    assert module.DEFAULT_ANALYSIS_DIR.as_posix() == (
        "results/paper_revision_top10_corridor_v4_20260721/analysis/full"
    )
    calls: list[str] = []
    originals = {}
    names = (
        "fig1_framework",
        "fig2_map",
        "fig3_graph_scope",
        "fig4_paired_results",
        "fig5_decision_boundary",
        "fig6_resource_adaptive",
    )
    for number, name in enumerate(names, start=1):
        originals[name] = getattr(module, name)
        if number <= 2:
            setattr(module, name, lambda *, output_dir, n=number: calls.append(f"fig{n}"))
        else:
            setattr(
                module,
                name,
                lambda _data, *, output_dir, n=number: calls.append(f"fig{n}"),
            )
    try:
        module.build_figures(revision_data=object())
    finally:
        for name, value in originals.items():
            setattr(module, name, value)
    assert calls == ["fig2", "fig3", "fig4", "fig5", "fig6"], calls


def test_vector_fig1_requires_explicit_opt_in() -> None:
    module = _load_module()
    calls: list[str] = []
    originals = {}
    names = (
        "fig1_framework",
        "fig2_map",
        "fig3_graph_scope",
        "fig4_paired_results",
        "fig5_decision_boundary",
        "fig6_resource_adaptive",
    )
    for number, name in enumerate(names, start=1):
        originals[name] = getattr(module, name)
        if number <= 2:
            setattr(module, name, lambda *, output_dir, n=number: calls.append(f"fig{n}"))
        else:
            setattr(
                module,
                name,
                lambda _data, *, output_dir, n=number: calls.append(f"fig{n}"),
            )
    try:
        module.build_figures(include_vector_fig1=True, revision_data=object())
    finally:
        for name, value in originals.items():
            setattr(module, name, value)
    assert calls == ["fig1", "fig2", "fig3", "fig4", "fig5", "fig6"], calls


def test_output_dir_reaches_every_figure_entrypoint() -> None:
    module = _load_module()
    calls: list[tuple[str, Path]] = []
    originals = {}
    names = (
        "fig1_framework",
        "fig2_map",
        "fig3_graph_scope",
        "fig4_paired_results",
        "fig5_decision_boundary",
        "fig6_resource_adaptive",
    )
    for number, name in enumerate(names, start=1):
        originals[name] = getattr(module, name)
        if number <= 2:
            setattr(
                module,
                name,
                lambda *, output_dir, n=number: calls.append((f"fig{n}", Path(output_dir))),
            )
        else:
            setattr(
                module,
                name,
                lambda _data, *, output_dir, n=number: calls.append((f"fig{n}", Path(output_dir))),
            )
    output_dir = ROOT / "paper" / "figures" / "_build" / "entrypoint-test-output"
    try:
        module.build_figures(
            include_vector_fig1=True,
            revision_data=object(),
            output_dir=output_dir,
        )
    finally:
        for name, value in originals.items():
            setattr(module, name, value)
    assert calls == [(f"fig{number}", output_dir) for number in range(1, 7)], calls


def main() -> int:
    test_default_build_excludes_user_generated_fig1()
    print("PASS: default figure build preserves generated fig1")
    test_vector_fig1_requires_explicit_opt_in()
    print("PASS: vector fig1 requires opt-in")
    test_output_dir_reaches_every_figure_entrypoint()
    print("PASS: output directory reaches every figure entrypoint")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
