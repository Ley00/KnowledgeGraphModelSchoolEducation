import networkx
from matplotlib import pyplot
from Class import GraphManager
from DataExtraction.File import filereader
from KnotAndEdges.ReaderNetPy import extractnetworkx, extractpytorch

# Este script é usado para visualizar e analisar dados de alunos usando NetworkX e PyTorch Geometric
def draw_graph(manager: GraphManager):
    data = filereader(manager.filename[6])
    pyplot.figure(figsize=(12, 10))
    pos = networkx.spring_layout(data, seed=42)
    networkx.draw(data, pos, with_labels=False, node_size=2000, node_color='lightblue', edge_color='gray')
    labels = {node: data.nodes[node].get('name', node) for node in data.nodes}
    networkx.draw_networkx_labels(data, pos, labels, font_size=8)
    pyplot.title("Student Relationship Graph")
    pyplot.show()

# Função para consultar informações de um aluno específico usando NetworkX
def consult_student_networkx(manager: GraphManager, id_aluno):
    data = filereader(manager.filename[6])
    extracted_data, G = extractnetworkx(data)

    student_id = f"Student_{id_aluno}"
    student_info = next((s for s in extracted_data['Student'] if s['id'] == student_id), None)
    if not student_info:
        return "Aluno não encontrado."

    info = {'Aluno': student_info['NomeAluno'], 'Matrículas': []}

    for enrollment_id, dados in G[student_id].items():
        if dados['relation'] != 'has_enrollment':
            continue

        enrollment_attrs = G.nodes[enrollment_id]
        matricula_info = {
            'ID': enrollment_id,
            'Status': enrollment_attrs.get('SituacaoMatricula', 'Desconhecido'),
        }

        for type_name in manager.type_mapping:
            if type_name != "Student":
                matricula_info[type_name] = []

        for neighbor in G.neighbors(enrollment_id):
            node = G.nodes[neighbor]
            tipo = node.get('type')
            if tipo in matricula_info:
                matricula_info[tipo].append(node)

        info['Matrículas'].append(matricula_info)

    print(f"Aluno: {info['Aluno']}")
    for matricula in info['Matrículas']:
        print(f"\nID da Matrícula: {matricula['ID']}")
        print(f"Status: {matricula['Status']}")

        print("\nResponsáveis:")
        for responsavel in matricula.get('Responsible', []):
            print(f"- {responsavel.get('NomeResponsavel', 'Sem Nome')}")

        print("\nMédias:")
        for media in matricula.get('Grade', []):
            nome_disciplina = media.get("NomeDisciplina", "Disciplina Desconhecida")
            nome_etapa = media.get("NomeEtapa", "Etapa Desconhecida")
            valor_media = media.get("ValorMedia", "Sem Nota")
            try:
                valor_media_float = float(valor_media)
                print(f"- {nome_disciplina} {nome_etapa}: {valor_media_float:.5f}")
            except ValueError:
                print(f"- {nome_disciplina} {nome_etapa}: {valor_media}")

        print("\nFaltas:")
        faltas_por_disciplina = {}
        for falta in matricula.get('Absence', []):
            nome_disciplina = falta.get("NomeDisciplina", "Disciplina Desconhecida")
            nome_etapa = falta.get("NomeEtapa", "Etapa Desconhecida")
            data_falta = falta.get("DataFalta", "Data Desconhecida")
            faltas_por_disciplina.setdefault(nome_disciplina, {}).setdefault(nome_etapa, []).append(data_falta)

        for disciplina, etapas in faltas_por_disciplina.items():
            print(f"- {disciplina}:")
            for etapa, datas in etapas.items():
                for data in datas:
                    print(f"   - Etapa: {etapa}, Data da falta: {data}")

        print("\nPagamentos:")
        for pagamento in matricula.get('Payment', []):
            descricao_pagamento = pagamento.get("DescricaoMovimento", "Pagamento Desconhecido")
            valor_pago = pagamento.get("ValorPagoMovimento", "0.0")
            try:
                valor_pago_float = float(valor_pago)
                if "Mês" in descricao_pagamento:
                    descricao_pagamento = f"Mês {descricao_pagamento.split()[-1].upper()}"
                print(f"- {descricao_pagamento}: {valor_pago_float:.4f}")
            except ValueError:
                print(f"- {descricao_pagamento}: {valor_pago}")

        print("\n" + "-"*50 + "\n")

# Função para consultar informações de um aluno específico usando PyTorch Geometric
def consult_student_pytorch(manager: GraphManager, id_aluno):
    data = filereader(manager.filename[7])

    data_types = [tipo for tipo in manager.type_mapping if tipo != "Student"]

    extracted_data = extractpytorch(data)

    student_key = f"Student_{id_aluno}"
    if student_key not in data['node_data']:
        return "Aluno não encontrado."

    student_info = data['node_data'][student_key]
    id_matricula = student_info.get("IDMatricula", None)

    info = {'Aluno': student_info.get("NomeAluno", "Desconhecido"), 'Matrículas': [{}]}

    for tipo in data_types:
        info['Matrículas'][0][tipo] = [
            item for item in extracted_data.get(tipo, [])
            if item.get("IDMatricula") == id_matricula
        ]

    print(f"Aluno: {info['Aluno']}")
    for matricula in info['Matrículas']:
        print("\nResponsáveis:")
        for responsavel in matricula.get('Responsible', []):
            print(f"- {responsavel.get('NomeResponsavel', 'Sem Nome')}")

        print("\nMédias:")
        for media in matricula.get('Grade', []):
            nome_disciplina = media.get("NomeDisciplina", "Disciplina Desconhecida")
            nome_etapa = media.get("NomeEtapa", "Etapa Desconhecida")
            valor_media = media.get("ValorMedia", "Sem Nota")
            try:
                valor_media_float = float(valor_media)
                print(f"- {nome_disciplina} {nome_etapa}: {valor_media_float:.5f}")
            except ValueError:
                print(f"- {nome_disciplina} {nome_etapa}: {valor_media}")

        print("\nFaltas:")
        faltas_por_disciplina = {}
        for falta in matricula.get('Absence', []):
            nome_disciplina = falta.get("NomeDisciplina", "Disciplina Desconhecida")
            nome_etapa = falta.get("NomeEtapa", "Etapa Desconhecida")
            data_falta = falta.get("DataFalta", "Data Desconhecida")
            faltas_por_disciplina.setdefault(nome_disciplina, {}).setdefault(nome_etapa, []).append(data_falta)

        for disciplina, etapas in faltas_por_disciplina.items():
            print(f"- {disciplina}:")
            for etapa, datas in etapas.items():
                for data in datas:
                    print(f"   - Etapa: {etapa}, Data da falta: {data}")

        print("\nPagamentos:")
        for pagamento in matricula.get('Payment', []):
            descricao_pagamento = pagamento.get("DescricaoMovimento", "Pagamento Desconhecido")
            valor_pago = pagamento.get("ValorPagoMovimento", "0.0")
            try:
                valor_pago_float = float(valor_pago)
                if "Mês" in descricao_pagamento:
                    descricao_pagamento = f"Mês {descricao_pagamento.split()[-1].upper()}"
                print(f"- {descricao_pagamento}: {valor_pago_float:.4f}")
            except ValueError:
                print(f"- {descricao_pagamento}: {valor_pago}")
        print("\n" + "-"*50 + "\n")