import networkx
import os

class GraphManager:
    def __init__(self, filename=None):
        self.graph = networkx.Graph()
        self.node_mapping = {}
        self.node_count = 0
        self.folder = "Result"

        # Diretórios personalizados
        csv_dir = os.path.join(self.folder, "CSV")
        preprocessing_dir = os.path.join(self.folder, "Preprocessing")
        processing_dir = os.path.join(self.folder, "Processing")

        # Definir arquivos padrão com caminhos atualizados
        self.filename = filename if filename else {
            1: os.path.join(csv_dir, "aluno.csv"),
            2: os.path.join(csv_dir, "media_nota_aluno.csv"),
            3: os.path.join(csv_dir, "pagamento_aluno.csv"),
            4: os.path.join(csv_dir, "faltas_aluno.csv"),
            5: os.path.join(csv_dir, "responsaveis_aluno.csv"),
            6: os.path.join(preprocessing_dir, "networkx_graph.graphml"),
            7: os.path.join(preprocessing_dir, "pytorch_graph.pt"),
            8: os.path.join(processing_dir, "lstm_grade_prediction.pth"),
            9: os.path.join(processing_dir, "scalers.pkl")
        }

        self.data_types = [
            (1, "Student", "has_enrollment", "IDAluno", "IDMatricula"),
            (2, "Grade", "has_grade", "IDMedia", "IDMatricula"),
            (3, "Payment", "made_payment", "IDMovimento", "IDMatricula"),
            (4, "Absence", "has_absence", "IDFalta", "IDMatricula"),
            (5, "Responsible", "responsible_for", "IDResponsavel", "IDMatricula")
        ]

        # Campos utilizadas para os modelos
        self.features = ['NomePeriodo', 'NomeSerie', 'NomeAluno', 'NomeDisciplina', 'NomeEtapa']
        self.target = 'Media'
        self.average = 'ValorMedia'

    def classify_grade(self, valor):
        if valor >= 9.0:
            return "A"
        elif valor >= 8.0:
            return "B"
        elif valor >= 7.0:
            return "C"
        elif valor >= 6.0:
            return "D"
        else:
            return "E"