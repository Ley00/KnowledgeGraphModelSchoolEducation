import pandas
import seaborn
import matplotlib.pyplot as plt
from Class import GraphManager
from DataExtraction.File import filereader

# Análise de correlação entre as features e a média
def correlation_analysis(manager: GraphManager):
    df = filereader(manager.filename[2])



    # Garantir que average seja uma lista para concatenar com features
    #df = df[manager.features + [manager.average]].copy()

    # Transformar os campos categóricos em números
    # for col in manager.features:
    #     df[col] = pandas.factorize(df[col])[0]



    for col in [c for c in df.select_dtypes(include=['object', 'category']).columns if 'ID' not in c]:
        df[col] = pandas.factorize(df[col])[0]



    # Calcular a matriz de correlação
    corr = df.corr(numeric_only=True)

    # Criar o mapa de calor
    plt.figure(figsize=(10, 8))
    seaborn.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm', square=True)
    plt.title('Matriz de Correlação')
    plt.tight_layout()
    plt.show()