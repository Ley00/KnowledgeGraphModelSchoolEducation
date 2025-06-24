import torch.nn.functional as torch_functional
from torch_geometric.nn import GCNConv

# Primeira camada GCN (ou mais de uma, se desejar empilhar)
def first_layer(input_size, hidden_size):
    return GCNConv(input_size, hidden_size)

# Segunda camada GCN (transforma para o tamanho de saída desejado)
def second_layer(hidden_size, output_size):
    return GCNConv(hidden_size, output_size)

# Função de ativação
def activation_layer(x):
    return torch_functional.relu(x)