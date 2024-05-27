import pandas as pd
import networkx as nx
from sklearn.metrics import pairwise_distances
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf  # This import is not used in the provided code, but might be needed for future functionalities

def create_rag(df, similarity_threshold=0.5):
    """
    Creates a Relational Anomaly Graph (RAG) from the data in a DataFrame.

    Args:
        df (pd.DataFrame): DataFrame containing the student grades data.
        similarity_threshold (float): Threshold for determining edge weights in the RAG.

    Returns:
        networkx.Graph: The constructed Relational Anomaly Graph (RAG).
    """

    # Create a NetworkX graph
    G = nx.Graph()

    # Add nodes to the graph
    for index, row in df.iterrows():
        node_id = str(row['Aluno']) + '_' + str(row['Disciplina'])
        G.add_node(node_id, attributes=row.to_dict())

    # Calculate pairwise distances between nodes
    scaler = MinMaxScaler()
    scaled_grades = scaler.fit_transform(df[['Média']])
    pairwise_distances_matrix = pairwise_distances(scaled_grades, metric='euclidean')

    # Add edges to the graph based on similarity
    for i in range(len(df)):
        node_id_i = str(df.loc[i, 'Aluno']) + '_' + str(df.loc[i, 'Disciplina'])
        for j in range(i + 1, len(df)):
            node_id_j = str(df.loc[j, 'Aluno']) + '_' + str(df.loc[j, 'Disciplina'])
            similarity = 1 - pairwise_distances_matrix[i, j]
            if similarity >= similarity_threshold:
                G.add_edge(node_id_i, node_id_j, weight=similarity)

    return G

def training(df, RAG):
    """
    Trains a model on the provided Relational Anomaly Graph (RAG).

    Args:
        df (pd.DataFrame): DataFrame containing the student grades data (potentially not used here).
        RAG (networkx.Graph): The pre-built Relational Anomaly Graph.
    """

    # No need to recreate the graph or add nodes/edges here as RAG is already built

    # Use the provided RAG for training
    # You might need to modify this section based on your specific training needs
    # This example assumes using features from node attributes and labels derived elsewhere
    model = tf.keras.layers.GraphNetwork(
        layers=[
            tf.keras.layers.GraphConv1D(16, activation='relu'),
            tf.keras.layers.GraphConv1D(32, activation='relu'),
            tf.keras.layers.GraphConv1D(16, activation='relu'),
            tf.keras.layers.GraphPooling(pool_type='mean'),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ]
    )

    # Train the model using features and labels (implementation depends on your specific data)
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.fit(RAG, features=nx.get_node_attributes(RAG), labels=get_student_labels(df), epochs=10)  # Assuming labels are obtained from df

def rag(foldercsv, namecsv):
    """
    Loads data, creates RAG, and trains a model on the RAG.

    Args:
        foldercsv (str): Path to the folder containing the CSV file.
        namecsv (str): Name of the CSV file containing student grades data.
    """

    # Load student grades data from a CSV file
    df = pd.read_csv(f"{foldercsv}/{namecsv}", encoding='utf-8', decimal=',')

    # Create the Relational Anomaly Graph (RAG)
    RAG = create_rag(df, similarity_threshold=0.5)

    # Train the model on the created RAG
    training(df, RAG)

# Example usage (assuming get_student_labels function is defined elsewhere)
rag("data", "notas_alunos.csv")
