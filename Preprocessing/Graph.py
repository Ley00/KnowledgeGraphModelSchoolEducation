import networkx as nx
import torch
import matplotlib.pyplot as plt
from torch_geometric.data import Data
from DataExtraction.File import filereader, filedelete, savearchivestudent

def add_entities_and_relations(G, data, node_type, relation, id_column, enrollment_column=None, node_mapping=None, node_count=0):
    for _, row in data.iterrows():
        if node_type == 'Student':
            # Adiciona o aluno e todos os seus atributos ao grafo
            node_id = f"{node_type}_{row[id_column]}"
            enrollment_id = f"Enrollment_{row['IDMatricula']}"

            # Adiciona o aluno
            G.add_node(node_id, type='Student', **row.to_dict())
            
            # Adiciona a matrícula
            enrollment_attributes = {key: row[key] for key in data.columns if key != 'IDAluno'}
            G.add_node(enrollment_id, type='Enrollment', **enrollment_attributes)

            # Cria a relação aluno -> matrícula
            G.add_edge(node_id, enrollment_id, relation='has_enrollment')
            
            # Mapeamento dos nós para índices
            if node_id not in node_mapping:
                node_mapping[node_id] = node_count
                node_count += 1
            if enrollment_id not in node_mapping:
                node_mapping[enrollment_id] = node_count
                node_count += 1

        else:
            # Para os outros tipos de dados (como Grade, Payment, etc.)
            node_id = f"{node_type}_{row[id_column]}"
            enrollment_id = f"Enrollment_{row[enrollment_column]}"

            # Adiciona o nó com atributos
            G.add_node(node_id, type=node_type, **row.to_dict())
            
            # Cria a relação entre matrícula e o nó
            G.add_edge(enrollment_id, node_id, relation=relation)

            # Mapeamento dos nós para índices
            if node_id not in node_mapping:
                node_mapping[node_id] = node_count
                node_count += 1

    return node_mapping, node_count

# Processamento dos atributos dos nós (notas e valores)
def process_node_attributes(G, node_mapping):
    node_features = []

    for node in G.nodes:
        node_data = G.nodes[node]
        if 'type' in node_data:
            # Usando o mapeamento para associar os índices dos nós
            node_index = node_mapping[node]
            
            # Converte 'nota' e 'valor' para float, se possível, ou atribui 0 caso contrário
            score = node_data.get('score', 0)
            amount = node_data.get('amount', 0)
            
            # Verifica se a 'nota' e o 'valor' são strings e tenta convertê-los
            try:
                score = float(score) if isinstance(score, (int, float, str)) and score != '' else 0
            except ValueError:
                score = 0
            
            try:
                amount = float(amount) if isinstance(amount, (int, float, str)) and amount != '' else 0
            except ValueError:
                amount = 0
            
            node_features.append([score, amount])

    return node_features

# Processamento das arestas do grafo, associando relações e índices
def process_edges(G, node_mapping, relation_map):
    edge_index = []
    edge_attr = []

    for u, v, data in G.edges(data=True):
        u_idx = node_mapping[u]
        v_idx = node_mapping[v]
        edge_index.append([u_idx, v_idx])
        # Mapeia a relação para um número
        edge_attr.append([relation_map[data['relation']]])

    edge_index = torch.tensor(edge_index, dtype=torch.long).t().contiguous()
    edge_attr = torch.tensor(edge_attr, dtype=torch.float)

    return edge_index, edge_attr

# Função principal para processar e construir o grafo
def graphnode(foldercsv, filename):
    G = nx.Graph()
    node_mapping = {}  # Mapeamento dos IDs dos nós para índices numéricos
    node_count = 0  # Contador para os índices dos nós

    # Mapeamento das relações para números
    relation_map = {
        'has_enrollment': 0,
        'has_grade': 1,
        'made_payment': 2,
        'has_absence': 3,
        'responsible_for': 4
    }

    # Adicionar os dados de alunos, matrículas, médias, pagamentos, faltas e responsáveis
    students = filereader(foldercsv, filename["student"])
    node_mapping, node_count = add_entities_and_relations(G, students, 'Student', 'has_enrollment', 'IDAluno', 'IDMatricula', node_mapping, node_count)

    grades = filereader(foldercsv, filename["avg"])
    node_mapping, node_count = add_entities_and_relations(G, grades, 'Grade', 'has_grade', 'IDMedia', 'IDMatricula', node_mapping, node_count)

    payments = filereader(foldercsv, filename["payment"])
    node_mapping, node_count = add_entities_and_relations(G, payments, 'Payment', 'made_payment', 'IDMovimento', 'IDMatricula', node_mapping, node_count)

    absences = filereader(foldercsv, filename["absences"])
    node_mapping, node_count = add_entities_and_relations(G, absences, 'Absence', 'has_absence', 'IDFalta', 'IDMatricula', node_mapping, node_count)

    responsibles = filereader(foldercsv, filename["guardians"])
    node_mapping, node_count = add_entities_and_relations(G, responsibles, 'Responsible', 'responsible_for', 'IDResponsavel', 'IDMatricula', node_mapping, node_count)

    # Processar os atributos dos nós e as arestas
    node_features = process_node_attributes(G, node_mapping)
    edge_index, edge_attr = process_edges(G, node_mapping, relation_map)

    # Construir o objeto Data do PyG
    data = Data(x=torch.tensor(node_features, dtype=torch.float), edge_index=edge_index, edge_attr=edge_attr)

    filedelete(foldercsv, filename["networkx_graph"])
    savearchivestudent(foldercsv, filename["networkx_graph"], G)

    filedelete(foldercsv, filename["pytorch_graph"])
    savearchivestudent(foldercsv, filename["pytorch_graph"], {
        'x': data.x,  # Atributos dos nós
        'edge_index': data.edge_index,  # Arestas
        'edge_attr': data.edge_attr  # Atributos das arestas
    })

