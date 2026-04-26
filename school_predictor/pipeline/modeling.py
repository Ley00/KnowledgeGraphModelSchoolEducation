import math
import pickle

import numpy
import pandas
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor, RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    recall_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder

from school_predictor.project import ensure_parent_dir


def temporal_split(dataset: pandas.DataFrame) -> dict[str, pandas.DataFrame]:
    """Separa treino, validação e teste usando anos letivos.

    A divisão temporal evita vazamento entre passado e futuro e deixa
    a avaliação mais próxima do uso real do sistema na escola.
    """
    years = sorted(dataset["NomePeriodo"].dropna().astype(int).unique().tolist())
    if len(years) < 2:
        raise ValueError("A pipeline precisa de pelo menos dois anos letivos para validacao temporal.")

    test_year = years[-1]
    validation_year = years[-2] if len(years) >= 3 else years[-1]

    train_df = dataset[dataset["NomePeriodo"] < validation_year].copy()
    validation_df = dataset[dataset["NomePeriodo"] == validation_year].copy()
    test_df = dataset[dataset["NomePeriodo"] == test_year].copy()

    if train_df.empty:
        train_df = dataset[dataset["NomePeriodo"] < test_year].copy()
    if validation_df.empty:
        validation_df = test_df.copy()

    return {
        "train": train_df,
        "validation": validation_df,
        "test": test_df,
        "train_years": sorted(train_df["NomePeriodo"].astype(int).unique().tolist()),
        "validation_years": sorted(validation_df["NomePeriodo"].astype(int).unique().tolist()),
        "test_years": sorted(test_df["NomePeriodo"].astype(int).unique().tolist()),
    }


def build_preprocessor(feature_columns: list[str], categorical_columns: list[str], categorical_strategy: str = "onehot") -> ColumnTransformer:
    """Cria o pré-processamento de colunas numéricas e categóricas."""
    numeric_columns = [column for column in feature_columns if column not in categorical_columns]
    if categorical_strategy == "ordinal":
        categorical_pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)),
        ])
    else:
        categorical_pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ])

    return ColumnTransformer(
        transformers=[
            ("categorical", categorical_pipeline, categorical_columns),
            ("numeric", Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
            ]), numeric_columns),
        ]
    )


def build_regression_candidates(feature_columns: list[str], categorical_columns: list[str]) -> dict[str, Pipeline]:
    """Monta os modelos candidatos de regressão."""
    return {
        "random_forest_regressor": Pipeline(
            steps=[
                ("preprocessor", build_preprocessor(feature_columns, categorical_columns, categorical_strategy="onehot")),
                ("model", RandomForestRegressor(
                n_estimators=80,
                max_depth=10,
                min_samples_leaf=5,
                max_samples=0.5,
                random_state=42,
                n_jobs=1,
                )),
            ]
        ),
        "hist_gradient_boosting_regressor": Pipeline(
            steps=[
                ("preprocessor", build_preprocessor(feature_columns, categorical_columns, categorical_strategy="ordinal")),
                ("model", HistGradientBoostingRegressor(
                    max_depth=8,
                    learning_rate=0.05,
                    max_iter=250,
                    min_samples_leaf=40,
                    random_state=42,
                    early_stopping=False,
                )),
            ]
        ),
    }


def build_classification_candidates(feature_columns: list[str], categorical_columns: list[str]) -> dict[str, Pipeline]:
    """Monta os modelos candidatos de classificação."""
    return {
        "random_forest_classifier": Pipeline(
            steps=[
                ("preprocessor", build_preprocessor(feature_columns, categorical_columns, categorical_strategy="onehot")),
                ("model", RandomForestClassifier(
                    n_estimators=80,
                    max_depth=10,
                    min_samples_leaf=5,
                max_samples=0.5,
                class_weight="balanced",
                random_state=42,
                n_jobs=1,
                )),
            ]
        ),
        "hist_gradient_boosting_classifier": Pipeline(
            steps=[
                ("preprocessor", build_preprocessor(feature_columns, categorical_columns, categorical_strategy="ordinal")),
                ("model", HistGradientBoostingClassifier(
                    max_depth=8,
                    learning_rate=0.05,
                    max_iter=250,
                    min_samples_leaf=40,
                    random_state=42,
                    class_weight="balanced",
                    early_stopping=False,
                )),
            ]
        ),
    }


def evaluate_regression(y_true: pandas.Series, y_pred) -> dict[str, float]:
    """Calcula as métricas de regressão usadas na pipeline."""
    rmse = math.sqrt(mean_squared_error(y_true, y_pred))
    within_half = (abs(y_true - y_pred) <= 0.5).mean()
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(rmse),
        "accuracy_within_half_point": float(within_half),
    }


