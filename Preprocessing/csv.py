import csv
from Preprocessing.Treatment.Average import averagetreatment
from Preprocessing.Treatment.Payment import paymenttreatment
import pandas as pd

serie = "Série"
media = "Média"

def savearchiveaverage(results, namecsv):
    try:
        df = pd.DataFrame(results, columns=[
            "Aluno", "Matrícula", "Situação da Matrícula", "Período Letivo", "Curso",
                serie, "Turma", "Disciplina", "Etapa", media
        ])
        
        df.to_csv(namecsv, index=False, encoding='utf-8')
        print(f"Arquivo {namecsv} salvo com sucesso!")
        
    except Exception as e:
        print(f"Erro ao escrever no arquivo CSV: {e}")
    
    averagetreatment(namecsv)

def savearchivepay(results, namecsv):
    """
    Salva os resultados da consulta em um arquivo CSV.

    Args:
        results: Lista de tuplas contendo os dados da consulta.
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

        # Ordenando o DataFrame por curso, série, turma e aluno
        df = df.sort_values(by=["Curso", "Série", "Turma", "Aluno"])

        # Salvando o DataFrame em um arquivo CSV
        df.to_csv(namecsv, index=False, encoding='utf-8')
        print(f"Arquivo {namecsv} salvo com sucesso!")

    except Exception as e:
        print(f"Erro ao salvar os dados no arquivo CSV: {e}")
        
    paymenttreatment(namecsv)