# Desenhar o grafo com a biblioteca matplotlib
def draw_graph(foldercsv, filename):
    G = filereader(foldercsv, filename)
    plt.figure(figsize=(12, 10))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=False, node_size=2000, node_color='lightblue', edge_color='gray')
    labels = {node: G.nodes[node].get('name', node) for node in G.nodes}
    nx.draw_networkx_labels(G, pos, labels, font_size=8)
    plt.title("Student Relationship Graph")
    plt.show()

# Função para consultar informações de um aluno
def consult_student(foldercsv, filename, id_aluno):
    # Criar o grafo
    G = filereader(foldercsv, filename)

    student_id = f"Student_{id_aluno}"  # Certifique-se de que está adicionando o prefixo correto

    if student_id not in G:
        return "Aluno não encontrado."
    
    info = {'Aluno': G.nodes[student_id]['NomeAluno'], 'Matriculas': []}
    
    for enrollment_id, dados in G[student_id].items():
        if dados['relation'] == 'has_enrollment':
            matricula_info = {
                'ID': enrollment_id,
                'Status': G.nodes[enrollment_id]['SituacaoMatricula'],
                'Médias': [],
                'Faltas': [],
                'Pagamentos': [],
                'Responsáveis': []
            }
            
            # Organiza as médias com nome da disciplina e da etapa
            matricula_info['Médias'] = [
                f"{G.nodes[n]['NomeDisciplina']} {G.nodes[n]['NomeEtapa']}: {G.nodes[n]['ValorMedia']}"
                for n in G.neighbors(enrollment_id)
                if 'type' in G.nodes[n] and G.nodes[n]['type'] == 'Grade'
            ]

            # Organiza as faltas, agrupando por disciplina
            matricula_info['Faltas'] = {}
            for n in G.neighbors(enrollment_id):
                if 'type' in G.nodes[n] and G.nodes[n]['type'] == 'Absence':
                    subject = G.nodes[n]['NomeDisciplina']
                    date = G.nodes[n]['DataFalta']
                    
                    # Se a disciplina não estiver no dicionário, adiciona uma lista
                    if subject not in matricula_info['Faltas']:
                        matricula_info['Faltas'][subject] = []
                    
                    # Adiciona a falta à lista da disciplina correspondente
                    matricula_info['Faltas'][subject].append(f"Data da falta: {date}")

            # Formatar as faltas agrupadas por disciplina
            faltas_formatadas = []
            for subject, dates in matricula_info['Faltas'].items():
                faltas_formatadas.append(f"{subject}:")
                for date in dates:
                    faltas_formatadas.append(f"  - {date}")
            matricula_info['Faltas'] = faltas_formatadas
            
            # Organiza os pagamentos
            matricula_info['Pagamentos'] = [
                f"{descricao}: {valor}"
                for descricao, valor in [
                    (G.nodes[n]['DescricaoMovimento'], G.nodes[n]['ValorPagoMovimento'])
                    for n in G.neighbors(enrollment_id) 
                    if 'type' in G.nodes[n] and G.nodes[n]['type'] == 'Payment'
                ]
            ]
            
            # Adiciona os responsáveis
            matricula_info['Responsáveis'] = [
                G.nodes[n]['NomeResponsavel'] 
                for n in G.neighbors(enrollment_id) 
                if 'type' in G.nodes[n] and G.nodes[n]['type'] == 'Responsible'
            ]

            info['Matriculas'].append(matricula_info)
    
    # Exibe as informações de forma organizada
    print(f"Aluno: {info['Aluno']}\n")
    for matricula in info['Matriculas']:
        print(f"ID da Matrícula: {matricula['ID']}")
        print(f"Status: {matricula['Status']}")
        print("\nResponsáveis:")
        for responsavel in matricula['Responsáveis']:
            print(f"- {responsavel}")
        print("\nMédias:")
        for media in matricula['Médias']:
            print(f"- {media}")
        print("\nFaltas:")
        for falta in matricula['Faltas']:
            print(f"- {falta}")
        print("\nPagamentos:")
        for pagamento in matricula['Pagamentos']:
            print(f"- {pagamento}")
        print("\n" + "-"*50 + "\n")