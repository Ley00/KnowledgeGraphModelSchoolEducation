import pandas as pd
from setup import verify_dependencies
from DataAccess import create_session
from DataExtraction.File import savearchivestudent, filereader
from DataExtraction.Views import get_student, get_student_guardians, get_student_averages,get_paid_student, get_student_absences, get_student_guardians
from DataExtraction.Treatment import studenttreatment, averagetreatment, paymenttreatment, absencestreatment, guardianstreatment
from Preprocessing.Graph import consult_student, graphnode, draw_graph
from Training.GCN import gcn

def main():
    try:
        #Deixe descomentado apenas quando precisar instalar ou verificar se as bibliotecas estão atualizadas.
        #verify_dependencies()
        
        session = create_session("Warley")

        specific = True #Aluno específico
        academicperiod = "2024"
        student_name = "Ana Cecília Tavares Aleixo"
        idaluno = "1B14A547-1A18-4909-9071-DA3130EAD991"
        
        foldercsv = "Result"
        filenames = {
            "student": "aluno.csv",
            "avg": "media_nota_aluno.csv",
            "payment": "pagamento_aluno.csv",
            "absences": "faltas_aluno.csv",
            "guardians": "responsaveis_aluno.csv",
            "networkx_graph": "networkx_graph.graphml",
            "pytorch_graph": "pytorch_graph.pt"
        }

        # Processamento dos dados
        #process_data(session, foldercsv, filenames, student_name, academicperiod, specific)

        #Graph - Pré-Processing
        #Alterar para que todas as colunas sejam passadas
        graphnode(foldercsv, filenames)
        #draw_graph(foldercsv, filenames["networkx_graph"])
        consult_student(foldercsv, filenames["networkx_graph"], idaluno)

        #if specific: info = consult_student(foldercsv, filenames, idaluno)

        #Multi-Layer Perceptron + GCN:
        #Usar MLP + GCN em conjunto é vantajoso quando seus dados incluem tanto informações individuais dos alunos (como notas, faltas e pagamentos) 
        # quanto relações entre eles (como pertencem à mesma turma). O MLP processa as características individuais de forma eficiente, enquanto o GCN 
        # modela as interações e padrões entre alunos, melhorando a generalização e a precisão do modelo. Juntos, eles permitem capturar tanto os aspectos 
        # individuais quanto as relações estruturais entre alunos, proporcionando uma análise mais robusta e capaz de identificar padrões complexos, como as causas de 
        # quedas nas notas ou faltas.

        #Após o GCN gerar as representações dos alunos, você pode passar essas representações por um MLP para fazer previsões mais refinadas, como prever o motivo específico da queda 
        #nas notas (por exemplo, baixa frequência, dificuldades em uma disciplina específica, etc.). O MLP pode atuar como um classificador ou um regressor, dependendo de como você 
        # estrutura o problema.

        #GCN
        #gcn(G, data)

        #Multi-Layer Perceptron
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if session:
            session.close()

def process_data(session, foldercsv, filenames, student_name, academicperiod, specific):
    """Gerencia a extração e tratamento de dados de alunos."""
    try:
        # Processa os alunos
        process_students(session, foldercsv, filenames["student"], student_name, academicperiod, specific)

        # Processa as demais informações (média, pagamento, faltas, responsáveis)
        for key, view_func, treatment_func in [
            ("avg", get_student_averages, averagetreatment),
            ("payment", get_paid_student, paymenttreatment),
            ("absences", get_student_absences, absencestreatment),
            ("guardians", get_student_guardians, guardianstreatment),
        ]:
            process_generic(session, foldercsv, filenames["student"], filenames[key], view_func, treatment_func)

    except Exception as e:
        print(f"Error in process_data: {e}")
        raise

def process_students(session, foldercsv, filename, student_name, academicperiod, specific):
    """Obtém e processa informações dos alunos."""
    try:
        query = get_student(specific, student_name, academicperiod)
        params = {"student_name": student_name, "academicperiod": academicperiod} if student_name or academicperiod else {}
        result = session.execute(query, params)
        
        result_list = studenttreatment(result.keys(), [row for row in result])

        columns = list(result.keys())
        data = pd.DataFrame(result_list, columns=columns)
        savearchivestudent(foldercsv, filename, data)

    except Exception as e:
        print(f"Error in process_students: {e}")
        raise

def process_generic(session, foldercsv, input_file, output_file, view_func, treatment_func):
    """Processa qualquer tipo de informação (média, pagamento, faltas, responsáveis) para evitar repetição de código."""
    try:
        df = filereader(foldercsv, input_file)
        result_list = []

        for _, row in df.iterrows():
            query, params = view_func(row)
            result = session.execute(query, params)
            result_list.extend(result.fetchall())

        processed_data = treatment_func(result.keys(), result_list)
        
        columns = list(result.keys())
        data = pd.DataFrame(processed_data, columns=columns)
        savearchivestudent(foldercsv, output_file, data)

    except Exception as e:
        print(f"Error in process_generic ({output_file}): {e}")
        raise

if __name__ == "__main__":
    main()