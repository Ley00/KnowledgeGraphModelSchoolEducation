import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

def detect_and_impute_outliers(data, method='z-score', threshold=3):
    """
    Detecta e imputa valores atípicos em uma coluna de dados.

    Args:
        data (pd.Series): Série de dados contendo os valores a serem analisados.
        method (str): Método de detecção de outliers. Opções: 'z-score', 'iqr'.
        threshold (float): Limite para considerar um valor como outlier.

    Returns:
        pd.Series: Série de dados com outliers imputados.
    """

    if method == 'z-score':
        # Separar os valores de média
        data_split = data.str.split().apply(lambda x: pd.Series(x))

        # Converter os valores para float e empilhar as séries
        data_float = data_split.astype(float).stack()

        # Calcular os z-scores
        zscores = (data_float - data_float.mean()) / data_float.std()

        # Identificar os outliers
        outliers = zscores[abs(zscores) > threshold].index

        # Imputar outliers com a média dos valores
        data_float.loc[outliers] = data_float.mean()

        # Restaurar o formato original e reindexar
        data_imputed = data_float.unstack().reindex(data.index)
    elif method == 'iqr':
        q1 = data.quantile(0.25)
        q3 = data.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = data[(data < lower_bound) | (data > upper_bound)].index
        data_imputed = data.copy()
        data_imputed.loc[outliers] = data.mean()
    else:
        raise ValueError(f"Método de detecção de outliers inválido: {method}")

    return data_imputed

def normalize_data(data, method='min-max'):
    """
    Normaliza os dados em uma coluna utilizando o método especificado.

    Args:
        data (pd.Series): Série de dados contendo os valores a serem normalizados.
        method (str): Método de normalização. Opções: 'min-max', 'standard'.

    Returns:
        pd.Series: Série de dados normalizados.
    """

    if method == 'min-max':
        normalized_data = (data - data.min()) / (data.max() - data.min())
    elif method == 'standard':
        normalized_data = (data - data.mean()) / data.std()
    else:
        raise ValueError(f"Método de normalização inválido: {method}")

    return normalized_data

def apply_pca(df):
    """
    Aplica a análise de PCA nos dados do DataFrame.

    Args:
        df (pd.DataFrame): DataFrame contendo os dados a serem analisados.

    Returns:
        pd.DataFrame: DataFrame contendo os componentes principais após a PCA.
    """
    # Selecionando apenas as colunas numéricas para análise de PCA
    df.select_dtypes(include=['float64']).columns

    # Selecionando apenas as colunas categóricas para codificação one-hot
    categorical_features = df.select_dtypes(include=['object']).columns

    # Aplicando a codificação one-hot nas colunas categóricas
    ct = ColumnTransformer(
        [('onehot', OneHotEncoder(), categorical_features)],
        remainder='passthrough'
    )
    df_encoded = ct.fit_transform(df)

    # Normalizando os dados
    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df_encoded)

    # Aplicando a PCA nos dados normalizados
    pca = PCA()
    principal_components = pca.fit_transform(df_scaled)

    # Convertendo os componentes principais em um DataFrame
    df_pca = pd.DataFrame(data=principal_components, index=df.index)

    return df_pca

def identify_multivariate_outliers(data, method='PCA', threshold=3):
    """
    Identifica outliers multivariados em um conjunto de dados utilizando o método PCA.

    Args:
        data (pd.DataFrame): DataFrame contendo os dados a serem analisados.
        method (str): Método de detecção de outliers. Opções: 'PCA'.
        threshold (float): Limite para considerar um ponto como outlier.

    Returns:
        List: Lista de índices dos outliers identificados.
    """

    if method == 'PCA':
        pca = PCA(n_components=data.shape[1])  # Corrigindo o número de componentes
        principal_components = pca.fit_transform(data)
        reconstruction_errors = pca.inverse_transform(principal_components) - data
        reconstruction_errors = np.linalg.norm(reconstruction_errors, axis=1)
        outliers = data.index[reconstruction_errors > threshold * reconstruction_errors.mean()].tolist()
    else:
        raise ValueError(f"Método de detecção de outliers inválido: {method}")

    return outliers

def enrich_data(data, student_id='Aluno'):
    """
    Enriquece os dados criando novas colunas com informações adicionais.

    Args:
        data (pd.DataFrame): DataFrame contendo os dados a serem enriquecidos.
        student_id (str): Nome da coluna que contém o ID do aluno.

    Returns:
        pd.DataFrame: DataFrame com dados enriquecidos.
    """

    # Criar coluna com ano de nascimento com base na idade
    #data['Ano_Nascimento'] = data['Idade'].apply(lambda x: int(2024 - x))

    # Criar coluna com média anual com

def plot_distribution(data):
     """
     Gera um gráfico de distribuição para uma coluna de dados.

     Args:
         data (pd.Series): Série de dados contendo os valores a serem plotados.
     """

     plt.figure(figsize=(10, 6))
     plt.hist(data, bins=20, edgecolor='black')
     plt.xlabel('Valores')
     plt.ylabel('Frequência')
     plt.title("Distribuição da coluna Média")
     plt.grid(True)
     plt.show()

def plot_correlation_matrix(data):
     """
     Gera uma matriz de correlação usando o seaborn.

     Args:
         data (pd.DataFrame): DataFrame contendo os dados a serem analisados.
     """
     
     plt.figure(figsize=(10, 10))
     sns.heatmap(data.corr(), annot=True, cmap='coolwarm')
     plt.title('Matriz de Correlação')
     plt.show()

def averagetreatment(foldercsv, namecsv):
    """
    Pre-processes and parses the data from the CSV file.

    Perform the following steps:
        1. Reading the CSV file
        2. Filling in missing values
        3. Detection and Imputation of Abnormal Values
        4. Data Normalization
        5. Identification of Multivariate Outliers
        6. Data Enrichment
        7. Save Pre-Processed Data
        8. Data Visualization
    """
    media = 'Média'
    
    try:
        # Leitura do arquivo CSV
        df = pd.read_csv(f"{foldercsv}/{namecsv}", encoding='utf-8', decimal=',')

        # Preenchimento de valores ausentes
        df.fillna('N/A', inplace=True)

        # Detecção e Imputação de Valores Anormais
        df[media] = detect_and_impute_outliers(df[media], method='z-score')

        # Normalização de Dados
        df[media] = normalize_data(df[media], method='min-max')

        # Aplicação da análise de PCA
        # df_pca = apply_pca(df)

        # Identificação de Outliers Multivariados (se necessário)
        # outliers = identify_multivariate_outliers(df_pca, method='PCA')
        # df_pca = df_pca.drop(outliers)

        # Enriquecimento de Dados (se necessário)
        # df_enriched = enrich_data(df_pca, student_id='Aluno')

        # Salvar dados pré-processados
        df_pca.to_csv(foldercsv + "/" + namecsv, index=False)


        #print("Colunas e seus valores:")
        #print(df_pca)
        
        # Visualização de Dados (se necessário)
        #plot_distribution(df_pca)
        #plot_correlation_matrix(df_pca)

    except Exception as e:
        print(f"Erro durante o pré-processamento do arquivo CSV: {e}")