def evaluate_classification(y_true: pandas.Series, y_pred) -> dict[str, float]:
    """Calcula as métricas de classificação usadas na pipeline."""
    return {
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }


def classify_score_band(series: pandas.Series) -> pandas.Series:
    """Agrupa notas em faixas para análise de erro por banda de desempenho."""
    return pandas.cut(
        series.astype(float),
        bins=[-numpy.inf, 5.99, 6.99, 7.99, 8.99, numpy.inf],
        labels=["abaixo_6", "6_a_6_99", "7_a_7_99", "8_a_8_99", "9_ou_mais"],
    )


def build_regression_baselines(frame: pandas.DataFrame) -> dict[str, pandas.Series]:
    """Retorna os baselines de regressão disponíveis no dataset."""
    return {
        "ultima_nota": frame["baseline_ultima_nota"],
        "media_duas_ultimas": frame["baseline_media_duas_ultimas"],
        "media_tres_ultimas": frame["baseline_media_tres_ultimas"],
        "baseline_hibrido": frame["baseline_hibrido"],
    }


def build_classification_baselines(frame: pandas.DataFrame) -> dict[str, pandas.Series]:
    """Converte os baselines de nota em regras simples de classificação de risco."""
    return {name: (values < 6.0).astype(int) for name, values in build_regression_baselines(frame).items()}


def select_best_regression_model(
    train_df: pandas.DataFrame,
    validation_df: pandas.DataFrame,
    feature_columns: list[str],
    categorical_columns: list[str],
) -> tuple[str, Pipeline, dict, str]:
    """Compara candidatos de regressão na validação e escolhe o melhor por MAE."""
    X_train = train_df[feature_columns]
    X_validation = validation_df[feature_columns]
    y_train = train_df["target_nota_proxima"]
    y_validation = validation_df["target_nota_proxima"]

    candidate_metrics = {}
    best_name = None
    best_model = None
    best_score = float("inf")
    best_source = "model"

    for name, model in build_regression_candidates(feature_columns, categorical_columns).items():
        model.fit(X_train, y_train)
        predictions = model.predict(X_validation)
        metrics = evaluate_regression(y_validation, predictions)
        candidate_metrics[name] = metrics
        if metrics["mae"] < best_score:
            best_score = metrics["mae"]
            best_name = name
            best_model = model

    for name, predictions in build_regression_baselines(validation_df).items():
        metrics = evaluate_regression(y_validation, predictions)
        candidate_metrics[f"baseline::{name}"] = metrics
        if metrics["mae"] < best_score:
            best_score = metrics["mae"]
            best_name = name
            best_model = None
            best_source = "baseline"

    return best_name, best_model, candidate_metrics, best_source


def select_best_classification_model(
    train_df: pandas.DataFrame,
    validation_df: pandas.DataFrame,
    feature_columns: list[str],
    categorical_columns: list[str],
) -> tuple[str, Pipeline, dict, str]:
    """Compara candidatos de classificação na validação e escolhe o melhor por F1."""
    X_train = train_df[feature_columns]
    X_validation = validation_df[feature_columns]
    y_train = train_df["target_risco_proxima"]
    y_validation = validation_df["target_risco_proxima"]

    candidate_metrics = {}
    best_name = None
    best_model = None
    best_score = float("-inf")
    best_source = "model"

    for name, model in build_classification_candidates(feature_columns, categorical_columns).items():
        model.fit(X_train, y_train)
        predictions = model.predict(X_validation)
        metrics = evaluate_classification(y_validation, predictions)
        candidate_metrics[name] = metrics
        if metrics["f1"] > best_score:
            best_score = metrics["f1"]
            best_name = name
            best_model = model

    for name, predictions in build_classification_baselines(validation_df).items():
        metrics = evaluate_classification(y_validation, predictions)
        candidate_metrics[f"baseline::{name}"] = metrics
        if metrics["f1"] > best_score:
            best_score = metrics["f1"]
            best_name = name
            best_model = None
            best_source = "baseline"

    return best_name, best_model, candidate_metrics, best_source


