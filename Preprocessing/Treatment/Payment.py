import pandas as pd

dvm = "Data Vencimento Movimento"
vam = "Data Antecipado Movimento"
vam = "Valor Antecipado Movimento"
vm = "Valor Movimento"
media = "Média"

def paymenttreatment(namecsv):
  """
  Função que trata os dados de mensalidades escolares de um arquivo CSV.

  Argumentos:
    namecsv (str): Nome do arquivo CSV contendo os dados de mensalidades.

  Retorna:
    DataFrame: DataFrame contendo os dados tratados.
  """

  # Leitura do arquivo CSV
  df = pd.read_csv(namecsv)

  # Conversão de colunas para tipos de dados adequados
  df[dvm] = pd.to_datetime(df[dvm])
  df[vam] = pd.to_datetime(df[vam], errors="coerce")
  df[vam] = pd.to_numeric(df[vam], errors="coerce")
  df[vm] = pd.to_numeric(df[vm], errors="coerce")

  # Cálculo da média das parcelas
  df[media] = df[[vam, vm]].mean(axis=1)

  # Agrupamento por aluno e cálculo de estatísticas descritivas
  df_grouped = df.groupby("Aluno").agg({
    media: "mean",
    vam: "sum",
    vm: "sum",
    "Pago Movimento": "sum",
  })

  # Cálculo do valor total pago por aluno
  df_grouped["Valor Pago"] = df_grouped["Pago Movimento"] * df_grouped["Média"]

  # Cálculo da diferença entre o valor pago e o valor total das mensalidades
  df_grouped["Diferença"] = df_grouped["Valor Movimento"] - df_grouped["Valor Pago"]

  # Impressão do DataFrame tratado
  print(df_grouped)
  
  df_grouped.to_csv(namecsv, index=False)
