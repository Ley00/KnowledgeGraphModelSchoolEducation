import pickle
from torch_geometric.loader import DataLoader
from Class import GraphManager
from DataExtraction.File import filereader, savearchivestudent
from KnotAndEdges.ReaderNetPy import extractpytorch
from Processing.Preprocessing import generate_embeddings, normalize_data, process_attributes
from Processing.Training import GCNModel, create_optimizer_and_loss, run_training, build_graph

def lstm(manager: GraphManager):
    # Carregar o grafo do arquivo
    graph = filereader(manager.filename[7])

    # Extrair dados dos nós do grafo
    student_data = extractpytorch(graph)

    # Processar atributos (X) e rótulos (y)
    X, y, edge_index, train_mask, node_index_map = process_attributes(student_data)

    # Gerar embeddings
    embeddings, embedding_model = generate_embeddings(node_index_map.keys())

    # Normalizar atributos e rótulos
    X_normalized, y_normalized, x_scaler, y_scaler = normalize_data(embeddings, y)

    # Construir objeto Data do PyG
    data = build_graph(X_normalized, edge_index, y_normalized, train_mask)

    # Hiperparâmetros
    input_size = data.num_node_features
    hidden_size = 64
    output_size = 1
    num_epochs = 200
    learning_rate = 0.001

    # Inicializar o modelo GCN
    model = GCNModel(input_size, hidden_size, output_size)

    # Criar otimizador e função de perda
    optimizer, criterion = create_optimizer_and_loss(model, learning_rate)

    # Criar DataLoader com batch_size=1 (1 grafo)
    dataloader = DataLoader([data], batch_size=1)

    # Treinar o modelo
    run_training(model, dataloader, optimizer, criterion, num_epochs)

    # Salvar o modelo treinado
    savearchivestudent(manager.filename[8], model.state_dict())

    # Salvar os objetos de normalização (scalers)
    scalers_data = pickle.dumps({"x_scaler": x_scaler, "y_scaler": y_scaler})
    savearchivestudent(manager.filename[9], scalers_data)