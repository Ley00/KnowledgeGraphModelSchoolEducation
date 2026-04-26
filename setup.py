from __future__ import annotations

import argparse
import subprocess
import sys
import venv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
VENV_DIR = PROJECT_ROOT / ".venv"
CORE_REQUIREMENTS = PROJECT_ROOT / "requirements.txt"


def create_virtualenv() -> None:
    """Create the local virtual environment when it does not exist yet."""
    if VENV_DIR.exists():
        print("Ambiente virtual .venv já existe.")
        return

    print("Criando ambiente virtual em .venv...")
    venv.create(VENV_DIR, with_pip=True)


def get_pip_path() -> Path:
    """Return the pip executable inside the local virtual environment."""
    if sys.platform.startswith("win"):
        return VENV_DIR / "Scripts" / "pip.exe"
    return VENV_DIR / "bin" / "pip"


def run_pip_command(*args: str) -> None:
    pip_path = get_pip_path()
    subprocess.check_call([str(pip_path), *args], cwd=PROJECT_ROOT)


def install_python_dependencies() -> None:
    """Install the Python dependencies required by the current application."""
    create_virtualenv()
    print("Atualizando pip...")
    run_pip_command("install", "--upgrade", "pip")

    print(f"Instalando dependências principais de {CORE_REQUIREMENTS.name}...")
    run_pip_command("install", "-r", str(CORE_REQUIREMENTS))


def print_manual_notes() -> None:
    """Explain external dependencies that stay outside Python packaging."""
    print("\nBootstrap Python concluído.")
    print("Dependências externas continuam manuais:")
    print("- SQL Server acessível localmente ou em rede")
    print("- ODBC Driver 18 for SQL Server instalado no sistema")
    print("- MacTeX/TeX Live para compilar a monografia em LaTeX")


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        prog="setup.py",
        description="Bootstrap simplificado do ambiente Python do projeto.",
    )


def main(argv: list[str] | None = None) -> int:
    build_parser().parse_args(argv)
    install_python_dependencies()
    print_manual_notes()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
