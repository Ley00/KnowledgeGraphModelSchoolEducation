from matplotlib import pyplot
import numpy
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, mean_absolute_error, mean_squared_error
from BDBasic.DataExtraction.File import filereader

def split_data_one(X, y, test_size, random_state):
    if X is None or y is None:
        raise ValueError("X e y não podem ser None")
    
    if len(X) != len(y):
        raise ValueError(f"X e y devem ter o mesmo número de amostras. X: {len(X)}, y: {len(y)}")
    
    if not 0 < test_size < 1:
        raise ValueError("test_size deve estar entre 0 e 1")
    
    try:
        X_float = X.astype(float)
    except ValueError as e:
        raise ValueError(f"Erro ao converter X para float: {e}")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_float, 
        y, 
        test_size=test_size, 
        random_state=random_state,
        stratify=y
    )
    
    return X_train, X_test, y_train, y_test

def train_random_forest_one(manager, X_train, y_train, random_state=42, **kwargs):
    default_params = {
        'n_estimators': 200,           # Mais árvores para melhor estabilidade
        'max_depth': 10,               # Evita overfitting em dados pequenos
        'min_samples_split': 5,        # Mínimo de amostras para dividir um nó
        'min_samples_leaf': 2,         # Mínimo de amostras por folha
        'max_features': 'sqrt',        # Número de features por árvore
        'bootstrap': True,             # Usar bootstrap sampling
        'oob_score': True,             # Calcular score out-of-bag
        'class_weight': 'balanced',    # Balancear classes automaticamente
        'random_state': random_state,
        'n_jobs': -1                   # Usar todos os cores disponíveis
    }
    
    default_params.update(kwargs)
    
    if X_train is None or y_train is None:
        raise ValueError("X_train e y_train não podem ser None")
    
    if len(X_train) != len(y_train):
        raise ValueError(f"X_train e y_train devem ter o mesmo número de amostras. "
                        f"X_train: {len(X_train)}, y_train: {len(y_train)}")
    
    if len(X_train) < 10:
        print("Aviso: Poucas amostras de treinamento. Reduzindo complexidade do modelo.")
        default_params.update({
            'n_estimators': 50,
            'max_depth': 5,
            'min_samples_split': 2
        })
    
    try:
        clf = RandomForestClassifier(**default_params)
        clf.fit(X_train, y_train)
        
        training_info = []
        training_info.append(f"   Amostras de treinamento: {len(X_train)}")
        training_info.append(f"   Número de árvores: {clf.n_estimators}")
        
        if hasattr(clf, 'oob_score_') and clf.oob_score_ is not None:
            training_info.append(f"   OOB Score: {clf.oob_score_:.4f}")
        
        if hasattr(clf, 'feature_importances_'):
            importances = clf.feature_importances_
            training_info.append(f"   Importância das features: {importances}")
            
            feature_names = [f"Etapa_{i+1}" for i in range(len(importances))]
            for i, (name, importance) in enumerate(zip(feature_names, importances)):
                if importance > 0.1:
                    training_info.append(f"      {name}: {importance:.3f}")
        
        with open(manager.filename[12], "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n\n")
            f.write("Treinamento do Modelo - Random Forest\n")
            for info in training_info:
                f.write(info + "\n")
            f.write("\n")
            f.write("=" * 80 + "\n")
        
        return clf
        
    except Exception as e:
        raise RuntimeError(f"Erro ao treinar o modelo Random Forest: {str(e)}")

