from sqlalchemy import text

def get_student_specific_averages(student_name, discipline, academicperiod):
    query = text("""
    SELECT
        Alunos.CodigoAluno,
        Alunos.NomeAluno,
        Matriculas.SituacaoMatricula,
        PeriodosLetivos.NomePeriodo,
        Cursos.NomeCurso,
        Series.NomeSerie,
        Turmas.ApelidoTurma,
        Disciplinas.NomeDisciplina,
        Etapas.NomeEtapa,
        Medias.ValorMedia
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
        DisciplinasxSeries ON Series.IDSerie = DisciplinasxSeries.IDSerieDisciplinaxSerie
    INNER JOIN
        Disciplinas ON DisciplinasxSeries.IDDisciplinaDisciplinaxSerie = Disciplinas.IDDisciplina
    INNER JOIN
        EtapasxSeries ON Series.IDSerie = EtapasxSeries.IDSerieEtapaxSerie
    INNER JOIN
        Etapas ON EtapasxSeries.IDEtapaEtapaxSerie = Etapas.IDEtapa
    INNER JOIN
        Medias ON Alunos.IDAluno = Medias.IDAlunoMedia AND EtapasxSeries.IDEtapaxSerie = Medias.IDEtapaxSerieMedia AND DisciplinasxSeries.IDDisciplinaxSerie = Medias.IDDisciplinaxSerieMedia
    WHERE
        (Alunos.NomeAluno = :student_name) 
    ORDER BY
        Cursos.NomeCurso,
        Series.NomeSerie,
        Turmas.ApelidoTurma,
        Etapas.OrdemEtapa,
        Disciplinas.NomeDisciplina
    """)
    return query

def get_student_averages():
    query = text("""
    SELECT
        Alunos.CodigoAluno,
        Alunos.NomeAluno,
        Matriculas.SituacaoMatricula,
        PeriodosLetivos.NomePeriodo,
        Cursos.NomeCurso,
        Series.NomeSerie,
        Turmas.ApelidoTurma,
        Disciplinas.NomeDisciplina,
        Etapas.NomeEtapa,
        Medias.ValorMedia
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
        DisciplinasxSeries ON Series.IDSerie = DisciplinasxSeries.IDSerieDisciplinaxSerie
    INNER JOIN
        Disciplinas ON DisciplinasxSeries.IDDisciplinaDisciplinaxSerie = Disciplinas.IDDisciplina
    INNER JOIN
        EtapasxSeries ON Series.IDSerie = EtapasxSeries.IDSerieEtapaxSerie
    INNER JOIN
        Etapas ON EtapasxSeries.IDEtapaEtapaxSerie = Etapas.IDEtapa
    INNER JOIN
        Medias ON Alunos.IDAluno = Medias.IDAlunoMedia AND EtapasxSeries.IDEtapaxSerie = Medias.IDEtapaxSerieMedia AND DisciplinasxSeries.IDDisciplinaxSerie = Medias.IDDisciplinaxSerieMedia
    ORDER BY
        Cursos.NomeCurso,
        Series.NomeSerie,
        Turmas.ApelidoTurma,
        Etapas.OrdemEtapa,
        Disciplinas.NomeDisciplina
    """)
    return query
