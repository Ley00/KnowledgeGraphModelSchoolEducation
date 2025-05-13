import re
from sqlalchemy import text

#Consulta para buscar alunos
def get_student(has_where, student_name=None, academicperiod=None):
    query = """
    SELECT
        Unidades.IDUnidade,
        Unidades.NomeUnidade,
        UnidadesxTiposCursos.IDUnidadexTipoCurso,
        Cursos.IDCurso,
        Cursos.NomeCurso,
        PeriodosLetivos.IDPeriodo,
        PeriodosLetivos.NomePeriodo,
        CursosxPeriodos.IDCursoxPeriodo,
        Series.IDSerie,
        Series.NomeSerie,
        Turmas.IDTurma,
        Turmas.ApelidoTurma,
        Matriculas.IDMatricula,
        Matriculas.SituacaoMatricula,
        Matriculas.DataMatricula,
        Alunos.IDAluno,
        Alunos.CodigoAluno,
        Alunos.NomeAluno,
        Alunos.SexoAluno,
        Alunos.DataNascimentoAluno,
        Alunos.QuadraResidenciaAluno,
        Alunos.LoteResidenciaAluno,
        Alunos.NumeroResidenciaAluno,
        Alunos.ComplementoResidenciaAluno,
        Alunos.BairroResidenciaAluno,
        Alunos.CEPResidenciaAluno
    FROM
        CursosxPeriodos
    INNER JOIN
        Cursos ON CursosxPeriodos.IDCursoCursoxPeriodo = Cursos.IDCurso
    INNER JOIN
        PeriodosLetivos ON CursosxPeriodos.IDPeriodoCursoxPeriodo = PeriodosLetivos.IDPeriodo
    INNER JOIN
        Series ON CursosxPeriodos.IDCursoxPeriodo = Series.IDCursoxPeriodoSerie
    INNER JOIN
        Turmas ON Series.IDSerie = Turmas.IDSerieTurma
    INNER JOIN
        Matriculas ON Turmas.IDTurma = Matriculas.IDTurmaMatricula
    INNER JOIN
        Alunos ON Matriculas.IDAlunoMatricula = Alunos.IDAluno
    INNER JOIN
        Unidades
    INNER JOIN
        UnidadesxTiposCursos ON Unidades.IDUnidade = UnidadesxTiposCursos.IDUnidadeUnidadexTipoCurso ON Cursos.IDUnidadexTipoCursoCurso = UnidadesxTiposCursos.IDUnidadexTipoCurso
    """
    
    if has_where:
        query += " WHERE 1=1"
        if student_name:
            query += " AND Alunos.NomeAluno = :student_name"
        if academicperiod:
            query += " AND PeriodosLetivos.NomePeriodo = :academicperiod"
    
    query += """
    ORDER BY
        Unidades.NomeUnidade,
        Cursos.NomeCurso,
        PeriodosLetivos.NomePeriodo,
        Series.NomeSerie,
        Turmas.ApelidoTurma,
        Alunos.NomeAluno
    """
    
    return text(query)

#Consulta para buscar o pagamento
def get_paid_student(row):
    query = """
    SELECT
        :IDUnidade AS IDUnidade,
        :NomeUnidade AS NomeUnidade,
        :IDPeriodo AS IDPeriodo,
        :NomePeriodo AS NomePeriodo,
        :IDCurso AS IDCurso,
        :NomeCurso AS NomeCurso,
        :IDSerie AS IDSerie,
        :NomeSerie AS NomeSerie,
        :IDTurma AS IDTurma,
        :ApelidoTurma AS ApelidoTurma,
        :IDMatricula AS IDMatricula,
        :SituacaoMatricula AS SituacaoMatricula,
        :IDAluno AS IDAluno,
        :NomeAluno AS NomeAluno,
        IDMovimento,
        IDMatriculaMovimento,
        ParcelaMovimento,
        DescricaoMovimento,
        DataAntecipadoMovimento,
        ValorAntecipadoMovimento,
        DataVencimentoMovimento,
        ValorMovimento,
        PagoMovimento,
        ValorPagoMovimento,
        EhMensalidadeMovimento,
        EhMatriculaMovimento
    FROM
        Movimentos
    WHERE
        Movimentos.IDMatriculaMovimento = :IDMatricula
    ORDER BY
        Movimentos.ParcelaMovimento
    """

    placeholders = set(re.findall(r":(\w+)", query))
    params = {col: row[col] for col in placeholders if col in row}

    return text(query), params