def train_and_evaluate(dataset: pandas.DataFrame, feature_columns: list[str], categorical_columns: list[str]) -> dict:
    """Executa a parte central da modelagem.

    Esse bloco:
    1. aplica o split temporal
    2. remove colunas sem sinal útil no treino
    3. escolhe o melhor candidato em validação
    4. re-treina no conjunto treino + validação
    5. testa no ano final
    6. produz predições, métricas e análise de erro
    """
    split = temporal_split(dataset)
    train_df = split["train"]
    validation_df = split["validation"]
    test_df = split["test"]

    # Remove colunas sem variabilidade ou totalmente vazias no treino.
    effective_feature_columns = [
        column for column in feature_columns
        if (
            not train_df[column].isna().all()
            and train_df[column].dropna().nunique() > 1
        )
    ]
    effective_categorical_columns = [column for column in categorical_columns if column in effective_feature_columns]
    regression_choice = select_best_regression_model(
        train_df,
        validation_df,
        effective_feature_columns,
        effective_categorical_columns,
    )
    classification_choice = select_best_classification_model(
        train_df,
        validation_df,
        effective_feature_columns,
        effective_categorical_columns,
    )

    best_regression_name, best_regression_model, regression_candidates, regression_source = regression_choice
    best_classification_name, best_classification_model, classification_candidates, classification_source = classification_choice

    # Após escolher o melhor candidato, o modelo é re-treinado com mais dados.
    final_train_df = pandas.concat([train_df, validation_df], ignore_index=True)
    X_final_train = final_train_df[effective_feature_columns]
    X_test = test_df[effective_feature_columns]
    y_final_reg = final_train_df["target_nota_proxima"]
    y_final_clf = final_train_df["target_risco_proxima"]
    y_test_reg = test_df["target_nota_proxima"]
    y_test_clf = test_df["target_risco_proxima"]

    regression_baselines_test = build_regression_baselines(test_df)
    classification_baselines_test = build_classification_baselines(test_df)

    if regression_source == "model":
        final_regressor = build_regression_candidates(
            effective_feature_columns,
            effective_categorical_columns,
        )[best_regression_name]
        final_regressor.fit(X_final_train, y_final_reg)
        pred_reg = final_regressor.predict(X_test)
    else:
        final_regressor = None
        pred_reg = regression_baselines_test[best_regression_name]

    if classification_source == "model":
        final_classifier = build_classification_candidates(
            effective_feature_columns,
            effective_categorical_columns,
        )[best_classification_name]
        final_classifier.fit(X_final_train, y_final_clf)
        pred_clf = final_classifier.predict(X_test)
    else:
        final_classifier = None
        pred_clf = classification_baselines_test[best_classification_name]

    baseline_reg = regression_baselines_test["ultima_nota"]
    baseline_clf = classification_baselines_test["ultima_nota"]

    metrics = {
        "regression_model": evaluate_regression(y_test_reg, pred_reg),
        "regression_baseline": evaluate_regression(y_test_reg, baseline_reg),
        "classification_model": evaluate_classification(y_test_clf, pred_clf),
        "classification_baseline": evaluate_classification(y_test_clf, baseline_clf),
        "regression_validation_candidates": regression_candidates,
        "classification_validation_candidates": classification_candidates,
        "selected_regression_candidate": {
            "name": best_regression_name,
            "source": regression_source,
        },
        "selected_classification_candidate": {
            "name": best_classification_name,
            "source": classification_source,
        },
        "split": {
            "train_years": split["train_years"],
            "validation_years": split["validation_years"],
            "test_years": split["test_years"],
            "train_rows": int(len(train_df)),
            "validation_rows": int(len(validation_df)),
            "test_rows": int(len(test_df)),
            "feature_columns": effective_feature_columns,
        },
    }

    # A tabela de predictions é a base analítica principal para inspeção de resultados.
    predictions = test_df[
        ["IDAluno", "NomeAluno", "NomePeriodo", "NomeSerie", "NomeDisciplina", "NomeEtapa", "ValorMedia", "target_nota_proxima", "target_risco_proxima"]
    ].copy()
    predictions["predicted_next_grade"] = pred_reg
    predictions["predicted_risk_flag"] = pred_clf
    predictions["baseline_next_grade"] = baseline_reg
    predictions["selected_regression_candidate"] = best_regression_name
    predictions["selected_classification_candidate"] = best_classification_name
    predictions["absolute_error"] = (predictions["predicted_next_grade"] - predictions["target_nota_proxima"]).abs()
    predictions["signed_error"] = predictions["predicted_next_grade"] - predictions["target_nota_proxima"]
    predictions["score_band"] = classify_score_band(predictions["target_nota_proxima"]).astype(str)
    predictions["risk_hit"] = (predictions["predicted_risk_flag"] == predictions["target_risco_proxima"]).astype(int)

    error_analysis = build_error_analysis(predictions)

    return {
        "models": {
            "regression": final_regressor,
            "classification": final_classifier,
        },
        "metrics": metrics,
        "predictions": predictions,
        "error_analysis": error_analysis,
    }


