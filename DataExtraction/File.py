import os
import pickle
import pandas as pd
import torch
import networkx as nx
from torch_geometric.data import Data

def savearchivestudent(foldercsv, filename, data):
    try:
        # Criando a pasta "Result" se não existir
        if not os.path.exists(foldercsv):
            os.makedirs(foldercsv)

        file_path = os.path.join(foldercsv, filename)
        ext = filename.split('.')[-1].lower()  # Obtém a extensão do arquivo
        
        if ext == 'csv':
            if isinstance(data, pd.DataFrame):
                data.to_csv(file_path, index=False, encoding='utf-8')
            else:
                raise ValueError("Os dados devem ser um DataFrame para salvar como CSV.")

        elif ext == 'json':
            if isinstance(data, pd.DataFrame):
                data.to_json(file_path, orient='records', lines=True)
            else:
                raise ValueError("Os dados devem ser um DataFrame para salvar como JSON.")

        elif ext in ['xls', 'xlsx']:
            if isinstance(data, pd.DataFrame):
                data.to_excel(file_path, index=False)
            else:
                raise ValueError("Os dados devem ser um DataFrame para salvar como Excel.")

        elif ext == 'pkl':
            if isinstance(data, Data):
                with open(file_path, 'wb') as f:
                    pickle.dump(data, f)
            else:
                raise ValueError("Os dados devem ser um objeto Data do PyTorch Geometric para salvar como .pkl")

        elif ext == 'graphml':
            if isinstance(data, nx.Graph):
                nx.write_graphml(data, file_path)
            else:
                raise ValueError("Os dados devem ser um grafo NetworkX para salvar como GraphML.")

        elif ext == 'pt':
            if isinstance(data, dict):
                torch.save(data, file_path)
            else:
                raise ValueError("Os dados devem ser um dicionário com tensores para salvar como .pt")

        else:
            raise ValueError(f"Formato de arquivo não suportado: {ext}")
        
        #print(f"Arquivo salvo com sucesso em: {file_path}")

    except Exception as e:
        print(f"Erro ao salvar o arquivo: {e}")
        raise

def filereader(foldercsv, filename):
    file_path = os.path.join(foldercsv, filename)
    
    try:
        ext = filename.split('.')[-1].lower()

        if ext == 'csv':
            df = pd.read_csv(file_path, encoding='utf-8', decimal=',')
            df = df.astype(str).fillna("NULL")
            return df

        elif ext == 'json':
            return pd.read_json(file_path)

        elif ext in ['xls', 'xlsx']:
            return pd.read_excel(file_path)

        elif ext == 'pkl':
            with open(file_path, 'rb') as f:
                return pickle.load(f)

        elif ext == 'graphml':
            return nx.read_graphml(file_path)

        elif ext == 'pt':
            return torch.load(file_path)

        else:
            raise ValueError(f"Formato de arquivo não suportado: {ext}")

    except Exception as e:
        print(f"Erro ao ler '{filename}': {e}")
        return None

    except Exception as e:
        print(f"Error writing file: {e}")
        raise

def filedelete(foldercsv, filenames):
    try:
        if isinstance(filenames, str):  # Se for string, transforma em lista
            filenames = [filenames]

        for filename in filenames:
            filepath = os.path.join(foldercsv, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                # print(f"Arquivo '{filename}' excluído com sucesso.")
            # else:
                # print(f"Arquivo '{filename}' não encontrado.")
    except Exception as e:
        print(f"Erro deleting file: {e}")
        raise