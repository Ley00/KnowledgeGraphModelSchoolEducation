from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PipelinePaths:
    """Agrupa todos os caminhos de entrada e saída de uma execução da pipeline."""
    mode: str
    project_root: Path
    school_report_dir: Path
    grades_csv: Path
    absences_csv: Path
    payments_csv: Path
    teachers_csv: Path
    output_dir: Path
    dataset_csv: Path
    predictions_csv: Path
    metrics_txt: Path
    model_pkl: Path
    error_by_subject_csv: Path
    error_by_series_csv: Path
    error_by_band_csv: Path
    error_summary_txt: Path
    min_history: int

    @classmethod
    def from_project_root(cls, project_root: str | Path, min_history: int = 2, mode: str = "default") -> "PipelinePaths":
        """Monta os caminhos padronizados a partir da raiz do projeto."""
        root = Path(project_root).resolve()
        output_dir = root / "TCCPipeline" / "Result" / mode
        return cls(
            mode=mode,
            project_root=root,
            school_report_dir=root / "TCCPipeline" / "Result" / "relatorios_escolares",
            grades_csv=root / "BDBasic" / "Result" / "CSV" / "media_nota_aluno.csv",
            absences_csv=root / "BDBasic" / "Result" / "CSV" / "faltas_aluno.csv",
            payments_csv=root / "BDBasic" / "Result" / "CSV" / "pagamento_aluno.csv",
            teachers_csv=root / "BDBasic" / "Result" / "CSV" / "professor_disciplina.csv",
            output_dir=output_dir,
            dataset_csv=output_dir / "student_prediction_dataset.csv",
            predictions_csv=output_dir / "student_prediction_predictions.csv",
            metrics_txt=output_dir / "student_prediction_report.txt",
            model_pkl=output_dir / "student_prediction_model.pkl",
            error_by_subject_csv=output_dir / "error_analysis_by_subject.csv",
            error_by_series_csv=output_dir / "error_analysis_by_series.csv",
            error_by_band_csv=output_dir / "error_analysis_by_score_band.csv",
            error_summary_txt=output_dir / "error_analysis_summary.txt",
            min_history=min_history,
        )
