import numpy
import pandas
import matplotlib.pyplot as plt
import gc
from matplotlib.colors import ListedColormap
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.neural_network import MLPClassifier
from Class import GraphManager
from DataExtraction.File import filereader

# Codificação de colunas categóricas
def encode_labels(df, columns):
    le_dict = {}
    df_encoded = df.copy()
    for col in columns:
        le = LabelEncoder()
        df_encoded[col] = le.fit_transform(df_encoded[col])
        le_dict[col] = le
    return df_encoded, le_dict

# Carregamento e preparação dos dados
def load_and_prepare_data(manager, features, target, average):
    df = filereader(manager.filename[2])
    df = df[[col for col in df.columns if 'ID' not in col]]
    df[average] = pandas.to_numeric(df[average], errors="coerce", downcast='float')
    df = df.dropna(subset=[average])
    df[target] = df[average].apply(manager.classify_grade).astype("category")
    for col in features:
        df[col] = df[col].astype("category")
    return df

# Seleção de amostra estratificada
def sample_stratified(df, target, sample_size, target_names):
    df_sampled = df.groupby(target).apply(
        lambda x: x.sample(n=min(len(x), sample_size // len(target_names)), random_state=42)
    ).reset_index(drop=True)
    return df_sampled

# Pré-processamento: normalização, seleção de atributos e t-SNE
def preprocess_data(X, y, k_best):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    selector = SelectKBest(score_func=f_classif, k=min(k_best, X_scaled.shape[1]))
    X_selected = selector.fit_transform(X_scaled, y)
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_selected)
    return X_selected, X_pca

# Obtenção dos classificadores e seus nomes
def get_classifiers():
    names = [
        "Nearest Neighbors", "Linear SVM", "RBF SVM", "Gaussian Process",
        "Decision Tree", "Random Forest", "Neural Net", "AdaBoost",
        "Naive Bayes", "QDA"
    ]
    classifiers = [
        KNeighborsClassifier(3),
        SVC(kernel="linear", C=0.025, random_state=42),
        SVC(gamma=2, C=1, random_state=42),
        GaussianProcessClassifier(1.0 * RBF(1.0), random_state=42),
        DecisionTreeClassifier(max_depth=5, random_state=42),
        RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1, random_state=42),
        MLPClassifier(alpha=1, max_iter=1000, random_state=42),
        AdaBoostClassifier(random_state=42),
        GaussianNB(),
        QuadraticDiscriminantAnalysis(),
    ]
    return names, classifiers

# Visualização dos resultados com matplotlib
def plot_classifiers_results(X_vis, X_train, y, classifiers, names, target_labels):
    x_min, x_max = X_vis[:, 0].min() - 1, X_vis[:, 0].max() + 1
    y_min, y_max = X_vis[:, 1].min() - 1, X_vis[:, 1].max() + 1
    xx, yy = numpy.meshgrid(numpy.linspace(x_min, x_max, 200),
                         numpy.linspace(y_min, y_max, 200))
    
    cmap_bold = ['red', 'green', 'blue', 'gold', 'purple']
    cmap_light = ListedColormap(['#FFAAAA', '#AAFFAA', '#AAAAFF', '#FFFFAA', '#FFCCFF'])

    plt.figure(figsize=(25, 20))
    for idx, (name, clf) in enumerate(zip(names, classifiers), 1):
        clf.fit(X_vis, y)
        Z = clf.predict(numpy.c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)

        plt.subplot(4, 3, idx)
        plt.contourf(xx, yy, Z, cmap=cmap_light, alpha=0.4)
        for i, label in enumerate(target_labels):
            mask = y == i
            plt.scatter(
                X_vis[mask, 0], X_vis[mask, 1],
                c=cmap_bold[i],
                label=label,
                edgecolor="k", s=30
            )
        plt.title(name)
        plt.legend(loc="best", fontsize="small")
        plt.grid(True)
    plt.tight_layout()
    plt.suptitle("Comparação de Classificadores com PCA", fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.subplots_adjust(hspace=0.4)
    plt.show()

# Função principal de comparação
def classifiers_comparison_pca(manager: GraphManager, sample_size=100, k_best=5):
    df = load_and_prepare_data(manager, manager.features, manager.target, manager.average)

    # Filtrando os dados para o ano de 2024
    df = df[df['NomePeriodo'] == '2024'].reset_index(drop=True)

    columns_needed = manager.features + [manager.target]
    df = df[columns_needed].copy()
    df_encoded, label_encoders = encode_labels(df, columns_needed)

    X = df_encoded[manager.features]
    y = df_encoded[manager.target]
    target_names = label_encoders[manager.target].classes_

    df_encoded[manager.target] = y
    df_sampled = sample_stratified(df_encoded, manager.target, sample_size, target_names)

    X = df_sampled[manager.features]
    y = df_sampled[manager.target]

    X_selected, X_tsne = preprocess_data(X, y, k_best)
    names, classifiers = get_classifiers()
    # names, classifiers = manager.get_best_classifiers(X_selected, y)
    plot_classifiers_results(X_tsne, X_selected, y, classifiers, names, target_names)

    del df, df_encoded, X, y, X_selected, X_tsne
    gc.collect()