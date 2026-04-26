# Diagrama Detalhado da Arquitetura Refatorada

Este diagrama mostra o fluxo principal da aplicação após a reorganização estrutural do projeto.

```mermaid
flowchart TD
    A["main.py ou python -m school_predictor"] --> B["school_predictor.cli"]
    B --> C["workflow"]
    B --> D["prepare-db"]
    B --> E["extract"]
    B --> F["pipeline"]
    B --> G["reports"]
    B --> H["compare-history"]
    B --> H1["clean"]

    C --> I["school_predictor.application.run_default_workflow()"]
    I --> J["school_predictor.pipeline.run_full_reporting_pipeline()"]
    J --> K["run_real_pipeline(mode='previsao_nota')"]
    J --> L["run_real_pipeline(mode='alerta_risco')"]
    J --> M["build_school_reports()"]

    F --> N["school_predictor.pipeline.orchestration"]
    K --> N
    L --> N

    N --> O["PipelinePaths.from_project_root()"]
    O --> P["school_predictor.pipeline.data.load_source_tables()"]
    P --> Q["Leitura dos CSVs em artifacts/database/csv"]

    Q --> R["school_predictor.pipeline.dataset.build_prediction_dataset()"]
    R --> R1["prepare_grades()"]
    R --> R2["prepare_absences()"]
    R --> R3["prepare_payments()"]
    R --> R4["prepare_teachers()"]
    R --> R5["features temporais e baselines"]

    R5 --> S["school_predictor.pipeline.modeling.train_and_evaluate()"]
    S --> S1["split temporal"]
    S --> S2["seleção de regressão por MAE"]
    S --> S3["seleção de classificação por F1"]
    S --> S4["predições e análise de erro"]

    S4 --> T["save_artifacts()"]
    T --> T1["artifacts/pipeline/previsao_nota"]
    T --> T2["artifacts/pipeline/alerta_risco"]

    M --> U["school_predictor.pipeline.reporting"]
    G --> U
    U --> U1["relatorio_professor.csv"]
    U --> U2["relatorio_coordenacao.csv"]
    U --> U3["relatorio_secretaria.csv"]
    U --> U4["ranking_executivo_coordenacao.csv"]

    V["dashboard_streamlit.py"] --> W["school_predictor.app.dashboard"]
    W --> U

    D --> X["school_predictor.database.maintenance"]
    X --> X1["school_predictor/database/private_runtime.py"]
    E --> Y["school_predictor.database.extraction"]
    Y --> X1
    Y --> Y1["consultas SQL privadas locais"]
    Y1 --> Y2["school_predictor/database/private_sql ou SCHOOL_PREDICTOR_SQL_DIR"]
    Y2 --> Q
    H --> Z["school_predictor.pipeline.history"]
    H1 --> AA["school_predictor.cleanup"]
```

## Leitura rápida

- `school_predictor/` passou a ser a arquitetura principal do projeto.
- `database/` cuida de banco e extração.
- a execução real de preparação do banco e de extração com tratamento sensível fica em `school_predictor/database/private_runtime.py`, mantido fora do Git.
- as consultas SQL reais de extração ficam fora do Git e são carregadas localmente de `school_predictor/database/private_sql/` ou de um diretório privado equivalente definido por ambiente.
- `pipeline/` cuida de dataset, modelagem e relatórios.
- `cleanup/` cuida da limpeza local de caches e auxiliares de build.
- `app/` cuida do dashboard.
- `artifacts/` passou a ser o diretório canônico de saídas locais da aplicação.
- o código histórico fora do fluxo atual foi removido para manter o projeto focado no caminho operacional do TCC.
