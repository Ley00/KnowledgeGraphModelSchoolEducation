from Class import GraphManager
from BDBasic.Test.ClassificationPCA import classifiers_comparison_pca
from BDBasic.Test.CorrelationAnalysis import correlation_analysis
from setup import verify_dependencies
from DataAccess import create_session
from BDBasic.DataExtraction.Treatment import process_data
from BDBasic.DataExtraction.DatabaseMaintenance import prepare_updated_database
from BDBasic.KnotAndEdges.Graph import graphnode
from BDBasic.KnotAndEdges.ConsultNetPy import consult_student_networkx, consult_student_pytorch, draw_graph
from BDBasic.Processing.LSTM import lstm
from BDBasic.Test.ClassificationModel import classifiers_comparison_mf
from BDTreatment.DataExtraction.DataUnderstanding import data_understanding_one
from BDTreatment.DataExtraction.Treatment import process_data_one, check_student_grade_one
from BDTreatment.Processing.RandomForest import random_forest_one
from TCCPipeline import run_full_reporting_pipeline, run_real_pipeline

def main():
    session = None
    try:
        # Deixe descomentado apenas quando precisar instalar ou verificar se as bibliotecas estão atualizadas.
        # verify_dependencies()

        specific = False  # Aluno específico
        academicperiod = "2024"
        student_name = "Ana Cecília Tavares Aleixo"
        idaluno = "1B14A547-1A18-4909-9071-DA3130EAD991"

        manager = GraphManager()

        # Tratamento do banco atualizado
        # Rode apenas quando um novo banco for importado/atualizado.
        # A função tenta renomear o banco importado para COLEGIO_TESTE,
        # remove tabelas inúteis, anonimiza alunos e reorganiza o banco.
        # prepare_updated_database("Warley")

        # BDBASIC
        # Extração dos dados para CSV
        # Requer conexão com o banco:
        # session = create_session("Warley")
        # process_data(session, manager, student_name, academicperiod, specific)

        # Análise de correlação
        # correlation_analysis(manager)

        # Comparação de classificadores
        # classifiers_comparison_mf(manager)

        # Comparação de classificadores com PCA
        # classifiers_comparison_pca(manager)

        # Processa um grafo heterogêneo a partir de dados tabulares CSV
        # graphnode(manager)

        # Visualização e consultas
        # draw_graph(manager)
        # consult_student_networkx(manager, idaluno)
        # consult_student_pytorch(manager, idaluno)

        # Treinamento do modelo LSTM
        # lstm(manager)



        # BDTREATMENT
        # Extração dos dados para CSV
        # process_data_one(manager)
        # check_student_grade_one(manager)
        # data_understanding_one(manager)

        # Pipeline completa orientada ao objetivo do TCC:
        # roda previsão de nota, alerta de risco e gera relatórios finais
        # para professor, coordenação e secretaria.
        run_full_reporting_pipeline(".")

        # Pipeline real refatorada a partir dos CSVs já extraídos
        # Modo focado em previsão numérica da próxima nota
        # run_real_pipeline(".", mode="previsao_nota")

        # Modo focado em alerta pedagógico de risco
        # run_real_pipeline(".", mode="alerta_risco")

        # Fluxo tabular legado
        # random_forest_one(manager)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if session is not None:
            session.close()

if __name__ == "__main__":
    main()
