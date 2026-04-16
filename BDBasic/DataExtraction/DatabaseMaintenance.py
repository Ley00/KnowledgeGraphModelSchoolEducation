from __future__ import annotations

from sqlalchemy import text

from DataAccess import create_engine, get_connection_params


KEEP_TABLES = [
    "MovimentosxAlunos", "Cartoes", "SubGruposFinanceiros", "MovimentosxResponsaveis",
    "Fornecedores", "Funcionarios", "PeriodosLetivos", "TiposCursos", "TiposNotas",
    "TiposNotasxDisciplinasxEtapas", "Cidades", "Alunos", "AlunosxResponsaveis", "Turmas",
    "Predios", "GruposFinanceiros", "FaltasDia", "Turnos", "UFs", "Unidades",
    "UnidadesxTiposCursos", "FuncionariosxUnidades", "DisciplinasxFuncionarios",
    "Programacoes", "Usuarios", "UsuariosWebApi", "Historicos",
    "Cursos", "CursosxPeriodos", "CursosxTurnos", "DiarioMatricula", "Baixas",
    "Diarios", "BaixasxMovimentos", "DiarioTurmas", "Bancos", "Religioes", "Disciplinas",
    "Responsaveis", "ResponsaveisxMatriculas", "Matriculas", "Resultados",
    "DisciplinasxSeries", "MatriculasxDiciplinas", "Empresas", "Salas", "Series",
    "Medias", "EscolasOutras", "EstadosCivis", "CaixasContas", "Etapas", "EtapasxSeries",
    "Movimentos", "Faltas",
]


DATABASE_PREPARATION_SQL = """
SET NOCOUNT ON;
DECLARE @DatabaseName SYSNAME = DB_NAME();

DECLARE @KeepTables TABLE (Tabela SYSNAME COLLATE DATABASE_DEFAULT PRIMARY KEY);

INSERT INTO @KeepTables (Tabela)
VALUES
{keep_values};

DECLARE @Sql NVARCHAR(MAX);

DECLARE ViewCursor CURSOR LOCAL FAST_FORWARD FOR
SELECT QUOTENAME(SCHEMA_NAME(schema_id)) + '.' + QUOTENAME(name)
FROM sys.views;

DECLARE @ViewName NVARCHAR(258);
OPEN ViewCursor;
FETCH NEXT FROM ViewCursor INTO @ViewName;

WHILE @@FETCH_STATUS = 0
BEGIN
    SET @Sql = N'DROP VIEW ' + @ViewName;
    EXEC sp_executesql @Sql;
    FETCH NEXT FROM ViewCursor INTO @ViewName;
END;

CLOSE ViewCursor;
DEALLOCATE ViewCursor;

DECLARE @HasWork BIT = 1;
WHILE @HasWork = 1
BEGIN
    SET @HasWork = 0;

    DECLARE FkCursor CURSOR LOCAL FAST_FORWARD FOR
    SELECT
        QUOTENAME(SCHEMA_NAME(pt.schema_id)) + '.' + QUOTENAME(pt.name) AS ParentTable,
        QUOTENAME(fk.name) AS ForeignKeyName
    FROM sys.foreign_keys fk
    INNER JOIN sys.tables pt ON fk.parent_object_id = pt.object_id
    INNER JOIN sys.tables rt ON fk.referenced_object_id = rt.object_id
    WHERE pt.name COLLATE DATABASE_DEFAULT NOT IN (SELECT Tabela FROM @KeepTables)
       OR rt.name COLLATE DATABASE_DEFAULT NOT IN (SELECT Tabela FROM @KeepTables);

    DECLARE @ParentTable NVARCHAR(258);
    DECLARE @ForeignKeyName NVARCHAR(258);

    OPEN FkCursor;
    FETCH NEXT FROM FkCursor INTO @ParentTable, @ForeignKeyName;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        SET @Sql = N'ALTER TABLE ' + @ParentTable + N' DROP CONSTRAINT ' + @ForeignKeyName;
        EXEC sp_executesql @Sql;
        SET @HasWork = 1;
        FETCH NEXT FROM FkCursor INTO @ParentTable, @ForeignKeyName;
    END;

    CLOSE FkCursor;
    DEALLOCATE FkCursor;

    DECLARE TriggerCursor CURSOR LOCAL FAST_FORWARD FOR
    SELECT
        QUOTENAME(SCHEMA_NAME(tbl.schema_id)) + '.' + QUOTENAME(trg.name) AS TriggerName
    FROM sys.triggers trg
    INNER JOIN sys.tables tbl ON trg.parent_id = tbl.object_id
    WHERE trg.parent_class_desc = 'OBJECT_OR_COLUMN';

    DECLARE @TriggerName NVARCHAR(258);

    OPEN TriggerCursor;
    FETCH NEXT FROM TriggerCursor INTO @TriggerName;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        SET @Sql = N'DROP TRIGGER ' + @TriggerName;
        EXEC sp_executesql @Sql;
        SET @HasWork = 1;
        FETCH NEXT FROM TriggerCursor INTO @TriggerName;
    END;

    CLOSE TriggerCursor;
    DEALLOCATE TriggerCursor;

    DECLARE TableCursor CURSOR LOCAL FAST_FORWARD FOR
    SELECT QUOTENAME(SCHEMA_NAME(schema_id)) + '.' + QUOTENAME(name) AS TableName
    FROM sys.tables
    WHERE name COLLATE DATABASE_DEFAULT NOT IN (SELECT Tabela FROM @KeepTables);

    DECLARE @TableName NVARCHAR(258);

    OPEN TableCursor;
    FETCH NEXT FROM TableCursor INTO @TableName;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        BEGIN TRY
            SET @Sql = N'DROP TABLE ' + @TableName;
            EXEC sp_executesql @Sql;
            SET @HasWork = 1;
        END TRY
        BEGIN CATCH
        END CATCH;

        FETCH NEXT FROM TableCursor INTO @TableName;
    END;

    CLOSE TableCursor;
    DEALLOCATE TableCursor;
END;

;WITH OrderedStudents AS (
    SELECT
        IDAluno,
        ROW_NUMBER() OVER (ORDER BY IDAluno) AS RowNumber
    FROM Alunos
)
UPDATE Alunos
SET
    NomeAluno = CONCAT('Aluno ', RIGHT(CONCAT('00000', OrderedStudents.RowNumber), 5)),
    CodigoAluno = OrderedStudents.RowNumber,
    DataNascimentoAluno = CASE
        WHEN Alunos.DataNascimentoAluno IS NULL THEN NULL
        ELSE DATEFROMPARTS(YEAR(Alunos.DataNascimentoAluno), 6, 15)
    END,
    QuadraResidenciaAluno = NULL,
    LoteResidenciaAluno = NULL,
    NumeroResidenciaAluno = NULL,
    ComplementoResidenciaAluno = NULL,
    BairroResidenciaAluno = 'Bairro Anonimizado',
    CEPResidenciaAluno = NULL
FROM Alunos
INNER JOIN OrderedStudents ON OrderedStudents.IDAluno = Alunos.IDAluno;

DECLARE @LogFileName SYSNAME;
SELECT @LogFileName = name
FROM sys.database_files
WHERE type_desc = 'LOG';

IF @LogFileName IS NOT NULL
BEGIN
    SET @Sql = N'DBCC SHRINKFILE (' + QUOTENAME(@LogFileName) + N', 1)';
    EXEC sp_executesql @Sql;
END;

SET @Sql = N'DBCC SHRINKDATABASE (' + QUOTENAME(@DatabaseName) + N', 10)';
EXEC sp_executesql @Sql;

DECLARE IndexCursor CURSOR LOCAL FAST_FORWARD FOR
SELECT QUOTENAME(SCHEMA_NAME(schema_id)) + '.' + QUOTENAME(name)
FROM sys.tables
WHERE name COLLATE DATABASE_DEFAULT IN (SELECT Tabela FROM @KeepTables);

DECLARE @IndexTable NVARCHAR(258);
OPEN IndexCursor;
FETCH NEXT FROM IndexCursor INTO @IndexTable;

WHILE @@FETCH_STATUS = 0
BEGIN
    SET @Sql = N'ALTER INDEX ALL ON ' + @IndexTable + N' REORGANIZE';
    BEGIN TRY
        EXEC sp_executesql @Sql;
    END TRY
    BEGIN CATCH
    END CATCH;

    FETCH NEXT FROM IndexCursor INTO @IndexTable;
END;

CLOSE IndexCursor;
DEALLOCATE IndexCursor;

EXEC sp_updatestats;
"""


