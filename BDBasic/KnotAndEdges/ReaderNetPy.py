#Le os dados de um grafo em formato de rede NetworkX e extrai informações sobre os nós.
def extractnetworkx(G):
    enrollment_info = {}

    for node_key, attributes in G.nodes(data=True):
        node_type = attributes.get("type")
        if node_type:
            if node_type not in enrollment_info:
                enrollment_info[node_type] = []
            node_info = dict(attributes)
            node_info['id'] = node_key
            enrollment_info[node_type].append(node_info)

    return enrollment_info, G

# Le os dados de um grafo em formato de rede PyTorch e extrai informações sobre os nós.
def extractpytorch(graph):
    enrollment_info = {}

    for node_key, attributes in graph.get('node_data', {}).items():
        node_type = attributes.get("type")
        if node_type:
            if node_type not in enrollment_info:
                enrollment_info[node_type] = []
            enrollment_info[node_type].append(dict(attributes))

    return enrollment_info