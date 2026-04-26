# Diagrama Arquitetural

Este diagrama resume a arquitetura atual do projeto, mostrando a separacao entre entrada operacional, camada de banco, pipeline analitica, artefatos e consumo final.

```mermaid
flowchart TD
    A["main.py"] --> B["school_predictor.cli"]
    B --> C["workflow"]
    B --> D["prepare-db"]
    B --> E["extract"]
    B --> F["pipeline"]
    B --> G["reports"]
    B --> H["compare-history"]
    B --> I["clean"]

    C --> J["school_predictor.application.run_default_workflow()"]
    J --> K["school_predictor.pipeline.orchestration.run_full_reporting_pipeline()"]

    D --> L["school_predictor.database.maintenance.prepare_updated_database()"]
    E --> M["school_predictor.application.extract_school_data_from_database()"]
    M --> N["school_predictor.database.extraction.extract_school_data()"]
    N --> O["artifacts/database/csv"]

    F --> P["school_predictor.pipeline.orchestration.run_real_pipeline()"]
    P --> Q["school_predictor.pipeline.config.PipelinePaths"]
    P --> R["school_predictor.pipeline.data.load_source_tables()"]
    P --> S["school_predictor.pipeline.dataset.build_prediction_dataset()"]
    P --> T["school_predictor.pipeline.modeling.train_and_evaluate()"]
    P --> U["school_predictor.pipeline.modeling.save_artifacts()"]
    P --> V["school_predictor.pipeline.modeling.write_report()"]

    K --> P1["modo previsao_nota"]
    K --> P2["modo alerta_risco"]
    K --> W["school_predictor.pipeline.reporting.build_school_reports()"]

    O --> R
    T --> X["artifacts/pipeline/previsao_nota"]
    T --> Y["artifacts/pipeline/alerta_risco"]
    W --> Z["artifacts/reports"]

    Z --> AA["relatorio_professor"]
    Z --> AB["relatorio_coordenacao"]
    Z --> AC["relatorio_secretaria"]
    Z --> AD["ranking_executivo"]

    AE["dashboard_streamlit.py"] --> AF["school_predictor.app.dashboard"]
    AF --> Z
```

## Leitura rapida

- `main.py` chama a CLI principal do projeto.
- `school_predictor.cli` organiza os comandos operacionais: preparar banco, extrair dados, rodar pipeline, gerar relatorios e limpar artefatos.
- `database/` concentra manutencao do banco e extracao dos dados brutos.
- `artifacts/database/csv` guarda os CSVs extraidos do banco.
- `pipeline/` concentra leitura dos CSVs, engenharia de atributos, treino, avaliacao e relatorios tecnicos.
- `run_full_reporting_pipeline()` executa os dois modos centrais: `previsao_nota` e `alerta_risco`.
- `reporting.py` consolida as saidas da modelagem em relatorios voltados para professor, coordenacao e secretaria.
- `dashboard_streamlit.py` consome os artefatos finais de `artifacts/reports`.
