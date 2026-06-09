"""Check optional GPU-backed ML runtime evidence.

This script writes non-acceptance runtime evidence only. It can support a
bounded GPU-backed ML post-analysis claim only when a package-specific GPU
operation and CPU fallback both pass. It does not prove the simulator is GPU
accelerated.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.gpu_ml_runtime import (  # noqa: E402
    DEFAULT_GPU_ML_RUNTIME_DOC,
    DEFAULT_GPU_ML_RUNTIME_LOG,
    DEFAULT_GPU_ML_RUNTIME_MANIFEST,
    DEFAULT_GPU_PACKAGES,
    check_gpu_ml_runtime,
    write_gpu_ml_runtime_outputs,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    actual_argv = list(sys.argv[1:] if argv is None else argv)
    args = _parse_args(actual_argv)
    packages = tuple(args.package) if args.package else DEFAULT_GPU_PACKAGES
    command = [str(Path(__file__).relative_to(ROOT)), *actual_argv]
    manifest = check_gpu_ml_runtime(
        packages=packages,
        requested_device=args.requested_device,
        run_fit=not args.import_only,
        nvidia_smi_command=tuple(args.nvidia_smi_command),
        requirements_path=args.requirements,
        output_manifest_path=args.manifest,
        output_log_path=args.log,
        output_doc_path=args.doc,
        command=command,
        cwd=ROOT,
    )
    written = write_gpu_ml_runtime_outputs(
        manifest=manifest,
        manifest_path=args.manifest,
        log_path=args.log,
        doc_path=args.doc,
    )
    print(json.dumps(written, indent=2, sort_keys=True))
    if args.fail_on_blockers and written["remaining_blockers"]:
        return 1
    if args.require_gpu and not written["can_support_gpu_ml_claim"]:
        return 1
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--package",
        action="append",
        default=[],
        help=(
            "Optional ML package to check. May be repeated. Defaults to xgboost. "
            "Supported package-specific checks: xgboost, torch, cupy."
        ),
    )
    parser.add_argument(
        "--requested-device",
        default="cuda",
        help="Requested accelerator device string passed to supported packages.",
    )
    parser.add_argument(
        "--import-only",
        action="store_true",
        help="Only check imports and versions; this cannot support a GPU ML claim.",
    )
    parser.add_argument(
        "--require-gpu",
        action="store_true",
        help="Return exit code 1 unless the manifest can support a GPU ML claim.",
    )
    parser.add_argument(
        "--fail-on-blockers",
        action="store_true",
        help="Return exit code 1 if any runtime blocker remains.",
    )
    parser.add_argument(
        "--nvidia-smi-command",
        nargs="+",
        default=["nvidia-smi"],
        help="Command used to collect GPU driver evidence.",
    )
    parser.add_argument(
        "--requirements",
        type=Path,
        default=ROOT / "requirements.txt",
        help="Requirements file to hash in the manifest.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_GPU_ML_RUNTIME_MANIFEST,
        help="Output JSON manifest path.",
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=DEFAULT_GPU_ML_RUNTIME_LOG,
        help="Output JSONL log path.",
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_GPU_ML_RUNTIME_DOC,
        help="Output Markdown note path.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