def _keep_values_sql() -> str:
    return ",\n".join(f"('{table}')" for table in KEEP_TABLES)


def _build_preparation_sql() -> str:
    return DATABASE_PREPARATION_SQL.format(keep_values=_keep_values_sql())


def detect_source_database(user: str, target_database: str) -> str | None:
    engine = create_engine(user, database_override="master")
    query = text(
        """
        SELECT name
        FROM sys.databases
        WHERE name NOT IN ('master', 'tempdb', 'model', 'msdb', :target_database)
          AND state_desc = 'ONLINE'
        ORDER BY create_date DESC, name
        """
    )
    with engine.connect() as connection:
        databases = [row[0] for row in connection.execute(query, {"target_database": target_database})]

    if not databases:
        return None
    if len(databases) == 1:
        return databases[0]
    raise RuntimeError(
        "Não foi possível detectar automaticamente o banco atualizado. "
        f"Encontrados múltiplos bancos candidatos: {databases}"
    )


def rename_database_to_target(user: str, source_database: str, target_database: str) -> None:
    if source_database == target_database:
        return

    engine = create_engine(user, database_override="master")
    rename_sql = f"""
    IF DB_ID(N'{target_database}') IS NOT NULL
        THROW 50001, 'O banco de destino já existe e impede a renomeação.', 1;

    ALTER DATABASE [{source_database}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    ALTER DATABASE [{source_database}] MODIFY NAME = [{target_database}];
    ALTER DATABASE [{target_database}] SET MULTI_USER;
    """
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
        connection.execute(text(rename_sql))


def prepare_updated_database(user: str = "Warley", source_database: str | None = None) -> str:
    target_database = get_connection_params(user)["database"]
    chosen_source = source_database or detect_source_database(user, target_database) or target_database

    rename_database_to_target(user, chosen_source, target_database)

    engine = create_engine(user, database_override=target_database)
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
        connection.execute(text(_build_preparation_sql()))

    return target_database
