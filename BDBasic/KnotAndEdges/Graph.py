import numpy
import pandas
import torch
from sklearn.preprocessing import OneHotEncoder
from Class import GraphManager
from BDBasic.DataExtraction.File import filereader, savearchivestudent

# Processa os dados e adiciona nós e arestas ao grafo
def add_entities_and_relations(G, data, node_type, relation, id_column, enrollment_column=None, node_mapping=None, node_count=0, data_types=None):
    for _, row in data.iterrows():
        if node_type == 'Student':
            node_id = f"{node_type}_{row[id_column]}"
            enrollment_id = f"Enrollment_{row['IDMatricula']}"

            G.add_node(node_id, type='Student', **row.to_dict())
            enrollment_attributes = {key: row[key] for key in data.columns if key != 'IDAluno'}
            G.add_node(enrollment_id, type='Enrollment', **enrollment_attributes)
            G.add_edge(node_id, enrollment_id, relation='has_enrollment')

            if node_id not in node_mapping:
                node_mapping[node_id] = node_count
                node_count += 1
            if enrollment_id not in node_mapping:
                node_mapping[enrollment_id] = node_count
                node_count += 1
        else:
            node_id = f"{node_type}_{row[id_column]}"
            enrollment_id = f"Enrollment_{row[enrollment_column]}"

            G.add_node(node_id, type=node_type, **row.to_dict())
            G.add_edge(enrollment_id, node_id, relation=relation)

            if node_id not in node_mapping:
                node_mapping[node_id] = node_count
                node_count += 1

    return node_mapping, node_count

# Processa os atributos dos nós do grafo
def process_node_attributes(G, max_unique_threshold=100):
    data = []
    for node in G.nodes:
        data.append(G.nodes[node])
    
    df = pandas.DataFrame(data)
    
    numerical_cols = df.select_dtypes(include=[numpy.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=[object, "category"]).columns.tolist()
    
    df[numerical_cols] = df[numerical_cols].fillna(0.0)
    df[categorical_cols] = df[categorical_cols].fillna('')
    
    safe_categorical_cols = [col for col in categorical_cols if df[col].nunique() <= max_unique_threshold]
    
    if safe_categorical_cols:
        encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        categorical_encoded = encoder.fit_transform(df[safe_categorical_cols])
    else:
        categorical_encoded = numpy.array([], dtype=numpy.float32).reshape(len(df), 0)
    
    numerical_data = df[numerical_cols].to_numpy(dtype=numpy.float32)
    final_features = numpy.hstack([numerical_data, categorical_encoded])
    
    return torch.tensor(final_features, dtype=torch.float32)

# Processa as arestas do grafo
def process_edges(G, node_mapping, data_types):
    edge_index = []
    edge_attr = []

    for u, v, data in G.edges(data=True):
        u_idx = node_mapping[u]
        v_idx = node_mapping[v]
        edge_index.append([u_idx, v_idx])
        relation = data.get('relation', None)
        relation_idx = next((index for index, (_, _, rel, _, _) in enumerate(data_types) if rel == relation), -1)
        edge_attr.append([relation_idx])

    edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()
    edge_attr = torch.tensor(edge_attr, dtype=torch.long)
    return edge_index, edge_attr

# Função principal para processar o grafo
def graphnode(manager: GraphManager):
    for file_key, entity_type, relation, id1, id2 in manager.data_types:
        data = filereader(manager.filename[file_key])
        manager.node_mapping, manager.node_count = add_entities_and_relations(
            manager.graph, data, entity_type, relation, id1, id2, 
            manager.node_mapping, manager.node_count, manager.data_types
        )

    node_features = process_node_attributes(manager.graph)
    all_node_data = {node_id: attributes for node_id, attributes in manager.graph.nodes(data=True)}
    edge_index, edge_attr = process_edges(manager.graph, manager.node_mapping, manager.data_types)

    savearchivestudent(manager.filename[6], manager.graph)
    savearchivestudent(manager.filename[7], {
        'x': node_features,
        'edge_index': edge_index,
        'edge_attr': edge_attr,
        'node_data': all_node_data
    })