import seaborn
import matplotlib.pyplot as plt
from Class import GraphManager
from DataExtraction.File import filereader

# Análise de correlação entre as features e a média
def correlation_analysis(manager: GraphManager):
    df = filereader(manager.filename[2])
    df = df[[col for col in df.columns if 'ID' not in col]]

    # Calcular a matriz de correlação
    corr = df.corr(numeric_only=True)

    # Criar o mapa de calor
    plt.figure(figsize=(10, 8))
    seaborn.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm', square=True)
    plt.title('Matriz de Correlação')
    plt.tight_layout()
    plt.show()