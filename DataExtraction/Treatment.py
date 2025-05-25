from collections import defaultdict
import datetime
import random
import pandas
from Class import GraphManager
from DataExtraction.File import filereader, savearchivestudent
from DataExtraction.Views import get_paid_student, get_student, get_student_absences, get_student_averages, get_student_guardians

# Processamento de dados
def process_data(session, manager:GraphManager, student_name, academicperiod, specific):
    try:
        # # Processa os alunos
        # process_students(session, manager.filename[1], student_name, academicperiod, specific)

        # # Processa as demais informações (média, pagamento, faltas, responsáveis)
        # for key, view_func, treatment_func in [
        #     (2, get_student_averages, averagetreatment),
        #     (3, get_paid_student, paymenttreatment),
        #     (4, get_student_absences, absencestreatment),
        #     (5, get_student_guardians, guardianstreatment),
        # ]:
        #     process_generic(session, manager.filename[1], manager.filename[key], view_func, treatment_func)

        # average_single_line(manager)
        check_student_grade(manager)

    except Exception as e:
        print(f"Error in process_data: {e}")
        raise

# Processa os alunos e salva os dados em um arquivo
def process_students(session, filename, student_name, academicperiod, specific):
    try:
        query = get_student(specific, student_name, academicperiod)
        params = {"student_name": student_name, "academicperiod": academicperiod} if student_name or academicperiod else {}
        result = session.execute(query, params)
        
        result_list = studenttreatment(result.keys(), [row for row in result])

        columns = list(result.keys())
        data = pandas.DataFrame(result_list, columns=columns)
        savearchivestudent(filename, data)

    except Exception as e:
        print(f"Error in process_students: {e}")
        raise

# Processa os dados genéricos (média, pagamento, faltas, responsáveis) e salva em um arquivo
def process_generic(session, input_file, output_file, view_func, treatment_func):
    try:
        df = filereader(input_file)
        result_list = []

        for _, row in df.iterrows():
            query, params = view_func(row)
            result = session.execute(query, params)
            result_list.extend(result.fetchall())

        processed_data = treatment_func(result.keys(), result_list)
        
        columns = list(result.keys())
        data = pandas.DataFrame(processed_data, columns=columns)
        savearchivestudent(output_file, data)

    except Exception as e:
        print(f"Error in process_generic ({output_file}): {e}")
        raise

# Função para pré-processar os dados
def preprocessdata(columns, result_list, mappings=None, date_fields=None):
    """
    Processa os dados substituindo valores vazios, aplicando mapeamentos e formatando datas.
    """
    try:
        columns_list = list(columns)
        index_map = {col: columns_list.index(col) for col in columns_list}
        
        for idx, row in enumerate(result_list):
            row = tuple(
                "NULL" if value in [None, '', ' '] else value.strip() if isinstance(value, str) else value
                for value in row
            )
            
            if mappings:
                for col, mapping in mappings.items():
                    if col in index_map and row[index_map[col]] in mapping:
                        row = tuple(
                            mapping.get(value, value) if i == index_map[col] else value
                            for i, value in enumerate(row)
                        )
            
            if date_fields:
                for col in date_fields:
                    if col in index_map and isinstance(row[index_map[col]], datetime.datetime):
                        row = tuple(
                            row[index_map[col]].strftime("%Y-%m-%d") if i == index_map[col] else value
                            for i, value in enumerate(row)
                        )
            
            result_list[idx] = row

        return result_list
    except Exception as e:
        print(f"Erro durante o pré-processamento: {e}")
        raise

# Funções de tratamento específicas para cada tipo de dado
def studenttreatment(columns, result_list):
    mappings = {
        "SituacaoMatricula": {
            "1": "Aguardando Confirmacao", "2": "Aguardando Confirmacao Pagamento", "3": "Aguardando Secretaria",
            "M": "Matriculado", "T": "Transferido", "D": "Desistente", "O": "Trancado", "A": "Abandono",
            "C": "Cancelado", "0": "Pre Matriculado", "F": "Formado", "N": "Nao Matriculado", "X": "Concludente"
        },
        "SexoAluno": {"M": "Masculino", "F": "Feminino"}
    }
    return preprocessdata(columns, result_list, mappings)

# Função de tratamento para pagamentos
def paymenttreatment(columns, result_list):
    return studenttreatment(columns, result_list)

# Função de tratamento para responsáveis
def guardianstreatment(columns, result_list):
    mappings = {
        "TipoResponsavel": {"P": "Pai", "M": "Mae"},
        "SexoResponsavel": {"M": "Masculino", "F": "Feminino"}
    }
    date_fields = ["DataNascimentoResponsavel"]
    return preprocessdata(columns, result_list, mappings, date_fields)

# Função de tratamento para médias
def averagetreatment(columns, result_list):
    return preprocessdata(columns, result_list)

# Função de tratamento para faltas
def absencestreatment(columns, result_list):
    return preprocessdata(columns, result_list)

