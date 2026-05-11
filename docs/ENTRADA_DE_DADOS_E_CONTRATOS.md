# Entrada de Dados e Contratos de Extracao

Este documento explica como os dados entram no projeto sem expor as consultas SQL reais nem detalhar publicamente a estrutura completa do banco institucional.

## Principio de seguranca adotado

O repositório publica:
- o fluxo de extração
- os arquivos CSV gerados
- o contrato conceitual de cada extração
- os parâmetros esperados em cada etapa

O repositório nao publica:
- as consultas SQL reais
- a rotina SQL completa de preparação e sanitização do banco
- o desenho completo das tabelas internas
- os relacionamentos detalhados do banco operacional da instituição

As consultas reais ficam apenas em ambiente local, na pasta ignorada:
- `school_predictor/database/private_sql/`

A orquestração local das etapas privadas fica em:
- `school_predictor/database/private_runtime.py`

Opcionalmente, esse diretório pode ser sobrescrito pela variável:
- `SCHOOL_PREDICTOR_SQL_DIR`

## Como a entrada de dados funciona

1. O banco restaurado localmente pode ser preparado fisicamente por uma função privada em `school_predictor/database/private_runtime.py`.
2. A etapa pública `school_predictor/database/maintenance.py` atua apenas como wrapper seguro.
3. A extração com tratamento sensível também vive em `school_predictor/database/private_runtime.py`.
4. A etapa pública `school_predictor/database/extraction.py` atua apenas como wrapper seguro.
5. Cada função de extração chama uma consulta privada local por meio de `school_predictor/database/queries.py`.
6. Os resultados são tratados e gravados em:
   - `artifacts/database/csv/`
7. A pipeline consome esses CSVs para gerar:
   - artefatos analíticos em `artifacts/pipeline/`
   - relatórios operacionais em `artifacts/reports/`

## Separação recomendada das etapas privadas

### Etapa 1. Alterações físicas do banco

Responsabilidade:
- renomear o banco restaurado
- remover tabelas desnecessárias
- anonimizar dados sensíveis na base local
- reorganizar índices e atualizar estatísticas

Função privada recomendada:
- `prepare_private_database(...)`

Wrapper público:
- `school_predictor/database/maintenance.py`

### Etapa 2. Extração com tratamento dos dados

Responsabilidade:
- executar as consultas privadas locais
- aplicar tratamentos sensíveis ainda necessários para saída analítica
- gerar os CSVs canônicos usados pela pipeline

Função privada recomendada:
- `extract_private_school_data(...)`

Wrapper público:
- `school_predictor/database/extraction.py`

Observação:
- para testes operacionais do repositório, é válido iniciar apenas pela etapa 2 quando o banco já estiver previamente tratado

## Contrato publico das extrações

Observação:
- o `README.md` contém exemplos mínimos de cabeçalho, uma linha por CSV e um glossário resumido das colunas, apenas para orientar quem quiser montar uma réplica pública sem acesso ao banco institucional

### 1. Alunos

Arquivo gerado:
- `aluno.csv`

Objetivo:
- formar a base de matrícula ativa ou histórica por aluno, série, turma, curso e período letivo

Granularidade esperada:
- uma linha por vínculo aluno x matrícula x turma x período

Campos conceituais esperados:
- unidade
- período letivo
- curso
- série
- turma
- matrícula
- aluno
- situação da matrícula
- dados cadastrais básicos anonimizados

Parâmetros opcionais:
- nome do aluno
- período letivo

### 2. Médias e notas

Arquivo gerado:
- `media_nota_aluno.csv`

Objetivo:
- recuperar as médias do aluno por disciplina e etapa avaliativa

Granularidade esperada:
- uma linha por aluno x matrícula x disciplina x etapa

Campos conceituais esperados:
- chaves acadêmicas herdadas da base do aluno
- disciplina
- etapa
- identificador da média
- valor da média

Dependência lógica:
- usa como entrada as chaves já identificadas em `aluno.csv`

### 3. Pagamentos

Arquivo gerado:
- `pagamento_aluno.csv`

Objetivo:
- recuperar o histórico financeiro da matrícula para análises complementares de risco

Granularidade esperada:
- uma linha por matrícula x parcela ou movimento financeiro

Campos conceituais esperados:
- chaves acadêmicas herdadas da base do aluno
- movimento financeiro
- parcela
- vencimento
- valor
- status de pagamento
- indicadores de mensalidade e matrícula

### 4. Faltas

Arquivo gerado:
- `faltas_aluno.csv`

Objetivo:
- recuperar faltas do aluno por disciplina e etapa

Granularidade esperada:
- uma linha por evento de falta

Campos conceituais esperados:
- chaves acadêmicas herdadas da base do aluno
- disciplina
- etapa
- identificador da falta
- data da falta

### 5. Responsáveis

Arquivo gerado:
- `responsaveis_aluno.csv`

Objetivo:
- recuperar vínculos familiares e responsáveis para compor visão cadastral e analítica complementar

Granularidade esperada:
- uma linha por aluno x responsável

Campos conceituais esperados:
- chaves acadêmicas herdadas da base do aluno
- responsável
- tipo de responsável
- dados cadastrais anonimizados do responsável

### 6. Professores por turma e disciplina

Arquivo gerado:
- `professor_disciplina.csv`

Objetivo:
- mapear professor vinculado a turma e disciplina quando esse vínculo existir no banco

Granularidade esperada:
- uma linha por unidade x período x curso x série x turma x disciplina x professor

Campos conceituais esperados:
- unidade
- período
- curso
- série
- turma
- disciplina
- professor

Observação:
- turmas ou disciplinas sem professor vinculado nao devem ser descartadas da pipeline; a ausência do professor é tratada como dado faltante legítimo

## O que deve ser documentado publicamente

Quando o fluxo mudar, o repositório deve atualizar:
- `README.md` com a visão geral da entrada de dados
- este arquivo com os contratos das extrações
- diagramas em `diagrama/` se a arquitetura da entrada mudar

## O que deve continuar privado

Nao deve ser publicado:
- SQL bruto das extrações
- SQL bruto de preparação e saneamento do banco
- views internas da instituição
- nomes completos e estrutura integral do banco operacional

Se as consultas já tiverem sido publicadas em commits anteriores, removê-las apenas do estado atual do repositório nao elimina o histórico. Nesse caso, a limpeza do histórico Git precisa ser tratada separadamente antes da publicação do repositório.
