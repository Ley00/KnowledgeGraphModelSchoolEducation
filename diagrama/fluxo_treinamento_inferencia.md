# Diagrama de Fluxo de Treinamento e Inferencia

Este diagrama separa o fluxo em duas partes: treinamento da pipeline e uso do modelo para gerar saídas operacionais.

```mermaid
flowchart TD
    subgraph TREINAMENTO["Fluxo de treinamento"]
        A["CSV de notas, faltas, pagamentos e professores"] --> B["load_source_tables()"]
        B --> C["build_prediction_dataset()"]
        C --> C1["prepare_grades()"]
        C --> C2["prepare_absences()"]
        C --> C3["prepare_payments()"]
        C --> C4["prepare_teachers()"]
        C --> D["features temporais e contextuais"]
        D --> E["target_nota_proxima e target_risco_proxima"]
        E --> F["filtro por min_history"]
        F --> G["select_model_columns()"]
        G --> H["train_and_evaluate()"]
        H --> H1["temporal_split()"]
        H --> H2["escolha do melhor regressor por MAE"]
        H --> H3["escolha do melhor classificador por F1"]
        H --> H4["retreino com treino + validacao"]
        H --> H5["predicoes no conjunto de teste"]
        H --> H6["analise de erro"]
        H6 --> I["save_artifacts()"]
        H6 --> J["write_report()"]
    end

    subgraph INFERENCIA["Fluxo de inferencia e uso"]
        I --> K["artifacts/pipeline/previsao_nota"]
        I --> L["artifacts/pipeline/alerta_risco"]
        K --> M["build_school_reports()"]
        L --> M
        M --> N["relatorio_escolar_integrado.csv"]
        M --> O["relatorio_professor.csv"]
        M --> P["relatorio_coordenacao.csv"]
        M --> Q["relatorio_secretaria.csv"]
        M --> R["ranking_executivo_coordenacao.csv"]
        N --> S["dashboard_streamlit.py"]
        O --> S
        P --> S
        Q --> S
        R --> S
    end
```

## Leitura rapida

### Treinamento

- a pipeline comeca lendo os CSVs ja extraidos.
- `build_prediction_dataset()` transforma esses dados em um dataset longitudinal de modelagem.
- nesse dataset sao criadas features historicas, de faltas, de pagamento e de contexto escolar.
- depois sao criados os alvos de previsao de nota e de risco.
- o dataset passa por corte de historico minimo para garantir elegibilidade minima do aluno.
- `train_and_evaluate()` faz split temporal, compara modelos e baselines, escolhe o melhor candidato, retreina e testa.
- os resultados finais sao salvos como dataset, predições, modelo e relatorio tecnico.

### Inferencia e uso

- as saidas dos modos `previsao_nota` e `alerta_risco` sao consolidadas por `build_school_reports()`.
- essa consolidacao gera uma base integrada e relatorios especificos por perfil escolar.
- o dashboard em Streamlit le esses artefatos prontos e apresenta a informacao para consulta.
