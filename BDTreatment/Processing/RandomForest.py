from sklearn.model_selection import train_test_split
from Class import GraphManager
from BDBasic.DataExtraction.File import filereader, savearchivestudent
from BDTreatment.Processing.Preprocessing import encode_features_target_one, preprocess_data_one, split_features_targets_one
from BDTreatment.Processing.Training import predict_one, split_data_one, train_random_forest_one, evaluate_model_one

def random_forest_one(manager: GraphManager):
    df = filereader(manager.filename[10])

    # Prepara um DataFrame de notas escolares para uso em modelos de machine learning
    df, etapas, previsao_cols = preprocess_data_one(df, manager)

    # Divide o DataFrame em características (X) e alvos (y) para treinamento
    X, y = split_features_targets_one(df, etapas, previsao_cols)

    # Codifica as características e o alvo usando LabelEncoder
    X, y, le_X, le_y = encode_features_target_one(X, y)

    test_size = 0.2
    random_state = 42

    # Divide os dados em conjuntos de treinamento, validação e predição
    X_trainval, X_predic, y_trainval, y_predic = train_test_split(X, y, test_size=test_size, random_state=random_state)

    # Divide os dados de treinamento e validação em conjuntos de treinamento e teste
    X_train, X_test, y_train, y_test = split_data_one(X_trainval, y_trainval, test_size, random_state)

    # Treina um modelo de Random Forest com os dados de treinamento
    model = train_random_forest_one(manager, X_train, y_train, random_state=random_state)

    # Avalia o modelo com os dados de teste e imprime o relatório de classificação
    evaluate_model_one(manager, model, X_test, y_test, le_y)

    artifacts = {
        "model": model,
        "le_X": le_X,
        "le_y": le_y
    }

    # Salva o modelo treinado e os codificadores em um arquivo
    savearchivestudent(manager.filename[13], artifacts)

    # predict_one(manager, X_predic)