import pandas as pd
import networkx as nx
from sklearn.metrics import pairwise_distances
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from spektral.data import Graph
from spektral.data import Dataset
from spektral.layers import GraphConv
from spektral.layers.pooling import GlobalSumPool
from spektral.utils import sparse

def create_rag(df, similarity_threshold=0.5):
    """
    Creates a Relational Anomaly Graph (RAG) from the data in a DataFrame.

    Args:
        df (pd.DataFrame): DataFrame containing the student grades data.
        similarity_threshold (float): Threshold for determining edge weights in the RAG.

    Returns:
        networkx.Graph: The constructed Relational Anomaly Graph (RAG).
    """
    G = nx.Graph()
    
    for index, row in df.iterrows():
        node_id = str(row['Aluno']) + '_' + str(row['Disciplina'])
        G.add_node(node_id, attributes=row.to_dict())
    
    scaler = MinMaxScaler()
    scaled_grades = scaler.fit_transform(df[['Média']])
    pairwise_distances_matrix = pairwise_distances(scaled_grades, metric='euclidean')
    
    for i in range(len(df)):
        node_id_i = str(df.loc[i, 'Aluno']) + '_' + str(df.loc[i, 'Disciplina'])
        for j in range(i + 1, len(df)):
            node_id_j = str(df.loc[j, 'Aluno']) + '_' + str(df.loc[j, 'Disciplina'])
            similarity = 1 - pairwise_distances_matrix[i, j]
            if similarity >= similarity_threshold:
                G.add_edge(node_id_i, node_id_j, weight=similarity)
    
    return G

def get_student_labels(df):
    """
    Extracts the labels for the students from the DataFrame.

    Args:
        df (pd.DataFrame): DataFrame containing the student grades data.

    Returns:
        np.array: Array of labels indicating if the student is at risk of dropout.
    """
    return df['Risco'].values  # Assuming 'Risco' column exists

def create_graph_data(G):
    """
    Converts the networkx graph to Spektral's Graph object.

    Args:
        G (networkx.Graph): The relational anomaly graph.

    Returns:
        spektral.data.Graph: Spektral graph object.
    """
    nodes = list(G.nodes)
    adj = nx.adjacency_matrix(G, nodelist=nodes)
    features = [list(G.nodes[node]['attributes'].values()) for node in nodes]
    
    return Graph(x=tf.convert_to_tensor(features, dtype=tf.float32), 
                 a=sparse.adj_to_sparse_tensor(adj))

class MyDataset(Dataset):
    def __init__(self, graph):
        self.graph = graph
        super().__init__()

    def read(self):
        return [self.graph]

def training(df, RAG):
    """
    Trains a model on the provided Relational Anomaly Graph (RAG).

    Args:
        df (pd.DataFrame): DataFrame containing the student grades data.
        RAG (networkx.Graph): The pre-built Relational Anomaly Graph.
    """
    graph_data = create_graph_data(RAG)
    dataset = MyDataset(graph_data)
    
    model = tf.keras.Sequential([
        GraphConv(16, activation='relu', input_shape=(dataset.n_node_features, )),
        GraphConv(32, activation='relu'),
        GlobalSumPool(),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    labels = get_student_labels(df)
    
    model.fit(dataset, y=labels, epochs=10, batch_size=1)

def rag(foldercsv, namecsv):
    """
    Loads data, creates RAG, and trains a model on the RAG.

    Args:
        foldercsv (str): Path to the folder containing the CSV file.
        namecsv (str): Name of the CSV file containing student grades data.
    """
    df = pd.read_csv(f"{foldercsv}/{namecsv}", encoding='utf-8', decimal=',')
    
    RAG = create_rag(df, similarity_threshold=0.5)
    
    training(df, RAG)

# Example usage
rag("data", "notas_alunos.csv")
