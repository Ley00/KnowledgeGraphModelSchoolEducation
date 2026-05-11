# Arquitetura da Solução

Este diagrama representa a estrutura estática da solução, destacando os blocos principais, suas responsabilidades e dependências, sem focar na sequência de execução.

```mermaid
flowchart LR
    subgraph Interfaces["Interfaces de Entrada e Uso"]
        CLI["CLI<br/>school_predictor.cli"]
        MAIN["main.py"]
        DASH["dashboard_streamlit.py"]
    end

    subgraph Aplicacao["Camada de Aplicação"]
        APP["application.py"]
        CLEAN["cleanup.py"]
    end

    subgraph Banco["Camada de Banco e Extração"]
        ACCESS["database/access.py"]
        MAINT["database/maintenance.py"]
        EXTRACT["database/extraction.py"]
        QUERIES["database/queries.py"]
        PRIVATE["private_runtime.py local"]
        SQL["private_sql/ local"]
    end

    subgraph Pipeline["Camada Analítica"]
        ORCH["pipeline/orchestration.py"]
        DATA["pipeline/data.py"]
        DATASET["pipeline/dataset.py"]
        MODEL["pipeline/modeling.py"]
        REPORT["pipeline/reporting.py"]
        HISTORY["pipeline/history.py"]
    end

    subgraph Artefatos["Artefatos Locais"]
        CSV["artifacts/database/csv"]
        PIPE["artifacts/pipeline"]
        REPS["artifacts/reports"]
    end

    subgraph Consumo["Consumo Institucional"]
        PROF["Professor"]
        COORD["Coordenação"]
        SEC["Secretaria"]
    end

    MAIN --> CLI
    CLI --> APP
    CLI --> CLEAN
    APP --> ACCESS
    APP --> MAINT
    APP --> EXTRACT
    EXTRACT --> PRIVATE
    MAINT --> PRIVATE
    PRIVATE --> SQL
    EXTRACT --> QUERIES
    EXTRACT --> CSV

    APP --> ORCH
    ORCH --> DATA
    ORCH --> DATASET
    ORCH --> MODEL
    ORCH --> REPORT
    ORCH --> HISTORY
    DATA --> CSV
    MODEL --> PIPE
    REPORT --> PIPE
    REPORT --> REPS

    DASH --> REPS
    REPS --> PROF
    REPS --> COORD
    REPS --> SEC
```

## Leitura rápida

- `school_predictor/` concentra a aplicação ativa.
- a camada privada local protege SQL real e rotinas sensíveis do banco.
- `artifacts/database/csv` é a interface de entrada pública da pipeline.
- `artifacts/pipeline` guarda os resultados técnicos dos modelos.
- `artifacts/reports` guarda as saídas operacionais consumidas pela escola e pelo dashboard.
