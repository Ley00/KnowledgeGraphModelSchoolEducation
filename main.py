from DataAccess import create_session
from Preprocessing.Views.AverageGrade import get_student_specific_averages
from Preprocessing.Views.AverageGrade import get_student_averages
from Preprocessing.Views.Payment import get_paid_student_especific
from Preprocessing.Views.Payment import get_paid_student
from Preprocessing.CSV import savearchiveaverage
from Preprocessing.CSV import savearchivepay
import os

def main():
    try:
        session = create_session()
        
        student_name = "Ana Cecília Tavares Aleixo"
        discipline = "Arte"
        academicperiod = "2023"
        
        #Name Archive CSV
        namecsv = ["media_nota_aluno.csv", "pagamento_aluno.csv"]
        
        #Delete Archive CSV
        deleteoldcsv(namecsv)
        
        #Média dos alunos
        avg(session, namecsv[0], student_name, discipline, academicperiod)
        
        #Pagamento dos alunos
        payment(session, namecsv[1], student_name, academicperiod)
        
    except Exception as e:
        print("Error:", e)
    finally:
        if session:
            session.close()

def avg(session, namecsv, student_name, discipline, academicperiod):
    try:
        # Specific Student
        query = get_student_specific_averages(student_name, discipline, academicperiod)
        result = session.execute(query, {"student_name": student_name, "discipline": discipline, "academicperiod": academicperiod})

        # All Students
        #query = get_student_averages()
        #result = session.execute(query)

        # Adds each query result to the list
        result_list = [resultads for resultads in result]

        savearchiveaverage(result_list, namecsv)
        
    except Exception as e:
        print("Error in avg function:", e)
        
def payment(session, namecsv, student_name, academicperiod):
    try:
        # Specific Student
        query = get_paid_student_especific(student_name, academicperiod)
        result = session.execute(query, {"student_name": student_name, "academicperiod": academicperiod})

        # All Students
        #query = get_paid_student()
        #result = session.execute(query)

        # Adds each query result to the list
        result_list = [resultads for resultads in result]

        savearchivepay(result_list, namecsv)
        
    except Exception as e:
        print("Error in payment function:", e)
        
def deleteoldcsv(namecsv):
    try:
        for filename in namecsv:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"Arquivo '{filename}' excluído com sucesso.")
            else:
                print(f"Arquivo '{filename}' não encontrado.")
    except Exception as e:
        print(f"Erro ao excluir arquivo: {e}")

if __name__ == "__main__":
    main()
