import os
import pickle

import pandas


def _load_networkx():
    """Import networkx only when graph serialization is actually requested."""
    import networkx

    return networkx


def _load_torch():
    """Import torch lazily so the current tabular pipeline does not depend on it."""
    import torch

    return torch


def savearchivestudent(filename, data):
    """Salva dados em diferentes formatos preservando compatibilidade histórica."""
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

        elif ext == 'graphml':
            networkx = _load_networkx()
            if isinstance(data, networkx.Graph):
                networkx.write_graphml(data, file_path)
            else:
                raise TypeError(f"Esperado networkx.Graph para GraphML, recebido {type(data)}.")

        elif ext in ['pt', 'pth']:
            torch = _load_torch()
            torch.save(data, file_path)

        else:
            raise ValueError(f"Formato de arquivo não suportado: '{ext}'")

    except Exception as e:
        print(f"Erro ao salvar o arquivo '{filename}': {e}")
        raise

def filereader(filename):
    """Lê arquivos usados pelo projeto atual e pelos experimentos históricos."""
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

        elif ext == 'graphml':
            networkx = _load_networkx()
            return networkx.read_graphml(file_path)

        elif ext == 'pt':
            torch = _load_torch()
            return torch.load(file_path)

        else:
            raise ValueError(f"Formato de arquivo não suportado: {ext}")

    except Exception as e:
        print(f"Erro ao ler '{filename}': {e}")
        return None

    except Exception as e:
        print(f"Error writing file: {e}")
        raise

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
