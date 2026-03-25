import numpy
import pandas
import re
from sklearn.calibration import LabelEncoder

def preprocess_data_one(df, manager):
    etapa_regex = re.compile(r"(.+)_(\d+º)\s+([BT]IMESTRE)", re.IGNORECASE)
    
    etapas = []
    disciplina_etapas = {}
    
    for col in df.columns:
        m = etapa_regex.search(col)
        if m:
            etapas.append(col)
            disciplina = m.group(1)
            numero_etapa = m.group(2)
            tipo_etapa = m.group(3).upper()
            etapa_completa = f"{numero_etapa} {tipo_etapa}"
            
            if disciplina not in disciplina_etapas:
                disciplina_etapas[disciplina] = []
            disciplina_etapas[disciplina].append((col, etapa_completa, numero_etapa, tipo_etapa))

    previsao_cols = []
    
    for disciplina, cols in disciplina_etapas.items():
        if not cols:
            continue
            
        tipo_sistema = cols[0][3]
        
        if tipo_sistema == "BIMESTRE":
            etapa_final_numero = "4º"
            etapas_anteriores_numeros = ["1º", "2º", "3º"]
        else:
            etapa_final_numero = "3º"
            etapas_anteriores_numeros = ["1º", "2º"]
        
        col_final = None
        cols_anteriores = []
        
        for col, etapa_completa, numero, tipo in cols:
            if numero == etapa_final_numero:
                col_final = col
            elif numero in etapas_anteriores_numeros:
                cols_anteriores.append(col)
        
        if col_final and cols_anteriores:
            cols_anteriores.sort(key=lambda x: next(
                (numero for col, _, numero, _ in cols if col == x), "0º"
            ))
            
            previsao_cols.append({
                "disciplina": disciplina,
                "etapas_anteriores": cols_anteriores,
                "etapa_final": col_final,
                "tipo_sistema": tipo_sistema
            })

    def safe_classify(value):
        try:
            if pandas.notnull(value):
                return manager.classify_grade(float(value))
        except (ValueError, TypeError):
            pass
        return None
    
    class_dataframes = []
    for col in etapas:
        class_df = pandas.DataFrame({
            col + "_class": df[col].apply(safe_classify)
        })
        class_dataframes.append(class_df)
    
    if class_dataframes:
        class_data_df = pandas.concat(class_dataframes, axis=1)
        df = pandas.concat([df, class_data_df], axis=1)

    return df, etapas, previsao_cols

def split_features_targets_one(df, etapas, previsao_cols):
    if not previsao_cols:
        return [], []
    
    max_len = max(len(item["etapas_anteriores"]) for item in previsao_cols)
    X = []
    y = []
    
    for item in previsao_cols:
        cols_anteriores = item["etapas_anteriores"]
        col_final = item["etapa_final"]
        
        cols_anteriores_class = [c + "_class" for c in cols_anteriores]
        col_final_class = col_final + "_class"
        
        required_cols = cols_anteriores + [col_final] + cols_anteriores_class + [col_final_class]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            continue
        
        valid_mask = (
            df[cols_anteriores + [col_final]].notnull().all(axis=1) &
            df[cols_anteriores_class + [col_final_class]].notnull().all(axis=1)
        )
        
        valid_df = df[valid_mask]
        if valid_df.empty:
            continue
        
        features_df = valid_df[cols_anteriores_class]
        targets = valid_df[col_final_class].tolist()
        
        for _, row in features_df.iterrows():
            features = row.tolist() + [None] * (max_len - len(row))
            X.append(features)
        
        y.extend(targets)
    return X, y

def encode_features_target_one(X, y):
    if not X or not y:
        raise ValueError("X e y não podem estar vazios")
    
    if len(X) != len(y):
        raise ValueError("X e y devem ter o mesmo número de amostras")
    
    X = numpy.array(X, dtype=object)
    y = numpy.array(y, dtype=object)
    
    def safe_str_convert(val):
        if val is None or (isinstance(val, float) and numpy.isnan(val)):
            return "MISSING"
        return str(val)
    
    X_str = numpy.array([[safe_str_convert(val) for val in row] for row in X])
    y_str = numpy.array([safe_str_convert(val) for val in y])
    
    if X_str.size == 0 or y_str.size == 0:
        raise ValueError("Dados insuficientes para encoding")
    
    le_X = []
    X_encoded = numpy.zeros_like(X_str, dtype=int)
    
    for i in range(X_str.shape[1]):
        le = LabelEncoder()
        try:
            X_encoded[:, i] = le.fit_transform(X_str[:, i])
            le_X.append(le)
        except Exception as e:
            raise ValueError(f"Erro ao codificar coluna {i}: {str(e)}")
    
    le_y = LabelEncoder()
    try:
        y_encoded = le_y.fit_transform(y_str)
    except Exception as e:
        raise ValueError(f"Erro ao codificar target: {str(e)}")
    
    if X_encoded.shape[0] != y_encoded.shape[0]:
        raise ValueError("Inconsistência nos dados após encoding")
    
    return X_encoded, y_encoded, le_X, le_y