def evaluate_model_one(manager, model, X_test, y_test, le_y, save_plots=False, plot_dir=None):
    y_pred = model.predict(X_test)
    
    y_test_decoded = le_y.inverse_transform(y_test)
    y_pred_decoded = le_y.inverse_transform(y_pred)
    
    is_categorical = any(isinstance(val, str) and val in ['A', 'B', 'C', 'D', 'E'] 
                        for val in numpy.concatenate([y_test_decoded[:5], y_pred_decoded[:5]]))
    
    output_lines = []
    
    if is_categorical:
        output_lines.append("MODO: Classificação Categórica (A-E)")
        
        accuracy = accuracy_score(y_test, y_pred)
        output_lines.append(f"\n MÉTRICAS DE CLASSIFICAÇÃO:")
        output_lines.append(f"Acurácia: {accuracy:.4f} ({accuracy*100:.1f}%)")
        
        output_lines.append(f"\n ANÁLISE POR CATEGORIAS:")
        categorias = {'A': 'Excelente (9.0-10.0)', 'B': 'Bom (8.0-8.9)', 
                     'C': 'Regular (7.0-7.9)', 'D': 'Fraco (6.0-6.9)', 
                     'E': 'Insuficiente (<6.0)'}
        
        for categoria, descricao in categorias.items():
            mask_real = y_test_decoded == categoria
            mask_pred = y_pred_decoded == categoria
            if numpy.any(mask_real) or numpy.any(mask_pred):
                precisao = numpy.sum((y_test_decoded == categoria) & (y_pred_decoded == categoria)) / max(numpy.sum(mask_pred), 1)
                recall = numpy.sum((y_test_decoded == categoria) & (y_pred_decoded == categoria)) / max(numpy.sum(mask_real), 1)
                output_lines.append(f"{categoria} - {descricao}: Precisão={precisao:.3f}, Recall={recall:.3f}")
        
        metrics = {
            'accuracy': accuracy,
            'mae': None,
            'rmse': None,
            'accuracy_with_tolerance': None,
            'y_test_decoded': y_test_decoded,
            'y_pred_decoded': y_pred_decoded,
            'is_categorical': True
        }
        
    else:
        output_lines.append("MODO: Regressão Numérica")
        
        try:
            y_test_numeric = y_test_decoded.astype(float)
            y_pred_numeric = y_pred_decoded.astype(float)
            
            mae = mean_absolute_error(y_test_numeric, y_pred_numeric)
            mse = mean_squared_error(y_test_numeric, y_pred_numeric)
            rmse = numpy.sqrt(mse)
            
            tolerance = 0.5
            accurate_within_tolerance = numpy.abs(y_test_numeric - y_pred_numeric) <= tolerance
            accuracy_with_tolerance = numpy.mean(accurate_within_tolerance)
            
            output_lines.append(f"\n MÉTRICAS NUMÉRICAS:")
            output_lines.append(f"MAE (Erro Médio Absoluto): {mae:.4f}")
            output_lines.append(f"RMSE (Raiz do Erro Quadrático Médio): {rmse:.4f}")
            output_lines.append(f"Acurácia com tolerância (±{tolerance}): {accuracy_with_tolerance:.4f} ({accuracy_with_tolerance*100:.1f}%)")
            
            errors = y_pred_numeric - y_test_numeric
            output_lines.append(f"\n ANÁLISE DE ERROS:")
            output_lines.append(f"Erro médio: {numpy.mean(errors):.4f}")
            output_lines.append(f"Desvio padrão dos erros: {numpy.std(errors):.4f}")
            output_lines.append(f"Erro máximo: {numpy.max(numpy.abs(errors)):.4f}")
            
            output_lines.append(f"\n ANÁLISE POR FAIXAS DE NOTAS:")
            faixas = [(0, 5, "Insuficiente"), (5, 7, "Regular"), (7, 8.5, "Bom"), (8.5, 10, "Excelente")]
            
            for min_nota, max_nota, categoria in faixas:
                mask = (y_test_numeric >= min_nota) & (y_test_numeric < max_nota)
                if numpy.any(mask):
                    faixa_mae = mean_absolute_error(y_test_numeric[mask], y_pred_numeric[mask])
                    faixa_accuracy = numpy.mean(numpy.abs(y_test_numeric[mask] - y_pred_numeric[mask]) <= tolerance)
                    output_lines.append(f"{categoria} ({min_nota}-{max_nota}): MAE={faixa_mae:.3f}, Acc={faixa_accuracy:.3f}")
            
        except ValueError:
            output_lines.append("Aviso: Não foi possível converter as notas para valores numéricos")
            mae = mse = rmse = accuracy_with_tolerance = None
        
        accuracy = accuracy_score(y_test, y_pred)
        output_lines.append(f"\n MÉTRICAS DE CLASSIFICAÇÃO:")
        output_lines.append(f"Acurácia exata: {accuracy:.4f} ({accuracy*100:.1f}%)")
        
        metrics = {
            'accuracy': accuracy,
            'mae': mae,
            'rmse': rmse,
            'accuracy_with_tolerance': accuracy_with_tolerance,
            'y_test_decoded': y_test_decoded,
            'y_pred_decoded': y_pred_decoded,
            'is_categorical': False
        }
    
    output_lines.append(f"\n RELATÓRIO DETALHADO:")
    output_lines.append(classification_report(y_test_decoded, y_pred_decoded, zero_division=0))
    
    unique_classes = numpy.unique(numpy.concatenate([y_test_decoded, y_pred_decoded]))
    if len(unique_classes) <= 20:
        cm = confusion_matrix(y_test_decoded, y_pred_decoded)
        output_lines.append(f"\n MATRIZ DE CONFUSÃO:")
        output_lines.append(str(cm))
        
        if save_plots and plot_dir:
            pyplot.figure(figsize=(10, 8))
            try:
                import seaborn as sns
                sns.heatmap(cm, annot=True, fmt='d', xticklabels=unique_classes, 
                           yticklabels=unique_classes, cmap='Blues')
            except ImportError:
                pyplot.imshow(cm, interpolation='nearest', cmap='Blues')
                pyplot.colorbar()
            
            pyplot.title('Matriz de Confusão - Predição de Notas')
            pyplot.ylabel('Valores Reais')
            pyplot.xlabel('Valores Preditos')
            pyplot.tight_layout()
            pyplot.savefig(f"{plot_dir}/confusion_matrix.png", dpi=300, bbox_inches='tight')
            pyplot.close()
    
    with open(manager.filename[12], "a", encoding="utf-8") as f:
        f.write("\n" + "Avaliação do Modelo - Random Forest\n")
        
        for line in output_lines:
            f.write(str(line) + "\n")
        
        f.write(f"Total de amostras testadas: {len(y_test)}\n")
        f.write(f"Tipo de dados: {'Categórico (A-E)' if is_categorical else 'Numérico'}\n")
        f.write("\n" + "=" * 80)
    
    return metrics