def summarize_group_errors(frame: pandas.DataFrame, group_column: str) -> pandas.DataFrame:
    """Resume erro médio e acurácia de risco por grupo."""
    grouped = (
        frame.groupby(group_column, dropna=False)
        .agg(
            samples=("IDAluno", "size"),
            mae=("absolute_error", "mean"),
            rmse=("signed_error", lambda s: float(math.sqrt((s ** 2).mean()))),
            mean_signed_error=("signed_error", "mean"),
            risk_accuracy=("risk_hit", "mean"),
            actual_risk_rate=("target_risco_proxima", "mean"),
        )
        .reset_index()
        .sort_values(["mae", "samples"], ascending=[False, False], kind="stable")
    )
    grouped["samples"] = grouped["samples"].astype(int)
    return grouped


def build_error_analysis(predictions: pandas.DataFrame) -> dict[str, pandas.DataFrame]:
    """Constrói a análise de erro por disciplina, série e faixa de nota."""
    return {
        "by_subject": summarize_group_errors(predictions, "NomeDisciplina"),
        "by_series": summarize_group_errors(predictions, "NomeSerie"),
        "by_band": summarize_group_errors(predictions, "score_band"),
    }


def save_artifacts(paths, dataset: pandas.DataFrame, training_output: dict) -> None:
    """Salva todos os artefatos gerados na execução do modo."""
    paths.output_dir.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(paths.dataset_csv, index=False, encoding="utf-8")
    training_output["predictions"].to_csv(paths.predictions_csv, index=False, encoding="utf-8")
    training_output["error_analysis"]["by_subject"].to_csv(paths.error_by_subject_csv, index=False, encoding="utf-8")
    training_output["error_analysis"]["by_series"].to_csv(paths.error_by_series_csv, index=False, encoding="utf-8")
    training_output["error_analysis"]["by_band"].to_csv(paths.error_by_band_csv, index=False, encoding="utf-8")

    with open(paths.model_pkl, "wb") as file:
        pickle.dump(
            {
                "models": training_output["models"],
                "metrics": training_output["metrics"],
                "selected_regression_candidate": training_output["metrics"]["selected_regression_candidate"],
                "selected_classification_candidate": training_output["metrics"]["selected_classification_candidate"],
            },
            file,
        )

    write_error_summary(paths, training_output["error_analysis"])


def write_error_summary(paths, error_analysis: dict[str, pandas.DataFrame]) -> None:
    """Gera um resumo textual curto dos principais pontos de erro."""
    by_subject = error_analysis["by_subject"].head(10)
    by_series = error_analysis["by_series"].head(10)
    by_band = error_analysis["by_band"].head(10)

    lines = [
        "ANALISE DE ERRO DA PIPELINE",
        "",
        "Piores disciplinas por MAE",
    ]
    for _, row in by_subject.iterrows():
        lines.append(
            f"- {row['NomeDisciplina']}: samples={int(row['samples'])}, mae={row['mae']:.4f}, rmse={row['rmse']:.4f}, risk_accuracy={row['risk_accuracy']:.4f}"
        )

    lines.extend(["", "Series com maior erro medio"])
    for _, row in by_series.iterrows():
        lines.append(
            f"- {row['NomeSerie']}: samples={int(row['samples'])}, mae={row['mae']:.4f}, rmse={row['rmse']:.4f}, risk_accuracy={row['risk_accuracy']:.4f}"
        )

    lines.extend(["", "Faixas de nota com maior erro medio"])
    for _, row in by_band.iterrows():
        lines.append(
            f"- {row['score_band']}: samples={int(row['samples'])}, mae={row['mae']:.4f}, rmse={row['rmse']:.4f}, risk_accuracy={row['risk_accuracy']:.4f}"
        )

    ensure_parent_dir(paths.error_summary_txt)
    paths.error_summary_txt.write_text("\n".join(lines), encoding="utf-8")


