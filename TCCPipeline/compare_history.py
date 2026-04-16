from pathlib import Path

import pandas

from TCCPipeline import run_real_pipeline


def compare_min_history(
    project_root: str | Path = ".",
    history_values: tuple[int, ...] = (1, 2, 3),
    mode: str = "previsao_nota",
) -> pandas.DataFrame:
    """Executa a pipeline várias vezes para comparar cortes de histórico mínimo."""
    rows = []

    for min_history in history_values:
        try:
            result = run_real_pipeline(project_root, min_history=min_history, mode=mode)
            metrics = result["metrics"]
            rows.append(
                {
                    "mode": mode,
                    "min_history": min_history,
                    "status": "ok",
                    "error": "",
                    "dataset_rows": len(result["dataset"]),
                    "train_rows": metrics["split"]["train_rows"],
                    "validation_rows": metrics["split"]["validation_rows"],
                    "test_rows": metrics["split"]["test_rows"],
                    "selected_regression": f"{metrics['selected_regression_candidate']['source']}::{metrics['selected_regression_candidate']['name']}",
                    "selected_classification": f"{metrics['selected_classification_candidate']['source']}::{metrics['selected_classification_candidate']['name']}",
                    "regression_mae": metrics["regression_model"]["mae"],
                    "regression_rmse": metrics["regression_model"]["rmse"],
                    "regression_acc_half": metrics["regression_model"]["accuracy_within_half_point"],
                    "regression_baseline_mae": metrics["regression_baseline"]["mae"],
                    "classification_precision": metrics["classification_model"]["precision"],
                    "classification_recall": metrics["classification_model"]["recall"],
                    "classification_f1": metrics["classification_model"]["f1"],
                    "classification_baseline_f1": metrics["classification_baseline"]["f1"],
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "mode": mode,
                    "min_history": min_history,
                    "status": "error",
                    "error": str(exc),
                    "dataset_rows": 0,
                    "train_rows": 0,
                    "validation_rows": 0,
                    "test_rows": 0,
                    "selected_regression": "",
                    "selected_classification": "",
                    "regression_mae": None,
                    "regression_rmse": None,
                    "regression_acc_half": None,
                    "regression_baseline_mae": None,
                    "classification_precision": None,
                    "classification_recall": None,
                    "classification_f1": None,
                    "classification_baseline_f1": None,
                }
            )

    return pandas.DataFrame(rows).sort_values("min_history").reset_index(drop=True)


def write_history_comparison(
    project_root: str | Path = ".",
    history_values: tuple[int, ...] = (1, 2, 3),
    mode: str = "previsao_nota",
) -> tuple[Path, Path]:
    """Salva a comparação de min_history em CSV e TXT."""
    root = Path(project_root).resolve()
    output_dir = root / "TCCPipeline" / "Result" / mode
    output_dir.mkdir(parents=True, exist_ok=True)

    comparison = compare_min_history(root, history_values=history_values, mode=mode)
    csv_path = output_dir / "history_min_comparison.csv"
    txt_path = output_dir / "history_min_comparison.txt"

    comparison.to_csv(csv_path, index=False, encoding="utf-8")

    lines = [
        "COMPARACAO DE HISTORICO MINIMO",
        "",
        f"modo={mode}",
        "",
    ]

    for _, row in comparison.iterrows():
        lines.extend([
            f"min_history={int(row['min_history'])}",
            f"- status: {row['status']}",
        ])

        if row["status"] != "ok":
            lines.extend([
                f"- error: {row['error']}",
                "",
            ])
            continue

        lines.extend([
            f"- dataset_rows: {int(row['dataset_rows'])}",
            f"- train_rows: {int(row['train_rows'])}",
            f"- validation_rows: {int(row['validation_rows'])}",
            f"- test_rows: {int(row['test_rows'])}",
            f"- selected_regression: {row['selected_regression']}",
            f"- selected_classification: {row['selected_classification']}",
            f"- regression_mae: {row['regression_mae']:.4f}",
            f"- regression_rmse: {row['regression_rmse']:.4f}",
            f"- regression_acc_half: {row['regression_acc_half']:.4f}",
            f"- regression_baseline_mae: {row['regression_baseline_mae']:.4f}",
            f"- classification_precision: {row['classification_precision']:.4f}",
            f"- classification_recall: {row['classification_recall']:.4f}",
            f"- classification_f1: {row['classification_f1']:.4f}",
            f"- classification_baseline_f1: {row['classification_baseline_f1']:.4f}",
            "",
        ])

    successful = comparison[comparison["status"] == "ok"].copy()
    lines.append("Melhores cortes observados")
    if successful.empty:
        lines.append("- nenhum corte gerou experimento valido")
    else:
        best_regression = successful.sort_values("regression_mae").iloc[0]
        best_classification = successful.sort_values("classification_f1", ascending=False).iloc[0]
        lines.append(f"- melhor regressao por MAE: min_history={int(best_regression['min_history'])} ({best_regression['regression_mae']:.4f})")
        lines.append(f"- melhor classificacao por F1: min_history={int(best_classification['min_history'])} ({best_classification['classification_f1']:.4f})")

    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return csv_path, txt_path


if __name__ == "__main__":
    csv_path, txt_path = write_history_comparison(".")
    print(csv_path)
    print(txt_path)
