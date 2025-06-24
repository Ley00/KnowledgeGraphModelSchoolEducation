import pandas
import gc
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.metrics import accuracy_score, classification_report
from Class import GraphManager
from BDBasic.DataExtraction.File import filereader

# Função para codificar rótulos de colunas específicas
def encode_labels(df, columns):
    le_dict = {}
    df_encoded = df.copy()
    for col in columns:
        le = LabelEncoder()
        df_encoded[col] = le.fit_transform(df_encoded[col])
        le_dict[col] = le
    return df_encoded, le_dict

# Função para treinar e avaliar o modelo
def load_and_prepare_data(manager, features, target, average):
    df = filereader(manager.filename[2])
    df[average] = pandas.to_numeric(df[average], errors="coerce", downcast='float')
    df = df.dropna(subset=[average])
    df[target] = df[average].apply(manager.classify_grade).astype("category")

    for col in features:
        df[col] = df[col].astype("category")

    return df

# Função para treinar e avaliar múltiplos classificadores
def train_and_evaluate_classifiers(X_train, X_test, y_train, y_test):
    classifiers = {
        "KNN": KNeighborsClassifier(3),
        "Linear SVM": SVC(kernel="linear", C=0.025, random_state=42),
        "RBF SVM": SVC(gamma=2, C=1, random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=5, random_state=42),
        "Random Forest": RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1, random_state=42),
        "MLP (Neural Net)": MLPClassifier(alpha=1, max_iter=1000, random_state=42),
        "AdaBoost": AdaBoostClassifier(random_state=42),
        "Naive Bayes": GaussianNB(),
        "QDA": QuadraticDiscriminantAnalysis(),
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    }

    results = {}
    print("\n--- Avaliação dos Classificadores ---")
    for name, clf in classifiers.items():
        model = make_pipeline(StandardScaler(), clf)

        try:
            scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
            print(f"\n==== {name} ====")
            print(f"Acurácia média (validação cruzada): {scores.mean():.2f} (+/- {scores.std():.2f})")
            results[name] = {"accuracy_cv": scores.mean(), "std_cv": scores.std()}
        except Exception as e:
            print(f"Erro na validação cruzada para {name}: {e}")
            results[name] = {"accuracy_cv": None, "std_cv": None, "error_cv": str(e)}
            continue

        try:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            acc = accuracy_score(y_test, y_pred)
            report = classification_report(y_test, y_pred, zero_division=0)
            print(f"Acurácia no conjunto de teste: {acc:.2f}")
            print("Relatório de Classificação:")
            print(report)
            results[name]["accuracy_test"] = acc
            results[name]["classification_report"] = report
            del model, y_pred, report, acc, scores
            gc.collect()
        except Exception as e:
            print(f"Erro no treinamento/teste para {name}: {e}")
            results[name]["accuracy_test"] = None
            results[name]["classification_report"] = None
            results[name]["error_train_test"] = str(e)
    return results

# Função para plotar os resultados de acurácia
def plot_classification_results(results):
    names = list(results.keys())
    accuracies_test = [res.get("accuracy_test") for res in results.values()]

    valid_names = [name for i, name in enumerate(names) if accuracies_test[i] is not None]
    valid_accuracies = [acc for acc in accuracies_test if acc is not None]

    plt.figure(figsize=(14, 7))
    bars = plt.bar(valid_names, valid_accuracies, color='skyblue')
    plt.title("Acurácia dos Classificadores no Conjunto de Teste")
    plt.ylabel("Acurácia")
    plt.xlabel("Classificador")
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 1.05)
    plt.tight_layout()
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.01, f"{yval:.2f}", ha='center', va='bottom')

    plt.show()

# Função principal para comparação de classificadores de multiplas features
def classifiers_comparison_mf(manager: GraphManager):
    df = load_and_prepare_data(manager, manager.features, manager.target, manager.average)
    
    # Reduzindo o tamanho do DataFrame para 5% dos dados
    df = df.sample(frac=0.05, random_state=42).reset_index(drop=True)

    # Filtra para apenas os alunos do período 2024
    # df = df[df['NomePeriodo'] == '2024'].reset_index(drop=True)

    df_encoded, _ = encode_labels(df, manager.features)
    X = df_encoded[manager.features]
    y = df_encoded[manager.target]

    del df, df_encoded
    gc.collect()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, stratify=y, random_state=42
    )

    del X, y
    gc.collect()

    results = train_and_evaluate_classifiers(X_train, X_test, y_train, y_test)
    plot_classification_results(results)
    return results