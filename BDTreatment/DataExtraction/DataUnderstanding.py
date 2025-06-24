import seaborn
from matplotlib import pyplot
from Class import GraphManager
from BDBasic.DataExtraction.File import filereader
import pandas

def data_understanding(manager: GraphManager):
    try:
        output_path = "BDTreatment/Result/TXT/data_understanding_output.txt"
        df = filereader(manager.filename[10])
        # aluno = "Pedro Lucas Ferreira Gomes"
        # df = df[df['NomeAluno'].astype(str).str.strip().str.lower() == aluno.strip().lower()]
        data_understanding_output(df, output_path)
        outliers(df)
        atribute_numeric(df, "Biologia")
        atribute_categorical(df, "Pedro Lucas Ferreira Gomes" , "7º Ano")

    except Exception as e:
        print(f"Error in data_understanding: {e}")
        raise

# Insere os resultados da análise de entendimento dos dados em um arquivo de texto
def data_understanding_output(df, output_path):
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("Tipos de dados das colunas:\n")
            f.write(str(df.dtypes))
            f.write("\n\n")

            value = 10
            f.write(f"Amostra de {value} linhas do DataFrame:\n")
            f.write(str(df.sample(value)))
            f.write("\n\n")

            f.write(f"O dataset contém {df.shape[0]} instâncias e {df.shape[1]} atributos.\n\n")

            f.write("Resumo estatístico do DataFrame:\n")
            f.write(str(df.describe()))
            f.write("\n\n")

            f.write("Presença de valores nulos por coluna:\n")
            f.write(str(df.isnull().sum()))
            f.write("\n\n")

            f.write("Porcentagem de valores nulos por coluna:\n")
            f.write(str((df.isnull().sum() / len(df) * 100).round(2)))
            f.write("\n\n")
    except Exception as e:
        print(f"Error in data_understanding_output: {e}")
        raise

# Visualizar presença de outliers (valores fora do intervalo [0, 10])
def outliers(df):
    try:
        nota_columns = [col for col in df.columns if col != 'NomeAluno']
        invalid_percentages = {}

        for feature in nota_columns:
            df[feature] = pandas.to_numeric(df[feature], errors='coerce')

            series = df[feature].dropna()
            if series.empty:
                continue

            invalid = series[(series < 0) | (series > 10)]
            percent = (len(invalid) / len(series)) * 100
            invalid_percentages[feature] = percent

        invalid_percentages = {k: v for k, v in invalid_percentages.items() if v > 0}

        if invalid_percentages:
            pyplot.figure(figsize=(10, 6))
            seaborn.barplot(
                x=list(invalid_percentages.keys()),
                y=list(invalid_percentages.values()),
                palette="Reds_r"
            )
            pyplot.ylabel("Porcentagem de Valores Inválidos (%)")
            pyplot.xlabel("Coluna")
            pyplot.title("Porcentagem de Valores < 0 ou > 10 por Coluna")
            pyplot.xticks(rotation=45, ha='right')
            pyplot.tight_layout()
            pyplot.show()
        else:
            print("Nenhum valor fora do intervalo [0, 10] encontrado nas colunas analisadas.")

    except Exception as e:
        print(f"Error in atribute_numeric: {e}")
        raise

# Visualizar atributos numéricos de um determinada disciplina
def atribute_numeric(df, subject):
    try:
        subject_cols = [col for col in df.columns if subject in col]
        if not subject_cols:
            print("Nenhuma coluna encontrada para o subject informado.")
            return

        df_subject = df[subject_cols].apply(pandas.to_numeric, errors='coerce')

        numeric_columns = df_subject.select_dtypes(include=['number']).columns.tolist()
        if not numeric_columns:
            print("Nenhum atributo numérico encontrado.")
            return

        pyplot.figure(figsize=(12, 6))
        seaborn.boxplot(data=df_subject[numeric_columns])
        pyplot.title("Boxplot dos Atributos Numéricos")
        pyplot.xticks(rotation=45)
        pyplot.tight_layout()
        pyplot.show()

    except Exception as e:
        print(f"Error in atribute_numeric: {e}")
        raise

# Visualizar atributos categóricos
def atribute_categorical(df, studant, serie):
    try:
        df = df[df['NomeAluno'].astype(str).str.strip().str.lower() == studant.strip().lower()]
        serie_cols = [col for col in df.columns if serie.strip().lower() in col.strip().lower()]
        if not serie_cols:
            print("Nenhuma coluna encontrada para a série informada.")
            return

        disciplinas = {}
        for col in serie_cols:
            partes = col.split('_')
            if len(partes) >= 2:
                nome_disciplina = partes[1].strip()
                if nome_disciplina not in disciplinas:
                    disciplinas[nome_disciplina] = []
                disciplinas[nome_disciplina].append(col)

        plot_data = []
        for disciplina, cols in disciplinas.items():
            notas = df[cols].apply(pandas.to_numeric, errors='coerce').values.flatten()
            for nota in notas:
                if not pandas.isna(nota):
                    plot_data.append({"Disciplina": disciplina, "Nota": nota})

        plot_df = pandas.DataFrame(plot_data)

        if plot_df.empty:
            print("Não há dados para plotar a distribuição.")
            return

        pyplot.figure(figsize=(10, 6))
        seaborn.boxplot(
            data=plot_df,
            x="Disciplina",
            y="Nota",
            hue="Disciplina",
            palette="viridis",
            legend=False
        )
        pyplot.title(f"Distribuição das Notas das Disciplinas para {serie} ({studant})")
        pyplot.xlabel("Disciplina")
        pyplot.ylabel("Notas")
        pyplot.ylim(0, 10)
        pyplot.xticks(rotation=45, ha='right')
        pyplot.tight_layout()
        pyplot.show()

    except Exception as e:
        print(f"Error in atribute_categorical: {e}")
        raise