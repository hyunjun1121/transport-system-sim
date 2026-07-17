"""Figure and table scaffolding for pilot scaffold outputs.

The artifacts produced here are generated from the current scaffold CSVs. They
are intentionally labeled as sample scaffolding, not calibrated real-world
results or operational forecasts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "results" / "realworld_pilot"
DEFAULT_FIGURES_DIR = DEFAULT_OUTPUT_DIR / "figures"
DEFAULT_TABLES_DIR = DEFAULT_OUTPUT_DIR / "tables"
DEFAULT_PILOT_SUMMARY_PATH = DEFAULT_OUTPUT_DIR / "pilot_full_summary.csv"
DEFAULT_SENSITIVITY_SUMMARY_PATH = DEFAULT_OUTPUT_DIR / "morris_summary.csv"
DEFAULT_PILOT_MANIFEST_PATH = DEFAULT_OUTPUT_DIR / "pilot_full_manifest.json"
DEFAULT_SENSITIVITY_MANIFEST_PATH = DEFAULT_OUTPUT_DIR / "morris_manifest.json"

FIGURE_FILENAMES = (
    "completion_by_disruption.png",
    "censored_by_disruption.png",
    "policy_resource_tradeoff.png",
    "sensitivity_ranking.png",
    "bottleneck_attribution.png",
    "policy_regime_map.png",
)
TABLE_FILENAMES = (
    "main_result_table.csv",
    "sensitivity_result_table.csv",
    "bottleneck_attribution_table.csv",
    "policy_regime_table.csv",
    "claim_boundary_table.csv",
    "figure_table_manifest.json",
)
FIXTURE_LABEL = "scaffold-only"
FIGURE_SCOPE = (
    "Generated from current pilot scaffold CSVs only; not calibrated "
    "real-world results or an operational forecast."
)

PILOT_SUMMARY_REQUIRED_COLUMNS = (
    "region_id",
    "graph_source",
    "policy_id",
    "scenario_id",
    "scenario_family",
    "scenario_type",
    "mode",
    "run_count",
    "mean_completion_rate",
    "mean_censored_count",
    "mean_penalized_makespan",
    "mean_total_service_minutes",
    "mean_passengers_per_total_service_minute",
    "mean_first_arrival_time",
    "mean_median_arrival_time",
    "mean_p80_arrival_time",
    "mean_p95_arrival_time",
    "claim_scope",
)
SENSITIVITY_SUMMARY_REQUIRED_COLUMNS = (
    "metric",
    "rank",
    "parameter_id",
    "salib_name",
    "method",
    "max_abs_delta",
    "mean_abs_delta",
    "max_abs_delta_level",
    "max_abs_delta_policy_id",
    "max_abs_delta_scenario_id",
    "baseline_value",
    "low_value",
    "high_value",
    "unit",
    "applies_to",
    "scenario_filter",
    "run_count",
    "claim_scope",
)
MORRIS_SUMMARY_REQUIRED_COLUMNS = (
    "metric",
    "policy_id",
    "scenario_id",
    "rank",
    "parameter_id",
    "salib_name",
    "method",
    "mu",
    "mu_star",
    "sigma",
    "mu_star_conf",
    "sample_count",
    "num_trajectories",
    "num_levels",
    "claim_scope",
)
MAIN_RESULT_TABLE_COLUMNS = (
    "region_id",
    "graph_source",
    "policy_id",
    "mode",
    "scenario_id",
    "scenario_family",
    "scenario_type",
    "run_count",
    "completion_rate",
    "censored_count",
    "penalized_makespan_min",
    "total_service_minutes",
    "passengers_per_total_service_minute",
    "first_arrival_time",
    "median_arrival_time",
    "p80_arrival_time",
    "p95_arrival_time",
    "evidence_label",
    "claim_scope",
)
SENSITIVITY_RESULT_TABLE_COLUMNS = (
    "metric",
    "rank",
    "parameter_id",
    "salib_name",
    "method",
    "max_abs_delta",
    "mean_abs_delta",
    "max_abs_delta_level",
    "max_abs_delta_policy_id",
    "max_abs_delta_scenario_id",
    "baseline_value",
    "low_value",
    "high_value",
    "unit",
    "applies_to",
    "scenario_filter",
    "run_count",
    "evidence_label",
    "claim_scope",
    "mu",
    "mu_star",
    "sigma",
    "mu_star_conf",
    "sample_count",
    "num_trajectories",
    "num_levels",
)
CLAIM_BOUNDARY_COLUMNS = (
    "artifact",
    "source_file",
    "evidence_label",
    "allowed_use",
    "prohibited_use",
    "limitation",
    "source_scope",
)
BOTTLENECK_ATTRIBUTION_COLUMNS = (
    "region_id",
    "scenario_id",
    "scenario_family",
    "scenario_type",
    "policy_id",
    "mode",
    "bottleneck_class",
    "completion_loss",
    "censored_increase",
    "penalized_makespan_increase_min",
    "p95_arrival_increase_min",
    "performance_loss_score",
    "evidence_label",
    "claim_scope",
)
POLICY_REGIME_COLUMNS = (
    "region_id",
    "scenario_id",
    "scenario_family",
    "scenario_type",
    "decision_lens",
    "winning_policy_id",
    "winning_mode",
    "winning_value",
    "second_best_value",
    "margin_to_second",
    "regime_label",
    "evidence_label",
    "claim_scope",
)


def build_pilot_figure_tables(
    *,
    pilot_summary_path: str | Path = DEFAULT_PILOT_SUMMARY_PATH,
    sensitivity_summary_path: str | Path = DEFAULT_SENSITIVITY_SUMMARY_PATH,
    pilot_manifest_path: str | Path = DEFAULT_PILOT_MANIFEST_PATH,
    sensitivity_manifest_path: str | Path = DEFAULT_SENSITIVITY_MANIFEST_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    figures_dir: str | Path | None = None,
    tables_dir: str | Path | None = None,
    sensitivity_metric: str = "penalized_makespan",
) -> dict[str, Any]:
    """Build scaffold-only figures, result tables, and a manifest from CSV paths."""

    pilot_summary_file = Path(pilot_summary_path)
    sensitivity_summary_file = Path(sensitivity_summary_path)
    pilot_manifest_file = Path(pilot_manifest_path)
    sensitivity_manifest_file = Path(sensitivity_manifest_path)
    base_output_dir = Path(output_dir)
    figure_output_dir = Path(figures_dir) if figures_dir is not None else base_output_dir / "figures"
    table_output_dir = Path(tables_dir) if tables_dir is not None else base_output_dir / "tables"
    figure_output_dir.mkdir(parents=True, exist_ok=True)
    table_output_dir.mkdir(parents=True, exist_ok=True)

    pilot_summary = _read_csv(
        pilot_summary_file,
        required_columns=PILOT_SUMMARY_REQUIRED_COLUMNS,
    )
    sensitivity_summary = _read_csv(
        sensitivity_summary_file,
        required_columns=(),
    )
    pilot_manifest = _read_manifest(pilot_manifest_file)
    sensitivity_manifest = _read_manifest(sensitivity_manifest_file)

    main_table = build_main_result_table(pilot_summary)
    sensitivity_table = build_sensitivity_result_table(sensitivity_summary)
    bottleneck_table = build_bottleneck_attribution_table(main_table)
    policy_regime_table = build_policy_regime_table(main_table)
    claim_boundary_table = build_claim_boundary_table(
        pilot_summary_path=pilot_summary_file,
        sensitivity_summary_path=sensitivity_summary_file,
        pilot_manifest=pilot_manifest,
        sensitivity_manifest=sensitivity_manifest,
    )

    table_paths = {
        "main_result_table": table_output_dir / "main_result_table.csv",
        "sensitivity_result_table": table_output_dir / "sensitivity_result_table.csv",
        "bottleneck_attribution_table": (
            table_output_dir / "bottleneck_attribution_table.csv"
        ),
        "policy_regime_table": table_output_dir / "policy_regime_table.csv",
        "claim_boundary_table": table_output_dir / "claim_boundary_table.csv",
    }
    _write_csv(table_paths["main_result_table"], main_table)
    _write_csv(table_paths["sensitivity_result_table"], sensitivity_table)
    _write_csv(table_paths["bottleneck_attribution_table"], bottleneck_table)
    _write_csv(table_paths["policy_regime_table"], policy_regime_table)
    _write_csv(table_paths["claim_boundary_table"], claim_boundary_table)

    selected_metric = _select_sensitivity_metric(
        sensitivity_table,
        requested_metric=sensitivity_metric,
    )
    figure_paths = {
        "completion_by_disruption": figure_output_dir / "completion_by_disruption.png",
        "censored_by_disruption": figure_output_dir / "censored_by_disruption.png",
        "policy_resource_tradeoff": figure_output_dir / "policy_resource_tradeoff.png",
        "sensitivity_ranking": figure_output_dir / "sensitivity_ranking.png",
        "bottleneck_attribution": figure_output_dir / "bottleneck_attribution.png",
        "policy_regime_map": figure_output_dir / "policy_regime_map.png",
    }
    plot_completion_by_disruption(main_table, figure_paths["completion_by_disruption"])
    plot_censored_by_disruption(main_table, figure_paths["censored_by_disruption"])
    plot_policy_resource_tradeoff(main_table, figure_paths["policy_resource_tradeoff"])
    plot_sensitivity_ranking(
        sensitivity_table,
        figure_paths["sensitivity_ranking"],
        metric=selected_metric,
    )
    plot_bottleneck_attribution(
        bottleneck_table,
        figure_paths["bottleneck_attribution"],
    )
    plot_policy_regime_map(
        policy_regime_table,
        figure_paths["policy_regime_map"],
    )

    manifest = build_figure_table_manifest(
        pilot_summary_path=pilot_summary_file,
        sensitivity_summary_path=sensitivity_summary_file,
        pilot_manifest_path=pilot_manifest_file,
        sensitivity_manifest_path=sensitivity_manifest_file,
        pilot_manifest=pilot_manifest,
        sensitivity_manifest=sensitivity_manifest,
        main_table=main_table,
        sensitivity_table=sensitivity_table,
        bottleneck_table=bottleneck_table,
        policy_regime_table=policy_regime_table,
        claim_boundary_table=claim_boundary_table,
        figure_paths=figure_paths,
        table_paths=table_paths,
        selected_sensitivity_metric=selected_metric,
    )
    manifest_path = table_output_dir / "figure_table_manifest.json"
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")

    return {
        "figures": figure_paths,
        "tables": {**table_paths, "figure_table_manifest": manifest_path},
        "manifest": manifest,
        "figures_dir": figure_output_dir,
        "tables_dir": table_output_dir,
    }


def build_main_result_table(pilot_summary: pd.DataFrame) -> pd.DataFrame:
    """Return the compact main result table used by reports and figures."""

    _require_columns(pilot_summary, PILOT_SUMMARY_REQUIRED_COLUMNS, "pilot summary")
    table = pilot_summary.loc[:, PILOT_SUMMARY_REQUIRED_COLUMNS].copy()
    table = table.rename(
        columns={
            "mean_completion_rate": "completion_rate",
            "mean_censored_count": "censored_count",
            "mean_penalized_makespan": "penalized_makespan_min",
            "mean_total_service_minutes": "total_service_minutes",
            "mean_passengers_per_total_service_minute": (
                "passengers_per_total_service_minute"
            ),
            "mean_first_arrival_time": "first_arrival_time",
            "mean_median_arrival_time": "median_arrival_time",
            "mean_p80_arrival_time": "p80_arrival_time",
            "mean_p95_arrival_time": "p95_arrival_time",
        }
    )
    table["evidence_label"] = FIXTURE_LABEL
    table = table.loc[:, MAIN_RESULT_TABLE_COLUMNS]
    return _sort_main_table(_coerce_numeric(table))


def build_sensitivity_result_table(sensitivity_summary: pd.DataFrame) -> pd.DataFrame:
    """Return the compact sensitivity result table used by reports and figures."""

    if _has_columns(sensitivity_summary, SENSITIVITY_SUMMARY_REQUIRED_COLUMNS):
        table = _deterministic_sensitivity_table(sensitivity_summary)
    elif _has_columns(sensitivity_summary, MORRIS_SUMMARY_REQUIRED_COLUMNS):
        table = _morris_sensitivity_table(sensitivity_summary)
    else:
        missing_deterministic = [
            column
            for column in SENSITIVITY_SUMMARY_REQUIRED_COLUMNS
            if column not in sensitivity_summary.columns
        ]
        missing_morris = [
            column
            for column in MORRIS_SUMMARY_REQUIRED_COLUMNS
            if column not in sensitivity_summary.columns
        ]
        raise KeyError(
            "sensitivity summary is missing required columns for both supported "
            f"schemas; deterministic_missing={missing_deterministic}, "
            f"morris_missing={missing_morris}"
        )

    table["evidence_label"] = FIXTURE_LABEL
    table = table.loc[:, SENSITIVITY_RESULT_TABLE_COLUMNS]
    return _sort_sensitivity_table(_coerce_numeric(table))


def build_bottleneck_attribution_table(main_table: pd.DataFrame) -> pd.DataFrame:
    """Return scenario-family bottleneck attribution proxies.

    These rows compare each policy/scenario result with the same policy's
    no-disruption baseline. They are attribution scaffolds, not causal
    bottleneck measurements from instrumented vehicle logs.
    """

    _require_columns(main_table, MAIN_RESULT_TABLE_COLUMNS, "main result table")
    table = _coerce_numeric(main_table)
    baseline = table[table["scenario_id"] == "no_disruption"].copy()
    if baseline.empty:
        raise ValueError("main result table must include no_disruption rows")

    baseline_by_policy = {
        str(row["policy_id"]): row
        for _, row in baseline.iterrows()
    }
    rows: list[dict[str, Any]] = []
    for _, row in table.iterrows():
        policy_id = str(row["policy_id"])
        base = baseline_by_policy.get(policy_id)
        if base is None:
            continue
        completion_loss = max(
            0.0,
            float(base["completion_rate"]) - float(row["completion_rate"]),
        )
        censored_increase = max(
            0.0,
            float(row["censored_count"]) - float(base["censored_count"]),
        )
        makespan_increase = max(
            0.0,
            float(row["penalized_makespan_min"])
            - float(base["penalized_makespan_min"]),
        )
        p95_increase = max(
            0.0,
            float(row["p95_arrival_time"]) - float(base["p95_arrival_time"]),
        )
        rows.append(
            {
                "region_id": row["region_id"],
                "scenario_id": row["scenario_id"],
                "scenario_family": row["scenario_family"],
                "scenario_type": row["scenario_type"],
                "policy_id": policy_id,
                "mode": row["mode"],
                "bottleneck_class": _bottleneck_class(row["scenario_id"]),
                "completion_loss": round(completion_loss, 6),
                "censored_increase": round(censored_increase, 6),
                "penalized_makespan_increase_min": round(makespan_increase, 6),
                "p95_arrival_increase_min": round(p95_increase, 6),
                "performance_loss_score": round(
                    completion_loss * 1000.0
                    + censored_increase
                    + makespan_increase
                    + p95_increase,
                    6,
                ),
                "evidence_label": FIXTURE_LABEL,
                "claim_scope": row["claim_scope"],
            }
        )
    result = pd.DataFrame(rows, columns=BOTTLENECK_ATTRIBUTION_COLUMNS)
    return result.sort_values(
        ["bottleneck_class", "scenario_id", "policy_id"],
        kind="mergesort",
    ).reset_index(drop=True)


def build_policy_regime_table(main_table: pd.DataFrame) -> pd.DataFrame:
    """Return policy winners by scenario under reliability, speed, and resource lenses."""

    _require_columns(main_table, MAIN_RESULT_TABLE_COLUMNS, "main result table")
    table = _coerce_numeric(main_table)
    rows: list[dict[str, Any]] = []
    for scenario_id, group in table.groupby("scenario_id", sort=True):
        rows.extend(_policy_regime_rows(str(scenario_id), group))
    result = pd.DataFrame(rows, columns=POLICY_REGIME_COLUMNS)
    return result.sort_values(
        ["scenario_family", "scenario_id", "decision_lens"],
        kind="mergesort",
    ).reset_index(drop=True)


def _policy_regime_rows(scenario_id: str, group: pd.DataFrame) -> list[dict[str, Any]]:
    lenses = (
        (
            "reliability",
            ["completion_rate", "censored_count", "penalized_makespan_min"],
            [False, True, True],
            "completion_rate",
        ),
        (
            "speed",
            ["penalized_makespan_min", "p95_arrival_time", "total_service_minutes"],
            [True, True, True],
            "penalized_makespan_min",
        ),
        (
            "resource",
            [
                "passengers_per_total_service_minute",
                "completion_rate",
                "penalized_makespan_min",
            ],
            [False, False, True],
            "passengers_per_total_service_minute",
        ),
    )
    rows: list[dict[str, Any]] = []
    for lens, sort_columns, ascending, value_column in lenses:
        ranked = group.sort_values(sort_columns, ascending=ascending, kind="mergesort")
        winner = ranked.iloc[0]
        second = ranked.iloc[1] if len(ranked) > 1 else winner
        winning_value = float(winner[value_column])
        second_value = float(second[value_column])
        margin = (
            winning_value - second_value
            if lens in {"reliability", "resource"}
            else second_value - winning_value
        )
        rows.append(
            {
                "region_id": winner["region_id"],
                "scenario_id": scenario_id,
                "scenario_family": winner["scenario_family"],
                "scenario_type": winner["scenario_type"],
                "decision_lens": lens,
                "winning_policy_id": winner["policy_id"],
                "winning_mode": winner["mode"],
                "winning_value": round(winning_value, 6),
                "second_best_value": round(second_value, 6),
                "margin_to_second": round(margin, 6),
                "regime_label": _regime_label(lens, winner),
                "evidence_label": FIXTURE_LABEL,
                "claim_scope": winner["claim_scope"],
            }
        )
    return rows


def _deterministic_sensitivity_table(sensitivity_summary: pd.DataFrame) -> pd.DataFrame:
    """Normalize deterministic OAT sensitivity rows to the report table schema."""

    table = sensitivity_summary.loc[:, SENSITIVITY_SUMMARY_REQUIRED_COLUMNS].copy()
    for column in (
        "mu",
        "mu_star",
        "sigma",
        "mu_star_conf",
        "sample_count",
        "num_trajectories",
        "num_levels",
    ):
        table[column] = ""
    return table


def _morris_sensitivity_table(sensitivity_summary: pd.DataFrame) -> pd.DataFrame:
    """Normalize SALib Morris rows to the report table schema."""

    source = sensitivity_summary.loc[:, MORRIS_SUMMARY_REQUIRED_COLUMNS].copy()
    table = pd.DataFrame(
        {
            "metric": source["metric"],
            "rank": source["rank"],
            "parameter_id": source["parameter_id"],
            "salib_name": source["salib_name"],
            "method": source["method"],
            "max_abs_delta": source["mu_star"],
            "mean_abs_delta": source["mu"],
            "max_abs_delta_level": "",
            "max_abs_delta_policy_id": source["policy_id"],
            "max_abs_delta_scenario_id": source["scenario_id"],
            "baseline_value": "",
            "low_value": "",
            "high_value": "",
            "unit": "",
            "applies_to": "",
            "scenario_filter": "",
            "run_count": source["sample_count"],
            "claim_scope": source["claim_scope"],
            "mu": source["mu"],
            "mu_star": source["mu_star"],
            "sigma": source["sigma"],
            "mu_star_conf": source["mu_star_conf"],
            "sample_count": source["sample_count"],
            "num_trajectories": source["num_trajectories"],
            "num_levels": source["num_levels"],
        }
    )
    return table


def build_claim_boundary_table(
    *,
    pilot_summary_path: str | Path,
    sensitivity_summary_path: str | Path,
    pilot_manifest: Mapping[str, Any],
    sensitivity_manifest: Mapping[str, Any],
) -> pd.DataFrame:
    """Return explicit scaffold-only claim boundaries for generated artifacts."""

    pilot_scope = _scope_from_manifest(pilot_manifest, fallback=FIGURE_SCOPE)
    sensitivity_scope = _scope_from_manifest(sensitivity_manifest, fallback=FIGURE_SCOPE)
    sensitivity_method = str(sensitivity_manifest.get("method", "")).strip()
    if sensitivity_method == "salib_morris":
        sensitivity_allowed = (
            "SALib Morris screening scaffold for identifying which current "
            "scaffold assumptions move selected metrics."
        )
        sensitivity_prohibited = (
            "Do not describe as calibrated real-world sensitivity evidence, "
            "Sobol analysis, causal attribution, or an operational forecast."
        )
        sensitivity_limitation = (
            "Formal Morris indices are computed on current scaffold inputs and "
            "the reduced analysis graph; they are not calibrated real-world "
            "sensitivity evidence."
        )
        manifest_limitation = (
            "Records generated artifacts only; calibration, reviewed OSM "
            "inputs, external-router validation, and accepted full pilot "
            "outputs remain separate tasks."
        )
    else:
        sensitivity_allowed = (
            "Deterministic one-at-a-time screening scaffold for identifying "
            "which scaffold assumptions move selected metrics."
        )
        sensitivity_prohibited = (
            "Do not describe as SALib Morris/Sobol indices, calibrated causal "
            "sensitivity, or an operational forecast."
        )
        sensitivity_limitation = (
            "Scaffold-only sensitivity screening with current sample inputs; "
            "not calibrated real-world sensitivity evidence."
        )
        manifest_limitation = (
            "Records generated artifacts only; calibration, reviewed OSM "
            "inputs, and formal sensitivity analysis remain separate tasks."
        )
    rows = [
        {
            "artifact": "main_result_table_and_policy_figures",
            "source_file": _display_path(pilot_summary_path),
            "evidence_label": FIXTURE_LABEL,
            "allowed_use": (
                "Decision-support figure/table scaffold generated from the "
                "current pilot full-profile scaffold summary."
            ),
            "prohibited_use": (
                "Do not use as a calibrated real-world result, operational "
                "route plan, or public-agency forecast."
            ),
            "limitation": (
                "Scaffold-only full-profile output with uncalibrated "
                "assumptions, a cached demo graph, and reduced analysis "
                "corridors; not calibrated real-world evidence."
            ),
            "source_scope": pilot_scope,
        },
        {
            "artifact": "sensitivity_result_table_and_ranking_figure",
            "source_file": _display_path(sensitivity_summary_path),
            "evidence_label": FIXTURE_LABEL,
            "allowed_use": sensitivity_allowed,
            "prohibited_use": sensitivity_prohibited,
            "limitation": sensitivity_limitation,
            "source_scope": sensitivity_scope,
        },
        {
            "artifact": "figure_table_manifest",
            "source_file": (
                f"{_display_path(pilot_summary_path)}; "
                f"{_display_path(sensitivity_summary_path)}"
            ),
            "evidence_label": FIXTURE_LABEL,
            "allowed_use": (
                "Reproducibility index for the generated scaffold-only figures "
                "and tables."
            ),
            "prohibited_use": (
                "Do not cite the generated manifest as proof of publication-grade "
                "validation or deployment readiness."
            ),
            "limitation": manifest_limitation,
            "source_scope": FIGURE_SCOPE,
        },
    ]
    return pd.DataFrame(rows, columns=CLAIM_BOUNDARY_COLUMNS)


def plot_completion_by_disruption(table: pd.DataFrame, output_path: str | Path) -> Path:
    """Plot mean completion rate by disruption case and policy."""

    plot_df = _plot_ready_main_table(table)
    fig, ax = plt.subplots(figsize=(11, 5.5))
    sns.barplot(
        data=plot_df,
        x="disruption_label",
        y="completion_rate",
        hue="policy_id",
        errorbar=None,
        ax=ax,
    )
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Disruption case")
    ax.set_ylabel("Completion rate")
    ax.set_title("Completion Rate By Disruption (Scaffold-Only Pilot)")
    _finish_categorical_axis(ax)
    _save_figure(fig, output_path)
    return Path(output_path)


def plot_censored_by_disruption(table: pd.DataFrame, output_path: str | Path) -> Path:
    """Plot mean censored passenger count by disruption case and policy."""

    plot_df = _plot_ready_main_table(table)
    fig, ax = plt.subplots(figsize=(11, 5.5))
    sns.barplot(
        data=plot_df,
        x="disruption_label",
        y="censored_count",
        hue="policy_id",
        errorbar=None,
        ax=ax,
    )
    upper = max(1.0, float(plot_df["censored_count"].max()) * 1.15)
    ax.set_ylim(0, upper)
    ax.set_xlabel("Disruption case")
    ax.set_ylabel("Censored passengers")
    ax.set_title("Censored Passengers By Disruption (Scaffold-Only Pilot)")
    if float(plot_df["censored_count"].max()) == 0.0:
        ax.text(
            0.5,
            0.92,
            "Current scaffold output has zero censored passengers in every row.",
            ha="center",
            va="center",
            transform=ax.transAxes,
            fontsize=9,
        )
    _finish_categorical_axis(ax)
    _save_figure(fig, output_path)
    return Path(output_path)


def plot_policy_resource_tradeoff(table: pd.DataFrame, output_path: str | Path) -> Path:
    """Plot total service minutes versus penalized makespan by policy."""

    plot_df = _plot_ready_main_table(table)
    fig, ax = plt.subplots(figsize=(8.5, 6))
    sns.scatterplot(
        data=plot_df,
        x="total_service_minutes",
        y="penalized_makespan_min",
        hue="policy_id",
        style="scenario_family",
        size="completion_rate",
        sizes=(70, 140),
        ax=ax,
    )
    ax.set_xlabel("Total service minutes")
    ax.set_ylabel("Penalized makespan (min)")
    ax.set_title("Policy Resource Trade-Off (Scaffold-Only Pilot)")
    ax.grid(True, alpha=0.3)
    sns.move_legend(ax, "upper left", bbox_to_anchor=(1.02, 1), borderaxespad=0)
    _save_figure(fig, output_path)
    return Path(output_path)


def plot_sensitivity_ranking(
    table: pd.DataFrame,
    output_path: str | Path,
    *,
    metric: str = "penalized_makespan",
    limit: int = 10,
) -> Path:
    """Plot the largest absolute screening deltas for one sensitivity metric."""

    _require_columns(table, SENSITIVITY_RESULT_TABLE_COLUMNS, "sensitivity table")
    metric_df = table[table["metric"] == metric].copy()
    if metric_df.empty:
        raise ValueError(f"no sensitivity rows found for metric {metric!r}")
    uses_morris = "salib_morris" in set(str(value) for value in metric_df["method"].dropna())
    score_column = "mu_star" if uses_morris else "max_abs_delta"
    metric_df[score_column] = pd.to_numeric(
        metric_df[score_column],
        errors="coerce",
    )
    metric_df = metric_df.dropna(subset=[score_column])
    if metric_df.empty:
        raise ValueError(
            f"no finite sensitivity score rows found for metric {metric!r}"
        )
    metric_df = metric_df.sort_values(
        [score_column, "parameter_id"],
        ascending=[False, True],
    ).head(limit)
    metric_df = metric_df.sort_values(score_column, ascending=True)
    metric_df["parameter_label"] = metric_df["parameter_id"].map(_label_from_identifier)

    fig, ax = plt.subplots(figsize=(9, 6))
    sns.barplot(
        data=metric_df,
        x=score_column,
        y="parameter_label",
        hue="parameter_label",
        dodge=False,
        legend=False,
        ax=ax,
    )
    if uses_morris:
        ax.set_xlabel(f"Morris mu-star: {_label_from_identifier(metric)}")
        ax.set_title("Sensitivity Ranking (Scaffold-Only SALib Morris)")
    else:
        ax.set_xlabel(f"Max absolute delta: {_label_from_identifier(metric)}")
        ax.set_title("Sensitivity Ranking (Scaffold-Only Deterministic Screening)")
    ax.set_ylabel("Sensitivity parameter")
    ax.grid(True, axis="x", alpha=0.3)
    _save_figure(fig, output_path)
    return Path(output_path)


def plot_bottleneck_attribution(
    table: pd.DataFrame,
    output_path: str | Path,
) -> Path:
    """Plot scenario-family bottleneck loss proxies."""

    _require_columns(table, BOTTLENECK_ATTRIBUTION_COLUMNS, "bottleneck table")
    plot_df = _coerce_numeric(table)
    plot_df = plot_df[plot_df["scenario_id"] != "no_disruption"].copy()
    if plot_df.empty:
        plot_df = _coerce_numeric(table).copy()

    fig, ax = plt.subplots(figsize=(11, 5.8))
    sns.barplot(
        data=plot_df,
        x="bottleneck_class",
        y="performance_loss_score",
        hue="policy_id",
        errorbar=None,
        ax=ax,
    )
    ax.set_xlabel("Bottleneck class")
    ax.set_ylabel("Relative loss score")
    ax.set_title("Bottleneck Attribution Proxy (Scaffold-Only Pilot)")
    _finish_categorical_axis(ax)
    _save_figure(fig, output_path)
    return Path(output_path)


def plot_policy_regime_map(
    table: pd.DataFrame,
    output_path: str | Path,
) -> Path:
    """Plot policy winners by scenario and decision lens."""

    _require_columns(table, POLICY_REGIME_COLUMNS, "policy regime table")
    plot_df = table.copy()
    plot_df["scenario_label"] = plot_df["scenario_id"].map(_label_from_identifier)
    plot_df["policy_code"] = pd.Categorical(plot_df["winning_policy_id"]).codes
    pivot = plot_df.pivot(
        index="decision_lens",
        columns="scenario_label",
        values="policy_code",
    )
    labels = plot_df.pivot(
        index="decision_lens",
        columns="scenario_label",
        values="winning_policy_id",
    )

    fig, ax = plt.subplots(figsize=(12, 4.8))
    sns.heatmap(
        pivot,
        annot=labels,
        fmt="",
        cmap="tab20",
        cbar=False,
        linewidths=0.5,
        linecolor="white",
        ax=ax,
    )
    ax.set_xlabel("Scenario")
    ax.set_ylabel("Decision lens")
    ax.set_title("Policy Regime Map (Scaffold-Only Pilot)")
    ax.tick_params(axis="x", labelrotation=30)
    for label in ax.get_xticklabels():
        label.set_ha("right")
    _save_figure(fig, output_path)
    return Path(output_path)


def build_figure_table_manifest(
    *,
    pilot_summary_path: str | Path,
    sensitivity_summary_path: str | Path,
    pilot_manifest_path: str | Path,
    sensitivity_manifest_path: str | Path,
    pilot_manifest: Mapping[str, Any],
    sensitivity_manifest: Mapping[str, Any],
    main_table: pd.DataFrame,
    sensitivity_table: pd.DataFrame,
    bottleneck_table: pd.DataFrame,
    policy_regime_table: pd.DataFrame,
    claim_boundary_table: pd.DataFrame,
    figure_paths: Mapping[str, Path],
    table_paths: Mapping[str, Path],
    selected_sensitivity_metric: str,
) -> dict[str, Any]:
    """Return deterministic metadata for scaffold-only generated artifacts."""

    return {
        "schema_version": 1,
        "result_scope": FIGURE_SCOPE,
        "evidence_label": FIXTURE_LABEL,
        "command": "scripts/make_pilot_figures.py",
        "inputs": {
            "pilot_summary_path": _display_path(pilot_summary_path),
            "sensitivity_summary_path": _display_path(sensitivity_summary_path),
            "pilot_manifest_path": _display_path(pilot_manifest_path),
            "sensitivity_manifest_path": _display_path(sensitivity_manifest_path),
        },
        "source_result_scopes": {
            "pilot": _scope_from_manifest(pilot_manifest, fallback=FIGURE_SCOPE),
            "sensitivity": _scope_from_manifest(
                sensitivity_manifest,
                fallback=FIGURE_SCOPE,
            ),
        },
        "source_commands": {
            "pilot": str(pilot_manifest.get("command", "")),
            "sensitivity": str(sensitivity_manifest.get("command", "")),
        },
        "morris_index_handling": {
            "tables": (
                "Blank, masked, NaN, or infinite Morris index values are kept "
                "in generated sensitivity tables for reviewer visibility."
            ),
            "figures": (
                "Sensitivity ranking figures coerce index values to numeric "
                "and exclude non-finite rows from the plotted top rankings."
            ),
            "audit": (
                "scripts/audit_sensitivity_diagnostics.py counts blank and "
                "non-finite index rows; it does not accept sensitivity claims."
            ),
        },
        "graph_scale": {
            "pilot": _graph_scale_from_manifest(pilot_manifest),
            "sensitivity": _graph_scale_from_manifest(sensitivity_manifest),
        },
        "row_counts": {
            "main_result_table": int(len(main_table)),
            "sensitivity_result_table": int(len(sensitivity_table)),
            "bottleneck_attribution_table": int(len(bottleneck_table)),
            "policy_regime_table": int(len(policy_regime_table)),
            "claim_boundary_table": int(len(claim_boundary_table)),
        },
        "selected_sensitivity_metric": selected_sensitivity_metric,
        "figures": {
            key: {
                "path": _display_path(path),
                "caption_note": FIGURE_SCOPE,
            }
            for key, path in sorted(figure_paths.items())
        },
        "tables": {
            key: _display_path(path)
            for key, path in sorted(table_paths.items())
        },
        "claim_boundary": (
            "All generated artifacts are scaffold-only outputs and must not be "
            "described as calibrated real-world or operational outputs."
        ),
    }


def _graph_scale_from_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    existing = manifest.get("graph_scale")
    if isinstance(existing, Mapping):
        return {
            "source": dict(existing.get("source", {}))
            if isinstance(existing.get("source"), Mapping)
            else {},
            "analysis": dict(existing.get("analysis", {}))
            if isinstance(existing.get("analysis"), Mapping)
            else {},
        }
    return {
        "source": {
            "nodes": manifest.get("source_graph_nodes", ""),
            "edges": manifest.get("source_graph_edges", ""),
        },
        "analysis": {
            "nodes": manifest.get("graph_nodes", ""),
            "edges": manifest.get("graph_edges", ""),
            "reduced": bool(manifest.get("analysis_graph_reduced", False)),
            "strategy": str(manifest.get("analysis_graph_strategy", "")),
        },
    }


def _read_csv(path: Path, *, required_columns: tuple[str, ...]) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    _require_columns(df, required_columns, path.as_posix())
    return df


def _read_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _write_csv(path: Path, df: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")


def _require_columns(df: pd.DataFrame, columns: tuple[str, ...], label: str) -> None:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise KeyError(f"{label} is missing required column(s): {missing}")


def _has_columns(df: pd.DataFrame, columns: tuple[str, ...]) -> bool:
    return all(column in df.columns for column in columns)


def _coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    coerced = df.copy()
    numeric_columns = [
        "rank",
        "run_count",
        "completion_rate",
        "censored_count",
        "penalized_makespan_min",
        "total_service_minutes",
        "passengers_per_total_service_minute",
        "first_arrival_time",
        "median_arrival_time",
        "p80_arrival_time",
        "p95_arrival_time",
        "completion_loss",
        "censored_increase",
        "penalized_makespan_increase_min",
        "p95_arrival_increase_min",
        "performance_loss_score",
        "winning_value",
        "second_best_value",
        "margin_to_second",
        "max_abs_delta",
        "mean_abs_delta",
        "mu",
        "mu_star",
        "sigma",
        "mu_star_conf",
        "sample_count",
        "num_trajectories",
        "num_levels",
    ]
    for column in numeric_columns:
        if column in coerced.columns:
            coerced[column] = pd.to_numeric(coerced[column], errors="coerce")
    return coerced


def _sort_main_table(table: pd.DataFrame) -> pd.DataFrame:
    return table.sort_values(
        ["scenario_family", "scenario_id", "mode", "policy_id"],
        kind="mergesort",
    ).reset_index(drop=True)


def _sort_sensitivity_table(table: pd.DataFrame) -> pd.DataFrame:
    return table.sort_values(
        ["metric", "rank", "parameter_id"],
        kind="mergesort",
    ).reset_index(drop=True)


def _plot_ready_main_table(table: pd.DataFrame) -> pd.DataFrame:
    _require_columns(table, MAIN_RESULT_TABLE_COLUMNS, "main result table")
    plot_df = _coerce_numeric(table).copy()
    plot_df["disruption_label"] = plot_df.apply(_disruption_label, axis=1)
    return plot_df


def _disruption_label(row: pd.Series) -> str:
    family = _label_from_identifier(str(row["scenario_family"]))
    scenario_type = str(row["scenario_type"])
    if scenario_type and scenario_type != "none":
        return f"{family}\n{_label_from_identifier(scenario_type)}"
    return family


def _bottleneck_class(scenario_id: Any) -> str:
    text = str(scenario_id)
    if text == "no_disruption":
        return "none"
    if "origin_to_station" in text:
        return "rail access road"
    if "origin_to_destination" in text:
        return "direct road access"
    if "last_mile" in text:
        return "last-mile road"
    if "rail_station_access" in text:
        return "station access road"
    if "critical_link" in text:
        return "critical road link"
    if "spatial" in text:
        return "spatial exposure corridor"
    if "random" in text:
        return "random road degradation"
    return "scenario-defined bottleneck"


def _regime_label(lens: str, row: pd.Series) -> str:
    completion = float(row["completion_rate"])
    if completion < 0.95:
        return "no policy reliably meets the window"
    if lens == "reliability":
        return f"{row['policy_id']} reliability-favored"
    if lens == "speed":
        return f"{row['policy_id']} speed-favored"
    if lens == "resource":
        return f"{row['policy_id']} resource-favored"
    return f"{row['policy_id']} favored"


def _select_sensitivity_metric(
    table: pd.DataFrame,
    *,
    requested_metric: str,
) -> str:
    available = set(str(metric) for metric in table["metric"].dropna().unique())
    if requested_metric in available:
        return requested_metric
    ranked = table.copy()
    ranked["max_abs_delta"] = pd.to_numeric(ranked["max_abs_delta"], errors="coerce")
    ranked = ranked.dropna(subset=["max_abs_delta"])
    if ranked.empty:
        return sorted(available)[0]
    index = ranked["max_abs_delta"].idxmax()
    return str(ranked.loc[index, "metric"])


def _finish_categorical_axis(ax: plt.Axes) -> None:
    ax.tick_params(axis="x", labelrotation=20)
    for label in ax.get_xticklabels():
        label.set_ha("right")
    sns.move_legend(ax, "upper left", bbox_to_anchor=(1.02, 1), borderaxespad=0)


def _save_figure(fig: plt.Figure, output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.text(0.01, 0.01, FIGURE_SCOPE, ha="left", va="bottom", fontsize=8)
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def _label_from_identifier(value: str) -> str:
    return value.replace("_", " ").strip().title()


def _scope_from_manifest(manifest: Mapping[str, Any], *, fallback: str) -> str:
    scope = str(manifest.get("result_scope", "")).strip()
    return scope or fallback


def _display_path(path: str | Path) -> str:
    filepath = Path(path)
    try:
        return filepath.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return filepath.as_posix()


__all__ = [
    "CLAIM_BOUNDARY_COLUMNS",
    "DEFAULT_FIGURES_DIR",
    "DEFAULT_OUTPUT_DIR",
    "DEFAULT_PILOT_MANIFEST_PATH",
    "DEFAULT_PILOT_SUMMARY_PATH",
    "DEFAULT_SENSITIVITY_MANIFEST_PATH",
    "DEFAULT_SENSITIVITY_SUMMARY_PATH",
    "DEFAULT_TABLES_DIR",
    "FIGURE_FILENAMES",
    "FIGURE_SCOPE",
    "FIXTURE_LABEL",
    "BOTTLENECK_ATTRIBUTION_COLUMNS",
    "MAIN_RESULT_TABLE_COLUMNS",
    "MORRIS_SUMMARY_REQUIRED_COLUMNS",
    "POLICY_REGIME_COLUMNS",
    "SENSITIVITY_RESULT_TABLE_COLUMNS",
    "SENSITIVITY_SUMMARY_REQUIRED_COLUMNS",
    "TABLE_FILENAMES",
    "build_bottleneck_attribution_table",
    "build_claim_boundary_table",
    "build_figure_table_manifest",
    "build_main_result_table",
    "build_pilot_figure_tables",
    "build_policy_regime_table",
    "build_sensitivity_result_table",
    "plot_bottleneck_attribution",
    "plot_censored_by_disruption",
    "plot_completion_by_disruption",
    "plot_policy_regime_map",
    "plot_policy_resource_tradeoff",
    "plot_sensitivity_ranking",
]
