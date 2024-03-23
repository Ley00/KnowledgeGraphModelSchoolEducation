from Preprocessing.DataAccess import criar_sessao
from Preprocessing.Average.AverageGrade import obter_medias_aluno
from Preprocessing.Average.AverageGrade import obter_medias_aluno_especifico
from Preprocessing.csv import savearchive

def main():

    sessao = criar_sessao()
    
    #Aluno Específico
    # nome_aluno = "Ana Cecília Tavares Aleixo"
    # disciplina = "Arte"
    # periodoletivo = "2023"
    
    # query = obter_medias_aluno_especifico(nome_aluno, disciplina, periodoletivo)
    # resultados = sessao.execute(query, {"disciplina": disciplina, "nome_aluno": nome_aluno, "periodoletivo": periodoletivo})

    #Todos Alunos
    query = obter_medias_aluno()
    resultados = sessao.execute(query)

    # Adicione cada resultado da consulta à lista
    resultados_lista = [resultado for resultado in resultados]

    sessao.close()

    savearchive(resultados_lista)

if __name__ == "__main__":
    main()
