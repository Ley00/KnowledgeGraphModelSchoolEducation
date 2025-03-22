import torch
import torch.nn as nn
import torch.optim as optim
from torch_geometric.nn import GCNConv
from torch_geometric.data import DataLoader

# Definindo o modelo GCN
class GCNModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(GCNModel, self).__init__()
        # Primeira camada GCN
        self.conv1 = GCNConv(input_dim, hidden_dim)
        # Segunda camada GCN
        self.conv2 = GCNConv(hidden_dim, output_dim)
        # Camada de ativação
        self.relu = nn.ReLU()
        # Camada de pooling
        self.pool = nn.AdaptiveAvgPool1d(1)  # Usando um pooling simples
        # Camada de saída (se necessário)
        self.fc = nn.Linear(output_dim, 1)  # Por exemplo, predição de uma classe

    def forward(self, data):
        x, edge_index = data.x, data.edge_index
        # Passando pela primeira camada GCN e ativação ReLU
        x = self.conv1(x, edge_index)
        x = self.relu(x)
        # Passando pela segunda camada GCN
        x = self.conv2(x, edge_index)
        # Pooling dos resultados
        x = self.pool(x.unsqueeze(2)).squeeze(2)
        # Passando pela camada de saída
        x = self.fc(x)
        return x

# Função de treinamento
def train(model, data, optimizer, criterion):
    model.train()
    optimizer.zero_grad()  # Limpa os gradientes das iterações anteriores
    out = model(data)  # Realiza a inferência com o modelo
    loss = criterion(out, data.y)  # Calcula a função de perda
    loss.backward()  # Retropropaga o erro
    optimizer.step()  # Atualiza os pesos do modelo
    return loss.item()

# Função de avaliação
def evaluate(model, data, criterion):
    model.eval()  # Define o modelo em modo de avaliação
    out = model(data)  # Realiza a inferência
    loss = criterion(out, data.y)  # Calcula a função de perda
    return loss.item()

# Processamento dos atributos dos nós (notas e valores)
def process_node_attributes(G, node_mapping):
    node_features = torch.zeros(len(node_mapping), dtype=torch.float)  # Vetor de características

    for node, index in node_mapping.items():
        node_data = G.nodes[node]

        # Criando um vetor de características simples
        if node_data["type"] == "Grade":
            node_features[index] = float(node_data["score"])
        elif node_data["type"] == "Payment":
            node_features[index] = float(node_data["amount"])
        elif node_data["type"] == "Absence":
            node_features[index] = -1  # Podemos representar faltas de forma negativa
        else:
            node_features[index] = 0  # Outros tipos de nós podem ter valor 0 por padrão

    return node_features

# Processamento dos atributos dos nós (notas e valores)
def process_node_attributes(G, node_mapping):
    node_features = []

    for node in G.nodes:
        node_data = G.nodes[node]
        node_index = node_mapping.get(node, None)

        if node_index is not None:
            features = []

            # Adiciona um valor numérico para o tipo do nó
            node_type = node_data.get('type', 'Unknown')
            type_encoding = {'Student': 0, 'Enrollment': 1, 'Grade': 2, 'Payment': 3, 'Absence': 4, 'Responsible': 5}
            features.append(type_encoding.get(node_type, -1))

            # Adiciona informações numéricas, se existirem
            features.append(float(node_data.get('score', 0)))  # Notas
            features.append(float(node_data.get('amount', 0)))  # Pagamentos

            # Adiciona os atributos processados na lista de features
            node_features.append((node_index, features))

    return node_features

def gcn(G, data):
    # Inicializando o modelo GCN
    input_dim = len(process_node_attributes(G, data))  # Número de atributos por nó
    hidden_dim = 64  # Número de unidades na camada oculta
    output_dim = 32  # Número de unidades na camada de saída

    model = GCNModel(input_dim, hidden_dim, output_dim)

    # Definindo o otimizador e a função de perda
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    criterion = nn.MSELoss()  # Usando MSE para regressão (pode mudar para outra conforme necessário)

    # Dados do grafo (obtido da função graphnode)
    #G, data = graphnode('caminho/para/csv', ['aluno.csv', 'media_nota_aluno.csv', 'pagamento_aluno.csv', 'faltas_aluno.csv', 'responsaveis_aluno.csv'])

    # Definindo a variável y (exemplo de usar as médias para treinamento)
    # Criando a variável target y considerando múltiplos atributos dos nós
    data.y = torch.tensor(
        [
            [
                float(node_data.get('ValorMedia', 0)),  # Média das notas
                float(node_data.get('amount', 0)),  # Valores pagos
                float(node_data.get('score', 0)),  # Notas individuais
                1 if node_data.get('type') == 'Absence' else 0  # Indicador de falta
            ]
            for node_data in data.x
        ],
        dtype=torch.float
    )

    # Loop de treinamento
    for epoch in range(200):  # Número de épocas
        loss = train(model, data, optimizer, criterion)
        if epoch % 10 == 0:
            print(f"Epoch {epoch}, Loss: {loss}")

    # Avaliação no final do treinamento
    loss = evaluate(model, data, criterion)
    print(f"Final evaluation loss: {loss}")
