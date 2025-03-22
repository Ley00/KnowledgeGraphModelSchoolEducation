import datetime

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
            
            # Aplica mapeamentos se houver
            if mappings:
                for col, mapping in mappings.items():
                    if col in index_map and row[index_map[col]] in mapping:
                        row = tuple(
                            mapping.get(value, value) if i == index_map[col] else value
                            for i, value in enumerate(row)
                        )
            
            # Formata datas se houver
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

def paymenttreatment(columns, result_list):
    return studenttreatment(columns, result_list)

def guardianstreatment(columns, result_list):
    mappings = {
        "TipoResponsavel": {"P": "Pai", "M": "Mae"},
        "SexoResponsavel": {"M": "Masculino", "F": "Feminino"}
    }
    date_fields = ["DataNascimentoResponsavel"]
    return preprocessdata(columns, result_list, mappings, date_fields)

def averagetreatment(columns, result_list):
    return preprocessdata(columns, result_list)

def absencestreatment(columns, result_list):
    return preprocessdata(columns, result_list)