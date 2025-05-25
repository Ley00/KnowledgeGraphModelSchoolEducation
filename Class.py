import networkx
import os
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

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
            9: os.path.join(processing_dir, "scalers.pkl"),
            10: os.path.join(csv_dir, "media_nota_aluno_single_line.csv")
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
        
    def get_best_classifiers(self, X, y, scoring='accuracy', cv=3):
        self.random_state = 42 

        param_grids = [
            {
                "name": "Linear SVM",
                "estimator": SVC(kernel="linear", random_state=self.random_state),
                "params": {"C": [0.01, 0.1, 1, 10]}
            },
            {
                "name": "RBF SVM",
                "estimator": SVC(kernel="rbf", random_state=self.random_state),
                "params": {"C": [0.1, 1, 10], "gamma": [0.001, 0.01, 0.1]}
            },
            {
                "name": "Gaussian Process",
                "estimator": GaussianProcessClassifier(random_state=self.random_state),
                "params": {}
            },
            {
                "name": "Decision Tree",
                "estimator": DecisionTreeClassifier(random_state=self.random_state),
                "params": {"max_depth": [3, 5, 10, None], "min_samples_split": [2, 5, 10]}
            },
            {
                "name": "Random Forest",
                "estimator": RandomForestClassifier(random_state=self.random_state),
                "params": {"n_estimators": [50, 100], "max_depth": [5, 10, None]}
            },
            {
                "name": "Neural Net",
                "estimator": MLPClassifier(max_iter=1000, random_state=self.random_state),
                "params": {"alpha": [0.0001, 0.001], "hidden_layer_sizes": [(50,), (100,)]}
            },
            {
                "name": "AdaBoost",
                "estimator": AdaBoostClassifier(random_state=self.random_state),
                "params": {"n_estimators": [50, 100], "learning_rate": [0.5, 1.0]}
            },
            {
                "name": "QDA",
                "estimator": QuadraticDiscriminantAnalysis(),
                "params": {"reg_param": [0.0, 0.1, 0.5]}
            },
            {
                "name": "KNN",
                "estimator": KNeighborsClassifier(),
                "params": {"n_neighbors": [3, 5, 7], "weights": ["uniform", "distance"]}
            }
        ]

        results = []

        for config in param_grids:
            grid = GridSearchCV(
                config["estimator"],
                config["params"],
                cv=cv,
                n_jobs=-1,
                scoring=scoring
            )
            grid.fit(X, y)
            best_model = grid.best_estimator_
            results.append((config["name"], best_model))

        names = [name for name, _ in results]
        models = [clf for _, clf in results]

        return names, models
