"""Write a phase-scoped runtime preflight manifest.

This script records environment, package, git, dirty-worktree, and optional GPU
runtime context before compact/full/benchmark/ML runs. It does not run the
simulation and does not close readiness gates.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.runtime_preflight import (  # noqa: E402
    DEFAULT_PACKAGE_SPECS,
    DEFAULT_REQUIREMENTS_PATHS,
    write_runtime_preflight_manifest,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    actual_argv = list(sys.argv[1:] if argv is None else argv)
    args = _parse_args(actual_argv)
    command = [str(Path(__file__).relative_to(ROOT)), *actual_argv]
    package_specs = tuple(args.package) if args.package else DEFAULT_PACKAGE_SPECS
    requirements = tuple(args.requirements) if args.requirements else DEFAULT_REQUIREMENTS_PATHS
    manifest = write_runtime_preflight_manifest(
        phase_id=args.phase_id,
        execution_scope=args.execution_scope,
        package_specs=package_specs,
        requirements_paths=requirements,
        dirty_manifest_path=args.dirty_manifest,
        include_gpu=args.include_gpu,
        gpu_smoke_command=args.gpu_smoke_command,
        analysis_command=args.analysis_command,
        command=command,
        cwd=ROOT,
        output_manifest_path=args.manifest,
        output_log_path=args.log,
        output_doc_path=args.doc,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    if args.fail_on_blockers and manifest["remaining_blockers"]:
        return 1
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--phase-id",
        required=True,
        help="Phase-scoped identifier for this runtime preflight.",
    )
    parser.add_argument(
        "--execution-scope",
        default="cpu",
        choices=["cpu", "micro_probe", "compact", "full", "benchmark", "gpu_ml"],
        help="Run scope that this preflight supports.",
    )
    parser.add_argument(
        "--package",
        action="append",
        default=[],
        help=(
            "Package to version/import check. Use 'distribution' or "
            "'distribution:import_name'. May be repeated. Defaults to core "
            "requirements.txt packages."
        ),
    )
    parser.add_argument(
        "--requirements",
        action="append",
        type=Path,
        default=[],
        help="Requirements file to hash. May be repeated.",
    )
    parser.add_argument(
        "--dirty-manifest",
        type=Path,
        default=ROOT / "data" / "validation" / "dirty_worktree_classification_manifest.json",
        help="Dirty-worktree classification manifest to hash and summarize.",
    )
    parser.add_argument(
        "--include-gpu",
        action="store_true",
        help="Collect nvidia-smi and require GPU smoke command metadata.",
    )
    parser.add_argument(
        "--gpu-smoke-command",
        default="",
        help="Exact GPU smoke command associated with this phase, if GPU is in scope.",
    )
    parser.add_argument(
        "--analysis-command",
        default="",
        help="Exact downstream analysis/run command this preflight is intended to support.",
    )
    parser.add_argument("--manifest", type=Path, default=None, help="Output JSON path.")
    parser.add_argument("--log", type=Path, default=None, help="Output JSONL path.")
    parser.add_argument("--doc", type=Path, default=None, help="Output Markdown path.")
    parser.add_argument(
        "--fail-on-blockers",
        action="store_true",
        help="Return exit code 1 when the preflight has runtime blockers.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
