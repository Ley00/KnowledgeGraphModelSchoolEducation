import math
import numpy
import torch
from collections import defaultdict
from typing import Dict, List, Tuple
from sklearn.preprocessing import MinMaxScaler
from Class import GraphManager

# Processa os atributos dos alunos e gera um grafo com arestas baseadas em grupos de atributos
def process_attributes(student_data):
    MAX_EDGES_PER_GROUP = 100
    grouped = defaultdict(list)

    for grade in student_data["Grade"]:
        try:
            nota = float(grade.get('ValorMedia', ''))
            if math.isnan(nota):
                continue
        except (ValueError, TypeError):
            continue

        key = tuple(grade[campo] for campo in GraphManager.features)
        grouped[key].append(nota)

    temp_X, temp_y = {}, {}
    for key, notas in grouped.items():
        if len(notas) == 0:
            continue
        temp_X[key] = [numpy.mean(notas)] 
        temp_y[key] = [numpy.mean(notas)]

    valid_keys = list(temp_X.keys())
    node_index_map = {key: idx for idx, key in enumerate(valid_keys)}

    X = [temp_X[key] for key in valid_keys]
    y = [temp_y[key] for key in valid_keys]
    num_nodes = len(X)

    grupos_por_campo = {campo: defaultdict(list) for campo in GraphManager.features}
    for key, idx in node_index_map.items():
        for i, campo in enumerate(GraphManager.features):
            grupos_por_campo[campo][key[i]].append(idx)

    edge_list = []

    for grupo in grupos_por_campo.values():
        add_edges(edge_list, grupo, MAX_EDGES_PER_GROUP)

    edge_list.extend((idx, idx) for idx in range(num_nodes))

    edge_index = torch.tensor(edge_list, dtype=torch.long).t().contiguous() if edge_list else torch.empty((2, 0), dtype=torch.long)
    X_tensor = torch.tensor(X, dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.float32)
    train_mask = torch.ones(num_nodes, dtype=torch.bool)

    return X_tensor, y_tensor, edge_index, train_mask, node_index_map

# Adiciona arestas entre os índices de um grupo, limitando o número máximo de arestas
def add_edges(edge_list: List[Tuple[int, int]], grupos: Dict[str, List[int]], max_edges: int):
    for indices in grupos.values():
        indices = indices[:max_edges]
        for i in range(len(indices)):
            for j in range(i + 1, len(indices)):
                edge_list.append((indices[i], indices[j]))
                edge_list.append((indices[j], indices[i]))

# Normaliza os dados de entrada e saída usando MinMaxScaler
def normalize_data(X, y):
    if X.ndim == 3:
        batch, seq_len, input_size = X.shape
        X_reshaped = X.reshape(batch * seq_len, input_size)
    else:
        X_reshaped = X 

    X_reshaped = X_reshaped.detach().numpy()

    x_scaler = MinMaxScaler()
    X_scaled = x_scaler.fit_transform(X_reshaped)

    if X.ndim == 3:
        X_normalized = X_scaled.reshape(batch, seq_len, input_size)
    else:
        X_normalized = X_scaled

    y = y.detach().numpy()
    y_scaler = MinMaxScaler()
    y_normalized = y_scaler.fit_transform(y)

    return X_normalized, y_normalized, x_scaler, y_scaler

# Constrói o grafo PyTorch Geometric a partir dos dados normalizados
def generate_embeddings(keys, embedding_dim=8):
    categories = defaultdict(set)
    for key in keys:
        for i, field in enumerate(CATEGORICAL_CAMPS):
            categories[field].add(key[i])

    embedding_model = CategoricalEmbedding(categories, embedding_dim)

    all_embeddings = []
    for key in keys:
        sample = {field: key[i] for i, field in enumerate(CATEGORICAL_CAMPS)}
        emb = embedding_model(sample)
        all_embeddings.append(emb)

    return torch.stack(all_embeddings), embedding_model

# Classe para gerar embeddings categóricos
class CategoricalEmbedding(torch.nn.Module):
    def __init__(self, categories, embedding_dim=8):
        super().__init__()
        self.embeddings = torch.nn.ModuleDict({})
        self.index_maps = {}

        for field, values in categories.items():
            unique_values = sorted(set(values))
            self.index_maps[field] = {val: idx for idx, val in enumerate(unique_values)}
            self.embeddings[field] = torch.nn.Embedding(len(unique_values), embedding_dim)

    def forward(self, sample):
        embedded = []
        for field, idx_map in self.index_maps.items():
            value = sample[field]
            index = idx_map.get(value, 0)  # usa 0 se não encontrar
            emb = self.embeddings[field](torch.tensor(index))
            embedded.append(emb)
        return torch.cat(embedded)