#Consulta para buscar os responsáveis
def get_student_guardians(row):
    query = """
    SELECT
        :IDUnidade AS IDUnidade,
        :NomeUnidade AS NomeUnidade,
        :IDPeriodo AS IDPeriodo,
        :NomePeriodo AS NomePeriodo,
        :IDCurso AS IDCurso,
        :NomeCurso AS NomeCurso,
        :IDSerie AS IDSerie,
        :NomeSerie AS NomeSerie,
        :IDTurma AS IDTurma,
        :ApelidoTurma AS ApelidoTurma,
        :IDMatricula AS IDMatricula,
        :SituacaoMatricula AS SituacaoMatricula,
        :IDAluno AS IDAluno,
        :NomeAluno AS NomeAluno,
        Responsaveis.IDResponsavel,
        AlunosxResponsaveis.TipoResponsavel,
        Responsaveis.NomeResponsavel,
        Responsaveis.SexoResponsavel,
        Responsaveis.DataNascimentoResponsavel,
        Responsaveis.LogradouroResidenciaResponsavel,
        Responsaveis.QuadraResidenciaResponsavel,
        Responsaveis.LoteResidenciaResponsavel,
        Responsaveis.NumeroResidenciaResponsavel,
        Responsaveis.ComplementoResidenciaResponsavel,
        Responsaveis.BairroResidenciaResponsavel,
        Responsaveis.CEPResidenciaResponsavel
    FROM
        Responsaveis
    INNER JOIN
        AlunosxResponsaveis ON :IDAluno = AlunosxResponsaveis.IDAlunoAlunoxResponsavel
        AND AlunosxResponsaveis.IDResponsavelAlunoxResponsavel = Responsaveis.IDResponsavel
    ORDER BY
        Responsaveis.NomeResponsavel
    """

    placeholders = set(re.findall(r":(\w+)", query))
    params = {col: row[col] for col in placeholders if col in row}

    return text(query), params

#Consulta para buscar as médias
def get_student_averages(row):
    query = """
    SELECT
        :IDUnidade AS IDUnidade,
        :NomeUnidade AS NomeUnidade,
        :IDPeriodo AS IDPeriodo,
        :NomePeriodo AS NomePeriodo,
        :IDCurso AS IDCurso,
        :NomeCurso AS NomeCurso,
        :IDSerie AS IDSerie,
        :NomeSerie AS NomeSerie,
        :IDTurma AS IDTurma,
        :ApelidoTurma AS ApelidoTurma,
        :IDMatricula AS IDMatricula,
        :SituacaoMatricula AS SituacaoMatricula,
        :IDAluno AS IDAluno,
        :NomeAluno AS NomeAluno,
        Disciplinas.IDDisciplina,
        Disciplinas.NomeDisciplina,
        Etapas.IDEtapa,
        Etapas.NomeEtapa,
        Medias.IDMedia,
        Medias.ValorMedia
    FROM
        Medias
    INNER JOIN
        EtapasxSeries ON Medias.IDEtapaxSerieMedia = EtapasxSeries.IDEtapaxSerie
        AND EtapasxSeries.IDSerieEtapaxSerie = :IDSerie
    INNER JOIN
        Etapas ON EtapasxSeries.IDEtapaEtapaxSerie = Etapas.IDEtapa
    INNER JOIN
        MatriculasxDiciplinas ON MatriculasxDiciplinas.IDMatriculaMatriculaxDisciplina = :IDMatricula
        AND MatriculasxDiciplinas.IDTurmaMatriculaxDisciplina = :IDTurma
    INNER JOIN
        DisciplinasxSeries ON MatriculasxDiciplinas.IDDisciplinaxSerieMatriculaxDisciplina = DisciplinasxSeries.IDDisciplinaxSerie
        AND DisciplinasxSeries.IDSerieDisciplinaxSerie = :IDSerie
    INNER JOIN
        Disciplinas ON DisciplinasxSeries.IDDisciplinaDisciplinaxSerie = Disciplinas.IDDisciplina
        AND Medias.IDDisciplinaxSerieMedia = DisciplinasxSeries.IDDisciplinaxSerie
    WHERE
        Medias.IDAlunoMedia = :IDAluno
    ORDER BY 
        Disciplinas.NomeDisciplina,
        Etapas.OrdemEtapa
    """

    placeholders = set(re.findall(r":(\w+)", query))
    params = {col: row[col] for col in placeholders if col in row}

    return text(query), params

