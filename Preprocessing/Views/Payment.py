from sqlalchemy import text

def get_paid_student_especific(student_name, academicperiod):
    query = text("""
    SELECT        
        Alunos.CodigoAluno, 
        Alunos.NomeAluno, 
        Matriculas.SituacaoMatricula, 
        PeriodosLetivos.NomePeriodo, 
        Cursos.NomeCurso, 
        Series.NomeSerie, 
        Turmas.ApelidoTurma, 
        Movimentos.ParcelaMovimento, 
        Movimentos.DescricaoMovimento, 
        Movimentos.DataAntecipadoMovimento, 
        Movimentos.ValorAntecipadoMovimento, 
        Movimentos.DataVencimentoMovimento, 
        Movimentos.ValorMovimento, 
        Movimentos.PagoMovimento
    FROM            
        PeriodosLetivos 
    INNER JOIN
        CursosxPeriodos ON PeriodosLetivos.IDPeriodo = CursosxPeriodos.IDPeriodoCursoxPeriodo 
    INNER JOIN
        Cursos ON CursosxPeriodos.IDCursoCursoxPeriodo = Cursos.IDCurso 
    INNER JOIN
        Series ON CursosxPeriodos.IDCursoxPeriodo = Series.IDCursoxPeriodoSerie 
    INNER JOIN
        Turmas ON Series.IDSerie = Turmas.IDSerieTurma 
    INNER JOIN
        Alunos 
    INNER JOIN
        Matriculas ON Alunos.IDAluno = Matriculas.IDAlunoMatricula ON Turmas.IDTurma = Matriculas.IDTurmaMatricula 
    INNER JOIN
        Movimentos ON Matriculas.IDMatricula = Movimentos.IDMatriculaMovimento
    WHERE        
        (Alunos.NomeAluno = :student_name) 
        AND (PeriodosLetivos.NomePeriodo = :academicperiod) 
    ORDER BY 
        Cursos.NomeCurso, 
        Series.NomeSerie, 
        Turmas.ApelidoTurma, 
        Alunos.NomeAluno, 
        Movimentos.ParcelaMovimento
    """)
    return query

def get_paid_student():
    query = text("""
    SELECT        
        Alunos.CodigoAluno, 
        Alunos.NomeAluno, 
        Matriculas.SituacaoMatricula, 
        PeriodosLetivos.NomePeriodo, 
        Cursos.NomeCurso, 
        Series.NomeSerie, 
        Turmas.ApelidoTurma, 
        Movimentos.ParcelaMovimento, 
        Movimentos.DescricaoMovimento, 
        Movimentos.DataAntecipadoMovimento, 
        Movimentos.ValorAntecipadoMovimento, 
        Movimentos.DataVencimentoMovimento, 
        Movimentos.ValorMovimento, 
        Movimentos.PagoMovimento
    FROM            
        PeriodosLetivos 
    INNER JOIN
        CursosxPeriodos ON PeriodosLetivos.IDPeriodo = CursosxPeriodos.IDPeriodoCursoxPeriodo 
    INNER JOIN
        Cursos ON CursosxPeriodos.IDCursoCursoxPeriodo = Cursos.IDCurso 
    INNER JOIN
        Series ON CursosxPeriodos.IDCursoxPeriodo = Series.IDCursoxPeriodoSerie 
    INNER JOIN
        Turmas ON Series.IDSerie = Turmas.IDSerieTurma 
    INNER JOIN
        Alunos 
    INNER JOIN
        Matriculas ON Alunos.IDAluno = Matriculas.IDAlunoMatricula ON Turmas.IDTurma = Matriculas.IDTurmaMatricula 
    INNER JOIN
        Movimentos ON Matriculas.IDMatricula = Movimentos.IDMatriculaMovimento
    ORDER BY 
        Cursos.NomeCurso, 
        Series.NomeSerie, 
        Turmas.ApelidoTurma, 
        Alunos.NomeAluno, 
        Movimentos.ParcelaMovimento
    """)
    return query
