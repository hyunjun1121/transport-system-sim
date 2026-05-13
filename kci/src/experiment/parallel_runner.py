"""Parallel CRN paired experiment runner with per-cell checkpointing + resume.

Each worker process builds the OSM corridor graph ONCE in its initializer
(amortizes the ~14s build over many cells); cells are dispatched to workers
as discrete units of (params, R reps). Completed cells are appended to the
output CSV immediately so an external kill never loses more than one cell.
A subsequent invocation with the same output path skips cells already in the
file (resume).

Public functions:
- run_phase1_parallel  (paired-CRN over s × p_fail at one origin)
- run_phase2_singlemode_parallel  (paired-CRN over bus.fleet × dispatch × p_fail)
- run_phase3_parallel  (paired-CRN over Phase 3 counterfactual levers)

All three return the consolidated DataFrame and also write the CSV.
"""
from __future__ import annotations

import ctypes
import multiprocessing as mp
import os
import platform
from copy import deepcopy
from itertools import product
from pathlib import Path
from typing import Iterable

import pandas as pd

from src.experiment.runner import _paired_result_row


# --- worker-side module globals (set by _init_worker) -----------------------

_GRAPH = None
_BASE_CONFIG = None


def _available_ram_gb() -> float:
    """Return free physical RAM in GB; ctypes fallback so no psutil dep."""
    if platform.system() != "Windows":
        try:
            import resource  # type: ignore
            # crude fallback for non-Windows
            return 16.0
        except ImportError:
            return 16.0
    class _MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [('dwLength', ctypes.c_ulong),
                    ('dwMemoryLoad', ctypes.c_ulong),
                    ('ullTotalPhys', ctypes.c_ulonglong),
                    ('ullAvailPhys', ctypes.c_ulonglong),
                    ('ullTotalPageFile', ctypes.c_ulonglong),
                    ('ullAvailPageFile', ctypes.c_ulonglong),
                    ('ullTotalVirtual', ctypes.c_ulonglong),
                    ('ullAvailVirtual', ctypes.c_ulonglong),
                    ('sullAvailExtendedVirtual', ctypes.c_ulonglong)]
    ms = _MEMORYSTATUSEX()
    ms.dwLength = ctypes.sizeof(_MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
    return ms.ullAvailPhys / (1024 ** 3)


def recommended_workers(n_cells: int) -> int:
    """Recommend Pool size given machine RAM + CPU count.

    Heuristic: each worker holds ~2 GB (OSM corridor graph + Python overhead).
    Cap by min(cpu_count(), free_GB // 2, n_cells). Leaves 4 GB headroom for OS.
    """
    cpu = os.cpu_count() or 1
    free_gb = max(0.0, _available_ram_gb() - 4.0)  # 4 GB headroom
    ram_workers = max(1, int(free_gb // 2))
    return max(1, min(cpu, ram_workers, n_cells))


def _set_high_priority_windows() -> None:
    """Best-effort: bump process priority class on Windows (no-op elsewhere)."""
    if platform.system() != "Windows":
        return
    try:
        ABOVE_NORMAL_PRIORITY_CLASS = 0x00008000
        handle = ctypes.windll.kernel32.GetCurrentProcess()
        ctypes.windll.kernel32.SetPriorityClass(handle, ABOVE_NORMAL_PRIORITY_CLASS)
    except Exception:
        pass


def _init_worker(region_path: str, cache_path: str, origin: str | None,
                 base_config: dict) -> None:
    """Build the corridor graph once per worker process.

    Pins BLAS / threading libs to 1 thread so they don't fight each other when
    many workers run concurrently (oversubscription kills throughput on
    multi-core boxes). Also bumps Windows process priority class so the OS
    scheduler favors simulation work over background tasks.
    """
    global _GRAPH, _BASE_CONFIG
    # Limit nested threading BEFORE numpy/scipy import inside the worker.
    for var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS",
                "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ.setdefault(var, "1")
    _set_high_priority_windows()
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from src.kci_runtime import build_corridor_graph, load_region_with_origin
    region = load_region_with_origin(region_path, None, origin) if origin is None else \
        load_region_with_origin(
            region_path,
            Path(region_path).parent / "origin_candidates.json",
            origin,
        )
    _GRAPH = build_corridor_graph(region, cache_path)
    _BASE_CONFIG = base_config


def _run_cell_phase1(args):
    """Worker task: run one Phase-1 cell (R paired reps) and return its rows."""
    cell_id, s, p_fail_scale, sigma, seed_base, R, late_penalty_extra_overrides = args
    from src.policies import StrictPolicy
    from src.scenario import run_scenario

    cfg = deepcopy(_BASE_CONFIG)
    if late_penalty_extra_overrides:
        for path, value in late_penalty_extra_overrides:
            d = cfg
            for k in path[:-1]:
                d = d.setdefault(k, {})
            d[path[-1]] = value

    policy = StrictPolicy()
    rows = []
    for r in range(R):
        seed = seed_base + r
        params = {"s": s, "p_fail_scale": p_fail_scale, "sigma": sigma}
        bus = run_scenario(_GRAPH, cfg, "bus_only", policy, params, seed)
        multi = run_scenario(_GRAPH, cfg, "multimodal", policy, params, seed)
        rows.append(_paired_result_row({
            "s": s,
            "p_fail_scale": p_fail_scale,
            "network_variant": cfg.get("network", {}).get("variant", "baseline"),
            "failure_mode": cfg.get("failure", {}).get("mode", "blocked"),
            "capacity_reduction_factor": cfg.get("failure", {}).get("capacity_reduction_factor"),
            "rep": r,
            "seed": seed,
            "cell_id": cell_id,
        }, bus, multi))
    return rows


def _run_cell_phase2_singlemode(args):
    """Worker task: run one Phase-2 single-mode cell."""
    cell_id, fleet, dispatch, p_fail, sigma, seed_base, R, s = args
    from src.policies import StrictPolicy
    from src.scenario import run_scenario

    cfg = deepcopy(_BASE_CONFIG)
    cfg["bus"]["fleet_size"] = int(fleet)
    cfg["bus"]["dispatch_interval_min"] = float(dispatch)

    policy = StrictPolicy()
    rows = []
    for r in range(R):
        seed = seed_base + r
        params = {"s": s, "p_fail_scale": float(p_fail), "sigma": sigma}
        bus = run_scenario(_GRAPH, cfg, "bus_only", policy, params, seed)
        multi = run_scenario(_GRAPH, cfg, "multimodal", policy, params, seed)
        rows.append(_paired_result_row({
            "bus_fleet_size": int(fleet),
            "bus_dispatch_interval_min": float(dispatch),
            "p_fail_scale": float(p_fail),
            "rep": r,
            "seed": seed,
            "s": s,
            "cell_id": cell_id,
        }, bus, multi))
    return rows


def _run_cell_phase3(args):
    """Worker task: run one Phase-3 counterfactual lever cell."""
    cell_id, point_dict, sigma, seed_base, R = args
    from src.kci_runtime import apply_phase3_lever_override
    from src.policies import StrictPolicy
    from src.scenario import run_scenario
    from src.experiment.doe import Phase3Point

    point = Phase3Point(**point_dict)
    cfg = apply_phase3_lever_override(deepcopy(_BASE_CONFIG), point)

    policy = StrictPolicy()
    rows = []
    for r in range(R):
        seed = seed_base + r
        params = {"s": 1.0, "p_fail_scale": point.p_fail_scale, "sigma": sigma}
        bus = run_scenario(_GRAPH, cfg, "bus_only", policy, params, seed)
        multi = run_scenario(_GRAPH, cfg, "multimodal", policy, params, seed)
        rows.append(_paired_result_row({
            "rail_headway_min": point.rail_headway_min,
            "lastmile_fleet_size": point.lastmile_fleet_size,
            "rail_capacity_pax_per_train": point.rail_capacity_pax_per_train,
            "p_fail_scale": point.p_fail_scale,
            "network_variant": point.network_variant,
            "failure_mode": point.failure_mode,
            "capacity_reduction_factor": point.capacity_reduction_factor,
            "rep": r,
            "seed": seed,
            "cell_id": cell_id,
        }, bus, multi))
    return rows


# --- public driver helpers --------------------------------------------------

def _completed_cell_ids(output_path: Path) -> set:
    """Return set of cell_ids already present in the output CSV (for resume)."""
    if not output_path.exists():
        return set()
    try:
        df = pd.read_csv(output_path)
        if "cell_id" not in df.columns:
            return set()
        return set(df["cell_id"].astype(str).tolist())
    except (pd.errors.EmptyDataError, FileNotFoundError):
        return set()


def _append_rows_to_csv(rows: list[dict], output_path: Path) -> None:
    if not rows:
        return
    df = pd.DataFrame(rows)
    header_needed = not output_path.exists() or output_path.stat().st_size == 0
    df.to_csv(output_path, mode="a", header=header_needed, index=False, encoding="utf-8")


def _drive_pool(work_units, runner_fn, init_args, output_path: Path,
                n_workers: int, log_prefix: str) -> pd.DataFrame:
    """Dispatch work_units to a Pool, write each cell's rows immediately."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    completed = _completed_cell_ids(output_path)
    remaining = [u for u in work_units if str(u[0]) not in completed]
    if completed:
        print(f"{log_prefix}: resume - {len(completed)} cells already in {output_path.name}, "
              f"{len(remaining)} remaining", flush=True)

    total = len(remaining)
    if total == 0:
        return pd.read_csv(output_path)

    n_workers = max(1, n_workers or recommended_workers(total))
    print(f"{log_prefix}: starting Pool({n_workers}); total cells={total}", flush=True)

    with mp.Pool(
        processes=n_workers,
        initializer=_init_worker,
        initargs=init_args,
    ) as pool:
        done = 0
        import time
        t0 = time.time()
        for rows in pool.imap_unordered(runner_fn, remaining):
            _append_rows_to_csv(rows, output_path)
            done += 1
            elapsed = time.time() - t0
            eta = elapsed / done * (total - done)
            print(
                f"  {log_prefix}: cell {done}/{total} done; elapsed={elapsed:.1f}s ETA={eta:.0f}s",
                flush=True,
            )
    return pd.read_csv(output_path)


def run_phase1_parallel(config: dict, *, region_path: str, cache_path: str,
                        origin: str | None, output_path: Path | str,
                        s_levels: Iterable[float] | None = None,
                        p_levels: Iterable[float] | None = None,
                        R: int | None = None, n_workers: int | None = None) -> pd.DataFrame:
    """Phase 1 parallel runner with per-cell checkpointing."""
    output_path = Path(output_path)
    s_levels = list(s_levels if s_levels is not None else config["congestion_scale"]["levels"])
    p_levels = list(p_levels if p_levels is not None else config["failure_rate"]["levels"])
    R = int(R if R is not None else config["experiment"]["R"])
    sigma = float(config["lateness"]["sigma_levels"][0])
    seed_base = int(config["experiment"]["seed_base"])

    work_units = []
    for s, p in product(s_levels, p_levels):
        cell_id = f"s={s:g}|p={p:g}"
        work_units.append((cell_id, float(s), float(p), sigma, seed_base, R, None))

    return _drive_pool(
        work_units,
        _run_cell_phase1,
        init_args=(region_path, cache_path, origin, config),
        output_path=output_path,
        n_workers=n_workers,
        log_prefix="Phase 1",
    )


def run_phase2_singlemode_parallel(config: dict, *, region_path: str, cache_path: str,
                                    origin: str | None, output_path: Path | str,
                                    fleet_levels: Iterable[int], dispatch_levels: Iterable[float],
                                    p_levels: Iterable[float], R: int,
                                    s: float = 1.2, n_workers: int | None = None) -> pd.DataFrame:
    """Phase 2 single-mode parametric parallel runner."""
    output_path = Path(output_path)
    sigma = float(config["lateness"]["sigma_levels"][0])
    seed_base = int(config["experiment"]["seed_base"])

    work_units = []
    for fleet, dispatch, p_fail in product(fleet_levels, dispatch_levels, p_levels):
        cell_id = f"fleet={fleet}|disp={dispatch:g}|p={p_fail:g}"
        work_units.append((cell_id, int(fleet), float(dispatch), float(p_fail),
                          sigma, seed_base, R, s))

    return _drive_pool(
        work_units,
        _run_cell_phase2_singlemode,
        init_args=(region_path, cache_path, origin, config),
        output_path=output_path,
        n_workers=n_workers,
        log_prefix="Phase 2",
    )


def run_phase3_parallel(config: dict, *, region_path: str, cache_path: str,
                        origin: str | None, output_path: Path | str,
                        n_workers: int | None = None) -> pd.DataFrame:
    """Phase 3 counterfactual lever sweep parallel runner."""
    from src.experiment.doe import phase3_grid

    output_path = Path(output_path)
    sigma = float(config["lateness"]["sigma_levels"][0])
    seed_base = int(config["experiment"]["seed_base"])
    R = int(config["experiment"].get("R_phase3", config["experiment"]["R"]))

    grid = phase3_grid(config)
    work_units = []
    for point in grid:
        cell_id = (f"h={point.rail_headway_min:g}|f={point.lastmile_fleet_size}|"
                   f"c={point.rail_capacity_pax_per_train}|p={point.p_fail_scale:g}")
        work_units.append((cell_id, point._asdict(), sigma, seed_base, R))

    return _drive_pool(
        work_units,
        _run_cell_phase3,
        init_args=(region_path, cache_path, origin, config),
        output_path=output_path,
        n_workers=n_workers,
        log_prefix="Phase 3",
    )
