# Fluxo da Pipeline

Este diagrama representa o fluxo operacional principal do projeto, desde a preparação opcional do banco até a geração dos relatórios e o consumo pelo dashboard.

```mermaid
flowchart TD
    A["Início da execução"] --> B["CLI: school_predictor"]
    B --> C{"Qual comando foi acionado?"}

    C -->|prepare-db| D["Preparar banco restaurado"]
    D --> D1["Anonimização e limpeza estrutural"]
    D1 --> Z["Fim"]

    C -->|extract| E["Conectar ao banco"]
    E --> F["Executar extração privada"]
    F --> G["Gerar CSVs em artifacts/database/csv"]
    G --> Z

    C -->|workflow| H["Rodar pipeline completa"]
    H --> I["Carregar CSVs canônicos"]
    I --> J["Construir dataset temporal"]
    J --> K["Criar features históricas, faltas, financeiro e professor"]
    K --> L["Executar modo previsao_nota"]
    K --> M["Executar modo alerta_risco"]
    L --> N["Treinar, validar e testar regressão"]
    M --> O["Treinar, validar e testar classificação"]
    N --> P["Salvar artifacts/pipeline/previsao_nota"]
    O --> Q["Salvar artifacts/pipeline/alerta_risco"]
    P --> R["Consolidar relatórios escolares"]
    Q --> R
    R --> S["Gerar artifacts/reports"]
    S --> T["Dashboard e leitura operacional"]
    T --> Z

    C -->|reports| R
    C -->|compare-history| U["Comparar min_history entre cenários"]
    U --> Z
    C -->|clean| V["Limpar caches e artefatos locais"]
    V --> Z
```

## Leitura rápida

- `prepare-db` atua na base restaurada e é opcional, usado quando o banco é renovado.
- `extract` transforma o banco tratado em CSVs canônicos.
- `workflow` é o fluxo principal do TCC: lê CSVs, modela, avalia e gera relatórios.
- `previsao_nota` e `alerta_risco` nascem a partir do mesmo dataset, mas com objetivos e cortes de histórico diferentes.
- o dashboard consome apenas os relatórios finais, não treina modelos.
