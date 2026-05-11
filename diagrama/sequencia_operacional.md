# Sequência Operacional

Este diagrama mostra, em ordem temporal, como uma execução completa do projeto acontece quando o usuário roda o workflow principal.

```mermaid
sequenceDiagram
    actor Usuario
    participant CLI as school_predictor.cli
    participant APP as application.py
    participant ORCH as orchestration.py
    participant DATA as data.py / dataset.py
    participant MODEL as modeling.py
    participant REPORT as reporting.py
    participant ART as artifacts/
    participant DASH as dashboard

    Usuario->>CLI: workflow
    CLI->>APP: run_default_workflow()
    APP->>ORCH: run_full_reporting_pipeline()

    ORCH->>ORCH: run_real_pipeline(previsao_nota)
    ORCH->>DATA: load_source_tables()
    DATA-->>ORCH: CSVs carregados
    ORCH->>DATA: build_prediction_dataset()
    DATA-->>ORCH: dataset temporal
    ORCH->>MODEL: train_and_evaluate()
    MODEL-->>ORCH: métricas, predictions, análise de erro
    ORCH->>ART: salvar artifacts/pipeline/previsao_nota

    ORCH->>ORCH: run_real_pipeline(alerta_risco)
    ORCH->>DATA: load_source_tables()
    DATA-->>ORCH: CSVs carregados
    ORCH->>DATA: build_prediction_dataset()
    DATA-->>ORCH: dataset temporal
    ORCH->>MODEL: train_and_evaluate()
    MODEL-->>ORCH: métricas, predictions, análise de erro
    ORCH->>ART: salvar artifacts/pipeline/alerta_risco

    ORCH->>REPORT: build_school_reports()
    REPORT->>ART: ler pipeline + gravar reports
    REPORT-->>ORCH: relatórios finais
    ART-->>DASH: relatórios prontos para consulta
```

## Leitura rápida

- a execução principal sempre começa pela CLI.
- os dois modos da pipeline são rodados separadamente dentro do mesmo workflow.
- cada modo produz seus próprios artefatos técnicos.
- os relatórios finais surgem apenas depois que os dois modos terminam.
