import os
import subprocess
import sys
import platform

# Lista de dependências
dependencies = [
    'pyodbc', 
    'sqlalchemy', 
    'pandas', 
    'scikit-learn', 
    'matplotlib',
    'torch', 
    'torchvision', 
    'torchaudio',
    'torch-geometric',
    'seaborn',
]

# Caminho do pip será definido globalmente
pip_path = None

# Cria o ambiente virtual
def create_virtualenv():
    if not os.path.exists('.venv'):
        print("Criando ambiente virtual (.venv)...")
        subprocess.check_call([sys.executable, "-m", "venv", ".venv"])
    else:
        print("Ambiente virtual (.venv) já existe.")

# Verifica se as dependências estão instaladas
def install_dependency(dependency):
    try:
        print(f"Verificando se {dependency} está instalado...")
        subprocess.check_call([pip_path, 'show', dependency])
        print(f"{dependency} já está instalado.")
    except subprocess.CalledProcessError:
        print(f"{dependency} não encontrado. Instalando...")
        subprocess.check_call([pip_path, 'install', dependency])

# Atualiza a dependência, caso já esteja instalada
def update_dependency(dependency):
    try:
        print(f"Atualizando {dependency} para a versão mais recente...")
        subprocess.check_call([pip_path, 'install', '--upgrade', dependency])
    except subprocess.CalledProcessError as e:
        print(f"Erro ao atualizar {dependency}: {e}")
        sys.exit()

# Instala o Homebrew e os pacotes MSODBCSQL18 e MSSQL-TOOLS18 no Mac
def install_homebrew_dependencies():
    if platform.system() == 'Darwin':
        if subprocess.call(['which', 'brew']) != 0:
            print("Homebrew não encontrado. Instalando...")
            subprocess.check_call(['/bin/bash', '-c', "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"])
            subprocess.call(['echo', 'eval "$(/opt/homebrew/bin/brew shellenv)" >> ~/.zprofile'], shell=True)
            subprocess.call(['source ~/.zprofile'], shell=True)

        try:
            subprocess.check_call(['brew', 'tap', 'microsoft/mssql-release', 'https://github.com/Microsoft/homebrew-mssql-release'])
            subprocess.check_call(['brew', 'update'])
            print("Instalando msodbcsql18 e mssql-tools18...")
            env = os.environ.copy()
            env['HOMEBREW_ACCEPT_EULA'] = 'Y'
            subprocess.check_call(['brew', 'install', 'msodbcsql18', 'mssql-tools18'], env=env)
        except subprocess.CalledProcessError:
            print("Erro ao instalar os pacotes MSODBCSQL18 ou MSSQL-TOOLS18.")
            sys.exit()

# Verifica o sistema operacional e instala as dependências
def install_dependencies():
    global pip_path
    if platform.system() == 'Darwin':
        pip_path = './.venv/bin/pip'
        install_homebrew_dependencies()
    elif platform.system() == 'Windows':
        pip_path = '.\\.venv\\Scripts\\pip.exe'
    else:
        raise OSError("Sistema operacional não suportado.")

    print("Instalando dependências...")
    for dependency in dependencies:
        install_dependency(dependency)

# Atualiza as dependências
def update_dependencies():
    print("Atualizando dependências...")
    for dependency in dependencies:
        update_dependency(dependency)

# Verifica se o ambiente virtual e as dependências estão instaladas
def verify_dependencies():
    create_virtualenv()
    install_dependencies()
    update_dependencies()
    if platform.system() == 'Darwin':
        install_homebrew_dependencies()