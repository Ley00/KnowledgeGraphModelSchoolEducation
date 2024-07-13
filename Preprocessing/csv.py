import csv
import pandas as pd

serie = "Série"
media = "Média"

def savearchiveaverage(results, foldercsv, namecsv):
  """
  Função para salvar os resultados em um arquivo CSV na pasta "Result".

  Args:
      results: Dicionário contendo os resultados a serem salvos.
      namecsv: Nome do arquivo CSV (sem extensão).

  Returns:
      None
  """

  try:
      # Criando o DataFrame com os resultados
      df = pd.DataFrame(results, columns=[
          "Aluno", "Matrícula", "Situação da Matrícula", "Período Letivo", "Curso",
          "Série", "Turma", "Disciplina", "Etapa", "Média"
      ])

      # Removendo espaços em branco desnecessários do nome do bimestre
      df['Etapa'] = df['Etapa'].str.strip()

      # Salvando o DataFrame no arquivo CSV na pasta "Result"
      df.to_csv(f"{foldercsv}/{namecsv}", index=False, encoding='utf-8')

  except Exception as e:
      # Imprimindo mensagem de erro
      print(f"Erro ao escrever no arquivo CSV: {e}")

def savearchivepay(results, foldercsv, namecsv):
    """
    Salva os resultados da consulta em um arquivo CSV na pasta "Result".

    Args:
        results: Lista de tuplas contendo os dados da consulta.
        namecsv: Nome do arquivo CSV (sem a extensão).
    """

    try:
        # Criando o DataFrame
        df = pd.DataFrame(results, columns=[
            "Matrícula" ,"Aluno", "Situação da Matrícula", "Período Letivo", "Curso",
            serie, "Turma", "Parcela Movimento", "Descrição Movimento", "Data Antecipado Movimento",
            "Valor Antecipado Movimento", "Data Vencimento Movimento", "Valor Movimento",
            "Pago Movimento"
        ])

        # Calculando a média para cada linha
        df[media] = df[["Valor Antecipado Movimento", "Valor Movimento"]].mean(axis=1)

        # Arredondando a média para duas casas decimais
        df[media] = df[media].round(2)

        # Criando a pasta "Result" se não existir
        import os
        if not os.path.exists("Result"):
            os.makedirs("Result")

        # Salvando o DataFrame em um arquivo CSV na pasta "Result"
        df.to_csv(f"{foldercsv}/{namecsv}", index=False, encoding='utf-8')

    except Exception as e:
        print(f"Erro ao salvar os dados no arquivo CSV: {e}")
