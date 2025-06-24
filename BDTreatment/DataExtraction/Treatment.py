import pandas
from BDBasic.DataExtraction.File import filereader
from Class import GraphManager

# Função para unir em uma única linha as médias de um alun
def average_single_line(manager: GraphManager):
    try:
        studantName = 'NomeAluno'
        serie_col = 'NomeSerie'
        disciplina_col = 'NomeDisciplina'
        etapa_col = 'NomeEtapa'
        nota_col = 'ValorMedia'

        df = filereader(manager.filename[2])
        # df = df[df[studantName] == "Pedro Lucas Ferreira Gomes"]
        df = df[[col for col in df.columns if 'ID' not in col]]
        df = df[[col for col in df.columns if col not in ['NomeUnidade', 'NomePeriodo', 'NomeCurso', 'ApelidoTurma', 'SituacaoMatricula']]]

        # Identifica as colunas fixas e dinâmicas
        fixed_columns = [col for col in df.columns if col not in [serie_col, disciplina_col, etapa_col, nota_col]]

        # Agrupa os dados por aluno
        grouped = df.groupby(fixed_columns)

        # Cria um novo DataFrame com NomeSerie, NomeDisciplina e NomeEtapa concatenados como colunas
        result = []
        for group_values, group in grouped:
            row_data = {col: value for col, value in zip(fixed_columns, group_values)}
            for _, row in group.iterrows():
                col_name = f"{row[serie_col]}_{row[disciplina_col]}_{row[etapa_col]}"
                row_data[col_name] = row[nota_col]
            result.append(row_data)

        # Converte o resultado em um DataFrame
        df_result = pandas.DataFrame(result)

        # Preenche valores ausentes com 'NULL'
        df_result = df_result.fillna("NULL")

        # Reorganiza as colunas para trazer NomeAluno como a primeira coluna
        columns_order = [studantName] + [col for col in df_result.columns if col != studantName]
        df_result = df_result[columns_order]

        # Salva resultado em CSV
        df_result.to_csv(manager.filename[10], index=False, encoding='utf-8')

    except Exception as e:
        print(f"Error in average_single_line: {e}")
        raise

# Função para verificar a nota de um aluno do average_single_line
def check_student_grade(manager: GraphManager):

    try:
        aluno = "Pedro Lucas Ferreira Gomes"
        serie = '7º Ano'
        disciplina = "Educação Física"
        etapa = "2º BIMESTRE"

        # Lê o arquivo CSV gerado por average_single_line
        df = filereader(manager.filename[10])

        # Filtra o DataFrame para encontrar o aluno
        aluno_row = df[df['NomeAluno'].astype(str).str.strip().str.lower() == aluno.strip().lower()]
        if aluno_row.empty:
            print(f"Aluno '{aluno}' não encontrado.")
            return None

        # Busca a coluna correspondente à disciplina e etapa
        col_name = f"{serie}_{disciplina}_{etapa}"
        if col_name not in aluno_row.columns:
            print(f"Coluna '{col_name}' não encontrada no arquivo.")
            return None

        # Obtém a nota do aluno para a disciplina e etapa
        nota = aluno_row.iloc[0][col_name]
        print(f"\nAluno: Nota de {aluno}\nSerie: {serie}\nDisciplina: {disciplina}\nEtapa: {etapa}\nNota: {nota}\n")
        return nota

    except Exception as e:
        print(f"Erro ao consultar nota: {e}")
        return None