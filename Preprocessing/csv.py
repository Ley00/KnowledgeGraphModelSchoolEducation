import pandas as pd
import csv

# Abrindo um arquivo CSV para escrita
def savearchive(resultados):
    try:
        with open('resultado_consulta.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow([
                "Aluno", "Matrícula", "Situação da Matrícula", "Período Letivo", "Curso",
                "Série", "Turma", "Disciplina", "Etapa", "Média"
            ])
            for resultado in resultados:
                writer.writerow([resultado[0], resultado[1], resultado[2], resultado[3],
                                 resultado[4], resultado[5], resultado[6], resultado[7],
                                 resultado[8], (resultado[9])])
    except Exception as e:
        print(f"Erro ao escrever no arquivo CSV: {e}")

    treatment()

def treatment():
    try:
        # Leitura do arquivo CSV
        df = pd.read_csv('resultado_consulta.csv', encoding='latin1')

        # Preenchimento de valores ausentes
        df.fillna('N/A', inplace=True)

        # Detecção e Imputação de Valores Anormais
        df['Média'] = detect_and_impute_outliers(df['Média'], method='z-score')

        # Normalização de Dados
        df['Média'] = normalize_data(df['Média'], method='min-max')

        # Identificação de Outliers Multivariados
        outliers = identify_multivariate_outliers(df, method='PCA')
        df = df.drop(outliers)

        # Enriquecimento de Dados
        df = enrich_data(df, student_id='Aluno')

        # Salvar dados pré-processados
        df.to_csv('resultado_pre_processado.csv', index=False)

        # Visualização de Dados
        plot_distribution(df['Média'])
        plot_correlation_matrix(df)

    except Exception as e:
        print(f"Erro durante o pré-processamento do arquivo CSV: {e}")
        