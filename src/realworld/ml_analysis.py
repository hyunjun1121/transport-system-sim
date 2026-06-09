"""Bounded Phase 10 post-simulation ML analysis helpers.

These helpers derive risk labels from simulation output rows and optionally fit
an XGBoost classifier. The outputs are descriptive decision-support artifacts;
they do not validate simulation calibration or operational forecasting.
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ANALYSIS_DIR = (
    PROJECT_ROOT
    / "results"
    / "realworld_pilot"
    / "phase8_compact_scoped_20260605"
    / "analysis"
)
DEFAULT_SOURCE_RESULTS = (
    PROJECT_ROOT
    / "results"
    / "realworld_pilot"
    / "phase8_compact_scoped_20260605"
    / "pilot_staged_results.csv"
)
DEFAULT_SOURCE_MANIFEST = (
    PROJECT_ROOT
    / "results"
    / "realworld_pilot"
    / "phase8_compact_scoped_20260605"
    / "pilot_staged_manifest.json"
)
ML_CLAIM_SCOPE = (
    "Phase 10 post-simulation ML decision-support analysis only; labels are "
    "derived from simulation outputs and do not prove real-world calibration, "
    "publication readiness, final-study readiness, formal acceptance, or "
    "operational forecasting."
)
LABEL_COLUMNS = (
    "row_id",
    "region_id",
    "graph_source",
    "policy_id",
    "scenario_id",
    "scenario_family",
    "scenario_type",
    "disruption_mode",
    "seed",
    "mode",
    "completion_rate",
    "censored_count",
    "risk_label",
    "risk_label_rule",
    "claim_scope",
)
PREDICTION_COLUMNS = (
    *LABEL_COLUMNS,
    "split",
    "predicted_risk_label",
    "prediction_correct",
    "model_status",
)
IMPORTANCE_COLUMNS = (
    "feature",
    "importance",
    "importance_type",
    "model_status",
    "claim_scope",
)
FEATURE_CATEGORICAL_COLUMNS = (
    "policy_id",
    "scenario_family",
    "scenario_type",
    "disruption_mode",
    "mode",
)
FEATURE_NUMERIC_COLUMNS = ("selected_edge_count",)


def load_simulation_rows(path: str | Path) -> list[dict[str, str]]:
    """Load simulation result CSV rows."""

    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_label_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    claim_scope: str = ML_CLAIM_SCOPE,
) -> list[dict[str, str]]:
    """Derive risk labels from completion and censoring fields."""

    label_rows: list[dict[str, str]] = []
    for index, row in enumerate(rows, start=1):
        completion = _float(row.get("completion_rate"), default=0.0)
        censored = int(_float(row.get("censored_count"), default=0.0))
        risk_label = _risk_label(completion, censored)
        label_rows.append(
            {
                "row_id": f"simrow-{index:06d}",
                "region_id": _text(row.get("region_id")),
                "graph_source": _text(row.get("graph_source")),
                "policy_id": _text(row.get("policy_id")),
                "scenario_id": _text(row.get("scenario_id")),
                "scenario_family": _text(row.get("scenario_family")),
                "scenario_type": _text(row.get("scenario_type")),
                "disruption_mode": _text(row.get("disruption_mode")),
                "seed": _text(row.get("seed")),
                "mode": _text(row.get("mode")),
                "completion_rate": f"{completion:.6g}",
                "censored_count": str(censored),
                "risk_label": risk_label,
                "risk_label_rule": _risk_label_rule(),
                "claim_scope": claim_scope,
            }
        )
    return label_rows


def write_ml_analysis_outputs(
    *,
    rows: Sequence[Mapping[str, Any]],
    output_dir: str | Path = DEFAULT_ANALYSIS_DIR,
    source_results_path: str | Path = DEFAULT_SOURCE_RESULTS,
    source_manifest_path: str | Path = DEFAULT_SOURCE_MANIFEST,
    output_prefix: str = "pilot_staged_scoped",
    allow_xgboost: bool = True,
    device: str = "cpu",
    command: Sequence[str] | None = None,
    claim_scope: str = ML_CLAIM_SCOPE,
) -> dict[str, Any]:
    """Write label, prediction, feature-importance, and manifest artifacts."""

    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    labels_path = directory / f"{output_prefix}_ml_labels.csv"
    predictions_path = directory / f"{output_prefix}_ml_predictions.csv"
    importance_path = directory / f"{output_prefix}_ml_feature_importance.csv"
    metrics_path = directory / f"{output_prefix}_ml_metrics.json"
    manifest_path = directory / f"{output_prefix}_ml_manifest.json"
    doc_path = directory / f"{output_prefix}_ml_analysis.md"

    label_rows = build_label_rows(rows, claim_scope=claim_scope)
    feature_frame = _build_feature_frame(rows)
    model_result = _fit_or_fallback_model(
        feature_frame["matrix"],
        [row["risk_label"] for row in label_rows],
        feature_frame["feature_names"],
        allow_xgboost=allow_xgboost,
        device=device,
    )
    prediction_rows = _prediction_rows(
        label_rows=label_rows,
        predictions=model_result["predictions"],
        splits=model_result["splits"],
        model_status=model_result["model_status"],
    )
    importance_rows = _importance_rows(
        feature_names=feature_frame["feature_names"],
        importances=model_result["feature_importance"],
        model_status=model_result["model_status"],
        claim_scope=claim_scope,
    )
    metrics = _metrics_payload(
        labels=[row["risk_label"] for row in label_rows],
        predictions=model_result["predictions"],
        splits=model_result["splits"],
        model_result=model_result,
        source_results_path=source_results_path,
        source_manifest_path=source_manifest_path,
        output_prefix=output_prefix,
        command=command,
        claim_scope=claim_scope,
    )

    _write_csv(labels_path, LABEL_COLUMNS, label_rows)
    _write_csv(predictions_path, PREDICTION_COLUMNS, prediction_rows)
    _write_csv(importance_path, IMPORTANCE_COLUMNS, importance_rows)
    metrics["outputs"] = {
        "labels": _display_path(labels_path),
        "predictions": _display_path(predictions_path),
        "feature_importance": _display_path(importance_path),
        "metrics": _display_path(metrics_path),
        "manifest": _display_path(manifest_path),
        "doc": _display_path(doc_path),
    }
    metrics_path.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest = dict(metrics)
    manifest.update(
        {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "label_row_count": len(label_rows),
            "prediction_row_count": len(prediction_rows),
            "feature_importance_row_count": len(importance_rows),
            "publication_ready": False,
            "final_study_ready": False,
            "formal_acceptance_evidence": False,
        }
    )
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc_path.write_text(_ml_markdown(manifest), encoding="utf-8")
    return {
        "labels_path": labels_path,
        "predictions_path": predictions_path,
        "importance_path": importance_path,
        "metrics_path": metrics_path,
        "manifest_path": manifest_path,
        "doc_path": doc_path,
        "manifest": manifest,
    }


def _risk_label(completion: float, censored: int) -> str:
    if completion >= 0.95 and censored == 0:
        return "normal"
    if completion >= 0.80:
        return "watch"
    if completion >= 0.50:
        return "risk"
    return "failure"


def _risk_label_rule() -> str:
    return (
        "normal if completion_rate>=0.95 and censored_count=0; watch if "
        "completion_rate>=0.80; risk if completion_rate>=0.50; otherwise failure"
    )


def _build_feature_frame(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    categories = {
        column: sorted({_text(row.get(column)) for row in rows})
        for column in FEATURE_CATEGORICAL_COLUMNS
    }
    feature_names: list[str] = []
    for column in FEATURE_NUMERIC_COLUMNS:
        feature_names.append(column)
    for column in FEATURE_CATEGORICAL_COLUMNS:
        feature_names.extend(f"{column}={value}" for value in categories[column])

    matrix: list[list[float]] = []
    for row in rows:
        values: list[float] = [
            _float(row.get(column), default=0.0) for column in FEATURE_NUMERIC_COLUMNS
        ]
        for column in FEATURE_CATEGORICAL_COLUMNS:
            actual = _text(row.get(column))
            values.extend(1.0 if actual == value else 0.0 for value in categories[column])
        matrix.append(values)
    return {"feature_names": feature_names, "matrix": matrix}


def _fit_or_fallback_model(
    matrix: Sequence[Sequence[float]],
    labels: Sequence[str],
    feature_names: Sequence[str],
    *,
    allow_xgboost: bool,
    device: str,
) -> dict[str, Any]:
    splits = ["test" if index % 5 == 0 else "train" for index in range(len(labels))]
    label_values = sorted(set(labels))
    if len(label_values) < 2:
        predictions = [labels[0] if labels else "" for _ in labels]
        return {
            "model_status": "skipped_single_class",
            "model_package": "none",
            "device": "not_used",
            "class_labels": label_values,
            "splits": splits,
            "predictions": predictions,
            "feature_importance": {name: 0.0 for name in feature_names},
        }
    if not allow_xgboost:
        return _majority_fallback(labels, splits, feature_names, "disabled_by_request")
    try:
        import xgboost as xgb  # type: ignore
    except Exception:
        return _majority_fallback(labels, splits, feature_names, "missing_xgboost")

    label_to_id = {label: index for index, label in enumerate(label_values)}
    train_indices = [index for index, split in enumerate(splits) if split == "train"]
    if len({labels[index] for index in train_indices}) < 2:
        return _majority_fallback(labels, splits, feature_names, "train_split_single_class")

    train_x = [matrix[index] for index in train_indices]
    train_y = [label_to_id[labels[index]] for index in train_indices]
    full = xgb.DMatrix(matrix, feature_names=list(feature_names))
    train = xgb.DMatrix(train_x, label=train_y, feature_names=list(feature_names))
    params: dict[str, Any] = {
        "tree_method": "hist",
        "device": device,
        "eta": 0.2,
        "max_depth": 3,
        "seed": 1701,
    }
    if len(label_values) == 2:
        params.update({"objective": "binary:logistic", "eval_metric": "logloss"})
        booster = xgb.train(params, train, num_boost_round=20)
        raw_predictions = booster.predict(full)
        predicted_ids = [1 if float(value) >= 0.5 else 0 for value in raw_predictions]
    else:
        params.update(
            {
                "objective": "multi:softprob",
                "eval_metric": "mlogloss",
                "num_class": len(label_values),
            }
        )
        booster = xgb.train(params, train, num_boost_round=20)
        raw_predictions = booster.predict(full)
        predicted_ids = [
            max(range(len(row)), key=lambda index: float(row[index]))
            for row in raw_predictions
        ]
    score = booster.get_score(importance_type="gain")
    return {
        "model_status": "xgboost_trained",
        "model_package": "xgboost",
        "device": device,
        "class_labels": label_values,
        "splits": splits,
        "predictions": [label_values[index] for index in predicted_ids],
        "feature_importance": {name: float(score.get(name, 0.0)) for name in feature_names},
    }


def _majority_fallback(
    labels: Sequence[str],
    splits: Sequence[str],
    feature_names: Sequence[str],
    reason: str,
) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for index, label in enumerate(labels):
        if splits[index] == "train":
            counts[label] = counts.get(label, 0) + 1
    majority = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]
    return {
        "model_status": f"majority_fallback_{reason}",
        "model_package": "none",
        "device": "not_used",
        "class_labels": sorted(set(labels)),
        "splits": list(splits),
        "predictions": [majority for _ in labels],
        "feature_importance": {name: 0.0 for name in feature_names},
    }


def _prediction_rows(
    *,
    label_rows: Sequence[Mapping[str, str]],
    predictions: Sequence[str],
    splits: Sequence[str],
    model_status: str,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for label_row, prediction, split in zip(label_rows, predictions, splits):
        rows.append(
            {
                **dict(label_row),
                "split": split,
                "predicted_risk_label": prediction,
                "prediction_correct": str(prediction == label_row["risk_label"]).lower(),
                "model_status": model_status,
            }
        )
    return rows


def _importance_rows(
    *,
    feature_names: Sequence[str],
    importances: Mapping[str, float],
    model_status: str,
    claim_scope: str,
) -> list[dict[str, str]]:
    rows = [
        {
            "feature": name,
            "importance": f"{float(importances.get(name, 0.0)):.10g}",
            "importance_type": "gain" if model_status == "xgboost_trained" else "not_available",
            "model_status": model_status,
            "claim_scope": claim_scope,
        }
        for name in feature_names
    ]
    return sorted(rows, key=lambda row: (-_float(row["importance"], default=0.0), row["feature"]))


def _metrics_payload(
    *,
    labels: Sequence[str],
    predictions: Sequence[str],
    splits: Sequence[str],
    model_result: Mapping[str, Any],
    source_results_path: str | Path,
    source_manifest_path: str | Path,
    output_prefix: str,
    command: Sequence[str] | None,
    claim_scope: str,
) -> dict[str, Any]:
    train_indices = [index for index, split in enumerate(splits) if split == "train"]
    test_indices = [index for index, split in enumerate(splits) if split == "test"]
    return {
        "result_scope": claim_scope,
        "command": list(command or []),
        "output_prefix": output_prefix,
        "source_results_path": _display_path(source_results_path),
        "source_results_sha256": _sha256_file(source_results_path),
        "source_manifest_path": _display_path(source_manifest_path),
        "source_manifest_sha256": _sha256_file(source_manifest_path),
        "model_status": model_result["model_status"],
        "model_package": model_result["model_package"],
        "model_device": model_result["device"],
        "class_labels": list(model_result["class_labels"]),
        "row_count": len(labels),
        "train_row_count": len(train_indices),
        "test_row_count": len(test_indices),
        "label_counts": _counts(labels),
        "train_metrics": _classification_metrics(
            [labels[index] for index in train_indices],
            [predictions[index] for index in train_indices],
        ),
        "test_metrics": _classification_metrics(
            [labels[index] for index in test_indices],
            [predictions[index] for index in test_indices],
        ),
        "leakage_boundary": (
            "Features are limited to policy/scenario/mode fields and selected edge "
            "count; completion_rate and censored_count are used only for label "
            "derivation, not as model features."
        ),
        "publication_ready": False,
        "final_study_ready": False,
        "formal_acceptance_evidence": False,
    }


def _classification_metrics(labels: Sequence[str], predictions: Sequence[str]) -> dict[str, Any]:
    if not labels:
        return {"accuracy": "", "macro_f1": "", "row_count": 0}
    correct = sum(1 for actual, predicted in zip(labels, predictions) if actual == predicted)
    label_set = sorted(set(labels) | set(predictions))
    f1_values: list[float] = []
    for label in label_set:
        true_positive = sum(
            1 for actual, predicted in zip(labels, predictions) if actual == label and predicted == label
        )
        false_positive = sum(
            1 for actual, predicted in zip(labels, predictions) if actual != label and predicted == label
        )
        false_negative = sum(
            1 for actual, predicted in zip(labels, predictions) if actual == label and predicted != label
        )
        precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
        recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
        f1_values.append(2 * precision * recall / (precision + recall) if precision + recall else 0.0)
    return {
        "accuracy": correct / len(labels),
        "macro_f1": sum(f1_values) / len(f1_values),
        "row_count": len(labels),
    }


def _ml_markdown(manifest: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Phase 10 ML Analysis",
            "",
            f"- Scope: {manifest['result_scope']}",
            f"- Model status: `{manifest['model_status']}`",
            f"- Source rows: `{manifest['row_count']}`",
            f"- Labels: `{json.dumps(manifest['label_counts'], sort_keys=True)}`",
            f"- Publication ready: `{str(manifest['publication_ready']).lower()}`",
            f"- Final-study ready: `{str(manifest['final_study_ready']).lower()}`",
            f"- Formal acceptance evidence: `{str(manifest['formal_acceptance_evidence']).lower()}`",
            "",
        ]
    )


def _write_csv(path: Path, fieldnames: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def _counts(values: Sequence[str]) -> dict[str, int]:
    result: dict[str, int] = {}
    for value in values:
        result[value] = result.get(value, 0) + 1
    return dict(sorted(result.items()))


def _float(value: Any, *, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _text(value: Any) -> str:
    return "" if value is None else str(value)


def _sha256_file(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _display_path(path: str | Path) -> str:
    try:
        return Path(path).resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return Path(path).as_posix()