def write_report(paths, dataset: pandas.DataFrame, training_output: dict) -> None:
    """Escreve o relatório técnico final da execução do modo."""
    metrics = training_output["metrics"]
    error_analysis = training_output["error_analysis"]
    lines = [
        "PIPELINE REAL DE PREDICAO ESCOLAR",
        "",
        f"Modo de execução: {paths.mode}",
        "Resumo do dataset",
        f"- linhas para modelagem: {len(dataset)}",
        f"- alunos unicos: {dataset['IDAluno'].nunique()}",
        f"- disciplinas unicas: {dataset['NomeDisciplina'].nunique()}",
        f"- anos letivos unicos: {dataset['NomePeriodo'].nunique()}",
        "",
        "Split temporal",
        f"- anos de treino: {metrics['split']['train_years']}",
        f"- anos de validacao: {metrics['split']['validation_years']}",
        f"- anos de teste: {metrics['split']['test_years']}",
        f"- linhas de treino: {metrics['split']['train_rows']}",
        f"- linhas de validacao: {metrics['split']['validation_rows']}",
        f"- linhas de teste: {metrics['split']['test_rows']}",
        f"- historico minimo por disciplina para entrar na modelagem: {paths.min_history}",
        f"- candidato selecionado para regressao: {metrics['selected_regression_candidate']['source']}::{metrics['selected_regression_candidate']['name']}",
        f"- candidato selecionado para classificacao: {metrics['selected_classification_candidate']['source']}::{metrics['selected_classification_candidate']['name']}",
        "",
        "Ranking de regressao na validacao (ordenado por mae)",
    ]

    regression_ranking = sorted(
        metrics["regression_validation_candidates"].items(),
        key=lambda item: item[1]["mae"],
    )
    for name, values in regression_ranking:
        lines.append(
            f"- {name}: mae={values['mae']:.4f}, rmse={values['rmse']:.4f}, acerto<=0.5={values['accuracy_within_half_point']:.4f}"
        )

    lines.extend([
        "",
        "Ranking de classificacao na validacao (ordenado por f1)",
    ])

    classification_ranking = sorted(
        metrics["classification_validation_candidates"].items(),
        key=lambda item: item[1]["f1"],
        reverse=True,
    )
    for name, values in classification_ranking:
        lines.append(
            f"- {name}: precision={values['precision']:.4f}, recall={values['recall']:.4f}, f1={values['f1']:.4f}"
        )

    lines.extend([
        "",
        "Analise de erro",
        f"- por disciplina: {paths.error_by_subject_csv}",
        f"- por serie: {paths.error_by_series_csv}",
        f"- por faixa de nota: {paths.error_by_band_csv}",
        f"- resumo textual: {paths.error_summary_txt}",
        "",
        "Principais pontos de erro",
    ])

    for _, row in error_analysis["by_subject"].head(5).iterrows():
        lines.append(
            f"- disciplina critica: {row['NomeDisciplina']} | samples={int(row['samples'])} | mae={row['mae']:.4f} | risk_accuracy={row['risk_accuracy']:.4f}"
        )
    for _, row in error_analysis["by_series"].head(3).iterrows():
        lines.append(
            f"- serie critica: {row['NomeSerie']} | samples={int(row['samples'])} | mae={row['mae']:.4f} | risk_accuracy={row['risk_accuracy']:.4f}"
        )
    for _, row in error_analysis["by_band"].head(3).iterrows():
        lines.append(
            f"- faixa critica: {row['score_band']} | samples={int(row['samples'])} | mae={row['mae']:.4f} | risk_accuracy={row['risk_accuracy']:.4f}"
        )

    lines.extend([
        "",
        "Regressao: previsao da proxima nota",
        f"- modelo mae: {metrics['regression_model']['mae']:.4f}",
        f"- modelo rmse: {metrics['regression_model']['rmse']:.4f}",
        f"- modelo acerto <= 0.5: {metrics['regression_model']['accuracy_within_half_point']:.4f}",
        f"- baseline mae: {metrics['regression_baseline']['mae']:.4f}",
        f"- baseline rmse: {metrics['regression_baseline']['rmse']:.4f}",
        f"- baseline acerto <= 0.5: {metrics['regression_baseline']['accuracy_within_half_point']:.4f}",
        "",
        "Classificacao: risco de proxima nota abaixo de 6",
        f"- modelo precision: {metrics['classification_model']['precision']:.4f}",
        f"- modelo recall: {metrics['classification_model']['recall']:.4f}",
        f"- modelo f1: {metrics['classification_model']['f1']:.4f}",
        f"- baseline precision: {metrics['classification_baseline']['precision']:.4f}",
        f"- baseline recall: {metrics['classification_baseline']['recall']:.4f}",
        f"- baseline f1: {metrics['classification_baseline']['f1']:.4f}",
        "",
        "Arquivos gerados",
        f"- dataset: {paths.dataset_csv}",
        f"- predições: {paths.predictions_csv}",
        f"- modelo: {paths.model_pkl}",
    ])

    ensure_parent_dir(paths.metrics_txt)
    paths.metrics_txt.write_text("\n".join(lines), encoding="utf-8")
