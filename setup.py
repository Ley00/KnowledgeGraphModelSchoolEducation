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
    'seaborn', 
    'networkx', 
    'llama_index', 
    'pyvis', 
    'Ipython', 
    'langchain', 
    'pypdf', 
    'llama-index-llms-huggingface', 
    'llama-index-embeddings-langchain', 
    'langchain-community', 
    'pydantic'
]

def create_virtualenv():
    # Verifica se o ambiente virtual já existe
    if not os.path.exists('venv'):
        print("Criando ambiente virtual...")
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])
    else:
        print("Ambiente virtual já existe.")

def install_dependency(dependency):
    # Verifica se a dependência já está instalada, caso contrário, instala
    try:
        print(f"Verificando se {dependency} está instalado...")
        subprocess.check_call([pip_path, 'show', dependency])
        print(f"{dependency} já está instalado.")
    except subprocess.CalledProcessError:
        print(f"{dependency} não encontrado. Instalando...")
        subprocess.check_call([pip_path, 'install', dependency])
        sys.exit()

def update_dependency(dependency):
    # Atualiza a dependência, caso já esteja instalada
    try:
        print(f"Atualizando {dependency} para a versão mais recente...")
        subprocess.check_call([pip_path, 'install', '--upgrade', dependency])
    except subprocess.CalledProcessError as e:
        print(f"Erro ao atualizar {dependency}: {e}")
        sys.exit()

def install_homebrew_dependencies():
    """Instala o Homebrew e os pacotes MSODBCSQL18 e MSSQL-TOOLS18 no Mac, caso não estejam instalados."""
    # Verifica se o Homebrew está instalado
    if platform.system() == 'Darwin':
        if subprocess.call(['which', 'brew']) != 0:
            print("Homebrew não encontrado. Instalando...")
            subprocess.check_call(['/bin/bash', '-c', "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"])
            subprocess.check_call(['echo', 'eval "$(/opt/homebrew/bin/brew shellenv)"', '>>', '~/.zprofile'])
            subprocess.check_call(['source', '~/.zprofile'])

        # Verifica se os pacotes MSODBCSQL18 e MSSQL-TOOLS18 estão instalados
        try:
            subprocess.check_call(['brew', 'tap', 'microsoft/mssql-release', 'https://github.com/Microsoft/homebrew-mssql-release'])
            subprocess.check_call(['brew', 'update'])
            print("Instalando msodbcsql18 e mssql-tools18...")
            # Usando env para definir a variável HOMEBREW_ACCEPT_EULA
            env = os.environ.copy()
            env['HOMEBREW_ACCEPT_EULA'] = 'Y'  # Definindo a variável de ambiente corretamente
            subprocess.check_call(['brew', 'install', 'msodbcsql18', 'mssql-tools18'], env=env)
        except subprocess.CalledProcessError:
            print("Erro ao instalar os pacotes MSODBCSQL18 ou MSSQL-TOOLS18.")
            sys.exit()

def install_dependencies():
    # Ativa o ambiente virtual e instala as dependências
    if platform.system() == 'Darwin':  # Para MacOS
        global pip_path
        pip_path = './venv/bin/pip'
        install_homebrew_dependencies()  # Instalar Homebrew e pacotes no Mac
    elif platform.system() == 'Windows':  # Para Windows
        pip_path = './venv/Scripts/pip.exe'
    else:
        raise OSError("Sistema operacional não suportado.")
    
    print("Instalando dependências...")
    for dependency in dependencies:
        install_dependency(dependency)

def update_dependencies():
    # Atualiza as dependências
    print("Atualizando dependências...")
    for dependency in dependencies:
        update_dependency(dependency)

def verify_dependencies():
    create_virtualenv()
    install_dependencies()
    update_dependencies()
    install_homebrew_dependencies()
