import os
import pickle

import pandas


def savearchivestudent(filename, data):
    """Salva dados nos formatos usados pela pipeline tabular atual."""
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        file_path = os.path.join(filename)
        ext = filename.split('.')[-1].lower()

        if os.path.exists(file_path):
            filedelete(filename)

        if ext == 'csv':
            if isinstance(data, pandas.DataFrame):
                data.to_csv(file_path, index=False, encoding='utf-8')
            else:
                raise TypeError(f"Esperado DataFrame para CSV, recebido {type(data)}.")

        elif ext == 'json':
            if isinstance(data, pandas.DataFrame):
                data.to_json(file_path, orient='records', lines=True)
            else:
                raise TypeError(f"Esperado DataFrame para JSON, recebido {type(data)}.")

        elif ext in ['xls', 'xlsx']:
            if isinstance(data, pandas.DataFrame):
                data.to_excel(file_path, index=False)
            else:
                raise TypeError(f"Esperado DataFrame para Excel, recebido {type(data)}.")

        elif ext in ['pkl', 'pk']:
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)

        else:
            raise ValueError(f"Formato de arquivo não suportado: '{ext}'")

    except Exception as e:
        print(f"Erro ao salvar o arquivo '{filename}': {e}")
        raise

def filereader(filename):
    """Lê arquivos usados pela pipeline tabular atual."""
    file_path = os.path.join(filename)
    
    try:
        ext = filename.split('.')[-1].lower()

        if ext == 'csv':
            df = pandas.read_csv(file_path, encoding='utf-8', decimal=',', low_memory=False)
            return df

        elif ext == 'json':
            return pandas.read_json(file_path)

        elif ext in ['xls', 'xlsx']:
            return pandas.read_excel(file_path)

        elif ext == 'pkl':
            with open(file_path, 'rb') as f:
                return pickle.load(f)

        else:
            raise ValueError(f"Formato de arquivo não suportado: {ext}")

    except Exception as e:
        print(f"Erro ao ler '{filename}': {e}")
        return None

def filedelete(filenames):
    """Remove um ou mais arquivos locais se eles existirem."""
    try:
        if isinstance(filenames, str):
            filenames = [filenames]

        for filepath in filenames:
            if os.path.exists(filepath):
                os.remove(filepath)
                # print(f"Arquivo '{filepath}' excluído com sucesso.")
            # else:
                # print(f"Arquivo '{filepath}' não encontrado.")
    except Exception as e:
        print(f"Erro ao deletar arquivo: {e}")
        raise