def predict_one(manager, X_predic):
    try:
        df = filereader(manager.filename[13])
        
        if X_predic is None or len(X_predic) == 0:
            raise ValueError("X_predic não pode ser None ou vazio")
        
        X_predic = numpy.array([
            [str(val) if val is not None and str(val).strip() != '' else "0.0" 
             for val in row] 
            for row in X_predic
        ])
        
        le_X = df["le_X"]
        model = df["model"]
        le_y = df["le_y"]
        
        if X_predic.shape[1] != len(le_X):
            raise ValueError(f"Número de features incompatível. "
                           f"Esperado: {len(le_X)}, Recebido: {X_predic.shape[1]}")
        
        X_encoded = numpy.zeros_like(X_predic, dtype=float)
        
        for i in range(X_predic.shape[1]):
            current_feature = X_predic[:, i]
            encoder = le_X[i]
            
            unknown_mask = ~numpy.isin(current_feature, encoder.classes_)
            
            if numpy.any(unknown_mask):
                unknown_values = set(current_feature[unknown_mask])
                print(f"Aviso: Valores desconhecidos na feature {i}: {unknown_values}")
                
                if len(encoder.classes_) > 0:
                    most_frequent_class = encoder.classes_[0]
                    current_feature[unknown_mask] = most_frequent_class
                    print(f"   Substituído por: {most_frequent_class}")
                else:
                    raise ValueError(f"Encoder da feature {i} não possui classes conhecidas")
            
            try:
                X_encoded[:, i] = encoder.transform(current_feature)
            except ValueError as e:
                raise ValueError(f"Erro ao transformar feature {i}: {str(e)}")
        
        try:
            y_pred = model.predict(X_encoded)
        except Exception as e:
            raise RuntimeError(f"Erro durante a predição: {str(e)}")
        
        try:
            predictions = le_y.inverse_transform(y_pred)
        except Exception as e:
            raise RuntimeError(f"Erro ao decodificar predições: {str(e)}")
        
        print(f"Predições realizadas para {len(X_predic)} amostras")
        
        return predictions
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Modelo não encontrado em: {manager.filename[13]}")
    except Exception as e:
        raise RuntimeError(f"Erro inesperado na função predict_one: {str(e)}")

def predict_with_validation(manager, X_predic, return_confidence=False):
    try:
        df = filereader(manager.filename[13])
        model = df["model"]
        le_y = df["le_y"]
        
        predictions = predict_one(manager, X_predic)
        
        if return_confidence and hasattr(model, 'predict_proba'):
            X_predic_array = numpy.array([
                [str(val) if val is not None and str(val).strip() != '' else "0.0" 
                 for val in row] 
                for row in X_predic
            ])
            
            le_X = df["le_X"]
            X_encoded = numpy.zeros_like(X_predic_array, dtype=float)
            
            for i in range(X_predic_array.shape[1]):
                current_feature = X_predic_array[:, i]
                encoder = le_X[i]
                unknown_mask = ~numpy.isin(current_feature, encoder.classes_)
                
                if numpy.any(unknown_mask):
                    most_frequent_class = encoder.classes_[0]
                    current_feature[unknown_mask] = most_frequent_class
                
                X_encoded[:, i] = encoder.transform(current_feature)
            
            probabilities = model.predict_proba(X_encoded)
            max_probs = numpy.max(probabilities, axis=1)
            
            return predictions, max_probs
        
        return predictions
        
    except Exception as e:
        raise RuntimeError(f"Erro na predição com validação: {str(e)}")

def batch_predict_with_progress(manager, X_predic_batches, batch_size=100):
    all_predictions = []
    total_batches = len(X_predic_batches)
    
    for i, batch in enumerate(X_predic_batches):
        try:
            batch_predictions = predict_one(manager, batch)
            all_predictions.extend(batch_predictions)
            print(f"Processado lote {i+1}/{total_batches}")
        except Exception as e:
            print(f"Erro no lote {i+1}: {str(e)}")
            all_predictions.extend([None] * len(batch))
    
    return all_predictions