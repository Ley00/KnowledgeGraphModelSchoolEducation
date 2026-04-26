from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    root: Path
    artifacts_dir: Path
    data_artifacts_dir: Path
    csv_dir: Path
    pipeline_artifacts_dir: Path
    reports_artifacts_dir: Path
    env_file: Path

    @classmethod
    def from_root(cls, project_root: str | Path = ".") -> "ProjectPaths":
        root = Path(project_root).resolve()
        artifacts_dir = root / "artifacts"
        data_artifacts_dir = artifacts_dir / "database"
        pipeline_artifacts_dir = artifacts_dir / "pipeline"
        reports_artifacts_dir = artifacts_dir / "reports"
        return cls(
            root=root,
            artifacts_dir=artifacts_dir,
            data_artifacts_dir=data_artifacts_dir,
            csv_dir=data_artifacts_dir / "csv",
            pipeline_artifacts_dir=pipeline_artifacts_dir,
            reports_artifacts_dir=reports_artifacts_dir,
            env_file=root / ".env",
        )


DEFAULT_PATHS = ProjectPaths.from_root(Path(__file__).resolve().parent.parent)


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
