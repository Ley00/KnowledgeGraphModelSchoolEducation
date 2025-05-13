import datetime
import pandas
from Class import GraphManager
from DataExtraction.File import filereader, savearchivestudent
from DataExtraction.Views import get_paid_student, get_student, get_student_absences, get_student_averages, get_student_guardians

# Processamento de dados
def process_data(session, manager:GraphManager, student_name, academicperiod, specific):
    try:
        # Processa os alunos
        process_students(session, manager.filename[1], student_name, academicperiod, specific)

        # Processa as demais informações (média, pagamento, faltas, responsáveis)
        for key, view_func, treatment_func in [
            (2, get_student_averages, averagetreatment),
            (3, get_paid_student, paymenttreatment),
            (4, get_student_absences, absencestreatment),
            (5, get_student_guardians, guardianstreatment),
        ]:
            process_generic(session, manager.filename[1], manager.filename[key], view_func, treatment_func)

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