# Função para unir em uma única linha as médias de um aluno
def average_single_line(manager: GraphManager):
    try:
        # Define nomes das colunas relevantes
        unidade_col = 'NomeUnidade'
        periodo_col = 'NomePeriodo'
        curso_col = 'NomeCurso'
        serie_col = 'NomeSerie'
        turma_col = 'ApelidoTurma'
        situacao_col = 'SituacaoMatricula'
        aluno_col = 'NomeAluno'
        disciplina_col = 'NomeDisciplina'
        etapa_col = 'NomeEtapa'
        nota_col = 'ValorMedia'

        # Lê o arquivo de médias e remove colunas com 'ID'
        df = filereader(manager.filename[2])
        df = df[[col for col in df.columns if 'ID' not in col]]
        # df = df[df[aluno_col] == "Pedro Lucas Ferreira Gomes"]

        # Define colunas para agrupamento
        group_cols = [aluno_col]
        unidade_cols = [unidade_col]
        periodo_cols = [periodo_col, curso_col, serie_col, turma_col, situacao_col]

        alunos = {}
        # Agrupa por aluno
        for key, group_df in df.groupby(group_cols):
            unidades = []
            # Agrupa por unidade
            for unidade_key, unidade_df in group_df.groupby(unidade_cols):
                periodos = []
                # Agrupa por período
                for periodo_key, periodo_df in unidade_df.groupby(periodo_cols):
                    periodo_info = []
                    # Adiciona informações do período
                    for col, val in zip(periodo_cols, periodo_key):
                        periodo_info.append(col)
                        periodo_info.append(val)
                    # Adiciona disciplina, etapa e nota
                    for _, row in periodo_df.iterrows():
                        periodo_info.extend([
                            disciplina_col, row[disciplina_col],
                            etapa_col, row[etapa_col],
                            nota_col, f"{row[nota_col]:.5f}" if isinstance(row[nota_col], float) else str(row[nota_col])
                        ])
                    periodos.append(periodo_info)
                unidades.append((unidade_key, periodos))
            alunos[key] = unidades

        records = []
        # Monta linha única por aluno
        for key, unidades in alunos.items():
            base_line = []
            base_line.append(aluno_col)
            base_line.append(key[0])
            if unidades:
                # Primeira unidade completa
                unidade_key, periodos = unidades[0]
                base_line.append(unidade_col)
                base_line.append(unidade_key[0])
                if periodos:
                    base_line.extend(periodos[0])
                    # Demais períodos da primeira unidade
                    for periodo in periodos[1:]:
                        base_line.extend(periodo)
                # Demais unidades
                for unidade_key, periodos in unidades[1:]:
                    base_line.append(unidade_col)
                    base_line.append(unidade_key[0])
                    if periodos:
                        base_line.extend(periodos[0])
                        for periodo in periodos[1:]:
                            base_line.extend(periodo)
            records.append(base_line)

        # Preenche linhas para igualar tamanho
        max_len = max(len(r) for r in records) if records else 0
        records = [r + [""] * (max_len - len(r)) for r in records]
        result_df = pandas.DataFrame(records)

        # Salva resultado em CSV
        result_df.to_csv(manager.filename[10], header=False, index=False, encoding='utf-8')

    except Exception as e:
        print(f"Error in average_single_line: {e}")
        raise

# Função para verificar a nota de um aluno do average_single_line
def check_student_grade(manager: GraphManager):
    try:
        periodo = "2024"
        aluno = "Pedro Lucas Ferreira Gomes"
        disciplina = "Arte"
        etapa = "2º BIMESTRE"

        df = pandas.read_csv(manager.filename[10], header=None, encoding='utf-8', low_memory=False)

        aluno_row = df[df[1].astype(str).str.strip().str.lower() == aluno.strip().lower()]
        if aluno_row.empty:
            print(f"Aluno '{aluno}' não encontrado.")
            return None

        row = aluno_row.iloc[0]
        for i in range(len(row)):
            periodo_ok = True
            if periodo:
                periodo_ok = False
                for j in range(len(row)):
                    if (
                        str(row[j]) == "NomePeriodo"
                        and j + 1 < len(row)
                        and str(row[j + 1]).strip().lower() == periodo.strip().lower()
                    ):
                        periodo_ok = True
                        break
            if not periodo_ok:
                continue

            if (
                str(row[i]) == "NomeDisciplina"
                and i + 5 < len(row)
                and str(row[i + 1]).strip().lower() == disciplina.strip().lower()
                and str(row[i + 2]) == "NomeEtapa"
                and etapa.strip().upper() in str(row[i + 3]).upper()
                and str(row[i + 4]) == "ValorMedia"
            ):
                def find_prev_value(label):
                    for k in range(i, -1, -1):
                        if str(row[k]) == label and k + 1 < len(row):
                            return row[k + 1]
                    return ""

                labels = [
                    "NomePeriodo", "NomeCurso", "NomeSerie", "ApelidoTurma",
                    "SituacaoMatricula", "NomeAluno", "NomeDisciplina", "NomeEtapa", "ValorMedia"
                ]
                values = {}
                for label in labels[:-3]:
                    values[label] = find_prev_value(label)
                values["NomeAluno"] = row[1] if len(row) > 1 else ""
                values["NomeDisciplina"] = row[i + 1]
                values["NomeEtapa"] = row[i + 3]
                values["ValorMedia"] = row[i + 5]

                for label in labels:
                    print(f"{label}: {values.get(label, '')}")
                return values["ValorMedia"]

        print(f"Nota de {disciplina} em {etapa}" +
              (f" no período {periodo}" if periodo else "") +
              " não encontrada para este aluno.")
        return None

    except Exception as e:
        print(f"Erro ao consultar nota: {e}")
        return None