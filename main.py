from Class import GraphManager
from Test.ClassificationPCA import classifiers_comparison_pca
from Test.CorrelationAnalysis import correlation_analysis
from setup import verify_dependencies
from DataAccess import create_session
from DataExtraction.Treatment import process_data
from KnotAndEdges.Graph import graphnode
from KnotAndEdges.ConsultNetPy import consult_student_networkx, consult_student_pytorch, draw_graph
from Processing.LSTM import lstm
from Test.ClassificationModel import classifiers_comparison_mf

def main():
    try:
        # Deixe descomentado apenas quando precisar instalar ou verificar se as bibliotecas estão atualizadas.
        # verify_dependencies()
        
        session = create_session("Warley")

        specific = False  # Aluno específico
        academicperiod = "2024"
        student_name = "Ana Cecília Tavares Aleixo"
        idaluno = "1B14A547-1A18-4909-9071-DA3130EAD991"

        manager = GraphManager()

        # Extração dos dados para CSV
        process_data(session, manager, student_name, academicperiod, specific)

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

        '''
        PRÉ-PROCESSAMENTO DOS DADOS
        1 - Processamento dos atributos ✅
        → Preparar os dados brutos para o modelo, convertendo para tensores e separando X (entrada) e y (saída).

        2 - Normalização dos dados ✅
        → Escalar os valores dos atributos para uma mesma faixa, o que acelera o aprendizado.

        3 - Padronização de sequências ✅
        → Ajustar todas as sequências para o mesmo tamanho via padding e, se possível, usar pack_padded_sequence.

        4 - Embeddings ✅
        → Cada categoria vira um vetor denso treinável, permitindo que o modelo aprenda representações mais ricas.

        5 - Enriquecimento de atributos
        → Criar atributos derivados (ex: tendência de nota) que ajudam o modelo a aprender padrões mais profundos.

        
        DEFINIÇÃO DO MODELO
        1 - Primeira camada ✅
        → Camada inicial LSTM que processa sequências temporais dos dados.

        2 - Bidirectional LSTM
        → Torna a LSTM capaz de olhar para frente e para trás na sequência, melhorando o contexto.

        3 - Segunda camada ✅
        → Outra LSTM empilhada ou uma Linear que conecta a saída da LSTM com a próxima etapa.

        3 - Camadas adicionais (Dropout / BatchNorm)
        → Ajudam na regularização e estabilidade durante o treinamento.

        4 - Camada de ativação ✅
        → Aplica função não-linear (ex: ReLU ou Sigmoid) após camadas lineares para modelar relações complexas.

        5 - Attention Mechanism
        → Foca nas partes mais importantes da sequência ao invés de usar apenas o último hidden state.

        6 - Camada de pooling
        → (Opcional) Agrega informações ao longo da sequência, ex: média ou max pooling.

        7 - Custom Output Heads
        → Camadas de saída adaptadas para múltiplos alvos ou tarefas, como prever nota e comportamento.

        8 - Camada de saída ✅
        → Última camada linear que transforma os dados na dimensão da predição desejada.

        
        TREINAMENTO
        1 - Otimizador e a função de perda ✅
        → Define como os erros são calculados e como o modelo é ajustado a cada batch (ex: Adam + MSELoss).

        2 - Função de treinamento ✅
        → Loop que percorre batches, calcula perda, backpropagation e aplica o otimizador.

        3 - Early Stopping
        → Interrompe o treinamento se a validação parar de melhorar, evitando overfitting.

        4 - Scheduler de taxa de aprendizado
        → Ajusta automaticamente o learning rate para melhorar convergência.

        5 - Cross-validation (K-Fold)
        → Técnica de validação cruzada que melhora a avaliação do modelo em datasets pequenos.

        6 - Loop de treinamento e avaliação no final do treinamento
        → Executa o treinamento por várias épocas e avalia no final com métricas específicas.

        7 - Função de avaliação
        → Mede o desempenho do modelo em dados de teste, sem ajustar pesos.
        '''
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if session:
            session.close()

if __name__ == "__main__":
    main()