#Consulta para buscar as faltas
def get_student_absences(row):
    query = """
    SELECT
        :IDUnidade AS IDUnidade,
        :NomeUnidade AS NomeUnidade,
        :IDPeriodo AS IDPeriodo,
        :NomePeriodo AS NomePeriodo,
        :IDCurso AS IDCurso,
        :NomeCurso AS NomeCurso,
        :IDSerie AS IDSerie,
        :NomeSerie AS NomeSerie,
        :IDTurma AS IDTurma,
        :ApelidoTurma AS ApelidoTurma,
        :IDMatricula AS IDMatricula,
        :SituacaoMatricula AS SituacaoMatricula,
        :IDAluno AS IDAluno,
        :NomeAluno AS NomeAluno,
        DisciplinasxSeries.IDDisciplinaxSerie,
        Disciplinas.IDDisciplina,
        Disciplinas.NomeDisciplina,
        EtapasxSeries.IDEtapaxSerie,
        Etapas.IDEtapa,
        Etapas.NomeEtapa,
        Faltas.IDFalta,
        Faltas.DataFalta
    FROM
        Faltas
    INNER JOIN
        EtapasxSeries ON EtapasxSeries.IDSerieEtapaxSerie = :IDSerie
        AND EtapasxSeries.IDEtapaxSerie = Faltas.IDEtapaxSerieFalta
    INNER JOIN
        Etapas ON EtapasxSeries.IDEtapaEtapaxSerie = Etapas.IDEtapa
    INNER JOIN
        MatriculasxDiciplinas ON MatriculasxDiciplinas.IDMatriculaMatriculaxDisciplina = :IDMatricula
        AND MatriculasxDiciplinas.IDTurmaMatriculaxDisciplina = :IDTurma
    INNER JOIN
        DisciplinasxSeries ON MatriculasxDiciplinas.IDDisciplinaxSerieMatriculaxDisciplina = DisciplinasxSeries.IDDisciplinaxSerie
        AND DisciplinasxSeries.IDSerieDisciplinaxSerie = :IDSerie
        AND DisciplinasxSeries.IDDisciplinaxSerie = Faltas.IDDisciplinaxSerieFalta
    INNER JOIN
        Disciplinas ON DisciplinasxSeries.IDDisciplinaDisciplinaxSerie = Disciplinas.IDDisciplina
    WHERE
        Faltas.IDMatriculaFalta = :IDMatricula
    ORDER BY 
        Disciplinas.NomeDisciplina,
        Etapas.OrdemEtapa,
        Faltas.DataFalta
    """

    placeholders = set(re.findall(r":(\w+)", query))
    params = {col: row[col] for col in placeholders if col in row}

    return text(query), params