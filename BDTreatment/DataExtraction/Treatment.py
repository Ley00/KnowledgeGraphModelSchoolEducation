import pandas
from BDBasic.DataExtraction.File import filereader
from Class import GraphManager

# Função para unir em uma única linha as médias de um aluno
def process_data_one(manager: GraphManager):
    try:
        studantName = 'NomeAluno'
        periodo_col = 'NomePeriodo'
        serie_col = 'NomeSerie'
        disciplina_col = 'NomeDisciplina'
        etapa_col = 'NomeEtapa'
        nota_col = 'ValorMedia'

        df = filereader(manager.filename[2])
        # df = df[df[studantName] == "Adauri Alves Pinto Filho"]
        df = df[df[serie_col].isin(["1ª Série", "2ª Série"])]
        
        # Verificar quais alunos têm dados em ambas as séries
        alunos_com_ambas_series = df.groupby(studantName)[serie_col].nunique()
        alunos_validos = alunos_com_ambas_series[alunos_com_ambas_series == 2].index
        # Filtrar apenas os alunos que têm ambas as séries
        df = df[df[studantName].isin(alunos_validos)]
        
        df = df[[col for col in df.columns if 'ID' not in col]]
        df = df[[col for col in df.columns if col not in ['NomeUnidade', 'NomeCurso', 'ApelidoTurma', 'SituacaoMatricula']]]

        fixed_columns = [col for col in df.columns if col not in [periodo_col, serie_col, disciplina_col, etapa_col, nota_col]]

        grouped = df.groupby(fixed_columns)

        result = []
        for group_values, group in grouped:
            row_data = {col: value for col, value in zip(fixed_columns, group_values)}
            for _, row in group.iterrows():
                col_name = f"{row[periodo_col]}_{row[serie_col]}_{row[disciplina_col]}_{row[etapa_col]}"
                row_data[col_name] = row[nota_col]
            result.append(row_data)

        df_result = pandas.DataFrame(result)

        df_result = df_result.fillna("NULL")

        columns_order = [studantName] + [col for col in df_result.columns if col != studantName]
        df_result = df_result[columns_order]

        df_result.to_csv(manager.filename[10], index=False, encoding='utf-8')

    except Exception as e:
        print(f"Error in average_single_line: {e}")
        raise

# Função para verificar a nota de um aluno do average_single_line
def check_student_grade_one(manager: GraphManager):
    try:
        aluno = "Pedro Lucas Ferreira Gomes"
        periodo = "2024"
        serie = '7º Ano'
        disciplina = "Educação Física"
        etapa = "2º BIMESTRE"

        df = filereader(manager.filename[10])

        aluno_row = df[df['NomeAluno'].astype(str).str.strip().str.lower() == aluno.strip().lower()]
        if aluno_row.empty:
            print(f"Aluno '{aluno}' não encontrado.")
            return None

        col_suffix = f"{periodo}_{serie}_{disciplina}_{etapa}"
        col_name = None
        for col in aluno_row.columns:
            if col.endswith(col_suffix):
                col_name = col
                break

        if not col_name:
            print(f"Coluna terminando com '{col_suffix}' não encontrada no arquivo.")
            return None

        nota = aluno_row.iloc[0][col_name]
        print(f"\nAluno: Nota de {aluno}\nSerie: {serie}\nDisciplina: {disciplina}\nEtapa: {etapa}\nNota: {nota}\n")
        return nota

    except Exception as e:
        print(f"Erro ao consultar nota: {e}")
        return None