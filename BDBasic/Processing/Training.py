import torch
from torch_geometric.data import Data
from BDBasic.Processing.TemplateDefinition import activation_layer, first_layer, second_layer
from sklearn.metrics import mean_absolute_error, r2_score

# Modelo GCN com duas camadas e ReLU
class GCNModel(torch.nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(GCNModel, self).__init__()
        self.conv1 = first_layer(input_size, hidden_size)
        self.conv2 = second_layer(hidden_size, output_size)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = activation_layer(x)
        x = self.conv2(x, edge_index)
        return x

# Constrói um grafo com as informações necessárias
def build_graph(x, edge_index, y, train_mask=None, val_mask=None):
    return Data(
        x=torch.tensor(x, dtype=torch.float) if not isinstance(x, torch.Tensor) else x,
        edge_index=edge_index if isinstance(edge_index, torch.Tensor) else torch.tensor(edge_index, dtype=torch.long),
        y=torch.tensor(y, dtype=torch.float) if not isinstance(y, torch.Tensor) else y,
        train_mask=torch.tensor(train_mask, dtype=torch.bool) if train_mask is not None and not isinstance(train_mask, torch.Tensor) else train_mask,
        val_mask=torch.tensor(val_mask, dtype=torch.bool) if val_mask is not None and not isinstance(val_mask, torch.Tensor) else val_mask,
    )

# Cria e retorna o otimizador (Adam) e a função de perda (MSE)
def create_optimizer_and_loss(model, learning_rate=0.001):
    criterion = torch.nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    return optimizer, criterion

# Treina o modelo por época
def train_epoch(model, dataloader, optimizer, criterion):
    model.train()
    total_loss = 0
    for data in dataloader:
        optimizer.zero_grad()
        out = model(data.x, data.edge_index)
        loss = criterion(out[data.train_mask], data.y[data.train_mask])
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    return total_loss / len(dataloader)

# Avalia o modelo
@torch.no_grad()
def evaluate(model, dataloader):
    model.eval()
    all_preds = []
    all_targets = []
    for data in dataloader:
        out = model(data.x, data.edge_index)
        out = out.clamp(min=0, max=10)  # ajustável de acordo com a escala das notas
        preds = out[data.train_mask].cpu().numpy()
        targets = data.y[data.train_mask].cpu().numpy()
        all_preds.extend(preds)
        all_targets.extend(targets)

    rmse = torch.nn.functional.mse_loss(torch.tensor(all_preds), torch.tensor(all_targets)).sqrt().item()
    mae = mean_absolute_error(all_targets, all_preds)
    r2 = r2_score(all_targets, all_preds)

    return rmse, mae, r2

# Loop de treino/teste
def run_training(model, dataloader, optimizer, criterion, epochs):
    for epoch in range(1, epochs + 1):
        loss = train_epoch(model, dataloader, optimizer, criterion)
        rmse, mae, r2 = evaluate(model, dataloader)
        print(
            f"Epoch: {epoch:03d}, Loss: {loss:.4f} | "
            f"Train - RMSE: {rmse:.4f}, MAE: {mae:.4f}, R²: {r2:.4f}"
        )