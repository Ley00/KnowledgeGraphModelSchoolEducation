# Dashboard Streamlit

## Objetivo

Este dashboard apresenta os relatórios da pipeline de forma visual para:

- professor
- coordenação
- secretaria

## Pré-requisitos

Antes de abrir a interface, gere os relatórios com a pipeline:

```bash
./.venv/bin/python main.py
```

Isso deve atualizar os arquivos em:

`TCCPipeline/Result/relatorios_escolares/`

## Execução

Com o ambiente virtual ativo e as dependências instaladas:

```bash
./.venv/bin/streamlit run dashboard_streamlit.py
```

## Telas disponíveis

### Visão geral

- distribuição de risco
- disciplinas com maior taxa de alto risco
- dispersão entre nota atual e nota prevista
- ranking executivo resumido

### Professor

- casos filtrados por período, série, disciplina e risco
- alunos mais críticos
- relação entre nota atual, nota prevista e pontuação de risco
- tabela com fatores de alerta e recomendação pedagógica

### Coordenação

- agrupamentos críticos por série e disciplina
- mapa de calor de alto risco
- ranking executivo dos alunos mais urgentes

### Secretaria

- distribuição da prioridade administrativa
- maiores pendências financeiras
- tabela de acompanhamento para contato preventivo
